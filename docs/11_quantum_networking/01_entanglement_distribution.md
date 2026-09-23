# Entanglement Distribution

> **Prerequisites**: Bell states and nonlocality (02/04), density matrices and quantum channels
> (02/05), fidelity (02/10), teleportation and resource accounting (08/02), QKD and the
> repeaterless bound (04/08), photonic platforms and NV centers (07/03)
> **Connects to**: Repeaters and distillation (11/02), distributed quantum computing (11/03),
> quantum capacity (08/02)

---

## Overview

Every quantum network protocol reduces to one primitive: **two distant parties holding a shared
entangled pair of known, high fidelity**. Once Alice and Bob hold `|Φ⁺⟩`, teleportation moves
qubits (08/02), telegates apply nonlocal operations (11/03), and measuring in mutually unbiased
bases yields a secret key (04/08). The network layer's only job is to manufacture ebits.

That job is hard for one reason: **photon loss is exponential in distance and no-cloning forbids
amplification**. A classical link answers attenuation with erbium-doped amplifiers every 80 km; a
quantum link cannot, because an amplifier that copies the signal would clone an unknown state,
which the no-cloning theorem (08/02) rules out for any technology. Every quantum signal must cross
the fibre unassisted, with probability `10^{-αL/10}` at `α ≈ 0.2 dB/km` — `10⁻²⁰` at 1000 km.

The resolution is not to fight loss but to *detect* it. **Heralded** generation arranges for a
classical detector click to announce, after the fact, that a pair was created; failures are loud
and cheap, so loss becomes a rate penalty instead of a fidelity penalty — and rates are
recoverable by parallelism, while fidelity is not. **Entanglement swapping** then chains short
heralded links into long ones, replacing the exponential in `L` by an exponential in the much
smaller segment length. This chapter develops the elementary link: the loss law and what the
repeaterless bound forbids, the two heralding families and the trade between them, the Bell state
measurement they depend on and its 50% ceiling, swapping, and fidelity budgets for a chain.

---

## Why Direct Transmission Fails

### The Exponential Loss Law

Attenuation in single-mode fibre at 1550 nm is roughly `α = 0.2 dB/km`, so the transmittance of a
length `L` — the probability an injected photon reaches the far end — is

```
η(L) = 10^{-αL/10}        (1/e attenuation length ≈ 21.7 km)
```

| `L` (km) | `η` | pairs/s from a 10 GHz source |
|---|---|---|
| 100 | `10⁻²` | `10⁸` |
| 500 | `10⁻¹⁰` | `1` |
| 800 | `10⁻¹⁶` | one per 11.6 days |
| 1000 | `10⁻²⁰` | one per 317 years |

Metro distances are fine; continental ones are not an engineering problem. Three orders of
magnitude of extra source brightness buys 150 km.

### What the Repeaterless Bound Forbids

Cleverness in the protocol does not help either. The **PLOB bound** (Pirandola, Laurenza,
Ottaviani and Banchi, 2017), quoted in 04/08, fixes the two-way assisted quantum and secret-key
capacity of the pure-loss channel exactly:

$$C(\eta) = -\log_2(1-\eta) \;\approx\; \frac{\eta}{\ln 2} \approx 1.44\,\eta \quad (\eta \ll 1)$$

This is a capacity, not an artifact of one protocol: no point-to-point scheme, however many rounds
of classical communication it uses, exceeds `1.44 η` ebits (or secret bits) per channel use. At
800 km, `C = 1.44 × 10⁻¹⁶` caps even a 10 GHz source at one ebit every 8.0 days.

The classical fix is forbidden twice over. A deterministic amplifier `|ψ⟩ → |ψ⟩^{⊗2}` is a
cloner; a phase-insensitive linear amplifier of gain `G` is allowed but necessarily injects at
least `G-1` units of vacuum noise, cancelling the gain in every entanglement measure. The
information-theoretic form is the antidegradability argument of 08/02: a pure-loss channel with
`η ≤ 1/2` hands the environment a copy at least as good as the receiver's, so its one-way quantum
capacity is exactly zero. Loss below 3 dB is the only regime in which quantum information flows
forward at all — a number that returns in 11/02 as the third-generation repeater design rule.

---

## Heralded Entanglement Generation

An **elementary link** joins two neighbouring nodes, each holding a matter qubit (an NV center
electron spin, a trapped ion, a rare-earth ion, a neutral atom) with an optical interface. Each
node emits a photon entangled with its qubit, the photons meet at a station, and a detection
pattern **heralds** success. The heralding signal is classical and unambiguous: with no valid
click the attempt never happened and the qubits are reset, so loss never degrades the delivered
state — it only lowers the probability one is delivered. Placing the station at the **midpoint**
halves the fibre each photon crosses, which is why links herald in the middle.

### Single-Photon (Single-Click) Schemes

Cabrillo *et al.* (1999) weakly excite both nodes, so each is in
`√(1-α_e)|↓, vac⟩ + √α_e|↑, 1⟩` with `α_e ≪ 1`. The two optical modes are combined on a 50:50
beamsplitter and one click at either output port heralds. Because the beamsplitter erases which
node emitted, a click projects the spins onto `(|↓↑⟩ ± |↑↓⟩)/√2`. The success probability is
**linear** in the per-arm efficiency:

```
p_1ph ≈ 2 α_e η_arm
```

The price is the term where *both* nodes emitted and one photon was lost: that also gives exactly
one click, heralding the unentangled `|↑↑⟩`. Its relative weight is `≈ α_e`, so `F_1ph ≈ 1 - α_e`
— rate and fidelity trade off linearly through the single knob `α_e`. The scheme is also
**phase-sensitive**: the relative optical phase of the two arms enters the heralded state directly
and must be stabilized to a fraction of a wavelength over tens of kilometres.

### Two-Photon (Barrett-Kok) Schemes

Barrett and Kok (2005) trade rate for robustness. Each node emits deterministically into
`(|↓,0⟩ + |↑,1⟩)/√2`, and success requires **two** detections in successive rounds with the spins
flipped between them. Round one projects onto the one-photon subspace (weight `1/2`) and needs one
detection; round two has exactly one excitation and needs one more:

```
p_2ph = ½ η_arm²
```

The double-excitation error is removed by the second round rather than suppressed by a small
amplitude, so fidelity is not rate-limited, and only the slow relative phase *between rounds*
matters. Setting `p_1ph = p_2ph` gives the crossover `½η_arm² = 2α_e η_arm`, i.e. `η_arm = 4α_e`.
With a typical `α_e = 0.05` the two-photon scheme wins only above `η_arm = 0.2` — under about 7 dB of
total loss per arm. Real links are nowhere near that: tens-of-percent collection plus tens of
kilometres of fibre put `η_arm` near `10⁻²`. This is why the highest reported elementary-link rates
— the 39 Hz of Humphreys *et al.* (2018) between two NV centers — use the single-photon scheme and
pay for it with active phase stabilization, while the first loophole-free Bell test (Hensen *et
al.*, 2015: 245 trials over 220 hours at 1.3 km) used two-photon heralding for its phase immunity.

---

## Bell-State Measurement

A **Bell state measurement** (BSM) projects two qubits onto `{|Φ⁺⟩, |Φ⁻⟩, |Ψ⁺⟩, |Ψ⁻⟩}`. In circuit
form it is `CNOT`, then `H` on the control, then a computational readout of both qubits; the two
outcome bits are the pair's **phase parity** and **flip parity**. It drives teleportation (08/02),
heralding and swapping alike, and for matter qubits inside one node it is deterministic.

A *photonic* BSM cannot be. Send two polarization-encoded photons into a 50:50 beamsplitter:

- `|Ψ⁻⟩` is the only antisymmetric state, so the photons leave by *different* ports — a
  coincidence between the two output detectors identifies it uniquely.
- `|Ψ⁺⟩` sends both to the *same* port with orthogonal polarizations — a coincidence between that
  port's two polarization channels identifies it uniquely.
- `|Φ⁺⟩` and `|Φ⁻⟩` both send two identically polarized photons into one port, giving the same
  pattern. They are indistinguishable.

Two of four outcomes are resolved. Lütkenhaus, Calsamiglia and Suominen (1999) and Calsamiglia and
Lütkenhaus (2001) proved this is not a failure of ingenuity: with linear optics, vacuum ancillas
and photon counting, the maximum success probability of a complete photonic BSM is exactly `1/2`.
Beating it needs a nonlinearity, exponentially many ancilla photons, or matter qubits that turn
the problem back into a local gate. A 50% BSM at every swap in a chain of `2ⁿ` segments means all
`2ⁿ - 1` swaps succeed together with probability `2^{-(2ⁿ-1)}` — `1/128` for eight segments — which
is why repeaters need memories that let a failed swap be retried without discarding the chain.

---

## Entanglement Swapping

Żukowski, Zeilinger, Horne and Ekert (1993) observed that teleporting *half of an entangled pair*
transfers entanglement rather than a state. Alice and repeater `R` share `|Φ⁺⟩_{A,B₁}`; `R` and
Charlie share `|Φ⁺⟩_{B₂,C}`. Both of `R`'s qubits are local, so `R` performs a BSM on `(B₁, B₂)`
and broadcasts two bits; Charlie applies `X^{m_flip} Z^{m_phase}`, and `A` and `C` — who never
interacted — hold `|Φ⁺⟩`:

```
|Φ⁺⟩_{A,B₁} ⊗ |Φ⁺⟩_{B₂,C}  --BSM(B₁,B₂) + 2 cbits-->  |Φ⁺⟩_{A,C}
```

Verified on qiskit 2.5.2, with the measurements deferred into controlled corrections:

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity

# 0 = A (Alice), 1 = B1, 2 = B2 (both at the repeater), 3 = C (Charlie).
qc = QuantumCircuit(4)
qc.h(0); qc.cx(0, 1)        # elementary pair |Phi+> on (A, B1)
qc.h(2); qc.cx(2, 3)        # elementary pair |Phi+> on (B2, C)
qc.barrier()
qc.cx(1, 2); qc.h(1)        # Bell-state measurement on (B1, B2)
qc.cx(2, 3)                 # X correction on C, controlled by the parity bit
qc.cz(1, 3)                 # Z correction on C, controlled by the phase bit

rho_AC = partial_trace(Statevector(qc), [1, 2])
phi_plus = Statevector([1, 0, 0, 1]) / 2 ** 0.5
print("F(rho_AC, Phi+) =", round(state_fidelity(rho_AC, phi_plus), 12))
# F(rho_AC, Phi+) = 1.0
```

### Fidelity Composition

Swapping is not free: the output is strictly worse than either input. Write each elementary pair as
a **Werner state** `ρ_W = W|Φ⁺⟩⟨Φ⁺| + (1-W) I/4`, whose fidelity is `F = ⟨Φ⁺|ρ_W|Φ⁺⟩ = (1+3W)/4`.

Direct density-matrix simulation of the swap (ideal BSM, corrections applied, all four outcomes
summed) shows the output is again Werner with the **product** parameter `W_out = W₁W₂`, so `N`
identical segments deliver

$$W_N = \left(\frac{4F-1}{3}\right)^{\!N}, \qquad F_N = \frac{1 + 3 W_N}{4}$$

The Werner parameter decays *geometrically* in the segment count while the fidelity falls toward
its floor of `1/4`. With `F = 0.99` per link: `F₂ = 0.9801`, `F₄ = 0.9608`, `F₈ = 0.9236`,
`F₁₆ = 0.8550`; with `F = 0.95` the chain crosses `F = 1/2` at `N = 16`. Swapping alone cannot
build an arbitrarily long link — it must be interleaved with distillation (11/02).

---

## Key Formulas

- **Fibre transmittance**: `η(L) = 10^{-αL/10}`, `α ≈ 0.2 dB/km` at 1550 nm
- **Repeaterless (PLOB) capacity**: `C(η) = -log₂(1-η) ≈ 1.44 η` ebits or secret bits per use
- **Zero-capacity loss**: one-way quantum capacity vanishes for `η ≤ 1/2` (3 dB, antidegradable)
- **Single-photon heralding**: `p ≈ 2 α_e η_arm`, `F ≈ 1 - α_e`, phase-sensitive
- **Two-photon (Barrett-Kok) heralding**: `p = ½ η_arm²`, phase-insensitive
- **Crossover**: two-photon beats single-photon in rate iff `η_arm > 4 α_e`
- **Linear-optics BSM**: at most 2 of 4 Bell states resolved, `p_max = 1/2`
- **Werner fidelity**: `F = (1+3W)/4`, `W = (4F-1)/3`
- **Swapping**: `W_out = ∏ᵢ Wᵢ`, hence `F_N = (1 + 3W^N)/4` for `N` identical segments
- **Waiting time, `n` parallel links**: `E[max of n Geom(p)] ≈ H_n/p`, `H_n = Σ_{k=1}^{n} 1/k`

---

## Worked Example: An 800 km Chain of Eight Heralded Links

**Problem.** Build an 800 km link from eight 100 km segments, each heralded at its midpoint. Per
arm: collection efficiency `η_c = 0.50`, detector efficiency `η_d = 0.90`, 50 km of fibre at
0.2 dB/km, Barrett-Kok heralding, signals at `c/n = 2 × 10⁸ m/s`. Swapping is deterministic; all
eight links run in parallel and memories hold each finished link until all eight are up.
Elementary-link fidelity is `F = 0.99`. Find the end-to-end rate, the memory time, the delivered
fidelity, and the advantage over PLOB at 800 km.

**Solution.**

*(a) Per-arm efficiency and heralding probability.* Each photon crosses 50 km, so
`η_fibre = 10^{-0.2·50/10} = 0.100`:

```
η_arm = η_c · η_fibre · η_d = 0.50 × 0.100 × 0.90 = 0.0450
p     = ½ η_arm² = ½ (0.0450)² = 1.0125 × 10⁻³
```

*(b) Attempt period.* An attempt ends only when the herald returns from the midpoint, a cycle over
`2 × 50 km`:

```
t₀ = 100 × 10³ / (2 × 10⁸) = 5.00 × 10⁻⁴ s = 0.500 ms   ⟹   2000 attempts/s
```

One elementary link therefore yields `p/t₀ = 2.025` ebits/s.

*(c) End-to-end rate.* The chain is ready when the *slowest* of eight i.i.d. geometric variables
succeeds. Exact summation of `E[max] = Σ_{k≥0}[1 - (1-(1-p)^k)^8]` gives `2683.4` attempts, against
the harmonic estimate `H₈/p = 2684.3`:

```
T_chain = 2683.4 × 0.500 ms = 1.342 s        R_chain = 0.745 ebits/s
```

*(d) Memory requirement.* The first link to succeed waits on average the full `1.342 s` for its
slowest sibling, plus `4.0 ms` of one-way classical latency across 800 km. Coherence lasting
**seconds** is the binding requirement — which is why the storage qubit is an NV nuclear spin or a
rare-earth ensemble, not the electron spin that talks to photons.

*(e) Fidelity.* Seven swaps compose eight Werner links with `W = (4 × 0.99 - 1)/3 = 0.986667`:

```
W₈ = 0.986667⁸ = 0.898181        F₈ = (1 + 3 × 0.898181)/4 = 0.9236
```

*(f) Comparison with PLOB.* At 800 km, `η = 10⁻¹⁶` and `C = 1.4427 × 10⁻¹⁶` ebits/use, capping a
10 GHz repeaterless source at `1.4427 × 10⁻⁶` ebits/s — one per 8.0 days. The chain beats it by

```
0.745 / (1.4427 × 10⁻⁶) ≈ 5.2 × 10⁵
```

**Reading the result.** The advantage comes entirely from the exponent: the chain pays
`10^{-0.2·50/10}` per arm instead of `10^{-0.2·800/10}` end to end. But `F = 0.9236` is useless for
computation (11/03: a 6.1% gate error) and marginal even for QKD. Heralding and parallelism solved
the rate; only distillation (11/02) fixes fidelity.

---

## Summary

- Fibre loss is exponential, `η(L) = 10^{-αL/10}` with `α ≈ 0.2 dB/km`, and no-cloning forbids
  amplification; the PLOB bound `C = -log₂(1-η) ≈ 1.44η` caps *every* point-to-point protocol at
  8.0 days per ebit over 800 km, even at 10 GHz
- **Heralding** turns loss from a fidelity problem into a rate problem: a classical click announces
  success after the fact, failures are discarded, mid-point stations halve the fibre
- **Single-photon** schemes give `p ≈ 2α_e η_arm` at `F ≈ 1 - α_e` and need interferometric phase
  stability; **two-photon (Barrett-Kok)** schemes give `p = ½η_arm²` with phase immunity, winning
  on rate only when `η_arm > 4α_e`, which real links never reach
- The **Bell state measurement** underlies heralding, swapping and teleportation; linear optics
  caps it at 50% (only `|Ψ⁺⟩` and `|Ψ⁻⟩` resolvable), forcing memories into any multi-segment chain
- **Entanglement swapping** consumes two ebits and 2 cbits to produce one over twice the distance;
  Werner parameters *multiply*, `W_out = W₁W₂`, so `F = 0.99` per link decays to `0.9236` over
  eight segments
- An 800 km, eight-segment chain with realistic optics delivers `≈ 0.75` ebits/s at `F ≈ 0.92` —
  a `5 × 10⁵` rate advantage over PLOB, at a fidelity that still needs distillation (11/02)

---

## Exercises

**Exercise 1**: A 10 GHz entangled-photon source feeds a fibre with `α = 0.2 dB/km`. (a) Give the
transmittance and delivered pair rate at 400 km and 800 km. (b) Compare each with PLOB at the same
distance and clock. (c) What clock rate would a repeaterless system need for one ebit per second
at 800 km, and why is that not an engineering target?

<details><summary>Solution</summary>

(a) `η(400) = 10⁻⁸` → `100` pairs/s. `η(800) = 10⁻¹⁶` → `10⁻⁶` pairs/s, one per `10⁶ s ≈ 11.6` days.

(b) `C = 1.4427η`. At 400 km, `144` ebits/s; at 800 km, `1.4427 × 10⁻⁶` ebits/s, one per 8.0 days.
The bound sits only 1.44× above naive direct transmission — no protocol recovers the lost exponent.

(c) `R = 1/(1.4427 × 10⁻¹⁶) = 6.9 × 10¹⁵` Hz — about 36× the 193 THz carrier frequency of 1550 nm
light. Not merely hard but physically incoherent: the cleanest demonstration that brightening the
source cannot solve the problem.

</details>

**Exercise 2**: Elementary links have `F = 0.95`. (a) Give the fidelity after composing 4 and 8
segments. (b) Find the smallest `N` for which end-to-end fidelity falls below `1/2`. (c) A
protocol needs `F_end ≥ 0.99` over 8 segments — what per-link fidelity does that require?

<details><summary>Solution</summary>

(a) `W = (4 × 0.95 - 1)/3 = 0.933333`; `W⁴ = 0.758835` → `F₄ = 0.819126`, `W⁸ = 0.575830` →
`F₈ = 0.681872`.

(b) `F_N < 1/2` needs `W^N < 1/3`, i.e. `N > ln(1/3)/ln(0.933333) = 15.92`, so `N = 16`
(`F₁₆ = 0.498685`); `N = 15` still gives `F₁₅ = 0.516448`.

(c) `F_end = 0.99` needs `W_end = 0.986667`, so `W_link = 0.986667^{1/8} = 0.998324` and
`F_link = 0.998743`. Needing 99.87% per link to reach 99% over eight hops is the quantitative
statement that swapping *amplifies* infidelity, and why distillation is mandatory.

</details>

**Exercise 3**: A node pair can run either heralding scheme; the single-photon scheme uses
emission amplitude `α_e`. (a) Derive the efficiency at which they have equal success probability.
(b) For `α_e = 0.05`, express that crossover as a loss budget in dB per arm. (c) At
`η_arm = 0.045` (the worked example's 100 km link), which scheme is faster, by how much, and what
does it cost?

<details><summary>Solution</summary>

(a) `½η_arm² = 2α_e η_arm` gives `η_arm = 4α_e`.

(b) `4 × 0.05 = 0.20`, i.e. `10 log₁₀(1/0.20) = 6.99 dB` per arm for collection, fibre and
detection combined. Real links spend more than that on collection alone.

(c) `p_1ph = 2 × 0.05 × 0.045 = 4.50 × 10⁻³` versus `p_2ph = ½(0.045)² = 1.0125 × 10⁻³`: the
single-photon scheme is `4.44×` faster. It costs `F ≈ 1 - α_e = 0.95` and phase-stabilized fibre
arms, since the heralded state's relative phase *is* the optical path difference. Lowering `α_e` to
0.01 restores `F ≈ 0.99` but drops the advantage to `0.89×` — below parity. This trade is the whole
design space of the elementary link.

</details>

**Exercise 4**: A chain of 8 segments uses photonic BSMs at every swap. (a) With a linear-optics
BSM, what is the probability all swaps succeed in one shot? (b) If a failed swap destroys only the
two pairs it consumed while the survivors stay in memory, why does the architecture change
qualitatively? (c) The elementary links also need a BSM to herald — does the 50% ceiling bite
there too?

<details><summary>Solution</summary>

(a) Eight segments need `7` swaps: `2⁻⁷ = 1/128 ≈ 0.0078`. Sixteen segments (15 swaps) give
`2⁻¹⁵ ≈ 3.05 × 10⁻⁵`.

(b) Without memory one failure restarts the whole chain, so the success probability is the product
over all swaps and the rate collapses exponentially in the segment count. With memory a failed swap
is retried on its own sub-chain while the rest waits, so the cost becomes an expected number of
retries *per nesting level* and the exponential in `N` becomes polynomial. Memory is what makes a
repeater a repeater rather than a very slow direct link.

(c) It applies, but harmlessly: heralding need only recognize one unambiguous success pattern, and
discarding the rest costs a constant factor already folded into `p = ½η²`. At a swap the consumed
pairs were expensive, so a 50% loss compounds across levels.

</details>

**Exercise 5**: Redesign the worked example with 200 km segments (midpoint at 100 km), keeping
`η_c = 0.50`, `η_d = 0.90` and Barrett-Kok heralding. (a) Give the per-arm efficiency, success
probability and attempt period. (b) What is the single-link rate? (c) Doubling the segment length
divides the rate by what, and why does that not settle the design question?

<details><summary>Solution</summary>

(a) `η_fibre(100 km) = 10⁻²`, so `η_arm = 0.50 × 0.01 × 0.90 = 4.50 × 10⁻³` and
`p = ½(4.5 × 10⁻³)² = 1.0125 × 10⁻⁵`; the cycle covers `2 × 100 km`, giving
`t₀ = 200 × 10³/(2 × 10⁸) = 1.00 ms` and 1000 attempts/s.

(b) `R = p/t₀ = 1.0125 × 10⁻²` ebits/s — one pair every `98.8 s`, against `2.025` ebits/s at
100 km.

(c) A factor of 200. Efficiency enters squared, so doubling the segment length costs
`10^{2 × 0.2 × 50/10} = 100×` in `p`, and the doubled round trip costs another `2×` in attempt
rate. Two-photon heralding therefore pushes hard toward *short* segments — but short segments mean
more nodes, more swaps and more accumulated infidelity (Exercise 2). That tension is what repeater
architecture design is about.

</details>

---

## Further Reading

1. **Azuma, Economou, Elkouss, Hilaire, Jiang, Lo & Tzitrin** — "Quantum repeaters: From quantum
   networks to the quantum internet," *Rev. Mod. Phys.* 95, 045006 (2023). Sections II-III cover
   loss, heralding and swapping in the order used here; the definitive modern review.
2. **Żukowski, Zeilinger, Horne & Ekert** — "'Event-ready-detectors' Bell experiment via
   entanglement swapping," *Phys. Rev. Lett.* 71, 4287 (1993). The original swapping proposal.
3. **Cabrillo, Cirac, García-Fernández & Zoller** — "Creation of entangled states of distant atoms
   by interference," *Phys. Rev. A* 59, 1025 (1999). Single-photon heralding and its trade-off.
4. **Barrett & Kok** — "Efficient high-fidelity quantum computation using matter qubits and linear
   optics," *Phys. Rev. A* 71, 060310(R) (2005). The two-round, phase-insensitive protocol.
5. **Calsamiglia & Lütkenhaus** — "Maximum efficiency of a linear-optical Bell-state analyzer,"
   *Appl. Phys. B* 72, 67 (2001). Proof of the 1/2 ceiling and its ancilla-assisted generalization.
