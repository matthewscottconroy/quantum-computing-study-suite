# Getting Started

State of the suite as of 2026-08-27: content audited, corrected, and independently
re-verified; all seven apps launch; the docs corpus passes `tools/verify_docs.py`
with zero errors. One setup step remains before the API-powered apps work.

---

## The one missing piece: your API key

Six of the seven apps call the Claude API. Do either of these once:

```bash
export ANTHROPIC_API_KEY=sk-ant-...        # add to ~/.bashrc to persist
```
or
```bash
mkdir -p ~/.config/quantum-study
echo "sk-ant-..." > ~/.config/quantum-study/api_key.txt
```

Without a key you can still use, today:
- **flashcard-drill** — all 550 cards, fully offline
- **qec-trainer** — the 151 auto-graded problems (of 178) plus the decoder game
- **vqa-trainer** — the 153 multiple-choice problems (of 179)
- **qiskit-dojo** — all 36 coding katas (execution-graded locally; only the optional
  Claude review needs a key)
- **exam-sim** — full timed mock exams and sprints, fully offline
- **circuit-trainer sprint mode** — timed prediction drills, auto-graded
- **notebooks/**, **labs/** (fake-backend paths), **lesson-plans/**, **docs/** — all
  reading and executable material

## Environment (already done)

A venv at `.venv` has everything installed (Python 3.14, Qiskit 2.5.2, PyQt6,
anthropic, matplotlib, numpy, seaborn, qiskit-qasm3-import). Activate it:

```bash
cd ~/Development/Quantum-Computing
source .venv/bin/activate
```

---

## Day 1

```bash
source .venv/bin/activate
cd flashcard-drill && python main.py
```

Do one flashcard session (no key needed) to establish the daily habit, then skim
[docs/README.md](docs/README.md) — the ladder — and read the first file of
Chapter 1. That's it.

## The rhythm

The workflow every resource here is designed around:

1. **Read** a docs file (or lesson-plan module) and work its exercises on paper —
   solutions are in the collapsible blocks.
2. **Drill** the matching flashcard categories daily (10–15 min; the SRS weights
   what you miss).
3. **Quiz** yourself with the matching app to test retention:

| Reading | App |
|---|---|
| docs ch. 1–2 (math, QM) | math-quiz, flashcard-drill |
| docs ch. 3–4 (circuits, algorithms) | quantum-quiz, circuit-trainer |
| docs ch. 5 (QEC) | qec-trainer |
| docs ch. 6 (VQA) | vqa-trainer |
| docs ch. 7–8 (hardware, advanced) | quantum-quiz |
| any paper you're reading | paper-drill |

4. **Produce**: this is where skills actually form — write code in **qiskit-dojo**
   (execution-graded katas), work long-form problems and guided derivations in
   **problem-trainer**, run the executable **notebooks/** alongside each docs
   chapter, and take timed **exam-sim** mocks to measure readiness.
5. **Track and steer**: `python coach.py` is the daily driver — it reads every
   app's history and prescribes today's session (weakest categories, due reviews,
   a kata, a sprint). Run `python coach.py --diagnostic` once at the start for
   ladder placement, `--review` for the unified review queue, `--badges` to track
   the IBM Quantum Learning path. `python dashboard.py` shows the raw mastery
   report.

Follow the ladder order in [docs/README.md](docs/README.md) (Rung 1 → 8). The
recommended pace and per-chapter time estimates are in that file. Chapter 2 now
includes the wave-mechanics track (Schrödinger, oscillator, hydrogen,
perturbation theory), so the corpus stands alone against a standard QM course.

## If your goal is the IBM certification

Follow [lesson-plans/11-certification-prep.md](lesson-plans/11-certification-prep.md):
it maps every C1000-179 exam section to specific modules here, with a 5-week
schedule and a self-assessment checklist. Support tools:

- **qiskit-dojo** — 36 write-and-run katas weighted to the exam sections,
  including debugging and API-modernization drills
- **exam-sim** — timed 68-question/90-minute mocks scored against the 47/68 pass
  bar with per-section breakdowns, plus 10-minute section sprints
- flashcard-drill's **Qiskit API** category (45 exam-aligned cards)
- quantum-quiz's **Qiskit Certification (C1000-179)** subject (needs API key)
- Lessons 06 (Qiskit), 07 (QASM), 10 (Transpiling) — code verified on Qiskit 2.5.2
- **labs/** — the IBM hardware track, for hands-on runtime experience before the exam

Do the foundations first (docs ch. 1–4 at minimum) before starting the 5-week
cert track — the exam assumes the concepts, and tests the API.

## Housekeeping worth doing

- **Commit the current state.** The audited-and-fixed content exists only in the
  working tree; commit before you start editing anything, so there's a clean
  baseline: `git add -A && git commit`.
- After any future content edits, run the regression gate:
  `python tools/verify_docs.py --all` (from the venv).

## Known limitations (documented, not blockers)

- Lesson snippets that need `qiskit-ibm-runtime` or IBM hardware access are
  syntax-checked, not executed, by the verifier (10 of 22 blocks). To run
  circuits on real IBM hardware you'll eventually want
  `pip install qiskit-ibm-runtime` and an IBM Quantum Platform account.
- Exam logistics cited in lesson 11 (weights, passing score, price) are
  third-party-sourced — confirm on IBM's official C1000-179 page when you
  register.
- The docs are a self-contained companion, not a replacement for a textbook:
  the Further Reading sections point at Nielsen & Chuang / Griffiths / Preskill
  chapters where you'll want the deeper treatment.
