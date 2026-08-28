# Distance Measures and the Lindblad Master Equation

> **Prerequisites**: 02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md, 05_density_matrices_and_open_systems.md  
> **Connects to**: Quantum error correction thresholds, gate benchmarking (07_quantum_hardware/04_benchmarking_and_characterization.md), quantum channel capacities, decoherence modeling on real hardware

## Overview

Chapter 05 established that real quantum states are density matrices and real evolutions are CPTP maps with Kraus decompositions `ε(ρ) = Σₖ KₖρKₖ†`. Two natural questions follow immediately, and this chapter answers both.

First: **how close are two quantum states?** If a noisy device was supposed to prepare `ρ` but actually produced `σ`, we need a number quantifying the damage — and it should have operational meaning, not just be a formula. The two standard measures are the **trace distance** and the **fidelity**. The trace distance tells you exactly how well the two states can be distinguished by any measurement; the fidelity tells you how well one state "passes for" the other. They bound each other via the Fuchs–van de Graaff inequalities, so either one controls the other.

Second: **how do states evolve in continuous time under noise?** The Kraus picture describes a channel as a discrete black box: state in, state out. But hardware decoherence happens continuously — a qubit sitting idle for time `t` accumulates `T₁` decay and `T₂` dephasing that grow with `t`. The differential-equation counterpart of the CPTP framework is the **Lindblad master equation** (GKSL equation), which is to open systems what the Schrödinger equation is to closed ones. Its "jump operators" `Lₖ` encode the physical noise processes, and solving it for a qubit reproduces exactly the exponential decays that `T₁` and `T₂` experiments measure. These two topics — metrics on states and generators of noisy dynamics — are the working vocabulary of every experimental paper that quotes a fidelity or a coherence time.

## Trace Distance

### Definition and Basic Properties

The **trace distance** between density matrices `ρ` and `σ` is

```
D(ρ, σ) = ½ ‖ρ − σ‖₁ = ½ Tr|ρ − σ|,   where |A| = √(A†A)
```

Since `ρ − σ` is Hermitian and traceless, `Tr|ρ − σ|` is just the sum of the absolute values of its eigenvalues. Trace distance is a genuine metric: `D(ρ,σ) ≥ 0` with equality iff `ρ = σ`, it is symmetric, and it satisfies the triangle inequality. It ranges from `0` (identical states) to `1` (perfectly distinguishable states, i.e. states with orthogonal supports).

### Operational Meaning: Optimal State Discrimination

Suppose someone hands you a single copy of either `ρ` or `σ`, each with probability `½`, and you must guess which. The **Holevo–Helstrom theorem** says the best possible success probability over all measurements is

```
p_success = ½ (1 + D(ρ, σ))
```

Equivalently, `D(ρ,σ) = max_P Tr(P(ρ − σ))` over all projectors (indeed all POVM effects `0 ≤ P ≤ I`); the optimal `P` projects onto the positive eigenspace of `ρ − σ`. So `D = 0` means guessing is a coin flip and `D = 1` means one measurement distinguishes the states perfectly. Trace distance also bounds how much any single measurement statistic can differ: for every POVM, the classical total-variation distance between the two outcome distributions is at most `D(ρ,σ)`.

### Contractivity Under CPTP Maps

For every quantum channel `ε`,

```
D(ε(ρ), ε(σ)) ≤ D(ρ, σ)
```

Noise never *increases* distinguishability — if it could, you could distinguish states better by first degrading them, contradicting the Helstrom optimality above (any measurement after `ε` is just some measurement on the original states). Contractivity is the workhorse property: it is why decoherence irreversibly erases information, and why the distance of a state to a channel's fixed point decreases monotonically.

### Qubit Formula: Bloch Picture

For qubits `ρ = ½(I + r⃗·σ⃗)` and `σ = ½(I + s⃗·σ⃗)`,

```
ρ − σ = ½ (r⃗ − s⃗)·σ⃗   ⟹   D(ρ, σ) = ½ |r⃗ − s⃗|
```

because `(r⃗−s⃗)·σ⃗` has eigenvalues `±|r⃗−s⃗|`. Trace distance is **half the Euclidean distance between Bloch vectors** — the geometry of the Bloch ball is literally the geometry of distinguishability.

## Fidelity

### Definition and Convention

The **fidelity** between `ρ` and `σ` is

```
F(ρ, σ) = ( Tr √( √ρ σ √ρ ) )²
```

**Convention warning**: this chapter uses the *squared* convention, so that `F` is a probability (this matches Jozsa's original definition and virtually all experimental papers). Nielsen & Chuang define the *square root* of this quantity as their fidelity, `F_NC = Tr√(√ρ σ √ρ) = √F`. When reading any paper, check which convention it uses; here `F ∈ [0, 1]` always, with `F = 1` iff `ρ = σ` and `F = 0` iff the states have orthogonal supports. Despite appearances, `F` is symmetric: `F(ρ,σ) = F(σ,ρ)`.

### Special Cases

**Both states pure**, `ρ = |ψ⟩⟨ψ|`, `σ = |φ⟩⟨φ|`:

```
F = |⟨ψ|φ⟩|²
```

the familiar overlap probability.

**One state pure**, `ρ = |ψ⟩⟨ψ|`:

```
F(|ψ⟩⟨ψ|, σ) = ⟨ψ|σ|ψ⟩
```

the probability that `σ` passes a test for `|ψ⟩`. This is the quantity experimentalists report as "state preparation fidelity."

**Qubits (closed form)**:

```
F(ρ, σ) = Tr(ρσ) + 2√(det ρ · det σ)
```

If either state is pure its determinant vanishes and `F = Tr(ρσ)`. In Bloch form with a pure `ρ` (`|r⃗| = 1`): `F = ½(1 + r⃗·s⃗)`.

### Uhlmann's Theorem

Why is this strange-looking formula the right notion of "overlap" for mixed states? **Uhlmann's theorem**: 

```
F(ρ, σ) = max |⟨ψ_ρ | ψ_σ⟩|²
```

where the maximum runs over all **purifications** `|ψ_ρ⟩, |ψ_σ⟩` of `ρ` and `σ` on a system extended by an ancilla. Fidelity is the best possible pure-state overlap achievable by "lifting" both mixed states to pure states on a larger space. This makes many properties obvious: symmetry, invariance under unitaries, `F = 1 ⟺ ρ = σ`, and monotonicity `F(ε(ρ), ε(σ)) ≥ F(ρ, σ)` under channels (fidelity can only increase as noise makes states less distinguishable — the mirror image of trace-distance contractivity).

### Fuchs–van de Graaff Inequalities

Trace distance and fidelity control each other:

```
1 − √F(ρ,σ)  ≤  D(ρ,σ)  ≤  √(1 − F(ρ,σ))
```

The upper bound is an equality when both states are pure. Consequences: `F → 1 ⟺ D → 0` and `F → 0 ⟺ D → 1`, so the two measures define the same notion of "close" — but the bounds are quadratically loose, which matters in error-correction threshold arguments. A gate with infidelity `1 − F = 10⁻⁴` may have trace-distance (worst-case) error as large as `√(10⁻⁴) = 10⁻²`. This gap between average and worst case reappears below in the diamond norm.

## Distance Between Channels: the Diamond Norm

To compare two *channels* (say a noisy gate `ε` against the ideal unitary `U`), taking the worst-case trace distance over inputs is not enough — the gate may act on a qubit entangled with the rest of the computer. The **diamond norm distance** fixes this by allowing an ancilla:

```
½ ‖ε − U‖⋄ = max_ρ D( (ε ⊗ I)(ρ), (U ⊗ I)(ρ) )
```

maximized over states `ρ` on the system *plus an equally large ancilla*. It is the right metric for fault tolerance because it composes: the diamond error of a circuit is at most the sum of the diamond errors of its gates, so it gives worst-case guarantees no matter how gates are wired together or entangled with ancillas.

In contrast, **randomized benchmarking** (see 07_quantum_hardware/04_benchmarking_and_characterization.md) measures the **average gate fidelity** `F_avg = ∫ dψ ⟨ψ|U†ε(|ψ⟩⟨ψ|)U|ψ⟩`, an average over pure inputs rather than a worst case. The RB "error per Clifford" is `r = (d−1)(1 − F_avg)/d` (with `d = 2` for one qubit). The two are related but not interchangeable: `½‖ε − U‖⋄` is lower-bounded by roughly the infidelity `1 − F_avg`, but for *coherent* errors (small unitary miscalibrations) it can be as large as `∼ √(1 − F_avg)` — exactly the Fuchs–van de Graaff quadratic gap. This is why an RB number of `10⁻⁴` does not by itself certify a worst-case gate error of `10⁻⁴`, and why techniques like randomized compiling (which convert coherent errors into stochastic ones, closing the gap) matter for fault-tolerance projections.

## The Lindblad Master Equation

### From Kraus Maps to a Differential Equation

Chapter 05 gave the finite-time picture: evolution over any interval is a CPTP map `ε(ρ) = Σₖ KₖρKₖ†`. Now assume the noise is **Markovian**: the environment has no memory, so evolving for time `t + s` is the same as evolving for `t` then for `s`:

```
ε_{t+s} = ε_t ∘ ε_s,    ε_0 = I     (a quantum dynamical semigroup)
```

**GKSL theorem** (Gorini–Kossakowski–Sudarshan–Lindblad, 1976): a continuous semigroup of CPTP maps is generated by `ε_t = e^{tℒ}` where the generator has the form

```
dρ/dt = ℒ(ρ) = −i[H, ρ] + Σₖ ( Lₖ ρ Lₖ† − ½{Lₖ†Lₖ, ρ} )
```

with `H` Hermitian (the coherent part, possibly including environment-induced energy shifts) and arbitrary **jump operators** `Lₖ`. Conversely, every equation of this form generates a legitimate CPTP evolution. (Units: `ħ = 1`; `{A,B} = AB + BA` is the anticommutator.)

**Derivation sketch from the Kraus picture.** Over an infinitesimal step `dt`, expand the Kraus operators in powers of `√dt`:

```
K₀ = I + (−iH − ½ Σₖ Lₖ†Lₖ) dt,    Kₖ = Lₖ √dt   (k ≥ 1)
```

The jump operators come with `√dt` because a jump (e.g. photon emission) occurs with probability `∝ dt`, and probabilities are quadratic in Kraus operators. The completeness condition `Σ Kₖ†Kₖ = I` holds to order `dt` precisely because of the `−½ΣLₖ†Lₖ` term in `K₀` — that term is not optional; it is what keeps the evolution trace-preserving. Substituting into `ρ(t+dt) = Σₖ Kₖ ρ Kₖ†` and keeping terms of order `dt` yields the Lindblad equation. Each term has a physical reading: `LₖρLₖ†` is the state *after* jump `k` occurs, and `−½{Lₖ†Lₖ, ρ}` is the smooth "no-jump" back-action that renormalizes the state when the jump does not occur.

### Jump Operators for the Workhorse Channels

**Amplitude damping (energy relaxation).** Spontaneous decay `|1⟩ → |0⟩` at rate `γ`:

```
L = √γ σ₋,    σ₋ = |0⟩⟨1|
```

Writing `ρ = [[ρ₀₀, ρ₀₁], [ρ₁₀, ρ₁₁]]`, the dissipator gives (with `L†L = γ|1⟩⟨1|`):

```
dρ₁₁/dt = −γ ρ₁₁          ⟹  ρ₁₁(t) = ρ₁₁(0) e^{−γt}
dρ₀₁/dt = −(γ/2) ρ₀₁      (from the anticommutator term only)
```

The excited population decays exponentially with time constant `T₁ = 1/γ`; integrating the channel over time `t` reproduces the amplitude-damping Kraus operators of Chapter 05 with `γ_channel = 1 − e^{−t/T₁}`. Note that coherences decay at only *half* the population rate — this factor of 2 is the origin of the `2T₁` in the `T₂` bound.

**Pure dephasing.** Random `Z`-axis phase kicks at rate `γ_φ`:

```
L = √(γ_φ / 2) σ_z
```

Since `σ_z ρ σ_z` flips the sign of off-diagonal elements and `L†L = (γ_φ/2) I`:

```
dρ₀₁/dt = (γ_φ/2)(−ρ₀₁ − ρ₀₁) = −γ_φ ρ₀₁,    dρ₀₀/dt = dρ₁₁/dt = 0
```

Populations untouched, coherences decay at `γ_φ = 1/T_φ`. (The factor `½` in `L` is chosen precisely so that the coherence decay rate is `γ_φ`.)

**Thermal excitation.** An environment at temperature `T` with mean photon number `n̄` both absorbs and emits:

```
L↓ = √(γ(n̄+1)) σ₋,    L↑ = √(γ n̄) σ₊,    σ₊ = |1⟩⟨0|
```

The populations relax at the *enhanced* rate `γ(2n̄+1)` toward the thermal steady state `ρ₁₁ = n̄/(2n̄+1)` rather than the ground state. At `n̄ = 0` this reduces to pure amplitude damping. For a 5 GHz superconducting qubit at 20 mK, `n̄ ≈ 10⁻⁵`, which is why the zero-temperature model is usually adequate — but residual thermal population (`∼1%` excited-state population is commonly measured) is a real hardware imperfection.

### The T₂ Relation, Derived

Run amplitude damping and pure dephasing simultaneously (jump operators `√γ σ₋` and `√(γ_φ/2) σ_z`; both dissipators are additive in the Lindblad equation). The coherence obeys

```
dρ₀₁/dt = −(γ/2 + γ_φ) ρ₀₁   ⟹   ρ₀₁(t) = ρ₀₁(0) e^{−t/T₂}
```

with total dephasing rate `1/T₂ = γ/2 + γ_φ`. Substituting `γ = 1/T₁` and `γ_φ = 1/T_φ`:

```
1/T₂ = 1/(2T₁) + 1/T_φ
```

Energy relaxation *necessarily* dephases (a decayed qubit has lost its phase), contributing `1/(2T₁)`; pure dephasing adds on top. Since `T_φ ≥ 0`, this yields the fundamental bound `T₂ ≤ 2T₁` quoted in Chapter 05. Hardware where `T₂ ≈ 2T₁` is "`T₁`-limited" (dephasing dominated by unavoidable relaxation); `T₂ ≪ 2T₁` signals flux noise, photon shot noise, or other pure-dephasing mechanisms with headroom to engineer away.

### Solving the Qubit Lindblad Equation in the Bloch Picture

Work in the frame rotating at the qubit frequency, so `H = 0` (in the lab frame `H = (ω/2)σ_z` just adds Larmor precession `ṙ_x = −ω r_y`, `ṙ_y = ω r_x`). Convert the matrix equations above to the Bloch vector `r⃗ = (r_x, r_y, r_z)` using `ρ₀₁ = (r_x − i r_y)/2` and `r_z = ρ₀₀ − ρ₁₁`. From `dρ₁₁/dt = −γρ₁₁` and trace preservation, `ṙ_z = 2γρ₁₁ = γ(1 − r_z)`. The result is a closed linear ODE system:

```
ṙ_x = −r_x / T₂
ṙ_y = −r_y / T₂
ṙ_z = −(r_z − 1) / T₁
```

with the exponential solutions

```
r_x(t) = r_x(0) e^{−t/T₂}
r_y(t) = r_y(0) e^{−t/T₂}
r_z(t) = 1 + (r_z(0) − 1) e^{−t/T₁}
```

Geometrically: the Bloch vector's transverse component spirals inward with time constant `T₂` while its longitudinal component relaxes toward the north pole (`|0⟩`, `r_z = 1`) with time constant `T₁`. These are the **Bloch equations**, historically written down for NMR decades before the GKSL theorem — the Lindblad formalism is their rigorous quantum-mechanical justification.

**Connection to measurement on real hardware.** These solutions *are* the standard characterization experiments:

- **T₁ (inversion recovery)**: prepare `|1⟩` (`r_z = −1`), wait `t`, measure `Z`. Prediction: `⟨Z⟩ = 1 − 2e^{−t/T₁}` — fit the exponential, extract `T₁`.
- **T₂ (Ramsey)**: prepare `|+⟩` (`r_x = 1`) with a `π/2` pulse, wait `t`, apply another `π/2` and measure. The fringe envelope decays as `e^{−t/T₂*}` (Ramsey measures `T₂*`, which includes quasi-static frequency noise; a Hahn echo refocuses the slow noise and recovers the intrinsic `T₂`).

The measured decay curves in any qubit spec sheet are literally the exponentials above, and the quoted `T₁`, `T₂` are the `1/γ`, `1/(γ/2 + γ_φ)` of this section's jump operators.

## Key Formulas

**Trace distance**: `D(ρ,σ) = ½‖ρ−σ‖₁`; qubits: `D = ½|r⃗ − s⃗|`

**Helstrom bound**: `p_success = ½(1 + D)` for distinguishing `ρ` vs `σ` (single copy, equal priors)

**Contractivity**: `D(ε(ρ), ε(σ)) ≤ D(ρ,σ)` for every channel `ε`

**Fidelity** (squared convention): `F(ρ,σ) = (Tr√(√ρ σ √ρ))²`; pure–pure: `F = |⟨ψ|φ⟩|²`; pure–mixed: `F = ⟨ψ|σ|ψ⟩`; qubits: `F = Tr(ρσ) + 2√(det ρ det σ)`

**Uhlmann**: `F(ρ,σ) = max |⟨ψ_ρ|ψ_σ⟩|²` over purifications

**Fuchs–van de Graaff**: `1 − √F ≤ D ≤ √(1−F)` (right side tight for pure states)

**Lindblad equation**: `dρ/dt = −i[H,ρ] + Σₖ (Lₖ ρ Lₖ† − ½{Lₖ†Lₖ, ρ})`

**Jump operators**: amplitude damping `L = √γ σ₋` (`T₁ = 1/γ`); pure dephasing `L = √(γ_φ/2) σ_z`; thermal `L↓ = √(γ(n̄+1))σ₋`, `L↑ = √(γn̄)σ₊`

**Coherence times**: `1/T₂ = 1/(2T₁) + 1/T_φ`, hence `T₂ ≤ 2T₁`

**Bloch solutions**: `r_{x,y}(t) = r_{x,y}(0)e^{−t/T₂}`, `r_z(t) = 1 + (r_z(0)−1)e^{−t/T₁}`

## Worked Example

**Problem**: Take `ρ = |+⟩⟨+|` and let `σ` be the output of Chapter 05's phase-flip channel on `ρ` with `p = 1/4`. Compute `D(ρ,σ)` and `F(ρ,σ)` exactly, twice each — from the matrices and from the Bloch formulas — and verify the Fuchs–van de Graaff inequalities.

**Setup**: from Chapter 05's worked example,

```
ρ = ½ [[1, 1],       σ = ½ [[1, 1−2p],       = ½ [[1, ½],
       [1, 1]]              [1−2p, 1]]              [½, 1]]
```

Bloch vectors: `r⃗ = (1, 0, 0)` (pure, on the +x axis) and `s⃗ = (1−2p, 0, 0) = (½, 0, 0)`.

**Trace distance from matrices**:

```
ρ − σ = ½ [[0, ½], [½, 0]] = [[0, ¼], [¼, 0]]
```

Eigenvalues of `[[0, ¼],[¼, 0]]`: solve `λ² − (¼)² = 0`, so `λ = ±¼`. Then `‖ρ−σ‖₁ = ¼ + ¼ = ½` and

```
D(ρ, σ) = ½ · ½ = ¼
```

**Trace distance from Bloch vectors**: `D = ½|r⃗ − s⃗| = ½|(½, 0, 0)| = ½ · ½ = ¼`. ✔ Agrees.

**Fidelity from the full definition**: since `ρ` is a projector, `√ρ = ρ`, so

```
M = √ρ σ √ρ = |+⟩⟨+| σ |+⟩⟨+| = ⟨+|σ|+⟩ · |+⟩⟨+|
```

`⟨+|σ|+⟩` is half the sum of all entries of `σ`: `½ · ½ (1 + ½ + ½ + 1) = ¾`. So `M = ¾|+⟩⟨+|` has eigenvalues `¾` and `0`, giving `Tr√M = √(¾)` and

```
F = (Tr√M)² = ¾
```

**Fidelity from qubit formulas**: `Tr(ρσ) = ¼(1·1 + 1·½ + 1·½ + 1·1) = ¾` and `det ρ = 0`, so `F = Tr(ρσ) + 0 = ¾`. Bloch check with pure `ρ`: `F = ½(1 + r⃗·s⃗) = ½(1 + ½) = ¾`. ✔ All three routes agree.

**Fuchs–van de Graaff check**:

```
1 − √F = 1 − √3/2 ≈ 0.1340  ≤  D = 0.25  ≤  √(1−F) = √(¼) = 0.5   ✔
```

Both brackets hold with room to spare, as they must — `σ` is mixed, so the pure-state saturation of the upper bound does not apply. (Numerical verification, python3 stdlib: eigenvalues of `ρ−σ` = `±0.25` → `D = 0.25` both ways; `F = 0.75` by all four methods — full definition via `√ρ σ √ρ` eigenvalues `{0.75, 0}`, `⟨+|σ|+⟩`, the qubit determinant formula, and the Bloch form; FvdG `0.133975 ≤ 0.25 ≤ 0.5` → True.)

**Interpretation**: after 25% dephasing, the best single-shot measurement distinguishes the noisy state from the ideal one with probability `½(1 + ¼) = 62.5%`, and the state still passes a `|+⟩` test three times out of four.

## Summary

- **Trace distance** `D(ρ,σ) = ½‖ρ−σ‖₁` is the operational measure of distinguishability: best single-shot discrimination succeeds with probability `½(1+D)`, and no channel can increase `D` (contractivity)
- **Fidelity** `F(ρ,σ) = (Tr√(√ρσ√ρ))²` (squared convention here; N&C use its square root) measures overlap: `|⟨ψ|φ⟩|²` for pure states, best purification overlap in general (Uhlmann)
- **Fuchs–van de Graaff** `1−√F ≤ D ≤ √(1−F)` makes the two measures interchangeable up to a quadratic gap — the same gap separating average gate fidelity (what randomized benchmarking measures) from the **diamond norm** (what fault-tolerance proofs need)
- For qubits everything is Euclidean geometry on the Bloch ball: `D = ½|r⃗−s⃗|`, `F = Tr(ρσ) + 2√(det ρ det σ)`
- The **Lindblad equation** `dρ/dt = −i[H,ρ] + Σₖ(LₖρLₖ† − ½{Lₖ†Lₖ,ρ})` is the continuous-time limit of Markovian Kraus evolution; the GKSL theorem says this form is exactly equivalent to CPTP semigroup dynamics
- Workhorse jump operators: `√γ σ₋` (amplitude damping, `T₁ = 1/γ`), `√(γ_φ/2) σ_z` (pure dephasing), thermal pair `√(γ(n̄+1))σ₋, √(γn̄)σ₊`
- The dissipators combine additively, giving `1/T₂ = 1/(2T₁) + 1/T_φ` and the bound `T₂ ≤ 2T₁`
- Solving the qubit Lindblad equation yields the **Bloch equations** — pure exponential decays `e^{−t/T₂}` (transverse) and `e^{−t/T₁}` (longitudinal, toward `|0⟩`) that are exactly what `T₁` inversion-recovery and Ramsey/echo experiments fit on real hardware

## Exercises

**Exercise 1**: Compute `D` and `F` for the pure states `|0⟩` and `|+⟩`, and show they saturate the upper Fuchs–van de Graaff inequality.

<details><summary>Solution</summary>

Bloch vectors `r⃗ = (0,0,1)`, `s⃗ = (1,0,0)`. Trace distance: `D = ½|r⃗−s⃗| = ½√2 = 1/√2 ≈ 0.7071`. Fidelity (pure–pure): `F = |⟨0|+⟩|² = ½`. Upper FvdG bound: `√(1−F) = √(½) = 1/√2 = D` — equality, as expected for two pure states. Lower bound: `1 − √(½) ≈ 0.2929 ≤ 0.7071`. ✔
</details>

**Exercise 2**: For a general qubit state `ρ` with Bloch vector `r⃗`, show that `D(ρ, I/2) = |r⃗|/2` and `F(ρ, I/2) = ½(1 + √(1−|r⃗|²))`. What do these give for a pure state?

<details><summary>Solution</summary>

Trace distance: `ρ − I/2 = ½ r⃗·σ⃗` has eigenvalues `±|r⃗|/2`, so `D = ½(|r⃗|/2 + |r⃗|/2) = |r⃗|/2`. Fidelity via the qubit formula: `Tr(ρ · I/2) = ½`, `det(I/2) = ¼`, and `det ρ = (1−|r⃗|²)/4` (product of eigenvalues `(1±|r⃗|)/2`). So `F = ½ + 2√((1−|r⃗|²)/16) = ½(1 + √(1−|r⃗|²))`. For a pure state (`|r⃗| = 1`): `D = ½` and `F = ½` — every pure state is "half distinguishable" from white noise, and white noise passes any pure-state test with probability exactly `½`.
</details>

**Exercise 3**: Verify trace-distance contractivity explicitly for the phase-flip channel `ε(ρ) = (1−p)ρ + pZρZ` acting on arbitrary qubit states, using the Bloch picture. For which pairs of states does dephasing *not* reduce their distinguishability?

<details><summary>Solution</summary>

From Chapter 05, the phase-flip channel maps Bloch vectors as `(r_x, r_y, r_z) → ((1−2p)r_x, (1−2p)r_y, r_z)`. For two states with difference vector `d⃗ = r⃗ − s⃗`:

`D(ε(ρ),ε(σ)) = ½√((1−2p)²(d_x² + d_y²) + d_z²) ≤ ½√(d_x² + d_y² + d_z²) = D(ρ,σ)`

since `(1−2p)² ≤ 1` for `p ∈ [0,1]`. Equality holds iff `d_x = d_y = 0` (the states differ only in their `Z` populations — dephasing cannot hurt information stored in the `Z` basis) or `p ∈ {0, 1}` (the channel is unitary: identity or `Z`).
</details>

**Exercise 4**: Derive the Bloch equation for `r_z` under the thermal Lindblad dissipators `L↓ = √(γ(n̄+1))σ₋`, `L↑ = √(γn̄)σ₊`. Find the relaxation rate and the steady-state Bloch vector, and check the `n̄ → 0` limit.

<details><summary>Solution</summary>

The two dissipators give population rate equations `dρ₁₁/dt = −γ(n̄+1)ρ₁₁ + γn̄ ρ₀₀` (down-jumps drain `|1⟩`, up-jumps feed it). With `r_z = ρ₀₀ − ρ₁₁ = 1 − 2ρ₁₁`:

`ṙ_z = −2ρ̇₁₁ = 2γ(n̄+1)ρ₁₁ − 2γn̄ρ₀₀ = −γ(2n̄+1) r_z + γ`

using `ρ₁₁ = (1−r_z)/2`, `ρ₀₀ = (1+r_z)/2`. So the relaxation rate is `γ₁ = γ(2n̄+1)` — thermal photons *accelerate* `T₁` decay — and the steady state is `r_z^ss = 1/(2n̄+1)`, i.e. `ρ₁₁^ss = n̄/(2n̄+1)`, the thermal (Gibbs) population. As `n̄ → 0`: rate `→ γ`, steady state `→ |0⟩⟨0|`, recovering pure amplitude damping. Solution: `r_z(t) = r_z^ss + (r_z(0) − r_z^ss)e^{−γ(2n̄+1)t}`.
</details>

**Exercise 5**: A superconducting qubit is measured to have `T₁ = 80 μs` and (echo) `T₂ = 60 μs`. (a) Find the pure dephasing time `T_φ`. (b) Is this qubit `T₁`-limited? (c) If materials improvements doubled `T₁` with `T_φ` unchanged, what would the new `T₂` be?

<details><summary>Solution</summary>

(a) From `1/T₂ = 1/(2T₁) + 1/T_φ`: `1/T_φ = 1/60 − 1/160 = (8 − 3)/480 = 5/480 = 1/96`, so `T_φ = 96 μs`. (b) The `T₁`-limit would be `T₂ = 2T₁ = 160 μs`; the measured `60 μs` is far below it, so no — pure dephasing (`T_φ = 96 μs`) dominates the coherence budget. (c) With `T₁ = 160 μs`: `1/T₂ = 1/320 + 1/96 = (3 + 10)/960 = 13/960`, so `T₂ = 960/13 ≈ 73.8 μs` — doubling `T₁` bought only a 23% improvement in `T₂`, quantifying why dephasing-limited devices need noise-source engineering rather than better relaxation times.
</details>

## Further Reading

1. **Nielsen & Chuang**, Chapter 9 — distance measures for quantum information; the canonical treatment of trace distance, fidelity, and their properties (note their unsquared fidelity convention, §9.2.2)
2. **Preskill**, Lecture Notes Chapter 3 (§3.5) — from Kraus operators to the Lindblad master equation, with the semigroup derivation done carefully; Chapter 2 covers the Helstrom bound
3. **Breuer & Petruccione**, *The Theory of Open Quantum Systems* (Oxford), Chapter 3 — the definitive physicist's treatment of quantum dynamical semigroups, the GKSL theorem, and microscopic derivations (Born–Markov, secular approximation) that this chapter only sketches
4. **Wilde**, *Quantum Information Theory*, Chapter 9 — trace distance and fidelity with full proofs, including Uhlmann's theorem and the Fuchs–van de Graaff inequalities; Chapter 4 for the channel formalism
5. **Jozsa**, "Fidelity for mixed quantum states" (J. Mod. Opt. 41, 1994) — the source of the squared-fidelity convention and its axiomatic justification; **Nielsen**, "A simple formula for the average gate fidelity of a quantum dynamical operation" (Phys. Lett. A 303, 2002) — the bridge between average gate fidelity and channel descriptions that underlies randomized benchmarking
6. **Gorini, Kossakowski & Sudarshan** (J. Math. Phys. 17, 1976) and **Lindblad** (Commun. Math. Phys. 48, 1976) — the original GKSL papers, for the historically curious
