from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np
from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec

@dataclass(frozen=True)
class NonlinearStateTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    nonlinear_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int
    random_features: int
    @property
    def improvement(self) -> float:
        return self.zero_mae - self.nonlinear_mae
    @property
    def beats_zero(self) -> bool:
        return self.nonlinear_mae < self.zero_mae
    @property
    def beats_shuffled(self) -> bool:
        return self.nonlinear_mae < self.shuffled_mae

class NonlinearStateTrajectoryPredictor:
    """Predict next coherence innovation with deterministic nonlinear random features."""
    def __init__(self, feature_name="combined", history_length=2, train_fraction=0.5,
                 ridge=1e-4, random_features=256, random_seed=390001,
                 require_consecutive=True):
        if history_length < 2: raise ValueError("history_length must be >= 2")
        if not 0.0 < train_fraction < 1.0: raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0: raise ValueError("ridge must be >= 0")
        if random_features < 1: raise ValueError("random_features must be >= 1")
        matches=[s for s in STATE_FEATURES_WITH_COMBINED if s.name==feature_name]
        if not matches: raise ValueError(f"unknown state feature: {feature_name}")
        self.spec: StateFeatureSpec=matches[0]
        self.history_length=history_length; self.train_fraction=train_fraction
        self.ridge=ridge; self.random_features=random_features
        self.random_seed=random_seed; self.require_consecutive=require_consecutive

    def _design(self, x, mean, scale, weights, bias):
        normalized=(x-mean)/scale
        hidden=np.tanh(normalized@weights+bias)
        return np.column_stack((np.ones(len(x)),hidden))

    def evaluate(self, records: Iterable[MemoryRecord]):
        ordered=sorted(records,key=lambda x:(x.tick,x.identity))
        if not ordered:
            return NonlinearStateTrajectoryEvaluationResult(0,0,0,0,0,self.spec.name,self.history_length,self.random_features)
        lo,hi=ordered[0].tick,ordered[-1].tick
        heldout=lo+max(1,int((hi-lo)*self.train_fraction))
        groups={}
        for item in ordered: groups.setdefault(item.identity,[]).append(item)
        tx,ty,vx,vy=[],[],[],[]
        for items in groups.values():
            items.sort(key=lambda x:x.tick)
            for i in range(self.history_length,len(items)):
                window=items[i-self.history_length:i]; target=items[i]
                ticks=[x.tick for x in window]+[target.tick]
                if self.require_consecutive and any(ticks[j+1]!=ticks[j]+1 for j in range(len(ticks)-1)): continue
                vectors=[tuple(float(v) for v in self.spec.feature(x)) for x in window]
                if any(len(v)!=self.spec.width for v in vectors): continue
                row=tuple(v for vec in vectors for v in vec)
                delta=target.coherence-window[-1].coherence
                if target.tick<heldout: tx.append(row); ty.append(delta)
                else: vx.append(row); vy.append(delta)
        if not tx or not vx:
            return NonlinearStateTrajectoryEvaluationResult(0,0,0,0,heldout,self.spec.name,self.history_length,self.random_features)
        train=np.asarray(tx,float); test=np.asarray(vx,float); y=np.asarray(ty,float); actual=np.asarray(vy,float)
        mean=train.mean(0); scale=train.std(0); scale[scale==0]=1
        rng=np.random.default_rng(self.random_seed)
        weights=rng.normal(0.0,1.0/np.sqrt(train.shape[1]),(train.shape[1],self.random_features))
        bias=rng.uniform(-np.pi,np.pi,self.random_features)
        design=self._design(train,mean,scale,weights,bias)
        test_design=self._design(test,mean,scale,weights,bias)
        reg=np.eye(design.shape[1]); reg[0,0]=0
        coef=np.linalg.solve(design.T@design+self.ridge*reg,design.T@y)
        pred=test_design@coef
        shuffled=test.copy(); np.random.default_rng(self.random_seed).shuffle(shuffled)
        shuffled_pred=self._design(shuffled,mean,scale,weights,bias)@coef
        return NonlinearStateTrajectoryEvaluationResult(
            len(actual),float(np.mean(np.abs(actual))),float(np.mean(np.abs(actual-pred))),
            float(np.mean(np.abs(actual-shuffled_pred))),heldout,self.spec.name,self.history_length,self.random_features)
