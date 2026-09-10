# Contributing

Thanks for helping. The most valuable contributions are **corrections** (a wrong
answer, a stale Qiskit API, an arithmetic slip in a worked example) and **new bank
items** (flashcards, problems, katas, exam questions). Both are small, self-contained
files, and this guide shows exactly what they look like.

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Dev setup

```bash
git clone https://github.com/matthewscottconroy/quantum-computing-study-suite.git
cd quantum-computing-study-suite
./setup.sh --dev              # .venv + requirements.txt + requirements-dev.txt (pytest, Jupyter)
source .venv/bin/activate
```

Python 3.12+ recommended (developed on 3.14; CI runs 3.12 and 3.14 — `setup.sh` accepts
3.11 as its minimum, but nothing tests it). The suite targets Qiskit 2.x —
code that uses retired APIs (`execute()`, `bind_parameters`, V1 primitives, the
`ibm_quantum` channel) is a bug, not a style choice.

## Running the checks

```bash
bash tools/run_tests.sh                  # everything: root suite + every app suite (extra args are forwarded, e.g. -x -vv)
pytest                                   # root suite only: coach.py, dashboard.py, launch.py, tools/verify_docs.py
(cd qec-trainer && python -m pytest)     # one app — each app has tests/ + pytest.ini
(cd qiskit-dojo && python -m pytest -m slow tests/test_sweep.py)   # runs all 36 kata solutions (~30 s)
python tools/verify_docs.py --all        # docs + lesson-plans regression gate
python tools/verify_docs.py --no-snippets   # static checks only (no venv needed)
for nb in notebooks/*.ipynb; do MPLBACKEND=Agg jupyter execute "$nb"; done   # in memory, as CI does; --inplace would rewrite the tracked notebooks
```

Rules the harness relies on:

- **One pytest process per app.** Several apps share top-level package names (`core/`,
  `problems/`, `ui/`), so `pytest` from the repo root deliberately only collects `tests/`
  (console tools). `tools/run_tests.sh` loops over the apps for you.
- **Never touch real study data.** Every conftest sets `QUANTUM_STUDY_DATA_DIR` to a temp
  directory and, for the apps that do not read the variable (listed under Conventions),
  monkeypatches their `DATA_DIR` / `_DATA_DIR` constants; if you write a script or test
  that reads persistence, do the same. The real directory is `~/.local/share/quantum-study/`.
- **Headless Qt.** Set `QT_QPA_PLATFORM=offscreen` when running app tests without a display
  (CI does; every app conftest defaults it with `os.environ.setdefault`).
- Tests slower than ~30 s carry `@pytest.mark.slow` and are deselected by default.

## Repository layout in one screen

```
<app>/                 one of the 10 PyQt6 apps (see README "Architecture Notes")
  config.py            model id (MODEL or CLAUDE_MODEL), API_KEY_FILE, and for most apps DATA_DIR
  core/models.py       dataclasses — the bank item types documented below
  <bank dir>/          one file per item, auto-discovered (cards/, problems/, katas/, bank/, derivations/)
  persistence.py       history + *_flagged.json read/write (flashcard-drill: persistence/storage.py)
  tests/               pytest suite, pytest.ini
docs/                  58 chapter files in 8 numbered chapters + README.md (the ladder)
lesson-plans/          12 curricula; python blocks in 06/07/10 are executed by verify_docs
notebooks/ labs/ projects/   executable companions, IBM runtime labs, capstone specs
coach.py dashboard.py  console tools; tests in tests/ (with launch.py and verify_docs)
tools/verify_docs.py   corpus regression checker
launch.py setup.sh     launcher and bootstrap
```

## Conventions every app follows

- Model ID `claude-sonnet-4-6`, set once in each app's `config.py`.
- API key lookup: `ANTHROPIC_API_KEY` env var, then `~/.config/quantum-study/api_key.txt`.
- **Apps must launch with no key.** Offline features (banks, reference browser, history,
  model solutions) work; only generate/grade/review actions may fail, with a clear message.
- History and flags go to `DATA_DIR` (`~/.local/share/quantum-study/`), as JSON, append-only.
  New code resolves it as `Path(os.environ.get("QUANTUM_STUDY_DATA_DIR") or
  Path.home() / ".local/share/quantum-study")`, as `flashcard-drill/config.py`,
  `qiskit-dojo/config.py`, `math-quiz/persistence.py`, `quantum-quiz/persistence.py`,
  `coach.py` and `launch.py` already do. circuit-trainer, exam-sim, paper-drill,
  problem-trainer, qec-trainer, vqa-trainer and `dashboard.py` still hard-code the default
  path — a known gap, not a convention to copy.
- Review flags follow one contract: `<prefix>_flagged.json` (prefix = the app's history
  prefix: `qec_`, `quiz_`, `math_`, `trainer_`, `paper_`, `dojo_`, `problems_`, `vqa_`;
  flashcard-drill's legacy file is `flagged_cards.json`) holding a JSON list of
  `{"id", "label", "category", "app", "timestamp"}` (only `id` required). Entries are
  either that dict shape or — in the legacy files `flagged_cards.json`, `qec_flagged.json`
  and `vqa_flagged.json`, whose writers still dump a sorted list of id strings — bare
  strings; readers must accept both (`coach._flag_entry` does). New writers use the dict
  shape. Flagging is a toggle, and each app lists its flags with an Unflag control on its
  History screen (qec-trainer and vqa-trainer do not yet; they unflag from the result
  screen). `coach.py --review` discovers these files by name — a new app joins the review
  queue with no coach changes.
- Every app has a Reference screen (`ui/screens/reference_screen.py`, opened from the
  setup/home screen, with a Back button) that renders `<repo>/docs/**/*.md`; the docs root
  is `Path(__file__).resolve().parents[3] / "docs"` — never hard-code a home path.

---

## Adding content

All static banks use the same mechanism: **one file per item, discovered at start-up by
walking the bank directory**. The loader imports every `*.py` (except `__init__.py`) and
keeps the module-level constant it expects (`CARD`, `PROBLEM`, `KATA`, `QUESTION`,
`DERIVATION`). Directories starting with `_` are skipped, and an import error makes the
item silently vanish — which is why each bank has a test that pins the item count and (in
every bank except exam-sim) checks one loaded item per file or that the set of file stems
equals the set of ids. **The file stem must equal the item's `id`.** One caveat: never
name a bank file `test_*.py` or `*_test.py`. Every `pytest.ini` sets `testpaths = tests`,
so a bare `pytest` never reaches the bank, but pytest collects such files when it is given
an explicit path or run from inside the bank directory — so an item
whose natural id ends in `_test` gets a longer file name (`alg_swap_test_circuit.py`,
`alg_hadamard_test_circuit.py`, `cc_if_test_control_flow.py` keep their original ids so
saved history still matches; they are the only exceptions).

Each bank test also pins the total (`EXPECTED_CARD_COUNT = 550`, `EXPECTED_COUNT = 178`,
…). When you add an item, bump that constant in the same PR and update the count in the
app's README; that is intentional — it makes accidental deletions fail loudly.

### Flashcard — `flashcard-drill/cards/<category_dir>/<id>.py`

```python
"""Card: pauli_anticommute"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='pauli_anticommute',            # == file stem; [A-Za-z0-9_-]+, unique across the bank
    category='Pauli Matrices',         # display name; the category list is derived from the cards
    front='{X, Z} = ?  (anticommutator)',
    back='{X, Z} = XZ + ZX = 0  — all distinct Paulis anticommute',
    # latex: bool = False              # optional; render the back with math markers
)
```

Discovery: `cards/__init__.py::all_cards()` walks `cards/<dir>/*.py` and collects `CARD`.
A new category is just a new directory whose cards share a new `category` string (it
appears in the setup screen automatically). Test to bump: `tests/test_cards.py`
(`EXPECTED_CARD_COUNT`, `EXPECTED_CATEGORY_COUNT`). Keep the front a single recall cue and
the back a one-line answer; put derivations in the docs, not on the card.

### QEC problem — `qec-trainer/problems/<category_dir>/<id>.py`

```python
"""Problem: bos_binomial_code"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_binomial_code',            # == file stem
    category='Bosonic Codes',          # one of the 6 category strings (tests pin the set)
    difficulty='intermediate',         # 'beginner' | 'intermediate' | 'advanced'
    question='The binomial code ... codewords use Fock states:',
    choices=[                          # MC: >= 2 distinct, non-empty; free-form: []
        'Spaced L+1 apart in photon number ...',
        'Only the vacuum |0⟩ and single-photon |1⟩ states',
        'Coherent superpositions of all Fock states up to |L⟩',
        'Only even Fock states for bit-flip protection',
    ],
    correct_index=0,                   # index into choices; -1 for free-form
    explanation='...',                 # shown after submission; also the model answer for free-form
    hints=['Fock state spacing L+1 ensures L losses cannot confuse the codewords.'],
    grade_mode=GradeMode.AUTO,         # AUTO (MC, graded locally) | CLAUDE (free-form, API)
)
```

Discovery: `problems/__init__.py::all_problems()`, categories derived from the problems.
Tests: `tests/test_bank.py` (`EXPECTED_COUNT`, `EXPECTED_CATEGORIES`; AUTO problems must
have a valid `correct_index`, CLAUDE problems must have `choices == []`). Prefer AUTO —
it works offline. Any numeric claim in `question`/`explanation` (a syndrome, a distance,
a threshold) must be checked by a script before you commit it; the 2026 audit found the
old wrong answers precisely in un-scripted problems.

### VQA problem — `vqa-trainer/problems/<category_dir>/<id>.py`

Same `Problem` shape as QEC plus a numeric mode:

```python
PROBLEM = Problem(
    id='qoc_pi_pulse_time',
    category='Optimal Control',        # one of the 7 category strings
    difficulty='intermediate',
    question='... Enter your answer in microseconds (μs).',
    choices=[], correct_index=-1,
    correct_value=0.5,                 # numeric answer (float)
    tolerance=0.001,                   # absolute tolerance for full credit
    explanation='t = π/Ω = 1/(2×10⁶) s = 0.5 μs ...',
    hints=['π-pulse condition: Ω·t = π.'],
    grade_mode=GradeMode.AUTO,         # AUTO = numeric | MC = multiple choice | CLAUDE = free-form
)
```

State the unit and the expected precision in the question. Numeric answers within 20×
tolerance earn partial credit, so pick a tolerance that reflects the rounding in your
explanation. Tests: `tests/test_bank.py` (`EXPECTED_COUNT`, `EXPECTED_CATEGORIES`).

### Dojo kata — `qiskit-dojo/katas/<section_dir>/<id>.py`

```python
"""Kata: cc_bell_state"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc_bell_state",                # == file stem
    section="Create circuits",         # must be in katas/__init__.py::SECTION_ORDER
    title="Build a Bell state",
    difficulty="beginner",             # 'beginner' | 'intermediate' | 'advanced'
    prompt="""Build a 2-qubit QuantumCircuit named `qc` that prepares (|00> + |11>)/sqrt(2) ...""",
    starter_code="""from qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2)\n# TODO\n""",
    test_code="""import numpy as np
from qiskit.quantum_info import Statevector
assert isinstance(qc, QuantumCircuit), "qc must be a QuantumCircuit"
sv = Statevector.from_instruction(qc)
assert sv.equiv(Statevector(np.array([1, 0, 0, 1]) / np.sqrt(2))), f"State is {np.round(sv.data, 3)} ..."
print("Bell state prepared correctly.")
""",
    solution_code="""from qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n""",
    hints=["One Hadamard, one CX.", "H on qubit 0, then CX(0, 1)."],   # 2–3, progressive
)
```

The harness (`core/runner.py`) writes the learner's code and `test_code` to a temp
directory and runs a small driver in a subprocess (`config.RUN_TIMEOUT_SECS = 20`,
`MPLBACKEND=Agg`; interpreter = the active venv, else `../.venv/bin/python`, else
`qiskit-dojo/.venv/bin/python`, else `sys.executable`). The driver `exec`s the user code
into a fresh namespace and then the tests into that *same* namespace, so name the objects
the prompt asks for. Outcomes (`RunResult.phase`): an exception in the learner's code →
`user_error`; an `AssertionError` *or any other exception* raised inside the tests →
`test_failed` (the latter is printed under "Error while running tests"); exceeding the
time limit → `timeout`; any other exit code, or a failure to launch the interpreter →
`crash`. Every assertion message should tell the learner *what* was wrong. `hints` must be
non-empty (2–3 progressive hints by convention). A new section needs an entry in
`SECTION_ORDER`. Tests: `tests/test_katas.py` (`EXPECTED_KATA_COUNT`; ids match file
stems; all three code fields must compile) and the slow sweep `tests/test_sweep.py`, which
requires that **every `solution_code` passes and no `starter_code` already passes** — run
it: `python -m pytest -m slow tests/test_sweep.py`.

### Exam question — `exam-sim/bank/<section_dir>/<id>.py`

```python
"""Question: cc_assign_parameters_copy"""
from core.models import Question

QUESTION = Question(
    id='cc_assign_parameters_copy',    # == file stem
    section='Create circuits',         # one of the 8 keys of config.SECTIONS
    question='What does this print?\n\n```python\n...\n```',   # fenced code blocks render
    options=[ 'A ...', 'B ...', 'C ...', 'D ...' ],             # exactly 4, distinct
    correct_index=0,
    explanation='assign_parameters() returns a new bound circuit by default ...',
    difficulty='medium',               # 'easy' | 'medium' | 'hard'
)
```

Exams are drawn **proportionally to `config.SECTIONS`** (section → count in the bank,
mirroring the exam weights; `BANK_SIZE = sum(SECTIONS.values())`), and
`tests/test_bank.py` pins those per-section counts in `DOCUMENTED_SECTIONS` plus the
literal total (110), so adding a question means bumping the section's number in
`config.SECTIONS` and in `DOCUMENTED_SECTIONS`, and the pinned total in the same test
file. Questions must be **original** study material — never
reproduce real exam content — and every code snippet must have been executed on
Qiskit 2.x with the printed output confirmed. Write distractors that encode real
misconceptions (bit ordering, retired APIs, ISA requirements).

### Problem-trainer problem — `problem-trainer/problems/<topic_dir>/<id>.py`

```python
"""Problem: la_pauli_algebra — Pauli algebra and qubit rotations."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="la_pauli_algebra",             # == file stem
    topic="Linear Algebra & QM Math",  # one of the 6 topic strings (derived from the bank)
    title="Pauli Algebra, Operator Expansion, and Rotations",
    statement="Let σ₁ = X, σ₂ = Y, σ₃ = Z ... (shared setup for all parts)",
    parts=[
        Part(
            part_id="a",
            prompt="Prove σᵢσⱼ + σⱼσᵢ = 2δᵢⱼ I and deduce (n̂·σ)² = I.",
            points=3,                  # weight of this part in the 0–10 problem score
            rubric=[                   # grader-facing: each bullet is a thing that earns credit
                "Establishes σᵢ² = I and anticommutation for i ≠ j.",
                "Expands (n̂·σ)² and symmetrises so cross terms cancel.",
                "Concludes (Σ nᵢ²) I = I using |n̂| = 1.",
            ],
            model_solution="Direct computation gives X² = Y² = Z² = I ...",
        ),
        # Part(part_id="b", ...), ...
    ],
)
```

Guided derivations live one level up in `problem-trainer/derivations/<id>.py` as a
`DERIVATION = Derivation(id, title, goal, steps=[Step(step_id, prompt, expected, hint,
model_step), ...])`; `expected` is what the grader checks against, `model_step` is what
the learner sees on reveal. Both registries auto-discover (`problems/<dir>/*.py`,
`derivations/*.py`). Tests: `tests/test_banks.py` (`EXPECTED_PROBLEMS`,
`EXPECTED_DERIVATIONS`). Rubric bullets should be checkable statements, not restatements
of the prompt; model solutions are read by learners, so show the algebra.

### circuit-trainer, quantum-quiz, math-quiz, paper-drill

These generate problems rather than load them. circuit-trainer categories are generator
modules (`circuit-trainer/problems/<category>.py` exposing `generate(difficulty) -> Problem`);
a new category needs a member in `core.models.ProblemCategory` and a branch in the
`problems/__init__.py::generate` dispatcher. Answers come from `qiskit.quantum_info` — the
`Statevector` / `Operator` of the generated circuit, via the helpers in `problems/_utils.py`
(the noise category is analytic) — so a new generator must derive its answer from that
computation, never from a hand-typed value. quantum-quiz and math-quiz topics live in `core/topics.py`
(`TOPICS: dict[subject, list[topic]]`); `tests/test_topics_and_contexts.py` pins
quantum-quiz at 11 subjects / 124 topics and `tests/test_topics.py` pins math-quiz at
13 subjects, so bump those when you add a topic.

---

## Docs style rules (`docs/` and `lesson-plans/`)

The corpus is meant to be *trusted*. Rules:

1. **Inline math in backticks; display math as fenced text or `$$` blocks.** Inline
   expressions go in backticks — `` `|ψ⟩ = α|0⟩ + β|1⟩` ``, `` `e^{-iθn̂·σ/2}` `` — and
   **never** in single dollars: no `$...$` anywhere. A display equation stands alone on
   its own lines, either as a fenced block (```` ``` ```` … ```` ``` ````, plain text with
   Unicode symbols) or as a `$$ … $$` block (LaTeX). Unicode (`⟨`, `⊗`, `√`, `σ`,
   subscripts) is preferred to ASCII spelling-out inside backticks. Qiskit is
   little-endian; when a formula is big-endian, say so.
2. **Every chapter file ends in the same five sections, in this order:**
   `## Key Formulas` → `## Worked Example` → `## Summary` → `## Exercises` →
   `## Further Reading`. A heading may carry a suffix after the fixed words
   (`## Worked Example: Grover on 3 qubits`, `## Key Formulas and Containments`) but must
   start with them. `verify_docs.py --structure` enforces only Exercises and Further
   Reading; the other three, and the order, are convention and reviewers will ask for them.
3. **Exercise / solution block format** — 3–5 exercises, each with a fully worked solution
   in a collapsible block:

   ````markdown
   **Exercise 2**: Expand `A = [[1,2],[2,-1]]` in the Pauli basis.

   <details><summary>Solution</summary>

   `a = ½Tr(A) = 0`, `b = ½Tr(XA) = 2`, `c = ½Tr(YA) = 0`, `d = ½Tr(ZA) = 1`, so `A = 2X + Z`.
   Check: `2X + Z = [[1,2],[2,-1]]` ✓

   </details>
   ````

   The blank lines inside `<details>` are required for the Markdown to render. Exactly the
   text `<summary>Solution</summary>`; one `<details>` per exercise; number the items
   `**Exercise N**:` (or `**N.**`). `--structure` checks that the tags balance, that every
   block carries the Solution summary and that the Exercises section has recognizable items.
4. **Every printed number is verified by a script.** If a worked example or solution states
   a value (`P ≈ 0.961`, `E₀ = −1.857275 Ha`, `p_th ≈ 1%` from a fit, a syndrome table),
   you must have computed it — numpy/Qiskit in a throwaway script or, better, a cell in the
   chapter's `notebooks/chNN.ipynb` with an `assert`. Include the check in the PR description.
   "Verified numerically" comments in bank files should say *what* was verified.
5. **No AI leftovers.** `verify_docs.py --lint` rejects drafting self-talk ("wait, let
   me…", "hmm,", "let me recompute", "let me verify:"), `TODO`/`FIXME` and `XXX ` markers,
   and stranded `·...` fragments.
6. **Links resolve.** Repo-relative `.md` links (and `/`-terminated directory links) and
   backtick-quoted `.md` paths are checked by `--crossrefs` (`.py`, `.ipynb` and other
   backtick paths are not); if you add a chapter file, add it to the chapter's file-map table in
   `docs/README.md` (`--readme` checks the map).
7. **Lesson-plan Python blocks run.** Blocks in `lesson-plans/06-qiskit.md`, `07-qasm.md`
   and `10-transpiling.md` are executed cumulatively by `--snippets`; if a block genuinely
   needs IBM hardware, start it with `# verify: skip — reason`.

Run `python tools/verify_docs.py --all` before opening the PR; it must exit 0.

---

## Pull request checklist

- [ ] Branch from `main`; one topic per PR (a bank addition, a docs fix, an app change).
- [ ] `tools/run_tests.sh` passes locally (or the affected app's suite plus the root suite).
- [ ] `python tools/verify_docs.py --all` exits 0 if you touched `docs/` or `lesson-plans/`.
- [ ] New bank items: file stem == `id`; count constant bumped in the bank test; README
      count updated; for exam-sim, `config.SECTIONS` and `DOCUMENTED_SECTIONS` updated;
      for dojo, the slow sweep passes.
- [ ] Every number you added or changed was checked by a script — say how in the description.
- [ ] Qiskit code is 2.x-current and was executed (state the version).
- [ ] No API key, no personal data, nothing from `~/.local/share/quantum-study/`, and no
      real exam content in the diff.
- [ ] App changes launch with `QT_QPA_PLATFORM=offscreen` and without an API key.
- [ ] Docs math: inline in backticks, display as fenced text or `$$` blocks, no inline `$`;
      chapter files keep the five-section ending.

Open an issue first for anything larger than a bank item or a fix — a new app, a new
chapter, a change to the flagging/persistence contract — so the design can be agreed
before the work.

## Reporting problems

Use [GitHub issues](https://github.com/matthewscottconroy/quantum-computing-study-suite/issues).
For a wrong answer or a technical error in the content, quote the file path and the exact
claim, and if you can, the calculation that contradicts it — that turns a report into a fix.
