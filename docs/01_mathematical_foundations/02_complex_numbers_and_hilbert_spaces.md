# Complex Numbers and Hilbert Spaces

> **Prerequisites**: 01_linear_algebra.md — vector spaces, inner products, Dirac notation  
> **Connects to**: Qubits (the global phase argument), quantum measurements (projection operators), density matrices (operators on Hilbert space)

## Overview

Quantum mechanics is inescapably a theory over the complex numbers. This is not a historical accident or a notational convenience — it is a deep feature. The interference effects that make quantum computers powerful arise from complex amplitudes that can cancel (destructive interference) or reinforce (constructive interference). Real-number quantum mechanics would be a strictly weaker theory.

This chapter builds the two mathematical pillars that support everything else. First, we review complex numbers: their arithmetic, their geometry, and Euler's formula connecting them to rotations. Second, we define Hilbert spaces — complete inner product spaces — and explain the two properties that make them the right setting for quantum mechanics: they accommodate superposition and they have a rich geometry of subspaces and projections.

We also address a crucial physical subtlety: two quantum states that differ only by a global phase are physically identical. This seemingly technical point has profound consequences for how we should think about the state space and for understanding why the Bloch sphere works.

## Complex Numbers

### Cartesian and Polar Forms

A **complex number** `z ∈ ℂ` can be written in Cartesian form as `z = a + bi` where `a, b ∈ ℝ` and `i² = -1`. Here `a = Re(z)` is the **real part** and `b = Im(z)` is the **imaginary part**.

The **complex conjugate** of `z = a + bi` is `z* = a - bi`. Conjugation reverses the sign of the imaginary part, reflecting the number across the real axis in the complex plane.

The **modulus** (or absolute value) is `|z| = √(a² + b²) = √(zz*)`. This is the distance from the origin in the complex plane.

The **argument** (or phase) is `arg(z) = θ = arctan(b/a)`, the angle the line from the origin to `z` makes with the positive real axis. It is defined modulo `2π`.

In **polar form**: `z = |z|e^{iθ}`, where Euler's formula gives the crucial connection:

$$e^{i\theta} = \cos\theta + i\sin\theta$$

This is not merely a definition — it follows from the Taylor series of `eˣ`, `cos x`, and `sin x`:

$$e^{i\theta} = \sum_{n=0}^\infty \frac{(i\theta)^n}{n!} = 1 + i\theta - \frac{\theta^2}{2!} - \frac{i\theta^3}{3!} + \frac{\theta^4}{4!} + \cdots = \cos\theta + i\sin\theta$$

Polar form makes multiplication geometric: `z₁z₂ = |z₁||z₂| e^{i(θ₁+θ₂)}`. Multiplying complex numbers multiplies their moduli and **adds** their arguments. Division subtracts arguments.

### Arithmetic

- **Addition**: `(a+bi) + (c+di) = (a+c) + (b+d)i` — add real and imaginary parts
- **Multiplication**: `(a+bi)(c+di) = (ac-bd) + (ad+bc)i`
- **Conjugate rules**: `(z+w)* = z*+w*`, `(zw)* = z*w*`, `|z|² = zz*`
- **Division**: `z/w = zw*/|w|²`

**Special values**:
- `e^{i·0} = 1`, `e^{iπ/2} = i`, `e^{iπ} = -1`, `e^{i3π/2} = -i`, `e^{2πi} = 1`
- Euler's identity: `e^{iπ} + 1 = 0`

### Why Complex Numbers Appear in Quantum Mechanics

Schrödinger's equation is `iℏ ∂|ψ⟩/∂t = H|ψ⟩`. The factor `i` on the left is not cosmetic. It ensures that probability (`⟨ψ|ψ⟩`) is conserved: the time evolution operator is `U(t) = e^{-iHt/ℏ}`, which is unitary precisely because `H` is Hermitian (real eigenvalues on the exponent).

More fundamentally, quantum mechanics requires that probability amplitudes can interfere, producing patterns that no real-valued probability theory can reproduce. The two-slit experiment, Bell inequality violations, and quantum speedups all stem from this complex arithmetic.

## Hilbert Spaces

### Definition and Structure

A **Hilbert space** `ℋ` is a complex vector space equipped with an inner product `⟨·,·⟩` that is **complete** — every Cauchy sequence converges to a limit in `ℋ`.

Completeness is the technical condition that rules out "holes" in the space; it is automatically satisfied for finite-dimensional vector spaces (all norms are equivalent in finite dimensions), and it becomes important for infinite-dimensional spaces like `L²(ℝ)` (square-integrable functions on the real line).

**For quantum computing**, we almost always work with **finite-dimensional Hilbert spaces** `ℂⁿ`. The relevant Hilbert space for `n` qubits is `ℂ^{2ⁿ}`. Completeness is not a practical concern here, but the full machinery of Hilbert space theory (projections, orthonormal bases, completeness relations) is essential.

An `n`-dimensional Hilbert space `ℋ` has:
- An inner product: `⟨φ|ψ⟩ ∈ ℂ`
- A norm: `‖|ψ⟩‖ = √⟨ψ|ψ⟩`
- Any orthonormal basis `{|eᵢ⟩}` satisfies `⟨eᵢ|eⱼ⟩ = δᵢⱼ`
- The resolution of the identity: `Σᵢ |eᵢ⟩⟨eᵢ| = I`

### Subspaces and Projections

A **subspace** of `ℋ` is a subset `W ⊆ ℋ` that is itself a vector space under the same operations. Subspaces are crucial for measurement theory.

For any subspace `W`, the **orthogonal complement** is `W⊥ = {|v⟩ ∈ ℋ : ⟨v|w⟩ = 0 for all |w⟩ ∈ W}`. We have `ℋ = W ⊕ W⊥` (direct sum decomposition).

A **projection operator** `P` onto subspace `W` is the linear map that sends each vector to its component in `W`:

$$P = \sum_{i \in W} |e_i\rangle\langle e_i|$$

where `{|eᵢ⟩}` is any orthonormal basis for `W`. Key properties:
- `P² = P` (idempotent — projecting twice does nothing)
- `P† = P` (Hermitian — projections are observables)
- `0 ≤ P ≤ I` (positive semidefinite, bounded above by identity)
- `‖P|ψ⟩‖² = ⟨ψ|P|ψ⟩` is the probability of measuring the outcome associated with `W`

**One-dimensional projections** are particularly important: `Pψ = |ψ⟩⟨ψ|` projects onto the line spanned by `|ψ⟩`. The Born rule says: if the system is in state `|φ⟩` and we measure an observable with eigenvector `|ψ⟩`, the probability is:

$$\text{Prob} = \langle \phi | P_\psi | \phi \rangle = |\langle \psi | \phi \rangle|^2$$

### The Cauchy-Schwarz Inequality

For any two vectors `|φ⟩, |ψ⟩` in a Hilbert space:

$$|\langle \phi | \psi \rangle|^2 \leq \langle \phi | \phi \rangle \cdot \langle \psi | \psi \rangle$$

with equality iff `|φ⟩ = c|ψ⟩` for some scalar `c` (i.e., the vectors are proportional).

**Proof**: Consider the vector `|γ⟩ = |ψ⟩ - ⟨φ|ψ⟩/⟨φ|φ⟩ · |φ⟩` (this is `|ψ⟩` with its component along `|φ⟩` removed). Then `⟨γ|γ⟩ ≥ 0` expands to give Cauchy-Schwarz.

For unit vectors, `|⟨φ|ψ⟩|² ≤ 1`, with equality iff `|φ⟩ = e^{iθ}|ψ⟩`. This bounds transition probabilities: the overlap between any two states is between 0 (orthogonal) and 1 (identical up to phase).

## Global Phase Irrelevance

This is one of the most important — and most frequently misunderstood — points in quantum mechanics.

**Claim**: The states `|ψ⟩` and `e^{iθ}|ψ⟩` are **physically identical** for any real `θ`. They represent the same physical state.

**Why**: Every measurable quantity in quantum mechanics takes the form `⟨ψ|A|ψ⟩` (expectation values) or `|⟨φ|ψ⟩|²` (transition probabilities). In both cases, a global phase `e^{iθ}` cancels:

$$\langle e^{i\theta}\psi | A | e^{i\theta}\psi \rangle = e^{-i\theta}e^{i\theta}\langle\psi|A|\psi\rangle = \langle\psi|A|\psi\rangle$$

$$|\langle \phi | e^{i\theta}\psi \rangle|^2 = |e^{i\theta}|^2 |\langle\phi|\psi\rangle|^2 = |\langle\phi|\psi\rangle|^2$$

**Consequence for the state space**: The physical state space is not `ℋ` but the **projective Hilbert space** `P(ℋ)` — the space of rays (equivalence classes of unit vectors differing by a phase). For a single qubit, `P(ℂ²) ≅ S²` (the 2-sphere), which is exactly the Bloch sphere.

**What global phase is vs. relative phase**: Global phase (a single phase multiplying the entire state) is unobservable. But **relative phase** between components of a superposition is physically real and observable:

$$|\psi_1\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} \neq \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |\psi_2\rangle$$

These two states are physically distinct: `|ψ₁⟩ = |+⟩` and `|ψ₂⟩ = |−⟩` are orthogonal. The minus sign is a relative phase (between the `|0⟩` and `|1⟩` components), not a global phase.

**Practical rule**: When comparing states, factor out any overall phase and compare. But never factor out phases from individual components of a superposition and treat them as removable.

## Orthonormal Bases and Gram-Schmidt

Given any linearly independent set of vectors `{|v₁⟩, ..., |vₙ⟩}`, the **Gram-Schmidt process** constructs an orthonormal basis:

1. `|e₁⟩ = |v₁⟩/‖|v₁⟩‖`
2. `|u₂⟩ = |v₂⟩ - ⟨e₁|v₂⟩|e₁⟩` (subtract component along `|e₁⟩`), then normalize: `|e₂⟩ = |u₂⟩/‖|u₂⟩‖`
3. Continue: `|uₖ⟩ = |vₖ⟩ - Σⱼ₌₁^{k-1} ⟨eⱼ|vₖ⟩|eⱼ⟩`, then normalize

This process is used, for example, to convert a set of measurement operators into projectors, or to find the orthogonal complement of a subspace.

## Operator Norms and Spectral Radius

For quantum computing, we sometimes need to know how "large" an operator is. The **operator norm** (spectral norm) is:

$$\|A\| = \max_{\||\psi\rangle\|=1} \|A|\psi\rangle\|$$

For normal operators, `‖A‖ = max|λᵢ|` (the largest eigenvalue magnitude). This equals the largest singular value of `A`.

For a unitary operator `U`, `‖U‖ = 1` since `‖U|ψ⟩‖ = ‖|ψ⟩‖ = 1` for all unit vectors.

The **trace norm** `‖A‖₁ = Tr(√(A†A))` is used in quantum information to measure distinguishability of quantum states (via the trace distance `½‖ρ - σ‖₁`).

The **Frobenius norm** `‖A‖_F = √(Tr(A†A)) = √(Σᵢⱼ|Aᵢⱼ|²)` is the Hilbert-Schmidt norm and appears in the Hilbert-Schmidt inner product `⟨A,B⟩_HS = Tr(A†B)`.

## Spectral Projective Decompositions

For a Hermitian operator `A = Σᵢ λᵢ|i⟩⟨i|`, we can group terms by eigenvalue to get the **spectral projective decomposition**:

$$A = \sum_m m \cdot P_m$$

where `Pₘ = Σᵢ: λᵢ=m |i⟩⟨i|` projects onto the eigenspace of eigenvalue `m`. The projectors satisfy:
- `PₘPₘ' = δₘₘ' Pₘ` (orthogonal)
- `Σₘ Pₘ = I` (completeness)
- `Pₘ† = Pₘ` (Hermitian)
- `Pₘ² = Pₘ` (idempotent)

This decomposition is exactly what appears in the quantum mechanical description of measurement (Postulate 3 in the next chapter): measuring observable `A` on state `|ψ⟩` gives outcome `m` with probability `⟨ψ|Pₘ|ψ⟩`, and leaves the system in state `Pₘ|ψ⟩/√⟨ψ|Pₘ|ψ⟩`.

## Key Formulas

**Euler's formula**:
$$e^{i\theta} = \cos\theta + i\sin\theta$$

**Polar form**:
$$z = |z|e^{i\,\text{arg}(z)}, \quad |z|^2 = zz^*$$

**Cauchy-Schwarz inequality**:
$$|\langle \phi | \psi \rangle|^2 \leq \langle \phi|\phi\rangle\,\langle\psi|\psi\rangle$$

**Global phase irrelevance**:
$$|e^{i\theta}\psi\rangle \equiv |\psi\rangle \quad \text{(physically identical)}$$

**Projection operator**:
$$P_W = \sum_{i \in \text{basis of } W} |e_i\rangle\langle e_i|, \quad P_W^2 = P_W, \quad P_W^\dagger = P_W$$

**Born rule via projector**:
$$\text{Prob}(m) = \langle\psi|P_m|\psi\rangle$$

## Worked Example

**Problem**: Show that `|+⟩ = (|0⟩+|1⟩)/√2` and `|+i⟩ = (|0⟩+i|1⟩)/√2` are unit vectors with a specific inner product, and find the projector onto `|+⟩`.

**Solution**:

Step 1 — Norms:
$$\langle +|+\rangle = \frac{1}{2}(\langle 0|+\langle 1|)(|0\rangle+|1\rangle) = \frac{1}{2}(\langle 0|0\rangle + \langle 0|1\rangle + \langle 1|0\rangle + \langle 1|1\rangle) = \frac{1}{2}(1+0+0+1) = 1 \checkmark$$

Similarly `⟨+i|+i⟩ = ½(1 + |i|²) = ½(1+1) = 1`.

Step 2 — Inner product:
$$\langle +i|+\rangle = \frac{1}{2}(\langle 0| - i\langle 1|)(|0\rangle+|1\rangle) = \frac{1}{2}(1 + (-i)) = \frac{1-i}{2}$$

The **overlap probability** is `|⟨+i|+⟩|² = |1-i|²/4 = 2/4 = 1/2`.

Step 3 — Projector onto `|+⟩`:
$$P_+ = |+\rangle\langle+| = \frac{1}{2}\begin{pmatrix}1\\1\end{pmatrix}\begin{pmatrix}1&1\end{pmatrix} = \frac{1}{2}\begin{pmatrix}1&1\\1&1\end{pmatrix}$$

Verify idempotency:
$$P_+^2 = \frac{1}{4}\begin{pmatrix}1&1\\1&1\end{pmatrix}\begin{pmatrix}1&1\\1&1\end{pmatrix} = \frac{1}{4}\begin{pmatrix}2&2\\2&2\end{pmatrix} = \frac{1}{2}\begin{pmatrix}1&1\\1&1\end{pmatrix} = P_+ \checkmark$$

Step 4 — Global phase check: Is `i|+⟩` the same physical state as `|+⟩`?
$$i|+\rangle = \frac{i}{\sqrt{2}}\begin{pmatrix}1\\1\end{pmatrix}$$
The expectation value of `Z`: `⟨i+|Z|i+⟩ = ⟨+|(-i)(i)Z|+⟩ = ⟨+|Z|+⟩ = 0`. Any observable gives the same result, confirming global phase irrelevance.

Step 5 — Relative phase matters: compare `|+⟩` and `|−⟩ = (|0⟩-|1⟩)/√2`.
$$P_{-} = \frac{1}{2}\begin{pmatrix}1&-1\\-1&1\end{pmatrix}, \quad P_+ + P_- = \begin{pmatrix}1&0\\0&1\end{pmatrix} = I$$
These are orthogonal projectors (`P₊P₋ = 0`), confirming `|+⟩` and `|−⟩` are physically distinct (orthogonal) states. The minus sign in `|−⟩` is a physically observable relative phase.

## Summary

- Complex numbers have Cartesian form `a+bi` and polar form `|z|e^{iθ}`; multiplication adds arguments (phases)
- **Euler's formula** `e^{iθ} = cosθ + i sinθ` connects complex exponentials to rotations
- A **Hilbert space** is a complete inner product space; for quantum computing, it is essentially `ℂⁿ` with the standard inner product
- **Projection operators** `P = |e⟩⟨e|` satisfy `P² = P = P†` and describe measurement outcomes
- The **Cauchy-Schwarz inequality** bounds inner products and transition probabilities
- **Global phase** is physically unobservable: `|ψ⟩` and `e^{iθ}|ψ⟩` describe the same state
- **Relative phase** between components of a superposition is physically real and drives interference
- The true state space is the **projective Hilbert space** P(ℋ) — equivalence classes of unit vectors under global phase

## Further Reading

1. **Nielsen & Chuang**, *Quantum Computation and Quantum Information*, §2.1.7–2.1.8 — inner products, Hilbert spaces, and the physicists' conventions
2. **Preskill**, *Lecture Notes for Physics 229: Quantum Information and Computation* (Caltech, freely available) — Chapter 2 covers Hilbert spaces with exceptional clarity
3. **Griffiths & Schroeter**, *Introduction to Quantum Mechanics* (Cambridge, 3rd ed.) — Chapter 1 motivates complex amplitudes from the physics of superposition and interference
4. **Strocchi**, *An Introduction to the Mathematical Structure of Quantum Mechanics* (World Scientific) — rigorous treatment of why quantum mechanics requires complex Hilbert spaces rather than real ones
5. **Hardy**, *Quantum Theory From Five Reasonable Axioms* (arXiv:quant-ph/0101012) — derives Hilbert space formalism from informational axioms; shows where complex numbers arise naturally
