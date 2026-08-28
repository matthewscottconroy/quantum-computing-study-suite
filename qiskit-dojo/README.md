# Qiskit Dojo

A desktop "coding dojo" for the IBM Certified Quantum Developer exam
(C1000-179): you **write real Qiskit 2.x code** in an editor, the app
executes it in an isolated subprocess, and assertion-based tests grade it
automatically — fully offline.

Part of the quantum-study suite; mirrors the architecture and theme of
`vqa-trainer`.

## Running

```bash
# From the repo root, using the shared study venv:
../.venv/bin/python main.py        # or: python main.py inside the venv
```

Dependencies: see `requirements.txt` (PyQt6, anthropic, matplotlib for the
UI). The **execution harness** additionally needs qiskit, qiskit-aer, and
numpy — these come from the shared venv at `../.venv`, which the harness
locates automatically (current venv → `../.venv/bin/python` → fallback to
`sys.executable`).

## What a session looks like

1. **Setup** — pick sections, kata count, and order (shuffled or
   curriculum order). Katas you have failed recently are weighted to
   reappear.
2. **Kata** — task statement on the left; code editor (monospace,
   Tab = 4 spaces) and output pane on the right. Buttons:
   - **Run** — executes your code + the kata's tests in a subprocess
     (20 s timeout, `MPLBACKEND=Agg`), shows pass/fail plus stdout and
     tracebacks.
   - **Hint** — progressive hints (2–3 per kata).
   - **Reveal Solution** — shows the reference solution.
   - **Claude Review** — optional: sends the task + your code to Claude
     for style/idiom feedback. Needs an Anthropic API key
     (`ANTHROPIC_API_KEY` env var or `~/.config/quantum-study/api_key.txt`);
     everything else works with no key and no network.
3. **Summary** — pass rate and per-section breakdown.
4. **History** — lifetime stats and per-section pass-rate charts.

## Sections (~36 katas)

The 8 C1000-179 exam areas, weighted roughly like the exam, plus two
dojo-specific practice styles:

| Section            | Katas | Notes |
|--------------------|-------|-------|
| Create circuits    | 4     | Bell/GHZ, registers, Parameter/assign_parameters, compose |
| Quantum operations | 3     | Operator identities, SparsePauliOp (little-endian), Statevector evolve |
| Run circuits       | 3     | AerSimulator run, generate_preset_pass_manager/ISA, optimization levels |
| Sampler            | 3     | SamplerV2 PUBs, parameterized PUBs, named-creg BitArray access |
| Estimator          | 3     | EstimatorV2 PUBs, parameter sweeps, Hamiltonian energies |
| Visualization      | 3     | plot_histogram, plot_bloch_multivector, draw() return types |
| Results analysis   | 2     | per-qubit probabilities (endianness), ⟨ZZ⟩ from counts |
| OpenQASM           | 2     | qasm2 round-trip, qasm3 loads/dumps |
| Debugging          | 6     | starter contains a REAL bug you must find and fix |
| Modernization      | 7     | starter uses retired 0.x APIs you must rewrite for 2.x |

Debugging bugs: wrong bit order, measured circuit passed to the Estimator,
non-ISA circuit submitted to a backend, off-by-one in a parameter loop,
wrong measurement basis, mutating `qc.data` while iterating.

Modernization targets: `qiskit.execute`, `from qiskit import Aer`,
`BasicAer`, V1 primitives (`quasi_dists`), `bind_parameters`, `qc.qasm()`,
`CXCancellation`. Their tests fail on the legacy starter and pass on a
correct 2.x rewrite.

## Kata file format

One file per kata under `katas/<section_dir>/`, auto-discovered at
startup. Each file exposes a `KATA` object:

```python
from core.models import Kata

KATA = Kata(
    id="my_kata",                  # unique, stable (used in history)
    section="Sampler",             # must match a section name
    title="Short imperative title",
    difficulty="intermediate",     # beginner | intermediate | advanced
    prompt="Task statement…",      # markdown-ish plain text
    starter_code="…",              # what the editor opens with
    test_code="…",                 # plain asserts w/ helpful messages;
                                   # runs in the SAME namespace as the
                                   # user's code (their variables are in scope)
    solution_code="…",             # reference solution; must pass test_code
    hints=["…", "…"],              # 2–3 progressive hints
)
```

### Adding a kata

1. Drop a new file in the right `katas/` subdirectory (create a new
   directory for a new section and add it to `SECTION_ORDER` in
   `katas/__init__.py`).
2. Write `test_code` as bare asserts with actionable messages — the
   harness reports the first failing assert to the user.
3. Verify: the `solution_code` must pass, and for Debugging/Modernization
   katas the `starter_code` must fail. Quick check from the app dir:

```python
import sys; sys.path.insert(0, ".")
from katas import all_katas
from core.runner import run_kata
k = next(k for k in all_katas() if k.id == "my_kata")
print(run_kata(k.solution_code, k.test_code))
```

## Execution harness (core/runner.py)

- Writes `user_code.py`, `test_code.py`, and a generated `harness.py`
  into a `tempfile.TemporaryDirectory`.
- Runs `<venv python> harness.py` with `cwd=` that temp dir,
  `MPLBACKEND=Agg`, and a 20-second timeout.
- The harness `exec`s the user code into a fresh namespace, then `exec`s
  the kata's `test_code` against that same namespace; a sentinel line on
  stdout plus exit code 0 marks success. Exit code 2 = error in user
  code, 3 = test failure/error.
- The UI runs the harness on a `QThread` so the window never blocks.

## Persistence

Sessions append to `~/.local/share/quantum-study/dojo_history.json`
(schema is integrated against by the coach app — do not change):

```json
[
  {
    "timestamp": 1724800000.0,
    "total": 8,
    "passed": 6,
    "attempts": [
      {"kata_id": "sam_basic", "section": "Sampler", "passed": true, "tries": 2}
    ]
  }
]
```
