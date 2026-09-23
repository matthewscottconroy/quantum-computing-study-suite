# Training Roadmap — Skills-Gap Analysis and Proposed Features

> **Status (2026-09-23): round 3 — error analysis, corpus breadth and navigation.**
> Round 2 made the habit stick and made progress measurable; round 3 asks *why* the
> wrong answers are wrong, widens the corpus past the core ladder, and stops the
> ladder being the only way to navigate it.
>
> **Learning from mistakes.** All ten apps now write two cross-app journals under the
> shared data directory. `mistakes.json` files every wrong answer under one of six
> causes — `misread`, `didnt_know`, `knew_but_slipped`, `confused`, `out_of_time`,
> `other` — chosen from a row of pills on the result screen (one click, skippable; the
> mistake is journalled either way, and re-answering the item correctly resolves it).
> `confidence.json` pairs a 1–4 rating taken *before* the reveal with the verdict.
> Reading them: `coach.py --mistakes` (causes ranked, recurring concepts, a 14-day
> trend against the 14 days before, the unresolved list), `coach.py --calibration`
> (measured accuracy per confidence level against the calibrated 25/50/75/95 % targets,
> an overconfidence index, a Brier score, and the **confidently wrong** list — the
> topics rated *fairly sure* or *certain* and still missed, which nothing else in the
> suite surfaces), and `coach.py --item-analysis` (the 300-question exam bank split
> into always-missed / always-correct / mixed / never-attempted). `dashboard.py` gained
> a condensed panel for each journal. Both files are new — neither touches a
> `*_history.json` schema — and every report degrades to "no data" rather than a
> number when the evidence is thin.
>
> **Corpus breadth.** Three application chapters — `docs/09_quantum_machine_learning/`
> (4 files), `docs/10_quantum_chemistry/` (4) and `docs/11_quantum_networking/` (3) —
> plus `docs/07_quantum_hardware/05_modern_benchmarking.md`. The corpus is 70 chapter
> files in 11 chapters (was 58 in 8); the ladder in `docs/README.md` runs Rung 1 → 11,
> with 9–11 as electives rather than prerequisites.
>
> **Navigation and reach.** `tools/concept_map.py` is a curated prerequisite DAG over
> the corpus — 128 concepts, 236 edges, 16 layers — scored with `dashboard.py`'s own
> decay, answering "what am I ready to learn next?" (`--next`, `--area`, `--html`,
> `--dot`, `--check`). `tools/gen_cloze.py` generates a **Cloze** flashcard category
> from every chapter's Key Formulas section, conservative by construction (an
> unparseable formula is dropped, never guessed): 306 generated cards on top of the 550
> hand-written ones, so the deck is 856 in 15 categories. `tools/sync_history.sh` makes
> the study-history directory a git repository of its own, synced to a private remote,
> so a second machine is not a second history. And `QUANTUM_STUDY_DATA_DIR` finally
> reaches qec-trainer and vqa-trainer — all ten apps honour it, and the caveat that
> used to appear in the README and GETTING_STARTED is gone.
>
> No round-3 analysis section was written before the work; this block is the record.
> The round-1 and round-2 analyses below are preserved unchanged.

> **Status (2026-09-16): round 2 — all four tiers implemented.** Tier 1 (friction) →
> `tools/export_cards.py` + `.github/workflows/pages.yml` (Anki `.apkg`, `cards.json`
> and the self-contained web deck published to
> <https://matthewscottconroy.github.io/quantum-computing-study-suite/>), a real SM-2
> scheduler in flashcard-drill (`core/scheduler.py`, `flashcard_schedule.json`, "N due
> today" sessions), and `tools/daily_nudge.sh` + `tools/install_nudge.sh` (desktop
> notification on a systemd `--user` timer or cron). Tier 2 (content depth) → a worked
> solution for every exercise in all 12 lesson plans, the exam-sim bank 110 → 300
> questions held to the published section weights, the dojo 36 → 72 katas rebalanced to
> the exam blueprint. Tier 3 (project hygiene) → `pyproject.toml` + `Makefile`
> (`setup/dev/test/docs/lint/coverage/notebooks/export/launch/clean`), CI coverage and
> advisory mypy steps, `release.yml`, Dependabot, issue forms and a PR template. Tier 4
> (analytics) → `coach.py --readiness` (exam projection with a confidence band),
> `coach.py --calibrate` (SM-2 intervals vs measured recall) and the `dashboard.py`
> retention view (weekly accuracy, fitted forgetting curve). The tier analysis is
> recorded at the end of this file.

> **Status (2026-08-27): all ten gaps implemented.** Gap 1 → `qiskit-dojo/` (36 katas
> incl. debugging + modernization) and `notebooks/` (9 executable notebooks). Gap 2 →
> `exam-sim/` (110-question bank, full + sprint modes). Gap 3 → `problem-trainer/`
> (16 rubric-graded problems + 7 guided derivations). Gap 4 → circuit-trainer sprint
> mode. Gap 5 → `labs/` (5-lab runtime track) + `notebooks/noise_labs.ipynb`. Gap 6 →
> qec-trainer decoder game. Gap 7 → quantum-quiz teach-back + viva modes. Gap 8 →
> `coach.py` (plan/diagnostic/badges/unified review). Gap 9 → `projects/` (5 capstone
> specs). Gap 10 → `lesson-plans/12-reading-ladder.md`. Details below preserved as the
> design record.

*Drafted 2026-08-27. Premise: the suite currently trains recall and recognition well
(flashcards, Q&A, multiple choice, reading with exercises) but under-trains
**production skills** — writing code, long-form problem solving, timed performance,
and hands-on hardware. Each gap below maps to proposed features/programs.*

---

## Gap 1 — Writing real Qiskit code *(highest priority)*

Nothing in the suite has the user type code that executes. The C1000-179 exam and all
practical work demand it.

| Feature | Description |
|---|---|
| **qiskit-dojo** (new app) | Task specs ("prepare GHZ; assert `⟨ZZZ⟩ = 1`", "build a SamplerV2 PUB with a parameter sweep") + editor pane + sandboxed execution in `.venv` + assertion-based auto-grading + Claude style review. Katas laddered to the 8 exam sections. |
| Debug drills | Broken snippets (bit-ordering, measured circuit → Estimator, non-ISA submission) to fix and prove fixed by execution. |
| Modernization drills | Qiskit 0.x/1.x code (`execute()`, V1 primitives) to rewrite for 2.x — trains the exam's current-API discrimination. |
| Companion notebooks | One Jupyter notebook per docs chapter reproducing every worked example in runnable code. |

## Gap 2 — Exam conditions

| Feature | Description |
|---|---|
| **Mock-exam mode** (new app or quantum-quiz mode) | 68 questions / 90 minutes, MC with code snippets, scored vs the 47/68 bar, per-section breakdown against official weights. Missed questions feed the flashcard SRS. Curated fixed bank + Claude-generated variants for retakes. |
| Sprint drills | 10 questions / 10 minutes on a single weak section. |

## Gap 3 — Long-form problem solving and proofs (the textbook gap)

| Feature | Description |
|---|---|
| **Problem-set trainer** | Multi-part N&C-style problems; rubric-based Claude grading of free-form written math with partial credit per part; revision loop until rubric satisfied. |
| **Guided-derivation mode** | Socratic reconstruction of the canon (QPE, Grover's optimal count, CHSH bound, threshold-theorem sketch, no-cloning) — each step checked before the next hint unlocks. |

## Gap 4 — Mental circuit-simulation fluency

- Timed trace drills in circuit-trainer: predict counts/statevector before Aer reveals
  the answer; bit-ordering traps; deterministic-basis puzzles; "sprint mode" scoring.

## Gap 5 — Hardware practice

- **Runtime lab track**: `pip install qiskit-ibm-runtime`, free IBM account, graded lab
  sequence — submit a job, Session vs Batch, read calibration data, pick the best qubit
  chain from `backend.target`, measure the effect of dynamical decoupling.
- **Noise labs**: simulate T1/T2/RB experiments with Aer noise models and fit the decay
  curves (docs ch. 7 → practice).

## Gap 6 — QEC hands-on

- **Decoder game** in qec-trainer: syndrome patterns on repetition/surface codes →
  choose the correction; scored rounds building MWPM intuition. Stim-backed for larger
  codes if desired.
- Stabilizer-tableau lab: verify stabilizer claims computationally.

## Gap 7 — Explanation as a skill

- **Teach-back (Feynman) mode** in quantum-quiz: write an explanation for a novice;
  Claude grades accuracy, completeness, leaky analogies.
- **Viva mode**: chained probing follow-ups on each answer, oral-exam style.

## Gap 8 — Study orchestration

- **Coach**: evolve `dashboard.py` into a prescription engine — diagnostic placement
  exam on first run, then a daily plan (due reviews, weakest-topic targeting, one dojo
  kata) from cross-app history; streaks; IBM Quantum Learning badge tracker.
- **Unified SRS**: one review queue across flashcards, missed quiz topics, and missed
  mock-exam questions.

## Gap 9 — Capstone projects (integration skills)

Guided specs with milestones + Claude code review:
1. VQE for H₂ end-to-end (Hamiltonian → ansatz → optimizer → dissociation curve)
2. Write and test a custom transpiler pass
3. Steane-code simulator with syndrome extraction and logical-error benchmarking
4. BB84 simulation with an intercept-resend eavesdropper and QBER measurement
5. Grover applied to a real SAT instance, with resource counting

## Gap 10 — Structured reading program

Curated paper ladder per docs chapter (EPR → Bell → Shor → Preskill NISQ → Google 2019
→ IBM gross code 2024), each entry feeding paper-drill; classic-papers list with
difficulty ratings and reading order.

---

## Suggested build order

1. **qiskit-dojo** — attacks the largest gap; directly serves the certification.
2. **Mock-exam mode** — cheap once a bank exists; makes readiness measurable.
3. **Problem-set trainer + guided derivations** — closes the textbook gap.
4. **Coach / unified SRS** — multiplies the value of everything else.
5. **Runtime + noise labs** — schedule just before certification registration.
6. Decoder game, teach-back, capstones, reading ladder — ongoing enrichment.

---

# Round 2 — Retention, Friction and Measurability

*Drafted 2026-09-16, after two weeks of using the round-1 suite. Premise: the suite now
covers every skill it was built to train, so the remaining risk is not a missing feature
but the habit failing — studying only happens at the one desktop that has the software,
the flashcard "SRS" only re-weights a session rather than scheduling anything, the daily
plan exists but nothing surfaces it, and nothing yet says whether the studying is
working. Four tiers, in the order they pay back.*

## Tier 1 — Friction *(highest priority)*

Every day the deck is not opened is a day the schedule slips. Remove the reasons.

| Feature | Description |
|---|---|
| **Phone deck** | Export the 550 flashcards through flashcard-drill's own loader (never a copy of the card text) as a single self-contained HTML file — no CDN, no network — with reveal / Again–Good–Easy / Leitner boxes in `localStorage`; publish it from `main` to GitHub Pages so "Add to Home Screen" is the whole install. Also an Anki `.apkg` (one subdeck per category, stable GUIDs so a re-import updates in place) and a plain `cards.json`. |
| **Real SM-2 in flashcard-drill** | Per-card ease factor, interval and due date in a new `flashcard_schedule.json` (never a change to `flashcard_history.json`, which `coach.py` and `dashboard.py` parse); a *Due today* session that draws exactly the due queue, oldest first, topped up with new cards; the setup screen opens on "N cards due today"; the schedule is reconstructed from existing history on first run. |
| **Daily nudge** | `coach.py`'s plan delivered as a desktop notification each morning — a systemd `--user` timer with a cron fallback, idempotent install / status / uninstall, degrading to stdout when there is no session bus. |

## Tier 2 — Content depth

| Feature | Description |
|---|---|
| **Lesson-plan solutions** | Every exercise in all 12 lesson plans gets a fully worked solution in the same collapsible `<details><summary>Solution</summary>` block the docs use (every printed number checked by a script, as the docs rules require). |
| **Exam bank 110 → 300** | Enough that a 68-question mock never repeats a question and every section can fill a 10-question sprint several times over; each section's share of the bank held within 1.5 pp of its published exam weight; every code snippet executed on Qiskit 2.x. |
| **Katas 36 → 72** | Rebalance the dojo to the exam blueprint (per-section floors: 10/9/8/7/7/6/6/3 across the eight exam sections, plus 8 debugging and 8 modernization drills); every solution must pass and no starter may. |

## Tier 3 — Project hygiene

- `pyproject.toml` (PEP 621 metadata, console-script entry points for the three root
  tools, mypy and coverage configuration) and a `Makefile` that only shells out to the
  existing scripts (`setup`, `dev`, `test`, `docs`, `lint`, `coverage`, `notebooks`,
  `export`, `launch`, `clean`) so the documented commands cannot drift.
- CI: a coverage run of the root suite and an advisory mypy pass on the 3.14 leg; a
  `release.yml` that re-runs the whole gate on a `v*` tag before attaching an sdist and
  wheel; Dependabot for pip and GitHub Actions; issue forms (bug, content error) and a
  PR template that repeats the CONTRIBUTING checklist.

## Tier 4 — Measurability

| Feature | Description |
|---|---|
| **`coach.py --readiness`** | A projected C1000-179 score with a 95 % band from exam-sim and dojo history, weighted by the published section weights and decayed by evidence age; refuses to print a number until ~40 observations cover 60 % of the exam weight, and says per section what would earn one. |
| **`coach.py --calibrate`** | Compare the SM-2 intervals in `flashcard_schedule.json` with measured recall from `flashcard_history.json` (same card seen twice) and say whether the schedule runs long or short; needs 20 repeat reviews before it judges. |
| **Dashboard retention view** | Weekly accuracy per category with the observation count behind every cell, and a forgetting curve `R(t) = exp(−t/τ)` fitted to repeat sightings of the same item — never fitted to fewer than 20 observations over 2 interval buckets, never reported below `R² = 0.5`. |

## Build order

1. **Phone deck + Pages** — the single largest friction; ships in a day.
2. **SM-2 + due-today** — makes the daily drill a queue instead of a choice.
3. **Nudge** — closes the loop between the plan and the person.
4. **Solutions, exam bank, katas** — content work that parallelises across contributors.
5. **Hygiene** — cheap, and it protects everything above from regressing.
6. **Readiness / calibration / retention** — only meaningful once 1–3 have generated data.
