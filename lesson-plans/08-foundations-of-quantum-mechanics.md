# Foundations of Quantum Mechanics

## Goal
Engage with the deep conceptual and philosophical questions underlying quantum mechanics — interpretations, measurement problem, non-locality, and information-theoretic foundations — to build a rigorous mental model rather than just a computational toolkit.

---

## Module 1 — The Measurement Problem

**Objective:** Understand precisely what the measurement problem is and why it is unresolved.

| Aspect | Description |
|---|---|
| Unitary evolution | Schrödinger equation is linear and deterministic |
| Measurement outcome | Is random and collapses the state — non-linear |
| The problem | Measurement devices are quantum systems too; when does collapse happen? |
| Von Neumann chain | Observer → apparatus → environment → … — where does the cut go? |
| Heisenberg cut | Pragmatic division between quantum system and classical observer |

**Key questions:**
- What is a measurement, physically?
- Does collapse actually occur, or is it apparent?
- Can a quantum system measure another quantum system?

**Exercises:**
- Trace through a Stern-Gerlach measurement using the full quantum formalism for apparatus + particle

<details><summary>Solution</summary>

Treat the "apparatus" as the atom's own centre-of-mass degree of freedom — that is
the minimal honest model, and it already shows everything.

**Initial state.** A silver atom with spin state `α|↑⟩ + β|↓⟩` and a spatial wave
packet `φ₀(z)` (Gaussian, width `σ`):

```
|Ψ(0)⟩ = (α|↑⟩ + β|↓⟩) ⊗ |φ₀⟩
```

**Interaction.** The inhomogeneous field `B_z(z) ≈ B₀ + (∂B/∂z)z` couples spin to
position through `H = −μ·B = −γ(B₀ + (∂B/∂z)z)S_z`. Because `S_z` is diagonal in
`{|↑⟩, |↓⟩}`, the evolution operator factorises on each spin branch, and the term
linear in `z` is a spin-dependent force `F = ±μ_B ∂B/∂z`:

```
|Ψ(t)⟩ = α|↑⟩ ⊗ |φ₊(t)⟩ + β|↓⟩ ⊗ |φ₋(t)⟩
```

where `φ±` are the original packet displaced by `±Δz(t)` and carrying momentum
`±Δp = ±F t`. No collapse has been invoked: this is pure Schrödinger evolution,
and it is **exactly the structure of a CNOT** — the spin is the control, the
position is the target, and the result is an entangled spin–position state.

**Numbers** (`∂B/∂z = 100 T/m`, magnet length `0.10 m`, beam speed `500 m/s`, so
`t = 2.0×10⁻⁴ s`, silver atom `m = 1.79×10⁻²⁵ kg`):

```
F  = μ_B ∂B/∂z      = 9.27×10⁻²² N
Δp = F t            = 1.86×10⁻²⁵ kg·m/s   (velocity kick 1.04 m/s)
2Δz inside magnet   = 2.1×10⁻⁴ m  ≈ 0.21 mm
extra split after a 0.5 m field-free drift ≈ 2.07 mm
```

**When does it become a measurement?** The spin's reduced state is

```
ρ_spin = |α|²|↑⟩⟨↑| + |β|²|↓⟩⟨↓| + αβ*⟨φ₋|φ₊⟩|↑⟩⟨↓| + h.c.
```

The interference terms are suppressed by the packet overlap. For Gaussians of
width `σ` separated by `d`, `⟨φ₊|φ₋⟩ = exp(−d²/8σ²)` (checked by numerical
integration: `d/σ = 2` gives `0.6065`, `d/σ = 4` gives `0.1353`, both matching the
formula to six digits). With `σ ≈ 10 μm` and `d = 207 μm` the overlap is
`4.8×10⁻²⁴` — utterly negligible. **Only then** is the spin's reduced state
diagonal, i.e. indistinguishable from a classical probabilistic mixture.

**The residue.** The *global* state is still the pure superposition
`α|↑⟩|φ₊⟩ + β|↓⟩|φ₋⟩`. Nothing in the dynamics has selected "up" or "down"; the
formalism has only moved the superposition from the spin onto a bigger, more
robust degree of freedom. Add the screen, the photons, the experimenter and you
add more factors to the same branch structure. That is the measurement problem in
one calculation — see the next exercise.

</details>

- Show that including the measurement apparatus in the wavefunction produces an entangled state, not a definite outcome

<details><summary>Solution</summary>

**Von Neumann's measurement model.** Require the interaction to be a legitimate
(unitary, hence linear) map that records the system's basis states:

```
U |s⟩|A_ready⟩ = |s⟩|A_s⟩,     s ∈ {0, 1},  ⟨A₀|A₁⟩ = 0
```

Linearity — not an extra assumption, just what "unitary" means — forces the action
on a superposition:

```
U (c₀|0⟩ + c₁|1⟩)|A_ready⟩ = c₀|0⟩|A₀⟩ + c₁|1⟩|A₁⟩
```

This is an **entangled** state, not `|one particular s⟩|A_s⟩`. Unitary dynamics
cannot map a pure state to one of two different pure states probabilistically:
that would be non-linear and non-deterministic.

**What the observer's statistics look like.** With `|c₀|² = 0.3`, `|c₁|² = 0.7`,
tracing out the apparatus gives (computed with `qiskit.quantum_info`):

```
ρ_system = [[0.3, 0], [0, 0.7]] ,  purity Tr(ρ²) = 0.58 < 1
entanglement entropy S(ρ) = 0.8813 bits
```

So the Born-rule *frequencies* are reproduced: anybody who only looks at the system
(or only at the pointer) sees the right statistics.

**Why that is not a solution.** The diagonal `ρ_system` is an **improper mixture**.
A proper mixture means "it is one of these, we do not know which"; an improper
mixture is a bookkeeping device obtained by ignoring a correlated partner, while
the global state remains the pure, definite, superposed
`c₀|0⟩|A₀⟩ + c₁|1⟩|A₁⟩`. The two are indistinguishable by any measurement *on the
subsystem alone* — and distinguishable in principle by a measurement on the whole
(an interference experiment in the entangled basis, e.g. measuring the observable
`|0A₀⟩⟨1A₁| + h.c.`, which has nonzero expectation in the pure state and zero in a
proper mixture).

**The chain does not terminate.** Add the environment: `Σ_s c_s|s⟩|A_s⟩|E_s⟩`.
Add the experimenter's brain, the lab, the light cone — every step is another
tensor factor joining the branch, never a step that deletes a branch. Decoherence
makes the off-diagonal terms unmeasurable in practice (see Module 4), but it is
derived *from* unitary evolution and therefore cannot produce a single outcome.

**Which is exactly the fork in the road.** Everett: accept the branches as real.
Copenhagen: declare the apparatus classical by fiat (Heisenberg cut). Bohm: add
particle positions that always have definite values. GRW/CSL: modify the dynamics
so that large superpositions really do collapse. QBism: read the state as the
agent's belief. Each takes a different exit from the same, entirely mundane,
calculation above.

</details>

- Explain why the Born rule is not derivable from unitary evolution alone (without additional assumptions)

<details><summary>Solution</summary>

**The logical gap.** Unitary evolution is deterministic, linear and reversible; it
maps state vectors to state vectors. The Born rule assigns *probabilities*
`p(s) = |⟨s|ψ⟩|²` to outcomes. A deterministic evolution law cannot by itself
imply a probability measure over outcomes that it never selects among — there is
nothing in `iħ∂_t|Ψ⟩ = H|Ψ⟩` that says which branch happens, or how often.

**Concrete failure of the naive derivation: branch counting.** In the Everettian
picture the post-measurement state is `c₀|0⟩|A₀⟩|E₀⟩ + c₁|1⟩|A₁⟩|E₁⟩`. Count the
branches: there are two of them for *any* nonzero `c₀, c₁`. Counting therefore
gives `p = 1/2` regardless of amplitudes, contradicting Born unless the measure
over branches is put in by hand. Nor can the measure be read off the dynamics: any
positive weighting of branches is consistent with the Schrödinger equation.

**What extra assumption is always needed.** Every known derivation adds something:

- **Gleason's theorem (1957)**: assume probabilities are assigned to projectors by a
  *non-contextual*, countably additive measure, in dimension `≥ 3`. Then the measure
  must be `Tr(ρP)`. This derives Born from measure-theoretic axioms about
  probability assignment — not from dynamics — and it fails in dimension 2.
- **Deutsch (1999) / Wallace (2010) decision theory**: assume a rational agent's
  preferences obey certain axioms (in particular branching indifference and
  measurement neutrality). Born weights are then the unique rational credences.
  Critics point out that the axioms already encode the amplitude-squared measure.
- **Zurek's envariance (2003)**: assume states related by environment-assisted
  symmetry transformations must receive equal probability. Equal-amplitude branches
  then get equal weight, and general amplitudes follow by fine-graining.
- **Many-minds / Bohm**: Bohmian mechanics reproduces Born only under the
  *quantum equilibrium hypothesis* `ρ = |ψ|²` for the initial particle distribution —
  an independent postulate (with a plausible dynamical-relaxation story).

**The sharpest statement.** Unitarity fixes the *kinematics of branching*; it is
silent about the *measure on branches*. You may bolt any measure onto unitary
quantum mechanics without contradicting the dynamics — it will just disagree with
experiment. Born's rule is therefore an independent physical postulate (or a
consequence of independent postulates), which is why textbooks list it separately.

**Why a quantum programmer should care.** Everything measurable — sampling
distributions, expectation values from an Estimator, error rates — is Born-rule
output. The unitary part of the formalism is the part that is *not* directly
observable; only the Born-rule bridge turns amplitudes into counts.

</details>


---

## Module 2 — Interpretations of Quantum Mechanics

**Objective:** Understand the major interpretations — what they say, what they predict, and their implications for quantum computing.

| Interpretation | Core Claim | Collapse? | Many Worlds? |
|---|---|---|---|
| Copenhagen | Stop asking; use the formalism | Yes (pragmatic) | No |
| Many-Worlds (Everett) | All branches exist; branching on measurement | No | Yes |
| Pilot Wave (de Broglie-Bohm) | Hidden variables; deterministic | No (apparent) | No |
| Relational QM | States are relative to observers | Relative | No |
| QBism | Quantum states are agent beliefs | Subjective | No |
| Consistent Histories | Multiple consistent classical frameworks | Conditional | No |
| Objective Collapse (GRW/CSL) | Physical collapse mechanism added | Yes (modified dynamics) | No |

**Quantum computing perspective:**
- Many-Worlds is favored by many quantum computer scientists (Deutsch)
- Interpretations agree on all predictions — they differ on ontology
- Decoherence provides a partial answer regardless of interpretation

**Exercises:**
- State the EPR argument and explain what it was trying to show

<details><summary>Solution</summary>

**The 1935 paper's target.** Einstein, Podolsky and Rosen did *not* argue that
quantum mechanics is wrong. They argued it is **incomplete** — that the
wavefunction is not the whole story about a physical system, and that a deeper
description with additional ("hidden") variables must exist.

**The three premises.**

1. **Criterion of reality**: "If, without in any way disturbing a system, we can
   predict with certainty the value of a physical quantity, then there exists an
   element of physical reality corresponding to that quantity."
2. **Locality**: measurements on A cannot disturb a spacelike-separated system B.
3. **Completeness requirement**: a complete theory must contain a counterpart for
   every element of reality.

**The argument (Bohm's cleaner spin version).** Prepare the singlet

```
|Ψ⁻⟩ = (|↑↓⟩ − |↓↑⟩)/√2
```

and separate the particles.

- Alice measures `S_z` on A. The outcome lets her predict B's `S_z` with certainty.
  By locality she did not disturb B, so by the reality criterion B's `S_z` is an
  element of reality.
- Alice could instead have measured `S_x`. The same reasoning makes B's `S_x` an
  element of reality.
- Whichever she chooses is up to her, and B is spacelike separated, so **both** `S_z`
  and `S_x` of B must have been elements of reality all along.
- But quantum mechanics cannot assign simultaneous definite values to `S_z` and `S_x`
  (they do not commute; `|ψ⟩` specifies at most one).

**Conclusion (EPR's):** the wavefunction is an incomplete description; the real
state of B includes definite values for both, which the formalism omits.

**Conclusion (history's):** Bell (1964) took EPR's premises seriously and showed
that *any* theory satisfying them — local hidden variables — must obey inequalities
that quantum mechanics violates, and that experiment then violated. So the EPR
premises are not merely unnecessary, they are **false**. The argument's lasting
value is that it isolated the exact assumptions (realism + locality + free choice)
that nature refuses to satisfy, and it named the phenomenon: Schrödinger coined
"entanglement" (*Verschränkung*) in direct response to this paper.

**What EPR got right.** Entanglement is not a technicality; correlations of this
kind are a genuinely new physical resource. Today the same state, the same
correlations, and very nearly the same argument are what make teleportation,
device-independent cryptography and Bell-test-certified randomness work.

</details>

- Describe what "the wavefunction of the universe" means in Many-Worlds

<details><summary>Solution</summary>

**The claim.** There is exactly one quantum state, `|Ψ⟩`, for everything — systems,
apparatus, observers, the lab, the planet — living in the tensor product of all
subsystem Hilbert spaces, and it obeys one law with no exceptions:

```
iħ ∂_t |Ψ⟩ = H |Ψ⟩
```

No collapse postulate, no measurement axiom, no classical/quantum divide. The
Everett interpretation is precisely "quantum mechanics with the second dynamical
law deleted".

**Where worlds come from.** They are not postulated; they are *emergent structure*
in `|Ψ⟩`. When a system entangles with an apparatus and then with the environment,

```
|Ψ⟩ = Σ_s c_s |s⟩|A_s⟩|E_s⟩ ,   ⟨E_s|E_s'⟩ ≈ δ_{ss'}
```

the environment states become effectively orthogonal within femtoseconds
(decoherence), so the branches no longer interfere and each evolves as if the
others were absent. A "world" is one of these dynamically autonomous branches:
approximately defined, emergent like a thermodynamic phase, not a fundamental
posit. The number of worlds is not a well-defined integer, which is a feature of
the ontology, not a gap in it.

**What is being claimed, in ontological terms.** The universal state vector is the
complete physical inventory; everything else — particles, tables, observers,
probabilities — is pattern within it. "The wavefunction of the universe" also has a
literal use in quantum cosmology (Hartle–Hawking, DeWitt's Wheeler–DeWitt equation
`H|Ψ⟩ = 0`, where time itself must be recovered relationally), and Everettians
regard the availability of a sensible cosmological state as a point in their favour:
a collapse-based theory has no obvious account of a system with no external
observer.

**The two hard problems.**

1. **Preferred basis**: `|Ψ⟩` can be expanded in infinitely many bases; what makes
   the pointer basis the one worlds are indexed by? Answer offered: einselection —
   the interaction Hamiltonian with the environment picks out the robust,
   quasi-classical (roughly position) basis. Critics say this is approximate and
   circular-adjacent, since "robust" presupposes a decomposition into subsystems.
2. **Probability**: if all branches occur, what does "probability 0.3" mean? Answers
   offered: Deutsch–Wallace decision theory, Zurek's envariance, self-locating
   uncertainty (Sebens–Carroll). Each adds axioms (see the Born-rule exercise).

**Why quantum computing people like it.** Deutsch's framing — "where was the
factoring computed, if not in the other branches?" — makes the branch structure feel
operational. That framing is heuristic, though: Shor's algorithm is not parallel
search, its power comes from interference between amplitude paths, which every
interpretation describes identically. The formalism, the circuits and the results
are interpretation-independent; only the story is not.

</details>

- Explain why no interpretation can be empirically distinguished (today)

<details><summary>Solution</summary>

**The structural reason.** An "interpretation" in the strict sense keeps the
formalism — the same Hilbert space, the same unitary dynamics, the same Born rule —
and changes only what the formalism is *about*. Two theories that share a
predictive algorithm cannot be distinguished by predictions. Copenhagen,
Many-Worlds, relational QM, QBism and consistent histories are all in this class,
and their empirical equivalence is not a coincidence but a design constraint:
each was constructed to reproduce standard quantum mechanics exactly.

Bohmian mechanics adds particle trajectories, but reproduces Born statistics
exactly under the quantum equilibrium hypothesis (`ρ = |ψ|²`), which it assumes for
initial conditions. Empirically equivalent again — by construction.

**The important exception: some "interpretations" are actually different theories.**
Objective-collapse models (GRW, CSL, Diósi–Penrose gravitational collapse) *modify
the Schrödinger equation* with a stochastic nonlinear term. They make genuinely
different predictions:

- tiny anomalous heating and spontaneous X-ray emission from bulk matter,
- loss of interference for masses above a model-dependent scale,
- a collapse rate `λ` and correlation length `r_C` that are free parameters.

These are being actively constrained: underground X-ray searches, LISA-Pathfinder
noise limits, and matter-wave interferometry with molecules of `10⁴–10⁵` amu have
excluded large regions of the GRW/CSL parameter space (though not the whole of it).
So the honest statement is not "interpretations can never be tested" but "theories
that only reinterpret are untestable; theories that modify dynamics are testable,
and are being tested".

**A third category: assumption-testing experiments.** Extended Wigner's-friend
setups (Frauchiger–Renner 2018; Brukner; Bong et al.'s "local friendliness" tests
2020) do not test interpretations one at a time. They show that *sets of
assumptions* — e.g. "observers' measurement records are absolute facts" + locality
+ free choice — are jointly inconsistent with quantum theory, so every
interpretation must give up at least one. That narrows the field logically rather
than empirically, which is real progress.

**What a good answer must therefore say.** (i) Interpretations that only reinterpret
are empirically equivalent by construction, so today's experiments cannot select
among them. (ii) Collapse *theories* are exempt and are being excluded piecewise.
(iii) Interpretations still matter — they generate research programmes
(decoherence theory came out of foundations, as did device-independent
cryptography from Bell), and they differ in the questions they make it natural to
ask.

</details>


---

## Module 3 — Bell's Theorem and Non-Locality

**Objective:** Understand Bell's theorem — the most important result in foundations — and what it proves about the structure of physical reality.

| Concept | Description |
|---|---|
| Local hidden variables | Pre-existing definite values + no faster-than-light influence |
| Bell inequality | Classical bound on correlations: e.g., `|E(a,b) − E(a,c)| ≤ 1 + E(b,c)` |
| CHSH inequality | `|⟨CHSH⟩| ≤ 2` classically; quantum: up to `2√2` |
| Bell test | Measure correlations on entangled pairs and check inequality |
| Loopholes | Detection loophole, locality loophole, freedom-of-choice loophole |
| Loophole-free tests | Achieved in 2015 (Hensen et al., Giustina et al.) |
| Implications | No local hidden variable theory can reproduce QM predictions |

**Exercises:**
- Derive the CHSH inequality from local realism assumptions

<details><summary>Solution</summary>

**Assumptions, stated precisely.**

1. **Realism**: each run is characterised by a hidden variable `λ` (of arbitrary
   nature) that fixes outcome functions `A(a, λ), B(b, λ) ∈ {−1, +1}`.
2. **Locality**: `A` does not depend on the distant setting `b`, and `B` not on `a`.
3. **Measurement independence (free choice)**: the distribution `ρ(λ)` is the same
   whatever settings are chosen — `ρ(λ|a, b) = ρ(λ)`.

Correlations are then

```
E(a, b) = ∫ dλ ρ(λ) A(a, λ) B(b, λ)
```

**The derivation.** Take two settings per side, `a₀, a₁` and `b₀, b₁`, and form

```
S = E(a₀,b₀) + E(a₀,b₁) + E(a₁,b₀) − E(a₁,b₁)
  = ∫ dλ ρ(λ) [ A₀(B₀ + B₁) + A₁(B₀ − B₁) ]
```

writing `A_i = A(a_i, λ)`, `B_j = B(b_j, λ)`. Crucially all four values exist
*simultaneously* for the same `λ` — that is the realism assumption doing its work,
and it is why the same `λ` can be factored out of all four terms (locality and free
choice are what license using one `ρ(λ)` across the four setting pairs).

Now `B₀, B₁ ∈ {±1}`, so exactly one of the following holds:

- `B₀ = B₁`  ⇒ `B₀ + B₁ = ±2` and `B₀ − B₁ = 0`
- `B₀ = −B₁` ⇒ `B₀ + B₁ = 0` and `B₀ − B₁ = ±2`

Either way the bracket equals `±2A₀` or `±2A₁`, hence lies in `[−2, +2]`. Averaging
a quantity bounded by 2 against a normalised probability density gives

```
|S| ≤ 2 · ∫ dλ ρ(λ) = 2      (the CHSH inequality)
```

**What is and is not assumed.** No assumption about the physics of the particles,
the dimension of `λ`, determinism of the *apparatus*, or the form of the
correlations. Stochastic local models are covered too: randomise `A` and `B` given
`λ` and absorb the randomness into `λ` itself. This generality is what makes the
inequality a test of a whole *class* of theories.

**Loopholes = the assumptions in disguise.** Each experimental loophole is a way
the derivation could still hold:

- *Locality loophole*: if a signal can travel from Alice's setting to Bob's outcome,
  premise 2 fails — closed by fast random setting choices and spacelike separation.
- *Detection/fair-sampling loophole*: if only a biased subensemble is detected, the
  measured averages are not `E(a, b)` — closed by high-efficiency detectors
  (`η > 2/3` for CHSH with maximally entangled states).
- *Freedom-of-choice loophole*: correlations between `λ` and the settings violate
  premise 3 — addressed by fast quantum random number generators, cosmic photons
  (the Cosmic Bell tests) and the BIG Bell Test.

The 2015 loophole-free experiments (Hensen et al.; Giustina et al.; Shalm et al.)
closed locality and detection simultaneously. Superdeterminism — denying premise 3
outright — remains logically available and empirically untouchable.

</details>

- Compute the quantum mechanical prediction for `⟨CHSH⟩` for `|Φ⁺⟩`

<details><summary>Solution</summary>

**Setup.** `|Φ⁺⟩ = (|00⟩ + |11⟩)/√2`. Alice measures `A(a) = a·σ`, Bob
`B(b) = b·σ`, with unit vectors `a, b`.

**General correlator.** Using `⟨Φ⁺|σ_i ⊗ σ_j|Φ⁺⟩ = diag(1, −1, 1)_{ij}` (i.e. `+1`
for `XX` and `ZZ`, `−1` for `YY`, `0` off-diagonal):

```
E(a, b) = ⟨Φ⁺|(a·σ) ⊗ (b·σ)|Φ⁺⟩ = a_x b_x − a_y b_y + a_z b_z
```

Restricting both settings to the `x–z` plane, `a = (sin α, 0, cos α)`,
`b = (sin β, 0, cos β)`:

```
E(α, β) = cos α cos β + sin α sin β = cos(α − β)
```

(Verified numerically: `E(0, π/4) = 0.707107 = cos(π/4)` ✓.)

**Optimal settings.** Choose `α₀ = 0`, `α₁ = π/2`, `β₀ = π/4`, `β₁ = −π/4`. Then

```
E(α₀,β₀) = cos(−π/4) = +1/√2
E(α₀,β₁) = cos(+π/4) = +1/√2
E(α₁,β₀) = cos(+π/4) = +1/√2
E(α₁,β₁) = cos(3π/4) = −1/√2
```

so

```
S = E(α₀,β₀) + E(α₀,β₁) + E(α₁,β₀) − E(α₁,β₁) = 4/√2 = 2√2 ≈ 2.828427
```

Exact `StatevectorEstimator` evaluation of the four observables returns
`[0.707107, 0.707107, 0.707107, −0.707107]` and `S = 2.828427`, confirming the
algebra.

**Why these angles.** Each Bob setting sits `45°` from each Alice setting, i.e. all
four correlators have magnitude `cos(π/4)`, and the sign pattern is arranged so all
four terms add. Geometrically: with `E = cos(α−β)`, `S(α₀,α₁,β₀,β₁)` is maximised
when the four directions are equally spaced by `45°` in the plane — the classic
"CHSH pinwheel".

**The gap that matters.** Classical local-realistic bound `2`; quantum value
`2√2 ≈ 2.828`; algebraic maximum `4` (reached only by a hypothetical
"Popescu–Rohrlich box", which no physical state achieves). The ratio `√2` is the
whole of the Bell violation, and it is measurable with a few thousand shots.

</details>

- Show that `2√2` is the Tsirelson bound (maximum quantum violation)

<details><summary>Solution</summary>

**Setup (no assumption of qubits).** Let `A₀, A₁` act on Alice's Hilbert space and
`B₀, B₁` on Bob's, each Hermitian with `A_i² = B_j² = I` (`±1`-valued observables),
and `[A_i, B_j] = 0` (they act on different tensor factors). Define the CHSH
operator

```
C = A₀⊗B₀ + A₀⊗B₁ + A₁⊗B₀ − A₁⊗B₁
```

Then `|⟨CHSH⟩| = |⟨ψ|C|ψ⟩| ≤ ‖C‖` for any state, so it suffices to bound the
operator norm.

**Cirel'son's algebraic identity.** Expand `C²`. The squares of the four terms give
`4I`; the cross terms cancel in pairs except for the commutators, leaving

```
C² = 4I − [A₀, A₁] ⊗ [B₀, B₁]
```

(Verified numerically on random qubit observables: the maximum entrywise
difference between the two sides is `0.0`.)

**Bounding the commutators.** For any operators with `‖A_i‖ = 1`:

```
‖[A₀, A₁]‖ = ‖A₀A₁ − A₁A₀‖ ≤ 2‖A₀‖‖A₁‖ = 2
```

and likewise `‖[B₀, B₁]‖ ≤ 2`. Therefore

```
‖C²‖ ≤ 4 + ‖[A₀,A₁]‖·‖[B₀,B₁]‖ ≤ 4 + 4 = 8
```

Since `C` is Hermitian, `‖C‖ = √‖C²‖ ≤ √8 = 2√2`. ∎

**Attainability.** The bound is tight: the Bell state with the pinwheel angles of
the previous exercise achieves exactly `2√2`. A brute-force numerical maximisation
over 20 000 random pairs of qubit observables reached `2.828423`, converging to
`2√2 = 2.828427` from below, as expected.

**Reading the proof.** The classical bound `2` comes from the four values existing
simultaneously; the quantum excess is exactly the failure of that, quantified by
`[A₀, A₁] ≠ 0`. If Alice's two observables commute (jointly measurable), `C² = 4I`
and the classical bound returns. **Non-commutativity on each side is the sole
source of the violation**, and the `√2` is how much non-commutativity can buy.

**Context.** `2√2` is not required by no-signalling: the Popescu–Rohrlich box gives
`S = 4` while still forbidding superluminal communication. So quantum theory sits
strictly between local realism and the no-signalling limit, and explaining *why*
nature stops at `2√2` (information causality, macroscopic locality, exclusivity
principles) is an active foundational programme. Operationally, near-maximal
violation also certifies the devices themselves — this is the basis of
device-independent QKD and certified randomness.

</details>

- Design a Bell test circuit in Qiskit and simulate the CHSH value

<details><summary>Solution</summary>

**Design.** One circuit per setting pair. Prepare `|Φ⁺⟩` with `H` + `CNOT`, then
rotate each qubit's measurement basis before a `Z`-basis measurement. Measuring `Z`
after applying `R_y(−θ)` is the same as measuring `cos θ·Z + sin θ·X`, because

```
R_y(−θ)† Z R_y(−θ) = cos θ·Z + sin θ·X
```

(checked numerically: max deviation `1.1×10⁻¹⁶`). Use the optimal angles
`α₀ = 0`, `α₁ = π/2`, `β₀ = π/4`, `β₁ = −π/4`.

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

a0, a1, b0, b1 = 0.0, np.pi / 2, np.pi / 4, -np.pi / 4
angles = [(a0, b0), (a0, b1), (a1, b0), (a1, b1)]

def bell_meas(a, b):
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(-a, 0)          # rotate Alice's measurement basis
    qc.ry(-b, 1)          # rotate Bob's measurement basis
    qc.measure([0, 1], [0, 1])
    return qc

sampler = StatevectorSampler(seed=np.random.default_rng(1234))
res = sampler.run([bell_meas(a, b) for a, b in angles], shots=20_000).result()

E = []
for k, (a, b) in enumerate(angles):
    counts = res[k].data.c.get_counts()
    total = sum(counts.values())
    # correlator = P(even parity) - P(odd parity)
    E.append(sum((1 if bs.count('1') % 2 == 0 else -1) * n
                 for bs, n in counts.items()) / total)

S = E[0] + E[1] + E[2] - E[3]
print("E =", [round(e, 4) for e in E])
print("S =", round(S, 4))
```

**Real output** (Qiskit 2.5.2, 20 000 shots per setting):

```
 (+0.0000,+0.7854) counts={'00': 8593, '01': 1460, '10': 1435, '11': 8512} E=+0.7105
 (+0.0000,-0.7854) counts={'00': 8534, '01': 1475, '10': 1489, '11': 8502} E=+0.7036
 (+1.5708,+0.7854) counts={'00': 8350, '01': 1464, '10': 1478, '11': 8708} E=+0.7058
 (+1.5708,-0.7854) counts={'00': 1461, '01': 8601, '10': 8553, '11': 1385} E=-0.7154
 S = 2.8353   (quantum maximum 2.8284, classical bound 2)
```

`S = 2.835 > 2` — a clear violation. The value slightly exceeds `2√2` here purely
from shot noise: with 20 000 shots per correlator the standard error on each `E` is
`≈ √((1−E²)/n) ≈ 0.005`, so `σ_S ≈ 0.01`, and `2.835` is within one and a half
sigma of `2.828`.

**Cross-check with the Estimator** (exact, no sampling):

```python
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

bell = QuantumCircuit(2); bell.h(0); bell.cx(0, 1)
def obs(a, b):
    return SparsePauliOp(["ZZ", "ZX", "XZ", "XX"],
                         coeffs=[np.cos(a)*np.cos(b), np.cos(a)*np.sin(b),
                                 np.sin(a)*np.cos(b), np.sin(a)*np.sin(b)])
est = StatevectorEstimator()
evs = [float(est.run([(bell, obs(a, b))]).result()[0].data.evs) for a, b in angles]
# -> [0.707107, 0.707107, 0.707107, -0.707107],  S = 2.828427
```

**Notes for running this on hardware.** (i) The circuits must be transpiled to ISA
form first (`generate_preset_pass_manager`). (ii) Real devices typically give
`S ≈ 2.2–2.7` — readout error and decoherence pull the correlators toward zero;
readout mitigation recovers much of it. (iii) This is *not* a loophole-free Bell
test: the two qubits sit microns apart on one chip and are measured by the same
electronics, so locality and freedom-of-choice are wide open. It demonstrates the
quantum correlation value, not the exclusion of local realism.

</details>


---

## Module 4 — Decoherence and the Classical Limit

**Objective:** Understand how quantum systems become effectively classical through interaction with the environment — without needing collapse.

| Topic | Key Concepts |
|---|---|
| Einselection | Environment selects preferred "pointer" basis |
| Decoherence timescale | Extremely fast for macroscopic objects (10⁻²³ s for a dust grain) |
| Reduced density matrix | Tracing out environment destroys off-diagonal coherences |
| Pointer states | States robust under environmental monitoring |
| Quantum Darwinism | Classical world emerges when many environment copies record the same info |
| Decoherence vs collapse | Decoherence produces apparent collapse; does not solve preferred basis problem |

**Quantum computing relevance:**
- T₂ decoherence time measures how quickly superposition is destroyed
- Gate fidelity degrades as decoherence destroys coherences
- Error correction must fight decoherence faster than it occurs

**Exercises:**
- Compute how the off-diagonal elements of `ρ` decay under a dephasing channel

<details><summary>Solution</summary>

**Discrete (Kraus) form.** The phase-flip channel applies `Z` with probability `p`:

```
E(ρ) = (1 − p) ρ + p ZρZ ,   K₀ = √(1−p) I ,  K₁ = √p Z
```

Act on a general qubit state:

```
ρ = [[ρ₀₀, ρ₀₁], [ρ₁₀, ρ₁₁]]   →   E(ρ) = [[ρ₀₀, (1−2p)ρ₀₁], [(1−2p)ρ₁₀, ρ₁₁]]
```

because `Z ρ Z` flips the sign of the off-diagonals and leaves the populations
alone. So **populations are untouched; coherences shrink by the factor `1 − 2p`**.
Verified numerically on `ρ = |+⟩⟨+|`, `p = 0.1`: `ρ₀₁` goes from `0.5` to `0.4`,
exactly the factor `0.8 = 1 − 2p`.

**Composition and the exponential.** `n` independent applications multiply the
factors:

```
ρ₀₁(n) = (1 − 2p)ⁿ ρ₀₁(0) = e^{−n Γ} ρ₀₁(0),   Γ = −ln(1 − 2p)
```

Check with `p = 0.1`, `n = 50`: `(0.8)⁵⁰ = 1.427248×10⁻⁵`, and
`exp(−50 × 0.223144) = 1.427248×10⁻⁵` ✓.

**Continuous (Lindblad) form.** With dephasing operator `L = √(γ/2) Z`:

```
dρ/dt = γ/2 (ZρZ − ρ)   ⇒   ρ₀₁(t) = ρ₀₁(0) e^{−γ t} ,   ρ₀₀, ρ₁₁ constant
```

Defining `T₂ = 1/γ` (pure dephasing only) gives the familiar

```
ρ₀₁(t) = ρ₀₁(0) e^{−t/T₂}
```

**Bloch-sphere picture.** `(x, y, z) → (x e^{−t/T₂}, y e^{−t/T₂}, z)`: the sphere
collapses onto the `z`-axis. A `|+⟩` state becomes maximally mixed while `|0⟩` and
`|1⟩` are untouched — dephasing destroys *phase* information, not *population*.
The `z`-axis is the pointer basis einselected by this interaction, which is exactly
the Module 4 story in two lines of algebra.

**Where the measurement problem shows up again.** The final state
`diag(ρ₀₀, ρ₁₁)` is an *improper* mixture: the phase has leaked into the
environment, not vanished. In principle a measurement on system + environment
recovers it (spin echoes and dynamical decoupling do exactly this for the
*reversible*, low-frequency part of the noise); in practice, once the environment
is large and uncontrolled, it is gone.

**Hardware translation.** A superconducting qubit with `T₂ = 100 μs` and a
`300 ns` two-qubit gate keeps usable coherence for roughly `T₂/t_gate ≈ 330` gates
— which is precisely why NISQ circuits are shallow, and why `XY4`-style dynamical
decoupling (Module 7 of the Qiskit lesson) is worth enabling on idle qubits.

</details>

- Explain why Schrödinger's cat is in practice always decohered

<details><summary>Solution</summary>

**The mechanism.** Coherence between two branches survives only while the
*environment* cannot tell them apart. Each scattered air molecule, photon or
phonon that carries away "which branch" information multiplies the off-diagonal
term by the overlap of the corresponding environment states. After `N` such events

```
ρ_offdiag ∝ ⟨E_alive|E_dead⟩ ≈ (overlap per event)^N → 0
```

For a macroscopic separation, one scattering event already resolves the two
positions almost perfectly (the scatterer's wavelength is far smaller than the
separation), so the overlap per event is `≈ 0` and the **decoherence rate saturates
at the scattering rate**.

**Order-of-magnitude arithmetic (a cat in air).** Number density at STP
`n ≈ 2.5×10²⁵ m⁻³`, mean molecular speed `v ≈ 500 m/s`, cat cross-section
`A ≈ 0.1 m²`:

```
collision rate = n v A ≈ 1.3×10²⁷ s⁻¹   →   τ_dec ≈ 8×10⁻²⁸ s
```

Repeat for a 10 μm dust grain (`A = π(5 μm)² = 7.9×10⁻¹¹ m²`):
`rate ≈ 9.8×10¹⁷ s⁻¹`, `τ ≈ 10⁻¹⁸ s`. Standard treatments (Joos–Zeh; Zurek's
tables) use the localisation-rate form `Γ = Λ(Δx)²` and quote figures from
`10⁻¹⁸` down to `10⁻³⁶ s` depending on the environment and the separation assumed
— the module table's `10⁻²³ s` sits in the middle of that range. Every route gives
the same verdict: the cat's coherence is destroyed unimaginably faster than any
measurement could probe it.

**Remove the air, and it still fails.** In vacuum, 300 K blackbody photons still
scatter off the cat; remove those and the 2.7 K cosmic microwave background
remains; and the cat radiates its own thermal photons. Because the cat is warm and
big, it broadcasts "which branch" information into the universe continuously — this
is Zurek's quantum Darwinism: the record is redundantly copied into many
environment fragments, which is *why* the outcome looks objective to every observer.

**The scaling law worth remembering.** Decoherence rate grows with (i) the size of
the superposed separation, (ii) the coupling strength, and (iii) the number of
environmental degrees of freedom — roughly as `Λ(Δx)²` for small separations,
saturating at the scattering rate for large ones. Interference has been
demonstrated with molecules up to `~10⁴–10⁵` amu in ultra-high vacuum and
cryogenic conditions; a cat is `~10²⁷` amu and sits in air. The gap is not
technological squeamishness, it is roughly twenty orders of magnitude.

**What this does and does not explain.** It explains *why we never see the
interference* — the cat problem as a practical matter is completely solved. It does
**not** explain why the observer sees a specific outcome: decoherence turns the
superposition into an improper mixture over the pointer basis, not into one
definite fact. That residue is the measurement problem, and Module 1's chain is
untouched by any amount of air.

</details>

- Relate T₂ time on a qubit to the decoherence mechanism

<details><summary>Solution</summary>

**Definitions.**

- `T₁` — *energy relaxation* (amplitude damping): the qubit exchanges a quantum with
  the environment, `|1⟩ → |0⟩`. Populations decay as `e^{−t/T₁}`.
- `T_φ` — *pure dephasing*: the qubit's frequency fluctuates, randomising the phase
  without energy exchange. Coherence decays as `e^{−t/T_φ}`.
- `T₂` — total coherence decay of the off-diagonals. The two channels add in rate:

```
1/T₂ = 1/(2T₁) + 1/T_φ        ⇒  T₂ ≤ 2T₁
```

(the factor 2 because an energy decay event destroys half as much phase
information per unit time as it destroys population — `⟨σ₋⟩` decays at half the
rate of the population difference.)

**Which physical mechanism feeds which term** (superconducting transmons):

| Mechanism | Affects |
|---|---|
| Purcell decay into the readout resonator, dielectric loss, two-level-system defects, quasiparticles | `T₁` |
| `1/f` flux noise (flux-tunable qubits), charge noise, critical-current noise | `T_φ` |
| Thermal photon shot noise in the readout resonator (AC Stark shift jitter) | `T_φ` |
| Slow drift of the qubit frequency across an ensemble of runs | `T₂*` only |

**`T₂` versus `T₂*`.** A Ramsey experiment measures `T₂*`, which includes
*quasi-static* noise — frequency offsets constant within a run but varying between
runs. A Hahn echo (`X` pulse at the midpoint) refocuses that slow component, so
`T₂^echo ≥ T₂*`, and the echo decay isolates the genuinely high-frequency noise.
A `CPMG`/`XY4` pulse train pushes the filter function to higher frequencies still.
This is the physical content of the `dynamical_decoupling` option on IBM runtime
primitives: it converts the `T₂*`-limited idle into a `T₂^echo`-limited one.

**Turning `T₂` into a circuit budget.** For a qubit decohering for a time `t`, the
average gate infidelity of the resulting thermal-relaxation channel is

```
ε ≈ (t/3)·(1/T₂ + 1/(2T₁))
```

Checked against `qiskit_aer.noise.thermal_relaxation_error` +
`average_gate_fidelity`: `T₁ = T₂ = 100 μs, t = 300 ns` gives a measured
`ε = 1.498×10⁻³` against the formula's `1.500×10⁻³`; `T₁ = 200 μs, T₂ = 400 μs,
t = 60 ns` gives `9.999×10⁻⁵` against `1.000×10⁻⁴`. So:

```
T₁ = T₂ = 100 μs, t_2q = 300 ns  →  ε ≈ 1.5×10⁻³ per gate, ≈ 330 gates before T₂
T₁ = 200, T₂ = 400 μs, t_2q = 60 ns  →  ε ≈ 1.0×10⁻⁴ per gate, ≈ 6700 gates
```

That single ratio — coherence time over gate time — is the most useful
single-number figure of merit for a NISQ device, and it has to reach roughly
`10³–10⁴` before error correction buys more than it costs.

**Foundational reading of the same numbers.** `T₂` is the timescale on which the
environment learns which branch the qubit is in. A quantum computer is an attempt
to build a system whose "cat" (an entangled register) decoheres slowly enough to be
useful — pushing the Module 4 decoherence estimate from `10⁻²⁷ s` for a real cat up
to `10⁻⁴ s` for an engineered one, by making the system small, cold, weakly coupled
and isolated.

</details>


---

## Module 5 — Quantum Information-Theoretic Foundations

**Objective:** Understand quantum mechanics through the lens of information — the framework that most directly connects to quantum computing.

| Topic | Key Concepts |
|---|---|
| No-cloning theorem | Cannot copy an unknown quantum state |
| No-deleting theorem | Cannot delete an unknown quantum state |
| Holevo bound | Quantum channel can transmit at most n classical bits per n qubits |
| Superdense coding | Send 2 classical bits per entangled qubit pair |
| Quantum teleportation | Transmit qubit using entanglement + 2 classical bits |
| No-communication theorem | Entanglement cannot transmit information faster than light |
| Information as fundamental | Wheeler's "It from Bit"; QBism; information-theoretic axioms |

**Axiomatic approaches:**
- Hardy's axioms (2001): reconstruct QM from 5 simple information-theoretic postulates
- Chiribella-D'Ariano-Perinotti (CDP): QM from operational axioms about experiments
- Goal: understand *why* nature is quantum, not just *that* it is

**Exercises:**
- Prove the no-cloning theorem from linearity of quantum mechanics

<details><summary>Solution</summary>

**Statement.** There is no unitary `U` and fixed blank state `|b⟩` with

```
U(|ψ⟩ ⊗ |b⟩) = |ψ⟩ ⊗ |ψ⟩    for all |ψ⟩ in a Hilbert space of dimension ≥ 2
```

**Proof 1 — linearity.** Suppose such a `U` exists. It clones the basis states:

```
U(|0⟩|b⟩) = |0⟩|0⟩ ,     U(|1⟩|b⟩) = |1⟩|1⟩
```

Apply it to `|+⟩ = (|0⟩ + |1⟩)/√2`. By linearity:

```
U(|+⟩|b⟩) = (U|0⟩|b⟩ + U|1⟩|b⟩)/√2 = (|00⟩ + |11⟩)/√2
```

But cloning demands

```
|+⟩|+⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
```

These differ (the first is a maximally entangled Bell state, the second a product
state; their inner product is `1/√2 ≠ 1`). Contradiction. ∎

**Proof 2 — inner products.** Unitaries preserve inner products. For any `|ψ⟩, |φ⟩`:

```
⟨ψ|φ⟩ = ⟨ψ|φ⟩⟨b|b⟩ = (⟨ψ|⟨b|)U†U(|φ⟩|b⟩) = ⟨ψ|φ⟩²
```

so `x = x²` with `x = ⟨ψ|φ⟩`, giving `x ∈ {0, 1}`. Cloning is therefore possible
only for a set of states that are pairwise orthogonal (or identical) — i.e. only
for *known* states from a fixed orthonormal set, which is just classical copying.
∎ This second proof also quantifies the obstruction: the more non-orthogonal the
states, the worse any cloning attempt must be.

**What is not forbidden.**

- *Copying known states*: if you are told `|ψ⟩`, you can prepare as many as you like.
- *Copying orthogonal states*: `CNOT` copies `|0⟩, |1⟩` in the computational basis
  (but not their superpositions — the same `CNOT` entangles `|+⟩` instead).
- *Approximate cloning*: the optimal universal symmetric `1 → 2` qubit cloner
  (Bužek–Hillery) achieves fidelity `5/6 ≈ 0.833` on every input — good, not perfect.
- *Broadcasting mixed states*: forbidden too (no-broadcasting theorem), except for
  commuting families.
- *Teleportation*: moves a state without copying it — the original is destroyed by
  the Bell measurement, which is precisely what keeps it legal.

**Consequences worth naming.**

- **QKD security**: an eavesdropper cannot copy the qubits in transit; measuring
  disturbs, and BB84's error rate exposes her.
- **Quantum error correction cannot work by redundancy**: `|ψ⟩ → |ψψψ⟩` is illegal.
  The 3-qubit code instead spreads one qubit's information over an entangled
  codeword `α|000⟩ + β|111⟩` and measures *stabilizers*, which reveal errors without
  revealing (or duplicating) the state.
- **No superluminal signalling via cloning**: if Bob could clone his half of an
  entangled pair, he could distinguish Alice's measurement basis and signal faster
  than light. No-cloning is what closes that loophole.

</details>

- Trace through quantum teleportation step by step, identifying where entanglement is consumed

<details><summary>Solution</summary>

**Resources.** Alice holds the unknown `|ψ⟩ = α|0⟩ + β|1⟩` (qubit 1) and half of a
Bell pair (qubit 2); Bob holds the other half (qubit 3). The channel is two
classical bits.

**Step 0 — the shared state.**

```
|Ψ₀⟩ = |ψ⟩₁ ⊗ |Φ⁺⟩₂₃ = (α|0⟩ + β|1⟩)₁ ⊗ (|00⟩ + |11⟩)₂₃/√2
```

**Step 1 — rewrite in Alice's Bell basis.** This is the whole protocol; it is pure
algebra, no dynamics. Expanding `|00⟩₁₂, |01⟩₁₂, …` in the Bell basis gives the
identity

```
|Ψ₀⟩ = ½ [ |Φ⁺⟩₁₂ (α|0⟩ + β|1⟩)₃
         + |Φ⁻⟩₁₂ (α|0⟩ − β|1⟩)₃
         + |Ψ⁺⟩₁₂ (β|0⟩ + α|1⟩)₃
         + |Ψ⁻⟩₁₂ (β|0⟩ − α|1⟩)₃ ]
```

Every branch carries amplitude `½`, so each outcome has probability `¼` — and
**Bob's four conditional states are `I|ψ⟩`, `Z|ψ⟩`, `X|ψ⟩`, `XZ|ψ⟩`** (the last two
up to an unobservable sign), i.e. the unknown state up to a Pauli.

**Step 2 — Alice's Bell measurement.** Implemented as `CNOT(1→2)` then `H(1)`, then
measure both in the computational basis. Outcome `(m₁, m₀)` occurs with probability
`1/4` *independent of α, β* — which is exactly why Alice learns nothing about `|ψ⟩`
(and why no cloning has occurred: qubit 1 is now part of a Bell state and its
original content is gone).

**Step 3 — classical channel.** Alice sends the two bits. This step is limited by
the speed of light and is not optional.

**Step 4 — Bob's correction.** Apply `X^{m₁} Z^{m₀}` (with the usual convention
`m₀` from qubit 1, `m₁` from qubit 2):

```
bits m₁m₀:  00 → I ,  01 → Z ,  10 → X ,  11 → XZ   ⇒  Bob holds |ψ⟩ exactly
```

**Verified.** Running the coherent (deferred-measurement) version in Qiskit with a
random input `|ψ⟩ = (0.018 + 0.645i)|0⟩ + (0.716 − 0.269i)|1⟩` gives Bob's reduced
state with fidelity `1.0` (to 12 decimal places) against the input.

**Where the entanglement goes — the bookkeeping.**

- *Before*: 1 ebit shared between qubits 2 and 3; qubit 1 in a product state with
  the pair.
- *After the Bell measurement*: qubits 1 and 2 are in a **maximally entangled state
  with each other** (one of the four Bell states) and are **completely unentangled
  from qubit 3**. Bob's qubit is now pure again, carrying the message.
- So the ebit has been *consumed*: the entanglement was moved from (2,3) to (1,2)
  and thereby spent as the channel that carried `|ψ⟩` across. You cannot reuse it;
  the next teleportation needs a fresh Bell pair.
- The ebit is consumed even if `|ψ⟩ = |0⟩`. The resource cost is fixed by the
  protocol, not by the message.

**Resource inequalities (Bennett's accounting).**

```
1 ebit + 2 cbits  ≥  1 qubit   (teleportation)
1 ebit + 1 qubit  ≥  2 cbits   (superdense coding)
```

The two are duals, and both are tight: entanglement alone transmits nothing (see the
no-signalling exercise), and 2 classical bits alone cannot carry an arbitrary qubit.

</details>

- State Hardy's 5 axioms and explain what distinguishes QM from classical probability

<details><summary>Solution</summary>

Hardy's *Quantum Theory From Five Reasonable Axioms* (2001) reconstructs the
formalism from operational statements about preparations, transformations and
measurements. Two numbers carry the argument:

- `N` — the number of perfectly distinguishable states of a system (its
  "dimension"),
- `K` — the number of real parameters needed to determine the state completely
  (the number of independent probability measurements required).

**The five axioms.**

1. **Probabilities.** Relative frequencies in ensembles of identically prepared
   systems tend to a limit; the theory is about these probabilities.
2. **Simplicity.** `K` is a function of `N` alone, `K = K(N)`, and takes the
   *smallest* value consistent with the other axioms.
3. **Subspaces.** A system whose state is constrained to lie in an `M`-dimensional
   subspace (`M < N`) behaves exactly like a system of dimension `M`.
4. **Composite systems.** For a system made of two parts,
   `N = N_A N_B` and `K = K_A K_B`.
5. **Continuity.** Between any two pure states there exists a **continuous**
   reversible transformation, and reversible transformations form a continuous
   group.

**How the derivation runs.** Axioms 1–4 force `K = N^r` for some positive integer
`r` (the composition rule makes `K` multiplicative while `N` is multiplicative, and
the subspace axiom forces a power law). Then:

- `r = 1` gives `K = N`: **classical probability theory**. The state is a
  probability vector over `N` outcomes; pure states are the `N` vertices of a
  simplex.
- `r = 2` gives `K = N²`: **quantum theory**. The state is an `N × N` density
  matrix (`N² − 1` real parameters plus normalisation).
- `r ≥ 3` is excluded by the remaining axioms.

**What singles out quantum theory: axiom 5, continuity.** In a classical simplex
the pure states are isolated vertices; any reversible transformation is a
permutation of them, hence *discrete*. There is no continuous reversible path from
one vertex to another that stays inside the state space. Quantum theory's state
space (the Bloch ball for `N = 2`) has a **continuous** set of pure states on its
boundary, so continuous reversible transformations exist — these are exactly the
unitaries. Drop axiom 5 and you get classical probability back; keep it and you are
forced to `r = 2`.

**The physics content of that.** "Continuous reversible transformation between pure
states" is a very operational way of saying "there are gates" — `R_y(θ)` for
infinitesimal `θ` moves `|0⟩` continuously toward `|1⟩` through genuinely new pure
states (superpositions). Everything quantum computing depends on — interference,
continuous rotations, the whole of gate synthesis — is the physical content of
axiom 5.

**Successors.** Chiribella–D'Ariano–Perinotti (2011) reconstruct quantum theory
from five operational axioms plus **purification** (every mixed state is the
marginal of a pure state of a larger system, essentially uniquely) — with
purification doing the distinguishing work that continuity does for Hardy.
Information-causality (Pawłowski et al.) and exclusivity principles instead try to
single out the `2√2` Tsirelson bound directly. The shared goal is to answer *why*
nature is quantum rather than merely classical-probabilistic or
super-quantum — and the recurring answer is that quantum theory is the unique
theory with a continuous, purifiable, locally-tomographic state space.

</details>


---

## Module 6 — Quantum Reference Frames and Relativity

**Objective:** Understand how quantum mechanics interfaces with special relativity and the role of reference frames in quantum theory.

| Topic | Key Concepts |
|---|---|
| Relativistic QM | Dirac equation; Klein-Gordon equation |
| Quantum field theory (QFT) | Particles as excitations of fields; the correct fundamental theory |
| Lorentz covariance | Physical laws must be the same in all inertial frames |
| Quantum nonlocality vs relativity | Entanglement is nonlocal but cannot signal — consistent with relativity |
| Quantum reference frames | Quantizing the reference frame itself |
| Unruh effect | Accelerating observer sees thermal radiation in vacuum |

**Quantum computing relevance:**
- Relativistic effects matter for satellite-based quantum communication
- QFT is the target for quantum simulation of particle physics
- Understanding causal structure is relevant to quantum causal models and process matrices

**Exercises:**
- Show that quantum teleportation does not allow faster-than-light signaling

<details><summary>Solution</summary>

**The specific worry.** Alice's Bell measurement instantaneously "changes" Bob's
qubit from half a Bell pair to `X^{m₁}Z^{m₀}|ψ⟩`. If Bob could detect that change,
he would learn something the moment Alice acted — superluminally.

**Direct computation.** Before Bob applies any correction (and before he knows
Alice's outcome), his state is the average over Alice's four equally likely
outcomes:

```
ρ_Bob = ¼( |ψ⟩⟨ψ| + Z|ψ⟩⟨ψ|Z + X|ψ⟩⟨ψ|X + XZ|ψ⟩⟨ψ|ZX ) = I/2
```

The uniform Pauli twirl of *any* qubit state is the maximally mixed state.
Verified numerically for four different inputs — `|0⟩`, `|1⟩`, `|+⟩` and a random
state — every time:

```
ρ_Bob = [[0.5, 0], [0, 0.5]]
```

Bob's local statistics are literally independent of `|ψ⟩`: whatever measurement he
performs, he gets `50/50`. He learns nothing until the two classical bits arrive
at, at best, the speed of light — and those bits are what turn his maximally mixed
qubit into `|ψ⟩`.

**The general theorem (no-signalling).** Nothing about teleportation is special.
Let `ρ_AB` be any shared state and let Alice apply any local operation — a unitary,
a measurement, a full CPTP map `E_A` — possibly discarding the outcome. Since `E_A`
is **trace preserving**:

```
Tr_A[(E_A ⊗ I)(ρ_AB)] = Tr_A[ρ_AB] = ρ_B
```

Bob's reduced state is unchanged, so no local measurement on B can reveal anything
about what Alice did. Conversely, if Alice *post-selects* on an outcome, Bob's
conditional state does change — but post-selection requires telling him which runs
to keep, which is a classical message.

**The right way to describe what happened.** Entanglement creates correlations that
cannot be explained by pre-existing local values (Bell), yet those correlations are
only *visible* when the two records are brought together. Quantum mechanics is
**non-local in the Bell sense** (no local hidden-variable model) but **no-signalling**
at the operational level. Special relativity forbids superluminal *signalling*, not
superluminal *correlation*, and quantum theory threads that needle exactly.

**Checks on the reasoning.** (i) Bob cannot substitute cloning for the classical
bits — copying his half to measure it twice is forbidden by no-cloning. (ii) He
cannot detect "collapse" by interference, because he does not hold the other half.
(iii) Teleportation does not copy: qubit 1's state is destroyed at the Bell
measurement, consistent with both no-cloning and relativity.

</details>

- Explain why the Dirac equation predicts antiparticles

<details><summary>Solution</summary>

**The construction.** Dirac wanted a relativistic wave equation that is **first
order in time** (so that `|ψ|²` is a positive conserved density, unlike the
Klein–Gordon equation) and Lorentz covariant. First order in `∂_t` plus covariance
forces first order in `∂_x` too:

```
(iγ^μ ∂_μ − m)ψ = 0 ,   {γ^μ, γ^ν} = 2g^{μν}
```

The anticommutation relation is required so that squaring the operator returns the
relativistic dispersion relation, `(□ + m²)ψ = 0`. It cannot be satisfied by
numbers, only by matrices — minimally `4×4` — so `ψ` must have **four** components.

**Where the extra solutions come from.** Two of the four components describe the
two spin states of the electron; the other two solve the same equation with

```
E = −√(p²c² + m²c⁴)
```

The negative-energy branch is not removable: the dispersion relation `E² = p² + m²`
has two roots, and a first-order equation keeps both as independent solutions. A
spectrum unbounded below would be a catastrophe — every electron could cascade
downward forever, radiating infinite energy.

**Dirac's first answer (1930): the sea.** Postulate that all negative-energy states
are filled; the Pauli exclusion principle then blocks the cascade. A *hole* in the
sea — an absent electron of charge `−e` and energy `−E` — behaves as a present
particle of charge `+e` and energy `+E`: an antiparticle with the same mass and
opposite charge. Dirac initially hoped the hole was the proton; Weyl showed the
masses must be equal, and Anderson found the positron in cloud-chamber tracks in
1932.

**The modern answer (Stückelberg–Feynman, then QFT).** The sea is unnecessary (and
useless for bosons, which have no exclusion principle). In quantum field theory the
Dirac field operator is

```
ψ(x) = Σ_s ∫ d³p [ b_{p,s} u_s(p) e^{−ipx} + d†_{p,s} v_s(p) e^{+ipx} ]
```

The negative-frequency modes are reinterpreted as **creation** operators `d†` for
antiparticles rather than negative-energy states of particles; the Hamiltonian is
then positive-definite. Crucially, both terms must appear with these relative
weights for the field to satisfy **microcausality**:

```
{ψ(x), ψ̄(y)} = 0  for spacelike separation (x − y)² < 0
```

The particle and antiparticle contributions cancel exactly outside the light cone.
So antiparticles are not an artefact of one equation — they are *required* by the
combination of **relativity + quantum mechanics + locality**. The same logic gives
the spin-statistics theorem and CPT; Feynman's picture of an antiparticle as a
particle propagating backward in time is the same statement in the propagator
language.

**Why a quantum computing student should care.** Simulating fermionic quantum field
theories (lattice QCD, the Schwinger model) is a flagship application of quantum
simulation, and mapping Dirac fermions onto qubits (Jordan–Wigner, Bravyi–Kitaev)
means encoding exactly these particle/antiparticle mode operators.

</details>

- Describe how the quantum Zeno effect relates to measurement frequency

<details><summary>Solution</summary>

**The short-time law.** For a state `|ψ⟩` evolving under `H`, the survival
probability is *quadratic*, not exponential, at short times:

```
P(t) = |⟨ψ|e^{−iHt/ħ}|ψ⟩|² = 1 − (ΔH)²t²/ħ² + O(t⁴),   (ΔH)² = ⟨H²⟩ − ⟨H⟩²
```

Quadratic decay is the whole mechanism: `1 − εt²` repeated `n` times with `t → t/n`
gives `1 − εt²/n`, which tends to 1, whereas exponential decay `e^{−Γt}` would be
untouched by interruption.

**The Zeno argument.** Measure "is the system still in `|ψ⟩`?" `n` times during a
total time `t`. Each interval contributes `P(t/n) ≈ 1 − (ΔH)²t²/(n²ħ²)`, and
projections reset the clock, so

```
P_survive(n) = [P(t/n)]ⁿ ≈ 1 − (ΔH)²t²/(nħ²)  →  1   as n → ∞
```

**Concrete numbers (Rabi oscillation, `P(t) = cos²(gt)` with `g = 1`, `t = 1`):**

```
n =    1 : survival = 0.2919      (1 − g²t²/n = 0.000)
n =    2 : survival = 0.5931      (0.500)
n =    5 : survival = 0.8176      (0.800)
n =   10 : survival = 0.9047      (0.900)
n =  100 : survival = 0.9901      (0.990)
n = 1000 : survival = 0.9990      (0.999)
```

Computed as `cos^{2n}(gt/n)` — the convergence to the `1 − g²t²/n` asymptote is
visible from `n = 10` onward. "A watched quantum pot never boils."

**The essential caveats.**

1. **The quadratic regime must be reachable.** Real decay into a continuum is
   quadratic only for `t < τ_Z ≈ ħ/ΔH`, set by the *bandwidth* of the environment
   (for spontaneous emission, `τ_Z` is femtoseconds or shorter). Measuring more
   slowly than that lands in the exponential regime, where interruption does
   nothing. This is why the Zeno effect is routine for engineered two-level
   oscillations (Itano et al. 1990, trapped ions) and essentially impossible for
   natural radioactive decay.
2. **The anti-Zeno effect.** At intermediate measurement rates, repeated
   measurement can *accelerate* decay, because the projections broaden the state's
   energy spread into regions of higher environmental density of states. Whether
   you get Zeno or anti-Zeno depends on the overlap of the measurement-broadened
   line with the environment's spectral density.
3. **Measurement need not mean an observer.** Any strong coupling that continuously
   resolves the pointer basis does the job — the "measurement" can be a laser, a
   detector, or an engineered dissipator.

**Connections in this suite.** Zeno dynamics can confine evolution to a subspace —
the basis of Zeno-based error suppression and of dissipative state engineering. QEC
does something adjacent: frequent stabilizer measurement projects the state back
into the code space before errors can accumulate coherently, which is why syndrome
extraction is repeated every cycle rather than at the end (and is exactly the
opposite of deferring measurement). And the same projective formalism underlies
interaction-free measurement and counterfactual computation.

</details>


---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| *Quantum Theory and Measurement* — Wheeler & Zurek (eds.) | Book | Original papers on foundations |
| *The Fabric of Reality* — Deutsch | Book | Many-Worlds, by its foremost proponent |
| *Quantum Theory Cannot Hurt You* — Vedral | Book | Accessible, covers QM and relativity |
| *Something Deeply Hidden* — Carroll | Book | Modern Many-Worlds account |
| Bell's 1964 paper "On the Einstein-Podolsky-Rosen Paradox" | Paper | Original Bell theorem |
| Zurek's papers on decoherence and einselection | Papers | Definitive reference on decoherence |
| Hardy (2001) "Quantum Theory From Five Reasonable Axioms" | Paper | Information-theoretic reconstruction |

---

## Progression Checkpoints

- [ ] Clearly articulate the measurement problem without using the word "collapse" carelessly
- [ ] Derive the CHSH inequality and compute the quantum violation for a Bell state
- [ ] Distinguish between decoherence and collapse and explain what decoherence does and does not resolve
- [ ] Prove the no-cloning theorem
- [ ] State and explain at least two axiomatic reconstructions of quantum mechanics
- [ ] Explain why Bell's theorem rules out local hidden variables without ruling out non-local ones
