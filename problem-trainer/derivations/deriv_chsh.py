"""Derivation: CHSH inequality and the Tsirelson bound.

Verified numerically: S² = 4I − [A,A']⊗[B,B'], and the Bell state with
measurement angles 0, π/2 (Alice) and ±π/4 (Bob) attains ⟨S⟩ = 2√2.
"""
from __future__ import annotations
from core.models import Derivation, Step

DERIVATION = Derivation(
    id="deriv_chsh",
    title="CHSH and the Tsirelson Bound",
    goal=(
        "Derive the classical CHSH bound |⟨S⟩| ≤ 2 and the quantum Tsirelson bound "
        "|⟨S⟩| ≤ 2√2, and exhibit a strategy attaining 2√2."
    ),
    steps=[
        Step(
            step_id="s1",
            prompt=(
                "Setup: Alice measures a or a′, Bob measures b or b′, all outcomes "
                "±1. Consider the combination S = ab + ab′ + a′b − a′b′. Assuming a "
                "local hidden-variable model (all four values a, a′, b, b′ exist "
                "simultaneously as numbers ±1), show S = ±2 always."
            ),
            expected=(
                "Factor S = a(b + b′) + a′(b − b′). Since b, b′ ∈ {±1}, either "
                "b + b′ = ±2 and b − b′ = 0, or b + b′ = 0 and b − b′ = ±2; in both "
                "cases exactly one term survives and S = ±2."
            ),
            hint=(
                "Group the four terms so b + b′ and b − b′ appear. What pairs of "
                "values can (b + b′, b − b′) take?"
            ),
            model_step=(
                "S = a(b + b′) + a′(b − b′). If b = b′ then b − b′ = 0 and "
                "b + b′ = ±2, so S = ±2a = ±2. If b = −b′ then b + b′ = 0 and "
                "b − b′ = ±2, so S = ±2a′ = ±2. In every deterministic assignment of "
                "the four ±1 values, S = ±2."
            ),
        ),
        Step(
            step_id="s2",
            prompt=(
                "Deduce the CHSH inequality for any local hidden-variable theory: "
                "what bound on |⟨S⟩| = |E(a,b) + E(a,b′) + E(a′,b) − E(a′,b′)| "
                "follows, and why does averaging over the hidden variable preserve it?"
            ),
            expected=(
                "Averaging a quantity that always equals ±2 over any probability "
                "distribution λ gives |⟨S⟩| = |∫dλ p(λ) S(λ)| ≤ ∫dλ p(λ)|S(λ)| = 2. "
                "Hence |⟨S⟩| ≤ 2 for every LHV model — the CHSH inequality."
            ),
            hint=(
                "The hidden variable λ fixes all four values; the observed correlators "
                "are averages over λ. Use the triangle inequality."
            ),
            model_step=(
                "In an LHV model each λ assigns definite values a(λ), a′(λ), b(λ), "
                "b′(λ) ∈ {±1}, and by step 1 S(λ) = ±2 for every λ. The measured "
                "correlators are E(x,y) = ∫dλ p(λ) x(λ)y(λ), so "
                "⟨S⟩ = ∫dλ p(λ)S(λ), and |⟨S⟩| ≤ ∫dλ p(λ)·2 = 2. Any experiment with "
                "|⟨S⟩| > 2 rules out ALL local hidden-variable theories."
            ),
        ),
        Step(
            step_id="s3",
            prompt=(
                "Quantum case: A, A′ on Alice's qubit and B, B′ on Bob's are ±1-valued "
                "observables (A² = I etc.), and S = A⊗B + A⊗B′ + A′⊗B − A′⊗B′. "
                "Compute S² and show S² = 4I − [A, A′]⊗[B, B′]."
            ),
            expected=(
                "Expanding S² using A² = A′² = B² = B′² = I: the 16 terms collapse; "
                "squared terms give 4I and the cross terms assemble into "
                "−[A,A′]⊗[B,B′] (sign conventions consistent with the student's "
                "expansion accepted). Key ingredients: operators on different sides "
                "commute; A,A′ (and B,B′) need not commute."
            ),
            hint=(
                "Write S = A⊗(B+B′) + A′⊗(B−B′) and square, using "
                "(B+B′)² + (B−B′)² = 4I and (B+B′)(B−B′) = −[B,B′]-type identities."
            ),
            model_step=(
                "With S = A⊗(B+B′) + A′⊗(B−B′):\n"
                "S² = A²⊗(B+B′)² + A′²⊗(B−B′)² + AA′⊗(B+B′)(B−B′) + A′A⊗(B−B′)(B+B′).\n"
                "Now (B+B′)² + (B−B′)² = 2B² + 2B′² = 4I, and "
                "(B+B′)(B−B′) = B² − BB′ + B′B − B′² = B′B − BB′ = −[B,B′], while "
                "(B−B′)(B+B′) = +[B,B′]. So the cross terms give "
                "(A′A − AA′)⊗[B,B′] = −[A,A′]⊗[B,B′], and\n"
                "S² = 4I − [A,A′]⊗[B,B′]  (identity verified numerically)."
            ),
        ),
        Step(
            step_id="s4",
            prompt=(
                "From S² = 4I − [A,A′]⊗[B,B′], derive the Tsirelson bound "
                "|⟨S⟩| ≤ 2√2. (Use operator norms: ‖XY‖ ≤ ‖X‖‖Y‖, "
                "‖[X,Y]‖ ≤ 2‖X‖‖Y‖, and ‖A‖ = 1 for ±1-valued observables.)"
            ),
            expected=(
                "‖[A,A′]‖ ≤ 2 and ‖[B,B′]‖ ≤ 2, so ‖S²‖ ≤ 4 + 4 = 8, hence "
                "‖S‖ ≤ √8 = 2√2 and |⟨S⟩| ≤ ‖S‖ ≤ 2√2. (Any correct argument via "
                "eigenvalues/variance also accepted.)"
            ),
            hint=(
                "Bound the norm of each commutator by 2, then take the square root of "
                "the operator inequality."
            ),
            model_step=(
                "Each observable has norm 1 (eigenvalues ±1), so "
                "‖[A,A′]‖ ≤ ‖AA′‖ + ‖A′A‖ ≤ 2, likewise ‖[B,B′]‖ ≤ 2, and "
                "‖[A,A′]⊗[B,B′]‖ ≤ 4. Hence ‖S²‖ ≤ ‖4I‖ + 4 = 8. Since S is Hermitian, "
                "‖S‖² = ‖S²‖ ≤ 8 ⇒ ‖S‖ ≤ 2√2, and for any state "
                "|⟨S⟩| ≤ ‖S‖ ≤ 2√2 — Tsirelson's bound. Note the quantum advantage "
                "lives entirely in the non-vanishing commutators: if Alice's (or "
                "Bob's) two observables commute, S² ≤ 4I and the classical bound 2 "
                "returns."
            ),
        ),
        Step(
            step_id="s5",
            prompt=(
                "Show the bound is achieved: give a state and four observables "
                "attaining ⟨S⟩ = 2√2, and verify the four correlators. (Standard "
                "choice: Bell state |Φ⁺⟩, Alice A = Z, A′ = X, Bob "
                "B = (Z+X)/√2, B′ = (Z−X)/√2.)"
            ),
            expected=(
                "For |Φ⁺⟩, the correlator identity ⟨(n̂·σ)⊗(m̂·σ)⟩-style gives "
                "E(θ_A, θ_B) = cos(θ_A − θ_B) for measurement axes in the x–z plane. "
                "With angles 0, π/2 (Alice) and π/4, −π/4 (Bob): "
                "E(A,B) = E(A,B′) = E(A′,B) = cos(π/4) = 1/√2 and "
                "E(A′,B′) = cos(3π/4) = −1/√2, so ⟨S⟩ = 4·(1/√2)·(±-correct signs) "
                "= 2√2. Any equivalent verified configuration accepted."
            ),
            hint=(
                "On |Φ⁺⟩, measurements along axes at angles θ_A, θ_B in the x–z plane "
                "have correlator cos(θ_A − θ_B). Choose the four angles to make three "
                "cosines +1/√2 and the minus-sign one −1/√2."
            ),
            model_step=(
                "Take |Φ⁺⟩ = (|00⟩+|11⟩)/√2 with A = Z (angle 0), A′ = X (angle π/2), "
                "B = (Z+X)/√2 (angle π/4), B′ = (Z−X)/√2 (angle −π/4). On |Φ⁺⟩ the "
                "correlator of x–z-plane observables is E = cos(θ_A − θ_B):\n"
                "E(A,B) = cos(−π/4) = 1/√2, E(A,B′) = cos(π/4) = 1/√2, "
                "E(A′,B) = cos(π/4) = 1/√2, E(A′,B′) = cos(3π/4) = −1/√2.\n"
                "⟨S⟩ = 1/√2 + 1/√2 + 1/√2 − (−1/√2) = 4/√2 = 2√2 (verified "
                "numerically). Quantum mechanics saturates Tsirelson's bound — "
                "violating classical locality maximally, yet staying strictly below "
                "the no-signalling maximum of 4 (the PR-box value)."
            ),
        ),
    ],
)
