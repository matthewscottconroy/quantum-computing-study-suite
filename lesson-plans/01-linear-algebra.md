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

<details><summary>Solution</summary>

The standard basis of `ℂ²` is `e₁ = (1, 0)ᵀ` and `e₂ = (0, 1)ᵀ`. Dirac notation simply renames them:

```
|0⟩ = (1, 0)ᵀ        |1⟩ = (0, 1)ᵀ
```

An arbitrary ket is then the column vector `|ψ⟩ = α|0⟩ + β|1⟩ = (α, β)ᵀ` with `α, β ∈ ℂ`, and the matching bra is the conjugate-transposed row vector `⟨ψ| = |ψ⟩† = (α*, β*)`, so `⟨0| = (1, 0)` and `⟨1| = (0, 1)`.

The labelling is not arbitrary: the computational basis is *defined* as the eigenbasis of the Pauli `Z` observable,

```
Z|0⟩ = +|0⟩        Z|1⟩ = −|1⟩
```

which is why "measuring in the computational basis" and "measuring `Z`" are the same instruction. The four outer products of these vectors,

`|0⟩⟨0| = [[1,0],[0,0]]`, `|0⟩⟨1| = [[0,1],[0,0]]`, `|1⟩⟨0| = [[0,0],[1,0]]`, `|1⟩⟨1| = [[0,0],[0,1]]`

are the matrix units, so every `2×2` operator — every single-qubit gate — has a Dirac-notation expression. For example `X = |0⟩⟨1| + |1⟩⟨0|`.

</details>

- Compute inner products and verify orthonormality of computational basis

<details><summary>Solution</summary>

The Hermitian inner product on `ℂ²` is `⟨φ|ψ⟩ = Σᵢ φᵢ* ψᵢ` — conjugate-linear in the bra slot, linear in the ket slot. On the computational basis:

```
⟨0|0⟩ = 1·1 + 0·0 = 1
⟨1|1⟩ = 0·0 + 1·1 = 1
⟨0|1⟩ = 1·0 + 0·1 = 0
⟨1|0⟩ = 0·1 + 1·0 = 0
```

i.e. `⟨i|j⟩ = δᵢⱼ`: the basis is orthonormal. Two consequences get used constantly.

**Completeness.** `|0⟩⟨0| + |1⟩⟨1| = [[1,0],[0,0]] + [[0,0],[0,1]] = I`. Inserting this resolution of the identity into `|ψ⟩` gives `|ψ⟩ = |0⟩⟨0|ψ⟩ + |1⟩⟨1|ψ⟩`, so the expansion coefficients are themselves inner products: `α = ⟨0|ψ⟩`, `β = ⟨1|ψ⟩`.

**General inner products.** For `|ψ⟩ = α|0⟩ + β|1⟩` and `|φ⟩ = γ|0⟩ + δ|1⟩`, sesquilinearity plus orthonormality give `⟨φ|ψ⟩ = γ*α + δ*β`. Hence `⟨ψ|ψ⟩ = |α|² + |β|² ≥ 0` (the normalization condition of the Born rule) and `⟨φ|ψ⟩ = ⟨ψ|φ⟩*`.

A second orthonormal basis, used just as often, is the `X` eigenbasis `|+⟩ = (|0⟩+|1⟩)/√2`, `|−⟩ = (|0⟩−|1⟩)/√2`: `⟨+|+⟩ = ½(1+1) = 1`, `⟨−|−⟩ = 1`, and `⟨+|−⟩ = ½(1−1) = 0` ✓.

</details>

- Construct a 2-qubit Hilbert space ℂ² ⊗ ℂ² and write all four basis states

<details><summary>Solution</summary>

`dim(ℂ² ⊗ ℂ²) = 2 × 2 = 4`, and a basis is obtained by tensoring the one-qubit bases. With the Kronecker rule `(a, b)ᵀ ⊗ (c, d)ᵀ = (ac, ad, bc, bd)ᵀ`:

```
|00⟩ = |0⟩⊗|0⟩ = (1, 0, 0, 0)ᵀ
|01⟩ = |0⟩⊗|1⟩ = (0, 1, 0, 0)ᵀ
|10⟩ = |1⟩⊗|0⟩ = (0, 0, 1, 0)ᵀ
|11⟩ = |1⟩⊗|1⟩ = (0, 0, 0, 1)ᵀ
```

The basis vector `|q₁q₀⟩` sits at index `2q₁ + q₀`, i.e. the computational basis is the binary counting order. (Qiskit prints basis states as `|q_{n−1}…q₁q₀⟩` with qubit 0 rightmost, which agrees with this ordering as long as the *first* tensor factor is taken to be the highest-numbered qubit.)

Orthonormality is inherited factor by factor: `⟨q₁q₀|p₁p₀⟩ = ⟨q₁|p₁⟩⟨q₀|p₀⟩ = δ_{q₁p₁} δ_{q₀p₀}`.

A general 2-qubit state is `|ψ⟩ = c₀₀|00⟩ + c₀₁|01⟩ + c₁₀|10⟩ + c₁₁|11⟩` with `Σ|c|² = 1`: four complex amplitudes, seven real parameters after normalization and global phase. Only a measure-zero subset of these factor as `|a⟩ ⊗ |b⟩` (which has 3 + 3 = 6 real parameters) — the excess is entanglement. Dimension grows as `2ⁿ`, which is why simulating `n` qubits classically costs exponential memory.

</details>

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

<details><summary>Solution</summary>

`A†` is the conjugate transpose: `(A†)ᵢⱼ = (Aⱼᵢ)*`. Transpose, then conjugate every entry.

```
A  = [[1,   2+i],        A† = [[1,    −3i],
      [3i,  4  ]]              [2−i,  4  ]]

S  = [[1, 0],            S† = [[1, 0 ],
      [0, i]]                  [0, −i]]

T  = [[1, 0      ],      T† = [[1, 0       ],
      [0, e^{iπ/4}]]           [0, e^{−iπ/4}]]
```

Numerically confirmed in the venv: `A†` comes out as `[[1−0j, 0−3j],[2−1j, 4−0j]]`, `S† = diag(1, −i)`, `T† = diag(1, 0.7071 − 0.7071i)`.

Three special cases worth memorising, because they are the whole point of the definition:

- `X† = X`, `Y† = Y`, `Z† = Z`, `H† = H` — Hermitian, so these are observables as well as gates.
- `S† = S³` and `T† = T⁷` — the phase gates are not Hermitian; `S† = S⁻¹` is the "Sdg" gate in Qiskit.
- For a scalar, `(λA)† = λ* A†`; for a ket, `(|ψ⟩)† = ⟨ψ|`. The dagger is exactly the map that turns kets into bras, which is why `⟨φ|ψ⟩ = (|φ⟩)†|ψ⟩`.

</details>

- Show that the adjoint of a composition is `(AB)† = B†A†`

<details><summary>Solution</summary>

Work entrywise. By definition `(M†)ᵢⱼ = (Mⱼᵢ)*`, so

```
((AB)†)ᵢⱼ = ((AB)ⱼᵢ)* = ( Σₖ Aⱼₖ Bₖᵢ )* = Σₖ (Bₖᵢ)* (Aⱼₖ)* = Σₖ (B†)ᵢₖ (A†)ₖⱼ = (B†A†)ᵢⱼ
```

The conjugation passes through the sum and product because it is a field automorphism of `ℂ`; the *order reversal* comes from the transpose, since `(AB)ᵀ = BᵀAᵀ`.

Basis-free version: the adjoint is the unique operator satisfying `⟨u|M|v⟩ = ⟨M†u|v⟩` for all `|u⟩, |v⟩`. Applying that definition twice, `⟨u|AB|v⟩ = ⟨A†u|B|v⟩ = ⟨B†A†u|v⟩`, so `B†A†` satisfies the defining property of `(AB)†`, and by uniqueness they are equal.

Concrete check with `A = [[1, 2+i],[3i, 4]]` and `B = [[0, i],[1, 0]]`:

```
AB       = [[2+i,  i],[4, −3]]
(AB)†    = [[2−i,  4],[−i, −3]]
B†A†     = [[0,1],[−i,0]] · [[1,−3i],[2−i,4]] = [[2−i, 4],[−i, −3]]   ✓
```

(verified numerically). The order matters: `A†B† = [[1,−3i],[2−i,4]]·[[0,1],[−i,0]] = [[−3, 1],[−4i, 2−i]] ≠ (AB)†`. Circuit reading: reversing a circuit means daggering each gate **and** running them backwards — `(U₃U₂U₁)† = U₁†U₂†U₃†`.

</details>

- Verify that applying a gate then its adjoint returns the identity

<details><summary>Solution</summary>

For a unitary `U` the defining property is `U†U = I`, so the circuit "`U` then `U†`" is the identity channel. Three checks of increasing generality.

**Concrete.** `T†T = diag(1, e^{−iπ/4}) diag(1, e^{iπ/4}) = diag(1, 1) = I` ✓. Likewise `H†H = H² = ½(X+Z)² = ½(X² + Z² + XZ + ZX) = ½(I + I + 0) = I`, using `XZ + ZX = 0`.

**All rotations at once.** Every single-qubit gate is `U = e^{−iθ n̂·σ/2} = cos(θ/2) I − i sin(θ/2) n̂·σ` with `n̂` a real unit vector (corpus convention, `R_x(θ) = e^{−iθX/2}`). Then `U† = cos(θ/2) I + i sin(θ/2) n̂·σ`, and since `(n̂·σ)² = (n_x² + n_y² + n_z²) I = I`,

```
U†U = cos²(θ/2) I + sin²(θ/2) (n̂·σ)² = (cos² + sin²) I = I
```

Equivalently `U† = U⁻¹ = e^{+iθ n̂·σ/2} = R_n̂(−θ)`: undoing a rotation means rotating back.

**General.** `U†U = I` already forces `UU† = I` for square matrices (a left inverse of a square matrix is a two-sided inverse), so the order of the pair does not matter.

Practical consequence: `qc.h(0); qc.h(0)` and `qc.t(0); qc.tdg(0)` both compile away to nothing, and "uncomputation" of an ancilla is exactly the application of the adjoint of the sub-circuit that computed it.

</details>

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

<details><summary>Solution</summary>

**Claim.** If `U†U = I` then `UU† = U†U`, i.e. `U` is normal.

**Proof.** `U†U = I` says `U†` is a left inverse of `U`. For square matrices a left inverse is a two-sided inverse: `U†U = I` makes `U` injective, hence (finite dimension, rank–nullity) bijective, hence invertible; multiplying `U†U = I` on the right by `U⁻¹` gives `U† = U⁻¹`, and therefore `UU† = UU⁻¹ = I = U†U`. ∎

So `UU† = U†U = I`, and normality holds with both products equal to the identity — the strongest possible form.

**Why this matters.** Normal is exactly the hypothesis of the spectral theorem: a matrix is unitarily diagonalizable iff it is normal. Hence every quantum gate has an orthonormal eigenbasis, `U = Σⱼ λⱼ|vⱼ⟩⟨vⱼ|`. Combining with unitarity, `1 = ⟨vⱼ|U†U|vⱼ⟩ = |λⱼ|²`, so all eigenvalues lie on the unit circle, `λⱼ = e^{iθⱼ}`. That is the statement that every gate is `e^{−iH}` for a Hermitian `H` (take `H = Σ (−θⱼ)|vⱼ⟩⟨vⱼ|`) — the bridge to Lie theory used in the abstract-algebra plan.

The converse fails: normality does not imply unitarity. `Z + I = diag(2, 0)` is Hermitian, hence normal, but not unitary. Hermitian and unitary are two different sub-classes of the normal matrices; their intersection is the set of Hermitian involutions such as `X`, `Y`, `Z`, `H`.

</details>

- Show that eigenvalues of Hermitian matrices are real

<details><summary>Solution</summary>

**Claim.** If `A = A†` and `A|v⟩ = λ|v⟩` with `|v⟩ ≠ 0`, then `λ ∈ ℝ`.

**Proof.** Take the inner product with `|v⟩`:

```
λ⟨v|v⟩ = ⟨v|A|v⟩
```

Now evaluate `⟨v|A|v⟩` a second way. Since `A = A†`, the number `⟨v|A|v⟩` is its own complex conjugate:

```
⟨v|A|v⟩* = ⟨v|A†|v⟩ = ⟨v|A|v⟩
```

(the first equality is the definition of the adjoint applied to a scalar, `⟨u|M|w⟩* = ⟨w|M†|u⟩`, with `u = w = v`). So `⟨v|A|v⟩` is real. Since `⟨v|v⟩ > 0` is real and positive, `λ = ⟨v|A|v⟩ / ⟨v|v⟩` is real. ∎

**Companion fact.** Eigenvectors for distinct eigenvalues are orthogonal: if `A|v⟩ = λ|v⟩` and `A|w⟩ = μ|w⟩` with `λ ≠ μ`, then `λ⟨w|v⟩ = ⟨w|A|v⟩ = (⟨v|A|w⟩)* = (μ⟨v|w⟩)* = μ⟨w|v⟩` (using `μ` real), so `(λ − μ)⟨w|v⟩ = 0` and `⟨w|v⟩ = 0`. Together with the spectral theorem this gives the orthonormal eigenbasis that Postulate 3 needs.

**Physical content.** Observables are Hermitian precisely so that measurement outcomes — the eigenvalues — are real numbers, and so that the outcomes come with an orthonormal set of distinguishable post-measurement states. `Tr(A) = Σλᵢ` and `det(A) = Πλᵢ` are then real too, which is why `⟨A⟩ = Tr(ρA)` is always a real expectation value.

</details>

- Verify that Pauli matrices X, Y, Z are both Hermitian and unitary

<details><summary>Solution</summary>

Write them out and dagger them:

```
X  = [[0, 1],[1, 0]]        X† = [[0, 1],[1, 0]]  = X    (real symmetric)
Y  = [[0, −i],[i, 0]]       Y† = [[0, −i],[i, 0]] = Y    (transpose swaps the entries, conjugation flips both signs back)
Z  = [[1, 0],[0, −1]]       Z† = [[1, 0],[0, −1]] = Z    (real diagonal)
```

so all three are Hermitian. For unitarity it is enough to square them:

```
X² = [[0,1],[1,0]]² = [[1,0],[0,1]] = I
Y² = [[0,−i],[i,0]]² = [[(−i)(i), 0],[0, (i)(−i)]] = I
Z² = diag(1, 1) = I
```

Combining, `P†P = P² = I` for `P ∈ {X, Y, Z}` — Hermitian *and* unitary, i.e. Hermitian involutions.

**Consequences that get used everywhere.**

- Eigenvalues must be real (Hermitian) and of modulus 1 (unitary), hence `±1`. Since `Tr(X) = Tr(Y) = Tr(Z) = 0`, each has exactly one `+1` and one `−1` eigenvalue.
- Each Pauli is its own inverse: `X² = I` means "apply `X` twice = do nothing", which is why a bit-flip error is corrected by re-applying `X`.
- `(n̂·σ)² = I` for any real unit vector `n̂` (cross terms cancel by anticommutativity), which is what collapses the exponential series into `e^{−iθ n̂·σ/2} = cos(θ/2) I − i sin(θ/2) n̂·σ`.
- `{I, X, Y, Z}` is an orthogonal basis of `2×2` matrices under `⟨A,B⟩ = ½Tr(A†B)`, so any single-qubit Hamiltonian or density matrix has a real Pauli expansion.

</details>

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

<details><summary>Solution</summary>

Each Pauli is Hermitian and squares to `I`, so before computing anything we know the spectrum is `{+1, −1}`, one of each (trace 0).

**`Z`** is already diagonal: `Z|0⟩ = +|0⟩`, `Z|1⟩ = −|1⟩`. Eigenvectors `|0⟩, |1⟩`.

**`X`**: `det(X − λI) = λ² − 1 = 0` gives `λ = ±1`. For `λ = +1`, `(v₂, v₁) = (v₁, v₂)` forces `v₁ = v₂`; normalizing,

```
|+⟩ = (|0⟩ + |1⟩)/√2
```

For `λ = −1`, `v₂ = −v₁`, giving `|−⟩ = (|0⟩ − |1⟩)/√2`.

**`Y`**: `det(Y − λI) = λ² − (−i)(i) = λ² − 1 = 0`, again `λ = ±1`. For `λ = +1`: `−i v₂ = v₁`, i.e. `v₂ = i v₁`, so

```
|+i⟩ = (|0⟩ + i|1⟩)/√2
```

Check: `Y(1, i)ᵀ/√2 = (−i·i, i·1)ᵀ/√2 = (1, i)ᵀ/√2` ✓. For `λ = −1`, `|−i⟩ = (|0⟩ − i|1⟩)/√2`.

**Summary and geometry.**

| operator | `+1` eigenvector | `−1` eigenvector | Bloch axis |
|---|---|---|---|
| `X` | `\|+⟩` | `\|−⟩` | `±x` |
| `Y` | `\|+i⟩` | `\|−i⟩` | `±y` |
| `Z` | `\|0⟩` | `\|1⟩` | `±z` |

These six states are the poles of the three Bloch axes, and each pair is an orthonormal basis of `ℂ²`. Their mutual overlaps are all `|⟨a|b⟩|² = ½` across different bases — the three bases are *mutually unbiased*, which is the property BB84 and state tomography both rely on. More generally `n̂·σ` has eigenvalues `±1` with eigenvectors the antipodal points `±n̂` of the Bloch sphere.

</details>

- Use spectral decomposition to compute `e^(iθZ)` — this is the Rz gate

<details><summary>Solution</summary>

`Z` is Hermitian with spectral decomposition `Z = (+1)|0⟩⟨0| + (−1)|1⟩⟨1|`, and the projectors are orthogonal and complete. For any function `f`, `f(Z) = f(+1)|0⟩⟨0| + f(−1)|1⟩⟨1|` — no series summation needed, because `|0⟩⟨0|` and `|1⟩⟨1|` are idempotent and annihilate each other. With `f(z) = e^{iθz}`:

```
e^{iθZ} = e^{iθ}|0⟩⟨0| + e^{−iθ}|1⟩⟨1| = [[e^{iθ}, 0],[0, e^{−iθ}]]
```

Equivalently, splitting the Taylor series by parity and using `Z² = I`,

`e^{iθZ} = (Σ_{k even} (iθ)^k/k!) I + (Σ_{k odd} (iθ)^k/k!) Z = cos θ · I + i sin θ · Z`

Both forms were checked numerically at `θ = 0.7` and agree with `scipy.linalg.expm(1j*0.7*Z)`.

**Relation to the corpus `Rz`.** This chapter's corpus fixes rotations as `R_z(θ) = e^{−iθZ/2} = diag(e^{−iθ/2}, e^{+iθ/2})` (matching `R_x(θ) = e^{−iθX/2}`). Comparing exponents:

```
e^{iθZ} = R_z(−2θ) = R_z(2θ)†
```

verified numerically. So `e^{iθZ}` *is* a `z`-rotation, but with the opposite sign convention and twice the angle — worth internalising, because the factor of 2 (half-angles in the gate, full angles on the Bloch sphere) and the sign are the two most common slips in this subject. Both differ from the hardware phase gate `P(θ) = diag(1, e^{iθ}) = e^{iθ/2} R_z(θ)` only by a global phase, which is unobservable; `S = P(π/2)`, `T = P(π/4)`.

**Bloch reading.** `e^{iθZ}` sends `|ψ⟩ = cos(ϑ/2)|0⟩ + e^{iφ}sin(ϑ/2)|1⟩` to a state with `φ → φ − 2θ`: a rotation of the Bloch sphere about the `z`-axis by `−2θ`. Eigenstates `|0⟩, |1⟩` only pick up phases, which is why `Z`-rotations are "free" in the computational basis and are implemented virtually (by frame changes) on superconducting hardware.

</details>

- Verify the spectral decomposition of the Hadamard gate

<details><summary>Solution</summary>

`H = (X + Z)/√2 = (1/√2)[[1, 1],[1, −1]]`. It is Hermitian, and

`H² = ½(X + Z)² = ½(X² + Z² + XZ + ZX) = ½(I + I + 0) = I`

since `XZ + ZX = 0`. So `H` is a Hermitian involution: eigenvalues `±1`, and `Tr(H) = 0` forces one of each.

**Eigenvectors.** Solve `(1/√2)(v₁ + v₂) = v₁` for the `+1` eigenvector: `v₂ = (√2 − 1)v₁`, so `|h₊⟩ ∝ (1 + √2, 1)` after clearing the surd (multiply by `1 + √2`). Normalizing,

```
|h₊⟩ = cos(π/8)|0⟩ + sin(π/8)|1⟩ ≈ 0.923880|0⟩ + 0.382683|1⟩
|h₋⟩ = −sin(π/8)|0⟩ + cos(π/8)|1⟩ ≈ −0.382683|0⟩ + 0.923880|1⟩
```

with the exact values `cos(π/8) = √(2+√2)/2` and `sin(π/8) = √(2−√2)/2` (both confirmed numerically to 16 digits). Direct substitution confirms `H|h₊⟩ = |h₊⟩` and `H|h₋⟩ = −|h₋⟩`.

**Decomposition.** `H = (+1)|h₊⟩⟨h₊| + (−1)|h₋⟩⟨h₋|`, i.e.

```
|h₊⟩⟨h₊| − |h₋⟩⟨h₋| = [[cos²(π/8) − sin²(π/8),  2 sin(π/8)cos(π/8)],
                       [2 sin(π/8)cos(π/8),    sin²(π/8) − cos²(π/8)]]
                     = [[cos(π/4), sin(π/4)],[sin(π/4), −cos(π/4)]] = (1/√2)[[1,1],[1,−1]] = H ✓
```

using the double-angle identities; verified numerically to machine precision.

**Geometry and payoff.** The `+1` eigenvector sits at polar angle `ϑ = π/4` on the Bloch sphere, i.e. along `n̂ = (1, 0, 1)/√2` — the diagonal of the `x–z` plane. `H` is the reflection through that axis (a `π` rotation about it, up to phase), which is exactly why `HXH = Z` and `HZH = X`. With the spectral form in hand, any function of `H` is free: `e^{−iαH} = e^{−iα}|h₊⟩⟨h₊| + e^{iα}|h₋⟩⟨h₋| = cos α · I − i sin α · H`, and `√H = |h₊⟩⟨h₊| + i|h₋⟩⟨h₋|`.

</details>

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

<details><summary>Solution</summary>

**`H ⊗ I`.** Each entry of `H` is replaced by that entry times the `2×2` block `I`:

```
H ⊗ I = (1/√2) [[1, 0,  1,  0],
                [0, 1,  0,  1],
                [1, 0, −1,  0],
                [0, 1,  0, −1]]
```

(verified numerically). This is "Hadamard on qubit 1, nothing on qubit 0", and its action on the basis is `|0q₀⟩ → (|0q₀⟩ + |1q₀⟩)/√2`, `|1q₀⟩ → (|0q₀⟩ − |1q₀⟩)/√2` — the second index never moves, which is the signature of a product operator.

**`CNOT`** (control = first/left factor) is *not* a tensor product of two single-qubit gates; it is a sum of two:

```
CNOT = |0⟩⟨0| ⊗ I + |1⟩⟨1| ⊗ X = [[1, 0, 0, 0],
                                  [0, 1, 0, 0],
                                  [0, 0, 0, 1],
                                  [0, 0, 1, 0]]
```

(verified). Reading the blocks: the top-left `2×2` block is `I` (control `|0⟩`: leave the target alone) and the bottom-right block is `X` (control `|1⟩`: flip it).

**Why the difference matters.** A product operator `A ⊗ B` maps product states to product states, `(A ⊗ B)(|a⟩⊗|b⟩) = A|a⟩ ⊗ B|b⟩`, so it can never create entanglement. `CNOT` is a *sum* of two product operators, and that is precisely what lets it entangle:

```
CNOT (H ⊗ I) |00⟩ = CNOT (|00⟩ + |10⟩)/√2 = (|00⟩ + |11⟩)/√2 = |Φ⁺⟩
```

(verified numerically: the output vector is `(0.7071, 0, 0, 0.7071)`). This two-gate circuit is the standard Bell-pair preparation.

A clean way to prove `CNOT ≠ A ⊗ B`: reshape a `4×4` operator into the `4×4` matrix of coefficients in the basis `{σ_a ⊗ σ_b}` and take its rank (the **operator Schmidt rank**). A product operator has rank 1. Expanding `CNOT = ½(I⊗I + I⊗X + Z⊗I − Z⊗X)`, the coefficient matrix has two non-zero rows (`I` and `Z`), so the operator Schmidt rank is 2 — `CNOT` genuinely does not factor. Product operators also satisfy `Tr(A ⊗ B) = Tr(A)Tr(B)`; for instance `Tr(H ⊗ I) = 0 · 2 = 0` ✓.

</details>

- Show that `|Φ⁺⟩ = (|00⟩ + |11⟩)/√2` is not separable

<details><summary>Solution</summary>

**Direct contradiction.** Suppose `|Φ⁺⟩ = (a|0⟩ + b|1⟩) ⊗ (c|0⟩ + d|1⟩)`. Expanding,

```
= ac|00⟩ + ad|01⟩ + bc|10⟩ + bd|11⟩
```

Matching coefficients with `|Φ⁺⟩` requires

```
ac = 1/√2,   ad = 0,   bc = 0,   bd = 1/√2
```

From `ad = 0`, either `a = 0` or `d = 0`. If `a = 0` then `ac = 0 ≠ 1/√2`; if `d = 0` then `bd = 0 ≠ 1/√2`. Both branches contradict, so no such factorization exists. ∎

**Determinant / rank criterion (the reusable version).** Arrange the amplitudes of `|ψ⟩ = Σ cᵢⱼ|ij⟩` into the matrix `C` with rows indexed by qubit A and columns by qubit B. Then `|ψ⟩` is separable **iff** `rank(C) = 1`, because `|ψ⟩ = |a⟩⊗|b⟩` is exactly the statement `cᵢⱼ = aᵢbⱼ`, i.e. `C = a bᵀ` is an outer product. For two qubits, rank 1 `⟺ det C = 0`. Here

```
C = (1/√2) [[1, 0],
            [0, 1]]        det C = 1/2 ≠ 0
```

so `rank(C) = 2` and `|Φ⁺⟩` is entangled. The same test instantly classifies any two-qubit state — e.g. `(|00⟩ − |01⟩ + |10⟩ − |11⟩)/2` has `C = ½[[1,−1],[1,−1]]` with `det = 0`, hence separable (`= |+⟩⊗|−⟩`).

**Third view.** The singular values of `C` are the Schmidt coefficients; here `CC† = I/2`, so both equal `1/√2`. Schmidt rank 2 (> 1) means entangled, and *equal* coefficients means maximally entangled — the next exercise makes this concrete via the reduced state.

</details>

- Use partial trace to find the reduced state of each qubit in `|Φ⁺⟩`

<details><summary>Solution</summary>

Start from the full density matrix:

```
ρ_AB = |Φ⁺⟩⟨Φ⁺| = ½( |00⟩⟨00| + |00⟩⟨11| + |11⟩⟨00| + |11⟩⟨11| )
```

The partial trace over B is `ρ_A = Σⱼ (I_A ⊗ ⟨j|_B) ρ_AB (I_A ⊗ |j⟩_B)`, which on product terms acts as `Tr_B(|a⟩⟨a'| ⊗ |b⟩⟨b'|) = |a⟩⟨a'| · ⟨b'|b⟩`. Term by term:

```
Tr_B |00⟩⟨00| = |0⟩⟨0| · ⟨0|0⟩ = |0⟩⟨0|
Tr_B |00⟩⟨11| = |0⟩⟨1| · ⟨1|0⟩ = 0        ← the coherences die
Tr_B |11⟩⟨00| = |1⟩⟨0| · ⟨0|1⟩ = 0
Tr_B |11⟩⟨11| = |1⟩⟨1| · ⟨1|1⟩ = |1⟩⟨1|
```

Hence

```
ρ_A = ½(|0⟩⟨0| + |1⟩⟨1|) = I/2
```

and by the symmetry of `|Φ⁺⟩` under swapping the qubits, `ρ_B = I/2` as well. Both were confirmed numerically by contracting the reshaped density matrix (`einsum('ikjk->ij', ρ)` and `einsum('kikj->ij', ρ)`), each returning `[[0.5, 0],[0, 0.5]]`.

**What this says.** `Tr(ρ_A²) = ½`, the minimum for a qubit, so each half of a Bell pair is *maximally mixed*: every local measurement on qubit A alone gives 50/50 in every basis, and the local state carries no information whatsoever. All of the state's content lives in the correlations. The entanglement entropy `S(ρ_A) = −Tr(ρ_A log₂ ρ_A) = 1` bit is maximal, which is the formal definition of a maximally entangled two-qubit state.

**Contrast.** For the product state `|0⟩⊗|+⟩`, the same computation gives `ρ_A = |0⟩⟨0|` — pure, `Tr(ρ_A²) = 1`, `S = 0`. The purity of the reduced state is therefore a complete separability test for bipartite *pure* states: `ρ_A` pure `⟺` the global state is a product.

</details>

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

<details><summary>Solution</summary>

**Pure state `|+⟩`.** `ρ₊ = |+⟩⟨+|` with `|+⟩ = (1,1)ᵀ/√2`:

```
ρ₊ = ½ [[1, 1],
        [1, 1]]
```

Checks: Hermitian ✓; `Tr ρ₊ = ½ + ½ = 1` ✓; eigenvalues `1` and `0` (the matrix is `2 × (½)` times a rank-1 projector), so positive semi-definite ✓; `Tr(ρ₊²) = 1` (verified numerically) so it is pure ✓. Bloch vector `r = (Tr(ρX), Tr(ρY), Tr(ρZ)) = (1, 0, 0)` — the `+x` pole, on the surface of the ball.

**Maximally mixed state.**

```
I/2 = [[½, 0],
       [0, ½]]
```

Checks: Hermitian ✓; trace 1 ✓; eigenvalues `½, ½` ✓; `Tr((I/2)²) = ½` (verified) — the minimum possible purity for a qubit, hence "maximally mixed". Bloch vector `r = 0`, the centre of the ball, because every Pauli is traceless.

**The lesson about ensembles.** The same `I/2` arises from physically different preparations:

```
I/2 = ½|0⟩⟨0| + ½|1⟩⟨1| = ½|+⟩⟨+| + ½|−⟩⟨−| = ½|+i⟩⟨+i| + ½|−i⟩⟨−i|
```

(each pair sums to `(I + r·σ)/2 + (I − r·σ)/2 = I`). No measurement can distinguish these ensembles: the density matrix, not the ensemble, is the complete physical description. This is exactly why `ρ` — rather than a list of states and probabilities — is the right object, and it is the reason the no-signalling theorem holds for entangled pairs.

General parametrization: every qubit state is `ρ = (I + r·σ)/2` with `|r| ≤ 1`, pure iff `|r| = 1`. `ρ₊` has `|r| = 1`, `I/2` has `|r| = 0`.

</details>

- Show that `Tr(ρ²) ≤ 1` with equality iff `ρ` is pure

<details><summary>Solution</summary>

`ρ` is Hermitian and positive semi-definite with unit trace, so the spectral theorem gives `ρ = Σᵢ λᵢ|i⟩⟨i|` with an orthonormal `{|i⟩}`, `λᵢ ≥ 0`, and `Σᵢ λᵢ = 1`. Then `ρ² = Σᵢ λᵢ²|i⟩⟨i|` and

```
Tr(ρ²) = Σᵢ λᵢ²
```

Because each `λᵢ` lies in `[0, 1]` (it is non-negative and no single eigenvalue can exceed the total trace 1), we have `λᵢ² ≤ λᵢ`, so

```
Tr(ρ²) = Σᵢ λᵢ² ≤ Σᵢ λᵢ = 1
```

**Equality.** `Σλᵢ² = Σλᵢ` forces `λᵢ² = λᵢ` for every `i`, i.e. `λᵢ ∈ {0, 1}`. Combined with `Σλᵢ = 1`, exactly one eigenvalue equals 1 and the rest vanish, so `ρ = |ψ⟩⟨ψ|` for the corresponding eigenvector — a pure state. Conversely if `ρ = |ψ⟩⟨ψ|` then `ρ² = ρ` and `Tr(ρ²) = Tr(ρ) = 1`. ∎

**Lower bound.** By Cauchy–Schwarz on the `d` eigenvalues, `1 = (Σλᵢ)² ≤ d Σλᵢ²`, so `Tr(ρ²) ≥ 1/d`, with equality iff all `λᵢ = 1/d`, i.e. `ρ = I/d`. Purity therefore ranges over `[1/d, 1]`, from maximally mixed to pure.

**Qubit form.** With `ρ = (I + r·σ)/2` and `Tr(σⱼσₖ) = 2δⱼₖ`,

```
Tr(ρ²) = ¼ Tr(I + 2 r·σ + (r·σ)²) = ¼(2 + 0 + 2|r|²) = (1 + |r|²)/2
```

so purity `1` ⟺ `|r| = 1` (surface) and purity `½` ⟺ `r = 0` (centre). Numerical check with `r = (0.4, 0.2, 0.4)`: `(1 + 0.36)/2 = 0.68`, and computing `Tr(ρ²)` directly from the matrix gives `0.68` ✓. Purity is the cheapest experimental witness of decoherence: any noise process that shrinks `|r|` shows up immediately as `Tr(ρ²) < 1`.

</details>

- Compute measurement probabilities in the Z basis for a given `ρ`

<details><summary>Solution</summary>

Take the concrete mixed state

```
ρ = [[0.7,       0.2 − 0.1i],
     [0.2 + 0.1i, 0.3      ]]
```

**First check it is a state.** Hermitian ✓; `Tr ρ = 0.7 + 0.3 = 1` ✓; `det ρ = 0.21 − |0.2 + 0.1i|² = 0.21 − 0.05 = 0.16 > 0`, so with positive trace both eigenvalues are positive — numerically they are `0.8` and `0.2` ✓. Its Bloch vector is `r = (2Re ρ₀₁, −2Im ρ₀₁, ρ₀₀ − ρ₁₁) = (0.4, 0.2, 0.4)` with `|r| = 0.6 < 1`, so it is a legitimate mixed state (purity `(1 + 0.36)/2 = 0.68`, confirmed numerically).

**Z-basis probabilities.** With `Π₀ = |0⟩⟨0|` and `Π₁ = |1⟩⟨1|`,

```
p(0) = Tr(Π₀ ρ) = ρ₀₀ = 0.7
p(1) = Tr(Π₁ ρ) = ρ₁₁ = 0.3
```

Sum `= 1` ✓. In the computational basis the rule is simply "read the diagonal".

**Post-measurement states.**

```
ρ|₀ = Π₀ ρ Π₀ / p(0) = (0.7 |0⟩⟨0|)/0.7 = |0⟩⟨0|
ρ|₁ = Π₁ ρ Π₁ / p(1) = |1⟩⟨1|
```

(verified numerically). If the outcome is discarded — a *non-selective* measurement — the state becomes `Σᵢ Πᵢ ρ Πᵢ = diag(0.7, 0.3)`: the diagonal survives and the off-diagonal coherences are erased. That map is exactly the completely dephasing channel of Module 6 of the quantum-mechanics plan, `r → (0, 0, r_z)`.

**What the coherences do.** They are invisible to a `Z` measurement but control the other axes:

```
⟨Z⟩ = p(0) − p(1) = 0.4
⟨X⟩ = Tr(ρX) = 2 Re(ρ₀₁) = 0.4
⟨Y⟩ = Tr(ρY) = −2 Im(ρ₀₁) = 0.2
```

(all three confirmed numerically). So a full state tomography needs measurements in all three bases; the `Z` histogram alone determines only one of the three Bloch components.

</details>

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
