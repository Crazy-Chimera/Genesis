# GENESIS-2.49 Result

| noise | exact coupling selection |
|---:|---:|
| 0.001 | 4/6 |
| 0 | 6/6 |

At noise = 0, all six tested actual coupling values are recovered exactly and the minimum MAE is 0.

At production noise = 0.001, four of six recover the exact coupling and two select the adjacent +0.000125 grid point.

## Conclusion

The coupling-estimation offset observed in GENESIS-2.48 is attributable to the stochastic noise term under the tested protocol. GENESIS-2.50 tests the noise-amplitude dependence of this effect.
