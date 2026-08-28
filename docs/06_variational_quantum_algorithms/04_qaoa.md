# QAOA: Quantum Approximate Optimization Algorithm

> **Prerequisites**: VQE fundamentals (06/01), Hamiltonian variational ansatz (06/02),
> combinatorial optimization basics
> **Connects to**: Barren plateaus (06/05), adiabatic quantum computation, quantum advantage

---

## Overview

The Quantum Approximate Optimization Algorithm (QAOA), introduced by Farhi, Goldstone, and
Gutmann in 2014, is the canonical near-term quantum algorithm for combinatorial optimization.
It targets problems like MaxCut, MAXSAT, and graph coloring — problems where the task is to
find a binary assignment that maximizes a classical objective function.

QAOA is elegant in its simplicity: a depth-`p` QAOA circuit alternates between applying the
problem's cost function as a quantum unitary and applying a transverse-field "mixer" unitary,
sweeping through a series of angles `(γ₁,...,γₚ, β₁,...,βₚ)`. At `p = 1` it gives provable
(if modest) approximation guarantees; as `p → ∞` it converges to the adiabatic quantum annealing
limit, provably reaching the exact optimum.

The theoretical analysis of QAOA is one of the richest areas of quantum algorithms research,
connecting to adiabatic computation, variational methods, random matrix theory, and
computational complexity. Whether QAOA achieves quantum advantage over the best classical
algorithms (like the Goemans-Williamson SDP algorithm) is a central open question in the field.

---

## MaxCut: The Canonical Problem

### Problem Definition

Given an undirected graph `G = (V, E)` with vertex set `V` and edge set `E`, the **MaxCut**
problem asks for a partition of `V` into sets `S` and `V\S` such that the number of edges
crossing the partition (the cut) is maximized:

```
MaxCut(G) = max_{z ∈ {0,1}^n} |{(i,j) ∈ E : zᵢ ≠ zⱼ}|
```

Or in `{±1}` spin notation (`zᵢ → sᵢ = (-1)^{zᵢ}`):

```
MaxCut(G) = max_{s ∈ {±1}^n} (1/2) Σ_{(i,j)∈E} (1 - sᵢsⱼ)
            = |E|/2 + (1/2) max_{s} -Σ_{(i,j)∈E} sᵢsⱼ
```

MaxCut is NP-hard in general. For 3-regular graphs, the maximum cut is at most `|E| = 3n/2`
edges. MaxCut is the prototype of a combinatorial optimization problem that QAOA targets.

### Cost Hamiltonian

Map spin variable `sᵢ → Zᵢ` (the Pauli Z on qubit `i`). The cost Hamiltonian is:

```
H_C = (1/2) Σ_{(i,j)∈E} (I - ZᵢZⱼ)
```

`H_C` has eigenvalues equal to the number of edges in the cut for each computational basis
state `|z⟩ = |z₁,...,zₙ⟩`. Maximizing `⟨H_C⟩` maximizes the expected cut value.

---

## The QAOA Circuit

### Structure

The depth-`p` QAOA circuit starts from the superposition state `|s⟩ = |+⟩^⊗n = H^⊗n|0⟩^⊗n`
and applies alternating unitaries:

```
|ψ_QAOA(γ,β)⟩ = U_M(βₚ) U_C(γₚ) ... U_M(β₁) U_C(γ₁) |+...+⟩
```

where:
- **Cost unitary**: `U_C(γ) = e^{-iγH_C} = ∏_{(i,j)∈E} e^{-iγ(I-ZᵢZⱼ)/2}`
- **Mixer unitary**: `U_M(β) = e^{-iβH_B}` where `H_B = Σᵢ Xᵢ` (transverse field)

Each factor `e^{-iγ(I-ZᵢZⱼ)/2}` is a two-qubit gate (phase rotation between qubits `i` and `j`),
and each `e^{-iβXᵢ}` is a single-qubit X rotation.

### Parameters

The variational parameters are `γ = (γ₁,...,γₚ) ∈ [0,2π)^p` and `β = (β₁,...,βₚ) ∈ [0,π)^p`.
The QAOA objective is:

```
F_p(γ,β) = ⟨ψ_QAOA(γ,β)|H_C|ψ_QAOA(γ,β)⟩
```

Optimize over `(γ,β)` to find:
```
C_p = max_{γ,β} F_p(γ,β)
```

The **approximation ratio** is `r_p = C_p / MaxCut(G)`.

---

## QAOA at Depth p=1: Analytic Results

### Exact Formula for MaxCut on 3-Regular Graphs

For 3-regular graphs (every vertex has degree 3), Farhi et al. derived an analytic formula for
the depth-1 QAOA approximation ratio. For an edge `(u,v)`, the contribution to `F₁(γ,β)` is:

```
⟨(I - ZᵤZᵥ)/2⟩ = (1/2)[1 - ⟨ZᵤZᵥ⟩]
```

By the locality of the depth-1 circuit, this can be computed exactly by considering only the
local neighborhood of the edge `(u,v)`. For a **triangle-free** `d`-regular graph the result is:

```
F₁(γ,β) = |E| · [1/2 + (1/2) sin(4β) sin(γ) cos^{d-1}(γ)]
```

(graphs with triangles acquire an extra correction term; triangle-free is the worst case for
3-regular graphs). For `d = 3`, maximizing `sin(γ)cos²(γ)` gives `sin(γ*) = 1/√3`, i.e.
`γ* = 0.6155` rad, and `sin(4β*) = 1` gives `β* = π/8 = 0.3927` rad, so:

```
F₁/|E| = 1/2 + (1/2)(1/√3)(2/3) = 0.6924
r₁ = C₁ / MaxCut ≥ 0.6924
```

(Numerical check: simulating depth-1 QAOA on the 3-regular triangle-free graph `K₃,₃` at
`(γ*, β*)` gives `F₁ = 6.2321 = 9 × 0.69245`. ✓)

This means QAOA at depth 1 guarantees at least `69.24%` of the optimal cut for any 3-regular
graph. This is a **provable, unconditional** approximation guarantee — one of the few in quantum
algorithms.

### Comparison to Classical Algorithms

The best classical polynomial-time algorithm for MaxCut is the **Goemans-Williamson (GW) SDP
algorithm** (1995), which achieves approximation ratio `0.878` (unconditionally) and is tight
under the Unique Games Conjecture. The depth-1 QAOA ratio `0.6924` is worse than GW.

At depth `p = 11`, numerical evidence suggests QAOA exceeds GW for 3-regular graphs. Proving
or disproving this is an open question.

---

## QAOA at Large p: Adiabatic Limit

### Trotterized Adiabatic Theorem

**Theorem**: As `p → ∞` with appropriate choice of `(γ,β)`, the QAOA converges to the
adiabatic quantum annealing limit and reaches the exact ground state of `H_C`.

**Argument**: Choose the angles to implement a Trotter approximation of the adiabatic path:
start with `H_B` as the initial Hamiltonian and slowly evolve to `H_C`. The adiabatic theorem
guarantees convergence to the ground state for slow enough annealing. QAOA with the "Trotterized
adiabatic" parameter schedule achieves this in the limit `p → ∞`.

This theorem proves that QAOA is in principle **exact** — it can solve MaxCut exactly for
sufficiently large `p`. The question is: how large must `p` be, and can quantum hardware
implement that depth before noise destroys the computation?

### Parameter Concentration

A remarkable property of QAOA for large random instances: **optimal parameters `(γ*,β*)` 
concentrate** — they become approximately independent of the specific graph instance as `n → ∞`.

For a fixed `p`, the optimal parameters for a random 3-regular graph on `n` vertices converge
(as `n → ∞`) to deterministic values. This means:
1. The QAOA parameters can be pre-computed on small instances and transferred to large ones.
2. Classical pre-training can reduce the optimization cost for quantum hardware.

---

## Classical Competition: Goemans-Williamson

### SDP Relaxation

The GW algorithm relaxes the MaxCut integer program to a semidefinite program (SDP). Associate
a unit vector `vᵢ ∈ ℝ^n` with each vertex `i`. The SDP maximizes:

```
max Σ_{(i,j)∈E} (1 - vᵢ · vⱼ) / 2   subject to |vᵢ| = 1
```

The SDP solution can be computed in polynomial time. Then randomly project: generate a random
vector `r`, assign `sᵢ = sign(vᵢ · r)`. The expected cut value satisfies:

```
E[cut] ≥ α_GW × MaxCut   where   α_GW = min_{0<θ<π} 2θ/(π(1-cos θ)) ≈ 0.878
```

### Why GW is Strong

The GW bound 0.878 is known to be tight under the **Unique Games Conjecture** (Khot, 2002):
no polynomial-time algorithm can achieve approximation ratio `> 0.878` for MaxCut unless UGC
fails. Under UGC, GW is the optimal classical algorithm.

**Implications for QAOA**: If QAOA at polynomial depth achieves `> 0.878`, it either violates
UGC or provides superpolynomial quantum advantage. This is the precise theoretical question about
quantum advantage for combinatorial optimization.

---

## Beyond MaxCut: QAOA Variants

### MAXSAT and Combinatorial Optimization

QAOA generalizes directly to any problem expressible as a quadratic unconstrained binary
optimization (QUBO):

```
H_C = Σᵢ hᵢ Zᵢ + Σ_{i<j} Jᵢⱼ ZᵢZⱼ
```

This covers Ising model ground-state finding, portfolio optimization, drug design, logistics
planning, and many other NP-hard problems.

### Constrained Optimization (QAOA+)

For constrained optimization (e.g., only valid colorings, or fixed particle number), the standard
transverse-field mixer can leave the feasible subspace. Modified mixers (Hadfield et al., 2019)
preserve feasibility:
- **Ring mixer**: `XᵢXⱼ + YᵢYⱼ` for particle-conserving problems.
- **Grover mixer**: optimal mixer for fully constrained problems.

---

## Key Formulas

- **Cost Hamiltonian (MaxCut)**: `H_C = (1/2) Σ_{(i,j)∈E} (I - ZᵢZⱼ)`
- **QAOA circuit**: `|ψ(γ,β)⟩ = ∏_{l=p}^1 [e^{-iβₗΣXᵢ} e^{-iγₗH_C}] |+⟩^⊗n`
- **Cost unitary**: `U_C(γ) = e^{-iγH_C} = ∏_{(ij)∈E} e^{-iγ(I-ZᵢZⱼ)/2}`
- **Mixer unitary**: `U_M(β) = ⊗ᵢ e^{-iβXᵢ} = ⊗ᵢ Rx(2β)`
- **p=1 approximation ratio (3-regular MaxCut)**: `r₁ = 0.6924`
- **Goemans-Williamson ratio**: `0.878` (optimal under UGC)
- **Adiabatic limit**: `p → ∞` QAOA → exact optimal solution

---

## Worked Example: QAOA on a 4-Vertex Triangle + Edge Graph

**Graph**: Vertices `{1,2,3,4}`, edges `{(1,2),(2,3),(3,1),(1,4)}` — a triangle with a pendant
edge. **MaxCut = 3**: a triangle contributes at most 2 of its 3 edges to any cut, and the
pendant edge `(1,4)` can always be cut, so the best possible is `2 + 1 = 3` (e.g., partition
`S = {1}` cuts `(1,2), (3,1), (1,4)`; also `S = {2,4}` cuts `(1,2), (2,3), (1,4)`). No
partition cuts all 4 edges.

**Cost Hamiltonian**:
```
H_C = (1/2)[(I-Z₁Z₂) + (I-Z₂Z₃) + (I-Z₃Z₁) + (I-Z₁Z₄)]
    = 2I - (Z₁Z₂ + Z₂Z₃ + Z₃Z₁ + Z₁Z₄)/2
```
Its largest eigenvalue is 3, attained on the six optimal cut bitstrings.

**Depth-1 QAOA circuit** (`n=4` qubits):
1. Prepare `|++++⟩ = H⊗4|0000⟩`
2. Apply `U_C(γ) = e^{-iγH_C}`: for each edge `(i,j)`, apply the two-qubit phase
   `e^{-iγ(I-ZᵢZⱼ)/2}` (an `Rzz` rotation plus phase, compiled as
   `CNOT_{i→j} · Rz(-γ)_j · CNOT_{i→j}` up to the global phase `e^{-iγ/2}`, with the
   convention `Rz(θ) = e^{-iθZ/2}`)
3. Apply `U_M(β)`: apply `e^{-iβXᵢ} = Rx(2β)` to each qubit.

**Parameter optimization** (exact statevector simulation of the 16-dimensional system):

```
At (γ, β) = (0.4, 0.4):     F₁ = 2.593,  ratio = 2.593/3 = 0.864
At the optimum (γ*, β*) ≈ (0.652, 1.901):  F₁* = 2.713,  ratio = 0.904
```

Both exceed the worst-case 3-regular guarantee of 0.6924, illustrating that
instance-specific optimization on small graphs typically far exceeds the worst-case bound.
(Note `F₁* < 3`: depth-1 QAOA does not reach the optimum exactly.)

**Measurement**: Sampling from `|ψ(γ*, β*)⟩`, the four balanced optimal cuts `|1100⟩, |1010⟩,
|0101⟩, |0011⟩` (writing `z₁z₂z₃z₄`) appear with probability `0.132` each and the two
singleton-1 cuts `|1000⟩, |0111⟩` with probability `0.105` each — in total, an optimal cut is
sampled with probability `≈ 0.74` per shot, so a handful of shots suffices to find the true
MaxCut for this instance.

---

## Summary

- QAOA is a depth-`p` parameterized circuit alternating cost and mixer unitaries, targeting
  combinatorial optimization problems.
- At `p=1`, QAOA achieves a provable approximation ratio of 0.6924 for MaxCut on 3-regular
  graphs — a rare unconditional guarantee in quantum algorithms.
- The Goemans-Williamson SDP achieves 0.878; QAOA surpassing GW at polynomial depth would
  imply quantum advantage for combinatorial optimization (under UGC).
- As `p → ∞`, QAOA approaches adiabatic quantum annealing and converges to the exact optimum.
- **Parameter concentration** allows pre-computing optimal angles on small instances and
  transferring them to large ones, reducing optimization overhead.
- QAOA generalizes to arbitrary QUBO problems and constrained optimization via modified mixers.

---

## Exercises

**1.** For the 5-cycle `C₅` (vertices `0..4`, edges forming a ring), find MaxCut by hand. Then,
using the triangle-free formula with `d = 2`, find the optimal depth-1 angles and the value
`F₁*`. What approximation ratio does depth-1 QAOA achieve on `C₅`?

<details><summary>Solution</summary>

An odd cycle cannot be 2-colored, so at least one edge is uncut: `MaxCut(C₅) = 4`.
For `d = 2`: `F₁ = 5[1/2 + (1/2)sin(4β)sin(γ)cos(γ)] = 5[1/2 + (1/4)sin(4β)sin(2γ)]`,
maximized at `β* = π/8`, `γ* = π/4`, giving `F₁* = 5 × 3/4 = 3.75` (statevector simulation
confirms `F₁(π/4, π/8) = 3.7500`). Ratio: `3.75/4 = 0.9375` — well above the 3-regular
worst case because low degree helps depth-1 QAOA.

</details>

**2.** Show that the cost unitary factor for one edge acts on computational basis states as
`e^{-iγ(I-ZᵢZⱼ)/2}|zᵢzⱼ⟩ = |zᵢzⱼ⟩` if `zᵢ = zⱼ` and `e^{-iγ}|zᵢzⱼ⟩` if `zᵢ ≠ zⱼ`.

<details><summary>Solution</summary>

`(I - ZᵢZⱼ)/2` has eigenvalue `0` on aligned states (`ZᵢZⱼ = +1`) and `1` on anti-aligned
states (`ZᵢZⱼ = -1`). Exponentiating a diagonal operator applies `e^{-iγ·(eigenvalue)}`:
phase `1` for aligned, `e^{-iγ}` for anti-aligned. Summing over edges, `U_C(γ)` applies the
phase `e^{-iγ·cut(z)}` to basis state `|z⟩` — the cost function enters the circuit purely as
a cut-dependent phase, which is why `U_C` is cheap to implement.

</details>

**3.** For depth `p = 3` QAOA on a 3-regular graph with `n = 16` vertices: how many variational
parameters, how many edges, and how many CNOT gates (compiling each edge phase as
CNOT-Rz-CNOT) does one circuit execution use?

<details><summary>Solution</summary>

Parameters: `2p = 6` (namely `γ₁,γ₂,γ₃,β₁,β₂,β₃`) — independent of `n`; this is why QAOA
avoids some barren plateau issues at low depth. Edges: `|E| = 3n/2 = 24`. CNOTs: each of the
24 edge phases needs 2 CNOTs per layer, so `2 × 24 × 3 = 144` CNOTs (plus `16 × 3 = 48`
single-qubit `Rx` gates and 16 initial Hadamards).

</details>

**4.** A 3-regular graph instance has `MaxCut = 100`. What expected cut value must QAOA achieve
to beat (a) the depth-1 worst-case guarantee, (b) the Goemans-Williamson guarantee? If depth-1
QAOA on this instance reaches `F₁ = 85`, has it demonstrated any quantum advantage?

<details><summary>Solution</summary>

(a) `0.6924 × 100 = 69.24`. (b) `0.878 × 100 = 87.8`. An instance value of `F₁ = 85` beats
the QAOA worst case but is *below* the GW guarantee — and GW is a polynomial-time classical
algorithm, so no advantage is demonstrated. Even exceeding 87.8 on one instance would prove
nothing: GW's 0.878 is a worst-case bound, and on typical instances both classical heuristics
and GW do much better. Claims of quantum advantage require beating the *best classical
algorithm on the same instances*, not a worst-case constant.

</details>

---

## Further Reading

1. **Farhi, E., Goldstone, J., and Gutmann, S.** — "A quantum approximate optimization algorithm,"
   arXiv:1411.4028 (2014). The original QAOA paper.
2. **Goemans, M. X. and Williamson, D. P.** — "Improved approximation algorithms for maximum cut
   and satisfiability problems using semidefinite programming," *J. ACM* 42, 1115 (1995). GW SDP.
3. **Guerreschi, G. G. and Matsuura, A. Y.** — "QAOA for MaxCut requires hundreds of qubits for
   quantum speed-up," *Sci. Rep.* 9, 6903 (2019). Resource analysis.
4. **Farhi, E. and Harrow, A. W.** — "Quantum supremacy through the quantum approximate
   optimization algorithm," arXiv:1602.07674 (2016). Complexity arguments for QAOA.
5. **Hadfield, S. et al.** — "From the quantum approximate optimization algorithm to a quantum
   alternating operator ansatz," *Algorithms* 12, 34 (2019). Constrained QAOA variants.
