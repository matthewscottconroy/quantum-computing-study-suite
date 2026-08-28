# Wave Mechanics and the Schrödinger Equation

> **Prerequisites**: 01_postulates_of_quantum_mechanics.md (state vectors, observables, unitary evolution), 03_quantum_measurements.md (projective measurement, Born rule), 01_mathematical_foundations (Hilbert spaces, Hermitian operators)
> **Connects to**: 07_harmonic_oscillator.md (the next continuous-variable system), 09_perturbation_theory.md (approximation methods built on stationary states), docs/07_quantum_hardware (real qubits live in continuous potentials — a transmon is an anharmonic well)

## Overview

Everything in this curriculum so far has lived in finite-dimensional Hilbert spaces: qubits are `ℂ²`, registers are `(ℂ²)^⊗n`. But the physical systems that host qubits — electrons in atoms, currents in superconducting circuits, motional modes of trapped ions — live in the **infinite-dimensional** Hilbert space of a particle moving in one or more continuous dimensions. This chapter extends the postulates from Chapter 2.1 to that setting.

The translation dictionary is simple but profound. The state `|ψ⟩` is now expanded not in a discrete basis `{|0⟩, |1⟩}` but in a continuum of position eigenstates `{|x⟩}`. The expansion coefficients form a function, the **wavefunction** `ψ(x) = ⟨x|ψ⟩`. Inner products become integrals, matrices become differential operators, and the abstract evolution equation `iℏ d|ψ⟩/dt = Ĥ|ψ⟩` becomes a partial differential equation — the **Schrödinger equation** — whose solutions exhibit the interference, quantization, and tunneling that make quantum mechanics famous.

Nothing conceptually new is required: the postulates are identical. What is new is the machinery — Fourier transforms connecting position and momentum, boundary conditions producing discrete energy levels, and wave packets showing how classical motion emerges.

## Position and Momentum Representations

### Continuous bases

The position operator `x̂` has a continuum of eigenstates, `x̂|x⟩ = x|x⟩`, normalized with the Dirac delta instead of the Kronecker delta:

`⟨x|x'⟩ = δ(x − x')`,  `∫ dx |x⟩⟨x| = 1`

Expanding a state in this basis gives the wavefunction:

`|ψ⟩ = ∫ dx ψ(x)|x⟩`,  where `ψ(x) = ⟨x|ψ⟩`

The Born rule (Chapter 2.3) now reads: `|ψ(x)|² dx` is the probability of finding the particle in `[x, x+dx]`. Normalization is `∫ |ψ(x)|² dx = 1`. Inner products become `⟨φ|ψ⟩ = ∫ φ*(x)ψ(x) dx` — the Hilbert space is `L²(ℝ)`.

The momentum operator `p̂` likewise has eigenstates `p̂|p⟩ = p|p⟩` with `⟨p|p'⟩ = δ(p − p')`. Its action in the position representation is a derivative:

`⟨x|p̂|ψ⟩ = −iℏ (d/dx) ψ(x)`

This follows from `p̂` being the generator of spatial translations, exactly as `Ĥ` generates time translations. The two operators satisfy the **canonical commutation relation**:

`[x̂, p̂] = iℏ`

This is the infinite-dimensional replacement for relations like `[X, Y] = 2iZ`. It cannot be realized by finite matrices (take the trace of both sides: the left side gives 0, the right gives `iℏ · dim` — contradiction). Continuous variables are irreducibly infinite-dimensional.

### The plane-wave overlap

Solving `−iℏ (d/dx)⟨x|p⟩ = p⟨x|p⟩` gives the central formula of wave mechanics:

`⟨x|p⟩ = e^{ipx/ℏ} / √(2πℏ)`

A momentum eigenstate is a plane wave of wavelength `λ = 2πℏ/p = h/p` — the de Broglie relation. The change of basis between the position and momentum representations is therefore the Fourier transform:

`ψ̃(p) = ⟨p|ψ⟩ = ∫ dx ⟨p|x⟩⟨x|ψ⟩ = (1/√(2πℏ)) ∫ dx e^{−ipx/ℏ} ψ(x)`

`|ψ̃(p)|² dp` is the probability of measuring momentum in `[p, p+dp]`. The Fourier reciprocity between a function and its transform is the origin of the Heisenberg uncertainty relation `Δx·Δp ≥ ℏ/2`: a state sharply localized in `x` is necessarily broad in `p`, and vice versa.

## The Schrödinger Equation

### Time-dependent form

For a particle of mass `m` in a potential `V(x)`, the Hamiltonian is `Ĥ = p̂²/(2m) + V(x̂)`. Projecting the abstract evolution postulate `iℏ (d/dt)|ψ⟩ = Ĥ|ψ⟩` onto `⟨x|` gives the **time-dependent Schrödinger equation (TDSE)**:

`iℏ ∂ψ(x,t)/∂t = −(ℏ²/2m) ∂²ψ(x,t)/∂x² + V(x)ψ(x,t)`

This is linear (superposition holds), first-order in time (the wavefunction now determines the entire future), and norm-preserving (evolution is unitary: `U(t) = e^{−iĤt/ℏ}`).

### Probability current

Local conservation of probability follows from the TDSE. Define the density `ρ(x,t) = |ψ(x,t)|²` and the **probability current**

`j(x,t) = (ℏ/m) Im[ψ* ∂ψ/∂x] = (ℏ/2mi)(ψ* ∂ψ/∂x − ψ ∂ψ*/∂x)`

Then a short computation using the TDSE gives the continuity equation:

`∂ρ/∂t + ∂j/∂x = 0`

Probability is not just globally conserved — it flows. For a plane wave `ψ = A e^{ikx}`, `j = |A|² ℏk/m = |A|² v`: density times velocity, as expected. The current is the right tool for defining transmission and reflection coefficients in scattering and tunneling problems.

### Time-independent form and stationary states

When `Ĥ` is time-independent, separation of variables `ψ(x,t) = φ(x) e^{−iEt/ℏ}` reduces the TDSE to the **time-independent Schrödinger equation (TISE)** — the eigenvalue problem for `Ĥ`:

`−(ℏ²/2m) φ''(x) + V(x)φ(x) = E φ(x)`,  i.e.  `Ĥ|φ⟩ = E|φ⟩`

Solutions `φ_n(x)` with energies `E_n` are **stationary states**: their probability density `|φ_n(x)e^{−iE_n t/ℏ}|² = |φ_n(x)|²` never changes. All time dependence in quantum mechanics comes from *superpositions* of stationary states, whose relative phases rotate at the Bohr frequencies `ω_{mn} = (E_m − E_n)/ℏ`:

`ψ(x,t) = Σ_n c_n φ_n(x) e^{−iE_n t/ℏ}`

This is the spectral decomposition of `e^{−iĤt/ℏ}` — the same structure used throughout the finite-dimensional chapters, now with wavefunctions as the eigenvectors.

## The Infinite Square Well

The simplest bound-state problem: `V(x) = 0` for `0 < x < L`, `V = ∞` outside. The wavefunction must vanish at the walls. Inside, the TISE is `φ'' = −k²φ` with `k = √(2mE)/ℏ`, so `φ(x) = A sin(kx) + B cos(kx)`. The boundary condition `φ(0) = 0` kills the cosine; `φ(L) = 0` forces `kL = nπ`. Quantization emerges purely from boundary conditions:

`E_n = n²π²ℏ² / (2mL²)`,  `n = 1, 2, 3, …`

`φ_n(x) = √(2/L) sin(nπx/L)`

Key features:

- **Zero-point energy**: the lowest energy is `E_1 > 0`, not zero — confinement to `Δx ~ L` forces `Δp ~ ℏ/L`, hence kinetic energy `~ ℏ²/(2mL²)`.
- **Orthonormality**: `∫₀^L φ_m(x)φ_n(x) dx = δ_{mn}` (a standard trigonometric integral). The `{φ_n}` form a complete basis for `L²([0,L])` — this is exactly a Fourier sine series.
- **Node counting**: `φ_n` has `n − 1` interior nodes. More nodes = more curvature = higher kinetic energy. This node theorem holds for all 1D bound states.
- **Spectrum grows as `n²`**: level spacing increases with `n`, unlike the harmonic oscillator's uniform ladder (next chapter).

### The finite square well (qualitatively)

Replace the infinite walls by a finite depth `V₀`. Now the wavefunction does not vanish at the walls; it decays exponentially into the classically forbidden region as `e^{−κ|x|}` with `κ = √(2m(V₀−E))/ℏ`. Consequences:

- There are finitely many bound states (a deep/wide well holds many, but even an arbitrarily shallow 1D well holds at least one).
- Energies are shifted *below* the infinite-well values: the wavefunction spreads slightly into the walls, effectively enlarging the box.
- Above `V₀` the spectrum is continuous — scattering states.
- The exponential tails in the forbidden region are the seed of tunneling.

## Free Particles and Wave Packets

For `V = 0`, energy eigenstates are the plane waves `e^{ikx}` with `E = ℏ²k²/(2m)`. They are not normalizable — physical states are **wave packets**, superpositions

`ψ(x,t) = (1/√(2πℏ)) ∫ dp ψ̃(p) e^{i(px − E(p)t)/ℏ}`

Two velocities appear:

- **Phase velocity** `v_p = ω/k = ℏk/(2m)` — the speed of individual crests (not physical for a massive particle).
- **Group velocity** `v_g = dω/dk = ℏk/m = p/m` — the speed of the packet's envelope, which equals the classical velocity. This is Ehrenfest's theorem in action: `d⟨x⟩/dt = ⟨p⟩/m`.

Because `ω(k) ∝ k²` is not linear, the packet **disperses**: a Gaussian packet of initial width `σ` spreads as `σ(t) = σ√(1 + (ℏt/2mσ²)²)`. Localized particles do not stay localized — another way infinite dimensions differ from a qubit's tidy Bloch sphere.

## Tunneling Through a Rectangular Barrier

Consider a barrier `V(x) = V₀` for `0 < x < a`, zero elsewhere, and a particle incident from the left with `E < V₀`. Classically it always reflects. Quantum mechanically the wavefunction inside the barrier is a decaying exponential, `e^{±κx}` with

`κ = √(2m(V₀ − E)) / ℏ`

Matching `ψ` and `ψ'` at both edges and comparing the transmitted to the incident probability current gives the **transmission coefficient**:

`T = [1 + (V₀² sinh²(κa)) / (4E(V₀ − E))]^{−1}`

with `R = 1 − T`. In the *opaque barrier* limit `κa ≫ 1`, `sinh(κa) ≈ e^{κa}/2` and

`T ≈ (16E(V₀ − E)/V₀²) e^{−2κa}`

The exponential `e^{−2κa}` dominates everything: transmission is extraordinarily sensitive to barrier width and height. This sensitivity powers the scanning tunneling microscope, alpha decay, and — directly relevant to this curriculum — the **Josephson junction**, where Cooper pairs tunnel through an oxide barrier to create the nonlinear inductance at the heart of every superconducting qubit (Chapter 7.1).

For `E > V₀`, replace `sinh` by `sin` (with `κ → k' = √(2m(E−V₀))/ℏ`): transmission oscillates and hits `T = 1` at resonances `k'a = nπ` — the basis of the Ramsauer–Townsend effect.

## Key Formulas

- Position/momentum overlap: `⟨x|p⟩ = e^{ipx/ℏ}/√(2πℏ)`
- Canonical commutator: `[x̂, p̂] = iℏ`; uncertainty: `Δx·Δp ≥ ℏ/2`
- TDSE: `iℏ ∂ψ/∂t = −(ℏ²/2m)∂²ψ/∂x² + V(x)ψ`
- Probability current: `j = (ℏ/m) Im[ψ* ∂ψ/∂x]`, with `∂ρ/∂t + ∂j/∂x = 0`
- TISE: `Ĥφ = Eφ`; general solution `ψ(x,t) = Σ_n c_n φ_n(x) e^{−iE_n t/ℏ}`
- Infinite well: `E_n = n²π²ℏ²/(2mL²)`, `φ_n(x) = √(2/L) sin(nπx/L)`
- Group velocity: `v_g = dω/dk = p/m`
- Tunneling: `T = [1 + V₀² sinh²(κa)/(4E(V₀−E))]^{−1}`, `κ = √(2m(V₀−E))/ℏ`

## Worked Example: A Two-Level Superposition in a Box

**Problem**: An electron in an infinite well of width `L = 1 nm` is prepared in

`ψ(x, 0) = (φ₁(x) + φ₂(x))/√2`

(a) Find `E₁`, `E₂`, and the oscillation frequency of the probability density. (b) Show that `⟨x⟩(t)` oscillates and compute its amplitude and period numerically.

**Solution**:

**(a) Energies.** With `m = 9.109×10⁻³¹ kg`, `ℏ = 1.055×10⁻³⁴ J·s`, `L = 10⁻⁹ m`:

`E₁ = π²ℏ²/(2mL²) = 6.025×10⁻²⁰ J = 0.376 eV`

`E₂ = 4E₁ = 1.504 eV`,  so  `ΔE = E₂ − E₁ = 3E₁ = 1.128 eV`

The state evolves as `ψ(x,t) = [φ₁ e^{−iE₁t/ℏ} + φ₂ e^{−iE₂t/ℏ}]/√2`. Pulling out a global phase:

`|ψ(x,t)|² = ½[φ₁² + φ₂² + 2φ₁φ₂ cos(ω₂₁ t)]`,  `ω₂₁ = ΔE/ℏ`

Numerically `ω₂₁ = 3E₁/ℏ = 1.714×10¹⁵ rad/s`. Each stationary state alone would be static; the *superposition* sloshes.

**(b) Motion of `⟨x⟩`.** By symmetry `⟨φ_n|x̂|φ_n⟩ = L/2` for every `n`. The cross term needs

`⟨φ₁|x̂|φ₂⟩ = (2/L) ∫₀^L x sin(πx/L) sin(2πx/L) dx = −16L/(9π²)`

(verified numerically: `−0.180127 L` vs analytic `−16/(9π²) = −0.180127`). Therefore

`⟨x⟩(t) = L/2 − (16L/9π²) cos(ω₂₁ t)`

- **Amplitude**: `16L/(9π²) = 0.180 L = 0.180 nm` — the packet's centroid swings across 36% of the box.
- **Period**: `T = 2π/ω₂₁ = 2πℏ/ΔE = 3.67×10⁻¹⁵ s ≈ 3.7 fs`.

The electron's charge density oscillates at `ω₂₁/2π ≈ 273 THz` — an optical-frequency dipole. This is precisely the mechanism by which atoms emit light at Bohr frequencies, and (scaled to microwaves) how a transmon couples to its drive line.

## Summary

- Wave mechanics is the same postulate set in the continuous basis `{|x⟩}`: `ψ(x) = ⟨x|ψ⟩`, inner products are integrals, `p̂ = −iℏ d/dx`, and `[x̂,p̂] = iℏ` forces infinite dimensions
- `⟨x|p⟩ = e^{ipx/ℏ}/√(2πℏ)`: momentum eigenstates are plane waves, and the position↔momentum change of basis is the Fourier transform
- The TDSE is the position representation of `iℏ d|ψ⟩/dt = Ĥ|ψ⟩`; probability obeys a local continuity equation with current `j`
- Stationary states solve `Ĥφ = Eφ`; all dynamics comes from interference between stationary states at Bohr frequencies `(E_m − E_n)/ℏ`
- Infinite square well: `E_n = n²π²ℏ²/(2mL²)` with sine eigenfunctions — quantization from boundary conditions, zero-point energy from confinement
- Wave packets move at the group velocity `v_g = p/m` and disperse
- Tunneling through a barrier: `T ∝ e^{−2κa}` in the opaque limit — the physics behind Josephson junctions and hence superconducting qubits

## Exercises

**Exercise 1**: Show that `⟨x|p⟩ = e^{ipx/ℏ}/√(2πℏ)` satisfies both eigenvalue equation and normalization `⟨p|p'⟩ = δ(p−p')`.

<details><summary>Solution</summary>

Eigenvalue equation: `−iℏ (d/dx) e^{ipx/ℏ}/√(2πℏ) = −iℏ·(ip/ℏ)·e^{ipx/ℏ}/√(2πℏ) = p ⟨x|p⟩` ✓.

Normalization: `⟨p|p'⟩ = ∫ dx ⟨p|x⟩⟨x|p'⟩ = (1/2πℏ) ∫ dx e^{i(p'−p)x/ℏ}`. Substituting `u = x/ℏ` gives `(1/2π) ∫ du e^{i(p'−p)u} = δ(p'−p)`, using the Fourier representation of the delta function. The `1/√(2πℏ)` prefactor is exactly what makes this come out with unit coefficient. ✓
</details>

**Exercise 2**: A particle in the infinite well is in the ground state when the wall at `x = L` is suddenly moved to `x = 2L` (fast compared to all timescales). What is the probability of finding the particle in the ground state of the *new* well?

<details><summary>Solution</summary>

Sudden approximation: the wavefunction is unchanged, but the basis is new. The amplitude is `c₁ = ∫₀^L √(2/L) sin(πx/L) · √(2/2L) sin(πx/2L) dx` (the old wavefunction vanishes for `x > L`). Using `sin A sin B = ½[cos(A−B) − cos(A+B)]` with `A = πx/L`, `B = πx/2L`:

`c₁ = (√2/L) ∫₀^L ½[cos(πx/2L) − cos(3πx/2L)] dx = (√2/2L)[(2L/π)sin(π/2) − (2L/3π)sin(3π/2)] = (√2/π)(1 + 1/3) = 4√2/(3π)`

Probability: `P₁ = |c₁|² = 32/(9π²) ≈ 0.360`. About 36% — the rest is spread over excited states of the new well.
</details>

**Exercise 3**: Compute the probability current for `ψ(x) = A e^{ikx} + B e^{−ikx}` and interpret the result.

<details><summary>Solution</summary>

`j = (ℏ/m) Im[ψ* ψ']` with `ψ' = ik(Ae^{ikx} − Be^{−ikx})`. Expanding:

`ψ*ψ' = ik[|A|² − |B|² − A*B e^{−2ikx} + AB* e^{2ikx}]`

The last two terms are `ik·(2i Im[AB* e^{2ikx}])`, which is real, so it drops out of the imaginary part. Thus

`j = (ℏk/m)(|A|² − |B|²)`

The net current is the rightward flux `|A|²v` minus the leftward flux `|B|²v` — the interference cross-terms carry no net current. This justifies defining reflection as `R = |B|²/|A|²` in scattering problems.
</details>

**Exercise 4**: An electron hits a barrier with `V₀ = 1 eV`, `a = 1 nm`, carrying `E = 0.5 eV`. Compute `κ`, `κa`, and the transmission coefficient. Compare exact and opaque-limit formulas.

<details><summary>Solution</summary>

`κ = √(2m(V₀−E))/ℏ = √(2 · 9.109×10⁻³¹ · 0.5 · 1.602×10⁻¹⁹)/1.055×10⁻³⁴ = 3.623×10⁹ m⁻¹`, so `κa = 3.623`.

Exact: `T = [1 + V₀² sinh²(κa)/(4E(V₀−E))]^{−1}`. With `E(V₀−E) = 0.25 eV²`, `V₀² = 1 eV²`, `sinh(3.623) = 18.71`:

`T = [1 + 350.1/1]^{−1} = 2.85×10⁻³`

Opaque limit: `T ≈ 16·(0.25/1)·e^{−7.245} = 4·7.14×10⁻⁴ = 2.85×10⁻³`. The two agree to three digits because `κa ≫ 1`. Doubling the width to 2 nm multiplies `T` by `e^{−7.245} ≈ 7×10⁻⁴` — the exponential sensitivity that makes tunneling devices work.
</details>

**Exercise 5**: Prove that 1D bound states are non-degenerate.

<details><summary>Solution</summary>

Suppose `φ₁`, `φ₂` both solve the TISE with the same `E`. Then `φ₁φ₂'' − φ₂φ₁'' = 0`, i.e. `(φ₁φ₂' − φ₂φ₁')' = 0`, so the Wronskian `W = φ₁φ₂' − φ₂φ₁'` is constant. Bound states vanish at infinity, so `W = 0` everywhere. Then `φ₂'/φ₂ = φ₁'/φ₁` wherever both are nonzero, and integrating gives `ln φ₂ = ln φ₁ + const`, i.e. `φ₂ ∝ φ₁`: the same physical state. (This fails in 3D, where degeneracy is generic — see the hydrogen atom, Chapter 2.8.)
</details>

## Further Reading

1. **Griffiths & Schroeter**, *Introduction to Quantum Mechanics* (3rd ed.), Chapter 2 — the canonical first pass at the TISE: infinite/finite wells, free particle, delta-function well, all with full algebra
2. **Shankar**, *Principles of Quantum Mechanics* (2nd ed.), Chapters 1 and 5 — Chapter 1 builds the continuous-basis formalism (`|x⟩`, `|p⟩`, delta normalization) with unusual care; Chapter 5 solves the standard 1D problems in that language
3. **Sakurai & Napolitano**, *Modern Quantum Mechanics* (3rd ed.), §1.6–1.7 and §2.4–2.5 — position/momentum representations, propagators, and the path from bras and kets to wave mechanics
4. **Cohen-Tannoudji, Diu & Laloë**, *Quantum Mechanics*, Vol. I, Chapter I and Complements — wave packets, group velocity, and spreading treated more thoroughly than anywhere else at this level
5. **Feynman, Leighton & Sands**, *The Feynman Lectures on Physics*, Vol. III, Chapter 16 — the dependence of amplitudes on position and time, and how the Schrödinger equation emerges from the amplitude formalism
