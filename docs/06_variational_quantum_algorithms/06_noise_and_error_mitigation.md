# Noise and Error Mitigation in NISQ Algorithms

> **Prerequisites**: VQE fundamentals (06/01), quantum noise channels (Chapter 2), basic
> statistical inference
> **Connects to**: Quantum hardware (Chapter 7), quantum error correction (Chapter 5),
> fault tolerance (05/07)

---

## Overview

Current quantum computers are noisy — every gate, every measurement, every moment of idle time
introduces errors. Fault-tolerant quantum error correction (Chapter 5) provides a long-term
solution but requires hundreds to thousands of physical qubits per logical qubit. In the NISQ
era, we work directly with noisy physical qubits and must either tolerate the noise or mitigate
it.

**Error mitigation** is a collection of classical post-processing techniques that reduce the
effect of noise on quantum algorithm outputs without requiring full error correction. Unlike
error correction, error mitigation does not remove errors — it cannot recover lost quantum
information. Instead, it uses additional circuit evaluations and classical computation to
extrapolate or cancel the systematic bias introduced by noise. Error mitigation improves the
accuracy of expectation value estimates at the cost of increased sampling overhead.

This chapter covers the main NISQ noise channels, and the four main error mitigation strategies:
zero-noise extrapolation (ZNE), probabilistic error cancellation (PEC), Clifford data regression
(CDR), and virtual distillation.

---

## NISQ Noise Channels

### Amplitude Damping (T₁ Decay)

The `T₁` channel models spontaneous emission: a qubit in `|1⟩` decays to `|0⟩` at rate `1/T₁`.
The Kraus operators:

```
K₀ = [[1, 0], [0, √(1-γ)]]
K₁ = [[0, √γ], [0, 0]]
```

where `γ = 1 - e^{-t/T₁}` for idle time `t`. For `t ≪ T₁`: `γ ≈ t/T₁`.

Effect on Bloch vector: `Z` component decays: `⟨Z⟩ → ⟨Z⟩(1-γ) + γ`. X and Y components also
decay: `⟨X⟩, ⟨Y⟩ → ⟨X⟩,⟨Y⟩ · √(1-γ)`. Amplitude damping breaks the symmetry between `|0⟩`
and `|1⟩`.

### Dephasing (T₂ Decay)

The `T₂` (phase coherence) channel models random phase kicks from low-frequency noise (e.g.,
flux noise in superconductors):

```
ρ → (1-p) ρ + p Z ρ Z   (depolarizing in Z basis)
```

Effect: `⟨X⟩, ⟨Y⟩ → ⟨X⟩, ⟨Y⟩ · (1 - 2p) = ⟨X⟩,⟨Y⟩ · e^{-t/T₂}` for `p = (1 - e^{-t/T₂})/2`.
`T₂ ≤ 2T₁` always; in practice `T₂ ≪ 2T₁` due to low-frequency noise.

### Depolarizing Channel

The standard gate error model is the **depolarizing channel**: each gate is followed by a random
Pauli error:

```
ε(ρ) = (1-p) ρ + (p/3)(XρX + YρY + ZρZ)
```

For multi-qubit depolarizing on `n` qubits: random Pauli from `{I,X,Y,Z}^⊗n` (excluding I)
with total error probability `p`. This is the most common noise model for gate benchmarking.

### Crosstalk and Leakage

Beyond the standard noise models:
- **Crosstalk**: a gate on qubit `i` disturbs qubit `j` due to physical coupling.
- **Leakage**: population escapes the qubit subspace `{|0⟩, |1⟩}` to higher energy levels
  (e.g., `|2⟩` of a transmon). Leakage errors are not correctable by standard QEC without
  leakage reduction units.

---

## Zero-Noise Extrapolation (ZNE)

### Principle

ZNE (Temme et al., 2017; Li and Benjamin, 2017) exploits the fact that noise effects vary
analytically with the noise rate `λ`. If we can artificially amplify the noise, we can measure
`C(λ)` for several values of `λ` and extrapolate to the zero-noise limit `C(0)`.

### Noise Amplification via Gate Folding

Physical noise amplification is challenging. Instead, use **gate folding**: replace each gate
`U` with `U · U† · U` (this is the identity if perfect, but triples the error probability when
noisy). More generally, replace `U` with `(U · U†)^{k-1} · U` to amplify noise by factor `2k-1`.

For a circuit with base noise rate `λ₀`, folding by factors `{c₁, c₂, ...}` gives noise
rates `{c₁λ₀, c₂λ₀, ...}`. Measure `C(cᵢλ₀)` for each.

### Richardson Extrapolation

For a **linear noise model** `C(λ) = C(0) + a₁λ` (noise enters linearly):
```
C(0) ≈ (c₂ C(c₁λ₀) - c₁ C(c₂λ₀)) / (c₂ - c₁)
```

With `c₁ = 1, c₂ = 3`:
```
C(0) ≈ (3 C(λ₀) - C(3λ₀)) / 2
```

For a **quadratic model** `C(λ) = C(0) + a₁λ + a₂λ²` (three measurements needed):
```
C(0) ≈ (c₂c₃ C(c₁λ₀) - c₁c₃ C(c₂λ₀) + c₁c₂ C(c₃λ₀)) / ((c₁-c₂)(c₁-c₃)(c₂-c₃))
```

Higher-order extrapolation removes higher-order noise contributions but amplifies shot noise.

### Limitations

- Requires the noise model to be **smooth** (analytically continuable) in `λ`.
- Richardson extrapolation amplifies statistical errors by a factor that grows with the
  extrapolation order.
- Cannot mitigate coherent errors (which enter non-analytically) or state preparation errors.
- For circuits with `G` gates at rate `λ`, the mitigated estimator has variance amplified by
  `~(2c-1)^{2G}` compared to the unmitigated estimator — exponential in circuit size.

---

## Probabilistic Error Cancellation (PEC)

### Quasi-Probability Decomposition

PEC (Temme et al., 2017) provides a formally exact error mitigation method (in the limit of
infinite sampling) by representing the ideal gate `G_ideal` as a quasi-probability mixture of
noisy, implementable operations:

```
G_ideal = Σᵢ qᵢ Bᵢ
```

where `Bᵢ` are noisy operations achievable on hardware and `qᵢ` are real numbers (not
necessarily positive — hence "quasi-probability"). Normalization: `Σᵢ qᵢ = 1`.

For each circuit evaluation:
1. Sample operation `Bᵢ` with probability `|qᵢ|/Σⱼ|qⱼ|`.
2. Execute `Bᵢ` and measure outcome `r`.
3. Assign signed weight `r · sign(qᵢ) · Σⱼ|qⱼ|`.
4. Average over many samples: the expectation equals the ideal `⟨G_ideal O⟩`.

### Sampling Overhead

Let `γ = Σᵢ|qᵢ|` be the **one-norm** of the quasi-probability. For `d`-qubit depolarizing noise
with rate `ε`, the ideal gate requires `γ = 1/(1-ε)^{4^d-1}` in the worst case. For `n` gates:

```
γ_total = γ^n = (1/(1-ε))^{n(4^d-1)}
```

The sampling overhead (number of circuit evaluations needed to achieve standard error `σ`) is:

```
S_PEC = γ_total² / σ²
```

For `n = 100` gates and `ε = 10^{-2}`: `γ_total = (1/0.99)^{100·3} ≈ e^{3} ≈ 20`. Overhead:
`400×` more evaluations than without mitigation.

This overhead is **exponential in the circuit depth**: it grows as `e^{O(nε)}` for `n` gates
with error rate `ε`. For circuits below threshold for error correction, this overhead is
manageable; for deep circuits, it becomes prohibitive.

### Fundamental Sampling Overhead Bound

Takagi et al. (2022) proved a fundamental lower bound: **any error mitigation scheme** that
achieves precision `ε` on a circuit with `T` gates (each with noise magnitude `‖N-I‖` = error
rate) requires sampling overhead at least `e^{Ω(T · rate)}`. This proves that error mitigation
cannot overcome exponential overhead in depth.

---

## Clifford Data Regression (CDR)

### Training with Classically Simulable Circuits

CDR (Czarnik et al., 2021) uses the Gottesman-Knill theorem (Clifford circuits are classically
simulable) to build a regression model for noise-corrected expectation values.

**Protocol**:
1. Generate a set of **near-Clifford training circuits**: circuits close to the target circuit
   but with non-Clifford gates replaced by Clifford approximations (e.g., replace T gates with
   S gates).
2. For each training circuit `Cⱼ`:
   - Compute the **ideal** expectation value `⟨O⟩_ideal(Cⱼ)` classically (Clifford simulation).
   - Measure the **noisy** expectation value `⟨O⟩_noisy(Cⱼ)` on hardware.
3. Fit a regression model: `⟨O⟩_ideal ≈ f(⟨O⟩_noisy)` (linear: `a ⟨O⟩_noisy + b`).
4. Apply the learned regression to the target circuit: `⟨O⟩_mitigated = f(⟨O⟩_noisy(C_target))`.

### Advantages and Limitations

**Advantages**:
- No additional circuit overhead (no gate folding or quasi-probability sampling).
- Can capture complex, non-linear noise effects.
- Compatible with other mitigation methods (CDR + ZNE).

**Limitations**:
- Requires the noise to be **similar** between training circuits and the target circuit.
- Linear regression assumes noise acts linearly on expectation values — not always valid.
- Computationally expensive if many training circuits are needed.

---

## Virtual Distillation (Symmetry Expansion)

### M-Copy Circuits

Virtual distillation (Huggins et al., 2021) uses `M` copies of the noisy state `ρ` and the
overlap between copies to exponentially suppress errors.

**Setup**: Run the target circuit `M` times, producing `M` noisy copies of `ρ`. Prepare the
combined state `ρ^⊗M`. Measure the expectation value of `O` with respect to the "purified" state:

```
⟨O⟩_VD = Tr[O ρ^M] / Tr[ρ^M]
```

This quantity corresponds to measuring `O` on the `M`-th power of `ρ`, normalized. If `ρ` is
close to a pure state `|ψ⟩⟨ψ|` with small noise `ε`, then `ρ^M` is much closer to pure: the
noise is exponentially suppressed.

**For depolarizing noise**: `ρ = (1-ε)|ψ⟩⟨ψ| + ε I/d`. Then:
```
Tr[O ρ^M] / Tr[ρ^M] → ⟨ψ|O|ψ⟩ + O((ε/(1-ε))^M)
```

Noise suppression is exponential in `M` — but so is the circuit overhead.

### Implementation

The circuit to measure `Tr[O ρ^M] / Tr[ρ^M]` uses the **SWAP test** or cyclic permutation
unitary between `M` registers. For `M = 2`, the overhead is approximately doubling the circuit
width (number of qubits) and depth. In practice, `M = 2` is most commonly used.

---

## Comparing Mitigation Methods

| Method | Circuit overhead | Classical overhead | Assumptions | Best for |
|--------|-----------------|-------------------|-------------|---------|
| ZNE | ~3-10× depth increase | Minimal | Analytically continuable noise | Short circuits, any noise |
| PEC | ~100-1000× samples | Minimal | Known noise model | Short circuits, characterized noise |
| CDR | Training circuits | Classical simulation | Similar noise to training | Medium circuits |
| VD | 2-4× qubits | Moderate | Nearly pure output state | When qubit overhead affordable |

---

## Key Formulas

- **ZNE (linear extrapolation)**: `C(0) ≈ [c₂C(c₁λ) - c₁C(c₂λ)] / (c₂-c₁)`
- **PEC quasi-probability**: `G_ideal = Σᵢ qᵢ Bᵢ`; overhead `∝ γ² = (Σ|qᵢ|)²`
- **Fundamental sampling lower bound** (Takagi): `S_min ≥ e^{Ω(T·ε)}`
- **Virtual distillation**: `⟨O⟩_VD = Tr[Oρ^M]/Tr[ρ^M]`; noise suppressed as `O(ε^M)`
- **Noise decay with depth (noise-induced BP)**: `|C(θ)-C_mix| ≤ (1-p)^D ‖O‖`

---

## Worked Example: ZNE on a 5-Qubit Circuit

**Setting**: 5-qubit variational circuit with 20 CNOT gates. Physical depolarizing error rate
`p = 5×10^{-3}` per CNOT. Target: estimate `⟨Z₁⟩`.

**Noise model assumption**: Linear → `C(λ) = C(0) + aλ`.

**Measurements**:
- No folding (`c=1`, 20 CNOTs): `⟨Z₁⟩_meas = 0.450 ± 0.01`
- 1-fold (`c=3`, 60 CNOTs): `⟨Z₁⟩_meas = 0.320 ± 0.01`

**ZNE extrapolation**:
```
C(0) ≈ [3 × 0.450 - 1 × 0.320] / (3-1) = (1.350 - 0.320) / 2 = 1.030/2 = 0.515
```

**Verification**: Ideal value (classical simulation): `⟨Z₁⟩_ideal = 0.510`. ZNE estimate
`0.515` is within `1%`. Unmitigated value `0.450` was `12%` off. ZNE improved accuracy
from 12% to 1% error at cost of doubling circuit evaluations. ✓

**Error estimate**: The ZNE output has standard error amplified by factor `|3/(3-1)| + |1/(3-1)| = 2`
compared to each measurement. With `σ_meas = 0.01`, `σ_ZNE ≈ √(9+1)/2 × 0.01 = 0.016`.

---

## Summary

- NISQ hardware noise includes amplitude damping (`T₁`), dephasing (`T₂`), depolarizing gate
  errors, crosstalk, and leakage — each with different mitigation strategies.
- **ZNE** amplifies noise via gate folding and extrapolates to zero noise; simple, widely
  applicable, but exponential overhead with circuit depth.
- **PEC** represents ideal operations as quasi-probability mixtures of noisy operations;
  formally exact but requires known noise model and exponential sampling overhead.
- **CDR** uses classically simulable circuits as training data to build a regression model;
  efficient but relies on noise similarity.
- **Virtual distillation** uses multiple circuit copies to exponentially suppress noise with
  `M`; overhead is exponential in `M` but `M=2` gives useful improvement.
- **Fundamental limit** (Takagi et al.): no error mitigation method can avoid exponential
  sampling overhead in circuit depth × error rate. Error correction, not mitigation, is the
  long-term solution.

---

## Further Reading

1. **Temme, K., Bravyi, S., and Gambetta, J. M.** — "Error mitigation for short-depth quantum
   circuits," *Phys. Rev. Lett.* 119, 180509 (2017). Original ZNE and PEC papers.
2. **Li, Y. and Benjamin, S. C.** — "Efficient variational quantum simulator incorporating
   active error minimization," *Phys. Rev. X* 7, 021050 (2017). Independent ZNE development.
3. **Czarnik, P. et al.** — "Error mitigation with Clifford quantum-circuit data," *Quantum* 5,
   592 (2021). Clifford data regression.
4. **Huggins, W. J. et al.** — "Virtual distillation for quantum error mitigation," *Phys. Rev.
   X* 11, 041036 (2021). Virtual distillation.
5. **Takagi, R. et al.** — "Fundamental limits of quantum error mitigation," *npj Quantum
   Information* 8, 114 (2022). Lower bound on mitigation sampling overhead.
