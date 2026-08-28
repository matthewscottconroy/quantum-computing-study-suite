"""Problem: vqa_qaoa_p1 — exact p=1 QAOA analysis on a single edge.

Verified numerically: F(γ,β) = 1/2 + (1/2)·sin(4β)·sin(γ), optimum F = 1 at
γ = π/2, β = π/8 (mixer convention e^{−iβ(X₁+X₂)}).
"""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="vqa_qaoa_p1",
    topic="VQA",
    title="QAOA at p = 1: Exact Analysis of a Single Edge",
    statement=(
        "Consider MaxCut on the smallest graph: two vertices joined by one edge. The "
        "cost operator is C = (1 − Z₁Z₂)/2 (eigenvalue 1 on the cut states |01⟩, |10⟩; "
        "0 on |00⟩, |11⟩). The p = 1 QAOA state is\n\n"
        "    |γ, β⟩ = e^{−iβ(X₁+X₂)} · e^{−iγC} · |+⟩|+⟩ ,\n\n"
        "and the objective is F(γ, β) = ⟨γ,β| C |γ,β⟩. Everything here can be computed "
        "in closed form."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Write out the state e^{−iγC}|++⟩ explicitly in the computational basis, "
                "and explain why the cost layer only imprints a relative phase e^{−iγ} "
                "on the two cut states."
            ),
            points=3,
            rubric=[
                "|++⟩ = ½(|00⟩ + |01⟩ + |10⟩ + |11⟩).",
                "C is diagonal with eigenvalues {0, 1, 1, 0} on "
                "{|00⟩, |01⟩, |10⟩, |11⟩}, so e^{−iγC} multiplies |01⟩, |10⟩ by e^{−iγ} "
                "and leaves |00⟩, |11⟩ unchanged.",
                "Result: e^{−iγC}|++⟩ = ½(|00⟩ + e^{−iγ}|01⟩ + e^{−iγ}|10⟩ + |11⟩); "
                "notes only the relative phase between cut/uncut sectors matters.",
            ],
            model_solution=(
                "C|00⟩ = 0, C|11⟩ = 0, C|01⟩ = |01⟩, C|10⟩ = |10⟩ — C is diagonal. "
                "Hence e^{−iγC} acts as e^{−iγ·0} = 1 on the uncut states and "
                "e^{−iγ·1} = e^{−iγ} on the cut states:\n"
                "e^{−iγC}|++⟩ = ½(|00⟩ + e^{−iγ}|01⟩ + e^{−iγ}|10⟩ + |11⟩).\n"
                "Because a global phase is irrelevant, the only physical content of the "
                "cost layer is the RELATIVE phase e^{−iγ} between the cut and uncut "
                "sectors — QAOA's cost layers are pure phase oracles."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Compute F(γ, β) in closed form. (Recommended route: Heisenberg picture "
                "— write ⟨Z₁Z₂⟩ by conjugating Z₁Z₂ through the mixer using "
                "e^{iβX} Z e^{−iβX} = cos(2β) Z + sin(2β) Y per qubit, then take the "
                "expectation in the phased state from (a).) Show that\n"
                "    F(γ, β) = 1/2 + (1/2) sin(4β) sin(γ) ."
            ),
            points=4,
            rubric=[
                "Correct single-qubit conjugation e^{iβX} Z e^{−iβX} = cos(2β)Z + "
                "sin(2β)Y (other sign conventions accepted if used consistently to a "
                "correct final answer).",
                "Expands M†Z₁Z₂M = cos²(2β) Z₁Z₂ + sin(2β)cos(2β)(Y₁Z₂ + Z₁Y₂) + "
                "sin²(2β) Y₁Y₂ and evaluates each term in the state from (a).",
                "Correct intermediate expectations in the phased state: ⟨Z₁Z₂⟩ = 0, "
                "⟨Y₁Y₂⟩ = 0, ⟨Y₁Z₂ + Z₁Y₂⟩ = −2 sin(γ), assembling to "
                "⟨M†Z₁Z₂M⟩ = −sin(4β) sin(γ). Accept any complete correct route "
                "(direct state-vector computation included).",
                "Final formula exactly F = (1 − ⟨Z₁Z₂⟩)/2 = ½ + ½ sin(4β) sin(γ); "
                "sin(4β) — not sin(2β) — because BOTH qubits' mixers contribute.",
            ],
            model_solution=(
                "Heisenberg picture: with M = e^{−iβ(X₁+X₂)}, "
                "F = ⟨φ| M† C M |φ⟩ where |φ⟩ = e^{−iγC}|++⟩. Per qubit, "
                "e^{iβX} Z e^{−iβX} = cos(2β) Z + sin(2β) Y (rotation of Z about x̂), so\n"
                "M† Z₁Z₂ M = [cos2β Z₁ + sin2β Y₁][cos2β Z₂ + sin2β Y₂]\n"
                "= cos²2β Z₁Z₂ + sin2β cos2β (Y₁Z₂ + Z₁Y₂) + sin²2β Y₁Y₂.\n"
                "In |φ⟩ = ½(|00⟩ + e^{−iγ}|01⟩ + e^{−iγ}|10⟩ + |11⟩) (all verified "
                "numerically):\n"
                "⟨Z₁Z₂⟩ = ¼(1 − 1 − 1 + 1) = 0;  ⟨Y₁Y₂⟩ = 0;  "
                "⟨Y₁Z₂ + Z₁Y₂⟩ = −2 sin γ (the Y operators connect the uncut sector to "
                "the cut sector, picking up the relative phase e^{∓iγ}, and the "
                "imaginary parts add to −2 sinγ).\n"
                "Assembling: ⟨M† Z₁Z₂ M⟩ = sin2β cos2β · (−2 sinγ) = −sin(4β) sin(γ),\n"
                "hence F = (1 − ⟨Z₁Z₂⟩(γ,β))/2 = ½ + ½ sin(4β) sin(γ). This closed form "
                "was verified numerically against direct matrix-exponential simulation "
                "at several (γ, β) points; note the 4β: the two single-qubit mixers "
                "contribute sin2β·cos2β = sin(4β)/2."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Maximise F over (γ, β): give optimal angles, the optimal value, and the "
                "resulting approximation ratio for this instance. Then explain briefly "
                "why p = 1 QAOA is NOT exact for general graphs (e.g. what changes for "
                "a triangle or larger MaxCut instances), citing the known ring result "
                "F/edge → 3/4 or a similar fact if you know one."
            ),
            points=3,
            rubric=[
                "Optimum where sin(4β) = sin(γ) = 1 (or both −1): e.g. γ = π/2, "
                "β = π/8, giving F = 1.",
                "Approximation ratio F/C_max = 1/1 = 1: p = 1 QAOA solves the "
                "single-edge instance exactly.",
                "General graphs: each edge's expectation involves interference from "
                "shared neighbours; a single (γ, β) pair cannot phase-align all edges "
                "simultaneously, so F < C_max — e.g. for the 2-regular ring, p = 1 "
                "achieves ratio 3/4 (Farhi et al.), improving toward 1 only as p grows "
                "(adiabatic limit). Any correct qualitative account earns credit.",
            ],
            model_solution=(
                "F = ½ + ½ sin(4β) sin(γ) ≤ 1, with equality iff sin(4β)sin(γ) = 1, "
                "e.g. β* = π/8, γ* = π/2 (verified numerically: F(π/2, π/8) = 1). The "
                "state |γ*, β*⟩ is then supported entirely on {|01⟩, |10⟩}: the exact "
                "MaxCut. Approximation ratio 1 — depth-1 QAOA is exact for one edge.\n"
                "For larger graphs exactness fails: the conjugated cost of an edge (u,v) "
                "picks up contributions from every edge sharing a vertex with it, and "
                "one global (γ, β) must trade off all local neighbourhoods "
                "simultaneously. For the 2-regular ring (each vertex degree 2), the "
                "exact p = 1 value is 3/4 per edge; for triangle-containing and "
                "higher-degree graphs the ratio is likewise bounded away from 1. As "
                "p → ∞, QAOA can Trotter-approximate adiabatic evolution and the ratio "
                "approaches 1 — at the price of circuit depth and a harder classical "
                "parameter search."
            ),
        ),
    ],
)
