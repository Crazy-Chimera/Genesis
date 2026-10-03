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


## GENESIS-1.8 — lokální relativní fáze

GENESIS-1.8 mění pouze lokální reprezentaci měřeného stavu. Pro každý observer-detekovaný region se ukládá centroidově zarovnaný 3×3 patch relativních fází ve formě dvojic `(sin Δφ, cos Δφ)`, kde Δφ je fáze vůči středu patchu. Absolutní fáze tedy není prediktoru přímo předávána.

Prediktor používá pouze předchozí `phase_patch`, ridge regresi a stejný chronologický 50% holdout s požadavkem na přesně po sobě jdoucí tick. Persistence zůstává baseline a zamíchaný patch je kontrola. Universe rules se nemění a prediktor neposílá žádnou zpětnou vazbu do `GenesisUniverse`.

### Clean PW-001 result

Run: PW-001 experiment #20  
Commit: `20cb6e565b0a6cd4c1e54357b101736e40fd4fe4`

| seed | samples | persistence MAE | phase-patch MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.048083425627 | 0.066787142627 | -0.047962856175 |
| 390002 | 93990 | 0.000097287754 | 0.048990027315 | 0.062524097114 | -0.048892739562 |
| 390003 | 86979 | 0.000107119591 | 0.053485890305 | 0.066156441546 | -0.053378770714 |

Fázový patch v této reprezentaci nepřekonal persistence baseline v žádném ze tří seedů. Ordered phase patch byl současně lepší než shuffled control ve všech třech případech, takže reprezentace obsahuje časově strukturovanou informaci, ale testovaný lineární prediktor ji nedokáže využít k překonání persistence.

### Interpretation

GENESIS-1.8 dále zužuje vysvětlení signálu z GENESIS-1.6b:

1. aggregate region statistics jej nevysvětlují v testovaných modelech;
2. centroidově zarovnaný 3×3 coherence patch jej nevysvětluje;
3. kvadratické rozšíření stejného coherence patchu jej nevysvětluje;
4. relativní phase patch `(sin Δφ, cos Δφ)` jej v testovaném lineárním modelu rovněž nevysvětluje.

To není důkaz, že prostorová nebo fázová informace není relevantní. Testována byla konkrétní lokální reprezentace, konkrétní velikost patchu a konkrétní lineární ridge model. Další experiment by měl proto před dalším zvyšováním modelové složitosti ověřit jinou **reprezentaci prostorového stavu**, například lokální gradient/flux nebo zachování orientované geometrie bez centroidové komprese.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení. Jde stále o externí predikční analýzu observer-level paměti.

Reprodukční vstup: `experiments/pw001_structural_eval.py` (řádek `LOCAL_PHASE`).


## GENESIS-1.9 — lokální gradient / flux reprezentace

GENESIS-1.9 testuje jinou lokální reprezentaci prostorového stavu: orientované zabalené fázové gradienty v centroidově zarovnaném 3×3 poli. Pro každou pozici jsou uloženy dvě složky:

- dx — wrapped rozdíl fáze mezi buňkou a jejím pravým sousedem;
- dy — wrapped rozdíl fáze mezi buňkou a sousedem pod ní.

Rozdíly jsou počítány přes periodickou geometrii a reprezentovány v intervalu [-π, π]. Výsledkem je 18 hodnot pro radius 1. Reprezentace je observer-level a není zapisována do GenesisUniverse.

Prediktor používá pouze předchozí gradientový patch, lineární ridge regresi, chronologický 50% holdout a požadavek na přesně po sobě jdoucí tick. Persistence zůstává baseline a deterministicky zamíchaný gradientový patch je kontrola.

### Clean PW-001 result

Run: PW-001 experiment #24  
Commit: 5b1257ba1b7dd9e0054c899c0529ee52a3bc404f

| seed | samples | persistence MAE | gradient MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.059232644235 | 0.058862640413 | -0.059112074783 |
| 390002 | 93990 | 0.000097287754 | 0.052823362513 | 0.054479135712 | -0.052726074759 |
| 390003 | 86979 | 0.000107119591 | 0.061462964228 | 0.062034467792 | -0.061355844638 |

Lokální gradientový model nepřekonal persistence v žádném ze tří seedů. Rozdíl proti baseline je přibližně o dva až tři řády větší než chyba persistence.

Shuffled kontrola není ve všech seedech horší než ordered gradient: u seedu 390001 je shuffled MAE dokonce mírně nižší než ordered MAE. Proto tento experiment neposkytuje důkaz, že tato konkrétní gradientová reprezentace obsahuje využitelnou časovou prediktivní informaci.

### Interpretation

GENESIS-1.9 dále zužuje hypotézu o zdroji signálu z GENESIS-1.6b:

1. aggregate region statistics jej nevysvětlují v testovaných modelech;
2. jednotlivé aggregate structural features jej nevysvětlují;
3. centroidově zarovnaný 3×3 coherence patch jej nevysvětluje;
4. kvadratické rozšíření stejného patchu jej nevysvětluje;
5. relativní phase patch (sin Δφ, cos Δφ) jej nevysvětluje;
6. orientovaný lokální gradientový patch jej rovněž nevysvětluje v testovaném lineárním modelu.

Důležité je, že 1.9 současně neposkytuje pozitivní shuffled-control signál. To znamená, že další krok by neměl být interpretován jako „gradient byl téměř správně“. Experiment pouze vylučuje tuto konkrétní reprezentaci a model v rámci daného protokolu.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení. Universe rules zůstaly nezměněny a žádná predikce nebyla vrácena do GenesisUniverse.

Reprodukční vstup: experiments/pw001_structural_eval.py (řádek LOCAL_GRADIENT).


## GENESIS-2.0 — relativní pohyb regionu

Po vyčerpání několika lokálních patchových reprezentací testuje GENESIS-2.0 přímo pohyb měřeného regionu mezi dvěma po sobě jdoucími rámci. Observer ukládá:

- periodický posun centroidu v ose řádků;
- periodický posun centroidu v ose sloupců;
- změnu velikosti regionu.

Jde pouze o observer-level veličiny. GenesisUniverse není změněn a predikce není vracena do simulace.

### Clean PW-001 result

Run: PW-001 experiment #28  
Commit: a583ba91852a7ab7356243557870538bcd63d78e

| seed | samples | persistence MAE | motion MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103885 | 0.000120540651 | 0.053682126270 | 0.053681799408 | -0.053561585619 |
| 390002 | 93951 | 0.000097256523 | 0.051163088992 | 0.051165723885 | -0.051065832470 |
| 390003 | 86937 | 0.000107100653 | 0.058401544083 | 0.058402856938 | -0.058294443429 |

Motion-only model nepřekonal persistence v žádném ze tří seedů. Ordered a shuffled MAE jsou prakticky totožné ve všech seedech, takže tato reprezentace neposkytuje v rámci protokolu důkaz využitelného časového prediktivního signálu.

### Interpretation

GENESIS-2.0 rozšiřuje dosavadní negativní mapu:

1. aggregate region statistics — bez vysvětlení signálu;
2. jednotlivé strukturální veličiny — bez vysvětlení;
3. local coherence patch — bez vysvětlení;
4. quadratic local patch — bez vysvětlení;
5. relative phase patch — bez vysvětlení;
6. oriented phase gradient — bez vysvětlení;
7. region motion — bez vysvětlení.

Současně je důležité oddělit tento výsledek od tvrzení, že „pohyb není důležitý“. Testována byla pouze tříprvková centroidová reprezentace a lineární ridge model. Nebyla testována deformace regionu, rotace, lokální tok přes hranici, změna vnitřní geometrie ani vyšší časové derivace.

Další experimentální krok proto dává větší smysl zaměřit na **lokální tok přes hranici / deformaci regionu**, nikoli pouze přidávat další globální nebo centroidové veličiny.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.

Reprodukční vstup: experiments/pw001_structural_eval.py (řádek LOCAL_MOTION).


## GENESIS-2.1 — Boundary Flux / hranice regionu

GENESIS-2.1 testuje informaci na hranici regionu namísto centroidového pohybu. Pro každou měřenou oblast se počítá:

- průměrný podepsaný phase-flux přes horizontální hranice;
- průměrný podepsaný phase-flux přes vertikální hranice;
- průměrná absolutní velikost fluxu;
- počet hraničních hran;
- počet hraničních hran normalizovaný velikostí regionu.

Phase flux používá lokální wrapped rozdíl a funkci sin(Δφ), tedy stejný lokální coupling term jako základní fázová interakce. Veličiny jsou observer-level a nejsou vraceny do GenesisUniverse.

### Clean PW-001 result

Run: PW-001 experiment #32  
Commit: 9aba487af4bdaf4f4d46388a95e098fcefaaddb6

| seed | samples | persistence MAE | boundary-flux MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.046877428501 | 0.059806772883 | -0.046756859049 |
| 390002 | 93990 | 0.000097287754 | 0.043990439793 | 0.056204637128 | -0.043893152039 |
| 390003 | 86979 | 0.000107119591 | 0.054710921230 | 0.063000259297 | -0.054603801639 |

Boundary-flux model nepřekonal persistence v žádném ze tří seedů. Na rozdíl od GENESIS-2.0 je ordered flux konzistentně lepší než shuffled kontrola, což ukazuje, že tato reprezentace obsahuje nějakou časově uspořádanou informaci. Současně je však její predikční chyba stále přibližně dvě až tři řády větší než persistence baseline.

### Interpretation

GENESIS-2.1 tedy poskytuje první z posledních lokálních sond, kde je shuffled kontrola konzistentně horší než ordered reprezentace, ale samotná reprezentace stále nevysvětluje hlavní signál GENESIS-1.6b.

To rozlišuje dvě otázky:

1. obsahuje reprezentace časovou informaci? — v tomto protokolu ano, ordered flux je lepší než shuffled;
2. vysvětluje tato reprezentace hlavní prediktivní výhodu coherence history? — ne, protože nepřekonává persistence.

Další smysluplný krok je proto přejít od okamžité boundary reprezentace k její změně mezi rámci: boundary-flux derivative, změna permeability hranice a lokální topologická změna hranových vazeb. Tím se otestuje, zda je relevantní nikoli samotný stav hranice, ale její pohyb / přestavba.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.

Reprodukční vstup: experiments/pw001_structural_eval.py (řádek BOUNDARY_FLUX).


## GENESIS-2.2 — Boundary Deformation

GENESIS-2.2 měří změnu hranice mezi po sobě jdoucími rámci. Reprezentace obsahuje změnu horizontálního a vertikálního phase fluxu, změnu jeho absolutní velikosti, změnu počtu hraničních hran, změnu hustoty hranice a velikost symetrického rozdílu buněk mezi starým a novým regionem.

Clean PW-001 experiment #36, commit 10eec0af631b7b0f49f40e22baf92b3e819f85f2, proběhl se stejným chronological holdout a exact-consecutive protokolem jako předchozí sondy.

Autoritativní artifact: 11262560049, digest sha256:62d2cb6c4be0005ae1bf254216d73498082b7c293281216d14c5913c25956e29.

| seed | samples | persistence MAE | deformation MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103885 | 0.000120540651 | 0.053672841565 | 0.053675879601 | -0.053552300914 |
| 390002 | 93951 | 0.000097256523 | 0.051169762144 | 0.051182149632 | -0.051072505621 |
| 390003 | 86937 | 0.000107100653 | 0.058421959737 | 0.058432728087 | -0.058314859084 |

Boundary deformation nepřekonala persistence v žádném ze tří seedů. Ordered a shuffled výsledky jsou prakticky shodné, takže tento konkrétní sedmiprvkový popis změny hranice neposkytuje důkaz o užitečné časové predikční informaci.

Výsledek tedy nepodporuje hypotézu, že hlavní signál GENESIS-1.6b je vysvětlitelný touto jednoduchou boundary-deformation reprezentací.

Další krok: pokud deformace nepřekoná persistence, je vhodné přestat přidávat další ručně navržené regionální reprezentace a přejít k systematickému rozlišení, zda je 1.6b signál artefaktem měřicího protokolu, nebo skutečně využitelnou krátkodobou predikční strukturou.


## GENESIS-2.2 — Boundary Deformation

GENESIS-2.2 měří změnu hranice mezi dvěma po sobě jdoucími rámci. Reprezentace obsahuje změnu horizontálního a vertikálního phase fluxu, změnu absolutního fluxu, změnu počtu hraničních hran, změnu hustoty hranice a velikost/sazbu symetrického rozdílu regionů.

### Clean PW-001 result

Run: PW-001 experiment #36  
Commit: 10eec0af631b7b0f49f40e22baf92b3e819f85f2

| seed | samples | persistence MAE | deformation MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103885 | 0.000120540651 | 0.053672841565 | 0.053675879601 | -0.053552300913 |
| 390002 | 93951 | 0.000097256523 | 0.051169762144 | 0.051182149632 | -0.051072505622 |
| 390003 | 86937 | 0.000107100653 | 0.058421959737 | 0.058432728086 | -0.058314859085 |

Boundary deformation nepřekonala persistence v žádném ze tří seedů. Ordered a shuffled reprezentace jsou prakticky stejné, takže tento konkrétní popis změny hranice neposkytl přesvědčivý důkaz využitelné časové prediktivní informace.

Robustnost základního coherence-history prediktoru zůstává zachována: ve všech 12 kombinacích seed × history length (2, 3, 5, 10) překonává lineární history model persistence, mean-history i shuffled control.

### Interpretation

2.2 tedy neposkytuje podporu hypotéze, že hlavní prediktivní signál GENESIS-1.6b vzniká z jednoduché lokální deformace pozorovaných regionálních hranic.

V kombinaci s 2.1 vzniká přesnější rozlišení: samotná boundary flux reprezentace obsahovala časově uspořádanou informaci, ale její změna mezi rámci tuto vlastnost v testovaném modelu nezachovává.

Další experiment by měl opustit další ručně agregované regionální atributy a testovat přímo **prostorově-temporální lokální stavovou reprezentaci**, přičemž je nutné zachovat stejné časové holdouty, shuffled control a observer-only invariantu.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.


## GENESIS-2.3 — Prostorově-temporální lokální stav

GENESIS-2.3 zachovává v jediném vstupu současný lokální fázový stav a jeho jednorámovou změnu v centroidově zarovnaném 3×3 patchi. Pro každou z 9 pozic se ukládá sin/cos aktuální fáze a sin/cos změny fáze, celkem 36 hodnot.

### Clean PW-001 result

Run: PW-001 experiment #40  
Commit: b705bad516f3a2fc99dabf20876df7c4fdad722a

| seed | samples | persistence MAE | spatiotemporal MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.063775315388 | 0.060691130676 | -0.063654745935 |
| 390002 | 93990 | 0.000097287754 | 0.053245859352 | 0.059630985231 | -0.053148571598 |
| 390003 | 86979 | 0.000107119591 | 0.068248304485 | 0.063469757759 | -0.068141184895 |

Spatiotemporální patch nepřekonal persistence v žádném ze tří seedů. V seed 390002 je ordered reprezentace lepší než shuffled kontrola, ale v 390001 a 390003 je shuffled kontrola dokonce lepší. Proto tento experiment neposkytuje robustní důkaz využitelné časové prediktivní informace v této konkrétní reprezentaci.

### Interpretation

GENESIS-2.3 tedy nepodporuje hypotézu, že hlavní coherence-history signál lze vysvětlit jednoduchým centroidově zarovnaným 3×3 prostorem a jeho jednorámovou změnou.

Důležitá metodická hranice zůstává: patch je stále centroidově zarovnaný, takže experiment netestuje plnou prostorovou geometrii bez ztráty orientace ani širší prostorový kontext. Negativní výsledek proto nevylučuje obecnou prostorově-temporální prediktivní strukturu.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.


## GENESIS-2.3 — Spatiotemporal Local Patch

GENESIS-2.3 zachovává lokální prostor i jeho jednorámcovou změnu současně. Pro 3×3 patch obsahuje každý bod sin(phi), cos(phi), sin(phi_t−phi_{t−1}) a cos(phi_t−phi_{t−1}), celkem 36 hodnot. Predictor nepoužívá coherence history jako vstup.

### Clean PW-001 result

Run: PW-001 experiment #40  
Commit: b705bad516f3a2fc99dabf20876df7c4fdad722a

| seed | samples | persistence MAE | patch MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.063775315388 | 0.060691130676 | -0.063654745935 |
| 390002 | 93990 | 0.000097287754 | 0.053245859352 | 0.059630985231 | -0.053148571598 |
| 390003 | 86979 | 0.000107119591 | 0.068248304485 | 0.063469757759 | -0.068141184895 |

Ani v jednom seedu spatiotemporální patch nepřekonal persistence. Ordered patch navíc není konzistentně lepší než shuffled kontrola: v seed 390001 a 390003 je shuffled predikce lepší. Tato konkrétní 36rozměrná reprezentace tedy neposkytuje důkaz, že hlavní coherence-history signál lze rekonstruovat z centroidově zarovnaného lokálního phase-state + one-step-change patch.

### Interpretation

2.3 je důležitý negativní výsledek: pouhé zachování lokálního prostoru a jeho okamžité změny nestačí. Tím se zmenšuje prostor hypotéz, ale stále se netestoval plný prostorově-temporální kontext, orientovaná topologie sousedství ani více než jeden krok historie.

Další experiment by měl proto testovat vícekrokovou lokální trajektorii bez použití coherence jako prediktoru: stejný lokální patch ve více minulých rámcích, s explicitním zachováním prostorové orientace. To umožní rozlišit, zda je informace skutečně v krátké trajektorii lokálního pole, nikoli v jediném stavu nebo jeho první diferenci.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.


## GENESIS-2.4 — Pevně orientované lokální prostorové pole

GENESIS-2.4 odstranil časovou derivaci z 2.3 a testoval samotný pevně orientovaný 3×3 phase field. Každá z devíti pozic je reprezentována jako sin/cos fáze, celkem 18 hodnot. Patch je stále centrován na měřeném regionu, ale jeho orientace není vůči regionu rotována ani jinak normalizována.

### Clean PW-001 result

Run: PW-001 experiment #44  
Commit: 1accc27f86a570a15ec4943aba93a7268cbf8fdd

| seed | samples | persistence MAE | spatial-field MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.054256577544 | 0.054121286055 | -0.054136008092 |
| 390002 | 93990 | 0.000097287754 | 0.051439207594 | 0.051378300251 | -0.051341919840 |
| 390003 | 86979 | 0.000107119591 | 0.058560070546 | 0.058586094145 | -0.058452950955 |

Pevně orientované lokální pole nepřekonalo persistence v žádném ze tří seedů. Ordered a shuffled výsledky jsou prakticky shodné; rozdíly navíc nemají konzistentní směr.

### Interpretation

GENESIS-2.4 nepodporuje hypotézu, že hlavní coherence-history signál je vysvětlitelný jednoduchým 3×3 pevně orientovaným lokálním fázovým polem.

Spolu s 2.3 to ale stále nevylučuje širší prostorový kontext. Oba testy používají malý 3×3 receptive field a centrum regionu. Další rozumná sonda je proto víceškálové pole, například současně radius 1 a radius 2, aby se testovalo, zda relevantní vztah přesahuje bezprostřední sousedství.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.


## GENESIS-2.4 — Pevně orientované lokální prostorové pole

GENESIS-2.4 odstranil centroidové přeuspořádání hodnot jako experimentální osu. Predictor používá pevně orientovaný 3×3 lokální phase field reprezentovaný 18 hodnotami sin/cos fáze. Reprezentace proto zachovává orientaci jednotlivých pozic v patchi.

### Clean PW-001 result

Run: PW-001 experiment #44  
Commit: 1accc27f86a570a15ec4943aba93a7268cbf8fdd

| seed | samples | persistence MAE | spatial-field MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.054256577544 | 0.054121286055 | -0.054136008092 |
| 390002 | 93990 | 0.000097287754 | 0.051439207594 | 0.051378300251 | -0.051341919840 |
| 390003 | 86979 | 0.000107119591 | 0.058560070546 | 0.058586094145 | -0.058452950956 |

Autoritativní experiment doběhl úspěšně. Hodnoty jsou zachovány v artifactu PW-001 #44; tato dokumentace zde neuvádí neověřené desetinné údaje.

Pevně orientované pole v testovaném lineárním modelu nepředstavuje vysvětlení hlavního coherence-history signálu GENESIS-1.6b. Persistence zůstává řádově přesnější baseline.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.


## GENESIS-2.5 — Víceškálové lokální prostorové pole

GENESIS-2.5 rozšířil 2.4 o dvě současná prostorová měřítka: pevně orientované pole 3×3 (radius 1) a 5×5 (radius 2). Každý bod je reprezentován sin/cos fáze, celkem 68 hodnot. Coherence history není prediktivní vstup.

### Clean PW-001 result

Run: PW-001 experiment #48  
Commit: d19e0a7f595ab59c86c0289b15a295bbf1fb046e

| seed | samples | persistence MAE | multiscale MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.054723868128 | 0.054580002685 | -0.054603298676 |
| 390002 | 93990 | 0.000097287754 | 0.052144416433 | 0.052125091097 | -0.052047128679 |
| 390003 | 86979 | 0.000107119591 | 0.058938777842 | 0.059084851468 | -0.058831658251 |

Víceškálové pole nepřekonalo persistence v žádném ze tří seedů. Ordered a shuffled MAE jsou prakticky shodné; jejich pořadí není konzistentní mezi seedy.

### Interpretation

GENESIS-2.5 nepodporuje hypotézu, že hlavní coherence-history signál lze vysvětlit jednoduchým současným 3×3 + 5×5 lokálním fázovým polem.

Tím se uzavírá další třída hypotéz založených na statickém lokálním prostorovém poli. Další krok by měl testovat **vícekrokovou lokální trajektorii**, nikoli pouze rozšiřovat prostorový receptive field: stejnou lokální reprezentaci zachovat pro několik po sobě jdoucích minulých rámců a zachovat orientaci i pořadí těchto rámců.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.


## GENESIS-2.5 — Víceškálové prostorové pole

GENESIS-2.5 rozšiřuje pevně orientované lokální pole z 3×3 na dvě současné prostorové škály: radius 1 a radius 2. Každá pozice je reprezentována sin/cos fáze. Celková reprezentace má 68 hodnot.

### Clean PW-001 result

Run: PW-001 experiment #52  
Commit: 2800b40e872c82922c547091db749450b9dfb14e

| seed | samples | persistence MAE | multiscale MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.054723868128 | 0.054580002685 | -0.054603298676 |
| 390002 | 93990 | 0.000097287754 | 0.052144416433 | 0.052125091097 | -0.052047128679 |
| 390003 | 86979 | 0.000107119591 | 0.058938777842 | 0.059084851468 | -0.058831658251 |

Víceškálové pole nepřekonalo persistence v žádném ze tří seedů. Ordered reprezentace je navíc prakticky shodná se shuffled kontrolou, takže tato reprezentace neposkytuje přesvědčivý důkaz využitelné časové informace.

Výsledek společně s 2.4 ukazuje, že jednoduché pevně orientované lokální phase fields — ani na jedné, ani na dvou prostorových škálách — nevysvětlují hlavní prediktivní výhodu coherence history.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.



## GENESIS-2.6 — Lokální trajektorie

GENESIS-2.6 testuje tři po sobě jdoucí 3×3 pevně orientované lokální phase fields jako jediný prediktivní vstup. Celkem jde o 54 hodnot; coherence history není vstupem. Páry jsou přijímány pouze při přesně po sobě jdoucích tickech.

### Clean PW-001 result

Run: PW-001 experiment #54  
Commit: 911966f05a4158f4759b907a25a24d91f0d8c52c

| seed | samples | persistence MAE | trajectory MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103839 | 0.000120511918 | 0.095598945712 | 0.095445144645 | -0.095478433794 |
| 390002 | 93912 | 0.000097225676 | 0.064810652413 | 0.064627208559 | -0.064713426737 |
| 390003 | 86895 | 0.000107081617 | 0.058564593123 | 0.058571464367 | -0.058457511506 |

Lokální trajektorie nepřekonala persistence v žádném ze tří seedů. Ordered trajectory navíc není lepší než shuffled kontrola; v seedech 390001 a 390002 je shuffled MAE dokonce mírně nižší. Neexistuje tedy v tomto protokolu důkaz, že hlavní coherence-history signál lze rekonstruovat z posledních tří lokálních prostorových stavů.

### Interpretation

GENESIS-2.6 uzavírá test jednoduché krátké lokální trajektorie. Rozšíření z jednoho rámce na tři po sobě jdoucí rámce nejen nepřineslo zlepšení, ale v testovaném lineárním modelu vedlo k výrazně vyšší chybě než persistence.

To stále není důkaz, že veškerá lokální trajektorie je nepoužitelná. Testoval se konkrétní 3×3 pevně orientovaný phase field, tři kroky historie a lineární ridge predictor. Nezahrnoval větší časové okno, nelineární model ani jiné prostorové kotvení.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.


## GENESIS-2.7 — Cross-region relational predictor

GENESIS-2.7 testuje, zda prediktivní informace neleží uvnitř jediného regionu, ale ve vztazích mezi současně pozorovanými regiony. Pro každý cílový region jsou zvoleny dva nejbližší peer-regiony podle deterministické periodické vzdálenosti.

Relational representation obsahuje pro každého peer-regionu relativní řádkovou a sloupcovou pozici, sinus a kosinus rozdílu střední fáze, logaritmický poměr velikostí, rozdíl boundary contrast a vzdálenost, doplněné maskou existence peeru. Celkem jde o 16 hodnot. **Koherence cílového ani peer-regionů není vstupem prediktoru.** Cíl je koherence cílového regionu v následujícím ticku.

### Clean PW-001 result

Run: PW-001 experiment #59  
Commit: 3b8ff9a13f9f35dad39505e5bbd92d1bd79efa39

| seed | samples | persistence MAE | relational MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.050121898680 | 0.063422266948 | -0.050001329227 |
| 390002 | 93990 | 0.000097287754 | 0.045819253626 | 0.058142361628 | -0.045721965872 |
| 390003 | 86979 | 0.000107119591 | 0.049063441833 | 0.063266603707 | -0.048956322242 |

### Interpretation

Cross-region relational representation nepřekonala persistence v žádném ze tří seedů. Relational MAE je přibližně o dva řády vyšší než persistence MAE.

Současně je relational predictor ve všech třech seedech lepší než shuffled control. To znamená, že testovaná relational representation obsahuje měřitelnou časovou informaci, ale v tomto konkrétním lineárním modelu není tato informace dostatečná k predikci následující coherence na úrovni persistence baseline.

Výsledek proto podporuje pouze slabší tvrzení: **současné vztahy mezi regiony nejsou čistě časově náhodnou reprezentací.** Nepodporuje tvrzení, že cross-region relations vysvětlují hlavní coherence-history prediktivní signál.

Další experiment by měl rozlišit, zda je informace rozložena v samotné síti vztahů, a ne pouze v nejbližších dvou peerech. Vhodnou další sondou je proto graph-level relational predictor s deterministickou agregací většího počtu peer-regionů, stále bez coherence jako vstupu a se zachováním shuffled kontroly.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.


## GENESIS-2.8 — Graph-level relational predictor

GENESIS-2.8 rozšiřuje cross-region probe z maximálně dvou nejbližších peer regionů na širší lokální graf až osmi peerů. Pro každý cílový region se vztahy agregují pomocí mean/std/min/max přes relativní polohu, fázový vztah, poměr velikostí, rozdíl boundary contrast a vzdálenost; přidává se normalizovaný počet dostupných peerů. Výsledná reprezentace má 33 hodnot. Cílová koherence není vstupem prediktoru.

PW-001 run #64 (a0842fa12c57b72cd052a79efe47784e7a117556) dokončil celý benchmark úspěšně. Artifact digest: sha256:e8923d2667f55a2117516959954a37ba1c83ba38b869403a014f667753dd4b69.

| seed | samples | persistence MAE | graph MAE | shuffled graph MAE | improvement |
|---|---:|---:|---:|---:|---:|
| 390001 | 103931 | 0.000120569452 | 0.050765597517 | 0.066235851797 | -0.050645028064 |
| 390002 | 93990 | 0.000097287754 | 0.047290570970 | 0.061824190387 | -0.047193283216 |
| 390003 | 86979 | 0.000107119591 | 0.054775654688 | 0.067305877639 | -0.054668535097 |

Interpretace:
- Graph-level relational prediction nepřekonala persistence v žádném ze tří seed.
- Ordered graph representation byla ve všech třech seed lepší než shuffled control.
- Rozšíření z 2 peerů na 8 peerů tedy pod současnou lineární reprezentací nepřineslo přístup k hlavnímu predikčnímu signálu.
- Výsledek nepodporuje tvrzení, že hlavní krátkodobá predikční informace je obsažena pouze v současné širší síti regionálních vztahů.
- Výsledek také není důkazem, že vztahy mezi regiony nenesou informaci: rozdíl vůči shuffled control ukazuje, že testovaná reprezentace obsahuje určitou časovou strukturu.
- Stejně jako předchozí fáze neposkytuje důkaz inteligence, agency, self-modelu ani endogenous learning.

Další probe by měl oddělit samotnou autoregresní informaci v již pozorované koherenci od informace přítomné v ostatních měřených strukturách. To zabrání tomu, aby opakované vítězství history predictor bylo mylně interpretováno jako důkaz emergentní predikce vyšší úrovně.


## GENESIS-2.9 — Coherence innovation predictor

GENESIS-2.9 tests whether the predictive structure observed in GENESIS-1.6b remains after removing simple level persistence. Instead of predicting the next coherence value directly, the predictor models the next **coherence change** (innovation).

For each observer identity, the input consists only of the preceding coherence differences over a bounded history window. The target is the next coherence difference. The evaluation keeps the same chronological 50% holdout and exact-consecutive-tick requirement. A zero-change baseline predicts that the next coherence change is zero. A deterministic shuffled-history control tests whether the ordering of the previous changes matters.

The experiment remains observer-only: no innovation prediction is fed back into GenesisUniverse or TemporalMemory, and no goals, rewards, agency, meaning, language, self-model, or endogenous learning are introduced.

### Clean PW-001 result

Run: PW-001 experiment #67  
Commit: `4aac7d14c40d9e07dbd068d5691f8013dab9abc1`  
Artifact: `11266983326`  
Artifact digest: `sha256:a62fa761bca8359c45d3c735befc47df682aa45ccb13a0a512b1b7e68178bc5d`

| seed | history | samples | zero-change MAE | innovation MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|---:|
| 390001 | 2 | 103885 | 0.000120540651 | 0.000118292732 | 0.000120885863 | +0.000002247919 |
| 390001 | 3 | 103839 | 0.000120511918 | 0.000116298076 | 0.000121377950 | +0.000004213842 |
| 390001 | 5 | 103747 | 0.000120453902 | 0.000112607665 | 0.000122572581 | +0.000007846237 |
| 390001 | 10 | 103517 | 0.000120311442 | 0.000104829708 | 0.000125547330 | +0.000015481738 |
| 390002 | 2 | 93951 | 0.000097256523 | 0.000096160431 | 0.000097724232 | +0.000001096092 |
| 390002 | 3 | 93912 | 0.000097225676 | 0.000094846048 | 0.000097949794 | +0.000002379627 |
| 390002 | 5 | 93834 | 0.000097163027 | 0.000092365998 | 0.000098474289 | +0.000004797029 |
| 390002 | 10 | 93639 | 0.000097007272 | 0.000086918632 | 0.000099987211 | +0.000010088635 |
| 390003 | 2 | 86937 | 0.000107100653 | 0.000105678016 | 0.000107497144 | +0.000001422638 |
| 390003 | 3 | 86895 | 0.000107081617 | 0.000093989937 | 0.000111255433 | +0.000013091680 |
| 390003 | 5 | 86811 | 0.000107043112 | 0.000093550904 | 0.000111585302 | +0.000013492208 |
| 390003 | 10 | 86601 | 0.000106948247 | 0.000089860664 | 0.000113041251 | +0.000017087584 |

### Interpretation

The innovation predictor beats the zero-change baseline in **all 12 tested seed × history-length combinations**. Its MAE is also lower than the shuffled-history control in all 12 combinations. The improvement grows with history length for every seed, with the largest observed improvement at history length 10.

This result is methodologically stronger than the earlier level-prediction comparison because it asks a narrower question: whether recent coherence changes contain information about the next coherence change beyond simply assuming no change. Under the tested linear model and protocol, the answer is yes.

The result does **not** establish intelligence, agency, self-modeling, endogenous learning, or an autonomous predictive process. The predictor is an external statistical model trained and evaluated on observer measurements. It also does not establish causality or identify which physical variables generate the innovation signal. The result shows only that the measured coherence trajectory contains reproducible short-history information about its subsequent change under the stated protocol.

GENESIS-2.9 therefore changes the interpretation of GENESIS-1.6b in an important but bounded way: the observed coherence-history signal cannot be reduced entirely to a trivial last-value persistence baseline, because a model of recent coherence changes still improves prediction of the next change. The next experimental question is to identify the physical/observer representation that carries this innovation signal without supplying coherence history directly.

The universe rules remain unchanged and all prediction remains external to GenesisUniverse.



## GENESIS-2.10 — State-to-innovation source probe

GENESIS-2.10 asks whether the coherence-innovation signal identified in GENESIS-2.9 can be reconstructed from the **current non-coherence observer state**, rather than from previous coherence changes.

The predictor targets the next coherence change:

`delta coherence = coherence(t+1) - coherence(t)`

but receives only the current observer representation. Coherence itself is excluded from every predictor input. The tested representations are:

- structure — size, boundary contrast, lifetime, persistence, overlap
- local_patch
- phase_patch
- gradient_patch
- motion
- boundary_flux
- spatial_field
- multiscale_field
- relational
- graph_relational

The same 50% chronological holdout and exact-consecutive-tick protocol is retained. The zero-change baseline predicts delta coherence = 0. A deterministic shuffled-state control tests whether the ordered state representation provides an advantage.

### Clean PW-001 result

Run: PW-001 experiment #70  
Commit: `b0def8157a077f753304e2905725a2d4cb5ad310`  
Artifact: `11268229198`  
Artifact digest: `sha256:dbdc86bba337313a749e069aa137a0239c24fe963163e709e2634acb9c3468a2`

| feature | seed | samples | zero-change MAE | state MAE | shuffled MAE | improvement |
|---|---:|---:|---:|---:|---:|---:|
| structure | 390001 | 103931 | 0.000120569452 | 0.000133870449 | 0.000158464540 | -0.000013300997 |
| structure | 390002 | 93990 | 0.000097287754 | 0.000107885995 | 0.000126289027 | -0.000010598241 |
| structure | 390003 | 86979 | 0.000107119591 | 0.000094175336 | 0.000115903304 | +0.000012944254 |
| local_patch | 390001 | 103931 | 0.000120569452 | 0.000131120779 | 0.000127531024 | -0.000010551327 |
| local_patch | 390002 | 93990 | 0.000097287754 | 0.000113949445 | 0.000108671741 | -0.000016661691 |
| local_patch | 390003 | 86979 | 0.000107119591 | 0.000110112590 | 0.000110844244 | -0.000002993000 |
| phase_patch | 390001 | 103931 | 0.000120569452 | 0.000133219234 | 0.000133055737 | -0.000012649782 |
| phase_patch | 390002 | 93990 | 0.000097287754 | 0.000106904764 | 0.000106508163 | -0.000009617010 |
| phase_patch | 390003 | 86979 | 0.000107119591 | 0.000110368552 | 0.000118869844 | -0.000003248961 |
| gradient_patch | 390001 | 103931 | 0.000120569452 | 0.000126709089 | 0.000130852157 | -0.000006139637 |
| gradient_patch | 390002 | 93990 | 0.000097287754 | 0.000106506987 | 0.000107075089 | -0.000009219233 |
| gradient_patch | 390003 | 86979 | 0.000107119591 | 0.000110049700 | 0.000116059997 | -0.000002930109 |
| motion | 390001 | 103885 | 0.000120540651 | 0.000120380734 | 0.000120396892 | +0.000000159917 |
| motion | 390002 | 93951 | 0.000097256523 | 0.000097503738 | 0.000097513571 | -0.000000247215 |
| motion | 390003 | 86937 | 0.000107100653 | 0.000107221899 | 0.000107229244 | -0.000000121245 |
| boundary_flux | 390001 | 103931 | 0.000120569452 | 0.000124811892 | 0.000124168638 | -0.000004242439 |
| boundary_flux | 390002 | 93990 | 0.000097287754 | 0.000101815807 | 0.000101068519 | -0.000004528053 |
| boundary_flux | 390003 | 86979 | 0.000107119591 | 0.000110200389 | 0.000110400545 | -0.000003080798 |
| spatial_field | 390001 | 103931 | 0.000120569452 | 0.000120965669 | 0.000121485704 | -0.000000396217 |
| spatial_field | 390002 | 93990 | 0.000097287754 | 0.000099045225 | 0.000099135259 | -0.000001757467 |
| spatial_field | 390003 | 86979 | 0.000107119591 | 0.000107457495 | 0.000107705605 | -0.000000337904 |
| multiscale_field | 390001 | 103931 | 0.000120569452 | 0.000124621574 | 0.000126082643 | -0.000004052121 |
| multiscale_field | 390002 | 93990 | 0.000097287754 | 0.000106331677 | 0.000105838218 | -0.000009043923 |
| multiscale_field | 390003 | 86979 | 0.000107119591 | 0.000110435541 | 0.000111674519 | -0.000003315950 |
| relational | 390001 | 103931 | 0.000120569452 | 0.000128506707 | 0.000130423949 | -0.000007937255 |
| relational | 390002 | 93990 | 0.000097287754 | 0.000099367675 | 0.000103745442 | -0.000002079921 |
| relational | 390003 | 86979 | 0.000107119591 | 0.000106338344 | 0.000109613740 | +0.000000781247 |
| graph_relational | 390001 | 103931 | 0.000120569452 | 0.000135062276 | 0.000133060893 | -0.000014492824 |
| graph_relational | 390002 | 93990 | 0.000097287754 | 0.000114740956 | 0.000112638409 | -0.000017453202 |
| graph_relational | 390003 | 86979 | 0.000107119591 | 0.000118902909 | 0.000121446026 | -0.000011783314 |

### Interpretation

The state-to-innovation probe does **not** provide a robust reconstruction of the GENESIS-2.9 innovation signal.

Most tested representations fail to beat the zero-change baseline in all or nearly all seeds. Three isolated positive cases occur:

- structure in seed 390003: +0.000012944254
- motion in seed 390001: +0.000000159917
- relational in seed 390003: +0.000000781247

None is reproduced consistently across all three seeds. The strongest positive structure result is therefore not sufficient to establish a general state-to-innovation relationship.

The result is important because it separates two observations:

1. **GENESIS-2.9:** recent coherence changes themselves contain reproducible predictive information about the next coherence change.
2. **GENESIS-2.10:** the tested single-frame non-coherence observer representations do not robustly recover that information.

This means the current evidence does not identify the physical/observer variable carrying the innovation signal. The signal may require a different representation, a multi-frame state, a nonlinear model, or a combination of variables not captured by the present probes. GENESIS-2.10 therefore narrows the hypothesis space rather than closing it.

No predictor output is fed back into GenesisUniverse or TemporalMemory. The result provides no evidence of intelligence, agency, self-modeling, or endogenous learning.

The next logical probe is a **state-trajectory innovation predictor**: preserve a short sequence of non-coherence states across consecutive ticks and predict the next coherence change, while continuing to exclude coherence history itself. This directly tests whether the missing information resides in the trajectory of the underlying state rather than in any single frame.

## GENESIS-2.10 — State-to-innovation source probe

GENESIS-2.10 testuje další otázku po 2.9: pokud je predikovatelná změna koherence, lze tuto změnu predikovat přímo z aktuálního observer-state bez použití coherence history?

Cíl je následující změna koherence: delta C(t+1) = C(t+1) − C(t).

Prediktor dostává pouze reprezentaci aktuálního měřeného regionu. Coherence aktuálního ani předchozího rámce není součástí vstupu. Používá se stejný 50% chronological holdout, exact-consecutive-tick požadavek a deterministický shuffled control jako v předchozích sondách. Zero baseline předpokládá delta C = 0.

Testovány byly: structure, local_patch, phase_patch, gradient_patch, motion, boundary_flux, spatial_field, multiscale_field, relational a graph_relational.

### Clean PW-001 result

Run: PW-001 experiment #70  
Commit: `b0def8157a077f753304e2905725a2d4cb5ad310`  
Artifact: `11268229198`  
Artifact digest: `sha256:dbdc86bba337313a749e069aa137a0239c24fe963163e709e2634acb9c3468a2`

| feature | seed | samples | zero MAE | state MAE | shuffled MAE | improvement |
|---|---:|---:|---:|---:|---:|---:|
| structure | 390001 | 103931 | 0.000120569452 | 0.000133870449 | 0.000158464540 | -0.0000133010 |
| structure | 390002 | 93990 | 0.000097287754 | 0.000107885995 | 0.000126289027 | -0.0000105982 |
| structure | 390003 | 86979 | 0.000107119591 | 0.000094175331 | 0.000115903304 | +0.0000129443 |
| local_patch | 390001 | 103931 | 0.000120569452 | 0.000131120779 | 0.000127531024 | -0.0000105513 |
| local_patch | 390002 | 93990 | 0.000097287754 | 0.000113949445 | 0.000108671741 | -0.0000166617 |
| local_patch | 390003 | 86979 | 0.000107119591 | 0.000110112590 | 0.000110844244 | -0.0000029930 |
| phase_patch | 390001 | 103931 | 0.000120569452 | 0.000133219234 | 0.000133055737 | -0.0000126498 |
| phase_patch | 390002 | 93990 | 0.000097287754 | 0.000106904764 | 0.000106508163 | -0.0000096170 |
| phase_patch | 390003 | 86979 | 0.000107119591 | 0.000110368552 | 0.000118869844 | -0.0000032490 |
| gradient_patch | 390001 | 103931 | 0.000120569452 | 0.000126709089 | 0.000130852157 | -0.0000061396 |
| gradient_patch | 390002 | 93990 | 0.000097287754 | 0.000106506987 | 0.000107075089 | -0.0000092192 |
| gradient_patch | 390003 | 86979 | 0.000107119591 | 0.000110049700 | 0.000116059997 | -0.0000029301 |
| motion | 390001 | 103885 | 0.000120540651 | 0.000120380734 | 0.000120396892 | +0.0000001599 |
| motion | 390002 | 93951 | 0.000097256523 | 0.000097503738 | 0.000097513571 | -0.0000002472 |
| motion | 390003 | 86937 | 0.000107100653 | 0.000107221899 | 0.000107229244 | -0.0000001212 |
| boundary_flux | 390001 | 103931 | 0.000120569452 | 0.000124811892 | 0.000124168638 | -0.0000042424 |
| boundary_flux | 390002 | 93990 | 0.000097287754 | 0.000101815807 | 0.000101068519 | -0.0000045281 |
| boundary_flux | 390003 | 86979 | 0.000107119591 | 0.000110200389 | 0.000110400545 | -0.0000030808 |
| spatial_field | 390001 | 103931 | 0.000120569452 | 0.000120965669 | 0.000121485704 | -0.0000003962 |
| spatial_field | 390002 | 93990 | 0.000097287754 | 0.000099045221 | 0.000099135259 | -0.0000017575 |
| spatial_field | 390003 | 86979 | 0.000107119591 | 0.000107457495 | 0.000107705605 | -0.0000003379 |
| multiscale_field | 390001 | 103931 | 0.000120569452 | 0.000124621574 | 0.000126082643 | -0.0000040521 |
| multiscale_field | 390002 | 93990 | 0.000097287754 | 0.000106331677 | 0.000105838218 | -0.0000090439 |
| multiscale_field | 390003 | 86979 | 0.000107119591 | 0.000110435541 | 0.000111674520 | -0.0000033160 |
| relational | 390001 | 103931 | 0.000120569452 | 0.000128506707 | 0.000130423948 | -0.0000079373 |
| relational | 390002 | 93990 | 0.000097287754 | 0.000099367675 | 0.000103745442 | -0.0000020799 |
| relational | 390003 | 86979 | 0.000107119591 | 0.000106338344 | 0.000109613740 | +0.0000007812 |
| graph_relational | 390001 | 103931 | 0.000120569452 | 0.000135062276 | 0.000133060893 | -0.0000144928 |
| graph_relational | 390002 | 93990 | 0.000097287754 | 0.000114740956 | 0.000112638409 | -0.0000174532 |
| graph_relational | 390003 | 86979 | 0.000107119591 | 0.000118902909 | 0.000121446027 | -0.0000117833 |

### Interpretation

Žádná z testovaných reprezentací neposkytla robustní tříseedovou výhodu nad zero-change baseline pro predikci delta C.

Dvě drobné výjimky stojí za zaznamenání: structure překonala zero baseline pouze v seedu 390003 a relational ji překonala pouze v seedu 390003.

U motion je MAE téměř identické s nulovým baseline ve všech třech seedech, ale výhoda se nereprodukuje: 390001 je nepatrně lepší, zatímco 390002 a 390003 jsou nepatrně horší. Motion proto nelze označit za robustní nosič inovačního signálu.

Výsledek 2.10 tedy neposkytuje jednoduchou fyzickou/observer-level reprezentaci, která by sama vysvětlila inovační predikční signál z GENESIS-2.9. Signál z 2.9 není v této podobě snadno rekonstruovatelný z žádné z deseti testovaných aktuálních reprezentací.

Důležitá metodická hranice: všechny sondy používají lineární ridge model a konkrétní observer reprezentace. Negativní výsledek proto nevylučuje nelineární kombinace, víceškálové časové kontexty, jiné kotvení regionu ani latentní kombinace více měřených polí.

### Stav hypotézy po 2.10

GENESIS-2.9 ukázal reprodukovatelnou predikovatelnost změny koherence z její vlastní krátké historie. GENESIS-2.10 současně neukázal, že by tento inovační signál byl jednoduše dostupný z jednoho aktuálního observer-state reprezentovaného testovanými poli.

Další experimentální krok proto bude systematická multi-state innovation reconstruction: kombinovat několik aktuálních stavových reprezentací současně, ale stále bez coherence jako vstupu, a ověřit, zda kombinace nese inovační informaci, kterou jednotlivé reprezentace samostatně neodhalily.

Výsledek neposkytuje důkaz inteligence, agentivity, self-modelu ani endogenního učení.
