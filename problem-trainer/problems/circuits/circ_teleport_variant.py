"""Problem: circ_teleport_variant — teleportation with a |Φ⁻⟩ resource state.

Corrections verified numerically: with Bell measurement outcomes labelled
(i,j) for state |β_ij⟩ = (|0 j⟩ + (−1)^i |1 j̄⟩)/√2, Bob's correction is
X^j Z^(i⊕1) up to global phase (I→Z, X→Y~ZX, Z→I, Y→X relative to standard).
"""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="circ_teleport_variant",
    topic="Circuits & Gates",
    title="Teleportation with a |Φ⁻⟩ Resource",
    statement=(
        "Standard teleportation uses the resource state |Φ⁺⟩ = (|00⟩+|11⟩)/√2 shared "
        "between Alice (qubit 2) and Bob (qubit 3); Alice Bell-measures qubits 1–2 and "
        "Bob applies X^j Z^i for outcome (i, j). Suppose instead the shared pair was "
        "prepared in |Φ⁻⟩ = (|00⟩ − |11⟩)/√2, but the protocol is otherwise unchanged.\n\n"
        "Label Bell states |β_ij⟩ = (|0, j⟩ + (−1)^i |1, j⊕1⟩)/√2, so β₀₀ = Φ⁺, "
        "β₀₁ = Ψ⁺, β₁₀ = Φ⁻, β₁₁ = Ψ⁻. Alice's input is |ψ⟩ = α|0⟩ + β|1⟩."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Expand the total state |ψ⟩₁ ⊗ |Φ⁻⟩₂₃ in the Bell basis of qubits 1 and "
                "2, i.e. write it as (1/2) Σ_ij |β_ij⟩₁₂ ⊗ |φ_ij⟩₃ and give Bob's "
                "(unnormalised) conditional states |φ_ij⟩ explicitly in terms of α, β."
            ),
            points=4,
            rubric=[
                "Correct expansion of |ψ⟩⊗|Φ⁻⟩ = (1/√2)[α|000⟩ − α|011⟩ + β|100⟩ − β|111⟩].",
                "Inverts the Bell basis correctly, e.g. |00⟩ = (β₀₀+β₁₀)/√2, "
                "|01⟩ = (β₀₁+β₁₁)/√2, |10⟩ = (β₀₁−β₁₁)/√2, |11⟩ = (β₀₀−β₁₀)/√2 "
                "(any consistent convention accepted).",
                "Obtains, up to overall 1/2 and consistent labelling: "
                "outcome β₀₀ → α|0⟩ − β|1⟩ (= Z|ψ⟩); β₀₁ → −α|1⟩ + β|0⟩ (∝ ZX|ψ⟩ ~ Y|ψ⟩); "
                "β₁₀ → α|0⟩ + β|1⟩ (= |ψ⟩); β₁₁ → α|1⟩ + β|0⟩ (= X|ψ⟩).",
                "Each conditional state occurs with probability 1/4 (stated or implied "
                "by the uniform 1/2 coefficients).",
            ],
            model_solution=(
                "|ψ⟩₁|Φ⁻⟩₂₃ = (1/√2)[α|0⟩(|00⟩−|11⟩) + β|1⟩(|00⟩−|11⟩)]\n"
                "= (1/√2)[α|00⟩|0⟩ − α|01⟩|1⟩ + β|10⟩|0⟩ − β|11⟩|1⟩].\n"
                "Using |00⟩ = (β₀₀+β₁₀)/√2, |11⟩ = (β₀₀−β₁₀)/√2, |01⟩ = (β₀₁+β₁₁)/√2, "
                "|10⟩ = (β₀₁−β₁₁)/√2 on qubits 1–2 and collecting terms:\n"
                "= ½[ β₀₀ ⊗ (α|0⟩ − β|1⟩) + β₀₁ ⊗ (β|0⟩ − α|1⟩) "
                "+ β₁₀ ⊗ (α|0⟩ + β|1⟩) + β₁₁ ⊗ (−(β|0⟩ + α|1⟩)) ].\n"
                "Explicitly (verified numerically): outcome (0,0): Z|ψ⟩; (0,1): ∝ Y|ψ⟩ "
                "(equivalently ZX|ψ⟩ up to phase); (1,0): |ψ⟩; (1,1): X|ψ⟩. All four "
                "outcomes have amplitude ½, hence probability ¼ each."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "For each measurement outcome (i, j), state the correction Bob must apply "
                "to recover |ψ⟩ exactly (up to global phase). Express the pattern as a "
                "single formula and compare it with the standard-protocol corrections "
                "X^j Z^i."
            ),
            points=3,
            rubric=[
                "Corrections (up to phase): (0,0) → Z; (0,1) → Y (or equivalently ZX); "
                "(1,0) → I (identity); (1,1) → X. Consistent with the student's own "
                "convention from part (a) — internal consistency is what earns credit.",
                "Compact formula: correction = X^j Z^(i⊕1) up to global phase — i.e. the "
                "standard correction with the Z-bit flipped.",
                "Interprets the change: |Φ⁻⟩ = (Z⊗I)|Φ⁺⟩ (or (I⊗Z)|Φ⁺⟩), so the extra Z "
                "on the resource propagates into an extra Z on Bob's correction.",
            ],
            model_solution=(
                "From part (a) Bob holds: (0,0): Z|ψ⟩ → apply Z; (0,1): Y|ψ⟩ up to phase "
                "→ apply Y (or X then Z); (1,0): |ψ⟩ → do nothing; (1,1): X|ψ⟩ → apply X. "
                "Pattern: correction = X^j Z^(i⊕1), i.e. exactly the standard rule "
                "X^j Z^i with i replaced by i⊕1 (numerically verified for all four "
                "outcomes).\n"
                "Reason: |Φ⁻⟩ = (Z⊗I)|Φ⁺⟩. The Z on Alice's half of the resource "
                "commutes through the protocol and is equivalent to relabelling the "
                "phase bit i of her Bell measurement, so Bob compensates with one extra Z."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Explain why this protocol (like standard teleportation) transmits no "
                "information faster than light, and why exactly 2 classical bits are "
                "necessary. What does Bob's density matrix look like before he receives "
                "Alice's message?"
            ),
            points=3,
            rubric=[
                "Before receiving (i, j), Bob's state is the uniform mixture "
                "¼Σ P_ij|ψ⟩⟨ψ|P_ij = I/2 — independent of α, β — so no measurement by "
                "Bob reveals anything about |ψ⟩ (no-signalling).",
                "Necessity of 2 bits: the four Pauli corrections {I, X, Z, Y(=ZX)} are "
                "genuinely different unitaries mapping Bob's four conditional states to "
                "|ψ⟩; distinguishing four equiprobable outcomes requires log₂4 = 2 bits "
                "(fewer bits would leave residual Pauli errors with probability ≥ 1/2 "
                "on some outcomes).",
                "(Any correct additional framing accepted, e.g. via Holevo/causality; "
                "key point is I/2 independence plus the 4-outcome counting argument.)",
            ],
            model_solution=(
                "Averaged over Alice's four equiprobable outcomes, Bob's density matrix is "
                "ρ_B = ¼(Z|ψ⟩⟨ψ|Z + Y|ψ⟩⟨ψ|Y + |ψ⟩⟨ψ| + X|ψ⟩⟨ψ|X) = I/2 for every "
                "input |ψ⟩ (the Pauli twirl depolarises any qubit state). Since ρ_B "
                "carries no dependence on α, β, nothing Bob can do before the classical "
                "message arrives yields information about |ψ⟩ — the protocol respects "
                "causality; the quantum state is only recovered after classical "
                "communication, which is lightspeed-limited.\n"
                "Two bits are necessary: the four conditional states Z|ψ⟩, Y|ψ⟩, |ψ⟩, "
                "X|ψ⟩ require four distinct corrections, and which one applies is "
                "uniformly random. Selecting among 4 equiprobable alternatives requires "
                "log₂ 4 = 2 classical bits; with fewer, at least two outcomes would share "
                "a correction and Bob's output would be wrong (a fixed Pauli off) with "
                "probability at least 1/4 per state — teleportation would not be faithful."
            ),
        ),
    ],
)
