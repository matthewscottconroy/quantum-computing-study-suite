"""Problem: circ_universality — universality of {H, T, CNOT}."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="circ_universality",
    topic="Circuits & Gates",
    title="Universality of {H, T, CNOT}",
    statement=(
        "The gate set {H, T, CNOT} is universal for quantum computation: any n-qubit "
        "unitary can be approximated to arbitrary accuracy by circuits over these gates. "
        "This problem walks through the core of the argument (Nielsen & Chuang §4.5). "
        "Recall T = diag(1, e^{iπ/4}) and that, up to global phase, "
        "T = Rz(π/4) = exp(−iπZ/8)."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Show that T is (up to global phase) a rotation Rz(π/4) about the ẑ axis "
                "of the Bloch sphere, and that HTH is (up to the same global phase) a "
                "rotation Rx(π/4) about the x̂ axis."
            ),
            points=3,
            rubric=[
                "Writes T = e^{iπ/8}·diag(e^{−iπ/8}, e^{iπ/8}) = e^{iπ/8} Rz(π/4), "
                "identifying Rz(θ) = exp(−iθZ/2).",
                "Uses HZH = X (or conjugation of the exponential: "
                "H exp(−iθZ/2) H = exp(−iθ HZH/2) = exp(−iθX/2)).",
                "Concludes HTH = e^{iπ/8} Rx(π/4); the global phase is correctly "
                "identified as irrelevant.",
            ],
            model_solution=(
                "T = diag(1, e^{iπ/4}) = e^{iπ/8} diag(e^{−iπ/8}, e^{iπ/8}) "
                "= e^{iπ/8} exp(−i(π/4)Z/2) = e^{iπ/8} Rz(π/4).\n"
                "Since H² = I and HZH = X, conjugating the exponential term by term gives "
                "H exp(−iπZ/8) H = exp(−iπ(HZH)/8) = exp(−iπX/8) = Rx(π/4). Hence "
                "HTH = e^{iπ/8} Rx(π/4): a π/4 rotation about x̂, up to an irrelevant "
                "global phase."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Consider the composite gate THTH ≅ Rz(π/4)Rx(π/4). Show it is a "
                "rotation R_n̂(θ) about some axis n̂ with cos(θ/2) = cos²(π/8), and argue "
                "why θ being an irrational multiple of π implies that repeated "
                "applications generate rotations about n̂ that are dense in [0, 2π)."
            ),
            points=4,
            rubric=[
                "Multiplies Rz(π/4)Rx(π/4) = [cos(π/8)I − i sin(π/8)Z][cos(π/8)I − i sin(π/8)X] "
                "and expands using ZX = iY.",
                "Reads off the identity component: cos(θ/2) = cos²(π/8) (the resulting "
                "axis n̂ ∝ (cos π/8, sin π/8, cos π/8)·sin(π/8)-weighted is a bonus, not "
                "required in detail).",
                "States (may cite without proof) that θ/π is irrational for this value.",
                "Density argument: the angles kθ mod 2π for k = 0,1,2,… are all distinct "
                "when θ/2π is irrational, and an infinite set of distinct points on a "
                "circle has points within any ε — pigeonhole gives a small net rotation "
                "whose multiples fill the circle to within ε.",
            ],
            model_solution=(
                "Rz(π/4)Rx(π/4) = [cos(π/8)I − i sin(π/8)Z][cos(π/8)I − i sin(π/8)X]\n"
                "= cos²(π/8) I − i cos(π/8)sin(π/8)(X + Z) − sin²(π/8) ZX.\n"
                "Since ZX = iY, the last term is −i sin²(π/8) Y — traceless, like X and Z. "
                "So the whole product has the form cos(θ/2)I − i sin(θ/2)(n̂·σ) with\n"
                "cos(θ/2) = cos²(π/8) ≈ 0.8536 and axis "
                "n̂ ∝ (cos(π/8), sin(π/8), cos(π/8)), giving θ ≈ 0.3489π "
                "(numerically verified). One can show θ/π is irrational "
                "(N&C Exercise 4.11 / Appendix). Then the multiples {kθ mod 2π} are "
                "pairwise distinct (equality would force θ/2π rational). Infinitely many "
                "distinct points on the circle must have two within ε of each other "
                "(pigeonhole); their difference is a rotation about n̂ by 0 < δ < ε, and "
                "the multiples of δ step around the whole circle in increments < ε. Hence "
                "any angle is approximated to within ε: the generated rotations are dense."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Complete the universality argument in outline: given that we can "
                "approximate arbitrary rotations about one axis n̂, explain (i) how H "
                "conjugation gives a second, non-parallel axis and why two-axis rotations "
                "suffice for any single-qubit unitary (Euler decomposition), and (ii) why "
                "single-qubit unitaries plus CNOT suffice for arbitrary n-qubit unitaries "
                "(you may cite the two-level-unitary decomposition)."
            ),
            points=3,
            rubric=[
                "Notes H R_n̂(θ) H = R_m̂(θ) where m̂ is n̂ with x and z components "
                "exchanged (since HXH = Z, HZH = X, HYH = −Y), giving a second axis not "
                "parallel to n̂.",
                "Cites the Euler-angle style decomposition: any U ∈ SU(2) equals "
                "R_n̂(α) R_m̂(β) R_n̂(γ) (up to phase) for two non-parallel axes, so dense "
                "one-axis rotations about two axes approximate any single-qubit gate.",
                "For (ii): any d-dimensional unitary is a product of two-level unitaries; "
                "each two-level unitary can be implemented with CNOTs (via Gray codes / "
                "multi-controlled operations) and single-qubit gates — so "
                "{single-qubit gates, CNOT} is exactly universal, and with H,T dense "
                "approximation carries through (Solovay–Kitaev gives efficiency).",
            ],
            model_solution=(
                "(i) Conjugating by H maps X↔Z and Y→−Y, so H R_n̂(θ) H = R_m̂(θ) with "
                "m̂ = (n₃, −n₂, n₁) — an axis not parallel to n̂ for our n̂. Any "
                "single-qubit unitary can be written (up to global phase) as "
                "U = R_n̂(α) R_m̂(β) R_n̂(γ) for two fixed non-parallel axes (generalised "
                "Euler decomposition), so from dense rotation angles about n̂ and m̂ we "
                "approximate any U to arbitrary accuracy.\n\n"
                "(ii) Any unitary on d = 2ⁿ dimensions factors exactly into at most "
                "d(d−1)/2 two-level unitaries (acting nontrivially on two basis states). "
                "A two-level unitary is implemented by Gray-coding the two basis strings "
                "into neighbours using CNOTs/multi-controlled X, then applying a "
                "controlled single-qubit rotation, which itself reduces to CNOTs and "
                "single-qubit gates. Hence {single-qubit unitaries, CNOT} is exactly "
                "universal, and replacing single-qubit unitaries by ε-approximations from "
                "{H, T} keeps the total error bounded by the sum of the parts "
                "(errors add sub-additively for unitaries). Solovay–Kitaev makes the "
                "approximation efficient: O(log^c(1/ε)) gates per rotation."
            ),
        ),
    ],
)
