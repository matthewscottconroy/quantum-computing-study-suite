"""Problem: la_schmidt — Schmidt decomposition computation."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="la_schmidt",
    topic="Linear Algebra & QM Math",
    title="Schmidt Decomposition of a Two-Qubit State",
    statement=(
        "Consider the two-qubit state\n\n"
        "    |ψ⟩ = (|00⟩ + |01⟩ + |10⟩) / √3 .\n\n"
        "Every bipartite pure state admits a Schmidt decomposition "
        "|ψ⟩ = Σᵢ √pᵢ |iᴬ⟩|iᴮ⟩ with pᵢ ≥ 0, Σpᵢ = 1. Compute it for this state and "
        "quantify its entanglement."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Compute the reduced density matrix ρᴬ = Tr_B |ψ⟩⟨ψ| in the "
                "{|0⟩, |1⟩} basis. Give the 2×2 matrix explicitly."
            ),
            points=3,
            rubric=[
                "Sets up the partial trace correctly (e.g. via ρᴬ = Σ_b ⟨b|_B ψ⟩⟨ψ |b⟩_B, "
                "or via the coefficient matrix M with ρᴬ = MM†).",
                "Obtains ρᴬ = (1/3)[[2, 1], [1, 1]] exactly (diagonal 2/3 and 1/3, "
                "off-diagonals 1/3).",
                "Sanity check present or implied: Tr ρᴬ = 1, ρᴬ Hermitian.",
            ],
            model_solution=(
                "Write |ψ⟩ = (1/√3)(|0⟩(|0⟩+|1⟩) + |1⟩|0⟩). The coefficient matrix in the "
                "computational basis is M = (1/√3)[[1,1],[1,0]] (rows = system A, "
                "columns = system B), and ρᴬ = MM†:\n"
                "ρᴬ = (1/3)[[1,1],[1,0]]·[[1,1],[1,0]]ᵀ = (1/3)[[2,1],[1,1]].\n"
                "Check: trace = (2+1)/3 = 1 and the matrix is Hermitian, as required."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Find the eigenvalues of ρᴬ, and from them the Schmidt coefficients "
                "√p₁, √p₂ of |ψ⟩. Exact expressions preferred; decimals accepted."
            ),
            points=4,
            rubric=[
                "Characteristic polynomial correct: λ² − λ + 1/9 = 0 "
                "(from trace 1 and det = (2·1 − 1·1)/9 = 1/9).",
                "Eigenvalues p± = (3 ± √5)/6 ≈ 0.8727 and 0.1273 (equivalently "
                "(1 ± √5/3)/2).",
                "Schmidt coefficients are the square roots: √p₊ ≈ 0.9342, √p₋ ≈ 0.3568.",
                "Notes/uses that the same pᵢ would come from ρᴮ (Schmidt spectrum is "
                "shared) — or otherwise correctly connects eigenvalues of ρᴬ to Schmidt "
                "coefficients of |ψ⟩.",
            ],
            model_solution=(
                "Tr ρᴬ = 1 and det ρᴬ = (2·1 − 1²)/9 = 1/9, so the characteristic "
                "equation is λ² − λ + 1/9 = 0, giving\n"
                "    p± = (1 ± √(1 − 4/9))/2 = (3 ± √5)/6 ≈ 0.87268 and 0.12732.\n"
                "The Schmidt decomposition reads |ψ⟩ = √p₊|u₊⟩|v₊⟩ + √p₋|u₋⟩|v₋⟩ where "
                "|u±⟩ are the eigenvectors of ρᴬ (and |v±⟩ of ρᴮ, which has the same "
                "spectrum). The Schmidt coefficients are √p₊ ≈ 0.93417 and √p₋ ≈ 0.35682."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Is |ψ⟩ entangled? Justify via the Schmidt rank, and compute the "
                "entanglement entropy E = −Σᵢ pᵢ log₂ pᵢ (2–4 significant figures)."
            ),
            points=3,
            rubric=[
                "States the criterion: a pure bipartite state is entangled iff its "
                "Schmidt rank ≥ 2 (equivalently ρᴬ is mixed), and concludes |ψ⟩ IS "
                "entangled since both p± > 0.",
                "Computes E = −p₊log₂p₊ − p₋log₂p₋ ≈ 0.550 bits (accept 0.54–0.56).",
                "Notes it is less than maximal (1 ebit for a Bell state) or otherwise "
                "correctly interprets the number.",
            ],
            model_solution=(
                "The Schmidt rank is 2 (two non-zero Schmidt coefficients), so |ψ⟩ is "
                "entangled — a product state would have Schmidt rank 1 and a pure reduced "
                "state. The entanglement entropy is\n"
                "E = −0.87268·log₂(0.87268) − 0.12732·log₂(0.12732) ≈ 0.1714 + 0.3786 "
                "≈ 0.5500 bits,\n"
                "i.e. partially entangled: more than a product state (0) but well below a "
                "Bell state (1 ebit)."
            ),
        ),
    ],
)
