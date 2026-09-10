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

Plus two study aids shared with the rest of the suite:

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

Set `QUANTUM_STUDY_DATA_DIR` to relocate both files (history and flagged) to
another directory — the same override `coach.py` and `launch.py` honour; the
default directory is unchanged.

## Layout

```
problem-trainer/
  config.py          constants (model, paths, window)
  persistence.py     history + review-flag schemas above
  core/models.py     Problem/Part, Derivation/Step, session dataclasses
  ai/                client, prompt builders, robust JSON response parsing, grader
  workers/           QThread wrappers for part grading and step checking
  problems/          auto-discovered bank: one file per problem, PROBLEM object
  derivations/       auto-discovered bank: one file per derivation, DERIVATION object
  ui/                theme + screens (setup, problem, derivation, summary, history,
                     reference — the docs browser; resolves <repo>/docs relative
                     to its own path, never a hardcoded home directory)
```

All quantitative claims in rubrics/model solutions (Schmidt spectra, gate
identities, teleportation corrections, Grover/QPE numbers, QAOA closed form,
Holevo χ, threshold arithmetic, CHSH operator identity, …) were verified
numerically with numpy during authoring.
