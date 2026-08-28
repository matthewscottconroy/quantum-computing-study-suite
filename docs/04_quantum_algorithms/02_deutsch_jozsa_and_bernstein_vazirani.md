# Deutsch-Jozsa and Bernstein-Vazirani

> **Prerequisites**: 04_quantum_algorithms/01_quantum_parallelism_and_interference.md, 03_quantum_gates_and_circuits/01_single_qubit_gates.md and 02_multi_qubit_gates.md  
> **Connects to**: Simon's problem (structural generalization), Grover search (oracle model), quantum complexity theory (query complexity separations)

## Overview

The Deutsch-Jozsa algorithm (1992) and the Bernstein-Vazirani algorithm (1993) are historically the first problems where quantum computers were proven to be provably more efficient than classical computers. They are pedagogically essential because they demonstrate the core quantum algorithmic technique — query-then-interfere — in its simplest form, with clean proofs of both correctness and classical hardness.

Neither algorithm solves a problem of immediate practical importance. Deutsch-Jozsa asks whether a function is constant or balanced — a toy problem. Bernstein-Vazirani finds a hidden linear function — useful mainly for its elegant structure. Their value is theoretical: they prove quantum speedups exist, demonstrate interference as the mechanism, and establish the query complexity framework for proving hardness.

Simon's problem (also covered here) is the structural generalization that led directly to Shor's algorithm. Simon's period-finding algorithm processes a function with a hidden period structure using `O(n)` quantum queries where classically `Ω(2^{n/2})` queries are needed — an exponential quantum speedup. The key ideas in Simon's algorithm (finding a hidden subgroup structure via Hadamard + phase kickback + Fourier analysis) are precisely the ideas in Shor's algorithm for integer factoring.

## Deutsch's Problem

### The Problem

**Deutsch's problem** (1985): Given a function `f: {0,1} → {0,1}`, is `f` *constant* (same output for both inputs: `f(0)=f(1)`) or *balanced* (different outputs: `f(0) ≠ f(1)`)?

There are 4 possible functions:
- Constant-0: `f(0)=f(1)=0`
- Constant-1: `f(0)=f(1)=1`
- Identity: `f(0)=0, f(1)=1` (balanced)
- NOT: `f(0)=1, f(1)=0` (balanced)

**Classically**: You must evaluate `f(0)` and `f(1)` and compare — 2 queries. In the worst case, 2 queries are needed (if the first query gives the same value for both constant functions).

**Quantum**: Deutsch showed 1 quantum query suffices, with certainty.

### The Algorithm

**Setup**: One input qubit `|x⟩`, one ancilla qubit `|b⟩`. Oracle: `O_f|x,b⟩ = |x, b⊕f(x)⟩`.

**Circuit**:
1. Initialize: `|0⟩|1⟩`
2. Apply `H⊗H`: `|+⟩|−⟩ = [(|0⟩+|1⟩)/√2][(|0⟩-|1⟩)/√2]`
3. Apply `O_f`: phase kickback gives `[(-1)^{f(0)}|0⟩ + (-1)^{f(1)}|1⟩]/√2 · |−⟩`
4. Apply `H` to first qubit (not second): get result and measure

**After step 3**: Using phase kickback `O_f|x⟩|−⟩ = (-1)^{f(x)}|x⟩|−⟩`:

$$\frac{(-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle}{\sqrt{2}} \cdot |{-}\rangle = (-1)^{f(0)}\frac{|0\rangle + (-1)^{f(0)\oplus f(1)}|1\rangle}{\sqrt{2}} \cdot |{-}\rangle$$

**After step 4** (applying `H` to first qubit):

If `f(0) ⊕ f(1) = 0` (constant): `(|0⟩ + |1⟩)/√2 → H → |0⟩`. Measure 0.

If `f(0) ⊕ f(1) = 1` (balanced): `(|0⟩ - |1⟩)/√2 → H → |1⟩`. Measure 1.

**Result**: Measure 0 iff `f` is constant. 1 iff balanced. Deterministic with 1 query.

**Why this works**: The two cases — constant vs. balanced — differ by a relative phase of `(-1)^{f(0)⊕f(1)} = ±1` in the superposition. The Hadamard at the end converts this relative phase difference into a measurable amplitude difference. Constructive interference at `|0⟩` for constant; destructive for balanced.

## Deutsch-Jozsa Algorithm

### The Generalization

**Deutsch-Jozsa problem**: Given `f: {0,1}ⁿ → {0,1}`, promised that `f` is either:
- **Constant**: same output for all inputs (`f(x) = 0` for all `x`, or `f(x) = 1` for all `x`)
- **Balanced**: exactly half the inputs give 0, half give 1

Determine which case.

**Classical complexity**: In the worst case (deterministic), you might check `2^{n-1}` inputs and all give the same answer before finding a disagreement. Worst case: `2^{n-1}+1` queries.

**Randomized classical**: With `k` random samples, the probability of all agreeing by chance when the function is balanced is `≤ (1/2)^{k-1}`. So `O(n)` samples give error `≤ 2^{-(n-1)}`. So classically, `O(n)` samples suffice with high probability. **This is the key point**: classically with randomization, the problem is easy!

**Quantum**: 1 query, zero error.

The Deutsch-Jozsa algorithm demonstrates an **exact** quantum speedup over deterministic classical algorithms, but only a constant-factor speedup over randomized classical algorithms. Its real significance is pedagogical, not practical.

### The Algorithm

**Setup**: `n` input qubits + 1 ancilla.

1. Initialize: `|0⟩^n|1⟩`
2. Apply `H^{⊗n}⊗H`: `(1/√2ⁿ)Σ_x|x⟩|−⟩`
3. Apply oracle `O_f`: phase kickback gives `(1/√2ⁿ)Σ_x (-1)^{f(x)}|x⟩|−⟩`
4. Apply `H^{⊗n}` to input register
5. Measure input register; output 0 iff all bits are 0

**After step 4**: Using `H^{⊗n}|x⟩ = (1/√2ⁿ)Σ_y(-1)^{x·y}|y⟩`:

$$H^{\otimes n}\left[\frac{1}{\sqrt{2^n}}\sum_x (-1)^{f(x)}|x\rangle\right] = \frac{1}{2^n}\sum_y \left[\sum_x(-1)^{f(x)+x\cdot y}\right]|y\rangle$$

**Amplitude of `|0⟩^n = |0...0⟩`** (the all-zeros string, where `x·y = 0` for all `x`):

$$\text{amp}(0^n) = \frac{1}{2^n}\sum_x (-1)^{f(x)}$$

- **If `f` is constant-0**: `Σ_x (-1)^{f(x)} = Σ_x 1 = 2ⁿ`. Amplitude = 1. Probability = 1.
- **If `f` is constant-1**: `Σ_x (-1)^{f(x)} = Σ_x (-1) = -2ⁿ`. Amplitude = -1. Probability = 1.
- **If `f` is balanced**: exactly `2^{n-1}` terms are `+1` and `2^{n-1}` are `-1`. Sum = 0. Probability = 0.

**Conclusion**: Measuring `|0⟩^n` (all zeros) occurs with probability 1 iff `f` is constant; probability 0 if `f` is balanced. One query, zero error.

**Interference analysis**: The Hadamard transform at the end performs a Fourier-like analysis of the function. For constant `f`, all phases `(-1)^{f(x)}` are equal, so their interference (the sum) is maximally constructive at `y = 0...0`. For balanced `f`, the phases are exactly split `+1/-1`, so their sum is zero — perfect destructive interference at `y = 0...0`.

## Bernstein-Vazirani Algorithm

### The Problem

**Bernstein-Vazirani problem** (1993): Given a function `f: {0,1}ⁿ → {0,1}` of the form `f(x) = s·x mod 2` for an unknown hidden string `s ∈ {0,1}ⁿ`, find `s`.

Here `s·x = Σᵢ sᵢxᵢ mod 2` is the bitwise dot product (parity of the bitwise AND).

**Classical complexity**: To find all `n` bits of `s`, we need `n` queries. Query `f` on `eᵢ = 0...010...0` (the standard basis vector with 1 in position `i`): `f(eᵢ) = s·eᵢ = sᵢ`. Each query reveals one bit of `s`.

**Quantum**: 1 query suffices to find all `n` bits.

### The Algorithm

The circuit is identical to Deutsch-Jozsa:

1. Initialize: `|0⟩^n|1⟩`
2. Apply `H^{⊗n}⊗H`: `(1/√2ⁿ)Σ_x|x⟩|−⟩`
3. Apply oracle `O_f`: `(1/√2ⁿ)Σ_x(-1)^{s·x}|x⟩|−⟩`
4. Apply `H^{⊗n}` to input register
5. Measure — the result is `s` with certainty

**After step 4**:

$$H^{\otimes n}\left[\frac{1}{\sqrt{2^n}}\sum_x(-1)^{s\cdot x}|x\rangle\right] = \frac{1}{2^n}\sum_y\left[\sum_x(-1)^{s\cdot x + x\cdot y}\right]|y\rangle = \frac{1}{2^n}\sum_y\left[\sum_x(-1)^{x\cdot(s\oplus y)}\right]|y\rangle$$

The inner sum `Σ_x (-1)^{x·z}` equals `2ⁿ` if `z = 0` and `0` otherwise (this is the orthogonality of characters of `(ℤ/2)ⁿ`).

So the amplitude of `|y⟩` is:
$$\frac{1}{2^n} \cdot 2^n \cdot [y = s] = \begin{cases} 1 & \text{if } y = s \\ 0 & \text{otherwise}\end{cases}$$

After the final `H^{⊗n}`, the state is exactly `|s⟩`. Measuring gives `s` with probability 1.

**Classical vs quantum**:
- Classical: `n` queries to `f` (one per bit of `s`)
- Quantum: 1 query to `f` (finds all `n` bits simultaneously)

**Why this works**: The oracle encodes `s` as a "Fourier phase" in the amplitude array `{(-1)^{s·x}}`. The Hadamard transform (a Fourier transform on `(ℤ/2)ⁿ`) decodes it perfectly in one step. With 1 query and `n` bits of output, we achieve an `n`-fold speedup in query complexity.

## Simon's Problem

### The Problem

**Simon's problem** (1994): Given `f: {0,1}ⁿ → {0,1}ⁿ` promised to be **2-to-1** with a hidden period `s ∈ {0,1}ⁿ` (with `s ≠ 0^n`) satisfying:

$$f(x) = f(y) \iff x \oplus y \in \{0^n, s\}$$

That is, `f` is constant on pairs `{x, x⊕s}`. Find `s`.

**Classical complexity**: `Ω(2^{n/2})` queries (by birthday paradox: need to find two inputs with the same output, expected after `~√(2ⁿ) = 2^{n/2}` random queries).

**Quantum complexity**: `O(n)` queries and `O(n²)` classical post-processing.

### The Algorithm

**Quantum part**:

1. Initialize: `|0⟩^n|0⟩^n`
2. Apply `H^{⊗n}⊗I`: `(1/√2ⁿ)Σ_x|x⟩|0⟩^n`
3. Apply oracle: `(1/√2ⁿ)Σ_x|x⟩|f(x)⟩`
4. Measure the second register, obtaining some value `f(x₀)`

After step 4: the first register collapses to the superposition of the **two preimages** of `f(x₀)`:

$$\frac{|x_0\rangle + |x_0 \oplus s\rangle}{\sqrt{2}}$$

5. Apply `H^{⊗n}` to the first register

Using `H^{⊗n}|x⟩ = (1/√2ⁿ)Σ_y(-1)^{x·y}|y⟩`:

$$H^{\otimes n}\frac{|x_0\rangle + |x_0\oplus s\rangle}{\sqrt{2}} = \frac{1}{\sqrt{2^{n+1}}}\sum_y (-1)^{x_0\cdot y}(1 + (-1)^{s\cdot y})|y\rangle$$

The factor `(1 + (-1)^{s·y})`:
- `s·y = 0 mod 2`: factor = 2 (constructive)
- `s·y = 1 mod 2`: factor = 0 (destructive)

**Result**: Measuring the first register always gives some `y` with `s·y = 0 mod 2` (a **uniformly random linear constraint** on `s`).

6. Repeat `O(n)` times to collect `n` independent linear equations `{s·yᵢ = 0}`

**Classical post-processing**: Solve the `n`-equation linear system over `GF(2)` (Gaussian elimination in `O(n³)` steps) to recover `s`.

### Why Simon's Algorithm Matters

Simon's algorithm achieves an **exponential** quantum speedup in query complexity: `O(n)` vs `Ω(2^{n/2})` queries. This is not a speedup over the best randomized classical algorithm for an artificial problem — Simon's problem has a natural "period finding" structure that appears in real computations.

More importantly, Simon's algorithm is the **structural precursor to Shor's algorithm**:

| Simon | Shor |
|-------|------|
| Period in `(ℤ/2)ⁿ` | Period in `ℤ/N` |
| Hadamard transform | Quantum Fourier transform |
| GF(2) linear algebra | Number theory (GCD) |
| Exact period | Approximate period (continued fractions) |

Shor's algorithm replaces the Hadamard transform with the QFT (which handles non-power-of-2 periods and works over `ℤ/N` instead of `(ℤ/2)ⁿ`) and replaces GF(2) linear algebra with the continued fractions algorithm for extracting the exact period from approximate period estimates.

## Comparison: Quantum Speedups vs. BPP

A critical subtlety: the Deutsch-Jozsa algorithm is faster than deterministic classical algorithms but not exponentially faster than **probabilistic** classical algorithms (which are in BPP). Simon's algorithm is exponentially faster than any BPP algorithm, making it a genuine unconditional speedup in the query model.

| Algorithm | Quantum | Classical Det. | Classical BPP | Speedup Type |
|-----------|---------|----------------|----------------|--------------|
| Deutsch | 1 | 2 | 2 | Constant (exact) |
| Deutsch-Jozsa | 1 | 2^{n-1}+1 | O(n) | Exponential vs det., constant vs BPP |
| Bernstein-Vazirani | 1 | n | n | n-fold (exact) |
| Simon's | O(n) | 2^{n-1}+1 | 2^{n/2} | Exponential vs BPP |

Simon's is the only one where the quantum speedup is exponential over BPP (not just over deterministic algorithms). This is the crucial distinction for arguing genuine quantum advantage.

## Key Formulas

**Deutsch's algorithm final state**:
$$H|(-1)^{f(0)}, (-1)^{f(1)}\rangle: \text{measure 0 (constant), 1 (balanced)}$$

**Deutsch-Jozsa amplitude at 0^n**:
$$\text{amp}(0^n) = \frac{1}{2^n}\sum_{x}(-1)^{f(x)} = \begin{cases} \pm 1 & f \text{ constant} \\ 0 & f \text{ balanced}\end{cases}$$

**Bernstein-Vazirani: amplitude after H^n**:
$$\text{amp}(y) = [y = s]$$

**Simon's: measurable set**:
$$\{y : s\cdot y = 0 \pmod 2\}$$

**Linear constraints give the period**: `n` random samples of `{y : s·y = 0}` determine `s` via Gaussian elimination over `GF(2)` with high probability.

## Worked Example

**Problem**: Apply the Bernstein-Vazirani algorithm for `n=3` with hidden string `s = 110`.

(a) Specify the oracle `O_f`.  
(b) Trace through the algorithm to verify the output is `110`.  
(c) How many classical queries would be needed, and what queries would you make?

**Solution**:

**(a) Oracle for `f(x) = s·x = x₁⊕x₂` (dot product mod 2 with `s=110`)**:

`f(000) = 0, f(001) = 0, f(010) = 1, f(011) = 1, f(100) = 1, f(101) = 1, f(110) = 0, f(111) = 0`.

The phase oracle: `O_f|x⟩ = (-1)^{x_1 \oplus x_2}|x⟩` (or equivalently, `(-1)^{s·x}|x⟩` where `s = 110`).

**(b) Algorithm trace**:

Step 1 — Initial state: `|000⟩`.

Step 2 — After `H^{⊗3}`:
$$\frac{1}{2\sqrt{2}}\sum_{x \in \{0,1\}^3}|x\rangle = \frac{1}{2\sqrt{2}}(|000\rangle+|001\rangle+|010\rangle+|011\rangle+|100\rangle+|101\rangle+|110\rangle+|111\rangle)$$

Step 3 — After oracle (phase kickback):
$$\frac{1}{2\sqrt{2}}\sum_x (-1)^{x_1\oplus x_2}|x\rangle$$

Applying the phases:
- `|000⟩, |001⟩`: `s·x = 0`, phase +1
- `|010⟩, |011⟩`: `s·x = 1`, phase -1
- `|100⟩, |101⟩`: `s·x = 1`, phase -1
- `|110⟩, |111⟩`: `s·x = 0`, phase +1

$$= \frac{1}{2\sqrt{2}}(|000\rangle+|001\rangle-|010\rangle-|011\rangle-|100\rangle-|101\rangle+|110\rangle+|111\rangle)$$

Step 4 — After `H^{⊗3}`:

The amplitude of `|y⟩` is `(1/8)Σ_x (-1)^{s·x+x·y} = (1/8)Σ_x (-1)^{x·(s⊕y)}`.

For `y = 110`: `s⊕y = 110⊕110 = 000`, so each term is `(-1)^{x·0} = 1`. Sum = 8, amplitude = 8/8 = 1.

For any `y ≠ 110`: `s⊕y ≠ 0`, so `Σ_x(-1)^{x·(s⊕y)} = 0` (orthogonality of characters).

Final state: `|110⟩`. Measurement outcome: `110 = s`. ✓

**(c) Classical approach**:

Need to find bits `s₁, s₂, s₃` of `s = 110`:
- Query `f(100) = s·100 = s₁ = 1` → reveals `s₁ = 1`
- Query `f(010) = s·010 = s₂ = 1` → reveals `s₂ = 1`
- Query `f(001) = s·001 = s₃ = 0` → reveals `s₃ = 0`

**3 classical queries** to recover `s = 110`.

The quantum algorithm used **1 oracle call** (plus `O(n) = O(3)` gates). The classical algorithm always needs exactly `n = 3` queries — one per bit of `s`. Quantum speedup: `n`-fold.

**Note**: For large `n`, this `n`-fold speedup represents a genuine advantage (linear vs. linear, but with better constant — quantum finds all bits at once). More importantly, the technique generalizes to Simon's problem where quantum achieves exponential speedup over classical.

## Summary

- **Deutsch's algorithm**: 1 quantum query vs 2 classical; determines constant vs balanced for `f: {0,1} → {0,1}`; demonstrates interference (phase kickback + Hadamard) on the simplest possible example
- **Deutsch-Jozsa**: 1 quantum query vs `2^{n-1}+1` deterministic classical; but only constant speedup over randomized (`O(n)` BPP queries); the algorithm uses global interference to test a global property of `f`
- **Bernstein-Vazirani**: 1 quantum query vs `n` classical queries; finds hidden linear function `f(x) = s·x mod 2` from a single oracle call; demonstrates `n`-fold speedup
- **Simon's problem**: `O(n)` quantum queries vs `Ω(2^{n/2})` classical (BPP); exponential speedup; works by sampling random linear constraints on the hidden period, then using Gaussian elimination
- **Simon → Shor**: Simon's algorithm is the structural blueprint for Shor's factoring algorithm; replace Hadamard with QFT, replace GF(2) linear algebra with continued fractions
- These are **query complexity** results: the speedup is measured in oracle calls; the circuit depth and gate count are also polynomial, making these genuine polynomial-time quantum algorithms

## Exercises

**Exercise 1**: Run the Bernstein-Vazirani algorithm for `n = 4` with hidden string `s = 1011`. Give the state after the oracle (list the sign of each basis state's amplitude for `x ∈ {0000, 0001, 0010, 0011}`), the final state, and the number of classical queries needed.

<details><summary>Solution</summary>

After the oracle the state is `(1/4)Σ_x (-1)^{s·x}|x⟩` with `s·x = x₁ ⊕ x₃ ⊕ x₄`. For the requested inputs:

- `0000`: `s·x = 0` → `+`
- `0001`: `s·x = 1` → `−`
- `0010`: `s·x = 1` → `−`
- `0011`: `s·x = 0` → `+`

The final `H^{⊗4}` maps `(1/4)Σ_x(-1)^{s·x}|x⟩` exactly to `|s⟩ = |1011⟩` (orthogonality of characters), so the measurement returns `1011` with probability 1 after **one** query.

Classically: 4 queries, one per standard basis vector (`f(1000) = s₁ = 1`, `f(0100) = s₂ = 0`, `f(0010) = s₃ = 1`, `f(0001) = s₄ = 1`).

</details>

**Exercise 2**: The function `f(x₁x₂) = x₁ ∨ x₂ (OR)` is neither constant nor balanced — it violates the Deutsch-Jozsa promise. Compute the full output distribution of the DJ circuit for this `f`. What would the algorithm (which reports "constant" iff the outcome is `00`) conclude, and with what probability?

<details><summary>Solution</summary>

`f(00) = 0`, `f(01) = f(10) = f(11) = 1`. The amplitude of outcome `y` is `(1/4)Σ_x(-1)^{f(x)+x·y}`:

- `amp(00) = (1/4)(1 - 1 - 1 - 1) = -1/2`
- `amp(01) = (1/4)(1 + 1 - 1 + 1) = 1/2`
- `amp(10) = (1/4)(1 - 1 + 1 + 1) = 1/2`
- `amp(11) = (1/4)(1 + 1 + 1 - 1) = 1/2`

Distribution: `P(00) = P(01) = P(10) = P(11) = 1/4` (checks: squares sum to 1).

The algorithm reports "constant" with probability `1/4` and "balanced" with probability `3/4`. Neither answer is meaningful — the promise is what makes the one-query separation possible; without it the outcome is just noise.

</details>

**Exercise 3**: In Simon's algorithm with `n = 3` and unknown period `s`, two runs return `y⁽¹⁾ = 110` and `y⁽²⁾ = 011`. Find all candidate periods `s` and state what a third run is for.

<details><summary>Solution</summary>

Constraints: `s·110 = 0` and `s·011 = 0`, i.e. `s₁ ⊕ s₂ = 0` and `s₂ ⊕ s₃ = 0`. Hence `s₁ = s₂ = s₃`, giving `s ∈ {000, 111}`. Since Simon's problem promises `s ≠ 000`, the unique candidate is `s = 111`.

Here two independent equations already determine `s` (they span a 2-dimensional subspace of the 3-dimensional space, whose orthogonal complement minus `0` is a single string). A third run is only needed when earlier samples are linearly dependent (e.g., a repeat or `000`); in general one collects samples until `n-1` independent constraints are found, then confirms classically with two evaluations: `f(0...0) = f(s)` iff `s` is the period.

</details>

**Exercise 4**: For Simon's algorithm with period `s = 101` (`n = 3`), suppose the second-register measurement returned `f(x₀)` with `x₀ = 010`. Write the post-measurement state of the first register, apply `H^{⊗3}`, and list the outcomes that can occur with their probabilities.

<details><summary>Solution</summary>

The two preimages are `x₀ = 010` and `x₀ ⊕ s = 111`, so the register collapses to `(|010⟩ + |111⟩)/√2`.

After `H^{⊗3}`, the amplitude of `|y⟩` is `(1/4)(-1)^{010·y}(1 + (-1)^{101·y})`: nonzero iff `s·y = y₁ ⊕ y₃ = 0`.

The strings with `y₁ ⊕ y₃ = 0` are `{000, 010, 101, 111}`, each with amplitude `±1/2`, hence probability `1/4` each. (Explicit signs from the `(-1)^{010·y}` prefactor, i.e. `(-1)^{y₂}`: `+` for `000` and `101`, `−` for `010` and `111`.)

Every outcome satisfies `s·y = 0`, giving one uniformly random linear constraint on `s` per run — the raw material for the Gaussian-elimination post-processing.

</details>

## Further Reading

1. **Deutsch**, "Quantum Theory, the Church-Turing Principle and the Universal Quantum Computer" (Proceedings of the Royal Society A, 1985) — the original paper; introduces the first quantum algorithm
2. **Bernstein & Vazirani**, "Quantum Complexity Theory" (SIAM Journal on Computing, 1997) — proves BV algorithm and introduces quantum complexity theory; arXiv:quant-ph/9701001
3. **Simon**, "On the Power of Quantum Computation" (SIAM Journal on Computing, 1997) — Simon's period-finding algorithm; the bridge between early QA and Shor
4. **Cleve, Ekert, Macchiavello & Mosca**, "Quantum Algorithms Revisited" (Proceedings of the Royal Society A, 1998) — unifying presentation of Deutsch-Jozsa, BV, and Simon via phase kickback; arXiv:quant-ph/9708016
5. **Mosca**, "Quantum Algorithms" in *Encyclopedia of Complexity and Systems Science* (arXiv:0808.0369) — comprehensive survey with full proofs and historical context for all the algorithms in this chapter
