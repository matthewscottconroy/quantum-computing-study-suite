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

### 2. Bell (1964) — ★★
J. S. Bell, *"On the Einstein Podolsky Rosen Paradox"*, Physics Physique
Fizika 1, 195 (1964).
- **Get out of it:** how a *testable inequality* falls out of the locality +
  hidden-variable assumptions; the exact role of the free-choice assumption;
  reproduce the inequality derivation yourself.
- **Drill it:** derivation questions — have paper-drill walk you through the
  correlation-function bound step by step; you fill in each inequality.

### 3. CHSH (1969) — ★★
J. F. Clauser, M. A. Horne, A. Shimony, R. A. Holt, *"Proposed Experiment to
Test Local Hidden-Variable Theories"*, Physical Review Letters 23, 880 (1969).
- **Get out of it:** why Bell's original inequality wasn't experiment-ready
  and what CHSH relaxed; the |S| ≤ 2 bound and the quantum 2√2 violation
  (Tsirelson bound — docs [02/04](../docs/02_quantum_mechanics/04_entanglement_and_nonlocality.md)).
- **Drill it:** factual + derivation mix; then, closed-book, write the four
  measurement settings that achieve 2√2.

### 4. Deutsch–Jozsa (1992) — ★★
D. Deutsch, R. Jozsa, *"Rapid solution of problems by quantum computation"*,
Proceedings of the Royal Society A 439, 553 (1992).
- **Get out of it:** the first clean exponential quantum-classical separation
  (for exact computation); the phase-kickback + interference template every
  later algorithm reuses — compare with docs
  [04/02](../docs/04_quantum_algorithms/02_deutsch_jozsa_and_bernstein_vazirani.md)'s modern one-page version.
- **Drill it:** derivation drill on the modern form; then a conceptual round
  on *why* the speedup evaporates if you allow bounded error classically.

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

### 7. Preskill NISQ (2018) — ★
J. Preskill, *"Quantum Computing in the NISQ era and beyond"*, Quantum 2, 79
(2018), arXiv:1801.00862.
- **Get out of it:** the vocabulary and the sober scorecard: what 50–100 noisy
  qubits can and cannot plausibly do; the framing every hardware paper since
  has been answering. Read before doing the [labs](../labs/).
- **Drill it:** factual + conceptual; a good first paper-drill session — it's
  prose, quantitative but not technical.

### 8. Google Supremacy (2019) — ★★
F. Arute et al., *"Quantum supremacy using a programmable superconducting
processor"*, Nature 574, 505 (2019).
- **Get out of it:** what exactly was claimed (sampling, not useful
  computation); cross-entropy benchmarking (XEB) as the verification trick;
  the extrapolated-classical-cost controversy that followed. Companion: docs
  [07/04](../docs/07_quantum_hardware/04_benchmarking_and_characterization.md).
- **Drill it:** paste the main text (skip supplements); conceptual questions
  on XEB and on which criticisms of the classical-cost estimate later stuck.

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

### 13. QAOA — Farhi, Goldstone, Gutmann (2014) — ★★
E. Farhi, J. Goldstone, S. Gutmann, *"A Quantum Approximate Optimization
Algorithm"*, arXiv:1411.4028 (2014).
- **Get out of it:** the alternating cost/mixer structure; the p → ∞ adiabatic
  limit; the MaxCut p = 1 ring analysis you can follow completely. Companion:
  docs [06/04](../docs/06_variational_quantum_algorithms/04_qaoa.md), `vqa-trainer` app.
- **Drill it:** derivation drill on the p = 1 expectation for a single edge;
  conceptual round on what is actually known about QAOA's advantage (be
  honest: not much is proven).

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
2. **Ekert & Knight (1995)**, *"Entangled quantum systems and the Schmidt
   decomposition"*, American Journal of Physics 63, 415. — ★★
   - *Get:* the Schmidt decomposition as a working tool — existence proof,
     relation to SVD, reduced-state spectra. Pairs with docs
     [01/03](../docs/01_mathematical_foundations/03_tensor_products_and_multipartite_systems.md).
   - *Drill:* derivation drill; then compute the Schmidt coefficients of two
     given 2-qubit states by hand and check with `qiskit.quantum_info`.
3. **Horodecki, Horodecki, Horodecki & Horodecki (2009)**, *"Quantum
   entanglement"*, Reviews of Modern Physics 81, 865, arXiv:quant-ph/0702225. — ★★★
   - *Get:* a *map*, not mastery: separability criteria, entanglement
     measures, distillation. Read §§ I–IV now; keep as a reference.
   - *Drill:* paste one section at a time (it's far beyond the truncation
     limit); factual questions to build the taxonomy.

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
4. **Hensen et al. (2015)**, *"Loophole-free Bell inequality violation using
   electron spins separated by 1.3 kilometres"*, Nature 526, 682. — ★★
   - *Get:* what the detection and locality loopholes were and how the
     event-ready scheme closes both at once; the experiment that ended the
     hidden-variable escape routes.
   - *Drill:* factual round on the loopholes; conceptual on why closing both
     *simultaneously* was the hard part.

### Chapter 03 — Quantum Gates and Circuits ([docs/03](../docs/03_quantum_gates_and_circuits/))

1. **DiVincenzo (2000)**, *"The Physical Implementation of Quantum
   Computation"*, Fortschritte der Physik 48, 771, arXiv:quant-ph/0002077. — ★
   - *Get:* the five DiVincenzo criteria — the checklist every hardware
     platform in docs [07](../docs/07_quantum_hardware/) is graded against.
   - *Drill:* closed-book: list all five criteria (plus the two communication
     ones) and give one platform that struggles with each.
2. **Barenco et al. (1995)**, *"Elementary gates for quantum computation"*,
   Physical Review A 52, 3457, arXiv:quant-ph/9503016. — ★★
   - *Get:* universality of single-qubit + CNOT; the standard Toffoli
     decomposition; counting arguments behind docs
     [03/03](../docs/03_quantum_gates_and_circuits/03_circuit_model_and_universality.md). Feeds
     [project 2](../projects/project2_transpiler_pass.md) directly.
   - *Drill:* derivation drill on the two-qubit decompositions; rebuild the
     6-CNOT Toffoli construction on paper.
3. **Dawson & Nielsen (2005)**, *"The Solovay-Kitaev Algorithm"*,
   arXiv:quant-ph/0505030. — ★★
   - *Get:* how *any* gate is approximated from a finite set with
     polylog(1/ε) overhead — the theorem that makes "universal gate set" a
     useful phrase; algorithmic, very readable.
   - *Drill:* conceptual + one derivation round on the recursion and its
     ε-scaling.
4. **Raussendorf & Briegel (2001)**, *"A One-Way Quantum Computer"*, Physical
   Review Letters 86, 5188. — ★★★
   - *Get:* computation by measurement on a cluster state — the model behind
     docs [03/05](../docs/03_quantum_gates_and_circuits/05_measurement_based_qc.md); understand
     teleportation-driven gates and feed-forward.
   - *Drill:* conceptual; then derive the 1-qubit teleportation identity that
     powers the scheme.

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
2. **Bennett & Brassard (1984)**, *"Quantum cryptography: Public key
   distribution and coin tossing"*, Proc. IEEE Int. Conf. on Computers,
   Systems and Signal Processing, Bangalore, 175. — ★
   - *Get:* the BB84 protocol from the source — it's short and concrete;
     exactly what [project 4](../projects/project4_bb84.md) implements.
   - *Drill:* closed-book protocol walkthrough: state the four states, the
     sifting rule, and the intercept-resend QBER of 25%.
3. **Ekert (1991)**, *"Quantum cryptography based on Bell's theorem"*,
   Physical Review Letters 67, 661. — ★★
   - *Get:* entanglement-based QKD; security from a CHSH test rather than
     conjugate coding — ties chapters 02 and 04 together.
   - *Drill:* conceptual round contrasting E91's security argument with BB84's.
4. **Harrow, Hassidim & Lloyd (2009)**, *"Quantum Algorithm for Linear Systems
   of Equations"*, Physical Review Letters 103, 150502, arXiv:0811.3171. — ★★★
   - *Get:* the HHL pipeline (docs [04/07](../docs/04_quantum_algorithms/07_hhl_quantum_linear_systems.md));
     and — just as important — the fine print: state preparation, condition
     number, and output-access caveats.
   - *Drill:* factual round on the assumptions; conceptual on which caveat
     kills which proposed application.

### Chapter 05 — Quantum Error Correction ([docs/05](../docs/05_quantum_error_correction/))

Core: **Kitaev toric code**, **Panteleev–Kalachev**, **Bravyi et al.** —
classics ladder #9–11.

1. **Shor (1995)**, *"Scheme for reducing decoherence in quantum computer
   memory"*, Physical Review A 52, R2493. — ★★
   - *Get:* the 9-qubit code that proved QEC possible; how it beats the
     no-cloning objection (docs [05/01](../docs/05_quantum_error_correction/01_why_qec_is_hard.md)).
   - *Drill:* derivation: show the code corrects an arbitrary single-qubit
     error from just bit-flip + phase-flip correction.
2. **Steane (1996)**, *"Error Correcting Codes in Quantum Theory"*, Physical
   Review Letters 77, 793. — ★★
   - *Get:* the CSS insight — classical Hamming codes used twice; the
     [[7,1,3]] code of [project 3](../projects/project3_steane_simulator.md).
   - *Drill:* drill after docs [05/05](../docs/05_quantum_error_correction/05_css_codes_and_steane.md);
     closed-book, write the six stabilizer generators.
3. **Gottesman (1997)**, *"Stabilizer Codes and Quantum Error Correction"*,
   PhD thesis, Caltech, arXiv:quant-ph/9705052. — ★★★
   - *Get:* the stabilizer formalism as a *language* (docs
     [05/04](../docs/05_quantum_error_correction/04_stabilizer_formalism.md)); read chapters 2–4, keep
     the rest as reference; the `qec-trainer` app drills the same machinery.
   - *Drill:* one thesis chapter per session; derivation questions on
     symplectic representation and the error-correction conditions.
4. **Fowler, Mariantoni, Martinis & Cleland (2012)**, *"Surface codes: Towards
   practical large-scale quantum computation"*, Physical Review A 86, 032324,
   arXiv:1208.0928. — ★★
   - *Get:* the tutorial-style bridge from toric code to practical surface
     code: syndrome cycles, braiding-era logic, threshold ~1%. Pairs with docs
     [05/06](../docs/05_quantum_error_correction/06_surface_code.md)–[07](../docs/05_quantum_error_correction/07_fault_tolerance.md).
   - *Drill:* section-by-section; factual on the error budget tables,
     derivation on the distance-vs-logical-rate scaling.

### Chapter 06 — Variational Quantum Algorithms ([docs/06](../docs/06_variational_quantum_algorithms/))

Core: **Peruzzo (VQE)**, **Farhi (QAOA)** — classics ladder #12–13.

1. **O'Malley et al. (2016)**, *"Scalable Quantum Simulation of Molecular
   Energies"*, Physical Review X 6, 031007. — ★★
   - *Get:* VQE done carefully on hardware for H₂ — including the tabulated
     bond-distance Hamiltonian coefficients that
     [project 1](../projects/project1_vqe_h2.md) milestone 1 uses.
   - *Drill:* factual on the experimental pipeline; then reproduce their
     dissociation curve in project 1 — the project *is* the drill.
2. **Kandala et al. (2017)**, *"Hardware-efficient variational quantum
   eigensolver for small molecules and quantum magnets"*, Nature 549, 242,
   arXiv:1704.05018. — ★★
   - *Get:* the "hardware-efficient ansatz" idea and its costs; error
     mitigation entering the VQE story. Pairs with docs
     [06/02](../docs/06_variational_quantum_algorithms/02_ansatz_design.md).
   - *Drill:* conceptual: chemically-motivated vs hardware-efficient ansätze —
     argue both sides.
3. **McClean et al. (2018)**, *"Barren plateaus in quantum neural network
   training landscapes"*, Nature Communications 9, 4812, arXiv:1803.11173. — ★★
   - *Get:* why random deep ansätze have exponentially vanishing gradients
     (docs [06/05](../docs/06_variational_quantum_algorithms/05_barren_plateaus.md)); the
     concentration-of-measure argument in outline.
   - *Drill:* derivation-lite: state the variance scaling and what assumptions
     produce it; then run project 1's stretch-goal gradient-variance probe.
4. **Cerezo et al. (2021)**, *"Variational quantum algorithms"*, Nature
   Reviews Physics 3, 625, arXiv:2012.09265. — ★★
   - *Get:* the field map — read *last*, as consolidation; it organizes
     everything docs chapter 06 covers.
   - *Drill:* factual sweep, one section per session; perfect closed-book
     material for the `vqa-trainer` app in parallel.

### Chapter 07 — Quantum Hardware ([docs/07](../docs/07_quantum_hardware/))

Core: **Preskill NISQ**, **Arute et al.** — classics ladder #7–8.

1. **Cirac & Zoller (1995)**, *"Quantum Computations with Cold Trapped Ions"*,
   Physical Review Letters 74, 4091. — ★★
   - *Get:* the first concrete gate proposal on real physics: shared motional
     modes as the qubit bus (docs [07/02](../docs/07_quantum_hardware/02_trapped_ion_qubits.md)).
   - *Drill:* conceptual on why the phonon bus gives all-to-all connectivity
     and what limits gate speed.
2. **Koch et al. (2007)**, *"Charge-insensitive qubit design derived from the
   Cooper pair box"*, Physical Review A 76, 042319, arXiv:cond-mat/0703002. — ★★★
   - *Get:* the transmon: why running E_J/E_C large exponentially suppresses
     charge noise at only polynomial cost in anharmonicity — the trade that
     powers every IBM device you used in the [labs](../labs/).
   - *Drill:* skip the heavy appendices; derivation round on the
     charge-dispersion vs anharmonicity scaling.
3. **Krantz et al. (2019)**, *"A Quantum Engineer's Guide to Superconducting
   Qubits"*, Applied Physics Reviews 6, 021318, arXiv:1904.06560. — ★★
   - *Get:* the working reference for docs [07/01](../docs/07_quantum_hardware/01_superconducting_qubits.md):
     gates, readout, T1/T2 characterization — read it with your lab 3
     calibration data open.
   - *Drill:* section-by-section factual; then re-answer the questions using
     numbers you pull from `FakeTorino`'s target (lab 3).
4. **Cross et al. (2019)**, *"Validating quantum computers using randomized
   model circuits"*, Physical Review A 100, 032328, arXiv:1811.12926. — ★★
   - *Get:* Quantum Volume: what the metric actually measures, and its
     limitations (docs [07/04](../docs/07_quantum_hardware/04_benchmarking_and_characterization.md)).
   - *Drill:* factual on the protocol; conceptual on what QV hides (crosstalk?
     stability? width-depth trade).

### Chapter 08 — Advanced Topics ([docs/08](../docs/08_advanced_topics/))

1. **Watrous (2008)**, *"Quantum Computational Complexity"*, arXiv:0804.3401. — ★★★
   - *Get:* clean definitions of BQP, QMA, QIP and the known inclusions —
     the rigorous backbone of docs [08/01](../docs/08_advanced_topics/01_quantum_complexity_theory.md).
   - *Drill:* factual: class definitions and canonical complete problems;
     closed-book, draw the inclusion diagram.
2. **Lloyd (1996)**, *"Universal Quantum Simulators"*, Science 273, 1073. — ★★
   - *Get:* Trotterized Hamiltonian simulation — Feynman's conjecture made an
     algorithm (docs [08/03](../docs/08_advanced_topics/03_many_body_physics_and_simulation.md));
     the error-vs-step-count trade you can verify in Qiskit in an afternoon.
   - *Drill:* derivation round on the Trotter error bound; then implement a
     2-site Heisenberg Trotter step and check it against exact evolution.
3. **Nayak, Simon, Stern, Freedman & Das Sarma (2008)**, *"Non-Abelian anyons
   and topological quantum computation"*, Reviews of Modern Physics 80, 1083,
   arXiv:0707.1889. — ★★★
   - *Get:* what non-abelian statistics is and why braiding is naturally
     fault-tolerant; §§ I–II suffice for docs
     [08/04](../docs/08_advanced_topics/04_topological_quantum_computation.md); read after the toric
     code (ladder #9).
   - *Drill:* conceptual only on a first pass — fusion rules and why the
     computation is protected.
4. **Gilyén, Su, Low & Wiebe (2019)**, *"Quantum singular value transformation
   and beyond"*, Proc. 51st STOC (2019), arXiv:1806.01838. — ★★★
   - *Get:* block-encodings + polynomial transformations as the "grand
     unification" of quantum algorithms (docs [08/05](../docs/08_advanced_topics/05_qsvt.md));
     aim for the framework statement, not the proofs, on the first pass.
   - *Drill:* drill docs [08/05](../docs/08_advanced_topics/05_qsvt.md) first; then factual questions
     on which classic algorithms QSVT recovers and with what polynomial.

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
