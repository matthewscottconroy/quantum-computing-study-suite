# The Parameter-Shift Rule and Quantum Gradients

> **Prerequisites**: Calculus (derivatives), VQE fundamentals (06/01), parameterized quantum
> circuits (Chapter 3)
> **Connects to**: Barren plateaus (06/05), quantum optimal control (06/07), ansatz training

---

## Overview

Optimizing a variational quantum algorithm requires computing or estimating gradients of the
cost function with respect to circuit parameters. Unlike classical neural networks where
backpropagation computes exact gradients analytically, quantum circuits present a challenge:
the quantum state is not directly accessible, and classical differentiation cannot be applied
naively.

The **parameter-shift rule** (Mitarai et al., 2018; Schuld et al., 2019) provides an exact
analytical gradient formula for parameterized quantum circuits that requires only two forward
circuit evaluations per parameter. This makes gradient-based optimization of quantum circuits
feasible without approximation, and is now the standard method for variational quantum algorithms.

Beyond the basic parameter-shift rule, this chapter covers the quantum natural gradient (which
uses the Fisher information metric to correct for parameter space curvature), second-order
methods, and the practical implications of shot noise on gradient estimates.

---

## Setup: Parameterized Quantum Gates

### Pauli Rotation Gates

The most common parameterized gate in quantum algorithms is the **Pauli rotation**:

```
Rₚ(θ) = exp(-i θ P/2)   where P ∈ {X, Y, Z}
```

In matrix form:
```
Rz(θ) = [[e^{-iθ/2}, 0       ],
          [0,         e^{iθ/2}]]
```

The generator `P/2` has spectrum `{-1/2, +1/2}`.

More generally, for a generator `G` with two eigenvalues `±r` (and `r > 0`):
```
U(θ) = exp(-i θ G)
```

Most standard gates fit this pattern with `r = 1/2` or `r = 1`.

### Cost Function Structure

The cost function for a parameterized circuit:
```
f(θ) = ⟨ψ₀| U(θ)† O U(θ) |ψ₀⟩
```

where `O` is an observable (Hermitian operator), and the parameterized circuit
`U(θ) = U(θ₁, ..., θₘ)` depends on `m` scalar parameters.

Often we focus on the gradient with respect to a single parameter `θᵢ` while all others
are held fixed:
```
∂f/∂θᵢ = ⟨ψ₀| U† (∂U/∂θᵢ)† O U + U† O (∂U/∂θᵢ) |ψ₀⟩
```

---

## The Parameter-Shift Rule

### Derivation for Pauli Rotations

Consider a circuit where the `i`-th parameter `θ` enters only through a single gate
`Rₚ(θ) = exp(-iθP/2)`. The cost function is:

```
f(θ) = ⟨ψ(θ)|O|ψ(θ)⟩
```

Absorb the gates after `Rₚ` into an effective observable `A = U_after† O U_after` and the
gates before it into the input state `|φ⟩ = U_before|ψ₀⟩`, so
`f(θ) = ⟨φ|Rₚ(θ)† A Rₚ(θ)|φ⟩`. Using `Rₚ'(θ) = -i(P/2)Rₚ(θ)`:

```
∂f/∂θ = (i/2) ⟨φ| Rₚ(θ)† [P, A] Rₚ(θ) |φ⟩
```

The key algebraic identity (using `Rₚ(±π/2) = (I ∓ iP)/√2` and `P² = I`) is:

```
Rₚ(π/2)† A Rₚ(π/2) - Rₚ(-π/2)† A Rₚ(-π/2) = i[P, A]
```

(Expand: `(I+iP)A(I-iP)/2 - (I-iP)A(I+iP)/2 = i(PA - AP)`.) Substituting `[P, A]` back, and
using `Rₚ(θ)Rₚ(±π/2) = Rₚ(θ ± π/2)`:

```
∂f/∂θ = [f(θ + π/2) - f(θ - π/2)] / 2
```

**This is the parameter-shift rule**: the exact partial derivative equals the difference of
two circuit evaluations with shifted parameters, divided by 2.

### Formal Statement

**Theorem (Mitarai et al., 2018; Schuld et al., 2019)**: For a parameterized quantum circuit
`U(θ) = ... Rₚ(θ) ...` where `Rₚ(θ) = exp(-iθP/2)` and `P² = I`:

```
∂f/∂θ = [f(θ + π/2) - f(θ - π/2)] / 2
```

This is an **exact** gradient (not an approximation) and requires exactly 2 circuit evaluations
per parameter.

### Proof via Generator Spectrum

For a gate `U(θ) = exp(-iθG)` where the generator `G` has eigenvalues `±r` (and no others):

```
∂f/∂θ = r · [f(θ + π/(4r)) - f(θ - π/(4r))]
```

**Consistency check** — `G = P/2` with `r = 1/2` (Pauli rotations):
`∂f/∂θ = (1/2)[f(θ+π/2) - f(θ-π/2)]`, recovering the Pauli rule above. ✓

For `G = P` with `r = 1` (full Pauli, some hardware-native gates):
`∂f/∂θ = f(θ+π/4) - f(θ-π/4)`. Numerical check: `U(θ) = e^{-iθX}` on `|0⟩` with `O = Z`
gives `f(θ) = cos(2θ)`, and `f(θ+π/4) - f(θ-π/4) = -2sin(2θ) = f'(θ)` exactly. ✓

### Generalization to Multi-Eigenvalue Generators

For gates `U(θ) = exp(-iθG)` where `G` has `s` distinct eigenvalues (not just ±r), the
gradient is a sum of `2s-2` circuit evaluations with different parameter shifts
(Wierichs et al., 2022). This is the "generalized parameter shift" for more complex native gates.

---

## Comparison with Finite Differences

The most naive gradient estimation is **finite difference**:
```
∂f/∂θ ≈ [f(θ + ε) - f(θ - ε)] / (2ε)
```

**Comparison**:

| Method | Evaluations per parameter | Exact? | Noise sensitivity |
|--------|--------------------------|--------|-------------------|
| Finite difference | 2 | No (error `O(ε²)`) | High (1/ε amplification) |
| Parameter shift | 2 | Yes | Moderate |
| Forward finite diff | 1 | No (error `O(ε)`) | Highest |

The parameter-shift rule is superior: same cost as finite difference but **exact** (up to shot
noise). With finite difference, taking small `ε` for accuracy amplifies shot noise by `1/ε`.
Parameter shift avoids this trade-off entirely.

---

## Quantum Natural Gradient

### The Problem with Standard Gradient Descent

Standard gradient descent updates parameters as `θ ← θ - η∇E(θ)`. This ignores the geometry
of the parameter space. Two different parameter vectors `θ` and `θ'` that are close in Euclidean
distance may correspond to quantum states `|ψ(θ)⟩` and `|ψ(θ')⟩` that are very different, or
vice versa.

Optimizing in parameter space rather than state space leads to slow convergence and poor
conditioning when the parameter-to-state map has non-uniform Jacobian.

### Quantum Fisher Information Matrix (QFIM)

The natural gradient uses the **quantum Fisher information matrix (QFIM)** `F` as a metric tensor
on the parameter manifold. For pure states we use the convention (standard in quantum metrology):

```
F_{ij} = 4 Re[⟨∂ᵢψ|∂ⱼψ⟩ - ⟨∂ᵢψ|ψ⟩⟨ψ|∂ⱼψ⟩]
        = 4 Re[⟨∂ᵢψ|(I - |ψ⟩⟨ψ|)|∂ⱼψ⟩]
```

where `|∂ᵢψ⟩ = ∂|ψ(θ)⟩/∂θᵢ`. (Beware conventions: much of the QNG literature works with the
**Fubini-Study metric tensor** `g = F/4`, i.e., the same expression without the factor 4.
Since the natural-gradient update uses a pseudo-inverse, the choice only rescales the
learning rate — but statements like "F = 1" are convention-dependent, so always say which
normalization you use.)

`g = F/4` is the Fubini-Study metric on the space of quantum states: the infinitesimal
distance between `|ψ(θ)⟩` and `|ψ(θ+dθ)⟩` is `ds² = dθᵀ g dθ`.

### Quantum Natural Gradient Update

The **quantum natural gradient (QNG)** update is:

```
θ ← θ - η F⁺ ∇E(θ)
```

where `F⁺` is the pseudo-inverse of the QFIM. The QFIM regularizes the gradient by the local
geometry of the parameter manifold.

**Intuition**: The QNG takes a step of fixed size in *state space* (Fubini-Study geometry)
rather than in *parameter space*. Steps in state space are more meaningful physically and
avoid over-shooting when the parameter-to-state map is poorly conditioned.

### Computing the QFIM

For a circuit whose `i`-th parameter enters through a Pauli rotation `Rₚᵢ(θᵢ) = exp(-iθᵢPᵢ/2)`,
the diagonal QFIM elements have a closed form. With `|∂ᵢψ⟩ = -i(Pᵢ/2)` inserted at the gate's
position, `⟨∂ᵢψ|∂ᵢψ⟩ = 1/4` (since `Pᵢ² = I`) and `⟨ψ|∂ᵢψ⟩ = -(i/2)⟨Pᵢ⟩`, giving:

```
F_{ii} = 1 - ⟨Pᵢ⟩²
```

where `⟨Pᵢ⟩` is evaluated in the state just before the gate `Rₚᵢ` (one extra circuit per
parameter). The full off-diagonal QFIM requires additional circuit evaluations (overlap or
Hadamard-test circuits) but is often approximated by its diagonal (block-diagonal QNG) to
reduce cost.

**Cost**: `O(m²)` circuit evaluations for the full QFIM, or `O(m)` for the diagonal approximation.

---

## Second-Order Methods: Parameter Shift for the Hessian

The second derivative (Hessian) can also be computed exactly using parameter shifts:

```
∂²f/∂θᵢ∂θⱼ = [f(θ+sᵢ+sⱼ) - f(θ+sᵢ-sⱼ) - f(θ-sᵢ+sⱼ) + f(θ-sᵢ-sⱼ)] / 4
```

where `sᵢ = (π/2) eᵢ` is the shift vector. This requires `4` circuit evaluations per Hessian
element, giving `O(m²)` total evaluations for the full Hessian.

Second-order methods (Newton's method, BFGS) can converge faster than first-order methods but
are expensive for large `m`. In practice, limited-memory BFGS (L-BFGS) or Adam optimizer are
common choices for VQE.

---

## SPSA: Gradient-Free Alternative

**Simultaneous Perturbation Stochastic Approximation (SPSA)** estimates the full gradient
using only 2 circuit evaluations regardless of the number of parameters:

```
Δθ ~ Rademacher random vector (each entry ±1 independently)
g̃(θ) = [f(θ + cΔθ) - f(θ - cΔθ)] / (2c) · (1/Δθ)
```

where `(1/Δθ)` is the componentwise inverse. This is an unbiased estimator of the gradient
with variance `O(1/(c²S))` per component (using `S` shots).

**SPSA vs. parameter shift**:
- SPSA: `2` evaluations for all parameters simultaneously. Cheap per step but very noisy.
- Parameter shift: `2m` evaluations for all parameters. Expensive per step but much less noisy.

SPSA is useful in the very large parameter regime (`m ≫ 100`) where parameter-shift gradients
are too expensive, or on hardware where circuit execution is expensive.

---

## Shot Noise on Gradient Estimates

In practice, quantum measurements are stochastic. Each expectation value `⟨O⟩` is estimated
from `S` shots (circuit executions), with variance:

```
Var_S(⟨O⟩) = Var(O) / S ≤ 1/S   (since |eigenvalues of O| ≤ 1 for Pauli)
```

For the parameter-shift gradient `gᵢ = [f(θ+π/2 eᵢ) - f(θ-π/2 eᵢ)] / 2`:

```
Var_S(gᵢ) = [Var_S(f(θ+)) + Var_S(f(θ-))] / 4 ≤ 2/(4S) = 1/(2S)
```

To achieve gradient standard deviation `σ_g` per component:
```
S ≥ 1/(2σ_g²)
```

For `σ_g = 10^{-2}` (1% gradient accuracy): `S ≥ 5000` shots per parameter per iteration.
For `m = 100` parameters: `100 × 2 × 5000 = 10^6` shots per gradient step. This is the
typical regime for NISQ-era VQE.

**Interaction with barren plateaus**: In the barren plateau regime (Chapter 06/05), the
gradients themselves have magnitude `~2^{-n/2}` (variance `~2^{-n}` over random parameters).
To resolve such a gradient, the shot-noise standard deviation must be pushed below it:
`S ≳ 1/(2 · 2^{-n}) = 2^{n-1}` shots per component. At `n = 20` that is already `~5 × 10⁵`
shots per parameter per iteration, and the requirement doubles with every added qubit. This
exponential shot scaling is why barren plateaus make training infeasible.

---

## Key Formulas

- **Parameter-shift rule**: `∂f/∂θᵢ = [f(θ + π/2 eᵢ) - f(θ - π/2 eᵢ)] / 2`
- **General generator**: `∂f/∂θᵢ = r[f(θ + π/(4r) eᵢ) - f(θ - π/(4r) eᵢ)]` for generator
  eigenvalues `±r` (`r = 1/2` recovers the Pauli rule)
- **QFIM (pure state)**: `F_{ij} = 4 Re[⟨∂ᵢψ|∂ⱼψ⟩ - ⟨∂ᵢψ|ψ⟩⟨ψ|∂ⱼψ⟩]`; Fubini-Study metric `g = F/4`
- **QNG update**: `θ ← θ - η F⁺ ∇E(θ)`
- **Shot noise on gradient**: `Var_S(gᵢ) ≤ 1/(2S)`, need `S ≥ 1/(2σ_g²)`
- **Hessian shift**: `∂²f/∂θᵢ∂θⱼ = [f(++) - f(+-) - f(-+) + f(--)]/4`

---

## Worked Example: Parameter-Shift on a Single-Qubit Circuit

**Circuit**: `|ψ(θ)⟩ = Ry(θ)|0⟩`, **Observable**: `O = Z`.

```
f(θ) = ⟨ψ(θ)|Z|ψ(θ)⟩ = cos(θ)
```

(since `⟨0|Ry(-θ) Z Ry(θ)|0⟩ = cos θ`)

**Exact derivative**: `df/dθ = -sin(θ)`.

**Parameter-shift calculation at `θ = π/3`**:
```
f(π/3 + π/2) = f(5π/6) = cos(5π/6) = -√3/2 ≈ -0.866
f(π/3 - π/2) = f(-π/6) = cos(-π/6) = √3/2 ≈ 0.866

df/dθ|_{θ=π/3} = (-0.866 - 0.866) / 2 = -0.866
```

**Exact answer**: `-sin(π/3) = -√3/2 ≈ -0.866`. ✓ Parameter-shift is exact.

**Finite difference at `ε = 0.1`**:
```
[f(π/3 + 0.1) - f(π/3 - 0.1)] / 0.2 = [cos(π/3+0.1) - cos(π/3-0.1)] / 0.2
= [cos(1.147) - cos(0.947)] / 0.2 = [0.41104 - 0.58396] / 0.2 = -0.86458
```

**Error**: `|-0.86458 - (-0.86603)| ≈ 0.0014` (0.17% error) due to higher-order terms — matching
the leading truncation term `ε²|f‴(θ)|/6 = (0.01)(sin(π/3))/6 ≈ 0.0014`. The parameter-shift
has zero systematic error.

**QFIM computation** (convention `F = 4[⟨∂ψ|∂ψ⟩ - |⟨ψ|∂ψ⟩|²]`, as defined above):
```
|ψ(θ)⟩ = Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
|∂ψ⟩ = (1/2)(-sin(θ/2)|0⟩ + cos(θ/2)|1⟩)

⟨∂ψ|∂ψ⟩ = (1/4)(sin²(θ/2) + cos²(θ/2)) = 1/4
⟨ψ|∂ψ⟩ = (1/2)(-cos(θ/2)sin(θ/2) + sin(θ/2)cos(θ/2)) = 0

F = 4(1/4 - 0) = 1
```
This agrees with the closed form `F = 1 - ⟨Y⟩²` for an `Ry` gate applied to `|0⟩`, since
`⟨0|Y|0⟩ = 0`. (In the Fubini-Study convention without the factor 4, the same computation
reads `g = 1/4`.) The QFIM is constant in `θ`, so for this one-parameter circuit QNG reduces
to standard gradient descent with a rescaled learning rate.

---

## Summary

- The **parameter-shift rule** provides exact gradients using only 2 circuit evaluations per
  parameter — same cost as finite difference but without approximation error.
- The rule follows from the spectral decomposition of the gate generator; it generalizes to any
  gate with a 2-eigenvalue generator.
- **Quantum natural gradient** corrects for parameter space geometry using the QFIM (Fubini-Study
  metric), accelerating convergence compared to naive gradient descent.
- **SPSA** estimates all gradients with just 2 evaluations (high variance but low cost) —
  useful when `m ≫ 1` and per-step cost dominates.
- **Shot noise** sets a fundamental lower bound on gradient quality; in barren plateau regimes,
  the required shot count is exponential in system size, making training infeasible.

---

## Exercises

**1.** For `f(θ) = ⟨0|Ry(θ)† Z Ry(θ)|0⟩ = cos(θ)`, evaluate the parameter-shift gradient at
`θ = π/6` and compare with the exact derivative.

<details><summary>Solution</summary>

```
f(π/6 + π/2) = cos(2π/3) = -1/2
f(π/6 - π/2) = cos(-π/3) = +1/2
∂f/∂θ = (-1/2 - 1/2)/2 = -1/2
```
Exact: `f'(π/6) = -sin(π/6) = -1/2`. ✓ Agreement is exact — the rule has no discretization error.

</details>

**2.** The gate `U(θ) = exp(-iθ X₁X₂)` has generator `G = X₁X₂` with eigenvalues `±1`
(`r = 1`). For input `|00⟩` and observable `O = Z₁`, first show `f(θ) = cos(2θ)`, then verify
the two-term rule `∂f/∂θ = r[f(θ + π/(4r)) - f(θ - π/(4r))]` at `θ = 0.37`.

<details><summary>Solution</summary>

`U(θ)|00⟩ = cos(θ)|00⟩ - i sin(θ)|11⟩`, so `⟨Z₁⟩ = cos²θ - sin²θ = cos(2θ)`.
Rule with `r = 1`: `f(θ+π/4) - f(θ-π/4) = cos(2θ+π/2) - cos(2θ-π/2) = -2sin(2θ)`, which is
exactly `f'(θ)`. At `θ = 0.37`: the shifted evaluations give
`cos(2.3108) - cos(-0.8308) = -0.67429 - 0.67429 = -1.34858`, and the exact derivative is
`-2sin(0.74) = -1.34858`. ✓ Note that the Pauli-rule shift
`π/2` with prefactor `1/2` would give the wrong answer here — the shift and prefactor are set
by the generator's eigenvalue gap.

</details>

**3.** Using the Hessian shift formula with `i = j` (shift `s = π/2 eᵢ`), compute
`∂²f/∂θ²` for `f(θ) = cos(θ)` at `θ = 0`.

<details><summary>Solution</summary>

With `i = j`, the four evaluations become `f(θ+π)`, two copies of `f(θ)`, and `f(θ-π)`:
```
∂²f/∂θ² = [f(θ+π) - 2f(θ) + f(θ-π)] / 4 = [(-1) - 2(1) + (-1)]/4 = -1
```
Exact: `f''(0) = -cos(0) = -1`. ✓

</details>

**4.** Compute the (scalar) QFIM, convention `F = 4(⟨∂ψ|∂ψ⟩ - |⟨ψ|∂ψ⟩|²)`, for
(a) `|ψ(θ)⟩ = Rz(θ)|+⟩` and (b) `|ψ(θ)⟩ = Rz(θ)|0⟩`. Interpret the difference.

<details><summary>Solution</summary>

(a) `Rz(θ)|+⟩ = (e^{-iθ/2}|0⟩ + e^{iθ/2}|1⟩)/√2`. Then `|∂ψ⟩ = -i/2(e^{-iθ/2}|0⟩ - e^{iθ/2}|1⟩)/√2`,
`⟨∂ψ|∂ψ⟩ = 1/4`, `⟨ψ|∂ψ⟩ = -(i/2)⟨Z⟩ = 0`, so `F = 1`. The state moves at maximal speed
around the equator of the Bloch sphere.

(b) `Rz(θ)|0⟩ = e^{-iθ/2}|0⟩`: `⟨∂ψ|∂ψ⟩ = 1/4` but `⟨ψ|∂ψ⟩ = -i/2`, so
`F = 4(1/4 - 1/4) = 0`. The parameter only changes a global phase — the physical state does
not move at all. `F = 0` flags a redundant parameter; the QFIM is singular there and QNG must
use a pseudo-inverse or regularization. Both results match the closed form `F = 1 - ⟨Z⟩²`
(generator `Z/2`): `⟨+|Z|+⟩ = 0` gives 1, `⟨0|Z|0⟩ = 1` gives 0.

</details>

**5.** You want each parameter-shift gradient component to have shot-noise standard deviation
`σ_g ≤ 5 × 10⁻³`. Using `Var_S(gᵢ) ≤ 1/(2S)`, how many shots per shifted circuit are needed?
For `m = 50` parameters, how many total circuit executions per gradient step?

<details><summary>Solution</summary>

`S ≥ 1/(2σ_g²) = 1/(2 × 2.5 × 10⁻⁵) = 2 × 10⁴` shots per evaluation. Each component needs 2
evaluations, so one full gradient costs `50 × 2 × 2 × 10⁴ = 2 × 10⁶` circuit executions —
per optimizer iteration.

</details>

---

## Further Reading

1. **Mitarai, K. et al.** — "Quantum circuit learning," *Phys. Rev. A* 98, 032309 (2018).
   Original parameter-shift rule.
2. **Schuld, M. et al.** — "Evaluating analytic gradients on quantum hardware," *Phys. Rev. A*
   99, 032331 (2019). Independent derivation and broader treatment.
3. **Stokes, J. et al.** — "Quantum natural gradient," *Quantum* 4, 269 (2020). QNG derivation
   and connection to classical natural gradient.
4. **Wierichs, D. et al.** — "General parameter-shift rules for quantum gradients," *Quantum* 6,
   677 (2022). Generalized parameter shift for multi-eigenvalue generators.
5. **Sweke, R. et al.** — "Stochastic gradient descent for hybrid quantum-classical optimization,"
   *Quantum* 4, 314 (2020). Shot noise analysis and stochastic gradient methods.
