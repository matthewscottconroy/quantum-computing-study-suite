# Qiskit

## Goal
Gain practical, expert-level proficiency with Qiskit — IBM's open-source quantum SDK — to build, simulate, transpile, and execute quantum circuits on real hardware.

---

## Module 1 — Qiskit Architecture and Setup

**Objective:** Understand the structure of the Qiskit ecosystem and get a working environment.

| Component | Purpose |
|---|---|
| `qiskit` | Meta-package, installs core components |
| `qiskit-terra` | Core circuit model (now just `qiskit` in v1.x) |
| `qiskit-aer` | High-performance classical simulators |
| `qiskit-ibm-runtime` | Connect to IBM Quantum hardware |
| `qiskit-experiments` | Calibration and characterization tools |

**Setup:**
```bash
pip install qiskit qiskit-aer qiskit-ibm-runtime
```

**Environment check:**
```python
import qiskit
print(qiskit.__version__)

from qiskit_aer import AerSimulator
sim = AerSimulator()
print(sim.name)
```

**Exercises:**
- Install Qiskit in a virtual environment
- Run `qiskit.version_info` and understand each package version
- Connect to IBM Quantum (requires free account) and list available backends

---

## Module 2 — Building Quantum Circuits

**Objective:** Construct any quantum circuit using Qiskit's `QuantumCircuit` API.

| Concept | Code |
|---|---|
| Create circuit | `qc = QuantumCircuit(n_qubits, n_bits)` |
| Add gates | `qc.h(0)`, `qc.cx(0, 1)`, `qc.t(2)` |
| Barrier | `qc.barrier()` — separates sections visually |
| Measure | `qc.measure(qubit, cbit)` |
| Measure all | `qc.measure_all()` |
| Visualize | `qc.draw('mpl')` |
| Get unitary | `qc.unitary()` (for small circuits) |

**Key gate methods:**

| Gate | Method | Notes |
|---|---|---|
| X, Y, Z | `qc.x(q)`, `qc.y(q)`, `qc.z(q)` | Pauli gates |
| H | `qc.h(q)` | Hadamard |
| S, T, Sdg, Tdg | `qc.s(q)`, `qc.t(q)` | Phase gates and adjoints |
| Rx, Ry, Rz | `qc.rx(θ, q)` | Rotation gates |
| CNOT | `qc.cx(ctrl, tgt)` | Controlled-X |
| CZ | `qc.cz(ctrl, tgt)` | Controlled-Z |
| SWAP | `qc.swap(q1, q2)` | Swap |
| Toffoli | `qc.ccx(c1, c2, tgt)` | |
| Custom gate | `qc.unitary(matrix, qubits)` | Arbitrary unitary |

**Exercises:**
- Build circuits for all four Bell states
- Implement the QFT for n=3 qubits
- Create a circuit for Grover's oracle for a 2-qubit search

---

## Module 3 — Simulation with Qiskit Aer

**Objective:** Use classical simulators to test circuits before running on hardware.

| Simulator | Use Case |
|---|---|
| `AerSimulator` (statevector) | Exact statevector, no shots needed |
| `AerSimulator` (qasm) | Measurement sampling with shots |
| `AerSimulator` (unitary) | Full unitary matrix of circuit |
| `AerSimulator` (density_matrix) | Noisy simulation |
| `StatevectorSimulator` | Legacy, still available |

```python
from qiskit_aer import AerSimulator
from qiskit import transpile

sim = AerSimulator(method='statevector')
qc_t = transpile(qc, sim)
result = sim.run(qc_t, shots=1024).result()
counts = result.get_counts()

# Statevector
from qiskit.quantum_info import Statevector
sv = Statevector(qc)  # No measurement gates allowed
print(sv)
```

**Noise models:**
```python
from qiskit_aer.noise import NoiseModel, depolarizing_error

noise_model = NoiseModel()
error = depolarizing_error(0.01, 1)  # 1% single-qubit depolarizing
noise_model.add_all_qubit_quantum_error(error, ['h', 'x'])

sim_noisy = AerSimulator(noise_model=noise_model)
```

**Exercises:**
- Simulate a Bell state circuit and verify the output statevector
- Add a noise model and observe how counts distribution changes
- Simulate a 10-qubit QFT and measure runtime vs qubit count

---

## Module 4 — Quantum Information Tools

**Objective:** Use Qiskit's `quantum_info` module for state analysis and operator manipulation.

| Tool | Purpose |
|---|---|
| `Statevector` | Represent and manipulate state vectors |
| `DensityMatrix` | Mixed state representation |
| `Operator` | Arbitrary operator/matrix |
| `SparsePauliOp` | Efficient Pauli sum representation |
| `state_fidelity` | Compare two states |
| `process_fidelity` | Compare two channels |
| `partial_trace` | Trace out subsystem |
| `entropy` | Von Neumann entropy |

```python
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace, entropy

sv = Statevector.from_label('00')  # |00⟩
sv = sv.evolve(qc)                 # Apply circuit

dm = DensityMatrix(sv)
rho_A = partial_trace(dm, [1])     # Trace out qubit 1
S = entropy(rho_A, base=2)         # Entanglement entropy
```

**Exercises:**
- Compute the entanglement entropy of each Bell state
- Use `SparsePauliOp` to define the Ising Hamiltonian
- Verify that a CNOT circuit is unitary using `Operator`

---

## Module 5 — Parameterized Circuits and Variational Algorithms

**Objective:** Build parameterized circuits for variational algorithms (VQE, QAOA).

```python
from qiskit.circuit import ParameterVector, Parameter

theta = Parameter('θ')
qc = QuantumCircuit(1)
qc.ry(theta, 0)

# Bind parameters
bound = qc.assign_parameters({theta: 1.57})

# ParameterVector for many parameters
params = ParameterVector('θ', 4)
qc2 = QuantumCircuit(2)
qc2.ry(params[0], 0)
qc2.ry(params[1], 1)
qc2.cx(0, 1)
qc2.ry(params[2], 0)
qc2.ry(params[3], 1)
```

**Exercises:**
- Build the hardware-efficient ansatz for 4 qubits with depth 3
- Implement VQE for the H₂ molecule Hamiltonian
- Build a QAOA circuit for MaxCut on a 4-node graph

---

## Module 6 — Running on IBM Quantum Hardware

**Objective:** Submit jobs to real quantum hardware via IBM Quantum Runtime.

```python
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit import transpile

# Authenticate
service = QiskitRuntimeService(channel="ibm_quantum", token="YOUR_TOKEN")

# Select backend
backend = service.least_busy(operational=True, simulator=False)

# Transpile for hardware
qc_t = transpile(qc, backend, optimization_level=3)

# Run with Sampler primitive
with Sampler(backend) as sampler:
    job = sampler.run([qc_t], shots=1024)
    result = job.result()
    pub_result = result[0]
    counts = pub_result.data.meas.get_counts()
```

**Key concepts:**
- **Primitives**: `SamplerV2` (measurement counts) and `EstimatorV2` (expectation values)
- **Transpilation**: Map abstract circuit to hardware topology and native gates
- **Error mitigation**: ZNE, PEC, measurement error mitigation via `qiskit-ibm-runtime`

**Exercises:**
- Run a Bell state circuit on real hardware and compare to simulation
- Use `EstimatorV2` to measure ⟨Z⊗Z⟩ for a Bell state
- Apply zero-noise extrapolation and observe the improvement

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| Qiskit documentation (docs.quantum.ibm.com) | Official docs | Primary reference |
| IBM Quantum Learning (learning.quantum.ibm.com) | Tutorials | Free, hands-on |
| Qiskit GitHub repository | Source | Read the source |
| *Learn Quantum Computation Using Qiskit* | Online textbook | Free, interactive |

---

## Progression Checkpoints

- [ ] Build, simulate, and visualize circuits for all standard algorithms
- [ ] Use all three AerSimulator methods (statevector, qasm, density_matrix)
- [ ] Construct a parameterized ansatz and optimize its parameters classically
- [ ] Submit a job to real IBM hardware and interpret the noisy results
- [ ] Apply error mitigation and quantify its effect
- [ ] Use `SparsePauliOp` to represent Hamiltonians for VQE
