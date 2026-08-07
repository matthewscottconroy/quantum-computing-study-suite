# Barren Plateaus

> **Prerequisites**: VQE fundamentals (06/01), ansatz design (06/02), parameter-shift gradient
> (06/03), basic probability theory
> **Connects to**: Ansatz design strategies (06/02), noise and error mitigation (06/06),
> fundamental limits of variational algorithms

---

## Overview

In 2018, McClean, Boixo, Smelyanskiy, Babbush, and Neven published a paper titled "Barren
plateaus in quantum neural network training landscapes." The result was sobering: for random
quantum circuits acting on `n` qubits with global cost functions, the variance of any gradient
component decreases **exponentially** in `n`. This means that for large systems, gradients are
exponentially small in magnitude, their fluctuations are exponentially small, and distinguishing
a true gradient from shot noise requires exponentially many measurements.

The term "barren plateau" refers to the training landscape of the cost function: a vast, flat
region where no gradient signal is visible. A random point in parameter space is almost certainly
in a barren plateau, and gradient-based optimization from such a starting point will fail to
navigate toward the (rare, deep) minima.

Barren plateaus threaten the scalability of virtually all variational quantum algorithms.
Understanding their origin, quantifying their severity, and developing mitigation strategies is
one of the most active and consequential research areas in quantum computing. This chapter
provides a rigorous treatment.

---

## The McClean et al. Result

### Setup

Consider an `n`-qubit parameterized circuit `U(θ) = W L(θ) V` where `L(θ)` is a single
parameterized layer and `V, W` are random Clifford circuits drawn from an approximate unitary
2-design (e.g., several layers of random Clifford gates). The cost function is:

```
C(θ) = ⟨0|U(θ)† O U(θ)|0⟩
```

where `O` is an observable. Define the partial derivative with respect to any parameter `θᵢ`.

### Main Theorem

**Theorem (McClean et al., 2018)**: For a global observable `O` (acting non-trivially on all
`n` qubits, e.g., `O = |0...0⟩⟨0...0|`), and for circuits `V` and `W` that form unitary
2-designs:

```
E_θ[∂C/∂θᵢ] = 0
Var_θ[∂C/∂θᵢ] ≤ 2/d² = 2/4^n
```

where the expectation and variance are over random parameter choices, and `d = 2^n` is the
Hilbert space dimension.

The variance is exponentially small: `Var ∝ 2^{-2n}`, so the gradient standard deviation
`∼ 2^{-n}`. To detect this gradient above shot noise requires at least `∼ 4^n` measurements.
For `n = 50` qubits: `4^{50} ≈ 10^{30}` measurements — impossible.

### Intuition: Concentration of Measure

The underlying mechanism is **concentration of measure**: random quantum circuits on many qubits
form approximate unitary designs, spreading the quantum state nearly uniformly over the Hilbert
space. The cost function value at a random point is very close to its average `Tr[O]/d`, with
fluctuations exponentially small in `n`.

More intuitively: a random high-depth quantum circuit maps `|0⟩` to something close to the
maximally mixed state (averaged over parameters). All such states give nearly the same energy.
The cost function is essentially constant everywhere on the parameter manifold — hence the
"plateau."

### Mean is Exactly Zero

The mean `E[∂C/∂θᵢ] = 0` exactly for symmetric distributions. This follows from the rotational
invariance of the Haar measure: for any `θᵢ`, the distribution over `U(θ)` is symmetric
under `θᵢ → θᵢ + π`, which maps gradients to their negatives. Combined with concentration,
this means the distribution of gradients is nearly a delta function at zero.

---

## Local vs. Global Cost Functions

### The Local Cost Escape Route

Cerezo et al. (2021) showed that using **local cost functions** (observables acting on only
`O(1)` qubits) can partially escape barren plateaus:

**Theorem (Cerezo et al., 2021)**: For a local observable `O = Oₗ ⊗ I^{⊗(n-l)}` acting on
`l` qubits, and a circuit of depth `D`:

- If `D = O(log n)`: `Var[∂C/∂θᵢ] = Ω(1/poly(n))` — polynomial, not exponential.
- If `D = Ω(n)`: `Var[∂C/∂θᵢ] = O(1/4^n)` — still exponentially small.

**Consequence**: Local cost functions at shallow depth avoid barren plateaus. But local cost
functions are computationally weaker — they do not directly probe global properties of the state.

### The Concentration Hierarchy

Different types of ansätze and cost functions fall into different regimes:

| Ansatz/cost type | Gradient variance scaling |
|-----------------|--------------------------|
| Random, global cost, depth `O(n)` | `2^{-2n}` (exponential BP) |
| Random, local cost, depth `O(log n)` | `1/poly(n)` (trainable) |
| Random, local cost, depth `O(n)` | `2^{-2n}` (noise-induced BP) |
| Structured (HVA, equivariant), global | `1/poly(n)` (often) |
| ADAPT-VQE, first parameter | Non-zero by construction |

---

## Noise-Induced Barren Plateaus

### The Wang et al. Result

Wang et al. (2021) showed that even local cost functions suffer barren plateaus in the presence
of hardware noise:

**Theorem (Wang et al., 2021)**: For a circuit of depth `D` with depolarizing noise probability
`p` per gate, the cost function is exponentially close to a constant:

```
|C(θ) - C_mixed| ≤ (1 - p)^D · ||O||
```

where `C_mixed = Tr[O ρ_mixed]/2^n` is the cost for the maximally mixed state.

**Consequence**: As depth increases, the cost function "leaks" toward the constant `C_mixed`
exponentially fast in `D`. Gradients shrink as `(1-p)^D`. For `p = 10^{-2}` and `D = 100`:
`(0.99)^{100} ≈ 0.37` — 63% of the signal is lost. For `D = 1000`: `< 5×10^{-5}` of signal
remains.

This noise-induced barren plateau is independent of the expressibility of the ansatz; it arises
purely from the physical noise of the hardware. It sets a hard limit on useful circuit depth
for NISQ-era variational algorithms.

---

## Can Barren Plateaus Be Fixed?

### What Cannot Fix a Barren Plateau

**Claim**: No classical preprocessing strategy can fix a barren plateau without changing the
information content of the circuit or using exponential classical resources.

**Argument**: The barren plateau implies that the cost function `C(θ)` has exponentially small
variance around its mean. This means the cost landscape contains exponentially little information
about where the minima are. Any strategy that does not access this (exponentially small) information
cannot find the minima faster than random search.

In particular:
- **Warm starting** from a good classical solution only helps if the classical solution is
  already near-optimal.
- **Adaptive learning rate** scaling cannot overcome zero gradient direction information.
- **Re-parameterization** (changing basis) cannot change the information content; barren plateaus
  are reparametrization-invariant properties of the distribution `{|ψ(θ)⟩}`.

### Genuine Mitigation Strategies

**1. Identity block initialization (Grant et al., 2019)**: Initialize every pair of adjacent
layers to implement the identity (parameters initialized to cancel). This places the initial
state in a region where gradients are non-zero (near the identity, the QFIM is full rank).

**2. Layer-wise training**: Train one layer at a time, fixing earlier layers once trained. Each
new layer is added near the identity, avoiding barren plateau initialization.

**3. Local cost functions** (Cerezo et al.): Design the cost function to probe local observables,
avoiding global cost functions that induce barren plateaus.

**4. Problem-inspired structured ansätze**: Use ansätze with natural problem structure (HVA,
ADAPT-VQE). By construction, the initial ansatz gradients are tied to the problem's structure
and are not exponentially small.

**5. Quantum convolutional neural networks (QCNN)**: Circuits with a hierarchical pooling
structure (Cong et al., 2019) have polynomial gradient variance; QCNN architectures are
specifically designed to avoid barren plateaus for certain problem types.

---

## The Fundamental Trade-Off

Barren plateaus reveal a deep tension in variational quantum algorithms:

- **Expressive ansatz** → can represent complex states → prone to barren plateaus → untrainable
- **Structured ansatz** → avoids barren plateaus → restricted expressibility → may miss the
  ground state

This is the quantum analogue of the **no-free-lunch theorem** for machine learning. There is no
universal variational algorithm that is both expressive and trainable for all problems. Problem-
specific structure must be exploited.

The practical upshot: VQE and QAOA may be useful only for problems where:
1. Problem structure guides ansatz design away from barren plateaus.
2. System size is small enough that barren plateaus are not exponentially severe.
3. Adiabatic initialization provides a warm start near the solution.

---

## Key Formulas

- **Barren plateau theorem (global cost)**: `Var_θ[∂C/∂θᵢ] ≤ 2/4^n`
- **Mean gradient**: `E_θ[∂C/∂θᵢ] = 0` (symmetry/concentration)
- **Local cost threshold**: `Var ∝ 1/poly(n)` for depth `O(log n)` and local observables
- **Noise-induced plateau**: `|C(θ) - C_mix| ≤ (1-p)^D ||O||`
- **Required measurement shots**: `S ~ 1/Var ~ 4^n` to detect gradient (exponential overhead)

---

## Worked Example: Gradient Variance Calculation

**Setup**: `n = 4` qubit random circuit (`U(θ) = W Ry(θ) V` with `V, W` random Clifford).
Observable: `O = Z₁⊗Z₂⊗Z₃⊗Z₄` (global 4-qubit Pauli).

**Theoretical bound**: `Var[∂C/∂θ] ≤ 2/4^4 = 2/256 ≈ 0.0078`.

**Numerical experiment** (schematic):
Draw 1000 random `(V, W, θ)` samples. Compute `∂C/∂θ` via parameter shift for each.

Results:
- Mean: `-0.0023` (approximately 0, as expected)
- Standard deviation: `0.088` → variance `≈ 0.0077` ✓ (matches bound)

For `n = 10`:
- Theoretical bound: `2/4^{10} = 2/10^6 ≈ 2×10^{-6}`
- Standard deviation: `~1.4×10^{-3}`
- To achieve SNR=1: `S ≥ 1/Var = 5×10^5` shots per gradient component.
- For 100 parameters: `10^8` shots per gradient step.

For `n = 20`: `10^{17}` shots needed. Infeasible with any realistic hardware.

This calculation shows concretely why barren plateaus make large-scale VQE intractable without
structured ansätze.

---

## Summary

- **Barren plateaus** are exponentially flat regions in the cost landscape of random parameterized
  quantum circuits; gradient variance scales as `2^{-2n}` for `n` qubits with global cost functions.
- The mechanism is **concentration of measure**: random circuits form approximate unitary designs,
  spreading all states near the maximally mixed state.
- **Noise-induced barren plateaus** further constrain trainability: circuit noise exponentially
  suppresses the cost signal with circuit depth, independent of ansatz expressibility.
- **Local cost functions** at shallow depth avoid barren plateaus but are computationally weaker.
- **Genuine mitigation**: identity block initialization, layer-wise training, ADAPT-VQE, and
  symmetry-preserving structured ansätze.
- The barren plateau problem reveals a fundamental expressibility-trainability tension; no
  universal fix exists without exploiting problem structure.

---

## Further Reading

1. **McClean, J. R. et al.** — "Barren plateaus in quantum neural network training landscapes,"
   *Nature Communications* 9, 4812 (2018). The seminal barren plateau paper.
2. **Cerezo, M. et al.** — "Cost function dependent barren plateaus in shallow parametrized
   quantum circuits," *Nature Communications* 12, 1791 (2021). Local vs. global costs.
3. **Wang, S. et al.** — "Noise-induced barren plateaus in variational quantum algorithms,"
   *Nature Communications* 12, 6961 (2021). Noise-induced plateaus.
4. **Grant, E. et al.** — "An initialization strategy for addressing barren plateaus in
   parametrized quantum circuits," *Quantum* 3, 214 (2019). Identity block initialization.
5. **Arrasmith, A. et al.** — "Equivalence of quantum barren plateaus to cost concentration
   and narrow gorges," *Quantum Sci. Technol.* 7, 045015 (2022). Mathematical foundations.
