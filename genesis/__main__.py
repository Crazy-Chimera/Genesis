import argparse

from .core import GenesisConfig, GenesisObserver, GenesisUniverse


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GENESIS-PW-001.")
    parser.add_argument("--ticks", type=int, default=100_000)
    args = parser.parse_args()

    config = GenesisConfig(ticks=args.ticks)
    universe = GenesisUniverse(config)
    observer = GenesisObserver()

    for _ in range(config.ticks):
        universe.step()

    result = observer.measure(universe)
    print(f"tick={result['tick']} coherence={result['coherence']:.9f}")


if __name__ == "__main__":
    main()
