# Circuit Trainer

A hands-on quantum circuit problem trainer. Problems are generated programmatically using
Qiskit — the correct answers are computed by running real quantum circuits through
Qiskit's Aer simulator, so there is no ambiguity in correctness. Free-form explanation
questions are graded by Claude (`claude-sonnet-4-6`).

---

## Features

- **12 problem categories** covering every aspect of circuit arithmetic
- **3 difficulty levels** — beginner, intermediate, advanced
- **4 answer formats** — multiple choice, numeric, state vector, and free-form explanation
- **Auto-graded locally** — MC, numeric, and state vector answers are checked instantly
  against Qiskit-computed correct values; no API call needed for these
- **Claude-graded explanations** — circuit explanation problems use Claude for open-ended
  grading with step-by-step feedback
- **Circuit images** — every problem displays the circuit rendered as a PNG via Qiskit's
  `circuit_drawer` (matplotlib backend)
- **Worked solutions** — each problem includes a step-by-step solution shown after
  submission
- **Session history** — sortable table of past sessions with per-category score breakdown
- **CollapsiblePanel** — hints and solution steps animate open on click

---

## Requirements

```
anthropic>=0.93.0
qiskit>=2.0.0
qiskit-aer>=0.17.0
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
your environment. If not set, free-form problems will error at grading time with a
descriptive message; all other problem types work offline.

---

## Running

```bash
python main.py
```

---

## Usage

### Setup Screen

1. **Select categories** — choose any subset of the 12 categories
2. **Pick difficulty** — Beginner / Intermediate / Advanced / Mixed
3. **Set problem count** — default 12
4. Click **Start Session**

### Problem Screen

- The circuit image is displayed in the left panel
- Depending on answer format:
  - **Multiple choice** — four radio buttons
  - **Numeric** — single-line text input (accepts decimal, e.g. `0.4330`)
  - **State vector** — comma-separated complex amplitudes
  - **Free-form** — multi-line text box
- **Hint** button (collapsible) — reveals progressive hints
- **Submit** button enables once a valid answer is entered

### Feedback

After submission:
- Auto-graded: result shown immediately with a coloured verdict badge
- Free-form: loading overlay while Claude grades
- **Worked solution** — collapsible step-by-step solution
- **Key concepts** — list of tested concepts
- **Next Problem** or **End Session**

### Summary and History

Session summary with accuracy and per-category scores. History screen shows all past
sessions in a sortable table.

---

## Problem Categories

| Category | Answer Format | Description |
|---|---|---|
| Single-gate output | Multiple choice | Apply one gate to a known input state; find output |
| Gate sequence | Multiple choice | Apply 2–4 gates in sequence; find final output |
| Measurement probabilities | Numeric | Compute measurement outcome probabilities |
| Gate / matrix identification | Multiple choice | Match a matrix to its gate name |
| Circuit unitary | Multiple choice | Compute the full unitary matrix of a small circuit |
| Entanglement detection | Multiple choice | Determine if a 2-qubit output state is entangled |
| Multi-qubit circuit output | Multiple choice | Multi-qubit circuits including CNOT, CZ, SWAP, Toffoli |
| Circuit equivalence | Multiple choice | Determine if two circuits implement the same unitary |
| Notation reading | Multiple choice | Parse Dirac notation and circuit shorthand |
| Circuit composition | Multiple choice | Compose two circuits; find the resulting unitary |
| Noise channel | Multiple choice / Numeric | Identify noise channels and their Kraus operators |
| Circuit explanation | Free-form | Explain the purpose or operation of a circuit in prose |

---

## Grading Details

### Auto-grading (local, no API)

**Multiple choice**: index comparison, score 0 or 10.

**Numeric**: absolute tolerance `NUMERIC_TOLERANCE = 1e-3`. Score 10 if within tolerance,
0 otherwise (no partial credit for numeric in this app — exact agreement is expected for
probability/amplitude values).

**State vector**: parsed as comma-separated complex numbers, checked component-by-component
within tolerance, with global-phase invariance (the state `e^{iφ}|ψ⟩` is accepted for any
global phase `φ`).

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
│   │   ├── setup_screen.py      Category/difficulty/count selection
│   │   ├── problem_screen.py    Problem display and answer input
│   │   ├── summary_screen.py    Session results chart
│   │   └── history_screen.py    Past sessions table
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
2. Run through `AerSimulator` (statevector mode) with the chosen input state
3. Format the output statevector as a human-readable string
4. Generate 3 distractors via `make_distractors()` (wrong answers that look plausible)
5. Shuffle choices, record correct index, render circuit PNG
6. Return a fully-populated `Problem` dataclass

**Static pools** (notation.py): questions drawn from a fixed list, shuffled per call.

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

---

## Known Limitations

- **Single-gate solution steps** are only written out in full for X, H, and Z gates.
  All other gates fall back to a generic "apply the matrix" step. This is a content
  gap, not a code bug.
- **Notation pool** has 10 static questions; long sessions will see repeats.
- **Gate sequence pool** has 5–6 fixed sequences per difficulty level.
- Free-form explanation problems require the `ANTHROPIC_API_KEY` environment variable.

---

## Data Persistence

Sessions written to `~/.local/share/quantum-study/circuit_trainer_history.json`.
