# Quantum Kernel Methods

> **Prerequisites**: Data encoding and feature maps (09/01), inner products and Hilbert spaces
> (01/02), probability and estimators (01/06), density matrices and partial trace (02/05)
> **Connects to**: Variational classifiers (09/03), QML in practice (09/04), quantum complexity
> (08/01), shot-noise accounting (06/03)

---

## Overview

Kernel methods are the one corner of machine learning where quantum computing has a clean story.
A support vector machine never touches its feature vectors directly; it needs only the inner
products `⟨φ(x), φ(x')⟩`. So if a quantum computer can prepare `|φ(x)⟩` and estimate
`|⟨φ(x)|φ(x')⟩|²`, it slots into the classical machinery as a drop-in kernel, leaving the convex
optimization and the generalization theory intact.

That structural fit is genuine, and it is why quantum kernels are the best-understood QML model.
What does not follow is any advantage. This chapter develops the construction, computes a real
kernel matrix on qiskit 2.5.2 and trains a classifier with it, then spends equal effort on the
three reasons not to over-read the result: the fidelity kernel concentrates exponentially,
estimating it costs `O(1/ε²)` shots per entry, and classical algorithms match several proposed
"advantage" kernels.

---

## The Kernel Trick, Briefly

A classifier `f(x) = sign(w · φ(x) + b)` is linear in a feature space `φ: 𝒳 → ℋ` that may be far
larger than the input space. The representer theorem puts the optimal `w` in the span of the
training features, `w = Σ_m α_m φ(x_m)`, so

```
f(x) = sign( Σ_m α_m ⟨φ(x_m), φ(x)⟩ + b ) = sign( Σ_m α_m k(x_m, x) + b )
```

and the feature map appears only through the **kernel** `k(x, x') = ⟨φ(x), φ(x')⟩`. Training
needs the `M × M` **Gram matrix** `K_{mm'} = k(x_m, x_{m'})` and nothing else. A function `k` is
a valid kernel iff it is symmetric and positive semi-definite (Mercer); the classical workhorses
are the polynomial `(x·x' + c)^p` and the Gaussian (RBF) `exp(-γ‖x - x'‖²)`.

The worked examples below use **kernel ridge regression**, minimizing
`Σ_m (f(x_m) - y_m)² + λ‖w‖²` for the closed-form dual solution
`α = (K + λI)^{-1} y` with `f(x) = sign(Σ_m α_m k(x_m, x))`. An SVM gives slightly different
numbers; no conclusion below depends on the choice.

---

## The Fidelity Quantum Kernel

Given a feature map circuit `U_φ(x)` from 09/01, the natural kernel is the state overlap. Since
states are defined up to phase and the observable quantity is a probability, the standard choice
is the squared overlap, or **fidelity kernel**:

```
K_Q(x, x') = |⟨φ(x)|φ(x')⟩|² = |⟨0|U_φ(x)† U_φ(x')|0⟩|²
```

This is a valid Mercer kernel: `K_Q(x, x') = Tr[ρ(x)ρ(x')]` with `ρ(x) = |φ(x)⟩⟨φ(x)|` is the
Hilbert–Schmidt inner product of two positive operators, hence symmetric and PSD, with
`K_Q(x,x) = 1` and `0 ≤ K_Q ≤ 1`.

### Estimating It: Compute–Uncompute

The standard circuit runs the feature map forwards on `x'`, backwards on `x`, then measures:

```
|0⟩^{⊗n} ── U_φ(x') ── U_φ(x)† ── measure all n qubits
P(0…0) = |⟨0|U_φ(x)† U_φ(x')|0⟩|² = K_Q(x, x')
```

The estimator `K̂ = (# all-zero outcomes)/S` is unbiased with binomial variance `K(1-K)/S`, on
`n` qubits at twice the feature-map depth, no ancilla. The **SWAP test** is the alternative
(`2n + 1` qubits and a controlled-SWAP, but the two states prepared independently); the
**Hadamard test** gives the signed overlap `Re⟨φ(x)|φ(x')⟩` instead of its square.

Measured shot noise for one entry of the `zz_feature_map(2, reps=2)` kernel with
`x = (0.2, 0.4)`, `x' = (0.6, 0.8)`, over 200 repetitions on `AerSimulator`:

| shots `S` | 100 | 1 000 | 10 000 | 100 000 |
|-----------|-----|-------|--------|---------|
| mean `K̂` | 0.2833 | 0.2844 | 0.2856 | 0.2857 |
| observed std | 0.0417 | 0.0138 | 0.0044 | 0.0015 |
| `√(K(1-K)/S)` | 0.0452 | 0.0143 | 0.0045 | 0.0014 |

against the exact value `0.285768`; the binomial formula predicts the spread to within 10%. The
transpiled compute–uncompute circuit is 6 CNOTs at depth 14.

### The Gram Matrix Budget

Precision `ε` per entry costs `S ≈ K(1-K)/ε² ≤ 1/(4ε²)` shots, and `M` training points need
`M(M-1)/2` distinct entries plus `M·M_test` for prediction:

| `M` | 20 | 100 | 1 000 | 5 000 |
|-----|----|-----|-------|-------|
| entries | 190 | 4 950 | 499 500 | 12 497 500 |
| shots at `10⁴` each | `1.9×10⁶` | `4.95×10⁷` | `5.0×10⁹` | `1.25×10¹¹` |
| wall time at `10⁴`/s | 3 min | 1.4 h | 5.8 days | 145 days |

The quadratic scaling in `M` is inherited from classical kernel methods; the constant —
thousands of circuit executions per entry — is not, which is why no published quantum-kernel
experiment uses more than a few hundred training points.

---

## When Can a Quantum Kernel Help?

Three things must hold at once for a quantum kernel to beat every classical kernel:
(1) `K_Q` must be **hard to compute classically**, or you simulate it and skip the hardware;
(2) `K_Q` must be **well matched to the labels**, with the target function in or near the RKHS
`K_Q` induces, at small norm; (3) **no classical kernel** may be equally well matched — the part
almost never checked.

Huang et al. (2021) made requirement 3 quantitative with the **geometric difference**
`g(K_C, K_Q) = ‖√K_Q (K_C)^{-1} √K_Q‖_∞^{1/2}`, computed on the training inputs with both Gram
matrices trace-normalized. Large `g` is *necessary* for the quantum kernel to outperform the
classical one: if `g = O(1)`, the classical kernel matches the quantum predictions at comparable
sample complexity whatever the labels are. Since `g` needs only unlabelled data, it is a cheap
pre-flight check.

### The Artificial-Advantage Construction

There is a reliable way to make a quantum kernel win: define the labels with the quantum feature
map. Havlíček et al. (2019) label points by `y(x) = sign⟨φ(x)|V†(Z⊗Z)V|φ(x)⟩` for fixed random
`V`, discarding points near the boundary; the worked example below reproduces this, and the
quantum kernel reaches 95% test accuracy against RBF's 55–65%. This is a real, reproducible
separation that means almost nothing about real data: the labels were *defined* by the feature
map, so requirement 2 holds by construction and requirement 3 fails for the classical kernel by
construction. Liu, Arunachalam and Temme (2021) did produce a
*rigorous* end-to-end separation, a discrete-logarithm learning problem where a quantum kernel
achieves high accuracy and no classical algorithm can under the standard DLP assumption. That is
the existence proof the field needed; it is also about a problem nobody has data for.

---

## Exponential Concentration

The deepest obstacle is that the fidelity kernel collapses. If the feature map is expressive
enough to be interesting, random pairs of encoded states become nearly orthogonal and
`K_Q(x, x') → 0` for all `x ≠ x'`, exponentially in `n`. Measured with `zz_feature_map(n, reps=2)`
on 40 uniformly random points:

| `n` | 2 | 4 | 6 | 8 | 10 | 12 |
|-----|---|---|---|---|----|----|
| mean off-diag `K_Q` | 0.27530 | 0.06746 | 0.01942 | 0.00602 | 0.00191 | 0.00076 |
| std | 0.21814 | 0.06084 | 0.01894 | 0.00603 | 0.00179 | 0.00061 |
| max | 0.97920 | 0.42638 | 0.13076 | 0.03977 | 0.01321 | 0.00405 |
| `1/2ⁿ` | 0.25000 | 0.06250 | 0.01562 | 0.00391 | 0.00098 | 0.00024 |

The mean tracks `2^{-n}` closely. In the limit the Gram matrix becomes the identity, every point
is its own cluster, and the model memorizes the training set while generalizing at chance.
**Theorem (Thanasilp et al., 2024)**: for expressive feature maps (approximate 2-designs), global
measurements, or under local noise, `Var[K_Q(x,x')] ∈ O(2^{-n})` — `K_Q` concentrates around a
fixed value exponentially in `n`.

Concentration compounds with shot noise disastrously. Resolving an entry of size `2^{-n}` to 10%
*relative* accuracy needs `S ≈ (1-K)/(0.01K) ≈ 100·2ⁿ` shots — `10⁵` at `n = 10`, `10⁸` at
`n = 20`, `10¹¹` at `n = 30` — hence 2.9 hours per *single entry* at `n = 20` and `10⁴` shots/s,
and 166 years for a `1000 × 1000` Gram matrix.

### Two Partial Escapes

**Bandwidth tuning.** Rescaling the data, `x → c·x`, shrinks the region of Hilbert space the map
explores (Shaydulin and Wild, 2022; Canatar et al., 2023). At `n = 10` with 30 random points:

| `c` | 1.00 | 0.25 | 0.10 | 0.05 | 0.02 |
|-----|------|------|------|------|------|
| mean off-diagonal `K_Q` | 0.00164 | 0.00167 | 0.00588 | 0.01642 | 0.19190 |
| effective rank of `K` | 30.00 | 30.00 | 29.95 | 29.70 | 13.51 |

(Effective rank is the participation ratio `(Σλ)²/Σλ²`.) At `c = 1` the Gram matrix is
numerically the identity — 30 of 30, no structure to learn from. At `c = 0.02` it has real
off-diagonal mass and the effective rank halves, which is what generalization requires. The cost
is expressivity: small `c` shrinks the accessible Fourier frequencies (09/01), and as `c → 0` the
kernel becomes classically trivial. Bandwidth is a dial between "concentrated and useless" and
"classical and useless", with a narrow useful region, if any.

**Projected quantum kernels.** Huang et al. (2021) avoid the global overlap by measuring only
reduced density matrices, `K_PQ(x, x') = exp(-γ Σ_{k=1}^{n} ‖ρ_k(x) - ρ_k(x')‖²_F)`, with `ρ_k`
the reduced state of qubit `k`. Each lives in a fixed 2-dimensional space, so no exponential
concentration occurs. Measured at `γ = 1` on 20 uniformly random points per size:

| `n` | 2 | 4 | 6 | 8 | 10 |
|-----|---|---|---|---|----|
| mean off-diag fidelity kernel | 0.27714 | 0.06859 | 0.01714 | 0.00534 | 0.00275 |
| mean off-diag projected kernel | 0.26455 | 0.50472 | 0.57216 | 0.79194 | 0.73680 |

The fidelity kernel decays by two orders of magnitude while the projected kernel stays `O(1)`.
The trade-off: `K_PQ` depends only on 1-body marginals, exactly the quantities classical shadows
estimate efficiently, so it sits much closer to the classically simulable regime.

---

## Dequantization and Classical Shadows

Three lines of work erode quantum kernel claims from the classical side. **Dequantization**:
Tang's 2019 recommendation-systems algorithm and its successors showed that several
"exponentially faster" quantum linear-algebra routines beat only classical algorithms *denied the
same input access model*; given `ℓ²`-norm sample-and-query access — the classical analogue of the
state-preparation assumption — classical algorithms match them up to polynomial factors. Any
speedup resting on loading a classical dataset into amplitudes should be assumed dequantizable
until proven otherwise (09/04).

**Classical shadows.** Huang, Kueng and Preskill (2020) showed `O(log(N)/ε²)` randomized
measurements suffice to predict `N` low-weight observables, so any kernel built from few-body
observables — the projected kernel included — is estimable from a modest shadow with no circuit
at prediction time. The kernels resisting shadow estimation are exactly the concentrated ones.

**Trainability versus simulability.** Cerezo et al. (2023) observe that the structures used to
*prove* absence of barren plateaus (small dynamical Lie algebras, shallow depth, local
observables) are often the same ones that make a circuit classically simulable. If that pattern
is general, the trainable and the classically-hard regions may not overlap — an open question,
and the sharpest statement of the field's difficulty.

---

## Key Formulas

- **Kernel expansion**: `f(x) = sign(Σ_m α_m k(x_m, x) + b)`; **ridge**: `α = (K + λI)^{-1} y`
- **Fidelity quantum kernel**: `K_Q(x,x') = |⟨φ(x)|φ(x')⟩|² = Tr[ρ(x)ρ(x')]`
- **Compute–uncompute estimator**: `K̂ = N_{0…0}/S`, unbiased, `Var = K(1-K)/S`
- **Shots per entry for precision `ε`**: `S ≈ K(1-K)/ε² ≤ 1/(4ε²)`
- **Gram matrix cost**: `M(M-1)/2` entries for training, `M·M_test` for prediction
- **Geometric difference**: `g(K_C, K_Q) = ‖√K_Q K_C^{-1} √K_Q‖_∞^{1/2}`
- **Concentration**: `Var[K_Q] ∈ O(2^{-n})`; relative-`δ` estimation needs `S ≈ 1/(δ² K)`
- **Projected kernel**: `K_PQ(x,x') = exp(-γ Σ_k ‖ρ_k(x) - ρ_k(x')‖²_F)`

---

## Worked Example: A Real Kernel Matrix and a Real Classifier

**Step 1 — the Gram matrix.** Four points with `zz_feature_map(2, reps=2)`:

```
import numpy as np
from qiskit.circuit.library import zz_feature_map
from qiskit.quantum_info import Statevector

fm = zz_feature_map(feature_dimension=2, reps=2)

def gram(A, B=None):
    sa = [Statevector(fm.assign_parameters(list(x))) for x in A]
    sb = sa if B is None else [Statevector(fm.assign_parameters(list(x)))
                               for x in B]
    return np.array([[abs(a.inner(b))**2 for b in sb] for a in sa])

K = gram(np.array([[0.20, 0.40], [0.60, 0.80], [2.40, 2.00], [2.80, 2.60]]))
print(np.round(K, 4)); print(np.round(np.linalg.eigvalsh(K), 4))
```

Output:

```
[[1.     0.2858 0.4777 0.0164]
 [0.2858 1.     0.9138 0.4778]
 [0.4777 0.9138 1.     0.2687]
 [0.0164 0.4778 0.2687 1.    ]]
[0.0433 0.5868 1.0264 2.3434]
```

Sanity checks pass: symmetric, unit diagonal, all eigenvalues positive (PSD), trace `= 4 = M`.
The entry `K_{01} = 0.2858` was independently reproduced by an explicit NumPy product of the
`4 × 4` matrices of `H^{⊗2}`, the two `P(2x_i)` phases and `CX–P(2(π-x₀)(π-x₁))–CX`, agreeing to
`10^{-16}`.
Notice `K_{12} = 0.9138`: points 1 and 2 are far apart in input space yet nearly identical in
feature space. The ZZ geometry has little to do with Euclidean geometry — the source of both its
potential and its unreliability.

**Step 2 — classification.** Labels come from a random observable in the feature space,
Havlíček style: `V = random_unitary(4, seed=11)`, `O = V†(Z⊗Z)V`, label `sign⟨φ(x)|O|φ(x)⟩`,
discarding points with `|⟨O⟩| ≤ 0.25`. Ten training and ten test points per class, kernel ridge
regression at `λ = 10^{-2}` via `np.sign(Kte @ np.linalg.solve(Ktr + lam*np.eye(20), y))`:

```
quantum kernel: train 1.00  test 0.95     RBF gamma=1.00: train 1.00  test 0.60
RBF gamma=0.25: train 0.95  test 0.55     RBF gamma=2.00: train 1.00  test 0.65
RBF gamma=0.50: train 1.00  test 0.60
```

**Step 3 — honest labels.** Replace the feature-map-generated labels with the ordinary XOR-like
pattern `y = sign(sin x₀ · sin x₁)` and rerun:

```
quantum kernel test acc 0.57              RBF gamma=0.50 test acc 0.80
RBF gamma=0.25 test acc 0.82              RBF gamma=1.00 test acc 0.80
```

The ranking inverts completely. The quantum kernel is not "better", it is *different*, and it
wins exactly when the labels come from its own geometry. Reporting only step 2 would be a
textbook case of the benchmarking failure catalogued in 09/04.

**Step 4 — the shot bill.** All of the above used exact statevectors. Re-running step 2 with
each Gram entry estimated from `S` shots (binomial resampling, 40 repeats):

| shots per entry | exact | `10²` | `10³` | `10⁴` | `10⁵` |
|-----------------|-------|-------|-------|-------|-------|
| test accuracy | 0.950 | 0.647 ± 0.116 | 0.732 ± 0.163 | 0.844 ± 0.132 | 0.943 ± 0.018 |

Recovering the exact-kernel accuracy takes `10⁵` shots per entry — `1.9 × 10⁷` shots for a
20-point toy problem on two qubits with no hardware noise. A quantum-kernel result quoted without
its shot budget is incomplete.

---

## Summary

- A quantum feature map induces the valid Mercer kernel `K_Q(x,x') = |⟨φ(x)|φ(x')⟩|²`, which
  drops into classical SVM or kernel-ridge machinery unchanged.
- The compute–uncompute circuit gives an unbiased estimator with variance `K(1-K)/S`; measured
  spreads match that prediction to within 10%. Gram matrices cost `M(M-1)/2` entries at thousands
  of shots each — 5.8 days of hardware for `M = 1000` at `10⁴` shots/s.
- Fidelity kernels **concentrate exponentially**: the mean off-diagonal entry tracks `2^{-n}`,
  driving the Gram matrix to the identity and generalization to chance.
- **Bandwidth tuning** and **projected kernels** each defeat concentration, but by moving the
  model toward the classically simulable regime.
- Advantage needs a hard-to-simulate kernel matched to the labels that no classical kernel
  matches; `g(K_C, K_Q)` tests the last condition from unlabelled data. The one rigorous
  separation (Liu et al. 2021) is real and has no natural dataset.

---

## Exercises

**1.** Verify that the `4 × 4` Gram matrix above is a valid kernel matrix, then compute the kernel
ridge solution `α` for labels `y = (+1, +1, -1, -1)` at `λ = 10^{-2}` and check that the fitted
values have the right signs.

<details><summary>Solution</summary>

Validity: symmetric, unit diagonal (since `K(x,x) = ⟨φ|φ⟩² = 1`), eigenvalues
`(0.0433, 0.5868, 1.0264, 2.3434)` all positive, hence PSD. Solving `(K + 0.01 I)α = y` gives
`α = (5.1335, 21.6603, -21.5273, -5.5932)` and fitted values
`Kα = (0.9487, 0.7834, -0.7847, -0.9441)`; all four signs match `y`, so the training set is
separated. The coefficient magnitudes near 22 are a warning: the smallest eigenvalue is `0.0433`,
so `K` is nearly singular and `α` is dominated by that eigendirection — the one most sensitive to
shot noise. At
`λ = 10^{-1}` they drop to `(2.32, 7.97, -7.93, -2.47)` with fit `(0.77, 0.20, -0.21, -0.75)` —
still correct, visibly regularized. Small eigenvalues are the finite-`n` shadow of the
concentration that drives `K → I`.

</details>

**2.** You want every Gram entry accurate to `ε = 5 × 10^{-3}` for a 400-point training set: how
many shots per entry, how many total, and how long at `10⁴` shots per second? Then show that the
angle-encoding kernel `∏_i cos²((x_i - x'_i)/2)` from 09/01 cannot give an advantage, and say why
"the quantum kernel beat RBF on my dataset" is not by itself evidence of anything quantum.

<details><summary>Solution</summary>

Worst case `K = 1/2`, so `S ≥ 1/(4ε²) = 10⁴` shots per entry; `400 × 399/2 = 79 800` entries give
`7.98 × 10⁸` shots, `≈ 22.2 hours` at `10⁴` shots/s, excluding compilation, queueing and
calibration — and that is for *one* Gram matrix, so a hyperparameter sweep multiplies it.

The angle kernel has a closed form evaluable in `O(d)` classical arithmetic, so requirement 1
(hardness) fails outright: NumPy computes it exactly, faster, without shot noise. It is still a
perfectly good kernel and beats an RBF whenever the data is periodic per feature rather than
radial — a statement about inductive bias, not about quantum mechanics. Beating one classical
kernel shows only that that kernel was badly matched; the meaningful comparison is against the
best classical kernel found with equal tuning effort, plus a `g(K_C, K_Q)` check.

</details>

**3.** Using the concentration table, estimate the mean off-diagonal kernel value and the shots
needed for 10% relative precision at `n = 20` and `n = 30`. Comment on the feasibility of a
50-qubit fidelity-kernel experiment.

<details><summary>Solution</summary>

The measured mean tracks `≈ 2^{-n}` (slightly above, as `zz_feature_map` is not a full 2-design),
giving `K ≈ 9.5 × 10^{-7}` at `n = 20` and `9.3 × 10^{-10}` at `n = 30`. For 10% relative
precision, `S ≈ (1-K)/(0.01K) ≈ 100·2ⁿ`: `1.05 × 10⁸` shots at `n = 20`, `1.07 × 10¹¹` at
`n = 30` — 2.9 hours and 124 days per entry at `10⁴` shots/s. At `n = 50` it is `1.1 × 10¹⁷`
shots per entry, 360 000 years. A 50-qubit fidelity-kernel experiment can produce numbers, but
they are indistinguishable from an identity Gram matrix plus shot noise.

</details>

**4.** The projected kernel is stated with `ρ_k` the 1-qubit reduced density matrices. Show that
`‖ρ_k(x) - ρ_k(x')‖²_F` can be written in terms of Bloch vectors, and explain why this makes
`K_PQ` an easier target for classical shadows.

<details><summary>Solution</summary>

Write `ρ_k = (I + r_k · σ)/2` with Bloch vector `r_k ∈ ℝ³`, `|r_k| ≤ 1`. Then
`ρ_k(x) - ρ_k(x') = (Δr_k · σ)/2` with `Δr_k = r_k(x) - r_k(x')`, and since
`Tr[(a·σ)(b·σ)] = 2 a·b`,

```
‖ρ_k(x) - ρ_k(x')‖²_F = Tr[((Δr_k·σ)/2)²] = |Δr_k|²/2
```

so `K_PQ(x,x') = exp(-γ Σ_k |Δr_k|²/2)`. The kernel depends on the state only through `3n` real
numbers, the single-qubit Pauli expectations `⟨X_k⟩, ⟨Y_k⟩, ⟨Z_k⟩`, and classical shadows
estimate all of them to additive `ε` from `O(log(n)/ε²)` randomized measurements regardless of
circuit depth. Once the shadow is collected the whole projected Gram matrix is computed
classically — the `M(M-1)/2` pairwise circuit executions disappear. That is a large practical win
and simultaneously the reason the projected kernel is a weak advantage candidate: a quantity
estimable from `O(log n)` measurements is not doing much a classical learner cannot access.

</details>

---

## Further Reading

1. **Havlíček, V. et al.** — "Supervised learning with quantum-enhanced feature spaces," *Nature*
   567, 209–212 (2019). The quantum kernel estimation protocol and the ad-hoc dataset reproduced
   above.
2. **Schuld, M. and Killoran, N.** — "Quantum machine learning in feature Hilbert spaces,"
   *Phys. Rev. Lett.* 122, 040504 (2019). Establishes that variational QML models are kernel
   methods in disguise.
3. **Huang, H.-Y. et al.** — "Power of data in quantum machine learning," *Nature Communications*
   12, 2631 (2021). The geometric difference `g`, projected quantum kernels, and the
   prediction-advantage framework.
4. **Thanasilp, S., Wang, S., Cerezo, M. and Holmes, Z.** — "Exponential concentration in quantum
   kernel methods," *Nature Communications* 15, 5200 (2024). The concentration theorem behind the
   `2^{-n}` table.
5. **Liu, Y., Arunachalam, S. and Temme, K.** — "A rigorous and robust quantum speed-up in
   supervised machine learning," *Nature Physics* 17, 1013–1017 (2021). The discrete-logarithm
   separation: the one unconditional-modulo-DLP advantage result.
