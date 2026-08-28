# The Quantum Harmonic Oscillator

> **Prerequisites**: 06_wave_mechanics_and_schrodinger.md (TISE, stationary states, `[x̂,p̂] = iℏ`), 01_postulates_of_quantum_mechanics.md (operators, eigenstates)
> **Connects to**: docs/05_quantum_error_correction/08_bosonic_codes.md (cat and GKP codes live in the oscillator Hilbert space — this chapter is the prerequisite for that one), docs/07_quantum_hardware/01_superconducting_qubits.md (a transmon is a weakly anharmonic oscillator; readout resonators and cavities are literal QHOs), 09_perturbation_theory.md

## Overview

The harmonic oscillator is the most important solvable problem in quantum mechanics. Every potential minimum looks quadratic up close, so the QHO is the universal first approximation to molecules, crystals, and circuits. More importantly for this curriculum: **every mode of the electromagnetic field is a harmonic oscillator**. Microwave cavities, readout resonators, and the bosonic modes used for cat and GKP error-correcting codes (Chapter 5.8) are all described by exactly the mathematics of this chapter. A "photon" is nothing but one quantum of excitation of an oscillator mode.

We solve the problem twice. The first route — power series in the position representation — is honest wave mechanics and shows where Hermite polynomials come from. The second route — Dirac's ladder operators — is pure algebra, requiring nothing but `[x̂,p̂] = iℏ`, and is the version you will use everywhere: it is the language of creation and annihilation operators that underlies quantum optics, field theory, and bosonic codes. We finish with coherent states, the "most classical" oscillator states and the raw material of cat codes.

## The Problem and the Series Solution (Sketch)

The Hamiltonian for mass `m` and angular frequency `ω`:

`Ĥ = p̂²/(2m) + ½mω²x̂²`

In the position representation the TISE reads `−(ℏ²/2m)φ'' + ½mω²x²φ = Eφ`. Introduce the dimensionless variable `ξ = x/x₀` with the natural length `x₀ = √(ℏ/mω)`, and write `φ(ξ) = h(ξ) e^{−ξ²/2}` (the Gaussian handles the behavior at infinity). Then `h` satisfies the Hermite equation

`h'' − 2ξh' + (2E/ℏω − 1)h = 0`

A power-series solution `h = Σ aₖξᵏ` gives the recursion `a_{k+2} = [2k + 1 − 2E/ℏω] aₖ / [(k+1)(k+2)]`. For generic `E` the series behaves like `e^{ξ²}` at large `ξ` and the wavefunction blows up. Normalizability forces the series to **terminate**: `2E/ℏω − 1 = 2n` for some integer `n ≥ 0`, i.e.

`E_n = ℏω(n + ½)`

and `h(ξ)` becomes the Hermite polynomial `H_n(ξ)`. The normalized eigenfunctions are

`φ_n(x) = (mω/πℏ)^{1/4} (1/√(2ⁿ n!)) H_n(x/x₀) e^{−x²/2x₀²}`

with `H₀ = 1`, `H₁ = 2ξ`, `H₂ = 4ξ² − 2`, … The spectrum is an evenly spaced ladder with zero-point energy `ℏω/2` — confinement plus the uncertainty principle again. That even spacing is *why* a bare oscillator cannot be a qubit: a drive resonant with the `0→1` transition is equally resonant with `1→2`. The transmon fixes this by adding anharmonicity (Chapter 7.1).

## The Ladder-Operator Solution

### Defining â and â†

Define the dimensionless, non-Hermitian combinations

`â = √(mω/2ℏ) (x̂ + ip̂/mω)`,  `â† = √(mω/2ℏ) (x̂ − ip̂/mω)`

Inverting:

`x̂ = √(ℏ/2mω) (â + â†)`,  `p̂ = i√(mℏω/2) (â† − â)`

From `[x̂,p̂] = iℏ` follows the single most used commutator in physics:

`[â, â†] = 1`

Substituting into `Ĥ` and using the commutator to normal-order:

`Ĥ = ℏω(â†â + ½) = ℏω(N̂ + ½)`,  where `N̂ = â†â` is the **number operator**.

### Building the spectrum algebraically

Two commutators do all the work:

`[N̂, â] = −â`,  `[N̂, â†] = +â†`

So if `N̂|n⟩ = n|n⟩`, then `N̂(â|n⟩) = (n−1)(â|n⟩)` and `N̂(â†|n⟩) = (n+1)(â†|n⟩)`: `â` lowers and `â†` raises the excitation number by one — hence *annihilation* and *creation* operators, or collectively **ladder operators**.

The ladder must stop going down: `‖â|n⟩‖² = ⟨n|â†â|n⟩ = n ≥ 0`, so eigenvalues are non-negative, and lowering must eventually hit a state annihilated by `â`. That requires `n` to be a non-negative **integer**, with ground state `â|0⟩ = 0`. The normalizations follow from the same norm computation:

`â|n⟩ = √n |n−1⟩`,  `â†|n⟩ = √(n+1) |n+1⟩`

and the whole tower is built from the vacuum:

`|n⟩ = (â†)ⁿ/√(n!) |0⟩`,  `E_n = ℏω(n + ½)`

In the position representation, `â|0⟩ = 0` is the first-order ODE `(ξ + d/dξ)φ₀ = 0`, giving the Gaussian `φ₀ ∝ e^{−ξ²/2}` — the series solution recovered with almost no work. The states `|n⟩` are called **Fock states** or number states; in field-mode language, `|n⟩` is the `n`-photon state. Fock states are exactly the basis used to write down bosonic code words in Chapter 5.8.

### Expectation values in |n⟩

Because `â` and `â†` change `n` by one, `⟨n|â|n⟩ = ⟨n|â†|n⟩ = 0`, hence

`⟨x̂⟩ = ⟨p̂⟩ = 0` in every Fock state.

For the squares, expand and keep only number-conserving terms (`â†â` and `ââ†`):

`⟨n|x̂²|n⟩ = (ℏ/2mω)⟨n|ââ† + â†â|n⟩ = (ℏ/2mω)(2n+1)`

`⟨n|p̂²|n⟩ = (mℏω/2)(2n+1)`

So `Δx = √((2n+1)ℏ/2mω)`, `Δp = √((2n+1)mℏω/2)`, and

`Δx·Δp = (n + ½)ℏ`

Only the ground state saturates the Heisenberg bound `ℏ/2`; excited Fock states are increasingly "unclassical" (their Wigner functions have negative rings). Also note `⟨T⟩ = ⟨V⟩ = E_n/2` — the virial theorem.

## Coherent States

### Eigenstates of the annihilation operator

A **coherent state** `|α⟩` is defined by

`â|α⟩ = α|α⟩`,  `α ∈ ℂ`

(`â` is not Hermitian, so complex eigenvalues are allowed and `|α⟩` states are not orthogonal.) Expanding in Fock states and using `â|n⟩ = √n|n−1⟩` gives the recursion `c_n = α c_{n−1}/√n`, so

`|α⟩ = e^{−|α|²/2} Σ_n (αⁿ/√(n!)) |n⟩`

Equivalently, `|α⟩ = D̂(α)|0⟩` where the **displacement operator**

`D̂(α) = e^{αâ† − α*â}`

is a unitary that rigidly translates the oscillator in phase space: `D̂†(α) â D̂(α) = â + α`. Coherent states are displaced vacuum states.

### Properties

- **Poisson photon statistics**: `P(n) = |⟨n|α⟩|² = e^{−|α|²} |α|^{2n}/n!` — a Poisson distribution with mean `⟨n⟩ = |α|²` and variance `Var(n) = |α|²`, so `Δn = |α| = √⟨n⟩`. This is the photon-number distribution of an ideal laser.
- **Minimal uncertainty**: `Δx = √(ℏ/2mω)`, `Δp = √(mℏω/2)`, `Δx·Δp = ℏ/2` for *every* `α` — the same circle of vacuum noise, just displaced. Coherent states are the quantum states that most resemble a classical oscillation.
- **Classical dynamics**: under `Ĥ`, `|α⟩ → e^{−iωt/2}|αe^{−iωt}⟩` — a coherent state stays coherent, its label rotating in phase space at frequency `ω`, and `⟨x̂⟩(t) = √(2ℏ/mω) Re[α e^{−iωt}]` traces the classical trajectory exactly.
- **Overcompleteness**: `⟨β|α⟩ = e^{−|α−β|²/2} e^{i Im(β*α)}` — distinct coherent states overlap, but the overlap dies as `e^{−|α−β|²/2}`.

### Why this matters for bosonic codes

Chapter 5.8 (bosonic codes) builds qubits out of a single oscillator mode:

- **Cat codes** use superpositions of coherent states like `|α⟩ ± |−α⟩`. Their key resource is exactly the near-orthogonality above: for `|α|² ≳ 2`, `⟨−α|α⟩ = e^{−2|α|²}` is negligible, so `|±α⟩` act like a two-level system. Photon loss maps `â|α⟩ = α|α⟩` — coherent states are *eigenstates of the error operator*, which is why cat codes handle loss gracefully.
- **GKP codes** use superpositions of displaced squeezed states arranged on a grid in phase space, built entirely from `D̂(α)` and the `x̂, p̂` quadratures defined here.

Everything in that chapter — Fock-space expansions, displacement operators, quadratures, photon loss `â` — is the algebra of this chapter.

## Key Formulas

- Hamiltonian: `Ĥ = p̂²/2m + ½mω²x̂² = ℏω(â†â + ½)`; spectrum `E_n = ℏω(n + ½)`
- Ladder algebra: `[â,â†] = 1`, `â|n⟩ = √n|n−1⟩`, `â†|n⟩ = √(n+1)|n+1⟩`, `|n⟩ = (â†)ⁿ|0⟩/√(n!)`
- Quadratures: `x̂ = √(ℏ/2mω)(â+â†)`, `p̂ = i√(mℏω/2)(â†−â)`
- Fock-state moments: `⟨x̂⟩ = ⟨p̂⟩ = 0`, `⟨x̂²⟩ = (ℏ/2mω)(2n+1)`, `Δx·Δp = (n+½)ℏ`
- Coherent state: `â|α⟩ = α|α⟩`, `|α⟩ = D̂(α)|0⟩ = e^{−|α|²/2} Σ αⁿ/√(n!) |n⟩`
- Displacement: `D̂(α) = e^{αâ†−α*â}`, `D̂†âD̂ = â + α`
- Photon statistics: `P(n) = e^{−⟨n⟩}⟨n⟩ⁿ/n!`, `⟨n⟩ = |α|²`, `Δn = |α|`
- Ground-state length scale: `x₀ = √(ℏ/mω)`

## Worked Example: Moments via Ladder Algebra

**Problem**: Compute `⟨x̂²⟩` and the uncertainty product `Δx·Δp` (a) in the Fock state `|2⟩`, (b) in the coherent state `|α = 2⟩` (real `α`). Use only ladder algebra.

**Solution**:

Write `x̂ = u(â + â†)` with `u = √(ℏ/2mω)`, and `p̂ = iv(â† − â)` with `v = √(mℏω/2)`. Note `uv = ℏ/2`.

**(a) Fock state `|2⟩`.** Expand `x̂² = u²(â² + â†² + ââ† + â†â)`. The `â²` and `â†²` terms connect `|2⟩` to `|0⟩` and `|4⟩` — zero diagonal contribution. Using `ââ† = â†â + 1 = N̂ + 1`:

`⟨2|x̂²|2⟩ = u²⟨2|2N̂ + 1|2⟩ = u²(2·2 + 1) = 5u² = 5ℏ/(2mω)`

Identically `⟨2|p̂²|2⟩ = v²(2N̂+1) → 5v² = 5mℏω/2`. Since `⟨x̂⟩ = ⟨p̂⟩ = 0`:

`Δx·Δp = √(5u²)·√(5v²) = 5uv = 5ℏ/2 = (n + ½)ℏ` with `n = 2` ✓

Numerical check (60-level matrix truncation): `⟨2|(â+â†)²|2⟩ = 5.000000`, `⟨2|(i(â†−â))²|2⟩ = 5.000000`.

**(b) Coherent state `|α = 2⟩`.** Use the eigenvalue relation and its adjoint: `â|α⟩ = α|α⟩`, `⟨α|â† = ⟨α|α*`. With `α = 2` real:

`⟨x̂⟩ = u⟨α|â + â†|α⟩ = u(α + α*) = 4u`

For `x̂²`, normal-order using `ââ† = â†â + 1`:

`⟨x̂²⟩ = u²⟨â² + â†² + 2â†â + 1⟩ = u²(α² + α*² + 2|α|² + 1) = u²(4 + 4 + 8 + 1) = 17u² = 17ℏ/(2mω)`

Variance: `(Δx)² = ⟨x̂²⟩ − ⟨x̂⟩² = (17 − 16)u² = u² = ℏ/2mω` — the *vacuum* variance, independent of `α`. The same computation for `p̂` (with `α` real, `⟨p̂⟩ = 0`) gives `(Δp)² = v²`. Hence

`Δx·Δp = uv = ℏ/2`

— a minimum-uncertainty state, while sitting at a displaced position `⟨x̂⟩ = 4√(ℏ/2mω)`. Photon statistics: `⟨n⟩ = |α|² = 4`, `Var(n) = 4`, `Δn = 2`.

Numerical check (Fock expansion of `|α=2⟩` to 60 levels): norm `= 1.00000000`, `⟨â+â†⟩ = 4.000000`, `⟨(â+â†)²⟩ = 17.000000`, variance `= 1.000000`, `⟨n⟩ = 4.000000`, `Var(n) = 4.000000`. All match.

## Summary

- `Ĥ = ℏω(N̂ + ½)` with evenly spaced spectrum `E_n = ℏω(n+½)`; even spacing is why a linear oscillator can't be addressed as a qubit without anharmonicity
- The series solution yields Hermite-Gaussian eigenfunctions; the ladder method gets the same spectrum from `[â,â†] = 1` alone
- `â` and `â†` lower/raise Fock states: `â|n⟩ = √n|n−1⟩`, `â†|n⟩ = √(n+1)|n+1⟩`; the vacuum satisfies `â|0⟩ = 0`
- Fock states have `⟨x̂⟩ = ⟨p̂⟩ = 0` and `Δx·Δp = (n+½)ℏ` — only the vacuum is minimum-uncertainty
- Coherent states `|α⟩ = D̂(α)|0⟩` are eigenstates of `â` with Poissonian photon number (`⟨n⟩ = |α|²`, `Δn = |α|`), minimum uncertainty for all `α`, and exactly classical dynamics
- This chapter is the direct prerequisite for bosonic codes (Chapter 5.8): cat codes superpose coherent states, GKP codes superpose displaced states, and photon loss is the operator `â`

## Exercises

**Exercise 1**: Verify `[â, â†] = 1` directly from the definitions and `[x̂,p̂] = iℏ`.

<details><summary>Solution</summary>

Write `â = √(mω/2ℏ)(A + B)` and `â† = √(mω/2ℏ)(A − B)` with `A = x̂`, `B = ip̂/mω`. Using the bilinearity of the commutator, `[A+B, A−B] = −[A,B] + [B,A] = −2[A,B]`, so:

`[â,â†] = (mω/2ℏ)·(−2)[x̂, ip̂/mω] = (mω/2ℏ)·(−2i/mω)(iℏ) = (mω/2ℏ)(2ℏ/mω) = 1` ✓
</details>

**Exercise 2**: Compute `⟨0|x̂⁴|0⟩` using ladder algebra.

<details><summary>Solution</summary>

`x̂⁴ = u⁴(â+â†)⁴`. Sandwiched between `⟨0|` and `|0⟩`, a product of four ladder operators survives only if it has two raisings and two lowerings and never takes the state below the vacuum (reading right to left, it must start with `â†` and never dip negative). The two surviving orderings are `â â â† â†` (matrix-element chain `|0⟩ → |1⟩ → |2⟩ → |1⟩ → |0⟩`, value `√1·√2·√2·√1 = 2`) and `â â† â â†` (chain `|0⟩ → |1⟩ → |0⟩ → |1⟩ → |0⟩`, value `1`). Total `= 3`. So

`⟨x̂⁴⟩₀ = 3u⁴ = 3(ℏ/2mω)²`

consistent with Gaussian statistics: `⟨x⁴⟩ = 3⟨x²⟩²`. Numerical check with truncated matrices: `⟨0|(â+â†)⁴|0⟩ = 3.000000`.
</details>

**Exercise 3**: Show that under free evolution a coherent state remains coherent: `e^{−iĤt/ℏ}|α⟩ = e^{−iωt/2}|α e^{−iωt}⟩`.

<details><summary>Solution</summary>

Apply the propagator to the Fock expansion: `e^{−iĤt/ℏ}|α⟩ = e^{−|α|²/2} Σ (αⁿ/√(n!)) e^{−iω(n+½)t}|n⟩ = e^{−iωt/2} e^{−|α|²/2} Σ ((αe^{−iωt})ⁿ/√(n!))|n⟩`.

Since `|αe^{−iωt}| = |α|`, the prefactor `e^{−|α|²/2}` is also the correct normalization for the new label. Hence the state is `e^{−iωt/2}|αe^{−iωt}⟩`: the phase-space point rotates classically, the shape never changes. This is why coherent states are the pointer states of driven cavities.
</details>

**Exercise 4**: Compute the overlap `⟨−α|α⟩` for real `α`, and evaluate it for `α = 2`. Why does this matter for cat codes?

<details><summary>Solution</summary>

From the general formula `⟨β|α⟩ = e^{−|β|²/2 − |α|²/2 + β*α}` with `β = −α`:

`⟨−α|α⟩ = e^{−α²/2 − α²/2 − α²} = e^{−2α²}`

For `α = 2`: `e^{−8} ≈ 3.4×10⁻⁴`. The states `|α⟩` and `|−α⟩` are almost orthogonal, so the cat-code states `|C±⟩ ∝ |α⟩ ± |−α⟩` behave like an orthonormal qubit basis, with normalization corrections of order `e^{−2|α|²}` (see Chapter 5.8). Larger `|α|` means better orthogonality but faster photon loss — the central trade-off of cat qubits.
</details>

**Exercise 5**: A microwave resonator has frequency `ω/2π = 6 GHz`. Find the zero-point energy, the thermal occupation `n̄ = 1/(e^{ℏω/kT} − 1)` at `T = 15 mK`, and comment.

<details><summary>Solution</summary>

`ℏω = 6.626×10⁻³⁴ · 6×10⁹ J = 3.98×10⁻²⁴ J ≈ 24.8 μeV`; zero-point energy `ℏω/2 ≈ 12.4 μeV`.

`ℏω/kT = 3.98×10⁻²⁴/(1.381×10⁻²³ · 0.015) = 19.2`, so `n̄ = 1/(e^{19.2} − 1) ≈ 4.5×10⁻⁹`.

At dilution-refrigerator temperatures the mode is essentially in its vacuum state — the prerequisite for using cavities as quantum memories and for initializing bosonic qubits. At room temperature (`T = 300 K`), `ℏω/kT ≈ 10⁻³` and `n̄ ≈ 1000`: hopelessly classical. This is why superconducting quantum processors live in dilution refrigerators (Chapter 7.1).
</details>

## Further Reading

1. **Griffiths & Schroeter**, *Introduction to Quantum Mechanics* (3rd ed.), §2.3 — both the algebraic and analytic solutions, side by side, at the gentlest pace
2. **Shankar**, *Principles of Quantum Mechanics* (2nd ed.), Chapter 7 — the oscillator done thoroughly in both representations, plus the propagator; Chapter 21 (path integrals) revisits it
3. **Sakurai & Napolitano**, *Modern Quantum Mechanics* (3rd ed.), §2.3 — the ladder-operator treatment in Dirac notation, including time evolution and coherent states in the Heisenberg picture
4. **Cohen-Tannoudji, Diu & Laloë**, *Quantum Mechanics*, Vol. I, Chapter V and Complement G_V — the definitive coherent-state treatment: displacement operators, quasi-classical states, and their dynamics
5. **Gerry & Knight**, *Introductory Quantum Optics* (Cambridge), Chapters 2–3 — field quantization and coherent states in the photonic language used by bosonic codes and circuit QED
