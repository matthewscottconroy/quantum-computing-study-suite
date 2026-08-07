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
matching) that scales polynomially. Every major quantum computing company — Google, IBM, Microsoft,
IonQ — has surface code implementations or surface code-inspired designs at the center of their
error correction roadmaps.

The surface code originates from Kitaev's toric code (1997), defined on a torus for theoretical
elegance, then modified by Freedman and Hastings to a planar geometry with boundaries. The
planar "surface code" is what appears in experiments, since building a torus in hardware is
impractical.

This chapter develops the surface code from the lattice geometry, defines the stabilizers and
logical operators, explains the threshold and why it is so high, and describes minimum-weight
perfect matching (MWPM) decoding. We include resource estimates for practical quantum advantage.

---

## The Toric Code: Conceptual Foundation

### Lattice and Qubits

Place `L×L` qubits on the edges of an `L×L` square lattice drawn on a torus. There are `2L²`
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

**Qubits**: Place data qubits on edges of the grid. For a distance-`d` code:
- `d² + (d-1)² = 2d² - 2d + 1` data qubits in the full surface code geometry,
- Often described more simply as `d²` data qubits with `d²-1` ancilla qubits for syndrome
  measurement, totaling `2d²-1` physical qubits.

A common, slightly simplified description: `d` rows × `d` columns = `d²` data qubits, with
`(d-1)²` Z-plaquette stabilizers and `d(d-1)/2 + ... = d²-1` combined stabilizer qubits.

For simplicity we use the rotated surface code geometry (Bombin-Delgado-Martin 2007; Fowler 2012):
**`d²` data qubits**, `(d²-1)/2` X-ancillas, `(d²-1)/2` Z-ancillas (for odd `d`), encoding
**1 logical qubit** with distance `d`.

### Stabilizers of the Planar Surface Code

In the rotated (tilted) lattice representation:

**X stabilizers (plaquettes)**: each X stabilizer acts on 4 (or 2 at boundaries) data qubits
with X.

**Z stabilizers (vertices)**: each Z stabilizer acts on 4 (or 2 at boundaries) data qubits
with Z.

The number of independent stabilizers is `d² - 1` (since the product of all same-type stabilizers
is identity on the boundary), giving code space dimension `2^{d²-(d²-1)} = 2^1 = 2`, encoding
1 logical qubit. ✓

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

For physical error rate `p = 10^{-3}` and threshold `p_th = 10^{-2}`:

| Distance `d` | Physical qubits | `p_L` per logical gate |
|-------------|----------------|----------------------|
| 3  | 9   | ~10^{-3}  |
| 5  | 25  | ~10^{-4.5} |
| 7  | 49  | ~10^{-6}  |
| 11 | 121 | ~10^{-9}  |
| 17 | 289 | ~10^{-14} |
| 25 | 625 | ~10^{-20} |

For fault-tolerant Shor's algorithm on RSA-2048 (requiring ~`10^8` T gates on ~2,000 logical
qubits), logical error rate per gate must be ~`10^{-12}`. This requires `d ≈ 17`, hence
~`289 × 4000` ~ `10^6` physical qubits minimum, not counting magic state distillation factories.
Total estimates: `10^6` to `10^7` physical qubits.

---

## Key Formulas

- **Surface code parameters**: `[[d², 1, d]]` (rotated lattice; more precisely `[[2d²-1,1,d]]`)
- **Stabilizers**: X-plaquettes `A_p = ⊗_{j ∈ p} X_j`, Z-vertices `B_v = ⊗_{j ∈ v} Z_j`
- **Logical operators**: weight-`d` strings crossing the lattice
- **Threshold**: `p_th ≈ 1%` (circuit-level depolarizing noise; MWPM decoding)
- **Logical error rate**: `p_L ≈ C(p/p_th)^{⌈d/2⌉}`
- **MWPM**: solve minimum-weight perfect matching on syndrome defect graph

---

## Worked Example: d=3 Surface Code Error Correction

**Setup.** Use a distance-3 (9 data qubit) rotated surface code. The stabilizers are four
X-plaquettes and four Z-vertices (8 total for 9 qubits, encoding 1 logical qubit).

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

**Decoding failure scenario** (illustration): Suppose X errors occur on all 3 qubits in the
top row. The syndromes at the plaquettes between those qubits cancel out (each qubit creates two
syndrome violations, which pair and annihilate with adjacent violations). The syndrome appears
as two violations at the boundary. The decoder matches them through the interior (short path,
correct) — or through the boundary (also short path). If it chooses through the interior, it
applies 1 correction; the remaining 2-qubit error creates a logical error (horizontal string of
length 3 = logical operator). If it goes through the boundary, no error propagates. The threshold
corresponds to the crossover where correct decoding probability = 0.5.

---

## Summary

- The surface code `[[d², 1, d]]` encodes 1 logical qubit in a `d×d` array of physical qubits
  using only nearest-neighbor interactions on a 2D planar grid.
- X-plaquette and Z-vertex stabilizers detect bit-flip and phase-flip errors respectively;
  logical operators are weight-`d` strings connecting opposite boundaries.
- The ~1% threshold is the highest among local 2D codes, arising from the code's mapping to a
  statistical mechanical phase transition.
- MWPM decoding treats syndrome defects as anyon pairs and finds minimum-weight correction;
  polynomial time classical algorithm.
- Resource estimates: ~300-1000 physical qubits per logical qubit at physical error rate 0.1%;
  ~10^6-10^7 physical qubits for RSA-breaking algorithms.

---

## Further Reading

1. **Kitaev, A. Yu.** — "Fault-tolerant quantum computation by anyons," *Ann. Phys.* 303, 2 (2003).
   arXiv:quant-ph/9707021. Original toric code paper.
2. **Dennis, E. et al.** — "Topological quantum memory," *J. Math. Phys.* 43, 4452 (2002).
   Establishes the 1% threshold; RBIM mapping.
3. **Fowler, A. G. et al.** — "Surface codes: Towards practical large-scale quantum computation,"
   *Phys. Rev. A* 86, 032324 (2012). Comprehensive surface code review and resource estimation.
4. **Edmonds, J.** — "Paths, trees, and flowers," *Canad. J. Math.* 17, 449 (1965). The MWPM
   blossom algorithm.
5. **Bravyi, S. and Haah, J.** — "Magic state distillation with low overhead," *Phys. Rev. A*
   86, 052329 (2012). Improved resource estimates for surface code + distillation.
