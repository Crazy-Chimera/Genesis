from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_delta import StateDeltaPredictor

def collect(seed, ticks=10_000):
    u=GenesisUniverse(GenesisConfig(seed=seed,ticks=ticks))
    t=RegionTracker(LocalStructureObserver()); m=TemporalMemory()
    o,e=t.observe_events(u.phase); m.record(u.tick,o,e)
    for _ in range(ticks):
        u.step(); o,e=t.observe_events(u.phase); m.record(u.tick,o,e)
    return m.all()

def main():
    print("GENESIS-2.13 state-delta trajectory benchmark")
    for seed in (390001,390002,390003):
        records=collect(seed)
        for terminal in (False,True):
            for h in (2,3,5,10):
                r=StateDeltaPredictor(feature_name="combined",history_length=h,
                    include_terminal_state=terminal,train_fraction=0.5,ridge=1e-6,
                    require_consecutive=True).evaluate(records)
                print(seed,int(terminal),h,r.samples,f"{r.zero_mae:.15g}",
                    f"{r.delta_mae:.15g}",f"{r.shuffled_mae:.15g}",
                    f"{r.improvement:.15g}",r.beats_zero,r.beats_shuffled)

if __name__=="__main__":
    main()
