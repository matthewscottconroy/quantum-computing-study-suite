# Paper Drill

Paste any quantum computing research paper (or any text) and Paper Drill generates
comprehension questions using Claude, then grades your answers. Designed for active
reading — instead of highlighting passively, you answer targeted factual, conceptual,
and derivation questions about what you just read.

---

## Features

- **Dynamic question generation** — Claude generates questions tailored to the specific
  paper you provide; no fixed question bank
- **Three question types** — factual (recall), conceptual (understanding), derivation
  (follow the math)
- **Open-ended grading** — Claude grades each answer on a 0–10 scale with detailed
  feedback and a model answer
- **Configurable question count** — 1–15 questions per session (default 5)
- **Session history** — every completed session with title, question count,
  per-question scores, and average score
- **Grading failure recovery** — if Claude grading fails, a dialog offers to skip the
  question with a score of 0 and continue, or to stay on the same question and retry
- **Paper truncation** — papers longer than 12,000 characters are truncated before
  sending to Claude (fits within context limits while keeping token costs predictable)
- **Flag for review** — mark any graded question for later review; flagged questions are
  listed (and can be unflagged) on the History screen and picked up by `coach.py`
- **Mistake journal** — a wrong answer (score < 4) is logged to the suite-wide
  `mistakes.json` the moment it is graded, and a compact **What went wrong?** row offers
  one click to say *why*: misread / didn't know / knew but slipped / confused / out of
  time / other, plus an optional one-line note. Skipping it is free — the mistake is
  already on record, uncategorised. The point is the pattern: "six misreads this month"
  is a study plan, nine flagged questions are not
- **Confidence calibration** — an optional 1–4 self-rating (**guessing → certain**) taken
  *before* Submit, paired with the grade in the suite-wide `confidence.json`. It separates
  "right" from "right and knew it", and surfaces the **confidently wrong** topics — the
  unknown unknowns that sink exam scores. One click on **Don't ask again** retires the
  strip for good
- **Reference browser** — read the shared `docs/` corpus (every chapter, rendered from
  markdown) inside the app without leaving your drill session
- **Report a problem with this item** — a generated question that is wrong, ambiguous or
  unanswerable from the paper now has a path from *"this is wrong"* to a fix: one control
  on the Feedback screen opens a **prefilled GitHub issue** carrying the item id, the
  question exactly as it was shown, your description and an optional correction. Nothing
  is sent from the app — the issue form opens in your browser and you submit it
- **Versioned, backed-up data** — every file the app writes carries a schema version in a
  sidecar, migrates forward when the format changes, is **refused rather than
  downgraded** if a newer build wrote it, and is copied to a rotating `.bak` before the
  first write of each session

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

---

## API Key

Set `ANTHROPIC_API_KEY` in your environment, or write the key to
`~/.config/quantum-study/api_key.txt`. Both generation and grading require an API key.
The app itself launches without one — the Reference browser, Library, and History all
work offline; only **Generate Questions** needs the key.

---

## Running

```bash
python main.py
```

## Tests

```bash
cd paper-drill && python -m pytest
```

195 tests. They run Qt offscreen, stub the Anthropic client, and point
`QUANTUM_STUDY_DATA_DIR` at a temp directory, so they need no API key, no network, and
never touch `~/.local/share/quantum-study/`. The `data_dir` fixture asserts that every
one of this app's six path helpers lands inside that temp directory, so a store added
later that forgets to go through `common.datadir` fails the suite rather than quietly
writing to your real study history.

| File | Covers |
|---|---|
| `test_config.py` | the data-directory rule, resolved at call time |
| `test_persistence.py` | session history and the paper library |
| `test_flagging.py` | the flag contract, legacy bare-id upgrade, unknown rows surviving a rewrite |
| `test_learning_signals.py` | the journal and calibration stores, foreign rows, caps |
| `test_learning_ui.py` | the confidence strip and the "What went wrong?" row, driven headlessly |
| `test_screens.py` | the session flow, grading-failure recovery, history, Reference |
| `test_errata.py` | the report control: URL, keyboard, never blocking, no-browser fallback |
| `test_schema_versioning.py` | sidecars, forward migration, refused downgrades, rotating backups |
| `test_common_migration.py` | the shim is unedited and works three ways; the forked copies are gone |
| `test_parser.py`, `test_prompts.py`, `test_models_and_app.py` | generation/grading prompts, parsing, models |

---

## Usage

### Paper Input Screen

1. **Paste your paper** — paste the text of a paper, abstract, or any document into the
   large text area. PDFs should be converted to text first (e.g. `pdftotext` or copy
   from a PDF viewer).
2. **Paper title** — type a short title used to label sessions in history
3. **Question count** — how many questions to generate (default 5)
4. Click **Generate Questions** — a loading overlay appears while Claude generates

The heading row also has **Reference** (opens the in-app docs browser) and **Library**
(saved papers).

If generation fails (network error, invalid API key, malformed or empty JSON response),
an error dialog is shown and you stay on the current screen — the input screen, or the
Summary screen if you clicked **Drill Same Paper Again** — so you can retry.

### Question Screen

- Questions are shown one at a time
- The question type badge (FACTUAL / CONCEPTUAL / DERIVATION) appears above each question
- Type your answer in the free-text box
- **How sure are you?** — an optional confidence strip sits just above Submit:
  **Guessing / Unsure / Fairly sure / Certain**. It is deliberately *before* the grade so
  the rating cannot be hindsight. Clicking the chosen level again unrates the question;
  **Don't ask again** hides the strip permanently (stored in `paper_settings.json`)
- Click **Submit Answer** — a loading overlay appears while Claude grades
- If grading fails, a dialog asks whether to skip with score 0 or stay on the question.
  Choosing **No** keeps the same question and your typed answer in place; **Submit
  Answer** grades it again

### Feedback Screen

- **Score** (0–10) and **verdict** (Correct / Partially correct / Incorrect)
- **Feedback** — Claude's prose explanation of what was right and wrong
- **Model answer** — what an ideal answer looks like
- **⚑ Flag for Review** — toggles this question in your review list. The button reads
  **Flagged — click to unflag** while the question is flagged; clicking again removes it.
- **What went wrong?** — shown only when the score is below 4. Six one-click causes and an
  optional note; the chosen cause is marked with a ✓ and a solid accent border. Nothing
  here blocks you: the mistake was written to `mistakes.json` (with `cause: null`) before
  the row appeared, **Next Question** stays live, and there is no modal. Clicking the
  chosen cause again clears it back to uncategorised. Answering the same question
  correctly in a later session marks its entries `resolved`.
  A grading *failure* records nothing — the 0 shown there stands for "never graded", not
  for something you got wrong.
- **⚑ Report a problem with this item** — opens a small form (*what is wrong* / *what it
  should say* / *how bad*), then a prefilled GitHub issue in your browser. The item id is
  the same hash the review flag and the mistake journal use, so a report can be matched
  to a logged mistake. It is reachable by Tab, never blocks the drill (no network call,
  **Next Question** stays live, nothing is written to your data directory), and if no
  browser can be opened the URL is shown in a selectable, modeless box so the report is
  not lost
- **Next Question** advances to the next; on the last question the button reads **View
  Summary**

### Summary Screen

- Average score across all questions in the session
- Paper title and a per-question scores line (e.g. `Scores: 9  5  0`)
- **Drill Same Paper Again** regenerates a fresh set of questions from the same paper
  text
- **← New Paper** returns to the input screen

### History Screen

- Session / paper / lifetime-average stat cards and an average-score trend chart
- **Flagged for review** — every question you flagged, newest first, showing the
  question text and the paper it came from; **Unflag** removes an entry
- **Mistake patterns** — a read-only tally of your mistake journal: each cause with how
  many times it has happened and how many of those are still open, plus a
  **Confidently wrong** row ("1 of 2" = one of the two answers you rated *fairly sure* or
  *certain* was wrong). Hidden until there is something to show; only this app's rows are
  counted
- **Back to Setup**

### Reference Screen

This is the suite-wide screen (`common/ui/reference.py`), not a copy of it — paper-drill
used to carry a 357-line fork. It is constructed with no *default chapter* and no *topic
map*, because paper-drill drills whatever paper you paste and so has no home rung on the
ladder; the "Jump to topic" picker other apps get therefore hides itself.

- Browses the shared `docs/` corpus, resolved at call time (beside the package, then
  upwards from the working directory; `QUANTUM_STUDY_DOCS_DIR` overrides it), so it works
  from any checkout location and from an installed wheel
- Left: chapter-grouped document list, in ladder order; right: the rendered markdown
- **Chapter** dropdown and a **search** box that searches titles *and body text*
- **Show solutions** hides the `<details>` solution blocks so you can try first
- `$$…$$` display maths, tables and cross-references between docs are rendered; relative
  `.md` links open in-app, web links and non-markdown targets open in your browser
- **Open externally** opens the current file with your system default application
- The corpus is re-scanned when it changes on disk while the app is open
- **← Back** returns to the input screen

---

## Accessibility

- Every control on the confidence strip and the **What went wrong?** row is reachable by
  Tab, has an accessible name (e.g. *"Confidence 3 of 4: Fairly sure"*, *"Cause: Out of
  time"*), and draws a dashed accent focus ring that stays visible even on the selected
  button
- Selection never rests on colour: the chosen confidence level and the chosen cause are
  prefixed with a ✓ glyph and set in bold, and the accessible description reads
  *"Selected"*
- **⚑ Report a problem with this item** is a plain button in the tab order with the
  accessible name *"Report a problem with this question"*; the dialog it opens is a
  labelled form, and its **Open the issue on GitHub** button stays disabled until there
  is a description to read
- The verdict is always spelled out in words next to the coloured score
- Keyboard focus is visible on *every* control, not only the new ones: the shared base
  stylesheet draws a focus ring for buttons, pills, text fields, combo boxes, radio
  buttons and check boxes, and each rule shrinks the padding by exactly the pixel the
  border grows, so tabbing never shifts the layout
- Every text colour used by the new widgets clears WCAG AA 4.5:1 against the dark palette
  (`TEXT` 14.6:1 on the card surface, `TEXT_MUTED` 5.6:1, `ACCENT` 6.9:1) — asserted by
  `tests/test_learning_ui.py`

---

## How Questions Are Generated

The generation prompt instructs Claude to:

1. Read the paper excerpt (truncated to 12,000 characters if longer)
2. Generate exactly `n` questions that test **deep understanding**, not mere recall
3. Mix factual, conceptual, and derivation types
4. Return a JSON array, no extra text — each element has `index`, `text`, and `type` fields

The response is JSON-parsed; markdown code fences (` ```json ``` `) are stripped if
present. Each parsed item becomes a `Question` dataclass.

---

## How Answers Are Graded

The grading prompt sends Claude:
- The paper excerpt (same truncation)
- The question
- The user's answer

Claude returns a JSON object with:
- `score` — integer 0–10
- `feedback` — prose explanation
- `model_answer` — ideal answer text

The verdict is not asked of Claude; it is derived from the score: ≥7 = Correct,
≥4 = Partially correct, <4 = Incorrect. The score is clamped to [0, 10].

---

## Architecture

```
paper-drill/
├── main.py
├── common_path.py               THE IMPORT SHIM — an unedited copy of
│                                common/app_shim.py; importing it puts the
│                                repository root on sys.path so `import common`
│                                resolves.  Appends, never prepends, so the
│                                app's own modules always win
├── config.py                    MODEL, MAX_PAPER_CHARS, file names, defaults.
│                                Paths are *functions* over common.datadir,
│                                resolved at call time
├── core/
│   └── models.py                Question, DrillConfig, Evaluation, QuestionAttempt,
│                                SessionStats, Verdict enum
├── ai/
│   ├── client.py                make_client() — reads API key from env or file
│   ├── generator.py             generate_questions(paper_text, count) → list[Question]
│   └── grader.py                grade_answer(paper_text, question, answer) → Evaluation
├── workers/
│   ├── generation_worker.py     QThread: call generator → emit questions_ready or failed
│   └── grading_worker.py        QThread: call grader → emit graded or failed
├── ui/
│   ├── main_window.py           Screen controller (7 pages: input, question, feedback,
│   │                            summary, history, library, reference)
│   ├── theme.py                 QTYPE_COLORS + two widget rules; the palette and
│   │                            the base stylesheet come from common.ui.theme
│   └── screens/
│       ├── paper_input_screen.py  Text paste, title, question count, generate button,
│       │                          Reference / Library / History navigation
│       ├── question_screen.py     One question at a time, answer box, progress label,
│       │                          pre-answer confidence strip (+ opt-out)
│       ├── feedback_screen.py     Score, verdict, feedback, model answer, flag toggle,
│       │                          errata report control, "What went wrong?" cause row
│       ├── summary_screen.py      Session average and per-question scores
│       ├── history_screen.py      Stat cards, trend chart, flagged-for-review list,
│       │                          mistake-pattern tally
│       └── library_screen.py      Saved papers: drill again / delete
├── journal_sync.py              **Dead in this app** — kept only because
│                                tests/test_journal_concurrency.py asserts the ten
│                                copies are byte-identical.  The live implementation
│                                is common.locking; delete this file in the same
│                                commit that updates that test
├── persistence.py               The app-shaped face of the shared stores: supplies
│                                app="paper-drill", keeps make_flag_id and the paper
│                                library, delegates everything else to common
└── tests/                       pytest suite (offscreen Qt, temp data dir; no network)
```

### What comes from `common/`

paper-drill carries no copy of the shared machinery any more. Deleted from this tree and
imported instead:

| Was here | Now | Notes |
|---|---|---|
| `persistence.py`'s journal (~200 lines) | `common.journal` | Same call signatures; the store is shared |
| `persistence.py`'s flag store | `common.flags` | Reads legacy bare-id files, rewrites from the *raw* list |
| `persistence.py`'s `_atomic_write_json` / `_load_json_list` | `common.jsonio` | pid-qualified temp names |
| `journal_sync.py` (276 lines) | `common.locking` | The file stays on disk; see above |
| `config.py`'s `DATA_DIR` constants | `common.datadir` | Resolved at call time, not at import |
| `ui/theme.py`'s palette + stylesheet (92 lines) | `common.ui.theme` | The twelve colours were byte-identical in all ten apps |
| `ui/widgets/loading_overlay.py` (35 lines) | `common.ui.widgets` | The animated overlay: a sub-label, a dot ellipsis, and a `hide_overlay()` that stops the timer |
| `ui/screens/reference_screen.py` (357 lines) | `common.ui.reference` | Body search, maths, solution hiding, live re-scan |
| — | `common.schema` | New: version sidecars, migration, rotating backups |
| — | `common.errata` / `common.ui.errata_dialog` | New: the report control |

Kept deliberately local, because it is this app's own and not a fork of anything shared:

- **`make_flag_id`** — the SHA-256 of *paper title + question text*. It is not
  `common.flags.make_id`, which normalises whitespace differently: the digest is written
  into `paper_flagged.json` and into every `mistakes.json` row this app has ever logged,
  so changing it would orphan the flags and the mistake history already on your disk.
  `tests/test_common_migration.py` pins the difference so nobody "tidies" it later.
- **`QTYPE_COLORS`** and **`MISTAKE_SCORE_THRESHOLD`** — paper-drill's vocabulary
  (factual / conceptual / derivation; graded out of ten).
- **The paper library** — no other app has one, so this app registers its own
  `paper_library` schema kind.

---

## Screen Flow

```
PaperInputScreen
      │ drill_requested (config)
      ▼
[GenerationWorker] → questions_ready
      │
      ▼
QuestionScreen ──── answer_submitted (attempt)
      │                     │
      │              [GradingWorker] → graded
      │                     │
      ▼                     ▼
      │              FeedbackScreen
      │                     │ next_requested / done_requested
      ◄────────────────────┘
      │ (done)
      ▼
SummaryScreen ──── back_requested → PaperInputScreen
      │ drill_again → GenerationWorker (same config; Summary stays under the overlay)

PaperInputScreen ─── history_requested
      │
      ▼
HistoryScreen ──── back_requested → PaperInputScreen
      │ Unflag → persistence.unflag()
      │ refresh() → persistence.cause_counts() / confidently_wrong() (read-only)

PaperInputScreen ─── reference_requested
      │
      ▼
ReferenceScreen ── back_requested → PaperInputScreen

FeedbackScreen ─── flag_requested → persistence.toggle_flag() → set_flagged()
FeedbackScreen ─── mistake_cause_selected (cause, note) → persistence.set_mistake_cause()
FeedbackScreen ─── errata button → common.ui.errata_dialog.ErrataDialog
      │                        → common.errata.issue_url(...)
      │                        → QDesktopServices.openUrl()  (or the copyable
      │                          fallback box if there is no browser)
      └ errata_reported (url) → MainWindow._on_errata_reported

MainWindow._record_learning_signals(attempt)   (runs as the feedback screen is shown)
      │ score < 4  → persistence.log_mistake()      → show "What went wrong?"
      │ score >= 4 → persistence.resolve_mistake()  → hide it
      └ rated?     → persistence.log_confidence(confidence, correct)
```

---

## Configuration (`config.py`)

| Constant | Default | Effect |
|---|---|---|
| `MODEL` | `claude-sonnet-4-6` | Claude model for generation and grading |
| `DEFAULT_Q_COUNT` | 5 | Pre-filled question count |
| `MAX_PAPER_CHARS` | 12,000 | Hard truncation limit for paper text |
| `API_KEY_FILE` | `~/.config/quantum-study/api_key.txt` | Fallback when `ANTHROPIC_API_KEY` is unset |

Paths are **functions**, not constants, and each is resolved when it is called:

| Function | Returns |
|---|---|
| `data_dir()` | `$QUANTUM_STUDY_DATA_DIR` if set and non-blank (with `~` expanded), else `~/.local/share/quantum-study` |
| `history_file()` | `data_dir() / paper_history.json` |
| `library_file()` | `data_dir() / paper_library.json` |
| `flagged_file()` | `data_dir() / paper_flagged.json` |
| `settings_file()` | `data_dir() / paper_settings.json` |
| `mistakes_file()` | `data_dir() / mistakes.json` — shared by every app in the suite |
| `confidence_file()` | `data_dir() / confidence.json` — shared by every app in the suite |

The rule itself lives in `common.datadir` and is the same for all ten apps, `coach.py`,
`dashboard.py` and `tools/run_tests.sh`. Resolving on each call (rather than freezing the
directory into a module constant at import time, as every app used to) means setting
`QUANTUM_STUDY_DATA_DIR` takes effect immediately, anywhere, with no reload — which is
also why the test suite needs no monkeypatched path constants any more.

`config.py` fails its own import if these file names ever drift from
`common.datadir.APP_FILES["paper-drill"]`, because that table is how `coach.py` finds
this app's history.

---

## Data Persistence

Sessions are appended to `paper_history.json` in `DATA_DIR` (by default
`~/.local/share/quantum-study/`, or `$QUANTUM_STUDY_DATA_DIR` when set). Each entry
records: paper title, question count, average score, and per-question scores list.

Saved papers live in `paper_library.json` (`id`, `title`, `text`, `q_count`, `saved_at`).

Flagged questions live in `paper_flagged.json`, following the suite-wide flagging
contract shared with the other apps and `coach.py`:

```json
{
  "id":        "paper-<16 hex chars>",
  "label":     "<question text, truncated to 80 chars>",
  "category":  "<paper title>",
  "app":       "paper-drill",
  "timestamp": 1757400000.0
}
```

Because questions are generated fresh each session, the `id` is a SHA-256 hash of the
paper title plus the question text — the same question on the same paper always maps to
the same id. Flagging is a toggle: flagging an already-flagged question removes it.

### Mistake journal — `mistakes.json`

Suite-wide: every app appends to this one file, tagged with its own `app`.

```json
{
  "id":             "paper-<16 hex chars>",
  "app":            "paper-drill",
  "category":       "<paper title>",
  "question":       "<question text, <= 200 chars>",
  "your_answer":    "<what you wrote, <= 200 chars>",
  "correct_answer": "<the model answer, <= 200 chars>",
  "cause":          "misread | didnt_know | knew_but_slipped | confused | out_of_time | other | null",
  "note":           "<optional note, <= 500 chars; line breaks kept>",
  "timestamp":      1757400000.0,
  "resolved":       false
}
```

`cause: null` means "logged but not categorised yet" — that is what a skipped row leaves
behind, and it is still counted (as `uncategorised`) by `persistence.cause_counts()`. The
id is the same hash the review flags use, so a question can be flagged *and* journalled
without drifting apart. Each fresh slip on the same question appends its own row (the
count is the signal); picking or changing a cause edits the newest open row rather than
piling up duplicates. Answering that item correctly later sets `resolved: true` on every
row for it, keeping the analysis while clearing the backlog.

### Confidence calibration — `confidence.json`

Also suite-wide:

```json
{
  "id":         "paper-<16 hex chars>",
  "app":        "paper-drill",
  "category":   "<paper title>",
  "confidence": 4,
  "correct":    false,
  "timestamp":  1757400000.0
}
```

`confidence` is 1 = guessing, 2 = unsure, 3 = fairly sure, 4 = certain, captured *before*
the answer is graded. A row where `confidence >= 3` and `correct` is false is a
confidently-wrong item — `persistence.confidently_wrong()` returns exactly those.

### Reading and writing these files

The rules below are `common.journal` / `common.flags` / `common.jsonio` /
`common.locking`, not this app's own code, so a fix to any of them reaches all ten apps
at once.

* Every path honours `QUANTUM_STUDY_DATA_DIR`, resolved at call time.
* A missing, empty, corrupt or wrongly-shaped file reads as an empty list; nothing raises
  and nothing else in the app changes behaviour.
* Every read-modify-write is held under an `fcntl.flock` on a `<file>.lock` sidecar and
  **re-reads the file inside the lock**, so two open windows (or two apps) cannot each
  read a stale list and write the other's new rows away.
* Writes are atomic (temp file in the same directory + `os.replace`, the temp name
  carrying the pid), so a crash mid-write cannot truncate another app's rows and readers
  need no lock at all.
* Every row owned by another app is written back **verbatim, unknown keys included**.
* Growth is capped at 2,000 mistake rows and 5,000 confidence rows. **Trimming only ever
  drops paper-drill's own oldest rows** — another app's entries are never discarded to
  make room, so the cap is safe on a file nine other apps also write to.
* Nothing here touches the existing `paper_history.json` / `paper_library.json` /
  `paper_flagged.json` schemas that `coach.py` and `dashboard.py` parse.

Pure, Qt-free helpers for all of the above are re-exported from `persistence.py`:
`make_mistake_entry`, `load_mistakes`, `log_mistake`, `set_mistake_cause`,
`resolve_mistake`, `mistakes_for`, `cause_counts`, `make_confidence_entry`,
`load_confidence`, `log_confidence`, `confidently_wrong`, `calibration_summary`,
`clip_text`, `clip_note`, `normalise_cause`, and the settings pair
`confidence_prompt_enabled` / `set_confidence_prompt_enabled`.

### Schema versions, migration and backups

Every one of the six files above now goes through `common.schema`.

**The version marker is a sidecar, not a key in the data.** `paper_history.json` gains
`paper_history.json.schema.json`:

```json
{"file": "paper_history.json", "kind": "history", "schema": 1,
 "written_by": "common/1.0.0", "updated": 1758600000.0}
```

A `{"schema": 1, "rows": [...]}` wrapper was not available: `coach._load_list`,
`dashboard._load` and `dashboard._read_journal` all do
`return data if isinstance(data, list) else []`, so wrapping the payload would make every
one of them read the file as **empty**. The sidecar is invisible to them — they open one
exact file name, and `…schema.json` is not it. The data files are byte-for-byte the shape
they always were.

| Situation | What happens |
|---|---|
| A file already on your disk, with no sidecar | Read as v1 (which it is — the sidecar was introduced without changing any format). Reading never writes. |
| A file older than this build | Migrated forward **in memory** on read; the migrated shape is written, and stamped, the next time something writes. |
| A file written by a **newer** build | The write is **refused**, the file is left exactly as it was, and `persistence.last_write_error()` says so. The drill carries on — a refused journal write never raises into a study session. |
| Before the first write of each session | The current contents are copied to `<name>.bak`, ageing `<name>.bak` → `.bak.1` → `.bak.2`. Three generations, one backup per process, best-effort. `common.schema.restore_backup(path)` rolls one back. |

Backups are why the data directory holds three files per store: the data, an empty
`.lock`, and the `.schema.json` sidecar (plus `.bak*` once a second session has written).

---

## Behaviour changes in the shared-package migration

Everything the app does is unchanged except for the following, each of which is a
divergence `common/` reconciled in favour of the copy that was right. They are listed
because a test somewhere asserted the old behaviour.

| Change | Why |
|---|---|
| `set_mistake_cause(item_id, cause)` now **keeps** the existing note (`note=None` is the default); pass `note=""` to clear it | The old default of `""` wiped the note whenever a cause was picked *after* the note had been typed. The UI always passes both, so the app's own flow is unaffected |
| A confidence rating of `True` is rejected instead of recorded as 1 | `bool` is an `int` subclass, but `True` is not a rating anyone gave |
| A rating stored as a numeric string (`"4"`) now counts as confidently wrong | It is a rating; ignoring it under-reported the tally |
| `load_mistakes()` keeps a dict row that has no `"id"` | A rewrite has to put back rows it cannot parse, or it deletes another app's data |
| The note cap is 500 characters (was 200) and notes keep their line breaks | A note is prose the learner typed; reflowing it destroys deliberate structure. The UI's one-line box still caps input at 200 |
| A flag whose `timestamp` is a string sorts as oldest rather than being parsed | `common.flags` normalises a stored row to the contract shape on load. Nothing raises and no flag disappears; the screen's own `_flag_timestamp` coercion is still there and still tested |
| Config path *constants* (`DATA_DIR`, `HISTORY_FILE`, …) are now *functions* (`data_dir()`, `history_file()`, …) | An import-time constant cannot honour an environment variable set afterwards, which is why every app test needed a reload or a monkeypatched private name |

Gained, with no change required here: the animated loading overlay with a working
`hide_overlay()`, atomic flag writes (four apps used a truncating `write_text`), flag
rewrites from the raw list (five apps deleted rows they did not understand), visible
keyboard focus rings on every control, and a Reference screen with body-text search,
maths rendering and solution hiding.

---

## Tips for Best Results

- **More context is better** — paste the full introduction and methods sections rather
  than just the abstract
- **Derivation-heavy papers** — include the equations in your paste (LaTeX is fine;
  Claude can read it)
- **Re-drilling** — **Drill Same Paper Again** (Summary) and **Drill Again** (Library)
  regenerate completely new questions from the same paper because Claude is
  non-deterministic; you will not see the same questions
- **Long papers** — papers over 12,000 characters are truncated from the end. If your
  paper has important content in the conclusion, paste that section separately
