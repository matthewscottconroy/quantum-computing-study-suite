"""Problem: qec_threshold_estimate — concatenation and the threshold.

Arithmetic verified: c = 10^4, p = 10^-5 -> cp = 0.1; p_l = (cp)^(2^l)/c gives
p_3 = 1e-12 (> 1e-15) and p_4 = 1e-20 (<= 1e-15), so l = 4 levels needed.
"""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="qec_threshold_estimate",
    topic="Error Correction",
    title="Concatenation and a Threshold Estimate",
    statement=(
        "A distance-3 code corrects any single fault in a logical gate 'gadget'. If "
        "physical components fail independently with probability p, a level-1 encoded "
        "gadget fails only when ≥ 2 of its components fault, so its failure probability "
        "is at most c·p², where c counts the malignant pairs of fault locations "
        "(typically c ~ 10⁴ for early fault-tolerant constructions). Concatenation "
        "encodes each qubit of the code again in the same code, level after level."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Let p_l be the failure probability of a level-l encoded gadget, with "
                "p₀ = p and the recursion p_{l+1} = c·p_l². Solve the recursion in "
                "closed form and identify the threshold p_th below which p_l → 0."
            ),
            points=4,
            rubric=[
                "Iterates or telescopes the recursion; the clean route: define "
                "q_l = c·p_l, then q_{l+1} = q_l², so q_l = q₀^{2^l} = (cp)^{2^l}.",
                "Closed form p_l = (cp)^{2^l} / c.",
                "Threshold: p_l → 0 (doubly exponentially) iff cp < 1, i.e. "
                "p_th = 1/c; above it the bound blows up.",
            ],
            model_solution=(
                "Multiply the recursion by c: (c p_{l+1}) = (c p_l)². So q_l = c p_l "
                "squares at each level: q_l = q₀^{2^l} = (cp)^{2^l}, giving\n"
                "    p_l = (cp)^{2^l} / c.\n"
                "If cp < 1 this falls doubly exponentially in the level number l; if "
                "cp > 1 it grows. The threshold is p_th = 1/c: physical error rates "
                "below 1/c can be suppressed to any desired logical error rate by "
                "adding levels."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Take c = 10⁴ (so p_th = 10⁻⁴) and a physical error rate p = 10⁻⁵. "
                "How many levels of concatenation are needed for a logical failure "
                "probability at most 10⁻¹⁵ per gadget? Show the arithmetic."
            ),
            points=3,
            rubric=[
                "Computes cp = 10⁻¹ and applies p_l = (0.1)^{2^l}/10⁴.",
                "Checks levels: l = 3 → (0.1)⁸/10⁴ = 10⁻⁸⁻⁴ = 10⁻¹² (insufficient); "
                "l = 4 → (0.1)¹⁶/10⁴ = 10⁻²⁰ ≤ 10⁻¹⁵ (sufficient).",
                "Answer: 4 levels (accept a general formula "
                "2^l ≥ log(1/(cε))/log(1/(cp)) evaluated correctly).",
            ],
            model_solution=(
                "cp = 10⁴·10⁻⁵ = 0.1. Then p_l = (0.1)^{2^l}/10⁴ = 10^{−2^l − 4}:\n"
                "l = 1: 10⁻⁶;  l = 2: 10⁻⁸;  l = 3: 10⁻¹²;  l = 4: 10⁻²⁰.\n"
                "We need 10^{−2^l−4} ≤ 10⁻¹⁵, i.e. 2^l ≥ 11, so l = 4 (2⁴ = 16). Three "
                "levels give only 10⁻¹², four give 10⁻²⁰ — comfortably below target. "
                "(Verified arithmetically.)"
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Estimate the resource overhead: if one level of encoding multiplies "
                "the number of physical qubits (and gadget size) by a constant "
                "G (say G ≈ 7–100), express the overhead after l levels, substitute the "
                "l from part (b), and explain why the total overhead for achieving "
                "error ε scales polylogarithmically in 1/ε. State the resulting "
                "threshold theorem informally."
            ),
            points=3,
            rubric=[
                "Overhead after l levels is G^l (qubits/gates per logical gadget).",
                "Inverts the suppression formula: to reach error ε need "
                "2^l ~ log(1/ε)-ish, i.e. l = O(log log(1/ε)), so overhead "
                "G^l = (log(1/ε))^{log₂G} — polylog in 1/ε. (Substituting l = 4, "
                "G = 7: 7⁴ ≈ 2400 physical qubits per logical qubit.)",
                "Threshold theorem stated: provided p < p_th, any quantum circuit of "
                "size T can be simulated fault-tolerantly with error ε at multiplicative "
                "cost polylog(T/ε) — arbitrarily long quantum computation is possible "
                "with noisy hardware.",
            ],
            model_solution=(
                "Each level replaces every qubit/gadget by G of them, so l levels cost "
                "G^l. From p_l = (cp)^{2^l}/c ≤ ε we need "
                "2^l ≥ log(1/(cε))/log(1/(cp)), so l = O(log log(1/ε)) and the overhead "
                "is G^l = 2^{l log₂ G} = O((log(1/ε))^{log₂ G}) — polylogarithmic in "
                "1/ε. For the concrete numbers of (b) with G = 7 (Steane code): "
                "7⁴ = 2401 physical qubits per logical qubit; with G = 100 gadget "
                "locations, 100⁴ = 10⁸ locations per logical gadget — large but "
                "poly-log-bounded.\n"
                "Threshold theorem (informal): if the physical error rate per component "
                "is below a constant threshold p_th, then any ideal quantum circuit with "
                "T gates can be executed to within total error ε using "
                "O(T·polylog(T/ε)) noisy components. Reliability is a constant-factor "
                "hardware demand, not a scaling obstacle."
            ),
        ),
    ],
)
