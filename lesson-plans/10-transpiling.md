# Transpiling for Quantum Computing

## Goal
Gain deep expertise in quantum circuit transpilation — the compilation process that maps abstract circuits to hardware-executable form — including routing, gate synthesis, optimization passes, and custom pass development.

---

## Module 1 — What Is Transpilation?

**Objective:** Understand the full transpilation pipeline and why it is essential for running on real quantum hardware.

### The Problem

Abstract quantum circuits specify *what* to compute, not *how* to run it on a specific chip. Hardware imposes:

| Constraint | Example |
|---|---|
| Native gate set | `{CX, RZ, SX, X}` on IBM hardware |
| Qubit connectivity | Not all-to-all; defined by coupling map |
| Gate fidelity variation | Some two-qubit pairs have much better fidelity |
| Calibration drift | Gates are recalibrated daily |
| Circuit depth limits | Coherence time sets max depth |

### The Pipeline (Qiskit)

```
Abstract Circuit
       │
  [Translation]    — decompose gates into basis gates
       │
  [Routing]        — insert SWAP gates to satisfy connectivity
       │
  [Optimization]   — minimize gate count and depth
       │
  [Scheduling]     — assign timing to parallel gates
       │
Hardware-Ready ISA Circuit
```

---

## Module 2 — Basis Translation

**Objective:** Decompose arbitrary unitaries into a hardware's native gate set.

### Standard Decompositions

**Single-qubit decomposition (ZYZ):**
Any U ∈ SU(2) can be written:
```
U = e^(iα) Rz(β) Ry(γ) Rz(δ)
```

**IBM native gates: {CX, RZ, SX, X}**

| Abstract Gate | Native Decomposition |
|---|---|
| H | `RZ(π/2) · SX · RZ(π/2)` |
| S | `RZ(π/2)` |
| T | `RZ(π/4)` |
| SWAP | 3× CX (or 3× iSWAP) |
| CZ | `H · CX · H` |
| Toffoli | 6× CNOT + single-qubit gates |

**Solovay-Kitaev for discrete gate sets:**
- Any single-qubit U can be approximated to error ε using O(log^c(1/ε)) gates from {H, T, CNOT}
- c ≈ 3.97 in practice (improved to ~1.5 with modern variants)
- Use for fault-tolerant contexts where only Clifford + T is available

**In Qiskit:**
```python
from qiskit import transpile

# Decompose to IBM basis
qc_t = transpile(qc, basis_gates=['cx', 'rz', 'sx', 'x'])
print(qc_t.count_ops())
```

**Exercises:**
- Manually decompose a Toffoli gate into {CX, H, T, Tdg}
- Verify your decomposition using Qiskit's `Operator` equivalence check
- Count the CX depth of a 3-qubit QFT after basis translation

---

## Module 3 — Qubit Routing

**Objective:** Map logical qubits to physical qubits satisfying the hardware coupling map.

### The Problem

A two-qubit gate `CX(q0, q1)` requires q0 and q1 to be physically adjacent. If they're not, insert SWAPs to move them together.

**SWAP cost:** 3 CX gates — expensive!

### Routing Algorithms

| Algorithm | Strategy | Quality | Speed |
|---|---|---|---|
| Stochastic SWAP | Random SWAP insertion + scoring | Good | Fast |
| SABRE | Lookahead heuristic, bidirectional | Better | Moderate |
| SABRE (v2) | Improved heuristic | State of the art | Moderate |
| Exact (ILP) | Integer linear program, optimal | Optimal | Slow (small circuits) |
| Basic | Greedy, suboptimal | Poor | Very fast |

### SABRE Algorithm

1. Compute front layer (gates ready to execute)
2. Score each candidate SWAP by how much it reduces future gate distances
3. Apply best SWAP, update front layer
4. Repeat until all gates are routed

**Layout strategies:**
- **Trivial layout:** Map qubit i → physical qubit i (rarely optimal)
- **Dense layout:** Place qubits near graph center
- **SABRE layout:** Use routing heuristic to find good initial layout
- **VF2 layout:** Graph isomorphism to find subgraph match

```python
from qiskit import transpile
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

backend = FakeNairobiV2()

# Full transpile with SABRE routing
qc_t = transpile(
    qc,
    backend=backend,
    routing_method='sabre',
    layout_method='sabre',
    optimization_level=3
)

# Inspect final layout
print(qc_t.layout)
print(qc_t.count_ops())
```

**Exercises:**
- Draw the coupling map for FakeNairobiV2 and manually route a 3-qubit circuit
- Compare SWAP overhead for trivial vs SABRE layout on a 5-qubit GHZ circuit
- Implement a greedy routing algorithm from scratch

---

## Module 4 — Circuit Optimization Passes

**Objective:** Apply algebraic and peephole optimizations to reduce gate count and depth.

### Categories of Optimization

**1. Cancellation and Merging**
- `X · X = I` → remove both
- `CX · CX = I` → remove both
- Consecutive Rz gates → merge: `Rz(a) · Rz(b) = Rz(a+b)`

**2. Commutation Rules**
- `Rz(θ) · CX(ctrl, tgt)` = `CX(ctrl, tgt) · Rz(θ)` if Rz on control
- Use commutation to reorder gates for cancellation opportunities

**3. Template Matching**
- Search for subsequences that match known equivalent but cheaper templates
- E.g., replace 3-CNOT SWAP with iSWAP where available

**4. Clifford Optimization**
- Clifford circuits have O(n²/log n) optimal size; tableau simulation
- Peephole optimization on Clifford subcircuits

**5. KAK Decomposition (two-qubit)**
- Any 2-qubit unitary = (local A) · exp(iΣ cᵢ σᵢ⊗σᵢ) · (local B)
- Exactly 3 CX gates suffice for generic 2-qubit gate; sometimes 2 or 1
- Implemented in Qiskit as `UnitarySynthesis`

```python
from qiskit.transpiler.passes import (
    Optimize1qGates,
    CXCancellation,
    CommutativeCancellation,
    ConsolidateBlocks,
    UnitarySynthesis,
)
```

**Exercises:**
- Apply `CXCancellation` manually to a circuit with redundant CNOTs
- Verify that KAK decomposition of a SWAP uses exactly 3 CX gates
- Build a circuit, run through optimization level 3, and count the gate reduction

---

## Module 5 — The Qiskit Transpiler Pass Manager

**Objective:** Understand and customize the Qiskit pass manager to build tailored compilation pipelines.

### Pass Types

| Pass Type | Description |
|---|---|
| `TransformationPass` | Modifies the circuit (routing, optimization) |
| `AnalysisPass` | Computes properties, stores in `property_set` |
| `ConditionalController` | Run passes conditionally |
| `DoWhileController` | Repeat passes until convergence |

### Built-in Optimization Levels

| Level | What It Does |
|---|---|
| 0 | Only mapping (routing + translation); no optimization |
| 1 | Light optimization: trivial cancellation |
| 2 | Medium: commutation, Clifford optimization |
| 3 | Heavy: full KAK + template matching + Clifford synthesis |

### Custom Pass Manager

```python
from qiskit.transpiler import PassManager, CouplingMap
from qiskit.transpiler.passes import (
    SetLayout,
    ApplyLayout,
    SabreLayout,
    SabreSwap,
    BasisTranslator,
    Optimize1qGatesDecomposition,
    CXCancellation,
)
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel

coupling_map = CouplingMap.from_line(5)

pm = PassManager([
    # Layout
    SabreLayout(coupling_map, max_iterations=3, seed=42),
    ApplyLayout(),
    # Routing
    SabreSwap(coupling_map, heuristic='decay', seed=42),
    # Translation
    BasisTranslator(sel, ['cx', 'rz', 'sx', 'x']),
    # Optimization
    Optimize1qGatesDecomposition(basis=['rz', 'sx', 'x']),
    CXCancellation(),
])

qc_t = pm.run(qc)
```

### Writing a Custom Pass

```python
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.dagcircuit import DAGCircuit

class RemoveDoubleX(TransformationPass):
    """Cancel consecutive X gates."""
    
    def run(self, dag: DAGCircuit) -> DAGCircuit:
        for node in dag.topological_op_nodes():
            if node.op.name == 'x':
                successors = [s for s in dag.successors(node)
                              if s.type == 'op' and s.op.name == 'x'
                              and s.qargs == node.qargs]
                for succ in successors:
                    dag.remove_op_node(node)
                    dag.remove_op_node(succ)
        return dag
```

**Exercises:**
- Build a pass manager that only performs routing and translation, no optimization
- Write a custom pass that counts the number of T gates and stores in `property_set`
- Chain `DoWhileController` with `CXCancellation` until no further cancellation is possible

---

## Module 6 — Hardware-Aware Optimization

**Objective:** Use knowledge of hardware properties to make better transpilation decisions.

### Key Hardware Properties

| Property | Impact on Transpilation |
|---|---|
| Coupling map | Which qubit pairs can have 2Q gates |
| Gate error rates | Prefer high-fidelity qubit pairs |
| Gate durations | Minimize circuit duration for decoherence |
| T1, T2 times | Set maximum useful circuit depth |
| Readout error | Affects measurement fidelity |

### Backend Properties API

```python
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

backend = FakeNairobiV2()
props = backend.properties()

# Gate error for a specific gate
cx_error = props.gate_error('cx', [0, 1])

# Best qubit pair for CX
from qiskit.transpiler import CouplingMap
cm = CouplingMap(backend.coupling_map)

# Error-aware routing (Qiskit v1)
from qiskit.transpiler.passes import SabreSwap
# Pass error map into routing heuristic
```

### Noise-Aware Layout

```python
from qiskit.transpiler.passes import VF2PostLayout, SabreLayout

# VF2PostLayout: after initial layout, try to improve using error rates
pm_noise_aware = PassManager([
    SabreLayout(coupling_map, max_iterations=5),
    ApplyLayout(),
    VF2PostLayout(
        target=backend.target,
        max_trials=50,
        seed=42,
    ),
    SabreSwap(coupling_map, heuristic='decay'),
    BasisTranslator(sel, target_basis),
    Optimize1qGatesDecomposition(basis=target_basis),
])
```

### Dynamic Circuits (Feed-Forward)

QASM 3 + new IBM systems support mid-circuit measurement and real-time classical feed-forward:

```python
from qiskit.circuit import QuantumCircuit, IfElseOp

qc = QuantumCircuit(2, 1)
qc.h(0)
qc.measure(0, 0)
with qc.if_test((0, 1)):
    qc.x(1)  # Conditioned on measurement result
```

**Exercises:**
- Use `backend.target` to find the two-qubit pair with lowest CX error
- Re-transpile a circuit using noise-aware layout and measure fidelity improvement
- Implement a dynamic circuit for quantum teleportation with mid-circuit measurement

---

## Module 7 — Metrics and Benchmarking

**Objective:** Measure and compare transpilation quality objectively.

| Metric | Description |
|---|---|
| Gate count | Total number of gates |
| CX count | Two-qubit gate count (dominant cost) |
| Circuit depth | Longest path (critical path) |
| CX depth | Critical path counting only CX gates |
| T count | Relevant for fault-tolerant T-gate cost |
| SWAP overhead | Extra SWAPs inserted by router |
| Expected fidelity | `∏ (1 − ε_i)` over all gates — rough estimate |

```python
from qiskit.converters import circuit_to_dag

def circuit_metrics(qc):
    ops = qc.count_ops()
    return {
        'cx_count': ops.get('cx', 0),
        'depth': qc.depth(),
        'cx_depth': qc.depth(filter_function=lambda x: x.operation.name == 'cx'),
        'total_gates': sum(ops.values()),
    }
```

**Exercises:**
- Compare metrics for optimization levels 0, 1, 2, 3 on a 10-qubit random circuit
- Plot CX count vs optimization time for increasing circuit sizes
- Implement expected fidelity estimation using backend error rates

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| Qiskit transpiler docs (docs.quantum.ibm.com/transpile) | Official docs | Primary reference |
| Amy et al. "Verified Compilation of Space-Efficient Reversible Circuits" | Paper | Gate synthesis theory |
| Cowtan et al. "On the Qubit Routing Problem" | Paper | Routing algorithm survey |
| Li et al. "Tackling the Qubit Mapping Problem for NISQ-Era Quantum Devices" | Paper | SABRE algorithm |
| Qiskit source — `qiskit/transpiler/passes/` | Source | Best way to learn the internals |

---

## Progression Checkpoints

- [ ] Manually decompose any single-qubit gate into {RZ, SX, X}
- [ ] Route a circuit onto a line topology by hand using SWAP insertion
- [ ] Build a custom PassManager with routing + translation + optimization
- [ ] Write a custom TransformationPass that simplifies a specific pattern
- [ ] Use noise-aware layout to improve expected circuit fidelity
- [ ] Measure and compare transpilation quality across optimization levels
- [ ] Implement a dynamic circuit using mid-circuit measurement and feed-forward
