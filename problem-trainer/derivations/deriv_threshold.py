"""Derivation: threshold theorem sketch via concatenation.

Recursion arithmetic verified: p_l = (cp)^{2^l}/c; for c = 1e4, p = 1e-5,
levels l = 1..4 give 1e-6, 1e-8, 1e-12, 1e-20.
"""
from __future__ import annotations
from core.models import Derivation, Step

DERIVATION = Derivation(
    id="deriv_threshold",
    title="The Threshold Theorem (Sketch)",
    goal=(
        "Derive the concatenation recursion p → cp², solve it, and conclude that "
        "arbitrarily long quantum computation is possible below a constant error "
        "threshold."
    ),
    steps=[
        Step(
            step_id="s1",
            prompt=(
                "Why does error correction alone not immediately solve the noise "
                "problem — what is the catch when the encoding/syndrome/recovery "
                "circuitry is itself built from noisy gates, and what design principle "
                "addresses it?"
            ),
            expected=(
                "The QEC circuitry is made of faulty components too, and naive "
                "circuits can spread a single fault into multiple data errors "
                "(exceeding the code's correction power). The fix is FAULT-TOLERANT "
                "gadget design: transversal/carefully scheduled operations, verified "
                "ancillas, repeated syndrome extraction — ensuring one component "
                "fault causes at most one error per code block."
            ),
            hint=(
                "Think about what a single faulty CNOT inside the syndrome-extraction "
                "circuit can do to the data block."
            ),
            model_step=(
                "Correction machinery is noisy: a faulty gate inside syndrome "
                "extraction can propagate (e.g. a bad CNOT copies its error onto the "
                "data), potentially turning one fault into a multi-qubit error the "
                "code cannot fix — the cure could be worse than the disease. "
                "Fault-tolerant design tames this: transversal gates (bitwise, never "
                "coupling two qubits of the same block), verified/flagged ancilla "
                "states, and repeated syndrome measurements guarantee that any SINGLE "
                "component fault produces at most one error in each code block — "
                "within a distance-3 code's correction power."
            ),
        ),
        Step(
            step_id="s2",
            prompt=(
                "Consider a fault-tolerant gadget (logical gate + error correction) "
                "built on a distance-3 code, with physical components failing "
                "independently with probability p. Argue that the LOGICAL failure "
                "probability of the gadget is at most c·p², and say what the constant "
                "c counts."
            ),
            expected=(
                "By fault tolerance, one fault anywhere is corrected; a logical "
                "failure requires at least TWO faults in the same gadget. Union bound "
                "over pairs of fault locations: P(fail) ≤ (number of malignant pairs)·"
                "p² ≡ c·p², where c counts pairs of locations whose simultaneous "
                "failure defeats the gadget (c ~ A²/2-ish for A locations, e.g. "
                "~10⁴)."
            ),
            hint=(
                "If single faults are always handled, what is the cheapest way for "
                "the gadget to fail? Count those events with a union bound."
            ),
            model_step=(
                "A distance-3 fault-tolerant gadget corrects any single component "
                "fault, so failure needs ≥ 2 faults. If the gadget has A fault "
                "locations, the union bound over pairs gives "
                "P(fail) ≤ Σ_malignant pairs p² = c·p², where c ≤ A(A−1)/2 counts the "
                "MALIGNANT pairs — pairs whose joint failure actually causes a logical "
                "error (many pairs are benign). For classic constructions A ~ 10²–10³ "
                "and c ~ 10⁴–10⁶; c is a property of the code and gadget design, not "
                "of the hardware."
            ),
        ),
        Step(
            step_id="s3",
            prompt=(
                "Now concatenate: encode each physical qubit of the code again in the "
                "same code, recursively, l levels deep. Write the recursion for the "
                "level-(l+1) failure probability in terms of level-l, and explain why "
                "the same constant c appears at every level."
            ),
            expected=(
                "p_{l+1} = c·p_l² with p₀ = p: a level-(l+1) gadget is the same "
                "gadget diagram whose 'components' are level-l gadgets, failing "
                "independently with probability p_l — so the two-fault counting "
                "argument repeats verbatim with the same malignant-pair count c "
                "(self-similarity of concatenation)."
            ),
            hint=(
                "At level l+1, what plays the role of a 'physical component', and "
                "what is its failure probability?"
            ),
            model_step=(
                "A level-(l+1) logical gadget is built from the SAME circuit diagram, "
                "but each elementary component is now a level-l encoded gadget, "
                "failing with probability p_l. The fault-tolerance argument is "
                "structure-only, so it applies unchanged: failure needs two level-l "
                "sub-gadget failures in a malignant pair, giving\n"
                "    p_{l+1} = c · p_l²,   p₀ = p.\n"
                "Concatenation is self-similar — the constant c is inherited from the "
                "gadget design at every level."
            ),
        ),
        Step(
            step_id="s4",
            prompt=(
                "Solve the recursion p_{l+1} = c·p_l² in closed form and identify the "
                "threshold: for which p does the logical error vanish as l grows, and "
                "how fast?"
            ),
            expected=(
                "Multiplying by c: cp_{l+1} = (cp_l)², so cp_l = (cp)^{2^l} and "
                "p_l = (cp)^{2^l}/c. If p < p_th = 1/c the logical error falls DOUBLY "
                "exponentially in l; above threshold it diverges. (E.g. c = 10⁴, "
                "p = 10⁻⁵: p_l = 10^{−2^l−4}.)"
            ),
            hint=(
                "Substitute q_l = c·p_l to turn the recursion into pure squaring."
            ),
            model_step=(
                "Let q_l = c·p_l. Then q_{l+1} = q_l², so q_l = q₀^{2^l} = (cp)^{2^l}, "
                "i.e.\n"
                "    p_l = (cp)^{2^l} / c.\n"
                "The behaviour is governed by cp: if p < p_th = 1/c then cp < 1 and "
                "p_l falls doubly exponentially with level (squaring the suppression "
                "each level); if p > 1/c the bound explodes. Concretely with c = 10⁴, "
                "p = 10⁻⁵ (cp = 0.1): p₁ = 10⁻⁶, p₂ = 10⁻⁸, p₃ = 10⁻¹², p₄ = 10⁻²⁰ "
                "(verified arithmetically) — four levels take you from one error per "
                "hundred thousand gates to one per 10²⁰."
            ),
        ),
        Step(
            step_id="s5",
            prompt=(
                "Estimate the overhead: each level multiplies the qubit/gate count by "
                "a constant G. Express the cost of reaching logical error ε and show "
                "it is polylogarithmic in 1/ε."
            ),
            expected=(
                "Need (cp)^{2^l}/c ≤ ε ⇒ 2^l ≥ log(1/cε)/log(1/cp) ⇒ "
                "l = O(log log(1/ε)); overhead G^l = 2^{l·log₂G} = "
                "O((log(1/ε))^{log₂ G}) = polylog(1/ε). Doubly-exponential error "
                "suppression is what makes the overhead only polylog."
            ),
            hint=(
                "Solve p_l ≤ ε for 2^l first, then substitute into G^l — note "
                "G^l = (2^l)^{log₂ G}."
            ),
            model_step=(
                "Setting (cp)^{2^l}/c ≤ ε and solving: 2^l ≥ log(1/(cε))/log(1/(cp)), "
                "so l = ⌈log₂ of that⌉ = O(log log(1/ε)). The physical resources per "
                "logical gadget grow as G^l = (2^l)^{log₂G} = "
                "O( (log 1/ε)^{log₂ G} ): POLYLOGARITHMIC in the target error. The "
                "magic pairing: error falls doubly exponentially in l while cost "
                "grows only singly exponentially in l — so cost as a function of "
                "achieved error is merely polylog. For a circuit of T gates one takes "
                "ε ~ δ/T, keeping total overhead O(polylog(T/δ))."
            ),
        ),
        Step(
            step_id="s6",
            prompt=(
                "State the threshold theorem in full, and note two caveats that the "
                "constant-c sketch sweeps under the rug."
            ),
            expected=(
                "Theorem (informal): if physical components fail independently with "
                "probability p < p_th (a constant set by the code/gadget design), any "
                "ideal quantum circuit of size T can be simulated with total error ≤ δ "
                "using O(T·polylog(T/δ)) noisy components. Caveats (any two): error "
                "model assumptions (independence/locality; correlated or coherent "
                "noise weakens bounds), fresh ancillas needed throughout, classical "
                "processing assumed fast/reliable, threshold values from this crude "
                "counting are pessimistic vs. modern codes (e.g. surface code ~1%), "
                "geometric locality constraints, non-Clifford gates need magic-state "
                "distillation."
            ),
            hint=(
                "One caveat concerns the NOISE MODEL, another the auxiliary resources "
                "or specific gates the sketch quietly assumed."
            ),
            model_step=(
                "Threshold theorem: there is a constant p_th > 0, depending only on "
                "the code and gadget constructions, such that for physical error "
                "rates p < p_th, every ideal quantum circuit with T locations can be "
                "executed fault-tolerantly to within any total error δ at a cost "
                "multiplied by O(polylog(T/δ)). Arbitrarily long quantum computation "
                "is possible on imperfect hardware.\n"
                "Caveats: (1) the noise model matters — the counting assumed "
                "independent, uncorrelated stochastic faults; strongly correlated or "
                "adversarial noise degrades or invalidates the bound; (2) hidden "
                "resources — a constant supply of fresh, verified ancilla qubits, "
                "fast reliable classical decoding, and parallel operations are "
                "assumed, and universal computation additionally needs non-transversal "
                "gates supplied via e.g. magic-state distillation. Also, real "
                "thresholds are architecture-dependent: this crude pair-counting gives "
                "~10⁻⁴, while surface-code estimates approach ~10⁻²."
            ),
        ),
    ],
)
