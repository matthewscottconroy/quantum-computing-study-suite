# Shor's Algorithm

> **Prerequisites**: 04_quantum_algorithms/03_quantum_fourier_transform.md, 04_quantum_phase_estimation.md, 02_deutsch_jozsa_and_bernstein_vazirani.md (Simon's algorithm as the precursor)  
> **Connects to**: Quantum circuit complexity (BQP ≠ BPP evidence), post-quantum cryptography (RSA vulnerability), quantum hardware requirements (large fault-tolerant circuits)

## Overview

Shor's algorithm (1994) factors an `n`-bit integer `N` in polynomial quantum time — specifically `O(n³)` gate operations. The best classical algorithm (the General Number Field Sieve) requires sub-exponential time `exp(O(n^{1/3} (log n)^{2/3}))` — exponentially slower than Shor's. Breaking 2048-bit RSA encryption (the industry standard) would take a classical computer millions of years but could in principle be done by a sufficiently large fault-tolerant quantum computer in hours.

Shor's algorithm is the most important quantum algorithm for two reasons. Practically: it threatens the most widely deployed public-key cryptographic system (RSA) and has driven the multi-billion-dollar investment in quantum hardware. Theoretically: it is the strongest evidence that BQP ≠ BPP — that quantum computers are genuinely more powerful than classical probabilistic algorithms for important problems.

The algorithm is a combination of classical number theory and a single quantum subroutine. The quantum part is **order-finding** (finding the multiplicative order of a number mod `N`), implemented via quantum phase estimation. The classical parts — which are entirely rigorous and well-understood — reduce factoring to order-finding and extract the factors from the order. The quantum speedup lives entirely in the order-finding step.

Understanding Shor's algorithm requires number theory (multiplicative order, GCD), quantum phase estimation (QPE), the quantum Fourier transform, and the continued fractions algorithm. Each piece is important, and together they form one of the most elegant algorithms ever discovered.

## Factoring Reduces to Order-Finding

### The Number-Theoretic Reduction

**Integer factoring**: Given composite `N`, find nontrivial factors.

**Multiplicative order**: For `a` coprime to `N` (`gcd(a,N) = 1`), the **multiplicative order** of `a` modulo `N` is the smallest positive integer `r` such that:

$$a^r \equiv 1 \pmod{N}$$

This is also called the period of the sequence `a, a², a³, ...` mod `N` (since `a^{r+k} ≡ a^k mod N` for all `k`).

**From order to factors** (the key theorem):

**Theorem**: Given `a` coprime to `N` with multiplicative order `r`, if:
1. `r` is even, AND
2. `a^{r/2} ≢ -1 \pmod{N}` (equivalently, `a^{r/2} + 1 ≢ 0 \pmod{N}`)

then at least one of `gcd(a^{r/2} - 1, N)` or `gcd(a^{r/2} + 1, N)` is a nontrivial factor of `N`.

**Proof**: Since `a^r ≡ 1 (mod N)`, we have `a^r - 1 ≡ 0 (mod N)`, i.e., `N | a^r - 1`. With `r` even:

$$a^r - 1 = (a^{r/2} - 1)(a^{r/2} + 1)$$

So `N | (a^{r/2}-1)(a^{r/2}+1)`. Now `N ∤ (a^{r/2}-1)`: since `r` is the *smallest* positive exponent with `a^r ≡ 1 (mod N)` and `0 < r/2 < r`, we have `a^{r/2} ≢ 1 (mod N)`. And `N ∤ (a^{r/2}+1)` is exactly condition 2. Then `N` must share a nontrivial common factor with both `(a^{r/2}-1)` and `(a^{r/2}+1)`.

Since `gcd(a^{r/2}-1, N)` divides `N` but is not 1 and not `N` (from the conditions), it is a nontrivial factor. ✓

**Success probability**: For a random `a` coprime to `N`:
- The joint event "`r` is even **and** `a^{r/2} ≢ -1 (mod N)`" occurs with probability `≥ 1 - 1/2^{k-1}`, where `k` is the number of distinct odd prime factors of `N`
- For `N = pq` (RSA modulus, product of two large primes): probability `≥ 1 - 1/2 = 1/2`

So roughly half of all choices of `a` give a useful order, and we can try multiple `a` values until one works.

### The Complete Reduction Algorithm

**Shor's factoring algorithm** (classical + quantum):

**Classical preprocessing**:
1. If `N` is even: return factor 2
2. If `N = p^k` for some prime `p`: return `p` (detectable classically in `O(n²)` time via primality testing)
3. Choose a random `a ∈ {2,...,N-1}`:
   - Compute `g = gcd(a, N)` using Euclidean algorithm: `O(n³)` classical ops
   - If `g > 1`: lucky! `g` is a nontrivial factor. Done.
   - If `g = 1`: proceed to quantum order-finding

**Quantum order-finding** (the quantum core):
4. Find the order `r` of `a` mod `N` using QPE — the quantum subroutine

**Classical postprocessing**:
5. If `r` is odd or `a^{r/2} ≡ -1 (mod N)`: go to step 3 (choose new `a`)
6. Compute `p = gcd(a^{r/2} - 1, N)` and `q = gcd(a^{r/2} + 1, N)`
7. Return the nontrivial factor(s) found

Expected number of `a` choices until success: `O(1)` (constant).

## The Quantum Order-Finding Algorithm

### The Unitary for Modular Exponentiation

Define the unitary `U_a` acting on computational basis states `|y⟩` (for `0 ≤ y ≤ N-1`):

$$U_a|y\rangle = |ay \bmod N\rangle, \quad \text{for } y < N$$

(For `y ≥ N`, some convention like `U_a|y⟩ = |y⟩` is used for the extra basis states, but they do not affect the algorithm.)

This is a well-defined unitary because multiplication by `a` (mod `N`) is a bijection on `{1,...,N-1}` when `gcd(a,N) = 1`. It maps `|y⟩ → |ay mod N⟩` for all `y`.

**Eigenvalues of `U_a`**: The eigenstates of `U_a` are the "discrete Fourier modes" over the multiplicative group:

$$|u_s\rangle = \frac{1}{\sqrt{r}}\sum_{j=0}^{r-1}e^{-2\pi i sj/r}|a^j \bmod N\rangle, \quad s = 0, 1, \ldots, r-1$$

These satisfy:
$$U_a|u_s\rangle = e^{2\pi i s/r}|u_s\rangle$$

So the eigenvalues are `e^{2πis/r}` for `s = 0,...,r-1`. The corresponding phases are `φ_s = s/r`.

**Proof**: 
$$U_a|u_s\rangle = \frac{1}{\sqrt{r}}\sum_{j=0}^{r-1}e^{-2\pi isj/r}|a^{j+1} \bmod N\rangle = \frac{e^{2\pi is/r}}{\sqrt{r}}\sum_{j=0}^{r-1}e^{-2\pi is(j+1)/r}|a^{j+1} \bmod N\rangle = e^{2\pi is/r}|u_s\rangle$$

where the last step uses the periodicity of the sum.

### QPE on the Eigenstate Superposition

We cannot efficiently prepare a specific `|u_s⟩` without knowing `r` (which is what we are trying to find!). However, we can use a neat trick: prepare `|1⟩` and observe that:

$$|1\rangle = \frac{1}{\sqrt{r}}\sum_{s=0}^{r-1}|u_s\rangle$$

(This is because `|u_s⟩` is a superposition of `|a^j mod N⟩` for `j = 0,...,r-1`, and `|1⟩ = |a^0 mod N⟩` appears in each `|u_s⟩` with amplitude `e^{0}/(√r) = 1/√r`.)

Now apply **QPE** to the superposition:

$$\text{QPE on }(|0\rangle^n|1\rangle): \quad \sum_{s=0}^{r-1}\frac{1}{\sqrt{r}}\text{QPE}(|u_s\rangle) = \sum_{s=0}^{r-1}\frac{1}{\sqrt{r}}|\tilde{s/r}\rangle|u_s\rangle$$

where `|s̃/r⟩` is the best `n`-bit approximation to `s/r`. Measuring the ancilla register gives some `s̃/r` for a random `s ∈ {0,...,r-1}`.

### Extracting r via Continued Fractions

The measurement gives a value `j/2ⁿ ≈ s/r` for some random `s`. From this approximation, we recover `r` using the **continued fractions algorithm**:

**Key theorem**: If `|φ - s/r| ≤ 1/2^{n+1}` and `r < N ≤ 2ⁿ/2`, then the continued fraction expansion of `φ = j/2ⁿ` includes `s/r` as one of its convergents (rational approximations with denominator `≤ N`).

The continued fraction algorithm runs in `O(n²)` classical time and recovers the rational `s/r` in lowest terms. The resulting denominator `r'` is a candidate for the order (if `gcd(s, r) > 1`, it is a proper divisor of `r`). We verify: `a^{r'} ≡ 1 (mod N)`? If yes, `r'` is the order. If not, try small multiples `2r', 3r', ...` until `a^{k·r'} ≡ 1 (mod N)`, or rerun the quantum step to sample a new `s`.

### Success Probability

For `n ≥ 2log₂(N) + 1` ancilla qubits:
- With probability `Ω(1/log log N)` over the choice of `s`, the continued fractions algorithm recovers `r` exactly from `s/r`
- After `O(log log N)` trials, we get `r` with high probability
- Total oracle (controlled-`U_a`) calls: `O(n · log log N) = O(n log log N)`

The standard analysis uses the **Chinese Remainder Theorem** and the distribution of `gcd(s, r)` to bound the success probability.

## Circuit Implementation

### Modular Exponentiation

The core quantum circuit implements the controlled-`U_a^{2^k}` gates. Rather than applying `U_a` repeatedly `2^k` times (which would be exponential in `k`), we use **repeated squaring**:

$$U_a^{2^k} = \underbrace{U_a \cdot U_a \cdots U_a}_{2^k \text{ times}} = U_{a^{2^k} \bmod N}$$

The operator `U_{b}` (multiplication by `b = a^{2^k} mod N`) can be precomputed classically and then implemented as a quantum circuit. The quantum circuit for multiplication by a fixed `b` mod `N` uses `O(n²)` gates (via addition circuits, multiplication circuits, and modular reduction).

For controlled-`U_b` (with the QPE ancilla as control), the circuit uses `O(n²)` gates per ancilla qubit, and we have `n` ancilla qubits, giving `O(n³)` gates total.

### Total Gate Count

| Component | Gate count |
|-----------|-----------|
| `H^{⊗n}` (ancilla initialization) | `n` |
| Controlled-`U_a^{2^k}` for k=0,...,n-1 | `O(n³)` |
| Inverse QFT | `O(n²)` |
| **Total** | **`O(n³)`** |

With improved modular arithmetic (Karatsuba multiplication, FFT-based): `O(n² log n log log n)`.

With best known quantum arithmetic: `O(n² log n)` gates or `O(n³/log n)` Toffoli gates.

**T-count**: Each Toffoli gate uses 7 T gates. Total T-count for Shor's algorithm: `O(n³)` (or `O(n²log n)` with optimization).

### Qubit Count

- `n` ancilla qubits for QPE (to estimate `n`-bit phase)
- `n` qubits for the system register (to hold values `0,...,N-1`)
- `O(n)` ancilla for modular exponentiation circuits

Total: `O(n)` logical qubits. For 2048-bit RSA: `~6,000` logical qubits (`≈ 3n` in the Gidney-Ekerå layout).

## Classical vs. Quantum Complexity

### The Classical Record

The best classical algorithm for factoring `n`-bit integers (where `n = log₂ N`):

**General Number Field Sieve (GNFS)**:
$$T_\text{GNFS} = \exp\left(O\left(n^{1/3}(\log n)^{2/3}\right)\right) = L[1/3, c]$$

where `L[α, c] = exp((c+o(1))(log N)^α (log log N)^{1-α})`. This is **sub-exponential** in `n` (it grows faster than polynomial but slower than exponential in the bit length).

For `N = 2^{2048}` (2048-bit RSA): evaluating the exponent `(64/9)^{1/3}(\ln N)^{1/3}(\ln\ln N)^{2/3} ≈ 81` gives `T_GNFS ≈ e^{81} ≈ 10^{35}` operations (`≈ 2^{117}`, matching the standard ~112-120-bit security estimates for RSA-2048). At `10^{15}` operations/second (exaflop): `~10^{20}` seconds — orders of magnitude longer than the age of the universe.

### Shor's Record

**Shor's algorithm**: `O(n³) = O((log N)³) = O(n³)` gate operations. For `N = 2^{2048}`: `O(2048³) ≈ 10^{10}` quantum gates.

This is exponentially faster than the GNFS. The quantum speedup is not just polynomial — it changes the complexity class from sub-exponential to polynomial.

| | Classical (GNFS) | Quantum (Shor) |
|-|-----------------|----------------|
| Complexity | `exp(O(n^{1/3}))` | `O(n³)` |
| 2048-bit RSA | ~10^35 ops | ~10^10 gates |
| Time (quantum HW) | millions of years | ~8 hours (est.) |

### Physical Resource Requirements

From Gidney & Ekerå (2021), the resource requirements for breaking 2048-bit RSA:

- **Logical qubits**: ~6,200 (`≈ 3n` for `n = 2048`)
- **Physical qubits** (with surface code, distance ~20): ~20,000,000 (20 million)
- **Logical gates**: ~3 × 10^9
- **Runtime** at 1μs per gate cycle: ~8 hours

Current largest quantum computers (2024-2025): ~1000-2000 high-quality superconducting qubits. To run Shor for RSA-2048: need ~10,000× more qubits. Target timeline: 2030s, contingent on engineering progress.

## The Hidden Subgroup Perspective

Shor's algorithm is a special case of the **Hidden Subgroup Problem (HSP)**:

**HSP**: Given a function `f: G → S` from a group `G` to a set `S` that is constant on cosets of a hidden subgroup `H ≤ G` and distinct on different cosets, find `H`.

For Shor's algorithm: `G = ℤ/2ⁿ` (integers mod `2ⁿ`), the "period function" `f(x) = a^x mod N` has a hidden subgroup `H = rℤ/2ⁿ = {0, r, 2r, ...} mod 2ⁿ` (multiples of `r`). Finding `H` = finding `r`.

**The quantum algorithm for abelian HSP**:
1. Prepare superposition of `G`
2. Evaluate `f` via oracle
3. Apply QFT over `G`
4. Measure to get a coset label
5. Repeat and use linear algebra to identify `H`

This works for all **abelian** groups and recovers Simon's algorithm (G = (ℤ/2)ⁿ) and Shor (G = ℤ/N) as special cases. The **non-abelian** case (e.g., graph isomorphism via the symmetric group) is a major open problem in quantum computing.

## Key Formulas

**Order-finding to factoring reduction**:
$$\gcd(a^{r/2} \pm 1, N) \text{ gives factors when } r \text{ even and } a^{r/2} \not\equiv -1 \pmod{N}$$

**Eigenvalues of U_a**:
$$U_a|u_s\rangle = e^{2\pi is/r}|u_s\rangle, \quad |u_s\rangle = \frac{1}{\sqrt{r}}\sum_{j=0}^{r-1}e^{-2\pi isj/r}|a^j \bmod N\rangle$$

**Superposition of eigenstates**:
$$|1\rangle = \frac{1}{\sqrt{r}}\sum_{s=0}^{r-1}|u_s\rangle$$

**Quantum circuit gate count**:
$$O(n^3) \text{ gates for } n = \log_2 N \text{ (basic)}$$
$$O(n^2 \log n) \text{ gates (optimized)}$$

**Classical speedup**:
$$\text{GNFS: } \exp(O(n^{1/3})) \text{ vs. Shor: } O(n^3) = \text{polynomial}$$

## Worked Example

**Problem**: Shor's algorithm applied to `N = 15`.

(a) Factor 15 using order-finding with `a = 7`.  
(b) Verify the eigenstate `|u_1⟩` for `U_7` acting on `{|1⟩, |7⟩, |4⟩, |13⟩}`.  
(c) What is the expected output of the QPE step (using sufficient precision)?

**Solution**:

**(a) Order-finding for `a=7, N=15`**:

Compute powers of 7 mod 15:
- `7¹ mod 15 = 7`
- `7² mod 15 = 49 mod 15 = 4`
- `7³ mod 15 = 7·4 mod 15 = 28 mod 15 = 13`
- `7⁴ mod 15 = 7·13 mod 15 = 91 mod 15 = 1`

Order `r = 4` (since `7⁴ ≡ 1 mod 15`).

Classical check:
1. `r = 4` is even ✓
2. `a^{r/2} = 7² mod 15 = 4`. Is `4 ≡ -1 ≡ 14 (mod 15)`? No ✓

Compute factors:
- `gcd(a^{r/2} - 1, N) = gcd(4-1, 15) = gcd(3, 15) = 3` ← factor!
- `gcd(a^{r/2} + 1, N) = gcd(4+1, 15) = gcd(5, 15) = 5` ← factor!

**Factors: 3 and 5 (15 = 3 × 5)** ✓

**(b) Eigenstate `|u_1⟩`**:

The orbit of `U_7` starting at `|1⟩` cycles through `|1⟩ → |7⟩ → |4⟩ → |13⟩ → |1⟩`. With `r = 4, s = 1`:

$$|u_1\rangle = \frac{1}{2}\sum_{j=0}^3 e^{-2\pi i\cdot 1\cdot j/4}|7^j \bmod 15\rangle = \frac{1}{2}(|1\rangle + e^{-i\pi/2}|7\rangle + e^{-i\pi}|4\rangle + e^{-3i\pi/2}|13\rangle)$$

$$= \frac{1}{2}(|1\rangle - i|7\rangle - |4\rangle + i|13\rangle)$$

Verify `U_7|u_1⟩ = e^{2πi·1/4}|u_1⟩ = i|u_1⟩`. Since `U_7` maps `|1⟩→|7⟩, |7⟩→|4⟩, |4⟩→|13⟩, |13⟩→|1⟩`, applying it term by term:

$$U_7|u_1\rangle = \frac{1}{2}(|7\rangle - i|4\rangle - |13\rangle + i|1\rangle) = \frac{1}{2}(i|1\rangle + |7\rangle - i|4\rangle - |13\rangle)$$

Factoring out `i` from each amplitude (`i = i·1`, `1 = i·(-i)`, `-i = i·(-1)`, `-1 = i·i`):

$$U_7|u_1\rangle = i \cdot \frac{1}{2}(|1\rangle - i|7\rangle - |4\rangle + i|13\rangle) = i\,|u_1\rangle \checkmark$$

So `U_7|u_1⟩ = i|u_1⟩ = e^{iπ/2}|u_1⟩` — eigenvalue `i = e^{2πi·1/4}`, confirming phase `φ₁ = s/r = 1/4` ✓.

**(c) QPE output**:

The input `|1⟩ = (1/2)(|u_0⟩ + |u_1⟩ + |u_2⟩ + |u_3⟩)` is an equal mixture of all four eigenstates.

QPE with sufficient precision (`n ≥ 4` ancilla bits for `r = 4 ≤ 15`) gives phase `φ_s = s/4` for random `s ∈ {0,1,2,3}`:

- `s=0`: phase `0/4 = 0`, QPE output `|0000⟩` (i.e., `0`)
- `s=1`: phase `1/4`, QPE output `|0100⟩` (i.e., `4` in 4-bit representation, since `1/4 × 2⁴ = 4`)
- `s=2`: phase `2/4 = 1/2`, QPE output `|1000⟩` (i.e., `8`)
- `s=3`: phase `3/4`, QPE output `|1100⟩` (i.e., `12`)

Each outcome occurs with probability `1/4`.

From each measurement, applying continued fractions:
- Output `4/16 = 1/4`: `r` divides `4`; candidates: `1, 2, 4`. Verify `7^4 ≡ 1 (mod 15)` ✓
- Output `8/16 = 1/2`: candidate denominator `r' = 2`, but `7² = 49 ≡ 4 ≢ 1 (mod 15)`. Trying the multiple `2r' = 4`: `7⁴ ≡ 1` ✓, so `r = 4`.
- Output `12/16 = 3/4`: continued fraction gives `3/4`; denominator 4 → `r = 4` ✓
- Output `0`: uninformative (`s=0`); rerun the quantum order-finding step

Thus from outcomes 1, 2, or 3 (probability 3/4), we can recover `r = 4` and factor `N = 15`.

## Summary

- Shor's algorithm factors an `n`-bit integer in `O(n³)` quantum gates — polynomial quantum time vs. sub-exponential classical time
- **Reduction**: factoring reduces to order-finding; order `r` of `a` mod `N` gives factors via `gcd(a^{r/2}±1, N)` (when `r` even and `a^{r/2} ≢ -1`)
- **Quantum core**: QPE on the unitary `U_a|y⟩ = |ay mod N⟩` estimates eigenphases `s/r`; input state `|1⟩ = (1/√r)Σ|u_s⟩` ensures all `r` eigenphases are sampled
- **Continued fractions**: from `j/2ⁿ ≈ s/r`, recover `r` classically in `O(n²)` time
- **Circuit cost**: `O(n³)` gates (dominated by modular exponentiation); optimized versions achieve `O(n² log n)`; ~6,000 logical qubits and 20M physical qubits for 2048-bit RSA
- **Classical hardness**: best classical algorithm (GNFS) requires `exp(O(n^{1/3}))` time — exponentially slower; Shor's algorithm is the strongest evidence for `BQP ≠ BPP`
- **HSP framework**: Shor's algorithm is a special case of the abelian hidden subgroup problem; Simon's algorithm (period over (ℤ/2)ⁿ) is the direct precursor
- **Post-quantum implication**: RSA, Diffie-Hellman, and elliptic curve cryptography are broken by Shor; post-quantum standards (NIST 2024: ML-KEM, ML-DSA, SLH-DSA) use lattice-based and hash-based cryptography

## Exercises

**Exercise 1**: Run the classical part of Shor's algorithm by hand for `N = 15` with `a = 2`: compute the order `r`, check the two conditions, and extract the factors.

<details><summary>Solution</summary>

Powers of 2 mod 15: `2, 4, 8, 16 ≡ 1` — so `r = 4`.

Conditions: `r = 4` is even ✓; `a^{r/2} = 2² = 4 ≢ -1 ≡ 14 (mod 15)` ✓.

Factors: `gcd(4 - 1, 15) = gcd(3, 15) = 3` and `gcd(4 + 1, 15) = gcd(5, 15) = 5`. Indeed `15 = 3 × 5` ✓.

</details>

**Exercise 2**: For `N = 15`, classify the bases `a = 4` and `a = 14`: for each, find the order and determine whether the reduction succeeds or the algorithm must pick a new `a`.

<details><summary>Solution</summary>

`a = 4`: `4² = 16 ≡ 1 (mod 15)`, so `r = 2` (even ✓). `a^{r/2} = 4 ≢ -1 (mod 15)` ✓. Factors: `gcd(3, 15) = 3`, `gcd(5, 15) = 5` — success.

`a = 14`: `14² = 196 ≡ 1 (mod 15)`, so `r = 2` (even ✓). But `a^{r/2} = 14 ≡ -1 (mod 15)` — condition 2 **fails**. Indeed `gcd(14-1, 15) = gcd(13,15) = 1` and `gcd(14+1, 15) = gcd(15,15) = 15`, both trivial. The algorithm must choose a new `a`. (`a = 14 ≡ -1` always has order 2 with `a^{r/2} ≡ -1`; it is the canonical "unlucky" choice.)

</details>

**Exercise 3**: Order-finding for `N = 21`, `a = 2` uses `t = 11` ancilla qubits (`2^t = 2048`; `N = 21` is a 5-bit number, and `t = 2·5 + 1 = 11`). The QPE measurement returns `j = 341`. Recover the order via continued fractions and factor 21.

<details><summary>Solution</summary>

The measured phase is `j/2048 = 341/2048 ≈ 0.16650`. Continued fraction expansion: `341/2048 = 1/(6 + 2/341)`, so the convergents are `0, 1/6, 170/1021, 341/2048`. The convergent with denominator `< 21` is `1/6`, giving candidate `r = 6`.

Verify: powers of 2 mod 21: `2, 4, 8, 16, 32 ≡ 11, 22 ≡ 1` — indeed `r = 6` ✓ (and `341 ≈ 2048·(1/6) = 341.3`, consistent with `s = 1`).

Reduction: `r = 6` even ✓; `a^{r/2} = 2³ = 8 ≢ -1 ≡ 20 (mod 21)` ✓. Factors: `gcd(8-1, 21) = gcd(7,21) = 7` and `gcd(8+1, 21) = gcd(9,21) = 3`. So `21 = 3 × 7` ✓.

</details>

**Exercise 4**: In the worked example (`N = 15`, `a = 7`, `r = 4`), suppose the QPE step is repeated twice and returns outcomes `4` and `8` (out of 16). Show what each outcome alone tells you about `r`, and how combining them pins down `r = 4`.

<details><summary>Solution</summary>

Outcome `4`: phase `4/16 = 1/4`, in lowest terms `s/r = 1/4` → candidate `r' = 4`. Check: `7⁴ = 2401 = 160·15 + 1 ≡ 1 (mod 15)` ✓ — this outcome alone already gives `r = 4`.

Outcome `8`: phase `8/16 = 1/2` → candidate `r' = 2` (here `gcd(s, r) = 2`, so the fraction `2/4` collapsed to `1/2` and the denominator is only a divisor of `r`). Check: `7² = 49 ≡ 4 ≢ 1 (mod 15)` — fails, so `r' = 2` is not the order, only a divisor of it.

Combining: the true `r` must be a common multiple of the observed denominators — `lcm(4, 2) = 4` — and `7⁴ ≡ 1` confirms `r = 4`. Taking the `lcm` of denominators from a few runs is the standard way to handle outcomes with `gcd(s, r) > 1`.

</details>

**Exercise 5**: Estimate how many bits of RSA key Shor's algorithm "breaks per gate" compared to GNFS: for `n = 2048`, compare `n³` with `exp(1.9·n^{1/3}(ln n)^{2/3})`-type growth qualitatively — if hardware improves so that both classical and quantum machines get 1000× faster, which side benefits more, and why?

<details><summary>Solution</summary>

Shor: `n³ = 2048³ ≈ 8.6 × 10⁹` gates — polynomial. GNFS: sub-exponential, of order `10^{30}`+ operations for 2048-bit moduli (the precise constant depends on the formula's `o(1)` term; empirically RSA-250, 829 bits, took ~2700 core-years).

A 1000× speedup shifts a *polynomial* algorithm's reach dramatically: for Shor, `1000× ≈ 10³` more gates means handling `n → 10·n` (since `(10n)³ = 1000·n³`) — ten times longer keys. For GNFS, because cost grows like `exp(c·n^{1/3})`, a 1000× speedup only adds a modest additive increment to the manageable key length (roughly, `n^{1/3}` grows by `ln(1000)/c`, a few percent at these sizes). Polynomial scaling means hardware progress translates almost directly into capability; sub-exponential scaling means it barely moves the needle. This asymmetry is why key-length increases cannot defend RSA against a quantum adversary, while they work fine against classical ones.

</details>

## Further Reading

1. **Shor**, "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer" (SIAM Journal on Computing, 1997; arXiv:quant-ph/9508027) — the original paper; beautifully written; covers both factoring and discrete log
2. **Ekert & Jozsa**, "Quantum Computation and Shor's Factoring Algorithm" (Reviews of Modern Physics, 1996) — accessible review connecting the algorithm to physics; excellent pedagogical exposition
3. **Nielsen & Chuang**, §5.3–5.4 — complete treatment of order-finding, QPE, and the continued fractions step; Appendix 4 covers number theory background
4. **Gidney & Ekerå**, "How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits" (Quantum, 2021) — definitive resource estimate for practical Shor implementation with surface codes and magic state distillation
5. **Childs & van Dam**, "Quantum algorithms for algebraic problems" (Reviews of Modern Physics, 2010) — places Shor in the unifying framework of the hidden subgroup problem; surveys generalizations and open problems
