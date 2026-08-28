"""Derivation: Grover's optimal iteration count."""
from __future__ import annotations
from core.models import Derivation, Step

DERIVATION = Derivation(
    id="deriv_grover_count",
    title="Grover's Optimal Iteration Count",
    goal=(
        "Derive the number of Grover iterations that maximises the success "
        "probability, R ≈ (π/4)√(N/M), from the rotation picture."
    ),
    steps=[
        Step(
            step_id="s1",
            prompt=(
                "Define the two-dimensional stage: with M marked items out of N, "
                "introduce normalised states |β⟩ (marked) and |α⟩ (unmarked), and "
                "express the uniform superposition |s⟩ in terms of them. What angle "
                "parametrises the decomposition?"
            ),
            expected=(
                "|β⟩ = (1/√M)Σ_{marked}|x⟩, |α⟩ = (1/√(N−M))Σ_{unmarked}|x⟩; "
                "|s⟩ = cosθ|α⟩ + sinθ|β⟩ with sinθ = √(M/N) (so cosθ = √((N−M)/N)). "
                "The essential content: |s⟩ lies in the plane spanned by |α⟩, |β⟩ at "
                "angle θ = arcsin√(M/N) from |α⟩."
            ),
            hint=(
                "Split the sum Σ_x|x⟩/√N into its marked and unmarked pieces and "
                "normalise each piece separately."
            ),
            model_step=(
                "Write |s⟩ = (1/√N)Σ_x|x⟩ = √(M/N)·(1/√M)Σ_{marked}|x⟩ + "
                "√((N−M)/N)·(1/√(N−M))Σ_{unmarked}|x⟩ = sinθ|β⟩ + cosθ|α⟩, where "
                "sinθ = √(M/N). All of Grover's dynamics happens in the 2D plane "
                "span{|α⟩, |β⟩}, with the initial state at angle θ above the |α⟩ axis."
            ),
        ),
        Step(
            step_id="s2",
            prompt=(
                "Show that the oracle O (which flips the sign of marked states) acts on "
                "this plane as a reflection. About which axis?"
            ),
            expected=(
                "O|α⟩ = |α⟩ and O|β⟩ = −|β⟩ (marked components change sign), so within "
                "the plane O is the reflection about the |α⟩ axis. Must identify both "
                "the invariance of |α⟩ and the sign flip of |β⟩."
            ),
            hint=(
                "Apply O to each basis vector of the plane: which one is built from "
                "marked strings?"
            ),
            model_step=(
                "The oracle maps |x⟩ → −|x⟩ for marked x and fixes unmarked x. Hence "
                "O|β⟩ = −|β⟩ and O|α⟩ = |α⟩: restricted to the plane, "
                "O = reflection about the |α⟩ axis. (Geometrically it flips the "
                "component along |β⟩.)"
            ),
        ),
        Step(
            step_id="s3",
            prompt=(
                "Show the diffusion operator D = 2|s⟩⟨s| − I is also a reflection. "
                "About which axis, and why does D preserve the plane?"
            ),
            expected=(
                "D fixes |s⟩ (D|s⟩ = |s⟩) and negates every vector orthogonal to |s⟩ "
                "(D|s^⊥⟩ = −|s^⊥⟩): it is the reflection about the |s⟩ axis. It "
                "preserves the plane because |s⟩ lies in the plane, so 2|s⟩⟨s| − I maps "
                "plane vectors to plane vectors."
            ),
            hint=(
                "Evaluate D on |s⟩ and on any vector orthogonal to |s⟩. What are the "
                "eigenvalues?"
            ),
            model_step=(
                "D|s⟩ = 2|s⟩⟨s|s⟩ − |s⟩ = |s⟩, and for ⟨s|v⟩ = 0, D|v⟩ = −|v⟩: D has "
                "eigenvalue +1 along |s⟩ and −1 on its orthocomplement — a reflection "
                "about |s⟩ ('inversion about the mean'). Since |s⟩ ∈ span{|α⟩,|β⟩}, D "
                "maps the plane to itself, acting there as the 2D reflection about the "
                "line of |s⟩."
            ),
        ),
        Step(
            step_id="s4",
            prompt=(
                "The Grover iterate is G = D·O: a composition of two reflections. What "
                "is the composition of two reflections in a plane, and what specific "
                "transformation is G here?"
            ),
            expected=(
                "Two reflections compose to a rotation by twice the angle between the "
                "mirror lines. The mirrors |α⟩ and |s⟩ are separated by θ, so G rotates "
                "the plane by 2θ, in the sense carrying |α⟩ toward |β⟩ — each iteration "
                "moves the state 2θ closer to the marked axis."
            ),
            hint=(
                "A classical geometry fact: reflect in line 1, then line 2 — the result "
                "is a rotation by 2× the angle between the lines."
            ),
            model_step=(
                "Reflection about |α⟩ followed by reflection about |s⟩ is a rotation by "
                "2·(angle between the mirrors) = 2θ, oriented from |α⟩ toward |s⟩ and "
                "beyond. In the (|α⟩,|β⟩) basis, G = [[cos2θ, −sin2θ],[sin2θ, cos2θ]]. "
                "So Grover's algorithm is nothing but a rotation cranked 2θ per oracle "
                "call — amplitude amplification made literal."
            ),
        ),
        Step(
            step_id="s5",
            prompt=(
                "Starting from |s⟩ at angle θ, write the state and the success "
                "probability after k iterations."
            ),
            expected=(
                "After k iterations the state sits at angle (2k+1)θ: "
                "|ψ_k⟩ = cos((2k+1)θ)|α⟩ + sin((2k+1)θ)|β⟩, and measuring hits a "
                "marked item with probability P(k) = sin²((2k+1)θ)."
            ),
            hint=(
                "Initial angle θ; each G adds 2θ. What is the |β⟩ amplitude at angle "
                "ψ?"
            ),
            model_step=(
                "|ψ_k⟩ = G^k|s⟩ is at angle θ + k·2θ = (2k+1)θ from |α⟩:\n"
                "|ψ_k⟩ = cos((2k+1)θ)|α⟩ + sin((2k+1)θ)|β⟩.\n"
                "The probability of measuring some marked item is the squared |β⟩ "
                "amplitude: P(k) = sin²((2k+1)θ) (verified numerically for N = 8: the "
                "amplitude after k iterations equals sin((2k+1)θ) exactly)."
            ),
        ),
        Step(
            step_id="s6",
            prompt=(
                "Maximise P(k): derive the optimal integer k, the asymptotic count "
                "R ≈ (π/4)√(N/M) for M ≪ N, and explain why running MORE iterations "
                "than R makes things worse."
            ),
            expected=(
                "Set (2k+1)θ ≈ π/2 ⇒ k ≈ π/(4θ) − 1/2; optimal integer "
                "R = round(π/(4θ) − 1/2). For M ≪ N, θ ≈ √(M/N) gives "
                "R ≈ (π/4)√(N/M). Overshooting: the rotation continues past |β⟩, so "
                "P(k) = sin²((2k+1)θ) decreases after the peak — the algorithm is "
                "periodic, not monotone."
            ),
            hint=(
                "sin² is maximal when its argument is π/2. And what happens to a "
                "rotation that keeps rotating?"
            ),
            model_step=(
                "P(k) is maximal when (2k+1)θ is closest to π/2, giving "
                "R = round(π/(4θ) − 1/2); with θ ≈ sinθ = √(M/N) for M ≪ N, "
                "R ≈ (π/4)√(N/M) oracle calls — the quadratic speedup over classical "
                "Θ(N/M). Because G is a fixed rotation, iterating past R rotates the "
                "state beyond |β⟩ and the success probability falls back down "
                "(returning near |α⟩ after ~π/θ steps): Grover search must be stopped "
                "at the right time, unlike classical search which only improves with "
                "more queries."
            ),
        ),
    ],
)
