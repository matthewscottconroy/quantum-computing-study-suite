# Quantum Fourier Transform

> **Prerequisites**: 03_quantum_gates_and_circuits/01_single_qubit_gates.md and 02_multi_qubit_gates.md, 04_quantum_algorithms/01_quantum_parallelism_and_interference.md  
> **Connects to**: Quantum phase estimation (Chapter 4.4), Shor's algorithm (Chapter 4.6), quantum simulation, HHL algorithm

## Overview

The **Quantum Fourier Transform** (QFT) is the quantum analogue of the discrete Fourier transform and is arguably the single most important subroutine in quantum computing. It appears in quantum phase estimation (QPE), Shor's algorithm, quantum simulation, HHL (for linear systems), and numerous other algorithms. Understanding the QFT is a prerequisite to understanding the majority of exponential-speedup quantum algorithms.

The QFT transforms the **amplitudes** of a quantum state according to the discrete Fourier transform. Given an `n`-qubit state `|ψ⟩ = Σⱼ aⱼ|j⟩`, the QFT produces `Σₖ â_k|k⟩` where `{â_k}` are the DFT coefficients of `{aⱼ}`. This is a unitary transformation because the DFT is a unitary matrix.

The key advantage of the QFT over the classical FFT is not in speed for computing a DFT directly (the QFT does not speed up DFT problems — you cannot read out all the transformed amplitudes without measurement). Rather, the QFT is useful because:
1. It implements an exact unitary in `O(n²)` gates (vs `O(n · 2ⁿ)` classical operations for FFT on `2ⁿ` inputs)
2. It efficiently extracts **phase information** from quantum states — specifically, the period of a function encoded in amplitudes

The approximate QFT reduces the gate count to `O(n log n)` while maintaining exponential precision.

## The Discrete Fourier Transform

### Definition

For an `N`-point sequence `{xⱼ}_{j=0}^{N-1}`, the **discrete Fourier transform (DFT)** produces `{x̂_k}_{k=0}^{N-1}`:

$$\hat{x}_k = \frac{1}{\sqrt{N}}\sum_{j=0}^{N-1} x_j \omega^{jk}, \quad \omega = e^{2\pi i/N}$$

The factor `1/√N` makes the DFT a unitary matrix: `F_{kj} = ω^{jk}/√N`, so `F†F = I`.

**Key properties**:
- **Linearity**: DFT is a linear transform
- **Unitarity**: `F†F = I` (equivalent to Parseval's theorem: `Σ|x̂_k|² = Σ|xⱼ|²`)
- **Inverse**: `F⁻¹ = F†` (inverse DFT uses `ω⁻¹ = e^{-2πi/N}`)
- **Convolution theorem**: DFT converts convolution to pointwise multiplication

The classical **Fast Fourier Transform (FFT)** computes the DFT in `O(N log N) = O(n · 2ⁿ)` operations using the **divide-and-conquer** recursion based on the factoring:

$$\omega^{jk} = \omega_N^{jk} = \omega_{N/2}^{jk/2} \quad (\text{when } k \text{ is even})$$

The QFT achieves the same Fourier transform as a unitary operation on `n = log₂ N` qubits in `O(n²)` gates — exponentially fewer than `O(n · 2ⁿ)`. But the input and output are quantum states.

## Definition of the Quantum Fourier Transform

### On Basis States

The **QFT on `N = 2ⁿ` points** acts on the computational basis as:

$$\text{QFT}|j\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1}\omega^{jk}|k\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1}e^{2\pi i jk/N}|k\rangle$$

This is the DFT applied to the unit vector `eⱼ` (which has a 1 in position `j` and 0 elsewhere). The QFT of `|j⟩` is a superposition of all computational basis states with complex amplitudes `ω^{jk}/√N`.

### On General States

For a general state `|ψ⟩ = Σⱼ aⱼ|j⟩`:

$$\text{QFT}|ψ\rangle = \sum_k \hat{a}_k|k\rangle, \quad \hat{a}_k = \frac{1}{\sqrt{N}}\sum_j a_j e^{2\pi ijk/N}$$

The QFT applies the DFT to the amplitude vector `{aⱼ}`.

### Product Form

The QFT has a beautiful product-state form using binary representation. Writing `j = j₁·2^{n-1} + j₂·2^{n-2} + ... + jₙ` (binary digits `j₁,...,jₙ`):

$$\text{QFT}|j_1 j_2 \cdots j_n\rangle = \frac{1}{\sqrt{2^n}}\bigotimes_{l=1}^n \left(|0\rangle + e^{2\pi i \cdot 0.j_{n-l+1}\cdots j_n}|1\rangle\right)$$

where `0.j_m j_{m+1} ... j_n = j_m/2 + j_{m+1}/4 + ... + j_n/2^{n-m+1}` is the binary fraction.

**Explanation**: Each qubit in the output is in a state `(|0⟩ + e^{2πiφ}|1⟩)/√2` where `φ` is a specific binary fraction of the input `j`. This product form directly reveals the circuit structure.

## The QFT Circuit

### Structure

The QFT circuit uses two types of gates:

**Hadamard gate `H`**: Implements `|0⟩ → (|0⟩+|1⟩)/√2`, `|1⟩ → (|0⟩-|1⟩)/√2`. This is `QFT_2` — the 2-point Fourier transform.

**Controlled phase rotation `Rₖ`**:

$$R_k = \begin{pmatrix}1 & 0 \\ 0 & e^{2\pi i/2^k}\end{pmatrix}$$

This applies a phase of `e^{2πi/2ᵏ}` to `|1⟩`. Special cases:
- `R₁ = Z` (phase π)
- `R₂ = S` (phase π/2)
- `R₃ = T` (phase π/4)
- `R₄` = phase π/8 (non-standard gate)

### The Circuit for QFT on n Qubits

```
q₁: ─── H ── R₂ ─── R₃ ─── ··· ─── Rₙ ─── ··· ─────────────────── SWAP ─
              │      │              │
q₂: ──────── ● ─── ─── H ─── R₂ ── ··· ─── Rₙ₋₁ ─── ··· ──────── SWAP ─
                          │   
q₃: ──────────────────── ● ─── H ─ R₂ ─ ··· ─ Rₙ₋₂ ─── ··· ── SWAP ─
                                    
qₙ: ──────────── ··· ──────────── ──── ·── H ── SWAP ─
```

**Procedure for qubit 1**:
1. Apply `H` to qubit 1
2. Apply controlled-`R₂` with qubit 2 as control
3. Apply controlled-`R₃` with qubit 3 as control
...
4. Apply controlled-`Rₙ` with qubit `n` as control

**Procedure for qubit 2**:
1. Apply `H` to qubit 2
2. Apply controlled-`R₂` with qubit 3 as control
...

Continue for all qubits. After all H and phase gates, apply a bit-reversal (series of SWAP gates) to put the output in the correct order.

### Gate Count

The QFT circuit uses:
- `n` Hadamard gates
- `n-1 + n-2 + ... + 1 = n(n-1)/2` controlled-`Rₖ` gates
- `⌊n/2⌋` SWAP gates (for bit-reversal)

**Total**: `O(n²)` gates. This is exponentially fewer than the classical FFT's `O(n·2ⁿ)` classical operations.

**Circuit depth**: `O(n²)` or `O(n log n)` with parallelization. Controlled-`Rₖ` gates that act on non-overlapping pairs of qubits can be parallelized.

## The Approximate QFT

For practical applications (especially phase estimation), we only need the QFT to finite precision. The phase rotations `Rₖ` for large `k` are tiny (rotation by `2π/2ᵏ` → exponentially small for large `k`) and can be omitted without significantly affecting the result.

**Approximate QFT**: Drop all `Rₖ` gates with `k > m` (where `m = O(log n + log(1/ε))` for approximation error `ε`). This reduces the gate count to:

$$\text{Gates} = O(n \cdot m) = O(n \log n) \quad \text{for } m = O(\log n)$$

**Error analysis**: Omitting rotation `Rₖ` introduces a phase error of `O(2π/2ᵏ)` per qubit. With `n` qubits and `k > m`, the total error is `O(n · 2^{-m})`. Setting `m = ⌈log₂(n/ε)⌉` gives total error `≤ ε`.

For `n = 50` qubits and `ε = 10⁻⁶`: `m ≈ log₂(50/10⁻⁶) ≈ 26`. Each qubit then keeps at most `m - 1 = 25` controlled rotations (instead of up to `n - 1 = 49`), so the retained count is `Σ_ℓ min(n-ℓ, m-1) = 925` gates instead of `50 × 49 / 2 = 1225` for the exact QFT.

## Important Distinction: QFT ≠ Classical FFT Speedup

A common misconception is that the QFT provides a quantum speedup for classical FFT problems (signal processing, spectral analysis). **This is false.**

The QFT computes the Fourier transform of the **amplitude vector** of a quantum state — a vector with `2ⁿ` entries. But:
1. **Input**: Preparing a quantum state encoding `2ⁿ` arbitrary classical values requires `O(2ⁿ)` operations (you must set each amplitude individually, or use a quantum RAM which is physically challenging)
2. **Output**: Measuring the output state gives only one sample from the transformed distribution; reading all `2ⁿ` Fourier coefficients requires `O(2ⁿ)` measurements

So the QFT does not speed up classical DFT problems. The exponential speedup comes when the **amplitudes of the input state are efficiently preparable** (e.g., the state is the output of a quantum computation) and only **global properties** of the Fourier transform are needed (e.g., the dominant frequency, or the period).

**The role of QFT in Shor's algorithm**: The input state to the QFT is the superposition `Σⱼ |j⟩|aʲ mod N⟩` produced by the modular exponentiation circuit. After tracing out the second register (by measuring it), the first register is in a state `(1/√r)Σ_k|x₀ + kr⟩` — a superposition of values spaced by the period `r`. The QFT converts this periodic structure into a sharp peak at multiples of `N/r`, allowing period extraction with high probability. This is exactly the use case where the QFT is powerful.

## QFT Applied to a Periodic State

### Why QFT Reveals Periodicity

Consider a state encoding a periodic function with period `r`:

$$|\psi\rangle = \frac{1}{\sqrt{M}}\sum_{k=0}^{M-1}|kr\rangle \quad \text{(superposition of multiples of } r\text{ mod } N)$$

Applying the QFT:

$$\text{QFT}|\psi\rangle = \frac{1}{\sqrt{M}}\sum_{k=0}^{M-1}\text{QFT}|kr\rangle = \frac{1}{\sqrt{MN}}\sum_{k=0}^{M-1}\sum_{j=0}^{N-1}e^{2\pi ikrj/N}|j\rangle$$

$$= \frac{1}{\sqrt{MN}}\sum_{j=0}^{N-1}\left[\sum_{k=0}^{M-1}e^{2\pi ikrj/N}\right]|j\rangle$$

The inner sum `Σₖ e^{2πikrj/N}` is a geometric series. For large `M ≈ N/r`:
- It is large (≈ M) when `rj/N ≈ m` for integer `m`, i.e., `j ≈ mN/r`
- It is small (≈ 0) otherwise

**Conclusion**: The QFT maps the periodic state to a state concentrated at integer multiples of `N/r`. Measuring `j ≈ mN/r` allows recovery of `r` via `r ≈ mN/j` and the continued fractions algorithm.

This is the key: the QFT transforms **period** information (a global property of the superposition) into **frequency** information (the location of peaks in the transformed state), which is efficiently extractable by measurement.

## Key Formulas

**QFT definition**:
$$\text{QFT}|j\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1}e^{2\pi ijk/N}|k\rangle$$

**Product form**:
$$\text{QFT}|j_1\cdots j_n\rangle = \frac{1}{\sqrt{2^n}}\bigotimes_{l=1}^n\left(|0\rangle + e^{2\pi i\cdot 0.j_{n-l+1}\cdots j_n}|1\rangle\right)$$

**Gate count**:
$$\text{Exact QFT: } O(n^2), \quad \text{Approximate QFT: } O(n\log n)$$

**Rotation gates**:
$$R_k = \begin{pmatrix}1 & 0 \\ 0 & e^{2\pi i/2^k}\end{pmatrix}$$

**QFT of a periodic state** (peaks at `j = mN/r` for `m = 0, 1, ..., r-1`):
$$\text{QFT}\left[\frac{1}{\sqrt{r}}\sum_{m=0}^{r-1}|x_0 + mr\rangle\right] \approx \frac{1}{\sqrt{r}}\sum_{m=0}^{r-1}e^{2\pi ix_0\cdot m/r}\left|\frac{mN}{r}\right\rangle$$

## Worked Example

**Problem**: Apply the 2-qubit QFT to the state `|2⟩` (i.e., `|10⟩` in binary, for `n=2, N=4`).

(a) Write the expected QFT output using the definition.  
(b) Verify the result using the circuit (H on qubit 1, controlled-R₂, H on qubit 2, SWAP).  
(c) Interpret the output state.

**Solution**:

**Setup**: `n=2` qubits, `N=4`, `ω = e^{2πi/4} = i`. Input: `|j=2⟩ = |10⟩`.

**(a) QFT definition**:

$$\text{QFT}|2\rangle = \frac{1}{2}\sum_{k=0}^3 i^{2k}|k\rangle = \frac{1}{2}\sum_{k=0}^3 (-1)^k|k\rangle$$

$$= \frac{1}{2}(|0\rangle - |1\rangle + |2\rangle - |3\rangle) = \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$$

**(b) Circuit verification**:

Input: `|10⟩` (qubit 1 = 1, qubit 2 = 0, so `j₁=1, j₂=0`).

**Step 1 — H on qubit 1** (j₁=1):
$$H|1\rangle = \frac{|0\rangle-|1\rangle}{\sqrt{2}}, \quad \text{qubit 2 unchanged: } |0\rangle$$

State: `(|0⟩-|1⟩)/√2 ⊗ |0⟩`

**Step 2 — Controlled-R₂** with qubit 2 as control:

`R₂ = [[1,0],[0,e^{iπ/2}]] = [[1,0],[0,i]]`. Since qubit 2 (control) = `|0⟩`, the controlled-R₂ does nothing:

State: `(|0⟩-|1⟩)/√2 ⊗ |0⟩` (unchanged)

**Step 3 — H on qubit 2** (j₂=0):
$$H|0\rangle = \frac{|0\rangle+|1\rangle}{\sqrt{2}}$$

State: `(|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2`

$$= \frac{1}{2}(|00\rangle+|01\rangle-|10\rangle-|11\rangle)$$

**Step 4 — SWAP** (bit reversal):

The SWAP gate exchanges the two qubits: `|00⟩→|00⟩`, `|01⟩→|10⟩`, `|10⟩→|01⟩`, `|11⟩→|11⟩`. Applying it term by term to `(1/2)(|00⟩+|01⟩-|10⟩-|11⟩)`:

$$\text{After SWAP: } \frac{1}{2}(|00\rangle+|10\rangle-|01\rangle-|11\rangle) = \frac{1}{2}(|0\rangle-|1\rangle+|2\rangle-|3\rangle)$$

This matches the definition: `QFT|2⟩ = (|0⟩-|1⟩+|2⟩-|3⟩)/2` ✓.

**(c) Interpretation**:

The state `(|0⟩-|1⟩+|2⟩-|3⟩)/2` has:
- Equal probability `1/4` of each outcome `{0,1,2,3}`
- Phases `{+1, -1, +1, -1}` alternating — this is the Fourier mode at frequency `k=2` (the 2nd Fourier mode of 4)

The state `|j=2⟩` has "frequency" 2 in the DFT sense. The QFT maps it to the superposition with phase `ω^{jk} = i^{2k} = (-1)^k` — alternating signs, reflecting the period of 2 in the Fourier domain. Measuring a random outcome from `{0,1,2,3}` with equal probability confirms that `|j=2⟩` has no definite Fourier frequency to extract — but for a **superposition** of inputs (as in Shor's algorithm), the QFT reveals the dominant period.

## Summary

- The **QFT** applies the discrete Fourier transform to the amplitude vector of a quantum state: `QFT|j⟩ = (1/√N)Σₖ ω^{jk}|k⟩` with `ω = e^{2πi/N}`
- The QFT circuit uses `O(n²)` gates (Hadamards + controlled phase rotations `Rₖ`) with `n = log₂ N`; the classical FFT uses `O(n · 2ⁿ)` operations
- The **approximate QFT** drops small phase rotations (`k > O(log n)`) to achieve `O(n log n)` gates with `ε`-approximation
- The QFT does **not** speed up classical DFT problems; it is useful when: (a) the input state is efficiently preparable by quantum circuits, and (b) only global properties (periods, phases) of the Fourier transform are needed
- The **product form** `QFT|j⟩ = ⊗_l(|0⟩ + e^{2πi·0.j_{n-l+1}...j_n}|1⟩)/√(2^n)` directly gives the circuit structure
- The QFT converts **periodic state** information (period `r`) into **frequency** information (peaks at multiples of `N/r`), enabling period extraction; this is its role in QPE and Shor's algorithm

## Exercises

**Exercise 1**: Compute `QFT|3⟩` for `n = 2` qubits (`N = 4`) directly from the definition. Compare the phase pattern with `QFT|2⟩` from the worked example.

<details><summary>Solution</summary>

With `ω = e^{2πi/4} = i` and `j = 3`, the amplitudes are `ω^{3k}/2 = i^{3k}/2`:

- `k=0`: `i⁰ = 1`
- `k=1`: `i³ = -i`
- `k=2`: `i⁶ = -1`
- `k=3`: `i⁹ = i`

So `QFT|3⟩ = (1/2)(|0⟩ - i|1⟩ - |2⟩ + i|3⟩)`.

Whereas `QFT|2⟩` has phases stepping by `π` per unit of `k` (pattern `+, -, +, -`), `QFT|3⟩` has phases stepping by `3π/2` per unit of `k` (pattern `1, -i, -1, i`) — the input value `j` sets the "frequency" of the phase winding. All outcome probabilities are `1/4` in both cases.

</details>

**Exercise 2**: Count the gates in the exact QFT circuit for `n = 6` qubits: how many Hadamards, controlled-`Rₖ` rotations, and SWAPs? What is the smallest rotation angle that appears?

<details><summary>Solution</summary>

- Hadamards: `n = 6`
- Controlled rotations: `n(n-1)/2 = 6·5/2 = 15`
- SWAPs: `⌊n/2⌋ = 3`

Total: `24` gates. The smallest rotation is `R₆`, applying phase `e^{2πi/2⁶} = e^{2πi/64}` — an angle of `2π/64 ≈ 0.098` rad. This illustrates why the approximate QFT can drop high-`k` rotations: they are exponentially close to the identity.

</details>

**Exercise 3**: Write `QFT|101⟩` (`n = 3`, `j = 5`) in product form, giving each qubit's relative phase as a binary fraction. Verify the product form against the definition by computing the amplitude of `|111⟩` both ways.

<details><summary>Solution</summary>

With `j₁j₂j₃ = 101`, the three binary fractions are:

- `0.j₃ = 0.1₂ = 1/2`
- `0.j₂j₃ = 0.01₂ = 1/4`
- `0.j₁j₂j₃ = 0.101₂ = 5/8`

$$\text{QFT}|101\rangle = \frac{1}{\sqrt{8}}\left(|0\rangle + e^{2\pi i\cdot 1/2}|1\rangle\right)\left(|0\rangle + e^{2\pi i\cdot 1/4}|1\rangle\right)\left(|0\rangle + e^{2\pi i\cdot 5/8}|1\rangle\right)$$

Amplitude of `|111⟩` from the product form: `(1/√8)·e^{2πi(1/2 + 1/4 + 5/8)} = (1/√8)e^{2πi·11/8} = (1/√8)e^{2πi·3/8}`.

From the definition: `(1/√8)e^{2πi·jk/8} = (1/√8)e^{2πi·35/8} = (1/√8)e^{2πi·3/8}` (since `35 = 4·8 + 3`). The two agree ✓.

</details>

**Exercise 4**: Apply the 3-qubit QFT (`N = 8`) to the periodic state `(|0⟩ + |4⟩)/√2` (period `r = 4`). Which outcomes have nonzero probability, and how does this illustrate period extraction?

<details><summary>Solution</summary>

$$\text{QFT}\frac{|0\rangle+|4\rangle}{\sqrt{2}} = \frac{1}{\sqrt{16}}\sum_{k=0}^{7}\left(1 + e^{2\pi i\cdot 4k/8}\right)|k\rangle = \frac{1}{4}\sum_k \left(1 + (-1)^k\right)|k\rangle$$

The factor `1 + (-1)^k` is `2` for even `k` and `0` for odd `k`:

$$= \frac{1}{2}(|0\rangle + |2\rangle + |4\rangle + |6\rangle)$$

Only multiples of `N/r = 8/4 = 2` survive, each with probability `1/4`. Measuring gives some `j = m·(N/r)`; from `j/N = m/r` one recovers the period `r = 4` (e.g., outcome `j = 6` gives `6/8 = 3/4`, denominator 4). This is exactly the mechanism Shor's algorithm uses at scale.

</details>

## Further Reading

1. **Nielsen & Chuang**, §5.1 — the QFT circuit, gate count, and approximate QFT; the clearest standard reference
2. **Shor**, "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer" (SIAM Journal on Computing, 1997) — Section 5 derives the QFT as part of the factoring algorithm; arXiv:quant-ph/9508027
3. **Cooley & Tukey**, "An Algorithm for the Machine Calculation of Complex Fourier Series" (Mathematics of Computation, 1965) — the original FFT paper; shows the classical structure that the QFT generalizes
4. **Coppersmith**, "An Approximate Fourier Transform Useful in Quantum Factoring" (IBM Research Report, 1994; arXiv:quant-ph/0201067) — introduces the approximate QFT with the key circuit and error analysis
5. **Childs & van Dam**, "Quantum algorithms for algebraic problems" (Reviews of Modern Physics, 2010) — surveys the role of QFT in the hidden subgroup problem (the unifying framework for factoring, discrete log, and related problems)
