# GENESIS-2.13 — State-Difference Trajectory Screening

Run: GENESIS 2.13 experiment #5
Commit: 0dc7ad357bba96951a163e73579936912472e5d7
Protocol: 2,000 ticks; 50% chronological holdout; exact consecutive ticks; zero-change baseline; shuffled control.

| seed | history | samples | zero MAE | difference MAE | shuffled MAE | improvement |
|---:|---:|---:|---:|---:|---:|---:|
| 390001 | 2 | 16955 | 0.000119222109 | 0.000346325698 | 0.000418585016 | -0.000227103589 |
| 390001 | 3 | 16947 | 0.000119181114 | 0.002050236926 | 0.002118018919 | -0.001931055812 |
| 390001 | 5 | 16931 | 0.000119099104 | 0.010224696914 | 0.010286005153 | -0.010105597809 |
| 390001 | 10 | 16891 | 0.000118896023 | 0.019832200936 | 0.019884308548 | -0.019713304913 |
| 390002 | 2 | 15577 | 0.000086979801 | 0.000200211533 | 0.000255217690 | -0.000113231732 |
| 390002 | 3 | 15574 | 0.000086975891 | 0.001936593787 | 0.001988749486 | -0.001849617896 |
| 390002 | 5 | 15568 | 0.000086967991 | 0.005583307070 | 0.005632442186 | -0.005496339080 |
| 390002 | 10 | 15553 | 0.000086950032 | 0.015381241221 | 0.015417708682 | -0.015294291190 |
| 390003 | 2 | 15528 | 0.000098640887 | 0.000548826749 | 0.000603547307 | -0.000450185862 |
| 390003 | 3 | 15522 | 0.000098625763 | 0.003371000442 | 0.003423944243 | -0.003272374680 |
| 390003 | 5 | 15510 | 0.000098594755 | 0.008865872015 | 0.008915921036 | -0.008767277259 |
| 390003 | 10 | 15482 | 0.000098511961 | 0.031351164750 | 0.031391833440 | -0.031252652789 |

## Interpretation

State-difference trajectories did not beat the zero-change baseline in any of the 12 seed × history combinations.

They beat the shuffled control in all 12 combinations. Thus the ordered difference trajectory contains measurable structure for the tested model, but that structure is not sufficient for accurate next-step coherence-innovation prediction.

Longer histories degraded performance strongly in every seed.

This is a 2,000-tick screening result. It does not establish that all nonlinear state models fail. A separate nonlinear random-feature predictor exists in the repository but has not been treated here as a completed full-length benchmark.

The experiment remains measurement-only: no prediction is fed back into GenesisUniverse and no goals, rewards, agency, self-model, or endogenous learning are introduced.

Next clean question: test the model-class hypothesis using the same combined representation before adding further observer variables.
