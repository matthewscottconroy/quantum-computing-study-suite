# Density Matrices and Open Systems

> **Prerequisites**: 02_quantum_mechanics/01_postulates_of_quantum_mechanics.md, 03_tensor_products_and_multipartite_systems.md, 04_entanglement_and_nonlocality.md  
> **Connects to**: Quantum error correction, decoherence and noise models, quantum channels in quantum information, POVM measurements, mixed-state quantum computation

## Overview

The formalism developed so far describes **pure states** — quantum systems we know completely, represented by a single unit vector `|ψ⟩`. But in practice, we rarely have this luxury. A qubit interacts with its environment (electromagnetic fluctuations, vibrations, stray fields), entangling the two systems. If we track only the qubit, ignoring the environment, its state cannot be described by any pure state. It is a **mixed state** — a statistical ensemble of pure states.

The correct mathematical object for describing mixed states is the **density matrix** (also called density operator). Density matrices generalize pure state vectors in a fundamental way: they represent both quantum uncertainty (superposition) and classical uncertainty (ignorance) within a single formalism. The price of this generality is additional mathematical structure, but the payoff is a complete framework for describing open quantum systems — systems coupled to an environment.

This chapter develops the density matrix formalism, characterizes the class of physically allowed quantum operations (completely positive trace-preserving maps), and describes the key noise channels that affect real quantum hardware. Understanding decoherence — the process by which quantum coherence is destroyed through environmental interaction — is essential for understanding why quantum computers are hard to build and how quantum error correction combats it.

## Pure States and Mixed States

### The Density Matrix of a Pure State

For a pure state `|ψ⟩`, the **density matrix** is the rank-1 projector:

$$\rho = |\psi\rangle\langle\psi|$$

This is a `d × d` Hermitian matrix (where `d` is the Hilbert space dimension). All expectation values and probabilities can be expressed in terms of `ρ`:

$$\langle A \rangle = \text{Tr}(A\rho) = \langle\psi|A|\psi\rangle$$
$$p(m) = \text{Tr}(P_m\rho) = \langle\psi|P_m|\psi\rangle$$

The trace formulation `Tr(Aρ)` works for any state, pure or mixed.

**Characterizing pure states**: A density matrix `ρ` describes a pure state iff `Tr(ρ²) = 1` (equivalently, `ρ² = ρ`, so `ρ` is a projector). For any pure state `|ψ⟩⟨ψ|`:

$$\text{Tr}(\rho^2) = \text{Tr}(|\psi\rangle\langle\psi|\psi\rangle\langle\psi|) = \text{Tr}(|\psi\rangle\langle\psi|) = 1$$

### Mixed States

A **mixed state** arises when we have classical uncertainty about which pure state the system is in. If the system is in state `|ψᵢ⟩` with probability `pᵢ` (classical probabilities, `Σᵢ pᵢ = 1`), the density matrix is:

$$\rho = \sum_i p_i |\psi_i\rangle\langle\psi_i|$$

This is a convex combination of pure state density matrices. For this ensemble, observable `A` has expectation value:

$$\langle A\rangle = \sum_i p_i \langle\psi_i|A|\psi_i\rangle = \sum_i p_i \text{Tr}(A|\psi_i\rangle\langle\psi_i|) = \text{Tr}(A\rho)$$

The same formula as before — the density matrix captures all measurable information regardless of the source of uncertainty.

### Properties of Density Matrices

A Hermitian matrix `ρ` is a valid density matrix iff:

1. **Hermitian**: `ρ† = ρ`
2. **Positive semidefinite**: `ρ ≥ 0` (all eigenvalues `≥ 0`)
3. **Unit trace**: `Tr(ρ) = 1`

These three conditions are necessary and sufficient. Conversely, any matrix satisfying them can be prepared as a quantum state.

**Eigendecomposition**: Since `ρ` is Hermitian and PSD, it has eigendecomposition:

$$\rho = \sum_i \lambda_i |i\rangle\langle i|, \quad \lambda_i \geq 0, \quad \sum_i \lambda_i = 1$$

The eigenvalues `{λᵢ}` form a probability distribution. This is the unique **diagonal ensemble** — the most natural way to read `ρ` as a probability distribution, in the eigenbasis.

**Purity** `Tr(ρ²) = Σᵢ λᵢ²` satisfies `1/d ≤ Tr(ρ²) ≤ 1`:
- `Tr(ρ²) = 1`: pure state
- `Tr(ρ²) = 1/d`: maximally mixed state `ρ = I/d`

**Von Neumann entropy** `S(ρ) = -Tr(ρ log ρ) = -Σᵢ λᵢ log λᵢ` satisfies:
- `S(ρ) = 0`: pure state
- `S(ρ) = log d`: maximally mixed state
- `S(ρ) ≥ 0` always

### Important Examples

**Single qubit — Bloch sphere connection**:
$$\rho = \frac{I + \mathbf{r}\cdot\boldsymbol{\sigma}}{2}, \quad \mathbf{r} = (\langle X\rangle, \langle Y\rangle, \langle Z\rangle)$$

Pure states: `|r| = 1` (surface of sphere). Mixed states: `|r| < 1` (interior). Maximally mixed: `r = 0`.

**The maximally mixed state** `ρ = I/d`:
- All computational basis outcomes equally likely (probability `1/d`)
- `Tr(ρ²) = 1/d` (minimum purity)
- This is the state of a qubit that has been completely decohered by noise

## Quantum Operations: CPTP Maps

### Motivation

The Schrödinger equation (`iℏ ∂ρ/∂t = [H, ρ]`) describes unitary evolution: `ρ(t) = U(t)ρ(0)U†(t)`. But a quantum system interacting with an environment undergoes **non-unitary** evolution from the system's perspective. What are the most general allowed evolutions?

**Definition**: A **quantum channel** (or **quantum operation**) is a map `ε: ρ → ε(ρ)` that is:
1. **Linear**: `ε(αρ + βσ) = αε(ρ) + βε(σ)`
2. **Trace-preserving**: `Tr(ε(ρ)) = 1` for all `ρ` with `Tr(ρ) = 1`
3. **Completely positive**: for any extension of the system by an ancilla, the map `ε ⊗ I_ancilla` is positive (maps positive matrices to positive matrices)

The complete positivity (CP) condition is the crucial one. Positivity alone is not sufficient — there exist positive maps that fail to be completely positive, and those maps do not correspond to physical operations. The transpose map `ρ → ρᵀ` is positive but not completely positive (applying it to half of a Bell state gives a matrix with a negative eigenvalue).

### Kraus Representation Theorem

**Theorem**: A map `ε` is completely positive and trace-preserving (CPTP) iff it has a **Kraus decomposition**:

$$\varepsilon(\rho) = \sum_k K_k \rho K_k^\dagger, \quad \sum_k K_k^\dagger K_k = I$$

The operators `{Kₖ}` are called **Kraus operators**. The trace-preservation condition `Σₖ Kₖ†Kₖ = I` ensures `Tr(ε(ρ)) = Tr(ρ) = 1`.

**Proof sketch (forward direction)**: If `ε` has a Kraus decomposition, it is clearly CPTP. The reverse direction (every CPTP map has Kraus operators) follows from the **Stinespring dilation**: any CPTP map arises from unitary evolution of system+environment followed by partial trace.

**Stinespring dilation**: For any CPTP map `ε` on system S, there exists an environment E in initial state `|0⟩_E` and a unitary `U_{SE}` such that:

$$\varepsilon(\rho_S) = \text{Tr}_E[U_{SE}(\rho_S \otimes |0\rangle\langle 0|_E)U_{SE}^\dagger]$$

The Kraus operators are `Kₖ = ⟨k|_E U_{SE}|0⟩_E` (the "matrix elements" of `U_{SE}` between environment basis states).

**Non-uniqueness**: The Kraus decomposition is not unique. If `{Kₖ}` is a Kraus representation, so is `{K̃ₖ = Σⱼ vₖⱼKⱼ}` for any unitary matrix `v`. The physical channel `ε` is unique; the Kraus operators are a convenient (non-unique) representation.

**Unitary evolution as a special case**: Pure unitary evolution `ε(ρ) = UρU†` is the Kraus decomposition with a single operator `K₁ = U`. Since `K₁†K₁ = U†U = I`, this satisfies the completeness condition.

## Key Noise Channels

### Bit Flip Channel

The **bit flip channel** flips the qubit (applies X) with probability `p`:

$$\varepsilon_\text{BF}(\rho) = (1-p)\rho + p X\rho X, \quad K_1 = \sqrt{1-p}\,I, \quad K_2 = \sqrt{p}\,X$$

Effect on Bloch vector: `(r_x, r_y, r_z) → (r_x, (1-2p)r_y, (1-2p)r_z)`. The X axis is preserved; Y and Z components are shrunk. At `p = 1/2`, all Y and Z coherence is destroyed.

### Phase Flip (Dephasing) Channel

The **phase flip channel** applies Z with probability `p`:

$$\varepsilon_\text{PF}(\rho) = (1-p)\rho + p Z\rho Z, \quad K_1 = \sqrt{1-p}\,I, \quad K_2 = \sqrt{p}\,Z$$

Effect on Bloch vector: `(r_x, r_y, r_z) → ((1-2p)r_x, (1-2p)r_y, r_z)`. The Z axis is preserved; X and Y components shrink. This is the **dephasing** channel: it destroys superpositions in the Z basis without flipping the qubit.

In matrix form, acting on `ρ = [[a,b],[c,d]]`:
$$\varepsilon_\text{PF}(\rho) = \begin{pmatrix}a & (1-2p)b \\ (1-2p)c & d\end{pmatrix}$$

The diagonal (populations) are unchanged; the off-diagonals (coherences) are suppressed by factor `(1-2p)`. This models the physically dominant noise in many systems (including superconducting qubits undergoing `T₂` dephasing).

### Depolarizing Channel

The **depolarizing channel** leaves the state alone with probability `1-p` and, with probability `p`, applies a uniformly random Pauli (I, X, Y, or Z, each with probability `p/4`):

$$\varepsilon_\text{dep}(\rho) = (1-p)\rho + \frac{p}{4}(I\rho I + X\rho X + Y\rho Y + Z\rho Z)$$

The key algebraic identity for qubits is:

$$X\rho X + Y\rho Y + Z\rho Z = 2I\,\text{Tr}(\rho) - \rho = 2I - \rho \quad \text{(for Tr}\,\rho = 1)$$

(Proof via the Bloch form: writing `ρ = (I + r·σ)/2`, conjugation by `X` flips the signs of `r_y` and `r_z`, conjugation by `Y` flips `r_x, r_z`, and conjugation by `Z` flips `r_x, r_y`. Summing the three conjugates, each `σᵢ` appears with coefficient `+1` once and `-1` twice, so the sum is `(3I - r·σ)/2 = 2I - (I + r·σ)/2 = 2I - ρ`.)

Substituting into the channel:

$$\varepsilon_\text{dep}(\rho) = (1-p)\rho + \frac{p}{4}\bigl(\rho + 2I - \rho\bigr) = (1-p)\rho + \frac{p}{2}I = (1-p)\rho + p\,\frac{I}{2}$$

So "apply a uniformly random Pauli with probability `p`" is exactly the same as "replace the state with the maximally mixed state `I/2` with probability `p`."

Effect on Bloch vector: `r → (1-p)r`. The Bloch vector shrinks uniformly toward the center, and at `p = 1` the state is maximally mixed.

**Alternative convention**: Some texts define the depolarizing channel as applying a *non-trivial* Pauli (X, Y, or Z, each with probability `p/3`) with total error probability `p`:

$$\varepsilon'_\text{dep}(\rho) = (1-p)\rho + \frac{p}{3}(X\rho X + Y\rho Y + Z\rho Z) = (1-p)\rho + \frac{p}{3}(2I - \rho) = \left(1 - \tfrac{4p}{3}\right)\rho + \frac{4p}{3}\cdot\frac{I}{2}$$

In this convention the Bloch vector scales as `r → (1 - 4p/3)r`, and the state becomes maximally mixed already at `p = 3/4` (a uniformly random Pauli, including I, corresponds to complete depolarization). The two conventions are related by `p_{\text{mixed}} = 4p_{\text{Pauli}}/3`; always check which one a paper uses before plugging in error rates.

### Amplitude Damping Channel

The **amplitude damping channel** models spontaneous emission: a qubit in state `|1⟩` decays to `|0⟩` with probability `γ` (related to `T₁` relaxation time):

$$K_0 = \begin{pmatrix}1&0\\0&\sqrt{1-\gamma}\end{pmatrix}, \quad K_1 = \begin{pmatrix}0&\sqrt{\gamma}\\0&0\end{pmatrix}$$

Acting on `ρ = [[a,b],[c,d]]`:
$$\varepsilon_\text{AD}(\rho) = K_0\rho K_0^\dagger + K_1\rho K_1^\dagger = \begin{pmatrix}a+\gamma d & \sqrt{1-\gamma}\,b \\ \sqrt{1-\gamma}\,c & (1-\gamma)d\end{pmatrix}$$

**Interpretation**: 
- Population `d = ⟨1|ρ|1⟩` decreases: `d → (1-γ)d`
- Population `a = ⟨0|ρ|0⟩` increases: `a → a + γd` (probability flows from `|1⟩` to `|0⟩`)
- Coherences shrink: `b → √(1-γ)b`
- At `γ = 1`, any state decays to `|0⟩⟨0|`

The amplitude damping channel has a fixed point `|0⟩⟨0|` rather than `I/2` — it models energy relaxation toward the ground state.

## Decoherence

### The Physical Picture

**Decoherence** is the process by which quantum coherence (off-diagonal elements of the density matrix) is destroyed through entanglement with the environment. It is the main obstacle to building large-scale quantum computers.

Consider a qubit initially in superposition `|ψ⟩ = (|0⟩+|1⟩)/√2` coupled to an environment `|E₀⟩`. After interaction:

$$\frac{|0\rangle+|1\rangle}{\sqrt{2}} \otimes |E_0\rangle \to \frac{|0\rangle|E_0\rangle + |1\rangle|E_1\rangle}{\sqrt{2}}$$

where `|E₀⟩` and `|E₁⟩` are the environment states correlated with qubit states `|0⟩` and `|1⟩`. The reduced state of the qubit is:

$$\rho_\text{qubit} = \text{Tr}_E\left[\frac{|0\rangle|E_0\rangle + |1\rangle|E_1\rangle}{\sqrt{2}}\cdot\text{h.c.}\right] = \frac{1}{2}\begin{pmatrix}1 & \langle E_1|E_0\rangle \\ \langle E_0|E_1\rangle & 1\end{pmatrix}$$

As the environment states become more orthogonal (`|⟨E₁|E₀⟩| → 0`), the off-diagonal coherences vanish. The qubit approaches the classical mixture `I/2`.

**The key insight**: Decoherence does not require any "observer" or "measurement device." Interaction with any macroscopic environment (with many degrees of freedom) effectively performs a measurement on the qubit, because the environment becomes entangled with the qubit and acts as a record of which state it was in.

### Decoherence Timescales

Two characteristic times govern qubit decoherence:

- **T₁ (energy relaxation time)**: Time for excited state `|1⟩` to decay to ground state `|0⟩`. Related to amplitude damping with `γ ≈ 1 - e^{-t/T₁}`.
- **T₂ (dephasing time)**: Time for off-diagonal coherences to vanish. `T₂ ≤ 2T₁` (fundamental bound). Related to phase damping.

**Physical values** (superconducting qubits, 2024):
- `T₁ ≈ 100-500 μs` (state of the art)
- `T₂ ≈ 100-300 μs`
- Gate time ≈ 10-100 ns
- Ratio (coherence time / gate time) ≈ 10⁴–10⁵ operations per qubit before significant decoherence

This ratio determines the **fault tolerance threshold**: the decoherence rate must be below a threshold (roughly `10⁻³–10⁻²` per gate) for quantum error correction to succeed.

## Key Formulas

**Density matrix of pure state**:
$$\rho = |\psi\rangle\langle\psi|, \quad \text{Tr}(\rho^2) = 1$$

**Density matrix of mixed state**:
$$\rho = \sum_i p_i|\psi_i\rangle\langle\psi_i|, \quad p_i \geq 0, \quad \sum_i p_i = 1$$

**Validity conditions**:
$$\rho^\dagger = \rho, \quad \rho \geq 0, \quad \text{Tr}(\rho) = 1$$

**Expectation value**:
$$\langle A\rangle = \text{Tr}(A\rho)$$

**Kraus representation**:
$$\varepsilon(\rho) = \sum_k K_k \rho K_k^\dagger, \quad \sum_k K_k^\dagger K_k = I$$

**Von Neumann entropy**:
$$S(\rho) = -\text{Tr}(\rho\log_2\rho) = -\sum_i \lambda_i \log_2 \lambda_i$$

**Purity**:
$$\text{Tr}(\rho^2) = \sum_i \lambda_i^2, \quad \frac{1}{d} \leq \text{Tr}(\rho^2) \leq 1$$

## Worked Example

**Problem**: A qubit starts in the pure state `|+⟩ = (|0⟩+|1⟩)/√2` and undergoes the phase damping channel with parameter `p`.

(a) Write the density matrix before and after.  
(b) Find the Bloch vector before and after.  
(c) At what value of `p` does the state become maximally mixed?  
(d) Compute the von Neumann entropy as a function of `p`.

**Solution**:

**(a) Density matrices**:

Before:
$$\rho_0 = |+\rangle\langle+| = \frac{1}{2}\begin{pmatrix}1&1\\1&1\end{pmatrix}$$

After phase damping `ε_PF(ρ) = (1-p)ρ + pZρZ`:

$$Z\rho_0 Z = \frac{1}{2}\begin{pmatrix}1&0\\0&-1\end{pmatrix}\begin{pmatrix}1&1\\1&1\end{pmatrix}\begin{pmatrix}1&0\\0&-1\end{pmatrix} = \frac{1}{2}\begin{pmatrix}1&-1\\-1&1\end{pmatrix}$$

$$\rho(p) = (1-p)\cdot\frac{1}{2}\begin{pmatrix}1&1\\1&1\end{pmatrix} + p\cdot\frac{1}{2}\begin{pmatrix}1&-1\\-1&1\end{pmatrix} = \frac{1}{2}\begin{pmatrix}1 & 1-2p \\ 1-2p & 1\end{pmatrix}$$

**(b) Bloch vectors**:

Before: `r = (1, 0, 0)` (the state `|+⟩` is on the +x axis of the Bloch sphere).

After: read the Bloch vector off the density matrix using `ρ = ½[[1+r_z, r_x - ir_y],[r_x + ir_y, 1-r_z]]`, i.e. `r_z = ρ_{00} - ρ_{11}`, `r_x = 2Re(ρ_{10})`, `r_y = 2Im(ρ_{10})`:
- `r_z = 1/2 - 1/2 = 0`
- `r_x = 2Re((1-2p)/2) = 1-2p`
- `r_y = 2Im((1-2p)/2) = 0`

After: `r = (1-2p, 0, 0)`. The Bloch vector shrinks along the x-axis.

**(c) Maximally mixed**:

The state becomes maximally mixed when `r = 0`, i.e., `1-2p = 0`, so `p = 1/2`.

At `p = 1/2`: `ρ(1/2) = ½ I = [[1/2, 0],[0, 1/2]]`. This is the maximally mixed state.

**(d) Von Neumann entropy**:

Eigenvalues of `ρ(p)` (a matrix with equal diagonal entries `1/2` and off-diagonal `(1-2p)/2`):
$$\lambda_\pm = \frac{1}{2} \pm \frac{|1-2p|}{2}$$

For `p ≤ 1/2`: `λ₊ = (2-2p)/2 = 1-p` and `λ₋ = p`.

Von Neumann entropy:
$$S(p) = -\lambda_+ \log_2 \lambda_+ - \lambda_- \log_2 \lambda_- = -((1-p)\log_2(1-p) + p\log_2 p) = H(p)$$

This is the **binary entropy function** `H(p)`.

- `S(0) = 0`: pure state (no phase damping)
- `S(1/2) = 1`: maximally mixed (maximum entropy)
- `S(1) = 0`: pure state `|−⟩` (the state has been unitarily rotated to `|−⟩`; at `p=1`, `ZρZ = |−⟩⟨−|` since `Z|+⟩ = |−⟩`)

The von Neumann entropy increases from 0 to 1 bit as the phase damping increases from 0 to 1/2, then decreases back to 0 at `p=1` — because at `p=1` the channel acts as the unitary `Z`, leaving a definite pure state again.

## Summary

- The **density matrix** `ρ = Σᵢ pᵢ|ψᵢ⟩⟨ψᵢ|` describes both pure and mixed states; characterization: `ρ† = ρ, ρ ≥ 0, Tr(ρ) = 1`
- **Pure states**: `Tr(ρ²) = 1`; **mixed states**: `Tr(ρ²) < 1`; **maximally mixed**: `ρ = I/d`
- **CPTP maps** are the most general allowed quantum operations; characterized by the Kraus representation `ε(ρ) = ΣₖKₖρKₖ†` with `ΣₖKₖ†Kₖ = I`
- Key noise channels: **bit flip** (X errors), **phase flip** (dephasing, Z errors), **depolarizing** (all errors equally), **amplitude damping** (energy relaxation `|1⟩→|0⟩`)
- **Decoherence** arises from entanglement with the environment, causing coherences (off-diagonal density matrix elements) to vanish
- **T₁** (energy relaxation) and **T₂** (dephasing) are the key timescales; current superconducting qubits achieve `T₁, T₂ ∼ 100μs` with gate times `∼ 10-100ns`
- The **von Neumann entropy** `S(ρ) = -Tr(ρ log ρ)` measures the degree of mixedness: 0 for pure, log d for maximally mixed

## Exercises

**Exercise 1**: Which of the following are valid density matrices? (a) `A = ½[[1,1],[1,1]]`, (b) `B = [[0.7, 0.3],[0.3, 0.3]]`, (c) `C = [[0.5, 0.6],[0.6, 0.5]]`. For the valid ones, decide whether they are pure or mixed.

<details><summary>Solution</summary>

All three are Hermitian with unit trace, so the question is positive semidefiniteness (both eigenvalues `≥ 0`). For a `2×2` Hermitian matrix, eigenvalues are `Tr/2 ± √((Tr/2 - d)² ... )` — simplest is to check the determinant (product of eigenvalues) and trace (sum).

**(a)** `det A = ¼(1·1 - 1·1) = 0`, `Tr A = 1`. Eigenvalues `{1, 0}` — valid, and since `A² = A` it is a **pure state**: `A = |+⟩⟨+|`.

**(b)** `det B = 0.21 - 0.09 = 0.12 > 0` and `Tr B = 1 > 0`, so both eigenvalues are positive (they are `≈ 0.861, 0.139`) — valid. `Tr(B²) = 0.861² + 0.139² ≈ 0.76 < 1`, so **mixed**.

**(c)** `det C = 0.25 - 0.36 = -0.11 < 0` — one eigenvalue is negative (`{1.1, -0.1}`). **Not a valid density matrix**: it would assign a negative probability to the `|−⟩` outcome of an X measurement.

</details>

**Exercise 2**: Show that the ensemble "`|0⟩` with probability 3/4, `|1⟩` with probability 1/4" and the ensemble "`|a⟩ = (√3|0⟩+|1⟩)/2` with probability 1/2, `|b⟩ = (√3|0⟩-|1⟩)/2` with probability 1/2" have the **same** density matrix. What does this imply physically?

<details><summary>Solution</summary>

First ensemble: `ρ₁ = ¾|0⟩⟨0| + ¼|1⟩⟨1| = [[3/4, 0],[0, 1/4]]`.

Second ensemble: `|a⟩⟨a| = ¼[[3, √3],[√3, 1]]` and `|b⟩⟨b| = ¼[[3, -√3],[-√3, 1]]`, so

`ρ₂ = ½(|a⟩⟨a| + |b⟩⟨b|) = ½·¼[[6, 0],[0, 2]] = [[3/4, 0],[0, 1/4]] = ρ₁` ✓

The off-diagonal terms cancel. Since all measurement statistics are functions of `ρ` alone (`p(m) = Tr(Eₘρ)`), **no experiment can distinguish which ensemble was prepared**. A density matrix does not carry a unique decomposition into pure states — classical ignorance about "which pure state we have" is not a physically meaningful question beyond `ρ` itself.

</details>

**Exercise 3**: Verify the identity `XρX + YρY + ZρZ = 2I - ρ` explicitly for `ρ = |0⟩⟨0|`, and then prove it for arbitrary single-qubit `ρ` with `Tr ρ = 1`.

<details><summary>Solution</summary>

For `ρ = |0⟩⟨0| = [[1,0],[0,0]]`:

- `X|0⟩⟨0|X = |1⟩⟨1|`
- `Y|0⟩⟨0|Y = (i|1⟩)(⟨1|(-i)) = |1⟩⟨1|`
- `Z|0⟩⟨0|Z = |0⟩⟨0|`

Sum: `2|1⟩⟨1| + |0⟩⟨0| = [[1,0],[0,2]]`. And `2I - ρ = [[2,0],[0,2]] - [[1,0],[0,0]] = [[1,0],[0,2]]` ✓.

General proof: write `ρ = (I + r_x X + r_y Y + r_z Z)/2`. Conjugating by a Pauli `σᵢ` leaves `I` and `σᵢ` fixed and negates the other two Paulis (since they anticommute with `σᵢ`). Summing over `i = x, y, z`: the `I` term contributes `3·(I/2)`, and each `σⱼ` term appears once with `+` and twice with `-`, contributing `-(r·σ)/2`. Total: `(3I - r·σ)/2 = 2I - (I + r·σ)/2 = 2I - ρ`. (For unnormalized `ρ`, the same computation gives `2I·Tr(ρ) - ρ`.)

</details>

**Exercise 4**: Apply the amplitude damping channel with `γ = 1/2` to the state `|+⟩⟨+|`. Compute the output density matrix, its Bloch vector, and its purity.

<details><summary>Solution</summary>

Input: `ρ = ½[[1,1],[1,1]]` (entries `a = b = c = d = ½`). Using the amplitude damping action

`ε_AD(ρ) = [[a + γd, √(1-γ)b],[√(1-γ)c, (1-γ)d]]`

with `γ = ½`: `a + γd = ½ + ¼ = ¾`, `(1-γ)d = ¼`, off-diagonals `√(½)·½ = 1/(2√2)`:

`ε_AD(ρ) = [[3/4, 1/(2√2)],[1/(2√2), 1/4]]`

Bloch vector: `r_x = 2·1/(2√2) = 1/√2 ≈ 0.707`, `r_y = 0`, `r_z = 3/4 - 1/4 = 1/2`.

`|r|² = 1/2 + 1/4 = 3/4 < 1` — the state has moved off the sphere surface (mixed) and drifted **toward the north pole** (`r_z` increased from 0 to 1/2), reflecting energy relaxation toward `|0⟩`.

Purity: `Tr(ρ'²) = (1 + |r|²)/2 = (1 + 3/4)/2 = 7/8`.

</details>

## Further Reading

1. **Nielsen & Chuang**, Chapter 8 — quantum noise and quantum operations; the canonical reference for Kraus representations and noise channels with physical motivation
2. **Preskill**, Lecture Notes Chapter 3 — density operators and quantum operations; §3.5 on the meaning of decoherence is particularly lucid
3. **Breuer & Petruccione**, *The Theory of Open Quantum Systems* (Oxford) — comprehensive treatment of open system dynamics, Lindblad master equations, and decoherence for physicists
4. **Wilde**, *Quantum Information Theory*, Chapter 4 — density matrices and quantum channels with information-theoretic perspective
5. **Zurek**, "Decoherence and the Transition from Quantum to Classical" (Physics Today, 1991) — accessible explanation of how the classical world emerges from quantum mechanics through decoherence; foundational paper for understanding why macroscopic systems do not show quantum behavior
