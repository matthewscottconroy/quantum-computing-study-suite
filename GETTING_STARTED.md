# Getting Started

This is the day-1 guide. [README.md](README.md) explains *what* is in the suite;
this file tells you what to do first, what to do every day, and how to make the
apps steer you. It assumes a fresh clone.

---

## 1. Ten minutes of setup

```bash
git clone https://github.com/matthewscottconroy/quantum-computing-study-suite.git
cd quantum-computing-study-suite
./setup.sh                    # creates .venv, installs everything, smoke-checks the apps
source .venv/bin/activate
python launch.py              # the launcher — every app one click away
```

`python launch.py flashcard-drill` (or an alias such as `python launch.py dojo`) starts
one app directly; `python launch.py --list` prints the names, aliases and which apps
use an API key for their full feature set (section 2 lists what each does without one). If you would rather not use the launcher, every app also runs as
`cd <app> && python main.py` from the activated venv.

Python 3.12+ is recommended (developed on 3.14; CI runs 3.12 and 3.14); `setup.sh` accepts
3.11 as its minimum, but that path is untested. On a
minimal Linux install PyQt6 also needs the Qt runtime libraries; `setup.sh` prints the
`apt`/`dnf` line if they are missing. Nothing is written outside the repo except your
study history in `~/.local/share/quantum-study/` (a few JSON files per app — see the
table in [README.md](README.md#shared-data-directory)), the API-key file described next
if you create it, a Jupyter kernelspec named `quantum-study` under
`~/.local/share/jupyter/kernels/` (only with `./setup.sh --dev`), and the usual pip and
matplotlib caches under `~/.cache/`. `QUANTUM_STUDY_DATA_DIR`
redirects the history directory for `coach.py`, `launch.py`, flashcard-drill,
qiskit-dojo, math-quiz and quantum-quiz only; the other six apps and `dashboard.py`
always use the default path.

## 2. The one optional piece: an API key

Seven of the ten apps use the Claude API for question generation or open-ended grading
(and qiskit-dojo can optionally ask Claude for a style review of a passing kata).
Every app **launches and is useful without a key**; add one whenever you want the
generated / graded features. Do either of these once:

```bash
export ANTHROPIC_API_KEY=sk-ant-...        # add to ~/.bashrc to persist
```
or
```bash
mkdir -p ~/.config/quantum-study
echo "sk-ant-..." > ~/.config/quantum-study/api_key.txt
```

What works today with **no key at all**:

- **flashcard-drill** — all 550 cards, fully offline
- **exam-sim** — full timed 68-question mocks, section sprints, missed-question review,
  score-trend history; fully offline
- **qiskit-dojo** — all 36 coding katas, execution-graded locally (only the optional
  Claude style review needs a key)
- **qec-trainer** — the 170 auto-graded problems (of 178) plus the decoder game
- **vqa-trainer** — the 153 multiple-choice and 7 exact-numeric problems (of 179)
- **circuit-trainer** — every category except free-form explanations, including sprint mode
- **problem-trainer** — every problem part and derivation step has a "show model
  solution / model step" fallback, so you can work everything offline; only grading needs a key
- the **Reference** button in every app (the whole `docs/` corpus, rendered in-app)
- **docs/**, **lesson-plans/**, **notebooks/**, **labs/** (fake-backend paths),
  **projects/** — all reading and executable material
- `python coach.py` and `python dashboard.py`

With a key: **quantum-quiz**, **math-quiz** and **paper-drill** become live, and the
free-form / rubric grading switches on everywhere else.

---

## 3. Day 1

```bash
source .venv/bin/activate
python launch.py flashcard-drill
```

Do one flashcard session (no key needed) to establish the daily habit. Then run
`python coach.py --diagnostic` once — a 20-question placement quiz that tells you which
rung of the docs ladder to start on — and skim [docs/README.md](docs/README.md), the
ladder itself. Read the first file of Chapter 1. That's it.

## 4. The rhythm

The workflow every resource here is designed around:

1. **Read** a docs file (or lesson-plan module) and work its exercises on paper —
   solutions are in the collapsible blocks at the end of every file. Every app's
   **Reference** button opens the same corpus, so you can read the chapter behind a
   problem without leaving the app.
2. **Drill** the matching flashcard categories daily (10–15 min; the SRS weights
   what you miss).
3. **Quiz** yourself with the matching app to test retention:

| Reading | App |
|---|---|
| docs ch. 1 (math: linear algebra, Hilbert spaces, tensor products, plus files 04–09: groups and abstract algebra, representation theory, probability and statistics, number theory and Fourier analysis, analysis for QM, topology and geometry) | math-quiz, flashcard-drill |
| docs ch. 2 (quantum mechanics, incl. the wave-mechanics track) | math-quiz, quantum-quiz, flashcard-drill |
| docs ch. 3–4 (circuits, algorithms) | quantum-quiz, circuit-trainer |
| docs ch. 5 (QEC) | qec-trainer |
| docs ch. 6 (VQA) | vqa-trainer |
| docs ch. 7–8 (hardware, advanced) | quantum-quiz |
| any paper you're reading | paper-drill |

   The Chapter 1 core track is files 01–03; the extended files 04–09 are read on demand
   when later chapters cite them (the stabilizer formalism is group theory over `GF(2)`,
   Shor's algorithm is Fourier analysis on `ℤ_N`, the threshold theorem is a
   concentration bound). Don't block on them before Chapter 2.

4. **Produce** — this is where skills actually form: write code in **qiskit-dojo**
   (execution-graded katas), work long-form problems and guided derivations in
   **problem-trainer**, run the executable **notebooks/** alongside each docs chapter,
   and take timed **exam-sim** mocks to measure readiness.
5. **Flag what stumped you.** Every trainer has a **⚑ Flag for review** toggle on the
   screen where you answer or see the verdict — the problem, card, kata, result or
   feedback screen, depending on the app. Flag anything you got wrong for a reason
   you can name, or got right by luck. circuit-trainer, flashcard-drill, math-quiz,
   paper-drill, problem-trainer, qiskit-dojo and quantum-quiz list their flags (with
   Unflag) on their History screen; qec-trainer and vqa-trainer have no flag list there —
   unflag from the result screen, or run a "flagged only" session from the setup screen
   (flashcard-drill and problem-trainer offer the same session mode). exam-sim's in-exam
   "Flag for review" is different: it only marks a question to come back to during the
   mock; missed exam questions enter the review queue automatically.
6. **Track and steer** with the console tools:
   - `python coach.py` — the daily driver. Reads every app's history and prescribes
     today's session: weakest categories, due reviews, a kata, a sprint.
   - `python coach.py --review` — the unified review queue: every flag from every app,
     plus missed exam questions and recent low scores, oldest and worst first. Work
     through it, then unflag items as they stick (History screen; result screen in
     qec-trainer and vqa-trainer).
   - `python coach.py --badges` — the IBM Quantum Learning badge checklist.
   - `python dashboard.py` — the raw mastery report.

Follow the ladder order in [docs/README.md](docs/README.md) (Rung 1 → 8). The
recommended pace and per-chapter time estimates are in that file.

## 5. If your goal is the IBM certification

Follow [lesson-plans/11-certification-prep.md](lesson-plans/11-certification-prep.md):
it maps every C1000-179 exam section to specific modules here, with a 5-week
schedule and a self-assessment checklist. Support tools:

- **qiskit-dojo** — 36 write-and-run katas weighted to the exam sections,
  including debugging and API-modernization drills
- **exam-sim** — timed 68-question/90-minute mocks scored against the 47/68 pass
  bar with per-section breakdowns, 10-minute section sprints, a review mode for
  missed questions, and a History screen with your score trend against the pass mark
- flashcard-drill's **Qiskit API** category (45 exam-aligned cards)
- quantum-quiz's **Qiskit Certification (C1000-179)** subject (needs API key)
- Lessons 06 (Qiskit), 07 (QASM), 10 (Transpiling) — code verified on Qiskit 2.5.2
- **labs/** — the IBM hardware track, for hands-on runtime experience before the exam

Do the foundations first (docs ch. 1–4 at minimum) before starting the 5-week
cert track — the exam assumes the concepts, and tests the API.

## 6. Housekeeping

- After any content edit, run the regression gate: `python tools/verify_docs.py --all`
  (from the venv). The full test suite is `tools/run_tests.sh` after `./setup.sh --dev`;
  see [CONTRIBUTING.md](CONTRIBUTING.md).
- Your history lives in `~/.local/share/quantum-study/`. Back it up like any other
  data; nothing in the suite deletes it.
- The exam-sim **History** screen and `coach.py` are the two places that show progress
  over time — glance at them weekly.

## 7. Known limitations (documented, not blockers)

- Lesson snippets that need `qiskit-ibm-runtime` or IBM hardware access are
  syntax-checked, not executed, by the verifier. To run circuits on real IBM
  hardware you need an IBM Quantum Platform account; `qiskit-ibm-runtime` is in
  `requirements.txt`, and [labs/](labs/) walks through the first job.
- Exam logistics cited in lesson 11 and exam-sim (weights, passing score, price) are
  third-party-sourced — confirm on IBM's official C1000-179 page when you register.
  All exam-sim questions are original study material, not real exam content.
- The docs are a self-contained companion, not a replacement for a textbook:
  the Further Reading sections point at Nielsen & Chuang / Griffiths / Preskill
  chapters where you'll want the deeper treatment.
