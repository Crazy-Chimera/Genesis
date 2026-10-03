from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .observer import RegionEvent, RegionObservation


@dataclass(frozen=True)
class MemoryRecord:
    """One observer-level temporal trace; it is not universe state."""

    tick: int
    identity: int
    cells: tuple[tuple[int, int], ...]
    coherence: float
    boundary_contrast: float
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
    multiscale_field: tuple[float, ...] = ()
    events: tuple[str, ...] = ()


class TemporalMemory:
    """External append-only memory of measured region observations."""

    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    def record(
        self,
        tick: int,
        observations: Iterable[RegionObservation],
        events: Iterable[RegionEvent] = (),
    ) -> list[MemoryRecord]:
        events_by_identity: dict[int, list[str]] = {}
        for event in events:
            events_by_identity.setdefault(event.identity, []).append(event.kind)

        added: list[MemoryRecord] = []
        for observation in observations:
            item = MemoryRecord(
                tick=tick,
                identity=observation.identity,
                cells=observation.cells,
                coherence=observation.coherence,
                boundary_contrast=observation.boundary_contrast,
                lifetime=observation.lifetime,
                persistence=observation.persistence,
                overlap=observation.overlap,
                local_patch=observation.local_patch,
                phase_patch=observation.phase_patch,
                gradient_patch=observation.gradient_patch,
                motion=observation.motion,
                boundary_flux=observation.boundary_flux,
                boundary_deformation=observation.boundary_deformation,
                spatiotemporal_patch=observation.spatiotemporal_patch,
                spatial_field=observation.spatial_field,
                multiscale_field=observation.multiscale_field,
                multiscale_field=observation.multiscale_field,
                events=tuple(sorted(events_by_identity.get(observation.identity, ()))),
            )
            self._records.append(item)
            added.append(item)
        return added

    def all(self) -> tuple[MemoryRecord, ...]:
        return tuple(self._records)

    def for_identity(self, identity: int) -> tuple[MemoryRecord, ...]:
        return tuple(record for record in self._records if record.identity == identity)

    def at_tick(self, tick: int) -> tuple[MemoryRecord, ...]:
        return tuple(record for record in self._records if record.tick == tick)

    def __len__(self) -> int:
        return len(self._records)
