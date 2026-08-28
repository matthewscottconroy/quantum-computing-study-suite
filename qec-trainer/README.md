# QEC Trainer

A focused problem trainer for quantum error correction. 178 curated problems across 6
categories — from 3-qubit repetition codes through the surface code and fault tolerance
thresholds. Multiple choice and free-form questions; free-form answers are graded by
Claude (`claude-sonnet-4-6`).

---

## Features

- **178 curated problems** across 6 QEC categories
- **Two answer modes** — multiple choice (auto-graded instantly) and free-form
  (Claude-graded with detailed feedback)
- **3 difficulty levels** — beginner, intermediate, advanced
- **Hint system** — each problem has 1–2 hints, revealed progressively
- **Grading failure recovery** — if Claude grading fails, a dialog offers to skip
  with score 0 and continue the session
- **Session history** — past sessions with per-category score breakdown
- **Result screen** — shows worked explanation and model answer after each submission
- **Decoder Game** — interactive syndrome-decoding rounds with a difficulty ladder
  (3-qubit repetition → 5-qubit repetition → distance-3 surface code), verified
  locally with GF(2)/symplectic arithmetic — no API key needed

---

## Requirements

```
PyQt6>=6.6
anthropic>=0.25
```

Install:
```bash
pip install -r requirements.txt
```

The `anthropic` package is only called for free-form problems. All multiple choice
problems are graded locally with no API call.

---

## API Key

Set `ANTHROPIC_API_KEY` in your environment, or write the key to
`~/.config/quantum-study/api_key.txt`.

---

## Running

```bash
python main.py
```

---

## Usage

### Setup Screen

1. **Select categories** — all 5 checked by default
2. **Difficulty** — Beginner / Intermediate / Advanced / Mixed
3. **Problem count** — default 10
4. Click **Start Session**

### Problem Screen

- Question is displayed in a card
- **Multiple choice**: four radio buttons (A–D)
- **Free-form**: multi-line text box
- **Hint** button — click to reveal the next hint (button shows remaining hint count)
- **Submit** enables once a selection or non-empty text is entered

### Result Screen

After submission:
- **Verdict badge** — Correct / Incorrect (MC) or Correct / Partially correct / Incorrect (free-form)
- **Feedback** — explanation of the correct answer
- **Model answer** — what an ideal answer looks like (free-form only)
- **Next Problem** or **Finish Session**

### Summary and History

Session summary with accuracy rate and per-category scores. History table shows all past
sessions.

---

## Decoder Game

Launched with **Play Decoder Game** on the setup screen. 12 rounds of hands-on
syndrome decoding climbing a difficulty ladder (3 rounds per level):

1. **3-qubit repetition code** — a random X error (weight ≤ 1) is applied; the
   Z₁Z₂ / Z₂Z₃ syndrome is shown; pick the correction from 4 choices
   (including "no error").
2. **5-qubit repetition code** — weight-1 or weight-2 X errors; distance 5
   corrects both unambiguously from the 4-bit syndrome.
3. **Distance-3 rotated surface code, weight-1 errors** — 9 data qubits on a
   3×3 grid with 4 X-checks and 4 Z-checks drawn as squares (lit red when
   fired). Click data qubits to cycle a proposed correction (· → X → Z → Y),
   then submit.
4. **Surface code, weight-2 errors** — same grid, harder syndromes.

**Verification is exact GF(2)/symplectic computation** (`core/decoder_game.py`):
a correction succeeds iff `correction ⊕ error` lies in the stabilizer group —
it must commute with every stabilizer generator *and* act trivially on the
logical operators. Degenerate corrections (differing from the error by a
stabilizer) are therefore accepted on the surface code. The hardcoded surface
layout (X-checks {1,2}, {0,1,3,4}, {4,5,7,8}, {6,7}; Z-checks {0,3},
{1,2,4,5}, {3,4,6,7}, {5,8}; logical X = X₀X₃X₆, logical Z = Z₀Z₁Z₂ — 0-indexed)
was verified to be a [[9,1,3]] code by exhaustive symplectic checks.

Score and streaks are tracked during the game; the end screen shows the total,
accuracy, best streak, and a per-level breakdown. Each game is saved to
`qec_history.json` in the standard session schema under the category
**"Decoder Game"**, so it appears in the history screen and the repo-level
dashboard alongside the quiz categories.

---

## Problem Bank

178 problems: Repetition Code (34), Stabilizer Formalism (34), Fault Tolerance (33),
Steane Code (32), Surface Code (30), and Bosonic Codes (15). The tables below show a
representative sample from each category.

### Repetition Code (34 problems, sample below)

| ID | Difficulty | Type | Topic |
|---|---|---|---|
| rep_encode_0 | Beginner | MC | 3-qubit bit-flip encoding: |0⟩ → |000⟩ |
| rep_syndrome_10 | Beginner | MC | Syndrome (1,0): Z₁Z₂=−1, Z₂Z₃=+1 → qubit 1 flipped |
| rep_syndrome_11 | Beginner | MC | Syndrome (1,1): both stabilizers −1 → qubit 2 flipped |
| rep_syndrome_01 | Beginner | MC | Syndrome (0,1): Z₁Z₂=+1, Z₂Z₃=−1 → qubit 3 flipped |
| rep_no_error | Intermediate | MC | Syndrome (0,0): no error — what does this mean? |
| rep_phase_flip | Intermediate | MC | 3-qubit phase-flip code — how is |+⟩ encoded? |
| rep_5qubit | Advanced | MC | 5-qubit perfect code: parameters [[5,1,3]] |
| shor_9 | Advanced | Free-form | Shor's 9-qubit code — concatenation structure |

### Stabilizer Formalism (34 problems, sample below)

| ID | Difficulty | Type | Topic |
|---|---|---|---|
| stab_definition | Beginner | MC | Stabilizer definition: S|ψ⟩ = |ψ⟩ |
| stab_bell | Intermediate | MC | Stabilizers of a Bell state: XX, ZZ |
| stab_generators | Intermediate | MC | Minimum generator count for an [[n,k]] code |
| stab_clifford | Advanced | MC | Clifford group maps Pauli → Pauli under conjugation |
| stab_logical_x | Advanced | MC | Logical X̄ for 3-qubit bit-flip code |
| stab_commute | Intermediate | MC | Stabilizers must commute — why? |
| stab_freeform | Advanced | Free-form | Derive the syndrome measurement circuit for a stabilizer |

### Steane Code (32 problems, sample below)

| ID | Difficulty | Type | Topic |
|---|---|---|---|
| steane_params | Beginner | MC | [[7,1,3]] Steane code parameters |
| steane_css | Intermediate | MC | CSS code construction: Calderbank-Shor-Steane |
| steane_xstabs | Intermediate | MC | X stabilizers of the Steane code |
| steane_zstabs | Intermediate | MC | Z stabilizers of the Steane code |
| eastin_knill | Advanced | Free-form | Eastin-Knill theorem statement and implications |

### Surface Code (30 problems, sample below)

| ID | Difficulty | Type | Topic |
|---|---|---|---|
| surface_threshold | Beginner | MC | Fault tolerance threshold ~1% |
| surface_logical | Intermediate | MC | Logical error rate scaling with code distance |
| surface_decoder | Intermediate | MC | MWPM (minimum weight perfect matching) decoder |
| surface_plaquette | Advanced | MC | Plaquette and vertex stabilizers in the toric code |
| surface_freeform | Advanced | Free-form | Why does the surface code threshold improve with distance? |

### Fault Tolerance (33 problems, sample below)

| ID | Difficulty | Type | Topic |
|---|---|---|---|
| ft_threshold | Beginner | MC | Threshold theorem statement |
| ft_transversal | Intermediate | MC | Transversal gates — why they prevent error propagation |
| ft_magic | Advanced | MC | Magic state distillation for T gate |
| ft_cat | Advanced | MC | Cat qubits — bias-preserving operations |
| ft_syndrome_rep | Advanced | Free-form | Why must syndrome measurements be repeated? |

---

## Grading Details

### Multiple Choice (local, no API)

The user's letter selection (A–D) is mapped to an index and compared against
`correct_index`. Score is 10 for correct, 0 for incorrect. Feedback includes the
explanation stored in the problem record.

### Free-Form (Claude-graded)

The grading prompt includes the question, the user's answer, and the stored explanation.
Claude returns:
- `score` — 0–10
- `verdict` — "Correct" / "Partially correct" / "Incorrect"
- `feedback` — prose explanation
- `model_answer` — ideal answer

Verdict mapping: score ≥7 → Correct, ≥4 → Partially correct, <4 → Incorrect.

---

## Architecture

```
qec-trainer/
├── main.py
├── config.py                    MODEL, DATA_DIR, defaults
├── core/
│   ├── models.py                Problem, TrainerConfig, Attempt, SessionStats,
│   │                            GradeMode, Verdict enums
│   └── decoder_game.py          Decoder Game logic: codes, syndromes, GF(2)
│                                success verification, round generation
├── problems/
│   ├── __init__.py              all_problems(): auto-discovers one file per problem
│   ├── repetition_code/         34 problems
│   ├── stabilizer_formalism/    34 problems
│   ├── fault_tolerance/         33 problems
│   ├── steane_code/             32 problems
│   ├── surface_code/            30 problems
│   └── bosonic_codes/           15 problems
├── grading/
│   └── auto_grader.py           grade_mc(problem, answer) → Attempt (local)
├── workers/
│   └── grading_worker.py        QThread: Claude grading for GradeMode.CLAUDE problems
├── ui/
│   ├── main_window.py           Screen controller (setup → problem → result →
│   │                            summary → history)
│   ├── screens/
│   │   ├── setup_screen.py      Category/difficulty/count selection
│   │   ├── problem_screen.py    Question display, MC radio buttons or free-form box
│   │   ├── result_screen.py     Verdict, feedback, model answer
│   │   ├── summary_screen.py    Session stats
│   │   ├── history_screen.py    Past sessions table
│   │   └── decoder_screen.py    Decoder Game rounds, surface-code grid, results
│   └── widgets/
│       └── loading_overlay.py   Grading spinner
└── persistence.py
```

---

## Session Flow

```
SetupScreen
      │ session_started (TrainerConfig)
      ▼
ProblemScreen ─── answer_submitted (problem, answer_str)
      │
      ├── GradeMode.AUTO → auto_grader.grade_mc() [immediate]
      │
      └── GradeMode.CLAUDE → GradingWorker [async]
              │
              ▼
        ResultScreen ─── next_requested
              │
              ▼
        ProblemScreen (next problem)
              │ (all done)
              ▼
        SummaryScreen ─── back_requested → SetupScreen
```

---

## Configuration (`config.py`)

| Constant | Default | Effect |
|---|---|---|
| `MODEL` | `claude-sonnet-4-6` | Claude model for free-form grading |
| `DEFAULT_PROBLEM_COUNT` | 10 | Pre-filled problem count |
| `DATA_DIR` | `~/.local/share/quantum-study` | Session history directory |

---

## Data Persistence

Sessions appended to `~/.local/share/quantum-study/qec_history.json`. Each entry
records: problem count, correct count, accuracy, and per-attempt detail (problem ID,
category, difficulty, user answer, score, verdict).

---

## Adding Problems

Add a new Python file inside the appropriate `problems/<category>/` directory, defining
a single module-level `PROBLEM`:

```python
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id="unique_snake_case_id",
    category="Category Name",          # must match an existing category string
    difficulty="beginner",             # "beginner" | "intermediate" | "advanced"
    question="Question text here.",
    choices=["A text", "B text", "C text", "D text"],   # empty list for CLAUDE mode
    correct_index=0,                   # 0-based; -1 for CLAUDE mode
    explanation="Explanation shown after answering.",
    hints=["First hint.", "Second hint."],
    grade_mode=GradeMode.AUTO,         # or GradeMode.CLAUDE for free-form
)
```

`problems/__init__.py` auto-discovers every problem file, so no registration step
is needed.
