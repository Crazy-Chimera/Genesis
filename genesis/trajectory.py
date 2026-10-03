from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import numpy as np
from .memory import MemoryRecord

@dataclass(frozen=True)
class TrajectoryEvaluationResult:
    samples: int
    baseline_mae: float
    trajectory_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.trajectory_mae

class LocalTrajectoryPredictor:
    """Predict next coherence from the last N consecutive local phase fields."""
    def __init__(self, history_length: int = 3, train_fraction: float = 0.5,
                 ridge: float = 1e-6, require_consecutive: bool = True):
        if history_length < 2: raise ValueError("history_length must be >= 2")
        if not 0.0 < train_fraction < 1.0: raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0: raise ValueError("ridge must be >= 0")
        self.history_length, self.train_fraction = history_length, train_fraction
        self.ridge, self.require_consecutive = ridge, require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> TrajectoryEvaluationResult:
        ordered=sorted(records,key=lambda x:(x.tick,x.identity))
        if not ordered: return TrajectoryEvaluationResult(0,0,0,0,0)
        lo,hi=ordered[0].tick,ordered[-1].tick
        heldout=lo+max(1,int((hi-lo)*self.train_fraction))
        groups={}
        for item in ordered: groups.setdefault(item.identity,[]).append(item)
        tx,ty,vx,vy,base=[],[],[],[],[]
        for items in groups.values():
            items.sort(key=lambda x:x.tick)
            for i in range(self.history_length, len(items)):
                window=items[i-self.history_length:i]
                target=items[i]
                if self.require_consecutive and any(
                    window[j+1].tick != window[j].tick+1 for j in range(len(window)-1)
                ): continue
                if self.require_consecutive and target.tick != window[-1].tick+1: continue
                if any(len(x.spatial_field)!=18 for x in window): continue
                row=tuple(v for x in window for v in x.spatial_field)
                if target.tick<heldout: tx.append(row); ty.append(target.coherence)
                else: vx.append(row); vy.append(target.coherence); base.append(abs(target.coherence-window[-1].coherence))
        if not tx or not vx: return TrajectoryEvaluationResult(0,0,0,0,heldout)
        train,test=np.asarray(tx,float),np.asarray(vx,float)
        mean,scale=train.mean(0),train.std(0); scale[scale==0]=1
        train,test=(train-mean)/scale,(test-mean)/scale
        X=np.column_stack((np.ones(len(train)),train)); V=np.column_stack((np.ones(len(test)),test))
        reg=np.eye(X.shape[1]); reg[0,0]=0
        coef=np.linalg.solve(X.T@X+self.ridge*reg,X.T@np.asarray(ty))
        pred=V@coef
        shuffled=test.copy(); np.random.default_rng(390001).shuffle(shuffled)
        sp=np.column_stack((np.ones(len(shuffled)),shuffled))@coef
        return TrajectoryEvaluationResult(len(vy),float(np.mean(base)),
            float(np.mean(np.abs(np.asarray(vy)-pred))),
            float(np.mean(np.abs(np.asarray(vy)-sp))),heldout)
