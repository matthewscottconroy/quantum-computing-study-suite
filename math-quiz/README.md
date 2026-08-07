# Math for Quantum Computing Quiz

An AI-powered quiz application covering 13 mathematical subjects that underpin quantum
computing. Questions are generated on-demand by Claude (`claude-sonnet-4-6`) and graded
by Claude with structured feedback. Lighter than `quantum-quiz` — no Qiskit dependency.

---

## Features

- **13 subjects, 197 topics** — from linear algebra through topology and a dedicated
  "Quantum Connections" cross-domain subject
- **4 question types** — conceptual explanation, calculation, proof sketch, comparison
- **4 difficulty levels** — beginner, intermediate, advanced, expert
- **Quantum-relevance annotations** — every subject has a one-sentence note explaining
  its connection to QC; this is injected into the generation prompt so questions stay
  grounded in why the math matters
- **Subject-type supplements** — the prompt builder detects subject+type combinations
  likely to produce weak questions (e.g. "Topology & Geometry" + "calculation") and
  injects specific guidance to ensure concrete, well-formed problems
- **Hint system** — up to 3 progressive hints per question
- **Spaced repetition weighting** — past scores influence subject sampling frequency
- **Session history** — full record of every session with per-subject score breakdown
- **Collapsible panels** — model answer and missed key points animate open on click
- **Score bar** — animated score display with colour-coded verdict

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
2. **Pick difficulty** — Beginner / Intermediate / Advanced / Expert / Mixed
3. **Pick question types** — any combination
4. **Set question count** — default 10
5. Click **Start Quiz**

### Question Screen

- Free-text answer box
- **Hint** button (up to 3 hints)
- **Skip** to advance without answering
- **Submit Answer** sends to Claude for grading

### Feedback → Summary → History

Same flow as `quantum-quiz`: feedback with score bar and collapsible model answer,
session summary with matplotlib bar chart, history table with per-question detail.

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
│   ├── main_window.py           Screen controller (5 pages)
│   ├── screens/
│   │   ├── setup_screen.py      Subject/difficulty/type configuration
│   │   ├── question_screen.py   Question display and answer entry
│   │   ├── feedback_screen.py   Score, verdict, collapsible panels
│   │   ├── summary_screen.py    Session chart (matplotlib)
│   │   └── history_screen.py    Past session table
│   └── widgets/
│       ├── collapsible_panel.py Animated expand/collapse
│       ├── loading_overlay.py   Spinner overlay
│       ├── pill_badge.py        Verdict badge
│       └── score_bar.py         Animated score bar
└── persistence.py               JSON session history
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
| `MAX_HINT_COUNT` | 3 | Maximum hints per question |
| `PREVIOUS_QUESTION_DEDUP_WINDOW` | 8 | Recent questions shown to Claude |
| `SCORE_CORRECT_THRESHOLD` | 7 | Score ≥ this → "Correct" |
| `SCORE_PARTIAL_THRESHOLD` | 4 | Score ≥ this → "Partially correct" |

---

## Data Persistence

Sessions are appended to `~/.local/share/quantum-study/math_quiz_history.json`.
Each record contains: timestamp, subjects, difficulty, question count, average score,
and per-question detail (subject, topic, user answer, score, feedback, model answer).

SRS decay factor: 0.88 per session (same as quantum-quiz). Subjects where you scored
poorly recently receive a proportionally higher weight in future topic sampling.
