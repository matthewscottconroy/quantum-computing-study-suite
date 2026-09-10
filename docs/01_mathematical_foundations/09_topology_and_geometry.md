# Topology and Geometry for Quantum Computing

> **Prerequisites**: 01_linear_algebra.md (Pauli matrices, spectral theorem), 02_complex_numbers_and_hilbert_spaces.md (global phase, projective space), 04_groups_and_abstract_algebra.md (Lie algebras, exponential map, SU(2) → SO(3) via Ad), 08_analysis_for_quantum_mechanics.md (matrix exponential, Schrödinger equation as an ODE), docs/02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md (Bloch sphere, rotations)  
> **Connects to**: docs/06_variational_quantum_algorithms/03_parameter_shift_gradient.md (Fubini-Study metric and quantum Fisher information), docs/06_variational_quantum_algorithms/07_quantum_optimal_control.md (time-optimal gates, quantum speed limit), docs/03_quantum_gates_and_circuits/04_quantum_circuit_complexity.md (gate-count and depth measures that geodesic length lower-bounds), docs/05_quantum_error_correction/06_surface_code.md (toric code logical qubits), docs/08_advanced_topics/04_topological_quantum_computation.md (braid group, anyons)

## Overview

Linear algebra tells you *what* the state space of a qubit is: unit vectors in `ℂ²` modulo phase. Topology and geometry tell you *what shape* it is — a sphere — and shape has consequences. Because the Bloch sphere is `S²` and not a plane, there is no continuous way to assign a phase to every state at once, and a state dragged slowly around a closed loop comes back with a memory of the loop's area: the Berry phase. Because the rotation group `SO(3)` has a hole in it (a non-contractible loop), a spin-1/2 particle rotated by `2π` picks up a sign, and single-qubit gates are elements of the double cover `SU(2) ≅ S³` rather than of `SO(3)`. Because a torus has two independent holes, the toric code stores exactly two logical qubits. Because exchanging particles in two dimensions is a braid rather than a permutation, anyons exist and can compute.

This chapter surveys the topology and differential geometry behind these facts, keeping each concept tethered to where it is used later in the corpus. It moves from point-set notions (metric and topological spaces, compactness) through homotopy (the fundamental group, covering spaces), the geometry of state space (`CP¹`, the Hopf fibration, the Fubini-Study metric), geometric phases (connections and holonomy), homology (cycles on a torus), the braid group, and finally manifolds and Lie groups. The worked example computes a Berry phase both analytically and by integrating the Schrödinger equation.

## Metric and Topological Spaces

A **metric space** is a set `M` with a distance function `d: M × M → ℝ` satisfying `d(x,y) = 0 ⟺ x = y`, symmetry, and the triangle inequality `d(x,z) ≤ d(x,y) + d(y,z)`. Every normed space is a metric space with `d(x,y) = ‖x - y‖`; the operator norm makes the set of `n × n` matrices one, and gate-approximation statements such as "`‖U - V‖ < ε`" are statements in this metric space.

A **topological space** keeps only the notion of **open sets** (unions and finite intersections of open sets are open) and discards distances. A map `f` is **continuous** if preimages of open sets are open; for metric spaces this is the familiar `ε-δ` definition. The topology is what survives continuous deformation — it is why "the state space is a sphere" is a meaningful statement independent of any particular coordinates.

Two properties recur:

- **Compactness**: every open cover has a finite subcover; in `ℝⁿ` or `ℂⁿ` this is equivalent to closed and bounded (Heine-Borel). The unitary group `U(n)` is compact: it is bounded (`‖U‖ = 1`) and closed (`U†U = I` is a closed condition). Consequences: every sequence of unitaries has a convergent subsequence, continuous functions on `U(n)` attain their extrema, and for every `ε > 0` there is a **finite `ε`-net** of gates covering all of `SU(2)`. That finite net is the base case of the Solovay-Kitaev construction (docs/03, chapter 3).
- **Connectedness**: a space that cannot be split into two disjoint nonempty open sets; **path-connected** if any two points are joined by a continuous path. `U(n)` and `SU(n)` are path-connected because every unitary is `e^{iH}` for some Hermitian `H`, and `t ↦ e^{itH}` is a path from `I` to `U`. By contrast `O(3)` has two components (`det = ±1`): a reflection cannot be reached continuously from the identity, which is why parity is a discrete symmetry.

## Homotopy and the Fundamental Group

Two loops based at a point `x₀` are **homotopic** if one can be continuously deformed into the other. The homotopy classes of loops form a group under concatenation, the **fundamental group** `π₁(M, x₀)`. A space with `π₁ = 0` (every loop contractible) is **simply connected**.

Standard values: `π₁(S¹) = ℤ` (loops are classified by winding number), `π₁(Sⁿ) = 0` for `n ≥ 2`, `π₁(T²) = ℤ × ℤ` (independent windings around the two holes).

**Winding numbers in quantum mechanics.** Because `π₁(S¹) = ℤ`, a wavefunction on a ring must return to itself after one circuit, `ψ(φ + 2π) = ψ(φ)`, which quantizes angular momentum: `ψ ∝ e^{imφ}` with `m ∈ ℤ`. Thread a magnetic flux through the ring and the allowed phases shift by the Aharonov-Bohm phase `e^{iqΦ/ℏ}` — a phase that depends only on the homotopy class (winding number) of the electron's path, not on its shape. The toric code's `-1` phase for carrying an `e` anyon once around an `m` anyon (docs/08_advanced_topics/04_topological_quantum_computation.md) is the same mechanism with `ℤ₂` in place of `U(1)`.

**Why `SO(3)` is not simply connected.** Parametrize a rotation by an axis `n̂` and angle `θ ∈ [0, π]`, i.e. the vector `θn̂` in a solid ball of radius `π`. Rotations by `π` about `n̂` and `-n̂` are the same, so antipodal points of the boundary sphere are identified: `SO(3) ≅ ℝP³` (real projective 3-space). A path from the center to the boundary that reappears at the antipode and returns to the center is a closed loop that cannot be contracted (it crosses the boundary an odd number of times, a homotopy invariant). Traversing it twice *can* be contracted. Hence `π₁(SO(3)) = ℤ₂`. Physically: a `2π` rotation is not deformable to "do nothing", but a `4π` rotation is. This is the **belt trick** (Dirac's string trick): a belt given a full `2π` twist cannot be untwisted by moving the buckle around while keeping both ends fixed, but a `4π` twist can.

**`SU(2)` is the double cover.** Writing `U = [[α, -β*],[β, α*]]` with `|α|² + |β|² = 1` identifies `SU(2)` with the unit sphere `S³ ⊂ ℂ² ≅ ℝ⁴`, which is simply connected. The map

`Φ: SU(2) → SO(3)`,  `Φ(U)ᵢⱼ = ½ Tr(σᵢ U σⱼ U†)`

is a continuous surjective group homomorphism with kernel `{+I, -I}` — a 2-to-1 covering. (This is the adjoint map `Ad(U)` of 04_groups_and_abstract_algebra.md, defined there by `U(n̂·σ)U† = (Ad(U)n̂)·σ`, written out in components; that chapter uses the basis `σ_k/2` for the Lie algebra where this one uses `{iX, iY, iZ}` — the two differ only by real scalars.) `SO(3) = SU(2)/{±I} = S³/(x ∼ -x) = ℝP³`, consistent with the previous paragraph. The non-contractible loop in `SO(3)` (rotation by `2π`) lifts to an *open* path in `SU(2)` from `I` to `-I`: `R_z(2π) = e^{-iπZ} = -I`. A spin-1/2 state therefore acquires the sign `-1` under a `2π` rotation, and it takes `4π` (`e^{-2πiZ} = +I`) to return. This is why single-qubit gates are described by `SU(2)` rather than `SO(3)`: the qubit carries a **projective** representation of the rotation group, which becomes an honest representation only on the simply connected cover.

## The Bloch Sphere as `CP¹` and the Hopf Fibration

A normalized qubit state `(α, β)` is a point of `S³`. Physical states are equivalence classes under global phase, `(α, β) ∼ e^{iχ}(α, β)`, i.e. one-dimensional subspaces of `ℂ²` — points of the **complex projective line** `CP¹`. The map

`h: S³ → S²`,  `h(α, β) = (2 Re(α*β), 2 Im(α*β), |α|² - |β|²)`

is well defined on equivalence classes (each component is invariant under `(α,β) → e^{iχ}(α,β)`) and lands on the unit sphere, since `(2|α||β|)² + (|α|² - |β|²)² = (|α|² + |β|²)² = 1`. For `α = cos(θ/2)`, `β = e^{iφ} sin(θ/2)` it returns `(sin θ cos φ, sin θ sin φ, cos θ)` — the Bloch vector `⟨σ⟩`. This is the **Hopf fibration**: `S³` is a bundle over `S² = CP¹` whose fiber over each point is a circle `S¹ ≅ U(1)`, the set of global phases of that state.

The bundle is **non-trivial**: `S³` is not `S² × S¹` (their fundamental groups differ, `0` versus `ℤ`). Concretely, there is no continuous choice of a representative `(α, β)` for every point of the Bloch sphere — the standard choice `(cos(θ/2), e^{iφ} sin(θ/2))` is ill-defined at the south pole, where `φ` is meaningless but the phase `e^{iφ}` is not. This failure is the geometric root of the Berry phase below: a phase convention is a *local* gauge choice, and the curvature of the bundle is what remains gauge-invariant.

## Projective Hilbert Space and the Fubini-Study Metric

For a `d`-dimensional Hilbert space the space of physical states is `CP^{d-1}`, of real dimension `2d - 2` (for `n` qubits: `2^{n+1} - 2`, not the `2^{n+1}` real parameters of the raw amplitudes). It carries a natural Riemannian metric, the **Fubini-Study metric**, defined for an infinitesimal change `|ψ⟩ → |ψ⟩ + |dψ⟩` by

`ds²_FS = ⟨dψ|dψ⟩ - |⟨ψ|dψ⟩|²`

The subtracted term removes the component of `|dψ⟩` along `|ψ⟩` itself (change of phase and normalization), so `ds²` depends only on the ray. The geodesic distance between two rays is

`d_FS(ψ, φ) = arccos |⟨ψ|φ⟩|`

ranging from `0` (same state) to `π/2` (orthogonal states). On the Bloch sphere `ds²_FS = ¼(dθ² + sin²θ dφ²)`: the Fubini-Study metric is the round metric on a sphere of radius `1/2`, and orthogonal states (antipodal points, Bloch angle `π`) are at Fubini-Study distance `π/2`.

For a family of states `|ψ(θ)⟩` depending on parameters `θ = (θ₁, ..., θₘ)`, pulling the metric back gives the tensor `gᵢⱼ = Re[⟨∂ᵢψ|∂ⱼψ⟩ - ⟨∂ᵢψ|ψ⟩⟨ψ|∂ⱼψ⟩]`. The **quantum Fisher information matrix** of docs/06_variational_quantum_algorithms/03_parameter_shift_gradient.md is exactly `F = 4g`. For mixed states the role of `d_FS` is played by the **Bures distance** `d_B(ρ, σ)² = 2(1 - √F(ρ,σ))`, with `F` the Uhlmann fidelity of docs/02_quantum_mechanics/10_distance_measures_and_lindblad.md; for pure states `√F = |⟨ψ|φ⟩|` and the Bures metric reduces to the Fubini-Study metric, and in general `ds_B² = ¼ F_Q dθ²` — the QFI is four times the Bures metric, exactly as it is four times the Fubini-Study metric. The quantum natural gradient therefore follows the steepest descent direction as measured by the actual geometry of state space rather than by Euclidean parameter distance, and the Cramér-Rao bound `Var(θ̂) ≥ 1/F` says that a parameter can be estimated precisely only if it moves the state a large Fubini-Study distance.

## Geometric (Berry) Phase

Let `H(R)` depend on slowly varying parameters `R(t)`, with a non-degenerate eigenstate `|n(R)⟩`, `H(R)|n(R)⟩ = Eₙ(R)|n(R)⟩`. The **adiabatic theorem** says a system starting in `|n(R(0))⟩` stays in the instantaneous eigenstate, up to a phase. Substituting `|ψ(t)⟩ = e^{iγ(t)} e^{-i∫₀ᵗ Eₙ dt'/ℏ} |n(R(t))⟩` into the Schrödinger equation and projecting onto `⟨n|` gives

`dγ/dt = i ⟨n|∂ₜ n⟩ = i ⟨n|∇_R n⟩ · dR/dt`

Define the **Berry connection** `A(R) = i⟨n(R)|∇_R n(R)⟩` (real, because `⟨n|n⟩ = 1` implies `⟨n|∇n⟩` is imaginary). Around a closed loop `C` in parameter space the accumulated **Berry phase** is

`γ = ∮_C A · dR`

Under a change of phase convention `|n⟩ → e^{iχ(R)}|n⟩` the connection shifts by `A → A - ∇χ`, but the loop integral changes by `-∮∇χ · dR = 0` (mod `2π` if `χ` winds): `γ` is **gauge invariant** and hence physical. This is **parallel transport**: the condition `⟨n|dn⟩ = 0` transports the state with no local phase change, and the mismatch after a closed loop — the **holonomy** — is `e^{iγ}`. By Stokes' theorem `γ = ∫∫_S F · dS` where `F = ∇ × A` is the **Berry curvature**, the gauge-invariant field strength.

**Spin-1/2 in a magnetic field.** For `H = -(B/2) n̂·σ` (`ℏ = 1`) with `n̂ = (sin θ cos φ, sin θ sin φ, cos θ)` the ground state is `|n̂⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩`. The curvature is that of a **magnetic monopole** of charge `-1/2` at the origin of `B`-space: `F = -R̂/(2R²)`. Hence for any closed loop

`γ = -½ Ω(C)`

where `Ω(C)` is the solid angle the loop subtends at the origin. The phase is independent of the speed, the field strength, and the loop's shape — only the enclosed solid angle matters. Since the excited state `|-n̂⟩` acquires `+Ω/2`, the loop implements the relative phase `e^{-iΩ}` between the two eigenstates of `n̂·σ`: a rotation about `n̂` by angle `Ω`. This is a **geometric gate** — its angle is set by an area, and it is insensitive to noise that perturbs the path without changing the enclosed solid angle, which is the motivation for holonomic quantum computation.

**Beyond adiabaticity.** Adiabaticity is convenient but not essential. Aharonov and Anandan showed that *any* cyclic evolution of a state — one whose ray returns to itself, `|ψ(T)⟩ = e^{iα}|ψ(0)⟩` — splits the total phase `α` into a dynamical part `-∫⟨ψ|H|ψ⟩dt/ℏ` and a geometric part equal to `-Ω/2`, where `Ω` is now the solid angle enclosed by the state's own trajectory on the Bloch sphere. A fast `2π` Rabi rotation about a tilted axis is a cyclic evolution, and its geometric phase can be read off from the cone the Bloch vector traces; this is how geometric phase gates are implemented in superconducting and trapped-ion hardware without waiting for an adiabatic ramp.

## Homology: Cycles, Boundaries, and the Toric Code

Homology counts holes by linear algebra over a field, here `ℤ₂ = {0, 1}`. Draw a graph on a surface: vertices `V`, edges `E`, faces `F`. A **1-chain** is a subset of edges (a vector in `ℤ₂^E`); the **boundary** `∂₁` sends an edge to its two endpoints, and `∂₂` sends a face to the edges around it. The key identity is `∂₁∂₂ = 0`: the boundary of a boundary is empty. A 1-chain with `∂₁c = 0` is a **cycle** (every vertex touched an even number of times — a closed loop); a chain of the form `∂₂f` is a **boundary** (a loop that encloses a region). The first homology group

`H₁ = Z₁/B₁ = ker ∂₁ / im ∂₂`

consists of cycles that are not boundaries — loops that wind around holes. On a sphere `H₁ = 0`; on a torus `H₁ = ℤ₂²` (one class for each of the two independent ways to wind around), and on a genus-`g` surface `H₁ = ℤ₂^{2g}`.

**The toric code is homology made physical** (docs/05_quantum_error_correction/06_surface_code.md, docs/08_advanced_topics/04_topological_quantum_computation.md). Put a qubit on every edge of an `L × L` lattice on a torus. A `Z`-type Pauli string is a 1-chain; it commutes with all vertex stabilizers iff it is a cycle, and it is a product of plaquette stabilizers iff it is a boundary. The non-trivial logical `Z` operators are therefore the elements of `H₁ = ℤ₂²`: two independent classes, so the code has **2 logical qubits**. The counting agrees: `2L²` qubits, `L²` vertex and `L²` plaquette stabilizers with one relation in each family (`Π A_v = I`, `Π B_f = I`), so `2L² - 2` independent stabilizers and `k = 2L² - (2L² - 2) = 2`. The two relations are themselves topological: the Euler characteristic `V - E + F = L² - 2L² + L² = 0 = 2 - 2g` confirms `g = 1`. On a planar patch (`g = 0`) with two rough and two smooth boundaries, relative homology gives `k = 1` instead.

## The Braid Group and Anyons

The **braid group** `B_n` is generated by `σ₁, ..., σ_{n-1}` (`σᵢ` crosses strand `i` over strand `i+1`) subject to

`σᵢσⱼ = σⱼσᵢ` for `|i - j| ≥ 2`,  `σᵢσᵢ₊₁σᵢ = σᵢ₊₁σᵢσᵢ₊₁` (Yang-Baxter relation)

Imposing the extra relation `σᵢ² = 1` (crossing twice is the same as not crossing) yields the **symmetric group** `Sₙ`; the map `B_n → Sₙ` sending each braid to its permutation of endpoints is a surjective homomorphism whose kernel is the pure braid group. Topologically, `B_n` is the fundamental group of the configuration space of `n` indistinguishable points in the plane, whereas for points in three-dimensional space the fundamental group is only `Sₙ` — in 3D any two exchange paths are homotopic, because one strand can be lifted over the other. Note that `B_n` is infinite: `σ₁` has infinite order.

Exchanging identical particles transports the wavefunction around a loop in configuration space, so the quantum state carries a **unitary representation** of that fundamental group. In 3D the only one-dimensional representations of `Sₙ` are the trivial and sign representations: bosons and fermions. In 2D, one-dimensional representations of `B_n` assign `σᵢ ↦ e^{iθ}` for *any* angle `θ` — **Abelian anyons** (the toric code's `e` and `m` particles, with mutual statistics `-1`). Higher-dimensional irreducible representations, acting on a degenerate fusion space, describe **non-Abelian anyons**; the Fibonacci representation in docs/08_advanced_topics/04_topological_quantum_computation.md is a two-dimensional representation of `B₄` (four anyons of total charge `1`) whose image is dense in `U(2)` — i.e. dense in `SU(2)` up to a global phase, which is all a gate needs. Topological quantum computation is the program of using braids as gates, with the topological invariance of the braid class as the error protection.

## Manifolds, Lie Groups, and Geodesic Gates

A **manifold** is a topological space that locally looks like `ℝᵏ` (with smooth coordinate changes); `S²`, `S³`, `T²`, and `CP^{d-1}` are manifolds. A **Lie group** is a group that is also a manifold with smooth multiplication and inversion. The examples that matter for quantum computing are all matrix groups: `U(1) ≅ S¹`, `SU(2) ≅ S³`, `SO(3) ≅ ℝP³`, and `SU(2ⁿ)`, the manifold of `n`-qubit gates, of real dimension `4ⁿ - 1`. The tangent space at the identity is the **Lie algebra**: for `SU(2)` it is `su(2) = span{iX, iY, iZ}` (traceless anti-Hermitian matrices), and the exponential map `su(2) → SU(2)` is the statement that every gate is `e^{-iH}` for a Hamiltonian `H`. A curve `U(t)` in `SU(2ⁿ)` is a gate being executed in time; its velocity `U̇U†` is `-iH(t)`, the instantaneous Hamiltonian.

With the bi-invariant metric `⟨A, B⟩ = ½Tr(A†B)` on the Lie algebra, the geodesics through the identity are the one-parameter subgroups `t ↦ e^{-iHt}`, and the length of the geodesic from `I` to `U` is the norm of the smallest generator of `U`. If the hardware can apply Hamiltonians of bounded strength `‖H‖ ≤ Ω/2` (Rabi frequency `Ω`, i.e. `H = (Ω/2) n̂·σ` as in docs/06 chapter 7), the fastest way to reach `U` is to move along a geodesic at full speed, so gate time equals geodesic length divided by the maximum speed `Ω/2` — time-optimal control is geodesic finding (docs/06_variational_quantum_algorithms/07_quantum_optimal_control.md). For a single qubit driven from `|0⟩` to `|1⟩` the shortest geodesic is `e^{-i(Ω/2)Xt}` with `‖(Ω/2)X‖ = Ω/2`, and it reaches `X` (up to phase) at `T = π/Ω` — the `π`-pulse duration, which saturates the Mandelstam-Tamm quantum speed limit of docs/06 chapter 7. Nielsen's geometric approach to circuit complexity (Nielsen, Dowling, Gu & Doherty 2006, Further Reading 5) uses a *different*, right-invariant metric that penalizes many-body directions in the Lie algebra, so that geodesic length lower-bounds the gate counts and depths studied in docs/03_quantum_gates_and_circuits/04_quantum_circuit_complexity.md.

## Key Formulas

**SU(2) → SO(3) double cover**:
`Φ(U)ᵢⱼ = ½ Tr(σᵢ U σⱼ U†)`,  `ker Φ = {±I}`,  `π₁(SO(3)) = ℤ₂`,  `π₁(SU(2)) = 0`

**Hopf map (Bloch vector)**:
`(α, β) ↦ (2 Re(α*β), 2 Im(α*β), |α|² - |β|²) ∈ S²`

**Fubini-Study metric and distance**:
`ds² = ⟨dψ|dψ⟩ - |⟨ψ|dψ⟩|²`,  `d_FS = arccos|⟨ψ|φ⟩|`,  Bloch sphere: `ds² = ¼(dθ² + sin²θ dφ²)`,  QFI `F = 4g`

**Berry connection, phase, curvature**:
`A = i⟨n|∇n⟩`,  `γ = ∮ A · dR = ∫∫ F · dS`,  spin-1/2 aligned with the field: `γ = -Ω/2`

**Bures distance (mixed states)**:
`d_B(ρ,σ)² = 2(1 - √F(ρ,σ))`,  `ds_B² = ¼ F_Q dθ²`

**Homology**:
`∂₁∂₂ = 0`,  `H₁ = ker ∂₁ / im ∂₂`,  torus: `H₁(T²; ℤ₂) = ℤ₂²` ⟹ `k = 2`

**Braid relations**:
`σᵢσᵢ₊₁σᵢ = σᵢ₊₁σᵢσᵢ₊₁`,  `σᵢσⱼ = σⱼσᵢ (|i-j| ≥ 2)`;  adding `σᵢ² = 1` gives `Sₙ`

**Lie group geometry**:
`T_I SU(2) = su(2) = span{iX, iY, iZ}`,  geodesics through `I`: `t ↦ e^{-iHt}`

## Worked Example

**Problem**: A spin-1/2 is prepared in the ground state of `H = -(B/2) n̂·σ` (`ℏ = 1`) and the field direction `n̂` is carried slowly once around a cone of half-angle `θ` about the `z` axis. Derive the Berry phase, state the sign convention, and verify it numerically for `θ = π/3`.

**Solution**:

Step 1 — Sign convention. We write the adiabatic solution as `|ψ(T)⟩ = e^{iγ} e^{-iET}|n̂(0)⟩` with `E = -B/2` the ground energy, so `γ` is the phase left over after removing the dynamical phase `e^{-iET}`. With this convention `A = i⟨n|∇n⟩` and `γ = ∮A · dR`. (Some texts write `e^{-iγ}` or track the excited state; both flip the sign.)

Step 2 — The connection. Take `|n̂⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩`, which is the `+1` eigenvector of `n̂·σ` and therefore the ground state of `H`. Along the cone only `φ` varies, `φ: 0 → 2π`, and

`∂_φ|n̂⟩ = i e^{iφ} sin(θ/2)|1⟩`,  so  `A_φ = i⟨n̂|∂_φ n̂⟩ = i · (i sin²(θ/2)) = -sin²(θ/2)`

Step 3 — The phase.

`γ = ∫₀^{2π} A_φ dφ = -2π sin²(θ/2) = -π(1 - cos θ)`

The solid angle of a cone of half-angle `θ` is `Ω = 2π(1 - cos θ)`, so `γ = -Ω/2`, as the monopole picture predicts. For `θ = π/3`: `cos θ = 1/2`, `Ω = π`, and `γ = -π/2 ≈ -1.5708`. Check the limits: `θ → 0` gives `γ → 0` (the field barely moves), and `θ = π/2` (equatorial loop) gives `γ = -π`, i.e. the sign flip of a `2π` rotation.

Step 4 — Numerical verification. Set `B = 1`, `n̂(t)` with `φ(t) = 2πt/T`, and integrate the Schrödinger equation from `|ψ(0)⟩ = |n̂(0)⟩` using `200` piecewise-constant steps per unit time, each step an exact `2 × 2` matrix exponential `e^{-iH(φ)Δt}`. At the end compute the overlap `z = ⟨n̂(0)|ψ(T)⟩`; adiabatically `z ≈ e^{i(γ - ET)} = e^{i(γ + T/2)}`, so `γ = arg z - T/2` reduced to `(-π, π]`.

| `T` | `abs(z)` | extracted `γ` | error vs `-π/2` |
|---|---|---|---|
| 50 | 0.99480 | -1.4318 | 0.139 |
| 200 | 0.99972 | -1.5345 | 0.036 |
| 800 | 0.999994 | -1.5616 | 0.0092 |
| 3200 | 0.999999 | -1.5685 | 0.0023 |

Step 5 — Reading the table. `|z| → 1` confirms the adiabatic theorem: the state stays in the instantaneous ground state. The extracted phase converges to `-π/2`, and the error falls by a factor of `4` each time `T` quadruples — the residual is the first non-adiabatic correction, of order `1/(BT)`, and would be different for a different ramp speed while the limit `-π/2` would not. The dynamical phase `-ET = +1600` radians at `T = 3200` is enormous compared with the geometric `-π/2`, which is why an experiment measures Berry phases interferometrically against a reference that shares the dynamical phase (or uses a spin echo to cancel it).

**Key insight**: The Berry phase is a holonomy — the failure of parallel transport around a loop to return the original phase — and for a spin-1/2 it equals minus half the solid angle. The loop in `B`-space could be traversed at any (slow) speed, at any field strength, along any path enclosing the same solid angle, and the answer would be the same `-π/2`. That is what makes it a *geometric* gate.

## Summary

- **Compactness** of `U(n)` guarantees finite `ε`-nets of gates and convergent subsequences; `SU(n)` is **path-connected** because every unitary is an exponential
- `π₁(SO(3)) = ℤ₂` (the `2π` rotation is a non-contractible loop; the belt trick) while `SU(2) ≅ S³` is **simply connected** and **double covers** `SO(3)` with kernel `{±I}`; this is why a `2π` rotation multiplies a qubit by `-1`
- The Bloch sphere is `CP¹ = S²`; the **Hopf fibration** `S³ → S²` has the global phase `U(1)` as its fiber and is non-trivial, so no continuous global phase convention exists
- The **Fubini-Study metric** `ds² = ⟨dψ|dψ⟩ - |⟨ψ|dψ⟩|²` is the natural geometry of projective Hilbert space; the quantum Fisher information is `4g`
- The **Berry phase** `γ = ∮ i⟨n|∇n⟩·dR` is gauge invariant; for a spin-1/2 it is `-Ω/2`, and its loop-shape independence makes holonomic gates robust
- **Homology** `H₁ = ker ∂₁/im ∂₂` counts non-contractible cycles; `H₁(T²; ℤ₂) = ℤ₂²` is why the toric code has **2 logical qubits**
- The **braid group** `B_n` surjects onto `Sₙ` but is infinite; its unitary representations are anyons, and non-Abelian ones can compute
- Lie groups are manifolds; `SU(2) ≅ S³` with Lie algebra `su(2)`, and **geodesics** `e^{-iHt}` are the time-optimal gates under bounded Hamiltonian strength

## Exercises

**Exercise 1**: Compute `U = e^{-iπY/4}` and its image `Φ(U) ∈ SO(3)` under `Φ(U)ᵢⱼ = ½Tr(σᵢUσⱼU†)`. Verify that `Φ(-U) = Φ(U)`, and identify the rotation. Then compute `R_z(2π)` and `R_z(4π)` in `SU(2)`.

<details><summary>Solution</summary>

`e^{-iπY/4} = cos(π/4) I - i sin(π/4) Y = (1/√2)[[1, -1],[1, 1]]`.

Computing the nine traces (e.g. `Φ₁₃ = ½Tr(X U Z U†)`): the result is

`Φ(U) = [[0, 0, 1],[0, 1, 0],[-1, 0, 0]]`

which sends `ẑ ↦ x̂` and `x̂ ↦ -ẑ` while fixing `ŷ`: a rotation by `+π/2` about the `y` axis, as expected for `R_y(π/2)`. Since `Φ` is quadratic in `U` (one `U` and one `U†`), `Φ(-U) = Φ(U)` exactly — both `U` and `-U` describe the same Bloch-sphere rotation.

`R_z(2π) = e^{-iπZ} = cos π I - i sin π Z = -I`, and `R_z(4π) = e^{-2πiZ} = +I`. The loop of rotations by angle `0 → 2π` in `SO(3)` lifts to an open path `I → -I` in `SU(2)`; only the `4π` loop lifts to a closed one.

</details>

**Exercise 2**: For `|ψ(α)⟩ = cos(α/2)|0⟩ + sin(α/2)|1⟩`, compute the Fubini-Study distance from `|0⟩` and the quantum Fisher information for estimating `α`. Then compute the QFI for estimating `φ` in `|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩` at `θ = π/3`. Interpret both with the Bloch sphere.

<details><summary>Solution</summary>

`|⟨0|ψ(α)⟩| = cos(α/2)`, so `d_FS = arccos(cos(α/2)) = α/2`. For `α = π/3`, `d_FS = π/6 ≈ 0.5236`. On the Bloch sphere `α` is the polar angle, and the Fubini-Study sphere has radius `1/2`, so the arc length is `α/2` ✓.

QFI for `α`: `|∂_α ψ⟩ = ½(-sin(α/2), cos(α/2))`, so `⟨∂ψ|∂ψ⟩ = 1/4` and `⟨ψ|∂ψ⟩ = 0`. Hence `g = 1/4` and `F = 4g = 1`, independent of `α` — a meridian is traversed at Fubini-Study speed `1/2` (radius `1/2` times unit angular speed), and the factor `4` in `F = 4g` makes the QFI exactly `1`.

QFI for `φ`: `|∂_φ ψ⟩ = (0, i e^{iφ} sin(θ/2))`, so `⟨∂ψ|∂ψ⟩ = sin²(θ/2)` and `|⟨ψ|∂ψ⟩|² = sin⁴(θ/2)`. Then `g = sin²(θ/2)(1 - sin²(θ/2)) = ¼ sin²θ` and `F = sin²θ`. At `θ = π/3`, `F = 3/4`. This is the `sin²θ dφ²` term of the metric: a circle of latitude at polar angle `θ` has circumference proportional to `sin θ`, so a phase `φ` is most estimable on the equator (`F = 1`) and not at all at the poles (`F = 0`, where `φ` is pure global phase).

</details>

**Exercise 3**: Apply the Hopf map to `(α, β) = e^{iχ}(1, e^{iπ/4})/√2` for several values of `χ`. Which point of the Bloch sphere results, and what is the preimage of that point in `S³`?

<details><summary>Solution</summary>

`α*β = e^{-iχ}e^{iχ} · e^{iπ/4}/2 = e^{iπ/4}/2`, independent of `χ`. So

`h(α, β) = (2 Re(α*β), 2 Im(α*β), |α|² - |β|²) = (cos(π/4), sin(π/4), 0) = (0.7071, 0.7071, 0)`

for every `χ`: the equatorial point at azimuth `π/4`, i.e. the `+1` eigenstate of `(X + Y)/√2`. Its norm is `1` ✓. The preimage `h⁻¹(point)` is the full circle `{e^{iχ}(1, e^{iπ/4})/√2 : χ ∈ [0, 2π)}`, a great circle in `S³` — the `U(1)` fiber of global phases. Every fiber is a great circle and any two fibers are linked once (the Hopf link), which is the geometric meaning of the bundle being non-trivial.

</details>

**Exercise 4**: For the toric code on an `L × L` torus with `L = 3`, count qubits, stabilizer generators, relations, and logical qubits, and explain each number in the language of chains, cycles, and boundaries. What changes on a genus-2 surface?

<details><summary>Solution</summary>

Qubits sit on edges: `E = 2L² = 18`. There are `V = L² = 9` vertex (`X`-type) stabilizers and `F = L² = 9` plaquette (`Z`-type) stabilizers, `18` in total, but the product of all vertex operators is `I` (every edge touches two vertices) and the product of all plaquettes is `I` (every edge borders two faces): two relations, `16` independent generators, and `k = 18 - 16 = 2` logical qubits.

Homologically: `Z`-strings are 1-chains in `ℤ₂^{18}`. Commuting with all vertex checks means the string has even degree at every vertex — it is a **cycle**, `∂₁c = 0`. Being a product of plaquettes means it is a **boundary**, `c = ∂₂f`. The logical `Z` operators are cycles modulo boundaries, `H₁(T²; ℤ₂) = ℤ₂²`: the two non-contractible loops (horizontal and vertical). The two relations among the stabilizers are the statements `H₀ = ℤ₂` (the torus is connected) and `H₂ = ℤ₂` (it is a closed orientable surface); together with `V - E + F = 0 = 2 - 2g` they pin `g = 1`.

On a genus-2 surface `H₁ = ℤ₂⁴`, so the same local stabilizers encode `k = 4` logical qubits; in general `k = 2g`. Nothing about the local check operators changed — the extra logical qubits are entirely a property of the global topology.

</details>

**Exercise 5**: Using the Fibonacci braid matrices of the corpus, `ρ(σ₁) = diag(e^{4πi/5}, e^{-3πi/5})` and `ρ(σ₂) = F ρ(σ₁) F` with `F = [[φ⁻¹, φ^{-1/2}],[φ^{-1/2}, -φ⁻¹]]`, verify the Yang-Baxter relation, show that `ρ(σ₁)` and `ρ(σ₂)` do not commute, and find the order of `ρ(σ₁)`. Why does this show the representation does not factor through `S₃`?

<details><summary>Solution</summary>

`F` is real, symmetric, and `F² = I` (check: `φ⁻² + φ⁻¹ = 1`, the defining identity of the golden ratio). Multiplying out with `φ = 1.618`:

`ρ(σ₂) = [[-0.5000 - 0.3633i, -0.2429 + 0.7477i],[-0.2429 + 0.7477i, -0.6180]]`

Direct multiplication gives `ρ(σ₁)ρ(σ₂)ρ(σ₁) = ρ(σ₂)ρ(σ₁)ρ(σ₂)` to machine precision (both sides are the same unitary), while `ρ(σ₁)ρ(σ₂) ≠ ρ(σ₂)ρ(σ₁)` (`ρ(σ₁)` is diagonal with distinct entries and `ρ(σ₂)` has non-zero off-diagonal elements, so they cannot commute).

Order of `ρ(σ₁)`: its eigenvalues are `e^{4πi/5}` and `e^{-3πi/5}`. The smallest `k` with `4k/5` and `3k/5` both even integers is `k = 10`; indeed `ρ(σ₁)⁵ = diag(1, -1) ≠ I` and `ρ(σ₁)¹⁰ = I`. In `S₃` the image of `σ₁` is a transposition of order `2`; since `ρ(σ₁)² ≠ I`, `ρ` restricted to `⟨σ₁, σ₂⟩ ≅ B₃` does not factor through `B₃ → S₃`. The extra relation `σᵢ² = 1` that distinguishes permutations from braids is exactly what these anyons violate, and the group generated by `ρ(σ₁), ρ(σ₂)` is infinite — dense in `U(2)` (note `det ρ(σ₁) = e^{iπ/5} ≠ 1`, so the image is dense in `SU(2)` only up to global phase), which is why braiding Fibonacci anyons is universal.

</details>

## Further Reading

1. **Nakahara**, *Geometry, Topology and Physics* (2nd ed., IOP), Chapters 4, 9, 10 — homotopy groups, fibre bundles (the Hopf map and the monopole `U(1)` bundle are the worked examples of Chapter 9), connections and holonomy, written for physicists; §10.6 derives Berry's phase, including the spin-1/2 monopole
2. **Bengtsson & Życzkowski**, *Geometry of Quantum States* (2nd ed., Cambridge), Chapters 3, 4 — projective Hilbert space, `CP^{d-1}`, the Fubini-Study metric, and the Hopf fibration, with the quantum Fisher information connection
3. **Berry**, "Quantal phase factors accompanying adiabatic changes", *Proc. R. Soc. A* 392, 45 (1984) — the original paper; short, and the spin-1/2 solid-angle result is worked out in full; **Shapere & Wilczek** (eds.), *Geometric Phases in Physics* collects the follow-ups
4. **Kitaev**, "Fault-tolerant quantum computation by anyons", *Annals of Physics* 303, 2 (2003), §§2-4 — the toric code as `ℤ₂` homology, and anyons as braid-group representations; **Nayak, Simon, Stern, Freedman & Das Sarma**, *Rev. Mod. Phys.* 80, 1083 (2008), §II for braid groups and fusion spaces
5. **Hall**, *Lie Groups, Lie Algebras, and Representations* (Springer GTM 222), Chapters 1 and 3 — matrix Lie groups as manifolds, `SU(2) ≅ S³`, the `SU(2) → SO(3)` covering map, and connectedness of `SU(n)`; **Nielsen, Dowling, Gu & Doherty**, "Quantum computation as geometry", *Science* 311, 1133 (2006) for geodesics and gate complexity
