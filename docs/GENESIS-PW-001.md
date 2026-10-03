# GENESIS-PW-001 — Primordial Emergence Experiment

## Purpose

Test whether persistent relational structures can emerge from local oscillator rules without hard-coding entities, language, goals, meaning, or intelligence.

## Universe

The GENESIS universe contains only oscillator state and local interaction rules. The observer is external and measurement-only.

### GENESIS-1.0

- 16x16 periodic lattice = 256 oscillators
- deterministic seed: 390001
- local four-neighbour coupling
- deterministic noise
- 100,000 ticks
- global coherence measurement

### GENESIS-1.1

The external observer adds a local coherence field and connected-region detection.

A detected coherent region is **not an entity**. It is an observer measurement. The universe does not store cluster labels and detection does not modify oscillator phases.

### GENESIS-1.2

The observer adds persistence, lifetime, boundary contrast, and Jaccard identity overlap.

Region identity is assigned by the observer using spatial overlap only. It is not part of the universe state.

### GENESIS-1.3

The observer adds a lifecycle event stream:

- **birth** — a measured region has no qualifying predecessor.
- **growth** — a tracked region gains cells.
- **decay** — a tracked region loses cells.
- **split** — one predecessor overlaps multiple current regions.
- **merge** — one current region overlaps multiple predecessors.
- **death** — a predecessor has no qualifying successor.

These are observer-level classifications of measured region sets. They are not causal mechanisms inside the universe.

### GENESIS-1.4

An external temporal memory records measured region observations and lifecycle events.

Each memory record contains:

- tick
- observer identity
- cells
- coherence
- boundary contrast
- lifetime
- persistence
- overlap
- lifecycle event kinds

TemporalMemory is append-only observer state. It does not write anything into GenesisUniverse, alter oscillator state, or create endogenous memory.

This layer is deliberately descriptive. Recording history does not imply that the universe itself remembers.

### GENESIS-1.5

An external predictive-memory layer evaluates whether temporal traces contain information about the next observed region state beyond a persistence baseline.

The baseline predicts that the next scalar feature remains equal to the most recent observation. The history predictor extrapolates a linear trend from a bounded history window. Prediction quality is measured with mean absolute error (MAE).

The predictor is measurement-only:

- it reads MemoryRecord values
- it does not modify GenesisUniverse
- it does not write back into TemporalMemory
- it does not introduce goals, rewards, agency, meaning, language, or self-models

A history-based predictor is considered empirically useful for this experiment only when its error is lower than the baseline on held-out transitions. This is a test of predictive information, not a claim of intelligence.
### GENESIS-1.5 empirical substrate experiment

The first direct experiment was run on the actual GENESIS-PW-001 substrate trajectory for ticks 0–10,000 using the same universe parameters and observer/tracker rules as the reference implementation.

For each observer-tracked identity, the experiment compared a persistence baseline with the linear history predictor over a three-record history window. The target was the next recorded observation for that identity. MAE was used as the error metric.

Observed result:

| feature | samples | persistence MAE | history MAE | improvement |
|---|---:|---:|---:|---:|
| coherence | 189,681 | 0.0001195000050 | 0.0000353671743 | +0.0000841328307 |
| region size | 189,681 | 0.000506112895 | 0.001012225790 | -0.000506112895 |

The trajectory produced 189,783 observer records across 102 observer-assigned identities during the 10,000-tick interval.

The result is feature-specific. Coherence contained measurable short-history predictive information under this predictor, while region size did not benefit from the same linear model. This does not establish intelligence, agency, or self-modeling. It establishes only that one measured property of the observed trajectory was more predictable from short history than from a last-value baseline under the stated experiment.

The experiment remains external to the universe rules. No prediction is fed back into GenesisUniverse, GenesisConfig, phase, omega, or the coupling rule.

### GENESIS-1.6 — predictive evaluation protocol

GENESIS-1.6 separates **model selection from evaluation** by using a chronological walk-forward holdout.

Protocol:

1. Sort observer records chronologically within each observer identity.
2. Define a future holdout boundary from the configured chronological split.
3. Evaluate only targets at or after that boundary.
4. By default, require the target and its history window to occupy exact consecutive ticks. Missing observations are therefore not silently treated as adjacent.
5. Compare three predictors:
   - persistence baseline — repeat the latest observed value;
   - linear history predictor — extrapolate the recent bounded history;
   - shuffled-history null — apply the same linear predictor after a deterministic permutation of the history values.
6. Report MAE for each predictor and the history predictor's improvement over persistence.
7. Keep the evaluation entirely external to GenesisUniverse and TemporalMemory.

The shuffled-history null is not a statistical proof by itself. It is a diagnostic control: if the ordered history predictor cannot outperform a permutation of the same observed values, the apparent temporal advantage is weakened.

The evaluation result records:

- sample count
- persistence MAE
- ordered-history MAE
- shuffled-history MAE
- chronological holdout boundary
- history length

This protocol addresses the principal GENESIS-1.5 limitation: the earlier experiment evaluated next-record transitions across possible observation gaps and did not isolate a future holdout interval.

GENESIS-1.6 still does **not** introduce learning objectives, rewards, agency, endogenous memory, meaning, language, or self-modeling. It only strengthens the measurement of predictive information.


### GENESIS-1.6 empirical evaluation

The strengthened evaluation was run on the actual PW-001 trajectory from tick 0 through tick 10,000. It used the current observer, region tracker, temporal memory, and PredictiveEvaluator with a 50% chronological holdout and exact consecutive-tick transitions.

| history length | samples | persistence MAE | ordered-history MAE | shuffled-history MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 1 | 103,931 | 0.000663902012 | 0.000663902012 | 0.000663902012 | 0.000000000000 |
| 2 | 103,885 | 0.000664195986 | 0.001328391972 | 0.001684555036 | -0.000664195986 |
| 3 | 103,839 | 0.000664490220 | 0.001328980441 | 0.002214967401 | -0.000664490220 |
| 5 | 103,747 | 0.000665079472 | 0.001315700695 | 0.003279130962 | -0.000650621491 |
| 10 | 103,517 | 0.000666557183 | 0.001298220377 | 0.005427713380 | -0.000631663910 |

The trajectory again contained 189,783 observer records across 102 observer-assigned identities. Under the stricter next-tick holdout, the linear history predictor did not beat the persistence baseline for coherence at any tested history length.

This result changes the interpretation of GENESIS-1.5. The earlier positive result was obtained on the next recorded observation for an identity, where observations could be separated by missing ticks. GENESIS-1.6 removes that ambiguity by requiring exact consecutive ticks and a chronological future holdout. The earlier apparent predictive advantage therefore cannot be treated as evidence of next-tick predictive information.

The shuffled-history control also does not rescue the linear predictor: its error is larger than the ordered-history error for history lengths 2–10, but both are worse than persistence. This means the ordered temporal values contain some structure that the linear extrapolator is exploiting, while that particular extrapolation rule is nevertheless inferior to simply retaining the latest value.

**GENESIS-1.6 conclusion:** Under the single linear-vs-persistence comparison, PW-001 did not demonstrate a predictive advantage. GENESIS-1.6b supersedes this as the broader baseline-suite evaluation while retaining the GENESIS-1.6 result as an explicit methodological control.

Reproduction entry point: experiments/pw001_predictive_eval.py.



### GENESIS-1.6b — baseline suite and seed robustness

GENESIS-1.6b extends the strict next-tick evaluation with a second naive baseline and tests whether the observed result depends on the initial random seed.

The evaluation compares:

- **persistence** — repeat the latest value;
- **mean history** — predict the arithmetic mean of the recent history window;
- **ordered linear history** — extrapolate the recent history;
- **shuffled linear history** — apply the same linear predictor after a deterministic permutation of the same history.

The PW-001 experiment was executed in a clean GitHub Actions environment for 10,000 ticks. The strict protocol remained unchanged: 50% chronological holdout and exact consecutive-tick histories.

For the reference seed 390001:

| history length | samples | persistence MAE | linear MAE | mean MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 103,885 | 0.000120540651 | 0.000043602189 | 0.000180697755 | 0.000199595043 | +0.000076938461 |
| 3 | 103,839 | 0.000120511918 | 0.000043305745 | 0.000240728909 | 0.000297553269 | +0.000077206174 |
| 5 | 103,747 | 0.000120453902 | 0.000043119177 | 0.000360311497 | 0.000464316125 | +0.000077334724 |
| 10 | 103,517 | 0.000120311442 | 0.000043049732 | 0.000656780671 | 0.000872442258 | +0.000077260974 |

The result was reproduced with two additional initial seeds:

| seed | history | persistence MAE | linear MAE | mean MAE | shuffled MAE |
|---:|---:|---:|---:|---:|---:|
| 390002 | 2 | 0.000097256523 | 0.000028650330 | 0.000145835352 | 0.000159368795 |
| 390002 | 3 | 0.000097225676 | 0.000028320944 | 0.000194330659 | 0.000233506190 |
| 390002 | 5 | 0.000097163027 | 0.000028180159 | 0.000291157521 | 0.000372050680 |
| 390002 | 10 | 0.000097007272 | 0.000028230802 | 0.000532262674 | 0.000688440461 |
| 390003 | 2 | 0.000107100653 | 0.000034457494 | 0.000160559202 | 0.000177287056 |
| 390003 | 3 | 0.000107081617 | 0.000034143436 | 0.000213928813 | 0.000263198332 |
| 390003 | 5 | 0.000107043112 | 0.000034009959 | 0.000320449550 | 0.000404884434 |
| 390003 | 10 | 0.000106948247 | 0.000033802074 | 0.000584235188 | 0.000766197363 |

Across all three seeds and all tested history lengths, the ordered linear predictor has lower MAE than both persistence and mean-history baselines, while the shuffled-history control has higher MAE than the ordered predictor.

This is evidence that, under the stated measurement and evaluation protocol, the observed coherence trajectory contains reproducible short-history predictive structure. It remains a statement about the measured trajectory and the tested predictor, not evidence of intelligence, agency, self-modeling, or endogenous learning.

The universe rules remain unchanged and prediction is not fed back into the universe.

Reproduction entry points:

- `experiments/pw001_predictive_eval.py`
- `experiments/pw001_robustness.py`

The experiment artifact was produced by the GitHub Actions workflow `PW-001 experiment` from commit `fdc5a098cfae53ea377c66892481ef24e7fbdec2`.

## Measurement rule

For regions A and B:

J(A,B) = |A intersection B| / |A union B|

A current region inherits a previous identity when J(A,B) >= overlap_threshold and that previous identity has not already been assigned in the current frame.

Lifecycle events are then derived from the overlap graph between consecutive observation frames.

## Non-interference rule

GENESIS-1.6 must not:

- write identities, lifecycle events, or memory records into GenesisUniverse
- modify phase, frequency, amplitude, coupling, or noise
- introduce endogenous memory
- introduce goals, meaning, language, agency, or self-models

The next experimental question is predictive value: whether the temporal trace contains information about a future region state beyond a suitable baseline.


## GENESIS-1.7 — structure-only causal probe

GENESIS-1.7 asks whether the short-history predictive structure observed in GENESIS-1.6b can be explained by the observer's measured region structure alone.

The new predictor uses only these observer-level measurements from the previous consecutive frame:

- region size
- boundary contrast
- lifetime
- persistence
- overlap

Current coherence is deliberately excluded from the predictor inputs. The model is trained only on the chronological pre-holdout portion and evaluated on the future holdout. A deterministic permutation of the held-out structural rows provides a control.

The universe rules are unchanged. The predictor remains external and measurement-only.

### Clean CI result

Run: PW-001 experiment #5  
Commit: `69be0fb4331e33de78b7742193e58fa6b8dd6e4c`

| seed | samples | persistence MAE | structure-only MAE | shuffled structure MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.043121575274 | 0.065012893657 | -0.043001005822 |
| 390002 | 93990 | 0.000097287754 | 0.043784649968 | 0.062749533591 | -0.043687362213 |
| 390003 | 86979 | 0.000107119591 | 0.046144387078 | 0.063992656782 | -0.046037267488 |

Across all three seeds, the structure-only model does not beat persistence. The shuffled control is worse than the ordered structure-only model, so the model does use information contained in the structural features, but that information is not sufficient for next-step coherence prediction under this model and protocol.

This result narrows the interpretation of GENESIS-1.6b: the observed predictive advantage of coherence history is not reproduced by this aggregate structure-only model. It does not prove that structural information is irrelevant; individual structural variables, alternative horizons, or different model classes remain open questions.

GENESIS-1.7 therefore separates two observations:

1. **Temporal coherence history is predictive under the GENESIS-1.6b protocol.**
2. **The current aggregate region-structure representation does not explain that predictive advantage by itself.**

No predictive output is fed back into the universe.


## GENESIS-1.7b — per-feature structural isolation

GENESIS-1.7b isolates the five observer-level structural inputs used by GENESIS-1.7. The purpose is to determine whether the failure of the aggregate structure-only model is caused by one particular feature, by their combination, or by the representation/model class as a whole.

The tested feature sets are:

- size
- boundary_contrast
- lifetime
- persistence
- overlap
- all five together

Coherence is excluded from every structural predictor. The evaluation uses the same chronological holdout and exact-consecutive-tick protocol as GENESIS-1.6b. A deterministic shuffled structural control is evaluated alongside each ordered predictor.

### Clean CI result

Run: PW-001 experiment #7  
Commit: 4a20f186c2e35cc8ee30371830ef109c70e518af

| seed | feature set | samples | persistence MAE | structural MAE | shuffled MAE | improvement |
|---:|---|---:|---:|---:|---:|---:|
| 390001 | size | 103931 | 0.000120569452 | 0.057199585985 | 0.054984347729 | -0.057079016533 |
| 390001 | boundary_contrast | 103931 | 0.000120569452 | 0.049412267523 | 0.064658559774 | -0.049291698070 |
| 390001 | lifetime | 103931 | 0.000120569452 | 0.051418189842 | 0.055048264973 | -0.051297620390 |
| 390001 | persistence | 103931 | 0.000120569452 | 0.051418189842 | 0.055048264973 | -0.051297620390 |
| 390001 | overlap | 103931 | 0.000120569452 | 0.053653946617 | 0.053693731953 | -0.053533377165 |
| 390001 | all five | 103931 | 0.000120569452 | 0.043121575274 | 0.065012893657 | -0.043001005822 |
| 390002 | size | 93990 | 0.000097287754 | 0.051237922991 | 0.051296161240 | -0.051140635237 |
| 390002 | boundary_contrast | 93990 | 0.000097287754 | 0.044191604450 | 0.061039098378 | -0.044094316696 |
| 390002 | lifetime | 93990 | 0.000097287754 | 0.054404354304 | 0.058205446404 | -0.054307066550 |
| 390002 | persistence | 93990 | 0.000097287754 | 0.054404354304 | 0.058205446404 | -0.054307066550 |
| 390002 | overlap | 93990 | 0.000097287754 | 0.051161773297 | 0.051186657764 | -0.051064485543 |
| 390002 | all five | 93990 | 0.000097287754 | 0.043784649967 | 0.062749533591 | -0.043687362213 |
| 390003 | size | 86979 | 0.000107119591 | 0.057716891673 | 0.058759001549 | -0.057609772083 |
| 390003 | boundary_contrast | 86979 | 0.000107119591 | 0.049483490406 | 0.062099979025 | -0.049376370816 |
| 390003 | lifetime | 86979 | 0.000107119591 | 0.056430813483 | 0.059380056509 | -0.056323693892 |
| 390003 | persistence | 86979 | 0.000107119591 | 0.056430813483 | 0.059380056509 | -0.056323693892 |
| 390003 | overlap | 86979 | 0.000107119591 | 0.058399288586 | 0.058416556382 | -0.058292168996 |
| 390003 | all five | 86979 | 0.000107119591 | 0.046144387078 | 0.063992656782 | -0.046037267488 |

The per-feature result is consistent across all three seeds: no isolated structural feature beats persistence, and the five-feature combination also remains far above the persistence error. The best aggregate structural MAE in each seed is approximately 0.043–0.046, whereas persistence remains approximately 0.000097–0.000121.

The shuffled controls are not uniformly worse than the ordered predictors for every isolated feature. Therefore the shuffled comparison should be treated only as a diagnostic control, not as proof that every feature carries independently ordered temporal information.

### Interpretation

GENESIS-1.7b strengthens the negative result from GENESIS-1.7. Under the tested linear structural model and representation:

1. no individual measured structural feature explains the GENESIS-1.6b coherence prediction advantage;
2. combining all five measured structural features does not explain it either;
3. the predictive signal therefore remains associated with the measured coherence history rather than with these aggregate region statistics under the tested model.

This still does not identify the physical source of the predictive signal. It leaves open spatially local variables, phase-derived quantities other than global coherence, alternative temporal horizons, nonlinear predictors, and other observer representations.

The result also does not establish causality: all structural quantities are observer measurements derived from the same underlying universe trajectory.

No predictive output is fed back into GenesisUniverse.

Reproduction entry point: experiments/pw001_structural_eval.py.


## GENESIS-1.7c — spatially local patch probe

GENESIS-1.7c tests whether the predictive structure left unexplained by aggregate region statistics is present in the immediate spatial neighborhood of a measured region.

The observer records a centroid-centered 3×3 periodic local-coherence patch for each tracked region. The patch is persisted in TemporalMemory, but it remains an observer measurement: the universe does not store the patch and no prediction is fed back into the universe.

The local predictor uses only the previous consecutive local patch to predict the next region coherence. It does not use coherence history, region-level structural features, goals, rewards, or any endogenous state. The evaluation uses the same chronological 50% holdout and exact-consecutive-tick requirement as GENESIS-1.6b. A deterministic shuffled-patch control is evaluated alongside the ordered predictor.

### Clean CI result

Run: PW-001 experiment #13  
Commit: `c633d79690223e8ba4ff92d41e83cbdbe4bdf4f8`

| seed | samples | persistence MAE | local-patch MAE | shuffled-patch MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.023174929106 | 0.081205220928 | -0.023054359653 |
| 390002 | 93990 | 0.000097287754 | 0.023363792751 | 0.072392853747 | -0.023266504997 |
| 390003 | 86979 | 0.000107119591 | 0.047296662074 | 0.063986074905 | -0.047189542483 |

Across all three seeds, the local-patch predictor does not beat persistence. The ordered local patch is nevertheless substantially better than its shuffled control in every seed, so the local representation contains temporally structured information that the tested ridge model can partially exploit. That information is not sufficient to explain the much smaller error achieved by the coherence-history predictor in GENESIS-1.6b.

### Interpretation

GENESIS-1.7c narrows the representation question further:

1. aggregate region statistics do not explain the GENESIS-1.6b coherence prediction advantage under the tested linear model;
2. individual aggregate structural features do not explain it;
3. a centroid-centered 3×3 local coherence patch also does not explain it under the tested linear model;
4. the local patch still carries measurable temporal structure, as shown by its improvement over the shuffled-patch control.

The remaining result is therefore specifically about representation **and model class**. It does not establish that spatial structure is irrelevant, because the current probe compresses the neighborhood into a 3×3 scalar patch centered on the previous region centroid and then applies a linear ridge model. It leaves open larger spatial contexts, phase-derived local features, multi-step horizons, nonlinear predictors, and representations that preserve region-relative geometry without centroid alignment.

No predictive output is fed back into GenesisUniverse. GENESIS-1.7c therefore remains an external measurement experiment, not an endogenous learning mechanism.

Reproduction entry point: `experiments/pw001_structural_eval.py` (the `LOCAL_PATCH` probe).


## GENESIS-1.7d — nelineární lokální patch

GENESIS-1.7d testuje, zda GENESIS-1.7c selhává pouze proto, že vztah mezi 3×3 lokálním coherence patchem a následující koherencí není lineární. K předchozímu lokálnímu patchi proto přidáváme kvadratické členy všech patchových složek a ridge regularizaci. Vstupem zůstává pouze předchozí lokální patch; coherence history ani aggregate region statistics nejsou použity jako prediktory.

Protokol zůstává shodný s GENESIS-1.6b/1.7c: chronologický 50% holdout, přesně po sobě jdoucí tick a persistence baseline. Součástí je deterministicky zamíchaný lokální patch jako kontrola.

### Clean CI result

Run: PW-001 experiment #16  
Commit: `f94bbf0d4c7eda89b48f91430a6e73aa4aebde86`

| seed | samples | persistence MAE | nonlinear local MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.024248702709 | 0.079331006662 | -0.024128133256 |
| 390002 | 93990 | 0.000097287754 | 0.017138120905 | 0.071630001523 | -0.017040833151 |
| 390003 | 86979 | 0.000107119591 | 0.027937330220 | 0.077322828039 | -0.027830210630 |

Kvadratický lokální model v žádném ze tří seedů nepřekonal persistence baseline. Ve všech případech je jeho MAE řádově vyšší než persistence MAE. Ordered nonlinear patch je současně výrazně lepší než shuffled control, takže lokální patch obsahuje časově strukturovanou informaci, kterou model využívá; tato informace však v testovaném kvadratickém modelu nevysvětluje prediktivní výhodu coherence history z GENESIS-1.6b.

### Interpretation

GENESIS-1.7d zužuje hypotézu z GENESIS-1.7c:

1. lineární ridge model lokálního 3×3 patche nepřekonává persistence;
2. kvadratické rozšíření stejného 3×3 reprezentace také nepřekonává persistence;
3. proto samotná nelinearita modelu není v tomto testu dostatečným vysvětlením rozdílu mezi lokálním patchem a coherence-history prediktorem;
4. hlavní signál z GENESIS-1.6b zůstává v rámci tohoto experimentálního designu nevysvětlen.

Tento výsledek stále neříká, že lokální prostorová informace není relevantní. Testována byla pouze konkrétní centroidově zarovnaná 3×3 coherence reprezentace a konkrétní kvadratický ridge model. Další rozumný krok je proto změna **reprezentace**, nikoli další zvyšování složitosti stejného modelu — například phase-derived local features nebo zachování lokální geometrie bez centroidové komprese.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení. Predikce zůstávají čistě externím měřením a nejsou zpětně vloženy do GenesisUniverse.

Reprodukční vstup: `experiments/pw001_structural_eval.py` (řádek `LOCAL_QUADRATIC`).
