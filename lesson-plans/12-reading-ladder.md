# Lesson 12 — The Reading Ladder

## Goal

Move from reading *about* quantum computing to reading the primary literature.
This lesson is a curated paper-reading program in two parts: a **classics
ladder** — thirteen landmark papers in historical-conceptual order that trace
the field from the EPR paradox to modern quantum LDPC hardware codes — and a
**per-chapter reading list** keyed to the eight [docs/](../docs/) chapters,
2–4 papers each, in recommended reading order. Every entry carries a
difficulty rating, what to extract from it, and a note on drilling it with the
[`paper-drill`](../paper-drill/) app.

**Difficulty scale:** ★ readable after the relevant docs chapter · ★★ needs
real effort, work through it with pencil and paper · ★★★ hard; expect multiple
passes and skipped sections on the first read.

**Sourcing note:** titles, authors, venues, and years below are given from
careful recall; arXiv identifiers are included only where confidence is high
and omitted otherwise — a title + author search finds every one of these
papers immediately. If a detail conflicts with the paper in front of you,
trust the paper.

---

## How to drill a paper

1. Read once for structure (abstract, section heads, figures, conclusions).
2. Read again for the argument, with the "what to get out of it" question in
   front of you.
3. Paste the paper (or the key sections — `paper-drill` truncates beyond
   ~12,000 characters, so for long papers paste the sections named in the
   drill note) into `paper-drill`, generate 5–10 questions, and answer them
   closed-book.
4. Score below 7/10 average → reread the flagged sections and re-drill with
   fresh questions.

---

## Part I — The Classics Ladder

Read in this order. Each rung either created a subfield or ended a debate.

### 1. EPR (1935) — ★★
A. Einstein, B. Podolsky, N. Rosen, *"Can Quantum-Mechanical Description of
Physical Reality Be Considered Complete?"*, Physical Review 47, 777 (1935).
- **Get out of it:** the precise definitions of "element of reality" and
  "completeness"; how entanglement (not yet so named) generates the paradox;
  why the argument is *logically valid* — the escape is in the premises.
- **Companion:** docs [02/04](../docs/02_quantum_mechanics/04_entanglement_and_nonlocality.md), lesson [08](08-foundations-of-quantum-mechanics.md).
- **Drill it:** conceptual questions only — ask paper-drill for the premises
  of the argument and where a local realist vs. a quantum mechanic must part ways.

<details><summary>Solution</summary>

**Model answer.** EPR argues that quantum mechanics is *incomplete*, and the argument
is valid — so one of its premises must be rejected.

- **Element of reality** (their definition, quoted almost verbatim): "if, without in
  any way disturbing a system, we can predict with certainty the value of a physical
  quantity, then there exists an element of physical reality corresponding to it."
- **Completeness**: every element of reality must have a counterpart in the theory.
- **Locality/separability** (assumed, never stated as a postulate): measuring system
  A cannot disturb a spatially separated system B.

**The argument.** Take the entangled state they construct (position/momentum
correlations; Bohm's spin version `(|01⟩−|10⟩)/√2` is the standard modern
substitute). Measuring `A` in the position basis predicts `B`'s position with
certainty; measuring `A` in the momentum basis predicts `B`'s momentum with
certainty. By locality, the choice made at `A` cannot affect `B`, so *both* must have
been elements of reality all along. Quantum mechanics assigns no simultaneous values
to non-commuting observables, therefore it is incomplete.

**Where a good reader lands.** The logic is airtight; the escape is in a premise.
Bohr's reply denies the "without in any way disturbing" clause for entangled
systems. Bell, thirty years later, shows the locality premise has *testable*
consequences — turning a philosophical dispute into an experiment. Note what EPR
does **not** claim: no signalling, no proof that hidden variables exist, only that
*if* locality holds, they must.

**Drill check.** A local realist must deny that the measurement choice at `A` is
free, or accept nonlocal influence; a quantum mechanic denies that the unmeasured
observable had a value. Both of those are premises, not conclusions.

</details>

### 2. Bell (1964) — ★★
J. S. Bell, *"On the Einstein Podolsky Rosen Paradox"*, Physics Physique
Fizika 1, 195 (1964).
- **Get out of it:** how a *testable inequality* falls out of the locality +
  hidden-variable assumptions; the exact role of the free-choice assumption;
  reproduce the inequality derivation yourself.
- **Drill it:** derivation questions — have paper-drill walk you through the
  correlation-function bound step by step; you fill in each inequality.

<details><summary>Solution</summary>

**Model answer.** Bell converts EPR's premises into an inequality that quantum
mechanics violates.

**Setup.** A hidden variable `λ` with distribution `ρ(λ)`; outcomes
`A(a, λ) = ±1` and `B(b, λ) = ±1`. *Locality* is the statement that `A` does not
depend on `b` and `B` does not depend on `a`. *Free choice* is that `ρ(λ)` does not
depend on the settings `a, b`. Perfect anticorrelation at equal settings forces
`B(a, λ) = −A(a, λ)`.

**The derivation (reproduce this without the paper).**

```
P(a,b) − P(a,c) = −∫ρ(λ)[A(a,λ)A(b,λ) − A(a,λ)A(c,λ)]dλ
                = −∫ρ(λ)A(a,λ)A(b,λ)[1 − A(b,λ)A(c,λ)]dλ
```

using `A(b,λ)² = 1`. The bracket is non-negative and `|A A| = 1`, so

```
|P(a,b) − P(a,c)| ≤ ∫ρ(λ)[1 − A(b,λ)A(c,λ)]dλ = 1 + P(b,c)
```

**Quantum violation.** For the singlet, `P(a,b) = −cos θ_ab`. Take
`θ_ab = 60°`, `θ_ac = 120°`, `θ_bc = 60°`:

```
|P(ab) − P(ac)| = |−0.5 − 0.5| = 1.0        1 + P(bc) = 1 − 0.5 = 0.5
```

`1.0 > 0.5` — the inequality fails by a factor of two.

**What the free-choice assumption does.** If `ρ(λ)` could depend on `a` and `b` (a
superdeterministic or detector-settings-correlated world), the factorisation above
never gets started and no inequality follows. This is the one loophole no experiment
can close, and it is why "free choice" is always listed alongside locality.

</details>

### 3. CHSH (1969) — ★★
J. F. Clauser, M. A. Horne, A. Shimony, R. A. Holt, *"Proposed Experiment to
Test Local Hidden-Variable Theories"*, Physical Review Letters 23, 880 (1969).
- **Get out of it:** why Bell's original inequality wasn't experiment-ready
  and what CHSH relaxed; the |S| ≤ 2 bound and the quantum 2√2 violation
  (Tsirelson bound — docs [02/04](../docs/02_quantum_mechanics/04_entanglement_and_nonlocality.md)).
- **Drill it:** factual + derivation mix; then, closed-book, write the four
  measurement settings that achieve 2√2.

<details><summary>Solution</summary>

**Model answer.** CHSH turns Bell's inequality into something an imperfect experiment
can actually test.

**What was wrong with Bell (1964).** Its derivation needs *perfect* anticorrelation
at identical settings, `P(a,a) = −1`. No real detector achieves that — any
inefficiency or misalignment makes the premise false and the inequality inapplicable.

**What CHSH relaxes.** Four settings instead of three, and no assumption about
perfect correlations. Define `S = E(a,b) + E(a,b') + E(a',b) − E(a',b')`. For any
local hidden-variable model, each term is an average of `±1` products and the
deterministic maximum is 2 (brute-forcing all 16 deterministic strategies confirms
`max|S| = 2`). Hence

```
|S| ≤ 2        (local realism)
```

**Quantum maximum.** For `|Φ⁺⟩ = (|00⟩+|11⟩)/√2` with in-plane measurement directions
`a = 0°, a' = 90°, b = 45°, b' = −45°`:

```
S = 2.828427 = 2√2        (Tsirelson bound)
```

verified by direct computation. `2√2` is not an accident: Tsirelson proved it is the
maximum over *all* quantum states and observables, so quantum mechanics is nonlocal
but not maximally so — a PR box would reach 4.

**Closed-book target.** The four settings above (equivalently `0°, 45°, 22.5°,
67.5°` in the half-angle convention used for photon polarisers), and the reason they
work: consecutive settings differ by 45°, so three correlators are `+1/√2` and the
fourth is `−1/√2`.

</details>

### 4. Deutsch–Jozsa (1992) — ★★
D. Deutsch, R. Jozsa, *"Rapid solution of problems by quantum computation"*,
Proceedings of the Royal Society A 439, 553 (1992).
- **Get out of it:** the first clean exponential quantum-classical separation
  (for exact computation); the phase-kickback + interference template every
  later algorithm reuses — compare with docs
  [04/02](../docs/04_quantum_algorithms/02_deutsch_jozsa_and_bernstein_vazirani.md)'s modern one-page version.
- **Drill it:** derivation drill on the modern form; then a conceptual round
  on *why* the speedup evaporates if you allow bounded error classically.

<details><summary>Solution</summary>

**Model answer.** Deutsch–Jozsa is the first clean exponential separation, and the
template every later algorithm reuses.

**Problem.** `f: {0,1}ⁿ → {0,1}` is promised to be constant or balanced. Decide
which. Classically, *exact* determination needs `2ⁿ⁻¹ + 1` queries in the worst case.
Quantumly, one.

**The circuit and the derivation.**

```
|0⟩^⊗n ──H⊗n──U_f──H⊗n──M
|1⟩    ──H────┘
```

The ancilla in `|−⟩` converts the oracle into a phase:
`U_f|x⟩|−⟩ = (−1)^f(x)|x⟩|−⟩` — that is the **phase kickback**. The query register
becomes `2^(−n/2) Σ_x (−1)^f(x)|x⟩`, and the final `H⊗ⁿ` gives amplitude

```
⟨0…0|ψ⟩ = (1/2ⁿ) Σ_x (−1)^f(x)
```

which is `±1` for constant `f` and exactly `0` for balanced `f`. Measuring anything
other than the all-zeros string proves "balanced" with certainty. That is **quantum
parallelism plus destructive interference** — the superposition alone does nothing;
the cancellation is the algorithm.

**The honest caveat, and why the drill asks for it.** Allow *bounded error*
classically and the separation evaporates: sample `O(1)` random inputs, and a
balanced function gives two different values with probability `1 − 2^(1−k)` after
`k` samples. Deutsch–Jozsa separates `P` from `EQP` relative to this oracle, not
`BPP` from `BQP`. Bernstein–Vazirani (hidden string, one query versus `n`) and later
Simon's problem are the bridge to a genuine bounded-error separation.

</details>

### 5. Shor (1994) — ★★★
P. W. Shor, *"Algorithms for Quantum Computation: Discrete Logarithms and
Factoring"*, Proc. 35th FOCS (1994). Journal version: *"Polynomial-Time
Algorithms for Prime Factorization and Discrete Logarithms on a Quantum
Computer"*, SIAM Journal on Computing 26, 1484 (1997), arXiv:quant-ph/9508027.
- **Get out of it:** the factoring → order-finding reduction (classical), and
  order-finding → phase estimation over the QFT (quantum); where the
  continued-fractions step enters. Read alongside docs
  [04/06](../docs/04_quantum_algorithms/06_shors_algorithm.md).
- **Drill it:** paste the order-finding section only; derivation questions on
  the QFT measurement statistics, plus one worked run of factoring 15 by hand.

<details><summary>Solution</summary>

**Model answer.** Shor is two reductions bolted together: a classical one and a
quantum one.

**Classical: factoring → order finding.** To factor odd composite `N` that is not a
prime power, pick `a` uniformly from `Z*_N`. If `gcd(a, N) > 1` you are already done.
Otherwise find the order `r` with `a^r ≡ 1 (mod N)`. If `r` is even and
`a^(r/2) ≢ −1 (mod N)`, then `N | (a^(r/2)−1)(a^(r/2)+1)` while dividing neither
factor, so `gcd(a^(r/2) ± 1, N)` is a non-trivial divisor. That happens with
probability `≥ 1 − 2^(1−k)` for `k` distinct prime factors, hence `≥ 1/2`.

**Quantum: order finding → phase estimation.** `U|y⟩ = |ay mod N⟩` is unitary on
`Z*_N`, with eigenvalues `e^(2πi s/r)` and eigenvectors
`|u_s⟩ = r^(−1/2) Σ_k e^(−2πisk/r)|a^k mod N⟩`. Crucially `|1⟩ = r^(−1/2) Σ_s |u_s⟩`,
so you can run QPE on `|1⟩` without knowing any eigenvector, and you get a uniformly
random `s`.

**Where continued fractions enter.** QPE with `t = 2n + 1` counting qubits returns an
integer `k` with `|k/2^t − s/r| ≤ 2^(−2n−1) < 1/(2r²)`. The classical theorem on
continued fractions says a rational with denominator `< N` is *uniquely* determined
by any approximation that good, so the convergents of `k/2^t` recover `s/r` in lowest
terms. Then `r` follows if `gcd(s, r) = 1`, which holds with probability
`φ(r)/r = Ω(1/log log r)`.

**Cost.** `O((log N)³)` gates dominated by modular exponentiation; `O(log N)` qubits.

**Worked check on `N = 15`, `a = 7`.** Four counting qubits give measurement outcomes
`{0, 4, 8, 12}` each with probability exactly `1/4`; `4/16 = 1/4` and `12/16 = 3/4`
both yield `r = 4`, and `7² = 49 ≡ 4`, so `gcd(3,15) = 3` and `gcd(5,15) = 5`. A
single run succeeds half the time.

</details>

### 6. Grover (1996) — ★★
L. K. Grover, *"A fast quantum mechanical algorithm for database search"*,
Proc. 28th STOC (1996), arXiv:quant-ph/9605043.
- **Get out of it:** the two-reflection geometry (it's a rotation in a 2-D
  subspace — docs [04/05](../docs/04_quantum_algorithms/05_grover_search.md)); why √N is optimal (BBBV);
  follow-up worth knowing: Boyer–Brassard–Høyer–Tapp, *"Tight bounds on
  quantum searching"* (1998), for unknown solution counts — needed by
  [project 5](../projects/project5_grover_sat.md).
- **Drill it:** derivation drill: recover sin²((2k+1)θ) from the rotation
  picture, then answer why k iterations can *overshoot*.

<details><summary>Solution</summary>

**Model answer.** Grover is a rotation in a plane, and the plane is two-dimensional
no matter how large `N` is.

**The geometry.** Split the uniform superposition into the marked component and the
rest: `|s⟩ = sin θ |w⟩ + cos θ |s'⟩` with `sin θ = √(M/N)`. The oracle reflects about
`|s'⟩`; the diffuser `2|s⟩⟨s| − I` reflects about `|s⟩`. The composition of two
reflections whose axes meet at angle `θ` is a **rotation by `2θ`**, and it never
leaves `span{|w⟩, |s'⟩}`. Hence

```
P_success(k) = sin²((2k+1)θ),   k_opt = π/(4θ) − 1/2 ≈ (π/4)√(N/M)
```

Recovering `sin²((2k+1)θ)` from the picture — draw the two mirror lines, note the
angle after `k` rotations is `(2k+1)θ` — is the whole derivation.

**Why `k` can overshoot.** A rotation is periodic. Past `k_opt` the state rotates
*away* from `|w⟩`. For `N = 8, M = 1` (`θ = 20.7°`) the success probabilities are
`0.125, 0.781, 0.945, 0.330, 0.012, …` — two iterations too many is worse than not
running the algorithm at all.

**Why `√N` is optimal.** BBBV's hybrid argument: an algorithm making `T` queries
spreads total query mass `T` over `N` indices, so some index `i*` receives at most
`T/N`; flipping the oracle at `i*` changes the final state by at most `2T/√N`.
Distinguishing needs that to be `Ω(1)`, hence `T = Ω(√N)`.

**The BBHT follow-up, and why project 5 needs it.** When `M` is unknown you cannot
choose `k`. Boyer–Brassard–Høyer–Tapp draw `k` uniformly from `[0, m)` with `m`
growing geometrically (`m ← 6m/5`), which finds a solution in `O(√(N/M))` expected
queries without knowing `M`, and detects `M = 0` in `O(√N)`. For SAT instances with
an unknown number of satisfying assignments, that is the algorithm you actually
implement.

</details>

### 7. Preskill NISQ (2018) — ★
J. Preskill, *"Quantum Computing in the NISQ era and beyond"*, Quantum 2, 79
(2018), arXiv:1801.00862.
- **Get out of it:** the vocabulary and the sober scorecard: what 50–100 noisy
  qubits can and cannot plausibly do; the framing every hardware paper since
  has been answering. Read before doing the [labs](../labs/).
- **Drill it:** factual + conceptual; a good first paper-drill session — it's
  prose, quantitative but not technical.

<details><summary>Solution</summary>

**Model answer.** Preskill names the era and sets the scorecard everything since has
been graded against.

**The vocabulary.** *NISQ* — Noisy Intermediate-Scale Quantum: 50–100 qubits,
two-qubit gate errors around `10⁻³`, no error correction, so circuit depth is capped
at roughly the inverse error rate — a few thousand two-qubit gates at best, and in
practice far fewer.

**What such a device can plausibly do.** Sampling tasks that are classically hard but
have no known use (random circuit sampling, boson sampling); variational algorithms
(VQE, QAOA) whose shallow circuits fit inside the coherence budget; small quantum
simulations of strongly correlated models. What it cannot do: Shor at cryptographic
scale, Grover at useful scale (the `√N` speedup is eaten by the error rate long
before `N` is interesting), or anything needing `10⁶`-gate circuits.

**The sober framing to carry away.**

- Quantum advantage is not the same as quantum *usefulness*, and Preskill is explicit
  that NISQ devices may deliver the first without the second.
- Error correction is the real destination; NISQ is a stepping stone whose main value
  may be as an engineering school for building the fault-tolerant machine.
- The classical competition improves too — any advantage claim is a moving target,
  which is exactly what happened to the 2019 supremacy claim.

**Why read it before the labs.** Every number you pull off `FakeTorino`'s target
(T1, T2, CX error, readout error) is a data point in Preskill's scorecard, and the
labs are where the abstract "depth is capped at `1/ε`" becomes a circuit that visibly
stops working.

</details>

### 8. Google Supremacy (2019) — ★★
F. Arute et al., *"Quantum supremacy using a programmable superconducting
processor"*, Nature 574, 505 (2019).
- **Get out of it:** what exactly was claimed (sampling, not useful
  computation); cross-entropy benchmarking (XEB) as the verification trick;
  the extrapolated-classical-cost controversy that followed. Companion: docs
  [07/04](../docs/07_quantum_hardware/04_benchmarking_and_characterization.md).
- **Drill it:** paste the main text (skip supplements); conceptual questions
  on XEB and on which criticisms of the classical-cost estimate later stuck.

<details><summary>Solution</summary>

**Model answer.** A precise, narrow claim, a clever verification trick, and a
classical-cost estimate that did not survive.

**What was claimed.** The 53-qubit Sycamore processor sampled from the output
distribution of a *random* quantum circuit (20 cycles, depth ~20) in about 200
seconds, a task the authors estimated would take the best classical supercomputer of
the day roughly 10 000 years. The claim is about **sampling**, not about computing
anything anyone wants — no factoring, no optimisation, no chemistry.

**Cross-entropy benchmarking (XEB), the verification trick.** You cannot check a
53-qubit sample against a classically computed distribution — that is the point. XEB
instead estimates the fidelity from the *average simulated probability of the
observed bitstrings*:

```
F_XEB = 2ⁿ ⟨ p_ideal(x_measured) ⟩ − 1
```

A perfect device gives `F ≈ 1`, a uniform-noise device gives `F ≈ 0`, because
Porter–Thomas statistics make the ideal distribution heavily non-uniform. Sycamore
reported `F_XEB ≈ 0.002` — two parts in a thousand — which is tiny but statistically
overwhelming over the millions of samples collected, and calibrated by a "digital
error model" whose
predicted fidelity is the product of individual gate fidelities.

**The controversy, and which criticisms stuck.** IBM argued almost immediately that a
tensor-network contraction using secondary storage would take days, not millennia.
Over the following years, tensor-network and Pauli-path methods (Pan–Zhang and
successors) reproduced the task in hours on classical clusters, and eventually at
comparable XEB fidelity. **The criticism that stuck** is that the 10 000-year figure
assumed a Schrödinger-style full-statevector simulation and badly underestimated
classical contraction algorithms. **What survived** is the experiment itself: the
device really did produce correlated samples at the claimed fidelity, and the
error-model calibration is the foundation of modern benchmarking.

</details>

### 9. Kitaev's Toric Code — ★★★
A. Yu. Kitaev, *"Fault-tolerant quantum computation by anyons"*, Annals of
Physics 303, 2 (2003); preprint 1997, arXiv:quant-ph/9707021.
- **Get out of it:** stabilizers from *local* plaquette/star operators;
  degeneracy from topology; anyonic excitations as syndrome endpoints. This is
  the ancestor of the surface code (docs [05/06](../docs/05_quantum_error_correction/06_surface_code.md))
  and of docs [08/04](../docs/08_advanced_topics/04_topological_quantum_computation.md).
- **Drill it:** first drill only §§ on the code and excitations; use the
  `qec-trainer` app in parallel — then a derivation round on why logical
  operators are non-contractible loops.

<details><summary>Solution</summary>

**Model answer.** Kitaev shows that error correction can be *geometric* — all the
checks are local, and all the protected information is topological.

**The code.** Qubits on the edges of an `L × L` square lattice on a torus
(`2L²` qubits). Two families of stabilizers, both weight 4 and both **local**:

```
star     A_v = Π_{e ∋ v} X_e      (edges meeting at a vertex v)
plaquette B_p = Π_{e ∈ ∂p} Z_e    (edges around a face p)
```

All of them commute — any star and plaquette share either 0 or 2 edges, so the
anticommutations cancel. There are `L²` of each with two global relations
(`Π A_v = Π B_p = I`), giving `2L² − 2` independent generators on `2L²` qubits and
hence `k = 2` logical qubits: the code is `[[2L², 2, L]]`.

**Degeneracy from topology.** The logical operators are `X`- and `Z`-strings running
around the two **non-contractible loops** of the torus. A contractible loop is a
product of stabilizers, so it acts trivially — that is the derivation the drill
wants. Two independent cycles × two operator types = 4 logical operators = 2 logical
qubits, and the code distance is `L`, the length of the shortest non-contractible
loop.

**Anyons as syndrome endpoints.** A single `Z` error on an edge anticommutes with the
two stars at its ends, flipping two syndromes; a chain of errors flips only the two
syndromes at its *endpoints*. Those endpoints behave as particles (`e` charges from
star violations, `m` fluxes from plaquette violations) with mutual `−1` braiding
statistics — the abelian anyons of the title. Decoding is therefore a *matching*
problem: pair up the excitations with the shortest error chain.

**Why this is the ancestor of everything.** Take the torus, cut it open into a planar
patch with boundaries, and you have the surface code; the local weight-4 checks are
exactly what makes a 2-D superconducting chip able to run it.

</details>

### 10. Panteleev–Kalachev (2021) — ★★★
P. Panteleev, G. Kalachev, *"Asymptotically Good Quantum and Locally Testable
Classical LDPC Codes"*, arXiv:2111.03654 (2021); STOC 2022.
- **Get out of it:** what "asymptotically good" means (constant rate *and*
  constant relative distance) and why it was a decades-open problem; the
  lifted/balanced-product construction at block-diagram level — full proofs
  are graduate-combinatorics hard; skimming them is allowed. Companion: docs
  [05/09](../docs/05_quantum_error_correction/09_qldpc_codes.md).
- **Drill it:** conceptual/factual only; ask paper-drill for the statement of
  the main theorem and the definitions it needs — don't drill the proofs.

<details><summary>Solution</summary>

**Model answer.** A decades-open existence question, answered.

**What "asymptotically good" means.** A family of `[[n, k, d]]` codes is
*asymptotically good* if **both** the rate `k/n` and the relative distance `d/n` stay
bounded below by positive constants as `n → ∞`. Classical LDPC codes with this
property have existed since Gallager (1962). The quantum case was open for over
twenty years.

**Why it was hard.** The CSS construction needs two classical codes with
`C₂^⊥ ⊆ C₁`, which forces the parity checks to overlap in even numbers of positions —
a severe constraint once you also demand *low weight* (LDPC) checks. The surface code
is the cautionary example: `[[n, 1, √n]]`, so both rate and relative distance vanish.
Hypergraph-product codes reached constant rate but distance only `Θ(√n)`.

**The construction, at block-diagram level.** Panteleev–Kalachev use **lifted
products**: take a hypergraph/tensor product of two chain complexes, but with the
entries lifted from `F₂` to the group algebra `F₂[G]` of a suitable non-abelian
group. The group structure supplies the expansion that the plain product lacks, and
a probabilistic argument over the lift shows a good choice exists. The same machinery
yields the first locally testable classical codes with constant rate, distance and
query complexity — the "`c³`-LTC" result that arrived in parallel.

**How to read it.** The theorem statement and the definitions it needs (chain
complex, lift, balanced/lifted product, expansion) are within reach; the proofs are
graduate combinatorics and skimming them is the right call on a first pass.

**What it does and does not deliver.** It settles *existence* asymptotically. It says
nothing directly about thresholds, decoders, or whether the required connectivity is
buildable — the constructions need long-range checks that no planar chip provides.
That gap is exactly what the next rung, the IBM gross code, attacks.

</details>

### 11. IBM Gross Code (2024) — ★★
S. Bravyi, A. W. Cross, J. M. Gambetta, D. Maslov, P. Rall, T. J. Yoder,
*"High-threshold and low-overhead fault-tolerant quantum memory"*, Nature 627,
778 (2024), arXiv:2308.07915.
- **Get out of it:** bivariate bicycle codes; the headline [[144,12,12]]
  "gross" code and its ~10× qubit-overhead saving vs. surface codes; the price
  (long-range couplers, harder logic). The paper that made qLDPC an
  engineering roadmap. Companion: docs [05/09](../docs/05_quantum_error_correction/09_qldpc_codes.md).
- **Drill it:** factual round on the code parameters and assumptions, then
  conceptual: what exactly does the surface code still do better?

<details><summary>Solution</summary>

**Model answer.** The paper that turned qLDPC from a theorem into an engineering
roadmap, by finding a code that is good *at a useful finite size* rather than
asymptotically.

**Bivariate bicycle codes.** Build the two CSS parity-check matrices from polynomials
in two commuting cyclic shifts `x` and `y` on an `ℓ × m` grid:

```
A = x^a1 + y^a2 + y^a3      H_X = [A | B]
B = y^b1 + x^b2 + x^b3      H_Z = [Bᵀ | Aᵀ]
```

`A B = B A` guarantees `H_X H_Zᵀ = 0`, so the CSS condition holds by construction.
Every check has **weight 6** and every qubit touches 6 checks, independent of size —
that is the LDPC property, and it is why the syndrome circuit stays shallow.

**The headline numbers.** The `[[144, 12, 12]]` "gross" code (the name is the old
unit: 144 = a gross) stores **12 logical qubits in 144 data qubits** plus 144
ancillas — 288 physical qubits in total. A surface code storing 12 logical qubits at
distance 12 needs roughly `12 × 2d² ≈ 3456` physical qubits. That is the paper's
**order-of-magnitude overhead saving**,
and the simulated threshold is comparable — around `0.7%` under circuit-level
depolarising noise with a BP-OSD decoder.

**The price, which the drill asks about.** Weight-6 checks on a bivariate torus need
**long-range couplers**: the layout requires two planar layers of connectivity, with
some couplers spanning the array rather than joining nearest neighbours. And logic is
harder — the surface code has clean lattice surgery, transversal-ish CNOTs and a
well-understood magic-state pipeline, while qLDPC codes need ancilla surface-code
patches or more exotic constructions to perform gates at all.

**What the surface code still does better.** Strictly 2-D nearest-neighbour
connectivity, a higher and better-characterised threshold, decoders that are fast and
provably good (minimum-weight matching), single-shot-ish syndrome handling, and a
mature story for logical operations. The gross code wins on **memory overhead**; the
surface code wins on **buildability and computation**.

</details>

### 12. VQE — Peruzzo et al. (2014) — ★★
A. Peruzzo, J. McClean, P. Shadbolt, M.-H. Yung, X.-Q. Zhou, P. J. Love,
A. Aspuru-Guzik, J. L. O'Brien, *"A variational eigenvalue solver on a
photonic quantum processor"*, Nature Communications 5, 4213 (2014),
arXiv:1304.3061.
- **Get out of it:** the division of labor (quantum expectation values,
  classical optimizer) and *why* that helps with coherence limits; how the
  Hamiltonian averaging works term by term. Then do
  [project 1](../projects/project1_vqe_h2.md) and [lab 5](../labs/lab5_full_workflow.md).
- **Drill it:** conceptual drill, then re-derive the variational bound
  E(θ) ≥ E₀ closed-book.

<details><summary>Solution</summary>

**Model answer.** VQE moves the hard part out of the coherent circuit.

**The division of labour.** The quantum processor prepares `|ψ(θ)⟩` and measures
expectation values of Pauli terms; a *classical* optimiser proposes the next `θ`.
Decomposing `H = Σ_i h_i P_i` and using linearity,

```
⟨H⟩ = Σ_i h_i ⟨ψ(θ)|P_i|ψ(θ)⟩
```

each term measured in its own basis and averaged — "Hamiltonian averaging". Terms
that commute qubit-wise can share a measurement basis, which is the main
shot-reduction lever.

**Why that helps with coherence limits.** QPE-based energy estimation needs a
*single* coherent circuit of depth `O(1/ε)` — thousands of gates for chemical
accuracy, far beyond a NISQ device. VQE replaces it with many circuits of depth
`O(1)`, paying in **measurement shots** (which are cheap and parallelisable) instead
of **coherence** (which is not). The experiment in the paper is a two-qubit photonic
processor computing the ground state of HeH⁺, which is tiny — the point is the
protocol, not the molecule.

**The variational bound, closed-book.** Expand the trial state in the exact
eigenbasis, `|ψ(θ)⟩ = Σ_n c_n|n⟩` with `Σ|c_n|² = 1`:

```
E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩ = Σ_n |c_n|² E_n ≥ E₀ Σ_n |c_n|² = E₀
```

with equality exactly when `|ψ(θ)⟩` is a ground state. So the energy is a *loss
function you can never undershoot* — every improvement is real, and the gap
`E(θ) − E₀` is an honest error bar on the state preparation.

**What the paper does not solve, and what the follow-ups are for.** Nothing here
guarantees the ansatz can reach `E₀` (expressibility), that the optimiser can find it
(barren plateaus, McClean 2018), or that noise leaves the estimate usable (Kandala
2017 and error mitigation). Doing project 1 and lab 5 is where those become concrete.

</details>

### 13. QAOA — Farhi, Goldstone, Gutmann (2014) — ★★
E. Farhi, J. Goldstone, S. Gutmann, *"A Quantum Approximate Optimization
Algorithm"*, arXiv:1411.4028 (2014).
- **Get out of it:** the alternating cost/mixer structure; the p → ∞ adiabatic
  limit; the MaxCut p = 1 ring analysis you can follow completely. Companion:
  docs [06/04](../docs/06_variational_quantum_algorithms/04_qaoa.md), `vqa-trainer` app.
- **Drill it:** derivation drill on the p = 1 expectation for a single edge;
  conceptual round on what is actually known about QAOA's advantage (be
  honest: not much is proven).

<details><summary>Solution</summary>

**Model answer.** QAOA is a discretised adiabatic path with the schedule turned into
free parameters.

**The construction.** Encode the objective as a diagonal Hamiltonian `C`, take the
transverse-field mixer `B = Σ_j X_j`, and alternate:

```
|γ,β⟩ = e^(−iβ_p B) e^(−iγ_p C) … e^(−iβ_1 B) e^(−iγ_1 C) |+⟩^⊗n
```

Maximise `⟨γ,β|C|γ,β⟩` over the `2p` angles classically. `C` is diagonal, so
`e^(−iγC)` is a product of `RZ` and `RZZ` gates — one layer per edge; the mixer is a
layer of `RX`.

**The `p → ∞` limit.** A Trotterised adiabatic evolution from the `B` ground state
`|+⟩^⊗n` to the `C` ground state is exactly of this alternating form, so the
adiabatic theorem guarantees that some choice of angles approaches the optimum as
`p → ∞`. QAOA at finite `p` is that path with the schedule *optimised* rather than
guessed, which is why it can beat the Trotterised schedule at the same depth.

**The `p = 1` ring analysis you can follow completely.** On the ring of disagrees
(the `n`-cycle MaxCut, whose optimum is `n` for even `n`), locality makes the
expectation a sum of identical single-edge terms, each computable in closed form
because the reverse light-cone of an edge is only three qubits at `p = 1`. The result
is the famous

```
approximation ratio = (2p + 1)/(2p + 2)    ->   3/4 at p = 1
```

Direct simulation confirms it: optimising `(γ, β)` for the 6-, 8- and 10-cycle gives
`⟨C⟩ = 4.5, 6.0, 7.5` against maximum cuts of `6, 8, 10` — a ratio of exactly
`0.7500` in every case.

**Be honest about the advantage.** For general 3-regular MaxCut, `p = 1` QAOA
guarantees `0.6924`, while the classical Goemans–Williamson SDP guarantees `0.8785`.
No proven quantum advantage for QAOA exists on any natural optimisation problem;
there are obstruction results at low `p` on large-girth graphs, and barren-plateau
and noise problems at large `p`. The interesting claims are empirical, and the
reading should leave you able to say precisely that.

</details>

---

## Part II — Per-Chapter Reading Lists

Papers already on the classics ladder are cross-referenced, not repeated —
read them at their ladder position.

### Chapter 01 — Mathematical Foundations ([docs/01](../docs/01_mathematical_foundations/))

1. **Dirac (1939)**, *"A New Notation for Quantum Mechanics"*, Mathematical
   Proceedings of the Cambridge Philosophical Society 35, 416. — ★
   - *Get:* bra-ket notation from its inventor, in four pages; why the
     notation *is* the linear algebra of lesson [01](01-linear-algebra.md).
   - *Drill:* light factual round; mostly a historical pleasure read.

   <details><summary>Solution</summary>

   **Model answer.** Dirac's four pages introduce notation that *is* the linear algebra,
   not a shorthand for it.

   - A **ket** `|ψ⟩` is a vector in a complex vector space; a **bra** `⟨φ|` is an element
     of its dual, i.e. a linear functional. The inner product `⟨φ|ψ⟩` is literally the
     functional applied to the vector — the "bracket" split in two, which is where the
     names come from.
   - The **Riesz correspondence** `|ψ⟩ ↔ ⟨ψ|` (antilinear, since `⟨aψ| = a*⟨ψ|`) is what
     makes the notation consistent, and it is the reason the adjoint `†` reverses order.
   - The **outer product** `|ψ⟩⟨φ|` is an operator, and `Σ_i |i⟩⟨i| = I` (completeness)
     lets you insert a resolution of the identity anywhere — the single most-used
     manipulation in the whole subject.
   - The notation is *basis-free*: `|ψ⟩` names the state, `⟨i|ψ⟩` names its `i`-th
     component. Everything in lesson 01 is this.

   **What a good reader notices.** Dirac motivates the notation by how it makes
   associativity do the work: `⟨φ|(A|ψ⟩) = (⟨φ|A)|ψ⟩`, so you can read expressions
   left-to-right or right-to-left and never need to track whether something is a row or
   a column. The mild dishonesty worth spotting is that in infinite dimensions not every
   bra has a corresponding normalisable ket (`⟨x|` is not in the Hilbert space) — the
   rigged-Hilbert-space subtlety Dirac glosses over and docs 01/08 makes precise.

   Read it as a historical pleasure, but close it able to state: bra = dual vector,
   ket = vector, bracket = inner product, ket-bra = operator.

   </details>

2. **Ekert & Knight (1995)**, *"Entangled quantum systems and the Schmidt
   decomposition"*, American Journal of Physics 63, 415. — ★★
   - *Get:* the Schmidt decomposition as a working tool — existence proof,
     relation to SVD, reduced-state spectra. Pairs with docs
     [01/03](../docs/01_mathematical_foundations/03_tensor_products_and_multipartite_systems.md).
   - *Drill:* derivation drill; then compute the Schmidt coefficients of two
     given 2-qubit states by hand and check with `qiskit.quantum_info`.

   <details><summary>Solution</summary>

   **Model answer.** The Schmidt decomposition is the singular value decomposition wearing
   physics notation, and it makes bipartite entanglement a one-number question.

   **Statement.** Any pure `|ψ⟩ ∈ H_A ⊗ H_B` can be written

   ```
   |ψ⟩ = Σ_(i=1)^(r) λ_i |a_i⟩ ⊗ |b_i⟩,    λ_i > 0,  Σ λ_i² = 1
   ```

   with `{|a_i⟩}` and `{|b_i⟩}` orthonormal in their own factors. `r` is the **Schmidt
   rank** and the `λ_i` are the **Schmidt coefficients**.

   **Existence proof (the derivation the drill wants).** Write
   `|ψ⟩ = Σ_(jk) C_(jk) |j⟩|k⟩` in any product basis and take the SVD `C = U Σ V†`.
   Setting `|a_i⟩ = Σ_j U_(ji)|j⟩` and `|b_i⟩ = Σ_k V*_(ki)|k⟩` gives the form above with
   `λ_i` the singular values. Existence and uniqueness (up to degeneracy) come free from
   the SVD.

   **Relation to reduced states.** `ρ_A = Tr_B|ψ⟩⟨ψ| = Σ_i λ_i²|a_i⟩⟨a_i|` and
   `ρ_B = Σ_i λ_i²|b_i⟩⟨b_i|` — *the two reduced density matrices have identical
   non-zero spectra*, however different their dimensions. Hence `r = 1` iff the state is
   a product state, and the entanglement entropy is `S = −Σ λ_i² log λ_i²` for either
   side.

   **Worked check.** For `|ψ⟩ = √0.8|00⟩ + √0.2|11⟩`,
   `qiskit.quantum_info.schmidt_decomposition` returns coefficients
   `0.894427, 0.447214` — exactly `√0.8` and `√0.2`; the reduced state has eigenvalues
   `{0.8, 0.2}` and `entropy(ρ_A) = 0.721928 = −0.8 log₂0.8 − 0.2 log₂0.2`.

   **The limitation to state out loud.** There is no Schmidt decomposition for three or
   more parties — `GHZ` and `W` are inequivalent classes with no single-number summary,
   which is why multipartite entanglement needs the machinery of the next paper.

   </details>

3. **Horodecki, Horodecki, Horodecki & Horodecki (2009)**, *"Quantum
   entanglement"*, Reviews of Modern Physics 81, 865, arXiv:quant-ph/0702225. — ★★★
   - *Get:* a *map*, not mastery: separability criteria, entanglement
     measures, distillation. Read §§ I–IV now; keep as a reference.
   - *Drill:* paste one section at a time (it's far beyond the truncation
     limit); factual questions to build the taxonomy.

   <details><summary>Solution</summary>

   **Model answer.** Read this for the *map*, and keep it as a reference. A good
   first-pass summary is a taxonomy, not a mastery claim.

   **Separability.** A mixed state is separable if `ρ = Σ_i p_i ρ_A^i ⊗ ρ_B^i`, entangled
   otherwise. Deciding this is NP-hard in general. The workhorse criteria:

   - **PPT / Peres–Horodecki**: separable implies `ρ^(T_B) ⪰ 0`. Necessary *and
     sufficient* only for `2×2` and `2×3` systems (the Horodeckis' own theorem); in
     higher dimensions PPT entangled ("bound") states exist.
   - **Entanglement witnesses**: a Hermitian `W` with `Tr(Wσ) ≥ 0` for all separable `σ`
     but `Tr(Wρ) < 0` for the target — the experimentally usable form, and dual to the
     separability problem by Hahn–Banach.
   - Others to recognise: reduction criterion, range criterion, CCNR/realignment.

   **Measures.** For *pure* states everything collapses to the entropy of entanglement.
   For mixed states the measures split: entanglement of formation and entanglement cost
   (how much is needed to make it), distillable entanglement (how much you can get
   back), relative entropy of entanglement, negativity (the computable one, from PPT).
   Key fact: they disagree, and `E_D ≤ E_F` strictly for bound entangled states, where
   `E_D = 0` but `E_F > 0`.

   **Distillation.** LOCC protocols converting many noisy copies into fewer near-maximal
   ones; the asymptotic rate is `E_D`. **Bound entanglement** — entangled but
   undistillable — is the conceptual surprise of the field.

   **How to read it.** Sections I–IV now, one at a time, pasting each into `paper-drill`
   separately since the whole review is far beyond the truncation limit. Build the
   taxonomy first; the proofs can wait until a specific one is needed.

   </details>

### Chapter 02 — Quantum Mechanics ([docs/02](../docs/02_quantum_mechanics/))

1. **EPR (1935)** — classics ladder #1.
2. **Bell (1964)** — classics ladder #2, then **CHSH (1969)** — ladder #3.
3. **Zurek (2003)**, *"Decoherence, einselection, and the quantum origins of
   the classical"*, Reviews of Modern Physics 75, 715, arXiv:quant-ph/0105127. — ★★★
   - *Get:* pointer states and einselection; why decoherence explains the
     *appearance* of collapse without resolving the measurement problem
     (lesson [08](08-foundations-of-quantum-mechanics.md) makes that
     distinction load-bearing). Pairs with docs
     [02/05](../docs/02_quantum_mechanics/05_density_matrices_and_open_systems.md) and [02/10](../docs/02_quantum_mechanics/10_distance_measures_and_lindblad.md).
   - *Drill:* conceptual only, section by section; ask explicitly for
     questions distinguishing decoherence from collapse.

   <details><summary>Solution</summary>

   **Model answer.** Decoherence explains why the world *looks* classical. It does not
   explain why one outcome happens.

   **Einselection and pointer states.** A system does not decohere in the abstract — it
   decoheres relative to how it couples to its environment. The interaction Hamiltonian
   `H_SE` selects a preferred basis: the **pointer states** are those left (nearly)
   unchanged by the coupling, i.e. the eigenstates of the system operator appearing in
   `H_SE`, or more precisely the states that commute with it (the "commutativity
   criterion"). Everything else gets rapidly correlated with the environment. This is
   **environment-induced superselection** — einselection — and it is why position, not
   momentum superpositions, survives for a dust grain.

   **The mechanism.** `(α|0⟩+β|1⟩)|E⟩ → α|0⟩|E₀⟩ + β|1⟩|E₁⟩`. Tracing out the
   environment leaves `ρ_S` with off-diagonal terms multiplied by `⟨E₀|E₁⟩`, which for a
   macroscopic environment decays on a timescale many orders of magnitude shorter than
   `T₁`. The improper mixture that results is *indistinguishable by any local
   measurement* from a classical probability distribution.

   **The distinction lesson 08 makes load-bearing.** Decoherence turns a coherent
   superposition into a **mixture**, but a mixture is still "all outcomes with
   probabilities". Nothing in the unitary evolution picks one. The measurement problem —
   why *this* outcome — is untouched: Everettians say all branches occur, collapse
   theories add dynamics, epistemic interpretations deny the question. Zurek's own
   programme (quantum Darwinism, einselection) explains the *emergence of objectivity*
   via redundant records in the environment, not the selection of an outcome.

   **Drill focus.** Ask explicitly for questions that separate "why is the density matrix
   diagonal in the pointer basis" (decoherence answers this) from "why do I see one
   value" (it does not). Pairs directly with docs `02/05` and `02/10`, where the Lindblad
   equation gives the quantitative version.

   </details>

4. **Hensen et al. (2015)**, *"Loophole-free Bell inequality violation using
   electron spins separated by 1.3 kilometres"*, Nature 526, 682. — ★★
   - *Get:* what the detection and locality loopholes were and how the
     event-ready scheme closes both at once; the experiment that ended the
     hidden-variable escape routes.
   - *Drill:* factual round on the loopholes; conceptual on why closing both
     *simultaneously* was the hard part.

   <details><summary>Solution</summary>

   **Model answer.** The experiment that closed the last two doors on local realism at
   the same time.

   **The two loopholes.**

   - **Detection (fair-sampling) loophole.** If detectors miss most events, a local model
     can reproduce the quantum correlations by conditioning *which* events get detected
     on the local setting. Closing it requires detection efficiency above a threshold
     (~2/3 for CHSH with maximally entangled states); photon experiments historically
     could not reach it, while ion and atom experiments could.
   - **Locality (communication) loophole.** If a signal can travel from Alice's setting
     choice to Bob's outcome, the correlations are trivially explicable. Closing it
     requires the setting choice and the distant outcome to be spacelike separated —
     which needs distance and fast randomness, and historically forced *short* detection
     windows and therefore lossy photon detection.

   They pull in opposite directions: distance costs efficiency, efficiency costs
   distance. That tension is why closing both at once was the hard part.

   **The event-ready scheme.** Two NV centres in diamond, 1.3 km apart. Each spin emits
   a photon entangled with it; the photons meet at a midpoint and a Bell-state
   measurement **heralds** entanglement between the two distant spins. Heralding is the
   trick: the photon loss happens *before* the measurement settings are chosen, so
   losing photons only lowers the rate, not the fairness of the sample. Once heralded,
   the spins are read out with near-unit efficiency, and the 1.3 km separation makes
   setting choice and distant readout spacelike separated.

   **Result.** `S = 2.42 ± 0.20` over 245 heralded trials, violating `|S| ≤ 2` with a
   p-value around `0.04` — statistically modest but loophole-free, and confirmed by
   higher-statistics photonic experiments in Vienna and at NIST the same year.

   **What remains open.** Only superdeterminism / freedom-of-choice, which no experiment
   can close; later "cosmic Bell" tests pushed setting choices back to photons from
   distant quasars, which narrows but cannot eliminate it.

   </details>

### Chapter 03 — Quantum Gates and Circuits ([docs/03](../docs/03_quantum_gates_and_circuits/))

1. **DiVincenzo (2000)**, *"The Physical Implementation of Quantum
   Computation"*, Fortschritte der Physik 48, 771, arXiv:quant-ph/0002077. — ★
   - *Get:* the five DiVincenzo criteria — the checklist every hardware
     platform in docs [07](../docs/07_quantum_hardware/) is graded against.
   - *Drill:* closed-book: list all five criteria (plus the two communication
     ones) and give one platform that struggles with each.

   <details><summary>Solution</summary>

   **Model answer — the five criteria, closed-book, with a platform that struggles with
   each:**

   1. **A scalable physical system with well-characterised qubits.** Struggles:
      semiconductor spin qubits — fabrication variability means every dot is slightly
      different and must be individually characterised.
   2. **The ability to initialise the state to a simple fiducial state such as
      `|000…⟩`.** Struggles: NMR, where at room temperature the thermal state is almost
      maximally mixed and only pseudo-pure states are available.
   3. **Long relevant decoherence times, much longer than the gate-operation time.**
      Struggles: superconducting qubits — `T₂` of tens to hundreds of microseconds
      against gate times of tens of nanoseconds gives a ratio of `10³–10⁴`, which is the
      binding constraint on NISQ depth.
   4. **A universal set of quantum gates.** Struggles: linear optics, where two-photon
      gates are not deterministic and KLM-style measurement-induced nonlinearity plus
      heavy ancilla overhead is required.
   5. **A qubit-specific measurement capability.** Struggles: neutral atoms and some
      ion species, where fluorescence readout can be slow and can heat or lose the
      qubit.

   **The two communication criteria** (often forgotten, and the reason this is a
   "five plus two" list):

   6. The ability to **interconvert stationary and flying qubits**.
   7. The ability to **faithfully transmit flying qubits** between distant locations.

   **How to read the paper.** It is a scorecard, not a theory paper, and its real value
   is that every hardware chapter in docs `07` is implicitly answering it. Note that no
   platform is bad at all five — each is excellent at some and poor at others, which is
   exactly why the field has not converged. Note also what DiVincenzo does *not* list:
   connectivity, gate fidelity thresholds, and classical control bandwidth, all of which
   turned out to matter as much as anything on his list.

   </details>

2. **Barenco et al. (1995)**, *"Elementary gates for quantum computation"*,
   Physical Review A 52, 3457, arXiv:quant-ph/9503016. — ★★
   - *Get:* universality of single-qubit + CNOT; the standard Toffoli
     decomposition; counting arguments behind docs
     [03/03](../docs/03_quantum_gates_and_circuits/03_circuit_model_and_universality.md). Feeds
     [project 2](../projects/project2_transpiler_pass.md) directly.
   - *Drill:* derivation drill on the two-qubit decompositions; rebuild the
     6-CNOT Toffoli construction on paper.

   <details><summary>Solution</summary>

   **Model answer.** The paper that makes "universal gate set" a concrete engineering
   statement.

   **Universality.** CNOT plus arbitrary single-qubit gates can implement any `n`-qubit
   unitary exactly. The proof is constructive and worth following: any `U ∈ U(2ⁿ)` is a
   product of **two-level unitaries** (Givens rotations, `O(4ⁿ)` of them); each two-level
   unitary is a **multiply-controlled single-qubit gate** via Gray-code conjugation; and
   each of those decomposes into CNOTs and single-qubit gates. The resulting count is
   exponential — `O(n² 4ⁿ)` — and that is not a defect of the construction: a counting
   argument shows almost all unitaries need `Ω(4ⁿ)` gates, because `4ⁿ` real parameters
   cannot be covered by fewer.

   **The standard Toffoli decomposition, on paper.** `CCX = H₂ · CCZ · H₂`, and `CCZ`
   expands as `±π/4` `Z`-rotations on each qubit, each pair, and the triple. Sharing the
   CNOT ladders gives the canonical circuit:

   ```
   H(2); CX(1,2) T†(2); CX(0,2) T(2); CX(1,2) T†(2); CX(0,2) T(1) T(2); H(2);
   CX(0,1) T(0) T†(1); CX(0,1)
   ```

   **6 CNOTs, 7 T gates, 2 Hadamards, T-depth 3** — verified exactly equal to `CCX`
   (not merely equal up to global phase, which matters if you ever control it). Six
   CNOTs is optimal without ancillas; with one clean ancilla you can trade down.

   **Related counts from the same paper worth memorising.** A controlled-`U` for
   arbitrary single-qubit `U` costs 2 CNOTs; a generic two-qubit unitary costs 3 CNOTs
   (the KAK bound); an `n`-controlled Toffoli costs `O(n)` Toffolis with `n−2` clean
   ancillas, or `O(n²)` without.

   **Why project 2 needs it.** A transpiler pass is exactly an implementation of these
   identities, and the paper is where the identity list comes from.

   </details>

3. **Dawson & Nielsen (2005)**, *"The Solovay-Kitaev Algorithm"*,
   arXiv:quant-ph/0505030. — ★★
   - *Get:* how *any* gate is approximated from a finite set with
     polylog(1/ε) overhead — the theorem that makes "universal gate set" a
     useful phrase; algorithmic, very readable.
   - *Drill:* conceptual + one derivation round on the recursion and its
     ε-scaling.

   <details><summary>Solution</summary>

   **Model answer.** Solovay–Kitaev is what makes a *finite* gate set as good as a
   continuous one, and Dawson–Nielsen is the readable, algorithmic account.

   **The theorem.** Let `G` be a finite set of gates in `SU(2)` that is closed under
   inverse and generates a dense subgroup. Then any `U ∈ SU(2)` can be approximated to
   operator-norm error `ε` by a sequence of `O(log^c(1/ε))` gates from `G`, and the
   sequence is *found* in `O(log^(2.71)(1/ε))` time. The original analysis gives
   `c ≈ 3.97`; modern variants (Ross–Selinger for the specific Clifford+T case, using
   number theory rather than the generic recursion) reach `c ≈ 1`, with `3 log₂(1/ε)`
   T gates.

   **The recursion, which is the whole algorithm.** Suppose `Approx(U, n−1)` returns a
   sequence within `ε_(n−1)`. To get level `n`:

   1. Compute `Δ = U · Approx(U, n−1)†`, which is close to the identity.
   2. Write `Δ` as a **group commutator** `Δ = V W V† W†` with `V, W` themselves close
      to the identity — possible because, near `I`, the commutator map is
      "quadratically contracting": if `Δ` is `δ` from `I`, then `V` and `W` need only be
      `O(√δ)` from `I`.
   3. Recursively approximate `V` and `W` at level `n−1` and concatenate.

   **The ε-scaling derivation the drill wants.** Errors compose additively over the four
   factors, so `ε_n ≤ C ε_(n−1)^(3/2)`. Writing `x_n = C² ε_n` gives
   `x_n ≤ x_(n−1)^(3/2)`, so `ε_n` shrinks doubly exponentially in `n`, i.e.
   `n = O(log log(1/ε))` levels suffice. Each level multiplies the sequence length by 5,
   so length `= 5^n = O(log^(log 5 / log(3/2))(1/ε)) = O(log^(3.97)(1/ε))`.

   **Where it matters and where it does not.** It matters in fault-tolerant compilation,
   where only Clifford+T is available and `RZ(θ)` must be synthesised. It does *not*
   matter on NISQ hardware, where `RZ` is a free frame change and `SX` is calibrated —
   which is why lesson 10's basis translation never invokes it.

   </details>

4. **Raussendorf & Briegel (2001)**, *"A One-Way Quantum Computer"*, Physical
   Review Letters 86, 5188. — ★★★
   - *Get:* computation by measurement on a cluster state — the model behind
     docs [03/05](../docs/03_quantum_gates_and_circuits/05_measurement_based_qc.md); understand
     teleportation-driven gates and feed-forward.
   - *Drill:* conceptual; then derive the 1-qubit teleportation identity that
     powers the scheme.

   <details><summary>Solution</summary>

   **Model answer.** Computation with no unitary gates at all — just a fixed entangled
   resource and adaptive single-qubit measurements.

   **The resource.** A **cluster state**: prepare every qubit of a 2-D lattice in `|+⟩`
   and apply `CZ` on every edge. It is a stabilizer state with generators
   `K_a = X_a Π_(b ∈ N(a)) Z_b`, and it is *universal* — a large enough cluster plus
   measurements can simulate any circuit.

   **The mechanism: teleportation-driven gates.** The one-qubit identity that powers
   everything is single-qubit teleportation through one cluster bond. Take
   `|ψ⟩ = α|0⟩+β|1⟩` on qubit 1, `|+⟩` on qubit 2, apply `CZ`, then measure qubit 1 in
   the basis `|±_φ⟩ = (|0⟩ ± e^(iφ)|1⟩)/√2`. Qubit 2 is left in

   ```
   X^m H RZ(φ) |ψ⟩        where m ∈ {0,1} is the measurement outcome
   ```

   Derive that once and the whole scheme follows: chaining `k` such measurements along a
   wire applies `H RZ(φ_k) … H RZ(φ_1)`, which generates all of `SU(2)`; a vertical bond
   between two wires supplies the `CZ` that makes it universal.

   **Feed-forward.** The `X^m` (and the `Z` byproducts from vertical bonds) are random,
   so later measurement angles must be *adapted* — `φ → (−1)^m φ` — using earlier
   outcomes. This is why the model needs classical feed-forward and why the
   **temporal order** of measurements matters even though the resource state is prepared
   all at once. Byproduct operators that are Clifford can be propagated to the end and
   absorbed into the readout; only the non-Clifford angles need real-time adaptation.

   **Why anyone cares.** It decouples entanglement generation (offline, probabilistic,
   heralded) from computation (deterministic, local measurements) — which is exactly
   what linear optics needs, and it is the model behind photonic architectures and
   fusion-based quantum computing. It also makes the resource-theory question crisp:
   what makes a state a universal resource?

   </details>

### Chapter 04 — Quantum Algorithms ([docs/04](../docs/04_quantum_algorithms/))

Core: **Deutsch–Jozsa**, **Shor**, **Grover** — classics ladder #4–6
(BBHT unknown-M search rides with the Grover entry).

1. **Kitaev (1995)**, *"Quantum measurements and the Abelian Stabilizer
   Problem"*, arXiv:quant-ph/9511026. — ★★★
   - *Get:* phase estimation in its original form; how the abelian
     hidden-subgroup view unifies Shor-type algorithms (lesson
     [03](03-representation-theory.md)'s payoff). Pairs with docs
     [04/04](../docs/04_quantum_algorithms/04_quantum_phase_estimation.md).
   - *Drill:* drill the modern QPE from docs first, then this paper's framing;
     derivation round on precision vs. ancilla count.

   <details><summary>Solution</summary>

   **Model answer.** Phase estimation before it was called phase estimation, and the
   frame that explains why Shor, Simon and Deutsch–Jozsa are the same algorithm.

   **The abelian stabilizer problem.** Given a group `G` acting on a set `X` and an
   element `x ∈ X`, find the stabilizer `St_G(x) = {g : g·x = x}`, a subgroup of `G`.
   Factoring is the instance `G = Z`, action `k · y = a^k y mod N`, `x = 1`: the
   stabilizer is `rZ`, so finding it *is* order finding. Discrete log, Simon's problem
   and Deutsch–Jozsa are all instances of the same **hidden subgroup problem** over
   abelian groups.

   **Why abelian is the special case.** The irreducible representations of a finite
   abelian group are all one-dimensional and form the dual group `Ĝ ≅ G`; the Fourier
   transform over `G` therefore maps a coset-uniform state to a state supported on the
   subgroup's *annihilator*, and sampling it a few times generates the answer. That is
   the representation-theory payoff lesson 03 builds toward. For non-abelian `G` the
   irreps are higher-dimensional and the analogous sampling does not determine the
   subgroup — which is why graph isomorphism (symmetric group) and lattice problems
   (dihedral group) remain open.

   **Kitaev's method versus textbook QPE.** Kitaev does not build a full inverse QFT.
   He estimates each bit of the phase with a separate Hadamard-test-style measurement on
   a *single* ancilla, repeated to suppress error, and reconstructs the phase
   classically. That is the ancestor of **iterative** / **semiclassical** QPE, which
   needs one ancilla instead of `t` — the trick Beauregard later used to bring Shor's
   qubit count down to `2n + 3`.

   **Precision versus ancilla count, the derivation.** With `t` ancillas, textbook QPE
   returns the best `t`-bit approximation with probability `≥ 4/π² ≈ 0.405`, and to get
   `n` bits correct with failure probability `≤ δ` you need
   `t = n + ⌈log₂(2 + 1/(2δ))⌉`. Verified at `t = 3`: a phase of `1/8` is returned with
   probability exactly 1, while `φ = 0.3` peaks on `2/8` with probability `0.578` and
   `3/8` with `0.259`.

   </details>

2. **Bennett & Brassard (1984)**, *"Quantum cryptography: Public key
   distribution and coin tossing"*, Proc. IEEE Int. Conf. on Computers,
   Systems and Signal Processing, Bangalore, 175. — ★
   - *Get:* the BB84 protocol from the source — it's short and concrete;
     exactly what [project 4](../projects/project4_bb84.md) implements.
   - *Drill:* closed-book protocol walkthrough: state the four states, the
     sifting rule, and the intercept-resend QBER of 25%.

   <details><summary>Solution</summary>

   **Model answer — the protocol walkthrough, closed-book.**

   **The four states.** Two conjugate bases, two states each:

   ```
   rectilinear (+)  :  |0⟩  -> bit 0        |1⟩  -> bit 1
   diagonal    (×)  :  |+⟩  -> bit 0        |−⟩  -> bit 1
   ```

   Any state in one basis is an equal superposition in the other, so a measurement in
   the wrong basis is a fair coin. No-cloning forbids Eve copying, and the conjugate
   encoding forbids her learning without disturbing.

   **The protocol.**

   1. Alice picks a random bit and a random basis for each pulse, and sends the
      corresponding state.
   2. Bob picks a random basis for each arriving pulse and measures.
   3. **Sifting** (public, authenticated classical channel): they announce *bases only*,
      never bits, and keep the roughly 50% of positions where the bases agree.
   4. **Parameter estimation**: they reveal a random subset of the sifted bits and
      compute the quantum bit error rate.
   5. **Error correction** (information reconciliation) and **privacy amplification** (a
      two-universal hash shrinking the key to remove Eve's partial information).

   **Intercept–resend QBER = 25%, derived.** Eve measures each pulse in a random basis
   and resends what she saw. Condition on a *sifted* position, so Alice and Bob share a
   basis. With probability 1/2 Eve guessed that basis: no disturbance, no error. With
   probability 1/2 she guessed wrong: her resent state is unbiased in Alice and Bob's
   basis, so Bob errs with probability 1/2. Total

   ```
   QBER = (1/2)(0) + (1/2)(1/2) = 1/4
   ```

   A measured QBER above the protocol's threshold (about 11% for one-way
   reconciliation against general attacks) means abort.

   **What is short and concrete about the original.** BB84 is four pages, the protocol
   is stated in a paragraph, and it also contains the coin-tossing protocol nobody
   remembers. Security proofs came a decade later (Mayers, Shor–Preskill); the paper
   itself argues only against specific attacks — a distinction worth noticing.

   </details>

3. **Ekert (1991)**, *"Quantum cryptography based on Bell's theorem"*,
   Physical Review Letters 67, 661. — ★★
   - *Get:* entanglement-based QKD; security from a CHSH test rather than
     conjugate coding — ties chapters 02 and 04 together.
   - *Drill:* conceptual round contrasting E91's security argument with BB84's.

   <details><summary>Solution</summary>

   **Model answer — E91 versus BB84, contrasted.**

   **The protocol.** A source emits singlets; Alice and Bob each measure along one of
   three randomly chosen directions. Positions where they chose *compatible* directions
   give perfectly anticorrelated bits — the key. The *incompatible* positions are not
   discarded: they are used to evaluate a **CHSH (or Bell) sum**, and the observed
   value certifies security.

   **Where the security comes from — the contrast the drill asks for.**

   | | BB84 | E91 |
   |---|---|---|
   | resource | conjugate coding of single states | shared entanglement |
   | security argument | no-cloning: measuring disturbs | monogamy of entanglement: a maximal Bell violation forces Alice and Bob's state to be pure and hence *unentangled with Eve* |
   | test statistic | QBER on a revealed subset | `S` from the incompatible-basis subset |
   | what an eavesdropper costs you | raises the error rate | lowers `S` below `2√2` |
   | assumptions about devices | you must trust your state preparation and detectors | in the device-independent limit, you need not |

   **The deep point.** A CHSH value of `2√2` is achievable *only* by a maximally
   entangled pure state, and monogamy says a maximally entangled pair cannot be
   correlated with anything else. So the Bell violation itself — a directly measured
   number — bounds Eve's information, without any assumption about what is inside the
   boxes. That observation is the seed of **device-independent QKD**, made rigorous
   decades later (Barrett–Hardy–Kent, Acín et al., Vazirani–Vidick).

   **Practical honesty.** E91 is harder to implement (entangled sources, higher loss,
   and the detection loophole reappears as a security loophole rather than a
   philosophical one), so deployed QKD is overwhelmingly BB84-like. The equivalence
   result worth knowing is that entanglement-based and prepare-and-measure protocols are
   formally interchangeable — Shor–Preskill's security proof for BB84 proceeds by
   reducing it to an entanglement-based protocol.

   </details>

4. **Harrow, Hassidim & Lloyd (2009)**, *"Quantum Algorithm for Linear Systems
   of Equations"*, Physical Review Letters 103, 150502, arXiv:0811.3171. — ★★★
   - *Get:* the HHL pipeline (docs [04/07](../docs/04_quantum_algorithms/07_hhl_quantum_linear_systems.md));
     and — just as important — the fine print: state preparation, condition
     number, and output-access caveats.
   - *Drill:* factual round on the assumptions; conceptual on which caveat
     kills which proposed application.

   <details><summary>Solution</summary>

   **Model answer.** HHL is a genuine exponential speedup, hedged by four assumptions
   that between them kill most proposed applications.

   **The pipeline.** Given `A x = b` with `A` Hermitian (otherwise embed it),
   `s`-sparse, and condition number `κ`:

   1. Prepare `|b⟩ = Σ_j b_j |j⟩` (normalised).
   2. Run QPE with `e^(iAt)` to get `Σ_j β_j |λ_j⟩|u_j⟩` in the eigenbasis.
   3. Rotate an ancilla by `arcsin(C/λ_j)` conditioned on the eigenvalue register — the
      **inversion**, the only genuinely new step.
   4. Uncompute the QPE.
   5. Postselect the ancilla on `|1⟩`; the remaining register holds
      `|x⟩ ∝ Σ_j (β_j/λ_j)|u_j⟩ ∝ A^(-1)|b⟩`.

   Runtime `O(log(N) · s² κ² / ε)`, against `O(N s κ log(1/ε))` for classical conjugate
   gradient — exponential in `N`, polynomial in everything else. Amplitude amplification
   removes one factor of `κ`; later work (Childs–Kothari–Somma, then QSVT) improves the
   `1/ε` to `log(1/ε)`.

   **The four caveats, and which application each kills.**

   - **State preparation.** You must be able to build `|b⟩` in `O(polylog N)`. If `b`
     lives in classical memory, loading it costs `Ω(N)` and the speedup is gone. This
     kills any "solve my data-science linear system" proposal that lacks a QRAM or an
     efficiently computable `b`.
   - **Sparsity / block-encoding.** You need efficient access to `A`'s entries.
     Dense, unstructured `A` kills the speedup.
   - **Condition number.** `κ²` (or `κ` with amplification) in the runtime; ill-conditioned
     systems are hopeless, and preconditioning is not obviously quantum-friendly.
   - **Readout.** The output is a *quantum state*. Reading all `N` amplitudes costs
     `Ω(N)` samples. You only win if you want a single global summary such as
     `⟨x|M|x⟩`. This kills any application whose answer is the vector itself.

   **The dequantisation postscript.** Tang's classical sampling algorithms showed that
   when you *do* have the strong `ℓ²`-sampling access that QRAM assumes, classical
   algorithms with only polynomial overhead exist for several HHL-style problems. The
   honest summary: HHL's speedup is real in its own model, and the model is the hard
   part.

   </details>

### Chapter 05 — Quantum Error Correction ([docs/05](../docs/05_quantum_error_correction/))

Core: **Kitaev toric code**, **Panteleev–Kalachev**, **Bravyi et al.** —
classics ladder #9–11.

1. **Shor (1995)**, *"Scheme for reducing decoherence in quantum computer
   memory"*, Physical Review A 52, R2493. — ★★
   - *Get:* the 9-qubit code that proved QEC possible; how it beats the
     no-cloning objection (docs [05/01](../docs/05_quantum_error_correction/01_why_qec_is_hard.md)).
   - *Drill:* derivation: show the code corrects an arbitrary single-qubit
     error from just bit-flip + phase-flip correction.

   <details><summary>Solution</summary>

   **Model answer.** The paper that proved quantum error correction is possible at all.

   **The construction.** Concatenate two three-qubit repetition codes:

   ```
   phase-flip layer:  |0⟩ -> |+++⟩,  |1⟩ -> |−−−⟩
   bit-flip layer:    each |±⟩ -> (|000⟩ ± |111⟩)/√2
   giving            |0_L⟩ = [(|000⟩+|111⟩)/√2]^⊗3 / ... , 9 qubits in total
   ```

   Stabilizers: six weight-2 `Z`-type checks (`Z₁Z₂, Z₂Z₃` within each block, three
   blocks) detecting bit flips, and two weight-6 `X`-type checks
   (`X₁…X₆`, `X₄…X₉`) comparing the phases of neighbouring blocks. Eight independent
   generators on nine qubits leave `k = 1`; direct computation of the stabilizer
   projector confirms a two-dimensional codespace, and the distance is 3, so the code is
   `[[9,1,3]]`.

   **How it beats the no-cloning objection.** Classical repetition means *copying*,
   which is forbidden. The quantum version does not copy the state: it *spreads* one
   logical qubit across nine physical ones in an entangled way, so no single qubit
   carries any information about `α, β` (every single-qubit reduced state is maximally
   mixed). The syndrome measurements extract information about the **error** while
   learning nothing about the **state** — that is the whole trick, and it is why the
   checks are products of Paulis rather than measurements of individual qubits.

   **The derivation the drill wants: arbitrary single-qubit errors.** Any single-qubit
   operation `E` expands in the Pauli basis, `E = c_I I + c_X X + c_Y Y + c_Z Z`, and
   `Y = iXZ`. Applying `E` to the encoded state gives a superposition of the four
   correctable cases; measuring the syndrome **projects** onto one of them, and the
   correction for that syndrome undoes it exactly. So correcting `X` and `Z` on each
   qubit suffices to correct *every* single-qubit error, including small coherent
   rotations and amplitude damping — the **discretisation of errors**, which is the
   single most important idea in the paper.

   </details>

2. **Steane (1996)**, *"Error Correcting Codes in Quantum Theory"*, Physical
   Review Letters 77, 793. — ★★
   - *Get:* the CSS insight — classical Hamming codes used twice; the
     [[7,1,3]] code of [project 3](../projects/project3_steane_simulator.md).
   - *Drill:* drill after docs [05/05](../docs/05_quantum_error_correction/05_css_codes_and_steane.md);
     closed-book, write the six stabilizer generators.

   <details><summary>Solution</summary>

   **Model answer.** The CSS insight: one good classical code, used twice.

   **The construction.** Take the classical `[7,4,3]` Hamming code with parity-check
   matrix `H` whose columns are the binary numbers 1 to 7. Because Hamming is weakly
   self-dual (`C^⊥ ⊆ C`), you may use `H` for `X`-type checks and the *same* `H` for
   `Z`-type checks, and the CSS condition `H_X H_Z^T = 0` holds automatically. The result
   is the `[[7,1,3]]` Steane code.

   **The six stabilizer generators, closed-book:**

   ```
   g1 = I I I X X X X        g4 = I I I Z Z Z Z
   g2 = I X X I I X X        g5 = I Z Z I I Z Z
   g3 = X I X I X I X        g6 = Z I Z I Z I Z
   ```

   Verified: all six commute pairwise, and the stabilizer projector has trace 2, so the
   codespace is two-dimensional — one logical qubit in seven, distance 3.

   **Why it is nicer than Shor's nine-qubit code.** Fewer qubits, and far better gate
   properties: because the `X` and `Z` checks are identical, the entire Clifford group is
   **transversal** — `X̄ = X^⊗7`, `Z̄ = Z^⊗7`, `H̄ = H^⊗7` (it swaps the `X` and `Z`
   generator sets, which are identical patterns here), a transversal phase gate giving
   logical `S` up to the `S`/`S†` convention, and logical CNOT as seven physical CNOTs
   between two blocks. Transversal gates cannot spread a
   single error into two within a block, so they are automatically fault-tolerant. `T` is
   *not* transversal (Eastin–Knill guarantees something must be missing), which is why
   magic-state distillation exists.

   **The general CSS recipe to carry away.** Given classical codes `C₂ ⊂ C₁` with `C₁`
   `[n,k₁,d₁]` and `C₂` `[n,k₂,d₂]`, the CSS code is `[[n, k₁−k₂, ≥ min(d₁, d₂^⊥)]]`.
   Steane is `C₁ = C₂^⊥ = ` Hamming. Everything in docs `05/05` is this construction, and
   project 3 builds the decoder.

   </details>

3. **Gottesman (1997)**, *"Stabilizer Codes and Quantum Error Correction"*,
   PhD thesis, Caltech, arXiv:quant-ph/9705052. — ★★★
   - *Get:* the stabilizer formalism as a *language* (docs
     [05/04](../docs/05_quantum_error_correction/04_stabilizer_formalism.md)); read chapters 2–4, keep
     the rest as reference; the `qec-trainer` app drills the same machinery.
   - *Drill:* one thesis chapter per session; derivation questions on
     symplectic representation and the error-correction conditions.

   <details><summary>Solution</summary>

   **Model answer.** The thesis that turns error correction from a collection of clever
   codes into a *language*.

   **Chapters 2–4, the part to actually read.**

   **The stabilizer group.** A code is specified by an abelian subgroup `S ⊆ P_n` of the
   `n`-qubit Pauli group with `−I ∉ S`. The codespace is the joint `+1` eigenspace.
   `n − k` independent generators encode `k` logical qubits. Everything — encoding,
   syndromes, logical operators, distance — is read off the group instead of the
   `2ⁿ`-dimensional state.

   **Symplectic (binary) representation.** Map each Pauli to a `2n`-bit vector
   `(a | b)` meaning `Π X_i^(a_i) Z_i^(b_i)`, ignoring phase. Then multiplication is
   addition mod 2, and — the key point — two Paulis **commute iff their symplectic
   inner product vanishes**:

   ```
   ⟨(a|b), (a'|b')⟩ = a · b' + b · a'  (mod 2)  = 0
   ```

   So a stabilizer code is a *self-orthogonal binary code* under that form, and the
   entire theory of classical linear codes becomes available. This is why the
   `qec-trainer` app can represent everything as `GF(2)` matrices.

   **The error-correction conditions.** Knill–Laflamme says a code with projector `P`
   corrects an error set `{E_a}` iff `P E_a† E_b P = c_(ab) P`. For stabilizer codes this
   collapses to something checkable by hand: the code corrects `{E_a}` iff for every
   pair, `E_a† E_b` is **either in `S` (harmless — a stabilizer acts trivially) or
   anticommutes with some generator (detectable — it flips a syndrome bit)**. The
   failure case is exactly `E_a† E_b ∈ N(S) \ S`, the *undetectable logical errors*. The
   distance is the minimum weight of an element of `N(S) \ S`.

   **Logical operators.** `N(S)/S` is the logical Pauli group. Finding a symplectic basis
   for it — `2k` operators with the right commutation pattern — is how you name `X̄_i`
   and `Z̄_i`.

   **Reading strategy.** One chapter per session, and do the derivations: the symplectic
   form, the syndrome map, and the distance definition. Keep the rest (fault tolerance,
   the classification of small codes) as reference.

   </details>

4. **Fowler, Mariantoni, Martinis & Cleland (2012)**, *"Surface codes: Towards
   practical large-scale quantum computation"*, Physical Review A 86, 032324,
   arXiv:1208.0928. — ★★
   - *Get:* the tutorial-style bridge from toric code to practical surface
     code: syndrome cycles, braiding-era logic, threshold ~1%. Pairs with docs
     [05/06](../docs/05_quantum_error_correction/06_surface_code.md)–[07](../docs/05_quantum_error_correction/07_fault_tolerance.md).
   - *Drill:* section-by-section; factual on the error budget tables,
     derivation on the distance-vs-logical-rate scaling.

   <details><summary>Solution</summary>

   **Model answer.** The paper that made the surface code an engineering plan rather than
   a topology result.

   **The code.** Kitaev's toric code cut open onto a planar patch with boundaries: data
   qubits on edges, measure-`X` and measure-`Z` ancillas alternating on a checkerboard,
   every check weight 4 and strictly nearest-neighbour. A distance-`d` patch costs about
   `2d²` physical qubits for one logical qubit.

   **The syndrome cycle.** One round is: prepare each ancilla, four CNOTs to its
   neighbouring data qubits **in a fixed order** (the order matters — a bad order lets a
   single ancilla fault produce a weight-2 data error that the code cannot handle),
   measure, reset. This repeats forever; the logical qubit's state is never measured,
   only the checks. Because the measurements are themselves faulty, you repeat for
   `O(d)` rounds and decode in **2+1 dimensions** (space × time), matching syndrome
   *changes* rather than syndrome values.

   **Threshold and scaling — the derivation the drill wants.** Below a threshold physical
   error rate `p_th`, the logical error rate per round falls as

   ```
   p_L ≈ A (p / p_th)^(⌊(d+1)/2⌋)
   ```

   because the smallest uncorrectable error chain has weight `⌈d/2⌉`, and the number of
   such chains grows only polynomially while their probability falls as `p^(d/2)`. The
   paper's headline number is `p_th ≈ 1%` under a circuit-level depolarising model with
   minimum-weight perfect matching decoding — *the* number that made superconducting
   hardware a plausible target, since `10⁻³` gates are an order of magnitude below it.
   The cost is that suppressing `p_L` by a factor of ten needs `d` to grow by about 2,
   and qubits go as `d²`.

   **Braiding-era logic.** The paper's computation model creates logical qubits as pairs
   of holes (deactivated stabilizers) and performs CNOT by braiding one hole around
   another — an appealing picture that the field has since largely replaced with
   **lattice surgery** (merging and splitting patches), which is cheaper in qubits. Read
   the braiding sections for intuition, not as current practice.

   **The error budget tables.** Their real value is the accounting: how many physical
   qubits and how many surface-code cycles a useful algorithm needs. That accounting is
   the direct ancestor of the Gidney–Ekerå RSA-2048 estimate.

   </details>

### Chapter 06 — Variational Quantum Algorithms ([docs/06](../docs/06_variational_quantum_algorithms/))

Core: **Peruzzo (VQE)**, **Farhi (QAOA)** — classics ladder #12–13.

1. **O'Malley et al. (2016)**, *"Scalable Quantum Simulation of Molecular
   Energies"*, Physical Review X 6, 031007. — ★★
   - *Get:* VQE done carefully on hardware for H₂ — including the tabulated
     bond-distance Hamiltonian coefficients that
     [project 1](../projects/project1_vqe_h2.md) milestone 1 uses.
   - *Drill:* factual on the experimental pipeline; then reproduce their
     dissociation curve in project 1 — the project *is* the drill.

   <details><summary>Solution</summary>

   **Model answer.** VQE done carefully enough on hardware to be reproducible — the
   paper that sets project 1's target.

   **The experimental pipeline, step by step.**

   1. **Classical pre-processing.** Compute the H₂ electronic Hamiltonian in the STO-3G
      minimal basis at each bond distance `R`, map it to qubits with Jordan–Wigner (four
      spin orbitals, four qubits), then use the `Z₂` symmetries of the problem to taper
      down to **two qubits**, giving a Hamiltonian of the form
      `g₀I + g₁Z₀ + g₂Z₁ + g₃Z₀Z₁ + g₄Y₀Y₁ + g₅X₀X₁` with tabulated `g_i(R)`.
   2. **Ansatz.** The unitary coupled-cluster single excitation `exp(−iθ X₀Y₁)`, which
      for this problem is *exact* — one parameter, so the optimisation landscape is a
      1-D curve you can plot.
   3. **Measurement.** Each Pauli term in its own basis, with the `ZZ` terms sharing one
      setting; sum with the tabulated coefficients.
   4. **Optimisation.** Nelder–Mead on the hardware, plus a full sweep of `θ` as a
      sanity check.
   5. **Comparison.** The same energies computed by iterative QPE on the same device —
      which fails at chemical accuracy because the circuit is far deeper, and that
      contrast is the paper's real argument for VQE.

   **What to extract for project 1.** The tabulated `g_i(R)` at each bond distance are
   milestone 1's input. Independently, you can generate them yourself: computing the
   STO-3G integrals from the three-Gaussian contraction, forming the symmetry-fixed MOs,
   and diagonalising the full CI matrix gives `E₀ = −1.1373072 Ha` at `R = 0.735 Å` —
   the textbook value, and the number your VQE must reproduce to within
   `1.6 × 10⁻³ Ha`.

   **The honest reading.** Two qubits and one parameter is a demonstration, not a
   computation — the classical answer was known exactly. What the paper establishes is
   that the *error behaviour* is favourable: VQE's variational bound makes energies
   robust to coherent control error in a way QPE's phase is not, and the measured curve
   tracks the exact one even on a noisy device.

   </details>

2. **Kandala et al. (2017)**, *"Hardware-efficient variational quantum
   eigensolver for small molecules and quantum magnets"*, Nature 549, 242,
   arXiv:1704.05018. — ★★
   - *Get:* the "hardware-efficient ansatz" idea and its costs; error
     mitigation entering the VQE story. Pairs with docs
     [06/02](../docs/06_variational_quantum_algorithms/02_ansatz_design.md).
   - *Drill:* conceptual: chemically-motivated vs hardware-efficient ansätze —
     argue both sides.

   <details><summary>Solution</summary>

   **Model answer.** The hardware-efficient ansatz, and the argument for and against it.

   **The idea.** Stop asking chemistry what the ansatz should be. Instead, build the
   deepest circuit the device can actually run: alternating layers of arbitrary
   single-qubit rotations (`R_z R_x R_z` per qubit) and the device's **native**
   entangler applied along its **native** coupling map, repeated `d` times. No
   Trotterisation of excitation operators, no long `Z`-strings from Jordan–Wigner, no
   SWAP networks. The paper uses it for H₂, LiH and BeH₂ (six qubits) and for a
   Heisenberg spin model.

   **The case for.**

   - Circuit depth is set by the hardware, so every gate you spend is a gate the device
     can execute at its best fidelity. A UCCSD circuit for BeH₂ on the same device would
     be orders of magnitude deeper and return noise.
   - It is universal enough in practice: with enough layers the ansatz covers the
     relevant subspace.
   - It generalises across problem domains — the same circuit shape does chemistry and
     magnetism.

   **The case against.**

   - It does not respect the problem's symmetries (particle number, spin, point group),
     so the optimiser wanders into unphysical states and wastes parameters. Chemically
     motivated ansätze stay in the correct sector by construction.
   - Its very expressibility is the problem: a random deep hardware-efficient circuit
     approximates a 2-design, which is exactly the barren-plateau condition of the next
     paper. **Expressibility and trainability trade against each other.**
   - No convergence guarantee and no systematic improvement path — adding a layer is not
     like adding an excitation order.

   **The other contribution.** This is where error mitigation enters the VQE story in
   earnest: Richardson/zero-noise extrapolation applied to the measured energies, and
   careful readout calibration. The mitigated BeH₂ curve is visibly better than the raw
   one, and that technique is now `resilience_level=2` in `EstimatorV2`.

   **How to argue both sides in the drill.** Frame it as a resource question: chemically
   motivated ansätze spend *coherence* to buy structure; hardware-efficient ansätze
   spend *optimisation difficulty* to buy shallowness. Which is right depends entirely on
   which resource is scarcer on your device.

   </details>

3. **McClean et al. (2018)**, *"Barren plateaus in quantum neural network
   training landscapes"*, Nature Communications 9, 4812, arXiv:1803.11173. — ★★
   - *Get:* why random deep ansätze have exponentially vanishing gradients
     (docs [06/05](../docs/06_variational_quantum_algorithms/05_barren_plateaus.md)); the
     concentration-of-measure argument in outline.
   - *Drill:* derivation-lite: state the variance scaling and what assumptions
     produce it; then run project 1's stretch-goal gradient-variance probe.

   <details><summary>Solution</summary>

   **Model answer.** Deep random ansätze are untrainable, and the reason is
   concentration of measure, not a bad optimiser.

   **The result, stated precisely.** For a parameterised circuit `U(θ)` that forms a
   **2-design** over the unitary group (which random hardware-efficient circuits
   approach as depth grows past `O(poly(n))`), and a cost `E(θ) = ⟨0|U†(θ) H U(θ)|0⟩`:

   ```
   E[∂_k E] = 0      and      Var[∂_k E] ∈ O(2^(-n))  (exponentially small in n)
   ```

   Both the gradient and its variance vanish exponentially, so by Chebyshev the gradient
   is exponentially small with overwhelming probability. Not a bad initialisation — a
   *bad landscape*: the cost is essentially flat almost everywhere, with a narrow
   gorge around the minimum.

   **The concentration argument in outline.** The first moment is zero by the left/right
   invariance of Haar measure (the Pauli-weighted average of `U†HU` over the unitary
   group is proportional to the identity, whose derivative vanishes). The second moment
   needs only the *second* moment of Haar measure — hence "2-design" — and the
   Weingarten calculus gives a factor of `1/(2²ⁿ − 1)` from the dimension. Physically:
   in an exponentially large space, a randomly chosen direction has exponentially small
   overlap with any fixed one.

   **Assumptions that produce it, and therefore the escapes.** The result needs (i) deep
   enough circuits to be a 2-design, (ii) a *global* cost function (an observable
   supported on all `n` qubits), and (iii) random initialisation. Each is a lever:

   - **Shallow, local ansätze** with `O(log n)` depth and *local* cost functions have
     gradients vanishing only polynomially (Cerezo et al.).
   - **Structured initialisation** — identity blocks, layerwise growth, or
     physics-motivated starting points — starts you inside the gorge.
   - **Symmetry-preserving ansätze** restrict to a small sector where the dimension
     factor is not `2ⁿ`.
   - Noise creates its own, worse, "noise-induced barren plateau" that none of these
     fix.

   **The project-1 stretch goal.** Sample random parameter vectors for ansätze of
   increasing width and depth, estimate `∂E/∂θ_k` with the parameter-shift rule, and
   plot `Var[∂_k E]` against `n` on a log axis. A straight line with slope about `−1`
   per qubit is the barren plateau appearing in your own data.

   </details>

4. **Cerezo et al. (2021)**, *"Variational quantum algorithms"*, Nature
   Reviews Physics 3, 625, arXiv:2012.09265. — ★★
   - *Get:* the field map — read *last*, as consolidation; it organizes
     everything docs chapter 06 covers.
   - *Drill:* factual sweep, one section per session; perfect closed-book
     material for the `vqa-trainer` app in parallel.

   <details><summary>Solution</summary>

   **Model answer.** Read this *last*, as consolidation — it is the field map, and its
   value is that it organises what you already know.

   **The common skeleton every VQA shares.** (1) a cost function encoding the problem,
   (2) an ansatz with trainable parameters, (3) a gradient or gradient-free optimiser,
   (4) a measurement strategy, (5) a hybrid loop. Once you see that VQE, QAOA,
   variational quantum classifiers, quantum autoencoders, variational error correction
   and quantum-state diagonalisation are all the same five boxes with different
   contents, the literature stops looking like a pile of unrelated acronyms.

   **The four cross-cutting problems the review organises everything around.**

   - **Trainability** — barren plateaus (from expressibility, from global cost
     functions, from entanglement, and from noise), and the mitigations for each.
   - **Expressibility** — can the ansatz reach the answer, measured against Haar-random
     states; and the fundamental tension with trainability.
   - **Accuracy under noise** — error mitigation (ZNE, probabilistic error cancellation,
     symmetry verification) versus correction.
   - **Efficiency** — measurement cost, which is the usually-underestimated bottleneck:
     `O(1/ε²)` shots per Pauli term, times thousands of terms, times every optimiser
     iteration. Grouping into commuting cliques and classical shadows are the standard
     answers.

   **Gradients.** The parameter-shift rule gives *exact* analytic gradients on hardware
   for gates of the form `e^(−iθP/2)` with `P² = I`:
   `∂_θ⟨H⟩ = [⟨H⟩_(θ+π/2) − ⟨H⟩_(θ−π/2)]/2`. Know that it is exact, not a finite
   difference, and that it costs two circuit evaluations per parameter.

   **The honest bottom line the review states and you should repeat.** No variational
   algorithm has a proof of quantum advantage. The case for them is that they fit
   current hardware, and the open question is whether that is enough.

   **How to drill it.** One section per session, factual sweep, with `vqa-trainer` open
   in parallel — it is exactly this taxonomy in flashcard form.

   </details>

### Chapter 07 — Quantum Hardware ([docs/07](../docs/07_quantum_hardware/))

Core: **Preskill NISQ**, **Arute et al.** — classics ladder #7–8.

1. **Cirac & Zoller (1995)**, *"Quantum Computations with Cold Trapped Ions"*,
   Physical Review Letters 74, 4091. — ★★
   - *Get:* the first concrete gate proposal on real physics: shared motional
     modes as the qubit bus (docs [07/02](../docs/07_quantum_hardware/02_trapped_ion_qubits.md)).
   - *Drill:* conceptual on why the phonon bus gives all-to-all connectivity
     and what limits gate speed.

   <details><summary>Solution</summary>

   **Model answer.** The first gate proposal grounded in a real, buildable physical
   system.

   **The architecture.** Ions in a linear Paul trap, Coulomb-repelled into a chain.
   Each ion's *internal* electronic states are the qubit; the chain's *collective*
   vibrational modes (phonons) are a shared bus. Lasers addressed at individual ions
   drive transitions on the **red sideband**, which couples the internal state to the
   centre-of-mass phonon mode:

   ```
   |g⟩|n⟩  <->  |e⟩|n−1⟩
   ```

   **The CNOT.** Start with the bus cooled to `|n = 0⟩`. A red-sideband `π` pulse on the
   control ion writes its internal state into the phonon mode. A `2π` pulse on the
   target ion, routed through an **auxiliary internal level**, imprints a `−1` phase
   conditional on the phonon being present. A final `π` pulse on the control returns the
   phonon state to the ion. Net effect: a controlled-phase, hence (with Hadamards) a
   CNOT — between *any* two ions in the chain, because the bus is shared.

   **Why it gives all-to-all connectivity.** The phonon mode is a property of the whole
   chain, not of a neighbouring pair. Any ion can write to it and any ion can read from
   it, so the "coupling map" is complete — the single biggest architectural advantage
   over superconducting chips, where routing SWAPs dominate (lesson 10).

   **What limits gate speed — the drill's second question.** The sideband Rabi frequency
   is suppressed by the Lamb–Dicke parameter `η ≈ k x₀ ≪ 1`, so sideband transitions are
   intrinsically slow: microseconds to milliseconds, against nanoseconds for
   superconducting gates. Driving faster excites the *other* motional modes (spectral
   crowding, which worsens as the chain lengthens) and leaves the Lamb–Dicke regime.
   Add the need for ground-state cooling before every gate, and motional heating from
   trap-electrode noise, and the trade is clear: ions win on fidelity, coherence time
   and connectivity; they lose on clock speed and, so far, on scaling a single chain
   past a few tens of ions.

   **What came after.** Mølmer–Sørensen gates removed the requirement for a
   ground-state-cooled bus and are what modern trapped-ion machines actually run — but
   the shared-mode idea is unchanged.

   </details>

2. **Koch et al. (2007)**, *"Charge-insensitive qubit design derived from the
   Cooper pair box"*, Physical Review A 76, 042319, arXiv:cond-mat/0703002. — ★★★
   - *Get:* the transmon: why running E_J/E_C large exponentially suppresses
     charge noise at only polynomial cost in anharmonicity — the trade that
     powers every IBM device you used in the [labs](../labs/).
   - *Drill:* skip the heavy appendices; derivation round on the
     charge-dispersion vs anharmonicity scaling.

   <details><summary>Solution</summary>

   **Model answer.** One dimensionless ratio, traded exponentially against
   polynomially — the design decision behind every IBM device you use in the labs.

   **The circuit.** A Cooper-pair box is a Josephson junction (energy `E_J`) shunted by a
   capacitance (charging energy `E_C = e²/2C`). Its Hamiltonian is

   ```
   H = 4E_C (n̂ − n_g)² − E_J cos φ̂
   ```

   a particle in a cosine potential, where `n_g` is the *offset charge* set by the
   uncontrolled electrostatic environment. Charge noise means `n_g` drifts, and in the
   `E_J ≪ E_C` regime the level spacings depend strongly on `n_g` — the dephasing
   mechanism that limited Cooper-pair boxes to nanosecond coherence.

   **The transmon move.** Shunt the junction with a large capacitor so that
   `E_J/E_C ≫ 1` (typically 50–100). Then:

   - **Charge dispersion** — the peak-to-peak variation of level `m` with `n_g` — falls
     **exponentially**:

     ```
     ε_m ∝ exp(−√(8 E_J/E_C))
     ```

     Sensitivity to the dominant noise source is suppressed by orders of magnitude for a
     modest change of ratio.
   - **Anharmonicity** — the price — falls only **algebraically**. Deep in the transmon
     regime the cosine is nearly harmonic, and

     ```
     α = ω₁₂ − ω₀₁ ≈ −E_C,     relative anharmonicity α/ω₀₁ ∝ (E_J/E_C)^(−1/2)
     ```

   **The trade, in one sentence.** An exponential gain in charge-noise immunity costs
   only a square-root loss in anharmonicity — so you push `E_J/E_C` as high as you dare,
   stopping when the anharmonicity (typically `−200` to `−300` MHz) becomes small enough
   that fast pulses start leaking population into `|2⟩`. That leakage limit is why gate
   times are tens of nanoseconds rather than a few, and why DRAG pulse shaping exists.

   **Reading strategy.** The derivation via Mathieu functions in the appendices is heavy
   and skippable on a first pass; the asymptotic formulas above and Figure 2's plots of
   charge dispersion and anharmonicity versus `E_J/E_C` carry the argument. Then look at
   `FakeTorino`'s target: the `T₁`, `T₂` and anharmonicity numbers you find there are
   this trade-off made concrete.

   </details>

3. **Krantz et al. (2019)**, *"A Quantum Engineer's Guide to Superconducting
   Qubits"*, Applied Physics Reviews 6, 021318, arXiv:1904.06560. — ★★
   - *Get:* the working reference for docs [07/01](../docs/07_quantum_hardware/01_superconducting_qubits.md):
     gates, readout, T1/T2 characterization — read it with your lab 3
     calibration data open.
   - *Drill:* section-by-section factual; then re-answer the questions using
     numbers you pull from `FakeTorino`'s target (lab 3).

   <details><summary>Solution</summary>

   **Model answer.** This is the working reference, not an argument — read it with
   device data open and answer its questions with real numbers.

   **The five things it covers that you need.**

   1. **Qubit design.** Transmon, its circuit quantisation, and the modern variants
      (tunable transmon with a SQUID loop, C-shunt flux qubit, fluxonium) with the
      coherence/anharmonicity trade for each.
   2. **Single-qubit gates.** Resonant microwave drives, the rotating frame, `RZ` as a
      *virtual* frame update (zero duration, zero error — which is exactly why the IBM
      basis is `{RZ, SX, X}`), and **DRAG** pulse shaping to suppress leakage into `|2⟩`.
   3. **Two-qubit gates.** Cross-resonance (drive the control at the target's frequency
      — the Eagle `ECR`), tunable-coupler `CZ` via the `|11⟩ ↔ |02⟩` avoided crossing
      (Heron), and the `iSWAP` family. Knowing which family a device uses tells you what
      its native two-qubit gate is, and therefore what the transpiler must emit.
   4. **Readout.** Dispersive coupling to a resonator, `χ` shift, Purcell filters,
      and why readout is both the slowest operation and often the largest single error.
   5. **Characterisation.** `T₁` (energy relaxation, inversion recovery), `T₂*`
      (Ramsey, includes low-frequency dephasing), `T₂` echo (Hahn), randomised
      benchmarking for average gate error, and interleaved RB for a specific gate.

   **The exercise that makes it stick.** Re-answer the guide's questions using
   `FakeTorino`'s target: pull `t1`, `t2` and `frequency` from
   `target.qubit_properties[q]`, and `error`/`duration` from `target['cz'][(i,j)]` and
   `target['measure'][(q,)]`. Then check the consistency relations the guide gives —
   `T₂ ≤ 2T₁`, and gate error roughly `≳ t_gate/T₂` as a coherence floor. Where a device
   is far above that floor, the error is control or crosstalk, not decoherence, and that
   distinction is what lab 3's calibration data is for.

   **How to drill.** Section by section, factual. Any question you can answer from the
   device target rather than from memory is a question you now understand.

   </details>

4. **Cross et al. (2019)**, *"Validating quantum computers using randomized
   model circuits"*, Physical Review A 100, 032328, arXiv:1811.12926. — ★★
   - *Get:* Quantum Volume: what the metric actually measures, and its
     limitations (docs [07/04](../docs/07_quantum_hardware/04_benchmarking_and_characterization.md)).
   - *Drill:* factual on the protocol; conceptual on what QV hides (crosstalk?
     stability? width-depth trade).

   <details><summary>Solution</summary>

   **Model answer.** Quantum Volume is a single number that refuses to let you cheat on
   any one axis.

   **The protocol, precisely.**

   1. Generate random **square** model circuits on `m` qubits with `m` layers. Each layer
      pairs the qubits at random and applies a Haar-random `SU(4)` to each pair.
   2. Compile each circuit for the device *as well as you can* — any layout, any
      optimisation, any error mitigation the vendor likes. This is deliberate: QV scores
      the whole stack, compiler included.
   3. Classically simulate the ideal circuit and find its **heavy outputs**: the
      bitstrings whose ideal probability exceeds the median.
   4. Run on hardware and measure the **heavy output probability** (HOP). An ideal device
      gives `HOP → (1 + ln 2)/2 ≈ 0.85`; a uniformly random device gives `0.5`.
   5. The device *passes* width `m` if the HOP exceeds `2/3` with two-sigma confidence
      over many random circuits. Then `QV = 2^(m_max)`.

   **What it actually measures.** Simultaneously: two-qubit gate fidelity, connectivity
   (a sparse coupling map costs SWAPs, which cost depth), qubit count usable *at once*,
   crosstalk during parallel layers, and compiler quality. You cannot raise QV by adding
   poor qubits, because the circuits must be square — width is bought with depth.

   **What QV hides — the conceptual half of the drill.**

   - **It saturates.** QV is exponential in a width that is capped by what you can
     classically simulate (~50 qubits), so it cannot grade the machines that matter next.
     IBM's successor metrics are CLOPS (speed) and "error per layered gate".
   - **Square circuits only.** A workload that is wide and shallow, or narrow and deep,
     is not what QV measures.
   - **A single best subset.** QV finds the *best* `m` qubits; it says nothing about the
     other 120.
   - **Compiler conflation.** A better compiler raises QV without any hardware change —
     arguably a feature, but it makes QV a poor physics diagnostic.
   - **Stability and drift.** One good day passes the test; QV is not a time-averaged
     quantity.
   - **No statement about error correction.** A high QV device may still be above
     threshold for a given code.

   </details>

### Chapter 08 — Advanced Topics ([docs/08](../docs/08_advanced_topics/))

1. **Watrous (2008)**, *"Quantum Computational Complexity"*, arXiv:0804.3401. — ★★★
   - *Get:* clean definitions of BQP, QMA, QIP and the known inclusions —
     the rigorous backbone of docs [08/01](../docs/08_advanced_topics/01_quantum_complexity_theory.md).
   - *Drill:* factual: class definitions and canonical complete problems;
     closed-book, draw the inclusion diagram.

   <details><summary>Solution</summary>

   **Model answer.** The rigorous definitions behind the informal claims, and the
   inclusion diagram you should be able to draw closed-book.

   **The classes.**

   - **BQP** — decided by a uniform family of polynomial-size quantum circuits with error
     `≤ 1/3`. Amplification makes the constant irrelevant. Canonical members: factoring,
     discrete log, Jones-polynomial approximation. *Not known* to contain any
     `NP`-complete problem.
   - **QMA** — the quantum analogue of `NP`/`MA`: a polynomial-size *quantum* witness
     `|ψ⟩` verified by a polynomial quantum circuit, with completeness `2/3` and
     soundness `1/3`. Canonical complete problem: the **local Hamiltonian problem**
     (Kitaev), the quantum Cook–Levin theorem; also consistency of local density
     matrices, and quantum-circuit non-identity.
   - **QIP** — quantum interactive proofs, a polynomial-time quantum verifier exchanging
     messages with an all-powerful prover. The landmark result is **QIP = PSPACE**
     (Jain–Ji–Upadhyay–Watrous), matching the classical `IP = PSPACE` — so quantum
     interaction buys nothing in this setting. Note the contrast with `MIP* = RE`, which
     arrived later and is the opposite kind of surprise.

   **The inclusions to draw.**

   ```
   P  ⊆  BPP  ⊆  BQP  ⊆  PP  ⊆  PSPACE = QIP = IP
   P  ⊆  NP   ⊆  MA   ⊆  QMA ⊆  PP  ⊆  PSPACE
   BQP ⊆ QMA
   ```

   Every containment shown is *not known* to be strict, and `BQP` versus `NP` is
   incomparable as far as anyone can prove. `BQP ⊆ PP` is the sharpest easy upper bound
   (sum over Feynman paths); `BQP ⊆ PSPACE` follows.

   **The oracle results that shape intuition.** Relative to a random oracle,
   `NP ⊄ BQP` (BBBV) — so any proof that `NP ⊆ BQP` must be non-relativising. Relative
   to a suitable oracle, `BQP ⊄ PH` (Raz–Tal, 2018, via Forrelation) — the strongest
   evidence that quantum computation is not captured by the classical polynomial
   hierarchy.

   **Reading strategy.** Watrous is a survey with real definitions. Get the definitions
   and the complete problems; the proofs of `QIP = PSPACE` and the Cook–Levin analogue
   can wait.

   </details>

2. **Lloyd (1996)**, *"Universal Quantum Simulators"*, Science 273, 1073. — ★★
   - *Get:* Trotterized Hamiltonian simulation — Feynman's conjecture made an
     algorithm (docs [08/03](../docs/08_advanced_topics/03_many_body_physics_and_simulation.md));
     the error-vs-step-count trade you can verify in Qiskit in an afternoon.
   - *Drill:* derivation round on the Trotter error bound; then implement a
     2-site Heisenberg Trotter step and check it against exact evolution.

   <details><summary>Solution</summary>

   **Model answer.** Feynman's 1982 conjecture — that a quantum computer could simulate
   quantum physics efficiently — turned into an explicit algorithm with an error bound.

   **The theorem.** If `H = Σ_(j=1)^(L) H_j` where each `H_j` acts on `O(1)` qubits, then
   `e^(−iHt)` can be approximated to error `ε` in time `poly(L, t, 1/ε)`. "Local" does
   not require geometric locality — only that each term touches a constant number of
   qubits, which covers essentially every Hamiltonian physics cares about.

   **The construction.** Each `e^(−iH_j δ)` acts on `O(1)` qubits, so it is a constant-size
   unitary implementable with `O(1)` gates. Lloyd interleaves them:

   ```
   e^(−iHt) ≈ ( Π_j e^(−iH_j t/r) )^r
   ```

   **The error bound, derived.** For a single step,
   `e^(−i(A+B)δ) − e^(−iAδ)e^(−iBδ) = −(δ²/2)[A,B] + O(δ³)`, so one step errs by
   `≤ (δ²/2)Σ_(j<k) ‖[H_j, H_k]‖`. Errors add over `r` steps with `δ = t/r`:

   ```
   ‖e^(−iHt) − (Π_j e^(−iH_j t/r))^r‖  ≤  (t²/2r) Σ_(j<k) ‖[H_j, H_k]‖  =  O(t²/r)
   ```

   Setting that to `ε` gives `r = O(t²/ε)` and a total gate count `O(L t²/ε)` — the
   scaling every later method (higher-order Suzuki, LCU, qubitization, QSVT) is measured
   against.

   **The afternoon experiment the note promises.** Build a two-site Heisenberg
   Hamiltonian `H = J(XX + YY + ZZ)`, implement one Trotter step as `RXX·RYY·RZZ`, and
   compare `Statevector` after `r` steps with `expm(−iHt)`. Two things to observe: for
   *this* Hamiltonian the three terms commute, so Trotter is **exact** at any `r` — a
   useful sanity check; add a transverse field `−h Σ X_i` and the terms stop commuting
   and the `1/r` error appears. On a 3-site transverse-field Ising chain
   (`J = 1, h = 0.8, t = 2`) the measured infidelities are
   `3.97 × 10⁻³, 9.43 × 10⁻⁴, 2.32 × 10⁻⁴` at `r = 16, 32, 64` — a factor of 4 per
   doubling, i.e. state error `∝ 1/r`, exactly as the bound predicts.

   </details>

3. **Nayak, Simon, Stern, Freedman & Das Sarma (2008)**, *"Non-Abelian anyons
   and topological quantum computation"*, Reviews of Modern Physics 80, 1083,
   arXiv:0707.1889. — ★★★
   - *Get:* what non-abelian statistics is and why braiding is naturally
     fault-tolerant; §§ I–II suffice for docs
     [08/04](../docs/08_advanced_topics/04_topological_quantum_computation.md); read after the toric
     code (ladder #9).
   - *Drill:* conceptual only on a first pass — fusion rules and why the
     computation is protected.

   <details><summary>Solution</summary>

   **Model answer.** Non-abelian statistics, and why braiding protects a computation by
   construction rather than by correction.

   **What non-abelian statistics is.** In 2+1 dimensions, exchanging two identical
   particles need not give `±1`. If a set of `n` anyons at fixed positions has a
   *degenerate* ground space of dimension `> 1`, then exchanging two of them acts on
   that space as a **unitary matrix**, and exchanges in different orders need not
   commute. The braid group, not the permutation group, labels the possibilities.

   **Fusion rules — the bookkeeping.** Anyon types fuse: `a × b = Σ_c N^c_(ab) c`. When
   some `N^c_(ab) > 1` (or several `c` appear), the fusion *outcome* is a quantum degree
   of freedom, and the dimension of the `n`-anyon space grows as `d^n` where `d` is the
   quantum dimension. Two standard examples:

   ```
   Ising anyons:     σ × σ = 1 + ψ        d_σ = √2     (not universal by braiding alone)
   Fibonacci anyons: τ × τ = 1 + τ        d_τ = φ      (universal by braiding alone)
   ```

   **Why braiding is naturally fault tolerant — the conceptual core.** The logical
   information lives in the *fusion space*, which is a global, topological property: no
   **local** operator acts on it at all. A local perturbation can therefore only produce
   an exponentially small error, `∝ exp(−L/ξ)` in the anyon separation. And the gate is
   the braid's **topology**, not its geometry — a wobbly path and a clean path around the
   same anyon give exactly the same unitary. So there is no calibration error, no
   over-rotation, and no need for an error-correction cycle: the protection is built
   into the Hilbert space. This is the same mechanism as the toric code (ladder #9),
   where logical operators are non-contractible loops, which is why reading these in
   that order is worth it.

   **The honest status.** Ising anyons (Majorana zero modes in nanowires, the `ν = 5/2`
   fractional quantum Hall state) give only Clifford gates by braiding and need a
   non-topological `T` gate, so they are not universal on their own. Fibonacci anyons
   are universal but have not been convincingly observed. Experimental claims of
   Majorana modes have repeatedly been contested. Read §§ I–II for the framework and
   treat the platform sections as history.

   </details>

4. **Gilyén, Su, Low & Wiebe (2019)**, *"Quantum singular value transformation
   and beyond"*, Proc. 51st STOC (2019), arXiv:1806.01838. — ★★★
   - *Get:* block-encodings + polynomial transformations as the "grand
     unification" of quantum algorithms (docs [08/05](../docs/08_advanced_topics/05_qsvt.md));
     aim for the framework statement, not the proofs, on the first pass.
   - *Drill:* drill docs [08/05](../docs/08_advanced_topics/05_qsvt.md) first; then factual questions
     on which classic algorithms QSVT recovers and with what polynomial.

   <details><summary>Solution</summary>

   **Model answer.** QSVT is the statement that almost every quantum algorithm is
   "apply a polynomial to the singular values of a matrix".

   **The two ingredients.**

   - **Block-encoding.** A unitary `U` *block-encodes* `A` (with `‖A‖ ≤ 1`) if `A` sits
     in its top-left corner: `A = (⟨0|⊗I) U (|0⟩⊗I)`. Prepare an ancilla in `|0⟩`, apply
     `U`, postselect the ancilla on `|0⟩`, and you have applied `A`. Sparse matrices,
     LCU decompositions `H = Σ α_l U_l` (via PREPARE/SELECT), density matrices and
     unitaries all admit efficient block-encodings.
   - **Qubitization / phase sequences.** Interleaving `U`, `U†` and ancilla `Z`-rotations
     by angles `φ_1 … φ_d` produces a new block-encoding of `P(A)`, where `P` is a
     degree-`d` polynomial with parity `d mod 2` and `|P| ≤ 1` on `[−1,1]`. The angles
     are computed classically from `P`. That is the whole theorem: **any** such
     polynomial is reachable, with cost `d` calls to the block-encoding.

   **Which algorithms it recovers, and with what polynomial.**

   | algorithm | polynomial applied to the singular values |
   |---|---|
   | Hamiltonian simulation | `e^(−iHt)` — Jacobi–Anger expansion in Chebyshev polynomials, degree `O(t + log(1/ε))` |
   | matrix inversion (HHL) | an approximation to `1/x` on `[1/κ, 1]`, degree `O(κ log(1/ε))` |
   | amplitude amplification / Grover | the Chebyshev polynomial `T_d(x)`, which is the rotation by `2dθ` |
   | phase estimation / eigenvalue filtering | an approximate step function or rectangle |
   | fixed-point amplitude amplification | a polynomial that saturates rather than oscillates |
   | Gibbs-state preparation | `e^(−βx/2)` |

   **Why "grand unification" is fair.** These were separate papers with separate
   analyses; QSVT gives one circuit template and reduces algorithm design to
   **approximation theory** — find a bounded polynomial with the behaviour you want, and
   its degree is your query complexity. It also frequently gives *optimal* complexities,
   matching known lower bounds.

   **Reading strategy.** Drill docs `08/05` first so the notation is familiar. On the
   first pass aim for the framework statement (block-encoding in, polynomial out, degree
   = cost) and the table above; the proofs — that the phase sequence realises exactly the
   achievable polynomial set, and the numerically stable angle-finding — are a second
   pass.

   </details>

---

## Suggested cadence

- **One ladder rung per week** alongside Phases 2–3 of the
  [learning sequence](README.md#recommended-learning-sequence): rungs 1–4 with
  lesson 08, rungs 5–6 with lesson 09, rungs 7–8 with the labs, rungs 9–11
  with the QEC chapter, rungs 12–13 with lesson 09's VQE/QAOA modules and
  project 1.
- **Chapter lists on demand**: when you open a docs chapter, queue its list;
  finish a paper before its project milestone needs it.
- Every paper ends the same way: a `paper-drill` session, and any score below
  7/10 sends the paper back to the pile for next week.

## Connections

- Lessons [08](08-foundations-of-quantum-mechanics.md) and
  [09](09-quantum-algorithm-design.md) provide the theory needed for most of
  the ladder's first half; [labs](../labs/) and
  [projects](../projects/) consume the second half.
- The `paper-drill` app is the retention engine for this entire lesson; the
  `flashcard-drill` app covers the definitions the papers assume.
