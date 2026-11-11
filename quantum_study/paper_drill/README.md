# Paper Drill

Paste any quantum computing research paper (or any text) and Paper Drill generates
comprehension questions using Claude, then grades your answers. Designed for active
reading — instead of highlighting passively, you answer targeted factual, conceptual,
and derivation questions about what you just read.

## Run

```bash
python launch.py paper                 # from the repository root (or: quantum-study paper)
python -m quantum_study.paper_drill
```

Needs a Claude API key (`ANTHROPIC_API_KEY`, or `~/.config/quantum-study/api_key.txt`): the questions and the grading come from Claude. Without one, only the Reference browser and the history screen work.
Setup is covered in [GETTING_STARTED.md](../../GETTING_STARTED.md).

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

This is the suite-wide screen (`quantum_study/common/ui/reference.py`), not a copy of it — paper-drill
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

## How Questions Are Generated

The generation prompt instructs Claude to:

1. Read the paper excerpt (truncated to 12,000 characters if longer)
2. Generate exactly `n` questions that test **deep understanding**, not mere recall
3. Mix factual, conceptual, and derivation types
4. Return a JSON array, no extra text — each element has `index`, `text`, and `type` fields

The response is JSON-parsed; markdown code fences (` ```json ``` `) are stripped if
present. Each parsed item becomes a `Question` dataclass.

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

## Data files

Written under `~/.local/share/quantum-study/`, or `$QUANTUM_STUDY_DATA_DIR` if set:

| File | Holds |
|---|---|
| `paper_history.json` | every finished session; read by `coach.py` and `dashboard.py` |
| `paper_flagged.json` | items you flagged for review (the coach's review queue) |
| `paper_library.json` | the papers you have loaded |
| `paper_settings.json` | preferences |
| `mistakes.json`, `confidence.json` | the mistake journal and the confidence ratings, shared by all ten apps |

## Code and tests

The app is the package `quantum_study/paper_drill/`. What it shares with the other nine (the data directory, the journals, the theme, the Reference screen) is in [`quantum_study/common/`](../common/README.md).

```bash
pytest quantum_study/paper_drill        # this app's tests
```
