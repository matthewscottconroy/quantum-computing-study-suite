# Lab 1 — Account Setup and Your First Hardware Job

**Goal:** save IBM Quantum credentials, explore available backends, pick the
least-busy one, transpile a Bell-state circuit to its ISA, submit it through
`SamplerV2`, and read back real-hardware counts.

**Estimated time:** 30–45 minutes of work + queue time (minutes to hours).

**Verified against:** `qiskit` 2.5.2, `qiskit-ibm-runtime` 0.49.0. All code up
to job submission was executed locally; the `[HARDWARE]` cells were validated
for API correctness against the installed package but require an account to run.

---

## Step 1 — Save your account (one time only)

Get your API key from [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com)
(it's on the dashboard). Then, in a Python session:

```python
# [HARDWARE-ADJACENT] Requires your API key, but submits nothing.
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",   # the IBM Cloud-based platform
    token="YOUR_API_KEY_HERE",
    # instance="crn:...",             # optional: pin a specific instance CRN;
                                      # omit to let the service pick one
    set_as_default=True,
    overwrite=True,                   # replace an older saved account
)
```

Credentials land in `~/.qiskit/qiskit-ibm.json`. From now on,
`QiskitRuntimeService()` with no arguments uses them.

> Signature check (v0.49.0): `save_account(token=None, url=None, instance=None,
> channel=None, filename=None, name=None, proxies=None, verify=None,
> overwrite=False, set_as_default=None, private_endpoint=False, region=None,
> plans_preference=None, tags=None)`. `region` and `plans_preference` let you
> steer which instance is auto-selected if you have several.

**Offline rehearsal:** you can rehearse every remaining step without an account
by replacing the service lookup with a fake backend — shown in Step 6.

---

## Step 2 — List backends

```python
# [HARDWARE-ADJACENT] Queries the cloud API; costs no quantum time.
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
for b in service.backends():
    status = b.status()
    print(f"{b.name:20s} {b.num_qubits:4d} qubits   "
          f"pending jobs: {status.pending_jobs:5d}   operational: {status.operational}")
```

Useful filters (all verified parameters of `service.backends()`):

```python
service.backends(min_num_qubits=127)
service.backends(dynamic_circuits=True)
service.backends(filters=lambda b: b.status().pending_jobs < 50)
```

---

## Step 3 — Pick the least-busy backend

```python
backend = service.least_busy(min_num_qubits=127)
print(backend.name)
```

`least_busy()` accepts `min_num_qubits`, `instance`, and `filters`. "Least
busy" means fewest pending jobs — it says nothing about calibration quality;
Lab 3 teaches you to choose on error rates instead.

---

## Step 4 — Build the Bell circuit and transpile to ISA

```python
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa_circuit = pm.run(qc)

print(isa_circuit.count_ops())
print("layout:", isa_circuit.layout.final_index_layout())
```

Two things to notice:

- `generate_preset_pass_manager` lives in **`qiskit.transpiler`** in Qiskit 2.x
  (verified import).
- On current IBM devices your `h` and `cx` disappear: the ISA circuit contains
  only the native set (e.g. `cz`/`ecr`, `sx`, `x`, `rz`, plus `measure`), and
  your 2 virtual qubits are mapped onto 2 physical qubits chosen by the
  transpiler (layout).

---

## Step 5 — Submit through SamplerV2 and retrieve counts

```python
# [HARDWARE] This submits a real job and consumes quantum time.
from qiskit_ibm_runtime import SamplerV2

sampler = SamplerV2(mode=backend)          # "job mode": one standalone job
job = sampler.run([isa_circuit], shots=4096)
print("job id:", job.job_id())
print("estimated usage:", job.usage_estimation)
```

Don't block on the result if the queue is long. Come back later:

```python
# [HARDWARE-ADJACENT] Retrieval; no new quantum time.
job = service.job("YOUR_JOB_ID")
print(job.status())                        # 'QUEUED' / 'RUNNING' / 'DONE'

result = job.result()                      # blocks until done
pub_result = result[0]                     # one PUB (circuit) was submitted
counts = pub_result.data.meas.get_counts() # 'meas' = register from measure_all()
print(counts)
print("quantum seconds used:", job.usage())
```

The register accessor is named after your classical register: `measure_all()`
creates a register called `meas`, hence `data.meas`. If you had used
`qc.measure(range(2), range(2))` with an explicit `ClassicalRegister(2, "c")`,
it would be `data.c`.

---

## Step 6 — The same thing, offline (verified end-to-end)

This exact pattern was executed successfully during authoring:

```python
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2
from qiskit_ibm_runtime.fake_provider import FakeTorino


def main():
    backend = FakeTorino()                 # 133-qubit snapshot, cz basis
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
    isa_circuit = pm.run(qc)

    sampler = SamplerV2(mode=backend)      # local testing mode -> LocalRuntimeJob
    job = sampler.run([isa_circuit], shots=4096)
    counts = job.result()[0].data.meas.get_counts()
    print(counts)


if __name__ == "__main__":
    main()
```

Observed output: `{'11': 2004, '00': 2006, '01': 55, '10': 31}`.

---

## Verification checkpoint

**You should see:** counts dominated by `00` and `11` in roughly equal
proportion, with a few percent of leakage into `01`/`10`. On the fake backend
above, ~98% of shots landed in the two correlated outcomes. On real hardware
expect anywhere from ~90–99% depending on the device and the qubits chosen. If
`00` and `11` together are below ~85%, something is off (bad qubit pair, or you
skipped transpilation-driven layout).

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `AccountNotFoundError` on `QiskitRuntimeService()` | `save_account` never ran, or ran under a different channel. Re-run Step 1 with `overwrite=True`. |
| `IBMInputValueError` about instances | Your key has multiple instances; pass `instance="crn:..."` (find the CRN on the cloud dashboard) or set `plans_preference`. |
| Error that the circuit doesn't match the target / uses unsupported gates | You submitted the untranspiled circuit. Primitives require ISA circuits — run the preset pass manager first. |
| `data.meas` attribute missing | Your classical register isn't named `meas`. Use the register's actual name, or inspect `pub_result.data` fields. |
| Counts look uniform random | You measured before entangling, transpiled with `initial_layout` onto dead qubits, or the backend was recently recalibrated. Check `backend.properties`-style data via Lab 3 and rerun. |
| Job stuck in `QUEUED` for hours | Normal on free tier. Do not cancel-and-resubmit (you lose your queue position). Retrieve later by job ID. |
