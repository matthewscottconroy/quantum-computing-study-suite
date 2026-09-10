# Analysis for Quantum Mechanics

> **Prerequisites**: 01_linear_algebra.md (operators, spectral theorem, Pauli matrices), 02_complex_numbers_and_hilbert_spaces.md (Hilbert spaces, operator norms), single-variable calculus  
> **Connects to**: docs/02_quantum_mechanics/06_wave_mechanics_and_schrodinger.md and 07_harmonic_oscillator.md (infinite-dimensional Hilbert spaces, separation of variables), docs/02_quantum_mechanics/09_perturbation_theory.md (first-order time-dependent perturbation theory, Fermi's golden rule), docs/03_quantum_gates_and_circuits/03_circuit_model_and_universality.md (Solovay-Kitaev error bounds), docs/08_advanced_topics/03_many_body_physics_and_simulation.md (Trotter error), docs/06_variational_quantum_algorithms/07_quantum_optimal_control.md (time-dependent Hamiltonians)

## Overview

Finite-dimensional linear algebra carries you a long way in quantum computing, but sooner or later every serious question turns into a question of *analysis*: does this series converge, how large is the error after `n` Trotter steps, why is `e^{A+B}` not `e^A e^B`, what does "the spectrum of the momentum operator" even mean when there are no normalizable eigenvectors? This chapter collects the pieces of real, complex, and functional analysis — plus the theory of ordinary and partial differential equations — that the rest of the corpus quietly assumes.

The organizing idea is the **matrix exponential** `e^{-iHt}`. It is defined by a power series (real analysis), evaluated using Euler's formula and eigenvalues (complex analysis), it solves the Schrödinger equation (ODEs), and when `H` is a differential operator on `L²` it forces us to confront unbounded operators and continuous spectra (functional analysis). Each section is motivated by where it is used later: convergence for Solovay-Kitaev and Trotter bounds, the Dyson series for perturbation theory and pulse-level control, `L²` and self-adjointness for wave mechanics, trace-class operators for density matrices.

The treatment is honest about depth. Topics you will compute with (series bounds, BCH, Trotter, Dyson) are developed fully; topics you mainly need to *recognize* (projection-valued measures, distributions) are surveyed with precise statements and pointers.

## Sequences, Series, and Convergence

A sequence `(aₙ)` in a normed space converges to `a` if `‖aₙ - a‖ → 0`. It is **Cauchy** if `‖aₘ - aₙ‖ → 0` as `m, n → ∞`. A space in which every Cauchy sequence converges is **complete** — this is the defining property of a Banach space (complete normed space) and of a Hilbert space (complete inner-product space). Completeness is what lets us define objects by limits, and every existence theorem in this chapter uses it.

A series `Σ aₖ` **converges absolutely** if `Σ ‖aₖ‖ < ∞`. In a complete space, absolute convergence implies convergence (the partial sums are Cauchy by the triangle inequality). The two comparison tests you will use most:

- **Geometric series**: if `‖A‖ < 1` for an operator `A`, then `Σₖ Aᵏ` converges absolutely and equals `(I - A)⁻¹` (the **Neumann series**). The tail after `N` terms is bounded by `‖A‖ᴺ/(1 - ‖A‖)`.
- **Ratio test**: if `‖aₖ₊₁‖/‖aₖ‖ → L < 1` the series converges absolutely. Applied to `Aᵏ/k!` the ratio is `‖A‖/(k+1) → 0`, so the exponential series converges for every bounded `A`.

**Why this matters later.** The Solovay-Kitaev theorem (docs/03, chapter 3) builds an approximation `U ≈ U₀U₁U₂...` where the `k`-th correction has error `εₖ₊₁ = c εₖ^{3/2}`. Because `3/2 > 1`, the errors `εₖ` shrink super-geometrically once `c²ε₀ < 1`, so the total error `Σₖ εₖ` converges and the recursion depth needed for precision `ε` is only `O(log log(1/ε))` — that is where the polylogarithmic gate count comes from. Trotter bounds (below) are sums of `n` per-step errors, each `O((t/n)²)`; the sum converges to `0` as `n → ∞` because `n · (t/n)² = t²/n`.

**Uniform vs pointwise.** A sequence of functions `fₙ → f` **pointwise** if `fₙ(x) → f(x)` for each `x`; **uniformly** if `sup_x |fₙ(x) - f(x)| → 0`. Uniform limits of continuous functions are continuous; pointwise limits need not be. In quantum mechanics the relevant notion is usually `L²` convergence, `‖fₙ - f‖₂ → 0`, which is neither implied by nor implies pointwise convergence.

## Taylor Series and the Matrix Exponential

For a bounded operator `A` on a Hilbert space (any matrix, in finite dimensions), define

`e^A = Σₖ₌₀^∞ Aᵏ/k! = I + A + A²/2 + A³/6 + ...`

The series converges absolutely because `Σ ‖A‖ᵏ/k! = e^{‖A‖} < ∞`, and it satisfies `‖e^A‖ ≤ e^{‖A‖}`.

**Evaluation by the spectral theorem.** If `A = Σᵢ λᵢ|i⟩⟨i|` is normal, then `e^A = Σᵢ e^{λᵢ}|i⟩⟨i|`. For an involution (`A² = I`, e.g. any Pauli or any product of Paulis), the series splits into even and odd powers:

`e^{iθA} = (cos θ) I + i (sin θ) A`

This is the formula behind every rotation gate `R_n̂(θ) = e^{-iθ n̂·σ/2} = cos(θ/2) I - i sin(θ/2) n̂·σ`.

**The exponential does not turn sums into products.** If `[A, B] = 0` then `e^{A+B} = e^A e^B` (expand both series and regroup — allowed because of absolute convergence). If they do not commute, the identity fails. Take `A = X`, `B = Z`:

`e^{X+Z} = cosh(√2) I + (sinh(√2)/√2)(X + Z) ≈ [[3.5465, 1.3683], [1.3683, 0.8099]]`

`e^X e^Z = [cosh(1) I + sinh(1) X] · diag(e, e⁻¹) ≈ [[4.1945, 0.4323], [3.1945, 0.5677]]`

(the closed form uses `X + Z = √2 · n̂·σ` with `n̂ = (1,0,1)/√2`, so `(X+Z)² = 2I`.) The two matrices differ by `2.03` in operator norm; the product is not even symmetric.

**Baker-Campbell-Hausdorff to second order.** The correct statement is

`e^A e^B = exp(A + B + ½[A,B] + (1/12)([A,[A,B]] + [B,[B,A]]) + ...)`

Everything beyond `A + B` is built from nested commutators. For the Trotter step we need it with `A → -iAs`, `B → -iBs`:

`e^{-iAs} e^{-iBs} = exp(-i(A+B)s - (s²/2)[A,B] + O(s³))`

**Lie-Trotter formula.** Splitting `t` into `n` steps of size `s = t/n`:

`e^{-i(A+B)t} = lim_{n→∞} (e^{-iAt/n} e^{-iBt/n})ⁿ`

with the quantitative first-order bound

`‖e^{-i(A+B)t} - (e^{-iAt/n} e^{-iBt/n})ⁿ‖ ≤ (t²/2n) ‖[A,B]‖`

*Proof sketch.* Per step, BCH gives an error operator of norm at most `(s²/2)‖[A,B]‖ + O(s³)`. A telescoping argument (`Uⁿ - Vⁿ = Σₖ Uᵏ(U - V)Vⁿ⁻ᵏ⁻¹`, and unitaries have norm 1) shows that `n` steps accumulate at most `n` times the per-step error: `n · (t/n)² ‖[A,B]‖/2 = t²‖[A,B]‖/(2n)`. This is the bound quoted in docs/08_advanced_topics/03_many_body_physics_and_simulation.md; the symmetric (Strang) splitting `e^{-iAs/2}e^{-iBs}e^{-iAs/2}` cancels the `s²` term and gives `O(t³/n²)`.

## Complex Analysis Essentials

A function `f: ℂ → ℂ` is **analytic** (holomorphic) on an open set if it is complex-differentiable there. This is far stronger than real differentiability: analytic functions are automatically infinitely differentiable and equal to their Taylor series on any disk that avoids singularities. Writing `f = u + iv`, analyticity is equivalent to the **Cauchy-Riemann equations** `∂u/∂x = ∂v/∂y`, `∂u/∂y = -∂v/∂x`.

**Euler's formula** `e^{iθ} = cos θ + i sin θ` follows from the exponential series by separating real and imaginary parts. Consequences used constantly:

- `|e^{iθ}| = 1`; global phases are points on the unit circle
- `cos θ = (e^{iθ} + e^{-iθ})/2`, `sin θ = (e^{iθ} - e^{-iθ})/2i`
- The **`N`-th roots of unity** `ω_N^k = e^{2πik/N}`, `k = 0, ..., N-1`, satisfy `Σₖ ω_N^{jk} = N δ_{j,0 mod N}`. This orthogonality relation *is* the unitarity of the quantum Fourier transform (docs/04, chapter 3) and the character orthogonality of `ℤ_N`.

**Contour integrals.** For a closed curve `C` and `f` analytic inside and on `C`, **Cauchy's theorem** says `∮_C f(z) dz = 0`. If `f` has isolated singularities `zⱼ` inside `C`, the **residue theorem** says

`∮_C f(z) dz = 2πi Σⱼ Res(f, zⱼ)`

where for a simple pole `Res(f, z₀) = lim_{z→z₀} (z - z₀) f(z)`. Two standard applications:

1. **Real integrals over the line.** Close the contour with a large semicircle in the upper half-plane; **Jordan's lemma** guarantees the semicircle contributes nothing for integrands like `e^{ikz} g(z)` with `g → 0` and `k > 0`. Example: `∫_{-∞}^{∞} dx/(x² + a²)`: the only upper-half-plane pole is `z = ia` with residue `1/(2ia)`, so the integral is `2πi/(2ia) = π/a`.
2. **Green's functions and resolvents.** The retarded Green's function `G(E) = (E - H + iη)⁻¹` has poles at the eigenvalues of `H` pushed just below the real axis. The `+iη` prescription selects which half-plane to close in and therefore encodes causality; the density of states is `-(1/π) Im Tr G(E)`. Contour deformation is also how the Sokhotski-Plemelj formula `1/(x - iη) → P(1/x) + iπδ(x)` arises.

## Ordinary Differential Equations

**Linear systems.** The initial-value problem `x'(t) = A x(t)`, `x(0) = x₀`, with `A` a constant matrix, has the unique solution `x(t) = e^{At} x₀`. Uniqueness follows from the Picard-Lindelöf theorem (Lipschitz right-hand side), and existence is a direct check: term-by-term differentiation of the exponential series is legitimate because it converges uniformly on bounded `t`-intervals, and gives `(d/dt) e^{At} = A e^{At}`.

**The Schrödinger equation is a linear ODE.** For a time-independent Hamiltonian `H` (Hermitian),

`iℏ d|ψ⟩/dt = H|ψ⟩  ⟹  |ψ(t)⟩ = e^{-iHt/ℏ}|ψ(0)⟩ = U(t)|ψ(0)⟩`

`U(t)` is unitary because `(e^{-iHt})† = e^{iH†t} = e^{iHt} = U(t)⁻¹`. In the eigenbasis `H|n⟩ = Eₙ|n⟩`, each component simply rotates: `cₙ(t) = cₙ(0) e^{-iEₙt/ℏ}`. This is *all* of closed-system quantum dynamics.

**Time-dependent Hamiltonians.** If `H(t)` varies, `e^{-i∫H}` is *not* the solution unless `[H(t), H(t')] = 0` for all `t, t'`. Iterating the integral form `U(t) = I - (i/ℏ)∫₀ᵗ H(t₁)U(t₁) dt₁` produces the **Dyson series**

`U(t) = I + (-i/ℏ)∫₀ᵗ dt₁ H(t₁) + (-i/ℏ)² ∫₀ᵗ dt₁ ∫₀^{t₁} dt₂ H(t₁)H(t₂) + ...`

Later times always stand to the left. This is written compactly as the **time-ordered exponential** `U(t) = 𝒯 exp(-(i/ℏ)∫₀ᵗ H(t') dt')`. Truncating at first order in an interaction-picture perturbation `V(t)` gives Fermi's golden rule and time-dependent perturbation theory (docs/02, chapter 9); the full series is what a numerical pulse simulator (docs/06, chapter 7) approximates by many short piecewise-constant steps, each solved exactly by the matrix exponential.

**Magnus expansion.** An alternative to Dyson writes `U(t) = exp(Ω(t))` with `Ω = Ω₁ + Ω₂ + ...`, where `Ω₁ = -(i/ℏ)∫₀ᵗ H(t₁)dt₁` and `Ω₂ = -(1/2ℏ²)∫₀ᵗ dt₁∫₀^{t₁} dt₂ [H(t₁), H(t₂)]`. Unlike a truncated Dyson series, every truncation of the Magnus series is exactly unitary, which is why it underlies average-Hamiltonian theory in dynamical decoupling and NMR pulse design; the leading correction `Ω₂` is the continuous-time analogue of the BCH commutator term.

## Partial Differential Equations: Separation of Variables

When `H = -(ℏ²/2m)∂²/∂x² + V(x)` acts on wavefunctions, the Schrödinger equation is a PDE in `(x, t)`. **Separation of variables** — the ansatz `ψ(x,t) = φ(x) T(t)` — splits it: dividing by `φT` gives `iℏ T'/T = (Hφ)/φ`, and a function of `t` alone can equal a function of `x` alone only if both are a constant `E`. Hence

`T(t) = e^{-iEt/ℏ}`,  `Hφ = Eφ` (the time-independent Schrödinger equation)

The general solution is the superposition `ψ(x,t) = Σₙ cₙ φₙ(x) e^{-iEₙt/ℏ}` — the same statement as `|ψ(t)⟩ = e^{-iHt/ℏ}|ψ(0)⟩` expanded in the energy basis. Boundary conditions (vanishing at the walls of a box, normalizability at infinity) are what quantize `E`. docs/02_quantum_mechanics/06_wave_mechanics_and_schrodinger.md carries this out for the square well, and 07_harmonic_oscillator.md for the oscillator, where separation in the position representation leads to the Hermite equation. In higher dimensions one separates further (`φ(r,θ,φ) = R(r)Y(θ,φ)` for hydrogen), and the angular part produces the spherical harmonics and the representation theory of rotations.

## Functional Analysis: The Infinite-Dimensional Setting

### L² spaces and orthonormal bases

`L²(ℝ)` is the space of (equivalence classes of) measurable functions with `∫|ψ(x)|² dx < ∞`, with inner product `⟨φ|ψ⟩ = ∫ φ(x)* ψ(x) dx`. Its completeness (the Riesz-Fischer theorem) is why we use the Lebesgue integral rather than Riemann's. An orthonormal set `{φₙ}` is a **basis** (complete) if `Σₙ |φₙ⟩⟨φₙ| = I`, equivalently `‖ψ‖² = Σₙ |⟨φₙ|ψ⟩|²` for every `ψ` (Parseval). `L²` is **separable**: it has a countable orthonormal basis, e.g. the Hermite functions. This is why the oscillator Hilbert space, though infinite-dimensional, is spanned by the countable Fock basis `{|n⟩}`.

### Bounded and unbounded operators

An operator `A` is **bounded** if `‖A‖ = sup_{‖ψ‖=1} ‖Aψ‖ < ∞`. All finite matrices are bounded; so are unitaries, projectors, and density matrices. The operators that make wave mechanics interesting — position `x̂` and momentum `p̂ = -iℏ d/dx` — are **unbounded**: `‖x̂ψ‖` can be made arbitrarily large relative to `‖ψ‖`, and `p̂` is not even defined on all of `L²` (most `L²` functions are not differentiable). An unbounded operator therefore always comes with a **domain** `D(A) ⊂ L²`, a dense subspace on which it acts.

### Self-adjoint versus Hermitian

In finite dimensions "Hermitian" and "self-adjoint" coincide. In infinite dimensions they do not, and the difference is not pedantry. An operator is **symmetric** (Hermitian) if `⟨φ|Aψ⟩ = ⟨Aφ|ψ⟩` for all `φ, ψ ∈ D(A)`. Its adjoint `A†` is defined on the (possibly larger) set of `φ` for which `ψ ↦ ⟨φ|Aψ⟩` is bounded. `A` is **self-adjoint** if `A† = A` *including the domains*, `D(A†) = D(A)`. Only self-adjoint operators have a spectral decomposition and generate unitary groups `e^{-iAt}` (Stone's theorem). Standard cautionary example: `p̂ = -i d/dx` on `[0, 1]` with Dirichlet conditions `ψ(0) = ψ(1) = 0` is symmetric but not self-adjoint; imposing the twisted-periodic condition `ψ(1) = e^{iα}ψ(0)` for a chosen `α` yields a self-adjoint extension, one for each `α`, with different spectra `{2πn + α}`. Physically: a particle on an interval has no momentum observable until you say what happens at the walls. Whenever a textbook writes "Hermitian" for `x̂`, `p̂`, or a Hamiltonian on an unbounded domain, self-adjoint is what is meant and what the theorems require.

### The spectral theorem in infinite dimensions

For a self-adjoint `A` the spectrum `σ(A) ⊂ ℝ` splits into a **point spectrum** (genuine eigenvalues with normalizable eigenvectors) and a **continuous spectrum** (values `λ` for which `(A - λ)⁻¹` fails to be bounded but no `L²` eigenvector exists). `x̂` and `p̂` on `L²(ℝ)` have purely continuous spectrum `ℝ`; the hydrogen Hamiltonian has discrete negative bound-state levels plus the continuous scattering spectrum `[0, ∞)`. The spectral theorem replaces the finite sum `A = Σᵢ λᵢ Pᵢ` with an integral against a **projection-valued measure** `E(·)`, which assigns an orthogonal projector `E(S)` to each Borel set `S ⊂ ℝ`:

`A = ∫ λ dE(λ)`,  `f(A) = ∫ f(λ) dE(λ)`,  `Prob(A ∈ S | ψ) = ⟨ψ|E(S)|ψ⟩`

The last formula is the Born rule for continuous observables: the probability of finding the position in an interval is `∫_S |ψ(x)|² dx`, i.e. `E(S)` is multiplication by the indicator of `S`. The "eigenstates" `|x⟩` and `|p⟩` of docs/02 are convenient bookkeeping for this measure, not vectors in `L²`.

### Compact and trace-class operators

A bounded operator is **compact** if it is a norm limit of finite-rank operators; compact self-adjoint operators behave exactly like finite matrices (discrete spectrum accumulating only at `0`, orthonormal eigenbasis). An operator `T` is **trace class** if `Tr|T| = Σₙ ⟨φₙ| |T| |φₙ⟩ < ∞`, in which case `Tr T` is finite and basis-independent. Density matrices are precisely the positive trace-class operators with `Tr ρ = 1`; this is the infinite-dimensional version of the definition in docs/02, chapter 5, and it guarantees that `Tr(ρA)` is finite for every bounded observable `A`. A thermal state `ρ ∝ e^{-βH}` of the oscillator is trace class because `Σₙ e^{-βℏω(n+½)} < ∞` — a geometric series again.

### The Fourier transform as a unitary

The Fourier transform on `L²(ℝ)`,

`(Fψ)(p) = (2πℏ)^{-1/2} ∫ e^{-ipx/ℏ} ψ(x) dx`

is a **unitary** operator (Plancherel's theorem: `‖Fψ‖ = ‖ψ‖`, and `F` is onto). It diagonalizes `p̂`: `F p̂ F⁻¹` is multiplication by `p`. This is the precise content of "the momentum representation is the Fourier transform of the position representation" and the reason `x̂` and `p̂` have the same continuous spectrum. The Gaussian `π^{-1/4} e^{-x²/2}` (with `ℏ = 1`) is a fixed point of `F`; more generally `F⁴ = I`, so the eigenvalues of `F` are the fourth roots of unity `{1, -i, -1, i}`, taken by the Hermite functions in order — the finite-dimensional QFT inherits the same `F⁴ = I` structure.

### Distributions and the delta function

The Dirac delta is not a function: no `L²` (or any) function satisfies `∫ δ(x) f(x) dx = f(0)`. It is a **distribution** — a continuous linear functional on a space of smooth rapidly-decaying test functions `f`, written `δ[f] = f(0)`. Derivatives of distributions are defined by moving the derivative onto the test function, `δ'[f] = -f'(0)`, which is how one differentiates step functions and gives meaning to `p̂` acting on plane waves. In this language `⟨x|x'⟩ = δ(x - x')` and `∫|x⟩⟨x| dx = I` are statements about the projection-valued measure of `x̂`, and the "plane-wave eigenstates" `e^{ipx/ℏ}` are tempered distributions rather than states.

## Key Formulas

**Matrix exponential**:
`e^A = Σₖ Aᵏ/k!`,  `‖e^A‖ ≤ e^{‖A‖}`,  `e^{iθA} = cos θ I + i sin θ A` when `A² = I`

**Baker-Campbell-Hausdorff (second order)**:
`e^A e^B = exp(A + B + ½[A,B] + O(3))`

**First-order Trotter bound**:
`‖e^{-i(A+B)t} - (e^{-iAt/n} e^{-iBt/n})ⁿ‖ ≤ t² ‖[A,B]‖ / (2n)`

**Residue theorem**:
`∮_C f(z) dz = 2πi Σⱼ Res(f, zⱼ)`

**Roots of unity orthogonality**:
`Σ_{k=0}^{N-1} e^{2πijk/N} = N δ_{j ≡ 0 (mod N)}`

**Schrödinger solution and Dyson series**:
`U(t) = e^{-iHt/ℏ}` (constant `H`);  `U(t) = 𝒯 exp(-(i/ℏ)∫₀ᵗ H(t')dt') = I - (i/ℏ)∫₀ᵗ H(t₁)dt₁ - (1/ℏ²)∫₀ᵗdt₁∫₀^{t₁}dt₂ H(t₁)H(t₂) + ...`

**Spectral theorem (self-adjoint `A`)**:
`A = ∫ λ dE(λ)`,  `Prob(A ∈ S) = ⟨ψ|E(S)|ψ⟩`

**Fourier transform is unitary**:
`‖Fψ‖₂ = ‖ψ‖₂`,  `F p̂ F⁻¹ = p` (multiplication),  `F⁴ = I`

## Worked Example

**Problem**: Let `A = X`, `B = Z`, `t = 1`. Estimate the first-order Trotter error `‖e^{-i(A+B)t} - (e^{-iAt/n} e^{-iBt/n})ⁿ‖` from the BCH commutator term, then compare with direct numerical evaluation for `n ∈ {1, 2, 4, 8, 16}` and confirm the `O(t²/n)` scaling.

**Solution**:

Step 1 — The commutator. From the Pauli algebra `XZ = -iY` and `ZX = iY`, so `[X, Z] = -2iY` and `‖[X, Z]‖ = 2` (operator norm; `Y` has eigenvalues `±1`).

Step 2 — BCH for a single step of size `s = t/n`. Substituting `A → -iXs`, `B → -iZs` into `e^Ae^B = exp(A + B + ½[A,B] + ...)`:

`e^{-iXs} e^{-iZs} = exp(-i(X+Z)s + ½(-is)²[X,Z] + O(s³)) = exp(-i(X+Z)s - (s²/2)(-2iY) + O(s³)) = exp(-i(X+Z)s + i s² Y + O(s³))`

The per-step error operator is `i s² Y`, of norm `s²`. Equivalently, per step the error is `(s²/2)‖[A,B]‖ = s²`.

Step 3 — Accumulate over `n` steps. The telescoping bound gives total error at most `n · s² = n · (t/n)² = t²/n = 1/n`. So the prediction is `ε(n) ≤ 1/n`, i.e. `O(t²/n)`.

Step 4 — Direct numerical comparison. The exact evolution is `e^{-i(X+Z)} = cos(√2) I - i (sin(√2)/√2)(X + Z)`. Computing `(e^{-iX/n} e^{-iZ/n})ⁿ` with a matrix exponential routine and taking the operator norm of the difference:

| `n` | single-step error | `s² = 1/n²` | total error `ε(n)` | `n · ε(n)` | bound `1/n` |
|---|---|---|---|---|---|
| 1 | 0.7992 | 1.0000 | 0.7992 | 0.799 | 1.0000 |
| 2 | 0.2365 | 0.2500 | 0.3624 | 0.725 | 0.5000 |
| 4 | 0.0616 | 0.0625 | 0.1763 | 0.705 | 0.2500 |
| 8 | 0.01557 | 0.015625 | 0.0875 | 0.700 | 0.1250 |
| 16 | 0.003903 | 0.003906 | 0.0437 | 0.699 | 0.0625 |

Step 5 — Reading the table. The single-step error matches the BCH prediction `s²` to three digits by `n = 8` (the discrepancy is the `O(s³)` remainder). The total error halves every time `n` doubles: `n · ε(n)` settles at `≈ 0.70`, confirming `ε(n) = C · t²/n` with `C ≈ 0.70`. The observed constant is below the worst-case `1` because the per-step error operators `i s² Y` are conjugated by different amounts of the exact evolution before they add, so they partially cancel rather than adding coherently — the bound is an upper bound, not an equality. Doubling accuracy costs doubling the circuit depth at first order; the second-order Strang splitting would instead show `n² · ε(n)` approaching a constant.

**Key insight**: The Trotter error is *entirely* a commutator effect. If `A` and `B` commuted the table would be all zeros; the size `‖[A,B]‖` sets the prefactor, and the `1/n` law follows from adding `n` errors each of size `(t/n)²`.

## Summary

- **Completeness** (Cauchy sequences converge) is the property that makes limits, series, and the exponential well-defined; the Neumann and exponential series converge absolutely for bounded operators
- `e^{A+B} = e^A e^B` **only** when `[A,B] = 0`; the Baker-Campbell-Hausdorff correction starts at `½[A,B]`, and the first-order **Trotter error** is `≤ t²‖[A,B]‖/(2n)`
- **Euler's formula** and the **roots of unity** underlie phases and the QFT; the **residue theorem** evaluates real integrals and propagators by closing contours
- The Schrödinger equation is a linear ODE solved by `e^{-iHt/ℏ}`; for time-dependent `H` the solution is the **time-ordered (Dyson) exponential**, and the **Magnus expansion** gives unitary truncations
- **Separation of variables** turns the Schrödinger PDE into the eigenvalue problem `Hφ = Eφ` plus phases `e^{-iEt/ℏ}`
- In `L²`, physically important operators are **unbounded** and must be **self-adjoint** (not merely symmetric) to have a spectral decomposition and generate unitary dynamics
- The infinite-dimensional **spectral theorem** uses projection-valued measures and allows **continuous spectrum**; density matrices are **trace-class** operators; the **Fourier transform** is a unitary with `F⁴ = I`; the delta function is a **distribution**

## Exercises

**Exercise 1**: Let `A = X/2`. Show that the Neumann series `Σₖ Aᵏ` converges, compute its sum in closed form, and check it against `(I - A)⁻¹`. How many terms are needed to guarantee an error below `0.05` in operator norm?

<details><summary>Solution</summary>

`‖A‖ = 1/2 < 1`, so the series converges absolutely. Since `X² = I`, even powers give `(1/2)^{2m} I` and odd powers give `(1/2)^{2m+1} X`:

`Σₖ Aᵏ = (Σₘ 4^{-m}) I + (½ Σₘ 4^{-m}) X = (4/3) I + (2/3) X = [[4/3, 2/3], [2/3, 4/3]]`

Check: `(I - A) = [[1, -1/2], [-1/2, 1]]`, and `(I - A)·[[4/3, 2/3],[2/3, 4/3]] = [[4/3 - 1/3, 2/3 - 2/3],[2/3 - 2/3, 4/3 - 1/3]] = I` ✓.

The tail after `N` terms is bounded by `‖A‖ᴺ/(1 - ‖A‖) = 2 · 2^{-N}`. For this to be `< 0.05` we need `2^{-N} < 0.025`, i.e. `N ≥ 6`. (The actual 6-term partial sum is `[[1.3125, 0.65625],[0.65625, 1.3125]]`, off by `0.03125` — the bound is tight here because `X` has a `+1` eigenvector.)

</details>

**Exercise 2**: Compute `e^{iπX/4}` and `e^{iπZ/4}` from the series, form their product, and compare with `e^{iπ(X+Z)/4}`. Report the operator-norm difference.

<details><summary>Solution</summary>

Using `e^{iθA} = cos θ I + i sin θ A` with `θ = π/4`:

`e^{iπX/4} = (1/√2)(I + iX) = [[0.7071, 0.7071i],[0.7071i, 0.7071]]`,  `e^{iπZ/4} = diag(e^{iπ/4}, e^{-iπ/4})`

Product: `e^{iπX/4} e^{iπZ/4} = [[0.5 + 0.5i, 0.5 + 0.5i], [-0.5 + 0.5i, 0.5 - 0.5i]]`.

For the sum, `(X + Z)² = 2I`, so with `M = (X+Z)/√2` (an involution) and angle `π/(2√2)`:

`e^{iπ(X+Z)/4} = cos(π/2√2) I + i sin(π/2√2) M = [[0.4440 + 0.6336i, 0.6336i], [0.6336i, 0.4440 - 0.6336i]]`

The difference has operator norm `0.537`. The product has an off-diagonal element with a real part; the true exponential of the sum does not — the discrepancy is the `½[iπX/4, iπZ/4] = -(π²/32)[X,Z] = (iπ²/16)Y` BCH term at leading order.

</details>

**Exercise 3**: Evaluate `∫_{-∞}^{∞} dx/(x² + 4)` and `∫₀^{2π} dθ/(5 + 3cos θ)` using the residue theorem.

<details><summary>Solution</summary>

*First integral.* `f(z) = 1/(z² + 4)` has simple poles at `z = ±2i`. Close in the upper half-plane (the integrand decays like `1/|z|²`, so the arc vanishes). `Res(f, 2i) = 1/(2z)|_{z=2i} = 1/(4i)`. Hence the integral is `2πi · 1/(4i) = π/2 ≈ 1.5708`, consistent with the general formula `π/a` at `a = 2`.

*Second integral.* Substitute `z = e^{iθ}`, `cos θ = (z + 1/z)/2`, `dθ = dz/(iz)`, turning the integral into a contour integral over the unit circle:

`∮ dz / (iz(5 + (3/2)(z + 1/z))) = ∮ 2 dz / (i(3z² + 10z + 3)) = (2/i) ∮ dz / (3(z + 3)(z + 1/3))`

Only `z = -1/3` lies inside the unit circle. `Res = 1/(3(-1/3 + 3)) = 1/8`. The integral is `(2/i) · 2πi · (1/8) = π/2 ≈ 1.5708`, matching `2π/√(a² - b²) = 2π/√(25 - 9) = π/2`.

</details>

**Exercise 4**: A qubit starts in `|0⟩` and evolves under `H(t) = ε X` for `0 ≤ t ≤ T` (`ℏ = 1`). Compute the amplitude `⟨1|U(T)|0⟩` from the Dyson series to first order, explain why the second-order term contributes nothing to this amplitude, and compare with the exact result for `εT = 0.3`.

<details><summary>Solution</summary>

First order: `U⁽¹⁾ = -i ∫₀ᵀ εX dt = -iεT X`, so `⟨1|U⁽¹⁾|0⟩ = -iεT ⟨1|X|0⟩ = -iεT`. For `εT = 0.3` this is `-0.3i`.

Second order: `U⁽²⁾ = (-i)² ∫₀ᵀdt₁∫₀^{t₁}dt₂ ε²X² = -(ε²T²/2) I`. It is proportional to the identity, so `⟨1|U⁽²⁾|0⟩ = 0` — even powers of `X` never flip the qubit. Third order gives `+i(εT)³/6 · ⟨1|X|0⟩`, so the series for the amplitude is `-i(εT - (εT)³/6 + ...) = -i sin(εT)`.

Exact: `U(T) = e^{-iεTX} = cos(εT) I - i sin(εT) X`, so `⟨1|U|0⟩ = -i sin(0.3) = -0.2955i`. The first-order Dyson term `-0.3i` is off by `1.5%`; including the third-order term gives `-0.29550i`, matching the exact `-0.29552i` to four digits (the fifth-order term `(εT)⁵/120 ≈ 2×10⁻⁵` closes the gap). Here `H` commutes with itself at all times, so time ordering is trivial and the Dyson series is just the Taylor series of the exponential.

</details>

**Exercise 5**: Take `ℏ = 1` and `ψ(x) = π^{-1/4} e^{-x²/2}`. Verify that `ψ` is normalized, compute `⟨x²⟩`, and show that `ψ` is an eigenfunction of the Fourier transform with eigenvalue `1`. What does this imply for `Δx Δp`?

<details><summary>Solution</summary>

Normalization: `∫ |ψ|² dx = π^{-1/2} ∫ e^{-x²} dx = π^{-1/2} · √π = 1` ✓.

Second moment: `⟨x²⟩ = π^{-1/2} ∫ x² e^{-x²} dx = π^{-1/2} · (√π/2) = 1/2`. Since `⟨x⟩ = 0` by symmetry, `Δx = 1/√2`.

Fourier transform: `(Fψ)(p) = (2π)^{-1/2} π^{-1/4} ∫ e^{-ipx} e^{-x²/2} dx`. Completing the square, `∫ e^{-x²/2 - ipx} dx = √(2π) e^{-p²/2}`, so `(Fψ)(p) = π^{-1/4} e^{-p²/2} = ψ(p)`. Numerically at `p = 0.7` both sides equal `0.5879`. Thus `Fψ = ψ`: the Gaussian is the ground state of the oscillator and the eigenvalue-`1` eigenvector of `F`.

Since the momentum-space wavefunction is the same Gaussian, `Δp = 1/√2` as well, and `Δx Δp = 1/2` — the Heisenberg bound is saturated. This is the minimum-uncertainty property of coherent states used in docs/02_quantum_mechanics/07_harmonic_oscillator.md.

</details>

## Further Reading

1. **Hall**, *Quantum Theory for Mathematicians* (Springer GTM 267), Chapters 6-10 — the cleanest modern account of unbounded operators, self-adjointness, and the spectral theorem for physicists who want the proofs; Chapter 9 covers the `[0,1]` momentum example
2. **Reed & Simon**, *Methods of Modern Mathematical Physics I: Functional Analysis*, Chapters II, VI, VIII — the standard reference for `L²`, trace-class operators, and the spectral theorem via projection-valued measures
3. **Childs**, *Lecture Notes on Quantum Algorithms* (University of Maryland, free online), Chapter 27 "Simulating Hamiltonian dynamics" — Lie-Trotter and higher-order product formulas with the commutator error bounds used here
4. **Hall**, *Lie Groups, Lie Algebras, and Representations* (Springer GTM 222), Chapters 2 and 5 — the matrix exponential, its convergence, and a full proof of the Baker-Campbell-Hausdorff formula
5. **Sakurai & Napolitano**, *Modern Quantum Mechanics* (3rd ed.), §2.1 and §5.7 — time-evolution operator, the Dyson series, and time-dependent perturbation theory in the interaction picture; **Blanes, Casas, Oteo & Ros**, "The Magnus expansion and some of its applications", *Physics Reports* 470 (2009), for the Magnus series
