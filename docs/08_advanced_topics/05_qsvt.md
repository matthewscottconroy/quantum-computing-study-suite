# Quantum Singular Value Transformation

> **Prerequisites**: Linear algebra and SVD (Chapter 1), Grover/amplitude amplification (04/05),
> QPE and Hamiltonian simulation (04/04, 08/03), HHL linear systems (04/07)
> **Connects to**: Qubitization costs (08/03), modern linear-systems solvers (04/07), ground-state
> preparation, quantum chemistry compilation

---

## Overview

Most quantum algorithms of the textbook era — Grover search, phase estimation, Hamiltonian
simulation, HHL — were discovered separately, each with its own bespoke analysis. The **quantum
singular value transformation** (QSVT, Gilyén-Su-Low-Wiebe 2019) reveals them as one algorithm.
The template: embed a matrix `A` inside a unitary (a *block encoding*), then interleave that
unitary with simple single-parameter phase rotations. The resulting circuit applies a
*polynomial* `P` to the singular values of `A` — and the choice of polynomial is the choice of
algorithm. A sign function gives Grover; a truncated `e^{ixt}` gives optimal Hamiltonian
simulation; an approximation of `1/x` gives the modern linear-systems solver that supersedes
HHL. Martyn, Rossi, Tan, and Chuang (2021) call this the "grand unification" of quantum
algorithms, and QSVT is now the standard compilation target for fault-tolerant algorithm design.

The mathematical engine is small: a single-qubit identity called **quantum signal processing**
(QSP) characterizes exactly which polynomials a sequence of alternating rotations can produce,
and qubitization lifts it to arbitrary matrices. This chapter builds the story bottom-up: block
encodings, the QSP theorem (with a fully verified degree-2 example), the lifting to QSVT, and
the polynomial constructions behind each name-brand algorithm.

---

## Block Encodings

### Definition

A matrix `A` (say `N × N`, with `||A|| ≤ 1`) generally is not unitary, so it cannot be a quantum
gate. A **block encoding** hides it in the corner of a larger unitary: `U` acting on `a` ancilla
qubits plus the system is an `(α, a, ε)`-block-encoding of `A` if

```
|| A - α (⟨0|^{⊗a} ⊗ I) U (|0⟩^{⊗a} ⊗ I) || ≤ ε
```

i.e., up to normalization `α` and error `ε`, the top-left block of `U` *is* `A`:

```
U = [ A/α   ·  ]
    [  ·    ·  ]
```

Operationally: prepare ancillas in `|0⟩`, apply `U`, and postselect the ancillas on `|0⟩`; the
system then experienced `A/α`. The normalization `α ≥ ||A||` is a resource — every factor of
`α` you concede is paid back in circuit repetitions or polynomial degree.

### Access Models

Block encodings are the universal input format; the main ways to build one:

- **Linear combination of unitaries (LCU)**: for `H = Σⱼ cⱼ Pⱼ` (Pauli decomposition),
  `PREPARE` loads amplitudes `√(cⱼ/λ)` on the ancillas and `SELECT = Σⱼ |j⟩⟨j| ⊗ Pⱼ` applies
  the terms; together they block-encode `H/λ` with `λ = Σⱼ|cⱼ| = ||H||₁` — the same `λ` that
  sets the qubitization cost in Chapter 08/03.
- **Sparse-access oracles**: an `s`-sparse matrix with entry oracles gives an `(s, ·, ·)`-block
  encoding.
- **Density matrices, POVMs, Gram matrices** — each standard input model has a block-encoding
  recipe, which is why QSVT statements are model-independent.

### Qubitization Recap

A block encoding can be applied once, but powers `(A/α)^m` obtained by naive repetition-with-
postselection decay exponentially. **Qubitization** (Low-Chuang 2019) fixes this: from `U` one
builds a *walk operator* `W` whose action, in each invariant 2D subspace labeled by a singular
value `σ` of `A/α`, is a rotation by angle `arccos(σ)` — exactly the single-qubit signal
operator below, with `x = σ`. All the analysis of QSVT therefore reduces to one qubit. The
cost accounting is as in Chapter 08/03: each use of `W` costs one call to `U` or `U†`.

---

## Quantum Signal Processing: The Single-Qubit Engine

### Signal and Processing Operators

Fix a *signal parameter* `x ∈ [-1, 1]`, encoded in the X-rotation-like **signal operator**

```
W(x) = [    x         i√(1-x²) ]
       [ i√(1-x²)        x     ]
```

(`W(x) = e^{i arccos(x) X}` — one column of a walk operator). Interleave `d` copies of `W(x)`
with Z-phase **processing operators**, giving the QSP sequence with phases
`φ = (φ₀, φ₁, ..., φ_d)`:

```
U_φ(x) = e^{iφ₀Z} · W(x) e^{iφ₁Z} · W(x) e^{iφ₂Z} · ... · W(x) e^{iφ_dZ}
```

### The QSP Theorem

The sequence `U_φ(x)` always has the form

```
U_φ(x) = [ P(x)            iQ(x)√(1-x²)  ]
         [ iQ*(x)√(1-x²)   P*(x)         ]
```

and the achievable `(P, Q)` are *exactly characterized*: for every `d ≥ 0` there exist phases
`φ ∈ ℝ^{d+1}` realizing polynomials `P, Q` if and only if

1. `deg P ≤ d`, `deg Q ≤ d - 1`;
2. `P` has parity `d mod 2`, `Q` has parity `(d-1) mod 2`;
3. `|P(x)|² + (1-x²)|Q(x)|² = 1` for all `x ∈ [-1, 1]` (hence `|P(x)| ≤ 1`).

In trigonometric form (`x = cos θ`): `⟨0|U_φ(cos θ)|0⟩` ranges over exactly the degree-`d`
trigonometric polynomials in `θ` obeying the parity and normalization constraints — QSP is a
quantum realization of Chebyshev/Fourier approximation theory. Given a target polynomial, the
phases `φ` are computed *classically* in `poly(d)` time by stable root-finding/optimization;
the quantum circuit just plays them back. Any real target with `|P| ≤ 1` and definite parity
can be embedded (as `Re P`) with at most a doubling of the bookkeeping.

The trivial phase choice is already interesting: `φ = (0, 0, ..., 0)` gives `U = W(x)^d`, and
since `W(x) = e^{iθX}` with `x = cos θ`, the top-left entry is `cos(dθ) = T_d(x)` — the
**Chebyshev polynomials are QSP's natural response**, and all other polynomials are phased
deformations of them.

---

## From One Qubit to Matrices: The QSVT Theorem

### Projector-Controlled Phase Rotations

Let `U` block-encode `A/α` with singular value decomposition `A/α = Σᵢ σᵢ |wᵢ⟩⟨vᵢ|`. Let `Π`
be the projector onto the ancilla-`|0⟩` subspace. The matrix analogue of `e^{iφZ}` is the
**projector-controlled phase rotation**

```
Π_φ = e^{iφ(2Π - I)}
```

implemented with one ancilla-controlled NOT pair around a single `e^{iφZ}` — cost `O(a)` gates,
independent of `N`.

### The Theorem

For a polynomial `P` of degree `d` satisfying the QSP conditions (parity `d mod 2`,
`|P(x)| ≤ 1` on `[-1,1]`), the alternating sequence

```
U_Φ = Π_{φ₀} U Π_{φ₁} U† Π_{φ₂} U Π_{φ₃} U† ...    (d applications of U/U† total)
```

is a block encoding of `P^{(SV)}(A/α)`, the polynomial applied to the **singular values**:

```
P^{(SV)}(A/α) = Σᵢ P(σᵢ) |wᵢ⟩⟨vᵢ|      (odd P; even P maps to Σᵢ P(σᵢ)|vᵢ⟩⟨vᵢ|)
```

The proof is qubitization: `U` and `Π` decompose the Hilbert space into 2D subspaces, one per
singular value, and inside each the sequence is literally the single-qubit QSP circuit with
`x = σᵢ`. For Hermitian `A`, singular values are `|eigenvalues|`, and odd/even polynomials of
eigenvalues are recovered — so "eigenvalue transformation" is the Hermitian special case.

**Cost**: `d` queries to `U`/`U†`, `d + 1` phase rotations, and `O(1)` extra ancillas. The
entire design problem becomes classical approximation theory: *find the lowest-degree
polynomial with your desired shape.*

---

## The Grand Unification

### Amplitude Amplification and Grover

Preparing `|ψ⟩` with `⟨good|ψ⟩ = a` is a singular-value problem: the `1 × 1` "matrix"
`Π_good |ψ⟩⟨ψ| Π_ψ` has singular value `a`. Applying a polynomial with `P(a') ≈ 1` for all
`a' ≥ a_min` — an approximation of the **sign/step function** — amplifies the amplitude to
constant in `d = O(1/a_min)` iterations: Grover's `O(√N)` with `a_min = 1/√N`. Chebyshev
phases recover textbook Grover exactly (each Grover iteration — two reflections — is one `W`
step); sign-function phases give **fixed-point** amplitude amplification that does not
overshoot when `a` is unknown, a refinement invisible in the original framework (cf. 04/05).

### Hamiltonian Simulation

To implement `e^{-iHt}` from a block encoding of `H/λ`: approximate `cos(λt·x)` and
`sin(λt·x)` on `[-1,1]` by their **Jacobi-Anger expansions**,

```
cos(tx) = J₀(t) + 2 Σ_{k≥1} (-1)^k J_{2k}(t) T_{2k}(x)
sin(tx) = 2 Σ_{k≥0} (-1)^k J_{2k+1}(t) T_{2k+1}(x)
```

Bessel coefficients `J_k(t)` decay superexponentially once `k > |t|`, so truncating at degree

```
d = O( λt + log(1/ε) )
```

suffices — matching the qubitization query cost quoted in Chapter 08/03 exactly, and provably
optimal in both `t` and `ε`. (Numerically: `t = 5` needs degree 15 and `t = 10` needs degree
22 for `ε = 10⁻⁶` — the additive `log(1/ε)` behavior is visible already at small `t`.)
Contrast Trotterization's `poly(1/ε)` step counts (08/03).

### Linear Systems: Beyond HHL

To solve `Ax = b`, apply `P(x) ≈ 1/x` to the singular values. On the domain `[1/κ, 1]`
(eigenvalues rescaled as in HHL, Chapter 04/07), an odd polynomial approximating
`(1/2κ)·(1/x)` to error `ε` exists with degree

```
d = O( κ log(κ/ε) )
```

giving a linear-systems solver with overall complexity `O(κ log(1/ε))` (variable-time
amplification folds in the `O(κ)` postselection rounds) — the modern replacement for HHL's
`O(κ²/ε)`: exponentially better in precision, quadratically better in condition number. This
is the QSVT formulation of the Childs-Kothari-Somma Chebyshev/LCU approach flagged among
Chapter 04/07's refinements. All of HHL's "fine print" (state preparation, sparsity, output
access) still applies — QSVT fixes the algorithmic overhead, not the input/output model.

### Eigenvalue Filtering and Ground-State Preparation

A shifted sign function `P(x) ≈ sign(x - μ)` filters spectral weight: applied to a block-
encoded Hamiltonian it projects a trial state onto eigenvalues below threshold `μ`. With
spectral gap `Δ` and trial overlap `γ`, ground-state projection costs degree
`O((1/Δ) log(1/(γε)))` plus `O(1/γ)` amplification rounds (Lin-Tong 2020) — the fault-tolerant
successor to VQE-style heuristics; the same filter idea underlies QSVT-based eigenvalue
thresholding, Gibbs sampling, and phase-estimation variants.

---

## Key Formulas

- **Block encoding**: `A = α (⟨0|^{⊗a} ⊗ I) U (|0⟩^{⊗a} ⊗ I)`, `α ≥ ||A||`; LCU gives `α = λ = Σ|cⱼ|`
- **QSP sequence**: `U_φ(x) = e^{iφ₀Z} Π_{j=1}^{d} [W(x) e^{iφⱼZ}]`, `W(x) = e^{i arccos(x) X}`
- **QSP theorem**: `⟨0|U_φ|0⟩ = P(x)` iff `deg P ≤ d`, parity `d mod 2`, `|P|² + (1-x²)|Q|² = 1`
- **Chebyshev response**: all-zero phases give `⟨0|W(x)^d|0⟩ = T_d(x) = cos(d arccos x)`
- **QSVT**: `d` alternating `U/U†` with `e^{iφⱼ(2Π-I)}` block-encode `Σᵢ P(σᵢ)|wᵢ⟩⟨vᵢ|`
- **Hamiltonian simulation**: Jacobi-Anger truncation, `d = O(λt + log(1/ε))` (agrees with 08/03)
- **Linear systems**: `P(x) ≈ 1/x` on `[1/κ, 1]`, degree `O(κ log(κ/ε))` → `O(κ log(1/ε))` solver (cf. 04/07)
- **Amplitude amplification**: sign-function QSVT, `d = O(1/a_min)`

---

## Worked Example: A Degree-2 QSP Sequence Implementing T₂(x)

**Claim.** The three-phase sequence `φ = (0, 0, 0)` — i.e. `U = W(x)·W(x)` — implements the
degree-2 Chebyshev polynomial `T₂(x) = 2x² - 1` as its `⟨0|·|0⟩` matrix element.

**Symbolic product.** Write `s = √(1-x²)`. Then:

```
W(x)² = [  x    is ] [  x    is ]  =  [ x² + (is)(is)     x(is) + (is)x  ]
        [  is    x ] [  is    x ]     [ (is)x + x(is)     (is)(is) + x²  ]

      = [ x² - (1-x²)      2ixs        ]   =   [ 2x² - 1        2ix√(1-x²) ]
        [    2ixs        x² - (1-x²)   ]       [ 2ix√(1-x²)     2x² - 1    ]
```

So `⟨0|U|0⟩ = 2x² - 1 = T₂(x)` identically, with `Q(x) = 2x` supplying the unitarity balance:
`|T₂(x)|² + (1-x²)(2x)² = (2x²-1)² + 4x²(1-x²) = 4x⁴ - 4x² + 1 + 4x² - 4x⁴ = 1` ✓. All three
QSP conditions check out: degree 2 ≤ 2, even parity, norm constraint exact.

**Numerical verification** (`.venv` numpy, scanning 21 points on `[-1, 1]`):

```
phases (0,0,0):  max |⟨0|U_φ(x)|0⟩ - T₂(x)| = 1.1 × 10⁻¹⁶      ← machine precision
at x = 0.6:  W(0.6) = [[0.6, 0.8i], [0.8i, 0.6]]
             U = W(0.6)² = [[-0.28, 0.96i], [0.96i, -0.28]],  T₂(0.6) = -0.28 ✓
             (off-diagonal: 2·(0.6)·(0.8) = 0.96 = Q(x)√(1-x²) with Q = 2x ✓)
```

**The phases matter.** Changing only the middle phase to `π/2`, i.e. `φ = (0, π/2, 0)`:
`e^{i(π/2)Z} = diag(i, -i)`, and the product `W(x)·diag(i,-i)·W(x)` has top-left entry
`ix² + (is)(-i)(is) = ix² + i(1-x²)·(-1)·(-1) = i(x² + 1 - x²) = i` — a *constant*, verified
numerically to `1.2 × 10⁻¹⁶`. Same signal operator, same circuit depth, completely different
polynomial: the processing phases alone select the function, which is the whole point of QSP.
Lifted through the QSVT theorem, these same three phases applied to a block-encoded matrix `A`
implement `T₂` on every singular value of `A` simultaneously.

---

## Summary

- A block encoding places `A/α` in the top-left corner of a unitary; LCU, sparse oracles, and
  density matrices all produce one, making it the universal input model (`α = λ = ||H||₁` for
  LCU, matching 08/03's qubitization cost parameter).
- Quantum signal processing characterizes exactly which polynomials `d` interleaved signal and
  phase rotations produce on one qubit: degree ≤ `d`, parity `d mod 2`, norm ≤ 1. Chebyshev
  polynomials are the zero-phase response.
- QSVT lifts QSP to matrices via qubitization: `d` alternating `U/U†` calls with projector-
  controlled phases apply `P` to every singular value at once, for `d` queries total.
- One framework, many algorithms: sign function → Grover/fixed-point amplitude amplification;
  Jacobi-Anger truncation → Hamiltonian simulation at `O(λt + log(1/ε))`; `1/x` approximation →
  `O(κ log(1/ε))` linear solvers (modernizing HHL, 04/07); shifted sign filters → ground-state
  preparation.
- Algorithm design reduces to classical polynomial approximation plus classical phase-finding;
  QSVT is the standard compilation layer for fault-tolerant algorithms.

---

## Exercises

**Exercise 1**: Show that the degree-1 QSP sequence with general phases,
`U = e^{iφ₀Z} W(x) e^{iφ₁Z}`, has `⟨0|U|0⟩ = e^{i(φ₀+φ₁)} x`. Conclude that up to a global
phase, `P(x) = x` is the *only* degree-1 QSP polynomial with `|P(±1)| = 1`, and reconcile this
with the QSP theorem's constraints.

<details><summary>Solution</summary>

`e^{iφ₀Z} = diag(e^{iφ₀}, e^{-iφ₀})`, so the top-left entry of the product is
`e^{iφ₀} · x · e^{iφ₁} = e^{i(φ₀+φ₁)} x` (the off-diagonal path picks up the `Q` entry
instead). Numerically, `φ₀ = 0.7, φ₁ = -0.3, x = 0.42` gives `⟨0|U|0⟩ = 0.3868 + 0.1636i =
e^{0.4i}·0.42` ✓. The theorem requires odd parity at `d = 1` (so `P(x) = cx`), and the norm
condition at `x = ±1` forces `|P(±1)| = |c| = 1` since `Q`'s contribution vanishes there
(`1 - x² = 0`). Hence `c` is a pure phase: the phases can only *rotate* the degree-1 response,
never reshape it. Reshaping begins at degree 2, where `Q` has freedom on the interior.

</details>

**Exercise 2**: Prove that the all-zero phase sequence of length `d` gives
`⟨0|W(x)^d|0⟩ = T_d(x)`, using `W(x) = e^{iθX}` with `θ = arccos(x)`.

<details><summary>Solution</summary>

`W(x) = cos θ · I + i sin θ · X = e^{iθX}` (check: `cos θ = x`, `sin θ = √(1-x²)` matches the
matrix). Then `W(x)^d = e^{idθX} = cos(dθ) I + i sin(dθ) X`, so
`⟨0|W^d|0⟩ = cos(dθ) = cos(d arccos x) = T_d(x)` — the defining identity of Chebyshev
polynomials. Numerical check (this chapter's script): max deviation from `T_d` over
`x ∈ [-1,1]` is `< 10⁻¹⁵` for `d = 1, 2, 3, 5`. This is why Chebyshev expansions (Jacobi-Anger
for `e^{ixt}`, Chebyshev series for `1/x`) translate so directly into QSVT circuits: the
Chebyshev basis is what the hardware natively computes, and phases reweight the basis.

</details>

**Exercise 3**: Why can no QSP sequence implement `P(x) = x²` exactly? Which condition fails,
and what is the closest degree-2 polynomial QSP can do? What does this imply for implementing
non-definite-parity functions like `e^{ixt}` in QSVT?

<details><summary>Solution</summary>

`P(x) = x²` has even parity and degree 2, so conditions 1-2 on `P` look fine — the failure is
the parity condition on the *partner polynomial* `Q`, which at `d = 2` must be **odd**. Odd
`Q` has `Q(0) = 0`, so condition 3 at `x = 0` reads `|P(0)|² = 1` — but `x²` vanishes at 0.
(Directly: `W(0) = iX`, so at `x = 0` the sequence is a product of Z-phases and `iX` factors;
for even `d` the `|0⟩→|0⟩` amplitude always has modulus 1. Numerically, minimizing
`max_x |⟨0|U_φ(x)|0⟩ - x²|` over all phase triples bottoms out at exactly `1.0` — the error at
`x = 0` is irreducible.) The achievable even degree-2 responses are `T₂ = 2x² - 1` and its
phased deformations, all with `|P(0)| = 1`; targets violating such constraints must be
rescaled or shifted. The same preprocessing handles non-definite-parity functions like
`e^{ixt} = cos(xt) + i sin(xt)`: implement the even and odd parts with separate phase
sequences and combine them with one extra ancilla (an LCU of two QSVT circuits), at most
doubling the query count.

</details>

**Exercise 4**: Using the Bessel decay in the Jacobi-Anger expansion, the truncation degree for
`ε = 10⁻⁶` is `d = 15` at `t = 5` and `d = 22` at `t = 10` (computed numerically). Check these
against the scaling `d = O(t + log(1/ε))`, and estimate the query count to simulate a Hamiltonian
with `λ = 20` for time `t = 5` at `ε = 10⁻⁶`. Compare qualitatively with first-order Trotter.

<details><summary>Solution</summary>

Between `t = 5` and `t = 10` the degree grows by `7 ≈ Δt` (slope near 1) on top of a
`log(1/ε)`-sized additive offset of ≈ 10-12 — consistent with `d ≈ t + O(log(1/ε))`. For a
block-encoded `H/λ` with `λ = 20`, the signal is `x = E/λ` and the effective time is
`λt = 100`: degree `d ≈ 100 + O(log 10⁶) ≈ 115-120`, so ~120 queries to the block encoding,
each an `O(1)`-cost LCU `PREPARE/SELECT` pair. First-order Trotter at comparable accuracy
needs `n = O(t²||[A,B]||/ε) ~ 10⁷+` steps at `ε = 10⁻⁶` — the `1/ε` versus `log(1/ε)` gap of
Chapter 08/03, now with concrete numbers.

</details>

**Exercise 5**: A linear system has `κ = 100` and target precision `ε = 10⁻⁸`. Compare the
query counts of (a) original HHL at `O(κ²/ε)`, and (b) QSVT with degree `O(κ log(κ/ε))` plus
`O(κ)`-round amplification, and explain *why* QSVT's precision cost is logarithmic where HHL's
is polynomial.

<details><summary>Solution</summary>

(a) HHL: `κ²/ε = 10⁴ × 10⁸ = 10¹²` — dominated by the `1/ε` from phase-estimation precision.
(b) QSVT: degree `≈ κ ln(κ/ε) = 100 × ln(10¹⁰) ≈ 2.3 × 10³` queries per run, overall
`O(κ log(1/ε)) ≈ 10³-10⁴` with variable-time amplification — roughly *eight orders of
magnitude* fewer. The reason: HHL digitizes eigenvalues into a clock register, and `b` bits of
precision cost `2^b` uses of `e^{iAt}`. QSVT never digitizes — it applies `1/x` *coherently*
as a polynomial, and Chebyshev approximation error on `[1/κ, 1]` decays exponentially in
degree, so precision costs only `log(1/ε)`. The `κ` dependence is information-theoretically
necessary (`Ω(κ)` queries), so QSVT is essentially optimal in both parameters (cf. 04/07 on
Childs-Kothari-Somma).

</details>

---

## Further Reading

1. **Gilyén, A., Su, Y., Low, G. H., and Wiebe, N.** — "Quantum singular value transformation
   and beyond," *STOC 2019*; arXiv:1806.01838. The QSVT framework and the general theorem.
2. **Low, G. H. and Chuang, I. L.** — "Hamiltonian simulation by qubitization," *Quantum* 3,
   163 (2019); arXiv:1610.06546. Qubitization and optimal-query simulation.
3. **Martyn, J. M., Rossi, Z. M., Tan, A. K., and Chuang, I. L.** — "Grand unification of
   quantum algorithms," *PRX Quantum* 2, 040203 (2021). Pedagogical QSP/QSVT treatment of
   search, simulation, factoring subroutines, and linear systems.
4. **Childs, A. M., Kothari, R., and Somma, R. D.** — "Quantum algorithm for systems of linear
   equations with exponentially improved dependence on precision," *SIAM J. Comput.* 46, 1920
   (2017); arXiv:1511.02306. The `O(κ polylog(κ/ε))` linear solver QSVT reformulates.
5. **Lin, L. and Tong, Y.** — "Near-optimal ground state preparation," *Quantum* 4, 372 (2020);
   arXiv:2002.12508. Eigenvalue filtering for ground-state preparation via QSVT.
