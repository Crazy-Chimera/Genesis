from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.local import LocalPatchPredictor
from genesis.local_nonlinear import NonlinearLocalPatchPredictor
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.structural import StructuralPredictor


def collect(seed: int, ticks: int = 10_000):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    observer = LocalStructureObserver()
    tracker = RegionTracker(observer)
    memory = TemporalMemory()

    observations, events = tracker.observe_events(universe.phase)
    memory.record(universe.tick, observations, events)

    for _ in range(ticks):
        universe.step()
        observations, events = tracker.observe_events(universe.phase)
        memory.record(universe.tick, observations, events)

    return memory.all()


def main() -> None:
    print("seed samples baseline_mae structural_mae shuffled_mae improvement")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        predictor = StructuralPredictor(train_fraction=0.5, require_consecutive=True)
        for feature_names in (
            ("size",),
            ("boundary_contrast",),
            ("lifetime",),
            ("persistence",),
            ("overlap",),
            ("size", "boundary_contrast", "lifetime", "persistence", "overlap"),
        ):
            result = predictor.evaluate(records, feature_names)
            print(
                seed,
                ",".join(result.feature_names),
                result.samples,
                f"{result.baseline_mae:.15g}",
                f"{result.structural_mae:.15g}",
                f"{result.shuffled_mae:.15g}",
                f"{result.improvement:.15g}",
            )

        local = LocalPatchPredictor(
            train_fraction=0.5, require_consecutive=True, radius=1
        ).evaluate(records)
        print(
            "LOCAL_PATCH",
            seed,
            local.samples,
            f"{local.baseline_mae:.15g}",
            f"{local.local_mae:.15g}",
            f"{local.shuffled_mae:.15g}",
            f"{local.improvement:.15g}",
        )

        nonlinear = NonlinearLocalPatchPredictor(
            train_fraction=0.5, require_consecutive=True, radius=1
        ).evaluate(records)
        print(
            "LOCAL_QUADRATIC",
            seed,
            nonlinear.samples,
            f"{nonlinear.baseline_mae:.15g}",
            f"{nonlinear.nonlinear_mae:.15g}",
            f"{nonlinear.shuffled_mae:.15g}",
            f"{nonlinear.improvement:.15g}",
        )


if __name__ == "__main__":
    main()
