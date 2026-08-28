"""Problem: info_holevo — applying the Holevo bound.

Verified numerically: rho = (|0><0| + |+><+|)/2 = [[0.75,0.25],[0.25,0.25]],
eigenvalues (1 ± 1/sqrt2)/2 = cos^2(pi/8), sin^2(pi/8); chi = S(rho) ~ 0.6009 bits.
"""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="info_holevo",
    topic="Information Theory",
    title="The Holevo Bound in Action",
    statement=(
        "Alice encodes a uniformly random classical bit x ∈ {0, 1} into a qubit: "
        "x = 0 → |0⟩, x = 1 → |+⟩ = (|0⟩+|1⟩)/√2, and sends it to Bob, who may perform "
        "any measurement (POVM). The Holevo bound states that the accessible "
        "information satisfies\n\n"
        "    I(X : Y) ≤ χ = S(ρ) − Σₓ pₓ S(ρₓ) ,\n\n"
        "where ρ = Σₓ pₓ ρₓ is the average state and S is the von Neumann entropy "
        "(in bits)."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Compute the average state ρ = ½|0⟩⟨0| + ½|+⟩⟨+| as an explicit 2×2 "
                "matrix, and find its eigenvalues exactly."
            ),
            points=3,
            rubric=[
                "ρ = ½[[1,0],[0,0]] + ½[[½,½],[½,½]] = [[¾, ¼],[¼, ¼]].",
                "Eigenvalues from λ² − λ + det: det ρ = 3/16 − 1/16 = 1/8, so "
                "λ± = (1 ± √(1 − ½))/2 = (1 ± 1/√2)/2 ≈ 0.8536, 0.1464.",
                "Recognises (optionally) λ± = cos²(π/8), sin²(π/8) — the Bloch-vector "
                "length is 1/√2, reflecting the 45° angle between |0⟩ and |+⟩.",
            ],
            model_solution=(
                "|+⟩⟨+| = ½[[1,1],[1,1]], so ρ = [[3/4, 1/4],[1/4, 1/4]] (verified). "
                "Tr ρ = 1 and det ρ = 3/16 − 1/16 = 1/8, so λ² − λ + 1/8 = 0:\n"
                "λ± = (1 ± √(1/2))/2 = (1 ± 1/√2)/2 ≈ 0.85355 and 0.14645,\n"
                "which are exactly cos²(π/8) and sin²(π/8): geometrically, ρ sits at the "
                "midpoint of the Bloch vectors ẑ and x̂, at distance "
                "|r| = |ẑ+x̂|/2 = 1/√2 from the centre, giving eigenvalues (1 ± |r|)/2."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Evaluate the Holevo quantity χ for this ensemble (3–4 significant "
                "figures), and state clearly why the second term Σₓ pₓ S(ρₓ) vanishes "
                "here."
            ),
            points=3,
            rubric=[
                "Both ρ₀ = |0⟩⟨0| and ρ₁ = |+⟩⟨+| are PURE, so S(ρₓ) = 0 and "
                "χ = S(ρ).",
                "χ = H₂((1+1/√2)/2) = −λ₊log₂λ₊ − λ₋log₂λ₋ ≈ 0.6009 bits "
                "(accept 0.60 ± 0.005).",
                "Computation shown (not just the number): plugs the eigenvalues from "
                "(a) into the entropy.",
            ],
            model_solution=(
                "The signal states are pure, and pure states have zero von Neumann "
                "entropy, so Σₓ pₓS(ρₓ) = 0 and χ = S(ρ). Using the eigenvalues from "
                "part (a):\n"
                "χ = −0.85355·log₂(0.85355) − 0.14645·log₂(0.14645)\n"
                "  ≈ 0.19499 + 0.40590 ≈ 0.6009 bits (verified numerically).\n"
                "So although Alice chose from 2 alternatives (1 bit of source entropy), "
                "at most ≈ 0.601 bits are accessible to ANY measurement Bob makes."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Interpret the result: (i) why can Bob not decode Alice's bit reliably, "
                "and how is this consistent with |0⟩ and |+⟩ being linearly independent? "
                "(ii) Use the Holevo bound to prove the general statement that n qubits "
                "(without entanglement assistance) cannot carry more than n bits of "
                "classical information — and reconcile this with superdense coding."
            ),
            points=4,
            rubric=[
                "(i) Non-orthogonality: |⟨0|+⟩|² = 1/2 ≠ 0, so no measurement "
                "distinguishes the states perfectly; χ < 1 quantifies the maximum "
                "extractable correlation. Linear independence ≠ orthogonality — "
                "unambiguous discrimination is possible only probabilistically.",
                "(ii) For any ensemble on n qubits, S(ρ) ≤ log₂(2ⁿ) = n (entropy is "
                "maximised by the maximally mixed state), and Σpₓ S(ρₓ) ≥ 0, so "
                "χ ≤ n ⇒ I(X:Y) ≤ n bits.",
                "Superdense coding sends 2 bits with 1 transmitted qubit but uses "
                "PRE-SHARED entanglement: the Holevo analysis then applies to the full "
                "2-qubit system Bob ends up measuring (χ ≤ 2) — no contradiction; "
                "without prior entanglement the n-bit limit stands.",
            ],
            model_solution=(
                "(i) ⟨0|+⟩ = 1/√2 ≠ 0: the two signal states are non-orthogonal, and "
                "no POVM can distinguish non-orthogonal states with certainty (perfect "
                "discrimination would clone/distinguish them, violating unitarity). "
                "Linear independence permits UNAMBIGUOUS discrimination, but only with "
                "an inconclusive outcome of nonzero probability; the Holevo value "
                "0.6009 < 1 bit caps the mutual information any strategy achieves.\n"
                "(ii) For states on n qubits, S(ρ) ≤ n (dimension bound, equality at "
                "ρ = I/2ⁿ) and the subtracted term is non-negative, so "
                "χ = S(ρ) − ΣpₓS(ρₓ) ≤ n. By Holevo, I(X:Y) ≤ n: at most n classical "
                "bits per n transmitted qubits.\n"
                "Superdense coding is consistent: Alice and Bob pre-share a Bell pair; "
                "Alice's local Pauli encodes 2 bits and she transmits ONE qubit, but "
                "Bob decodes by measuring BOTH qubits. The Holevo bound applied to the "
                "pair (χ ≤ 2, achieved by the four orthogonal Bell states) allows "
                "exactly 2 bits. The bound constrains information carried per measured "
                "system; entanglement lets one transmitted qubit unlock correlations "
                "stored in two."
            ),
        ),
    ],
)
