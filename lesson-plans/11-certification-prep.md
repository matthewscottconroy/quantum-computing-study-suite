# Certification Prep — IBM C1000-179

## Goal
Pass the **IBM Certified Associate Developer — Quantum Computation using Qiskit v2.X** exam (C1000-179) by systematically mapping each exam section onto this repository's lesson plans, docs, and interactive apps, closing gaps with targeted hands-on practice, and finishing with the official IBM sample test. This is a study *track*, not new material — every exam section below points into content you already have.

---

## Exam Facts

> **Source caveat:** the weights and logistics below are compiled from third-party exam-prep sources. **Confirm everything on IBM's official C1000-179 exam page** (search "IBM C1000-179" on ibm.com/training) before booking — IBM occasionally revises section weights and question counts.

| Fact | Value |
|---|---|
| Exam code | C1000-179 |
| Title | Fundamentals of Quantum Computing Using Qiskit v2.X Developer — Associate |
| Replaces | C1000-112 (Qiskit v0.2x), retired September 2025 |
| Questions | 68 |
| Time | 90 minutes (~79 seconds/question) |
| Passing score | 47 of 68 (~69%) |
| Cost | ~$200 USD |
| Format | Multiple choice, heavy on reading/completing Qiskit v2.x code snippets |
| Qiskit version | 2.x (SamplerV2/EstimatorV2, ISA circuits, no `execute()`, no `qiskit.pulse`) |

### Section Weights

| # | Exam Section | Weight | ≈ Questions |
|---|---|---|---|
| 1 | Create quantum circuits | 18% | ~12 |
| 2 | Perform quantum operations | 16% | ~11 |
| 3 | Run quantum circuits | 15% | ~10 |
| 4 | Use the Sampler primitive | 12% | ~8 |
| 5 | Use the Estimator primitive | 12% | ~8 |
| 6 | Use visualization | 11% | ~7 |
| 7 | Retrieve and analyze results | 10% | ~7 |
| 8 | Use OpenQASM | 6% | ~4 |

Note that sections 3 + 4 + 5 + 7 together are **49%** — half the exam is the primitives execution workflow. Prioritize accordingly.

---

## Section-by-Section Study Map

Each subsection lists the repo resources that cover the exam section, then what to practice hands-on. Lesson/module references below have been verified against the current files.

### 1 — Create Quantum Circuits (18%)

| Resource | What it covers |
|---|---|
| [Lesson 06, Module 2](06-qiskit.md) — Building Quantum Circuits | `QuantumCircuit` constructor, gate methods, barrier, measure, `measure_all()` |
| [Lesson 06, Module 5](06-qiskit.md) — Parameterized Circuits | `Parameter`, `ParameterVector`, `assign_parameters` |
| [docs/03_quantum_gates_and_circuits](../docs/03_quantum_gates_and_circuits/) | Gate theory behind the API (single-qubit, multi-qubit, circuit model) |
| `circuit-trainer` | `single_gate`, `gate_sequence`, `composition`, `multi_qubit` categories |
| `quantum-quiz` | Qiskit subject ("building circuits with QuantumCircuit") + the new Qiskit Certification (C1000-179) subject |
| `flashcard-drill` | `qiskit_api` category + `gate_unitaries` for the matrices behind each method |

**Practice:** build all four Bell states, a 3-qubit QFT, and a parameterized ansatz from memory. Know `QuantumCircuit(n)` vs `QuantumCircuit(n, m)`, `qc.compose()`, `qc.append()`, `qc.copy()`, `qc.depth()`, `qc.count_ops()`, and register/creg naming (`measure_all()` creates creg `meas`).

### 2 — Perform Quantum Operations (16%)

| Resource | What it covers |
|---|---|
| [Lesson 06, Module 4](06-qiskit.md) — Quantum Information Tools | `Statevector`, `DensityMatrix`, `Operator`, `SparsePauliOp`, `partial_trace`, fidelities |
| [Lesson 06, Module 2](06-qiskit.md) | The full gate method table (Pauli, phase, rotation, controlled gates) |
| [Lesson 04](04-quantum-mechanics.md) / [docs/02](../docs/02_quantum_mechanics/) | Measurement, Born rule, Bloch sphere — conceptual backing |
| `circuit-trainer` | `circuit_unitary`, `gate_identity`, `equivalence`, `measurement` categories |
| `flashcard-drill` | `pauli_matrices`, `gate_unitaries`, `quantum_info`, `qiskit_api` categories |

**Practice:** `Statevector.from_label()`, `sv.evolve(qc)`, `Operator(qc)`, `SparsePauliOp(["ZZ","XX"], coeffs=...)`, operator composition (`@`, `.tensor()`, `.compose()`), and — critical — **Qiskit's little-endian convention**: qubit 0 is the *rightmost* bit in labels and counts keys, and `Statevector([a,b,c,d])` orders basis states |q1 q0⟩.

### 3 — Run Quantum Circuits (15%)

| Resource | What it covers |
|---|---|
| [Lesson 06, Module 7](06-qiskit.md) — Primitives Workflow | ISA circuits, `generate_preset_pass_manager`, Job/Session/Batch execution modes |
| [Lesson 06, Module 8](06-qiskit.md) — IBM Hardware | `QiskitRuntimeService`, `save_account`, `least_busy`, job lifecycle |
| [Lesson 06, Module 3](06-qiskit.md) — Aer | Local simulation, `transpile` + `run` on `AerSimulator` |
| [Lesson 10, Modules 1 & 5](10-transpiling.md) | Transpilation pipeline, optimization levels 0–3, preset pass manager |
| `quantum-quiz` | Transpiling subject + Qiskit Certification subject (ISA circuits, execution modes) |

**Practice:** write the four-line hardware recipe from memory — service → backend → `generate_preset_pass_manager(optimization_level=..., backend=...)` → `pm.run(qc)` → primitive. Know *why* runtime primitives reject non-ISA circuits, when to use Session vs Batch vs job mode, and `job.status()` / `job.job_id()` / `service.job(job_id)`.

### 4 — Sampler Primitive (12%)

| Resource | What it covers |
|---|---|
| [Lesson 06, Module 7](06-qiskit.md) — Primitives Workflow | `StatevectorSampler` / `SamplerV2`, Sampler PUB shapes, shots |
| `quantum-quiz` | Qiskit Certification subject (SamplerV2 PUB construction and result access) |
| `flashcard-drill` | `qiskit_api` category |

**Practice:** Sampler PUB shapes — `(circuit,)`, `(circuit, parameter_values)`, `(circuit, parameter_values, shots)` — and that circuits **must contain measurements**. Result access chain: `job.result()[0].data.meas.get_counts()` (attribute name = classical register name). Run one job with three PUBs and extract each PUB's counts.

### 5 — Estimator Primitive (12%)

| Resource | What it covers |
|---|---|
| [Lesson 06, Module 7](06-qiskit.md) — Primitives Workflow | `StatevectorEstimator` / `EstimatorV2`, Estimator PUBs, observables, `apply_layout`, resilience |
| [Lesson 06, Module 4](06-qiskit.md) | `SparsePauliOp` observable construction |
| `vqa-trainer` + [Lesson 06, Module 5](06-qiskit.md) | Estimator-in-a-loop context (VQE/QAOA) |
| `quantum-quiz` | Qiskit Certification subject (EstimatorV2 PUBs, `data.evs`) |

**Practice:** Estimator PUB shapes — `(circuit, observables)`, `(circuit, observables, parameter_values)`, `(..., precision)` — circuits must have **no measurements**. Result access: `result[0].data.evs` (and `.stds`). Sweep θ over one parameterized PUB and plot ⟨Z⟩(θ). On hardware: `observable.apply_layout(isa_circuit.layout)`. Know Estimator options: `resilience_level` 0/1/2, dynamical decoupling, twirling (Sampler has no resilience levels).

### 6 — Visualization (11%)

| Resource | What it covers |
|---|---|
| [Lesson 06, Module 6](06-qiskit.md) — Visualization | The full function table, `qc.draw()` outputs, exam-tested distinctions |
| `quantum-quiz` | Qiskit Certification subject (visualization function selection) |

**Practice:** *which function for which job* — `plot_histogram` (counts) vs `plot_distribution` (probabilities, heights sum to 1); `plot_bloch_multivector` (per-qubit reduced states — vanishing vectors for entangled qubits) vs `plot_state_qsphere` (global amplitudes + phases) vs `plot_state_city` (density-matrix bars); `qc.draw(output='text'|'mpl'|'latex')` with `fold` and `idle_wires`. Know the install extras: `pip install "qiskit[visualization]"`.

### 7 — Retrieve and Analyze Results (10%)

| Resource | What it covers |
|---|---|
| [Lesson 06, Modules 7 & 8](06-qiskit.md) | `PrimitiveResult` indexing, per-creg data access, counts, evs, job retrieval |
| [Lesson 06, Module 3](06-qiskit.md) | `result.get_counts()` on Aer, statevector extraction |
| `circuit-trainer` | `measurement` category — predicting count distributions |

**Practice:** the result object tree for both primitives (`result[i]` → PUB result → `.data` → creg/evs → values), `get_counts()` vs per-shot bitarrays (`data.meas.get_bitstrings()`, `.array`), interpreting counts keys in little-endian order, and retrieving historical jobs via `service.jobs()` / `service.job(job_id)`.

### 8 — OpenQASM (6%)

| Resource | What it covers |
|---|---|
| [Lesson 07, Module 1](07-qasm.md) | QASM 2 file structure, `qelib1.inc`, syntax elements |
| [Lesson 07, Module 3](07-qasm.md) | QASM 3 types, control flow, mid-circuit measurement |
| [Lesson 07, Module 4](07-qasm.md) | `qiskit.qasm2` / `qiskit.qasm3` `dumps`/`loads` round-tripping |
| `quantum-quiz` | QASM subject + Qiskit Certification subject (OpenQASM 2/3) |

**Practice:** read a QASM 2 snippet and predict the circuit (and vice versa); know `OPENQASM 2.0;` + `include "qelib1.inc";` boilerplate, `qreg`/`creg` vs QASM 3 `qubit[n]`/`bit[n]`, `measure q -> c;` syntax, and that `qiskit.qasm3.loads` needs the optional `qiskit_qasm3_import` package. Only ~4 questions — do not over-invest here.

---

## 5-Week Part-Time Prep Schedule

Assumes ~5–7 hours/week. Compress to 4 weeks or stretch to 6 by merging/splitting weeks 2–3.

| Week | Focus (exam sections) | Activities |
|---|---|---|
| **1** | Circuits & operations (§1, §2 — 34%) | Re-read Lesson 06 Modules 1–4; drill `circuit-trainer` and `flashcard-drill` (`qiskit_api`, `gate_unitaries`) daily; hand-write the Bell/GHZ/QFT builders; nail little-endian ordering |
| **2** | Primitives (§4, §5 — 24%) | Lesson 06 Module 7 line by line; write Sampler and Estimator PUBs of every arity from memory; parameter-sweep exercise; quantum-quiz on the Qiskit Certification subject |
| **3** | Running & results (§3, §7 — 25%) | Lesson 06 Module 8 + Lesson 10 Modules 1 & 5; run one real job on IBM hardware end-to-end (free open plan); practice `generate_preset_pass_manager` + result-object navigation; execution modes table from memory |
| **4** | Visualization & OpenQASM (§6, §8 — 17%) | Lesson 06 Module 6 + Lesson 07 Modules 1, 3, 4; generate every plot type against the same Bell state; QASM read/write drills; start IBM Quantum Learning badge quizzes as checkpoints |
| **5** | Integration & mock exam | **Official IBM sample test** on the exam page under timed conditions; review every miss against the study map above; re-drill weak sections with quantum-quiz; book the exam |

**Daily micro-habit throughout:** 10 minutes of `flashcard-drill` (`qiskit_api` category) — API recall is what the 79-seconds-per-question pace actually tests.

---

## External Resources

| Resource | Where | Notes |
|---|---|---|
| Official C1000-179 exam page | ibm.com/training (search "C1000-179") | Objectives, logistics, **official sample test** — the single most exam-representative resource; take it in week 5 |
| IBM Quantum Learning — *Basics of Quantum Information* | learning.quantum.ibm.com | States, measurements, circuits; badge quiz requires **80%** |
| IBM Quantum Learning — *Fundamentals of Quantum Algorithms* | learning.quantum.ibm.com | Query algorithms, Grover, phase estimation; badge quiz requires 80% |
| IBM Quantum Learning — *Variational Algorithm Design* | learning.quantum.ibm.com | Estimator-centric workflows, ansätze; badge quiz requires 80% |
| IBM Quantum Learning — *Quantum Computing in Practice* | learning.quantum.ibm.com | Running on real hardware, primitives, error mitigation — closest to exam sections 3–5, 7 |
| IBM Quantum documentation | quantum.cloud.ibm.com/docs | Canonical API reference — exam answers follow current docs, not old tutorials |
| Qiskit API reference | quantum.cloud.ibm.com/docs/api/qiskit | Check exact signatures when a flashcard feels ambiguous |

---

## Self-Assessment Checklist

Go section by section; every unchecked box maps to a study-map row above. You are ready to book when all boxes check and the official sample test scores comfortably above 69%.

**§1 Create quantum circuits**
- [ ] Can I write `QuantumCircuit(2, 2)` Bell-state prep + measurement from memory, and explain how it differs from `measure_all()`?
- [ ] Can I bind a `ParameterVector` two ways (`assign_parameters` with dict and with list)?
- [ ] Do I know what `qc.compose()`, `qc.append()`, `qc.depth()`, and `qc.count_ops()` each return?

**§2 Perform quantum operations**
- [ ] Can I build `SparsePauliOp(["ZZ", "XX"], coeffs=[1, 0.5])` and predict its matrix dimension?
- [ ] Given `Statevector.from_label('01')`, do I know which qubit is in |1⟩? (little-endian: qubit 0)
- [ ] Can I evolve a state with `sv.evolve(qc)` and extract probabilities without measuring?

**§3 Run quantum circuits**
- [ ] Can I write the service → backend → pass manager → ISA circuit → primitive pipeline from memory?
- [ ] Can I state when to use job mode vs Batch vs Session, in one sentence each?
- [ ] Do I know why `SamplerV2(mode=backend).run([qc])` fails if `qc` is not ISA?

**§4 Sampler primitive**
- [ ] Can I write a SamplerV2 PUB from memory — all three arities, including per-PUB shots?
- [ ] Do I know that Sampler circuits require measurements, and where the creg name resurfaces in results?
- [ ] Can I run three PUBs in one job and index each result?

**§5 Estimator primitive**
- [ ] Can I write an EstimatorV2 PUB from memory — circuit (no measurements!), observables, parameter values, precision?
- [ ] Do I know `result[0].data.evs` vs `.stds`, and what shape `evs` has for a parameter sweep?
- [ ] Can I explain `observable.apply_layout(...)` and the resilience levels 0/1/2?

**§6 Visualization**
- [ ] Given a scenario (counts / probabilities / single-qubit states / global phases / density matrix), can I name the one right plot function?
- [ ] Do I know why a Bell pair's `plot_bloch_multivector` shows zero-length vectors?
- [ ] Do I know the `qc.draw()` output options and the `fold` / `idle_wires` kwargs?

**§7 Retrieve and analyze results**
- [ ] Can I navigate `job.result()[0].data.<creg>.get_counts()` blindfolded, for both `meas` and named cregs?
- [ ] Can I read a counts dict key like `'011'` and say which qubit measured what?
- [ ] Can I retrieve a past job by ID and re-extract its data?

**§8 OpenQASM**
- [ ] Can I hand-write a valid QASM 2 Bell-state program including boilerplate?
- [ ] Can I translate between `qreg q[2];` (QASM 2) and `qubit[2] q;` (QASM 3) styles?
- [ ] Do I know the four `qiskit.qasm2`/`qasm3` functions (`dumps`/`loads` × 2) and the extra package QASM 3 import needs?

---

## Connections

- **Lesson 06 (Qiskit)** is the backbone — its Modules 6–8 map almost one-to-one onto exam sections 3–7.
- **Lesson 07 (QASM)** Modules 1, 3, 4 cover section 8; skip Modules 5–6 for exam purposes (interchange and `defcal` are out of scope).
- **Lesson 10 (Transpiling)** Modules 1 and 5 supply the ISA-circuit / preset-pass-manager knowledge that section 3 tests; the rest of Lesson 10 is deeper than the exam requires.
- **Apps:** `flashcard-drill` (`qiskit_api`) for API recall, `quantum-quiz` (Qiskit Certification subject) for exam-style questions, `circuit-trainer` for circuit arithmetic under time pressure.
