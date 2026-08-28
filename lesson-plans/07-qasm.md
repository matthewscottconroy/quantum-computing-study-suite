# OpenQASM (Quantum Assembly Language)

## Goal
Achieve fluency in OpenQASM 2 and OpenQASM 3 — the portable intermediate representation for quantum circuits — to write, read, and manipulate circuits at the assembly level, essential for transpiler work and hardware-level optimization.

---

## Module 1 — OpenQASM 2 Fundamentals

**Objective:** Read and write the format used by virtually every quantum SDK for circuit interchange.

### File Structure

```qasm
// OpenQASM 2 program
OPENQASM 2.0;
include "qelib1.inc";   // Standard gate library

// Register declarations
qreg q[2];              // 2-qubit quantum register
creg c[2];              // 2-bit classical register

// Gates
h q[0];
cx q[0], q[1];

// Measurement
measure q[0] -> c[0];
measure q[1] -> c[1];
```

### Syntax Elements

| Element | Syntax | Example |
|---|---|---|
| Qubit register | `qreg name[n];` | `qreg q[3];` |
| Classical register | `creg name[n];` | `creg c[3];` |
| Gate application | `gate q[i];` | `h q[0];` |
| Two-qubit gate | `gate ctrl, tgt;` | `cx q[0], q[1];` |
| Measurement | `measure q -> c;` | `measure q[0] -> c[0];` |
| Reset | `reset q[i];` | `reset q[0];` |
| Barrier | `barrier q;` | `barrier q[0], q[1];` |
| Comment | `// text` | |

### Standard Gates in qelib1.inc

| Gate | QASM Name | Parameters |
|---|---|---|
| Hadamard | `h` | — |
| Pauli X | `x` | — |
| Pauli Y | `y` | — |
| Pauli Z | `z` | — |
| S gate | `s` | — |
| T gate | `t` | — |
| S† | `sdg` | — |
| T† | `tdg` | — |
| CNOT | `cx` | — |
| Toffoli | `ccx` | — |
| SWAP | `swap` | — |
| Rz | `rz(λ)` | angle λ |
| Ry | `ry(θ)` | angle θ |
| Rx | `rx(θ)` | angle θ |
| U3 (universal) | `u3(θ,φ,λ)` | 3 angles |
| U1 (phase) | `u1(λ)` | 1 angle |

**Exercises:**
- Write QASM for all four Bell state preparation circuits
- Write QASM for the 3-qubit QFT
- Parse a QASM file manually and trace the circuit state

---

## Module 2 — Custom Gate Definitions in QASM 2

**Objective:** Define and reuse custom gates — essential for structured circuit design.

```qasm
OPENQASM 2.0;
include "qelib1.inc";

// Define a custom gate
gate bell a, b {
    h a;
    cx a, b;
}

// Define a parameterized gate
gate rzz(theta) a, b {
    cx a, b;
    rz(theta) b;
    cx a, b;
}

// Use custom gates
qreg q[4];
creg c[4];

bell q[0], q[1];
rzz(pi/4) q[2], q[3];
```

**Exercises:**
- Define a custom `cphase(θ)` gate using U1 and CNOT
- Define the Fredkin gate using CNOT and Toffoli
- Write a QASM subroutine for a QFT of arbitrary depth

---

## Module 3 — OpenQASM 3 — The New Standard

**Objective:** Master the dramatically expanded OpenQASM 3 specification, which adds classical control flow, typed variables, and pulse-level access.

### Key Additions over QASM 2

| Feature | QASM 2 | QASM 3 |
|---|---|---|
| Classical types | `creg` only | `bit`, `int`, `float`, `angle`, `bool`, arrays |
| Control flow | None | `if`, `for`, `while`, `switch` |
| Classical computation | None | Full classical expressions and arithmetic |
| Timing | No | `delay`, `duration`, `stretch` |
| Pulse-level | No | `cal`, `defcal`, OpenPulse integration |
| Scoping | Flat | Block scoping |
| Subroutines | Gate definitions only | `def` subroutines with return values |
| Extern calls | None | Link to classical functions |

### QASM 3 Example

```qasm
OPENQASM 3.0;

// Typed declarations
qubit[2] q;
bit[2] c;
float[64] theta = π / 4;
int[32] shots = 1000;

// Custom gate — gate parameters are untyped (implicitly angles);
// typed parameters like angle[32] are only allowed on `def` subroutines
gate rz_custom(λ) q {
    U(0, 0, λ) q;
}

// Classical control flow
for int i in [0:3] {
    h q[0];
    cx q[0], q[1];
    c = measure q;
    if (c[0] == 1) {
        x q[1];
    }
    reset q;
}
```

### Mid-Circuit Measurement and Feed-Forward

```qasm
OPENQASM 3.0;
qubit[2] q;
bit[1] m;

h q[0];
cx q[0], q[1];
m[0] = measure q[0];

// Classically conditioned gate
if (m[0]) {
    x q[1];
}
```

**Exercises:**
- Rewrite a QASM 2 circuit in QASM 3 with proper typed declarations
- Write a QASM 3 program for quantum teleportation using mid-circuit measurement
- Implement a quantum error correction syndrome measurement loop in QASM 3

---

## Module 4 — QASM in the Qiskit Ecosystem

**Objective:** Load, export, and manipulate QASM in Qiskit workflows.

```python
from qiskit import QuantumCircuit
from qiskit.qasm2 import dumps, loads
from qiskit.qasm3 import dumps as dumps3, loads as loads3

# Build circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Export to QASM 2
qasm2_str = dumps(qc)
print(qasm2_str)

# Import from QASM 2 string
qc2 = loads(qasm2_str)

# Export to QASM 3
qasm3_str = dumps3(qc)
print(qasm3_str)

# Round-trip through a file
with open('circuit.qasm', 'w') as f:
    f.write(qasm2_str)
with open('circuit.qasm') as f:
    qc_from_file = loads(f.read())
```

Note: importing OpenQASM 3 (`qiskit.qasm3.loads`) requires the optional `qiskit_qasm3_import` package (`pip install qiskit_qasm3_import`); exporting does not.

**QASM and transpilation:**
```python
from qiskit import transpile
from qiskit_ibm_runtime.fake_provider import FakeManilaV2

# FakeManilaV2 models the retired 5-qubit Manila device — fine for
# offline study, but not representative of current IBM hardware.
backend = FakeManilaV2()
qc_t = transpile(qc, backend, optimization_level=3)

# Inspect native QASM output
print(dumps(qc_t))
```

**Exercises:**
- Export a QFT circuit to QASM 2 and examine the gate decompositions
- Round-trip a circuit through QASM 2 and verify fidelity
- Use QASM 3 `loads` to import a custom circuit with classical control

---

## Module 5 — QASM in Other Ecosystems

**Objective:** Understand QASM's role as an interchange format across the quantum software stack.

| SDK | QASM Support |
|---|---|
| Qiskit | QASM 2 + QASM 3 (full) |
| Cirq | QASM 2 import/export |
| PennyLane | QASM 2 via qiskit plugin |
| tket (Pytket) | QASM 2 import/export |
| Braket | QASM 2 import |
| Quil | Separate format (Rigetti), similar concepts |

**Cross-platform workflow:**
```python
# Export from Qiskit
qasm_str = dumps(qc)

# Import in pytket
from pytket.qasm import circuit_from_qasm_str
tk_circuit = circuit_from_qasm_str(qasm_str)

# Compile with pytket and re-export
from pytket.qasm import circuit_to_qasm_str
compiled = circuit_to_qasm_str(tk_circuit)
```

**Exercises:**
- Export a circuit from Qiskit and import it in Cirq
- Identify what gates require custom definitions when exporting to QASM 2
- Compare QASM 2 and Quil for the same circuit

---

## Module 6 — Pulse-Level Control with QASM 3 `defcal`

**Objective:** Understand QASM 3's pulse-level extensions for defining custom gate calibrations.

> **Currency note (important):** Pulse-level control was **removed from Qiskit** — `qiskit.pulse` was deprecated in 1.x and deleted in Qiskit 2.0 — and **IBM retired pulse-level access on its hardware at the end of 2024**. `defcal`/OpenPulse remains part of the portable OpenQASM 3 specification and is still used by some other vendors and research stacks, so treat this module as background/spec knowledge, not something you can execute on IBM systems today.

```qasm
OPENQASM 3.0;

// Select the calibration grammar before any cal/defcal block
defcalgrammar "openpulse";

// Shared calibration definitions live in a cal block
cal {
    // Declare a port and frame
    extern port p0;
    frame fq0 = newframe(p0, 5e9, 0.0);  // 5 GHz qubit frame
}

// Define a custom gate calibration (body uses OpenPulse grammar)
defcal x $0 {
    play(fq0, gaussian(0.2, 100ns, 40ns));
}

// Use the calibrated gate on physical qubit $0
x $0;
```

**Key concepts:**
- `defcal` overrides the default compiler lowering for a gate
- Waveforms: `gaussian`, `drag`, `constant`, `arb_waveform`
- Frames and ports connect to hardware channels
- Enables fine-grained control for noise experiments and new gate designs

**Exercises:**
- Write a `defcal` for a DRAG pulse on a single qubit
- Define a two-qubit `defcal` for a cross-resonance gate
- Explain how `defcal` interacts with transpilation

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| OpenQASM 2 paper — Cross et al. (2017) | Paper | Original specification |
| OpenQASM 3 paper — Cross et al. (2022) | Paper | Full language spec |
| openqasm.com | Spec site | Grammar, examples |
| Qiskit QASM 2 docs | Official docs | `qiskit.qasm2` module |
| Qiskit QASM 3 docs | Official docs | `qiskit.qasm3` module |

---

## Progression Checkpoints

- [ ] Write any standard circuit from scratch in QASM 2
- [ ] Define custom parameterized gates in QASM 2
- [ ] Use QASM 3 control flow (if/for/while) and classical types
- [ ] Round-trip a circuit through QASM in Qiskit without loss
- [ ] Use QASM as an interchange format between Qiskit and another SDK
- [ ] Write a basic `defcal` for a custom pulse-level gate definition
