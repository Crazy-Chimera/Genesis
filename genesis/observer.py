from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Cluster:
    """A measurement-only connected region in the observer's phase field."""

    cells: tuple[tuple[int, int], ...]
    coherence: float


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
            vectors
            + np.roll(vectors, 1, 0)
            + np.roll(vectors, -1, 0)
            + np.roll(vectors, 1, 1)
            + np.roll(vectors, -1, 1)
        ) / 5.0
        return np.abs(neighbourhood)

    def mask(self, phase: np.ndarray) -> np.ndarray:
        return self.local_coherence(phase) >= self.threshold

    @staticmethod
    def _components(mask: np.ndarray) -> list[list[tuple[int, int]]]:
        """Return four-neighbour connected components with periodic boundaries."""
        rows, cols = mask.shape
        seen = np.zeros_like(mask, dtype=bool)
        components: list[list[tuple[int, int]]] = []

        for start in zip(*np.nonzero(mask)):
            start = (int(start[0]), int(start[1]))
            if seen[start]:
                continue

            stack = [start]
            seen[start] = True
            component: list[tuple[int, int]] = []

            while stack:
                r, c = stack.pop()
                component.append((r, c))
                for nr, nc in (
                    ((r - 1) % rows, c),
                    ((r + 1) % rows, c),
                    (r, (c - 1) % cols),
                    (r, (c + 1) % cols),
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

        return sorted(clusters, key=lambda cluster: (-len(cluster.cells), cluster.cells))
