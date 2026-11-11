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

## Run

```bash
python launch.py problem                 # from the repository root (or: quantum-study problem)
python -m quantum_study.problem_trainer
```

Needs a Claude API key (`ANTHROPIC_API_KEY`, or `~/.config/quantum-study/api_key.txt`): the questions and the grading come from Claude. Without one, only the Reference browser and the history screen work.
Setup is covered in [GETTING_STARTED.md](../../GETTING_STARTED.md).

## Data files

Written under `~/.local/share/quantum-study/`, or `$QUANTUM_STUDY_DATA_DIR` if set:

| File | Holds |
|---|---|
| `problems_history.json` | every finished session; read by `coach.py` and `dashboard.py` |
| `problems_flagged.json` | items you flagged for review (the coach's review queue) |
| `problems_settings.json` | preferences |
| `mistakes.json`, `confidence.json` | the mistake journal and the confidence ratings, shared by all ten apps |

## Code and tests

The app is the package `quantum_study/problem_trainer/`. What it shares with the other nine (the data directory, the journals, the theme, the Reference screen) is in [`quantum_study/common/`](../common/README.md).

```bash
pytest quantum_study/problem_trainer        # this app's tests
```
