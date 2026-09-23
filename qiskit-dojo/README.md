# Qiskit Dojo

A desktop "coding dojo" for the IBM Certified Quantum Developer exam
(C1000-179): you **write real Qiskit 2.x code** in an editor, the app
executes it in an isolated subprocess, and assertion-based tests grade it
automatically — fully offline.

Part of the quantum-study suite; mirrors the architecture and theme of
`vqa-trainer`.

## Running

```bash
# From this directory (qiskit-dojo/), using the shared study venv:
../.venv/bin/python main.py        # or: python main.py inside the venv

# Or from the repo root:
.venv/bin/python qiskit-dojo/main.py
```

Tests (offscreen Qt, temp data dir — never touches your real history):

```bash
cd qiskit-dojo && ../.venv/bin/python -m pytest          # fast suite, a few seconds
../.venv/bin/python -m pytest -m slow tests/test_sweep.py  # all 72 katas through the harness
../.venv/bin/python -m pytest -m slow tests/test_sweep.py -k "dbg or mod"  # fix-it katas only
```

The fast suite checks the bank structurally (`tests/test_katas.py`: at least
72 katas, per-section floors matching the exam blueprint, unique ids and
titles, 2-3 hints, code compiles, files live in their section directory).
The slow sweep runs every kata twice through `core/runner.py` - the
reference solution must pass and the starter must not - so it is one
parametrised case per kata (144+ cases, ~1-1.5 s each on an idle machine;
several minutes on a loaded one).

Dependencies: see `requirements.txt` (PyQt6, anthropic, matplotlib for the
UI). The **execution harness** additionally needs qiskit, qiskit-aer, and
numpy — these come from the shared venv at `../.venv`, which the harness
locates automatically (current venv → `../.venv/bin/python` → fallback to
`sys.executable`).

## What a session looks like

1. **Setup** — pick sections, kata count, and order (shuffled or
   curriculum order). Katas you have failed recently are weighted to
   reappear. The per-section pass rates shown here refresh every time
   you return to this screen.
2. **Kata** — task statement on the left; code editor (monospace,
   Tab = 4 spaces) and output pane on the right. Buttons:
   - **Run** — executes your code + the kata's tests in a subprocess
     (20 s timeout, `MPLBACKEND=Agg`), shows pass/fail plus stdout and
     tracebacks. Skip and End Session are disabled until the run
     finishes, so a result always lands on the kata it graded.
   - **Hint** — progressive hints (2–3 per kata).
   - **Reveal Solution** — shows the reference solution.
   - **Claude Review** — optional: sends the task + your code to Claude
     for style/idiom feedback. Needs an Anthropic API key
     (`ANTHROPIC_API_KEY` env var or `~/.config/quantum-study/api_key.txt`);
     everything else works with no key and no network.
   - **⚑ Flag for review** — toggles the current kata on the shared review
     list (`dojo_flagged.json`, see Persistence). Click again to unflag.
     The button shows the saved state whenever a kata opens, so a kata
     flagged in an earlier session lights up immediately.
3. **Summary** — pass rate and per-section breakdown.
4. **History** — lifetime stats, per-section pass-rate charts, and the
   **Flagged for review** list (section badge, title, date flagged) with a
   per-row **Unflag** button.
5. **Reference** — the **Browse Reference** button on the setup screen opens
   the in-app docs browser (see below); **← Back** returns to setup.

## Reference browser

`ui/screens/reference_screen.py` renders the suite's shared documentation
corpus without leaving the app. It resolves the docs root relative to its
own location — `Path(__file__).resolve().parents[3] / "docs"`, i.e.
`<repo>/docs` — so the app must live inside the repository checkout (no
home path is hard-coded). Every `docs/**/*.md` file is listed:

- **Left**: a chapter tree (one node per `docs/<NN_chapter>/` directory,
  leaves titled from each file's first `# ` heading; `docs/README.md`
  appears first as *Learning Ladder*) with a live filter box.
- **Right**: the selected chapter rendered with Qt's native Markdown
  import (GitHub tables and fenced code blocks supported). Exercise
  `<details><summary>Solution</summary>` blocks are shown inline as a bold
  **Solution:** lead-in. Relative `.md` links navigate inside the browser
  and `#fragment` links jump to the matching heading (GitHub-style slugs);
  a link whose target file is missing reports *Link target not found* in
  the breadcrumb instead of being handed to the desktop. `http(s)` links
  open in your system browser; **Open externally** hands the current file
  to your desktop's Markdown handler.

Fully offline; nothing here touches the network or the API key.

## Sections (72 katas)

The 8 C1000-179 exam areas, weighted like the exam blueprint, plus two
dojo-specific practice styles:

| Section            | Katas | Notes |
|--------------------|-------|-------|
| Create circuits    | 10    | Bell/GHZ, registers (incl. cross-register Toffoli), Parameter/ParameterVector sweeps, compose, `to_gate` + control, dynamic `if_test`, inverse/uncompute, W state |
| Quantum operations | 9     | Operator identities, SparsePauliOp (little-endian) and Hamiltonian simplification, Statevector evolve, global phase vs equality, partial_trace/purity/fidelity, commuting groups, random_clifford |
| Run circuits       | 8     | AerSimulator run and one-job batches, generate_preset_pass_manager/ISA compliance, optimization level vs depth, Target queries, lowest-error qubit chain |
| Sampler            | 7     | SamplerV2 PUBs, parameterized and multi-PUB jobs, named- and two-creg BitArrays, post-selection, parameter broadcasting/PUB shape |
| Estimator          | 7     | EstimatorV2 PUBs, parameter sweeps, Hamiltonian energies, estimate vs exact diagonalisation, precision/shots/stds, observable broadcasting |
| Visualization      | 6     | plot_histogram (one and two datasets), plot_bloch_multivector, plot_state_city, `draw()` return types, `idle_wires`/`fold`/`cregbundle` |
| Results analysis   | 6     | per-qubit probabilities (endianness), ⟨ZZ⟩ and ⟨Z2 Z0⟩ from counts, marginal_counts, BitArray basics, shot-noise error bars |
| OpenQASM           | 3     | qasm2 round-trip, qasm3 loads/dumps, qasm3 round-trip that preserves the unitary |
| Debugging          | 8     | starter contains a REAL bug you must find and fix |
| Modernization      | 8     | starter uses retired 0.x APIs you must rewrite for 2.x |

Debugging bugs: wrong bit order, `enumerate()` reading a counts key
big-endian, measured circuit passed to the Estimator, observable not mapped
to the transpiled layout, non-ISA circuit submitted to a backend,
off-by-one in a parameter loop, wrong measurement basis, mutating `qc.data`
while iterating.

Modernization targets: `qiskit.execute`, `from qiskit import Aer`,
`BasicAer`, V1 primitives (`quasi_dists`), `bind_parameters`, `qc.qasm()`,
`CXCancellation`, and a full `execute` + V1-Sampler script that has to
become a preset pass manager + SamplerV2. Their tests fail on the legacy
starter and pass on a correct 2.x rewrite.

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
3. Verify: the `solution_code` must pass, and the `starter_code` must not
   (for Debugging/Modernization katas it must fail with a test failure or
   an error in the user's code - never a timeout). Quick check from the
   app dir:

```python
import sys; sys.path.insert(0, ".")
from katas import all_katas
from core.runner import run_kata
k = next(k for k in all_katas() if k.id == "my_kata")
print(run_kata(k.solution_code, k.test_code))
```

   Then run the fast suite (it will tell you if the file failed to import,
   sits in the wrong directory, or has the wrong number of hints) and the
   sweep for just your kata:
   `../.venv/bin/python -m pytest -m slow tests/test_sweep.py -k my_kata`.
   Section floors live in `tests/test_katas.py::SECTION_TARGETS`; raise
   the floor when a section grows and you want the new count locked in.

## Execution harness (core/runner.py)

- Writes `user_code.py`, `test_code.py`, and a generated `harness.py`
  into a `tempfile.TemporaryDirectory`.
- Runs `<venv python> harness.py` with `cwd=` that temp dir,
  `MPLBACKEND=Agg`, and a 20-second timeout.
- The harness `exec`s the user code into a fresh namespace, then `exec`s
  the kata's `test_code` against that same namespace; a sentinel line on
  stdout plus exit code 0 marks success. Exit code 2 = error in user
  code, 3 = test failure/error.
- Feedback starts with a one-liner — `FAILED: <assert message>` or
  `ERROR: <ExceptionType>: <message>` — followed by a traceback with the
  harness's own frames removed, so the first frame you read is in
  `your_code.py` or `kata_tests.py` (with the offending source line).
- The UI runs the harness on a `QThread` so the window never blocks.

## Persistence

All files live in `~/.local/share/quantum-study/` (override the directory
with the `QUANTUM_STUDY_DATA_DIR` environment variable — handy for tests).

Sessions append to `dojo_history.json`
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

### Flagged katas

`⚑ Flag for review` maintains `dojo_flagged.json` following the suite-wide
flagging contract (read by `coach.py`'s review queue). Flagging is a
toggle — flagging an already-flagged kata removes its entry:

```json
[
  {
    "id": "dbg_bit_order",
    "label": "Fix it: wrong bit order",
    "category": "Debugging",
    "app": "qiskit-dojo",
    "timestamp": 1724800000.0
  }
]
```

`id` is the kata id, `label` its title, `category` its section. Helpers in
`persistence.py`: `load_flagged()`, `flagged_ids()`, `is_flagged(id)`,
`toggle_flag(kata) -> bool` (new state), `unflag(id)`.
