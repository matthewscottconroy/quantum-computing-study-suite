# Quantum Optimal Control

> **Prerequisites**: Schrödinger equation, unitary evolution, variational calculus basics
> **Connects to**: Hardware calibration (07/04), VQE and QAOA as discrete control problems
> (06/01, 06/04), superconducting qubit control pulses (07/01)

---

## Overview

Quantum optimal control (QOC) addresses the following question: given a quantum system with
controllable Hamiltonian `H(u(t))` — where `u(t)` are classical control parameters (microwave
pulse amplitudes and phases, laser intensities, etc.) — find the time-dependent control signal
`u*(t)` that drives the system from an initial state to a target final state or unitary in
minimum time, with maximum fidelity, or with minimum energy consumption.

QOC is not just a theoretical curiosity. Every quantum gate executed on actual hardware is
implemented by a classical control pulse. The transmon qubit gate with `20 ns` duration and
`99.9%` fidelity that appears in papers is the output of a quantum optimal control algorithm
applied to the physical Hamiltonian parameters of that specific device. Understanding QOC is
essential for understanding how quantum hardware actually works and how gate fidelities can
be improved.

Beyond hardware-level gates, QOC has deep connections to variational quantum algorithms:
QAOA is discrete optimal control, VQE gradient optimization is continuous control in parameter
space, and the quantum speed limit gives fundamental bounds on how fast quantum computation
can proceed.

---

## Problem Formulation

### The Control Problem

Consider a quantum system with Hamiltonian:

```
H(t) = H₀ + Σₖ uₖ(t) Hₖ
```

where `H₀` is the **drift Hamiltonian** (internal dynamics, cannot be turned off) and `Hₖ` are
**control Hamiltonians** modulated by time-dependent control signals `uₖ(t)`.

**Objective**: Find control functions `{uₖ(t)}` over time interval `[0, T]` such that the
time-evolution operator `U(T) = T exp(-i ∫₀ᵀ H(t) dt)` is as close as possible to a target
unitary `U_target`:

```
max_{u(t)} F(u) = |Tr[U_target† U(T)]|² / d²
```

where `d = 2^n` is the Hilbert space dimension and `F` is the gate fidelity (ranges 0 to 1).

Constraints may include:
- **Amplitude constraint**: `|uₖ(t)| ≤ u_max` (hardware limits)
- **Bandwidth constraint**: `|duₖ/dt| ≤ B` (finite rise time)
- **Duration constraint**: `T ≤ T_max` (before decoherence kills fidelity)

---

## GRAPE: Gradient Ascent Pulse Engineering

### Method

GRAPE (Khaneja et al., 2005) is the most widely used QOC algorithm. It parameterizes the
pulse as piece-wise constant: divide `[0,T]` into `N` time intervals of duration `Δt = T/N`.
The control `uₖ(t) = uₖ,ⱼ` is constant on interval `j`.

The evolution operator is:
```
U(T) = U_N U_{N-1} ... U₂ U₁
where U_j = exp(-i H(uⱼ) Δt)
```

The fidelity `F(u)` is differentiable with respect to `{uₖ,ⱼ}`. The gradient is computed
via forward and backward propagators:

```
∂F/∂u_{k,j} = 2 Δt · Re[ Tr[U_target† U_N...U_{j+1} (-iHₖ) Uⱼ ... U₁] ]
             = 2 Δt · Re[ ⟨Λⱼ| -iHₖ |Pⱼ⟩ ]
```

where `|Pⱼ⟩ = Uⱼ...U₁|ψ₀⟩` is the **forward propagated state** and
`⟨Λⱼ|` is the **backward propagated co-state** `= ⟨ψ₀|U₁†...Uⱼ†... U_N† U_target`.

**GRAPE iteration**:
```
u_{k,j} ← u_{k,j} + α · ∂F/∂u_{k,j}
```

The gradient is computed in `O(N · d²)` operations (matrix multiplications for each time step).

### GRAPE in Practice

GRAPE is the algorithm behind the DRAG pulse (Derivative Removal via Adiabatic Gate) technique
used in superconducting qubits. DRAG pulses suppress leakage to the `|2⟩` state by using
quadrature control `(I, Q)` to implement effective DRAG corrections:

```
Ω_X(t) = Ω₀(t) + λ Ω̇_Y(t) / Δ
```

where `Δ` is the anharmonicity and `λ` is a calibrated parameter. DRAG enables sub-20 ns
single-qubit gates with fidelity `> 99.9%` on superconducting hardware.

---

## Krotov Method

The **Krotov method** (Krotov, 1995) is an alternative to GRAPE that guarantees monotonic
convergence of the fidelity: each iteration never decreases `F`. This is theoretically appealing
but practically GRAPE (with line search) achieves comparable convergence.

**Update rule** (monotonically convergent):
```
u'_{k,j} = u_{k,j} + (α / Im[∂F/∂u]) · Re[⟨Λⱼ|Hₖ|P'ⱼ⟩]
```

The key difference: GRAPE computes `|P'ⱼ⟩` using the **old** controls for all `j`, then updates.
Krotov updates controls **sequentially** left-to-right, using updated controls immediately for
subsequent propagation. This sequential update guarantees monotonic convergence.

---

## CRAB: Chopped Random Basis

**CRAB** (Doria, Calarco, Montangero, 2011) takes a different approach: instead of piece-wise
constant pulses with `N` parameters, parameterize the pulse as a truncated random Fourier series:

```
u(t) = u_guess(t) · [1 + Σₗ₌₁ᴿ (aₗ sin(νₗt) + bₗ cos(νₗt))]
```

where `{νₗ}` are randomly chosen frequencies and `{aₗ, bₗ}` are `2R` optimization parameters.

**Advantages**:
- Very few parameters (`2R`, typically `R = 5-20`) → fast optimization.
- The random frequency choice avoids local optima.
- Applicable when gradient computation is expensive.

**Disadvantages**:
- Gradient-free by default (can be combined with gradient evaluation).
- Less efficient than GRAPE for many-parameter problems.

CRAB is widely used in cold atom experiments where hardware bandwidth limits the pulse complexity.

---

## Pontryagin Minimum Principle

The **Pontryagin minimum principle** (PMP) gives necessary conditions for time-optimal control.
For a quantum system, the PMP states that the optimal control satisfies:

```
H(x*(t), u*(t), λ*(t)) = min_{u ∈ U} H(x*(t), u, λ*(t))
```

where `H = λᵀ f(x,u)` is the Pontryagin Hamiltonian (not the quantum Hamiltonian), `x` is the
system state, and `λ` is the costate (adjoint variable).

For quantum gates with amplitude constraint `|u| ≤ u_max`, the PMP implies that **optimal
control is typically bang-bang**: `u(t) ∈ {±u_max}` (the control switches between maximum
amplitude values). This is the origin of the `π`-pulses and composite pulse sequences used
in NMR and quantum computing.

---

## Quantum Speed Limit

### The Mandelstam-Tamm Bound

The **quantum speed limit (QSL)** bounds the minimum time `τ` required to evolve a quantum
state to an orthogonal state. The **Mandelstam-Tamm (MT) bound** (1945):

```
τ_MT = ℏ π / (2 ΔE)
```

where `ΔE = √(⟨H²⟩ - ⟨H⟩²)` is the standard deviation of energy. This bound is tight for
two-level systems evolving between orthogonal states with a constant Hamiltonian.

### The Margolus-Levitin Bound

The **Margolus-Levitin (ML) bound** (1998):

```
τ_ML = ℏ π / (2 ⟨E⟩)
```

where `⟨E⟩ = ⟨H⟩ - E₀` is the mean energy above the ground state. The tighter bound is:

```
τ_QSL = ℏ π / (2 max(ΔE, ⟨E⟩))
```

**Implication for quantum gates**: A single-qubit rotation gate `Ry(π) = X` applied to a qubit
with energy splitting `ω₀` has minimum gate time `τ ≥ π/(2ω₀)`. For a transmon with
`ω₀/2π = 5 GHz`: `τ ≥ π/(10π GHz) = 0.1 ns`. In practice, gates take `~10-50 ns` due to
bandwidth limitations and anharmonicity constraints, not the QSL.

### QSL for Unitary Synthesis

For the gate synthesis problem (reach target unitary `U_target`), the QSL generalizes using the
Bures metric on the unitary group. The minimum time depends on the "distance" between the identity
and the target in the appropriate Riemannian metric. For a `k`-local Hamiltonian, the QSL for
implementing a `k`-body unitary scales as `Ω(n / k)`.

---

## VQAs as Discrete Optimal Control

### QAOA = Trotterized Adiabatic Control

The QAOA circuit with `p` layers is precisely a **discrete-time optimal control** problem:

```
State: |ψ(γ,β)⟩ = ∏_{l=1}^p [e^{-iβₗH_B} e^{-iγₗH_C}] |+⟩^⊗n
Control: (γ₁,...,γₚ, β₁,...,βₚ) ∈ [0,2π)^p × [0,π)^p
Objective: max F_p(γ,β) = ⟨H_C⟩
```

This maps directly to the quantum optimal control formulation with `H = H_C + (βₗ/γₗ) H_B`,
except that QAOA alternates between two Hamiltonians rather than mixing them.

The GRAPE algorithm applied to the continuum limit of QAOA recovers quantum annealing. QAOA
parameter optimization using gradient methods is formally identical to GRAPE applied to a
piece-wise constant control problem.

### VQE = Gradient-Based Control in Circuit Space

VQE with parameter-shift gradients is discrete-variable optimal control over the circuit
parameter manifold. The "control input" is the circuit parameters `θ`; the "state" is the
current quantum state `|ψ(θ)⟩`; the "Pontryagin Hamiltonian" corresponds to the cost function.

The connection is not merely formal: GRAPE-style techniques developed for pulse-level control
can be adapted to circuit-level parameter optimization, potentially improving convergence.

---

## Robust Control

Real quantum hardware has calibration errors: the qubit frequency `ω` is known only to
finite precision, there is crosstalk between qubits, etc. **Robust control** designs pulses
that are insensitive to these uncertainties.

**Average Hamiltonian Theory**: For a systematic error `δH`, the effective evolution over time
`T` is `U_eff = exp(-i(H₀ + δH + [H₀,δH]T/2 + ...)T)`. Designing `u(t)` to make the
first-order term `δH·T` small (e.g., via refocusing) gives **first-order robust** control.

**DRAG as robust control**: The DRAG correction is a form of robust control: it is designed to
cancel the effect of the `|2⟩` leakage level to first order in `δ/Δ` (ratio of gate rate to
anharmonicity), even without knowing the exact anharmonicity.

---

## Key Formulas

- **Control Hamiltonian**: `H(t) = H₀ + Σₖ uₖ(t) Hₖ`
- **Gate fidelity**: `F = |Tr[U_target† U(T)]|² / d²`
- **GRAPE gradient**: `∂F/∂u_{k,j} = 2Δt · Re[⟨Λⱼ|(-iHₖ)|Pⱼ⟩]`
- **Mandelstam-Tamm QSL**: `τ ≥ πℏ / (2ΔE)`
- **Margolus-Levitin QSL**: `τ ≥ πℏ / (2⟨E-E₀⟩)`
- **DRAG correction**: `Ω_X(t) = Ω₀ + (λ/Δ) dΩ_Y/dt`

---

## Worked Example: Single-Qubit GRAPE Iteration

**System**: Single qubit with `H₀ = (ω₀/2) Z`, control `H₁ = X`. Target gate: `X` (bit flip).
Duration: `T = π/ω₀` (one half-Rabi period). Piece-wise constant: `N = 4` intervals.

**Initial control**: `u₁,ⱼ = ω₀/2` for all `j` (constant drive).

**Forward propagation** (sketch, `Δt = T/4 = π/(4ω₀)`):
- `U_j = exp(-i(H₀ + u·X)Δt)` for each interval.
- `P₄ = U₄ U₃ U₂ U₁ |0⟩` (final state).

**Fidelity** at constant drive: `F₀ = |⟨0|X·P₄|0⟩|² ≈ 0.85` (not fully inverted for this
crude discretization).

**Gradient computation**:
For interval `j=2`: `∂F/∂u_{1,2} = 2Δt Re[⟨Λ₂|(-iX)|P₂⟩]`

**After 1 GRAPE step** (with step size `α = 0.1`):
`u_{1,2} ← 0.5 + 0.1 × grad ≈ 0.5 + 0.1 × 0.3 = 0.53`

After 20-50 iterations, GRAPE converges to the optimal pulse. Typical convergence: `F > 0.9999`
(99.99% fidelity) for `N = 20` intervals. This quantitatively reproduces the fidelities achieved
by optimized pulses on actual hardware.

---

## Summary

- Quantum optimal control finds time-dependent control pulses maximizing gate fidelity;
  it underlies all high-fidelity quantum gates on actual hardware.
- **GRAPE** uses gradient ascent with forward/backward propagators; standard for piece-wise
  constant pulses, enables `>99.9%` fidelity gates.
- **Krotov** is monotonically convergent; **CRAB** uses random Fourier basis for gradient-free
  optimization with few parameters.
- The **Pontryagin minimum principle** implies optimal controls are often bang-bang; the
  **quantum speed limit** (MT and ML bounds) gives fundamental lower bounds on gate times.
- QAOA is discrete optimal control; VQE gradient optimization is continuous control in circuit
  parameter space.
- **Robust control** (DRAG, composite pulses) makes gates insensitive to calibration errors —
  critical for real hardware performance.

---

## Further Reading

1. **Khaneja, N. et al.** — "Optimal control of coupled spin dynamics: design of NMR pulse
   sequences by gradient ascent algorithms," *J. Magn. Reson.* 172, 296 (2005). GRAPE algorithm.
2. **Doria, P., Calarco, T., and Montangero, S.** — "Optimal control technique for many-body
   quantum dynamics," *Phys. Rev. Lett.* 106, 190501 (2011). CRAB algorithm.
3. **Margolus, N. and Levitin, L. B.** — "The maximum speed of dynamical evolution," *Physica D*
   120, 188 (1998). ML quantum speed limit.
4. **Glaser, S. J. et al.** — "Training Schrödinger's cat: quantum optimal control," *Eur. Phys.
   J. D* 69, 279 (2015). Comprehensive review.
5. **Krantz, P. et al.** — "A quantum engineer's guide to superconducting qubits," *Appl. Phys.
   Rev.* 6, 021318 (2019). Chapter 4 covers pulse-level control for transmon qubits.
