# Project 3 — Steane [[7,1,3]] Code Simulator

**Deliverable:** a simulator for the Steane code that encodes a logical qubit,
extracts syndromes, injects errors, decodes, and produces the payoff plot of
QEC: **logical error rate vs. physical error rate**, exhibiting the
pseudo-threshold crossover where encoding starts to help.

**Background:** the Steane code is the smallest CSS code correcting an
arbitrary single-qubit error, built from the classical [7,4,3] Hamming code
used twice (X and Z sectors). Its stabilizer group has 6 generators; the
distance is 3, so any weight-1 error is correctable and weight-2 errors cause
logical failures. Everything you need is in
[docs/05_quantum_error_correction/04_stabilizer_formalism.md](../docs/05_quantum_error_correction/04_stabilizer_formalism.md)
and [05_css_codes_and_steane.md](../docs/05_quantum_error_correction/05_css_codes_and_steane.md);
drill with the `qec-trainer` app first.

Simulation engine: stabilizer simulation, so 7+ qubits cost nothing.
Verified against the venv: `AerSimulator(method="stabilizer")` runs
Clifford+measure circuits correctly (GHZ test produced only `000`/`111`), and
`qiskit.quantum_info.StabilizerState` / `Pauli` / `PauliList` all import.
Error injection with random Paulis keeps everything Clifford — the whole
project runs in milliseconds per shot.

---

## Milestones

### M1 — Code data structures

Represent the code: the 6 stabilizer generators (3 X-type, 3 Z-type from the
Hamming parity-check matrix H), logical X̄ = X⊗7, Z̄ = Z⊗7 (up to stabilizer
multiplication).

```python
H_hamming = [[0,0,0,1,1,1,1],
             [0,1,1,0,0,1,1],
             [1,0,1,0,1,0,1]]   # columns = binary 1..7
```

**Acceptance criteria:**
- [ ] Generators stored as `qiskit.quantum_info.PauliList` (6 elements,
      weight 4 each).
- [ ] Test: all pairs of generators commute; logicals commute with all
      generators; X̄ and Z̄ anticommute.
- [ ] Test: every weight-1 Pauli error anticommutes with ≥ 1 generator
      (distance sanity check).

### M2 — Encoder

Build the encoding circuit |ψ⟩ → |ψ̄⟩ (standard Steane encoder: prepare six
ancilla-free qubits, H on three of them, CNOT network per the generator
matrix).

**Acceptance criteria:**
- [ ] `StabilizerState(encode(QuantumCircuit(7)))` is stabilized by all 6
      generators (use `StabilizerState.expectation_value(pauli)` == +1).
- [ ] Encoding |0⟩ vs |1⟩ (apply X̄ before or after) yields states
      distinguished by Z̄ expectation ±1.
- [ ] Encoding |+⟩ gives X̄ expectation +1.

### M3 — Syndrome extraction

Add 6 ancillas measuring the generators (ancilla-in-|+⟩ controlled-Pauli
pattern, or CNOT ladders for the CSS structure — both are in
[docs/05.../05_css_codes_and_steane.md](../docs/05_quantum_error_correction/05_css_codes_and_steane.md)).
Output: a 6-bit syndrome per shot.

**Acceptance criteria:**
- [ ] No error ⇒ syndrome 000000 on every shot.
- [ ] Each of the 21 weight-1 Pauli errors (7 qubits × {X, Y, Z}) produces its
      predicted, **unique-per-sector** syndrome: the 3 Z-checks locate any X
      error at binary position b₁b₂b₃, ditto X-checks for Z; Y triggers both.
      Test all 21 exhaustively.
- [ ] Syndrome extraction leaves an *unencoded-error-free* codeword intact
      (extract twice; second syndrome is trivial).

### M4 — Decoder + error injection

Lookup-table decoder (syndrome → correction Pauli; 2³ = 8 entries per sector).
Error channel: i.i.d. depolarizing with probability p per data qubit
(each qubit gets X, Y, or Z with p/3 each).

**Acceptance criteria:**
- [ ] Logical-failure detector: after correction, the residual operator is
      checked against the stabilizer group — failure iff residual ∉ ⟨S⟩, i.e.
      it acts as X̄, Ȳ, or Z̄. (Implement as: residual commutes with all
      generators but has Z̄/X̄ expectation flipped.)
- [ ] All 21 weight-1 errors are corrected perfectly (zero logical failures).
- [ ] Some weight-2 errors fail (find and record one explicitly — e.g. X₁X₂).

### M5 — The benchmark plot

Monte Carlo: for p ∈ {1e-4 … 0.3} (log grid, ≥ 10 points, ≥ 10⁴ shots each),
measure logical error rate p_L. Overlay the unencoded single-qubit error rate
(p_L = p line) and fit the low-p behavior.

**Acceptance criteria:**
- [ ] Log-log plot: p_L vs p, with the p_L = p reference line and the
      crossover (pseudo-threshold) marked. With perfect
      extraction it sits somewhere around the percent scale — record yours.
- [ ] Low-p fit: p_L ≈ c·p² (slope ≈ 2 on log-log); report c and the fitted
      slope (expect 2.0 ± 0.2). The p² law is the distance-3 signature —
      explain it in one sentence in NOTES.md.
- [ ] Error bars (binomial) on every point; shots chosen so the smallest p_L
      has ≥ 10 failure events.

### M6 — Noisy syndrome extraction (this is where QEC gets real)

Add measurement error: flip each syndrome bit with probability p_m, and use
**repeated extraction** (2–3 rounds, majority vote) as in
[docs/05.../07_fault_tolerance.md](../docs/05_quantum_error_correction/07_fault_tolerance.md).

**Acceptance criteria:**
- [ ] With p_m = p and single-round extraction, show the p² scaling is
      destroyed (slope → ~1 at low p).
- [ ] With 3-round majority voting, quadratic scaling is restored (slope back
      near 2); plot all three curves together.

---

## Starter scaffolding hints

- Keep two representations in sync: circuits (for Aer stabilizer runs) and
  symplectic binary vectors (for fast commutation checks:
  `Pauli.anticommutes(other)` or the binary symplectic product from
  [docs/05.../04_stabilizer_formalism.md](../docs/05_quantum_error_correction/04_stabilizer_formalism.md)).
  The Monte Carlo in M5 does **not** need circuits at all — pure symplectic
  arithmetic over F₂ (numpy int8 arrays) is ~1000× faster and is itself a
  great acceptance test against the circuit version.
- Layout: `p3/code.py` (generators, logicals), `p3/encoder.py`,
  `p3/syndrome.py`, `p3/decode.py`, `p3/montecarlo.py`, `p3/test_*.py`.
- The CSS structure means X and Z sectors decode *independently* — exploit it;
  Y errors are just X and Z at the same site.
- Determinism: seed the error generator; log (seed, p, shots) with results.

## Stretch goals

- Fault-tolerant flagged extraction (one flag qubit per generator) and compare
  pseudo-threshold against bare extraction.
- Swap the lookup decoder for minimum-weight decoding over the Hamming code
  and show identical performance (why? distance 3 — argue it).
- Do the same pipeline for the [[5,1,3]] perfect code and compare constants c.
- Transversal logic: verify X̄, Z̄, H̄ (transversal H works for Steane), and
  CNOT between two logical blocks; test logical Bell-pair creation.
- Estimate the same p_L curve on `FakeTorino`'s noise model (Aer, non-Clifford
  now — restrict to fewer shots) and compare with your i.i.d. model.

## References

- [docs/05_quantum_error_correction/02_classical_error_correction.md](../docs/05_quantum_error_correction/02_classical_error_correction.md) — Hamming [7,4,3]
- [docs/05_quantum_error_correction/04_stabilizer_formalism.md](../docs/05_quantum_error_correction/04_stabilizer_formalism.md) — symplectic machinery
- [docs/05_quantum_error_correction/05_css_codes_and_steane.md](../docs/05_quantum_error_correction/05_css_codes_and_steane.md) — the code itself
- [docs/05_quantum_error_correction/07_fault_tolerance.md](../docs/05_quantum_error_correction/07_fault_tolerance.md) — M6
- Shor 1995, Steane 1996, Gottesman 1997 — [reading ladder](../lesson-plans/12-reading-ladder.md), chapter 5 section
- `qec-trainer` app — drill syndromes before building
