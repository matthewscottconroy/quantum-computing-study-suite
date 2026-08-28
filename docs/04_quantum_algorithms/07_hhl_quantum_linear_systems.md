# HHL and Quantum Linear Systems

> **Prerequisites**: 04_quantum_algorithms/03_quantum_fourier_transform.md, 04_quantum_phase_estimation.md, 03_quantum_gates_and_circuits/02_multi_qubit_gates.md (controlled rotations)  
> **Connects to**: Quantum machine learning (HHL as a subroutine), Hamiltonian simulation (implementing `e^{iAt}`), dequantization results (limits of quantum speedups), quantum chemistry (linear response)

## Overview

The **Harrow-Hassidim-Lloyd (HHL) algorithm** (2009) addresses the most ubiquitous problem in scientific computing: solving a linear system `Ax = b`. Given an `N × N` Hermitian matrix `A` and a vector `b`, HHL prepares a quantum state `|x⟩` proportional to the solution `A⁻¹b` in time `O(log(N) s² κ²/ε)` — polylogarithmic in the dimension `N`, where `s` is the sparsity, `κ` the condition number, and `ε` the target precision. The best general classical algorithms run in time polynomial in `N`, so for well-conditioned, sparse systems this is an exponential speedup — with respect to a carefully circumscribed problem statement.

That circumscription is essential, and this chapter treats it as seriously as the algorithm itself. HHL does **not** output the vector `x`. It outputs a quantum state `|x⟩ = Σᵢ xᵢ|i⟩/‖x‖` whose amplitudes are the solution entries. Reading out all `N` amplitudes would cost `O(N)` measurements, destroying the speedup. The algorithm is useful only when the desired answer is a *global property* of `x` — an expectation value `⟨x|M|x⟩`, an overlap with another state, or a sample from the distribution `|xᵢ|²`. Similarly, the input `|b⟩` must be efficiently preparable, and `A` must admit efficient Hamiltonian simulation. When any of these assumptions fails, the speedup evaporates — a set of caveats crisply catalogued in Aaronson's "Read the fine print" (2015).

Structurally, HHL is a beautiful application of the machinery from the previous chapters: quantum phase estimation (Chapter 4.4) extracts the eigenvalues of `A` into a register, a controlled rotation imprints the factor `1/λ` onto an ancilla amplitude, and uncomputation of the QPE removes all garbage, leaving the eigenvalue-weighted superposition that *is* the solution state. It is worth studying both as the flagship "quantum linear algebra" primitive and as a case study in how easily headline quantum speedups can be overstated.

## The Quantum Linear Systems Problem

### Problem Statement

**Quantum Linear Systems Problem (QLSP)**: Given (implicit access to) a Hermitian matrix `A ∈ ℂ^{N×N}` and a unit vector `|b⟩ = Σᵢ bᵢ|i⟩`, prepare a quantum state `|x⟩` such that:

$$|x\rangle = \frac{A^{-1}|b\rangle}{\|A^{-1}|b\rangle\|}$$

i.e., `|x⟩ ∝ A⁻¹|b⟩`, satisfying `A|x⟩ ∝ |b⟩`.

If `A` is not Hermitian, the standard dilation replaces it by the Hermitian matrix `[[0, A],[A†, 0]]`, which doubles the dimension and maps the problem to an equivalent Hermitian one. We therefore assume `A = A†` throughout, with spectral decomposition:

$$A = \sum_{j} \lambda_j |u_j\rangle\langle u_j|, \qquad |b\rangle = \sum_j \beta_j |u_j\rangle$$

The solution state in the eigenbasis is:

$$A^{-1}|b\rangle = \sum_j \frac{\beta_j}{\lambda_j}|u_j\rangle$$

The whole algorithm is a machine for producing exactly this eigenvalue-weighted superposition.

### Assumptions (the load-bearing fine print)

1. **Sparsity / simulability**: `A` has at most `s` nonzero entries per row, with efficiently computable positions and values (or, more generally, `A` admits an efficient block-encoding). This is what makes Hamiltonian simulation of `e^{iAt}` possible in time `O(s · polylog(N))` per unit `t`.
2. **Condition number**: `κ = |λ_max|/|λ_min|` is bounded, and the spectrum is rescaled so all eigenvalues lie in a known window, conventionally `1/κ ≤ |λⱼ| ≤ 1`. Runtime grows as `κ²` (improvable to near-linear in `κ` with modern methods).
3. **State preparation**: `|b⟩` can be prepared by an efficient circuit. If preparing `|b⟩` from classical data takes `O(N)` operations (the generic case without QRAM), the exponential speedup is already gone.
4. **Output model**: only `O(polylog N)` measurements are extracted from `|x⟩` — an observable `⟨x|M|x⟩` or a sample, never the full vector.

## The Algorithm

### Registers

- **Solution register** (`log₂ N` qubits): holds `|b⟩`, becomes `|x⟩`
- **Clock register** (`n` qubits): holds eigenvalue estimates from QPE
- **Rotation ancilla** (1 qubit): receives the `1/λ` amplitude factor

### Step 1: Phase Estimation on e^{iAt}

Since `A` is Hermitian, `U = e^{iAt}` is unitary with eigenvalues `e^{iλⱼt}` on the same eigenvectors `|uⱼ⟩`. Run QPE with `U` on the input `|b⟩ = Σⱼ βⱼ|uⱼ⟩`. Linearity of QPE over the eigenbasis gives:

$$\sum_j \beta_j |u_j\rangle|0\rangle^n \xrightarrow{\text{QPE}} \sum_j \beta_j |u_j\rangle|\tilde{\lambda}_j\rangle$$

where `λ̃ⱼ` is the `n`-bit estimate of `λⱼt/(2π)` scaled to an integer, i.e. `λ̃ⱼ ≈ λⱼ t 2ⁿ/(2π)`. The time `t` is chosen so the eigenvalue window fills the clock register without wrapping (e.g. `λⱼt/(2π) ∈ (0, 1)`). Unlike Shor's use of QPE, here the eigenvalue register stays **entangled** with the solution register — that entanglement is the point: each eigencomponent now carries its own eigenvalue as addressable data.

### Step 2: Controlled Rotation (the 1/λ step)

Append the ancilla in `|0⟩` and apply a rotation controlled on the clock value `λ̃`:

$$|\tilde{\lambda}\rangle|0\rangle \to |\tilde{\lambda}\rangle\left(\sqrt{1 - \frac{C^2}{\tilde{\lambda}^2}}\,|0\rangle + \frac{C}{\tilde{\lambda}}\,|1\rangle\right)$$

with a constant `C ≤ min_j |λ̃ⱼ|` (of order `1/κ` after rescaling) so that every rotation angle is legal. The state becomes:

$$\sum_j \beta_j |u_j\rangle |\tilde{\lambda}_j\rangle \left(\sqrt{1 - \tfrac{C^2}{\tilde{\lambda}_j^2}}|0\rangle + \tfrac{C}{\tilde{\lambda}_j}|1\rangle\right)$$

This is the only non-unitary-looking move in the algorithm, and it is implemented unitarily: the desired `1/λ` weighting sits on the `|1⟩` branch of the ancilla, to be selected by post-selection.

### Step 3: Uncompute the Clock

Run QPE in reverse (inverse QFT ↔ QFT, inverted controlled-`U` powers) to disentangle the clock register, returning it to `|0⟩^n`:

$$\sum_j \beta_j |u_j\rangle|0\rangle^n\left(\sqrt{1-\tfrac{C^2}{\tilde\lambda_j^2}}|0\rangle + \tfrac{C}{\tilde\lambda_j}|1\rangle\right)$$

Uncomputation is essential: if the clock stayed entangled, the eigencomponents could not interfere and the solution register would be left in a useless mixed state.

### Step 4: Post-select the Ancilla

Measure the ancilla. Outcome `|1⟩` occurs with probability:

$$P(1) = \sum_j |\beta_j|^2 \frac{C^2}{\tilde{\lambda}_j^2} \geq \frac{C^2}{\lambda_{max}^2} = \Omega(1/\kappa^2)$$

and the post-measurement solution register is:

$$|x\rangle = \frac{\sum_j \beta_j (C/\tilde{\lambda}_j)|u_j\rangle}{\sqrt{P(1)}} \propto \sum_j \frac{\beta_j}{\lambda_j}|u_j\rangle = A^{-1}|b\rangle \; \checkmark$$

On outcome `|0⟩`, discard and repeat (or wrap the whole circuit in amplitude amplification, reducing the expected repetitions from `O(κ²)` to `O(κ)`).

## Complexity and the Classical Comparison

### Quantum Cost

Combining the pieces — Hamiltonian simulation `e^{iAt}` to precision `ε` for sparse `A`, clock precision `n = O(log(κ/ε))`, and `O(κ)` amplification rounds:

$$T_{HHL} = O\!\left(\log(N)\, s^2 \kappa^2 / \varepsilon\right)$$

(the original HHL scaling; later refinements — Ambainis' variable-time amplification, and the Childs-Kothari-Somma Chebyshev/LCU approach — improve this to near-linear `κ` dependence and `polylog(1/ε)` precision scaling).

### Classical Cost

- **Gaussian elimination**: `O(N³)` — exact, general
- **Conjugate gradient**: `O(N s \sqrt{κ}\, \log(1/ε))` for sparse *positive definite* systems (the bound quoted in the HHL paper itself), and `O(N s κ\, \log(1/ε))` in the general Hermitian case — the fair comparison point; still linear in `N` because it touches every entry
- **Verdict**: HHL wins exponentially in `N` *only when* `s, κ = O(polylog N)`, `|b⟩` is cheap to prepare, and a global property of `x` suffices

### Read the Fine Print (Aaronson, 2015)

Each caveat has teeth:

1. **Input**: loading `N` arbitrary classical numbers into `|b⟩` costs `Ω(N)` without QRAM; large-scale QRAM remains speculative hardware.
2. **Output**: `|x⟩` is a state; extracting a single amplitude to precision `ε` costs `O(1/ε²)` samples. Only observables/samples preserve the speedup.
3. **Conditioning**: `κ` enters polynomially; physically interesting systems (e.g. finite-element discretizations) often have `κ` growing with `N`.
4. **Dequantization** (Tang, 2018): for the *low-rank* regime with classical sample-and-query access (the same access model quantum recommendation systems assumed), classical randomized algorithms solve the analogous tasks with only polynomial slowdown — quantum-inspired algorithms removed the claimed exponential speedups for recommendation systems and low-rank linear systems. HHL's home turf is therefore the **sparse, high-rank, well-conditioned** regime, where dequantization does not apply and the problem is BQP-complete — matching the strongest complexity-theoretic evidence that the speedup is real for *some* instances.

## Key Formulas

**Problem**: prepare `|x⟩ ∝ A⁻¹|b⟩` given `A = Σⱼ λⱼ|uⱼ⟩⟨uⱼ|`, `|b⟩ = Σⱼ βⱼ|uⱼ⟩`

**Solution in eigenbasis**:
$$A^{-1}|b\rangle = \sum_j \frac{\beta_j}{\lambda_j}|u_j\rangle$$

**Controlled rotation**:
$$|\tilde\lambda\rangle|0\rangle \to |\tilde\lambda\rangle\left(\sqrt{1 - C^2/\tilde\lambda^2}\,|0\rangle + (C/\tilde\lambda)|1\rangle\right), \quad C \leq \tilde\lambda_{min}$$

**Post-selection probability**:
$$P(1) = \sum_j |\beta_j|^2 C^2/\tilde\lambda_j^2 = \Omega(1/\kappa^2)$$

**Runtime**:
$$O(\log(N)\, s^2\kappa^2/\varepsilon) \quad \text{vs. classical conjugate gradient } O(Ns\sqrt{\kappa}\log(1/\varepsilon)) \text{ (positive definite; } O(Ns\kappa\log(1/\varepsilon)) \text{ general)}$$

## Worked Example

**Problem**: Run HHL on the standard pedagogical instance

$$A = \begin{pmatrix} 1 & -1/3 \\ -1/3 & 1 \end{pmatrix}, \qquad |b\rangle = |0\rangle$$

(a) Diagonalize `A` and expand `|b⟩` in the eigenbasis.  
(b) Choose the evolution time `t` so that a 2-qubit clock register stores both eigenvalues exactly, and trace the algorithm through the controlled rotation with `C` chosen maximal.  
(c) Give the post-selection probability and the final state `|x⟩`; verify against the classical solution.

**Solution**:

**(a) Eigenstructure**: `A = I - (1/3)X`, so its eigenvectors are those of `X`:

$$A|+\rangle = \left(1 - \tfrac{1}{3}\right)|+\rangle = \tfrac{2}{3}|+\rangle, \qquad A|-\rangle = \left(1 + \tfrac{1}{3}\right)|-\rangle = \tfrac{4}{3}|-\rangle$$

Eigenvalues: `λ₁ = 2/3` (for `|u₁⟩ = |+⟩`), `λ₂ = 4/3` (for `|u₂⟩ = |−⟩`). Condition number `κ = (4/3)/(2/3) = 2`.

Input expansion: `|b⟩ = |0⟩ = (|+⟩ + |−⟩)/√2`, so `β₁ = β₂ = 1/√2`.

**(b) QPE stage**: Choose `t = 3π/4`. Then the QPE phases `φⱼ = λⱼt/(2π)` are:

- `φ₁ = (2/3)(3π/4)/(2π) = 1/4` → 2-bit clock value `λ̃₁ = 4·(1/4) = 1 = 01₂`
- `φ₂ = (4/3)(3π/4)/(2π) = 1/2` → 2-bit clock value `λ̃₂ = 4·(1/2) = 2 = 10₂`

Both phases are dyadic rationals, so 2 clock qubits store them **exactly** (no QPE error in this instance). After QPE:

$$\frac{1}{\sqrt{2}}\left(|+\rangle|01\rangle + |-\rangle|10\rangle\right)$$

Note `λ̃₂/λ̃₁ = 2 = λ₂/λ₁`: the integer clock values are faithful rescalings of the eigenvalues.

**Controlled rotation**: take `C = 1 = λ̃_min`. The rotation gives amplitude `C/λ̃ⱼ` on ancilla `|1⟩`:

- Clock `01` (`λ̃ = 1`): ancilla → `√(1-1)|0⟩ + 1·|1⟩ = |1⟩`
- Clock `10` (`λ̃ = 2`): ancilla → `√(3)/2·|0⟩ + (1/2)|1⟩`

State (after uncomputing the clock back to `|00⟩`, suppressed):

$$\frac{1}{\sqrt{2}}|+\rangle|1\rangle + \frac{1}{\sqrt{2}}|-\rangle\left(\frac{\sqrt{3}}{2}|0\rangle + \frac{1}{2}|1\rangle\right)$$

**(c) Post-selection**: probability of ancilla `|1⟩`:

$$P(1) = \frac{1}{2}(1)^2 + \frac{1}{2}\left(\frac{1}{2}\right)^2 = \frac{1}{2} + \frac{1}{8} = \frac{5}{8}$$

Post-selected state (normalize the `|1⟩` branch by `√(5/8)`):

$$|x\rangle = \frac{(1/\sqrt2)|+\rangle + (1/(2\sqrt2))|-\rangle}{\sqrt{5/8}} = \frac{2|+\rangle + |-\rangle}{\sqrt{5}}$$

Converting to the computational basis with `|±⟩ = (|0⟩ ± |1⟩)/√2`:

$$|x\rangle = \frac{1}{\sqrt{5}}\cdot\frac{(2+1)|0\rangle + (2-1)|1\rangle}{\sqrt{2}} = \frac{3|0\rangle + |1\rangle}{\sqrt{10}}$$

**Classical check**: solve `Ax = (1,0)ᵀ` directly. From the second row, `-x₁/3 + x₂ = 0`, so `x₂ = x₁/3`; the first row gives `x₁ - x₁/9 = 1`, so `x₁ = 9/8`, `x₂ = 3/8`:

$$x = \left(\tfrac{9}{8}, \tfrac{3}{8}\right), \qquad \frac{x}{\|x\|} = \frac{(9,3)}{\sqrt{90}} = \frac{(3,1)}{\sqrt{10}} \; \checkmark$$

(Direct verification: `A·(9/8, 3/8)ᵀ = (9/8 - 1/8, -3/8 + 3/8)ᵀ = (1, 0)ᵀ` ✓.) Measurement of `|x⟩` yields `0` with probability `9/10` and `1` with probability `1/10` — the squared, normalized solution entries. Note what is *not* delivered: the norm `‖x‖ = 3√10/8 ≈ 1.186` is absorbed into `P(1)` and must be estimated separately if needed.

## Exercises

**Exercise 1**: For the worked example's matrix `A`, run the algorithm on `|b⟩ = |1⟩` instead. Using symmetry, write down the eigen-expansion, the post-selection probability, and the final state `|x⟩`. Check against the classical solution.

<details><summary>Solution</summary>

`|1⟩ = (|+⟩ - |−⟩)/√2`, so `β₁ = 1/√2`, `β₂ = -1/√2` — same magnitudes as the worked example, only a sign change on the `|−⟩` component.

The rotation amplitudes depend only on `|βⱼ|` and `λ̃ⱼ`, so `P(1) = 5/8` again. The post-selected state:

$$|x\rangle = \frac{2|+\rangle - |-\rangle}{\sqrt{5}} = \frac{(2-1)|0\rangle + (2+1)|1\rangle}{\sqrt{10}} = \frac{|0\rangle + 3|1\rangle}{\sqrt{10}}$$

Classical check: `Ax = (0,1)ᵀ` gives `x = (3/8, 9/8)` (mirror of the worked example by the symmetry of `A` under swapping the basis states), and `x/‖x‖ = (1,3)/√10` ✓.

</details>

**Exercise 2**: Solve `Ax = b` by HHL-in-the-eigenbasis for `A = [[2, 1],[1, 2]]` and `|b⟩ = |0⟩`: find the eigenvalues, `κ`, the ideal post-selected state, and the classical solution. (Work abstractly; no need to pick `t`.)

<details><summary>Solution</summary>

`A = 2I + X`: eigenvectors `|+⟩` (eigenvalue `λ = 3`) and `|−⟩` (`λ = 1`); `κ = 3`.

`|b⟩ = (|+⟩ + |−⟩)/√2`, so:

$$A^{-1}|b\rangle = \frac{1}{\sqrt2}\left(\frac{1}{3}|+\rangle + |-\rangle\right) \propto |+\rangle + 3|-\rangle$$

Normalized: `|x⟩ = (|+⟩ + 3|−⟩)/√10 = ((1+3)|0⟩ + (1-3)|1⟩)/√20 = (2|0⟩ - |1⟩)/√5`.

Classical check: `x = A⁻¹(1,0)ᵀ`. `A⁻¹ = (1/3)[[2,-1],[-1,2]]`, so `x = (2/3, -1/3)`; verify `A·(2/3,-1/3)ᵀ = (4/3 - 1/3, 2/3 - 2/3)ᵀ = (1,0)ᵀ` ✓ and `x/‖x‖ = (2,-1)/√5` ✓.

Taking the maximal legal rotation constant `C = λ_min = 1`: `P(1) = (1/2)(C/3)² + (1/2)(C/1)² = (1/2)(1/9) + (1/2)(1) = 5/9`. The heavier weight lands on the *small* eigenvalue's component — `A⁻¹` amplifies exactly the directions `A` suppresses.

</details>

**Exercise 3**: In the worked example, the clock register used the mapping `λ̃ = λt·2ⁿ/(2π)` with `t = 3π/4`, `n = 2`. Suppose instead `t = 3π/8`. What clock values do the two eigenvalues produce, is the encoding still exact, and what goes wrong with the rotation constant `C`?

<details><summary>Solution</summary>

Phases: `φ₁ = (2/3)(3π/8)/(2π) = 1/8` and `φ₂ = (4/3)(3π/8)/(2π) = 1/4`. Clock values `λ̃ = 4φ`: `λ̃₁ = 0.5` and `λ̃₂ = 1`.

`λ̃₁ = 0.5` is **not an integer**: with `n = 2` clock qubits the phase `1/8` is not a dyadic rational of the form `j/4`, so QPE is no longer exact — the clock register ends in a superposition spread around `j = 0` and `j = 1` (probability `≈ 0.427` each, as computed in the QPE chapter's exercises), entangling error into the solution register.

Worse, outcomes `j = 0` occur with high probability, and the rotation `C/λ̃` is undefined at `λ̃ = 0` (in practice: that branch must be excluded, costing success probability and accuracy). The fix is either more clock qubits (`n = 3` makes `1/8` exact) or rescaling `t` so the smallest eigenvalue maps to a comfortably nonzero integer — this is the practical content of the requirement "eigenvalues known to lie in `[1/κ, 1]`".

</details>

**Exercise 4**: A dense, unstructured `N × N` system with `N = 10⁶` and `κ = √N` is proposed as an HHL application, with `b` given as a classical array and the full solution vector `x` required as output. Itemize where the claimed exponential speedup fails (there are at least three independent failures), and name one problem regime where HHL-type algorithms retain a defensible advantage.

<details><summary>Solution</summary>

1. **Input**: loading `10⁶` arbitrary classical entries of `b` into `|b⟩` costs `Ω(N)` gates (no QRAM assumed) — already polynomial in `N`, before the algorithm starts.
2. **Sparsity**: dense `A` means `s = N`; the `s²` factor makes the runtime `Ω(N²)` — worse than conjugate gradient.
3. **Conditioning**: `κ = √N = 10³` contributes `κ² = 10⁶` (a further `poly(N)` factor: `κ²` alone erases "exponential" whenever `κ = poly(N)`).
4. **Output**: demanding all of `x` requires `O(N)` state tomography samples at minimum; the quantum output is a state, not an array.

Any one of these reduces HHL to polynomial-in-`N` cost; together they make it uncompetitive. A defensible regime: `A` sparse with structure given by an efficient oracle (e.g., a local discretized operator), `κ = O(polylog N)` (well-preconditioned), `|b⟩` generated by a short quantum circuit (e.g., the output of another quantum subroutine), and only an observable `⟨x|M|x⟩` required — for instance, estimating a scattering cross-section or an effective resistance, where the linear system lives natively inside a larger quantum pipeline. This sparse well-conditioned regime is also where the problem is BQP-complete, so a generic classical dequantization would collapse BQP.

</details>

## Summary

- HHL prepares `|x⟩ ∝ A⁻¹|b⟩` in `O(log(N) s²κ²/ε)` time: QPE on `e^{iAt}` writes each eigenvalue into a clock register, a controlled rotation imprints amplitude `C/λ̃`, uncomputation disentangles the clock, and post-selecting the ancilla on `|1⟩` leaves the eigenvalue-weighted solution state
- In the eigenbasis the algorithm computes `Σⱼ (βⱼ/λⱼ)|uⱼ⟩` — inversion happens amplitude-by-amplitude on eigencomponents, which is why the eigenvalues must first be made addressable by QPE
- Success probability is `Ω(1/κ²)`, improved to `O(κ)` repetitions by amplitude amplification; clock precision needs only `O(log(κ/ε))` qubits
- The output is a **quantum state, not a vector**: only observables, overlaps, or samples of `x` are efficiently available; the norm `‖x‖` arrives separately through the post-selection statistics
- The exponential speedup requires *simultaneously*: efficient preparation of `|b⟩`, sparse/simulable `A`, `κ = O(polylog N)`, and a global-property output — Aaronson's "fine print"
- Tang's dequantization (2018) removed the exponential quantum advantage for low-rank instances under sample-and-query access; the surviving quantum regime — sparse, high-rank, well-conditioned — is BQP-complete, the strongest evidence that the speedup is genuine there
- Later algorithms (Ambainis; Childs-Kothari-Somma) improve the scaling to near-linear in `κ` and `polylog(1/ε)`, replacing QPE with Chebyshev-polynomial/LCU implementations of `A⁻¹`

## Further Reading

1. **Harrow, Hassidim & Lloyd**, "Quantum Algorithm for Linear Systems of Equations" (Physical Review Letters 103, 150502, 2009; arXiv:0811.3171) — the original paper, including the BQP-completeness argument and the `κ²` analysis
2. **Aaronson**, "Read the fine print" (Nature Physics 11, 291-293, 2015) — the essential caveat catalogue for HHL and quantum machine learning applications built on it
3. **Childs, Kothari & Somma**, "Quantum Algorithm for Systems of Linear Equations with Exponentially Improved Dependence on Precision" (SIAM Journal on Computing 46, 1920-1950, 2017; arXiv:1511.02306) — replaces QPE with LCU/Chebyshev techniques, achieving `polylog(1/ε)` scaling
4. **Tang**, "A Quantum-Inspired Classical Algorithm for Recommendation Systems" (STOC 2019; arXiv:1807.04271) — the dequantization breakthrough; with follow-ups, delimits which linear-algebra speedups survive
5. **Dervovic et al.**, "Quantum linear systems algorithms: a primer" (arXiv:1802.08227, 2018) — a pedagogical walkthrough of HHL and its refinements, including the worked 2×2 example used in this chapter
