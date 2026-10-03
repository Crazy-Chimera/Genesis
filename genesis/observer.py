from __future__ import annotations

from dataclasses import dataclass
import numpy as np

Cell = tuple[int, int]

@dataclass(frozen=True)
class Cluster:
    """A measurement-only connected region in the observer's phase field."""
    cells: tuple[Cell, ...]
    coherence: float

@dataclass(frozen=True)
class RegionObservation:
    """A cluster enriched with boundary and temporal measurements."""
    cells: tuple[Cell, ...]
    coherence: float
    boundary_contrast: float
    identity: int
    lifetime: int
    persistence: int
    overlap: float

class LocalStructureObserver:
    """Detect local coherent regions without changing universe state."""

    def __init__(self, threshold: float = 0.7) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold

    @staticmethod
    def local_coherence(phase: np.ndarray) -> np.ndarray:
        """Measure phase coherence over each cell and its four neighbours."""
        vectors = np.exp(1j * phase)
        neighbourhood = (
            vectors + np.roll(vectors, 1, 0) + np.roll(vectors, -1, 0)
            + np.roll(vectors, 1, 1) + np.roll(vectors, -1, 1)
        ) / 5.0
        return np.abs(neighbourhood)

    def mask(self, phase: np.ndarray) -> np.ndarray:
        return self.local_coherence(phase) >= self.threshold

    @staticmethod
    def _components(mask: np.ndarray) -> list[list[Cell]]:
        """Return four-neighbour connected components with periodic boundaries."""
        rows, cols = mask.shape
        seen = np.zeros_like(mask, dtype=bool)
        components: list[list[Cell]] = []
        for start in zip(*np.nonzero(mask)):
            start = (int(start[0]), int(start[1]))
            if seen[start]:
                continue
            stack = [start]
            seen[start] = True
            component: list[Cell] = []
            while stack:
                r, c = stack.pop()
                component.append((r, c))
                for nr, nc in (
                    ((r - 1) % rows, c), ((r + 1) % rows, c),
                    (r, (c - 1) % cols), (r, (c + 1) % cols),
                ):
                    if mask[nr, nc] and not seen[nr, nc]:
                        seen[nr, nc] = True
                        stack.append((nr, nc))
            components.append(component)
        return components

    def detect(self, phase: np.ndarray) -> list[Cluster]:
        local = self.local_coherence(phase)
        mask = local >= self.threshold
        clusters = []
        for cells in self._components(mask):
            values = np.array([local[r, c] for r, c in cells])
            clusters.append(
                Cluster(cells=tuple(sorted(cells)), coherence=float(values.mean()))
            )
        return sorted(clusters, key=lambda c: (-len(c.cells), c.cells))

    @staticmethod
    def boundary_contrast(cluster: Cluster, local: np.ndarray) -> float:
        """Measure inside-vs-outside coherence across the region boundary."""
        cells = set(cluster.cells)
        rows, cols = local.shape
        inside = [local[r, c] for r, c in cluster.cells]
        outside = []
        for r, c in cluster.cells:
            for nr, nc in (
                ((r - 1) % rows, c), ((r + 1) % rows, c),
                (r, (c - 1) % cols), (r, (c + 1) % cols),
            ):
                if (nr, nc) not in cells:
                    outside.append(local[nr, nc])
        if not outside:
            return 0.0
        return float(np.mean(inside) - np.mean(outside))

class RegionTracker:
    """Track observer-detected regions across frames without modifying the universe."""

    def __init__(self, observer: LocalStructureObserver, overlap_threshold: float = 0.5):
        if not 0.0 <= overlap_threshold <= 1.0:
            raise ValueError("overlap_threshold must be between 0 and 1")
        self.observer = observer
        self.overlap_threshold = overlap_threshold
        self._next_identity = 1
        self._previous: dict[int, Cluster] = {}
        self._lifetimes: dict[int, int] = {}
        self._persistence: dict[int, int] = {}

    @staticmethod
    def jaccard(a: Cluster, b: Cluster) -> float:
        left, right = set(a.cells), set(b.cells)
        union = left | right
        return 1.0 if not union else len(left & right) / len(union)

    def observe(self, phase: np.ndarray) -> list[RegionObservation]:
        local = self.observer.local_coherence(phase)
        clusters = self.observer.detect(phase)
        candidates = []
        for cluster in clusters:
            for identity, previous in self._previous.items():
                overlap = self.jaccard(cluster, previous)
                if overlap >= self.overlap_threshold:
                    candidates.append((overlap, len(cluster.cells), identity, cluster))
        candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
        matched_current: set[int] = set()
        matched_previous: set[int] = set()
        assignments: list[tuple[int, Cluster, float]] = []
        for overlap, _, identity, cluster in candidates:
            key = id(cluster)
            if key in matched_current or identity in matched_previous:
                continue
            matched_current.add(key)
            matched_previous.add(identity)
            assignments.append((identity, cluster, overlap))
        for cluster in clusters:
            if id(cluster) not in matched_current:
                identity = self._next_identity
                self._next_identity += 1
                assignments.append((identity, cluster, 0.0))
        assignments.sort(key=lambda item: item[1].cells)
        observations = []
        current: dict[int, Cluster] = {}
        for identity, cluster, overlap in assignments:
            lifetime = self._lifetimes.get(identity, 0) + 1
            persistence = self._persistence.get(identity, 0) + 1
            self._lifetimes[identity] = lifetime
            self._persistence[identity] = persistence
            current[identity] = cluster
            observations.append(RegionObservation(
                cells=cluster.cells,
                coherence=cluster.coherence,
                boundary_contrast=self.observer.boundary_contrast(cluster, local),
                identity=identity,
                lifetime=lifetime,
                persistence=persistence,
                overlap=overlap,
            ))
        self._previous = current
        return observations
