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

`make setup` and `make launch` do the same two things, and plain `make` lists every
target (`test`, `docs`, `export`, `coverage`, `lint`, `notebooks`, `clean`). Each one
just shells out to the script it names, so nothing can drift.

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
matplotlib caches under `~/.cache/`. `QUANTUM_STUDY_DATA_DIR` redirects the history
directory for `coach.py`, `dashboard.py`, `launch.py`, `tools/concept_map.py` and all ten
apps; set it before launching, since it is read at import time.

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

- **flashcard-drill** — all 856 cards on the SM-2 scheduler, fully offline
- **exam-sim** — full timed 68-question mocks, section sprints, missed-question review,
  score-trend history; fully offline
- **qiskit-dojo** — all 72 coding katas, execution-graded locally (only the optional
  Claude style review needs a key)
- **qec-trainer** — the 170 auto-graded problems (of 178) plus the decoder game
- **vqa-trainer** — the 153 multiple-choice and 7 exact-numeric problems (of 179)
- **circuit-trainer** — every category except free-form explanations, including sprint mode
- **problem-trainer** — every problem part and derivation step has a "show model
  solution / model step" fallback, so you can work everything offline; only grading needs a key
- the **Reference** button in every app (the whole `docs/` corpus, rendered in-app)
- **docs/**, **lesson-plans/**, **notebooks/**, **labs/** (fake-backend paths),
  **projects/** — all reading and executable material
- `python coach.py` and `python dashboard.py` in full, including `--readiness`,
  `--calibrate`, `--mistakes`, `--calibration` and `--item-analysis`
- `python tools/concept_map.py` — the prerequisite graph, scored against your history
- the **phone deck** — `python tools/export_cards.py` and the published web deck below
- the **mistake journal** and **confidence rating** in every app — both are local JSON

With a key: **quantum-quiz**, **math-quiz** and **paper-drill** become live, and the
free-form / rubric grading switches on everywhere else.

---

## 3. Day 1

**First, put the deck on your phone.** The single biggest reason a study habit dies is
that studying requires sitting at the machine that has the software. It does not here —
open this on your phone and use **Add to Home Screen**:

**<https://matthewscottconroy.github.io/quantum-computing-study-suite/>**

That is all 856 cards in one self-contained page: no app, no account, no network once it
has loaded. Rate cards Again / Good / Easy and it schedules them for you (Leitner boxes,
in the phone's own storage — separate from the desktop app's SM-2 schedule, which it
never reads or writes). On your own fork, GitHub Pages has to be enabled once by hand —
repository **Settings → Pages → Build and deployment → Source: GitHub Actions** — before
the `pages.yml` deploy succeeds; `make export` builds the same page locally into
`exports/index.html`, and `exports/quantum-study.apkg` imports into Anki if you already
live there.

Then, on the desktop:

```bash
source .venv/bin/activate
python launch.py flashcard-drill
```

Do one flashcard session (no key needed) to establish the daily habit — the desktop app
keeps its own SM-2 schedule, and the setup screen will greet you with "N cards due today"
from tomorrow on. Then run `python coach.py --diagnostic` once — a 20-question placement
quiz that tells you which rung of the docs ladder to start on — and skim
[docs/README.md](docs/README.md), the ladder itself. Read the first file of Chapter 1.
That's it.

Finally, make the plan come to you:

```bash
tools/install_nudge.sh --time 08:00     # a daily desktop notification with today's plan
```

It installs a systemd `--user` timer (or a crontab line where no user systemd answers)
that runs `tools/daily_nudge.sh`, which delivers `coach.py`'s plan as a notification and
on stdout. `tools/daily_nudge.sh --dry-run` shows what you would get without notifying;
`tools/install_nudge.sh --status` reports what is scheduled and `--uninstall` removes it.

## 4. The rhythm

The workflow every resource here is designed around:

1. **Read** a docs file (or lesson-plan module) and work its exercises on paper —
   every exercise has a worked solution in a collapsible block (at the end of each docs
   file, under each exercise in the lesson plans). Every app's
   **Reference** button opens the same corpus, so you can read the chapter behind a
   problem without leaving the app.
2. **Clear the due queue** in flashcard-drill, daily (10–15 min). The setup screen opens
   on today's pull — `23 cards due today`, broken down into overdue / scheduled / new —
   and **Review Due Cards** starts exactly that queue, oldest due first, topped up with
   cards you have never seen. That is the loop: whatever SM-2 says is due, cleared every
   day. *Free drill* is still there when you want a weighted mix of a particular
   category rather than the schedule, and it updates the schedule just the same. Away
   from the desk, drill the phone deck instead; its progress is separate, so the desktop
   queue is still waiting when you get back.
3. **Quiz** yourself with the matching app to test retention:

| Reading | App |
|---|---|
| docs ch. 1 (math: linear algebra, Hilbert spaces, tensor products, plus files 04–09: groups and abstract algebra, representation theory, probability and statistics, number theory and Fourier analysis, analysis for QM, topology and geometry) | math-quiz, flashcard-drill |
| docs ch. 2 (quantum mechanics, incl. the wave-mechanics track) | math-quiz, quantum-quiz, flashcard-drill |
| docs ch. 3–4 (circuits, algorithms) | quantum-quiz, circuit-trainer |
| docs ch. 5 (QEC) | qec-trainer |
| docs ch. 6 (VQA) | vqa-trainer |
| docs ch. 7–8 (hardware, advanced) | quantum-quiz |
| docs ch. 9–11 (QML, chemistry, networking) | quantum-quiz; ch. 10 pairs with vqa-trainer |
| any paper you're reading | paper-drill |

   The Chapter 1 core track is files 01–03; the extended files 04–09 are read on demand
   when later chapters cite them (the stabilizer formalism is group theory over `GF(2)`,
   Shor's algorithm is Fourier analysis on `ℤ_N`, the threshold theorem is a
   concentration bound). Don't block on them before Chapter 2.

4. **Produce** — this is where skills actually form: write code in **qiskit-dojo**
   (execution-graded katas), work long-form problems and guided derivations in
   **problem-trainer**, run the executable **notebooks/** alongside each docs chapter,
   and take timed **exam-sim** mocks to measure readiness.
5. **Say how sure you are, before you look.** Every app shows an optional 1–4 strip —
   *guessing / unsure / fairly sure / certain* — before the answer is revealed. It costs
   one keystroke, it never affects your score, and it is the only thing in the suite that
   can tell "right" from "right and knew it". Rate honestly; a rating you inflate buys you
   nothing. Switch it off per app if you hate it — the setting sticks.
6. **When you get one wrong, spend ten seconds on why.** The result screen shows six
   cause pills — *misread / didn't know / knew but slipped / confused / out of time /
   other* — plus an optional note. One click, then move on; the mistake is already
   recorded either way, so skipping only costs you the category. Answering the same item
   correctly later resolves it on its own.

   This is the step people skip, and it is the one that pays. **One mistake is noise;
   forty mistakes with causes is a diagnosis.** "Nine little-endian misreads this month"
   tells you to slow down your reading, not to re-study endianness — and you cannot tell
   those apart from a list of flags.

   Flagging still exists and is different: **⚑ Flag for review** is a bookmark you set
   deliberately, including on questions you got *right* by luck. circuit-trainer,
   flashcard-drill, math-quiz, paper-drill, problem-trainer, qiskit-dojo and quantum-quiz
   list their flags (with Unflag) on their History screen; qec-trainer and vqa-trainer
   unflag from the result screen, or run a "flagged only" session from the setup screen
   (flashcard-drill and problem-trainer offer the same session mode). exam-sim's in-exam
   "Flag for review" is different again: it only marks a question to come back to during
   the mock; missed exam questions enter the review queue automatically.
7. **Track and steer** with the console tools:
   - `python coach.py` — the daily driver. Reads every app's history and prescribes
     today's session: weakest categories, due reviews, a kata, a sprint.
   - `python coach.py --mistakes` — **the payoff for step 6.** Your mistakes ranked by
     cause, the concepts behind each one, the last 14 days against the 14 before (so you
     can see a cause shrinking), and the unresolved list oldest first. Weekly.
   - `python coach.py --calibration` — **the payoff for step 5.** Your measured accuracy
     at each confidence level against what a calibrated learner hits (roughly
     25 / 50 / 75 / 95 % at levels 1–4), an overconfidence index, and then the list that
     matters: **confidently wrong** — the topics you rated *fairly sure* or *certain* and
     still got wrong. Treat those as unlearned, not as slips. Nothing else surfaces them.
   - `python coach.py --item-analysis` — which exam-bank questions still teach you
     something: always-missed, always-correct, mixed (the ones worth your time),
     seen-but-undecided and never-attempted. Three attempts earn a verdict; below that
     the question is listed as needing more.
   - `python coach.py --review` — the unified review queue: every flag from every app,
     plus missed exam questions, unresolved mistakes and recent low scores, oldest and
     worst first. Work through it, then unflag items as they stick (History screen;
     result screen in qec-trainer and vqa-trainer).
   - `python coach.py --badges` — the IBM Quantum Learning badge checklist.
   - `python coach.py --readiness` — once you have real exam-sim and dojo history, a
     projected C1000-179 score with a confidence band and a per-section evidence table.
     It refuses to guess: with thin data it says so and tells you what would earn a
     number (one full 68-question mock covers all eight sections at once).
   - `python coach.py --calibrate` — a different thing from `--calibration`: this one
     checks the SM-2 *intervals* against your measured recall and says whether the
     schedule is running too long or too short.
   - `python dashboard.py` — the raw mastery report, a mistakes-by-cause panel, a
     confidence panel, and a retention view (weekly review table and a fitted forgetting
     curve).

   Every one of these reports refuses to invent a number: with no data they say so, and
   a confidence level with fewer than five observations is left unjudged. If you installed
   the nudge on Day 1, the plan arrives on its own each morning; the rest are worth a look
   weekly rather than daily.

Follow the ladder order in [docs/README.md](docs/README.md) (Rung 1 → 11; rungs 9–11 —
quantum machine learning, quantum chemistry, quantum networking — are electives, not
prerequisites for anything below them). The recommended pace and per-chapter time
estimates are in that file.

### When you don't know what to read next

The ladder is one fixed order for everyone. The concept map is *your* order:

```bash
python tools/concept_map.py --next 10
```

It loads a curated prerequisite DAG over the corpus — 128 concepts, 236 edges — scores
every concept against your actual history using `dashboard.py`'s own decay, and lists the
concepts whose prerequisites you have already mastered but which you have not started.
Each row names the files that teach it and the app categories that drill it, so the answer
is a reading list and a session, not a label. `--area qec` narrows it, `--html` writes an
interactive graph to `exports/concept_map.html`, and `--check` validates the graph against
the repo. With no history it simply says everything is untouched and points at layer 0.

## 5. If your goal is the IBM certification

Follow [lesson-plans/11-certification-prep.md](lesson-plans/11-certification-prep.md):
it maps every C1000-179 exam section to specific modules here, with a 5-week
schedule and a self-assessment checklist. Support tools:

- **qiskit-dojo** — 72 write-and-run katas balanced to the exam blueprint,
  including 8 debugging and 8 API-modernization drills
- **exam-sim** — a 300-question bank in the published section proportions; timed
  68-question/90-minute mocks scored against the 47/68 pass bar with per-section
  breakdowns, 10-minute section sprints, a review mode for missed questions, and a
  History screen with your score trend against the pass mark
- `python coach.py --readiness` — the projected score and 95 % band once you have
  about 40 exam-sim/dojo observations covering 60 % of the exam weight (one full mock
  gets you most of the way); below that it lists what each section still needs
- flashcard-drill's **Qiskit API** category (45 exam-aligned cards)
- quantum-quiz's **Qiskit Certification (C1000-179)** subject (needs API key)
- Lessons 06 (Qiskit), 07 (QASM), 10 (Transpiling) — code verified on Qiskit 2.5.2
- **labs/** — the IBM hardware track, for hands-on runtime experience before the exam

Do the foundations first (docs ch. 1–4 at minimum) before starting the 5-week
cert track — the exam assumes the concepts, and tests the API.

## 6. Housekeeping

- After any content edit, run the regression gate: `make docs` (`python
  tools/verify_docs.py --all` from the venv). The full test suite is `make test`
  (`tools/run_tests.sh`) after `./setup.sh --dev`; see [CONTRIBUTING.md](CONTRIBUTING.md).
- Your history lives in `~/.local/share/quantum-study/`, including the SM-2 schedule
  (`flashcard_schedule.json`) and the two cross-app journals (`mistakes.json`,
  `confidence.json`). Back it up like any other data; nothing in the suite deletes it.
  Phone-deck and Anki progress live on those devices and are not part of it.
- The exam-sim **History** screen, `coach.py --readiness` and `dashboard.py --retention`
  are the places that show progress over time — glance at them weekly.

### Studying on more than one machine

Your history is what makes `coach.py` worth running, and it is per-machine by default —
a laptop and a desktop will each prescribe from half a picture. `tools/sync_history.sh`
turns the data directory into a git repository of its own and syncs it to a **private**
remote you control (never this public repo, and never a submodule of it — the script
refuses to run if the data directory sits inside this checkout):

```bash
tools/sync_history.sh init --remote <your private remote>   # once, on the first machine
tools/sync_history.sh push                                  # commit + push
git clone <your private remote> ~/.local/share/quantum-study   # on the second machine
tools/sync_history.sh auto                                  # pull then push; safe from cron
```

`status` reports the remote and how far ahead or behind you are, `--dry-run` shows what
any command would do and changes nothing, and nothing here ever force-pushes. A genuine
conflict — the same file edited on two machines before a sync — exits 3 and leaves the
merge to you. Sync before and after a session and the coach sees one history.

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
