# IBM Hardware Lab Track

Five hands-on labs that take you from a fresh IBM Quantum account to a complete
hardware VQE workflow. Everything before job submission is verified against the
packages installed in this repo's `.venv`:

| Package | Version verified |
|---|---|
| `qiskit` | 2.5.2 |
| `qiskit-ibm-runtime` | 0.49.0 |
| `qiskit-aer` | 0.17.2 |

Run all lab code with the project interpreter: `.venv/bin/python`.

---

## The Labs

| Lab | Topic | Needs an IBM account? |
|---|---|---|
| [Lab 1](lab1_account_and_first_job.md) | Account setup, backends, first Bell-state job | Yes (final step) |
| [Lab 2](lab2_sessions_and_batch.md) | Job vs. batch vs. session execution modes | Yes (final step) |
| [Lab 3](lab3_reading_calibration.md) | Reading calibration data; best-linear-chain selector | **No** — runs on a fake backend |
| [Lab 4](lab4_error_suppression.md) | Dynamical decoupling and Pauli twirling | No for the local variant; yes for hardware |
| [Lab 5](lab5_full_workflow.md) | Capstone: end-to-end VQE-style estimation | No for checkpoints 1–3; yes for checkpoint 4 |

Do them in order. Labs 3 and 4 (local variant) are fully executable offline and
were run successfully against `qiskit_ibm_runtime.fake_provider` backends during
authoring.

---

## Prerequisites

1. **A free IBM Quantum Platform account on IBM Cloud.** IBM's quantum services
   now live on IBM Cloud (the standalone IBM Quantum Platform at
   quantum-computing.ibm.com was sunset). Sign up at
   [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com), create an instance on
   the **Open plan** (free), and copy your API key.
2. **The `ibm_quantum_platform` channel.** This is the channel string that
   `QiskitRuntimeService` uses for the IBM Cloud-based platform. The installed
   `qiskit-ibm-runtime` accepts `channel` values
   `"ibm_quantum_platform"`, `"ibm_cloud"`, and `"local"` (verified against
   v0.49.0). Use `"ibm_quantum_platform"` for real hardware and `"local"` (or
   just a fake backend as `mode=`) for offline testing.
3. **Lesson background.** Lessons [06 (Qiskit)](../lesson-plans/06-qiskit.md)
   and [10 (Transpiling)](../lesson-plans/10-transpiling.md), plus
   [docs chapter 07 (Quantum Hardware)](../docs/07_quantum_hardware/) for what
   T1/T2 and gate errors physically mean.

---

## Conventions Used in Every Lab

- Cells marked **`[HARDWARE]`** submit real jobs and require a saved account.
  Everything else runs locally.
- All scripts wrap their entry point in `if __name__ == "__main__":`. This is
  not just style: on this machine (Python 3.14, Linux forkserver start method),
  Qiskit's parallel transpilation re-imports the main module in worker
  processes, and unguarded module-level code can crash or re-execute. This was
  observed directly while authoring these labs.
- Counts keys are **little-endian**: in the string `"01"`, the rightmost
  character is qubit 0.
- An "ISA circuit" is a circuit transpiled to the backend's Instruction Set
  Architecture (its basis gates + coupling map). Runtime primitives **reject
  non-ISA circuits** — you must transpile before `run()`.

---

## Safety Notes: Queue Times and Quotas

- **The Open plan gives you 10 minutes of quantum time per 28-day window**
  (check your current allocation on the platform dashboard — plans change).
  A single carelessly-shaped job can burn a meaningful fraction of it.
- **Quantum time ≠ wall-clock time.** You are billed for time the QPU spends on
  your workload, not time in the queue. But queues on free-tier backends
  routinely run from minutes to many hours. Never sit in a blocking
  `job.result()` call in a terminal you might close — record `job.job_id()` and
  retrieve results later with `service.job(job_id)`.
- **Estimate before you submit.** After submission, `job.usage_estimation`
  reports estimated quantum seconds; `job.usage()` and `job.metrics()` report
  actuals afterwards. Cancel anything surprising with `job.cancel()`.
- **Sessions are not available on the Open plan** (dedicated sessions are a
  paid-plan feature; the Open plan supports job mode and batch mode). Lab 2's
  session code is written so you can run it if you have a paid/educational
  instance and read it if you don't.
- **Shots discipline.** 4096 shots is plenty for every lab here. Default-shot
  settings of primitives can be higher than you need.
- **Do everything on a fake backend first.** Passing
  `FakeTorino()` (or any `fake_provider` backend) as `mode=` to `SamplerV2` /
  `EstimatorV2` runs the identical code path locally with a realistic noise
  model — for free. Every lab uses this pattern before touching hardware.
