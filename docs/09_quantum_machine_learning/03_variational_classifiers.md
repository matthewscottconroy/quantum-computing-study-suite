# Variational Quantum Classifiers

> **Prerequisites**: Data encoding (09/01), quantum kernels (09/02), VQE fundamentals (06/01),
> ansatz design (06/02), the parameter-shift rule (06/03), barren plateaus (06/05)
> **Connects to**: QML in practice (09/04), noise and error mitigation (06/06), QAOA (06/04)

---

## Overview

A **variational quantum classifier (VQC)** encodes a data point, runs a trainable circuit, and
reads out a label from an expectation value. It is a VQE loop with the Hamiltonian replaced by a
fixed observable and the energy replaced by a supervised loss, so most of the machinery from
Chapter 6 transfers directly: the parameter-shift rule gives exact gradients, the same ansätze
apply, and the same barren plateaus are waiting.

What is new is everything statistical. A VQE has one number to minimize; a VQC has a training
set, a test set and a gap between them, bringing in overfitting, sample complexity and the
question of whether the model's inductive bias suits the data — questions with nothing to do with
quantum mechanics that nonetheless decide whether the model is useful. It also brings a new
source of barren plateaus: the *encoding* can flatten the landscape even when the ansatz is
shallow and the observable local, precisely the regime Cerezo et al. (2021) proved safe for VQE.
This chapter trains a real VQC on qiskit 2.5.2 and reports what happens.

---

## Architecture

A VQC is three stages on `n` qubits:

```
|0⟩^{⊗n} ── U_φ(x) ── W(θ) ── measure ⟨O⟩  ──→  f(x, θ) = ⟨0|U_φ(x)† W(θ)† O W(θ) U_φ(x)|0⟩
```

- **Encoding** `U_φ(x)`: fixed, data-dependent, no trainable parameters (09/01).
- **Ansatz** `W(θ)`: trainable, data-independent — hardware-efficient layers of single-qubit
  rotations plus entanglers (`RealAmplitudes`, `EfficientSU2`) by default; see 06/02.
- **Readout** `O`: a Hermitian observable — `Z₀` (local) or `Z^{⊗n}` (global) for binary labels,
  commuting observables or the first `⌈log₂ C⌉` qubits for `C` classes.

**The kernel connection.** Schuld and Killoran (2019) observed that the model is linear in the
density matrix `ρ(x) = |φ(x)⟩⟨φ(x)|` — indeed `f(x, θ) = Tr[ρ(x) M(θ)]` with
`M(θ) = W(θ)† O W(θ)` — so any VQC is a linear model in the feature space the *encoding* fixes,
and training `θ` searches over measurements rather than over feature maps. The consequence is
sharp: the best possible VQC on an encoding cannot beat the optimal kernel machine on the same
encoding. It trades the kernel method's convexity and global optimum for `O(M)` rather than
`O(M²)` training cost.

**Data re-uploading architectures.** Interleaving encoding and ansatz blocks,
`W(θ_R) U_φ(x) … W(θ_1) U_φ(x) W(θ_0)`, breaks the clean "fixed feature map, trainable
measurement" split and is strictly more expressive (09/01), at the price that the kernel picture
no longer applies exactly — the analysis of what the model can express becomes the Fourier
argument instead.

---

## Loss Functions

The raw output is `f(x, θ) = ⟨O⟩ ∈ [-1, 1]` for a Pauli observable. Three standard ways to turn
it into a loss for labels `y ∈ {-1, +1}`:

```
Squared loss     L = (1/M) Σ_m ( f(x_m, θ) - y_m )²
Hinge loss       L = (1/M) Σ_m max(0, 1 - y_m f(x_m, θ))
Cross-entropy    L = -(1/M) Σ_m [ p_m log q_m + (1 - p_m) log(1 - q_m) ]
                 with q_m = (1 + f(x_m, θ))/2  and  p_m = (1 + y_m)/2 ∈ {0, 1}
```

Squared loss is the simplest and is used in the worked example. Its floor is not zero — a Pauli
observable on a normalized state cannot always reach `⟨O⟩ = ±1`, so a converged model plateaus at
a positive loss, here `0.19`, while classifying every training point correctly. Reading that
residual as underfitting would be a mistake.

Two practical refinements: a **trainable bias and scale** `ŷ = a·f(x,θ) + b` with `a, b`
optimized classically costs nothing quantum and usually removes a stubborn loss floor, and
**class weighting** matters more here than classically, since shot noise on `f` is symmetric
while the decision boundary need not be.

---

## Gradients

The parameter-shift rule of 06/03 applies unchanged, because the loss depends on `θ` only through
the expectation values `f(x_m, θ)`. For a parameter entering through a single Pauli rotation
`e^{-iθ_k P/2}`,

```
∂f(x, θ)/∂θ_k = [ f(x, θ + (π/2)e_k) - f(x, θ - (π/2)e_k) ] / 2
```

and for the squared loss the chain rule gives

```
∂L/∂θ_k = (2/M) Σ_m ( f(x_m, θ) - y_m ) · ∂f(x_m, θ)/∂θ_k
```

Verified on the worked example's circuit (2 qubits, `zz_feature_map(2, reps=2)` plus
`real_amplitudes(2, reps=2)`, 6 parameters): parameter-shift and central finite differences at
`h = 10^{-5}` agree to `2.0 × 10^{-11}` — the finite difference's truncation error, not the
shift rule's.

**The cost.** A full gradient needs 2 circuits per parameter per data point, so
`circuits per gradient step = 2 · P · M`. For `P = 6` parameters and `M = 20` training points
that is 240 circuits per step, 14 400 over 60 steps, and at `10⁴` shots each, `1.44 × 10⁸` shots
— four hours at `10⁴` shots/s for a two-qubit toy problem. Mini-batching cuts `M`, SPSA cuts the
`P` factor at the price of gradient variance (06/03), and both are essential at realistic sizes.

---

## Generalization

A VQC that fits its training set has proved nothing. The relevant bound:

**Theorem (Caro et al., 2022)**: for a variational model with `T` parameterized gates trained on
`M` samples, with high probability the generalization gap satisfies

```
| L_test - L_train | ∈ O( √( T log T / M ) )
```

and if only `K < T` of the gates are actually trained, `T` may be replaced by `K`.

The bound is encouraging in shape — it depends on the *gate count*, not on the Hilbert space
dimension `2ⁿ` — and weak in practice. For the worked example, `T = 6` and `M = 20` give
`√(6 ln 6 / 20) = 0.733`; since the squared loss lies in `[0, 4]` and the model's actual
train/test accuracy gap is `1.00 - 0.85 = 0.15`, the bound constrains nothing observable.
Driving it to `0.1` requires `M = T ln T / 0.01 = 1075` samples for six parameters; a
60-parameter model needs `24 566`. Since each additional sample multiplies the training shot
bill, the bound's real message is that variational models are sample-hungry in exactly the regime
where quantum circuits are expensive.

Overfitting shows up empirically well before the bound bites: in the worked example training
accuracy reaches 1.00 at step 9 while test accuracy is still 0.75, and the gap never fully closes.
Standard remedies apply — fewer layers, `L2` penalty on `θ`, early stopping on a validation split
— plus a quantum-specific one: shot noise regularizes, so a model trained at 1 000 shots per
circuit sometimes generalizes better than one trained at `10⁵`.

---

## Encoding-Induced Barren Plateaus

Chapter 06/05 established the ansatz-side story: deep random ansätze plus global observables give
`Var[∂C/∂θ] ≈ 2/4ⁿ`, and Cerezo et al. (2021) showed that a **shallow** ansatz with a **local**
observable escapes. Both conditions can hold in a VQC and the landscape can still be flat,
because the data encoding is also a circuit and it also scrambles.

The experiment below fixes the trainable ansatz at `real_amplitudes(n, reps=1)` — one layer,
maximally shallow — and fixes the observable at the local `Z₀`. The only thing that changes is
the encoding: eight layers of either (a) product rotations `R_y(w_{ri} x_i)`, or (b) the same
rotations plus a ring of CNOTs and a layer of `R_z(w_{ri} x_{i+1})`. Variance of
`∂f/∂θ_0` over 300 random `(x, θ)` pairs:

```
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import real_amplitudes
from qiskit.quantum_info import Statevector, SparsePauliOp

def var_grad(n, entangling, R=8, L=1, nsamp=300, seed=3):
    rng = np.random.default_rng(seed)
    ans = real_amplitudes(num_qubits=n, reps=L)     # shallow, fixed
    tp = list(ans.parameters)
    O = SparsePauliOp("I"*(n-1) + "Z")              # LOCAL observable
    w = rng.normal(1.0, 0.5, size=(R, n))
    g = []
    for _ in range(nsamp):
        x = rng.uniform(0, 2*np.pi, size=n)
        th = rng.uniform(-np.pi, np.pi, size=len(tp))
        e = np.zeros(len(tp)); e[0] = np.pi/2
        def f(t):
            qc = QuantumCircuit(n)
            for r in range(R):
                for i in range(n):
                    qc.ry(w[r, i]*x[i], i)
                if entangling:
                    for i in range(n):
                        qc.cx(i, (i+1) % n)
                    for i in range(n):
                        qc.rz(w[r, i]*x[(i+1) % n], i)
            qc.compose(ans.assign_parameters(dict(zip(tp, t))), inplace=True)
            return np.real(Statevector(qc).expectation_value(O))
        g.append(0.5*(f(th+e) - f(th-e)))
    return np.var(g)

for n in [2, 4, 6, 8, 10, 12]:
    vp, ve = var_grad(n, False), var_grad(n, True)
    print("n=%2d  product %.3e   entangling %.3e   ratio %7.1f"
          % (n, vp, ve, vp/ve))
```

Output:

```
n= 2  product 3.791e-01   entangling 2.016e-01   ratio     1.9
n= 4  product 3.095e-01   entangling 6.374e-02   ratio     4.9
n= 6  product 2.668e-01   entangling 1.679e-02   ratio    15.9
n= 8  product 2.725e-01   entangling 4.135e-03   ratio    65.9
n=10  product 2.465e-01   entangling 1.090e-03   ratio   226.2
n=12  product 2.512e-01   entangling 2.074e-04   ratio  1211.1
```

The product encoding holds `Var ≈ 0.25` at every size — flat, trainable, indifferent to `n`. The
entangling encoding decays by a factor of 972 between `n = 2` and `n = 12`, a fitted scaling of
`Var ∝ 2^{-0.99 n}`: textbook exponential decay, produced entirely by the *fixed, untrainable*
part of the circuit.

This matters because the usual mitigations do not apply: identity-block initialization, layerwise
training and local cost functions all act on the ansatz, and none of them touches `U_φ(x)`. The
encoding is fixed by the data-loading design, and its scrambling is what was supposed to make the
model interesting. The only levers are the encoding-side ones from 09/01 and 09/02 — fewer
repetitions, less entanglement, bandwidth rescaling `x → c·x` — each reducing expressivity in
exactly the way that makes the model more classically simulable. Extrapolating the fit, `n = 20`
gives `Var ≈ 8.4 × 10^{-7}` and `≈ 1.2 × 10⁶` shots per gradient component; `n = 30` gives
`≈ 1.2 × 10⁹`.

---

## Key Formulas

- **VQC model**: `f(x, θ) = ⟨0|U_φ(x)† W(θ)† O W(θ) U_φ(x)|0⟩ = Tr[ρ(x) M(θ)]`
- **Squared loss**: `L(θ) = (1/M) Σ_m (f(x_m, θ) - y_m)²`
- **Parameter shift**: `∂f/∂θ_k = [f(θ + (π/2)e_k) - f(θ - (π/2)e_k)]/2`
- **Loss gradient**: `∂L/∂θ_k = (2/M) Σ_m (f(x_m, θ) - y_m) ∂f(x_m, θ)/∂θ_k`
- **Gradient cost**: `2·P·M` circuit evaluations per step, `2·P·M·S` shots
- **Generalization bound**: `|L_test - L_train| ∈ O(√(T log T / M))` (Caro et al., 2022)
- **Encoding-induced plateau (measured)**: `Var[∂f/∂θ] ∝ 2^{-0.99 n}` for an entangling encoding
  with a shallow ansatz and a local observable

---

## Worked Example: Training a Two-Qubit VQC

**Setup.** Encoding `zz_feature_map(2, reps=2)`; ansatz `real_amplitudes(2, reps=2)` with 6
parameters; observable `Z⊗Z`; squared loss; Adam at learning rate `0.20`; `θ` initialized to
`0.1` in every component. Data is the ad-hoc set from 09/02 (labels from a random observable in
the feature space, boundary margin `0.25`), 10 training and 10 test points per class.

**Gradient check first.** Comparing the parameter-shift gradient with central finite differences
at a random `(x, θ)`:

```
parameter-shift grad: [-0.0298 -0.0027 -0.4256  0.2835  0.3033  0.0429]
finite-difference   : [-0.0298 -0.0027 -0.4256  0.2835  0.3033  0.0429]
max |diff| = 1.98e-11
```

**Training run** (60 Adam steps; each step costs `2 × 6 × 20 = 240` circuit evaluations):

| step | squared loss | train acc | test acc | `‖∇L‖` |
|------|--------------|-----------|----------|---------|
| 0 | 0.8344 | 0.65 | 0.70 | 0.4571 |
| 9 | 0.2674 | 1.00 | 0.75 | 0.3682 |
| 19 | 0.2160 | 0.95 | 0.80 | 0.1638 |
| 29 | 0.1986 | 1.00 | 0.80 | 0.1043 |
| 39 | 0.1942 | 1.00 | 0.85 | 0.0625 |
| 49 | 0.1926 | 1.00 | 0.80 | 0.0480 |
| 59 | 0.1916 | 1.00 | 0.85 | 0.0332 |
| 60 | 0.1915 | 1.00 | 0.85 | — |

Final parameters `θ = (-0.2592, 0.8422, -1.5834, 0.9765, 0.1704, 1.0635)`.

**Reading the run.** Four things are worth noting, and only one of them is good news.

*It trains.* The loss falls by a factor of 4.4, the gradient norm decays by 14×, and the model
separates the training set perfectly by step 9. Two qubits, six parameters, no barren plateau.

*It overfits.* Training accuracy hits 1.00 at step 9 while test accuracy is 0.75, and after 60
steps the gap is still 0.15. Everything after step 9 improved the *loss* while test accuracy
oscillated between 0.75 and 0.85 — the difference between a margin and a decision.

*The loss floor is structural.* The final loss `0.1915` is not residual error: with
`f = ⟨Z⊗Z⟩ ∈ [-1, 1]` and this ansatz, no `θ` drives every `f(x_m)` to exactly `±1`, and a
trainable output scale and bias would absorb most of it without changing one prediction.

*It loses to the kernel.* The same encoding and the same data through kernel ridge regression
(09/02) gives 0.95 test accuracy against this model's 0.85, exactly as the Schuld–Killoran
argument predicts: the VQC searches over measurements inside a feature space the kernel method
optimizes over exactly. The VQC's advantage is cost — `O(M)` circuits per training step against
the kernel's `O(M²)` up front — and at `M = 20` that trade is not worth making.

**Shot accounting.** All numbers above come from exact statevectors. On hardware at `10⁴` shots
per circuit, the 14 400 circuit evaluations become `1.44 × 10⁸` shots — four hours at `10⁴`
shots/s, for a two-qubit six-parameter model that a classical SVM fits in milliseconds.

---

## Summary

- A VQC is encoding, then trainable ansatz, then readout of `⟨O⟩`; it is a VQE loop with a
  supervised loss, so the Chapter 6 machinery transfers.
- Because `f(x, θ) = Tr[ρ(x) M(θ)]`, a VQC is a **linear model in the encoding's feature space**:
  training searches over measurements, and it cannot beat the optimal kernel machine on the same
  encoding. Its advantage over the kernel is `O(M)` versus `O(M²)` training cost.
- The **parameter-shift rule** transfers unchanged and is exact — verified to `2 × 10^{-11}`
  against finite differences. A full gradient costs `2·P·M` circuits per step.
- The **Caro et al. bound** `O(√(T log T / M))` scales with gate count rather than Hilbert-space
  dimension, but is numerically vacuous at realistic sizes: six parameters need `M ≈ 1075` for a
  bound of 0.1.
- The measured run trains cleanly (loss `0.83 → 0.19`, train accuracy 1.00) and **overfits**
  (test accuracy 0.85), and loses to the kernel method on the same encoding.
- **Encoding-induced barren plateaus** are QML-specific: with a one-layer ansatz and a local
  observable — the regime Cerezo et al. prove safe — an entangling encoding still drives
  `Var[∂f/∂θ] ∝ 2^{-0.99n}` while a product encoding holds `Var ≈ 0.25` at every size, and the
  standard ansatz-side mitigations cannot reach the encoding.

---

## Exercises

**1.** A VQC has `P = 40` parameters and is trained on `M = 500` samples for 200 optimizer steps
with `10⁴` shots per circuit. Compute the total shot count and the wall-clock time at `10⁴`
shots/s. What does mini-batching at batch size 32 change?

<details><summary>Solution</summary>

Circuits per step `= 2 P M = 2 × 40 × 500 = 40 000`; over 200 steps, `8 × 10⁶` circuits and
`8 × 10^{10}` shots — `8 × 10⁶` seconds, or **93 days** of pure execution. Mini-batching at 32
replaces `M = 500` by 32 per step, cutting circuits per step to 2 560 and the total to
`5.12 × 10⁹` shots, about **5.9 days**: a 15.6× saving, at the cost of a gradient estimate now
stochastic in the batch as well as in the shots. SPSA replaces the `2P` factor with two loss
evaluations per step — at batch 32 that is `2 × 32 = 64` circuits per step and `1.28 × 10⁸` shots
total, 3.6 hours, with a much noisier gradient (06/03).

</details>

**2.** Using the Caro et al. bound, how many training samples does a 40-parameter VQC need for a
generalization gap bound of 0.2? Of 0.05? Comment on the interaction with the shot cost from
exercise 1.

<details><summary>Solution</summary>

`M = T ln T / ε²` with `T = 40`, `ln 40 = 3.689`, so `T ln T = 147.6`. For `ε = 0.2`,
`M = 147.6/0.04 = 3 690`; for `ε = 0.05`, `M = 147.6/0.0025 = 59 023`. Since the training shot
cost is linear in `M`, tightening the bound from 0.2 to 0.05 multiplies the shot bill by 16 on
top of an already impractical figure — the full-batch 200-step run of exercise 1 at `M = 59 023`
would need `9.4 × 10^{12}` shots. It is only an upper bound: the *measured* gap in the worked
example (0.15 at `M = 20`) is far below what it predicts (0.73), so the numbers are pessimistic.
They are nevertheless the only rigorous guidance available, and they say that variational quantum
models and large training sets do not combine.

</details>

**3.** Explain why the encoding-induced barren plateau in the table above is not covered by the
Cerezo et al. (2021) shallow-ansatz/local-cost result, and why identity-block initialization does
not help.

<details><summary>Solution</summary>

Cerezo et al. bound the gradient variance of `C(θ) = ⟨0|V(θ)† O V(θ)|0⟩` in terms of the depth of
the *parameterized* circuit `V(θ)` and the locality of `O`. Their hypothesis is that `V(θ)` is
shallow; in a VQC the state reaching the ansatz is not `|0⟩` but `U_φ(x)|0⟩`, and the theorem says
nothing about how scrambled that input is. The measured run satisfies both of their conditions —
`reps=1` ansatz, observable `Z₀` — and still shows `Var ∝ 2^{-0.99n}`, because averaging over
random `x` makes `U_φ(x)|0⟩` behave like a random state, and `⟨Z₀⟩` on a random `n`-qubit state
concentrates around 0 with variance `O(2^{-n})`.

Identity-block initialization sets `W(θ_init) = I` so the circuit starts in a region of
non-vanishing gradient. That still leaves `f = ⟨φ(x)|O|φ(x)⟩`, an expectation on the scrambled
encoded state, and it is *that* quantity whose variance over the data is exponentially small.
The initialization fixes the ansatz's contribution to a problem the ansatz did not cause.

</details>

**4.** The worked example's squared loss converges to `0.1915` with every training point correctly
classified. Show that a trainable output scale and bias `ŷ = a f(x,θ) + b` can only reduce the
loss, and estimate the achievable reduction if the 20 outputs `f(x_m)` have class means `±0.55`
with within-class spread `0.1`.

<details><summary>Solution</summary>

Fixing `θ` and optimizing `(a, b)` is ordinary least squares of `y` on `f`, and `(a, b) = (1, 0)`
is in the feasible set, so the optimum is at most the current loss — the reduction is never
negative. With class means `±0.55` and within-class standard deviation `0.1`, the best affine map
sends `±0.55 ↦ ±1`, i.e. `a = 1/0.55 = 1.818`, `b = 0`. The residual is then the amplified
within-class spread, `a × 0.1 = 0.182`, giving `L ≈ 0.182² = 0.033` versus the current
`(1 - 0.55)² + 0.1² ≈ 0.213`. So roughly a 6× loss reduction with zero additional quantum cost
and zero change in predictions, since `a > 0` preserves every sign. This is why a reported VQC
loss, unlike a VQE energy, carries almost no information on its own.

</details>

**5.** Given the measured scaling `Var[∂f/∂θ] ≈ 0.2016 × 2^{-0.992(n-2)}` for the entangling
encoding, find the largest `n` at which one gradient component can be resolved at signal-to-noise
1 within a `10⁸`-shot budget. How does the answer change for the product encoding?

<details><summary>Solution</summary>

Resolving a gradient of standard deviation `σ = √Var` needs `S ≈ 1/Var` shots (06/03). Setting
`1/Var = 10⁸` gives `Var = 10^{-8}`, so `2^{-0.992(n-2)} = 10^{-8}/0.2016 = 4.96 × 10^{-8}`, and
`0.992(n-2) = log₂(2.02 × 10⁷) = 24.3`, giving `n - 2 = 24.5` and **`n ≈ 26`** qubits. Checking
against the extrapolation: at `n = 20`, `Var ≈ 8.4 × 10^{-7}` needs `1.2 × 10⁶` shots; at
`n = 30`, `Var ≈ 8.7 × 10^{-10}` needs `1.2 × 10⁹`. And this is *per gradient component, per data
point, per optimizer step* — a 40-parameter model on 500 samples at `n = 26` would need
`4 × 10^{12}` shots for one step.

For the product encoding `Var ≈ 0.25` independent of `n`, so `S ≈ 4` shots per component suffices
at any size and the budget never binds. The catch is 09/01: a product encoding has a closed-form
classical kernel, so the trainable model is a laborious way to fit a function a laptop fits
directly. Trainability and hardness trade off here just as they do for kernels (09/02).

</details>

---

## Further Reading

1. **Schuld, M. and Killoran, N.** — "Quantum machine learning in feature Hilbert spaces,"
   *Phys. Rev. Lett.* 122, 040504 (2019). The proof that variational classifiers are linear models
   in the encoding's feature space.
2. **Caro, M. C. et al.** — "Generalization in quantum machine learning from few training data,"
   *Nature Communications* 13, 4919 (2022). The `√(T log T / M)` bound used above.
3. **Cerezo, M. et al.** — "Cost function dependent barren plateaus in shallow parametrized
   quantum circuits," *Nature Communications* 12, 1791 (2021). The shallow-ansatz/local-cost
   escape whose hypotheses the encoding experiment violates.
4. **Thanasilp, S., Wang, S., Nghiem, N. A., Coles, P. J. and Cerezo, M.** — "Subtleties in the
   trainability of quantum machine learning models," *Quantum Machine Intelligence* 5, 21 (2023).
   Encoding-induced flat landscapes and the limits of the standard mitigations.
5. **Bowles, J., Ahmed, S. and Schuld, M.** — "Better than classical? The subtle art of
   benchmarking quantum machine learning models," arXiv:2403.07059 (2024). Twelve QML models,
   including VQCs, benchmarked honestly against classical baselines.
