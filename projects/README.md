# Capstone Projects

Five multi-week projects that turn the [docs/](../docs/) theory and
[lesson-plans/](../lesson-plans/) curriculum into working code. Each project is
a spec, not a tutorial: it defines *what done looks like* (milestones with
acceptance criteria) and leaves the *how* to you.

| Project | Builds on | Core skill |
|---|---|---|
| [1 — VQE for H₂](project1_vqe_h2.md) | docs ch. 06, lesson 09, lab 5 | Variational algorithms, chemistry mapping |
| [2 — Custom transpiler pass](project2_transpiler_pass.md) | docs ch. 03, lesson 10 | Compiler engineering, DAG manipulation |
| [3 — Steane code simulator](project3_steane_simulator.md) | docs ch. 05, lesson 05 | Stabilizer QEC, error injection |
| [4 — BB84 with an eavesdropper](project4_bb84.md) | docs ch. 04 §08, lesson 08 | Quantum cryptography, information accounting |
| [5 — Grover on 3-SAT](project5_grover_sat.md) | docs ch. 04 §05, lesson 09 | Oracle construction, resource analysis |

All code fragments in the specs were written for **Qiskit 2.5.2 /
qiskit-ibm-runtime 0.49.0 / qiskit-aer 0.17.2** (the versions in this repo's
`.venv`), and the tricky ones were executed against those versions during
authoring. Use `.venv/bin/python`.

---

## How to work a project

1. **Read the whole spec first**, then the referenced docs chapters. The specs
   assume that background; they do not re-teach it.
2. **Create a working directory per project** (e.g. `projects/p1/` — your code
   directories are yours; only the `*.md` specs are maintained here).
3. **Work milestone by milestone, in order.** Milestones are gated: each one's
   acceptance criteria are the *inputs* the next milestone relies on. Don't
   move on with a milestone half-green.
4. **Keep a lab notebook** (`NOTES.md` in your project directory): what you
   tried, what failed, plots. Several acceptance criteria ask for numbers —
   record them when you get them.
5. **Write tests as you go.** Every project has at least one milestone whose
   acceptance criteria are literally "a test suite passes". `pytest` is the
   assumed runner.
6. **Only then** reach for stretch goals.

Budget expectation: 10–25 focused hours per project. Projects 1–3 are harder
than 4–5.

---

## How to ask Claude Code for a milestone review

When you finish a milestone, ask for a review in this shape — specific inputs,
specific criteria, explicit "don't fix it for me" if you want to stay in the
driver's seat:

```text
Review milestone 2 of projects/project3_steane_simulator.md.
My implementation is in projects/p3/steane.py, tests in projects/p3/test_steane.py.
Check each acceptance criterion, run the tests with .venv/bin/python -m pytest,
and tell me which criteria pass and which don't and why.
Don't rewrite my code — point at problems and reference the relevant
docs/ chapter so I can fix it myself.
```

Good review requests to make at each gate:

- **Criteria audit** — "which acceptance criteria does my code actually meet?"
- **Physics audit** — "is my math/simulation physically correct, per
  docs/05_quantum_error_correction/04_stabilizer_formalism.md?"
- **Test-gap audit** — "what edge cases do my tests miss for this milestone?"
- **Post-mortem** (after the final milestone) — "critique my design as if this
  were a code review for a library contribution."

Claude Code can run your code in the repo `.venv`, so reviews can be *verified*
("criterion 3 fails: your logical error rate is computed per-shot, not
per-round — rerun of your script shows 0.034, criterion demands < 0.02")
rather than stylistic.
