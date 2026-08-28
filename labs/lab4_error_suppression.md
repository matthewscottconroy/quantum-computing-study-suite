# Lab 4 — Error Suppression: Dynamical Decoupling and Pauli Twirling

**Goal:** turn on dynamical decoupling (DD) and Pauli twirling through
`SamplerV2`/`EstimatorV2` options, measure their effect on a GHZ observable on
hardware, and — because the effect only exists where there is real noise —
reproduce both mechanisms locally with hand-built Aer noise models.

**Estimated time:** 90 minutes local + optional hardware runs.

**Verified against:** `qiskit-ibm-runtime` 0.49.0, `qiskit-aer` 0.17.2. The
options schema below was read from the installed package; both local
experiments in Part B were executed and matched their analytic predictions.

---

## Part A — The runtime options (hardware path)

### The options, as installed (v0.49.0)

`SamplerOptions` and `EstimatorOptions` both carry:

```text
dynamical_decoupling:
    enable: bool                      (default False)
    sequence_type: "XX" | "XpXm" | "XY4"     (default "XX")
    extra_slack_distribution: "middle" | "edges"
    scheduling_method: "alap" | "asap"
    skip_reset_qubits: bool
twirling:
    enable_gates: bool                # 2-qubit Clifford (Pauli) gate twirling
    enable_measure: bool              # measurement (readout) twirling
    num_randomizations: int | "auto"
    shots_per_randomization: int | "auto"
    strategy: "active" | "active-accum" | "active-circuit" | "all"
```

Sequence meanings (from the installed docstrings): `"XX"` is
`τ/2 - X - τ - X - τ/2`; `"XpXm"` replaces the second pulse with −X to cancel
pulse-calibration errors; `"XY4"` is the 4-pulse sequence that also refocuses
X/Y-axis noise. For the Estimator, twirling defaults are tied to
`resilience_level` (gates twirled at level 2, measurements at levels 1–2) — so
**set `resilience_level=0` when you want to isolate the suppression effects**.

### GHZ experiment on hardware

```python
# [HARDWARE] Four estimator jobs: {DD off/on} x {twirling off/on}.
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService

service = QiskitRuntimeService()
backend = service.least_busy(min_num_qubits=127)

n = 6                                   # use your Lab 3 best chain!
ghz = QuantumCircuit(n)
ghz.h(0)
for i in range(n - 1):
    ghz.cx(i, i + 1)

pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa = pm.run(ghz)
# GHZ coherence witness: <X^n> = 1 ideally, and it is the quantity that
# dephasing during idle windows destroys -- exactly what DD protects.
obs = SparsePauliOp("X" * n).apply_layout(isa.layout)

results = {}
for dd in (False, True):
    for tw in (False, True):
        est = EstimatorV2(mode=backend)
        est.options.resilience_level = 0            # no mitigation; isolate suppression
        est.options.dynamical_decoupling.enable = dd
        est.options.dynamical_decoupling.sequence_type = "XY4"
        est.options.twirling.enable_gates = tw
        est.options.twirling.enable_measure = tw
        est.options.twirling.num_randomizations = 32
        est.options.twirling.shots_per_randomization = 128
        job = est.run([(isa, obs)])
        results[(dd, tw)] = job.job_id()
        print(f"DD={dd} twirl={tw}: job {job.job_id()}")

# Later:
# for k, jid in results.items():
#     ev = service.job(jid).result()[0].data.evs
#     print(k, float(ev))
```

**Expected on hardware:** ⟨X⊗…⊗X⟩ well below 1 in all cases; DD typically
helps most when the transpiled circuit has long idle windows (deep chains,
wide devices); twirling changes the *character* of the error (unbiased,
shot-noise-like) more than its size, which is exactly why mitigation methods
(Lab 5) require it.

> **Local-mode warning (verified):** if you pass a fake backend as `mode=`,
> these options are silently ignored — local testing mode maps onto
> `BackendSamplerV2`/`BackendEstimatorV2`, which don't implement DD or
> twirling. That's why Part B builds the physics by hand.

---

## Part B — Local fallback: build both effects yourself (runs without an account)

Both experiments below were **executed during authoring**; observed numbers are
quoted after each.

### B1. Dynamical decoupling refocuses quasi-static dephasing

Model low-frequency dephasing as a coherent `RZ(0.4)` attached to every
`delay` instruction. A Ramsey-style sequence accumulates the phase; inserting
an X-pulse between two equal idle windows refocuses it (the second window's
phase is echoed away — see the spin-echo discussion in
[docs/07_quantum_hardware/01_superconducting_qubits.md](../docs/07_quantum_hardware/01_superconducting_qubits.md)).

```python
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RZGate
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, coherent_unitary_error


def main():
    theta = 0.4
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(
        coherent_unitary_error(RZGate(theta).to_matrix()), ["delay"]
    )
    sim = AerSimulator(noise_model=nm)

    # no DD: sx . idle . idle . sx   (sx.sx = X, so ideal P(1) = 1)
    plain = QuantumCircuit(1)
    plain.sx(0)
    plain.delay(100, 0, unit="ns")
    plain.delay(100, 0, unit="ns")
    plain.sx(0)
    plain.measure_all()

    # DD: an X between the idles echoes the static phase; trailing X restores frame
    dd = QuantumCircuit(1)
    dd.sx(0)
    dd.delay(100, 0, unit="ns")
    dd.x(0)
    dd.delay(100, 0, unit="ns")
    dd.x(0)
    dd.sx(0)
    dd.measure_all()

    shots = 20000
    for label, qc in [("no DD", plain), ("with DD", dd)]:
        counts = sim.run(transpile(qc, sim), shots=shots).result().get_counts()
        print(f"{label:8s} P(1) = {counts.get('1', 0) / shots:.4f}")


if __name__ == "__main__":
    main()
```

**Observed:** `no DD P(1) = 0.8484`, `with DD P(1) = 1.0000`. The no-DD value
matches the prediction cos²(θ) = cos²(0.4) ≈ 0.8484 exactly. (Why cos²θ and
not cos²(2θ/2)·something: the two idles accumulate total phase 2θ; the second
`sx` converts phase 2θ into population cos²(2θ/2) = cos²θ.)

DD does **not** help against Markovian T1 decay — only against noise with
memory (quasi-static/low-frequency), which is what this model captures.

To see the production insertion mechanics (rather than hand-placed pulses),
this pass pipeline was also verified to run on a FakeTorino-transpiled circuit:

```python
from qiskit.circuit.library import XGate
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes.scheduling import ALAPScheduleAnalysis, PadDynamicalDecoupling

dd_pm = PassManager([
    ALAPScheduleAnalysis(target=backend.target),
    PadDynamicalDecoupling(dd_sequence=[XGate(), XGate()], target=backend.target),
])
padded = dd_pm.run(isa)     # X gates appear in idle windows
```

### B2. Pauli twirling converts coherent error into stochastic error

Attach a coherent `RX(ε)` overrotation to every `cz`. In a string of N
identity-composing CZs, coherent amplitude errors add *linearly* → probability
error (Nε/2)². Twirling (conjugating each CZ by random Paulis, with the
compensating Pauli `P' = CZ·P·CZ†` on the far side) makes each error an
independent coin flip → probability error ~N(ε/2)². For N=24, ε=0.06:

```python
import random
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RXGate
from qiskit.quantum_info import Operator, Pauli
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, coherent_unitary_error


def build_twirl_table():
    """For each 2-qubit Pauli P, find P' with CZ.P = P'.CZ (up to phase)."""
    CZ = Operator(np.diag([1, 1, 1, -1]))
    labels = [a + b for a in "IXYZ" for b in "IXYZ"]
    table = []
    for lab in labels:
        p = Operator(Pauli(lab))
        pprime = CZ @ p @ CZ.adjoint()
        for lab2 in labels:
            q = Operator(Pauli(lab2))
            nz = np.abs(q.data) > 1e-9
            if np.allclose(np.abs(pprime.data), np.abs(q.data)):
                vals = pprime.data[nz] / q.data[nz]
                if np.allclose(vals, vals[0]):
                    table.append((lab, lab2))
                    break
    assert len(table) == 16
    return table


def apply_pauli(qc, label):
    for idx, ch in enumerate(reversed(label)):     # little-endian
        if ch != "I":
            getattr(qc, ch.lower())(idx)


def main():
    eps, n_cz, shots = 0.06, 24, 4096
    err = coherent_unitary_error(np.kron(np.eye(2), RXGate(eps).to_matrix()))
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(err, ["cz"])
    sim = AerSimulator(noise_model=nm)

    # raw: 24 CZs on |00> (identity circuit); coherent RX drift accumulates
    raw = QuantumCircuit(2)
    for _ in range(n_cz):
        raw.cz(0, 1)
    raw.measure_all()
    c = sim.run(transpile(raw, sim, optimization_level=0), shots=shots).result().get_counts()
    p_raw = c.get("00", 0) / shots

    # twirled: P . CZ . P'  per gate, averaged over randomizations
    table = build_twirl_table()
    rng = random.Random(42)
    n_rand, acc = 32, 0.0
    for _ in range(n_rand):
        qc = QuantumCircuit(2)
        for _ in range(n_cz):
            p, pprime = table[rng.randrange(16)]
            apply_pauli(qc, p)
            qc.cz(0, 1)
            apply_pauli(qc, pprime)
        qc.measure_all()
        c = sim.run(transpile(qc, sim, optimization_level=0), shots=512).result().get_counts()
        acc += c.get("00", 0) / sum(c.values())
    p_tw = acc / n_rand

    print(f"raw      P(00) = {p_raw:.4f}   predicted cos^2(N*eps/2) = {np.cos(n_cz * eps / 2)**2:.4f}")
    print(f"twirled  P(00) = {p_tw:.4f}   predicted ((1+cos eps)/2)^N = {((1 + np.cos(eps)) / 2)**n_cz:.4f}")


if __name__ == "__main__":
    main()
```

**Observed:** `raw P(00) = 0.5657` (prediction 0.5652) vs
`twirled P(00) = 0.9716` (prediction 0.9786). Coherent buildup cost ~43% of
survival probability; the twirled, stochastic version cost ~3%. This is the
quadratic-vs-linear accumulation argument made concrete — and it's why
hardware options enable twirling before any mitigation is attempted.

---

## Verification checkpoint

**You should see:**

- B1: `P(1) = 0.8484 ± 0.01` without DD (= cos² 0.4) and `1.0000` with DD.
- B2: raw survival within a few σ of 0.565; twirled survival near 0.97,
  dramatically above raw.
- `PadDynamicalDecoupling` inserts a nonzero number of `x` gates into the
  transpiled circuit (check `padded.count_ops()['x'] > isa.count_ops().get('x', 0)`).
- Hardware (optional): the DD-on GHZ ⟨X…X⟩ at least matches, usually beats,
  DD-off; twirl-on estimates have error bars consistent with unbiased noise.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Options had no effect | You ran in local testing mode — options are ignored there (verified behavior). Use Part B locally, options only on hardware. |
| `ValueError` setting `sequence_type` | Only `"XX"`, `"XpXm"`, `"XY4"` are accepted (v0.49.0). |
| Twirled result *worse* than raw | Check the twirl table: the compensating Pauli must satisfy CZ·P = P'·CZ. Using P on both sides (instead of P') breaks the circuit for X/Y-type Paulis. |
| DD demo shows no difference | The noise must be attached to `delay` instructions and be *coherent*. `transpile(..., optimization_level=0)` matters too — higher levels may remove your delays or Paulis. |
| Hardware DD makes things worse | Real pulse errors: each DD pulse is itself imperfect. Try `"XpXm"` (self-cancelling calibration error) and `skip_reset_qubits=True`. |
| Estimator results already look mitigated | `resilience_level` defaulted above 0 and enabled twirling/TREX under you. Pin `resilience_level = 0` for controlled comparisons. |
