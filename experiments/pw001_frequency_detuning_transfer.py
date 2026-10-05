from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import MemoryRecord
from genesis.observer import LocalStructureObserver, RegionTracker


def frequency_state(record: MemoryRecord, omega: np.ndarray) -> tuple[float, ...]:
    values = np.asarray([omega[r, c] for r, c in record.cells], dtype=float)
    if values.size == 0:
        return (0.0, 0.0, 0.0)
    mean = float(values.mean())
    return (
        mean,
        float(values.std()),
        float(np.mean(np.abs(values - omega.mean()))),
    )


def collect(seed: int, ticks: int = 600):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    observer = LocalStructureObserver()
    tracker = RegionTracker(observer)
    records: list[MemoryRecord] = []

    observations, events = tracker.observe_events(universe.phase)
    for observation in observations:
        records.append(MemoryRecord(
            tick=universe.tick,
            identity=observation.identity,
            cells=observation.cells,
            coherence=observation.coherence,
            boundary_contrast=observation.boundary_contrast,
            lifetime=observation.lifetime,
            persistence=observation.persistence,
            overlap=observation.overlap,
            event_kinds=tuple(e.kind for e in events if e.identity == observation.identity),
            local_patch=observation.local_patch,
            phase_patch=observation.phase_patch,
            gradient_patch=observation.gradient_patch,
            motion=observation.motion,
            boundary_flux=observation.boundary_flux,
            boundary_deformation=observation.boundary_deformation,
            spatiotemporal_patch=observation.spatiotemporal_patch,
            spatial_field=observation.spatial_field,
            multiscale_field=observation.multiscale_field,
            relational=observation.relational,
            graph_relational=observation.graph_relational,
        ))

    # Keep a separate observer-only frequency map keyed by (tick, identity).
    freq = {(r.tick, r.identity): frequency_state(r, universe.omega) for r in records}

    for _ in range(ticks):
        universe.step()
        observations, events = tracker.observe_events(universe.phase)
        for observation in observations:
            record = MemoryRecord(
                tick=universe.tick,
                identity=observation.identity,
                cells=observation.cells,
                coherence=observation.coherence,
                boundary_contrast=observation.boundary_contrast,
                lifetime=observation.lifetime,
                persistence=observation.persistence,
                overlap=observation.overlap,
                event_kinds=tuple(e.kind for e in events if e.identity == observation.identity),
                local_patch=observation.local_patch,
                phase_patch=observation.phase_patch,
                gradient_patch=observation.gradient_patch,
                motion=observation.motion,
                boundary_flux=observation.boundary_flux,
                boundary_deformation=observation.boundary_deformation,
                spatiotemporal_patch=observation.spatiotemporal_patch,
                spatial_field=observation.spatial_field,
                multiscale_field=observation.multiscale_field,
                relational=observation.relational,
                graph_relational=observation.graph_relational,
            )
            records.append(record)
            freq[(record.tick, record.identity)] = frequency_state(record, universe.omega)

    return records, freq


def evaluate(train_records, train_freq, test_records, test_freq, ridge=1e-6):
    train_x = np.asarray([train_freq[(r.tick, r.identity)] for r in train_records], float)
    train_y = np.asarray([
        r.coherence - prev.coherence
        for prev, r in zip(train_records, train_records[1:])
        if prev.identity == r.identity and r.tick == prev.tick + 1
    ], float)
    # Rebuild exact consecutive pairs to keep X/Y aligned.
    pairs = []
    by_id = {}
    for r in train_records:
        by_id.setdefault(r.identity, []).append(r)
    for items in by_id.values():
        items.sort(key=lambda r: r.tick)
    train_x, train_y = [], []
    for items in by_id.values():
        for a, b in zip(items, items[1:]):
            if b.tick != a.tick + 1:
                continue
            train_x.append(train_freq[(a.tick, a.identity)])
            train_y.append(b.coherence - a.coherence)

    by_id = {}
    for r in test_records:
        by_id.setdefault(r.identity, []).append(r)
    test_x, test_y = [], []
    for items in by_id.values():
        items.sort(key=lambda r: r.tick)
        for a, b in zip(items, items[1:]):
            if b.tick != a.tick + 1:
                continue
            test_x.append(test_freq[(a.tick, a.identity)])
            test_y.append(b.coherence - a.coherence)

    train_x, train_y = np.asarray(train_x, float), np.asarray(train_y, float)
    test_x, test_y = np.asarray(test_x, float), np.asarray(test_y, float)
    mean, scale = train_x.mean(0), train_x.std(0)
    scale[scale == 0] = 1
    X = np.column_stack((np.ones(len(train_x)), (train_x - mean) / scale))
    V = np.column_stack((np.ones(len(test_x)), (test_x - mean) / scale))
    reg = np.eye(X.shape[1]); reg[0, 0] = 0
    coef = np.linalg.solve(X.T @ X + ridge * reg, X.T @ train_y)
    pred = V @ coef

    rng = np.random.default_rng(390001)
    perm_mae = []
    for _ in range(25):
        shuffled = test_x.copy()
        rng.shuffle(shuffled)
        sp = np.column_stack((np.ones(len(shuffled)), (shuffled - mean) / scale)) @ coef
        perm_mae.append(float(np.mean(np.abs(test_y - sp))))

    zero = float(np.mean(np.abs(test_y)))
    model = float(np.mean(np.abs(test_y - pred)))
    return len(test_y), zero, model, float(np.mean(perm_mae)), zero - model


def main() -> None:
    print("GENESIS-2.34 local frequency-detuning transfer")
    source = tuple(range(390013, 390025))
    target = tuple(range(390025, 390037))
    source_records = [collect(seed) for seed in source]
    target_records = [collect(seed) for seed in target]

    results = []
    for target_seed, (target_records_i, target_freq_i) in zip(target, target_records):
        train_records = [r for pair in source_records for r in pair[0] if r.tick < 300]
        train_freq = {k: v for pair in source_records for k, v in pair[1].items() if k[0] < 300}
        test_records = [r for r in target_records_i if 450 <= r.tick < 600]
        test_freq = {k: v for k, v in target_freq_i.items() if 450 <= k[0] < 600}
        result = evaluate(train_records, train_freq, test_records, test_freq)
        results.append(result)
        print(target_seed, *result)

    arr = np.asarray(results, float)
    print("aggregate", len(results), int(np.sum(arr[:, 2] < arr[:, 1])), int(np.sum(arr[:, 2] < arr[:, 3])),
          float(arr[:, 1].mean()), float(arr[:, 2].mean()), float(arr[:, 3].mean()), float(arr[:, 4].mean()))


if __name__ == "__main__":
    main()
