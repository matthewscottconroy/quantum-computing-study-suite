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

  <details><summary>Solution</summary>

  ```python
  from qiskit import QuantumCircuit

  qc = QuantumCircuit(2, 2)      # 2 qubits, 2 classical bits in a creg named 'c'
  qc.h(0)
  qc.cx(0, 1)
  qc.measure([0, 1], [0, 1])     # explicit qubit -> clbit mapping
  ```

  **The difference from `measure_all()`**, verified:

  ```
  explicit cregs: ['c']    ops {'measure': 2, 'h': 1, 'cx': 1}
  measure_all   : ['meas'] ops {'measure': 2, 'h': 1, 'cx': 1, 'barrier': 1}
  ```

  `measure_all()` (a) **adds a new** classical register named `meas` sized to the
  qubit count — it does not reuse an existing creg unless you pass
  `add_bits=False` — and (b) inserts a **barrier** before the measurements. So
  `QuantumCircuit(2, 2)` plus `measure_all()` gives you *four* classical bits, `c`
  and `meas`, which is a classic exam trap.

  The creg name is not cosmetic: it is the attribute you index in a SamplerV2 result,
  `result[0].data.meas.get_counts()` versus `result[0].data.c.get_counts()`.

  </details>

- [ ] Can I bind a `ParameterVector` two ways (`assign_parameters` with dict and with list)?

  <details><summary>Solution</summary>

  All three of these are equivalent (checked with `Operator(...).equiv`):

  ```python
  from qiskit import QuantumCircuit
  from qiskit.circuit import ParameterVector

  t = ParameterVector('t', 3)
  qc = QuantumCircuit(1)
  for i in range(3):
      qc.rz(t[i], 0)

  by_list = qc.assign_parameters([0.1, 0.2, 0.3])          # positional, by sort order
  by_dict = qc.assign_parameters({t[0]: 0.1, t[1]: 0.2, t[2]: 0.3})
  by_vec  = qc.assign_parameters({t: [0.1, 0.2, 0.3]})     # whole vector at once
  ```

  **What to remember.**

  - The **list form binds in `qc.parameters` order**, which is *sorted by name*, not
    insertion order. For a `ParameterVector` the names are `t[0], t[1], …`, so the
    order is the natural one — but mixing plain `Parameter('beta')` and
    `Parameter('alpha')` will bind alphabetically and silently swap your values.
    Always `print(list(qc.parameters))` when in doubt.
  - `assign_parameters` returns a **new circuit** by default; pass `inplace=True` to
    mutate.
  - A dict keyed by the `ParameterVector` itself takes the whole list, which is the
    tidiest form for an ansatz.
  - Partial binding is legal — the result is still parameterised.
  - For the primitives you usually do **not** bind at all: pass the parameter values
    in the PUB and let the primitive broadcast over them.

  </details>

- [ ] Do I know what `qc.compose()`, `qc.append()`, `qc.depth()`, and `qc.count_ops()` each return?

  <details><summary>Solution</summary>

  | call | returns | note |
  |---|---|---|
  | `qc.compose(other)` | a **new `QuantumCircuit`** | `inplace=True` returns `None`; `qubits=[...]` maps wires; the sub-circuit is *inlined*, not boxed |
  | `qc.append(op, qargs)` | an **`InstructionSet`** | mutates `qc` in place; the return value is a handle, *not* the circuit — `qc = qc.append(...)` is a bug |
  | `qc.depth()` | an **`int`** | longest path through the DAG; takes an optional `filter_function` for per-gate-type depth |
  | `qc.count_ops()` | an **`OrderedDict`** name → count | counts what is *currently* in the circuit; a boxed instruction counts as 1 until you `.decompose()` |

  Verified: `compose -> QuantumCircuit | append -> InstructionSet | depth -> int |
  count_ops -> OrderedDict`.

  Two further distinctions the exam likes: `compose` inlines while `append` keeps the
  operation as a single opaque instruction (so `count_ops` and `depth` see one gate,
  not its contents); and `qc.copy()` is a deep copy of the circuit while
  `qc.copy_empty_like()` keeps only the registers.

  </details>

**§2 Perform quantum operations**
- [ ] Can I build `SparsePauliOp(["ZZ", "XX"], coeffs=[1, 0.5])` and predict its matrix dimension?

  <details><summary>Solution</summary>

  ```python
  from qiskit.quantum_info import SparsePauliOp

  op = SparsePauliOp(["ZZ", "XX"], coeffs=[1, 0.5])
  print(op.num_qubits, op.to_matrix().shape)
  ```

  ```
  2 (4, 4)
  ```

  **The reasoning to be able to give instantly.** Each Pauli string has length 2, so
  the operator acts on 2 qubits, so the matrix is `2² × 2² = 4 × 4`. The *number of
  terms* (2 here) has nothing to do with the dimension — it is the length of the
  strings that sets it. `SparsePauliOp` stores the terms symbolically, which is the
  whole point: a 100-qubit Hamiltonian with 5000 terms is a 5000-entry list, not a
  `2¹⁰⁰ × 2¹⁰⁰` matrix, and `to_matrix()` on it would be fatal.

  Related facts worth having ready: all Pauli strings in one `SparsePauliOp` must
  have the same length; `SparsePauliOp.from_list([("ZZ", 1), ("XX", 0.5)])` is the
  alternative constructor; `op.simplify()` combines duplicate terms; and the string
  is written in Qiskit's little-endian order, so in `"ZI"` the `Z` acts on **qubit
  1** and the `I` on qubit 0.

  </details>

- [ ] Given `Statevector.from_label('01')`, do I know which qubit is in |1⟩? (little-endian: qubit 0)

  <details><summary>Solution</summary>

  **Qubit 0 is in `|1⟩`.** Labels are written **left to right from the highest qubit
  index down to qubit 0**, so `'01'` means `q₁ = 0`, `q₀ = 1`.

  Verified:

  ```
  Statevector.from_label('01').data = [0, 1, 0, 0]
  -> the amplitude sits at index 1 = 0b01
  probabilities_dict() = {'01': 1.0}
  ```

  Index `1` in the vector is basis state `|q₁q₀⟩ = |01⟩`, i.e. qubit 0 excited.

  **The same convention, everywhere, is what the exam actually tests:**

  - `Statevector([a, b, c, d])` orders the basis as `|00⟩, |01⟩, |10⟩, |11⟩` with the
    *right-hand* bit being qubit 0.
  - A counts key `'011'` means `q₂ = 0, q₁ = 1, q₀ = 1`.
  - `SparsePauliOp('ZI')` puts `Z` on qubit 1.
  - `qc.draw()` shows `q_0` on the *top* wire, which is the opposite visual order —
    the single most common source of confusion.
  - `plot_histogram` keys and `qc.draw(reverse_bits=True)` let you flip the display
    if you prefer big-endian, but the data model never changes.

  </details>

- [ ] Can I evolve a state with `sv.evolve(qc)` and extract probabilities without measuring?

  <details><summary>Solution</summary>

  ```python
  from qiskit import QuantumCircuit
  from qiskit.quantum_info import Statevector, SparsePauliOp

  qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1)
  sv = Statevector.from_label('00').evolve(qc)      # or just Statevector(qc)
  print(sv.probabilities_dict())
  print(sv.probabilities([0]))                      # marginal on qubit 0
  print(sv.expectation_value(SparsePauliOp('ZZ')).real)
  ```

  Real output:

  ```
  {'00': 0.5, '11': 0.5}
  [0.5 0.5]
  1.0
  ```

  **The point of the checklist item:** no measurement instruction is involved
  anywhere. `evolve` applies the circuit's unitary to the state; `probabilities()`
  and `probabilities_dict()` give the exact Born-rule distribution;
  `expectation_value` gives an exact observable value. Adding `measure` to the
  circuit before `Statevector(qc)` is an error, because a measurement is not a
  unitary.

  Neighbouring API you should also be fluent in: `Statevector(qc)` as shorthand for
  evolving `|0…0⟩`; `sv.sample_counts(shots)` if you *want* sampling noise;
  `sv.draw('latex')`; `partial_trace(sv, [1])` for a reduced `DensityMatrix`; and
  `Operator(qc)` for the full unitary.

  </details>

**§3 Run quantum circuits**
- [ ] Can I write the service → backend → pass manager → ISA circuit → primitive pipeline from memory?

  <details><summary>Solution</summary>

  ```python
  from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
  from qiskit.transpiler import generate_preset_pass_manager

  service = QiskitRuntimeService()                       # 1. authenticate
  backend = service.least_busy(operational=True, simulator=False)   # 2. pick hardware
  pm = generate_preset_pass_manager(optimization_level=1, backend=backend)  # 3. compile
  isa = pm.run(qc)                                       # 4. ISA circuit
  sampler = SamplerV2(mode=backend)                      # 5. primitive
  job = sampler.run([isa], shots=4096)
  result = job.result()                                  # 6. results
  ```

  **Each line, in one sentence.**

  1. `QiskitRuntimeService()` reads saved credentials (`QiskitRuntimeService.save_account(channel=..., token=...)` writes them once).
  2. `service.backend("ibm_...")` for a named device, or `least_busy(operational=True, simulator=False)` to pick one.
  3. `generate_preset_pass_manager(optimization_level=0..3, backend=backend)` builds
     the same pipeline `transpile()` uses.
  4. `pm.run(qc)` returns the **ISA circuit** — native basis, coupling-map-legal,
     physical qubit indices.
  5. The primitive is bound to where it runs with `mode=`: a backend (job mode), a
     `Batch`, or a `Session`.
  6. `job.job_id()`, `job.status()`, and `service.job(job_id)` for later retrieval.

  For an Estimator the only differences are that the circuit carries **no
  measurements** and the observable must be re-indexed with
  `observable.apply_layout(isa.layout)`.

  For local practice with no account, substitute
  `qiskit.primitives.StatevectorSampler` / `StatevectorEstimator` (no transpilation
  required) or a `qiskit_ibm_runtime.fake_provider` backend with `qiskit_aer`.

  </details>

- [ ] Can I state when to use job mode vs Batch vs Session, in one sentence each?

  <details><summary>Solution</summary>

  - **Job mode** (`SamplerV2(mode=backend)`): one independent job per `run` call —
    use it for a single self-contained workload where you do not care how long you
    wait in the queue between submissions.
  - **Batch** (`with Batch(backend=backend) as batch:`): many *independent* jobs
    submitted together and scheduled as one unit — use it when you can generate all
    the circuits up front, such as a parameter sweep, because it removes per-job
    queueing without holding the device idle.
  - **Session** (`with Session(backend=backend) as session:`): a reserved window in
    which your jobs get priority and each one can depend on the previous result —
    use it for iterative, feedback-driven workloads such as a VQE optimisation loop.

  **The distinction the exam tests** is *dependency*: Batch is for workloads whose
  circuits are all known in advance, Session is for workloads where circuit `n+1`
  depends on result `n`. Sessions are the more expensive resource because the device
  sits idle while your classical optimiser thinks, and the session clock keeps
  running, so do not use a Session where a Batch would do.

  </details>

- [ ] Do I know why `SamplerV2(mode=backend).run([qc])` fails if `qc` is not ISA?

  <details><summary>Solution</summary>

  Because the runtime primitives do **no compilation**. `SamplerV2` hands the
  circuit almost directly to the control electronics, so it must already be:

  1. expressed only in the backend's **native basis** (`{CZ, RZ, SX, X}` on Heron,
     `{ECR, RZ, SX, X}` on Eagle) — an `h` or a `ccx` has no pulse definition;
  2. **connectivity-legal** — every two-qubit gate on an edge of the coupling map;
  3. written in **physical qubit indices**, with width equal to the device's qubit
     count, so `qc.num_qubits` matches `backend.num_qubits`.

  Violating any of these raises `IBMInputValueError` ("circuits do not match the
  target ISA"). The fix is always the same: run the circuit through
  `generate_preset_pass_manager(optimization_level=..., backend=backend).run(qc)`
  first.

  This is the single largest change from Qiskit v0.x, where `backend.run()` and the
  removed `execute()` transpiled for you. It was made deliberate so that *you* own
  the compilation — you can inspect the ISA circuit, count its two-qubit gates, and
  choose the optimisation level, rather than having the choice made silently at
  submission time.

  The corollary for Estimator: after `pm.run`, the observable is indexed against the
  original logical qubits and must be mapped too, with
  `observable.apply_layout(isa.layout)`.

  </details>

**§4 Sampler primitive**
- [ ] Can I write a SamplerV2 PUB from memory — all three arities, including per-PUB shots?

  <details><summary>Solution</summary>

  ```python
  from qiskit import QuantumCircuit
  from qiskit.circuit import Parameter
  from qiskit.primitives import StatevectorSampler   # or SamplerV2 from the runtime

  theta = Parameter('θ')
  qc = QuantumCircuit(2)
  qc.h(0); qc.cx(0, 1); qc.rz(theta, 0)
  qc.measure_all()

  sampler = StatevectorSampler(seed=42)
  job = sampler.run(
      [
          (qc, [0.0]),                # 2-tuple: circuit + parameter values
          (qc, [1.5708], 2000),       # 3-tuple: + per-PUB shots, overriding run-level
          (qc, [3.14159]),            # run-level shots again
      ],
      shots=1000,
  )
  for i, r in enumerate(job.result()):
      print(i, r.data.meas.num_shots, r.data.meas.get_counts())
  ```

  (A circuit with no free parameters also accepts the bare 1-tuple `(qc,)`, or even
  the circuit on its own.)

  Real output from exactly that shape (a parameterised Bell circuit):

  ```
  pub 0: shots 1000  {'11': 497, '00': 503}
  pub 1: shots 2000  {'11': 992, '00': 1008}
  pub 2: shots 1000  {'11': 497, '00': 503}
  ```

  **The rules.**

  - A bare circuit is accepted and coerced to `(circuit,)`; a 1-tuple is the explicit
    form.
  - Parameter values are an array broadcast over the PUB's shape — `[0.1, 0.2]` for
    a two-parameter circuit, or a `(5, 2)` array for a five-point sweep, which makes
    `result[0].data.meas` carry a shape-`(5,)` set of results.
  - **Per-PUB shots override the run-level `shots`**, and the run-level value is the
    fallback for PUBs that omit it. Verified above: 2000 versus 1000.
  - `precision` is the Estimator's knob; `shots` is the Sampler's. They are not
    interchangeable.

  </details>

- [ ] Do I know that Sampler circuits require measurements, and where the creg name resurfaces in results?

  <details><summary>Solution</summary>

  **Yes to both, and they are linked.** A Sampler returns *samples of classical
  bits*, so a circuit with no measurement instruction produces no data at all — the
  job fails or returns an empty `DataBin`. (The Estimator is the mirror image:
  measurements are forbidden, because it computes expectation values itself.)

  The creg name resurfaces as the **attribute name on the result's `DataBin`**:

  ```python
  from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
  from qiskit.primitives import StatevectorSampler

  auto = QuantumCircuit(2)
  auto.h(0); auto.cx(0, 1)
  auto.measure_all()                                  # creates a creg called 'meas'

  qr = QuantumRegister(2, 'q'); cr = ClassicalRegister(2, 'alice')
  named = QuantumCircuit(qr, cr)
  named.h(0); named.cx(0, 1); named.measure([0, 1], [0, 1])

  res = StatevectorSampler(seed=1).run([auto, named], shots=500).result()
  print(res[0].data.meas.get_counts())
  print(res[1].data.alice.get_counts(), list(res[1].data.keys()))
  ```

  Verified:

  ```
  named creg access: {'11': 241, '00': 259}   fields: ['alice']
  ```

  If you forget the name, `list(result[0].data.keys())` tells you — there is one
  entry per classical register, which is exactly why circuits with several cregs give
  you several independently addressable result fields. Beyond `get_counts()`, each
  field offers `get_bitstrings()` (one string per shot, in order) and `.array`
  (a `(shots, n_bytes)` `uint8` array), verified as shape `(1000, 1)` for a two-qubit
  circuit at 1000 shots.

  </details>

- [ ] Can I run three PUBs in one job and index each result?

  <details><summary>Solution</summary>

  ```python
  from qiskit import QuantumCircuit
  from qiskit.circuit import Parameter
  from qiskit.primitives import StatevectorSampler

  phi = Parameter('φ')
  circ = QuantumCircuit(2)
  circ.h(0); circ.cx(0, 1); circ.rz(phi, 0)
  circ.measure_all()

  sampler = StatevectorSampler(seed=42)
  job = sampler.run([(circ, [0.0]), (circ, [1.57], 2000), (circ, [3.14])], shots=1000)
  result = job.result()
  for i, pub_result in enumerate(result):
      print(i, pub_result.data.meas.num_shots, pub_result.data.meas.get_counts())
  ```

  ```
  0 1000 {'11': 497, '00': 503}
  1 2000 {'11': 992, '00': 1008}
  2 1000 {'11': 497, '00': 503}
  ```

  **The shape of the result object, which is what the exam really asks:**

  ```
  PrimitiveResult            <- job.result(),  iterable and indexable
    └── result[i]            <- SamplerPubResult, one per PUB, in submission order
          ├── .data          <- DataBin, one attribute per classical register
          │     └── .meas    <- BitArray: .get_counts(), .get_bitstrings(), .array, .num_shots
          └── .metadata      <- shots actually used, backend info
  ```

  One `run` call is one job, so three PUBs cost one queue wait rather than three —
  that is the whole reason PUBs exist. `len(result)` is the number of PUBs;
  `result[i]` never reorders.

  </details>

**§5 Estimator primitive**
- [ ] Can I write an EstimatorV2 PUB from memory — circuit (no measurements!), observables, parameter values, precision?

  <details><summary>Solution</summary>

  ```python
  import numpy as np
  from qiskit import QuantumCircuit
  from qiskit.circuit import Parameter
  from qiskit.primitives import StatevectorEstimator
  from qiskit.quantum_info import SparsePauliOp

  theta = Parameter('θ')
  qc = QuantumCircuit(1); qc.ry(theta, 0)          # NO measurements
  est = StatevectorEstimator(seed=7)
  thetas = np.linspace(0, np.pi, 5)

  est.run([(qc.assign_parameters([0.4]), SparsePauliOp('Z'))])   # 2-tuple: needs a bound circuit
  est.run([(qc, SparsePauliOp('Z'), thetas.reshape(-1, 1))])     # 3-tuple: + parameter values
  est.run([(qc, SparsePauliOp('Z'), thetas.reshape(-1, 1))], precision=0.02)  # + precision
  ```

  A 2-tuple leaves no slot for parameter values, so the circuit must already be bound;
  passing a circuit with a free parameter raises
  `ValueError: The number of values (0) does not match the number of parameters (1)`.

  **The four slots.** `(circuit, observables, parameter_values, precision)` — the
  first two are mandatory, the last two optional, and `precision` can also be set
  once for the whole `run` call.

  **Why no measurements.** The Estimator computes `⟨ψ(θ)|O|ψ(θ)⟩` itself: it derives
  the measurement bases from the observable's Pauli terms and inserts them. A
  circuit that already collapses the state has nothing left to measure, and the job
  is rejected.

  **Observables.** Anything coercible to an observable array —
  `SparsePauliOp`, a `Pauli`, a plain string `"ZZ"`, a dict
  `{"ZZ": 1, "XX": 0.5}`, or a nested list of those, whose *shape* is broadcast
  against the parameter-value shape.

  **`precision`** is the target standard error of the returned expectation value
  (the Estimator converts it to a shot count internally); `precision=0` means "as
  exact as this implementation can be". It is the Estimator's analogue of the
  Sampler's `shots`, and the two are not interchangeable.

  </details>

- [ ] Do I know `result[0].data.evs` vs `.stds`, and what shape `evs` has for a parameter sweep?

  <details><summary>Solution</summary>

  - **`result[0].data.evs`** — the expectation values, one per element of the PUB's
    broadcast shape.
  - **`result[0].data.stds`** — the estimated standard error of each entry, same
    shape. On hardware this is what tells you whether a VQE energy difference is
    real; the local `StatevectorEstimator` reports zeros because it evaluates
    expectation values exactly.

  **The shape is the broadcast of the observables' shape against the parameter
  values' shape.** Verified:

  ```
  1 observable,  5 parameter points   -> evs.shape == (5,)
  2 observables, 5 parameter points   -> evs.shape == (2, 5)
     [[ 1.  0.7071  0. -0.7071 -1. ]     <- <Z>(θ)
      [ 0.  0.7071  1.  0.7071  0. ]]    <- <X>(θ)
  ```

  built by passing `observables` of shape `(2, 1)` and `parameter_values` of shape
  `(1, 5)`. Mismatched shapes are a hard error, not a silent broadcast:

  ```
  ValueError: The observables shape (2,) and the parameter values shape (5,)
  are not broadcastable.
  ```

  which is worth triggering once on purpose so you recognise it. A single
  unparameterised circuit with one observable gives `evs.shape == ()` — a
  zero-dimensional array, so use `float(result[0].data.evs)` rather than indexing it.

  </details>

- [ ] Can I explain `observable.apply_layout(...)` and the resilience levels 0/1/2?

  <details><summary>Solution</summary>

  **`observable.apply_layout(isa_circuit.layout)`.** Transpilation maps your logical
  qubits onto physical ones and widens the circuit to the full device, so an
  observable written against the logical qubits is now pointing at the wrong wires.
  `apply_layout` re-indexes and pads it. Verified on FakeNairobiV2:

  ```
  ZZ  ->  IIIIIZZ        (2-qubit observable -> 7-qubit device, layout [0, 1])
  ```

  Forgetting this is the classic silent-wrong-answer bug: the job runs, returns
  plausible numbers, and measures the wrong qubits. `apply_layout` also accepts an
  explicit index list if you are not using a transpiler layout.

  **Resilience levels** (`estimator.options.resilience_level = 0 | 1 | 2`) trade
  runtime for bias:

  | level | what it does | cost |
  |---|---|---|
  | 0 | no mitigation — raw expectation values | 1× |
  | 1 | TREX: twirled readout error extinction, plus measurement mitigation | small overhead, removes readout bias |
  | 2 | ZNE: zero-noise extrapolation — run at amplified noise and extrapolate to zero | several× the shots, removes much gate bias, adds variance |

  Level 1 is the runtime's default for `EstimatorV2` when you do not set one, and is
  nearly free. Level 2 is worth it when a systematic offset dominates your error
  budget, and harmful when statistical noise already does, because extrapolation
  inflates the variance.

  Two related facts: **Sampler has no resilience levels at all** (mitigation of a raw
  bitstring distribution is not well defined in the same way — it exposes only
  dynamical decoupling and twirling); and the other options worth knowing are
  `options.dynamical_decoupling.enable` (fills idle time with echo pulses) and
  `options.twirling.enable_gates` (Pauli twirling, which turns coherent error into
  stochastic error that mitigation can handle).

  </details>

**§6 Visualization**
- [ ] Given a scenario (counts / probabilities / single-qubit states / global phases / density matrix), can I name the one right plot function?

  <details><summary>Solution</summary>

  | you have… | use | why |
  |---|---|---|
  | a counts dict from a Sampler | `plot_histogram(counts)` | bars are raw shot counts; accepts a list of dicts to overlay runs |
  | probabilities (or quasi-probabilities) | `plot_distribution(probs)` | heights sum to 1; use it for anything normalised, including negative quasi-probabilities from mitigation |
  | a state, and you care about **each qubit separately** | `plot_bloch_multivector(state)` | one Bloch sphere per qubit, from the reduced density matrices |
  | a state, and you care about **amplitudes and relative phases** | `plot_state_qsphere(state)` | one node per basis state: radius = amplitude, colour = phase |
  | a density matrix | `plot_state_city(rho)` | 3-D bars for real and imaginary parts; the only one that shows coherences directly |
  | a single qubit's vector, by hand | `plot_bloch_vector([x, y, z])` | takes the Bloch coordinates, not a state |

  Two more that appear in questions: `plot_state_hinton` (matrix-element magnitudes
  as squares) and `plot_gate_map` / `plot_error_map` / `plot_circuit_layout` (device
  topology, calibration data and where your circuit landed — all in
  `qiskit.visualization`).

  The discriminating questions to ask yourself are: *counts or probabilities?*
  (histogram versus distribution) and *per-qubit or global?* (Bloch versus qsphere).
  Note also that all of these need `pip install "qiskit[visualization]"` —
  `matplotlib`, `pylatexenc` and `seaborn` are not core dependencies.

  </details>

- [ ] Do I know why a Bell pair's `plot_bloch_multivector` shows zero-length vectors?

  <details><summary>Solution</summary>

  Because `plot_bloch_multivector` plots the **reduced** state of each qubit, and for
  a maximally entangled pair that reduced state is maximally mixed. For
  `(|00⟩+|11⟩)/√2`:

  ```
  partial_trace(sv, [1]) = [[0.5, 0  ],
                            [0,   0.5]]
  Bloch vector (⟨X⟩, ⟨Y⟩, ⟨Z⟩) = (0, 0, 0)   -> length 0.0
  purity Tr(ρ²) = 0.5
  ```

  The Bloch vector's length is exactly the purity measure: `|r| = √(2 Tr(ρ²) − 1)`,
  which is 1 for a pure state and 0 for the maximally mixed state. All the
  information in a Bell pair is in the *correlations* between the qubits, and a
  per-qubit picture cannot show a correlation — locally each qubit is a fair coin.

  **The exam point:** the vanishing vectors are not a bug or a numerical artefact,
  they are the signature of maximal entanglement, and the right plot for that state
  is `plot_state_qsphere` (two nodes of equal radius at `|00⟩` and `|11⟩`, same
  colour, so equal phase) or `plot_state_city` on the density matrix (which shows the
  off-diagonal coherences). A product state such as `|+⟩|0⟩` gives full-length Bloch
  vectors, so comparing the two plots side by side is a quick entanglement check.

  </details>

- [ ] Do I know the `qc.draw()` output options and the `fold` / `idle_wires` kwargs?

  <details><summary>Solution</summary>

  **Outputs**: `qc.draw(output=...)` takes

  - `'text'` — ASCII art, the default, works anywhere, returns a `TextDrawing`;
  - `'mpl'` — a matplotlib `Figure`, needs `matplotlib` (and `pylatexenc` for nicely
    typeset gate labels);
  - `'latex'` — a PIL image rendered through LaTeX, needs a working LaTeX install;
  - `'latex_source'` — the raw LaTeX string, which always works and is handy for
    papers.

  **The two kwargs named in the checklist:**

  - `fold=n` — sets pagination, and means slightly different things per backend: in
    `'text'` it is the **line length in characters** (default `None`, which guesses
    the console width via `shutil.get_terminal_size()`, or 80 in Jupyter); in
    `'mpl'` it is the **number of visual layers before wrapping**, default 25.
    `fold=-1` disables folding entirely. Set `fold=200` or `fold=-1` to stop a wide
    circuit being chopped into unreadable strips.
  - `idle_wires=False` — hide qubits that carry no operations. Essential after
    transpiling to a 127-qubit device, where otherwise you get 125 empty lines around
    your two-qubit circuit.

  Others worth knowing: `reverse_bits=True` (display big-endian, without changing the
  data model), `plot_barriers=False`, `initial_state=True`, `with_layout=False` (hide
  the `q_0 -> 3` annotations on a transpiled circuit), `cregbundle`, `scale`,
  `filename=` to save, and `style=` for colours.

  </details>

**§7 Retrieve and analyze results**
- [ ] Can I navigate `job.result()[0].data.<creg>.get_counts()` blindfolded, for both `meas` and named cregs?

  <details><summary>Solution</summary>

  ```
  job.result()          -> PrimitiveResult        (iterable, indexable, len == #PUBs)
        [0]             -> SamplerPubResult       (one per PUB, submission order)
        .data           -> DataBin                (one attribute per classical register)
        .meas           -> BitArray               (the register named 'meas')
        .get_counts()   -> dict[str, int]
  ```

  So:

  - `measure_all()` creates a register called `meas`, hence
    `job.result()[0].data.meas.get_counts()`.
  - `ClassicalRegister(2, 'alice')` gives
    `job.result()[0].data.alice.get_counts()` — verified: `{'11': 241, '00': 259}`.
  - `QuantumCircuit(2, 2)` names its register `c`, hence `...data.c.get_counts()`.
  - When you cannot remember, `list(result[0].data.keys())` lists the fields.
  - A circuit with several cregs yields several independent fields, which is how you
    read out a mid-circuit measurement separately from the final one.

  Beyond `get_counts()`, the same `BitArray` gives `get_bitstrings()` (one string per
  shot, in shot order — needed for post-selection or per-shot correlations),
  `.array` (raw `uint8`, shape `(shots, ceil(nbits/8))`), and `.num_shots`.

  Estimator results use the same tree with a different leaf:
  `result[0].data.evs` and `result[0].data.stds` instead of a per-creg `BitArray`.

  </details>

- [ ] Can I read a counts dict key like `'011'` and say which qubit measured what?

  <details><summary>Solution</summary>

  `'011'` means **`q₂ = 0`, `q₁ = 1`, `q₀ = 1`** — the leftmost character is the
  highest-numbered qubit, the rightmost is qubit 0.

  The trap is that `qc.draw()` puts `q_0` on the **top** wire, so the visual order
  and the string order are mirror images. A useful habit: read a counts key
  right-to-left while reading a circuit diagram top-to-bottom.

  Two refinements that show up in questions:

  - With **multiple classical registers**, `get_counts()` on a single field gives
    only that register's bits. A whole-job counts string (as produced by Aer's
    `result.get_counts()` on a circuit with several cregs) separates registers with
    **spaces**, in reverse register-declaration order — for example
    `'0 1 1'` for the three one-bit registers of the teleportation circuit.
  - The bit index inside a register follows the `measure(qubit, clbit)` mapping you
    wrote, not the qubit index. `measure(0, 1)` puts qubit 0's outcome in classical
    bit 1, which is the *second character from the right*.

  If big-endian display suits you better, `plot_histogram(counts)` has no reversal
  option but `qc.draw(reverse_bits=True)` flips the diagram, and
  `''.join(reversed(key))` flips the key — the underlying data model never changes.

  </details>

- [ ] Can I retrieve a past job by ID and re-extract its data?

  <details><summary>Solution</summary>

  ```python
  from qiskit_ibm_runtime import QiskitRuntimeService

  service = QiskitRuntimeService()

  job = sampler.run([isa])
  jid = job.job_id()              # save this
  print(job.status())             # 'QUEUED' | 'RUNNING' | 'DONE' | 'ERROR' | 'CANCELLED'

  # later, in a completely different session:
  old = service.job(jid)
  result = old.result()           # same PrimitiveResult tree as before
  counts = result[0].data.meas.get_counts()
  ```

  **What else to know.**

  - `service.jobs(limit=10, backend_name="ibm_...", created_after=...)` lists recent
    jobs when you did not save the id; `job.inputs` and `job.metrics()` recover what
    was submitted and how long it queued.
  - Results are retained by IBM for a limited period, so a job id is not a permanent
    archive — persist the results you care about yourself.
  - `job.cancel()` while queued, `job.error_message()` when the status is `ERROR`.
  - `job.result()` **blocks** until the job finishes; the status poll is the
    non-blocking form.
  - Results survive the session that created them: the id, not the `Session` or
    `Batch` context, is what ties you to the data.
  - This is the one topic with no offline substitute — `QiskitRuntimeService()` raises
    `AccountNotFoundError` without saved credentials, and local primitives have no job
    store. Learn the call names; you can only exercise them against a real account.

  </details>

**§8 OpenQASM**
- [ ] Can I hand-write a valid QASM 2 Bell-state program including boilerplate?

  <details><summary>Solution</summary>

  ```
  OPENQASM 2.0;
  include "qelib1.inc";
  qreg q[2];
  creg c[2];
  h q[0];
  cx q[0],q[1];
  measure q[0] -> c[0];
  measure q[1] -> c[1];
  ```

  That is byte-for-byte what `qiskit.qasm2.dumps(qc)` produces for
  `QuantumCircuit(2, 2)` with `h(0); cx(0,1); measure([0,1],[0,1])`, and
  `qiskit.qasm2.loads(...)` round-trips it back to `{'measure': 2, 'h': 1, 'cx': 1}`.

  **The five boilerplate facts you must not lose marks on:**

  1. `OPENQASM 2.0;` is the first non-comment line, with the semicolon.
  2. `include "qelib1.inc";` — without it, `h` and `cx` are undefined. (QASM 3 uses
     `include "stdgates.inc";`.)
  3. `qreg name[size];` and `creg name[size];` declare registers; QASM 2 has no other
     types.
  4. Statements end in semicolons; arguments to two-qubit gates are comma-separated
     with the control first.
  5. `measure q[i] -> c[j];` uses the arrow. QASM 3 writes the same thing as
     `c[j] = measure q[i];`.

  Also legal and sometimes asked about: `barrier q;`, `reset q[0];`, `U(θ,φ,λ) q[0];`
  and `CX a,b;` as the two built-in primitives, `gate myg a,b { ... }` for
  user-defined gates, and `if (c==3) x q[0];` as QASM 2's only (deprecated) control
  flow.

  </details>

- [ ] Can I translate between `qreg q[2];` (QASM 2) and `qubit[2] q;` (QASM 3) styles?

  <details><summary>Solution</summary>

  The same Bell circuit in both dialects, as emitted by Qiskit:

  | QASM 2 | QASM 3 |
  |---|---|
  | `OPENQASM 2.0;` | `OPENQASM 3.0;` |
  | `include "qelib1.inc";` | `include "stdgates.inc";` |
  | `qreg q[2];` | `qubit[2] q;` |
  | `creg c[2];` | `bit[2] c;` |
  | `h q[0];` | `h q[0];` |
  | `cx q[0],q[1];` | `cx q[0], q[1];` |
  | `measure q[0] -> c[0];` | `c[0] = measure q[0];` |

  **The shape of the change.** QASM 2 declares registers verb-first
  (`qreg name[n]`); QASM 3 is a *typed* language and declares them type-first
  (`qubit[n] name`, `bit[n] name`), alongside `int`, `float`, `angle`, `bool`,
  `duration` and `stretch`. Measurement becomes an ordinary expression assignment.

  **Why it matters beyond syntax.** QASM 3 is what makes dynamic circuits
  expressible: real `if (c == 1) { x q[1]; }` blocks, `while`, `for`, subroutines
  (`def`), classical arithmetic on measurement results, and timing (`delay`,
  `barrier` with durations). QASM 2's `if (c==3)` could only compare a whole register
  to a constant, and nothing else classical was possible. Any circuit built with
  `with qc.if_test(...)` can be serialised to QASM 3 and not to QASM 2.

  </details>

- [ ] Do I know the four `qiskit.qasm2`/`qasm3` functions (`dumps`/`loads` × 2) and the extra package QASM 3 import needs?

  <details><summary>Solution</summary>

  The four functions, two per module:

  ```python
  from qiskit import QuantumCircuit, qasm2, qasm3

  bell = QuantumCircuit(2, 2)
  bell.h(0); bell.cx(0, 1); bell.measure([0, 1], [0, 1])

  src2 = qasm2.dumps(bell)    # QuantumCircuit -> str
  qasm2.loads(src2)           # str            -> QuantumCircuit
  src3 = qasm3.dumps(bell)    # QuantumCircuit -> str
  qasm3.loads(src3)           # str            -> QuantumCircuit  (needs the extra package)
  ```

  plus the file-based `dump(qc, file)` / `load(file)` variants in both modules.

  **The extra package.** `qiskit.qasm3.dumps` (export) is built in, but
  `qiskit.qasm3.loads` (import) is backed by the optional **`qiskit-qasm3-import`**
  package. Without it you get

  ```
  MissingOptionalLibraryError: "The 'qiskit_qasm3_import' library is required to ..."
  ```

  (`qiskit.qasm3.loads`/`load` are decorated with
  `HAS_QASM3_IMPORT.require_in_call`.) Install with
  `pip install qiskit-qasm3-import`, or via the extra
  `pip install "qiskit[qasm3-import]"`. Nothing extra is needed for QASM 2 in either
  direction, nor for QASM 3 *export*.

  **Round-tripping caveats worth a mark.** `qasm2.dumps` fails on gates that have no
  `qelib1.inc` equivalent — decompose or supply a `gate` definition first — and on
  any dynamic-circuit construct. Parameterised circuits cannot be exported to QASM 2
  with free parameters; bind them first. And a round trip is not guaranteed to
  preserve register names, gate boxing, or the exact gate set, only the semantics.

  Section 8 is roughly 4 questions out of 68 — know the four function names, the two
  include files, the register declarations, and the measure syntax, then move on.

  </details>

---

## Connections

- **Lesson 06 (Qiskit)** is the backbone — its Modules 6–8 map almost one-to-one onto exam sections 3–7.
- **Lesson 07 (QASM)** Modules 1, 3, 4 cover section 8; skip Modules 5–6 for exam purposes (interchange and `defcal` are out of scope).
- **Lesson 10 (Transpiling)** Modules 1 and 5 supply the ISA-circuit / preset-pass-manager knowledge that section 3 tests; the rest of Lesson 10 is deeper than the exam requires.
- **Apps:** `flashcard-drill` (`qiskit_api`) for API recall, `quantum-quiz` (Qiskit Certification subject) for exam-style questions, `circuit-trainer` for circuit arithmetic under time pressure.
