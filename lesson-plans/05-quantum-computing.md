# Quantum Computing

## Goal
Build a comprehensive, rigorous understanding of the quantum computing model — from circuits and complexity to error correction and fault tolerance — sufficient to understand, implement, and analyze quantum algorithms.

---

## Module 1 — The Quantum Circuit Model

**Objective:** Master the standard model of quantum computation — the framework in which all major algorithms are expressed.

| Topic | Key Concepts |
|---|---|
| Qubits and registers | n-qubit state in ℂ^(2ⁿ) |
| Single-qubit gates | X, Y, Z, H, S, T, Rₓ, Rᵧ, R_z, U |
| Two-qubit gates | CNOT, CZ, SWAP, iSWAP, CPhase |
| Three-qubit gates | Toffoli (CCNOT), Fredkin (CSWAP) |
| Circuit diagram conventions | Wires = qubits, boxes = gates, measurements |
| Gate depth and width | Circuit complexity metrics |
| Classical control | Conditioned gates, deferred measurement principle |

**Exercises:**
- Implement a circuit that prepares all four Bell states
- Show that Toffoli + ancilla can simulate any reversible classical computation
- Prove the deferred measurement principle

---

## Module 2 — Universality

**Objective:** Understand what it means for a gate set to be universal and which sets achieve it.

| Topic | Key Concepts |
|---|---|
| Universal gate set | Can approximate any unitary to arbitrary precision |
| Solovay-Kitaev theorem | {H, T, CNOT} is universal; approximation depth is O(log^c(1/ε)) |
| Clifford + T | Standard universal gate set in fault-tolerant contexts |
| Continuous vs discrete | Continuous parameter gates vs finite discrete sets |
| Entangling power | Why CNOT is needed alongside single-qubit gates |
| Gate synthesis | Decomposing arbitrary unitaries into gate sets |

**Exercises:**
- Decompose an arbitrary single-qubit gate using ZYZ decomposition
- Verify that {H, T} generates a dense subset of U(2)
- Count T gates in a given circuit (T-count optimization)

---

## Module 3 — Quantum Complexity Theory

**Objective:** Understand where quantum computers provide advantage — and where they don't.

| Class | Definition | Key Results |
|---|---|---|
| BQP | Efficiently solvable on a quantum computer | Factoring ∈ BQP |
| QMA | Quantum analog of NP | Local Hamiltonian problem is QMA-complete |
| QCMA | Classical witness, quantum verifier | |
| BPP | Classical efficient with randomness | BPP ⊆ BQP (suspected strict) |
| P | Classical deterministic polynomial time | P ⊆ BPP ⊆ BQP |
| PSPACE | Classical polynomial space | BQP ⊆ PSPACE |

| Separation | Status |
|---|---|
| P ≠ NP | Unproven |
| BPP ≠ BQP | Strongly suspected, unproven |
| BQP ⊄ PH | Evidence via oracle separations (Raz-Tal) |

**Exercises:**
- Place factoring, graph isomorphism, and unstructured search in complexity classes
- Explain why Grover's algorithm doesn't imply BQP ⊃ NP
- Describe the oracle separation between BQP and PH

---

## Module 4 — Quantum Error Correction

**Objective:** Understand how quantum information can be protected from noise without violating the laws of quantum mechanics.

| Topic | Key Concepts |
|---|---|
| No-cloning theorem | Cannot copy unknown quantum states |
| 3-qubit bit-flip code | Encode `|ψ⟩` as `|ψψψ⟩`, detect and correct single bit flips |
| 3-qubit phase-flip code | Hadamard basis, detect and correct phase errors |
| Shor's 9-qubit code | First full QEC code; corrects any single-qubit error |
| Stabilizer formalism | Code defined by abelian subgroup of Pauli group |
| Syndrome measurement | Projective measurement that identifies error without revealing state |
| CSS codes | Calderbank-Shor-Steane: built from two classical codes |
| Distance d code | Corrects ⌊(d−1)/2⌋ errors; detects d−1 errors |

**Exercises:**
- Verify the 3-qubit code detects (but doesn't correct) two bit-flip errors
- Find stabilizer generators and logical operators for the 7-qubit Steane code
- Compute the code distance of the 5-qubit perfect code

---

## Module 5 — Fault Tolerance

**Objective:** Understand how to perform reliable computation on imperfect hardware.

| Topic | Key Concepts |
|---|---|
| Fault tolerance threshold | Error rate below which error correction helps: ~10⁻³ |
| Transversal gates | Apply gate bitwise to each qubit in codeblock |
| Magic state distillation | Produce clean T-gate states from noisy ones |
| Concatenated codes | Recursively encode to suppress errors exponentially |
| Surface code | 2D local code, high threshold (~1%), leading practical candidate |
| Logical error rate | Error rate on encoded logical qubit |
| Overhead | Physical qubits per logical qubit (10²–10³ for surface code) |

**Exercises:**
- Show that a transversal CNOT on two [[7,1,3]] Steane blocks implements a logical CNOT
- Estimate the physical qubit overhead for a fault-tolerant T gate via magic state distillation
- Describe why Clifford gates cannot be universal fault-tolerantly via transversals alone

---

## Module 6 — Key Quantum Algorithms Overview

**Objective:** Survey the major quantum algorithms and understand their speedup origins.

| Algorithm | Problem | Speedup | Mechanism |
|---|---|---|---|
| Deutsch-Jozsa | Constant vs balanced function | Exponential (exact) | Phase kickback, interference |
| Bernstein-Vazirani | Find hidden string | n classical queries → 1 quantum query (exact) | Phase kickback + Hadamard (Fourier) sampling |
| Simon's algorithm | Find period in GF(2) | Exponential | Quantum Fourier sampling |
| Shor's algorithm | Integer factoring | Exponential | QFT + hidden subgroup |
| Grover's algorithm | Unstructured search | Quadratic; k* ≈ (π/4)√(N/M) iterations for M marked items | Amplitude amplification |
| HHL algorithm | Linear systems | Exponential* | QPE + conditional rotation |
| VQE | Ground state energy | Heuristic | Variational hybrid |
| QAOA | Combinatorial optimization | Heuristic | Variational hybrid |
| Quantum simulation | Simulate Hamiltonians | Exponential | Trotterization / LCU |

*Exponential subject to classical input/output bottleneck caveats.

**Exercises:**
- Trace through a 2-qubit Deutsch-Jozsa circuit step by step
- Explain why Grover's O(√N) speedup is optimal
- Describe the quantum speedup conditions for HHL (sparse, well-conditioned matrix)

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Quantum Computation and Quantum Information* — Nielsen & Chuang | Textbook | The definitive reference |
| Preskill's lecture notes — Caltech | Notes | Free, excellent on QEC |
| *An Introduction to Quantum Computing* — Kaye, Laflamme, Mosca | Textbook | More accessible than N&C |
| Aaronson's *Quantum Computing Since Democritus* | Book | Complexity theory focus |
| IBM Qiskit Textbook | Online | Hands-on, free |

---

## Progression Checkpoints

- [ ] Implement all standard gates and verify their matrix representations
- [ ] Decompose multi-qubit unitaries into CNOT + single-qubit gates
- [ ] Explain BQP and what quantum speedup means rigorously
- [ ] Encode a logical qubit using stabilizer code formalism
- [ ] Trace through Shor's and Grover's algorithms circuit by circuit
- [ ] Describe the surface code and why it's the leading fault-tolerance candidate
