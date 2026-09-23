# QML in Practice: Claims, Evidence and Benchmarks

> **Prerequisites**: Data encoding (09/01), quantum kernels (09/02), variational classifiers
> (09/03), barren plateaus (06/05)
> **Connects to**: Quantum complexity theory (08/01), HHL and state preparation (04/07),
> benchmarking and characterization (07/04), many-body simulation (08/03)

---

## Overview

The previous three chapters built quantum machine learning models and ran them. This one asks
what the field has actually established, and it is a short list. There is no demonstrated quantum
advantage on any natural classical dataset. Several headline speedups have been dequantized. The
most careful head-to-head benchmark published to date found that ordinary classical baselines
match or beat every quantum model tested.

None of that makes QML worthless, and the chapter is not a dismissal. The genuine results are
real and they are elsewhere: in learning from *quantum* data, where exponential separations are
proven and demonstrated; in simulating physical systems, where the quantum computer's advantage
comes from the physics rather than from the statistics; and in the negative results themselves,
which are sharp enough to tell you what not to try. The goal here is to give you the accounting
tools to audit a claim — your own or someone else's — before it costs a month of hardware time.

---

## What Has and Has Not Been Established

| Claim | Status |
|-------|--------|
| Quantum kernels are valid kernels and slot into classical SVM machinery | **Established** (09/02) |
| Parameter-shift gradients are exact for VQC training | **Established** (06/03, 09/03) |
| A learning problem exists with a provable quantum kernel advantage | **Established**, conditional on the hardness of discrete logarithm (Liu et al., 2021) |
| Exponential advantage exists for learning from *quantum* data | **Established and demonstrated** (Huang et al., 2022) |
| Quantum models generalize from few samples | **Bounded**, `O(√(T log T / M))`, numerically weak (Caro et al., 2022) |
| Quantum advantage on a natural classical dataset | **Not demonstrated** |
| Quantum advantage on any classical dataset at all | **Not demonstrated** outside constructed problems |
| Amplitude-encoded QML speedups survive an honest input model | **Refuted in general** by dequantization |
| Deep entangling feature maps are trainable at scale | **Refuted**: `Var ∝ 2^{-n}` (09/03) |

The distance between rows 1–4 and rows 6–7 is the distance between "the mathematics works" and
"this beats a laptop."

---

## Failure Mode 1: The Data-Loading Bottleneck

Every exponential-speedup story for classical data starts by assuming the data is already in
amplitudes. Measured on qiskit 2.5.2, generic amplitude encoding of a `d`-dimensional vector
costs `2ⁿ - n - 1 ≈ d` CNOTs at depth `2^{n+1} - 2n - 1 ≈ 2d` (09/01). Loading a 4096-feature
vector is 4083 two-qubit gates, *per data point, per shot*.

The standard escape is **QRAM**: a hypothetical device that returns
`Σ_k α_k|k⟩|x_k⟩` in `O(log d)` time. No scalable QRAM exists, and the proposals require `O(d)`
physical components with error rates that must fall as the address space grows. Treating QRAM as
free is the single most common way a QML speedup is manufactured. The rule of thumb: **if the
algorithm's advantage disappears when state preparation is charged at `Θ(d)`, there is no
advantage.**

---

## Failure Mode 2: Dequantization

Tang (2019) showed that the exponentially faster quantum recommendation-systems algorithm was
only faster than classical algorithms denied the same input model. Given `ℓ²`-norm
sample-and-query access to the data — the honest classical analogue of "the state is already
prepared" — a classical algorithm matches it up to polynomial factors. The same technique has
since dequantized quantum PCA, quantum supervised clustering, low-rank linear systems and
low-rank semidefinite programming.

Cotler, Huang and McClean (2021) sharpened the framing: the question is never "quantum versus
classical" but "quantum with access model A versus classical with access model B", and most
claimed separations come from mismatched `A` and `B`. Their conclusion, which is the practical
takeaway for this chapter: for learning tasks on *classical* data with comparable access, the
achievable speedup is generally polynomial, not exponential.

Dequantization does not touch problems where the input is itself a quantum state, which is why
the surviving positive results all live there.

---

## Failure Mode 3: Concentration and the Shot Wall

The fidelity kernel's off-diagonal entries decay like `2^{-n}` (09/02), and the gradient variance
of a VQC with an entangling encoding decays like `2^{-0.99n}` (09/03). Both force the shot budget
up exponentially. Combining the measured concentration with the binomial shot requirement:

| `n` | typical `K_off ≈ 2^{-n}` | shots for 10% relative precision | time per entry at `10⁴` shots/s |
|-----|---------------------------|----------------------------------|----------------------------------|
| 10 | `9.8 × 10^{-4}` | `1.0 × 10⁵` | 10 s |
| 20 | `9.5 × 10^{-7}` | `1.0 × 10⁸` | 2.9 hours |
| 30 | `9.3 × 10^{-10}` | `1.1 × 10¹¹` | 124 days |
| 40 | `9.1 × 10^{-13}` | `1.1 × 10¹⁴` | 348 years |

This is *before* hardware noise, which adds its own exponential suppression with depth (06/05).
The practical consequence is that any experiment above roughly 20 qubits with an expressive
encoding is measuring shot noise, and the reported Gram matrix is an identity matrix with a
fitted haze on top. The tell is easy to check: report the mean and maximum off-diagonal kernel
value. If the mean is within a few standard errors of zero, the model has learned nothing.

---

## Failure Mode 4: Benchmarks That Do Not Measure What They Claim

Bowles, Ahmed and Schuld (2024) benchmarked twelve QML models — variational classifiers, quantum
kernels, quantum neural networks, re-uploading models — across a suite of small classification
datasets, with a serious effort at fair hyperparameter tuning on both sides. Out-of-the-box
classical baselines matched or beat the quantum models essentially everywhere, and a substantial
part of the apparent quantum performance was traceable to the classical components of the
pipelines (preprocessing, the classical optimizer, the final linear layer).

A checklist for reading, or writing, a QML benchmark:

1. **Is the dataset natural?** Labels generated by the feature map, or by a random quantum
   circuit, guarantee the quantum model wins and say nothing (09/02, step 2 versus step 3).
2. **Was the classical baseline tuned?** An untuned RBF SVM is not a baseline. Compare against
   the best classical model found with equal effort, including gradient boosting and a small
   neural network.
3. **Is the shot budget reported?** Exact-statevector results are simulations of a machine that
   does not exist. The worked example in 09/02 loses 30 accuracy points at `10²` shots per entry.
4. **Is the dataset large enough to distinguish anything?** With 20 test points, the standard
   error on an accuracy of 0.85 is `√(0.85 × 0.15/20) = 0.08`. Differences below about 15 points
   are noise.
5. **Was the quantum model's classical part ablated?** Replace the circuit with a random feature
   map of the same output dimension and re-run. If accuracy barely moves, the circuit is not
   doing the work.
6. **Does the comparison scale?** A result at `n = 4` that requires `2ⁿ` shots at `n = 20` is a
   result about `n = 4`.
7. **Is the geometric difference reported?** `g(K_C, K_Q) = O(1)` rules out advantage from
   unlabelled data alone — though, as the worked example shows, large `g` proves nothing.

---

## Where the Real Results Are

### Learning from Quantum Data

The strongest positive result in the field concerns tasks whose *input* is a quantum state.
Huang et al. (2022) proved that for several natural learning problems — predicting observables of
an unknown state, distinguishing physical processes, learning the eigenvalue structure of a
channel — an agent with a quantum memory that can store and jointly measure multiple copies
needs `O(1)` experiments where an agent restricted to single-copy measurements needs `Ω(2ⁿ)`.
This is an unconditional, exponential separation, and it was demonstrated on a superconducting
processor with up to 40 qubits.

Nothing in that result involves classical data, state preparation or QRAM: the quantum state is
the input, so there is no loading cost to pay and nothing to dequantize. That is not a
coincidence. Every robust QML advantage known has this shape.

### Learning Physical Systems

The related practical direction is using QML machinery on physics problems where quantum
simulation is already the right tool: learning ground-state properties across a phase diagram,
classifying phases of matter from measurement data, and learning compact representations of
Hamiltonians (08/03). Huang et al. (2022, *Science* 377) proved that classical ML algorithms
trained on data from quantum experiments can predict ground-state properties of gapped
Hamiltonians with provably efficient sample complexity — a positive result for *classical* ML on
quantum data, which is a useful reminder of where the value actually sits.

### Negative Results as Results

The barren-plateau, concentration and dequantization theorems are the field's most reliable
output. They are also actionable: they say to use shallow circuits with structure, local
observables, and encodings matched to the problem's symmetry; to measure concentration before
scaling up; and to charge honestly for state preparation. Geometric quantum machine learning —
building equivariance under the problem's symmetry group into the ansatz — is the main
constructive line to come out of them.

---

## Key Formulas

- **Encoding cost (measured)**: `CNOT = 2ⁿ - n - 1`, `depth = 2^{n+1} - 2n - 1` per data point
- **Gram matrix cost**: `M(M-1)/2 · S` shots for training, `M · M_test · S` for prediction
- **VQC gradient cost**: `2 · P · M · S` shots per optimizer step
- **Relative-precision shots under concentration**: `S ≈ (1-K)/(δ² K) ≈ 2ⁿ/δ²`
- **Accuracy standard error**: `SE = √(p(1-p)/M_test)` — the resolution of any reported accuracy
- **Geometric difference**: `g(K_C, K_Q) = ‖√K_Q K_C^{-1} √K_Q‖_∞^{1/2}`; `g = O(1)` rules out
  advantage, large `g` does not establish it
- **Generalization bound**: `|L_test - L_train| ∈ O(√(T log T / M))`

---

## Worked Example: Auditing a Proposed Experiment

**The proposal.** "Run a quantum support vector machine with a 20-qubit ZZ feature map on 1 000
training samples of a 20-feature classical dataset, on hardware, and compare against RBF-SVM."

**Step 1 — geometric difference.** The pre-flight check needs only the inputs. On the 2-qubit
datasets of 09/02, computed against RBF at three bandwidths:

```
ad-hoc inputs   g_CQ vs RBF: {0.25: 22.57, 0.5: 7.76, 1.0: 3.43}
XOR inputs      g_CQ vs RBF: {0.25: 26.57, 0.5: 7.07, 1.0: 3.19}
```

Both datasets have large `g`, so neither is ruled out. But the quantum kernel scores 0.95 on the
first and 0.57 on the second. `g` depends only on the inputs, and both sets of inputs are
uniform on the same square — the labels are what differ, and `g` cannot see them. **Large `g` is
necessary, not sufficient.** The check is worth running because a small `g` would have killed the
proposal for free; a large one licenses nothing.

**Step 2 — concentration.** At `n = 20` the expected off-diagonal kernel value is `≈ 2^{-20}`,
about `10^{-6}`. Ten per cent relative precision needs `≈ 10⁸` shots per matrix entry. The Gram
matrix has `1000 × 999/2 = 499 500` entries, for `5 × 10¹³` shots. At `10⁴` shots/s that is
`5 × 10⁹` seconds, or **158 years** — about `3 × 10⁴` times a 48-hour allocation. This is the
number that should be computed first.

**Step 3 — what the experiment would actually produce.** Suppose it runs anyway at a realistic
`10⁴` shots per entry (5.8 days of hardware, still optimistic). The estimator's standard error is
`√(K(1-K)/S) ≈ √(10^{-6}/10⁴) = 10^{-5}`, ten times the signal itself. Every off-diagonal entry
comes back as noise around zero, so `K ≈ I`, kernel ridge regression returns
`α = y/(1 + λ)`, and every test prediction is a weighted sum of `≈ 0` — chance accuracy, plus
whatever the classical preprocessing contributes.

**Step 4 — the accuracy resolution.** Even with a working kernel, a 200-point test set resolves
accuracy to `SE = √(0.8 × 0.2/200) = 0.028`. A quantum-versus-classical difference below about
6 points is not measurable on that test set, and the proposal did not specify one large enough
to support the comparison it wants to make.

**Step 5 — the redesign.** The audit points at a different experiment: drop to `n = 8`–`10`
qubits where the kernel has measurable off-diagonal mass; apply bandwidth rescaling and report
the mean off-diagonal value as a diagnostic; use a projected kernel, whose entries stay `O(1)`
(09/02); budget `10⁴`–`10⁵` shots per entry against `M ≈ 100`, which is `5 × 10⁷`–`5 × 10⁸`
shots, 1.4 to 14 hours; and tune the classical baseline as hard as the quantum model. That is a
publishable experiment. It will probably show the classical baseline winning, which is also a
result, and one worth a day of hardware rather than 158 years.

---

## Summary

- **No quantum advantage has been demonstrated on any natural classical dataset.** The claim is
  not that it is impossible, only that it has not happened.
- **Data loading** costs `Θ(d)` gates without QRAM, and QRAM does not exist at scale. If the
  advantage vanishes when state preparation is charged honestly, there is no advantage.
- **Dequantization** removed the exponential speedup from recommendation systems, quantum PCA,
  low-rank linear systems and more, by giving the classical algorithm a comparable input model.
- **Concentration** drives kernel entries and gradients to `2^{-n}`, so shot budgets grow
  exponentially: `10⁸` shots per kernel entry at 20 qubits, `10¹⁴` at 40.
- The most careful public benchmark (Bowles et al., 2024) found classical baselines matching or
  beating twelve quantum models, with much of the quantum performance attributable to classical
  pipeline components.
- **The real results concern quantum data**: an unconditional exponential separation for learning
  from experiments, proven and demonstrated on up to 40 qubits, where there is no loading cost to
  pay and nothing to dequantize.
- Audit any proposal with four numbers: state-preparation cost, expected kernel or gradient
  magnitude, total shots, and the standard error of the accuracy being compared.

---

## Exercises

**1.** A paper reports that a 12-qubit quantum kernel SVM achieves 0.78 test accuracy against an
RBF-SVM's 0.74 on a 150-point test set, using `2 × 10³` shots per Gram entry. Give three
quantitative objections.

<details><summary>Solution</summary>

(i) *Resolution.* `SE = √(0.78 × 0.22/150) = 0.034`, so the 0.04 gap is 1.2 standard errors —
consistent with noise. Distinguishing 0.78 from 0.74 at two standard errors needs
`M_test ≳ 0.78 × 0.22/0.02² = 429` points.
(ii) *Concentration.* At `n = 12` the measured mean off-diagonal kernel value is `7.6 × 10^{-4}`
(09/02). With `S = 2 × 10³` the estimator's standard error is `√(K/S) ≈ 6 × 10^{-4}`, comparable
to the signal, so the reported Gram matrix is dominated by shot noise and is close to `I`.
(iii) *Baseline.* One RBF kernel at one bandwidth is not a classical baseline; the comparison
must include a tuned `γ`, a polynomial kernel, gradient boosting and a small MLP. Given (ii),
a fourth objection follows: the paper should report the mean and max off-diagonal kernel value,
which would show whether anything was measured at all.

</details>

**2.** A proposal amplitude-encodes 2 048 features on 11 qubits and claims an `O(polylog d)`
inference speedup. Compute the loading cost and state the condition under which the claim could
survive.

<details><summary>Solution</summary>

`n = log₂ 2048 = 11` qubits; `CNOT = 2¹¹ - 11 - 1 = 2036`; `depth = 2¹² - 22 - 1 = 4073`. So
loading is `Θ(d)`, and any `O(polylog d)` inference is dominated by it — total cost `Θ(d)`, the
same as reading the vector classically. The claim survives only if the amplitudes never have to
be loaded from classical memory: either the state is produced by a quantum process (a simulation,
a sensor, a previous quantum subroutine), or the amplitude function `k ↦ x_k` is efficiently
computable so the state can be synthesized in `polylog(d)` gates without a classical database.
A QRAM assumption does not rescue it, because QRAM at this scale does not exist and its cost
model is the thing in dispute.

</details>

**3.** Explain why the geometric difference gave `g ≈ 22.6` and `g ≈ 26.6` for two datasets on
which the quantum kernel scored 0.95 and 0.57. What would a small `g` have told you?

<details><summary>Solution</summary>

`g(K_C, K_Q)` is computed from the two Gram matrices on the *training inputs* only; no labels
enter. Both datasets draw inputs uniformly from `[0, 2π]²`, so both give essentially the same
pair of Gram matrices and therefore essentially the same `g`. The quantity measures how different
the two kernels' geometries are — whether the quantum kernel *could* express something the
classical one cannot. Whether it expresses the *right* thing depends entirely on the labels,
which is why one dataset scores 0.95 and the other 0.57.

Small `g` is the informative case: `g = O(1)` means the classical kernel can reproduce any
function the quantum kernel expresses, with comparable sample complexity, for *every* labelling.
That is a genuine no-go, obtainable from unlabelled data before any hardware time is spent.
Large `g` only means the no-go does not apply.

</details>

**4.** You have 48 hours of hardware at `5 × 10³` shots/s. Design the largest quantum-kernel
experiment that is actually measurable, stating qubit count, training-set size and shots per
entry, and justify each choice.

<details><summary>Solution</summary>

Budget: `48 × 3600 × 5 × 10³ = 8.64 × 10⁸` shots.

*Shots per entry.* The kernel entry must be resolved to a fraction of its own size. At `n` qubits
the typical off-diagonal entry is `≈ 2^{-n}`, so 10% relative precision needs `S ≈ 100 · 2ⁿ`.
*Entries.* `M(M-1)/2 ≈ M²/2`. So the constraint is `M² · 50 · 2ⁿ ≤ 8.64 × 10⁸`, i.e.
`M² ≤ 1.73 × 10⁷/2ⁿ`.

| `n` | `S = 100·2ⁿ` | max `M` |
|-----|---------------|---------|
| 8 | 25 600 | 260 |
| 10 | 102 400 | 130 |
| 12 | 409 600 | 65 |
| 16 | 6 553 600 | 16 |

Above `n ≈ 12` the training set collapses below what any learning claim can rest on. The best
design is around `n = 10`, `M = 120`, `S = 10⁵`, leaving headroom for the test Gram matrix — and
it should use bandwidth rescaling or a projected kernel to lift the off-diagonal entries, which
directly reduces the required `S` and buys back either qubits or samples. A 120-point training
set with a 200-point test set resolves accuracy to `± 0.03`, so only differences above roughly
6 points will be reportable. Every one of those constraints is fixed before any data is chosen.

</details>

---

## Further Reading

1. **Bowles, J., Ahmed, S. and Schuld, M.** — "Better than classical? The subtle art of
   benchmarking quantum machine learning models," arXiv:2403.07059 (2024). Twelve models, honest
   baselines, the field's most useful negative result.
2. **Huang, H.-Y. et al.** — "Quantum advantage in learning from experiments," *Science* 376,
   1182–1186 (2022). The unconditional exponential separation for quantum data, demonstrated on
   40 qubits.
3. **Tang, E.** — "A quantum-inspired classical algorithm for recommendation systems," *STOC '19*,
   217–228 (2019). The original dequantization result.
4. **Cotler, J., Huang, H.-Y. and McClean, J. R.** — "Revisiting dequantization and quantum
   advantage in learning tasks," arXiv:2112.00811 (2021). Access models and where separations
   really come from.
5. **Schuld, M. and Killoran, N.** — "Is quantum advantage the right goal for quantum machine
   learning?", *PRX Quantum* 3, 030101 (2022). The argument that the field should be measuring
   something other than speedups.
