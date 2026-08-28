"""Derivation: the no-cloning theorem."""
from __future__ import annotations
from core.models import Derivation, Step

DERIVATION = Derivation(
    id="deriv_no_cloning",
    title="The No-Cloning Theorem",
    goal=(
        "Prove that no unitary machine can copy an arbitrary unknown quantum state, "
        "and locate exactly which states CAN be copied."
    ),
    steps=[
        Step(
            step_id="s1",
            prompt=(
                "Formalise the claim: write down what a universal cloning machine would "
                "have to do, as a unitary U acting on the input state together with a "
                "blank register (and possibly an ancilla). What equation must hold for "
                "EVERY input |ψ⟩?"
            ),
            expected=(
                "A cloner is a unitary U with U(|ψ⟩⊗|e⟩) = |ψ⟩⊗|ψ⟩ (times possibly a "
                "ψ-dependent ancilla/phase) for ALL states |ψ⟩, where |e⟩ is a fixed "
                "blank/ready state. Key points: U is fixed (independent of ψ), the "
                "blank state is fixed, and the requirement is universal over ψ."
            ),
            hint=(
                "The machine cannot depend on the unknown state — a single fixed U and "
                "a fixed blank |e⟩ must work for every possible input."
            ),
            model_step=(
                "Suppose there is a fixed unitary U and fixed blank state |e⟩ such "
                "that for every state |ψ⟩:  U(|ψ⟩ ⊗ |e⟩) = |ψ⟩ ⊗ |ψ⟩  (an ancilla "
                "register ending in a possibly ψ-dependent state |a_ψ⟩ can be carried "
                "along; the simplest form suffices for the core argument). "
                "Universality — one machine for all inputs — is the assumption we will "
                "contradict."
            ),
        ),
        Step(
            step_id="s2",
            prompt=(
                "Apply the cloning equation to two arbitrary states |ψ⟩ and |φ⟩ and "
                "take the inner product of the two output equations. What constraint on "
                "⟨ψ|φ⟩ do you get from the fact that U preserves inner products?"
            ),
            expected=(
                "⟨ψ|φ⟩·⟨e|e⟩ = ⟨ψ|φ⟩² (inner product of U(|ψ⟩|e⟩) with U(|φ⟩|e⟩); "
                "unitarity preserves it). With ⟨e|e⟩ = 1 this reads x = x² where "
                "x = ⟨ψ|φ⟩."
            ),
            hint=(
                "⟨U u | U v⟩ = ⟨u|v⟩ for any unitary. Compute both sides for "
                "u = |ψ⟩|e⟩, v = |φ⟩|e⟩."
            ),
            model_step=(
                "Unitarity: ⟨ψ⊗e| U†U |φ⊗e⟩ = ⟨ψ|φ⟩⟨e|e⟩ = ⟨ψ|φ⟩. But using the "
                "cloning outputs, the same quantity equals ⟨ψ⊗ψ|φ⊗φ⟩ = ⟨ψ|φ⟩². "
                "Hence x = x² with x = ⟨ψ|φ⟩. (With a ψ-dependent ancilla the equation "
                "becomes x = x²⟨a_ψ|a_φ⟩, and |x| ≥ |x|² still forces the same "
                "conclusion below.)"
            ),
        ),
        Step(
            step_id="s3",
            prompt=(
                "Solve the constraint and interpret it: for which pairs |ψ⟩, |φ⟩ can "
                "the equation hold, and why does that contradict universal cloning?"
            ),
            expected=(
                "x = x² has only the solutions x = 0 and x = 1: the two states must be "
                "orthogonal or identical. A universal cloner must handle non-orthogonal "
                "pairs (e.g. |0⟩ and |+⟩ with ⟨0|+⟩ = 1/√2, giving 1/√2 ≠ 1/2) — "
                "contradiction. Hence no universal cloner exists."
            ),
            hint=(
                "x² − x = x(x − 1) = 0. Are all pairs of quantum states orthogonal or "
                "identical?"
            ),
            model_step=(
                "x = x² ⇒ x(x−1) = 0 ⇒ ⟨ψ|φ⟩ ∈ {0, 1}: the pair is either orthogonal "
                "or the same state. But the state space contains non-orthogonal "
                "distinct pairs — e.g. |0⟩, |+⟩ with ⟨0|+⟩ = 1/√2, which would demand "
                "1/√2 = 1/2. Contradiction: no single unitary clones all states. Only "
                "sets of mutually orthogonal states — i.e. classical information "
                "embedded in a known basis — can be copied (a CNOT clones |0⟩/|1⟩ "
                "perfectly)."
            ),
        ),
        Step(
            step_id="s4",
            prompt=(
                "Give the alternative one-line linearity argument: assume the cloner "
                "works on |0⟩ and |1⟩ and test it on |+⟩ = (|0⟩+|1⟩)/√2. What goes "
                "wrong?"
            ),
            expected=(
                "Linearity forces U(|+⟩|e⟩) = [U(|0⟩|e⟩) + U(|1⟩|e⟩)]/√2 = "
                "(|00⟩ + |11⟩)/√2 — an entangled Bell state — whereas cloning demands "
                "|+⟩|+⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2. These differ, so cloning fails on "
                "superpositions: copying the basis 'entangles' rather than clones."
            ),
            hint=(
                "Apply U to the superposition term by term (linearity!), then compare "
                "with the desired output |+⟩⊗|+⟩."
            ),
            model_step=(
                "If U(|0⟩|e⟩) = |00⟩ and U(|1⟩|e⟩) = |11⟩, then by linearity\n"
                "U(|+⟩|e⟩) = (|00⟩ + |11⟩)/√2,\n"
                "the maximally entangled Bell state — NOT the required product "
                "|+⟩|+⟩ = ½(|00⟩+|01⟩+|10⟩+|11⟩). The two outputs differ (one is "
                "entangled, the other is a product), so a machine correct on the basis "
                "necessarily fails on its superpositions. Cloning is forbidden by "
                "linearity alone — unitarity wasn't even needed."
            ),
        ),
        Step(
            step_id="s5",
            prompt=(
                "Draw the consequences: name two places where no-cloning is essential "
                "to quantum information (one protective, one seemingly obstructive), "
                "and reconcile cloning's impossibility with the existence of "
                "teleportation."
            ),
            expected=(
                "Protective: security of QKD (an eavesdropper cannot copy in-flight "
                "states without disturbance) — or: enforces no-signalling. "
                "Obstructive: no classical-style repeaters/backup copies; QEC must "
                "protect information without reading or copying it (hence syndrome "
                "measurement/redundant encoding, not duplication). Teleportation is "
                "consistent because the original is destroyed by Alice's measurement — "
                "the state is MOVED, not copied; at no time do two copies exist."
            ),
            hint=(
                "Think of eavesdroppers, of amplifiers/repeaters, and of what happens "
                "to Alice's original during teleportation."
            ),
            model_step=(
                "(1) Protective: quantum key distribution — Eve cannot copy the "
                "transmitted qubits for later analysis; any information gain disturbs "
                "the states and shows up in the error rate. No-cloning also blocks "
                "using entanglement for superluminal signalling (a cloner would let "
                "Bob distinguish Alice's measurement bases statistically). "
                "(2) Obstructive: there is no naive backup/amplify strategy for "
                "quantum memories or channels — classical repeaters copy and re-send, "
                "which is illegal; instead, error correction encodes one logical qubit "
                "nonlocally in many physical qubits and measures only syndromes, and "
                "long links need entanglement-swapping quantum repeaters. "
                "Teleportation does not violate the theorem: Alice's Bell measurement "
                "destroys her copy at the same moment the state becomes recoverable at "
                "Bob's side — exactly one copy exists at every stage."
            ),
        ),
    ],
)
