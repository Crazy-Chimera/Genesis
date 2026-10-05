# GENESIS-2.36 — Mechanistic One-Step Rule Prediction

Status: VERIFIED POSITIVE

Experiment: `experiments/pw001_mechanistic.py`  
Workflow: GENESIS-2.36 mechanistic benchmark #1  
Commit: `1fbb2966450f4ecc26d252150f4c6a945c9e1900`

Protocol:
- seeds: 390001–390006
- 2,000 ticks per seed
- mechanistic one-step prediction derived directly from the universe local update rule
- target: next coherence innovation
- baseline: zero-change prediction
- no coherence history as predictor input
- no feedback into the universe

| seed | samples | zero MAE | mechanistic MAE | improvement | beats zero |
|---:|---:|---:|---:|---:|---|
| 390001 | 2000 | 8.444411823e-06 | 3.535830459e-07 | +8.090828777e-06 | yes |
| 390002 | 2000 | 1.684121870e-05 | 3.486073891e-07 | +1.649261131e-05 | yes |
| 390003 | 2000 | 3.628382486e-06 | 3.553881476e-07 | +3.272994338e-06 | yes |
| 390004 | 2000 | 4.517595026e-06 | 3.514016777e-07 | +4.166193348e-06 | yes |
| 390005 | 2000 | 4.672357803e-06 | 3.489248535e-07 | +4.323432949e-06 | yes |
| 390006 | 2000 | 6.277700877e-06 | 3.516872357e-07 | +5.926013641e-06 | yes |

Conclusion:

GENESIS-2.36 is the first tested mechanism in this branch that beats the zero-change baseline on every tested seed. The predictor is tied directly to the local update rule rather than an increasingly large observer representation.

This result supports the narrower statement that the tested local rule-update information contains strong one-step predictive information about the next coherence innovation under the stated protocol.

It does not establish intelligence, agency, self-modeling, or endogenous learning. The predictor remains external and measurement-only, and its output is not fed back into `GenesisUniverse`.

Next criterion: independently validate the mechanistic signal under stronger controls and/or longer horizons before treating it as a stable property of PW-001.
