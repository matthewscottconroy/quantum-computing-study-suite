# Postulates of Quantum Mechanics

> **Prerequisites**: 01_linear_algebra.md, 02_complex_numbers_and_hilbert_spaces.md, 03_tensor_products_and_multipartite_systems.md  
> **Connects to**: Every subsequent chapter — these postulates are the axiomatic foundation from which all quantum computing theory is derived

## Overview

Physics progresses by finding the minimal set of assumptions from which all observed phenomena can be derived. Quantum mechanics, as currently understood, rests on **four postulates**. Everything else — interference, entanglement, the measurement problem, quantum speedups, decoherence — is a consequence of these four axioms applied to specific systems.

These postulates are remarkable for their mathematical precision. Unlike classical mechanics, which can be stated informally before being made rigorous, the postulates of quantum mechanics essentially require the mathematical language of Hilbert spaces and linear operators. The formalism is not a decoration over an intuitively obvious theory; it *is* the theory.

This chapter states the postulates carefully and discusses what each one means, why it takes the form it does, and what would break if we tried to weaken or modify it. We also discuss the deep interpretational puzzle around Postulate 3 (measurement), which remains philosophically contentious despite being computationally unambiguous.

A crucial point to internalize: the Born rule (the probability interpretation of amplitudes in Postulate 3) is a **postulate**, not a theorem. It has never been derived from the other postulates in a fully satisfactory way. Significant theoretical effort has been devoted to this question — the many-worlds interpretation, Gleason's theorem, and quantum Bayesianism all approach it differently — but no consensus exists. For the practical purposes of quantum computing, the Born rule simply works.

## Postulate 1: State Space

> **Postulate 1**: The state of an isolated physical system is represented by a **unit vector** in a complex Hilbert space `ℋ`, called the **state space** of the system.

The state vector `|ψ⟩ ∈ ℋ` with `⟨ψ|ψ⟩ = 1` encodes all information that can ever be known about the system. The state space of a **qubit** (two-level quantum system) is `ℋ = ℂ²`. A general qubit state is:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \quad |\alpha|^2 + |\beta|^2 = 1$$

where `α, β ∈ ℂ`.

**Why unit vectors**: The normalization condition ensures that probabilities (as computed by Postulate 3) sum to 1. If `|ψ⟩` were not normalized, probabilities would not be valid.

**Why complex numbers**: As argued in Chapter 1.2, quantum interference requires complex amplitudes. With real amplitudes only, relative phases are limited to `±1`, which is insufficient to describe the full range of quantum phenomena.

**What the state is**: In the Copenhagen interpretation, `|ψ⟩` is not a description of an objective physical reality but of our information about (or dispositions of) the system. In the many-worlds interpretation, `|ψ⟩` is a perfectly real object in a much larger Hilbert space. The mathematics is the same either way.

**Global phase**: As established in Chapter 1.2, `|ψ⟩` and `e^{iθ}|ψ⟩` represent the same physical state. Formally, the state space is the **projective Hilbert space** `P(ℋ)`, but we usually work with unit vectors and just remember to ignore global phases.

### Classical Analogy and Departure

In classical mechanics, the state of a particle is a point `(q, p)` in phase space. The state fully determines the future evolution (given the Hamiltonian). In quantum mechanics, the state `|ψ⟩` also fully determines future evolution (Postulate 2) — but it determines future **measurement probability distributions**, not future measurement outcomes. This is a fundamental departure from classical determinism.

Quantum states generalize classical probability distributions in a precise sense: a classical probability distribution `{pᵢ}` is like a diagonal density matrix `ρ = Σᵢ pᵢ|i⟩⟨i|`, but quantum states also allow **off-diagonal coherences** that produce interference. These coherences have no classical analogue.

## Postulate 2: Dynamics

> **Postulate 2**: The time evolution of a closed quantum system is described by a **unitary operator**. If the state at time `t₁` is `|ψ(t₁)⟩`, then at time `t₂` the state is:
> $$|\psi(t_2)\rangle = U(t_1, t_2)|\psi(t_1)\rangle$$
> where `U` is a unitary operator depending only on `t₁` and `t₂`.

For a time-independent Hamiltonian `H` (a Hermitian operator representing the total energy), the time evolution operator is:

$$U(t) = e^{-iHt/\hbar}$$

This is the solution to the **Schrödinger equation**:

$$i\hbar \frac{\partial}{\partial t}|\psi(t)\rangle = H|\psi(t)\rangle$$

The Schrödinger equation is the infinitesimal statement of Postulate 2: the Hamiltonian `H` is the generator of time evolution.

**Why unitary evolution is necessary**: Unitarity `U†U = I` preserves the inner product: `⟨ψ(t₂)|ψ(t₂)⟩ = ⟨ψ(t₁)|U†U|ψ(t₁)⟩ = ⟨ψ(t₁)|ψ(t₁)⟩ = 1`. Probabilities remain normalized at all times. Any non-unitary evolution would create or destroy probability.

**Why Hermitian generates unitary**: If `H = H†`, then `(e^{-iHt})† = e^{iH†t} = e^{iHt}`. So `U†U = e^{iHt}e^{-iHt} = I`. Hermiticity of the Hamiltonian is exactly what ensures unitarity of time evolution.

**In quantum computing**: Gates are unitary operators. Applying a quantum gate `G` to state `|ψ⟩` produces `G|ψ⟩`. The circuit is a product of unitary operations, hence itself unitary.

**Time reversibility**: Unitary evolution is reversible: `U⁻¹ = U†`. Every quantum circuit can in principle be run backwards. This is unlike irreversible classical logic gates (like AND, OR) and has important consequences for fault tolerance and thermodynamics.

## Postulate 3: Measurement

> **Postulate 3**: Quantum measurements are described by a collection `{Mₘ}` of **measurement operators**, indexed by outcome `m`, satisfying the **completeness condition**:
> $$\sum_m M_m^\dagger M_m = I$$
> If the system is in state `|ψ⟩`, then:
> - Outcome `m` occurs with probability `p(m) = ⟨ψ|Mₘ†Mₘ|ψ⟩`
> - After obtaining outcome `m`, the state collapses to:
> $$|\psi_m\rangle = \frac{M_m|\psi\rangle}{\sqrt{p(m)}}$$

The completeness condition ensures `Σₘ p(m) = Σₘ ⟨ψ|Mₘ†Mₘ|ψ⟩ = ⟨ψ|(Σₘ Mₘ†Mₘ)|ψ⟩ = ⟨ψ|ψ⟩ = 1`. All probabilities sum to 1.

**Projective measurements** are the special case where `Mₘ = Pₘ` are orthogonal projectors: `PₘPₘ' = δₘₘ'Pₘ` and `ΣₘPₘ = I`. Then `Mₘ†Mₘ = Pₘ†Pₘ = Pₘ² = Pₘ` and:

$$p(m) = \langle\psi|P_m|\psi\rangle, \quad |\psi_m\rangle = \frac{P_m|\psi\rangle}{\sqrt{p(m)}}$$

For an observable `M = Σₘ m Pₘ` (spectral decomposition), the **expectation value** is:

$$\langle M \rangle = \sum_m m\, p(m) = \sum_m m \langle\psi|P_m|\psi\rangle = \langle\psi|M|\psi\rangle$$

**Standard computational basis measurement**: The most common measurement in quantum computing projects onto `{|0⟩, |1⟩}` (or `{|0⟩⟨0|, |1⟩⟨1|}` in projector notation). For `|ψ⟩ = α|0⟩ + β|1⟩`:

$$p(0) = |\alpha|^2, \quad p(1) = |\beta|^2$$

After measuring 0, the state is `|0⟩`; after measuring 1, the state is `|1⟩`. The superposition is destroyed — this is **wavefunction collapse**.

### The Born Rule as a Postulate

The rule `p(m) = ⟨ψ|Mₘ†Mₘ|ψ⟩` is the **Born rule**, named after Max Born who proposed it in 1926. It is the single most experimentally well-tested rule in all of physics, confirmed to extraordinary precision in countless experiments. Yet it has never been convincingly *derived* from the other postulates.

**Gleason's theorem** comes closest: it shows that if we want a probability assignment to subspaces of a Hilbert space of dimension ≥ 3 that is additive on orthogonal subspaces, then it must be of the form `p = Tr(ρP)` for some density operator `ρ`. This constrains the *form* of the Born rule but does not derive the quantum state `|ψ⟩` as such.

**Why this matters for quantum computing**: The Born rule is what connects quantum amplitudes to computational outcomes. The whole goal of quantum algorithm design is to engineer interference so that the Born rule gives high probability to the correct answer. Understanding that this rule is postulated, not derived, helps clarify why quantum mechanics is irreducibly probabilistic.

### Collapse and the Measurement Problem

The "collapse" of the state after measurement (`|ψ⟩ → |ψₘ⟩`) is not a physical process in Postulate 2's sense — Postulate 2 says evolution is unitary, but collapse is not. This tension is the **measurement problem** and remains unresolved after a century of debate.

For quantum computing purposes, we sidestep the philosophical issues by treating collapse as an operational rule: after obtaining outcome `m`, update the state to `|ψₘ⟩` for all subsequent calculations. This is the standard **Copenhagen update rule** and it works perfectly for computing predictions.

## Postulate 4: Composite Systems

> **Postulate 4**: The state space of a composite physical system is the **tensor product** of the state spaces of the component systems. If systems 1 and 2 are in states `|ψ₁⟩` and `|ψ₂⟩`, the joint state is `|ψ₁⟩ ⊗ |ψ₂⟩`.

This postulate is deceptively simple but has profound consequences:

1. **Entanglement exists**: The tensor product allows states like `(|00⟩+|11⟩)/√2` that cannot be written as `|ψ₁⟩ ⊗ |ψ₂⟩`. These are entangled states.

2. **Exponential state space**: `n` qubits have state space `ℂ^{2ⁿ}`. This is why simulating a quantum computer classically is hard.

3. **Non-locality without signaling**: Entangled systems can have correlated measurement outcomes even when spatially separated, but these correlations cannot be used to send information faster than light (because we cannot control which outcome we get).

## Consistency and Necessity of the Postulates

The four postulates are highly constrained — each one is close to the minimal assumption needed to make the theory work.

**Can we drop any postulate?**:
- Without Postulate 1 (Hilbert space structure): no way to combine states or compute probabilities
- Without Postulate 2 (unitary evolution): time evolution could be non-linear, creating serious problems (non-linear quantum mechanics would allow superluminal signaling, as Gisin showed)
- Without Postulate 3 (the Born rule): no way to connect the mathematics to observable frequencies; the theory makes no predictions
- Without Postulate 4 (tensor product): no composite systems, no entanglement, no quantum communication

**Modifications and alternatives**:
- **Spontaneous collapse models** (GRW, CSL): modify Postulate 2 to include stochastic, non-unitary collapse events. These are empirically viable but predict tiny deviations from standard QM.
- **Bohmian mechanics**: keeps Postulate 1 but adds hidden variables; deterministic but non-local.
- **Many-worlds**: keeps Postulates 1-4 exactly but reinterprets what they mean; avoids collapse by treating the universal wavefunction as real.

All of these give the same computational predictions for quantum algorithms.

## Key Formulas

**Postulate 1 — Normalization**:
$$\langle \psi | \psi \rangle = 1$$

**Postulate 2 — Unitary evolution**:
$$|\psi(t)\rangle = e^{-iHt/\hbar}|\psi(0)\rangle, \quad U^\dagger U = I$$

**Postulate 2 — Schrödinger equation**:
$$i\hbar \frac{d}{dt}|\psi(t)\rangle = H|\psi(t)\rangle$$

**Postulate 3 — Born rule (general)**:
$$p(m) = \langle\psi|M_m^\dagger M_m|\psi\rangle$$

**Postulate 3 — Born rule (projective)**:
$$p(m) = \langle\psi|P_m|\psi\rangle = \|P_m|\psi\rangle\|^2$$

**Postulate 3 — Post-measurement state**:
$$|\psi_m\rangle = \frac{M_m|\psi\rangle}{\sqrt{p(m)}}$$

**Postulate 3 — Expectation value**:
$$\langle M \rangle = \langle\psi|M|\psi\rangle$$

**Postulate 4 — Tensor product**:
$$\mathcal{H}_{12} = \mathcal{H}_1 \otimes \mathcal{H}_2, \quad \dim = \dim(\mathcal{H}_1) \cdot \dim(\mathcal{H}_2)$$

## Worked Example

**Problem**: A qubit is prepared in state `|ψ⟩ = (|0⟩ + i|1⟩)/√2`. 

(a) Verify normalization.  
(b) Find the probabilities for outcomes 0 and 1 in a computational basis measurement.  
(c) Find the expectation value of `Z`.  
(d) Show that unitary time evolution under `H = ωZ/2` for time `t = π/ω` maps `|ψ⟩` to a state that still gives the same measurement probabilities.

**Solution**:

**(a) Normalization**:
$$\langle\psi|\psi\rangle = \frac{1}{2}(\langle 0| - i\langle 1|)(|0\rangle + i|1\rangle) = \frac{1}{2}(1 + (-i)(i)) = \frac{1}{2}(1 + 1) = 1 \checkmark$$

**(b) Measurement probabilities**:
- `p(0) = |α|² = |1/√2|² = 1/2`
- `p(1) = |β|² = |i/√2|² = |i|²/2 = 1/2`

**(c) Expectation value of Z**:
$$\langle Z \rangle = \langle\psi|Z|\psi\rangle = \frac{1}{2}(\langle 0| - i\langle 1|)\begin{pmatrix}1&0\\0&-1\end{pmatrix}\begin{pmatrix}1\\i\end{pmatrix}$$
$$= \frac{1}{2}(\langle 0| - i\langle 1|)\begin{pmatrix}1\\-i\end{pmatrix} = \frac{1}{2}(1 - i(-i)) = \frac{1}{2}(1 - 1) = 0$$

Alternatively: `⟨Z⟩ = p(0)·(+1) + p(1)·(-1) = 1/2 - 1/2 = 0`. The two calculations agree, as they must.

**(d) Time evolution**:

The Hamiltonian `H = ωZ/2` has eigenvalues `±ω/2`. The time evolution operator:
$$U(t) = e^{-iHt/\hbar} = e^{-i\omega Zt/2\hbar}$$

Using the spectral decomposition `Z = |0⟩⟨0| - |1⟩⟨1|`:
$$U(t) = e^{-i\omega t/2\hbar}|0\rangle\langle 0| + e^{i\omega t/2\hbar}|1\rangle\langle 1| = \begin{pmatrix}e^{-i\omega t/2\hbar} & 0 \\ 0 & e^{i\omega t/2\hbar}\end{pmatrix}$$

At `t = π/ω` (setting `ℏ = 1`):
$$U(\pi/\omega) = \begin{pmatrix}e^{-i\pi/2} & 0 \\ 0 & e^{i\pi/2}\end{pmatrix} = \begin{pmatrix}-i & 0 \\ 0 & i\end{pmatrix}$$

Applied to `|ψ⟩`:
$$U|\psi\rangle = \frac{1}{\sqrt{2}}\begin{pmatrix}-i & 0 \\ 0 & i\end{pmatrix}\begin{pmatrix}1 \\ i\end{pmatrix} = \frac{1}{\sqrt{2}}\begin{pmatrix}-i \\ i^2\end{pmatrix} = \frac{1}{\sqrt{2}}\begin{pmatrix}-i \\ -1\end{pmatrix} = -i\cdot\frac{1}{\sqrt{2}}\begin{pmatrix}1 \\ -i\end{pmatrix}$$

This is `(-i)(|0⟩ - i|1⟩)/√2`. The global factor `-i = e^{-iπ/2}` is a global phase and is unobservable. The measurement probabilities are `|1/√2|² = 1/2` for each outcome — identical to the original state. But note: `|ψ'⟩ = (|0⟩ - i|1⟩)/√2 ≠ |ψ⟩` up to global phase. The relative phase has changed from `+i` to `-i`. This state would give **different** results when measured in the X or Y basis.

## Summary

- **Postulate 1**: States are unit vectors in a complex Hilbert space; physical state space is the projective Hilbert space
- **Postulate 2**: Closed system evolution is unitary; the generator of evolution is the Hermitian Hamiltonian; quantum gates are unitary operators
- **Postulate 3**: Measurement outcomes have probabilities given by the Born rule `p(m) = ⟨ψ|Mₘ†Mₘ|ψ⟩`; post-measurement state is the renormalized projected state; the Born rule is a postulate, not a theorem
- **Postulate 4**: Composite system state space is the tensor product of component spaces; this enables entanglement
- Unitarity (Postulate 2) ensures reversibility and probability conservation
- The tension between unitary evolution and state collapse (Postulate 3) is the measurement problem — computationally irrelevant but philosophically deep
- All quantum algorithms are derivable from these four postulates applied to specific circuits and measurement schemes

## Exercises

**Exercise 1**: The unnormalized vector `2|0⟩ + (1+i)|1⟩` is proposed as a qubit state. Normalize it (Postulate 1) and compute the computational-basis measurement probabilities (Postulate 3).

<details><summary>Solution</summary>

Norm squared: `|2|² + |1+i|² = 4 + 2 = 6`. The normalized state is

`|ψ⟩ = (2|0⟩ + (1+i)|1⟩)/√6`

Probabilities: `p(0) = 4/6 = 2/3` and `p(1) = 2/6 = 1/3`. Check: `2/3 + 1/3 = 1` ✓.

</details>

**Exercise 2**: A qubit evolves under the Hamiltonian `H = X` (setting `ℏ = 1`). Show that `U(t) = e^{-iXt} = cos(t)I - i sin(t)X`, and compute the probability of measuring outcome 1 at time `t` if the qubit starts in `|0⟩`. What happens at `t = π/2`?

<details><summary>Solution</summary>

Since `X² = I`, the exponential series splits into even and odd powers:

`e^{-iXt} = Σₙ (-it)ⁿXⁿ/n! = (Σ even)I + (Σ odd)X = cos(t)I - i sin(t)X`

Applied to `|0⟩`: `U(t)|0⟩ = cos(t)|0⟩ - i sin(t)|1⟩`.

By the Born rule: `p(1) = |-i sin t|² = sin²t`. The qubit oscillates between `|0⟩` and `|1⟩` — a **Rabi oscillation**. At `t = π/2`: `U = -iX` and `p(1) = 1` — the qubit has flipped with certainty (the global phase `-i` is unobservable).

</details>

**Exercise 3**: Verify that the operators `M₀ = |0⟩⟨0| + (1/√2)|1⟩⟨1|` and `M₁ = (1/√2)|1⟩⟨1|` satisfy the completeness condition of Postulate 3. For the input state `|+⟩ = (|0⟩+|1⟩)/√2`, compute the outcome probabilities and the post-measurement state after outcome 0.

<details><summary>Solution</summary>

Completeness: `M₀†M₀ = |0⟩⟨0| + ½|1⟩⟨1|` and `M₁†M₁ = ½|1⟩⟨1|`. Their sum is `|0⟩⟨0| + |1⟩⟨1| = I` ✓.

Probabilities for `|+⟩`:

`p(0) = ⟨+|M₀†M₀|+⟩ = ½·1 + ½·½ = 3/4`, `p(1) = ⟨+|M₁†M₁|+⟩ = ½·½ = 1/4` (sum is 1 ✓)

Post-measurement state after outcome 0:

`M₀|+⟩ = (|0⟩ + (1/√2)|1⟩)/√2`, so `|ψ₀⟩ = M₀|+⟩/√(3/4) = (√2|0⟩ + |1⟩)/√3`

Note the state is disturbed (no longer `|+⟩`) but not fully collapsed — this is a **weak measurement**: outcome 0 only partially distinguishes the basis states, so the superposition partially survives.

</details>

**Exercise 4**: Two qubits are prepared in the product state `|ψ⟩ = |+⟩ ⊗ |1⟩` (Postulate 4). Show that measuring qubit 2 in the computational basis gives outcome 1 with certainty and leaves qubit 1 in `|+⟩` — i.e., measuring one factor of a product state does not disturb the other.

<details><summary>Solution</summary>

Expand: `|ψ⟩ = (|01⟩ + |11⟩)/√2`. The measurement of qubit 2 uses projectors `P₀ = I⊗|0⟩⟨0|` and `P₁ = I⊗|1⟩⟨1|`.

`p(1) = ⟨ψ|P₁|ψ⟩ = ½ + ½ = 1` and `p(0) = 0` — outcome 1 is certain.

Post-measurement state: `P₁|ψ⟩/√p(1) = (|01⟩+|11⟩)/√2 = |+⟩⊗|1⟩` — unchanged. Because the state factorizes, the measurement of qubit 2 leaves qubit 1's state exactly `|+⟩`; contrast this with an entangled state like `(|00⟩+|11⟩)/√2`, where measuring qubit 2 collapses qubit 1 as well.

</details>

## Further Reading

1. **Nielsen & Chuang**, *Quantum Computation and Quantum Information*, §2.2 — definitive presentation of the postulates; §2.2.3 discusses the connection between general and projective measurements
2. **Preskill**, *Lecture Notes for Physics 229*, Chapter 2 — excellent discussion of why the postulates take the form they do; §2.1 motivates Hilbert space from scratch
3. **Peres**, *Quantum Theory: Concepts and Methods* (Springer) — careful treatment of the postulates with emphasis on operational meaning and measurement theory
4. **Aaronson**, *Quantum Computing Since Democritus* (Cambridge) — Chapter 9 discusses the measurement problem and interpretations from a theoretical computer scientist's perspective
5. **Zurek**, "Decoherence, Einselection, and the Quantum Origins of the Classical" (Reviews of Modern Physics, 2003) — shows how classical behavior and the preferred basis for measurement emerge from entanglement with the environment (einselection)
