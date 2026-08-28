# Photonic and Other Quantum Computing Platforms

> **Prerequisites**: Quantum mechanics postulates (Chapter 2), linear algebra (Chapter 1),
> basic optics (optional but helpful)
> **Connects to**: Measurement-based quantum computation (Chapter 3), bosonic codes (05/08),
> topological computation (08/04)

---

## Overview

Beyond superconducting qubits and trapped ions, several other physical platforms are under active
development for quantum computing. Each exploits different physical degrees of freedom, has
different error mechanisms, and offers distinct trade-offs in speed, scalability, connectivity,
and operating environment.

This chapter covers four major alternative platforms: photonic quantum computing (linear optics
and Boson sampling), nitrogen-vacancy (NV) centers in diamond, Rydberg atom arrays, and
topological qubits based on Majorana fermions. We also briefly survey silicon spin qubits.
Together, these platforms span the full range of current quantum computing research and
illustrate how different physical systems can implement the same abstract quantum computational
operations.

---

## Photonic Quantum Computing

### Photon Encoding Schemes

Light offers multiple degrees of freedom for encoding qubits:

- **Polarization**: `|0⟩ = |H⟩` (horizontal), `|1⟩ = |V⟩` (vertical). Simple, fast switching
  with wave plates and PBS. Limited scalability on-chip.
- **Path (dual-rail)**: `|0⟩ = |1,0⟩_{ab}` (photon in mode `a`, vacuum in `b`),
  `|1⟩ = |0,1⟩_{ab}`. Natural for integrated photonics; robust against loss detection.
- **Time-bin**: `|0⟩ = |early⟩`, `|1⟩ = |late⟩`. Compatible with optical fiber, good for
  quantum networks and long-distance communication.
- **Frequency/Mode**: encode in different frequency bins or spatial modes.

All encoding schemes can represent a qubit; the optimal choice depends on the application and
device architecture.

### Linear Optical Quantum Computing (LOQC)

The central challenge of photonic quantum computing: **photons do not interact with each other**
in linear optics. Two-qubit gates require interactions, which in linear optics can only be
induced via measurement (post-selection) using auxiliary photons.

The **KLM protocol** (Knill, Laflamme, Milburn, 2001) showed that universal quantum computing
is possible with:
1. Linear optical elements (beam splitters, phase shifters).
2. Single photon sources.
3. Photon number-resolving detectors.
4. Feed-forward (adaptive measurements based on earlier outcomes).

**KLM CNOT gate**: Built from two nonlinear-sign (NS) gates, each using an ancilla photon and
post-selection and each succeeding with probability `1/4`; the resulting CNOT/CZ succeeds with
probability `1/16`. Success can be boosted arbitrarily close to 1 using teleportation-based
protocols but at large ancilla cost.

**Scalability**: The overhead of KLM is significant. Efficient implementations require photon
number-resolving detectors, deterministic single photon sources, and very low-loss waveguides —
all challenging to achieve simultaneously.

### Fusion-Based Photonic Quantum Computing

**PsiQuantum and others** pursue **fusion-based quantum computing (FBQC)** (Bartolucci et al.,
2021): generate resource states (small entangled states of photons), then fuse them together
using linear optics measurements to create large cluster states, and perform measurement-based
quantum computation.

Key insight: probabilistic linear optics fusion can be boosted to near-unity success rates using
redundancy — if a fusion fails, use another resource state. The architecture is inherently
fault-tolerant.

**Advantage**: Operates at room temperature (photons don't need cryogenics); compatible with
telecom wavelengths for quantum networks; massive parallelism via time-multiplexing.

**Disadvantage**: Photon loss is the dominant error; silicon photonics loss `~0.1-1 dB/cm`;
fast photon number-resolving detectors are technically challenging; entangling rates are limited.

### Boson Sampling

**Boson sampling** (Aaronson-Arkhipov, 2011) is a specific computational problem that is
classically hard but naturally implemented by photons:

**Setup**: `n` single photons enter a linear interferometer (random unitary on `m ≫ n` modes).
Detect the output photon number pattern. The probability of any specific output is the permanent
of a submatrix of the unitary matrix:

```
P(output s | input r) = |Perm(U_{rs})|² / (r! s!)
```

Computing matrix permanents is #P-hard classically, making boson sampling classically
intractable for large `n`. Demonstrating boson sampling at scale provides evidence of quantum
computational advantage without implementing a full universal quantum computer.

**Gaussian boson sampling (GBS)**: Uses squeezed states instead of single photons; more
experimentally accessible. Xanadu's Borealis system (2022) demonstrated 216-mode GBS.

---

## NV Centers in Diamond

### Physical System

A **nitrogen-vacancy (NV) center** is a point defect in diamond: a substitutional nitrogen atom
adjacent to a vacancy, with an extra electron. The NV center has:

- **Electron spin S=1** ground state with zero-field splitting `D/2π = 2.87 GHz`.
- Spin states `|m_s = 0⟩` and `|m_s = ±1⟩`; the qubit uses `|0⟩ = |m_s=0⟩` and
  `|1⟩ = |m_s=-1⟩` (or `|m_s=+1⟩`).
- Optical transition at `637 nm` (zero-phonon line) with spin-selective fluorescence.

**Key advantage**: NV centers can operate at **room temperature** with coherence times of
milliseconds (and seconds for nuclear spin registers). No cryogenics required for the spin qubit.

### Gate Operations

Single-qubit gates: microwave pulses at `2.87 GHz - γ_e B` (Larmor frequency, adjusted for
magnetic field `B`). Gate times `~10-100 ns`.

Nuclear spin registers: Each NV center has neighboring `¹³C` nuclear spins (natural abundance
1.1%, or isotopically purified) that can be used as ancilla/memory qubits. Nuclear spin
coherence `T₂ ~ 1-100 ms` at room temperature.

Two-qubit gates: mediated by dipole-dipole coupling between NV centers, or via shared optical
fiber/waveguide for remote entanglement. Optical interconnects enable a **quantum network
architecture**: NV centers separated by meters can be entangled by photon emission, transmission,
and detection.

### Limitations

- **Qubit density**: NV centers are dilute in diamond; spacing `~30-100 nm` prevents addressing
  individual NVs with diffraction-limited optics without near-field probes.
- **Scalability**: two-qubit gates between NV centers require proximity or optical networking;
  scaling beyond `~10` physical qubits is challenging.
- **Optical indistinguishability**: the zero-phonon line has low efficiency (~3% at room temp);
  cryogenic cooling to `4 K` boosts ZPL emission to `~10-30%` but sacrifices the room-temp advantage.

**Primary application**: Quantum sensing (magnetometry, nanoscale NMR), quantum networks and
quantum repeaters, not necessarily large-scale quantum computing.

---

## Rydberg Atom Arrays

### Physical Setup

**Rydberg atoms** are neutral atoms (typically Rb or Cs) excited to very high principal quantum
numbers `n ~ 50-100`. A Rydberg atom has an exaggerated electric dipole moment:

```
d ∝ n² a₀     (dipole moment scales as n²)
```

Rydberg atoms experience **van der Waals** (or resonant dipole-dipole) interactions at ranges of
`1-10 μm`:

```
V(r) = C₆/r⁶   where C₆ ∝ n¹¹
```

**Rydberg blockade**: If two atoms within `r_blockade ~ 5-10 μm` are both excited, the interaction
`V(r) ≫ Ω` (Rabi frequency) prevents both from being in the Rydberg state simultaneously. This
is the basis for two-qubit gates.

### Tweezer Arrays

Neutral atoms are held in **optical tweezer arrays**: focused laser beams that create strong
attractive potentials via the AC Stark effect. Programmable tweezer arrays allow arbitrary
2D and 3D geometries with `~100-1000` atoms:

- **Lukin group (Harvard)**: Demonstrated `~300` qubit arrays with reconfigurable geometry.
- **Atom Computing**: 1180-site tweezer array.
- **QuEra Computing**: Commercial Aquila system with `~256` qubits.

**Qubit encoding**: `|0⟩ = |g⟩` (ground state), `|1⟩ = |r⟩` (Rydberg state) for "Rydberg
qubits"; or two hyperfine ground states (`|↑⟩`, `|↓⟩`) for "atomic qubits" with optical
Rydberg excitation for two-qubit gates.

### Rydberg Blockade Gate

The **CZ gate** via Rydberg blockade:
1. Apply `π` pulse to control qubit: `|0⟩_c → |0⟩_c`, `|1⟩_c → |r⟩_c`.
2. Apply `2π` pulse to target: if control is in `|r⟩`, blockade prevents target excitation and
   the target acquires no phase (`+1`); if control is in `|0⟩`, target completes the full `2π`
   rotation and acquires phase `-1`.
3. Apply `π` pulse to control: de-excite.

Net effect on `|1,0⟩, |0,1⟩, |0,0⟩`: phase `-1`, `-1`, `+1` → diagonal gate with `|1,1⟩ → -|1,1⟩`:
this is the **CZ gate** (up to single-qubit phase corrections).

**Gate fidelity**: `~99.0-99.5%` (current best).
**Gate time**: `~0.5-5 μs`.

### Mid-Circuit Measurement and Reconfiguration

A key advantage of Rydberg arrays: atoms can be moved ("reconfigured") mid-circuit, allowing
dynamic connectivity changes. This enables:
- **Long-range gates** without SWAP networks (shuttle atoms to interact).
- **Mid-circuit measurement**: measure a subset of atoms and feed forward.
- **Non-planar connectivities**: arbitrary graphs via atom rearrangement.

The Lukin group (Bluvstein et al., 2023) demonstrated logical-qubit circuits in a Rydberg
array — including a transversal CNOT between a pair of distance-7 surface codes, and sampling
circuits on 48 logical qubits encoded in [[8,3,2]] color-code blocks.

---

## Topological Qubits (Majorana Zero Modes)

### Concept

**Topological qubits** store quantum information in non-local, topologically protected degrees
of freedom. The standard approach uses **Majorana zero modes (MZMs)**: boundary states of a
topological superconductor that are their own antiparticles (`γ† = γ`).

**Kitaev chain** (2001): A 1D model of spinless p-wave superconductor with open boundaries hosts
MZMs at its ends in the topological phase. The two MZMs at the ends together form a single
fermionic mode that is **non-locally stored** — no local perturbation can flip it without affecting
both ends.

### Noise Protection

The topological protection of MZMs means:
- **Local perturbations** (e.g., flux noise, charge noise at one end) cannot affect the logical
  state, since information is stored non-locally.
- The qubit lifetime scales **exponentially** with the separation between the two MZM ends.

The MZMs are non-Abelian anyons: braiding two MZMs implements a unitary gate on the degenerate
ground space (see Chapter 08/04). In principle, a universal gate set could be implemented purely
by braiding (topologically protected), with no need for careful pulse calibration.

### Experimental Status

Microsoft has pursued Majorana-based topological qubits as their primary quantum computing
strategy. A 2023 Microsoft paper (*Phys. Rev. B*) reported observing topological gaps and local
spectral signatures consistent with Majorana modes in InAs nanowire-superconductor devices.

However, implementing a topological qubit suitable for quantum computation requires:
1. **Braiding operations**: physically moving MZMs around each other — not yet demonstrated.
2. **Long coherence**: demonstrated exponential suppression of noise with separation.
3. **Scalable device fabrication**: integrating many topological wires.

As of 2025, topological qubits remain pre-experimental (demonstrated signatures, not full qubit
operations). Microsoft's "topological qubit" announcement (2025) remains under peer scrutiny.

---

## Silicon Spin Qubits

### Physical Platform

Silicon spin qubits use the electron or nuclear spin of dopant atoms (phosphorus, arsenic) or
quantum dot-confined electrons in silicon or silicon-germanium heterostructures.

**Advantages**: Leverage mature semiconductor fabrication; potential for high-density qubit arrays;
long nuclear spin coherence; compatible with classical electronics integration.

**Qubit types**:
- **Spin-1/2 quantum dot**: single electron in a gate-defined quantum dot.
- **Singlet-triplet qubit**: two-electron spin state.
- **Nuclear spin**: `³¹P` donor nuclear spin, `T₂ > 1` s.

**Gate fidelity** (UNSW, Intel): Single-qubit `> 99.9%`; two-qubit `~ 99.5%` (exchange gate).
**Gate time**: `1-100 ns`.

**Challenges**: Qubit variability from fabrication disorder; operating at `~ 20-100 mK` (like
superconducting); precise control of exchange coupling between dots.

---

## Platform Comparison Summary

| Platform | T₁ | Gate speed | Fidelity (2Q) | Connectivity | T_operate |
|----------|-----|-----------|--------------|-------------|-----------|
| Superconducting | 100 μs | 20-200 ns | 99-99.8% | Local 2D | 15 mK |
| Trapped ion | 1-1000 s | 50-500 μs | 99.6-99.9% | All-to-all | Room T + laser |
| Photonic | ∞ (no decay) | ~1 ns | ~95%+ | Programmable | Room T |
| Rydberg array | ~1 s | 0.5-5 μs | 99.0-99.5% | Programmable 2D | Room T + laser |
| NV center | ms | 1-100 μs | ~90-95% | Limited | Room T |
| Silicon spin | 1 ms | 1-100 ns | ~99.5% | Local | 20-100 mK |
| Topological | (theoretically ∞) | – | (not yet) | – | mK |

---

## Key Formulas

- **Boson sampling probability**: `P(s|r) = |Perm(U_{rs})|² / (r!s!)`
- **Rydberg blockade radius**: `r_b = (C₆/Ω)^{1/6}` where `Ω` is Rabi frequency
- **NV zero-field splitting**: `D/2π = 2.87 GHz`
- **Rydberg dipole moment**: `d ~ n² a₀` (scales as `n²`)
- **Kitaev Majorana wire**: open boundary MZMs `γ₁, γ₂` with `{γᵢ, γⱼ} = 2δᵢⱼ`

---

## Worked Example: Rydberg Blockade Gate Fidelity

**Parameters**: `Rb` atoms excited to the `n = 70` Rydberg level, atom separation `r = 3 μm`,
gate Rabi rate `Ω/2π = 2 MHz`.

**Blockade strength**: `V = C₆/r⁶`, where for Rb `70S`: `C₆/h ≈ 870 GHz·μm⁶`.

```
V/h = 870×10⁹ / 3⁶ = 870×10⁹ / 729 ≈ 1.2 × 10⁹ Hz = 1.2 GHz
```

**Blockade condition**: `V/(ℏΩ) ≈ 1.2 GHz / 2 MHz = 600 ≫ 1`. ✓ Strong blockade regime.

**Main error sources**:
1. **Finite blockade**: double-excitation leakage `ε_b ~ (Ω/V)² ≈ (1/600)² ≈ 3 × 10^{-6}`.
   Negligible at this spacing.
2. **Rydberg state decay**: the `70S` lifetime at room temperature (including blackbody
   redistribution) is `τ ≈ 150 μs`. The blockade-gate pulse sequence has total area `~4π`,
   so `t ≈ 4π/Ω = 2/( Ω/2π ) = 1 μs`. With roughly half the population in the Rydberg state
   during the gate: `p_decay ~ 0.5 × t/τ = 0.5 × 10^{-6}/1.5×10^{-4} ≈ 3 × 10^{-3}`.
3. **Laser phase noise, intensity noise, and Doppler shifts**: typically contribute at the
   `~10^{-3}` level in current experiments.

**Estimated gate fidelity**: `1 - ε ≈ 99.5%`, dominated by Rydberg decay and laser noise —
consistent with the best published blockade-gate fidelities (`99.0-99.5%`). Note what the
budget implies: increasing `Ω` shortens the gate and reduces decay error, but eats into the
blockade ratio `V/Ω`; the optimum balances the two, which is why groups push to larger `C₆`
(higher `n`) and smaller, colder, better-localized atom pairs.

---

## Summary

- **Photonic qubits**: room-temperature operation, intrinsically networkable, but two-qubit gates
  require ancilla photons and are inherently probabilistic (KLM, FBQC); boson sampling provides
  a near-term quantum advantage demonstration.
- **NV centers in diamond**: room-temperature qubits with ms coherence; ideal for quantum sensing
  and networks, limited scalability for computing.
- **Rydberg atom arrays**: programmable 2D geometry, all-to-all connectivity via atom shuttling,
  good gate fidelities; leading platform for quantum simulation and growing for gate-based QC.
- **Topological qubits (Majorana)**: theoretically ideal for fault tolerance, but no functioning
  qubit demonstrated yet (2025); long-term bet.
- **Silicon spin qubits**: CMOS-compatible, high-density potential, improving fidelities; viable
  long-term contender especially for industrial scale.

---

## Exercises

**1.** Estimate the Rydberg blockade radius `r_b = (C₆/ℏΩ)^{1/6}` for Rb `70S` atoms
(`C₆/h ≈ 870 GHz·μm⁶`) driven at `Ω/2π = 2 MHz`.

<details><summary>Solution</summary>

Working in frequency units (the `h` factors cancel):
`r_b = (870×10⁹ Hz·μm⁶ / 2×10⁶ Hz)^{1/6} = (4.35×10⁵)^{1/6} μm ≈ 8.7 μm`.
Any pair of atoms closer than `~8.7 μm` is deep in the blockade regime for this drive
strength; typical tweezer spacings of `3-5 μm` sit comfortably inside it. Note the extremely
weak 1/6-power dependence: changing `Ω` by a factor of 64 moves `r_b` by only 2×.

</details>

**2.** A photonic circuit requires 3 KLM-style CZ gates (each succeeding with probability
`1/16`) to all succeed in a single post-selected run. What is the success probability, and how
many runs are needed on average? What architectural idea rescues linear-optics computing from
this scaling?

<details><summary>Solution</summary>

`P = (1/16)³ = 1/4096 ≈ 2.4×10⁻⁴`, so `~4096` runs on average — and the cost grows as `16^G`
in the number of gates. The rescue is *offline* preparation with feed-forward: probabilistic
gates are used to grow entangled resource states (cluster states) ahead of time, retrying
failures without touching the computation, and the actual computation proceeds by
deterministic single-photon measurements (measurement-based/fusion-based QC).

</details>

**3.** In a boson sampling experiment, two photons enter modes 1 and 2 of an interferometer;
the relevant 2×2 submatrix of the mode unitary is `U_sub = [[0.6, 0.8], [-0.8, 0.6]]`.
Compute the probability of detecting one photon in each of the two output modes.

<details><summary>Solution</summary>

`Perm(U_sub) = (0.6)(0.6) + (0.8)(-0.8) = 0.36 - 0.64 = -0.28`.
`P = |Perm|²/(1!1!·1!1!) = 0.0784`. Compare the classical (distinguishable-particle) value,
which uses the permanent of the element-wise squared matrix:
`0.36×0.36 + 0.64×0.64 = 0.539`. The suppression (7.8% vs. 54%) is two-photon interference —
the same physics as the Hong-Ou-Mandel dip, and the effect that makes permanents (not
determinants) appear.

</details>

**4.** An NV center sits in a magnetic field `B = 10 mT` aligned with the NV axis. Using
`γ_e/2π ≈ 28 GHz/T`, compute the transition frequencies `|0⟩ → |m_s = ±1⟩` given the
zero-field splitting `D/2π = 2.87 GHz`. Why does the field make the two transitions separately
addressable?

<details><summary>Solution</summary>

Zeeman shift: `γ_e B/2π = 28 GHz/T × 0.01 T = 280 MHz`. The transitions split to
`D ± γ_eB: 2.87 + 0.28 = 3.15 GHz` and `2.87 - 0.28 = 2.59 GHz`. With 560 MHz separation —
far larger than typical MHz-scale Rabi rates — a microwave tone addresses one transition
without driving the other, turning the S = 1 ground state into a well-defined two-level qubit
(`|m_s = 0⟩` and one chosen `|m_s = ±1⟩` level).

</details>

---

## Further Reading

1. **Knill, E., Laflamme, R., and Milburn, G. J.** — "A scheme for efficient quantum computation
   with linear optics," *Nature* 409, 46 (2001). KLM protocol.
2. **Aaronson, S. and Arkhipov, A.** — "The computational complexity of linear optics,"
   *STOC 2011*. Boson sampling hardness.
3. **Jaksch, D. et al.** — "Fast quantum gates for neutral atoms," *Phys. Rev. Lett.* 85, 2208
   (2000). Rydberg blockade gate proposal.
4. **Doherty, M. W. et al.** — "The nitrogen-vacancy colour centre in diamond," *Phys. Rep.*
   528, 1 (2013). Comprehensive NV center review.
5. **Kitaev, A. Yu.** — "Unpaired Majorana fermions in quantum wires," *Phys. Usp.* 44 (suppl.),
   131 (2001). Kitaev chain and Majorana zero modes.
