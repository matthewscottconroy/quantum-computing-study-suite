# Lab 2 — Execution Modes: Job, Batch, and Session

**Goal:** understand the three ways to run workloads on IBM hardware, know when
each is the right tool, and write correct code for all three.

**Estimated time:** 45 minutes reading + coding; hardware execution optional.

**Verified against:** `qiskit-ibm-runtime` 0.49.0 — all constructor signatures
and methods below were checked by inspection of the installed package
(`Session(backend, max_time=None)`, `Batch(backend, max_time=None)`,
`SamplerV2(mode=...)`, `Session.details/status/usage/close/from_id`).

---

## The three modes in one table

| | **Job mode** | **Batch mode** | **Session mode** |
|---|---|---|---|
| What it is | One standalone primitive job | A group of independent jobs scheduled together | A time window with (near-)exclusive device access |
| `mode=` argument | a backend | a `Batch` | a `Session` |
| Queuing | Each job queues normally | The whole batch queues once; jobs inside run back-to-back with parallelized classical overhead | You queue to *open* the session; then your jobs skip the public queue until it closes |
| Best for | One-shot experiments; anything in this repo's labs | Many *independent* circuits known up front (parameter sweeps, benchmarking suites) | *Iterative* workloads where the next job depends on the last result (VQE, QAOA, calibration loops) |
| Cost profile | Pay per job's QPU time | Pay per job's QPU time; less total overhead than N separate jobs | Pay (on most paid plans) for the wall-clock window you hold, including your own think-time between jobs |
| Open (free) plan | ✅ | ✅ | ❌ not available |

**Decision rule:** independent circuits, all known now → batch. A classical
optimizer in the loop → session (if your plan has it) or job mode with patience
(the free-plan VQE reality — see Lab 5). Just one thing to run → job mode.

**Cost/queue implications worth internalizing:**

- Batch ≈ same quantum time as separate jobs, but *one* queue wait instead of
  N, and the service parallelizes the classical pre/post-processing.
- A session is the only mode with a *reservation* character: between jobs the
  device sits idle **on your clock**. A slow classical optimizer inside a
  session wastes reserved time. Keep the classical step fast or close the
  session between phases.
- `max_time` caps how long a batch/session can live (seconds or strings like
  `"2h"`). Sessions also auto-close after a plan-dependent idle timeout.
- Always use the context-manager form — an unclosed session keeps billing
  until it times out.

---

## Mode 1 — Job mode

```python
# [HARDWARE] one standalone job
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

service = QiskitRuntimeService()
backend = service.least_busy(min_num_qubits=127)

sampler = SamplerV2(mode=backend)        # backend as mode == job mode
job = sampler.run([isa_bell], shots=4096)
```

That's what Lab 1 did. Nothing more to it.

---

## Mode 2 — Batch mode

Scenario: estimate ⟨Z⟩ for the same ansatz at 12 pre-chosen parameter points
(a sweep — independent, known up front).

```python
# [HARDWARE] one batch containing one job with 12 PUBs
import numpy as np
from qiskit.circuit.library import efficient_su2
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import Batch, EstimatorV2, QiskitRuntimeService

service = QiskitRuntimeService()
backend = service.least_busy(min_num_qubits=127)

ansatz = efficient_su2(4, reps=1)
pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa = pm.run(ansatz)
obs = SparsePauliOp("ZZZZ").apply_layout(isa.layout)

sweep = [np.random.uniform(-np.pi, np.pi, ansatz.num_parameters)
         for _ in range(12)]

with Batch(backend=backend, max_time="30m") as batch:
    estimator = EstimatorV2(mode=batch)
    # One PUB per parameter point; you could also split into several jobs
    # inside the batch and they would be scheduled together.
    job = estimator.run([(isa, obs, x) for x in sweep])

result = job.result()
energies = [float(pub.data.evs) for pub in result]
```

Note the subtlety: **a single job with many PUBs is often enough** — you only
need multiple jobs in a batch when the PUBs would exceed job-size limits or
when you want partial results early.

---

## Mode 3 — Session mode

Scenario: an optimizer picks the next parameters from the last energy —
serially dependent, so batch can't help.

```python
# [HARDWARE — paid/educational plans only; Open plan will reject this]
from qiskit_ibm_runtime import Session, EstimatorV2
from scipy.optimize import minimize

with Session(backend=backend, max_time="1h") as session:
    estimator = EstimatorV2(mode=session)

    def cost(params):
        return float(estimator.run([(isa, obs, params)]).result()[0].data.evs)

    out = minimize(cost, x0, method="COBYLA", options={"maxiter": 40})

# leaving the `with` block closes the session -> billing stops
```

Session bookkeeping (all verified methods):

```python
session.status()      # e.g. 'In progress'
session.details()     # dict: id, backend, timestamps, activated/closed ...
session.usage()       # seconds of usage attributed to the session
Session.from_id("SESSION_ID", service)   # re-attach from another process
```

---

## Offline rehearsal

Local testing mode ignores batch/session semantics but accepts the same code
shape, so you can dry-run the batch sweep by replacing the service lookup with:

```python
from qiskit_ibm_runtime.fake_provider import FakeTorino
backend = FakeTorino()
# ... and use EstimatorV2(mode=backend) directly instead of the Batch context.
```

(Verified: `EstimatorV2(mode=FakeTorino()).run([...])` returns a
`LocalRuntimeJob` with the same result interface.)

---

## Verification checkpoint

**You should see:**

- Batch sweep: 12 energy values; for a `reps=1` `efficient_su2` with random
  parameters, values scattered roughly in (−1, 1) — the point is that they all
  came back from *one* queue wait.
- Session run: `session.details()` shows the session id and its backend, and
  jobs submitted inside carry `job.session_id == session.session_id`.
- On the Open plan, constructing a `Session` job fails with a clear
  plan-related error — that is itself the expected observation; switch the
  code to batch or job mode.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Session creation rejected / plan error | You're on the Open plan. Sessions require a paid or educational instance. Use batch. |
| Batch jobs run far apart rather than back-to-back | Jobs inside a batch are only co-scheduled if submitted while the batch is active; make sure all `run()` calls happen inside the `with` block. |
| Session seems to bill while "nothing is running" | That's the model — the reservation clock runs between your jobs. Close sessions promptly; don't keep humans in the loop mid-session. |
| `max_time` exceeded errors | Batch/session hit its cap mid-workload. Raise `max_time` or split the workload. |
| Results needed from a crashed script | `service.jobs(limit=10)` lists recent jobs; `Session.from_id(...)` / `service.job(id)` re-attach. Nothing is lost with job IDs recorded. |
