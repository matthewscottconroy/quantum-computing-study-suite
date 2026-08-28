"""Problem: vqa_parameter_shift — general-shift parameter-shift rule.

Verified numerically: for U(θ)=exp(-iθP/2) with P²=I, the identity
dE/dθ = [E(θ+s) − E(θ−s)]/(2 sin s) holds for arbitrary shifts s.
"""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="vqa_parameter_shift",
    topic="VQA",
    title="Parameter-Shift Rule with an Arbitrary Shift",
    statement=(
        "Let U(θ) = exp(−iθP/2) with P a Pauli string (so P² = I), acting inside a "
        "variational circuit, and let\n\n"
        "    E(θ) = ⟨ψ| U†(θ) H U(θ) |ψ⟩\n\n"
        "be the measured cost (H an observable; fixed |ψ⟩ absorbs the rest of the "
        "circuit). The standard parameter-shift rule uses shifts of ±π/2. Here you "
        "derive the rule for an ARBITRARY shift s and find the statistically optimal "
        "choice."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Using P² = I, show U(θ) = cos(θ/2) I − i sin(θ/2) P and deduce that "
                "E(θ) = A + B cos θ + C sin θ for θ-independent constants A, B, C "
                "(give them as expectation values in |ψ⟩)."
            ),
            points=4,
            rubric=[
                "Series expansion (or spectral argument) with P² = I gives "
                "U(θ) = cos(θ/2)I − i sin(θ/2)P.",
                "Expands U†HU into the four terms and groups with double-angle "
                "identities: cos²(θ/2) = (1+cosθ)/2, sin²(θ/2) = (1−cosθ)/2, "
                "2 sin(θ/2)cos(θ/2) = sinθ.",
                "Identifies A = ⟨H + PHP⟩/2, B = ⟨H − PHP⟩/2, C = ⟨i[H, P]/2⟩ — i.e. "
                "C from the cross term i⟨[H,P]⟩-type expression (accept "
                "C = (i/2)⟨[H,P]⟩ or equivalent sign convention consistent with the "
                "student's expansion).",
                "Concludes E(θ) = A + B cosθ + C sinθ: a pure first-harmonic "
                "trigonometric polynomial.",
            ],
            model_solution=(
                "Splitting the exponential series into even/odd powers and using "
                "P² = I: U(θ) = cos(θ/2)I − i sin(θ/2)P. Then\n"
                "U†HU = [cos(θ/2)I + i sin(θ/2)P] H [cos(θ/2)I − i sin(θ/2)P]\n"
                "= cos²(θ/2) H + sin²(θ/2) PHP + i sin(θ/2)cos(θ/2)(PH − HP).\n"
                "Taking ⟨ψ|·|ψ⟩ and using the double-angle identities:\n"
                "E(θ) = ⟨H + PHP⟩/2 + ⟨H − PHP⟩/2 · cosθ + (i/2)⟨[P, H]⟩ · sinθ\n"
                "≡ A + B cosθ + C sinθ. All three coefficients are θ-independent "
                "expectation values in |ψ⟩; note C is real since i[P, H] is Hermitian."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Derive the general-shift rule: for any s with sin s ≠ 0,\n"
                "    dE/dθ = [E(θ + s) − E(θ − s)] / (2 sin s) ,\n"
                "and check it reduces to the standard rule at s = π/2. Why is this an "
                "EXACT identity rather than a finite-difference approximation?"
            ),
            points=3,
            rubric=[
                "Computes E(θ+s) − E(θ−s) = −2B sinθ sin s + 2C cosθ sin s using "
                "angle-addition formulas.",
                "Compares with dE/dθ = −B sinθ + C cosθ to get the identity; s = π/2 "
                "gives the familiar [E(θ+π/2) − E(θ−π/2)]/2.",
                "Exactness: E is exactly a first-harmonic trig polynomial (part a), and "
                "the central difference of sin/cos at any shift reproduces the "
                "derivative up to the known factor sin s — no higher harmonics exist to "
                "contribute error (unlike generic finite differences on unknown "
                "functions).",
            ],
            model_solution=(
                "From E(θ) = A + B cosθ + C sinθ:\n"
                "E(θ+s) − E(θ−s) = B[cos(θ+s) − cos(θ−s)] + C[sin(θ+s) − sin(θ−s)]\n"
                "= −2B sinθ sin s + 2C cosθ sin s = 2 sin s · (−B sinθ + C cosθ) "
                "= 2 sin s · E′(θ).\n"
                "Hence E′(θ) = [E(θ+s) − E(θ−s)]/(2 sin s) for every s with sin s ≠ 0 "
                "(verified numerically for s = π/2, 0.4, 1.1 on a random H and state). "
                "At s = π/2, sin s = 1: the standard rule. It is exact because part (a) "
                "shows E contains only the first harmonic in θ; a central difference of "
                "cosθ and sinθ is EXACTLY proportional to their derivatives, with the "
                "universal factor sin s. Finite differences are only approximate for "
                "functions with unknown higher-order structure — here the structure is "
                "fully known."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "On hardware, E(θ ± s) are estimated from N shots each, with per-point "
                "variance ≈ σ² independent of s (to leading order). Compute the variance "
                "of the gradient estimator ĝ = [Ê(θ+s) − Ê(θ−s)]/(2 sin s) and show it "
                "is minimised at s = π/2. What happens as s → 0, and what does this say "
                "about naive finite differences on a quantum computer?"
            ),
            points=3,
            rubric=[
                "Var(ĝ) = [Var(Ê₊) + Var(Ê₋)]/(4 sin²s) = σ²/(2N sin²s)-type expression "
                "(any consistent bookkeeping of the two independent estimates accepted).",
                "sin²s ≤ 1 with equality at s = π/2 (±π/2 mod 2π), so the variance is "
                "minimised exactly at the standard shift.",
                "As s → 0 the variance diverges like 1/s²: small-shift finite "
                "differences amplify shot noise unboundedly, which is why the "
                "large-shift exact rule is preferred on quantum hardware.",
            ],
            model_solution=(
                "The two estimates are independent, so\n"
                "Var(ĝ) = [Var(Ê(θ+s)) + Var(Ê(θ−s))]/(2 sin s)² ≈ 2(σ²/N)/(4 sin²s) "
                "= σ²/(2N sin²s).\n"
                "The s-dependence is the prefactor 1/sin²s, minimised where |sin s| = 1, "
                "i.e. s = π/2: the standard parameter-shift rule is not merely "
                "conventional but statistically optimal (for s-independent σ²). As "
                "s → 0, Var(ĝ) ~ σ²/(2N s²) → ∞: a naive small-step finite difference — "
                "the natural instinct from classical numerics — is the worst possible "
                "choice under shot noise, since the signal difference shrinks linearly "
                "in s while the noise stays fixed. The exact π/2-shift rule gets an "
                "unbiased derivative with the best attainable constant."
            ),
        ),
    ],
)
