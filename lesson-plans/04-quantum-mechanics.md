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
- Compute the expected value `⟨Z⟩` for `|+⟩ = (|0⟩+|1⟩)/√2`
- Show that post-measurement states are renormalized projections

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
- Show that a general qubit rotation maps to a rotation of the Bloch sphere
- Find the Bloch vector of `ρ = I/2` (maximally mixed state)

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
- Design a POVM that distinguishes `|0⟩` and `|+⟩` with minimum error
- Derive the uncertainty relation for X and Z on a qubit

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
- Show that the Hadamard gate is `e^(iπ(X+Z)/2√2)` up to global phase
- Derive the first-order Trotter error bound

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
- Find the Schmidt decomposition of `(|00⟩ + |01⟩ + |10⟩ − |11⟩)/2`
- Compute entanglement entropy for `|Φ⁺⟩`

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
- Derive the Kraus operators for the depolarizing channel
- Compute how Bloch vector components decay under dephasing noise

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
