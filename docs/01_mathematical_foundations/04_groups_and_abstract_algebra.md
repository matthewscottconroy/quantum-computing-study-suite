# Groups and Abstract Algebra for Quantum Computing

> **Prerequisites**: 01_linear_algebra.md (matrices, unitaries, Pauli matrices), 02_complex_numbers_and_hilbert_spaces.md (global phase), 03_tensor_products_and_multipartite_systems.md (Kronecker products of Paulis)  
> **Connects to**: The Pauli and Clifford groups of `05_quantum_error_correction/04_stabilizer_formalism.md`, classical codes over `GF(2)` in `05_quantum_error_correction/02_classical_error_correction.md`, single-qubit rotations and the `SU(2) → SO(3)` map in `02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md`, fermionic antisymmetry in `08_advanced_topics/03_many_body_physics_and_simulation.md`, and the representation theory of `05_representation_theory.md`

## Overview

Every quantum gate is invertible, gates compose associatively, and the "do nothing" gate is an identity. Those three facts say that the gates on `n` qubits form a **group** — `U(2ⁿ)` — and much of quantum computing is the study of interesting subgroups of it: the Pauli group that labels errors, the Clifford group that can be simulated classically, the continuous one-parameter subgroups `e^{-iθH}` that hardware actually drives. Abstract algebra gives this zoo a common vocabulary.

This chapter covers three layers of structure. First, **groups**: axioms, subgroups, cosets, quotients, and homomorphisms, illustrated throughout on the symmetric group and the Pauli group. Second, **rings and fields**, in particular `GF(2)` and its extensions, because stabilizer codes are ultimately linear algebra over the field with two elements. Third, **Lie groups and Lie algebras**, the continuous groups `U(n)`, `SU(2)` and `SO(3)` and the exponential map that turns Hermitian generators into unitary gates — including the famous 2-to-1 map from `SU(2)` to `SO(3)` that makes a qubit pick up a sign under a `2π` rotation.

The target is fluency, not encyclopaedic coverage: by the end you should be able to compute with cosets of the Pauli group, read a symplectic vector, count the single-qubit Clifford group, and explain why `e^{-iπZ} = -I`.

## Groups

### Definition and First Examples

A **group** is a set `G` with a binary operation `(g, h) ↦ gh` satisfying:

1. **Closure**: `g, h ∈ G ⟹ gh ∈ G`
2. **Associativity**: `(gh)k = g(hk)`
3. **Identity**: there is `e ∈ G` with `eg = ge = g` for all `g`
4. **Inverses**: for every `g` there is `g⁻¹` with `gg⁻¹ = g⁻¹g = e`

If additionally `gh = hg` for all `g, h`, the group is **abelian**. The **order** `|G|` is the number of elements; the order of an element `g` is the least `k ≥ 1` with `gᵏ = e`.

Examples that recur in this corpus:

- `ℤ_N = {0, 1, ..., N-1}` under addition mod `N` — abelian, cyclic, order `N`; the group behind the QFT
- `(ℤ_2)ⁿ` — bit strings under XOR; the group behind Simon's algorithm and CSS codes
- `U(n)` — `n×n` unitary matrices under multiplication; closure follows from `(UV)†(UV) = V†U†UV = I`, the identity matrix is unitary, and `U⁻¹ = U†` is unitary. This is the group of `log₂ n`-qubit gates
- `SU(n) ⊂ U(n)` — the unitaries with `det = 1`
- `S_n` — permutations of `n` objects, order `n!`
- `P_n` — the `n`-qubit Pauli group, order `4^{n+1}` (below)

Non-abelian is the rule, not the exception: `XZ = -ZX`, so even `P_1` fails to commute.

### Subgroups, Cosets and Lagrange

A subset `H ⊆ G` closed under products and inverses is a **subgroup**, written `H ≤ G`. For `g ∈ G` the **left coset** is `gH = {gh : h ∈ H}`; right cosets `Hg` are defined analogously. Two left cosets are either identical or disjoint, and every coset has `|H|` elements, so the cosets partition `G` into `|G|/|H|` equal pieces. The number of cosets is the **index** `[G : H]`.

**Lagrange's theorem**: if `H ≤ G` and `G` is finite, then `|H|` divides `|G|`. Consequently the order of any element divides `|G|`.

Cosets are the basic object of hidden-subgroup algorithms (Chapter 4): the oracle in Simon's problem or Shor's period finding is a function that is *constant on the cosets* of a hidden `H`, and the quantum algorithm samples information about `H` from a uniform superposition over one coset. They are also how logical operators are counted in stabilizer codes: the logical Paulis are the cosets of the stabilizer group inside its normalizer.

### Normal Subgroups, Quotients and Homomorphisms

A subgroup `N` is **normal** (`N ⊴ G`) if `gNg⁻¹ = N` for every `g`, equivalently if left and right cosets agree. Exactly then the cosets themselves form a group, the **quotient group** `G/N`, with multiplication `(gN)(hN) = (gh)N` and order `[G : N]`. Every subgroup of an abelian group is normal; the **center** `Z(G) = {z : zg = gz ∀g}` is always normal.

A **homomorphism** is a map `φ: G → K` with `φ(gh) = φ(g)φ(h)`. Its **kernel** `ker φ = {g : φ(g) = e}` is a normal subgroup, and its image is a subgroup of `K`. A bijective homomorphism is an **isomorphism**, `G ≅ K`.

**First isomorphism theorem**: `G / ker φ ≅ im φ`.

Two examples that will matter:

- `det: U(n) → U(1)` is a homomorphism (`det(UV) = det U · det V`) with kernel `SU(n)`, so `U(n)/SU(n) ≅ U(1)`. Note that this quotient keeps only the determinant phase and forgets the gate (`H` and `e^{iπ/4}H` differ by a global phase yet lie in different `SU(2)`-cosets, with `det = -1` and `det = -i`). "Forgetting the global phase" is the *other* quotient, by the center `{e^{iφ}I} ≅ U(1)`, which gives the projective unitary group `PU(n) = U(n)/U(1) ≅ SU(n)/ℤ_n`. Since every `U ∈ U(n)` factors as `e^{iφ}V` with `V ∈ SU(n)` (`V` unique up to an `n`-th root of unity), one can always fix `det = 1` at the cost of an unobservable phase — which is why gates are usually written as `SU(2)` elements
- The map `P_n → (ℤ_2)^{2n}` recording which Paulis appear, but not the phase, is a homomorphism with kernel the center `{±I, ±iI}` (next section)

### Cyclic and Abelian Groups, Direct Products, Presentations

A group generated by one element, `⟨g⟩ = {gᵏ}`, is **cyclic**; every cyclic group of order `N` is isomorphic to `ℤ_N`, and its subgroups are exactly `⟨d⟩` for the divisors `d` of `N`. The **direct product** `G × H` is the set of pairs with componentwise multiplication; the **fundamental theorem of finite abelian groups** says every finite abelian group is a direct product of cyclic groups of prime-power order. `ℤ_2 × ℤ_2` (the Klein four-group) is not cyclic: it has no element of order 4, and it is the group `P_1/Z(P_1)` below.

Groups are often specified by **generators and relations**: `⟨r, s | r⁴ = s² = e, srs = r⁻¹⟩` is the dihedral group `D_4` of order 8 (symmetries of a square), and as we will see, `⟨X, Z⟩ ≅ D_4` — the qubit Paulis *are* the square's symmetry group in disguise.

## The Symmetric Group and Parity

`S_n` is the group of bijections of `{1, ..., n}`. Every permutation factors into disjoint **cycles**, and every cycle of length `L` is a product of `L - 1` transpositions (swaps). Although the factorisation into transpositions is not unique, its **parity** is: a permutation is **even** or **odd**, and the **sign** `sgn(σ) = ±1` is a homomorphism `S_n → {±1}`. Its kernel, the **alternating group** `A_n`, is normal of index 2. Concretely, `sgn(σ) = det(P_σ)` where `P_σ` is the permutation matrix.

Parity is the algebraic root of particle statistics. For `n` identical particles the Hilbert space carries an action of `S_n` by permuting tensor factors; **bosons** live in the trivial-sign subspace (symmetric tensors) and **fermions** in the `sgn` subspace (antisymmetric tensors), so exchanging two fermions multiplies the state by `sgn(swap) = -1`. That minus sign is what the Jordan-Wigner strings in `08_advanced_topics/03_many_body_physics_and_simulation.md` are tracking, and it is the reason the singlet `(|01⟩ - |10⟩)/√2` in `02_quantum_mechanics/08_angular_momentum_and_hydrogen.md` is antisymmetric.

## The Pauli Group

### Structure

The **single-qubit Pauli group** is

`P_1 = {±I, ±iI, ±X, ±iX, ±Y, ±iY, ±Z, ±iZ}`, `|P_1| = 16`

It is closed because products of Paulis are Paulis up to `±1, ±i` (`XY = iZ` and so on). The `n`-qubit Pauli group `P_n` consists of all `n`-fold tensor products of `{I, X, Y, Z}` with an overall phase in `{±1, ±i}`, so `|P_n| = 4 · 4ⁿ = 4^{n+1}`. Any two elements either commute or anticommute.

### Center and Quotient

The **center** is `Z(P_n) = {±I, ±iI}`: the four phase multiples of the identity, and nothing else, since any non-identity Pauli string anticommutes with some other string. `Z(P_n)` is normal, of index `4ⁿ`, and the quotient `P_n / Z(P_n)` is an abelian group of order `4ⁿ` in which every element squares to the identity (because `P² = ±I` for every Pauli string). It is therefore isomorphic to `(ℤ_2)^{2n} = F_2^{2n}`, the `2n`-dimensional vector space over the two-element field.

The isomorphism is explicit. Write a Pauli string, up to phase, as a **symplectic vector** `(x | z) ∈ F_2^{2n}` where `x_j = 1` if qubit `j` carries `X` or `Y` and `z_j = 1` if it carries `Z` or `Y` — so `I ↦ (0|0)`, `X ↦ (1|0)`, `Z ↦ (0|1)`, `Y ↦ (1|1)` per qubit. Multiplication of Paulis becomes addition of vectors mod 2. What the quotient forgets — whether two strings commute — is recovered by the **symplectic form**

`ω((x|z), (x'|z')) = x·z' + z·x'  (mod 2)`

with `P` and `Q` commuting iff `ω = 0`. The whole of `05_quantum_error_correction/04_stabilizer_formalism.md` is built on this dictionary: a stabilizer group is an **isotropic** subspace (`ω = 0` on all pairs), and its normalizer is the symplectic complement.

## The Clifford Group as a Normalizer

For a subgroup `H ≤ G`, the **normalizer** `N_G(H) = {g : gHg⁻¹ = H}` is the largest subgroup of `G` in which `H` is normal. The **Clifford group** is

`C_n = N_{U(2ⁿ)}(P_n) = {U ∈ U(2ⁿ) : U P U† ∈ P_n for all P ∈ P_n}`

i.e. the unitaries that map Pauli strings to Pauli strings under conjugation. `H`, `S` and `CNOT` are Cliffords (`HXH = Z`, `HZH = X`, `SXS† = Y`, `SZS† = Z`), and they generate all of `C_n`. Because conjugation by a Clifford is determined by its action on the generators `X_j, Z_j`, and the phases are unobservable, one works with `C_n / U(1)`. Its order is `2^{n²+2n} ∏_{j=1}^{n} (4ʲ - 1)`: `24` for one qubit and `11520` for two. The action of `C_n` on `P_n / Z(P_n) ≅ F_2^{2n}` preserves `ω`, giving a homomorphism `C_n → Sp(2n, F_2)` whose kernel is the Paulis themselves (up to phase) — the structural content of the Gottesman-Knill theorem in `03_quantum_gates_and_circuits/03_circuit_model_and_universality.md`.

## Rings, Fields and GF(2)

A **ring** has two operations, `+` and `·`, with `(R, +)` an abelian group, multiplication associative with identity, and distributivity. An **ideal** `I ⊆ R` is an additive subgroup absorbing multiplication (`rI ⊆ I`), and the quotient `R/I` is again a ring — the ring-theoretic twin of a normal subgroup. A **field** is a commutative ring in which every nonzero element has a multiplicative inverse.

`ℤ_N` is a field iff `N` is prime (for composite `N = ab`, `a·b = 0` with `a, b ≠ 0`, so `a` has no inverse). The smallest field is `GF(2) = F_2 = {0, 1}` with `1 + 1 = 0`. Vector spaces over `F_2` are sets of bit strings closed under XOR; a **linear code** is a subspace of `F_2ⁿ`, its generator matrix a basis, its parity-check matrix a basis of the dual subspace — the content of `05_quantum_error_correction/02_classical_error_correction.md`.

Finite fields exist exactly for prime-power orders. `GF(2ᵐ)` is built as `F_2[x] / (p(x))` for an irreducible polynomial `p` of degree `m`, exactly as `ℂ = ℝ[x]/(x² + 1)`. For `m = 2`, `p(x) = x² + x + 1` gives `GF(4) = {0, 1, ω, ω²}` with `ω² = ω + 1` and `ω³ = 1`; a Pauli can be encoded as a single `GF(4)` symbol so that Pauli multiplication modulo phase becomes `GF(4)` addition — this is how the additive-code literature describes stabilizer codes. Any bijection compatible with `Y = X·Z ↔ ω + ω² = 1` works; this chapter uses `I ↦ 0`, `X ↦ 1`, `Z ↦ ω`, `Y ↦ ω²`, while Calderbank, Rains, Shor and Sloane map `(x|z) ↦ ωx + ω̄z`, i.e. `X ↦ ω`, `Z ↦ ω̄ = ω²`, `Y ↦ 1`. For `m = 3` there are two irreducible cubics, `x³ + x + 1` and `x³ + x² + 1`, and `x` generates the cyclic group `GF(8)ˣ` of order 7.

## Lie Groups, Lie Algebras and the Exponential Map

### Matrix Lie Groups

`U(n)`, `SU(n)`, `SO(n)` are **Lie groups**: groups that are also smooth manifolds, so one can differentiate curves through the identity. The tangent space at the identity is the **Lie algebra** `𝔤`, closed under the **commutator** `[A, B] = AB - BA`. Differentiating `U(t)†U(t) = I` at `t = 0` gives `A† + A = 0`: the Lie algebra `𝔲(n)` is the anti-Hermitian matrices, `𝔰𝔲(n)` the traceless anti-Hermitian ones, and `𝔰𝔬(n)` the real antisymmetric ones. The **exponential map** `exp: 𝔤 → G` sends `A ↦ e^{A} = Σ Aᵏ/k!`; physicists write `A = -iH` so that `e^{-iH}` is unitary whenever `H` is Hermitian. Every gate is `e^{-iHt}` for a **generator** `H` — the Hamiltonian that hardware turns on for time `t`.

### su(2), Pauli Matrices and Rotations

`𝔰𝔲(2)` is 3-dimensional with basis `{-iX/2, -iY/2, -iZ/2}`; the Hermitian generators `J_k = σ_k/2` obey

`[J_x, J_y] = iJ_z`, `[J_y, J_z] = iJ_x`, `[J_z, J_x] = iJ_y`

which are precisely the angular-momentum relations of `02_quantum_mechanics/08_angular_momentum_and_hydrogen.md`. Because `(n̂·σ)² = I`, the exponential series collapses:

`R_n̂(θ) = e^{-iθ n̂·σ/2} = cos(θ/2) I - i sin(θ/2) n̂·σ`

which is the general single-qubit gate up to phase. `𝔰𝔬(3)` also has three generators obeying the same brackets — the two algebras are isomorphic, which is why `SU(2)` and `SO(3)` are locally identical.

### The SU(2) → SO(3) Double Cover

Conjugating the Pauli vector by `U ∈ SU(2)` gives a real linear map on `ℝ³`: `U (n̂·σ) U† = (Rn̂)·σ` for a unique `R = Ad(U) ∈ SO(3)`, and `Ad(UV) = Ad(U)Ad(V)`. This is the map that sends a gate to its Bloch-sphere rotation. It is surjective, but not injective: `Ad(U) = Ad(-U)`, and the kernel is exactly `{I, -I}`, so

`SO(3) ≅ SU(2) / {±I}`

Every rotation has two preimages, differing by sign. Consequences: `R_z(2π) = e^{-iπZ} = -I` is a `2π` rotation of the Bloch sphere that multiplies the state vector by `-1`, and only `R_z(4π) = I` returns to the identity. The phase is unobservable on a single qubit — `-I` acts trivially on `ρ = |ψ⟩⟨ψ|` — but it is observable in a controlled rotation, where the controlled-`R_z(2π)` is the gate `Z` on the control. This is the algebraic origin of "spin-½ objects need a `4π` rotation" and of the `-1` fermions acquire under `2π`.

## Key Formulas

**Lagrange**: `H ≤ G ⟹ |G| = [G : H] · |H|`

**First isomorphism theorem**: `G / ker φ ≅ im φ`

**Sign of a permutation**: `sgn(σ) = (-1)^{(number of transpositions)} = det(P_σ)`

**Pauli group**: `|P_n| = 4^{n+1}`, `Z(P_n) = {±I, ±iI}`, `P_n / Z(P_n) ≅ F_2^{2n}`

**Symplectic form**: `ω((x|z), (x'|z')) = x·z' + z·x' mod 2`; `PQ = QP ⟺ ω = 0`

**Clifford group**: `C_n = {U : U P_n U† = P_n}`, `|C_n / U(1)| = 2^{n²+2n} ∏_{j=1}^{n}(4ʲ - 1)`

**GF(4)**: `ω² = ω + 1`, `ω³ = 1`

**Lie algebra of SU(2)**: `[σ_j/2, σ_k/2] = i ε_{jkl} σ_l/2`

**Single-qubit rotation**: `e^{-iθ n̂·σ/2} = cos(θ/2) I - i sin(θ/2) n̂·σ`

**Double cover**: `SO(3) ≅ SU(2)/{±I}`, `e^{-i·2π·n̂·σ/2} = -I`

## Worked Example

**Problem**: (a) Show that the single-qubit Clifford group has exactly 24 elements modulo global phase, by counting the possible images of `(X, Z)`. (b) Write out the coset decomposition of `P_1` with respect to its center and verify that the quotient is the Klein four-group `ℤ_2 × ℤ_2`, not `ℤ_4`.

**Solution**:

*(a) Counting.* A Clifford `U` is determined up to phase by the pair `(UXU†, UZU†)`: these two images fix the conjugation action on every Pauli (since `Y = iXZ` gives `UYU† = i(UXU†)(UZU†)`), and two unitaries with the same conjugation action on a basis of `2×2` matrices differ by a scalar. So we count admissible pairs.

Step 1 — image of `X`. `UXU†` must be Hermitian (conjugation preserves Hermiticity), have eigenvalues `±1`, and lie in `P_1`. The elements of `P_1` that are Hermitian with trace 0 are `±X, ±Y, ±Z`: **6 choices**. (`±iX` etc. are anti-Hermitian; `±I` has the wrong spectrum.)

Step 2 — image of `Z`. `UZU†` must likewise be one of `±X, ±Y, ±Z`, and it must anticommute with `UXU†` because `XZ = -ZX` is preserved by conjugation. Whichever axis `UXU†` occupies, the anticommuting choices are the four signed Paulis on the other two axes: **4 choices**.

Step 3 — total: `6 × 4 = 24` admissible pairs. Every one is realised, because `H` and `S` alone generate 24 distinct conjugation actions (`HXH = Z, HZH = X, SXS† = Y, SZS† = Z`, and `SH` has order 3 modulo phase, cycling the axes `X → Z → Y → X`; the product in the other order, `HS`, also has order 3 but cycles only up to sign, `X ↦ -Y ↦ -Z ↦ X`). Numerical check: closing `{H, S}` under multiplication with matrices identified up to phase produces exactly 24 matrices, and their `(UXU†, UZU†)` pairs are 24 distinct signed pairs.

Structural reading: `C_1/U(1)` acts on the 6 signed axes `±X, ±Y, ±Z` as the rotation group of the octahedron, `S_4`, of order 24. Modulo the Paulis (which flip signs but keep axes), it permutes the three axes: `C_1 / P_1 ≅ S_3`, consistent with `24 / 4 = 6 = |S_3|` and with `C_1/P_1 ≅ Sp(2, F_2) ≅ S_3`.

*(b) Coset decomposition.* Write `C = Z(P_1) = {I, iI, -I, -iI}` for the center (using `C` rather than `Z` to avoid a clash with the Pauli `Z`). The four cosets are

- `I·C = {I, iI, -I, -iI}`
- `X·C = {X, iX, -X, -iX}`
- `Y·C = {Y, iY, -Y, -iY}`
- `Z·C = {Z, iZ, -Z, -iZ}`

They are disjoint, each has `|C| = 4` elements, and together they exhaust all 16 elements, as Lagrange demands (`[P_1 : C] = 16/4 = 4`). Coset multiplication is well defined since the center is normal: `(X·C)(Y·C) = (XY)·C = (iZ)·C = Z·C`, i.e. in symplectic coordinates `(1|0) + (1|1) = (0|1)`. Every coset squares to the identity coset because `X² = Y² = Z² = I`, so no element of the quotient has order 4: the quotient is `ℤ_2 × ℤ_2 ≅ F_2²`, with `X ↦ (1|0)`, `Z ↦ (0|1)`, `Y ↦ (1|1)`. Numerically, a brute-force enumeration of `P_1` confirms closure (all 256 products land in the 16-element set), a center of size exactly 4, and 4 cosets each of whose representatives squares into the center. By contrast the subgroup `⟨X⟩ = {I, X}` has 8 left cosets but is **not** normal — `Z X Z⁻¹ = -X ∉ ⟨X⟩` — so `P_1/⟨X⟩` is not a group.

## Summary

- A **group** packages closure, associativity, identity and inverses; the gates `U(2ⁿ)` form a group and nearly every gate set of interest is a subgroup
- **Lagrange**: subgroup orders divide the group order; cosets partition the group and are what hidden-subgroup algorithms sample
- **Normal subgroups** are kernels of homomorphisms and are exactly the subgroups you can quotient by; `G/ker φ ≅ im φ`
- **Parity** of a permutation is a homomorphism `S_n → {±1}`; the antisymmetric subspace it defines is where fermions live
- The **Pauli group** `P_n` has order `4^{n+1}`, center `{±I, ±iI}`, and quotient `F_2^{2n}`; commutation is the symplectic form `ω` on that quotient
- The **Clifford group** is the normalizer of `P_n` in `U(2ⁿ)`; modulo phase it has 24 elements for one qubit and acts on `F_2^{2n}` through `Sp(2n, F_2)`
- `GF(2)` and `GF(2ᵐ)` are the fields behind classical linear codes and the `GF(4)` description of stabilizer codes
- **Lie algebras** are tangent spaces at the identity; `𝔰𝔲(2)` is spanned by `σ_k/2` and exponentiates to every single-qubit gate
- `SU(2)` **double covers** `SO(3)`: `Ad(U) = Ad(-U)`, so a `2π` Bloch-sphere rotation is `-I` on the state

## Exercises

**Exercise 1**: List every subgroup of `ℤ_12`, giving a generator and the order of each, and confirm that the list is consistent with Lagrange's theorem. Which of them is the kernel of the homomorphism `φ: ℤ_12 → ℤ_4`, `φ(k) = k mod 4`?

<details><summary>Solution</summary>

A cyclic group of order 12 has exactly one subgroup for each divisor of 12, namely `⟨d⟩` for `d | 12`:

| generator `d` | subgroup | order |
|---|---|---|
| 1 | `ℤ_12` | 12 |
| 2 | `{0,2,4,6,8,10}` | 6 |
| 3 | `{0,3,6,9}` | 4 |
| 4 | `{0,4,8}` | 3 |
| 6 | `{0,6}` | 2 |
| 12 (i.e. 0) | `{0}` | 1 |

Six subgroups, with orders `1, 2, 3, 4, 6, 12` — every divisor of 12 and nothing else, as Lagrange requires. The kernel of `k ↦ k mod 4` is the set of multiples of 4, `⟨4⟩ = {0, 4, 8}` of order 3, and the first isomorphism theorem gives `ℤ_12/⟨4⟩ ≅ ℤ_4`; check: `12/3 = 4` ✓.

</details>

**Exercise 2**: Determine the parity of the permutations `σ = (1 2 3 4 5)` and `τ = (1 2)(3 4 5)` in `S_5`, and confirm your answer for `τ` by computing the determinant of its permutation matrix. Explain what the sign of `τ` does to a five-fermion wavefunction.

<details><summary>Solution</summary>

A cycle of length `L` is a product of `L - 1` transpositions. `σ` is a single 5-cycle: `4` transpositions, so `σ` is **even**, `sgn(σ) = +1`. `τ` is a 2-cycle times a 3-cycle: `1 + 2 = 3` transpositions, so `τ` is **odd**, `sgn(τ) = -1`.

The permutation matrix `P_τ` sends `e_1 ↔ e_2` and cycles `e_3 → e_4 → e_5 → e_3`. Its determinant is the product of the determinants of the blocks: the swap block has `det = -1` and the 3-cycle block has `det = +1` (a 3-cycle is even), so `det P_τ = -1` ✓ (numerically, `det` of the `5×5` matrix is `-1.0`).

For fermions the state lies in the antisymmetric subspace, where `S_5` acts through its sign character: `P_τ |Ψ⟩ = sgn(τ)|Ψ⟩ = -|Ψ⟩`. Relabelling the five particles by `τ` flips the sign of the wavefunction, while relabelling by `σ` leaves it unchanged.

</details>

**Exercise 3**: Convert each Pauli string to a symplectic vector `(x | z)` and use the symplectic form to decide whether the pairs commute: (a) `XZ` and `ZX`, (b) `XX` and `ZZ`, (c) `XI` and `ZI`, (d) `XYZ` and `ZXX`. Verify (a) and (c) by direct multiplication.

<details><summary>Solution</summary>

Per qubit: `I ↦ (0|0)`, `X ↦ (1|0)`, `Z ↦ (0|1)`, `Y ↦ (1|1)`; `ω = x·z' + z·x' mod 2`.

(a) `XZ ↦ (1,0 | 0,1)`, `ZX ↦ (0,1 | 1,0)`. `ω = (1·1 + 0·0) + (0·0 + 1·1) = 2 ≡ 0` — **commute**. Direct: `(X⊗Z)(Z⊗X) = XZ ⊗ ZX = (-ZX) ⊗ (-XZ) = ZX ⊗ XZ = (Z⊗X)(X⊗Z)` ✓ (two anticommutations cancel).

(b) `XX ↦ (1,1 | 0,0)`, `ZZ ↦ (0,0 | 1,1)`. `ω = (1+1) + 0 = 2 ≡ 0` — **commute** (this is why `XX` and `ZZ` can be measured together to identify the Bell basis).

(c) `XI ↦ (1,0 | 0,0)`, `ZI ↦ (0,0 | 1,0)`. `ω = 1 + 0 = 1` — **anticommute**. Direct: `(X⊗I)(Z⊗I) = XZ ⊗ I = -ZX ⊗ I = -(Z⊗I)(X⊗I)` ✓.

(d) `XYZ ↦ (1,1,0 | 0,1,1)`, `ZXX ↦ (0,1,1 | 1,0,0)`. `x·z' = 1·1 + 1·0 + 0·0 = 1`; `z·x' = 0·0 + 1·1 + 1·1 = 2`. `ω = 3 ≡ 1` — **anticommute**. (Equivalently: the strings differ by a non-identity, non-equal pair on qubits 1, 2 and 3 — three anticommuting positions, an odd number.)

A brute-force check over all `16 × 16` pairs of two-qubit Pauli strings confirms that `ω = 0` exactly when the Kronecker-product matrices commute.

</details>

**Exercise 4**: Build the multiplication table of `GF(4) = F_2[x]/(x² + x + 1)`, writing `ω` for the class of `x`. Then find all monic irreducible cubics over `F_2` and state the order of `x` in the multiplicative group of `GF(8) = F_2[x]/(x³ + x + 1)`.

<details><summary>Solution</summary>

In `GF(4)` the relation is `ω² = ω + 1`, hence `ω³ = ω·ω² = ω² + ω = 1`. The nonzero elements `{1, ω, ω²}` form the cyclic group `ℤ_3`:

| `·` | `0` | `1` | `ω` | `ω²` |
|---|---|---|---|---|
| `0` | 0 | 0 | 0 | 0 |
| `1` | 0 | 1 | `ω` | `ω²` |
| `ω` | 0 | `ω` | `ω²` | 1 |
| `ω²` | 0 | `ω²` | 1 | `ω` |

Addition is XOR on the coefficient pairs `a + bω`, e.g. `1 + ω = ω²` and `ω + ω² = 1`. (Under `I ↦ 0, X ↦ 1, Z ↦ ω, Y ↦ ω²`, the addition table is the Pauli multiplication table modulo phase; the same holds under the Calderbank-Rains-Shor-Sloane convention `X ↦ ω, Z ↦ ω², Y ↦ 1`.)

A cubic over `F_2` is irreducible iff it has no root in `{0, 1}` (a reducible cubic must have a linear factor). Of the four monic cubics with constant term 1 (constant term 0 gives the root 0), `x³ + 1` and `x³ + x² + x + 1` both vanish at `x = 1`; the survivors are `x³ + x + 1` and `x³ + x² + 1` — exactly two irreducible cubics. In `GF(8)ˣ`, a cyclic group of order 7 (prime), every non-identity element has order 7, so `x` has order 7: `x, x², x³ = x + 1, x⁴ = x² + x, x⁵ = x² + x + 1, x⁶ = x² + 1, x⁷ = 1`.

</details>

**Exercise 5**: For `U = R_z(π/2) = e^{-iπZ/4}`, compute the `3×3` rotation `Ad(U)` defined by `U σ_k U† = Σ_j Ad(U)_{jk} σ_j`. Show that `Ad(-U) = Ad(U)`, and compute `R_z(2π)` and `R_z(4π)` explicitly. Why is `R_z(2π) ≠ I` invisible on the Bloch sphere but visible in a controlled-`R_z(2π)` gate?

<details><summary>Solution</summary>

`U = diag(e^{-iπ/4}, e^{iπ/4})`. Conjugating: `UZU† = Z`; `UXU† = cos(π/2) X + sin(π/2) Y = Y`; `UYU† = -X`. Reading off columns (`Ad(U)_{jk} = ½ Tr(σ_j U σ_k U†)`):

`Ad(U) = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]`

a rotation by `+90°` about the `z`-axis, with `det = 1` ✓. Since `(-U) σ_k (-U)† = U σ_k U†`, the sign cancels and `Ad(-U) = Ad(U)` — two elements of `SU(2)` map to one element of `SO(3)`.

From `R_z(θ) = cos(θ/2) I - i sin(θ/2) Z`: `R_z(2π) = cos(π) I = -I` and `R_z(4π) = cos(2π) I = I`. On the Bloch sphere `-I` acts as `Ad(-I) = Ad(I) = I₃`, so a single-qubit state is unchanged: `(-I)ρ(-I)† = ρ`. In a controlled gate the phase is *relative*, not global: controlled-`(-I) = |0⟩⟨0| ⊗ I + |1⟩⟨1| ⊗ (-I) = Z ⊗ I`, a `Z` gate on the control, which is perfectly observable (it flips `|+⟩` to `|−⟩` on the control). This is the double cover made experimentally concrete.

</details>

## Further Reading

1. **Dummit & Foote**, *Abstract Algebra* (Wiley, 3rd ed.), Chapters 1–3 (groups, subgroups, quotients and homomorphisms) and Chapters 13–14 (field extensions; finite fields in §14.3) — the standard reference for everything in the first half of this chapter
2. **Artin**, *Algebra* (Pearson, 2nd ed.), Chapters 2, 6 and 9 — an unusually geometric treatment; Chapter 9 builds `SU(2)`, `SO(3)` and the double cover by hand
3. **Hall**, *Lie Groups, Lie Algebras, and Representations* (Springer, 2nd ed.), Chapters 1–3 — matrix Lie groups, the exponential map and `𝔰𝔲(2) ≅ 𝔰𝔬(3)` without manifold machinery
4. **Gottesman**, *Stabilizer Codes and Quantum Error Correction* (PhD thesis, Caltech 1997, arXiv:quant-ph/9705052), Chapters 2–3 — the Pauli group, symplectic representation and Clifford group as used in QEC
5. **Calderbank, Rains, Shor & Sloane**, "Quantum error correction via codes over GF(4)" (IEEE Trans. Inf. Theory 44, 1998) — the `GF(4)` encoding of the Pauli group, the bridge from finite fields to stabilizer codes, and the order formula `2^{n²+2n} ∏(4ʲ - 1)` for the Clifford group modulo phase
