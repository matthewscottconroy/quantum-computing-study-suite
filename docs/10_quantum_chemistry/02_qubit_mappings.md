# Fermion-to-Qubit Mappings and Qubit Tapering

> **Prerequisites**: Second quantization (10/01), Pauli group and the symplectic form (01/04),
> stabilizer formalism (05/04), Jordan-Wigner basics (06/01, 08/03)
> **Connects to**: Active spaces and ansätze (10/03), beyond VQE (10/04),
> ansatz design (06/02)

---

## Overview

Chapter 10/01 ended with a Hamiltonian written in fermionic operators. Qubits do not obey those
relations — Paulis on *different* qubits commute, while fermionic operators on different orbitals
anticommute. Bridging that gap is the job of a **fermion-to-qubit mapping**, and the choice is not
cosmetic: it fixes the qubit count, the number of Pauli terms, the weight of each term, and
therefore the depth of every Trotter step, ansatz layer and measurement circuit.

Chapter 06/01 introduced Jordan-Wigner and Bravyi-Kitaev in a paragraph each and asserted that
symmetry lets two qubits be "tapered off" from H₂. This chapter earns those statements. All three
standard encodings turn out to be the *same* construction with a different invertible binary
matrix, and the differences in Pauli weight follow from the sparsity of that matrix and its
inverse. Qubit tapering is then developed as a general stabilizer computation — find the `Z₂`
symmetries in the binary symplectic kernel, rotate each to a single-qubit `Z` with a Clifford,
delete that qubit — and run end-to-end on H₂ until Chapter 06/01's two-qubit Hamiltonian falls out
with all five coefficients matching.

---

## Encodings as Binary Matrices

Every standard encoding stores, on qubit `j`, some fixed parity of occupation numbers:

```
q_j = ⊕_k β_{jk} n_k   (mod 2),   β ∈ GF(2)^{N×N} invertible
```

Different `β` give different encodings:

| encoding | `β` | qubit `j` stores |
|---|---|---|
| Jordan-Wigner | identity | `n_j` (occupation) |
| parity | lower-triangular all-ones | `n₀ ⊕ … ⊕ n_j` (parity of the first `j+1`) |
| Bravyi-Kitaev | binary-tree matrix | a partial sum over a sub-tree |

Since `β` is invertible over `GF(2)` the map is a permutation of computational basis states, so
every encoding represents the *same* operator exactly — identical spectra, different Pauli
supports. Three index sets control the cost of `a_j`:

- **update set** `U(j) = {i ≠ j : β_{ij} = 1}` — qubits that flip when `n_j` flips; they carry `X`.
- **flip set** `F(j) = {k ≠ j : (β⁻¹)_{jk} = 1}` — qubits needed to read `n_j`; they carry `Z`.
- **parity set** `P(j)` — qubits encoding `Σ_{k<j} n_k`, the Jordan-Wigner phase; also `Z`.

The Pauli weight of `a_j` is `1 + |U(j)| + |F(j) ∪ P(j)|` up to overlaps, so a good encoding makes
`β` **and** `β⁻¹` sparse at once. Jordan-Wigner makes `β⁻¹` maximally sparse but pays in `P(j)`;
parity does the reverse; Bravyi-Kitaev balances them.

---

## Jordan-Wigner in Full

With `β = I`, qubit `j` holds `n_j` directly. Writing `σ^± = (X ∓ iY)/2` so that
`σ⁻|1⟩ = |0⟩`, the mapping is

```
a_j  = (Z₀ Z₁ … Z_{j-1}) ⊗ (X_j + i Y_j)/2
a_j† = (Z₀ Z₁ … Z_{j-1}) ⊗ (X_j - i Y_j)/2
n̂_j  = a_j† a_j = (I - Z_j)/2
```

The `Z` string is the operator form of the `(-1)^{Σ_{k<j} n_k}` sign of Chapter 10/01, and it is
what makes the images anticommute: for `p < q`, the image of `a_q` carries `Z_p` exactly where the
image of `a_p` carries `X_p` or `Y_p`, and `{Z, X} = {Z, Y} = 0` supplies the single minus sign.

### What the Hamiltonian becomes

Two structures dominate. **Number-conserving diagonal terms** are cheap, because the strings
cancel: `n̂_p = (I - Z_p)/2` and `n̂_p n̂_q = (I - Z_p - Z_q + Z_p Z_q)/4`. **Hopping terms** keep a
string between the two sites:

```
a_p† a_q + a_q† a_p = (X_p Z_{p+1} … Z_{q-1} X_q + Y_p Z_{p+1} … Z_{q-1} Y_q)/2   (p < q)
```

so a hop between orbitals `p` and `q` costs Pauli weight `q - p + 1`, and double excitations give
eight strings of weight up to `|p-q| + |r-s| + 2`. Only off-diagonal terms carry strings, so a
Jordan-Wigner molecular Hamiltonian has `O(N⁴)` terms of *average* weight `O(N)` with a large
low-weight majority. Jordan-Wigner is therefore the right default for small systems and for
diagonal-dominated algorithms; its weakness is geometric, since on a 2D lattice spatial neighbours
can be `O(L)` apart in any linear orbital ordering — the reason 2D Hubbard simulations
(Chapter 08/03) suffer under it.

---

## Parity Encoding

Take `β` lower-triangular with all ones, so `q_j = n₀ ⊕ … ⊕ n_j`. The Jordan-Wigner string is now
free — the parity already sits on qubit `j-1` — but reading `n_j = q_j ⊕ q_{j-1}` needs two qubits,
and *updating* `n_j` must flip every qubit above `j`:

```
a_j = ( Z_{j-1} X_j X_{j+1} … X_{N-1}  +  i Y_j X_{j+1} … X_{N-1} ) / 2
```

The `X` tail replaces the `Z` string one for one, so parity buys nothing in weight. Its value is
specific: **the parity encoding puts conserved parities on named qubits.** With blocked orbital
ordering (all α spin orbitals, then all β), qubit `M-1` stores the α electron parity and qubit
`2M-1` the total parity. Both are conserved, so both qubits decouple and can be removed by hand —
the "two-qubit reduction" behind Chapter 06/01's H₂ Hamiltonian. Occupations also stay cheap here:
`n̂_j = (I - Z_{j-1} Z_j)/2`.

---

## Bravyi-Kitaev

Bravyi-Kitaev interpolates with a binary-tree `β`, defined recursively for `N` a power of two:

```
β₁ = [1],   β_{2n} = [ β_n   0  ]     with A the n×n matrix whose last row is all ones
                     [  A   β_n ]     and whose other entries are zero
```

For `N = 4`:

```
       n₀ n₁ n₂ n₃
q₀  =   1  0  0  0        q₀ = n₀
q₁  =   1  1  0  0        q₁ = n₀ ⊕ n₁
q₂  =   0  0  1  0        q₂ = n₂
q₃  =   1  1  1  1        q₃ = n₀ ⊕ n₁ ⊕ n₂ ⊕ n₃
```

Even-indexed qubits store occupations (empty flip set); odd-indexed qubits store partial sums over
a sub-tree. Both `β` and `β⁻¹` have `O(log N)` ones per row, so `U(j)`, `F(j)` and `P(j)` all have
size `O(log N)` and `weight(a_j) = O(log N)`. For H₂'s four spin orbitals:

```
a₀ = (X₀X₁I₂X₃ + i Y₀X₁I₂X₃)/2
a₁ = (Z₀X₁I₂X₃ + i I₀Y₁I₂X₃)/2
a₂ = (I₀Z₁X₂X₃ + i I₀Z₁Y₂X₃)/2
a₃ = (I₀Z₁Z₂X₃ + i I₀I₁I₂Y₃)/2
```

---

## The Locality / Weight Trade-off

Computing the Pauli images of every `a_j` and recording the maximum and mean weight gives the
following (verified numerically, all terms of every `a_j` counted):

| `N` spin orbitals | Jordan-Wigner | parity | Bravyi-Kitaev |
|---|---|---|---|
| 4 (max / mean) | 4 / 2.50 | 4 / 2.88 | **3** / 2.62 |
| 8 (max / mean) | 8 / 4.50 | 8 / 4.94 | **4** / 3.56 |

Jordan-Wigner and parity are mirror images — JW cheap at low `j`, parity at high `j`, with nearly
equal means. Bravyi-Kitaev is the only one whose maximum grows like `log N` rather than `N`.

Three caveats worth stating plainly. For `N ≲ 12` the constants dominate and Bravyi-Kitaev's
advantage is small (3 versus 4 at `N = 4`). Jordan-Wigner strings are cheap on all-to-all hardware
with long-range gates (trapped ions, Chapter 07/02) and expensive on a fixed-degree superconducting
lattice (Chapter 07/01). And Jordan-Wigner's `Z` strings commute with the measurement basis, so
many terms group for simultaneous measurement, while Bravyi-Kitaev's mixed strings group less
neatly — a per-term weight advantage can be spent again on extra measurement circuits.

---

## `Z₂` Symmetries and Qubit Tapering

### The construction

Let `H = Σ_i c_i P_i` be the qubit Hamiltonian. Write each Pauli `P` as a binary symplectic vector
`(x | z) ∈ GF(2)^{2n}`, with `x_j = 1` for `X` or `Y` on qubit `j` and `z_j = 1` for `Z` or `Y`.
Two Paulis commute exactly when their symplectic product vanishes:

```
⟨(x|z), (x'|z')⟩ = x · z' + z · x'  =  0   (mod 2)
```

The Paulis commuting with *every* term of `H` are therefore the `GF(2)` kernel of the matrix whose
rows are `(z_i | x_i)`; a basis `{τ₁, …, τ_k}` of that kernel generates an abelian group of `Z₂`
symmetries with `τ_m² = I`. For each generator pick a distinct qubit `q_m` on which `τ_m` acts
non-trivially but no other generator does, and build a Clifford `U` with

```
U τ_m U† = Z_{q_m}   for every m
```

(For all-`Z` generators a CNOT network suffices; in general the Bravyi-Gambetta-Mezzacapo-Temme
construction uses `U_m = (X_{q_m} + τ_m)/√2`.) After the rotation, `U H U†` contains only `I` or
`Z` on every `q_m`. Replacing each `Z_{q_m}` by an eigenvalue `±1` removes that qubit:

```
n qubits, k independent Z₂ symmetries  →  n - k qubits, 2^k sectors
```

The physics is in the sector choice: each `±1` labels a symmetry sector (`N_α` parity, `N_β`
parity, a point-group irrep), and the wrong choice gives a perfectly valid ground energy of the
*wrong* state. The safe recipe is `⟨Φ_HF|τ_m|Φ_HF⟩`, which is exactly `±1` on a determinant.

At least two `Z₂` symmetries are guaranteed for any molecular Hamiltonian — the parities of `N_α`
and `N_β`, from `[H, N̂_α] = [H, N̂_β] = 0`, which under blocked Jordan-Wigner read
`Z₀Z₁…Z_{M-1}` and `Z_M…Z_{2M-1}`. Point-group symmetry supplies more: for H₂ the `g/u` parity of
`D_∞h` gives a third.

---

## Key Formulas

- **Encoding matrix**: `q = β n (mod 2)`, `β` invertible over `GF(2)`
- **Jordan-Wigner**: `a_j = (⊗_{k<j} Z_k)(X_j + iY_j)/2`, `n̂_j = (I - Z_j)/2`
- **JW hopping**: `a_p†a_q + h.c. = (X_p Z⋯Z X_q + Y_p Z⋯Z Y_q)/2`, weight `q - p + 1`
- **Weight scaling**: JW and parity `O(N)`; Bravyi-Kitaev `O(log N)`
- **Commutation test**: `⟨(x|z),(x'|z')⟩ = x·z' + z·x' mod 2`
- **Tapering**: `k` independent `Z₂` symmetries remove `k` qubits and split `H` into `2^k` sectors

---

## Worked Example: H₂ from Four Qubits to Two (and One)

**Start.** The H₂/STO-3G integrals of Chapter 10/01, Jordan-Wigner mapped with blocked ordering
`0 = σ_g α`, `1 = σ_u α`, `2 = σ_g β`, `3 = σ_u β`, give a 15-term electronic Hamiltonian
(hartree; subscripts are spin-orbital indices):

```
H = -0.810548 I
  + 0.172184 (Z₀ + Z₂)  - 0.225753 (Z₁ + Z₃)
  + 0.120913 (Z₀Z₁ + Z₂Z₃) + 0.168928 Z₀Z₂ + 0.174643 Z₁Z₃
  + 0.166145 (Z₀Z₃ + Z₁Z₂)
  + 0.045233 (X₀X₁X₂X₃ + X₀X₁Y₂Y₃ + Y₀Y₁X₂X₃ + Y₀Y₁Y₂Y₃)
```

The degeneracies are the symmetry at work: `Z₀` and `Z₂` share a coefficient because `σ_g α` and
`σ_g β` are the same spatial orbital, and `0.045233 = 0.180931/4` is the `(gu|gu)` integral over
four. Adding `E_nuc = 0.719969` and diagonalizing gives `-1.137306` Ha — the `2 × 2` CI answer of
Chapter 10/01, as it must be.

**Finding the symmetries.** Build the symplectic matrix of the 15 terms and take its `GF(2)`
kernel:

```python
import numpy as np
from qiskit.quantum_info import SparsePauliOp

terms = {"IIII": -0.81054799, "ZIII": +0.17218394, "IZII": -0.22575348,
         "IIZI": +0.17218394, "IIIZ": -0.22575348, "ZZII": +0.12091263,
         "ZIZI": +0.16892754, "ZIIZ": +0.16614543, "IZZI": +0.16614543,
         "IZIZ": +0.17464342, "IIZZ": +0.12091263, "XXXX": +0.04523280,
         "XXYY": +0.04523280, "YYXX": +0.04523280, "YYYY": +0.04523280}
H = SparsePauliOp([k[::-1] for k in terms], coeffs=list(terms.values()))  # to Qiskit order
print("E_total(FCI) =", round(np.linalg.eigvalsh(H.to_matrix()).real.min() + 0.71996899, 8))

# a Pauli (x|z) commutes with every term iff A @ (x|z) = 0 over GF(2)
N = 4
A = np.hstack([H.paulis.z.astype(int)[:, ::-1], H.paulis.x.astype(int)[:, ::-1]]) % 2
R, piv = A.copy(), []                                    # Gaussian elimination mod 2
for c in range(2 * N):
    q = next((i for i in range(len(piv), len(R)) if R[i, c]), None)
    if q is None: continue
    R[[len(piv), q]] = R[[q, len(piv)]]
    for i in range(len(R)):
        if i != len(piv) and R[i, c]: R[i] = (R[i] + R[len(piv)]) % 2
    piv.append(c)
sym = {(0, 0): "I", (1, 0): "X", (0, 1): "Z", (1, 1): "Y"}
for f in (c for c in range(2 * N) if c not in piv):
    v = np.zeros(2 * N, int); v[f] = 1
    for i, c in enumerate(piv): v[c] = R[i, f]
    print("Z2 generator:", "".join(sym[(v[j], v[N + j])] for j in range(N)))
```

Output (Qiskit 2.5.2):

```
E_total(FCI) = -1.13730604
Z2 generator: ZZII
Z2 generator: ZIZI
Z2 generator: ZIIZ
```

Three generators — `Z₀Z₁` (α parity), `Z₀Z₂`, `Z₀Z₃` — whose products include `Z₂Z₃` (β parity)
and `Z₀Z₁Z₂Z₃` (total parity). The group is the two guaranteed particle-number symmetries plus one
extra from the `g/u` parity of `D_∞h`.

**Two qubits, by parity encoding.** Re-encoding in the parity basis puts the α parity on qubit 1
and the total parity on qubit 3, and both then appear only as `I` or `Z`. `|HF⟩` has one α electron
and two electrons in total, so the sector is `Z₁ = -1`, `Z₃ = +1`; substituting and dropping those
qubits leaves

```
H₂q = -1.052373 I + 0.397937 Z₀ - 0.397937 Z₁ - 0.011280 Z₀Z₁ + 0.180931 X₀X₁
```

which is the Hamiltonian of Chapter 06/01, coefficient for coefficient. Its spectrum is
`{-1.857275, -1.244585, -0.882722, -0.224911}` Ha electronic, ground total `-1.137306` Ha, and
`⟨10|H₂q|10⟩ = -1.836968` Ha reproduces Hartree-Fock.

**One qubit, using all three symmetries.** The generators are all `Z`-type, so
`U = CNOT_{0→1} CNOT_{0→2} CNOT_{0→3}` sends `Z₀Z₁ → Z₁`, `Z₀Z₂ → Z₂`, `Z₀Z₃ → Z₃`. Evaluated on
`|HF⟩ = |1010⟩` the generators give the sector `(Z₁, Z₂, Z₃) = (-1, +1, -1)`, and tapering all
three leaves

```
H₁q = -1.041093 I + 0.795875 Z + 0.180931 X
```

Its eigenvalues are `-1.041093 ± √(0.795875² + 0.180931²) = -1.041093 ± 0.816182`, i.e.
`{-1.857275, -0.224911}` Ha — the exact FCI answer on one qubit. Substituting a Bloch vector
`(sin θ, 0, cos θ)` reproduces, term for term, the energy function
`E(θ) = -1.041093 + 0.795875 cos θ + 0.180931 sin θ` that Chapter 06/01 minimizes by hand: that
worked example is secretly a tapered one-qubit Hamiltonian.

---

## Summary

- All standard fermion-to-qubit encodings are one construction, `q = β n (mod 2)` with invertible
  binary `β`; they give identical spectra and differ only in Pauli support.
- Jordan-Wigner (`β = I`) has `n̂_j = (I - Z_j)/2` and pays an `O(N)` `Z` string on every hopping
  term. Parity is its mirror, with an `O(N)` `X` tail, but places conserved parities on named
  qubits.
- Bravyi-Kitaev's binary-tree `β` keeps `β` and `β⁻¹` both `O(log N)`-sparse, giving `O(log N)`
  weights: measured maxima are 3 versus 4 at `N = 4`, and 4 versus 8 at `N = 8`.
- `Z₂` symmetries are the `GF(2)` symplectic kernel of the Hamiltonian's Pauli strings; `k`
  independent generators remove `k` qubits at the price of choosing among `2^k` sectors, which the
  Hartree-Fock expectation values fix.
- H₂/STO-3G: 4 qubits → 2 qubits by particle-number symmetry (recovering Chapter 06/01's
  Hamiltonian exactly) → 1 qubit using the extra `g/u` symmetry, still exact at `-1.137306` Ha.

---

## Exercises

**Exercise 1**: Under Jordan-Wigner, write out `a₂† a₅ + a₅† a₂` as Pauli strings and give its
weight. Then write `a₂† a₃ + a₃† a₂`. What does the comparison say about orbital ordering?

<details><summary>Solution</summary>

```
a₂†a₅ + a₅†a₂ = (X₂ Z₃ Z₄ X₅ + Y₂ Z₃ Z₄ Y₅)/2      weight 4
a₂†a₃ + a₃†a₂ = (X₂ X₃ + Y₂ Y₃)/2                   weight 2
```

Adjacent hops are weight 2 regardless of `N`; distant hops cost `q - p + 1`. Orbital ordering is a
free design choice, so placing strongly coupled orbitals adjacently directly buys circuit depth —
and the same reasoning is why Jordan-Wigner hurts on 2D lattices, where no linear order keeps all
lattice neighbours adjacent.

</details>

**Exercise 2**: A Hamiltonian on `n = 12` qubits has 6 independent `Z₂` symmetries. How many
qubits remain after tapering, how many sectors are there, and how would you find the right one
without diagonalizing all of them?

<details><summary>Solution</summary>

`12 - 6 = 6` qubits remain, split across `2⁶ = 64` sectors. Diagonalizing all 64 would defeat the
purpose.

Evaluate each generator on a reference determinant of the target state. Each `τ_m` is a Pauli
string, so `⟨Φ|τ_m|Φ⟩ = ±1` exactly on a computational-basis state, and the 6 signs pick the sector
in one pass. The reference need not be accurate, only in the right symmetry sector: right electron
count, right `S_z`, right spatial irrep.

</details>

**Exercise 3**: Under the parity encoding, `n̂_j = (I - Z_{j-1} Z_j)/2` for `j > 0`. Verify this
from `q_j = n₀ ⊕ … ⊕ n_j`, and explain why a *diagonal* Coulomb term `n̂_p n̂_q` still has weight
at most 4 in this encoding.

<details><summary>Solution</summary>

`q_{j-1} ⊕ q_j = n_j`, so the eigenvalue of `Z_{j-1}Z_j` is `(-1)^{q_{j-1}+q_j} = (-1)^{n_j}`,
giving `n̂_j = (I - Z_{j-1}Z_j)/2`. (For `j = 0`, `n̂_0 = (I - Z_0)/2`.)

`n̂_p n̂_q` expands into products of `I`, `Z_{p-1}Z_p` and `Z_{q-1}Z_q`, whose supports are at most
four distinct qubits, so weight `≤ 4` — independent of `|p - q|`. Diagonal terms are cheap in every
encoding; it is only the off-diagonal hopping and exchange terms that pay for non-locality. Since a
molecular Hamiltonian's `O(N⁴)` terms include `O(N²)` diagonal ones, the weight statistics are
always dominated by the excitation terms.

</details>

**Exercise 4**: Chapter 06/01 states that H₂ needs "4 spin-orbitals → 4 qubits → taper 2 →
2 qubits". This chapter reaches one qubit. Why is the two-qubit form still the right one to quote,
and when does the extra reduction stop being available?

<details><summary>Solution</summary>

The third symmetry is the `g/u` inversion parity of `D_∞h`. It is a property of this molecule at
this geometry, not of electronic structure in general: it disappears for any molecule without a
centre of inversion (HeH⁺, H₂O, essentially every interesting catalyst), and it disappears even for
H₂ if the two basis functions differ. Only the `N_α` and `N_β` parities are universal, so
"`2M` qubits minus 2" is the generic statement and the two-qubit H₂ Hamiltonian is the honest
benchmark.

There is a second reason: tapering ties the sector choice to the ansatz. The one-qubit Hamiltonian
can only describe the totally symmetric singlet, so excited states of other irreps are gone —
aggressive tapering trades away exactly the flexibility open-shell and excited-state calculations
need.

</details>

---

## Further Reading

1. **Jordan, P. and Wigner, E.** — "Über das Paulische Äquivalenzverbot," *Z. Phys.* 47, 631
   (1928). The original transformation.
2. **Bravyi, S. B. and Kitaev, A. Yu.** — "Fermionic quantum computation," *Ann. Phys.* 298, 210
   (2002). Section 4 introduces the binary-tree encoding and the `O(log N)` weight bound.
3. **Seeley, J. T., Richard, M. J. and Love, P. J.** — "The Bravyi-Kitaev transformation for
   quantum computation of electronic structure," *J. Chem. Phys.* 137, 224109 (2012). Update, flip
   and parity sets, plus the H₂ Hamiltonians in all three encodings.
4. **Bravyi, S., Gambetta, J. M., Mezzacapo, A. and Temme, K.** — "Tapering off qubits to simulate
   fermionic Hamiltonians," arXiv:1701.08213 (2017). The `Z₂` symmetry / Clifford construction used
   in this chapter's worked example.
5. **Setia, K., Bravyi, S., Mezzacapo, A. and Whitfield, J. D.** — "Superfast encodings for
   fermionic quantum simulation," *Phys. Rev. Research* 1, 033033 (2019). Local encodings that
   trade extra qubits for constant-weight operators on lattices.
