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
- **Mistake journal** — a wrong answer (graded below 4/10) is recorded in the
  suite-wide `mistakes.json` together with *why* it was wrong: one tap on
  Misread / Didn't know / Knew but slipped / Confused / Ran out of time / Other,
  plus an optional one-line note. A bookmark tells you *what* to revisit; the cause
  tells you the pattern ("nine little-endian slips this month"). Answering the same
  question correctly later resolves the entry
- **Confidence calibration** — rate how sure you are (1 guessing → 4 certain) *before*
  submitting, and the rating is paired with the grade in the suite-wide
  `confidence.json`. This is what surfaces the topics you are *confidently wrong*
  about — the unknown unknowns that sink an exam. Entirely optional, and "Don't ask"
  turns it off for good

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
- **How sure are you?** — an optional 1–4 confidence strip above the buttons
  (1 Guessing · 2 Unsure · 3 Fairly sure · 4 Certain). Rate before you submit, or
  ignore it; clicking the chosen chip again clears it. **Don't ask** hides the strip
  permanently — re-enable it under **Study aids** on the setup screen
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
- **What went wrong?** appears on the feedback screen whenever the grade is below
  4/10. The mistake is already journalled by then (with `cause: null`), so the row is
  pure upside: one tap adds the cause, the text field adds a one-line note, and
  **Next Question** is never blocked. Nothing here is modal.

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
│   │   ├── setup_screen.py      Subject/difficulty/type configuration + study aids
│   │   ├── question_screen.py   Question display, answer entry, confidence strip
│   │   ├── feedback_screen.py   Score, verdict, collapsible panels, flag + mistake row
│   │   ├── summary_screen.py    Session chart (matplotlib)
│   │   ├── history_screen.py    Lifetime stats + flagged-for-review list
│   │   └── reference_screen.py  In-app docs/ Markdown browser
│   └── widgets/
│       ├── collapsible_panel.py Animated expand/collapse
│       ├── loading_overlay.py   Spinner overlay
│       ├── chip_button.py       Checkable pill (confidence + mistake-cause chips)
│       ├── pill_badge.py        Verdict badge
│       └── score_bar.py         Animated score bar
└── persistence.py               JSON history, flags, mistake journal, confidence, settings
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

### Mistake journal — `mistakes.json`

Every app in the suite appends to this one file, so the journal is suite-wide:

```json
{
  "id": "fee39328a8253945",
  "app": "math-quiz",
  "category": "Linear Algebra",
  "question": "State the spectral theorem for Hermitian operators.",
  "your_answer": "Every Hermitian operator is unitary.",
  "correct_answer": "the model answer",
  "cause": "confused",
  "note": "mixed up Hermitian and unitary",
  "timestamp": 1757400000.0,
  "resolved": false
}
```

- `id` — SHA-1 (16 hex chars) of `subject` + the whitespace-collapsed question text, so
  the same question re-worded across lines is still the same item. The topic is
  deliberately *not* part of it.
- `category` — the subject.
- `cause` — `misread`, `didnt_know`, `knew_but_slipped`, `confused`, `out_of_time`,
  `other`, or `null` (logged but not yet categorised).
- `question`, `your_answer`, `correct_answer` and `note` are collapsed to one line and
  truncated to 200 characters.
- A wrong answer is written **immediately** with `cause: null`, so skipping the
  "what went wrong?" row never loses the mistake. Choosing a cause updates that same
  entry. Missing the same item again while it is still open updates it rather than
  duplicating it.
- `resolved` flips to `true` when the same item (matched on `app` + `id`) is later
  graded ≥ `SCORE_CORRECT_THRESHOLD`. Missing it again after that opens a fresh entry.

### Confidence calibration — `confidence.json`

Also suite-wide, one row per rated answer:

```json
{
  "id": "fee39328a8253945",
  "app": "math-quiz",
  "category": "Linear Algebra",
  "confidence": 4,
  "correct": false,
  "timestamp": 1757400000.0
}
```

`confidence` is 1 = guessing, 2 = unsure, 3 = fairly sure, 4 = certain, always chosen
before the answer is submitted. `correct` is `score >= SCORE_CORRECT_THRESHOLD` (7/10).
`id` is the same item id as the journal uses, so the two files join on `app` + `id`.
`persistence.confidently_wrong_counts()` reads the "rated ≥ 3 and still wrong" rows —
the unknown unknowns.

### App settings — `math_settings.json`

`{"confidence_prompt": true}` — this app's own preferences, new file, nothing else
touched. It remembers the **Don't ask** opt-out so the strip is never shown again
until it is re-enabled from the setup screen.

Both new files tolerate a missing or corrupt file (they start fresh rather than
crashing) and are written as UTF-8 atomically (temp file + `os.replace`). Each is
capped at its newest 5 000 rows — the cap is on the whole shared file, not per app,
so the journal cannot grow without bound however many apps append to it.

Set `QUANTUM_STUDY_DATA_DIR` to relocate every file above (history, draft, flagged,
mistakes, confidence, settings); the default directory is unchanged.

Spaced repetition uses time-based decay with a 14-day half-life: a record from 14 days
ago carries half the weight of one from today, 28 days ago a quarter, and so on.
Subjects and topics whose decayed average score is low receive a proportionally
higher weight in future topic sampling.

---

## Accessibility

The confidence strip, the mistake-cause chips and the note field are all keyboard
reachable (Tab/Space) with a 2 px accent focus ring, and each carries an accessible
name — e.g. "Confidence 4 of 4: Certain", "Cause of mistake: Knew but slipped". No
new control encodes meaning in colour alone: a chip's leading glyph flips from "○"
to "✓" and its label goes bold as well as gaining the accent border, and the state is
mirrored into the accessible description (both states carry a glyph, so selecting one
never shifts or elides its label). Chip text stays `#e6edf3` in both states — 12.9:1 on the
unselected fill and 9.4:1 on the accent-tinted selected fill, against a 4.5:1
requirement (there is a unit test for this in
`tests/test_mistakes_confidence.py`).
