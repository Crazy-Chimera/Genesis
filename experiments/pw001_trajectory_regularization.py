from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_trajectory import StateTrajectoryPredictor


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
    print("GENESIS-2.13 trajectory regularization sweep")
    print("feature history ridge samples zero_mae trajectory_mae shuffled_mae improvement")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        for feature in ("structure", "local_patch", "phase_patch", "gradient_patch",
                        "motion", "boundary_flux", "spatial_field",
                        "multiscale_field", "relational", "graph_relational", "combined"):
            for history in (2, 3):
                for ridge in (1e-4, 1e-2, 1.0):
                    result = StateTrajectoryPredictor(
                        feature_name=feature,
                        history_length=history,
                        train_fraction=0.5,
                        ridge=ridge,
                        require_consecutive=True,
                    ).evaluate(records)
                    print(
                        seed, feature, history, ridge, result.samples,
                        f"{result.zero_mae:.15g}",
                        f"{result.trajectory_mae:.15g}",
                        f"{result.shuffled_mae:.15g}",
                        f"{result.improvement:.15g}",
                    )


if __name__ == "__main__":
    main()
