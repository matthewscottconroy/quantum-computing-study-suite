"""Problem: alg_grover_geometry — Grover's algorithm as a rotation."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="alg_grover_geometry",
    topic="Algorithms",
    title="The Geometry of Grover's Algorithm",
    statement=(
        "Grover search over N items with M marked solutions uses the iterate "
        "G = D·O, where O flips the sign of marked basis states and "
        "D = 2|s⟩⟨s| − I is inversion about the uniform superposition "
        "|s⟩ = (1/√N)Σₓ|x⟩. Define |β⟩ = (1/√M)Σ_{x marked}|x⟩ and "
        "|α⟩ = (1/√(N−M))Σ_{x unmarked}|x⟩."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Show that |s⟩ = cos(θ)|α⟩ + sin(θ)|β⟩ with sin(θ) = √(M/N), and prove "
                "that G acts within span{|α⟩, |β⟩} as a rotation by angle 2θ."
            ),
            points=4,
            rubric=[
                "Decomposes |s⟩ correctly: coefficient of |β⟩ is √(M/N) = sinθ, of |α⟩ "
                "is √((N−M)/N) = cosθ.",
                "Shows O acts on the plane as reflection about |α⟩ "
                "(O|α⟩ = |α⟩, O|β⟩ = −|β⟩), and D = 2|s⟩⟨s| − I as reflection about |s⟩; "
                "both preserve span{|α⟩, |β⟩}.",
                "Uses the composition-of-two-reflections theorem (or explicit 2×2 matrix "
                "computation) to conclude G rotates the plane by 2θ — twice the angle "
                "between the mirror axes |α⟩ and |s⟩ — rotating the state away from |α⟩ "
                "toward |β⟩.",
            ],
            model_solution=(
                "Split the uniform sum over the M marked and N−M unmarked strings:\n"
                "|s⟩ = √((N−M)/N)|α⟩ + √(M/N)|β⟩ ≡ cosθ|α⟩ + sinθ|β⟩, sinθ = √(M/N).\n"
                "The oracle fixes |α⟩ and negates |β⟩: in the (|α⟩,|β⟩) plane it is the "
                "reflection about the |α⟩ axis. D = 2|s⟩⟨s| − I fixes |s⟩ and negates "
                "vectors orthogonal to it: reflection about |s⟩. Both maps send the plane "
                "to itself. The product of two reflections in a plane is a rotation by "
                "twice the angle between the mirror lines; the angle between |α⟩ and |s⟩ "
                "is θ, so G = D·O is a rotation by 2θ (in the direction from |α⟩ toward "
                "|β⟩). Explicitly, in the (|α⟩,|β⟩) basis "
                "G = [[cos2θ, −sin2θ],[sin2θ, cos2θ]]."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Deduce that after k iterations the state is "
                "cos((2k+1)θ)|α⟩ + sin((2k+1)θ)|β⟩, and derive the optimal iteration "
                "count R. Show R ≈ (π/4)√(N/M) for M ≪ N and give the exact "
                "closest-integer expression."
            ),
            points=3,
            rubric=[
                "Initial angle θ plus k rotations of 2θ gives angle (2k+1)θ; success "
                "probability sin²((2k+1)θ).",
                "Sets (2k+1)θ ≈ π/2 ⇒ k ≈ π/(4θ) − 1/2; exact prescription "
                "R = round(π/(4θ) − 1/2) or equivalently R = ⌈arccos(√(M/N))/(2θ)⌉ "
                "(either accepted).",
                "Small-M/N limit: θ ≈ sinθ = √(M/N) gives R ≈ (π/4)√(N/M); notes the "
                "quadratic speedup over classical O(N/M).",
            ],
            model_solution=(
                "|ψ₀⟩ = |s⟩ makes angle θ with |α⟩; each G adds 2θ, so after k iterations "
                "the angle is (2k+1)θ and |ψₖ⟩ = cos((2k+1)θ)|α⟩ + sin((2k+1)θ)|β⟩ "
                "(verified numerically for N = 8). Success probability "
                "P(k) = sin²((2k+1)θ) is maximised when (2k+1)θ is closest to π/2:\n"
                "R = round(π/(4θ) − 1/2)  (equivalently ⌈arccos√(M/N)/(2θ)⌉).\n"
                "For M ≪ N, θ ≈ √(M/N), so R ≈ π/(4√(M/N)) = (π/4)√(N/M): O(√(N/M)) "
                "oracle calls versus Θ(N/M) classically — a quadratic speedup."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Evaluate the case N = 4, M = 1 exactly: compute θ, the optimal number "
                "of iterations, and the exact success probability after that many "
                "iterations. Comment on why this case is special."
            ),
            points=3,
            rubric=[
                "θ = arcsin(√(1/4)) = arcsin(1/2) = π/6.",
                "One iteration: angle becomes 3θ = π/2, success probability "
                "sin²(π/2) = 1 — exact, deterministic success.",
                "Comment: (2k+1)θ hits π/2 exactly only for special N/M ratios; "
                "generically the optimal angle overshoots/undershoots and success "
                "probability is 1 − O(M/N), not exactly 1.",
            ],
            model_solution=(
                "sinθ = √(M/N) = 1/2 ⇒ θ = π/6. After k = 1 iteration the state angle is "
                "3θ = π/2, i.e. the state is exactly |β⟩: success probability "
                "sin²(π/2) = 1 (verified numerically: one Grover iteration on N = 4 maps "
                "the uniform state exactly onto the marked state). R = round(π/(4·π/6) "
                "− 1/2) = round(1) = 1.\n"
                "This case is special because (2k+1)θ = π/2 has an exact integer solution "
                "k = 1. For general N/M, π/(4θ) − 1/2 is not an integer, the final angle "
                "misses π/2 slightly, and the best success probability is "
                "1 − O(M/N) — one then repeats the whole algorithm a few times or uses "
                "amplitude amplification variants for exactness."
            ),
        ),
    ],
)
