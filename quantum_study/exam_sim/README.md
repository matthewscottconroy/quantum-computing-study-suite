# Exam Sim

A timed mock-exam simulator for **IBM certification exam C1000-179 —
"Fundamentals of Quantum Computing Using Qiskit v2.X Developer"**
(68 questions, 90 minutes, 47 correct to pass).

Fully offline: a static bank of 300 original multiple-choice questions, no API
keys, no network access. Part of the quantum-study suite (see `vqa-trainer`,
`qec-trainer`, etc.): the dark theme, the mistake/confidence journal, the data
directory, the schema versioning and the Reference browser all come from the
repository's shared [`quantum_study/common/`](../common/README.md) package rather than from a
copy kept here.

> **Disclaimer** — The exam logistics (question count, time limit, pass mark,
> section weights) are third-party-sourced and may change; verify them against
> IBM's official exam page. Every question in the bank is **original study
> material** written for this app. None of it is real exam content, and using
> this app is not affiliated with or endorsed by IBM.

## Run

```bash
python launch.py exam                 # from the repository root (or: quantum-study exam)
python -m quantum_study.exam_sim
```

Fully offline; it never calls the API.
Setup is covered in [GETTING_STARTED.md](../../GETTING_STARTED.md).

## Modes

### Full exam
- 68 questions drawn from the bank **proportionally to the exam section
  weights** (largest-remainder allocation, randomized order)
- 90-minute countdown, always visible (turns red under 5 minutes; auto-submits
  at zero)
- Question navigator: jump to any question, **flag** for review, skip and
  return; answered/flagged/unanswered states are colour-coded, and flagged
  also draws a dashed border so the state survives without colour vision.
  The in-exam flag only marks a question to return to before submitting and
  is **never persisted** — exam-sim is the one suite app without a `*_flagged.json`
  review-flag file; missed questions feed the suite review queue
  (`coach.py --review`) through `exam_missed.json` instead
- **No per-question feedback** during the exam
- **Confidence strip** under the options: rate how sure you are (1 guessing /
  2 unsure / 3 fairly sure / 4 certain) with keys `1`-`4` (`0` clears), or by
  clicking a chip. Optional, per question, and asked *before* anything is
  revealed, so it can never be hindsight; **Hide** turns it off for good (turn
  it back on from the home screen). The rating is paired with right/wrong at
  submit time and written to `confidence.json` — that pairing is what finds
  *confidently wrong* topics, the unknown unknowns that sink exam scores
- On submit: results screen with score vs the 47/68 pass bar, a per-section
  table (your % vs exam weight), and a review pane walking every missed
  question with its explanation
- Every miss is also written to the **mistake journal** (`mistakes.json`) and
  each review card carries a compact, skippable **"What went wrong?"** row:
  one chip per cause (misread / didn't know / knew it, slipped / confused two
  things / out of time / other) plus an optional one-line note. Skipping is
  fine — the miss is logged with `cause: null` either way, so nothing is lost;
  tagging it turns a flagged question into analysis ("nine little-endian slips
  this month"). Answering the same question correctly later flips every row
  for it to `resolved: true` without discarding the cause

### Sprint
- Pick one section, 10 questions, 10-minute timer
- Same results/review flow (pass bar scaled to the 47/68 ratio)

### Review mode
- Browse previously missed questions (from `exam_missed.json`) and re-answer
  them with immediate feedback
- Answer one correctly and it is removed from the missed list; miss it again
  and it stays (timestamp refreshed)
- The same confidence strip (before **Check Answer**) and the same
  "What went wrong?" row (on an incorrect answer) as the exam flow

### Report a problem with this item
- A **⚑ Report a problem with this item** button sits on every missed-question
  card on the results screen and in the review screen's feedback area — the
  two places a question is shown *after* it has been graded. It is deliberately
  **not** on the timed exam runner: nothing may spend exam time or reveal that
  a question is disputed while the clock runs
- It opens a three-field form (what is wrong / what it should say / how bad),
  then a **prefilled GitHub issue** in your browser: the bank file, the
  question id, the question exactly as you saw it (options marked "keyed
  correct" and "your answer"), and your comment. Nothing is sent from the app —
  you read and submit the issue yourself
- Keyboard reachable like every other control, and it never blocks: the URL
  goes to `QDesktopServices.openUrl`, which returns immediately. On a machine
  with no browser the URL is copied to the clipboard and shown in a non-modal
  box you can copy from, so the report is not lost
- The dialog and the URL builder are shared (`common.ui.errata_dialog` over
  `common.errata`); `ui/errata.py` is the exam-sim wiring

### Home screen
- A one-line **mistake-journal readout**: how many of this app's mistakes are
  still open, the most common cause among them, and how many are still
  untagged
- **Confidence prompt: on/off** toggle — the same opt-out the **Hide** button
  writes, so a user who dislikes the prompt is never asked again

### History
- Reads `exam_history.json` (read-only — the schema below is untouched)
- Stat cards: sessions, full exams, best full score, full-exam pass rate
- **Score trend** chart (matplotlib): every attempt in chronological order,
  full exams and sprints as separate series, with the 47/68 pass mark drawn
  as a reference line
- **Past attempts** table: date, mode (sprints show their section), score,
  PASS/FAIL against the 47/68 ratio scaled to the session length, duration
- **Per-section accuracy** table aggregated over full exams only (sprints
  sample a single section, so they are excluded), with the exam weight of
  each section alongside
- Opened from the **View History** button on the home screen; **Back to Home**
  returns

### Reference
- In-app browser for the shared study-suite docs corpus (`<repo>/docs/**/*.md`,
  resolved at call time, so any checkout location works and
  `QUANTUM_STUDY_DOCS_DIR` can override it)
- The browser itself is `common.ui.reference` — one implementation for all ten
  apps. Chapter filter, full-text search, a **Show solutions** toggle, and a
  **Jump to topic** picker that opens the chapter backing an exam section
- **★ Suggested for C1000-179** (the checkbox in the top bar) narrows the list
  to the twelve chapters that back an objective; each one's tooltip and its
  header line name the sections that suggest it (`exam sections: Estimator`).
  The map lives in `ui/screens/reference_screen.py` as `SECTION_DOCS`
- Markdown is rendered in-app (headings, tables, code blocks, display math,
  exercise solutions); the bare `NN_chapter/NN_file.md` cross-references the
  corpus writes in prose are turned into links that navigate inside the
  browser (`#heading` suffixes jump to the heading), external links and
  **Open externally** hand off to the system handler
- Opened from the **Browse Reference** button on the home screen; **← Back**
  returns

## Question bank

300 questions across the exact C1000-179 objective sections. Each section's
share of the bank tracks its exam weight (the `config.SECTIONS` numbers,
20/18/16/13/13/12/11/7). Every section holds at least four full exams' worth
of questions (draws are independent, so repeats across sessions are possible
but rare) and comfortably more than one 10-question sprint (OpenQASM, the
smallest, has 18):

| Section | Questions | Share of bank | Exam weight | Per full exam (of 68) |
|---|---|---|---|---|
| Create circuits | 54 | 18.0 % | 18.2 % | 12 |
| Quantum operations | 48 | 16.0 % | 16.4 % | 11 |
| Run circuits | 45 | 15.0 % | 14.5 % | 10 |
| Sampler | 36 | 12.0 % | 11.8 % | 8 |
| Estimator | 36 | 12.0 % | 11.8 % | 8 |
| Visualization | 33 | 11.0 % | 10.9 % | 8 |
| Results analysis | 30 | 10.0 % | 10.0 % | 7 |
| OpenQASM | 18 | 6.0 % | 6.4 % | 4 |
| **Total** | **300** | | | **68** |

Style mimics associate-level exam items: a short Qiskit 2.x code snippet plus
"what is the output / which line is wrong / which option completes this", with
plausible distractors (off-by-one qubit indices, big-endian assumptions,
V1-primitive idioms, removed APIs such as `execute`, `qiskit.Aer`,
`bind_parameters`, `c_if`, `quasi_dists`). Code snippets target qiskit 2.x +
qiskit-aer (2.5.2 at the time of writing). The original 110-question core was
verified by executing every snippet against qiskit 2.5.2 (one question, the
IBM Runtime ISA-circuit requirement, against the Qiskit / Runtime docs
instead), and `CONTRIBUTING.md` requires the same of every addition,
including the September 2026 expansion to 300: a printed output goes in the
bank only after the code has been run and the output confirmed.

### Bank format

One file per question under `bank/<section_dir>/`, auto-discovered — no
registration step. The section directory is the section name lower-cased with
spaces as underscores (`Results analysis` → `results_analysis/`), the file
stem **is** the question id, and the id starts with the section's two-letter
prefix (`cc_` `qo_` `rc_` `sa_` `es_` `vz_` `ra_` `oq_`):

```python
"""Question: cc_example"""
from core.models import Question

QUESTION = Question(
    id="cc_example",                  # unique across the bank; == file stem
    section="Create circuits",        # one of the 8 exact section names
    question="What does this print?\n\n```python\nprint(1 + 1)\n```",
    options=["2", "11", "1", "It raises TypeError"],   # exactly 4, distinct
    correct_index=0,
    explanation="Why the answer is right and the distractors are wrong.",
    difficulty="easy",                # easy | medium | hard
)
```

A fenced ``` block inside `question` is rendered monospace in the UI.

Adding a question is one new file plus bumping `BANK_TOTAL` in
`tests/test_bank.py`. The loader silently skips a file that fails to import,
so run the tests after adding one — `test_every_question_file_loads` reports
the actual exception. The other bank tests check shape rather than exact
counts: every section present and at least sprint-sized, each section's share
of the bank within 2 percentage points of its exam weight, unique ids that
match their file names and section prefixes, four distinct options, a valid
`correct_index`, a substantive explanation, balanced code fences, and no two
questions with identical text or with the same snippet and answer.

`correct_index` is 0 for 261 of the 300 questions, which no longer matters:
the exam and review screens shuffle the options for every attempt
(`common.choices`), and `chosen_index` is always recorded as a bank index, so
nothing on disk depends on the order shown. `test_option_shuffle.py` drives
the real screens — including an "always pick the first row" run of a full
mock, which must fail the 47 pass mark — and `test_bank.py` rejects any
option that refers to another by letter or position.

## Data files

Written under `~/.local/share/quantum-study/`, or `$QUANTUM_STUDY_DATA_DIR` if set:

| File | Holds |
|---|---|
| `exam_history.json` | every finished session; read by `coach.py` and `dashboard.py` |
| `exam_missed.json` | missed questions waiting in Review mode |
| `exam_settings.json` | preferences |
| `mistakes.json`, `confidence.json` | the mistake journal and the confidence ratings, shared by all ten apps |

## Code and tests

The app is the package `quantum_study/exam_sim/`. What it shares with the other nine (the data directory, the journals, the theme, the Reference screen) is in [`quantum_study/common/`](../common/README.md).

```bash
pytest quantum_study/exam_sim        # this app's tests
```
