# Probability and Statistics for Quantum Computing

> **Prerequisites**: 01_linear_algebra.md (expectation of an observable as `⟨ψ|M|ψ⟩`, spectral decomposition), 02_complex_numbers_and_hilbert_spaces.md (moduli of complex numbers); single-variable calculus for the entropy sections  
> **Connects to**: `02_quantum_mechanics/03_quantum_measurements.md` (the Born rule is a probability measure), `06_variational_quantum_algorithms/01_vqe_fundamentals.md` (shot budgets), `07_quantum_hardware/04_benchmarking_and_characterization.md` (fits and error bars), `05_quantum_error_correction/02_classical_error_correction.md` and `08_advanced_topics/02_quantum_information_theory.md` (entropy), `02_quantum_mechanics/04_entanglement_and_nonlocality.md` (Bell-test statistics)

## Overview

Every number that comes out of a quantum computer is a *sample*. A circuit run 4,000 times does not return `⟨Z⟩`; it returns a bit-string histogram from which `⟨Z⟩` is *estimated*, with an error bar that shrinks only as `1/√N`. The Born rule turns amplitudes into a probability distribution, and everything downstream — expectation values for VQE, success probabilities for Grover, CHSH correlators for Bell tests, decay curves for randomized benchmarking — is classical statistics applied to that distribution.

This chapter collects the probability and statistics that the rest of the corpus assumes. The first half is classical probability: random variables, moments, Bayes' theorem, the binomial distribution and its normal approximation, and the concentration inequalities (Hoeffding, Chernoff) that give the universal shot-count rule `N ∼ 1/ε²`. The second half covers information measures (Shannon entropy, mutual information, KL divergence, the binary entropy function that appears throughout the error-correction and cryptography chapters), then confronts the one place where quantum theory departs from classical probability — amplitudes interfere, probabilities do not — and closes with the hypothesis-testing vocabulary used when a paper reports a Bell violation "at 18σ" or a gate error "with 95% confidence".

## Sample Spaces, Events, and Random Variables

A **probability space** is a triple `(Ω, F, P)`: a **sample space** `Ω` of outcomes, a collection `F` of subsets of `Ω` called **events** (a σ-algebra: closed under complement and countable union), and a **probability measure** `P: F → [0,1]` satisfying Kolmogorov's axioms:

1. `P(A) ≥ 0` for every event `A`
2. `P(Ω) = 1`
3. **Countable additivity**: `P(A₁ ∪ A₂ ∪ ...) = Σᵢ P(Aᵢ)` for pairwise disjoint events

For an `n`-qubit measurement in the computational basis, `Ω = {0,1}ⁿ` (finite, so `F` is simply all subsets), and `P({x}) = |⟨x|ψ⟩|²`. Axiom 2 is the normalization `Σₓ |⟨x|ψ⟩|² = ⟨ψ|ψ⟩ = 1`.

A **random variable** is a function `X: Ω → ℝ`. Its **distribution** is `pₓ(x) = P(X = x)` for discrete `X`, or a density `f(x)` with `P(a ≤ X ≤ b) = ∫ₐᵇ f(x)dx` for continuous `X`. Two random variables are **independent** if `P(X = x, Y = y) = P(X = x)P(Y = y)` for all `x, y`. Measuring the eigenvalue of an observable `M` is the random variable `X(ω) = m` when outcome `ω` lies in the eigenspace of `m`.

## Expectation, Variance, and Covariance

The **expectation** (mean) of a discrete random variable is `E[X] = Σₓ x·pₓ(x)`; for continuous `X`, `E[X] = ∫ x f(x)dx`. Expectation is linear: `E[aX + bY] = aE[X] + bE[Y]` — *always*, independent or not.

The **variance** measures spread:

`Var(X) = E[(X − E[X])²] = E[X²] − E[X]²`

and the **standard deviation** is `σ = √Var(X)`. Variance is not linear: `Var(aX) = a²Var(X)`, and

`Var(X + Y) = Var(X) + Var(Y) + 2Cov(X, Y)`,  `Cov(X, Y) = E[XY] − E[X]E[Y]`

The **covariance** vanishes for independent variables (independence implies `E[XY] = E[X]E[Y]`; the converse is false). The normalized covariance `Corr(X,Y) = Cov(X,Y)/(σₓσ_Y) ∈ [−1, 1]` is the **correlation coefficient**. In a CHSH experiment, each correlator `E(a,b) = E[AB]` for `±1`-valued outcomes is exactly such a quantity.

**Quantum dictionary.** For an observable `M = Σₘ m Pₘ` and state `|ψ⟩`, the measured eigenvalue has `E[X] = Σₘ m⟨ψ|Pₘ|ψ⟩ = ⟨ψ|M|ψ⟩` and `Var(X) = ⟨ψ|M²|ψ⟩ − ⟨ψ|M|ψ⟩²`. A Pauli operator has eigenvalues `±1`, so `M² = I` and `Var = 1 − ⟨M⟩² ≤ 1`. This one-line bound sets the shot cost of every expectation-value estimate in the corpus.

## Conditional Probability and Bayes' Theorem

The **conditional probability** of `A` given `B` (with `P(B) > 0`) is `P(A|B) = P(A ∩ B)/P(B)`. Rearranging twice gives **Bayes' theorem**:

`P(A|B) = P(B|A)P(A) / P(B)`,  `P(B) = Σᵢ P(B|Aᵢ)P(Aᵢ)` (law of total probability over a partition `{Aᵢ}`)

Bayes' theorem is the rule for *updating beliefs on evidence*. It is how readout error is handled in practice. Suppose a qubit is in `|1⟩` with prior probability `0.3` and the readout has assignment errors `P(read 1 | true 1) = 0.95`, `P(read 1 | true 0) = 0.02`. If the detector reports `1`:

`P(true 1 | read 1) = (0.95 × 0.3) / (0.95 × 0.3 + 0.02 × 0.7) = 0.285 / (0.285 + 0.014) ≈ 0.953`

The prior `0.3` became a posterior `0.953` — the evidence is strong because false positives are rare. The same arithmetic, applied to a full `2ⁿ × 2ⁿ` assignment matrix, is the readout-mitigation step that precedes the gate-error methods (ZNE, PEC, CDR) of `06_variational_quantum_algorithms/06_noise_and_error_mitigation.md`; that chapter does not itself cover readout calibration, but Exercise 1 below works through the inversion.

*Do not confuse Bayesian updating with quantum collapse.* Bayes' rule updates a probability distribution over states of a system that has a definite (but unknown) value. The Born-rule collapse in `02_quantum_mechanics/03_quantum_measurements.md` produces a new *state vector*, and, as the interference section below shows, no classical prior over hidden values reproduces it in general.

## The Binomial Distribution and Its Normal Approximation

Run a circuit `N` times and count how often outcome `1` appears. If each shot is independent with success probability `p`, the count `K` is **binomial**:

`P(K = k) = C(N,k) pᵏ(1−p)^{N−k}`,  `E[K] = Np`,  `Var(K) = Np(1−p)`

The estimated probability `p̂ = K/N` therefore has `E[p̂] = p` and `Var(p̂) = p(1−p)/N ≤ 1/(4N)`. With `N = 1000` and `p = 0.3`: `E[K] = 300`, `σ_K = √210 ≈ 14.5`, so `σ_p̂ ≈ 0.0145`.

**Central limit theorem (CLT).** For large `N`, the standardized sum `(K − Np)/√(Np(1−p))` is approximately standard normal `N(0,1)`, whatever the underlying distribution. This is why error bars are quoted as "`±1σ` ≈ 68%, `±2σ` ≈ 95%, `±3σ` ≈ 99.7%". Check: with `N = 1000`, `p = 0.3`, the exact binomial gives `P(K ≤ 280) = 0.0886`; the normal approximation (with continuity correction, `z = (280.5 − 300)/14.49 = −1.35`) gives `0.0892`. The rule of thumb `Np(1−p) ≳ 10` is comfortably met.

The CLT explains the *shape* of fluctuations but gives no rigorous finite-`N` guarantee. For that we need concentration inequalities.

## Law of Large Numbers and Concentration Inequalities

The **(weak) law of large numbers** states that the sample mean `X̄_N = (1/N)Σᵢ Xᵢ` of i.i.d. variables converges in probability to `μ = E[X]`. **Chebyshev's inequality** gives the first quantitative version: `P(|X̄_N − μ| ≥ ε) ≤ Var(X)/(Nε²)`. Polynomial decay in `N` is weak; bounded variables do exponentially better.

**Hoeffding's inequality.** If `X₁, ..., X_N` are independent with `Xᵢ ∈ [a, b]`, then

`P(|X̄_N − μ| ≥ ε) ≤ 2 exp(−2Nε² / (b − a)²)`

**The shot-count rule.** Set the right-hand side equal to a failure probability `δ` and solve for `N`:

`N ≥ (b − a)² ln(2/δ) / (2ε²)`

For a probability estimate (`Xᵢ ∈ {0,1}`, so `b − a = 1`): `N ≥ ln(2/δ)/(2ε²)`. For `ε = 0.01`, `δ = 0.05`: `N ≥ ln(40)/(2 × 10⁻⁴) ≈ 18,444` shots. For a Pauli expectation value (`Xᵢ ∈ {−1, +1}`, `b − a = 2`): `N ≥ 2 ln(2/δ)/ε²`, which for the same `ε, δ` is `≈ 73,778` shots. Either way the scaling is

`N ∼ 1/ε²` — halving the error costs four times the shots, and each extra decimal digit costs a factor of 100.

This quadratic law is the single most important practical fact about sampling quantum computers. It is why quantum counting / amplitude estimation — phase estimation (`04_quantum_algorithms/04_quantum_phase_estimation.md`) applied to the Grover operator (`04_quantum_algorithms/05_grover_search.md`, §Quantum Counting) — which reaches precision `ε` with `O(1/ε)` oracle calls, is called a quadratic speedup, and why VQE shot budgets reach `10⁶–10⁸` (worked example below).

**Chernoff bounds** give the multiplicative form for a sum `K` of independent Bernoulli trials with mean `μ = E[K]`: for `0 < δ ≤ 1`,

`P(K ≥ (1+δ)μ) ≤ exp(−δ²μ/3)`,  `P(K ≤ (1−δ)μ) ≤ exp(−δ²μ/2)`

The BQP error-reduction argument in `08_advanced_topics/01_quantum_complexity_theory.md` (majority vote over `k` runs drives error to `e^{−ck}`) is a direct application.

**Distinguishing two probabilities.** Suppose a circuit outputs `1` with probability either `p` or `q` (`p < q`), and you must decide which. Threshold the empirical frequency at the midpoint `(p+q)/2`; an error requires a deviation of at least `(q−p)/2`, so Hoeffding gives error `≤ exp(−N(q−p)²/2)` and

`N ≥ 2 ln(1/δ) / (q − p)²`

To separate `p = 0.50` from `q = 0.55` with error `δ = 0.01` requires `N ≥ 2 ln(100)/0.0025 ≈ 3,684` shots. (The normal approximation says the actual error at that `N` is about `0.0012` — Hoeffding is loose by roughly a factor of ten, but its scaling is right.) The asymptotically optimal exponent for this symmetric error is the *Chernoff information*, a close cousin of the KL divergence discussed below; for `p` near `1/2` it essentially coincides with Hoeffding's exponent `(q−p)²/2`, so the bound above is loose only in its prefactor, not its rate.

## Estimators: Bias, Variance, and Monte Carlo

An **estimator** `θ̂` is any function of the data used to guess a parameter `θ`. Its **bias** is `E[θ̂] − θ` and its **mean squared error** decomposes as

`MSE(θ̂) = E[(θ̂ − θ)²] = Bias(θ̂)² + Var(θ̂)`

The sample mean is unbiased for `μ`. The naive sample variance `(1/N)Σ(Xᵢ − X̄)²` is *biased* low by the factor `(N−1)/N`; dividing by `N − 1` instead (Bessel's correction) removes the bias. A simulation of `±1` outcomes with `⟨X⟩ = 0.4` in blocks of `N = 5` shots gives mean naive variance `0.672` versus unbiased `0.840` and true `1 − 0.4² = 0.84`. The lesson generalizes: an estimator can be systematically wrong even with unlimited data, and zero-noise extrapolation and other mitigation methods (`06_variational_quantum_algorithms/06_noise_and_error_mitigation.md`) trade bias for variance deliberately.

**Monte Carlo estimation** replaces an expectation by a sample average: `E[f(X)] ≈ (1/N)Σᵢ f(Xᵢ)`, with standard error `σ_f/√N`. Estimating `π` by throwing `10⁶` uniform points into the unit square and counting those inside the quarter circle gives `3.1432 ± 0.0016`. Every expectation value read off a quantum computer is a Monte Carlo estimate in exactly this sense: the hardware is the sampler, and for a Hamiltonian `H = Σᵢ cᵢPᵢ` estimated term-by-term with `Sᵢ` shots each,

`Var(Ê) = Σᵢ cᵢ² Var(⟨Pᵢ⟩)/Sᵢ ≤ Σᵢ cᵢ²/Sᵢ`

## Information Measures

**Shannon entropy** quantifies the uncertainty of a distribution `p` in bits:

`H(X) = −Σₓ p(x) log₂ p(x)`  (with `0 log 0 := 0`)

It is zero for a deterministic outcome and maximal, `log₂|Ω|`, for the uniform distribution; `H(X)` is the minimum average number of bits needed to encode samples of `X` (Shannon's source-coding theorem). The **binary entropy function**

`H₂(p) = −p log₂ p − (1−p) log₂(1−p)`

is symmetric about `p = 1/2`, where it equals `1`, and has infinite slope at `0` and `1`. Reference values: `H₂(0.1) = 0.469`, `H₂(0.25) = 0.811`, `H₂(0.5) = 1`. It is the capacity deficit of the binary symmetric channel (`C = 1 − H₂(p)`, `05_quantum_error_correction/02_classical_error_correction.md`), the entropy of a qubit's reduced state in `02_quantum_mechanics/05_density_matrices_and_open_systems.md`, and the origin of the BB84 threshold: the key rate `1 − 2H₂(Q)` in `04_quantum_algorithms/08_quantum_cryptography.md` crosses zero at `Q = 0.110`, because `H₂(0.11) = 0.4999`.

**Joint, conditional, and mutual information.** For two random variables, `H(X,Y) = −Σ p(x,y) log₂ p(x,y)`, the **conditional entropy** is `H(Y|X) = H(X,Y) − H(X)` (the remaining uncertainty in `Y` once `X` is known), and the **mutual information**

`I(X;Y) = H(X) + H(Y) − H(X,Y) = H(Y) − H(Y|X) ≥ 0`

measures how many bits one variable reveals about the other; it is zero iff they are independent. For a binary symmetric channel with flip probability `0.1` and uniform input, `I(X;Y) = 1 − H₂(0.1) = 0.531` bits per use. The quantum analogues (von Neumann entropy, quantum mutual information, Holevo bound) are developed in `08_advanced_topics/02_quantum_information_theory.md` with the same algebra applied to eigenvalue spectra.

**Kullback–Leibler divergence** compares two distributions on the same space:

`D(P‖Q) = Σₓ p(x) log₂ (p(x)/q(x)) ≥ 0`, with equality iff `P = Q` (Gibbs' inequality)

It is not symmetric and not a metric, but it controls hypothesis testing. Two different error exponents arise, and they must not be confused:

- **Stein's lemma** (asymmetric setting): with `P` as the null hypothesis and the type-I error held below a fixed `α`, the type-II error of the optimal likelihood-ratio test decays as `2^{−N·D(P‖Q)}` — the exponent depends on which hypothesis is the null.
- **Chernoff information** (symmetric/Bayesian setting, the one relevant to the midpoint test above): the best achievable total error decays as `2^{−N·C(P,Q)}` with

`C(P,Q) = max_{0≤λ≤1} [ −log₂ Σₓ p(x)^λ q(x)^{1−λ} ]`

which is symmetric in `P` and `Q` and never larger than either `D(P‖Q)` or `D(Q‖P)` (Cover & Thomas, §11.8–11.9). For `p = 0.5`, `q = 0.6` (Exercise 5), `C = 0.0073` bits, roughly a quarter of `D(P‖Q) = 0.0294` bits.

**Pinsker's inequality** bounds it below by the total-variation distance `TV(P,Q) = ½Σₓ|p(x) − q(x)|`:

`D(P‖Q) ≥ (2/ln 2) · TV(P,Q)²`  (bits)

Example: for Bernoulli distributions with `p = 0.5` and `q = 0.6`, `TV = 0.1`, Pinsker demands `D ≥ 0.0289` bits, and the actual value is `D = 0.5 log₂(0.5/0.6) + 0.5 log₂(0.5/0.4) = 0.0294` bits — nearly tight. The trace distance in `02_quantum_mechanics/10_distance_measures_and_lindblad.md` is the quantum analogue of `TV`; the quantum relative entropy `S(ρ‖σ) = Tr ρ(log₂ρ − log₂σ)` satisfies the same Pinsker bound `S(ρ‖σ) ≥ (2/ln 2)·T(ρ,σ)²` (Wilde, *Quantum Information Theory*, §11.9), though that chapter does not cover it.

## Classical versus Quantum Probability

A classical random process on `d` states evolves a probability vector `p` by a **stochastic matrix** `S` (non-negative entries, columns summing to one): `p ↦ Sp`. Quantum mechanics instead evolves an **amplitude vector** `|ψ⟩ ∈ ℂᵈ` by a **unitary** `U`, and probabilities are recovered only at the end by the **Born rule** `P(x) = |⟨x|ψ⟩|²`. Amplitudes are complex numbers of modulus at most one whose *squared moduli* sum to one — they are not probabilities, and the difference is not cosmetic.

**One calculation.** Send `|0⟩` through a Hadamard, a phase gate `P(φ) = diag(1, e^{iφ})`, and a second Hadamard. The amplitude of `|0⟩` after the sequence is

`⟨0|H P(φ) H|0⟩ = ½(1 + e^{iφ})`, so `P(0) = |½(1 + e^{iφ})|² = cos²(φ/2)`

At `φ = π/3`, `P(0) = 0.75`; at `φ = π`, `P(0) = 0` — the two paths to `|0⟩` cancel exactly. Now attempt a classical account: a Hadamard "randomizes" the bit, so model it by the stochastic matrix `S = ½[[1,1],[1,1]]`. Two applications give `S²(1,0)ᵀ = (½, ½)` regardless of any phase, because a classical mixture cannot depend on `φ` (the phase does nothing to a bit that already has a definite value). Adding a second route to an outcome can only *increase* a classical probability; it can *decrease* a quantum one. That is **interference**, and it is the resource that Deutsch–Jozsa, Grover, and the QFT exploit (`04_quantum_algorithms/01_quantum_parallelism_and_interference.md`).

**The Born rule as the bridge.** Everything classical in this chapter applies the instant a measurement is made: the Born rule delivers a genuine probability measure on outcomes, shots are i.i.d. samples from it, and Hoeffding, Bayes, and the CLT apply verbatim. The quantum novelty lives entirely *before* measurement, in how the distribution was generated. The formal statement — projective and POVM measurements, post-measurement states, and the expectation-value formula `⟨M⟩ = Tr(ρM)` — is in `02_quantum_mechanics/03_quantum_measurements.md`.

## Statistical Hypothesis Testing

Experimental quantum papers report claims such as "CHSH `S = 2.42`, violating the local bound by `18σ`" or "error per Clifford `(1.3 ± 0.2) × 10⁻³`". The framework behind both is hypothesis testing.

- A **null hypothesis** `H₀` is the boring explanation (local realism holds, `S ≤ 2`; the gate has error `≥ x`).
- A **test statistic** `T` is computed from the data (`S`, or the fitted decay rate).
- The **p-value** is `P(T at least as extreme as observed | H₀)`. A small p-value means the data would be surprising if `H₀` were true; it is *not* the probability that `H₀` is true (that would require a prior and Bayes' theorem).
- A **z-score** `z = (T − T₀)/σ_T` converts a Gaussian-distributed statistic to a p-value: `z = 3` gives one-sided `p ≈ 1.3 × 10⁻³`, `z = 5` gives `2.9 × 10⁻⁷`.

**Bell test.** Each CHSH correlator `Eᵢ` is the mean of `n` `±1` outcomes, so `Var(Eᵢ) = (1 − Eᵢ²)/n ≤ 1/n`. With `n = 5000` shots per setting and `E₁ = E₂ = E₃ ≈ 0.605`, `E₄ ≈ −0.605` (so `S = E₁ + E₂ + E₃ − E₄ = 2.42`, and `Var(S) = Σᵢ Var(Eᵢ)` since the four settings are independent), `σ_S = √(4 × (1 − 0.605²)/5000) = 0.0225` and `z = (2.42 − 2)/0.0225 = 18.6`. The one-sided p-value is `≈ 6 × 10⁻⁷⁸`. The corresponding physics is in `02_quantum_mechanics/04_entanglement_and_nonlocality.md`; note that the statistics alone do not close the locality or detection loopholes.

**Randomized benchmarking.** The RB decay `P(m) = A pᵐ + B` in `07_quantum_hardware/04_benchmarking_and_characterization.md` is fit by least squares; the reported uncertainty on `p` comes from the fit covariance or from **bootstrapping** (resampling the per-length shot data with replacement and refitting). A `95%` confidence interval is the range that would contain the true value in 95% of repeated experiments. Two cautions carry over from the wider sciences: multiple comparisons inflate false positives (testing twenty qubits at `p < 0.05` will flag one by chance), and a p-value says nothing about *effect size* — a `10⁻⁴` improvement in fidelity can be statistically significant and practically irrelevant.

## Key Formulas

**Expectation and variance of an observable**:
`⟨M⟩ = ⟨ψ|M|ψ⟩`,  `Var(M) = ⟨M²⟩ − ⟨M⟩²`,  Pauli: `Var = 1 − ⟨P⟩² ≤ 1`

**Bayes' theorem**:
`P(A|B) = P(B|A)P(A) / Σᵢ P(B|Aᵢ)P(Aᵢ)`

**Binomial estimate**:
`p̂ = K/N`,  `Var(p̂) = p(1−p)/N ≤ 1/(4N)`

**Hoeffding and the shot-count rule** (`Xᵢ ∈ [a,b]`):
`P(|X̄ − μ| ≥ ε) ≤ 2e^{−2Nε²/(b−a)²}`  ⟹  `N ≥ (b−a)² ln(2/δ)/(2ε²)`

**Distinguishing `p` from `q`**:
`N ≥ 2 ln(1/δ)/(q − p)²`

**Shannon, binary, conditional, mutual**:
`H(X) = −Σ p log₂ p`,  `H₂(p) = −p log₂ p − (1−p) log₂(1−p)`,  `I(X;Y) = H(X) + H(Y) − H(X,Y)`

**KL divergence, Pinsker, Chernoff information**:
`D(P‖Q) = Σ p log₂(p/q) ≥ (2/ln 2)·TV(P,Q)²`,  `C(P,Q) = max_λ [−log₂ Σ p^λ q^{1−λ}]` (symmetric-error exponent `2^{−N·C}`)

**Born rule**:
`P(x) = |⟨x|ψ⟩|²`,  interference: `|α + β|² ≠ |α|² + |β|²` in general

**Optimal shot allocation for `H = Σ cᵢPᵢ`** (derived below):
`Sᵢ ∝ |cᵢ|σᵢ`,  `N_total = (Σᵢ |cᵢ|σᵢ)² / ε²`

## Worked Example

**Problem**: You submit the two-qubit H₂ Hamiltonian from `06_variational_quantum_algorithms/01_vqe_fundamentals.md`,

`H = −1.052373 I + 0.397937 Z₁ − 0.397937 Z₂ − 0.011280 Z₁Z₂ + 0.180931 X₁X₂`  (Hartree),

to an `EstimatorV2` primitive and require the statistical error on `⟨H⟩` to be `σ_E ≤ 1 mHa = 10⁻³ Ha`. Assuming each Pauli term is measured in its own circuit, how many total shots are needed (a) with equal shots per term, (b) with the optimal coefficient-weighted allocation?

**Solution**:

*Step 0 — what costs shots.* The identity term is a constant and costs nothing. The four remaining terms have `|cᵢ| = (0.397937, 0.397937, 0.011280, 0.180931)`. Each is a `±1`-valued Pauli, so `Var(⟨Pᵢ⟩) = (1 − ⟨Pᵢ⟩²)/Sᵢ ≤ 1/Sᵢ` with `Sᵢ` shots; we use the worst-case bound `σᵢ² = 1` because the state is unknown before the optimization converges. Then

`σ_E² = Σᵢ cᵢ² Var(⟨Pᵢ⟩) ≤ Σᵢ cᵢ²/Sᵢ`

*Step 1 — naive equal allocation.* With `Sᵢ = S` for all four terms, `σ_E² ≤ (Σᵢ cᵢ²)/S`. The sum of squares is

`Σ cᵢ² = 0.158354 + 0.158354 + 0.000127 + 0.032736 = 0.349571`

Requiring `σ_E ≤ 10⁻³` gives `S ≥ 0.349571/10⁻⁶ = 349,571` shots per term, i.e. `N_naive = 4 × 349,571 ≈ 1.40 × 10⁶` shots in total. Note that the `Z₁Z₂` term, which contributes `0.04%` of the variance, receives a quarter of the budget.

*Step 2 — optimal allocation.* Minimize `N = Σᵢ Sᵢ` subject to `Σᵢ cᵢ²σᵢ²/Sᵢ = ε²`. The Lagrangian condition `∂/∂Sᵢ [Σ Sᵢ + λ Σ cᵢ²σᵢ²/Sᵢ] = 0` gives `Sᵢ = √λ |cᵢ|σᵢ`, so shots should be proportional to `|cᵢ|σᵢ`, not `cᵢ²`. Substituting back into the constraint:

`N_opt = (Σᵢ |cᵢ|σᵢ)² / ε²`

With `σᵢ = 1`: `Σ|cᵢ| = 0.988085`, `(Σ|cᵢ|)² = 0.976312`, hence `N_opt = 0.976312/10⁻⁶ ≈ 9.76 × 10⁵` shots, distributed as `Sᵢ = |cᵢ| (Σ|cⱼ|)/ε²`:

| Term | `|cᵢ|` | `Sᵢ` (optimal) |
|---|---|---|
| `Z₁` | 0.397937 | 393,196 |
| `Z₂` | 0.397937 | 393,196 |
| `Z₁Z₂` | 0.011280 | 11,146 |
| `X₁X₂` | 0.180931 | 178,775 |

The ratio `N_opt/N_naive = (Σ|cᵢ|)²/(4 Σcᵢ²) = 0.698` — a `30%` saving, guaranteed `≤ 1` by the Cauchy–Schwarz inequality `(Σ|cᵢ|)² ≤ M Σcᵢ²`, with equality only when all coefficients have equal magnitude.

*Step 3 — refinement once the state is known.* Near the converged ground state (`θ* ≈ 3.365` in the VQE chapter's ansatz) the actual variances are `Var(Z₁) = Var(Z₂) = 0.049`, `Var(Z₁Z₂) = 0`, `Var(X₁X₂) = 0.951`. Feeding these `σᵢ` into `N_opt = (Σ|cᵢ|σᵢ)²/ε²` gives `≈ 1.24 × 10⁵` shots — eight times fewer than the worst-case bound, because the dominant `Z` terms are nearly deterministic in the ground state. Grouping qubit-wise-commuting terms (`Z₁, Z₂, Z₁Z₂` share one measurement basis) is a further lever that `EstimatorV2` applies automatically.

**Key insight**: `1 mHa` precision on even the smallest molecule costs `∼10⁵–10⁶` shots *per energy evaluation*; multiplied by hundreds of optimizer iterations, this is the `1/ε²` law in action. Reading the variance bound as `1/S` and weighting by `|cᵢ|` is the difference between a feasible and an infeasible experiment.

## Summary

- A quantum measurement defines a **probability space** on outcomes via the Born rule; from then on, classical statistics applies verbatim
- **Expectation** is linear; **variance** of a Pauli observable is `1 − ⟨P⟩² ≤ 1`, which fixes shot costs
- **Bayes' theorem** updates classical uncertainty (readout mitigation); it is not the same operation as Born-rule collapse
- Shot counts are **binomial**; the CLT gives Gaussian error bars, and **Hoeffding/Chernoff** give rigorous finite-`N` guarantees with the universal scaling `N ∼ ln(1/δ)/ε²`
- Estimators have **bias** and **variance**; every hardware expectation value is a **Monte Carlo** estimate
- **Shannon entropy**, the **binary entropy** `H₂(p)`, **mutual information**, and **KL divergence** (with Pinsker's inequality) are the classical information measures that the QEC, QKD, and quantum-information chapters generalize
- **Amplitudes are not probabilities**: adding a path can reduce a probability (interference), which no stochastic matrix can reproduce
- **Hypothesis testing** (p-values, z-scores, confidence intervals) is how Bell violations and benchmarking numbers are reported — a p-value is not the probability that the null hypothesis is true

## Exercises

**Exercise 1**: A readout channel has `P(read 1 | true 1) = 0.95` and `P(read 1 | true 0) = 0.02`. You observe the frequency of `1` to be `0.40` over many shots. Estimate the true probability `p` of the state being `|1⟩` before readout, and explain why this is an *inversion* rather than a Bayesian update.

<details><summary>Solution</summary>

By the law of total probability, `P(read 1) = 0.95p + 0.02(1 − p) = 0.02 + 0.93p`. Setting this equal to `0.40` gives `p = (0.40 − 0.02)/0.93 ≈ 0.409`.

This inverts the (known) assignment matrix acting on the (unknown) true distribution — a linear-algebra step on frequencies, not a belief update about a single shot. The Bayesian question "given that *this* shot read `1`, what is the probability it was truly `1`?" uses the same matrix but also needs the prior `p`; with `p = 0.409` it gives `0.95 × 0.409/(0.40) ≈ 0.97`. Matrix inversion can produce slightly negative "probabilities" when frequencies are noisy, which is why practical mitigation uses constrained least squares.

</details>

**Exercise 2**: You want `⟨Z⟩` to within `ε = 0.02` with confidence `99%`. How many shots does Hoeffding's inequality demand? How many does the CLT-based estimate (`Var(⟨Z⟩) ≤ 1/N`, `z_{0.995} = 2.576`) suggest? Why do they differ?

<details><summary>Solution</summary>

Outcomes are `±1`, so `b − a = 2` and Hoeffding gives `N ≥ 2 ln(2/δ)/ε² = 2 ln(200)/0.0004 ≈ 26,492` shots.

The CLT route: the standard error is at most `1/√N`, and a two-sided `99%` interval has half-width `2.576/√N`; setting this to `0.02` gives `N ≥ (2.576/0.02)² ≈ 16,589` shots.

Hoeffding is a rigorous bound valid for every `N` and every distribution on `[−1, 1]`, so it is necessarily conservative; the CLT figure is an asymptotic approximation that also uses the worst-case variance `1`. If `|⟨Z⟩|` is close to `1`, the true variance `1 − ⟨Z⟩²` is small and both numbers are pessimistic. Both scale as `1/ε²`.

</details>

**Exercise 3**: Two qubits are measured in the `Z⊗Z` basis with outcome probabilities `p(00) = p(11) = (1+V)/4`, `p(01) = p(10) = (1−V)/4` (a noisy Bell pair with visibility `V`). Compute `H(A)`, `H(B)`, `H(A,B)`, and `I(A;B)` for `V = 0.8`. What are the limits `V = 1` and `V = 0`?

<details><summary>Solution</summary>

Each marginal is uniform, so `H(A) = H(B) = 1` bit. The joint distribution has two outcomes of probability `(1+V)/4 = 0.45` and two of probability `(1−V)/4 = 0.05`, so

`H(A,B) = −2(0.45 log₂ 0.45) − 2(0.05 log₂ 0.05) = 1.469` bits

(equivalently `H(A,B) = 1 + H₂((1−V)/2) = 1 + H₂(0.1)`). Hence `I(A;B) = 1 + 1 − 1.469 = 0.531` bits — the same number as the BSC with flip probability `0.1`, because given `A`, the bit `B` is `A` flipped with probability `(1−V)/2 = 0.1`.

At `V = 1`: `H(A,B) = 1`, `I = 1` bit — perfect correlation. At `V = 0`: `H(A,B) = 2`, `I = 0` — independent. Note that even at `V = 1` the classical mutual information is only `1` bit; the entanglement of the state is visible in measurements in *other* bases, which is what the CHSH test exploits.

</details>

**Exercise 4**: A CHSH experiment uses `n = 2000` shots per setting and measures correlators `E = (0.68, 0.68, 0.68, −0.68)`. Compute `S`, its standard error, the z-score against the local bound `S = 2`, and the one-sided p-value. Is the conclusion sensitive to using the worst-case variance bound `1/n` instead of `(1 − E²)/n`?

<details><summary>Solution</summary>

`S = 0.68 × 4 = 2.72`. Each correlator has `Var(Eᵢ) = (1 − 0.68²)/2000 = 0.5376/2000 = 2.688 × 10⁻⁴`, so `Var(S) = 4 × 2.688 × 10⁻⁴ = 1.075 × 10⁻³` and `σ_S = 0.0328`.

`z = (2.72 − 2)/0.0328 = 21.96`. The one-sided Gaussian tail at `z = 22` is `≈ 4 × 10⁻¹⁰⁷` — the local-realist null hypothesis is untenable on these data.

With the worst-case bound `Var(Eᵢ) ≤ 1/n`: `σ_S ≤ √(4/2000) = 0.0447` and `z = 16.1`. The conclusion is unchanged; the conservative bound only costs a factor `1.4` in the z-score. (Whether the *physics* conclusion holds depends on loopholes the statistics cannot address.)

</details>

**Exercise 5**: Using the Bernoulli pair `p = 0.5`, `q = 0.6`: (a) verify Pinsker's inequality numerically; (b) how many shots does the midpoint-threshold Hoeffding rule need to distinguish them with error `δ = 10⁻³`; (c) compute the Chernoff information `C(P,Q)` and compare `2^{−N·C}` at that `N` with the Hoeffding guarantee and with the exact error of the midpoint test; why would using the Stein exponent `D(Q‖P)` here be a mistake?

<details><summary>Solution</summary>

(a) `TV = ½(|0.5 − 0.6| + |0.5 − 0.4|) = 0.1`, so Pinsker requires `D(P‖Q) ≥ (2/ln 2)(0.01) = 0.0289` bits. Direct computation: `D(P‖Q) = 0.5 log₂(0.5/0.6) + 0.5 log₂(0.5/0.4) = 0.5(−0.2630) + 0.5(0.3219) = 0.0294` bits ✓ (in nats: `0.0204 ≥ 0.0200`).

(b) `N ≥ 2 ln(1/δ)/(q − p)² = 2 ln(1000)/0.01 ≈ 1,382` shots.

(c) The function `g(λ) = 0.5^λ 0.6^{1−λ} + 0.5^λ 0.4^{1−λ}` is minimized at `λ ≈ 0.50`, giving `C(P,Q) = −log₂ g(0.50) = −log₂(√0.30 + √0.20) = 0.00732` bits (`0.00508` nats). Then `2^{−N·C} = 2^{−1382 × 0.00732} ≈ 2^{−10.1} ≈ 9 × 10⁻⁴` — essentially the same as Hoeffding's `10⁻³`. This is no accident: at `p = 1/2` the Hoeffding exponent `(q−p)²/2 = 0.00500` nats agrees with `C` to leading order in `q − p`, so Hoeffding is already rate-optimal here. The exact error of the midpoint test at `N = 1,382` (summing the binomial tails) is `9.1 × 10⁻⁵` for a false alarm and `8.8 × 10⁻⁵` for a miss — an order of magnitude below both bounds, the difference being only the `1/√N` Gaussian prefactor that neither exponent captures.

Using `D(Q‖P) = 0.6 log₂(0.6/0.5) + 0.4 log₂(0.4/0.5) = 0.0290` bits instead would predict `2^{−1382 × 0.029} ≈ 2^{−40} ≈ 10⁻¹²`, eight orders of magnitude too optimistic. That exponent is Stein's: it governs only the type-II error of a Neyman–Pearson test with `Q` as the null and the type-I error pinned at some fixed `α`, and it is bought by letting the type-I error stay at `α` rather than shrink. For the symmetric problem, where both errors must vanish, the Chernoff information is the correct — and much smaller — exponent.

</details>

## Further Reading

1. **Nielsen & Chuang**, *Quantum Computation and Quantum Information* (Cambridge, 2000), Appendix 1 (probability theory) and §11.1–11.2 (Shannon entropy and its properties) — the minimal classical background the rest of the book assumes
2. **Cover & Thomas**, *Elements of Information Theory* (Wiley, 2nd ed.), Chapters 2 and 11 — entropy, mutual information, KL divergence, Pinsker's inequality, and hypothesis testing: Stein's lemma (§11.8) and the Chernoff information (§11.9)
3. **Mitzenmacher & Upfal**, *Probability and Computing* (Cambridge, 2nd ed.), Chapter 4 — Chernoff and Hoeffding bounds with the sampling applications that underlie shot-count arguments
4. **Wasserman**, *All of Statistics* (Springer), Chapters 6–10 — estimators, bias–variance, confidence intervals, and hypothesis testing in a compact modern treatment
5. **Wecker, Hastings & Troyer**, *Progress towards practical quantum variational algorithms*, Phys. Rev. A 92, 042303 (2015), arXiv:1507.08969 — the coefficient-weighted shot-allocation analysis reproduced in the worked example, and its consequences for VQE cost estimates
6. **Wilde**, *Quantum Information Theory* (Cambridge, 2nd ed., 2017), Chapter 11 — quantum relative entropy and the quantum Pinsker inequality cited in the KL section, the quantum counterpart of the classical measures developed here
