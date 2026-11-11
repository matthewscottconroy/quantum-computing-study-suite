# Math for Quantum Computing Quiz

An AI-powered quiz application covering 13 mathematical subjects that underpin quantum
computing. Questions are generated on-demand by Claude (`claude-sonnet-4-6`) and graded
by Claude with structured feedback. Lighter than `quantum-quiz` — no Qiskit dependency.

## Run

```bash
python launch.py math                 # from the repository root (or: quantum-study math)
python -m quantum_study.math_quiz
```

Needs a Claude API key (`ANTHROPIC_API_KEY`, or `~/.config/quantum-study/api_key.txt`): the questions and the grading come from Claude. Without one, only the Reference browser and the history screen work.
Setup is covered in [GETTING_STARTED.md](../../GETTING_STARTED.md).

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
  pure upside: one tap adds the cause, the text field adds a note, and
  **Next Question** is never blocked. Nothing here is modal.
- **⚠ Report a problem with this item** (feedback screen, beside the flag) opens a
  short form — what is wrong, what it should say, how bad — and then a **prefilled
  GitHub issue** in your browser, carrying the item id and the question text exactly
  as you saw it. The app sends nothing: it builds a URL and hands it to the desktop,
  and nothing is filed until you submit it there. The button is Tab-reachable, never
  blocks the drill, and on a machine with no browser the link goes to your clipboard
  and the status bar says so.

### Reference

**Reference** on the setup screen opens the suite's shared in-app reader for the
repository's `docs/` chapters (found relative to the package, then the working
directory; `QUANTUM_STUDY_DOCS_DIR` overrides it). The left pane lists every chapter
file grouped by rung; the chapter drop-down and the search box narrow the list, and
the search box matches document *text*, not just titles. **Jump to topic** opens the
chapter that covers a quiz subject — that map is `SUBJECT_DOCS` in
`ui/screens/reference_screen.py`, one entry per subject in `core/topics.py`. The
reader opens on `01_mathematical_foundations`, the rung this app drills, and
**Show solutions** hides worked answers so you can try first. Relative links between
chapters navigate inside the reader; external links and **Open externally** hand off
to the desktop. **← Back** returns to setup and keeps your place.

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

## Data files

Written under `~/.local/share/quantum-study/`, or `$QUANTUM_STUDY_DATA_DIR` if set:

| File | Holds |
|---|---|
| `math_history.json` | every finished session; read by `coach.py` and `dashboard.py` |
| `math_flagged.json` | items you flagged for review (the coach's review queue) |
| `math_draft.json` | an unsent answer, restored on the next start |
| `math_settings.json` | preferences |
| `mistakes.json`, `confidence.json` | the mistake journal and the confidence ratings, shared by all ten apps |

## Code and tests

The app is the package `quantum_study/math_quiz/`. What it shares with the other nine (the data directory, the journals, the theme, the Reference screen) is in [`quantum_study/common/`](../common/README.md).

```bash
pytest quantum_study/math_quiz        # this app's tests
```
