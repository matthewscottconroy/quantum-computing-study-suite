# Quantum Repeaters and Entanglement Distillation

> **Prerequisites**: Entanglement distribution, swapping and the Werner budget (11/01), density
> matrices and quantum channels (02/05), fidelity (02/10), why QEC is hard (05/01), QKD and the
> repeaterless bound (04/08), quantum capacity (08/02)
> **Connects to**: Distributed quantum computing (11/03), surface code (05/06), bosonic codes
> (05/08), photonic platforms and NV centers (07/03)

---

## Overview

Chapter 11/01 left a link that works and a link that is useless. Heralding and parallelism fixed
the *rate* — an 800 km chain of eight heralded segments gives about `0.75` ebits/s against the
`1.4 × 10⁻⁶` the PLOB bound allows any repeaterless scheme. But swapping multiplies Werner
parameters, so eight segments at `F = 0.99` deliver `F = 0.9236`, and nothing in that architecture
pushes it back up. A quantum repeater is the machine that can: **heralded links, a way to raise
fidelity, and memories to hold intermediate results while the probabilistic parts are retried**.

Raising fidelity without a quantum channel to a referee is the hard part. Error correction in the
usual sense (05/01) puts encoder and decoder on the same side of the noise; here Alice and Bob hold
halves of a noisy pair and may only use local operations and classical communication (LOCC).
**Entanglement distillation** is the LOCC answer: consume two noisy pairs, measure a parity
sensitive to the noise but not to the encoded entanglement, keep the survivor when the parities
agree. It is probabilistic, destroys at least half the input, and works above a fidelity
threshold — provided the local operations are good enough.

This chapter states the PLOB bound precisely and shows how one midpoint node converts `η` into
`√η`; develops distillation from Bell-diagonal states through BBPSSW to DEJMPS, every fidelity
checked against a full density-matrix simulation; classifies repeaters into three generations,
derives the 3 dB rule, and lists what a quantum memory must do.

---

## The Rate-Distance Problem

### The Bound, Precisely

For the pure-loss bosonic channel of transmittance `η`, Pirandola, Laurenza, Ottaviani and Banchi
(2017) proved that the two-way assisted quantum capacity and the secret-key capacity coincide and
equal

$$C(\eta) \;=\; -\log_2(1-\eta) \;\approx\; 1.44\,\eta \quad (\eta \ll 1)$$

Two words carry the weight. *Two-way assisted*: Alice and Bob may exchange unlimited free
classical communication, adaptively, in as many rounds as they like. *Capacity*: an achievable
optimum, not a bound on one protocol. What it does **not** cover is a third party with a quantum
device between them — and that loophole is the entire business model of a repeater.

### How One Node Changes the Exponent

Put a station at the midpoint of a link of length `2L`. Because the loss law is exponential,
`η(L) = 10^{-αL/10} = √(10^{-α(2L)/10}) = √η(2L)`, any architecture whose end-to-end rate is
proportional to the *segment* transmittance scales as `√η` of the full distance. At 500 km with
`α = 0.2 dB/km`, `η = 10⁻¹⁰` while `√η = 10⁻⁵` — a factor of `10⁵`. Nesting `n` levels gives
`η^{1/2ⁿ}`.

Two milestones live in this gap. **Twin-field QKD** (Lucamarini *et al.*, 2018) achieves `√η`
scaling with a *classical* midpoint — single-photon interference at an untrusted station, no
memory — and is why fibre QKD records reach many hundreds of kilometres. **Memory-enhanced QKD**
(Bhaskar *et al.*, 2020) used a silicon-vacancy centre in a nanophotonic cavity as a genuine
quantum memory and beat the repeaterless bound for its channel. Neither is a full repeater; both
show the bound is a law about point-to-point links, not about nature.

The cost of the midpoint is latency. In first- and second-generation designs every swap waits for
a herald to cross the segment, so the top nesting level cannot cycle faster than `L/c`: at 1000 km
in fibre (`c/n = 2 × 10⁸ m/s`), `5 ms` one way and `10 ms` round trip, a ceiling of about 100
end-to-end attempts per second before any probability factors. Removing that wait is what
third-generation repeaters are for.

---

## Entanglement Distillation

### The Problem Statement

Alice and Bob hold `n` copies of a noisy `ρ` with `F = ⟨Φ⁺|ρ|Φ⁺⟩ < 1` and may use only LOCC. A
**distillation** (or purification) protocol outputs `k < n` pairs of higher fidelity. For two
qubits every entangled state is distillable, and a Werner state is entangled exactly when
`W > 1/3`, i.e. `F > 1/2`; below that, no protocol can help.

### Bell-Diagonal States and Twirling

A general two-qubit state has 15 parameters; distillation is analyzed on the four-parameter
**Bell-diagonal** family `ρ = A|Φ⁺⟩⟨Φ⁺| + B|Ψ⁻⟩⟨Ψ⁻| + C|Ψ⁺⟩⟨Ψ⁺| + D|Φ⁻⟩⟨Φ⁻|` with
`A + B + C + D = 1` and `A = F`. This is no loss of generality: a random bilateral Pauli `P ⊗ P`
(shared randomness, hence LOCC) kills the off-diagonal Bell terms without changing `A`. Averaging
over random `U ⊗ U*` instead — a **Werner twirl** — forces `B = C = D = (1-F)/3`, reducing the
state to the Werner state of the same fidelity. Twirling throws information away.

### BBPSSW

Bennett, Brassard, Popescu, Schumacher, Smolin and Wootters (1996) twirl to Werner form, then run
the **bilateral CNOT**: Alice applies `CNOT` from her first qubit to her second, Bob does the same,
both measure the second pair in `Z`, and they keep the first pair when the outcomes agree. For a
Werner input, with `q = (1-F)/3`, this gives `F' = (F² + q²)/p` at `p = F² + 2Fq + 5q²`. The output
is not Werner, so BBPSSW twirls again before the next round — which is where it loses.

### DEJMPS

Deutsch, Ekert, Jozsa, Macchiavello, Popescu and Sanpera (1996) keep the bilateral CNOT but
prepend a **bilateral rotation**: `R_x(π/2)` on both of Alice's qubits, `R_x(-π/2)` on both of
Bob's, and no twirling. On the Bell basis that rotation is a permutation — it fixes `|Φ⁺⟩` and
`|Ψ⁺⟩` and **swaps `|Ψ⁻⟩ ↔ |Φ⁻⟩`** — while the bilateral CNOT merges Bell states of equal flip
parity, fusing `{|Φ⁺⟩, |Φ⁻⟩}` into `|Φ⁺⟩` and `{|Ψ⁺⟩, |Ψ⁻⟩}` into `|Ψ⁺⟩`. Composing the two gives
the exact map (checked below against a full density-matrix simulation to `6 × 10⁻¹⁶`):

$$N = (A+B)^2 + (C+D)^2, \quad A' = \frac{A^2+B^2}{N}, \quad B' = \frac{2CD}{N}, \quad
C' = \frac{C^2+D^2}{N}, \quad D' = \frac{2AB}{N}$$

with `p_success = N`. The rotation is not cosmetic: without it the bilateral CNOT pairs `A` with
`D`, and after one round `D` is the *second largest* coefficient, so round two combines the two
largest weights and the fidelity collapses. From a Werner state at `F = 0.80`:

| round | plain bilateral CNOT | BBPSSW (twirl each round) | DEJMPS |
|---|---|---|---|
| 1 | 0.838150 | 0.838150 | 0.838150 |
| 2 | 0.755888 | 0.873585 | 0.943639 |
| 3 | 0.631391 | 0.904540 | 0.987974 |
| 4 | 0.534527 | 0.930048 | 0.996854 |

All three agree on round 1 — for a Werner input the rotation permutes equal coefficients — and
diverge immediately after. DEJMPS wins because the asymmetry BBPSSW twirls away is precisely the
resource the rotation exploits.

### Threshold and Cost

On the Werner line `F = 1/2` is an exact fixed point of the DEJMPS map, which increases above it
and decreases below: `0.45 → 0.440871`, `0.50 → 0.500000`, `0.55 → 0.560345`.

Each round consumes two pairs and succeeds with probability `p`, so the expected input pairs per
output pair obeys `c_k = 2c_{k-1}/p_k` with `c_0 = 1`; `2^k` is unavoidable and the `1/p_k` factors
are the price of probabilism. All of this assumes perfect local gates, and the second threshold
that assumption hides is usually the binding one: with local error `ε`, each round injects noise as
well as removing it and the protocol acquires a **fixed point below 1**, saturating at `F_max(ε)`.
Briegel, Dür, Cirac and Zoller (1998) showed this makes repeaters an engineering problem rather
than an impossibility proof — budgets of `10⁻²` to `10⁻³` already give useful `F_max`.

---

## The Three Repeater Generations

Muralidharan *et al.* (2016) classify repeaters by how they handle *loss* and how they handle
*operation errors*, which together fix the communication pattern and therefore the rate.

| | loss | operation errors | classical comms | memory time | limiting rate |
|---|---|---|---|---|---|
| **1G** | heralding | distillation | two-way, every level | `≳ L/c` | `∝ c/L` × probabilities |
| **2G** | heralding | QEC | two-way for loss only | `≳ L₀/c` | `∝ c/L₀` |
| **3G** | QEC | QEC | one-way | gate time only | local gate speed |

**First generation** is the Briegel-Dür-Cirac-Zoller architecture: heralded links, nested
swapping, distillation interleaved at each level. Every level waits for a herald from the level
below, so the rate carries a `c/L` factor and memories must hold for the end-to-end round trip.

**Second generation** replaces distillation with quantum error correction on encoded Bell pairs.
Operation errors are corrected one-way inside each station, so only loss needs two-way signalling —
over one *segment*, not the chain. Memory requirements drop from `L/c` to `L₀/c` and the rate stops
depending on total distance.

**Third generation** corrects loss itself with a code (quantum parity codes, tree codes,
Gottesman-Kitaev-Preskill encodings), transmits one-way, and never waits for a herald, so the rate
is limited only by decoder speed. The price is hundreds to thousands of qubits per station,
fault-tolerant local error rates, and a hard constraint on segment loss.

### The 3 dB Rule

A pure-loss channel with `η ≤ 1/2` is antidegradable — the environment's output is at least as
good as the receiver's — so its one-way quantum capacity is exactly zero (08/02), and no loss code
transmits through it. Third-generation stations must therefore sit closer than `L_max = 3 dB / α`.
At `α = 0.2 dB/km` that is `15 km`, so a 1000 km link needs about 67 segments and 66 stations; at
`α = 0.5 dB/km` it drops to `6 km` and 166 stations. The 3 dB rule, not the qubit count, is what
makes 3G an infrastructure problem.

---

## Quantum Memories

A repeater memory must do four conflicting things at once.

1. **Hold long enough** — `≈ 1.3 s` for the eight parallel 1G links of 11/01, but only `L₀/c`
   (`0.5 ms` for a 100 km segment) for 2G.
2. **Talk to photons efficiently** — the optical interface *is* the `η_arm` of 11/01, entering the
   two-photon heralding rate squared.
3. **Support local gates** — swapping needs a Bell measurement, distillation a CNOT between two
   stored pairs; a write-only memory is not a repeater node.
4. **Multiplex** — many modes per node cut the waiting time roughly as `1/n_modes`.

The platforms split these tasks. NV and SiV centres in diamond use the electron spin as optical
interface and nearby `¹³C` nuclear spins as memory — Bradley *et al.* (2019) demonstrated a
ten-qubit register with nuclear-spin coherence beyond a minute under dynamical decoupling. Trapped
ions give the best local gates and readout. Rare-earth-doped crystals (Eu:YSO, Pr:YSO) and atomic
ensembles multiplex heavily through atomic frequency combs, at the cost of harder local processing.
No platform leads on all four axes, which is why network and computing experiments still use
different hardware.

---

## Key Formulas

- **PLOB (repeaterless) capacity**: `C(η) = -log₂(1-η) ≈ 1.44η` ebits or secret bits per use
- **Midpoint advantage**: `η(L) = √η(2L)`; nesting `n` levels gives `η^{1/2ⁿ}`
- **Bell-diagonal state**: `(A, B, C, D)` on `(|Φ⁺⟩, |Ψ⁻⟩, |Ψ⁺⟩, |Φ⁻⟩)`, `A = F`
- **BBPSSW (Werner input, `q = (1-F)/3`)**: `F' = (F² + q²)/p`, `p = F² + 2Fq + 5q²`
- **DEJMPS**: `N = (A+B)² + (C+D)² = p_success`; `A' = (A²+B²)/N`, `B' = 2CD/N`,
  `C' = (C²+D²)/N`, `D' = 2AB/N`
- **Distillability (two qubits)**: possible iff entangled; Werner iff `W > 1/3`, i.e. `F > 1/2`
- **Pair cost**: `c_k = 2 c_{k-1}/p_k`, `c_0 = 1`; deterministic floor `2^k`
- **3 dB rule (3G)**: spacing `L_max = 3/α` km (15 km at 0.2 dB/km); **latency ceiling (1G/2G)**:
  at most `c/(2L)` end-to-end attempts per second

---

## Worked Example: DEJMPS from `F = 0.80`

**Problem.** Two nodes share Werner pairs at `F = 0.80` with perfect local gates. Run DEJMPS and
report, per round, the success probability, the Bell-diagonal coefficients and the expected raw
pairs per surviving output; do round 2 by hand and confirm it against the simulation.

**Solution.**

*Round 1.* The Werner input is `(A, B, C, D) = (0.8, 0.066667, 0.066667, 0.066667)`.

```
N  = 0.866667² + 0.133333² = 0.751111 + 0.017778 = 0.768889
A' = (0.640000 + 0.004444)/N = 0.644444/0.768889 = 0.838150
B' = 2(0.066667)(0.066667)/N = 0.008889/0.768889 = 0.011561
C' = (0.004444 + 0.004444)/N = 0.008889/0.768889 = 0.011561
D' = 2(0.800000)(0.066667)/N = 0.106667/0.768889 = 0.138728
```

The output is no longer Werner: `D` (the `|Φ⁻⟩` weight, a pure phase error) is now twelve times
`B` and `C`. That asymmetry is what BBPSSW twirls away and DEJMPS keeps.

*Round 2, by hand.* Feed `(0.838150, 0.011561, 0.011561, 0.138728)` back in:

```
N  = 0.849711² + 0.150289² = 0.722009 + 0.022587 = 0.744596
A' = (0.702495 + 0.000134)/0.744596 = 0.943639
```

Because the rotation swaps `|Ψ⁻⟩ ↔ |Φ⁻⟩`, the large `D` leaves the slot the bilateral CNOT fuses
with `A` and the tiny `B` takes its place, so round 2 squares a number near 1 — the fidelity jumps
over five points. A full two-copy density-matrix simulation (bilateral `R_x(±π/2)`, bilateral CNOT,
coincidence post-selection) reproduces the closed form to `6 × 10⁻¹⁶` over four rounds:

| round | `p_success` | `F` | `(B, C, D)` | raw pairs per output |
|---|---|---|---|---|
| 1 | 0.768889 | 0.838150 | (0.011561, 0.011561, 0.138728) | 2.60 |
| 2 | 0.744596 | 0.943639 | (0.004308, 0.026026, 0.026026) | 6.99 |
| 3 | 0.901313 | 0.987974 | (0.001503, 0.001503, 0.009020) | 15.50 |
| 4 | 0.979175 | 0.996854 | (0.000028, 0.000085, 0.003033) | 31.67 |

```python
import numpy as np

def dejmps(c):
    """One DEJMPS round on Bell-diagonal coefficients c = (A, B, C, D)
    for (|Phi+>, |Psi->, |Psi+>, |Phi->).  Returns (new coefficients, p_success)."""
    A, B, C, D = c
    N = (A + B) ** 2 + (C + D) ** 2
    return np.array([A * A + B * B, 2 * C * D, C * C + D * D, 2 * A * B]) / N, N

F = 0.80
c = np.array([F, (1 - F) / 3, (1 - F) / 3, (1 - F) / 3])   # Werner state
pairs = 1.0
for k in range(1, 5):
    c, p = dejmps(c)
    pairs = 2 * pairs / p
    print(f"round {k}: p_succ = {p:.6f}  F = {c[0]:.6f}  raw pairs per output = {pairs:.2f}")
```

**Reading the result.** The success probability *rises* towards 1 as the state improves, so late
rounds are nearly deterministic and the cost approaches the unavoidable `2^k`. And the returns are
sharply superlinear once the state is clean: the jump from 0.9436 to 0.9880 costs 8.5 extra raw
pairs, the first jump from 0.80 to 0.8382 only 1.6. Distillation is cheap where you least need it,
which argues for distilling *before* swapping degrades the fidelity — see Exercise 5.

---

## Summary

- The PLOB bound `C = -log₂(1-η)` is a capacity for *point-to-point* links with unlimited two-way
  classical assistance; a quantum midpoint escapes it because `η(L) = √η(2L)` — a factor `10⁵` at
  500 km. Twin-field QKD and memory-enhanced QKD have both demonstrated the escape
- **Distillation** is error correction under LOCC: two noisy pairs in, one better out when a
  bilateral parity check agrees. Every entangled two-qubit state is distillable; Werner states need
  `F > 1/2`, an exact fixed point of the DEJMPS map
- **BBPSSW** twirls to Werner form each round; **DEJMPS** prepends a bilateral `R_x(±π/2)` that
  swaps `|Ψ⁻⟩ ↔ |Φ⁻⟩` so the bilateral CNOT fuses the largest coefficient with the smallest.
  From `F = 0.80`: DEJMPS reaches `0.9969` in four rounds, BBPSSW `0.9300`, and the same circuit
  without the rotation *degrades* to `0.5345`
- Imperfect local gates give distillation a fixed point `F_max(ε) < 1`; that number, not the
  protocol, sets what a repeater can achieve
- **Three generations**: 1G = heralding + distillation (two-way at every level, memory `≳ L/c`);
  2G = heralding + QEC (two-way per segment, memory `≳ L₀/c`); 3G = QEC for loss too (one-way,
  gate-speed limited) but needing segment loss under **3 dB** — 15 km spacing and 66 stations
  across 1000 km at 0.2 dB/km
- A repeater **memory** must hold for the waiting time, couple efficiently to photons, support
  local gates, and multiplex; no platform yet leads on all four

---

## Exercises

**Exercise 1**: A link delivers the Bell-diagonal state `(A, B, C, D) = (0.70, 0.10, 0.15, 0.05)`.
(a) Compute the DEJMPS success probability and output coefficients. (b) Which coefficient grows,
and why is that not a failure? (c) What does BBPSSW give on the same input?

<details><summary>Solution</summary>

(a) `N = (0.70 + 0.10)² + (0.15 + 0.05)² = 0.64 + 0.04 = 0.680000`;
`A' = (0.49 + 0.01)/0.68 = 0.735294`, `B' = 2(0.15)(0.05)/0.68 = 0.022059`,
`C' = (0.0225 + 0.0025)/0.68 = 0.036765`, `D' = 2(0.70)(0.10)/0.68 = 0.205882`, summing to 1.

(b) `D` grows from 0.05 to 0.206: DEJMPS concentrates the residual error into one Bell component
while pushing `A` up. That is the point — next round the large `D` pairs against the small `B` and
`A'' = (A² + B²)/N` squares a near-unit number.

(c) BBPSSW twirls to Werner `F = 0.70` first, also giving `F' = 0.735294` at `p = 0.68`. The
numbers coincide only because this input already has `B = (1-F)/3 = 0.10`, so the twirl leaves both
`A² + B²` and `(A+B)² + (C+D)²` unchanged. The divergence appears from round 2, where BBPSSW has
thrown away the asymmetry the first round created.

</details>

**Exercise 2**: (a) Show by direct substitution that `F = 1/2` is a fixed point of DEJMPS on the
Werner line. (b) Evaluate the map at `F = 0.45` and `F = 0.55`. (c) Explain the fixed point in
terms of entanglement rather than arithmetic.

<details><summary>Solution</summary>

(a) At `F = 1/2`, `q = 1/6` and `(A, B, C, D) = (1/2, 1/6, 1/6, 1/6)`, so
`N = (2/3)² + (1/3)² = 5/9` and `A' = (1/4 + 1/36)/(5/9) = (10/36)(9/5) = 1/2`. Fixed.

(b) `F = 0.45`: `q = 0.183333`, `N = 0.633333² + 0.366667² = 0.535556`,
`A' = 0.236111/0.535556 = 0.440871` — worse. `F = 0.55`: `q = 0.15`, `N = 0.70² + 0.30² = 0.58`,
`A' = 0.325/0.58 = 0.560345` — better.

(c) A Werner state is separable for `W ≤ 1/3`, i.e. `F ≤ 1/2`, and LOCC cannot create
entanglement, so *no* protocol can raise a separable state above `F = 1/2` (a value a product
state already attains). `F = 1/2` is the boundary of the entangled set; any sensible map must fix
it, so (a) is a consistency check rather than a coincidence.

</details>

**Exercise 3**: Starting from Werner pairs at `F = 0.80`, how many DEJMPS rounds are needed to
exceed `F = 0.99`, and what is the expected raw-pair cost per output? Compare with the
deterministic `2^k` floor and explain the gap.

<details><summary>Solution</summary>

Round 3 reaches `0.987974` (short of 0.99) and round 4 reaches `0.996854`, so four rounds are
needed. The recursion `c_k = 2c_{k-1}/p_k` with `p = (0.768889, 0.744596, 0.901313, 0.979175)`
gives `c₄ = 31.67` raw pairs per output against the floor `2⁴ = 16`. The gap is `1/∏p_k = 1.98`,
almost all incurred in the first two rounds where `p ≈ 0.75`; by round 4, `p = 0.979` and the round
is nearly free. Starting from `F = 0.95` instead, two rounds clear 0.99 at a cost near 4 — the cost
is far more sensitive to the starting fidelity than to the target.

</details>

**Exercise 4**: (a) Derive the maximum third-generation station spacing from the antidegradability
argument. (b) Evaluate it at `α = 0.2` and `α = 0.5 dB/km`, with the station count for a 1000 km
link. (c) A 2G design uses 100 km segments. Why is it not subject to the same constraint?

<details><summary>Solution</summary>

(a) A one-way loss code needs positive one-way quantum capacity, hence `η > 1/2`, since the
pure-loss channel is antidegradable at `η ≤ 1/2`. With `η = 10^{-αL/10}` that is
`αL < 10 log₁₀ 2 = 3.01 dB`, i.e. `L < 3/α` km.

(b) `α = 0.2`: `L_max = 15.0 km`, so 1000 km needs `⌈1000/15⌉ = 67` segments and 66 stations.
`α = 0.5`: `L_max = 6.0 km`, 167 segments and 166 stations.

(c) 2G handles loss by *heralding*, not coding: a lost photon produces no herald, the attempt is
discarded, and nothing was encoded into the lost mode. Heralding costs rate but has no threshold,
because it never asks the channel to carry quantum information forward one-way. The 3 dB rule is
the price of removing the classical round trip.

</details>

**Exercise 5**: The 11/01 chain has eight segments at `F_link = 0.99`, giving `F_end = 0.923635`
after seven swaps. Compare two routes to `F_end > 0.999`: **(A)** swap first, then distill the
end-to-end pairs; **(B)** distill each link first, then swap. Price both in raw elementary pairs
(deterministic swapping, perfect local gates).

<details><summary>Solution</summary>

**(A) Swap, then distill.** From `F = 0.923635`, DEJMPS gives `0.945079` (`p = 0.903364`), then
`0.993800` (`p = 0.898748`), then `0.999629` (`p = 0.988005`). Three rounds, costing `c₃ = 9.97`
*end-to-end* pairs — and each costs 8 elementary links, so **79.8 raw links**.

**(B) Distill, then swap.** DEJMPS on `F = 0.99` gives `0.993266` (`p = 0.986756`) then `0.999909`
(`p = 0.986668`) at `c₂ = 4.11` raw pairs per link. Swapping eight such links:
`W = 0.999879`, `W⁸ = 0.999031`, `F_end = 0.999272`. Cost `8 × 4.11 =` **32.9 raw links**.

B is 2.4× cheaper and still clears the target. Two effects compound: distillation is cheapest when
the input is already good (Exercise 3), and an elementary pair costs `1/8` of an end-to-end pair.
This is the reasoning behind Briegel-Dür-Cirac-Zoller *nested* purification — distill at every
level, as low in the nesting tree as the fidelity budget permits, never only at the top.

</details>

---

## Further Reading

1. **Briegel, Dür, Cirac & Zoller** — "Quantum repeaters: The role of imperfect local operations
   in quantum communication," *Phys. Rev. Lett.* 81, 5932 (1998). The original nested-purification
   repeater and the local-error fixed point.
2. **Bennett, Brassard, Popescu, Schumacher, Smolin & Wootters** — "Purification of noisy
   entanglement and faithful teleportation via noisy channels," *Phys. Rev. Lett.* 76, 722 (1996).
   BBPSSW, twirling, and the LOCC framing.
3. **Deutsch, Ekert, Jozsa, Macchiavello, Popescu & Sanpera** — "Quantum privacy amplification and
   the security of quantum cryptography over noisy channels," *Phys. Rev. Lett.* 77, 2818 (1996).
   DEJMPS and the bilateral rotation.
4. **Muralidharan, Li, Kim, Lütkenhaus, Lukin & Jiang** — "Optimal architectures for long distance
   quantum communication," *Sci. Rep.* 6, 20463 (2016). The three-generation taxonomy.
5. **Pirandola, Laurenza, Ottaviani & Banchi** — "Fundamental limits of repeaterless quantum
   communications," *Nat. Commun.* 8, 15043 (2017). The PLOB bound for loss and thermal channels.
