# Superconducting Qubits

> **Prerequisites**: Quantum harmonic oscillator, basic circuit theory (capacitors, inductors),
> quantum mechanics postulates (Chapter 2)
> **Connects to**: Trapped ion comparison (07/02), benchmarking (07/04), surface code
> implementation (05/06), VQA noise (06/06)

---

## Overview

Superconducting qubits are the dominant platform for large-scale quantum computing in industry.
Google's Sycamore processor (53 qubits, 2019 supremacy demonstration), IBM's Osprey (433 qubits,
2022), and Google's Willow (105 qubits, 2024) are all superconducting. The platform combines
several favorable properties: GHz-frequency operation matching room-temperature microwave
electronics, mature lithographic fabrication, microsecond coherence times adequate for hundreds
of gate operations, and a highly developed theoretical framework.

The central element of a superconducting qubit is the **Josephson junction** — a thin insulating
layer between two superconductors that exhibits quantum tunneling of Cooper pairs. The Josephson
junction provides the essential nonlinearity that transforms an ordinary LC circuit (which has
equally spaced energy levels — a harmonic oscillator) into an anharmonic oscillator with a
finite gap between the `|0⟩ → |1⟩` and `|1⟩ → |2⟩` transitions. This anharmonicity is what
makes the two lowest levels addressable as a qubit.

This chapter develops the physical theory of the transmon qubit (the most widely used design),
explains readout and control, and discusses the engineering realities of dilution refrigerators
and fabrication.

---

## Josephson Junction Physics

### Cooper Pair Tunneling

Below the critical temperature `Tc` (e.g., `Tc ≈ 1.2 K` for aluminum), electrons form Cooper
pairs (charge `2e`, spin 0) that condense into a macroscopic quantum state described by a
single phase `φ`. Across a Josephson junction (thin insulating barrier between two
superconductors), Cooper pairs tunnel, producing:

**Josephson relations**:
```
I = I_c sin(φ)           (current-phase relation)
V = (ℏ/2e) dφ/dt        (voltage-phase relation)
```

where `φ = φ₁ - φ₂` is the phase difference across the junction and `I_c` is the critical
current. These two relations define a **nonlinear inductor**: the energy stored is
`E = -E_J cos(φ)` where `E_J = I_c ℏ/(2e)` is the Josephson energy.

### Circuit Quantization

The Josephson junction in parallel with a capacitor `C` forms the basic qubit circuit. Treating
`φ` as a quantum variable (conjugate to the charge `Q = 2en` where `n` is the Cooper pair
number):

```
[n̂, φ̂] = i
```

The Hamiltonian:
```
H = 4E_C (n̂ - n_g)² - E_J cos(φ̂)
```

where `E_C = e²/(2C)` is the charging energy and `n_g` is a gate charge offset (from nearby
voltage sources).

---

## The Transmon Qubit

### The E_J/E_C Ratio

The behavior of the circuit Hamiltonian depends critically on the dimensionless ratio `E_J/E_C`:

- **E_J/E_C ≪ 1** (Cooper pair box regime): eigenstates are nearly definite charge states. The
  qubit frequency is strongly charge-dependent → highly sensitive to charge noise.
- **E_J/E_C ≫ 1** (transmon regime): the cosine potential creates a deep well; eigenstates are
  nearly harmonic oscillator states with exponentially suppressed charge dispersion.

The **transmon** (Koch et al., 2007) operates at `E_J/E_C ≈ 50-100`, achieved by using a
large shunting capacitor. This suppresses charge noise by a factor `~e^{-√(8E_J/E_C)}`,
transforming the charge noise sensitivity from `~E_C` to `~e^{-\sqrt{8E_J/E_C}} E_C`
— exponentially small.

### Energy Levels and Anharmonicity

Expanding the cosine potential for `E_J/E_C ≫ 1`:
```
-E_J cos(φ) ≈ -E_J + E_J φ²/2 - E_J φ⁴/24 + ...
```

The `φ²` term gives a harmonic oscillator; the `-φ⁴/24` term is the anharmonic correction.
Using the harmonic oscillator solution:

**Qubit transition frequency**:
```
ω₀₁/2π ≈ √(8 E_J E_C) / h ≈ 4-6 GHz (typical)
```

**Anharmonicity**:
```
α = ω₁₂ - ω₀₁ ≈ -E_C/ℏ ≈ -100 to -300 MHz
```

The negative anharmonicity means the `|1⟩ → |2⟩` transition is red-detuned from the
`|0⟩ → |1⟩` transition. This allows driving qubit transitions at `ω₀₁` without accidentally
exciting the `|2⟩` level, as long as the pulse bandwidth is less than `|α|`.

### Typical Parameters

| Parameter | Typical value |
|-----------|--------------|
| `E_J/E_C` | 50–100 |
| Qubit frequency `ω₀₁/2π` | 4–6 GHz |
| Anharmonicity `|α|/2π` | 100–300 MHz |
| Coherence `T₁` | 50–500 μs (2025) |
| Coherence `T₂` | 20–200 μs |
| Single-qubit gate time | 10–50 ns |
| Two-qubit gate time | 20–200 ns |
| Single-qubit gate error | `~10^{-3}–10^{-4}` |
| Two-qubit gate error | `~10^{-3}–10^{-2}` |

---

## Qubit Control

### Microwave Drive

The qubit is driven by a microwave signal at frequency `ω_d ≈ ω₀₁`. In the rotating frame,
the drive Hamiltonian is:

```
H_drive = (Ω/2)(cos(δt + φ) X - sin(δt + φ) Y)
```

where `δ = ω_d - ω₀₁` is the detuning and `Ω` is the Rabi rate (proportional to drive amplitude).
On-resonance (`δ = 0`) with phase `φ = 0`: `H = (Ω/2) X` → Rabi oscillation. Setting
`Ωτ = π` gives an X gate in time `τ = π/Ω`.

**IQ control**: Real implementations use in-phase (I) and quadrature (Q) channels, allowing
arbitrary single-qubit rotations:

```
U(θ, φ) = exp(-i θ/2 (cos φ · X + sin φ · Y))
```

by controlling `Ω_I = Ω cos φ` and `Ω_Q = Ω sin φ`.

### DRAG Pulse Shaping

The standard Gaussian pulse shape `Ω(t) = Ω₀ exp(-(t-t₀)²/2σ²)` has sidebands near `ω₀₁ ± α`,
which can drive transitions to `|2⟩`. The DRAG technique adds a correction to the quadrature
channel:

```
Ω_X(t) = Ω_0(t)
Ω_Y(t) = -λ/Δ · dΩ_X/dt
```

where `Δ = -α` is the anharmonicity and `λ ≈ 0.5` is empirically optimized. DRAG reduces
leakage errors by ~`10×` for `Δt ~ 20 ns` pulses.

---

## Two-Qubit Gates

### Cross-Resonance Gate

The **cross-resonance (CR) gate** (used in IBM systems) drives qubit A at the frequency of
qubit B. Due to the coupling between qubits, this creates an effective `ZX` interaction:

```
H_CR = (ω_ZX/2) Z_A X_B
```

After time `t = π/(2ω_ZX)`, this implements `CNOT` (up to single-qubit corrections). The CR
gate requires `~200-400 ns` on IBM hardware.

### Flux-Tuned Gates (iSWAP Family and CZ)

**Parametric modulation** (used in Google and Rigetti systems) tunes the qubit frequency via
a flux pulse to bring two qubits into resonance momentarily:

```
H_int = J(t) (a₁†a₂ + a₁a₂†)
```

On resonance this XY (excitation-hopping) coupling generates **iSWAP-family** gates: activating
it for time `t = π/(4J)` gives `√iSWAP`, and `t = π/(2J)` gives `iSWAP`. A **CZ gate** is
obtained differently, via the transmon's third level: flux-tuning the pair to the
`|11⟩ ↔ |20⟩` avoided crossing, where the coupling matrix element is `√2·J`, lets `|11⟩`
complete one full cycle in time `t ≈ π/(√2 J)` and return with an extra phase of `-1` — a
controlled-phase gate. CZ gates take `~20-100 ns` and achieve fidelity `99.0-99.7%` on current
hardware.

### iSWAP and √iSWAP

Google's Sycamore processor natively implemented `fSim(π/2, π/6)` — an iSWAP-like gate with an
additional conditional phase; later Google devices have used the `√iSWAP` gate:

```
√iSWAP = [[1, 0,     0,     0  ],
           [0, 1/√2, i/√2,  0  ],
           [0, i/√2, 1/√2,  0  ],
           [0, 0,    0,     1  ]]
```

Two `√iSWAP` gates compose to `iSWAP`, equivalent to `SWAP` up to Z rotations. This native
gate set enables the random quantum circuits used in quantum supremacy demonstrations.

---

## Readout

### Dispersive Coupling

Qubit state readout uses a **resonator** (microwave cavity) coupled to the qubit via the
**dispersive coupling** (Blais et al., 2004). When the resonator frequency `ω_r` is far
detuned from the qubit frequency `ω₀₁` (dispersive limit `|ω_r - ω₀₁| ≫ g` where `g` is
the coupling):

```
H_disp = ωr a†a + ω₀₁ σ_z/2 + χ σ_z a†a
```

The **dispersive shift** `χ` (typically `χ/2π ~ 1-5 MHz`) shifts the resonator frequency by
`±χ` depending on the qubit state. By probing the resonator at frequency `ω_r` with a weak
coherent drive, the phase or amplitude of the reflected/transmitted signal indicates the qubit state.

**Measurement time**: A standard dispersive readout pulse takes `~100-500 ns` and achieves
assignment fidelity `~95-99%`.

**Quantum non-demolition (QND)**: Dispersive readout is approximately QND — it preserves the
qubit state in the `{|0⟩, |1⟩}` basis after measurement. In practice, measurement-induced
state transitions (photon number-dependent dephasing) reduce QND fidelity.

---

## Dilution Refrigerator

Superconducting qubits require operation at temperatures `T ~ 10-20 mK`, achieved by a
**dilution refrigerator** (DR). The required temperature is set by the qubit energy scale:
`kT ≪ ℏω₀₁`, i.e., `T ≪ ℏ(5 GHz)/k_B = 240 mK`. Operating at `15 mK` gives thermal
photon occupation `n_th = 1/(e^{ℏω/kT} - 1) ≈ e^{-16} ≈ 10^{-7}` — effectively zero.

**Dilution refrigerator stages**:
- 300 K (room temperature)
- 77 K (liquid nitrogen pre-cooling)
- 4 K (pulse tube cooler)
- 800 mK (first dilution stage)
- 50 mK (cold plate)
- **10-15 mK** (mixing chamber — where qubits live)

**Wiring**: Microwave lines from room-temperature electronics to the mixing chamber require
careful design — attenuation to thermalize input noise, isolators to prevent reflected
signals from reaching qubits, and quantum-limited amplifiers (HEMT, JTWPA) for readout signal
amplification.

---

## Key Formulas

- **Josephson relations**: `I = I_c sinφ`, `V = (ℏ/2e) dφ/dt`
- **Transmon Hamiltonian**: `H = 4E_C n̂² - E_J cos φ̂`
- **Qubit frequency**: `ω₀₁ ≈ √(8 E_J E_C) / ℏ`
- **Anharmonicity**: `α ≈ -E_C / ℏ`
- **Dispersive shift**: `H_disp ∋ χ σ_z a†a`, shifts resonator by `±χ` depending on qubit state
- **Charge noise suppression**: sensitivity `∝ e^{-√(8 E_J/E_C)}` in transmon regime

---

## Worked Example: Transmon Design Parameters

**Specification**: Design a transmon with `ω₀₁/2π = 5 GHz`, `|α|/2π = 200 MHz`.

**Step 1**: From `α ≈ -E_C/ℏ`:
```
E_C/h = |α| = 200 MHz → E_C = h × 200 MHz = 6.626 × 10^{-34} × 2×10^8 = 1.32 × 10^{-25} J
```

**Step 2**: From `ω₀₁ ≈ √(8 E_J E_C)/ℏ`:
```
(2π × 5×10^9)² = (8 E_J E_C) / ℏ²
E_J = ℏ² (2π × 5×10^9)² / (8 E_C) = (1.055×10^{-34})² × (3.14×10^{10})² / (8 × 1.32×10^{-25})
    = 1.11×10^{-68} × 9.87×10^{20} / (1.06×10^{-24})
    ≈ 1.03 × 10^{-23} J = h × 15.6 GHz
```

**Step 3**: `E_J/E_C = 15.6 GHz / 0.2 GHz = 78`. This is well in the transmon regime (`≫ 1`). ✓

**Step 4**: Capacitance from `E_C = e²/(2C)`:
```
C = e²/(2 E_C) = (1.6×10^{-19})² / (2 × 1.32×10^{-25}) = 2.56×10^{-38} / 2.64×10^{-25} ≈ 97 fF
```
This is a realistic value for a lithographic capacitor (shunting capacitance `~100 fF`). ✓

**Step 5**: Critical current from `E_J = I_c ℏ/(2e)`:
```
I_c = 2e E_J / ℏ = 2 × 1.6×10^{-19} × 1.03×10^{-23} / 1.055×10^{-34} ≈ 31 nA
```
This corresponds to a Josephson junction area of `~0.04 μm²` — consistent with standard
electron-beam lithography fabrication for Al/AlOx/Al junctions.

---

## Summary

- The **Josephson junction** provides the essential nonlinearity (`E = -E_J cosφ`) that creates
  the anharmonic transmon qubit.
- The **transmon** operates at `E_J/E_C ≈ 50-100`, achieving exponentially suppressed charge
  noise sensitivity while retaining `|α|/2π ≈ 100-300 MHz` anharmonicity.
- Control via IQ microwave drive at `ω₀₁`; DRAG pulse shaping reduces leakage to `|2⟩`.
- Two-qubit gates: cross-resonance (IBM), parametric CZ (Google/Rigetti), `√iSWAP` (Google).
- Readout via dispersive coupling to a resonator: qubit state shifts resonator frequency by `±χ`.
- Operation at `10-20 mK` in a dilution refrigerator; dilution refrigerator physics is a
  critical engineering bottleneck for scaling.

---

## Exercises

**1.** Design a transmon with `ω₀₁/2π = 4.5 GHz` and anharmonicity `α/2π = -250 MHz`.
Compute `E_C`, `E_J` (in frequency units), the ratio `E_J/E_C`, the shunt capacitance `C`, and
the junction critical current `I_c`.

<details><summary>Solution</summary>

`E_C/h = |α|/2π = 250 MHz`. From `ℏω₀₁ ≈ √(8E_JE_C)`:
`E_J/h = (ω₀₁/2π)²/(8 · E_C/h) = (4.5 GHz)²/(8 × 0.25 GHz) = 10.13 GHz`.
`E_J/E_C = 10.13/0.25 = 40.5` — transmon regime, though with more residual charge dispersion
than a 5 GHz/200 MHz design (`E_J/E_C = 78`).
`C = e²/(2E_C) = (1.602×10⁻¹⁹)²/(2 × 6.626×10⁻³⁴ × 2.5×10⁸) ≈ 77 fF`.
`I_c = 2eE_J/ℏ = 2 × 1.602×10⁻¹⁹ × (6.626×10⁻³⁴ × 1.013×10¹⁰)/1.055×10⁻³⁴ ≈ 20 nA`.

</details>

**2.** For the 4.5 GHz transmon operating at `T = 20 mK`, compute `ℏω₀₁/k_BT` and the thermal
photon occupation `n_th = 1/(e^{ℏω/k_BT} - 1)`. What residual `|1⟩` population does this imply?

<details><summary>Solution</summary>

`ℏω/k_BT = (6.626×10⁻³⁴ × 4.5×10⁹)/(1.381×10⁻²³ × 0.02) ≈ 10.8`.
`n_th ≈ e^{-10.8} ≈ 2×10⁻⁵`. Thermal equilibrium would give ~0.002% excited population —
negligible. (Measured residual populations on real devices are typically `0.1-1%`, dominated
by non-equilibrium quasiparticles and noise from higher-temperature stages leaking down the
wiring, not by the mixing chamber temperature.)

</details>

**3.** A dispersive readout uses `χ/2π = 2 MHz` and a resonator linewidth `κ/2π = 4 MHz`.
The qubit-state-dependent phase of the reflected probe is `φ_± = ±arctan(2χ/κ)`. Compute the
total phase separation between `|0⟩` and `|1⟩`.

<details><summary>Solution</summary>

`2χ/κ = 1`, so `φ_± = ±45°` and the separation is `2 × arctan(1) = 90°`. This is the
optimum regime (`2χ ≈ κ`): larger `κ` washes out the phase contrast, much smaller `κ` slows
the resonator response and lengthens measurement relative to `T₁`.

</details>

**4.** A single-qubit X gate uses a resonant drive with `Ω/2π = 20 MHz`. (a) What is the
`π`-pulse duration? (b) Roughly what pulse bandwidth does this imply, and is a DRAG correction
needed for a transmon with `|α|/2π = 200 MHz`?

<details><summary>Solution</summary>

(a) `τ = π/Ω = 1/(2 × 20 MHz) = 25 ns`.
(b) Bandwidth `~1/τ = 40 MHz`. This is only 5× smaller than `|α|/2π = 200 MHz`, so the pulse
spectrum has non-negligible weight at the `|1⟩→|2⟩` transition (detuned by `α`): leakage is
suppressed but not negligible, and DRAG correction is worthwhile — it is standard on all
production transmon systems at these gate speeds. Slowing the gate reduces leakage but costs
more decoherence per gate; DRAG breaks that trade-off.

</details>

---

## Further Reading

1. **Koch, J. et al.** — "Charge-insensitive qubit design derived from the Cooper pair box,"
   *Phys. Rev. A* 76, 042319 (2007). Original transmon paper.
2. **Blais, A. et al.** — "Cavity quantum electrodynamics for superconducting electrical
   circuits," *Phys. Rev. A* 69, 062320 (2004). Circuit QED and dispersive readout.
3. **Krantz, P. et al.** — "A quantum engineer's guide to superconducting qubits," *Appl.
   Phys. Rev.* 6, 021318 (2019). Comprehensive engineering review. The key reference.
4. **Arute, F. et al.** — "Quantum supremacy using a programmable superconducting processor,"
   *Nature* 574, 505 (2019). Sycamore 53-qubit supremacy demonstration.
5. **Place, A. P. M. et al.** — "New material platform for superconducting transmon qubits with
   coherence times exceeding 0.3 milliseconds," *Nature Communications* 12, 1779 (2021).
   State-of-the-art coherence.
