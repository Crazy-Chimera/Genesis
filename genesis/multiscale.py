from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import numpy as np
from .memory import MemoryRecord

@dataclass(frozen=True)
class MultiscaleEvaluationResult:
    samples: int
    baseline_mae: float
    field_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.field_mae

class MultiscaleFieldPredictor:
    """Predict next coherence from radius-1 + radius-2 fixed-orientation phase fields."""
    def __init__(self, train_fraction: float = 0.5, ridge: float = 1e-6, require_consecutive: bool = True):
        if not 0.0 < train_fraction < 1.0: raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0: raise ValueError("ridge must be >= 0")
        self.train_fraction, self.ridge, self.require_consecutive = train_fraction, ridge, require_consecutive
    def evaluate(self, records: Iterable[MemoryRecord]) -> MultiscaleEvaluationResult:
        ordered=sorted(records,key=lambda x:(x.tick,x.identity))
        if not ordered: return MultiscaleEvaluationResult(0,0,0,0,0)
        lo,hi=ordered[0].tick,ordered[-1].tick
        heldout=lo+max(1,int((hi-lo)*self.train_fraction))
        groups={}
        for item in ordered: groups.setdefault(item.identity,[]).append(item)
        tx,ty,vx,vy,base=[],[],[],[],[]
        for items in groups.values():
            items.sort(key=lambda x:x.tick)
            for i in range(1,len(items)):
                p,t=items[i-1],items[i]
                if self.require_consecutive and t.tick!=p.tick+1: continue
                if len(p.multiscale_field)!=68: continue
                if t.tick<heldout: tx.append(p.multiscale_field); ty.append(t.coherence)
                else: vx.append(p.multiscale_field); vy.append(t.coherence); base.append(abs(t.coherence-p.coherence))
        if not tx or not vx: return MultiscaleEvaluationResult(0,0,0,0,heldout)
        train,test=np.asarray(tx,float),np.asarray(vx,float); mean,scale=train.mean(0),train.std(0); scale[scale==0]=1
        train,test=(train-mean)/scale,(test-mean)/scale
        X=np.column_stack((np.ones(len(train)),train)); V=np.column_stack((np.ones(len(test)),test))
        reg=np.eye(X.shape[1]); reg[0,0]=0
        coef=np.linalg.solve(X.T@X+self.ridge*reg,X.T@np.asarray(ty))
        pred=V@coef; shuffled=test.copy(); np.random.default_rng(390001).shuffle(shuffled)
        sp=np.column_stack((np.ones(len(shuffled)),shuffled))@coef
        return MultiscaleEvaluationResult(len(vy),float(np.mean(base)),float(np.mean(np.abs(np.asarray(vy)-pred))),float(np.mean(np.abs(np.asarray(vy)-sp))),heldout)
