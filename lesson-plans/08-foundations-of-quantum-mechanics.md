# Foundations of Quantum Mechanics

## Goal
Engage with the deep conceptual and philosophical questions underlying quantum mechanics — interpretations, measurement problem, non-locality, and information-theoretic foundations — to build a rigorous mental model rather than just a computational toolkit.

---

## Module 1 — The Measurement Problem

**Objective:** Understand precisely what the measurement problem is and why it is unresolved.

| Aspect | Description |
|---|---|
| Unitary evolution | Schrödinger equation is linear and deterministic |
| Measurement outcome | Is random and collapses the state — non-linear |
| The problem | Measurement devices are quantum systems too; when does collapse happen? |
| Von Neumann chain | Observer → apparatus → environment → … — where does the cut go? |
| Heisenberg cut | Pragmatic division between quantum system and classical observer |

**Key questions:**
- What is a measurement, physically?
- Does collapse actually occur, or is it apparent?
- Can a quantum system measure another quantum system?

**Exercises:**
- Trace through a Stern-Gerlach measurement using the full quantum formalism for apparatus + particle
- Show that including the measurement apparatus in the wavefunction produces an entangled state, not a definite outcome
- Explain why the Born rule is not derivable from unitary evolution alone (without additional assumptions)

---

## Module 2 — Interpretations of Quantum Mechanics

**Objective:** Understand the major interpretations — what they say, what they predict, and their implications for quantum computing.

| Interpretation | Core Claim | Collapse? | Many Worlds? |
|---|---|---|---|
| Copenhagen | Stop asking; use the formalism | Yes (pragmatic) | No |
| Many-Worlds (Everett) | All branches exist; branching on measurement | No | Yes |
| Pilot Wave (de Broglie-Bohm) | Hidden variables; deterministic | No (apparent) | No |
| Relational QM | States are relative to observers | Relative | No |
| QBism | Quantum states are agent beliefs | Subjective | No |
| Consistent Histories | Multiple consistent classical frameworks | Conditional | No |
| Objective Collapse (GRW/CSL) | Physical collapse mechanism added | Yes (modified dynamics) | No |

**Quantum computing perspective:**
- Many-Worlds is favored by many quantum computer scientists (Deutsch)
- Interpretations agree on all predictions — they differ on ontology
- Decoherence provides a partial answer regardless of interpretation

**Exercises:**
- State the EPR argument and explain what it was trying to show
- Describe what "the wavefunction of the universe" means in Many-Worlds
- Explain why no interpretation can be empirically distinguished (today)

---

## Module 3 — Bell's Theorem and Non-Locality

**Objective:** Understand Bell's theorem — the most important result in foundations — and what it proves about the structure of physical reality.

| Concept | Description |
|---|---|
| Local hidden variables | Pre-existing definite values + no faster-than-light influence |
| Bell inequality | Classical bound on correlations: e.g., `|E(a,b) − E(a,c)| ≤ 1 + E(b,c)` |
| CHSH inequality | `|⟨CHSH⟩| ≤ 2` classically; quantum: up to `2√2` |
| Bell test | Measure correlations on entangled pairs and check inequality |
| Loopholes | Detection loophole, locality loophole, freedom-of-choice loophole |
| Loophole-free tests | Achieved in 2015 (Hensen et al., Giustina et al.) |
| Implications | No local hidden variable theory can reproduce QM predictions |

**Exercises:**
- Derive the CHSH inequality from local realism assumptions
- Compute the quantum mechanical prediction for `⟨CHSH⟩` for `|Φ⁺⟩`
- Show that `2√2` is the Tsirelson bound (maximum quantum violation)
- Design a Bell test circuit in Qiskit and simulate the CHSH value

---

## Module 4 — Decoherence and the Classical Limit

**Objective:** Understand how quantum systems become effectively classical through interaction with the environment — without needing collapse.

| Topic | Key Concepts |
|---|---|
| Einselection | Environment selects preferred "pointer" basis |
| Decoherence timescale | Extremely fast for macroscopic objects (10⁻²³ s for a dust grain) |
| Reduced density matrix | Tracing out environment destroys off-diagonal coherences |
| Pointer states | States robust under environmental monitoring |
| Quantum Darwinism | Classical world emerges when many environment copies record the same info |
| Decoherence vs collapse | Decoherence produces apparent collapse; does not solve preferred basis problem |

**Quantum computing relevance:**
- T₂ decoherence time measures how quickly superposition is destroyed
- Gate fidelity degrades as decoherence destroys coherences
- Error correction must fight decoherence faster than it occurs

**Exercises:**
- Compute how the off-diagonal elements of `ρ` decay under a dephasing channel
- Explain why Schrödinger's cat is in practice always decohered
- Relate T₂ time on a qubit to the decoherence mechanism

---

## Module 5 — Quantum Information-Theoretic Foundations

**Objective:** Understand quantum mechanics through the lens of information — the framework that most directly connects to quantum computing.

| Topic | Key Concepts |
|---|---|
| No-cloning theorem | Cannot copy an unknown quantum state |
| No-deleting theorem | Cannot delete an unknown quantum state |
| Holevo bound | Quantum channel can transmit at most n classical bits per n qubits |
| Superdense coding | Send 2 classical bits per entangled qubit pair |
| Quantum teleportation | Transmit qubit using entanglement + 2 classical bits |
| No-communication theorem | Entanglement cannot transmit information faster than light |
| Information as fundamental | Wheeler's "It from Bit"; QBism; information-theoretic axioms |

**Axiomatic approaches:**
- Hardy's axioms (2001): reconstruct QM from 5 simple information-theoretic postulates
- Chiribella-D'Ariano-Perinotti (CDP): QM from operational axioms about experiments
- Goal: understand *why* nature is quantum, not just *that* it is

**Exercises:**
- Prove the no-cloning theorem from linearity of quantum mechanics
- Trace through quantum teleportation step by step, identifying where entanglement is consumed
- State Hardy's 5 axioms and explain what distinguishes QM from classical probability

---

## Module 6 — Quantum Reference Frames and Relativity

**Objective:** Understand how quantum mechanics interfaces with special relativity and the role of reference frames in quantum theory.

| Topic | Key Concepts |
|---|---|
| Relativistic QM | Dirac equation; Klein-Gordon equation |
| Quantum field theory (QFT) | Particles as excitations of fields; the correct fundamental theory |
| Lorentz covariance | Physical laws must be the same in all inertial frames |
| Quantum nonlocality vs relativity | Entanglement is nonlocal but cannot signal — consistent with relativity |
| Quantum reference frames | Quantizing the reference frame itself |
| Unruh effect | Accelerating observer sees thermal radiation in vacuum |

**Quantum computing relevance:**
- Relativistic effects matter for satellite-based quantum communication
- QFT is the target for quantum simulation of particle physics
- Understanding causal structure is relevant to quantum causal models and process matrices

**Exercises:**
- Show that quantum teleportation does not allow faster-than-light signaling
- Explain why the Dirac equation predicts antiparticles
- Describe how the quantum Zeno effect relates to measurement frequency

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Quantum Theory and Measurement* — Wheeler & Zurek (eds.) | Book | Original papers on foundations |
| *The Fabric of Reality* — Deutsch | Book | Many-Worlds, by its foremost proponent |
| *Quantum Theory Cannot Hurt You* — Vedral | Book | Accessible, covers QM and relativity |
| *Something Deeply Hidden* — Carroll | Book | Modern Many-Worlds account |
| Bell's 1964 paper "On the Einstein-Podolsky-Rosen Paradox" | Paper | Original Bell theorem |
| Zurek's papers on decoherence and einselection | Papers | Definitive reference on decoherence |
| Hardy (2001) "Quantum Theory From Five Reasonable Axioms" | Paper | Information-theoretic reconstruction |

---

## Progression Checkpoints

- [ ] Clearly articulate the measurement problem without using the word "collapse" carelessly
- [ ] Derive the CHSH inequality and compute the quantum violation for a Bell state
- [ ] Distinguish between decoherence and collapse and explain what decoherence does and does not resolve
- [ ] Prove the no-cloning theorem
- [ ] State and explain at least two axiomatic reconstructions of quantum mechanics
- [ ] Explain why Bell's theorem rules out local hidden variables without ruling out non-local ones
