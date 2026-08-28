# Perturbation Theory and Driven Systems

> **Prerequisites**: 06_wave_mechanics_and_schrodinger.md (stationary states, TISE), 07_harmonic_oscillator.md (ladder operators), 02_qubits_and_the_bloch_sphere.md (rotations, Pauli algebra), 01_postulates_of_quantum_mechanics.md
> **Connects to**: docs/07_quantum_hardware/01_superconducting_qubits.md — Rabi oscillations under a microwave drive are *how single-qubit gates are physically implemented*; docs/06_variational_quantum_algorithms (Hamiltonians we can only treat approximately); 05_density_matrices_and_open_systems.md (weak coupling to environments)

## Overview

Exactly solvable Hamiltonians — the well, the oscillator, hydrogen — are a measure-zero set. Everything else is handled by systematic approximation, and **perturbation theory** is the workhorse: split `Ĥ = Ĥ₀ + λV̂` into a solvable part plus a small correction, and expand energies and states in powers of `λ`.

This chapter covers both flavors. *Time-independent* perturbation theory corrects energy levels — it explains fine structure, the Zeeman and Stark effects, and (in its degenerate form) how perturbations split degenerate levels. *Time-dependent* perturbation theory handles transitions driven by external fields, culminating in Fermi's golden rule.

But the payoff most relevant to this curriculum is the problem where perturbation theory fails and an exact solution takes over: the **driven two-level system**. A resonant drive doesn't nudge a qubit — it swings it fully between `|0⟩` and `|1⟩` in coherent **Rabi oscillations**. Turn the drive on for exactly half a cycle and you have executed an `X` gate. Every microwave pulse sent to a transmon, every laser pulse addressing a trapped ion (Chapter 7.1, 7.2) is engineering the Rabi problem solved here.

## Time-Independent Perturbation Theory

### Setup and the non-degenerate expansion

Let `Ĥ = Ĥ₀ + λV̂` with known spectrum `Ĥ₀|n⁰⟩ = E_n⁰|n⁰⟩`, assumed non-degenerate for now. Expand

`E_n = E_n⁰ + λE_n¹ + λ²E_n² + …`,  `|n⟩ = |n⁰⟩ + λ|n¹⟩ + …`

Insert into `Ĥ|n⟩ = E_n|n⟩` and match powers of `λ`.

**First-order energy** (project the `λ¹` equation onto `⟨n⁰|`):

`E_n¹ = ⟨n⁰|V̂|n⁰⟩`

— the average of the perturbation in the unperturbed state. Cheap and remarkably effective.

**First-order state** (project onto `⟨m⁰|`, `m ≠ n`):

`|n¹⟩ = Σ_{m≠n} [⟨m⁰|V̂|n⁰⟩ / (E_n⁰ − E_m⁰)] |m⁰⟩`

The perturbation mixes in other states, weighted by coupling over energy distance. Nearby levels mix strongly — the warning sign that the expansion is in trouble when levels approach.

**Second-order energy**:

`E_n² = Σ_{m≠n} |⟨m⁰|V̂|n⁰⟩|² / (E_n⁰ − E_m⁰)`

Two universal consequences: the **ground state is always pushed down** at second order (every denominator is negative), and **levels repel** — two coupled levels push each other apart. Level repulsion is ubiquitous: it is the avoided crossing seen in every qubit spectroscopy experiment.

### Degenerate perturbation theory

If `E_n⁰` is degenerate, the formula for `|n¹⟩` divides by zero. The fix: within the `g`-dimensional degenerate subspace, the perturbation itself decides the correct basis. Diagonalize the `g×g` matrix `V_{ij} = ⟨i⁰|V̂|j⁰⟩` (the **secular equation**); its eigenvalues are the first-order energy shifts, and its eigenvectors are the correct zeroth-order states.

**Worked 2×2 secular example.** Let `Ĥ₀` have a doubly degenerate level `E⁰` with basis `{|1⟩, |2⟩}`, and let the perturbation couple them:

`V = [[0, Δ], [Δ, 0]]`  (i.e. `⟨1|V̂|1⟩ = ⟨2|V̂|2⟩ = 0`, `⟨1|V̂|2⟩ = Δ`)

The secular equation `det(V − E¹ I) = (E¹)² − Δ² = 0` gives `E¹ = ±Δ`. The degeneracy splits symmetrically, and the correct zeroth-order states are

`|±⟩ = (|1⟩ ± |2⟩)/√2`,  `E_± = E⁰ ± λΔ`

This tiny calculation is everywhere: tunneling between two degenerate wells splits symmetric/antisymmetric combinations (the ammonia maser, flux-qubit persistent-current states), the `H₂⁺` bonding/antibonding orbitals, and the qubit `{|+⟩, |−⟩}` basis emerging as eigenstates of an `X`-type coupling.

## Time-Dependent Perturbation Theory

### Interaction picture

Now let `Ĥ = Ĥ₀ + V̂(t)`. Move to the **interaction picture**, which strips off the known evolution:

`|ψ_I(t)⟩ = e^{iĤ₀t/ℏ}|ψ(t)⟩`,  `V̂_I(t) = e^{iĤ₀t/ℏ} V̂(t) e^{−iĤ₀t/ℏ}`

Then `iℏ d|ψ_I⟩/dt = V̂_I(t)|ψ_I⟩` — all remaining dynamics is due to the perturbation. Expanding `|ψ_I⟩ = Σ_n c_n(t)|n⁰⟩` gives exact coupled equations

`iℏ ċ_m = Σ_n ⟨m|V̂(t)|n⟩ e^{iω_{mn}t} c_n`,  `ω_{mn} = (E_m⁰ − E_n⁰)/ℏ`

### First-order transition amplitude

If the system starts in `|i⟩` and the perturbation is weak, set `c_n ≈ δ_{ni}` on the right and integrate:

`c_f^{(1)}(t) = (1/iℏ) ∫₀^t dt' ⟨f|V̂(t')|i⟩ e^{iω_{fi}t'}`

The transition amplitude is the **Fourier component of the perturbation at the transition frequency** `ω_{fi}`. A drive transfers population efficiently only when it oscillates at (near) the Bohr frequency of the transition — the principle of all spectroscopy, and of frequency-selective qubit addressing.

### Fermi's golden rule

For a harmonic perturbation `V̂(t) = V̂e^{−iωt} + V̂†e^{+iωt}` acting for a long time, `|c_f|²` develops a sharply peaked `sinc²` factor centered on resonance, which for large `t` approaches `(2πt/ℏ)δ(E_f − E_i − ℏω)`. Transitions into a continuum of final states with density `ρ(E_f)` then occur at the constant rate

`Γ_{i→f} = (2π/ℏ) |⟨f|V̂|i⟩|² ρ(E_f)`

**Fermi's golden rule**: rate = coupling squared times density of states. It governs spontaneous emission, photoionization, and — centrally for this curriculum — **qubit relaxation**: a qubit weakly coupled to a continuum of environmental modes decays at a golden-rule rate, `1/T₁ = (2π/ℏ)|coupling|²ρ(ω_q)`. This is why hardware designers filter and impedance-engineer the qubit's electromagnetic environment (Purcell filters): reduce `ρ(ω_q)` and you increase `T₁` (Chapters 2.5, 7.1).

## The Rabi Problem: A Driven Two-Level System

### Setup

Take a qubit `Ĥ₀ = (ℏω_q/2)(−Z)` (so `|0⟩` is the ground state, transition frequency `ω_q`) driven by an oscillating field coupling through `X`:

`Ĥ(t) = −(ℏω_q/2)Z + ℏΩ cos(ω_d t) X`

`Ω` is the **drive amplitude** (units of angular frequency, set by field strength times dipole/charge matrix element) and `ω_d` the drive frequency. This is precisely a microwave tone on a transmon's drive line or a laser on an ion.

### Rotating frame and the rotating-wave approximation

Transform to the frame rotating at `ω_d` (interaction picture with respect to `−(ℏω_d/2)Z`). The drive term splits into a static part and a part oscillating at `2ω_d`. Provided `Ω, |Δ| ≪ ω_d`, the fast term averages to nothing — the **rotating-wave approximation (RWA)** — leaving the time-independent rotating-frame Hamiltonian

`Ĥ_RWA = (ℏΔ/2)Z + (ℏΩ/2)X`,  `Δ = ω_d − ω_q` (detuning)

(Dropping the "counter-rotating" term shifts levels slightly — the Bloch–Siegert shift `~ Ω²/4ω_d` — negligible for typical transmon parameters where `Ω/ω_q ~ 10⁻³`.)

### Exact solution: Rabi's formula

`Ĥ_RWA` is a static field of magnitude `(ℏ/2)√(Ω² + Δ²)` pointing along `(Ω, 0, Δ)` on the Bloch sphere. The state simply precesses about this axis (Chapter 2.2) at the **generalized Rabi frequency**

`Ω_R = √(Ω² + Δ²)`

Starting in `|0⟩`, the excited-state population is **Rabi's formula**:

`P_1(t) = (Ω²/Ω_R²) sin²(Ω_R t / 2)`

Read it on the Bloch sphere: the Bloch vector, starting at the north pole, cones around the tilted axis.

- **On resonance** (`Δ = 0`): the axis is the equatorial `x`-axis, `P_1(t) = sin²(Ωt/2)` reaches 1 — complete, coherent population transfer, no matter how weak `Ω`. Perturbation theory could never show this; the drive's effect is *cumulative*, not small.
- **Detuned**: the axis tilts toward the pole; oscillations are faster (`Ω_R > Ω`) but shallower, with maximum `P_1 = Ω²/(Ω² + Δ²)` — a Lorentzian lineshape in `Δ`. Sweeping `ω_d` and watching `P_1` *is* qubit spectroscopy.
- **First-order check**: for short times or large detuning, expanding reproduces the first-order perturbative amplitude — the exact solution contains the golden-rule regime.

### Pulses are gates

Turn the resonant drive on for a chosen duration `t`, and the qubit rotates about the `x`-axis by angle `θ = Ωt`:

- `Ωt = π` (**π-pulse**): `|0⟩ → |1⟩` — an `X` gate
- `Ωt = π/2`: an `X(π/2)` gate, creating `(|0⟩ − i|1⟩)/√2` — the workhorse of Ramsey interferometry
- Drive phase chooses the rotation axis in the `x–y` plane (`cos(ω_d t + φ)` drives about `cos φ x̂ + sin φ ŷ`), so `Y`-rotations are just phase-shifted pulses, and `Z`-rotations can be done in software by reframing subsequent pulse phases ("virtual Z")

This is the literal implementation of the single-qubit gates of Chapter 3, and the calibration language of Chapter 7.1: "amplitude and duration of the π-pulse" means exactly `Ωt = π`.

## Key Formulas

- First order: `E_n¹ = ⟨n⁰|V̂|n⁰⟩`; state mixing `|n¹⟩ = Σ_{m≠n} ⟨m⁰|V̂|n⁰⟩/(E_n⁰−E_m⁰) |m⁰⟩`
- Second order: `E_n² = Σ_{m≠n} |⟨m⁰|V̂|n⁰⟩|²/(E_n⁰−E_m⁰)`; ground state moves down; levels repel
- Degenerate PT: diagonalize `V_{ij}` in the degenerate subspace; 2×2 off-diagonal case splits by `±|Δ|` into `(|1⟩±|2⟩)/√2`
- First-order amplitude: `c_f(t) = (1/iℏ)∫₀^t dt' ⟨f|V̂(t')|i⟩ e^{iω_{fi}t'}`
- Fermi's golden rule: `Γ = (2π/ℏ)|⟨f|V̂|i⟩|² ρ(E_f)`
- RWA Hamiltonian: `Ĥ = (ℏΔ/2)Z + (ℏΩ/2)X`, `Δ = ω_d − ω_q`
- Rabi frequency: `Ω_R = √(Ω² + Δ²)`; Rabi formula `P_1(t) = (Ω²/Ω_R²) sin²(Ω_R t/2)`
- π-pulse: `t_π = π/Ω` (resonant) implements `X`

## Worked Example: Driving a Transmon

**Problem**: A transmon qubit (`ω_q/2π = 5 GHz`) is driven with amplitude `Ω/2π = 20 MHz`. (a) On resonance (`Δ = 0`): find `Ω_R`, the π-pulse duration, and `P_1(t_π)`. (b) Repeat for detuning `Δ/2π = 20 MHz`: find `Ω_R`, the maximum of `P_1`, and `P_1` at `t = 10 ns`. (c) Sanity-check the RWA.

**Solution**:

**(a) Resonant drive.** `Ω = 2π × 20 MHz = 1.257×10⁸ rad/s`. With `Δ = 0`:

`Ω_R = √(Ω² + 0) = Ω`,  so `Ω_R/2π = 20 MHz`

π-pulse: `t_π = π/Ω_R = π/(2π × 20 MHz) = 1/(2 × 20 MHz) = 25.0 ns`

`P_1(t_π) = (Ω²/Ω_R²) sin²(Ω_R t_π/2) = 1 × sin²(π/2) = 1.000000` — complete inversion. (Verified numerically: `t_π = 25.000 ns`, `P_1 = 1.000000`.) A 25 ns `X` gate at 20 MHz drive is exactly the parameter regime of production transmon devices, where single-qubit gates run 15–40 ns.

**(b) Detuned drive.** `Δ = 2π × 20 MHz`:

`Ω_R = √(Ω² + Δ²) = Ω√2`,  `Ω_R/2π = 28.28 MHz`

Maximum population: `P_1^max = Ω²/Ω_R² = 1/2 = 0.500` — the qubit never gets more than halfway to `|1⟩`; the Bloch vector cones at 45° about the tilted axis.

At `t = 10 ns`: `Ω_R t/2 = ½ × 2π × 28.28 MHz × 10 ns = 0.8886 rad`, so

`P_1 = 0.5 × sin²(0.8886) = 0.5 × 0.6024 = 0.3012`

Cross-check by direct numerical integration (RK4) of `iℏ ċ = Ĥ_RWA c` from `c = (1,0)`: `P_1(10 ns) = 0.301224` vs formula `0.301224` — exact agreement, as it must be since Rabi's formula is the exact solution of the RWA Hamiltonian.

**(c) RWA validity.** `Ω/ω_q = 20 MHz / 5 GHz = 4×10⁻³ ≪ 1`; the neglected counter-rotating term produces a Bloch–Siegert shift of order `Ω²/4ω_q ~ 2π × 20 kHz`, four orders below `Ω`. The RWA is excellent — though for the fastest gates (`Ω/2π ≳ 100 MHz`) and for pulse-shaping against leakage to the transmon's `|2⟩` state, hardware calibration does correct for such terms (DRAG pulses, Chapter 7.1).

## Summary

- Time-independent PT: `E¹ = ⟨n⁰|V̂|n⁰⟩`, `E² = Σ|V_{mn}|²/(E_n⁰−E_m⁰)`; states mix as coupling/energy-gap; the ground state descends and levels repel
- Degenerate levels require diagonalizing `V̂` within the degenerate subspace first; the off-diagonal 2×2 case splits `E⁰ ± Δ` with eigenstates `(|1⟩±|2⟩)/√2`
- The interaction picture isolates the perturbation's effect; to first order, transitions are driven by the Fourier component of `V̂(t)` at the Bohr frequency `ω_{fi}`
- Fermi's golden rule `Γ = (2π/ℏ)|V_{fi}|²ρ(E_f)` gives constant decay rates into continua — the origin of `T₁` and the logic of Purcell engineering
- The resonantly driven two-level system escapes perturbation theory: in the RWA rotating frame it is a static Bloch-sphere rotation at `Ω_R = √(Ω²+Δ²)`, with `P_1(t) = (Ω²/Ω_R²)sin²(Ω_R t/2)`
- Pulse area is rotation angle: `Ωt = π` is an `X` gate, `Ωt = π/2` a quarter turn (half of a π-pulse), drive phase sets the axis — this is how quantum gates are physically executed on superconducting and atomic hardware

## Exercises

**Exercise 1**: A harmonic oscillator is perturbed by `V̂ = εx̂`. Compute the exact spectrum and show second-order perturbation theory gives it exactly.

<details><summary>Solution</summary>

Exact: complete the square, `½mω²x² + εx = ½mω²(x + ε/mω²)² − ε²/2mω²` — a shifted oscillator, so `E_n = ℏω(n+½) − ε²/(2mω²)` for all `n`.

PT: `x̂ = √(ℏ/2mω)(â+â†)` couples `|n⟩` only to `|n±1⟩`, so `E¹ = ⟨n|εx̂|n⟩ = 0`. Second order:

`E² = ε²(ℏ/2mω)[ |⟨n+1|â†|n⟩|²/(−ℏω) + |⟨n−1|â|n⟩|²/(+ℏω) ] = ε²(ℏ/2mω)(1/ℏω)[n − (n+1)] = −ε²/(2mω²)`

matching exactly; all higher orders vanish. This linear-drive shift is also the classical statement that displacing an oscillator doesn't change its frequency.
</details>

**Exercise 2**: For `Ĥ₀ = diag(0, ℏδ)` and `V = [[0, v],[v, 0]]` with `v = 0.1ℏδ`, compare the second-order ground-state energy with the exact eigenvalue.

<details><summary>Solution</summary>

Exact: `E_∓ = (ℏδ/2)[1 ∓ √(1 + 4v²/ℏ²δ²)]`; ground state `E_− = (ℏδ/2)(1 − √1.04) = −0.009902 ℏδ`.

PT: `E¹ = 0`, `E² = |v|²/(0 − ℏδ) = −0.01 ℏδ`.

Agreement to 1% — the error is `O(v⁴/δ³)`, the next term in the expansion of the square root: `E_− = −v²/ℏδ + v⁴/(ℏδ)³ − …`. (Numerical check: exact `−0.009902`, second-order `−0.010000`.) When `v ~ ℏδ` the series is useless and the 2×2 must be diagonalized exactly — that crossover is precisely the transition from the perturbative to the degenerate/secular regime.
</details>

**Exercise 3**: Two degenerate states are coupled by `V = [[ε, Δ],[Δ, −ε]]`. Find the first-order splittings and eigenstates, and discuss the limits `ε ≫ Δ` and `Δ ≫ ε`.

<details><summary>Solution</summary>

`V = εZ' + ΔX'` in Pauli form (in the degenerate basis), so eigenvalues are `±√(ε² + Δ²)` — total splitting `2√(ε²+Δ²)`. Eigenstates: mixing angle `tan θ = Δ/ε`, with `|+⟩ = cos(θ/2)|1⟩ + sin(θ/2)|2⟩`, etc.

`ε ≫ Δ`: eigenstates ≈ `|1⟩, |2⟩` — the original basis survives, energies `≈ ±(ε + Δ²/2ε)` (level repulsion at second order in `Δ`). `Δ ≫ ε`: eigenstates ≈ `(|1⟩±|2⟩)/√2`, splitting `≈ ±Δ` — the coupling picks the symmetric/antisymmetric combinations. Note this is the same algebra as the Rabi problem's `(Δ/2)Z + (Ω/2)X`: an avoided crossing swept through by tuning `ε` is qubit spectroscopy in disguise.
</details>

**Exercise 4**: Using Rabi's formula, find the drive detuning at which a would-be π-pulse (duration calibrated on resonance, `t_π = π/Ω`) instead leaves `P_1 = 0` — the first "zero" of the detuned Rabi pattern.

<details><summary>Solution</summary>

`P_1(t_π) = (Ω²/Ω_R²) sin²(Ω_R t_π/2)` vanishes when `Ω_R t_π = 2πk`, i.e. `Ω_R = 2kΩ`. With `Ω_R² = Ω² + Δ²`: `Δ = Ω√(4k² − 1)`; the first zero is `Δ = √3 Ω`. For `Ω/2π = 20 MHz`, `Δ/2π = 34.6 MHz`: a qubit detuned by 34.6 MHz sees this π-pulse as (approximately) the identity. Frequency-selective addressing in multi-qubit chips exploits exactly these zeros — and pulse shaping (Gaussian rather than square envelopes) pushes off-resonant excitation down further.
</details>

**Exercise 5**: A qubit couples to an environment whose noise at the qubit frequency has spectral density `S(ω_q)`, with `1/T₁ ∝ S(ω_q)` by Fermi's golden rule. Its relaxation is measured at `T₁ = 100 μs`. The design is changed so the density of environmental modes at `ω_q` drops by a factor of 5 while the coupling matrix element is halved. Predict the new `T₁`.

<details><summary>Solution</summary>

Golden rule: `Γ = (2π/ℏ)|M|²ρ`. New rate: `Γ' = Γ × (1/2)² × (1/5) = Γ/20`. So `T₁' = 20 × 100 μs = 2 ms`.

This is not hypothetical arithmetic — Purcell filters do exactly this: they reshape the impedance seen by the qubit so that `ρ(ω)` is large at the readout frequency (fast measurement) but suppressed at `ω_q` (long `T₁`). Golden-rule reasoning is the daily language of coherence engineering (Chapter 7.1, 7.4).
</details>

## Further Reading

1. **Griffiths & Schroeter**, *Introduction to Quantum Mechanics* (3rd ed.), Chapters 7 and 11 — time-independent (including degenerate) and time-dependent PT, with the two-level system and golden rule
2. **Shankar**, *Principles of Quantum Mechanics* (2nd ed.), Chapters 17–18 — perturbation theory with full derivations, hydrogen fine structure as the extended application, and transition rates
3. **Sakurai & Napolitano**, *Modern Quantum Mechanics* (3rd ed.), Chapter 5 — approximation methods in Dirac notation: the interaction picture, exact Rabi solution (§5.5), and Fermi's golden rule with scattering applications
4. **Cohen-Tannoudji, Diu & Laloë**, *Quantum Mechanics*, Vol. II, Chapters XI–XIII — stationary PT, the fine and hyperfine structure of hydrogen worked in detail, and time-dependent methods; Complement F_XIII treats the driven two-level atom
5. **Krantz et al.**, "A Quantum Engineer's Guide to Superconducting Qubits", *Applied Physics Reviews* 6, 021318 (2019), §4 — the bridge from this chapter to the lab: rotating frames, RWA, Rabi driving, DRAG pulses, and virtual-Z gates exactly as used on transmons
