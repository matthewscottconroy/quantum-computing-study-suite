# Qubits and the Bloch Sphere

> **Prerequisites**: 01_linear_algebra.md (Pauli matrices, unitary operators), 02_complex_numbers_and_hilbert_spaces.md (global phase, projective space), 02_quantum_mechanics/01_postulates_of_quantum_mechanics.md  
> **Connects to**: Single-qubit gates (Chapter 3.1), quantum measurements (Chapter 2.3), quantum circuits, Bloch sphere interpretation of gate actions

## Overview

The **qubit** (quantum bit) is the fundamental unit of quantum information — the quantum analogue of the classical bit. Where a classical bit is either 0 or 1, a qubit can be in any superposition of the two basis states. But the qubit's state space is richer than just a probabilistic mixture: it forms a continuous sphere, the **Bloch sphere**, and the geometry of this sphere encodes all the physics.

The Bloch sphere is one of the most powerful tools in quantum computing. It makes abstract quantum states visual: every single-qubit state corresponds to a point on (or inside, for mixed states) the unit sphere in three dimensions. Every single-qubit gate corresponds to a rotation of this sphere. The relationship between quantum gates and rotations is not just a metaphor — it is an exact mathematical isomorphism between `SU(2)` (the group of `2×2` unitary matrices with determinant 1) and `SO(3)` (the group of rotations in three dimensions).

This chapter develops the Bloch sphere representation in detail, explains the physical meaning of the angles `θ` and `φ`, identifies the special states at the poles and equator, and then works out how the Pauli matrices and standard single-qubit gates act as rotations.

## The Qubit State Space

### Parametrizing the Qubit

A qubit is a two-dimensional complex quantum system with basis states `|0⟩` and `|1⟩`. The general state is:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \quad \alpha, \beta \in \mathbb{C}, \quad |\alpha|^2 + |\beta|^2 = 1$$

The constraint `|α|² + |β|² = 1` defines a 3-sphere `S³` in `ℂ² ≅ ℝ⁴`. But the physical state space is the projective space — we mod out by global phase. Removing the overall phase `e^{iγ}` reduces `S³` to the ordinary 2-sphere `S²`.

To see this explicitly, write `α = cos(θ/2)` and `β = e^{iφ}sin(θ/2)`:

$$|\psi\rangle = \cos\frac{\theta}{2}|0\rangle + e^{i\phi}\sin\frac{\theta}{2}|1\rangle$$

where `θ ∈ [0, π]` and `φ ∈ [0, 2π)`. We have used our freedom to choose a global phase to make `α` real and non-negative. These two parameters `(θ, φ)` are the standard spherical coordinates of a point on the unit 2-sphere `S²`.

**Why θ/2 and not θ?** If we used `θ ∈ [0, 2π)` directly, the north pole `(θ=0)` and south pole `(θ=π)` would correspond to the same vector `|0⟩` — making the parametrization redundant. Using `θ/2` ensures the full sphere `θ ∈ [0, π]` maps injectively to distinct states.

### The Bloch Sphere

The **Bloch sphere** is the unit sphere `{(x,y,z) ∈ ℝ³ : x²+y²+z² = 1}` where the point `(sin θ cos φ, sin θ sin φ, cos θ)` represents the state `cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩`.

The Cartesian Bloch vector `r = (r_x, r_y, r_z)` with `|r| = 1` encodes the same information. The Bloch vector is the expectation value of the Pauli vector:

$$\mathbf{r} = \langle\psi|\mathbf{\sigma}|\psi\rangle = (\langle X\rangle, \langle Y\rangle, \langle Z\rangle)$$

where `⟨X⟩ = ⟨ψ|X|ψ⟩`, etc. For a pure state, `|r| = 1` (on the sphere surface). For a mixed state (density matrix), `|r| < 1` (inside the sphere). The completely mixed state `I/2` has `r = 0` (the center).

**The density matrix from the Bloch vector**:

$$\rho = \frac{I + \mathbf{r}\cdot\mathbf{\sigma}}{2} = \frac{1}{2}\begin{pmatrix}1+r_z & r_x - ir_y \\ r_x + ir_y & 1-r_z\end{pmatrix}$$

This is a key formula: any single-qubit state (pure or mixed) is completely characterized by its Bloch vector `r`.

## Special States

### Poles: Computational Basis

- **North pole** `(θ=0)`: `|ψ⟩ = |0⟩`, Bloch vector `(0,0,1)`. This is the `+1` eigenstate of `Z`.
- **South pole** `(θ=π)`: `|ψ⟩ = e^{iφ}|1⟩ ≡ |1⟩` (global phase). Bloch vector `(0,0,-1)`. This is the `-1` eigenstate of `Z`.

Measuring `Z` (computational basis measurement) distinguishes these poles: `|0⟩` gives outcome `+1` with certainty, `|1⟩` gives outcome `-1` with certainty.

### Equatorial Points: X and Y Eigenstates

The equator `(θ = π/2)` consists of all states with equal superposition `|α| = |β| = 1/√2`, differing only in relative phase:

- **`|+⟩ = (|0⟩+|1⟩)/√2`**: Bloch vector `(1,0,0)`. The `+1` eigenstate of `X`.
- **`|−⟩ = (|0⟩-|1⟩)/√2`**: Bloch vector `(-1,0,0)`. The `-1` eigenstate of `X`.
- **`|+i⟩ = (|0⟩+i|1⟩)/√2`**: Bloch vector `(0,1,0)`. The `+1` eigenstate of `Y`.
- **`|−i⟩ = (|0⟩-i|1⟩)/√2`**: Bloch vector `(0,-1,0)`. The `-1` eigenstate of `Y`.

These six states form three orthogonal pairs (the "Pauli bases"). Standard quantum tomography measures in all three bases to reconstruct an unknown state.

### Geometric Interpretation of Orthogonality

A crucial fact: orthogonal quantum states correspond to **antipodal points** on the Bloch sphere, not perpendicular points.

For `|ψ⟩` with Bloch vector `r`, the orthogonal state `|ψ⊥⟩` has Bloch vector `-r`. This is because:

$$\langle\psi|\psi_\perp\rangle = 0 \iff \text{Bloch vectors are antiparallel}$$

Proof: `|0⟩` and `|1⟩` are orthogonal states at `(0,0,1)` and `(0,0,-1)` — antipodal, not perpendicular. `|+⟩` and `|-⟩` are at `(1,0,0)` and `(-1,0,0)` — also antipodal.

This means a qubit can only distinguish two **orthogonal** states perfectly, and these two states are always at opposite poles of some diameter of the Bloch sphere.

## Pauli Matrices as Observables

The Pauli matrices are the natural observables for a qubit. Each one measures a projection along one axis of the Bloch sphere.

For state `|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩`:

$$\langle Z\rangle = \cos\theta, \quad \langle X\rangle = \sin\theta\cos\phi, \quad \langle Y\rangle = \sin\theta\sin\phi$$

These are exactly the Cartesian coordinates of the Bloch vector expressed in spherical coordinates. Measuring `Z` asks "is the state closer to north or south pole?" Measuring `X` asks "is it closer to `|+⟩` or `|−⟩`?"

**Uncertainty principle**: The Pauli observables satisfy `[X,Y] = 2iZ`, `[Y,Z] = 2iX`, `[Z,X] = 2iY`. The generalized uncertainty principle gives:

$$\Delta X \cdot \Delta Y \geq |\langle [X,Y]/2i\rangle| = |\langle Z\rangle|$$

A state on the equator (`⟨Z⟩ = 0`) can simultaneously have zero variance in X and Y only if it is an eigenstate of both — impossible since `[X,Y] ≠ 0` in general. The trade-off between knowing X and Y is constrained by the Z expectation value.

## Rotations on the Bloch Sphere

### The Rotation Formula

This is the key result connecting `SU(2)` to rotations: the unitary

$$R_{\hat{n}}(\theta) = e^{-i\theta(\hat{n}\cdot\boldsymbol{\sigma})/2} = \cos\frac{\theta}{2}\,I - i\sin\frac{\theta}{2}(\hat{n}\cdot\boldsymbol{\sigma})$$

**rotates the Bloch vector by angle `θ` around axis `n̂`**.

Here `n̂ = (n_x, n_y, n_z)` is a unit vector and `n̂·σ = n_x X + n_y Y + n_z Z`. The second equality uses `(n̂·σ)² = I` (which follows from the Pauli algebra).

**Proof of rotation**: For state `ρ = (I + r·σ)/2`, the evolved state under `R_n̂(θ)` is:

$$\rho' = R_{\hat{n}}(\theta)\rho R_{\hat{n}}(\theta)^\dagger = \frac{I + \mathbf{r}'\cdot\boldsymbol{\sigma}}{2}$$

where `r' = R_{3D}(n̂,θ)r` is the classical 3D rotation of `r` by angle `θ` around axis `n̂`. The quantum gate is the `2×2` unitary; its action on the Bloch sphere is the `3×3` rotation matrix.

**The `SU(2) → SO(3)` double cover**: There is a 2-to-1 map from `SU(2)` to `SO(3)`. Both `R_n̂(θ)` and `R_n̂(θ+2π) = -R_n̂(θ)` produce the **same** rotation on the Bloch sphere (since the global phase `-1` is unobservable). A full `2π` rotation of the Bloch sphere requires a `4π` rotation in `SU(2)`. This has observable consequences for spin-1/2 particles in certain interference experiments.

### Standard Single-Qubit Gates as Rotations

**Pauli gates** (π rotations). The rotation formula gives `R_x(π) = cos(π/2)I - i sin(π/2)X = -iX`, so the Pauli gates equal π-rotations up to a global phase of `i`:
- `X = iR_x(π)`: rotates Bloch vector by `π` around x-axis. Sends `|0⟩ ↔ |1⟩`, `|+⟩ → |+⟩`, `|−⟩ → −|−⟩`.
- `Y = iR_y(π)`: rotates by `π` around y-axis. Sends `|0⟩ → i|1⟩, |1⟩ → -i|0⟩`.
- `Z = iR_z(π)`: rotates by `π` around z-axis. Sends `|+⟩ ↔ |−⟩`, `|0⟩ → |0⟩`, `|1⟩ → -|1⟩`.

**Hadamard** `H`: rotation by `π` around the axis `(x+z)/√2`:

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix} = \frac{X+Z}{\sqrt{2}}$$

Bloch sphere action: swaps the x- and z-axes. Sends `|0⟩ ↔ |+⟩`, `|1⟩ ↔ |−⟩`. This is why `HZH = X` and `HXH = Z` — Hadamard conjugation swaps the X and Z observables.

**Phase gate** `S = R_z(π/2)` (up to global phase):

$$S = \begin{pmatrix}1&0\\0&i\end{pmatrix} = e^{i\pi/4}\begin{pmatrix}e^{-i\pi/4}&0\\0&e^{i\pi/4}\end{pmatrix} = e^{i\pi/4}R_z(\pi/2)$$

Rotates Bloch vector by `π/2` around z-axis. `S² = Z` (two quarter-turns = half-turn). Maps `|+⟩ → |+i⟩`, `|-⟩ → |-i⟩`.

**T gate** `T = R_z(π/4)` (up to global phase):

$$T = \begin{pmatrix}1&0\\0&e^{i\pi/4}\end{pmatrix}$$

Rotates by `π/4` around z-axis. `T² = S`, `T⁴ = Z`, `T⁸ = I`. The T gate is **non-Clifford** — it cannot be decomposed into H, S, CNOT gates — and is a critical resource for universal quantum computing.

**Rotation gates**:
$$R_x(\theta) = e^{-i\theta X/2} = \begin{pmatrix}\cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2)\end{pmatrix}$$

$$R_y(\theta) = e^{-i\theta Y/2} = \begin{pmatrix}\cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2)\end{pmatrix}$$

$$R_z(\theta) = e^{-i\theta Z/2} = \begin{pmatrix}e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2}\end{pmatrix}$$

These are continuous families of gates parameterized by the rotation angle. Any single-qubit unitary can be decomposed as `U = e^{iγ}R_z(α)R_y(β)R_z(δ)` for some angles (Euler decomposition).

## Gate Identities from Bloch Sphere Geometry

Understanding the Bloch sphere makes many gate identities obvious:

- `H² = I`: two half-turns around the same axis return to start ✓
- `S² = Z`: two quarter-turns around z = half-turn around z ✓
- `T² = S`: two π/8 rotations = one π/4 rotation ✓
- `HXH = Z`: H swaps x and z axes, so X (x-axis rotation) becomes Z (z-axis rotation) ✓
- `HZH = X`: same swap in the other direction ✓
- `HYH = -Y`: H swaps x and z but leaves y up to sign ✓

More generally, for any axis `n̂` and any rotation operator `V`:
$$V R_{\hat{n}}(\theta) V^\dagger = R_{V\hat{n}}(\theta)$$

where `Vn̂` is the image of `n̂` under the Bloch sphere rotation corresponding to `V`. This is the **adjoint action** of `SU(2)` on `SO(3)`, and it explains all conjugation identities.

## Key Formulas

**Qubit state (Bloch sphere parameterization)**:
$$|\psi\rangle = \cos\frac{\theta}{2}|0\rangle + e^{i\phi}\sin\frac{\theta}{2}|1\rangle$$

**Bloch vector components**:
$$r_x = \langle X\rangle = \sin\theta\cos\phi, \quad r_y = \langle Y\rangle = \sin\theta\sin\phi, \quad r_z = \langle Z\rangle = \cos\theta$$

**Density matrix from Bloch vector**:
$$\rho = \frac{I + \mathbf{r}\cdot\boldsymbol{\sigma}}{2}$$

**Rotation operator**:
$$R_{\hat{n}}(\theta) = e^{-i\theta\hat{n}\cdot\boldsymbol{\sigma}/2} = \cos\frac{\theta}{2}I - i\sin\frac{\theta}{2}(\hat{n}\cdot\boldsymbol{\sigma})$$

**Euler decomposition**:
$$U = e^{i\gamma}R_z(\alpha)R_y(\beta)R_z(\delta)$$

## Worked Example

**Problem**: 

(a) Express the state `|ψ⟩ = (√3|0⟩ + i|1⟩)/2` in Bloch sphere form and find its Bloch vector.  
(b) What state results from applying the gate `S = [[1,0],[0,i]]`?  
(c) What state results from applying `H` to `|ψ⟩`?

**Solution**:

**(a) Bloch sphere form**:

We need `cos(θ/2) = √3/2` and `e^{iφ}sin(θ/2) = i/2`.

From `cos(θ/2) = √3/2`: `θ/2 = π/6`, so `θ = π/3` (60°).

From `sin(θ/2) = sin(π/6) = 1/2` and `e^{iφ}·(1/2) = i/2`: `e^{iφ} = i = e^{iπ/2}`, so `φ = π/2`.

Bloch vector:
$$r_x = \sin(\pi/3)\cos(\pi/2) = \frac{\sqrt{3}}{2}\cdot 0 = 0$$
$$r_y = \sin(\pi/3)\sin(\pi/2) = \frac{\sqrt{3}}{2}\cdot 1 = \frac{\sqrt{3}}{2}$$
$$r_z = \cos(\pi/3) = \frac{1}{2}$$

So `r = (0, √3/2, 1/2)`. Check: `|r|² = 0 + 3/4 + 1/4 = 1 ✓`

**(b) After applying S**:

$$S|\psi\rangle = \begin{pmatrix}1&0\\0&i\end{pmatrix}\frac{1}{2}\begin{pmatrix}\sqrt{3}\\i\end{pmatrix} = \frac{1}{2}\begin{pmatrix}\sqrt{3}\\i^2\end{pmatrix} = \frac{1}{2}\begin{pmatrix}\sqrt{3}\\-1\end{pmatrix}$$

New state: `(√3|0⟩ - |1⟩)/2`. The amplitude of `|1⟩` changed from `i/2` to `-1/2`.

New Bloch vector: `cos(θ'/2) = √3/2` (unchanged), `e^{iφ'}sin(θ'/2) = -1/2`. So `θ' = π/3` (unchanged) and `e^{iφ'} = -1 = e^{iπ}`, giving `φ' = π`.

New `r' = (sin(π/3)cos(π), sin(π/3)sin(π), cos(π/3)) = (-√3/2, 0, 1/2)`.

The S gate (R_z(π/2)) rotated the Bloch vector by 90° around the z-axis: `(0, √3/2, 1/2) → (-√3/2, 0, 1/2)`. The z-component is preserved (as it should be for a z-rotation), and the x-y components are rotated by 90°.

**(c) After applying H**:

$$H|\psi\rangle = \frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix}\frac{1}{2}\begin{pmatrix}\sqrt{3}\\i\end{pmatrix} = \frac{1}{2\sqrt{2}}\begin{pmatrix}\sqrt{3}+i\\\ \sqrt{3}-i\end{pmatrix}$$

Bloch vector after H: H swaps the x and z axes of the Bloch sphere (while negating y). So:
$$r'_x = r_z = 1/2, \quad r'_y = -r_y = -\sqrt{3}/2, \quad r'_z = r_x = 0$$

Verify: `|r'|² = 1/4 + 3/4 + 0 = 1 ✓`. The point has moved from the northern hemisphere to the equator, with a specific orientation determined by the gate.

## Summary

- A qubit state `α|0⟩ + β|1⟩` with `|α|²+|β|² = 1` is parameterized by angles `θ ∈ [0,π]` and `φ ∈ [0,2π)` via `α = cos(θ/2)`, `β = e^{iφ}sin(θ/2)`
- The **Bloch sphere** maps every single-qubit pure state to a unique point on the unit sphere; mixed states map to points inside the sphere
- Orthogonal states are **antipodal** on the Bloch sphere (not perpendicular)
- The Bloch vector is `r = (⟨X⟩, ⟨Y⟩, ⟨Z⟩)` and the density matrix is `ρ = (I + r·σ)/2`
- Single-qubit gates correspond to **rotations** of the Bloch sphere via `R_n̂(θ) = e^{-iθn̂·σ/2}`
- X, Y, Z are π-rotations around their respective axes; H is a π-rotation around `(x̂+ẑ)/√2`; S is a π/2-rotation around z; T is a π/4-rotation around z
- Gate identities `HXH = Z`, `HZH = X`, `S² = Z`, etc. follow directly from the geometry of Bloch sphere rotations
- There is a 2-to-1 map `SU(2) → SO(3)`: a `4π` rotation in `SU(2)` returns to the identity, but a `2π` rotation returns to `-I` (same Bloch sphere rotation, different global phase)

## Exercises

**Exercise 1**: Find the Bloch sphere angles `(θ, φ)` and the Bloch vector for (a) `|ψ⟩ = (|0⟩ - |1⟩)/√2` and (b) `|ψ⟩ = (√3|0⟩ + |1⟩)/2`.

<details><summary>Solution</summary>

**(a)** `cos(θ/2) = 1/√2` gives `θ = π/2`; the amplitude of `|1⟩` is `-1/√2 = e^{iπ}·(1/√2)`, so `φ = π`. Bloch vector: `r = (sin(π/2)cos π, sin(π/2)sin π, cos(π/2)) = (-1, 0, 0)`. This is `|−⟩`, the `-1` eigenstate of `X`, on the negative x-axis.

**(b)** `cos(θ/2) = √3/2` gives `θ/2 = π/6`, so `θ = π/3`; the `|1⟩` amplitude `1/2` is real positive, so `φ = 0`. Bloch vector: `r = (sin(π/3), 0, cos(π/3)) = (√3/2, 0, 1/2)`. Check: `|r|² = 3/4 + 1/4 = 1` ✓ — a point in the x–z plane, 60° down from the north pole.

</details>

**Exercise 2**: Verify by direct matrix computation that `R_x(π) = -iX`, and hence `X = iR_x(π)`. Why do `X` and `R_x(π)` implement the *same* Bloch sphere rotation despite being different matrices?

<details><summary>Solution</summary>

From the rotation formula:

`R_x(π) = cos(π/2)I - i sin(π/2)X = 0·I - i·X = -iX`

Explicitly: `R_x(π) = [[0, -i],[-i, 0]] = -i[[0,1],[1,0]] = -iX` ✓. Multiplying both sides by `i` gives `X = iR_x(π)`.

They implement the same rotation because they differ only by the global phase `-i`, and global phases have no effect on the Bloch vector: the state transformation `ρ → UρU†` is unchanged when `U → e^{iγ}U`, since `e^{iγ}Uρ(e^{iγ}U)† = UρU†`. This is the 2-to-1 nature of the `SU(2) → SO(3)` map.

</details>

**Exercise 3**: Apply the `T` gate to `|+⟩` and find the Bloch vector of the result. Verify that the action is a rotation of `(1,0,0)` by `π/4` around the z-axis.

<details><summary>Solution</summary>

`T|+⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2`. This has `θ = π/2` (equal magnitudes) and `φ = π/4`.

Bloch vector: `r = (cos(π/4), sin(π/4), 0) = (√2/2, √2/2, 0)`.

The initial state `|+⟩` has Bloch vector `(1, 0, 0)`. Rotating `(1,0,0)` by `π/4` about the z-axis gives `(cos(π/4), sin(π/4), 0)` — exactly the result ✓. The z-component is preserved (both are 0), as required for a z-rotation.

</details>

**Exercise 4**: Prove that orthogonal states are antipodal: show that for any state `|ψ⟩` with angles `(θ, φ)`, the state `|ψ⊥⟩` with angles `(π - θ, φ + π)` satisfies `⟨ψ⊥|ψ⟩ = 0`.

<details><summary>Solution</summary>

Write both states in the standard parameterization:

`|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩`

`|ψ⊥⟩ = cos((π-θ)/2)|0⟩ + e^{i(φ+π)}sin((π-θ)/2)|1⟩ = sin(θ/2)|0⟩ - e^{iφ}cos(θ/2)|1⟩`

using `cos((π-θ)/2) = sin(θ/2)`, `sin((π-θ)/2) = cos(θ/2)`, and `e^{iπ} = -1`. Then:

`⟨ψ⊥|ψ⟩ = sin(θ/2)cos(θ/2) + (-e^{-iφ})(e^{iφ})cos(θ/2)sin(θ/2) = sin(θ/2)cos(θ/2) - cos(θ/2)sin(θ/2) = 0` ✓

The angles `(π-θ, φ+π)` are exactly the antipodal point on the sphere: `(sin(π-θ)cos(φ+π), sin(π-θ)sin(φ+π), cos(π-θ)) = (-sinθ cosφ, -sinθ sinφ, -cosθ) = -r`.

</details>

## Further Reading

1. **Nielsen & Chuang**, §4.2 — single-qubit gates and the Bloch sphere; §4.1 defines qubits from the quantum mechanical perspective
2. **Bengtsson & Życzkowski**, *Geometry of Quantum States* (Cambridge) — comprehensive treatment of the geometry of qubit and multi-qubit state spaces; Chapter 5 is on the Bloch sphere
3. **Mermin**, *Quantum Computer Science: An Introduction* (Cambridge) — Chapter 1 introduces qubits with exceptional clarity without requiring physics background
4. **Feynman, Leighton & Sands**, *The Feynman Lectures on Physics*, Vol. III, Chapter 6 — the original pedagogically brilliant treatment of two-state systems and spin precession; the Bloch sphere picture in physicists' language
5. **Barnett**, *Quantum Information* (Oxford) — Chapter 2 develops the qubit and Bloch sphere with emphasis on measurement statistics and state tomography
