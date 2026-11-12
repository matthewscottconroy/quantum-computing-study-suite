# VQA Trainer

A focused problem trainer for variational quantum algorithms. 179 problems across 7
categories — from VQE fundamentals and the parameter shift rule through QAOA, ansatz
design, barren plateaus, noise mitigation, and quantum optimal control. Three answer modes: multiple choice,
exact numeric (for parameter shift calculations), and open-ended free-form.

## Run

```bash
python launch.py vqa                 # from the repository root (or: quantum-study vqa)
python -m quantum_study.vqa_trainer
```

Runs offline. A Claude API key (`ANTHROPIC_API_KEY`, or `~/.config/quantum-study/api_key.txt`) adds the Claude-graded parts.
Setup is covered in [GETTING_STARTED.md](../../GETTING_STARTED.md).

## Features

- **179 curated problems** across 7 VQA categories
- **Three answer modes:**
  - **Multiple choice** — auto-graded instantly
  - **Numeric** — exact value with tolerance and partial credit (for parameter shift
    and gradient calculations)
  - **Free-form** — Claude-graded with detailed feedback
- **Partial credit for numeric answers** — answers within 20× tolerance receive 4–9
  points scaled by proximity; only exact answers (within tolerance) get 10
- **Hint system** — 1–2 hints per problem
- **Errata reporting** — "Report a problem with this item" on the result screen opens a
  prefilled GitHub issue about the problem you are looking at
- **Grading failure recovery** — skip dialog on Claude API errors
- **Mistake journal** — a wrong answer becomes *analysis*, not a bookmark: an inline,
  skippable "What went wrong?" row asks *why* you missed it (misread / didn't know /
  knew but slipped / confused / out of time / other) plus an optional one-line note.
  Nine "knew but slipped" rows in a month is a signal; nine flagged items is not.
  Answering the same item correctly later marks its entries resolved
- **Confidence calibration** — a 1–4 confidence strip shown *before* you submit, so the
  rating can never be hindsight. Pairing it with the grade surfaces the
  **confidently wrong** topics — the unknown unknowns that sink exam scores. Optional,
  skippable, and "Don't ask again" turns it off for good
- **Accessible controls** — every chip and field is keyboard reachable with a visible
  focus ring and an accessible name, and no result is carried by colour alone
  (verdicts pair their colour with ✓ / ◐ / ✗ and the spelled-out word)
- **Session history** — per-category score tracking
- **Reference browser** — the suite's shared `docs/**/*.md` corpus rendered inside
  the app: chapter filter, full-text search, jump-to-topic for every VQA category,
  in-app cross-reference links — no API key needed
- **numpy required** — used for parameter shift gradient computations in the problem bank

## Usage

### Setup Screen

1. **Select categories** — all 7 checked by default
2. **Difficulty** — Beginner / Intermediate / Advanced / Mixed
3. **Problem count** — default 8
4. Click **Start Session**

### Problem Screen

Depending on grade mode:
- **Multiple choice** — radio buttons (A–D)
- **Numeric** — single-line text input; accepts decimal notation (e.g. `-0.4330`)
- **Free-form** — multi-line text box

Hint button shows remaining hint count. Submit enables on valid input.

**Confidence strip** — above the Submit button, *before* the answer is graded:

| Button | Meaning |
|---|---|
| `1 · Guessing` | pure guess |
| `2 · Unsure` | leaning one way, far from sure |
| `3 · Fairly sure` | fairly sure this is right |
| `4 · Certain` | certain this is right |

Skipping it costs nothing — the problem grades exactly the same and no row is written.
**Don't ask again** hides the strip permanently (stored in `vqa_settings.json`; delete
the `confidence_prompt` key, or the file, to get it back).

### Result Screen

- Verdict badge and score (0–10), glyphed (`✓` / `◐` / `✗`) as well as coloured
- Feedback with explanation
- Model answer (for numeric and free-form)
- **Mistake journal** — shown only when the answer scored below 7/10. The mistake is
  already recorded by the time the row appears, so pressing **Next Problem** loses
  nothing; clicking a cause chip categorises it, and the note field takes one line of
  "what to remember next time" (flushed automatically when you move on)
- **⚑ Flag for Review** — a toggle; flagged problems come back via **Flagged only** on
  the setup screen and through `coach.py`'s review queue
- **⚑ Report a problem with this item** — see below
- **Next Problem** or **Finish**

#### Reporting a wrong or ambiguous problem

The repository is public, and the only thing worse than a wrong answer key is a wrong
answer key nobody told anyone about. **⚑ Report a problem with this item** opens a
short form — *what is wrong*, *what it should say*, *how bad* — and then a GitHub
issue that is **already filled in** with the problem's file and id, and the problem
text exactly as you saw it, choices included.

- The button is tab-reachable and named for a screen reader; the **Open the issue on
  GitHub** button stays disabled until you have described the defect.
- Nothing is sent from the app. It builds a URL and hands it to the system browser;
  you read and submit the issue there.
- Nothing blocks. If there is no browser (a headless box, a sandbox with no portal),
  the link goes to your clipboard and the screen says so, so the report is not lost.
- Cancelling opens nothing, and reporting never disturbs the journal row, the flag or
  the **Next Problem** button.

The form and the URL come from `quantum_study/common/errata.py` and `quantum_study/common/ui/errata_dialog.py`, so
every app in the suite files the same shaped issue.

### Reference Screen

**Browse Reference** on the setup screen opens the in-app docs browser for the
repository's shared `docs/` corpus — literally the same browser every app in the
suite ships (`quantum_study/common/ui/reference.py`); no API key needed. The docs folder is resolved
at call time — beside the `common` package (`<repo>/docs`), else upwards from the
working directory or the launched script — so run the app from inside a checkout, or
set **`QUANTUM_STUDY_DOCS_DIR`** to point it at a corpus of your own.

- **Chapter list** (left) — every `docs/**/*.md` file grouped by chapter and numbered in
  ladder order (`6.4  QAOA: Quantum Approximate Optimization Algorithm`). The screen opens on
  `06_variational_quantum_algorithms/01_vqe_fundamentals.md`, this trainer's rung; the
  whole corpus stays listed. Files added, removed or edited while the app is running
  are picked up the next time the screen is used.
- **Jump to topic** — opens the chapter that backs a problem category:

  | Category | Doc |
  |---|---|
  | VQE Fundamentals | `06_variational_quantum_algorithms/01_vqe_fundamentals.md` |
  | Ansatz Design | `06_variational_quantum_algorithms/02_ansatz_design.md` |
  | Parameter Shift | `06_variational_quantum_algorithms/03_parameter_shift_gradient.md` |
  | QAOA | `06_variational_quantum_algorithms/04_qaoa.md` |
  | Barren Plateaus | `06_variational_quantum_algorithms/05_barren_plateaus.md` |
  | Noise & Mitigation | `06_variational_quantum_algorithms/06_noise_and_error_mitigation.md` |
  | Optimal Control | `06_variational_quantum_algorithms/07_quantum_optimal_control.md` |

- **Chapter filter** and **search** — the search box matches titles and full text, shows
  a hit count per document, and highlights the first hit in the reader.
- **Reader** (right) — Markdown rendered in-app with dark-theme styling for code, tables,
  quotes and links. Relative links between docs — including the bare
  `NN_chapter/NN_file.md` cross-references the chapters use in prose (a bare `NN_file.md`
  means the sibling file, or the one file of that name anywhere in the corpus) —
  navigate inside the browser (a `#heading` suffix on a cross-reference is honoured),
  `#heading` links scroll to that heading — headings get GitHub-style anchors
  (`## Key Formulas` → `#key-formulas`; a repeated heading gets `-1`, `-2`, …) —
  `http(s)` links open in the system browser, and files outside `docs/` open with the
  system default application. `$$ … $$` display math is shown as a monospace block that
  soft-wraps long lines (kept inside its block quote when quoted); fenced code keeps its
  layout. `<details><summary>Solution</summary>` blocks become "▸ Solution" sections.
- **Show solutions** — untick to hide exercise solutions for self-testing.
- **Open externally** — opens the current `.md` file with the system default application.
- **← Back** returns to the setup screen; the reader keeps its place when you return.

Programmatic entry points (for tests and other screens):
`open_doc("06_variational_quantum_algorithms/04_qaoa.md")`, `show_chapter("06_variational_quantum_algorithms")`,
`show_category("QAOA")`.

## Problem Bank

179 problems: VQE Fundamentals (30), Noise and Mitigation (28), Ansatz Design (27),
Parameter Shift Rule (27), QAOA (27), Barren Plateaus (25), and Quantum Optimal
Control (15). The tables below show a representative sample from each category.

### VQE Fundamentals (30 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| vqe_variational_principle | Beginner | MC | ⟨ψ(θ)|H|ψ(θ)⟩ ≥ E₀ |
| vqe_pauli_decomp | Beginner | MC | Why decompose H into Pauli strings? |
| vqe_ansatz | Intermediate | MC | Hardware-efficient ansatz structure |
| vqe_optimizer | Intermediate | MC | Classical optimiser role in the VQE loop |
| vqe_accuracy | Advanced | MC | Chemical accuracy threshold (1.6 × 10⁻³ Hartree) |
| vqe_freeform | Advanced | Free-form | Analyse trade-offs between expressibility and trainability |

### QAOA (27 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| qaoa_structure | Beginner | MC | QAOA ansatz: alternating U_C and U_B layers |
| qaoa_maxcut | Intermediate | MC | QAOA cost Hamiltonian for MaxCut |
| qaoa_p1 | Intermediate | MC | QAOA p=1 approximation ratio for MaxCut |
| qaoa_depth | Advanced | MC | Depth scaling with problem size |
| qaoa_freeform | Advanced | Free-form | When does QAOA converge to the exact solution? |

### Parameter Shift Rule (27 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| ps_rule | Beginner | MC | ∂⟨H⟩/∂θ = [⟨H⟩(θ+π/2) − ⟨H⟩(θ−π/2)] / 2 |
| ps_numeric_basic | Intermediate | **Numeric** | Compute ∂⟨Z⟩/∂θ for Ry(θ)|0⟩ at θ=π/3 → 0.4000 |
| ps_numeric_sin | Advanced | **Numeric** | Compute ∂⟨Z⟩/∂θ for Ry(θ) at θ=π/3 → −sin(π/3) |
| ps_higher_order | Advanced | MC | Higher-order parameter shift for non-Pauli generators |
| ps_freeform | Advanced | Free-form | Prove the parameter shift rule from Euler decomposition |

### Ansatz Design (27 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| ansatz_expressibility | Beginner | MC | Expressibility: how well the ansatz covers state space |
| ansatz_entanglement | Intermediate | MC | Entanglement capability of different ansatz topologies |
| ansatz_hardware | Intermediate | MC | Native gate sets and connectivity constraints |
| ansatz_freeform | Advanced | Free-form | Design a 4-qubit HEA for a linear coupling map |

### Barren Plateaus (25 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| bp_definition | Beginner | MC | Variance of gradient vanishes exponentially with n |
| bp_cause | Intermediate | MC | Global cost functions and random initialisation |
| bp_mitigation | Intermediate | MC | Layer-by-layer training and local cost functions |
| bp_freeform | Advanced | Free-form | Relate barren plateaus to the 2-design property |

### Noise and Mitigation (28 problems, sample below)

| ID | Difficulty | Mode | Topic |
|---|---|---|---|
| noise_depolarising | Beginner | MC | Depolarising channel effect on VQA gradients |
| noise_zne | Intermediate | MC | Zero-noise extrapolation — Richardson extrapolation |
| noise_pec | Advanced | MC | Probabilistic error cancellation quasi-probability |
| noise_freeform | Advanced | Free-form | Compare ZNE and PEC trade-offs in near-term VQA |

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

Save each problem as its own file inside the appropriate `problems/<category>/`
directory, assigned to a module-level `PROBLEM`. `problems/__init__.py` auto-discovers
every problem file, so no registration step is needed.

## Data files

Written under `~/.local/share/quantum-study/`, or `$QUANTUM_STUDY_DATA_DIR` if set:

| File | Holds |
|---|---|
| `vqa_history.json` | every finished session; read by `coach.py` and `dashboard.py` |
| `vqa_flagged.json` | items you flagged for review (the coach's review queue) |
| `vqa_settings.json` | preferences |
| `mistakes.json`, `confidence.json` | the mistake journal and the confidence ratings, shared by all ten apps |

## Code and tests

The app is the package `quantum_study/vqa_trainer/`. What it shares with the other nine (the data directory, the journals, the theme, the Reference screen) is in [`quantum_study/common/`](../common/README.md).

```bash
pytest quantum_study/vqa_trainer        # this app's tests
```
