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
│   │   ├── question_screen.py     One question at a time, answer box, progress label
│   │   ├── feedback_screen.py     Score, verdict, feedback, model answer, flag toggle
│   │   ├── summary_screen.py      Session average and per-question scores
│   │   ├── history_screen.py      Stat cards, trend chart, flagged-for-review list
│   │   ├── library_screen.py      Saved papers: drill again / delete
│   │   └── reference_screen.py    In-app docs browser (docs/**/*.md)
│   └── widgets/
│       └── loading_overlay.py     Full-screen translucent spinner with message
├── persistence.py               Sessions, paper library, and review flags — JSON read/write
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

PaperInputScreen ─── reference_requested
      │
      ▼
ReferenceScreen ── back_requested → PaperInputScreen

FeedbackScreen ─── flag_requested → persistence.toggle_flag() → set_flagged()
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
