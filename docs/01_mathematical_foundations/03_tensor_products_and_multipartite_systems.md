# Tensor Products and Multipartite Systems

> **Prerequisites**: 01_linear_algebra.md (vector spaces, bases, operators), 02_complex_numbers_and_hilbert_spaces.md (inner products, Hilbert spaces)  
> **Connects to**: Multi-qubit states, entanglement, quantum circuits with multiple qubits, density matrices and partial trace, all of quantum algorithms

## Overview

When we want to describe a system composed of multiple parts — two electrons, three qubits, a quantum register — we need a mathematical operation that combines the individual component spaces into a joint space. That operation is the **tensor product** `⊗`.

The tensor product is perhaps the most consequential mathematical construction in quantum information theory. It is what gives quantum computers their exponential state space (two `n`-qubit systems together have `2ⁿ` dimensions), and it is what makes entanglement possible — the existence of joint states that cannot be decomposed into independent states of the parts.

This chapter defines the tensor product rigorously, explains how it combines operators and states, and introduces the **partial trace** — the operation that lets us extract the state of one subsystem from a joint state. We also preview the crucial distinction between separable (unentangled) and entangled states, which will be developed fully in Chapter 2.4.

Understanding tensor products is not just about passing an exam — it is the prerequisite to understanding why quantum computers are hard to simulate classically (the state space is exponentially large), why entanglement is a resource, and how quantum communication protocols work.

## Definition of the Tensor Product

### Bilinear Construction

Let `V` and `W` be complex vector spaces with dimensions `m` and `n` respectively, with bases `{|v₁⟩, ..., |vₘ⟩}` and `{|w₁⟩, ..., |wₙ⟩}`.

The **tensor product** `V ⊗ W` is the `mn`-dimensional vector space spanned by the **elementary tensors** (or **product vectors**):

$$\{|v_i\rangle \otimes |w_j\rangle : 1 \leq i \leq m, 1 \leq j \leq n\}$$

We usually abbreviate `|vᵢ⟩ ⊗ |wⱼ⟩` as `|vᵢ⟩|wⱼ⟩` or `|vᵢwⱼ⟩`.

The tensor product satisfies the following **bilinearity** conditions:

$$(\alpha|v_1\rangle + \beta|v_2\rangle) \otimes |w\rangle = \alpha(|v_1\rangle \otimes |w\rangle) + \beta(|v_2\rangle \otimes |w\rangle)$$

$$|v\rangle \otimes (\alpha|w_1\rangle + \beta|w_2\rangle) = \alpha(|v\rangle \otimes |w_1\rangle) + \beta(|v\rangle \otimes |w_2\rangle)$$

$$\alpha|v\rangle \otimes |w\rangle = |v\rangle \otimes \alpha|w\rangle = \alpha(|v\rangle \otimes |w\rangle)$$

**Important**: Not every vector in `V ⊗ W` is an elementary tensor. A general element is a linear combination:

$$|\Psi\rangle = \sum_{i,j} c_{ij} |v_i\rangle \otimes |w_j\rangle$$

Vectors that *can* be written as `|v⟩ ⊗ |w⟩` for some single `|v⟩ ∈ V` and `|w⟩ ∈ W` are called **product states** or **separable states**. All others are **entangled**. Entanglement is generic — "most" states in `V ⊗ W` are entangled.

### Inner Product on V ⊗ W

The inner product on `V ⊗ W` is defined on elementary tensors by:

$$(\langle v_1| \otimes \langle w_1|)(|v_2\rangle \otimes |w_2\rangle) = \langle v_1|v_2\rangle \cdot \langle w_1|w_2\rangle$$

and extended by linearity. In bra-ket notation: `(⟨v₁| ⊗ ⟨w₁|) = ⟨v₁w₁|`.

For a general state `|Ψ⟩ = Σᵢⱼ cᵢⱼ|vᵢwⱼ⟩` and `|Φ⟩ = Σᵢⱼ dᵢⱼ|vᵢwⱼ⟩`:

$$\langle \Phi|\Psi\rangle = \sum_{i,j} d_{ij}^* c_{ij}$$

## Multi-Qubit Systems

### The n-Qubit Hilbert Space

A single qubit lives in `ℂ²` with basis `{|0⟩, |1⟩}`. For `n` qubits, the joint Hilbert space is:

$$\mathcal{H}_n = \underbrace{\mathbb{C}^2 \otimes \mathbb{C}^2 \otimes \cdots \otimes \mathbb{C}^2}_{n \text{ times}} = \mathbb{C}^{2^n}$$

This is the fundamental reason quantum computers have exponential state space: adding one qubit **doubles** the dimension. A 300-qubit quantum computer has a state space of dimension `2³⁰⁰ ≈ 10⁹⁰` — larger than the number of atoms in the observable universe.

**Standard (computational) basis** for `n = 2`:

$$|00\rangle = |0\rangle \otimes |0\rangle = \begin{pmatrix}1\\0\end{pmatrix} \otimes \begin{pmatrix}1\\0\end{pmatrix} = \begin{pmatrix}1\\0\\0\\0\end{pmatrix}$$

$$|01\rangle = \begin{pmatrix}0\\1\\0\\0\end{pmatrix}, \quad |10\rangle = \begin{pmatrix}0\\0\\1\\0\end{pmatrix}, \quad |11\rangle = \begin{pmatrix}0\\0\\0\\1\end{pmatrix}$$

For general `n`, the computational basis states `|x⟩` are labeled by binary strings `x ∈ {0,1}ⁿ`, interpreted as integers from `0` to `2ⁿ - 1`. The ordering convention is that `|x₁x₂...xₙ⟩` corresponds to the integer `x₁·2^{n-1} + x₂·2^{n-2} + ... + xₙ·2⁰`.

### Kronecker Product

For matrices (operators), the tensor product becomes the **Kronecker product**. If `A` is `m×m` and `B` is `n×n`:

$$A \otimes B = \begin{pmatrix} A_{11}B & A_{12}B & \cdots \\ A_{21}B & A_{22}B & \cdots \\ \vdots & & \ddots \end{pmatrix}$$

Each entry `Aᵢⱼ` of `A` is replaced by the `n×n` block `AᵢⱼB`.

**Example**: `X ⊗ Z` for two qubits:

$$X \otimes Z = \begin{pmatrix}0&1\\1&0\end{pmatrix} \otimes \begin{pmatrix}1&0\\0&-1\end{pmatrix} = \begin{pmatrix}0\cdot Z & 1\cdot Z \\ 1\cdot Z & 0\cdot Z\end{pmatrix} = \begin{pmatrix}0&0&1&0\\0&0&0&-1\\1&0&0&0\\0&-1&0&0\end{pmatrix}$$

### Operator Action on Product States

For a product state `|ψ⟩ ⊗ |φ⟩`, a product operator `A ⊗ B` acts as:

$$(A \otimes B)(|\psi\rangle \otimes |\phi\rangle) = A|\psi\rangle \otimes B|\phi\rangle$$

This is the key: if we apply `A` only to qubit 1 and `B` only to qubit 2, the operator is `A ⊗ B`. If we apply `A` to qubit 1 and nothing (identity) to qubit 2, the operator is `A ⊗ I`.

**Algebraic properties**:
- `(A ⊗ B)(C ⊗ D) = (AC) ⊗ (BD)` — products compose componentwise
- `(A ⊗ B)† = A† ⊗ B†` — adjoint distributes
- `Tr(A ⊗ B) = Tr(A) · Tr(B)` — trace is multiplicative

### Local Operations on n-Qubit Registers

A gate `G` applied to qubit `k` in an `n`-qubit register acts as:

$$I \otimes \cdots \otimes I \otimes \underbrace{G}_{k\text{-th position}} \otimes I \otimes \cdots \otimes I$$

This is a `2ⁿ × 2ⁿ` matrix, but it is efficiently represented as a local operation. For instance, applying `H` to qubit 2 in a 3-qubit system:

$$I \otimes H \otimes I = I_2 \otimes \frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix} \otimes I_2$$

This `8×8` matrix implements Hadamard only on the second qubit.

## Separable and Entangled States

### Product (Separable) States

A two-qubit state `|Ψ⟩ ∈ ℂ² ⊗ ℂ²` is **separable** (a product state) if it can be written as:

$$|\Psi\rangle = |\psi\rangle \otimes |\phi\rangle$$

for some single-qubit states `|ψ⟩` and `|φ⟩`.

**Example**: `|Ψ⟩ = |+⟩ ⊗ |0⟩ = (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2`.

This is separable: qubit 1 is in state `|+⟩` and qubit 2 is in state `|0⟩`. Measuring qubit 2 always gives 0, regardless of qubit 1.

### Entangled States

A state is **entangled** if it is not separable. The canonical examples are the **Bell states**:

$$|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

To see this is entangled, suppose for contradiction that `|Φ⁺⟩ = (α|0⟩+β|1⟩) ⊗ (γ|0⟩+δ|1⟩) = αγ|00⟩ + αδ|01⟩ + βγ|10⟩ + βδ|11⟩`. Comparing coefficients: `αδ = 0` and `βγ = 0`, but `αγ = 1/√2 ≠ 0` and `βδ = 1/√2 ≠ 0`. The first two conditions require either `α = 0` or `δ = 0`, and either `β = 0` or `γ = 0`. But `αγ ≠ 0` requires `α ≠ 0` and `γ ≠ 0`, and `βδ ≠ 0` requires `β ≠ 0` and `δ ≠ 0`. Contradiction. Therefore `|Φ⁺⟩` is entangled.

The physical consequence of entanglement: measuring qubit 1 in `|Φ⁺⟩` gives 0 or 1 with probability 1/2, but measuring qubit 2 **immediately afterwards** gives the same result with certainty, regardless of the distance between the qubits. This correlates the outcomes without any classical communication.

## Partial Trace

### Motivation

If we have a two-qubit system in state `|Ψ⟩ = Σᵢⱼ cᵢⱼ|ij⟩`, what is the state of qubit 1 alone? For a product state `|ψ⟩⊗|φ⟩`, the answer is clear: qubit 1 is in state `|ψ⟩`. But for an entangled state, there is no single pure state for qubit 1 — the answer is a **mixed state**, described by a density matrix (Chapter 2.5).

### Definition

The **partial trace** over system B, written `Tr_B`, takes an operator on `ℋ_A ⊗ ℋ_B` and returns an operator on `ℋ_A`:

$$\rho_A = \text{Tr}_B[\rho_{AB}] = \sum_j (I_A \otimes \langle j|_B)\,\rho_{AB}\,(I_A \otimes |j\rangle_B)$$

where `{|j⟩_B}` is any orthonormal basis for `ℋ_B`. The result is independent of which basis is chosen.

**For a pure product state** `ρ_AB = |ψ⟩⟨ψ| ⊗ |φ⟩⟨φ|`:
$$\rho_A = \text{Tr}_B[|ψ\rangle\langle ψ| \otimes |φ\rangle\langle φ|] = |ψ\rangle\langle ψ|\cdot\text{Tr}(|φ\rangle\langle φ|) = |ψ\rangle\langle ψ|$$

The reduced state of A is `|ψ⟩⟨ψ|` — a pure state, as expected.

**For an entangled state** `|Φ⁺⟩ = (|00⟩+|11⟩)/√2`:

$$\rho_{AB} = |\Phi^+\rangle\langle\Phi^+| = \frac{1}{2}(|00\rangle + |11\rangle)(\langle 00| + \langle 11|)$$
$$= \frac{1}{2}(|00\rangle\langle 00| + |00\rangle\langle 11| + |11\rangle\langle 00| + |11\rangle\langle 11|)$$

Tracing over qubit B:

$$\rho_A = \text{Tr}_B[\rho_{AB}] = \frac{1}{2}(|0\rangle\langle 0|\langle 0|0\rangle + |1\rangle\langle 1|\langle 1|1\rangle) = \frac{1}{2}(|0\rangle\langle 0| + |1\rangle\langle 1|) = \frac{I}{2}$$

The reduced state of qubit A is the maximally mixed state `I/2` — perfect randomness. Each outcome is 50/50, but correlated with qubit B.

### Physical Interpretation

The partial trace answers: "What happens to subsystem A if we ignore subsystem B?" Specifically, for any observable `O_A` that only acts on A:

$$\langle O_A \rangle = \text{Tr}[(O_A \otimes I_B)\rho_{AB}] = \text{Tr}_A[O_A \rho_A]$$

The reduced state `ρ_A` captures everything observable about A in isolation. For a maximally entangled state, `ρ_A = I/2` means that A is locally completely random — all correlations are in the joint state.

**Monogamy of entanglement**: If A and B are maximally entangled (`ρ_A = I/2`), then A cannot be entangled with any third system C. This is why the state `|Φ⁺⟩_AB` tells us nothing about qubit A alone while encoding all the correlations between A and B.

## Key Formulas

**Tensor product dimension**:
$$\dim(V \otimes W) = \dim(V) \cdot \dim(W)$$

**n-qubit Hilbert space**:
$$({\mathbb{C}^2})^{\otimes n} = \mathbb{C}^{2^n}$$

**Bilinear action**:
$$(A \otimes B)(|\psi\rangle \otimes |\phi\rangle) = A|\psi\rangle \otimes B|\phi\rangle$$

**Kronecker product**: If `A` is `m×m` and `B` is `n×n`, then `A⊗B` is `mn×mn` with blocks `AᵢⱼB`.

**Composition rule**:
$$(A \otimes B)(C \otimes D) = (AC) \otimes (BD)$$

**Partial trace**:
$$\rho_A = \text{Tr}_B[\rho_{AB}] = \sum_j (I_A \otimes \langle j|_B)\,\rho_{AB}\,(I_A \otimes |j\rangle_B)$$

**Trace of tensor product**:
$$\text{Tr}(A \otimes B) = \text{Tr}(A)\cdot\text{Tr}(B)$$

## Worked Example

**Problem**: Consider the three-qubit state `|W⟩ = (|100⟩ + |010⟩ + |001⟩)/√3`. Find the reduced state of qubit 1 by tracing out qubits 2 and 3.

**Solution**:

First, write the density matrix:

$$\rho_{123} = |W\rangle\langle W| = \frac{1}{3}(|100\rangle + |010\rangle + |001\rangle)(\langle 100| + \langle 010| + \langle 001|)$$

Expanding:

$$= \frac{1}{3}\bigl(|100\rangle\langle 100| + |100\rangle\langle 010| + |100\rangle\langle 001| + |010\rangle\langle 100| + \cdots\bigr)$$

To trace over qubits 2 and 3, we sum over the four 2-qubit basis states `{|00⟩, |01⟩, |10⟩, |11⟩}` for the system (2,3):

$$\rho_1 = \sum_{j,k \in \{0,1\}} (I_1 \otimes \langle jk|_{23})\,\rho_{123}\,(I_1 \otimes |jk\rangle_{23})$$

To evaluate each term, note that for a term `|abc⟩⟨def|` in `ρ₁₂₃` (with `a, d` labeling qubit 1 and `bc, ef` labeling qubits 2,3):

$$(I \otimes \langle jk|)\,|abc\rangle\langle def|\,(I \otimes |jk\rangle) = \delta_{b,j}\delta_{c,k}\,\delta_{e,j}\delta_{f,k}\; |a\rangle\langle d|$$

Summing over `j, k`, a term survives only if its ket and bra agree on qubits 2,3 (`bc = ef`) — the partial trace extracts the "diagonal" in the 2,3 indices:

- `|100⟩⟨100|`: qubits 2,3 are `|00⟩`. Contributes `|1⟩⟨1| · ⟨00|00⟩ = |1⟩⟨1|`
- `|010⟩⟨010|`: qubits 2,3 are `|10⟩`. Contributes `|0⟩⟨0| · ⟨10|10⟩ = |0⟩⟨0|`
- `|001⟩⟨001|`: qubits 2,3 are `|01⟩`. Contributes `|0⟩⟨0| · ⟨01|01⟩ = |0⟩⟨0|`
- Cross terms `|100⟩⟨010|`, etc.: qubits 2,3 differ between ket and bra, so `⟨jk|jk'⟩ = 0` — they vanish.

Therefore:

$$\rho_1 = \frac{1}{3}(|1\rangle\langle 1| + |0\rangle\langle 0| + |0\rangle\langle 0|) = \frac{1}{3}|1\rangle\langle 1| + \frac{2}{3}|0\rangle\langle 0| = \begin{pmatrix}2/3 & 0 \\ 0 & 1/3\end{pmatrix}$$

This is a **mixed state** (classical mixture): qubit 1 is `|0⟩` with probability 2/3 and `|1⟩` with probability 1/3. The three-qubit `|W⟩` state is entangled, so its reduced state is mixed.

**Note**: The W state is entangled, but differently from GHZ-type states. The W state has the property that tracing out any one qubit still leaves the other two qubits entangled — it is **robustly entangled**. The GHZ state `(|000⟩+|111⟩)/√2`, by contrast, loses all entanglement when any one qubit is traced out: the remaining pair is left in the separable classical mixture `(|00⟩⟨00|+|11⟩⟨11|)/2`.

## Summary

- The **tensor product** `V ⊗ W` has dimension `dim(V) · dim(W)`; for `n` qubits, this is `2ⁿ`
- Elementary tensors `|ψ⟩ ⊗ |φ⟩` are product states; **most** states in the tensor product are entangled (linear combinations that cannot be factored)
- For matrices, the tensor product is the **Kronecker product**: each entry of `A` gets replaced by the block `AᵢⱼB`
- Product operators act locally: `(A⊗B)(|ψ⟩⊗|φ⟩) = A|ψ⟩ ⊗ B|φ⟩`
- The **partial trace** `Tr_B[ρ_AB]` gives the reduced state of A; it equals a mixed state whenever A and B are entangled
- Entanglement is a consequence of the tensor product structure: without `⊗`, there would be no entanglement and quantum computers would offer no superclassical advantage

## Exercises

**Exercise 1**: Write `|+⟩ ⊗ |−⟩` as an explicit 4-component vector in the computational basis. Then determine whether the state `|χ⟩ = (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2` is separable or entangled.

<details><summary>Solution</summary>

Product state:

`|+⟩ ⊗ |−⟩ = ½(|0⟩+|1⟩)(|0⟩-|1⟩) = ½(|00⟩ - |01⟩ + |10⟩ - |11⟩)`, i.e. the vector `(1, -1, 1, -1)/2`.

For `|χ⟩`, arrange the coefficients into the matrix `C = ½[[1, 1],[1, -1]]` (rows = qubit 1, columns = qubit 2). A two-qubit state is separable iff this matrix has rank 1, i.e. iff `det C = 0`. Here `det C = ¼(-1 - 1) = -½ ≠ 0`, so `|χ⟩` is **entangled**. (In fact `CC† = ½I`, so both Schmidt coefficients are `1/√2` — `|χ⟩` is maximally entangled.)

</details>

**Exercise 2**: Compute the `4×4` matrix `Z ⊗ X` and verify that `|1⟩ ⊗ |+⟩` is an eigenvector with eigenvalue `-1`.

<details><summary>Solution</summary>

By the Kronecker product rule (each entry of `Z` multiplies a copy of `X`):

`Z ⊗ X = [[0,1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,-1,0]]`

The state `|1⟩ ⊗ |+⟩ = (0, 0, 1, 1)/√2`. Applying the matrix: rows 3 and 4 give `(-1)·(1/√2)` and `(-1)·(1/√2)` respectively, so the result is `(0, 0, -1, -1)/√2 = -(|1⟩⊗|+⟩)` ✓.

This also follows structurally: `(Z⊗X)(|1⟩⊗|+⟩) = Z|1⟩ ⊗ X|+⟩ = (-|1⟩) ⊗ (+|+⟩) = -|1⟩⊗|+⟩`.

</details>

**Exercise 3**: Using the composition rule `(A⊗B)(C⊗D) = (AC)⊗(BD)`, show that `(X⊗X)(Z⊗Z) = (Z⊗Z)(X⊗X)` — i.e. `X⊗X` and `Z⊗Z` commute, even though `X` and `Z` anticommute individually.

<details><summary>Solution</summary>

Using the composition rule and `XZ = -ZX`:

`(X⊗X)(Z⊗Z) = (XZ)⊗(XZ) = (-ZX)⊗(-ZX) = (-1)(-1)·(ZX)⊗(ZX) = (ZX)⊗(ZX) = (Z⊗Z)(X⊗X)`

The two minus signs from the two factors cancel. This commutation is fundamental to quantum error correction: `X⊗X` and `Z⊗Z` can be measured simultaneously, and their joint eigenspaces are exactly the four Bell states.

</details>

**Exercise 4**: For the two-qubit state `|ψ⟩ = (|00⟩ + |01⟩ + |11⟩)/√3`, compute the reduced density matrix `ρ_B = Tr_A[|ψ⟩⟨ψ|]` of the second qubit, and use its purity `Tr(ρ_B²)` to decide whether the state is entangled.

<details><summary>Solution</summary>

Coefficient matrix (rows = qubit A, columns = qubit B): `C = (1/√3)[[1, 1],[0, 1]]`.

The reduced state of B is `ρ_B = (C†C)ᵀ` in general, which equals `C†C` here because `C` is real:

`C†C = (1/3)[[1, 0],[1, 1]]·[[1, 1],[0, 1]] = (1/3)[[1, 1],[1, 2]]`

Check: `Tr(ρ_B) = (1+2)/3 = 1` ✓.

Purity: `ρ_B² = (1/9)[[2, 3],[3, 5]]`, so `Tr(ρ_B²) = 7/9 < 1`.

Since the reduced state is mixed, the joint pure state is **entangled**. (Equivalently `det C = 1/3 ≠ 0`, so the Schmidt rank is 2. The eigenvalues of `ρ_B` are `(3±√5)/6 ≈ 0.873, 0.127`, giving entanglement entropy `S ≈ 0.55` ebits — entangled but not maximally.)

</details>

## Further Reading

1. **Nielsen & Chuang**, *Quantum Computation and Quantum Information*, §2.1.7–2.1.8 — tensor products and the partial trace; §2.4 covers density operators and reduced states
2. **Wilde**, *Quantum Information Theory*, Chapter 3 — tensor products and composite systems with careful notation
3. **Roman**, *Advanced Linear Algebra* (Springer) — Chapter on tensor products for a fully rigorous algebraic treatment
4. **Preskill**, *Lecture Notes for Physics 229*, Chapter 2 — excellent physical motivation for why tensor products are the right structure for composite quantum systems
5. **Harrow**, *The Church of the Symmetric Subspace* (arXiv:1308.6595) — advanced treatment of symmetric and antisymmetric subspaces of tensor products; relevant for quantum algorithms on identical particles
