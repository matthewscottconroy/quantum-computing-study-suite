# Lab 3 — Reading Calibration Data and Picking Good Qubits

**Goal:** explore `backend.target` — per-gate error rates, T1/T2 coherence
times, readout errors — and build a "best linear chain" selector that finds the
highest-fidelity path of connected qubits on a device.

**Estimated time:** 60 minutes. **No IBM account needed** — the whole lab runs
against `qiskit_ibm_runtime.fake_provider.FakeTorino`, and every snippet below
was executed successfully during authoring.

---

## Background

`least_busy()` optimizes for queue time, not quality. Real devices are wildly
heterogeneous: on the FakeTorino calibration snapshot used below, readout error
spans **0.6% to 16.7%** across qubits, and T1 spans ~60 µs to ~230 µs. Choosing
qubits well is often worth more than any error-mitigation option you can turn
on. The `Target` object is the machine-readable calibration database.

See [docs/07_quantum_hardware/04_benchmarking_and_characterization.md](../docs/07_quantum_hardware/04_benchmarking_and_characterization.md)
for what these numbers mean physically.

---

## Step 1 — Open the target

```python
from qiskit_ibm_runtime.fake_provider import FakeTorino

backend = FakeTorino()
target = backend.target
print(backend.name, backend.num_qubits)      # fake_torino 133
print(list(target.operation_names))
```

Observed: `['rz', 'reset', 'delay', 'switch_case', 'cz', 'measure', 'x',
'for_loop', 'if_else', 'id', 'sx']` — a **cz-basis** heavy-hex device with
dynamic-circuit support. (On a real backend, `service.backend("ibm_...")` gives
you the same `Target` interface; this lab is drop-in compatible.)

---

## Step 2 — Per-gate errors

`target[gate_name]` maps qubit tuples → `InstructionProperties(duration, error)`:

```python
cz_props = target["cz"]
for qubits, props in list(cz_props.items())[:5]:
    print(qubits, f"error={props.error:.5f}", f"duration={props.duration*1e9:.0f} ns")

meas = target["measure"]
worst = max(meas.items(), key=lambda kv: kv[1].error)
best = min(meas.items(), key=lambda kv: kv[1].error)
print("best readout:", best[0], f"{best[1].error:.4f}")
print("worst readout:", worst[0], f"{worst[1].error:.4f}")
```

Observed on the snapshot: `cz` on `(0, 1)` has error ≈ 0.00485; readout ranges
from 0.0063 to 0.1667. **A single bad qubit can dominate your whole circuit's
error budget.**

Gate direction matters: a pair may appear as `(a, b)` only. When you look up an
edge, try both orientations (the selector below does).

---

## Step 3 — T1/T2 via qubit properties

```python
for q in range(5):
    qp = target.qubit_properties[q]
    print(f"q{q}: T1={qp.t1*1e6:7.1f} us   T2={qp.t2*1e6:7.1f} us")
```

Verified details for this runtime version:

- `target.qubit_properties` is a list of `QubitProperties(t1, t2, frequency)`.
- **T1/T2 are in seconds** — multiply by 1e6 for microseconds.
- `frequency` can be `None` on some fake-backend snapshots (it is on
  FakeTorino), so don't assume it's populated.

Sanity rule from [docs chapter 02](../docs/02_quantum_mechanics/05_density_matrices_and_open_systems.md):
physically T2 ≤ 2·T1. Snapshots occasionally violate related folklore
(T2 > T1 is fine and common); T2 ≫ 2·T1 signals stale calibration data.

---

## Step 4 — Build the best-linear-chain selector

Linear chains are what you need for GHZ states, 1-D Trotter circuits, and the
repetition codes of [docs chapter 05](../docs/05_quantum_error_correction/03_repetition_code.md).
Score a chain by the product of (1 − error) over one round of nearest-neighbor
2-qubit gates plus readout on every qubit:

```python
"""Best linear chain selector. Executed successfully against FakeTorino."""


def gate_error(target, name, qubits):
    props = target[name].get(qubits)
    if props is None:                     # try the reversed orientation
        props = target[name].get(tuple(reversed(qubits)))
    return props.error if props is not None else None


def chain_fidelity(backend, chain):
    """Fidelity proxy: one layer of 2q gates along the chain + readout."""
    target = backend.target
    twoq = next(g for g in ("cz", "ecr", "cx") if g in target.operation_names)
    fid = 1.0
    for a, b in zip(chain, chain[1:]):
        err = gate_error(target, twoq, (a, b))
        if err is None:
            return 0.0
        fid *= 1.0 - err
    for q in chain:
        fid *= 1.0 - target["measure"][(q,)].error
    return fid


def coupling_neighbors(backend):
    neighbors = {}
    for a, b in backend.coupling_map.get_edges():
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
    return neighbors


def best_linear_chain(backend, length):
    """Exhaustive DFS over simple paths. Heavy-hex degree <= 3 keeps this
    fast for length up to ~12 (measured: ~1 s for length 6 on 133 qubits)."""
    neighbors = coupling_neighbors(backend)
    best = (0.0, None)

    def extend(path):
        nonlocal best
        if len(path) == length:
            f = chain_fidelity(backend, path)
            if f > best[0]:
                best = (f, list(path))
            return
        for nxt in neighbors[path[-1]]:
            if nxt not in path:
                path.append(nxt)
                extend(path)
                path.pop()

    for start in neighbors:
        extend([start])
    return best


def main():
    from qiskit_ibm_runtime.fake_provider import FakeTorino

    backend = FakeTorino()
    fid, chain = best_linear_chain(backend, 6)
    print(f"best 6-qubit chain on {backend.name}: {chain}")
    print(f"estimated chain fidelity: {fid:.4f}")
    t = backend.target
    for q in chain:
        qp = t.qubit_properties[q]
        print(f"  q{q}: T1={qp.t1*1e6:8.1f} us  T2={qp.t2*1e6:8.1f} us  "
              f"readout_err={t['measure'][(q,)].error:.4f}")


if __name__ == "__main__":
    main()
```

---

## Step 5 — Use the chain

Feed the chain to the transpiler as an initial layout so your GHZ/chain circuit
actually lands on those physical qubits:

```python
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager

n = 6
ghz = QuantumCircuit(n)
ghz.h(0)
for i in range(n - 1):
    ghz.cx(i, i + 1)
ghz.measure_all()

pm = generate_preset_pass_manager(
    optimization_level=3, backend=backend, initial_layout=chain
)
isa = pm.run(ghz)
```

---

## Verification checkpoint

**You should see** (exact numbers vary with the calibration snapshot in your
installed package version; these are from the authoring run):

```
best 6-qubit chain on fake_torino: [8, 17, 27, 28, 29, 36]
estimated chain fidelity: 0.8927
  q8: T1=   232.2 us  T2=    31.4 us  readout_err=0.0183
  ...
```

Checks that must hold regardless of snapshot:

- consecutive chain qubits are all edges of `backend.coupling_map`;
- chain fidelity for length 6 lands well above the *average* random chain
  (spot-check a few random paths — expect the best chain to beat them);
- every readout error on the chosen chain is below the device's worst-case.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `KeyError` when indexing `target["cx"]` | The device's 2-qubit gate is `cz` or `ecr`, not `cx`. Discover it from `target.operation_names` as the code above does. |
| `props.error is None` for some edges | Some snapshots omit values; treat missing data as disqualifying (the selector returns 0.0 fidelity). |
| T1/T2 look absurd (e.g. 0.0002) | They're in seconds. 0.0002 s = 200 µs — healthy. |
| Selector is slow for long chains | DFS over simple paths grows fast beyond length ~12. Prune: skip extending any path whose partial fidelity is already below the current best. |
| Transpiled circuit ignores your chain | Pass `initial_layout=chain` to `generate_preset_pass_manager` (verified parameter), and check `isa.layout.final_index_layout()` afterwards — routing may still insert SWAPs if your logical circuit isn't chain-shaped. |
