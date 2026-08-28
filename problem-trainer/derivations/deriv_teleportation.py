"""Derivation: the quantum teleportation protocol.

Correction table verified numerically: outcome (i,j) on Bell state |β_ij⟩
leaves Bob with X^j Z^i-corrupted |ψ⟩; corrections I, X, Z, Y(~ZX).
"""
from __future__ import annotations
from core.models import Derivation, Step

DERIVATION = Derivation(
    id="deriv_teleportation",
    title="Quantum Teleportation",
    goal=(
        "Derive the teleportation protocol: how a Bell pair plus two classical bits "
        "moves an unknown qubit state from Alice to Bob."
    ),
    steps=[
        Step(
            step_id="s1",
            prompt=(
                "Write the initial global state: Alice holds an unknown "
                "|ψ⟩ = α|0⟩ + β|1⟩ (qubit 1) and half of a Bell pair "
                "|Φ⁺⟩ = (|00⟩+|11⟩)/√2 (qubits 2–3, Bob holding qubit 3). Expand the "
                "3-qubit state in the computational basis."
            ),
            expected=(
                "|ψ⟩₁ ⊗ |Φ⁺⟩₂₃ = (1/√2)[α|000⟩ + α|011⟩ + β|100⟩ + β|111⟩] "
                "(qubit order 1,2,3; any clearly stated ordering accepted)."
            ),
            hint=(
                "Distribute (α|0⟩ + β|1⟩) over (|00⟩ + |11⟩)/√2 term by term."
            ),
            model_step=(
                "|ψ⟩₁|Φ⁺⟩₂₃ = (α|0⟩ + β|1⟩) ⊗ (|00⟩ + |11⟩)/√2 "
                "= (1/√2)[α|0,00⟩ + α|0,11⟩ + β|1,00⟩ + β|1,11⟩]. Note qubits 1–2 are "
                "with Alice, qubit 3 with Bob; nothing has interacted yet."
            ),
        ),
        Step(
            step_id="s2",
            prompt=(
                "Recall the Bell basis |β_ij⟩ = (|0, j⟩ + (−1)^i |1, j⊕1⟩)/√2. Invert "
                "it: express the two-qubit computational basis states |00⟩, |01⟩, "
                "|10⟩, |11⟩ as combinations of Bell states."
            ),
            expected=(
                "|00⟩ = (β₀₀ + β₁₀)/√2, |11⟩ = (β₀₀ − β₁₀)/√2, "
                "|01⟩ = (β₀₁ + β₁₁)/√2, |10⟩ = (β₀₁ − β₁₁)/√2 (consistent equivalent "
                "conventions accepted)."
            ),
            hint=(
                "β₀₀ ± β₁₀ and β₀₁ ± β₁₁ — add and subtract the definitions pairwise."
            ),
            model_step=(
                "From β₀₀ = (|00⟩+|11⟩)/√2 and β₁₀ = (|00⟩−|11⟩)/√2: "
                "|00⟩ = (β₀₀+β₁₀)/√2, |11⟩ = (β₀₀−β₁₀)/√2. From β₀₁ = (|01⟩+|10⟩)/√2 "
                "and β₁₁ = (|01⟩−|10⟩)/√2: |01⟩ = (β₀₁+β₁₁)/√2, |10⟩ = (β₀₁−β₁₁)/√2. "
                "The Bell basis is just another orthonormal basis for Alice's two "
                "qubits — measuring in it is legitimate and is implemented by a CNOT "
                "then H then computational measurement."
            ),
        ),
        Step(
            step_id="s3",
            prompt=(
                "Substitute the inversion into the state of step 1 and regroup so that "
                "Alice's qubits 1–2 appear in Bell states. Show the total state becomes "
                "(1/2) Σ_ij |β_ij⟩₁₂ ⊗ (X^j Z^i |ψ⟩)₃ — identify Bob's conditional "
                "state for each of the four Bell components."
            ),
            expected=(
                "Regrouped state: ½[ β₀₀ ⊗ (α|0⟩+β|1⟩) + β₀₁ ⊗ (α|1⟩+β|0⟩) + "
                "β₁₀ ⊗ (α|0⟩−β|1⟩) + β₁₁ ⊗ (α|1⟩−β|0⟩) ], i.e. Bob holds "
                "|ψ⟩, X|ψ⟩, Z|ψ⟩, XZ|ψ⟩ respectively — the pattern X^j Z^i |ψ⟩ "
                "(up to sign/phase conventions)."
            ),
            hint=(
                "Replace |00⟩, |01⟩, |10⟩, |11⟩ on qubits 1–2 by their Bell "
                "combinations and collect the coefficient of each |β_ij⟩."
            ),
            model_step=(
                "Substituting and collecting (verified numerically):\n"
                "(1/2)[ β₀₀ ⊗ (α|0⟩ + β|1⟩) + β₀₁ ⊗ (β|0⟩ + α|1⟩) "
                "+ β₁₀ ⊗ (α|0⟩ − β|1⟩) + β₁₁ ⊗ (−β|0⟩ + α|1⟩) ]\n"
                "= (1/2) Σ_ij |β_ij⟩₁₂ ⊗ X^j Z^i |ψ⟩₃ (the β₁₁ term is XZ|ψ⟩ up to "
                "sign, ∝ Y|ψ⟩). Remarkably, Bob's qubit already holds |ψ⟩ up to one of "
                "four FIXED Pauli corruptions — before any communication."
            ),
        ),
        Step(
            step_id="s4",
            prompt=(
                "Alice measures qubits 1–2 in the Bell basis, getting outcome (i, j) "
                "with what probability? What must Bob do, once told (i, j), to recover "
                "|ψ⟩ exactly?"
            ),
            expected=(
                "Each outcome has probability |1/2|² = 1/4, independent of α, β. Bob "
                "applies the inverse corruption: first X^j then Z^i (i.e. Z^i X^j as an "
                "operator), recovering |ψ⟩ exactly: outcome (0,0) → do nothing, "
                "(0,1) → X, (1,0) → Z, (1,1) → Z then X (≅ Y)."
            ),
            hint=(
                "Read the probabilities off the ½ amplitudes; the correction just "
                "inverts X^j Z^i (Paulis are self-inverse)."
            ),
            model_step=(
                "The four Bell components carry equal amplitude ½, so each outcome "
                "occurs with probability ¼ — crucially independent of the unknown "
                "α, β (the measurement learns NOTHING about |ψ⟩). On outcome (i,j) "
                "Bob's state is X^j Z^i|ψ⟩; applying Z^i X^j-inverse, i.e. X^j then "
                "Z^i (each Pauli is its own inverse), gives back |ψ⟩ exactly: "
                "(0,0)→I, (0,1)→X, (1,0)→Z, (1,1)→ZX ∝ Y (all four verified "
                "numerically). Alice's original is destroyed by the measurement — "
                "consistent with no-cloning."
            ),
        ),
        Step(
            step_id="s5",
            prompt=(
                "Why does the protocol not transmit information faster than light, and "
                "why are exactly 2 classical bits needed? What is Bob's density matrix "
                "before Alice's phone call?"
            ),
            expected=(
                "Before the message, Bob's state averaged over the four outcomes is "
                "¼Σ P|ψ⟩⟨ψ|P† = I/2 — independent of |ψ⟩ — so no measurement of Bob's "
                "reveals anything: no signalling. The four equiprobable corrections "
                "require log₂4 = 2 bits to specify; with fewer, Bob is left with a "
                "residual random Pauli and the output is wrong for generic |ψ⟩."
            ),
            hint=(
                "Average Bob's four conditional states with weight ¼ each (Pauli "
                "twirl). How many distinguishable messages must Alice send?"
            ),
            model_step=(
                "Bob's pre-message state is ρ = ¼(|ψ⟩⟨ψ| + X|ψ⟩⟨ψ|X + Z|ψ⟩⟨ψ|Z + "
                "Y-type term) = I/2: the uniform Pauli twirl depolarises every input "
                "completely. Since ρ carries no α, β dependence, nothing Bob does "
                "before receiving (i, j) can extract information — causality is safe; "
                "the quantum state only becomes usable after classical bits arrive at "
                "light speed or slower. And since the four corrections are genuinely "
                "distinct unitaries occurring with equal probability, Alice must send "
                "log₂ 4 = 2 bits. Teleportation thus trades: 1 ebit of entanglement + "
                "2 classical bits → transfer of 1 unknown qubit."
            ),
        ),
    ],
)
