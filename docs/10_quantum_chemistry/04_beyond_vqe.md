# Beyond VQE: Phase Estimation, Qubitization and Real Resource Estimates

> **Prerequisites**: Quantum phase estimation (04/04), active spaces and ansätze (10/03),
> Trotter and qubitization costs (08/03), block encodings and QSVT (08/05)
> **Connects to**: Surface code and fault tolerance (05/06, 05/07), quantum complexity (08/01)

---

## Overview

VQE trades circuit depth for measurement repetitions, and Chapter 10/03 showed what that trade
costs: `S ≈ (λ/ε)²` shots per energy evaluation, an unforgiving `1/ε²`. The fault-tolerant
alternative inverts the trade. **Quantum phase estimation** (QPE) reads an eigenvalue off the phase
of a controlled time evolution and reaches precision `ε` with `O(1/ε)` circuit applications —
Heisenberg scaling, quadratically better in `ε` — but needs a coherent circuit far deeper than any
NISQ device can run.

This chapter is about that algorithm applied to chemistry, and about the resource estimates it
supports. Those estimates are the most useful output the field has produced: they are concrete,
falsifiable, and have improved by four to five orders of magnitude in under a decade, largely
through better Hamiltonian representations rather than better quantum algorithms. The chapter ends
where Chapter 08/03 left FeMoco, with numbers assembled from the parts developed here.

---

## Quantum Phase Estimation for Chemistry

### The algorithm, specialized

Chapter 04/04 develops QPE in general. For chemistry the instance is: given a unitary
`U = e^{iHt}` and an input state `|φ⟩`, estimate the eigenphase. Three specializations matter.

**Shift and scale.** QPE reads a phase in `[0, 1)`, so the spectrum must be mapped into one
period. With `U = exp(i(H + Δ)t)` the measured bin `k` of `m` ancillas gives

```
E = 2π k / (2^m t)  -  Δ,   resolution  ΔE = 2π / (2^m t)
```

Choosing `t` too small wastes resolution; too large and eigenvalues wrap around and alias. A
spectral range bound `W ≥ E_max - E_min` fixes `t = 2π/W`, whence

```
m ≥ log₂(W / ΔE)      and, for ΔE = 2ε with ε = 1.6 mHa, m ≥ log₂(W/2ε)
```

so a molecule with a `W = 100` Ha spectral window needs `m ≥ 15` readout bits. The bit count is
cheap; the `2^m` controlled evolutions it implies are not.

**Overlap, not energy, sets the success probability.** QPE projects: run on `|φ⟩ = Σ_k c_k|E_k⟩` it
returns `E_k` with probability `|c_k|²`. The Hartree-Fock determinant is the standard input, and
the number of repetitions needed scales as `1/|⟨Φ_HF|ψ₀⟩|²`. That overlap is `0.988` for H₂ at
equilibrium, but it decays **exponentially in system size** for strongly correlated systems —
precisely the systems worth simulating. Better references (CISD, a truncated MPS, or a
VQE-optimized state) push the crossover out; none removes the scaling. This is the honest answer
to "QPE just works": it works if you can already prepare a state with non-negligible overlap, and
that is a real algorithmic problem, not an implementation detail.

**The cost is the evolution.** The ancilla register and the inverse QFT are negligible. Essentially
all of QPE's cost is the `2^m - 1` controlled applications of the Hamiltonian's evolution — which
is why the rest of this chapter is about how cheaply `e^{iHt}` can be implemented.

---

## Trotter versus Qubitization

Chapter 08/03 introduced the comparison; here it is specialized to molecules.

**Trotterization** splits `e^{-iHt} ≈ (∏_j e^{-i c_j P_j t/r})^r`. The gate count for a `p`-th
order product formula scales as `O(Λ t (Λt/ε)^{1/p})` with `Λ` a commutator-dependent norm. Trotter
is simple, needs no ancillas, and its empirical error on real molecules is far better than its
worst-case bound — but the `ε` dependence is polynomial, which is fatal at chemical accuracy.

**Qubitization** (Low-Chuang; Chapter 08/05) block-encodes `H/λ` from its linear combination of
unitaries and builds a walk operator whose eigenphases are `±arccos(E/λ)`. Phase estimation on the
walk operator needs

```
queries ≈ π λ / (2 ε)      to resolve energies to ε
```

with each query one `PREPARE`/`SELECT` pair. The `ε` dependence is optimal and the only free
parameter is

```
λ = Σ_j |c_j| = ||H||₁
```

the same `1`-norm that sets VQE's shot count in Chapter 10/03. This is the central fact of
fault-tolerant quantum chemistry: **`λ` is the cost.** Everything below is about making it smaller.

---

## Making `λ` Small: Hamiltonian Factorizations

Written naively in an arbitrary molecular-orbital basis, the `O(M⁴)` two-electron terms give a `λ`
that grows roughly as `O(M³)` and reaches thousands of hartree for realistic active spaces. Four
representations, in order of sophistication:

| representation | ancillas / qubits | `λ` scaling | notes |
|---|---|---|---|
| sparse (raw Pauli LCU) | `O(log M)` | `O(M³)` | largest `λ`, simplest circuit |
| single factorization (SF) | `O(M)` | smaller | Cholesky of the ERI matrix, rank `O(M)` |
| double factorization (DF) | `O(M)` | smaller still | diagonalize each Cholesky vector; truncate twice |
| tensor hypercontraction (THC) | `O(M)` | smallest | rank-`O(M)` grid representation of the ERI tensor |

Each step replaces an explicit sum over integrals with a compressed form whose `1`-norm is
genuinely lower, at the price of more ancilla qubits and a more elaborate `PREPARE`. The
historical resource reductions for FeMoco came almost entirely from this ladder — not from a better
phase-estimation algorithm. It is worth saying plainly, because it is easy to assume otherwise:
**the largest speedups in fault-tolerant quantum chemistry have come from classical linear
algebra applied to the Hamiltonian before the quantum computer ever sees it.**

---

## Honest Resource Estimates: FeMoco

FeMoco, the iron-molybdenum cofactor of nitrogenase (Chapter 08/03), is the field's benchmark
target: a 7-Fe, 9-S, 1-Mo, 1-C cluster whose minimal chemically meaningful active space is
CAS(54,54) — `3.8 × 10³⁰` determinants, hopelessly beyond classical CASSCF, and 108 qubits before
tapering.

The published trajectory:

| study | method | logical qubits | non-Clifford cost |
|---|---|---|---|
| Reiher et al. (2017) | Trotter + QPE | ~111 | `~10^{14}–10^{15}` T gates |
| Berry et al. (2019) | qubitization, sparse/SF | ~2,000 | `~10^{10}` Toffolis |
| von Burg et al. (2021) | qubitization, DF | ~4,000 | `~10^{9}–10^{10}` Toffolis |
| Lee et al. (2021) | qubitization, THC | ~2,000–4,000 | low `10^{9}` Toffolis |

Roughly five orders of magnitude in four years, with the logical qubit count *rising* — ancillas
bought the speedup. (A Toffoli costs about 4 T gates with catalyzed distillation, so the last rows
are `~10^{10}` T gates.)

The arithmetic is checkable from the formula above. With `λ ≈ 300` Ha, the value reported for
double-factorized FeMoco-scale Hamiltonians, and `ε = 1.6` mHa:

```
queries ≈ π × 300 / (2 × 1.6 × 10⁻³) ≈ 2.9 × 10⁵
```

At `10³`–`10⁴` Toffolis per query — the cost of `PREPARE`/`SELECT` over a few thousand coefficients
— that is `3 × 10⁸` to `3 × 10⁹` Toffolis, landing squarely on the published rows. With a
single-factorized `λ ≈ 1500` Ha the query count rises to `1.5 × 10⁶`, which is exactly why the
factorization ladder was worth climbing.

Translating to wall-clock and physical qubits requires the surface code (Chapter 05/06). Toffolis
are produced serially by magic-state factories, so at a rate `R`:

```
runtime ≈ N_Toffoli / R      3 × 10⁹ Toffolis at 10⁵ /s ≈ 8 hours;  at 10⁴ /s ≈ 3.5 days
```

and the factories, not the algorithm qubits, dominate the footprint: a few thousand logical qubits
at code distance `~25–35` plus distillation gives physical-qubit estimates in the low millions.
That is the honest summary — FeMoco is not a NISQ target, not a "thousand-qubit" target, and not
impossible: it is a millions-of-physical-qubits, hours-to-days target whose cost estimate is still
falling.

---

## Key Formulas

- **QPE readout**: `E = 2πk/(2^m t) - Δ`, resolution `2π/(2^m t)`, bits `m ≥ log₂(W/2ε)`
- **QPE success probability**: `|⟨φ|ψ₀⟩|²`; repetitions `∝ 1/|⟨φ|ψ₀⟩|²`
- **Hamiltonian `1`-norm**: `λ = Σ_j|c_j|`, the single cost parameter of qubitization
- **Qubitization queries**: `≈ πλ/(2ε)` for energy precision `ε`
- **VQE versus QPE**: `S ∝ (λ/ε)²` shots versus `∝ λ/ε` coherent queries
- **Toffoli-to-T**: `1` Toffoli `≈ 4` T gates with catalyzed distillation

---

## Worked Example: QPE on the Tapered H₂ Hamiltonian

Take the two-qubit tapered H₂ Hamiltonian from Chapter 10/02, shift it by `Δ = 2` Ha so the
spectrum `{-1.857, …, -0.225}` becomes positive, and set `t = 2π/4` so the encoded window is
exactly `4` Ha:

```python
import numpy as np
from scipy.linalg import expm
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate, QFTGate
from qiskit.quantum_info import Statevector, SparsePauliOp

H = SparsePauliOp(["II", "ZI", "IZ", "ZZ", "XX"],
                  coeffs=[-1.05237325, -0.39793742, +0.39793742,
                          -0.01128010, +0.18093119])
E_nuc, SHIFT, T = 0.71996899, 2.0, 2 * np.pi / 4.0
Hm = H.to_matrix().real
E_exact = np.linalg.eigvalsh(Hm).min()
U = expm(1j * (Hm + SHIFT * np.eye(4)) * T)

m = 12                                   # ancilla (readout) bits
qc = QuantumCircuit(m + 2)
qc.x(m)                                  # |HF> on the system register
qc.h(range(m))
for k in range(m):
    qc.append(UnitaryGate(np.linalg.matrix_power(U, 2 ** k)).control(1), [k, m, m + 1])
qc.append(QFTGate(m).inverse(), range(m))

probs = Statevector(qc).probabilities(range(m))
best = int(np.argmax(probs))
E_est = 2 * np.pi * (best / 2 ** m) / T - SHIFT
print(f"peak bin {best}/{2**m}, p = {probs[best]:.4f}")
print(f"E_elec(QPE)  = {E_est:.8f}   error = {1e3*(E_est-E_exact):+.3f} mHa")
print(f"E_total(QPE) = {E_est + E_nuc:.8f}   (exact {E_exact + E_nuc:.8f})")
```

Output (Qiskit 2.5.2):

```
peak bin 146/4096, p = 0.9162
E_elec(QPE)  = -1.85742188   error = -0.147 mHa
E_total(QPE) = -1.13745289   (exact -1.13730604)
```

Sweeping the ancilla count exposes the two error mechanisms separately:

| `m` | bin size | peak probability | error |
|---|---|---|---|
| 6 | 62.5 mHa | 0.752 | -17.7 mHa |
| 8 | 15.6 mHa | 0.930 | -2.10 mHa |
| 10 | 3.91 mHa | 0.462 | +1.81 mHa |
| 12 | 0.977 mHa | 0.916 | -0.147 mHa |
| 14 | 0.244 mHa | 0.568 | +0.097 mHa |

The error tracks the bin size and crosses chemical accuracy between `m = 10` and `m = 12`, as
`m ≥ log₂(4/0.0032) = 10.3` predicts. The peak probability, by contrast, does *not* increase
monotonically: it dips whenever the true phase falls near a bin boundary and the weight splits
between two neighbouring bins (`m = 10` and `m = 14` here). The standard fix is to add
`⌈log₂(2 + 1/2δ)⌉` extra bits, which guarantees the correct value to `m` bits with probability
`1 - δ` regardless of where the phase sits.

Two caveats keep this example honest. First, the peak probability is capped by
`|⟨Φ_HF|ψ₀⟩|² = 0.988`; the remaining `1.2 %` lands on the excited eigenvalue `-0.225` Ha, and on
a larger molecule that leakage is the dominant repetition cost. Second, the circuit here uses
exact matrix exponentials via `UnitaryGate`, which is legitimate for a `4 × 4` matrix and
completely unavailable at scale — everything in the resource-estimate section exists to replace
that one line.

---

## Summary

- QPE reaches precision `ε` with `O(1/ε)` applications of a controlled evolution — quadratically
  better than VQE's `O(1/ε²)` sampling — at the price of coherence far beyond NISQ devices.
- Readout bits are cheap (`m ≥ log₂(W/2ε)`); the cost is the `2^m` controlled evolutions, and the
  success probability is set by the reference overlap `|⟨φ|ψ₀⟩|²`, which decays exponentially with
  size for strongly correlated systems.
- Qubitization costs `≈ πλ/(2ε)` queries with `λ = ||H||₁`, so the whole engineering problem is
  shrinking `λ`: sparse → single factorization → double factorization → tensor hypercontraction.
- FeMoco estimates fell from `~10^{14}` T gates (Reiher 2017, Trotter) to low `10⁹` Toffolis
  (Lee 2021, THC) almost entirely through better Hamiltonian representations, with logical qubit
  counts rising from ~111 to a few thousand.
- Verified on tapered H₂: 12 readout bits give `-1.137453` Ha against an exact `-1.137306` Ha, an
  error of `0.147` mHa — inside chemical accuracy, with peak probability `0.916`.

---

## Exercises

**Exercise 1**: A molecule's active-space Hamiltonian has a spectral window `W = 80` Ha. How many
QPE readout bits are needed for `1.6` mHa resolution, and how many controlled evolutions does the
circuit contain?

<details><summary>Solution</summary>

`m ≥ log₂(W / 2ε) = log₂(80 / 0.0032) = log₂(25000) = 14.6`, so `m = 15` bits (bin size
`80/2¹⁵ = 2.44` mHa; `m = 16` gives `1.22` mHa if a margin is wanted).

The ancilla `k` controls `U^{2^k}`, so the total number of applications of `U` is
`Σ_{k=0}^{14} 2^k = 2¹⁵ - 1 = 32,767`. Fifteen qubits of readout is trivial; thirty-three thousand
coherent, controlled Hamiltonian evolutions in a row is the entire difficulty, and it is why the
`λ` of the evolution — not the ancilla count — is the quantity worth optimizing.

</details>

**Exercise 2**: Compare VQE and qubitized QPE for a Hamiltonian with `λ = 100` Ha at
`ε = 1.6` mHa. At what precision would VQE's sampling cost equal QPE's query cost, assuming one
shot and one query cost the same?

<details><summary>Solution</summary>

VQE: `S ≈ (λ/ε)² = (100/0.0016)² = 3.9 × 10⁹` shots per energy evaluation, times hundreds of
optimizer iterations — call it `10¹²`.

QPE: `πλ/(2ε) = π × 100 / 0.0032 = 9.8 × 10⁴` queries, once.

Setting `(λ/ε)² = πλ/(2ε)` gives `ε = 2λ/π ≈ 64` Ha. In other words, VQE only "wins" on raw
operation count at precisions vastly coarser than chemistry needs. The reason VQE is nonetheless
the right near-term algorithm is that its `3.9 × 10⁹` shots are *independent short circuits*,
tolerant of noise and trivially parallel, while QPE's `9.8 × 10⁴` queries must be coherent —
comparing operation counts alone mistakes the constraint.

</details>

**Exercise 3**: Halving `λ` by a better factorization also doubles the ancilla count. Argue,
using surface-code costs, when this is worth doing.

<details><summary>Solution</summary>

Halving `λ` halves the Toffoli count and therefore the runtime, which is linear in `λ`. Doubling
the ancilla register adds a fixed number of logical qubits, and logical qubits cost physical qubits
*linearly* (`~2d²` physical per logical at distance `d`).

So the trade is a factor-2 saving in time against an additive increase in space — and in a
fault-tolerant machine the dominant space cost is usually the magic-state factories, whose size is
set by the Toffoli *rate* required, not by the algorithm register. Fewer Toffolis lets the factory
shrink too. The trade is therefore almost always worth taking, which is exactly what the historical
progression shows: the FeMoco logical qubit count rose from ~111 to a few thousand while the
non-Clifford cost fell by five orders of magnitude.

The trade reverses only when ancillas push the total beyond what the hardware has at all, or when
distance must be raised because the longer-lived extra qubits raise the total logical error budget.

</details>

**Exercise 4**: In the worked example, `m = 10` gives a *worse* peak probability (0.462) than
`m = 8` (0.930). Explain, and say why this does not mean `m = 8` is the better choice.

<details><summary>Solution</summary>

QPE's output distribution is peaked on the bin nearest the true phase, with the sharpness set by
how close the phase is to a bin *centre*. The shifted, scaled ground-state phase is
`φ = (E + 2)/4 = 0.0356812…`. At `m = 8`, `2⁸φ = 9.13`, close to the integer 9, so almost all the
weight lands in one bin. At `m = 10`, `2¹⁰φ = 36.54` — nearly exactly halfway — so the weight
splits between bins 36 and 37 and the peak drops.

This is a property of the *readout*, not of the accuracy: the `m = 10` estimate is still four
times more precise than the `m = 8` estimate (`3.91` mHa bins versus `15.6` mHa), and the split
weight is recovered by a handful of repetitions or by the extra `⌈log₂(2 + 1/2δ)⌉` bits. Never
choose fewer bits to make a single-shot histogram look cleaner.

</details>

---

## Further Reading

1. **Aspuru-Guzik, A., Dutoi, A. D., Love, P. J. and Head-Gordon, M.** — "Simulated quantum
   computation of molecular energies," *Science* 309, 1704 (2005). The paper that put QPE on
   molecular Hamiltonians and introduced the overlap-with-Hartree-Fock argument.
2. **Reiher, M., Wiebe, N., Svore, K. M., Wecker, D. and Troyer, M.** — "Elucidating reaction
   mechanisms on quantum computers," *PNAS* 114, 7555 (2017). The original FeMoco resource
   estimate, Trotter-based.
3. **Low, G. H. and Chuang, I. L.** — "Hamiltonian simulation by qubitization," *Quantum* 3, 163
   (2019). The walk-operator construction and the `λt` query bound used throughout this chapter.
4. **von Burg, V., Low, G. H., Häner, T., Steiger, D. S., Reiher, M., Roetteler, M. and Troyer, M.**
   — "Quantum computing enhanced computational catalysis," *Phys. Rev. Research* 3, 033055 (2021).
   Double factorization and a full surface-code accounting for FeMoco.
5. **Lee, J., Berry, D. W., Gidney, C., Huggins, W. J., McClean, J. R., Wiebe, N. and Babbush, R.**
   — "Even more efficient quantum computations of chemistry through tensor hypercontraction,"
   *PRX Quantum* 2, 030305 (2021). The current low-water mark for FeMoco-scale Toffoli counts.
