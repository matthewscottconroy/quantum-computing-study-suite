# Quantum Phase Estimation

> **Prerequisites**: 04_quantum_algorithms/03_quantum_fourier_transform.md, 03_quantum_gates_and_circuits/02_multi_qubit_gates.md (controlled-U gates, phase kickback)  
> **Connects to**: Shor's algorithm (QPE for order-finding), quantum chemistry (ground state energy estimation), HHL algorithm, quantum simulation

## Overview

**Quantum Phase Estimation** (QPE) is the algorithm that extracts the eigenvalue of a unitary operator. Given a unitary `U` and one of its eigenstates `|u⟩` satisfying `U|u⟩ = e^{2πiφ}|u⟩`, QPE estimates the phase `φ ∈ [0,1)` to `n` bits of precision using `n` ancilla qubits and `O(2ⁿ)` applications of `U` (or `n` controlled-`U^{2^k}` gates for `k = 0,...,n-1`).

QPE is the most important quantum subroutine after the QFT. It provides the mechanism by which quantum computers can:
- Find eigenvalues of exponentially large matrices (quantum chemistry, quantum simulation)
- Extract the order (period) of a modular exponentiation function (Shor's algorithm)
- Estimate the ground state energy of a Hamiltonian (quantum chemistry applications)
- Implement the quantum linear systems algorithm (HHL) which uses phase estimation on the eigenvalues of a matrix

The circuit is elegant and deeply instructive: `n` "phase kickback" events accumulate phase bits into a binary register, and the inverse QFT decodes them. It is as if we are performing a quantum binary search for the phase value.

## The Phase Estimation Problem

### Setup

Given:
1. A unitary operator `U` (as a black box or circuit)
2. An eigenstate `|u⟩` with eigenvalue `e^{2πiφ}` (so `U|u⟩ = e^{2πiφ}|u⟩`)
3. `n` ancilla (ancillary) qubits initialized in `|0⟩`

**Goal**: Estimate `φ` to `n` bits of precision — i.e., find the `n`-bit binary fraction `φ̃ = 0.φ₁φ₂...φₙ` (in base 2) that best approximates `φ`.

**Why binary fractions?** Because the QFT maps integer states to binary fraction phases. If `φ = j/2ⁿ` exactly (a dyadic rational), QPE gives `j` with probability 1. For general `φ`, there is a small probability of error from the rounding.

**Conventions**: We write `φ` as a number in `[0,1)` (not `[0,2π)`). The unitary eigenvalue is `e^{2πiφ}`, so `φ = 0` gives eigenvalue 1 and `φ = 1/2` gives eigenvalue `-1`.

## The QPE Circuit

### Overview

The QPE circuit has three stages:

1. **Create superposition**: Put `n` ancilla qubits in state `|+⟩ = H|0⟩`
2. **Phase kickback**: Apply controlled-`U^{2^k}` for `k = 0, 1, ..., n-1`
3. **Inverse QFT**: Apply `QFT⁻¹` to the ancilla register and measure

### Stage 1: Creating Superposition

Apply `H^{⊗n}` to the `n` ancilla qubits:

$$H^{\otimes n}|0\rangle^n = \frac{1}{\sqrt{2^n}}\sum_{k=0}^{2^n-1}|k\rangle$$

Combined with the eigenstate `|u⟩`, the full state is `(1/√2ⁿ)Σ_k|k⟩|u⟩`.

### Stage 2: Phase Kickback via Controlled Powers of U

The key circuit element is the **controlled-`U^{2^j}`** gate for `j = 0, 1, ..., n-1`. The `j`-th ancilla qubit (initially in `|+⟩`) controls `U^{2^j}` on the eigenstate register.

**Phase kickback on one ancilla qubit** (say qubit `j`): The `j`-th ancilla is in state `H|0⟩ = (|0⟩+|1⟩)/√2`. Applying controlled-`U^{2^j}`:

$$\frac{|0\rangle + |1\rangle}{\sqrt{2}}\otimes|u\rangle \xrightarrow{C\text{-}U^{2^j}} \frac{|0\rangle|u\rangle + |1\rangle U^{2^j}|u\rangle}{\sqrt{2}} = \frac{|0\rangle + e^{2\pi i\cdot 2^j\varphi}|1\rangle}{\sqrt{2}}\otimes|u\rangle$$

The ancilla picks up phase `e^{2πi·2^j φ}`. The eigenstate `|u⟩` is unchanged (phase kickback — target remains in eigenstate).

**All `n` qubits together**: After applying all `n` controlled-`U^{2^j}` gates, the ancilla register is in:

$$\frac{1}{\sqrt{2^n}}\sum_{k=0}^{2^n-1}e^{2\pi i\varphi k}|k\rangle\otimes|u\rangle$$

**Derivation**: Writing `k = k_{n-1}·2^{n-1} + ... + k_0·2^0`:

$$\bigotimes_{j=0}^{n-1}\frac{|0\rangle + e^{2\pi i\cdot 2^j\varphi}|1\rangle}{\sqrt{2}} = \frac{1}{\sqrt{2^n}}\sum_{k=0}^{2^n-1}\prod_{j: k_j=1}e^{2\pi i\cdot 2^j\varphi}|k\rangle = \frac{1}{\sqrt{2^n}}\sum_{k}e^{2\pi i\varphi k}|k\rangle$$

The last equality uses `Σⱼ kⱼ 2ʲ = k` (binary representation of `k`).

**Interpretation**: The ancilla register now holds the quantum Fourier transform of the amplitude vector `δ_{k, round(2ⁿφ)}` — a peaked distribution at `k ≈ 2ⁿφ`. It is already in the QFT basis.

### Stage 3: Inverse QFT and Measurement

The state `(1/√2ⁿ)Σ_k e^{2πiφk}|k⟩` looks exactly like `QFT|φ⟩` where `|φ⟩` is the state peaked at `j = 2ⁿφ` (if φ is a dyadic rational) — because:

$$\text{QFT}|j\rangle = \frac{1}{\sqrt{2^n}}\sum_k e^{2\pi ijk/2^n}|k\rangle$$

So if `φ = j/2ⁿ`, then `(1/√2ⁿ)Σ_k e^{2πiφk}|k⟩ = QFT|j⟩` and applying `QFT⁻¹` gives `|j⟩`.

Measuring the ancilla register gives `j` with probability 1, and `φ = j/2ⁿ` exactly.

**For general `φ`**: If `φ` is not a dyadic rational, the state is approximately `QFT` of a distribution peaked near `j* = round(2ⁿφ)`. The inverse QFT gives a distribution concentrated near `j*`, and measuring `j` near `j*` allows recovering `φ` to precision `1/2ⁿ`.

## Success Probability and Precision

### Exact Case

If `φ = j*/2ⁿ` (dyadic rational), QPE succeeds with probability 1 in `n` ancilla qubits.

### General Case

For general `φ`, the probability of getting the best `n`-bit approximation `j*` (the integer closest to `2ⁿφ`) satisfies:

$$P(j^*) \geq \frac{4}{\pi^2} \approx 0.405$$

To get `n` bits with probability `≥ 1-ε`, use `n + ⌈log₂(2 + 1/(2ε))⌉` ancilla qubits. Using the extra bits as a buffer improves success probability.

**Derivation** (sketch): The state before inverse QFT is `(1/√2ⁿ)Σ_k e^{2πiφk}|k⟩`. The amplitude of `|j⟩` after `QFT⁻¹` is:

$$\alpha_j = \frac{1}{2^n}\sum_{k=0}^{2^n-1}e^{2\pi i(\varphi - j/2^n)k} = \frac{1}{2^n}\cdot\frac{1 - e^{2\pi i\cdot2^n(\varphi - j/2^n)}}{1 - e^{2\pi i(\varphi - j/2^n)}}$$

For `j = j*` (best approximation, `|φ - j*/2ⁿ| ≤ 1/2^{n+1}`), the geometric series has magnitude `≥ 4/π² · 2ⁿ`, giving `|α_{j*}|² ≥ 4/π²`. The bound `4/π²` comes from optimizing over the worst case phase offset.

**Boosting**: Repeating QPE `O(log(1/ε))` times and taking the median of the estimates gives error `ε` with probability `1-δ` using `O(n·log(1/ε))` total ancilla applications.

## Resource Requirements

### Gate Count

For QPE with `n` ancilla qubits estimating phase to `n` bits of precision:

- **Hadamard gates**: `n` (one per ancilla qubit)
- **Controlled-`U^{2^j}` gates**: `n` gates (one per ancilla qubit), each requiring `2^j` applications of `U` (or an efficient implementation of `U^{2^j}` using repeated squaring)
- **Inverse QFT**: `O(n²)` gates
- **Total `U` applications**: `2⁰ + 2¹ + ... + 2^{n-1} = 2ⁿ - 1 = O(2ⁿ)` applications

**The expensive part**: The controlled-`U^{2ⁿ⁻¹}` gate (controlling `U` applied `2^{n-1}` times) dominates. For large `n`, this requires deep circuits, making QPE a fault-tolerant algorithm (needing error correction for the many sequential applications of `U`).

**Efficient implementation**: If `U` can be efficiently computed (e.g., `U = e^{-iHτ}` via Trotter decomposition), then `U^{2^k} = e^{-iH·2^k τ}`, which can be implemented with circuit depth proportional to `2^k · poly(n)`. This makes total depth exponential in `n`.

For many practical applications (quantum chemistry), we can implement `U^{2^k}` via **phase kickback + Hamiltonian simulation** more efficiently using **qubitization** or **quantum signal processing** methods, reducing the number of `U` applications.

## Applications

### Eigenvalue Estimation (Quantum Chemistry)

For a Hamiltonian `H` with lowest eigenvalue `E₀` (ground state energy) and ground state `|E₀⟩`, use `U = e^{-iHτ}`:

$$U|E_0\rangle = e^{-iE_0\tau}|E_0\rangle$$

Phase: `φ = E₀τ/(2π)`. QPE estimates `φ` from which `E₀ = 2πφ/τ`.

**Precision**: `n` bits of `φ` gives energy precision `δE = 2π/(τ·2ⁿ)`. For chemistry accuracy (~1 kcal/mol), need extremely high precision and therefore deep circuits. This is why fault-tolerant quantum hardware is needed for quantum chemistry applications.

**Preparation of ground state**: A key challenge is preparing `|E₀⟩` (the ground state). If we prepare an approximate state `|ψ⟩ = Σᵢ cᵢ|Eᵢ⟩` with `|⟨E₀|ψ⟩|² = |c₀|²`, QPE returns `E₀` with probability `|c₀|²`. If the overlap is exponentially small, QPE gives wrong answers with high probability.

### Order-Finding (Shor's Algorithm)

In Shor's algorithm, `U|y⟩ = |ay mod N⟩` is the modular multiplication operator. Its eigenvalues are `e^{2πis/r}` for `s = 0, 1, ..., r-1`, where `r` is the multiplicative order of `a` mod `N` (the period). QPE on the uniform superposition `(1/√r)Σ_{s=0}^{r-1}|u_s⟩` extracts random values of `s/r`, from which `r` is recovered using continued fractions.

### HHL Algorithm (Linear Systems)

The Harrow-Hassidim-Lloyd (HHL) algorithm for solving `Ax = b` uses QPE to estimate the eigenvalues of `A` (embedded in a unitary), then applies conditioned rotations to compute `A⁻¹|b⟩`. The efficiency depends on the condition number of `A` and the sparsity, but in ideal cases achieves exponential speedup over classical methods.

## Key Formulas

**Phase estimation setup**:
$$U|u\rangle = e^{2\pi i\varphi}|u\rangle, \quad \varphi \in [0,1)$$

**State after kickback**:
$$\frac{1}{\sqrt{2^n}}\sum_{k=0}^{2^n-1}e^{2\pi i\varphi k}|k\rangle\otimes|u\rangle$$

**Measurement outcome**: Best `n`-bit approximation `j* = \text{round}(2^n\varphi)`

**Success probability (worst case)**:
$$P(j^*) \geq \frac{4}{\pi^2} \approx 0.405$$

**Gate count**: `n` ancilla qubits, `O(2^n)` applications of `U`, `O(n^2)` gates for inverse QFT

**Energy estimation precision**:
$$\delta E = \frac{2\pi}{\tau \cdot 2^n}$$

## Worked Example

**Problem**: Apply QPE with `n=3` ancilla qubits to the unitary `U = S` (the phase gate, acting on a single qubit) and eigenstate `|u⟩ = |1⟩`.

(a) Identify the eigenvalue and phase.  
(b) Trace through the QPE circuit.  
(c) What is the probability of obtaining the correct result?

**Solution**:

**(a) Eigenvalue**:

`S|1⟩ = i|1⟩ = e^{iπ/2}|1⟩ = e^{2πi·(1/4)}|1⟩`.

Phase: `φ = 1/4 = 0.01` in binary (since `1/4 = 2^{-2} = 0.00 + 0.01 + ...`). More precisely: `φ = 0.25 = 0.01` in binary `0.01₂`.

As an integer: `j* = 2ⁿφ = 8 · (1/4) = 2`. So the QPE should output `j* = 2 = 010₂`.

**(b) Circuit trace** with `n=3` ancilla qubits:

Step 1 — Initialize: ancilla `|000⟩`, eigenstate `|1⟩`.

Step 2 — Apply `H^{⊗3}` to ancilla:
$$|{+}{+}{+}\rangle|1\rangle = \frac{1}{2\sqrt{2}}\sum_{k=0}^7|k\rangle|1\rangle$$

Step 3 — Apply controlled-`U^{2^0} = S`, controlled-`U^{2^1} = S^2 = Z`, controlled-`U^{2^2} = S^4 = Z^2 = I`:

- Ancilla qubit 1 (bit 2, controls `U^4 = I`): trivial, no phase
- Ancilla qubit 2 (bit 1, controls `U^2 = Z`): `Z|1⟩ = -|1⟩ = e^{iπ}|1⟩`
- Ancilla qubit 3 (bit 0, controls `U^1 = S`): `S|1⟩ = i|1⟩ = e^{iπ/2}|1⟩`

After all controlled gates, the ancilla register is:

$$\bigotimes_{j=0}^{2}\frac{|0\rangle + e^{2\pi i\cdot 2^j\cdot(1/4)}|1\rangle}{\sqrt{2}}$$

- Ancilla qubit 1 (j=2): `e^{2πi·4·(1/4)} = e^{2πi} = 1` → state `(|0⟩+|1⟩)/√2`
- Ancilla qubit 2 (j=1): `e^{2πi·2·(1/4)} = e^{iπ} = -1` → state `(|0⟩-|1⟩)/√2 = |−⟩`
- Ancilla qubit 3 (j=0): `e^{2πi·1·(1/4)} = e^{iπ/2} = i` → state `(|0⟩+i|1⟩)/√2`

So ancilla state = `|+⟩|−⟩|+i⟩` ⊗ `|1⟩`.

Step 4 — Apply QFT⁻¹ to ancilla:

Since `φ = 1/4` is a dyadic rational (`φ = 2/8 = j*/2ⁿ` with `j*=2, n=3`), the inverse QFT maps the ancilla state to `|j*⟩ = |2⟩ = |010⟩` with probability 1.

Let me verify: the ancilla state is `(1/√8)Σ_k e^{2πi·k/4}|k⟩` (using `φ=1/4`).

QFT⁻¹ maps `(1/√2ⁿ)Σ_k e^{2πiφk}|k⟩ → |j*⟩` when `φ = j*/2ⁿ`, giving `|j*=2⟩ = |010⟩`.

Step 5 — Measure:

Outcome: `010₂ = 2`. 

Recovered phase: `φ̃ = 2/2³ = 2/8 = 1/4 = φ`. **Exact recovery!**

**(c) Success probability**:

Since `φ = 1/4 = 2/8` is exactly a dyadic rational with denominator `2³ = 8` (using `n=3` ancilla qubits), the success probability is **exactly 1**. The QPE outputs `|010⟩` with certainty.

If instead we had `n=2` ancilla qubits (so `j* = round(4·1/4) = round(1) = 1`), QPE would output `01₂ = 1` with certainty, recovering `φ̃ = 1/4 = φ` still exactly (since `φ` is also representable with 2 bits: `φ = 0.01₂`).

This example illustrates why dyadic rational phases are the "easy cases" — they require exactly `⌈log₂(1/φ)⌉` ancilla bits for exact recovery. Non-dyadic-rational phases (like `φ = 1/3`) require more ancilla bits and involve the success probability bound of `4/π²`.

## Summary

- QPE estimates the eigenphase `φ` of a unitary `U` given eigenstate `|u⟩` with `U|u⟩ = e^{2πiφ}|u⟩`
- **Circuit structure**: `n` ancilla qubits in `|+⟩`, `n` controlled-`U^{2^k}` gates (phase kickback), inverse QFT, measurement
- After all kickbacks, the ancilla state is `(1/√2ⁿ)Σ_k e^{2πiφk}|k⟩` — the QFT of the state `|2ⁿφ⟩`
- **Inverse QFT decodes** the phase: if `φ = j*/2ⁿ` (dyadic), measurement gives `j*` with certainty
- For general `φ`: probability of obtaining the best approximation is `≥ 4/π² ≈ 0.405`
- **Gate cost**: `O(2ⁿ)` applications of `U` for `n`-bit precision; this makes QPE a **deep circuit** algorithm requiring fault-tolerant hardware
- Key applications: quantum chemistry (eigenvalues of Hamiltonians), Shor's algorithm (order-finding), HHL (linear systems)
- The eigenstate `|u⟩` must be prepared beforehand; preparing the ground state of a Hamiltonian is itself a challenging problem

## Further Reading

1. **Kitaev**, "Quantum measurements and the Abelian Stabilizer Problem" (arXiv:quant-ph/9511026, 1995) — introduces QPE in the context of the hidden subgroup problem; the original source
2. **Nielsen & Chuang**, §5.2 — QPE circuit, analysis of success probability, and example with matrix eigenvalues
3. **Babbush et al.**, "Encoding Electronic Spectra in Quantum Circuits with Linear T Complexity" (Physical Review X, 2018) — modern qubitization-based QPE for quantum chemistry with optimal gate counts
4. **Berry, Craig & Babbush**, "Qubitization of Arbitrary Basis Quantum Chemistry Leveraging Sparsity and Low Rank Factorization" (Quantum, 2019) — state-of-the-art QPE resource estimates for large-scale chemistry applications
5. **Lin & Tong**, "Heisenberg-Limited Ground-State Energy Estimation for Early Fault-Tolerant Quantum Computers" (PRX Quantum, 2022) — improved QPE variant using fewer qubits and more robust to errors; important for near-term fault-tolerant applications
