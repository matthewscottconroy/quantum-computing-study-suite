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

Plus four study aids shared with the rest of the suite:

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
`unflag()`; legacy bare-string entries are tolerated on read.

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
not yet categorised — skipping the row is fine). `question`, `your_answer`,
`correct_answer` and `note` are clipped to 200 characters. A second bad attempt
at the same item refreshes the entry instead of duplicating it, and keeps any
cause/note you already chose.

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
atomically (temp file + `os.replace`), a missing or corrupt file simply starts
fresh instead of crashing, and the logs are capped at the newest 2 000
mistakes / 5 000 calibration rows (`MAX_MISTAKES`, `MAX_CONFIDENCE`).

### App preferences — `problems_settings.json`

A small file of this app's own UI preferences (currently just
`{"confidence_prompt": true}`, the opt-out behind "Don't ask"), kept separate
from anything the suite coach parses.

Set `QUANTUM_STUDY_DATA_DIR` to relocate every one of these files (history,
flagged, mistakes, confidence, settings) to another directory — the same
override `coach.py` and `launch.py` honour; the default directory is unchanged.

## Layout

```
problem-trainer/
  config.py          constants (model, paths, window)
  persistence.py     history, review-flag, mistake-journal, confidence and
                     settings schemas above (pure, Qt-free helpers)
  core/models.py     Problem/Part, Derivation/Step, session dataclasses
  ai/                client, prompt builders, robust JSON response parsing, grader
  workers/           QThread wrappers for part grading and step checking
  problems/          auto-discovered bank: one file per problem, PROBLEM object
  derivations/       auto-discovered bank: one file per derivation, DERIVATION object
  ui/                theme + screens (setup, problem, derivation, summary, history,
                     reference — the docs browser; resolves <repo>/docs relative
                     to its own path, never a hardcoded home directory)
  ui/widgets/        collapsible sections, loading overlay, and study_journal
                     (the confidence strip + "What went wrong?" row)
  tests/             pytest suite: banks, scoring, prompts, parser, grader,
                     persistence, flags, reference, study journal
```

All quantitative claims in rubrics/model solutions (Schmidt spectra, gate
identities, teleportation corrections, Grover/QPE numbers, QAOA closed form,
Holevo χ, threshold arithmetic, CHSH operator identity, …) were verified
numerically with numpy during authoring.
