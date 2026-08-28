# Quantum LDPC Codes

> **Prerequisites**: Classical linear codes and parity checks (05/02), stabilizer formalism (05/04),
> CSS construction (05/05), surface code (05/06)
> **Connects to**: Fault tolerance (05/07), surface code resource estimates (05/06), superconducting
> couplers (07/01), trapped-ion and neutral-atom connectivity (07/02, 07/03)

---

## Overview

The surface code is a superb code with a terrible rate. Its parameters `[[d², 1, d]]` mean the
encoding rate `k/n = 1/d²` tends to zero as the code grows: every additional logical qubit costs
a full fresh patch of physical qubits. At physical error rate `10⁻³` and target logical error
rate `10⁻¹²`, the resource table in Chapter 05/06 demands `d ≈ 21-27`, i.e. roughly 900-1500
physical qubits (data plus ancillas) *per logical qubit*. A useful machine with thousands of
logical qubits then needs millions of physical qubits.

**Quantum low-density parity-check (qLDPC) codes** attack this overhead directly. They keep
every stabilizer sparse — bounded weight, bounded qubit degree — like the surface code, but
drop the demand that checks be *geometrically local in 2D*. Freed from planarity, the
parameters improve dramatically: hypergraph product codes achieve constant rate; the 2021
Panteleev-Kalachev breakthrough gave "good" codes with constant rate *and* linear distance; and
IBM's 2024 bivariate bicycle codes (the `[[144,12,12]]` "gross code") pack 12 logical qubits
into the footprint the surface code spends on one or two — the concrete reason IBM's roadmap
moved off the surface code (see the roadmap note in Chapter 05/06). This chapter defines qLDPC
codes, develops the hypergraph product in full detail (with a worked `[[13,1,3]]` example
verified over GF(2)), surveys the route to good codes and the bivariate bicycle family, and
covers the two practical costs: decoding (BP+OSD) and long-range connectivity.

---

## What "LDPC" Means for a Quantum Code

A stabilizer code family `{[[n, k, d]]}` is **LDPC** if there are constants `w` and `c`,
independent of `n`, such that:

1. **Bounded check weight**: every stabilizer generator acts on at most `w` qubits.
2. **Bounded qubit degree**: every qubit appears in at most `c` stabilizer generators.

Equivalently, for a CSS code every row and column of `H_X` and `H_Z` has `O(1)` weight — the
matrices are *sparse*. Sparsity is what makes syndrome extraction fault-tolerant-friendly:
each check is measured by a constant-size circuit, so a single fault corrupts only `O(1)`
qubits.

The surface code is an LDPC code (`w = 4`, `c ≤ 4`) — but a *geometrically local* one, and
locality is the bottleneck. The Bravyi-Poulin-Terhal bound (2010) shows that any 2D code with
local checks obeys:

```
k d² ≤ c · n
```

The surface code saturates this (`k = 1`, `d = √n`): no 2D-local code can do fundamentally
better. Escaping the bound requires **long-range checks** — stabilizers connecting qubits far
apart in physical space. The qLDPC program asks: keeping checks sparse but not local, how good
can `[[n, k, d]]` be?

---

## Hypergraph Product Codes

### Construction

The **hypergraph product** (Tillich-Zémor, 2009) manufactures a CSS qLDPC code from any two
classical linear codes. Take classical parity-check matrices `H₁` (size `r₁ × n₁`) and `H₂`
(size `r₂ × n₂`). Place qubits on two blocks — `n₁n₂` "primal" qubits and `r₁r₂` "dual" qubits —
and define:

```
H_X = [ H₁ ⊗ I_{n₂} | I_{r₁} ⊗ H₂ᵀ ]
H_Z = [ I_{n₁} ⊗ H₂ | H₁ᵀ ⊗ I_{r₂} ]
```

The CSS commutation condition `H_X H_Zᵀ = 0 (mod 2)` holds automatically:

```
H_X H_Zᵀ = (H₁ ⊗ I)(I ⊗ H₂ᵀ) + (I ⊗ H₂ᵀ)(H₁ ⊗ I) = H₁ ⊗ H₂ᵀ + H₁ ⊗ H₂ᵀ = 0 (mod 2)
```

— the two terms are *equal*, and over GF(2) anything plus itself vanishes. This is the same
mechanism as the toric code's "0 or 2 shared qubits" argument, promoted to algebra.

### Parameters

If `H₁, H₂` check codes with parameters `[nᵢ, kᵢ, dᵢ]`, and the "transpose codes" (kernels of
`Hᵢᵀ`) have parameters `[rᵢ, kᵢᵀ, dᵢᵀ]`, the hypergraph product is:

```
[[ n₁n₂ + r₁r₂ ,  k₁k₂ + k₁ᵀk₂ᵀ ,  d ]]   with  d = min(d₁, d₂, d₁ᵀ, d₂ᵀ)
```

(distances of trivial `k = 0` factors are dropped). Sparsity is inherited: if the classical
codes are LDPC, so is the product. Two instructive specializations:

- **Repetition × repetition** gives the surface/toric code — see the worked example below.
- **Good classical LDPC × itself**: take `H` from a classical family with `k = Θ(n)` and
  `d = Θ(n)` (these exist — expander codes). The product is `[[Θ(n²), Θ(n²), Θ(n)]]`:
  **constant rate**, with distance `Θ(√N)` in the block length `N = Θ(n²)`. Constant rate is
  already a qualitative leap past the surface code's `1/d²`; the remaining blemish is that
  distance grows only as the square root of the block length.

---

## The Road to Good qLDPC Codes

For a decade, `d = Θ(√N)` looked like a wall. It fell through refinements of the product idea:
the **balanced product** (Breuckmann-Eberhardt, 2020) quotients the hypergraph product by a
common symmetry of the two factors, shrinking `n` while preserving `k` and `d`; the **lifted
product** (Panteleev-Kalachev, 2020-2021) replaces the binary entries of `H₁, H₂` by elements
of a group algebra `F₂[G]` — circulant blocks — inheriting the strong parameters of
quasi-cyclic classical LDPC codes.

**The breakthrough** (Panteleev-Kalachev, 2021): lifted products of expander-based codes give
**asymptotically good qLDPC codes**,

```
[[ n , k = Θ(n) , d = Θ(n) ]]   with stabilizer weight O(1)
```

— constant rate *and* linear distance, matching classical LDPC codes up to constants, long
suspected to be impossible quantumly. Leverrier and Zémor (2022) distilled the construction
into simpler **quantum Tanner codes**. These are asymptotic objects, not near-term blueprints —
but they proved the overhead of quantum error correction is in principle a *constant factor*,
not the surface code's `Θ(d²)` per logical qubit.

---

## Bivariate Bicycle Codes: The Practical Middle Ground

The **bivariate bicycle (BB) codes** (Bravyi et al., IBM, *Nature* 2024) are the family that
moved qLDPC from theory into hardware roadmaps. Construction: take two polynomials in commuting
variables `x, y` (with `xˡ = yᵐ = 1`), e.g. for the flagship code `l = 12`, `m = 6`:

```
A = x³ + y + y²,   B = y³ + x + x²   →   H_X = [A|B],  H_Z = [Bᵀ|Aᵀ]
```

Each matrix block is an `lm × lm` sum of three cyclic shift matrices, so every stabilizer has
**weight 6** and every qubit participates in 6 checks. The flagship instance is the

```
[[144, 12, 12]]  "gross code"
```

(named for the gross, 144 = 12 dozen): 144 data qubits + 144 check ancillas = 288 physical
qubits encode **12 logical qubits at distance 12**. Under circuit-level noise at `p = 10⁻³`,
its logical memory error rate matches a distance-13 surface code that would need roughly
**3000 physical qubits** for the same 12 logical qubits — a ~10× compression, and the single
number behind IBM's fault-tolerance roadmap (Starling, Blue Jay) being built on BB codes
rather than surface codes, the shift noted in Chapter 05/06's overview. The price: the Tanner
graph is non-planar; it embeds in two planar layers with each qubit coupled to 6 others, some
via long-range couplers.

---

## Decoding: Belief Propagation + Ordered Statistics (BP+OSD)

Surface codes have MWPM; general qLDPC codes do not, because their syndrome defects do not pair
up along strings. The workhorse is borrowed from classical LDPC practice and then patched:

- **Belief propagation (BP)**: pass probability messages along the Tanner graph edges;
  converges to near-maximum-likelihood on sparse *classical* codes. On quantum codes plain BP
  underperforms: the CSS commutation condition forces short cycles in the Tanner graph, and
  **degenerate errors** (equivalent up to a stabilizer) split the probability mass so BP fails
  to converge on any single representative.
- **Ordered statistics decoding (OSD)** post-processing (Panteleev-Kalachev, 2019): when BP
  stalls, use its soft output to rank bits by reliability, solve exactly (Gaussian elimination)
  on the most reliable information set, and re-encode. BP+OSD is slower than MWPM (the
  elimination step is cubic) but makes BB and hypergraph product codes perform close to their
  distance; real-time BP+OSD hardware decoders are an active engineering front.

### Single-Shot Error Correction

The surface code needs `Θ(d)` repeated syndrome rounds per cycle because one noisy measurement
round cannot be trusted. Some qLDPC codes are **single-shot**: redundancy among their checks
(or expansion properties called *confinement*) makes measurement errors themselves correctable,
so a single noisy syndrome round suffices and residual errors stay bounded instead of
accumulating (Bombín 2015 for certain topological codes; Quintavalle et al. 2021 and successors
for qLDPC families, including good codes). The payoff is a `Θ(d)` cut in time overhead —
significant when `d ≈ 20` rounds per logical cycle would otherwise be needed.

---

## The Connectivity Price

The BPT bound guarantees that beating the surface code requires **long-range checks**, and each
hardware platform pays differently:

- **Superconducting qubits** (07/01) natively couple only to fixed nearest neighbors on a chip.
  BB codes were designed to minimize the damage — degree 6, two planar layers — but still need
  centimeter-scale low-loss couplers and multi-chip links; IBM's "c-couplers" exist precisely
  to buy this connectivity.
- **Neutral atoms** (07/03) shuttle qubits in optical tweezers: any qubit can be moved next to
  any other between gate rounds, so a sparse non-local Tanner graph costs only rearrangement
  time. Hypergraph-product and lifted-product memories have been demonstrated this way.
- **Trapped ions** (07/02) have effective all-to-all connectivity within a trap via shared
  motional modes — long-range checks are nearly free at small scale.

This inverts the usual hardware ranking: the platforms with slower gates but richer
connectivity are *structurally* suited to qLDPC codes, while the fastest platform must re-
engineer its wiring to use them.

---

## Key Formulas

- **LDPC condition**: stabilizer weight `≤ w = O(1)`, qubit degree `≤ c = O(1)` (sparse `H_X, H_Z`)
- **BPT bound (2D local codes)**: `k d² = O(n)` — the surface code saturates it
- **Hypergraph product**: `H_X = [H₁ ⊗ I | I ⊗ H₂ᵀ]`, `H_Z = [I ⊗ H₂ | H₁ᵀ ⊗ I]`
- **HGP parameters**: `[[n₁n₂ + r₁r₂, k₁k₂ + k₁ᵀk₂ᵀ, min(d₁, d₂, d₁ᵀ, d₂ᵀ)]]`
- **CSS check**: `H_X H_Zᵀ = H₁ ⊗ H₂ᵀ + H₁ ⊗ H₂ᵀ = 0 (mod 2)`
- **Good qLDPC (Panteleev-Kalachev 2021)**: `[[n, Θ(n), Θ(n)]]` with `O(1)`-weight checks
- **Gross code (IBM 2024)**: `[[144, 12, 12]]`, weight-6 checks, degree-6 qubits; ≈10× fewer
  physical qubits than surface codes of equal performance

---

## Worked Example: Hypergraph Product of the [3,1,3] Repetition Code with Itself

**Setup.** The classical `[3,1,3]` repetition code has full-rank parity-check matrix

```
H = [ 1 1 0 ]      (r = 2 checks, n = 3 bits, k = 1)
    [ 0 1 1 ]
```

Its transpose code is trivial: `rank(Hᵀ) = 2 = r`, so `kᵀ = r - rank = 0`.

**Qubit count.** `n_Q = n² + r² = 9 + 4 = 13` qubits: nine "primal" qubits `(i,j)` on a `3×3`
grid (indices 0-8, row-major) and four "dual" qubits `(a,b)` on a `2×2` grid (indices 9-12).

**Logical qubits.** `k_Q = k·k + kᵀ·kᵀ = 1·1 + 0·0 = 1`.

**Stabilizers.** `H_X = [H ⊗ I₃ | I₂ ⊗ Hᵀ]` (6 rows) and `H_Z = [I₃ ⊗ H | Hᵀ ⊗ I₂]` (6 rows).
Writing the first rows out as Pauli strings on qubits 0-12:

```
X-check (0,0):  X I I X I I I I I | X I I I      (qubits 0, 3, 9)
X-check (0,1):  I X I I X I I I I | X X I I      (qubits 1, 4, 9, 10)
X-check (0,2):  I I X I I X I I I | I X I I      (qubits 2, 5, 10)
Z-check (0,0):  Z Z I I I I I I I | Z I I I      (qubits 0, 1, 9)
Z-check (0,1):  I Z Z I I I I I I | I Z I I      (qubits 1, 2, 10)
Z-check (1,0):  I I I Z Z I I I I | Z I Z I      (qubits 3, 4, 9, 11)
```

Every check has weight 3 or 4 and every qubit degree ≤ 4 — sparse, as promised. These are
exactly the boundary (weight-3) and bulk (weight-4) plaquettes of a surface code patch: the
hypergraph product of two repetition codes **is** the unrotated planar surface code,
`2d² - 2d + 1 = 13` for `d = 3` (cf. 05/06).

**Numerical verification** (GF(2) linear algebra with numpy):

```
rank(H) = 2, classical k = 1, transpose kᵀ = 0
n_qubits = 13 (= 3² + 2²)
H_X @ H_Zᵀ mod 2 == 0 : True          ← CSS commutation holds
rank H_X = 6, rank H_Z = 6  →  k = 13 - 6 - 6 = 1
min-weight X logical = 3, min-weight Z logical = 3   (exhaustive search)
check weights ∈ {3, 4};  max qubit degree = 4
```

Result: the `[[13, 1, 3]]` code, exactly as the parameter formula predicts
(`d = min(3, 3) = 3`; the trivial transpose factors contribute nothing).

---

## Summary

- The surface code's rate `1/d²` → 0 is its fatal flaw at scale: ~1000 physical qubits per
  logical qubit, millions for useful algorithms. The BPT bound `kd² = O(n)` shows any 2D-local
  code shares this fate — improvement requires long-range checks.
- qLDPC codes keep stabilizers sparse (`O(1)` weight and degree) but drop geometric locality.
- The hypergraph product turns any two classical codes into a CSS qLDPC code,
  `[[n₁n₂ + r₁r₂, k₁k₂ + k₁ᵀk₂ᵀ, min dᵢ]]`; good classical LDPC inputs give constant rate with
  `d = Θ(√n)`; repetition-code inputs reproduce the surface code.
- Lifted/balanced products led to the Panteleev-Kalachev 2021 good codes — constant rate,
  linear distance — proving constant-factor QEC overhead is possible in principle.
- IBM's `[[144,12,12]]` bivariate bicycle "gross code" delivers ~10× qubit savings over the
  surface code at realistic error rates and anchors IBM's post-surface-code roadmap.
- Practical costs: BP+OSD decoding (slower than MWPM, degeneracy-aware), and long-range
  connectivity — natural for neutral atoms and ions, hard-won couplers for superconductors.
  Single-shot qLDPC codes recoup a further `Θ(d)` factor in time overhead.

---

## Exercises

**Exercise 1.** Verify the CSS commutation condition for a general hypergraph product
algebraically: show `H_X H_Zᵀ = 0 (mod 2)` using the mixed-product identity
`(A ⊗ B)(C ⊗ D) = AC ⊗ BD`.

<details><summary>Solution</summary>

```
H_X H_Zᵀ = [H₁ ⊗ I_{n₂} | I_{r₁} ⊗ H₂ᵀ] · [I_{n₁} ⊗ H₂ | H₁ᵀ ⊗ I_{r₂}]ᵀ
        = (H₁ ⊗ I_{n₂})(I_{n₁} ⊗ H₂ᵀ) + (I_{r₁} ⊗ H₂ᵀ)(H₁ ⊗ I_{r₂})
        = H₁ ⊗ H₂ᵀ + H₁ ⊗ H₂ᵀ
```

By the mixed-product identity both terms equal `H₁ ⊗ H₂ᵀ`, and over GF(2), `M + M = 0`. Note
this uses nothing about `H₁, H₂` — *any* pair of classical codes works, which is what makes
the construction a factory.

</details>

**Exercise 2.** Compute the parameters of the hypergraph product of the `[7,4,3]` Hamming code
with itself. The Hamming parity-check matrix `H` is `3 × 7` with all nonzero 3-bit columns;
`rank(H) = 3`, and the transpose code is `[3, 0, -]`. What is the rate, and how does it compare
to a distance-3 surface code?

<details><summary>Solution</summary>

`n = 7·7 + 3·3 = 58` qubits; `k = 4·4 + 0·0 = 16` logical qubits;
`d = min(3, 3) = 3` (transpose factors trivial). Parameters: `[[58, 16, 3]]`, rate
`16/58 ≈ 0.28`. A rotated surface code protects 1 logical qubit at `d = 3` with 9 data qubits —
so 16 logical qubits cost `144` data qubits, versus 58 here: a 2.5× saving already at distance
3, and the gap widens with scale because the HGP rate stays constant while the surface code's
vanishes.

</details>

**Exercise 3.** The BPT bound says 2D-local codes obey `kd² ≤ cn`. Show that (a) the surface
code saturates it up to constants, and (b) a constant-rate code family (`k = ρn`) obeying the
bound would have `d = O(1)` — and explain why constant distance is useless.

<details><summary>Solution</summary>

(a) Surface code: `k = 1`, `d = √n` (rotated: `n = d²`), so `kd² = n` — saturation with
`c = 1`. (b) If `k = ρn`, the bound forces `ρ n d² ≤ cn`, i.e. `d² ≤ c/ρ = O(1)`. A constant-
distance family corrects only a constant number of errors regardless of block length, so as
`n → ∞` the probability of an uncorrectable error per block approaches 1 — the logical error
rate cannot be suppressed by scaling. Hence constant-rate scalable codes *must* be non-local,
which is the structural argument for qLDPC's long-range checks.

</details>

**Exercise 4.** In the `[[13,1,3]]` worked example, exhibit a weight-3 logical `Z̄` and verify
by hand that it (a) commutes with the three X-checks listed, and (b) is not a product of
Z-stabilizers. (Hint: try `Z` on the middle column of primal qubits, `{1, 4, 7}`.)

<details><summary>Solution</summary>

Take `Z̄ = Z₁Z₄Z₇` (primal qubits `(0,1), (1,1), (2,1)` — a vertical line through the grid).
(a) The six X-check supports are `{0,3,9}, {1,4,9,10}, {2,5,10}, {3,6,11}, {4,7,11,12},
{5,8,12}`; their overlaps with `{1,4,7}` have sizes `0, 2, 0, 0, 2, 0` — all even, so `Z̄`
commutes with every X-check. (b) Every row of `H_Z` touches a *horizontal* primal pair
`(i,j),(i,j+1)` plus dual qubits; no GF(2) combination of the six rows cancels all dual-qubit
support while producing the purely vertical pattern `{1,4,7}` (verified numerically:
`rank([H_Z; Z̄]) = rank(H_Z) + 1`). Since the code distance is 3 and `Z̄` has weight 3, it is a
minimum-weight logical — the vertical `Z` string of the `d = 3` surface code patch.

</details>

**Exercise 5.** A machine needs 1200 logical qubits at logical error rate `10⁻¹²` with physical
error rate `10⁻³`. Estimate physical qubit counts using (a) `d = 27` rotated surface codes
(cf. 05/06 Exercise 4), and (b) gross-code-style qLDPC blocks assumed to reach that logical
rate at 288 physical qubits per 12 logical qubits. What ratio results, and what hidden costs
does estimate (b) omit?

<details><summary>Solution</summary>

(a) Surface code: `2d² - 1 = 1457` physical qubits per logical qubit → `1200 × 1457 ≈ 1.75 ×
10⁶`. (b) qLDPC: `1200/12 = 100` blocks × 288 qubits `≈ 2.9 × 10⁴` — a ratio of ~60× (in
reality the gross code alone would need more than `d = 12` for `10⁻¹²`; the honestly
demonstrated figure is closer to 10×, with larger BB codes covering the rest of IBM's roadmap).
Omitted costs: (i) long-range couplers and multilayer wiring; (ii) real-time BP+OSD decoder
hardware; (iii) *logical operations* — addressing individual logical qubits inside a qLDPC
block needs ancilla systems and surgery gadgets that erode part of the memory savings, whereas
surface codes have cheap lattice-surgery Cliffords; (iv) magic-state distillation, common to
both.

</details>

---

## Further Reading

1. **Tillich, J.-P. and Zémor, G.** — "Quantum LDPC codes with positive rate and minimum
   distance proportional to √n," *IEEE Trans. Inf. Theory* 60, 1193 (2014); arXiv:0903.0566.
   The hypergraph product construction.
2. **Bravyi, S., Poulin, D., and Terhal, B.** — "Tradeoffs for reliable quantum information
   storage in 2D systems," *Phys. Rev. Lett.* 104, 050503 (2010). The `kd² = O(n)` bound.
3. **Panteleev, P. and Kalachev, G.** — "Asymptotically good quantum and locally testable
   classical LDPC codes," *STOC 2022*; arXiv:2111.03654. The good-qLDPC breakthrough.
4. **Bravyi, S. et al.** — "High-threshold and low-overhead fault-tolerant quantum memory,"
   *Nature* 627, 778 (2024); arXiv:2308.07915. Bivariate bicycle codes and the [[144,12,12]]
   gross code.
5. **Breuckmann, N. P. and Eberhardt, J. N.** — "Quantum low-density parity-check codes,"
   *PRX Quantum* 2, 040101 (2021). Accessible survey of the whole qLDPC landscape, including
   balanced products and decoding.
