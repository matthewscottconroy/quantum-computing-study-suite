# Project 4 — BB84 with an Eavesdropper

**Deliverable:** a full BB84 key-distribution simulation — honest protocol,
intercept-resend Eve, QBER measurement, and the **information accounting**
that turns a sifted key into a secret key: error-correction leakage plus
privacy amplification, with a plot of secret-key fraction vs. Eve's
interception rate.

**Background:** BB84 (Bennett & Brassard, 1984) encodes random bits in
randomly chosen conjugate bases (Z: {|0⟩,|1⟩}, X: {|+⟩,|−⟩}). An
intercept-resend attacker measures in a random basis and resends her result;
whenever her basis is wrong she destroys the state, producing a **25% error
rate** on the affected, sifted positions. Security is then an exercise in
classical information theory: Alice and Bob must sacrifice bits to correct
errors and to erase Eve's partial knowledge. Read
[docs/04_quantum_algorithms/08_quantum_cryptography.md](../docs/04_quantum_algorithms/08_quantum_cryptography.md)
and [docs/02_quantum_mechanics/03_quantum_measurements.md](../docs/02_quantum_mechanics/03_quantum_measurements.md)
first.

Implementation note: qubit-level simulation here is genuinely simple — each
qubit is independent, so you can use either `qiskit.quantum_info.Statevector`
(verified import) per qubit or plain probability bookkeeping with numpy. Do
the first milestone with Statevectors so the quantum mechanics is explicit;
switch to vectorized numpy for the big Monte Carlo runs.

---

## Milestones

### M1 — Honest protocol (no Eve, no noise)

Implement Alice (random bits + random bases → states), the channel (identity),
Bob (random bases → measurements), and **sifting** (keep positions where bases
match, over an authenticated classical channel you model as a plain function
call).

**Acceptance criteria:**
- [ ] With n = 10,000 transmitted qubits: sifted fraction = 0.50 ± 0.02, and
      **zero** disagreements on the sifted key.
- [ ] Statevector check (test): each of the four states measured in its own
      basis is deterministic; measured in the conjugate basis gives 50/50
      (assert within binomial tolerance).
- [ ] Protocol is reproducible from a seed (test runs twice, identical keys).

### M2 — Intercept-resend Eve

Eve intercepts each qubit independently with probability η, measures in a
uniformly random basis, resends her outcome's eigenstate.

**Acceptance criteria:**
- [ ] QBER estimation by public comparison of a random sample (say 10%) of the
      sifted key — those bits are then **discarded** (they're public now).
- [ ] Measured QBER matches theory: QBER(η) = η/4. Verify at
      η ∈ {0, 0.25, 0.5, 1.0} within statistical error (n large enough that
      error bars are ~1%).
- [ ] Eve's information: track what Eve actually knows. Empirically confirm
      that on sifted positions she intercepted, her bit agrees with Alice's
      with probability 3/4 (η = 1 run).

### M3 — Detection decision

Alice and Bob abort above a QBER threshold. Justify the classic 11%
one-way-postprocessing threshold from the asymptotic key-rate formula in M5
(r = 1 − 2h(Q) hits zero at Q ≈ 0.11, with h the binary entropy).

**Acceptance criteria:**
- [ ] Abort logic with a configurable threshold; default justified in NOTES.md
      via the r(Q) = 1 − 2h(Q) zero.
- [ ] ROC-style analysis: for n_sample ∈ {50, 200, 1000} compared bits and
      η = 0.25 (QBER 6.25%), report the probability the estimate exceeds
      threshold (false alarms at η=0 too). Finite-size statistics matter —
      show them.

### M4 — Error correction accounting

You may *simulate* error correction rather than implement cascade: reveal
positions of errors using ground truth, but **charge the information-theoretic
price**: leak_EC = f · h(Q) bits per sifted bit, f ≥ 1 (use f = 1.1, a
realistic cascade efficiency; f = 1 is the Shannon limit).

**Acceptance criteria:**
- [ ] Post-EC keys are identical between Alice and Bob for every run (assert).
- [ ] The ledger records leak_EC in bits for each run.
- [ ] A test at Q = 0: leak_EC = 0; at Q = 0.0625, leak_EC/bit ≈ 1.1·h(0.0625)
      ≈ 0.37.

### M5 — Privacy amplification accounting + secret-key rate

Compress the corrected key with a 2-universal hash (simulate with a random
binary Toeplitz matrix over F₂ — actually implement this part) to length
ℓ = n_sift·(1 − leak_EC/bit − I_E) − safety margin, where for
intercept-resend Eve's information per sifted bit is I_E = η/2 bits
(she learns the bit fully on the half of intercepts where her basis matched:
η·½·1, plus nothing useful otherwise at the individual-attack level — derive
and defend this in NOTES.md, comparing with the conservative one-way bound
I_E = h(Q)).

**Acceptance criteria:**
- [ ] Toeplitz hashing implemented over F₂ (numpy), with a test that hashing
      is linear and seed-reproducible.
- [ ] Plot: secret-key fraction ℓ/n_sift vs η for both accounting choices
      (individual-attack I_E = η/2 and conservative I_E = h(QBER)); the
      conservative curve hits 0 at QBER ≈ 11% (η ≈ 0.44).
- [ ] End-to-end run at η = 0.2, n = 100,000: nonzero secret key produced,
      full ledger printed (raw → sifted → sampled → corrected → amplified).
- [ ] Sanity: at η = 1.0 both accountings give ℓ = 0 (protocol yields nothing).

### M6 — Write-up

**Acceptance criteria:**
- [ ] NOTES.md: protocol diagram, the η/4 derivation, the I_E derivation, the
      finite-size caveats you observed in M3, and a paragraph on what
      intercept-resend *doesn't* cover (collective attacks, channel loss,
      photon-number splitting) with pointers to the docs chapter.

---

## Starter scaffolding hints

- Data model: a run is a table (numpy record array / dict of arrays) with
  columns `alice_bit, alice_basis, eve_intercepted, eve_basis, eve_bit,
  bob_basis, bob_bit, sifted, sampled` — every milestone is a column-wise
  operation. Vectorize; 10⁶ qubits should take well under a second.
- Binary entropy: `h(p) = -p*log2(p) - (1-p)*log2(1-p)` with `h(0)=h(1)=0` —
  write it once, test it.
- Toeplitz-over-F₂ trick: represent the matrix by its first row+column;
  `(T @ key) % 2` with numpy is enough (no need for bit-packing).
- Keep *ground truth* (what Eve did) separate from *protocol view* (what
  Alice/Bob can see) — two namespaces. Accounting bugs almost always come from
  peeking.

## Stretch goals

- Implement real cascade (or LDPC-style syndrome exchange with the Hamming
  code from project 3!) and measure its actual f against h(Q).
- Add channel depolarizing noise p_ch and show Alice/Bob cannot distinguish
  noise from Eve — recompute keys assuming all QBER is Eve.
- E91 variant: entanglement-based version where the CHSH value
  ([docs/02_quantum_mechanics/04_entanglement_and_nonlocality.md](../docs/02_quantum_mechanics/04_entanglement_and_nonlocality.md))
  plays the QBER role.
- Partial-measurement Eve: she measures in the Breidbart basis (π/8) —
  compute and verify her optimal information/disturbance tradeoff.

## References

- [docs/04_quantum_algorithms/08_quantum_cryptography.md](../docs/04_quantum_algorithms/08_quantum_cryptography.md) — protocol + security intuition
- [docs/02_quantum_mechanics/03_quantum_measurements.md](../docs/02_quantum_mechanics/03_quantum_measurements.md) — measurement in conjugate bases
- [docs/08_advanced_topics/02_quantum_information_theory.md](../docs/08_advanced_topics/02_quantum_information_theory.md) — entropies for the accounting
- BB84 paper & Ekert 1991 — [reading ladder](../lesson-plans/12-reading-ladder.md), chapter 4 section
