"""Problem: alg_simon — Simon's problem and its classical hardness."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="alg_simon",
    topic="Algorithms",
    title="Simon's Problem: Quantum Reduction to Linear Algebra",
    statement=(
        "Simon's problem: given oracle access to f : {0,1}ⁿ → {0,1}ⁿ promised to "
        "satisfy f(x) = f(y) ⇔ y = x or y = x⊕s for a hidden nonzero string s, find s. "
        "The quantum subroutine: prepare Σₓ|x⟩|0⟩/√2ⁿ, query f, measure the output "
        "register, then apply H^⊗n to the input register and measure, obtaining a "
        "string y. (Here a·b denotes the mod-2 inner product Σᵢaᵢbᵢ mod 2.)"
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "After measuring the output register with result f(x₀), the input "
                "register collapses to (|x₀⟩ + |x₀⊕s⟩)/√2. Apply H^⊗n and show that the "
                "amplitude of outcome y is nonzero only if y·s = 0 (mod 2)."
            ),
            points=4,
            rubric=[
                "Uses H^⊗n|x⟩ = (1/√2ⁿ) Σ_y (−1)^{x·y}|y⟩.",
                "Amplitude of y: [(−1)^{x₀·y} + (−1)^{(x₀⊕s)·y}] / √(2^{n+1}); factors "
                "out (−1)^{x₀·y}(1 + (−1)^{s·y}) using (x₀⊕s)·y = x₀·y ⊕ s·y.",
                "Concludes: amplitude vanishes when s·y = 1 and is ±1/√(2^{n−1}) when "
                "s·y = 0 — measured y always satisfies y·s = 0.",
            ],
            model_solution=(
                "H^⊗n[(|x₀⟩ + |x₀⊕s⟩)/√2] = (1/√(2^{n+1})) Σ_y [(−1)^{x₀·y} + "
                "(−1)^{(x₀⊕s)·y}] |y⟩. Since (x₀⊕s)·y ≡ x₀·y + s·y (mod 2), the bracket "
                "is (−1)^{x₀·y}[1 + (−1)^{s·y}]: it equals ±2 if s·y = 0 and 0 if "
                "s·y = 1. So only strings orthogonal (mod 2) to s appear "
                "(verified numerically for n = 3, s = 101)."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Show the measured y is uniformly distributed over the subspace "
                "s^⊥ = {y : y·s = 0}, which has 2^{n−1} elements. How many runs of the "
                "subroutine are needed (in expectation / with constant success "
                "probability) to determine s, and what classical post-processing "
                "finishes the job?"
            ),
            points=3,
            rubric=[
                "Probability of each y with y·s = 0 is |±2/√(2^{n+1})|² = 2^{−(n−1)}, "
                "uniform over the 2^{n−1} elements of s^⊥ (s ≠ 0 makes y·s = 0 a "
                "hyperplane of dimension n−1).",
                "Need n−1 linearly independent y's; each new uniform sample is "
                "independent of the span so far with probability ≥ 1/2, so O(n) runs "
                "suffice with constant success probability (expected ≈ n + O(1)).",
                "Post-processing: solve the linear system y⁽ⁱ⁾·s = 0 over GF(2) "
                "(Gaussian elimination) — the solution space is {0, s}; verify s with "
                "one query check f(0) = f(s).",
            ],
            model_solution=(
                "From (a) each y ∈ s^⊥ has amplitude ±√2/√(2^{n+1}) = ±2^{−(n−1)/2}, so "
                "probability 2^{−(n−1)}, independent of y: uniform on s^⊥, a dimension-"
                "(n−1) subspace with 2^{n−1} elements.\n"
                "Collect samples y⁽¹⁾, y⁽²⁾, …. If the current span has dimension "
                "d < n−1, a fresh uniform sample lies outside it with probability "
                "1 − 2^{d−(n−1)} ≥ 1/2, so on average at most 2 samples per new "
                "dimension: expected O(n) runs (a more careful bound: n − 1 + O(1) "
                "expected samples; with cn runs the success probability is "
                "1 − 2^{−Ω(n)}).\n"
                "Then solve the homogeneous linear system {y⁽ⁱ⁾·s = 0} over GF(2) by "
                "Gaussian elimination. With n−1 independent equations the solution space "
                "is exactly {0, s}, and the nonzero solution is s (confirm with one "
                "evaluation: f(0) = f(s))."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Sketch why any classical algorithm needs exponentially many queries: "
                "show that a deterministic-or-randomised classical algorithm making q "
                "queries can identify s (or even distinguish the promise from a random "
                "1-to-1 function) only if it finds a collision, and bound the collision "
                "probability to conclude q = Ω(2^{n/2}) queries are required."
            ),
            points=3,
            rubric=[
                "Key observation: distinct queries x₁,…,x_q reveal nothing about s "
                "unless two of them collide (f(xᵢ) = f(xⱼ), i.e. xᵢ⊕xⱼ = s); without a "
                "collision, the answers are consistent with (exponentially) many "
                "candidate s values / with a random injective f.",
                "Counting/probability bound: q queries produce at most C(q,2) ≈ q²/2 "
                "pairwise XORs; for s chosen uniformly among 2ⁿ−1 values, the chance any "
                "pair hits s is ≤ q²/2 / (2ⁿ − q²-ish) = O(q²/2ⁿ).",
                "Conclusion: constant success needs q²/2ⁿ = Ω(1), i.e. q = Ω(2^{n/2}); "
                "contrast with the quantum O(n) query cost (exponential separation).",
            ],
            model_solution=(
                "Classically, all information about s comes from observed equalities "
                "among f-values: seeing f(xᵢ) = f(xⱼ) reveals s = xᵢ⊕xⱼ, while seeing "
                "all-distinct values only rules out the candidates {xᵢ⊕xⱼ}. After q "
                "queries there are at most q(q−1)/2 ruled-out candidates, so if s is "
                "uniform over the 2ⁿ − 1 nonzero strings, the probability a collision "
                "was seen is at most [q(q−1)/2]/(2ⁿ − 1 − (excluded)) = O(q²/2ⁿ) "
                "(a birthday-style bound; the same bound shows the promise instance is "
                "indistinguishable from a random 1-to-1 function). For success "
                "probability bounded below by a constant we need q² = Ω(2ⁿ), i.e. "
                "q = Ω(2^{n/2}). Simon's quantum algorithm uses O(n) queries plus "
                "poly(n) classical processing — an exponential oracle separation, and "
                "the inspiration for Shor's period finding."
            ),
        ),
    ],
)
