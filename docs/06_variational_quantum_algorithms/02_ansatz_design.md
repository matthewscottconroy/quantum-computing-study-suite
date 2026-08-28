# Ansatz Design

> **Prerequisites**: VQE fundamentals (06/01), quantum gates and circuits (Chapter 3),
> Pauli operators
> **Connects to**: Barren plateaus (06/05), QAOA (06/04), VQE applications

---

## Overview

The ansatz — the parameterized quantum circuit family `{|ψ(θ)⟩}` used in VQE and other
variational algorithms — is arguably the most important design choice in the entire algorithm.
A bad ansatz is not merely inefficient: it may fail entirely, either by being inexpressive
(the ground state is not reachable) or by being untrainable (barren plateaus make optimization
impossible).

Ansatz design navigates a fundamental tension: **expressibility** versus **trainability**. A
highly expressive ansatz can in principle represent any state, but random high-depth circuits
suffer from exponentially vanishing gradients (barren plateaus, Chapter 06/05). Structured
ansätze trade some expressibility for meaningful gradients, but may be too restricted for the
target application.

This chapter systematically covers the major ansatz families — hardware-efficient, chemically
motivated, Hamiltonian variational, and adaptive — explaining the design principles, advantages,
and failure modes of each.

---

## What Makes a Good Ansatz?

### Desiderata

1. **Expressibility**: The ground state `|E₀⟩` (or a state within desired accuracy `ε` of it)
   is achievable: `min_θ ⟨ψ(θ)|H|ψ(θ)⟩ ≤ E₀ + ε`.

2. **Trainability**: Gradients `∂E/∂θᵢ` are non-exponentially small in the system size `n`.
   Vanishing gradients make classical optimization impossible.

3. **Implementability**: The circuit depth and gate count are feasible on available hardware
   (relevant qubit count, connectivity, error rates).

4. **Efficiency**: The number of parameters `m` is polynomial in system size, and each
   circuit evaluation requires polynomial resources.

These requirements often conflict. The challenge of ansatz design is to find the sweet spot for
a given problem and hardware.

### Expressibility Measure

The expressibility of an ansatz can be quantified by its ability to sample the Haar-random unitary
distribution (the distribution over all unitaries). Define:

```
Expr(A) = || ∫ dθ |ψ(θ)⟩⟨ψ(θ)|⊗2 - ∫ dU (U|0⟩⟨0|U†)⊗2 ||_F
```

Small `Expr` means the ansatz samples the entire state space nearly uniformly — which is
expressive but also a symptom of barren plateaus. High expressibility and high trainability
are in fundamental tension.

---

## Hardware-Efficient Ansatz (HEA)

### Structure

The **hardware-efficient ansatz** (Kandala et al., 2017) is designed for direct execution on
specific quantum hardware with minimal overhead. The typical structure is:

```
Layer 1: single-qubit rotations {Ry(θᵢ), Rz(φᵢ)} on all qubits
Layer 1: entanglement layer (CNOT or CZ on adjacent pairs, device topology)
Layer 2: single-qubit rotations
Layer 2: entanglement layer
...
(L layers total)
```

**Number of parameters**: `3nL` to `4nL` for `n` qubits and `L` layers.

**Hardware efficiency**: The CNOT pattern follows the device's native qubit connectivity
(e.g., heavy-hex topology on IBM devices, square lattice on Google devices), minimizing
circuit compilation overhead.

### Strengths and Weaknesses

**Strengths**:
- Deep circuits can be extremely expressive.
- No chemical knowledge required; applicable to any problem.
- Native gate set → minimal compilation errors.

**Weaknesses**:
- Severely prone to **barren plateaus** (Chapter 06/05): gradient variance decreases as
  `~2^{-n}` for depth `L ~ n` or global cost functions.
- No built-in symmetries: may prepare states that violate particle number conservation, wasting
  circuit complexity on unphysical states.
- Parameter landscapes are highly non-convex with many local minima.

### When to Use HEA

HEA is appropriate for:
- Small system sizes (`n ≤ 10`) where barren plateaus are not exponentially severe.
- Combinatorial optimization problems where the problem structure is hard to exploit.
- Initial benchmarking of hardware quality.

---

## Chemically Motivated Ansätze

### UCCSD (Unitary Coupled Cluster)

Reviewed in detail in Chapter 06/01. Key design principle: the circuit is derived from
the coupled cluster expansion of quantum chemistry, ensuring that physically relevant electron
correlations are captured.

```
|ψ_UCCSD⟩ = exp(Σ_{ia} θᵢᵃ(cₐ†cᵢ - cᵢ†cₐ) + Σ_{ijab} θᵢⱼᵃᵇ(cₐ†c_b†cⱼcᵢ - h.c.)) |HF⟩
```

**Strengths**: Systematically improvable, physically interpretable, connects to classical
quantum chemistry (CC theory).

**Weaknesses**: `O(N⁴)` parameters and circuit depth; training requires many circuit evaluations.

### k-UpCCGSD

The **k-unitary pair Coupled Cluster Generalized Singles and Doubles** (k-UpCCGSD) ansatz
(Lee et al., 2018) uses generalized (not just occupied→virtual) excitations paired with the
number operator to reduce circuit depth while maintaining accuracy:

```
|ψ(θ)⟩ = ∏_{l=1}^k exp(A^(l) + B^(l)) |HF⟩
```

where each layer `l` applies generalized single and double excitations. For `k ≥ 1`, this can
outperform UCCSD at lower circuit depth for some molecules.

### Particle-Conserving Ansätze

A key physical constraint: molecular ground states have fixed particle number `N_e` and spin.
Any ansatz that preserves `[H, N̂] = 0` can be restricted to the correct particle number sector,
reducing parameter space and improving trainability.

**Givens rotation ansatz**: Build the ansatz from Givens rotations on pairs of fermionic modes,
which by construction preserve particle number. These are equivalent to hardware-efficient
circuits of CNOT + single-qubit rotations but with guaranteed particle conservation.

---

## Hamiltonian Variational Ansatz (HVA)

### Principle

The **Hamiltonian variational ansatz** (Wecker et al., 2015) constructs the ansatz by
Trotterizing the Hamiltonian itself:

```
|ψ(θ)⟩ = ∏_{l=1}^L ∏_k e^{-i θₖˡ Hₖ} |ψ₀⟩
```

where `H = Σₖ Hₖ` is a decomposition of the Hamiltonian into commuting or non-commuting terms,
and each `e^{-iθHₖ}` is a parameterized rotation.

### Connection to Adiabatic Computation

HVA with increasing depth `L → ∞` and appropriate parameters approaches adiabatic quantum
computation: starting from an easy-to-prepare ground state `|ψ₀⟩` of a simple Hamiltonian `H₀`
and slowly evolving to the ground state of `H`. This guarantees that HVA can in principle reach
the exact ground state.

### Structure and Symmetries

If the Hamiltonian `H` commutes with a set of symmetry operators `{Sⱼ}`, and `|ψ₀⟩` is a
simultaneous eigenstate of all `Sⱼ`, then HVA preserves these symmetries by construction:
each factor `e^{-iθHₖ}` commutes with `Sⱼ` since `Hₖ` is a term in `H`. This equivariance
is a powerful inductive bias.

### QAOA as HVA

The QAOA circuit (Chapter 06/04) is precisely the HVA for a combinatorial optimization problem.
The cost Hamiltonian `H_C` and mixer `H_B` play the roles of the two terms in a decomposed
Hamiltonian. QAOA = `(e^{-iγH_C} e^{-iβH_B})^p`.

---

## ADAPT-VQE

### The Greedy Growth Strategy

**ADAPT-VQE** (Grimsley et al., 2019) avoids the need to specify the ansatz ahead of time by
growing it greedily from an **operator pool** `O = {Aₖ}`. The algorithm:

```
Initialize: |ψ(θ)⟩ = |HF⟩
Repeat:
  1. For each operator Aₖ in pool, compute gradient:
     ∂E/∂θₖ|_{θₖ=0} = ⟨ψ|[H, Aₖ]|ψ⟩
  2. Select Aₖ* with largest |∂E/∂θₖ|
  3. Append exp(θ* Aₖ*) to ansatz
  4. Re-optimize all θ parameters
Until: max |∂E/∂θₖ| < ε_adapt
```

The operator pool typically contains all UCCSD-type single and double excitation operators.

### ADAPT-VQE Advantages

- **Automatically compact**: grows only as large as needed; often needs far fewer parameters
  than full UCCSD.
- **Eliminates barren plateaus** (approximately): by selecting operators with non-zero gradients,
  ADAPT always starts with meaningful optimization directions.
- **Chemically informed**: the operators selected are physically meaningful excitations.

**Disadvantage**: Requires `|O| × (number of optimization steps)` circuit evaluations just to
select the next operator. For a pool of size `|O| ~ N^4/8`, this overhead can be significant.

---

## Layered Structure and Hardware Topology Matching

### Brick-Wall Circuits

A common practical structure is the **brick-wall** (or brickwork) pattern:

```
Layer 1: two-qubit gates on (1,2), (3,4), (5,6), ...
Layer 2: two-qubit gates on (2,3), (4,5), (6,7), ...
Layer 1 (again): ...
```

This pattern ensures every pair of adjacent qubits interacts with depth proportional to system
size. For depth `L` and `n` qubits, the circuit spans a light cone of size `min(L, n)`.

### Matching Hardware Connectivity

Real quantum devices have constrained qubit connectivity:
- **IBM heavy-hex**: each qubit connects to 2 or 3 others; good for 1D problems.
- **Google Sycamore**: 2D grid; each qubit has 4 neighbors.
- **IonQ**: all-to-all connectivity (via motional modes).

An ansatz that requires CNOT between non-adjacent qubits must use SWAP networks, roughly tripling
circuit depth per SWAP. Designing ansätze matching native connectivity reduces this overhead.

---

## Symmetry-Preserving and Equivariant Ansätze

Physical systems often have symmetries (particle number, spin, spatial symmetries). Symmetry-
preserving ansätze restrict the parameter space to symmetry-invariant states:

**Advantages**:
- Smaller effective parameter space → faster optimization.
- Physical constraints prevent wasted circuit complexity.
- Can improve expressibility within the relevant sector.

**Construction methods**:
1. **Symmetry verification**: run the ansatz and project to the symmetric subspace via
   post-selection or symmetry measurements.
2. **Equivariant gates**: use only gates that commute with the symmetry operators (e.g.,
   number-conserving Givens rotations for particle conservation).
3. **Fixed-point initialization**: initialize in the symmetric sector and use symmetric
   evolution operators to stay there.

---

## Key Formulas

- **HEA structure**: depth-`L` alternating rotation + entanglement layers; `~3nL` parameters
- **UCCSD**: `exp(T - T†)|HF⟩`, `T = T₁ + T₂`; `O(N⁴)` parameters
- **HVA**: `∏_l ∏_k exp(-iθₖˡHₖ)|ψ₀⟩`
- **ADAPT gradient selection**: `∂E/∂θₖ = ⟨ψ|[H, Aₖ]|ψ⟩`
- **Expressibility-trainability trade-off**: increasing expressibility `→` decreasing gradient
  magnitude `→` harder optimization

---

## Worked Example: ADAPT-VQE on H₂

**Setup**: the 2-qubit reduced H₂ Hamiltonian from Chapter 06/01 at `R = 0.735 Å`:
```
H = -1.052373 I + 0.397937 Z₁ - 0.397937 Z₂ - 0.011280 Z₁Z₂ + 0.180931 X₁X₂
```
Reference state `|HF⟩ = |10⟩` with `E_HF = -1.836968` Ha (electronic); exact ground energy
`E₀ = -1.857275` Ha. Operator pool (anti-Hermitian generators of the qubit-mapped excitations):
```
A₁ = i(X₁Y₂ - Y₁X₂)/2,   A₂ = i(X₁Y₂ + Y₁X₂)/2,   A₃ = i(Z₁Y₂ - Y₁Z₂)/2
```

**Iteration 1**:
- Compute pool gradients `∂E/∂θₖ|₀ = ⟨HF|[H, Aₖ]|HF⟩`. For `A₁`, only the `X₁X₂` term of
  `H` fails to commute with the excitation between `|10⟩` and `|01⟩`, and a direct evaluation
  gives `|⟨HF|[H, A₁]|HF⟩| = 2 × 0.180931 = 0.361862` Ha (verified numerically). The other
  pool gradients vanish: `A₂|HF⟩ = 0`, and `A₃` only connects `|HF⟩` to the orthogonal
  `{|00⟩, |11⟩}` block, which `H` does not couple to `|HF⟩`.
- `A₁` selected. Ansatz: `|ψ(θ₁)⟩ = exp(θ₁A₁)|HF⟩`, which rotates within the
  `{|01⟩, |10⟩}` block containing the ground state.
- Optimize `θ₁`: `θ₁* ≈ 0.1118` rad, `E = -1.857275` Ha — the exact ground energy of this
  2-qubit Hamiltonian, because a single generator already spans the relevant symmetry sector.

**Iteration 2**:
- Re-evaluate all pool gradients at `θ₁*`. All are `< 10⁻⁹` Ha (the state is an eigenstate,
  so `⟨ψ|[H, A]|ψ⟩ = 0` for every `A`).
- Convergence reached.

**Result**: 1 parameter recovers the full correlation energy (`-20.3` mHa below Hartree-Fock).
For H₂ the pool is tiny and one operator suffices; for larger molecules ADAPT-VQE typically
selects a handful of operators where full UCCSD would allocate hundreds — the compactness, and
the guaranteed non-zero initial gradient, are what suppress barren plateau problems.

---

## Summary

- Ansatz design is the central algorithmic choice in VQE; it must balance expressibility
  (reach the ground state), trainability (non-vanishing gradients), and implementability.
- **Hardware-efficient ansätze** are device-native but prone to barren plateaus and lack
  physical structure.
- **Chemically motivated ansätze** (UCCSD, k-UpCCGSD) are accurate but scale as `O(N⁴)`.
- **Hamiltonian variational ansätze** respect problem symmetry and connect to adiabatic
  computation; QAOA is the combinatorial optimization version.
- **ADAPT-VQE** grows the ansatz greedily using operator gradients, achieving compact circuits
  without specifying structure in advance.
- Symmetry preservation and hardware topology matching are critical practical considerations
  that can dramatically reduce circuit complexity and error rates.

---

## Exercises

**1.** A hardware-efficient ansatz on `n = 8` qubits uses `L = 5` layers, each consisting of
`Ry` and `Rz` rotations on every qubit followed by CNOTs on nearest neighbors in a line.
Count the trainable parameters and the CNOT gates.

<details><summary>Solution</summary>

Parameters: `2` rotations × `8` qubits × `5` layers = `80` parameters.
CNOTs: a line of 8 qubits has 7 nearest-neighbor pairs, so `7 × 5 = 35` CNOTs.
(Adding a final rotation layer after the last entangler, a common variant, would give
`2 × 8 × 6 = 96` parameters.)

</details>

**2.** The worked example in Chapter 06/01 shows that the ansatz
`cos(θ/2)|00⟩ + sin(θ/2)|11⟩` cannot represent the H₂ ground state, which lives in
`span{|01⟩, |10⟩}`. Explain this failure as a *symmetry mismatch* using the operator
`S = Z₁ + Z₂`.

<details><summary>Solution</summary>

`S = Z₁ + Z₂` generates a symmetry sector label: `|00⟩` and `|11⟩` have `S`-eigenvalues `+2`
and `-2`, while `|01⟩` and `|10⟩` both have `S = 0`. In the parity-mapped H₂ Hamiltonian,
the physical 2-electron sector corresponds to `S = 0`. The Bell-type ansatz is confined to the
`S = ±2` sectors for every `θ`, so no parameter value can produce any overlap with the ground
state — its variational minimum (`-1.244585` Ha) is simply the lowest eigenvalue *within the
wrong sector*. A symmetry-preserving ansatz starts from a reference in the correct sector
(here `|HF⟩ = |10⟩`) and uses only `S`-conserving gates.

</details>

**3.** For the H₂ setup of the worked example, show that the ADAPT initial gradient satisfies
`⟨HF|[H, A₁]|HF⟩ = ±2c₄`, where `c₄ = 0.180931` is the `X₁X₂` coefficient and
`A₁ = i(X₁Y₂ - Y₁X₂)/2`.

<details><summary>Solution</summary>

Only the `X₁X₂` term of `H` contributes: all diagonal terms (`I`, `Z₁`, `Z₂`, `Z₁Z₂`) map
`|10⟩` to a multiple of itself, and for those `⟨HF|[·, A₁]|HF⟩ = ⟨HF|D A₁ - A₁ D|HF⟩` reduces
to `(d_{10} - d_{10})⟨HF|A₁|HF⟩`-type expressions that vanish because `⟨10|A₁|10⟩ = 0`
(`A₁|10⟩ ∝ |01⟩`). Direct computation: `A₁|10⟩ = -|01⟩` and `X₁X₂|10⟩ = |01⟩`, so
`⟨10|[c₄X₁X₂, A₁]|10⟩ = c₄(⟨10|X₁X₂A₁|10⟩ - ⟨10|A₁X₁X₂|10⟩) = c₄(-1 - 1) = -2c₄ = -0.361862` Ha.
Numerical check (4×4 matrices): `⟨HF|[H, A₁]|HF⟩ = -0.361862`. ✓

</details>

**4.** Using the barren plateau bound `Var[∂E/∂θ] ≤ 2/4ⁿ` for a deep unstructured HEA with a
global cost, estimate the shots needed to distinguish one gradient component from shot noise
(SNR = 1, i.e., `S ≈ 1/Var`) at `n = 12`. Compare with a structured ansatz whose gradient
variance is `1/n²`.

<details><summary>Solution</summary>

Unstructured: `Var ≤ 2/4¹² ≈ 1.2 × 10⁻⁷`, so `S ≈ 1/Var ≈ 8.4 × 10⁶` shots per gradient
component per iteration. Structured with `Var ≈ 1/n² = 1/144 ≈ 7 × 10⁻³`: `S ≈ 144` shots.
The five-orders-of-magnitude gap at just 12 qubits — growing as `4ⁿ` — is why ansatz structure,
not optimizer cleverness, decides trainability.

</details>

---

## Further Reading

1. **Kandala, A. et al.** — "Hardware-efficient variational quantum eigensolver for small
   molecules and quantum magnets," *Nature* 549, 242 (2017). Original HEA paper.
2. **Grimsley, H. R. et al.** — "An adaptive variational algorithm for exact molecular
   simulations on a quantum computer," *Nature Communications* 10, 3007 (2019). ADAPT-VQE.
3. **Lee, J. et al.** — "Generalized unitary coupled cluster wave functions for quantum
   computation," *J. Chem. Theory Comput.* 15, 311 (2019). k-UpCCGSD.
4. **Wecker, D. et al.** — "Progress towards practical quantum advantage in quantum chemistry,"
   *Phys. Rev. A* 92, 042303 (2015). Hamiltonian variational ansatz.
5. **Sim, S., Johnson, P. D., and Aspuru-Guzik, A.** — "Expressibility and entangling capability
   of parameterized quantum circuits for hybrid quantum-classical algorithms," *Adv. Quantum
   Technol.* 2, 1900070 (2019). Quantitative expressibility measures.
