# Distributed Quantum Computing

> **Prerequisites**: Entanglement distribution and swapping (11/01), repeaters and distillation
> (11/02), teleportation and resource accounting (08/02), multi-qubit gates (03/02),
> measurement-based quantum computing (03/05), trapped ions (07/02)
> **Connects to**: Surface code and thresholds (05/06), fault tolerance (05/07), QKD (04/08),
> photonic platforms (07/03)

---

## Overview

Every qubit technology hits a ceiling on how many qubits fit in one box: ion chains slow down as
they lengthen, superconducting chips run out of wiring and refrigerator volume, neutral-atom arrays
run out of laser power. **Distributed quantum computing** answers the ceiling the way classical
computing did — many modules, connected — except that the interconnect must carry quantum
information, and the only one physics offers is the entangled pair that 11/01 and 11/02 spent their
pages manufacturing.

The surprising part is how little is needed. Gottesman and Chuang (1999) showed a gate can be
*teleported*: entanglement plus classical communication plus local operations implement a
two-qubit gate between qubits that never meet. Eisert, Jacobs, Papadopoulos and Plenio (2000)
pinned the cost exactly — **one ebit and two classical bits per nonlocal CNOT, and not less**.
With that plus arbitrary local gates the distributed machine is universal; only the price list
changes. This chapter is that price list: moving *data* versus moving the *gate*, the distributed
CNOT derived line by line and checked on qiskit, an imperfect ebit converted into an exact Pauli
channel, what a GHZ state buys that ebits do not, the layered stack, and what has actually been
demonstrated. The worked example prices one distributed CNOT over the 800 km chain of 11/01.

---

## Two Ways to Make a Gate Nonlocal

**Teledata**: teleport Alice's qubit to Bob (1 ebit, 2 cbits), apply the CNOT locally inside Bob's
module, teleport it back (1 ebit, 2 cbits) — **2 ebits + 4 cbits** and two round trips. Its virtue
is composability: once the qubit has migrated, *every* gate involving it and Bob's register is
local.

**Telegate**: leave both data qubits where they are and teleport the *operation*. Alice entangles
her data qubit with her half of a shared ebit, measures that half and tells Bob the bit; Bob uses
his half to apply the CNOT locally, then measures it out in a basis that reveals nothing about
Alice's data and returns the result. Cost: **1 ebit + 2 cbits**, one bit each way, one round trip.

| | ebits | cbits | rounds | best when |
|---|---|---|---|---|
| Teledata (there and back) | 2 | 4 | 2 | never, for a single isolated gate |
| Teledata (migrate once) | 2 | 4 | 2 | many gates involve the same migrating qubit |
| Telegate | 1 | 2 | 1 | isolated cross-module gates |

A compiler for a distributed machine is a placement problem in these units: six cross-module CNOTs
all involving one Alice qubit cost 2 ebits by migration but 6 as telegates, while six on six
different qubits cost 6 either way and the telegates win on latency. Because ebits are millions of
times more expensive than local gates (see the worked example), this accounting dominates
distributed compilation the way T-count dominates fault-tolerant compilation (03/04).

---

## Deriving the Distributed CNOT

Alice holds `a`, Bob holds `b`, and they share `|Φ⁺⟩_{e_A e_B}`. Take the data in a product state
`|ψ⟩_a|φ⟩_b` with `|ψ⟩ = α|0⟩ + β|1⟩`; linearity extends everything below to data already entangled
with the rest of the machine. **Steps 1-2 — Alice's CNOT (the cat-entangler), then measure `e_A` in
`Z` and send `m₁`.** Apply `CNOT(a → e_A)`; each outcome then has probability `1/2`:

```
(α|0⟩_a + β|1⟩_a)(|00⟩+|11⟩)_{e_A e_B}/√2  →  [α|0⟩_a(|00⟩+|11⟩) + β|1⟩_a(|10⟩+|01⟩)]/√2
m₁ = 0 :  α|0⟩_a|0⟩_{e_B} + β|1⟩_a|1⟩_{e_B}        m₁ = 1 :  α|0⟩_a|1⟩_{e_B} + β|1⟩_a|0⟩_{e_B}
```

**Step 3 — Bob applies `X^{m₁}` to `e_B`.** Both branches become
`α|0⟩_a|0⟩_{e_B} + β|1⟩_a|1⟩_{e_B}`: Bob's qubit now carries a *coherent copy of `a`'s
computational-basis value*. No-cloning is untouched — what was copied is one basis observable, not
the state, which is exactly what a CNOT does. **Step 4 — Bob's local CNOT.** Apply
`CNOT(e_B → b)` with `|φ⟩ = γ|0⟩ + δ|1⟩`, giving
`α|0⟩_a|0⟩_{e_B}|φ⟩_b + β|1⟩_a|1⟩_{e_B}X|φ⟩_b`. The data qubits now carry exactly
`CNOT(a → b)|ψ⟩|φ⟩`, but `e_B` is still entangled with them.

**Step 5 — the cat-disentangler.** Measuring `e_B` in `Z` would reveal `a`'s value and collapse the
superposition, so measure in `X`: apply `H`, giving

```
|0⟩_{e_B}(α|0⟩_a|φ⟩ + β|1⟩_a X|φ⟩)/√2  +  |1⟩_{e_B}(α|0⟩_a|φ⟩ - β|1⟩_a X|φ⟩)/√2
```

Outcome `m₂ = 0` leaves exactly `CNOT|ψ⟩|φ⟩`; `m₂ = 1` leaves `(Z_a ⊗ I)·CNOT|ψ⟩|φ⟩`, so
**Step 6** is Alice applying `Z^{m₂}` to `a`. One ebit consumed, one cbit each way, both data
qubits still at home.

### Verification and Optimality

Deferring both measurements into controlled corrections (`CNOT(e_A → e_B)` for step 3,
`CZ(e_B → a)` for step 6) gives a unitary that can be checked outright. On qiskit 2.5.2:

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity

telegate = QuantumCircuit(4)   # 0 = a (Alice's data), 1 = eA, 2 = eB, 3 = b (Bob's data)
telegate.cx(0, 1)      # Alice entangles her data qubit with her half of the ebit
telegate.cx(1, 2)      # deferred: measure eA -> m1, send to Bob, X on eB if m1 = 1
telegate.cx(2, 3)      # Bob applies the CNOT locally, eB -> b
telegate.h(2)
telegate.cz(2, 0)      # deferred: measure eB -> m2, send to Alice, Z on a if m2 = 1

prep = QuantumCircuit(4)
prep.ry(0.7, 0); prep.rx(1.3, 3); prep.cx(0, 3); prep.t(0)   # entangled data
prep.h(1); prep.cx(1, 2)                                     # the shared ebit
ideal = prep.copy(); ideal.cx(0, 3)                          # the CNOT we want

out = partial_trace(Statevector(prep.compose(telegate)), [1, 2])
ref = partial_trace(Statevector(ideal), [1, 2])
print("F(telegate, local CNOT) =", round(state_fidelity(out, ref), 12))
# F(telegate, local CNOT) = 1.0
```

Post-selecting the explicit measure-and-correct version instead, over 50 random two-qubit inputs
and all four `(m₁, m₂)` branches, every branch occurs with probability exactly `1/4` and reproduces
the ideal CNOT to `4 × 10⁻¹⁶`. Data-independent branch probabilities are the whole correctness
argument: the outcomes carry no information about `|ψ⟩`.

Eisert *et al.* (2000) proved the counts are tight: a nonlocal CNOT can *create* one ebit (feed it
`|+⟩_a|0⟩_b`), so at least one ebit must be consumed, and it signals in either direction (Alice's
`Z` input changes Bob's output, and conversely in the conjugate basis), so at least one classical
bit must travel each way. The protocol above saturates both.

### Noise: What an Imperfect ebit Costs

Substituting each Bell state for the resource and solving for the induced two-qubit operation
gives an exact dictionary — computed numerically, each case a Pauli times the ideal CNOT with no
residual phase:

| resource state | effective operation |
|---|---|
| `\|Φ⁺⟩` | `CNOT` |
| `\|Ψ⁺⟩` | `(X_b) · CNOT` |
| `\|Φ⁻⟩` | `(Z_a) · CNOT` |
| `\|Ψ⁻⟩` | `(Z_a X_b) · CNOT` |

A Bell-diagonal resource `(A, B, C, D)` therefore turns the telegate into the ideal CNOT followed
by a **Pauli channel** with exactly those weights, so the process (entanglement) fidelity is `A`
itself — `F_process = F_ebit` — and, with `d = 4`, the average gate fidelity is
`F_avg = (4F_ebit + 1)/5`. The first is exact — the telegate inherits the resource fidelity with
neither amplification nor dilution; the second follows from `F_avg = (d F_e + 1)/(d+1)` and was
checked against `qiskit.quantum_info.average_gate_fidelity` on the explicit Kraus channel, agreeing
to twelve digits at `F = 0.90, 0.95, 0.99`. Because the errors are Pauli, they are exactly the
model stabilizer codes (05/04, 05/06) are built to correct: a distributed logical CNOT tolerates a
noisy interconnect whenever the induced Pauli rate is under threshold.

---

## Multipartite Resources

Bipartite ebits are not the only currency. A shared **GHZ state**
`|GHZ_n⟩ = (|0⟩^{⊗n} + |1⟩^{⊗n})/√2` is a genuinely `n`-party resource, and some tasks consume it
more efficiently than any collection of pairs.

**Fan-out in one round.** Extend the cat-entangler: a `GHZ_{k+1}` is shared between Alice and `k`
Bobs, and Alice's `CNOT(a → e_A)` and `Z` measurement broadcast one bit that lets *every* Bob
correct his share at once. Each Bob applies `CNOT(e_{B_i} → b_i)`, measures in `X` and returns a
bit; Alice applies `Z^{m₂ ⊕ m₃ ⊕ …}`. The net operation is `CNOT(a, b₁)···CNOT(a, b_k)` — one
control, `k` targets — verified on qiskit for `k = 2` over 30 random inputs and all eight branches,
agreeing to `9 × 10⁻¹⁶`. The saving is *not* entanglement: distributing a `GHZ_{k+1}` by LOCC costs
`k` ebits, exactly as `k` telegates do, with the same `2k` classical bits. The saving is
**rounds** — one simultaneous round instead of `k` sequential ones, which matters when a round
costs milliseconds of light travel and the memories decohere while waiting.

Four tasks where a GHZ state is strictly better than any set of pairs:

- **Conference key agreement**: `n` parties extract one shared secret bit per `GHZ_n`, where
  pairwise QKD needs `n - 1` links plus a key-combining protocol and a trusted relay.
- **Anonymous transmission and distributed voting**: the security rests on the GHZ state's
  permutation symmetry and has no bipartite analogue.
- **Distributed sensing**: `n` entangled probes give Heisenberg-limited `1/n` phase sensitivity
  rather than the `1/√n` standard quantum limit.
- **Non-local stabilizer measurement**: a cross-module parity check *is* a GHZ-assisted fan-out
  plus one readout — the primitive a distributed surface code needs.

---

## The Quantum Internet Stack

Dahlberg *et al.* (2019) proposed the layering the field now works with, mirroring the classical
stack so applications can be written against a service rather than a physics experiment.

| layer | service it provides | new idea it introduces |
|---|---|---|
| **Physical** | one heralded entanglement *attempt* | no state kept between attempts |
| **Link** | neighbour ebits at a requested fidelity | a *cutoff time*: expire a pair before it rots |
| **Network** | ebits between arbitrary nodes, by swapping | entanglement routing and path selection |
| **Transport** | qubit delivery by teleportation | ordering, retransmission |
| **Application** | QKD, telegates, conference key, clock sync | — |

The genuinely new layer is the **link layer**. Classically a link either delivers a frame or does
not; here the deliverable is a *state whose fidelity decays while it waits*, so the service
definition needs both a fidelity target and a cutoff time after which the pair is discarded.
Distillation (11/02) is the link- and network-layer mechanism for meeting the fidelity target, and
the tension between "wait for a better pair" and "use it before it rots" is the scheduling problem
at the heart of quantum network protocol design.

Wehner, Elkouss and Hanson (2018) give the complementary road map of six stages: trusted-repeater,
prepare-and-measure, entanglement distribution, quantum memory, few-qubit fault-tolerant, and
quantum computing networks. Commercial deployments today sit at stage 1 or 2.

---

## Where This Actually Stands

The building blocks all exist, individually, at rates that are far too low.

- **Multi-node networks**: Delft ran a three-node NV-centre network, swapping entanglement to
  non-neighbouring nodes (Pompili *et al.*, 2021) and then teleporting a qubit between them
  (Hermans *et al.*, 2022); distillation between remote solid-state qubits came earlier (Kalb *et
  al.*, 2017).
- **Real fibre**: SiV memory nodes entangled over a 35 km deployed telecom loop near Boston (Knaut
  *et al.*, 2024); heralded entanglement across the 25 km Delft-to-The-Hague link (Stolk *et al.*,
  2024); memory-enhanced QKD beating the repeaterless bound (Bhaskar *et al.*, 2020).
- **Distributed computation**: two photonically linked trapped-ion modules executed a teleported
  two-qubit gate and ran Grover's algorithm across the link (Main *et al.*, 2025) — the telegate
  primitive of this chapter composing into an algorithm.

What is missing is not a principle but orders of magnitude: interconnect rates are `10⁰`-`10²` Hz
where local gates run at `10⁵`-`10⁹` Hz, so a distributed circuit is scheduled entirely around its
cross-module gates. The near-term architectures that make sense have low interconnect demand —
modular fault-tolerant machines whose network carries lattice-surgery boundaries between code
patches rather than individual logical gates.

---

## Key Formulas

- **Teledata (nonlocal CNOT)**: 2 ebits + 4 cbits, 2 rounds; **telegate**: 1 ebit + 2 cbits, 1 round
- **Telegate circuit**: `CNOT(a→e_A)`, measure `e_A` → `m₁`, `X^{m₁}` on `e_B`, `CNOT(e_B→b)`,
  `H` and measure `e_B` → `m₂`, `Z^{m₂}` on `a`; all four `(m₁, m₂)` have probability `1/4`
- **Optimality (Eisert *et al.*)**: 1 ebit and 1 cbit in each direction are each necessary
- **Resource-error dictionary**: `|Φ⁺⟩ → I`, `|Ψ⁺⟩ → X_b`, `|Φ⁻⟩ → Z_a`, `|Ψ⁻⟩ → Z_a X_b`
- **Telegate fidelity**: process fidelity `= F_ebit`, average gate fidelity `= (4F_ebit + 1)/5`,
  inverted as `F_ebit = (5 F_avg - 1)/4`
- **GHZ fan-out**: `GHZ_{k+1}` + `2k` cbits gives one control and `k` targets in **one** round
- **Stack**: physical → link (fidelity + cutoff) → network (swapping, routing) → transport →
  application

---

## Worked Example: One Distributed CNOT Across 800 km

**Problem.** Use the 800 km, eight-segment chain of 11/01 (links at `F = 0.99`,
`p = 1.0125 × 10⁻³` per `0.500 ms` attempt) for one nonlocal CNOT between the end modules. Give the
gate fidelity and rate (i) with raw swapped pairs and (ii) with the link-level distillation of
11/02, and compare with a local two-qubit gate.

**Solution.** *(a) Raw chain.* Seven swaps of `F = 0.99` Werner links give
`F_ebit = 0.923635` (11/01) at `0.745` ebits/s, and the telegate inherits that fidelity exactly:
`F_avg = (4 × 0.923635 + 1)/5 = 0.938908`, an error rate of `6.11 × 10⁻²`. A 6% two-qubit gate
error is useless — far above any fault-tolerance threshold, and worse than the `10⁻²` to `10⁻³`
local error rates the modules themselves achieve.

*(b) Distilled chain.* Strategy B of 11/02 Exercise 5 spends `4.108` raw pairs per link on two
DEJMPS rounds, lifting each link to `F = 0.999909` and the swapped pair to `F_ebit = 0.999272`, so
`F_avg = 0.999418` and the error rate is `5.82 × 10⁻⁴` — the interconnect is now *better* than a
typical local two-qubit gate.

*(c) The rate paid for it.* Distillation divides the effective per-link success probability by its
pair cost, `p_eff = 1.0125 × 10⁻³/4.108 = 2.465 × 10⁻⁴`, and with eight links in parallel
`E[max] ≈ H₈/p_eff = 11027` attempts, so `T_gate = 11027 × 0.500 ms = 5.51 s` and
`R_gate = 0.181` nonlocal CNOTs per second. Even with an ebit in hand the telegate still costs
`2 × 4.0 ms = 8.0 ms` of classical latency for the two bits to cross 800 km. Against a local
two-qubit gate of order `1 µs`, the ratio is `5.51 s / 1 µs ≈ 5.5 × 10⁶`.

**Reading the result.** Fidelity is solvable and rate is not. Two rounds of distillation moved the
interconnect from unusable (`6 × 10⁻²`) to better than local (`6 × 10⁻⁴`) for `4.1×` in rate — a
bargain. But `0.18 Hz` is six to seven orders of magnitude below local gate speed, and no amount of
distillation touches that; only more parallel links, more memory modes and faster heralding do. An
algorithm needing one cross-module gate per second is feasible in principle today; one needing a
cross-module gate per local gate is not.

---

## Summary

- A nonlocal CNOT costs **1 ebit + 2 cbits** as a **telegate** and **2 ebits + 4 cbits** as
  there-and-back **teledata**; migrating once pays 2 ebits but makes every later gate involving
  that qubit local, so distributed compilation is a placement problem in these units
- The **distributed CNOT** copies the control's `Z` value onto Bob's ebit half (the cat-entangler),
  does the CNOT locally, then measures that half in `X` (the cat-disentangler) so nothing about the
  data leaks. All four branches have probability `1/4` and the circuit reproduces the ideal CNOT to
  `4 × 10⁻¹⁶` on qiskit 2.5.2. Eisert *et al.* proved the cost is tight
- An imperfect ebit maps **exactly** onto a Pauli channel — `|Ψ⁺⟩ → X_b`, `|Φ⁻⟩ → Z_a`,
  `|Ψ⁻⟩ → Z_a X_b` — giving process fidelity `= F_ebit` and average gate fidelity
  `(4F_ebit + 1)/5`; Pauli errors are exactly what stabilizer codes correct
- A shared **GHZ** state buys *rounds*, not ebits: one simultaneous fan-out instead of `k`
  sequential telegates, and it is strictly better for conference key, anonymous transmission,
  Heisenberg-limited sensing and cross-module parity checks
- The stack runs physical → link → network → transport → application; the link layer is new because
  its deliverable decays, so its service definition needs a fidelity target *and* a cutoff time
- Over 800 km, distillation lifts the telegate from `6 × 10⁻²` to `6 × 10⁻⁴` error for `4.1×` the
  pair cost, but the rate is `0.18 Hz` — some `5 × 10⁶` times slower than a local gate. Fidelity is
  solved; rate is the open problem

---

## Exercises

**Exercise 1**: A distributed algorithm needs six CNOTs between Alice's module and Bob's. (a) Price
it with telegates. (b) Price it with naive there-and-back teledata. (c) If all six use the *same*
Alice qubit as control, price migrate-once teledata and say when migration wins.

<details><summary>Solution</summary>

(a) `6` ebits, `12` cbits, six rounds (parallelizable if six ebits are buffered). (b) `12` ebits
and `24` cbits — twice the entanglement and twice the latency, strictly worse.

(c) Teleport the control to Bob (1 ebit, 2 cbits), run all six CNOTs locally, teleport it back:
**2 ebits + 4 cbits**, a 3× saving. Migration wins whenever a qubit takes part in `k ≥ 3`
cross-module gates *with no intervening cross-module gate on Alice's side that needs it back*. That
proviso is the difficulty: the compiler must schedule migrations against the rest of the circuit,
which is why distributed-circuit partitioning is an optimization problem rather than a rule.

</details>

**Exercise 2**: Work the telegate branch `(m₁, m₂) = (1, 1)` explicitly from Step 2, confirming the
stated corrections, then explain why the two transmitted bits reveal nothing about the data.

<details><summary>Solution</summary>

After `m₁ = 1` the state is `α|0⟩_a|1⟩_{e_B} + β|1⟩_a|0⟩_{e_B}`. Bob's `X` on `e_B` gives
`α|0⟩_a|0⟩_{e_B} + β|1⟩_a|1⟩_{e_B}`, identical to the `m₁ = 0` branch — which is why one bit
suffices. His `CNOT(e_B → b)` yields `α|0⟩_a|0⟩_{e_B}|φ⟩ + β|1⟩_a|1⟩_{e_B}X|φ⟩`; applying `H` to
`e_B` and selecting `m₂ = 1` picks the `|1⟩_{e_B}` component, leaving
`α|0⟩_a|φ⟩ - β|1⟩_a X|φ⟩ = (Z_a ⊗ I)·CNOT|ψ⟩|φ⟩`, which Alice's `Z` restores. ∎

Every branch has probability exactly `1/4` regardless of `α, β, γ, δ`: `m₁` is the `Z` value of a
maximally mixed ebit half, and `m₂` an `X` measurement on a qubit whose `Z` value is perfectly
correlated with `a`. That data-independence is the non-signalling argument that makes ordinary
teleportation safe.

</details>

**Exercise 3**: (a) Invert `F_avg = (4F_ebit + 1)/5` for average gate fidelities `0.99`, `0.999`
and `0.9999`. (b) The raw 11/01 chain gives `F_ebit = 0.923635` — what `F_avg` is that, against the
surface-code threshold? (c) Why is comparing the telegate error to a code threshold legitimate?

<details><summary>Solution</summary>

(a) `F_ebit = (5F_avg - 1)/4`, giving `0.987500`, `0.998750`, `0.999875` — the interconnect must be
about `1.25×` better in infidelity than the gate it implements, since the telegate neither
amplifies nor suppresses noise.

(b) `F_avg = 0.938908`, an error rate of `6.11 × 10⁻²`. The surface-code threshold is near `1%`
under circuit-level depolarizing noise (05/06), so the raw chain is roughly six times too noisy —
and thresholds are not targets; useful operation needs an order of magnitude below them.

(c) Because the induced channel is *exactly* Pauli (`X_b`, `Z_a`, `Z_a X_b` with the Bell weights),
not a general CPTP map. Threshold statements are proved for Pauli noise and stabilizer decoders
handle Pauli errors directly; an interconnect producing coherent errors of the same magnitude would
be substantially worse.

</details>

**Exercise 4**: A control in Alice's module must apply CNOTs to `k` targets in `k` different
modules. (a) Count ebits, cbits and rounds for sequential telegates and for the `GHZ_{k+1}`
fan-out. (b) Where does the fan-out actually win? (c) Name a task for which a GHZ state is *not*
replaceable by ebits at any cost.

<details><summary>Solution</summary>

(a) Sequential telegates: `k` ebits, `2k` cbits, `k` rounds. GHZ fan-out: a `GHZ_{k+1}` costs `k`
ebits to distribute by LOCC, the traffic is the same `2k` bits (one broadcast out, `k` back), and
it completes in **1** round.

(b) In latency and therefore decoherence: a round costs `2L/c` of light travel — `8 ms` over
800 km — so eight sequential telegates spend `64 ms` where the fan-out spends `8 ms`. There is no
entanglement saving, and claims of one usually double-count the cost of building the GHZ state.

(c) Conference key agreement. With ebits, one party must generate the key and relay it pairwise,
which requires trusting that party and running `n - 1` separate QKD sessions; the GHZ protocol
gives all `n` parties a symmetric, simultaneously certified key. Anonymous transmission and
Heisenberg-limited distributed sensing are similar — the permutation symmetry *is* the protocol.

</details>

**Exercise 5**: In the Dahlberg *et al.* stack, (a) which layer owns distillation, and why is the
answer "it depends"? (b) Why does the link layer need a cutoff time when a classical one does not?
(c) At which Wehner-Elkouss-Hanson stage does a trusted-node QKD network sit, and what is the first
stage at which this chapter's telegate becomes possible?

<details><summary>Solution</summary>

(a) Link-level distillation (two neighbour pairs into a better neighbour pair) belongs to the link
layer, being part of delivering a neighbour ebit at a requested fidelity; end-to-end distillation
of swapped pairs belongs to the network layer. Exercise 5 of 11/02 shows they are not
interchangeable — the link-layer version is about `2.4×` cheaper for the same end fidelity.

(b) Because the deliverable decays. A classical frame in a buffer is the same frame an hour later;
an ebit loses fidelity continuously, and past some point using it is worse than starting again. The
cutoff makes that trade explicit and lets the layer above reason about what it will receive.

(c) Trusted-node QKD sits at stage 1 — the nodes hold the key in the clear, which is exactly what
later stages remove. A telegate needs both ends to hold live, storable entanglement and apply gates
to it, so the first sufficient stage is 4 (quantum memory networks); fault-tolerant distributed
computation needs stages 5 and 6.

</details>

---

## Further Reading

1. **Eisert, Jacobs, Papadopoulos & Plenio** — "Optimal local implementation of nonlocal quantum
   gates," *Phys. Rev. A* 62, 052317 (2000). The 1-ebit/2-cbit CNOT protocol and the matching
   lower bounds.
2. **Gottesman & Chuang** — "Demonstrating the viability of universal quantum computation using
   teleportation and single-qubit operations," *Nature* 402, 390 (1999). Gate teleportation.
3. **Cirac, Ekert, Huelga & Macchiavello** — "Distributed quantum computation over noisy channels,"
   *Phys. Rev. A* 59, 4249 (1999). How purification and distributed gates combine under noise.
4. **Wehner, Elkouss & Hanson** — "Quantum internet: A vision for the road ahead," *Science* 362,
   eaam9288 (2018). The six-stage road map and the functionality each stage unlocks.
5. **Dahlberg et al.** — "A link layer protocol for quantum networks," *Proc. ACM SIGCOMM 2019*,
   pp. 159-173. The layered stack, the link-layer service definition and the cutoff time.
