from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.local import LocalPatchPredictor
from genesis.local_nonlinear import NonlinearLocalPatchPredictor
from genesis.local_phase import PhasePatchPredictor
from genesis.local_gradient import LocalGradientPredictor
from genesis.local_motion import MotionPredictor
from genesis.boundary_flux import BoundaryFluxPredictor
from genesis.boundary_deformation import BoundaryDeformationPredictor
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

        phase = PhasePatchPredictor(
            train_fraction=0.5, require_consecutive=True, radius=1
        ).evaluate(records)
        print(
            "LOCAL_PHASE",
            seed,
            phase.samples,
            f"{phase.baseline_mae:.15g}",
            f"{phase.phase_mae:.15g}",
            f"{phase.shuffled_mae:.15g}",
            f"{phase.improvement:.15g}",
        )

        gradient = LocalGradientPredictor(
            train_fraction=0.5, require_consecutive=True, radius=1
        ).evaluate(records)
        print(
            "LOCAL_GRADIENT",
            seed,
            gradient.samples,
            f"{gradient.baseline_mae:.15g}",
            f"{gradient.gradient_mae:.15g}",
            f"{gradient.shuffled_mae:.15g}",
            f"{gradient.improvement:.15g}",
        )

        motion = MotionPredictor(
            train_fraction=0.5, require_consecutive=True
        ).evaluate(records)
        print(
            "LOCAL_MOTION",
            seed,
            motion.samples,
            f"{motion.baseline_mae:.15g}",
            f"{motion.motion_mae:.15g}",
            f"{motion.shuffled_mae:.15g}",
            f"{motion.improvement:.15g}",
        )

        flux = BoundaryFluxPredictor(
            train_fraction=0.5, require_consecutive=True
        ).evaluate(records)
        print(
            "BOUNDARY_FLUX",
            seed,
            flux.samples,
            f"{flux.baseline_mae:.15g}",
            f"{flux.flux_mae:.15g}",
            f"{flux.shuffled_mae:.15g}",
            f"{flux.improvement:.15g}",
        )

        deformation = BoundaryDeformationPredictor(
            train_fraction=0.5, require_consecutive=True
        ).evaluate(records)
        print(
            "BOUNDARY_DEFORMATION",
            seed,
            deformation.samples,
            f"{deformation.baseline_mae:.15g}",
            f"{deformation.deformation_mae:.15g}",
            f"{deformation.shuffled_mae:.15g}",
            f"{deformation.improvement:.15g}",
        )


if __name__ == "__main__":
    main()
