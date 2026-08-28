# Quantum Computing Study Suite

A self-contained desktop learning suite for quantum computing — from mathematical
foundations through hardware-level error correction and variational algorithms.
All apps are PyQt6 desktop GUIs; some generate problems locally, others call the
Claude API for dynamic question generation and open-ended answer grading.

---

## Projects

| App | Description | API Key | Qiskit |
|---|---|---|---|
| [lesson-plans](lesson-plans/) | 11 structured markdown curricula (incl. C1000-179 prep) | No | No |
| [quantum-quiz](quantum-quiz/) | Dynamic Q&A across 11 QC subjects | Yes | Yes |
| [math-quiz](math-quiz/) | Mathematical foundations for QC | Yes | No |
| [circuit-trainer](circuit-trainer/) | Qiskit-generated circuit problems | Yes | Yes |
| [flashcard-drill](flashcard-drill/) | SRS flashcards — 550 cards, no API | No | No |
| [paper-drill](paper-drill/) | Generate questions from any research paper | Yes | No |
| [qec-trainer](qec-trainer/) | QEC problem set + syndrome decoder game | Yes | No |
| [vqa-trainer](vqa-trainer/) | Variational quantum algorithm problems | Yes | No |
| [qiskit-dojo](qiskit-dojo/) | Write-and-run coding katas — 36, auto-graded by execution | Optional | Yes |
| [exam-sim](exam-sim/) | Timed C1000-179 mock exams — 110-question bank | No | No |
| [problem-trainer](problem-trainer/) | Textbook problem sets + guided derivations, AI-graded | Yes | No |

Beyond the apps: [docs/](docs/) (52-file teaching corpus), [lesson-plans/](lesson-plans/)
(12 curricula incl. certification prep and the reading ladder), [notebooks/](notebooks/)
(executable companions + noise labs), [labs/](labs/) (IBM hardware track),
[projects/](projects/) (5 capstones), [tools/](tools/) (docs regression checker), and two
console utilities at the root: `python dashboard.py` (mastery report) and
`python coach.py` (daily study prescription, diagnostic, badges, unified review queue).

---

## Quick Start

### Prerequisites

Python 3.11+ is recommended. Each app has its own `requirements.txt`.

**Recommended setup** — a project virtual environment at `.venv` covering every app:
```bash
python -m venv .venv && source .venv/bin/activate && pip install PyQt6 anthropic qiskit qiskit-aer matplotlib numpy pylatexenc
```

**Minimum (all apps without API features):**
```
pip install PyQt6
```

**For Claude API apps** (quantum-quiz, math-quiz, paper-drill, qec-trainer, vqa-trainer,
circuit-trainer's free-form grading):
```
pip install anthropic
```

**For Qiskit apps** (quantum-quiz, circuit-trainer):
```
pip install qiskit qiskit-aer pylatexenc
```

### API Key Setup

API apps look for the key in two places, in order:

1. Environment variable: `export ANTHROPIC_API_KEY=sk-ant-...`
2. File: `~/.config/quantum-study/api_key.txt`

The file approach persists across terminal sessions without modifying shell config:
```bash
mkdir -p ~/.config/quantum-study
echo "sk-ant-..." > ~/.config/quantum-study/api_key.txt
```

### Running an App

Each app is a standalone Python package. Run from its directory:
```bash
cd quantum-quiz
pip install -r requirements.txt
python main.py
```

---

## Shared Data Directory

All apps that record session history write to `~/.local/share/quantum-study/`.
Files are plain JSON and are never deleted automatically.

| File | Written by |
|---|---|
| `flashcard_history.json` | flashcard-drill |
| `flagged_cards.json` | flashcard-drill |
| `qec_flagged.json` | qec-trainer |
| `vqa_flagged.json` | vqa-trainer |
| `paper_history.json` | paper-drill |
| `qec_history.json` | qec-trainer |
| `vqa_history.json` | vqa-trainer |
| `quiz_history.json` | quantum-quiz |
| `math_history.json` | math-quiz |
| `trainer_history.json` | circuit-trainer |
| `dojo_history.json` | qiskit-dojo |
| `exam_history.json`, `exam_missed.json` | exam-sim |
| `problems_history.json` | problem-trainer |
| `coach_state.json` | coach.py |

---

## Recommended Learning Path

```
1. lesson-plans          Read the relevant curriculum first
         │
         ▼
2. flashcard-drill       No setup — drill core identities and theorems
         │
         ▼
3. math-quiz             Build mathematical foundations (API needed)
         │
         ▼
4. quantum-quiz          Full QC theory + Qiskit questions (API + Qiskit)
         │
         ├──► circuit-trainer   Hands-on circuit arithmetic (API + Qiskit)
         │
         ├──► qec-trainer       Error correction focus (API)
         │
         ├──► vqa-trainer       Variational algorithms focus (API)
         │
         └──► paper-drill       Test understanding of a specific paper (API)

Production-skill track (alongside the above):
   qiskit-dojo      Write real Qiskit code, graded by execution
   problem-trainer  Long-form problems and guided derivations (API)
   exam-sim         Timed mock exams for C1000-179 (offline)
   notebooks/ labs/ projects/   Executable examples, hardware labs, capstones

Daily driver:  python coach.py   — prescribes today's session from your history
```

---

## Architecture Notes

All apps follow the same structural pattern:

```
<app>/
├── main.py               Entry point — creates QApplication and MainWindow
├── config.py             App-wide constants (model, paths, thresholds)
├── core/
│   └── models.py         Dataclasses shared across all modules
├── ui/
│   ├── main_window.py    QMainWindow + QStackedWidget screen controller
│   ├── screens/          One file per screen (setup, problem, feedback, summary, history)
│   ├── widgets/          Reusable widgets (LoadingOverlay, CollapsiblePanel, ScoreBar, etc.)
│   └── theme.py          Colour palette and style constants
├── workers/              QThread subclasses for non-blocking API calls
├── persistence.py        JSON read/write for session history
└── requirements.txt
```

Apps with static problem banks (flashcard-drill, qec-trainer, vqa-trainer) add a
`cards/` or `problems/` directory. Apps with AI generation add an `ai/` directory.
circuit-trainer is the only app that uses Qiskit for problem generation itself (not
just as a quiz topic).

---

## Claude Model

All API apps use `claude-sonnet-4-6`. The model ID is set in each app's `config.py`
and can be changed there without touching any other code.
