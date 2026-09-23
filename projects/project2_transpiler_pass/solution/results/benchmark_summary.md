# Project 2 -- benchmark (milestone 4)

360 circuits: widths (3, 5, 8), depths (10, 30, 100), 20 seeds, both populations.
Unitary-equivalence spot check: 60 circuits (width <= 5), **0 mismatches**.

| population | n | CX removed (pooled) | CX removed (mean per circuit) | depth removed | fusions | annihilations | mean pass time |
|---|---:|---:|---:|---:|---:|---:|---:|
| planted | 180 | 25.3% | 25.9% | 11.5% | 5182 | 4 | 7.14 ms |
| unplanted | 180 | 0.0% | 0.0% | 0.0% | 3 | 0 | 2.22 ms |

Pass runtime vs gate count (DAG-level, best of two runs):

| population | slope | intercept | R^2 |
|---|---:|---:|---:|
| planted | 8.89 us/gate | -2043 us | 0.808 |
| unplanted | 2.78 us/gate | -185 us | 0.888 |

## By width and depth (planted)

| width | depth | CX before | CX after | reduction |
|---:|---:|---:|---:|---:|
| 3 | 10 | 498 | 370 | 25.7% |
| 3 | 30 | 1437 | 1073 | 25.3% |
| 3 | 100 | 4576 | 3402 | 25.7% |
| 5 | 10 | 978 | 728 | 25.6% |
| 5 | 30 | 2775 | 2073 | 25.3% |
| 5 | 100 | 9043 | 6757 | 25.3% |
| 8 | 10 | 1558 | 1162 | 25.4% |
| 8 | 30 | 4676 | 3492 | 25.3% |
| 8 | 100 | 15417 | 11529 | 25.2% |
