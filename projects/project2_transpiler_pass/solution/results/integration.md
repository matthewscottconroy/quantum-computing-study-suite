# Project 2 -- pass-manager integration (milestone 3)

Test circuit: Bell state + three adjacent `CX.RZ.CX` windows (`integration.bell_phase_circuit`).
`with` = the same preset pass manager plus `PassManager([CXRZCXFuser(), DropIdentityRZ()])` appended to the named stage.

| backend | opt level | stage | angles | 2q without -> with | rz without -> with | depth without -> with | ISA valid | coupling ok |
|---|---:|---|---|---:|---:|---:|:--:|:--:|
| fake_manila | 0 | init | numeric | 7 -> 3 | 5 -> 3 | 13 -> 7 | yes | yes |
| fake_manila | 0 | init | symbolic | 7 -> 3 | 5 -> 3 | 13 -> 7 | yes | yes |
| fake_manila | 0 | optimization | numeric | 7 -> 3 | 5 -> 3 | 13 -> 7 | yes | yes |
| fake_manila | 0 | optimization | symbolic | 7 -> 3 | 5 -> 3 | 13 -> 7 | yes | yes |
| fake_manila | 1 | init | numeric | 1 -> 1 | 3 -> 3 | 4 -> 4 | yes | yes |
| fake_manila | 1 | init | symbolic | 1 -> 1 | 5 -> 5 | 4 -> 4 | yes | yes |
| fake_manila | 1 | optimization | numeric | 1 -> 1 | 3 -> 3 | 4 -> 4 | yes | yes |
| fake_manila | 1 | optimization | symbolic | 1 -> 1 | 5 -> 5 | 4 -> 4 | yes | yes |
| fake_manila | 2 | init | numeric | 1 -> 1 | 3 -> 3 | 4 -> 4 | yes | yes |
| fake_manila | 2 | init | symbolic | 1 -> 1 | 5 -> 5 | 4 -> 4 | yes | yes |
| fake_manila | 2 | optimization | numeric | 1 -> 1 | 3 -> 3 | 4 -> 4 | yes | yes |
| fake_manila | 2 | optimization | symbolic | 1 -> 1 | 5 -> 5 | 4 -> 4 | yes | yes |
| fake_manila | 3 | init | numeric | 1 -> 1 | 3 -> 3 | 4 -> 4 | yes | yes |
| fake_manila | 3 | init | symbolic | 1 -> 1 | 5 -> 5 | 4 -> 4 | yes | yes |
| fake_manila | 3 | optimization | numeric | 1 -> 1 | 3 -> 3 | 4 -> 4 | yes | yes |
| fake_manila | 3 | optimization | symbolic | 1 -> 1 | 5 -> 5 | 4 -> 4 | yes | yes |
| fake_torino | 0 | init | numeric | 7 -> 3 | 33 -> 15 | 52 -> 22 | yes | yes |
| fake_torino | 0 | init | symbolic | 7 -> 3 | 33 -> 15 | 52 -> 22 | yes | yes |
| fake_torino | 0 | optimization | numeric | 7 -> 7 | 33 -> 33 | 52 -> 52 | yes | yes |
| fake_torino | 0 | optimization | symbolic | 7 -> 7 | 33 -> 33 | 52 -> 52 | yes | yes |
| fake_torino | 1 | init | numeric | 1 -> 1 | 6 -> 6 | 7 -> 7 | yes | yes |
| fake_torino | 1 | init | symbolic | 1 -> 1 | 9 -> 9 | 10 -> 10 | yes | yes |
| fake_torino | 1 | optimization | numeric | 1 -> 1 | 6 -> 6 | 7 -> 7 | yes | yes |
| fake_torino | 1 | optimization | symbolic | 1 -> 1 | 9 -> 9 | 10 -> 10 | yes | yes |
| fake_torino | 2 | init | numeric | 1 -> 1 | 5 -> 5 | 6 -> 6 | yes | yes |
| fake_torino | 2 | init | symbolic | 1 -> 1 | 8 -> 8 | 9 -> 9 | yes | yes |
| fake_torino | 2 | optimization | numeric | 1 -> 1 | 5 -> 5 | 6 -> 6 | yes | yes |
| fake_torino | 2 | optimization | symbolic | 1 -> 1 | 8 -> 8 | 9 -> 9 | yes | yes |
| fake_torino | 3 | init | numeric | 1 -> 1 | 5 -> 5 | 6 -> 6 | yes | yes |
| fake_torino | 3 | init | symbolic | 1 -> 1 | 8 -> 8 | 9 -> 9 | yes | yes |
| fake_torino | 3 | optimization | numeric | 1 -> 1 | 5 -> 5 | 6 -> 6 | yes | yes |
| fake_torino | 3 | optimization | symbolic | 1 -> 1 | 8 -> 8 | 9 -> 9 | yes | yes |

6 of 32 configurations show a strict 2-qubit-gate reduction; all of them are at `optimization_level=0`.
