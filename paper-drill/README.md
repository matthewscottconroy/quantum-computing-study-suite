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
- **Configurable question count** — 1–20 questions per session (default 5)
- **Session history** — all past sessions with title, date, question count, and average
  score
- **Grading failure recovery** — if Claude grading fails, a dialog offers to skip the
  question with a score of 0 and continue the session
- **Paper truncation** — papers longer than 12,000 characters are truncated before
  sending to Claude (fits within context limits while keeping token costs predictable)

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

---

## Running

```bash
python main.py
```

---

## Usage

### Paper Input Screen

1. **Paste your paper** — paste the text of a paper, abstract, or any document into the
   large text area. PDFs should be converted to text first (e.g. `pdftotext` or copy
   from a PDF viewer).
2. **Paper title** — type a short title used to label sessions in history
3. **Question count** — how many questions to generate (default 5)
4. Click **Generate Questions** — a loading overlay appears while Claude generates

If generation fails (network error, invalid API key, malformed JSON response), an error
dialog is shown and you are returned to the input screen to retry.

### Question Screen

- Questions are shown one at a time
- The question type badge (FACTUAL / CONCEPTUAL / DERIVATION) appears above each question
- Type your answer in the free-text box
- Click **Submit Answer** — a loading overlay appears while Claude grades
- If grading fails, a dialog asks whether to skip with score 0 or stay on the question

### Feedback Screen

- **Score** (0–10) and **verdict** (Correct / Partially correct / Incorrect)
- **Feedback** — Claude's prose explanation of what was right and wrong
- **Model answer** — what an ideal answer looks like
- **Next Question** advances to the next; on the last question the button reads **Finish**

### Summary Screen

- Average score across all questions in the session
- Per-question breakdown: question text, your answer, score, verdict
- **Drill Again** regenerates questions from the same paper text
- **Back to Home** returns to the input screen

### History Screen

- Table of past sessions: title, date, question count, average score
- Click a row to see the per-question detail
- **Back to Home**

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
- `verdict` — one of "Correct", "Partially correct", "Incorrect"
- `feedback` — prose explanation
- `model_answer` — ideal answer text

Verdict is derived from score: ≥7 = Correct, ≥4 = Partially correct, <4 = Incorrect.
The score is clamped to [0, 10].

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
│   ├── main_window.py           Screen controller (5 pages: input, question, feedback,
│   │                            summary, history)
│   ├── screens/
│   │   ├── paper_input_screen.py  Text paste, title, question count, generate button
│   │   ├── question_screen.py     One question at a time, answer box, progress label
│   │   ├── feedback_screen.py     Score, verdict, feedback, model answer
│   │   ├── summary_screen.py      Session overview and per-question table
│   │   └── history_screen.py      Past sessions table
│   └── widgets/
│       └── loading_overlay.py     Full-screen translucent spinner with message
└── persistence.py               save_session(), load_sessions() — JSON read/write
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
      │ drill_again → PaperInputScreen → GenerationWorker (same config)

PaperInputScreen ─── history_requested
      │
      ▼
HistoryScreen ──── back_requested → PaperInputScreen
```

---

## Configuration (`config.py`)

| Constant | Default | Effect |
|---|---|---|
| `MODEL` | `claude-sonnet-4-6` | Claude model for generation and grading |
| `DEFAULT_Q_COUNT` | 5 | Pre-filled question count |
| `MAX_PAPER_CHARS` | 12,000 | Hard truncation limit for paper text |
| `DATA_DIR` | `~/.local/share/quantum-study` | Session history directory |

---

## Data Persistence

Sessions appended to `~/.local/share/quantum-study/paper_history.json`. Each entry
records: paper title, question count, average score, and per-question scores list.

---

## Tips for Best Results

- **More context is better** — paste the full introduction and methods sections rather
  than just the abstract
- **Derivation-heavy papers** — include the equations in your paste (LaTeX is fine;
  Claude can read it)
- **Re-drilling** — the "Drill Again" button regenerates completely new questions from
  the same paper because Claude is non-deterministic; you will not see the same questions
- **Long papers** — papers over 12,000 characters are truncated from the end. If your
  paper has important content in the conclusion, paste that section separately
