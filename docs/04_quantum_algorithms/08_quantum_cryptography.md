# Quantum Cryptography

> **Prerequisites**: 02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md (measurement bases), 03_quantum_gates_and_circuits/01_single_qubit_gates.md, 04_quantum_algorithms/06_shors_algorithm.md (what quantum computers break)  
> **Connects to**: Quantum information theory (Holevo bound, monogamy of entanglement — 08/02), no-cloning theorem, Bell inequalities and device independence, post-quantum cryptography standards

## Overview

Quantum cryptography inverts the usual relationship between quantum computing and security. Shor's algorithm (Chapter 4.6) shows that quantum *computers* destroy the public-key cryptography that secures the internet. Quantum *communication*, by contrast, enables something classical physics cannot: **key distribution whose security rests on physical law rather than computational hardness**. An eavesdropper on a quantum channel cannot avoid disturbing the states she inspects, and that disturbance is detectable.

The root of this guarantee is the **no-cloning theorem**: an unknown quantum state cannot be copied. A classical eavesdropper can passively duplicate every bit on a wire and remain invisible; a quantum eavesdropper who wants to learn about non-orthogonal signal states must measure them, and measurement in the wrong basis irreversibly damages the state. Security becomes a *conservation law*: information gained by the eavesdropper is paid for in errors visible to the legitimate parties. Alice and Bob quantify the damage (the quantum bit error rate, QBER), bound Eve's knowledge from it, and distill a shorter key about which Eve provably knows essentially nothing.

This chapter develops BB84 — the first and still dominant quantum key distribution (QKD) protocol — in full: the protocol table, the exact analysis of the intercept-resend attack (the origin of the famous 25% error rate), and the classical post-processing pipeline (sifting, error correction, privacy amplification). We then sketch the entanglement-based protocols E91 and BBM92 and the idea of device independence, survey the engineering realities (weak laser pulses, decoy states, distance limits), and position QKD against post-quantum cryptography — the two very different answers to the threat Shor created.

## No-Cloning as the Security Root

The no-cloning theorem (proved in Chapter 08/02) states that no unitary satisfies `U|ψ⟩|0⟩ = |ψ⟩|ψ⟩` for all `|ψ⟩`. Two consequences do all the cryptographic work:

1. **No passive wiretap**: Eve cannot copy the qubit in flight and measure the copy at leisure. Whatever she learns must come from an interaction with the *single* transmitted system.
2. **Information-disturbance trade-off**: for states drawn from a set containing non-orthogonal pairs (like BB84's `{|0⟩, |1⟩, |+⟩, |−⟩}`), any interaction that extracts information necessarily perturbs at least some of the states. Non-orthogonal states cannot be distinguished perfectly even in principle (`|⟨0|+⟩|² = 1/2`), and an interaction that leaves *all* signal states untouched can be shown to extract zero information.

This is why BB84 deliberately uses **two mutually unbiased bases**. If Alice used only orthogonal states `{|0⟩, |1⟩}`, Eve could measure in that basis, learn everything, resend perfect copies, and cause no errors. Non-orthogonality is not a nuisance — it is the entire mechanism.

## BB84

### The Protocol

Alice encodes random bits in one of two bases, chosen at random per bit:

- **Z basis (`+`)**: bit 0 → `|0⟩`, bit 1 → `|1⟩`
- **X basis (`×`)**: bit 0 → `|+⟩ = (|0⟩+|1⟩)/√2`, bit 1 → `|−⟩ = (|0⟩-|1⟩)/√2`

Bob measures each arriving qubit in a basis he picks at random (Z or X, 50/50). When his basis matches Alice's, his outcome reproduces her bit perfectly (in the ideal channel); when it differs, his outcome is a fair coin.

A run looks like this:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Alice's bit | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 1 |
| Alice's basis | + | + | × | + | × | × | + | × |
| State sent | `\|0⟩` | `\|1⟩` | `\|−⟩` | `\|0⟩` | `\|−⟩` | `\|+⟩` | `\|0⟩` | `\|−⟩` |
| Bob's basis | + | × | × | + | + | × | × | × |
| Bob's result | 0 | 0/1 | 1 | 0 | 0/1 | 0 | 0/1 | 1 |
| Bases match? | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Sifted key | 0 | — | 1 | 0 | — | 0 | — | 1 |

**Steps**:

1. **Quantum transmission**: Alice sends `n` qubits prepared as above.
2. **Sifting**: over an authenticated public classical channel, Alice and Bob announce their *basis* choices (never bit values) and discard all positions where bases differ. About half survive: the **sifted key** (`≈ n/2` bits).
3. **Parameter estimation**: they sacrifice a random subset of sifted bits, compare them publicly, and estimate the QBER `Q`. If `Q` exceeds the security threshold (≈ 11% for one-way post-processing), they abort.
4. **Error correction (information reconciliation)**: interactive parity exchanges (e.g., Cascade, or LDPC syndromes) make their strings identical, leaking a known number of additional bits to Eve — at least `n_sift·H₂(Q)` bits by Shannon's bound, where `H₂` is the binary entropy.
5. **Privacy amplification**: they apply a random universal hash function, compressing the reconciled key by enough to erase Eve's partial knowledge (from both her channel attack and the error-correction leakage). The asymptotic secure key rate per sifted bit is:

$$r = 1 - H_2(Q) - H_2(Q) = 1 - 2H_2(Q)$$

(Shor-Preskill, 2000): one `H₂(Q)` paid to correct errors, one to amplify away Eve's information. `r > 0` requires `Q < 0.1100...` — the 11% threshold.

### The Intercept-Resend Attack: the 25% QBER

The simplest attack: Eve measures every qubit in a randomly chosen BB84 basis and resends the state corresponding to her outcome. Analyze one *sifted* position (Alice's and Bob's bases match, say both Z; the X case is symmetric):

- **Eve guesses the basis right** (probability `1/2`): she measures Z, gets Alice's bit exactly, resends the identical state. Bob's outcome is correct. Error probability: `0`. Eve's knowledge of this bit: complete.
- **Eve guesses wrong** (probability `1/2`): she measures X on `|0⟩` or `|1⟩`, obtaining `|+⟩` or `|−⟩` at random, and resends *that*. Bob measures Z on `|±⟩`: outcome is a fair coin. Error probability: `1/2`. Eve's X-outcome is statistically independent of Alice's Z bit: she learns nothing.

$$\text{QBER} = \frac{1}{2}\cdot 0 + \frac{1}{2}\cdot\frac{1}{2} = 25\%$$

Eve's information: after sifting, the bases are public, so Eve knows which half of her measurements used the right basis. She holds `1` full bit on those and `0` bits on the rest:

$$I(A{:}E) = \frac{1}{2}\cdot 1 + \frac{1}{2}\cdot 0 = 0.5 \text{ bits per sifted bit}$$

A 25% QBER is far above the 11% threshold — full intercept-resend is caught essentially immediately (each compared bit independently reveals the attack with probability 1/4). Eve can instead attack only a fraction `η` of the pulses, scaling both her information (`η/2` bits) and the QBER (`η/4`) down linearly — which is precisely why Alice and Bob compute their key length as a function of the *measured* `Q`.

### Why Eve Cannot Do Better Silently

Intercept-resend is not the optimal attack (optimal collective attacks attain the `1 - 2H₂(Q)` bound), but no attack is free: any channel that transmits both bases faithfully transmits *all* states faithfully (the four BB84 states span the qubit space, and a channel fixing two non-orthogonal pure states is the identity on their span), leaving Eve's probe unentangled and informationless. Monogamy of entanglement gives the complementary entanglement-based view: the more Bob's outcomes correlate with Alice's in two mutually unbiased bases, the less room remains for correlations with any third party.

## Entanglement-Based Protocols

### E91 (Ekert, 1991)

A source (even an untrusted one) distributes pairs in the singlet state `|Ψ⁻⟩ = (|01⟩ - |10⟩)/√2`. Alice and Bob measure in randomly chosen analyzer directions. Perfectly anti-correlated basis pairs supply key bits; the remaining combinations are used to evaluate the **CHSH quantity** `S`. An undisturbed singlet gives `S = 2√2`; any eavesdropping (which necessarily entangles a probe and degrades the singlet) pulls `S` toward the classical bound `|S| ≤ 2`. Security is certified by the observed Bell violation itself.

This is the seed of **device-independent QKD**: if the observed correlations violate CHSH, the key is secure *even if the measurement devices are black boxes built by the adversary* — the violation certifies intrinsic randomness and bounds Eve's information with no assumptions about the internal physics. The price is severe: a loophole-free Bell test with very high detection efficiency, so demonstrated key rates are tiny (first experimental DI-QKD demonstrations appeared in 2022).

### BBM92 (Bennett-Brassard-Mermin, 1992)

The pragmatic middle ground: distribute entangled pairs, but have Alice and Bob simply measure in randomly chosen Z/X bases, BB84-style, and sift. Outcomes in matched bases are perfectly (anti-)correlated, and the analysis reduces exactly to BB84 — as if Alice had "sent" the state Bob's qubit collapses to. BBM92 removes the trusted-source assumption of BB84 (a malicious source shows up as errors) without requiring a Bell test, and is the protocol behind entanglement-based satellite links (Micius, 2020: 1120 km).

## QKD in Practice

**Weak coherent pulses and the PNS attack**: Real systems rarely use true single photons; they use attenuated laser pulses (mean photon number `μ ≈ 0.1-0.5`) which sometimes contain 2+ photons. Eve can then mount the **photon-number-splitting (PNS)** attack: block single-photon pulses, split one photon off multi-photon pulses, store it, and measure it *after* basis announcement — gaining full information on those bits with zero disturbance.

**Decoy states** (Hwang 2003; Lo, Ma, Chen 2005): Alice randomly intersperses pulses of different intensities (e.g., signal `μ`, decoy `ν < μ`, vacuum). Eve cannot tell signal from decoy, so any photon-number-dependent blocking distorts the yield statistics across intensities. Comparing detection rates lets Alice and Bob tightly lower-bound the single-photon contribution, restoring security at practical rates. Decoy-state BB84 is the workhorse of deployed QKD.

**Distance limits**: Optical fiber attenuates by `≈ 0.2 dB/km`, and no-cloning forbids amplifying a quantum signal. Key rate therefore falls off linearly with channel transmittance `η_ch` — and the repeaterless (PLOB) bound `≈ 1.44·η_ch` bits/pulse caps *any* point-to-point protocol. Practical consequences: metro-scale fiber links run at Mbit/s; records reach ~500-1000 km in fiber using twin-field QKD (which scales as `√η_ch`); continental distances need satellites or, eventually, quantum repeaters. A further practical caveat: implementation side channels (detector blinding, timing) have enabled real "quantum hacking," answered by measurement-device-independent (MDI) QKD, which removes all detector-side assumptions.

## QKD vs. Post-Quantum Cryptography

Shor's algorithm breaks the *public-key* primitives (RSA, Diffie-Hellman, elliptic curves) whose job is key establishment and signatures; Grover's algorithm merely halves the effective strength of symmetric ciphers (AES-256 stays safe). Two disjoint responses:

| | Post-quantum crypto (PQC) | QKD |
|---|---|---|
| What it is | New classical math problems (lattices: ML-KEM/ML-DSA; hashes: SLH-DSA — NIST 2024) | Physics-based key distribution |
| Security basis | Computational (conjectured hardness, incl. vs. quantum computers) | Information-theoretic (given the models/devices) |
| Deployment | Software update, works over existing networks, any distance | Dedicated optics, range-limited, point-to-point |
| Threat coverage | Also does signatures/authentication | Keys only; still *requires* an authenticated classical channel |
| Residual risk | Algorithmic breakthrough against the new problems | Implementation side channels, trusted relays |

They are complements, not competitors: QKD itself needs authentication (today, done with PQC or pre-shared keys), while "harvest now, decrypt later" adversaries recording today's RSA-protected traffic are the reason both migrations are urgent.

## Key Formulas

**BB84 signal states**: `{|0⟩, |1⟩}` (Z basis), `{|+⟩, |−⟩}` (X basis); `|⟨0|+⟩|² = 1/2`

**Intercept-resend (random BB84 basis)**:
$$\text{QBER} = \frac{1}{4}, \qquad I(A{:}E) = \frac{1}{2} \text{ bit/sifted bit}, \qquad P(\text{Eve guesses bit}) = \frac{3}{4}$$

**Breidbart-basis intercept-resend**:
$$\text{QBER} = \frac{1}{4}, \qquad P(\text{Eve guesses bit}) = \cos^2(\pi/8) \approx 0.854, \qquad I(A{:}E) = 1 - H_2(\cos^2(\pi/8)) \approx 0.399$$

**Detection**: comparing `k` sifted bits, `P(\text{Eve undetected}) = (1 - Q_{attack})^k = (3/4)^k` for full intercept-resend

**Asymptotic BB84 key rate (one-way post-processing)**:
$$r = 1 - 2H_2(Q) > 0 \iff Q < 11.0\%$$

**CHSH certificate (E91)**: `S_quantum = 2√2` vs. `S_classical ≤ 2`

## Worked Example

**Problem**: Compute the exact QBER and Eve's information for intercept-resend when Eve measures every qubit in (a) the **computational (Z) basis**, versus (b) the **Breidbart basis** `{|η₀⟩, |η₁⟩}` with

$$|\eta_0\rangle = \cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle, \qquad |\eta_1\rangle = -\sin(\pi/8)|0\rangle + \cos(\pi/8)|1\rangle$$

(the basis lying exactly halfway between Z and X). Compare the two strategies.

**Solution**:

**(a) Fixed Z-basis measurement.** Consider sifted positions only (Alice's and Bob's bases agree).

*Alice used Z* (half the sifted bits): Eve's Z measurement yields Alice's bit with certainty; she resends the same state; Bob receives it unchanged. Errors: 0. Eve's knowledge: 1 bit.

*Alice used X* (other half): Eve measures Z on `|±⟩`: outcome 0 or 1 with probability 1/2, uncorrelated with Alice's bit — Eve learns nothing. She resends `|0⟩` or `|1⟩`; Bob measures X and gets `|⟨+|0⟩|² = 1/2` — a fair coin. Errors: 1/2.

$$\text{QBER}_Z = \frac{1}{2}(0) + \frac{1}{2}\left(\frac{1}{2}\right) = \frac{1}{4}, \qquad I(A{:}E) = \frac{1}{2}(1) + \frac{1}{2}(0) = 0.5 \text{ bits}$$

Eve's per-bit guessing probability: `1` on Z-positions, `1/2` on X-positions — average `3/4` (identical to the random-basis attack of the main text; after sifting Eve knows *which* bits she holds perfectly).

**(b) Breidbart basis.** The Breidbart states make angle `π/8` (22.5°) with both bases' states. The relevant overlaps, identical for every BB84 signal state `|ψ⟩` by symmetry:

$$|\langle\eta_e|\psi\rangle|^2 \in \{\cos^2(\pi/8), \sin^2(\pi/8)\} = \{0.8536, 0.1464\}$$

*Eve's guess*: whichever outcome she gets, the more-likely-compatible bit value is correct with probability `cos²(π/8) ≈ 0.854` — for **every** bit, regardless of Alice's basis. This is the maximum achievable per-bit guessing probability for any fixed intercept basis.

*Bob's error*: Alice sends `|ψ⟩`, Eve resends `|η_e⟩` with probability `|⟨η_e|ψ⟩|²`, and Bob (in Alice's basis, post-sifting) gets the correct bit with probability `|⟨ψ|η_e⟩|²`. Summing over Eve's outcomes:

$$P(\text{Bob correct}) = \sum_e |\langle\eta_e|\psi\rangle|^4 = \cos^4(\pi/8) + \sin^4(\pi/8) = 1 - 2\sin^2(\pi/8)\cos^2(\pi/8) = 1 - \frac{\sin^2(\pi/4)}{2} = \frac{3}{4}$$

$$\text{QBER}_{Breidbart} = \frac{1}{4}$$

— exactly the same disturbance as strategy (a).

*Eve's Shannon information*: her guess forms a binary symmetric channel with error `sin²(π/8) ≈ 0.1464`:

$$I(A{:}E) = 1 - H_2(\cos^2(\pi/8)) = 1 - H_2(0.8536) = 1 - 0.6009 \approx 0.399 \text{ bits per sifted bit}$$

**Comparison** (all intercept-resend, per sifted bit):

| Strategy | QBER | P(guess bit) | I(A:E) |
|----------|------|--------------|--------|
| Random BB84 basis | 25% | 0.75 | 0.500 bits |
| Fixed Z basis | 25% | 0.75 | 0.500 bits |
| Breidbart basis | 25% | 0.854 | 0.399 bits |

All three cause identical, glaring disturbance. The Breidbart basis maximizes Eve's probability of guessing each individual bit (useful if she must guess the whole key outright), yet delivers *less* Shannon information than the basis-matching strategies — uniform 85% confidence on every bit carries less entropy reduction than certainty on half the bits. "Best attack" depends on the figure of merit; security proofs must therefore bound Eve by her *optimal* information, not by any specific strategy.

## Exercises

**Exercise 1**: Alice and Bob run BB84 and publicly compare `k` sifted bits to test for a full intercept-resend attack. (a) What is the probability Eve escapes detection (no errors in the compared bits)? (b) How large must `k` be to catch her except with probability `10⁻⁶`? (c) What is the expected number of compared bits until the *first* error reveals her?

<details><summary>Solution</summary>

(a) Each compared bit is erroneous independently with probability `1/4`, so `P(undetected) = (3/4)^k`.

(b) `(3/4)^k ≤ 10⁻⁶` gives `k ≥ ln(10⁻⁶)/ln(3/4) = 13.82/0.2877 ≈ 48.02`, so `k = 49` bits suffice (`k = 48` falls just short: `(3/4)^48 ≈ 1.007 × 10⁻⁶`, while `(3/4)^49 ≈ 7.6 × 10⁻⁷`).

(c) Geometric distribution with success probability `1/4`: expected `4` comparisons. Full-strength eavesdropping on a quantum channel is not subtle — it is the *partial* attacks that force the careful entropy accounting of privacy amplification.

</details>

**Exercise 2**: Eve intercept-resends (random BB84 basis) only a fraction `η` of the pulses and lets the rest pass. Alice and Bob measure `QBER = 5%` on an otherwise noiseless channel. (a) Infer `η`. (b) Bound Eve's information per sifted bit. (c) Using the Shor-Preskill rate, how much secure key per sifted bit remains?

<details><summary>Solution</summary>

(a) `QBER = η/4 = 0.05` gives `η = 0.20`: Eve touched 20% of the pulses.

(b) She gains `1/2` bit on each attacked sifted bit: `I(A:E) = η/2 = 0.10` bits per sifted bit.

(c) `r = 1 - 2H₂(0.05) = 1 - 2(0.2864) ≈ 0.427` secure bits per sifted bit. Note the proof-driven rate charges *more* than Eve's intercept-resend haul of 0.10 bits: the bound must cover the **optimal** attack consistent with `Q = 5%` (coherent collective attacks), not merely the one we analyzed. At `Q = 11%`, `H₂(Q) = 1/2` and `r` hits zero — beyond that, no one-way post-processing can rescue the key.

</details>

**Exercise 3**: In the **six-state protocol**, Alice uses three mutually unbiased bases (Z, X, and Y), and sifting keeps the ~1/3 of positions where Bob's random basis matches. Compute the QBER caused by full intercept-resend when Eve picks uniformly among the three bases. Why does the extra basis help Alice and Bob?

<details><summary>Solution</summary>

On a sifted position, Eve's basis matches Alice's with probability `1/3` (no error, full information). With probability `2/3` she measures in one of the two wrong bases; any state of one mutually unbiased basis gives a uniformly random outcome in another, and the resent state then gives Bob a fair coin in Alice's basis: error `1/2`.

$$\text{QBER}_{6\text{-state}} = \frac{2}{3}\cdot\frac{1}{2} = \frac{1}{3} \approx 33\%$$

versus 25% for BB84. The same eavesdropping produces *more* visible disturbance — equivalently, for a fixed observed QBER, Eve's possible information is smaller, so the six-state protocol tolerates a higher error threshold (≈ 12.6% vs. 11.0% for one-way post-processing) at the cost of keeping only 1/3 of positions in sifting.

</details>

**Exercise 4**: Evaluate the asymptotic BB84 key rate `r = 1 - 2H₂(Q)` at `Q = 1%, 5%, 8%`, and find the threshold `Q` where `r = 0`. A metro link produces `10⁶` sifted bits/s at `Q = 5%`: what secure-key throughput remains after post-processing (asymptotically)?

<details><summary>Solution</summary>

- `H₂(0.01) = 0.0808` → `r = 1 - 0.1616 = 0.838`
- `H₂(0.05) = 0.2864` → `r = 0.427`
- `H₂(0.08) = 0.4022` → `r = 0.196`
- Threshold: `r = 0` when `H₂(Q) = 1/2`, i.e. `Q ≈ 0.1100` (11.0%)

Throughput at `Q = 5%`: `10⁶ × 0.427 ≈ 4.3 × 10⁵` secure bits/s. The rate degrades steeply with QBER: going from 1% to 8% error costs over 75% of the key, which is why source and detector quality dominate practical QKD engineering.

</details>

**Exercise 5**: Prove the security root directly: show that no unitary `U` (with any ancilla) can satisfy `U|ψ⟩|0⟩|E⟩ = |ψ⟩|ψ⟩|E_ψ⟩` for both `|ψ⟩ = |0⟩` and `|ψ⟩ = |+⟩`. Conclude which state sets *can* be copied, and why BB84's choice defeats copying.

<details><summary>Solution</summary>

Suppose `U|0⟩|0⟩|E⟩ = |0⟩|0⟩|E₀⟩` and `U|+⟩|0⟩|E⟩ = |+⟩|+⟩|E_+⟩`. Unitaries preserve inner products. Before:

`⟨0|+⟩ · ⟨0|0⟩ · ⟨E|E⟩ = 1/√2`

After:

`⟨0|+⟩ · ⟨0|+⟩ · ⟨E₀|E_+⟩ = (1/2)⟨E₀|E_+⟩`

Equating: `1/√2 = (1/2)⟨E₀|E_+⟩`, so `⟨E₀|E_+⟩ = √2 > 1` — impossible, since inner products of unit vectors are bounded by 1 (Cauchy-Schwarz). Contradiction. ∎

In general, `s = s²·⟨E_ψ|E_φ⟩` with `s = ⟨ψ|φ⟩` forces `|s| ∈ {0, 1}`: only sets of **mutually orthogonal** (or identical) states admit a cloner — which is exactly classical copying. BB84's four states contain non-orthogonal pairs with `|⟨ψ|φ⟩| = 1/√2 ∉ {0,1}`, so *no* device — regardless of technology — can duplicate them, and every eavesdropping gain must come with disturbance.

</details>

## Summary

- Quantum cryptography turns the no-cloning theorem into a security guarantee: information about non-orthogonal signal states cannot be extracted without creating detectable errors — security by physics, not by assumed computational hardness
- **BB84**: random bits in random Z/X bases; sifting keeps the ~50% of basis-matched positions; comparing a sample estimates the QBER; error correction (cost `H₂(Q)`) and privacy amplification (cost `H₂(Q)`) yield the asymptotic rate `r = 1 - 2H₂(Q)`, positive below `Q ≈ 11%`
- **Intercept-resend** in a random BB84 basis (or fixed Z) causes exactly `25%` QBER and gains Eve `0.5` bits/sifted bit; the **Breidbart basis** maximizes her per-bit guessing probability (`cos²(π/8) ≈ 0.854`) but yields *less* Shannon information (`≈ 0.399` bits) at the same 25% disturbance
- **E91** certifies security by CHSH violation (`S = 2√2` undisturbed) and grounds device-independent QKD; **BBM92** is entanglement-based BB84 without the Bell test and reduces to BB84's analysis
- Practical QKD uses weak coherent pulses with **decoy states** to defeat photon-number-splitting; fiber loss plus no-amplification caps point-to-point range (PLOB bound), motivating twin-field QKD, satellites, MDI-QKD, and future repeaters
- QKD and post-quantum cryptography answer Shor differently: QKD offers information-theoretic key distribution on dedicated hardware; PQC (ML-KEM, ML-DSA, SLH-DSA) offers computationally secure drop-in software including signatures — deployments increasingly combine both

## Further Reading

1. **Bennett & Brassard**, "Quantum Cryptography: Public Key Distribution and Coin Tossing" (Proceedings of IEEE ICCSSP, Bangalore, 1984; reprinted in Theoretical Computer Science 560, 2014) — the original BB84 paper, remarkably readable
2. **Ekert**, "Quantum Cryptography Based on Bell's Theorem" (Physical Review Letters 67, 661, 1991) — E91; the conceptual origin of device-independent security
3. **Shor & Preskill**, "Simple Proof of Security of the BB84 Quantum Key Distribution Protocol" (Physical Review Letters 85, 441, 2000; arXiv:quant-ph/0003004) — the security proof behind the `1 - 2H₂(Q)` rate and 11% threshold
4. **Lo, Ma & Chen**, "Decoy State Quantum Key Distribution" (Physical Review Letters 94, 230504, 2005; arXiv:quant-ph/0411004) — the technique that made weak-pulse QKD secure and practical
5. **Pirandola et al.**, "Advances in Quantum Cryptography" (Advances in Optics and Photonics 12, 1012-1236, 2020; arXiv:1906.01645) — comprehensive modern survey: protocols, security proofs, PLOB bound, MDI/twin-field QKD, and implementation attacks
