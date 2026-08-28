# Quantum Circuit Complexity

> **Prerequisites**: 03_circuit_model_and_universality.md, familiarity with classical complexity classes (P, NP, BPP)  
> **Connects to**: Quantum algorithms (contextualizes speedups), Shor and Grover (BQP hardness), fault-tolerant computing (resource overhead)

## Overview

Quantum circuit complexity is the study of what quantum computers can and cannot efficiently compute. It provides the theoretical framework that separates genuine quantum speedups from mere constant-factor improvements, and it clarifies the relationship between quantum computation and classical complexity theory.

The central complexity class is **BQP** (Bounded-error Quantum Polynomial time) — the set of problems solvable by a quantum computer in polynomial time with error probability at most 1/3. Understanding BQP requires knowing where it sits relative to classical classes: P (deterministic polynomial time), BPP (randomized polynomial time), and NP (non-deterministic polynomial time). These relationships reveal what quantum computers are (and are not) better at.

A striking feature of quantum complexity theory is that many fundamental questions remain open. We do not know whether BQP ⊆ P (would quantum computing collapse to classical), whether BQP ⊆ NP (whether a classical witness could always verify quantum outputs), or whether BQP = BPP (would quantum provide no advantage at all). What we do know is that BQP contains problems like integer factoring that are not known to be in P or BPP — and this asymmetry is what makes quantum computing valuable.

This chapter also covers the fault-tolerant resource measures T-depth and T-count in more depth, and introduces the query complexity model — a cleaner mathematical setting where quantum speedups can be proven unconditionally.

## BQP: Bounded-Error Quantum Polynomial Time

### Definition

**BQP** is the class of decision problems (yes/no questions) solvable by a quantum circuit family `{Cₙ}` where:

1. For any input `x` of length `n`, the circuit `Cₙ` runs on `poly(n)` qubits and has `poly(n)` gates
2. The circuit outputs one bit (measuring one qubit in the computational basis)
3. If the correct answer is "yes," the circuit outputs 1 with probability `≥ 2/3`
4. If the correct answer is "no," the circuit outputs 1 with probability `≤ 1/3`

The error probability 1/3 is arbitrary — any constant `< 1/2` gives the same class. By running the circuit `O(log(1/δ))` times and taking the majority vote, we can reduce the error to `δ` for any `δ > 0`, at polynomial overhead.

The circuit family `{Cₙ}` must be **uniformly computable**: a classical computer can generate the description of `Cₙ` from `n` in polynomial time. This prevents the circuits from "hardcoding" exponentially long classical computations.

### Known Inclusions

$$P \subseteq BPP \subseteq BQP \subseteq PP \subseteq PSPACE$$

Whether BQP is contained in the **polynomial hierarchy** (PH) is a major open problem — no inclusion like `BQP ⊆ NP` or `BQP ⊆ NP^NP` is known. In fact there is strong evidence against it: **Raz and Tal (2019)** constructed an oracle relative to which `BQP ⊄ PH`, so any proof that BQP sits inside the polynomial hierarchy would have to use non-relativizing techniques.

The inclusion `BQP ⊆ PSPACE` follows from the fact that quantum computations can be simulated classically using only polynomial *space* (though exponential time). The simulation enumerates the amplitudes of the computation path-by-path.

`P ⊆ BQP` because any classical deterministic computation can be implemented as a quantum circuit (simulate each bit operation reversibly using Toffoli gates, then measure).

`BPP ⊆ BQP` because any randomized classical algorithm can be simulated: replace random coin flips with Hadamard gates and measurements.

**The key open question**: Is `BPP = BQP`? If yes, quantum computers provide no asymptotic advantage. The near-universal belief is that `BPP ≠ BQP` — that quantum computers can solve some problems (like factoring) exponentially faster than any classical randomized algorithm. But this is **not proven**.

### BQP vs. NP

The relationship between BQP and NP is subtle and important. There is strong evidence that:

$$BQP \not\supseteq NP \quad \text{(quantum computers cannot solve all NP-hard problems)}$$

The evidence: the Grover search algorithm gives a quadratic speedup for NP-complete problems, and the BBBV theorem (Bennett–Bernstein–Brassard–Vazirani 1997) proves this is optimal in the black-box setting — any quantum algorithm searching an unstructured space of `N` candidates needs `Ω(√N)` queries. Beating that would require exploiting problem *structure*, and despite decades of effort no candidate polynomial-time quantum algorithm for an NP-complete problem is known. Whether `NP ⊆ BQP` remains formally open, but it is widely disbelieved.

**Oracle separations**: In the oracle model (where the algorithm can query a black-box function), there exist problems where quantum computers are exponentially faster than classical (the "exponential gap"). But oracle results do not directly imply separations for the real complexity classes. Shor's algorithm is not an oracle result — it genuinely factors numbers efficiently.

**Practical consequence**: Do not expect quantum computers to solve NP-complete problems (like 3-SAT, traveling salesman, protein folding) in polynomial time. The quantum advantage for NP-hard problems is at best quadratic (via Grover search), and even that may not help for practical instance sizes.

## QMA: Quantum Merlin-Arthur

**QMA** is the quantum analogue of NP. A problem is in QMA if:
- Given a witness (proof), a quantum verifier can check the answer in polynomial quantum time
- If the answer is "yes," there exists a quantum witness `|w⟩` that the verifier accepts with probability `≥ 2/3`
- If the answer is "no," all quantum witnesses are rejected with probability `≥ 2/3`

**QMA ⊇ NP**: Classical NP witnesses are also valid quantum witnesses (just encode the classical witness as a computational basis state).

**QMA-complete problems**:
- **Local Hamiltonian problem**: Given a Hamiltonian `H = Σᵢ Hᵢ` where each `Hᵢ` acts on at most `k` qubits, decide whether the ground state energy is `≤ a` or `≥ b` (for `b - a ≥ 1/poly(n)`). This is the quantum analogue of 3-SAT.
- **Consistency of quantum marginals**: Given local density matrices `{ρᵢⱼ}`, does there exist a global state consistent with all of them?

QMA is relevant to quantum chemistry: computing molecular ground state energies is QMA-hard in general (though specific physical instances may be easier). This suggests that even quantum computers face fundamental limitations in solving arbitrary quantum chemistry problems.

## Oracle Separations and the Query Complexity Model

### Query Complexity

In the **query complexity model**, the input is a function `f: {0,1}ⁿ → {0,1}` (or a string `x = x₁...xₙ ∈ {0,1}ⁿ`) and the algorithm accesses it only through **queries** to individual bits. The complexity is measured in the number of queries (not gate count), which gives a clean lower bound independent of circuit implementation.

**Classical query complexity**:
- Deterministic: `D(f)` = minimum queries to determine `f(x)` in the worst case
- Randomized: `R(f)` = minimum expected queries with bounded error

**Quantum query complexity**:

The quantum algorithm accesses `x` through an oracle `O_x`:

$$O_x|i\rangle|b\rangle = |i\rangle|b \oplus x_i\rangle \quad \text{(bit oracle)}$$

or the phase oracle:

$$O_x|i\rangle = (-1)^{x_i}|i\rangle \quad \text{(phase oracle)}$$

The quantum algorithm can make superposition queries: it applies `O_x` in superposition, accessing all bits "simultaneously." The quantum query complexity `Q(f)` is the minimum number of queries to determine `f(x)` with bounded error.

### Key Separations in Query Complexity

These are **unconditional** separations (not relative to oracles) — they prove genuine quantum speedups in the query model:

**Grover search**: `Q(OR) = O(√n)` vs `D(OR) = n`, `R(OR) = Ω(n)`. Quadratic speedup.

**Element distinctness**: Is there any repeated element in a list of `n` items? `Q = O(n^{2/3})` (Ambainis) vs `R = Θ(n)`. Sub-quadratic quantum speedup.

**NAND tree evaluation**: A balanced binary tree of NAND gates on `n` leaves. The classical randomized complexity is `R = Θ(n^{0.7537...})` (exponent `log₂((1+√33)/4)`, Snir's algorithm shown optimal by Saks–Wigderson) — note this is already sublinear, not `Θ(n)`. Quantumly, the Farhi–Goldstone–Gutmann continuous-time walk algorithm evaluates the tree in time `O(√n)`; in the discrete query model this yields algorithms with `O(√n · log n)` queries (later improved to `n^{1/2+o(1)}`, and `Ω(√n)` queries is a proven lower bound). The quantum speedup is thus polynomial: roughly `n^{0.75} → n^{0.5}`.

**Forrelation**: A specific problem where `Q = O(1)` and `R = Ω(√n/log n)`. An exponential quantum speedup in query complexity (Aaronson-Ambainis 2014, confirmed by Bansal-Sinha 2021 to be related to bounded-degree polynomials).

### The Polynomial Method and Adversary Method

**Polynomial method**: Any quantum algorithm making `T` queries to `x` computes a multilinear polynomial of degree at most `2T` in the input bits. Therefore, if the function `f(x)` requires a polynomial of degree `d` to approximate it, then `Q(f) ≥ d/2`.

**Adversary method** (Ambainis 2002): A more powerful lower bound. One exhibits a relation pairing yes-instances with no-instances that are hard to tell apart: if every input participates in many hard pairs while any single bit position distinguishes only a few of them, then `Q(f)` must be large. Weighted refinements (the negative-weight adversary) in fact characterize quantum query complexity up to constant factors.

These methods prove the optimality of Grover search and other quantum algorithms.

## Fault-Tolerant Resource Measures

### Why T-Count Dominates

In fault-tolerant quantum computing using surface codes (or other stabilizer codes), the implementation of logical gates differs dramatically between Clifford and non-Clifford gates:

**Clifford gates** (H, S, CNOT) can be implemented **transversally** on stabilizer codes — applying the gate bitwise to all physical qubits in the code block preserves the code structure. Transversal gates require `O(d)` physical operations where `d` is the code distance.

**T gates** cannot be implemented transversally on the surface code, and the Eastin–Knill theorem shows no single code can transversally implement a full universal gate set. (Some codes, like the `[[15,1,3]]` Reed–Muller code, do have a transversal T — but then lack a transversal Clifford gate.) On the surface code, T gates instead require:

1. **Magic state preparation**: Prepare a noisy `|T⟩ = T|+⟩` state using physical T gates
2. **Magic state distillation**: Purify `k` noisy `|T⟩` states into one high-fidelity `|T⟩` using `O(k)` Clifford operations. The standard 15-to-1 protocol produces one good magic state from 15 noisy ones.
3. **Gate teleportation**: Consume one `|T⟩` to apply a logical T gate using Clifford operations and measurement

The overhead: one logical T gate costs roughly 100–1000 physical qubits and ~100 cycles of quantum error correction. One logical Clifford gate costs 1 cycle.

### T-Depth and T-Count Definitions

**T-count**: Total number of T and T† gates in a circuit.

**T-depth** (or T-parallel depth): The length of the longest path through the circuit counting only T-gate layers. T gates that can be applied in parallel (no quantum data dependencies) contribute only 1 to T-depth.

**Why T-depth matters**: With parallel magic state factories (multiple dedicated quantum processors preparing T states simultaneously), the throughput of T gates scales with the number of factories. Each factory runs autonomously, so parallel T gates are executed simultaneously. The total runtime is proportional to T-depth (not T-count) when many factories are available.

For quantum chemistry simulations, the T-depth determines the wall-clock time on a fault-tolerant machine.

### Resource Estimates for Important Algorithms

**Grover search on N items**:
- T-count: `O(√N · TC(oracle))` where TC is the T-count of the oracle
- T-depth: similar scaling
- Qubit count: `n + O(1)` for an `N = 2ⁿ` database

**Shor's algorithm for `n`-bit integer factoring**:
- CNOT count: `O(n³)` (or `O(n² log n)` with optimizations)
- T-count: `O(n³)` (or `O(n² log n)`)
- Qubit count: `O(n)` to `O(n log n)` depending on space-time tradeoffs
- Logical depth: `O(n³)` cycles

**Quantum simulation (second-quantized, `η` electrons, `N` spin orbitals)**:
- T-count for one Trotter step: `O(N^4)` or `O(N^3)` (improved methods)
- Total T-count: `O(N^4/ε)` where `ε` is energy precision

These estimates reveal why fault-tolerant quantum computing requires millions of physical qubits: a 2048-bit RSA key (n = 2048) requires roughly (Gidney–Ekerå 2021):
- `~6,000` logical qubits (about `3n` for `n = 2048`)
- `~10⁹` logical gate operations (≈ 2.7 × 10⁹ Toffolis)
- `~10¹²` physical gate operations (after error correction overhead)
- Physical qubits: at code distance `d ≈ 27`, each logical qubit costs `≈ 2d² ≈ 1,500` physical qubits, so `6,000 × 1,500 ≈ 9 × 10⁶` for the data alone; magic-state factories and routing roughly double this to `~2 × 10⁷` physical qubits, running for ~8 hours

## Circuit Depth Lower Bounds

### NC and QNC

Classical parallel complexity classes:
- `NC¹`: problems solvable in `O(log n)` depth with `poly(n)` gates
- `NC`: union of `NC^k` for all `k`; parallel polynomial time

Quantum analogues:
- `QNC¹`: `O(log n)` depth quantum circuits
- `QNC`: unbounded-depth polynomial-size quantum circuits

Known: `NC ⊆ QNC ⊆ BQP`. Whether `QNC = BQP` (can all polynomial-time quantum computations be parallelized into logarithmic depth?) is unknown.

**Shallow circuits and noise**: In the NISQ (Noisy Intermediate-Scale Quantum) era, noise prohibits deep circuits. The relevant question becomes: what can be achieved with constant-depth (`O(1)`) or logarithmic-depth circuits?

Constant-depth quantum circuits can solve some problems that constant-depth classical circuits cannot (e.g., certain "quantum advantage" experiments on random circuit sampling). But they cannot implement most useful quantum algorithms.

### Lower Bounds via Information-Theoretic Methods

For any circuit computing a function where the answer requires "synthesizing" information from `n` distributed inputs, we need at least `Ω(log n)` depth (since in `d` depth, each output qubit can only depend on qubits within distance `2^d`). This is the **light cone argument**.

For specific functions with high communication complexity, we can prove explicit circuit depth lower bounds. These are unconditional results and apply to quantum circuits as well as classical.

## Key Formulas

**BQP definition**:
$$\text{BQP} = \{L : \exists \text{ poly-size quantum circuit family with } p_\text{yes} \geq 2/3, p_\text{no} \leq 1/3\}$$

**Known complexity inclusions**:
$$P \subseteq BPP \subseteq BQP \subseteq PSPACE, \quad NP \not\subseteq BQP \text{ (conjectured)}$$

**Error reduction**:
$$\text{Repeat } O(\log(1/\delta)) \text{ times, majority vote} \Rightarrow \text{error} \leq \delta$$

**T-count for Toffoli**:
$$T\text{-count}(\text{Toffoli}) = 7$$

**Magic state distillation (15-to-1)**:
$$15 \text{ noisy } |T\rangle \text{ states with error } \varepsilon \to 1 \text{ state with error } 35\varepsilon^3$$

## Worked Example

**Problem**: Analyze the complexity class placement of integer factoring. Where does FACTOR sit relative to P, BPP, BQP, NP?

**Solution**:

Let FACTOR = {(N, k) : N has a factor ≤ k}.

**FACTOR ∈ NP**: Given a factor `p ≤ k` of `N`, we can verify `p | N` in polynomial time (compute `N mod p = 0` and check `1 < p ≤ k`). So the witness is the factor `p` itself.

**FACTOR ∈ co-NP**: Given a claim "N has no factor ≤ k," a prime factorization of N (provable using the AKS primality test) serves as a witness. So FACTOR ∈ NP ∩ co-NP.

**The NP ∩ co-NP placement is significant**: FACTOR is not known to be NP-complete (and under standard assumptions, it is not, since NP-complete problems are not in co-NP unless NP = co-NP). This suggests factoring is "between" P and NP-complete in some sense.

**FACTOR ∈ BQP**: Shor's algorithm solves FACTOR in polynomial quantum time. Specifically, on an `n`-bit number `N`:
- Preprocessing: classical `O(n³)` checks (is N even? a prime? a prime power?)
- Quantum order-finding: `O(n²)` qubits, `O(n³)` gates, finds period of `aˣ mod N`
- Postprocessing: classical `O(n³)` (GCD computation)
- Total: `O(n³)` quantum gates → polynomial quantum time → FACTOR ∈ BQP

**FACTOR ∈ P?**: Unknown. The best classical algorithm is the **General Number Field Sieve (GNFS)**:
$$\text{GNFS time} = \exp\left(O\left(n^{1/3}(\log n)^{2/3}\right)\right) = \text{sub-exponential in } n = \log N$$

This is faster than exponential in `n` (the number of bits) but much slower than polynomial. FACTOR is not known to be in P.

**Summary of placements**: `FACTOR ∈ NP ∩ co-NP ∩ BQP`; it is not known to be in `P` (or `BPP`), and it is believed not to be NP-complete.

The diagram:

```
PSPACE
  ↑
 PP
  ↑
BQP ← FACTOR is here (Shor's algorithm)
  ↑
BPP
  ↑     NP ← NP-complete problems (SAT, TSP, etc.)
  P        (likely not in BQP)
```

**Key lesson**: Shor's algorithm demonstrates `BQP \neq BPP` (assuming factoring is hard classically), without putting FACTOR in NP-complete. Quantum computers are powerful for specific algebraic problems, not necessarily for NP-complete problems.

## Summary

- **BQP** is the class of problems efficiently solvable by quantum computers; `P ⊆ BPP ⊆ BQP ⊆ PSPACE`; whether `BPP = BQP` is unknown
- **BQP vs NP**: quantum computers almost certainly cannot solve NP-hard problems in polynomial time; Grover search gives at best a quadratic (not exponential) speedup for NP problems
- **QMA** is the quantum analogue of NP; the local Hamiltonian problem is QMA-complete and is relevant to quantum chemistry
- The **query complexity model** allows unconditional quantum speedup proofs; Grover (quadratic), element distinctness (sub-quadratic), Forrelation (exponential) are key results
- **T-count and T-depth** are the dominant fault-tolerant resource measures; Clifford gates are cheap, T gates cost ~1000x more due to magic state distillation overhead
- **Integer factoring** (Shor's algorithm) is the flagship BQP problem: in NP ∩ co-NP classically, polynomial quantum time; this separation (assuming classical hardness) constitutes the strongest evidence that BQP ≠ BPP
- Quantum computers are neither general-purpose speedup machines nor limited to trivial improvements — they excel at specific algebraic and search problems with proven speedups

## Exercises

**Exercise 1**: A BQP machine errs with probability at most `1/3` per run. Compute the exact error probability after taking the majority vote of 5 independent runs, and explain why repeating `O(log(1/δ))` times suffices for error `δ`.

<details><summary>Solution</summary>

The majority is wrong iff at least 3 of the 5 runs err. With per-run error `1/3`:

`P(err) = C(5,3)(1/3)³(2/3)² + C(5,4)(1/3)⁴(2/3) + C(5,5)(1/3)⁵`

`= 10·(4/243) + 5·(2/243) + 1/243 = (40 + 10 + 1)/243 = 51/243 = 17/81 ≈ 0.210`

Five runs cut the error from `0.333` to `0.210`; the Chernoff bound shows the error of a `k`-run majority decays as `e^{-ck}` for a constant `c > 0` (since each run is correct with probability bounded away from `1/2`). Setting `e^{-ck} ≤ δ` gives `k = O(log(1/δ))` — this is why the constant `1/3` in the definition of BQP is arbitrary.

</details>

**Exercise 2**: A Grover search runs over a database of `N = 2²⁰` items with a single marked item. The oracle circuit has T-count `10⁴`. Estimate (a) the number of Grover iterations and (b) the total oracle T-count of the algorithm.

<details><summary>Solution</summary>

**(a)** The optimal iteration count is `⌊(π/4)√N⌋`. Here `√N = 2¹⁰ = 1024`, so

`⌊(π/4)·1024⌋ = ⌊804.2⌋ = 804 iterations`

**(b)** Each iteration makes one oracle call (plus the reflection, whose cost we ignore here):

`804 × 10⁴ ≈ 8.0 × 10⁶ T gates`

Compare classical: `~5×10⁵` expected classical evaluations of the predicate. The quadratic query advantage (`~800` vs `~500,000`) is real, but the fault-tolerant cost per quantum oracle call means the crossover to a practical advantage requires large `N` and cheap oracles — the standard caveat about Grover in practice.

</details>

**Exercise 3**: The 15-to-1 magic state distillation protocol maps 15 states of error `ε` to one state of error `35ε³`. Starting from raw magic states with `ε = 10⁻²`, compute the output error after one and after two rounds of distillation, and the number of raw states consumed per final state after two rounds.

<details><summary>Solution</summary>

Round 1: `ε₁ = 35·(10⁻²)³ = 3.5 × 10⁻⁵`.

Round 2: `ε₂ = 35·(3.5×10⁻⁵)³ = 35·4.29×10⁻¹⁴ ≈ 1.5 × 10⁻¹²`.

Raw-state cost: each round-2 input consumes 15 raw states, and the round-2 protocol consumes 15 round-1 outputs: `15 × 15 = 225` raw states per final magic state (ignoring the Clifford overhead and failure probabilities).

The doubly-exponential error suppression (`ε → ε³ → ε⁹` in scaling) is why two rounds usually suffice for algorithm-scale error targets — and the `~225×` state cost is the origin of the "T gates are 100–1000× more expensive" rule of thumb.

</details>

**Exercise 4**: Classical simulation of an `n`-qubit state vector stores `2ⁿ` complex amplitudes at 16 bytes each (double precision). Find the largest `n` for which the state vector fits in (a) a 64 GiB (`2³⁶` byte) workstation and (b) a 1 PB (`10¹⁵` byte) supercomputer, and comment on what this says about `BQP ⊆ PSPACE` versus practical simulability.

<details><summary>Solution</summary>

**(a)** Need `2ⁿ · 16 ≤ 64 × 2³⁰ = 2³⁶`, i.e. `2ⁿ ≤ 2³²`. Largest `n = 32`.

**(b)** Need `2ⁿ · 16 ≤ 10¹⁵`, i.e. `2ⁿ ≤ 6.25 × 10¹³`. Since `2⁴⁵ ≈ 3.5 × 10¹³` fits (`5.6 × 10¹⁴` bytes) but `2⁴⁶ ≈ 7.0 × 10¹³` does not (`1.13 × 10¹⁵` bytes), the largest is `n = 45`.

Each added qubit doubles the memory — brute-force simulation hits a wall around 45–50 qubits regardless of engineering. Note the contrast with `BQP ⊆ PSPACE`: the *space*-efficient simulation avoids storing the state vector by summing over computation paths, but pays with exponential *time*. Exponential resources appear somewhere in every known classical simulation; the open question `BPP vs BQP` is whether that is fundamentally necessary.

</details>

## Further Reading

1. **Aaronson**, *Quantum Computing Since Democritus* (Cambridge) — Chapter 10 on quantum complexity theory; exceptional for intuition about BQP vs NP vs PSPACE
2. **Watrous**, *The Theory of Quantum Information* (Cambridge, 2018; free online) — rigorous complexity-theoretic treatment of quantum computation, BQP, QMA, and quantum interactive proof systems
3. **Ambainis**, "Quantum Lower Bounds by Quantum Arguments" (JCSS, 2002) — introduces the adversary method for quantum lower bounds; the key tool for proving optimality of Grover search
4. **Bravyi, Gosset & König**, "Quantum Advantage with Shallow Circuits" (Science, 2018) — proves an unconditional (not oracle-relative) quantum advantage for constant-depth circuits; major theoretical breakthrough
5. **Gidney & Ekerå**, "How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits" (Quantum, 2021) — concrete fault-tolerant resource estimates for Shor's algorithm on realistic hardware; shows the practical scale of the quantum computing challenge
