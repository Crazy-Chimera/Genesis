from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .global_harmonics import global_phase_harmonics

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
    phase_patch: tuple[float, ...] = ()
    gradient_patch: tuple[float, ...] = ()
    motion: tuple[float, ...] = ()
    boundary_flux: tuple[float, ...] = ()
    boundary_deformation: tuple[float, ...] = ()
    spatiotemporal_patch: tuple[float, ...] = ()
    spatial_field: tuple[float, ...] = ()
    multiscale_field: tuple[float, ...] = ()
    relational: tuple[float, ...] = ()
    graph_relational: tuple[float, ...] = ()
    global_harmonics: tuple[float, ...] = ()


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
    def phase_patch(cluster: Cluster, phase: np.ndarray, radius: int = 1) -> tuple[float, ...]:
        """Return sin/cos of local phase relative to the patch center."""
        if radius < 0:
            raise ValueError("radius must be >= 0")
        rows, cols = phase.shape
        if not cluster.cells:
            return ()
        center_r = int(round(sum(r for r, _ in cluster.cells) / len(cluster.cells)))
        center_c = int(round(sum(c for _, c in cluster.cells) / len(cluster.cells)))
        center = phase[center_r % rows, center_c % cols]
        values: list[float] = []
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                delta = phase[(center_r + dr) % rows, (center_c + dc) % cols] - center
                values.extend((float(np.sin(delta)), float(np.cos(delta))))
        return tuple(values)

    @staticmethod
    def gradient_patch(cluster: Cluster, phase: np.ndarray, radius: int = 1) -> tuple[float, ...]:
        """Return oriented wrapped phase gradients (dx, dy) around a region."""
        if radius < 0:
            raise ValueError("radius must be >= 0")
        rows, cols = phase.shape
        if not cluster.cells:
            return ()
        center_r = int(round(sum(r for r, _ in cluster.cells) / len(cluster.cells)))
        center_c = int(round(sum(c for _, c in cluster.cells) / len(cluster.cells)))
        values: list[float] = []
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r = (center_r + dr) % rows
                c = (center_c + dc) % cols
                dx = np.angle(np.exp(1j * (phase[r, (c + 1) % cols] - phase[r, c])))
                dy = np.angle(np.exp(1j * (phase[(r + 1) % rows, c] - phase[r, c])))
                values.extend((float(dx), float(dy)))
        return tuple(values)

    @staticmethod
    def motion(previous: Cluster | None, current: Cluster, shape: tuple[int, int]) -> tuple[float, ...]:
        """Measure observer-level periodic centroid displacement and size change."""
        if previous is None or not previous.cells or not current.cells:
            return ()
        rows, cols = shape

        def centroid(cluster: Cluster) -> tuple[float, float]:
            return (
                sum(r for r, _ in cluster.cells) / len(cluster.cells),
                sum(c for _, c in cluster.cells) / len(cluster.cells),
            )

        old_r, old_c = centroid(previous)
        new_r, new_c = centroid(current)

        def periodic_delta(new: float, old: float, size: int) -> float:
            delta = new - old
            half = size / 2.0
            if delta > half:
                delta -= size
            elif delta < -half:
                delta += size
            return delta

        return (
            periodic_delta(new_r, old_r, rows),
            periodic_delta(new_c, old_c, cols),
            float(len(current.cells) - len(previous.cells)),
        )

    @staticmethod
    def boundary_flux(cluster: Cluster, phase: np.ndarray) -> tuple[float, ...]:
        """Measure signed phase flux and boundary geometry across a region."""
        if not cluster.cells:
            return ()
        cells = set(cluster.cells)
        rows, cols = phase.shape
        horizontal: list[float] = []
        vertical: list[float] = []
        boundary_edges = 0
        for r, c in cluster.cells:
            for nr, nc, axis in (
                ((r - 1) % rows, c, 0),
                ((r + 1) % rows, c, 0),
                (r, (c - 1) % cols, 1),
                (r, (c + 1) % cols, 1),
            ):
                if (nr, nc) in cells:
                    continue
                delta = np.angle(np.exp(1j * (phase[nr, nc] - phase[r, c])))
                (horizontal if axis == 0 else vertical).append(float(np.sin(delta)))
                boundary_edges += 1
        if boundary_edges == 0:
            return (0.0, 0.0, 0.0, 0.0, 0.0)
        values = horizontal + vertical
        return (
            float(np.mean(horizontal)) if horizontal else 0.0,
            float(np.mean(vertical)) if vertical else 0.0,
            float(np.mean(np.abs(values))),
            float(boundary_edges),
            float(boundary_edges / len(cells)),
        )

    @staticmethod
    def boundary_deformation(
        previous: Cluster | None,
        current: Cluster,
        previous_phase: np.ndarray | None,
        current_phase: np.ndarray,
    ) -> tuple[float, ...]:
        """Measure change of boundary flux and boundary geometry between frames."""
        if previous is None or previous_phase is None:
            return ()
        old_cells, new_cells = set(previous.cells), set(current.cells)
        rows, cols = current_phase.shape

        def flux_vector(cells: set[tuple[int, int]], phase: np.ndarray) -> tuple[float, ...]:
            horizontal: list[float] = []
            vertical: list[float] = []
            edges = 0
            for r, c in cells:
                for nr, nc, axis in (
                    ((r - 1) % rows, c, 0),
                    ((r + 1) % rows, c, 0),
                    (r, (c - 1) % cols, 1),
                    (r, (c + 1) % cols, 1),
                ):
                    if (nr, nc) in cells:
                        continue
                    delta = np.angle(np.exp(1j * (phase[nr, nc] - phase[r, c])))
                    (horizontal if axis == 0 else vertical).append(float(np.sin(delta)))
                    edges += 1
            values = horizontal + vertical
            return (
                float(np.mean(horizontal)) if horizontal else 0.0,
                float(np.mean(vertical)) if vertical else 0.0,
                float(np.mean(np.abs(values))) if values else 0.0,
                float(edges),
                float(edges / len(cells)) if cells else 0.0,
            )

        old_flux = flux_vector(old_cells, previous_phase)
        new_flux = flux_vector(new_cells, current_phase)
        symmetric_difference = len(old_cells ^ new_cells)
        union_size = len(old_cells | new_cells)
        return (
            new_flux[0] - old_flux[0],
            new_flux[1] - old_flux[1],
            new_flux[2] - old_flux[2],
            new_flux[3] - old_flux[3],
            new_flux[4] - old_flux[4],
            float(symmetric_difference),
            float(symmetric_difference / union_size) if union_size else 0.0,
        )

    @staticmethod
    def spatiotemporal_patch(
        previous_phase: np.ndarray | None,
        current_phase: np.ndarray,
        cluster: Cluster,
        radius: int = 1,
    ) -> tuple[float, ...]:
        """Preserve a centroid-aligned local phase state and its one-step change."""
        if previous_phase is None or not cluster.cells:
            return ()
        if radius < 0:
            raise ValueError("radius must be >= 0")
        rows, cols = current_phase.shape
        center_r = int(round(sum(r for r, _ in cluster.cells) / len(cluster.cells)))
        center_c = int(round(sum(c for _, c in cluster.cells) / len(cluster.cells)))
        values: list[float] = []
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r = (center_r + dr) % rows
                c = (center_c + dc) % cols
                current = current_phase[r, c]
                previous = previous_phase[r, c]
                values.extend((
                    float(np.sin(current)),
                    float(np.cos(current)),
                    float(np.sin(current - previous)),
                    float(np.cos(current - previous)),
                ))
        return tuple(values)

    @staticmethod
    def spatial_field(
        phase: np.ndarray,
        cluster: Cluster,
        radius: int = 1,
    ) -> tuple[float, ...]:
        """Measure a fixed-orientation local phase field around the region."""
        if not cluster.cells:
            return ()
        if radius < 0:
            raise ValueError("radius must be >= 0")
        rows, cols = phase.shape
        center_r = int(round(sum(r for r, _ in cluster.cells) / len(cluster.cells)))
        center_c = int(round(sum(c for _, c in cluster.cells) / len(cluster.cells)))
        values: list[float] = []
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r = (center_r + dr) % rows
                c = (center_c + dc) % cols
                values.extend((float(np.sin(phase[r, c])), float(np.cos(phase[r, c]))))
        return tuple(values)

    @staticmethod
    def multiscale_field(phase: np.ndarray, cluster: Cluster) -> tuple[float, ...]:
        """Measure concatenated fixed-orientation radius-1 and radius-2 phase fields."""
        return LocalStructureObserver.spatial_field(phase, cluster, radius=1) + LocalStructureObserver.spatial_field(
            phase, cluster, radius=2
        )

    @staticmethod
    def multiscale_field(
        phase: np.ndarray,
        cluster: Cluster,
        radii: tuple[int, ...] = (1, 2),
    ) -> tuple[float, ...]:
        """Measure fixed-orientation phase fields at multiple spatial scales."""
        if not cluster.cells:
            return ()
        rows, cols = phase.shape
        center_r = int(round(sum(r for r, _ in cluster.cells) / len(cluster.cells)))
        center_c = int(round(sum(c for _, c in cluster.cells) / len(cluster.cells)))
        values: list[float] = []
        for radius in radii:
            if radius < 0:
                raise ValueError("radii must be non-negative")
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r = (center_r + dr) % rows
                    c = (center_c + dc) % cols
                    values.extend((float(np.sin(phase[r, c])), float(np.cos(phase[r, c]))))
        return tuple(values)

    @staticmethod
    def relational_features(
        target: Cluster,
        peers: list[Cluster],
        phase: np.ndarray,
        local: np.ndarray,
        max_peers: int = 2,
    ) -> tuple[float, ...]:
        """Measure deterministic cross-region relations; coherence itself is excluded."""
        if max_peers < 1:
            raise ValueError("max_peers must be >= 1")
        if not target.cells:
            return (0.0,) * (max_peers * 7 + max_peers)
        rows, cols = phase.shape

        def centroid(cluster: Cluster) -> tuple[float, float]:
            return (
                sum(r for r, _ in cluster.cells) / len(cluster.cells),
                sum(c for _, c in cluster.cells) / len(cluster.cells),
            )

        def mean_phase(cluster: Cluster) -> float:
            z = np.mean(np.exp(1j * np.asarray([phase[r, c] for r, c in cluster.cells])))
            return float(np.angle(z))

        tr, tc = centroid(target)
        tp = mean_phase(target)
        candidates = []
        for peer in peers:
            if peer is target:
                continue
            pr, pc = centroid(peer)
            dr = pr - tr
            dc = pc - tc
            dr -= round(dr / rows) * rows
            dc -= round(dc / cols) * cols
            distance = float(np.hypot(dr / rows, dc / cols))
            candidates.append((distance, tuple(peer.cells), peer, dr, dc))
        candidates.sort(key=lambda item: (item[0], item[1]))

        values: list[float] = []
        target_boundary = LocalStructureObserver.boundary_contrast(target, local)
        for index in range(max_peers):
            if index >= len(candidates):
                values.extend((0.0,) * 7)
                values.append(0.0)
                continue
            distance, _, peer, dr, dc = candidates[index]
            phase_delta = mean_phase(peer) - tp
            phase_delta = float(np.angle(np.exp(1j * phase_delta)))
            size_ratio = np.log((len(peer.cells) + 1.0) / (len(target.cells) + 1.0))
            boundary_delta = LocalStructureObserver.boundary_contrast(peer, local) - target_boundary
            values.extend((
                float(dr / rows),
                float(dc / cols),
                float(np.sin(phase_delta)),
                float(np.cos(phase_delta)),
                float(size_ratio),
                float(boundary_delta),
                distance,
            ))
            values.append(1.0)
        return tuple(values)


    @staticmethod
    def graph_relational_features(
        target: Cluster,
        peers: list[Cluster],
        phase: np.ndarray,
        local: np.ndarray,
        max_peers: int = 8,
    ) -> tuple[float, ...]:
        """Aggregate relations to a wider peer graph into a fixed-width vector."""
        if max_peers < 1:
            raise ValueError("max_peers must be >= 1")
        if not target.cells:
            return (0.0,) * 33
        rows, cols = phase.shape

        def centroid(cluster: Cluster) -> tuple[float, float]:
            return (
                sum(r for r, _ in cluster.cells) / len(cluster.cells),
                sum(c for _, c in cluster.cells) / len(cluster.cells),
            )

        def mean_phase(cluster: Cluster) -> float:
            z = np.mean(np.exp(1j * np.asarray([phase[r, c] for r, c in cluster.cells])))
            return float(np.angle(z))

        tr, tc = centroid(target)
        tp = mean_phase(target)
        target_boundary = LocalStructureObserver.boundary_contrast(target, local)
        candidates = []
        for peer in peers:
            if peer is target:
                continue
            pr, pc = centroid(peer)
            dr = pr - tr - round((pr - tr) / rows) * rows
            dc = pc - tc - round((pc - tc) / cols) * cols
            distance = float(np.hypot(dr / rows, dc / cols))
            phase_delta = float(np.angle(np.exp(1j * (mean_phase(peer) - tp))))
            size_ratio = float(np.log((len(peer.cells) + 1.0) / (len(target.cells) + 1.0)))
            boundary_delta = LocalStructureObserver.boundary_contrast(peer, local) - target_boundary
            candidates.append((distance, tuple(peer.cells), (
                dr / rows, dc / cols, np.sin(phase_delta), np.cos(phase_delta),
                size_ratio, boundary_delta, distance, 1.0,
            )))
        candidates.sort(key=lambda item: (item[0], item[1]))
        selected = [item[2] for item in candidates[:max_peers]]
        if not selected:
            return (0.0,) * 33
        values = np.asarray(selected, dtype=np.float64)
        mean = values.mean(axis=0)
        std = values.std(axis=0)
        minimum = values.min(axis=0)
        maximum = values.max(axis=0)
        return tuple(np.concatenate((mean, std, minimum, maximum, np.asarray([len(selected) / max_peers]))))

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
        previous_phase = getattr(self, "_previous_phase", None)
        assigned_clusters = [cluster for _, cluster, _ in assignments]
        for identity, cluster, overlap in assignments:
            lifetime = self._lifetimes.get(identity, 0) + 1
            persistence = self._persistence.get(identity, 0) + 1
            self._lifetimes[identity] = lifetime
            self._persistence[identity] = persistence
            current[identity] = cluster
            previous_cluster = self._previous.get(identity)
            motion = self.observer.motion(previous_cluster, cluster, phase.shape) if previous_cluster else ()
            observations.append(RegionObservation(
                cells=cluster.cells,
                coherence=cluster.coherence,
                boundary_contrast=self.observer.boundary_contrast(cluster, local),
                identity=identity,
                lifetime=lifetime,
                persistence=persistence,
                overlap=overlap,
                local_patch=self.observer.local_patch(cluster, local),
                phase_patch=self.observer.phase_patch(cluster, phase),
                gradient_patch=self.observer.gradient_patch(cluster, phase),
                motion=motion,
                boundary_flux=self.observer.boundary_flux(cluster, phase),
                boundary_deformation=self.observer.boundary_deformation(previous_cluster, cluster, previous_phase, phase),
                spatiotemporal_patch=self.observer.spatiotemporal_patch(previous_phase, phase, cluster),
                spatial_field=self.observer.spatial_field(phase, cluster),
                multiscale_field=self.observer.multiscale_field(phase, cluster),
                relational=self.observer.relational_features(cluster, assigned_clusters, phase, local),
                graph_relational=self.observer.graph_relational_features(cluster, assigned_clusters, phase, local),
                global_harmonics=global_phase_harmonics(phase),
            ))
        self._previous = current
        self._previous_phase = phase.copy()
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
