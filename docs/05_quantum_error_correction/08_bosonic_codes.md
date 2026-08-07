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
`D(β)|α⟩ = e^{i Im(β*α)} |α+β⟩`. In phase space (the Wigner function picture), `D(β)` displaces
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

Define the logical qubit:
```
|0_L⟩ = |cat+⟩ = N+ (|α⟩ + |-α⟩)   (even photon number superposition)
|1_L⟩ = |cat-⟩ = N- (|α⟩ - |-α⟩)   (odd photon number superposition)
```

### Noise Bias Property

**Photon loss (amplitude damping)**: The dominant error channel in microwave cavities is photon
loss, described by the Lindblad operator `L = √κ â`. Acting on a coherent state `|α⟩`, loss
causes a drift `α → α e^{-κt/2}`. For a cat qubit with large `|α|`, photon loss maps
`|α⟩ → |αe^{-κt/2}⟩` and `|-α⟩ → |-αe^{-κt/2}⟩`.

The key: the *relative* sign between `|+α⟩` and `|-α⟩` is preserved under small losses. Thus
photon loss preserves the logical Z basis `{|0_L⟩, |1_L⟩}` but may cause Z errors (bit flips
in the X basis).

More precisely:
- **Phase flip (Z) errors** (bit flips in the X basis): photon loss at rate `κ` causes Z errors
  exponentially suppressed as `e^{-2|α|²}`. This is the **noise bias**: Z errors are
  exponentially rare.
- **Bit flip (X) errors**: these flip `|0_L⟩ ↔ |1_L⟩` and arise with probability polynomial in
  `κ` and `|α|²`.

### Biased Noise Architecture

The exponential suppression of Z errors (`~e^{-2|α|²}`) while X errors remain polynomial creates
a strongly **biased noise channel** with noise bias `η ~ e^{2|α|²}`. For `|α|² = 4`, the bias
is `η ~ e^8 ≈ 3000`. This means a cat qubit has 3000 times more Z errors than X errors.

Biased noise is valuable because **repetition codes against one type of error** are much more
efficient than full QEC. A 1D repetition code of length `n` against X errors has threshold
`p_X^{1/2}` — much more lenient than full two-dimensional codes. Combined with the biased cat
qubit, this yields a hierarchical error correction architecture.

---

## GKP Codes (Gottesman-Kitaev-Preskill)

### Phase Space Lattice

The GKP code (Gottesman, Kitaev, Preskill, 2001) encodes a logical qubit in the phase space
of a harmonic oscillator using a lattice structure.

Define displacement operators:
```
S_q = D(i√π) = e^{i√π p̂}  (shift in q by √π)
S_p = D(√π)  = e^{-i√π q̂} (shift in p by √π)
```

The GKP code is stabilized by:
```
g₁ = S_q² = D(2i√π),   g₂ = S_p² = D(2√π)
```

(These are displacements by `2√π` in the `q` and `p` quadratures respectively.)

### Code Space

The code space consists of states invariant under displacements by `2√π`. The logical codewords
in the q basis are:

```
|0_L⟩ = Σ_{n=-∞}^∞ |q = 2n√π⟩     (sum of q-eigenstates at even multiples of √π)
|1_L⟩ = Σ_{n=-∞}^∞ |q = (2n+1)√π⟩  (sum at odd multiples of √π)
```

These are non-normalizable ideal GKP states (finite-energy approximations exist and are used
in practice).

### Error Correction Mechanism

An arbitrary small displacement error `D(ε)` with `|ε|` small shifts the state in phase space.
The syndrome measurement involves determining where in the lattice cell `[0, 2√π) × [0, 2√π)`
the state has been displaced to, then applying the inverse displacement to return to the lattice.

**Correction capability**: GKP corrects any displacement error `D(ε)` with
`|Re(ε)|, |Im(ε)| < √π/2`. Errors larger than this half-period cannot be corrected.

**Connection to classical lattice codes**: GKP can be generalized to encode `k` modes using a
`2k`-dimensional lattice. The construction is analogous to classical lattice coding, with the
symplectic form playing the role of the binary inner product.

### Physical Implementations

**Circuit QED (microwave cavities)**: GKP qubits in superconducting cavities are among the most
experimentally advanced bosonic codes. Demonstrations include:
- Ofek et al. (2016): first demonstration of cat qubit exceeding break-even on lifetime.
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
"spacing" `S = L + G + 1` and "order" `N ≥ max(2D, L+G)`. Define:

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

For the more capable `[N=2, S=2]` binomial code:
```
|0_L⟩ = (|0⟩ + |4⟩)/√2,   |1_L⟩ = |2⟩
```

This corrects loss of 1 photon: `â|0_L⟩ = 0` and `â|1_L⟩ = √2|1⟩` (both detectable).
Correction: measure photon parity and apply appropriate unitary.

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

- **Cat qubit logical states**: `|0_L⟩ = N+(|α⟩+|-α⟩)`, `|1_L⟩ = N-(|α⟩-|-α⟩)`
- **Cat qubit noise bias**: Z-error rate `~ e^{-2|α|²}` vs X-error rate `~ κ|α|²Δt`
- **GKP stabilizers**: `D(2i√π)` and `D(2√π)` (displacements by `2√π` in q and p)
- **GKP correction radius**: corrects displacements `|Re(ε)|, |Im(ε)| < √π/2`
- **Displacement operator**: `D(β) = e^{β â† - β* â}`, shifts coherent state: `D(β)|α⟩ ∝ |α+β⟩`
- **Photon number spacing for binomial codes**: spacing `S = L + G + 1` for `L` loss, `G` gain
  corrections

---

## Worked Example: Cat Qubit Noise Rate

**Parameters**: `|α|² = 4`, photon loss rate `κ = 10^{-3} μs^{-1}`, gate time `τ = 1 μs`.

**Z error probability per gate** (bit flip in X basis from photon loss):
```
p_Z ≈ κ|α|²τ/4 = (10^{-3})(4)(1)/4 = 10^{-3}
```

**X error probability per gate** (logical bit flip, exponentially suppressed):
```
p_X ≈ e^{-2|α|²} = e^{-8} ≈ 3.35 × 10^{-4}
```

Wait — actually for cat qubits, Z errors (phase flips relative to the cat basis) grow with `κ`,
while X errors (logical bit flips that change `|+cat⟩ ↔ |-cat⟩`) are exponentially suppressed:

```
p_X ≈ κ/(4κ_2) · e^{-2|α|² (1 - 4κ/κ_2)} ≈ e^{-2|α|²}
     ≈ e^{-8} ≈ 3.4 × 10^{-4}
```

**Noise bias**: `η = p_Z / p_X = 10^{-3} / 3.4×10^{-4} ≈ 3`

Hmm — at `|α|² = 4` the bias is still modest. At `|α|² = 9`:
```
p_X ≈ e^{-18} ≈ 1.5 × 10^{-8}
```
`η = p_Z/p_X = 10^{-3}/1.5×10^{-8} = 6.7 × 10^4` — a truly massive noise bias.

**Consequence**: A repetition code of length `n = 5` against X errors (with X-error threshold
`~50%`) can bring the logical X error rate to `~35 p_X^3 ≈ 1.6 × 10^{-22}` while the Z error
rate is corrected separately. This is far below what a qubit-only architecture could achieve.

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
