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

<details><summary>Solution</summary>

A representation of `ℤ₄ = {0,1,2,3}` is fixed by the image of the generator `1`: pick any `A ∈ GL(2,ℂ)` with `A⁴ = I` and set `ρ(k) = Aᵏ`. Three instructive choices.

**(a) The rotation representation, `A = [[0, −1],[1, 0]]`** (90° rotation of the plane):

```
ρ(0) = [[1,0],[0,1]]     ρ(1) = [[0,−1],[1, 0]]
ρ(2) = [[−1,0],[0,−1]]   ρ(3) = [[0, 1],[−1,0]]
```

`A⁴ = I` and `A² = −I` (verified), and `A` has order 4, so `ρ` is **faithful**. Its character is `χ(k) = Tr Aᵏ = (2, 0, −2, 0)` (verified numerically).

Over `ℂ` this is reducible: `A` has eigenvalues `±i`, so decomposing against the `ℤ₄` characters `χ_k(j) = i^{jk}` gives multiplicities `(0, 1, 0, 1)` — computed in the venv — i.e.

`ρ ≅ χ₁ ⊕ χ₃`

diagonalized by `S = (1/√2)[[1, 1],[i, −i]]`, giving `S⁻¹AS = diag(−i, i)` (verified). Over `ℝ` the same `ρ` *is* irreducible — complex irreducibility and real irreducibility differ, and representation theory over `ℂ` is the version quantum mechanics needs.

**(b) A diagonal faithful representation**, `ρ'(k) = diag(iᵏ, 1) = χ₁ ⊕ χ₀`. Also faithful, already decomposed.

**(c) The trivial-squared representation**, `ρ''(k) = I` for all `k` `= χ₀ ⊕ χ₀`. Not faithful (`ker = ℤ₄`).

**The general statement.** `ℤ₄` is abelian, so every complex irrep is 1-dimensional (Schur). Hence *every* 2-dimensional complex representation of `ℤ₄` is `χ_a ⊕ χ_b` for some `a, b ∈ {0,1,2,3}`, and there are `10` inequivalent ones (unordered pairs with repetition). Choosing a representation on `ℂ²` therefore amounts to choosing which two characters the two qubit basis states carry — which is exactly what "encoding a `ℤ₄` symmetry in a qubit" means, and why a `Z`-rotation `diag(1, i) = χ₀ ⊕ χ₁` is the natural single-qubit realization of `ℤ₄`.

</details>

- Show that the regular representation of S₃ has degree 6

<details><summary>Solution</summary>

The regular representation acts on the group algebra `ℂ[G]`, the vector space with one basis vector `|g⟩` for each group element, by left multiplication:

`ρ_reg(g)|h⟩ = |gh⟩`

The **degree** of a representation is `dim V`, and `dim ℂ[G] = |G|` by construction. For `S₃`, `|S₃| = 3! = 6`, so the regular representation has degree 6: each `ρ_reg(g)` is a `6 × 6` permutation matrix.

It is a genuine representation (`ρ_reg(g)ρ_reg(h)|k⟩ = |ghk⟩ = ρ_reg(gh)|k⟩`) and it is faithful, since `ρ_reg(g)|e⟩ = |g⟩ ≠ |e⟩` unless `g = e`.

**Its character.** `χ_reg(g)` counts the basis vectors fixed by `g`, i.e. the `h` with `gh = h`, i.e. `g = e`. So

`χ_reg = (6, 0, 0)` on the classes `(e, transpositions, 3-cycles)`

**Decomposition — the structural reason degree 6 is the "right" number.** Using the `S₃` character table (`χ_triv = (1,1,1)`, `χ_sgn = (1,−1,1)`, `χ_std = (2,0,−1)`) and `⟨χᵢ, χ_reg⟩ = (1/6)(1 · χᵢ(e)* · 6) = χᵢ(e) = dᵢ`:

`ℂ[S₃] ≅ triv ⊕ sgn ⊕ 2·std`

Dimension check: `1 + 1 + 2·2 = 6` ✓, which is the general identity `Σᵢ dᵢ² = |G|`. Every irrep appears in the regular representation, with multiplicity equal to its own dimension — which is why the regular representation is the universal object for building character tables, and why `ℂ[G] ≅ ⊕_ρ M_{d_ρ}(ℂ)` (the Artin–Wedderburn/Peter–Weyl decomposition) has `Σ d_ρ² = |G|` entries.

**Algorithmic relevance.** For abelian `G` the regular representation is the cyclic shift and the change of basis that block-diagonalizes it is the QFT; for non-abelian `G` the same change of basis is the non-abelian Fourier transform of Module 6, and the blocks of size `d_ρ > 1` are exactly what makes the non-abelian hidden subgroup problem hard.

</details>

- Prove that equivalent representations have the same character

<details><summary>Solution</summary>

Two representations `ρ, ρ'` of `G` on `V` are **equivalent** if there is an invertible `S` with `ρ'(g) = S ρ(g) S⁻¹` for all `g`.

**Proof.** The trace is invariant under cyclic permutation of a product, `Tr(ABC) = Tr(BCA)`. Hence for every `g`:

```
χ_{ρ'}(g) = Tr( S ρ(g) S⁻¹ ) = Tr( ρ(g) S⁻¹ S ) = Tr( ρ(g) ) = χ_ρ(g)
```

∎ So the character is an invariant of the equivalence class — it does not depend on the choice of basis.

**Corollary: characters are class functions.** Apply the same argument with `S = ρ(h)`:

`χ(hgh⁻¹) = Tr(ρ(h)ρ(g)ρ(h)⁻¹) = Tr(ρ(g)) = χ(g)`

so `χ` is constant on conjugacy classes. This is why a character table has one column per class rather than one per group element.

**The converse (for finite groups over `ℂ`).** Equal characters imply equivalence. Reason: Maschke's theorem writes `V ≅ ⊕ᵢ nᵢVᵢ`, the multiplicities are recovered from the character alone by `nᵢ = ⟨χᵢ, χ_V⟩`, and two representations with the same multiplicities of the same irreps are isomorphic. So the character is a **complete invariant** — a single vector of `#classes` numbers determines the representation up to isomorphism.

That completeness is what makes character theory a practical computational tool: to test whether `V` is irreducible, compute `⟨χ_V, χ_V⟩` and check it equals 1; to decompose `V`, take inner products against the table. No matrices required. Quantum example: two gate sets generate the same symmetry action on a degenerate energy level iff the corresponding representations have the same character, which is the selection-rule machinery of `docs/01_mathematical_foundations/05_representation_theory.md`.

</details>

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

<details><summary>Solution</summary>

The representation in question is `ρ(0) = I`, `ρ(1) = −I` on `ℂ²`.

**Reducibility, directly.** A representation is reducible if it has a proper non-zero invariant subspace. Here every scalar matrix commutes with everything, so *every* subspace is invariant. In particular `W₁ = span{|0⟩}` and `W₂ = span{|1⟩}` are one-dimensional invariant subspaces, and

`ℂ² = W₁ ⊕ W₂`

with `ρ` acting on each `Wᵢ` as the sign character. So `ρ ≅ sgn ⊕ sgn` — reducible, and in fact isotypic (both summands the same irrep).

**Reducibility, via characters.** `χ_ρ = (Tr I, Tr(−I)) = (2, −2)`. The `ℤ₂` characters are `χ_triv = (1,1)` and `χ_sgn = (1,−1)`, so

```
⟨χ_triv, χ_ρ⟩ = ½(2 − 2) = 0
⟨χ_sgn,  χ_ρ⟩ = ½(2 + 2) = 2
⟨χ_ρ, χ_ρ⟩ = ½(4 + 4) = 4 = 2² ≠ 1
```

`⟨χ_ρ, χ_ρ⟩ ≠ 1` is the irreducibility test failing; the multiplicity vector `(0, 2)` says `ρ ≅ 2·sgn` ✓.

**The general principle.** `ℤ₂` is abelian, so by Schur every complex irrep is 1-dimensional. Therefore **no** 2-dimensional complex representation of `ℤ₂` can be irreducible — the only question is which pair of characters it decomposes into.

**A more interesting `ℤ₂` on `ℂ²`.** Take `ρ(1) = X` instead. Now the invariant lines are *not* the computational basis: `χ_ρ = (2, 0)`, giving multiplicities `⟨triv, χ⟩ = 1` and `⟨sgn, χ⟩ = 1`, so `ρ ≅ triv ⊕ sgn` with invariant lines `span{|+⟩}` (eigenvalue `+1`) and `span{|−⟩}` (eigenvalue `−1`). Physically: a Hamiltonian with a `ℤ₂` symmetry generated by `X` has its eigenstates labelled by `X`-parity `±1`, and no perturbation respecting the symmetry can mix the two sectors. That block structure — symmetry sectors as isotypic components — is the everyday use of representation theory in quantum simulation.

</details>

- Decompose the regular representation of ℤ₃ into irreps

<details><summary>Solution</summary>

`ℂ[ℤ₃]` has basis `{|0⟩, |1⟩, |2⟩}` and `ρ_reg(k)|j⟩ = |j + k mod 3⟩`, so `ρ_reg(1)` is the cyclic shift

```
ρ_reg(1) = [[0, 0, 1],
            [1, 0, 0],
            [0, 1, 0]]
```

**Characters.** `χ_reg = (3, 0, 0)`. The irreps of `ℤ₃` are the three characters `χ_k(j) = ω^{jk}` with `ω = e^{2πi/3}`. Multiplicities:

`n_k = ⟨χ_k, χ_reg⟩ = (1/3) Σ_j χ_k(j)* χ_reg(j) = (1/3)(1 · 3) = 1`

for each `k = 0, 1, 2`. Hence

`ℂ[ℤ₃] ≅ χ₀ ⊕ χ₁ ⊕ χ₂`

each irrep once — the general theorem `multiplicity = dimension` for the regular representation, and `Σ dᵢ² = 1 + 1 + 1 = 3 = |G|` ✓.

**The explicit change of basis.** The invariant lines are spanned by

`|v_k⟩ = (1/√3) Σ_{j=0}^{2} ω^{jk} |j⟩`,  with `ρ_reg(1)|v_k⟩ = ω^{−k}|v_k⟩`

Direct check: `ρ_reg(1)|v_k⟩ = (1/√3)Σ_j ω^{jk}|j+1⟩ = (1/√3)Σ_m ω^{(m−1)k}|m⟩ = ω^{−k}|v_k⟩`. Verified numerically for `k = 0, 1, 2`, and the eigenvalues of the shift are indeed `{1, ω, ω²}` (computed: `1, −0.5 ± 0.866i`).

**Why this is the QFT.** The matrix whose rows are the `|v_k⟩` is `F_{kj} = ω^{jk}/√3` — the 3-point discrete Fourier transform, unitary (verified `FF† = I`) and equal to `QFT₃`. So:

> Decomposing the regular representation of a finite abelian group into irreps **is** the Fourier transform on that group.

That single sentence is the bridge from this module to Module 6: the QFT over `ℤ_N` is the change of basis that block-diagonalizes translation, its rows are the characters, and its eigenvalue structure is precisely what period finding measures.

</details>

- State and apply Maschke's theorem to a specific example

<details><summary>Solution</summary>

**Statement.** Let `G` be a finite group and `V` a finite-dimensional representation of `G` over a field `k` whose characteristic does not divide `|G|` (e.g. `k = ℂ`). Then every `G`-invariant subspace `W ⊆ V` has a `G`-invariant complement: `V = W ⊕ W'` with `ρ(g)W' ⊆ W'`. Consequently `V` is **completely reducible**: `V ≅ ⊕ᵢ nᵢ Vᵢ` with each `Vᵢ` irreducible.

**Proof sketch (averaging).** Choose any linear projector `P: V → W` with `P|_W = id`. Average it over the group:

`P̄ = (1/|G|) Σ_{g∈G} ρ(g) P ρ(g)⁻¹`

The division by `|G|` is where the characteristic hypothesis is used. Since `W` is invariant, `P̄` still maps `V` into `W` and restricts to the identity on `W`, so it is again a projector onto `W`; and `ρ(h)P̄ρ(h)⁻¹ = P̄` by reindexing the sum, so `P̄` is a `G`-map. Then `W' = ker P̄` is invariant and `V = W ⊕ W'`. ∎ (Equivalently: average any inner product into a `G`-invariant one, making every `ρ(g)` unitary, and take `W' = W^⊥`.)

**Application: the permutation representation of `S₃` on `ℂ³`,** `ρ(σ)eᵢ = e_{σ(i)}`.

The vector `u = e₁ + e₂ + e₃` is fixed by every permutation, so `W = span{u}` is invariant and carries the trivial representation. Maschke guarantees an invariant complement. Since each `ρ(σ)` is a permutation matrix, it is already unitary for the standard inner product, so the averaged inner product *is* the standard one and

`W' = W^⊥ = {x ∈ ℂ³ : x₁ + x₂ + x₃ = 0}`

is invariant of dimension 2 — the standard representation.

**Confirmation by characters.** `χ_perm(σ) = #fixed points = (3, 1, 0)` on `(e, transpositions, 3-cycles)`. Then

```
⟨χ_perm, χ_perm⟩ = (1/6)(1·9 + 3·1 + 2·0) = 2 = 1² + 1²   → exactly two irreducible summands, each once
⟨χ_triv, χ_perm⟩ = (1/6)(3 + 3 + 0) = 1
⟨χ_sgn,  χ_perm⟩ = (1/6)(3 − 3 + 0) = 0
⟨χ_std,  χ_perm⟩ = (1/6)(2·3 + 0 − 0) = 1
```

(multiplicities `{triv: 1, sgn: 0, std: 1}` verified numerically), so `ℂ³ ≅ triv ⊕ std` ✓, matching the geometric decomposition above.

**Where Maschke fails.** The hypothesis is essential. Over `F₂`, let `ℤ₂` act on `F₂²` by `ρ(1) = [[1,1],[0,1]]` (which squares to the identity). The line `span{e₁}` is invariant, but it is the *only* invariant line, so it has no invariant complement and the representation is indecomposable yet reducible. Characteristic 2 divides `|ℤ₂| = 2`, so averaging is unavailable — this is modular representation theory, and it is why the clean "everything decomposes" picture used throughout quantum mechanics depends on working over `ℂ`.

</details>

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

<details><summary>Solution</summary>

**`S₃`** has `|G| = 6` and three conjugacy classes (cycle types): `{e}` of size 1, the transpositions `{(12),(13),(23)}` of size 3, and the 3-cycles `{(123),(132)}` of size 2. Three classes `⟹` three irreps, and `Σ dᵢ² = 6` forces dimensions `1, 1, 2`.

| `S₃` | `e` | transpositions | 3-cycles |
|---|---|---|---|
| class size | 1 | 3 | 2 |
| `χ_triv` | 1 | 1 | 1 |
| `χ_sgn` | 1 | −1 | 1 |
| `χ_std` | 2 | 0 | −1 |

`χ_std` is obtained as `χ_perm − χ_triv` with `χ_perm = (3,1,0)` the fixed-point count of the permutation action on `ℂ³`. The `3 × 3` Gram matrix under `⟨χ,ψ⟩ = (1/6)Σ_C |C| χ(C)*ψ(C)` is the identity (verified numerically), so the rows are orthonormal and the table is complete.

**`D₄ = ⟨r, s | r⁴ = s² = e, srs = r⁻¹⟩`** has 8 elements in five classes: `{e}`, `{r²}`, `{r, r³}`, `{s, r²s}` (axis reflections), `{rs, r³s}` (diagonal reflections). Five classes `⟹` five irreps, and `Σ dᵢ² = 8` forces `1,1,1,1,2`. The one-dimensional ones send `r ↦ ±1`, `s ↦ ±1` (the relation `χ(r) = χ(srs) = χ(r)⁻¹` forces `χ(r)² = 1`); the two-dimensional one is the geometric action on the plane, `r ↦ [[0,−1],[1,0]]`, `s ↦ [[1,0],[0,−1]]`.

| `D₄` | `e` | `r²` | `r, r³` | `s, r²s` | `rs, r³s` |
|---|---|---|---|---|---|
| class size | 1 | 1 | 2 | 2 | 2 |
| `χ_{++}` | 1 | 1 | 1 | 1 | 1 |
| `χ_{+−}` | 1 | 1 | 1 | −1 | −1 |
| `χ_{−+}` | 1 | 1 | −1 | 1 | −1 |
| `χ_{−−}` | 1 | 1 | −1 | −1 | 1 |
| `χ_E` | 2 | −2 | 0 | 0 | 0 |

(subscripts give `(χ(r), χ(s))`; matches `docs/01_mathematical_foundations/05_representation_theory.md`). The `5 × 5` Gram matrix is the identity — computed in the venv — confirming all five rows are irreducible and mutually orthogonal. Column orthogonality: `Σᵢ |χᵢ(C)|² = |G|/|C|` gives `1+1+1+1+4 = 8` on `{e}` ✓ and `1+1+1+1+0 = 4 = 8/2` on each class of size 2 ✓.

**The qubit connection.** `⟨X, Z⟩ = {±I, ±X, ±Z, ±XZ}` is a copy of `D₄` with `r = XZ` and `s = X`: `r⁴ = I`, `r² = −I`, `s² = I`, and `s r s⁻¹ = X(XZ)X = ZX = r⁻¹` — all verified numerically. The Pauli matrices then realise `χ_E` exactly: `Tr(I) = 2`, `Tr(r²) = Tr(−I) = −2`, `Tr(r) = Tr(s) = Tr(rs) = 0` ✓. So the single-qubit Pauli action **is** the unique 2-dimensional irrep of `D₄`, and the four 1-dimensional irreps are the four ways of assigning signs to `X` and `Z` — which is how phase conventions in the Pauli group are classified.

</details>

- Use orthogonality to verify the character table of ℤ₄

<details><summary>Solution</summary>

The irreps of `ℤ₄` are the four characters `χ_k(j) = i^{jk}`, `k = 0,1,2,3` (all one-dimensional, since the group is abelian):

| `ℤ₄` | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| `χ₀` | 1 | 1 | 1 | 1 |
| `χ₁` | 1 | `i` | −1 | `−i` |
| `χ₂` | 1 | −1 | 1 | −1 |
| `χ₃` | 1 | `−i` | −1 | `i` |

**Row (first) orthogonality.** Every conjugacy class is a singleton, so

```
⟨χ_k, χ_l⟩ = ¼ Σ_{j=0}^{3} χ_k(j)* χ_l(j) = ¼ Σ_{j=0}^{3} i^{−jk} i^{jl} = ¼ Σ_{j=0}^{3} z^j,   z = i^{l−k}
```

If `l ≡ k (mod 4)` then `z = 1` and the sum is `4`, giving `1`. Otherwise `z` is a non-trivial 4th root of unity, so `z ≠ 1` but `z⁴ = 1`, and the geometric series gives

`Σ_{j=0}^{3} z^j = (z⁴ − 1)/(z − 1) = 0`

Hence `⟨χ_k, χ_l⟩ = δ_{kl}` ✓. Numerically the `4 × 4` Gram matrix is the identity.

**Column (second) orthogonality.** `Σ_k χ_k(j)* χ_k(j') = Σ_k i^{k(j'−j)} = 4 δ_{jj'}` by the identical computation. The general rule `Σᵢ χᵢ(C)* χᵢ(C') = (|G|/|C|) δ_{CC'}` reads `4 δ` here, since every class has size 1 ✓.

**Counting checks.** Number of irreps `= 4 =` number of conjugacy classes ✓; `Σ dᵢ² = 1+1+1+1 = 4 = |G|` ✓; each character is a homomorphism into `U(1)` (`χ_k(j + j') = χ_k(j)χ_k(j')` since `i^{(j+j')k} = i^{jk}i^{j'k}`) ✓.

**The unitary reformulation.** Stack the normalized characters into

`F_{kj} = χ_k(j)/√4 = i^{jk}/2`

Row orthonormality is exactly the statement `F F† = I` — verified numerically. So the *content* of the orthogonality relations for `ℤ₄` is "the character table, divided by `√|G|`, is a unitary matrix", and that unitary matrix is the 4-point QFT (Module 6). Orthogonality of characters is therefore not an abstract curiosity: it is the reason the QFT is a legal quantum gate.

</details>

- Determine the multiplicity of each irrep in a given reducible representation

<details><summary>Solution</summary>

**The tool.** For a finite group over `ℂ`, `V ≅ ⊕ᵢ nᵢVᵢ` with

`nᵢ = ⟨χᵢ, χ_V⟩ = (1/|G|) Σ_{classes C} |C| χᵢ(C)* χ_V(C)`

and the self-check `⟨χ_V, χ_V⟩ = Σᵢ nᵢ²` (so `V` is irreducible iff this equals 1).

**Take `V = ℂ³ ⊗ ℂ³` for `G = S₃`,** where `ℂ³` is the permutation representation `ρ(σ)eᵢ = e_{σ(i)}`. The character of a tensor product is the product of characters, so with `χ_perm = (3, 1, 0)` on `(e, transpositions, 3-cycles)`:

`χ_V = χ_perm² = (9, 1, 0)`

Using the `S₃` table (`χ_triv = (1,1,1)`, `χ_sgn = (1,−1,1)`, `χ_std = (2,0,−1)`) and class sizes `(1, 3, 2)`:

```
n_triv = (1/6)( 1·1·9 + 3·1·1 + 2·1·0 )      = 12/6 = 2
n_sgn  = (1/6)( 1·1·9 + 3·(−1)·1 + 2·1·0 )   =  6/6 = 1
n_std  = (1/6)( 1·2·9 + 3·0·1 + 2·(−1)·0 )   = 18/6 = 3
```

all three confirmed numerically. So

`ℂ³ ⊗ ℂ³ ≅ 2·triv ⊕ 1·sgn ⊕ 3·std`

**Checks.**
- Dimensions: `2·1 + 1·1 + 3·2 = 9 = 3 × 3` ✓
- Norm: `⟨χ_V, χ_V⟩ = (1/6)(81 + 3·1 + 0) = 14`, and `Σ nᵢ² = 4 + 1 + 9 = 14` ✓ — the two computations agree, which is a strong independent check that no multiplicity was mis-counted.
- `⟨χ_V,χ_V⟩ = 14 ≠ 1`, so `V` is (very) reducible, as expected.

**Reading the answer.** The two copies of the trivial representation are the `S₃`-invariant vectors of `ℂ³ ⊗ ℂ³`: the "diagonal" `Σᵢ eᵢ⊗eᵢ` and the "all-ones" `(Σeᵢ)⊗(Σeⱼ)` combination. The multiplicity spaces are where physics puts its quantum numbers: in a Hamiltonian commuting with the `S₃` action, the energy eigenspaces are unions of isotypic components, states within one copy of `std` are exactly degenerate by symmetry, and matrix elements between different irreps vanish — the selection rules. The same counting, applied to `SU(2)` instead of `S₃`, is the Clebsch-Gordan series of Module 4.

</details>

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

<details><summary>Solution</summary>

Work in the `|j, m⟩` basis with `j = 1` and `m = +1, 0, −1` in that order, and set `ħ = 1` (the convention used in `docs/01_mathematical_foundations/05_representation_theory.md`; Chapter 2.8 keeps the `ħ`).

**`J_z`** is diagonal by construction, `J_z|1,m⟩ = m|1,m⟩`:

```
J_z = [[1, 0,  0],
       [0, 0,  0],
       [0, 0, −1]]
```

**Ladder operators.** `J₊|j,m⟩ = √(j(j+1) − m(m+1)) |j,m+1⟩` gives `J₊|1,0⟩ = √2|1,1⟩` and `J₊|1,−1⟩ = √2|1,0⟩`, so

```
J₊ = √2 [[0, 1, 0],        J₋ = J₊† = √2 [[0, 0, 0],
         [0, 0, 1],                       [1, 0, 0],
         [0, 0, 0]]                       [0, 1, 0]]
```

**Cartesian components** from `J_x = (J₊ + J₋)/2`, `J_y = (J₊ − J₋)/(2i)`:

```
J_x = (1/√2) [[0, 1, 0],       J_y = (1/√2) [[0, −i,  0],
              [1, 0, 1],                     [i,  0, −i],
              [0, 1, 0]]                     [0,  i,  0]]
```

**Verification** (all checked numerically in the venv):

```
[J_x, J_y] = i J_z      [J_y, J_z] = i J_x      [J_z, J_x] = i J_y
J² = J_x² + J_y² + J_z² = 2·I₃ = j(j+1) I  with j = 1   ✓
```

All three are Hermitian, as angular-momentum observables must be, and `Tr J_k = 0`.

**What is different from spin-½.** The spin-1 rep is the `2j+1 = 3` dimensional irrep `V₁`, and it **descends to `SO(3)`**: `e^{−iθJ_z} = diag(e^{−iθ}, 1, e^{iθ})` is `2π`-periodic, whereas the spin-½ analogue `e^{−iθZ/2}` needs `4π`. In the language of Module 4, `−I ∈ SU(2)` acts trivially exactly for integer `j`, so integer-spin irreps are genuine `SO(3)` representations and half-integer ones are only projective. `V₁` is the "vector" representation: conjugating by the corresponding `SU(2)` element reproduces the ordinary `3 × 3` rotation matrices acting on `(x, y, z)` — which is the same `Ad` map that sends a single-qubit gate to its Bloch-sphere rotation.

For quantum computing, spin-1 systems appear as qutrits, as the `|1,m⟩` triplet sector of two coupled qubits (next exercise), and as the natural language for the `J = 1` subspace of decoherence-free-subspace encodings.

</details>

- Decompose the tensor product of two spin-1/2 representations: `1/2 ⊗ 1/2`

<details><summary>Solution</summary>

**By characters.** The `SU(2)` character depends only on the rotation angle: `χ_j(θ) = sin((2j+1)θ/2)/sin(θ/2)`, so `χ_{½}(θ) = 2cos(θ/2)` and `χ₁(θ) = 1 + 2cos θ`, `χ₀ = 1`. Then

`χ_{½}(θ)² = 4cos²(θ/2) = 2 + 2cos θ = (1 + 2cos θ) + 1 = χ₁(θ) + χ₀(θ)`

for every `θ`, so

```
½ ⊗ ½ ≅ 1 ⊕ 0
```

Dimension check `2 × 2 = 4 = 3 + 1` ✓, and this is the `j₁ = j₂ = ½` case of the general Clebsch-Gordan series `V_{j₁} ⊗ V_{j₂} ≅ ⊕_{J=|j₁−j₂|}^{j₁+j₂} V_J`.

**Explicitly.** The total angular momentum is `J_k = J_k^{(1)} ⊗ I + I ⊗ J_k^{(2)}` with `J_k = σ_k/2`. Diagonalizing `J²` and `J_z` and using `|↑⟩ = |0⟩`, `|↓⟩ = |1⟩` (the dictionary of `docs/02_quantum_mechanics/08_angular_momentum_and_hydrogen.md`):

**Triplet** (`J = 1`, symmetric under exchange):

```
|1, +1⟩ = |00⟩
|1,  0⟩ = (|01⟩ + |10⟩)/√2
|1, −1⟩ = |11⟩
```

**Singlet** (`J = 0`, antisymmetric):

```
|0, 0⟩ = (|01⟩ − |10⟩)/√2
```

Numerical verification in the venv: `J²` evaluates to `2 = j(j+1)` on all three triplet vectors and to `0` on the singlet, and `J_x, J_y, J_z` each annihilate the singlet ✓.

**Bell-state dictionary.** `|0,0⟩ = |Ψ⁻⟩` and `|1,0⟩ = |Ψ⁺⟩`, while `|Φ^±⟩ = (|00⟩ ± |11⟩)/√2 = (|1,1⟩ ± |1,−1⟩)/√2` live entirely inside the triplet sector. So the Bell basis is the coupled `|J, M⟩` basis, and the Bell measurement used in teleportation is a measurement of total spin.

**Why it matters.** The singlet is the unique `SU(2)`-invariant state of two qubits — `(U ⊗ U)|Ψ⁻⟩ = det(U)|Ψ⁻⟩ ~ |Ψ⁻⟩` — which is why it is perfectly anti-correlated along *every* axis and why singlet-like states form decoherence-free subspaces against collective noise. More generally, Schur–Weyl duality extends this decomposition to `(ℂ²)^{⊗n} ≅ ⊕_j V_j ⊗ W_j`, the basis of Schur sampling and spectrum estimation.

</details>

- Verify the Clebsch-Gordan coefficients for the j=0 singlet state

<details><summary>Solution</summary>

**Definition.** The coupled states expand in the product basis as

`|J, M⟩ = Σ_{m₁+m₂=M} ⟨j₁ m₁; j₂ m₂ | J M⟩ · |j₁ m₁⟩|j₂ m₂⟩`

with the coefficients vanishing unless `M = m₁ + m₂` (because `J_z = J_z^{(1)} + J_z^{(2)}`).

**Set-up.** `j₁ = j₂ = ½`, `J = M = 0`. The only product states with `m₁ + m₂ = 0` are `|↑↓⟩` and `|↓↑⟩`, so

`|0,0⟩ = a|↑↓⟩ + b|↓↑⟩`

**Fix the ratio by the raising operator.** `J₊ = J₊^{(1)} + J₊^{(2)}` must annihilate the top of a `J = 0` multiplet (there is no `M = 1` state in it). With `J₊|↓⟩ = |↑⟩` and `J₊|↑⟩ = 0`:

```
J₊|↑↓⟩ = |↑↑⟩,      J₊|↓↑⟩ = |↑↑⟩
J₊|0,0⟩ = (a + b)|↑↑⟩ = 0    ⟹    b = −a
```

**Fix the magnitude by normalization.** `|a|² + |b|² = 2|a|² = 1 ⟹ |a| = 1/√2`.

**Fix the phase by Condon–Shortley.** The standard convention makes the coefficient with the largest `m₁` real and positive, so `a = +1/√2`. Hence

```
⟨½ ½; ½ −½ | 0 0⟩ = +1/√2
⟨½ −½; ½ ½ | 0 0⟩ = −1/√2
```

and

`|0,0⟩ = (|↑↓⟩ − |↓↑⟩)/√2 = (|01⟩ − |10⟩)/√2 = |Ψ⁻⟩`

matching the sign convention of `docs/02_quantum_mechanics/08_angular_momentum_and_hydrogen.md`.

**Verification** (numerical, in the venv, with `J_k = σ_k^{(1)}/2 + σ_k^{(2)}/2`):

- `J_x|0,0⟩ = J_y|0,0⟩ = J_z|0,0⟩ = 0` ✓ — the state carries zero total angular momentum in every direction, which is the defining property of `J = 0`.
- Hence `J²|0,0⟩ = 0 = J(J+1)` with `J = 0` ✓.
- `⟨1,0|0,0⟩ = 0` ✓ — orthogonal to the `M = 0` triplet member, as the two belong to different irreps (Schur).

**Consistency checks on the table.** The `2 × 2` Clebsch-Gordan matrix for `M = 0`,

```
[[ 1/√2,  1/√2],      rows:    |1,0⟩, |0,0⟩
 [ 1/√2, −1/√2]]      columns: |↑↓⟩, |↓↑⟩
```

is orthogonal, as any Clebsch-Gordan block must be (it is a unitary change of basis). Note it is exactly the Hadamard matrix — coupling two spin-½ particles in the `M = 0` sector is a Hadamard on the `{|01⟩, |10⟩}` subspace.

**Physical payoff.** The relative minus sign is the whole story: it makes `|Ψ⁻⟩` antisymmetric under particle exchange (required for two identical fermions in the same spatial orbital), makes it `SU(2)`-invariant, and makes it the unique two-qubit state that is perfectly anti-correlated in every basis — the state used in EPR/Bell tests and in decoherence-free encodings.

</details>

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

<details><summary>Solution</summary>

**The 16 elements.** `P₁ = {i^a P : a ∈ {0,1,2,3}, P ∈ {I, X, Y, Z}}`:

```
 I,  X,  Y,  Z
iI, iX, iY, iZ
−I, −X, −Y, −Z
−iI, −iX, −iY, −iZ
```

`|P₁| = 4 × 4 = 16` (verified by exhaustive enumeration). The phases are forced: the Pauli matrices alone are not closed under multiplication (`XY = iZ`), so the factor `⟨i⟩ ≅ ℤ₄` must be included.

**Conjugacy classes.** For `Q, P ∈ P₁`, the phases cancel in `QPQ⁻¹`, and two Paulis either commute or anticommute, so

`QPQ⁻¹ = ±P`   (`+` if they commute, `−` if they anticommute)

Hence each class is either `{P}` (if `P` commutes with everything — i.e. `P` is central) or `{P, −P}`. Brute-force enumeration in the venv gives exactly **10 classes**:

| class | size |
|---|---|
| `{I}`, `{iI}`, `{−I}`, `{−iI}` | 1 each |
| `{X, −X}`, `{iX, −iX}` | 2 each |
| `{Y, −Y}`, `{iY, −iY}` | 2 each |
| `{Z, −Z}`, `{iZ, −iZ}` | 2 each |

Total `4·1 + 6·2 = 16` ✓.

**Structure read off the class list.**

- The centre is the union of the singleton classes: `Z(P₁) = {±I, ±iI} ≅ ℤ₄`, of order 4 (verified) — matching the module table.
- The quotient `P₁/Z(P₁)` has order `16/4 = 4`, and since `X² = Y² = Z² = I`, every non-identity coset squares to the identity coset: `P₁/Z(P₁) ≅ ℤ₂ × ℤ₂ ≅ F₂²`, **not** `ℤ₄`. In symplectic coordinates `I ↦ (0|0)`, `X ↦ (1|0)`, `Z ↦ (0|1)`, `Y ↦ (1|1)`, and Pauli multiplication becomes vector addition mod 2 (`docs/01_mathematical_foundations/04_groups_and_abstract_algebra.md`).
- The commutator subgroup is `[P₁, P₁] = {±I}` (every commutator is `±I`), so the abelianization has order 8 and is `≅ ℤ₂³`, giving **eight** one-dimensional irreps.
- Ten classes means ten irreps; with `Σ dᵢ² = 16` and eight of them one-dimensional, the remaining two satisfy `d² + d'² = 8`, so `d = d' = 2`. The two 2-dimensional irreps are the defining representation and its complex conjugate — they differ by how the central element `iI` acts (`+i` versus `−i`). The defining one is the Pauli matrices themselves, which is why "the Pauli group" and "the Pauli matrices" are used interchangeably.

This class structure is what the whole stabilizer formalism rests on: the `±` in `QPQ⁻¹ = ±P` is the syndrome bit, and the quotient `F₂^{2n}` is the linear-algebra arena where codes are designed.

</details>

- Find a set of generators for the stabilizer group of the 3-qubit bit-flip code

<details><summary>Solution</summary>

The code space is `span{|000⟩, |111⟩}` — the `[[3,1,1]]` bit-flip code of `docs/05_quantum_error_correction/03_repetition_code.md`.

**The generators.**

```
g₁ = Z₁Z₂ = Z ⊗ Z ⊗ I
g₂ = Z₂Z₃ = I ⊗ Z ⊗ Z
```

**Why they work.** `Z|0⟩ = |0⟩` and `Z|1⟩ = −|1⟩`, so on the logical basis states

```
g₁|000⟩ = (+1)(+1)|000⟩ = |000⟩          g₁|111⟩ = (−1)(−1)|111⟩ = |111⟩
g₂|000⟩ = |000⟩                           g₂|111⟩ = |111⟩
```

Both generators fix the code space pointwise, hence fix every superposition `α|000⟩ + β|111⟩`.

**It is a legitimate stabilizer group.** `g₁` and `g₂` are both `Z`-type, so they commute (symplectic form `ω = 0`, since neither has any `x` component); they are independent; and `−I ∉ S`. So `S = ⟨g₁, g₂⟩ = {III, ZZI, IZZ, ZIZ}` has order `2² = 4`, and the joint `+1` eigenspace has dimension `2³/2² = 2` — one logical qubit, matching `[[3,1,·]]`.

**Syndromes.** Measuring `(g₁, g₂)` distinguishes the four single-`X` scenarios, because `Xⱼ` anticommutes with a `Z`-type generator exactly when they overlap:

| error | `g₁ = Z₁Z₂` | `g₂ = Z₂Z₃` |
|---|---|---|
| none | `+1` | `+1` |
| `X₁` | `−1` | `+1` |
| `X₂` | `−1` | `−1` |
| `X₃` | `+1` | `−1` |

Four distinct syndromes for four cases — every single bit-flip is identified and corrected by re-applying the same `X`.

**Logical operators and the distance.** The normalizer of `S` in `P₃`, modulo `S`, is generated by

`X̄ = X₁X₂X₃`  and  `Z̄ = Z₁`

`X̄` commutes with both `Z`-type generators (it overlaps each in two positions) and swaps `|000⟩ ↔ |111⟩`; `Z₁` commutes with `g₁` and `g₂` and gives `|000⟩ ↦ |000⟩`, `|111⟩ ↦ −|111⟩`, so it acts as logical `Z`. (`Z₁`, `Z₂`, `Z₃` all act identically on the code space — they differ by elements of `S`.)

Since `Z̄` has weight 1, the code distance is `d = 1`: a single `Z` error is an *undetectable* logical error. That is the precise sense in which the bit-flip code is blind to phase flips, and it is why the Shor code concatenates it with the phase-flip code `⟨X₁X₂, X₂X₃⟩` to reach `d = 3`.

</details>

- Verify that the stabilizers of the 5-qubit perfect code commute pairwise

<details><summary>Solution</summary>

The generators are the four cyclic shifts

```
g₁ = X Z Z X I
g₂ = I X Z Z X
g₃ = X I X Z Z
g₄ = Z X I X Z
```

**Method 1 — count the disagreements.** Two Pauli strings commute iff the number of positions where *both* are non-identity and *different* is even (each such position contributes one anticommutation, and `PQ = (−1)^{#} QP`). Position by position:

| pair | positions where both non-identity and different | count | verdict |
|---|---|---|---|
| `g₁, g₂` | 2 (`Z` vs `X`), 4 (`X` vs `Z`) | 2 | commute |
| `g₁, g₃` | 3 (`Z` vs `X`), 4 (`X` vs `Z`) | 2 | commute |
| `g₁, g₄` | 1 (`X` vs `Z`), 2 (`Z` vs `X`) | 2 | commute |
| `g₂, g₃` | 3 (`Z` vs `X`), 5 (`X` vs `Z`) | 2 | commute |
| `g₂, g₄` | 4 (`Z` vs `X`), 5 (`X` vs `Z`) | 2 | commute |
| `g₃, g₄` | 1 (`X` vs `Z`), 4 (`Z` vs `X`) | 2 | commute |

Every count is even, so all six pairs commute. (The pattern is forced by the cyclic structure: each generator is the previous one shifted by one site, so any two overlap in exactly two mismatched positions.)

**Method 2 — the symplectic form.** In `(x|z)` coordinates, `g₁ = (10010 | 01100)`, `g₂ = (01001 | 00110)`, and so on. Computing `ω(gᵢ, gⱼ) = Σ (xᵢ z'ⱼ + zᵢ x'ⱼ) mod 2` gives the all-zeros `4 × 4` table (verified in the venv), i.e. the row space of the `4 × 10` check matrix is an **isotropic** subspace of `F₂^{10}`. Direct `32 × 32` matrix multiplication confirms `gᵢgⱼ = gⱼgᵢ` for all pairs.

**Consequences.**

- `S = ⟨g₁,…,g₄⟩` is abelian with `−I ∉ S`, so the generators have a simultaneous `+1` eigenspace. `|S| = 2⁴ = 16`, and the code space has dimension `2⁵/2⁴ = 2` — confirmed numerically: the projector `Π = ∏ᵢ(I + gᵢ)/2` satisfies `Π² = Π` with `rank Π = 2`.
- Independence: no generator is a product of the others (equivalently the `4 × 10` binary check matrix has rank 4), which is what makes the count `2⁵/2⁴` correct.
- Logical operators `X̄ = XXXXX` and `Z̄ = ZZZZZ` commute with all four generators (verified) and anticommute with each other, giving one encoded qubit.
- The 16 syndromes label "no error" plus the 15 single-qubit Pauli errors `{X, Y, Z} × {1..5}` bijectively — the code is *perfect*, saturating the quantum Hamming bound `2¹(1 + 3·5) = 32 = 2⁵` (`docs/05_quantum_error_correction/03_repetition_code.md`).

</details>

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

<details><summary>Solution</summary>

**The principle.** For a finite abelian group `G`, every irrep is a character `χ: G → U(1)`, and the characters form an orthonormal basis of `ℂ[G]` after dividing by `√|G|`. The unitary implementing that change of basis is the quantum Fourier transform:

`QFT_{kj} = χ_k(j)/√|G|`

**Apply to `ℤ₄`.** The characters are `χ_k(j) = ω^{jk}` with `ω = e^{2πi/4} = i`, giving the table

| `ℤ₄` | `j=0` | `j=1` | `j=2` | `j=3` |
|---|---|---|---|---|
| `χ₀` | 1 | 1 | 1 | 1 |
| `χ₁` | 1 | `i` | −1 | `−i` |
| `χ₂` | 1 | −1 | 1 | −1 |
| `χ₃` | 1 | `−i` | −1 | `i` |

Dividing by `√4 = 2`:

```
F₄ = ½ [[1,  1,  1,  1],
        [1,  i, −1, −i],
        [1, −1,  1, −1],
        [1, −i, −1,  i]]
```

Verified numerically: `F₄ F₄† = I`. Unitarity is *exactly* the orthogonality relations for the characters of `ℤ₄` — nothing else is needed.

**Consistency with the standard definition.** `F₄|j⟩ = ½ Σ_k i^{jk}|k⟩ = (1/√N) Σ_k e^{2πijk/N}|k⟩` with `N = 4` ✓, matching `docs/01_mathematical_foundations/05_representation_theory.md` and the QFT of `docs/04_quantum_algorithms/03_quantum_fourier_transform.md`. Row `k` of the matrix is the character `χ_k` divided by `√N`.

**Circuit.** On two qubits with `|j⟩ = |j₁j₀⟩`, the standard construction is `H` on the high-order qubit, a controlled-`S` (phase `i`) between the two, `H` on the low-order qubit, then a `SWAP` to reverse the bit order — four elementary gates realising the `4 × 4` matrix above.

**The deeper point.** `F₄` diagonalizes the regular representation of `ℤ₄`, i.e. the cyclic shift `|j⟩ ↦ |j+1 mod 4⟩`: the eigenvectors of the shift are the characters, with eigenvalue `ω^{−k}` on `Σ_j ω^{jk}|j⟩`. Period finding is nothing but reading off which characters survive after a coset state is Fourier-transformed, so "the QFT is the character table of `ℤ_N`" is the precise statement of why Shor's algorithm exists. For `G = (ℤ₂)ⁿ` the same recipe gives `χ_y(x) = (−1)^{x·y}` and the transform is `H^{⊗n}` — the Hadamard layer in Deutsch–Jozsa and Simon.

</details>

- Explain why Shor's algorithm solves the HSP for ℤ_N

<details><summary>Solution</summary>

**The reduction.** Factoring `N` reduces classically to finding the order `r` of a random `a` coprime to `N`, i.e. the period of `f(x) = aˣ mod N`. Working in the register group `G = ℤ_M` (`M` a power of two, `M > N²`), `f` is constant on the cosets of the subgroup

`H = ⟨r⟩ ≤ ℤ_M`

and takes distinct values on distinct cosets. That is exactly the **hidden subgroup problem**: given oracle access to `f`, find `H`.

**The standard HSP algorithm.**

1. Prepare `(1/√M) Σ_{x} |x⟩|f(x)⟩`.
2. Measure (or simply discard) the second register. The first collapses to a uniform **coset state** `|x₀ + H⟩ = (1/√|H|) Σ_{h ∈ H} |x₀ + h⟩` for a uniformly random, unknown `x₀`.
3. Apply the QFT over `ℤ_M` and measure.

**Why step 3 works — the representation theory.** The key identity is the orthogonality of characters restricted to a subgroup:

`Σ_{h ∈ H} χ(h) = |H|` if `χ|_H ≡ 1`, and `0` otherwise

Fourier-transforming the coset state therefore gives amplitude only on the **annihilator**

`H⊥ = {χ_k ∈ Ẑ_M : χ_k(h) = 1 for all h ∈ H} = {k : kr ≡ 0 mod M}`

and the unknown offset `x₀` appears only as an overall phase `χ_k(x₀)`, which the measurement discards. So every run returns a *uniformly random element of `H⊥`*, independent of `x₀`. Because `ℤ_M` is abelian, all its irreps are one-dimensional, so "Fourier sampling" returns a complete, measurable label `k` and nothing is lost.

**From samples to `r`.** If `r | M` exactly, `H⊥ = {0, M/r, 2M/r, …}` and each sample is `k = sM/r`, so `k/M = s/r` in lowest terms and a single continued-fraction expansion yields `r` (with `O(1)` repetitions to handle `gcd(s,r) ≠ 1`). If `r ∤ M` the peaks are smeared but still concentrate within `O(1)` of the multiples of `M/r`, and `M > N²` guarantees that `s/r` is the unique fraction with denominator `< N` within `1/(2M)` of `k/M` — the continued-fraction step still succeeds with constant probability. Then `H = (H⊥)⊥` is recovered, and classically `gcd(a^{r/2} ± 1, N)` gives a non-trivial factor whenever `r` is even and `a^{r/2} ≢ −1`.

**A concrete instance** from `docs/01_mathematical_foundations/05_representation_theory.md`: for `H = ⟨4⟩ ≤ ℤ₁₂`, the QFT of a coset state puts probability exactly `¼` on each of `k ∈ {0, 3, 6, 9}` and zero elsewhere — precisely `H⊥`, from which `H` is immediate.

**Summary in one line.** Shor's algorithm is the abelian HSP algorithm; it works because the characters of `ℤ_M` are a computable orthonormal basis (the QFT), because coset states Fourier-transform to uniform distributions on annihilators, and because one-dimensionality of abelian irreps means a measurement in that basis returns the full label.

</details>

- Describe what makes the non-abelian HSP hard

<details><summary>Solution</summary>

A good answer identifies where each ingredient of the abelian algorithm breaks, and names the consequences.

**1. The Fourier transform still exists — that is not the problem.** By Peter-Weyl, `ℂ[G] ≅ ⊕_ρ V_ρ ⊗ V_ρ*` and the matrix coefficients `√(d_ρ) ρ(g)_{ij}` form an orthonormal basis of `L²(G)`, with `Σ_ρ d_ρ² = |G|`. Efficient quantum circuits for this transform are known for `S_n` and many other families. So the obstruction is not the transform; it is the **measurement**.

**2. Irreps of dimension `> 1` hide the information in a basis, not a label.** Fourier-transforming a coset state yields an irrep label `ρ` together with a `d_ρ × d_ρ` block of matrix entries. For abelian `G` every `d_ρ = 1`, so the label *is* the answer. For non-abelian `G` the information about `H` sits in the block — and in a basis of that block that depends on the unknown coset representative, which measurement must somehow average away.

**3. Weak Fourier sampling is provably insufficient.** Measuring only the label `ρ` gives a distribution that, for `G = S_n`, is exponentially close for `H = {e}` and `H` a hidden order-2 subgroup of the type that encodes graph isomorphism (Hallgren–Russell–Ta-Shma; Moore–Russell–Schulman). No amount of repetition distinguishes them.

**4. Strong Fourier sampling needs a basis nobody knows how to choose,** and even that is not enough: for `S_n`, single-register measurements — in *any* basis — carry too little information, so one must measure jointly across `Ω(n log n)` coset states. Such entangled measurements exist information-theoretically (Ettinger–Høyer–Knill show the HSP always has polynomial *query* complexity) but no efficient circuit implementing them is known. The gap is computational, not informational.

**5. The consequences are load-bearing for cryptography.**

- **Graph isomorphism** is HSP over `S_n`; the failure above is why the quantum approach stalled (and classically Babai's quasipolynomial algorithm has since overtaken it).
- **Dihedral HSP** encodes the unique shortest vector problem (Regev), which underpins lattice-based post-quantum cryptography. The best known algorithm, Kuperberg's sieve, runs in subexponential `2^{O(√log N)}` time and space — far short of the polynomial time Shor achieves for `ℤ_N`.

**6. The one-sentence reason.** Abelian HSP works because "the dual group is a group of labels you can measure"; non-abelian HSP fails because the dual is a set of *matrix blocks*, the hidden subgroup is encoded in the internal basis of those blocks, and extracting it appears to require joint measurements on many registers that we do not know how to implement efficiently. This is the sharp mathematical reason Shor-type attacks have not generalised to lattices (`docs/01_mathematical_foundations/05_representation_theory.md`).

</details>

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
