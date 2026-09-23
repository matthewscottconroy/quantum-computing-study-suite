# Abstract Algebra for Quantum Computing

## Goal
Develop the algebraic structures — groups, rings, fields, and algebras — that underpin quantum symmetry, error correction, and the mathematical language of quantum theory.

---

## Module 1 — Groups

**Objective:** Understand groups as the mathematical language of symmetry and reversible operations — exactly what unitary gates are.

| Topic | Key Concepts |
|---|---|
| Group axioms | Closure, associativity, identity, inverses |
| Subgroups | Lagrange's theorem, cosets |
| Cyclic groups | Generator, order, ℤₙ |
| Permutation groups | Sₙ, cycle notation, even/odd permutations |
| Group homomorphisms | Kernel, image, isomorphism theorems |
| Normal subgroups | Quotient group G/N |

**Quantum connections:**
- The set of all n-qubit unitary matrices forms a group under multiplication: U(2ⁿ)
- Clifford gates form a finite group — central to error correction
- The symmetric group Sₙ appears in boson/fermion statistics

**Exercises:**
- Show that U(n) (unitary matrices) is a group

<details><summary>Solution</summary>

`U(n) = {U ∈ M_n(ℂ) : U†U = I}` under matrix multiplication. Check the four axioms.

**Closure.** If `U†U = I` and `V†V = I` then

`(UV)†(UV) = V†U†UV = V†IV = V†V = I`

so `UV ∈ U(n)`.

**Associativity.** Inherited from matrix multiplication, which is associative because it represents composition of linear maps.

**Identity.** `I†I = I`, so `I ∈ U(n)`, and `IU = UI = U`.

**Inverses.** `U†U = I` with `U` square makes `U` invertible with `U⁻¹ = U†` (a left inverse of a square matrix is two-sided). And `U†` is itself unitary: `(U†)†U† = UU† = I`. So `U⁻¹ = U† ∈ U(n)`. ∎

`U(n)` is non-abelian for `n ≥ 2`: `XZ = −ZX ≠ ZX`.

**Structure worth noting.** `det: U(n) → U(1)` is a group homomorphism (`det(UV) = det U det V`) and `|det U|² = det(U†U) = 1`, so the image really is the circle group. Its kernel is `SU(n) = {U : det U = 1}`, which is therefore a normal subgroup, and the first isomorphism theorem gives `U(n)/SU(n) ≅ U(1)`. Concretely: every unitary is a special unitary times a global phase, and the phase is physically invisible — the reason single-qubit gates are usually discussed as elements of `SU(2)` rather than `U(2)`.

**Quantum reading.** Closure = "a circuit of gates is a gate"; inverses = "every quantum computation is reversible"; the identity = "doing nothing is allowed". Postulate 2 of quantum mechanics is exactly the statement that closed-system dynamics are given by a group action of `U(2ⁿ)` on state space.

</details>

- Find all subgroups of ℤ₁₂

<details><summary>Solution</summary>

Every subgroup of a cyclic group is cyclic. If `H ≤ ℤ₁₂` is non-trivial, let `d` be its smallest positive element; dividing any `h ∈ H` by `d` gives `h = qd + r` with `0 ≤ r < d`, and `r = h − qd ∈ H` forces `r = 0`. So `H = ⟨d⟩`. Moreover `12 ∈ ⟨d⟩` (since `12 ≡ 0`), which forces `d | 12`. Conversely each divisor gives a subgroup, so there is exactly one subgroup per divisor of 12:

| generator `d` | subgroup | order `12/d` |
|---|---|---|
| 1 | `ℤ₁₂` | 12 |
| 2 | `{0,2,4,6,8,10}` | 6 |
| 3 | `{0,3,6,9}` | 4 |
| 4 | `{0,4,8}` | 3 |
| 6 | `{0,6}` | 2 |
| 12 ≡ 0 | `{0}` | 1 |

Six subgroups, of orders `1, 2, 3, 4, 6, 12` — exactly the divisors of 12, and nothing else. This is consistent with Lagrange's theorem (every subgroup order divides `|G|`), and in cyclic groups the converse also holds: for each divisor there is exactly *one* subgroup of that order. The subgroup lattice is the divisor lattice of 12, with `⟨d⟩ ⊆ ⟨e⟩ ⟺ e | d`.

Since `ℤ₁₂` is abelian, every subgroup is normal, and the quotients are again cyclic: `ℤ₁₂/⟨d⟩ ≅ ℤ_d`. For instance `⟨4⟩ = {0,4,8}` is the kernel of `k ↦ k mod 4`, and `ℤ₁₂/⟨4⟩ ≅ ℤ₄` — matching `12/3 = 4`. (The same computation appears as Exercise 1 of `docs/01_mathematical_foundations/04_groups_and_abstract_algebra.md`.)

</details>

- Prove the kernel of a homomorphism is always a normal subgroup

<details><summary>Solution</summary>

Let `φ: G → H` be a group homomorphism and `K = ker φ = {g ∈ G : φ(g) = e_H}`.

**`K` is a subgroup.** `φ(e_G) = e_H` because `φ(e_G) = φ(e_G e_G) = φ(e_G)φ(e_G)`; cancelling gives `φ(e_G) = e_H`, so `e_G ∈ K` and `K ≠ ∅`. If `a, b ∈ K` then

`φ(ab⁻¹) = φ(a)φ(b)⁻¹ = e_H e_H⁻¹ = e_H`

(using `φ(b⁻¹) = φ(b)⁻¹`, which follows from `φ(b)φ(b⁻¹) = φ(e) = e`), so `ab⁻¹ ∈ K`. By the one-step subgroup test, `K ≤ G`.

**`K` is normal.** For any `g ∈ G` and `k ∈ K`,

`φ(gkg⁻¹) = φ(g)φ(k)φ(g)⁻¹ = φ(g) e_H φ(g)⁻¹ = e_H`

so `gkg⁻¹ ∈ K`, i.e. `gKg⁻¹ ⊆ K` for every `g`. Applying this with `g⁻¹` gives `g⁻¹Kg ⊆ K`, hence `K ⊆ gKg⁻¹`, so `gKg⁻¹ = K` for all `g`. That is precisely normality, `K ⊴ G`. ∎

**Converse.** Every normal subgroup is a kernel: `N ⊴ G` is the kernel of the quotient map `π: G → G/N`, `g ↦ gN`. So "normal subgroup" and "kernel of a homomorphism" describe the same objects — this is what makes `G/N` well defined, and it is the content of the first isomorphism theorem `G/ker φ ≅ im φ`.

**Quantum examples.**
- `det: U(n) → U(1)` has kernel `SU(n) ⊴ U(n)`, giving `U(n)/SU(n) ≅ U(1)` — factoring out the global phase.
- The map `P_n → F_2^{2n}` sending a Pauli string to its symplectic vector `(x|z)` is a homomorphism whose kernel is the centre `{±I, ±iI}`; normality of the centre is why `P_n/Z(P_n) ≅ F_2^{2n}` is a group at all, and that quotient is the arena of the whole stabilizer formalism (`docs/01_mathematical_foundations/04_groups_and_abstract_algebra.md`).

</details>

---

## Module 2 — Lie Groups and Lie Algebras

**Objective:** Connect continuous symmetry groups to the generators used to construct quantum gates.

| Topic | Key Concepts |
|---|---|
| Matrix Lie groups | GL(n,ℂ), SU(n), SO(n) — groups that are also smooth manifolds |
| SU(2) and U(1) | Single-qubit gates live in SU(2) |
| Lie algebra | Tangent space at the identity, bracket `[A,B] = AB − BA` |
| Exponential map | `exp(iθG)` turns algebra elements into group elements |
| Generators | Pauli matrices as generators of SU(2) |
| Adjoint representation | How algebra elements act on each other |

**Quantum connections:**
- Every quantum gate `U = e^(iH)` for some Hermitian `H` (the generator/Hamiltonian)
- The Pauli group is the foundation of stabilizer codes
- SU(2) double-covers SO(3), explaining spinor behavior

**Exercises:**
- Verify that `e^(iθX/2)` is a valid single-qubit rotation

<details><summary>Solution</summary>

Because `X² = I`, the exponential series splits by parity:

```
e^{iθX/2} = Σₖ (iθ/2)ᵏ Xᵏ / k!
          = [Σ_{k even} (iθ/2)ᵏ/k!] I + [Σ_{k odd} (iθ/2)ᵏ/k!] X
          = cos(θ/2) I + i sin(θ/2) X
          = [[cos(θ/2),   i sin(θ/2)],
             [i sin(θ/2), cos(θ/2)  ]]
```

(confirmed numerically against `scipy.linalg.expm` at `θ = 0.9`).

**Unitary.** `(e^{iθX/2})† = cos(θ/2) I − i sin(θ/2) X`, so

`(e^{iθX/2})† e^{iθX/2} = cos²(θ/2) I + sin²(θ/2) X² = I` ✓

**Determinant 1.** `det = cos²(θ/2) − (i sin(θ/2))² = cos²(θ/2) + sin²(θ/2) = 1` ✓ (verified numerically). So it lies in `SU(2)`, not merely `U(2)` — it is a genuine rotation with no leftover global phase.

**General principle.** `e^{iA}` is unitary for any Hermitian `A` (here `A = θX/2`), because `(e^{iA})† = e^{−iA†} = e^{−iA} = (e^{iA})⁻¹`; and `det(e^{iA}) = e^{i Tr A}`, so tracelessness of `A` is exactly what puts the result in `SU(2)`. The Pauli matrices are traceless Hermitian, hence generators of `SU(2)`.

**Sign convention.** The corpus fixes `R_x(θ) = e^{−iθX/2}`, so

`e^{iθX/2} = R_x(−θ)`

(verified numerically). On the Bloch sphere this is a rotation by `−θ` about the `x`-axis — the same one-parameter subgroup, traversed in the opposite direction.

**Double cover.** At `θ = 2π`, `e^{iπX} = cos π · I + i sin π · X = −I`, not `I`. A full `2π` rotation returns every Bloch vector to where it started but multiplies the state by `−1`; only at `θ = 4π` does the matrix return to `I`. This is the `SU(2) → SO(3)` double cover, and it is physically real: it shows up as the sign flip in neutron-interferometry experiments and as the `−1` picked up by a fermionic mode under exchange.

</details>

- Compute `[X, Y]`, `[Y, Z]`, `[Z, X]` and identify the Lie algebra of SU(2)

<details><summary>Solution</summary>

First the products. `XY = [[0,1],[1,0]][[0,−i],[i,0]] = [[i,0],[0,−i]] = iZ`, and `YX = −iZ`. Cyclically, `YZ = iX`, `ZY = −iX`, `ZX = iY`, `XZ = −iY`. Hence

```
[X, Y] = XY − YX = 2iZ
[Y, Z] = 2iX
[Z, X] = 2iY
```

all verified numerically. Compactly, `[σ_a, σ_b] = 2i ε_{abc} σ_c` with `ε` the Levi-Civita symbol; the companion relation is `{σ_a, σ_b} = 2δ_{ab} I`, and the two together give `σ_a σ_b = δ_{ab} I + i ε_{abc} σ_c`.

**Identifying the algebra.** Rescale to `J_k = σ_k/2`:

```
[J_x, J_y] = iJ_z,   [J_y, J_z] = iJ_x,   [J_z, J_x] = iJ_y
```

(checked numerically) — exactly the angular-momentum algebra of `docs/01_mathematical_foundations/04_groups_and_abstract_algebra.md` and `docs/02_quantum_mechanics/08_angular_momentum_and_hydrogen.md`.

Strictly, `𝔰𝔲(2)` is a **real** Lie algebra: differentiating `U(t)†U(t) = I` at `t = 0` gives `A† + A = 0`, and `det U = 1` gives `Tr A = 0`, so

`𝔰𝔲(2) = {traceless anti-Hermitian 2×2 matrices} = span_ℝ{−iX/2, −iY/2, −iZ/2}`

a 3-dimensional real vector space. It is closed under the bracket: with `e_a = −iσ_a/2`,

`[e_x, e_y] = (−i)²[σ_x/2, σ_y/2] = −(i σ_z/2) = −iσ_z/2 = e_z`

so `[e_a, e_b] = ε_{abc} e_c` — the structure constants of `𝔰𝔬(3)`. The two algebras are isomorphic, `𝔰𝔲(2) ≅ 𝔰𝔬(3)`, which is the infinitesimal shadow of the `SU(2) → SO(3)` double cover: the groups differ globally (by the centre `{±I}`) but are identical near the identity.

**Why it matters for gates.** The exponential map sends the algebra onto the group: every single-qubit gate is `e^{−iθ n̂·σ/2}`, generated by the Hermitian combination `n̂·σ/2 ∈ i·𝔰𝔲(2)`. The commutators are what make gate sets universal — the Lie bracket of two available generators produces a *new* direction of motion, which is the algebraic content of "`H` and `T` generate a dense subgroup" and of Trotter-based Hamiltonian simulation.

</details>

- Show SU(2) matrices have determinant 1 and are unitary

<details><summary>Solution</summary>

`SU(2)` is *defined* as `{U ∈ M₂(ℂ) : U†U = I, det U = 1}`, so the content of the exercise is the explicit description: **every** such matrix has the form

```
U = [[ a,   b ],
     [−b*,  a*]]        with |a|² + |b|² = 1
```

**These matrices are in `SU(2)`.** `det U = a a* − b(−b*) = |a|² + |b|² = 1` ✓, and

`U†U = [[a*, −b],[b*, a]] [[a, b],[−b*, a*]] = [[|a|²+|b|², a*b − b a*],[b*a − a b*, |b|²+|a|²]] = I` ✓

**Every `SU(2)` matrix has this form.** For `U = [[a,b],[c,d]]` with `det U = 1`, the inverse is the adjugate: `U⁻¹ = [[d, −b],[−c, a]]`. Unitarity says `U⁻¹ = U† = [[a*, c*],[b*, d*]]`. Comparing entries: `d = a*` and `c = −b*`. Unitarity of the first column then gives `|a|² + |b|² = 1`. ∎

**Geometry.** Writing `a = a₁ + ia₂`, `b = b₁ + ib₂`, the constraint is `a₁² + a₂² + b₁² + b₂² = 1`: as a manifold `SU(2) ≅ S³`, the unit 3-sphere — compact, connected and simply connected, which is exactly why it is the universal cover of `SO(3) ≅ ℝP³`.

**Consistency with the rotation form.** For `U = e^{−iθ n̂·σ/2} = cos(θ/2) I − i sin(θ/2) n̂·σ`,

```
a = cos(θ/2) − i n_z sin(θ/2)
b = (−n_y − i n_x) sin(θ/2)
```

and `|a|² + |b|² = cos²(θ/2) + sin²(θ/2)(n_z² + n_y² + n_x²) = 1` ✓, since `n̂` is a unit vector. So the Euler-angle-free parametrization of a single-qubit gate and the `(a, b)` parametrization of `SU(2)` are the same two complex numbers. `U(2) = SU(2) × U(1)/{±1}`: an arbitrary gate is an `SU(2)` rotation times an unobservable global phase, which is why gate synthesis and the Bloch sphere only ever need `SU(2)`.

</details>

---

## Module 3 — Rings and Fields

**Objective:** Understand the algebraic structures behind finite field arithmetic used in classical error correction and quantum stabilizer codes.

| Topic | Key Concepts |
|---|---|
| Ring axioms | Two operations, distributivity, not necessarily invertible |
| Integral domains | No zero divisors |
| Fields | Every nonzero element is invertible |
| Finite fields GF(q) | Exist when q = pⁿ for prime p |
| Polynomial rings | GF(2)[x], factoring, irreducible polynomials |
| Field extensions | GF(2⁴) from GF(2) |

**Quantum connections:**
- Binary stabilizer codes work over GF(2)
- Reed-Solomon and BCH codes (classical) inform quantum LDPC codes
- GF(4) encodes the symplectic structure of the Pauli group

**Exercises:**
- Construct the addition and multiplication tables for GF(4)

<details><summary>Solution</summary>

Build `GF(4) = F_2[x]/(x² + x + 1)` — the quotient is a field because `x² + x + 1` has no root in `F_2` (`0² + 0 + 1 = 1`, `1 + 1 + 1 = 1`) and so is irreducible. Writing `ω` for the class of `x`, the elements are `{0, 1, ω, ω²}` with the single defining relation

`ω² = ω + 1`   (equivalently `ω² + ω + 1 = 0`, since `−1 = +1` in characteristic 2)

**Addition** is componentwise `XOR` of the coefficient pair `(c₁, c₀)` in `c₁ω + c₀`; every element is its own additive inverse:

| `+` | 0 | 1 | ω | ω² |
|---|---|---|---|---|
| **0** | 0 | 1 | ω | ω² |
| **1** | 1 | 0 | ω² | ω |
| **ω** | ω | ω² | 0 | 1 |
| **ω²** | ω² | ω | 1 | 0 |

(Read off `1 + ω = ω²` and `ω + ω² = 1` directly from `ω² = ω + 1`.)

**Multiplication** uses `ω³ = ω·ω² = ω² + ω = 1`, so the non-zero elements form the cyclic group `⟨ω⟩ ≅ ℤ₃`:

| `×` | 0 | 1 | ω | ω² |
|---|---|---|---|---|
| **0** | 0 | 0 | 0 | 0 |
| **1** | 0 | 1 | ω | ω² |
| **ω** | 0 | ω | ω² | 1 |
| **ω²** | 0 | ω² | 1 | ω |

Both tables were generated and checked by exhaustive polynomial arithmetic in the venv; the multiplication table confirms `ω·ω = ω²` and `ω³ = 1`.

**Two points worth internalising.**

1. `GF(4) ≠ ℤ₄`. In `ℤ₄`, `2·2 = 0` — zero divisors, so it is not a field. `GF(4)` has characteristic 2 (`x + x = 0` for all `x`), not 4. Finite fields exist exactly for prime-power orders, and for order `pⁿ` with `n > 1` they are *never* `ℤ_{pⁿ}`.
2. `GF(4)` is the natural alphabet for Pauli operators. Using the corpus dictionary `I ↦ 0`, `X ↦ 1`, `Z ↦ ω`, `Y ↦ ω²` (`docs/01_mathematical_foundations/04_groups_and_abstract_algebra.md`), multiplication of Paulis modulo phase becomes **addition** in `GF(4)`: `X·Z = −iY` ↔ `1 + ω = ω²` ✓, `Y·Z = iX` ↔ `ω² + ω = 1` ✓. An `n`-qubit Pauli string modulo phase is then a vector in `GF(4)ⁿ`, and stabilizer codes become additive codes over `GF(4)` — the Calderbank–Rains–Shor–Sloane picture. (Their paper uses the alternative dictionary `X ↦ ω`, `Z ↦ ω²`, `Y ↦ 1`; any bijection respecting `Y = X·Z` works.)

</details>

- Find an irreducible polynomial over GF(2) of degree 3

<details><summary>Solution</summary>

A polynomial of degree 2 or 3 over a field is irreducible **iff** it has no root in that field: any non-trivial factorization of a cubic must contain a linear factor, and a linear factor `x − r` corresponds to a root `r`.

Over `GF(2)` there are only two points to test, so a monic cubic `f(x) = x³ + c₂x² + c₁x + c₀` is irreducible iff

- `f(0) = c₀ = 1` (non-zero constant term), and
- `f(1) = 1 + c₂ + c₁ + c₀ = 1`, i.e. the polynomial has an **odd** number of non-zero coefficients.

The monic cubics with `c₀ = 1` are `x³+1`, `x³+x+1`, `x³+x²+1`, `x³+x²+x+1`. Testing `f(1)`: `x³+1 → 0` (root at 1), `x³+x+1 → 1` ✓, `x³+x²+1 → 1` ✓, `x³+x²+x+1 → 0`. So exactly two irreducible cubics exist over `GF(2)`:

```
x³ + x + 1        and        x³ + x² + 1
```

confirmed by exhaustive search over all eight monic cubics in the venv. (They are reverses of each other, hence give isomorphic field extensions — as they must, since `GF(8)` is unique up to isomorphism.)

**Using one.** `GF(8) = F_2[x]/(x³ + x + 1)` has 8 elements `{0, 1, α, α+1, α², α²+1, α²+α, α²+α+1}` where `α³ = α + 1`. The multiplicative group has order 7, a prime, so *every* non-identity element is a generator; in particular `α` is primitive, and `1, α, α², …, α⁶` enumerate all non-zero elements.

**Why this shows up in quantum computing.** Irreducible polynomials over `GF(2)` are the generator polynomials of classical cyclic codes, and `x³ + x + 1` generates (up to a coordinate permutation) the `[7,4,3]` Hamming code — the classical ingredient from which the CSS construction builds the Steane `[[7,1,3]]` code (`docs/05_quantum_error_correction/05_css_codes_and_steane.md`). The same machinery, over `GF(2^m)`, gives BCH and Reed–Solomon codes, which feed into quantum LDPC and concatenated-code constructions.

</details>

- Show that ℤₚ is a field for prime p but not for composite n

<details><summary>Solution</summary>

`ℤ_n` is always a commutative ring with identity; the only axiom in question is invertibility of every non-zero element.

**`p` prime `⟹` `ℤ_p` is a field.** Let `a ∈ {1, …, p−1}`. Since `p` is prime and `p ∤ a`, `gcd(a, p) = 1`, so Bézout's identity gives integers `u, v` with

`ua + vp = 1`

Reducing mod `p`: `ua ≡ 1 (mod p)`, so `[u]` is a multiplicative inverse of `[a]`. Every non-zero class is invertible, and `1 ≢ 0` because `p > 1`, so `ℤ_p` is a field. (Constructively, `u` comes from the extended Euclidean algorithm — the same routine used for modular inverses in Shor's post-processing.)

**`n` composite `⟹` `ℤ_n` is not a field.** Write `n = ab` with `1 < a, b < n`. Then `[a] ≠ 0` and `[b] ≠ 0`, but `[a][b] = [n] = 0`: `ℤ_n` has **zero divisors**. A field cannot: if `[a]` had an inverse `[a]⁻¹`, then

`[b] = [a]⁻¹[a][b] = [a]⁻¹·0 = 0`

contradicting `[b] ≠ 0`. So `[a]` is not invertible and `ℤ_n` is not a field. ∎

**Example.** In `ℤ₆`: `2·3 = 0`, and the units are only `{1, 5}` (those `k` with `gcd(k,6) = 1`). In general `|ℤ_n^×| = φ(n)`, which equals `n − 1` exactly when `n` is prime.

**Consequences used later.**
- Finite fields have prime-power order `q = pᵐ`, and for `m > 1` they are *not* `ℤ_q` — they are `F_p[x]/(irreducible of degree m)`, as in the `GF(4)` and `GF(8)` exercises above.
- Binary linear codes and the whole stabilizer formalism are linear algebra over `GF(2) = ℤ₂`: Gaussian elimination, row space, null space and rank all work because `ℤ₂` is a field. Over `ℤ₄` (a ring, not a field) none of that is available in the same form, which is why the symplectic picture uses `F_2^{2n}` rather than `ℤ_4^n`.
- `ℤ_n` being a ring rather than a field is precisely the structure Shor's algorithm exploits: the multiplicative group `ℤ_N^×` for composite `N` is what period finding probes, and a "failure" of invertibility (a non-trivial `gcd`) is a factor.

</details>

---

## Module 4 — Vector Spaces over Fields (Algebraic View)

**Objective:** Re-examine linear algebra through the abstract algebraic lens to understand stabilizer codes and syndrome decoding.

| Topic | Key Concepts |
|---|---|
| Modules vs vector spaces | Module: ring of scalars; vector space: field of scalars |
| Linear codes as subspaces | Codewords form a subspace of GF(2)ⁿ |
| Dual space and parity checks | H-matrix, syndrome, dual code |
| Symplectic vector spaces | Inner product structure on GF(2)²ⁿ |

**Quantum connections:**
- Stabilizer codes are defined by isotropic subspaces of GF(2)²ⁿ (symplectic)
- The symplectic inner product detects whether two Paulis commute or anti-commute

**Exercises:**
- Find the dual of the [7,4] Hamming code

<details><summary>Solution</summary>

Use the corpus parity-check matrix, whose columns are the binary representations of `1, …, 7` (`docs/05_quantum_error_correction/05_css_codes_and_steane.md`):

```
H = | 0 0 0 1 1 1 1 |
    | 0 1 1 0 0 1 1 |
    | 1 0 1 0 1 0 1 |
```

The Hamming code is `C = ker H = [7, 4, 3]`: exhaustive enumeration in the venv gives `|C| = 16 = 2⁴` codewords with weight distribution `{0: 1, 3: 7, 4: 7, 7: 1}`, so `d = 3` ✓.

**The dual.** By definition `C⊥ = {y : y·c = 0 for all c ∈ C}`, and for a code with parity-check matrix `H` the dual is the **row space of `H`**:

```
C⊥ = rowspace(H) = [7, 3, 4]
```

with `dim C + dim C⊥ = 4 + 3 = 7 = n` ✓ and `|C|·|C⊥| = 16 · 8 = 128 = 2⁷` ✓. Enumerating it: 8 codewords, the zero word plus **seven words all of weight 4** (verified). A code whose non-zero words all have the same weight is a *simplex* code; `[7,3,4]` is the simplex code, the dual of the Hamming code and the punctured first-order Reed–Muller code `RM(1,3)`.

**The property that matters: `C⊥ ⊆ C` (dual-containing).** Checked exhaustively — all 8 dual codewords lie in `C`. The structural reason is `H Hᵀ = 0` over `GF(2)`: each row of `H` has weight 4 (even, so it is orthogonal to itself in characteristic 2) and any two distinct rows overlap in exactly 2 positions (even), so every row of `H` is in `ker H = C`; since the rows generate `C⊥`, the whole dual sits inside `C`.

**Why this is the punchline.** The CSS construction needs a pair `C₂ ⊆ C₁`; taking `C₁ = C` and `C₂ = C⊥` yields the Steane code

`[[n, k₁ − k₂, min(d(C₁), d(C₂⊥))]] = [[7, 4 − 3, min(3,3)]] = [[7,1,3]]`

with three `X`-type stabilizers `g_{X,i}` and three `Z`-type stabilizers `g_{Z,i}`, both read off the rows of the same `H`. Because the same matrix does both jobs, the `X` and `Z` syndromes are ordinary Hamming syndromes: the 3-bit syndrome read as a binary number is the index of the faulty qubit.

</details>

- Determine which Pauli pairs commute using the symplectic inner product

<details><summary>Solution</summary>

**The dictionary** (corpus convention, `docs/01_mathematical_foundations/04_groups_and_abstract_algebra.md`): a Pauli string modulo phase becomes a vector `(x | z) ∈ F_2^{2n}`, with `x_j = 1` if qubit `j` carries `X` or `Y`, and `z_j = 1` if it carries `Z` or `Y`. Per qubit: `I ↦ (0|0)`, `X ↦ (1|0)`, `Z ↦ (0|1)`, `Y ↦ (1|1)`. The symplectic form is

```
ω( (x|z), (x'|z') ) = Σⱼ ( xⱼ z'ⱼ + zⱼ x'ⱼ )  mod 2
```

and `P, Q` **commute iff `ω = 0`**, anticommute iff `ω = 1`. (Reason: `PQ = (−1)^ω QP`; each qubit position where the two factors are different non-identity Paulis contributes one anticommuting swap, and `ω` counts those positions mod 2.)

**Worked pairs** (all cross-checked by explicit matrix multiplication in the venv):

| pair | `(x\|z)` of first | `(x\|z)` of second | `ω` | verdict |
|---|---|---|---|---|
| `XZ`, `ZX` | `(10\|01)` | `(01\|10)` | `1·1 + 0·0 + 0·0 + 1·1 = 0` | commute |
| `XX`, `ZZ` | `(11\|00)` | `(00\|11)` | `1·1 + 1·1 + 0 + 0 = 0` | commute |
| `XI`, `ZI` | `(10\|00)` | `(00\|10)` | `1·1 = 1` | anticommute |
| `XYZ`, `ZXX` | `(110\|011)` | `(011\|100)` | `= 1` | anticommute |

Reading the first two rows the intuitive way: `XZ` vs `ZX` disagree at *both* qubits (X↔Z, then Z↔X), two anticommutations that cancel; `XX` vs `ZZ` likewise disagree at both positions. `XI` vs `ZI` disagree at exactly one position, so they anticommute — and indeed `X Z = −Z X`.

**Why this is the right tool.** Deciding commutation from matrices costs `O(4ⁿ)` work; the symplectic form costs `O(n)`. Everything in the stabilizer formalism is phrased in this language:

- a **stabilizer group** is an *isotropic* subspace (`ω = 0` on every pair), which is what allows a simultaneous `+1` eigenspace;
- the **normalizer** of a stabilizer is its symplectic complement, and logical operators are the quotient of the two;
- the number of independent generators is capped at `n`, because an isotropic subspace of a `2n`-dimensional symplectic space has dimension at most `n` — this is the algebraic reason an `[[n, k, d]]` code has `n − k` stabilizer generators.

</details>

- Encode a logical qubit in the 5-qubit perfect code using its stabilizer generators

<details><summary>Solution</summary>

The `[[5,1,3]]` perfect code has four stabilizer generators, each a cyclic shift of the previous one:

```
g₁ = X Z Z X I
g₂ = I X Z Z X
g₃ = X I X Z Z
g₄ = Z X I X Z
```

**Step 1 — they generate a valid stabilizer group.** The symplectic form vanishes on every pair (the full `4×4` table of `ω` values is all zeros, verified in the venv, and confirmed by direct matrix multiplication), so `S = ⟨g₁,g₂,g₃,g₄⟩` is abelian. The four generators are independent and `−I ∉ S`, so `|S| = 2⁴ = 16` and the joint `+1` eigenspace has dimension `2⁵/2⁴ = 2`: one logical qubit.

**Step 2 — the code projector.**

```
Π = ∏ᵢ (I + gᵢ)/2 = (1/16) Σ_{g ∈ S} g
```

Numerically `Π² = Π` and `rank Π = 2` ✓.

**Step 3 — encode.** Apply `Π` to `|00000⟩` and normalize. All 16 group elements contribute a distinct basis string with amplitude `±1/4`:

```
|0_L⟩ = ¼ ( + |00000⟩ − |00011⟩ + |00101⟩ − |00110⟩
            + |01001⟩ + |01010⟩ − |01100⟩ − |01111⟩
            − |10001⟩ + |10010⟩ + |10100⟩ − |10111⟩
            − |11000⟩ − |11011⟩ − |11101⟩ − |11110⟩ )
```

(computed exactly in the venv from `Π|00000⟩`; norm `= 16·(1/16) = 1` ✓). Every string has even weight, which is the visible signature of `Z̄ = ZZZZZ` acting as `+1` here.

**Step 4 — logical operators and `|1_L⟩`.** `X̄ = XXXXX` and `Z̄ = ZZZZZ` both commute with all four generators (verified), lie outside `S`, and anticommute with each other — exactly the algebra of a logical qubit. Then

`|1_L⟩ = X̄|0_L⟩`

which, since `X^{⊗5}` complements every bit, is obtained from the expansion above by **flipping all five bits of each basis string while keeping its sign**: `+|11111⟩ − |11100⟩ + |11010⟩ − …`. Checks performed numerically: `Z̄|0_L⟩ = +|0_L⟩` and `Z̄|1_L⟩ = −|1_L⟩` ✓, and `⟨0_L|1_L⟩ = 0`.

**Why "perfect".** `n = 5` saturates the quantum Hamming bound for `k = 1, t = 1`: `2¹(1 + 3·5) = 32 = 2⁵` — the 16 syndromes exactly label "no error" plus the `3 × 5 = 15` single-qubit Pauli errors, with none left over (`docs/05_quantum_error_correction/03_repetition_code.md`). It also saturates the quantum Singleton bound `n − k ≥ 2(d−1)`, so no distance-3 code can use fewer than five qubits.

</details>

---

## Module 5 — Algebras and the Clifford Algebra

**Objective:** Understand the algebraic structure that unifies spinors, Pauli matrices, and quantum gates into a single framework.

| Topic | Key Concepts |
|---|---|
| Associative algebras | Algebra over a field, dimension, basis |
| Clifford algebra Cl(n) | Generated by {γᵢ} with `γᵢγⱼ + γⱼγᵢ = 2δᵢⱼ` |
| Pauli algebra | Cl(3) ≅ M₂(ℂ) ⊕ M₂(ℂ) — Pauli matrices as generators |
| Clifford gates | Normalizer of Pauli group, efficiently simulable |
| Gottesman-Knill theorem | Clifford circuits are classically simulable |

**Exercises:**
- Show that X, Y, Z satisfy the Clifford algebra relations

<details><summary>Solution</summary>

The defining relations of the Clifford algebra `Cl(3)` on generators `γ₁, γ₂, γ₃` are

```
γᵢγⱼ + γⱼγᵢ = 2δᵢⱼ · 1
```

Set `γ₁ = X`, `γ₂ = Y`, `γ₃ = Z`.

**Diagonal case `i = j`.** `X² = Y² = Z² = I`, so `γᵢγᵢ + γᵢγᵢ = 2I = 2δᵢᵢ I` ✓.

**Off-diagonal case `i ≠ j`.** From `XY = iZ` and `YX = −iZ`,

```
XY + YX = iZ − iZ = 0
YZ + ZY = iX − iX = 0
ZX + XZ = iY − iY = 0
```

✓ — distinct Paulis anticommute. Both families together are the single identity `σ_aσ_b = δ_{ab} I + i ε_{abc} σ_c`, whose symmetric part gives the Clifford relations and whose antisymmetric part gives the Lie brackets `[σ_a,σ_b] = 2iε_{abc}σ_c` of Module 2. The Clifford algebra and the Lie algebra are the two halves of the same product rule.

**The algebra they generate.** Products of *distinct* generators give a basis

```
1 ;  X, Y, Z ;  XY, YZ, ZX ;  XYZ
```

`1 + 3 + 3 + 1 = 8` elements, so the real span is 8-dimensional — matching `dim_ℝ Cl(3) = 2³ = 8`. Concretely `XY = iZ`, `YZ = iX`, `ZX = iY` and the **pseudoscalar** `XYZ = iI`, which is central (it commutes with everything, being a scalar) and satisfies `(XYZ)² = (iI)² = −I`.

**The isomorphism in the module table.** Because the pseudoscalar `ω = γ₁γ₂γ₃` is central with `ω² = −1`, complexifying gives two central idempotents `(1 ± iω)/2`, and the complex Clifford algebra splits:

`Cl(3) ⊗ ℂ ≅ M₂(ℂ) ⊕ M₂(ℂ)`

(complex dimension `8 = 4 + 4`) — exactly the entry in the module table. The two summands are the two inequivalent 2-dimensional irreducible representations, differing by the sign of the pseudoscalar, i.e. by the chirality/handedness of the Pauli triple `(X, Y, Z)` versus `(X, −Y, Z)`. The real algebra generated by the Paulis inside `M₂(ℂ)` is one of these blocks, `Cl(3,0) ≅ M₂(ℂ)` as a real algebra.

**Payoff.** `Cl(3)` is why a qubit *is* a spinor: the even subalgebra `span{1, XY, YZ, ZX}` is isomorphic to the quaternions `ℍ ≅ SU(2)`, and its unit group acting by conjugation gives the Bloch-sphere rotations. Clifford algebras in higher dimensions do the same job for fermionic modes, where `Cl(2n)` generators are the Majorana operators of the Jordan–Wigner transform.

</details>

- Prove that H, S, CNOT generate the Clifford group

<details><summary>Solution</summary>

Fix the definition: the **Clifford group** `C_n` is the normalizer of the Pauli group in `U(2ⁿ)`, `C_n = {U : U P U† ∈ P_n for all P ∈ P_n}`. Generation statements are always *modulo global phase* — the matrix group `⟨H, S, CNOT⟩` also contains scalars such as `(SH)³ = e^{iπ/4} I` (verified numerically), which are physically irrelevant.

**Step 1 — the generators are Clifford.** Check the conjugation action on `X` and `Z` (which determines it on all of `P_n`, since `Y = iXZ`):

```
H X H = Z            H Z H = X
S X S† = Y           S Z S† = Z
CNOT (X⊗I) CNOT = X⊗X       CNOT (I⊗X) CNOT = I⊗X
CNOT (Z⊗I) CNOT = Z⊗I       CNOT (I⊗Z) CNOT = Z⊗Z
```

All four `CNOT` relations verified numerically. Paulis map to Paulis, so each generator normalizes `P_n`.

**Step 2 — a Clifford is determined, mod phase, by a symplectic matrix plus signs.** `U ↦ (U X_j U†, U Z_j U†)_j` records `2n` Pauli strings. Conjugation preserves commutation relations, so in symplectic coordinates the map `F_2^{2n} → F_2^{2n}` it induces preserves the form `ω` — it is an element of `Sp(2n, F_2)`. Two Cliffords with the same symplectic action and the same output signs differ by a scalar (their ratio commutes with all Paulis, and the Paulis span the matrix algebra, so by Schur the ratio is `λI`). Hence

`C_n / (P_n · U(1)) ≅ Sp(2n, F_2)`

**Step 3 — the generators realise elementary symplectic moves.** In the `(x|z)` coordinates of Module 4:

- `H` on qubit `j` swaps `x_j ↔ z_j`;
- `S` on qubit `j` is the shear `z_j ← z_j + x_j`;
- `CNOT` with control `c`, target `t` is `x_t ← x_t + x_c`, `z_c ← z_c + z_t`.

These are exactly the elementary row/column operations that Gaussian elimination needs. Gottesman's canonical-form algorithm sweeps the `2n × 2n` symplectic matrix qubit by qubit: use `H`/`S` to make the leading entry an `X`, use `CNOT`s to clear the rest of the row, then recurse on the remaining `2(n−1)` coordinates. Every element of `Sp(2n, F_2)` is therefore a product of these moves.

**Step 4 — recover the signs and the Paulis.** The symplectic part fixes `U` only up to a Pauli; but the Paulis themselves are generated, `Z = S²` and `X = HS²H`, so multiplying by a suitable Pauli finishes the job. Hence `⟨H, S, CNOT⟩ = C_n` modulo phase. ∎

**Numerical confirmation.** Breadth-first closure of the generated matrix group modulo global phase, in the venv:

- one qubit: `|⟨H, S⟩| = 24`, matching the count of 24 single-qubit Cliffords in `docs/01_mathematical_foundations/04_groups_and_abstract_algebra.md`;
- two qubits: `|⟨H₁, H₂, S₁, S₂, CNOT₁₂⟩| = 11520`, matching the closed form `|C_n/U(1)| = 2^{n²+2n} ∏_{j=1}^{n}(4ʲ − 1)`, which for `n = 2` gives `2⁸ · 3 · 15 = 11520`.

The generated group also contains `SWAP` and every single-qubit Pauli, as it must.

</details>

- Explain why Clifford + T gives universal quantum computation

<details><summary>Solution</summary>

Four ingredients, each doing a distinct job.

**1. Clifford alone cannot be universal.** Modulo phase, `|C_n| = 2^{n²+2n} ∏_{j=1}^{n}(4ʲ − 1)` is *finite* (11520 for two qubits, verified above), while `SU(2ⁿ)` is a continuum: a finite set cannot be dense. Worse, the Gottesman–Knill theorem says a Clifford circuit acting on a stabilizer input with Pauli measurements can be simulated classically in `O(n²)` time per gate by updating the `2n × 2n` symplectic tableau. Clifford circuits produce entanglement and interference but no quantum advantage.

**2. `T` is outside the Clifford group.** `T = diag(1, e^{iπ/4})` conjugates `X` to

`T X T† = [[0, e^{−iπ/4}],[e^{iπ/4}, 0]] = (X + Y)/√2`

(verified numerically) — a *sum* of Paulis, not a Pauli. So `T ∉ C_1`. It does map Paulis into the Clifford group (`(X+Y)/√2` is Clifford), which places `T` at level 3 of the Clifford hierarchy.

**3. Clifford + `T` is dense in `SU(2)`.** Up to phase `T ∝ R_z(π/4)` and `HTH ∝ R_x(π/4)`, so

`THTH ∝ R_z(π/4) R_x(π/4) = cos²(π/8) I − i [ cos(π/8)sin(π/8)(X + Z) + sin²(π/8) Y ]`

This is a rotation `R_n̂(θ)` about the fixed axis `n̂ ∝ (cos(π/8)sin(π/8), sin²(π/8), cos(π/8)sin(π/8))` with

`cos(θ/2) = cos²(π/8) = (2 + √2)/4 ≈ 0.8535534`, hence `θ ≈ 1.09606 rad ≈ 62.80°`

(all values computed numerically). The key classical fact (Nielsen & Chuang §4.5.3) is that this `θ` is an **irrational multiple of `π`** — `θ/π ≈ 0.348886…`. An irrational rotation angle makes `{R_n̂(θ)^k : k ∈ ℕ}` dense in the whole one-parameter subgroup of rotations about `n̂`. Conjugating by `H` gives dense rotations about a second axis `n̂' = H n̂ H`, which is not parallel to `n̂`, and rotations about two non-parallel axes generate a dense subgroup of `SU(2)`. So any single-qubit gate can be approximated to arbitrary accuracy.

**4. Dense single-qubit + `CNOT` = universal.** The standard construction decomposes an arbitrary `U ∈ U(2ⁿ)` into two-level unitaries, each of which is a controlled single-qubit rotation, each of which compiles into `CNOT`s and single-qubit gates. Since `CNOT` is Clifford and the single-qubit gates are approximable by step 3, `{H, S, CNOT, T}` is universal.

**5. From dense to *efficient*: Solovay–Kitaev.** Density alone could require exponentially many gates. The Solovay–Kitaev theorem says any single-qubit unitary can be approximated to accuracy `ε` using `O(log^c(1/ε))` gates from any dense, inverse-closed generating set, with `c ≈ 2`; for Clifford+`T` specifically, number-theoretic synthesis (Ross–Selinger) achieves `≈ 3 log₂(1/ε)` `T` gates, which is optimal up to constants.

**Practical consequence.** In fault-tolerant architectures Clifford gates are cheap — often transversal — while `T` is not (Eastin–Knill forbids a transversal universal gate set), so `T` must be injected via magic-state distillation. That is why **`T`-count** and **`T`-depth**, not total gate count, are the headline cost metrics for fault-tolerant compilation.

</details>

---

## Module 6 — Group Representations (Preview)

**Objective:** Bridge abstract group theory to concrete matrix actions — the full treatment appears in the Representation Theory lesson plan.

| Topic | Key Concepts |
|---|---|
| Group representation | Homomorphism ρ: G → GL(V) |
| Faithful representation | Injective homomorphism |
| Regular representation | G acting on itself by multiplication |
| Character | χ(g) = Tr(ρ(g)), class function |

**Exercises:**
- Write down the regular representation of ℤ₃

<details><summary>Solution</summary>

The regular representation acts on the group algebra `ℂ[ℤ₃]`, which has one basis vector per group element: `{|0⟩, |1⟩, |2⟩}`. The action is left translation,

`ρ(k)|j⟩ = |j + k mod 3⟩`

so the degree is `|G| = 3`. Explicitly, `ρ(0) = I` and

```
ρ(1) = [[0, 0, 1],        ρ(2) = ρ(1)² = [[0, 1, 0],
        [1, 0, 0],                        [0, 0, 1],
        [0, 1, 0]]                        [1, 0, 0]]
```

`ρ(1)` is the cyclic shift (column `j` has a 1 in row `j+1 mod 3`). Check: `ρ(1)³ = I` ✓, and `ρ` is faithful since `ρ(1) ≠ I ≠ ρ(2)`, and it is a homomorphism because translation by `k` then by `k'` is translation by `k + k'`.

**Character.** `χ_reg(k) = Tr ρ(k) = #{j : j + k ≡ j} = 3` if `k = 0`, else `0`. So `χ_reg = (3, 0, 0)` — the general fact `χ_reg(g) = |G| δ_{g,e}`.

**Decomposition.** The eigenvalues of the shift are the cube roots of unity, `1, ω, ω²` with `ω = e^{2πi/3}`, so

`ρ_reg ≅ χ₀ ⊕ χ₁ ⊕ χ₂`

each one-dimensional irrep appearing exactly once, in agreement with the general theorem "multiplicity of `Vᵢ` in the regular representation `= dim Vᵢ`" (here all `dim = 1`, and `Σ dᵢ² = 3 = |G|` ✓). Via characters: `⟨χ_k, χ_reg⟩ = (1/3)(χ_k(0)* · 3) = 1` for each `k`.

The eigenvector for character `χ_k` is `|v_k⟩ = (1/√3) Σ_j ω^{jk}|j⟩`, and `ρ(1)|v_k⟩ = ω^{−k}|v_k⟩` (verified numerically for `k = 0, 1, 2`). The change of basis from `{|j⟩}` to `{|v_k⟩}` is the 3-point discrete Fourier transform. That is the whole content of "the QFT diagonalizes the cyclic shift", and it generalises verbatim to `ℤ_N` — the representation-theoretic reason the QFT is the right tool for period finding.

</details>

- Find all irreps of ℤ₄

<details><summary>Solution</summary>

**Why they are all one-dimensional.** `ℤ₄` is abelian, so in any irrep `ρ` every `ρ(g)` commutes with every `ρ(h)`. By Schur's lemma, an operator commuting with an irreducible representation is a scalar, so each `ρ(g) = λ_g I`. But then *every* subspace is invariant, and irreducibility forces `dim V = 1`. Equivalently: the number of irreps equals the number of conjugacy classes, which for an abelian group is `|G| = 4`, and `Σ dᵢ² = 4` with four summands forces every `dᵢ = 1`.

**The four characters.** A 1-dimensional representation is determined by `ρ(1) = λ` with `λ⁴ = 1`, so `λ ∈ {1, i, −1, −i}`. Writing `χ_k(j) = i^{jk}` for `k = 0,1,2,3`:

| `ℤ₄` | `j = 0` | `j = 1` | `j = 2` | `j = 3` |
|---|---|---|---|---|
| `χ₀` | 1 | 1 | 1 | 1 |
| `χ₁` | 1 | `i` | −1 | `−i` |
| `χ₂` | 1 | −1 | 1 | −1 |
| `χ₃` | 1 | `−i` | −1 | `i` |

matching `docs/01_mathematical_foundations/05_representation_theory.md`.

**Checks.**
- `Σ dᵢ² = 1 + 1 + 1 + 1 = 4 = |G|` ✓
- Orthogonality `⟨χ_k, χ_l⟩ = ¼ Σ_j i^{−jk} i^{jl} = ¼ Σ_j i^{j(l−k)} = δ_{kl}`, since for `l ≢ k` the sum is a full geometric series of a non-trivial 4th root of unity, `(z⁴ − 1)/(z − 1) = 0`. Numerically the `4 × 4` Gram matrix is the identity.
- Kernels: `χ₁` and `χ₃` are faithful (`i` has order 4); `ker χ₂ = {0, 2}`; `ker χ₀ = ℤ₄`.

**The payoff.** The matrix `F_{kj} = χ_k(j)/√4 = i^{jk}/2` is unitary — the character table, normalized, *is* the 4-point quantum Fourier transform. This is the `N = 4` case of the general statement that for a finite abelian group the Fourier transform is the change of basis into the character basis, which is exactly what the QFT does in Shor's algorithm. The dual group `Ẑ₄ = {χ₀,χ₁,χ₂,χ₃}` is itself isomorphic to `ℤ₄` under pointwise multiplication (`χ_kχ_l = χ_{k+l}`).

</details>

- Compute the character table of S₃

<details><summary>Solution</summary>

**Conjugacy classes.** In `S_n` conjugacy classes are cycle types. For `S₃`, `|G| = 6` and there are three:

| class | elements | size |
|---|---|---|
| `e` | identity | 1 |
| transpositions | `(12), (13), (23)` | 3 |
| 3-cycles | `(123), (132)` | 2 |

Three classes `⟹` three irreps. `Σ dᵢ² = 6` with three positive integers forces `(d₁,d₂,d₃) = (1,1,2)`.

**The irreps.**
- **Trivial** `χ_triv(σ) = 1`.
- **Sign** `χ_sgn(σ) = sgn(σ)`: `+1` on `e` and the 3-cycles (even), `−1` on transpositions (odd).
- **Standard** (degree 2): take the permutation representation on `ℂ³`, `ρ(σ)eᵢ = e_{σ(i)}`, whose character is the number of fixed points, `χ_perm = (3, 1, 0)`. The line `span{e₁+e₂+e₃}` carries the trivial rep, and its complement `{x : x₁+x₂+x₃ = 0}` is the 2-dimensional standard rep with `χ_std = χ_perm − χ_triv = (2, 0, −1)`.

**Character table.**

| `S₃` | `e` (1) | transpositions (3) | 3-cycles (2) |
|---|---|---|---|
| `χ_triv` | 1 | 1 | 1 |
| `χ_sgn` | 1 | −1 | 1 |
| `χ_std` | 2 | 0 | −1 |

**Verification.** With `⟨χ, ψ⟩ = (1/|G|) Σ_classes |C| χ(C)* ψ(C)`:

```
⟨χ_std, χ_std⟩ = (1/6)(1·4 + 3·0 + 2·1) = 6/6 = 1   → irreducible ✓
⟨χ_triv, χ_sgn⟩ = (1/6)(1 − 3 + 2) = 0              ✓
⟨χ_triv, χ_std⟩ = (1/6)(2 + 0 − 2) = 0              ✓
⟨χ_sgn, χ_std⟩  = (1/6)(2 + 0 − 2) = 0              ✓
```

The full `3 × 3` Gram matrix computed in the venv is the identity. Column orthogonality also checks out: `Σᵢ |χᵢ(C)|² = |G|/|C|` gives `1+1+4 = 6 = 6/1` on `e`, `1+1+0 = 2 = 6/3` on transpositions, and `1+1+1 = 3 = 6/2` on 3-cycles ✓.

**Sanity check via the regular representation.** `χ_reg = (6,0,0)` and `⟨χᵢ, χ_reg⟩ = dᵢ`, so `ℂ[S₃] ≅ triv ⊕ sgn ⊕ 2·std` with dimension `1 + 1 + 4 = 6` ✓. `S₃ ≅ D₃` is the symmetry group of a triangle; `χ_std` is its geometric action on the plane.

</details>

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Abstract Algebra* — Dummit & Foote | Textbook | Comprehensive, rigorous |
| *Algebra* — Lang | Textbook | Graduate level, good for Lie theory |
| *Group Theory in Physics* — Cornwell | Textbook | Physics-oriented approach |
| Artin's *Algebra* | Textbook | Accessible, good on groups and reps |

---

## Progression Checkpoints

- [ ] Verify that specific gate sets form groups
- [ ] Derive quantum gates as matrix exponentials from generators
- [ ] Work with GF(2) and GF(4) arithmetic
- [ ] Understand the symplectic structure of the Pauli group
- [ ] State the Gottesman-Knill theorem and explain why Clifford gates are special
