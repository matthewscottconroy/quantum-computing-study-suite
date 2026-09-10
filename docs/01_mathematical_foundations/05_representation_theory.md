# Representation Theory for Quantum Computing

> **Prerequisites**: 01_linear_algebra.md (eigendecomposition, trace, unitaries), 03_tensor_products_and_multipartite_systems.md (tensor products of operators), 04_groups_and_abstract_algebra.md (groups, cosets, homomorphisms, `SU(2)`, the Pauli group)  
> **Connects to**: Angular momentum addition in `02_quantum_mechanics/08_angular_momentum_and_hydrogen.md`, the QFT in `04_quantum_algorithms/03_quantum_fourier_transform.md`, Simon's algorithm in `04_quantum_algorithms/02_deutsch_jozsa_and_bernstein_vazirani.md`, the hidden-subgroup view of `04_quantum_algorithms/06_shors_algorithm.md`, symmetry-adapted ansätze in `06_variational_quantum_algorithms/02_ansatz_design.md`

## Overview

A group is an abstract list of symmetries; a **representation** is that list made concrete as matrices acting on a vector space. Quantum mechanics hands us representations constantly: rotations act on the two-dimensional state space of a spin-½, the permutations of identical particles act on their joint Hilbert space, the group `ℤ_N` acts on an `N`-dimensional register by cyclic shift. Representation theory asks how such an action breaks the space into pieces that cannot be broken further — the **irreducible representations** — and the answer explains degeneracies of Hamiltonians, selection rules, why the quantum Fourier transform has the matrix it has, and why Shor's and Simon's algorithms are the *same* algorithm run on different groups.

This chapter develops the finite-group theory first: invariant subspaces, Maschke's theorem, Schur's lemma, characters and their orthogonality, and the character tables of `ℤ_N`, `S_3` and `D_4`. It then turns to `SU(2)`, whose irreducible representations are the spin-`j` multiplets and whose tensor products decompose by Clebsch-Gordan. The final sections make the algorithmic payoff explicit: Fourier analysis on a finite abelian group *is* the character table, the QFT is its unitary matrix, and the hidden subgroup problem is the problem of reading a subgroup off Fourier samples — easy when all irreps are one-dimensional, and stubbornly hard when they are not.

## Representations

### Definitions

A **representation** of a group `G` on a complex vector space `V` is a homomorphism

`ρ: G → GL(V)`, `ρ(gh) = ρ(g)ρ(h)`, `ρ(e) = I`

The **dimension** (or degree) of `ρ` is `dim V`. Two representations are **equivalent** if they differ by a change of basis, `ρ'(g) = S ρ(g) S⁻¹` for a fixed invertible `S`. A representation is **faithful** if `ρ` is injective. For a finite group every representation is equivalent to a **unitary** one (average any inner product over the group), so we assume `ρ(g)` unitary throughout — exactly the situation in quantum mechanics, where symmetries act by unitaries.

Standard examples:

- The **trivial** representation `ρ(g) = 1` on `ℂ`
- The **sign** representation of `S_n`, `ρ(σ) = sgn(σ)` on `ℂ`
- The **permutation** representation of `S_n` on `ℂⁿ`: `ρ(σ) e_i = e_{σ(i)}`
- The **defining** representation of `SU(2)` on `ℂ²` — the qubit
- The **regular** representation of a finite `G` on `ℂ[G] = span{|g⟩ : g ∈ G}`, `ρ(g)|h⟩ = |gh⟩`, of dimension `|G|`
- The qubit representation of `D_4 ≅ ⟨X, Z⟩`, in which the square's symmetries act by Pauli matrices

### Invariant Subspaces and Irreducibility

A subspace `W ⊆ V` is **invariant** if `ρ(g)W ⊆ W` for all `g`. A representation with no invariant subspaces other than `{0}` and `V` is **irreducible** (an **irrep**); otherwise it is **reducible**. If `W` is invariant and `ρ` is unitary then `W^⊥` is invariant too, so `V = W ⊕ W^⊥` as representations.

**Maschke's theorem** (extended to compact groups by Weyl's unitarian trick): every finite-dimensional representation of a finite group, or of a compact Lie group, decomposes as a direct sum of irreps,

`V ≅ n_1 V_1 ⊕ n_2 V_2 ⊕ ... ⊕ n_k V_k`

with multiplicities `n_i ≥ 0`, and the decomposition is unique up to equivalence. Physically: a Hamiltonian commuting with a symmetry group is block-diagonal in the irrep decomposition, and states in a single irreducible block are forced to be degenerate. This is why the action of `S_n` on `n` qubits by permuting tensor factors splits into the symmetric sector and mixed-symmetry sectors (an antisymmetric sector exists only for `n = 2`, since a qubit has two levels — see Schur-Weyl below) and why symmetry-preserving ansätze in Chapter 6 search a smaller space.

### Schur's Lemma

Let `ρ_1` on `V_1` and `ρ_2` on `V_2` be irreps, and let `T: V_1 → V_2` be an **intertwiner**, `T ρ_1(g) = ρ_2(g) T` for all `g`. Then:

1. `T = 0` or `T` is an isomorphism (so `ρ_1 ≅ ρ_2`)
2. If `V_1 = V_2` and `ρ_1 = ρ_2`, then `T = λI` for some scalar `λ`

*Proof sketch.* `ker T` is invariant under `ρ_1` (if `Tv = 0` then `T ρ_1(g) v = ρ_2(g) T v = 0`), so by irreducibility it is `{0}` or `V_1`; likewise `im T` is invariant under `ρ_2`, so it is `{0}` or `V_2`. Either `T = 0` or `T` is injective and surjective. For (2), take any eigenvalue `λ` of `T` (which exists over `ℂ`); `T - λI` is also an intertwiner and has nontrivial kernel, hence is zero.

Consequences: an operator commuting with an irreducible symmetry action is a scalar (a Casimir such as `J²` is constant on each spin multiplet); all irreps of an abelian group are one-dimensional (each `ρ(h)` commutes with the whole action, so is a scalar, so every 1-dimensional subspace is invariant). Numerically, the space of matrices commuting with the 2-dimensional standard representation of `S_3` is 1-dimensional (just `λI`), while for the reducible 3-dimensional permutation representation it is 2-dimensional — the dimension of the commutant counts `Σ n_i²`.

## Characters

### Definition and Basic Properties

The **character** of `ρ` is the function `χ_ρ(g) = Tr ρ(g)`. Since the trace is basis-independent, equivalent representations have equal characters, and since `Tr(ρ(h)ρ(g)ρ(h)⁻¹) = Tr ρ(g)`, characters are **class functions**: constant on conjugacy classes. Also `χ(e) = dim V`, `χ(g⁻¹) = χ(g)*`, `χ_{V⊕W} = χ_V + χ_W`, and `χ_{V⊗W} = χ_V · χ_W`.

### Orthogonality Relations

Define the inner product on class functions

`⟨χ, ψ⟩ = (1/|G|) Σ_{g∈G} χ(g)* ψ(g) = (1/|G|) Σ_{classes C} |C| χ(C)* ψ(C)`

**Theorem (orthogonality of irreducible characters)**: the characters of inequivalent irreps satisfy `⟨χ_i, χ_j⟩ = δ_ij`, and they form an orthonormal basis of the space of class functions. Hence:

- The number of irreps equals the number of conjugacy classes
- The multiplicity of `V_i` in `V` is `n_i = ⟨χ_i, χ_V⟩`
- `⟨χ_V, χ_V⟩ = Σ n_i²`; in particular `V` is irreducible iff `⟨χ_V, χ_V⟩ = 1`
- The regular representation contains each irrep `d_i = dim V_i` times, so `Σ_i d_i² = |G|`

A **character table** lists the irreducible characters (rows) on the conjugacy classes (columns). It becomes a square unitary matrix once the entry in column `C` is multiplied by `√(|C|/|G|)`, which is where the "column orthogonality" relation `Σ_i χ_i(C)* χ_i(C') = (|G|/|C|) δ_{CC'}` comes from.

### Character Tables of ℤ_N and D_4

`ℤ_N` is abelian, so it has `N` one-dimensional irreps, `χ_k(j) = ω^{jk}` with `ω = e^{2πi/N}`, `k = 0, ..., N-1`. For `N = 4`:

| `ℤ_4` | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| `χ_0` | 1 | 1 | 1 | 1 |
| `χ_1` | 1 | `i` | −1 | `−i` |
| `χ_2` | 1 | −1 | 1 | −1 |
| `χ_3` | 1 | `−i` | −1 | `i` |

Orthogonality says `(1/N) Σ_j χ_k(j)* χ_l(j) = δ_kl`, i.e. the matrix `T_{kj} = ω^{jk}/√N` is unitary — it is the **discrete Fourier transform**, and its rows are the characters (verified numerically: `T T† = I`).

`D_4 = ⟨r, s | r⁴ = s² = e, srs = r⁻¹⟩` has 8 elements in 5 classes: `{e}`, `{r²}`, `{r, r³}`, `{s, r²s}` (reflections in the two axes) and `{rs, r³s}` (reflections in the two diagonals). Five classes means five irreps, and `Σ d_i² = 8` forces `1, 1, 1, 1, 2`. The one-dimensional ones send `r ↦ ±1`, `s ↦ ±1` (the relations force `χ(r)² = 1` since `χ(r) = χ(srs) = χ(r)⁻¹`); the two-dimensional one is the geometric action on the plane, `r ↦ [[0,-1],[1,0]]`, `s ↦ [[1,0],[0,-1]]`:

| `D_4` | `e` | `r²` | `r, r³` | `s, r²s` | `rs, r³s` |
|---|---|---|---|---|---|
| class size | 1 | 1 | 2 | 2 | 2 |
| `χ_{++}` | 1 | 1 | 1 | 1 | 1 |
| `χ_{+−}` | 1 | 1 | 1 | −1 | −1 |
| `χ_{−+}` | 1 | 1 | −1 | 1 | −1 |
| `χ_{−−}` | 1 | 1 | −1 | −1 | 1 |
| `χ_E` | 2 | −2 | 0 | 0 | 0 |

(Subscripts give `(χ(r), χ(s))`.) The Gram matrix of these five rows under `⟨·,·⟩` is the `5×5` identity (checked numerically). The qubit connection: `⟨X, Z⟩ = {±I, ±X, ±Z, ±XZ}` is a copy of `D_4` with `r = XZ` (order 4, since `(XZ)² = -I`) and `s = X` (check `srs⁻¹ = X·XZ·X = ZX = (XZ)⁻¹`). The Pauli matrices then realise `χ_E`: `Tr(±I) = ±2` and `Tr(±X) = Tr(±Z) = Tr(±XZ) = 0`, matching the last row. The single-qubit Pauli action is the unique two-dimensional irrep of `D_4`.

## Tensor Products and Clebsch-Gordan

If `ρ_1` and `ρ_2` are representations of the same group `G`, the **tensor product representation** on `V_1 ⊗ V_2` is `g ↦ ρ_1(g) ⊗ ρ_2(g)` (the *same* `g` on both factors — this is a representation of `G`, not of `G × G`). Its character is the product `χ_1 χ_2`, and it is generally reducible even when the factors are irreducible. Decomposing `V_i ⊗ V_j = ⊕_k N_{ij}^k V_k` is the **Clebsch-Gordan problem**; the coefficients `N_{ij}^k = ⟨χ_k, χ_i χ_j⟩` follow from the character table, and the unitary change of basis from product states to irrep states is the matrix of **Clebsch-Gordan coefficients**. For `S_3`, the standard representation satisfies `χ_std² = (4, 0, 1)` on the classes `(e, transpositions, 3-cycles)`, which decomposes as `triv ⊕ sgn ⊕ std` — every irrep exactly once.

## Representations of SU(2)

`SU(2)` is compact, so Maschke and Schur still apply, with sums over `G` replaced by integrals against the Haar measure. Its irreps are classified by a **spin** `j ∈ {0, ½, 1, 3/2, ...}`; the spin-`j` irrep `V_j` has dimension `2j + 1` with basis `|j, m⟩`, `m = -j, ..., j`, on which the generators act by the angular-momentum matrices of `02_quantum_mechanics/08_angular_momentum_and_hydrogen.md`. `V_0` is trivial, `V_½ = ℂ²` is the qubit, `V_1 = ℂ³` is the vector representation that factors through `SO(3)`. The character of `V_j` depends only on the rotation angle `θ` (conjugacy classes of `SU(2)` are labelled by `θ ∈ [0, 2π]`):

`χ_j(θ) = sin((2j+1)θ/2) / sin(θ/2)`

For `j = ½` this is `2cos(θ/2)`, for `j = 1` it is `1 + 2cos θ`. Integer-`j` characters are `2π`-periodic; half-integer ones satisfy `χ_j(θ + 2π) = -χ_j(θ)` — the character-theoretic shadow of the double cover of Chapter 1.4. Whether a representation of `SU(2)` descends to `SO(3)` is exactly whether `-I` acts trivially, which happens iff `j` is an integer.

**Clebsch-Gordan for SU(2)**: `V_{j_1} ⊗ V_{j_2} ≅ V_{|j_1 - j_2|} ⊕ V_{|j_1 - j_2| + 1} ⊕ ... ⊕ V_{j_1 + j_2}`, each summand once. Two qubits give `½ ⊗ ½ = 1 ⊕ 0`: the triplet and the singlet `|Ψ⁻⟩`. A spin-1 with a spin-½ gives `1 ⊗ ½ = 3/2 ⊕ ½`, dimensions `6 = 4 + 2`; numerically, the total Casimir `J²` on `ℂ³ ⊗ ℂ²` has eigenvalue `15/4` with multiplicity 4 and `3/4` with multiplicity 2 (units `ħ = 1` here and in Exercise 4; Chapter 2.8 keeps the `ħ²`), and the characters satisfy `χ_1(θ) χ_½(θ) = χ_{3/2}(θ) + χ_½(θ)` at every `θ`.

**Schur-Weyl duality** in one paragraph: on `(ℂ²)^{⊗n}`, the group `SU(2)` acts by `U^{⊗n}` and `S_n` acts by permuting factors; the two actions commute, and each is the full commutant of the other. Consequently `(ℂ²)^{⊗n} ≅ ⊕_j V_j ⊗ W_j`, where `W_j` is an irrep of `S_n` — the spin-`j` sector of `n` qubits carries a definite permutation symmetry. This is the algebraic engine behind the symmetric subspace, Schur sampling, spectrum estimation of unknown states, and collective decoherence-free subspaces.

## Fourier Analysis on Finite Abelian Groups and the QFT

For a finite abelian group `G` every irrep is a character `χ: G → U(1)`, and the characters themselves form a group `Ĝ ≅ G` (the **dual group**). Orthogonality of characters says the functions `{χ/√|G|}` are an orthonormal basis of `ℂ[G] = ℂ^{|G|}`, so any `f: G → ℂ` expands uniquely as

`f̂(χ) = (1/√|G|) Σ_{g∈G} χ(g) f(g)`, `f(g) = (1/√|G|) Σ_{χ∈Ĝ} f̂(χ) χ(g)*`

This is the **Fourier transform on G**, and the unitary implementing it on a quantum register is the **quantum Fourier transform**. (Many texts put the conjugate on the forward transform instead; the two conventions differ only by the relabelling `χ ↦ χ*`, and the sign chosen here is the one that matches the corpus QFT `F_{kj} = ω^{jk}/√N` exactly.) For `G = ℤ_N` the characters are `χ_k(j) = e^{2πijk/N}`, so `QFT|j⟩ = (1/√N) Σ_k e^{2πijk/N}|k⟩`: the `k`-th row of the QFT matrix of `04_quantum_algorithms/03_quantum_fourier_transform.md` is the character `χ_k` divided by `√N`. For `G = (ℤ_2)ⁿ` the characters are `χ_y(x) = (-1)^{x·y}` and the Fourier transform is `H^{⊗n}` — the "orthogonality of characters" that Chapter 4.2 invokes for Deutsch-Jozsa and Simon is the `(ℤ_2)ⁿ` case of the relations above. The same theorem also explains why the QFT diagonalises the cyclic shift `|j⟩ ↦ |j+1⟩` (the regular representation of `ℤ_N`) — the shift's eigenvectors are the characters and its eigenvalue on the vector `Σ_j χ_k(j)|j⟩` is `ω^{-k}` (`01_mathematical_foundations/07_number_theory_and_fourier_analysis.md` labels the conjugate vector `|χ_k⟩` and so quotes `ω^{k}`); for `ℤ_3` the eigenvalues are `1, e^{±2πi/3}`.

## The Hidden Subgroup Problem

**HSP**: given a group `G` and oracle access to `f: G → S` that is constant on the left cosets of an unknown subgroup `H` and takes distinct values on distinct cosets, find (generators of) `H`.

Simon's problem is HSP on `(ℤ_2)ⁿ` with `H = {0, s}`; period finding — the core of Shor's algorithm — is HSP on `ℤ_N` with `H = ⟨r⟩`; discrete logarithm is HSP on `ℤ_N × ℤ_N`. The standard quantum algorithm prepares `Σ_g |g⟩|f(g)⟩`, measures the second register to collapse the first to a uniform superposition over a coset `|gH⟩ = (1/√|H|) Σ_{h∈H} |gh⟩`, and applies the QFT. Representation theory says what comes out. Because `Σ_{h∈H} χ(h)` equals `|H|` if `χ` is trivial on `H` and `0` otherwise, the Fourier transform of a coset state is supported only on the **annihilator** `H^⊥ = {χ ∈ Ĝ : χ(h) = 1 ∀h ∈ H}`, with the unknown coset shift `g` appearing only as a phase `χ(g)` that measurement discards. Each run therefore returns a uniformly random `χ ∈ H^⊥`, and `O(log|G|)` runs pin down `H^⊥`, hence `H`. For `H = {0, s} ≤ (ℤ_2)³` with `s = 110`, the samples are `y ∈ {000, 001, 110, 111}` — exactly the `y` with `y·s = 0`; for `H = ⟨4⟩ ≤ ℤ_12`, the QFT of a coset state puts probability `1/4` on each of `k ∈ {0, 3, 6, 9}` and zero elsewhere. This works precisely because every irrep of an abelian group is one-dimensional, so "Fourier sampling" returns a label `χ` and nothing is lost.

**The non-abelian obstacle.** For non-abelian `G` — the symmetric group for graph isomorphism, the dihedral group for lattice problems — the Fourier transform over `G` still exists (below), but an irrep `ρ` of dimension `d_ρ > 1` contributes a `d_ρ × d_ρ` block, and the coset state's information hides in the *matrix entries* of that block in a basis that depends on the unknown `H`. Measuring only the irrep label ("weak Fourier sampling") is provably insufficient for `S_n`, and no efficient strategy for the general case is known; an efficient algorithm for the dihedral HSP would solve a lattice problem (unique shortest vector) believed to be hard (Regev), and the best known dihedral algorithm (Kuperberg) is subexponential. This is the sharp mathematical reason Shor's algorithm has not generalised to break lattice-based post-quantum cryptography.

**Peter-Weyl theorem.** For a finite (or compact) group `G`, the matrix coefficients `√(d_ρ) ρ(g)_{ij}` of a complete set of inequivalent unitary irreps form an orthonormal basis of `L²(G)`; equivalently `ℂ[G] ≅ ⊕_ρ V_ρ ⊗ V_ρ*` as a `G × G` representation, so `Σ_ρ d_ρ² = |G|`. The non-abelian Fourier transform is the unitary change of basis from `{|g⟩}` to `{|ρ, i, j⟩}`; efficient circuits for it exist for `S_n` and many other families, which is why the difficulty of non-abelian HSP lies in the *measurement*, not the transform.

## Key Formulas

**Representation**: `ρ: G → GL(V)`, `ρ(gh) = ρ(g)ρ(h)`

**Maschke**: `V ≅ ⊕_i n_i V_i` (finite or compact `G`)

**Schur**: intertwiner between irreps is `0` or an isomorphism; a self-intertwiner of an irrep is `λI`

**Character inner product**: `⟨χ, ψ⟩ = (1/|G|) Σ_g χ(g)* ψ(g)`

**Orthogonality and multiplicities**: `⟨χ_i, χ_j⟩ = δ_ij`, `n_i = ⟨χ_i, χ_V⟩`, `⟨χ_V, χ_V⟩ = Σ n_i²`

**Sum of squares**: `Σ_i d_i² = |G|`; number of irreps = number of conjugacy classes

**Tensor products**: `χ_{V⊗W} = χ_V χ_W`, `N_{ij}^k = ⟨χ_k, χ_i χ_j⟩`

**SU(2) characters and Clebsch-Gordan**: `χ_j(θ) = sin((2j+1)θ/2)/sin(θ/2)`; `V_{j_1} ⊗ V_{j_2} = ⊕_{J=|j_1-j_2|}^{j_1+j_2} V_J`

**Characters of ℤ_N are the QFT**: `χ_k(j) = e^{2πijk/N}`, `QFT_{kj} = χ_k(j)/√N`

**Abelian HSP**: QFT of a coset state of `H` is uniform on `H^⊥ = {χ : χ|_H = 1}`

## Worked Example

**Problem**: Build the full character table of `S_3` and use it to decompose the 3-dimensional permutation representation `ρ(σ) e_i = e_{σ(i)}` into irreps.

**Solution**:

Step 1 — Conjugacy classes. Conjugacy in `S_n` is the same as cycle type, so `S_3` has three classes: the identity `{e}` (size 1), the three transpositions `{(12), (13), (23)}` (size 3), and the two 3-cycles `{(123), (132)}` (size 2). Three classes, hence three irreps, and `Σ d_i² = 6` forces dimensions `1, 1, 2`.

Step 2 — The two one-dimensional irreps are the trivial character `χ_triv = (1, 1, 1)` and the sign `χ_sgn = (1, -1, 1)` (transpositions are odd, 3-cycles are even).

Step 3 — The two-dimensional irrep. The permutation representation fixes the vector `e_1 + e_2 + e_3`, so the orthogonal complement `W = {v : v_1 + v_2 + v_3 = 0}` is a 2-dimensional invariant subspace, the **standard representation**. In the basis `w_1 = e_1 - e_2`, `w_2 = e_2 - e_3` (which spans `W` but is not orthonormal — traces do not care), the transposition `(23)` acts by `w_1 ↦ e_1 - e_3 = w_1 + w_2`, `w_2 ↦ e_3 - e_2 = -w_2`, giving the matrix `[[1, 0], [1, -1]]` with trace `0`; the 3-cycle `(123)` (sending `1 → 2 → 3 → 1`) acts by `w_1 ↦ e_2 - e_3 = w_2`, `w_2 ↦ e_3 - e_1 = -w_1 - w_2`, giving `[[0, -1], [1, -1]]` with trace `-1`. So `χ_std = (2, 0, -1)`.

Step 4 — The table, with class sizes:

| `S_3` | `e` (1) | `(ab)` (3) | `(abc)` (2) |
|---|---|---|---|
| `χ_triv` | 1 | 1 | 1 |
| `χ_sgn` | 1 | −1 | 1 |
| `χ_std` | 2 | 0 | −1 |

Verify orthonormality: `⟨χ_std, χ_std⟩ = (1·4 + 3·0 + 2·1)/6 = 1` ✓ (so `std` really is irreducible); `⟨χ_triv, χ_sgn⟩ = (1 - 3 + 2)/6 = 0` ✓; `⟨χ_triv, χ_std⟩ = (2 + 0 - 2)/6 = 0` ✓; `⟨χ_sgn, χ_std⟩ = (2 + 0 - 2)/6 = 0` ✓. Column check on the transposition class: `1² + 1² + 0² = 2 = 6/3` ✓.

Step 5 — Character of the permutation representation. `Tr ρ(σ)` counts fixed points: `χ_perm = (3, 1, 0)`.

Step 6 — Multiplicities by inner product:

- `n_triv = ⟨χ_triv, χ_perm⟩ = (1·3 + 3·1·1 + 2·1·0)/6 = 6/6 = 1`
- `n_sgn = ⟨χ_sgn, χ_perm⟩ = (3 - 3 + 0)/6 = 0`
- `n_std = ⟨χ_std, χ_perm⟩ = (2·3 + 0 + 0)/6 = 1`

Therefore `ℂ³ ≅ triv ⊕ std`, consistent with dimensions `3 = 1 + 2` and with `⟨χ_perm, χ_perm⟩ = (9 + 3 + 0)/6 = 2 = 1² + 1²` (two distinct irreducible constituents, each once). Numerically: constructing all six `3×3` permutation matrices, computing the standard-representation matrices by restriction to `W`, and evaluating the inner products above reproduces `(1, 0, 1)` exactly; the commutant of the permutation representation is 2-dimensional (`= Σ n_i²`) while that of `std` is 1-dimensional, as Schur's lemma predicts.

**Physical reading**: for three qubits, the same `S_3` acts by permuting tensor factors, and the three states `|100⟩, |010⟩, |001⟩` carry precisely this permutation representation. The trivial component is the `W` state `(|100⟩ + |010⟩ + |001⟩)/√3` of Chapter 1.3 — the unique permutation-symmetric state in that sector — and the standard component is the two-dimensional space of "one excitation with a phase pattern", the two-dimensional `m = +½` slice of the `j = ½` sector predicted by Schur-Weyl for `n = 3` (that sector is `V_½ ⊗ W_½`, with `W_½ = std`).

## Summary

- A **representation** turns group elements into matrices; **irreps** are the indecomposable ones, and by **Maschke** every finite-group representation is a direct sum of irreps
- **Schur's lemma**: operators commuting with an irrep are scalars; abelian groups have only one-dimensional irreps
- **Characters** `χ(g) = Tr ρ(g)` are class functions; irreducible characters are orthonormal, multiplicities are `⟨χ_i, χ_V⟩`, and `Σ d_i² = |G|`
- The **character table** of `ℤ_N` is the QFT matrix (up to `1/√N`); that of `D_4` has four one-dimensional rows and one two-dimensional row realised by the Pauli matrices
- **Tensor products** of representations decompose by **Clebsch-Gordan**; for `SU(2)`, `V_{j_1} ⊗ V_{j_2} = ⊕ V_J` with `J` from `|j_1 - j_2|` to `j_1 + j_2`
- `SU(2)` irreps are the spin-`j` multiplets of dimension `2j + 1`; half-integer `j` do not descend to `SO(3)`; **Schur-Weyl** pairs them with `S_n` irreps on `n` qubits
- The abelian **hidden subgroup problem** is solved by Fourier sampling because the QFT of a coset state is supported on the annihilator `H^⊥`; **non-abelian** irreps of dimension `> 1` hide the answer in matrix entries, which is why graph isomorphism and lattice problems resist the same attack
- **Peter-Weyl**: matrix coefficients of irreps form an orthonormal basis of functions on `G`, generalising Fourier series

## Exercises

**Exercise 1**: The group `ℤ_4` acts on `ℝ² ⊂ ℂ²` by rotating the plane through `90°` per generator: `ρ(1) = [[0, -1], [1, 0]]`. Compute its character on all four elements, decompose it into the irreps `χ_0, ..., χ_3` of the `ℤ_4` table above, and identify the invariant one-dimensional subspaces.

<details><summary>Solution</summary>

`ρ(0) = I`, `ρ(1) = R`, `ρ(2) = R² = -I`, `ρ(3) = R³ = -R`, so the character is `χ_ρ = (Tr I, Tr R, Tr(-I), Tr(-R)) = (2, 0, -2, 0)`.

Multiplicities `n_k = (1/4) Σ_j χ_k(j)* χ_ρ(j)`:

- `n_0 = (2 + 0 - 2 + 0)/4 = 0`
- `n_1 = (2 + 0 + (-1)(-2) + 0)/4 = 1`
- `n_2 = (2 + 0 + (1)(-2) + 0)/4 = 0`
- `n_3 = (2 + 0 + (-1)(-2) + 0)/4 = 1`

So `ρ ≅ χ_1 ⊕ χ_3`. Concretely, `R` has eigenvalues `±i` (confirmed numerically) with eigenvectors `(1, ∓i)/√2`: on `(1, -i)/√2` the generator acts as `i = χ_1(1)`, and on `(1, i)/√2` as `-i = χ_3(1)`. The real representation is irreducible over `ℝ` (no real eigenvectors) but splits over `ℂ` — a reminder that irreducibility depends on the field. Note `χ_ρ(2) = -2`: the element `2 ∈ ℤ_4` (rotation by `180°`) acts as `-I` on the plane. This is an honest rotation, unlike the `R_z(2π) = -I` of `SU(2)`, where a rotation that is trivial on the Bloch sphere still flips the spinor sign.

</details>

**Exercise 2**: Compute the character of the regular representation of `S_3` and decompose it using the character table from the worked example. Confirm the general statement that each irrep appears with multiplicity equal to its dimension, and check `Σ d_i² = |G|`.

<details><summary>Solution</summary>

In the regular representation `ρ(g)|h⟩ = |gh⟩`, the basis vector `|h⟩` is fixed iff `gh = h`, i.e. `g = e`. So `χ_reg(e) = |G| = 6` and `χ_reg(g) = 0` for `g ≠ e`: `χ_reg = (6, 0, 0)`.

Multiplicities `n_i = (1/6) Σ_C |C| χ_i(C)* χ_reg(C) = (1/6)·1·χ_i(e)·6 = χ_i(e) = d_i`:

- `n_triv = 1`, `n_sgn = 1`, `n_std = 2`

So `ℂ[S_3] ≅ triv ⊕ sgn ⊕ std ⊕ std`, and comparing dimensions, `6 = 1 + 1 + 2·2 = Σ d_i²` ✓. (A brute-force construction of the six `6×6` left-multiplication matrices gives trace `6` at the identity and `0` elsewhere, and the inner products evaluate to `(1, 1, 2)`.) This is the finite-group Peter-Weyl theorem: the regular representation contains every irrep, `d_i` times each.

</details>

**Exercise 3**: `D_4` acts on the four vertices `(±1, ±1)` of a square by permutation, giving a 4-dimensional representation. Compute its character on the five classes (in the order of the `D_4` table above, with `s` the reflection in the `x`-axis and `rs` a reflection in a diagonal) and decompose it into irreps.

<details><summary>Solution</summary>

The character counts fixed vertices:

- `e`: all 4 fixed → `4`
- `r²` (rotation by `180°`): no vertex fixed → `0`
- `r, r³` (rotation by `±90°`): none fixed → `0`
- `s, r²s` (reflections in the `x`- and `y`-axes): these swap vertices in pairs, none fixed → `0`
- `rs, r³s` (reflections in the diagonals `y = x`, `y = -x`): each fixes the two vertices on its mirror line → `2`

So `χ_V = (4, 0, 0, 0, 2)` in the class order `(e, r², {r,r³}, {s,r²s}, {rs,r³s})`. With class sizes `(1, 1, 2, 2, 2)` and `|G| = 8`:

- `n_{++} = (4 + 0 + 0 + 0 + 2·2·1)/8 = 8/8 = 1`
- `n_{+−} = (4 + 0 + 0 + 0 + 2·2·(-1))/8 = 0`
- `n_{−+} = (4 + 0 + 0 + 0 + 2·2·(-1))/8 = 0`
- `n_{−−} = (4 + 0 + 0 + 0 + 2·2·(+1))/8 = 1`
- `n_E = (2·4 + (-2)·0 + 0 + 0 + 0)/8 = 1`

Hence `V ≅ χ_{++} ⊕ χ_{−−} ⊕ E`, dimensions `4 = 1 + 1 + 2` ✓, and `⟨χ_V, χ_V⟩ = (16 + 0 + 0 + 0 + 2·4)/8 = 3` = three distinct constituents ✓. The trivial summand is the all-ones vector (sum of vertices); the `χ_{−−}` summand is the alternating vector `(+1, -1, +1, -1)` around the square (a "checkerboard" colouring, flipped by `r` and by axis reflections but preserved by diagonal reflections); `E` is the plane itself, spanned by the coordinate functions. Numerically, building the four permutation matrices and evaluating the sums returns `(1, 0, 0, 1, 1)`.

</details>

**Exercise 4**: Using characters, decompose `1 ⊗ ½` and `1 ⊗ 1` for `SU(2)`, and check each by dimension counting and by the eigenvalues of the total Casimir `J² = (J⁽¹⁾ + J⁽²⁾)²`.

<details><summary>Solution</summary>

Characters multiply: `χ_1(θ)χ_½(θ) = (1 + 2cos θ)(2cos(θ/2))`. Using `2cos θ cos(θ/2) = cos(3θ/2) + cos(θ/2)`, this is `2cos(θ/2) + 2cos(3θ/2) + 2cos(θ/2)`. Meanwhile `χ_{3/2}(θ) = sin(2θ)/sin(θ/2) = 2cos(3θ/2) + 2cos(θ/2)` (sum of `e^{imθ}` over `m = ±½, ±3/2`), so `χ_1 χ_½ = χ_{3/2} + χ_½`: `1 ⊗ ½ = 3/2 ⊕ ½`. Dimensions `3·2 = 6 = 4 + 2` ✓. Numerically at `θ = 1.1`: `χ_1 = 1.9072`, `χ_½ = 1.7050`, product `3.2519`; `χ_{3/2} + χ_½ = 1.5468 + 1.7050 = 3.2519` ✓. The Casimir on `ℂ³ ⊗ ℂ²` has eigenvalues `j(j+1)`: `15/4 = 3.75` with multiplicity 4 and `3/4 = 0.75` with multiplicity 2 ✓.

For `1 ⊗ 1`: `(1 + 2cos θ)² = 1 + 4cos θ + 4cos² θ = 3 + 4cos θ + 2cos 2θ`, and `χ_2 + χ_1 + χ_0 = (1 + 2cos θ + 2cos 2θ) + (1 + 2cos θ) + 1` — identical. So `1 ⊗ 1 = 2 ⊕ 1 ⊕ 0`, dimensions `9 = 5 + 3 + 1` ✓. Casimir eigenvalues on `ℂ³ ⊗ ℂ³`: `6` (×5), `2` (×3), `0` (×1) ✓. The `j = 0` singlet in `1 ⊗ 1` is the rotationally invariant state `(|1,-1⟩ - |0,0⟩ + |-1,1⟩)/√3`, the spin-1 analogue of `|Ψ⁻⟩`.

</details>

**Exercise 5**: Let `G = ℤ_12` and let `f` hide the subgroup `H = ⟨4⟩ = {0, 4, 8}`. After measuring the second register, the first register is in a coset state `|g + H⟩ = (|g⟩ + |g+4⟩ + |g+8⟩)/√3`. Compute the QFT of this state, show that the measurement outcome is independent of `g`, list the possible outcomes with their probabilities, and explain how two outcomes typically suffice to recover `H`.

<details><summary>Solution</summary>

With `ω = e^{2πi/12}`, `QFT|j⟩ = (1/√12) Σ_k ω^{jk}|k⟩`, so

`QFT|g + H⟩ = (1/√36) Σ_k ω^{gk} (1 + ω^{4k} + ω^{8k}) |k⟩`

The bracket is a geometric sum over `H`: it equals `3` when `ω^{4k} = 1`, i.e. `4k ≡ 0 mod 12`, i.e. `k ∈ {0, 3, 6, 9}`, and `0` otherwise (`1 + ζ + ζ² = 0` for a primitive cube root `ζ`). So

`QFT|g + H⟩ = (1/2) Σ_{k ∈ {0,3,6,9}} ω^{gk} |k⟩`

The coset label `g` survives only as the phase `ω^{gk}`, which the measurement ignores: each of `k = 0, 3, 6, 9` occurs with probability `|½|² = 1/4`, independent of `g` (numerically, the QFT of `(1,0,0,0,1,0,0,0,1,0,0,0)/√3` has squared amplitudes `0.25` at `k = 0, 3, 6, 9` and `0` elsewhere). These `k` are exactly the annihilator `H^⊥ = {k : χ_k(4) = ω^{4k} = 1}`; the characters `χ_k` trivial on `H` are those with `k` a multiple of `12/|H| = 3`.

Recovery: an outcome `k` tells us that every `h ∈ H` satisfies `hk ≡ 0 mod 12`. From `k = 3` alone we learn `H ⊆ {0, 4, 8}`; from `k = 9` the same; `k = 6` gives only `H ⊆ {0, 2, 4, 6, 8, 10}` and `k = 0` gives nothing. Two independent samples avoid the uninformative outcomes with probability `1 - (1/2)² = 3/4` and then determine `H` exactly, and the confidence grows exponentially with more samples. In Shor's algorithm the same computation, with `N = 2ⁿ` and `H = ⟨r⟩` for the unknown period `r`, returns `k ≈ (multiple of N/r)`, from which continued fractions extract `r`.

</details>

## Further Reading

1. **Serre**, *Linear Representations of Finite Groups* (Springer GTM 42), Part I, Chapters 1–3 — the cleanest short account of characters, orthogonality and Maschke; the `S_3`/`D_4` tables appear in §5
2. **Fulton & Harris**, *Representation Theory: A First Course* (Springer GTM 129), Lectures 1–4, 6 and 11 — finite groups, Schur-Weyl duality for `S_n` (§6.1), and the representations of `𝔰𝔩_2 ≅ 𝔰𝔲(2)_ℂ`
3. **Tinkham**, *Group Theory and Quantum Mechanics* (Dover), Chapters 3–5 — the physicist's route: symmetry, degeneracy, selection rules, and angular momentum as `SU(2)` representation theory
4. **Childs**, *Lecture Notes on Quantum Algorithms* (University of Maryland, free online), Chapters on the abelian HSP, non-abelian Fourier sampling and Kuperberg's dihedral algorithm — the definitive treatment of the representation-theoretic view of Shor and its limits
5. **Harrow**, *Applications of Coherent Classical Communication and the Schur Transform to Quantum Information Theory* (PhD thesis, MIT 2005, arXiv:quant-ph/0512255), Chapters 5–8 — Schur-Weyl duality made computational: efficient circuits for the Schur transform and their uses
