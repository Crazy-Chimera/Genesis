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
    local_patch: tuple[float, ...] = ()


@dataclass(frozen=True)
class RegionEvent:
    """An observer-level transition between measured region states."""

    kind: str
    identity: int
    related: tuple[int, ...] = ()
    size_delta: int = 0


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
    @staticmethod
    def local_patch(cluster: Cluster, local: np.ndarray, radius: int = 1) -> tuple[float, ...]:
        """Return a small centroid-centered local coherence patch."""
        if radius < 0:
            raise ValueError("radius must be >= 0")
        rows, cols = local.shape
        if not cluster.cells:
            return ()
        center_r = int(round(sum(r for r, _ in cluster.cells) / len(cluster.cells)))
        center_c = int(round(sum(c for _, c in cluster.cells) / len(cluster.cells)))
        values = []
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                values.append(float(local[(center_r + dr) % rows, (center_c + dc) % cols]))
        return tuple(values)

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

    def _assign(self, clusters: list[Cluster]) -> tuple[list[tuple[int, Cluster, float]], dict[int, list[int]], dict[int, list[int]]]:
        candidates = []
        parents: dict[int, list[int]] = {}
        for index, cluster in enumerate(clusters):
            for identity, previous in self._previous.items():
                overlap = self.jaccard(cluster, previous)
                if overlap >= self.overlap_threshold:
                    candidates.append((overlap, len(cluster.cells), identity, index))
                    parents.setdefault(index, []).append(identity)
        candidates.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))
        matched_current: set[int] = set()
        matched_previous: set[int] = set()
        assignments: list[tuple[int, Cluster, float]] = []
        for overlap, _, identity, index in candidates:
            if index in matched_current or identity in matched_previous:
                continue
            matched_current.add(index)
            matched_previous.add(identity)
            assignments.append((identity, clusters[index], overlap))
        for index, cluster in enumerate(clusters):
            if index not in matched_current:
                identity = self._next_identity
                self._next_identity += 1
                assignments.append((identity, cluster, 0.0))
        children: dict[int, list[int]] = {}
        for index, cluster in enumerate(clusters):
            for identity in parents.get(index, []):
                assigned = next(
                    assigned_id for assigned_id, assigned_cluster, _ in assignments
                    if assigned_cluster is cluster
                )
                children.setdefault(identity, []).append(assigned)
        return assignments, parents, children

    @staticmethod
    def classify_events(
        previous: dict[int, Cluster],
        current: dict[int, Cluster],
        overlap_threshold: float = 0.5,
    ) -> list[RegionEvent]:
        """Classify birth/death/growth/decay/split/merge from region overlap."""
        parents: dict[int, list[int]] = {}
        children: dict[int, list[int]] = {}
        for current_id, current_cluster in current.items():
            for previous_id, previous_cluster in previous.items():
                if RegionTracker.jaccard(current_cluster, previous_cluster) >= overlap_threshold:
                    parents.setdefault(current_id, []).append(previous_id)
                    children.setdefault(previous_id, []).append(current_id)

        events: list[RegionEvent] = []
        for current_id, cluster in current.items():
            previous_ids = sorted(parents.get(current_id, []))
            if len(previous_ids) > 1:
                events.append(RegionEvent("merge", current_id, tuple(previous_ids)))
            elif not previous_ids:
                events.append(RegionEvent("birth", current_id, size_delta=len(cluster.cells)))
            else:
                previous_cluster = previous[previous_ids[0]]
                delta = len(cluster.cells) - len(previous_cluster.cells)
                if len(children.get(previous_ids[0], [])) > 1:
                    events.append(RegionEvent("split", previous_ids[0], tuple(sorted(children[previous_ids[0]]))))
                elif delta > 0:
                    events.append(RegionEvent("growth", current_id, size_delta=delta))
                elif delta < 0:
                    events.append(RegionEvent("decay", current_id, size_delta=delta))
        for previous_id in sorted(previous):
            if not children.get(previous_id):
                events.append(RegionEvent("death", previous_id, size_delta=-len(previous[previous_id].cells)))
        return sorted(events, key=lambda event: (event.kind, event.identity, event.related))

    def observe(self, phase: np.ndarray) -> list[RegionObservation]:
        local = self.observer.local_coherence(phase)
        clusters = self.observer.detect(phase)
        assignments, _, _ = self._assign(clusters)
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
                local_patch=self.observer.local_patch(cluster, local),
            ))
        self._previous = current
        return observations

    def observe_events(self, phase: np.ndarray) -> tuple[list[RegionObservation], list[RegionEvent]]:
        previous = self._previous.copy()
        observations = self.observe(phase)
        events = self.classify_events(previous, self._previous, self.overlap_threshold)
        if not previous:
            events = [
                event for event in events
                if event.kind == "birth"
            ]
        return observations, events
