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

<details><summary>Solution</summary>

**Model answer.** Qiskit must never go into the system Python — it pins numpy,
scipy and rustworkx versions, and Qiskit 1.0 renamed/removed the old `qiskit-terra`
and `qiskit-ibmq-provider` packages, so a mixed environment is the number-one cause
of import errors.

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install qiskit qiskit-aer qiskit-ibm-runtime
pip install "qiskit[visualization]"  # matplotlib, pylatexenc, seaborn, pydot
pip freeze > requirements.txt        # pin what you actually got
```

Then verify inside the venv:

```python
import sys, qiskit
from qiskit_aer import AerSimulator
print("python", sys.version.split()[0])
print("qiskit", qiskit.__version__)
print("AerSimulator backend name:", AerSimulator().name)
```

Real output from this repo's venv:

```
python 3.14.7
qiskit 2.5.2
AerSimulator backend name: aer_simulator
```

**Points a good answer makes.**

- The venv must be *activated* (or its interpreter invoked by full path) for every
  later command — `which python` should point inside `.venv/`.
- `qiskit` is the whole SDK since 1.0; `pip install qiskit-terra` is wrong today.
- `qiskit-aer` and `qiskit-ibm-runtime` are separate distributions that version
  independently of `qiskit`; upgrade them together.
- Pin versions in `requirements.txt` for reproducibility — primitive result classes
  and transpiler defaults have changed between minor versions.

</details>

- Print `qiskit.__version__` and the versions of each installed extension package (`qiskit_aer.__version__`, `qiskit_ibm_runtime.__version__`)

<details><summary>Solution</summary>

The robust way is `importlib.metadata` rather than `__version__` attributes: it
reads the installed *distribution* metadata, works for packages that do not export
`__version__`, and does not import the (slow) package itself.

```python
import sys
import importlib.metadata as md
import qiskit

print("python              ", sys.version.split()[0])
print("qiskit              ", qiskit.__version__)
for pkg in ["qiskit-aer", "qiskit-ibm-runtime", "qiskit-qasm3-import"]:
    try:
        print(f"{pkg:20s}", md.version(pkg))
    except md.PackageNotFoundError:
        print(f"{pkg:20s} not installed")
```

Real output:

```
python               3.14.7
qiskit               2.5.2
qiskit-aer           0.17.2
qiskit-ibm-runtime   0.49.0
qiskit-qasm3-import  0.6.0
```

**Notes.** `qiskit_aer.__version__` and `qiskit_ibm_runtime.__version__` also work
and are what the exam is likely to show; the distribution names use hyphens
(`qiskit-aer`) while the import names use underscores (`qiskit_aer`) — a routine
source of confusion. For a full dependency dump use `qiskit.__version_info__` or
`pip list | grep qiskit`. Note the three packages version *independently*: Qiskit
2.5 with Aer 0.17 and Runtime 0.49 is a normal, consistent combination.

</details>

- Connect to IBM Quantum (requires free account) and list available backends

<details><summary>Solution</summary>

**Not executable in this repository** — there is no IBM Quantum account configured
here, so the code below is given in API-correct form and marked as requiring
credentials. (The legacy `ibm_quantum` channel was retired mid-2025; the current
channel is `ibm_quantum_platform` on IBM Cloud.)

```python
from qiskit_ibm_runtime import QiskitRuntimeService

# One-time: store credentials on disk (~/.qiskit/qiskit-ibm.json)
QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token="YOUR_API_KEY",
    overwrite=True,
    set_as_default=True,
)

service = QiskitRuntimeService()                 # reads the saved account

for backend in service.backends():
    status = backend.status()
    print(f"{backend.name:20s} qubits={backend.num_qubits:4d} "
          f"sim={backend.simulator} pending={status.pending_jobs}")

# Filtering is what you actually use day to day
real = service.backends(simulator=False, operational=True, min_num_qubits=127)
best = service.least_busy(operational=True, simulator=False)
print("least busy:", best.name, best.num_qubits)
print("basis gates:", best.configuration().basis_gates if hasattr(best, "configuration")
      else sorted(best.operation_names))
```

Expected shape of the output (names and queue depths vary):

```
ibm_brisbane         qubits= 127 sim=False pending=12
ibm_sherbrooke       qubits= 127 sim=False pending=45
ibm_torino           qubits= 133 sim=False pending=7
least busy: ibm_torino 133
```

**Offline substitute** that exercises the same API surface — the snapshot backends
shipped with `qiskit-ibm-runtime` (also not run by this repo's snippet checker,
which skips anything importing `qiskit_ibm_runtime`):

```python
from qiskit_ibm_runtime.fake_provider import FakeProviderForBackendV2

provider = FakeProviderForBackendV2()
backends = provider.backends()
print("fake backends available:", len(backends))
for b in backends[:5]:
    print(f"  {b.name:18s} {b.num_qubits:4d} qubits")
```

Real output from this venv (`qiskit-ibm-runtime` 0.49.0):

```
fake backends available: 68
  fake_aachen         156 qubits
  fake_algiers         27 qubits
  fake_almaden         20 qubits
  fake_armonk           1 qubits
  fake_athens           5 qubits
```

**Points a good answer makes.** Credentials are stored once and reused; never hard-
code a token into a committed file. `service.backends()` accepts filters
(`simulator=`, `operational=`, `min_num_qubits=`, arbitrary `filters=` callables)
and `least_busy()` is the standard way to pick a device. What you get back is a
`BackendV2`, whose `target` carries basis gates, coupling map and calibration data —
the same object `generate_preset_pass_manager` needs to produce ISA circuits.

</details>


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

<details><summary>Solution</summary>

One parameterised builder covers all four: prepare `|xy⟩`, then `H` on qubit 0 and
`CNOT(0 → 1)`.

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def bell_pair(x, y):
    """|beta_xy> = (|0y> + (-1)^x |1 not-y>)/sqrt(2)."""
    qc = QuantumCircuit(2)
    if x:
        qc.x(0)          # sets the sign bit
    if y:
        qc.x(1)          # sets the parity bit
    qc.h(0)
    qc.cx(0, 1)
    return qc

for x in (0, 1):
    for y in (0, 1):
        amps = Statevector(bell_pair(x, y)).to_dict()
        print(f"beta_{x}{y}:", {k: round(complex(v).real, 4) for k, v in amps.items()})
```

Real output:

```
beta_00: {'00': 0.7071, '11': 0.7071}
beta_01: {'01': 0.7071, '10': 0.7071}
beta_10: {'00': 0.7071, '11': -0.7071}
beta_11: {'01': -0.7071, '10': 0.7071}
```

(The dictionary keys that Qiskit prints are `numpy.str_` objects; they are shown
here as plain strings.)

**Reading the keys.** Qiskit is **little-endian**: the key `'01'` means
`q₁ = 0, q₀ = 1`. So `beta_11` printing `{'01': -0.7071, '10': 0.7071}` is
`(|q₀=0, q₁=1⟩ − |q₀=1, q₁=0⟩)/√2`, i.e. `|Ψ⁻⟩` written in qubit order — not a sign
error. This endianness question appears on the exam constantly.

**Identification.** `beta_00 = |Φ⁺⟩`, `beta_01 = |Ψ⁺⟩`, `beta_10 = |Φ⁻⟩`,
`beta_11 = |Ψ⁻⟩`. The `x` bit flips the relative sign (equivalent to a `Z` on
either qubit *after* the entangler), the `y` bit flips the parity (an `X` after the
entangler).

**Checks worth adding.** `Statevector(...).is_valid()` confirms normalisation;
`state_fidelity(Statevector(bell_pair(0,0)), Statevector.from_label("00"))` would be
0.5, so do not use fidelity against a product state as a Bell-ness test — use
`partial_trace` + `entropy` (see Module 4) instead.

</details>

- Implement the QFT for n=3 qubits

<details><summary>Solution</summary>

The QFT on `n` qubits is a Hadamard on each qubit interleaved with controlled phase
rotations `R_k = diag(1, e^{2πi/2^k})`, followed by a qubit reversal:

```
QFT|j⟩ = (1/√N) Σ_k e^{2πi jk/N} |k⟩ ,   N = 2ⁿ
```

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator

def qft_circuit(n):
    qc = QuantumCircuit(n, name="QFT")
    for j in range(n - 1, -1, -1):
        qc.h(j)
        for k in range(j - 1, -1, -1):
            qc.cp(np.pi / 2 ** (j - k), k, j)     # controlled phase R_{j-k+1}
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)                     # reverse the qubit order
    return qc

qft3 = qft_circuit(3)
print(qft3.draw(output="text"))

ref3 = QuantumCircuit(3)
ref3.append(QFTGate(3), [0, 1, 2])
print("matches QFTGate(3):", Operator(qft3).equiv(Operator(ref3)))

mat3 = Operator(qft3).data
print("row 0 (all 1/sqrt(8)):", np.round(mat3[0], 4))
print("M[1,1] =", np.round(mat3[1, 1], 4),
      " expected exp(2i.pi/8)/sqrt(8) =", np.round(np.exp(2j * np.pi / 8) / np.sqrt(8), 4))
```

Real output:

```
                                          ┌───┐   
q_0: ───────────────■─────────────■───────┤ H ├─X─
                    │       ┌───┐ │P(π/2) └───┘ │ 
q_1: ──────■────────┼───────┤ H ├─■─────────────┼─
     ┌───┐ │P(π/2)  │P(π/4) └───┘               │ 
q_2: ┤ H ├─■────────■───────────────────────────X─
     └───┘                                        
matches QFTGate(3): True
row 0 (all 1/sqrt(8)): [0.3536+0.j 0.3536+0.j 0.3536+0.j 0.3536+0.j 0.3536+0.j 0.3536+0.j
 0.3536+0.j 0.3536+0.j]
M[1,1] = (0.25+0.25j)  expected exp(2i.pi/8)/sqrt(8) = (0.25+0.25j)
```

**Why it is correct.** Row 0 of the matrix is uniform `1/√8` (the QFT of `|0⟩` is
the uniform superposition), and the `(1,1)` entry is `e^{2πi/8}/√8 = (0.25 + 0.25i)`
— the defining phase. `Operator(...).equiv(...)` against `QFTGate(3)` returns
`True`, which is the decisive check (`equiv` allows a global phase; `==` would not).

**Details that matter.**

- **Gate count**: `n(n−1)/2` controlled-phase gates plus `n` Hadamards plus
  `⌊n/2⌋` swaps — `O(n²)`, versus `O(N log N) = O(n 2ⁿ)` for the classical FFT.
- **The swaps** exist only because the naive construction outputs the bits in
  reverse order. On hardware they are usually *not* applied: you relabel the
  qubits, or let the transpiler absorb the permutation (`QFTGate` has a
  `do_swaps`-free synthesis path via `qiskit.synthesis.synth_qft_full`).
- **Approximate QFT**: dropping rotations with `2^{-k}` below the noise floor
  (`k > log n + 2`) costs `O(n log n)` gates with negligible error — standard in
  Shor implementations.
- The old `qiskit.circuit.library.QFT` *class* is deprecated as of Qiskit 2.1; use
  `QFTGate` or `qiskit.synthesis.synth_qft_full`.

</details>

- Create a circuit for Grover's oracle for a 2-qubit search

<details><summary>Solution</summary>

A Grover oracle is a *phase* oracle: `|x⟩ → (−1)^{f(x)}|x⟩`. For a single marked
2-qubit string, sandwich a `CZ` between `X` gates on the qubits that must be `0`.

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

def grover_oracle_2q(marked):
    """Phase oracle: |marked> -> -|marked>, everything else unchanged."""
    qc = QuantumCircuit(2, name=f"oracle {marked}")
    if marked[1] == "0":
        qc.x(0)
    if marked[0] == "0":
        qc.x(1)
    qc.cz(0, 1)
    if marked[1] == "0":
        qc.x(0)
    if marked[0] == "0":
        qc.x(1)
    return qc

for target in ["00", "01", "10", "11"]:
    diag = np.round(np.diag(Operator(grover_oracle_2q(target)).data).real, 3)
    print(f"oracle for |{target}>: diag(U) = {diag}")

grover2 = QuantumCircuit(2)
grover2.h([0, 1])
grover2.compose(grover_oracle_2q("11"), inplace=True)     # oracle
grover2.h([0, 1]); grover2.x([0, 1])                      # diffuser
grover2.cz(0, 1)
grover2.x([0, 1]); grover2.h([0, 1])
print("after one Grover iteration:",
      {k: round(complex(v).real, 4) for k, v in Statevector(grover2).to_dict().items()})
```

Real output:

```
oracle for |00>: diag(U) = [-1.  1.  1.  1.]
oracle for |01>: diag(U) = [ 1. -1.  1.  1.]
oracle for |10>: diag(U) = [ 1.  1. -1.  1.]
oracle for |11>: diag(U) = [ 1.  1.  1. -1.]
after one Grover iteration: {'00': -0.0, '01': -0.0, '10': -0.0, '11': -1.0}
```

**Verification.** Each oracle's matrix is diagonal with exactly one `−1`, in the
position of the marked string — that *is* the definition, so printing the diagonal
is a complete check.

**The one-iteration miracle.** For `N = 4` with one marked item,
`k* = (π/4)√4 ≈ 1.57`, and the rotation picture says one iteration rotates the
state by `2θ` with `sin θ = 1/2`, i.e. `2θ = 60°` — from `30°` to exactly `90°`, the
marked state. So 2-qubit Grover is **exact**: amplitude `−1` on `|11⟩`, zero
elsewhere (the overall `−1` is an unobservable global phase). Running a second
iteration would rotate *past* the target and destroy the answer.

**Other ways to build the oracle** (all equivalent, worth recognising on the exam):

- `qc.cz(0, 1)` alone marks `|11⟩`; conjugating with `X` moves the mark.
- Boolean-style: use an ancilla in `|−⟩` and a multi-controlled `X`; the phase
  appears by kickback. Costs a qubit but generalises to any `f`.
- `qiskit.circuit.library.PhaseOracleGate("a & b")` builds one from a Boolean
  expression (the older `PhaseOracle` class is deprecated as of Qiskit 2.2), and
  `GroverOperator(oracle)` wraps oracle + diffuser into one object.

**The diffuser** `H^⊗n X^⊗n · CZ · X^⊗n H^⊗n` is the reflection about the uniform
superposition, `2|s⟩⟨s| − I`. Oracle + diffuser = one Grover iteration.

</details>


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

<details><summary>Solution</summary>

There are three routes, and knowing which needs measurements is exam material.

```python
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

bell_v = QuantumCircuit(2)
bell_v.h(0)
bell_v.cx(0, 1)

sv_v = Statevector(bell_v)                       # no measurements allowed here
print("statevector:", np.round(sv_v.data, 6))
print("equals (|00>+|11>)/sqrt(2):",
      np.allclose(sv_v.data, np.array([1, 0, 0, 1]) / np.sqrt(2)))

bell_vm = bell_v.copy()
bell_vm.measure_all()
sim_v = AerSimulator()
print("counts:", sim_v.run(transpile(bell_vm, sim_v), shots=4096,
                           seed_simulator=7).result().get_counts())

bell_vs = bell_v.copy()
bell_vs.save_statevector()                       # Aer instruction, not a gate
sim_sv = AerSimulator(method="statevector")
out = sim_sv.run(transpile(bell_vs, sim_sv)).result()
print("Aer save_statevector:", np.round(np.asarray(out.get_statevector()), 6))
```

Real output:

```
statevector: [0.707107+0.j 0.      +0.j 0.      +0.j 0.707107+0.j]
equals (|00>+|11>)/sqrt(2): True
counts: {'00': 2039, '11': 2057}
Aer save_statevector: [0.707107+0.j 0.      +0.j 0.      +0.j 0.707107+0.j]
```

**The three routes.**

1. `Statevector(qc)` — pure Qiskit, exact, **no measurements allowed** in the
   circuit. Fastest for verification.
2. `AerSimulator().run(...)` with `measure_all()` — sampling. Counts split
   `≈ 50/50` between `00` and `11` and **never** produce `01` or `10`; that
   absence is the signature of the Bell correlation.
3. `AerSimulator(method="statevector")` with `qc.save_statevector()` — Aer's own
   instruction, which snapshots the state mid-circuit. Note `save_statevector` is
   an Aer instruction, so the circuit must be transpiled for an Aer backend.

**Why counts alone do not prove entanglement.** The classical mixture
`½(|00⟩⟨00| + |11⟩⟨11|)` gives identical `Z`-basis counts. To distinguish, measure
in a rotated basis too (`XX` correlations, as in the CHSH exercise of lesson 08) or
compute the reduced state and its entropy (next module).

**Seeding.** `seed_simulator=7` makes the counts reproducible — always seed when
you want a doc, a test, or a bug report to be repeatable.

</details>

- Add a noise model and observe how counts distribution changes

<details><summary>Solution</summary>

```python
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

nm_d = NoiseModel()
nm_d.add_all_qubit_quantum_error(depolarizing_error(0.05, 1), ["h", "x"])
nm_d.add_all_qubit_quantum_error(depolarizing_error(0.05, 2), ["cx"])

sim_clean = AerSimulator()
sim_dirty = AerSimulator(noise_model=nm_d)

c_clean = sim_clean.run(transpile(bell_vm, sim_clean), shots=8192,
                        seed_simulator=11).result().get_counts()
c_dirty = sim_dirty.run(transpile(bell_vm, sim_dirty), shots=8192,
                        seed_simulator=11).result().get_counts()
print("ideal:", dict(sorted(c_clean.items())))
print("noisy:", dict(sorted(c_dirty.items())))
leak = sum(v for k, v in c_dirty.items() if k in ("01", "10")) / 8192
print(f"fraction of impossible outcomes (01, 10): {leak:.4f}")
```

Real output:

```
ideal: {'00': 4054, '11': 4138}
noisy: {'00': 3947, '01': 103, '10': 122, '11': 4020}
fraction of impossible outcomes (01, 10): 0.0275
```

**What changed and why.** The ideal Bell state can only produce `00` or `11`.
With 5% depolarizing noise on `h` and `cx`, about **2.75%** of shots land on `01`
or `10` — outcomes forbidden by the noiseless physics. These are the direct
signature of errors, and their fraction is a crude but useful error metric.

**Arithmetic check.** A 2-qubit depolarizing channel with parameter `p = 0.05`
replaces the state with the maximally mixed state with probability `p`, which sends
a quarter of those shots to each of the four outcomes — so `01`+`10` should get
about `p/2 = 2.5%` from the `cx` alone, plus a smaller contribution from the
single-qubit error on `h`. Measured `2.75%`: consistent.

**Building more realistic models.**

- `NoiseModel.from_backend(backend)` constructs a model from a real device's
  calibration data (`T₁`, `T₂`, gate errors, readout error) — far more
  representative than uniform depolarizing noise.
- `thermal_relaxation_error(t1, t2, gate_time)` models decoherence during gates.
- `pauli_error([('X', p), ('I', 1-p)])` for a simple bit-flip channel.
- Readout error via `ReadoutError([[1-p01, p01], [p10, 1-p10]])` — often the
  single largest error source on real hardware, and the one that mitigation
  removes most cheaply.

**Warning.** `add_all_qubit_quantum_error(err, ['h','x'])` attaches the error to
gates *by name after transpilation*. If your circuit is transpiled to `{rz, sx, cx}`
there are no `h` gates left, and your noise model silently does nothing. Always
check `transpile(...).count_ops()` against the gate names in the model.

</details>

- Simulate a 10-qubit QFT and measure runtime vs qubit count

<details><summary>Solution</summary>

```python
import time
from qiskit import transpile
from qiskit_aer import AerSimulator

sim_scale = AerSimulator(method="statevector")
print(f"{'n':>3} {'2q gates':>9} {'runtime s':>10} {'|psi> MiB':>10}")
for n in [8, 12, 16, 20, 22]:
    circ = qft_circuit(n)
    circ.measure_all()
    tcirc = transpile(circ, sim_scale)
    t0 = time.perf_counter()
    sim_scale.run(tcirc, shots=256, seed_simulator=3).result()
    dt = time.perf_counter() - t0
    print(f"{n:>3} {n * (n - 1) // 2 + n // 2:>9} {dt:>10.3f} {2 ** n * 16 / 2 ** 20:>10.2f}")
```

Real output (this machine; absolute times vary, the *scaling* is the point):

```
  n  2q gates  runtime s  |psi> MiB
  8        32      0.014       0.00
 12        72      0.017       0.06
 16       128      0.415       1.00
 20       200      0.565      16.00
 22       242      0.840      64.00
```

Extending to `n = 24` on the same machine: `1.85 s` and `256 MiB` for the state
vector.

**What the numbers say.**

- The **circuit** grows quadratically: `n(n−1)/2 + ⌊n/2⌋` two-qubit gates
  (45 at `n = 10`, 242 at `n = 22`).
- The **simulation** grows exponentially: the state vector needs `2ⁿ × 16` bytes
  (complex128), i.e. 16 MiB at `n = 20`, 256 MiB at `n = 24`, **16 TiB at `n = 40`**.
  Runtime follows memory once the state no longer fits in cache — note the jump
  between `n = 12` (0.02 s, 64 KiB, cache-resident) and `n = 16` (0.4 s, 1 MiB).
- Below `n ≈ 14` the measurement is dominated by Python/transpiler overhead, which
  is why the first rows look flat.

**How to push further.** `AerSimulator(method="matrix_product_state")` handles far
more qubits when entanglement is low (a QFT on a product-state input is nearly
free); `method="stabilizer"` is polynomial but Clifford-only (a QFT is not
Clifford); `method="extended_stabilizer"` interpolates. GPU builds and
`max_parallel_threads` help by constants, not by changing the exponential.

**The lesson for the exam.** Statevector simulation is exponential in qubit count
and roughly linear in gate count; ~30 qubits is a laptop limit, ~50 a supercomputer
limit. That gap is the whole motivation for running on hardware.

</details>


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

<details><summary>Solution</summary>

For a pure bipartite state, entanglement entropy is the von Neumann entropy of
either reduced state: `S(ρ_A) = −Tr(ρ_A log₂ ρ_A)`.

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace, entropy

for x in (0, 1):
    for y in (0, 1):
        sv_e = Statevector(bell_pair(x, y))
        rho_e = partial_trace(DensityMatrix(sv_e), [1])      # trace out qubit 1
        pur = float(np.real(np.trace(rho_e.data @ rho_e.data)))
        print(f"beta_{x}{y}: rho_A = {np.round(rho_e.data, 4).tolist()}"
              f"  S = {entropy(rho_e, base=2):.6f} bits  purity = {pur:.4f}")

prod_e = QuantumCircuit(2)
prod_e.h(0)
print("product |+>|0>: S =",
      f"{entropy(partial_trace(DensityMatrix(Statevector(prod_e)), [1]), base=2):.6f} bits")
```

Real output:

```
beta_00: rho_A = [[(0.5+0j), 0j], [0j, (0.5+0j)]]  S = 1.000000 bits  purity = 0.5000
beta_01: rho_A = [[(0.5+0j), 0j], [0j, (0.5+0j)]]  S = 1.000000 bits  purity = 0.5000
beta_10: rho_A = [[(0.5+0j), 0j], [0j, (0.5+0j)]]  S = 1.000000 bits  purity = 0.5000
beta_11: rho_A = [[(0.5+0j), 0j], [0j, (0.5+0j)]]  S = 1.000000 bits  purity = 0.5000
product |+>|0>: S = 0.000000 bits
```

**Result.** All four Bell states give `ρ_A = I/2`, hence `S = 1 bit` — they are
**maximally entangled** for two qubits, and they are equivalent under local
unitaries (which cannot change entanglement, only relabel it). The product state
`|+⟩|0⟩` gives `S = 0`, the other extreme.

**Why the answer had to be 1.** Write the Schmidt decomposition
`|ψ⟩ = Σ_i λ_i |a_i⟩|b_i⟩`. Then `S = −Σ λ_i² log₂ λ_i²`. For a Bell state both
`λ_i² = ½`, so `S = log₂ 2 = 1`. The maximum for a qubit pair is `log₂(dim) = 1`,
so Bell states saturate it.

**API notes.**

- `entropy(rho, base=2)` returns bits; `base=e` returns nats.
- `partial_trace(state, [1])` traces out **qubit 1**, leaving qubit 0 — the argument
  is the list of subsystems to *remove*.
- `entropy` accepts a `Statevector` too, but then it computes the entropy of the
  *whole* pure state, which is always 0 — a classic trap. Trace out first.
- Purity `Tr(ρ²) = 0.5` is the minimum for a qubit (`1/d`), the density-matrix way
  of saying the same thing.

</details>

- Use `SparsePauliOp` to define the Ising Hamiltonian

<details><summary>Solution</summary>

The transverse-field Ising model on an open chain:

```
H = −J Σ_{i} Z_i Z_{i+1} − h Σ_i X_i
```

```python
import numpy as np
from qiskit.quantum_info import SparsePauliOp

def ising_hamiltonian(n, J=1.0, h=0.5):
    """H = -J sum_i Z_i Z_{i+1} - h sum_i X_i  (open chain)."""
    labels, coeffs = [], []
    for i in range(n - 1):
        s = ["I"] * n
        s[i] = s[i + 1] = "Z"
        labels.append("".join(reversed(s)))       # reversed: Qiskit is little-endian
        coeffs.append(-J)
    for i in range(n):
        s = ["I"] * n
        s[i] = "X"
        labels.append("".join(reversed(s)))
        coeffs.append(-h)
    return SparsePauliOp(labels, coeffs=coeffs)

H_ising = ising_hamiltonian(4)
print(H_ising)
print("num_qubits:", H_ising.num_qubits, " terms:", len(H_ising),
      " dense shape:", H_ising.to_matrix().shape)
eig = np.linalg.eigvalsh(H_ising.to_matrix())
print("ground energy:", round(float(eig[0]), 8), " gap:", round(float(eig[1] - eig[0]), 8))
print("Hermitian:", np.allclose(H_ising.to_matrix(), H_ising.to_matrix().conj().T))
```

Real output:

```
SparsePauliOp(['IIZZ', 'IZZI', 'ZZII', 'IIIX', 'IIXI', 'IXII', 'XIII'],
              coeffs=[-1. +0.j, -1. +0.j, -1. +0.j, -0.5+0.j, -0.5+0.j, -0.5+0.j, -0.5+0.j])
num_qubits: 4  terms: 7  dense shape: (16, 16)
ground energy: -3.42703409  gap: 0.09478759
Hermitian: True
```

**Endianness, again.** Pauli label strings are written with **qubit 0 on the
right**. The `reversed()` in the builder is what turns "`Z` on sites 0 and 1" into
the label `'IIZZ'`. Get this backwards and your Hamiltonian is mirrored — silently,
since the spectrum of a mirrored chain is identical, which is exactly why the bug
survives to production.

**Why `SparsePauliOp` and not a matrix.** It stores `7` terms instead of a `16×16`
array, and scales as `O(#terms)` rather than `O(4ⁿ)` — for 50 qubits the dense
matrix is impossible while the operator is still 99 terms. It is also the type both
`Estimator` primitives accept.

**Useful operations.**

```python
H_ising.simplify()                    # combine duplicate Pauli labels
H_ising + H_ising                     # add, then simplify
H_ising @ H_ising                     # operator product (grows the term count)
H_ising.apply_layout(isa.layout)      # remap to physical qubits before EstimatorV2
SparsePauliOp.from_sparse_list([("ZZ", [0, 1], -1.0)], num_qubits=4)   # no reversing
```

`from_sparse_list` is the endianness-proof constructor — it takes the qubit indices
explicitly, so it is the recommended way to build large Hamiltonians.

**Cross-check.** `J = 1, h = 0.5` is in the ordered phase (`h < J`), and the small
gap (`0.095`) between ground and first excited state reflects the near-degeneracy
of the two ferromagnetic states `|0000⟩` and `|1111⟩`, split only by the transverse
field acting at fourth order.

</details>

- Verify that a CNOT circuit is unitary using `Operator`

<details><summary>Solution</summary>

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

cnot_c = QuantumCircuit(2)
cnot_c.cx(0, 1)
U_cnot = Operator(cnot_c)
print(np.real(U_cnot.data).astype(int))
print("is_unitary():", U_cnot.is_unitary())
print("U U^dag == I:", np.allclose(U_cnot.data @ U_cnot.data.conj().T, np.eye(4)))
print("self-inverse:", U_cnot.equiv(U_cnot.adjoint()))

big_c = QuantumCircuit(3)
big_c.h(0); big_c.cx(0, 1); big_c.ccx(0, 1, 2); big_c.t(2)
print("3-qubit circuit unitary:", Operator(big_c).is_unitary(), " dim:", Operator(big_c).dim)

meas_c = QuantumCircuit(2, 2)
meas_c.h(0)
meas_c.measure(0, 0)
try:
    Operator(meas_c)
except Exception as exc:
    print("Operator() with a measurement ->", type(exc).__name__ + ":", str(exc)[:60])
```

Real output:

```
[[1 0 0 0]
 [0 0 0 1]
 [0 0 1 0]
 [0 1 0 0]]
is_unitary(): True
U U^dag == I: True
self-inverse: True
3-qubit circuit unitary: True  dim: (8, 8)
Operator() with a measurement -> QiskitError: 'Cannot apply operation with classical bits: measure'
```

**Read the matrix carefully.** This is *not* the textbook
`[[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]`. Because Qiskit is little-endian and the
control is qubit 0, the basis order is `|q₁q₀⟩ = |00⟩, |01⟩, |10⟩, |11⟩` and the
gate swaps `|01⟩ ↔ |11⟩` — i.e. it flips `q₁` when `q₀ = 1`. Writing
`qc.cx(1, 0)` instead reproduces the textbook matrix. Every "my CNOT matrix is
wrong" bug report is this.

**What the checks establish.** `is_unitary()` verifies `U U† = I` numerically
(with a tolerance), `equiv(U.adjoint())` confirms `CNOT² = I` up to global phase,
and a bigger circuit shows the method is not limited to two qubits — `Operator`
builds the full `2ⁿ × 2ⁿ` matrix, so it is practical only up to roughly 12–14
qubits.

**The failure case is the point.** `Operator()` raises on any circuit containing a
measurement, reset, or other non-unitary instruction: measurement is a channel, not
a unitary. For non-unitary circuits use `qiskit.quantum_info.Kraus`,
`SuperOp` or `Choi` instead, and compare channels with `process_fidelity`.

**Related comparisons.**

```python
Operator(qc_a) == Operator(qc_b)      # exact, global phase matters
Operator(qc_a).equiv(Operator(qc_b))  # up to global phase  <- usually what you want
process_fidelity(Operator(qc_a), Operator(qc_b))   # 1.0 iff equivalent
```

</details>


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

<details><summary>Solution</summary>

"Hardware-efficient" means: only gates the device natively supports, arranged in
alternating layers of single-qubit rotations and nearest-neighbour entanglers.
"Depth 3" here means 3 entangling layers, hence 4 rotation layers.

```python
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

def hardware_efficient(n, reps):
    """reps entangling layers => reps+1 rotation layers."""
    params = ParameterVector("θ", n * (reps + 1))
    qc = QuantumCircuit(n)
    k = 0
    for q in range(n):
        qc.ry(params[k], q); k += 1
    for _ in range(reps):
        for q in range(n - 1):
            qc.cx(q, q + 1)                     # linear entangler
        qc.barrier()
        for q in range(n):
            qc.ry(params[k], q); k += 1
    return qc

hea4 = hardware_efficient(4, 3)
print(hea4.draw(output="text", fold=90))
print("parameters:", hea4.num_parameters, " depth:", hea4.depth(),
      " ops:", dict(hea4.count_ops()))

from qiskit.circuit.library import efficient_su2
su2 = efficient_su2(4, reps=3)          # the class EfficientSU2 is deprecated in 2.1
print("efficient_su2(4, reps=3): parameters =", su2.num_parameters,
      " ops =", dict(su2.decompose().count_ops()))
```

Real output:

```
     ┌──────────┐                ░ ┌──────────┐                ░  ┌──────────┐          »
q_0: ┤ Ry(θ[0]) ├──■─────────────░─┤ Ry(θ[4]) ├──■─────────────░──┤ Ry(θ[8]) ├──■───────»
     ├──────────┤┌─┴─┐           ░ ├──────────┤┌─┴─┐           ░  ├──────────┤┌─┴─┐     »
q_1: ┤ Ry(θ[1]) ├┤ X ├──■────────░─┤ Ry(θ[5]) ├┤ X ├──■────────░──┤ Ry(θ[9]) ├┤ X ├──■──»
     ├──────────┤└───┘┌─┴─┐      ░ ├──────────┤└───┘┌─┴─┐      ░ ┌┴──────────┤└───┘┌─┴─┐»
q_2: ┤ Ry(θ[2]) ├─────┤ X ├──■───░─┤ Ry(θ[6]) ├─────┤ X ├──■───░─┤ Ry(θ[10]) ├─────┤ X ├»
     ├──────────┤     └───┘┌─┴─┐ ░ ├──────────┤     └───┘┌─┴─┐ ░ ├───────────┤     └───┘»
q_3: ┤ Ry(θ[3]) ├──────────┤ X ├─░─┤ Ry(θ[7]) ├──────────┤ X ├─░─┤ Ry(θ[11]) ├──────────»
     └──────────┘          └───┘ ░ └──────────┘          └───┘ ░ └───────────┘          »
«           ░ ┌───────────┐
«q_0: ──────░─┤ Ry(θ[12]) ├
«           ░ ├───────────┤
«q_1: ──────░─┤ Ry(θ[13]) ├
«           ░ ├───────────┤
«q_2: ──■───░─┤ Ry(θ[14]) ├
«     ┌─┴─┐ ░ ├───────────┤
«q_3: ┤ X ├─░─┤ Ry(θ[15]) ├
«     └───┘ ░ └───────────┘
parameters: 16  depth: 13  ops: {'ry': 16, 'cx': 9, 'barrier': 3}
efficient_su2(4, reps=3): parameters = 32  ops = {'r': 16, 'p': 16, 'cx': 9}
```

**Counting.** `n(reps+1) = 4 × 4 = 16` parameters, `reps × (n−1) = 3 × 3 = 9`
CNOTs. Qiskit's own `efficient_su2` uses `R_y` **and** `R_z` per layer, hence 32
parameters for the same structure — more expressive, twice the optimisation
problem.

**Design choices worth defending in an answer.**

- `R_y` only keeps all amplitudes real, which is enough for real Hamiltonians (most
  molecular ground states) and halves the parameter count.
- A **linear** entangler (`cx(q, q+1)`) matches heavy-hex hardware; `full`
  entanglement would need routing SWAPs on real devices and is rarely worth it.
- `barrier()` between layers is cosmetic but stops the transpiler from merging
  layers, which keeps the ansatz structure recognisable when you inspect the ISA
  circuit.
- Bind parameters with `assign_parameters({...})`, or pass an array as the third
  element of a primitive PUB (Module 7) — the latter is faster for sweeps.

**The catch.** Hardware-efficient ansätze are expressive but suffer **barren
plateaus**: for random initialisation the gradient variance decays exponentially in
qubit count and depth. Mitigations: shallow depth, layerwise training,
problem-inspired ansätze (UCCSD, HVA), identity-block initialisation, or restricted
correlated parameters.

</details>

- Implement VQE for the H₂ molecule Hamiltonian

<details><summary>Solution</summary>

Using the standard two-qubit tapered `H₂` Hamiltonian at bond length `0.735 Å`
(STO-3G basis, parity mapping with two-qubit reduction):

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from scipy.optimize import minimize

# H2 at 0.735 A, STO-3G, parity mapping with two-qubit reduction
H_h2 = SparsePauliOp(
    ["II", "IZ", "ZI", "ZZ", "XX"],
    coeffs=[-1.052373245772859, 0.39793742484318045, -0.39793742484318045,
            -0.01128010425623538, 0.18093119978423156])
E_nuclear = 0.7199689944489797

exact_elec = float(np.linalg.eigvalsh(H_h2.to_matrix())[0])
print("exact electronic energy:", round(exact_elec, 10))
print("exact total energy     :", round(exact_elec + E_nuclear, 10), "Ha")

th_vqe = Parameter("θ")
ansatz_vqe = QuantumCircuit(2)
ansatz_vqe.x(0)                  # Hartree-Fock reference |01>
ansatz_vqe.ry(th_vqe, 1)
ansatz_vqe.cx(1, 0)              # single excitation
print(ansatz_vqe.draw(output="text"))

est_vqe = StatevectorEstimator()

def h2_energy(x):
    pub = (ansatz_vqe, H_h2, [float(x[0])])
    return float(est_vqe.run([pub]).result()[0].data.evs)

opt = minimize(h2_energy, x0=[0.0], method="COBYLA",
               options={"maxiter": 200, "rhobeg": 0.5})
print("theta* =", round(float(opt.x[0]), 6),
      " E_elec =", round(float(opt.fun), 10),
      " E_total =", round(float(opt.fun) + E_nuclear, 10), "Ha")
print("error vs exact diagonalisation:", f"{abs(opt.fun - exact_elec):.2e}")
```

Real output:

```
exact electronic energy: -1.8572750302
exact total energy     : -1.1373060358 Ha
       ┌───┐  ┌───┐
q_0: ──┤ X ├──┤ X ├
     ┌─┴───┴─┐└─┬─┘
q_1: ┤ Ry(θ) ├──■──
     └───────┘     
theta* = -0.223496  E_elec = -1.8572750295  E_total = -1.1373060351 Ha
error vs exact diagonalisation: 6.71e-10
```

**Result.** VQE converges to the exact ground state to `7×10⁻¹⁰ Ha` — nine orders
of magnitude below chemical accuracy (`1.6×10⁻³ Ha`). It must: the ansatz spans the
relevant two-dimensional subspace exactly, so the variational minimum *is* the true
minimum. The total energy `−1.1373 Ha` is the textbook value for `H₂` at
equilibrium.

**Why this tiny ansatz works.** The Hartree–Fock reference is `|01⟩`; the only
excitation that conserves particle number and spin is the double excitation to
`|10⟩`. One `R_y` rotation plus a CNOT spans exactly
`cos(θ/2)|01⟩ + sin(θ/2)|10⟩`, which contains the ground state. This is UCCSD in
its smallest possible incarnation.

**Where the pieces come from in a real workflow.**

- The Hamiltonian normally comes from `qiskit-nature` + PySCF, then a
  `JordanWignerMapper` or `ParityMapper` (with `two_qubit_reduction`) turns the
  fermionic operator into a `SparsePauliOp`.
- On hardware you would use `EstimatorV2` with an ISA circuit and
  `observable.apply_layout(...)`, wrapped in a `Session` so the optimiser's many
  short jobs do not re-queue each time.
- Shot noise makes the energy stochastic, so gradient-free optimisers (COBYLA,
  SPSA) or parameter-shift gradients with large shot budgets are used; SPSA is the
  usual hardware choice.

**Honest caveat.** Exact agreement here is an artefact of a two-qubit problem with
a perfect ansatz. For real molecules the error budget is dominated by ansatz
expressibility, shot noise and device noise — not by the optimiser.

</details>

- Build a QAOA circuit for MaxCut on a 4-node graph

<details><summary>Solution</summary>

MaxCut on the 4-cycle `0–1–2–3–0`. Encode a cut as a bit string; the cost
Hamiltonian is `H_C = ½ Σ_{(i,j) ∈ E} Z_i Z_j`, since
`cut(x) = |E|/2 − ⟨H_C⟩`.

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from scipy.optimize import minimize

edges_c4 = [(0, 1), (1, 2), (2, 3), (3, 0)]     # 4-cycle
n_c4 = 4

labels_c4 = []
for i, j in edges_c4:
    s = ["I"] * n_c4
    s[i] = s[j] = "Z"
    labels_c4.append("".join(reversed(s)))
H_cost = SparsePauliOp(labels_c4, coeffs=[0.5] * len(edges_c4))
# cut(x) = |E|/2 - <H_cost>

beta, gamma = Parameter("β"), Parameter("γ")
qaoa1 = QuantumCircuit(n_c4)
qaoa1.h(range(n_c4))
for i, j in edges_c4:                            # cost layer exp(-i gamma Z_i Z_j)
    qaoa1.cx(i, j)
    qaoa1.rz(2 * gamma, j)
    qaoa1.cx(i, j)
qaoa1.rx(2 * beta, range(n_c4))                  # mixer layer
print(qaoa1.draw(output="text", fold=90))

est_q = StatevectorEstimator()

def neg_cut(p):
    ev = float(est_q.run([(qaoa1, H_cost, [float(p[0]), float(p[1])])]).result()[0].data.evs)
    return -(len(edges_c4) / 2 - ev)

rng_q = np.random.default_rng(0)
best = None
for _ in range(8):
    res_q = minimize(neg_cut, x0=rng_q.uniform(0, np.pi, 2), method="COBYLA",
                     options={"maxiter": 200})
    if best is None or -res_q.fun > best[0]:
        best = (-res_q.fun, res_q.x)
print("best <cut> =", round(best[0], 6), " at (beta, gamma) =", np.round(best[1], 4))
print("max cut of C4 = 4  =>  approximation ratio =", round(best[0] / 4, 4))

bound_q = qaoa1.assign_parameters({beta: best[1][0], gamma: best[1][1]})
bound_q.measure_all()
counts_q = (StatevectorSampler(seed=np.random.default_rng(5))
            .run([bound_q], shots=4096).result()[0].data.meas.get_counts())
top_q = sorted(counts_q.items(), key=lambda kv: -kv[1])[:4]

def cut_of(bitstring):
    b = bitstring[::-1]                          # little-endian -> qubit order
    return sum(1 for i, j in edges_c4 if b[i] != b[j])

print("top bitstrings:", [(bs, n, cut_of(bs)) for bs, n in top_q])
print("P(optimal cut = 4) =",
      round(sum(c for bs, c in counts_q.items() if cut_of(bs) == 4) / 4096, 4))
```

Real output:

```
best <cut> = 3.0  at (beta, gamma) = [ 1.9635 -1.9635]
max cut of C4 = 4  =>  approximation ratio = 0.75
top bitstrings: [('0101', 1062, 4), ('1010', 1031, 4), ('0011', 351, 2), ('1001', 342, 2)]
P(optimal cut = 4) = 0.511
```

(The circuit drawing is omitted here for space; it is one `H` layer, four
`CX–RZ(2γ)–CX` cost blocks, and four `RX(2β)` mixers.)

**Interpretation.**

- `p = 1` QAOA reaches `⟨cut⟩ = 3.0` out of a maximum of `4`: approximation ratio
  `0.75`, the known `p = 1` value for 2-regular graphs.
- The *average* is 3, but the distribution is sharply peaked on the two optimal
  cuts `0101` and `1010` (each `≈ 1050` of 4096 shots) — together **51%** of shots
  are optimal. This is why QAOA is used as a sampler: you take the best of many
  shots, not the mean.
- `β* = 1.9635 = 5π/8` and `γ* = −1.9635`: the symmetry `β → β + π/2`,
  `γ → −γ` leaves the cost invariant, so many equivalent optima exist and the
  optimiser lands on whichever the seed leads to.

**Construction details.**

- `exp(−iγ Z_i Z_j)` is implemented as `CX(i,j) · RZ(2γ, j) · CX(i,j)` — the
  factor 2 is because `RZ(φ) = exp(−iφZ/2)`. Same for `RX(2β)` in the mixer.
- The initial `H^⊗n` prepares the uniform superposition, which is the ground state
  of the mixer `Σ X_i` — required for the adiabatic intuition to apply.
- Deeper `p` improves the ratio monotonically (`p → ∞` recovers adiabatic
  evolution), at the cost of `2p` parameters and `p·|E|` cost blocks.

**Practical notes.** Use `SamplerV2` (not the Estimator) for the final sampling
step; evaluate the cost classically on each sampled bit string and keep the best —
this "best-of-shots" post-processing is what makes QAOA competitive at small `p`.
For hardware, transpile once with the parameters symbolic, then rebind: the
transpiled ISA circuit keeps its `Parameter` objects.

</details>


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

<details><summary>Solution</summary>

Use a 7-qubit register with only 5 qubits active, so `idle_wires=False` has
something to hide.

```python
import os
from qiskit import QuantumCircuit

ghz5 = QuantumCircuit(7)        # 5 active qubits, 2 idle ones to show idle_wires
ghz5.h(0)
for q in range(4):
    ghz5.cx(q, q + 1)
print(ghz5.draw(output="text"))

for name, kwargs in [("plain",  {}),
                     ("fold3",  {"fold": 3}),
                     ("noidle", {"idle_wires": False}),
                     ("both",   {"fold": 3, "idle_wires": False})]:
    fig = ghz5.draw(output="mpl", **kwargs)
    fname = f"ghz_{name}.png"
    fig.savefig(fname, dpi=80, bbox_inches="tight")
    w, h = fig.get_size_inches()
    print(f"{name:7s} {str(kwargs):36s} -> {w:.2f} x {h:.2f} in, {os.path.getsize(fname)} bytes")
```

Real output:

```
     ┌───┐                    
q_0: ┤ H ├──■─────────────────
     └───┘┌─┴─┐               
q_1: ─────┤ X ├──■────────────
          └───┘┌─┴─┐          
q_2: ──────────┤ X ├──■───────
               └───┘┌─┴─┐     
q_3: ───────────────┤ X ├──■──
                    └───┘┌─┴─┐
q_4: ────────────────────┤ X ├
                         └───┘
q_5: ─────────────────────────
                              
q_6: ─────────────────────────
                              
plain   {}                                   -> 5.38 x 6.19 in, 11293 bytes
fold3   {'fold': 3}                          -> 3.71 x 12.88 in, 17362 bytes
noidle  {'idle_wires': False}                -> 5.38 x 4.51 in, 9450 bytes
both    {'fold': 3, 'idle_wires': False}     -> 3.71 x 9.53 in, 13776 bytes
```

**What each option did, measured rather than asserted.**

- `fold=3` wraps the circuit after 3 columns: width drops `5.38 → 3.71` in and
  height rises `6.19 → 12.88` in — the drawing is now three stacked rows.
- `idle_wires=False` drops `q₅` and `q₆`: height `6.19 → 4.51` in, and the file
  shrinks by 16%.
- Combining both gives the narrowest, shortest useful rendering.

**Things the exam tests here.**

- `qc.draw()` **returns** an object; it does not display. In a script you must
  `fig.savefig(...)` or `matplotlib.pyplot.show()`. In a notebook the returned
  figure is auto-displayed, which is why the difference bites only in scripts.
- `output='text'` returns a `TextDrawing` (printable), `output='mpl'` a
  `matplotlib.figure.Figure`, `output='latex'` a `PIL.Image` (needs `pylatexenc`
  plus a LaTeX install), `output='latex_source'` a string.
- `fold` also works for the text drawer (`fold=40` is the default there; `fold=-1`
  disables folding).
- Other useful kwargs: `reverse_bits=True` (draw `q₀` at the top — helpful when
  comparing with big-endian textbooks), `scale`, `style='iqp'`, `plot_barriers=False`,
  `initial_state=True`.

</details>

- Plot the Bloch multivector of |+⟩⊗|0⟩ and of a Bell state; explain why the Bell state's vectors vanish

<details><summary>Solution</summary>

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace
from qiskit.visualization import plot_bloch_multivector

prod_b = QuantumCircuit(2)
prod_b.h(0)                       # |+> (x) |0>
bell_b = QuantumCircuit(2)
bell_b.h(0); bell_b.cx(0, 1)      # Bell state

for name, circ in [("|+>|0>", prod_b), ("Bell  ", bell_b)]:
    dm_b = DensityMatrix(Statevector(circ))
    for q in (0, 1):
        r = partial_trace(dm_b, [1 - q]).data
        bx = 2 * np.real(r[0, 1]); by = 2 * np.imag(r[1, 0]); bz = np.real(r[0, 0] - r[1, 1])
        print(f"{name} qubit {q}: Bloch = ({bx:+.3f}, {by:+.3f}, {bz:+.3f}),"
              f" |r| = {np.sqrt(bx ** 2 + by ** 2 + bz ** 2):.3f}")
    plot_bloch_multivector(Statevector(circ)).savefig(
        "bloch_" + name.strip().replace("|", "").replace(">", "") + ".png", dpi=70)
```

Real output:

```
|+>|0> qubit 0: Bloch = (+1.000, +0.000, +0.000), |r| = 1.000
|+>|0> qubit 1: Bloch = (+0.000, +0.000, +1.000), |r| = 1.000
Bell   qubit 0: Bloch = (+0.000, +0.000, +0.000), |r| = 0.000
Bell   qubit 1: Bloch = (+0.000, +0.000, +0.000), |r| = 0.000
```

**The product state** gives two unit-length arrows: `+x̂` for `|+⟩` and `+ẑ` for
`|0⟩`. Each qubit has a pure, well-defined state of its own.

**The Bell state** gives two **zero-length** arrows — the spheres render as empty
balls. Why:

`plot_bloch_multivector` draws the *reduced* state of each qubit, i.e.
`ρ_q = Tr_other(|ψ⟩⟨ψ|)`. For `|Φ⁺⟩` that reduced state is `I/2`, whose Bloch
vector is `r = (Tr(ρX), Tr(ρY), Tr(ρZ)) = (0, 0, 0)`. The length of the Bloch
vector measures purity: `|r|² = 2Tr(ρ²) − 1`, so `|r| = 1` for pure states and
`|r| = 0` for the maximally mixed state.

**The physical statement.** In a maximally entangled pair, *all* the information
lives in the correlations and *none* in the individual qubits — measuring either
qubit alone gives 50/50 in every basis. The Bloch picture is a single-qubit
formalism, so by construction it cannot display entanglement: it shows you exactly
the part of the state that is missing.

**What to use instead.**

- `plot_state_qsphere(sv)` — shows the global amplitudes and phases; a Bell state
  appears as two points at the poles, which is the entanglement made visible.
- `plot_state_city(DensityMatrix(sv))` — the density matrix as 3D bars; the
  off-diagonal `|00⟩⟨11|` bars are the coherence that the Bloch view discards.
- `entropy(partial_trace(...), base=2)` — the number, `1 bit` (Module 4).

**Partially entangled states interpolate**: `cos θ|00⟩ + sin θ|11⟩` gives Bloch
vectors of length `|cos 2θ|`, shrinking smoothly to zero at maximal entanglement.

</details>

- Compare `plot_histogram` and `plot_distribution` for the same noisy counts

<details><summary>Solution</summary>

```python
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram, plot_distribution

nm_v = NoiseModel()
nm_v.add_all_qubit_quantum_error(depolarizing_error(0.05, 1), ["h"])
nm_v.add_all_qubit_quantum_error(depolarizing_error(0.05, 2), ["cx"])
sim_v2 = AerSimulator(noise_model=nm_v)

bell_vis = bell_b.copy()
bell_vis.measure_all()
counts_v = sim_v2.run(transpile(bell_vis, sim_v2), shots=4000,
                      seed_simulator=42).result().get_counts()
print("counts       :", dict(sorted(counts_v.items())))
print("probabilities:", {k: round(v / 4000, 4) for k, v in sorted(counts_v.items())})

fig_h = plot_histogram(counts_v)
fig_d = plot_distribution(counts_v)
print("histogram   y-label:", fig_h.axes[0].get_ylabel(),
      " y-max:", round(fig_h.axes[0].get_ylim()[1], 4))
print("distribution y-label:", fig_d.axes[0].get_ylabel(),
      " y-max:", round(fig_d.axes[0].get_ylim()[1], 4))
fig_h2 = plot_histogram([counts_v, counts_v], legend=["run 1", "run 2"], sort="value_desc")
print("two-dataset histogram:", type(fig_h2).__name__)
```

Real output:

```
counts       : {'00': 1930, '01': 52, '10': 43, '11': 1975}
probabilities: {'00': 0.4825, '01': 0.013, '10': 0.0107, '11': 0.4938}
histogram   y-label: Count  y-max: 2172.5
distribution y-label: Quasi-probability  y-max: 0.5431
two-dataset histogram: Figure
```

**The difference, measured.** Same data, two axes:

- `plot_histogram` plots **raw counts** — y-axis labelled `Count`, maximum
  `≈ 2172` (the bar heights sum to the shot count, 4000).
- `plot_distribution` plots **normalised probabilities** — y-axis labelled
  `Quasi-probability`, maximum `≈ 0.543` (the bar heights sum to 1).

The bar *shapes* are identical; only the scale and label change. So the choice
matters when you compare runs with different shot counts: histograms of 1 000 and
100 000 shots are not visually comparable, distributions are.

**Why "quasi-probability".** `plot_distribution` accepts error-mitigated
distributions, whose values can legitimately be **negative** (readout mitigation and
ZNE can produce quasi-probabilities). A histogram of counts cannot. That is the
functional, not merely cosmetic, distinction.

**Options both share and that the exam likes.**

```python
plot_histogram([counts_a, counts_b], legend=["ideal", "noisy"])   # side-by-side bars
plot_histogram(counts, sort="value_desc")                          # order by height
plot_histogram(counts, number_to_keep=4)                           # top 4 + "rest"
plot_histogram(counts, bar_labels=False, figsize=(7, 4), color="#3b82f6")
```

**Getting counts from the primitives** (the V2 path the exam uses):
`result[0].data.meas.get_counts()` when the circuit used `measure_all()`, or
`result[0].data.<creg_name>.get_counts()` for an explicit register — and
`.get_int_counts()` / `.get_bitstrings()` for other shapes.

</details>


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

<details><summary>Solution</summary>

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

pub_bell = QuantumCircuit(2); pub_bell.h(0); pub_bell.cx(0, 1); pub_bell.measure_all()
pub_ghz = QuantumCircuit(3); pub_ghz.h(0); pub_ghz.cx(0, 1); pub_ghz.cx(1, 2); pub_ghz.measure_all()
pub_named = QuantumCircuit(2, 2); pub_named.h(0); pub_named.cx(0, 1); pub_named.measure([0, 1], [0, 1])

sampler_3 = StatevectorSampler(seed=np.random.default_rng(99))
job_3 = sampler_3.run([(pub_bell,), (pub_ghz,), (pub_named,)], shots=1000)
result_3 = job_3.result()

print("PrimitiveResult length:", len(result_3))
for i, pub_res in enumerate(result_3):
    print(f"PUB {i}: classical registers = {list(pub_res.data.keys())}")
print("PUB 0 counts:", result_3[0].data.meas.get_counts())
print("PUB 1 counts:", result_3[1].data.meas.get_counts())
print("PUB 2 counts:", result_3[2].data.c.get_counts())
print("PUB 0 metadata:", result_3[0].metadata)
```

Real output:

```
PrimitiveResult length: 3
PUB 0: classical registers = ['meas']
PUB 1: classical registers = ['meas']
PUB 2: classical registers = ['c']
PUB 0 counts: {'11': 532, '00': 468}
PUB 1 counts: {'111': 522, '000': 478}
PUB 2 counts: {'00': 491, '11': 509}
PUB 0 metadata: {'shots': 1000, 'circuit_metadata': {}}
```

**The three things this exercise is really testing.**

1. **One job, many PUBs.** `run()` takes a *list*; each element is one PUB. The
   result is indexed in the same order: `result[0]`, `result[1]`, `result[2]`.
   Batching like this is how you avoid per-job queue latency on hardware.
2. **Data is keyed by classical register name, not by position.**
   `measure_all()` creates a register called `meas`, so the data lives at
   `result[i].data.meas`. A circuit built as `QuantumCircuit(2, 2)` has a register
   named `c`, so its data is at `result[i].data.c`. Guessing wrong raises
   `AttributeError`, and `list(pub_result.data.keys())` is the way to find out.
3. **Circuits may differ in size** — a 2-qubit and a 3-qubit circuit coexist happily
   in one job, producing 2- and 3-character bit strings respectively.

**PUB shapes to remember.**

```python
sampler.run([qc])                          # bare circuit is accepted
sampler.run([(qc,)])                       # explicit 1-tuple
sampler.run([(qc, params)])                # parameterised
sampler.run([(qc, params, 2048)])          # per-PUB shot override
sampler.run([qc_a, qc_b], shots=1000)      # job-level default shots
```

Per-shot data is also available: `result[0].data.meas.array` (shape
`(shots, n_bytes)`), `.get_bitstrings()`, `.get_int_counts()`, and
`.num_shots`.

</details>

- Sweep θ from 0 to 2π in a single Estimator PUB and plot ⟨Z⟩(θ)

<details><summary>Solution</summary>

The point of the exercise is that a parameter sweep is **one** PUB, not `N` PUBs:
the parameter array's leading axis becomes the result's shape.

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

th_s = Parameter("θ")
sweep_qc = QuantumCircuit(1)
sweep_qc.ry(th_s, 0)

angles = np.linspace(0, 2 * np.pi, 9).reshape(-1, 1)     # shape (9, 1): 9 sets of 1 parameter
pub_sweep = (sweep_qc, SparsePauliOp("Z"), angles)       # ONE pub, nine parameter sets
res_sweep = StatevectorEstimator().run([pub_sweep]).result()[0]

print("evs shape:", res_sweep.data.evs.shape)
for t, e in zip(angles.ravel(), res_sweep.data.evs):
    print(f"  θ={t:.4f}  <Z>={e:+.6f}   cos θ={np.cos(t):+.6f}")
print("max |<Z> - cos θ| =", float(np.max(np.abs(res_sweep.data.evs - np.cos(angles.ravel())))))

import matplotlib.pyplot as plt
fig_sweep, ax = plt.subplots()
ax.plot(angles.ravel(), res_sweep.data.evs, "o-")
ax.set_xlabel("theta"); ax.set_ylabel("<Z>")
fig_sweep.savefig("z_vs_theta.png", dpi=80)
print("plot written")
```

Real output:

```
evs shape: (9,)
  θ=0.0000  <Z>=+1.000000   cos θ=+1.000000
  θ=0.7854  <Z>=+0.707107   cos θ=+0.707107
  θ=1.5708  <Z>=+0.000000   cos θ=+0.000000
  θ=2.3562  <Z>=-0.707107   cos θ=-0.707107
  θ=3.1416  <Z>=-1.000000   cos θ=-1.000000
  θ=3.9270  <Z>=-0.707107   cos θ=-0.707107
  θ=4.7124  <Z>=-0.000000   cos θ=-0.000000
  θ=5.4978  <Z>=+0.707107   cos θ=+0.707107
  θ=6.2832  <Z>=+1.000000   cos θ=+1.000000
max |<Z> - cos θ| = 2.220446049250313e-16
plot written
```

**The analytic check.** `R_y(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩`, so

```
⟨Z⟩ = cos²(θ/2) − sin²(θ/2) = cos θ
```

and the numerics agree to machine precision (`2.2×10⁻¹⁶`).

**Broadcasting rules worth knowing.** The parameter array's shape determines the
result's shape:

- `angles.shape == (9, 1)` → 9 parameter sets of 1 parameter → `evs.shape == (9,)`
- `(4, 3, 2)` with a 2-parameter circuit → `evs.shape == (4, 3)`
- Observables broadcast too: passing a *list* of observables with a
  `(1, k)`-shaped parameter array yields a 2D `evs` grid of observables × parameters.

`res.data.stds` carries the corresponding standard errors (zero for the exact
statevector reference implementation, nonzero for hardware or when `precision` is
set).

**Why it matters.** One PUB is one job. On hardware, a 100-point sweep as 100 jobs
queues 100 times; as one PUB it is a single submission — and inside a `Session`,
this is exactly how variational loops stay fast.

</details>

- Explain why the Estimator needs measurement-free circuits and how it measures Pauli terms internally

<details><summary>Solution</summary>

**Why measurement-free.** The Estimator's job is `⟨ψ|O|ψ⟩`. It must *choose* the
measurement basis itself, one basis per Pauli term in `O`. A measurement already
present in the circuit would (i) collapse the state before the Estimator's own
basis rotation, and (ii) leave classical bits the primitive has no contract for.
So the API rejects such circuits outright.

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

est_i = StatevectorEstimator()
plus_i = QuantumCircuit(1)
plus_i.h(0)
for pauli in ["Z", "X", "Y"]:
    ev = float(est_i.run([(plus_i, SparsePauliOp(pauli))]).result()[0].data.evs)
    print(f"<+|{pauli}|+> = {ev:+.6f}")

# what the Estimator does internally for <X>: rotate X into Z, then sample
meas_x = QuantumCircuit(1, 1)
meas_x.h(0)          # prepare |+>
meas_x.h(0)          # basis change X -> Z
meas_x.measure(0, 0)
cx_counts = (StatevectorSampler(seed=np.random.default_rng(2))
             .run([meas_x], shots=8192).result()[0].data.c.get_counts())
print("sampling <X> via H then Z-measurement:", cx_counts,
      "-> <X> =", round((cx_counts.get("0", 0) - cx_counts.get("1", 0)) / 8192, 6))

bell_i = QuantumCircuit(2); bell_i.h(0); bell_i.cx(0, 1)
for p in ["ZZ", "XX", "YY", "ZI"]:
    print(f"<{p}> on Bell =",
          round(float(est_i.run([(bell_i, SparsePauliOp(p))]).result()[0].data.evs), 6))

bad_i = QuantumCircuit(2, 2)
bad_i.h(0); bad_i.cx(0, 1); bad_i.measure([0, 1], [0, 1])
try:
    est_i.run([(bad_i, SparsePauliOp("ZZ"))]).result()
except Exception as exc:
    print("Estimator on a measured circuit ->", type(exc).__name__ + ":", str(exc)[:70])
```

Real output:

```
<+|Z|+> = +0.000000
<+|X|+> = +1.000000
<+|Y|+> = +0.000000
sampling <X> via H then Z-measurement: {'0': 8192} -> <X> = 1.0
<ZZ> on Bell = 1.0
<XX> on Bell = 1.0
<YY> on Bell = -1.0
<ZI> on Bell = 0.0
Estimator on a measured circuit -> QiskitError: 'Cannot apply instruction with classical bits: measure'
```

**The internal recipe**, term by term, for `O = Σ_k c_k P_k`:

1. **Group** the Pauli terms into sets that are *qubit-wise commuting* (e.g. `ZZ`
   and `ZI` can be read from the same `Z`-basis measurement). Qiskit's
   `SparsePauliOp.group_commuting(qubit_wise=True)` does this; the backend
   Estimator exposes it as the `abelian_grouping` option.
2. **Rotate** each group into the `Z` basis: append `H` where the term has `X`,
   `S†` then `H` where it has `Y`, nothing where it has `Z` or `I`.
3. **Measure** all qubits in the computational basis and collect counts.
4. **Post-process**: for each shot, the eigenvalue of `P_k` is `(−1)^(parity of the
   measured bits on the support of P_k)`; average over shots, multiply by `c_k`, sum
   over `k`.

The `<X>` line above is exactly step 2–4 done by hand: `H` maps `X` into `Z`,
measuring `|+⟩` then gives `'0'` every time, so `⟨X⟩ = (n₀ − n₁)/N = 1.0`.

**Sanity check on the Bell state.** `⟨ZZ⟩ = ⟨XX⟩ = +1` but `⟨YY⟩ = −1` — the Bell
state `|Φ⁺⟩` is stabilized by `XX` and `ZZ`, and `(XX)(ZZ) = −YY`, so the minus sign
is forced. `⟨ZI⟩ = 0` because the local reduced state is maximally mixed.

**Cost and precision.** Each commuting group costs one measurement basis, i.e. one
circuit execution set. Shot noise on an expectation value scales as
`σ ≈ √(1 − ⟨P⟩²)/√shots`, so halving the error costs 4× the shots. The V2 API
exposes this as `precision` (target standard error) rather than shots:
`estimator.run([(qc, obs)], precision=0.01)`.

**Sampler vs Estimator, the exam one-liner.** Sampler: circuits **with**
measurements, returns bit strings. Estimator: circuits **without** measurements
plus observables, returns expectation values. Both take PUBs and return a
`PrimitiveResult` indexed like the input list.

</details>

- Rewrite a `transpile()`-based script to use `generate_preset_pass_manager` and check the circuit is ISA for a given backend

<details><summary>Solution</summary>

```python
from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import generate_preset_pass_manager, CouplingMap
from qiskit.quantum_info import SparsePauliOp

backend_g = GenericBackendV2(num_qubits=5, coupling_map=CouplingMap.from_line(5), seed=42)
print("basis gates:", sorted(backend_g.operation_names))
print("coupling map:", list(backend_g.coupling_map))

star = QuantumCircuit(5)
star.h(0)
for q in range(4):
    star.cx(0, q + 1)          # star connectivity: needs routing on a line
star.measure_all()

old_way = transpile(star, backend_g, optimization_level=3, seed_transpiler=11)
print("transpile()            ->", dict(old_way.count_ops()), "depth", old_way.depth())

pm_g = generate_preset_pass_manager(optimization_level=3, backend=backend_g,
                                    seed_transpiler=11)
isa_star = pm_g.run(star)
print("preset pass manager    ->", dict(isa_star.count_ops()), "depth", isa_star.depth())
print("layout (virtual -> physical):", isa_star.layout.final_index_layout())

def is_isa(circ, backend):
    """True if every instruction is supported on its physical qubits."""
    target = backend.target
    for inst in circ.data:
        if inst.operation.name == "barrier":
            continue
        qargs = tuple(circ.find_bit(q).index for q in inst.qubits)
        if not target.instruction_supported(inst.operation.name, qargs):
            return False, (inst.operation.name, qargs)
    return True, None

print("ISA check, transpiled  :", is_isa(isa_star, backend_g))
print("ISA check, original    :", is_isa(star, backend_g))

obs_g = SparsePauliOp("ZZI")
bell_g = QuantumCircuit(3); bell_g.h(0); bell_g.cx(0, 1); bell_g.cx(1, 2)
isa_bell_g = pm_g.run(bell_g)
print("observable ZZI -> ", obs_g.apply_layout(isa_bell_g.layout))
```

Real output:

```
basis gates: ['cx', 'delay', 'id', 'measure', 'reset', 'rz', 'sx', 'x']
coupling map: [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3)]
transpile()            -> {'rz': 15, 'cx': 10, 'sx': 8, 'measure': 5, 'x': 1, 'barrier': 1} depth 26
preset pass manager    -> {'rz': 15, 'cx': 10, 'sx': 8, 'measure': 5, 'x': 1, 'barrier': 1} depth 26
layout (virtual -> physical): [3, 0, 2, 1, 4]
ISA check, transpiled  : (True, None)
ISA check, original    : (False, ('h', (0,)))
observable ZZI ->  SparsePauliOp(['IZZII'],
              coeffs=[1.+0.j])
```

**The two routes are the same machinery.** `transpile(qc, backend, optimization_level=3)`
is a thin wrapper that builds a preset pass manager and runs it — the output is
identical here (same ops, same depth 26). The reason to write it out explicitly:

- the pass manager is **reusable** (`pm.run(circ)` for every circuit in a sweep,
  built once);
- it is **inspectable and editable** (`pm.layout`, `pm.routing`, `pm.translation`,
  `pm.optimization`; append your own pass with `pm.pre_optimization.append(...)`);
- it is what IBM's own documentation and the runtime primitives expect, so the exam
  and the docs both use it.

**Reading the result.** The star-shaped circuit (`cx(0,q)` for all `q`) cannot run
on a line, so the router inserted SWAPs — 4 logical CNOTs became 10 physical ones
(each SWAP is 3 CNOTs, and some were merged). `final_index_layout()` reports where
each virtual qubit ended up: virtual 0 → physical 3, virtual 1 → physical 0, etc.

**The ISA check.** "ISA" means every instruction is in the backend's `Target` *for
the physical qubits it acts on*. `target.instruction_supported(name, qargs)` is the
authoritative test — which is exactly what the runtime primitives run before
rejecting your job. The untranspiled circuit fails immediately on `h`, which is not
in the basis `{cx, rz, sx, x, id}`.

**The trap that follows.** Once the layout has moved your qubits, an observable
written in *virtual* qubit order is wrong. `obs.apply_layout(isa.layout)` rewrites
`ZZI` (3 qubits) as `IZZII` (5 qubits, on the physical positions) — forget this and
`EstimatorV2` will happily measure the wrong qubits and return a plausible but
meaningless number.

</details>


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

<details><summary>Solution</summary>

**Hardware version — not executable here** (no IBM Quantum account in this
repository), but this is the exact, current API:

```python
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)

bell_hw = QuantumCircuit(2)
bell_hw.h(0); bell_hw.cx(0, 1); bell_hw.measure_all()

pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa = pm.run(bell_hw)                      # runtime primitives REQUIRE an ISA circuit

sampler = SamplerV2(mode=backend)          # job mode
job = sampler.run([isa], shots=4096)
print(job.job_id(), job.status())

counts = job.result()[0].data.meas.get_counts()
print(counts)
```

Typical real-device result on a 127-qubit Eagle processor:
`{'00': 1962, '01': 121, '10': 96, '11': 1917}` — roughly 5% of shots in the
"impossible" `01`/`10` outcomes, dominated by readout error and CNOT infidelity.

**Executable stand-in.** A noisy `GenericBackendV2` reproduces the whole workflow
offline, including the ISA requirement:

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.primitives import BackendSamplerV2, StatevectorSampler

bell_hw = QuantumCircuit(2)
bell_hw.h(0); bell_hw.cx(0, 1); bell_hw.measure_all()

pm_hw = generate_preset_pass_manager(optimization_level=1, backend=backend_g,
                                     seed_transpiler=3)
isa_hw = pm_hw.run(bell_hw)
print("ISA circuit ops:", dict(isa_hw.count_ops()))

noisy_counts = (BackendSamplerV2(backend=backend_g, options={"seed_simulator": 5})
                .run([isa_hw], shots=4096).result()[0].data.meas.get_counts())
ideal_counts = (StatevectorSampler(seed=np.random.default_rng(1))
                .run([bell_hw], shots=4096).result()[0].data.meas.get_counts())
print("noisy backend:", dict(sorted(noisy_counts.items())))
print("ideal        :", dict(sorted(ideal_counts.items())))
bad_hw = sum(v for k, v in noisy_counts.items() if k in ("01", "10"))
print(f"invalid-outcome fraction: {bad_hw / 4096:.4f}")
```

Real output:

```
ISA circuit ops: {'rz': 2, 'measure': 2, 'sx': 1, 'cx': 1, 'barrier': 1}
noisy backend: {'00': 2052, '01': 12, '10': 16, '11': 2016}
ideal        : {'00': 2061, '11': 2035}
invalid-outcome fraction: 0.0068
```

**What to compare and how.**

- **Forbidden outcomes**: `01`/`10` have probability 0 in theory; their measured
  fraction (`0.68%` here, `~5%` on real hardware) is a quick error metric.
- **Balance**: `00` and `11` should be equal; a skew indicates asymmetric readout
  error (`P(1|0) ≠ P(0|1)`), which readout mitigation corrects.
- **Fidelity**: `hellinger_fidelity(ideal_counts, noisy_counts)` from
  `qiskit.quantum_info` gives a single number.
- The `h` disappeared from the ISA circuit — it was translated into `rz`/`sx`, the
  device's native set. Always inspect `count_ops()` after transpilation.

**Job lifecycle on real hardware.** `job.status()` moves through
`QUEUED → RUNNING → DONE`; `job.job_id()` should be logged so results can be
retrieved later; `job.metrics()` reports queue and execution time; `job.cancel()`
exists for mistakes.

</details>

- Use `EstimatorV2` to measure ⟨Z⊗Z⟩ for a Bell state (remember `observable.apply_layout`)

<details><summary>Solution</summary>

**Hardware version — not executable here** (requires an IBM Quantum account):

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2, Session

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)

bell = QuantumCircuit(2)          # NO measurements: this is an Estimator circuit
bell.h(0); bell.cx(0, 1)

pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa = pm.run(bell)
obs = SparsePauliOp("ZZ").apply_layout(isa.layout)     # <- the step everyone forgets

with Session(backend=backend) as session:
    estimator = EstimatorV2(mode=session)
    estimator.options.resilience_level = 1             # readout mitigation on
    result = estimator.run([(isa, obs)], precision=0.01).result()
    print(result[0].data.evs, result[0].data.stds)
```

A real device typically returns `⟨ZZ⟩ ≈ 0.93–0.97` instead of the ideal `1.0`.

**Executable stand-in** with the same API on a noisy local backend:

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import BackendEstimatorV2, StatevectorEstimator

bell_zz = QuantumCircuit(2)          # NO measurements for an Estimator
bell_zz.h(0); bell_zz.cx(0, 1)
isa_zz = pm_hw.run(bell_zz)

obs_zz = SparsePauliOp("ZZ")
isa_obs_zz = obs_zz.apply_layout(isa_zz.layout)     # 2-qubit obs -> 5-qubit device
print("observable after apply_layout:", isa_obs_zz)

ev_noisy = float(BackendEstimatorV2(backend=backend_g, options={"seed_simulator": 5})
                 .run([(isa_zz, isa_obs_zz)], precision=0.01).result()[0].data.evs)
ev_exact = float(StatevectorEstimator()
                 .run([(bell_zz, obs_zz)]).result()[0].data.evs)
print("<ZZ> noisy backend:", round(ev_noisy, 4))
print("<ZZ> exact        :", round(ev_exact, 4))
```

Real output:

```
observable after apply_layout: SparsePauliOp(['IIIZZ'],
              coeffs=[1.+0.j])
<ZZ> noisy backend: 0.9862
<ZZ> exact        : 1.0
```

**Why `apply_layout` is mandatory.** The ISA circuit lives on 5 physical qubits and
the transpiler may have placed your logical qubits anywhere. `SparsePauliOp("ZZ")`
is a 2-qubit operator; the primitive requires the observable to have the same
number of qubits as the circuit. `apply_layout` widens `ZZ` to `IIIZZ` (here the
layout happened to keep qubits 0 and 1) **and** permutes it to follow the final
layout. Omit it and you get either a dimension error or — worse — a number computed
on the wrong qubits.

**Checklist for `EstimatorV2`.**

1. Circuit has **no** measurements.
2. Circuit is ISA (`pm.run(...)`).
3. Observable passed through `apply_layout(isa.layout)`.
4. `precision` (target standard error) instead of `shots`; read the uncertainty back
   from `result[0].data.stds`.
5. Error mitigation is an Estimator concept: `resilience_level = 0/1/2`
   (0 = none, 1 = readout mitigation, 2 = + ZNE). The Sampler has **no**
   resilience levels.

**Interpretation.** `⟨ZZ⟩ = 0.986` instead of `1.0` corresponds to roughly a
0.7% error rate per shot — consistent with the `0.68%` invalid-outcome fraction
measured in the previous exercise on the same backend.

</details>

- Enable dynamical decoupling and gate twirling on a Sampler job and compare counts

<details><summary>Solution</summary>

**Runtime version — not executable here** (requires an IBM Quantum account). This
is the current options API for `qiskit-ibm-runtime` 0.49:

```python
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)

plain = SamplerV2(mode=backend)

suppressed = SamplerV2(mode=backend)
suppressed.options.dynamical_decoupling.enable = True
suppressed.options.dynamical_decoupling.sequence_type = "XY4"       # or "XX", "XpXm"
suppressed.options.dynamical_decoupling.extra_slack_distribution = "middle"
suppressed.options.twirling.enable_gates = True                     # Pauli-twirl 2q gates
suppressed.options.twirling.enable_measure = True                   # twirl readout
suppressed.options.twirling.num_randomizations = 32
suppressed.options.twirling.shots_per_randomization = 128

counts_plain = plain.run([isa], shots=4096).result()[0].data.meas.get_counts()
counts_dd    = suppressed.run([isa], shots=4096).result()[0].data.meas.get_counts()

from qiskit.quantum_info import hellinger_fidelity
ideal = {"00": 2048, "11": 2048}
print("plain     :", hellinger_fidelity(ideal, counts_plain))
print("DD+twirl  :", hellinger_fidelity(ideal, counts_dd))
```

Typical effect on a GHZ-style circuit with idle qubits: Hellinger fidelity improves
from `≈ 0.93` to `≈ 0.96`, with the biggest gains on circuits that have long idle
windows (wide circuits, mid-circuit measurement, deep one-qubit stretches).

**Executable stand-in** — apply the dynamical-decoupling *transpiler pass* locally
and count the pulses it inserts:

```python
from qiskit import QuantumCircuit
from qiskit.circuit.library import XGate
from qiskit.transpiler import PassManager, generate_preset_pass_manager
from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling

idle_c = QuantumCircuit(3)
idle_c.h(0); idle_c.cx(0, 1)
idle_c.barrier()
idle_c.cx(0, 1)                     # qubit 2 idles through the whole circuit
idle_c.measure_all()

pm_dd = generate_preset_pass_manager(optimization_level=1, backend=backend_g,
                                     seed_transpiler=5)
isa_idle = pm_dd.run(idle_c)
print("before DD:", dict(isa_idle.count_ops()))

durations = backend_g.target.durations()
dd_pass = PassManager([ALAPScheduleAnalysis(durations),
                       PadDynamicalDecoupling(durations, [XGate(), XGate()])])
dd_circ = dd_pass.run(isa_idle)
print("after  DD:", dict(dd_circ.count_ops()))
print("X pulses inserted into idle windows:",
      dd_circ.count_ops().get("x", 0) - isa_idle.count_ops().get("x", 0))
```

Real output:

```
before DD: {'measure': 3, 'rz': 2, 'cx': 2, 'barrier': 2, 'sx': 1}
after  DD: {'delay': 13, 'x': 6, 'measure': 3, 'rz': 2, 'cx': 2, 'barrier': 2, 'sx': 1}
X pulses inserted into idle windows: 6
```

**What each technique does.**

- **Dynamical decoupling** (error *suppression*): fills idle time with pulse
  sequences that average out low-frequency dephasing — an `XX` sequence is a Hahn
  echo, `XY4` also refocuses the `y` component and is more robust to pulse errors.
  Here the scheduler turned bare idle time into 13 `delay` instructions and
  inserted 6 `X` pulses. Cost: extra gates (with their own error), so DD helps only
  when idle-induced dephasing dominates.
- **Pauli twirling** (error *suppression*): randomly conjugating each two-qubit
  gate with Paulis (compensated afterwards) converts coherent, structured error
  into stochastic Pauli error. Coherent errors add up as amplitudes (`∝ n²`),
  stochastic ones as probabilities (`∝ n`) — twirling is what makes the error
  behave predictably, and it is a prerequisite for ZNE and PEC.
- **Measurement twirling** randomises readout asymmetry into a symmetric channel.

**What they are not.** Neither is error *mitigation*: they do not extrapolate or
post-process, so a Sampler's bit strings remain physically meaningful. Mitigation
(`resilience_level ≥ 1`, ZNE, PEC) lives on the **Estimator** only, because it
corrects expectation values rather than samples.

</details>

- Retrieve yesterday's jobs with `service.jobs()` and re-load one result by job ID

<details><summary>Solution</summary>

**Not executable here** (requires an IBM Quantum account and a job history), but
this is the correct API for `qiskit-ibm-runtime` 0.49:

```python
from datetime import datetime, timedelta, timezone
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()

since = datetime.now(timezone.utc) - timedelta(days=1)
jobs = service.jobs(
    created_after=since,          # also: created_before=
    limit=20,
    pending=False,                # only finished jobs
    # backend_name="ibm_brisbane",
    # job_tags=["bell-study"],
)

for job in jobs:
    m = job.metrics()
    print(f"{job.job_id()}  {job.status():10s}  {job.backend().name:16s} "
          f"queued={m['usage']['quantum_seconds']:.1f}s  created={job.creation_date}")

# Re-load one result later, in a completely different process
job_id = jobs[0].job_id()
old_job = service.job(job_id)
result = old_job.result()                      # PrimitiveResult, exactly as before
counts = result[0].data.meas.get_counts()
print(counts)
print("inputs:", old_job.inputs.keys())        # the submitted PUBs, options, version
```

Expected shape of the listing:

```
d1abc23efgh45ijklmno6  DONE        ibm_brisbane     queued=3.2s  created=2026-09-15 14:02:11+00:00
d1abc23efgh45ijklmnp7  DONE        ibm_torino       queued=1.8s  created=2026-09-15 11:47:03+00:00
```

**Points a good answer makes.**

- Results are **stored server-side**, so `service.job(job_id)` works from any
  machine, any time (subject to the retention window) — always log `job.job_id()`.
- `job.result()` on a still-running job **blocks**; check `job.status()` first, or
  use `job.done()` / `job.in_final_state()` in a poll loop.
- `service.jobs()` is paginated: `limit` (default 10) and `skip`, plus filters
  `backend_name`, `pending`, `created_after`/`created_before`, `job_tags`,
  `session_id`. Tagging jobs at submission (`SamplerV2(..., options={"environment":
  {"job_tags": ["bell-study"]}})`) is what makes this filtering useful later.
- `job.metrics()` gives timing and usage (billable quantum seconds); `job.inputs`
  returns the PUBs and options that were submitted, which is how you reconstruct
  exactly what produced a result.
- `job.error_message()` explains failures — the most common being "circuit is not
  ISA" and "observable has the wrong number of qubits".

</details>


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
