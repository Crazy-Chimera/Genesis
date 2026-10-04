from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import numpy as np
from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec

@dataclass(frozen=True)
class StateDeltaEvaluationResult:
    samples: int
    zero_mae: float
    delta_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int
    include_terminal_state: bool
    @property
    def improvement(self) -> float:
        return self.zero_mae - self.delta_mae
    @property
    def beats_zero(self) -> bool:
        return self.delta_mae < self.zero_mae
    @property
    def beats_shuffled(self) -> bool:
        return self.delta_mae < self.shuffled_mae

class StateDeltaPredictor:
    """Predict next coherence innovation from observer-state pohyb."""
    def __init__(self, feature_name="combined", history_length=2, train_fraction=0.5,
                 ridge=1e-6, require_consecutive=True, include_terminal_state=False):
        if history_length < 2: raise ValueError("history_length must be >= 2")
        if not 0.0 < train_fraction < 1.0: raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0: raise ValueError("ridge must be >= 0")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches: raise ValueError(f"unknown state feature: {feature_name}")
        self.spec: StateFeatureSpec = matches[0]
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive
        self.include_terminal_state = include_terminal_state

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateDeltaEvaluationResult:
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return StateDeltaEvaluationResult(0,0.0,0.0,0.0,0,self.spec.name,self.history_length,self.include_terminal_state)
        lo, hi = ordered[0].tick, ordered[-1].tick
        heldout = lo + max(1, int((hi-lo)*self.train_fraction))
        groups = {}
        for item in ordered: groups.setdefault(item.identity, []).append(item)
        tx=[]; ty=[]; vx=[]; vy=[]
        for items in groups.values():
            items.sort(key=lambda x:x.tick)
            for i in range(self.history_length, len(items)):
                window=items[i-self.history_length:i]; target=items[i]
                ticks=[x.tick for x in window]+[target.tick]
                if self.require_consecutive and any(ticks[j+1] != ticks[j]+1 for j in range(len(ticks)-1)): continue
                states=[np.asarray(self.spec.feature(x),dtype=float) for x in window]
                if any(len(s)!=self.spec.width for s in states): continue
                deltas=[states[j+1]-states[j] for j in range(len(states)-1)]
                vals=[v for d in deltas for v in d]
                if self.include_terminal_state: vals.extend(states[-1])
                row=tuple(float(v) for v in vals)
                delta=target.coherence-window[-1].coherence
                (tx if target.tick < heldout else vx).append(row)
                (ty if target.tick < heldout else vy).append(delta)
        if not tx or not vx:
            return StateDeltaEvaluationResult(0,0.0,0.0,0.0,heldout,self.spec.name,self.history_length,self.include_terminal_state)
        train=np.asarray(tx,float); test=np.asarray(vx,float); y=np.asarray(ty,float)
        mean=train.mean(0); scale=train.std(0); scale[scale==0]=1
        X=np.column_stack((np.ones(len(train)),(train-mean)/scale))
        reg=np.eye(X.shape[1]); reg[0,0]=0
        coef=np.linalg.solve(X.T@X+self.ridge*reg,X.T@y)
        pred=np.column_stack((np.ones(len(test)),(test-mean)/scale))@coef
        shuffled=test.copy(); np.random.default_rng(390001).shuffle(shuffled)
        sp=np.column_stack((np.ones(len(shuffled)),(shuffled-mean)/scale))@coef
        actual=np.asarray(vy,float)
        return StateDeltaEvaluationResult(len(actual),float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual-pred))),float(np.mean(np.abs(actual-sp))),
            heldout,self.spec.name,self.history_length,self.include_terminal_state)
