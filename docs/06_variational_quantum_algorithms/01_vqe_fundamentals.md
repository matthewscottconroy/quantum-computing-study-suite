# VQE Fundamentals

> **Prerequisites**: Quantum mechanics postulates (Chapter 2), Pauli operators and Hamiltonians,
> basic optimization concepts
> **Connects to**: Ansatz design (06/02), parameter shift gradient (06/03), QAOA (06/04),
> many-body physics simulation (08/03)

---

## Overview

The Variational Quantum Eigensolver (VQE) is the foundational near-term quantum algorithm for
quantum chemistry and condensed matter simulation. Proposed by Peruzzo et al. in 2014, VQE
hybridizes a quantum computer — which prepares parameterized quantum states and measures
Hamiltonian expectation values — with a classical computer that optimizes the parameters to
minimize energy. The algorithm exploits the **variational principle** from quantum mechanics:
any trial state gives an energy expectation value that is an upper bound on the true ground-state
energy.

VQE was a paradigm shift for the NISQ (Noisy Intermediate-Scale Quantum) era. Rather than
requiring perfect, fault-tolerant quantum computation, VQE uses shallow quantum circuits to
prepare trial states and reduces the quantum computation burden by delegating the optimization
loop to a classical computer. Whether VQE will achieve quantum advantage for practically relevant
chemical systems remains an open question, but it has driven enormous progress in quantum
hardware characterization, algorithmic design, and our understanding of the boundary between
easy and hard quantum simulations.

This chapter covers the variational principle, the VQE algorithm structure, Hamiltonian encoding
via Pauli decomposition and fermion-to-qubit mappings, the UCCSD ansatz for quantum chemistry,
and a clear-eyed assessment of VQE's capabilities and limitations.

---

## The Variational Principle

### Statement

For any quantum system with Hamiltonian `H` and ground-state energy `E₀` (lowest eigenvalue):

```
⟨ψ|H|ψ⟩ ≥ E₀   for all normalized states |ψ⟩
```

with equality if and only if `|ψ⟩` is a ground state of `H`.

**Proof**: Let `{|Eₖ⟩}` be the orthonormal eigenstates of `H` with eigenvalues `E₀ ≤ E₁ ≤ E₂ ≤ ...`.
Any state expands as `|ψ⟩ = Σₖ cₖ|Eₖ⟩` with `Σₖ|cₖ|² = 1`. Then:
```
⟨ψ|H|ψ⟩ = Σₖ |cₖ|² Eₖ ≥ E₀ Σₖ |cₖ|² = E₀
```
Equality holds when `|c₀|² = 1` (i.e., `|ψ⟩ = e^{iφ}|E₀⟩`). QED.

### VQE Formulation

Let `|ψ(θ)⟩` be a parameterized quantum state with classical parameter vector
`θ ∈ ℝ^m`. Define the **cost function**:

```
E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩
```

VQE minimizes `E(θ)` over `θ`:

```
θ* = argmin_θ E(θ),   E₀ ≈ E(θ*)
```

The quality of the approximation depends on whether the true ground state lies within (or close
to) the family of states `{|ψ(θ)⟩ : θ ∈ ℝ^m}`. This is the **expressibility** requirement
on the ansatz.

---

## The VQE Algorithm Loop

The VQE algorithm alternates between quantum and classical steps:

```
Initialization: choose starting parameters θ⁰

Loop:
  1. [Quantum] Prepare |ψ(θ)⟩ on the quantum computer
  2. [Quantum] Measure ⟨H⟩ = Σ_i c_i ⟨P_i⟩ (Pauli decomposition; see below)
  3. [Classical] Evaluate E(θ) = Σ_i c_i ⟨P_i⟩
  4. [Classical] Compute or estimate ∂E/∂θ
  5. [Classical] Update θ ← θ - η ∇E(θ)  (or use a more sophisticated optimizer)

Until convergence: |E(θ^{t+1}) - E(θ^t)| < ε

Output: θ*, E* = E(θ*)
```

The quantum circuit prepares `|ψ(θ)⟩` using parameterized gates (Rx, Ry, Rz rotations
with trainable angles), and the quantum computer measures expectation values of individual
Pauli strings. The classical optimizer updates the parameters.

---

## Hamiltonian as a Pauli Sum

### Pauli Decomposition

Any Hermitian operator `H` on `n` qubits can be written as a sum of Pauli strings:

```
H = Σ_{P ∈ Pₙ} c_P · P,   c_P = (1/2^n) Tr[PH]
```

For a molecular electronic structure Hamiltonian in second quantization with `N` spin-orbitals,
the number of non-zero terms in the Pauli decomposition is at most `O(N⁴)` (though often
significantly fewer in practice due to symmetry).

**Measuring `⟨H⟩`**: Since `⟨H⟩ = Σ_P c_P ⟨P⟩`, one estimates each `⟨P_i⟩` separately by
rotating into the appropriate measurement basis and sampling. Paulis that commute can be
measured simultaneously in a single circuit execution (grouped measurements).

### Example: Hydrogen Molecule H₂

The simplest non-trivial molecular system is H₂ in a minimal basis (STO-3G). After a parity
(Bravyi-Kitaev-style) mapping and symmetry reduction to 2 qubits, at bond length `R = 0.735 Å`:

```
H_H₂ = -1.052373 I + 0.397937 Z₁ - 0.397937 Z₂ - 0.011280 Z₁Z₂ + 0.180931 X₁X₂
```

(coefficients in Hartree). Diagonalizing this 4×4 matrix gives the exact **electronic**
ground-state energy `E₀ = -1.857274` Ha. Adding the fixed nuclear repulsion energy
`E_nuc = +0.719969` Ha gives the total energy `E_total = -1.137306` Ha — the familiar
H₂ ground-state energy. (Different fermion-to-qubit mappings produce different-looking
Pauli sums with identical spectra.)

---

## Fermion-to-Qubit Mappings

Molecular Hamiltonians are naturally expressed in terms of fermionic operators `{cᵢ, cⱼ†}` with
anticommutation relations `{cᵢ, cⱼ†} = δᵢⱼ`. Qubits are bosonic (commuting). Mapping fermionic
operators to qubit operators requires a non-trivial transformation.

### Jordan-Wigner (JW) Transformation

The JW mapping associates each spin-orbital `j` with one qubit:

```
cⱼ = (⊗_{k<j} Z_k) ⊗ (X_j + iY_j)/2
cⱼ† = (⊗_{k<j} Z_k) ⊗ (X_j - iY_j)/2
```

The `Z_{k<j}` "string" encodes the Jordan-Wigner phase that ensures fermionic anticommutation.

**Cost**: A single fermionic operator `cⱼ` becomes a weight-`j` Pauli string (acting on all
qubits `1` through `j`). Two-electron operators (quartic in `c`s) become weight up to `2j`
Pauli strings. The Hamiltonian has `O(N⁴)` terms each of weight `O(N)` under JW.

### Bravyi-Kitaev (BK) Transformation

The BK mapping interleaves qubit and occupation-number representations to reduce the average
Pauli weight from `O(N)` to `O(log N)`:

```
H_BK = O(N⁴) terms, average weight O(log N)
```

For large systems, BK significantly reduces the circuit depth required to implement each
Hamiltonian term, an important practical advantage.

### Parity Mapping and Tapering

Additional symmetry reductions can further compress the qubit count. If the Hamiltonian conserves
particle number and spin, two qubits can be "tapered off" (removed), reducing the qubit count by
`2`. For H₂ in a minimal basis: 4 spin-orbitals → 4 qubits → taper 2 → **2 qubits** (as
above).

---

## The UCCSD Ansatz

### Unitary Coupled Cluster Theory

Coupled cluster theory is one of the most accurate methods in quantum chemistry. The standard
unitary coupled cluster singles and doubles (UCCSD) ansatz is:

```
|ψ_UCCSD(θ)⟩ = e^{T(θ) - T†(θ)} |ψ_ref⟩
```

where `|ψ_ref⟩` is a reference state (usually the Hartree-Fock state), and `T = T₁ + T₂` is
the cluster operator:

```
T₁ = Σ_{ia} θᵢᵃ cₐ† cᵢ          (single excitations: electron from orbital i to a)
T₂ = Σ_{ijab} θᵢⱼᵃᵇ cₐ† c_b† cⱼ cᵢ  (double excitations)
```

The anti-Hermitian combination `T - T†` ensures the unitary `U = e^{T-T†}` is unitary.

### Implementation on a Quantum Computer

Each Pauli term in the decomposition of `T - T†` is exponentiated separately (Trotterization):

```
U(θ) ≈ ∏_k exp(θk Pₖ)
```

Each exponential `exp(θ Pₖ)` for a Pauli string `Pₖ` is implemented as a rotation gate with
appropriate CNOT ladders. For UCCSD with `N` spin-orbitals:
- Number of parameters: `O(N²)` singles + `O(N⁴)` doubles ≈ `O(N⁴)`.
- Circuit depth: `O(N³)` to `O(N⁴)` two-qubit gates.

### Scaling Issues

For `N` spin-orbitals (typically `N = 2×(number of electrons)` in minimal basis):

| System | N | UCCSD parameters | Circuit depth |
|--------|---|-----------------|---------------|
| H₂ (minimal) | 4 | 3 | ~50 CNOT |
| H₂O (STO-3G) | 14 | ~72 | ~500 CNOT |
| FeMoco (minimal) | 54 | ~thousands | ~millions CNOT |

FeMoco (the active site of nitrogenase, involved in nitrogen fixation) is a target application
requiring ~100+ qubits; at current error rates, this is far beyond NISQ-era capabilities.

---

## Chemical Accuracy

Chemical accuracy is defined as energy error less than `1 kcal/mol = 1.594 mHartree ≈ 4.34 × 10^{-2} eV`.

This is the threshold at which quantum chemistry predictions become useful for reaction rate
calculations. Achieving chemical accuracy with VQE requires:
1. Sufficiently expressive ansatz to capture the electron correlation energy.
2. Sufficient measurement shots to reduce statistical uncertainty of `⟨H⟩` below 1.6 mHartree.
3. Optimization converged to within chemical accuracy of the global minimum.

For a Hamiltonian with `M` Pauli terms, each measured with `S` shots, the statistical error is:
```
σ²(E) = Σ_i c_i² Var(⟨Pᵢ⟩) ≤ M/(4S) · (Σ_i |cᵢ|)²
```

For chemical accuracy `σ(E) < 1.6 × 10^{-3}` Hartree on a 10-qubit system with `M ~ 100`
terms and `|Σ cᵢ| ~ 1`: need `S ~ M / (4σ²) ~ 100 × (1.6×10^{-3})^{-2} / 4 ~ 10^7` shots.

This shot overhead is a significant practical limitation of VQE.

---

## Classical Simulation and Limitations

VQE cannot achieve quantum advantage for systems efficiently simulable classically:

- **1D systems**: Matrix Product States (MPS) and DMRG can solve 1D quantum systems with modest
  bond dimensions efficiently. VQE has no advantage here.
- **Weakly correlated systems**: Hartree-Fock or perturbation theory (MP2) is sufficient.
- **High symmetry**: Group theory reduces the problem size dramatically.

Quantum advantage targets are systems with:
1. High entanglement (large bond dimension in MPS).
2. In 2D or 3D geometry.
3. Strongly correlated (large U/t in Hubbard models or multi-reference character in chemistry).

---

## Key Formulas

- **Variational principle**: `E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀`
- **Pauli decomposition**: `H = Σ_P c_P P`, `c_P = Tr[PH]/2^n`
- **JW transformation**: `cⱼ = (⊗_{k<j} Zₖ) · (Xⱼ + iYⱼ)/2`
- **UCCSD ansatz**: `|ψ(θ)⟩ = exp(T(θ) - T†(θ))|ψ_ref⟩`
- **Measurement variance**: `Var(E) ≤ (Σ_i |c_i|)² M / (4S)` (M terms, S shots)
- **Chemical accuracy**: `|ΔE| < 1.6 mHartree = 1 kcal/mol`

---

## Worked Example: H₂ VQE by Hand

**Hamiltonian** (the 2-qubit reduced H₂ Hamiltonian from above, at `R = 0.735 Å`):
```
H = -1.052373 I + 0.397937 Z₁ - 0.397937 Z₂ - 0.011280 Z₁Z₂ + 0.180931 X₁X₂
```

**Exact diagonalization** (do this first, so we know the answer): `H` is block-diagonal in the
subspaces `span{|00⟩, |11⟩}` and `span{|01⟩, |10⟩}` (the diagonal terms preserve each pair,
and `X₁X₂` couples `|00⟩ ↔ |11⟩` and `|01⟩ ↔ |10⟩`). Diagonalizing the two 2×2 blocks gives
eigenvalues `{-1.857274, -1.244584, -0.882722, -0.224912}` Ha, so:
```
E₀ = -1.857274 Ha   (ground state lies in the {|01⟩, |10⟩} block)
```
The Hartree-Fock state is `|HF⟩ = |10⟩` with `E_HF = ⟨10|H|10⟩ = -1.836968` Ha; the
correlation energy is `E₀ - E_HF = -20.3` mHa.

**Ansatz** (1 parameter, prepared with an X gate, one Ry, and one CNOT):
```
|ψ(θ)⟩ = CNOT_{1→2} · (Ry(θ)₁ ⊗ I₂) · |01⟩ = cos(θ/2)|01⟩ + sin(θ/2)|10⟩
```
Operators act right-to-left: starting from `|01⟩ = X₂|00⟩`, first `Ry(θ)` rotates qubit 1
(`cos(θ/2)|01⟩ + sin(θ/2)|11⟩`), then the CNOT maps `|11⟩ → |10⟩`. At `θ = π` this is the
Hartree-Fock state `|10⟩`; the ansatz explores the two-dimensional block that contains the
ground state.

**Energy function** (for `|ψ(θ)⟩ = cos(θ/2)|01⟩ + sin(θ/2)|10⟩`):
```
⟨Z₁⟩ = cos²(θ/2) - sin²(θ/2) = cosθ
⟨Z₂⟩ = -cos²(θ/2) + sin²(θ/2) = -cosθ
⟨Z₁Z₂⟩ = -1                       (both |01⟩ and |10⟩ have anti-aligned spins)
⟨X₁X₂⟩ = 2cos(θ/2)sin(θ/2) = sinθ  (X₁X₂|01⟩ = |10⟩)
```

**E(θ):**
```
E(θ) = -1.052373 + 0.397937 cosθ + 0.397937 cosθ + 0.011280 + 0.180931 sinθ
     = -1.041093 + 0.795874 cosθ + 0.180931 sinθ
```

**Minimizing**: writing `a cosθ + b sinθ = R cos(θ - φ)` with
`R = √(0.795874² + 0.180931²) = 0.816181`:
```
E_min = -1.041093 - 0.816181 = -1.857274 Ha   at θ* = π + arctan(0.180931/0.795874) ≈ 3.3651 rad
```

`E_min = E₀` to all digits shown: the variational principle holds with equality because this
one-parameter ansatz can reach the exact ground state (any real superposition in the
`{|01⟩, |10⟩}` block). Sanity checks: `E(π) = -1.836968` Ha recovers Hartree-Fock, and adding
`E_nuc = 0.719969` Ha gives the total energy `-1.137306` Ha.

**What an under-expressive ansatz does**: suppose we had instead used
`|ψ(θ)⟩ = CNOT_{1→2}(Ry(θ)₁ ⊗ I₂)|00⟩ = cos(θ/2)|00⟩ + sin(θ/2)|11⟩`. Repeating the
calculation gives `E(θ) = -1.063653 + 0.180931 sinθ`, minimized at `E = -1.244585` Ha —
exactly the lowest eigenvalue of the `{|00⟩, |11⟩}` block, but `0.61` Ha **above** `E₀`.
This is the correct lesson about expressivity: an ansatz that cannot reach the ground state
still obeys `E(θ) ≥ E₀` — it can only **over**estimate the ground-state energy, never
undershoot it. (If a VQE "result" ever comes out below the exact ground energy, the
Hamiltonian, the measurement, or the arithmetic is wrong — the variational principle leaves
no third option.)

---

## Summary

- VQE exploits the variational principle: any parameterized quantum state gives an upper bound
  on the ground-state energy; minimize this bound by optimizing circuit parameters.
- The quantum computer prepares `|ψ(θ)⟩` and measures Pauli expectation values;
  the classical computer minimizes `E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩`.
- Molecular Hamiltonians are mapped to qubit Hamiltonians via JW or BK transformations;
  the number of Pauli terms scales as `O(N⁴)`.
- UCCSD is the chemically motivated ansatz; it has `O(N⁴)` parameters and is classically
  intractable to evaluate directly for large `N`.
- Shot overhead and barren plateaus are key practical limitations; chemical accuracy requires
  `~10^6-10^8` circuit evaluations for realistic molecules.

---

## Exercises

**1.** A Hamiltonian has eigenvalues `{-2, -1, 0, +3}` (in some energy unit). A trial state has
overlap `|c₀|² = 0.9` with the ground state and `|c₁|² = 0.1` with the first excited state
(zero overlap with the rest). Compute `⟨H⟩` and confirm it satisfies the variational principle.
What is the lowest possible `⟨H⟩` over all states *orthogonal* to the ground state?

<details><summary>Solution</summary>

`⟨H⟩ = 0.9(-2) + 0.1(-1) = -1.9 ≥ E₀ = -2`. ✓

For states orthogonal to the ground state, `c₀ = 0`, so `⟨H⟩ = Σ_{k≥1}|cₖ|²Eₖ ≥ E₁ = -1`,
with equality for the first excited state. This is the basis of variational methods for excited
states (deflation): minimizing over the orthogonal complement of `|E₀⟩` yields `E₁`.

</details>

**2.** Decompose the single-qubit Hamiltonian `H = [[1, 0], [0, -3]]` into Pauli operators
using `c_P = Tr[PH]/2`.

<details><summary>Solution</summary>

`c_I = Tr[H]/2 = (1 - 3)/2 = -1`, `c_Z = Tr[ZH]/2 = (1 + 3)/2 = 2`, `c_X = c_Y = 0`
(H is diagonal, and `X`, `Y` have zero diagonal). So `H = -I + 2Z`.
Check: `-I + 2Z = [[-1+2, 0], [0, -1-2]] = [[1, 0], [0, -3]]`. ✓

</details>

**3.** For the worked example's ansatz `|ψ(θ)⟩ = cos(θ/2)|01⟩ + sin(θ/2)|10⟩` and the 2-qubit
H₂ Hamiltonian, evaluate `E(θ)` at `θ = 0`, `θ = π/2`, and `θ = π`. Which of these is the
Hartree-Fock energy, and why is `θ = π/2` (the maximally entangled state) *not* optimal?

<details><summary>Solution</summary>

Using `E(θ) = -1.041093 + 0.795874 cosθ + 0.180931 sinθ`:

- `E(0) = -1.041093 + 0.795874 = -0.245219 Ha` (this is `⟨01|H|01⟩`, a highly excited configuration)
- `E(π/2) = -1.041093 + 0.180931 = -0.860162 Ha`
- `E(π) = -1.041093 - 0.795874 = -1.836968 Ha` = `E_HF` (the state is `|10⟩ = |HF⟩`)

The optimum `θ* ≈ 3.365` is close to `π`: the true ground state is mostly Hartree-Fock with a
small admixture of `|01⟩` (amplitude ≈ 0.11). Entanglement in VQE is a resource to be dosed by
the Hamiltonian, not maximized for its own sake — the Bell state at `θ = π/2` grossly
over-rotates and lands `~1 Ha` above the ground state.

</details>

**4.** You estimate the term `0.180931 X₁X₂` by measuring `X₁X₂` (eigenvalues `±1`) with `S`
shots. Using `Var(⟨X₁X₂⟩) ≤ 1/S`, how many shots guarantee the statistical error of this
term's energy contribution is below chemical accuracy (`1.6 mHa`)?

<details><summary>Solution</summary>

The term's standard error is `σ = |c| · σ(⟨X₁X₂⟩) ≤ 0.180931/√S`. Requiring
`0.180931/√S < 1.6 × 10⁻³` gives `S > (0.180931/0.0016)² ≈ 1.28 × 10⁴` shots — about 13,000
shots for one Pauli term of one energy evaluation. Multiply by the number of terms and the
number of optimizer iterations to see why VQE shot budgets reach `10⁶-10⁸` quickly.

</details>

---

## Further Reading

1. **Peruzzo, A. et al.** — "A variational eigenvalue solver on a photonic chip," *Nature
   Communications* 5, 4213 (2014). The original VQE paper.
2. **Romero, J. et al.** — "Strategies for quantum computing molecular energies using the
   unitary coupled cluster ansatz," *Quantum Sci. Technol.* 4, 014008 (2019).
3. **McArdle, S. et al.** — "Quantum computational chemistry," *Rev. Mod. Phys.* 92, 015003
   (2020). Comprehensive review of quantum chemistry on quantum computers.
4. **Cerezo, M. et al.** — "Variational quantum algorithms," *Nature Reviews Physics* 3, 625
   (2021). Broad overview of VQAs beyond VQE.
5. **Bravyi, S. B. and Kitaev, A. Yu.** — "Fermionic quantum computation," *Ann. Phys.* 298,
   210 (2002). Bravyi-Kitaev transformation for improved qubit efficiency.
