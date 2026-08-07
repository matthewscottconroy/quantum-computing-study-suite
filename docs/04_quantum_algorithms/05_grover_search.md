# Grover's Search Algorithm

> **Prerequisites**: 04_quantum_algorithms/01_quantum_parallelism_and_interference.md, 03_quantum_gates_and_circuits/01_single_qubit_gates.md and 02_multi_qubit_gates.md  
> **Connects to**: Quantum circuit complexity (optimality of Grover), amplitude amplification (generalization), quantum cryptography (impact on symmetric key lengths)

## Overview

**Grover's algorithm** (1996) solves the unstructured search problem: given a function `f: {0,1}ⁿ → {0,1}` with exactly one (or few) marked elements (where `f(x*) = 1`), find `x*`. Classically, this requires `O(N)` evaluations of `f` in the worst case, where `N = 2ⁿ`. Grover's algorithm finds `x*` using only `O(√N)` quantum evaluations — a quadratic speedup.

This is a provably **optimal** quantum speedup for unstructured search. The BBBV theorem (Bennett, Bernstein, Brassard, Vazirani, 1997) proves that no quantum algorithm can search an unsorted database in fewer than `Ω(√N)` queries. Grover's algorithm is therefore not just a speedup — it is the *best possible* quantum speedup for this problem.

The algorithm works through **amplitude amplification**: a geometric rotation in a 2-dimensional subspace that gradually boosts the amplitude of the target state. After `O(π√N/4)` iterations, the target amplitude approaches 1. Each iteration consists of two reflections — the oracle reflection and the diffusion operator — which together constitute a rotation by a fixed angle `2θ` in the 2D subspace.

The quadratic speedup has important cryptographic implications: Grover's algorithm can break symmetric encryption with `n`-bit keys in `O(2^{n/2})` instead of `O(2ⁿ)` operations. This is why post-quantum cryptography standards recommend doubling key sizes for symmetric algorithms (e.g., AES-256 instead of AES-128) to maintain security against quantum adversaries.

## The Problem and Oracle

### Unstructured Search

**Problem**: Given a function `f: {0,...,N-1} → {0,1}` with `N = 2ⁿ`, where exactly `M` inputs satisfy `f(x) = 1` (the "marked" items), find any marked item.

For simplicity we first analyze `M = 1` (single marked item `x*`).

**Classical hardness**: In the worst case, must evaluate `f` on each input until finding `x*`. Expected evaluations: `N/2`. In a randomized algorithm: `O(N)` evaluations.

### The Phase Oracle

The oracle marks the solution with a phase flip:

$$O_f|x\rangle = (-1)^{f(x)}|x\rangle = \begin{cases} -|x\rangle & \text{if } x = x^* \\ |x\rangle & \text{otherwise}\end{cases}$$

This is a phase oracle (as derived in Chapter 4.1 via phase kickback). The oracle `O_f` is a **reflection** about the subspace orthogonal to `|x*⟩`:

$$O_f = I - 2|x^*\rangle\langle x^*|$$

This flips the sign of the `x*` component while leaving all others unchanged.

**Circuit for the oracle**: The oracle is an implementation detail that depends on the specific function `f`. For a known target, it can be a multi-controlled-Z gate. For a general boolean function, it is implemented using Toffoli gates.

## The Grover Diffusion Operator

### Definition

The **Grover diffusion operator** (also called inversion about the mean) is:

$$G_D = 2|s\rangle\langle s| - I, \quad |s\rangle = \frac{1}{\sqrt{N}}\sum_{x=0}^{N-1}|x\rangle$$

where `|s⟩` is the uniform superposition state. `G_D` is also a reflection — it reflects any state about `|s⟩`.

**Matrix form**: The diffusion operator has the explicit form:

$$G_D = H^{\otimes n}(2|0\rangle\langle 0|^{\otimes n} - I)H^{\otimes n}$$

Because `|s⟩ = H^{⊗n}|0⟩^n`, we can write `|s⟩⟨s| = H^{⊗n}|0⟩⟨0|H^{⊗n}`, and thus:

$$2|s\rangle\langle s| - I = H^{\otimes n}(2|0\rangle\langle 0| - I)H^{\otimes n}$$

The operator `2|0⟩⟨0| - I` flips the sign of every state except `|0⟩`. This is implemented by:
1. Apply `H^{⊗n}` (to go to the `|s⟩` basis)
2. Apply phase flip on `|0⟩^n` (multi-controlled-Z with all controls `|0⟩`, implemented as X⊗n · MCZ · X⊗n)
3. Apply `H^{⊗n}` (to return to computational basis)

**Physical interpretation**: The diffusion operator performs "inversion about the mean." If state amplitudes are `{a_x}` with mean `μ = (1/N)Σ_x a_x`, then after `G_D`, each amplitude transforms as:

$$a_x \to 2\mu - a_x$$

This maps any amplitude below the mean to above the mean (and vice versa). If `x*` has a larger negative amplitude (after the oracle flip), its amplitude after inversion exceeds the mean by more than before — it grows.

## The Grover Iteration and Geometric Picture

### One Grover Step

The **Grover iteration** (or **Grover operator**) is:

$$G = G_D \cdot O_f = (2|s\rangle\langle s| - I)(I - 2|x^*\rangle\langle x^*|)$$

Each iteration applies: first the oracle `O_f` (flip amplitude of `x*`), then the diffusion `G_D` (inversion about mean).

### Geometric Analysis

The key insight is that Grover's algorithm operates in a **2-dimensional subspace**:

$$\text{span}\{|x^*\rangle, |s'\rangle\}$$

where `|s'⟩` is the uniform superposition over all non-marked states:

$$|s'\rangle = \frac{1}{\sqrt{N-1}}\sum_{x \neq x^*}|x\rangle$$

The initial state `|s⟩` can be written as:

$$|s\rangle = \sin\theta|x^*\rangle + \cos\theta|s'\rangle, \quad \sin\theta = \frac{1}{\sqrt{N}}, \quad \cos\theta = \sqrt{\frac{N-1}{N}}$$

For large `N`: `θ ≈ 1/√N` (small angle).

**Each Grover iteration rotates the state by angle `2θ` toward `|x*⟩`**:

After `k` iterations:
$$G^k|s\rangle = \sin((2k+1)\theta)|x^*\rangle + \cos((2k+1)\theta)|s'\rangle$$

The probability of measuring `x*` after `k` iterations is:
$$P(x^*) = \sin^2((2k+1)\theta)$$

**Proof**: The oracle `O_f = I - 2|x*⟩⟨x*|` reflects about `|s'⟩` (flips the `|x*⟩` component). The diffusion `G_D = 2|s⟩⟨s| - I` reflects about `|s⟩`. Two reflections compose to a rotation. The angle between `|s⟩` and `|s'⟩` is `θ`, so the rotation angle is `2θ`.

### Optimal Number of Iterations

We want `sin²((2k+1)θ) ≈ 1`, i.e., `(2k+1)θ ≈ π/2`. Solving:

$$k^* = \left\lfloor\frac{\pi}{4\theta} - \frac{1}{2}\right\rfloor \approx \frac{\pi}{4\theta} \approx \frac{\pi}{4}\sqrt{N}$$

The success probability at `k = k*` satisfies `P(x*) ≥ 1 - O(1/N)` for large `N`.

**Why overrotating is bad**: If we apply too many iterations (say `2k*`), the state rotates past `|x*⟩` and back toward `|s'⟩`, reducing `P(x*)`. The algorithm must stop at the right number of iterations. For unknown `M` (number of marked states), use a quantum counting subroutine or the "exponential search" strategy.

### Multiple Marked Elements

For `M > 1` marked elements, the analysis generalizes. The initial angle is:

$$\sin\theta = \sqrt{\frac{M}{N}}$$

The optimal iterations: `k* ≈ (π/4)√(N/M)`.

As `M → N/4` (many marked elements), `k* → 1` — almost no iterations needed. If `M > N/2`, classical random sampling is better than Grover.

## Circuit Analysis

### Gate Count

**Full Grover circuit**:
1. Initialize: `H^{⊗n}|0⟩^n = |s⟩` → `n` gates, depth 1
2. Repeat `k* ≈ π√N/4` times:
   - Oracle `O_f`: `T_O` gates (oracle depth)
   - Diffusion `G_D`: `H^{⊗n}`, multi-controlled-Z, `H^{⊗n}` → `O(n)` gates, `O(n)` depth
3. Measure: `n` gates

**Total gates**: `O(√N · (T_O + n))` where `T_O` is the oracle gate count.

**Multi-controlled-Z in the diffusion**: The operator `2|0⟩⟨0| - I` requires a phase flip on `|0⟩^n`. This is an `n`-qubit phase gate that flips only the all-zeros state. It can be implemented as `X^{⊗n} · (n-1)`-controlled-Z `· X^{⊗n}` plus ancilla qubits, costing `O(n)` Toffoli gates.

### T-Gate Count

Each Grover iteration uses:
- Oracle T-gates: `T_O`
- Diffusion T-gates: `O(n)` (for the multi-controlled phase)

Total T-count: `O(√N · (T_O + n))`.

## Amplitude Amplification

Grover's algorithm is a special case of **amplitude amplification** (Brassard, Hoyer, Mosca, Tapp, 2002), which generalizes to:

1. Any initial state (not just the uniform superposition `|s⟩`)
2. Any oracle that marks a subset of states
3. Non-uniform success probability in the initial state

**Amplitude amplification**: Given any quantum algorithm `A` that succeeds (produces a marked state) with probability `p`, amplitude amplification boosts the success probability to near 1 using `O(1/√p)` calls to `A` and `A⁻¹`.

This is a quadratic speedup over the naive strategy of running `A` repeatedly (`O(1/p)` repetitions expected). Amplitude amplification is used in:
- **Grover search**: `A = H^{⊗n}`, `p = M/N`, amplification to probability 1 in `O(√(N/M))` steps
- **Quantum walk search**: `A` is a quantum walk operator; amplitude amplification gives `O(√N/M)` speedup over classical
- **Quantum optimization** (QAOA): amplification of good solutions
- **Quantum simulation**: amplification of specific eigenstates

## Lower Bound: BBBV Theorem

### Statement

**BBBV Theorem** (1997): Any quantum algorithm for unstructured search on `N` items requires `Ω(√N)` oracle queries.

This proves Grover's algorithm is **optimal**: no quantum algorithm can do better than `O(√N)`.

### Proof Idea

The proof uses a **hybrid argument**:

1. Consider a sequence of databases: `D₀` (no marked items), `D₁` (item `x₁` marked), `D₂` (item `x₂` marked), ..., `DₙN}` (all items marked)
2. Any quantum algorithm is a circuit of oracle calls and gates. The oracle call on `Dₖ` differs from `D₀` only in the action on `|x_k⟩`
3. After `T` oracle queries, the quantum state can only "see" at most `T` different inputs (via the hybrid argument — the state differs from the no-marked-item case only through accumulation of differences caused by the oracle)
4. Therefore, the algorithm cannot reliably distinguish "one marked item" from "no marked items" unless `T = Ω(√N)` (since it must accumulate amplitude difference of `Ω(1)` for the marked item, but each oracle query contributes only `O(T/N)` difference)

The formal proof uses the **polynomial method** or the **adversary method** (Ambainis, 2002). The polynomial method: any quantum algorithm that outputs a marked item must compute a polynomial of degree `Ω(√N)` in the input bits, but polynomials of degree `T < Ω(√N)` cannot distinguish the single-marked from no-marked cases.

## Quantum Counting

**Quantum counting** (Brassard, Høyer, Tapp, 1998) uses QPE applied to the Grover operator `G` to estimate the number of marked items `M`.

The Grover operator `G` has eigenvalues `e^{±2iθ}` where `sin²θ = M/N`. QPE on `G` estimates `θ` to `n` bits of precision, from which `M ≈ N sin²θ` is recovered.

Gate count: `O(√N)` applications of `G` for constant precision estimate of `M/N`.

## Key Formulas

**Initial angle**:
$$\sin\theta = \sqrt{M/N}, \quad \theta \approx \sqrt{M/N} \text{ for small } M/N$$

**State after k iterations**:
$$G^k|s\rangle = \sin((2k+1)\theta)|x^*\rangle + \cos((2k+1)\theta)|s'\rangle$$

**Probability of success**:
$$P(x^*) = \sin^2((2k+1)\theta)$$

**Optimal iteration count**:
$$k^* \approx \frac{\pi}{4}\sqrt{N/M}$$

**Grover operator**:
$$G = (2|s\rangle\langle s| - I)(I - 2|x^*\rangle\langle x^*|)$$

**Oracle** (phase oracle):
$$O_f = I - 2\sum_{x: f(x)=1}|x\rangle\langle x|$$

**Diffusion operator**:
$$G_D = H^{\otimes n}(2|0\rangle\langle 0| - I)H^{\otimes n}$$

## Worked Example

**Problem**: Apply Grover's algorithm for `N = 16` (n=4 qubits) with a single marked item `x* = 5` (binary: `0101`).

(a) How many Grover iterations are optimal?  
(b) What is `P(x*)` after the optimal number of iterations?  
(c) Describe the oracle gate for `f(x) = [x = 5]`.

**Solution**:

**(a) Optimal iteration count**:

`N = 16, M = 1`. Initial angle: `sin θ = 1/√16 = 1/4`, so `θ = arcsin(1/4) ≈ 0.2527` radians.

Optimal iterations: `k* = floor(π/(4θ) - 1/2) = floor(3.14159/(4·0.2527) - 0.5) = floor(3.107 - 0.5) = floor(2.607) = 2`.

Alternatively, using the approximation: `k* ≈ (π/4)√N = (π/4)·4 = π ≈ 3.14`, so `k* = 3`.

Let me compute precisely:
- `k=2`: `P(x*) = sin²(5θ) = sin²(5·0.2527) = sin²(1.2635) = sin²(72.4°) ≈ 0.908`
- `k=3`: `P(x*) = sin²(7θ) = sin²(7·0.2527) = sin²(1.7689) = sin²(101.3°) ≈ 0.961`

The maximum of `sin²((2k+1)θ)` is closest to 1 at `k=3`.

More carefully: `(2k+1)θ = π/2` gives `k = (π/(2θ) - 1)/2`. With `θ = 0.2527`:
`k = (3.14159/(2·0.2527) - 1)/2 = (6.215 - 1)/2 = 2.607`

So `k = 3` (rounding up) is optimal, with `P(x*) = sin²(7·0.2527) = sin²(1.769) ≈ sin²(101.4°)`.

Actually `sin(101.4°) = sin(180° - 78.6°) = sin(78.6°) ≈ 0.981`, so `P(x*) ≈ 0.961`.

**(b) Success probability after 3 iterations**:

`P(x*) = sin²(7θ) = sin²(7·arcsin(1/4)) ≈ 0.961`.

This means measuring the final state gives `x* = 5` with ~96% probability. In 3 oracle calls, we have a high probability of finding the marked item.

Compare to classical: expected 8 queries (average over random sampling from 16 items).

**(c) Oracle for `f(x) = [x = 5 = 0101₂]`**:

The marked state is `|0101⟩ = |q₁=0, q₂=1, q₃=0, q₄=1⟩` (with `q₁` as most significant bit).

The oracle flips the phase if and only if `x = 0101`, i.e., `q₁=0, q₂=1, q₃=0, q₄=1`:

**Circuit**:
1. Apply `X` to qubits 1 and 3 (to flip the 0 bits of `x*` to 1, so the multi-controlled gate fires when all qubits are `|1⟩`)
2. Apply a 4-qubit controlled-Z (or 4-qubit controlled-phase on `|1111⟩`)
3. Apply `X` to qubits 1 and 3 (to restore the 0 bits)

This is:
```
q₁: X ──── ● ──── X
           │
q₂: ────── ● ─────
           │
q₃: X ──── ● ──── X
           │
q₄: ────── Z ─────
```

The 4-controlled-Z (control `|111⟩` on first 3 qubits, Z on qubit 4) flips phase of `|1111⟩`. The outer X gates on qubits 1 and 3 convert this to flipping phase of `|0101⟩`.

The 4-controlled-Z gate can be decomposed into Toffoli gates and ancilla, costing `O(n) = O(4)` Toffoli gates (and thus `O(n) = O(4)` T-gates since T-count(Toffoli) = 7).

**Verification**: After the oracle, `|0101⟩ → -|0101⟩` (phase flip) and all other states `|x⟩, x≠5` are unchanged.

**Note on `N=16`**: With 3 oracle calls and ~96% success probability, Grover's algorithm dramatically outperforms random classical search (8 expected queries). For larger `N`, the advantage grows as `√N`.

## Summary

- Grover's algorithm finds a marked item in an unsorted database of `N` items using `O(√N)` oracle queries — a quadratic speedup over the classical `O(N)` bound
- The oracle `O_f = I - 2Σ_{x:f(x)=1}|x⟩⟨x|` marks solutions with a phase flip; the diffusion `G_D = 2|s⟩⟨s| - I` performs inversion about the mean
- Geometrically: each iteration rotates the state by `2θ` (where `sin θ = √(M/N)`) in the 2D subspace spanned by `|x*⟩` and `|s'⟩`
- After `k* = ⌊π√N/(4M) + 1/2⌋` iterations, `P(x*) ≥ 1 - O(M/N)`
- **BBBV theorem** proves `Ω(√N)` queries are necessary — Grover's algorithm is optimal
- **Amplitude amplification** generalizes Grover to arbitrary initial states, giving `O(1/√p)` oracle calls for any algorithm with success probability `p`
- Cryptographic implication: symmetric encryption with `n`-bit keys requires `O(2^{n/2})` quantum work — recommend `n ≥ 256` for post-quantum security

## Further Reading

1. **Grover**, "A Fast Quantum Mechanical Algorithm for Database Search" (STOC, 1996; arXiv:quant-ph/9605043) — the original paper; elegant and readable
2. **Bennett, Bernstein, Brassard & Vazirani**, "Strengths and Weaknesses of Quantum Computing" (SIAM Journal on Computing, 1997) — proves the BBBV lower bound; defines BQP vs NP relations
3. **Brassard, Høyer, Mosca & Tapp**, "Quantum Amplitude Amplification and Estimation" (AMS Contemporary Mathematics, 2002; arXiv:quant-ph/0005055) — generalization to amplitude amplification; full analysis with tight bounds
4. **Zalka**, "Grover's quantum searching algorithm is optimal" (Physical Review A, 1999) — proves tightness of the `π√N/4` iteration count
5. **Montanaro**, "Quantum speedup of Monte Carlo methods" (Proceedings of the Royal Society A, 2015) — applies amplitude amplification to Monte Carlo integration; shows quantum advantage in statistical estimation problems
