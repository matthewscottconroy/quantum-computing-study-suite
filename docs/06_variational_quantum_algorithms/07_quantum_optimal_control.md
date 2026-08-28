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

A widely used pulse-shaping technique in superconducting qubits is the DRAG pulse (Derivative
Removal via Adiabatic Gate; Motzoi et al., 2009). DRAG is an analytic derivation, not a GRAPE
product — though it is a common starting point and benchmark for GRAPE optimization. DRAG
pulses suppress leakage to the `|2⟩` state by using quadrature control `(I, Q)`: the in-phase
envelope `Ω_X(t) = Ω₀(t)` is accompanied by a quadrature component carrying its derivative,

```
Ω_Y(t) = -λ Ω̇_X(t) / Δ
```

where `Δ` is the anharmonicity and `λ` is a calibrated parameter. DRAG enables sub-20 ns
single-qubit gates with fidelity `> 99.9%` on superconducting hardware.

---

## Krotov Method

The **Krotov method** (Krotov, 1995) is an alternative to GRAPE that guarantees monotonic
convergence of the fidelity: each iteration never decreases `F`. This is theoretically appealing
but practically GRAPE (with line search) achieves comparable convergence.

**Update rule** (schematic, first order):
```
u'ₖ(t) = uₖ(t) + (α / S(t)) · Im[⟨Λ(t)| ∂H/∂uₖ |ψ'(t)⟩]
```

where `S(t) > 0` is a chosen weight (shape) function. The key difference: GRAPE evaluates its
gradient with the **old** controls at every time step, then updates all of them at once.
Krotov updates controls **sequentially** left-to-right, propagating `|ψ'(t)⟩` with the
already-updated controls for subsequent times. This sequential update guarantees monotonic
convergence.

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

**Implication for quantum gates**: A `π` rotation such as `Rx(π) = -iX` (equal to `X` up to
global phase) must take `|0⟩` to `|1⟩` — an evolution between orthogonal states. For a qubit
with energy splitting `ℏω₀`, suppose the total Hamiltonian (drive included) is capped in norm
at the qubit's own energy scale, `‖H‖ ≤ ℏω₀/2`; then `ΔE ≤ ℏω₀/2`, and the Mandelstam-Tamm
bound gives `τ ≥ πℏ/(2ΔE) ≥ π/ω₀`. (A stronger drive raises `ΔE` and lowers the bound
proportionally.) For a transmon with `ω₀/2π = 5 GHz`:
`τ ≥ π/(2π × 5 GHz) = 0.1 ns`. In practice, gates take `~10-50 ns` — limited by drive
amplitude, pulse bandwidth, and anharmonicity constraints, not by the QSL.

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
- **DRAG correction**: `Ω_X(t) = Ω₀(t)`, `Ω_Y(t) = -(λ/Δ) dΩ_X/dt`

---

## Worked Example: Single-Qubit GRAPE Run

**System**: Single qubit with drift `H₀ = (ω₀/2)Z`, control `H₁ = X`. Target gate: `X` (bit
flip). Duration `T = π/ω₀`, piece-wise constant control with `N = 4` intervals
(`Δt = T/4`). Work in units `ω₀ = 1`.

**Initial control**: `u_j = ω₀/2 = 0.5` for all `j` (constant drive — what a naive Rabi pulse
would be *if the drift were absent*).

**Initial fidelity**: with constant `u`, `U(T) = exp(-i(Z/2 + uX)T)`. For `u = 0.5` the
rotation axis is tilted 45° out of the equatorial plane, and evaluating
`F = |Tr[X†U(T)]|²/4` gives:
```
F₀ = sin²(π/√2)/2 = 0.3166
```
The drift `H₀` is not negligible, so the constant drive badly fails to invert the qubit —
a good starting point for optimization.

**Gradient computation**: numerically (or via the forward/backward propagator formula
`∂F/∂u_j = 2Δt Re[⟨Λⱼ|(-iX)|Pⱼ⟩]`), the initial gradient is symmetric in time:
```
∂F/∂u = (-0.308, +0.089, +0.089, -0.308)
```
GRAPE should *reduce* the drive at the edges and *increase* it in the middle.

**Gradient ascent** (fixed step `α = 0.3`, `u ← u + α ∂F/∂u`):
```
iteration   1:  F = 0.377
iteration  10:  F = 0.931
iteration  50:  F = 1.000000 (converged to numerical precision)
```
The converged pulse is `u* ≈ (-0.49, +1.34, +1.34, -0.49)` — strongly time-dependent and
symmetric, compensating the drift rotation. With `N = 20` intervals the same procedure also
reaches `F > 0.999999` in under 200 iterations, converging to a smooth ramped pulse. Even
crude piece-wise constant parameterizations reach the `>99.99%` fidelities quoted for
optimized pulses on hardware; real devices are instead limited by decoherence during the
pulse and by model inaccuracies (which robust control addresses).

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

## Exercises

**1.** A qubit evolves under a Hamiltonian with energy standard deviation
`ΔE/ℏ = 2π × 10 MHz`. What is the Mandelstam-Tamm minimum time to reach an orthogonal state?

<details><summary>Solution</summary>

`τ_MT = πℏ/(2ΔE) = π/(2 × 2π × 10⁷ rad/s) = 2.5 × 10⁻⁸ s = 25 ns`. Any control scheme
confined to this energy uncertainty — however cleverly shaped — cannot flip the qubit faster.

</details>

**2.** A resonant Rabi drive gives `H = (Ω/2)X` in the rotating frame with
`Ω/2π = 25 MHz`. (a) How long is a `π`-pulse (X gate)? (b) Show this saturates the
Mandelstam-Tamm bound for this Hamiltonian.

<details><summary>Solution</summary>

(a) `τ_π = π/Ω = π/(2π × 2.5 × 10⁷) = 20 ns`.
(b) For `|0⟩` under `(Ω/2)X`: `⟨H⟩ = 0` and `⟨H²⟩ = (ℏΩ/2)²`, so `ΔE = ℏΩ/2` and
`τ_MT = πℏ/(2·ℏΩ/2) = π/Ω` — exactly the `π`-pulse duration. A resonant constant drive is
time-optimal for this control set; pulse shaping buys robustness and spectral selectivity,
not raw speed.

</details>

**3.** Reproduce the worked example's starting point: for `H = (ω₀/2)Z + u·X` with `u = ω₀/2`
applied for `T = π/ω₀`, show the gate fidelity to `X` is `F = sin²(π/√2)/2 ≈ 0.317`.

<details><summary>Solution</summary>

Write `H = (ω₀/√2)·n̂·σ` with `n̂ = (1,0,1)/√2` (in units `ω₀ = 1`, `H = (Z+X)/2`, `|H| = 1/√2`).
Then `U(T) = cos(a)I - i sin(a)(X+Z)/√2` with rotation angle `a = |H|·T = π/√2 ≈ 2.221`.
So `Tr[X†U] = -i sin(a)·(1/√2)·Tr[X(X+Z)] = -i√2 sin(a)`, giving
`F = |Tr[X†U]|²/4 = 2sin²(π/√2)/4 = sin²(π/√2)/2 = 0.3166`. The drift tilts the rotation
axis 45° away from `x̂` and changes the effective rotation angle, so the constant drive both
rotates about the wrong axis and by the wrong amount.

</details>

**4.** A DRAG-corrected pulse uses a Gaussian `Ω_X(t) = Ω₀ e^{-(t-t₀)²/2σ²}` with `σ = 5 ns`,
`Ω₀/2π = 40 MHz`, `λ = 0.5`, and anharmonicity `|Δ|/2π = 250 MHz`. Estimate the peak amplitude
of the quadrature correction `Ω_Y = -(λ/Δ) dΩ_X/dt` relative to `Ω₀`.

<details><summary>Solution</summary>

`|dΩ_X/dt|` peaks at `t = t₀ ± σ` with value `Ω₀ e^{-1/2}/σ`. So
`max|Ω_Y|/Ω₀ = λ e^{-1/2}/(|Δ|σ) = 0.5 × 0.6065/(2π × 2.5 × 10⁸ × 5 × 10⁻⁹) ≈ 0.039`.
The DRAG correction is only ~4% of the main pulse amplitude, yet it suppresses `|2⟩` leakage
by an order of magnitude — small quadrature corrections targeting a specific error channel
are typical of robust-control solutions.

</details>

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
