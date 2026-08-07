# VQA Trainer

A focused problem trainer for variational quantum algorithms. 28 problems across 6
categories — from VQE fundamentals and the parameter shift rule through QAOA, ansatz
design, barren plateaus, and noise mitigation. Three answer modes: multiple choice,
exact numeric (for parameter shift calculations), and open-ended free-form.

---

## Features

- **28 curated problems** across 6 VQA categories
- **Three answer modes:**
  - **Multiple choice** — auto-graded instantly
  - **Numeric** — exact value with tolerance and partial credit (for parameter shift
    and gradient calculations)
  - **Free-form** — Claude-graded with detailed feedback
- **Partial credit for numeric answers** — answers within 20× tolerance receive 4–9
  points scaled by proximity; only exact answers (within tolerance) get 10
- **Hint system** — 1–2 hints per problem
- **Grading failure recovery** — skip dialog on Claude API errors
- **Session history** — per-category score tracking
- **numpy required** — used for parameter shift gradient computations in the problem bank

---

## Requirements

```
PyQt6>=6.6
anthropic>=0.25
numpy>=1.26
```

Install:
```bash
pip install -r requirements.txt
```

---

## API Key

Set `ANTHROPIC_API_KEY` in your environment, or write to
`~/.config/quantum-study/api_key.txt`. Only free-form problems call the API.

---

## Running

```bash
python main.py
```

---

## Usage

### Setup Screen

1. **Select categories** — all 6 checked by default
2. **Difficulty** — Beginner / Intermediate / Advanced / Mixed
3. **Problem count** — default 8
4. Click **Start Session**

### Problem Screen

Depending on grade mode:
- **Multiple choice** — radio buttons (A–D)
- **Numeric** — single-line text input; accepts decimal notation (e.g. `-0.4330`)
- **Free-form** — multi-line text box

Hint button shows remaining hint count. Submit enables on valid input.

### Result Screen

- Verdict badge and score (0–10)
- Feedback with explanation
- Model answer (for numeric and free-form)
- **Next Problem** or **Finish**

---

## Problem Bank

### VQE Fundamentals (6 problems)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| vqe_variational_principle | Beginner | MC | ⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀ |
| vqe_pauli_decomp | Beginner | MC | Why decompose H into Pauli strings? |
| vqe_ansatz | Intermediate | MC | Hardware-efficient ansatz structure |
| vqe_optimizer | Intermediate | MC | Classical optimiser role in the VQE loop |
| vqe_accuracy | Advanced | MC | Chemical accuracy threshold (1.6 × 10⁻³ Hartree) |
| vqe_freeform | Advanced | Free-form | Analyse trade-offs between expressibility and trainability |

### QAOA (5 problems)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| qaoa_structure | Beginner | MC | QAOA ansatz: alternating U_C and U_B layers |
| qaoa_maxcut | Intermediate | MC | QAOA cost Hamiltonian for MaxCut |
| qaoa_p1 | Intermediate | MC | QAOA p=1 approximation ratio for MaxCut |
| qaoa_depth | Advanced | MC | Depth scaling with problem size |
| qaoa_freeform | Advanced | Free-form | When does QAOA converge to the exact solution? |

### Parameter Shift Rule (5 problems)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| ps_rule | Beginner | MC | ∂⟨H⟩/∂θ = [⟨H⟩(θ+π/2) − ⟨H⟩(θ−π/2)] / 2 |
| ps_numeric_basic | Intermediate | **Numeric** | Compute ∂⟨Z⟩/∂θ for Ry(θ)|0⟩ at θ=π/3 → 0.4000 |
| ps_numeric_sin | Advanced | **Numeric** | Compute ∂⟨Z⟩/∂θ for Ry(θ) at θ=π/3 → −sin(π/3) |
| ps_higher_order | Advanced | MC | Higher-order parameter shift for non-Pauli generators |
| ps_freeform | Advanced | Free-form | Prove the parameter shift rule from Euler decomposition |

### Ansatz Design (4 problems)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| ansatz_expressibility | Beginner | MC | Expressibility: how well the ansatz covers state space |
| ansatz_entanglement | Intermediate | MC | Entanglement capability of different ansatz topologies |
| ansatz_hardware | Intermediate | MC | Native gate sets and connectivity constraints |
| ansatz_freeform | Advanced | Free-form | Design a 4-qubit HEA for a linear coupling map |

### Barren Plateaus (4 problems)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| bp_definition | Beginner | MC | Variance of gradient vanishes exponentially with n |
| bp_cause | Intermediate | MC | Global cost functions and random initialisation |
| bp_mitigation | Intermediate | MC | Layer-by-layer training and local cost functions |
| bp_freeform | Advanced | Free-form | Relate barren plateaus to the 2-design property |

### Noise and Mitigation (4 problems)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| noise_depolarising | Beginner | MC | Depolarising channel effect on VQA gradients |
| noise_zne | Intermediate | MC | Zero-noise extrapolation — Richardson extrapolation |
| noise_pec | Advanced | MC | Probabilistic error cancellation quasi-probability |
| noise_freeform | Advanced | Free-form | Compare ZNE and PEC trade-offs in near-term VQA |

---

## Numeric Grading Details

The parameter shift numeric problems use exact computed values:

| Problem | Correct value | Tolerance |
|---|---|---|
| ps_numeric_basic | 0.4000 | 1 × 10⁻⁴ |
| ps_numeric_sin | −sin(π/3) ≈ −0.8660 | 1 × 10⁻³ |

**Partial credit formula:**

```
diff = |user_value - correct_value|

if diff ≤ tolerance:
    score = 10,  verdict = Correct

elif diff ≤ tolerance × 20:
    score = max(4, round(10 × (1 - diff / (tolerance × 20))))
    verdict = Partially correct

else:
    score = 0,  verdict = Incorrect
```

This means:
- Exact answers → 10
- Answers within 20× tolerance → 4–9 (scaled linearly)
- Further off → 0

---

## Architecture

```
vqa-trainer/
├── main.py
├── config.py                    MODEL, DATA_DIR, defaults
├── core/
│   └── models.py                Problem, TrainerConfig, Attempt, SessionStats,
│                                GradeMode (AUTO/MC/CLAUDE), Verdict enums
├── problems/
│   ├── __init__.py              ALL_PROBLEMS aggregated from all modules
│   ├── vqe_fundamentals.py      6 problems
│   ├── qaoa.py                  5 problems
│   ├── parameter_shift.py       5 problems (2 numeric auto-graded)
│   ├── ansatz_design.py         4 problems
│   ├── barren_plateaus.py       4 problems
│   └── noise_and_mitigation.py  4 problems
├── grading/
│   └── auto_grader.py           grade_mc() and grade_numeric() — local, no API
├── workers/
│   └── grading_worker.py        QThread: Claude grading for GradeMode.CLAUDE problems
├── ai/
│   └── grader.py                Claude grading implementation
├── ui/
│   ├── main_window.py           Screen controller
│   ├── screens/
│   │   ├── setup_screen.py      Category/difficulty/count
│   │   ├── problem_screen.py    MC radio / numeric input / free-form box
│   │   ├── result_screen.py     Verdict, feedback, model answer
│   │   ├── summary_screen.py    Session stats
│   │   └── history_screen.py    Past sessions table
│   └── widgets/
│       └── loading_overlay.py
└── persistence.py
```

---

## GradeMode Enum

`vqa-trainer` has three grade modes, unlike `qec-trainer` which only has two:

| GradeMode | Used for | Grading method |
|---|---|---|
| `MC` | Multiple choice problems | `auto_grader.grade_mc()` — local index comparison |
| `AUTO` | Numeric calculation problems | `auto_grader.grade_numeric()` — local float comparison with partial credit |
| `CLAUDE` | Free-form explanation problems | `GradingWorker` → Claude API |

---

## Configuration (`config.py`)

| Constant | Default | Effect |
|---|---|---|
| `MODEL` | `claude-sonnet-4-6` | Claude model for free-form grading |
| `DEFAULT_PROBLEM_COUNT` | 8 | Pre-filled problem count |
| `DATA_DIR` | `~/.local/share/quantum-study` | Session history directory |

---

## Data Persistence

Sessions appended to `~/.local/share/quantum-study/vqa_history.json`. Each entry
records: problem count, correct count, accuracy, and per-attempt detail.

---

## Adding Problems

```python
from core.models import Problem, GradeMode

# Multiple choice
Problem(
    id="unique_id",
    category="Category Name",
    difficulty="intermediate",
    question="Question text.",
    choices=["A", "B", "C", "D"],
    correct_index=0,
    explanation="Explanation text.",
    hints=["Hint 1."],
    grade_mode=GradeMode.MC,
)

# Numeric
Problem(
    id="numeric_id",
    category="Parameter Shift",
    difficulty="advanced",
    question="Compute the gradient ...",
    correct_value=0.5000,
    tolerance=1e-4,
    explanation="The parameter shift rule gives ...",
    hints=["Apply f(θ+π/2) and f(θ-π/2)."],
    grade_mode=GradeMode.AUTO,
)

# Free-form
Problem(
    id="freeform_id",
    category="VQE Fundamentals",
    difficulty="advanced",
    question="Explain ...",
    explanation="Model answer: ...",
    grade_mode=GradeMode.CLAUDE,
)
```

Add to `ALL_PROBLEMS` in `problems/__init__.py`. No other changes needed.
