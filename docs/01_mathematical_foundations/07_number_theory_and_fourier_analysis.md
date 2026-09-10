# Number Theory and Fourier Analysis

> **Prerequisites**: 01_linear_algebra.md (unitary matrices, eigenvectors, change of basis), 02_complex_numbers_and_hilbert_spaces.md (roots of unity, `e^{iθ}`), 03_tensor_products_and_multipartite_systems.md (`H^{⊗n}`); comfort with integer arithmetic  
> **Connects to**: `04_quantum_algorithms/03_quantum_fourier_transform.md` and `04_quantum_algorithms/04_quantum_phase_estimation.md` (the QFT is the DFT of this chapter), `04_quantum_algorithms/06_shors_algorithm.md` (every classical step of Shor is proved here), `04_quantum_algorithms/02_deutsch_jozsa_and_bernstein_vazirani.md` (Simon's algorithm and the Hadamard transform), `02_quantum_mechanics/06_wave_mechanics_and_schrodinger.md` (position–momentum duality)

## Overview

Shor's algorithm is famous as a *quantum* algorithm, but most of it is classical mathematics from two subjects that predate quantum mechanics by a century: elementary number theory and Fourier analysis. The quantum computer performs exactly one task — it samples a number whose distribution is peaked at multiples of `Q/r`, where `r` is the multiplicative order of a random base modulo `N`. Everything else — why knowing `r` factors `N`, why a random base works at least half the time, how to recover `r` from a noisy sample, and why the quantum Fourier transform concentrates probability at multiples of `Q/r` in the first place — is a theorem you can prove with pencil and paper.

This chapter supplies those theorems. The number-theory half builds from divisibility and the Euclidean algorithm through modular arithmetic, Euler's theorem, the Chinese remainder theorem, and multiplicative order, culminating in the full reduction of factoring to order-finding and the continued-fraction post-processing step. The Fourier half treats the discrete Fourier transform as a unitary change of basis, proves that it diagonalizes shift operators (the real reason period-finding works), contrasts the transform on `ℤ_N` with the Hadamard transform on `ℤ₂ⁿ`, and connects to the continuous Fourier transform that relates position and momentum. The worked example factors `21` by hand, with every number checked.

## Divisibility, the Euclidean Algorithm, and Bézout's Identity

For integers `a, b` with `b ≠ 0`, `b` **divides** `a` (written `b | a`) if `a = qb` for some integer `q`. The **division algorithm** guarantees unique `q, r` with `a = qb + r` and `0 ≤ r < |b|`. A **prime** is an integer `p > 1` whose only positive divisors are `1` and `p`; the **fundamental theorem of arithmetic** states that every integer `n > 1` factors uniquely (up to order) into primes. Finding that factorization is the problem Shor's algorithm attacks — no classical algorithm is known that does it in time polynomial in `log N`.

The **greatest common divisor** `gcd(a, b)` is the largest integer dividing both. The **Euclidean algorithm** computes it by repeated division, using `gcd(a, b) = gcd(b, a mod b)`:

| Step | `a` | `b` | `q` | `a − qb` |
|---|---|---|---|---|
| 1 | 240 | 46 | 5 | 10 |
| 2 | 46 | 10 | 4 | 6 |
| 3 | 10 | 6 | 1 | 4 |
| 4 | 6 | 4 | 1 | 2 |
| 5 | 4 | 2 | 2 | 0 |

The last nonzero remainder is `gcd(240, 46) = 2`. The number of steps is `O(log min(a,b))` (Lamé's theorem), so gcds of thousand-bit numbers are instantaneous — this is why the final `gcd(a^{r/2} ± 1, N)` step of Shor costs nothing.

**Bézout's identity**: for any `a, b` there exist integers `s, t` with `sa + tb = gcd(a, b)`. The **extended Euclidean algorithm** finds them by back-substituting the table: `2 = 6 − 4 = 6 − (10 − 6) = 2·6 − 10 = 2(46 − 4·10) − 10 = 2·46 − 9·10 = 2·46 − 9(240 − 5·46) = 47·46 − 9·240`. Check: `47 × 46 − 9 × 240 = 2162 − 2160 = 2` ✓. Bézout is the tool that produces modular inverses, and hence RSA keys and the constructive Chinese remainder theorem below.

## Modular Arithmetic and the Group ℤ_N^*

Integers `a, b` are **congruent modulo `N`**, `a ≡ b (mod N)`, if `N | (a − b)`. Congruence respects addition and multiplication, so the residues `ℤ_N = {0, 1, ..., N−1}` form a ring. The **unit group**

`ℤ_N^* = {a ∈ ℤ_N : gcd(a, N) = 1}`

consists of the residues with multiplicative inverses: by Bézout, `gcd(a, N) = 1` gives `sa + tN = 1`, i.e. `sa ≡ 1 (mod N)`, so `a⁻¹ ≡ s`. Conversely if `gcd(a,N) = d > 1` then `a·x ≡ 1` is impossible since `d` would divide `1`. For example, the extended Euclidean algorithm on `(21, 8)` gives `8 × 8 = 64 = 3 × 21 + 1`, so `8⁻¹ ≡ 8 (mod 21)`.

For `N = 21`: `ℤ_21^* = {1, 2, 4, 5, 8, 10, 11, 13, 16, 17, 19, 20}`, a group of order `12` under multiplication mod `21`. Modular exponentiation `a^k mod N` is computed by repeated squaring in `O(log k)` multiplications; the quantum circuit for `|x⟩|y⟩ ↦ |x⟩|y·aˣ mod N⟩` in Shor's algorithm is the reversible version of exactly this routine, and it dominates the gate count.

## Euler's Totient and the Euler–Fermat Theorems

**Euler's totient** `φ(N) = |ℤ_N^*|` counts residues coprime to `N`. For a prime `p`, `φ(p) = p − 1`; for a prime power, `φ(pᵏ) = pᵏ − p^{k−1}`; and `φ` is multiplicative on coprime factors, `φ(mn) = φ(m)φ(n)`. Thus `φ(21) = φ(3)φ(7) = 2 × 6 = 12`, matching the list above, and `φ(pq) = (p−1)(q−1)` for an RSA modulus.

**Euler's theorem**: for `gcd(a, N) = 1`, `a^{φ(N)} ≡ 1 (mod N)`. Proof sketch: multiplication by `a` permutes `ℤ_N^*`, so the product of all units equals the product of `a·u` over all units `u`, which is `a^{φ(N)}` times the same product; cancel. **Fermat's little theorem** is the prime case: `a^{p−1} ≡ 1 (mod p)`. Check: `2¹² = 4096 = 195 × 21 + 1 ≡ 1 (mod 21)`, and `2⁶ = 64 = 9 × 7 + 1 ≡ 1 (mod 7)`.

Euler's theorem is the correctness proof of RSA (`m^{ed} ≡ m` when `ed ≡ 1 (mod φ(N))`), and it guarantees that the order defined below exists and divides `φ(N)`.

## The Chinese Remainder Theorem

**Theorem (CRT)**: if `m₁, ..., m_k` are pairwise coprime, the map `x ↦ (x mod m₁, ..., x mod m_k)` is a ring isomorphism `ℤ_M ≅ ℤ_{m₁} × ... × ℤ_{m_k}` with `M = m₁···m_k`. Concretely, the system `x ≡ aᵢ (mod mᵢ)` has a unique solution modulo `M`, built as `x = Σᵢ aᵢ Mᵢ yᵢ` where `Mᵢ = M/mᵢ` and `yᵢ = Mᵢ⁻¹ mod mᵢ` (a Bézout inverse).

Example: `x ≡ 2 (mod 3)`, `x ≡ 3 (mod 7)`. Here `M₁ = 7`, `7⁻¹ ≡ 1 (mod 3)`; `M₂ = 3`, `3⁻¹ ≡ 5 (mod 7)`. So `x = 2·7·1 + 3·3·5 = 14 + 45 = 59 ≡ 17 (mod 21)`. Check: `17 = 5·3 + 2` and `17 = 2·7 + 3` ✓.

The CRT is why composite moduli have *extra* square roots of `1`. Modulo a prime, `x² ≡ 1` has only `x ≡ ±1`. Modulo `21 = 3 × 7`, `x² ≡ 1` requires `x ≡ ±1 (mod 3)` and `x ≡ ±1 (mod 7)` independently — four sign choices, hence four roots: `1, 8, 13, 20`. (`8² = 64 ≡ 1`, `13² = 169 = 8·21 + 1 ≡ 1`.) The two **nontrivial** roots `8` and `13` are the ones that factor `N`, as the next section shows.

## Multiplicative Order and the Reduction of Factoring to Order-Finding

For `a ∈ ℤ_N^*`, the **multiplicative order** `r = ord_N(a)` is the smallest positive integer with `aʳ ≡ 1 (mod N)`. It exists and divides `φ(N)` by Euler's theorem, and the powers `a, a², a³, ...` repeat with period `r`. For `a = 2`, `N = 21`: `2, 4, 8, 16, 11, 1, 2, 4, ...` so `ord_21(2) = 6`.

**Theorem (order → factor)**. Let `N` be odd and composite, `a ∈ ℤ_N^*` with order `r`. If `r` is even and `a^{r/2} ≢ −1 (mod N)`, then `gcd(a^{r/2} − 1, N)` and `gcd(a^{r/2} + 1, N)` are both nontrivial factors of `N`.

*Proof.* Set `y = a^{r/2}`. Then `y² ≡ 1`, so `N | (y − 1)(y + 1)`. Since `0 < r/2 < r` and `r` is minimal, `y ≢ 1`, so `N ∤ (y − 1)`; by hypothesis `y ≢ −1`, so `N ∤ (y + 1)`. A number that divides a product but neither factor must share a nontrivial factor with each. ∎

`y` is precisely a nontrivial square root of `1`. For `a = 2`, `N = 21`: `r = 6`, `y = 2³ = 8`, `gcd(7, 21) = 7`, `gcd(9, 21) = 3`. Done.

**Failure cases.** The reduction fails when (i) `r` is odd, or (ii) `r` is even but `a^{r/2} ≡ −1`. Both happen: for `N = 21`, `a = 4` and `a = 16` have order `3` (odd); `a = 5`, `17`, `20` have `a^{r/2} ≡ 20 ≡ −1`. Neither failure is detectable without knowing `r`, so the algorithm simply picks a fresh random `a` and repeats.

**Why a random base succeeds with probability ≥ 1/2.** Let `N = p₁^{e₁} ··· p_k^{e_k}` with `k ≥ 2` distinct odd primes. By the CRT, choosing `a` uniformly from `ℤ_N^*` is the same as choosing independent uniform components `aᵢ ∈ ℤ_{pᵢ^{eᵢ}}^*`. Each of those groups is cyclic, so write the order of `aᵢ` as `2^{dᵢ}·(odd)`. Both failure modes force *all* the `dᵢ` to be equal: odd `r` means every `dᵢ = 0`, and `a^{r/2} ≡ −1 (mod N)` means `a^{r/2} ≡ −1` modulo every prime power, which forces every `dᵢ` to equal the maximal `d`. In a cyclic group of order `2ᶜ·(odd)` with `c ≥ 1`, exactly half the elements have the maximal value `dᵢ = c` and half have `dᵢ < c`, so no single value of `dᵢ` has probability above `1/2`. Fixing `d₁`, each of the other `k − 1` independent components matches it with probability at most `1/2`, so the chance that all `k` values coincide is at most `1/2^{k−1} ≤ 1/2`. For `N = 21`, a direct count gives `6` good bases out of the `11` non-identity units (`2, 8, 10, 11, 13, 19`), a success rate of `0.545`. Repeating with `t` independent bases fails with probability at most `2^{−t}` — the Chernoff-style amplification of `06_probability_and_statistics.md`.

Two trivial cases are excluded up front classically: even `N` (divide by `2`) and prime powers `N = pᵉ` (detectable by taking integer `e`-th roots). If a chosen `a` happens to share a factor with `N`, `gcd(a, N)` already factors it.

## Continued Fractions and the Convergents Theorem

The quantum subroutine does not output `r`. It outputs an integer `j` from a `Q = 2ᵗ`-element register whose distribution is peaked at `j ≈ sQ/r` for a uniformly random `s ∈ {0, ..., r−1}`. Recovering the rational `s/r` from the approximation `φ = j/Q` is the job of **continued fractions**.

Every rational `x` has a finite expansion `x = [a₀; a₁, a₂, ..., a_n] = a₀ + 1/(a₁ + 1/(a₂ + ...))`, computed by repeatedly splitting off the integer part and inverting the remainder — literally the Euclidean algorithm on numerator and denominator. Truncating after `k` terms gives the **convergents** `pₖ/qₖ`, generated by

`pₖ = aₖp_{k−1} + p_{k−2}`,  `qₖ = aₖq_{k−1} + q_{k−2}`,  with `(p_{−1}, q_{−1}) = (1, 0)`, `(p_{−2}, q_{−2}) = (0, 1)`

Convergents are the best rational approximations to `x` for their denominator size, and the key fact is a converse:

**Theorem (Legendre)**: if `|x − s/r| < 1/(2r²)` with `gcd(s, r) = 1`, then `s/r` is one of the convergents of `x`. (The inequality is strict; with `≤` the boundary case can fail — `x = 1/2`, `s/r = 1/1` has `|x − s/r| = 1/2 = 1/(2·1²)` yet `1/1` is not a convergent of `1/2 = [0; 2]`.)

Shor's algorithm chooses `Q ≥ N²` precisely so that this applies: with probability at least `4/π² ≈ 0.405` (in the worked example, `79%`) the measured `j` is the integer nearest `sQ/r` and so satisfies `|j/Q − s/r| ≤ 1/(2Q) ≤ 1/(2N²) < 1/(2r²)` since `r < N`; other outcomes make the continued-fraction step fail, and the run is repeated. The denominator `r` is then read off the last convergent with denominator less than `N`.

**A concrete sample.** With `N = 21`, `Q = 512`, suppose the measurement returns `j = 171`. Then `171/512 = [0; 2, 1, 170]` (`512 = 2·171 + 170`, `171 = 1·170 + 1`, `170 = 170·1`), with convergents `0/1, 1/2, 1/3, 171/512`. The last denominator below `21` is `3`, so the candidate is `r' = 3`. But `2³ = 8 ≢ 1 (mod 21)` — the sample had `s = 2`, sharing a factor with `r = 6`, so the reduced fraction `1/3` lost that factor. The remedy is to test small multiples: `2⁶ = 64 ≡ 1 (mod 21)` ✓, so `r = 2r' = 6`. In general `r'` is `r/gcd(s, r)`, and `s` coprime to `r` (probability `φ(r)/r = Ω(1/log log r)`) gives `r` directly.

## Primality Testing

Deciding whether `N` is prime is much easier than factoring it, and Shor's algorithm assumes `N` has already been certified composite. Fermat's theorem gives a quick filter: if `a^{N−1} ≢ 1 (mod N)` for some `a`, `N` is composite. The filter has blind spots (Carmichael numbers such as `561` pass it for every coprime `a`), which the **Miller–Rabin test** closes by also watching for nontrivial square roots of `1`: write `N − 1 = 2ᵘ·d` with `d` odd, compute `aᵈ`, and square it `u` times; if the sequence neither starts at `1` nor passes through `−1` before reaching `1`, `N` is composite. For `N = 21`, `a = 2`: `20 = 2²·5`, `2⁵ ≡ 11`, `11² ≡ 16`, `16² ≡ 4` — never `1` or `20`, so `21` is composite. For `561`, `a = 2` gives the sequence `263, 166, 67, 1`: it reaches `1` from `67 ≢ ±1`, exposing a nontrivial square root of `1` and thus compositeness. Each random base catches a composite with probability at least `3/4`, so `t` rounds give error `≤ 4^{−t}`; deterministic polynomial-time primality testing also exists (AKS, 2002) but is slower in practice.

## The Discrete Fourier Transform as a Unitary Change of Basis

Let `ω = e^{2πi/N}` be a primitive `N`-th root of unity. The **discrete Fourier transform** on `ℂᴺ` is the matrix

`F_{kj} = ω^{jk}/√N`,  i.e.  `x̂ₖ = (1/√N) Σⱼ ω^{jk} xⱼ`

Its rows are orthonormal because `Σⱼ ω^{j(k−k')} = N δ_{kk'}` (a geometric series that vanishes unless `k = k'`). Hence `F†F = I`: **the DFT is unitary**, and the vectors `|χₖ⟩ = F†|k⟩ = (1/√N)Σⱼ ω^{−jk}|j⟩` form an orthonormal basis of `ℂᴺ` — the **Fourier basis**. The QFT of `04_quantum_algorithms/03_quantum_fourier_transform.md` is exactly this `F` acting on the amplitude vector of an `n`-qubit register with `N = 2ⁿ`.

Three consequences follow from unitarity and the group structure of `ℤ_N`:

- **Parseval's identity**: `Σₖ |x̂ₖ|² = Σⱼ |xⱼ|²`. Probabilities are conserved by the QFT — it is a gate, not a measurement.
- **Convolution theorem**: for the circular convolution `(x ∗ y)ₙ = Σₘ xₘ y_{n−m mod N}`, `(x ∗ y)^ = √N · x̂ ⊙ ŷ` (pointwise product). Convolution in one basis is multiplication in the other.
- **Inverse**: `F⁻¹ = F†`, obtained by replacing `ω` with `ω⁻¹`; the inverse QFT is the same circuit with negated phases.

## The DFT Diagonalizes Shifts: Why the QFT Reveals Periods

Define the **cyclic shift** `S|j⟩ = |j + 1 mod N⟩`. It is a permutation matrix, hence unitary, and it commutes with `F` up to a diagonal:

`F S F† = diag(1, ω, ω², ..., ω^{N−1})`

*Proof*: the vector `|χₖ⟩ = F†|k⟩ = (1/√N)Σⱼ ω^{−jk}|j⟩` satisfies `S|χₖ⟩ = (1/√N)Σⱼ ω^{−jk}|j+1⟩ = (1/√N)Σⱼ ω^{−(j−1)k}|j⟩ = ωᵏ|χₖ⟩`. So the Fourier basis is the eigenbasis of *every* shift-invariant operator, and translation by `m` becomes multiplication by `ω^{km}`. Note that `|χₖ⟩` has components `χₖ(j)*/√N = ω^{−jk}/√N` — the *conjugate* of the character `χₖ(j) = ω^{jk}` defined in the next section; the character vector itself, `F|k⟩ = (1/√N)Σⱼ ω^{jk}|j⟩`, is also an eigenvector of `S`, with eigenvalue `ω^{−k}`, which is the labelling used in `05_representation_theory.md`. (Numerically, for `N = 6` the diagonal is `(1, ½+0.866i, −½+0.866i, −1, −½−0.866i, ½−0.866i)`.)

Now take a state that is **periodic with period `r`** (with `r | N` for simplicity): `|ψ⟩ = √(r/N) Σₘ |x₀ + mr⟩`. It is invariant under `Sʳ`, so its Fourier transform is supported only where `ω^{kr} = 1`, i.e. on `k ∈ {0, N/r, 2N/r, ...}` — multiples of `N/r`, each with probability `1/r`. Example: the period-`3` comb on `ℤ₁₂` (ones at `0, 3, 6, 9`) transforms to a comb at `k = 0, 4, 8` with equal magnitudes, and Parseval holds (`Σ|x|² = Σ|x̂|² = 4`). The offset `x₀` appears only as a phase `ω^{kx₀}` and is invisible to measurement — which is exactly what Shor needs, since the offset (the random value of the second register) is unknown. When `r ∤ N` the peaks broaden slightly around `sN/r`, and the continued-fraction step absorbs the error; the worked example quantifies this.

## Fourier Analysis on ℤ_N versus ℤ₂ⁿ

The DFT is a special case of Fourier analysis on a finite abelian group `G`: the **characters** `χ: G → U(1)` (homomorphisms into the unit circle) form an orthonormal basis of functions on `G`, and the Fourier transform expands a function in that basis. For `G = ℤ_N` the characters are `χₖ(j) = ω^{jk}`; for `G = ℤ₂ⁿ` (bit strings under XOR) they are `χ_y(x) = (−1)^{x·y}` with `x·y = Σ xᵢyᵢ mod 2`. The transform matrix for `ℤ₂ⁿ` is `(1/√2ⁿ)(−1)^{x·y}`, which is exactly `H^{⊗n}` — the **Hadamard transform** is the Fourier transform of `ℤ₂ⁿ`.

The choice between them is dictated by the *group in which the hidden period lives*:

| | Simon's problem | Shor's order-finding |
|---|---|---|
| Group | `ℤ₂ⁿ` | `ℤ_N` (approximated by `ℤ_Q`) |
| Promise | `f(x ⊕ s) = f(x)` | `f(x + r) = f(x)` |
| Transform | `H^{⊗n}` | QFT `F_Q` |
| Post-processing | linear algebra over GF(2) | continued fractions |

In Simon's algorithm, the state after evaluating the oracle and measuring its output is `(|x₀⟩ + |x₀ ⊕ s⟩)/√2`; the Hadamard transform maps it to a superposition over exactly those `y` with `y·s = 0`. For `n = 3`, `s = 101`, `x₀ = 010`, the output support is `{000, 010, 101, 111}` — each has `y·s = 0` — with amplitudes `±½`. Collecting `n − 1` independent such `y` determines `s` by GF(2) elimination (`04_quantum_algorithms/02_deutsch_jozsa_and_bernstein_vazirani.md`). Order-finding is periodic under *addition*, not XOR, so the same trick requires the characters of `ℤ_N`. This is why Simon's algorithm was the blueprint for Shor's and why the QFT, not another layer of Hadamards, is the engine of factoring.

## Sampling and Aliasing

A sinusoid of frequency `f` sampled at rate `f_s` is indistinguishable from one at `f + kf_s` for any integer `k`; frequencies above the Nyquist limit `f_s/2` fold back onto lower ones. This **aliasing** is a Fourier statement about `ℤ_N`: the DFT index `k` and `k + N` are the same character. In Shor's algorithm the register size `Q` is the sampling rate; taking `Q ≥ N²` guarantees the peak at `sQ/r` is resolved to better than half a unit and that distinct fractions `s/r`, `s'/r'` with denominators below `N` (which differ by at least `1/N²`) never alias onto the same `j`.

## The Continuous Fourier Transform and Position–Momentum Duality

Letting `N → ∞` with a shrinking lattice spacing turns sums into integrals. With the symmetric convention,

`ψ̃(k) = (1/√(2π)) ∫ ψ(x) e^{−ikx} dx`,  `ψ(x) = (1/√(2π)) ∫ ψ̃(k) e^{ikx} dk`

This is the physics convention of `02_quantum_mechanics/06_wave_mechanics_and_schrodinger.md` (forward kernel `e^{−ikx}`); it is the complex conjugate of the `ω^{+jk}` convention used for the DFT/QFT above, which is why a translation picks up `e^{−ika}` here but `ω^{+k}` in the discrete case.

Unitarity survives as Plancherel's theorem `∫|ψ|² dx = ∫|ψ̃|² dk`, the convolution theorem survives verbatim, and the shift-diagonalization becomes: translation by `a` multiplies `ψ̃(k)` by `e^{−ika}`, so the generator of translations is `−i d/dx` — the momentum operator up to `ℏ`. This is the mathematical content of the plane-wave overlap `⟨x|p⟩ = e^{ipx/ℏ}/√(2πℏ)` in `02_quantum_mechanics/06_wave_mechanics_and_schrodinger.md`: the position and momentum wavefunctions are Fourier transforms of each other. A Gaussian of width `σₓ` transforms to a Gaussian of width `σₖ = 1/(2σₓ)`, so `σₓσₖ = ½` exactly (numerically, `σₓ = 1.3` gives `σₖ = 0.3846`); with `p = ℏk` this is the Heisenberg relation `σₓσ_p = ℏ/2`, saturated by Gaussians. Sharp localization in one basis forces spread in the other — the same trade-off that makes a period-`r` comb transform to a comb of spacing `N/r`.

## Key Formulas

**Bézout**: `sa + tb = gcd(a, b)`; inverse: `a⁻¹ ≡ s (mod N)` when `gcd(a, N) = 1`

**Euler / Fermat**: `a^{φ(N)} ≡ 1 (mod N)`, `φ(pq) = (p−1)(q−1)`; `a^{p−1} ≡ 1 (mod p)`

**CRT**: `x = Σᵢ aᵢ Mᵢ (Mᵢ⁻¹ mod mᵢ) mod M`, `Mᵢ = M/mᵢ`

**Order → factor**: `r` even, `a^{r/2} ≢ −1`  ⟹  `gcd(a^{r/2} ± 1, N)` nontrivial; success probability `≥ 1 − 1/2^{k−1}`

**Convergents**: `pₖ = aₖp_{k−1} + p_{k−2}`, `qₖ = aₖq_{k−1} + q_{k−2}`; Legendre: `|x − s/r| < 1/(2r²)` ⟹ `s/r` is a convergent

**DFT**: `F_{kj} = ω^{jk}/√N`, `F†F = I`, `Σ|x̂ₖ|² = Σ|xⱼ|²`, `(x ∗ y)^ = √N x̂ ⊙ ŷ`

**Shift diagonalization**: `F S F† = diag(ωᵏ)`; period `r` ⟹ support on `k ∈ (N/r)ℤ`

**Characters**: `ℤ_N`: `ω^{jk}`; `ℤ₂ⁿ`: `(−1)^{x·y}` (Hadamard transform)

**Gaussian uncertainty**: `σₓσₖ = ½`

## Worked Example

**Problem**: Factor `N = 21` by order-finding with base `a = 2`, using a `t = 9`-qubit phase register (`Q = 2⁹ = 512 ≥ N² = 441`). Simulate the quantum step, post-process a typical measurement with continued fractions, and extract the factors.

**Solution**:

*Step 1 — classical preconditions.* `21` is odd, not a prime power (`√21 ≈ 4.58`, `∛21 ≈ 2.76`, `⁴√21 ≈ 2.14`; `e ≤ log₂ 21 < 5`, none an integer), and `gcd(2, 21) = 1`. Proceed.

*Step 2 — the order (which the quantum computer does not know).* `2¹ = 2, 2² = 4, 2³ = 8, 2⁴ = 16, 2⁵ = 32 ≡ 11, 2⁶ = 64 ≡ 1 (mod 21)`. So `r = 6`; it divides `φ(21) = 12` as Euler's theorem requires.

*Step 3 — the measurement distribution.* After the modular-exponentiation oracle and a measurement of the second register, the first register holds a uniform superposition over `m` values `x₀ + 6k`, where `m = 86` when the second-register outcome fixes `x₀ ∈ {0, 1}` (since `512 = 6·85 + 2`) and `m = 85` for the other four offsets. Taking `m = 86`, applying `F₅₁₂` and measuring gives `j` with probability `P(j) = |Σ_{k=0}^{85} e^{2πi·6jk/512}|² / (512 × 86)`. Since `6 ∤ 512`, the peaks are not exact delta functions: the six values nearest `s·512/6 = 85.33 s`, namely `j ∈ {0, 85, 171, 256, 341, 427}`, carry probabilities `0.168, 0.114, 0.114, 0.168, 0.114, 0.114` — `79.3%` in total, rising to `93.3%` if the neighbours `j ± 1` are included (for the `m = 85` offsets the figures are `0.166, 0.114, …`, `78.8%` and `93.1%` — a shift of less than `0.005`). The register size `Q ≥ N²` is what keeps the leakage this small.

*Step 4 — continued fractions on `j = 427`.* The phase is `φ = 427/512 = 0.833984`. Run the Euclidean algorithm on `(512, 427)`:

`512 = 1·427 + 85`, `427 = 5·85 + 2`, `85 = 42·2 + 1`, `2 = 2·1`

so `427/512 = [0; 1, 5, 42, 2]`. Build convergents with the recurrence:

| `k` | `aₖ` | `pₖ` | `qₖ` | `pₖ/qₖ` |
|---|---|---|---|---|
| 0 | 0 | 0 | 1 | 0 |
| 1 | 1 | 1 | 1 | 1 |
| 2 | 5 | 5 | 6 | 0.833333 |
| 3 | 42 | 211 | 253 | 0.833992 |
| 4 | 2 | 427 | 512 | 0.833984 |

The last convergent with denominator `< 21` is `5/6`, so `s = 5`, `r = 6`. Legendre's condition is satisfied with room to spare: `|427/512 − 5/6| = 0.000651 ≤ 1/(2Q) = 0.000977 < 1/(2r²) = 0.0139`.

*Step 5 — verify the order and factor.* `2⁶ ≡ 1 (mod 21)` ✓, and `r = 6` is even. Compute `y = 2^{r/2} = 2³ = 8`; `8 ≢ −1 ≡ 20`, so the theorem applies:

`gcd(8 − 1, 21) = gcd(7, 21) = 7`,  `gcd(8 + 1, 21) = gcd(9, 21) = 3`,  and `21 = 3 × 7` ✓

*Step 6 — the other outcomes.* `j = 85` gives `[0; 6, 42, 2]` with convergent `1/6` → `r = 6` directly. `j = 171` and `j = 341` give `1/3` and `2/3` → candidate `3`, rejected because `2³ ≢ 1`; doubling fixes it. `j = 256` gives `1/2` → candidate `2`, rejected; the multiples `4, 6` are tried and `6` succeeds. `j = 0` gives `s = 0` and no information. Two of six peaks yield `r` immediately, three more yield it after testing multiples up to `3r'`, and one is a rerun — consistent with the `Ω(1/log log N)` per-shot success guarantee and, in practice, one or two runs.

**Key insight**: the quantum computer's only contribution was the sample `j = 427`. Turning that into `r = 6` used continued fractions; turning `r = 6` into `3 × 7` used a two-line gcd argument. The exponential speedup lives in producing the sample; the correctness lives in this chapter.

## Summary

- The **Euclidean algorithm** computes gcds in `O(log N)` steps and, extended, yields **Bézout coefficients** and hence modular inverses
- `ℤ_N^*` is the group of units; its order is **Euler's totient** `φ(N)`, and **Euler's theorem** `a^{φ(N)} ≡ 1` guarantees every unit has a finite **multiplicative order**
- The **Chinese remainder theorem** splits `ℤ_N` into prime-power components; composite `N` therefore has **nontrivial square roots of 1**, and `a^{r/2}` is one whenever `r` is even and `a^{r/2} ≢ −1`
- **Factoring reduces to order-finding**: `gcd(a^{r/2} ± 1, N)` are factors, a random base works with probability `≥ 1/2`, and failures (odd `r`, or `a^{r/2} ≡ −1`) are handled by retrying
- **Continued fractions** recover `s/r` from `j/Q` whenever `Q ≥ N²` (Legendre's theorem); a shared factor between `s` and `r` is repaired by testing small multiples
- The **DFT** is a unitary change of basis; it satisfies **Parseval** and the **convolution theorem** and **diagonalizes shifts**, so a period-`r` state transforms to peaks at multiples of `N/r` — the mechanism of the QFT
- **Characters** of `ℤ_N` are `ω^{jk}`; those of `ℤ₂ⁿ` are `(−1)^{x·y}`, making `H^{⊗n}` the Fourier transform Simon's algorithm needs and `F_Q` the one Shor's needs
- The **continuous Fourier transform** relates position and momentum wavefunctions; Gaussians saturate `σₓσₖ = ½`

## Exercises

**Exercise 1**: An RSA key uses `N = 3233 = 53 × 61` and public exponent `e = 17`. Compute `φ(N)` and use the extended Euclidean algorithm to find the private exponent `d = e⁻¹ mod φ(N)`. Explain in one sentence why knowing `r = ord_N(a)` for a random `a` would let an attacker recover `d` without this computation.

<details><summary>Solution</summary>

`φ(3233) = 52 × 60 = 3120`. Euclid on `(3120, 17)`: `3120 = 183·17 + 9`, `17 = 1·9 + 8`, `9 = 1·8 + 1`, so `gcd = 1`. Back-substitute: `1 = 9 − 8 = 9 − (17 − 9) = 2·9 − 17 = 2(3120 − 183·17) − 17 = 2·3120 − 367·17`. Hence `17 × (−367) ≡ 1 (mod 3120)` and `d = −367 + 3120 = 2753`. Check: `17 × 2753 = 46801 = 15 × 3120 + 1` ✓.

Knowing an order gives factors of `N` via the reduction theorem, hence `p`, `q`, and `φ(N)` — after which `d` is this same two-line calculation. That is the entire threat Shor poses to RSA.

</details>

**Exercise 2**: For `N = 21`, compute the order of `a = 5`, `a = 13`, and `a = 20`, decide for each whether the order-finding reduction succeeds, and give the factors it produces when it does.

<details><summary>Solution</summary>

- `a = 5`: `5, 25 ≡ 4, 20, 100 ≡ 16, 80 ≡ 17, 85 ≡ 1`, so `r = 6`. Even, but `5³ ≡ 20 ≡ −1 (mod 21)` — **failure** (the `−1` case; `gcd(19, 21) = 1` and `gcd(21, 21) = 21` are both trivial).
- `a = 13`: `13² = 169 = 8·21 + 1`, so `r = 2`. `13¹ = 13 ≢ −1`, so **success**: `gcd(12, 21) = 3`, `gcd(14, 21) = 7`.
- `a = 20 ≡ −1`: `r = 2` and `20¹ ≡ −1` — **failure**. The base `−1` always fails, for any `N`.

Together with the list of good bases in the text (`2, 8, 10, 11, 13, 19`) this confirms `6` successes among the `11` bases `a ≠ 1`, i.e. a success rate of `≈ 0.55 ≥ 1/2`, as the theorem promises for `k = 2` prime factors.

</details>

**Exercise 3**: Solve `x ≡ 3 (mod 5)`, `x ≡ 4 (mod 7)`, `x ≡ 2 (mod 9)` using the constructive CRT formula, and verify the result.

<details><summary>Solution</summary>

`M = 5 × 7 × 9 = 315`; `M₁ = 63`, `M₂ = 45`, `M₃ = 35`. Inverses: `63 ≡ 3 (mod 5)` and `3 × 2 = 6 ≡ 1`, so `y₁ = 2`; `45 ≡ 3 (mod 7)` and `3 × 5 = 15 ≡ 1`, so `y₂ = 5`; `35 ≡ 8 (mod 9)` and `8 × 8 = 64 ≡ 1`, so `y₃ = 8`.

`x = 3·63·2 + 4·45·5 + 2·35·8 = 378 + 900 + 560 = 1838 ≡ 1838 − 5·315 = 263 (mod 315)`

Check: `263 = 52·5 + 3` ✓, `263 = 37·7 + 4` ✓, `263 = 29·9 + 2` ✓.

</details>

**Exercise 4**: Let `x ∈ ℂ¹⁶` have `xⱼ = ½` for `j ∈ {1, 5, 9, 13}` and `0` otherwise (a period-`4` comb with offset `1`). Without computing all sixteen sums, determine which Fourier coefficients `x̂ₖ` are nonzero and their squared magnitudes, and confirm Parseval's identity. What changes if the offset is `3` instead of `1`?

<details><summary>Solution</summary>

`x` is invariant under the shift `S⁴`, so `x̂` is supported where `ω^{4k} = 1`, i.e. `k ∈ {0, 4, 8, 12}`. On those indices, `x̂ₖ = (1/√16) Σ_{m=0}^{3} ½ ω^{k(1+4m)} = (1/4)(½)(4)ω^{k} = ½ ω^{k}`, since `ω^{4km} = 1`. Thus `|x̂ₖ|² = ¼` for `k = 0, 4, 8, 12`, and `Σₖ|x̂ₖ|² = 4 × ¼ = 1 = Σⱼ|xⱼ|² = 4 × ¼` ✓.

Changing the offset to `3` multiplies each nonzero coefficient by `ω^{2k}` — a phase — leaving the squared magnitudes, and hence the measurement statistics, unchanged. This offset-independence is why the unknown value in Shor's second register does not matter.

</details>

**Exercise 5**: In Simon's algorithm with `n = 3` and hidden string `s = 110`, the register after the oracle and a measurement of the output is `(|x₀⟩ + |x₀ ⊕ s⟩)/√2`. Apply `H^{⊗3}` and list the possible measurement outcomes `y`. Then explain why applying the `ℤ₈` QFT `F₈` instead would *not* produce a clean set of outcomes.

<details><summary>Solution</summary>

`H^{⊗3}(|x₀⟩ + |x₀ ⊕ s⟩)/√2 = (1/4) Σ_y [(−1)^{x₀·y} + (−1)^{(x₀⊕s)·y}] |y⟩ = (1/4) Σ_y (−1)^{x₀·y}[1 + (−1)^{s·y}] |y⟩`. The bracket is `2` when `s·y = 0` and `0` otherwise, so the outcomes are exactly the `y` with `y₁ ⊕ y₂ = 0` (bits `1` and `2` equal, bit `3` free): `{000, 001, 110, 111}`, each with probability `¼`. Any two linearly independent samples — e.g. `001` and `110` — determine `s` as the unique nonzero solution of `y·s = 0` for both, which is `110`.

The QFT over `ℤ₈` uses characters `ω^{jk}` of *addition mod 8*, but `x₀` and `x₀ ⊕ s` are not related by a fixed additive shift (for `x₀ = 000` the pair is `{0, 6}`, an additive gap of `6`; for `x₀ = 010` it is `{2, 4}`, a gap of `2`). The pair is not an orbit of any additive translation, so `F₈` produces `x₀`-dependent interference patterns with no fixed support set. The group in the promise (`ℤ₂³` under XOR) dictates the transform (`H^{⊗3}`).

</details>

## Further Reading

1. **Nielsen & Chuang**, *Quantum Computation and Quantum Information*, Appendix 4 (number theory: Euclid, modular arithmetic, CRT, continued fractions, the reduction of factoring to order-finding) and §5.1–5.3 — the standard reference for every step used here
2. **Hardy & Wright**, *An Introduction to the Theory of Numbers* (Oxford, 6th ed.), Chapters V–VI (congruences, Fermat and Euler) and X (continued fractions, including Legendre's convergent theorem)
3. **Shor**, *Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer*, SIAM J. Comput. 26, 1484 (1997), arXiv:quant-ph/9508027 — the original paper; §5 contains the continued-fraction analysis and the success-probability bound
4. **Stein & Shakarchi**, *Fourier Analysis: An Introduction* (Princeton, 2003), Chapters 5, 7 and 8 — the Fourier transform on `ℝ` (Gaussians, the uncertainty principle), finite Fourier analysis on `ℤ_N` and on general finite abelian groups via characters, and the application to Dirichlet's theorem
5. **Childs**, *Lecture Notes on Quantum Algorithms* (University of Maryland, free online), Chapters 4–6 — Fourier transforms on finite abelian groups, the hidden subgroup problem, and why Simon and Shor are the same algorithm on different groups
