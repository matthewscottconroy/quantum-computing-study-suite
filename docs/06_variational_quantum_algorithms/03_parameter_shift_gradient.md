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

The eigenvalues of `P/2` are `±1/2`, so `P/2` has eigenvalues `±1/2` and spectrum
`{-1/2, +1/2}`.

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

Taking the derivative:
```
∂f/∂θ = ⟨ψ₀| U_after† O U_after (-iP/2) Rₚ(θ) U_before |ψ₀⟩ + h.c.
```

Now use the identity for Pauli rotation gates: `Rₚ'(θ) = -i (P/2) Rₚ(θ)`. The key algebraic
identity is:

```
Rₚ(θ)' = -i(P/2) Rₚ(θ) = (i/2)[Rₚ(θ+π/2) - Rₚ(θ-π/2)]
```

(This follows from `e^{iα P/2} = cos(α/2)I + i sin(α/2)P` and differentiating with respect
to the rotation parameter.)

Substituting back:
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
∂f/∂θ = r · [f(θ + π/(4r)) - f(θ - π/(4r))] / 2
```

For `G = P/2` with `r = 1/2` (Pauli rotations): `∂f/∂θ = [f(θ+π/2) - f(θ-π/2)]/2`. ✓

For `G = P` with `r = 1` (full Pauli, some hardware-native gates): `∂f/∂θ = [f(θ+π/4) - f(θ-π/4)]/2`.

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
on the parameter manifold. Its definition:

```
F_{ij} = Re[⟨∂ᵢψ|∂ⱼψ⟩ - ⟨∂ᵢψ|ψ⟩⟨ψ|∂ⱼψ⟩]
        = Re[⟨∂ᵢψ|(I - |ψ⟩⟨ψ|)|∂ⱼψ⟩]
```

where `|∂ᵢψ⟩ = ∂|ψ(θ)⟩/∂θᵢ`.

`F` is the **Fubini-Study metric** on the space of quantum states: the infinitesimal Bures
distance between `|ψ(θ)⟩` and `|ψ(θ+dθ)⟩` is `ds² = dθᵀ F dθ`.

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

For a parameterized circuit with Pauli rotation gates, the QFIM element `F_{ij}` can be
computed using parameter shift rules:

```
F_{ij} = (1/2)[⟨ψ(θ+eᵢπ/2)|Pⱼ|ψ(θ-eᵢπ/2)⟩ - ⟨Pⱼ⟩² ]   (diagonal)
```

The full off-diagonal QFIM requires additional circuit evaluations but is often approximated
by its diagonal (block-diagonal QNG) to reduce cost.

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
Var_S(gᵢ) = Var_S(f(θ+)) + Var_S(f(θ-)) ≤ 2/(4S) = 1/(2S)
```

To achieve gradient standard deviation `σ_g` per component:
```
S ≥ 1/(2σ_g²)
```

For `σ_g = 10^{-2}` (1% gradient accuracy): `S ≥ 5000` shots per parameter per iteration.
For `m = 100` parameters: `100 × 2 × 5000 = 10^6` shots per gradient step. This is the
typical regime for NISQ-era VQE.

**Gradient amplification by barren plateaus**: In the barren plateau regime (Chapter 06/05),
`Var(gᵢ) ∝ 2^{-n}`. To maintain `σ_g = 10^{-2}` at `n = 20`: `S ≥ 2^{20}/200 ≈ 5,000` shots
*per parameter per iteration*, and this grows exponentially in `n`. This is why barren plateaus
make training infeasible.

---

## Key Formulas

- **Parameter-shift rule**: `∂f/∂θᵢ = [f(θ + π/2 eᵢ) - f(θ - π/2 eᵢ)] / 2`
- **General generator**: `∂f/∂θᵢ = r[f(θ + π/(4r) eᵢ) - f(θ - π/(4r) eᵢ)] / 2` for generator
  eigenvalues `±r`
- **QFIM**: `F_{ij} = Re[⟨∂ᵢψ|∂ⱼψ⟩ - ⟨∂ᵢψ|ψ⟩⟨ψ|∂ⱼψ⟩]`
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
= [cos(1.147) - cos(0.947)] / 0.2 = [0.409 - 0.585] / 0.2 = -0.88
```

**Error**: `|-0.88 - (-0.866)| = 0.014` (1.6% error) due to higher-order terms. The parameter-
shift has zero systematic error.

**QFIM computation**: `F = f(θ+π/2) - ⟨Z⟩² ... ` (see Appendix for single-qubit case).
For `Ry(θ)`, `F = ∂f/∂θ / (-2⟨Z⟩... )` — single qubit case gives `F = sin²(θ) / (1 - cos²θ) = 1`.
The QFIM is constant (= 1) for a single Pauli rotation, so QNG = standard gradient for this case.

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
