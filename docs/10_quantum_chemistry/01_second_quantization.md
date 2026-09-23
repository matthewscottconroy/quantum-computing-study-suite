# Second Quantization and the Electronic Structure Hamiltonian

> **Prerequisites**: Linear algebra and tensor products (01/01, 01/03), quantum mechanics
> postulates (02/01), many-body physics and the Jordan-Wigner string (08/03)
> **Connects to**: Qubit mappings (10/02), active spaces and ansätze (10/03),
> VQE fundamentals (06/01)

---

## Overview

Every quantum-chemistry algorithm on a quantum computer begins in the same place: a molecular
Hamiltonian written in **second quantization**. Chapter 06/01 quoted a five-term, two-qubit
operator for H₂ and used it to run VQE by hand. This chapter derives where such an operator comes
from — the integrals, the operator algebra, and the bookkeeping conventions that turn a molecule
into a finite Hermitian matrix.

Second quantization is not a new physical theory but a change of language. In *first*
quantization you write an antisymmetric wavefunction `Ψ(r₁, …, r_η)` and enforce the Pauli
principle by hand through Slater determinants. In *second* quantization you fix a finite
orthonormal set of **spin orbitals** and describe a state by which of them are occupied;
antisymmetry is absorbed once and for all into the operator algebra. The payoff for quantum
computing is immediate: occupation numbers are bits, so a state of `N` spin orbitals is a state of
`N` qubits, and the Hamiltonian becomes a short polynomial in operators that Chapter 10/02 maps to
Pauli strings.

This chapter develops Fock space, the fermionic operator algebra, the one- and two-electron
integrals that parameterize the Hamiltonian, and the Slater-Condon rules for its matrix elements,
closing with a worked H₂/STO-3G calculation whose numbers feed every later chapter.

---

## The Electronic Structure Problem

### Born-Oppenheimer separation

Nuclei are thousands of times heavier than electrons, so to excellent accuracy the nuclear
coordinates `{R_A}` can be frozen and the electrons solved in their static field. In **Hartree
atomic units** (`ħ = m_e = e = 4πε₀ = 1`; energies in hartree, lengths in bohr) the electronic
Hamiltonian for `η` electrons and `n_nuc` clamped nuclei of charge `Z_A` is

```
H_elec = - Σ_i ∇²_i / 2  -  Σ_i Σ_A Z_A / |r_i - R_A|  +  Σ_{i<j} 1 / |r_i - r_j|
```

and the total molecular energy at that geometry adds the constant nuclear repulsion

```
E_nuc = Σ_{A<B} Z_A Z_B / |R_A - R_B|
```

`E_nuc` is a number, not an operator: it shifts the whole spectrum and never affects eigenvectors.
Forgetting it is the commonest reason a quantum-chemistry energy is off by a fixed offset.

### Why a basis set is needed

`H_elec` acts on an infinite-dimensional space. Practical calculations project it onto a finite set
of `M` **spatial** basis functions `{φ_p(r)}` — for molecules, contracted Gaussians, since products
of Gaussians are Gaussians and every integral is analytic. Each spatial orbital carries two spin
functions, giving `N = 2M` **spin orbitals** `{χ_p(x)}` with `x = (r, σ)`. Everything below is
exact *within* that basis; basis-set incompleteness is a separate classical error that no quantum
algorithm removes.

---

## Fock Space and Occupation Numbers

Fix an orthonormal set of `N` spin orbitals. A Slater determinant of `η` of them is specified by
which orbitals are occupied, so label basis states by occupation numbers `n_p ∈ {0, 1}`:

```
|n₀ n₁ … n_{N-1}⟩,   n_p ∈ {0,1},   η = Σ_p n_p
```

The span of *all* `2^N` such states — every particle number at once — is the **Fock space**

```
F = ⨁_{η=0}^{N} Λ^η(C^N),   dim F = Σ_η C(N, η) = 2^N
```

This coincidence is what makes fermionic simulation natural on qubits: Fock space for `N` spin
orbitals and the Hilbert space of `N` qubits both have dimension `2^N`. The fixed-`η` sector
`Λ^η` has dimension `C(N, η)` — the number of Slater determinants, and the dimension of a full
configuration interaction (FCI) problem. The **vacuum** `|vac⟩ = |0 … 0⟩` contains no electrons;
physical states live in one particle-number sector, but the algebra is cleanest on all of `F`.

---

## Creation and Annihilation Operators

Define `a_p†` ("create in spin orbital `p`") and `a_p` ("annihilate") by their action on
occupation-number states, with an explicit **Jordan-Wigner sign** counting occupied orbitals to
the left of `p`:

```
a_p† |… n_p = 0 …⟩ = (-1)^{Σ_{k<p} n_k} |… n_p = 1 …⟩,   a_p† |… n_p = 1 …⟩ = 0
a_p  |… n_p = 1 …⟩ = (-1)^{Σ_{k<p} n_k} |… n_p = 0 …⟩,   a_p  |… n_p = 0 …⟩ = 0
```

The parity prefactor is not decoration: it is what encodes antisymmetry. It makes the operators
satisfy the **canonical anticommutation relations** (CAR)

```
{a_p, a_q†} = δ_pq,   {a_p, a_q} = 0,   {a_p†, a_q†} = 0
```

where `{A, B} = AB + BA`. Setting `p = q` in the third relation gives `(a_p†)² = 0` — the **Pauli
exclusion principle**, derived rather than imposed. And `a_p† a_q† = -a_q† a_p†` means a
determinant's orbital ordering matters up to a sign, so every implementation must fix one
convention and keep it.

The **number operator** `n̂_p = a_p† a_p` is a projector with eigenvalues `0, 1`, and
`N̂ = Σ_p n̂_p` counts electrons. Any operator with equal numbers of `a†`s and `a`s commutes with
`N̂`, so `H` conserves particle number — a fact Chapter 10/02 cashes in as two free qubits.

A determinant is built from the vacuum in a fixed order,
`|Φ⟩ = a_{p₁}† a_{p₂}† … a_{p_η}† |vac⟩` with `p₁ < p₂ < … < p_η`.

---

## Spin Orbitals, Integrals and Notation

### The two tensors

Projected onto the basis, `H_elec` is fully specified by two tensors of numbers computed
classically, once, before any quantum circuit runs.

**One-electron integrals** (kinetic energy plus nuclear attraction):

```
h_pq = ∫ dx  χ_p*(x) [ -∇²/2 - Σ_A Z_A/|r - R_A| ] χ_q(x)
```

**Two-electron integrals** (Coulomb repulsion). Two notations are in use and confusing them is a
classic bug:

```
chemist:   (pq|rs) = ∫∫ dx₁ dx₂  χ_p*(x₁) χ_q(x₁) (1/r₁₂) χ_r*(x₂) χ_s(x₂)
physicist: ⟨pr|qs⟩ = (pq|rs)
```

Chemist notation groups the two functions of the *same* electron together; Chapter 10 uses it
throughout. Both integrals vanish unless spins match within each pair: `h_pq = 0` unless
`σ_p = σ_q`, and `(pq|rs) = 0` unless `σ_p = σ_q` and `σ_r = σ_s`.

### Symmetry and counting

For real orbitals the chemist integrals have **8-fold permutational symmetry**

```
(pq|rs) = (qp|rs) = (pq|sr) = (qp|sr) = (rs|pq) = (sr|pq) = (rs|qp) = (sr|qp)
```

so the number of independent spatial-orbital integrals is `n(n+1)/2` with `n = M(M+1)/2` — still
`O(M⁴)`, but eight times cheaper than the naive count:

| `M` spatial orbitals | naive `M⁴` | unique 8-fold |
|---|---|---|
| 2 (H₂/STO-3G) | 16 | 6 |
| 7 (H₂O/STO-3G) | 2,401 | 406 |
| 100 | 10⁸ | 12,753,775 |

This `O(M⁴)` tensor is the origin of the `O(N⁴)` Pauli-term count quoted in Chapter 06/01.

---

## The Second-Quantized Hamiltonian

Collecting the pieces, the electronic Hamiltonian in second quantization is

```
H = Σ_{pq} h_pq a_p† a_q  +  (1/2) Σ_{pqrs} (pq|rs) a_p† a_r† a_s a_q  +  E_nuc
```

Note the operator order in the two-body term — `a_p† a_r† a_s a_q`, with the `q` index (paired with
`p` inside the integral) innermost. Writing `a_p† a_q† a_r a_s` with a chemist integral is a sign
error waiting to happen.

Two structural remarks. The Hamiltonian is a **quartic polynomial** in `2N` operators, and no
approximation has been made beyond the basis: diagonalizing it in the `η`-electron sector *is*
FCI. And `H` commutes with `N̂`, with `Ŝ_z = (1/2) Σ_p (-1)^{σ_p} n̂_p`, with `Ŝ²`, and with the
molecular point group — each conserved quantity a handle for reducing qubit count (Chapter 10/02)
or detecting errors in a noisy run (Chapter 06/06).

### Slater-Condon rules

Matrix elements between determinants follow mechanically from the CAR. For a determinant `|Φ⟩`
with occupied set `O`:

```
⟨Φ|H|Φ⟩ = Σ_{i∈O} h_ii + (1/2) Σ_{i,j∈O} [ (ii|jj) - (ij|ji) ] + E_nuc
```

`(ii|jj)` is the classical **Coulomb** repulsion `J_ij`; `(ij|ji)` is the **exchange** term
`K_ij`, a pure consequence of antisymmetry, nonzero only for parallel spins (the spin integral
`⟨σ_i|σ_j⟩` kills it otherwise). The `i = j` terms cancel exactly, so an electron does not repel
itself — the self-interaction freedom that approximate density functionals famously lack.
Determinants differing by one spin orbital (`i → a`) give

```
⟨Φ_i^a|H|Φ⟩ = h_ia + Σ_{j∈O} [ (ia|jj) - (ij|ja) ]
```

and by two (`i,j → a,b`) give the strikingly simple

```
⟨Φ_ij^ab|H|Φ⟩ = (ia|jb) - (ib|ja)
```

Determinants differing by three or more orbitals have zero matrix element: the Hamiltonian is a
two-body operator, so it can move at most two electrons. That single fact is why coupled cluster
truncates at singles and doubles, and why UCCSD (Chapter 10/03) is the natural ansatz family.

---

## Key Formulas

- **Electronic Hamiltonian (first quantized, atomic units)**:
  `H = -Σ_i ∇²_i/2 - Σ_{iA} Z_A/|r_i - R_A| + Σ_{i<j} 1/r_ij`
- **CAR**: `{a_p, a_q†} = δ_pq`, `{a_p, a_q} = {a_p†, a_q†} = 0`
- **Second-quantized Hamiltonian**:
  `H = Σ_pq h_pq a_p† a_q + (1/2) Σ_pqrs (pq|rs) a_p† a_r† a_s a_q + E_nuc`
- **Chemist integral**: `(pq|rs) = ∫∫ χ_p*(1)χ_q(1) r₁₂⁻¹ χ_r*(2)χ_s(2)`
- **Diagonal Slater-Condon**: `⟨Φ|H|Φ⟩ = Σ_i h_ii + ½Σ_ij [(ii|jj) - (ij|ji)] + E_nuc`
- **FCI dimension**: `C(M, η_α) × C(M, η_β)` for `M` spatial orbitals

---

## Worked Example: H₂ / STO-3G from Scratch

**Geometry and basis.** Two hydrogens at `R = 0.735 Å = 1.388949` bohr; STO-3G gives each atom one
contracted 1s function from three primitives with exponents
`α = (3.42525091, 0.62391373, 0.16885540)` and coefficients `(0.15432897, 0.53532814, 0.44463454)`.
Nuclear repulsion is `E_nuc = 1/R = 0.719969` Ha, the value used throughout Chapter 06.

**Atomic-orbital integrals** (analytic, from the Gaussian product theorem; hartree, index 1,2 =
the two atoms):

```
S₁₂  = 0.663146                      overlap
T₁₁  = 0.760032    T₁₂ = 0.239954    kinetic
V₁₁  = -1.884249   V₁₂ = -1.205211   nuclear attraction (both nuclei)
h₁₁  = -1.124218   h₁₂ = -0.965257   core = T + V
(11|11) = 0.774606   (11|22) = 0.571877
(12|12) = 0.300918   (11|12) = 0.447446
```

**Molecular orbitals.** The `D_∞h` symmetry of H₂ fixes the MOs with no SCF iteration:
`σ_g = (χ₁ + χ₂)/√(2 + 2S₁₂) = 0.548302 (χ₁ + χ₂)` and
`σ_u = (χ₁ - χ₂)/√(2 - 2S₁₂) = 1.218327 (χ₁ - χ₂)`. Transforming the integrals — for example
`h_gg = (h₁₁ + h₁₂)/(1 + S₁₂) = (-1.124218 - 0.965257)/1.663146 = -1.256339` — gives

```
h_gg = -1.256339    h_uu = -0.471896     (h_gu = 0 by symmetry)
(gg|gg) = 0.675710  (uu|uu) = 0.698574
(gg|uu) = 0.664582  (gu|gu) = 0.180931
```

The last of these, `(gu|gu) = 0.180931`, is exactly the coefficient of `X₁X₂` in the two-qubit
Hamiltonian of Chapter 06/01 — the entire correlation physics of H₂ in one integral.

**Spin orbitals.** Four of them, ordered `0 = σ_g α`, `1 = σ_u α`, `2 = σ_g β`, `3 = σ_u β`
("blocked" ordering: all α, then all β). The Hartree-Fock determinant is

```
|HF⟩ = a₀† a₂† |vac⟩ = |1 0 1 0⟩
```

**Hartree-Fock energy by Slater-Condon.** Occupied set `O = {0, 2}`, one-electron part
`h₀₀ + h₂₂ = 2 × (-1.256339) = -2.512678`. Of the four ordered pairs, the `i = j` ones cancel,
`(00|22) = (22|00) = 0.675710`, and the exchange `(02|20)` vanishes on opposite spins:

```
½[(00|00) - (00|00) + 0.675710 + 0.675710 + (22|22) - (22|22)] = 0.675710
E_HF(elec) = -2.512678 + 0.675710 = -1.836968 Ha
E_HF(total) = -1.836968 + 0.719969 = -1.116999 Ha
```

matching the `E_HF = -1.836968` Ha quoted in Chapter 06/01.

**Full CI.** With two electrons in two spatial orbitals the singlet space is two-dimensional,
spanned by `|σ_g²⟩` and `|σ_u²⟩` (the singly excited singlet has the wrong `g/u` parity and does
not mix), giving the `2 × 2` Hamiltonian

```
⟨gg|H|gg⟩ = 2h_gg + (gg|gg) = -1.836968
⟨uu|H|uu⟩ = 2h_uu + (uu|uu) = -0.245218
⟨gg|H|uu⟩ = (gu|gu)         =  0.180931
```

Diagonalizing gives electronic eigenvalues `{-1.857275, -0.224911}` Ha, so
`E₀(elec) = -1.857275` Ha, `E₀(total) = -1.857275 + 0.719969 = -1.137306` Ha and
`E_corr = E₀ - E_HF = -20.307` mHa — the familiar H₂ ground-state energy of Chapter 06/01, now
derived from the integrals up. The ground eigenvector is
`0.993760 |σ_g²⟩ - 0.111536 |σ_u²⟩`: only `1.24 %` doubly excited character, so H₂ at equilibrium
is a weakly correlated, single-reference molecule. Chapter 10/03 shows what happens to that number
as the bond stretches.

---

## Summary

- Second quantization fixes a finite spin-orbital basis and moves antisymmetry from the
  wavefunction into the operator algebra; Fock space for `N` spin orbitals has dimension `2^N`,
  exactly matching `N` qubits.
- The CAR `{a_p, a_q†} = δ_pq` imply Pauli exclusion (`(a_p†)² = 0`) and the Jordan-Wigner parity
  signs that Chapter 10/02 turns into `Z` strings.
- The molecular Hamiltonian is fixed by two classically computed tensors, `h_pq` (`O(M²)` numbers)
  and `(pq|rs)` (`O(M⁴)` numbers, reduced 8-fold by permutational symmetry), plus the constant
  `E_nuc`.
- Slater-Condon rules give all matrix elements; because `H` is two-body, determinants differing in
  three or more orbitals never couple — the structural reason singles and doubles dominate.
- For H₂/STO-3G at `R = 0.735 Å`: `h_gg = -1.256339`, `(gu|gu) = 0.180931`,
  `E_HF = -1.116999` Ha, `E_FCI = -1.137306` Ha, `E_corr = -20.3` mHa.

---

## Exercises

**Exercise 1**: Using only the CAR, evaluate `a_p a_p† a_p` and `n̂_p²`. What do the results say
about the spectrum of `n̂_p`?

<details><summary>Solution</summary>

From `{a_p, a_p†} = 1`, write `a_p a_p† = 1 - a_p† a_p`. Then

```
a_p a_p† a_p = (1 - a_p† a_p) a_p = a_p - a_p† a_p a_p = a_p
```

since `a_p a_p = 0` (from `{a_p, a_p} = 2a_p² = 0`). For the number operator,

```
n̂_p² = a_p† a_p a_p† a_p = a_p† (a_p a_p† a_p) = a_p† a_p = n̂_p
```

So `n̂_p` is idempotent and Hermitian: a projector, with eigenvalues `0` and `1` only. Occupation
numbers are bits because the algebra says so, not because we declared it.

</details>

**Exercise 2**: A closed-shell molecule has `M = 20` spatial orbitals and 20 electrons. Give
(a) the number of qubits under a one-spin-orbital-per-qubit encoding, (b) the FCI dimension, and
(c) the number of unique two-electron integrals.

<details><summary>Solution</summary>

(a) `N = 2M = 40` qubits.

(b) 10 α and 10 β electrons in 20 spatial orbitals:
`C(20,10)² = 184756² = 3.41 × 10^10` determinants. Storable, but only just — a dense FCI vector
at 8 bytes per amplitude is ~273 GB.

(c) `n = M(M+1)/2 = 210`, so `n(n+1)/2 = 22,155` unique integrals (versus `20⁴ = 160,000` naive).

Note the asymmetry that motivates quantum algorithms: the *input* to the problem is only tens of
thousands of numbers, while the *solution space* is `10^10`-dimensional and grows exponentially.

</details>

**Exercise 3**: For H₂/STO-3G above, compute `⟨σ_u²|H|σ_u²⟩` and explain why the doubly excited
determinant lies only `1.59` Ha above the Hartree-Fock one rather than `2 × (h_uu - h_gg)`.

<details><summary>Solution</summary>

`⟨σ_u²|H|σ_u²⟩ = 2h_uu + (uu|uu) = 2(-0.471896) + 0.698574 = -0.245218` Ha (electronic), which is
`-0.245218 - (-1.836968) = 1.591750` Ha above `E_HF`.

Twice the orbital-energy gap would be `2(h_uu - h_gg) = 2(0.784443) = 1.568886` Ha — close, but
not equal, because the two-electron repulsion also changes: the pair sits in `σ_u` rather than
`σ_g`, so `(gg|gg) = 0.675710` is replaced by `(uu|uu) = 0.698574`, adding `0.022864` Ha. Indeed
`1.568886 + 0.022864 = 1.591750` Ha. Orbital energies alone never give determinant energies;
the two-electron terms must be re-evaluated.

</details>

**Exercise 4**: The Hamiltonian conserves `N̂`. Prove that `[a_p† a_q, N̂] = 0` directly from the
CAR, and state what this implies for the block structure of `H` in the occupation-number basis.

<details><summary>Solution</summary>

Use `[A, BC] = {A, B}C - B{A, C}`. With `N̂ = Σ_k a_k† a_k`:

```
[a_q, a_k† a_k] = {a_q, a_k†}a_k - a_k†{a_q, a_k} = δ_qk a_k
```
so `[a_q, N̂] = a_q`, and taking adjoints `[a_p†, N̂] = -a_p†`. Then

```
[a_p† a_q, N̂] = a_p†[a_q, N̂] + [a_p†, N̂]a_q = a_p† a_q - a_p† a_q = 0
```

Since every Hamiltonian term has equal numbers of creation and annihilation operators, the same
telescoping gives `[H, N̂] = 0`. In the occupation basis `H` is therefore block diagonal, one block
per electron number `η`, of size `C(N, η)`. A quantum algorithm only ever needs the physical block,
which is why particle number is the first symmetry exploited for qubit reduction in Chapter 10/02.

</details>

---

## Further Reading

1. **Szabo, A. and Ostlund, N. S.** — *Modern Quantum Chemistry*, Dover (1996). Chapter 2
   (Hartree-Fock and the Slater-Condon rules) and Appendix A (the STO-3G H₂ integrals reproduced
   in this chapter's worked example).
2. **Helgaker, T., Jørgensen, P. and Olsen, J.** — *Molecular Electronic-Structure Theory*, Wiley
   (2000). Chapter 1 (second quantization) and Chapter 9 (Gaussian integral evaluation).
3. **McArdle, S., Endo, S., Aspuru-Guzik, A., Benjamin, S. C. and Yuan, X.** — "Quantum
   computational chemistry," *Rev. Mod. Phys.* 92, 015003 (2020). Section II sets up second
   quantization for quantum-computing audiences.
4. **Whitfield, J. D., Biamonte, J. and Aspuru-Guzik, A.** — "Simulation of electronic structure
   Hamiltonians using quantum computers," *Mol. Phys.* 109, 735 (2011). Fixed the operator-ordering
   and integral conventions most quantum-chemistry software now follows.
5. **Bartlett, R. J. and Musiał, M.** — "Coupled-cluster theory in quantum chemistry,"
   *Rev. Mod. Phys.* 79, 291 (2007). Section II: the excitation hierarchy behind Chapter 10/03.
