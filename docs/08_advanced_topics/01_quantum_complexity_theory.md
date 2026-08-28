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
  generic NP-complete problems achieves at most quadratic speedup, not superpolynomial.
- Bennett-Bernstein-Brassard-Vazirani (1997): relative to a random oracle, `NP ⊄ BQP`.
- Beyond such black-box evidence, `NP ⊄ BQP` remains unproven; it is widely believed because no
  quantum algorithm with superpolynomial advantage on any NP-complete problem has been found.

Evidence that `BQP ⊄ NP`:
- Fourier sampling problem (Bernstein-Vazirani; see below) is in BQP but not obviously in NP.
- More strongly, Aaronson-Arkhipov (2011) showed that exact boson sampling — a sampling task
  solvable by linear-optical quantum devices — cannot be efficiently simulated classically
  unless the polynomial hierarchy (PH) collapses to its third level.

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
   ground-state energies to constant relative error is QMA-hard.

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
classical: `n` queries — an `n`-vs-1 (linear) query speedup; the *recursive* Fourier sampling
version yields a superpolynomial separation.

**Simon's problem**: Find the period `s` of `f(x) = f(x⊕s)` — quantum: `O(n)` queries,
classical: `Ω(2^{n/2})` — exponential speedup. Foundation of Shor's algorithm.

**Collision problem**: Find `x ≠ y` with `f(x) = f(y)` for a 2-to-1 function — quantum:
`Θ(N^{1/3})` queries (algorithm: Brassard-Høyer-Tapp; matching lower bound: Aaronson-Shi),
classical: `Θ(√N)` — a polynomial speedup (exponent `1/2 → 1/3`).

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
that a verifier can check by reading only `O(1)` bits of the proof, chosen using `O(log n)`
random bits, with error `< 1/2`.

**Consequence (hardness of approximation)**: If `P ≠ NP`, then no polynomial-time algorithm
approximates MAX-3SAT (and many other optimization problems) beyond a certain constant ratio,
and MaxClique cannot be approximated within factor `n^{1-ε}` for any `ε > 0`.

### Quantum PCP

The **quantum PCP (QPCP) conjecture** posits a quantum analogue: every QMA proof can be
rewritten as a "quantum probabilistically checkable proof" with constant locality and constant
error. The QPCP conjecture is far from proven — it is one of the most important open problems
in quantum complexity.

**If QPCP holds**: Even approximating the ground-state energy of a local Hamiltonian to constant
*relative* precision (additive error `ε·m` for `m` local terms) is QMA-hard. This would have
dramatic implications:
- VQE cannot achieve even this coarse accuracy in polynomial time (for generic Hamiltonians),
  assuming QMA-hard problems are intractable.
- Classical simulation of quantum chemistry is fundamentally intractable even approximately.

Note that QPCP is *not* needed to limit quantum optimization heuristics like QAOA on classical
problems: the classical PCP theorem already makes approximating MaxCut beyond ratio `16/17`
NP-hard, which limits *any* algorithm — quantum included — assuming `NP ⊄ BQP`. QPCP concerns
the genuinely quantum question of QMA-hardness for ground-state energies, and remains open.

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
- **Collision**: `Q(collision) = Θ(N^{1/3})`, classical `Θ(√N)` — polynomial separation

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

**Query separation**: The Bernstein-Vazirani algorithm uses 1 query; a classical algorithm
needs exactly `n` queries. The separation is `n` vs. `1` — an unbounded factor, though only
linear in `n` (for a genuinely superpolynomial separation one uses recursive Fourier sampling
or Simon's problem).

**Note**: This is a *query complexity* separation. In the circuit complexity model, both
quantum and classical algorithms use `O(n)` total time (the input must be read). The distinction
is important: query complexity separations do not directly imply computational advantage.

---

## Summary

- **BQP** is the central quantum complexity class: `BPP ⊆ BQP ⊆ PP ⊆ PSPACE`. Neither
  `NP ⊆ BQP` nor `BQP ⊆ NP` is proven (both are believed false).
- **QMA** is the quantum analogue of NP; the Local Hamiltonian problem (ground state energy of
  `k`-local Hamiltonian) is QMA-complete.
- **QIP = PSPACE**: quantum interactive proofs are remarkably powerful.
- **Quantum query complexity** provides the cleanest separations: Grover (quadratic), Simon
  (exponential), Bernstein-Vazirani (`n` queries vs. 1).
- The **quantum PCP conjecture** would imply that approximating ground-state energies is
  QMA-hard; it remains unproven and is a central open problem.

---

## Exercises

**Exercise 1**: A BQP machine answers correctly with probability `2/3`. It is run `k` times
independently and the majority answer is taken. (a) Give a bound on the majority-vote error
using Hoeffding's inequality. (b) How large must `k` be to push the error below `2^{-20}`?

<details><summary>Solution</summary>

(a) The majority errs only if at most `k/2` runs are correct, i.e. the empirical success rate
falls `1/6` below its mean `2/3`. Hoeffding:

```
P(majority wrong) ≤ exp(-2k(1/6)²) = exp(-k/18)
```

(b) `exp(-k/18) ≤ 2^{-20}` requires `k ≥ 18 · 20 · ln 2 ≈ 250` repetitions. (For instance,
`k = 100` already gives error `≤ e^{-100/18} ≈ 0.004`.) Polynomially many repetitions give
exponentially small error — this is why the constant `1/3` in BQP's definition is arbitrary.

</details>

**Exercise 2**: Illustrate the Feynman path-sum idea behind `BQP ⊆ PSPACE` on a toy circuit:
compute the transition amplitude `⟨0|HTH|0⟩` by summing over the intermediate computational
basis states, then give the acceptance probability.

<details><summary>Solution</summary>

Insert the identity `Σ_y |y⟩⟨y|` between the gates:

```
⟨0|HTH|0⟩ = Σ_{y∈{0,1}} ⟨0|H|y⟩ ⟨y|T|y⟩ ⟨y|H|0⟩
          = (1/√2)(1)(1/√2) + (1/√2)(e^{iπ/4})(1/√2)
          = (1 + e^{iπ/4})/2
```

(`T` is diagonal, so only diagonal terms appear.) Acceptance probability:
`|(1 + e^{iπ/4})/2|² = (1 + cos(π/4))/2 = cos²(π/8) ≈ 0.854`.

The general point: an `m`-gate circuit's amplitude is a sum of `2^{O(nm)}` products, each of
which is computable with `poly(n, m)` space; the sum can be accumulated term by term reusing
space. Exponential *time*, polynomial *space* — hence `BQP ⊆ PSPACE`.

</details>

**Exercise 3**: Consider the 2-qubit, 2-local Hamiltonian `H = -Z₁Z₂ - X₁`. (a) Show the two
terms anticommute. (b) Use that to find all eigenvalues of `H` and the ground-state energy.
(This is a toy instance of the Local Hamiltonian problem — solvable by hand here, QMA-complete
in general.)

<details><summary>Solution</summary>

(a) `X₁` anticommutes with `Z₁` (and commutes with `Z₂`), so `(Z₁Z₂)(X₁) = -X₁(Z₁Z₂)`.

(b) Write `H = -(A + B)` with `A = Z₁Z₂`, `B = X₁`, where `A² = B² = I` and `AB = -BA`:

```
H² = (A + B)² = A² + B² + AB + BA = 2I   (cross terms cancel by anticommutation)
```

Every eigenvalue `λ` of `H` satisfies `λ² = 2`, so `λ = ±√2`, each with multiplicity 2
(the 4-dimensional space splits evenly since `Tr H = 0`). Ground-state energy: `E₀ = -√2`.

The Local Hamiltonian problem asks precisely such questions (`E₀ ≤ a` or `≥ b`?) for sums of
polynomially many local terms — where no such algebraic shortcut exists and the problem becomes
QMA-complete.

</details>

**Exercise 4**: Classify each known query separation as *polynomial* or *superpolynomial*
(in the input size `n`, with oracle domain `N = 2ⁿ`), and state one problem for which quantum
computers provably give **no** asymptotic query advantage: (a) Grover search, (b) Simon's
problem, (c) Bernstein-Vazirani, (d) collision, (e) parity of all `N` bits.

<details><summary>Solution</summary>

- (a) Grover: `Θ(√N)` vs `Θ(N)` — quadratic in `N`, i.e. polynomial (and exponential in `n`
  on both sides).
- (b) Simon: `O(n)` vs `Ω(2^{n/2})` — **superpolynomial (exponential)** separation.
- (c) Bernstein-Vazirani: `1` vs `n` — polynomial (linear) separation.
- (d) Collision: `Θ(N^{1/3})` vs `Θ(N^{1/2})` — polynomial separation.
- (e) Parity: computing the parity of all `N` oracle bits needs `Θ(N)` classical queries and
  `Θ(N/2)` quantum queries (polynomial-method lower bound of Beals et al.) — only a factor-2
  saving, i.e. **no asymptotic quantum advantage**.

Moral: quantum query advantages range from "none" to "exponential" depending on the *structure*
of the problem; unstructured problems (search, parity) admit at most polynomial gains.

</details>

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
5. **Aharonov, D., Arad, I., and Vidick, T.** — "The quantum PCP conjecture," arXiv:1309.7495
   (2013). Survey of the quantum PCP problem.
