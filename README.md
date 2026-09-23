# Quantum Computing Study Suite

![CI](https://github.com/matthewscottconroy/quantum-computing-study-suite/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)

A self-contained desktop learning suite for quantum computing — from mathematical
foundations through hardware-level error correction, variational algorithms, and
IBM's **C1000-179** Qiskit developer certification. Ten PyQt6 apps drill, quiz, grade
and time you; a 70-file teaching corpus, twelve lesson plans, nine executable notebooks,
five hardware labs and five capstone projects supply the material; console tools read
every app's history and tell you what to study next — and what you keep getting wrong,
and why; and the whole flashcard deck exports to a phone, so the daily drill is not tied
to this desktop.

Everything runs locally. Three apps (flashcard-drill, exam-sim, qiskit-dojo) are fully
usable offline and four more (qec-trainer, vqa-trainer, circuit-trainer, problem-trainer)
work offline for everything except free-form grading; the Claude API (`claude-sonnet-4-6`)
powers question generation and open-ended grading, and every app still launches — with
its offline features, Reference browser and history intact — when no key is configured.

---

## Study away from the desk

The PyQt6 apps need a desktop. The flashcards do not.
[`tools/export_cards.py`](tools/export_cards.py) reads the deck through flashcard-drill's
own loader — the card text is never duplicated — and re-emits all 856 cards in three
portable formats. The web deck is published from `main` on every push by
[`.github/workflows/pages.yml`](.github/workflows/pages.yml):

**<https://matthewscottconroy.github.io/quantum-computing-study-suite/>**

One self-contained HTML file: no CDN, no network requests of any kind. Open it on a
phone, **Add to Home Screen**, and it drills offline — category filters with due/new
counts, tap to reveal, Again / Good / Easy, undo, and Leitner scheduling saved in
`localStorage`. That progress is per-browser and deliberately separate from the desktop
app's SM-2 schedule, which it never reads or writes.

```bash
make export                                        # all three formats into exports/
python tools/export_cards.py --html --out _site    # just the web deck
```

| Output (in `exports/`) | What it is | Needs |
|---|---|---|
| `index.html` | the offline web deck above, built from the templates in `tools/webdeck/` | stdlib |
| `cards.json` | the deck as `{id, category, front, back}` objects, for piping anywhere | stdlib |
| `quantum-study.apkg` | an Anki package, one subdeck per category. Re-importing **updates notes in place** — GUIDs are the flashcard ids — so your Anki review history survives a re-export | `genanki` |

Outputs are byte-for-byte reproducible and the exporter refuses to ship a short deck;
[tools/README.md](tools/README.md#export_cardspy--take-the-flashcards-off-this-desktop)
has the formats, the web-deck keyboard shortcuts and the Anki re-import rules.

> **GitHub Pages must be switched on once, by hand:** repository **Settings → Pages →
> Build and deployment → Source: GitHub Actions**. A workflow cannot enable Pages for its
> own repository; until that is set, the deploy job fails with *"Get Pages site failed"*.
> The raw deck is served alongside the page at `/cards.json`.

---

## Features

### The ten apps

| App | What it trains | Offline | Needs |
|---|---|---|---|
| [flashcard-drill](flashcard-drill/) | Recall — 856 flashcards in 15 categories (Paulis, gate unitaries, theorems, QEC, Qiskit API, …): 550 hand-written plus a 306-card **Cloze** deck generated from the corpus's Key Formulas, all on a real **SM-2 scheduler**: every rating sets an ease factor, interval and due date, and the setup screen opens on "N cards due today" with a *Due today* session mode | Fully | — |
| [exam-sim](exam-sim/) | Exam conditions — 300-question C1000-179 bank with every section held to its published exam weight; 68 Q / 90 min mocks scored against the 47/68 bar, 10-minute section sprints, missed-question review, score-trend history | Fully | — |
| [qiskit-dojo](qiskit-dojo/) | Writing real Qiskit 2.x code — 72 katas in 10 sections, balanced to the exam blueprint (8 exam sections plus 8 debugging and 8 API-modernization drills), executed in a subprocess and graded by assertions | Fully (Claude style review optional) | Qiskit |
| [qec-trainer](qec-trainer/) | Error correction — 178 problems in 6 categories (170 auto-graded MC, 8 free-form) plus a syndrome-decoder game up to the distance-3 surface code | MC + decoder game | Key for 8 free-form |
| [vqa-trainer](vqa-trainer/) | Variational algorithms — 179 problems in 7 categories (153 MC, 7 exact-numeric, 19 free-form): VQE, parameter shift, QAOA, ansätze, barren plateaus, mitigation, optimal control | MC + numeric | Key for 19 free-form |
| [circuit-trainer](circuit-trainer/) | Circuit arithmetic — problems generated with Qiskit (`quantum_info` Statevector/Operator) in 12 categories (state output, measurement probabilities, identities, unitaries, entanglement, noise, …) with rendered circuits; sprint mode (10 rapid-fire questions, 60-second countdown each) | Everything except free-form explanations | Qiskit; key for explanations |
| [problem-trainer](problem-trainer/) | Long-form problem solving — 16 multi-part textbook problems graded against rubrics, plus 7 Socratic guided derivations (QPE, Grover count, CHSH, no-cloning, teleportation, parameter shift, threshold) | Model solutions and steps | Key for grading |
| [quantum-quiz](quantum-quiz/) | Open-ended QC theory — Claude-generated questions across 11 subjects / 124 topics with Qiskit-rendered context, 7 question types incl. teach-back (Feynman) and viva follow-ups | Reference + history | Key, Qiskit |
| [math-quiz](math-quiz/) | The mathematics underneath — 13 subjects / 197 topics from linear algebra to topology, generated and graded by Claude with hints | Reference + history | Key |
| [paper-drill](paper-drill/) | Active reading — paste any paper; Claude writes factual / conceptual / derivation questions and grades your answers; saved-paper library | Library + history | Key |

Every app has an in-app **Reference** button that renders the whole `docs/` corpus, and
every trainer has a **⚑ Flag for review** toggle whose flags feed the suite-wide review
queue (`python coach.py --review`). exam-sim is the exception: its in-exam "Flag for
review" button only marks a question to return to during the mock and is never persisted;
missed exam questions reach the review queue automatically via `exam_missed.json`.

All ten apps also share the same two learning mechanics, so the analysis below is drawn
from everything you do rather than from one app:

- **Mistake journal** — a wrong answer opens a row of six cause pills. One click files
  the mistake under *why* it was wrong; answering the item correctly later resolves it.
  Skipping costs nothing — the mistake is already recorded, just uncategorised.
- **Confidence calibration** — an optional 1–4 strip shown *before* the answer is
  revealed, paired with the verdict. It is what separates "right" from "right and knew
  it", and it is how the suite finds the topics you are confident about and still wrong
  about. It can be switched off per app and stays off.

### Learn from your mistakes

Flagging an item is a bookmark. A cause is analysis: nine scattered slips become
"nine little-endian misreads this month", which you can actually do something about.
Every wrong answer in any app lands in one shared journal, `mistakes.json`, under one
of six causes:

| Cause | Means | What it asks of you |
|---|---|---|
| `misread` | Misread the question | Slow the read; the knowledge was there |
| `didnt_know` | Didn't know it | Genuine gap — go back to the chapter |
| `knew_but_slipped` | Knew but slipped | Arithmetic/sign/endianness discipline, not study |
| `confused` | Confused two ideas | Drill the pair side by side until they separate |
| `out_of_time` | Ran out of time | Practise under the clock; flag rather than stall |
| `other` | Anything else | Use the free-text note |

```bash
python coach.py --mistakes       # by cause, top recurring concepts, 14-day trend, unresolved list
python coach.py --calibration    # confidence vs measured accuracy, and the confidently-wrong list
python coach.py --item-analysis  # which of the 300 exam questions still carry signal
```

`--mistakes` ranks the causes, names the concepts behind them and compares the last
14 days with the 14 before, so a shrinking cause is visible. `--calibration` scores each
confidence level against what a calibrated learner would hit (about 25 / 50 / 75 / 95 %
at levels 1–4, judged only at n ≥ 5) and prints an overconfidence index and a Brier
score — then the payoff: **confidently wrong**, the answers you rated 3 or 4 and still
got wrong, listed by topic. Those are the unknown unknowns; nothing else in the suite
flags them, because by every other measure they look like bad luck. `--item-analysis`
splits the exam bank into always-missed, always-correct, mixed (the ones worth drilling),
seen-but-undecided and never-attempted — an item needs three attempts before it gets a
verdict. `dashboard.py` shows a condensed panel for the first two.

Every one of these reports says what is missing rather than inventing a number: with an
empty journal they say so and explain what would fill it, no overall calibration verdict
is given below 20 rated answers, and a confidence level with fewer than five observations
is left unjudged.

### The content packs

| Pack | Contents |
|---|---|
| [docs/](docs/) | 70 chapter files in 11 chapters — the learning ladder from linear algebra to QSVT, then three application chapters: **09 quantum machine learning** (data encoding, quantum kernels, variational classifiers, and an honest chapter on what QML does and does not deliver), **10 quantum chemistry** (second quantization, qubit mappings, active spaces and ansätze, beyond VQE) and **11 quantum networking** (entanglement distribution, repeaters and distillation, distributed QC). Chapter 7 adds `05_modern_benchmarking.md` (layer fidelity, mirror circuits, quantum volume and CLOPS). Every file closes with the same five sections — Key Formulas, a Worked Example, a Summary, Exercises with collapsible solutions, and Further Reading. Chapter 1 also carries six extended-mathematics files (groups and abstract algebra, representation theory, probability and statistics, number theory and Fourier analysis, analysis for QM, topology and geometry). |
| [lesson-plans/](lesson-plans/) | 12 structured curricula — linear algebra through transpiling, plus the C1000-179 certification track (5-week schedule) and the paper-reading ladder. Every exercise now carries a worked solution in a collapsible block. Qiskit snippets verified on Qiskit 2.5.2. |
| [notebooks/](notebooks/) | 9 executable companions — one for each of chapters 1–8, reproducing its worked examples with assertions, plus an Aer noise-model lab (T₁, Ramsey, randomized benchmarking). Chapters 9–11 have no notebook yet. |
| [labs/](labs/) | 5-lab IBM Quantum runtime track — first job, Sessions vs Batch, reading calibration data, error suppression, a full hardware VQE workflow. |
| [projects/](projects/) | 5 capstone specs with milestones — VQE for H₂, a custom transpiler pass, a Steane-code simulator, BB84 with an eavesdropper, Grover on 3-SAT. |

### The console tools

| Tool | Purpose |
|---|---|
| `python coach.py` | Daily prescription from cross-app history: weakest categories, due reviews, a kata, a sprint. `--diagnostic` (placement quiz), `--review` (unified review queue: flags + missed exam questions + unresolved mistakes + low scores), `--badges` (IBM Quantum Learning tracker), `--readiness` (C1000-179 score projection with a confidence band, per-section evidence, and an honest "not scoreable yet" when the data is thin), `--calibrate` (measured flashcard recall vs the SM-2 intervals — says whether your schedule runs too long or too short), plus `--mistakes`, `--calibration` and `--item-analysis` (see [Learn from your mistakes](#learn-from-your-mistakes)). |
| `python dashboard.py` | Raw mastery report per app, weakest topics, recent activity, streak, a mistakes-by-cause panel and a confidence-calibration panel — plus a retention view: a weekly review table and a fitted forgetting curve (`--retention` / `--no-retention` show one half only). |
| `python tools/concept_map.py` | The corpus as a prerequisite DAG — 128 concepts, 236 edges, 16 layers — scored against your history with `dashboard.py`'s own decay. Answers "what am I ready to learn next?": `--next N` lists unlocked concepts with the files that teach them and the app categories that drill them, `--area` narrows to one area, `--html` / `--dot` export the graph, `--check` validates it against the repo. |
| `python tools/gen_cloze.py` | Regenerates the **Cloze** flashcard category from every chapter's Key Formulas section. `--dry-run` (the default) reports, `--write` writes, `--clean` removes, `--sample N` prints cards to review. Conservative by construction: an unparseable formula is dropped, never guessed. |
| `tools/sync_history.sh` | Makes `~/.local/share/quantum-study/` a git repository of its own and syncs it to a **private** remote, so your history follows you between machines. `init` / `push` / `pull` / `status` / `auto` (cron-safe), `--dry-run` throughout; it never force-pushes and refuses to run if the data dir sits inside this checkout. |
| `python tools/export_cards.py` | Exports the flashcards to `cards.json`, an Anki `.apkg` and the self-contained web deck (see [Study away from the desk](#study-away-from-the-desk)). |
| `tools/daily_nudge.sh` | Delivers today's `coach.py` plan as a desktop notification and on stdout (`--dry-run` prints only). `tools/install_nudge.sh` schedules it daily — a systemd `--user` timer when one answers, a marked crontab block otherwise (`--time HH:MM`, `--status`, `--uninstall`). |
| `python tools/verify_docs.py` | Regression gate for the corpus: structure, lint, cross-references, README file maps, lesson-plan snippet execution. |

<details>
<summary><b>Screenshots</b> — the launcher and all ten apps</summary>

| | |
|---|---|
| **Launcher** (`python launch.py`)<br>![launch.py](assets/screenshots/launch.png) | **flashcard-drill**<br>![flashcard-drill](assets/screenshots/flashcard-drill.png) |
| **exam-sim**<br>![exam-sim](assets/screenshots/exam-sim.png) | **qiskit-dojo**<br>![qiskit-dojo](assets/screenshots/qiskit-dojo.png) |
| **qec-trainer**<br>![qec-trainer](assets/screenshots/qec-trainer.png) | **vqa-trainer**<br>![vqa-trainer](assets/screenshots/vqa-trainer.png) |
| **circuit-trainer**<br>![circuit-trainer](assets/screenshots/circuit-trainer.png) | **problem-trainer**<br>![problem-trainer](assets/screenshots/problem-trainer.png) |
| **quantum-quiz**<br>![quantum-quiz](assets/screenshots/quantum-quiz.png) | **math-quiz**<br>![math-quiz](assets/screenshots/math-quiz.png) |
| **paper-drill**<br>![paper-drill](assets/screenshots/paper-drill.png) | |

</details>

---

## Quick Start

### Prerequisites

Python **3.12+** recommended — CI runs 3.12 and 3.14 (developed on 3.14) and the
current numpy/scipy wheels require 3.12. `setup.sh` accepts **3.11** as its minimum, but
3.11 is untested and depends on pip resolving older numpy/scipy. A desktop session for
the PyQt6 windows. On a minimal Linux install PyQt6 also needs the Qt runtime
libraries (Debian/Ubuntu: `libxcb-cursor0 libegl1 libgl1 libxkbcommon0`; Fedora:
`xcb-util-cursor mesa-libEGL mesa-libGL libxkbcommon`) — `setup.sh` prints that line if
they are missing. Everything else is a Python package that the setup script installs.

### 1. Set up

```bash
git clone https://github.com/matthewscottconroy/quantum-computing-study-suite.git
cd quantum-computing-study-suite
./setup.sh            # creates .venv, installs requirements.txt, checks core imports, imports every app headless
```

`./setup.sh --dev` additionally installs `requirements-dev.txt` (pytest, Jupyter kernel
and notebook execution deps, and `genanki` for the Anki export) for contributors.

A [`Makefile`](Makefile) wraps the same scripts, so the two can never drift — `make` on
its own lists the targets:

| Target | Runs |
|---|---|
| `make setup` / `make dev` | `setup.sh` / `setup.sh --dev` |
| `make test` | `tools/run_tests.sh` — every suite, one process per app |
| `make docs` | `tools/verify_docs.py --all` |
| `make export` | `tools/export_cards.py --all` → `exports/` |
| `make launch` | `launch.py` (`make launch ARGS=--list` for the CLI) |
| `make lint` / `make coverage` | mypy / the root suite under coverage, both configured in `pyproject.toml` |
| `make notebooks` | executes every notebook with nbclient, outputs not written back |
| `make clean` | deletes caches, `exports/` and build artefacts — nothing tracked |

Every target takes `ARGS="…"` (`make test ARGS="-x -vv"`, `make docs ARGS=--no-snippets`)
and `PYTHON=…` to pick an interpreter; the default is the repo `.venv`.

### 2. Launch

```bash
source .venv/bin/activate
python launch.py                  # graphical launcher — pick an app
python launch.py flashcard-drill  # or start one app directly by directory name ...
python launch.py dojo             # ... or by alias / unique prefix
python launch.py --list           # the app table: names, aliases, which apps use a key for their full feature set
```

`flashcard-drill`, `exam-sim` and `qiskit-dojo` work immediately with no key.

### 3. (Optional) API key for the Claude-powered features

API apps look for the key in two places, in order:

1. Environment variable: `export ANTHROPIC_API_KEY=sk-ant-...`
2. File: `~/.config/quantum-study/api_key.txt`

The file approach persists across terminal sessions without modifying shell config:
```bash
mkdir -p ~/.config/quantum-study
echo "sk-ant-..." > ~/.config/quantum-study/api_key.txt
```

Every app launches without a key; only generation, grading and review buttons need it,
and they report a clear error rather than crashing.

### 4. (Optional) Have the daily plan delivered

```bash
tools/daily_nudge.sh --dry-run        # print today's coach.py plan, no notification
tools/install_nudge.sh --time 08:00   # notify every morning; --status to inspect, --uninstall to remove
```

### Manual per-app fallback

Each app is a standalone Python package and can be run on its own. From the repo root:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # or one app's: pip install -r quantum-quiz/requirements.txt
cd quantum-quiz && python main.py
```

Minimum dependency tiers if you install by hand: `PyQt6` for every app (plus `matplotlib`
for all but problem-trainer); `anthropic` for the Claude features; `qiskit` + `pylatexenc`
for quantum-quiz, circuit-trainer and the qiskit-dojo execution harness (plus
`qiskit-qasm3-import` for the dojo's OpenQASM kata, which calls `qiskit.qasm3.loads`);
`qiskit-aer` for the Aer katas in qiskit-dojo, the notebooks and the labs;
`qiskit-ibm-runtime` only for the hardware labs — the lesson-plan snippets that import it
are skipped automatically by `verify_docs.py`, so the docs gate does not need it.
`qiskit-dojo` finds the interpreter for its sandbox automatically (the active venv →
`../.venv/bin/python` → `qiskit-dojo/.venv/bin/python` → `sys.executable`), so keep the
shared `.venv` if you use it.

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
         ├──► circuit-trainer   Hands-on circuit arithmetic (Qiskit; API for explanations)
         │
         ├──► qec-trainer       Error correction focus (API for free-form only)
         │
         ├──► vqa-trainer       Variational algorithms focus (API for free-form only)
         │
         └──► paper-drill       Test understanding of a specific paper (API)

Production-skill track (alongside the above):
   qiskit-dojo      Write real Qiskit code, graded by execution
   problem-trainer  Long-form problems and guided derivations (API for grading)
   exam-sim         Timed mock exams for C1000-179 (offline)
   notebooks/ labs/ projects/   Executable examples, hardware labs, capstones

Daily driver:  python coach.py   — prescribes today's session from your history
               (tools/install_nudge.sh delivers it as a morning notification)
What next:     python tools/concept_map.py --next   — the prerequisite graph, scored
               against your history: concepts you are now ready to learn
Why you miss:  python coach.py --mistakes / --calibration
Away from the desk:  the web deck on GitHub Pages, or the Anki export
                     (tools/sync_history.sh keeps your history in step across machines)
```

The docs ladder in [docs/README.md](docs/README.md) (Rung 1 → 11) gives the reading order
and per-chapter time estimates; `python tools/concept_map.py --next` answers the same
question from your own history instead of from the ladder; and
[GETTING_STARTED.md](GETTING_STARTED.md) turns the whole thing into a day-1 routine and a
certification track.

---

## Running the tests

```bash
source .venv/bin/activate          # after ./setup.sh --dev
make test                          # == bash tools/run_tests.sh: every suite, one pytest process per app
make docs                          # == python tools/verify_docs.py --all
```

Individually:

```bash
pytest                                   # root suite: coach.py, dashboard.py, launch.py, tools/verify_docs.py
(cd qec-trainer && python -m pytest)     # one app; each app has tests/ and its own pytest.ini
(cd qiskit-dojo && python -m pytest -m slow tests/test_sweep.py)  # opt-in: run all 72 kata solutions
python tools/verify_docs.py --all        # docs/lesson-plan regression gate (--no-snippets without the venv)
for nb in notebooks/*.ipynb; do MPLBACKEND=Agg jupyter execute "$nb"; done   # notebooks, executed in memory as CI does (--inplace would rewrite them with outputs)
make lint                                # mypy over coach.py, dashboard.py, launch.py, tools/ — advisory, baseline not yet clean
make coverage                            # root suite under coverage.py; both configured in pyproject.toml
```

Apps must run in separate pytest processes because several share top-level package names
(`core/`, `problems/`, `ui/`); `tools/run_tests.sh` handles that. Tests marked `slow` (more
than ~30 s) are deselected by default. Headless runs set `QT_QPA_PLATFORM=offscreen`, and
every test suite points `QUANTUM_STUDY_DATA_DIR` at a temporary directory *and*
monkeypatches the modules' path constants — the variable is read at import time, so a test
that has already imported `config` needs both — so nothing touches your real study history.

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs the same sequence on
Python 3.12 and 3.14 — byte-compile, an import smoke test of every app with no API key,
`python tools/verify_docs.py --all`, then `bash tools/run_tests.sh`. The 3.14 leg adds two
steps the 3.12 leg skips: coverage of the root suite (uploaded as `coverage.xml`; no
`--fail-under` yet) and mypy, which is advisory — it annotates the job but cannot fail it
until its baseline is clean. Three more workflows round it out:
[`notebooks.yml`](.github/workflows/notebooks.yml) executes every notebook on every push
and pull request to `main`, weekly, and on manual dispatch — a regression check on the
numbers printed in `docs/`; [`pages.yml`](.github/workflows/pages.yml) rebuilds and
deploys the web deck; and [`release.yml`](.github/workflows/release.yml) re-runs the whole
gate on a version tag, checking the tag against `[project].version`, before it builds and
publishes. Dependabot keeps the Actions and pip pins current, and the repository carries
issue forms for bugs and content errors plus a PR template.

---

## Shared Data Directory

All apps that record history write to `~/.local/share/quantum-study/`. Files are plain JSON
and are never deleted automatically. The `QUANTUM_STUDY_DATA_DIR` environment variable
redirects that directory for `coach.py`, `dashboard.py`, `launch.py`, `tools/concept_map.py`
and **all ten apps** — it is read when the app's `config.py` (or `persistence.py`) is
imported, so set it before launching.

| File | Written by |
|---|---|
| `flashcard_history.json`, `flagged_cards.json`, `flashcard_schedule.json` | flashcard-drill |
| `qec_history.json`, `qec_flagged.json` | qec-trainer |
| `vqa_history.json`, `vqa_flagged.json` | vqa-trainer |
| `paper_history.json`, `paper_library.json`, `paper_flagged.json` | paper-drill |
| `quiz_history.json`, `quiz_draft.json`, `quiz_flagged.json` | quantum-quiz |
| `math_history.json`, `math_draft.json`, `math_flagged.json` | math-quiz |
| `trainer_history.json`, `trainer_flagged.json` | circuit-trainer |
| `dojo_history.json`, `dojo_flagged.json` | qiskit-dojo |
| `exam_history.json`, `exam_missed.json` | exam-sim |
| `problems_history.json`, `problems_flagged.json` | problem-trainer |
| `mistakes.json`, `confidence.json` | **all ten apps** (read by coach.py and dashboard.py) |
| `mistakes.json.lock`, `confidence.json.lock` | **all ten apps** — empty lock sidecars, see below |
| `coach_state.json` | coach.py |

`flashcard_schedule.json` is the SM-2 scheduler's own state — `{card_id: {n, ef,
interval_days, due_iso, last_seen_iso, lapses}}` — written only by flashcard-drill and
read by `coach.py --calibrate`, which works fine when it is absent. It is a new file
rather than a change to `flashcard_history.json`, whose schema `coach.py` and
`dashboard.py` both parse.

`mistakes.json` and `confidence.json` are the two cross-app learning journals. Each is a
flat JSON list that every app appends to and only `coach.py` and `dashboard.py` read; each
record carries an `app` field, so one file serves the whole suite:

| File | Record |
|---|---|
| `mistakes.json` | `{"id", "app", "category", "question", "your_answer", "correct_answer", "cause", "note", "timestamp", "resolved"}` — `cause` is one of `misread` / `didnt_know` / `knew_but_slipped` / `confused` / `out_of_time` / `other`, or `null` for "logged but not categorised yet" |
| `confidence.json` | `{"id", "app", "category", "confidence", "correct", "timestamp"}` — `confidence` is 1 (guessing) to 4 (certain), captured *before* the reveal |

Both are append-only logs, trimmed to the newest N records so years of study cannot grow
them without bound, and both are new files rather than changes to any `*_history.json` —
whose schemas `coach.py` and `dashboard.py` parse and which are therefore frozen. Every
reader tolerates a missing, empty or corrupt journal by reporting "no data".

Because all ten apps append to the same two files and several apps can be open at once,
each journal is guarded by an empty sidecar — `mistakes.json.lock` and
`confidence.json.lock`. An app takes an exclusive `fcntl.flock` on the sidecar for the
whole read-modify-write (identical `journal_sync.py` in every app tree), so the list it
rewrites can never be a stale copy that silently drops rows another app just appended;
a rewrite also puts rows belonging to other apps back exactly as it read them. The
sidecars hold no data, are safe to delete when nothing is running, and readers
(`coach.py`, `dashboard.py`) ignore them: writes are still single atomic replaces, so
reading stays lock-free.

The `*_flagged.json` files share one contract — a JSON list of
`{"id", "label", "category", "app", "timestamp"}` entries (only `id` required). Three
legacy files — `flagged_cards.json`, `qec_flagged.json` and `vqa_flagged.json` — still hold
a bare list of id strings instead, so anything that reads these files must accept both
shapes, as `coach.py` does. `coach.py --review` discovers every such file by name, so a new
app joins the review queue just by writing `<prefix>_flagged.json`.

---

## Architecture Notes

All apps follow the same structural pattern (typical layout — the two API-free apps,
flashcard-drill and exam-sim, have no `workers/`; exam-sim has no `ui/widgets/`; and
flashcard-drill keeps persistence in a `persistence/storage.py` package):

```
<app>/
├── main.py               Entry point — creates QApplication and MainWindow
├── config.py             App-wide constants (model, paths, thresholds)
├── core/
│   └── models.py         Dataclasses shared across all modules
├── ui/
│   ├── main_window.py    QMainWindow + QStackedWidget screen controller
│   ├── screens/          One file per screen (setup, problem, feedback, summary, history, reference)
│   ├── widgets/          Reusable widgets (LoadingOverlay, CollapsiblePanel, ScoreBar, etc.)
│   └── theme.py          Colour palette and style constants
├── workers/              QThread subclasses for non-blocking API calls
├── persistence.py        JSON read/write for session history and review flags
├── tests/                pytest suite (+ pytest.ini)
└── requirements.txt
```

Apps with static banks add a one-file-per-item directory that is auto-discovered at start-up:
`flashcard-drill/cards/` (whose `cloze/` subdirectory is generated by
`tools/gen_cloze.py`, not hand-written), `qec-trainer/problems/`, `vqa-trainer/problems/`,
`qiskit-dojo/katas/`, `exam-sim/bank/`, `problem-trainer/problems/` and `derivations/`.
Where the Claude code lives differs by app family: qec-trainer, vqa-trainer and
circuit-trainer keep `auto_grader.py` beside `claude_grader.py` in `grading/`, and
qiskit-dojo keeps `claude_review.py` there; paper-drill and problem-trainer keep everything
Claude-facing in `ai/` (`client.py`, `grader.py`, and `generator.py` or `prompts.py` +
`response_parser.py`); quantum-quiz and math-quiz keep `prompt_builder.py` and
`response_parser.py` in `ai/` with the client in `core/claude_client.py`. circuit-trainer is the only app
that uses Qiskit to *generate* problems (`problems/<category>.py` generators compute the
answers with `qiskit.quantum_info` — `Statevector` / `Operator` — not Aer).
See [CONTRIBUTING.md](CONTRIBUTING.md) for the object shape of each bank item.

---

## Claude Model

All API apps use `claude-sonnet-4-6`. The model ID is set in each app's `config.py`
and can be changed there without touching any other code.

---

## Contributing

Bug reports, corrections to the content banks and new problems are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md) for the dev setup, the shape of each bank item, the
docs style rules and the PR checklist, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
Released under the [MIT License](LICENSE).

> The exam logistics quoted for C1000-179 (68 questions, 90 minutes, 47 to pass, section
> weights) are third-party-sourced; confirm them on IBM's official exam page. All exam-sim
> questions are original study material — not real exam content — and this project is not
> affiliated with or endorsed by IBM.
