# Qiskit

## Goal
Gain practical, expert-level proficiency with Qiskit — IBM's open-source quantum SDK — to build, simulate, transpile, and execute quantum circuits on real hardware. Content is aligned with Qiskit 2.x and the IBM Certified Associate Developer — Quantum Computation using Qiskit exam (C1000-179), whose heaviest sections are running circuits (15%), Sampler (12%), Estimator (12%), visualization (11%), and retrieving/analyzing results (10%).

---

## Module 1 — Qiskit Architecture and Setup

**Objective:** Understand the structure of the Qiskit ecosystem and get a working environment.

| Component | Purpose |
|---|---|
| `qiskit` | The core SDK: circuits, transpiler, quantum_info, primitives (the old `qiskit-terra` name was retired in v1.0) |
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
- Print `qiskit.__version__` and the versions of each installed extension package (`qiskit_aer.__version__`, `qiskit_ibm_runtime.__version__`)
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
| Get unitary | `qiskit.quantum_info.Operator(qc)` (for small circuits) — note `qc.unitary(matrix, qubits)` *appends* a unitary gate, it does not return one |

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
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# Sampling counts requires measurements in the circuit
qc_m = qc.copy()
qc_m.measure_all()

sim = AerSimulator(method='statevector')
qc_t = transpile(qc_m, sim)
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
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace, entropy

qc = QuantumCircuit(2)             # Bell-state circuit, no measurements
qc.h(0)
qc.cx(0, 1)

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

## Module 6 — Visualization

**Objective:** Visualize circuits, states, and results — an exam section in its own right (11% of C1000-179).

| Function | Purpose |
|---|---|
| `qc.draw()` | Render a circuit (`output='text'`, `'mpl'`, `'latex'`, `'latex_source'`) |
| `plot_histogram` | Bar chart of raw measurement counts |
| `plot_distribution` | Bar chart of quasi-probabilities/normalized frequencies |
| `plot_bloch_multivector` | One Bloch sphere per qubit (reduced states) |
| `plot_state_qsphere` | Amplitudes and phases of a full state on one sphere |
| `plot_state_city` | 3D bar plot of density-matrix real/imaginary parts |
| `plot_bloch_vector` | A single Bloch vector from coordinates |
| `plot_gate_map` / `plot_coupling_map` | Device topology diagrams |

Install plotting extras with `pip install "qiskit[visualization]"` (`plot_state_qsphere` additionally requires `seaborn`; `'latex'` drawing requires `pylatexenc`).

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import (
    plot_histogram, plot_distribution,
    plot_bloch_multivector, plot_state_qsphere, plot_state_city,
)
from qiskit.primitives import StatevectorSampler

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)

# Circuit drawing options
print(bell.draw(output='text'))         # ASCII art
bell.draw(output='mpl')                 # matplotlib figure
bell.draw(output='mpl', fold=40)        # wrap wide circuits after 40 columns
bell.draw(output='mpl', idle_wires=False)  # hide unused qubits

# Counts visualization
qc = bell.copy()
qc.measure_all()
counts = StatevectorSampler().run([qc], shots=2048).result()[0].data.meas.get_counts()
plot_histogram(counts)
plot_histogram([counts, counts], legend=['run 1', 'run 2'], sort='value_desc')
plot_distribution(counts)               # normalized probabilities

# State visualization (no measurements in the circuit)
sv = Statevector(bell)
plot_bloch_multivector(sv)              # per-qubit reduced Bloch vectors
plot_state_qsphere(sv)                  # global amplitudes + phases
plot_state_city(sv, alpha=0.6)          # density matrix cityscape
```

**Key distinctions the exam tests:**
- `plot_histogram` takes **counts**; `plot_distribution` shows **probabilities** (heights sum to 1)
- `plot_bloch_multivector` shows *reduced* single-qubit states — entangled qubits appear as shrunken vectors (zero-length for a Bell pair)
- `qc.draw()` returns an object (string or figure); it does not display by itself in scripts — use `matplotlib.pyplot.show()` or save with `fig.savefig(...)`

**Exercises:**
- Draw a 5-qubit GHZ circuit with `output='mpl'` and again with `fold` and `idle_wires=False`
- Plot the Bloch multivector of |+⟩⊗|0⟩ and of a Bell state; explain why the Bell state's vectors vanish
- Compare `plot_histogram` and `plot_distribution` for the same noisy counts

---

## Module 7 — Primitives Workflow (Sampler, Estimator, PUBs)

**Objective:** Master the V2 primitives model — the standard execution interface for Qiskit 2.x and the core of exam sections on Sampler (12%), Estimator (12%), and result analysis (10%).

### The two primitives

| Primitive | Question it answers | Input | Output |
|---|---|---|---|
| Sampler (`StatevectorSampler`, `SamplerV2`) | "What bitstrings come out?" | circuits with measurements | per-shot samples / counts |
| Estimator (`StatevectorEstimator`, `EstimatorV2`) | "What is ⟨ψ|O|ψ⟩?" | circuits **without** measurements + observables | expectation values |

Local, exact reference implementations live in base Qiskit (`qiskit.primitives`); hardware implementations live in `qiskit-ibm-runtime`. Both share the same PUB-based interface.

### PUBs (Primitive Unified Blocs)

Each element of the `run()` list is a PUB — a tuple bundling one circuit with everything it needs:

- Sampler PUB: `(circuit,)` or `(circuit, parameter_values)` or `(circuit, parameter_values, shots)`
- Estimator PUB: `(circuit, observables)` or `(circuit, observables, parameter_values)` or `(..., precision)`

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorSampler, StatevectorEstimator

# --- Sampler ---
bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
bell_m = bell.copy()
bell_m.measure_all()

sampler = StatevectorSampler()
job = sampler.run([bell_m], shots=1024)
result = job.result()                     # PrimitiveResult, indexed by PUB
counts = result[0].data.meas.get_counts() # 'meas' = creg name from measure_all()
# qc.measure(q, c) with QuantumCircuit(n, m) puts data under result[0].data.c

# --- Estimator ---
obs = SparsePauliOp(["ZZ", "XX"], coeffs=[1.0, 1.0])
estimator = StatevectorEstimator()
job = estimator.run([(bell, obs)])        # circuit has NO measurements
result = job.result()
print(result[0].data.evs)                 # expectation value(s)

# --- Parameterized PUB: one circuit, many parameter sets ---
theta = Parameter("θ")
pqc = QuantumCircuit(1)
pqc.ry(theta, 0)
job = estimator.run([(pqc, SparsePauliOp("Z"), [[0.0], [np.pi]])])
print(job.result()[0].data.evs)           # array([ 1., -1.])
```

### Hardware primitives, ISA circuits, and execution modes

Runtime primitives require **ISA circuits** — circuits already transpiled to the backend's basis gates and connectivity. Transpile with a preset pass manager before calling a primitive:

```python
# Requires qiskit-ibm-runtime and an IBM Quantum account
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import (
    QiskitRuntimeService, SamplerV2, EstimatorV2, Session, Batch,
)

service = QiskitRuntimeService()  # account saved previously
backend = service.least_busy(operational=True, simulator=False)

pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa_circuit = pm.run(bell_m)

# Job mode: one-off request
sampler = SamplerV2(mode=backend)
job = sampler.run([isa_circuit], shots=4096)
counts = job.result()[0].data.meas.get_counts()

# Session mode: iterative workloads (VQE) get dedicated backend access
with Session(backend=backend) as session:
    estimator = EstimatorV2(mode=session)
    isa_obs = obs.apply_layout(isa_circuit.layout)   # map observable to physical qubits
    job = estimator.run([(pm.run(bell), isa_obs)])
    evs = job.result()[0].data.evs

# Batch mode: many independent jobs scheduled together
with Batch(backend=backend) as batch:
    sampler = SamplerV2(mode=batch)
    jobs = [sampler.run([c]) for c in [isa_circuit]]
```

| Mode | Use case |
|---|---|
| Job | Single primitive call |
| Batch | Many independent PUB sets, parallel scheduling |
| Session | Iterative feedback loops; exclusive backend window |

### Error suppression and mitigation (survey level)

| Option | Type | Where |
|---|---|---|
| Dynamical decoupling | Suppression | `options.dynamical_decoupling.enable = True`, `sequence_type="XY4"` |
| Pauli twirling | Suppression | `options.twirling.enable_gates = True` |
| Measurement (readout) mitigation | Mitigation | Estimator `resilience_level ≥ 1` / `options.resilience.measure_mitigation` |
| ZNE (zero-noise extrapolation) | Mitigation | Estimator `options.resilience_level = 2` or `options.resilience.zne_mitigation` |
| Resilience level | Preset bundle | `EstimatorV2.options.resilience_level = 0/1/2` (Sampler has no resilience levels) |

**Exercises:**
- Run one `StatevectorSampler` job containing three PUBs and extract each PUB's counts
- Sweep θ from 0 to 2π in a single Estimator PUB and plot ⟨Z⟩(θ)
- Explain why the Estimator needs measurement-free circuits and how it measures Pauli terms internally
- Rewrite a `transpile()`-based script to use `generate_preset_pass_manager` and check the circuit is ISA for a given backend

---

## Module 8 — Running on IBM Quantum Hardware

**Objective:** Submit jobs to real quantum hardware via IBM Quantum Runtime, then retrieve and analyze the results.

```python
# Requires: pip install qiskit-ibm-runtime
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# Authenticate (one-time; credentials are stored on disk).
# The legacy "ibm_quantum" channel was sunset mid-2025; use the
# IBM Quantum Platform channel on IBM Cloud.
QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token="YOUR_API_KEY",
    overwrite=True,
)
service = QiskitRuntimeService()

# Select backend
backend = service.least_busy(operational=True, simulator=False)

# Transpile to an ISA circuit for this backend
pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
qc_isa = pm.run(qc)

# Run with the Sampler primitive (job mode)
sampler = Sampler(mode=backend)
job = sampler.run([qc_isa], shots=1024)
print(job.job_id(), job.status())

result = job.result()
pub_result = result[0]
counts = pub_result.data.meas.get_counts()

# Retrieve a past job later
job = service.job(job_id)
```

**Key concepts:**
- **Primitives**: `SamplerV2` (measurement counts) and `EstimatorV2` (expectation values) — see Module 7
- **ISA requirement**: runtime primitives reject circuits not transpiled to the backend's target
- **Job lifecycle**: `job.status()`, `job.result()`, `job.metrics()`, `service.jobs()` for history
- **Error suppression/mitigation**: dynamical decoupling, twirling, resilience levels via primitive options

**Exercises:**
- Run a Bell state circuit on real hardware and compare to simulation
- Use `EstimatorV2` to measure ⟨Z⊗Z⟩ for a Bell state (remember `observable.apply_layout`)
- Enable dynamical decoupling and gate twirling on a Sampler job and compare counts
- Retrieve yesterday's jobs with `service.jobs()` and re-load one result by job ID

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
- [ ] Compose Sampler and Estimator PUBs (with parameter sweeps) and extract results by classical-register name
- [ ] Use every core visualization: `plot_histogram`, `plot_distribution`, `plot_bloch_multivector`, `plot_state_qsphere`, `plot_state_city`
- [ ] Produce an ISA circuit with `generate_preset_pass_manager` and explain why runtime primitives require it
- [ ] Submit a job to real IBM hardware and interpret the noisy results
- [ ] Apply error suppression/mitigation (dynamical decoupling, twirling, resilience levels) and quantify the effect
- [ ] Use `SparsePauliOp` to represent Hamiltonians for VQE
