# Project 5 — Grover Search on a Real 3-SAT Instance

**Deliverable:** a Grover solver that takes an arbitrary 3-SAT formula in CNF,
builds a phase oracle *from the clauses*, runs amplitude amplification, and
reports a **resource comparison against classical search** (oracle calls,
gates, depth vs. clause evaluations) — plus a clear-eyed conclusion about what
the quadratic speedup does and doesn't buy.

**Background:** Grover's algorithm ([docs/04_quantum_algorithms/05_grover_search.md](../docs/04_quantum_algorithms/05_grover_search.md))
finds a marked item among N with ~(π/4)√(N/M) oracle calls (M = number of
solutions). 3-SAT gives a *structured* oracle: one multi-controlled flip per
clause. This project makes you build the oracle both ways — by hand from
clauses, and via Qiskit's synthesis — and confront the costs the textbook
picture hides (ancillas, Toffoli decomposition, and the "how many solutions?"
problem).

**Verified against the venv (executed):** `PhaseOracleGate` and
`grover_operator` (both `qiskit.circuit.library`). Note: the old `PhaseOracle`
class is **deprecated since Qiskit 2.2** — use `PhaseOracleGate`. A
7-clause, 3-variable instance with unique solution (v0,v1,v2)=(1,1,1) was run
through `grover_operator` with 2 iterations and produced P(`111`) = 0.945.
Also verified the classic failure mode: an instance with M = 5 of N = 8
solutions *inverts* — one iteration amplified the **non**-solutions
(P ≈ 0.28 each) because M > N/2. Your spec must handle this.

---

## Milestones

### M1 — Classical foundation

CNF representation (list of 3-literal clauses, literals ±(i+1) DIMACS-style),
a brute-force solver, and an instance generator (random 3-SAT at clause/variable
ratio α, plus a planted-solution generator).

**Acceptance criteria:**
- [ ] Parser round-trips DIMACS text; brute force counts solutions M exactly.
- [ ] The verified 7-clause instance above (in Qiskit expression syntax:
      `(v0|v1|v2)&(~v0|~v1|v2)&(v0|~v1|~v2)&(~v0|v1|~v2)&(v0|v1|~v2)&(v0|~v1|v2)&(~v0|v1|v2)`)
      is confirmed to have the unique solution (1,1,1).
- [ ] Random instances at α = 4.27 (the satisfiability threshold), n = 10:
      report the empirical SAT fraction over 200 instances (~0.5 expected).

### M2 — Oracle from clauses, by hand

Build the phase oracle yourself: per clause, an ancilla records "clause
violated" (an OR via De Morgan: X-conjugated multi-controlled-X); a
multi-controlled Z on "all clauses satisfied" applies the phase; then
**uncompute** the ancillas.

**Acceptance criteria:**
- [ ] `clause_oracle(cnf) -> QuantumCircuit` with n + n_clauses (+ scratch)
      qubits; unit test via `Statevector`: for **every** basis state, the
      amplitude picks up −1 iff the assignment satisfies the formula, and all
      ancillas return to |0⟩ (test on 3–4 variable instances exhaustively).
- [ ] Uncomputation verified: oracle² = identity (`Operator.equiv` on small
      instances).
- [ ] Cross-check against `PhaseOracleGate(expr)` on the data qubits
      (equal diagonal phases up to global phase).

### M3 — Amplitude amplification

Wrap the oracle with the diffuser — use `grover_operator(oracle)` (verified),
and also write your own diffuser (H⊗ⁿ · phase-flip-about-|0⟩ · H⊗ⁿ) to prove
they match. Iterate ⌊(π/4)√(N/M)⌋ times using M from M1.

**Acceptance criteria:**
- [ ] On the verified unique-solution instance: P(success) ≥ 0.94 with 2
      iterations (matches the authoring run: 0.9453).
- [ ] Success probability vs iteration count k plotted for one instance: the
      sin²((2k+1)θ) oscillation is visible, including *overshoot* past the
      optimum.
- [ ] The M > N/2 trap: reproduce the inverted-amplification failure and fix
      it (standard fix: add one ancilla-qubit to double the space so
      M/2N < 1/2, or detect M > N/2 classically and search the complement).
      Test demonstrates the fix.
- [ ] Unknown-M handling: implement the exponentially-growing-k randomized
      schedule (Boyer–Brassard–Høyer–Tapp) and show it finds solutions without
      knowing M, at O(√(N/M)) expected oracle calls.

### M4 — Resource counts vs classical

Transpile oracle + full Grover circuits to a hardware basis
(`generate_preset_pass_manager(optimization_level=3, backend=FakeTorino())`)
and count.

**Acceptance criteria:**
- [ ] Table vs n (variables) for planted instances at fixed α: oracle calls
      (quantum) vs expected clause-evaluations for classical brute force and
      for a random-guess baseline; and *per-oracle-call* cost: 2q-gate count
      and depth after transpilation.
- [ ] The honest crossover estimate: assuming (say) 1 µs per 2q gate layer and
      a modern CPU testing ~10⁹ assignments/s, at what n would Grover's
      wall-clock beat brute force *ignoring noise*? (You should land in the
      n ≳ 60–80 ballpark — show your arithmetic.) Then one paragraph on why
      noise makes even that optimistic
      ([docs/04.../05_grover_search.md](../docs/04_quantum_algorithms/05_grover_search.md)'s
      caveats + Preskill NISQ from the [reading ladder](../lesson-plans/12-reading-ladder.md)).
- [ ] Scaling fit: transpiled 2q-gate count per oracle call vs clause count is
      ~linear (plot).

### M5 — Noisy execution

Run the n = 3 verified instance under noise: `SamplerV2` in local testing mode
against `FakeTorino` ([lab 1](../labs/lab1_account_and_first_job.md) pattern),
and optionally on hardware.

**Acceptance criteria:**
- [ ] Noisy P(success) for 1 and 2 iterations, with shot-error bars, compared
      to ideal 0.945; explain the direction of the gap.
- [ ] The "more iterations = worse under noise" effect demonstrated: find the
      iteration count where noisy success probability peaks (it may be k = 1!).

---

## Starter scaffolding hints

- Bit-ordering discipline **from day one**: Qiskit counts keys are
  little-endian; decide that variable vᵢ ↔ qubit i ↔ counts-string position
  (n−1−i) and encode it in *one* helper (`assignment_from_bitstring`), tested.
  The authoring runs confirmed `PhaseOracleGate` maps v0 → qubit 0.
- Multi-controlled gates: `qc.mcx(controls, target)` exists; your transpile
  step will decompose it — that's part of the M4 story (Toffoli counts).
- `grover_operator(oracle)` builds the diffuser over all oracle qubits by
  default; when your hand-built oracle carries ancillas, pass
  `reflection_qubits=` (check its signature with `inspect` in the venv) or
  amplify only the data register — getting this wrong silently breaks
  amplification.
- Iterations: θ = arcsin(√(M/N)); optimal k = ⌊π/(4θ)⌋ is exact — use it in
  tests instead of the √(N/M) approximation for tiny N.

## Stretch goals

- Quantum counting: estimate M with QPE on the Grover operator
  ([docs/04_quantum_algorithms/04_quantum_phase_estimation.md](../docs/04_quantum_algorithms/04_quantum_phase_estimation.md))
  and compare with brute-force M on 3–4 variable instances.
- Solve a small graph-coloring or Sudoku-cell instance by reduction to CNF —
  end-to-end "real problem in, assignment out".
- Compare with a classical DPLL/WalkSAT implementation on the same instances:
  quadratic speedup vs *better algorithms* is the punchline.
- Amplitude estimation without phase estimation (iterative AE) for M.

## References

- [docs/04_quantum_algorithms/05_grover_search.md](../docs/04_quantum_algorithms/05_grover_search.md) — the algorithm and its caveats
- [docs/04_quantum_algorithms/01_quantum_parallelism_and_interference.md](../docs/04_quantum_algorithms/01_quantum_parallelism_and_interference.md) — why the diffuser works
- [docs/04_quantum_algorithms/04_quantum_phase_estimation.md](../docs/04_quantum_algorithms/04_quantum_phase_estimation.md) — counting stretch goal
- [docs/08_advanced_topics/01_quantum_complexity_theory.md](../docs/08_advanced_topics/01_quantum_complexity_theory.md) — BBBV optimality: √N is the best possible
- Grover 1996 & BBHT 1998 — [reading ladder](../lesson-plans/12-reading-ladder.md), chapter 4 section
