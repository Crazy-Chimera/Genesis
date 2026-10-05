# GENESIS-2.32 / 2.33 — Rule-Transition Replication and Audit

## 2.32 — Independent unseen-seed replication

Source seeds: 390013–390024. Target seeds: 390025–390036. Training uses source ticks 0–299; target ticks 300–449 are excluded; evaluation uses target ticks 450–599.

Verified run: GENESIS-2.32 #1  
Commit: db1b2545d16cc9afce430cab8a24a155ce9fa1de  
Artifact: 11328144132  
Digest: sha256:3f0726fe525189b1f1a6ef63bfb8db57a8cf22dbbc40c8cb703ee2c5fa30f63d

- 4/12 beat zero-change baseline.
- 4/12 beat shuffled control.
- Mean zero MAE: 1.4750818143e-05
- Mean transition MAE: 2.1887873320e-05
- Mean shuffled MAE: 2.1718214706e-05
- Mean improvement: -7.1370551769e-06

Decision: **negative independent replication**.

## 2.33 — Permutation audit

The same 12 target cases were evaluated with 500 deterministic permutations per case. The fitted predictor is held fixed and the test representation rows are permuted to form the null distribution.

Verified run: GENESIS-2.33 #1  
Commit: b384543916951dbaca40dea517ecc9b2e99b771e  
Artifact: 11328890633  
Digest: sha256:cd543c1d1262d67299c3da7c3edcc7b11aa171946f0a94348b40221303b7fbea

- 3/12 cases had p < 0.05.
- Median p: 0.532934.
- Minimum p: 0.00199601.

Decision: **not sufficient evidence for a general transferable mechanism**. The isolated uncorrected positives do not establish a cross-seed effect, and multiplicity correction further weakens the claim.

## Branch decision

The rule-transition linear branch should not be further tuned as the primary route. The next experiment should use an independently motivated representation or mechanism while preserving:

- blocked-time separation,
- unseen-seed evaluation,
- zero-change baseline,
- permutation/shuffled controls,
- measurement-only universe,
- no prediction feedback,
- no goals, rewards, agency, self-model, or endogenous learning.

The correct scientific interpretation is a falsification/negative result for the tested mechanism, not a failure of GENESIS as a whole.
