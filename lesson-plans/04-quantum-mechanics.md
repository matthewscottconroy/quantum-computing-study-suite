# Quantum Mechanics for Quantum Computing

## Goal
Develop the physical and mathematical foundations of quantum mechanics with a laser focus on the concepts that translate directly into quantum computing — state spaces, measurement, dynamics, and entanglement.

---

## Module 1 — The Postulates of Quantum Mechanics

**Objective:** Internalize the four postulates that define what quantum mechanics is.

| Postulate | Statement |
|---|---|
| 1. State space | A quantum system is associated with a Hilbert space H; the state is a unit vector `|ψ⟩ ∈ H` |
| 2. Evolution | Closed system dynamics are governed by a unitary operator: `|ψ(t)⟩ = U(t)|ψ(0)⟩` |
| 3. Measurement | An observable is a Hermitian operator A; outcomes are eigenvalues, probabilities are `|⟨aᵢ|ψ⟩|²` |
| 4. Composite systems | The state space of a composite system is `H₁ ⊗ H₂` |

**Exercises:**
- Verify that the Born rule probabilities sum to 1 for any normalized state

<details><summary>Solution</summary>

Let `A = A†` be an observable. By the spectral theorem it has an orthonormal eigenbasis `{|aᵢ⟩}` with `Σᵢ |aᵢ⟩⟨aᵢ| = I`. The Born rule assigns `p(i) = |⟨aᵢ|ψ⟩|²`. Then

```
Σᵢ p(i) = Σᵢ |⟨aᵢ|ψ⟩|²
        = Σᵢ ⟨ψ|aᵢ⟩⟨aᵢ|ψ⟩
        = ⟨ψ| ( Σᵢ |aᵢ⟩⟨aᵢ| ) |ψ⟩
        = ⟨ψ|I|ψ⟩ = ⟨ψ|ψ⟩ = 1
```

The only two inputs are **completeness** of the eigenbasis (guaranteed by Hermiticity, via the spectral theorem) and **normalization** of the state (Postulate 1). Nothing else is used — in particular the result holds for any observable and any state.

**Degenerate case.** Replace the rank-1 projectors by the spectral projectors `Πᵢ` onto each eigenspace, with `ΠᵢΠⱼ = δᵢⱼΠᵢ` and `ΣᵢΠᵢ = I`. Then `p(i) = ⟨ψ|Πᵢ|ψ⟩` and `Σᵢ p(i) = ⟨ψ|I|ψ⟩ = 1` by the same line.

**Mixed states and POVMs.** For `ρ` with `Tr ρ = 1`, `Σᵢ Tr(Πᵢρ) = Tr((ΣᵢΠᵢ)ρ) = Tr ρ = 1`. For a POVM `{Eᵢ}` the only requirement is `Eᵢ ≥ 0` and `Σ Eᵢ = I`, and again `Σᵢ Tr(Eᵢρ) = 1` — the completeness relation `Σ Eᵢ = I` is *defined* to be exactly the condition that makes probabilities normalize.

**Concrete check.** For `|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩` measured in the `Z` basis, `p(0) = cos²(θ/2)` and `p(1) = |e^{iφ}|²sin²(θ/2) = sin²(θ/2)`, summing to 1 for every `θ, φ` ✓. Note the phase `e^{iφ}` drops out of the `Z` statistics entirely — it is visible only in `X` or `Y` measurements.

</details>

- Compute the expected value `⟨Z⟩` for `|+⟩ = (|0⟩+|1⟩)/√2`

<details><summary>Solution</summary>

Three routes, all giving the same answer.

**Directly.** `Z|+⟩ = (Z|0⟩ + Z|1⟩)/√2 = (|0⟩ − |1⟩)/√2 = |−⟩`, and `⟨+|−⟩ = ½(1 − 1) = 0`, so

`⟨Z⟩ = ⟨+|Z|+⟩ = ⟨+|−⟩ = 0`

**From the Born rule.** `p(0) = |⟨0|+⟩|² = ½` and `p(1) = ½`, and the eigenvalues of `Z` are `±1`, so

`⟨Z⟩ = (+1)(½) + (−1)(½) = 0`

**From the Bloch vector.** `|+⟩` has `r = (1, 0, 0)`, and `⟨σ_k⟩ = r_k`, so `⟨Z⟩ = r_z = 0`.

**The variance, and why the answer is interesting.** `Z² = I`, so `⟨Z²⟩ = 1` and

`ΔZ = √(⟨Z²⟩ − ⟨Z⟩²) = √(1 − 0) = 1`

which is the *maximum* possible spread for an observable with eigenvalues `±1`. So `|+⟩` is maximally uncertain in `Z`. The flip side: `⟨X⟩ = 1` and `ΔX = 0`, because `|+⟩` is an `X` eigenstate. This trade-off is the uncertainty relation of Module 3 in action: `X` and `Z` are incompatible (`[X, Z] = −2iY ≠ 0`), so sharpness in one costs all information in the other.

`⟨Z⟩ = 0` is also the experimental signature that a Hadamard actually worked: run `qc.h(0)` and measure in the computational basis, and the 50/50 histogram is the statement `⟨Z⟩ = 0`. Measuring `⟨X⟩` instead requires rotating the basis first (`H` before the measurement), which is how any non-`Z` expectation value is read out on hardware.

</details>

- Show that post-measurement states are renormalized projections

<details><summary>Solution</summary>

**The postulate.** A projective measurement is a set `{Πᵢ}` with `Πᵢ = Πᵢ†`, `ΠᵢΠⱼ = δᵢⱼΠᵢ`, `ΣᵢΠᵢ = I`. Outcome `i` occurs with probability `p(i) = ⟨ψ|Πᵢ|ψ⟩`, and the state becomes

`|ψᵢ⟩ = Πᵢ|ψ⟩ / √p(i)`

**Why that normalization is forced.** The unnormalized post-measurement vector is `Πᵢ|ψ⟩`. Its squared norm is

`‖Πᵢ|ψ⟩‖² = ⟨ψ|Πᵢ†Πᵢ|ψ⟩ = ⟨ψ|Πᵢ²|ψ⟩ = ⟨ψ|Πᵢ|ψ⟩ = p(i)`

using `Πᵢ† = Πᵢ` and `Πᵢ² = Πᵢ`. Postulate 1 requires states to be unit vectors, and the only positive rescaling that achieves this is division by `√p(i)`. (The outcome is well defined only when `p(i) > 0`; an outcome of probability zero never occurs.) Note the beautiful economy: **the same quantity `⟨ψ|Πᵢ|ψ⟩` is both the probability and the squared norm** — the Born rule and the projection postulate are two readings of one equation.

**Repeatability.** Measuring again immediately gives the same outcome with certainty:

`Πᵢ|ψᵢ⟩ = Πᵢ²|ψ⟩/√p(i) = Πᵢ|ψ⟩/√p(i) = |ψᵢ⟩`  so  `p(i | i) = ⟨ψᵢ|Πᵢ|ψᵢ⟩ = 1`

and `p(j | i) = ⟨ψᵢ|Πⱼ|ψᵢ⟩ = 0` for `j ≠ i` by orthogonality. Idempotence of the projectors is exactly what makes measurement repeatable.

**Density-matrix form.** `ρ ↦ ΠᵢρΠᵢ / Tr(Πᵢρ)` for a recorded outcome, and `ρ ↦ Σᵢ ΠᵢρΠᵢ` if the outcome is discarded (non-selective measurement). The latter is a legitimate quantum channel — its Kraus operators are the `Πᵢ` themselves, and `ΣΠᵢ†Πᵢ = ΣΠᵢ = I` confirms trace preservation. For `Z`-basis measurement of a qubit it is the completely dephasing channel `r ↦ (0, 0, r_z)`.

**Global phase.** `Πᵢ|ψ⟩/√p(i)` fixes the state only up to a phase, but that is exactly right: `|ψᵢ⟩` and `e^{iα}|ψᵢ⟩` are the same physical state.

</details>

---

## Module 2 — Qubits and the Bloch Sphere

**Objective:** Develop intuition for single-qubit states via their geometric representation.

| Topic | Key Concepts |
|---|---|
| Qubit state space | ℂ² with unit norm: `α|0⟩ + β|1⟩`, `|α|²+|β|²=1` |
| Global phase irrelevance | `|ψ⟩` and `e^(iφ)|ψ⟩` represent the same state |
| Bloch sphere parametrization | `|ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩` |
| Poles and equator | Z eigenstates at poles; X,Y eigenstates on equator |
| Mixed states on Bloch ball | Density matrices fill the interior; surface = pure |

**Exercises:**
- Place `|+⟩`, `|−⟩`, `|i⟩`, `|−i⟩`, `|0⟩`, `|1⟩` on the Bloch sphere

<details><summary>Solution</summary>

Parametrize `|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩`; the Bloch vector is

`r = (⟨X⟩, ⟨Y⟩, ⟨Z⟩) = (sin θ cos φ, sin θ sin φ, cos θ)`

| state | ket | `(θ, φ)` | Bloch vector | pole |
|---|---|---|---|---|
| `\|0⟩` | `(1, 0)ᵀ` | `(0, –)` | `(0, 0, 1)` | `+z` |
| `\|1⟩` | `(0, 1)ᵀ` | `(π, –)` | `(0, 0, −1)` | `−z` |
| `\|+⟩` | `(\|0⟩+\|1⟩)/√2` | `(π/2, 0)` | `(1, 0, 0)` | `+x` |
| `\|−⟩` | `(\|0⟩−\|1⟩)/√2` | `(π/2, π)` | `(−1, 0, 0)` | `−x` |
| `\|i⟩` | `(\|0⟩+i\|1⟩)/√2` | `(π/2, π/2)` | `(0, 1, 0)` | `+y` |
| `\|−i⟩` | `(\|0⟩−i\|1⟩)/√2` | `(π/2, 3π/2)` | `(0, −1, 0)` | `−y` |

Spot-check `|i⟩`: `⟨X⟩ = ⟨i|X|i⟩ = ½(1, −i)·X·(1, i)ᵀ = ½(1, −i)·(i, 1)ᵀ = ½(i − i) = 0`; `⟨Y⟩ = ½(1, −i)·(1, i)ᵀ = ½(1 + 1) = 1`; `⟨Z⟩ = ½(1 − 1) = 0`. So `r = (0, 1, 0)` ✓.

**Three things to notice.**

1. **The half-angle.** Orthogonal states are *antipodal*, not perpendicular: `⟨0|1⟩ = 0` but their Bloch vectors are 180° apart. The factor `θ/2` in the parametrization is exactly what converts the 90° of Hilbert-space orthogonality into the 180° of the sphere — and it is the geometric face of the `SU(2) → SO(3)` double cover.
2. **The three axes are the three Pauli eigenbases.** `{|0⟩,|1⟩}` diagonalizes `Z`, `{|+⟩,|−⟩}` diagonalizes `X`, `{|i⟩,|−i⟩}` diagonalizes `Y`. Any two of these bases are *mutually unbiased*: `|⟨a|b⟩|² = ½` across bases, which is why measuring in the wrong basis yields a uniformly random bit (the BB84 security mechanism).
3. **Global phase is quotiented out.** `|1⟩` and `−|1⟩` are the same point; the map from `ℂ²` unit vectors to the sphere is the Hopf fibration `S³ → S²`, whose fibres are the global phases.

Gates as rotations: `X` rotates by `π` about `+x` (so it fixes `|±⟩` and swaps the poles), `Z` by `π` about `+z` (fixes `|0⟩, |1⟩`, swaps `|±⟩`), and `H` by `π` about `(1,0,1)/√2`, which swaps the `x` and `z` axes — hence `H|0⟩ = |+⟩` and `H|+⟩ = |0⟩`.

</details>

- Show that a general qubit rotation maps to a rotation of the Bloch sphere

<details><summary>Solution</summary>

**Set-up.** Every state is `ρ = (I + r·σ)/2` with `r ∈ ℝ³`, `|r| ≤ 1`, and `r_k = Tr(ρσ_k)`. Every gate is, up to global phase, `U = e^{−iθ n̂·σ/2} = cos(θ/2) I − i sin(θ/2) n̂·σ ∈ SU(2)`. Evolution is `ρ ↦ UρU†`.

**The induced map is linear.** Because `U I U† = I` and conjugation is linear,

`UρU† = (I + Σ_j r_j Uσ_jU†)/2`

Each `Uσ_jU†` is Hermitian and traceless (conjugation preserves both), so it is again a real combination of Paulis: `Uσ_jU† = Σ_i R_{ij} σ_i` with `R_{ij} = ½Tr(σ_i U σ_j U†)`. Hence `r ↦ r' = R r` with `R` a real `3 × 3` matrix. The compact statement is

`U (n̂·σ) U† = (R n̂)·σ`

**`R` is orthogonal.** The Hilbert–Schmidt form `⟨A, B⟩ = ½Tr(A†B)` makes `{σ₁,σ₂,σ₃}` orthonormal, and conjugation by a unitary preserves it: `½Tr((UAU†)†(UBU†)) = ½Tr(A†B)`. So `R` preserves the Euclidean inner product on `ℝ³`, i.e. `RᵀR = I`.

**`det R = +1`.** `R` depends continuously on `θ`, `R = I` at `θ = 0`, and `det R ∈ {±1}` is continuous, hence constant: `det R = 1`. So `R ∈ SO(3)`.

**Which rotation.** Expanding `R_{ij} = ½Tr(σ_i U σ_j U†)` with the Pauli algebra gives Rodrigues' formula — `R` is the rotation by angle `θ` about the axis `n̂`. Verified numerically for `U = R_z(0.7) = e^{−i(0.7)Z/2}`:

```
R = [[ cos 0.7, −sin 0.7, 0],      = [[ 0.764842, −0.644218, 0],
     [ sin 0.7,  cos 0.7, 0],         [ 0.644218,  0.764842, 0],
     [ 0,        0,       1]]         [ 0,         0,        1]]
```

with `RᵀR = I` and `det R = 1.0` ✓.

**The two-to-one map.** `Ad(U) = Ad(−U)`, since the two `−1`s cancel in `UρU†`. So the map `SU(2) → SO(3)` is a surjective homomorphism with kernel `{±I}`:

`SO(3) ≅ SU(2)/{±I}`

Physically: a `2π` gate is `R_n̂(2π) = −I` on the state vector — an observable relative phase when the qubit is half of an entangled pair — but it is the identity rotation of the Bloch sphere. Purity is preserved (`|r'| = |r|`), so unitary evolution moves points on a fixed-radius shell and can never take a pure state to a mixed one; that requires a non-unitary channel (Module 6).

</details>

- Find the Bloch vector of `ρ = I/2` (maximally mixed state)

<details><summary>Solution</summary>

The Bloch components are `r_k = Tr(ρ σ_k)`. With `ρ = I/2`,

`r_k = ½ Tr(σ_k) = 0`  for `k = x, y, z`

because all three Pauli matrices are traceless. So

`r = (0, 0, 0)` — the **centre** of the Bloch ball.

**Consistency.** The general parametrization `ρ = (I + r·σ)/2` returns `ρ = I/2` when `r = 0` ✓. Purity: `Tr(ρ²) = (1 + |r|²)/2 = ½`, the minimum for a qubit (verified numerically), so `I/2` is the unique state of minimal purity — hence "maximally mixed". Its von Neumann entropy is `S = −Tr(ρ log₂ ρ) = 1` bit, the maximum for a two-level system.

**What `r = 0` means operationally.** `⟨σ_k⟩ = r_k = 0` for every axis, and more generally `⟨n̂·σ⟩ = 0` for every direction `n̂`. So *every* projective measurement, in *every* basis, returns 50/50. The state carries no information at all.

**Invariance.** `U (I/2) U† = I/2` for every unitary — the centre is the unique fixed point of all Bloch rotations. That makes `I/2` the natural "no information" reference state: it is the output of the completely depolarizing channel, the result of twirling any state over a unitary 2-design (or over the full Haar measure), and the infinite-temperature thermal state.

**Where it shows up.**
- Each qubit of a Bell pair has `ρ_A = I/2` (Module 5) — maximal entanglement means maximal local ignorance, and this is exactly why entanglement cannot be used for signalling.
- Ensemble non-uniqueness: `I/2 = ½|0⟩⟨0| + ½|1⟩⟨1| = ½|+⟩⟨+| + ½|−⟩⟨−| = ∫ dn̂ |n̂⟩⟨n̂|`. Physically distinct preparations, identical density matrix, and therefore experimentally indistinguishable.
- The depolarizing channel `ε(ρ) = (1−p)ρ + p I/2` drives every state toward this point; `p → 1` is complete decoherence.

</details>

---

## Module 3 — Observables and Measurement

**Objective:** Understand the quantum measurement process precisely, including projective and generalized measurements.

| Topic | Key Concepts |
|---|---|
| Projective measurement | Orthogonal projectors {Πᵢ}, probabilities `p(i) = ⟨ψ|Πᵢ|ψ⟩` |
| Post-measurement state | `|ψ'⟩ = Πᵢ|ψ⟩ / √p(i)` |
| Compatible observables | [A,B] = 0 ⟺ simultaneously measurable |
| Uncertainty principle | `ΔA·ΔB ≥ ½|⟨[A,B]⟩|` |
| POVM | Positive Operator-Valued Measures — generalized measurement |
| POVM elements | Eᵢ ≥ 0, ΣEᵢ = I |

**Quantum computing connections:**
- Computational basis measurement is a projective measurement in {|0⟩, |1⟩} basis
- POVMs appear in quantum state discrimination and quantum communication
- The no-cloning theorem follows from linearity and unitarity

**Exercises:**
- Compute probabilities and post-measurement states for measuring `|+⟩` in Z basis

<details><summary>Solution</summary>

State `|+⟩ = (|0⟩ + |1⟩)/√2`; measurement operators `Π₀ = |0⟩⟨0|`, `Π₁ = |1⟩⟨1|`.

**Probabilities.**

```
p(0) = ⟨+|Π₀|+⟩ = |⟨0|+⟩|² = |1/√2|² = ½
p(1) = ⟨+|Π₁|+⟩ = |⟨1|+⟩|² = ½
```

Sum `= 1` ✓.

**Post-measurement states.**

```
|ψ₀⟩ = Π₀|+⟩/√p(0) = (|0⟩/√2)/(1/√2) = |0⟩
|ψ₁⟩ = Π₁|+⟩/√p(1) = (|1⟩/√2)/(1/√2) = |1⟩
```

The superposition is destroyed: the outcome is random, and afterwards the qubit sits in a definite computational-basis state.

**What was lost.** Before the measurement, `⟨X⟩ = 1` (the state is an `X` eigenstate, `ΔX = 0`). After it, each outcome state has `⟨X⟩ = 0`. Averaging over the unrecorded outcome gives

`ρ' = Σᵢ Πᵢ|+⟩⟨+|Πᵢ = ½|0⟩⟨0| + ½|1⟩⟨1| = I/2`

so the Bloch vector goes from `(1, 0, 0)` to `(0, 0, 0)` — the `Z`-basis measurement is the completely dephasing channel, killing the `x` and `y` components while leaving `r_z` (here already 0) untouched. Note the result is the **maximally mixed** state, not a pure state: the randomness of the outcome is the loss of coherence.

**Contrast: measure the same state in the `X` basis.** With `Π_± = |±⟩⟨±|`, `p(+) = 1`, `p(−) = 0`, and the post-measurement state is `|+⟩` — unchanged, and no randomness. A measurement is "gentle" precisely when the state is already an eigenstate of the measured observable.

**Practical reading.** This two-line calculation is what a Hadamard-then-measure circuit does: `qc.h(0); qc.measure(0,0)` on `|0⟩` yields a 50/50 histogram, and the hardware qubit really is left in `|0⟩` or `|1⟩`. To *see* the coherence of `|+⟩` you must undo the basis change first (a second `H`), which returns `|0⟩` with probability 1 — the standard single-qubit interference check.

</details>

- Design a POVM that distinguishes `|0⟩` and `|+⟩` with minimum error

<details><summary>Solution</summary>

**The problem.** One copy of an unknown state, equally likely to be `ρ₀ = |0⟩⟨0|` or `ρ₁ = |+⟩⟨+|`; choose a two-outcome POVM `{E₀, E₁}` (guess `|0⟩` on outcome 0) minimizing the average error. Since `|⟨0|+⟩|² = ½ ≠ 0`, the states are non-orthogonal and perfect discrimination is impossible.

**Helstrom's theorem.** For equal priors the optimal success probability is

`p_success = ½ ( 1 + ½‖ρ₀ − ρ₁‖₁ )`

attained by projecting onto the positive and negative eigenspaces of `Λ = ½(ρ₀ − ρ₁)`. (Sketch: `p_success = ½ + ½Tr(Λ(E₀ − E₁))`, and over `0 ≤ Eᵢ ≤ I` this is maximized by taking `E₀` to be the projector onto the positive part of `Λ`.)

**Apply it.** In Bloch form `ρ₀ = (I + Z)/2` and `ρ₁ = (I + X)/2`, so

`ρ₀ − ρ₁ = (Z − X)/2`

`Z − X` has eigenvalues `±√2`, so `ρ₀ − ρ₁` has eigenvalues `±1/√2` and `‖ρ₀ − ρ₁‖₁ = √2` (trace distance `1/√2 ≈ 0.7071`). Therefore

```
p_success = ½ + √2/4 = ½ + 1/(2√2) ≈ 0.853553
p_error   = ½ − 1/(2√2) = (1 − 1/√2)/2 ≈ 0.146447
```

Both values reproduced numerically. They also match the pure-state formula `p_err = ½(1 − √(1 − |⟨0|+⟩|²)) = ½(1 − 1/√2)` ✓.

**The measurement itself is projective.** The `+1` eigenvector of `(Z − X)/2` has Bloch axis

`n̂ = (−1, 0, 1)/√2`  (verified numerically)

so `E₀ = |n̂₊⟩⟨n̂₊|` with `|n̂₊⟩ = cos(π/8)|0⟩ − sin(π/8)|1⟩`, and `E₁ = I − E₀`. Outcome 0 → guess `|0⟩`; outcome 1 → guess `|+⟩`. No genuinely non-projective POVM is needed: for two hypotheses the optimum is always a projective measurement.

**Geometric reading.** `|0⟩` and `|+⟩` sit 90° apart on the Bloch sphere at `(0,0,1)` and `(1,0,0)`. Their bisector is `(1,0,1)/√2`; the optimal measurement axis is the perpendicular direction in the same plane, `(−1,0,1)/√2`, which separates the two Bloch vectors as symmetrically as possible. Each state lies at `45°` to the measurement axis, giving `cos²(22.5°) = 0.8536` — exactly `p_success`.

**Implementation.** `E₀` is the `Z`-basis projector conjugated by a rotation: applying `R_y(π/4) = e^{−i(π/4)Y/2}` sends `|n̂₊⟩` to `|0⟩` exactly (verified numerically), so the optimal strategy is one `R_y(π/4)` followed by a standard computational-basis readout.

**Contrast with unambiguous discrimination.** If you instead demand *never* to answer wrongly, you must allow an inconclusive outcome; the optimal (IDP/Ivanovic–Dieks–Peres) failure probability is `|⟨0|+⟩| = 1/√2 ≈ 0.707`. Minimum-error is the right figure of merit whenever you must commit to an answer on every shot — as in a quantum receiver, or in single-shot qubit readout.

</details>

- Derive the uncertainty relation for X and Z on a qubit

<details><summary>Solution</summary>

**General Robertson relation.** For Hermitian `A, B` and any state `|ψ⟩`, write `Ā = A − ⟨A⟩I`, `B̄ = B − ⟨B⟩I` (so `ΔA² = ⟨Ā²⟩`). Cauchy–Schwarz on `Ā|ψ⟩` and `B̄|ψ⟩` gives

`⟨Ā²⟩⟨B̄²⟩ ≥ |⟨Ā B̄⟩|²`

Split the product into Hermitian and anti-Hermitian parts, `ĀB̄ = ½{Ā,B̄} + ½[A,B]` (the commutator is unaffected by the shifts). `⟨{Ā,B̄}⟩` is real and `⟨[A,B]⟩` is purely imaginary, so the two contributions add in quadrature:

`|⟨ĀB̄⟩|² = ¼⟨{Ā,B̄}⟩² + ¼|⟨[A,B]⟩|² ≥ ¼|⟨[A,B]⟩|²`

Taking square roots, `ΔA · ΔB ≥ ½|⟨[A,B]⟩|`.

**Specialize to `X` and `Z`.** `[X, Z] = XZ − ZX = −iY − iY = −2iY`, so

```
ΔX · ΔZ ≥ ½|⟨−2iY⟩| = |⟨Y⟩|
```

**In Bloch coordinates.** For `r = (x, y, z)`, `⟨X⟩ = x` and `⟨X²⟩ = ⟨I⟩ = 1`, so `ΔX = √(1 − x²)`; likewise `ΔZ = √(1 − z²)` and `⟨Y⟩ = y`. The relation reads

`√((1 − x²)(1 − z²)) ≥ |y|`

**Check it holds.** For a pure state, `x² + y² + z² = 1`, so

`(1 − x²)(1 − z²) = (y² + z²)(x² + y²) = y⁴ + y²x² + y²z² + x²z² = y²(x² + y² + z²) + x²z² = y² + x²z² ≥ y²` ✓

with equality iff `xz = 0`. For mixed states `|r| ≤ 1` only enlarges the left side.

**Saturating examples.**
- `|+i⟩`, `r = (0, 1, 0)`: `ΔX = ΔZ = 1`, `|⟨Y⟩| = 1` — the bound `1 ≥ 1` is tight.
- `|0⟩`, `r = (0,0,1)`: `ΔZ = 0`, `ΔX = 1`, `⟨Y⟩ = 0` — both sides zero, tight but vacuous.
- `|+⟩`, `r = (1,0,0)`: `ΔX = 0`, `ΔZ = 1`, `⟨Y⟩ = 0` — likewise.

**Reading the physics.** `ΔX = ΔZ = 0` would require `x² = z² = 1`, impossible since `|r| ≤ 1`: no qubit state is sharp in both `X` and `Z`. This is not a statement about clumsy apparatus — it is a property of the state, forced by `[X, Z] ≠ 0`. Note also that the Robertson bound can be *trivially* zero (whenever `⟨Y⟩ = 0`) even though `X` and `Z` remain incompatible; the stronger Maccone–Pati and entropic relations fix that. The incompatibility of `X` and `Z` is a resource, not just a limitation: it is what makes BB84 secure (an eavesdropper must guess the basis) and what forces quantum error-correcting codes to protect against both bit-flip and phase-flip errors.

</details>

---

## Module 4 — Quantum Dynamics

**Objective:** Understand how quantum states evolve in time, both in continuous (Schrödinger) and discrete (circuit) formulations.

| Topic | Key Concepts |
|---|---|
| Schrödinger equation | `iℏ d|ψ⟩/dt = H|ψ⟩` |
| Time evolution operator | `U(t) = e^(−iHt/ℏ)` for time-independent H |
| Stationary states | Energy eigenstates `H|E⟩ = E|E⟩` evolve by phase |
| Interaction picture | Separate fast H₀ from slow perturbation H' |
| Trotter decomposition | `e^(A+B) ≈ e^(A)e^(B)` — basis of Hamiltonian simulation |
| Gate as unitary | Discrete-time evolution for quantum circuits |

**Exercises:**
- Derive the time evolution of `|+⟩` under H = ωZ/2

<details><summary>Solution</summary>

Work in units `ħ = 1`. The Hamiltonian is time-independent, so

`U(t) = e^{−iHt} = e^{−iωtZ/2} = R_z(ωt) = diag(e^{−iωt/2}, e^{+iωt/2})`

matching the corpus convention `R_z(θ) = e^{−iθZ/2}`. Applying it to `|+⟩ = (|0⟩ + |1⟩)/√2`:

```
|ψ(t)⟩ = (e^{−iωt/2}|0⟩ + e^{+iωt/2}|1⟩)/√2
       = e^{−iωt/2} (|0⟩ + e^{iωt}|1⟩)/√2
```

(verified numerically at `ω = 1.3`, `t = 0.85`: the state vector is `(0.6019 − 0.3711i, 0.6019 + 0.3711i)`, matching the analytic expression exactly.)

The energy eigenstates `|0⟩` and `|1⟩` (eigenvalues `±ω/2`) only acquire phases — they are **stationary states**, and all observable motion comes from their *relative* phase, which winds at rate `ω = E₁ − E₀`.

**Bloch picture.** With `α = e^{−iωt/2}/√2`, `β = e^{iωt/2}/√2`:

```
⟨X⟩ = 2 Re(α*β) = cos ωt
⟨Y⟩ = 2 Im(α*β) = sin ωt
⟨Z⟩ = |α|² − |β|² = 0
```

Numerical check at `ωt = 1.105`: `⟨X⟩ = 0.449134 = cos(1.105)`, `⟨Y⟩ = 0.893464 = sin(1.105)`, `⟨Z⟩ = 0` ✓.

So the Bloch vector starts at `+x` and **precesses in the equatorial plane** at angular frequency `ω`, in the positive (right-hand about `+z`) sense — Larmor precession. It reaches `|i⟩` at `ωt = π/2`, `|−⟩` at `ωt = π`, and returns to `|+⟩` at `ωt = 2π`.

**Two conventions worth separating.** The *state vector* only returns to itself at `ωt = 4π` (`U(t) = −I` at `ωt = 2π`), while the *physical state* has period `2π/ω` because the extra `−1` is a global phase. The double cover again.

**Why this is the workhorse experiment.** `H = ωZ/2` is a qubit detuned by `ω` from its drive, and the circuit "prepare `|+⟩`, wait `t`, apply `H`, measure `Z`" is a **Ramsey experiment**: the measured probability is `p(0) = (1 + cos ωt)/2`, a fringe of frequency `ω`. Fitting the fringe calibrates the qubit frequency; fitting the decay of its envelope measures `T₂*` (`docs/02_quantum_mechanics/10_distance_measures_and_lindblad.md`). Every `R_z` gate on superconducting hardware is this evolution, usually implemented "virtually" by shifting the phase of subsequent drive pulses rather than by waiting.

</details>

- Show that the Hadamard gate is `e^(iπ(X+Z)/2√2)` up to global phase

<details><summary>Solution</summary>

The key structural fact is that `H` is a **Hermitian involution**:

`H = (X + Z)/√2`,  `H† = H`,  `H² = ½(X² + Z² + XZ + ZX) = ½(I + I + 0) = I`

using `XZ + ZX = 0`. Any operator squaring to `I` collapses its exponential series exactly as the Paulis do:

`e^{iαH} = Σₖ (iα)ᵏHᵏ/k! = cos α · I + i sin α · H`

**Take `α = π/2`:**

```
e^{iπH/2} = cos(π/2) I + i sin(π/2) H = iH
```

Since `H = (X + Z)/√2`, the exponent `iπH/2` is `iπ(X + Z)/(2√2)`, so

`e^{iπ(X+Z)/(2√2)} = i H`,  equivalently  `H = −i · e^{iπ(X+Z)/(2√2)}`

i.e. the two agree up to the global phase `i`, as claimed. Numerically the exponential evaluates to `[[0.7071i, 0.7071i],[0.7071i, −0.7071i]] = i·H` ✓.

**In the corpus rotation convention.** With `n̂ = (1, 0, 1)/√2` so that `n̂·σ = H`,

`R_n̂(π) = e^{−iπ n̂·σ/2} = cos(π/2) I − i sin(π/2)(n̂·σ) = −i H`

so `H = i R_n̂(π)`. Reading it geometrically: **the Hadamard is a `π` rotation of the Bloch sphere about the diagonal axis `(1,0,1)/√2`**. That single sentence explains its entire behaviour:

- it exchanges the `x` and `z` axes, hence `HXH = Z` and `HZH = X` (verified numerically), and maps `|0⟩ ↔ |+⟩`, `|1⟩ ↔ |−⟩`;
- it reverses the `y` axis (`HYH = −Y`), since a `π` rotation flips the two directions perpendicular to its axis;
- `H² = I` because a `π` rotation applied twice is a `2π` rotation, which is the identity on the sphere (and `−I` on the state vector, absorbed into the global phase).

**Why the phase is unavoidable.** `det H = −1`, so `H ∈ U(2) \ SU(2)`; every exponential `e^{−iθn̂·σ/2}` has determinant 1. A phase factor is therefore *required* to connect them, and `i` is the smallest choice: `det(iH) = i²·(−1) = 1` ✓. Since global phases are unobservable, hardware and textbooks use `H` and `iH` interchangeably — but the distinction matters the moment `H` appears as a *controlled* operation, where the phase becomes relative.

</details>

- Derive the first-order Trotter error bound

<details><summary>Solution</summary>

**Goal.** Bound `‖e^{−i(A+B)t} − (e^{−iAt/n} e^{−iBt/n})^n‖` for Hermitian `A, B`, in the operator (spectral) norm.

**Step 1 — one short step.** Let `δ = t/n` and expand both sides to second order:

```
e^{−iAδ} e^{−iBδ} = (I − iAδ − A²δ²/2)(I − iBδ − B²δ²/2) + O(δ³)
                  = I − i(A+B)δ − (A² + 2AB + B²)δ²/2 + O(δ³)

e^{−i(A+B)δ}      = I − i(A+B)δ − (A+B)²δ²/2 + O(δ³)
                  = I − i(A+B)δ − (A² + AB + BA + B²)δ²/2 + O(δ³)
```

The first-order terms cancel identically. Subtracting:

```
e^{−iAδ}e^{−iBδ} − e^{−i(A+B)δ} = −½(2AB − AB − BA)δ² + O(δ³) = −½[A, B]δ² + O(δ³)
```

So the per-step error is `‖[A,B]‖ δ²/2 + O(δ³)`, and it vanishes identically when `A` and `B` commute.

**Step 2 — accumulate over `n` steps.** For unitaries, errors add rather than multiply: using unitary invariance of the operator norm and the telescoping identity `∏Uᵢ − ∏Vᵢ = Σⱼ (∏_{i<j}Vᵢ)(Uⱼ − Vⱼ)(∏_{i>j}Uᵢ)`,

`‖∏ᵢUᵢ − ∏ᵢVᵢ‖ ≤ Σᵢ ‖Uᵢ − Vᵢ‖`

With `n` identical steps of size `δ = t/n`:

```
‖e^{−i(A+B)t} − (e^{−iAt/n}e^{−iBt/n})^n‖ ≤ n · ‖[A,B]‖ (t/n)²/2 = ‖[A,B]‖ t² / (2n)
```

**Reading the bound.** Error scales as `O(t²/n)`, so reaching accuracy `ε` needs `n = O(‖[A,B]‖t²/ε)` Trotter steps — linear in `1/ε`, quadratic in the simulated time. The second-order (Strang) splitting `e^{−iAδ/2}e^{−iBδ}e^{−iAδ/2}` improves this to `O(t³/n²)`, and higher-order Suzuki formulas do better still; all of them reduce to the identity when the terms commute, which is why grouping a Hamiltonian into mutually commuting Pauli layers is the first move in any simulation compiler.

**Numerical confirmation** with `A = Z`, `B = X`, `t = 1`, so `[A,B] = [Z,X] = 2iY` and `‖[A,B]‖ = 2`, making the bound `1/n`:

| `n` | actual error | bound `‖[A,B]‖t²/(2n)` |
|---|---|---|
| 1 | 0.799214 | 1.000000 |
| 2 | 0.362410 | 0.500000 |
| 4 | 0.176261 | 0.250000 |
| 8 | 0.087513 | 0.125000 |
| 16 | 0.043679 | 0.062500 |
| 32 | 0.021830 | 0.031250 |

The bound holds at every `n`, and the measured error halves each time `n` doubles — the predicted `1/n` scaling.

</details>

---

## Module 5 — Entanglement

**Objective:** Understand entanglement as a physical phenomenon and as a computational resource.

| Topic | Key Concepts |
|---|---|
| Separability | `ρ_AB = ρ_A ⊗ ρ_B` — product state |
| Entanglement | State that is NOT separable |
| Bell states | The four maximally entangled 2-qubit states |
| Schmidt decomposition | Any bipartite pure state: `|ψ⟩ = Σ λᵢ|aᵢ⟩|bᵢ⟩` |
| Schmidt rank | Number of non-zero Schmidt coefficients |
| Entanglement entropy | `S(ρ_A) = −Tr(ρ_A log ρ_A)` |
| Monogamy of entanglement | Sharing limits: if A is maximally entangled with B, A is unentangled with C |

**Exercises:**
- Verify that all four Bell states are maximally entangled

<details><summary>Solution</summary>

The four Bell states and their coefficient matrices `C` (rows = qubit A, columns = qubit B, `|ψ⟩ = Σ C_{ij}|ij⟩`):

```
|Φ⁺⟩ = (|00⟩ + |11⟩)/√2      C = (1/√2)[[1, 0],[0,  1]]
|Φ⁻⟩ = (|00⟩ − |11⟩)/√2      C = (1/√2)[[1, 0],[0, −1]]
|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2      C = (1/√2)[[0, 1],[1,  0]]
|Ψ⁻⟩ = (|01⟩ − |10⟩)/√2      C = (1/√2)[[0, 1],[−1, 0]]
```

**The computation.** In each case `C` is `1/√2` times a unitary matrix, so `CC† = I/2`. Since `ρ_A = CC†` and the Schmidt coefficients are the singular values of `C`:

```
ρ_A = ρ_B = I/2,     λ₁ = λ₂ = 1/√2,     Schmidt rank = 2
```

Verified numerically for all four: singular values `(0.707107, 0.707107)`, `ρ_A = [[0.5, 0],[0, 0.5]]`, entanglement entropy

`S(ρ_A) = −Σ λᵢ² log₂ λᵢ² = −2(½ log₂ ½) = 1` bit

for every one of the four ✓.

**Why 1 bit is "maximal".** For a bipartite pure state of two qubits, `S(ρ_A) ≤ log₂(dim H_A) = log₂ 2 = 1`, with equality iff `ρ_A = I/2`, i.e. iff all Schmidt coefficients are equal. The Bell states saturate it, so they are maximally entangled — and equivalently, each half alone is maximally mixed and carries zero information.

**A second argument, no computation required.** The four states are related by *local* unitaries:

`|Φ⁻⟩ = (Z⊗I)|Φ⁺⟩`, `|Ψ⁺⟩ = (X⊗I)|Φ⁺⟩`, `|Ψ⁻⟩ = (XZ⊗I)|Φ⁺⟩` (up to a global sign)

Entanglement is invariant under local unitaries — `ρ_A ↦ Uρ_AU†` leaves the spectrum, hence `S`, unchanged — so if `|Φ⁺⟩` is maximally entangled, all four are. (Cross-ref `docs/02_quantum_mechanics/04_entanglement_and_nonlocality.md`, where the same table drives superdense coding.)

**What "1 ebit" buys.** One Bell pair plus two classical bits teleports one qubit; one Bell pair plus one qubit of communication sends two classical bits (superdense coding); one Bell pair maximally violates CHSH at `2√2`. The four states are also an orthonormal basis of `ℂ⁴`, so a Bell measurement is a legitimate projective measurement — the one Alice performs in teleportation.

</details>

- Find the Schmidt decomposition of `(|00⟩ + |01⟩ + |10⟩ − |11⟩)/2`

<details><summary>Solution</summary>

**Group by the first qubit** — for two qubits this is usually faster than running an SVD:

```
(|00⟩ + |01⟩ + |10⟩ − |11⟩)/2 = ½[ |0⟩(|0⟩ + |1⟩) + |1⟩(|0⟩ − |1⟩) ]
                               = (1/√2)[ |0⟩|+⟩ + |1⟩|−⟩ ]
```

(verified numerically). The A-side vectors `{|0⟩, |1⟩}` are orthonormal and so are the B-side vectors `{|+⟩, |−⟩}`, which is exactly the defining property of a Schmidt decomposition. Hence

```
|ψ⟩ = λ₁|a₁⟩|b₁⟩ + λ₂|a₂⟩|b₂⟩   with   λ₁ = λ₂ = 1/√2,
      |a₁⟩ = |0⟩, |b₁⟩ = |+⟩,  |a₂⟩ = |1⟩, |b₂⟩ = |−⟩
```

**Cross-check via the SVD.** The coefficient matrix is

`C = ½[[1, 1],[1, −1]] = H/√2`

`H` is unitary, so all its singular values are 1, and those of `C` are `1/√2, 1/√2` — confirmed numerically (`[0.70710678, 0.70710678]`). The Schmidt coefficients are the singular values of `C`, matching the decomposition above.

**Entanglement.** Schmidt rank 2 (> 1) `⟹` entangled. Equivalently `det C = ¼(−1 − 1) = −½ ≠ 0`, the rank-1 test failing — the same conclusion reached in Exercise 1 of `docs/01_mathematical_foundations/03_tensor_products_and_multipartite_systems.md`. The reduced state is

`ρ_A = CC† = I/2`,  so  `S(ρ_A) = 1` bit

— the state is **maximally** entangled, not merely entangled.

**The slick way to see it.** Apply `I ⊗ H` to `|Φ⁺⟩`:

`(I ⊗ H)|Φ⁺⟩ = (|0⟩H|0⟩ + |1⟩H|1⟩)/√2 = (|0⟩|+⟩ + |1⟩|−⟩)/√2 = |ψ⟩`

A local unitary on one half of a Bell pair — and local unitaries cannot change entanglement, so `|ψ⟩` is maximally entangled with `S = 1` bit, as computed. Every maximally entangled two-qubit state arises this way, as `(U ⊗ V)|Φ⁺⟩`.

**General recipe.** For an arbitrary bipartite state: write the coefficient matrix `C`, take `C = UΣV†`; the Schmidt coefficients are the diagonal of `Σ`, `|aₖ⟩` is the `k`-th column of `U`, and `|bₖ⟩` is the complex conjugate of the `k`-th column of `V`. The number of non-zero singular values is the Schmidt rank, and the state is a product iff that rank is 1.

</details>

- Compute entanglement entropy for `|Φ⁺⟩`

<details><summary>Solution</summary>

**Reduced state.** Tracing out qubit B from `|Φ⁺⟩⟨Φ⁺| = ½(|00⟩⟨00| + |00⟩⟨11| + |11⟩⟨00| + |11⟩⟨11|)`, the cross terms vanish because `⟨1|0⟩ = 0`, leaving

`ρ_A = ½(|0⟩⟨0| + |1⟩⟨1|) = I/2`

(verified numerically; same for `ρ_B`).

**Entropy.** `S(ρ) = −Tr(ρ log₂ ρ) = −Σᵢ λᵢ log₂ λᵢ` over the eigenvalues. Here `λ₁ = λ₂ = ½`:

```
S(ρ_A) = −(½ log₂ ½ + ½ log₂ ½) = −(½·(−1) + ½·(−1)) = 1 bit
```

Equivalently from the Schmidt coefficients `λᵢ = 1/√2`: `S = −Σ λᵢ² log₂ λᵢ² = 1` ✓. `S(ρ_A) = S(ρ_B)` always for a pure global state, because the two reduced states share the same non-zero spectrum (the squared Schmidt coefficients).

**Interpretation.**

- `S = 1` is the maximum for a qubit (`S ≤ log₂ d = 1`), so `|Φ⁺⟩` is maximally entangled. One unit of `S` is called one **ebit** — the standard currency of entanglement: one ebit plus two classical bits teleports a qubit, and entanglement distillation is measured in ebits per copy.
- The global state is pure, `S(ρ_AB) = 0`, while the subsystem has `S(ρ_A) = 1 > 0`. **The part is more disordered than the whole** — impossible for classical probability distributions, where `H(A) ≤ H(A,B)`. This inequality violation is arguably the cleanest single signature of entanglement, and the conditional entropy `S(A|B) = S(AB) − S(B) = −1` is negative, which is exactly the resource counted by state merging.

**Contrast and interpolation.** A product state `|0⟩⊗|+⟩` has `ρ_A = |0⟩⟨0|` pure, so `S = 0`. The one-parameter family `cos α|00⟩ + sin α|11⟩` has `ρ_A = diag(cos²α, sin²α)` and

`S = H₂(cos²α) = −cos²α log₂ cos²α − sin²α log₂ sin²α`

which runs continuously from 0 (product, `α = 0`) to 1 (`α = π/4`, the Bell state). For pure bipartite states this single number is a complete entanglement measure; for mixed states it is not, and one needs entanglement of formation, negativity, or distillable entanglement instead.

</details>

---

## Module 6 — Open Quantum Systems and Decoherence

**Objective:** Understand how real quantum systems interact with their environment — the source of noise in quantum computers.

| Topic | Key Concepts |
|---|---|
| Open systems | System + environment; environment is traced out |
| Lindblad master equation | `dρ/dt = −i[H,ρ] + Σ (LᵢρLᵢ† − ½{Lᵢ†Lᵢ,ρ})` |
| Jump operators Lᵢ | Describe specific noise channels |
| Bit flip channel | `ρ → (1−p)ρ + p XρX` |
| Phase flip channel | `ρ → (1−p)ρ + p ZρZ` |
| Depolarizing channel | Mixes with maximally mixed state |
| T1 and T2 times | Relaxation and dephasing — hardware specifications |
| Kraus operators | Any channel: `ε(ρ) = Σ KᵢρKᵢ†`, `ΣKᵢ†Kᵢ = I` |

**Exercises:**
- Show that the bit flip channel is trace-preserving and completely positive

<details><summary>Solution</summary>

The channel is `ε(ρ) = (1−p)ρ + p XρX` with `0 ≤ p ≤ 1`. Its Kraus operators are

`K₀ = √(1−p) I`,  `K₁ = √p X`

so that `ε(ρ) = K₀ρK₀† + K₁ρK₁†`.

**Trace preserving.** The condition is `Σᵢ Kᵢ†Kᵢ = I`:

`K₀†K₀ + K₁†K₁ = (1−p)I† I + p X†X = (1−p)I + pI = I` ✓

(verified numerically at `p = 0.35`). Then for any `ρ`,

`Tr ε(ρ) = Tr(Σᵢ KᵢρKᵢ†) = Tr(ρ Σᵢ Kᵢ†Kᵢ) = Tr(ρ)`

using cyclicity. So probabilities stay normalized.

**Completely positive — general argument.** Any map with a Kraus representation is CP. Positivity: for `ρ ≥ 0` and any `|v⟩`, `⟨v|KρK†|v⟩ = ⟨K†v|ρ|K†v⟩ ≥ 0`, and a sum of positive operators is positive. Complete positivity means `ε ⊗ id_d` is positive for every ancilla dimension `d`; but `(ε ⊗ id)(σ) = Σᵢ (Kᵢ ⊗ I)σ(Kᵢ ⊗ I)†`, which is again of the same form, hence positive. The tensoring changes nothing structural — that is the whole point of the Kraus form.

**Completely positive — direct Choi check.** By Choi's theorem, `ε` is CP iff the Choi matrix `J(ε) = Σ_{ij} |i⟩⟨j| ⊗ ε(|i⟩⟨j|)` is positive semi-definite. Computed numerically at `p = 0.35`, its eigenvalues are

`{0, 0, 2p, 2(1−p)} = {0, 0, 0.7, 1.3}`

all non-negative ✓, so `ε` is CP. (Positivity alone would not have sufficed: the transpose map `ρ ↦ ρᵀ` is positive but has a Choi matrix with a negative eigenvalue, hence is not CP — and that failure is precisely the PPT entanglement criterion.)

**Bloch action.** Using `XXX = X`, `XYX = −Y`, `XZX = −Z`:

`r = (r_x, r_y, r_z) ↦ (r_x, (1−2p)r_y, (1−2p)r_z)`

The `x` component is untouched (a bit-flip error commutes with `X`), while the other two shrink by `1 − 2p`: the Bloch ball is squashed into an ellipsoid of revolution about the `x`-axis. At `p = ½` it collapses to the `x`-axis segment — maximal decoherence — and at `p = 1` the channel is the unitary `X`, which is a rotation, not a contraction. Being CPTP is exactly the requirement that makes this a physically realizable process: by Stinespring it can always be implemented as a unitary on system + environment followed by tracing out the environment.

</details>

- Derive the Kraus operators for the depolarizing channel

<details><summary>Solution</summary>

Start from the corpus definition (`docs/02_quantum_mechanics/05_density_matrices_and_open_systems.md`): with probability `1−p` nothing happens, and with probability `p` a *uniformly random* Pauli including the identity is applied:

`ε(ρ) = (1−p)ρ + (p/4)(IρI + XρX + YρY + ZρZ)`

**Simplify using the Pauli twirl identity.** For a single qubit,

`XρX + YρY + ZρZ = 2I·Tr(ρ) − ρ = 2I − ρ`  (for `Tr ρ = 1`)

so

`ε(ρ) = (1−p)ρ + (p/4)(ρ + 2I − ρ) = (1−p)ρ + p·(I/2)`

— the channel mixes the input with the maximally mixed state, which is the form the name refers to.

**Read off the Kraus operators.** Collect the two `IρI` contributions: `(1−p) + p/4 = 1 − 3p/4`. Hence

```
K₀ = √(1 − 3p/4) · I
K₁ = √(p/4) · X
K₂ = √(p/4) · Y
K₃ = √(p/4) · Z
```

**Trace preservation.** Since `X² = Y² = Z² = I`,

`Σᵢ Kᵢ†Kᵢ = (1 − 3p/4)I + 3·(p/4)I = I` ✓

Verified numerically at `p = 0.4`, together with the equality `Σ KᵢρKᵢ† = (1−p)ρ + pI/2` ✓.

**Bloch action.** Each Pauli conjugation flips the two Bloch components orthogonal to its own axis, so `(XρX + YρY + ZρZ)/3` corresponds to `r ↦ −r/3`; feeding that into the definition — or reading it straight off `ε(ρ) = (1−p)ρ + pI/2` — gives

`r ↦ (1 − p) r`

a uniform contraction toward the centre — the only channel that treats all axes alike. Numerically at `p = 0.4` with `r = (0.3, 0.4, 0.5)`, the output Bloch vector is `(0.18, 0.24, 0.30) = 0.6 r` ✓. The channel is a valid CPTP map for `0 ≤ p ≤ 1`, and at `p = 1` it maps every state to `I/2`.

**The other convention.** Many papers apply a *non-trivial* Pauli with total probability `p`, each of `X, Y, Z` with probability `p/3`:

`ε'(ρ) = (1−p)ρ + (p/3)(XρX + YρY + ZρZ)`,  Kraus `{√(1−p)I, √(p/3)X, √(p/3)Y, √(p/3)Z}`

with Bloch action `r ↦ (1 − 4p/3)r` and complete depolarization already at `p = 3/4`. The two are related by `p_mixed = 4p_Pauli/3` — always check which one a quoted error rate uses.

**Generalization.** For `n` qubits, `ε(ρ) = (1−p)ρ + p I/2ⁿ` has `4ⁿ` Kraus operators, one per Pauli string: `K₀ = √(1 − p(4ⁿ−1)/4ⁿ) I` and `K_P = √(p/4ⁿ) P` for each non-identity string. The depolarizing channel is the standard worst-case noise model in threshold theorems precisely because Pauli twirling turns *any* channel into a depolarizing one with the same average fidelity.

</details>

- Compute how Bloch vector components decay under dephasing noise

<details><summary>Solution</summary>

**Discrete channel.** The phase-flip (dephasing) channel is `ε(ρ) = (1−p)ρ + p ZρZ`, with Kraus operators `√(1−p)I` and `√p Z` (`Σ Kᵢ†Kᵢ = (1−p)I + pI = I` ✓). Write `ρ = (I + r·σ)/2` and use

`ZXZ = −X`,  `ZYZ = −Y`,  `ZZZ = Z`

Then

```
ε(ρ) = ½[ I + (1−p)(r_x X + r_y Y + r_z Z) + p(−r_x X − r_y Y + r_z Z) ]
```

so

```
r ↦ ( (1−2p) r_x, (1−2p) r_y, r_z )
```

The transverse (coherence) components shrink by `1 − 2p`; the longitudinal (population) component is untouched. Verified numerically at `p = 0.3` with `r = (0.3, 0.4, 0.5)`: the output is `(0.12, 0.16, 0.50)`, and `1 − 2p = 0.4` ✓. At `p = ½` the channel is *completely* dephasing, `r ↦ (0, 0, r_z)` — exactly the non-selective `Z` measurement of Module 3.

**Continuous time (Lindblad).** With jump operator `L = √(γ_φ/2) Z` (corpus convention, `docs/02_quantum_mechanics/10_distance_measures_and_lindblad.md`), the dissipator is

`D[L]ρ = LρL† − ½{L†L, ρ} = (γ_φ/2)(ZρZ − ρ)`

Acting on the Bloch components:

```
dr_x/dt = −γ_φ r_x        dr_y/dt = −γ_φ r_y        dr_z/dt = 0
```

Hence `r_⊥(t) = r_⊥(0) e^{−t/T_φ}` with `1/T_φ = γ_φ`, and the populations never move. Matching to the discrete channel over a step of duration `t` gives `1 − 2p = e^{−γ_φ t}`, i.e. `p = (1 − e^{−t/T_φ})/2`.

**With relaxation as well.** Adding amplitude damping `L = √γ σ₋` (rate `γ = 1/T₁`) gives the full hardware picture:

```
r_z(t) = r_z^{eq} + (r_z(0) − r_z^{eq}) e^{−t/T₁}
r_⊥(t) = r_⊥(0) e^{−t/T₂},      1/T₂ = 1/(2T₁) + 1/T_φ
```

Relaxation necessarily dephases (a decayed qubit has lost its phase), contributing the `1/(2T₁)`; pure dephasing adds on top. Since `T_φ ≥ 0`, this yields the universal bound `T₂ ≤ 2T₁`.

**Why it matters for computing.** Dephasing destroys superpositions while leaving computational-basis populations intact: the equator of the Bloch sphere collapses toward the `z`-axis. So a bit-flip code, which measures `Z`-type stabilizers, is entirely blind to it — the `[[3,1,1]]` code has `d = 1` against `Z` errors — and correcting phase errors requires the conjugate code (`X`-type stabilizers) or a code like Steane's that handles both. Operationally, dephasing is what limits Ramsey fringe contrast, and dynamical decoupling (`X`-pulse echo sequences) suppresses the low-frequency part of it by periodically reversing the accumulated phase.

</details>

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Principles of Quantum Mechanics* — Shankar | Textbook | Clear, rigorous, excellent for physicists |
| *Introduction to Quantum Mechanics* — Griffiths | Textbook | Accessible starting point |
| *Quantum Computation and Quantum Information* Ch.2 — Nielsen & Chuang | Textbook | The computing-focused treatment |
| *The Theory of Open Quantum Systems* — Breuer & Petruccione | Textbook | Deep dive into noise and channels |
| Preskill's lecture notes (Caltech) | Notes | Free, comprehensive |

---

## Progression Checkpoints

- [ ] State and apply all four postulates without reference
- [ ] Fluently work with the Bloch sphere and single-qubit rotations
- [ ] Compute measurement probabilities for any state and any observable
- [ ] Derive `e^(−iHt)` for qubit Hamiltonians using Pauli decomposition
- [ ] Compute Schmidt decompositions and entanglement entropy
- [ ] Write down Kraus operators for standard noise channels
