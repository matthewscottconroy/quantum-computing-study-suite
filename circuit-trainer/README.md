# Circuit Trainer

A hands-on quantum circuit problem trainer. Problems are generated programmatically using
Qiskit — the correct answers are computed by evolving real quantum circuits with
`qiskit.quantum_info` (`Statevector` / `Operator`), so there is no ambiguity in
correctness. Free-form explanation questions are graded by Claude (`claude-sonnet-4-6`).

---

## Features

- **12 problem categories** covering every aspect of circuit arithmetic
- **3 difficulty levels** — beginner, intermediate, advanced
- **2 answer formats in use** — multiple choice (auto-graded) and free-form explanation
  (Claude-graded). Numeric and state-vector graders exist in `grading/auto_grader.py`,
  but no current generator emits those formats
- **Auto-graded locally** — multiple-choice answers are checked instantly against
  Qiskit-computed correct values; no API call needed
- **Claude-graded explanations** — circuit explanation problems use Claude for open-ended
  grading with step-by-step feedback
- **Circuit images** — every problem displays the circuit rendered as a PNG via Qiskit's
  `circuit_drawer` (matplotlib backend)
- **Worked solutions** — each problem includes a step-by-step solution shown after
  submission
- **Session history** — lifetime stat cards (sessions, problems, accuracy), an accuracy
  trend chart, per-category average scores, and the flagged-for-review list
- **CollapsiblePanel** — the Claude model answer on free-form problems folds open on click
- **Sprint mode** — 10 rapid-fire prediction questions with a 60-second countdown each,
  auto-graded only, instant right/wrong flash and auto-advance
- **Reference browser** — the repo's `docs/**/*.md` study chapters rendered in-app, with a
  "jump to category" picker that opens the chapter behind each problem category
- **Flag for review** — toggle a flag on any answered problem; flagged items are listed
  (and can be unflagged) on the history screen and picked up by the repo-level coach

---

## Requirements

```
anthropic>=0.93.0
qiskit>=2.0.0
PyQt6>=6.6.0
matplotlib>=3.8.0
numpy>=1.26.0
pylatexenc>=2.10
```

Install:
```bash
pip install -r requirements.txt
```

Qiskit is required even for the non-Claude problems — it is used to compute correct
answers and render circuit images.

---

## API Key

Only needed for circuit explanation (free-form) problems. Set `ANTHROPIC_API_KEY` in
your environment, or write the key to `~/.config/quantum-study/api_key.txt`. If neither
is set, free-form problems will error at grading time with a descriptive message; all
other problem types work offline.

---

## Running

```bash
python main.py
```

---

## Usage

### Setup Screen

1. **Select categories** — choose any subset of the 12 categories
2. **Pick difficulty** — Adaptive (recommended) / Beginner / Intermediate / Advanced
3. **Set problem count** — default 12
4. Click **Start Training** (or **Start Sprint ⏱** for the timed mode, see below)

### Problem Screen

- The question, circuit image(s), matrix and input state are displayed in the left panel
- Depending on answer format:
  - **Multiple choice** — four answer buttons; click one or press **A / B / C / D**
  - **Free-form** — multi-line text box plus **Submit Answer** (Enter also submits)
- **Hint** button — reveals progressive hints (the label shows how many remain)
- **Skip →** — counts the problem as attempted-but-unanswered; disabled once answered

### Feedback

After submission:
- Auto-graded: the correct choice is highlighted green (and a wrong pick red) immediately
- Free-form: loading overlay while Claude grades, then score + feedback + model answer
- **Worked solution** — step-by-step solution shown inline
- **Key concepts** — list of tested concepts
- **⚑ Flag for review** toggle and **Next Problem →** (the last one opens the summary)

### Summary and History

Session summary with accuracy and per-category scores. History screen shows lifetime
stats, an accuracy trend, per-category averages, and the **Flagged for review** list
(newest first, each row with an **Unflag** button).

### Flag for Review

Every answered problem's result view (worked solution visible) has a **⚑ Flag for
review** button next to **Next Problem**. Flagging is a toggle: click again to unflag.
The flag id is the problem's `problem_id` when the generator draws from a fixed pool
and stamps one (gate sequence `gs:H-X-H:0`, notation `notation:07`, gate identification
`gi:matrix:H` / `gi:desc:H`, Kraus identification `noise:kraus:depol`); for the
randomly generated problems it is a stable 16-hex-char SHA-1 of the category + question
text. Either way, re-seeing the identical problem shows it as already flagged. Sprint
mode has no flag control (no per-question result view).

Entries are appended to `trainer_flagged.json` in the suite data directory
(`~/.local/share/quantum-study/` unless `QUANTUM_STUDY_DATA_DIR` is set), following
the suite-wide flagging contract:

```json
{"id": "f8bd26a68bcf28a8",
 "label": "Single-gate output: Apply H to |0⟩. What is the output state?",
 "category": "Single-gate output",
 "app": "circuit-trainer",
 "timestamp": 1788958864.57}
```

### Reference

The **Reference** button on the setup screen opens an in-app browser for the shared
`docs/` corpus (resolved relative to the app: `../docs`). The left pane lists every
chapter grouped by section; the right pane renders the Markdown (GitHub dialect —
tables, code, exercise solutions shown inline). The **Jump to category…** picker opens
the chapter most relevant to a trainer category (e.g. *Noise channel* → density
matrices and open systems; *Notation reading* → linear algebra). Relative `.md` links
inside a chapter navigate in-app; **Open externally** hands the current file to your
system Markdown viewer. **← Back** returns to setup.

### Sprint Mode

Started with the **Start Sprint ⏱** button on the setup screen (the difficulty
selector applies; category checkboxes are ignored):

- **10 questions, 60 seconds each** — a visible countdown runs in the top bar
  (turns red under 10 seconds). Hitting zero counts the question as wrong and
  auto-advances.
- **Prediction categories only** — questions are drawn from the five generators
  with deterministic, auto-checkable answers: Measurement probabilities,
  Single-gate output, Gate sequence, Circuit unitary, and Multi-qubit circuit
  output. No Claude grading is ever used.
- **Instant feedback** — answering (click or A/B/C/D keys) flashes ✓/✗ for
  under a second, then the next question loads automatically. No hints, no
  worked solutions mid-sprint.
- **End screen** — score, accuracy, average response time, and a per-category
  breakdown table.

Sprint sessions are saved to `trainer_history.json` in the standard session
schema (attempts keep their real generator category), with an extra
session-level `"sprint": true` tag so they can be distinguished later; the
history screen and repo-level dashboard read them like any other session.

Timing constants live in `config.py`: `SPRINT_QUESTION_COUNT` (10),
`SPRINT_SECONDS` (60), `SPRINT_FLASH_MS` (900).

---

## Problem Categories

| Category | Answer Format | Description |
|---|---|---|
| Single-gate output | Multiple choice | Apply one gate to a known input state; find output |
| Gate sequence | Multiple choice | Apply 2–4 gates in sequence; find final output |
| Measurement probabilities | Multiple choice | Compute measurement outcome probabilities |
| Gate / matrix identification | Multiple choice | Match a matrix to its gate name |
| Circuit unitary | Multiple choice | Compute the full unitary matrix of a small circuit |
| Entanglement detection | Multiple choice | Determine if a 2-qubit output state is entangled |
| Multi-qubit circuit output | Multiple choice | Multi-qubit circuits including CNOT, CZ, SWAP, Toffoli |
| Circuit equivalence | Multiple choice | Determine if two circuits implement the same unitary |
| Notation reading | Multiple choice | Parse Dirac notation and circuit shorthand |
| Circuit composition | Multiple choice | Compose two circuits; find the resulting unitary |
| Noise channel | Multiple choice | Exact bit-flip / phase-flip / depolarizing / amplitude-damping calculations and Kraus identification |
| Circuit explanation | Free-form | Explain the purpose or operation of a circuit in prose |

---

## Grading Details

### Auto-grading (local, no API)

**Multiple choice**: index comparison, score 0 or 10. This is the only auto-graded
format any current generator produces.

The grader also implements two formats no generator currently emits (kept for future
problem types): **Numeric** — absolute tolerance `NUMERIC_TOLERANCE = 1e-3`, score 10
or 0; **State vector** — comma-separated complex amplitudes, checked component-by-
component within tolerance with global-phase invariance (`e^{iφ}|ψ⟩` accepted for any
`φ`).

### Claude grading (free-form)

The grader sends the problem text, the user's answer, and the worked solution to Claude.
The prompt requests a JSON response with `score` (0–10), `feedback`, `model_answer`, and
`follow_up`. The JSON fence is stripped if present.

---

## Architecture

```
circuit-trainer/
├── main.py
├── config.py                    Model, DPI, tolerance, session defaults
├── core/
│   ├── models.py                Problem, Attempt, TrainerConfig, SessionStats dataclasses
│   └── session.py               Session state: problem sequencing, attempt accumulation
├── problems/
│   ├── __init__.py              generate(category, difficulty) dispatcher (lazy import)
│   ├── _utils.py                SINGLE_QUBIT_GATES, INPUT_STATES, render_circuit(),
│   │                            format_statevector(), statevector_for_circuit(), make_distractors()
│   ├── single_gate.py           X/H/Z/S/T/Rx/Ry/Rz applied to known input states
│   ├── gate_sequence.py         Fixed sequences with known gate identities (HXH=Z, etc.)
│   ├── measurement.py           Measurement probability calculation
│   ├── gate_identity.py         Matrix → gate name matching
│   ├── circuit_unitary.py       Full unitary computation for small circuits
│   ├── entanglement.py          Entanglement detection after 2-qubit circuit
│   ├── multi_qubit.py           CNOT, CZ, SWAP, Toffoli output states
│   ├── equivalence.py           Circuit equivalence — two circuits, same unitary?
│   ├── notation.py              Static pool: 10 Dirac/circuit notation questions
│   ├── composition.py           Compose two circuits
│   ├── noise.py                 Noise channel identification and Kraus operators
│   └── circuit_explanation.py  Free-form: explain a circuit's purpose
├── grading/
│   ├── auto_grader.py           Local grading for MC, numeric, statevector
│   └── claude_grader.py         Claude grading for FREE_FORM answers
├── workers/
│   ├── problem_worker.py        QThread: generate problem (Qiskit runs here)
│   └── evaluation_worker.py     QThread: Claude grading
├── ui/
│   ├── main_window.py           Screen controller
│   ├── screens/
│   │   ├── setup_screen.py      Category/difficulty/count selection + sprint launch
│   │   ├── problem_screen.py    Problem display and answer input
│   │   ├── sprint_screen.py     Sprint mode: countdown question screen + end screen
│   │   ├── summary_screen.py    Session results chart
│   │   ├── history_screen.py    Lifetime stats + flagged-for-review list (unflag)
│   │   └── reference_screen.py  In-app docs browser (docs/**/*.md, category jump)
│   └── widgets/
│       ├── circuit_panel.py     Displays circuit PNG
│       ├── collapsible_panel.py Animated hints and solutions
│       └── loading_overlay.py   Grading spinner
├── tests/
└── persistence.py
```

---

## How Problems Are Generated

The `problems/__init__.py` dispatches to the correct module by `ProblemCategory`. Each
module exposes a single `generate(difficulty: str) -> Problem` function. Problem
generation is always synchronous inside a `QThread` worker so the UI stays responsive.

**Qiskit flow for computational problems** (e.g. single-gate output):
1. Build a `QuantumCircuit`
2. Evolve the chosen input `Statevector` through it (`qiskit.quantum_info`; no Aer needed)
3. Format the output statevector as a human-readable string
4. Generate 3 distractors via `make_distractors()` (wrong answers that look plausible)
5. Shuffle choices, record correct index, render circuit PNG
6. Return a fully-populated `Problem` dataclass

**Static pools** (notation.py, gate_sequence.py, gate_identity.py, the Kraus
identification problem in noise.py): questions drawn from a fixed list, choices shuffled
per call. These generators set a stable `problem_id`, which feeds the per-problem SRS
weights (`persistence.problem_score_weights()`) and doubles as the flag id.

**Threading note**: generation runs on a `ProblemWorker` QThread. Qiskit's native
extension must be initialised on the GUI thread first — `workers/problem_worker.py`
imports `qiskit` at module level for exactly that reason (first-importing it inside a
worker thread crashed the *next* worker on Python 3.14 / qiskit 2.5). Keep that import.

---

## Problem Content by Category

### Single-Gate Output
- Beginner: X, H, Z on |0⟩, |1⟩
- Intermediate: full single-qubit gate set (11 gates) on |0⟩, |1⟩, |+⟩, |−⟩
- Advanced: S, T, Sdg, Tdg, Y, Rx/Ry/Rz(π/4, π/2) on all 6 cardinal Bloch states
- Worked steps: detailed for X/H/Z; generic fallback for other gates

### Gate Sequence
- 5 sequences per difficulty level (beginner: XX=I, ZZ=I, HH=I, HXH=Z, HZH=X)
- Intermediate: SS=Z, TT=S, HSH, etc.
- Advanced: TTTT=Z, HTHTH, SHS, etc.

### Notation Reading
- 10 static questions: 3 beginner, 4 intermediate, 3 advanced
- Topics: ket vectors, inner products, |+⟩, expectation value ⟨ψ|A|ψ⟩, tensor products,
  outer products, spectral decomposition, [[n,k,d]] code notation

---

## Configuration (`config.py`)

| Constant | Default | Effect |
|---|---|---|
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Model for free-form grading |
| `CLAUDE_MAX_TOKENS` | 1400 | Max tokens in grading response |
| `NUMERIC_TOLERANCE` | 1e-3 | Absolute tolerance for numeric answers |
| `PHASE_TOLERANCE` | 1e-3 | Global phase threshold for state vector comparison |
| `DEFAULT_PROBLEM_COUNT` | 12 | Pre-filled problem count |
| `CIRCUIT_DPI` | 130 | DPI for Qiskit circuit rendering |
| `SPRINT_QUESTION_COUNT` | 10 | Questions per sprint |
| `SPRINT_SECONDS` | 60 | Countdown per sprint question (timeout = wrong) |
| `SPRINT_FLASH_MS` | 900 | Right/wrong flash duration before auto-advance |

---

## Known Limitations

- **Single-gate solution steps** are only written out in full for X, H, and Z gates.
  All other gates fall back to a generic "apply the matrix" step. This is a content
  gap, not a code bug.
- **Notation pool** has 10 static questions; long sessions will see repeats.
- **Gate sequence pool** has 5–6 fixed sequences per difficulty level.
- Free-form explanation problems require an Anthropic API key (`ANTHROPIC_API_KEY` env
  var or `~/.config/quantum-study/api_key.txt`).

---

## Data Persistence

Both files live in the shared suite data directory, `~/.local/share/quantum-study/` by
default. Set `QUANTUM_STUDY_DATA_DIR` to redirect them (the same override `coach.py`
and the other apps honour) — handy for tests and experiments that must not touch real
history.

- `trainer_history.json` — sessions (schema unchanged; read by the repo-level
  `dashboard.py` and `coach.py`; sprint sessions carry `"sprint": true`).
- `trainer_flagged.json` — flagged problems as a JSON list of
  `{id, label, category, app, timestamp}` entries (see *Flag for Review* above).

`persistence.py` exposes `flag_id_for()`, `toggle_flag()`, `unflag()`, `is_flagged()`,
`load_flagged()` and `flagged_file()` (the resolved path).
