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

<details><summary>Solution</summary>

All four share one body — `h q[0]; cx q[0],q[1];` — preceded by Pauli `X` gates that
select which Bell state comes out. Full program for `|Φ⁺⟩`:

```qasm
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];

h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
```

The four preparations, as the lines that replace the body:

```qasm
// |Phi+> = (|00> + |11>)/sqrt(2)
h q[0];
cx q[0], q[1];

// |Psi+> = (|01> + |10>)/sqrt(2)
x q[1];
h q[0];
cx q[0], q[1];

// |Phi-> = (|00> - |11>)/sqrt(2)
x q[0];
h q[0];
cx q[0], q[1];

// |Psi-> = (|01> - |10>)/sqrt(2)
x q[0];
x q[1];
h q[0];
cx q[0], q[1];
```

Verified by importing each one and reading the statevector:

```python
from qiskit import qasm2
from qiskit.quantum_info import Statevector

BELL_QASM = {
    "phi_plus":  "h q[0];\ncx q[0],q[1];",
    "psi_plus":  "x q[1];\nh q[0];\ncx q[0],q[1];",
    "phi_minus": "x q[0];\nh q[0];\ncx q[0],q[1];",
    "psi_minus": "x q[0];\nx q[1];\nh q[0];\ncx q[0],q[1];",
}
HEADER = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\n'

for name, body in BELL_QASM.items():
    circ = qasm2.loads(HEADER + body + "\n")
    amps = Statevector(circ).to_dict()
    print(f"{name:10s}", {k: round(complex(v).real, 4) for k, v in amps.items()})
```

Real output (Qiskit 2.5.2):

```
phi_plus   {'00': 0.7071, '11': 0.7071}
psi_plus   {'01': 0.7071, '10': 0.7071}
phi_minus  {'00': 0.7071, '11': -0.7071}
psi_minus  {'01': -0.7071, '10': 0.7071}
```

**QASM details worth noting.**

- `measure q -> c;` (whole register at once) is legal QASM 2 shorthand for the two
  element-wise measurements.
- Keys are printed little-endian (`|q₁q₀⟩`), so `psi_minus` showing
  `{'01': −0.7071, '10': +0.7071}` is `(|q₀=0,q₁=1⟩ − |q₀=1,q₁=0⟩)/√2` — the
  standard `|Ψ⁻⟩`, not a sign error.
- QASM 2 has no `if` other than `if (c == k)` on a whole classical register, and no
  arithmetic: everything above is straight-line code, which is exactly the point of
  the format.

</details>

- Write QASM for the 3-qubit QFT

<details><summary>Solution</summary>

The QFT is Hadamards interleaved with controlled phase rotations, then a bit
reversal. In QASM 2 the controlled phase is `cu1(λ)`.

```python
from qiskit import QuantumCircuit, qasm2
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator

QFT3_QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];

// rotation stage: q[0] is the least significant bit
h q[2];
cu1(pi/2) q[1], q[2];
cu1(pi/4) q[0], q[2];
h q[1];
cu1(pi/2) q[0], q[1];
h q[0];

// bit reversal; 'swap' is not in the arXiv qelib1.inc, so spell it out
cx q[0], q[2];
cx q[2], q[0];
cx q[0], q[2];
"""

qft3_from_qasm = qasm2.loads(QFT3_QASM)
print(qft3_from_qasm.draw(output="text", fold=90))

ref_qft3 = QuantumCircuit(3)
ref_qft3.append(QFTGate(3), [0, 1, 2])
print("equals QFTGate(3):", Operator(qft3_from_qasm).equiv(Operator(ref_qft3)))

# the same file with Qiskit's extended gate set available
with_swap = qasm2.loads(
    'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\nswap q[0],q[1];',
    custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
print("swap accepted with LEGACY_CUSTOM_INSTRUCTIONS:", dict(with_swap.count_ops()))
```

Real output:

```
                                             ┌───┐     ┌───┐     
q_0: ────────────────■──────────────■────────┤ H ├──■──┤ X ├──■──
                     │        ┌───┐ │U1(π/2) └───┘  │  └─┬─┘  │  
q_1: ──────■─────────┼────────┤ H ├─■───────────────┼────┼────┼──
     ┌───┐ │U1(π/2)  │U1(π/4) └───┘               ┌─┴─┐  │  ┌─┴─┐
q_2: ┤ H ├─■─────────■────────────────────────────┤ X ├──■──┤ X ├
     └───┘                                        └───┘     └───┘
equals QFTGate(3): True
swap accepted with LEGACY_CUSTOM_INSTRUCTIONS: {'swap': 1}
```

**The gotcha this exercise exposes.** `swap` is **not** in the `qelib1.inc` as
published in the OpenQASM 2 paper, and Qiskit's importer implements exactly that
list (`u3, u2, u1, cx, id, x, y, z, h, s, sdg, t, tdg, rx, ry, rz, cz, cy, ch, ccx,
crz, cu1, cu3`). So `swap q[0],q[2];` raises

```
QASM2ParseError: "<input>:10,0: 'swap' is not defined in this scope"
```

Three ways out: write the three CNOTs by hand (done above), add
`gate swap a,b { cx a,b; cx b,a; cx a,b; }` to the file, or import with
`custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS`, which restores Qiskit's
historically extended qelib1 (`swap`, `sx`, `cp`, `rzz`, `cswap`, `rxx`, `c3x`, …).

**Correctness.** `Operator(...).equiv(Operator(QFTGate(3)))` returns `True`, which
checks the full `8×8` unitary up to global phase — a far stronger test than
eyeballing the diagram. The rotation angles halve down the chain (`π/2`, `π/4`) and
the final three CNOTs implement the `q[0] ↔ q[2]` swap of the bit-reversal stage.

</details>

- Parse a QASM file manually and trace the circuit state

<details><summary>Solution</summary>

Take this program (Deutsch's algorithm with the oracle `f(x) = x`):

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[1];
x q[1];
h q[0];
h q[1];
cx q[0], q[1];
h q[0];
measure q[0] -> c[0];
```

**Hand trace** (writing states as `|q₁q₀⟩`):

1. `x q[1]` — `|00⟩ → |10⟩`, i.e. the ancilla `q₁` is now `|1⟩`.
2. `h q[0]` — `q₀ → |+⟩`: `(|10⟩ + |11⟩)/√2`.
3. `h q[1]` — `q₁ → |−⟩`: `|−⟩|+⟩ = ½(|00⟩ + |01⟩ − |10⟩ − |11⟩)`.
4. `cx q[0], q[1]` — control `q₀`, target `q₁`. Since the target is in `|−⟩`, an
   `X` on it returns `−|−⟩`: the gate writes a **phase** `(−1)^{q₀}` onto the control
   instead of flipping anything. The state becomes
   `½(|00⟩ − |01⟩ − |10⟩ + |11⟩) = |−⟩|−⟩`. This is phase kickback.
5. `h q[0]` — `|−⟩ → |1⟩` on `q₀`: `(|01⟩ − |11⟩)/√2 = |−⟩_{q₁}|1⟩_{q₀}`.
6. `measure q[0] -> c[0]` — `c[0] = 1` with probability 1: the oracle is balanced.

Machine check of every line:

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

TRACE_QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[1];
x q[1];
h q[0];
h q[1];
cx q[0], q[1];
h q[0];
measure q[0] -> c[0];
"""

steps = [("x q[1]",       lambda c: c.x(1)),
         ("h q[0]",       lambda c: c.h(0)),
         ("h q[1]",       lambda c: c.h(1)),
         ("cx q[0],q[1]", lambda c: c.cx(0, 1)),
         ("h q[0]",       lambda c: c.h(0))]

state = Statevector.from_label("00")
print(f"{'after':14s} amplitudes, keys are |q1 q0>")
print(f"{'start':14s}", {k: round(complex(v).real, 4) for k, v in state.to_dict().items()})
for label, apply in steps:
    step = QuantumCircuit(2)
    apply(step)
    state = state.evolve(step)
    print(f"{label:14s}", {k: round(complex(v).real, 4) for k, v in state.to_dict().items()})
print("P(c[0] = 1) =", round(float(state.probabilities([0])[1]), 6))
```

Real output:

```
after          amplitudes, keys are |q1 q0>
start          {'00': 1.0}
x q[1]         {'10': 1.0}
h q[0]         {'10': 0.7071, '11': 0.7071}
h q[1]         {'00': 0.5, '01': 0.5, '10': -0.5, '11': -0.5}
cx q[0],q[1]   {'00': 0.5, '01': -0.5, '10': -0.5, '11': 0.5}
h q[0]         {'00': 0.0, '01': 0.7071, '10': -0.0, '11': -0.7071}
P(c[0] = 1) = 1.0
```

Every line of the hand trace matches. **Method to reuse when reading any QASM
file**: (1) note the register sizes and the qubit-ordering convention, (2) write the
initial product state, (3) apply gates one line at a time, keeping the state
factored as long as you can — a state stops factoring exactly when a two-qubit gate
entangles it — and (4) look for `|±⟩` targets, where controlled gates turn into
phases rather than flips.

</details>


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

<details><summary>Solution</summary>

The identity to implement is `CP(θ) = diag(1, 1, 1, e^{iθ})`. Split the phase in
half and use a CNOT pair to make it conditional:

```
CP(θ) = U1(θ/2)_a · CX(a,b) · U1(−θ/2)_b · CX(a,b) · U1(θ/2)_b
```

**Why it works.** Track the phase on each basis state `|ab⟩`:

- `|00⟩`: `U1` acts as `1` on `|0⟩` everywhere → phase `1`.
- `|10⟩`: `U1(θ/2)_a` gives `e^{iθ/2}`; the CNOTs flip `b` to 1 and back, so
  `U1(−θ/2)_b` contributes `e^{−iθ/2}` and the final `U1(θ/2)_b` sees `b = 0` and
  contributes nothing → net phase `1`.
- `|01⟩`: only the final `U1(θ/2)_b` applies... and the middle `U1(−θ/2)_b` sees the
  CNOT-flipped value `b = 1`, contributing `e^{−iθ/2}` → net `e^{iθ/2}e^{−iθ/2} = 1`.
- `|11⟩`: `U1(θ/2)_a` gives `e^{iθ/2}`, the middle `U1(−θ/2)_b` acts on the flipped
  `b = 0` (nothing), and the final `U1(θ/2)_b` gives another `e^{iθ/2}` → net
  `e^{iθ}` ✓.

```python
import numpy as np
from qiskit import QuantumCircuit, qasm2
from qiskit.quantum_info import Operator

CPHASE_QASM = """OPENQASM 2.0;
include "qelib1.inc";

// controlled phase from u1 + cx:  diag(1, 1, 1, e^{i theta})
gate cphase(theta) a, b {
  u1(theta/2) a;
  cx a, b;
  u1(-theta/2) b;
  cx a, b;
  u1(theta/2) b;
}

qreg q[2];
cphase(pi/3) q[0], q[1];
"""

cphase_circ = qasm2.loads(CPHASE_QASM)
print("diagonal:", np.round(np.diag(Operator(cphase_circ).data), 6))

ref_cp = QuantumCircuit(2)
ref_cp.cp(np.pi / 3, 0, 1)
print("equals cp(pi/3):", Operator(cphase_circ).equiv(Operator(ref_cp)))
```

Real output (`θ = π/3`, so the last entry should be `e^{iπ/3} = 0.5 + 0.866i`):

```
diagonal: [1. +0.j       1. +0.j       1. +0.j       0.5+0.866025j]
equals cp(pi/3): True
```

**Notes.** `cu1` in `qelib1.inc` is defined by exactly this decomposition, so the
exercise is really "re-derive the library gate". `CP` is symmetric in its two
qubits (the matrix is diagonal), which is why no direction is specified. Parameter
expressions like `theta/2` and `-theta/2` inside a `gate` body are legal QASM 2:
the parameter arithmetic is evaluated at expansion time.

</details>

- Define the Fredkin gate using CNOT and Toffoli

<details><summary>Solution</summary>

The Fredkin (controlled-SWAP) gate swaps `b` and `c` when `a = 1`. Since
`SWAP(b,c) = CX(b,c)·CX(c,b)·CX(b,c)`, controlling the middle CNOT is enough:

```
CSWAP(a,b,c) = CX(c,b) · CCX(a,b,c) · CX(c,b)
```

**Why only the middle one needs controlling.** Conjugating by `CX(c,b)` maps the
controlled-`X` on `c` into a controlled-swap: in the `a = 0` subspace the two outer
CNOTs cancel (`CX·CX = I`), and in the `a = 1` subspace the sequence is exactly the
three-CNOT SWAP.

```python
import numpy as np
from qiskit import QuantumCircuit, qasm2
from qiskit.quantum_info import Operator

FREDKIN_QASM = """OPENQASM 2.0;
include "qelib1.inc";

// Fredkin (controlled-SWAP) from one Toffoli and two CNOTs
gate fredkin a, b, c {
  cx c, b;
  ccx a, b, c;
  cx c, b;
}

qreg q[3];
fredkin q[0], q[1], q[2];
"""

fredkin_circ = qasm2.loads(FREDKIN_QASM)
ref_cswap = QuantumCircuit(3)
ref_cswap.cswap(0, 1, 2)
print("equals cswap:", Operator(fredkin_circ).equiv(Operator(ref_cswap)))
print(np.real(Operator(fredkin_circ).data).astype(int))
```

Real output:

```
equals cswap: True
[[1 0 0 0 0 0 0 0]
 [0 1 0 0 0 0 0 0]
 [0 0 1 0 0 0 0 0]
 [0 0 0 0 0 1 0 0]
 [0 0 0 0 1 0 0 0]
 [0 0 0 1 0 0 0 0]
 [0 0 0 0 0 0 1 0]
 [0 0 0 0 0 0 0 1]]
```

**Reading the matrix.** It is a permutation matrix that exchanges basis states 3
and 5 — in Qiskit's little-endian order `|q₂q₁q₀⟩`, those are `|011⟩` and `|101⟩`,
i.e. the states where the control `q₀ = 1` and the two swapped qubits differ.
Everything else is fixed. That is precisely controlled-SWAP.

**Cost.** One Toffoli plus two CNOTs, so in Clifford+T the Fredkin costs the same
7 `T` gates as a Toffoli. Fredkin is universal for *reversible* computation on its
own (it is conservative — it preserves the number of 1s — which is why it appears
in billiard-ball and thermodynamic models of computation), and it is the natural
primitive for the SWAP test.

</details>

- Write a QASM subroutine for a QFT of arbitrary depth

<details><summary>Solution</summary>

**The honest answer first: OpenQASM 2 cannot do it.** `gate` bodies take a fixed
number of qubit arguments, there are no loops, no recursion, and no variadic
parameters. "Arbitrary depth" in QASM 2 means one of:

1. **Nested definitions, one per size** — legal, readable, and the closest thing to
   a subroutine:

```python
from qiskit import QuantumCircuit, qasm2
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator

QFT_RECURSIVE = """OPENQASM 2.0;
include "qelib1.inc";

// QFT_k on k qubits, a0 = least significant. Each level reuses the level below.
gate qft1 a0 { h a0; }
gate qft2 a0, a1 { h a1; cu1(pi/2) a0, a1; qft1 a0; }
gate qft3 a0, a1, a2 { h a2; cu1(pi/2) a1, a2; cu1(pi/4) a0, a2; qft2 a0, a1; }
gate qft4 a0, a1, a2, a3 {
  h a3;
  cu1(pi/2) a2, a3;
  cu1(pi/4) a1, a3;
  cu1(pi/8) a0, a3;
  qft3 a0, a1, a2;
}

qreg q[4];
qft4 q[0], q[1], q[2], q[3];

// bit reversal
cx q[0], q[3]; cx q[3], q[0]; cx q[0], q[3];
cx q[1], q[2]; cx q[2], q[1]; cx q[1], q[2];
"""

qft4_circ = qasm2.loads(QFT_RECURSIVE)
ref_qft4 = QuantumCircuit(4)
ref_qft4.append(QFTGate(4), [0, 1, 2, 3])
print("equals QFTGate(4):", Operator(qft4_circ).equiv(Operator(ref_qft4)))
print("top-level ops:", dict(qft4_circ.count_ops()))
```

Real output:

```
equals QFTGate(4): True
top-level ops: {'cx': 6, 'qft4': 1}
```

Each level is defined in terms of the one below, so adding `qft5` is four new lines.
The importer keeps `qft4` as a single opaque instruction until it is decomposed,
which is why `count_ops()` shows one `qft4` plus the six bit-reversal CNOTs.

2. **Generate the text from a host language** — what every real toolchain does:

```python
def qft_qasm(n):
    lines = ['OPENQASM 2.0;', 'include "qelib1.inc";', f"qreg q[{n}];"]
    for j in range(n - 1, -1, -1):
        lines.append(f"h q[{j}];")
        for k in range(j - 1, -1, -1):
            lines.append(f"cu1(pi/{2 ** (j - k)}) q[{k}], q[{j}];")
    for i in range(n // 2):
        a, b = i, n - 1 - i
        lines += [f"cx q[{a}], q[{b}];", f"cx q[{b}], q[{a}];", f"cx q[{a}], q[{b}];"]
    return "\n".join(lines) + "\n"
```

**OpenQASM 3 does have real subroutines** — `def`, `for`, sized types — so the
arbitrary-depth version can be written once:

```qasm
OPENQASM 3.0;
include "stdgates.inc";

def qft(qubit[4] reg) {
  for int j in [3:-1:0] {
    h reg[j];
    for int k in [j-1:-1:0] {
      ctrl @ p(pi / (2 ** (j - k))) reg[k], reg[j];
    }
  }
}

qubit[4] q;
qft(q);
```

This is spec-valid OpenQASM 3, but **Qiskit's importer does not support it today**:
`qiskit.qasm3.loads` on a program containing `def` raises

```
QASM3ImporterError: 'node of type SubroutineDefinition is not supported'
```

(verified in this venv with `qiskit-qasm3-import` 0.6.0). `for` loops *are*
supported — see the QEC exercise — but subroutines are not yet, so for Qiskit work
today the practical answer remains "generate it from Python".

</details>


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

<details><summary>Solution</summary>

**QASM 2 original and its QASM 3 translation**, line for line:

```qasm
OPENQASM 2.0;              |   OPENQASM 3.0;
include "qelib1.inc";      |   include "stdgates.inc";
qreg q[2];                 |   qubit[2] q;
creg c[2];                 |   bit[2] c;
h q[0];                    |   h q[0];
rz(pi/4) q[0];             |   rz(pi/4) q[0];
cx q[0], q[1];             |   cx q[0], q[1];
measure q[0] -> c[0];      |   c[0] = measure q[0];
measure q[1] -> c[1];      |   c[1] = measure q[1];
```

The four structural changes: `qelib1.inc → stdgates.inc`, `qreg → qubit[n]`,
`creg → bit[n]`, and measurement becomes an **assignment** (`c = measure q;` also
works for whole registers).

```python
from qiskit import qasm2, qasm3
from qiskit.quantum_info import Operator

QASM2_SRC = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
rz(pi/4) q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""

QASM3_SRC = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
rz(pi/4) q[0];
cx q[0], q[1];
c[0] = measure q[0];
c[1] = measure q[1];
"""

c2 = qasm2.loads(QASM2_SRC)
c3 = qasm3.loads(QASM3_SRC)
print("QASM 2 ops:", dict(c2.count_ops()))
print("QASM 3 ops:", dict(c3.count_ops()))
print("same unitary:", Operator(c2.remove_final_measurements(inplace=False))
      .equiv(Operator(c3.remove_final_measurements(inplace=False))))

# typed declarations are legal OpenQASM 3 but the Qiskit importer is a subset
TYPED = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
float[64] theta = pi / 4;
h q[0];
rz(theta) q[0];
cx q[0], q[1];
c = measure q;
"""
try:
    qasm3.loads(TYPED)
except Exception as exc:
    print("typed version ->", type(exc).__name__ + ":", str(exc)[:70])
```

Real output:

```
QASM 2 ops: {'measure': 2, 'h': 1, 'rz': 1, 'cx': 1}
QASM 3 ops: {'measure': 2, 'h': 1, 'rz': 1, 'cx': 1}
same unitary: True
typed version -> QASM3ImporterError: "5,0: declarations of type 'float' are not supported"
```

**The "proper typed declarations" version** — legal OpenQASM 3, and what the exam
and the spec expect you to be able to write:

```qasm
OPENQASM 3.0;
include "stdgates.inc";

const float[64] theta = pi / 4;    // compile-time constant
qubit[2] q;
bit[2] c;
int[32] shots = 1024;              // classical variable
angle[32] phi = theta / 2;         // angle type wraps mod 2pi

h q[0];
rz(theta) q[0];
cx q[0], q[1];
c = measure q;
```

**But note the toolchain reality, demonstrated above**: `qiskit-qasm3-import` 0.6.0
accepts `qubit`/`bit` declarations, inline `pi` expressions, `if`/`else`, `for`,
`while` and `gate` definitions, and rejects `float`, `int`, `angle` and `const`
declarations as well as `def`. So spec-valid QASM 3 with typed classical variables
will not round-trip through Qiskit today. Export (`qiskit.qasm3.dumps`) has no such
limitation, because Qiskit only emits the subset it can build.

**Other QASM 3 features to mention in a full answer**: block scoping (a variable
declared inside `{ }` does not leak), `input`/`output` modifiers for parameterised
programs, gate modifiers (`ctrl @`, `inv @`, `pow(k) @`), timing (`delay[100ns]`,
`duration`, `stretch`), and `$0`-style physical qubit references for already-mapped
circuits.

</details>

- Write a QASM 3 program for quantum teleportation using mid-circuit measurement

<details><summary>Solution</summary>

This is the canonical QASM 3 program — it needs exactly the features QASM 2 lacks:
mid-circuit measurement into typed bits, and gates conditioned on those bits.

```python
from qiskit import qasm3, transpile
from qiskit.circuit import ClassicalRegister
from qiskit_aer import AerSimulator
import numpy as np

TELEPORT_QASM3 = """OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;        // q[0] message, q[1] Alice's half, q[2] Bob's half
bit[2] c;

ry(0.7) q[0];      // prepare the message state

h q[1];            // shared Bell pair
cx q[1], q[2];

cx q[0], q[1];     // Bell measurement on message + Alice's half
h q[0];
c[0] = measure q[0];
c[1] = measure q[1];

if (c[1] == true) { x q[2]; }     // feed-forward corrections
if (c[0] == true) { z q[2]; }
"""

tele = qasm3.loads(TELEPORT_QASM3)
print("ops:", dict(tele.count_ops()))

check = tele.copy()
check.add_register(ClassicalRegister(1, "out"))
check.measure(2, check.clbits[-1])
sim_t = AerSimulator()
counts_t = sim_t.run(transpile(check, sim_t), shots=4000,
                     seed_simulator=5).result().get_counts()
p1 = sum(v for k, v in counts_t.items() if k.split(" ")[0] == "1") / 4000
print("P(Bob measures 1) =", round(p1, 4),
      " expected sin^2(0.7/2) =", round(float(np.sin(0.35) ** 2), 4))
```

Real output:

```
ops: {'h': 2, 'cx': 2, 'measure': 2, 'if_else': 2, 'ry': 1}
P(Bob measures 1) = 0.122  expected sin^2(0.7/2) = 0.1176
```

**Verification logic.** The message is `R_y(0.7)|0⟩`, whose probability of measuring
`1` is `sin²(0.35) = 0.1176`. After teleportation Bob's qubit is measured 4000
times and gives `1` with frequency `0.122` — within one standard error
(`√(0.1176·0.8824/4000) ≈ 0.005`) of the prediction. The protocol works, and the
`if_else` operations show the feed-forward survived the import.

**Points about the QASM 3 specifically.**

- `c[0] = measure q[0];` is the assignment form; the older `measure q[0] -> c[0];`
  is still accepted by the spec for compatibility.
- `if (c[1] == true) { x q[2]; }` — the Qiskit importer wants `bit == const bool`
  (or `bitarray == const int`); `if (c[1] == 1)` is rejected by
  `qiskit-qasm3-import` 0.6.0, and bare `if (c[1])` works.
- The corrections are `X` on `c[1]` (Alice's second measured bit) and `Z` on `c[0]`
  — swap them and the protocol silently fails for half the inputs, which is exactly
  the kind of bug the numeric check above catches.
- Hardware needs *fast* feed-forward: the conditional must be resolved inside the
  qubit's coherence time, which is why dynamic circuits are a hardware feature, not
  just a language feature.

</details>

- Implement a quantum error correction syndrome measurement loop in QASM 3

<details><summary>Solution</summary>

Repeated syndrome extraction for the 3-qubit bit-flip code, using a `for` loop,
ancilla `reset`, mid-circuit measurement and conditional correction — the full
dynamic-circuit vocabulary.

```python
from qiskit import qasm3, transpile
from qiskit_aer import AerSimulator

QEC_QASM3 = """OPENQASM 3.0;
include "stdgates.inc";

qubit[5] q;        // q[0..2] data, q[3..4] syndrome ancillas
bit[2] syn;        // 's' would collide with the S gate from stdgates.inc
bit[3] out;

// encode a logical |+>_L = (|000> + |111>)/sqrt(2)
h q[0];
cx q[0], q[1];
cx q[0], q[2];

x q[1];            // inject a bit-flip error on data qubit 1

for int r in [0:1] {
  reset q[3];
  reset q[4];
  cx q[0], q[3];
  cx q[1], q[3];            // syn[0] = parity of Z0 Z1
  cx q[1], q[4];
  cx q[2], q[4];            // syn[1] = parity of Z1 Z2
  syn[0] = measure q[3];
  syn[1] = measure q[4];
  if (syn == 1) { x q[0]; }   // 01 -> qubit 0 flipped
  if (syn == 3) { x q[1]; }   // 11 -> qubit 1 flipped
  if (syn == 2) { x q[2]; }   // 10 -> qubit 2 flipped
}

out[0] = measure q[0];
out[1] = measure q[1];
out[2] = measure q[2];
"""

qec = qasm3.loads(QEC_QASM3)
print("ops:", dict(qec.count_ops()))
sim_q = AerSimulator()
print("counts (out | syn):",
      sim_q.run(transpile(qec, sim_q), shots=2000, seed_simulator=9).result().get_counts())
```

Real output:

```
ops: {'measure': 3, 'cx': 2, 'h': 1, 'x': 1, 'for_loop': 1}
counts (out | syn): {'000 00': 991, '111 00': 1009}
```

**How to read the result.** The data register comes out `000` or `111` with equal
probability — correct, because the encoded state was the logical `|+⟩_L`
`= (|000⟩ + |111⟩)/√2` and the final measurement is in the `Z` basis. Crucially the
outcomes are **never** mixed (no `010`, `110`, …): the injected `X` error on qubit 1
was detected and corrected in round 0, and the syndrome register reads `00` at the
end of round 1, confirming a clean code state. Had the decoder failed, the
distribution would contain weight-1 or weight-2 strings.

**Structure to reuse.**

1. `reset` the ancillas at the top of every round — syndrome qubits must start in
   `|0⟩` or the parity read is garbage. (Reset is cheaper than allocating fresh
   ancillas each round.)
2. Two CNOTs per stabilizer copy the parity `Z_iZ_j` onto an ancilla.
3. Measure the ancillas into a classical `bit[2]`.
4. Decode: `syn == 1 → X q[0]`, `syn == 3 → X q[1]`, `syn == 2 → X q[2]`. Note the
   syndrome is read as a little-endian integer (`syn[1] syn[0]`), which is why
   `2` (binary `10`) means "only the second stabilizer fired" — qubit 2.
5. Loop.

**Language notes.** `bit[2] s;` collides with the `s` gate from `stdgates.inc` and
raises `Symbol 's' already inserted in symbol table` — hence `syn`. `for int r in
[0:1]` runs the body twice (the range is inclusive at both ends). Real QEC applies
the correction only in software (a Pauli frame) rather than with physical gates;
doing it in-circuit as here is pedagogically clearer but wastes gate time.

</details>


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

<details><summary>Solution</summary>

```python
from qiskit import QuantumCircuit, qasm2
from qiskit.circuit.library import QFTGate

qft_export = QuantumCircuit(3)
qft_export.append(QFTGate(3), [0, 1, 2])
qft_flat = qft_export.decompose(reps=3)
print("decomposed ops:", dict(qft_flat.count_ops()))
print(qasm2.dumps(qft_flat))
```

Real output:

```
decomposed ops: {'u': 12, 'cx': 9}
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
u(pi/2,0,pi) q[2];
u(0,0,pi/4) q[2];
cx q[2],q[1];
u(0,0,-pi/4) q[1];
cx q[2],q[1];
u(0,0,pi/4) q[1];
u(pi/2,0,pi) q[1];
u(0,0,pi/4) q[1];
u(0,0,pi/8) q[2];
cx q[2],q[0];
u(0,0,-pi/8) q[0];
cx q[2],q[0];
u(0,0,pi/8) q[0];
cx q[1],q[0];
u(0,0,-pi/4) q[0];
cx q[1],q[0];
u(0,0,pi/4) q[0];
u(pi/2,0,pi) q[0];
cx q[0],q[2];
cx q[2],q[0];
cx q[0],q[2];
```

**What the decomposition shows.**

- Every `H` became `u(π/2, 0, π)` — the Euler-angle form of the Hadamard.
- Every controlled-phase `CP(λ)` became **two CNOTs and three `u(0,0,±λ/2)`
  rotations**, exactly the `cphase` identity from Module 2. That is the real cost of
  a controlled phase on hardware: 2 CNOTs each.
- The final swap is three CNOTs (the exporter did not emit a `swap` token here
  because the circuit was decomposed first).
- Totals: `12` single-qubit `u` gates and `9` CNOTs for a 3-qubit QFT. In general
  `n(n−1)/2` controlled phases × 2 CNOTs, plus `3⌊n/2⌋` for the reversal.

**The `u` vs `u3` point.** Qiskit's exporter emits `u(θ,φ,λ)` (the OpenQASM 3-style
name, accepted by Qiskit's own importer as a builtin) rather than the paper's
`u3(θ,φ,λ)`. Strict OpenQASM 2 parsers from other vendors may reject `u`; if you
need maximum portability, transpile to `['u3','cx']` before exporting, or
post-process the text.

**Practical reading of the angles.** All the phase rotations are `±π/2^k`. For large
`n` these become exponentially small — below any device's calibration resolution —
which is the concrete reason the *approximate* QFT (dropping rotations with
`k > log₂ n + 2`) loses nothing on real hardware.

</details>

- Round-trip a circuit through QASM 2 and verify fidelity

<details><summary>Solution</summary>

```python
import numpy as np
from qiskit import QuantumCircuit, qasm2
from qiskit.quantum_info import Operator, Statevector, state_fidelity, process_fidelity

rt = QuantumCircuit(3)
rt.h(0); rt.cx(0, 1); rt.rz(0.37, 2); rt.ccx(0, 1, 2); rt.swap(0, 2); rt.t(1)

text = qasm2.dumps(rt)
print(text)

try:
    qasm2.loads(text)                       # default: the arXiv qelib1 only
except Exception as exc:
    print("default loads ->", type(exc).__name__ + ":", str(exc)[:70])

back = qasm2.loads(text, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
print("ops before:", dict(rt.count_ops()), " after:", dict(back.count_ops()))
print("Operator.equiv :", Operator(rt).equiv(Operator(back)))
print("process_fidelity:", round(float(np.real(process_fidelity(Operator(rt), Operator(back)))), 12))
print("state_fidelity  :", round(state_fidelity(Statevector(rt), Statevector(back)), 12))
```

Real output:

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
h q[0];
cx q[0],q[1];
rz(0.37) q[2];
ccx q[0],q[1],q[2];
swap q[0],q[2];
t q[1];
default loads -> QASM2ParseError: "<input>:8,0: 'swap' is not defined in this scope"
ops before: {'h': 1, 'cx': 1, 'rz': 1, 'ccx': 1, 'swap': 1, 't': 1}  after: {'h': 1, 'cx': 1, 'rz': 1, 'ccx': 1, 'swap': 1, 't': 1}
Operator.equiv : True
process_fidelity: 1.0
state_fidelity  : 1.0
```

**The headline finding: Qiskit's exporter and importer disagree by default.**
`qasm2.dumps` happily writes `swap` (and `sx`, `cp`, `rzz`, …) with no `gate`
definition, because Qiskit historically shipped an *extended* `qelib1.inc`. But
`qasm2.loads` implements the `qelib1.inc` of the OpenQASM 2 **paper**, which has no
`swap`. A naive `loads(dumps(qc))` therefore raises. Passing
`custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS` (or adding the missing gate
definitions to the text) restores the round trip.

**With that fixed, the round trip is exact**: identical `count_ops`,
`Operator.equiv → True`, `process_fidelity = 1.0` (the right metric for a unitary —
it compares the whole channel, not one state), and `state_fidelity = 1.0` on the
all-zeros input.

**What does *not* survive a QASM 2 round trip.**

- Unbound `Parameter`s (`QASM2ExportError`), so bind before exporting.
- Conditionals other than whole-register equality (`if (c == 3)`).
- Circuit metadata, registers' Python-side names in some edge cases, and any
  attached calibrations.
- Floating-point angles are written in decimal, so a value like `0.37` is exact here
  but in general expect `~1e-16` differences; use `Operator.equiv`, which has a
  tolerance, rather than `==`.

**Good practice.** Verify with `process_fidelity` (or `Operator.equiv`) rather than
comparing the text of two QASM files — formatting, gate ordering and angle
normalisation all differ harmlessly.

</details>

- Use QASM 3 `loads` to import a custom circuit with classical control

<details><summary>Solution</summary>

`qiskit.qasm3.loads` needs the optional `qiskit-qasm3-import` package
(`pip install qiskit_qasm3_import`); exporting with `qiskit.qasm3.dumps` does not.
The importer supports a *subset* of the spec, and the fastest way to learn the
boundary is to probe it:

```python
from qiskit import qasm3

HDR = 'OPENQASM 3.0;\ninclude "stdgates.inc";\n'
FEATURES = {
    "qubit/bit declarations": HDR + "qubit[2] q;\nbit[2] c;\nh q[0];\ncx q[0], q[1];\nc = measure q;\n",
    "inline pi expression":   HDR + "qubit[1] q;\nrz(pi/4) q[0];\n",
    "if (bit)":               HDR + "qubit[2] q;\nbit[1] m;\nm[0] = measure q[0];\nif (m[0]) { x q[1]; }\n",
    "if (bit == true)":       HDR + "qubit[2] q;\nbit[1] m;\nm[0] = measure q[0];\nif (m[0] == true) { x q[1]; }\n",
    "if (bitarray == int)":   HDR + "qubit[2] q;\nbit[2] c;\nc = measure q;\nif (c == 2) { x q[1]; }\n",
    "if/else":                HDR + "qubit[2] q;\nbit[1] m;\nm[0] = measure q[0];\nif (m[0] == true) { x q[1]; } else { z q[1]; }\n",
    "for loop":               HDR + "qubit[1] q;\nfor int i in [0:3] { h q[0]; }\n",
    "gate definition":        HDR + "qubit[2] q;\ngate bell a, b { h a; cx a, b; }\nbell q[0], q[1];\n",
    "physical qubits ($0)":   'OPENQASM 3.0;\ninclude "stdgates.inc";\nbit[1] c;\nh $0;\nc[0] = measure $0;\n',
    "float declaration":      HDR + "qubit[1] q;\nfloat[64] t = pi/4;\nrz(t) q[0];\n",
    "int declaration":        HDR + "qubit[1] q;\nint[32] n = 3;\nx q[0];\n",
    "const declaration":      HDR + "qubit[1] q;\nconst float[64] t = pi/4;\nrz(t) q[0];\n",
    "def subroutine":         HDR + "qubit[1] q;\ndef flip(qubit a) { x a; }\nflip(q[0]);\n",
    "while loop":             HDR + "qubit[1] q;\nbit[1] c;\nwhile (c[0] == false) { h q[0]; c[0] = measure q[0]; }\n",
}
for name, src in FEATURES.items():
    try:
        circ = qasm3.loads(src)
        print(f"  supported     {name:24s} ops={dict(circ.count_ops())}")
    except Exception as exc:
        print(f"  UNSUPPORTED   {name:24s} {str(exc)[:58]}")
```

Real output (`qiskit-qasm3-import` 0.6.0, Qiskit 2.5.2):

```
  supported     qubit/bit declarations   ops={'measure': 2, 'h': 1, 'cx': 1}
  supported     inline pi expression     ops={'rz': 1}
  supported     if (bit)                 ops={'measure': 1, 'if_else': 1}
  supported     if (bit == true)         ops={'measure': 1, 'if_else': 1}
  supported     if (bitarray == int)     ops={'measure': 2, 'if_else': 1}
  supported     if/else                  ops={'measure': 1, 'if_else': 1}
  supported     for loop                 ops={'for_loop': 1}
  supported     gate definition          ops={'bell': 1}
  supported     physical qubits ($0)     ops={'h': 1, 'measure': 1}
  UNSUPPORTED   float declaration        "4,0: declarations of type 'float' are not supported"
  UNSUPPORTED   int declaration          "4,0: declarations of type 'int' are not supported"
  UNSUPPORTED   const declaration        '4,0: node of type ConstantDeclaration is not supported'
  UNSUPPORTED   def subroutine           '4,0: node of type SubroutineDefinition is not supported'
  supported     while loop               ops={'while_loop': 1}
```

**What lands in the `QuantumCircuit`.** Classical control becomes real Qiskit
control-flow operations, not metadata: `if` → an `IfElseOp` (`'if_else'` in
`count_ops`), `for` → `ForLoopOp`, `while` → `WhileLoopOp`. These are exactly the
objects `QuantumCircuit.if_test`, `.for_loop` and `.while_loop` build, so an
imported dynamic circuit can be transpiled and run on a backend that supports
dynamic circuits (and Aer simulates them directly, as the teleportation and QEC
exercises show).

**Conditions have a required shape.** The importer accepts `bit`, `bit == true/false`
and `bitarray == <int>`; it rejects `bit == 1`. Write `if (c[0] == true)` or
`if (c[0])`, and for multi-bit syndromes `if (c == 3)`.

**Naming collision to watch.** Declaring `bit[2] s;` after `include "stdgates.inc";`
fails with `Symbol 's' already inserted in symbol table` — `s` is the phase gate from
the standard library. Any identifier that shadows a gate name (`s`, `t`, `x`, `h`,
`p`, `u`) will do the same; pick register names like `syn`, `meas` or `creg0`.

**Round-tripping.** `qiskit.qasm3.dumps` emits only what Qiskit can represent, so
`loads(dumps(qc))` is reliable; the gap is in the other direction, importing
hand-written spec-complete QASM 3.

</details>


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

<details><summary>Solution</summary>

**Not executable in this repository** — `cirq` is not installed in this venv (and
the repo's snippet checker skips blocks importing unavailable modules). The code
below is the correct API; install with `pip install cirq` to run it.

```python
from qiskit import QuantumCircuit, qasm2
import cirq
from cirq.contrib.qasm_import import circuit_from_qasm

qk = QuantumCircuit(3)
qk.h(0)
qk.cx(0, 1)
qk.ccx(0, 1, 2)
qk.rz(0.3, 2)
qasm_text = qasm2.dumps(qk)

cq = circuit_from_qasm(qasm_text)        # QASM 2 -> cirq.Circuit
print(cq)

# and back again
print(cirq.qasm(cq))                     # cirq.Circuit -> QASM 2 text

# numerical cross-check of the two SDKs
import numpy as np
from qiskit.quantum_info import Operator
u_qiskit = Operator(qk).data
u_cirq = cq.unitary()
print("unitaries agree up to phase:",
      np.allclose(abs(u_qiskit.conj().T @ u_cirq), np.eye(8) * abs((u_qiskit.conj().T @ u_cirq)[0, 0])))
```

Expected behaviour:

```
q_0: ───H───@───@───────────
            │   │
q_1: ───────X───@───────────
                │
q_2: ───────────X───Rz(...)─
```

**The three things that actually bite in cross-SDK transfer.**

1. **Qubit ordering.** Qiskit is little-endian (`q₀` is the least significant bit of
   a bit string); Cirq orders qubits as given and prints big-endian. The *circuit*
   transfers correctly, but any comparison of state vectors or bit strings needs a
   bit reversal. Compare unitaries after reordering, or compare measurement
   statistics keyed by explicit qubit names.
2. **Gate coverage.** Cirq's QASM importer supports the `qelib1.inc` gate set. Gates
   Qiskit exports as bare names outside the paper's list (`sx`, `cp`, `rzz`, `swap`
   in some versions) or as emitted `gate` definitions (`ecr`, `mcx`) may raise
   `QasmException`. Transpile to a common basis first:
   `transpile(qk, basis_gates=['u3', 'cx'])`.
3. **Global phase** is not represented in QASM 2, so unitaries agree only up to
   phase — compare with `equiv`-style tests, not `==`.

**The general lesson.** QASM 2 is a *lowest-common-denominator* interchange format:
straight-line circuits over a small gate set. Anything richer — parameters, control
flow, pulse calibrations, noise models — does not cross the boundary, which is
precisely the motivation for OpenQASM 3.

</details>

- Identify what gates require custom definitions when exporting to QASM 2

<details><summary>Solution</summary>

The rule: gates in the `qelib1.inc` of the OpenQASM 2 paper are emitted as bare
names; everything else Qiskit can decompose gets an explicit `gate ... { ... }`
definition in the file header; and a few things cannot be exported at all.
Measured rather than guessed:

```python
import numpy as np
from qiskit import QuantumCircuit, qasm2
from qiskit.circuit import Parameter
from qiskit.circuit.library import UnitaryGate

for name, build in [("swap", lambda c: c.swap(0, 1)),
                    ("sx",   lambda c: c.sx(0)),
                    ("cp",   lambda c: c.cp(0.3, 0, 1)),
                    ("rzz",  lambda c: c.rzz(0.3, 0, 1)),
                    ("ecr",  lambda c: c.ecr(0, 1)),
                    ("mcx",  lambda c: c.mcx([0, 1, 2], 3))]:
    circ = QuantumCircuit(4)
    build(circ)
    defs = [line for line in qasm2.dumps(circ).splitlines() if line.startswith("gate ")]
    head = (defs[0][:64] + "...") if defs else "-"
    print(f"{name:5s}: {len(defs)} gate definition(s)   {head}")

uni = QuantumCircuit(1)
uni.append(UnitaryGate(np.array([[0, 1], [1, 0]])), [0])
print()
print(qasm2.dumps(uni))

par = QuantumCircuit(1)
par.rz(Parameter("θ"), 0)
try:
    qasm2.dumps(par)
except Exception as exc:
    print("unbound parameter ->", type(exc).__name__ + ":", str(exc)[:60])

cond = QuantumCircuit(1, 1)
cond.h(0)
cond.measure(0, 0)
with cond.if_test((cond.clbits[0], 1)):
    cond.x(0)
try:
    qasm2.dumps(cond)
except Exception as exc:
    print("if_test on one clbit ->", type(exc).__name__ + ":", str(exc)[:60])
```

Real output:

```
swap : 0 gate definition(s)   -
sx   : 0 gate definition(s)   -
cp   : 0 gate definition(s)   -
rzz  : 0 gate definition(s)   -
ecr  : 1 gate definition(s)   gate ecr q0,q1 { s q0; sx q1; cx q0,q1; x q0; }...
mcx  : 1 gate definition(s)   gate mcx q0,q1,q2,q3 { h q3; p(pi/8) q0; p(pi/8) q1; p(pi/8) q2;...

OPENQASM 2.0;
include "qelib1.inc";
gate unitary q0 { u(pi,-pi,0) q0; }
qreg q[1];
unitary q[0];
unbound parameter -> QASM2ExportError: 'Cannot represent circuits with unbound parameters in OpenQA
if_test on one clbit -> QASM2ExportError: 'OpenQASM 2 only supports register-equality conditions'
```

**Three categories.**

1. **Emitted bare, no definition**: everything in Qiskit's *extended* qelib1 —
   `swap`, `sx`, `sxdg`, `cp`, `csx`, `cu`, `rxx`, `rzz`, `cswap`, `crx`, `cry`,
   `c3x`, `c4x`, `p`, `u`, … This is why other parsers (and Qiskit's own default
   importer) may reject Qiskit-written QASM 2: those names are **not** in the
   published `qelib1.inc`. Import such files with
   `custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS`.
2. **Emitted with an automatic `gate` definition**: anything Qiskit knows how to
   decompose but that has no standard name — `ecr`, `mcx`/multi-controlled gates,
   `UnitaryGate` (exported as `gate unitary q0 { u(pi,-pi,0) q0; }`, i.e. the matrix
   is first synthesised into Euler angles), `PauliEvolutionGate` after decomposition,
   and any user-defined `Gate` subclass with a definition.
3. **Cannot be exported at all** — `QASM2ExportError`:
   - unbound `Parameter`s ("Cannot represent circuits with unbound parameters");
   - conditionals that are not whole-register equality ("OpenQASM 2 only supports
     register-equality conditions") — so `if_test` on a single clbit fails, while
     `qc.if_test((creg, 3))`-style register conditions export as `if (c == 3)`;
   - `for`/`while` loops, `switch`, `break`/`continue`, mid-circuit typed classical
     computation — none of which QASM 2 has;
   - custom instructions with no `definition` (opaque gates) unless you pass them
     explicitly.

**Practical checklist before exporting.** Bind all parameters; transpile to a target
basis (`basis_gates=['u3','cx']` for maximum portability); replace dynamic control
flow with QASM 3 or with post-selection; and always test with
`qasm2.loads(qasm2.dumps(qc), custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)`
plus a `process_fidelity` check.

</details>

- Compare QASM 2 and Quil for the same circuit

<details><summary>Solution</summary>

The same Bell-state-and-measure program in both languages.

**OpenQASM 2** (IBM / Qiskit):

```qasm
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];

h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
```

**Quil** (Rigetti / pyQuil):

```
DECLARE ro BIT[2]

H 0
CNOT 0 1

MEASURE 0 ro[0]
MEASURE 1 ro[1]
```

**Structural comparison.**

| Aspect | OpenQASM 2 | Quil |
|---|---|---|
| Qubit declaration | `qreg q[2];` — named registers | none; qubits are bare integers `0, 1, 2 …` |
| Classical memory | `creg c[2];` | `DECLARE ro BIT[2]` — typed regions (`BIT`, `OCTET`, `INTEGER`, `REAL`) |
| Statement terminator | `;` | newline |
| Gate application | `cx q[0], q[1];` | `CNOT 0 1` |
| Measurement | `measure q[0] -> c[0];` | `MEASURE 0 ro[0]` |
| Custom gates | `gate name(params) a, b { … }` | `DEFGATE NAME AS MATRIX` (literal matrix!) or `DEFCIRCUIT` |
| Control flow | none (only `if (c == k)`) | `LABEL @start`, `JUMP`, `JUMP-WHEN`, `JUMP-UNLESS` — full classical branching |
| Classical arithmetic | none | `ADD`, `MUL`, `MOVE`, `EQ`, `LT` on declared memory |
| Parameterised programs | no | yes — `RX(theta) 0` with `theta` a declared `REAL` bound at run time |
| Timing / pulses | no (QASM 3 adds it) | Quil-T (`PULSE`, `DELAY`, `FENCE`, frames) |
| Native gate set | `u1/u2/u3`, `cx` | `RX(±π/2)`, `RZ(θ)`, `CZ`, `XY(θ)` |

**The substantive differences.**

1. **Quil was born with classical control.** `JUMP-WHEN` plus declared memory makes
   Quil a hybrid quantum/classical assembly language from day one — the capability
   OpenQASM only gained in version 3. Rigetti's parametric compilation (compile
   once, rebind `REAL` parameters per shot) follows directly from that design and is
   why Quil programs avoid the recompilation overhead that plagued early QASM 2
   variational loops.
2. **Custom gates.** QASM defines them *constructively* (a body of other gates);
   Quil's `DEFGATE ... AS MATRIX` lets you write the unitary literally, leaving
   synthesis to the compiler.
3. **No registers in Quil.** Qubits are global integers, so there is no
   virtual-to-physical distinction in the language itself — `PRAGMA
   INITIAL_REWIRING` controls mapping instead.
4. **Native gate sets differ** because the hardware differs: IBM's `cx`/`ecr` versus
   Rigetti's `CZ`/`XY`. Both formats are portable in principle, but a program
   written in either will be re-synthesised by the target compiler.

**Where each is used today.** OpenQASM (2 and 3) is the de facto interchange format
— Qiskit, Cirq, tket, Braket, Q# via conversion. Quil is essentially Rigetti-only,
but it is worth knowing because it pioneered the hybrid-control features that
OpenQASM 3 later adopted, and because Braket accepts both.

</details>


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

<details><summary>Solution</summary>

**Executable?** No. `defcal` is part of the OpenQASM 3 spec with the OpenPulse
grammar; it is not something Qiskit 2.x can parse or run (`qiskit.pulse` was deleted
in Qiskit 2.0, and IBM retired pulse access at the end of 2024). This answer is
spec-level, and the verification at the end shows exactly how the toolchain refuses
it.

A DRAG (Derivative Removal by Adiabatic Gate) pulse is a Gaussian on the in-phase
quadrature plus its scaled derivative on the quadrature channel:

```
Ω(t) = A·exp(−(t − t₀)²/2σ²)  +  i·β·(dΩ_I/dt)
```

The derivative term cancels leakage into the `|2⟩` state of the transmon, which is
the dominant coherent error for short single-qubit pulses. `β` is calibrated per
qubit (typically `β ≈ −1/Δ`, with `Δ` the anharmonicity, a few hundred MHz).

```qasm
OPENQASM 3.0;
defcalgrammar "openpulse";

cal {
  extern port d0;                              // physical drive port of qubit 0
  frame drive_f = newframe(d0, 5.02e9, 0.0);   // frame at the qubit frequency
}

// Calibrated X gate on physical qubit 0
defcal x $0 {
  play(drive_f, drag(0.1832, 160dt, 40dt, -1.284));
  //             amplitude, duration, sigma, beta
}

// A calibrated sqrt(X), the usual hardware primitive: half the amplitude
defcal sx $0 {
  play(drive_f, drag(0.0916, 160dt, 40dt, -1.284));
}

// Virtual Z: no pulse at all, just advance the frame phase
defcal rz(angle[32] theta) $0 {
  shift_phase(drive_f, -theta);
}

qubit[1] q;
x $0;
```

**Points a good answer makes.**

- The calibration is attached to a **physical** qubit (`$0`), not a virtual one —
  calibrations are device- and qubit-specific, so `defcal x $0` and `defcal x $1`
  have different amplitudes.
- `dt` is the backend's sample period (typically `0.222 ns` on IBM hardware);
  durations must be multiples of it and often of a hardware granularity (16 samples).
- `rz` costs nothing: it is a frame phase shift applied in software to all later
  pulses. This is why `rz` is free on IBM hardware and why the basis is
  `{rz, sx, x, cx/ecr}`.
- Parameters (`amp`, `beta`) come from calibration experiments — Rabi amplitude
  sweeps, DRAG-`β` scans, error-amplifying sequences — re-run daily as the device
  drifts.

**Toolchain check** (this part *is* executable and is the honest bottom line):

```python
from qiskit import qasm3
import importlib.util

DEFCAL_SRC = """OPENQASM 3.0;
defcalgrammar "openpulse";
cal {
  extern port d0;
  frame drive_f = newframe(d0, 5.0e9, 0.0);
}
defcal x $0 {
  play(drive_f, drag(0.2, 160dt, 40dt, 0.3));
}
qubit[1] q;
x $0;
"""
try:
    qasm3.loads(DEFCAL_SRC)
    print("parsed")
except Exception as exc:
    print("qiskit.qasm3.loads ->", type(exc).__name__ + ":", str(exc)[:80])
print("qiskit.pulse available in Qiskit 2.x:",
      importlib.util.find_spec("qiskit.pulse") is not None)
```

Real output:

```
qiskit.qasm3.loads -> QASM3ImporterError: '2,0: node of type CalibrationGrammarDeclaration is not supported'
qiskit.pulse available in Qiskit 2.x: False
```

So treat `defcal` as portable *specification* knowledge — exam-relevant, and live in
some non-IBM stacks (Quil-T, Qibo, AWS Braket pulse control, academic control
software) — but not something you can run through Qiskit today.

</details>

- Define a two-qubit `defcal` for a cross-resonance gate

<details><summary>Solution</summary>

**Not executable** (same reasons as the previous exercise: no `qiskit.pulse`, no
IBM pulse access, and `qiskit.qasm3.loads` rejects `defcalgrammar`). What follows is
spec-level OpenQASM 3 with OpenPulse.

**The physics.** Cross resonance drives the **control** qubit at the **target**
qubit's frequency. The static `ZX` coupling term in the two-transmon Hamiltonian
then generates the entangling rotation

```
H_CR ≈ (ν_ZX/2)·ZX  +  ν_IX·IX  +  ν_ZI·ZI  +  ν_ZZ·ZZ  + …
```

The wanted term is `ZX`; everything else is error. The standard remedy is the
**echoed** CR: two CR pulses of opposite sign separated by an `X` on the control.
The echo cancels the `IX` and `ZI` terms (which do not anticommute the same way)
while the `ZX` terms add, producing `R_ZX(π/2)` — and `R_ZX(π/2)` plus single-qubit
rotations is a CNOT. Simultaneous **rotary** tones on the target suppress residual
`IX`/`ZZ`.

```qasm
OPENQASM 3.0;
defcalgrammar "openpulse";

cal {
  extern port d0;                                // drive port, control qubit 0
  extern port d1;                                // drive port, target qubit 1
  extern port u01;                               // control-to-target coupling port

  frame q0_f  = newframe(d0,  5.02e9, 0.0);      // qubit 0 at its own frequency
  frame q1_f  = newframe(d1,  4.87e9, 0.0);      // qubit 1 at its own frequency
  frame cr_f  = newframe(u01, 4.87e9, 0.0);      // CR tone: qubit 0's port,
                                                 // qubit 1's frequency
}

// Echoed cross-resonance implementing R_ZX(pi/2) on control $0, target $1
defcal ecr $0, $1 {
  barrier q0_f, q1_f, cr_f;

  // first half: CR tone + rotary echo on the target
  play(cr_f, gaussian_square(0.21, 560dt, 64dt, 432dt));
  play(q1_f, gaussian_square(0.03, 560dt, 64dt, 432dt));   // rotary
  barrier q0_f, q1_f, cr_f;

  // echo pulse on the control
  play(q0_f, drag(0.1832, 160dt, 40dt, -1.284));
  barrier q0_f, q1_f, cr_f;

  // second half: opposite sign
  play(cr_f, gaussian_square(-0.21, 560dt, 64dt, 432dt));
  play(q1_f, gaussian_square(-0.03, 560dt, 64dt, 432dt));
  barrier q0_f, q1_f, cr_f;

  play(q0_f, drag(0.1832, 160dt, 40dt, -1.284));           // close the echo
}

// CNOT built from the calibrated ECR plus single-qubit frame/pulse work
defcal cx $0, $1 {
  play(q0_f, drag(0.0916, 160dt, 40dt, -1.284));   // sx on control
  shift_phase(q1_f, -pi/2);                        // virtual rz on target
  ecr $0, $1;
}
```

**Points a good answer makes.**

- `gaussian_square(amp, duration, sigma, width)` is a flat-top pulse: Gaussian
  rise and fall with a `width`-long plateau. The plateau length sets the rotation
  angle; the Gaussian edges limit spectral leakage.
- The CR frame lives on the **control's** port but at the **target's** frequency —
  that mismatch is the whole mechanism, and it is why CR gates are directional and
  why `ecr` appears asymmetrically in IBM's coupling maps.
- `barrier` between the blocks aligns the frames so the echo timing is exact;
  without it the compiler may schedule pulses to overlap incorrectly.
- Durations (`560dt ≈ 124 ns` at `dt = 0.222 ns`) are hardware-granular; total CR
  gate times of `300–600 ns` are typical, which is why two-qubit gates dominate
  circuit duration and hence decoherence error.
- All amplitudes here are illustrative. Real values come from Hamiltonian
  tomography of the CR interaction (measuring `ν_ZX`, `ν_IX`, `ν_ZI` versus pulse
  amplitude) followed by amplitude fine-tuning with error-amplifying sequences.

</details>

- Explain how `defcal` interacts with transpilation

<details><summary>Solution</summary>

**The model.** A compiler normally lowers a circuit through stages:
*virtual gates → basis gates → scheduled basis gates → pulses*. A `defcal` attaches
a pulse-level implementation to a **specific gate signature on specific physical
qubits** — `defcal x $0`, `defcal rz(angle[32] theta) $0`, `defcal ecr $0, $1` — and
tells the compiler: for this exact case, stop lowering and emit these pulses.

**Consequences, in the order they bite.**

1. **Physical qubits only.** A `defcal` matches `$0`, not a virtual qubit, so it can
   only be applied *after* layout and routing have fixed the mapping. Change the
   layout and a different set of calibrations applies. This is why calibration is
   the last compiler stage.
2. **It terminates basis translation.** If `defcal my_gate $0` exists, `my_gate`
   becomes effectively a basis gate for qubit 0: the translator must not decompose
   it further, and the target's gate set is extended for that qubit only. In the old
   Qiskit API this was the `PulseGate`/`calibrations` mechanism — a gate with an
   attached calibration was passed through untouched.
3. **Optimisation must be told to keep its hands off.** Peephole passes that would
   cancel `X·X` or merge rotations are only valid if the calibrated gates really
   implement the ideal unitary. A calibrated gate is a black box to the optimiser
   unless the compiler is given its matrix; typically such gates are frozen after a
   `barrier`-protected block.
4. **Scheduling needs durations.** The pulse body determines the gate's duration,
   which feeds the ALAP/ASAP scheduler, delay insertion and dynamical decoupling.
   A hand-written `defcal` that is longer than the default calibration silently
   changes the whole circuit's timing — and can invalidate DD sequences inserted
   earlier.
5. **Signature matching is exact.** `defcal rz(angle[32] theta) $0` matches any
   angle; `defcal rz(pi/2) $0` matches only that value. A parametric calibration is
   the usual choice for frame-shift gates, a fixed one for amplitude-calibrated
   pulses.

**The Qiskit-specific reality (2026).**

- `qiskit.pulse` was deprecated in Qiskit 1.x and **removed in Qiskit 2.0**; the
  `Target` no longer carries pulse calibrations, and `circuit.calibrations` is gone.
- IBM **retired pulse-level access** on its hardware at the end of 2024, so even with
  an older Qiskit you cannot submit custom calibrations to IBM devices.
- `qiskit.qasm3.loads` rejects the construct outright — verified in the DRAG exercise
  above: `QASM3ImporterError: node of type CalibrationGrammarDeclaration is not
  supported`.
- What replaced it for users: hardware-level control now happens through
  vendor-specific stacks (Qibo/Qibolab, Quil-T, Braket pulse, QICK, academic FPGA
  control systems), while IBM exposes *gate-level* knobs instead — fractional gates,
  dynamical decoupling options, twirling, and `Target`-level gate durations.

**What to say in one sentence.** `defcal` is the hook that lets a program override
the compiler's gate-to-pulse lowering for one gate on one set of physical qubits;
it therefore has to run after layout, it freezes further translation and
optimisation of that gate, and it feeds the scheduler a new duration — which is why
it is both powerful for calibration research and dangerous for a general-purpose
compiler to expose.

</details>


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
