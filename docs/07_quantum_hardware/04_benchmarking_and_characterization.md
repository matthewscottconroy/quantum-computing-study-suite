# Benchmarking and Characterization of Quantum Hardware

> **Prerequisites**: Quantum channels and noise models (Chapter 2), Clifford circuits (Chapter 3),
> basic statistics
> **Connects to**: Error mitigation (06/06), fault tolerance thresholds (05/07), hardware
> comparison (07/01, 07/02)

---

## Overview

How good is a quantum computer? This seemingly simple question has no simple answer. "Gate
fidelity" — the probability that a gate does what it's supposed to — is the most natural figure
of merit, but it conflates many different error mechanisms and may not reflect actual algorithm
performance. A quantum processor with high single-gate fidelity may still fail at deep circuits
if errors are coherent (they add rather than cancel). A processor with moderate fidelity but
error-free idling may outperform a faster, noisier one for idle-heavy algorithms.

Quantum hardware characterization has developed into a sophisticated discipline with rigorous
statistical methods, carefully defined figures of merit, and an awareness of the distinction
between what can be measured practically and what actually matters for computation. This chapter
covers the major characterization and benchmarking protocols used in research and commercial
quantum computing: randomized benchmarking (and its variants), gate set tomography, quantum
volume, CLOPS, mirror circuits, and T1/T2 measurements.

Understanding these protocols is essential for critically reading hardware papers and for making
informed decisions about which hardware to use for specific algorithms.

---

## T1 and T2 Measurements

### T1: Longitudinal Relaxation Time

`T₁` measures how long a qubit initialized in `|1⟩` stays there. The measurement protocol:

1. Prepare qubit in `|1⟩` via an X gate.
2. Wait for idle time `τ`.
3. Measure in the Z basis.
4. Repeat for multiple values of `τ` and many shots.
5. Fit `P(1|τ) = A e^{-τ/T₁} + B` (exponential decay).

The parameter `T₁` is the amplitude damping time; `B` accounts for measurement errors and
residual thermal population. Physical interpretation: `T₁` is the time for the qubit to relax
from `|1⟩` to `|0⟩` due to energy exchange with the environment.

**Typical values**: Transmon `T₁ ∼ 100-500 μs`; trapped ion `T₁ ∼ hours` (limited by
background gas collisions, not intrinsic quantum noise).

### T2*: Dephasing Time (Ramsey)

`T₂*` measures the free induction decay — how long the qubit maintains phase coherence in a
superposition state, including low-frequency noise (inhomogeneous dephasing).

**Ramsey protocol**:
1. Prepare `|+⟩ = H|0⟩`.
2. Detune drive by `δ` from qubit frequency.
3. Wait time `τ` (qubit precesses at `δ`).
4. Apply H gate.
5. Measure. Fit: `P(0|τ) = (1 + e^{-τ/T₂*} cos(2πδτ + φ))/2`.

`T₂* ≤ 2T₁` always. Often `T₂* ≪ 2T₁` due to slow (low-frequency) noise from flux, charge,
or magnetic field fluctuations.

### T2: Hahn Echo Time (Spin Echo)

The **Hahn echo** removes low-frequency noise (quasi-static dephasing) by applying a refocusing
`π` pulse midway through the free evolution:

```
H → wait(τ/2) → X → wait(τ/2) → H → measure
```

Slow noise (approximately constant over time `τ`) is refocused. The decay `e^{-τ/T₂}` reflects
higher-frequency noise. `T₂ ≥ T₂*` always; `T₂ ≤ 2T₁`.

**CPMG (Carr-Purcell-Meiboom-Gill)**: Apply `n` echo pulses equally spaced. Each dynamical
decoupling pulse refocuses noise at harmonics of `1/τ`, enabling measurement of `T₂` at
different frequencies and decoupling from quasi-static noise: `T₂_CPMG → 2T₁` in the limit
`n → ∞` (complete dynamical decoupling).

---

## Randomized Benchmarking (RB)

### Standard RB

Randomized benchmarking (Knill et al., 2008; Magesan et al., 2011) extracts the average error
rate of the Clifford group efficiently and robustly, avoiding the exponential cost of full
process tomography and being insensitive to **state preparation and measurement (SPAM)** errors.

**Protocol**:
1. Prepare `|0⟩`.
2. Apply a random sequence of `m` Clifford gates `C₁, C₂, ..., C_m`.
3. Compute and apply the **inverse** gate `C_inv = (C_m ... C₁)⁻¹` (also a Clifford gate).
4. Measure: if the circuit were perfect, outcome is `|0⟩` with certainty.
5. Repeat for many random sequences and lengths `m`.
6. Fit: `P(|0⟩|m) = A p^m + B`

where `A, B` absorb SPAM errors and `p` is the **depolarization parameter**. The average Clifford
error rate is:

```
r = (1 - p)(2^n - 1) / 2^n  ≈  1 - p  (for small r)
```

For single-qubit benchmarking (`n=1`): `r = (1-p)/2`.

**SPAM robustness**: The parameters `A` and `B` absorb preparation and measurement errors;
`p` is SPAM-independent to first order. This is a key advantage over simple fidelity measurements.

### Clifford Gate Definition

The `n`-qubit Clifford group has `|C_n| = 2^{n²+2n} ∏_{j=1}^n (4^j-1)` elements. For single
qubit: `|C_1| = 24` (the 24 elements of the octahedral symmetry group on the Bloch sphere).

Each single-qubit Clifford can be compiled into `∼1.875` native gates on average (for
`{Rx, Ry, CNOT}` native gate set). RB measures the combined fidelity of all gates in the
Clifford compilation.

### Interleaved RB

**Interleaved RB** (Magesan et al., 2012) isolates the error of a specific gate `G`:

1. Run standard RB to get reference decay rate `p_ref`.
2. Run "interleaved" RB: alternate random Cliffords with the target gate `G`.
3. Get interleaved decay rate `p_int`.
4. Gate error estimate: `r_G = (1 - p_int/p_ref) × (2^n-1)/(2^n)`.

This gives the error of `G` above the average Clifford noise floor. Systematic errors apply when
gate errors are not depolarizing (e.g., coherent errors).

---

## Gate Set Tomography (GST)

### What GST Does

**Process tomography** reconstructs the full process matrix (CPTP map) `Λ` of a gate. Standard
process tomography requires `O(16^n)` measurements (for `n` qubits) and is sensitive to SPAM
errors. **Gate set tomography (GST)** (Blume-Kohout et al., 2017) simultaneously characterizes
the gate set `{Gᵢ}`, state preparation `ρ`, and measurement `{E_j}` in a self-consistent,
SPAM-robust manner.

**Principle**: SPAM errors are absorbed into the state and measurement models and are estimated
simultaneously with the gate errors. The full gate set is represented as a **gauge-invariant**
model — equivalent gate sets that differ only by a basis change are treated as identical.

**Measurement count**: For 1 qubit and gate set of size `k`, GST requires `O(k · L_max)` distinct
circuits of maximum length `L_max` (logarithmically many lengths are used). Total circuits:
`~100-10,000` depending on desired precision.

**Output**: A complete Lindblad generator description of each gate, SPAM matrices, confidence
intervals, and process matrix fidelity. The best-characterized quantum gates in the world are
characterized via GST.

### GST vs. RB

- **RB**: Single number (error rate `r`), SPAM robust, fast. Loses information about error
  structure (coherent vs. incoherent, rotation error vs. decoherence).
- **GST**: Complete model (process matrix), SPAM robust, slow. Full information about error
  type and structure; can identify and separate systematic errors.

RB is used for routine device characterization; GST is used when detailed error diagnosis is needed.

---

## Quantum Volume (QV)

### Definition

**Quantum volume** (Cross et al., 2019) is a single-number benchmark that captures the largest
"square" quantum circuit (equal width and depth) that a device can execute reliably.

**Protocol**:
1. For circuit width `n` (number of qubits), construct a random depth-`n` circuit:
   - Each layer applies a random SU(4) gate on a random permutation of qubit pairs.
2. Classically compute the **ideal output distribution** `p_ideal`.
3. Run on hardware, obtain **measured output distribution** `p_meas`.
4. Compute **heavy output probability**: `h = Σ_{x: p_ideal(x) ≥ median} p_meas(x)`
   (fraction of outputs that are "heavy" — above the median ideal probability).
5. The circuit passes if `h > 2/3` (with high confidence).
6. Find the largest `n` for which the circuit passes: `QV = 2^n`.

**Interpretation**: `QV = 2^n` means the device can execute a circuit of `n` qubits × `n` depth
with enough fidelity that it produces the correct output distribution (above 2/3 heavy threshold).

**Records** (approximate, as of 2025): IBM: QV = 128; IonQ: QV = 4,194,304 (but using a
different compilation method); Quantinuum: QV > 1 million (with all-to-all connectivity advantage).

**Limitations**:
- QV scales as `2^n` → large QV numbers can be misleading; `QV = 1024` (n=10) vs. `QV = 2048`
  (n=11) is 2× in QV but only one additional qubit.
- QV penalizes limited connectivity: all-to-all systems (trapped ions, Rydberg) have high QV
  without necessarily being better for specific algorithms.
- Does not measure scaling: QV tells you about a fixed-size device, not how it scales.

---

## CLOPS: Circuit Layer Operations Per Second

### Motivation

Quantum Volume measures quality but not speed. CLOPS (cross-platform performance standard)
measures the **throughput** of a quantum computer: how many quantum circuits can be executed
per unit time.

**Definition**: CLOPS is the number of "quantum processing unit layers" (QPU layers) executed
per second, for a standard circuit template.

**Measurement protocol** (IBM standard):
1. Use the same random `n × n` circuit template as QV.
2. Execute `100` batches of `10` circuits each.
3. Measure wall-clock time from "jobs submitted" to "results returned."
4. CLOPS = (number of QPU layers) / (total time).

For IBM systems (approximate): `CLOPS ~ 1,000 - 30,000 QPU layers/second` depending on system.

**Relevance**: For algorithms requiring many short circuits (like VQE with many Pauli measurements),
CLOPS determines how many optimization steps can be done per hour. A 30× improvement in CLOPS
can turn a 30-day computation into a 1-day computation.

---

## Cycle Benchmarking and Mirror Circuits

### Cycle Benchmarking

**Cycle benchmarking** (Erhard et al., 2019) measures the error of a full **circuit cycle**
(one layer of parallel two-qubit gates across the entire processor), rather than individual
gates. This is more relevant for actual circuit performance, since multi-qubit layers may have
higher error from crosstalk.

Protocol: similar to RB but with a specific gate cycle interleaved, extracting the Pauli
error rate of the full layer.

### Mirror Circuits

**Mirror circuits** (Proctor et al., 2021) use a circuit and its **time-reversal** (inverse)
as a built-in test:

1. Apply random circuit `U`.
2. Apply `U†`.
3. Measure: perfect quantum computer returns `|0⟩` with certainty.
4. The "success rate" measures the circuit fidelity at scale.

Mirror circuits are:
- **Scalable**: work at any qubit count without classical simulation.
- **Sensitive to crosstalk**: multi-qubit errors show up as degraded mirror fidelity.
- **Hardware agnostic**: no specific gate set required.

---

## Key Formulas

- **T₁ decay**: `P(1|τ) = A e^{-τ/T₁} + B`
- **Ramsey fringe**: `P(0|τ) = [1 + e^{-τ/T₂*} cos(2πδτ + φ)] / 2`
- **RB decay**: `P(|0⟩|m) = A p^m + B`; gate error `r = (1-p)(2^n-1)/2^n`
- **Interleaved RB gate error**: `r_G ≈ (1 - p_int/p_ref) (2^n-1)/2^n`
- **QV heavy output**: `h = Σ_{x: p_ideal(x) ≥ median} p_meas(x) > 2/3` required
- **QV = 2^n** where `n` is the largest passing width

---

## Worked Example: Randomized Benchmarking Analysis

**Experiment**: Single-qubit RB on a superconducting qubit. Sequence lengths
`m ∈ {1, 10, 20, 50, 100, 200}`, `50` sequences per length, `1000` shots per sequence.

**Data** (illustrative):
```
m=1:   P(0) = 0.990 ± 0.003
m=10:  P(0) = 0.931 ± 0.004
m=20:  P(0) = 0.876 ± 0.005
m=50:  P(0) = 0.740 ± 0.007
m=100: P(0) = 0.580 ± 0.008
m=200: P(0) = 0.366 ± 0.009
```

**Fitting** `P(m) = A p^m + B`:

Using least-squares fit (or maximum likelihood):
- `A = 0.960`, `p = 0.9936`, `B = 0.020`

**Gate error rate**:
```
r = (1 - p)/2 = (1 - 0.9936)/2 = 0.0032 = 0.32%
```

This is the average error per Clifford gate. Each Clifford compiles to approximately 1.875
native gates (Rx, Ry), so the native gate error is approximately `r_native ≈ 0.32%/1.875 = 0.17%`.

**SPAM assessment**: `A = 0.960` means SPAM efficiency `= 0.960` (4% SPAM error total);
`B = 0.020` means 2% residual state preparation error. These are absorbed into `A, B` and do
not affect the extracted `p`. ✓

**Interleaved RB** for Z gate (nominally error-free as a virtual Z gate):
If `p_int/p_ref = 1.000`, then `r_Z = 0` — consistent with virtual Z gates having no hardware
error.

For CX gate (two-qubit): typical result on IBM hardware is `r_CX ≈ 0.5%`.

---

## Summary

- `T₁, T₂^*, T₂` measure qubit coherence; `T₁` from inversion recovery, `T₂*` from Ramsey
  fringe, `T₂` from Hahn echo. `T₂* ≤ T₂ ≤ 2T₁`.
- **Randomized benchmarking** extracts average Clifford error rate from exponential fidelity
  decay, SPAM-robustly with polynomial circuit count.
- **Interleaved RB** isolates error of a specific gate; **cycle benchmarking** characterizes
  full circuit layer errors including crosstalk.
- **Gate set tomography** provides the full process matrix (SPAM-robust) at `O(k·L_max)` circuit
  cost; best for detailed error characterization.
- **Quantum Volume** measures the largest reliably executable square circuit; captures both
  fidelity and connectivity.
- **CLOPS** measures throughput; **mirror circuits** provide scalable fidelity assessment
  without classical simulation.

---

## Further Reading

1. **Magesan, E., Gambetta, J. M., and Emerson, J.** — "Scalable and robust randomized
   benchmarking of quantum processes," *Phys. Rev. Lett.* 106, 180504 (2011). Standard RB.
2. **Blume-Kohout, R. et al.** — "Demonstration of qubit operations below a rigorous fault
   tolerance threshold with gate set tomography," *Nat. Commun.* 8, 14485 (2017). GST.
3. **Cross, A. W. et al.** — "Validating quantum computers using randomized model circuits,"
   *Phys. Rev. A* 100, 032328 (2019). Quantum volume definition.
4. **Proctor, T. et al.** — "Measuring the capabilities of quantum computers," *Nat. Phys.* 18,
   75 (2022). Mirror circuits and comprehensive benchmarking comparison.
5. **Magesan, E. et al.** — "Characterizing quantum gates via randomized benchmarking," *Phys.
   Rev. A* 85, 042311 (2012). Interleaved RB.
