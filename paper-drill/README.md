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

The suite runs Qt offscreen, stubs the Anthropic client, and redirects every
persistence path to a temp directory, so it needs no API key, no network, and never
touches `~/.local/share/quantum-study/`.

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

- Browses the shared `docs/` corpus (resolved relative to the repo checkout:
  `paper-drill/ui/screens/` → repository root `/docs`; nothing is hardcoded)
- Left: chapter → document tree, in ladder order; right: the rendered markdown
- **Chapter** dropdown and **Search titles** box filter the tree
- Relative `.md` links open in-app; web links open in your browser
- Exercise solutions (`<details>` blocks in the docs) are rendered inline under a bold
  **Solution.** lead-in
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
- The verdict is always spelled out in words next to the coloured score
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
├── config.py                    MODEL, MAX_PAPER_CHARS, DATA_DIR, defaults
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
│   ├── screens/
│   │   ├── paper_input_screen.py  Text paste, title, question count, generate button,
│   │   │                          Reference / Library / History navigation
│   │   ├── question_screen.py     One question at a time, answer box, progress label,
│   │   │                          pre-answer confidence strip (+ opt-out)
│   │   ├── feedback_screen.py     Score, verdict, feedback, model answer, flag toggle,
│   │   │                          "What went wrong?" cause row
│   │   ├── summary_screen.py      Session average and per-question scores
│   │   ├── history_screen.py      Stat cards, trend chart, flagged-for-review list,
│   │   │                          mistake-pattern tally
│   │   ├── library_screen.py      Saved papers: drill again / delete
│   │   └── reference_screen.py    In-app docs browser (docs/**/*.md)
│   └── widgets/
│       └── loading_overlay.py     Full-screen translucent spinner with message
├── persistence.py               Sessions, paper library, review flags, mistake journal,
│                                confidence calibration, app settings — JSON read/write
└── tests/                       pytest suite (offscreen Qt, temp data dir; no network)
```

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
| `DATA_DIR` | `~/.local/share/quantum-study` | Directory for history, library and flags; overridden by the `QUANTUM_STUDY_DATA_DIR` environment variable (the same override `coach.py` and `tools/run_tests.sh` use) |
| `FLAGGED_FILE` | `DATA_DIR / paper_flagged.json` | Flag-for-review store |
| `MISTAKES_FILE` | `DATA_DIR / mistakes.json` | Mistake journal (shared by every app in the suite) |
| `CONFIDENCE_FILE` | `DATA_DIR / confidence.json` | Confidence calibration (shared by every app in the suite) |
| `SETTINGS_FILE` | `DATA_DIR / paper_settings.json` | This app's UI preferences (currently the confidence-strip opt-out) |

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
  "note":           "<optional one-liner, <= 200 chars>",
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

* Both honour `QUANTUM_STUDY_DATA_DIR`, like every other store in the suite.
* A missing, empty, corrupt, or wrongly-shaped file reads as an empty list; nothing
  raises and nothing else in the app changes behaviour.
* Writes are atomic (temp file in the same directory + `os.replace`), so a crash
  mid-write cannot truncate another app's rows.
* Growth is capped at 2,000 mistake rows and 5,000 confidence rows. **Trimming only ever
  drops paper-drill's own oldest rows** — another app's entries are never discarded to
  make room, so the cap is safe on a file nine other apps also write to.
* Nothing here touches the existing `paper_history.json` / `paper_library.json` /
  `paper_flagged.json` schemas that `coach.py` and `dashboard.py` parse.

Pure, Qt-free helpers for all of the above live in `persistence.py`:
`make_mistake_entry`, `load_mistakes`, `log_mistake`, `set_mistake_cause`,
`resolve_mistake`, `mistakes_for`, `cause_counts`, `make_confidence_entry`,
`load_confidence`, `log_confidence`, `confidently_wrong`, `clip_text`,
`normalise_cause`, and the settings pair `confidence_prompt_enabled` /
`set_confidence_prompt_enabled`.

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
