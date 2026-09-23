# Modern Benchmarking: Mirror Circuits, XEB, and Layer Fidelity

> **Prerequisites**: Randomized benchmarking and quantum volume (07/04), stabilizer formalism
> and the Pauli group (05/04), Pauli channels and twirling (06/06)
> **Connects to**: Error mitigation overheads (06/06), hardware platforms (07/01, 07/02),
> circuit complexity (03/04), fault-tolerance thresholds (05/07)

---

## Overview

The previous chapter presented the classical characterization toolkit: coherence times, randomized
benchmarking, gate set tomography, quantum volume, CLOPS. All of it is still run daily, and all of
it is now an incomplete answer to what users ask — *will my circuit work on this machine?* Three
things forced the change. Processors outgrew the size at which the Clifford group can be sampled
cheaply, so `n`-qubit RB stopped being executable. Quantum volume's pass/fail structure stopped
tracking improvement, and its "best square subset" framing stopped describing devices of a hundred
uneven qubits. And the 2019 supremacy experiment showed a benchmark can be rigorous,
headline-grabbing, and unrelated to anything a user can run.

---

## Why Randomized Benchmarking Over-Reports

### The twirl hides coherence

RB's random Clifford sequence **twirls** the noise, so the quantity it fits is the average
infidelity of the *twirled* channel, which is stochastic by construction. Real gates carry coherent
error, and coherent error accumulates in amplitude, not probability. For a single-qubit
over-rotation `U = R_z(θ)` the average gate infidelity is exactly

```
r = 1 - (|Tr U|² + d)/(d(d+1)) = (2/3) sin²(θ/2) ≈ θ²/6
```

so `r = 10⁻³` means `θ = 0.0775 rad = 4.44°`. Run that gate 100 times where nothing twirls it and
the rotations add: `100θ = 7.75 rad`, giving accumulated infidelity `(2/3) sin²(100θ/2) = 0.298`
against the stochastic prediction `1 - (1-r)¹⁰⁰ = 0.095`. RB under-states the damage by 3.1×, and
while `mθ ≪ 1` coherent error grows as `m²r`, not `mr`. The worst-case (diamond-norm) error is
`½‖U - I‖_◇ = |sin(θ/2)| = 0.0387`, **39× the RB number**, and thresholds are stated in worst case.

### RB does not scale

A random `n`-qubit Clifford needs `O(n²/log n)` two-qubit gates, and its inverse as many again.
Measured with Qiskit 2.5.2 (20 random Cliffords per size, `optimization_level=2`, all-to-all):

```
n      2     3     4     5     6     7     8     9    10
CX   1.1   3.5   5.8   9.8  14.4  20.6  28.2  36.1  45.4
```

On a linear chain the `n = 8` Clifford costs about 96 CX after routing. Past three or four qubits a
single "gate" in the RB sequence is deeper than the algorithm being benchmarked, and the fitted
decay measures the twirl, not the device. This is why RB in practice means one- and two-qubit RB:
the protocol never sees the whole processor.

Two-qubit RB on one pair, with the rest of the chip idle, omits crosstalk from concurrently driven
neighbours, spectator dephasing, and idling error accrued waiting for a layer; simultaneous RB
(Gambetta et al., 2012) reliably reports worse numbers on the same pair. Combining per-gate numbers
into a circuit prediction, `F ≈ Π(1 - rᵢ)`, further assumes errors are independent, stochastic and
context-free — all three fail optimistically, and Proctor et al. found real circuits well below the
RB-derived prediction, the shortfall growing with width.

---

## Mirror-Circuit Benchmarking

### Construction

A **randomized mirror circuit** (Proctor et al., 2022) is built from a **layer set** `𝕃` — the
device's own native parallel layers, such as all two-qubit gates on one matching of the coupling
graph — rather than from abstract Cliffords:

```
F₀ → [P₁ L₁ P₂ L₂ … P_{d/2} L_{d/2}] → P_c → [L_{d/2}⁻¹ P_{d/2} … L₁⁻¹ P₁] → F₀⁻¹
```

`F₀` is a layer of uniformly random single-qubit Cliffords; each `Lᵢ` is drawn from `𝕃`, and the
second half applies the inverses in reverse order; the `Pᵢ` are random Pauli layers, self-inverse so
re-applying them preserves the mirror. `P_c` is the **central Pauli layer**, the load-bearing
piece. Every element is Clifford, so the full unitary is `(W F₀)† P_c (W F₀)` for some Clifford `W`,
itself a Pauli up to phase: the ideal output is one basis state — a **target bit string** `s_C`,
uniformly random across circuits and computable from the stabilizer tableau in polynomial time.
Without `P_c` every circuit would target `|0…0⟩`, and a device that merely relaxes would score well.

### Effective polarization

Success is not scored as "did we get `s_C`". The estimator uses the whole Hamming-distance
distribution `h_k`, the probability of a result at Hamming distance `k` from `s_C`:

```
S = [4ⁿ/(4ⁿ - 1)] · Σ_{k=0}^{n} (-1/2)^k h_k  -  1/(4ⁿ - 1)
```

Two sanity checks: `h₀ = 1` gives `S = 1`, and uniformly random output, `h_k = C(n,k)/2ⁿ`, gives
`S = 0` exactly. For a global depolarizing channel of parameter `γ`, `S = γ` identically. The naive
alternative `(2ⁿ h₀ - 1)/(2ⁿ - 1)` over-reports, because local Pauli errors pile up at low Hamming
weight rather than spreading uniformly. Mirror circuits also scale where RB does not.

Circuit cost is `O(n)` two-qubit gates per layer, not `O(n²/log n)` per Clifford; the classical cost
is a stabilizer tableau, not `2ⁿ` amplitudes; the layers run simultaneously across the full width,
so crosstalk and idling sit inside the measurement; and width and depth are independent knobs. Two
caveats. **Error echo**: a mirror partially undoes coherent error, since an over-rotation in the
forward half is reversed in the backward half — Pauli randomization breaks most of this, but mirror
benchmarks stay mildly optimistic for coherent noise. **Compiler collusion**: an optimizing
transpiler recognises the near-identity and cancels it. The protocol also characterises Clifford
layers only.

---

## Volumetric Benchmarks: the Depth-Width Frame

Blume-Kohout and Young (2020) reframed the question. A benchmark is a triple — circuit family,
success metric, threshold — evaluated on a grid of **shapes** `(w, d)`: width `w` qubits by depth
`d` layers. The output is not a number but a **capability region**, the set of shapes the device
runs above threshold. The older metrics are single points on that plane: quantum volume tests the
diagonal `w = d` at a heavy-output threshold of `2/3`, and IonQ's `#AQ` tests `n` qubits by
`~n²` two-qubit gates. Neither describes the tall-thin or short-wide shapes real algorithms
occupy.

A first-order boundary: if the per-layered-gate error is `ε` and a width-`w`, depth-`d` circuit
holds about `wd/2` two-qubit gates, the polarization is `≈ exp(-ε w d/2)` and the `1/e` contour is
the hyperbola `w · d = 2/ε`. For `ε = 1.2%` that is `w·d ≈ 167`: a 16-qubit circuit reaches about 10
layers deep. Measured regions bend away from it — narrowed at small `w` by best-qubit selection, cut
off at large `d` by drift and leakage — and that deviation is the interesting content.

---

## Cross-Entropy Benchmarking and What Supremacy Measured

For a random circuit `C` on `n` qubits with ideal distribution `p_C`, and `N` bit strings `xᵢ`
sampled from the device, the **linear cross-entropy benchmark** is

```
F_XEB = (2ⁿ/N) Σᵢ p_C(xᵢ) - 1
```

The justification is the Porter-Thomas distribution: a deep enough random circuit has exponentially
distributed output probabilities, `Pr(p) = D e^{-Dp}` with `D = 2ⁿ`, whose collision probability is
`Σ_x p(x)² = 2/D`. Sampling from `p_C` then gives `E[p_C(x)] = 2/D` and `F_XEB = 1`; sampling
uniformly gives `1/D` and `F_XEB = 0`. On brickwork circuits of random `SU(4)` gates at `n = 10`
(40 circuits per point, Qiskit 2.5.2) the measured `⟨Σ_x p(x)²⟩` is `1.952 × 10⁻³` at 40 cycles
against `2/D = 1.953 × 10⁻³`, so an ideal sampler scores `0.999`; at 10 cycles the circuit has not
anticoncentrated, `⟨Σ_x p(x)²⟩ = 2.312 × 10⁻³`, and a *perfect* device scores `1.367`.

**What Sycamore measured.** 53 qubits, 20 cycles, 30 million samples, `F_XEB = 2.24 × 10⁻³`,
asserted above `10⁻³` at 5σ — about 99.8% of the output was noise, and the claim was that the
surviving 0.2% correlation with `p_C` was detectable and expensive to reproduce classically. The
task has no verifiable answer: you cannot check a sample without the classical computation you claim
is infeasible. And the full-circuit `F_XEB` was never directly measured, because computing `p_C` for
53 qubits was the thing declared intractable — the headline extrapolates from patch and elided
circuits plus a **digital error model**, the product of per-gate fidelities.

XEB has since fallen out of favour on three counts. The classical baseline moves (10,000 years
became 2.5 days with secondary-storage tensor contraction, then roughly 15 hours on 512 GPUs);
`F_XEB` is not a fidelity in general, and Gao et al. (2024) give spoofing strategies that score high
without simulating the circuit; and it costs `2ⁿ`.

---

## Application-Level Benchmarks

**QED-C suite** (Lubinski et al., 2023). Fixed implementations of real algorithms — Grover, QFT,
phase and amplitude estimation, hidden shift, Bernstein-Vazirani, Monte Carlo, Hamiltonian
simulation, VQE — run across a range of widths, scored by a normalised classical (Hellinger)
fidelity rescaled so a uniform sampler gets 0, and plotted volumetrically against execution time.

**Algorithmic qubits** (`#AQ`, IonQ). The largest `N` such that every suite circuit of width `≤ N`
with roughly `N²` two-qubit gates returns classical fidelity above `1 - 1/e ≈ 0.37`. Three caveats:
0.37 is permissive; IonQ applies error mitigation (debiasing, symmetrisation) whose shot cost the
metric omits; and `N`-by-`N²` is one vendor-chosen curve.

**BACQ** (the MetriQs-France consortium: CEA, CNRS, Thales, Eviden, LNE, Teratec; sometimes
transcribed "BACS") spans physics simulation, optimisation, linear solving and factoring with an
explicit *reporting* standard rather than a headline number; Atos's **Q-score** reports the largest
MaxCut instance beaten against a random baseline. The limit of all of them: the vendor's compiler is
part of the measurement.

---

## Layer Fidelity and EPLG

**Layer fidelity** (McKay et al., 2023) is IBM's current headline metric, defined precisely enough
to reproduce:

1. Choose a path of `N` qubits through the coupling graph — in practice, the best such path.
2. Partition the `N - 1` two-qubit gates on that path into **disjoint layers**: two for a linear
   chain, up to three for heavy-hex.
3. Run **simultaneous direct RB** on each layer: every subsystem — each two-qubit gate *and* each
   single qubit idling during that layer — is benchmarked concurrently, giving its own decay `αᵢ`.
4. Convert each decay to a process (entanglement) fidelity, with `dᵢ = 2^{nᵢ}`:
   `Fᵢ = [1 + (dᵢ² - 1) αᵢ] / dᵢ²`, so a two-qubit subsystem has `F = α + (1-α)/16`.
5. Multiply over every subsystem of every layer: `LF = Π_layers Π_subsystems Fᵢ`.

Because idling subsystems are included, `LF` is *not* a product of gate fidelities. **Error per
layered gate** normalises it to a size-independent per-gate quantity, `EPLG = 1 - LF^{1/n_2Q}` with
`n_2Q = N - 1` for an `N`-qubit chain. From the defining paper, `ibm_sherbrooke` (Eagle) reached
`LF₁₀₀ = 0.19`, so `EPLG₁₀₀ = 1 - 0.19^{1/99} = 1.7 × 10⁻²`, and `ibm_montecarlo` (Heron) reached
`LF₈₀ = 0.61`, so `EPLG₈₀ = 6.2 × 10⁻³`.

EPG, for contrast, is the error of one gate in isolation. EPLG rolls in four things EPG excludes:
simultaneity (crosstalk between concurrently driven pairs); idling and spectator error on qubits not
gated in that layer; the worst link on the chain, since a product is dominated by its weakest
factor; and the demand that the chain be **contiguous**. Ratios of 2–3× over EPG are typical.

A vendor quoting 99.9% two-qubit fidelity (`EPG = 10⁻³`) alongside `EPLG = 1.2 × 10⁻²` is not
contradicting itself; it is saying that roughly 92% of the error you will experience is contextual.
A 1000-gate circuit has predicted fidelity `(1 - 0.001)¹⁰⁰⁰ = 0.37` under the EPG number and
`(1 - 0.012)¹⁰⁰⁰ = 5.7 × 10⁻⁶` under EPLG. `LF` also gives the `γ` factor governing probabilistic
error cancellation's sampling overhead (06/06).

---

## How to Read a Vendor Benchmark Critically

1. **Which qubits?** Best pair, best chain, or whole device? A best subset hides the median.
2. **Isolated or simultaneous?** If the rest of the chip was idle, crosstalk is missing.
3. **Compilation freedom?** Mirror and Clifford circuits collapse under a good optimiser.
4. **Post-processing?** Readout mitigation, post-selection, debiasing and ZNE all cost shots.
5. **Post-selection rate?** Discarding 90% of shots is a 10× time cost no fidelity shows.
6. **Connectivity?** Heavy-hex versus all-to-all changes a gate count by an `O(n)` SWAP factor.
7. **Measured or extrapolated?** A QV "projected" from component fidelities is a calculation.
8. **Statistics and drift.** How many circuits and shots, over what window, and does it reproduce?

Then convert the headline into a volumetric statement: *which circuit, on which qubits, at what
success probability.* A benchmark that resists that translation is a marketing number.

---

## Key Formulas

- **Coherent over-rotation**: `r = (2/3) sin²(θ/2) ≈ θ²/6`; worst case `½‖U-I‖_◇ = |sin(θ/2)|`
- **Effective polarization**: `S = [4ⁿ/(4ⁿ-1)] Σ_k (-1/2)^k h_k - 1/(4ⁿ-1)`; decay `S(d) = A p^d`
- **Polarization from process infidelity `ε`**: `γ = 1 - 4ⁿ ε/(4ⁿ - 1)`
- **Linear XEB**: `F_XEB = (2ⁿ/N) Σᵢ p_C(xᵢ) - 1`; Porter-Thomas collision probability `2/2ⁿ`
- **Process fidelity from a direct-RB decay**: `F = [1 + (d²-1)α]/d²`
- **Layer fidelity / EPLG**: `LF = Π Fᵢ`; `EPLG = 1 - LF^{1/n_2Q}`, `n_2Q = N-1` for a chain
- **Volumetric `1/e` boundary** at per-layered-gate error `ε`: `w · d ≈ 2/ε`

---

## Worked Example: Mirror Circuits Against the Polarizing Model

Build randomized mirror circuits on a 4-qubit line, run them under an Aer noise model with a known
1% two-qubit depolarizing error, and check the measured effective polarization against the
polarizing-model prediction. The layer set holds the two disjoint CZ matchings of the line
`0-1-2-3`, namely `{CZ(0,1), CZ(2,3)}` and `{CZ(1,2)}`. Noise is attached only to `cz`, so the
prediction is exact arithmetic: a strength-`p` two-qubit depolarizing channel has process infidelity
`ε = 15p/16`, whose global-equivalent polarization on `n = 4` qubits is
`γ₂ = 1 - (4⁴/(4⁴-1))(15 × 0.01/16) = 0.990588`, so the model predicts `S(d) = γ₂^{n_CZ}`.

```python
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import StabilizerState, random_clifford
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
rng = np.random.default_rng(2024)
N, P2, SHOTS = 4, 0.01, 4000
LAYERS = [[(0, 1), (2, 3)], [(1, 2)]]        # the layer set: two disjoint CZ matchings
PAULIS = [lambda c, q: None, QuantumCircuit.x, QuantumCircuit.y, QuantumCircuit.z]
def mirror_circuit(d):                       # d layers drawn from LAYERS, d even
    half = [LAYERS[rng.integers(len(LAYERS))] for _ in range(d // 2)]
    f0 = [random_clifford(1, seed=int(rng.integers(1 << 30))) for _ in range(N)]
    qc = QuantumCircuit(N)
    twirl = lambda: [PAULIS[rng.integers(4)](qc, q) for q in range(N)]
    for q, c in enumerate(f0): qc.compose(c.to_circuit(), [q], inplace=True)
    for L in half:                                       # forward half
        twirl(); [qc.cz(a, b) for a, b in L]
    twirl()                                              # central Pauli layer
    for L in reversed(half):                             # mirrored half
        [qc.cz(a, b) for a, b in L]; twirl()
    for q, c in enumerate(f0): qc.compose(c.adjoint().to_circuit(), [q], inplace=True)
    target = max(StabilizerState(qc).probabilities_dict().items(), key=lambda kv: kv[1])[0]
    qc.measure_all()
    return qc, target, 2 * sum(len(L) for L in half)
def effective_polarization(counts, target):
    h = np.zeros(N + 1)
    for bits, c in counts.items(): h[sum(x != y for x, y in zip(bits, target))] += c / SHOTS
    s = sum((-0.5) ** k * h[k] for k in range(N + 1))
    return (4**N * s - 1) / (4**N - 1), h[0]
nm = NoiseModel(); nm.add_all_qubit_quantum_error(depolarizing_error(P2, 2), ["cz"])
sim = AerSimulator(noise_model=nm)
gamma2 = 1 - (4**N / (4**N - 1)) * (15 * P2 / 16)        # per-CZ polarization
for d in [2, 4, 8, 16, 32, 64, 128]:
    out = []
    for _ in range(30):
        qc, target, n_cz = mirror_circuit(d)
        qct = transpile(qc, sim, optimization_level=0)  # level 0: else the mirror is cancelled
        job = sim.run(qct, shots=SHOTS, seed_simulator=int(rng.integers(1 << 30)))
        out.append((*effective_polarization(job.result().get_counts(), target), n_cz))
    s, p0, ncz = np.mean(out, axis=0)
    print(f"{d:4d} {ncz:6.1f} {p0:10.4f} {(2**N*p0-1)/(2**N-1):9.4f} "
          f"{s:8.4f} {gamma2**ncz:11.4f} {s/gamma2**ncz:8.3f}")
```

**Output** (30 circuits × 4000 shots per depth, about 16 s; fully seeded, so it reproduces):

```
   d   n_cz   P(target)   naive S   eff. S   predicted   S/pred
   2    2.9     0.9786    0.9772   0.9735      0.9726    1.001
   4    5.9     0.9562    0.9533   0.9466      0.9454    1.001
   8   11.8     0.9118    0.9059   0.8939      0.8944    0.999
  16   24.6     0.8258    0.8142   0.7919      0.7925    0.999
  32   48.3     0.6899    0.6693   0.6356      0.6331    1.004
  64   97.3     0.4874    0.4532   0.4040      0.3986    1.014
 128  191.2     0.2694    0.2207   0.1725      0.1640    1.052
```

Fitting `S(d) = A p^d` over the seven depths gives `A = 0.9930`, `p = 0.986333`: `0.01367` error per
layer at `1.494` CZ per layer, i.e. **`0.00917` error per CZ against the `0.00941` injected**, a
2.5% gap from statistics and from local (rather than global) depolarizing channels not composing
exactly. The third and fifth columns carry the second lesson: at `d = 128` the raw survival
probability `0.2694` becomes, under a naive global-depolarizing inversion, a polarization of
`0.2207` — **28% above** the correct `0.1725`. Rerun at Qiskit's default optimization level, which
cancels most of the mirror, the same script fits `0.00200` per CZ instead: a 4.7× under-report.

---

## Summary

- RB over-reports for four reasons: the twirl converts coherent error into stochastic error (worst
  case can be 39× the RB number); random `n`-qubit Cliffords cost `O(n²/log n)` 2Q gates so the
  protocol cannot scale; isolated gates omit crosstalk; and multiplying fidelities is optimistic.
- **Mirror circuits** recover a scalable measurement: native layers, Pauli randomization, a central
  Pauli that randomises the target bit string, and a target from the stabilizer tableau. Score with
  effective polarization, not survival probability.
- **Volumetric benchmarks** give a capability region over `(w, d)`; QV and `#AQ` are points on it.
- **XEB** measures correlation with a Porter-Thomas distribution and costs `2ⁿ`; Sycamore's
  `F_XEB = 2.24 × 10⁻³` was extrapolated. **Application benchmarks** (QED-C, `#AQ`, BACQ) measure
  what users run, at the price of folding the vendor's compiler in.
- **Layer fidelity** is a product over disjoint layers; `EPLG = 1 - LF^{1/(N-1)}` exceeds EPG 2–3×.

---

## Exercises

**1.** A single-qubit gate's error is a pure over-rotation and RB reports `r = 5 × 10⁻⁴`. (a) Find
`θ`. (b) The gate is applied 200 times consecutively with no intervening randomization; compare the
accumulated infidelity with `1 - (1-r)²⁰⁰`. (c) What change would make the RB number predictive?

<details><summary>Solution</summary>

(a) `(2/3)sin²(θ/2) = 5×10⁻⁴` gives `sin(θ/2) = √(7.5×10⁻⁴) = 0.027386`, so `θ = 0.054779 rad`. (b)
The rotations add: `200θ = 10.956 rad`, accumulated infidelity `(2/3)sin²(5.478) = 0.3466` against
`1 - (1-5×10⁻⁴)²⁰⁰ = 0.0952`, so RB under-states by 3.6×. (The `m²r` rule would give `20`; it holds
only while `mθ ≪ 1`, and here the error has saturated.) (c) Insert random Pauli or Clifford layers
between repetitions: twirling makes the physical channel match the one RB characterises, turning
`m²` growth into `m` growth — which is why mirror circuits interleave Pauli layers.

</details>

**2.** A 3-qubit randomized mirror circuit yields Hamming-distance distribution
`h = (0.62, 0.24, 0.10, 0.04)` for `k = 0,1,2,3`. Compute the effective polarization, compare it
with the polarization inferred from the survival probability alone, and explain the sign of the
discrepancy.

<details><summary>Solution</summary>

`Σ_k (-1/2)^k h_k = 0.62 - 0.12 + 0.025 - 0.005 = 0.520`. With `n = 3` and `4ⁿ = 64` this gives
`S = 0.5124`, against `(2³ × 0.62 - 1)/7 = 0.5657` from the survival probability alone — 10.4%
higher. The naive estimator assumes errors scatter the output uniformly over all `2ⁿ - 1` wrong
strings; real errors are low-weight Paulis, so `h₁` and `h₂` far exceed their uniform values. The
weighted sum penalises that concentration, and the bias grows with `n` and depth.

</details>

**3.** A 127-qubit device reports `LF₁₀₀ = 0.19` on its best 100-qubit chain, while isolated
two-qubit RB on those pairs gives a median EPG of `0.7%`. (a) Compute `EPLG₁₀₀`. (b) What
fraction of the layered error is *not* explained by isolated gate error? (c) How long a chain could
this device support before layer fidelity falls below `1/e`?

<details><summary>Solution</summary>

(a) `EPLG = 1 - 0.19^{1/99} = 1 - exp(-0.016775) = 0.01664`, i.e. 1.66%. (b)
`0.01664 - 0.0070 = 0.00964`, so 58% of the layered error rate is contextual: crosstalk, idling and
spectator error, and a contiguous chain's unavoidable weakest links; `EPLG/EPG = 2.38` is typical.
(c) `(1 - EPLG)^{N-1} = 1/e` needs `N - 1 = 1/(-ln(1 - 0.01664)) = 59.6`, so `N ≈ 61` — the
100-qubit chain is well past where an unmitigated result carries signal.

</details>

**4.** A vendor publishes an `F_XEB` run on a 12-qubit random circuit of 200 two-qubit gates, where
500,000 samples have mean ideal probability `3.05 × 10⁻⁴`, plus a claim that its "99.9% two-qubit
fidelity" makes a 1000-gate algorithm run at 37% fidelity; its published `EPLG₁₀₀` is `1.2 × 10⁻²`.
(a) Compute `F_XEB` and the per-gate error the digital error model implies. (b) Redo the 1000-gate
estimate with EPLG. (c) Give the volumetric boundary and the maximum depth at width 16. (d) Why can
the `F_XEB` check not be repeated at 60 qubits, and what would you run instead?

<details><summary>Solution</summary>

(a) `D = 2¹² = 4096`, so `F_XEB = 4096 × 3.05×10⁻⁴ - 1 = 0.249` (a uniform sampler scores exactly
0); the digital error model gives `(1-e)²⁰⁰ = 0.25`, so `e = 1 - 0.25^{1/200} = 0.0069`. (b)
`(1 - 0.012)¹⁰⁰⁰ = 5.7 × 10⁻⁶`, not 0.37: 99.9% is an isolated-gate figure, and algorithms run gates
in layers. (c) The `1/e` contour is `w·d ≈ 2/ε = 167`; at `w = 16`, `d ≈ 10`, and
`exp(-0.012 × 16 × 10/2) = 0.38`, so the honest claim is "16 qubits, about 10 layers deep". (d)
`p_C(xᵢ)` needs each sampled string's amplitude — simulation of a 60-qubit circuit, the very cost
the benchmark demonstrates. Run randomized mirror circuits instead.

</details>

---

## Further Reading

1. **Proctor, T., Seritan, S., Rudinger, K., Nielsen, E., Blume-Kohout, R., and Young, K.** —
   "Scalable randomized benchmarking of quantum computers using mirror circuits," *Phys. Rev. Lett.*
   129, 150502 (2022). The construction, the effective-polarization estimator, and the `O(n²/log n)`
   obstruction to scaling standard RB.
2. **Blume-Kohout, R. and Young, K. C.** — "A volumetric framework for quantum computer benchmarks,"
   *Quantum* 4, 362 (2020). The shape grid and capability region, with quantum volume as one point.
3. **McKay, D. C. et al.** — "Benchmarking quantum processor performance at scale," arXiv:2311.05933
   (2023). Layer fidelity and EPLG: simultaneous direct RB, the disjoint-layer partition, and the
   `ibm_sherbrooke` / `ibm_montecarlo` numbers used here.
4. **Gao, X., Kalinowski, M., Chou, C.-N., Lukin, M. D., Barak, B., and Choi, S.** — "Limitations of
   linear cross-entropy as a measure for quantum advantage," *PRX Quantum* 5, 010334 (2024). When
   `F_XEB` tracks fidelity, and the spoofing strategies for when it does not.
5. **Lubinski, T. et al.** — "Application-oriented performance benchmarks for quantum computing,"
   *IEEE Trans. Quantum Eng.* 4, 3100032 (2023). The QED-C suite: circuit families, the
   normalised-fidelity metric, and the volumetric presentation `#AQ` derives from.
