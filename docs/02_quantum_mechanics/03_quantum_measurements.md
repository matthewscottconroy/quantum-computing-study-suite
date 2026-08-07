# Quantum Measurements

> **Prerequisites**: 02_quantum_mechanics/01_postulates_of_quantum_mechanics.md, 02_qubits_and_the_bloch_sphere.md, 01_linear_algebra.md (spectral theorem, operators)  
> **Connects to**: Quantum algorithms (measurement extracts computation results), entanglement and nonlocality (measuring entangled systems), quantum error correction (syndrome measurement)

## Overview

Measurement is where quantum mechanics becomes strange. Until a measurement is performed, a quantum system can exist in a superposition of many possible outcomes. The act of measurement irreversibly picks one outcome, with probability given by the Born rule, and collapses the state to the measured eigenstate. This is fundamentally different from classical measurement, which we imagine merely reads off a pre-existing property without disturbing it.

For quantum computing, measurement is both a tool and an obstacle. It is a tool because it extracts classical information from quantum states — the entire output of a quantum computation is obtained by measuring the final state. It is an obstacle because it is irreversible and disturbs the state: measuring a qubit while the computation is still running destroys the coherence needed for the algorithm to work.

This chapter develops the full measurement formalism in four stages. We begin with projective measurements (the special case most commonly used in practice), then develop the general POVM (Positive Operator Valued Measure) framework, then derive the Heisenberg uncertainty principle from the measurement formalism, and finally discuss quantum non-demolition measurements — measurements that extract information without fully collapsing the state.

## Projective Measurements

### Definition and Born Rule

A **projective measurement** is described by an observable: a Hermitian operator `M` with spectral decomposition:

$$M = \sum_m m P_m$$

where the `{m}` are distinct real eigenvalues and `{Pₘ}` are the corresponding orthogonal projectors satisfying:
- `PₘPₘ' = δₘₘ' Pₘ` (orthogonality)
- `Σₘ Pₘ = I` (completeness)
- `Pₘ† = Pₘ` (Hermitian)
- `Pₘ² = Pₘ` (idempotent)

For a system in state `|ψ⟩`, measuring `M` gives:
- **Outcome `m`** with probability `p(m) = ⟨ψ|Pₘ|ψ⟩ = ‖Pₘ|ψ⟩‖²`
- **Post-measurement state**: `|ψₘ⟩ = Pₘ|ψ⟩/√p(m)` (the state collapses to the eigenspace of the measured eigenvalue)

The **expectation value** is:

$$\langle M \rangle = \sum_m m\, p(m) = \langle\psi|M|\psi\rangle$$

The **variance** is:

$$(\Delta M)^2 = \langle M^2\rangle - \langle M\rangle^2 = \langle\psi|M^2|\psi\rangle - \langle\psi|M|\psi\rangle^2$$

For a pure state that is an eigenstate `|m⟩` of `M`, the variance is zero: the measurement is deterministic. For a superposition, the variance is positive: outcomes are genuinely random.

### Computational Basis Measurement

The most commonly used measurement in quantum computing is the **standard basis measurement**: measuring the observable `Z = |0⟩⟨0| - |1⟩⟨1|` on a qubit.

For `|ψ⟩ = α|0⟩ + β|1⟩`:

$$P_0 = |0\rangle\langle 0|, \quad P_1 = |1\rangle\langle 1|$$
$$p(0) = |\alpha|^2, \quad p(1) = |\beta|^2$$

After measuring outcome 0: the state becomes `|0⟩`. After outcome 1: `|1⟩`.

For multi-qubit registers, measuring all `n` qubits gives outcome `x ∈ {0,1}ⁿ` with probability `|⟨x|ψ⟩|²`, where `|x⟩` is the computational basis state corresponding to bit string `x`. The result is a **sample** from the probability distribution defined by `{|⟨x|ψ⟩|²}`.

**The fundamental sampling limitation**: A quantum computation outputs a sample from a probability distribution. To estimate the full distribution, one must run the computation many times (hundreds to thousands of shots). This is why quantum speedup depends on extracting useful information from just one (or few) samples.

### Measurement in Other Bases

We can measure in any orthonormal basis `{|b₀⟩, |b₁⟩, ...}` by first applying the unitary transformation `V` that maps `{|bᵢ⟩}` to `{|i⟩}`, then measuring in the standard basis.

**Example**: To measure in the Hadamard (X) basis `{|+⟩, |−⟩}`, apply `H` then measure in the Z basis. For state `|ψ⟩`:

$$p(+) = |\langle +|\psi\rangle|^2, \quad p(-) = |\langle -|\psi\rangle|^2$$

This is equivalent to measuring the observable `X = |+⟩⟨+| - |−⟩⟨−|`.

## The POVM Formalism

### Why Go Beyond Projective Measurements

Projective measurements are idealized. In practice, measuring devices are imperfect, and we often want to perform measurements that:
1. Do not have orthogonal outcomes (e.g., "trine" measurements with three outcomes, none orthogonal)
2. Arise from performing projective measurements on a larger system (system + ancilla)
3. Have outcomes that occur probabilistically based on imperfect detector efficiency

The **POVM** (Positive Operator Valued Measure) formalism encompasses all physically realizable measurements.

### Definition

A **POVM** is a set of positive semidefinite operators `{Eₘ}` (called **POVM elements** or **effects**) satisfying:

$$\sum_m E_m = I, \quad E_m \geq 0$$

For system in state `|ψ⟩` (or density matrix `ρ`), the probability of outcome `m` is:

$$p(m) = \langle\psi|E_m|\psi\rangle = \text{Tr}(E_m |\psi\rangle\langle\psi|) = \text{Tr}(E_m \rho)$$

Unlike projective measurements, POVM elements need not be projectors (`Eₘ² ≠ Eₘ` in general) and need not be mutually orthogonal (`EₘEₘ' ≠ 0`).

### Connection to Projective Measurements

Every POVM can be realized as a projective measurement on a larger system (Naimark's dilation theorem):

**Naimark's theorem**: For any POVM `{Eₘ}` on `ℋ`, there exists a larger Hilbert space `ℋ_extended = ℋ ⊗ ℋ_ancilla`, a state `|0⟩_ancilla` for the ancilla, a unitary `U` on `ℋ_extended`, and an orthonormal basis `{|mₙ⟩}` for `ℋ_ancilla` such that:

$$p(m) = \|( I \otimes \langle m_n|) U (|\psi\rangle \otimes |0\rangle_\text{anc})\|^2$$

In words: prepare an ancilla, apply a unitary to system+ancilla, then measure the ancilla projectively. The resulting POVM on the system is `Eₘ = ⟨0|_anc U†(I ⊗ |mₙ⟩⟨mₙ|)U|0⟩_anc`.

This result is conceptually important: POVMs are not a new type of measurement, they are projective measurements on larger systems. But they are practically useful because they describe the effective measurement on the system alone, without explicitly modeling the ancilla.

### Kraus Operators

A more general description of measurement — that also specifies the post-measurement state — uses **Kraus operators** `{Mₘ}` (also called measurement operators):

$$E_m = M_m^\dagger M_m, \quad \sum_m M_m^\dagger M_m = I$$

The post-measurement state after outcome `m` is:

$$\rho_m = \frac{M_m \rho M_m^\dagger}{p(m)}, \quad p(m) = \text{Tr}(M_m^\dagger M_m \rho)$$

For projective measurements: `Mₘ = Pₘ` and `Eₘ = Pₘ² = Pₘ`.

**Unambiguous state discrimination** is an important POVM application. Given two non-orthogonal states `|ψ₁⟩` and `|ψ₂⟩`, no projective measurement can distinguish them with certainty. But a POVM with three outcomes can either identify the state unambiguously or return "inconclusive" — never making an error, at the cost of sometimes failing to identify.

## The Heisenberg Uncertainty Principle

### Derivation from Measurement Theory

The **Robertson uncertainty relation** states: for any two observables `A` and `B` and any state `|ψ⟩`:

$$\Delta A \cdot \Delta B \geq \frac{1}{2}|\langle [A, B]\rangle|$$

where `ΔA = √(⟨A²⟩ - ⟨A⟩²)` is the standard deviation and `[A,B] = AB - BA` is the commutator.

**Proof**: Define `|a⟩ = (A - ⟨A⟩)|ψ⟩` and `|b⟩ = (B - ⟨B⟩)|ψ⟩`. Then:
- `‖|a⟩‖² = ΔA²` and `‖|b⟩‖² = ΔB²`
- By Cauchy-Schwarz: `ΔA² · ΔB² ≥ |⟨a|b⟩|²`
- `⟨a|b⟩ = ⟨ψ|(A-⟨A⟩)(B-⟨B⟩)|ψ⟩ = ⟨AB⟩ - ⟨A⟩⟨B⟩`
- Writing `⟨a|b⟩ = ½⟨[A,B]⟩ + ½⟨{A,B}⟩ - ⟨A⟩⟨B⟩` (where `{A,B} = AB+BA`)
- `|⟨a|b⟩|² ≥ (Im⟨a|b⟩)² = ¼|⟨[A,B]⟩|²`

Therefore `ΔA · ΔB ≥ ½|⟨[A,B]⟩|`. QED.

### Application to Position and Momentum

For position `X̂` and momentum `P̂` in one dimension: `[X̂, P̂] = iℏI`, so:

$$\Delta X \cdot \Delta P \geq \frac{\hbar}{2}$$

This is Heisenberg's original uncertainty principle. In quantum computing, the analogous relation for qubits is:

$$\Delta X \cdot \Delta Z \geq \frac{1}{2}|\langle Y\rangle|$$

(using `[X,Z] = -2iY`).

### Physical Interpretation

The uncertainty principle is sometimes stated as "measuring A disturbs B." This is the **disturbance interpretation**, but it is more subtle than a simple mechanical disturbance. The Robertson relation is a statement about **state preparation**, not about the effect of one measurement on another:

- In a state where `ΔA = 0` (an eigenstate of `A`), we necessarily have `⟨[A,B]⟩ = ⟨ψ|[A,B]|ψ⟩ ≠ 0` in general, which forces `ΔB > 0`
- You cannot **prepare** a state that simultaneously has definite values of two non-commuting observables

The measurement disturbance interpretation is captured instead by the **Ozawa uncertainty relation** and the **Kennard inequality**, which more precisely quantify how measuring `A` affects subsequent measurements of `B`.

### Commuting Observables

If `[A,B] = 0`, then `A` and `B` can be **simultaneously diagonalized** (have a common eigenbasis), and `ΔA · ΔB ≥ 0` — no lower bound from the commutator. You can prepare states with definite values of both `A` and `B` simultaneously.

For quantum computing: measurements in the same basis (e.g., all Z measurements) commute and can be performed in any order. Measurements in different bases (e.g., X and Z) do not commute and measuring one disturbs the other.

## Measurement Collapse and Its Consequences

### Why Collapse Is Not Reversible

Postulate 2 says evolution is unitary (reversible). Measurement collapse is not unitary and thus is not reversible. Why not?

The collapse `|ψ⟩ → Pₘ|ψ⟩/‖Pₘ|ψ⟩‖` cannot be the action of any unitary operator because:
- Unitary operators are injective (one-to-one); collapse is many-to-one (all states in the eigenspace collapse to the same subspace)
- Unitary evolution is reversible; knowing the post-collapse state `|ψₘ⟩` does not let you recover `|ψ⟩`

The irreversibility of measurement is why quantum circuits must be designed carefully: **you cannot measure a qubit mid-circuit and hope to continue using it in superposition**. Once measured, the qubit is in a definite classical state.

### Deferred Measurement Principle

An important circuit identity: **measurement at the end of a circuit is equivalent to measurement at any earlier point followed by classically controlled gates**.

Formally: any quantum circuit with mid-circuit measurements can be transformed into a circuit where all measurements occur at the end, by replacing post-measurement conditional gates with coherent controlled operations. The two circuits produce identical output distributions.

This principle justifies the standard quantum algorithm structure: apply all quantum gates, then measure at the end.

### Quantum Non-Demolition Measurements

A **quantum non-demolition (QND) measurement** measures an observable `A` without changing the value of `A` in subsequent measurements. That is, the measurement does not disturb the eigenvalue of `A`, even if it does disturb other properties of the system.

Formally: if `|ψ₀⟩` is an eigenstate of `A` with eigenvalue `a`, then after a QND measurement the system is still in an eigenstate of `A` with eigenvalue `a`. This requires measuring without coupling to degrees of freedom that would disturb the `A` eigenvalue.

**Example in quantum error correction**: Syndrome measurements are QND measurements of stabilizer operators. They reveal which type of error occurred without collapsing the encoded logical state. This is the key insight enabling quantum error correction: we can measure without destroying the quantum information we are trying to protect, because we measure an **error syndrome** (a property of the error) not the logical information itself.

**Contrast with demolition measurement**: Photon detection (measuring photon number) is demolition — the photon is absorbed and destroyed. Cavity QED techniques can measure whether a photon is present without absorbing it (QND photon counting), which is an important experimental advance.

## Key Formulas

**Born rule (projective)**:
$$p(m) = \langle\psi|P_m|\psi\rangle = \|P_m|\psi\rangle\|^2$$

**Post-measurement state (projective)**:
$$|\psi_m\rangle = \frac{P_m|\psi\rangle}{\sqrt{p(m)}}$$

**Expectation value**:
$$\langle M \rangle = \langle\psi|M|\psi\rangle = \sum_m m\, p(m)$$

**Variance**:
$$(\Delta M)^2 = \langle M^2\rangle - \langle M\rangle^2$$

**POVM probabilities**:
$$p(m) = \text{Tr}(E_m\rho), \quad E_m \geq 0, \quad \sum_m E_m = I$$

**Robertson uncertainty relation**:
$$\Delta A \cdot \Delta B \geq \frac{1}{2}|\langle [A,B]\rangle|$$

**Heisenberg (position-momentum)**:
$$\Delta X \cdot \Delta P \geq \frac{\hbar}{2}$$

## Worked Example

**Problem**: A qubit is in state `|ψ⟩ = (2|0⟩ + i|1⟩)/√5`. 

(a) Measure observable `Z`. Find probabilities, expectation value, variance.  
(b) After obtaining outcome 0, the qubit is re-measured in the X basis `{|+⟩,|−⟩}`. Find probabilities.  
(c) Verify the uncertainty relation `ΔX · ΔZ ≥ ½|⟨Y⟩|` for the original state.

**Solution**:

**(a) Measuring Z on `|ψ⟩`**:

Probabilities:
$$p(0) = |\langle 0|\psi\rangle|^2 = |2/\sqrt{5}|^2 = 4/5$$
$$p(1) = |\langle 1|\psi\rangle|^2 = |i/\sqrt{5}|^2 = 1/5$$

Expectation value:
$$\langle Z\rangle = p(0)\cdot(+1) + p(1)\cdot(-1) = 4/5 - 1/5 = 3/5$$

Verify via formula: `⟨ψ|Z|ψ⟩ = (1/5)(2, -i)(1,0;0,-1)(2,i)ᵀ = (1/5)(2,-i)(2,-i)ᵀ = (1/5)(4+1) = 1`. Wait — let me recompute:
$$\langle Z\rangle = \frac{1}{5}(2^*,\, (-i)^*)\begin{pmatrix}1&0\\0&-1\end{pmatrix}\begin{pmatrix}2\\i\end{pmatrix} = \frac{1}{5}(2,\,i)\begin{pmatrix}2\\-i\end{pmatrix} = \frac{1}{5}(4 + i(-i)) = \frac{1}{5}(4+1) = 1$$

Hmm, that gives 1. Let me recheck: `(2, -i^*)` — conjugate of `i` is `-i`, so:
$$\langle Z\rangle = \frac{1}{5}(2,\, -i)\begin{pmatrix}2\\-i\end{pmatrix} = \frac{1}{5}(4 + (-i)(-i)) = \frac{1}{5}(4 - 1) = \frac{3}{5} \checkmark$$

Second moment: `⟨Z²⟩ = ⟨ψ|Z²|ψ⟩ = ⟨ψ|I|ψ⟩ = 1` (since `Z² = I`).

Variance: `(ΔZ)² = ⟨Z²⟩ - ⟨Z⟩² = 1 - 9/25 = 16/25`. So `ΔZ = 4/5`.

**(b) After measuring 0, qubit is in `|0⟩`**:

Measuring X on `|0⟩ = (|+⟩+|−⟩)/√2`:
$$p(+) = |\langle +|0\rangle|^2 = |1/\sqrt{2}|^2 = 1/2$$
$$p(-) = |\langle -|0\rangle|^2 = 1/2$$

The collapsed state `|0⟩` has maximum uncertainty in X — the measurement in Z basis has indeed disturbed the X outcome.

**(c) Uncertainty relation**:

Compute `⟨X⟩` for `|ψ⟩`:
$$\langle X\rangle = \frac{1}{5}(2,\,-i)\begin{pmatrix}0&1\\1&0\end{pmatrix}\begin{pmatrix}2\\i\end{pmatrix} = \frac{1}{5}(2,\,-i)\begin{pmatrix}i\\2\end{pmatrix} = \frac{1}{5}(2i - 2i) = 0$$

`⟨X²⟩ = 1` (since `X² = I`), so `ΔX = √(1-0) = 1`.

Compute `⟨Y⟩`:
$$\langle Y\rangle = \frac{1}{5}(2,\,-i)\begin{pmatrix}0&-i\\i&0\end{pmatrix}\begin{pmatrix}2\\i\end{pmatrix} = \frac{1}{5}(2,\,-i)\begin{pmatrix}-i^2\\2i\end{pmatrix} = \frac{1}{5}(2,\,-i)\begin{pmatrix}1\\2i\end{pmatrix}$$
$$= \frac{1}{5}(2 + (-i)(2i)) = \frac{1}{5}(2 + 2) = \frac{4}{5}$$

Check: `[X,Z] = XZ - ZX = -iY - iY`... Let me use `[X,Z] = -2iY` (from Chapter 1.1):

$$\Delta X \cdot \Delta Z \geq \frac{1}{2}|\langle -2iY\rangle| / (1) = |\langle Y\rangle| = 4/5$$

Wait, the formula is `ΔA·ΔB ≥ ½|⟨[A,B]⟩|` with `[X,Z] = -2iY`:
$$\Delta X \cdot \Delta Z \geq \frac{1}{2}|\langle -2iY\rangle| = |-i|\cdot|\langle Y\rangle| = \frac{4}{5}$$

LHS: `ΔX · ΔZ = 1 · (4/5) = 4/5`.  
RHS: `4/5`.

The uncertainty relation is **saturated** (equality holds). This state is a **minimum uncertainty state** for the X-Z pair.

## Summary

- **Projective measurements** use spectral decomposition `M = ΣₘmPₘ`; probability `p(m) = ⟨ψ|Pₘ|ψ⟩`; post-measurement state `Pₘ|ψ⟩/√p(m)`
- The **expectation value** `⟨M⟩ = ⟨ψ|M|ψ⟩` and variance `(ΔM)² = ⟨M²⟩ - ⟨M⟩²` quantify measurement statistics
- **POVMs** generalize projective measurements; elements `Eₘ ≥ 0` with `ΣₘEₘ = I`; realized as projective measurements on system+ancilla (Naimark's theorem)
- The **Robertson uncertainty principle** `ΔA·ΔB ≥ ½|⟨[A,B]⟩|` prohibits joint precision of non-commuting observables
- **Measurement collapse** is irreversible and non-unitary; the deferred measurement principle shows mid-circuit measurements can be moved to the end
- **QND measurements** extract information without disturbing the measured eigenvalue; used in quantum error correction for syndrome measurement
- Quantum computing output is fundamentally **sampling** from a probability distribution — statistical repetition is required to estimate the distribution

## Further Reading

1. **Nielsen & Chuang**, §2.2.3–2.2.6 — projective and POVM measurements, measurement statistics, Kraus operators
2. **Helstrom**, *Quantum Detection and Estimation Theory* (Academic Press, 1976) — the foundational work on optimal quantum measurement; introduces POVM formalism
3. **Wiseman & Milburn**, *Quantum Measurement and Control* (Cambridge) — modern treatment including continuous measurements, QND, and measurement-based feedback; Chapter 1 is an excellent introduction
4. **Busch, Grabowski & Lahti**, *Operational Quantum Physics* (Springer) — rigorous mathematical treatment of POVMs and quantum observables
5. **Ozawa**, "Universally valid reformulation of the Heisenberg uncertainty principle on noise and disturbance in measurement" (Physical Review A, 2003) — derives the correct measurement disturbance version of the uncertainty principle; corrects common misconceptions
