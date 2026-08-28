# Linear Algebra for Quantum Computing

> **Prerequisites**: High school algebra, basic familiarity with matrices and vectors  
> **Connects to**: Every subsequent chapter — linear algebra is the native language of quantum mechanics; immediately required for qubits, gates, and measurement

## Overview

Quantum computing is, at its mathematical core, a theory of linear algebra over the complex numbers. Quantum states are vectors in complex vector spaces, quantum gates are linear maps represented by matrices, and measurement is the process of decomposing a vector onto an orthonormal basis. Understanding this mathematical substrate is not optional background — it *is* the theory.

This chapter develops the linear algebra you need from the ground up, with an emphasis on the structures that matter most in quantum information: inner products, adjoint operators, unitary matrices, and the spectral theorem. We also introduce Dirac notation (bra-ket notation), the physicist's shorthand that makes quantum calculations dramatically more legible.

The exposition aims for rigor without abstraction for its own sake. Every definition is followed by a concrete example, and every abstract theorem is connected to something physically meaningful. By the end of this chapter you will have the vocabulary and computational tools to work through qubit states, quantum gates, and quantum measurement with confidence.

## Vector Spaces

A **vector space** over a field `F` (for us, `F = ℂ`, the complex numbers) is a set `V` equipped with two operations:

- **Addition**: `u, v ∈ V ⟹ u + v ∈ V`
- **Scalar multiplication**: `c ∈ ℂ, v ∈ V ⟹ cv ∈ V`

satisfying the usual axioms (associativity, commutativity, identity, inverses, distributivity). The key examples for quantum computing are `ℂⁿ` — column vectors of `n` complex numbers with component-wise addition and scalar multiplication.

A **basis** for `V` is a set of vectors `{e₁, ..., eₙ}` that is:
1. **Linearly independent**: `Σᵢ cᵢeᵢ = 0 ⟹ all cᵢ = 0`
2. **Spanning**: every `v ∈ V` can be written as `v = Σᵢ cᵢeᵢ` for some scalars `cᵢ`

The **dimension** of `V` is the number of basis vectors. For quantum computing with `n` qubits, the relevant space has dimension `2ⁿ`.

**Standard basis for ℂ²**: The computational basis consists of

$$|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, \quad |1\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}$$

Every vector in `ℂ²` can be written as `α|0⟩ + β|1⟩` for complex numbers `α, β`. This is the qubit state space.

## Inner Products

An **inner product** on a complex vector space `V` is a function `⟨·,·⟩: V × V → ℂ` satisfying:

1. **Conjugate symmetry**: `⟨u, v⟩ = ⟨v, u⟩*` (where `*` denotes complex conjugate)
2. **Linearity in the second argument**: `⟨u, αv + βw⟩ = α⟨u,v⟩ + β⟨u,w⟩`
3. **Positive definiteness**: `⟨v, v⟩ ≥ 0`, with equality iff `v = 0`

Note the physics convention: linearity is in the **second** argument. (Mathematicians often use the opposite convention; beware when reading math texts.)

For `ℂⁿ` with column vectors, the standard inner product is:

$$\langle u, v \rangle = u^\dagger v = \sum_{i=1}^n u_i^* v_i$$

where `†` denotes the conjugate transpose (adjoint).

The **norm** of a vector is `‖v‖ = √⟨v,v⟩`. Vectors with `‖v‖ = 1` are called **unit vectors** or **normalized vectors**. In quantum mechanics, all physical states are represented by unit vectors.

**Orthonormality**: Vectors `u, v` are **orthogonal** if `⟨u, v⟩ = 0`, and an **orthonormal set** satisfies `⟨eᵢ, eⱼ⟩ = δᵢⱼ` (Kronecker delta). The computational basis `{|0⟩, |1⟩}` is orthonormal:

$$\langle 0 | 0 \rangle = 1, \quad \langle 1 | 1 \rangle = 1, \quad \langle 0 | 1 \rangle = 0$$

## Dirac Notation

Paul Dirac introduced a notation that has become universal in quantum physics and quantum computing. It makes abstract linear algebra operations visually intuitive.

- A **ket** `|ψ⟩` is a column vector (an element of the Hilbert space `V`)
- A **bra** `⟨ψ|` is a row vector (the corresponding element of the dual space `V*`), obtained by taking the conjugate transpose: `⟨ψ| = (|ψ⟩)†`
- A **bra-ket** or **bracket** `⟨φ|ψ⟩` is the inner product of `|φ⟩` and `|ψ⟩`
- A **ket-bra** `|ψ⟩⟨φ|` is an **outer product**, which is a matrix (linear operator)

For `|ψ⟩ = α|0⟩ + β|1⟩`:

$$|\psi\rangle = \begin{pmatrix} \alpha \\ \beta \end{pmatrix}, \quad \langle \psi | = \begin{pmatrix} \alpha^* & \beta^* \end{pmatrix}$$

The outer product `|0⟩⟨1|` is the matrix:

$$|0\rangle\langle 1| = \begin{pmatrix} 1 \\ 0 \end{pmatrix}\begin{pmatrix} 0 & 1 \end{pmatrix} = \begin{pmatrix} 0 & 1 \\ 0 & 0 \end{pmatrix}$$

**Why outer products matter**: An orthonormal basis `{|i⟩}` satisfies the **completeness relation** (resolution of the identity):

$$\sum_i |i\rangle\langle i| = I$$

This is the identity operator expressed in terms of projection operators. It lets us expand any operator in a basis:

$$A = I \cdot A \cdot I = \sum_{i,j} |i\rangle\langle i|A|j\rangle\langle j| = \sum_{i,j} A_{ij} |i\rangle\langle j|$$

where `Aᵢⱼ = ⟨i|A|j⟩` are the matrix elements.

## Linear Operators and Matrices

A **linear operator** `A: V → W` satisfies `A(αu + βv) = αAu + βAv`. Given orthonormal bases for `V` and `W`, every linear operator is represented by a matrix.

The **composition** of operators `A` and `B` corresponds to matrix multiplication: `(AB)ᵢⱼ = Σₖ Aᵢₖ Bₖⱼ`. In quantum computing, applying gate `B` then gate `A` is represented by the matrix product `AB` (rightmost gate acts first).

### The Adjoint

The **adjoint** (Hermitian conjugate) of an operator `A` is the operator `A†` defined by:

$$\langle \phi | A^\dagger | \psi \rangle = \langle \psi | A | \phi \rangle^*$$

In matrix form, `(A†)ᵢⱼ = (Aⱼᵢ)*` — transpose and complex conjugate simultaneously. Key properties:

- `(AB)† = B†A†`
- `(A†)† = A`
- `(αA)† = α*A†`

An operator is **Hermitian** (self-adjoint) if `A† = A`. Hermitian operators have real eigenvalues and represent **observables** — measurable physical quantities. Hermitian matrices satisfy `Aᵢⱼ = Aⱼᵢ*`, so diagonal entries are real.

An operator is **normal** if `A†A = AA†`. Hermitian, unitary, and anti-Hermitian operators are all normal.

### Trace and Determinant

The **trace** of a matrix is the sum of its diagonal entries:

$$\text{Tr}(A) = \sum_i A_{ii}$$

Key properties:
- `Tr(A) = Σᵢ λᵢ` where `λᵢ` are eigenvalues (with multiplicity)
- `Tr(AB) = Tr(BA)` — cyclic invariance
- `Tr(A⊗B) = Tr(A)·Tr(B)` — product over tensor products
- Basis-independent: `Tr(A) = Tr(S⁻¹AS)` for any invertible `S`

The trace appears constantly in quantum mechanics through the formula `⟨A⟩ = Tr(ρA)` for the expectation value of observable `A` in state `ρ`.

The **determinant** of a matrix encodes many properties: `det(A) = Πᵢ λᵢ`. For quantum gates, we often work with `SU(2)` (special unitary group), the set of `2×2` unitary matrices with `det = 1`.

## Eigenvalues and Eigenvectors

A nonzero vector `|v⟩` is an **eigenvector** of `A` with **eigenvalue** `λ` if:

$$A|v\rangle = \lambda|v\rangle$$

Eigenvalues satisfy the **characteristic equation** `det(A - λI) = 0`. For a `2×2` matrix, this is a quadratic.

**Example**: Eigenvalues of the Pauli Z matrix:

$$Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$$

The characteristic equation: `det(Z - λI) = (1-λ)(-1-λ) = -(1-λ²) = 0`, giving `λ = ±1`. The eigenvectors are `|0⟩` (eigenvalue `+1`) and `|1⟩` (eigenvalue `-1`).

**Spectral Theorem**: Every **normal** operator on a finite-dimensional complex inner product space has a complete orthonormal set of eigenvectors. That is, any normal operator `A` can be written as:

$$A = \sum_i \lambda_i |i\rangle\langle i|$$

where `{|i⟩}` is an orthonormal basis of eigenvectors and `{λᵢ}` are the corresponding eigenvalues. This is the **spectral decomposition** or **eigendecomposition**.

For Hermitian operators, the eigenvalues `λᵢ` are **real**. For unitary operators, `|λᵢ| = 1` (eigenvalues lie on the unit circle in the complex plane).

The spectral theorem is fundamental because it allows us to define functions of operators: if `f` is any function and `A = Σᵢ λᵢ|i⟩⟨i|`, then `f(A) = Σᵢ f(λᵢ)|i⟩⟨i|`. This is how we define `e^{iA}`, `log(A)`, `√A`, etc.

## Unitary Matrices

A matrix `U` is **unitary** if:

$$U^\dagger U = U U^\dagger = I$$

Equivalently, the columns of `U` form an orthonormal set, and the rows of `U` also form an orthonormal set.

**Why unitarity matters for quantum computing**: Quantum gates must preserve the normalization `‖|ψ⟩‖ = 1` (probabilities must sum to 1). Since `‖U|ψ⟩‖² = ⟨ψ|U†U|ψ⟩ = ⟨ψ|ψ⟩ = 1`, unitarity is exactly the right condition. Unitary evolution also preserves inner products: `⟨Uφ|Uψ⟩ = ⟨φ|ψ⟩`.

**Key properties**:
- Eigenvalues lie on the unit circle: `|λᵢ| = 1`
- `det(U)` has modulus 1: `|det(U)| = 1`
- `U⁻¹ = U†`
- Product of unitaries is unitary: if `U, V` are unitary, so is `UV`
- Unitary matrices form a group under multiplication

**Special unitary group SU(2)**: The `2×2` unitary matrices with `det = 1` form the group `SU(2)`. Every element can be written as:

$$U = \begin{pmatrix} \alpha & -\beta^* \\ \beta & \alpha^* \end{pmatrix}, \quad |\alpha|^2 + |\beta|^2 = 1$$

This parameterizes all quantum gates on a single qubit (up to global phase).

## The Pauli Matrices

The **Pauli matrices** are three fundamental `2×2` Hermitian, unitary matrices:

$$X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \quad Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$$

Together with the identity `I`, they form an **orthogonal basis** for the space of `2×2` Hermitian matrices under the inner product `⟨A,B⟩ = ½Tr(A†B)`:

$$\frac{1}{2}\text{Tr}(\sigma_i^\dagger \sigma_j) = \delta_{ij}, \quad \sigma_0 = I, \sigma_1 = X, \sigma_2 = Y, \sigma_3 = Z$$

So any `2×2` Hermitian matrix can be written as `H = aI + bX + cY + dZ` for real `a, b, c, d`.

**Algebraic properties**:
- `X² = Y² = Z² = I`
- `XY = iZ`, `YZ = iX`, `ZX = iY` (cyclic)
- `YX = -iZ`, `ZY = -iX`, `XZ = -iY` (anti-cyclic)
- In short: `σᵢσⱼ = δᵢⱼI + iεᵢⱼₖσₖ` where `εᵢⱼₖ` is the Levi-Civita symbol
- Anti-commutation: `{X,Y} = XY + YX = 0`, and similarly for other pairs
- Commutation: `[X,Y] = XY - YX = 2iZ`, `[Y,Z] = 2iX`, `[Z,X] = 2iY`

**Eigenstructure**:
- `Z`: eigenvectors `|0⟩` (eigenvalue +1), `|1⟩` (eigenvalue -1)
- `X`: eigenvectors `|+⟩ = (|0⟩+|1⟩)/√2` (eigenvalue +1), `|−⟩ = (|0⟩-|1⟩)/√2` (eigenvalue -1)
- `Y`: eigenvectors `|+i⟩ = (|0⟩+i|1⟩)/√2` (eigenvalue +1), `|−i⟩ = (|0⟩-i|1⟩)/√2` (eigenvalue -1)

The Pauli matrices are simultaneously Hermitian and unitary, making them both observables (measurable quantities) and quantum gates (transformations). This dual role is central to quantum computing.

## Key Formulas

**Inner product (ℂⁿ)**:
$$\langle u | v \rangle = \sum_{i=1}^n u_i^* v_i$$

**Completeness relation**:
$$\sum_i |i\rangle\langle i| = I \quad \text{for any orthonormal basis}$$

**Spectral decomposition**:
$$A = \sum_i \lambda_i |i\rangle\langle i| \quad \text{(for normal operators)}$$

**Adjoint in matrix form**:
$$(A^\dagger)_{ij} = (A_{ji})^*$$

**Unitary condition**:
$$U^\dagger U = I \iff \text{columns of } U \text{ are orthonormal}$$

**Pauli algebra**:
$$\sigma_i \sigma_j = \delta_{ij} I + i\varepsilon_{ijk}\sigma_k$$

**Function of a Hermitian operator**:
$$f(A) = \sum_i f(\lambda_i)|i\rangle\langle i|$$

## Worked Example

**Problem**: Find the eigenvalues and eigenvectors of the Hadamard matrix

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$

and verify its spectral decomposition.

**Solution**:

Step 1 — Characteristic equation:

$$\det(H - \lambda I) = \det\begin{pmatrix} \frac{1}{\sqrt{2}} - \lambda & \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{2}} - \lambda \end{pmatrix} = 0$$

$$\left(\frac{1}{\sqrt{2}} - \lambda\right)\left(-\frac{1}{\sqrt{2}} - \lambda\right) - \frac{1}{2} = 0$$

$$\lambda^2 - \frac{1}{2} - \frac{1}{2} = 0 \implies \lambda^2 = 1 \implies \lambda = \pm 1$$

The Hadamard matrix is unitary (check: `H†H = I`) and Hermitian (check: `H = H†`), so we expect real eigenvalues on the unit circle — and indeed we get `±1`.

Step 2 — Eigenvectors:

For `λ = +1`:
$$\left(\frac{1}{\sqrt{2}} - 1\right)\alpha + \frac{1}{\sqrt{2}}\beta = 0 \implies \beta = (\sqrt{2}-1)\alpha$$

Normalized: `|v₊⟩ = cos(π/8)|0⟩ + sin(π/8)|1⟩` (approximately `0.924|0⟩ + 0.383|1⟩`)

For `λ = -1`:
$$\left(\frac{1}{\sqrt{2}} + 1\right)\alpha = \frac{1}{\sqrt{2}}\beta \implies \beta = -(\sqrt{2}+1)\alpha$$

Normalized: `|v₋⟩ = sin(π/8)|0⟩ - cos(π/8)|1⟩` (approximately `0.383|0⟩ - 0.924|1⟩`)

Step 3 — Spectral decomposition verification:

$$H = (+1)|v_+\rangle\langle v_+| + (-1)|v_-\rangle\langle v_-|$$

Computing `|v₊⟩⟨v₊| - |v₋⟩⟨v₋|` returns `H` as expected. Alternatively: note `H² = I` (which follows from `(+1)² = (-1)² = 1` in the spectral decomposition), confirming H is its own inverse.

**Key insight**: The Hadamard gate is an involution (`H² = I`) with eigenvalues `±1`, making it both a reflection (in the eigenvector basis) and its own inverse. This is why applying `H` twice does nothing.

## Summary

- A **vector space** over `ℂ` with an inner product is the mathematical home of quantum states
- **Dirac notation** `|ψ⟩` (ket), `⟨ψ|` (bra), `⟨φ|ψ⟩` (inner product), `|ψ⟩⟨φ|` (outer product) is the standard language of quantum computing
- The **adjoint** `A†` is the conjugate transpose; operators satisfying `A† = A` are Hermitian and represent observables
- **Unitary operators** satisfy `U†U = I`, preserve norms (probabilities), and represent quantum gates
- The **Spectral Theorem** guarantees normal operators diagonalize in an orthonormal basis; this enables defining `e^{iA}`, `√A`, and other operator functions
- The **Pauli matrices** `{I, X, Y, Z}` form a basis for `2×2` Hermitian matrices and encode the geometry of single-qubit states and rotations
- The **completeness relation** `Σᵢ|i⟩⟨i| = I` is used constantly to expand states and operators in any orthonormal basis

## Exercises

**Exercise 1**: Find the eigenvalues and normalized eigenvectors of the Pauli `X` matrix, and verify its spectral decomposition `X = Σᵢ λᵢ|i⟩⟨i|` by explicit matrix computation.

<details><summary>Solution</summary>

The characteristic equation is `det(X - λI) = λ² - 1 = 0`, so `λ = ±1`.

For `λ = +1`: `X|v⟩ = |v⟩` requires the components to be equal, giving `|+⟩ = (|0⟩+|1⟩)/√2`. For `λ = -1`: components opposite, giving `|−⟩ = (|0⟩-|1⟩)/√2`.

Spectral decomposition:

`|+⟩⟨+| = ½[[1,1],[1,1]]` and `|−⟩⟨−| = ½[[1,-1],[-1,1]]`, so

`(+1)|+⟩⟨+| + (-1)|−⟩⟨−| = ½[[1-1, 1+1],[1+1, 1-1]] = [[0,1],[1,0]] = X` ✓

</details>

**Exercise 2**: Expand the Hermitian matrix `A = [[1,2],[2,-1]]` in the Pauli basis, i.e. find real numbers `a, b, c, d` with `A = aI + bX + cY + dZ`.

<details><summary>Solution</summary>

Using orthogonality of the Pauli basis under `⟨A,B⟩ = ½Tr(A†B)`, each coefficient is a half-trace:

- `a = ½Tr(A) = ½(1 + (-1)) = 0`
- `b = ½Tr(XA) = ½Tr([[2,-1],[1,2]]) = ½(2+2) = 2`
- `c = ½Tr(YA) = ½Tr([[-2i, i],[i, 2i]]) = ½(-2i+2i) = 0`
- `d = ½Tr(ZA) = ½Tr([[1,2],[-2,1]]) = ½(1+1) = 1`

So `A = 2X + Z`. Check: `2X + Z = [[0,2],[2,0]] + [[1,0],[0,-1]] = [[1,2],[2,-1]] = A` ✓

</details>

**Exercise 3**: Verify the adjoint rule `(AB)† = B†A†` on the concrete pair `A = X`, `B = S = [[1,0],[0,i]]` by computing both sides explicitly.

<details><summary>Solution</summary>

Left side: `XS = [[0,1],[1,0]][[1,0],[0,i]] = [[0,i],[1,0]]`, so `(XS)† = [[0,1],[-i,0]]`.

Right side: `S† = [[1,0],[0,-i]]` and `X† = X`, so `S†X† = [[1,0],[0,-i]][[0,1],[1,0]] = [[0,1],[-i,0]]`.

Both sides equal `[[0,1],[-i,0]]` ✓. (Note the order reversal is essential: `A†B† = X S† = [[0,-i],[1,0]] ≠ (AB)†`.)

</details>

**Exercise 4**: Show that `V = ½[[1+i, 1-i],[1-i, 1+i]]` is unitary, compute `V²`, and find the eigenvalues of `V`. (This gate is called `√X` or `SX`.)

<details><summary>Solution</summary>

Unitarity: the (1,1) entry of `V†V` is `¼(|1+i|² + |1-i|²) = ¼(2+2) = 1`; the (1,2) entry is `¼((1-i)(1-i) + (1+i)(1+i)) = ¼((-2i) + (2i)) = 0`. By symmetry `V†V = I` ✓.

Squaring:

`V² = ¼[[(1+i)² + (1-i)², 2(1+i)(1-i)],[2(1+i)(1-i), (1+i)² + (1-i)²]] = ¼[[0, 4],[4, 0]] = X`

since `(1+i)² = 2i`, `(1-i)² = -2i`, and `(1+i)(1-i) = 2`. So `V = √X`.

Since `V` commutes with `X` (it is a polynomial in `X`), the eigenvectors of `X` are also eigenvectors of `V`. Applying `V` to `|+⟩`: each component becomes `½((1+i) + (1-i))·(1/√2) = 1/√2`, so `V|+⟩ = |+⟩` (eigenvalue `1`). Applying `V` to `|−⟩`: the components become `±½((1+i) - (1-i))·(1/√2) = ±i/√2`, so `V|−⟩ = i|−⟩` (eigenvalue `i`). Eigenvalues: `{1, i}` — square roots of the eigenvalues `{1, -1}` of `X`, as expected, and both lie on the unit circle as required for a unitary matrix.

</details>

## Further Reading

1. **Nielsen & Chuang**, *Quantum Computation and Quantum Information* (Cambridge, 2000), Chapter 2 — the canonical quantum computing reference; thorough linear algebra review in §2.1
2. **Axler**, *Linear Algebra Done Right* (Springer, 3rd ed.) — rigorous, proof-based treatment of linear algebra over ℂ; excellent on the Spectral Theorem
3. **Halmos**, *Finite-Dimensional Vector Spaces* (Springer) — classic treatment that develops linear algebra and its connection to physics elegantly
4. **Wilde**, *Quantum Information Theory* (Cambridge, 2nd ed.) — free online; Chapter 3 covers the linear algebra of quantum information with care
5. **3Blue1Brown**, *Essence of Linear Algebra* (YouTube series) — exceptional geometric intuition for linear transformations, eigenvectors, and bases; recommended before diving into the formalism
