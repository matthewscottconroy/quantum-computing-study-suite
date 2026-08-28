"""Problem: alg_qpe_error — quantum phase estimation error analysis."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="alg_qpe_error",
    topic="Algorithms",
    title="Phase Estimation: Accuracy and Register Size",
    statement=(
        "Quantum phase estimation (QPE) with a t-qubit register estimates the phase "
        "φ ∈ [0,1) of an eigenvalue e^{2πiφ} of a unitary U. After the controlled-U "
        "powers and the inverse QFT, measuring the register yields outcome m with "
        "amplitude\n\n"
        "    α_m = (1/2ᵗ) Σ_{k=0}^{2ᵗ−1} e^{2πik(φ − m/2ᵗ)} .\n\n"
        "Write b for the integer with b/2ᵗ the best t-bit approximation to φ from "
        "below, and δ = φ − b/2ᵗ ∈ [0, 2⁻ᵗ). (This is the analysis of "
        "Nielsen & Chuang §5.2.1.)"
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Show that if φ has an exact t-bit expansion (δ = 0), the measurement "
                "yields m = b with probability 1. Use the geometric-series form of α_m."
            ),
            points=3,
            rubric=[
                "Sums the geometric series: α_m = (1/2ᵗ)(1 − e^{2πi(2ᵗφ − m)})/"
                "(1 − e^{2πi(φ − m/2ᵗ)}) for φ ≠ m/2ᵗ.",
                "For δ = 0 and m = b: every term in the sum equals 1, so α_b = 1 "
                "(the exponent vanishes for all k).",
                "For m ≠ b: numerator vanishes (2ᵗφ − m is a nonzero integer... "
                "precisely: e^{2πi(2ᵗφ−m)} = 1 while the denominator is nonzero), so "
                "α_m = 0 — hence outcome b with certainty (normalisation confirms).",
            ],
            model_solution=(
                "If δ = 0 then 2ᵗφ = b is an integer. For m = b every summand is "
                "e^{2πik·0} = 1, so α_b = (1/2ᵗ)·2ᵗ = 1. For m ≠ b, α_m is a geometric "
                "series with ratio r = e^{2πi(b−m)/2ᵗ} ≠ 1, so "
                "α_m = (1/2ᵗ)(1 − r^{2ᵗ})/(1 − r), and r^{2ᵗ} = e^{2πi(b−m)} = 1 makes "
                "the numerator zero: α_m = 0. Thus the distribution is a point mass at "
                "m = b — QPE is deterministic for exactly representable phases "
                "(verified numerically for t = 5, φ = 6/32)."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "For general φ, bound the tail of the distribution: show that the "
                "probability that the outcome m differs from b by more than e "
                "(in the wraparound/mod-2ᵗ sense) satisfies\n"
                "    p(|m − b| > e) ≤ 1/(2(e − 1)).\n"
                "You may use |1 − e^{iθ}| ≤ |θ| and |1 − e^{iθ}| ≥ 2|θ|/π for |θ| ≤ π."
            ),
            points=4,
            rubric=[
                "Bounds a single amplitude, e.g. |α_{b+l}| ≤ 1/(2|l − 2ᵗδ|): numerator "
                "bounded by |1 − e^{iθ}| ≤ 2, denominator lower-bounded via "
                "|1 − e^{iθ}| ≥ 2|θ|/π applied to θ = 2π(δ − l/2ᵗ); any correct "
                "constant chain accepted.",
                "Sums over the tail |l| > e: p ≤ (1/4)[Σ_{l=e}^{...} 1/l² + symmetric], "
                "compares with the integral/telescoping bound Σ_{l≥e} 1/l² ≤ 1/(e−1) "
                "(or ∫ dl/l²).",
                "Arrives at p(|m − b| > e) ≤ 1/(2(e − 1)) (equivalent constants from a "
                "correct derivation accepted).",
            ],
            model_solution=(
                "With outcome b + l (l ≠ 0, mod 2ᵗ), the geometric sum gives\n"
                "|α_{b+l}| = (1/2ᵗ)·|1 − e^{2πi(2ᵗδ − l)}| / |1 − e^{2πi(δ − l/2ᵗ)}|.\n"
                "The numerator is at most 2. For the denominator, with "
                "θ = 2π(δ − l/2ᵗ) ∈ [−π, π] we use |1 − e^{iθ}| ≥ 2|θ|/π to get "
                "|1 − e^{iθ}| ≥ 4|l − 2ᵗδ|/2ᵗ. Hence |α_{b+l}| ≤ 1/(2|l − 2ᵗδ|) and, "
                "since 0 ≤ 2ᵗδ < 1, |α_{b+l}|² ≤ 1/(4(l − 1)²) for l > 0 and "
                "≤ 1/(4l²) for l < 0. Summing the tail:\n"
                "p(|m−b| > e) ≤ (1/4)[Σ_{l=e+1}^{∞} 1/(l−1)² + Σ_{l=e+1}^{∞} 1/l²] "
                "≤ (1/4)·2·Σ_{l=e}^{∞} 1/l² ≤ (1/2)∫_{e−1}^{∞} dl/l² = 1/(2(e−1)).\n"
                "(Numerically for t = 5, φ = 0.17 the observed tail masses are well "
                "under this bound.)"
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Conclude the register-size rule: to obtain φ accurate to n bits "
                "(error < 2⁻ⁿ) with failure probability at most ε, it suffices to take\n"
                "    t = n + ⌈log₂(2 + 1/(2ε))⌉ .\n"
                "Derive this from (b), and evaluate t for n = 4, ε = 0.1."
            ),
            points=3,
            rubric=[
                "Accuracy link: outcome within e of b gives phase error < 2⁻ⁿ provided "
                "e ≤ 2^{t−n} − 1, so choose e = 2^{t−n} − 1.",
                "Requires 1/(2(e−1)) ≤ ε ⇒ e ≥ 1/(2ε) + 1 ⇒ 2^{t−n} ≥ 2 + 1/(2ε), giving "
                "t = n + ⌈log₂(2 + 1/(2ε))⌉.",
                "Numeric case: n = 4, ε = 0.1 ⇒ log₂(2 + 5) = log₂7 ≈ 2.81 ⇒ ⌈·⌉ = 3 ⇒ "
                "t = 7.",
            ],
            model_solution=(
                "If |m − b| ≤ e then |m/2ᵗ − φ| ≤ (e + 1)/2ᵗ; demanding this be at most "
                "2⁻ⁿ means e + 1 ≤ 2^{t−n}, i.e. e = 2^{t−n} − 1 works. By part (b) the "
                "failure probability is at most 1/(2(e − 1)) ≤ ε provided "
                "e ≥ 1 + 1/(2ε), i.e. 2^{t−n} ≥ 2 + 1/(2ε). Taking logs and rounding up: "
                "t = n + ⌈log₂(2 + 1/(2ε))⌉ suffices.\n"
                "For n = 4, ε = 0.1: 2 + 1/(0.2) = 7, ⌈log₂7⌉ = 3, so t = 7 qubits — "
                "three extra qubits buy 90% confidence in 4 accurate bits."
            ),
        ),
    ],
)
