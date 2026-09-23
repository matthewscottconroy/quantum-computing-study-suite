# Exam Sim

A timed mock-exam simulator for **IBM certification exam C1000-179 —
"Fundamentals of Quantum Computing Using Qiskit v2.X Developer"**
(68 questions, 90 minutes, 47 correct to pass).

Fully offline: a static bank of 300 original multiple-choice questions, no API
keys, no network access. Part of the quantum-study suite (see `vqa-trainer`,
`qec-trainer`, etc.), sharing its dark theme and persistence directory.

> **Disclaimer** — The exam logistics (question count, time limit, pass mark,
> section weights) are third-party-sourced and may change; verify them against
> IBM's official exam page. Every question in the bank is **original study
> material** written for this app. None of it is real exam content, and using
> this app is not affiliated with or endorsed by IBM.

---

## Requirements

```
PyQt6>=6.6
matplotlib>=3.8
```

```bash
pip install -r requirements.txt
python main.py
```

The app itself only needs PyQt6 plus matplotlib (for the score-trend chart on
the History screen; every other screen works without it). Qiskit is not
required to *run* the app — the bank is static — but the code snippets in the
questions target qiskit 2.x + qiskit-aer and were verified by execution against
qiskit 2.5.2.

---

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
  resolved relative to the app so any checkout location works)
- Chapter filter, title search, and a **Suggested for C1000-179** view that
  maps each exam section (Create circuits, Quantum operations, …) to the
  chapters that back its objectives
- Markdown is rendered in-app (headings, tables, code blocks, display math,
  exercise solutions); the bare `NN_chapter/NN_file.md` cross-references the
  corpus writes in prose are turned into links that navigate inside the
  browser (`#heading` suffixes jump to the heading), external links and
  **Open externally** hand off to the system handler
- Opened from the **Browse Reference** button on the home screen; **← Back**
  returns

---

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

### Tests

```bash
cd exam-sim && python -m pytest        # ~12 s bank/allocation + offscreen Qt screens
```

`tests/test_mistake_journal.py` covers the Qt-free journal/confidence/settings
helpers (schema, clipping, caps, atomic writes, corrupt files) and
`tests/test_feedback_ui.py` drives the new widgets offscreen end to end
(rate → miss → tag a cause → answer it correctly → `resolved: true`), plus the
contrast and focus-ring rules above.

One test is currently marked `xfail`: `correct_index` is 0 for 261 of the
300 questions and the UI shows options in stored order, so "A" is the right
answer far more often than in a real exam. Rebalancing the bank (or shuffling
options per attempt in the UI) will flip it green.

---

## Data persistence

Shared directory `~/.local/share/quantum-study/` (a coach app integrates with
these files — schemas are stable). Set `QUANTUM_STUDY_DATA_DIR` to point the
whole suite (this app included) at a different directory, e.g. for tests or a
throwaway experiment.

`exam_history.json` — appended after every full/sprint session (the History
screen reads this file; nothing else writes it):

```json
[{"timestamp": 1724000000.0, "mode": "full", "total": 68, "correct": 51,
  "duration_secs": 4980.2,
  "sections": {"Create circuits": {"total": 12, "correct": 9}}}]
```

`exam_missed.json` — one entry per currently-missed question (deduped by id;
appended on a miss, removed when later answered correctly in Review mode).
Unchanged by the mistake journal: it still feeds `coach.py --review`, and
`mistakes.json` is written **in addition to** it, never instead:

```json
[{"question_id": "cc_depth", "section": "Create circuits",
  "question": "...", "correct_answer": "3", "chosen": "4",
  "timestamp": 1724000000.0}]
```

`mistakes.json` — the suite-wide **mistake journal** (same schema in every
app). One row per miss occurrence, so repeats are countable; `cause` is `null`
until you tag it on the results/review screen, and every row for an item flips
to `resolved: true` once the item is answered correctly:

```json
[{"id": "cc_depth", "app": "exam-sim", "category": "Create circuits",
  "question": "How deep is this circuit?", "your_answer": "4",
  "correct_answer": "3", "cause": "knew_but_slipped",
  "note": "counted the barrier", "timestamp": 1724000000.0,
  "resolved": false}]
```

`cause` is one of `misread`, `didnt_know`, `knew_but_slipped`, `confused`,
`out_of_time`, `other` — or `null` (logged, not yet categorised). The four
text fields are clipped to 200 characters.

`confidence.json` — the suite-wide **confidence-calibration** log: one row per
graded question you rated, written when the session is submitted (exam) or the
answer checked (review mode):

```json
[{"id": "cc_depth", "app": "exam-sim", "category": "Create circuits",
  "confidence": 4, "correct": false, "timestamp": 1724000000.0}]
```

`exam_settings.json` — this app's own preferences (currently just
`{"confidence_prompt": true|false}`). App-local; nothing else reads it.

All three are written atomically (temp file in the same directory +
`os.replace`, so a crash mid-write cannot truncate the journal), tolerate a
missing or corrupt file by starting fresh instead of raising, and are capped
so an append-only file cannot grow without bound — the newest
`persistence.MISTAKES_CAP` (2000) and `persistence.CONFIDENCE_CAP` (5000) rows
are kept. The pure helpers behind them (`make_mistake_entry`,
`mistake_entry_for`, `load_mistakes`, `log_mistake`, `update_mistake_cause`,
`resolve_mistake`, `record_mistakes`, `mistake_summary`, `log_confidence`,
`record_confidence`, `confidence_enabled`, …) live in `persistence.py` and are
unit-tested without Qt.

---

## Accessibility

The confidence strip, the cause chips and the note field are all keyboard
reachable (strong focus policy, `Tab` order, `1`-`4`/`0` shortcuts inside the
exam and review screens) and draw a visible focus ring — the theme adds
`:focus` rules for every button kind, radio buttons and combo boxes, widening
the border by 1 px while shrinking the padding by 1 px so focusing something
never shifts the layout.

Nothing new signals meaning by colour alone: a selected chip gains a `✓`
glyph, correct/incorrect lines are prefixed `✓`/`✗` as well as coloured, the
"Logged as …" confirmation is text, and a flagged question in the navigator
gets a **dashed** border alongside its colour (the legend says so). Every new
control carries an accessible name, and question navigator buttons announce
their state ("Question 7: answered, flagged, confidence 2 of 4").

New text was checked against the dark palette: chip label 12.9:1, selected
chip 7.5:1, prompts 6.2:1 on the background and 5.6:1 inside a card,
confirmation line 6.8:1 — all above the 4.5:1 minimum, asserted in
`tests/test_feedback_ui.py`.

---

## Architecture

```
exam-sim/
├── main.py
├── config.py                  exam logistics, section weights, data paths
├── core/
│   └── models.py              Question, ExamAttempt, ExamResult
├── bank/
│   ├── __init__.py            auto-discovery + weighted exam-set builder
│   ├── create_circuits/       54 questions (one file each, id == file stem)
│   ├── quantum_operations/    48
│   ├── run_circuits/          45
│   ├── sampler/               36
│   ├── estimator/             36
│   ├── visualization/         33
│   ├── results_analysis/      30
│   └── openqasm/              18
├── persistence.py             exam_history.json / exam_missed.json +
│                              mistakes.json / confidence.json / settings
├── tests/                     pytest suite: bank shape, allocation, persistence, offscreen screens
└── ui/
    ├── theme.py               dark theme (mirrors vqa-trainer) + focus rings
    ├── feedback.py            ConfidenceStrip + CauseRow (shared by 3 screens)
    ├── format.py              fenced-code → HTML rendering
    ├── main_window.py         screen controller
    └── screens/
        ├── home_screen.py       mode picker, history + journal summary, prompt toggle
        ├── exam_screen.py       timer, navigator, flag/skip/return, confidence strip
        ├── results_screen.py    pass bar, section table, review pane + cause rows
        ├── review_screen.py     re-answer missed questions (confidence + causes)
        ├── history_screen.py    attempts table, per-section accuracy, score-trend chart
        └── reference_screen.py  in-app docs browser (renders <repo>/docs/**/*.md)
```
