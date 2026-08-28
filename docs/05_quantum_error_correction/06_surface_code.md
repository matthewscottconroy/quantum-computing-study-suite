# The Surface Code

> **Prerequisites**: Stabilizer formalism (05/04), CSS codes (05/05), syndrome measurement
> **Connects to**: Fault tolerance (05/07), MWPM decoding, anyons and topological QC (08/04),
> hardware benchmarking (07/04)

---

## Overview

The surface code is currently the leading candidate for large-scale fault-tolerant quantum
computing, and for good reason. It achieves the highest known error threshold (~1%) among
practically realizable two-dimensional local codes, requires only nearest-neighbor interactions
on a planar grid, and admits an efficient classical decoding algorithm (minimum-weight perfect
matching) that scales polynomially. The surface code is central to several major error
correction roadmaps — Google's and AWS's architectures are built around it — though not all:
IBM's roadmap now centers on qLDPC codes, and trapped-ion and neutral-atom roadmaps emphasize
codes suited to their different connectivities.

The surface code originates from Kitaev's toric code (1997), defined on a torus for theoretical
elegance, then modified to a planar geometry with boundaries by Bravyi and Kitaev (1998) —
with closely related planar constructions by Freedman and Meyer (1998). The planar "surface
code" is what appears in experiments, since building a torus in hardware is impractical.

This chapter develops the surface code from the lattice geometry, defines the stabilizers and
logical operators, explains the threshold and why it is so high, and describes minimum-weight
perfect matching (MWPM) decoding. We include resource estimates for practical quantum advantage.

---

## The Toric Code: Conceptual Foundation

### Lattice and Qubits

Place one qubit on each edge of an `L×L` square lattice drawn on a torus. There are `2L²`
edge qubits. The lattice has `L²` vertices (stars) and `L²` faces (plaquettes).

**Vertex (star) operators** for vertex `v`:
```
A_v = ⊗_{e ∈ star(v)} X_e
```
(tensor product of X on all 4 edges meeting at vertex `v`)

**Plaquette (face) operators** for face `f`:
```
B_f = ⊗_{e ∈ ∂f} Z_e
```
(tensor product of Z on all 4 edges bordering face `f`)

### Stabilizer Properties

All vertex and plaquette operators commute:
- `[A_v, A_{v'}] = 0` (both X-type, so commute trivially)
- `[B_f, B_{f'}] = 0` (both Z-type)
- `[A_v, B_f] = 0`: The star of `v` and boundary of `f` overlap in exactly 0 or 2 edges (on a
  torus). Since 2 is even, the operators commute.

**Constraints**: `∏_v A_v = I` (product of all stars = identity) and `∏_f B_f = I`. So only
`L² - 1` star operators and `L² - 1` plaquette operators are independent. Total independent
generators: `2(L² - 1)`. On `2L²` qubits, code dimension `= 2L² - 2(L²-1) = 2`. The toric
code encodes **2 logical qubits**.

### Logical Operators of Toric Code

The logical operators are string operators running around the non-contractible loops of the torus:
```
Z̄₁ = Z on a horizontal path of edges across the torus
X̄₁ = X on a vertical path of edges across the torus
Z̄₂ = Z on a vertical path of edges
X̄₂ = X on a horizontal path of edges
```
Each string has length `L`, so minimum weight `d = L`. This is the origin of the `[[2L²,2,L]]`
notation.

---

## The Planar Surface Code

### Geometry

Replace the torus with a planar `d×d` grid. The boundary conditions break the toric code's
symmetry and require distinguishing two types of boundaries:

- **Smooth boundaries** (left and right): exposed vertex (star) operators — only 2-qubit or
  3-qubit versions instead of 4-qubit.
- **Rough boundaries** (top and bottom): exposed plaquette (face) operators.

**Qubits**: Two standard planar layouts exist, distinguished by how the lattice is cut:

- **Unrotated planar code**: data qubits on the edges of a `d×d` patch, giving
  `d² + (d-1)² = 2d² - 2d + 1` data qubits for distance `d`.
- **Rotated surface code** (Bombín and Martín-Delgado 2007; Fowler et al. 2012): the lattice
  is tilted 45° and trimmed, cutting the qubit count roughly in half for the same distance.

The rotated layout is what modern experiments use, and we adopt it from here on. For odd
distance `d` it has:

- **`d²` data qubits** (a `d×d` grid),
- **`d² - 1` stabilizers** — `(d²-1)/2` X-type and `(d²-1)/2` Z-type — each measured with one
  ancilla qubit,
- **`2d² - 1` physical qubits total** (data + ancillas), encoding **1 logical qubit** with
  distance `d`.

For example, `d = 3` uses 9 data qubits, 8 ancillas, 17 qubits total; `d = 5` uses 25 data
qubits, 24 ancillas, 49 total.

### Stabilizers of the Planar Surface Code

In the rotated (tilted) lattice representation, the star/plaquette distinction of the toric
code becomes a checkerboard: both stabilizer types are faces of the tilted lattice, colored
alternately X and Z:

**X stabilizers**: each acts on 4 data qubits with X (2 at the boundary).

**Z stabilizers**: each acts on 4 data qubits with Z (2 at the boundary).

Unlike the torus, the planar code has no global constraint among its stabilizers: all
`d² - 1` stabilizers are independent. On `d²` data qubits this gives code space dimension
`2^{d²-(d²-1)} = 2^1 = 2`, encoding 1 logical qubit. ✓

### Logical Operators

**Logical `Z̄`**: a chain of Z operators running from a rough boundary to the opposite rough
boundary — a Z string of length `d` crossing the lattice top-to-bottom.

**Logical `X̄`**: a chain of X operators running from a smooth boundary to the opposite smooth
boundary — an X string of length `d` crossing left-to-right.

The minimum weight of any logical operator is `d` (the distance). Errors of weight `< d/2` are
correctable. This is the source of the `[[d², 1, d]]` code parameters.

---

## Error Correction and Anyons

### Syndrome Measurement

Measuring the stabilizers reveals error syndromes. An error `E` (tensor product of single-qubit
Paulis) causes a syndrome `s` where each syndrome bit indicates whether `E` commutes or
anticommutes with the corresponding stabilizer.

**X errors** are detected by Z stabilizers: an X error on qubit `e` anticommutes with Z
stabilizers at the two faces bordering `e`.

**Z errors** are detected by X stabilizers: a Z error on qubit `e` anticommutes with X
stabilizers at the two vertices bordering `e`.

### Anyonic Picture

The syndrome defects of the toric/surface code can be interpreted as **anyons** (quasi-particles
with exotic braiding statistics):

- **`e` (electric) anyons**: syndrome defects of Z stabilizers, created by X errors.
- **`m` (magnetic) anyons**: syndrome defects of X stabilizers, created by Z errors.

Anyons are created in pairs at the endpoints of error strings. Moving an error string moves
one anyon while leaving the other fixed. Annihilating two anyons (bringing them together)
corresponds to correcting the error.

The surface code has Abelian anyons (the e and m particles have trivial mutual statistics, and
braiding e around m gives a phase of -1). Non-Abelian anyons (the foundation of topological
quantum computation) arise in other models; see Chapter 08/04.

---

## The ~1% Threshold

### Why the Threshold is High

The surface code threshold of approximately `p_th ≈ 1%` (under circuit-level depolarizing noise)
is remarkably high compared to other codes. The key reasons:

1. **Local 2D structure**: each stabilizer involves only 4 neighboring qubits. Error propagation
   is geometrically constrained. Errors on distant qubits are unlikely to conspire.

2. **High connectivity of syndrome graph**: the decoder's task — finding the most likely error
   given the syndrome — has a structure where the correct solution has weight roughly `d/2` and
   incorrect solutions have weight much higher. The "signal" (correct correction) rises above
   the "noise" (incorrect corrections) efficiently.

3. **Statistical mechanical mapping**: Dennis et al. (2002) showed that decoding the surface
   code is equivalent to finding the ground state of a random-bond Ising model (RBIM). The
   threshold coincides with the phase transition temperature of the RBIM, known from statistical
   mechanics to be high.

### Circuit-Level Noise

In practice, syndrome measurement qubits (ancillas) are themselves noisy. A single round of
syndrome measurement uses a 4-qubit Hadamard + CNOT circuit per stabilizer. Ancilla errors can
create false syndromes.

The solution: perform **multiple rounds** of syndrome measurement (at least `d` rounds) and
decode in the full 2+1 dimensional spacetime picture. The threshold for circuit-level noise is
lower than the "data qubit only" threshold but still ≈1%.

---

## Minimum-Weight Perfect Matching (MWPM) Decoding

### The Decoding Problem

Given a syndrome (set of stabilizer violations = anyon positions), find the most likely error
that produced it. Since errors create anyons in pairs, the syndrome consists of an even number
of violated stabilizers. The correction should be a string connecting paired anyons.

**MWPM formulation**: Given anyons at positions `{a₁, a₂, ..., a_{2m}}`, find a perfect
matching (pairing of all anyons) that minimizes the total string length (weight).

This is the **minimum-weight perfect matching** problem, solvable by Edmonds' blossom algorithm
in `O(n³)` time (for `n` anyons) or `O(n)` in practice for sparse syndrome data.

### Matching Graph

Construct a complete graph where:
- Nodes are the syndrome defects (violated stabilizers) plus virtual boundary nodes.
- Edge weights are the log-likelihood of the error corresponding to that string (for uniform
  error rate `p`, proportional to length).

The MWPM finds the lowest-weight matching, which corresponds to the maximum-likelihood correction
when errors are independent.

### Decoding Failure

Decoding fails when the error creates a logical operator, i.e., the error chain crosses the
lattice. For a random error pattern with rate `p`, the probability of a logical error scales as:

```
p_L ≈ A · (p/p_th)^{⌈d/2⌉}
```

Below threshold (`p < p_th`), larger `d` gives exponentially smaller `p_L`. This is the
fundamental reason to use large surface codes.

### Space-Time Decoding

For `d` rounds of syndrome measurement, the syndrome is a `d × d × d` 3D binary array (two
spatial dimensions, one time dimension). MWPM now matches defects in this 3D syndrome graph.
The time dimension introduces vertical edges (connecting the same spatial location at successive
times) with weight determined by the measurement error probability.

---

## Resource Estimates

### Physical Qubits per Logical Qubit

For a distance-`d` surface code with data error rate `p_data` and measurement error rate
`p_meas`, the logical error rate per logical gate is approximately:

```
p_L ≈ 0.1 · (p / p_th)^{⌈d/2⌉}
```

For physical error rate `p = 10^{-3}` and threshold `p_th = 10^{-2}` (so `p/p_th = 0.1` and
`⌈d/2⌉ = (d+1)/2` for odd `d`):

| Distance `d` | Data qubits (`d²`) | `p_L` per logical gate |
|-------------|----------------|----------------------|
| 3  | 9   | ~10^{-3}  |
| 5  | 25  | ~10^{-4} |
| 7  | 49  | ~10^{-5}  |
| 11 | 121 | ~10^{-7}  |
| 17 | 289 | ~10^{-10} |
| 21 | 441 | ~10^{-12} |
| 25 | 625 | ~10^{-14} |

For fault-tolerant Shor's algorithm on RSA-2048 (requiring ~`10^8` T gates on ~2,000 logical
qubits), the logical error rate per gate must be ~`10^{-12}`. This requires `d ≈ 21`, hence
~`441 × 4000 ≈ 1.8 × 10^6` physical qubits (data plus ancillas) for the logical registers
alone, not counting magic state distillation factories. Total estimates: `10^6` to `10^7`
physical qubits.

---

## Key Formulas

- **Surface code parameters**: `[[d², 1, d]]` for the rotated lattice (the `2d² - 1` figure
  counts physical hardware qubits including the `d² - 1` measurement ancillas, which are not
  part of the code block); `[[2d²-2d+1, 1, d]]` for the unrotated planar layout
- **Stabilizers**: X-stars `A_v = ⊗_{j ∈ star(v)} X_j`, Z-plaquettes `B_f = ⊗_{j ∈ ∂f} Z_j`
  (on the rotated lattice both types become 4-qubit plaquettes in a checkerboard pattern)
- **Logical operators**: weight-`d` strings crossing the lattice
- **Threshold**: `p_th ≈ 1%` (circuit-level depolarizing noise; MWPM decoding)
- **Logical error rate**: `p_L ≈ C(p/p_th)^{⌈d/2⌉}`
- **MWPM**: solve minimum-weight perfect matching on syndrome defect graph

---

## Worked Example: d=3 Surface Code Error Correction

**Setup.** Use a distance-3 (9 data qubit) rotated surface code. The stabilizers are four
X-type and four Z-type checkerboard plaquettes (8 total for 9 qubits, encoding 1 logical
qubit).

**Error**: X error on data qubit at position (2,2) (center qubit).

**Syndrome**: The X error anticommutes with Z stabilizers that include qubit (2,2). In a d=3
surface code, the center qubit is in two Z-stabilizer plaquettes. Both Z stabilizers at those
positions flip to `-1`.

**Syndrome pattern**: Two adjacent Z-stabilizer violations at the two plaquettes bordering
qubit (2,2).

**MWPM decoding**: Two violated Z stabilizers separated by distance 1. The minimum-weight
matching connects them with a string of length 1 through qubit (2,2). Decoder outputs: apply
`X` at qubit (2,2).

**Result**: `X · X = I` at qubit (2,2). Logical state unchanged. ✓

**Decoding failure scenario** (illustration): Let `q₁, q₂, q₃` be the three qubits of a
horizontal line whose product `X_{q₁}X_{q₂}X_{q₃}` is the logical `X̄` (a string connecting
the two X-type boundaries). Suppose X errors strike `q₁` and `q₂`. Where two error-string
segments meet, their syndrome contributions cancel: the Z-stabilizer between `q₁` and `q₂`
sees two errors and stays `+1`. The visible syndrome is a single defect at the Z-stabilizer
between `q₂` and `q₃` (the string's other endpoint, at `q₁`, terminates on the boundary and
produces no defect). The decoder now has two candidate matchings: connect the defect to the
*near* boundary through `q₃` (weight 1), or to the *far* boundary through `q₂` and `q₁`
(weight 2). MWPM picks the lighter one and applies `X_{q₃}` — completing
`X_{q₁}X_{q₂}X_{q₃} = X̄`, a logical error. This is the correct (maximum-likelihood) decision
that nonetheless fails: two errors exceed the `⌊(d-1)/2⌋ = 1` guarantee of a distance-3 code.
The threshold is the error rate below which such multi-error patterns become negligible as
`d` grows.

---

## Summary

- The surface code `[[d², 1, d]]` encodes 1 logical qubit in a `d×d` array of physical qubits
  using only nearest-neighbor interactions on a 2D planar grid.
- Z-plaquette stabilizers detect bit-flip errors and X-vertex (star) stabilizers detect
  phase-flip errors; logical operators are weight-`d` strings connecting opposite boundaries.
- The ~1% threshold is the highest among local 2D codes, arising from the code's mapping to a
  statistical mechanical phase transition.
- MWPM decoding treats syndrome defects as anyon pairs and finds minimum-weight correction;
  polynomial time classical algorithm.
- Resource estimates: ~300-1000 physical qubits per logical qubit at physical error rate 0.1%;
  ~10^6-10^7 physical qubits for RSA-breaking algorithms.

---

## Exercises

**Exercise 1.** For the toric code with `L = 3`, count: the number of data qubits, the number
of independent stabilizer generators, and the number of logical qubits. Write the resulting
`[[n, k, d]]` parameters.

<details><summary>Solution</summary>

Data qubits: `2L² = 18` (one per edge). Star operators: `L² = 9`, but `∏_v A_v = I` removes
one, leaving 8 independent; likewise 8 independent plaquette operators. Total independent
generators: `16`. Logical qubits: `k = n - (generators) = 18 - 16 = 2`. Distance: the shortest
non-contractible loop has length `L = 3`. Parameters: `[[18, 2, 3]]`.

</details>

**Exercise 2.** A distance-5 rotated surface code runs at physical error rate `p = 10^{-3}`
with `p_th = 10^{-2}`. Count its data qubits, ancilla qubits, and total physical qubits, and
estimate `p_L` using `p_L ≈ 0.1 (p/p_th)^{⌈d/2⌉}`.

<details><summary>Solution</summary>

Data: `d² = 25`. Stabilizers/ancillas: `d² - 1 = 24` (12 X-type, 12 Z-type). Total: `2d² - 1
= 49` physical qubits. Logical error rate: `⌈5/2⌉ = 3`, so `p_L ≈ 0.1 × (0.1)³ = 10^{-4}` —
roughly a 10× improvement over the bare physical error rate per operation.

</details>

**Exercise 3.** Explain why a connected chain of X errors in the bulk produces syndrome
defects only at its two endpoints, no matter how long the chain is.

<details><summary>Solution</summary>

A Z-stabilizer anticommutes with an X-error chain iff their shared support has odd size. For
a stabilizer in the *interior* of the chain, the chain enters and exits its support: it shares
exactly 2 qubits (even) → no defect. Only at the two chain endpoints does a Z-stabilizer share
exactly 1 qubit (odd) with the chain → defect. Hence errors act like strings whose endpoints
are the observable "anyons"; the error's interior path is invisible, which is also why any
correction chain with the same endpoints and the same homology class works equally well.

</details>

**Exercise 4.** Using `p_L ≈ 0.1 (p/p_th)^{(d+1)/2}` at `p/p_th = 0.1`, find the smallest odd
distance achieving `p_L ≤ 10^{-15}`, and the corresponding physical qubit count (rotated
layout, including ancillas).

<details><summary>Solution</summary>

Need `0.1 × 10^{-(d+1)/2} ≤ 10^{-15}`, i.e. `(d+1)/2 ≥ 14`, so `d = 27`. Check:
`0.1 × 10^{-14} = 10^{-15}` ✓. Qubit count: `d² = 729` data qubits plus `d² - 1 = 728`
ancillas = `1457` physical qubits for a single logical qubit at this fidelity.

</details>

**Exercise 5.** In the toric code, every error pattern produces an even number of syndrome
defects, yet in the planar surface code an odd number of defects is routinely observed.
Reconcile these facts, and explain what MWPM does differently in the planar case.

<details><summary>Solution</summary>

On the torus, error chains are closed-support-free: every chain has two endpoints and each
endpoint creates one defect, so defects come in pairs (total count even). In the planar code,
a chain may *terminate on a boundary*: a string ending on the appropriate boundary type has
only one interior endpoint, contributing a single defect. MWPM handles this by adding a
virtual boundary node for each real defect (edge weight = distance to the nearest compatible
boundary); defects may then be matched either to each other or to the boundary, and the
virtual nodes are matched among themselves at zero cost to keep the matching perfect.

</details>

---

## Further Reading

1. **Kitaev, A. Yu.** — "Fault-tolerant quantum computation by anyons," *Ann. Phys.* 303, 2 (2003).
   arXiv:quant-ph/9707021. Original toric code paper.
1. **Bravyi, S. B. and Kitaev, A. Yu.** — "Quantum codes on a lattice with boundary,"
   arXiv:quant-ph/9811052 (1998). Introduces the planar surface code with boundaries.
2. **Dennis, E. et al.** — "Topological quantum memory," *J. Math. Phys.* 43, 4452 (2002).
   Establishes the 1% threshold; RBIM mapping.
3. **Fowler, A. G. et al.** — "Surface codes: Towards practical large-scale quantum computation,"
   *Phys. Rev. A* 86, 032324 (2012). Comprehensive surface code review and resource estimation.
4. **Edmonds, J.** — "Paths, trees, and flowers," *Canad. J. Math.* 17, 449 (1965). The MWPM
   blossom algorithm.
5. **Bravyi, S. and Haah, J.** — "Magic state distillation with low overhead," *Phys. Rev. A*
   86, 052329 (2012). Improved resource estimates for surface code + distillation.
