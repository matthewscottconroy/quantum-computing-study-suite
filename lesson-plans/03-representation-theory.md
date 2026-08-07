# Representation Theory for Quantum Computing

## Goal
Understand how abstract symmetry groups act on quantum state spaces — the framework that explains degeneracies, selection rules, the structure of the Pauli group, and the design of fault-tolerant codes.

---

## Module 1 — Foundations of Representation Theory

**Objective:** Define what a representation is and establish the vocabulary used throughout.

| Topic | Key Concepts |
|---|---|
| Group representation | Homomorphism ρ: G → GL(V), linear action on vector space |
| Degree/dimension | dim(V) |
| Equivalent representations | Related by change of basis: ρ' = SρS⁻¹ |
| Faithful representation | Injective: ker(ρ) = {e} |
| Trivial representation | ρ(g) = 1 for all g |
| Regular representation | V = ℂ[G], G acts by left multiplication |

**Exercises:**
- Write explicit matrix representations for ℤ₄ acting on ℂ²
- Show that the regular representation of S₃ has degree 6
- Prove that equivalent representations have the same character

---

## Module 2 — Reducibility and Irreducibility

**Objective:** Decompose representations into irreducible building blocks — the atomic units of symmetry.

| Topic | Key Concepts |
|---|---|
| Invariant subspace | `ρ(g)W ⊆ W` for all g |
| Reducible representation | Has a proper invariant subspace |
| Irreducible representation (irrep) | No proper invariant subspace |
| Complete reducibility | Every rep of a finite group decomposes into irreps (Maschke's theorem) |
| Direct sum decomposition | `ρ ≅ ⊕ nᵢ ρᵢ` where nᵢ are multiplicities |

**Quantum connections:**
- Energy eigenstates within a degenerate subspace form an invariant subspace
- The tensor product of two irreps decomposes into irreps — this is the Clebsch-Gordan problem

**Exercises:**
- Show that ℂ² as a representation of ℤ₂ (acting by ±1) is reducible
- Decompose the regular representation of ℤ₃ into irreps
- State and apply Maschke's theorem to a specific example

---

## Module 3 — Schur's Lemma and Characters

**Objective:** Use Schur's lemma and characters to classify and compare representations without explicit matrices.

| Topic | Key Concepts |
|---|---|
| Schur's lemma | Intertwiner between irreps is 0 or isomorphism |
| Character | χ_ρ(g) = Tr(ρ(g)), class function |
| Character table | Rows: irreps; columns: conjugacy classes |
| Orthogonality relations | `⟨χᵢ, χⱼ⟩ = δᵢⱼ` (first and second kind) |
| Multiplicity formula | nᵢ = ⟨χ, χᵢ⟩ |
| Number of irreps | = number of conjugacy classes |

**Exercises:**
- Construct the full character table of S₃ and D₄
- Use orthogonality to verify the character table of ℤ₄
- Determine the multiplicity of each irrep in a given reducible representation

---

## Module 4 — Representations of SU(2)

**Objective:** Master SU(2) representations — the mathematical home of spin, qubits, and single-qubit gates.

| Topic | Key Concepts |
|---|---|
| SU(2) irreps labeled by spin-j | j = 0, 1/2, 1, 3/2, … |
| Spin-1/2 representation | The qubit: ρ(U) = U on ℂ² |
| Raising/lowering operators | J₊, J₋ built from Pauli matrices |
| Angular momentum commutation | `[Jₓ, Jᵧ] = iJᵤ` and cyclic |
| Clebsch-Gordan decomposition | `j₁ ⊗ j₂ = |j₁−j₂| ⊕ … ⊕ j₁+j₂` |
| SU(2) → SO(3) double cover | Spinors require 4π rotation to return to identity |

**Quantum connections:**
- Every single-qubit gate is an element of SU(2) — rotations on the Bloch sphere
- Multi-qubit systems decompose under Clebsch-Gordan — relevant to molecular simulation
- The double cover explains why fermionic states acquire a sign under 2π rotation

**Exercises:**
- Write the spin-1 representation matrices for Jₓ, Jᵧ, Jᵤ
- Decompose the tensor product of two spin-1/2 representations: `1/2 ⊗ 1/2`
- Verify the Clebsch-Gordan coefficients for the j=0 singlet state

---

## Module 5 — The Pauli Group as a Representation

**Objective:** Understand the n-qubit Pauli group and its representation-theoretic structure, which underpins quantum error correction.

| Topic | Key Concepts |
|---|---|
| Pauli group P₁ | {±I, ±iI, ±X, ±iX, ±Y, ±iY, ±Z, ±iZ} |
| n-qubit Pauli group Pₙ | Tensor products of single-qubit Paulis with phases |
| Center Z(Pₙ) | {±I, ±iI} |
| Quotient Pₙ/Z(Pₙ) | Isomorphic to GF(2)²ⁿ as abelian group |
| Stabilizer subgroups | Abelian subgroups of Pₙ that fix a code space |
| Weight of a Pauli | Number of non-identity tensor factors |

**Quantum connections:**
- Stabilizer codes are defined by choosing an abelian subgroup S ≤ Pₙ
- The code space is the +1 eigenspace of all elements of S
- Logical operators are the normalizer of S, modulo S itself

**Exercises:**
- List all elements and conjugacy classes of P₁
- Find a set of generators for the stabilizer group of the 3-qubit bit-flip code
- Verify that the stabilizers of the 5-qubit perfect code commute pairwise

---

## Module 6 — Representations in Quantum Algorithm Design

**Objective:** Understand how the representation theory of abelian groups underlies the quantum Fourier transform and hidden subgroup problem.

| Topic | Key Concepts |
|---|---|
| Characters of abelian groups | All irreps are 1-dimensional; character = irrep |
| Fourier transform on finite groups | Decompose functions in terms of irreps |
| Quantum Fourier transform (QFT) | QFT over ℤ_N: `|j⟩ → Σ e^(2πijk/N)|k⟩/√N` |
| Hidden subgroup problem (HSP) | Find H ≤ G given oracle f constant on cosets of H |
| Shor's algorithm as HSP | Group ℤ_N, subgroup generated by period r |
| Non-abelian HSP | Graph isomorphism, shortest vector — open problems |

**Exercises:**
- Derive the QFT matrix for N=4 from the character table of ℤ₄
- Explain why Shor's algorithm solves the HSP for ℤ_N
- Describe what makes the non-abelian HSP hard

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Representation Theory* — Fulton & Harris | Textbook | Standard graduate text |
| *Linear Representations of Finite Groups* — Serre | Textbook | Concise, rigorous |
| *Group Theory and Quantum Mechanics* — Tinkham | Textbook | Physics perspective |
| *Quantum Computation and Quantum Information* Ch.5 — Nielsen & Chuang | Textbook | QFT and HSP |
| Childs lecture notes on quantum algorithms | Notes | Free online, excellent |

---

## Progression Checkpoints

- [ ] Build character tables from scratch for S₃, D₄, ℤₙ
- [ ] Decompose SU(2) tensor products using Clebsch-Gordan
- [ ] Describe the Pauli group's center and quotient structure
- [ ] Construct stabilizer groups for the 3- and 5-qubit codes
- [ ] Derive the QFT from the character theory of ℤ_N
