# Quantum Walks

> **Prerequisites**: 04_quantum_algorithms/01_quantum_parallelism_and_interference.md, 05_grover_search.md, 01_mathematical_foundations/01_linear_algebra.md (spectral decomposition)  
> **Connects to**: Quantum complexity theory (Chapter 8.1 — query separations), Hamiltonian simulation (Chapter 8.3 — continuous-time walks are `e^{-iAt}`), Grover search and amplitude amplification (walk search generalizes both)

## Overview

The classical random walk is the workhorse of randomized algorithms: 2-SAT solvers, Markov chain Monte Carlo, volume estimation, and s-t connectivity in log-space all reduce to "wander randomly, exploit mixing." **Quantum walks** are the coherent counterpart — unitary processes whose interference pattern spreads *quadratically faster* than diffusion — and they are the engine behind a whole family of quantum algorithms: element distinctness in `O(N^{2/3})` queries, spatial search in `Θ(√N)` steps, triangle finding, formula evaluation, and one of the very few **provable exponential** query speedups (the glued-trees problem).

The defining contrast is in the spreading rate. A classical walker on the line has position standard deviation `σ ∝ √t` (diffusive); a quantum walker achieves `σ ∝ t` (ballistic). The reason is not speed of motion — both move one step per tick — but interference: amplitudes for the many paths to a given site cancel near the origin and reinforce near the "wavefronts" at `x ≈ ±t/√2`.

There are two formulations. The **discrete-time coined walk** enlarges the space with a coin register (the direct quantum analogue of flipping a coin then stepping), and its algorithmic refinement, the **Szegedy walk**, quantizes an arbitrary Markov chain and converts a classical spectral gap `δ` into a quantum phase gap `√δ` — the source of generic quadratic speedups for hitting problems. The **continuous-time walk** dispenses with the coin and simply evolves under the graph's adjacency matrix, `e^{-iAt}`, tying quantum walks directly to Hamiltonian simulation. Grover's algorithm itself (Chapter 4.5) is a quantum walk on the complete graph — walks are the natural generalization of amplitude amplification to structured search spaces.

## The Classical Baseline

A classical random walk on `ℤ` flips a fair coin each step and moves `±1`. After `t` steps the position is a sum of `t` independent `±1` variables:

$$P(x, t) = \binom{t}{(t+x)/2} 2^{-t}, \qquad \langle x \rangle = 0, \qquad \sigma_{\text{cl}} = \sqrt{t}$$

The distribution is a binomial centered at the origin — after 100 steps the walker is typically only ~10 sites away. Hitting times inherit this: reaching a target distance `n` away takes `Θ(n²)` expected steps, and on expander-like graphs the mixing time is governed by the spectral gap `δ` of the transition matrix as `O(1/δ · log N)`.

## Discrete-Time Coined Walks

### Coin and Shift

A naive "quantum walk" that maps `|x⟩ → (|x−1⟩ + |x+1⟩)/√2` is **not unitary** (the images of `|0⟩` and `|2⟩` are not orthogonal). The fix is a **coin register**: the Hilbert space is `ℋ_pos ⊗ ℋ_coin` with basis `|x⟩|c⟩`, `c ∈ {0, 1}`, and one step is

$$U = S\,(I \otimes C), \qquad C = H, \qquad S = \sum_x \Big(|x{+}1\rangle\langle x|\otimes|0\rangle\langle 0| + |x{-}1\rangle\langle x|\otimes|1\rangle\langle 1|\Big)$$

Flip the coin coherently (Hadamard), then shift conditioned on the coin: `c = 0` moves right, `c = 1` moves left. Crucially, the coin is **not measured** between steps — measuring it each step would collapse the process to exactly the classical walk (a useful sanity check, and the cleanest statement of where the quantumness lives).

### Ballistic Spreading

Because the walk is translation-invariant, it diagonalizes in the position-momentum (Fourier) basis. In the momentum sector `k`, one step is the `2×2` unitary `U_k = diag(e^{ik}, e^{-ik})·H` with eigenvalues `e^{±iω(k)}` where

$$\sin\omega(k) = \frac{\sin k}{\sqrt{2}}$$

This **dispersion relation** is the whole story. The group velocity `dω/dk = cos k/√(2−sin²k)` ranges over `[−1/√2, +1/√2]`: wavepackets propagate at constant speed up to `1/√2` site per step, so the distribution develops two peaks racing outward at `x ≈ ±t/√2`, with

$$\sigma_{\text{qu}} \approx \sqrt{1 - \tfrac{1}{\sqrt 2}}\; t \approx 0.5412\, t \qquad \text{versus} \qquad \sigma_{\text{cl}} = \sqrt t$$

Numerical check (exact amplitude evolution, symmetric initial coin `(|0⟩+i|1⟩)/√2`): `σ = 27.07` at `t = 50`, `54.12` at `t = 100`, `108.24` at `t = 200` — the ratio `σ/t = 0.5412` is already converged, while the classical values are `7.07, 10.0, 14.14`. Ballistic vs. diffusive.

Two features with no classical analogue:

- **Initial-state dependence**: starting the coin in `|0⟩` produces a *left-right asymmetric* distribution (drifting right for the `H` coin — the worked example shows this at `t = 3`), because `H` treats `|0⟩` and `|1⟩` asymmetrically in phase. The balanced coin `(|0⟩+i|1⟩)/√2` restores symmetry.
- **Shape**: the distribution is flat-ish between two sharp peaks near `±t/√2` — nearly the inverse of the classical Gaussian bump at the origin.

### Walks on General Graphs

On a `d`-regular graph the coin space is `d`-dimensional (one direction per edge at each vertex), the shift moves along the chosen edge, and the standard coin choice is the **Grover diffusion coin** `C = 2|s⟩⟨s| − I` on the `d` directions (Chapter 4.5's inversion about the mean, now steering a walker). Marked-vertex search replaces the coin by `−I` at marked vertices — the walk analogue of the phase oracle.

## Szegedy Walks: Quantizing a Markov Chain

Szegedy (2004) gave a coin-free, fully general quantization. Take any reversible Markov chain with transition matrix `P = (p_{xy})` on state space of size `N`. Work on **pairs** (edges) `ℋ = span{|x⟩|y⟩}` and define, for each vertex, the superposition of its outgoing transitions:

$$|\phi_x\rangle = |x\rangle \otimes \sum_y \sqrt{p_{xy}}\,|y\rangle$$

The walk operator is a product of two reflections — geometrically Grover-like:

$$W(P) = R_2 R_1, \qquad R_1 = 2\sum_x |\phi_x\rangle\langle\phi_x| - I, \qquad R_2 = \text{(the same, with the two registers swapped)}$$

**Spectral correspondence** (the key theorem): if the chain's discriminant matrix `D(P)` (`D_{xy} = √(p_{xy}p_{yx})`; equal to `P`'s spectrum for reversible chains) has eigenvalue `λ = cos θ`, then `W(P)` has eigenvalue pair `e^{±2iθ}` on the corresponding 2D subspace. Consequently a classical spectral gap `δ = 1 − λ₂` becomes a quantum **phase gap**

$$\Delta = 2\theta_2 = 2\arccos(\lambda_2) \geq 2\sqrt{2\delta} = \Omega(\sqrt{\delta})$$

since `cos θ = 1 − δ` gives `θ ≈ √(2δ)` for small `δ`. Distinguishing "stationary eigenphase 0" from "everything else" with phase estimation therefore costs `O(1/√δ)` walk steps instead of the classical `O(1/δ)` mixing/hitting cost — a *generic* quadratic speedup, inherited by every algorithm built on the framework (search with marked states: `O(1/√(δε))` vs classical `O(1/(δε))` with `ε` the marked fraction, recovering Grover exactly on the complete graph).

## Continuous-Time Walks

The continuous-time quantum walk (CTQW, Farhi-Gutmann 1998) needs no coin at all: take the graph's adjacency matrix `A` (or Laplacian) as a Hamiltonian and evolve

$$|\psi(t)\rangle = e^{-iAt}|\psi(0)\rangle$$

This is exactly the classical continuous-time walk's master equation `ṗ = −Lp` with `d/dt → i·d/dt` — replacing probability by amplitude. On the line, `e^{-iAt}` gives Bessel-function amplitudes `J_x(2t)` with the same ballistic `σ ∝ t` behavior as the coined walk. On two vertices (`A = X`), `e^{-iXt} = cos(t)I − i sin(t)X` — perfect state transfer at `t = π/2` (numerically: transfer probability exactly `1.0`). CTQW connects directly to Hamiltonian simulation (Chapter 8.3): implementing a walk on an exponentially large but sparse graph *is* sparse Hamiltonian simulation, which is how the glued-trees algorithm below runs on a quantum computer.

## Algorithmic Applications

### Grover as a Walk

Grover's algorithm is the coined walk on the **complete graph** `K_N` with the Grover coin and one marked vertex — the two reflections of a Grover iteration (Chapter 4.5) are precisely the two reflections of a Szegedy step for the uniform chain (`p_{xy} = 1/N`). The `Θ(√N)` iteration count is the `1/√δ` phase-gap cost with `δ = Θ(1)` and marked fraction `1/N`. This is the right mental model: **quantum-walk search = amplitude amplification that respects locality**, paying extra only when the graph mixes slowly.

### Element Distinctness — `O(N^{2/3})`

**Problem**: given query access to `x₁, ..., x_N`, decide whether some pair collides (`xᵢ = xⱼ`, `i ≠ j`). Classically `Θ(N)` queries are needed. Ambainis (2004) solved it in `Θ(N^{2/3})` quantum queries with a walk on the **Johnson graph** `J(N, r)`: vertices are size-`r` subsets `S` of indices (each stored *with* its queried values), edges swap one element in for one out.

The cost has the walk-framework anatomy `Setup + (1/√ε)·(1/√δ)·Update`:

- **Setup**: query all of `S` — `r` queries
- **Check**: a stored subset containing a collision is detected free of queries
- `ε = Θ((r/N)²)` (probability a random `S` contains both collision indices — for the promise version with a single colliding pair), `δ = Θ(1/r)` (Johnson-graph spectral gap), **update** = 1 swap ≈ 2 queries

$$Q(r) \approx r + \frac{N}{r}\cdot\sqrt{r} \quad\Longrightarrow\quad \frac{dQ}{dr} = 0 \text{ at } r = (N/2)^{2/3}, \qquad Q = 3(N/2)^{2/3} = \Theta(N^{2/3})$$

Numerically, for `N = 10⁶`: the optimum sits at `r ≈ 6300` with `Q ≈ 18,900` queries — versus `10⁶` classically. The matching `Ω(N^{2/3})` lower bound (Aaronson-Shi, via the polynomial method) makes this tight; it slots into the query-separation catalog of Chapter 8.1 alongside Grover (`Θ(√N)` vs `Θ(N)`) and collision (`Θ(N^{1/3})` vs `Θ(√N)`) as a `2/3`-power separation. The same walk framework yields triangle finding (`O(N^{1.3})` and later improvements) and matrix product verification.

### Spatial Search — `Θ(√N)` on Suitable Graphs

**Spatial search** asks for a marked vertex when the walker may only move along graph edges — Grover with locality constraints. Quantum walks achieve the optimal `Θ(√N)`:

- Complete graph, hypercube: `Θ(√N)` (coined walk, Shenvi-Kempe-Whaley for the hypercube)
- 2D lattice: `O(√N log N)` — the marginal dimension, where the walk's effective mass almost spoils the speedup
- Dimensions ≥ 3, and in fact any graph with sufficient spectral expansion: `Θ(√N)`; Chakraborty et al. (2016) showed `Θ(√N)` CTQW search for almost all graphs (Erdős–Rényi ensembles above the connectivity threshold)

Since a classical local search cannot beat `Ω(N)`, spatial search is a clean quadratic speedup that respects geometry — relevant to searching physical databases and to walk-based subroutines inside larger algorithms.

### Glued Trees — a Provable Exponential Speedup

Take two complete binary trees of depth `n`, and glue their `2ⁿ` leaves together by a random cycle (each leaf gets degree 3). ENTRANCE is one root, EXIT the other; the graph is given by an adjacency **oracle**. **Problem**: starting at ENTRANCE, find EXIT.

**Why classical fails**: any classical algorithm is effectively a walker on the column structure. The middle columns contain exponentially many vertices; a random walk's stationary drift pushes it *toward* the bulging middle (from the middle, twice as many edges lead "inward" as "outward"), and the random cycle destroys any addressing structure that could identify progress. Any classical algorithm needs `2^{Ω(n)}` queries (Childs et al., 2003 — proven, not conjectured).

**Why quantum succeeds**: `|entrance⟩` has support only on the **column subspace** — the `2n+2` states `|col_j⟩` = uniform superpositions over each column — and `A` preserves this subspace. Reduced to it, the walk is a CTQW on a *line* of `2n+2` sites with uniform couplings `√2` (and `2` at the glue): the ballistic propagation of this chapter's opening then carries the amplitude across in time `O(n)` with `Ω(1/poly(n))` probability at EXIT. Numerical check on the reduced line for `n = 8` (18 columns): the entrance-to-exit transfer probability peaks at `0.59` at `t ≈ 7.2` — linear-time traversal, while the classical walker is still lost among the `~2⁹` middle vertices. This is an **oracle separation**: exponential speedup for a black-box graph-traversal problem, one of the strongest pieces of evidence that quantum walks access genuinely nonclassical dynamics.

## Key Formulas

**Coined walk step**:
$$U = S(I\otimes H), \qquad S|x\rangle|0\rangle = |x{+}1\rangle|0\rangle,\quad S|x\rangle|1\rangle = |x{-}1\rangle|1\rangle$$

**Dispersion and spreading** (Hadamard walk on the line):
$$\sin\omega(k) = \frac{\sin k}{\sqrt 2}, \qquad |v_g|\leq \frac{1}{\sqrt2}, \qquad \sigma_{\text{qu}} \to \sqrt{1-\tfrac1{\sqrt2}}\,t \approx 0.54\,t, \qquad \sigma_{\text{cl}} = \sqrt t$$

**Szegedy spectral correspondence**:
$$\lambda = \cos\theta \;\text{ (chain)} \iff e^{\pm 2i\theta}\;\text{ (walk)}, \qquad \text{phase gap } \Delta = \Omega(\sqrt{\delta})$$

**Walk-search cost template**:
$$Q = \text{Setup} + \frac{1}{\sqrt{\varepsilon}}\left(\frac{1}{\sqrt{\delta}}\cdot\text{Update} + \text{Check}\right)$$

**Element distinctness** (Johnson graph, subset size `r`):
$$Q(r) \approx r + \frac{N}{\sqrt r} \;\Rightarrow\; r^* = (N/2)^{2/3},\; Q = \Theta(N^{2/3})$$

**Continuous-time walk**: `|ψ(t)⟩ = e^{-iAt}|ψ(0)⟩`; glued trees traverse in `O(n)` vs classical `2^{Ω(n)}`.

## Worked Example

**Problem**: Evolve the Hadamard-coined walk for 3 steps from `|0⟩_pos|0⟩_coin`. Give the full state after each step, the final position distribution, and compare with the classical 3-step walk.

**Solution**: Write states as `|x, c⟩`. Coin: `|0⟩ → (|0⟩+|1⟩)/√2`, `|1⟩ → (|0⟩−|1⟩)/√2`; then shift (`c=0` right, `c=1` left).

**Step 1**: coin gives `(|0,0⟩ + |0,1⟩)/√2`; shift gives

$$|\psi_1\rangle = \tfrac{1}{\sqrt2}\big(|1,0\rangle + |{-}1,1\rangle\big)$$

**Step 2**: coin on each term: `|1,0⟩ → (|1,0⟩+|1,1⟩)/√2`, `|−1,1⟩ → (|−1,0⟩−|−1,1⟩)/√2`; shift:

$$|\psi_2\rangle = \tfrac{1}{2}\big(|2,0\rangle + |0,1\rangle + |0,0\rangle - |{-}2,1\rangle\big)$$

**Step 3**: coin each of the four terms and collect (note the **interference** at `x = 0` before shifting: the coin outputs from `|0,1⟩` and `|0,0⟩` are `(|0⟩−|1⟩)/√2` and `(|0⟩+|1⟩)/√2` — the `|0,1⟩` components cancel, the `|0,0⟩` components add):

$$\tfrac{1}{2\sqrt2}\big(|2,0\rangle + |2,1\rangle + 2|0,0\rangle - |{-}2,0\rangle + |{-}2,1\rangle\big)$$

then shift:

$$|\psi_3\rangle = \tfrac{1}{2\sqrt2}\big(|3,0\rangle + |1,1\rangle + 2|1,0\rangle - |{-}1,0\rangle + |{-}3,1\rangle\big)$$

**Position distribution** (amplitudes in units of `1/(2√2) = 0.353553`):

| `x` | amplitudes (coin 0, coin 1) | `P_quantum(x)` | `P_classical(x)` |
|---|---|---|---|
| `+3` | `(1, 0)·1/(2√2)` | `1/8` | `1/8` |
| `+1` | `(2, 1)·1/(2√2)` | `5/8` | `3/8` |
| `−1` | `(−1, 0)·1/(2√2)` | `1/8` | `3/8` |
| `−3` | `(0, 1)·1/(2√2)` | `1/8` | `1/8` |

Total: `1/8 + 5/8 + 1/8 + 1/8 = 1` ✓. Numerical verification (exact sparse amplitude evolution) reproduces every amplitude: e.g. at `x = +1`, `(0.707107, 0.353553)`, `P = 0.625 = 5/8`, and at `x = −1` amplitude `−0.353553` on coin 0.

**Reading the table**: the distribution is strongly **asymmetric** — `⟨x⟩ = +0.5`, versus 0 classically — purely because the `H` coin's phases favor the initial coin state's direction; no classical coin can do this while remaining fair (each single step still gives 50/50). At `t = 3` the quantum spread `σ = √(3 − 0.25) = 1.658` is actually slightly *below* the classical `√3 = 1.732` — the ballistic advantage is asymptotic, not instantaneous: by `t = 100` the quantum `σ = 54.1` versus classical `10` (both verified numerically above). Small cases show the mechanism (interference reshaping the distribution); large `t` shows the scaling.

## Summary

- Quantum walks spread **ballistically** (`σ ∝ t`) versus classical **diffusion** (`σ ∝ √t`); the mechanism is path interference, visible in the Hadamard walk's dispersion `sin ω = sin k/√2` with group speed `1/√2`
- The **coined walk** `U = S(I⊗C)` is the discrete-time form; measuring the coin every step recovers exactly the classical walk; initial coin states control the asymmetry of the distribution
- **Szegedy's construction** quantizes any reversible Markov chain via two reflections on edge space; eigenvalues `cos θ` become eigenphases `±2θ`, converting spectral gap `δ` into phase gap `Ω(√δ)` — a generic quadratic speedup for hitting and search
- The **continuous-time walk** `e^{-iAt}` treats the graph as a Hamiltonian, linking walks to sparse Hamiltonian simulation
- Applications: **Grover = walk on the complete graph**; **element distinctness** in `Θ(N^{2/3})` via the Johnson graph (tight; see the separations table in Chapter 8.1); **spatial search** in `Θ(√N)` on expanders, hypercubes, and lattices of dimension ≥ 3 (`√N log N` in 2D); **glued trees** traversed in `poly(n)` time versus a proven classical `2^{Ω(n)}` — an exponential oracle separation
- Walks are the "structured Grover": amplitude amplification generalized to any geometry, paying only for slow mixing

## Exercises

**Exercise 1**: Run the Hadamard walk for 2 steps from the *symmetric* initial coin state `|0⟩_pos ⊗ (|0⟩ + i|1⟩)/√2`. Compute the state and position distribution, and show the distribution is left-right symmetric (unlike the coin-`|0⟩` walk of the worked example).

<details><summary>Solution</summary>

Step 1: coin gives `|0⟩⊗[(1+i)|0⟩ + (1−i)|1⟩]/2`; shift: `[(1+i)|1,0⟩ + (1−i)|−1,1⟩]/2`.

Step 2: coin: `(1+i)|1⟩(|0⟩+|1⟩)/√2 + (1−i)|−1⟩(|0⟩−|1⟩)/√2`, all over 2; shift:

`|ψ₂⟩ = (1/(2√2))[(1+i)|2,0⟩ + (1+i)|0,1⟩ + (1−i)|0,0⟩ − (1−i)|−2,1⟩]`

Distribution: `P(±2) = |1±i|²/8 = 2/8 = 1/4` each, `P(0) = (|1+i|² + |1−i|²)/8 = 1/2`. Symmetric ✓ (numerically confirmed: amplitudes `(±0.353553 ± 0.353553i)` patterns, `P = (0.25, 0.5, 0.25)`). The `i` makes the coin state unbiased for the `H` coin because `H`'s asymmetry lies in a *real* relative sign, which the `π/2` phase decouples from; the symmetric distribution persists for all `t`.

</details>

**Exercise 2**: Derive the dispersion relation. In momentum space the walk step is `U_k = diag(e^{ik}, e^{−ik})·H`. Show its eigenvalues are `e^{±iω(k)}` with `sin ω = sin k/√2`, and find the maximum group velocity.

<details><summary>Solution</summary>

`U_k = (1/√2)·[[e^{ik}, e^{ik}], [e^{−ik}, −e^{−ik}]]`, with `tr U_k = (e^{ik} − e^{−ik})/√2 = i√2 sin k` and `det U_k = −1`. The eigenvalues solve `μ² − (i√2 sin k)μ − 1 = 0`:

`μ = (i sin k)/√2 ± √(1 − (sin²k)/2)`

Both roots have `|μ| = 1` and imaginary part `sin k/√2`, so writing `μ = e^{iω}` gives `sin ω = sin k/√2` (the two eigenphases are `ω` and `π − ω`). Numerical check at `k = 0.9`: eigenphases of `U_k` are `0.587036` and `2.554557 = π − 0.587036`, and `arcsin(sin 0.9/√2) = 0.587036` ✓.

Group velocity: `v_g = dω/dk = cos k / √(2 − sin²k)`. At `k = 0`: `v_g = 1/√2 ≈ 0.7071` (numerically confirmed by finite difference), and `|v_g|` is maximized there — wavefronts at `x ≈ ±t/√2`, exactly where the two peaks of the long-time distribution sit.

</details>

**Exercise 3**: For the continuous-time walk on two vertices joined by an edge (`A = X`), compute `e^{−iAt}|0⟩` and find the earliest time of perfect state transfer `|0⟩ → |1⟩`. What is the transfer probability at `t = π/4`?

<details><summary>Solution</summary>

Since `X² = I`: `e^{−iXt} = cos(t)·I − i sin(t)·X`, so `e^{−iXt}|0⟩ = cos t·|0⟩ − i sin t·|1⟩`.

Perfect transfer when `|sin t| = 1`: earliest at `t = π/2`, giving `−i|1⟩` — probability `1.0` exactly (the global phase `−i` is unobservable). At `t = π/4`: amplitude `−i/√2` on `|1⟩`, probability `1/2` (numerically: state `(0.707107, −0.707107i)`, `P = 0.5` ✓).

Contrast the classical continuous-time walk on the same graph: `p₁(t) = (1 − e^{−2t})/2` approaches `1/2` monotonically and *never* exceeds it — probability spreads and equilibrates, while amplitude oscillates coherently (`P₁(t) = sin²t` — periodically perfect). This two-vertex example is the smallest instance of walk dynamics that classical stochastic dynamics cannot reproduce.

</details>

**Exercise 4**: In the element-distinctness cost model `Q(r) = r + (N/r)·√r = r + N/√r` (setup of `r` queries, then `1/√ε = N/r` amplification rounds of `1/√δ = √r` one-query update steps), find the optimal `r`, the resulting query count, and evaluate both for `N = 10⁶`. Compare to classical.

<details><summary>Solution</summary>

Minimize `Q(r) = r + N·r^{−1/2}`: `Q'(r) = 1 − (N/2)r^{−3/2} = 0` gives `r* = (N/2)^{2/3}`, and

`Q(r*) = (N/2)^{2/3} + N/(N/2)^{1/3} = (N/2)^{2/3}(1 + 2) = 3(N/2)^{2/3} ≈ 1.89·N^{2/3}`

For `N = 10⁶`: `r* = (5·10⁵)^{2/3} ≈ 6300` and `Q ≈ 18,900` queries (numerical minimization over `r` gives `r ≈ 6295`, `Q ≈ 18,899` ✓), versus `Θ(N) = 10⁶` classically — a ~50× saving that grows as `N^{1/3}`. Note `r* ∝ N^{2/3}`: the walker stores a *large* database subset, trading memory for queries; with the Aaronson-Shi `Ω(N^{2/3})` lower bound this exponent is optimal.

</details>

**Exercise 5**: For the 3-step walk of the worked example, compute `⟨x⟩` and `σ²`, and compare with the classical walk. Explain why the quantum variance can be *smaller* than classical at small `t` even though the walk is asymptotically ballistic.

<details><summary>Solution</summary>

Quantum: `⟨x⟩ = 3(1/8) + 1(5/8) − 1(1/8) − 3(1/8) = 4/8 = 0.5`; `⟨x²⟩ = 9/8 + 5/8 + 1/8 + 9/8 = 3`; `σ² = 3 − 0.25 = 2.75`, `σ = 1.658` (numerically confirmed).

Classical: `⟨x⟩ = 0`, `σ² = t = 3`, `σ = 1.732`.

The quantum walk here has *smaller* spread — because at `t = 3` interference has concentrated `5/8` of the probability at `x = +1` (a constructive pile-up), and ballistic scaling `σ ≈ 0.54t` only dominates `√t` once `0.54t > √t`, i.e., `t ≳ 3.4`. The crossover is invisible in `O(1)`-step examples and decisive asymptotically: at `t = 100`, `σ_qu = 54.1` versus `σ_cl = 10` (verified numerically). Moral: quantum walk advantages are statements about scaling, and small cases are for exhibiting mechanisms — the same lesson as comparing Grover at `N = 4` versus `N = 2⁶⁴`.

</details>

## Further Reading

1. **Kempe**, "Quantum random walks: an introductory overview" (Contemporary Physics 44, 307, 2003; arXiv:quant-ph/0303081) — the classic readable survey of coined and continuous-time walks; the source of the line-walk analysis in this chapter
2. **Szegedy**, "Quantum speed-up of Markov chain based algorithms" (FOCS 2004) — the quantization of general Markov chains and the `√δ` phase-gap theorem; the foundation of the walk-search framework
3. **Ambainis**, "Quantum walk algorithm for element distinctness" (SIAM Journal on Computing 37, 210, 2007; FOCS 2004) — the `O(N^{2/3})` algorithm and the Johnson-graph walk technique that launched walk-based query algorithms
4. **Childs, Cleve, Deotto, Farhi, Gutmann & Spielman**, "Exponential algorithmic speedup by a quantum walk" (STOC 2003; arXiv:quant-ph/0209131) — the glued-trees problem: quantum `poly(n)` traversal and the classical `2^{Ω(n)}` lower bound
5. **Magniez, Nayak, Roland & Santha**, "Search via quantum walk" (SIAM Journal on Computing 40, 142, 2011) — the unified MNRS framework `Setup + (1/√ε)(Update/√δ + Check)` used by essentially all walk-search algorithms; see also Childs, "Universal computation by quantum walk" (PRL 102, 180501, 2009) for walks as a complete computational model
