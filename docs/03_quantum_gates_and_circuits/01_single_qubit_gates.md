# Single-Qubit Gates

> **Prerequisites**: 02_qubits_and_the_bloch_sphere.md (rotation formula, Bloch vector), 01_linear_algebra.md (unitary matrices, Pauli matrices)  
> **Connects to**: Multi-qubit gates (Chapter 3.2), circuit model (Chapter 3.3), fault-tolerant computing (Clifford vs. non-Clifford distinction)

## Overview

Every single-qubit quantum gate is a `2×2` unitary matrix, and every `2×2` unitary matrix is (up to global phase) a rotation of the Bloch sphere. This chapter catalogs all the standard single-qubit gates used in quantum computing, providing for each one: the matrix representation, the action on basis states, the Bloch sphere interpretation as a rotation, and the gate's place in the hierarchy of Clifford versus non-Clifford operations.

Understanding individual gates deeply is not merely bookkeeping. The rotation formula `R_{n̂}(θ) = e^{-iθ n̂·σ/2}` connects the algebraic form of a gate to its geometric action, which in turn determines how errors propagate (a Z error before a gate becomes an X error after an H gate), what commutation relations hold, and how gates can be decomposed and optimized.

The Clifford/non-Clifford distinction deserves particular attention. Clifford gates (H, S, and CNOT) form an efficiently classically-simulable subset — the Gottesman-Knill theorem says any circuit built only from Clifford gates can be simulated in polynomial time on a classical computer. Adding any non-Clifford gate (like T) makes the gate set universal. This is why T gates (and their cost, T-count) are the key resource in fault-tolerant quantum computing.

## The Pauli Gates

### X Gate (NOT Gate, Bit Flip)

$$X = \begin{pmatrix}0 & 1\\ 1 & 0\end{pmatrix}$$

**Action on basis states**: `X|0⟩ = |1⟩`, `X|1⟩ = |0⟩` — flips the qubit, analogous to classical NOT.

**Action on general state**: `X(α|0⟩+β|1⟩) = α|1⟩+β|0⟩ = β|0⟩+α|1⟩` — swaps amplitudes.

**Bloch sphere**: Rotation by `π` around the x-axis. Sends `(r_x, r_y, r_z) → (r_x, -r_y, -r_z)`.

**Eigenstates**: `|+⟩ = (|0⟩+|1⟩)/√2` (eigenvalue +1), `|−⟩ = (|0⟩-|1⟩)/√2` (eigenvalue -1).

**Key property**: `X² = I` (self-inverse). Applying X twice returns to the original state.

### Y Gate

$$Y = \begin{pmatrix}0 & -i\\ i & 0\end{pmatrix}$$

**Action on basis states**: `Y|0⟩ = i|1⟩`, `Y|1⟩ = -i|0⟩`.

**Bloch sphere**: Rotation by `π` around the y-axis. Sends `(r_x, r_y, r_z) → (-r_x, r_y, -r_z)`.

**Eigenstates**: `|+i⟩ = (|0⟩+i|1⟩)/√2` (eigenvalue +1), `|−i⟩ = (|0⟩-i|1⟩)/√2` (eigenvalue -1).

**Key property**: `Y = iXZ = -iZX`. The Y gate is simultaneously a bit flip and a phase flip (with an extra `i` factor).

### Z Gate (Phase Flip)

$$Z = \begin{pmatrix}1 & 0\\ 0 & -1\end{pmatrix}$$

**Action on basis states**: `Z|0⟩ = |0⟩`, `Z|1⟩ = -|1⟩` — flips the phase of `|1⟩`, leaves `|0⟩` unchanged.

**Bloch sphere**: Rotation by `π` around the z-axis. Sends `(r_x, r_y, r_z) → (-r_x, -r_y, r_z)`.

**Eigenstates**: `|0⟩` (eigenvalue +1), `|1⟩` (eigenvalue -1) — the computational basis.

**Key property**: Z errors are "phase errors" — they do not affect `|0⟩` or `|1⟩` populations but flip the relative phase in superpositions.

## The Hadamard Gate

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix}1 & 1\\ 1 & -1\end{pmatrix}$$

**Action on basis states**: `H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2`, `H|1⟩ = |−⟩ = (|0⟩-|1⟩)/√2`.

**Action on superposition**: `H|+⟩ = |0⟩`, `H|−⟩ = |1⟩`. Hadamard swaps the computational and Hadamard bases.

**Bloch sphere**: Rotation by `π` around the diagonal axis `(x̂+ẑ)/√2`. Swaps the x and z axes: `(r_x, r_y, r_z) → (r_z, -r_y, r_x)`.

**Key identities**:
- `H² = I` (self-inverse)
- `HXH = Z`, `HZH = X`, `HYH = -Y`
- `H = (X+Z)/√2`

**Physical importance**: The Hadamard gate is the "go-to" gate for creating superpositions and changing measurement basis. It is used to:
1. Initialize a register in uniform superposition: `H⊗ⁿ|0⟩^n = (1/√2^n)Σ_x|x⟩`
2. Switch between X and Z measurement bases
3. Transform between computational and Hadamard eigenstates

Hadamard is a **Clifford gate**: it maps Pauli operators to Pauli operators under conjugation (`HXH = Z`, `HZH = X`, `HYH = -Y`).

## Phase Gates: S and T

### S Gate (Phase Gate, √Z)

$$S = \begin{pmatrix}1 & 0\\ 0 & i\end{pmatrix} = \sqrt{Z}$$

**Action on basis states**: `S|0⟩ = |0⟩`, `S|1⟩ = i|1⟩` — adds a phase of `i = e^{iπ/2}` to `|1⟩`.

**Bloch sphere**: Rotation by `π/2` around the z-axis (quarter turn).

**Key identity**: `S² = Z` (two quarter-turns = half-turn). `S⁴ = I`.

**S gate on superpositions**: `S|+⟩ = (|0⟩+i|1⟩)/√2 = |+i⟩`. Maps the +x equatorial point to the +y equatorial point.

**S is Clifford**: `SXS† = Y`, `SYS† = -X`, `SZS† = Z` (rotation of Pauli algebra by 90° around z-axis).

**S-dagger** (Sdg):
$$S^\dagger = \begin{pmatrix}1 & 0\\ 0 & -i\end{pmatrix}$$
This is `S⁻¹ = S³`. The adjoint of a gate undoes it.

### T Gate (π/8 Gate)

$$T = \begin{pmatrix}1 & 0\\ 0 & e^{i\pi/4}\end{pmatrix} = \begin{pmatrix}1 & 0\\ 0 & \frac{1+i}{\sqrt{2}}\end{pmatrix}$$

**Action on basis states**: `T|0⟩ = |0⟩`, `T|1⟩ = e^{iπ/4}|1⟩` — adds a phase of `e^{iπ/4} = (1+i)/√2`.

**Bloch sphere**: Rotation by `π/4` around the z-axis (one-eighth turn).

**Gate hierarchy**: `T² = S`, `T⁴ = Z`, `T⁸ = I`.

**Why "π/8 gate"?**: Up to global phase, `T = e^{iπ/8}R_z(π/4)`. The `π/8` comes from `π/(2^3)` in an older convention for the rotation angle.

**T is NOT Clifford**: `TXT† = (X+Y)/√2 = XR_z(π/4)†` — this is not a Pauli operator. Therefore T does not belong to the Clifford group.

**Fault-tolerant cost**: Implementing T fault-tolerantly using magic state distillation requires roughly 100-1000 physical qubits per logical T gate. T-count is therefore the dominant resource cost in fault-tolerant quantum computing.

**T-dagger** (Tdg):
$$T^\dagger = \begin{pmatrix}1 & 0\\ 0 & e^{-i\pi/4}\end{pmatrix}$$

## Rotation Gates

### Rx, Ry, Rz

The rotation gates provide continuous families parameterized by angle `θ`:

$$R_x(\theta) = e^{-i\theta X/2} = \begin{pmatrix}\cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2)\end{pmatrix}$$

$$R_y(\theta) = e^{-i\theta Y/2} = \begin{pmatrix}\cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2)\end{pmatrix}$$

$$R_z(\theta) = e^{-i\theta Z/2} = \begin{pmatrix}e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2}\end{pmatrix}$$

**Special cases**:
- `Rx(π) = -iX`, `Ry(π) = -iY`, `Rz(π) = -iZ` (Pauli gates up to global phase)
- `Rz(π/2) = e^{-iπ/4}S` (S gate up to global phase)
- `Rz(π/4) = e^{-iπ/8}T` (T gate up to global phase)
- `Ry(π/2) = (I-iY)/√2 = (I + Y)/√2 · e^{-iπ/4}` — used in circuit decompositions

**Euler decomposition**: Any single-qubit unitary can be written:

$$U = e^{i\gamma}R_z(\alpha)R_y(\beta)R_z(\delta)$$

for real angles `α, β, δ, γ`. This is useful for circuit compilation (finding the rotation angles that implement a desired unitary).

Alternative decomposition: `U = e^{iγ}R_z(α)R_x(β)R_z(δ)` (using Rx and Rz).

### U3 Gate (General Single-Qubit Gate)

IBM quantum devices use the `U3` gate as the most general single-qubit operation:

$$U_3(\theta,\phi,\lambda) = \begin{pmatrix}\cos(\theta/2) & -e^{i\lambda}\sin(\theta/2) \\ e^{i\phi}\sin(\theta/2) & e^{i(\phi+\lambda)}\cos(\theta/2)\end{pmatrix}$$

This parameterizes all `SU(2)` elements (2×2 unitaries with determinant 1). Special cases:
- `U3(π, 0, π) = X`
- `U3(π, π/2, π/2) = Y`
- `U3(0, 0, π) = Z`
- `U3(π/2, 0, π) = H`
- `U3(0, 0, π/2) = S`
- `U3(0, 0, π/4) = T`

## The Clifford Group and Clifford Gates

### Definition

The **Clifford group** `C_n` on `n` qubits is the group of unitaries that normalize the Pauli group under conjugation:

$$C_n = \{U : U P U^\dagger \in \mathcal{P}_n \text{ for all } P \in \mathcal{P}_n\}$$

where `P_n` is the `n`-qubit Pauli group (tensor products of Paulis with phases `±1, ±i`).

For single qubits, the Clifford group is generated by `{H, S}`. The 24 elements of the single-qubit Clifford group correspond to the 24 rotational symmetries of a cube (the chiral octahedral group).

**Clifford gates**: H, S (and their inverses/powers), and for multi-qubit: CNOT, CZ, SWAP.

**Clifford conjugation rules** (key for error propagation):
- `HXH = Z`, `HYH = -Y`, `HZH = X`
- `SXS† = Y`, `SYS† = -X`, `SZS† = Z`
- `CNOT(X⊗I)CNOT = X⊗X`
- `CNOT(I⊗X)CNOT = I⊗X`
- `CNOT(Z⊗I)CNOT = Z⊗I`
- `CNOT(I⊗Z)CNOT = Z⊗Z`

### Gottesman-Knill Theorem

**Gottesman-Knill theorem**: A quantum circuit consisting entirely of:
1. Computational basis state preparation
2. Clifford gates
3. Pauli measurements

can be simulated efficiently on a classical computer in polynomial time.

The simulation uses the **stabilizer formalism**: instead of tracking the state vector (exponentially large), track the `n` independent Pauli operators that stabilize the state. Clifford gates merely permute these operators, which can be updated in `O(n²)` time per gate.

**Implication**: Clifford gates alone give no quantum advantage over classical computation. The T gate (or any non-Clifford gate) is necessary to escape this simulation.

### Why T Is Non-Clifford

`TXT† = T·X·T† = [[0, e^{-iπ/4}],[e^{iπ/4}, 0]] = e^{-iπ/4}[[0,1],[e^{iπ/2},0]]`... let's compute directly:

$$TXT^\dagger = \begin{pmatrix}1&0\\0&e^{i\pi/4}\end{pmatrix}\begin{pmatrix}0&1\\1&0\end{pmatrix}\begin{pmatrix}1&0\\0&e^{-i\pi/4}\end{pmatrix} = \begin{pmatrix}0&e^{-i\pi/4}\\e^{i\pi/4}&0\end{pmatrix} = \frac{X+Y}{\sqrt{2}} \cdot e^{i\text{(global)}}$$

This is not a Pauli operator (it's `(X+Y)/√2` — a continuous rotation of X toward Y). So `T ∉ C₁`.

## Gate Identities

The following identities are essential for circuit simplification:

**Self-inverse gates**: `H² = X² = Y² = Z² = I`

**Pauli relations**: `XY = iZ`, `YZ = iX`, `ZX = iY`

**Hadamard conjugations**: `HXH = Z`, `HZH = X`, `HYH = -Y`

**Phase gate hierarchy**: `S = T²`, `Z = S² = T⁴`, `I = T⁸`

**Useful decompositions**:
- `X = HZH` — X is Z in the Hadamard basis
- `Y = iXZ = ISXSS†` — Y in terms of X, Z
- `H = (X+Z)/√2 = e^{iπ/2}R_x(π/2)ZR_x(π/2)` (various decompositions)

**Phase kickback identity** (crucial for algorithms): For `|+⟩` and phase gate `P|x⟩ = e^{iφ(x)}|x⟩`:
$$P \cdot H|0\rangle = \frac{e^{iφ(0)}|0\rangle + e^{iφ(1)}|1\rangle}{\sqrt{2}}$$

## Key Formulas

**Rotation gate**:
$$R_{\hat{n}}(\theta) = e^{-i\theta\hat{n}\cdot\boldsymbol{\sigma}/2} = \cos\frac{\theta}{2}I - i\sin\frac{\theta}{2}(\hat{n}\cdot\boldsymbol{\sigma})$$

**Euler decomposition**:
$$U = e^{i\gamma}R_z(\alpha)R_y(\beta)R_z(\delta)$$

**Clifford conjugation (H)**:
$$HXH = Z, \quad HZH = X, \quad HYH = -Y$$

**Gate hierarchy**:
$$T^2 = S, \quad S^2 = Z, \quad Z^2 = I, \quad T^8 = I$$

## Worked Example

**Problem**: 

(a) Show that `HTH = R_x(π/4)` up to a global phase, verifying the connection between H conjugation and Bloch sphere rotation axis change.  
(b) Decompose the unitary `U = (1/√2)[[1, i],[i, 1]]` into standard gates.

**Solution**:

**(a) Computing HTH**:

$$HTH = \frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix}\begin{pmatrix}1&0\\0&e^{i\pi/4}\end{pmatrix}\frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix}$$

Step 1 — TH:
$$TH = \begin{pmatrix}1&0\\0&e^{i\pi/4}\end{pmatrix}\frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix} = \frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\e^{i\pi/4}&-e^{i\pi/4}\end{pmatrix}$$

Step 2 — HTH:
$$HTH = \frac{1}{2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}\begin{pmatrix}1&1\\e^{i\pi/4}&-e^{i\pi/4}\end{pmatrix} = \frac{1}{2}\begin{pmatrix}1+e^{i\pi/4} & 1-e^{i\pi/4} \\ 1-e^{i\pi/4} & 1+e^{i\pi/4}\end{pmatrix}$$

Now `1 + e^{iπ/4} = 1 + (1+i)/√2 = (√2 + 1 + i)/√2`. Let `c = (1+e^{iπ/4})/2` and `s = (1-e^{iπ/4})/2 = -is_r` for real `s_r`.

Alternatively, compare with `R_x(π/4)`:
$$R_x(\pi/4) = \begin{pmatrix}\cos(\pi/8) & -i\sin(\pi/8) \\ -i\sin(\pi/8) & \cos(\pi/8)\end{pmatrix}$$

Note `(1+e^{iπ/4})/2 = e^{iπ/8}(e^{-iπ/8}+e^{iπ/8})/2 = e^{iπ/8}\cos(π/8)` and `(1-e^{iπ/4})/2 = -ie^{iπ/8}\sin(π/8)`.

Therefore:
$$HTH = e^{i\pi/8}\begin{pmatrix}\cos(\pi/8) & -i\sin(\pi/8) \\ -i\sin(\pi/8) & \cos(\pi/8)\end{pmatrix} = e^{i\pi/8}R_x(\pi/4)$$

The global phase `e^{iπ/8}` is unobservable. So **HTH** = `R_x(π/4)` up to global phase. **Interpretation**: H swaps the x and z axes of the Bloch sphere, so the z-axis rotation `T = R_z(π/4)` (up to phase) becomes an x-axis rotation under H conjugation.

**(b) Decomposing `U = (1/√2)[[1,i],[i,1]]`**:

Verify `U†U = I`:
$$U^\dagger U = \frac{1}{2}\begin{pmatrix}1&-i\\-i&1\end{pmatrix}\begin{pmatrix}1&i\\i&1\end{pmatrix} = \frac{1}{2}\begin{pmatrix}2&0\\0&2\end{pmatrix} = I \checkmark$$

`det(U) = (1/2)(1·1 - i·i) = (1/2)(1+1) = 1`. So `U ∈ SU(2)`.

Note `U = (I + iX)/√2 = e^{-iπ/2 \cdot (-X/2) \cdot 2}`. Actually, `(I + iX)/√2 = cos(π/4)I + i·sin(π/4)X = e^{iπX/4}`.

Using `R_x(θ) = e^{-iθX/2}`: `e^{iπX/4} = e^{-i(-π/2)X/2} = R_x(-π/2)`.

So `U = R_x(-π/2)`, a rotation by `-π/2` around the x-axis.

In terms of standard gates: `R_x(-π/2) = H·R_z(-π/2)·H = H·S†·H`.

Verify: `HSH·HH = HS†H`... Let's check directly: `HSH†`:
Wait, `S† = [[1,0],[0,-i]]`. Then `HS†H = (1/2)[[1,1],[1,-1]][[1,0],[0,-i]][[1,1],[1,-1]] = (1/2)[[1,-i],[1,i]][[1,1],[1,-1]] = (1/2)[[1+i, 1-i],[1-i,1+i]]/...`

This is getting complicated. More directly: `U = R_x(-π/2)` and since `R_x(θ) = HR_z(θ)H`, we have `U = H·R_z(-π/2)·H = H·S†·H`.

So the decomposition is: `U = H · S† · H`. Three standard Clifford gates.

## Summary

- Standard single-qubit gates: **I** (identity), **X** (NOT/bit-flip), **Y**, **Z** (phase-flip), **H** (Hadamard), **S** (phase/√Z), **S†** (S-dagger), **T** (π/8), **T†**
- All gates are rotations of the Bloch sphere via `R_n̂(θ) = e^{-iθn̂·σ/2}`
- **Clifford gates** (H, S, and their products) map Paulis to Paulis under conjugation; circuits of only Clifford gates are efficiently classically simulable (Gottesman-Knill)
- The **T gate** is non-Clifford and is the key resource for universal quantum computation; T-count is the dominant fault-tolerant resource cost
- Gate hierarchy: `T² = S`, `S² = Z`, `T⁸ = I`
- H conjugation swaps X and Z (and negates Y); this means X errors propagate as Z errors and vice versa after an H gate — critical for understanding error propagation in circuits
- Any single-qubit unitary has an **Euler decomposition** `U = e^{iγ}R_z(α)R_y(β)R_z(δ)`

## Further Reading

1. **Nielsen & Chuang**, §4.2 — single-qubit gates and their matrix representations; systematic treatment
2. **Gottesman**, "The Heisenberg Representation of Quantum Computers" (arXiv:quant-ph/9807006) — the original paper on the stabilizer formalism and Gottesman-Knill theorem
3. **Selinger**, "Generators and Relations for n-Qubit Clifford Operators" (Logical Methods in Computer Science, 2015) — modern treatment of Clifford group structure
4. **Fowler et al.**, "Surface codes: Towards practical large-scale quantum computation" (Physical Review A, 2012) — discusses T-count and T-depth as fault-tolerant resources in the context of surface codes
5. **Aaronson & Gottesman**, "Improved Simulation of Stabilizer Circuits" (Physical Review A, 2004) — efficient classical simulation of Clifford circuits; O(n²) per gate
