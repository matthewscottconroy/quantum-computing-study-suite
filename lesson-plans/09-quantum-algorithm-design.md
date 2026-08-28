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
- Show why the period r satisfies `gcd(a^(r/2)−1, N) > 1` with probability ≥ 1/2
- Estimate the number of qubits needed to factor a 2048-bit RSA key

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
- Show that applying Grover too many times *decreases* success probability
- Implement the oracle for the satisfiability problem on 3 clauses, 3 variables

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
- Explain the BBBV theorem and what it rules out
- Prove that any quantum algorithm for PARITY requires Ω(N) queries

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
- Estimate gate count for simulating H₂ molecule to chemical accuracy
- Explain why LCU achieves better scaling than first-order Trotter

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
- [ ] Derive the Grover iteration count and explain what happens past the optimal
- [ ] Use QPE to estimate an eigenvalue to 3 bits of precision
- [ ] Apply the polynomial method to a lower bound argument
- [ ] Design a Trotterized Hamiltonian simulation for a simple spin model
- [ ] Formulate a new problem and identify which algorithmic technique applies
