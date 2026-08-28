# Classical Error Correction

> **Prerequisites**: Linear algebra over fields (Chapter 1), modular arithmetic basics
> **Connects to**: CSS codes (05/05), stabilizer formalism (05/04) — CSS codes are the direct
> quantum generalization of the classical linear code construction here

---

## Overview

Classical error correction is not merely background material — it is the direct ancestor of the
most powerful quantum codes. The Calderbank-Shor-Steane (CSS) construction that yields the
Steane [[7,1,3]] code and underlies surface code variants takes two classical linear codes and
combines them in a specific way. To understand that construction, one must first understand
linear codes over the binary field, parity-check matrices, the dual code, and the significance
of self-orthogonality.

Beyond the CSS connection, classical coding theory provides the conceptual vocabulary — Hamming
distance, minimum distance, the error-correction capacity formula, Shannon capacity — that
quantum coding theory inherits and generalizes. Many results in quantum coding have exact
classical analogues, and the deviations from classical behavior reveal what is distinctively
quantum about QEC.

This chapter treats classical error correction at the level of a first graduate course in
information theory. We develop linear codes over GF(2) from scratch, work out the [7,4,3]
Hamming code in detail, discuss Shannon's capacity theorem qualitatively, and identify precisely
which classical properties survive quantization.

---

## The Basic Setup: Channels, Codes, and Distance

### Binary Symmetric Channel

The simplest classical noise model is the **binary symmetric channel (BSC)**: each transmitted
bit is flipped independently with probability `p`, and passes through unchanged with probability
`1-p`. For `p < 1/2`, the channel is useful.

An `[n, k, d]` **binary linear code** `C` maps `k` information bits to `n` codewords via a
linear map (the **encoder**), such that any two distinct codewords differ in at least `d` bit
positions. The integer `d` is the **minimum Hamming distance** of the code.

### Hamming Distance

The **Hamming distance** `d_H(u, v)` between two binary strings `u` and `v` of equal length is
the number of positions where they differ:

```
d_H(u, v) = |{i : u_i ≠ v_i}|  =  wt(u ⊕ v)
```

where `wt(x)` is the **Hamming weight** (number of 1s) of `x`, and `⊕` is bitwise XOR (addition
mod 2).

For a linear code, the minimum distance equals the minimum weight of any non-zero codeword,
because `d_H(c₁, c₂) = wt(c₁ ⊕ c₂) = wt(c₃)` where `c₃ = c₁ ⊕ c₂` is also a codeword
(by linearity).

### Error Detection and Correction Capacity

A code with minimum distance `d` can:

- **Detect** up to `d - 1` errors: any pattern of at most `d-1` errors moves a codeword to a
  non-codeword, which the receiver can recognize as invalid.
- **Correct** up to `t = ⌊(d-1)/2⌋` errors: the Hamming balls of radius `t` around distinct
  codewords are disjoint, so a received word is unambiguously decoded to the nearest codeword.

**Proof of correction capacity.** Suppose codewords `c₁` and `c₂` satisfy `d_H(c₁, c₂) ≥ d`.
If `y` is within Hamming distance `t` of `c₁`, then its distance to `c₂` is at least
`d - t ≥ d - ⌊(d-1)/2⌋ = ⌈(d+1)/2⌉ > t`. So `y` is not within distance `t` of any other
codeword. QED.

---

## Linear Codes over GF(2)

### Generator Matrix

A linear code `C ⊆ {0,1}^n` of dimension `k` is specified by a **generator matrix**
`G ∈ {0,1}^{k×n}` whose rows are a basis for `C`. Every codeword is a linear combination
(over GF(2)) of the rows:

```
c = m G   (row vector notation)
```

where `m ∈ {0,1}^k` is the `k`-bit message. The code has `2^k` codewords.

### Parity-Check Matrix

The **parity-check matrix** `H ∈ {0,1}^{(n-k)×n}` is a matrix whose row space is orthogonal to
`C`. A vector `v` is a codeword if and only if `H vᵀ = 0`. Equivalently, in row-vector notation:

```
c ∈ C  ⟺  c Hᵀ = 0
```

The rows of `H` and the rows of `G` satisfy `G Hᵀ = 0` (over GF(2)).

### Syndrome Decoding

When a codeword `c` is transmitted and error vector `e` is added (in GF(2)), the receiver gets
`y = c ⊕ e`. The **syndrome** of `y` is:

```
s = H yᵀ = H(c ⊕ e)ᵀ = H cᵀ ⊕ H eᵀ = 0 ⊕ H eᵀ = H eᵀ
```

The syndrome depends only on the error `e`, not the transmitted codeword `c`. A pre-computed
**syndrome table** maps each correctable syndrome `s` to the most likely error pattern `e(s)`,
and the corrected word is `y ⊕ e(s) = c`.

This structure — syndrome encodes only the error, not the data — is the direct template for
quantum syndrome measurement.

---

## The [7, 4, 3] Hamming Code

The **Hamming code** is the textbook example of a perfect single-error-correcting code. The
`[7, 4, 3]` variant is especially important because it is the classical code underlying the
Steane [[7,1,3]] quantum code.

### Parity-Check Matrix

```
H = | 0 0 0 1 1 1 1 |
    | 0 1 1 0 0 1 1 |
    | 1 0 1 0 1 0 1 |
```

The columns of `H` are the binary representations of the integers 1 through 7. This elegant
structure means the syndrome `s = H eᵀ` directly gives the binary address of the error bit:
if `s = (0,1,1)ᵀ`, interpreted as binary `011 = 3`, bit position 3 is in error.

### Generator Matrix

The code has dimension 4, so `G` is a `4×7` matrix. In systematic form `[I_k | P]`:

```
G = | 1 0 0 0 | 0 1 1 |
    | 0 1 0 0 | 1 0 1 |
    | 0 0 1 0 | 1 1 0 |
    | 0 0 0 1 | 1 1 1 |
```

(The rightmost three columns are the parity checks; exact form depends on column ordering.)

### Properties

- **Minimum distance**: `d = 3` (can correct 1 error, detect 2 errors).
- **Perfect code**: the Hamming balls of radius 1 around the 16 codewords (`2^4 = 16`), each
  containing `1 + 7 = 8` strings, exactly partition all `2^7 = 128` binary strings of length 7:
  `16 × 8 = 128`. ✓
- **Rate**: `k/n = 4/7 ≈ 0.571`.

### Syndrome Decoding Worked Out

A message `m = (1,0,1,1)` encodes to:
```
c = m G = (1,0,1,1,0,1,0)   (computation over GF(2))
```
Suppose bit 5 is flipped: `y = (1,0,1,1,1,1,0)`.

```
s = H yᵀ = (0+0+1+1+1+1+0, 0+0+1+0+0+1+0, 1+0+1+0+1+0+0)
          = (1, 0, 1) over GF(2)
```
Binary `101 = 5`. Flip bit 5: `y ⊕ e₅ = (1,0,1,1,0,1,0) = c`. Correct.

---

## The Dual Code and Self-Orthogonality

### Dual Code

The **dual code** `C⊥` of a linear code `C ⊆ {0,1}^n` is the code whose codewords are
orthogonal (in the GF(2) inner product `⟨u,v⟩ = Σᵢ uᵢvᵢ mod 2`) to all codewords of `C`:

```
C⊥ = {v ∈ {0,1}^n : ⟨u, v⟩ = 0 for all u ∈ C}
```

If `C = [n, k, d]`, then `C⊥ = [n, n-k, d⊥]` for some dual distance `d⊥`.

The generator matrix of `C⊥` is the parity-check matrix of `C`, and vice versa.

### Self-Orthogonal and Self-Dual Codes

A code `C` is **self-orthogonal** (also called weakly self-dual) if `C ⊆ C⊥`. This means every
codeword is orthogonal to every other codeword (and to itself). Equivalently:

```
G Gᵀ = 0  (over GF(2))
```

A code is **self-dual** if `C = C⊥`, which requires `n = 2k`.

The [7,4,3] Hamming code `C` is **not** self-orthogonal: `C ⊆ C⊥` is impossible on dimension
grounds alone, since `dim C = 4 > 3 = dim C⊥`. What *is* true — and what enables the Steane
construction — is the reverse inclusion: `C⊥ ⊆ C`. The dual `C⊥` is the `[7,3,4]` simplex
code, and every row of `H` (a generator of `C⊥`) is itself a Hamming codeword, which one checks
via `H Hᵀ = 0` over GF(2). A code containing its dual is called **dual-containing**;
equivalently, its dual `C⊥` is self-orthogonal (`C⊥ ⊆ (C⊥)⊥ = C`).

For the CSS quantum code construction, one needs two codes `C₁` and `C₂` with `C₂ ⊆ C₁`.
The Steane code takes `C₁ = C = [7,4,3]` and `C₂ = C⊥ = [7,3,4]`; the dual-containing
property `C⊥ ⊆ C` is exactly the required inclusion. See Chapter 05/05 for the full
construction.

---

## Shannon's Capacity Theorem

Claude Shannon's 1948 theorem gives the fundamental limit on communication over a noisy channel.

**Theorem (Shannon, 1948).** For a channel with capacity `C` bits per channel use, there exist
codes achieving reliable communication at any rate `R < C`. No reliable communication is possible
at rate `R > C`.

For the BSC with flip probability `p`:

```
C_BSC = 1 - H₂(p) = 1 - [-p log₂(p) - (1-p) log₂(1-p)]
```

where `H₂(p)` is the binary entropy function. At `p = 0`: `C = 1` (perfect channel). At
`p = 0.5`: `C = 0` (useless channel). At `p = 0.1`: `C ≈ 0.531` bits per use.

Shannon's theorem is an existence theorem — it guarantees good codes exist but does not construct
them. The search for capacity-achieving codes that are also computationally efficient (polynomial
time encoding and decoding) drove coding theory for 50 years, culminating in turbo codes (Berrou,
1993) and LDPC codes (Gallager, 1962; rediscovered 1996).

### Quantum Analogue

The quantum analogue of Shannon's capacity theorem is the **quantum capacity** (or hashing bound)
for quantum channels, discussed in Chapter 08/02. The key difference: a quantum channel can
transmit classical information, quantum information, or entanglement, and these capacities are
not simply related.

---

## What Survives in Quantum Codes

| Classical feature | Quantum analogue |
|---|---|
| Codewords as subspaces | Codewords as subspaces of Hilbert space |
| Parity-check matrix `H` | Stabilizer group generators |
| Syndrome `s = Heᵀ` | Syndrome (eigenvalue pattern of stabilizer measurements) |
| Dual code `C⊥` | Normalizer of stabilizer group |
| Self-orthogonality `C ⊆ C⊥` | Commutativity of CSS stabilizers |
| [7,4,3] Hamming code | Steane [[7,1,3]] quantum code |

---

## Key Formulas

- **Hamming distance**: `d_H(u,v) = wt(u ⊕ v)`
- **Error correction capacity**: a `[n,k,d]` code corrects `t = ⌊(d-1)/2⌋` errors
- **Syndrome**: `s = H eᵀ` (depends only on error, not on codeword)
- **Dual code**: `C⊥ = {v : ⟨u,v⟩ = 0 ∀ u ∈ C}`; generator of `C⊥` = parity check of `C`
- **BSC capacity**: `C = 1 - H₂(p) = 1 + p log₂ p + (1-p) log₂(1-p)`
- **Self-orthogonality**: `C ⊆ C⊥` iff `G Gᵀ = 0` over GF(2)

---

## Worked Example: Full Syndrome Decode of [7,4,3]

**Setting up the problem.** Alice sends the 4-bit message `m = (1,1,0,1)` using the [7,4,3]
Hamming code. Bob receives `y = (1,1,1,1,0,0,1)`. Was there an error, and if so, where?

**Step 1: Compute parity-check matrix H.**
```
H = | 0 0 0 1 1 1 1 |   (row 1: columns 4,5,6,7 marked)
    | 0 1 1 0 0 1 1 |   (row 2: columns 2,3,6,7 marked)
    | 1 0 1 0 1 0 1 |   (row 3: columns 1,3,5,7 marked)
```

**Step 2: Compute syndrome.**
`y = (y₁,...,y₇) = (1,1,1,1,0,0,1)`

```
s₁ = 0·y₁+0·y₂+0·y₃+1·y₄+1·y₅+1·y₆+1·y₇ = 0+0+0+1+0+0+1 = 0 (mod 2)
s₂ = 0·y₁+1·y₂+1·y₃+0·y₄+0·y₅+1·y₆+1·y₇ = 0+1+1+0+0+0+1 = 1 (mod 2)
s₃ = 1·y₁+0·y₂+1·y₃+0·y₄+1·y₅+0·y₆+1·y₇ = 1+0+1+0+0+0+1 = 1 (mod 2)
```

Syndrome `s = (0,1,1)`. Binary `011 = 3`. Bit 3 is in error.

**Step 3: Correct.**
Flip bit 3: `c = (1,1,0,1,0,0,1)`. This is the transmitted codeword.

**Step 4: Verify.**
Decode `c` to message: first 4 bits in systematic form: `m = (1,1,0,1)`. ✓ (Alice's message.)

---

## Summary

- Linear codes over GF(2) encode `k` bits into `n` bits with redundancy that allows correction
  of `t = ⌊(d-1)/2⌋` errors.
- The parity-check matrix `H` generates syndromes that depend only on the error, not the data.
- The [7,4,3] Hamming code corrects all single-bit errors with an elegant syndrome → error
  position mapping.
- The dual code `C⊥` and the dual-containing property (`C⊥ ⊆ C`) are prerequisites for the CSS
  quantum code construction.
- Shannon's capacity theorem gives the fundamental information-theoretic limits; quantum
  analogues (channel capacity, hashing bound) are studied in Chapter 8.
- The syndrome paradigm — measure correlations, not data — is the classical prototype for
  quantum stabilizer syndrome measurement.

---

## Exercises

**Exercise 1.** Encode the message `m = (0,1,1,0)` with the generator matrix `G` given in this
chapter. The channel flips bit 7 of the transmitted codeword. Compute the received word, the
syndrome, and verify that syndrome decoding recovers the transmitted codeword.

<details><summary>Solution</summary>

`c = m G` = row 2 + row 3 of `G` = `(0,1,0,0,1,0,1) ⊕ (0,0,1,0,1,1,0) = (0,1,1,0,0,1,1)`.
Flipping bit 7 gives `y = (0,1,1,0,0,1,0)`. Syndrome:
`s₁ = y₄+y₅+y₆+y₇ = 0+0+1+0 = 1`, `s₂ = y₂+y₃+y₆+y₇ = 1+1+1+0 = 1`,
`s₃ = y₁+y₃+y₅+y₇ = 0+1+0+0 = 1`. So `s = (1,1,1)`, binary `111 = 7`: bit 7 is flagged.
Flipping bit 7 of `y` returns `(0,1,1,0,0,1,1) = c`. ✓

</details>

**Exercise 2.** A code can *simultaneously* correct up to `t` errors and detect up to `s ≥ t`
errors if and only if `d ≥ t + s + 1`. Prove the "if" direction, and use it to show that a
distance-4 code can correct any single error while also detecting any double error.

<details><summary>Solution</summary>

Decode as follows: if the received word `y` lies within distance `t` of some codeword, correct
to it; otherwise declare "error detected." Suppose `c` was sent and at most `s` errors occurred.
If at most `t` errors occurred, `y` is within `t` of `c`; `y` cannot also be within `t` of
another codeword `c'`, since then `d(c, c') ≤ t + t ≤ t + s < d`. So correction is right.
If between `t+1` and `s` errors occurred, `y` cannot be within `t` of any codeword `c'≠ c`
(that would need `d(c,c') ≤ s + t < d`), so the decoder correctly reports detection rather than
miscorrecting. For `d = 4`: choosing `t = 1, s = 2` satisfies `4 ≥ 1 + 2 + 1`, so single-error
correction plus double-error detection is achievable — the extended Hamming code `[8,4,4]` is
used exactly this way.

</details>

**Exercise 3.** Show by direct computation that every non-zero codeword of the `[7,3,4]`
simplex code `C⊥` (the dual of the `[7,4,3]` Hamming code) has weight exactly 4. Use the rows
of `H` as the generator.

<details><summary>Solution</summary>

The 7 non-zero codewords are the non-empty GF(2) combinations of
`r₁ = 0001111`, `r₂ = 0110011`, `r₃ = 1010101`:

```
r₁ = 0001111 (wt 4)      r₁⊕r₂ = 0111100 (wt 4)
r₂ = 0110011 (wt 4)      r₁⊕r₃ = 1011010 (wt 4)
r₃ = 1010101 (wt 4)      r₂⊕r₃ = 1100110 (wt 4)
                          r₁⊕r₂⊕r₃ = 1101001 (wt 4)
```

All 7 have weight 4, so `C⊥` is a constant-weight (simplex) code with `d⊥ = 4`. This also
confirms `C⊥` is self-orthogonal: any two weight-4 codewords here overlap in an even number
of positions.

</details>

**Exercise 4.** Use the Hamming bound (sphere-packing bound) `2^k · Σ_{i=0}^{t} C(n,i) ≤ 2^n`
to prove that no binary `[10, 7, 3]` code exists. Would a `[10, 6, 3]` code violate the bound?

<details><summary>Solution</summary>

For `d = 3` (so `t = 1`), a `[10,7]` code would need `2^7 · (1 + 10) = 128 × 11 = 1408 ≤ 2^{10}
= 1024`. This fails, so no `[10,7,3]` code exists. For `[10,6,3]`: `2^6 × 11 = 704 ≤ 1024`
holds, so the bound does not rule it out (and indeed `[10,6,3]` codes exist, e.g. a shortened
Hamming code).

</details>

**Exercise 5.** Compute the BSC capacity at flip probability `p = 0.11` and comment on the
result.

<details><summary>Solution</summary>

`H₂(0.11) = -0.11 log₂ 0.11 - 0.89 log₂ 0.89 ≈ 0.11 × 3.184 + 0.89 × 0.168 ≈ 0.350 + 0.150 =
0.500`. So `C = 1 - H₂(0.11) ≈ 0.500`: at an 11% flip rate, at most about half a bit of
information can be conveyed per channel use. (Coincidentally, `p ≈ 11%` is also close to the
optimal-decoder code-capacity threshold of the surface code under independent bit-flip noise —
a manifestation of the same information-theoretic limit.)

</details>

---

## Further Reading

1. **MacWilliams, F. J. and Sloane, N. J. A.** — *The Theory of Error-Correcting Codes*,
   North-Holland, 1977. The comprehensive reference for classical coding theory.
2. **Lin, S. and Costello, D. J.** — *Error Control Coding*, Pearson, 2nd ed., 2004. More
   engineering-oriented but thorough on linear codes.
3. **Shannon, C. E.** — "A mathematical theory of communication," *Bell System Technical Journal*
   27, 379–423 (1948). The foundational paper.
4. **Calderbank, A. R. and Shor, P. W.** — "Good quantum error-correcting codes exist," *Phys.
   Rev. A* 54, 1098 (1996). Introduces CSS codes, directly uses the material in this chapter.
5. **Steane, A. M.** — "Multiple particle interference and quantum error correction," *Proc. R.
   Soc. Lond. A* 452, 2551 (1996). The other CSS paper; derives the [[7,1,3]] Steane code.
