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
- **Reference browser** — the suite's shared `docs/**/*.md` corpus rendered inside
  the app: chapter filter, full-text search, jump-to-topic for every QEC category,
  in-app cross-reference links — no API key needed
- **Mistake journal** — a wrong answer is not just a bookmark: one tap files it under
  a cause (misread / didn't know / knew but slipped / confused / out of time / other)
  in the suite-wide `mistakes.json`, and re-answering the item correctly resolves it
- **Confidence calibration** — an optional 1–4 "how sure are you?" strip shown *before*
  you submit, paired with the grade in `confidence.json`, so "certain and wrong"
  becomes visible instead of invisible
- **Report a problem with this item** — the bank is public and imperfect. One
  keyboard-reachable button on the result screen opens a *prefilled* GitHub issue for
  the item on screen (its id, its exact text, your description and a suggested fix), so
  "this answer is wrong" turns into a filed report instead of a memory you lose
- **Versioned, backed-up data** — every file the app writes carries a schema version in
  a sidecar, migrates forward when it is read, is refused rather than corrupted by a
  build that does not understand it, and is copied to a rotating `.bak` before the first
  write of each session
- **Keyboard and screen-reader friendly** — every control is tab-reachable with a
  visible focus ring and an accessible name, and no state is carried by colour alone
- **Shared code, not ten copies** — the theme, the docs browser, the journal, the flag
  store and the data-directory rule come from the repository's [`common/`](../common/README.md)
  package, so a fix reaches every app in the suite at once

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

1. **Select categories** — all 6 checked by default
2. **Difficulty** — Beginner / Intermediate / Advanced / Mixed
3. **Problem count** — default 10
4. Click **Start Session**

### Problem Screen

- Question is displayed in a card
- **Multiple choice**: four radio buttons (A–D)
- **Free-form**: multi-line text box
- **Hint** button — click to reveal the next hint (button shows remaining hint count)
- **Confidence strip** (optional) — *1 Guessing · 2 Unsure · 3 Fairly sure · 4 Certain*,
  just above Submit. Rate before you submit or ignore it entirely; **Don't ask again**
  retires it permanently. See
  [Mistake Journal & Confidence Calibration](#mistake-journal--confidence-calibration).
- **Submit** enables once a selection or non-empty text is entered

### Result Screen

After submission:
- **Verdict badge** — ✓ Correct / ◐ Partially correct / ✗ Incorrect (glyph + colour)
- **Feedback** — explanation of the correct answer
- **Model answer** — what an ideal answer looks like (free-form only)
- **"What went wrong?"** (wrong answers only) — six cause pills and an optional note.
  The mistake is already journalled by the time the row appears, so skipping it costs
  nothing; tapping a pill files it under a cause.
- **⚑ Flag for Review** — adds the problem to `qec_flagged.json`, with its question
  text and category, so `python coach.py --review` lists the question rather than a
  bare id
- **⚠ Report a problem with this item** — see [Errata](#errata--reporting-a-wrong-item)
- **Next Problem** or **Finish Session**

### Summary and History

Session summary with accuracy rate and per-category scores. History table shows all past
sessions.

### Reference Screen

**Browse Reference** on the setup screen opens the in-app docs browser for the
repository's shared `docs/` corpus. It is now literally the same browser every app in
the suite ships — [`common.ui.reference.ReferenceScreen`](../common/README.md), which
this app subclasses to supply two constants (the chapter to open first and the
topic → doc map). No API key needed. The docs folder is resolved **at call time**:
`QUANTUM_STUDY_DOCS_DIR` if set, else the `docs/` beside the `common` package, else
upwards from the working directory or the launching script — so it works from a
checkout, from `launch.py`, and from a test pointed at a temp corpus.

- **Chapter list** (left) — every `docs/**/*.md` file grouped by chapter and numbered in
  ladder order (`5.6  The Surface Code`). The screen opens on
  `05_quantum_error_correction/01_why_qec_is_hard.md`, this trainer's rung; the whole
  corpus stays listed. Files added, removed or edited while the app is running
  are picked up the next time the screen is used.
- **Jump to topic** — opens the chapter that backs a problem category:

  | Category | Doc |
  |---|---|
  | Repetition Code | `05_quantum_error_correction/03_repetition_code.md` |
  | Stabilizer Formalism | `05_quantum_error_correction/04_stabilizer_formalism.md` |
  | Steane Code | `05_quantum_error_correction/05_css_codes_and_steane.md` |
  | Surface Code, Decoder Game | `05_quantum_error_correction/06_surface_code.md` |
  | Fault Tolerance | `05_quantum_error_correction/07_fault_tolerance.md` |
  | Bosonic Codes | `05_quantum_error_correction/08_bosonic_codes.md` |

- **Chapter filter** and **search** — the search box matches titles and full text, shows
  a hit count per document, and highlights the first hit in the reader.
- **Reader** (right) — Markdown rendered in-app with dark-theme styling for code, tables,
  quotes and links. Relative links between docs — including the bare
  `NN_chapter/NN_file.md` cross-references the chapters use in prose (a bare `NN_file.md`
  means the sibling file, or the one file of that name anywhere in the corpus) —
  navigate inside the browser (a `#heading` suffix on a cross-reference is honoured),
  `#heading` links scroll to that heading — headings get GitHub-style anchors
  (`## Key Formulas` → `#key-formulas`; a repeated heading gets `-1`, `-2`, …) —
  `http(s)` links open in the system browser, and files outside `docs/` open with the
  system default application. `$$ … $$` display math is shown as a monospace block that
  soft-wraps long lines (kept inside its block quote when quoted); fenced code keeps its
  layout. `<details><summary>Solution</summary>` blocks become "▸ Solution" sections.
- **Show solutions** — untick to hide exercise solutions for self-testing.
- **Open externally** — opens the current `.md` file with the system default application.
- **← Back** returns to the setup screen; the reader keeps its place when you return.

Programmatic entry points (for tests and other screens):
`open_doc("05_quantum_error_correction/06_surface_code.md")`, `show_chapter("05_quantum_error_correction")`,
`show_category("Surface Code")`.

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

Every round also gets the confidence strip (before **Submit Correction**), and a failed
round is journalled under the id `decoder_<level>` — code plus round type — with your
placed Pauli as `your_answer` and the true error as `correct_answer`; the
"What went wrong?" row appears inside the feedback card. Decoding that level correctly
later resolves the entry.

Score and streaks are tracked during the game; the end screen shows the total,
accuracy, best streak, and a per-level breakdown. Each game is saved to
`qec_history.json` in the standard session schema under the category
**"Decoder Game"**, so it appears in the history screen and the repo-level
dashboard alongside the quiz categories.

---

## Mistake Journal & Confidence Calibration

Two small, skippable prompts turn a session into data you can act on. Both write to
suite-wide files shared by every app, so a pattern shows up across the whole suite
rather than one trainer at a time. Neither ever blocks the flow and neither opens a
dialog.

### Mistake journal — `mistakes.json`

Whenever an answer scores below 7 (any `Incorrect` or `Partially correct` verdict, and
any failed Decoder Game round) the mistake is written to
`~/.local/share/quantum-study/mistakes.json` **immediately**, with `cause: null`. The
result screen then shows a compact **"What went wrong?"** row — six cause pills plus an
optional one-line note. Tapping a pill fills in the cause; ignoring the row entirely
still leaves the mistake recorded, so nothing is lost by skipping.

| Field | Type | Notes |
|---|---|---|
| `id` | str | problem id, or `decoder_<level>` for a Decoder Game round (code + round type) |
| `app` | str | always `qec-trainer` from this app |
| `category` | str | problem category, or `Decoder Game` |
| `question` | str | clipped to 200 chars |
| `your_answer` | str | the letter you chose, your free-form text, or the Pauli you placed |
| `correct_answer` | str | `C. …` for MC, the model answer for free-form, the true error for a decoder round |
| `cause` | str \| null | `misread`, `didnt_know`, `knew_but_slipped`, `confused`, `out_of_time`, `other`, or `null` (logged but not yet categorised) |
| `note` | str | your optional one-liner |
| `timestamp` | float | epoch seconds |
| `resolved` | bool | set true when the same `app` + `id` is answered correctly later |

Missing the **same item twice writes two rows**, not one updated row: repetition is
exactly the signal `coach.py --mistakes` counts, and `dashboard.py` says so in its own
comments. (This app used to merge a repeat into the open row — the one behaviour the
move to `common.journal` deliberately changed. Picking a cause still edits a single
row: the newest open one for that item.)

The payload is the *cause counts*: "nine little-endian slips this month" is the signal,
not nine flagged items. `persistence.cause_counts()` and `persistence.open_mistakes()`
return that directly.

### Confidence calibration — `confidence.json`

Above the Submit button (and above **Submit Correction** in the Decoder Game) sits an
optional strip: **1 Guessing · 2 Unsure · 3 Fairly sure · 4 Certain**. It is asked
*before* the answer is submitted, so it can never be hindsight, and it locks the moment
you submit. Once the answer is graded the rating is paired with the outcome:

| Field | Type | Notes |
|---|---|---|
| `id` / `app` / `category` | str | as above |
| `confidence` | int | 1–4 |
| `correct` | bool | score ≥ 7 |
| `timestamp` | float | epoch seconds |

`persistence.calibration_summary()` reduces this to
`{confidence: {"total", "correct"}}` — the confidently-wrong bucket is the one that
sinks exam scores, and `persistence.confidently_wrong()` lists those rows outright. Skipping the strip
records nothing. **Don't ask again** hides it for good; the opt-out lives in
`qec_settings.json` and can be undone with
`persistence.set_confidence_prompt_enabled(True)`.

### Robustness

Both files honour `QUANTUM_STUDY_DATA_DIR`, tolerate being missing, empty, truncated or
not-a-list (they read as empty and are repaired on the next write, never crashing the
app), and are rewritten atomically (temp file + `os.replace`) under an `fcntl` lock held
across the whole read-modify-write, so a crash or a second app writing at the same time
cannot leave half a file or drop a row. Records written by other apps in the suite are
read and rewritten byte for byte, unknown keys included.

Growth is capped at 2,000 mistakes and 5,000 confidence rows by dropping **this app's**
oldest rows only. That is a bug fix: the previous code sorted the *merged* list by
timestamp and kept the newest N, which silently deleted the other nine apps' rows during
a write to a file this app does not own.

### Versioning, migration and backups

Every file this app writes is versioned through
[`common.schema`](../common/README.md#commonschema--versions-migration-backups):

- **The marker is a sidecar**, `mistakes.json.schema.json` beside `mistakes.json`, not a
  key inside the data. `coach.py` and `dashboard.py` all do
  `return data if isinstance(data, list) else []`, so wrapping the payload in
  `{"schema": 1, "rows": […]}` would make the whole journal read as *empty* in both.
  The on-disk data files are byte-for-byte the shape they always were.
- **Reading migrates forward in memory.** An unmarked file — anything written before
  versioning existed — is a v1 file. Reading never rewrites; the next write does.
- **A newer file is refused, not overwritten.** A build that does not understand v4 must
  not write its v1 view over a v4 file. Nothing raises into a drill: the refusal is
  recorded and `persistence.last_write_error()` reports it.
- **One rotating backup per session per file** — `…​.bak` → `.bak.1` → `.bak.2`, taken
  before the first write of the process, restorable with
  `common.schema.restore_backup(path, generation)`.

### Errata — reporting a wrong item

The problem bank is public and imperfect. The result screen carries
**⚠ Report a problem with this item**, which opens
[`common.ui.errata_dialog.ErrataDialog`](../common/README.md#commonuierrata_dialog):
what is wrong, what it should say, and how bad (wrong / misleading / typo). Accepting it
builds a URL that prefills the repository's
`.github/ISSUE_TEMPLATE/content_error.yml` form with the file, the item id, the question
*exactly as you saw it* (choices, bank answer and explanation included), and your
comment, then hands the URL to `QDesktopServices`.

- **Offline and non-blocking.** The URL is pure string work — no network call, no file
  write. The drill stays where it was and **Next** stays live throughout.
- **Keyboard reachable.** An ordinary tab-stop `QPushButton` with an accessible name and
  the theme's focus ring; the dialog's "Open the issue on GitHub" button stays disabled
  until there is a description to read, so an empty report cannot be filed.
- **Degrades without a browser.** If `QDesktopServices` cannot open anything (or raises),
  the link goes to the clipboard and is printed, selectable, on the result screen. The
  report is never silently lost.
- Nothing is sent anywhere: GitHub shows you the filled-in form and you decide.

### Accessibility

Every new control is a real `QPushButton` or `QLineEdit`: tab-reachable, with an
accessible name and a focus ring defined in `ui/theme.py` that never shifts the layout.
Selected state is shown with a `✓` glyph and a text readout as well as the accent fill,
the result verdict is prefixed with `✓ / ◐ / ✗`, and a fired stabilizer square in the
Decoder Game now reads `X−` (quiet ones read `X+`) instead of relying on the red fill
alone — its contrast also went from 3.4:1 to 5.7:1. All new text is ≥ 4.5:1 against the
dark palette.

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
├── common_path.py               the import shim: puts <repo> on sys.path so
│                                `from common import journal` resolves (a verbatim
│                                copy of common/app_shim.py — do not edit)
├── config.py                    MODEL, defaults, and the five file paths —
│                                resolved at call time from common.datadir
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
│   │   ├── reference_screen.py  89 lines: common.ui.reference.ReferenceScreen plus
│   │   │                        this app's chapter + topic map (was 992 lines)
│   │   └── decoder_screen.py    Decoder Game rounds, surface-code grid, results
│   ├── theme.py                 common.ui.theme + this app's topic colours
│   └── widgets/
│       ├── confidence_strip.py  Skippable 1–4 "how sure are you?" strip
│       └── mistake_row.py       Skippable "what went wrong?" cause pills + note
├── persistence.py               History, flags, mistake journal, confidence,
│                                settings — all pure, all call-time resolved
└── journal_sync.py              **dead**: replaced by common.locking. Still on disk
                                 only because tests/test_journal_concurrency.py
                                 asserts all ten apps ship a byte-identical copy;
                                 delete it together with that assertion.
```

Taken from the repository root:

```
common/                          the code the ten apps share
├── datadir.py                   where the data lives (call-time, env-overridable)
├── journal.py                   mistakes.json / confidence.json
├── flags.py                     <prefix>_flagged.json
├── schema.py                    versions, forward migration, rotating backups
├── errata.py                    prefilled GitHub issue URLs (pure, offline)
├── locking.py / jsonio.py       the fcntl lock; atomic writes, forgiving reads
└── ui/
    ├── theme.py                 the palette and base stylesheet
    ├── widgets.py               LoadingOverlay, CollapsiblePanel, PillBadge, ScoreBar
    ├── reference.py             the docs browser
    └── errata_dialog.py         ErrataDialog / ErrataButton
```

Migrating this app onto `common/` removed **776 lines of code** (892 of duplicated
logic, less the shim and the errata feature added back) and a further 129 once
`journal_sync.py` can go. Nothing was forked: where the shared version needed to differ
it takes a constructor argument (`ReferenceScreen(default_chapter=…, category_docs=…)`),
and where this app's call signatures had to survive, `persistence.py` is a thin adapter
over `common.journal` / `common.flags` rather than a second implementation.

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
| `DATA_DIR` | `$QUANTUM_STUDY_DATA_DIR` (stripped, `~` expanded), else `~/.local/share/quantum-study` | Data directory for every file below |
| `HISTORY_FILE` | `<DATA_DIR>/qec_history.json` | Session history (schema read by `coach.py` / `dashboard.py`) |
| `FLAGGED_FILE` | `<DATA_DIR>/qec_flagged.json` | Flag-for-review ids |
| `MISTAKES_FILE` | `<DATA_DIR>/mistakes.json` | Suite-wide mistake journal |
| `CONFIDENCE_FILE` | `<DATA_DIR>/confidence.json` | Suite-wide confidence calibration |
| `SETTINGS_FILE` | `<DATA_DIR>/qec_settings.json` | This app's opt-outs |

Every path above is **resolved on each read**, not frozen when `config.py` is imported:
they are computed by `common.datadir`, so setting `QUANTUM_STUDY_DATA_DIR` at any point
moves all of them, with nothing to reload and no private constant to monkeypatch. That
is the whole of this app's test fixture now. `config.data_dir()`, `history_file()`,
`flagged_file()`, `settings_file()`, `mistakes_file()` and `confidence_file()` are the
functions behind the constant names.

Set `QUANTUM_STUDY_DATA_DIR` to point the whole app at a throwaway directory — the same
override `coach.py`, `launch.py` and the other apps honour — so experiments and tests
never touch the real history. A blank value (`" "`) is treated as no override.

---

## Data Persistence

All files live under `DATA_DIR` (`$QUANTUM_STUDY_DATA_DIR`, defaulting to
`~/.local/share/quantum-study`):

| File | Written by | Shape |
|---|---|---|
| `qec_history.json` | every finished session and Decoder Game | list of sessions: problem count, correct count, accuracy, timestamp, and per-attempt detail (problem id, category, difficulty, score, verdict, hints used, elapsed secs) |
| `qec_flagged.json` | **⚑ Flag for Review** | `[{"id", "label", "category", "app", "timestamp"}]` — the suite's flag contract. A legacy bare-id file (`["p1", "p2"]`) is still read and is upgraded in place on the first write; `coach.py` parses both |
| `mistakes.json` | every wrong answer / failed decoder round | shared across the suite — see [Mistake Journal](#mistake-journal--confidence-calibration) |
| `confidence.json` | every confidence rating you give | shared across the suite |
| `qec_settings.json` | the **Don't ask again** opt-out | `{"confidence_prompt": bool}` |

Each file is accompanied by `<name>.schema.json` (the version marker) and, after the
first write of a second session, up to three `<name>.bak*` generations. The two shared
journals also carry an empty `<name>.lock` sidecar, which is what is `flock`ed for the
length of a read-modify-write.

`qec_history.json`'s schema is load-bearing — `coach.py` and `dashboard.py` parse it —
and is unchanged. The helpers behind all five are plain functions in `persistence.py`
(`make_mistake_entry`, `load_mistakes`, `log_mistake`, `set_mistake_cause`,
`resolve_mistake`, `cause_counts`, `open_mistakes`, `log_confidence`,
`calibration_summary`, `confidently_wrong`, `flagged_entries`,
`confidence_prompt_enabled`, `last_write_error`, …) with no Qt dependency, so they can
be called and tested directly. They are adapters: the storage itself is `common.journal`,
`common.flags` and `common.schema`.

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
