# Problem Trainer — Textbook Problems & Guided Derivations

Desktop app (PyQt6) for long-form quantum-computing study, part of the
quantum-study suite. Two modes:

1. **Problem Sets** — 16 multi-part, Nielsen&Chuang-end-of-chapter-style
   problems spanning the curriculum (linear algebra/QM math, circuits & gates,
   algorithms, error correction, VQA, information theory). You write free-form
   solutions per part (plain text with unicode/backtick math); Claude grades
   each part against a grader-facing rubric and returns a 0–10 score, feedback,
   and the rubric points you missed. Revise and resubmit any part as often as
   you like (attempts are tracked).
2. **Guided Derivations** — 7 scripted Socratic derivations (QPE, Grover's
   iteration count, CHSH/Tsirelson, no-cloning, teleportation, parameter-shift
   rule, threshold theorem sketch). Answer one step at a time; Claude checks
   each response against the expected step and either accepts it or nudges you.
   After 2 failed tries (or any time you choose) you can reveal the model step
   and continue. A progress bar tracks the steps.

Plus five study aids shared with the rest of the suite:

- **Reference** — an in-app browser for the suite's `docs/` corpus (every
  `docs/**/*.md` chapter, grouped by chapter directory, rendered as rich text).
  Open it from the Setup screen's "📖 Reference" button, or from the
  "📖 Reference" button on a problem/derivation to jump straight to the
  chapter backing that topic — Back returns you to exactly where you were,
  with your work intact. Filter by chapter or title; "Open externally" hands
  the `.md` file to your system viewer.
- **Flag for review** — a toggle on every problem, derivation, and session
  summary row. Flagged items are listed (with Unflag) on the History screen,
  and the Setup screen's "⚑ Flagged for review only" checkbox limits a session
  to them.
- **Mistake journal** — a wrong answer should become *analysis*, not just a
  bookmark. When a part scores under half its points, or a derivation step
  needs the model step, the item is written to the shared journal immediately
  and a compact "✗ What went wrong?" row appears inline on the feedback view:
  one small button per cause (Misread it · Didn't know · Knew it — slipped ·
  Confused · Out of time · Other) plus an optional one-line note. It never
  blocks you and it is never a modal — skip it and the mistake is still
  logged, just uncategorised. Answering the same item correctly later marks
  the entry resolved by itself. The causes are the payload: "nine
  knew-but-slipped entries this month" is the signal worth acting on.
- **Report a problem with this item** — the repository is public, and a wrong
  rubric, a sign error in a model solution or an ambiguous expected step used
  to have no route to a fix except remembering it later. Every problem part
  and every derivation step carries a "⚑ Report a problem with this item"
  button next to "Show model solution" / "Show model step". It opens a short
  form (what is wrong · what it should say · how bad) and then a **prefilled
  GitHub issue** in your browser: the file, the item id and the text exactly as
  you saw it are already filled in, and nothing is filed until you press Submit
  there. The form is modeless — the drill behind it keeps working, and you can
  leave a half-written report open. With no browser available the link is shown
  in a selectable box instead, so the report is never lost.
- **Confidence calibration** — an optional "◔ How sure?" strip (1 Guessing ·
  2 Unsure · 3 Fairly sure · 4 Certain) shown **before** you submit a part or
  check a derivation step, so it can never be hindsight. The rating is paired
  with the result once it is graded, which is what surfaces *confidently
  wrong* topics — the unknown unknowns that sink exam scores. "Don't ask"
  hides it for good; the Setup screen's "◔ Ask how sure I am before each
  answer" checkbox brings it back.

The History screen shows both: an "Open Mistakes" stat card, a calibration
line ("4 Certain: 7/10 right (70%)"), and the list of unresolved mistakes with
their cause and a "Mark resolved" button.

All of the new controls are keyboard reachable (Tab / Space) with a visible
focus ring and an accessible name, state is shown with a glyph (✓, ✗, ◔) as
well as colour, and every text/background pair clears 4.5:1 against the dark
palette.

## Running

```bash
pip install -r requirements.txt
python main.py
```

## API key

Grading and step-checking call Claude (`claude-sonnet-4-6`). The key is read
from the `ANTHROPIC_API_KEY` environment variable, falling back to
`~/.config/quantum-study/api_key.txt`.

The app launches and works **without a key**: every problem part and every
derivation step has a "Show model solution" / "Show model step" fallback, so
offline self-study is fully supported. Grading buttons produce a clear error
message if no key is configured.

## Persistence

Sessions are appended to `~/.local/share/quantum-study/problems_history.json`
(consumed by the suite coach):

```json
[
  {
    "timestamp": 1756250000.0,
    "total": 3,
    "avg_score": 7.2,
    "attempts": [
      {"problem_id": "la_schmidt", "kind": "problem", "score": 8.5},
      {"problem_id": "deriv_qpe", "kind": "derivation", "score": 6.0}
    ]
  }
]
```

Scores are on a 0–10 scale. A problem's score is the points-weighted average of
its part scores; a derivation's score is the fraction of steps accepted without
revealing the model step, scaled to 0–10.

Review flags follow the suite-wide flagging contract and live in
`~/.local/share/quantum-study/problems_flagged.json` (one entry per flagged
item; flagging again removes the entry):

```json
[
  {
    "id": "qec_distance_proof",
    "label": "Error-Correction Conditions and a Distance Proof",
    "category": "Error Correction",
    "app": "problem-trainer",
    "timestamp": 1756250000.0
  },
  {
    "id": "deriv_qpe",
    "label": "Quantum Phase Estimation",
    "category": "derivation",
    "app": "problem-trainer",
    "timestamp": 1756250100.0
  }
]
```

`id` is the problem or derivation id, `label` its title, and `category` the
problem topic (or `"derivation"` for guided derivations). `persistence.py`
exposes `load_flagged()`, `flagged_ids()`, `is_flagged()`, `toggle_flag()` and
`unflag()`; legacy bare-string and `{"problem_id": …}` entries are tolerated on
read and upgraded to the contract shape on the next write. The file is written
atomically from the *raw* list, so a row this app does not understand survives
a rewrite rather than being dropped.

### Mistake journal — `mistakes.json`

Suite-wide (shared with the other study apps; every entry carries an `app`
field, so this app only ever reads, updates and resolves its own rows):

```json
[
  {
    "id": "alg_grover_geometry:a",
    "app": "problem-trainer",
    "category": "Algorithms",
    "question": "Show that |s⟩ = cos(θ)|α⟩ + sin(θ)|β⟩ …",
    "your_answer": "the answer is obviously 42",
    "correct_answer": "Split the uniform sum over the M marked …",
    "cause": "misread",
    "note": "read the ket backwards",
    "timestamp": 1756250000.0,
    "resolved": false
  }
]
```

`id` is `<problem_id>:<part_id>` for a problem part and
`<derivation_id>:<step_id>` for a derivation step; `category` is the problem
topic, or `"derivation"`. `cause` is one of `misread`, `didnt_know`,
`knew_but_slipped`, `confused`, `out_of_time`, `other`, or `null` (logged but
not yet categorised — skipping the row is fine). `question`, `your_answer` and
`correct_answer` are collapsed to one line and clipped to 200 characters (they
are shown in one-line rows on the History screen and by `coach --mistakes`);
`note` keeps its line breaks and is clipped to the same 200. A second bad
attempt at the same item refreshes the entry instead of duplicating it, and
keeps any cause/note you already chose — a part here is *revised* (the feedback
view offers "Resubmit revision" with no limit), so appending a row per draft
would multiply the count the coach reports by however many times you iterated.

### Confidence calibration — `confidence.json`

Also suite-wide; one row per rated answer, appended when the answer is graded:

```json
[
  {
    "id": "alg_grover_geometry:a",
    "app": "problem-trainer",
    "category": "Algorithms",
    "confidence": 4,
    "correct": false,
    "timestamp": 1756250000.0
  }
]
```

`confidence` is 1 = guessing, 2 = unsure, 3 = fairly sure, 4 = certain. Rows
like the one above — high confidence, wrong — are the ones worth chasing.

`persistence.py` exposes the pure helpers `make_mistake_entry()`,
`load_mistakes()`, `save_mistakes()`, `app_mistakes()`, `find_mistake()`,
`log_mistake()`, `set_mistake_cause()`, `resolve_mistake()`,
`make_confidence_entry()`, `load_confidence()`, `log_confidence()` and
`confidence_summary()` — all usable without Qt. Both files are written
atomically (temp file + `os.replace`) under a cross-process lock, a missing or
corrupt file simply starts fresh instead of crashing, and each app keeps at
most the newest 2 000 mistakes / 5 000 calibration rows **of its own**
(`MAX_MISTAKES`, `MAX_CONFIDENCE`) — the files are shared, so trimming another
app's rows would be data loss, not housekeeping.

### App preferences — `problems_settings.json`

A small file of this app's own UI preferences (currently just
`{"confidence_prompt": true}`, the opt-out behind "Don't ask"), kept separate
from anything the suite coach parses.

Set `QUANTUM_STUDY_DATA_DIR` to relocate every one of these files (history,
flagged, mistakes, confidence, settings) to another directory — the same
override `coach.py` and `launch.py` honour; the default directory is unchanged.
A blank value is treated as no override, and a leading `~` is expanded.

### Schema versions, migration and backups

The study data above cannot be regenerated, so every file this app writes now
carries a version marker and a rotating backup, via `common/schema.py`:

```
problems_history.json              the data — unchanged, still a plain JSON list
problems_history.json.schema.json  {"file", "kind", "schema", "written_by", "updated"}
problems_history.json.bak          the state this session started from
problems_history.json.bak.1/.2     the two sessions before that
problems_history.json.lock         the advisory write lock (empty file)
```

The marker is a **sidecar** rather than a key inside the data because
`coach.py` and `dashboard.py` require the top level of these files to be a
plain JSON list — a `{"schema": 1, "rows": [...]}` wrapper would make all of
their loaders read the journal as empty. Nothing about the data files
themselves changed, so an existing directory keeps working untouched, and
`coach.py`'s `*_flagged.json` and `launch.py`'s `*_history.json` globs still
match exactly one file each.

Three guarantees follow:

- **Old files migrate forward.** A file with no sidecar is a v1 file. When a
  format does change, its migration runs *in memory* on read and the file is
  only rewritten the next time something writes it — reading is never
  destructive.
- **A newer file is refused, not corrupted.** If a file was written by a build
  that understands a later schema, this build will not overwrite it with its
  older view. The write is skipped, nothing is raised into a drill, and the
  Setup screen shows a warning line naming the file and the two versions
  (`persistence.last_write_error()`).
- **One backup per session.** Before the first write of each run the previous
  contents are copied to `<name>.bak`, ageing `.bak` → `.bak.1` → `.bak.2`.
  Three generations, best-effort; `common.schema.restore_backup(path)` puts one
  back.

## Layout

```
problem-trainer/
  common_path.py     the import shim: puts the repository root on sys.path so
                     `import common` works (verbatim copy of common/app_shim.py)
  config.py          constants (model, paths, window)
  persistence.py     history, review-flag, mistake-journal, confidence and
                     settings schemas above (pure, Qt-free helpers) over
                     common.journal / common.flags / common.schema
  core/models.py     Problem/Part, Derivation/Step, session dataclasses
  ai/                client, prompt builders, robust JSON response parsing, grader
  workers/           QThread wrappers for part grading and step checking
  problems/          auto-discovered bank: one file per problem, PROBLEM object
  derivations/       auto-discovered bank: one file per derivation, DERIVATION object
  ui/theme.py        the shared palette from common.ui.theme, plus this app's
                     topic colours, flag labels and widget rules
  ui/screens/        setup, problem, derivation, summary, history, and
                     reference — a thin subclass of common.ui.reference's docs
                     browser adding this app's topic/derivation chapter maps
  ui/widgets/        collapsible sections, study_journal (the confidence strip
                     + "What went wrong?" row) and errata (the "report this
                     item" button over common.ui.errata_dialog)
  journal_sync.py    retained, unmodified and no longer imported — see below
  tests/             pytest suite: banks, scoring, prompts, parser, grader,
                     persistence, flags, reference, study journal, schema
                     versioning, errata, and the common/ wiring itself
```

## Shared code (`common/`)

The data-directory rule, the mistake/confidence journal, the flag store, the
schema/backup machinery, the palette, the loading overlay, the Reference screen
and the errata dialog all live in the repository's `common/` package and are
*used*, not copied, here. `tests/test_common_migration.py` asserts that by
identity, so a helper cannot quietly be re-forked into this tree.

`common/` is reached through `common_path.py`, a verbatim copy of
`common/app_shim.py` that appends the repository root to `sys.path`. It is
imported by every module here that imports from `common` — including
`persistence.py`, which the repository's concurrency suite loads by path with
nothing but this directory on `sys.path`. It *appends* rather than prepends, so
a root module (`tests/`, `tools/`, `coach.py`) can never shadow an app module
of the same name. Installed as a wheel, `common` is an ordinary package and the
shim is a no-op.

`journal_sync.py` — the cross-process lock this app used before the migration —
is dead code here now: nothing imports it, and `common.locking` is the
behaviour-preserving extraction. The file is kept, byte-identical, only because
the repository-level `tests/test_journal_concurrency.py` still asserts that all
ten apps ship the same copy; it should be deleted in the same change that
relaxes that test.

All quantitative claims in rubrics/model solutions (Schmidt spectra, gate
identities, teleportation corrections, Grover/QPE numbers, QAOA closed form,
Holevo χ, threshold arithmetic, CHSH operator identity, …) were verified
numerically with numpy during authoring.
