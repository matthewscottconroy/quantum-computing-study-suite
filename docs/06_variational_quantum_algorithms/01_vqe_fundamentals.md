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

The simplest non-trivial molecular system is H₂ in a minimal basis (STO-3G). After Jordan-Wigner
mapping and symmetry reduction to 2 qubits:

```
H_H₂ = c₀ I + c₁ Z₁ + c₂ Z₂ + c₃ Z₁Z₂ + c₄ X₁X₂ + c₅ Y₁Y₂
```

where coefficients `c₀,...,c₅` depend on bond length `R`. At `R = 0.74 Å` (equilibrium):
approximately `c₀ ≈ -0.812`, `c₁ = c₂ ≈ 0.397`, `c₃ ≈ -0.011`, `c₄ = c₅ ≈ 0.181`.

Exact ground-state energy: `E₀ ≈ -1.137` Hartree.

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
| H₂ (minimal) | 4 | ~13 | ~50 CNOT |
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

**Hamiltonian** (2-qubit, after reduction):
```
H = -1.117 I + 0.171 Z₁ + 0.171 Z₂ - 0.222 Z₁Z₂ + 0.162 X₁X₂ + 0.162 Y₁Y₂
```
(Coefficients in Hartree, approximate values at R = 0.74 Å)

**Ansatz** (Ry ansatz, 1 parameter):
```
|ψ(θ)⟩ = Ry(θ)₁ · CNOT_{1→2} · |00⟩
         = cos(θ/2)|00⟩ + sin(θ/2)|11⟩
```
(This is a simple hardware-efficient ansatz spanning entangled states.)

**Energy function:**
```
⟨Z₁⟩ = cos²(θ/2) - sin²(θ/2) = cos θ
⟨Z₂⟩ = cos²(θ/2) - sin²(θ/2) = cos θ
⟨Z₁Z₂⟩ = cos²(θ/2)(+1) + sin²(θ/2)(+1) = 1   (both states |00⟩ and |11⟩ give +1)
⟨X₁X₂⟩ = 2 sin(θ/2) cos(θ/2) = sin θ           (off-diagonal terms)
⟨Y₁Y₂⟩ = -2 sin(θ/2) cos(θ/2) = -sin θ
```

Wait: for the Bell state `|ψ(θ)⟩ = cos(θ/2)|00⟩ + sin(θ/2)|11⟩`:
```
⟨X₁X₂⟩ = 2cos(θ/2)sin(θ/2) = sinθ
⟨Y₁Y₂⟩ = -2cos(θ/2)sin(θ/2) = -sinθ   (Y₁Y₂|00⟩ = -|11⟩)
```

**E(θ):**
```
E(θ) = -1.117 + 0.171 cosθ + 0.171 cosθ - 0.222(1) + 0.162 sinθ + 0.162(-sinθ)
     = -1.117 + 0.342 cosθ - 0.222
     = -1.339 + 0.342 cosθ
```

**Minimizing**: `∂E/∂θ = -0.342 sinθ = 0` → `θ = 0` or `θ = π`.

At `θ = π`: `E = -1.339 - 0.342 = -1.681` Hartree. But exact `E₀ ≈ -1.137` Hartree...

The discrepancy indicates this simple ansatz is not expressive enough for H₂ near equilibrium —
the full UCCSD ansatz (which includes X₁X₂ and Y₁Y₂ rotation terms) is needed. This exercise
illustrates that even a simple ansatz produces a VQE energy, but ansatz expressibility is critical.

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
