# Measurement-Based Quantum Computation

> **Prerequisites**: 03_quantum_gates_and_circuits/01_single_qubit_gates.md, 02_multi_qubit_gates.md (CZ gate), 02_quantum_mechanics/03_quantum_measurements.md  
> **Connects to**: Stabilizer formalism (Chapter 5.4 — graph states are stabilizer states), photonic hardware and fusion-based QC (Chapter 7.3), circuit model and universality (Chapter 3.3)

## Overview

The circuit model treats measurement as the final, destructive step of a computation. **Measurement-based quantum computation** (MBQC, also called the **one-way quantum computer**, Raussendorf and Briegel, 2001) turns this picture inside out: all the entanglement is created *first*, in a single fixed, algorithm-independent resource state — the **cluster state** — and the computation is then driven entirely by **single-qubit measurements**, performed one qubit at a time in adaptively chosen bases. No entangling gate is ever applied during the computation itself.

This sounds impossible at first: measurements are random and irreversible, so how can a sequence of them implement a deterministic unitary? The resolution has two parts. First, measuring a cluster qubit in a rotated basis *teleports* the logical state to a neighboring qubit while applying a known rotation to it. Second, the randomness of each outcome shows up only as a known Pauli **byproduct operator** (`X` or `Z`), which can be compensated by classically adapting later measurement angles — **feed-forward**. Determinism is recovered at the level of the whole computation even though every individual measurement outcome is a coin flip.

MBQC is strictly equivalent in power to the circuit model, but the equivalence is far from trivial in its resource accounting: it trades circuit *depth* for cluster *width*, it makes the cost of adaptivity explicit (Clifford parts of a computation need no adaptivity at all and collapse into a single simultaneous measurement round), and it is the natural computational model for photonic hardware, where two-qubit gates are probabilistic but single-qubit measurements are easy. Modern **fusion-based** photonic architectures (PsiQuantum) are direct descendants of this model.

## Cluster and Graph States

### Definition via CZ

Let `G = (V, E)` be a graph with `n` vertices. The **graph state** `|G⟩` is built in two steps:

1. Prepare every vertex qubit in `|+⟩ = (|0⟩+|1⟩)/√2`, giving `|+⟩^{⊗n}`
2. Apply `CZ` on every edge:

$$|G\rangle = \prod_{(u,v)\in E} CZ_{uv}\,|+\rangle^{\otimes n}$$

The order of the CZ gates is irrelevant — they are diagonal and all commute. A **cluster state** is the special case where `G` is a regular lattice: a line (1D cluster) or a square grid (2D cluster).

**Smallest example — two-qubit cluster**: `CZ|++⟩ = ½(|00⟩+|01⟩+|10⟩-|11⟩)`. This is maximally entangled (it is `(|0⟩|+⟩ + |1⟩|−⟩)/√2`, local-unitary equivalent to a Bell state).

### Stabilizer Description

Graph states are **stabilizer states** (Chapter 5.4). The stabilizer generators are read directly off the graph — one per vertex:

$$K_v = X_v \prod_{u \in N(v)} Z_u, \qquad K_v|G\rangle = +|G\rangle$$

where `N(v)` is the set of neighbors of `v`. The derivation is one line of conjugation: `|+⟩^{⊗n}` is stabilized by `{X_v}`, and each `CZ_{uv}` conjugates `X_v → X_v Z_u` (while fixing all `Z` operators). Applying all edge CZs dresses `X_v` with one `Z` per neighbor.

For the two-qubit cluster the generators are `K₁ = X⊗Z` and `K₂ = Z⊗X`; for a linear cluster the interior generators are `K_v = Z_{v-1} X_v Z_{v+1}`. The `n` generators determine `|G⟩` uniquely, so a graph state on `n` qubits is described by `O(n²)` classical bits (the adjacency matrix) — the Gottesman-Knill compression of Chapter 3.3 in action.

Two useful stabilizer consequences:

- **Z-measurement deletes a vertex**: measuring qubit `v` in the `Z` basis removes it from the graph (up to `Z` corrections on its neighbors). This is how unwanted lattice qubits are carved away.
- **Local complementation**: measuring in the `Y` basis, or applying certain local Cliffords, transforms the graph by complementing the neighborhood of a vertex — graph states that look different can be local-Clifford equivalent (e.g., the 3-vertex star graph and the GHZ state, see Exercise 4).

## The Teleportation Primitive

### One Segment: CZ Plus a Rotated Measurement

Everything in MBQC reduces to one two-qubit identity. Take an input qubit in `|ψ⟩ = α|0⟩ + β|1⟩`, attach a fresh `|+⟩` qubit with a CZ, and measure the *input* qubit in the rotated basis

$$|\pm_\theta\rangle = \frac{|0\rangle \pm e^{-i\theta}|1\rangle}{\sqrt{2}}$$

(the eigenbasis of the observable `cos θ · X − sin θ · Y`; for `θ = 0` this is the ordinary `X` basis). Write the post-CZ state grouped by the measurement basis:

$$CZ\,(|\psi\rangle \otimes |+\rangle) = \alpha|0\rangle|+\rangle + \beta|1\rangle|-\rangle$$

Projecting qubit 1 onto `⟨±_θ|` (note `⟨±_θ|1⟩ = ±e^{+iθ}/√2`) leaves qubit 2 in

$$\text{outcome } m \in \{0,1\}: \qquad |\text{out}\rangle \propto \alpha|+\rangle + (-1)^m \beta e^{i\theta}|-\rangle = H\left(\alpha|0\rangle + (-1)^m \beta e^{i\theta}|1\rangle\right)$$

Using `HZ = XH` to pull the outcome-dependent sign out as a Pauli:

$$|\text{out}\rangle = X^m H R_z(\theta)|\psi\rangle, \qquad R_z(\theta) = \mathrm{diag}(1, e^{i\theta})$$

**One measurement therefore implements the unitary `H·Rz(θ)` on the logical state**, teleporting it one site down the wire, at the price of a random known byproduct `X^m`. Both outcomes occur with probability exactly `1/2` regardless of `|ψ⟩` and `θ` — the outcome carries no information about the data (as it must, or measurement statistics would signal the logical state).

### Byproduct Operators

The byproduct `X^m` is not an error: `m` is known, so the byproduct is a known Pauli frame. There are two ways to deal with it:

1. **Track it classically** and reinterpret the final computational-basis readout (a final `X` byproduct flips the readout bit; a final `Z` byproduct does nothing to a `Z`-basis measurement)
2. **Adapt subsequent measurement bases** so that the byproduct commutes harmlessly through the rest of the pattern

Only non-Clifford rotations force option 2, as the next section shows.

## The One-Dimensional Wire

### Concatenating Segments

A linear cluster of `n+1` qubits with the input at one end is a **quantum wire**. Measuring qubits `1, 2, ..., n` at angles `θ₁, θ₂, ..., θₙ` (outcomes `m₁, ..., mₙ`) applies

$$|\text{out}\rangle = \left[\prod_{j=n}^{1} X^{m_j} H R_z(\theta_j)\right]|\psi\rangle$$

Since `HRz(θ)` factors alternate with Paulis, and `H X = Z H`, all byproducts can be commuted to the front, leaving a clean product of `HRz` rotations preceded by an overall Pauli `X^a Z^b` with `a, b` computable from the outcome record. Three consecutive segments give (using `HRz(θ)H = Rx(θ)` to pair the middle Hadamard)

$$H R_z(\theta_3)\cdot H R_z(\theta_2)\cdot H R_z(\theta_1) = H\, R_z(\theta_3)\,R_x(\theta_2)\,R_z(\theta_1)$$

which, by the Euler-angle decomposition (Chapter 3.1), reaches **any** single-qubit unitary up to the tracked Pauli and a leading `H` (absorbed by one more wire segment at `θ = 0`).

### Adaptivity and Feed-Forward

Commuting a byproduct through a rotation flips its angle:

$$X\,R_z(\theta) = R_z(-\theta)\,X \quad \text{(up to global phase)}$$

So if segment 1 produced outcome `m₁`, the rotation that segment 2 *actually* applies to the logical state is `Rz((-1)^{m₁}θ₂)` unless we intervene. The fix is **feed-forward**: measure qubit 2 at the adapted angle `(-1)^{m₁}θ₂`, so the *logical* rotation is always `Rz(θ₂)` regardless of `m₁`. This is the origin of the temporal order in MBQC — a measurement whose angle depends on an earlier outcome cannot be performed before that outcome exists.

**Clifford exception**: for `θ ∈ {0, ±π/2, π}` the adapted basis is the same basis (possibly with outcome relabeling): `X`- and `Y`-basis measurements never need adaptation. Hence **the entire Clifford part of a computation can be measured simultaneously in one round**, and only non-Clifford rotations (the T-gates of Chapter 3.3, in measurement clothing) create sequential depth. MBQC makes the Clifford/non-Clifford divide a *temporal* statement.

## Universality of the 2D Cluster State

A 1D wire only makes single-qubit unitaries. Universality requires an entangling gate, and this is exactly what the second dimension of a 2D cluster provides.

- **Arbitrary single-qubit unitaries**: horizontal chains of 3 (plus wire-extension) measurements implement `HRz(θ₃)HRz(θ₂)HRz(θ₁)` = any `U ∈ SU(2)` as above
- **CZ gates**: two horizontal wires joined by a vertical edge implement a CZ between the two logical qubits — the vertical CZ of the resource state *is* the logical CZ, teleported onto the logical states as they pass through. No measurement is needed to enact it beyond the wire measurements themselves
- **Layout**: unwanted lattice qubits are removed by `Z` measurements (vertex deletion), carving the fixed lattice into the circuit's wiring diagram

Since `{CZ, single-qubit unitaries}` ⊇ `{H, T, CNOT}` up to trivial rewriting, **the 2D cluster state is a universal resource**: any `n`-qubit, depth-`d` circuit compiles to measurements on a cluster of size `O(n) × O(d)`.

**Equivalence to the circuit model.** The simulation runs both ways with polynomial overhead:

- *Circuit → MBQC*: as above; cluster width ∝ circuit width, cluster length ∝ circuit depth, total qubits `O(nd)`
- *MBQC → circuit*: a measurement pattern on `N` cluster qubits is a circuit of `N` CZs, `N` single-qubit measurements, and classical control — directly executable in the circuit model with `O(N)` gates

The interesting tradeoff is **depth versus width**. MBQC spends a factor `O(d)` more qubits, but the *quantum* depth of the measurement sequence is set only by the adaptivity structure: `O(1)` measurement rounds for Clifford circuits (a genuine depth collapse — in the circuit model even Clifford circuits need depth `Ω(log n)`), and one round per layer of non-Clifford angles in general. MBQC is thus a natural framework for studying parallelism in quantum computation.

## Connections: Photonics, Fusion, and Codes

MBQC's practical appeal is that it front-loads all entangling operations into resource-state preparation, which may be **probabilistic** — fail-and-retry is acceptable *before* the logical data exists. This matches photonics (Chapter 7.3): linear-optics entangling gates succeed only probabilistically, but small entangled photon clusters can be generated, and **fusion measurements** (probabilistic two-photon Bell measurements) stitch them into larger clusters. **Fusion-based quantum computation** (FBQC, the PsiQuantum architecture) takes the limit of this idea: the computation consists entirely of generating small fixed resource states and fusing them, with the fusion outcomes playing the role of MBQC measurement outcomes.

The stabilizer connection runs deep: a 3D cluster state measured layer by layer implements the surface code (Chapter 5.6) — each 2D slice is one round of syndrome extraction ("foliation"). Fault-tolerant MBQC and circuit-model fault tolerance are two views of the same 3D spacetime object.

## Key Formulas

**Graph state**:
$$|G\rangle = \prod_{(u,v)\in E} CZ_{uv}|+\rangle^{\otimes n}, \qquad K_v = X_v \prod_{u\in N(v)} Z_u,\quad K_v|G\rangle = |G\rangle$$

**Teleportation primitive** (measure at angle `θ`, outcome `m`, each with `P = 1/2`):
$$CZ(|\psi\rangle\otimes|+\rangle) \xrightarrow{\ \langle\pm_\theta|\ } X^m H R_z(\theta)|\psi\rangle, \qquad |\pm_\theta\rangle = \frac{|0\rangle \pm e^{-i\theta}|1\rangle}{\sqrt 2}$$

**Byproduct propagation** (feed-forward rule):
$$X\,R_z(\theta) = R_z(-\theta)\,X \ \text{(up to phase)}, \qquad H X = Z H, \qquad HZ = XH$$

**Single-qubit universality on a wire** (reaches any `SU(2)` element via Euler angles, up to the leading `H` and global phase):
$$H R_z(\theta_3)\cdot H R_z(\theta_2)\cdot H R_z(\theta_1) = H\,R_z(\theta_3)\,R_x(\theta_2)\,R_z(\theta_1)$$

**Resource scaling**: circuit of width `n`, depth `d` → cluster of `O(n·d)` qubits; adaptive measurement rounds = non-Clifford depth (Clifford circuits: one round).

## Worked Example

**Problem**: Push `|ψ⟩ = (3/5)|0⟩ + (4/5)|1⟩` through one wire segment with measurement angle `θ = π/3`. Give the state after the CZ, both post-measurement states with full amplitudes, and verify the output is `X^m H R_z(π/3)|ψ⟩`.

**Solution**:

**Step 1 — Entangle.** With `|+⟩ = (|0⟩+|1⟩)/√2` on qubit 2:

$$CZ(|\psi\rangle\otimes|+\rangle) = \tfrac{1}{\sqrt2}\left(0.6|00\rangle + 0.6|01\rangle + 0.8|10\rangle - 0.8|11\rangle\right)$$

Numerically the four amplitudes are `(0.424264, 0.424264, 0.565685, -0.565685)` — only the `|11⟩` term picked up the CZ sign.

**Step 2 — Measure qubit 1 at `θ = π/3`.** Here `e^{iθ} = 0.5 + 0.866025i`. Expanding qubit 1 in `|±_θ⟩` and collecting qubit-2 amplitudes gives the unnormalized post-measurement states

$$m = 0:\ \frac{\alpha + \beta e^{i\theta}}{2}|0\rangle + \frac{\alpha - \beta e^{i\theta}}{2}|1\rangle, \qquad m = 1:\ \frac{\alpha - \beta e^{i\theta}}{2}|0\rangle + \frac{\alpha + \beta e^{i\theta}}{2}|1\rangle$$

With `α = 0.6`, `β = 0.8`: `βe^{iθ} = 0.4 + 0.692820i`, so

- `(α + βe^{iθ})/2 = 0.5 + 0.346410i`, with `|·|² = 0.37`
- `(α − βe^{iθ})/2 = 0.1 − 0.346410i`, with `|·|² = 0.13`

**Probabilities**: `P(m=0) = 0.37 + 0.13 = 0.5` and `P(m=1) = 0.13 + 0.37 = 0.5` — exactly `1/2` each, independent of `α, β, θ`, as the general argument demands.

**Step 3 — Normalize and compare.** Multiplying by `√2`, the normalized outputs are

$$m=0:\ (0.707107 + 0.489898i)|0\rangle + (0.141421 - 0.489898i)|1\rangle$$
$$m=1:\ (0.141421 - 0.489898i)|0\rangle + (0.707107 + 0.489898i)|1\rangle$$

Direct target computation: `Rz(π/3)|ψ⟩ = 0.6|0⟩ + (0.4 + 0.692820i)|1⟩`, then applying `H` gives `(0.707107+0.489898i)|0⟩ + (0.141421−0.489898i)|1⟩` — exactly the `m=0` output, and the `m=1` output is this with the two amplitudes swapped, i.e., an extra `X`. So

$$|\text{out}\rangle = X^m\,H\,R_z(\pi/3)|\psi\rangle \checkmark$$

Numerical verification (numpy, projecting the 4-component state onto both basis vectors and comparing with the target up to global phase) confirms both outcomes to machine precision, and a 200-trial randomized test over Haar-random `|ψ⟩` and uniform `θ` confirms the general rule `X^m H Rz(θ)` with `P(m) = 1/2` in every trial.

## Summary

- MBQC inverts the circuit model: a fixed, algorithm-independent **cluster state** is prepared first, and computation proceeds by **adaptive single-qubit measurements** only
- **Graph states** `|G⟩ = ∏ CZ|+⟩^n` are stabilizer states with generators `K_v = X_v ∏_{u∈N(v)} Z_u` — one per vertex, read off the graph
- The primitive: CZ to a fresh `|+⟩`, then measurement in the `θ`-rotated basis, teleports the state and applies `X^m H Rz(θ)`; each outcome has probability exactly `1/2`
- Random outcomes appear only as known Pauli **byproducts**; commuting them forward flips later angles (`X Rz(θ)X = Rz(−θ)`), which **feed-forward** compensates by measuring at `(−1)^m θ`
- Only non-Clifford angles require adaptivity — Clifford computation collapses to a single measurement round, making the Clifford/T divide a statement about *time*
- The **2D cluster state is universal**: chains give arbitrary `SU(2)` via Euler angles, vertical edges give CZ, `Z`-measurements delete unused qubits; circuit ↔ MBQC translation costs `O(nd)` qubits and preserves efficiency
- MBQC underlies **fusion-based photonic architectures** and, via 3D clusters, is dual to surface-code fault tolerance

## Exercises

**Exercise 1**: Verify by direct computation that `K₁ = X⊗Z` and `K₂ = Z⊗X` stabilize the two-qubit cluster state `|C₂⟩ = ½(|00⟩+|01⟩+|10⟩−|11⟩)`, and show that their product `K₁K₂` equals `Y⊗Y` and is also a stabilizer element.

<details><summary>Solution</summary>

`(X⊗Z)|C₂⟩`: `X` on qubit 1 swaps the first bit, `Z` on qubit 2 negates `|·1⟩` terms. Term by term: `|00⟩→|10⟩`, `|01⟩→−|11⟩`, `|10⟩→|00⟩`, `−|11⟩→+|01⟩`, giving `½(|10⟩−|11⟩+|00⟩+|01⟩) = |C₂⟩` ✓. By the symmetry of `|C₂⟩` under qubit swap, `(Z⊗X)|C₂⟩ = |C₂⟩` ✓.

Product: `K₁K₂ = (X⊗Z)(Z⊗X) = (XZ)⊗(ZX)`. Careful with the signs: `XZ = −iY` and `ZX = +iY`, so `K₁K₂ = (−iY)⊗(iY) = (−i)(i)·(Y⊗Y) = Y⊗Y`. Since the stabilizer group is closed under multiplication, `(Y⊗Y)|C₂⟩ = |C₂⟩` — which a term-by-term check confirms (`Y⊗Y` maps `|00⟩→−|11⟩` and `−|11⟩→... →|00⟩` etc., reproducing all four amplitudes). (Numerically verified: both generators and their product return the state exactly.)

</details>

**Exercise 2**: Show that measuring at `θ = 0` (the `X` basis) implements the Hadamard: one segment gives `X^m H|ψ⟩`. Then chain two `X`-basis segments on a 3-qubit linear cluster and show the output is `X^{m₂}Z^{m₁}|ψ⟩` — pure teleportation, no net rotation, no adaptivity needed.

<details><summary>Solution</summary>

At `θ = 0`, `Rz(0) = I`, so one segment gives `X^m H|ψ⟩` directly from the primitive.

Two segments compose to `X^{m₂}H · X^{m₁}H|ψ⟩`. Commute the inner byproduct through the outer Hadamard using `HX = ZH`:

`X^{m₂} H X^{m₁} H = X^{m₂} Z^{m₁} H H = X^{m₂} Z^{m₁}`

The output is `|ψ⟩` up to a fully known Pauli — the state has been teleported two sites with no rotation. Neither measurement angle depended on an earlier outcome, illustrating the Clifford exception: `X`-basis patterns are non-adaptive and can be measured simultaneously. (Numerically verified for all four outcome pairs `(m₁, m₂)` on a random input state.)

</details>

**Exercise 3**: Prove the feed-forward rule: commuting the byproduct `X^{m₁}` through the second segment's rotation requires measuring qubit 2 at `(−1)^{m₁}θ₂` to realize the logical rotation `Rz(θ₂)`. Use `X Rz(θ) = Rz(−θ)X` (up to global phase) and verify the phase.

<details><summary>Solution</summary>

With `Rz(θ) = diag(1, e^{iθ})`: `X·Rz(θ)` has matrix rows `[(0, e^{iθ}), (1, 0)]`, while `Rz(−θ)·X` has rows `[(0, 1), (e^{−iθ}, 0)]`. They differ by exactly the global phase `e^{iθ}`: `X Rz(θ) = e^{iθ} Rz(−θ) X`. (In the symmetric convention `Rz(θ) = diag(e^{−iθ/2}, e^{iθ/2})` the identity is exact with no phase — numerically confirmed.)

Segment 2 measured at angle `φ` acts on the incoming state `X^{m₁}H Rz(θ₁)|ψ⟩` as `X^{m₂}HRz(φ)·X^{m₁}(\cdots)`. Pulling `X^{m₁}` leftward: `Rz(φ)X^{m₁} = X^{m₁}Rz((−1)^{m₁}φ)` up to phase, so the *logical* rotation applied is `Rz((−1)^{m₁}φ)`. Choosing `φ = (−1)^{m₁}θ₂` makes this `Rz(θ₂)` for either outcome — the feed-forward rule. If `m₁ = 0` no adaptation occurs; if `m₁ = 1` the angle is negated. For `θ₂ ∈ {0, π}` the two bases coincide, recovering the Clifford exception.

</details>

**Exercise 4**: Show that the 3-qubit **star graph state** (center qubit 1 joined to qubits 2 and 3) becomes the GHZ state `(|000⟩+|111⟩)/√2` under `I⊗H⊗H`, confirming that GHZ is a graph state up to local unitaries.

<details><summary>Solution</summary>

`|G_star⟩ = CZ₁₂CZ₁₃|+++⟩`. Split on qubit 1: the `|0⟩` branch leaves qubits 2,3 in `|++⟩`; the `|1⟩` branch applies `Z⊗Z`, giving `|−−⟩`:

`|G_star⟩ = (|0⟩|+⟩|+⟩ + |1⟩|−⟩|−⟩)/√2`

Applying `H` to qubits 2 and 3 maps `|+⟩→|0⟩`, `|−⟩→|1⟩`:

`(I⊗H⊗H)|G_star⟩ = (|000⟩ + |111⟩)/√2` ✓ (numerically confirmed up to global phase)

Consistency check via stabilizers: the star generators `{X₁Z₂Z₃, Z₁X₂, Z₁X₃}` conjugate under `H₂, H₃` to `{X₁X₂X₃, Z₁Z₂, Z₁Z₃}` — precisely the GHZ stabilizer. Local (Clifford) unitaries preserve entanglement structure, so GHZ-type entanglement "is" star-graph entanglement.

</details>

**Exercise 5**: A circuit has width `n = 100` qubits and depth `d = 50` layers, of which 10 layers contain non-Clifford rotations (the rest are Clifford). Estimate (a) the cluster size for the MBQC compilation, (b) the number of adaptive measurement rounds, and (c) compare the quantum depth to the circuit-model execution.

<details><summary>Solution</summary>

(a) Cluster size ~ width × length: each circuit layer consumes `O(1)` cluster columns per logical qubit (a few columns per rotation via the 3-angle chain), so the cluster has on the order of `100 × 50 = 5000` sites up to the constant — tens of thousands of physical qubits with realistic constants. All must be entangled *before* measurement begins (or generated just-in-time layer by layer, as practical proposals do).

(b) Adaptive rounds are set by the non-Clifford structure only: all Clifford layers merge into a single simultaneous round, and each of the 10 non-Clifford layers needs its outcomes before the next adapted angles can be set → **11 rounds** (1 Clifford + 10 adaptive), versus 50 sequential layers for the circuit.

(c) Quantum depth drops from 50 gate layers to 11 measurement rounds — a ~4.5× parallelization bought with a ~50× qubit overhead. This is the MBQC depth/width tradeoff in miniature: time becomes cheap, space becomes the scarce resource, and *adaptivity* (= non-Cliffordness) is revealed as the true source of temporal depth.

</details>

## Further Reading

1. **Raussendorf & Briegel**, "A One-Way Quantum Computer" (Physical Review Letters 86, 5188, 2001) — the founding paper: cluster states, measurement patterns, and universality in four pages
2. **Raussendorf, Browne & Briegel**, "Measurement-based quantum computation on cluster states" (Physical Review A 68, 022312, 2003) — the detailed follow-up: byproduct algebra, feed-forward, circuit compilation, and fault-tolerance considerations
3. **Hein, Dür, Eisert, Raussendorf, Van den Nest & Briegel**, "Entanglement in graph states and its applications" (arXiv:quant-ph/0602096, 2006) — comprehensive graph-state review: stabilizers, local complementation, equivalence classes; Sections 2-4 are the reference for this chapter's formalism
4. **Briegel, Browne, Dür, Raussendorf & Van den Nest**, "Measurement-based quantum computation" (Nature Physics 5, 19, 2009) — accessible review connecting MBQC to entanglement theory and computational models
5. **Bartolucci et al. (PsiQuantum)**, "Fusion-based quantum computation" (Nature Communications 14, 912, 2023) — the modern photonic architecture descended from MBQC: resource states, fusion networks, and fault tolerance without a monolithic cluster
