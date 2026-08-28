# Bosonic Codes

> **Prerequisites**: Quantum harmonic oscillator, creation/annihilation operators, coherent states
> (Chapter 2), stabilizer formalism (05/04)
> **Connects to**: Superconducting hardware (07/01), photonic platforms (07/03), cat qubit
> architectures

---

## Overview

All codes discussed so far encode logical information in collections of two-level systems (qubits).
Bosonic codes take a different approach: encode a logical qubit (or multiple logical qubits) in
the infinite-dimensional Hilbert space of a single bosonic mode — a quantum harmonic oscillator.
The mode might be a microwave cavity in a circuit QED system, an optical mode, a motional mode
of a trapped ion, or a phonon mode in a mechanical resonator.

Bosonic codes exploit the rich structure of the harmonic oscillator Hilbert space to achieve
error correction without requiring many physical two-level systems. In some regimes, bosonic
codes can outperform qubit codes in both hardware overhead and noise tolerance. They also reveal
a deep connection between error correction and the geometry of phase space.

Three families of bosonic codes receive the most theoretical and experimental attention: **cat
codes** (superpositions of coherent states), **GKP codes** (Gottesman-Kitaev-Preskill, using
a lattice structure in phase space), and **binomial codes** (using photon number spacing). Each
has distinct noise-protection properties suited to different hardware platforms.

---

## Bosonic Mode Basics

### Creation and Annihilation Operators

A bosonic mode has:
- Annihilation operator `â` and creation operator `â†` with `[â, â†] = I`.
- Number states (Fock states) `|n⟩` satisfying `â†â|n⟩ = n|n⟩`, `â|n⟩ = √n|n-1⟩`,
  `â†|n⟩ = √(n+1)|n+1⟩`.
- Quadrature operators: `q̂ = (â + â†)/√2` and `p̂ = i(â† - â)/√2` with `[q̂, p̂] = i`.

### Coherent States

A **coherent state** `|α⟩` (for `α ∈ ℂ`) is the eigenstate of `â` with eigenvalue `α`:
`â|α⟩ = α|α⟩`. It is the quantum state closest to a classical oscillator:

```
|α⟩ = e^{-|α|²/2} Σ_{n=0}^∞ (α^n / √n!) |n⟩
```

The photon number distribution is Poissonian: `P(n) = e^{-|α|²}|α|^{2n}/n!` with mean `|α|²`.

### Displacement Operators

The **displacement operator** `D(β) = exp(βâ† - β*â)` shifts coherent states:
`D(β)|α⟩ = e^{i Im(βα*)} |α+β⟩`. In phase space (the Wigner function picture), `D(β)` displaces
the state by `β` in the complex plane.

Displacement operators satisfy:
```
D(α)D(β) = e^{i Im(α β*)} D(α+β)
```

---

## Cat Codes

### Cat State Definition

A **Schrödinger cat state** is a superposition of two or more coherent states with large `|α|`.
The two-component cat state:

```
|cat±⟩ = N± (|α⟩ ± |-α⟩)
```

where `N± = (2 ± 2e^{-2|α|²})^{-1/2}` are normalization constants. For large `|α|`, `N± ≈ 1/√2`.

The parity cat states define the logical X basis, and the coherent states themselves serve
(to exponential accuracy) as the logical Z basis:
```
|+_L⟩ = |cat+⟩ = N+ (|α⟩ + |-α⟩)   (even photon number superposition)
|-_L⟩ = |cat-⟩ = N- (|α⟩ - |-α⟩)   (odd photon number superposition)

|0_L⟩ = (|+_L⟩ + |-_L⟩)/√2 ≈ |α⟩,   |1_L⟩ = (|+_L⟩ - |-_L⟩)/√2 ≈ |-α⟩
```
(The `≈` is exponentially good: `|0_L⟩` and `|1_L⟩` differ from `|±α⟩` by terms of order
`e^{-2|α|²}`, since `⟨α|-α⟩ = e^{-2|α|²}`.)

### Noise Bias Property

**Photon loss (amplitude damping)**: The dominant error channel in microwave cavities is photon
loss, described by the Lindblad operator `L = √κ â`. Coherent states are eigenstates of `â`:
a photon-loss jump maps `â|±α⟩ = ±α|±α⟩`. Loss therefore never sends `|α⟩` toward `|-α⟩` — the
computational (coherent-state) basis is preserved — but the *relative sign* `±α` between the
two branches is exactly a logical `Z`. Each jump also flips photon-number parity, mapping
`|cat±⟩ → |cat∓⟩`, i.e. `|+_L⟩ ↔ |-_L⟩`: the same statement in the X basis.

For dissipatively stabilized cat qubits (Mirrahimi et al., 2014), where an engineered
two-photon drive/dissipation confines the mode to `span{|α⟩, |-α⟩}`:
- **Bit flip (X) errors** (`|0_L⟩ ↔ |1_L⟩`, i.e. `|α⟩ ↔ |-α⟩`): these require tunneling
  between the two well-separated coherent states and are **exponentially suppressed** in the
  cat size, `p_X ∝ e^{-2|α|²}`.
- **Phase flip (Z) errors**: each photon-loss jump applies a logical `Z`, and jumps occur at
  rate `κ⟨n̂⟩ ≈ κ|α|²`. Phase flips therefore grow **linearly** with `|α|²`: `p_Z ≈ κ|α|² Δt`.

Enlarging the cat thus trades a linear increase in phase flips for an exponential decrease in
bit flips.

### Biased Noise Architecture

The exponential suppression of X errors (`~e^{-2|α|²}`) while Z errors grow only linearly
creates a strongly **biased noise channel** with noise bias `η = p_Z/p_X ~ e^{2|α|²}`. For
`|α|² = 4`, the bias is `η ~ e^8 ≈ 3000`: the cat qubit has ~3000 times more phase flips than
bit flips.

Biased noise is valuable because **repetition codes against one type of error** are much more
efficient than full QEC. Since bit flips are already exponentially rare at the physical level,
a simple 1D repetition code in the phase-flip basis (stabilizers `X̄ᵢX̄ᵢ₊₁`) suffices to
correct the dominant Z errors, with the far more lenient threshold of a 1D code rather than a
full 2D surface code. Combined with the biased cat qubit, this yields a hierarchical,
hardware-efficient error correction architecture (the "repetition cat" design).

---

## GKP Codes (Gottesman-Kitaev-Preskill)

### Phase Space Lattice

The GKP code (Gottesman, Kitaev, Preskill, 2001) encodes a logical qubit in the phase space
of a harmonic oscillator using a lattice structure.

With the convention `[q̂, p̂] = i`, the GKP stabilizers are the two phase-space displacements
```
S_q = e^{i 2√π q̂}    (displaces states by +2√π in p: e^{ibq̂} |p⟩ = |p + b⟩)
S_p = e^{-i 2√π p̂}   (displaces states by +2√π in q: e^{-iap̂} |q⟩ = |q + a⟩)
```

They commute: using `e^A e^B = e^B e^A e^{[A,B]}` for operators whose commutator is a number,
```
[i2√π q̂, -i2√π p̂] = (i2√π)(-i2√π)[q̂, p̂] = (4π)(i) = i4π
⟹ S_q S_p = S_p S_q · e^{i4π} = S_p S_q
```
The displacement lengths `2√π` are chosen exactly so that the phase `e^{i(2√π)²} = e^{i4π}`
winds around twice and cancels — this is the continuous-variable analogue of two Pauli
operators overlapping on an even number of sites.

### Code Space

The code space consists of states invariant under displacements by `2√π`. The logical codewords
in the q basis are:

```
|0_L⟩ = Σ_{n=-∞}^∞ |q = 2n√π⟩     (sum of q-eigenstates at even multiples of √π)
|1_L⟩ = Σ_{n=-∞}^∞ |q = (2n+1)√π⟩  (sum at odd multiples of √π)
```

These are non-normalizable ideal GKP states (finite-energy approximations exist and are used
in practice). Both combs sit at `q ∈ √π ℤ`, so `S_q` gives phase `e^{i2√π · n√π} = e^{i2πn} = 1`
on every peak, and `S_p` shifts each comb by `2√π`, mapping it to itself. The logical Paulis
are the *half*-lattice displacements:

```
Z̄ = e^{i√π q̂}   (phase e^{iπn} on |q = n√π⟩: +1 on |0_L⟩, -1 on |1_L⟩)
X̄ = e^{-i√π p̂}  (shifts q by √π: swaps the two combs)
```

with `X̄² = S_p` and `Z̄² = S_q` — logical Paulis square to stabilizers.

### Error Correction Mechanism

An arbitrary small displacement error `D(ε)` shifts the state in phase space. Measuring the
stabilizer `S_q = e^{i2√π q̂}` reveals the eigenvalue `e^{i2√π q}`, i.e. it determines the
displacement of `q` **modulo `√π`** (the phase is unchanged under `q → q + √π`); measuring
`S_p` likewise determines the shift of `p` modulo `√π`. The correction returns the state to
the lattice by undoing the *smallest* displacement consistent with the syndrome.

**Correction capability**: GKP corrects any displacement error `D(ε)` with
`|Re(ε)|, |Im(ε)| < √π/2`. Errors larger than this half-period cannot be corrected.

**Connection to classical lattice codes**: GKP can be generalized to encode `k` modes using a
`2k`-dimensional lattice. The construction is analogous to classical lattice coding, with the
symplectic form playing the role of the binary inner product.

### Physical Implementations

**Circuit QED (microwave cavities)**: bosonic codes in superconducting cavities are among the
most experimentally advanced QEC platforms. Demonstrations include:
- Ofek et al. (2016): first bosonic-code demonstration (a cat code) exceeding break-even on
  lifetime.
- Campagne-Ibarcq et al. (2020): first real-time GKP error correction in superconducting cavity.
- Current best GKP logical qubit T₁ ~ 1 ms (compared to transmon T₁ ~ 100 μs).

**Trapped ions**: Motional modes of trapped ions serve as the bosonic mode; coupling via
laser-ion interaction. GKP encoding demonstrated in 2019 (Flühmann et al., Nature).

---

## Binomial Codes

### Construction Principle

Binomial codes (Michael et al., 2016) protect against photon loss, photon gain, and dephasing
by spacing the photon number distribution such that errors cannot confuse codewords.

For a code correcting `L` photon losses, `G` photon gains, and `D` dephasing events, choose
"spacing" `S = L + G + 1` and "order" `N ≥ max(L, G, 2D) + 1`. (So correcting a single loss,
`L = 1`, requires `N = 2` — the kitten code below — while `N = 1` gives detection only.) Define:

```
|0_L⟩ = Σ_{m=0}^{N/2} √(C(N, 2m)/2^{N-1}) |S·(2m)⟩ = Σ_m c_m |S·(2m)⟩
|1_L⟩ = Σ_{m=0}^{N/2} √(C(N, 2m+1)/2^{N-1}) |S·(2m+1)⟩
```

where `C(N,k)` are binomial coefficients and `|n⟩` are Fock states.

### Simplest Case: [N=1, S=2, L=1, G=0, D=0]

```
|0_L⟩ = |0⟩,   |1_L⟩ = |2⟩
```

A single photon loss maps `|0_L⟩ → 0` (no photon to lose) and `|1_L⟩ = |2⟩ → √2|1⟩`. The
loss event is heralded by leaving the code space (the syndrome: is the photon number even or
odd?). This is more a detection code than a correction code.

For the more capable `[N=2, S=2]` binomial code (the "kitten" code):
```
|0_L⟩ = (|0⟩ + |4⟩)/√2,   |1_L⟩ = |2⟩
```

This corrects the loss of 1 photon. Applying `â` (using `â|n⟩ = √n|n-1⟩`):
```
â|0_L⟩ = (1/√2) â|4⟩ = (2/√2)|3⟩ = √2 |3⟩
â|1_L⟩ = â|2⟩ = √2 |1⟩
```
Both error states have *odd* photon number, while the code states have even photon number, so
a single loss is heralded by a photon-number parity measurement (a QND measurement in circuit
QED). The two error states `|3⟩` and `|1⟩` are orthogonal with equal norms (`√2` each — a
consequence of both codewords having the same mean photon number `⟨n̂⟩ = 2`, as the
Knill-Laflamme conditions require), so a recovery unitary mapping `|3⟩ → |0_L⟩, |1⟩ → |1_L⟩`
restores the logical state.

---

## Comparison of Bosonic Code Families

| Property | Cat Code | GKP Code | Binomial Code |
|----------|----------|----------|---------------|
| Logical encoding | Superpositions of coherent states | Phase space lattice | Weighted Fock superpositions |
| Natural noise | Photon loss (biased) | Displacement noise | Photon loss/gain |
| Dominant strength | Biased noise → small repetition code | Universal error correction | Explicit photon error structure |
| Experimental maturity | High (many demos) | High (recent demos) | Moderate |
| Gate difficulty | Moderate (CX between cats) | Hard (non-Gaussian operations) | Moderate |
| Classical simulation | Hard | Hard | Hard |

---

## Key Formulas

- **Cat qubit logical states**: `|±_L⟩ = N±(|α⟩ ± |-α⟩)` (X basis); `|0_L⟩ ≈ |α⟩`,
  `|1_L⟩ ≈ |-α⟩` (Z basis, up to `O(e^{-2|α|²})` corrections)
- **Cat qubit noise bias**: X-error (bit-flip) rate `~ e^{-2|α|²}` vs Z-error (phase-flip)
  rate `~ κ|α|²Δt`; bias `η = p_Z/p_X ~ e^{2|α|²}`
- **GKP stabilizers**: `S_q = e^{i2√π q̂}`, `S_p = e^{-i2√π p̂}` (with `[q̂,p̂] = i`); logical
  Paulis `Z̄ = e^{i√π q̂}`, `X̄ = e^{-i√π p̂}` satisfy `Z̄² = S_q`, `X̄² = S_p`
- **GKP correction radius**: corrects displacements `|Re(ε)|, |Im(ε)| < √π/2`
- **Displacement operator**: `D(β) = e^{β â† - β* â}`, shifts coherent state: `D(β)|α⟩ ∝ |α+β⟩`
- **Photon number spacing for binomial codes**: spacing `S = L + G + 1` for `L` loss, `G` gain
  corrections

---

## Worked Example: Cat Qubit Noise Rates and Bias

**Parameters**: `|α|² = 4`, photon loss rate `κ = 10^{-3} μs^{-1}`, gate time `τ = 1 μs`.

**Z error probability per gate** (phase flip; one photon-loss jump applies a logical Z, and
jumps occur at rate `κ⟨n̂⟩ ≈ κ|α|²`):
```
p_Z ≈ κ|α|²τ = (10^{-3})(4)(1) = 4 × 10^{-3}
```

**X error probability per gate** (bit flip `|α⟩ ↔ |-α⟩`, exponentially suppressed in the cat
size; the prefactor depends on the ratio of single-photon loss to the engineered two-photon
dissipation rate `κ₂`, but the scaling is dominated by the exponential):
```
p_X ∝ e^{-2|α|²} = e^{-8} ≈ 3.4 × 10^{-4}
```

**Noise bias**: `η = p_Z / p_X ≈ 4×10^{-3} / 3.4×10^{-4} ≈ 12`. At `|α|² = 4` the bias is
still modest, because the exponential has not yet had room to work. Increasing to `|α|² = 9`:
```
p_Z ≈ κ|α|²τ = 9 × 10^{-3}        (grows only linearly)
p_X ∝ e^{-18} ≈ 1.5 × 10^{-8}     (falls exponentially)
η = p_Z/p_X ≈ 6 × 10^5            (a massive noise bias)
```

**Consequence**: With bit flips already negligible at the physical level, only phase flips
need active correction. A length-5 repetition code in the phase-flip basis corrects up to 2
Z errors, leaving a logical phase-flip rate of roughly
`C(5,3) p_Z³ = 10 × (9×10^{-3})³ ≈ 7 × 10^{-6}` per round, improvable by orders of magnitude
with each increment of the repetition length — while the residual bit-flip rate stays at the
`10^{-8}` level (a few unprotected qubits' worth). A thin 1D code thus does the work that
would otherwise require a full 2D surface code.

---

## Summary

- Bosonic codes encode logical qubits in the infinite-dimensional Hilbert space of harmonic
  oscillators (cavities, motional modes), achieving error correction with fewer physical systems.
- **Cat qubits**: exploit the exponential suppression of bit-flip errors in `|α|²` to create
  strongly biased noise, enabling efficient small repetition codes.
- **GKP codes**: use a phase-space lattice to correct arbitrary small displacement errors; the
  most versatile bosonic code, but requires non-Gaussian operations for gates.
- **Binomial codes**: protect against specific loss/gain events using photon-number spacing in
  Fock space.
- Bosonic codes are hardware-efficient and experimentally advanced; leading demonstrations exceed
  the break-even point (logical lifetime > physical lifetime).
- Biased-noise architectures (cat qubit + repetition code) may offer a more resource-efficient
  path to fault tolerance than surface codes for some hardware platforms.

---

## Exercises

**Exercise 1.** Derive the cat-state normalization constants `N± = (2 ± 2e^{-2|α|²})^{-1/2}`,
using the coherent-state overlap `⟨β|α⟩ = e^{-|α|²/2 - |β|²/2 + β*α}`.

<details><summary>Solution</summary>

`⟨cat±|cat±⟩ = N±² (⟨α| ± ⟨-α|)(|α⟩ ± |-α⟩) = N±² (⟨α|α⟩ + ⟨-α|-α⟩ ± ⟨α|-α⟩ ± ⟨-α|α⟩)`.
The diagonal terms are each 1. For the cross terms, the overlap formula gives
`⟨α|-α⟩ = e^{-|α|²/2 - |α|²/2 - |α|²} = e^{-2|α|²}`, and `⟨-α|α⟩` is the same (real). So
`⟨cat±|cat±⟩ = N±² (2 ± 2e^{-2|α|²}) = 1`, giving `N± = (2 ± 2e^{-2|α|²})^{-1/2}`. For large
`|α|` both approach `1/√2`, and the deviation is exactly the exponentially small overlap that
also controls the bit-flip suppression.

</details>

**Exercise 2.** Show by direct computation that a single photon-loss event flips the parity of
a cat qubit: compute `â|cat±⟩` and identify the resulting state. Then explain why the same
event is a logical `Z` in the coherent-state computational basis `|0_L⟩ ≈ |α⟩, |1_L⟩ ≈ |-α⟩`.

<details><summary>Solution</summary>

Using `â|±α⟩ = ±α|±α⟩`:
`â|cat+⟩ = N+ (â|α⟩ + â|-α⟩) = N+ α(|α⟩ - |-α⟩) ∝ |cat-⟩`, and similarly
`â|cat-⟩ ∝ |cat+⟩`. So one loss maps the even cat to the odd cat and vice versa —
`|+_L⟩ ↔ |-_L⟩`, a parity flip. In the computational basis, `â|0_L⟩ ≈ α|0_L⟩` and
`â|1_L⟩ ≈ -α|1_L⟩`: each basis state is (approximately) preserved but they acquire *opposite*
signs, which is precisely the action `|0_L⟩ → |0_L⟩, |1_L⟩ → -|1_L⟩` of a logical `Z` (up to
the overall constant `α`). Swapping `|±_L⟩` and applying a relative sign in the `{|0_L⟩,
|1_L⟩}` basis are the same operator viewed in two bases.

</details>

**Exercise 3.** For the kitten code `|0_L⟩ = (|0⟩ + |4⟩)/√2`, `|1_L⟩ = |2⟩`, verify the two
Knill-Laflamme conditions for the error set `{I, â}`: (a) `⟨0_L|â†â|0_L⟩ = ⟨1_L|â†â|1_L⟩`,
and (b) `⟨0_L|â†â|1_L⟩ = 0` and `⟨0_L|â|1_L⟩ = 0`.

<details><summary>Solution</summary>

(a) `â†â` is the number operator: `⟨0_L|n̂|0_L⟩ = (0 + 4)/2 = 2` and `⟨1_L|n̂|1_L⟩ = 2`. Equal ✓
— both codewords have mean photon number 2, so a loss event reveals no logical information.
(b) `â†â|1_L⟩ = 2|2⟩`, and `⟨0_L|2⟩ = 0` since `|0_L⟩` has support only on `{|0⟩, |4⟩}` ✓.
Also `â|1_L⟩ = √2|1⟩` and `⟨0_L|1⟩ = 0` ✓. The error states `â|0_L⟩/√2 = |3⟩` and
`â|1_L⟩/√2 = |1⟩` are orthonormal, so the recovery `|3⟩ → |0_L⟩, |1⟩ → |1_L⟩` (conditioned on
odd parity) is a legitimate isometry.

</details>

**Exercise 4.** Using `[q̂, p̂] = i` and the identity `e^A e^B = e^B e^A e^{[A,B]}` (valid when
`[A,B]` is a number), verify that (a) the GKP logical operators `Z̄ = e^{i√π q̂}` and
`X̄ = e^{-i√π p̂}` anticommute, and (b) each *commutes* with both stabilizers `S_q = Z̄²` and
`S_p = X̄²`.

<details><summary>Solution</summary>

(a) `[i√π q̂, -i√π p̂] = (i√π)(-i√π)(i) = iπ`, so `Z̄ X̄ = X̄ Z̄ e^{iπ} = -X̄ Z̄`:
they anticommute, as logical Paulis must. (b) For `Z̄` and `S_p = e^{-i2√π p̂}`:
`[i√π q̂, -i2√π p̂] = (i√π)(-i2√π)(i) = i2π`, giving `Z̄ S_p = S_p Z̄ e^{i2π} = S_p Z̄` ✓.
`Z̄` trivially commutes with `S_q = Z̄²`. The mirror computation handles `X̄`. The pattern:
displacement operators pick up `e^{i(area)}` phases, where "area" is the symplectic product of
the two displacement vectors; logical-times-stabilizer areas are multiples of `2π`
(commuting), while logical-times-logical areas are odd multiples of `π` (anticommuting).

</details>

**Exercise 5.** A dissipative cat qubit has `κτ = 10^{-3}` per gate. Compute `p_Z`, the
bit-flip scale `e^{-2|α|²}`, and the bias `η = p_Z/p_X` for `|α|² = 6`, taking `p_X ≈
e^{-2|α|²}`. Roughly what repetition-code length `n` (correcting `⌊(n-1)/2⌋` phase flips)
brings the logical Z rate per round, `C(n, ⌈n/2⌉) p_Z^{⌈n/2⌉}`, below `10^{-10}`?

<details><summary>Solution</summary>

`p_Z ≈ κ|α|²τ = 6 × 10^{-3}`; `p_X ≈ e^{-12} ≈ 6.1 × 10^{-6}`; `η ≈ 6×10^{-3} / 6.1×10^{-6}
≈ 10³`. For the repetition code: `n = 7` gives `C(7,4) p_Z⁴ = 35 × (6×10^{-3})⁴ ≈ 4.5 ×
10^{-8}` (not enough); `n = 9` gives `C(9,5) p_Z⁵ = 126 × (6×10^{-3})⁵ ≈ 9.8 × 10^{-10}`
(borderline); `n = 11` gives `C(11,6) p_Z⁶ = 462 × (6×10^{-3})⁶ ≈ 2.2 × 10^{-11} < 10^{-10}` ✓.
So roughly `n = 9`–`11` cat qubits per logical qubit — compare the several hundred physical
qubits a surface code needs for similar logical rates.

</details>

---

## Further Reading

1. **Gottesman, D., Kitaev, A., and Preskill, J.** — "Encoding a qubit in an oscillator,"
   *Phys. Rev. A* 64, 012310 (2001). Original GKP paper.
2. **Mirrahimi, M. et al.** — "Dynamically protected cat-qubits: a new paradigm for universal
   quantum computation," *New J. Phys.* 16, 045014 (2014). Cat qubit framework.
3. **Michael, M. H. et al.** — "New class of quantum error-correcting codes for a bosonic mode,"
   *Phys. Rev. X* 6, 031006 (2016). Binomial codes.
4. **Campagne-Ibarcq, P. et al.** — "Quantum error correction of a qubit encoded in grid states
   of an oscillator," *Nature* 584, 368 (2020). First real-time GKP error correction.
5. **Terhal, B. M., Conrad, J., and Vuillot, C.** — "Towards scalable bosonic quantum error
   correction," *Quantum Sci. Technol.* 5, 043001 (2020). Review of bosonic codes and hardware.
