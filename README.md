# Quantum Computing Study Suite

A self-contained desktop learning suite for quantum computing — from mathematical
foundations through hardware-level error correction and variational algorithms.
All apps are PyQt6 desktop GUIs; some generate problems locally, others call the
Claude API for dynamic question generation and open-ended answer grading.

---

## Projects

| App | Description | API Key | Qiskit |
|---|---|---|---|
| [lesson-plans](lesson-plans/) | 10 structured markdown curricula | No | No |
| [quantum-quiz](quantum-quiz/) | Dynamic Q&A across 10 QC subjects | Yes | Yes |
| [math-quiz](math-quiz/) | Mathematical foundations for QC | Yes | No |
| [circuit-trainer](circuit-trainer/) | Qiskit-generated circuit problems | Yes | Yes |
| [flashcard-drill](flashcard-drill/) | SRS flashcards — 82 cards, no API | No | No |
| [paper-drill](paper-drill/) | Generate questions from any research paper | Yes | No |
| [qec-trainer](qec-trainer/) | Quantum error correction problem set | Yes | No |
| [vqa-trainer](vqa-trainer/) | Variational quantum algorithm problems | Yes | No |

---

## Quick Start

### Prerequisites

Python 3.11+ is recommended. Each app has its own `requirements.txt`.

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
pip install qiskit qiskit-aer pylatexenc pillow
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
| `paper_history.json` | paper-drill |
| `qec_history.json` | qec-trainer |
| `vqa_history.json` | vqa-trainer |
| `quantum_quiz_history.json` | quantum-quiz |
| `math_quiz_history.json` | math-quiz |
| `circuit_trainer_history.json` | circuit-trainer |

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
