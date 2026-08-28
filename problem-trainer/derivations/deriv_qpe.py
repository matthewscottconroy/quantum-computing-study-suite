"""Derivation: quantum phase estimation — kickback + inverse QFT."""
from __future__ import annotations
from core.models import Derivation, Step

DERIVATION = Derivation(
    id="deriv_qpe",
    title="Quantum Phase Estimation",
    goal=(
        "Show why phase kickback followed by an inverse QFT lets a t-qubit register "
        "read out the eigenphase φ of U|u⟩ = e^{2πiφ}|u⟩."
    ),
    steps=[
        Step(
            step_id="s1",
            prompt=(
                "Start with one control qubit in |+⟩ and the eigenstate |u⟩. Apply "
                "controlled-U^{2^j}. What is the state of the CONTROL qubit afterwards, "
                "and why does the target stay unchanged? (This is phase kickback.)"
            ),
            expected=(
                "The control ends in (|0⟩ + e^{2πi·2^j·φ}|1⟩)/√2 while the target stays "
                "|u⟩. Key mechanism: U^{2^j}|u⟩ = e^{2πi 2^j φ}|u⟩ is the SAME state up "
                "to a phase, and because the operation is controlled, that phase "
                "attaches only to the |1⟩ branch of the control — the eigenstate "
                "factors out."
            ),
            hint=(
                "Write c-U^{2^j} acting on (|0⟩+|1⟩)|u⟩/√2 branch by branch. What does "
                "U^{2^j} do to an eigenstate of U?"
            ),
            model_step=(
                "c-U^{2^j} (|0⟩+|1⟩)|u⟩/√2 = (|0⟩|u⟩ + |1⟩U^{2^j}|u⟩)/√2 "
                "= (|0⟩ + e^{2πi 2^j φ}|1⟩)|u⟩/√2. Since |u⟩ is an eigenstate, "
                "U^{2^j}|u⟩ = e^{2πi 2^j φ}|u⟩ differs from |u⟩ only by a phase, which — "
                "being attached to the |1⟩ branch of the control — becomes a RELATIVE "
                "phase on the control qubit. The target is unentangled and unchanged: "
                "the phase has been 'kicked back'."
            ),
        ),
        Step(
            step_id="s2",
            prompt=(
                "Now use t control qubits, qubit j controlling U^{2^j} "
                "(j = 0, …, t−1), all prepared in |+⟩. Write the joint register state "
                "after all controlled powers, as a tensor product."
            ),
            expected=(
                "Register state ⨂_{j=t−1}^{0} (|0⟩ + e^{2πi 2^j φ}|1⟩)/√2 — each "
                "control qubit independently carries phase e^{2πi 2^j φ} on its |1⟩; "
                "equivalently (1/√2^t) Σ_{k=0}^{2^t−1} e^{2πikφ}|k⟩ by expanding the "
                "product over bitstrings."
            ),
            hint=(
                "Each control interacts with the same |u⟩ via its own power of U — step "
                "1 applies to each independently. Multiply the phases along each "
                "computational-basis branch k."
            ),
            model_step=(
                "Each control qubit j undergoes its own kickback: "
                "(|0⟩ + e^{2πi 2^j φ}|1⟩)/√2. The register is the product "
                "⨂ⱼ(|0⟩ + e^{2πi2^jφ}|1⟩)/√2. Expanding over basis states "
                "k = Σⱼ kⱼ2^j: the branch |k⟩ accumulates phase "
                "Π_{j:kⱼ=1} e^{2πi2^jφ} = e^{2πikφ}, so the state is "
                "(1/√2^t) Σ_k e^{2πikφ}|k⟩ ⊗ |u⟩."
            ),
        ),
        Step(
            step_id="s3",
            prompt=(
                "Recall the QFT: QFT|m⟩ = (1/√2^t) Σ_k e^{2πikm/2^t}|k⟩. Suppose φ has "
                "an exact t-bit expansion, φ = m/2^t. What is the register state of "
                "step 2 in terms of the QFT, and what operation therefore reveals m?"
            ),
            expected=(
                "With φ = m/2^t the register state (1/√2^t)Σ_k e^{2πikm/2^t}|k⟩ is "
                "EXACTLY QFT|m⟩. Applying the inverse QFT maps it to the computational "
                "basis state |m⟩, so measuring yields m = 2^t φ (all t bits of φ) with "
                "certainty."
            ),
            hint=(
                "Compare the phases e^{2πikφ} with the QFT matrix elements "
                "e^{2πikm/2^t}. When are they identical?"
            ),
            model_step=(
                "Substituting φ = m/2^t, the register reads "
                "(1/√2^t) Σ_k e^{2πik·m/2^t}|k⟩ = QFT|m⟩ — the kickback phases have "
                "precomputed a Fourier transform of the answer. Applying QFT† "
                "(inverse QFT) gives exactly |m⟩, and measurement returns the t bits of "
                "φ deterministically. The circuit's arithmetic is 'free': it happens in "
                "the phases."
            ),
        ),
        Step(
            step_id="s4",
            prompt=(
                "For general φ (no exact t-bit expansion), the inverse QFT gives "
                "outcome m with amplitude α_m = (1/2^t)Σ_k e^{2πik(φ−m/2^t)}. Explain "
                "qualitatively why this distribution concentrates on the best t-bit "
                "approximations of φ — what kind of interference is at work?"
            ),
            expected=(
                "α_m is a geometric series: when m/2^t ≈ φ the phases e^{2πik(φ−m/2^t)} "
                "are nearly aligned (constructive interference), giving |α_m| close "
                "to 1; when m/2^t is far from φ the phases wind around the unit circle "
                "and largely cancel (destructive interference), suppressing |α_m| like "
                "1/(distance). Hence outcomes concentrate on m ≈ 2^t φ."
            ),
            hint=(
                "Think of the terms e^{2πik(φ−m/2^t)} as unit vectors in the complex "
                "plane. What happens to their sum when the angle increment is tiny vs. "
                "large?"
            ),
            model_step=(
                "α_m sums 2^t unit phasors with constant angular increment "
                "2π(φ − m/2^t). If m/2^t is within 2^{−t} of φ the increment is at most "
                "~2π·2^{−t}: the phasors barely rotate and add near-coherently, so "
                "|α_m| = O(1). For distant m the phasors wrap the circle many times and "
                "cancel; summing the geometric series shows "
                "|α_m| ≤ 1/(2·|distance in units of 2^{−t}|). The measurement therefore "
                "returns one of the two nearest t-bit fractions with probability "
                "≥ 8/π² ≈ 0.81, and the tail decays quadratically."
            ),
        ),
        Step(
            step_id="s5",
            prompt=(
                "Put it together: state the full QPE recipe and its two accuracy knobs "
                "— what does adding more register qubits buy, and how do you boost the "
                "success probability for a fixed target precision?"
            ),
            expected=(
                "Recipe: prepare t controls in |+⟩ and eigenstate |u⟩; apply controlled-"
                "U^{2^j}; apply inverse QFT; measure to get m with m/2^t ≈ φ. More "
                "qubits t increase precision (error ~2^{−t}); for n-bit precision with "
                "failure probability ≤ ε, take t = n + O(log(1/ε)) extra qubits (or "
                "repeat and take majority/median). Some formulation of both knobs "
                "(precision from t, confidence from extra qubits/repetition) required."
            ),
            hint=(
                "One knob controls the spacing of the readable grid m/2^t; the other "
                "controls how much probability leaks outside the nearest grid points."
            ),
            model_step=(
                "QPE: (1) t-qubit register in |+⟩^⊗t alongside |u⟩; (2) controlled-"
                "U^{2^j} from qubit j (kickback writes e^{2πikφ} onto branch k); "
                "(3) inverse QFT; (4) measure m, estimate φ ≈ m/2^t. Precision: the "
                "readable grid has spacing 2^{−t}, so each extra qubit halves the "
                "error. Confidence: the concentration analysis gives failure "
                "probability ≤ 1/(2(e−1)) for error beyond e grid points, so choosing "
                "t = n + ⌈log₂(2 + 1/(2ε))⌉ delivers n accurate bits with probability "
                "≥ 1 − ε; alternatively repeat the whole procedure and take a majority "
                "vote. QPE is the engine inside Shor's algorithm, quantum chemistry "
                "energy estimation, and amplitude estimation."
            ),
        ),
    ],
)
