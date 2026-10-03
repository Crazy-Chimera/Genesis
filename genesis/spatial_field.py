from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import numpy as np
from .memory import MemoryRecord

@dataclass(frozen=True)
class SpatialFieldEvaluationResult:
    samples: int
    baseline_mae: float
    field_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.field_mae

class SpatialFieldPredictor:
    """Predict next coherence from a fixed-orientation local phase field."""
    def __init__(self, train_fraction: float = 0.5, ridge: float = 1e-6, require_consecutive: bool = True):
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.train_fraction, self.ridge, self.require_consecutive = train_fraction, ridge, require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> SpatialFieldEvaluationResult:
        ordered=sorted(records,key=lambda x:(x.tick,x.identity))
        if not ordered: return SpatialFieldEvaluationResult(0,0,0,0,0)
        lo,hi=ordered[0].tick,ordered[-1].tick
        heldout=lo+max(1,int((hi-lo)*self.train_fraction))
        groups={}
        for item in ordered: groups.setdefault(item.identity,[]).append(item)
        train_x,train_y,test_x,test_y,baseline=[],[],[],[],[]
        for items in groups.values():
            items.sort(key=lambda x:x.tick)
            for i in range(1,len(items)):
                previous,target=items[i-1],items[i]
                if self.require_consecutive and target.tick!=previous.tick+1: continue
                if len(previous.spatial_field)!=18: continue
                if target.tick<heldout:
                    train_x.append(previous.spatial_field); train_y.append(target.coherence)
                else:
                    test_x.append(previous.spatial_field); test_y.append(target.coherence)
                    baseline.append(abs(target.coherence-previous.coherence))
        if not train_x or not test_x: return SpatialFieldEvaluationResult(0,0,0,0,heldout)
        train,test=np.asarray(train_x,dtype=float),np.asarray(test_x,dtype=float)
        mean,scale=train.mean(0),train.std(0); scale[scale==0]=1
        train,test=(train-mean)/scale,(test-mean)/scale
        xt=np.column_stack((np.ones(len(train)),train)); xv=np.column_stack((np.ones(len(test)),test))
        reg=np.eye(xt.shape[1]); reg[0,0]=0
        coef=np.linalg.solve(xt.T@xt+self.ridge*reg,xt.T@np.asarray(train_y))
        pred=xv@coef
        shuffled=test.copy(); np.random.default_rng(390001).shuffle(shuffled)
        sp=np.column_stack((np.ones(len(shuffled)),shuffled))@coef
        return SpatialFieldEvaluationResult(len(test_y),float(np.mean(baseline)),float(np.mean(np.abs(np.asarray(test_y)-pred))),float(np.mean(np.abs(np.asarray(test_y)-sp))),heldout)
