# Data Encoding and Quantum Feature Maps

> **Prerequisites**: Linear algebra and Dirac notation (01/01), tensor products (01/03),
> single- and multi-qubit gates (03/01, 03/02), circuit universality (03/03)
> **Connects to**: Quantum kernels (09/02), variational classifiers (09/03), HHL and the
> state-preparation bottleneck (04/07), ansatz design (06/02)

---

## Overview

A quantum computer cannot read a CSV file. Before any quantum machine learning model can touch a
data point `x ∈ ℝ^d`, that point must be turned into a quantum state `|φ(x)⟩` by a circuit
`U_φ(x)` acting on `|0⟩^{⊗n}`. That circuit is the **encoding**, or **feature map**, and it is
the single most consequential design choice in the field.

It fixes three things at once. The **hypothesis class**: the map `x ↦ |φ(x)⟩` determines exactly
which functions the downstream model can express, as the Fourier analysis below makes precise.
The **cost**: loading `d` real numbers into amplitudes takes `Θ(d)` gates in the worst case,
usually enough to destroy any exponential speedup the rest of the algorithm offered. And
**trainability**: an expressive, entangling encoding pushes the model's outputs exponentially
close to a constant, producing barren plateaus that no optimizer repairs (09/03).

This chapter surveys the standard encodings — basis, amplitude, angle, and IQP-style feature
maps — with gate costs measured rather than asserted, then develops the data re-uploading picture
that unifies them. Every number was produced with Qiskit 2.5.2 and NumPy.

---

## The Encoding Problem

An encoding is a family of unitaries `{U_φ(x)}_{x ∈ 𝒳}` on `n` qubits with induced state map
`|φ(x)⟩ = U_φ(x)|0⟩^{⊗n}`. Encodings differing by a global phase or a fixed trailing unitary are
equivalent: the downstream model absorbs the fixed part. What is *not* absorbable is the geometry
the encoding induces, summarized by the **fidelity kernel**:

```
K(x, x') = |⟨φ(x)|φ(x')⟩|²
```

Every model sees the data only through these inner products, so choosing an encoding *is*
choosing a similarity measure on the data.

A usable encoding must be **cheap** (gates and depth fit the hardware, per point, per shot),
**injective enough** (differently labelled points map to distinguishable states),
**non-concentrating** (`K` must not collapse to a constant as `n` grows), and **not classically
trivial** (if `K` has a closed form computable in `O(poly(d))`, a laptop is faster). The last two
pull in opposite directions, and that tension is the central difficulty of the field: simple
encodings give closed-form kernels, complicated encodings give concentrated ones.

---

## Basis Encoding

The most literal encoding maps a bit string to the corresponding computational basis state,
`x = b_{n-1} … b_0 ↦ |b_{n-1} … b_0⟩`. Implementation: one `X` gate per set bit, depth 1,
`n` qubits for `n` bits. Encoding `x = 1011` costs three `X` gates.

It is exact, trivially cheap, and almost useless alone — the states are mutually orthogonal, so
`K(x, x') = δ_{xx'}` and every point is maximally dissimilar from every other. It becomes useful
only inside a superposition: `|D⟩ = M^{-1/2} Σ_m |x_m⟩|y_m⟩` over a whole training set is the
starting point of several textbook QML algorithms, but preparing it needs quantum RAM or an
explicit `Θ(M)` circuit, which is where those algorithms quietly lose their speedup.

---

## Amplitude Encoding

Amplitude encoding stores a `d`-dimensional vector in the amplitudes of `n = ⌈log₂ d⌉` qubits:

```
|φ(x)⟩ = (1/‖x‖) Σ_{k=0}^{d-1} x_k |k⟩
```

The appeal is `d = 2^n` numbers in `n` qubits. The catch: amplitudes are not readable, the vector
must be normalized (so `‖x‖` is lost unless stored separately), and state preparation is costly.

### Measured State-Preparation Cost

Qiskit's `StatePreparation` uses a multiplexed-rotation construction of the
Möttönen/Shende–Bullock–Markov family. Transpiled to `{u, cx}`, its cost for a generic complex
amplitude vector is:

```
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import StatePreparation

rng = np.random.default_rng(7)
for n in range(2, 8):
    v = rng.normal(size=2**n) + 1j*rng.normal(size=2**n)
    v /= np.linalg.norm(v)
    qc = QuantumCircuit(n)
    qc.append(StatePreparation(v), range(n))
    t = transpile(qc, basis_gates=["u", "cx"],
                  optimization_level=3, seed_transpiler=1)
    print(n, 2**n, t.count_ops()["cx"], t.depth())
```

Output (qiskit 2.5.2):

| `n` | `d = 2ⁿ` | CNOTs | depth |
|-----|----------|-------|-------|
| 2 | 4 | 1 | 3 |
| 3 | 8 | 4 | 9 |
| 4 | 16 | 11 | 23 |
| 5 | 32 | 26 | 53 |
| 6 | 64 | 57 | 115 |
| 7 | 128 | 120 | 241 |

The counts fit `CNOT(n) = 2ⁿ - n - 1` and `depth(n) = 2^{n+1} - 2n - 1` exactly. Loading `d`
features therefore costs `d - log₂ d - 1 ≈ d` two-qubit gates: **linear in the data, not
logarithmic**. A 1024-feature vector needs 10 qubits but 1013 CNOTs at depth 2027, already beyond
what current hardware runs with useful fidelity.

This is the **state-preparation bottleneck**, and it is why most claimed exponential QML speedups
evaporate. An algorithm running in `O(polylog d)` after loading still needs `Ω(d)` to load, unless
the state has structure (sparsity, an efficiently computable amplitude function, or quantum RAM).
Qiskit's generic routine does not even exploit sparsity: a 2-sparse 6-qubit state still
transpiles to 54 CNOTs.

---

## Angle (Product) Encoding

Angle encoding spends one qubit per feature and one rotation per qubit:

```
|φ(x)⟩ = ⊗_{i=1}^{n} R_y(x_i)|0⟩ = ⊗_{i=1}^{n} [cos(x_i/2)|0⟩ + sin(x_i/2)|1⟩]
```

Cost: `n` qubits, `n` single-qubit gates, depth 1, zero entanglement — the cheapest useful
encoding and the default for near-term experiments. The state factorizes, so the overlap does:

```
K(x, x') = ∏_{i=1}^{n} cos²((x_i - x'_i)/2)
```

confirmed to `10^{-17}` against Qiskit statevectors. The angle kernel is therefore computable
classically in `O(n)` arithmetic, and running it on hardware is strictly worse than running it in
NumPy — the same answer with shot noise attached. Angle encoding is a legitimate choice for
*hardware experiments*, but it cannot produce an advantage, and any paper claiming one on top of
a product encoding has a bug.

---

## IQP and ZZ Feature Maps

To get past product kernels the encoding must entangle. The standard construction (Havlíček et
al., 2019) is an **instantaneous quantum polynomial (IQP)** circuit: Hadamards, then a layer of
diagonal phase gates whose angles are functions of the data, repeated `R` times.

```
U_φ(x) = [ U_Z(x) H^{⊗n} ]^R

U_Z(x) = exp( i Σ_{S ⊆ [n], |S| ≤ 2} φ_S(x) ∏_{i ∈ S} Z_i )
```

Qiskit's `zz_feature_map` uses `φ_i(x) = 2 x_i` and `φ_{ij}(x) = 2(π - x_i)(π - x_j)`,
implemented as `P(2x_i)` on each qubit and `CX–P(2(π-x_i)(π-x_j))–CX` on each pair. For
`n = 2, R = 2` the decomposed circuit is 10 single-qubit gates and 4 CNOTs at depth 10.

The motivation is a hardness *conjecture*, not a theorem. Sampling from IQP output distributions
is classically hard unless the polynomial hierarchy collapses (Bremner, Jozsa and Shepherd, 2011),
so it is plausible that the induced kernel is hard to estimate too. The step from "sampling is
hard" to "estimating this one overlap to additive error `ε` is hard" has never been closed — and
additive `ε` is all a kernel method needs. Treat the ZZ feature map as a heuristic with
suggestive provenance, not a proven source of advantage (09/04).

---

## Data Re-uploading and the Fourier Picture

Nothing forbids feeding the data in more than once. **Data re-uploading** (Pérez-Salinas et al.,
2020) interleaves trainable blocks `W(θ_r)` with encoding blocks `S(x)`:

```
U(x, θ) = W(θ_R) S(x) W(θ_{R-1}) S(x) … W(θ_1) S(x) W(θ_0)
```

This makes a single qubit a universal function approximator and gives the cleanest answer to
"what can this model express?"

**Theorem (Schuld, Sweke and Meyer, 2021)**: if each encoding block is `S(x) = e^{-i x G}` with
generator `G` having eigenvalues `{λ_1, …, λ_D}`, the model output is a truncated Fourier series

```
f(x, θ) = Σ_{ω ∈ Ω} c_ω(θ) e^{i ω x}
```

whose frequency set `Ω` is the set of eigenvalue differences `λ_j - λ_k`, summed over the `R`
repetitions. The trainable blocks control the coefficients `c_ω(θ)`; the *encoding alone*
controls which frequencies exist at all. For `S(x) = R_z(x)` (generator `Z/2`, eigenvalues
`±1/2`) repeated `R` times, `Ω = {-R, …, R}`:

```
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

Z = SparsePauliOp("Z")
rng = np.random.default_rng(42)

def model(x, R, W):
    qc = QuantumCircuit(1)
    for r in range(R):
        qc.u(*W[r], 0)      # trainable block
        qc.rz(x, 0)         # data-encoding block, generator Z/2
    qc.u(*W[R], 0)
    return np.real(Statevector(qc).expectation_value(Z))

N = 64
grid = 2*np.pi*np.arange(N)/N
for R in [1, 2, 3, 5]:
    W = rng.uniform(0, 2*np.pi, size=(R+1, 3))
    c = np.fft.fft([model(x, R, W) for x in grid])/N
    print(R, [w for w in range(N//2) if abs(c[w]) > 1e-10],
          np.round(np.abs(c[:R+2]), 4))
```

Output:

```
1 [0, 1]             [0.0487 0.4676 0.    ]
2 [0, 1, 2]          [0.6561 0.088  0.0094 0.    ]
3 [0, 1, 2, 3]       [0.3279 0.2622 0.1298 0.0696 0.    ]
5 [0, 1, 2, 3, 4, 5] [0.2564 0.3056 0.2349 0.056  0.0245 0.0021 0.    ]
```

Exactly `R + 1` non-negative frequencies every time, identically zero above `ω = R` (to
`10^{-16}`): an `R = 3` model cannot represent `cos(4x)` however it is trained. The theorem also
explains why encodings are rescaled in practice — replacing `R_z(x)` by `R_z(c·x)` rescales the
frequency axis by `c`, the "bandwidth" knob that dominates kernel concentration (09/02).

---

## Choosing an Encoding

| Encoding | Qubits | Gates | Depth | Kernel | Classical cost of kernel |
|----------|--------|-------|-------|--------|--------------------------|
| Basis | `n` bits | ≤ `n` `X` | 1 | `δ_{xx'}` | `O(n)` |
| Amplitude | `⌈log₂ d⌉` | `≈ d` CNOT | `≈ 2d` | `(x·x'/‖x‖‖x'‖)²` | `O(d)` |
| Angle (product) | `d` | `d` | 1 | `∏ cos²((x_i-x'_i)/2)` | `O(d)` |
| ZZ / IQP, `R` reps | `d` | `O(R d²)` | `O(R d)` | no closed form | conjectured hard |
| Re-uploading, `R` reps | `1`–`d` | `O(R d)` | `O(R d)` | truncated Fourier | depends on `R` |

The last two rows are the only candidates for advantage, and they are exactly the two whose
kernels concentrate (09/02) and whose gradients vanish (09/03) — not a coincidence, but the shape
of the field.

---

## Key Formulas

- **Feature map and fidelity kernel**: `|φ(x)⟩ = U_φ(x)|0⟩^{⊗n}`, `K(x, x') = |⟨φ(x)|φ(x')⟩|²`
- **Amplitude encoding**: `|φ(x)⟩ = ‖x‖^{-1} Σ_k x_k|k⟩` on `n = ⌈log₂ d⌉` qubits
- **Measured state-prep cost**: `CNOT(n) = 2ⁿ - n - 1`, `depth(n) = 2^{n+1} - 2n - 1`
- **Angle encoding kernel**: `K(x, x') = ∏_i cos²((x_i - x'_i)/2)`
- **ZZ feature map phases**: `φ_i(x) = 2x_i`, `φ_{ij}(x) = 2(π - x_i)(π - x_j)`
- **Re-uploading spectrum**: `f(x, θ) = Σ_{ω ∈ Ω} c_ω(θ)e^{iωx}` with `|Ω| = 2R + 1` for a
  `Z/2` generator repeated `R` times

---

## Worked Example: Three Encodings, Three Geometries

**Amplitude encoding.** Normalize first: `‖x‖ = √(1 + 4 + 9 + 16) = √30 ≈ 5.477226`. On
`n = ⌈log₂ 4⌉ = 2` qubits,

```
|φ(x)⟩ = (1|00⟩ + 2|01⟩ + 3|10⟩ + 4|11⟩)/√30
       = 0.182574|00⟩ + 0.365148|01⟩ + 0.547723|10⟩ + 0.730297|11⟩
```

with probabilities `(1, 4, 9, 16)/30 = (0.0333, 0.1333, 0.3000, 0.5333)`, summing to 1. Qiskit's
`StatePreparation` reproduces these amplitudes and transpiles to 3 `u` gates and **1 CNOT** at
depth 3, matching `2² - 2 - 1 = 1`. The multiplexed-rotation construction builds it from a binary
tree of `R_y` angles: the root splits the vector into halves of norm `a = √5/√30 = 0.408248` and
`b = √25/√30 = 0.912871`, so `θ_root = 2 arccos(a) = 2.300524`, `θ_left = 2.214297` and
`θ_right = 1.854590`.

**Angle encoding.** Take `x = (0.3, 1.1)` and `x' = (0.9, 0.5)`; both differences are `∓0.6`, so
`K(x, x') = cos²(-0.3) cos²(0.3) = 0.9126678² = 0.8329625`, and the Qiskit statevector overlap
gives `0.8329625267644228` — agreement to `5 × 10^{-16}`. Two qubits, two gates, depth 1, and the
kernel was computed with a pocket calculator; the circuit added nothing.

**ZZ feature map.** For the same pair of points with `zz_feature_map(2, reps=2)` the fidelity
kernel is `0.7283896449145755`, computed two independent ways — Qiskit statevectors, and an
explicit `4 × 4` matrix product from `H`, the two `P(2x_i)` phases and
`CX–P(2(π-x₀)(π-x₁))–CX` — agreeing to the last printed digit. There is no closed form to check
it against, which is exactly the point of using it and exactly why it costs 4 CNOTs at depth 10
instead of 0 CNOTs at depth 1. The same pair of points reads as `0.833` similar under the angle
kernel and `0.728` similar under the ZZ kernel; with a gate cost spanning three orders of
magnitude once `d` grows, the encoding is the model.

---

## Summary

- The encoding `x ↦ |φ(x)⟩` fixes the hypothesis class, cost and trainability of every downstream
  QML model; it is not a preprocessing detail.
- **Basis encoding** is free but makes all points orthogonal; it is useful only inside a dataset
  superposition, which itself costs `Ω(M)`.
- **Amplitude encoding** packs `d` features into `⌈log₂ d⌉` qubits but costs `2ⁿ - n - 1` CNOTs
  at depth `2^{n+1} - 2n - 1` (measured on Qiskit 2.5.2) — linear in the data. This
  state-preparation bottleneck destroys most claimed exponential speedups.
- **Angle encoding** is depth-1 with the closed-form kernel `∏ cos²((x_i - x'_i)/2)`, evaluable
  classically in `O(d)`; it can never give an advantage.
- **IQP/ZZ feature maps** entangle and have no known closed form, motivated by an IQP *sampling*
  hardness result never extended to additive-error kernel estimation.
- **Data re-uploading** makes the model a truncated Fourier series whose frequency set is fixed
  entirely by the encoding: `R` repetitions of `R_z` give exactly `{-R, …, R}`, verified to
  `10^{-16}`.

---

## Exercises

**1.** Amplitude-encode `x = (3, 0, 4, 0)`. Give the normalization, amplitudes, measurement
probabilities and qubit count. How many CNOTs does the generic Qiskit routine use, and how many
are actually necessary?

<details><summary>Solution</summary>

`‖x‖ = √(9 + 16) = 5`, so `|φ(x)⟩ = 0.6|00⟩ + 0.8|10⟩` with probabilities `0.36` and `0.64` on
`n = 2` qubits. The closed form gives `2² - 2 - 1 = 1` CNOT, and the generic routine uses it.
But this state is a *product* state, `(0.6|0⟩ + 0.8|1⟩) ⊗ |0⟩`, so **zero** CNOTs are necessary:
a single `R_y(2 arctan(4/3)) = R_y(1.8546)` suffices. The generic multiplexed-rotation routine
does not detect the factorization — the same blindness that leaves a 2-sparse 6-qubit state at
54 CNOTs.

</details>

**2.** A dataset has `d = 4096` features. How many qubits, CNOTs and layers of depth does generic
amplitude encoding require? Compare the CNOT count with the classical cost of one inner product
against the same vector.

<details><summary>Solution</summary>

`n = log₂ 4096 = 12` qubits, `CNOT = 2¹² - 12 - 1 = 4083`, `depth = 2¹³ - 24 - 1 = 8167`.
A classical inner product is 4096 multiply-accumulates, roughly a microsecond on one core. The
circuit needs 4083 two-qubit gates *per data point, per shot*; at 300 ns per CNOT that is 1.2 ms
of coherent evolution before any computation begins, with an expected two-qubit error count of
`4083 × 10^{-3} ≈ 4` even at excellent fidelity. The encoding costs more than the classical
algorithm it is meant to beat.

</details>

**3.** Compute the angle-encoding kernel for `x = (0, 0, 0)` and `x' = (π/2, π/3, π/4)`, then
state when the angle kernel equals 1 and when it equals 0.

<details><summary>Solution</summary>

```
K = cos²(π/4) · cos²(π/6) · cos²(π/8)
  = 0.500000 × 0.750000 × 0.853553 = 0.320083
```

confirmed against the Qiskit overlap to `10^{-16}`. `K = 1` iff every `x_i - x'_i ≡ 0 (mod 4π)`.
`K = 0` iff *any single* factor vanishes, i.e. some `x_i - x'_i ≡ 2π (mod 4π)` — one antipodal
feature zeroes the kernel regardless of the other `n - 1`. This brittleness (a product of `n`
numbers below 1) is the first hint of the concentration analysed in 09/02: for data drawn
uniformly, `E[K] = E[cos²(Δ/2)]^n = 2^{-n}`.

</details>

**4.** A single-qubit re-uploading model uses `R = 5` repetitions of `R_z(x)`. Can it fit
`g(x) = 0.5 cos(2x) − 0.3 sin(5x)`? Can it fit `h(x) = cos(6x)`? Give the cheapest fix for the
case that fails.

<details><summary>Solution</summary>

`R = 5` gives `Ω = {-5, …, 5}`, so `g` is representable in principle — it uses only frequencies 2
and 5. `h` needs `ω = 6 ∉ Ω`, so the model's coefficient there is *identically zero*; the
numerical spectrum above shows `|c_6| < 10^{-16}` for `R = 5`, and no training run changes it.
Two fixes: add a sixth repetition (one extra encoding gate plus one trainable block), or rescale
the encoding to `R_z(c·x)` with `c = 6/5`, mapping the target's frequency 6 onto the model's
frequency 5 at zero gate cost. Rescaling changes the learned function's period, so it only works
when the whole target rescales consistently.

</details>

**5.** You must classify 1000 samples with 64 features each on hardware with 300 ns CNOTs.
Compare total two-qubit gate time for one pass using (a) amplitude and (b) angle encoding, and
say what (b) gives up.

<details><summary>Solution</summary>

(a) Amplitude: `n = 6` qubits, `2⁶ - 6 - 1 = 57` CNOTs per sample, `57 000` CNOTs `≈ 17.1 ms` of
two-qubit gate time per pass, on 6 qubits.
(b) Angle: 64 qubits, **0** CNOTs, one layer of single-qubit rotations — sub-microsecond, with
depth independent of `d`.

Angle encoding is over four orders of magnitude cheaper in two-qubit time, and since error rates
track gate counts it is far more accurate on hardware. What it gives up is any possibility of
advantage — `∏ cos²((x_i - x'_i)/2)` is closed-form classical arithmetic — and qubit economy,
64 qubits instead of 6.

</details>

---

## Further Reading

1. **Schuld, M. and Petruccione, F.** — *Machine Learning with Quantum Computers*, 2nd ed.,
   Springer (2021). The chapters on information encoding and on quantum models as kernel methods
   are the standard reference for the encoding taxonomy used here.
2. **Havlíček, V. et al.** — "Supervised learning with quantum-enhanced feature spaces,"
   *Nature* 567, 209–212 (2019). Introduces the ZZ/IQP feature map and the hardness argument
   behind it.
3. **Schuld, M., Sweke, R. and Meyer, J. J.** — "Effect of data encoding on the expressive power
   of variational quantum machine learning models," *Phys. Rev. A* 103, 032430 (2021). The
   Fourier-series theorem verified numerically above.
4. **Pérez-Salinas, A. et al.** — "Data re-uploading for a universal quantum classifier,"
   *Quantum* 4, 226 (2020). Introduces re-uploading and proves single-qubit universality.
5. **Shende, V. V., Bullock, S. S. and Markov, I. L.** — "Synthesis of quantum-logic circuits,"
   *IEEE Trans. CAD* 25, 1000–1010 (2006), Section IV. The multiplexed-rotation state-preparation
   construction whose `2ⁿ - n - 1` CNOT count Qiskit reproduces.
