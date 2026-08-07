# The Quantum Repetition Code

> **Prerequisites**: Qubits, Pauli operators, tensor products (Chapters 1–2), why QEC is hard
> (05/01), basic syndrome idea
> **Connects to**: Shor's 9-qubit code (this file), stabilizer formalism (05/04), CSS codes (05/05)

---

## Overview

The quantum repetition code is the simplest honest example of quantum error correction. It cannot
correct arbitrary single-qubit errors — it handles only bit-flip errors or only phase-flip errors,
not both simultaneously. Despite this limitation, it provides the clearest possible illustration
of syndrome measurement, the stabilizer group, and the construction of logical operators.
It also demonstrates explicitly why single-type codes fail and motivates the need for codes
that protect against the full Pauli group.

Peter Shor's 1995 breakthrough was to concatenate two repetition codes — one for bit flips,
one for phase flips — yielding the first complete quantum error-correcting code: the 9-qubit
Shor code. This construction is historically significant and conceptually illuminating, even
though more efficient codes (Steane's [[7,1,3]], the surface code) superseded it for practical
use.

This chapter develops the 3-qubit bit-flip code, the 3-qubit phase-flip code, and the 9-qubit
Shor code in careful detail. For each code, we specify the encoding circuit, stabilizer
generators, syndrome table, and recovery operations.

---

## Notation: [[n, k, d]]

A **quantum error-correcting code** `[[n, k, d]]` encodes `k` logical qubits into `n` physical
qubits with **distance** `d`. Distance `d` means the code can:
- **Detect** any error on up to `d-1` qubits.
- **Correct** any error on up to `t = ⌊(d-1)/2⌋` qubits.

"Any error on `t` qubits" means any combination of `I, X, Y, Z` on any set of `t` specific
qubits. The Pauli-decomposition miracle (Chapter 05/01) makes this precise.

---

## The 3-Qubit Bit-Flip Code [[3, 1, 1]]

### Encoding

The bit-flip code maps:
```
|0⟩ → |0_L⟩ = |000⟩
|1⟩ → |1_L⟩ = |111⟩
```

An arbitrary qubit `|ψ⟩ = α|0⟩ + β|1⟩` is encoded as:
```
|ψ_L⟩ = α|000⟩ + β|111⟩
```

**Encoding circuit**: Initialize ancillas `|00⟩`, then apply CNOT from logical qubit to each
ancilla:
```
CNOT_{1→2} · CNOT_{1→3} · |ψ⟩|00⟩ = α|000⟩ + β|111⟩
```

Note: this is NOT cloning. The superposition coefficients `α`, `β` are not copied — rather, the
*computational basis states* are copied via CNOT. The no-cloning theorem is not violated.

### Bit-Flip Error Model

Under independent bit-flip errors with probability `p`, the error probabilities are:
- No error: `(1-p)³ ≈ 1 - 3p`
- Single qubit `i` flipped: `p(1-p)² ≈ p` each (3 cases)
- Two qubits flipped: `p²(1-p) ≈ p²` each (3 cases)
- All three flipped: `p³`

For `p ≪ 1`, single-qubit errors dominate. The code corrects all weight-1 errors.

### Stabilizer Generators

The code space is stabilized by:
```
g₁ = Z₁Z₂    (qubits 1 and 2 have same Z-value)
g₂ = Z₂Z₃    (qubits 2 and 3 have same Z-value)
```

**Verification**: `g₁|000⟩ = |000⟩`, `g₁|111⟩ = |111⟩` (both eigenstates with eigenvalue +1).
So `g₁` (and `g₂`) stabilize the entire code space `{α|000⟩ + β|111⟩}`.

The stabilizer group is `S = {I, Z₁Z₂, Z₂Z₃, Z₁Z₃}` (closed under multiplication).

### Syndrome Measurement and Correction

| Error | `g₁ = Z₁Z₂` | `g₂ = Z₂Z₃` | Correction |
|-------|-------------|-------------|------------|
| None  | +1          | +1          | None (I)   |
| X₁    | -1          | +1          | X₁         |
| X₂    | -1          | -1          | X₂         |
| X₃    | +1          | -1          | X₃         |

Each single bit-flip gives a unique syndrome. After reading `(s₁, s₂) = (g₁, g₂)`, apply
the corresponding correction. The logical state `α|000⟩ + β|111⟩` is fully restored.

### Logical Operators

The **logical Z operator** `Z_L` must:
- Commute with all stabilizer generators.
- Have eigenvalue `+1` on `|0_L⟩ = |000⟩` and `-1` on `|1_L⟩ = |111⟩`.

Any of `Z₁, Z₂, Z₃` or their products `Z₁Z₂Z₃` work. The minimal choice is any single `Zᵢ`,
but the **dressed** logical operator `Z_L = Z₁Z₂Z₃` is preferable (minimum-weight representative
in the code's normalizer).

The **logical X operator** `X_L = X₁X₂X₃`: maps `|000⟩ → |111⟩` and vice versa.

### What the Bit-Flip Code Cannot Do

The code has no protection against **phase-flip errors** (`Z` errors). A `Z` on any qubit maps:
```
Z₁(α|000⟩ + β|111⟩) = α|000⟩ - β|111⟩
```
This changes the sign of `β` — a phase error on the logical qubit — but the syndrome
`(Z₁Z₂, Z₂Z₃)` gives `(+1, +1)`, the "no error" syndrome. The code is blind to Z errors.

---

## The 3-Qubit Phase-Flip Code

### Construction via Hadamard

The phase-flip code protects against `Z` errors using the Hadamard gate to rotate the error basis.
Recall `HZH = X` and `HXH = Z`. If we apply `H` to every qubit, bit flips become phase flips
and vice versa.

**Encoding**:
```
|0_L⟩ = |+++⟩ = (|0⟩+|1⟩)(|0⟩+|1⟩)(|0⟩+|1⟩) / 2√2
|1_L⟩ = |---⟩ = (|0⟩-|1⟩)(|0⟩-|1⟩)(|0⟩-|1⟩) / 2√2
```

where `|+⟩ = (|0⟩+|1⟩)/√2` and `|-⟩ = (|0⟩-|1⟩)/√2`.

Encoding circuit: first encode `|0⟩ → |+++⟩, |1⟩ → |---⟩` by applying H to a bit-flip
encoding:
```
|ψ_L⟩ = α|+++⟩ + β|---⟩
```

### Stabilizers for Phase-Flip Code

The stabilizers are:
```
g₁ = X₁X₂,   g₂ = X₂X₃
```

A Z error on qubit `i` anticommutes with `Xᵢ` and commutes with `Xⱼ` for `j ≠ i`, giving
a syndrome table symmetric with the bit-flip code table (Z and X swapped).

### Decoding Circuit

After syndrome measurement, apply `Z` correction to the appropriate qubit. The Hadamard
transformation that converts Z errors to X errors is already built into the code structure.

---

## Shor's 9-Qubit Code [[9, 1, 3]]

### The Key Idea: Concatenation

Neither the bit-flip nor the phase-flip repetition code alone corrects arbitrary single-qubit
errors. Shor's insight: use the phase-flip code to protect against Z errors *at the logical
level*, while using the bit-flip code to protect against X errors at the physical level.

**Concatenation**: encode one logical qubit in the phase-flip code (3 "macro-qubits"), then
encode each macro-qubit in the bit-flip code (3 physical qubits each). Total: 9 physical qubits.

### Codewords

```
|0_L⟩ = (|000⟩ + |111⟩)(|000⟩ + |111⟩)(|000⟩ + |111⟩) / 2√2
|1_L⟩ = (|000⟩ - |111⟩)(|000⟩ - |111⟩)(|000⟩ - |111⟩) / 2√2
```

Each factor `(|000⟩ ± |111⟩)/√2` is one "block" of 3 qubits (the bit-flip encoding of `|+⟩`
and `|-⟩` respectively).

### Stabilizer Generators

Label the 9 qubits as groups: block 1 = (1,2,3), block 2 = (4,5,6), block 3 = (7,8,9).

**Within-block Z stabilizers** (bit-flip protection, 6 generators):
```
Z₁Z₂,  Z₂Z₃,  Z₄Z₅,  Z₅Z₆,  Z₇Z₈,  Z₈Z₉
```

**Between-block X stabilizers** (phase-flip protection, 2 generators):
```
X₁X₂X₃X₄X₅X₆,   X₄X₅X₆X₇X₈X₉
```

Total: 8 generators for 8 = 9 - 1 syndrome bits. The code space is 2-dimensional (1 logical
qubit). ✓

### Error Correction Procedure

**Step 1 — Bit-flip correction**: measure the 6 Z-type syndrome operators. Each block's syndrome
(`Z_iZ_{i+1}`, `Z_{i+1}Z_{i+2}`) identifies a bit-flip within that block or signals no error.
Apply X corrections within each block as needed.

**Step 2 — Phase-flip correction**: measure the 2 X-type syndrome operators between blocks.
These detect whether blocks have acquired relative phase errors. Apply Z corrections to the
appropriate blocks.

After both steps, the logical state is restored.

### Why [[9,1,3]] Corrects All Single-Qubit Errors

Any single-qubit error decomposes as `E = eᵢI + eₓX + eᵧY + eᵤZ`. The syndrome measurement
projects this error onto one of `{I, X, Y, Z}` acting on the affected qubit. The Shor code
can correct:
- **X error** on any qubit: detected and corrected by within-block Z syndromes.
- **Z error** on any qubit: a Z error on qubit `i` flips the sign of one block, detected and
  corrected by between-block X syndromes.
- **Y = iXZ error**: both an X and Z correction are applied (independently). Since both
  corrections commute with the logical operators, the net effect is correct.
- **Identity (no error)**: all syndromes `+1`, no correction.

The minimum distance is `d = 3`: the minimum-weight logical operator is weight 3 (e.g., `X₁X₄X₇`
acting on one qubit per block), so any 1-qubit error is correctable.

---

## Resource Comparison

| Code | Physical qubits | Logical qubits | Distance | Corrects |
|------|----------------|---------------|---------|---------|
| [[3,1,1]] bit-flip | 3 | 1 | 1 | X errors only |
| [[3,1,1]] phase-flip | 3 | 1 | 1 | Z errors only |
| [[9,1,3]] Shor | 9 | 1 | 3 | All single-qubit |
| [[7,1,3]] Steane | 7 | 1 | 3 | All single-qubit |
| [[5,1,3]] Perfect | 5 | 1 | 3 | All single-qubit |

The 5-qubit "perfect" code achieves the quantum Hamming bound: `n ≥ 4t + 1` for correcting `t`
errors gives `n ≥ 5` for `t = 1`. Shor's 9-qubit code is not optimal but was the first proof
of principle.

---

## Key Formulas

- **Encoding**: `|0_L⟩ = |000⟩`, `|1_L⟩ = |111⟩` (bit-flip); `|0_L⟩ = |+++⟩`, `|1_L⟩ = |---⟩`
  (phase-flip)
- **Stabilizers (bit-flip)**: `g₁ = Z₁Z₂`, `g₂ = Z₂Z₃`
- **Stabilizers (phase-flip)**: `g₁ = X₁X₂`, `g₂ = X₂X₃`
- **Shor code word**:
  `|0_L⟩ = [(|000⟩+|111⟩)^⊗3] / 2√2`,
  `|1_L⟩ = [(|000⟩-|111⟩)^⊗3] / 2√2`
- **Syndrome-correction map**: unique syndrome `→` unique correctable error (for distance-3 code,
  all weight-1 errors are correctable)

---

## Worked Example: Y Error on Shor Code

**Setup.** The logical qubit is in state `|0_L⟩`. A Y error occurs on physical qubit 4.
`Y = iXZ`, so effectively both an X and a Z error occur on qubit 4.

**X component (qubit 4 is in block 2, position 1):**
Within-block syndrome for block 2: `(Z₄Z₅, Z₅Z₆)`.
`X₄|...0...⟩` flips qubit 4. Syndrome: `(-1, +1)` → error on qubit 4. Apply `X₄`. ✓

**Z component (qubit 4 is in block 2):**
Between-block syndrome: `X₁X₂X₃X₄X₅X₆` and `X₄X₅X₆X₇X₈X₉`.
A Z error on qubit 4 anticommutes with `X₄`. First syndrome becomes `-1`, second becomes `-1`.
Pattern `(-1,-1)` identifies block 2. Apply `Z₄Z₅Z₆` (or effectively `Z̄_block2`). ✓

**Combined**: both corrections applied, phase `i` from `Y = iXZ` is a global phase, physically
irrelevant. Logical state restored to `|0_L⟩`. ✓

---

## Summary

- The 3-qubit bit-flip code `[[3,1,1]]` corrects X errors via Z-type syndrome measurement; blind
  to Z errors.
- The 3-qubit phase-flip code corrects Z errors via X-type syndrome measurement; blind to X errors.
- Shor's 9-qubit code concatenates both, yielding the first `[[9,1,3]]` code correcting all
  single-qubit errors.
- The `[[n,k,d]]` notation characterizes a quantum code's resource use and error-correction power.
- All stabilizer codes extract syndrome information without disturbing the logical state, resolving
  the measurement-collapse obstacle.
- More efficient codes (`[[7,1,3]]` Steane, `[[5,1,3]]` perfect code) improve on Shor but require
  the CSS and stabilizer formalism of the next chapters.

---

## Further Reading

1. **Shor, P. W.** — "Scheme for reducing decoherence in quantum computer memory," *Phys. Rev. A*
   52, R2493 (1995). The original 9-qubit code paper.
2. **Calderbank, A. R. and Shor, P. W.** — "Good quantum error-correcting codes exist," *Phys.
   Rev. A* 54, 1098 (1996).
3. **Laflamme, R. et al.** — "Perfect quantum error correcting code," *Phys. Rev. Lett.* 77, 198
   (1996). The [[5,1,3]] perfect code.
4. **Preskill, J.** — Lecture Notes Chapter 7. Excellent pedagogical treatment of repetition codes.
5. **Devitt, S. J., Munro, W. J., and Nemoto, K.** — "Quantum error correction for beginners,"
   *Rep. Prog. Phys.* 76, 076001 (2013). Clear modern review accessible after this chapter.
