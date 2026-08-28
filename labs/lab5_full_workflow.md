# Lab 5 — Capstone: End-to-End VQE-Style Estimation on Hardware

**Goal:** run the full Qiskit pattern — **map → optimize → execute →
post-process** — for a VQE-style ground-state estimation of the H₂ molecule,
first entirely locally (verified), then on hardware with error suppression and
mitigation dialed in.

**Estimated time:** 2–3 hours local; hardware run adds queue time and consumes
several minutes of quantum time — read the cost box in checkpoint 4 first.

**Verified against:** `qiskit` 2.5.2, `qiskit-ibm-runtime` 0.49.0. Checkpoints
1–3 were executed during authoring; observed numbers are quoted.

**Prerequisites:** Labs 1–4;
[docs/06_variational_quantum_algorithms/01_vqe_fundamentals.md](../docs/06_variational_quantum_algorithms/01_vqe_fundamentals.md);
lesson [09](../lesson-plans/09-quantum-algorithm-design.md). This lab is the
hardware companion of [projects/project1_vqe_h2.md](../projects/project1_vqe_h2.md)
— the project builds the science, this lab builds the hardware execution.

---

## Step 0 — The problem (map)

The H₂ Hamiltonian at bond distance 0.735 Å, already mapped to 2 qubits
(parity mapping + Z₂ reduction; the project derives this, here we take it as
given):

```python
from qiskit.quantum_info import SparsePauliOp

H = SparsePauliOp.from_list([
    ("II", -1.052373245772859),
    ("IZ",  0.39793742484318045),
    ("ZI", -0.39793742484318045),
    ("ZZ", -0.01128010425623538),
    ("XX",  0.18093119978423156),
])
```

---

## Checkpoint 1 — Exact reference (post-process target)

```python
import numpy as np
exact = min(np.linalg.eigvalsh(H.to_matrix()))
print(f"exact ground energy: {exact:.6f} Ha")
```

**You should see:** `-1.857275 Ha` (observed: −1.8572750302023795). Every
later number is judged against this.

---

## Checkpoint 2 — Optimize: ISA circuit + observable layout

```python
from qiskit.circuit.library import efficient_su2
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime.fake_provider import FakeManilaV2

backend = FakeManilaV2()          # 5-qubit fake device for local work
ansatz = efficient_su2(H.num_qubits, reps=2)
print("parameters:", ansatz.num_parameters)

pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa = pm.run(ansatz)
H_isa = H.apply_layout(isa.layout)
```

Notes verified against the installed packages:

- `efficient_su2` (lowercase function, `qiskit.circuit.library`) is the
  Qiskit 2.x way; the class `EfficientSU2` still exists but the function form
  returns a plain `QuantumCircuit`. With `reps=2` on 2 qubits:
  **12 parameters**.
- `H.apply_layout(isa.layout)` expands the 2-qubit observable to the device
  width with the transpiled layout — forgetting this is the #1 crash in
  hardware VQE (`Estimator` rejects mismatched qubit counts).

**You should see:** `parameters: 12`, and `H_isa` is a 5-qubit operator whose
support sits exactly on `isa.layout.final_index_layout()`.

---

## Checkpoint 3 — Execute locally (verified end-to-end)

```python
import numpy as np
from scipy.optimize import minimize
from qiskit_ibm_runtime import EstimatorV2


def main():
    # ... build H, backend, isa, H_isa as above ...
    estimator = EstimatorV2(mode=backend)      # local testing mode

    history = []

    def cost(params):
        ev = estimator.run([(isa, H_isa, params)], precision=0.01).result()[0].data.evs
        history.append(float(ev))
        return float(ev)

    rng = np.random.default_rng(7)
    x0 = rng.uniform(-np.pi, np.pi, ansatz.num_parameters)
    res = minimize(cost, x0, method="COBYLA", options={"maxiter": 80})
    print(f"VQE energy: {res.fun:.6f} Ha  after {len(history)} evaluations")
    print(f"error vs exact: {(res.fun - exact) * 1000:.1f} mHa")


if __name__ == "__main__":
    main()
```

**Observed during authoring** (seed 7, 80 COBYLA evaluations, ~27 s wall):

```
exact ground state:   -1.857275 Ha
VQE (noisy backend):  -1.819532 Ha after 80 evaluations
error: 37.7 mHa
```

**You should see:** convergence to within **~20–60 mHa** of −1.857 Ha. You
will *not* hit chemical accuracy (1.6 mHa) on a noisy backend without
mitigation — that gap is the point: FakeManila's noise model costs you ~40 mHa.
(A noiseless `AerSimulator` run of the same code reaches < 2 mHa; try it.)

---

## Checkpoint 4 — Execute on hardware

> **Cost box.** Each cost-function call is one job. 80 iterations = 80 jobs.
> On the Open plan (~10 min quantum time per window, **no sessions**) a full
> optimization loop is not realistic. Two honest strategies:
>
> 1. **Optimize locally, validate on hardware** (recommended, done below):
>    converge on the fake backend, then spend hardware time on a handful of
>    final-point evaluations.
> 2. **Session-based loop** (paid/educational plans): wrap the Checkpoint 3
>    loop in `Session` per Lab 2, with `maxiter` ≤ 40.

```python
# [HARDWARE] a few evaluations at the locally-optimized point
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2
from qiskit.transpiler import generate_preset_pass_manager

service = QiskitRuntimeService()
hw = service.least_busy(min_num_qubits=127)

pm_hw = generate_preset_pass_manager(optimization_level=3, backend=hw)
isa_hw = pm_hw.run(ansatz)               # re-transpile for the real target!
H_hw = H.apply_layout(isa_hw.layout)

est = EstimatorV2(mode=hw)
est.options.resilience_level = 1                     # TREX measurement mitigation
est.options.dynamical_decoupling.enable = True       # Lab 4
est.options.dynamical_decoupling.sequence_type = "XY4"
est.options.twirling.enable_gates = True
est.options.twirling.enable_measure = True

x_opt = res.x                             # from checkpoint 3
job = est.run([(isa_hw, H_hw, x_opt)], precision=0.01)
print("job:", job.job_id())
# later:
r = job.result()[0]
print(f"hardware energy: {float(r.data.evs):.6f} +/- {float(r.data.stds):.6f} Ha")
```

Options escalation to experiment with (all fields verified in
`EstimatorOptions.resilience` for v0.49.0): `measure_mitigation`,
`zne_mitigation` with `zne.noise_factors` / `zne.extrapolator`, and (expensive)
`pec_mitigation`. Try `resilience_level = 2` (adds ZNE + gate twirling) and
compare error bars and quantum-time usage via `job.usage()`.

**You should see:** a hardware energy between roughly −1.75 and −1.86 Ha at
resilience 1; moving to resilience 2 should pull the estimate toward −1.857
with larger error bars and 5–10× the quantum time.

---

## Checkpoint 5 — Post-process and report

Produce a small table — this is the deliverable:

| Setting | Energy (Ha) | Error vs exact (mHa) | Quantum seconds |
|---|---|---|---|
| Exact diagonalization | −1.857275 | 0 | — |
| Noiseless Aer | | | — |
| FakeManila (local) | −1.819532 | 37.7 | — |
| Hardware, resilience 1 + DD + twirl | | | |
| Hardware, resilience 2 | | | |

Then plot `history` (energy vs iteration) — COBYLA on a noisy backend should
show a fast drop in the first ~30 evaluations, then a noise floor.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `Estimator` rejects the PUB: observable/circuit qubit mismatch | Forgot `apply_layout(isa.layout)`, or applied the *local* layout to the *hardware* circuit. Each target needs its own transpile + layout application. |
| Energy stuck near 0 or −1.0 | Optimizer trapped: ansatz too shallow, unlucky seed, or (on hardware) noise floor above the feature. Restart with a new seed; try `reps=1` (fewer parameters can optimize *better* under noise). |
| Runs crash with forkserver/`ConnectionResetError` on this machine | Module-level Qiskit code without an `if __name__ == "__main__":` guard (observed on Python 3.14 + forkserver during authoring). Guard your entry point. |
| Hardware numbers worse than fake-backend numbers | Expected sometimes — snapshots lag real calibration. Use Lab 3 to pick a good layout region and pass `initial_layout`. |
| Quantum time vanishing fast | You looped `est.run` per Hamiltonian *term*. One PUB estimates the whole `SparsePauliOp` at once — never decompose by hand. |
| `res.fun` differs run-to-run by ~10 mHa locally | Shot noise at `precision=0.01` plus COBYLA's stochastic path. Tighten precision only at the end — cost scales as 1/precision². |
