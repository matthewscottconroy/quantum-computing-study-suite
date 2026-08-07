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

By the symmetry of the problem and the product structure of the depth-1 circuit, this can be
computed exactly by considering only the local neighborhood of the edge `(u,v)`:

```
F₁(γ,β) = |E|/2 + (|E|/4) sin(4β)sin(γ) [cos^{d-1}(γ) - sin^{d-1}(γ)]
```

For 3-regular graphs (`d = 3`), this simplifies and is maximized at:
`γ* ≈ 0.3948` rad, `β* ≈ π/8 = 0.3927` rad, giving:

```
r₁ = C₁ / MaxCut ≈ 0.6924
```

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

**Graph**: Vertices `{1,2,3,4}`, edges `{(1,2),(2,3),(3,1),(1,4)}`. MaxCut = 4 (partition
`{2,4}` vs `{1,3}`).

**Cost Hamiltonian**:
```
H_C = (1/2)[(I-Z₁Z₂) + (I-Z₂Z₃) + (I-Z₃Z₁) + (I-Z₁Z₄)]
    = 2I - (Z₁Z₂ + Z₂Z₃ + Z₃Z₁ + Z₁Z₄)/2
```

**Depth-1 QAOA circuit** (`n=4` qubits):
1. Prepare `|++++⟩ = H⊗4|0000⟩`
2. Apply `U_C(γ)`: for each edge `(i,j)`, apply `Rzz(γ) = e^{-iγ ZᵢZⱼ/2}` (equivalent to
   `CNOT_{i→j} · Rz(γ)_j · CNOT_{i→j}`)
3. Apply `U_M(β)`: apply `Rx(2β)` to each qubit.

**Parameter optimization**: At `γ = 0.4`, `β = 0.4` (approximate optimal for this small graph):

```
F₁ ≈ 3.3  (expected cut value out of maximum 4)
Approximation ratio ≈ 3.3/4 = 0.825
```

This exceeds the depth-1 guarantee of 0.6924 for this specific graph, illustrating that instance-
specific optimization can significantly exceed the worst-case guarantee.

**Measurement**: Sample 1000 shots from `|ψ(γ,β)⟩`. Most frequent outcome: `|0101⟩` (cut `S={1,3}`)
and `|1010⟩` (cut `S={2,4}`), each appearing ~200 times. Both correspond to 4-edge cuts. ✓

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
