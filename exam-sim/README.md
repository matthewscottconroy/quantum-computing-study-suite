# Exam Sim

A timed mock-exam simulator for **IBM certification exam C1000-179 —
"Fundamentals of Quantum Computing Using Qiskit v2.X Developer"**
(68 questions, 90 minutes, 47 correct to pass).

Fully offline: a static bank of 300 original multiple-choice questions, no API
keys, no network access. Part of the quantum-study suite (see `vqa-trainer`,
`qec-trainer`, etc.): the dark theme, the mistake/confidence journal, the data
directory, the schema versioning and the Reference browser all come from the
repository's shared [`common/`](../common/README.md) package rather than from a
copy kept here — see [Shared code](#shared-code-common) below.

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

| file | covers |
|---|---|
| `test_bank.py` / `test_allocation.py` | bank shape, ids, weighted draw |
| `test_config_and_models.py` | exam logistics, the data-dir override |
| `test_persistence.py` | `exam_history.json` / `exam_missed.json` round-trips |
| `test_mistake_journal.py` | the journal adapter: Question → row, the session journal, caps, corrupt files, foreign rows |
| `test_schema_versioning.py` | the sidecar on every file, an unmarked file reading as v1, forward migration, a newer file refused, backup rotation |
| `test_errata_ui.py` | the report control: what it quotes, the URL fields, browser stubbed and browser absent, where the button is (and is not) |
| `test_common_package.py` | the shim is verbatim, every module that imports `common` imports it first, nothing imports `journal_sync`, the palette and journal are the shared ones, and `trim_own` no longer eats another app's rows |
| `test_feedback_ui.py` | the widgets offscreen end to end (rate → miss → tag a cause → answer it correctly → `resolved: true`) plus contrast and focus rings |
| `test_history_screen.py` / `test_reference_screen.py` | the two read-only screens against the live corpus |

The root suite (`tests/test_common_*.py`, run by `tools/run_tests.sh`) owns the
unit tests for `common/` itself, so they are not repeated here.

One test is currently marked `xfail`: `correct_index` is 0 for 261 of the
300 questions and the UI shows options in stored order, so "A" is the right
answer far more often than in a real exam. Rebalancing the bank (or shuffling
options per attempt in the UI) will flip it green.

---

## Data persistence

Shared directory `~/.local/share/quantum-study/` (a coach app integrates with
these files — schemas are stable). Set `QUANTUM_STUDY_DATA_DIR` to point the
whole suite (this app included) at a different directory, e.g. for tests or a
throwaway experiment. The directory is resolved by `common.datadir` **at call
time**, so setting the variable takes effect immediately, in this process and
in any subprocess — nothing is frozen at import.

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
`out_of_time`, `other` — or `null` (logged, not yet categorised; an
unrecognised value is stored as `null` rather than costing you the mistake).
`category`, `question`, `your_answer` and `correct_answer` are collapsed to one
line and clipped to 200 characters; `note` keeps its line breaks and is clipped
to 500.

`confidence.json` — the suite-wide **confidence-calibration** log: one row per
graded question you rated, written when the session is submitted (exam) or the
answer checked (review mode):

```json
[{"id": "cc_depth", "app": "exam-sim", "category": "Create circuits",
  "confidence": 4, "correct": false, "timestamp": 1724000000.0}]
```

`exam_settings.json` — this app's own preferences (currently just
`{"confidence_prompt": true|false}`). App-local; nothing else reads it.

Every one of these files is written through `common.journal` /
`common.schema`, which means:

- **Locked and atomic.** The read-modify-write of a shared journal runs inside
  an advisory lock on a `<name>.lock` sidecar and re-reads the file inside the
  lock, then writes via a temp file + `os.replace`. Ten apps can be open at
  once without losing a row.
- **Other apps' rows are never touched.** A rewrite puts every row this app
  does not own back exactly as it was read, unknown keys included — and the
  growth cap (`common.journal.MISTAKES_MAX` 2000, `CONFIDENCE_MAX` 5000) drops
  only **exam-sim's own** oldest rows. The copy this app used to carry trimmed
  the merged list, which deleted other apps' history during our write; that bug
  is gone.
- **Versioned.** Each file gets a sidecar `<name>.schema.json`
  (`{"file", "kind", "schema", "written_by", "updated"}`). A *sidecar* and not
  a key inside the data, because `coach.py` and `dashboard.py` require the top
  level of these files to be a plain JSON list — a `{"schema": 1, "rows": […]}`
  wrapper would make the journal read as empty everywhere. A file with no
  sidecar is a v1 file, so nothing had to be converted.
- **Refused, not corrupted.** A file written by a *newer* build is left alone
  instead of being overwritten with this build's narrower view of it;
  `persistence.last_write_error()` reports the refusal and nothing raises into a
  running exam.
- **Backed up.** The first write of each process rotates `<name>.bak` →
  `.bak.1` → `.bak.2` (three generations, best-effort);
  `common.schema.restore_backup()` puts one back.
- **Forgiving.** A missing or corrupt file reads as empty rather than raising.

The app-shaped helpers (`make_mistake_entry`, `mistake_entry_for`,
`load_mistakes`, `log_mistake`, `update_mistake_cause`, `resolve_mistake`,
`record_mistakes`, `mistake_summary`, `log_confidence`, `record_confidence`,
`confidence_enabled`, …) still live in `persistence.py`, are unit-tested
without Qt, and keep their signatures; the store underneath them is the shared
one.

---

## Shared code (`common/`)

exam-sim used to carry its own copy of the data-directory resolver, the
mistake/confidence journal, the cross-process lock, the theme palette and a
615-line docs Reference screen. All five are now the repository's
[`common/`](../common/README.md) package, one implementation for all ten apps.

| was here | is now |
|---|---|
| `ui/theme.py` (139 lines) | `common.ui.theme` + 95 lines of exam-sim's own: `SECTION_COLORS`, the `#nav` navigator buttons, the `#chip` pills, the history tables |
| `ui/screens/reference_screen.py` (615 lines) | `common.ui.reference.ReferenceScreen` + a 235-line subclass holding `SECTION_DOCS`, the ★ Suggested filter and the "exam sections" annotation |
| the journal half of `persistence.py` | `common.journal` (locked, atomic, foreign rows preserved, own-rows-only trim) |
| `DATA_DIR`/`HISTORY_FILE`/… frozen at import | `common.datadir`, resolved at call time |
| hand-rolled `write_text` for history/missed/settings | `common.schema.save_versioned` (versioned, backed up, atomic) |
| `journal_sync.py` | `common.locking` |

### The import shim

The apps are not packages — several define the same top-level module names
(`config`, `core`, `ui`, `persistence`) — so the repository root is not
importable from inside one. `common_path.py` is a **verbatim** copy of
`common/app_shim.py`; it locates the checkout from its own `__file__` and
**appends** the root to `sys.path` (appends, so a root module such as `tests`
can never shadow an app module). Every module here that imports `common`
imports it first:

```python
import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import journal
```

`tests/test_common_package.py` asserts both halves of that rule, because a
module that assumes something else ran the shim first works right up until the
day something imports it first.

### Behaviour reconciled with the other nine apps

The shared versions settle a handful of differences the ten copies had drifted
into (the full table is in `common/README.md` §3). Four of them are visible
here:

- **Cause labels.** `knew_but_slipped` now reads **"Knew but slipped"** and
  `confused` reads **"Confused"** — the wording seven of the ten apps used.
  exam-sim's "Knew it, slipped" / "Confused two things" were a local rewrite.
  The stored `cause` keys are unchanged, so nothing on disk moved.
- **An unknown cause no longer raises.** `make_mistake_entry(cause="nonsense")`
  stores `null` instead of `ValueError`: a stray label must not cost the
  mistake itself. A recognised cause still survives spacing and case.
- **A confidence rating outside 1-4 is rejected, not invented.**
  `log_confidence` records nothing and returns `None` (the pure builder still
  clamps, so a row that exists is always schema-valid).
- **Notes are 500 characters and keep their line breaks** (the one-line fields
  are still collapsed and clipped to 200). The note box in the UI still caps
  typing at 200.

Two things deliberately did **not** move:

- **`common.flags`.** exam-sim has no persisted flag store — "Flag for review"
  is an in-session marker on `ExamAttempt`, and misses reach the coach through
  `exam_missed.json` and `mistakes.json`. There was nothing to de-duplicate.
- **`ui/feedback.py`, `ui/format.py`, the screens and the graders.** They look
  like other apps' and are not: each encodes this app's session model.

`journal_sync.py` is still in the tree but is no longer imported by anything
here; it stays only because `tests/test_journal_concurrency.py` requires all
ten copies to be present and byte-identical. It should be deleted from all ten
apps in the commit that updates that test.

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
their state ("Question 7: answered, flagged, confidence 2 of 4"). The
**⚑ Report a problem with this item** button follows the same rules — strong
focus policy, accessible name, the theme's focus ring — and its no-browser
fallback is shown non-modally so it can never trap keyboard focus.

New text was checked against the dark palette: chip label 12.9:1, selected
chip 7.5:1, prompts 6.2:1 on the background and 5.6:1 inside a card,
confirmation line 6.8:1 — all above the 4.5:1 minimum, asserted in
`tests/test_feedback_ui.py`.

---

## Architecture

```
exam-sim/
├── main.py
├── common_path.py             the import shim, verbatim from common/app_shim.py
├── config.py                  exam logistics, section weights, data paths
│                              (resolved at call time via common.datadir)
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
├── persistence.py             exam_history.json / exam_missed.json + the
│                              common.journal adapter, all schema-versioned
├── journal_sync.py            superseded by common.locking; unused here
├── tests/                     pytest suite: bank shape, allocation, persistence, offscreen screens
└── ui/
    ├── theme.py               common.ui.theme + this app's own rules/colours
    ├── errata.py              "report this item" over common.ui.errata_dialog
    ├── feedback.py            ConfidenceStrip + CauseRow (shared by 3 screens)
    ├── format.py              fenced-code → HTML rendering
    ├── main_window.py         screen controller
    └── screens/
        ├── home_screen.py       mode picker, history + journal summary, prompt toggle
        ├── exam_screen.py       timer, navigator, flag/skip/return, confidence strip
        ├── results_screen.py    pass bar, section table, review pane + cause rows + report
        ├── review_screen.py     re-answer missed questions (confidence, causes, report)
        ├── history_screen.py    attempts table, per-section accuracy, score-trend chart
        └── reference_screen.py  common.ui.reference + SECTION_DOCS / ★ Suggested
```
