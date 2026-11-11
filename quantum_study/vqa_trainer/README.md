# VQA Trainer

A focused problem trainer for variational quantum algorithms. 179 problems across 7
categories — from VQE fundamentals and the parameter shift rule through QAOA, ansatz
design, barren plateaus, noise mitigation, and quantum optimal control. Three answer modes: multiple choice,
exact numeric (for parameter shift calculations), and open-ended free-form.

---

## Features

- **179 curated problems** across 7 VQA categories
- **Three answer modes:**
  - **Multiple choice** — auto-graded instantly
  - **Numeric** — exact value with tolerance and partial credit (for parameter shift
    and gradient calculations)
  - **Free-form** — Claude-graded with detailed feedback
- **Partial credit for numeric answers** — answers within 20× tolerance receive 4–9
  points scaled by proximity; only exact answers (within tolerance) get 10
- **Hint system** — 1–2 hints per problem
- **Errata reporting** — "Report a problem with this item" on the result screen opens a
  prefilled GitHub issue about the problem you are looking at
- **Grading failure recovery** — skip dialog on Claude API errors
- **Mistake journal** — a wrong answer becomes *analysis*, not a bookmark: an inline,
  skippable "What went wrong?" row asks *why* you missed it (misread / didn't know /
  knew but slipped / confused / out of time / other) plus an optional one-line note.
  Nine "knew but slipped" rows in a month is a signal; nine flagged items is not.
  Answering the same item correctly later marks its entries resolved
- **Confidence calibration** — a 1–4 confidence strip shown *before* you submit, so the
  rating can never be hindsight. Pairing it with the grade surfaces the
  **confidently wrong** topics — the unknown unknowns that sink exam scores. Optional,
  skippable, and "Don't ask again" turns it off for good
- **Accessible controls** — every chip and field is keyboard reachable with a visible
  focus ring and an accessible name, and no result is carried by colour alone
  (verdicts pair their colour with ✓ / ◐ / ✗ and the spelled-out word)
- **Session history** — per-category score tracking
- **Reference browser** — the suite's shared `docs/**/*.md` corpus rendered inside
  the app: chapter filter, full-text search, jump-to-topic for every VQA category,
  in-app cross-reference links — no API key needed
- **numpy required** — used for parameter shift gradient computations in the problem bank

---

## Requirements

```
PyQt6>=6.6
anthropic>=0.25
numpy>=1.26
```

Install:
```bash
pip install -r requirements.txt
```

---

## API Key

Set `ANTHROPIC_API_KEY` in your environment, or write to
`~/.config/quantum-study/api_key.txt`. Only free-form problems call the API.

---

## Running

```bash
python main.py
```

---

## Usage

### Setup Screen

1. **Select categories** — all 7 checked by default
2. **Difficulty** — Beginner / Intermediate / Advanced / Mixed
3. **Problem count** — default 8
4. Click **Start Session**

### Problem Screen

Depending on grade mode:
- **Multiple choice** — radio buttons (A–D)
- **Numeric** — single-line text input; accepts decimal notation (e.g. `-0.4330`)
- **Free-form** — multi-line text box

Hint button shows remaining hint count. Submit enables on valid input.

**Confidence strip** — above the Submit button, *before* the answer is graded:

| Button | Meaning |
|---|---|
| `1 · Guessing` | pure guess |
| `2 · Unsure` | leaning one way, far from sure |
| `3 · Fairly sure` | fairly sure this is right |
| `4 · Certain` | certain this is right |

Skipping it costs nothing — the problem grades exactly the same and no row is written.
**Don't ask again** hides the strip permanently (stored in `vqa_settings.json`; delete
the `confidence_prompt` key, or the file, to get it back).

### Result Screen

- Verdict badge and score (0–10), glyphed (`✓` / `◐` / `✗`) as well as coloured
- Feedback with explanation
- Model answer (for numeric and free-form)
- **Mistake journal** — shown only when the answer scored below 7/10. The mistake is
  already recorded by the time the row appears, so pressing **Next Problem** loses
  nothing; clicking a cause chip categorises it, and the note field takes one line of
  "what to remember next time" (flushed automatically when you move on)
- **⚑ Flag for Review** — a toggle; flagged problems come back via **Flagged only** on
  the setup screen and through `coach.py`'s review queue
- **⚑ Report a problem with this item** — see below
- **Next Problem** or **Finish**

#### Reporting a wrong or ambiguous problem

The repository is public, and the only thing worse than a wrong answer key is a wrong
answer key nobody told anyone about. **⚑ Report a problem with this item** opens a
short form — *what is wrong*, *what it should say*, *how bad* — and then a GitHub
issue that is **already filled in** with the problem's file and id, and the problem
text exactly as you saw it, choices included.

- The button is tab-reachable and named for a screen reader; the **Open the issue on
  GitHub** button stays disabled until you have described the defect.
- Nothing is sent from the app. It builds a URL and hands it to the system browser;
  you read and submit the issue there.
- Nothing blocks. If there is no browser (a headless box, a sandbox with no portal),
  the link goes to your clipboard and the screen says so, so the report is not lost.
- Cancelling opens nothing, and reporting never disturbs the journal row, the flag or
  the **Next Problem** button.

The form and the URL come from `common/errata.py` and `common/ui/errata_dialog.py`, so
every app in the suite files the same shaped issue.

### Reference Screen

**Browse Reference** on the setup screen opens the in-app docs browser for the
repository's shared `docs/` corpus — literally the same browser every app in the
suite ships (`common/ui/reference.py`); no API key needed. The docs folder is resolved
at call time — beside the `common` package (`<repo>/docs`), else upwards from the
working directory or the launched script — so run the app from inside a checkout, or
set **`QUANTUM_STUDY_DOCS_DIR`** to point it at a corpus of your own.

- **Chapter list** (left) — every `docs/**/*.md` file grouped by chapter and numbered in
  ladder order (`6.4  QAOA: Quantum Approximate Optimization Algorithm`). The screen opens on
  `06_variational_quantum_algorithms/01_vqe_fundamentals.md`, this trainer's rung; the
  whole corpus stays listed. Files added, removed or edited while the app is running
  are picked up the next time the screen is used.
- **Jump to topic** — opens the chapter that backs a problem category:

  | Category | Doc |
  |---|---|
  | VQE Fundamentals | `06_variational_quantum_algorithms/01_vqe_fundamentals.md` |
  | Ansatz Design | `06_variational_quantum_algorithms/02_ansatz_design.md` |
  | Parameter Shift | `06_variational_quantum_algorithms/03_parameter_shift_gradient.md` |
  | QAOA | `06_variational_quantum_algorithms/04_qaoa.md` |
  | Barren Plateaus | `06_variational_quantum_algorithms/05_barren_plateaus.md` |
  | Noise & Mitigation | `06_variational_quantum_algorithms/06_noise_and_error_mitigation.md` |
  | Optimal Control | `06_variational_quantum_algorithms/07_quantum_optimal_control.md` |

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
`open_doc("06_variational_quantum_algorithms/04_qaoa.md")`, `show_chapter("06_variational_quantum_algorithms")`,
`show_category("QAOA")`.

---

## Problem Bank

179 problems: VQE Fundamentals (30), Noise and Mitigation (28), Ansatz Design (27),
Parameter Shift Rule (27), QAOA (27), Barren Plateaus (25), and Quantum Optimal
Control (15). The tables below show a representative sample from each category.

### VQE Fundamentals (30 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| vqe_variational_principle | Beginner | MC | ⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀ |
| vqe_pauli_decomp | Beginner | MC | Why decompose H into Pauli strings? |
| vqe_ansatz | Intermediate | MC | Hardware-efficient ansatz structure |
| vqe_optimizer | Intermediate | MC | Classical optimiser role in the VQE loop |
| vqe_accuracy | Advanced | MC | Chemical accuracy threshold (1.6 × 10⁻³ Hartree) |
| vqe_freeform | Advanced | Free-form | Analyse trade-offs between expressibility and trainability |

### QAOA (27 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| qaoa_structure | Beginner | MC | QAOA ansatz: alternating U_C and U_B layers |
| qaoa_maxcut | Intermediate | MC | QAOA cost Hamiltonian for MaxCut |
| qaoa_p1 | Intermediate | MC | QAOA p=1 approximation ratio for MaxCut |
| qaoa_depth | Advanced | MC | Depth scaling with problem size |
| qaoa_freeform | Advanced | Free-form | When does QAOA converge to the exact solution? |

### Parameter Shift Rule (27 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| ps_rule | Beginner | MC | ∂⟨H⟩/∂θ = [⟨H⟩(θ+π/2) − ⟨H⟩(θ−π/2)] / 2 |
| ps_numeric_basic | Intermediate | **Numeric** | Compute ∂⟨Z⟩/∂θ for Ry(θ)|0⟩ at θ=π/3 → 0.4000 |
| ps_numeric_sin | Advanced | **Numeric** | Compute ∂⟨Z⟩/∂θ for Ry(θ) at θ=π/3 → −sin(π/3) |
| ps_higher_order | Advanced | MC | Higher-order parameter shift for non-Pauli generators |
| ps_freeform | Advanced | Free-form | Prove the parameter shift rule from Euler decomposition |

### Ansatz Design (27 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| ansatz_expressibility | Beginner | MC | Expressibility: how well the ansatz covers state space |
| ansatz_entanglement | Intermediate | MC | Entanglement capability of different ansatz topologies |
| ansatz_hardware | Intermediate | MC | Native gate sets and connectivity constraints |
| ansatz_freeform | Advanced | Free-form | Design a 4-qubit HEA for a linear coupling map |

### Barren Plateaus (25 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| bp_definition | Beginner | MC | Variance of gradient vanishes exponentially with n |
| bp_cause | Intermediate | MC | Global cost functions and random initialisation |
| bp_mitigation | Intermediate | MC | Layer-by-layer training and local cost functions |
| bp_freeform | Advanced | Free-form | Relate barren plateaus to the 2-design property |

### Noise and Mitigation (28 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| noise_depolarising | Beginner | MC | Depolarising channel effect on VQA gradients |
| noise_zne | Intermediate | MC | Zero-noise extrapolation — Richardson extrapolation |
| noise_pec | Advanced | MC | Probabilistic error cancellation quasi-probability |
| noise_freeform | Advanced | Free-form | Compare ZNE and PEC trade-offs in near-term VQA |

---

## Numeric Grading Details

The parameter shift numeric problems use exact computed values:

| Problem | Correct value | Tolerance |
|---|---|---|
| ps_numeric_basic | 0.4000 | 1 × 10⁻⁴ |
| ps_numeric_sin | −sin(π/3) ≈ −0.8660 | 1 × 10⁻³ |

**Partial credit formula:**

```
diff = |user_value - correct_value|

if diff ≤ tolerance:
    score = 10,  verdict = Correct

elif diff ≤ tolerance × 20:
    score = max(4, round(10 × (1 - diff / (tolerance × 20))))
    verdict = Partially correct

else:
    score = 0,  verdict = Incorrect
```

This means:
- Exact answers → 10
- Answers within 20× tolerance → 4–9 (scaled linearly)
- Further off → 0

---

## Architecture

```
vqa-trainer/
├── main.py
├── common_path.py               the import shim: puts <repo> on sys.path so the
│                                app can `from common import …` (a verbatim copy
│                                of common/app_shim.py — do not edit)
├── config.py                    MODEL, DATA_DIR, defaults
├── core/
│   └── models.py                Problem, TrainerConfig, Attempt, SessionStats,
│                                GradeMode (AUTO/MC/CLAUDE), Verdict enums
├── problems/
│   ├── __init__.py              all_problems(): auto-discovers one file per problem
│   ├── vqe_fundamentals/        30 problems
│   ├── noise_and_mitigation/    28 problems
│   ├── ansatz_design/           27 problems
│   ├── parameter_shift/         27 problems
│   ├── qaoa/                    27 problems
│   ├── barren_plateaus/         25 problems
│   └── quantum_optimal_control/ 15 problems
├── grading/
│   └── auto_grader.py           grade_mc() and grade_numeric() — local, no API
├── workers/
│   └── grading_worker.py        QThread: Claude grading for GradeMode.CLAUDE problems
├── ai/
│   └── grader.py                Claude grading implementation
├── ui/
│   ├── main_window.py           Screen controller
│   ├── screens/
│   │   ├── setup_screen.py      Category/difficulty/count
│   │   ├── problem_screen.py    MC radio / numeric input / free-form box
│   │   ├── result_screen.py     Verdict, feedback, model answer, errata button
│   │   ├── summary_screen.py    Session stats
│   │   ├── history_screen.py    Past sessions table
│   │   └── reference_screen.py  two constants + a 12-line subclass of
│   │                            common.ui.reference.ReferenceScreen
│   └── widgets/
│       ├── confidence_strip.py  1–4 rating strip, shown before submitting
│       └── mistake_row.py       "What went wrong?" cause chips + note field
├── persistence.py               adapter over common.journal / common.flags /
│                                common.schema — this app's call signatures,
│                                the suite's implementation
└── journal_sync.py              superseded by common.locking; kept on disk only
                                 because tests/test_journal_concurrency.py still
                                 asserts all ten copies are byte-identical.
                                 Nothing in this app imports it any more.
```

### What lives in `common/` now

`ui/theme.py` was 122 lines, `ui/screens/reference_screen.py` was 992, and
`persistence.py` carried its own copy of the journal, the flag store, the advisory
lock and the atomic writer. All of that is now one implementation in the repository's
[`common/`](../common/README.md) package, imported through `common_path.py`:

| This app's module | What it is now | From `common` |
|---|---|---|
| `ui/theme.py` | the category colours + three widget rules | `common.ui.theme` (palette, base stylesheet, `extend`, `apply`) |
| `ui/screens/reference_screen.py` | `_APP_CHAPTER_DIR` + `CATEGORY_DOC` + a subclass | `common.ui.reference` |
| `ui/widgets/loading_overlay.py` | **deleted** | `common.ui.widgets.LoadingOverlay` (animated; `hide_overlay()` also stops the timer) |
| `persistence.py` journal half | thin adapters that supply `app="vqa-trainer"` | `common.journal` |
| `persistence.py` flag half | `load_flagged()` / `toggle_flag()` | `common.flags` |
| path constants | resolved at call time | `common.datadir` |
| every write | versioned, backed up | `common.schema` |
| `journal_sync.py` | unused | `common.locking` |

Four behaviours changed with the move, all of them documented in
`common/README.md` as the winner of a ten-way divergence:

1. **The growth cap only trims this app's rows.** The old code sorted the *merged*
   `mistakes.json` by timestamp and kept the newest 2000 — which deleted **other
   apps'** rows during our write. Eight of the ten apps had this bug.
2. **`CAUSE_LABELS["didnt_know"]` is ASCII `"Didn't know"`.** This app was the only
   one with a typographic apostrophe.
3. **A confidence rating outside 1–4 records nothing** instead of being clamped to 1.
   A clamped rating is a rating the learner never gave.
4. **The note keeps its line breaks** and is capped at 500 characters; the one-line
   fields (question, your answer, correct answer) are still whitespace-collapsed and
   capped at 200. (The note box in the UI is a 200-character single line either way.)

The flag file also changes shape — see **Data Persistence** below.

---

## GradeMode Enum

`vqa-trainer` has three grade modes, unlike `qec-trainer` which only has two:

| GradeMode | Used for | Grading method |
|---|---|---|
| `MC` | Multiple choice problems | `auto_grader.grade_mc()` — local index comparison |
| `AUTO` | Numeric calculation problems | `auto_grader.grade_numeric()` — local float comparison with partial credit |
| `CLAUDE` | Free-form explanation problems | `GradingWorker` → Claude API |

---

## Configuration (`config.py`)

| Constant | Default | Effect |
|---|---|---|
| `MODEL` | `claude-sonnet-4-6` | Claude model for free-form grading |
| `DEFAULT_PROBLEM_COUNT` | 8 | Pre-filled problem count |
| `DATA_DIR` | `~/.local/share/quantum-study` | Session history directory |
| `APP_DIR_NAME` | `vqa-trainer` | The `app` field written into the shared journals |

`DATA_DIR` — and therefore every file below it — is overridden by the
**`QUANTUM_STUDY_DATA_DIR`** environment variable, the same override `coach.py`,
`launch.py` and the rest of the suite honour. It is resolved by `common.datadir`
**at call time**, so setting the variable at any point moves the whole app; a blank
value is ignored, and `~` is expanded. (The constants in `config.py` are an
import-time snapshot of the same resolution, kept because tooling reads them.)

```bash
QUANTUM_STUDY_DATA_DIR=/tmp/scratch-study python main.py   # touches nothing real
```

---

## Data Persistence

All files live under `DATA_DIR` (`~/.local/share/quantum-study` by default; see
`QUANTUM_STUDY_DATA_DIR` above). Every write goes through a temp file in the same
directory followed by `os.replace`, so an interrupted write can never truncate a file,
and every read tolerates a missing or corrupt file by starting fresh instead of
crashing. The two shared files are written under an `flock` held for the whole
read-modify-write, and rows owned by another app are put back exactly as they were
read — unknown keys included.

| File | Scope | Contents |
|---|---|---|
| `vqa_history.json` | this app | Sessions: problem count, correct count, accuracy, per-attempt detail *(schema unchanged)* |
| `vqa_flagged.json` | this app | Flagged problems *(shape changed — see below)* |
| `mistakes.json` | **whole suite** | Mistake journal — one row per wrong answer |
| `confidence.json` | **whole suite** | Confidence calibration — one row per rated answer |
| `vqa_settings.json` | this app | UI preferences (currently `confidence_prompt`) |

### Schema versions, migration and backups

Every one of those files now carries two companions:

| File | What it is |
|---|---|
| `<name>.schema.json` | the version sidecar: `{"file", "kind", "schema", "written_by", "updated"}` |
| `<name>.bak`, `.bak.1`, `.bak.2` | three rotating generations, one taken per run before its first write |
| `<name>.lock` | an empty file `flock`ed across a read-modify-write on a shared journal |

Why a **sidecar** rather than a `{"schema": 1, "rows": […]}` wrapper: `coach.py` and
`dashboard.py` both do `return data if isinstance(data, list) else []`, so a wrapper
object would make the whole mistake journal read as *empty* in both of them. The data
files keep the exact shape they have always had; the marker sits beside them, where
those readers never look.

What it buys:

- **An older file migrates forward on read**, in memory. Reading is never destructive —
  open a v1 file with a v3 build, change nothing, and it is still a v1 file afterwards.
  A file with no sidecar at all is a pre-versioning file, which is a v1 file.
- **A newer file is refused, not overwritten.** If `mistakes.json` was written by a
  build that understands v4 and this one only understands v1, the write is declined
  rather than silently dropping the newer build's fields. It does not raise into your
  session: `persistence.last_write_error()` reports it.
- **One bad write is recoverable.** `common.schema.restore_backup(path)` puts the
  previous generation back.

### `vqa_flagged.json` — shape change

This app used to write a bare list of ids, `["bp_definition", "qaoa_structure"]`. It
now writes the suite's contract shape, which seven of the ten apps already used and
which `coach.py`'s review queue prefers:

```json
[{"id": "qaoa_mixer_role", "label": "qaoa_mixer_role", "category": "",
  "app": "vqa-trainer", "timestamp": 1790179820.65}]
```

`coach.py` parses both, and an existing bare-id file is read as-is and upgraded in
place the first time you flag or unflag something — upgraded rows get `timestamp: 0.0`
rather than *now*, so a ten-month-old flag does not jump to the top of the review
queue on the day the file happens to be rewritten. Two further fixes come with it: the
file is written atomically (a plain `write_text` truncated first, so a crash mid-write
lost every flag), and the rewrite is based on the raw file, so a row this build does
not fully understand is not deleted.

### `mistakes.json`

A JSON list; every row carries an `app` field, so the ten apps share one journal.

```json
{
  "id": "qaoa_mixer_role",
  "app": "vqa-trainer",
  "category": "QAOA",
  "question": "Which operator does QAOA apply first in each layer?",
  "your_answer": "B. The mixer U_B",
  "correct_answer": "A. The cost operator U_C",
  "cause": "knew_but_slipped",
  "note": "U_C is the cost layer, U_B mixes",
  "timestamp": 1790169448.34,
  "resolved": false
}
```

`cause` is one of `misread`, `didnt_know`, `knew_but_slipped`, `confused`,
`out_of_time`, `other` — or `null`, meaning *logged but not yet categorised* (you
skipped the row). The four text fields are clipped to 200 characters. Repeated misses
of the same item are kept as separate rows: the repeat count *is* the signal.
`resolved` flips to `true` on every row for that item once you answer it correctly.

### `confidence.json`

```json
{
  "id": "qaoa_mixer_role",
  "app": "vqa-trainer",
  "category": "QAOA",
  "confidence": 4,
  "correct": false,
  "timestamp": 1790169448.34
}
```

`confidence` is `1` guessing / `2` unsure / `3` fairly sure / `4` certain, recorded
before submitting and paired with the grade afterwards. A low correct-rate at level 4
is the confidently-wrong signal.

**Growth caps.** The journal keeps this app's newest `MAX_MISTAKES = 2000` rows and
the calibration log its newest `MAX_CONFIDENCE = 5000`; **only this app's** oldest rows
are ever dropped. Both files are shared, and trimming them by a global timestamp order
— which this app used to do — deletes other apps' history during our own write.

### `persistence.py`

Unit-testable without Qt. Every signature below is unchanged by the migration to
`common/` — they are adapters that supply `app="vqa-trainer"` and forward:

```python
make_mistake_entry(...) -> dict      load_mistakes() -> list[dict]
log_mistake(...) -> dict             set_mistake_cause(id, cause, note) -> dict | None
resolve_mistakes(id) -> int          mistake_cause_counts(app=None) -> dict[str, int]
make_confidence_entry(...) -> dict   load_confidence() -> list[dict]
log_confidence(...) -> dict | None   confidence_breakdown() -> dict[int, tuple[int, int]]
load_flagged() -> set[str]           toggle_flag(problem_id) -> bool
save_session(stats)                  avg_scores_by_category() / problem_score_weights()
load_settings() / save_settings()    confidence_prompt_enabled() / set_confidence_prompt_enabled()
normalise_cause(cause) -> str | None last_write_error() -> SchemaError | None
```

Paths are resolved when they are used, not frozen at import:

```python
history_path()  flagged_path()  settings_path()  mistakes_path()  confidence_path()
```

so `QUANTUM_STUDY_DATA_DIR` alone redirects the app — no test needs to monkeypatch a
constant.

---

## Adding Problems

```python
from core.models import Problem, GradeMode

# Multiple choice
Problem(
    id="unique_id",
    category="Category Name",
    difficulty="intermediate",
    question="Question text.",
    choices=["A", "B", "C", "D"],
    correct_index=0,
    explanation="Explanation text.",
    hints=["Hint 1."],
    grade_mode=GradeMode.MC,
)

# Numeric
Problem(
    id="numeric_id",
    category="Parameter Shift",
    difficulty="advanced",
    question="Compute the gradient ...",
    correct_value=0.5000,
    tolerance=1e-4,
    explanation="The parameter shift rule gives ...",
    hints=["Apply f(θ+π/2) and f(θ-π/2)."],
    grade_mode=GradeMode.AUTO,
)

# Free-form
Problem(
    id="freeform_id",
    category="VQE Fundamentals",
    difficulty="advanced",
    question="Explain ...",
    explanation="Model answer: ...",
    grade_mode=GradeMode.CLAUDE,
)
```

Save each problem as its own file inside the appropriate `problems/<category>/`
directory, assigned to a module-level `PROBLEM`. `problems/__init__.py` auto-discovers
every problem file, so no registration step is needed.

---

## Tests

```bash
cd vqa-trainer && python -m pytest
```

`tests/conftest.py` sets `QUANTUM_STUDY_DATA_DIR` to a `tmp_path` directory (and
redirects the path constants in `config.py` and `persistence.py` to match), so the
suite can never touch the real `~/.local/share/quantum-study`.

| File | Covers |
|---|---|
| `test_bank.py` | Problem bank: counts, ids, categories, well-formed entries |
| `test_grading.py` | MC/numeric auto-graders, problem-set builder, Claude prompt (no API) |
| `test_persistence.py` | History and flag round-trips, the legacy bare-id upgrade, decay weighting, corrupt files |
| `test_config_env.py` | `QUANTUM_STUDY_DATA_DIR` relocates every path (fresh interpreter) |
| `test_journal.py` | Mistake journal / calibration / settings helpers — pure, no Qt |
| `test_journal_ui.py` | Headless drive: rate → answer wrongly → journal a cause → flag → re-answer correctly → resolved |
| `test_schema_versioning.py` | Sidecars, forward migration, a newer file refused, rotating backups |
| `test_errata.py` | "Report a problem with this item": the URL, the dialog, the browser call, the no-browser fallback |
| `test_app_launch.py` | `MainWindow` constructs offscreen with no API key |
| `test_reference.py` | In-app docs browser |

The suite-wide behaviour this app now shares lives in the repository root suite
(`tests/test_common_*.py`), including the ten-process concurrency test that has this
app's `persistence.py` writing `mistakes.json` alongside the other nine.
