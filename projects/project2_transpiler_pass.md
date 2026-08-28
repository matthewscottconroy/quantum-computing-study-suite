# Project 2 — A Custom Transpiler Pass, Tested and Benchmarked

**Deliverable:** a peephole optimization pass — a **CX–RZ–CX fuser** — written
as a proper Qiskit `TransformationPass`, with a correctness test suite
(unitary-equivalence based), integration into a preset pass manager, and a
benchmark over random circuits reporting gate-count and depth reductions.

**Background:** the pattern `CX(c,t) · RZ(θ, t) · CX(c,t)` equals a ZZ-type
interaction: it acts as `RZZ`-like phase `exp(-i θ/2 Z_c ⊗ Z_t)` up to
framing — and when two such blocks are adjacent, or when the enclosed rotation
is trivial, gates cancel. Peephole passes find local windows like this in the
DAG and rewrite them. This is exactly how production transpilers claw back
depth. Read [docs/03_quantum_gates_and_circuits/03_circuit_model_and_universality.md](../docs/03_quantum_gates_and_circuits/03_circuit_model_and_universality.md)
and all of [lesson 10 (Transpiling)](../lesson-plans/10-transpiling.md) first.

Verified against the venv (executed): `TransformationPass` subclassing,
`dag.op_nodes()`, `dag.remove_op_node(node)`, `dag.collect_runs([...])`,
`qiskit.circuit.random.random_circuit`, and `PassManager([...]).run(qc)` all
work as used below on Qiskit 2.5.2.

---

## Milestones

### M1 — Identity-elimination warm-up

Write `DropIdentityRZ(TransformationPass)` removing `rz` nodes with angle ≡ 0
(mod 4π, within tolerance). This exact skeleton was executed against the venv:

```python
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.dagcircuit import DAGCircuit

class DropIdentityRZ(TransformationPass):
    def run(self, dag: DAGCircuit) -> DAGCircuit:
        for node in dag.op_nodes():
            if node.op.name == "rz" and abs(float(node.op.params[0])) < 1e-12:
                dag.remove_op_node(node)
        return dag
```

**Acceptance criteria:**
- [ ] `PassManager([DropIdentityRZ()]).run(qc)` removes `rz(0)` and keeps
      `rz(1e-3)` (verified behavior: `{'cx': 2, 'rz': 1}` → `{'cx': 2}`).
- [ ] Angle handling: `rz(4π)` removed, `rz(2π)` **not** removed blindly — it
      is a global phase −1 on paper but identity as a gate action; decide,
      document, and test your convention.
- [ ] Parameterized `rz(θ)` (unbound `Parameter`) is left untouched (test).

### M2 — The CX–RZ–CX fuser

`CXRZCXFuser(TransformationPass)`: find windows where a `cx(c,t)` is followed
(on both wires, with nothing between on the control wire and only the `rz` on
the target wire) by `rz(θ, t)` then `cx(c,t)`, and rewrite:

- θ ≡ 0: drop all three gates (after M1's convention).
- adjacent fusable blocks `[CX·RZ(θ₁)·CX]·[CX·RZ(θ₂)·CX]` → single
  `CX·RZ(θ₁+θ₂)·CX` (the middle CX pair cancels).

**Correctness definition:** `Operator(original) == Operator(optimized)` up to
global phase — use `qiskit.quantum_info.Operator(...).equiv(...)`.

**Acceptance criteria:**
- [ ] Handles the interleaved-wire trap: a gate on the *control* qubit between
      the CXs must block the rewrite (test with `cx; rz(t); x(c); cx` — must
      not fuse).
- [ ] Direction trap: `cx(0,1) rz(1) cx(1,0)` must not fuse (test).
- [ ] 200 random 4-qubit circuits (`random_circuit(4, depth=8, seed=i)`,
      transpiled to `["cx", "rz", "sx", "x"]` first): pass output is
      `Operator`-equivalent to input for **every** seed.
- [ ] Property: running the pass twice = running it once (idempotence test).

### M3 — Pass manager integration

Register the pass inside a real pipeline: append it to
`generate_preset_pass_manager(optimization_level=2, ...)` via the pass
manager's staged structure (hint: `pm.optimization += your_stage` — inspect
`StagedPassManager` attributes; document what you find).

**Acceptance criteria:**
- [ ] A Bell+phase test circuit transpiled *with* your stage has strictly
      fewer 2-qubit gates than *without*, and remains ISA-valid for
      `FakeManilaV2` (its target accepts the output).
- [ ] The pass cooperates with routing: run against `FakeTorino` and confirm
      output still respects the coupling map.

### M4 — Benchmark

Benchmark on ≥ 300 random circuits across widths {3, 5, 8} and depths
{10, 30, 100}, each first transpiled to the `cx/rz/sx/x` basis, seeding a
generator that *plants* fusable patterns in half the circuits (otherwise pure
random circuits contain few windows — report both populations separately).

**Acceptance criteria:**
- [ ] CSV of: seed, width, depth, planted?, cx before/after, depth
      before/after, wall-time of the pass.
- [ ] Summary table: mean CX reduction on planted circuits ≥ 20%; honest
      reporting of (near-zero) reduction on unplanted ones.
- [ ] Pass runtime scales roughly linearly in gate count (plot or table).

### M5 — Write-up

**Acceptance criteria:**
- [ ] `NOTES.md` covering: the rewrite rules with a small derivation (show the
      CX·RZ·CX = ZZ-phase identity by multiplying 4×4 matrices), the traps M2
      caught, benchmark results, and one paragraph on what a production
      version would need (commutation analysis, `collect_runs`-style
      window extraction, symbolic parameters).

---

## Starter scaffolding hints

- Wire-following: `dag.op_nodes()` gives nodes; for each node,
  successors along a specific wire come from `dag.edges(node)` /
  `node.qargs`. Alternatively `dag.collect_runs(["cx", "rz"])` (verified
  callable) hands you candidate runs per wire — but note it returns
  *single-wire* runs; you must still validate the control wire is clean.
- Rewriting: for surgical replacement build a small `QuantumCircuit`, convert
  with `circuit_to_dag`, and use `dag.substitute_node_with_dag`; for deletion
  `dag.remove_op_node` (verified) is enough.
- Test helper: `assert Operator(before).equiv(Operator(after))` — write it
  once as `assert_equiv(qc1, qc2)`.
- Random-circuit basis normalization:
  `transpile(rc, basis_gates=["cx", "rz", "sx", "x"], optimization_level=0)`
  keeps the transpiler from doing your optimization for you.

## Stretch goals

- Generalize to `CX·(RZ⊗RZ)·CX` and to `cz`-basis devices (FakeTorino's basis
  is `cz` — verified).
- Add a `commutation`-aware version: let single-qubit gates that commute with
  Z slide through the window on the target wire.
- Compare against `optimization_level=3` alone: does your pass still find
  anything after Qiskit's own peepholes? Report honestly.
- Submit-quality polish: docstrings, type hints, and an `entry_points`-style
  plugin registration sketch (see Qiskit's transpiler-plugin docs).

## References

- [lesson-plans/10-transpiling.md](../lesson-plans/10-transpiling.md) — the whole pipeline
- [docs/03_quantum_gates_and_circuits/03_circuit_model_and_universality.md](../docs/03_quantum_gates_and_circuits/03_circuit_model_and_universality.md) — gate identities
- [docs/03_quantum_gates_and_circuits/04_quantum_circuit_complexity.md](../docs/03_quantum_gates_and_circuits/04_quantum_circuit_complexity.md) — why depth matters
- [labs/lab3_reading_calibration.md](../labs/lab3_reading_calibration.md) — targets/coupling maps you'll transpile against
