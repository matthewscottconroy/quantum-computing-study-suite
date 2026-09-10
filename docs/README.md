# Quantum Computing: A Complete Learning Ladder

This documentation covers quantum computing from mathematical foundations to cutting-edge research
topics. Whether you are a graduate student starting fresh, a physicist transitioning to quantum
information, or an engineer wanting to understand the theory behind quantum hardware, follow the
ladder from bottom to top. Each rung builds on the ones below.

---

## The Ladder

### Rung 0: Prerequisites
**No file — just a checklist.**

Before starting, you should be comfortable with:
- **Linear algebra**: vectors, matrices, eigenvalues, inner products, tensor products.
  (Review: Strang's *Introduction to Linear Algebra*, Chapters 1–6.)
- **Complex numbers**: polar form, Euler's formula `e^{iθ} = cosθ + i sinθ`.
- **Probability**: conditional probability, expectations, variance.
- **Python**: basic syntax helpful but not required (the companion apps use Python).

Optional but helpful:
- Differential equations (for time evolution in Chapter 2).
- Classical information theory (for Chapter 8).
- Basic chemistry concepts (for Chapter 6 VQE discussions).

---

### Rung 1: Mathematical Foundations (Chapter 1)
**Files**: `01_mathematical_foundations/` | **Time**: 3–5 weeks (files 01–03 in the first week; the rest can be read on demand as later chapters cite them)

The mathematical language of quantum mechanics, and the mathematics the rest of the corpus
silently assumes. The core track (files 01–03) is linear algebra in Dirac notation, complex
Hilbert spaces, the spectral theorem and tensor products. The extended track (files 04–09)
supplies the algebra, analysis, probability and geometry that the quantum-algorithms,
error-correction and hardware chapters draw on: groups and the Pauli/Clifford groups, finite
fields, Lie algebras and the `SU(2) → SO(3)` double cover, representation theory and characters
(the QFT and the hidden subgroup problem), probability and statistics, number theory and Fourier
analysis, functional analysis for unbounded operators, and topology and geometry.

**Key concepts you will master**:
- Dirac bra-ket notation `|ψ⟩`, `⟨φ|`, `⟨φ|ψ⟩`
- Hermitian operators and their physical meaning
- Unitary operators (quantum gates) and their properties
- Tensor product `|a⟩ ⊗ |b⟩` for multi-qubit systems
- Change of basis and spectral decomposition
- Groups, cosets and quotients; the Pauli group `P_n`, its center, and `P_n/Z(P_n) ≅ F_2^{2n}`
  with the symplectic form; the Clifford group as a normalizer; `GF(2)` and `GF(4)`
- Lie algebras and the exponential map: `𝔰𝔲(2)` generators `σ/2`, `e^{-iθn̂·σ/2}`, why
  `R(2π) = -I`
- Representations, characters and orthogonality; character tables of `ℤ_N`, `S_3`, `D_4`;
  Clebsch-Gordan for `SU(2)`; characters of `ℤ_N` as the QFT; the hidden subgroup problem
- Probability, estimators and concentration bounds behind shot noise and benchmarking
- Modular arithmetic, continued fractions and the DFT behind Shor's algorithm
- Function spaces, unbounded operators and the Fourier transform behind wave mechanics
- Manifolds, fibre bundles, Berry phase and homology behind Bloch geometry and topological codes

**Why it matters**: Every quantum computing concept, from the simplest qubit to topological
quantum computation, is phrased in this mathematical language. Skipping this chapter leads to
confusion when Hamiltonians, stabilizers, and density matrices appear in later chapters. The
extended files exist because the later chapters *use* this mathematics without re-deriving it:
the stabilizer formalism is group theory over `GF(2)`, Shor's algorithm is Fourier analysis on
`ℤ_N`, and the threshold theorem is a concentration bound.

**File map**:
| File | Topic |
|------|-------|
| `01_linear_algebra.md` | Vector spaces, Dirac notation, adjoints, spectral theorem, unitaries, Pauli matrices |
| `02_complex_numbers_and_hilbert_spaces.md` | Complex arithmetic, Euler's formula, Hilbert spaces, global phase |
| `03_tensor_products_and_multipartite_systems.md` | Tensor/Kronecker products, multi-qubit registers, partial trace |
| `04_groups_and_abstract_algebra.md` | Groups, cosets, quotients, `S_n` parity, Pauli and Clifford groups, `GF(2ᵐ)`, Lie algebras, `SU(2) → SO(3)` |
| `05_representation_theory.md` | Irreps, Schur, characters, `ℤ_N`/`S_3`/`D_4` tables, Clebsch-Gordan, `SU(2)` spin-`j`, QFT as characters, HSP |
| `06_probability_and_statistics.md` | Random variables, estimators, concentration bounds, shot noise, hypothesis testing |
| `07_number_theory_and_fourier_analysis.md` | Modular arithmetic, orders and periods, continued fractions, DFT/FFT |
| `08_analysis_for_quantum_mechanics.md` | `L²` spaces, unbounded operators, Fourier transform, distributions, Stone's theorem |
| `09_topology_and_geometry.md` | Manifolds, Bloch sphere geometry, fibre bundles, Berry phase, homology for topological codes |

---

### Rung 2: Quantum Mechanics Foundations (Chapter 2)
**Files**: `02_quantum_mechanics/` | **Time**: 3–5 weeks

The four postulates of quantum mechanics as applied to quantum computing: state spaces,
evolution, measurement, and composition. Qubits, the Bloch sphere, entanglement, density
matrices, quantum channels — plus a full wave-mechanics track (Schrödinger equation,
harmonic oscillator, angular momentum, hydrogen, perturbation theory) aligning the chapter
with a standard university QM course (Griffiths/Shankar level).

**Key concepts you will master**:
- The qubit `|ψ⟩ = α|0⟩ + β|1⟩` and Bloch sphere representation
- Measurement: Born rule, projective measurement, POVMs
- Entanglement: Bell states, EPR, Schmidt decomposition
- Density matrices `ρ`: mixed states, partial trace, reduced states
- Quantum channels (CPTP maps): Kraus representation, Lindblad equation
- Wave mechanics: Schrödinger equation, square wells, tunneling
- Harmonic oscillator with ladder operators; coherent states (prerequisite for bosonic codes)
- Angular momentum algebra, spin-½ as the qubit, hydrogen atom
- Perturbation theory, Fermi's golden rule, Rabi oscillations (how gates are driven)
- Distance measures: trace distance, fidelity, diamond norm

**Why it matters**: All quantum algorithms operate on the structures defined here. Without
understanding measurement collapse, entanglement, and mixed states, quantum error correction
and variational algorithms are unmotivated abstractions. The wave-mechanics files supply the
continuous-variable QM that bosonic codes (Chapter 5) and hardware physics (Chapter 7) assume.

**File map**:
| File | Topic |
|------|-------|
| `01_postulates_of_quantum_mechanics.md` | State space, evolution, measurement, composition |
| `02_qubits_and_the_bloch_sphere.md` | Qubit geometry, rotations |
| `03_quantum_measurements.md` | Born rule, projective, POVM, uncertainty |
| `04_entanglement_and_nonlocality.md` | Bell states, Schmidt, CHSH |
| `05_density_matrices_and_open_systems.md` | Mixed states, partial trace, Kraus channels |
| `06_wave_mechanics_and_schrodinger.md` | TDSE/TISE, wells, wave packets, tunneling |
| `07_harmonic_oscillator.md` | Ladder operators, Fock states, coherent states |
| `08_angular_momentum_and_hydrogen.md` | `|j,m⟩` tower, spin-½ ≡ qubit, CG, hydrogen |
| `09_perturbation_theory.md` | TIPT, Fermi's golden rule, Rabi problem |
| `10_distance_measures_and_lindblad.md` | Trace distance, fidelity, diamond norm, Lindblad |

---

### Rung 3: Quantum Circuits and Gates (Chapter 3)
**Files**: `03_quantum_gates_and_circuits/` | **Time**: 1–2 weeks

The quantum circuit model: single- and two-qubit gates, universal gate sets, circuit complexity,
the Clifford group, measurement-based quantum computing.

**Key concepts you will master**:
- Standard gates: H, S, T, CNOT, CZ, Toffoli
- Universal gate sets: `{H, S, T, CNOT}` is universal
- The Clifford group and Gottesman-Knill theorem
- Circuit depth and width as computational resources
- Quantum teleportation circuit

**Why it matters**: Quantum algorithms are specified as circuits. Hardware implementations,
error correction circuits, and variational ansätze are all circuits. The Clifford/non-Clifford
distinction is the foundation of fault tolerance.

**File map**:
| File | Topic |
|------|-------|
| `01_single_qubit_gates.md` | Pauli, Hadamard, phase, rotation gates; identities |
| `02_multi_qubit_gates.md` | CNOT, CZ, SWAP, Toffoli; teleportation |
| `03_circuit_model_and_universality.md` | Universal gate sets, Solovay-Kitaev, Clifford group |
| `04_quantum_circuit_complexity.md` | Depth/width, BQP, resource estimates |
| `05_measurement_based_qc.md` | Cluster states, one-way computing, fusion-based QC |

---

### Rung 4: Core Quantum Algorithms (Chapter 4)
**Files**: `04_quantum_algorithms/` | **Time**: 2–4 weeks

The landmark algorithms that establish quantum advantage: QFT and phase estimation, Shor's
factoring algorithm, Grover's search, HHL for linear systems, and quantum simulation.

**Key concepts you will master**:
- Quantum Fourier Transform (QFT) and phase kickback
- Quantum phase estimation (QPE) and its role in algorithms
- Shor's algorithm: period finding → factoring, beating RSA
- Grover's search: quadratic speedup for unstructured search
- Amplitude amplification as a general technique

**Why it matters**: These algorithms define what quantum computers can do that classical
computers cannot. Shor's algorithm is the reason quantum-resistant cryptography is being deployed
now. QPE is the subroutine underlying most fault-tolerant algorithms.

**File map**:
| File | Topic |
|------|-------|
| `01_quantum_parallelism_and_interference.md` | Oracles, interference, the real source of speedup |
| `02_deutsch_jozsa_and_bernstein_vazirani.md` | First exact separations, phase kickback |
| `03_quantum_fourier_transform.md` | QFT circuit and analysis |
| `04_quantum_phase_estimation.md` | QPE, precision/ancilla tradeoffs |
| `05_grover_search.md` | Amplitude amplification, optimality |
| `06_shors_algorithm.md` | Period finding → factoring |
| `07_hhl_quantum_linear_systems.md` | HHL, caveats, dequantization |
| `08_quantum_cryptography.md` | BB84, E91, QKD in practice vs post-quantum crypto |
| `09_quantum_walks.md` | Coined/Szegedy/continuous walks, element distinctness, glued trees |

---

### Rung 5: Quantum Error Correction (Chapter 5)
**Files**: `05_quantum_error_correction/` | **Time**: 3–4 weeks

Why quantum computers need error correction, and how it works. From the repetition code to the
surface code; from the threshold theorem to magic state distillation.

**Key concepts you will master**:
- Why QEC is hard (no-cloning, continuous errors, measurement collapse)
- Classical linear codes and their quantum generalization
- The 3-qubit repetition code and Shor's 9-qubit code
- Stabilizer formalism: the unified language of QEC
- CSS codes and the Steane `[[7,1,3]]` code
- Surface code: `[[d²,1,d]]`, ~1% threshold, MWPM decoding
- Fault tolerance: threshold theorem, magic state distillation
- Bosonic codes: cat qubits, GKP codes

**Why it matters**: Without error correction, quantum computers cannot scale beyond ~100 qubits
with useful circuit depth. The surface code and fault tolerance are the engineering path to
large-scale quantum computing. Magic state distillation and bosonic codes are central to
current hardware roadmaps.

**File map**:
| File | Topic |
|------|-------|
| `01_why_qec_is_hard.md` | No-cloning, continuous errors, the syndrome idea |
| `02_classical_error_correction.md` | Linear codes, Hamming, dual codes |
| `03_repetition_code.md` | 3-qubit codes, Shor 9-qubit code, `[[n,k,d]]` notation |
| `04_stabilizer_formalism.md` | Pauli group, stabilizer codes, Clifford group |
| `05_css_codes_and_steane.md` | CSS construction, `[[7,1,3]]` Steane code |
| `06_surface_code.md` | Toric/surface code, MWPM, ~1% threshold |
| `07_fault_tolerance.md` | Threshold theorem, magic state distillation |
| `08_bosonic_codes.md` | Cat qubits, GKP codes, binomial codes |
| `09_qldpc_codes.md` | Hypergraph/balanced products, bivariate bicycle codes, BP+OSD |

---

### Rung 6: Variational Quantum Algorithms (Chapter 6)
**Files**: `06_variational_quantum_algorithms/` | **Time**: 2–3 weeks

Near-term quantum algorithms for chemistry and optimization. VQE, QAOA, the parameter-shift
gradient, barren plateaus, error mitigation, and quantum optimal control.

**Key concepts you will master**:
- The variational principle and VQE algorithm loop
- Hamiltonian encoding: Pauli decomposition, JW and BK mappings
- Ansatz design: HEA, UCCSD, HVA, ADAPT-VQE
- Parameter-shift rule for exact quantum gradients
- QAOA for combinatorial optimization
- Barren plateaus: exponentially vanishing gradients
- Error mitigation: ZNE, PEC, CDR
- Quantum optimal control: GRAPE, CRAB, quantum speed limit

**Why it matters**: These algorithms are being run on hardware today. Understanding their
capabilities and limitations is essential for assessing quantum advantage claims in chemistry and
optimization, and for designing experiments on real hardware.

**File map**:
| File | Topic |
|------|-------|
| `01_vqe_fundamentals.md` | VQE loop, Hamiltonian encoding, UCCSD, chemical accuracy |
| `02_ansatz_design.md` | HEA, UCCSD, HVA, ADAPT-VQE, symmetry |
| `03_parameter_shift_gradient.md` | Parameter shift rule, QNG, SPSA, shot noise |
| `04_qaoa.md` | MaxCut, QAOA circuit, p=1 guarantee, adiabatic limit |
| `05_barren_plateaus.md` | Exponential gradient decay, mitigation strategies |
| `06_noise_and_error_mitigation.md` | ZNE, PEC, CDR, virtual distillation |
| `07_quantum_optimal_control.md` | GRAPE, CRAB, QSL, VQAs as control problems |

---

### Rung 7: Quantum Hardware (Chapter 7)
**Files**: `07_quantum_hardware/` | **Time**: 1–2 weeks

How quantum computers are physically built. Superconducting qubits (transmon, Josephson
junction), trapped ions (Paul trap, MS gate), photonic and other platforms, and how to
benchmark and characterize hardware.

**Key concepts you will master**:
- Transmon qubit: Josephson junction, `E_J/E_C` ratio, anharmonicity
- Qubit control: microwave drive, IQ channels, DRAG pulses
- Two-qubit gates: cross-resonance (IBM), CZ (Google), √iSWAP
- Trapped ion qubits: Lamb-Dicke, Mølmer-Sørensen gate, all-to-all connectivity
- Photonic QC: LOQC, KLM, boson sampling, Rydberg arrays
- Benchmarking: T1/T2, randomized benchmarking, GST, quantum volume, CLOPS

**Why it matters**: Algorithm performance depends critically on hardware characteristics.
Understanding gate fidelity, coherence times, connectivity, and benchmarking metrics is
essential for choosing hardware and interpreting experimental results.

**File map**:
| File | Topic |
|------|-------|
| `01_superconducting_qubits.md` | Transmon, Josephson junction, dilution refrigerator |
| `02_trapped_ion_qubits.md` | Paul trap, Jaynes-Cummings, MS gate, QCCD |
| `03_photonic_and_other_platforms.md` | Photonics, NV centers, Rydberg, Majorana |
| `04_benchmarking_and_characterization.md` | T1/T2, RB, GST, quantum volume, CLOPS |

---

### Rung 8: Advanced Topics (Chapter 8)
**Files**: `08_advanced_topics/` | **Time**: 3–6 weeks (ongoing reference)

The research frontier: quantum complexity theory (BQP, QMA, QPCP conjecture), quantum information
theory (Von Neumann entropy, channel capacity, teleportation), many-body physics and quantum
simulation (Ising, Heisenberg, Hubbard models, FeMoco), and topological quantum computation
(anyons, Fibonacci anyons, Majorana zero modes).

**Key concepts you will master**:
- BQP and its relationship to NP, PSPACE
- QMA-completeness of the Local Hamiltonian problem
- Von Neumann entropy, Holevo bound, quantum channel capacity
- Teleportation and superdense coding resource accounting
- Key many-body models: TFIM, Heisenberg, Hubbard
- Trotter simulation and qubitization
- Anyons, non-Abelian statistics, Fibonacci anyons → universal TQC
- Majorana zero modes and topological protection

**Why it matters**: These topics define the theoretical boundaries of quantum computing and
the ultimate targets for quantum advantage (FeMoco, quantum chemistry). Complexity theory tells
you what can and cannot be efficiently computed. Topological QC is the physical basis for
intrinsically fault-tolerant hardware.

**File map**:
| File | Topic |
|------|-------|
| `01_quantum_complexity_theory.md` | BQP, QMA, query complexity, QPCP |
| `02_quantum_information_theory.md` | Von Neumann entropy, Holevo, teleportation |
| `03_many_body_physics_and_simulation.md` | Models, Trotter, JW/BK, FeMoco |
| `04_topological_quantum_computation.md` | Anyons, Fibonacci TQC, Kitaev chain |
| `05_qsvt.md` | Block encodings, QSP, quantum singular value transformation |

---

## Quick Reference by Topic

| Topic | Chapter/File |
|-------|-------------|
| Linear algebra, Dirac notation, spectral theorem | 01/01 |
| Tensor products and partial trace | 01/03 |
| Groups, cosets, Pauli group and symplectic form, Clifford group | 01/04 |
| Lie algebras, `SU(2) → SO(3)` double cover | 01/04 |
| Representation theory, characters, Clebsch-Gordan | 01/05 |
| QFT as characters of `ℤ_N`; hidden subgroup problem | 01/05 |
| Probability, estimators, concentration bounds | 01/06 |
| Number theory, continued fractions, DFT | 01/07 |
| Functional analysis, unbounded operators, Fourier transform | 01/08 |
| Topology, Berry phase, homology | 01/09 |
| Qubit notation and Bloch sphere | 02 |
| Quantum gates (H, CNOT, T) | 03 |
| Entanglement and Bell states | 02 |
| Schrödinger equation, wells, tunneling | 02/06 |
| Harmonic oscillator and coherent states | 02/07 |
| Angular momentum and hydrogen | 02/08 |
| Perturbation theory, Rabi oscillations | 02/09 |
| Trace distance, fidelity, diamond norm | 02/10 |
| Lindblad master equation, T₁/T₂ | 02/10 |
| Shor's algorithm | 04 |
| Grover's search | 04 |
| HHL / quantum linear systems | 04/07 |
| BB84 and quantum key distribution | 04/08 |
| Quantum walks | 04/09 |
| Measurement-based QC / cluster states | 03/05 |
| qLDPC and bivariate bicycle codes | 05/09 |
| QSVT and block encodings | 08/05 |
| Quantum error correction basics | 05/01 |
| Surface code | 05/06 |
| VQE algorithm | 06/01 |
| Parameter-shift gradients | 06/03 |
| QAOA | 06/04 |
| Barren plateaus | 06/05 |
| Transmon qubit physics | 07/01 |
| Trapped ion qubits | 07/02 |
| Randomized benchmarking | 07/04 |
| Quantum complexity (BQP, QMA) | 08/01 |
| Von Neumann entropy | 08/02 |
| Hubbard model simulation | 08/03 |
| Majorana zero modes | 08/04 |
| Fault tolerance threshold | 05/07 |
| Magic state distillation | 05/07 |
| Bosonic/cat qubits | 05/08 |
| Quantum optimal control (GRAPE) | 06/07 |

---

## Time Estimates

| Chapter | Casual reading (surveys) | Active learning (all examples) | Research level |
|---------|--------------------------|-------------------------------|----------------|
| 1: Math (core, files 01–03) | 1 week | 2 weeks | — |
| 1: Math (extended, files 04–09) | 1 week | 3 weeks | — |
| 2: QM | 2 weeks | 5 weeks | — |
| 3: Circuits | 3 days | 1 week | — |
| 4: Algorithms | 1 week | 4 weeks | — |
| 5: QEC | 1 week | 4 weeks | 2+ months |
| 6: VQA | 1 week | 3 weeks | 2+ months |
| 7: Hardware | 3 days | 2 weeks | 1+ month |
| 8: Advanced | 1 week | 4 weeks | ongoing |
| **Total** | **~9 weeks** | **~6 months** | **ongoing** |

---

## How to Use These Notes

### For Self-Study

1. **Read actively**: Don't just read — work every derivation yourself on paper.
2. **Do the worked examples**: Before reading the worked example, try the problem yourself.
3. **Write code**: Use the companion `circuit-trainer` app (Qiskit) to implement gates and
   circuits from each chapter. Use the `quantum-quiz` app to test your understanding.
4. **Follow the prerequisites**: The prerequisites listed at the top of each file are real.
   If a concept is unclear, follow the link back to the prerequisite file.

### For a Course

Chapters 1–4 form a solid one-semester "Introduction to Quantum Computing" course.
Chapters 5–8 form an advanced graduate seminar on "Quantum Error Correction, Hardware, and
Algorithms."

A 10-week intensive covering the full curriculum:
- Weeks 1–2: Chapters 1–2 (math and QM foundations)
- Weeks 3–4: Chapters 3–4 (circuits and algorithms)
- Weeks 5–6: Chapter 5 (error correction)
- Weeks 7–8: Chapter 6 (variational algorithms)
- Week 9: Chapter 7 (hardware)
- Week 10: Chapter 8 (advanced topics, selective deep dives)

### For Reference

Each file is self-contained as a reference document. The "Key Formulas" section at the end of
each file summarizes the essential equations, and every file now carries an "Exercises"
section (3–5 problems with fully worked solutions in collapsible blocks) bridging reading and
the quiz apps. The "Further Reading" section gives the 5 most important papers or books for
deeper study.

---

## Notation Conventions Used Throughout

| Symbol | Meaning |
|--------|---------|
| `\|ψ⟩` | Ket (quantum state vector) |
| `⟨φ\|` | Bra (dual vector) |
| `\|0⟩`, `\|1⟩` | Computational basis states |
| `\|+⟩`, `\|-⟩` | Hadamard basis states `(|0⟩±|1⟩)/√2` |
| `X, Y, Z` | Pauli matrices |
| `H` | Hadamard gate (also Hamiltonian — context dependent) |
| `ρ` | Density matrix |
| `S(ρ)` | Von Neumann entropy |
| `[[n, k, d]]` | Quantum code: n physical, k logical, distance d |
| `[n, k, d]` | Classical code: n bits, k data bits, distance d |
| `E_J`, `E_C` | Josephson energy, charging energy (Chapter 7) |
| `T₁`, `T₂` | Qubit relaxation and coherence times |
| `p_th` | Error correction threshold |
| `BQP`, `QMA` | Quantum complexity classes (Chapter 8) |

---

## Companion Software

These notes are part of the Quantum Computing Learning Suite:

- **`quantum-quiz/`**: Claude API-powered PyQt6 GUI for testing your knowledge. Questions are
  generated by Claude based on the chapter content. Run `python main.py` in that directory.
- **`circuit-trainer/`**: Local Qiskit PyQt6 app for building and simulating quantum circuits.
  Hands-on practice for Chapters 3–6. Run `python main.py` in that directory.
- **`lesson-plans/`**: 10 structured lesson plan markdown files for course instructors.

---

## A Note on Mathematical Notation in These Files

Inline mathematical expressions are written in backtick notation:
`|ψ⟩ = α|0⟩ + β|1⟩`. Display equations appear either as fenced text blocks or as
`$$ … $$` blocks (rendered natively by VS Code, Obsidian, and GitHub; shown as monospace
blocks in the apps' in-app Reference browser). Inline `$…$` is never used, so files read
cleanly in any Markdown viewer.

For a LaTeX-rendered version, the expressions can be converted straightforwardly:
- Backtick inline math → `$...$`
- Text blocks of display equations → `$$...$$`

When studying with a rendering tool (VS Code + Markdown Math, Obsidian, JupyterBook), the
mathematical notation becomes substantially cleaner.

---

*Documentation version: 2026. For corrections or contributions, see the project repository.*
