# Exam Sim

A timed mock-exam simulator for **IBM certification exam C1000-179 —
"Fundamentals of Quantum Computing Using Qiskit v2.X Developer"**
(68 questions, 90 minutes, 47 correct to pass).

Fully offline: a static bank of 110 original multiple-choice questions, no API
keys, no network access. Part of the quantum-study suite (see `vqa-trainer`,
`qec-trainer`, etc.), sharing its dark theme and persistence directory.

> **Disclaimer** — The exam logistics (question count, time limit, pass mark,
> section weights) are third-party-sourced and may change; verify them against
> IBM's official exam page. Every question in the bank is **original study
> material** written for this app. None of it is real exam content, and using
> this app is not affiliated with or endorsed by IBM.

---

## Requirements

```
PyQt6>=6.6
```

```bash
pip install -r requirements.txt
python main.py
```

The app itself only needs PyQt6. (Qiskit is not required to *run* the app —
the bank is static — but the code snippets in the questions target
qiskit 2.x + qiskit-aer and were verified by execution against qiskit 2.5.2.)

---

## Modes

### Full exam
- 68 questions drawn from the bank **proportionally to the exam section
  weights** (largest-remainder allocation, randomized order)
- 90-minute countdown, always visible (turns red under 5 minutes; auto-submits
  at zero)
- Question navigator: jump to any question, **flag** for review, skip and
  return; answered/flagged/unanswered states are color-coded
- **No per-question feedback** during the exam
- On submit: results screen with score vs the 47/68 pass bar, a per-section
  table (your % vs exam weight), and a review pane walking every missed
  question with its explanation

### Sprint
- Pick one section, 10 questions, 10-minute timer
- Same results/review flow (pass bar scaled to the 47/68 ratio)

### Review mode
- Browse previously missed questions (from `exam_missed.json`) and re-answer
  them with immediate feedback
- Answer one correctly and it is removed from the missed list; miss it again
  and it stays (timestamp refreshed)

---

## Question bank

110 questions across the exact C1000-179 objective sections, proportional to
the exam weights:

| Section | Questions |
|---|---|
| Create circuits | 20 |
| Quantum operations | 18 |
| Run circuits | 16 |
| Sampler | 13 |
| Estimator | 13 |
| Visualization | 12 |
| Results analysis | 11 |
| OpenQASM | 7 |

Style mimics associate-level exam items: a short Qiskit 2.x code snippet plus
"what is the output / which line is wrong / which option completes this", with
plausible distractors (off-by-one qubit indices, big-endian assumptions,
V1-primitive idioms, removed APIs such as `execute`, `qiskit.Aer`,
`bind_parameters`, `c_if`, `quasi_dists`). 109 of the 110 questions were
verified by actually executing their code against qiskit 2.5.2 + qiskit-aer;
the single remaining question (IBM Runtime ISA-circuit requirement) was
verified against the Qiskit 2.x / Runtime documentation.

### Bank format

One file per question under `bank/<section_dir>/`, auto-discovered — no
registration step:

```python
"""Question: cc_example"""
from core.models import Question

QUESTION = Question(
    id="cc_example",                  # unique across the bank
    section="Create circuits",        # one of the 8 exact section names
    question="What does this print?\n\n```python\nprint(1 + 1)\n```",
    options=["2", "11", "1", "It raises TypeError"],   # exactly 4
    correct_index=0,
    explanation="Why the answer is right and the distractors are wrong.",
    difficulty="easy",                # easy | medium | hard
)
```

A fenced ``` block inside `question` is rendered monospace in the UI.

---

## Data persistence

Shared directory `~/.local/share/quantum-study/` (a coach app integrates with
these files — schemas are stable):

`exam_history.json` — appended after every full/sprint session:

```json
[{"timestamp": 1724000000.0, "mode": "full", "total": 68, "correct": 51,
  "duration_secs": 4980.2,
  "sections": {"Create circuits": {"total": 12, "correct": 9}}}]
```

`exam_missed.json` — one entry per currently-missed question (deduped by id;
appended on a miss, removed when later answered correctly in Review mode):

```json
[{"question_id": "cc_depth", "section": "Create circuits",
  "question": "...", "correct_answer": "3", "chosen": "4",
  "timestamp": 1724000000.0}]
```

---

## Architecture

```
exam-sim/
├── main.py
├── config.py                  exam logistics, section weights, data paths
├── core/
│   └── models.py              Question, ExamAttempt, ExamResult
├── bank/
│   ├── __init__.py            auto-discovery + weighted exam-set builder
│   ├── create_circuits/       20 questions (one file each)
│   ├── quantum_operations/    18
│   ├── run_circuits/          16
│   ├── sampler/               13
│   ├── estimator/             13
│   ├── visualization/         12
│   ├── results_analysis/      11
│   └── openqasm/              7
├── persistence.py             exam_history.json / exam_missed.json
└── ui/
    ├── theme.py               dark theme (mirrors vqa-trainer)
    ├── format.py              fenced-code → HTML rendering
    ├── main_window.py         screen controller
    └── screens/
        ├── home_screen.py     mode picker + history summary
        ├── exam_screen.py     timer, navigator, flag/skip/return
        ├── results_screen.py  pass bar, section table, review pane
        └── review_screen.py   re-answer missed questions
```
