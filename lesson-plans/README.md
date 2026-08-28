# Quantum Computing Mastery — Lesson Plans

A structured curriculum for achieving expert-level understanding of quantum computing, from mathematical foundations through practical implementation.

---

## Curriculum Map

```
Mathematics                    Physics                     Computing
─────────────                  ───────                     ─────────
01 Linear Algebra       ──►    04 Quantum Mechanics ──►   05 Quantum Computing
02 Abstract Algebra     ──►    08 Foundations QM   ──►   09 Algorithm Design
03 Representation Theory──►           │                   06 Qiskit
                                      │                   07 QASM
                                      ▼                   10 Transpiling
                               (hardware reality)
```

---

## Lesson Plans

| # | Subject | Focus |
|---|---|---|
| [01](01-linear-algebra.md) | Linear Algebra | Vector spaces, Dirac notation, eigendecomposition, tensor products, density matrices |
| [02](02-abstract-algebra.md) | Abstract Algebra | Groups, Lie algebras, finite fields, Clifford algebra, stabilizer codes |
| [03](03-representation-theory.md) | Representation Theory | Irreps, SU(2), Pauli group, QFT from characters, hidden subgroup |
| [04](04-quantum-mechanics.md) | Quantum Mechanics | Postulates, Bloch sphere, measurement, entanglement, open systems, noise channels |
| [05](05-quantum-computing.md) | Quantum Computing | Circuit model, universality, complexity, QEC, fault tolerance, algorithms survey |
| [06](06-qiskit.md) | Qiskit | QuantumCircuit API, Aer simulation, quantum_info, VQE/QAOA, visualization, primitives (Sampler/Estimator, PUBs), IBM hardware |
| [07](07-qasm.md) | QASM | OpenQASM 2 & 3 syntax, custom gates, mid-circuit measurement, defcal, cross-SDK interchange |
| [08](08-foundations-of-quantum-mechanics.md) | Foundations of QM | Measurement problem, interpretations, Bell's theorem, decoherence, information-theoretic axioms |
| [09](09-quantum-algorithm-design.md) | Algorithm Design | Core techniques, QPE, Grover, Shor, HHL, VQE, QAOA, simulation, query complexity |
| [10](10-transpiling.md) | Transpiling | Basis translation, routing, optimization passes, custom pass manager, noise-aware compilation |
| [11](11-certification-prep.md) | Certification Prep | IBM C1000-179 exam study track: section-by-section mapping to repo resources, 5-week schedule, self-assessment checklist |
| [12](12-reading-ladder.md) | Reading Ladder | Curated paper-reading program: classics ladder (EPR → Bell → CHSH → … → IBM gross code), per-docs-chapter reading lists with difficulty ratings, paper-drill integration |

---

## Recommended Learning Sequence

### Phase 1 — Mathematical Foundations (Months 1–3)
Study these in order; each builds on the previous.
1. **Linear Algebra** — the language of everything that follows
2. **Quantum Mechanics** — physical intuition and postulates
3. **Abstract Algebra** — groups and fields
4. **Representation Theory** — symmetry acting on state spaces

### Phase 2 — Quantum Computing Core (Months 3–5)
5. **Foundations of QM** — conceptual depth, interpretations, Bell's theorem
6. **Quantum Computing** — circuit model, error correction, algorithm survey
7. **Quantum Algorithm Design** — derive and analyze algorithms from scratch

### Phase 3 — Implementation (Months 5–7)
8. **QASM** — the IR; read and write circuits at assembly level
9. **Qiskit** — build, simulate, and run circuits on hardware
10. **Transpiling** — compilation pipeline, custom passes, noise-aware optimization

### Phase 4 — Certification (optional, Month 7+)
11. **Certification Prep** — a 4–6 week part-time track mapping the IBM C1000-179
    (Qiskit v2.x Associate Developer) exam onto lessons 06, 07, and 10 plus the
    interactive apps, ending with the official IBM sample test
12. **Reading Ladder** — runs in parallel with Phases 2–4 rather than after them:
    one classics-ladder paper per week plus each docs chapter's reading list,
    drilled with the paper-drill app

---

## Key References

| Book | Covers |
|---|---|
| Nielsen & Chuang, *Quantum Computation and Quantum Information* | Definitive reference for everything |
| Axler, *Linear Algebra Done Right* | Rigorous linear algebra |
| Dummit & Foote, *Abstract Algebra* | Groups, rings, fields |
| Shankar, *Principles of Quantum Mechanics* | Physics foundations |
| Fulton & Harris, *Representation Theory* | Groups and irreps |
| Preskill lecture notes (Caltech) | Free; excellent on QEC and advanced topics |
| Qiskit documentation (docs.quantum.ibm.com) | SDK reference |

---

## Lesson Plan Structure

Each markdown file follows a consistent structure:

- **Goal** — one-paragraph statement of what the lesson builds toward
- **Modules** — 5–10 thematic modules, each with a table of key concepts and concrete exercises
- **Practice problems** — worked examples and derivations
- **Further reading** — textbook sections and paper references
- **Connections** — explicit pointers to other lessons and quantum computing applications

### Lesson Scope Summary

| Lesson | Modules | Focus Areas |
|---|---|---|
| 01 Linear Algebra | 6 | Vector spaces, inner products, eigendecomposition, density matrices, tensor products, Schmidt decomposition |
| 02 Abstract Algebra | 6 | Groups, homomorphisms, Lie groups (SU(2)), finite fields, Clifford group, Pauli group structure |
| 03 Representation Theory | 6 | Irreps, characters, SU(2) reps, Clebsch-Gordan, QFT from character sums, hidden subgroup |
| 04 Quantum Mechanics | 6 | Postulates, Bloch sphere, measurement, entanglement, Lindblad, Kraus operators, Bell states |
| 05 Quantum Computing | 6 | Circuit model, gates, universality, QEC, CSS codes, surface code, fault tolerance, algorithms |
| 06 Qiskit | 8 | QuantumCircuit, AerSimulator, quantum_info, parameterized circuits, visualization, primitives (SamplerV2/EstimatorV2, PUBs), IBM Runtime |
| 07 QASM | 6 | QASM 2 syntax, qelib1.inc, QASM 3 types and control flow, mid-circuit measurement, defcal (spec background; pulse retired on IBM systems) |
| 08 Foundations of QM | 6 | Interpretations, Bell's theorem, CHSH, Tsirelson bound, decoherence, information-theoretic axioms |
| 09 Algorithm Design | 5 | Phase kickback, QPE, Grover, Shor, HHL, VQE, QAOA, simulation, query complexity |
| 10 Transpiling | 7 | Basis translation, routing, SWAP insertion, optimization passes, noise-aware compilation |

---

## Connection to Interactive Apps

The lesson plans and interactive apps are designed to be used together. Each app
targets a subset of the curriculum:

| App | Relevant Lessons |
|---|---|
| `flashcard-drill` | 01, 02, 03, 05, 06 — core identities, theorems, and Qiskit API |
| `math-quiz` | 01, 02, 03, and the math subjects absent from quantum-quiz |
| `quantum-quiz` | 04, 05, 06, 07, 08, 09, 10 |
| `circuit-trainer` | 05, 06 — circuit arithmetic and Qiskit |
| `qec-trainer` | 05 (QEC section), 08 (stabilizer formalism) |
| `vqa-trainer` | 09 (VQE, QAOA sections) |
| `paper-drill` | Any — test comprehension of papers on any topic |

**Recommended workflow**: read a lesson plan module → use the corresponding quiz app
to test retention → return to the lesson plan for review.

---

## Recurring Themes Across All Subjects

- **Unitarity** — quantum evolution preserves inner products; gates are reversible
- **Hilbert space** — the arena; dimension grows exponentially with qubits
- **Measurement** — the bridge between quantum amplitudes and classical outcomes
- **Entanglement** — the resource that makes quantum computing qualitatively different
- **Symmetry** — groups act on state spaces; conservation laws follow; codes exploit symmetry
- **Noise** — real hardware deviates from ideal; error correction and mitigation restore reliability
