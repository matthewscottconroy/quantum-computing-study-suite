# Quantum Algorithm Design

## Goal
Develop the skills to design, analyze, and optimize quantum algorithms — understanding the core techniques, when to apply them, and how to build new algorithms from first principles rather than just implementing known ones.

---

## Module 1 — Core Algorithmic Techniques

**Objective:** Master the six fundamental techniques from which nearly all quantum algorithms are constructed.

### 1. Phase Kickback

When a controlled-U gate acts on an eigenstate of U, the phase kicks back onto the control qubit.

```
|+⟩ ──●── → (e^(iλ)|0⟩ + |1⟩)/√2  when U|u⟩ = e^(iλ)|u⟩
|u⟩ ──U──
```

**Applications:** Deutsch-Jozsa, Bernstein-Vazirani, QPE, Grover oracle

### 2. Quantum Parallelism and Interference

- Superposition encodes exponentially many inputs simultaneously
- Interference amplifies correct answers and cancels wrong ones
- The hard part is designing the interference to be constructive for the right answer

**Key insight:** Measurement collapses superposition — the algorithm must arrange for the right answer to have high amplitude *before* measurement.

### 3. Quantum Phase Estimation (QPE)

Given unitary U and eigenstate |u⟩, estimate the phase φ where `U|u⟩ = e^(2πiφ)|u⟩`.

```
Circuit structure:
|0⟩^⊗t ──H⊗t──●──●──…──IQFT──M──  (ancilla register)
|u⟩    ────U──U²──…──────────────  (eigenstate register)
```

**Precision:** t ancilla qubits → φ accurate to 2⁻ᵗ
**Applications:** Shor's algorithm, quantum simulation, HHL

### 4. Amplitude Amplification

Generalization of Grover's search. Given oracle O_f that marks good states, amplify their amplitude.

**Grover operator:** `G = −H⊗ⁿ Z₀ H⊗ⁿ · O_f`

- Each application of G rotates state by 2θ toward target (θ = arcsin(√(M/N)))
- Optimal after k ≈ (π/4)√(N/M) iterations
- General: any algorithm using t queries can be quadratically sped up

### 5. Quantum Fourier Transform (QFT)

`QFT|j⟩ = (1/√N) Σₖ e^(2πijk/N)|k⟩`

- Implemented in O(n²) gates (vs O(N log N) classically, but N = 2ⁿ)
- **The** key primitive for period-finding and phase estimation

### 6. Variational / Hybrid Approach

- Classical optimizer adjusts parameters θ
- Quantum circuit evaluates `⟨ψ(θ)|H|ψ(θ)⟩`
- Loop until convergence

---

## Module 2 — Canonical Algorithms In Depth

**Objective:** Implement and analyze each landmark algorithm at the circuit level.

### Deutsch-Jozsa

**Problem:** Is f: {0,1}ⁿ → {0,1} constant or balanced?
**Classical:** O(2ⁿ⁻¹ + 1) queries in worst case
**Quantum:** 1 query

```
|0⟩^⊗n ──H⊗n──Uf──H⊗n──M──
|1⟩    ──H────────────────
```

**Key:** Phase kickback from the ancilla + interference on the query register

---

### Shor's Algorithm

**Problem:** Factor N into prime factors
**Classical best:** Sub-exponential GNFS: exp((64/9)^(1/3) (ln N)^(1/3) (ln ln N)^(2/3)) — in L-notation, L_N[1/3, (64/9)^(1/3)]
**Quantum:** O((log N)³) — exponential speedup

**Structure:**
1. Reduce factoring to period-finding: find r such that `aʳ ≡ 1 (mod N)`
2. If r is even and `a^(r/2) ≢ -1`: then `gcd(a^(r/2) ± 1, N)` gives a factor
3. Period-finding via QPE on the unitary `U|j⟩ = |aj mod N⟩`

**Circuit depth:** O((log N)²) with fast modular arithmetic

**Exercises:**
- Factor N=15 using the textbook QPE approach

  <details><summary>Solution</summary>

  **Step 1 — classical reduction.** `N = 15` is odd and not a prime power, so pick
  a random `a` coprime to it: take `a = 7`, `gcd(7, 15) = 1`.

  **Step 2 — order finding by QPE.** The unitary is `U|y⟩ = |7y mod 15⟩`, acting on
  `n = 4` work qubits (enough to hold `0…14`), with `t = 4` counting qubits. Start the
  work register in `|1⟩`, put the counting register in uniform superposition, apply
  controlled-`U^(2^j)` from counting qubit `j`, then the inverse QFT.

  Simulating that exactly (permutation matrix for multiplication by 7, explicit
  inverse QFT) gives only four outcomes, each with probability exactly 1/4:

  ```
  measure 0000 =  0  p=0.2500  phase=0.00  continued fraction = 0
  measure 0100 =  4  p=0.2500  phase=0.25  continued fraction = 1/4
  measure 1000 =  8  p=0.2500  phase=0.50  continued fraction = 1/2
  measure 1100 = 12  p=0.2500  phase=0.75  continued fraction = 3/4
  ```

  The outcomes are exact because `r = 4` divides `2^t = 16`, so every phase `s/r` is
  representable in 4 bits. (For a general `N` you need `t = 2n + 1` counting qubits —
  9 for `N = 15` — so that the continued-fraction step can recover `r` from an
  approximate phase.)

  **Step 3 — continued fractions.** `k/16 → s/r` gives denominators `1, 4, 2, 4`.
  Outcome 0 is useless, outcome 8 proposes `r = 2` which fails the check
  `7² = 49 ≡ 4 ≢ 1 (mod 15)`, and outcomes 4 and 12 both give the true order `r = 4`.
  So a single run succeeds with probability 1/2; two runs push that above 3/4.

  **Step 4 — extract the factors.** `r = 4` is even and

  ```
  a^(r/2) = 7² = 49 ≡ 4 (mod 15),  and 4 ≢ -1 (mod 15)
  gcd(4 - 1, 15) = gcd(3, 15) = 3
  gcd(4 + 1, 15) = gcd(5, 15) = 5
  ```

  so `15 = 3 × 5`.

  **Which bases work.** Brute-forcing every `a` in `Z*₁₅` shows only `a = 1` (odd
  order) and `a = 14 ≡ -1` (where `a^(r/2) = 14 ≡ -1`) fail — 6 of the 8 units
  succeed, a 75% success rate, comfortably above the 50% guaranteed by the next
  exercise.

  </details>

- Show why the period r satisfies `gcd(a^(r/2)−1, N) > 1` with probability ≥ 1/2

  <details><summary>Solution</summary>

  **What has to be proved.** Let `N` be odd with `k ≥ 2` distinct prime factors, and
  let `a` be drawn uniformly from `Z*_N` with order `r`. The claim is

  ```
  Pr[ r is even AND a^(r/2) ≢ -1 (mod N) ]  ≥  1 - 1/2^(k-1)  ≥  1/2
  ```

  and that when that event holds, `gcd(a^(r/2) - 1, N)` is a *non-trivial* factor.

  **The factor part first.** `a^r ≡ 1`, so `N` divides
  `a^r - 1 = (a^(r/2) - 1)(a^(r/2) + 1)`. Because `r` is the *order*, `a^(r/2) ≢ 1`,
  so `N ∤ (a^(r/2) - 1)`; by assumption `a^(r/2) ≢ -1`, so `N ∤ (a^(r/2) + 1)`. A
  number that divides a product but neither factor must split its prime power
  factors between them, so `1 < gcd(a^(r/2) - 1, N) < N`.

  **The probability part.** By CRT, `Z*_N ≅ Z*_(p₁^α₁) × … × Z*_(p_k^α_k)`, and
  choosing `a` uniformly is the same as choosing each component `aᵢ` independently
  and uniformly. Let `rᵢ = ord(aᵢ)` and `dᵢ = v₂(rᵢ)` (the exponent of 2 in `rᵢ`).
  Then `r = lcm(r₁,…,r_k)`, so `v₂(r) = max dᵢ`.

  The bad event is exactly "all the `dᵢ` are equal":

  - if `r` is odd, every `rᵢ` is odd, so all `dᵢ = 0`;
  - if `a^(r/2) ≡ -1 (mod N)`, then `a^(r/2) ≡ -1` modulo every `pᵢ^αᵢ`, so
    `rᵢ ∤ r/2` for every `i`, which forces `dᵢ = v₂(r)` for every `i`;
  - conversely, if some `dᵢ` is strictly smaller than the maximum, then `r` is even
    and `a^(r/2) ≡ +1` modulo that `pᵢ^αᵢ`, so it cannot be `-1` mod `N`.

  Now bound `Pr[dᵢ = d]`. Each `Z*_(pᵢ^αᵢ)` is cyclic of even order
  `2^cᵢ · mᵢ` with `mᵢ` odd and `cᵢ ≥ 1` (this is where "odd prime" is used). Writing
  `aᵢ = g^j` with `j` uniform, `ord(aᵢ) = 2^cᵢ mᵢ / gcd(j, 2^cᵢ mᵢ)`, so
  `dᵢ = cᵢ - v₂(j)` when `v₂(j) < cᵢ` and `dᵢ = 0` otherwise. Since
  `Pr[v₂(j) = e] = 2^(-(e+1))`,

  ```
  Pr[dᵢ = cᵢ] = 1/2,   Pr[dᵢ = cᵢ - e] = 2^(-(e+1)),   Pr[dᵢ = 0] = 2^(-cᵢ)
  ```

  so `Pr[dᵢ = d] ≤ 1/2` for every fixed `d`. By independence,

  ```
  Pr[bad] = Σ_d Π_i Pr[dᵢ = d] ≤ Σ_d (1/2)^(k-1) · Pr[d₁ = d] = (1/2)^(k-1)
  ```

  Hence `Pr[good] ≥ 1 - 2^-(k-1)`, which is `≥ 1/2` as soon as `k ≥ 2`. (A prime
  power has `k = 1` and the bound is vacuous — that is why Shor's algorithm strips
  prime powers classically before it starts.)

  **Numerical check** (brute force over all of `Z*_N`; every "good" `a` really does
  yield a non-trivial gcd):

  | N | factorisation | k | observed P(good) | bound `1 - 2^-(k-1)` |
  |---|---|---|---|---|
  | 15 | 3·5 | 2 | 0.750 | 0.500 |
  | 21 | 3·7 | 2 | 0.500 | 0.500 |
  | 33 | 3·11 | 2 | 0.500 | 0.500 |
  | 35 | 5·7 | 2 | 0.750 | 0.500 |
  | 105 | 3·5·7 | 3 | 0.875 | 0.750 |
  | 1155 | 3·5·7·11 | 4 | 0.938 | 0.875 |
  | 2431 | 11·13·17 | 3 | 0.984 | 0.750 |

  `N = 21, 33` show the bound is tight, so 1/2 cannot be improved for `k = 2`.

  </details>

- Estimate the number of qubits needed to factor a 2048-bit RSA key

  <details><summary>Solution</summary>

  Work with `n = 2048` bits and count **logical** qubits first, then multiply by the
  error-correction overhead.

  **Naive textbook circuit.** QPE for order finding needs `2n + 1` counting qubits,
  the modular exponentiation needs an `n`-qubit work register, and schoolbook
  reversible modular arithmetic needs roughly another `2n` ancillas for carries and
  the modular-reduction comparison:

  ```
  2n (counting) + n (work) + ~2n (arithmetic ancillas) ≈ 5n ≈ 10,240 logical qubits
  ```

  **Beauregard (2003).** Two standard tricks collapse this: the counting register is
  replaced by a *single* qubit re-used `2n` times with the semiclassical
  (measurement-conditioned) QFT, and Draper's transform adders remove most carry
  ancillas. Result: `2n + 3 = 4099` logical qubits, at the price of `O(n³ log n)`
  gates.

  **Gidney–Ekerå (2019), the current reference point.** Their optimised construction
  uses

  ```
  3n + 0.002 · n · lg n  =  3(2048) + 0.002(2048)(11)  ≈  6189 logical qubits
  0.3 n³ + 0.0005 n³ lg n  ≈  2.6 × 10⁹  Toffoli gates
  ```

  **Physical qubits.** This is where the real number lives. At a physical error rate
  of `10⁻³` with a surface code, each logical qubit of the required lifetime costs
  roughly `3 × 10³` physical qubits once routing space and magic-state factories are
  included, which is how that work arrives at its headline figure: **≈ 20 million
  noisy physical qubits, running for about 8 hours**.

  **The lesson to take away.** The interesting ratio is
  `2 × 10⁷ / 6.2 × 10³ ≈ 3200` physical qubits per logical qubit. Algorithmic
  cleverness has already squeezed the logical count from `10⁴` to `6 × 10³`; the
  remaining three orders of magnitude are pure error-correction overhead, so
  improving physical gate fidelity buys far more than further algorithmic tuning.
  Today's largest devices hold `~10³` *physical* qubits with no error correction.

  </details>

---

### Grover's Algorithm

**Problem:** Find marked element in unstructured database of N items
**Classical:** O(N) expected
**Quantum:** O(√N) — quadratic speedup (proven optimal)

**Algorithm:**
1. Prepare `|s⟩ = H⊗ⁿ|0⟩` (uniform superposition)
2. Repeat k ≈ (π/4)√N times: Apply oracle O_f, then Grover diffusion D = 2|s⟩⟨s| − I
3. Measure — find marked element with probability O(1)

**Exercises:**
- Simulate Grover on 3 qubits for a single marked state

  <details><summary>Solution</summary>

  With `N = 2³ = 8` and `M = 1`, `sin θ = √(M/N) = 1/(2√2)`, so
  `θ = 0.36137 rad = 20.705°` and the optimal iteration count is

  ```
  k_opt = round( (π/4)√(N/M) - 1/2 ) = round(2.2214 - 0.5) = 2
  ```

  **Closed form.** After `k` iterations the amplitude on the marked state is
  `sin((2k+1)θ)`. Writing `b_k = √8 · sin((2k+1)θ)` and using
  `cos 2θ = 1 - 2sin²θ = 3/4`, the triple-angle identity becomes the integer
  recursion `b_(k+1) = (3/2)b_k - b_(k-1)` with `b_0 = 1`, `b_1 = 5/2`:

  | k | `b_k` | `P = b_k²/8` |
  |---|---|---|
  | 0 | 1 | 1/8 = 0.1250 |
  | 1 | 5/2 | 25/32 = 0.7813 |
  | 2 | 11/4 | 121/128 = 0.9453 |
  | 3 | 13/8 | 169/512 = 0.3301 |
  | 4 | -5/16 | 25/2048 = 0.0122 |

  **Qiskit implementation** (oracle for `|101⟩` is `X` on `q1`, then a `CCZ`, then
  `X` on `q1`; the diffuser is `H⊗X⊗(multi-controlled Z)⊗X⊗H`):

  ```python
  from qiskit import QuantumCircuit
  from qiskit.quantum_info import Statevector

  def oracle_101():
      qc = QuantumCircuit(3, name="O")
      qc.x(1)
      qc.h(2); qc.ccx(0, 1, 2); qc.h(2)   # CCZ on (0,1,2)
      qc.x(1)
      return qc

  def diffuser(n):
      qc = QuantumCircuit(n, name="D")
      qc.h(range(n)); qc.x(range(n))
      qc.h(n-1); qc.mcx(list(range(n-1)), n-1); qc.h(n-1)
      qc.x(range(n)); qc.h(range(n))
      return qc

  for k in range(5):
      qc = QuantumCircuit(3)
      qc.h(range(3))
      for _ in range(k):
          qc.compose(oracle_101(), inplace=True)
          qc.compose(diffuser(3), inplace=True)
      print(k, Statevector(qc).probabilities_dict().get('101', 0))
  ```

  Actual output:

  ```
  k=0  P('101')=0.125000
  k=1  P('101')=0.781250
  k=2  P('101')=0.945312
  k=3  P('101')=0.330078
  k=4  P('101')=0.012207
  ```

  matching the table exactly. Two iterations give 94.5% success from two oracle
  calls, against the `(N+1)/2 = 4.5` expected classical queries.

  </details>

- Show that applying Grover too many times *decreases* success probability

  <details><summary>Solution</summary>

  **Why it must happen.** Grover's operator `G` never leaves the two-dimensional
  real plane spanned by the marked state `|w⟩` and the uniform superposition of the
  unmarked states `|s'⟩`. On that plane `G` is a *rotation* by a fixed angle `2θ`,
  where `sin θ = √(M/N)`. So after `k` iterations the state is

  ```
  |ψ_k⟩ = sin((2k+1)θ)|w⟩ + cos((2k+1)θ)|s'⟩,   P_success(k) = sin²((2k+1)θ)
  ```

  A rotation is periodic, not convergent. `P` reaches 1 only when
  `(2k+1)θ = π/2`; past that point the state keeps rotating and the amplitude on
  `|w⟩` *falls*. `P(k)` is periodic in `k` with period `π/θ ≈ (π/2)√(N/M)`, and it
  returns to (almost) zero at `(2k+1)θ ≈ π`, i.e. at roughly twice `k_opt`.

  **Concretely for `N = 8, M = 1`** (`θ = 20.705°`), the numbers from the previous
  exercise continue:

  | k | `(2k+1)θ` | P |
  |---|---|---|
  | 2 | 103.5° | 0.9453 |
  | 3 | 144.9° | 0.3301 |
  | 4 | 186.3° | 0.0122 |
  | 5 | 227.8° | 0.5480 |
  | 6 | 269.2° | 0.9998 |

  One extra iteration past the optimum costs 61 points of success probability; two
  extra iterations leave you *worse off than not running Grover at all* (`0.0122`
  versus the `0.125` of a blind measurement). The near-perfect value at `k = 6` is
  the rotation coming back around, not progress.

  **Consequences for practice.**

  - You must know `M` to choose `k`. If `M` is unknown, use the
    Boyer–Brassard–Høyer–Tapp exponential-search schedule (pick `k` at random below
    a geometrically growing cap), which still costs `O(√(N/M))` queries.
  - `M > N/2` makes `θ > 45°` and even a single iteration overshoots; pad the search
    space with an extra qubit to halve `M/N` before amplifying.
  - Fixed-point amplitude amplification (Yoder–Low–Chuang) replaces the plain
    reflections with phase-modified ones so that `P` increases *monotonically* — at
    the cost of a constant factor in queries.

  </details>

- Implement the oracle for the satisfiability problem on 3 clauses, 3 variables

  <details><summary>Solution</summary>

  Take the 3-CNF formula

  ```
  F(x₀,x₁,x₂) = (x₀ ∨ x₁ ∨ ¬x₂) ∧ (¬x₀ ∨ x₁ ∨ x₂) ∧ (x₀ ∨ ¬x₁ ∨ x₂)
  ```

  **Oracle construction.** A clause is an OR, and quantum circuits build ANDs
  (multi-controlled X), so use De Morgan: `l₀ ∨ l₁ ∨ l₂ = ¬(¬l₀ ∧ ¬l₁ ∧ ¬l₂)`. For
  each clause, `X` the variables that appear *positively* (so that "all controls
  high" means "all literals false"), apply an `MCX` onto a clause ancilla, then `X`
  the ancilla to flip the polarity, then undo the variable `X`s. Finally `MCX` the
  three clause ancillas onto the output qubit.

  ```python
  from qiskit import QuantumCircuit, QuantumRegister

  clauses = [[(0,1),(1,1),(2,0)], [(0,0),(1,1),(2,1)], [(0,1),(1,0),(2,1)]]
  v = QuantumRegister(3,'v'); c = QuantumRegister(3,'c'); o = QuantumRegister(1,'o')
  qc = QuantumCircuit(v, c, o)
  for i, cl in enumerate(clauses):
      for var, pos in cl:
          if pos: qc.x(v[var])
      qc.mcx([v[var] for var, _ in cl], c[i])
      qc.x(c[i])
      for var, pos in cl:
          if pos: qc.x(v[var])
  qc.mcx(list(c), o[0])
  ```

  This needs `3` variable qubits, `3` clause ancillas and `1` output qubit. Running
  it on every basis state confirms the truth table:

  ```
  x=(0,0,0) f=1    x=(0,0,1) f=0    x=(0,1,0) f=0    x=(0,1,1) f=1
  x=(1,0,0) f=0    x=(1,0,1) f=1    x=(1,1,0) f=1    x=(1,1,1) f=1
  ```

  exactly the five satisfying assignments found by brute force. To turn this into a
  *phase* oracle for Grover, initialise `o` in `|−⟩` so the `MCX` kicks back a `−1`,
  and run the three clause blocks in reverse afterwards to uncompute the ancillas
  (otherwise the ancillas stay entangled with the variables and the diffuser's
  interference is destroyed).

  **The trap in this instance.** Three full-width 3-literal clauses each exclude
  exactly one of the eight assignments, so `M = 5` of `N = 8` — `sin θ = √(5/8)`
  gives `θ = 52.2°`, and *one* Grover iteration already overshoots:

  ```
  k=0 P=0.6250   k=1 P=0.1562   k=2 P=0.9766
  ```

  Amplitude amplification makes things worse before it makes them better. The
  standard repair is to pad: add one ancilla qubit in `|+⟩` and mark
  `F(x) ∧ (anc = 0)`, which halves `M/N` to `5/16`, `θ = 34.0°`, and now the
  textbook schedule works:

  ```
  k=0 P=0.3125   k=1 P=0.9570   k=2 P=0.0305
  ```

  **Scaling note.** For `m` clauses on `n` variables the oracle costs `m` ancillas
  and `2m + 1` multi-controlled gates, and each `MCX` on `w` controls costs
  `O(w)` Toffolis with `O(w)` extra ancillas. Grover then needs
  `O(√(2ⁿ/M))` oracle calls — a quadratic speedup over brute force, which is *not*
  enough to put SAT in polynomial time.

  </details>

---

### HHL Algorithm (Quantum Linear Systems)

**Problem:** Given Ax = b, find |x⟩ (quantum state proportional to solution)
**Classical:** O(N · κ · log(1/ε)) for N-dimensional system with condition number κ
**Quantum:** O(log(N) · κ² · log(1/ε)) — exponential in N when s-sparse and well-conditioned

**Key steps:**
1. Encode `|b⟩` in quantum state
2. Use QPE to estimate eigenvalues of A
3. Apply controlled rotation `|λ⟩ → (C/λ)|λ⟩` (inversion step)
4. Uncompute QPE
5. Measure ancilla in |1⟩; remaining state is proportional to `|x⟩`

**Caveats (important):**
- Input must be loaded efficiently (QRAM problem)
- Output is a quantum state, not the vector x itself
- Speedup evaporates if you need to read out all components

---

### Variational Quantum Eigensolver (VQE)

**Problem:** Find ground state energy of Hamiltonian H
**Approach:** Variational principle: `E₀ ≤ ⟨ψ(θ)|H|ψ(θ)⟩`

**Algorithm:**
1. Choose ansatz `|ψ(θ)⟩` (hardware-efficient or chemistry-inspired UCC)
2. Classically minimize: `θ* = argmin_θ ⟨ψ(θ)|H|ψ(θ)⟩`
3. Evaluate expectation value on quantum hardware via Pauli decomposition: `H = Σ hᵢ Pᵢ`

**Key challenges:**
- Barren plateaus: gradients vanish exponentially in system size
- Noise: NISQ hardware errors corrupt the expectation values
- Ansatz expressibility vs trainability trade-off

---

### QAOA (Quantum Approximate Optimization Algorithm)

**Problem:** Approximate solution to combinatorial optimization (MaxCut, TSP, etc.)
**Approach:** Alternating problem unitary `U_C(γ)` and mixing unitary `U_B(β)`

```
|ψ(γ,β)⟩ = U_B(βₚ) U_C(γₚ) ... U_B(β₁) U_C(γ₁) |+⟩^⊗n
```

**Approximation ratio:** Increases with circuit depth p; p → ∞ is exact
**Barrier:** No proven quantum advantage for QAOA over classical algorithms

---

## Module 3 — Query Complexity and Lower Bounds

**Objective:** Understand the theoretical framework for proving quantum speedups.

| Concept | Description |
|---|---|
| Query complexity | Count oracle calls, not total time |
| Decision tree complexity | Classical queries needed |
| Quantum query complexity | Quantum queries needed |
| Polynomial method | Lower bounds via low-degree polynomial approximation |
| Adversary method | Lower bounds via adversary arguments |
| Forrelation | Biggest possible separation: O(1) quantum vs Ω̃(√N) classical |

**Key results:**

| Problem | Classical | Quantum | Optimal? |
|---|---|---|---|
| Unstructured search | O(N) | O(√N) | Yes (BBBV lower bound) |
| OR function | Θ(N) | Θ(√N) | Yes |
| Collision finding | Θ(√N) randomized (birthday bound) | Θ(N^(1/3)) | Yes |
| Element distinctness | Θ(N) | Θ(N^(2/3)) | Yes (Ambainis quantum walk) |
| Graph connectivity | O(N²) | O(N^(3/2)) | Open |

**Exercises:**
- Apply the polynomial method to prove Grover is optimal for unstructured search

  <details><summary>Solution</summary>

  **Setup (Beals–Buhrman–Cleve–Mosca–de Wolf).** Let a quantum algorithm make `T`
  queries to a black box holding `x ∈ {0,1}^N`. After `T` queries every amplitude of
  the final state is a multilinear polynomial in `x₁,…,x_N` of degree at most `T`
  (each query multiplies amplitudes by one input bit at most once). The acceptance
  probability is a sum of squared moduli of those amplitudes, hence a real
  multilinear polynomial `p(x)` of degree at most `2T` with `0 ≤ p(x) ≤ 1`.

  For `OR_N` an algorithm that errs with probability `≤ 1/3` gives
  `p(0…0) ≤ 1/3` and `p(x) ≥ 2/3` whenever `|x| ≥ 1`.

  **Symmetrise (Minsky–Papert).** `OR` is symmetric, so average `p` over all
  permutations of the input: `q(k) = E_{|x|=k}[p(x)]` is a *univariate* real
  polynomial of degree `≤ deg p ≤ 2T` with

  ```
  0 ≤ q(k) ≤ 1  for k = 0,1,…,N,     q(0) ≤ 1/3,     q(k) ≥ 2/3 for k ≥ 1
  ```

  **Apply Markov's inequality.** By the mean value theorem there is a
  `ξ ∈ (0,1)` with `q'(ξ) = q(1) - q(0) ≥ 1/3`. Markov's brothers' inequality says
  a degree-`d` polynomial bounded by `B` in absolute value on an interval of length
  `L` satisfies `max|q'| ≤ 2d²B/L`. Here `L = N` and, by the Ehlich–Zeller bound, a
  degree-`d` polynomial bounded by 1 at all integers of `[0,N]` is bounded by `B = 2`
  on the whole interval as long as `d ≤ √N` — precisely the regime we are ruling
  out. Therefore

  ```
  1/3 ≤ max|q'| ≤ 2d²·2/N   ⟹   d² ≥ N/12   ⟹   d ≥ √(N/12)
  ```

  and since `d ≤ 2T`,

  ```
  T ≥ (1/2)√(N/12) = √N / (4√3) ≈ 0.144 √N = Ω(√N)
  ```

  Grover achieves `(π/4)√N ≈ 0.785√N`, so the polynomial method is tight up to the
  constant. (Tightening `B` and the endpoint analysis recovers the optimal constant;
  the point of the exercise is the `√N`.)

  **Numerical sanity check on the two ingredients.** Markov's bound is exactly
  attained by Chebyshev polynomials: for `T_d` on `[-1,1]`, `max|T_d| = 1` and
  `max|T_d'| = d²` (checked for `d = 2,3,5,10` giving `4, 9, 25, 100`); rescaled to
  `[0,100]` with `d = 5`, `max|q'| = 0.49998` against the predicted `2d²/N = 0.5`.

  **Why the method is the right tool.** It converts "how many queries" into "how
  fast can a bounded low-degree polynomial move", which is a completely classical
  approximation-theory question. Its limitation is that it lower-bounds *approximate
  degree*, and for some functions (notably element distinctness) the approximate
  degree is strictly smaller than the quantum query complexity — that is where the
  adversary method takes over.

  </details>

- Explain the BBBV theorem and what it rules out

  <details><summary>Solution</summary>

  **Statement.** Bennett, Bernstein, Brassard and Vazirani (1997) proved that
  relative to an oracle, `NP ⊄ BQP` — more concretely, any quantum algorithm that
  finds a marked item among `N` with bounded error must make `Ω(√N)` oracle queries.
  Grover's `O(√N)` is therefore optimal, and no black-box quantum algorithm can
  search exponentially faster.

  **The hybrid argument.** Run the algorithm with the all-zero oracle (no marked
  item). Let `|ψ_t⟩` be the state just before query `t`, and let

  ```
  m_i = Σ_{t=1}^{T} |⟨i|ψ_t⟩|²
  ```

  be the total "query mass" the algorithm ever places on index `i`. Since each
  `|ψ_t⟩` is normalised, `Σ_i m_i = T`, so by averaging there exists an index `i*`
  with `m_{i*} ≤ T/N`.

  Now switch to the oracle that marks only `i*`. A standard hybrid/telescoping bound
  says the final states differ by at most twice the total amplitude touched:

  ```
  ‖ |ψ_T^(i*)⟩ - |ψ_T^(0)⟩ ‖  ≤  2 Σ_t |⟨i*|ψ_t⟩|  ≤  2 √( T · Σ_t |⟨i*|ψ_t⟩|² )
                              =  2 √(T · m_{i*})  ≤  2T/√N
  ```

  using Cauchy–Schwarz for the middle step. To answer correctly in both worlds the
  two final states must be distinguishable with constant probability, which needs
  `2T/√N = Ω(1)`, i.e. `T = Ω(√N)`.

  **What it rules out.**

  - Any *black-box* quantum speedup for unstructured search better than quadratic.
    In particular you cannot brute-force a SAT instance's `2ⁿ` assignments in
    `poly(n)` time by treating the verifier as an oracle; Grover only takes you from
    `2ⁿ` to `2^(n/2)`.
  - The "try all branches in superposition and read off the right one" folk
    description of quantum computing: superposition alone buys nothing without
    interference that exploits structure.

  **What it does not rule out.**

  - `NP ⊆ BQP` in the real (non-relativised) world. The theorem is an *oracle*
    separation; it says only that a proof of `NP ⊆ BQP` cannot relativise.
  - Speedups that exploit problem structure. Shor's algorithm is exponentially fast
    precisely because the period of `a^x mod N` is algebraic structure, not a
    featureless database.
  - Better-than-quadratic advantage for *promise* problems, where the input is
    guaranteed to have structure — Forrelation reaches an `O(1)` versus
    `Ω̃(√N)` separation.

  </details>

- Prove that any quantum algorithm for PARITY requires Ω(N) queries

  <details><summary>Solution</summary>

  **Claim.** `Q₂(PARITY_N) = N/2` exactly: `N/2` queries suffice and `N/2` are
  necessary, so the quantum speedup over the classical `N` queries is a factor of
  two — no more.

  **Upper bound (why it is `N/2` and not `N`).** One query to the phase oracle
  computes the parity of *two* bits: run Deutsch's algorithm on `x_{2j}, x_{2j+1}`.
  So `N/2` queries yield all `N/2` pairwise parities, and their XOR is `PARITY(x)`.

  **Lower bound by the polynomial method.** As in the Grover exercise, a `T`-query
  algorithm's acceptance probability is a multilinear polynomial `p(x)` of degree
  `d ≤ 2T` with `|p(x) - PARITY(x)| ≤ 1/3` for all `x`.

  Symmetrise: `q(k) = E_{|x|=k}[p(x)]` is univariate of degree `≤ d`, and since
  `PARITY(x)` depends only on `|x| mod 2`,

  ```
  |q(k) - (k mod 2)| ≤ 1/3   for every integer k in [0, N]
  ```

  Therefore `q(k) - 1/2 ≥ 1/6 > 0` for odd `k` and `≤ -1/6 < 0` for even `k`. The
  values `k = 0,1,…,N` give `N+1` alternating signs, so `q(x) - 1/2` has at least
  `N` real roots in `(0, N)`. A non-zero polynomial with `N` roots has degree `≥ N`,
  hence

  ```
  N ≤ d ≤ 2T   ⟹   T ≥ N/2
  ```

  **Numerical confirmation.** Solving, by linear program, for the univariate
  polynomial of each degree that minimises `max_k |q(k) - (k mod 2)|` over
  `k = 0,…,N` gives a minimax error of exactly `1/2` — no better than a constant
  guess — for every degree below `N`, and exactly `0` at degree `N`:

  ```
  N=4:  deg0..deg3 -> 0.5000  |  deg4 -> 0.0000
  N=5:  deg0..deg4 -> 0.5000  |  deg5 -> 0.0000
  N=6:  deg0..deg5 -> 0.5000  |  deg6 -> 0.0000
  ```

  So the approximate degree of `PARITY` is `N`, with no gap at all between exact and
  approximate degree.

  **Why parity is the canonical "no speedup" example.** Its polynomial
  representation `Π(1-2xᵢ)` is maximally non-smooth: every input bit matters equally
  at every point, so there is no structure for interference to exploit. Together
  with Grover's `Θ(√N)` for OR this brackets the whole range of what query
  complexity can deliver for total Boolean functions — Beals et al. showed the
  classical and quantum query complexities of any total function are polynomially
  related, with the largest possible separation for total functions now known to be
  quartic.

  </details>

---

## Module 4 — Quantum Simulation Algorithms

**Objective:** Design circuits that simulate quantum Hamiltonians — arguably the most important application.

| Method | Concept | Error Scaling |
|---|---|---|
| Product formula (Trotter) | `e^(i(A+B)t) ≈ (e^(iAt/r)e^(iBt/r))^r` | O(t²/r) |
| Higher-order Trotter | Suzuki-Trotter 4th order etc. | O(t^(2k+1)/r^(2k)) |
| Qubitization | Encode H via block-encoding, walk operator | O(t · ‖H‖) |
| LCU (Linear Combination of Unitaries) | `H = Σ αᵢ Uᵢ`, use SELECT and PREPARE | O(‖α‖₁) |
| QSVT (Quantum Singular Value Transformation) | Unify all simulation methods | Optimal |

**Exercises:**
- Implement Trotterized evolution for the Ising model

  <details><summary>Solution</summary>

  **The model.** Transverse-field Ising chain on `n` sites, open boundary:

  ```
  H = -J Σ_(i=0)^(n-2) Z_i Z_(i+1)  -  h Σ_(i=0)^(n-1) X_i  =  H_ZZ + H_X
  ```

  The two groups do not commute, but each group is internally commuting, so a
  first-order Trotter step is exact within each group:

  ```
  e^(-iHt) ≈ [ e^(-i H_ZZ t/r) · e^(-i H_X t/r) ]^r
  ```

  **Circuit primitives.** `exp(+i J δ Z_i Z_j) = RZZ(-2Jδ)` on the pair, and
  `exp(+i h δ X_i) = RX(-2hδ)`. Each `RZZ` is `CX · RZ(angle) · CX`, so one step of
  an `n`-site chain costs `2(n-1)` CX gates and `n` single-qubit rotations.

  ```python
  import numpy as np
  from qiskit import QuantumCircuit
  from qiskit.quantum_info import SparsePauliOp, Statevector, state_fidelity
  from scipy.linalg import expm

  n, J, h, t = 3, 1.0, 0.8, 2.0
  H = SparsePauliOp.from_list(
      [("".join("Z" if k in (i, i+1) else "I" for k in range(n)), -J) for i in range(n-1)]
      + [("".join("X" if k == i else "I" for k in range(n)), -h) for i in range(n)])

  def trotter_step(dt):
      qc = QuantumCircuit(n)
      for i in range(n-1):
          qc.rzz(-2*J*dt, i, i+1)
      for i in range(n):
          qc.rx(-2*h*dt, i)
      return qc

  exact = expm(-1j*H.to_matrix()*t) @ Statevector.from_label("0"*n).data
  for r in [1, 2, 4, 8, 16, 32, 64]:
      qc = QuantumCircuit(n)
      for _ in range(r):
          qc.compose(trotter_step(t/r), inplace=True)
      psi = Statevector.from_label("0"*n).evolve(qc)
      print(r, 1 - state_fidelity(psi, exact))
  ```

  Actual output for `n = 3`, `J = 1`, `h = 0.8`, `t = 2`:

  ```
     r   infidelity   ratio
     1    6.910e-01
     2    9.110e-01    0.76
     4    1.167e-01    7.81
     8    1.852e-02    6.30
    16    3.966e-03    4.67
    32    9.430e-04    4.21
    64    2.317e-04    4.07
  ```

  **Reading the numbers.** Small `r` is outside the asymptotic regime (`r = 1, 2`
  are nowhere near the target state at all). From `r = 16` on, the ratio settles at
  `4` per doubling of `r`, i.e. infidelity `∝ 1/r²`. That is consistent with the
  advertised `O(t²/r)` *state* error: infidelity is the square of the state-vector
  error, so `‖Δψ‖ ∝ 1/r` as predicted.

  One step transpiled to `{cx, rz, sx, x}` gives `OrderedDict({'rz': 11, 'sx': 6,
  'cx': 4})` — 4 CX for the two `RZZ` gates on a 3-site chain, so the whole `r = 32`
  circuit is 128 CX for a `4 × 10⁻⁴` infidelity.

  **Extensions worth doing.** Use the second-order (symmetric) formula
  `e^(-iH_X δ/2) e^(-iH_ZZ δ) e^(-iH_X δ/2)`; the error drops to `O(t³/r²)` for the
  same CX count, because the `RX` layers of neighbouring steps merge.

  </details>

- Estimate gate count for simulating H₂ molecule to chemical accuracy

  <details><summary>Solution</summary>

  **Target.** "Chemical accuracy" is 1 kcal/mol
  `= 4.184 / 2625.4995 Ha = 1.594 × 10⁻³ Ha` (1.6 mHa).

  **Step 1 — the Hamiltonian.** H₂ in the STO-3G minimal basis has two spatial
  orbitals (`σ_g`, `σ_u`), hence four spin-orbitals and, under Jordan–Wigner, four
  qubits. Computing the integrals from the STO-3G contraction
  (`α = ζ²·{0.109818, 0.405771, 2.22766}`, `ζ = 1.24`) at `R = 0.735 Å`, forming the
  symmetry-fixed MOs `σ_g,u = (φ₁ ± φ₂)/√(2(1±S))`, and diagonalising the full CI
  matrix reproduces the textbook value:

  ```
  E_nuc = 0.719969 Ha
  FCI total ground energy = -1.1373072 Ha     (textbook STO-3G value -1.1373 Ha)
  ```

  Decomposing that 16×16 matrix into Paulis gives **exactly 15 terms**:

  ```
  IIII -0.090578   IIIZ -0.225755   IIZI -0.225755   IZII +0.172183
  ZIII +0.172183   IIZZ +0.174645   ZZII +0.168928   ZIIZ +0.166146
  IZZI +0.166146   IZIZ +0.120913   ZIZI +0.120913
  XXYY -0.045233   XYYX +0.045233   YXXY +0.045233   YYXX -0.045233
  ```

  four single-`Z` terms, six `ZZ` terms, four weight-4 "double excitation" terms,
  and the identity.

  **Step 2 — Trotter step size.** Build the first-order product formula
  `U(δ) = Π_j e^(-i c_j P_j δ)` and read the ground eigenphase back out. Measured
  error in the recovered energy, as a function of step size:

  | δ (a.u.) | `|E_Trot - E₀|` (Ha) |
  |---|---|
  | 1.00 | 4.45 × 10⁻³ |
  | 0.80 | 2.79 × 10⁻³ |
  | 0.70 | 2.12 × 10⁻³ |
  | 0.60 | 1.55 × 10⁻³ |
  | 0.50 | 1.07 × 10⁻³ |
  | 0.25 | 2.65 × 10⁻⁴ |

  So `δ ≈ 0.6` a.u. already reaches chemical accuracy. Two things are worth noting.
  First, the error depends *only* on `δ`, not on the total simulated time — checked
  explicitly at `t = 1, 2, 4, 8, 16` with identical results, because Trotterisation
  is exactly the statement that you are evolving under an effective Hamiltonian
  `H_eff(δ)`. Second, the error scales as `δ²`, not the `δ` a first-order formula
  would suggest: every Pauli term here contains an *even* number of `Y`s, so every
  `H_j` is a real symmetric matrix, the leading BCH correction
  `(δ/2) Σ_(i<j) (-i)[H_i, H_j]` is purely imaginary-antisymmetric, and its
  expectation in the real ground state vanishes. The first non-zero contribution is
  second order in perturbation theory.

  **Step 3 — total gate count.** For QPE with `m` ancilla bits at base time
  `t₀ = 1` a.u., the energy resolution is `2π/2^m`. Chemical accuracy needs
  `2π/2^m ≤ 1.6 × 10⁻³`, i.e. `m = 12` (resolution `1.53 × 10⁻³ Ha`), and the total
  simulated time is `t₀(2^m − 1) = 4095` a.u. At `δ = 0.6` that is **6825 Trotter
  steps**.

  Per step, counting a CX ladder for each Pauli exponential:

  | term type | count | CX each | CX total |
  |---|---|---|---|
  | weight-1 `Z` | 4 | 0 | 0 |
  | weight-2 `ZZ` | 6 | 2 | 12 |
  | weight-4 `XXYY`-type | 4 | 6 | 24 |

  36 CX, 14 `RZ` and 32 basis-change single-qubit gates per step, giving

  ```
  6825 × 36 ≈ 2.5 × 10⁵ CX gates, on 4 + 12 = 16 qubits
  ```

  **Sanity check against reality.** Each CX must then succeed: at a `10⁻³` two-qubit
  error rate the expected fidelity of `2.5 × 10⁵` CX gates is `e^(-250) ≈ 0`. This is
  the whole argument for (a) error correction and (b) VQE — the variational route
  replaces one deep coherent circuit with many shallow ones and pays in measurement
  shots instead of coherence. Good optimisations trim the constant substantially:
  the four weight-4 terms share a magnitude and can be synthesised as a single
  4-qubit "double excitation" rotation, tapering symmetries reduces 4 qubits to 2,
  and a second-order product formula buys a larger `δ` for the same accuracy.

  </details>

- Explain why LCU achieves better scaling than first-order Trotter

  <details><summary>Solution</summary>

  **The short answer.** Trotter's cost is *polynomial* in `1/ε`; LCU's is
  *logarithmic*. Trotter approximates `e^(-iHt)` by a product whose error is a power
  law in the step size, while LCU approximates it by truncating a series whose
  remainder falls super-exponentially in the truncation order.

  **Trotter.** First-order: `‖e^(-i(A+B)t) - (e^(-iAt/r)e^(-iBt/r))^r‖ ≤ t²‖[A,B]‖/2r`.
  Fixing an error budget `ε` forces `r = O(t²/ε)`, so the gate count grows *linearly
  in `1/ε`*. A `2k`-th order Suzuki formula improves this to
  `r = O(t^(1+1/2k)/ε^(1/2k))`, which approaches `O(t)` in the limit but with a
  `5^k` prefactor, so `1/ε` never disappears entirely.

  **LCU.** Write `H = Σ_(l=1)^{L} α_l U_l` with `U_l` unitary and `α_l > 0`, and put
  `‖α‖₁ = Σ_l α_l`. Over a short segment, truncate the Taylor series

  ```
  e^(-iHt) ≈ Σ_(k=0)^{K} (-i t)^k H^k / k!
           = Σ_(k=0)^{K} Σ_(l₁…l_k) (-i t)^k α_{l₁}…α_{l_k} / k! · U_{l₁}…U_{l_k}
  ```

  which is itself a linear combination of unitaries, implemented with PREPARE (load
  `√(coefficients)` into an ancilla register), SELECT (apply the indexed product),
  PREPARE†, and oblivious amplitude amplification to remove the sub-normalisation.
  The truncation error is the tail of an exponential series:

  ```
  error ≤ Σ_(k>K) (‖α‖₁ t)^k / k!
  ```

  Choosing segments with `‖α‖₁ t_seg = ln 2` makes the tail `≤ ε` for
  `K = O( log(1/ε) / log log(1/ε) )`. Total cost
  `O( ‖α‖₁ t · log(1/ε)/log log(1/ε) )` — *additively* logarithmic in the precision
  and linear in time, which is optimal up to the log factor (no-fast-forwarding
  bounds `Ω(t)`).

  **Numbers.** For the 3-site Ising chain of the previous exercises
  (`‖α‖₁ = 4.4`, `t = 2`), comparing the first-order Trotter steps needed against
  the segmented-Taylor order needed, with cost counted as "term exponentials
  applied":

  | target ε | Trotter `r` | Trotter cost | LCU `K` | segments | LCU cost |
  |---|---|---|---|---|---|
  | 10⁻² | 138 | 690 | 4 | 13 | 260 |
  | 10⁻³ | 1 484 | 7 420 | 5 | 13 | 325 |
  | 10⁻⁴ | 12 126 | 60 630 | 6 | 13 | 390 |
  | 10⁻⁶ | 1 363 816 | 6 819 080 | 7 | 13 | 455 |
  | 10⁻⁸ | 1 251 075 352 | 6 255 376 760 | 9 | 13 | 585 |

  Trotter's cost rises by a factor of about ten per decade of precision; the LCU
  cost rises by *one or two units of `K`* per two decades. Every decade of extra
  accuracy is essentially free for LCU and ten times more expensive for Trotter.

  **The caveats that keep Trotter alive.** LCU needs ancilla registers of size
  `O(K log L)`, a coherent PREPARE over all `L` coefficients, and amplitude
  amplification, so its *constant factors and qubit overhead* are much larger.
  Trotter needs no ancillas at all, exploits locality and commuting groups
  automatically, and — as recent tighter commutator-based error bounds show — is
  often better than its worst-case scaling suggests on physically local
  Hamiltonians. LCU and qubitization win when high precision is the binding
  constraint (chemistry, fault-tolerant regimes); Trotter wins on NISQ hardware,
  where qubits are scarcer than precision.

  </details>

---

## Module 5 — Algorithm Design Workflow

**Objective:** Develop a systematic process for designing new quantum algorithms.

**Step 1 — Problem formulation**
- Is there a hidden algebraic structure? (period, subgroup, symmetry)
- Can the problem be cast as: finding a marked element? estimating a phase? optimizing a function?
- What is the classical complexity?

**Step 2 — Choose a technique**
- Algebraic structure → QFT / hidden subgroup
- Search / optimization → Grover / amplitude amplification
- Eigenvalue problem → QPE
- Continuous optimization / chemistry → VQE / QAOA
- Simulation → Trotterization / qubitization

**Step 3 — Oracle design**
- What does the oracle compute?
- How many ancilla qubits are needed?
- Can the oracle be uncomputed without measuring?

**Step 4 — Complexity analysis**
- Query complexity (oracle calls)
- Gate complexity (total gates)
- Space complexity (qubit count)
- Error analysis (how does precision affect gate count?)

**Step 5 — Lower bound check**
- Is there a matching lower bound?
- Can you prove your algorithm is optimal?

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Quantum Computation and Quantum Information* Ch.5-6 — Nielsen & Chuang | Textbook | Canonical algorithms |
| Childs' lecture notes on quantum algorithms | Notes | Free, rigorous, current |
| Montanaro "Quantum algorithms: an overview" (2016) | Survey | Comprehensive classification |
| *Quantum Algorithm Zoo* — Jordan | Website | Catalog of all known algorithms |
| Scott Aaronson's complexity zoo | Website | Complexity class relationships |

---

## Progression Checkpoints

- [ ] Implement Deutsch-Jozsa, Grover, Shor, and QFT at the circuit level

  <details><summary>Solution</summary>

  A complete answer is four working circuits plus the one sentence that explains
  each.

  - **Deutsch–Jozsa** (`n+1` qubits): `H` on all, `X` then `H` on the ancilla, the
    oracle `U_f|x⟩|y⟩ = |x⟩|y ⊕ f(x)⟩`, `H` on the query register, measure. The
    sentence: the ancilla in `|−⟩` converts `U_f` into the phase `(-1)^f(x)`, and the
    final `H⊗ⁿ` makes the amplitude of `|0…0⟩` equal to `(1/2ⁿ)Σ_x (-1)^f(x)`, which
    is `±1` for constant and exactly `0` for balanced.
  - **QFT** (`n` qubits): for each qubit `j`, `H` then controlled-`P(π/2^(k))` from
    each later qubit, finishing with the bit-reversal swaps. `O(n²)` gates. Check
    your implementation against `qiskit.circuit.library.QFTGate` with
    `Operator(...).equiv(...)`.
  - **Grover**: uniform superposition, then `k = round((π/4)√(N/M) - 1/2)`
    repetitions of phase oracle + diffuser `2|s⟩⟨s| - I`.
  - **Shor**: the classical wrapper (strip even numbers and prime powers, pick `a`,
    `gcd` check), then QPE on `U|y⟩ = |ay mod N⟩` with `2n+1` counting qubits, then
    continued fractions and the `gcd(a^(r/2) ± 1, N)` extraction.

  You are done when all four run end-to-end on a simulator and you can state each
  one's query/gate complexity without looking it up.

  </details>

- [ ] Derive the Grover iteration count and explain what happens past the optimal

  <details><summary>Solution</summary>

  **Derivation.** Write `|s⟩ = sin θ |w⟩ + cos θ |s'⟩` with `sin θ = √(M/N)`, where
  `|w⟩` is the normalised superposition of marked states and `|s'⟩` of unmarked ones.
  The oracle is a reflection about `|s'⟩`; the diffuser is a reflection about `|s⟩`.
  The product of two reflections in a plane is a rotation by twice the angle between
  their axes, i.e. by `2θ`. After `k` iterations the angle from `|s'⟩` is
  `(2k+1)θ`, so

  ```
  P_success(k) = sin²((2k+1)θ)
  ```

  Maximising means `(2k+1)θ = π/2`, i.e. `k* = π/(4θ) - 1/2`. For `M ≪ N`,
  `θ ≈ √(M/N)`, giving `k ≈ (π/4)√(N/M)`. Round to the nearest integer; the rounding
  error costs at most `sin²(θ) = M/N` in success probability.

  **Past the optimum.** `G` is a rotation, so it keeps turning. `P(k)` is periodic
  with period `π/θ` in `k`, falls back toward zero at `(2k+1)θ ≈ π`, and oscillates
  forever. For `N = 8, M = 1` the sequence is
  `0.125, 0.781, 0.945, 0.330, 0.012, 0.548, 1.000, …` — two iterations too many is
  worse than never running the algorithm.

  You can check yourself on the corollaries: why you need to know `M` in advance,
  why `M > N/2` breaks the schedule, and what BBHT and fixed-point amplitude
  amplification do about it.

  </details>

- [ ] Use QPE to estimate an eigenvalue to 3 bits of precision

  <details><summary>Solution</summary>

  Three ancillas resolve the phase to `2⁻³ = 1/8`. Take `U = P(2πφ)` with eigenstate
  `|1⟩`, so the answer is known in advance and you can grade yourself.

  ```python
  import numpy as np
  from qiskit import QuantumCircuit
  from qiskit.circuit.library import QFTGate, PhaseGate
  from qiskit.quantum_info import Statevector

  def qpe(phi, t=3):
      qc = QuantumCircuit(t+1)
      qc.x(t)                       # |u> = |1>
      qc.h(range(t))
      for j in range(t):            # controlled-U^(2^j)
          qc.append(PhaseGate(2*np.pi*phi*2**j).control(1), [j, t])
      qc.append(QFTGate(t).inverse(), range(t))
      return qc

  for phi in (1/8, 3/8, 0.3):
      probs = Statevector(qpe(phi)).probabilities_dict(range(3))
      print(phi, sorted(probs.items(), key=lambda kv: -kv[1])[:2])
  ```

  Real output:

  ```
  phi=0.125: '001'->1.0000 (estimate 1/8)   next 0.0000
  phi=0.375: '011'->1.0000 (estimate 3/8)   next 0.0000
  phi=0.300: '010'->0.5775 (estimate 2/8)   '011'->0.2593 (estimate 3/8)
  ```

  The two checks that matter. **Exact case**: when `φ` is a 3-bit binary fraction the
  inverse QFT lands on one basis state with probability 1. **Inexact case**:
  `φ = 0.3` is not representable, so the distribution peaks on the two nearest
  grid points `2/8` and `3/8`; the probability of the closest one is `0.5775`,
  comfortably above the `4/π² ≈ 0.405` worst-case guarantee.

  Also confirm you can read the register: Qiskit is little-endian, so the key
  `'010'` is `q₂q₁q₀ = 010 = 2`, giving `φ̂ = 2/8`, not `0/8`.

  </details>

- [ ] Apply the polynomial method to a lower bound argument

  <details><summary>Solution</summary>

  A good self-check is to reproduce the three-step template on a function you have
  not seen worked out, for example `AND_N` or `MAJORITY`:

  1. **Degree bound.** A `T`-query quantum algorithm's acceptance probability is a
     real multilinear polynomial in the input bits of degree `≤ 2T`, taking values
     in `[0,1]`. (Each query can multiply amplitudes by at most one input bit;
     probabilities are amplitudes squared.)
  2. **Symmetrise.** If the function is symmetric, average over the `N!` input
     permutations to get a *univariate* `q(k)` of no larger degree, with
     `|q(k) - f(k)| ≤ 1/3` for every integer `k` in `[0, N]`.
  3. **Bound the degree from below.** Use the shape of `q`: either an alternation
     argument (counting sign changes forces roots — this gives `deg ≥ N` for
     `PARITY`) or Markov's brothers' inequality (a bounded polynomial cannot have a
     large derivative unless its degree is large — this gives `deg = Ω(√N)` for `OR`
     and hence Grover's optimality).

  Then translate back: `2T ≥ deg`, so `T = Ω(deg/2)`.

  You should also be able to state the method's limits: it bounds *approximate
  degree*, which for some functions (element distinctness, and the collision
  problem before Kutin's tighter analysis) is strictly below the true quantum query
  complexity — the adversary method is the tool for those.

  </details>

- [ ] Design a Trotterized Hamiltonian simulation for a simple spin model

  <details><summary>Solution</summary>

  A complete design names five things. Using the transverse-field Ising chain as the
  worked example:

  1. **Hamiltonian and splitting.** `H = -J Σ Z_iZ_(i+1) - h Σ X_i`, split into the
     two internally-commuting groups `H_ZZ` and `H_X`.
  2. **Step circuit.** `RZZ(-2Jδ)` on each bond (`CX · RZ · CX`) followed by
     `RX(-2hδ)` on each site: `2(n-1)` CX and `n` single-qubit rotations per step.
  3. **Order and step count.** First order gives state error `O(t²/r)`, so
     `r = O(t²/ε)`; the symmetric second-order formula
     `e^(-iH_X δ/2) e^(-iH_ZZ δ) e^(-iH_X δ/2)` gives `O(t³/r²)` at essentially the
     same gate count, because adjacent half-steps merge.
  4. **Validation.** Compare against `expm(-iHt)` on 3–4 sites and confirm the
     infidelity falls by `4×` per doubling of `r` once you are in the asymptotic
     regime. (Measured: `3.97e-3, 9.43e-4, 2.32e-4` for `r = 16, 32, 64`.)
  5. **An observable to plot.** Time-dependent `⟨Z₀(t)⟩` or the domain-wall density,
     which is what makes the simulation physics rather than a norm calculation.

  If you can also state what changes for a Heisenberg chain (three non-commuting
  groups `XX`, `YY`, `ZZ`, each still internally commuting on alternating bonds) you
  have the transferable version of the skill.

  </details>

- [ ] Formulate a new problem and identify which algorithmic technique applies

  <details><summary>Solution</summary>

  The point of this checkpoint is the *diagnostic*, not any one answer. Run any
  candidate problem through Module 5's questions and see which technique the answer
  selects:

  | If the problem is… | …the technique is | …and the speedup is |
  |---|---|---|
  | hidden periodicity or a hidden abelian subgroup | QFT / hidden-subgroup | exponential |
  | "find `x` with `f(x) = 1`" in an unstructured domain | Grover / amplitude amplification | quadratic, and provably no more |
  | estimating an eigenvalue, an overlap, or a phase | QPE | exponential in the precision bits |
  | an expectation value of a `poly(n)`-term Hamiltonian, on NISQ hardware | VQE / QAOA | heuristic, unproven |
  | time evolution of a local Hamiltonian | Trotter / LCU / qubitization | exponential in system size |
  | counting or averaging | amplitude estimation | quadratic in the shot count |

  A worked example of the right shape: *given a sparse graph, decide whether it has
  a triangle*. Classical: `O(n^2.37)` by matrix multiplication. Cast as search over
  `O(n³)` candidate triples → Grover gives `O(n^1.5)` queries; cast as an element
  distinctness–style quantum walk gives `O(n^1.3)`. Then the lower-bound check: the
  best known lower bound is `Ω(n)`, so the problem is *open* — which is itself the
  correct conclusion and worth being comfortable stating.

  A red flag to internalise: if your answer is "load the data into a quantum state
  and search it", ask where the data comes from. Any algorithm whose input must be
  loaded from classical memory pays `Ω(N)` to load it, which usually cancels the
  speedup — the QRAM caveat that sinks most naive HHL applications.

  </details>

