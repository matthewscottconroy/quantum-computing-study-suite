# Quantum Computing

## Goal
Build a comprehensive, rigorous understanding of the quantum computing model — from circuits and complexity to error correction and fault tolerance — sufficient to understand, implement, and analyze quantum algorithms.

---

## Module 1 — The Quantum Circuit Model

**Objective:** Master the standard model of quantum computation — the framework in which all major algorithms are expressed.

| Topic | Key Concepts |
|---|---|
| Qubits and registers | n-qubit state in ℂ^(2ⁿ) |
| Single-qubit gates | X, Y, Z, H, S, T, Rₓ, Rᵧ, R_z, U |
| Two-qubit gates | CNOT, CZ, SWAP, iSWAP, CPhase |
| Three-qubit gates | Toffoli (CCNOT), Fredkin (CSWAP) |
| Circuit diagram conventions | Wires = qubits, boxes = gates, measurements |
| Gate depth and width | Circuit complexity metrics |
| Classical control | Conditioned gates, deferred measurement principle |

**Exercises:**
- Implement a circuit that prepares all four Bell states

<details><summary>Solution</summary>

One circuit with two classical switches does all four. Prepare the computational
state `|xy⟩`, apply `H` to the first qubit, then `CNOT` (first → second).

After the Hadamard:

```
(H ⊗ I)|xy⟩ = (|0y⟩ + (−1)^x |1y⟩)/√2
```

`CNOT` leaves `|0y⟩` untouched and maps `|1y⟩ → |1ȳ⟩`, so

```
|β_xy⟩ = (|0y⟩ + (−1)^x |1ȳ⟩)/√2
```

which enumerates the Bell basis:

- `x=0, y=0` → `|Φ⁺⟩ = (|00⟩ + |11⟩)/√2`
- `x=0, y=1` → `|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2`
- `x=1, y=0` → `|Φ⁻⟩ = (|00⟩ − |11⟩)/√2`
- `x=1, y=1` → `|Ψ⁻⟩ = (|01⟩ − |10⟩)/√2`

So the "switches" are just Pauli gates before the entangler: `x` flips the sign
(a `Z` on either qubit) and `y` swaps the parity (an `X` on either qubit). All
four states are local-unitary equivalent, as they must be — the entangler is the
same in each case.

Stabilizer picture (worth internalising for Module 4): the Bell basis is the
simultaneous eigenbasis of the commuting pair `X⊗X` and `Z⊗Z`, and the two bits
`x, y` are exactly the two eigenvalues:

- `|Φ⁺⟩`: `X⊗X = +1`, `Z⊗Z = +1`
- `|Ψ⁺⟩`: `X⊗X = +1`, `Z⊗Z = −1`
- `|Φ⁻⟩`: `X⊗X = −1`, `Z⊗Z = +1`
- `|Ψ⁻⟩`: `X⊗X = −1`, `Z⊗Z = −1`

A Bell measurement is nothing but measuring these two stabilizers.

Checked in Qiskit (`Statevector`, amplitudes keyed by `|q₁q₀⟩` — remember
Qiskit prints little-endian, so the roles of the two bits read right-to-left):
`β00 → {00: 0.7071, 11: 0.7071}`, `β01 → {01: 0.7071, 10: 0.7071}`,
`β10 → {00: 0.7071, 11: −0.7071}`, `β11 → {01: −0.7071, 10: 0.7071}`.

</details>

- Show that Toffoli + ancilla can simulate any reversible classical computation

<details><summary>Solution</summary>

Two steps: Toffoli is universal for Boolean logic, then Bennett's trick makes the
simulation reversible and garbage-free.

**Step 1 — Toffoli computes a universal gate set.** `TOF(a, b, c)` maps
`(a, b, c) → (a, b, c ⊕ ab)`. Fixing inputs gives:

- `NAND`: `TOF(a, b, 1) → (a, b, 1 ⊕ ab) = (a, b, ¬(a ∧ b))`
- `AND`: `TOF(a, b, 0) → (a, b, a ∧ b)`
- `NOT`: `TOF(1, 1, c) → (1, 1, ¬c)`
- `FANOUT`/`COPY`: `TOF(a, 1, 0) → (a, 1, a)`

`{NAND, FANOUT}` is universal for Boolean circuits, so any `f: {0,1}ⁿ → {0,1}ᵐ`
computed by a classical circuit of `s` gates can be computed by `s` Toffolis, each
writing its output onto a fresh ancilla initialised to `0` or `1`.

**Step 2 — remove the garbage (Bennett, 1973).** The circuit above realises

```
|x⟩|0…0⟩|0ᵐ⟩  →  |x⟩|g(x)⟩|f(x)⟩
```

where `g(x)` is the record of the `s` intermediate wire values. Now CNOT the
output register into `m` fresh output qubits, then run the whole circuit in
reverse (Toffoli is its own inverse, so "reverse" means applying the same gates in
the opposite order). Uncomputation restores the ancillas:

```
|x⟩|0…0⟩|0ᵐ⟩|0ᵐ⟩ → |x⟩|g(x)⟩|f(x)⟩|0ᵐ⟩ → |x⟩|g(x)⟩|f(x)⟩|f(x)⟩ → |x⟩|0…0⟩|0ᵐ⟩|f(x)⟩
```

The net map is `|x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩`, the standard reversible embedding — a
permutation of basis states, hence unitary, hence a legal quantum oracle. Cost:
`2s` Toffolis, `s` ancillas, `m` CNOTs, and a constant-factor depth increase.
Space can be traded against time (Bennett's pebble games) if `s` ancillas is too
many.

**Why the ancilla is genuinely necessary.** A gate acting on `k` of `n` bits
permutes the `2ⁿ` basis strings in `2ⁿ⁻ᵏ` disjoint blocks. A Toffoli on `n ≥ 4`
bits is therefore `2ⁿ⁻³` transpositions — an **even** permutation (`n=4`: 2 swaps;
`n=5`: 4 swaps; only at `n=3` is it a single swap and thus odd). The same is true
of `NOT` (`2ⁿ⁻¹` swaps) and `CNOT` (`2ⁿ⁻²` swaps) for `n ≥ 3`. So on a fixed
register of `n ≥ 4` bits these gates generate only the alternating group — odd
permutations such as a single transposition of two strings are unreachable.
One extra ancilla bit makes the target permutation act on `n+1` bits, where it
doubles into an even permutation, and reachability is restored. Hence the exercise
statement's "+ ancilla" is not a convenience, it is a parity obstruction.

</details>

- Prove the deferred measurement principle

<details><summary>Solution</summary>

**Claim.** Measuring a qubit and then applying a unitary conditioned on the
classical outcome is equivalent — same outcome distribution, same final state of
everything — to applying the corresponding coherently-controlled unitary first and
measuring at the end.

**Setup.** Let the measured qubit be `M` and the rest `R`, in a joint state `|ψ⟩`.
Let `P_i = |i⟩⟨i|_M ⊗ I_R` for `i ∈ {0,1}` and let the feed-forward operation be
`U_0` (on outcome 0) and `U_1` (on outcome 1). The coherent version is the
controlled unitary

```
CU = Σ_i |i⟩⟨i|_M ⊗ U_i
```

**Key identity.** `CU` commutes past the projectors in exactly the way we need:

```
P_i · CU = (|i⟩⟨i| ⊗ U_i) = CU · P_i
```

**Route A (measure first).** Outcome `i` occurs with probability
`p_i = ‖P_i|ψ⟩‖²`, and the conditional post-state is `(I ⊗ U_i)P_i|ψ⟩/√p_i`.
The full description (classical outcome + quantum state) is the ensemble

```
ρ_A = Σ_i |i⟩⟨i|_flag ⊗ (I ⊗ U_i) P_i |ψ⟩⟨ψ| P_i (I ⊗ U_i)†
```

**Route B (control first).** Apply `CU`, then measure `M`. Outcome `i` has
probability `‖P_i CU|ψ⟩‖² = ‖(I ⊗ U_i) P_i |ψ⟩‖² = ‖P_i|ψ⟩‖² = p_i` (unitaries
preserve norm), and the post-state is `P_i CU|ψ⟩/√p_i = (I ⊗ U_i)P_i|ψ⟩/√p_i`.
So

```
ρ_B = Σ_i |i⟩⟨i|_flag ⊗ (I ⊗ U_i) P_i |ψ⟩⟨ψ| P_i (I ⊗ U_i)† = ρ_A
```

Term by term, `ρ_A = ρ_B`. Since every later operation and measurement acts on
this same object, *all* subsequent statistics agree. Induction over the circuit
extends this to any number of deferred measurements: push each one to the end,
one at a time. ∎

**Reading the result both ways.**

- *Theory direction*: mid-circuit measurement and classical feed-forward add no
  computational power, so proofs may assume all measurements are terminal (this is
  why "measure at the end" is the standard circuit model, and why teleportation's
  Pauli corrections can be drawn as controlled gates).
- *Engineering direction*: the equivalence is not free. Deferring costs qubits —
  the measured qubit must stay coherent to the end instead of being measured and
  reset — and converts a cheap classical `if` into a genuine two-qubit gate. Real
  QEC does the opposite of deferring: it measures syndromes as early and as often
  as possible, precisely to stop errors accumulating.

</details>

---

## Module 2 — Universality

**Objective:** Understand what it means for a gate set to be universal and which sets achieve it.

| Topic | Key Concepts |
|---|---|
| Universal gate set | Can approximate any unitary to arbitrary precision |
| Solovay-Kitaev theorem | {H, T, CNOT} is universal; approximation depth is O(log^c(1/ε)) |
| Clifford + T | Standard universal gate set in fault-tolerant contexts |
| Continuous vs discrete | Continuous parameter gates vs finite discrete sets |
| Entangling power | Why CNOT is needed alongside single-qubit gates |
| Gate synthesis | Decomposing arbitrary unitaries into gate sets |

**Exercises:**
- Decompose an arbitrary single-qubit gate using ZYZ decomposition

<details><summary>Solution</summary>

**Theorem (ZYZ / Euler).** For every `U ∈ U(2)` there exist real `α, β, γ, δ` with

```
U = e^{iα} R_z(β) R_y(γ) R_z(δ),   R_z(θ) = diag(e^{−iθ/2}, e^{iθ/2}),
                                   R_y(θ) = [[cos(θ/2), −sin(θ/2)],
                                             [sin(θ/2),  cos(θ/2)]]
```

**Derivation.** Multiplying the three factors out:

```
e^{iα} · [[ e^{−i(β+δ)/2} cos(γ/2),  −e^{−i(β−δ)/2} sin(γ/2) ],
          [ e^{ i(β−δ)/2} sin(γ/2),   e^{ i(β+δ)/2} cos(γ/2) ]]
```

Unitarity of `U` forces `|U₀₀| = |U₁₁|` and `|U₀₁| = |U₁₀|` with
`|U₀₀|² + |U₁₀|² = 1`, which is exactly the `cos(γ/2)/sin(γ/2)` pattern above — so
the four real parameters suffice, matching `dim U(2) = 4`.

**Extraction recipe.** Given the matrix `U`:

1. `α = arg(det U)/2`; set `V = e^{−iα}U`, which has `det V = 1` (`V ∈ SU(2)`).
2. `γ = 2·atan2(|V₁₀|, |V₀₀|)` (so `γ ∈ [0, π]`).
3. `β + δ = −2·arg(V₀₀)` and `β − δ = 2·arg(V₁₀)`; solve the two-by-two system.
   (When `V₀₀ = 0` or `V₁₀ = 0` only the sum or difference is defined — one
   angle is gauge, fix `δ = 0`.)

**Worked example, `U = H`.** `det H = −1`, so `α = π/2`. Then `V = e^{−iπ/2}H`,
`|V₀₀| = |V₁₀| = 1/√2` → `γ = π/2`, and the phases give `β = 0`, `δ = π`:

```
H = e^{iπ/2} R_z(0) R_y(π/2) R_z(π) = i · R_y(π/2) R_z(π)
```

Verified numerically (max entrywise deviation `1.4e−16`). The same recipe on
`S = diag(1, i)` returns `(α, β, γ, δ) = (π/4, π/4, 0, π/4)` — i.e.
`S = e^{iπ/4}R_z(π/2)`, as expected for a diagonal gate — and on a Haar-random
`U ∈ U(2)` it reproduces the matrix to `1.7e−16`.

**Why this decomposition specifically.** Because `R_z` is diagonal and
`X R_z(θ) X = R_z(−θ)`, `X R_y(θ) X = R_y(−θ)`, one can always write
`U = e^{iα} A X B X C` with `ABC = I` (take `A = R_z(β)R_y(γ/2)`,
`B = R_y(−γ/2)R_z(−(δ+β)/2)`, `C = R_z((δ−β)/2)`). That is the standard route to
a controlled-`U` built from two CNOTs and three single-qubit gates (N&C Corollary
4.2), and it is why hardware basis sets expose `R_z` and one other rotation.

</details>

- Verify that {H, T} generates a dense subset of U(2)

<details><summary>Solution</summary>

Density means: for any `V ∈ SU(2)` and any `ε > 0`, some finite word in `H` and
`T` approximates `V` to within `ε` in operator norm (global phase ignored, so
work in `SU(2)`, i.e. in `U(2)/U(1) ≅ SO(3)`).

**Step 1 — two rotation axes.** Up to phase, `T = e^{iπ/8}R_z(π/4)` and
`HTH = e^{iπ/8}R_x(π/4)`. So the word `T·H·T·H` equals, up to global phase,

```
R_z(π/4) R_x(π/4)
```

**Step 2 — the composite is a rotation by an angle `θ` with**

```
cos(θ/2) = ½ Tr[R_z(π/4)R_x(π/4)] = cos²(π/8) = (2 + √2)/4 ≈ 0.8535533906
```

(Numerically confirmed: taking the `SU(2)` representative of `THTH` gives
`Tr/2 = 0.8535533906`, matching `cos²(π/8)` to ten digits.) So `THTH` is a
rotation of the Bloch sphere by `θ = 2 arccos((2+√2)/4) ≈ 1.09606` rad about the
axis `n̂ ∝ (cos(π/8), sin(π/8), cos(π/8))`.

**Step 3 — `θ` is an irrational multiple of `2π`.** If `θ/2` were a rational
multiple of `π`, say `θ/2 = 2πk/n`, then `2cos(θ/2) = ζ + ζ⁻¹` with `ζ` an `n`-th
root of unity, and `ζ + ζ⁻¹` is an **algebraic integer**. Here

```
2cos(θ/2) = (2 + √2)/2 = 1 + 1/√2
```

whose minimal polynomial over `ℚ` is `2x² − 4x + 1` (check: `x = 1 + 1/√2` ⇒
`(x−1)² = ½` ⇒ `2x² − 4x + 1 = 0`, verified numerically to `0.0`). That polynomial
is irreducible and not monic-with-integer-coefficients, so `1 + 1/√2` is *not* an
algebraic integer. Contradiction — hence `θ` is an irrational multiple of `2π`.

**Step 4 — irrational angle ⇒ dense on one axis.** The set `{kθ mod 2π}` is dense
in `[0, 2π)` (Weyl equidistribution / pigeonhole). Numerically, the first 2000
multiples leave a maximum gap of only `0.0069` rad. So powers of `THTH` approximate
`R_n̂(φ)` for *any* `φ`.

**Step 5 — a second, non-parallel axis.** Conjugating by `H` swaps the `x` and `z`
Bloch axes, so `H(THTH)H` is a rotation by the same `θ` about
`m̂ ∝ (cos(π/8), −sin(π/8), cos(π/8))`, which is not parallel to `n̂`. Every
`R ∈ SO(3)` factors as `R_n̂(φ₁)R_m̂(φ₂)R_n̂(φ₃)` (Euler angles about any two
non-parallel axes), so arbitrary rotations are approximable. Hence `⟨H, T⟩` is
dense in `SU(2)`, and with global phase in `U(2)` up to phase. ∎

**How fast?** Density alone says nothing about cost; the Solovay–Kitaev theorem
supplies `O(log^c(1/ε))` gates (`c ≈ 2` for the basic algorithm; modern
number-theoretic synthesis for `z`-rotations in Clifford+`T` achieves
`≈ 3log₂(1/ε)` `T` gates, which is optimal up to additive constants).

</details>

- Count T gates in a given circuit (T-count optimization)

<details><summary>Solution</summary>

**The circuit to count.** Take the standard ancilla-free Toffoli decomposition
(controls `a, b`, target `c`):

```
H c ; CX(b,c) ; T† c ; CX(a,c) ; T c ; CX(b,c) ; T† c ; CX(a,c) ;
T b ; T c ; H c ; CX(a,b) ; T a ; T† b ; CX(a,b)
```

Running this in Qiskit and comparing against `ccx` confirms
`Operator(qc).equiv(Operator(ccx)) = True`, with
`count_ops = {'cx': 6, 't': 4, 'tdg': 3, 'h': 2}`. So:

- **T-count = 7** (`t` and `t†` cost the same — both are non-Clifford and both
  consume one distilled magic state)
- CNOT-count = 6, T-depth = 3 if the gates are re-scheduled in parallel

Qiskit agrees: `transpile(ccx, basis_gates=['h','t','tdg','cx'],
optimization_level=3)` returns the same `{'cx': 6, 't': 4, 'tdg': 3, 'h': 2}`.
Seven is provably optimal for an *exact, ancilla-free* Clifford+T Toffoli
(Amy–Mosca, via a Reed–Muller code argument). Allowing an ancilla and a measured
Clifford correction brings it down to 4 (Jones, 2013).

**Why T-count and not gate count.** In a fault-tolerant surface-code machine
Clifford gates are (nearly) free — they are done by transversal operations, lattice
surgery or Pauli-frame bookkeeping — while every `T` needs a distilled magic
state, which dominates both qubit footprint and runtime. So the cost model is:
count `T`s, ignore Cliffords.

**Optimization example.** Consider

```
H(q0) ; CCX(q0,q1,q2) ; T(q1) ; CCX(q0,q1,q2) ; H(q0)
```

A naive decomposition gives `{'cx': 12, 't': 9, 'tdg': 6, 'h': 6}` — **T-count 15**
(7 + 7 + 1). But `T(q1)` is diagonal and `q1` is a *control* of both Toffolis, so
it commutes through: `CCX · T(q1) · CCX = T(q1) · CCX · CCX = T(q1)`. The circuit
is therefore exactly `H(q0) T(q1) H(q0)` — **T-count 1**. Qiskit confirms the
equivalence (`Operator(...).equiv(...) = True`), yet
`optimization_level=3` on the pre-decomposed circuit only reaches T-count 11: the
peephole optimizer cannot see the cancellation once the Toffolis are shredded into
`{h,t,cx}`.

**Lessons that generalise.** Optimise *before* decomposing; push diagonal gates
through controls; merge `T`s that land on the same qubit with no intervening
non-commuting gate (`T·T = S` is Clifford, so two `T`s can become zero); and for
serious work use a phase-polynomial / Reed–Muller based optimiser (Amy–Maslov–Mosca,
TODD, or ZX-calculus tools), which reason about the whole `{CNOT, T}` block at once
rather than locally.

</details>

---

## Module 3 — Quantum Complexity Theory

**Objective:** Understand where quantum computers provide advantage — and where they don't.

| Class | Definition | Key Results |
|---|---|---|
| BQP | Efficiently solvable on a quantum computer | Factoring ∈ BQP |
| QMA | Quantum analog of NP | Local Hamiltonian problem is QMA-complete |
| QCMA | Classical witness, quantum verifier | |
| BPP | Classical efficient with randomness | BPP ⊆ BQP (suspected strict) |
| P | Classical deterministic polynomial time | P ⊆ BPP ⊆ BQP |
| PSPACE | Classical polynomial space | BQP ⊆ PSPACE |

| Separation | Status |
|---|---|
| P ≠ NP | Unproven |
| BPP ≠ BQP | Strongly suspected, unproven |
| BQP ⊄ PH | Evidence via oracle separations (Raz-Tal) |

**Exercises:**
- Place factoring, graph isomorphism, and unstructured search in complexity classes

<details><summary>Solution</summary>

Be careful to state the *decision* version of each problem — complexity classes are
sets of languages.

**FACTORING** — decision form: "given `N` and `k`, does `N` have a nontrivial
factor `< k`?"

- In `NP`: a factor is a certificate, verified by one multiplication.
- In `coNP`: give the full prime factorisation plus AKS-style primality proofs for
  each prime (primality is in `P`); this certifies that *no* factor below `k`
  exists. So FACTORING `∈ NP ∩ coNP`.
- In `BQP` by Shor's algorithm (`Õ((log N)²)` quantum gates with fast arithmetic).
- Best classical: general number field sieve,
  `exp(c(log N)^{1/3}(log log N)^{2/3})` with `c = (64/9)^{1/3} ≈ 1.923` —
  subexponential but superpolynomial.
- **Not** believed `NP`-complete: an `NP`-complete problem in `coNP` would give
  `NP = coNP`, collapsing the polynomial hierarchy to its first level.

**GRAPH ISOMORPHISM** — "are `G₁` and `G₂` isomorphic?"

- In `NP` (the permutation is the certificate).
- In `coAM`, via the two-graph interactive proof for *non*-isomorphism; hence if GI
  were `NP`-complete, `PH` would collapse to `Σ₂` (Boppana–Håstad–Zachos). So GI is
  a canonical "`NP`-intermediate" candidate.
- Classically quasipolynomial: `exp((log n)^{O(1)})` (Babai, 2015–17).
- **No known quantum speedup.** The natural attack casts GI as a hidden subgroup
  problem over the *symmetric* group `Sₙ`, and no efficient non-abelian HSP
  algorithm is known there (strong Fourier sampling is provably insufficient for
  `Sₙ`). GI is in `BQP` only in the trivial sense that nobody can rule it out;
  quantum computers give no advantage over Babai's classical algorithm today.

**UNSTRUCTURED SEARCH** — two different framings, and conflating them is the
classic error:

- *Query (black-box) version*: find `x` with `f(x) = 1` given only oracle access.
  Classical randomised: `Θ(N)` queries. Quantum: `Θ(√N)` — Grover's upper bound
  and the BBBV lower bound match. This is a statement about **query complexity**,
  not a complexity class.
- *Explicit-circuit version*: given a circuit for `f` (e.g. SAT), the problem is
  `NP`-complete. Grover turns brute force `2ⁿ` into `2^{n/2}` — still exponential.
  Relative to a random oracle `A`, `NP^A ⊄ BQP^A` (BBBV), so no black-box method
  puts `NP` inside `BQP`.

**Summary map.** `P ⊆ BPP ⊆ BQP ⊆ PSPACE`; FACTORING sits in
`(NP ∩ coNP) ∩ BQP`, plausibly outside `BPP`; GI sits in `NP ∩ coAM`, plausibly
outside `P` but with no quantum advantage; SEARCH/SAT is `NP`-complete with only a
quadratic quantum speedup.

</details>

- Explain why Grover's algorithm doesn't imply BQP ⊃ NP

<details><summary>Solution</summary>

Three independent reasons, each sufficient.

**1. Quadratic ≠ exponential.** Grover finds a marked item among `N = 2ⁿ` in
`Θ(√N) = Θ(2^{n/2})` queries. For SAT on `n` variables that is `2^{n/2}` — still
exponential in `n`, so it is not a polynomial-time algorithm. `BQP ⊇ NP` would
require `poly(n)` time. (`√` of exponential is exponential; only an exponential
speedup of the *exponent* would help.)

**2. Grover is optimal, so "just improve it" is not available.** The BBBV lower
bound shows `Ω(√N)` queries are necessary for *any* quantum algorithm in the
black-box model. So the quadratic factor is the end of the road for unstructured
methods, not a first attempt.

**3. The oracle barrier.** BBBV (1997) exhibit an oracle `A` — in fact a random
oracle works with probability 1 — for which `NP^A ⊄ BQP^A`. Since Grover's
algorithm relativises (it works for *every* oracle), no argument of Grover's type
can prove `NP ⊆ BQP`. Any such proof must be **non-relativising**, i.e. must
exploit the internal structure of the circuit defining `f`, not merely query it.

**What Grover actually buys.** A generic square-root speedup for search-like
subroutines: SAT in `2^{n/2}`, collision finding, amplitude amplification inside
larger algorithms (e.g. quantum walks, Dürr–Høyer minimum finding). In practice
even that quadratic factor is eroded by fault-tolerance overhead — the standard
analysis (Babbush et al.) is that Grover only pays off for very large instances,
because each logical `T` gate is orders of magnitude slower than a classical
operation, whereas classical SAT solvers exploit structure that Grover ignores.

**The honest statement.** Quantum advantage for `NP`-complete problems, if it
exists, will come from *structure* (as it does for factoring via periodicity), not
from faster brute force.

</details>

- Describe the oracle separation between BQP and PH

<details><summary>Solution</summary>

**The result.** Raz and Tal (2018, building on Aaronson's 2010 Forrelation
problem) proved: there exists an oracle `A` with `BQP^A ⊄ PH^A`. Informally,
quantum computers can do something in the black-box world that *no* constant-round
classical scheme with unbounded-power nondeterministic/co-nondeterministic layers
can do.

**The problem — Forrelation.** Given oracle access to two Boolean functions
`f, g: {0,1}ⁿ → {±1}`, estimate

```
Φ(f, g) = 2^{−3n/2} Σ_{x,y} f(x) (−1)^{x·y} g(y)
```

i.e. the correlation between `g` and the Fourier transform of `f`. Decide whether
`Φ ≥ 3/5` or `|Φ| ≤ 1/100`.

**The quantum algorithm — one query each.** Prepare the uniform superposition with
`H^⊗n`, apply the phase oracle for `f`, apply `H^⊗n` (this *is* the Boolean Fourier
transform), apply the phase oracle for `g`, apply `H^⊗n`, and measure. The
amplitude on `|0ⁿ⟩` is exactly `Φ(f, g)`, so `O(1/ε²)` repetitions estimate it.
Two oracle queries total — quantum mechanics performs the Fourier transform for
free, which is the whole trick.

**The classical hardness — `PH` as `AC⁰`.** The standard translation
(Furst–Saxe–Sipser) says: a `PH` machine relative to an oracle corresponds to a
quasipolynomial-size, constant-depth circuit (`AC⁰`) over the oracle bits. Raz and
Tal define the *forrelation distribution* — pairs `(f, g)` built from correlated
Gaussians (`g` roughly the Fourier transform of `f`), rounded to `±1` — and prove
that this distribution is `1/polylog`-indistinguishable from the uniform
distribution by any `AC⁰` circuit of quasipolynomial size, while the quantum
algorithm distinguishes the two with constant advantage. Diagonalising over all
`PH` machines yields the oracle `A`.

**What it does and does not establish.**

- It does show quantum speedups can outrun the entire polynomial hierarchy *in the
  query model* — a far stronger statement than `BQP ⊄ NP` relative to an oracle.
- It does **not** prove `BQP ⊄ PH` in the real (unrelativised) world; oracle
  results are evidence and a barrier to relativising proof techniques, nothing more.
  Indeed there are oracles making `BQP` weak, and `BQP ⊆ PSPACE` unconditionally.
- Its practical descendant is random-circuit sampling: the same "quantum
  distributions are hard for shallow classical circuits" intuition underlies quantum
  supremacy/advantage experiments.

</details>

---

## Module 4 — Quantum Error Correction

**Objective:** Understand how quantum information can be protected from noise without violating the laws of quantum mechanics.

| Topic | Key Concepts |
|---|---|
| No-cloning theorem | Cannot copy unknown quantum states |
| 3-qubit bit-flip code | Encode `|ψ⟩` as `|ψψψ⟩`, detect and correct single bit flips |
| 3-qubit phase-flip code | Hadamard basis, detect and correct phase errors |
| Shor's 9-qubit code | First full QEC code; corrects any single-qubit error |
| Stabilizer formalism | Code defined by abelian subgroup of Pauli group |
| Syndrome measurement | Projective measurement that identifies error without revealing state |
| CSS codes | Calderbank-Shor-Steane: built from two classical codes |
| Distance d code | Corrects ⌊(d−1)/2⌋ errors; detects d−1 errors |

**Exercises:**
- Verify the 3-qubit code detects (but doesn't correct) two bit-flip errors

<details><summary>Solution</summary>

**Code.** `|0_L⟩ = |000⟩`, `|1_L⟩ = |111⟩`; stabilizers `S₁ = Z₁Z₂`, `S₂ = Z₂Z₃`.
The syndrome `(s₁, s₂)` records the two parities.

**Full syndrome table** (computed by XOR-ing the flip pattern; `s₁ = e₁⊕e₂`,
`s₂ = e₂⊕e₃`):

```
error      flips      (s₁, s₂)
none       000        (0, 0)
X₁         100        (1, 0)
X₂         010        (1, 1)
X₃         001        (0, 1)
X₁X₂       110        (0, 1)     ← same as X₃
X₁X₃       101        (1, 1)     ← same as X₂
X₂X₃       011        (1, 0)     ← same as X₁
```

**Detection.** Every weight-2 bit-flip error gives a *nonzero* syndrome, so the
error is always **detected** — you know something went wrong. This is the general
rule `detect up to d − 1 errors` with `d = 3`.

**Mis-correction.** The decoder sees `(0, 1)` and cannot tell `X₃` from `X₁X₂`;
it applies the minimum-weight fix `X₃`. The net operation on the encoded state is

```
X₃ · (X₁X₂) = X₁X₂X₃ = X̄
```

a **logical bit flip** — the decoder has actively turned a detected two-qubit error
into a logical error. Same for the other two rows. Hence `correct ⌊(d−1)/2⌋ = 1`
error, no more.

**Two caveats worth stating.**

1. The code is `[[3,1,3]]` only *against bit flips*. Against arbitrary Pauli noise
   its distance is 1: `Z₁` commutes with both stabilizers, so it is undetectable,
   and `Z₁` acts on the code space exactly as the logical `Z̄`. Protecting against
   both `X` and `Z` needs Shor's 9-qubit code (or Steane's 7-qubit code).
2. Because the code cannot correct two flips, the logical error probability is
   second order: with independent flip probability `p` per qubit,
   `p_L = 3p²(1−p) + p³ = 3p² − 2p³`. This beats the unencoded rate `p` exactly
   when `p < 1/2` — the simplest example of a threshold.

</details>

- Find stabilizer generators and logical operators for the 7-qubit Steane code

<details><summary>Solution</summary>

Steane's code is the CSS code built from the classical `[7,4,3]` Hamming code used
for both the `X` and the `Z` sector. Take the Hamming parity-check matrix whose
columns are the binary numbers 1…7:

```
H = [ 0 0 0 1 1 1 1 ]
    [ 0 1 1 0 0 1 1 ]
    [ 1 0 1 0 1 0 1 ]
```

**Six stabilizer generators** (qubits 1…7 left to right; a `1` in row `i` of `H`
becomes an `X` or a `Z`):

```
g₁ = I I I X X X X        g₄ = I I I Z Z Z Z
g₂ = I X X I I X X        g₅ = I Z Z I I Z Z
g₃ = X I X I X I X        g₆ = Z I Z I Z I Z
```

`6 = n − k = 7 − 1` generators, so the code encodes `k = 1` logical qubit.

**Checks (all verified with `qiskit.quantum_info.Pauli`).**

- All six generators pairwise commute: `True`. The only nontrivial cases are
  `X`-type vs `Z`-type, where the overlap is `|supp(rᵢ) ∩ supp(rⱼ)|`, always even
  because the rows of `H` overlap in an even number of positions (the Hamming code
  is *weakly self-dual*, `C^⊥ ⊆ C`) — that self-duality is exactly what makes the
  CSS construction work here.
- The projector `Π = Π_j (I + g_j)/2` has trace `2` — the code space is
  two-dimensional, as required.

**Logical operators.** `X̄ = X⊗7` and `Z̄ = Z⊗7` commute with every generator
(each row of `H` has even weight 4) and anticommute with each other (overlap 7,
odd) — both verified numerically. Multiplying by stabilizers gives cheaper
representatives: the weight-3 Hamming codewords have supports
`{1,2,3}, {1,4,5}, {1,6,7}, {2,4,6}, {2,5,7}, {3,4,7}, {3,5,6}`, so e.g.

```
X̄ ≃ X₁X₂X₃        Z̄ ≃ Z₁Z₂Z₃
```

are valid logical operators. The minimum weight over all such representatives is 3,
which is the code distance: `[[7,1,3]]`, correcting any single-qubit error.

**Codewords.** With `C_even` the 8 even-weight Hamming codewords (weights 0 and 4):

```
|0_L⟩ = (1/√8) Σ_{v ∈ C_even} |v⟩
|1_L⟩ = X̄|0_L⟩ = (1/√8) Σ_{v ∈ C_even} |v ⊕ 1111111⟩   (weights 3 and 7)
```

**Why this code is the fault-tolerance workhorse.** Every generator is purely `X`
or purely `Z` (CSS), so syndrome extraction splits into two independent classical
decoding problems; and because the two sectors use the *same* classical code, the
full Clifford group `{H, S, CNOT}` is transversal.

</details>

- Compute the code distance of the 5-qubit perfect code

<details><summary>Solution</summary>

**Code.** `[[5,1,3]]`, stabilizer generated by the four cyclic shifts

```
g₁ = X Z Z X I
g₂ = I X Z Z X
g₃ = X I X Z Z
g₄ = Z X I X Z
```

**Definition to use.** For a stabilizer code, `d = min{ wt(P) : P ∈ N(S) \ S }`:
the lightest Pauli that commutes with every stabilizer (so is undetectable) but is
not itself a stabilizer (so acts nontrivially on the code space).

**Brute-force computation** (all `4⁵ = 1024` Pauli strings, phases ignored):

- Stabilizer group `S`: `2⁴ = 16` elements ✓
- Normalizer `N(S)`: `64` elements ✓ (`= 2^{n+k} = 2⁶`, as it must be)
- Logical coset `N(S) \ S`: `48` elements; **minimum weight = 3**
- Undetectable errors of weight ≤ 2: **none** (empty list)

Examples of weight-3 logical operators: `IIXYX`, `IIYZY`, `IIZXZ`, `IXIYY`,
`IXXIZ`, `IXYXI`. So `d = 3`, and the code corrects any single-qubit error.

**Cross-check via Knill–Laflamme / syndromes.** There are `3n = 15` weight-1 Pauli
errors, and the enumeration shows they produce **15 distinct nonzero syndromes** —
together with the trivial syndrome that is `16 = 2⁴`, exactly the number of
available syndromes. The code is therefore **perfect**: it saturates the quantum
Hamming bound

```
2^{n−k} ≥ Σ_{j=0}^{t} 3^j C(n, j)   →   2⁴ = 16 ≥ 1 + 3·5 = 16 ✓
```

with equality at `n = 5, k = 1, t = 1`. No smaller code can correct an arbitrary
single-qubit error: `n = 5` is the minimum (the `[[4,1,2]]` code only detects).

**Contrast with Steane.** Both have `d = 3`, but the 5-qubit code is smaller and
non-CSS, which costs it transversality — Steane's CSS structure gives transversal
Cliffords, while the 5-qubit code's transversal gates are much more restricted.
Smaller is not always cheaper once fault tolerance is accounted for.

</details>

---

## Module 5 — Fault Tolerance

**Objective:** Understand how to perform reliable computation on imperfect hardware.

| Topic | Key Concepts |
|---|---|
| Fault tolerance threshold | Error rate below which error correction helps: ~10⁻³ |
| Transversal gates | Apply gate bitwise to each qubit in codeblock |
| Magic state distillation | Produce clean T-gate states from noisy ones |
| Concatenated codes | Recursively encode to suppress errors exponentially |
| Surface code | 2D local code, high threshold (~1%), leading practical candidate |
| Logical error rate | Error rate on encoded logical qubit |
| Overhead | Physical qubits per logical qubit (10²–10³ for surface code) |

**Exercises:**
- Show that a transversal CNOT on two [[7,1,3]] Steane blocks implements a logical CNOT

<details><summary>Solution</summary>

"Transversal CNOT" means: for each `i = 1…7`, apply a physical CNOT from qubit `i`
of block A (control) to qubit `i` of block B (target). Nothing couples different
positions within a block, so a single fault stays a single-qubit error in each
block — that is the fault-tolerance content.

**Basis-state argument.** Bitwise CNOT acts on computational basis states as
`|u⟩|v⟩ → |u⟩|u ⊕ v⟩`, where `u, v ∈ 𝔽₂⁷`. With `C_even` the 8 even-weight Hamming
codewords and `1 = 1111111`:

```
|0_L⟩ = 8^{−1/2} Σ_{u ∈ C_even} |u⟩ ,   |1_L⟩ = 8^{−1/2} Σ_{u ∈ C_even} |u ⊕ 1⟩
```

Take `|1_L⟩|1_L⟩`, the only nontrivial case:

```
CNOT^⊗7 · 8^{-1} Σ_{u,v ∈ C_even} |u⊕1⟩|v⊕1⟩
      = 8^{-1} Σ_{u,v} |u⊕1⟩|(u⊕1)⊕(v⊕1)⟩ = 8^{-1} Σ_{u,v} |u⊕1⟩|u⊕v⟩
```

`C_even` is a linear code, so for fixed `u` the map `v ↦ u ⊕ v` permutes `C_even`.
The target register is therefore an equal superposition over `C_even` — i.e.
`|0_L⟩` — and the state is `|1_L⟩|0_L⟩`. Verified exhaustively by enumerating all
`8 × 8 = 64` basis terms for each of the four inputs:

```
|0_L⟩|0_L⟩ → |0_L⟩|0_L⟩    ✓ (64 terms, bijective)
|0_L⟩|1_L⟩ → |0_L⟩|1_L⟩    ✓
|1_L⟩|0_L⟩ → |1_L⟩|1_L⟩    ✓
|1_L⟩|1_L⟩ → |1_L⟩|0_L⟩    ✓
```

Each map is a bijection on the 64 basis pairs, so amplitudes (all `1/8`) are
preserved — the action is exactly `|a_L⟩|b_L⟩ → |a_L⟩|(a⊕b)_L⟩`, the logical CNOT,
with no extra phases. By linearity this extends to arbitrary superpositions.

**Stabilizer argument (the slick version).** Conjugation by `CNOT^⊗7` maps

```
X_A ⊗ I → X_A ⊗ X_B ,  I ⊗ X_B → I ⊗ X_B ,
Z_A ⊗ I → Z_A ⊗ I ,    I ⊗ Z_B → Z_A ⊗ Z_B
```

position by position. An `X`-type Steane generator `g` on block A becomes `g ⊗ g`,
and a `Z`-type generator on block B becomes `g ⊗ g` — both products of generators
of the *joint* stabilizer group, because **both blocks use the same code with the
same generators**. So the stabilizer group is preserved (the code space is mapped
to itself, no leakage), and on logical operators the same rule reads
`X̄_A → X̄_A X̄_B`, `Z̄_B → Z̄_A Z̄_B` — precisely the Heisenberg-picture action of
CNOT. ∎

**Scope.** The same argument transversalises the whole Clifford group `{H, S, CNOT}`
for Steane's code (it is a self-dual CSS code). It does *not* extend to `T` — see
the Eastin–Knill exercise below.

</details>

- Estimate the physical qubit overhead for a fault-tolerant T gate via magic state distillation

<details><summary>Solution</summary>

An order-of-magnitude estimate with every assumption stated — that is all anyone
can honestly give, since the answer moves with the hardware error rate.

**Assumptions.**

- Physical error rate `p = 10⁻³`; surface-code threshold `p_th ≈ 10⁻²`.
- Logical error per code cell: `p_L(d) ≈ 0.1 (p/p_th)^{(d+1)/2}`.
- A distance-`d` surface-code patch costs `≈ 2d²` physical qubits (data + measure).
- Raw injected `|T⟩` states carry error `≈ p = 10⁻³` (injection fidelity is set by
  the physical error rate).
- Bravyi–Kitaev 15-to-1 distillation: `p_out = 35 p_in³`, consuming 15 inputs.
- Target: logical `T` infidelity `≈ 10⁻¹⁰` (enough for an algorithm with `~10⁹`
  `T` gates).

**Distillation rounds** (computed):

```
p_in = 10⁻³  →  level 1: 35(10⁻³)³ = 3.5×10⁻⁸   (15 raw states)
             →  level 2: 35(3.5×10⁻⁸)³ = 1.5×10⁻²¹ (225 raw states)
```

One round misses the `10⁻¹⁰` target; two rounds overshoot it hugely. So **two
levels, 225 raw `|T⟩` states per output** — or, in practice, one round of 15-to-1
plus a cheaper second-stage protocol.

**Code distance needed.** The distillation circuit is Clifford, but it must not
fail more often than its output error: a level-2 unit with `~10³` logical
operations needs `p_L ≲ 10⁻¹³`. From the formula:

```
d = 15 → p_L ≈ 1×10⁻⁹     (450 physical qubits/patch)
d = 19 → p_L ≈ 1×10⁻¹¹    (722)
d = 23 → p_L ≈ 1×10⁻¹³    (1058)
```

So `d ≈ 23` for the top level, `d ≈ 15` for the first level (its output is only
`3.5×10⁻⁸`, so it does not need more).

**Footprint.**

- One level-2 unit: ~15 logical qubits + ancillas ≈ 20 patches × 1058 ≈ `2×10⁴`
  physical qubits.
- Feeding it: 15 level-1 units at ≈ 20 × 450 ≈ `10⁴` each, but time-multiplexed —
  keep 2–4 running in parallel, `2–4×10⁴`.
- **Total: `10⁴–10⁵` physical qubits per T factory**, versus `≈ 2d² ≈ 10³` for a
  single logical data qubit — so one factory costs 10–100 logical qubits' worth of
  hardware, on top of the `10²–10³` physical-per-logical overhead quoted in the
  module table. That compounding is why a few hundred logical qubits becomes
  millions of physical ones.

**Sanity check against the literature.** Optimised factory designs
(Fowler–Gidney; Litinski's "Magic State Distillation: Not as Costly as You Think")
land at the low end, `~10⁴` physical qubits and tens of microseconds per output
`T` state, by tailoring distance per level and using lattice surgery. The estimate
above is the right order of magnitude.

**The strategic point.** `T` states — not Cliffords, not memory — dominate the cost
of fault-tolerant computation. That is why algorithm papers now report **T-count**
and **T-depth** as their headline resource numbers, and why T-count optimisation
(Module 2) is worth real effort.

</details>

- Describe why Clifford gates cannot be universal fault-tolerantly via transversals alone

<details><summary>Solution</summary>

Two separate facts, often conflated. The first says Cliffords are not enough; the
second says you cannot fix that by finding a cleverer code.

**1. Cliffords alone are classically simulable (Gottesman–Knill).** A circuit of
stabilizer-state preparations, Clifford gates and computational-basis measurements
can be simulated in polynomial time on a classical computer, by tracking the
`O(n²)`-bit stabilizer tableau instead of `2ⁿ` amplitudes. So a transversal-Clifford
machine is not a quantum computer in any useful sense — no speedup is possible.
Universality requires at least one non-Clifford gate, canonically `T`.

**2. Eastin–Knill theorem (2009): no code has a universal transversal gate set.**
For any quantum error-*detecting* code (one that detects arbitrary single-qubit
errors), the group of logical gates implementable transversally is **finite**.

*Sketch of why.* Transversal gates form a group `G`; because errors on a single
qubit are correctable, one can show `G` is a compact Lie group all of whose
elements are connected to the identity only through gates that act trivially on
the code space — so the logical image of `G` is a discrete (hence, by compactness,
finite) subgroup of the logical unitary group. A universal gate set generates an
infinite (dense) subgroup of `SU(2^k)`. Finite ≠ dense, so transversal gates can
never be universal. ∎

**3. The topological strengthening (Bravyi–König, 2013).** For topological
stabilizer codes in `D` spatial dimensions, *any* logical gate implemented by a
constant-depth local circuit lies in the `D`-th level of the Clifford hierarchy. In
2D — the surface code — that means level 2: Cliffords, and nothing more. The `T`
gate lives at level 3, so it is provably unreachable by local constant-depth means
in 2D.

**Why "transversal" is the property being given up.** Transversality is what makes
a gate fault tolerant for free: applying gates qubit-by-qubit within a block means
a single physical fault produces a single-qubit error per block, which the code can
still correct. Any non-transversal implementation must be *made* fault tolerant by
other machinery.

**The workarounds actually used.**

- **Magic state injection + distillation**: do `T` by consuming a distilled
  `|T⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2` state with a Clifford gadget (the previous
  exercise's cost model). This is the standard surface-code route.
- **Code switching / gauge fixing**: move between two codes with complementary
  transversal sets (e.g. Steane's `[[7,1,3]]` with transversal Cliffords and the
  15-qubit Reed–Muller code with transversal `T`), as in 3D gauge colour codes.
- **Pieceable fault tolerance**: split a non-transversal gate into rounds with
  intermediate error correction.
- **Lattice surgery + Pauli-frame tracking**: make the Clifford part almost free so
  that the entire budget can be spent on `T`.

</details>

---

## Module 6 — Key Quantum Algorithms Overview

**Objective:** Survey the major quantum algorithms and understand their speedup origins.

| Algorithm | Problem | Speedup | Mechanism |
|---|---|---|---|
| Deutsch-Jozsa | Constant vs balanced function | Exponential (exact) | Phase kickback, interference |
| Bernstein-Vazirani | Find hidden string | n classical queries → 1 quantum query (exact) | Phase kickback + Hadamard (Fourier) sampling |
| Simon's algorithm | Find period in GF(2) | Exponential | Quantum Fourier sampling |
| Shor's algorithm | Integer factoring | Exponential | QFT + hidden subgroup |
| Grover's algorithm | Unstructured search | Quadratic; k* ≈ (π/4)√(N/M) iterations for M marked items | Amplitude amplification |
| HHL algorithm | Linear systems | Exponential* | QPE + conditional rotation |
| VQE | Ground state energy | Heuristic | Variational hybrid |
| QAOA | Combinatorial optimization | Heuristic | Variational hybrid |
| Quantum simulation | Simulate Hamiltonians | Exponential | Trotterization / LCU |

*Exponential subject to classical input/output bottleneck caveats.

**Exercises:**
- Trace through a 2-qubit Deutsch-Jozsa circuit step by step

<details><summary>Solution</summary>

Two qubits means `n = 1` query qubit plus one ancilla — Deutsch's original problem:
decide whether `f: {0,1} → {0,1}` is constant or balanced with **one** query.

**Circuit.** `q₀` (query) starts in `|0⟩`, `q₁` (ancilla) in `|1⟩`; apply
`H ⊗ H`, then `U_f: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩`, then `H` on `q₀`, then measure `q₀`.

**Step-by-step.**

```
|ψ₀⟩ = |0⟩|1⟩
|ψ₁⟩ = (H⊗H)|ψ₀⟩ = |+⟩|−⟩ = ½(|0⟩+|1⟩)(|0⟩−|1⟩)
```

Phase kickback: because `|−⟩` is an eigenvector of `X` with eigenvalue `−1`,

```
U_f |x⟩|−⟩ = |x⟩ · (|f(x)⟩ − |1⊕f(x)⟩)/√2 = (−1)^{f(x)} |x⟩|−⟩
```

so the oracle writes its answer into a *phase* on the query register:

```
|ψ₂⟩ = [ (−1)^{f(0)}|0⟩ + (−1)^{f(1)}|1⟩ ]/√2 ⊗ |−⟩
     = (−1)^{f(0)} [ |0⟩ + (−1)^{f(0)⊕f(1)}|1⟩ ]/√2 ⊗ |−⟩
```

The global factor `(−1)^{f(0)}` is unobservable; the *relative* phase is
`f(0) ⊕ f(1)` — exactly the bit that distinguishes constant from balanced.
Finally `H|+⟩ = |0⟩`, `H|−⟩ = |1⟩`:

```
f constant (f(0)⊕f(1) = 0) → |ψ₃⟩ = ±|0⟩|−⟩ → measure 0 with probability 1
f balanced (f(0)⊕f(1) = 1) → |ψ₃⟩ = ±|1⟩|−⟩ → measure 1 with probability 1
```

**Simulated (Qiskit `Statevector`, all four oracles):**

```
f = 0 (constant) : P(q₀=0) = 1.000, P(q₀=1) = 0.000
f = 1 (constant) : P(q₀=0) = 1.000, P(q₀=1) = 0.000
f = x (balanced) : P(q₀=0) = 0.000, P(q₀=1) = 1.000
f = ¬x (balanced): P(q₀=0) = 0.000, P(q₀=1) = 1.000
```

(The oracles used were: identity; `X` on `q₁`; `CX(q₀,q₁)`; `CX(q₀,q₁)` then `X`.)

**Where the advantage comes from.** Not from "trying both inputs at once" — the
superposition alone tells you nothing, since measuring it gives a random `x`. The
advantage comes from (i) phase kickback turning function values into phases, and
(ii) the final Hadamard **interfering** those phases so that the answer bit
`f(0)⊕f(1)` appears deterministically while the individual values `f(0)`, `f(1)`
remain inaccessible. Classically one query gives one value and cannot decide the
question; here one query gives a global property and nothing else. The `n`-qubit
Deutsch–Jozsa is the same argument with `H^⊗n`, separating `1` quantum query from
`2^{n−1}+1` classical deterministic queries — though only `O(1)` randomised
classical queries suffice for bounded error, which is why the speedup is
"exponential" only in the exact, deterministic setting.

</details>

- Explain why Grover's O(√N) speedup is optimal

<details><summary>Solution</summary>

Optimality is a **query lower bound**: any quantum algorithm that finds a marked
item among `N` using oracle calls needs `Ω(√N)` of them (BBBV, 1997 — "Strengths
and weaknesses of quantum computing").

**The hybrid argument.** Let `|ψ^k⟩` be the state after `k` steps of the algorithm
run with the *empty* oracle (nothing marked), and `|ψ_y^k⟩` the state after the same
`k` steps with the oracle that marks only `y`. Define the total deviation

```
D_k = Σ_{y=1}^{N} ‖ |ψ_y^k⟩ − |ψ^k⟩ ‖²
```

Each query changes the state only where the query register has support on `y`:
`‖ O_y|φ⟩ − |φ⟩ ‖ = 2|⟨y|φ⟩|`. Feeding this into the triangle inequality and using
both `Σ_y |⟨y|ψ^k⟩|² = 1` and `Σ_y |⟨y|ψ^k⟩| ≤ √N` (Cauchy–Schwarz) gives the
recursion `D_{k+1} ≤ D_k + 4√(D_k) + 4`, whose solution is

```
D_k ≤ 4k²
```

Numerically confirmed on a random 6-query algorithm with `N = 16`: `D_k` came out
`4.0, 8.2, 11.1, 14.1, 15.9, 18.4` against the bound `4, 16, 36, 64, 100, 144` —
satisfied with room to spare, as an upper bound should be.

**Turning it into a lower bound.** If the algorithm identifies the marked `y`
correctly with probability ≥ `2/3` for *every* `y`, the states `|ψ_y^k⟩` must be
pairwise nearly distinguishable, which forces them to be far from the common
oracle-free state for most `y`: `D_k = Ω(N)`. Combined with `D_k ≤ 4k²`:

```
4k² ≥ cN   ⇒   k ≥ (√c/2)·√N = Ω(√N)
```

Grover matches this with `k* = ⌊(π/4)√N⌋` iterations (for one marked item), so the
bound is **tight up to the constant**. Simulation: `N = 1024` peaks at `k = 25`
(`(π/4)√1024 = 25.13`) with success probability `0.9995`; `N = 256` peaks at
`k = 12` (`12.57`) with `0.9999`.

**Geometric reason for the `√`.** Grover is a rotation in the 2D plane spanned by
the marked state `|w⟩` and its orthogonal complement. Each iteration rotates by
`2θ` with `sin θ = 1/√N`, so `θ ≈ 1/√N`; reaching `π/2` takes
`≈ (π/2)/(2/√N) = (π/4)√N` steps. The amplitude on the target grows *linearly* in
the number of iterations, so the *probability* grows quadratically — "amplitude
amplification" is exactly the statement that you get a square-root, and no more.

**Consequences.** Over-rotating hurts: at `k ≈ (π/2)√N` the success probability
returns to nearly zero, so the iteration count must be chosen (or fixed-point
amplitude amplification used). And since the bound is on *queries*, the only way to
beat `√N` is to stop treating `f` as a black box and exploit its structure.

</details>

- Describe the quantum speedup conditions for HHL (sparse, well-conditioned matrix)

<details><summary>Solution</summary>

HHL (Harrow–Hassidim–Lloyd, 2009) solves `Ax = b` in the sense of producing a
quantum state `|x⟩ ∝ A⁻¹|b⟩`. Its runtime is

```
O( κ² s² log(N) / ε )      (original)
O( κ s polylog(N/ε) )      (Childs–Kothari–Somma, with LCU/QSP and
                            Ambainis' variable-time amplitude amplification)
```

against `O(Ns)` for classical conjugate gradient on a sparse system — an
*exponential* advantage in `N`, but only if every one of the following holds.

**The four conditions.**

1. **Sparsity / efficient access.** `A` must be `s`-sparse (`s = polylog N` nonzeros
   per row) with an oracle giving the positions and values of the nonzeros in a row
   in `O(polylog N)` time. This is what makes `e^{−iAt}` implementable efficiently
   by Hamiltonian simulation. (`A` non-Hermitian is handled by the standard
   dilation `[[0, A],[A†, 0]]`.)
2. **Well-conditioned.** The condition number `κ = |λ_max|/|λ_min|` must be
   `polylog(N)`, or at worst small polynomial. Runtime is at best linear in `κ`, and
   the conditional rotation `|λ⟩|0⟩ → |λ⟩(√(1−C²/λ²)|0⟩ + (C/λ)|1⟩)` succeeds with
   probability `Ω(1/κ²)` (`Ω(1/κ)` with amplitude amplification), so an ill-conditioned
   system destroys the speedup. Preconditioning must preserve sparsity to help.
3. **Efficient state preparation.** You must be able to build `|b⟩` in
   `O(polylog N)` — e.g. from an analytic formula or QRAM. If preparing `|b⟩` costs
   `O(N)`, the speedup is gone before the algorithm starts.
4. **The output must be a "quantum" answer.** HHL yields the *state* `|x⟩`, not the
   `N` amplitudes. Reading all of `x` costs `Ω(N)` measurements. The algorithm is
   only useful when the answer wanted is an expectation value `⟨x|M|x⟩` — a weighted
   sum, a moment, a normalised overlap, whether `x` lies mostly in some subspace.

**Mechanism, briefly.** Expand `|b⟩ = Σ_j β_j|u_j⟩` in the eigenbasis of `A`; use
quantum phase estimation with `e^{−iAt}` to write eigenvalues into an ancilla
register, `Σ_j β_j|u_j⟩|λ̃_j⟩`; apply the `1/λ` conditional rotation; uncompute the
eigenvalue register; post-select on the ancilla being `|1⟩` to obtain
`∝ Σ_j (β_j/λ_j)|u_j⟩ = |A⁻¹b⟩`.

**The fine print (Aaronson, "Read the fine print", 2015).** All four conditions must
hold *simultaneously*; each is a potential `O(N)` trapdoor. Furthermore, the
dequantisation results (Tang and successors) show that for **low-rank** systems with
comparable sampling access, classical algorithms match HHL up to polynomial
factors — so genuine exponential advantage requires high-rank, sparse,
well-conditioned `A` with a real quantum input and a real quantum output. HHL is
best understood as a *subroutine template* (behind quantum recommendation systems,
differential-equation solvers, some QML proposals) rather than a drop-in linear
solver.

</details>

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Quantum Computation and Quantum Information* — Nielsen & Chuang | Textbook | The definitive reference |
| Preskill's lecture notes — Caltech | Notes | Free, excellent on QEC |
| *An Introduction to Quantum Computing* — Kaye, Laflamme, Mosca | Textbook | More accessible than N&C |
| Aaronson's *Quantum Computing Since Democritus* | Book | Complexity theory focus |
| IBM Qiskit Textbook | Online | Hands-on, free |

---

## Progression Checkpoints

- [ ] Implement all standard gates and verify their matrix representations
- [ ] Decompose multi-qubit unitaries into CNOT + single-qubit gates
- [ ] Explain BQP and what quantum speedup means rigorously
- [ ] Encode a logical qubit using stabilizer code formalism
- [ ] Trace through Shor's and Grover's algorithms circuit by circuit
- [ ] Describe the surface code and why it's the leading fault-tolerance candidate
