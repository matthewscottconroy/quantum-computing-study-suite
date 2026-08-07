# Linear Algebra for Quantum Computing

## Goal
Build a rigorous working knowledge of the linear algebra that underlies every quantum computing concept — from state vectors to quantum gates to measurement.

---

## Module 1 — Vector Spaces and the Dirac Notation

**Objective:** Translate standard linear algebra into the bra-ket language used throughout quantum mechanics.

| Topic | Key Concepts |
|---|---|
| Vector spaces over ℂ | Field axioms, closure, basis, dimension |
| Inner product spaces | Hermitian inner product, norm, orthogonality |
| Dirac notation | Kets `|ψ⟩`, bras `⟨ψ|`, inner product `⟨φ|ψ⟩` |
| Hilbert space | Completeness, L² space, finite vs infinite dimensional |
| Tensor products | `|ψ⟩ ⊗ |φ⟩`, how multi-qubit spaces are built |

**Exercises:**
- Express standard basis vectors of ℂ² as `|0⟩` and `|1⟩`
- Compute inner products and verify orthonormality of computational basis
- Construct a 2-qubit Hilbert space ℂ² ⊗ ℂ² and write all four basis states

---

## Module 2 — Linear Maps and Matrices

**Objective:** Understand how quantum gates are linear operators.

| Topic | Key Concepts |
|---|---|
| Linear transformations | Linearity conditions, kernel, image |
| Matrix representations | Change of basis, similarity |
| Composition and inverses | Matrix multiplication as function composition |
| Adjoint (Hermitian conjugate) | `A†`, conjugate transpose, bra-ket duality |
| Operator norms | Spectral norm, Frobenius norm |

**Exercises:**
- Compute `A†` for several complex matrices
- Show that the adjoint of a composition is `(AB)† = B†A†`
- Verify that applying a gate then its adjoint returns the identity

---

## Module 3 — Special Matrices in Quantum Computing

**Objective:** Identify and work with the matrix types that appear constantly in quantum circuits.

| Matrix Type | Definition | Quantum Role |
|---|---|---|
| Hermitian | `A = A†` | Observables, Hamiltonians |
| Unitary | `U†U = I` | Quantum gates (reversibility) |
| Projection | `P² = P`, `P = P†` | Measurement operators |
| Normal | `AA† = A†A` | Diagonalizable in orthonormal basis |
| Positive semi-definite | `⟨ψ|A|ψ⟩ ≥ 0` | Density matrices |

**Exercises:**
- Prove all unitary matrices are normal
- Show that eigenvalues of Hermitian matrices are real
- Verify that Pauli matrices X, Y, Z are both Hermitian and unitary

---

## Module 4 — Eigenvalues, Eigenvectors, and Spectral Theory

**Objective:** Understand measurement outcomes as the spectral decomposition of observables.

| Topic | Key Concepts |
|---|---|
| Eigenvalue equation | `A|v⟩ = λ|v⟩` |
| Characteristic polynomial | `det(A − λI) = 0` |
| Spectral theorem | Normal operators diagonalize in orthonormal basis |
| Spectral decomposition | `A = Σ λᵢ |vᵢ⟩⟨vᵢ|` |
| Functions of operators | `f(A) = Σ f(λᵢ) |vᵢ⟩⟨vᵢ|` |

**Exercises:**
- Find eigenvalues and eigenvectors of all three Pauli matrices
- Use spectral decomposition to compute `e^(iθZ)` — this is the Rz gate
- Verify the spectral decomposition of the Hadamard gate

---

## Module 5 — Tensor Products and Multi-Qubit Systems

**Objective:** Construct multi-qubit state spaces and understand entanglement algebraically.

| Topic | Key Concepts |
|---|---|
| Tensor product of spaces | Dimensions multiply: dim(V ⊗ W) = dim(V)·dim(W) |
| Tensor product of operators | `(A ⊗ B)(|v⟩ ⊗ |w⟩) = A|v⟩ ⊗ B|w⟩` |
| Kronecker product | Matrix representation of `A ⊗ B` |
| Separable vs entangled states | States that cannot be factored as `|a⟩ ⊗ |b⟩` |
| Partial trace | Reduced density matrix, tracing out a subsystem |

**Exercises:**
- Compute the Kronecker product `H ⊗ I` and `CNOT`
- Show that `|Φ⁺⟩ = (|00⟩ + |11⟩)/√2` is not separable
- Use partial trace to find the reduced state of each qubit in `|Φ⁺⟩`

---

## Module 6 — Density Matrices and Mixed States

**Objective:** Handle probabilistic ensembles of quantum states via density operators.

| Topic | Key Concepts |
|---|---|
| Pure vs mixed states | `ρ = |ψ⟩⟨ψ|` vs convex combination |
| Density matrix properties | Trace 1, positive semi-definite, Hermitian |
| Purity | `Tr(ρ²) = 1` iff pure |
| Time evolution | `ρ(t) = U ρ U†` |
| Measurement | `p(m) = Tr(Πₘ ρ)`, post-measurement state |

**Exercises:**
- Construct density matrices for `|+⟩` and the maximally mixed state `I/2`
- Show that `Tr(ρ²) ≤ 1` with equality iff `ρ` is pure
- Compute measurement probabilities in the Z basis for a given `ρ`

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Linear Algebra Done Right* — Axler | Textbook | Proof-based, no determinants first |
| *Quantum Computation and Quantum Information* Ch.2 — Nielsen & Chuang | Textbook | The standard QC reference |
| 3Blue1Brown Essence of Linear Algebra | Video series | Excellent geometric intuition |
| Griffiths QM App. A | Reference | Dirac notation crash course |

---

## Progression Checkpoints

- [ ] Fluently convert between matrix and Dirac notation
- [ ] Verify unitarity and Hermiticity by inspection
- [ ] Derive gates as matrix exponentials of Pauli operators
- [ ] Compute partial traces and reduced density matrices
- [ ] Explain entanglement in terms of separability of tensor products
