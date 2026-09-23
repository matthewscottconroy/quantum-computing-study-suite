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
./setup.sh --dev              # .venv + requirements.txt + requirements-dev.txt (pytest, Jupyter, genanki)
source .venv/bin/activate
```

`make dev` is the same command. The `Makefile` only ever shells out to the repository's
own scripts, so every `make` target below has a plain-command twin you can run instead.

Python 3.12+ recommended (developed on 3.14; CI runs 3.12 and 3.14 — `setup.sh` accepts
3.11 as its minimum, but nothing tests it). The suite targets Qiskit 2.x —
code that uses retired APIs (`execute()`, `bind_parameters`, V1 primitives, the
`ibm_quantum` channel) is a bug, not a style choice.

## Running the checks

```bash
make test                                # == bash tools/run_tests.sh: root suite + every app suite (make test ARGS="-x -vv" forwards flags)
pytest                                   # root suite only: coach.py, dashboard.py, launch.py, tools/verify_docs.py
(cd qec-trainer && python -m pytest)     # one app — each app has tests/ + pytest.ini
(cd qiskit-dojo && python -m pytest -m slow tests/test_sweep.py)   # runs all 72 solutions and 72 starters (a few minutes)
make docs                                # == python tools/verify_docs.py --all: docs + lesson-plans regression gate
python tools/verify_docs.py --no-snippets   # static checks only (no venv needed)
make notebooks                           # executes every notebook with nbclient, outputs not written back (CI: jupyter execute)
make lint                                # mypy over coach.py, dashboard.py, launch.py, tools/ — advisory; the baseline is not clean yet
make coverage                            # root suite under coverage.py; [tool.coverage] and [tool.mypy] live in pyproject.toml
make export                              # tools/export_cards.py --all -> exports/ (cards.json, quantum-study.apkg, index.html)
```

`make help` lists every target. CI runs `tools/run_tests.sh` and `verify_docs.py --all`
on Python 3.12 and 3.14 (the slow sweep is opt-in everywhere; notebooks have their own
workflow); `lint` and `coverage` run on the 3.14 leg only, and `lint` cannot fail the build
until its baseline reaches zero — do not add new mypy errors, but you are not expected to
clear the old ones in an unrelated PR.

Rules the harness relies on:

- **One pytest process per app.** Several apps share top-level package names (`core/`,
  `problems/`, `ui/`), so `pytest` from the repo root deliberately only collects `tests/`
  (console tools). `tools/run_tests.sh` loops over the apps for you.
- **Never touch real study data.** Every conftest sets `QUANTUM_STUDY_DATA_DIR` to a temp
  directory **and** monkeypatches the module's path constants (`DATA_DIR`, `HISTORY_FILE`,
  `MISTAKES_FILE`, `CONFIDENCE_FILE`, …). Both are needed: every app reads the variable, but
  it reads it once, when `config.py` / `persistence.py` is imported, so a test that has
  already imported the module would otherwise still hold the real path. If you write a
  script or test that reads persistence, do the same. The real directory is
  `~/.local/share/quantum-study/`, and nothing in a PR may write to it.
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
docs/                  70 chapter files in 11 numbered chapters + README.md (the ladder, Rung 1 -> 11)
lesson-plans/          12 curricula, every exercise with a <details> solution; python blocks in 06/07/10 are executed by verify_docs
notebooks/ labs/ projects/   executable companions, IBM runtime labs, capstone specs
coach.py dashboard.py  console tools; tests in tests/ (with launch.py and verify_docs)
tools/verify_docs.py   corpus regression checker
tools/export_cards.py  flashcards -> cards.json / Anki .apkg / web deck (templates in tools/webdeck/)
tools/gen_cloze.py     generates flashcard-drill/cards/cloze/ from every chapter's Key Formulas
tools/concept_map.py   prerequisite DAG (tools/concept_graph.json) with a mastery overlay
tools/sync_history.sh  the study-history dir as its own git repo, synced to a private remote
tools/daily_nudge.sh tools/install_nudge.sh   coach.py plan as a desktop notification, and its timer/cron installer
launch.py setup.sh     launcher and bootstrap
Makefile pyproject.toml   task runner (wraps the scripts above); packaging, mypy and coverage config
.github/               ci.yml, notebooks.yml, pages.yml (web deck), release.yml, dependabot.yml, issue forms, PR template
```

## Conventions every app follows

- Model ID `claude-sonnet-4-6`, set once in each app's `config.py`.
- API key lookup: `ANTHROPIC_API_KEY` env var, then `~/.config/quantum-study/api_key.txt`.
- **Apps must launch with no key.** Offline features (banks, reference browser, history,
  model solutions) work; only generate/grade/review actions may fail, with a clear message.
- History and flags go to `DATA_DIR` (`~/.local/share/quantum-study/`), as JSON, append-only.
  Resolve it as `Path(os.environ.get("QUANTUM_STUDY_DATA_DIR") or
  Path.home() / ".local/share/quantum-study")` — all ten apps, `coach.py`, `dashboard.py`,
  `launch.py` and `tools/concept_map.py` now do, so there is no longer an app whose
  behaviour you may copy as an exception. The variable is read at import time; do not cache
  the resolved path anywhere a test cannot monkeypatch it.
- **History schemas are frozen.** `coach.py` and `dashboard.py` parse every
  `*_history.json`; never change an existing file's shape — add a new file instead, as
  flashcard-drill did with `flashcard_schedule.json` (SM-2 state) rather than touching
  `flashcard_history.json`.
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
- **Two cross-app journals, one schema each** — see *The mistake and confidence contracts*
  below. Every app writes `mistakes.json` and `confidence.json`; a new app is expected to,
  and gets `coach.py --mistakes` / `--calibration` and both dashboard panels for free.
- Every app has a Reference screen (`ui/screens/reference_screen.py`, opened from the
  setup/home screen, with a Back button) that renders `<repo>/docs/**/*.md`; the docs root
  is `Path(__file__).resolve().parents[3] / "docs"` — never hard-code a home path.

---

## The mistake and confidence contracts

Two files in the shared data directory are written by **every** app and read only by
`coach.py` (`--mistakes`, `--calibration`, `--item-analysis`, and `--review`) and
`dashboard.py` (two panels). They are the reason a new app gets error analysis for free,
and the reason a new app must not invent its own shape. Neither file is an app's own
history: they are additions alongside the frozen `*_history.json` schemas, never changes
to one.

### `mistakes.json` — one record per wrong answer

A flat JSON list. Every record:

```json
{
  "id":             "qec_surface_d3_syndrome",
  "app":            "qec-trainer",
  "category":       "Surface Code",
  "question":       "first 200 chars of the prompt",
  "your_answer":    "first 200 chars",
  "correct_answer": "first 200 chars",
  "cause":          "confused",
  "note":           "free text, <= 500 chars",
  "timestamp":      1758600000.0,
  "resolved":       false
}
```

| Field | Rule |
|---|---|
| `id` | the bank item's id — the same id your `*_flagged.json` and history use, so the two line up |
| `app` | the app's directory name (`qec-trainer`, `flashcard-drill`, …). Every record carries it: one file serves ten apps |
| `category` | the app's own category string, exactly as its history spells it |
| `question` / `your_answer` / `correct_answer` | clipped to 200 characters each. Clip, never omit — a record with no text is unreadable in `--mistakes` |
| `cause` | exactly one of `misread`, `didnt_know`, `knew_but_slipped`, `confused`, `out_of_time`, `other` — **or `null`** for "logged, not categorised yet". Never invent a seventh cause; anything unrecognised is stored as `null` rather than rejected, so a stray value loses the category and not the mistake |
| `note` | optional free text, clipped. The cap is the app's own — qec-trainer allows 500, flashcard-drill 200 — so a reader must not assume a length |
| `timestamp` | UNIX seconds, float |
| `resolved` | `false` when logged; set `true` when the learner answers that item correctly again |

Behaviour the apps agree on, not just the shape:

- **Log first, categorise second.** The record is written the moment the answer is graded
  wrong, with `cause: null`. The cause pills are a second, optional step — skipping them
  must cost the learner nothing but the category.
- **One open record per `(app, id)`.** Re-missing the same item refreshes the existing
  unresolved record instead of appending a duplicate, and a cause already chosen for it
  survives the refresh.
- **Resolution is automatic.** A later correct answer to the same `(app, id)` sets
  `resolved: true`; nothing asks the learner to tidy up.
- **Bounded growth.** The file is trimmed on write, to 2000 mistake records. Either
  strategy in the tree is fine to copy: qec-trainer keeps the newest 2000 overall, sorting
  by `timestamp`; flashcard-drill keeps the newest 2000 *of its own* rows and never touches
  another app's. What is not fine is dropping other apps' rows in preference to your own,
  or letting the file grow without a bound.

### `confidence.json` — one record per rated answer

```json
{"id": "...", "app": "qec-trainer", "category": "Surface Code",
 "confidence": 3, "correct": false, "timestamp": 1758600000.0}
```

`confidence` is an integer 1–4 (1 guessing, 2 unsure, 3 fairly sure, 4 certain), captured
**before the answer is revealed** — a rating taken afterwards is not calibration data and
must not be written. Rating is optional and per-app switchable; when the learner skips it
or switches it off, write **nothing** (do not write a default, a 0 or a null). Out-of-range
values are dropped, not clamped into the record. Trim on write to 5000, by the same rule
as `mistakes.json`.

### Implementing it in a new app

- Put the paths in `config.py` as `MISTAKES_FILE = DATA_DIR / "mistakes.json"` and
  `CONFIDENCE_FILE = DATA_DIR / "confidence.json"` so tests can monkeypatch them.
- Keep the read/write helpers Qt-free in `persistence.py` (flashcard-drill uses
  `persistence/review_store.py`) so they can be unit tested without a QApplication.
  `qec-trainer/persistence.py` is the reference implementation; `coach.py` re-exports
  `dashboard.py`'s `make_mistake_entry`, `make_confidence_entry`, `normalise_mistake`,
  `normalise_confidence` and `cause_of` if you would rather import the schema than
  restate it.
- Write atomically (temp file + replace) **and under the journal lock** — two apps may be
  open at once, and an atomic write is only half the answer: the *read* in a
  read-modify-write goes stale the moment another app appends, and the rewrite then drops
  that app's new rows (measured: three writers, 60 rows each, 103 of 180 rows survived).
  Copy `journal_sync.py` from any app tree (the copies are byte-identical, and
  `tests/test_journal_concurrency.py` asserts that) and wrap the whole read-modify-write
  in `journal_sync.lock(MISTAKES_FILE, create=True)`, re-reading the file *inside* the
  lock. It flocks a `<file>.lock` sidecar, waits at most five seconds, always releases
  (including on a crash) and degrades to the unlocked behaviour where locking is
  unavailable rather than raising or hanging a GUI.
- **Never rewrite another app's rows.** On every write, pass the list through
  `journal_sync.merge_foreign(rows_on_disk, entries, APP_ID)`: rows whose `app` is not
  yours are written back exactly as they were read, unknown keys included, and rows that
  appeared since you read are kept. Only your own rows go through your schema.
- **Tolerate everything on read.** A missing, empty, truncated or non-list file must read
  as "no records", never as an exception. The console reports print "no data" and that is
  the correct outcome.
- Never write to either file from `coach.py` or `dashboard.py`. Reading is theirs; writing
  is the app's.
- Add tests alongside the existing `test_mistake_journal.py` / `test_mistakes_confidence.py`
  suites: a round trip, the `cause: null` path, the duplicate-refresh rule, resolution, and
  a corrupt file reading as empty.

### Regenerating the cloze deck

`flashcard-drill/cards/cloze/` is **generated, not hand-written** — one file per card,
produced from the `## Key Formulas` section of every chapter under `docs/`. Edit the
chapter, not the card.

```bash
python tools/gen_cloze.py                # == --dry-run: report only, writes nothing
python tools/gen_cloze.py --write        # (re)generate the cards
python tools/gen_cloze.py --sample 20 --seed 7   # print cards to eyeball
python tools/gen_cloze.py --clean        # remove every generated card
```

`--write` is idempotent: a card's id hashes its source path, label and left-hand side, so
a file is rewritten only when its bytes change and a card whose formula disappeared is
deleted. Run it after any edit to a Key Formulas section, and commit the resulting card
files — the app loads files, not the generator.

The generator is deliberately lossy. LaTeX conversion is a whitelist, and anything it does
not recognise — an unknown command, a matrix or cases environment, a clause mixing `=`
with `≤`, an ellipsis, an answer long enough to be an essay — is **dropped**. A missing
card is acceptable; a garbled card is not. If a formula you added produces no card, that is
the gate working; rewrite the formula in the corpus style rather than loosening the
generator. `flashcard-drill/tests/test_cards.py` holds the deck to *floors*
(`MIN_CARD_COUNT`, `MIN_CURATED_CARDS`, `MIN_CLOZE_CARDS`), so regeneration never turns the
suite red as long as the deck does not shrink.

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

Each bank test also pins the size. Most pin an **exact** total (qec-trainer's
`EXPECTED_COUNT = 178`, vqa-trainer's `EXPECTED_COUNT = 179`, exam-sim's
`BANK_TOTAL = 300`): when you add an item, bump that constant in the same PR and update the
count in the app's README. That is intentional — it makes accidental deletions fail loudly.
Two banks assert **floors** instead, because they grow on their own: qiskit-dojo
(`MIN_KATA_COUNT = 72` plus a per-section table), so adding a kata needs no test edit — but
still update its README's section table; and flashcard-drill, whose `cards/cloze/` category
is regenerated from the corpus by `tools/gen_cloze.py`. Its `tests/test_cards.py` carries
three floors — `MIN_CARD_COUNT` (whole deck), `MIN_CURATED_CARDS` (hand-written only) and
`MIN_CLOZE_CARDS` (generated only) — with the observed count noted beside each. Two floors,
not one, so a growing generated deck can never mask a shrinking hand-written one.

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
appears in the setup screen automatically) — add it to `REQUIRED_CATEGORIES` in
`tests/test_cards.py` so a directory that stops loading fails loudly. The size assertions
there are floors (`MIN_CARD_COUNT`, `MIN_CURATED_CARDS`, `MIN_CLOZE_CARDS`,
`MIN_CARDS_PER_CATEGORY`), so a hand-written card needs no constant bumped; raise a floor
only when you want to protect new ground. Keep the front a single recall cue and the back a
one-line answer; put derivations in the docs, not on the card. Do not hand-write anything
under `cards/cloze/` — that directory is generated (see *Regenerating the cloze deck*).

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
`crash`. Every assertion message should tell the learner *what* was wrong.

What `tests/test_katas.py` enforces on every kata (all fast, run them first):

- the file lives in `katas/<section_dir>/` where `section_dir` is the section name
  lower-cased with spaces as underscores (`Results analysis` → `results_analysis/`), and
  the file stem equals `id`;
- `section` is in `katas/__init__.py::SECTION_ORDER` (a new section needs an entry there
  *and* a floor in the test's `SECTION_TARGETS` table — the bank is held at or above
  10/9/8/7/7/6/6/3 katas across the eight exam sections plus 8 Debugging and 8
  Modernization, `MIN_KATA_COUNT = 72`, so adding katas never turns the suite red but
  losing one does);
- **2–3 distinct hints**, progressive; a unique `title`; in the Debugging and
  Modernization sections the title starts with `Fix it:` / `Modernize:` because the
  starter is deliberately broken;
- `test_code` contains at least one `assert`, `solution_code` differs from
  `starter_code`, and all three code fields compile.

Then the slow sweep `tests/test_sweep.py` requires that **every `solution_code` passes and
no `starter_code` already passes** — run it: `python -m pytest -m slow tests/test_sweep.py`
(145 subprocess runs; a few minutes). Pick the section by exam blueprint weight: the sections with
the fewest katas relative to their weight are where a new kata is most useful.

### Exam question — `exam-sim/bank/<section_dir>/<id>.py`

```python
"""Question: cc_assign_parameters_copy"""
from core.models import Question

QUESTION = Question(
    id='cc_assign_parameters_copy',    # == file stem
    section='Create circuits',         # one of the 8 keys of config.SECTIONS
    question='What does this print?\n\n```python\n...\n```',   # fenced code blocks render
    options=[ 'A ...', 'B ...', 'C ...', 'D ...' ],             # exactly 4, distinct
    correct_index=0,                   # index into options — vary it across new questions (see below)
    explanation='assign_parameters() returns a new bound circuit by default ...',
    difficulty='medium',               # 'easy' | 'medium' | 'hard'
)
```

Step by step:

1. Pick the section, then the id: a lowercase slug starting with the section's two-letter
   prefix — `cc_` Create circuits, `qo_` Quantum operations, `rc_` Run circuits, `sa_`
   Sampler, `es_` Estimator, `vz_` Visualization, `ra_` Results analysis, `oq_` OpenQASM.
2. Save it as `bank/<section_dir>/<id>.py` (`section_dir` = section name lower-cased,
   spaces to underscores); the file stem must equal `id`.
3. Run the snippet on Qiskit 2.x and paste the *printed* output — a question goes into the
   bank only after its code has been executed and the output confirmed. Say so, with the
   Qiskit version, in the PR.
4. Bump `BANK_TOTAL` in `tests/test_bank.py` (the one exact count) and the section row in
   `exam-sim/README.md`, then `cd exam-sim && python -m pytest`.

`config.SECTIONS` holds the exam **weights** (20/18/16/13/13/12/11/7), not bank counts: it
drives how a 68-question mock is allocated across sections and does not change when the
bank grows. The rest of `tests/test_bank.py` checks the bank's *shape* rather than
per-section totals: every section present and at least sprint-sized (10), each section's
share of the bank within 2 percentage points of its exam weight (so a batch that lands
entirely in one section fails — spread additions to keep the proportions), ids unique and
matching file name, directory and prefix, exactly four distinct options, `correct_index`
in range, an explanation of at least 40 characters, balanced ``` fences, and no two
questions with identical text or the same code snippet with the same answer. The loader
silently skips a file that fails to import; `test_every_question_file_loads` reports the
real exception. One test is currently `xfail`: most of the bank stores the correct answer
at index 0 and the UI shows options in stored order — so put the correct option somewhere
other than `A` in anything new. Questions must be **original** study material — never
reproduce real exam content — and distractors should encode real misconceptions (bit
ordering, retired APIs, ISA requirements).

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
13 subjects (197 topics today), so bump those when you add a topic.

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
   in a collapsible block (lesson-plan exercises use the identical block, one per
   exercise, so a lesson without solutions is now a bug):

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
      count updated; for exam-sim, `BANK_TOTAL` in `tests/test_bank.py` bumped and the
      section proportions still within tolerance; for dojo, the slow sweep passes and the
      README section table is updated.
- [ ] Touched a `## Key Formulas` section? `python tools/gen_cloze.py --write` re-run and
      the regenerated `flashcard-drill/cards/cloze/` files committed.
- [ ] New app or new persistence code: `mistakes.json` and `confidence.json` written in the
      shared schema (no seventh cause, no rating written when the learner skipped it), both
      read tolerantly, and `QUANTUM_STUDY_DATA_DIR` honoured.
- [ ] Journal writes go through `journal_sync`: the whole read-modify-write inside
      `journal_sync.lock(...)` (re-reading in the lock) and every rewrite through
      `merge_foreign(...)`, with `tests/test_journal_concurrency.py` still green.
- [ ] Added a docs chapter or an app category? `python tools/concept_map.py --check`
      still passes, and the concept that teaches or drills it is in
      `tools/concept_graph.json`.
- [ ] Every number you added or changed was checked by a script — say how in the description.
- [ ] Qiskit code is 2.x-current and was executed (state the version).
- [ ] No API key, no personal data, nothing from `~/.local/share/quantum-study/`, and no
      real exam content in the diff.
- [ ] App changes launch with `QT_QPA_PLATFORM=offscreen` and without an API key.
- [ ] Docs math: inline in backticks, display as fenced text or `$$` blocks, no inline `$`;
      chapter files keep the five-section ending.

Open an issue first for anything larger than a bank item or a fix — a new app, a new
chapter, a change to the flagging / mistake / confidence contracts — so the design can be
agreed before the work. Those three contracts are cross-app: changing one means changing
ten apps plus `coach.py` and `dashboard.py` in the same PR, which is exactly why the
schemas are written down above.

## Reporting problems

Use [GitHub issues](https://github.com/matthewscottconroy/quantum-computing-study-suite/issues);
there are forms for a bug and for a content error (`.github/ISSUE_TEMPLATE/`), and the PR
template repeats the checklist above. For a wrong answer or a technical error in the
content, quote the file path and the exact claim, and if you can, the calculation that
contradicts it — that turns a report into a fix.
