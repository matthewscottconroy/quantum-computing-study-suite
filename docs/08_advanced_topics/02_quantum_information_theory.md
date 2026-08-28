# Quantum Information Theory

> **Prerequisites**: Density matrices and mixed states (Chapter 2), quantum channels, entropy
> basics (Chapter 2), linear algebra (Chapter 1)
> **Connects to**: Quantum error correction (Chapter 5), entanglement theory, quantum networks

---

## Overview

Quantum information theory extends Shannon's classical information theory to quantum systems.
The central questions: how much information can a quantum channel transmit? How much entanglement
does a quantum state contain? What are the fundamental limits on quantum communication?

These questions are not merely theoretical. They define what quantum computers and quantum networks
can fundamentally do: the quantum capacity of a channel determines whether fault-tolerant
computation is possible through it; the entanglement structure of a quantum state determines
the power of measurement-based quantum computing; the Holevo bound limits how much classical
information can be extracted from qubits.

This chapter develops the Von Neumann entropy and its properties, quantum analogues of mutual
information and conditional entropy, the Holevo and quantum capacity bounds, and key
quantum information protocols: teleportation, superdense coding, and their resource accounting.
We also prove the no-cloning theorem rigorously and discuss monogamy of entanglement.

---

## Von Neumann Entropy

### Definition

For a quantum state described by density matrix `ρ`, the **Von Neumann entropy** is:

```
S(ρ) = -Tr[ρ log₂ ρ] = -Σᵢ λᵢ log₂ λᵢ
```

where `{λᵢ}` are the eigenvalues of `ρ` and `0 log 0 := 0`. The units are qubits (using
log base 2).

**Properties**:
1. `S(ρ) ≥ 0`, with equality iff `ρ` is a pure state.
2. `S(ρ) ≤ log₂ d` for a `d`-dimensional system, with equality iff `ρ = I/d` (maximally mixed).
3. **Unitary invariance**: `S(UρU†) = S(ρ)` for any unitary `U`.
4. **Concavity**: `S(Σₖ pₖ ρₖ) ≥ Σₖ pₖ S(ρₖ)`.
5. **Subadditivity**: `S(ρ_{AB}) ≤ S(ρ_A) + S(ρ_B)` with equality iff `ρ_{AB} = ρ_A ⊗ ρ_B`.
6. **Araki-Lieb inequality**: `|S(ρ_A) - S(ρ_B)| ≤ S(ρ_{AB})`.

### Entropy of Bipartite States

For a bipartite pure state `|ψ⟩_{AB}`:
```
S(ρ_A) = S(ρ_B)   (Schmidt theorem)
```

The entropy of the reduced state measures the entanglement. Pure product states have `S = 0`;
maximally entangled Bell states have `S = 1` qubit.

For a bipartite mixed state, subadditivity gives:
```
S(AB) ≤ S(A) + S(B)
```
Equality iff `A` and `B` are uncorrelated.

### Strong Subadditivity

The deepest inequality in quantum information:

**Theorem (Strong Subadditivity, Lieb-Ruskai 1973)**: For any tripartite state `ρ_{ABC}`:

```
S(ρ_{ABC}) + S(ρ_B) ≤ S(ρ_{AB}) + S(ρ_{BC})
```

Equivalently: `I(A:C|B) ≥ 0`, where `I(A:C|B) = S(AB) + S(BC) - S(B) - S(ABC)` is the
**quantum conditional mutual information**.

Strong subadditivity has numerous applications: it underlies the proof of the concavity of
channel capacity, gives area laws for quantum entanglement in 1D systems, and is used in
quantum cryptography security proofs.

---

## Quantum Mutual Information

### Definition

The **quantum mutual information** of a bipartite state `ρ_{AB}` is:

```
I(A:B) = S(A) + S(B) - S(AB)
```

Properties:
- `I(A:B) ≥ 0`, with equality iff `ρ_{AB} = ρ_A ⊗ ρ_B` (uncorrelated).
- `I(A:B) = I(B:A)` (symmetric).
- `I(A:B) ≤ 2 min(S(A), S(B))`.

For classical states (diagonal density matrices), `I(A:B)` reduces to Shannon mutual information.

### Quantum Conditional Entropy

The **quantum conditional entropy**:

```
S(A|B) = S(AB) - S(B)
```

Unlike the classical conditional entropy, `S(A|B)` can be **negative** for quantum states.

**Example**: For the maximally entangled state `|Φ⁺⟩_{AB}`:
- `S(AB) = 0` (pure state)
- `S(B) = 1` (maximally mixed subsystem)
- `S(A|B) = S(AB) - S(B) = 0 - 1 = -1`

Negative conditional entropy is a quintessentially quantum phenomenon with no classical analogue.
It indicates that the quantum correlations in the state are stronger than any classical correlations.

---

## The Holevo Bound

### Setup

Alice encodes classical message `i` (with probability `pᵢ`) into quantum state `ρᵢ`. Bob
receives the quantum state and performs any POVM measurement to extract the message.

**Holevo quantity**: `χ = S(Σᵢ pᵢ ρᵢ) - Σᵢ pᵢ S(ρᵢ)`

**Holevo theorem** (1973): The accessible mutual information `I_acc ≤ χ`. That is, no
measurement can extract more than `χ` bits of information about Alice's message.

For orthogonal pure states `ρᵢ = |ψᵢ⟩⟨ψᵢ|` (all `S(ρᵢ) = 0`): `χ = S(Σᵢ pᵢ |ψᵢ⟩⟨ψᵢ|) ≤ log₂ d`.
This gives the capacity of dense coding: at most `log₂ d` bits per qudit.

**Holevo-Schumacher-Westmoreland (HSW) theorem**: The classical capacity of a quantum channel
`N` is the regularized Holevo capacity:

```
C(N) = lim_{n→∞} (1/n) χ(N^{⊗n}),   where   χ(N) = max_{{pᵢ,ρᵢ}} [S(N(Σᵢpᵢρᵢ)) - Σᵢ pᵢ S(N(ρᵢ))]
```

The single-letter quantity `χ(N)` is always an achievable rate (`C ≥ χ`). For many channels
`χ` is additive and `C = χ(N)` with no regularization needed — but not in general: Hastings
(2009) showed channels exist for which entangled inputs across channel uses strictly exceed
the product-input (single-letter) rate, so the regularization cannot be dropped.

---

## Quantum Channel Capacity

### Classical Information Over Quantum Channel

A quantum channel `N: ρ → N(ρ)` can transmit classical and quantum information.

**Classical capacity**: `C(N) = lim (1/n) χ(N^{⊗n})`; achievable by encoding classical messages
into quantum states.

**Quantum capacity**: `Q(N) = lim (1/n) Q_1(N^{⊗n})`; the number of qubits per channel use
that can be reliably transmitted.

**Hashing bound** (lower bound on quantum capacity):

```
Q(N) ≥ I_c(N) = max_ρ [S(N(ρ)) - S_e(N, ρ)]
```

where `S_e` is the entropy exchange (related to the channel's complementary channel). For the
depolarizing channel with error rate `p`:

```
I_c(N_dep) = 1 - H₂(p) - p log₂ 3   (qubit depolarizing channel, total error probability p)
```

This **hashing bound** is positive for `p < p_hash ≈ 0.1893` (where `1 - H₂(p) - p log₂3 = 0`).
Separately, the quantum capacity is *exactly zero* for `p ≥ 1/4` (there the channel becomes
antidegradable — Eve's output is at least as good as Bob's, so `Q > 0` would violate no-cloning).
In the window `0.1893 < p < 0.25` the capacity is not fully characterized. These thresholds are
related to (but distinct from) QEC code thresholds.

### No-Go Results

- **No-cloning theorem** (revisited): The quantum capacity through the cloning map is 0, since
  no-cloning implies you cannot reliably copy and retransmit quantum information.
- **Quantum erasure channel**: Erases a qubit with probability `p`. `Q = max(1 - 2p, 0)`. The
  quantum capacity is 0 for `p ≥ 1/2` (more erasures than transmissions).
- **Depolarizing channel**: `Q = 0` for `p ≥ 25%` (four Pauli errors equally likely; better to
  transmit new state than correct).

---

## Quantum Teleportation

### Protocol

Quantum teleportation (Bennett et al., 1993) transfers an unknown quantum state `|ψ⟩` from
Alice to Bob using:
- 1 ebit (pre-shared Bell pair).
- 2 classical bits.
- No quantum channel.

**Protocol** (Alice has qubit `|ψ⟩ = α|0⟩ + β|1⟩`, Alice and Bob share `|Φ⁺⟩_{AB}`):

1. **Alice's Bell measurement**: Alice measures her qubit `|ψ⟩` and her half of `|Φ⁺⟩` in the
   Bell basis. Outcomes: one of `{|Φ⁺⟩, |Φ⁻⟩, |Ψ⁺⟩, |Ψ⁻⟩}`.
2. **Classical communication**: Alice sends her 2-bit outcome to Bob.
3. **Bob's correction**: Bob applies one of `{I, X, Z, XZ}` to his qubit depending on Alice's
   message.
4. **Bob's qubit is now `|ψ⟩`**.

**Resource accounting**: Teleportation uses 1 ebit + 2 cbits → transmits 1 qubit. This is the
**quantum teleportation equality**: `1 ebit + 2 cbits ↔ 1 qubit` (in terms of communication
resources).

**State verification**: After Bob's correction, his qubit is in the exact state `|ψ⟩`, without
Alice having measured `|ψ⟩` or knowing `α, β`. No information about `|ψ⟩` was transmitted
classically — only the Bell measurement outcome, which is independent of `α, β`.

---

## Superdense Coding

### Protocol

Superdense coding (Bennett-Wiesner, 1992) is the "inverse" of teleportation: transmit 2 cbits
using 1 qubit + 1 ebit.

**Protocol** (Alice and Bob share `|Φ⁺⟩_{AB}`):

Alice wants to send 2 classical bits `b₁b₂ ∈ {00, 01, 10, 11}`. She applies one of four
operations to her half of the Bell pair:

```
00 → I  (no operation): sends |Φ⁺⟩
01 → X:              sends |Ψ⁺⟩
10 → Z:              sends |Φ⁻⟩
11 → iY = XZ:        sends |Ψ⁻⟩
```

She then sends her physical qubit to Bob. Bob holds both qubits and performs a Bell measurement,
perfectly distinguishing the four Bell states and recovering `b₁b₂`.

**Resource accounting**: 1 ebit + 1 qubit (transmitted) → 2 cbits.

Combined with teleportation: `1 ebit + 2 cbits ↔ 1 qubit` (teleportation) and
`1 ebit + 1 qubit ↔ 2 cbits` (superdense coding). These are dual protocols — they exchange
the roles of classical and quantum communication.

---

## No-Cloning Theorem (Complete Proof)

**Theorem**: There is no unitary `U` such that `U|ψ⟩|0⟩ = |ψ⟩|ψ⟩` for all `|ψ⟩`.

**Proof**: Suppose such `U` exists.

1. `U|0⟩|0⟩ = |0⟩|0⟩` and `U|1⟩|0⟩ = |1⟩|1⟩`.

2. By linearity, for `|+⟩ = (|0⟩+|1⟩)/√2`:
   ```
   U|+⟩|0⟩ = (U|0⟩|0⟩ + U|1⟩|0⟩)/√2 = (|0⟩|0⟩ + |1⟩|1⟩)/√2 = |Φ⁺⟩
   ```

3. But cloning `|+⟩` should give:
   ```
   |+⟩|+⟩ = (|0⟩+|1⟩)(|0⟩+|1⟩)/2 = (|00⟩+|01⟩+|10⟩+|11⟩)/2
   ```

4. `|Φ⁺⟩ ≠ |+⟩|+⟩`. Contradiction. ∎

**No-broadcasting theorem** (Barnum et al., 1996): For mixed states, the no-cloning theorem
generalizes: there is no operation that takes `ρ → ρ⊗ρ` for all `ρ`. More precisely, a set of
density matrices `{ρᵢ}` can be broadcast — i.e., some single device maps each `ρᵢ` to a
bipartite state whose both marginals equal `ρᵢ` — if and only if the `ρᵢ` pairwise commute.

---

## Monogamy of Entanglement

### Principle

A key property distinguishing quantum from classical correlations: **monogamy of entanglement**.
If qubit `A` is maximally entangled with qubit `B`, it cannot be entangled with any other qubit `C`.

**Formal statement (Coffman-Kundu-Wootters, 2000)**: For any three-qubit pure state:

```
C²_{A|BC} ≥ C²_{AB} + C²_{AC}
```

where `C_{AB}` is the **concurrence** (a measure of bipartite entanglement). The inequality
shows that Alice's entanglement is "monogamously shared" — total entanglement with `B` and `C`
is bounded by entanglement with `BC` together.

**Squashed entanglement** (Christandl-Winter, 2004): The most operationally defined entanglement
measure satisfies monogamy exactly:

```
E_sq(A:BC) ≥ E_sq(A:B) + E_sq(A:C)
```

### Implications

1. **QKD security**: If Alice's qubit is highly entangled with Bob's, it is only weakly
   entangled with Eve's. Monogamy quantifies how much information Eve can extract.
2. **No quantum broadcast**: Monogamy prevents quantum information from being broadcast to
   multiple parties while maintaining entanglement.
3. **Tensor network physics**: Monogamy limits the entanglement that can be distributed in
   1D many-body systems (area law).

---

## Key Formulas

- **Von Neumann entropy**: `S(ρ) = -Tr[ρ log₂ ρ] = -Σᵢ λᵢ log₂ λᵢ`
- **Quantum mutual information**: `I(A:B) = S(A) + S(B) - S(AB) ≥ 0`
- **Strong subadditivity**: `S(ABC) + S(B) ≤ S(AB) + S(BC)`
- **Holevo bound**: `I_acc ≤ χ = S(Σᵢ pᵢ ρᵢ) - Σᵢ pᵢ S(ρᵢ)`
- **Teleportation**: `1 ebit + 2 cbits → 1 qubit transmitted`
- **Superdense coding**: `1 ebit + 1 qubit transmitted → 2 cbits`
- **Monogamy (CKW)**: `C²_{A|BC} ≥ C²_{AB} + C²_{AC}`

---

## Worked Example: Entanglement Entropy of Bell States

**Maximally entangled state**: `|Φ⁺⟩ = (|00⟩ + |11⟩)/√2`.

**Density matrix**: `ρ_{AB} = |Φ⁺⟩⟨Φ⁺| = (|00⟩⟨00| + |00⟩⟨11| + |11⟩⟨00| + |11⟩⟨11|)/2`.

**Reduced density matrix**: `ρ_A = Tr_B[ρ_{AB}] = (⟨0|ρ_{AB}|0⟩_B + ⟨1|ρ_{AB}|1⟩_B)`
```
= (|0⟩⟨0| + |1⟩⟨1|)/2 = I/2
```

**Von Neumann entropy**: `S(ρ_A) = -Tr[(I/2) log₂(I/2)] = -(1/2 log₂(1/2) + 1/2 log₂(1/2)) = 1` qubit.

**Interpretation**: 1 ebit of entanglement. This is the maximum possible for a 2-qubit system.

**Comparison**: For the product state `|00⟩`: `ρ_A = |0⟩⟨0|`, `S(ρ_A) = 0`. For the partially
entangled state `|ψ⟩ = √(0.9)|00⟩ + √(0.1)|11⟩`: `ρ_A = 0.9|0⟩⟨0| + 0.1|1⟩⟨1|`,
`S(ρ_A) = -0.9 log₂(0.9) - 0.1 log₂(0.1) = 0.469` ebit.

The entanglement ranges continuously from 0 (product) to 1 (maximally entangled), in contrast
to classical correlations which are not quantified in the same way.

---

## Summary

- **Von Neumann entropy** generalizes Shannon entropy; `S = 0` for pure states, `S = log d` for
  maximally mixed; strong subadditivity is the central inequality of quantum information.
- **Quantum conditional entropy** can be negative (for entangled states) — a uniquely quantum
  phenomenon.
- **Holevo bound** limits extractable classical information to the Holevo chi quantity.
- **Quantum capacity**: channels can transmit qubits at rate up to the coherent information;
  depolarizing noise above 25% kills quantum capacity.
- **Teleportation and superdense coding** are dual protocols: `1 ebit + 2 cbits ↔ 1 qubit`.
- **Monogamy of entanglement**: maximal entanglement with one party precludes entanglement with
  others — basis for QKD security proofs.

---

## Exercises

**Exercise 1**: Compute the quantum conditional entropy `S(A|B)` for (a) the classically
correlated state `ρ_{AB} = (|00⟩⟨00| + |11⟩⟨11|)/2` and (b) the Bell state `|Φ⁺⟩`. Interpret
the difference.

<details><summary>Solution</summary>

(a) `ρ_{AB}` has eigenvalues `{1/2, 1/2, 0, 0}`, so `S(AB) = 1`. The marginal is
`ρ_B = I/2`, so `S(B) = 1`. Hence `S(A|B) = S(AB) - S(B) = 1 - 1 = 0`.

(b) `|Φ⁺⟩` is pure: `S(AB) = 0`; marginal maximally mixed: `S(B) = 1`. Hence
`S(A|B) = 0 - 1 = -1`.

Interpretation: with classical correlation, knowing `B` removes all uncertainty about `A`
(`S(A|B) = 0`, exactly as for a classical shared random bit). Entanglement goes further: the
*joint* state is perfectly known (pure) while each part alone is maximally uncertain — a
situation impossible classically (classically `S(A|B) ≥ 0` always). The negative value `-1`
is operationally meaningful: via state merging, Alice can transfer her share using no quantum
communication and *gain* 1 ebit for future use.

</details>

**Exercise 2**: Alice encodes one classical bit by sending `|0⟩` (for 0) or `|+⟩` (for 1),
each with probability 1/2. Compute the Holevo bound on Bob's accessible information.

<details><summary>Solution</summary>

Both signal states are pure, so `χ = S(ρ̄)` with

```
ρ̄ = (|0⟩⟨0| + |+⟩⟨+|)/2 = [[3/4, 1/4], [1/4, 1/4]]
```

Eigenvalues: `λ± = (1 ± 1/√2)/2 ≈ 0.8536, 0.1464` (trace 1, determinant `1/8`).

```
χ = -0.8536 log₂ 0.8536 - 0.1464 log₂ 0.1464 ≈ 0.601 bits
```

Bob can extract at most `≈ 0.60` bits per qubit, even though Alice "used" a full bit — the
non-orthogonality of `|0⟩` and `|+⟩` (overlap `|⟨0|+⟩|² = 1/2`) makes the encoding partly
indistinguishable. (The optimal measurement actually achieves only `≈ 0.399` bits here; Holevo
is an upper bound, not always attained for single-copy measurements.)

</details>

**Exercise 3**: The quantum erasure channel replaces the input qubit by a flagged erasure state
`|e⟩` with probability `p`. Its quantum capacity is `Q = max(1 - 2p, 0)`. (a) Evaluate `Q` at
`p = 0.3`. (b) Give the no-cloning argument for why `Q = 0` at `p = 1/2`.

<details><summary>Solution</summary>

(a) `Q = 1 - 2(0.3) = 0.4` qubits per channel use.

(b) At `p = 1/2`, the channel can be simulated as follows: a symmetric splitter sends the input
to Bob and to the environment (Eve), each receiving it with probability 1/2 and an erasure flag
otherwise — Bob's and Eve's outputs are then *identical* channels. If `Q > 0`, Bob could decode
the transmitted qubit; by symmetry Eve could run the same decoder on her output, producing two
copies of an arbitrary unknown qubit — a cloning machine. No-cloning forbids this, so
`Q(p = 1/2) = 0` (and monotonicity gives `Q = 0` for all `p ≥ 1/2`). This "symmetric channels
have zero capacity" argument is the same one that kills the depolarizing channel at `p = 1/4`.

</details>

**Exercise 4**: Compute the quantum mutual information `I(A:B)` for the Bell state `|Φ⁺⟩` and
compare it with the maximum for two classically correlated bits. Which protocol "cashes in"
this factor?

<details><summary>Solution</summary>

For `|Φ⁺⟩`: `S(A) = S(B) = 1`, `S(AB) = 0`, so

```
I(A:B) = 1 + 1 - 0 = 2
```

Two classical bits (or any separable two-qubit state) satisfy `I(A:B) ≤ 1` when each marginal
carries at most one bit of entropy — perfectly correlated coins give exactly `I = 1`. The Bell
state doubles this, saturating the general bound `I(A:B) ≤ 2 min(S(A), S(B))`.

Superdense coding cashes in exactly this factor: 1 ebit + 1 transmitted qubit → 2 classical
bits, i.e. the pre-shared entanglement doubles the classical information carried per physical
qubit sent.

</details>

---

## Further Reading

1. **Nielsen, M. A. and Chuang, I. L.** — *Quantum Computation and Quantum Information*,
   Cambridge University Press, 2000. Chapters 11–12.
2. **Wilde, M. M.** — *Quantum Information Theory*, Cambridge University Press, 2nd ed. (2017).
   Comprehensive and modern; free arXiv version available.
3. **Lieb, E. H. and Ruskai, M. B.** — "Proof of the strong subadditivity of quantum-mechanical
   entropy," *J. Math. Phys.* 14, 1938 (1973). Original SSA proof.
4. **Bennett, C. H. et al.** — "Teleporting an unknown quantum state via dual classical and
   Einstein-Podolsky-Rosen channels," *Phys. Rev. Lett.* 70, 1895 (1993). Quantum teleportation.
5. **Coffman, V., Kundu, J., and Wootters, W. K.** — "Distributed entanglement," *Phys. Rev.
   A* 61, 052306 (2000). Monogamy of entanglement.
