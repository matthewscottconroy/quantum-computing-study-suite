# Quantum Complexity Theory

> **Prerequisites**: Classical complexity theory basics (P, NP, polynomial-time reductions),
> quantum algorithms overview (Chapter 4), circuit model (Chapter 3)
> **Connects to**: Quantum information theory (08/02), quantum advantage arguments, QAOA
> limits (06/04)

---

## Overview

Quantum complexity theory asks: what can be computed efficiently on a quantum computer, and how
does this relate to what can be computed classically? The answers illuminate both the power and
limits of quantum computers and provide the theoretical foundation for quantum advantage claims.

The central complexity class is **BQP** (bounded-error quantum polynomial time): problems
solvable in polynomial time on a quantum computer with error probability at most 1/3. Understanding
BQP's relationship to classical classes (P, NP, BPP, PSPACE) is a major open problem, but we
have strong evidence and conditional results.

This chapter develops the quantum complexity hierarchy, explains the key classes and their
relationships, covers quantum query complexity (where tight separations are known), and discusses
the quantum PCP conjecture — one of the deepest open problems connecting quantum complexity to
physics.

---

## Classical Complexity Background

### The Classical Hierarchy

Recall the fundamental complexity classes:

- **P**: polynomial-time deterministic computation.
- **NP**: problems where a solution can be *verified* in polynomial time.
- **BPP**: polynomial-time randomized computation, bounded error.
- **PSPACE**: problems solvable using polynomial space (unlimited time).
- **PP**: problems solvable in polynomial time with unbounded error (output correct with prob > 1/2).
- **#P**: counting the number of solutions to NP problems (harder than NP).

Known containments:
```
P ⊆ BPP ⊆ PP ⊆ PSPACE ⊆ EXP
P ⊆ NP ⊆ PH ⊆ PSPACE
```

The `P ≠ NP` conjecture is unproven; most believe `P ≠ NP ≠ PSPACE`.

---

## BQP: Bounded-Error Quantum Polynomial Time

### Definition

**BQP** (Bernstein-Vazirani, 1993) is the class of decision problems solvable by a
polynomial-size quantum circuit with error probability at most `1/3`:

```
L ∈ BQP  iff  ∃ poly-size QC C: P(C accepts L input correctly) ≥ 2/3
```

The constant 1/3 is not special: error can be reduced to `2^{-poly(n)}` by repeating
and taking the majority vote, while keeping polynomial resources.

### Relationships

**Known**:
```
BPP ⊆ BQP ⊆ PP ⊆ PSPACE
```

- **BPP ⊆ BQP**: Quantum computers can simulate classical randomized algorithms (replace random
  bits with Hadamards; this wastes quantum power but establishes containment).
- **BQP ⊆ PP**: Any quantum computation can be simulated in PP using the fact that quantum
  amplitudes are algebraic numbers and polynomial-size circuits involve polynomial-size
  amplitude computations.
- **BQP ⊆ PSPACE**: Quantum circuits can be simulated in polynomial space by tracking the state
  vector column by column.

**Conjectured (unproven)**:
```
BPP ⊊ BQP  (quantum speedup exists)
BQP ⊊ PP   (quantum computers are weaker than #P-oracle)
BQP ⊄ NP   (quantum computers cannot solve all NP problems efficiently)
NP ⊄ BQP   (quantum computers cannot solve all NP problems)
```

### BQP vs. NP

This relationship is particularly subtle and important. Evidence that `NP ⊄ BQP`:
- The Unstructured Search speedup of Grover is only quadratic; the best known QC algorithm for
  generic NP-complete problems achieves at most quadratic speedup, not polynomial.
- Bennett-Bernstein-Brassard-Vazirani (1997): relative to a random oracle, `NP ⊄ BQP`.
- Aaronson (2010): quantum query complexity lower bounds suggest that generic NP problems require
  exponential quantum queries.

Evidence that `BQP ⊄ NP`:
- Fourier sampling problem (Bernstein-Vazirani; see below) is in BQP but not obviously in NP.
- More strongly, Aaronson-Arkhipov (2011) showed that boson sampling, which is related to BQP,
  cannot be in `NP` unless the polynomial hierarchy (PH) collapses.

---

## QMA: Quantum Merlin-Arthur

### Definition

**QMA** (Kitaev, 2002) is the quantum analogue of NP:

```
L ∈ QMA  iff  ∃ polynomial-time quantum verifier V such that:
  - If x ∈ L: ∃ quantum witness |w⟩ with P(V accepts |w⟩) ≥ 2/3
  - If x ∉ L: ∀ quantum witnesses |w⟩, P(V accepts |w⟩) ≤ 1/3
```

The "witness" is a quantum state (polynomial qubits) and the verifier is a quantum circuit.

**Relationships**:
```
NP ⊆ QMA ⊆ PSPACE
BQP ⊆ QMA   (add trivial empty witness)
```

Whether `NP = QMA` is unknown; believed false (QMA is strictly harder than NP).

### The Local Hamiltonian Problem (QMA-Complete)

The paradigmatic QMA-complete problem is the **Local Hamiltonian (LH) problem**:

**Input**: A Hamiltonian `H = Σᵢ hᵢ` where each `hᵢ` acts on at most `k` qubits (k-local),
and energy bounds `a < b` with `b - a ≥ 1/poly(n)`.
**Question**: Is the ground-state energy `E₀ ≤ a` or `E₀ ≥ b`?

**Theorem (Kitaev, 2002)**: The 5-local Hamiltonian problem is QMA-complete. Subsequently,
the 2-local Hamiltonian problem is also QMA-complete (Kempe, Kitaev, Regev, 2006).

**Implications**:
1. **VQE hardness**: Finding the ground state of a generic local Hamiltonian (a central task of
   VQE) is QMA-hard. No polynomial-time classical or quantum algorithm is expected to solve it in
   general.
2. **Quantum simulation**: Simulating quantum systems exactly is QMA-hard; approximate simulation
   may have different complexity.
3. **Quantum PCP**: If a quantum analogue of the PCP theorem holds, then even approximating
   ground-state energies to constant error is QMA-hard.

---

## Other Quantum Complexity Classes

### QCMA (Classical Witness)

**QCMA** is like QMA but with a classical witness: the prover sends a classical bit string.
```
NP ⊆ QCMA ⊆ QMA
```
Whether QCMA = QMA is open. Separation would show that quantum witnesses are more powerful
than classical witnesses for quantum verification.

### QIP: Quantum Interactive Proofs

**QIP(k)** is the quantum analogue of IP: `k` rounds of quantum message-passing between prover
and verifier.

**Theorem (Jain et al., 2009; Kitaev-Watrous, 2000)**:
```
QIP(3) = QIP = PSPACE
```

Quantum interactive proofs with 3 rounds (and thus any polynomial number of rounds) capture all
of PSPACE. This is dramatically stronger than the classical result IP = PSPACE (which also holds
but requires many rounds). QIP(1) = QMA.

### QSZK: Quantum Statistical Zero-Knowledge

**QSZK** is the quantum analogue of statistical zero-knowledge proofs. The quantum state
distinguishability problem (are two circuits `C₁, C₂` producing near-identical or far-apart
output distributions?) is QSZK-complete. QSZK is known to be closed under complement.

---

## Quantum Query Complexity

### The Model

In the **query complexity model**, an algorithm accesses an oracle `f: {0,1}^n → {0,1}` via
queries. The complexity is the number of queries needed to compute some function of `f`. This
model separates quantum vs. classical in a clean way where tight bounds are proven.

### Known Separations

**Grover search**: Find `x` with `f(x) = 1` using `O(√N)` queries (classical: `O(N)`) —
quadratic speedup.

**Bernstein-Vazirani**: Find hidden string `s` given `f(x) = s·x mod 2` — quantum: `1` query,
classical: `n` queries — exponential query speedup.

**Simon's problem**: Find the period `s` of `f(x) = f(x⊕s)` — quantum: `O(n)` queries,
classical: `Ω(2^{n/2})` — exponential speedup. Foundation of Shor's algorithm.

**Collision problem**: Find `x ≠ y` with `f(x) = f(y)` — quantum: `O(N^{1/3})` queries
(Brassard et al., 2002), classical: `Θ(√N)` — cubic speedup.

### Polynomial Method and Adversary Method

Two main techniques for proving query lower bounds:

**Polynomial method** (Beals et al., 2001): Any quantum query algorithm computing `f` using
`q` queries can be expressed as a multivariate polynomial of degree `≤ 2q`. Lower bounds on
the polynomial degree of `f` give lower bounds on `q`.

**Adversary method** (Ambainis, 2002): Construct a bipartite relation between "positive" and
"negative" instances; the adversary chooses oracle bits to maximize the number of queries needed.
The general adversary method gives tight bounds for many functions.

---

## The Quantum PCP Conjecture

### Classical PCP Theorem

The **PCP theorem** (Arora-Safra-ALMSS, 1992-1998) is one of the deepest results in complexity:

**Theorem**: Every NP verification proof can be rewritten as a "probabilistically checkable proof"
that can be verified by checking only `O(1)` random bits, with error `< 1/2`.

**Consequence (hardness of approximation)**: If `P ≠ NP`, then there is no polynomial-time
algorithm achieving better than a constant approximation ratio for MaxClique, MAX-3SAT, and many
other optimization problems.

### Quantum PCP

The **quantum PCP (QPCP) conjecture** posits a quantum analogue: every QMA proof can be
rewritten as a "quantum probabilistically checkable proof" with constant locality and constant
error. The QPCP conjecture is far from proven — it is one of the most important open problems
in quantum complexity.

**If QPCP holds**: Even approximating the ground-state energy of a 2-local Hamiltonian to
constant additive error is QMA-hard. This would have dramatic implications:
- VQE cannot achieve constant accuracy in polynomial time (for generic Hamiltonians).
- QAOA cannot efficiently solve MaxCut to constant approximation ratio (under QPCP + ETH).
- Classical simulation of quantum chemistry is fundamentally intractable even approximately.

**Obstacles to QPCP**: Unlike the classical PCP theorem, which uses algebraic techniques
(sum-check protocol, low-degree testing), quantum proofs don't admit easy "randomized checking."
The no-cloning theorem prevents prover from distributing multiple copies of the witness without
exponential overhead.

---

## Key Formulas and Containments

- **Containments**: `P ⊆ BPP ⊆ BQP ⊆ PP ⊆ PSPACE`
- **NP/BQP**: `NP ⊄ BQP` (believed), `BQP ⊄ NP` (believed), neither proven
- **QMA-completeness**: `k`-Local Hamiltonian ∈ QMA-complete for `k ≥ 2`
- **QIP = PSPACE**: Quantum interactive proofs with 3 messages capture all of PSPACE
- **Grover**: `Q(search) = O(√N)`, classical `Ω(N)` — quadratic separation
- **Collision**: `Q(collision) = O(N^{1/3})`, classical `Θ(√N)` — cubic separation

---

## Worked Example: The Bernstein-Vazirani Problem

**Problem**: Given oracle `f(x) = s·x = Σᵢ sᵢxᵢ mod 2` for hidden `s ∈ {0,1}^n`, find `s`.

**Classical lower bound**: Must query at least `n` times (each query on input `eᵢ = 0...010...0`
reveals `sᵢ`; no query reveals more than 1 bit).

**Quantum algorithm** (1 query):
1. Prepare `|0⟩^n |1⟩`.
2. Apply `H^{⊗n}` to all: `|+⟩^n |−⟩ = (1/√2^n) Σ_x |x⟩ |−⟩`.
3. Query oracle: `|x⟩|−⟩ → (-1)^{f(x)} |x⟩|−⟩ = (-1)^{s·x} |x⟩ |−⟩`.
4. State after oracle: `(1/√2^n) Σ_x (-1)^{s·x} |x⟩ |−⟩`.
5. Apply `H^{⊗n}`: the Hadamard of `Σ_x (-1)^{s·x} |x⟩` is `|s⟩` (quantum Fourier analysis).
6. Measure: outcome is `s` with certainty. ✓

**Exponential query separation**: The Bernstein-Vazirani algorithm uses 1 query; a classical
algorithm needs `n` queries. The separation is `O(n) vs. O(1)` — exponential in `n`.

**Note**: This is a *query complexity* separation. In the circuit complexity model, classical
algorithms also use `O(n)` time (linear in input size), not exponential. The distinction
is important: query complexity separations do not directly imply computational advantage.

---

## Summary

- **BQP** is the central quantum complexity class: `BPP ⊆ BQP ⊆ PP ⊆ PSPACE`. Neither
  `NP ⊆ BQP` nor `BQP ⊆ NP` is proven (both are believed false).
- **QMA** is the quantum analogue of NP; the Local Hamiltonian problem (ground state energy of
  `k`-local Hamiltonian) is QMA-complete.
- **QIP = PSPACE**: quantum interactive proofs are remarkably powerful.
- **Quantum query complexity** provides the cleanest separations: Grover (quadratic), Simon
  (exponential), Bernstein-Vazirani (exponential in query count).
- The **quantum PCP conjecture** would imply that approximating ground-state energies is
  QMA-hard; it remains unproven and is a central open problem.

---

## Further Reading

1. **Bernstein, E. and Vazirani, U.** — "Quantum complexity theory," *SIAM J. Comput.* 26, 1411
   (1997). BQP definition and polynomial simulations.
2. **Kitaev, A., Shen, A., and Vyalyi, M.** — *Classical and Quantum Computation*, AMS, 2002.
   QMA and Local Hamiltonian problem.
3. **Aaronson, S.** — "BQP and the polynomial hierarchy," *STOC 2010*. BQP vs NP/PH separation
   relative to random oracle.
4. **Kempe, J., Kitaev, A., and Regev, O.** — "The complexity of the local Hamiltonian problem,"
   *SIAM J. Comput.* 35, 1070 (2006). 2-local QMA completeness.
5. **Aharonov, D. and Arad, I.** — "The BCS-HLT-RW quantum PCP conjecture," arXiv:1309.7495.
   Survey of the quantum PCP problem.
