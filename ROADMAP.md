# Training Roadmap — Skills-Gap Analysis and Proposed Features

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
