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

**KLM CNOT gate**: Uses 2 ancilla photons and post-selection. The gate succeeds with probability
`1/4` when using `n+2` modes for an `n`-photon input. Success can be boosted arbitrarily close
to 1 using teleportation-based protocols but at large ancilla cost.

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
2. Apply `2π` pulse to target: if control is in `|r⟩`, blockade prevents target excitation (picks
   up phase `+1` from failed excitation → phase π back); if control is in `|0⟩`, target completes
   `2π` rotation (phase `-1`).
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

Lukin group (2023) demonstrated 48-qubit error-corrected logical qubits (surface code and
transversal CNOT) in a Rydberg array.

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
strategy. A 2023 Nature paper from Microsoft reported observing topological gaps and local
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

**Parameters**: `Rb` atoms at `n=70` Rydberg level, atom separation `r = 5 μm`, gate Rabi rate
`Ω/2π = 1 MHz`.

**Blockade strength**: `V/h = C₆/r⁶` where for `n=70` Rb: `C₆ ≈ 2π × 10^{17} rad/s·μm⁶`.

```
V/h = 10^{17} / (5^6) = 10^{17} / 15625 ≈ 6.4 × 10^{12} Hz = 6.4 THz
```

**Blockade condition**: `V/Ω ≈ 6.4 THz / 1 MHz = 6.4 × 10^6 ≫ 1`. ✓ Strong blockade regime.

**Main error sources**:
1. **Finite blockade**: gate error `ε_b ≈ (Ω/V)² ≈ (10^6/6.4×10^{12})² ≈ 2.4 × 10^{-14}`. Negligible.
2. **Rydberg state decay**: Rydberg lifetime `τ_n ≈ n³ × τ₁ ≈ (70)³ × 10^{-8} s ≈ 3.4 ms`.
   Gate time `t ≈ 3/(2Ω) = 3/(4π×10^6) ≈ 240 ns`.
   Decay probability: `p_decay ≈ t/τ = 240×10^{-9}/3.4×10^{-3} ≈ 7 × 10^{-5}`. Small.
3. **Laser phase noise and intensity fluctuations**: typically dominates at `~10^{-3}` level.

**Estimated gate fidelity**: `~ 99.0-99.5%` (laser noise limited), consistent with experiment. ✓

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
