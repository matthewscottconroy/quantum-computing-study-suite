# Math for Quantum Computing Quiz

An AI-powered quiz application covering 13 mathematical subjects that underpin quantum
computing. Questions are generated on-demand by Claude (`claude-sonnet-4-6`) and graded
by Claude with structured feedback. Lighter than `quantum-quiz` — no Qiskit dependency.

---

## Features

- **13 subjects, 197 topics** — from linear algebra through topology and a dedicated
  "Quantum Connections" cross-domain subject
- **6 question types** — conceptual explanation, proof sketch, calculation, example
  construction, compare and contrast, counterexample
- **4 difficulty levels** — beginner, intermediate, advanced, expert
- **Quantum-relevance annotations** — every subject has a one-sentence note explaining
  its connection to QC; this is injected into the generation prompt so questions stay
  grounded in why the math matters
- **Subject-type supplements** — the prompt builder detects subject+type combinations
  likely to produce weak questions (e.g. "Topology & Geometry" + "calculation") and
  injects specific guidance to ensure concrete, well-formed problems
- **Hint system** — up to 3 progressive hints per question
- **Spaced repetition weighting** — past scores influence subject sampling frequency
- **Session history** — lifetime stat cards, a score-trend chart and a per-subject
  average chart built from every saved session
- **Collapsible panels** — model answer and missed key points animate open on click
- **Score bar** — animated score display with colour-coded verdict
- **Reference browser** — read the shared `docs/` corpus (all 8 chapters, 50+ Markdown
  files) inside the app; opens on Mathematical Foundations, filter by chapter or title
- **Flag for review** — bookmark any graded question from the feedback screen; flagged
  questions are listed (and can be unflagged) on the history screen and picked up by
  the suite-wide `coach.py` review queue via `math_flagged.json`

---

## Requirements

```
PyQt6>=6.5.0
anthropic>=0.25.0
matplotlib>=3.7.0
```

Install:
```bash
pip install -r requirements.txt
```

This is the lightest of the API-based quiz apps — no Qiskit, no heavy scientific stack.

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

1. **Select subjects** — all 13 checked by default; use All / None shortcuts
2. **Pick difficulty** — Randomise each question / Beginner / Intermediate / Advanced /
   Expert
3. **Pick question types** — any combination
4. **Set question count** — default 10
5. Click **Begin Session** — or **View History** / **Reference** (bottom-left) to
   review past sessions or read the docs first

### Question Screen

- Free-text answer box
- **Hint** button (up to 3 hints)
- **Skip** to advance without answering
- **Submit Answer** sends to Claude for grading

### Feedback → Summary → History

Same flow as `quantum-quiz`: feedback with score bar and collapsible model answer,
session summary with a matplotlib bar chart and per-question log (plus **Export JSON**
/ **Export Markdown**), and a history screen with lifetime stat cards (sessions,
questions, average), a score-trend chart, a per-subject average chart and the
flagged-for-review list.

- **Flag for review** (feedback screen, bottom-left) toggles a bookmark for the question
  you just answered. Click again to remove it.
- **History → Flagged for review** lists every bookmarked question (newest first, with
  subject and date). Select one and click **Unflag selected** to remove it.

### Reference

**Reference** on the setup screen opens an in-app reader for the repository's `docs/`
chapters (resolved relative to the app, `../docs`). The left pane lists every chapter
file grouped by rung; the chapter drop-down and title filter narrow the list. Relative
links between chapters navigate inside the reader; external links and **Open in external
viewer** hand off to the desktop. **← Back** returns to setup and keeps your place.

---

## Subject and Topic Inventory

| Subject | Topics |
|---|---|
| Linear Algebra | 20 — vector spaces through Schmidt decomposition, density matrices, SVD, projectors |
| Abstract Algebra | 18 — groups, Lie groups (SU(2)), finite fields, Pauli group, Clifford group, symplectic structure |
| Representation Theory | 15 — irreps, Schur's lemma, SU(2) reps, Clebsch-Gordan, hidden subgroup, QFT, Peter-Weyl |
| Complex Analysis | 15 — holomorphic functions, Cauchy, residue theorem, branch cuts, quantum phases |
| Calculus & Real Analysis | 17 — ε-δ, multivariable calculus, Lagrange multipliers, matrix calculus, semidefinite programming |
| Ordinary Differential Equations | 11 — Schrödinger as ODE, matrix exponentials, Hamiltonian systems, perturbation theory |
| Partial Differential Equations | 13 — time-dependent/independent Schrödinger, Sturm-Liouville, Wigner function, Lindblad |
| Functional Analysis | 15 — Banach/Hilbert spaces, spectral theorem, Stone's theorem, trace-class operators, quantum channels |
| Probability Theory | 12+ — expectation, conditional probability, entropy, quantum probability, Berry-Esseen |
| Fourier Analysis | 12+ — Fourier series, DFT, FFT, uncertainty principle, QFT connection |
| Number Theory | 12+ — modular arithmetic, RSA, Shor's period-finding, lattice problems |
| Topology & Geometry | 12+ — fundamental group, homotopy, Berry phase, topological QC, Chern numbers, anyons |
| Quantum Connections | Cross-domain — topics explicitly bridging two or more mathematical areas in QC research |

---

## Architecture

```
math-quiz/
├── main.py
├── config.py                    Constants: model, token limits, score thresholds, UI
├── core/
│   ├── models.py                QuizConfig, Question, Evaluation, QuestionRecord, SessionStats
│   └── topics.py                TOPICS dict + DIFFICULTY_LEVELS + QUESTION_TYPES
├── ai/
│   ├── prompt_builder.py        Assembles generation/evaluation prompts with QC relevance notes
│   └── response_parser.py       JSON fence stripping and field validation
├── workers/
│   ├── question_worker.py       QThread: topic selection → Claude → emit Question
│   └── evaluation_worker.py     QThread: grade answer → emit Evaluation
├── ui/
│   ├── main_window.py           Screen controller (6 pages)
│   ├── screens/
│   │   ├── setup_screen.py      Subject/difficulty/type configuration
│   │   ├── question_screen.py   Question display and answer entry
│   │   ├── feedback_screen.py   Score, verdict, collapsible panels, flag toggle
│   │   ├── summary_screen.py    Session chart (matplotlib)
│   │   ├── history_screen.py    Lifetime stats + flagged-for-review list
│   │   └── reference_screen.py  In-app docs/ Markdown browser
│   └── widgets/
│       ├── collapsible_panel.py Animated expand/collapse
│       ├── loading_overlay.py   Spinner overlay
│       ├── pill_badge.py        Verdict badge
│       └── score_bar.py         Animated score bar
└── persistence.py               JSON session history + flagged questions
```

---

## Prompt Engineering Details

### Quantum Relevance Injection

Every subject has a one-sentence "QC relevance" note injected into the generation
prompt. Example for Topology & Geometry:

> "Topology and geometry underlie the Berry phase, topological quantum computation, the
> toric code, anyonic statistics, and Chern number topological invariants."

This prevents Claude from generating pure-math questions with no connection to the
application domain.

### Subject-Type Supplements

Certain subject+type combinations produce weak questions without guidance. The prompt
builder detects these and adds specific instructions:

- **Topology + calculation**: must be a concrete algebraic-topology computation
  (e.g. compute π₁(T²), evaluate a Chern number)
- **Representation Theory + calculation**: must be concrete (decompose a specific rep,
  compute a character table entry)

### Difficulty Guide

| Level | Expectation |
|---|---|
| Beginner | Recall or state a definition, property, or basic fact |
| Intermediate | Apply a concept to a specific problem or scenario |
| Advanced | Derive a result, analyse structure, or compare two concepts |
| Expert | Synthesise across topics, construct a non-trivial proof, resolve a subtlety |

---

## Configuration (`config.py`)

| Constant | Default | Effect |
|---|---|---|
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Model for both generation and grading |
| `GENERATION_MAX_TOKENS` | 900 | Max tokens for question generation |
| `EVALUATION_MAX_TOKENS` | 1300 | Max tokens for grading |
| `DEFAULT_QUESTION_COUNT` | 10 | Pre-filled question count |
| `MAX_HINT_COUNT` | 3 | Hints requested from Claude and shown per question |
| `PREVIOUS_QUESTION_DEDUP_WINDOW` | 8 | Recent questions shown to Claude |
| `SCORE_CORRECT_THRESHOLD` | 7 | Score ≥ this → "Correct" |
| `SCORE_PARTIAL_THRESHOLD` | 4 | Score ≥ this → "Partially correct" |

---

## Data Persistence

Sessions are appended to `~/.local/share/quantum-study/math_history.json`. Each
session entry holds `date`, `timestamp`, `answered`, `average_score` and a `records`
list with one `{question_id, subject, topic, score, elapsed_seconds, timestamp}` per
graded question. Your answers, Claude's feedback and the model answers are not kept in
the history: they exist only in the in-progress draft (`math_draft.json`, deleted once
the session is saved) and in the JSON / Markdown exports from the summary screen.
All three files are written as UTF-8, atomically (temp file + rename).

Flagged questions live next to it in `math_flagged.json`, a JSON list using the
suite-wide flag schema (shared by every app and read by `coach.py --review`):

```json
{
  "id": "Linear Algebra::inner product spaces and Hilbert spaces#3f2a9c1d",
  "label": "Let V be a finite-dimensional inner product space. Show that ...",
  "category": "Linear Algebra",
  "app": "math-quiz",
  "timestamp": 1757400000.0
}
```

`id` is the SRS topic key (`subject::topic`) plus a short hash of the question text,
`label` is the question text truncated to 80 characters, `category` is the subject.
Flagging is a toggle: flagging an already-flagged question removes its entry.

Set `QUANTUM_STUDY_DATA_DIR` to relocate all three files (history, draft, flagged);
the default directory is unchanged.

Spaced repetition uses time-based decay with a 14-day half-life: a record from 14 days
ago carries half the weight of one from today, 28 days ago a quarter, and so on.
Subjects and topics whose decayed average score is low receive a proportionally
higher weight in future topic sampling.
