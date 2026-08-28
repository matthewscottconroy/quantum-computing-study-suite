"""Problem: info_entropy_inequalities — von Neumann entropy inequalities.

Verified numerically: for the Bell state, S(AB)=0, S(A)=S(B)=1, so the
"conditional entropy" S(B|A) = S(AB) − S(A) = −1 < 0.
"""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="info_entropy_inequalities",
    topic="Information Theory",
    title="Von Neumann Entropy: Basic Inequalities",
    statement=(
        "The von Neumann entropy is S(ρ) = −Tr(ρ log₂ ρ) = −Σᵢ λᵢ log₂ λᵢ over the "
        "eigenvalues λᵢ of ρ. Prove the following structural facts, then evaluate the "
        "quantum surprise in part (d)."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Prove that S(ρ) ≥ 0 for every density matrix, with equality if and "
                "only if ρ is a pure state."
            ),
            points=2,
            rubric=[
                "Eigenvalues of a density matrix satisfy λᵢ ∈ [0, 1] and Σλᵢ = 1, so "
                "each term −λᵢlog₂λᵢ ≥ 0 (with the convention 0·log0 = 0) ⇒ S ≥ 0.",
                "Equality analysis: S = 0 forces every λᵢ ∈ {0, 1}; with Σλᵢ = 1 "
                "exactly one eigenvalue is 1 ⇒ ρ = |ψ⟩⟨ψ| pure. Conversely a pure "
                "state has spectrum (1, 0, …) ⇒ S = 0. Both directions addressed.",
            ],
            model_solution=(
                "ρ is positive semidefinite with unit trace, so its eigenvalues obey "
                "0 ≤ λᵢ ≤ 1, Σλᵢ = 1. For λ ∈ (0,1], −λ log₂ λ ≥ 0 (log₂λ ≤ 0), and "
                "the λ = 0 terms contribute 0 by continuity (x log x → 0). Hence "
                "S(ρ) = Σᵢ(−λᵢ log₂ λᵢ) ≥ 0.\n"
                "Equality: each term must vanish individually, so every λᵢ is 0 or 1; "
                "the trace condition then leaves exactly one eigenvalue equal to 1, "
                "i.e. ρ is a rank-1 projector |ψ⟩⟨ψ| — a pure state. Conversely any "
                "pure state has spectrum {1, 0, …, 0} and S = 0."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "State the subadditivity inequality for a bipartite state ρ_AB and "
                "prove that equality holds for product states ρ_AB = ρ_A ⊗ ρ_B. "
                "(You may use that the spectrum of ρ_A ⊗ ρ_B is {λᵢ μⱼ}.)"
            ),
            points=3,
            rubric=[
                "States subadditivity: S(ρ_AB) ≤ S(ρ_A) + S(ρ_B) (for all joint "
                "states, equality iff product).",
                "For a product state, uses the spectrum {λᵢμⱼ} of ρ_A ⊗ ρ_B (λᵢ, μⱼ "
                "the marginal spectra).",
                "Computes S(ρ_A⊗ρ_B) = −Σᵢⱼ λᵢμⱼ(log₂λᵢ + log₂μⱼ) "
                "= −Σᵢλᵢlog₂λᵢ·Σⱼμⱼ − Σⱼμⱼlog₂μⱼ·Σᵢλᵢ = S(ρ_A) + S(ρ_B), using "
                "normalisation of each marginal spectrum.",
            ],
            model_solution=(
                "Subadditivity: for any bipartite ρ_AB with marginals ρ_A, ρ_B,\n"
                "    S(ρ_AB) ≤ S(ρ_A) + S(ρ_B).\n"
                "If ρ_AB = ρ_A ⊗ ρ_B with spectra {λᵢ}, {μⱼ}, then ρ_AB has eigenvalues "
                "{λᵢμⱼ} and\n"
                "S(ρ_AB) = −Σᵢⱼ λᵢμⱼ log₂(λᵢμⱼ) = −Σᵢⱼ λᵢμⱼ (log₂λᵢ + log₂μⱼ)\n"
                "= −(Σⱼμⱼ)(Σᵢλᵢlog₂λᵢ) − (Σᵢλᵢ)(Σⱼμⱼlog₂μⱼ) = S(ρ_A) + S(ρ_B),\n"
                "since Σᵢλᵢ = Σⱼμⱼ = 1. So the bound is saturated exactly when the "
                "subsystems are uncorrelated (and in general the deficit "
                "S(A) + S(B) − S(AB) is the mutual information I(A:B) ≥ 0)."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Prove that for any PURE bipartite state |ψ⟩_AB, the marginal entropies "
                "are equal: S(ρ_A) = S(ρ_B). (Hint: Schmidt decomposition.)"
            ),
            points=2,
            rubric=[
                "Writes the Schmidt decomposition |ψ⟩ = Σᵢ √pᵢ |iᴬ⟩|iᴮ⟩ with "
                "orthonormal {|iᴬ⟩}, {|iᴮ⟩}.",
                "Computes both marginals: ρ_A = Σᵢ pᵢ|iᴬ⟩⟨iᴬ|, ρ_B = Σᵢ pᵢ|iᴮ⟩⟨iᴮ| — "
                "identical spectra {pᵢ} ⇒ identical entropies S(A) = S(B) = "
                "−Σpᵢlog₂pᵢ.",
            ],
            model_solution=(
                "Every pure bipartite state admits a Schmidt decomposition "
                "|ψ⟩ = Σᵢ √pᵢ |iᴬ⟩|iᴮ⟩ with pᵢ ≥ 0, Σpᵢ = 1 and orthonormal Schmidt "
                "bases on each side. Tracing out B: ρ_A = Σᵢ pᵢ |iᴬ⟩⟨iᴬ|; tracing out "
                "A: ρ_B = Σᵢ pᵢ |iᴮ⟩⟨iᴮ|. The two reduced states are diagonal in their "
                "Schmidt bases with the SAME eigenvalue list {pᵢ}, so "
                "S(ρ_A) = −Σᵢpᵢlog₂pᵢ = S(ρ_B). (Entropy depends only on the "
                "spectrum.) This common value is the entanglement entropy of |ψ⟩."
            ),
        ),
        Part(
            part_id="d",
            prompt=(
                "For the Bell state |Φ⁺⟩ = (|00⟩+|11⟩)/√2 compute S(AB), S(A), S(B), "
                "and the conditional entropy S(B|A) = S(AB) − S(A). Explain why the "
                "result is impossible for classical Shannon entropies and what it "
                "signifies."
            ),
            points=3,
            rubric=[
                "S(AB) = 0 (pure state); ρ_A = ρ_B = I/2 ⇒ S(A) = S(B) = 1 bit.",
                "S(B|A) = 0 − 1 = −1: NEGATIVE conditional entropy.",
                "Classically H(B|A) = H(AB) − H(A) ≥ 0 always (conditioning cannot "
                "create negative uncertainty; H(AB) ≥ H(A)); negativity is a signature "
                "of entanglement — the whole is more sharply determined than its "
                "parts. (Bonus interpretations accepted: quantum state merging cost, "
                "coherent information > 0 enabling quantum communication.)",
            ],
            model_solution=(
                "|Φ⁺⟩ is pure ⇒ S(AB) = 0. Its marginals are ρ_A = ρ_B = I/2 "
                "(tracing either qubit of ½(|00⟩⟨00| + |00⟩⟨11| + |11⟩⟨00| + |11⟩⟨11|) "
                "kills the cross terms), each with entropy log₂2 = 1 bit "
                "(verified numerically). Hence\n"
                "    S(B|A) = S(AB) − S(A) = 0 − 1 = −1 bit.\n"
                "Classically this cannot happen: H(AB) = H(A) + H(B|A) with "
                "H(B|A) ≥ 0, so a subsystem can never be more uncertain than the "
                "whole. Quantumly the joint state is perfectly known (pure) while each "
                "part alone is maximally random — the information resides entirely in "
                "the correlations. Negative conditional entropy is an entanglement "
                "witness, and operationally −S(B|A) quantifies resources gained in "
                "protocols like state merging (Alice can transfer her share using "
                "no communication and banking entanglement when S(B|A) < 0)."
            ),
        ),
    ],
)
