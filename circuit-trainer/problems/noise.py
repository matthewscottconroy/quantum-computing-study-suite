"""
Noise channel problems — bit-flip, phase-flip, depolarizing, amplitude damping,
T1/T2 decay, two-qubit noise. All answers are analytically derived exact values.
"""

from __future__ import annotations
import random
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import make_prob_distractors


def _distinct_distractors(correct: float, candidates: list[float], n: int = 3) -> list[float]:
    """First ``n`` candidates (in order) that differ from ``correct`` and from
    each other.  Used where the natural distractors (p, 1-p, ...) can collide
    with the answer -- e.g. p = 0.5 -- so every choice list has ``n`` distinct
    wrong values and the correct value appears exactly once."""
    out: list[float] = []
    for v in candidates:
        if abs(v - correct) > 1e-4 and all(abs(v - d) > 1e-4 for d in out):
            out.append(v)
        if len(out) == n:
            break
    return out


def generate(difficulty: str) -> Problem:
    if difficulty == "beginner":
        return random.choice([
            _bit_flip_prob,
            _phase_flip_z_basis,
            _bit_flip_on_plus,
            _phase_flip_x_basis,
        ])()
    elif difficulty == "intermediate":
        return random.choice([
            _depolarizing_density_00,
            _depolarizing_on_bell,
            _two_qubit_depolarizing,
            _repeated_bit_flip,
        ])()
    else:
        return random.choice([
            _amplitude_damping_00,
            _identify_kraus,
            _t1_excited_state,
            _amplitude_damping_superposition,
        ])()


# ── Beginner ──────────────────────────────────────────────────────────────────

def _bit_flip_prob() -> Problem:
    p = random.choice([0.1, 0.15, 0.2, 0.3])
    correct = p

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"The bit-flip channel applies X with probability p and leaves ρ unchanged with probability (1-p).",
        "Starting from |0⟩⟨0|: ρ_out = (1-p)|0⟩⟨0| + p·X|0⟩⟨0|X† = (1-p)|0⟩⟨0| + p|1⟩⟨1|.",
        f"P(|1⟩) = Tr(|1⟩⟨1| ρ_out) = p = {p}.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="beginner",
        question_text=(
            f"A bit-flip (X) error channel acts on a qubit in |0⟩ with flip probability p = {p}.\n\n"
            f"What is the probability of measuring |1⟩?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |0⟩,  bit-flip rate p = {p}",
        solution_steps=steps,
        key_concepts=["bit-flip channel", "Pauli X error", "density matrix"],
        hints=[
            f"The output state is a mixture: (1-p)|0⟩⟨0| + p|1⟩⟨1|.",
            "P(|1⟩) is just the coefficient on |1⟩⟨1| in the output mixture.",
        ],
    )


def _phase_flip_z_basis() -> Problem:
    p = random.choice([0.25, 0.5, 0.75])
    correct = 0.5

    # At p = 0.5 both 1-p and p equal the answer, so draw from an ordered,
    # deduplicated pool (always yields 3 distinct wrong values).
    choices_f = [correct] + _distinct_distractors(
        correct,
        [round(1.0 - p, 4), round(p, 4), round((1 - p) / 2, 4), 0.25, 0.75, 1.0, 0.0],
    )
    random.shuffle(choices_f)
    choices = [str(round(v, 4)) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Phase-flip (Z error) channel on |+⟩ = (|0⟩+|1⟩)/√2 with rate p = {p}.",
        "Z|+⟩ = |−⟩.  ρ_out = (1-p)|+⟩⟨+| + p|−⟩⟨−|.",
        "Both |+⟩ and |−⟩ give P(|0⟩) = 1/2 in the Z basis.",
        "P(|0⟩) = 0.5 regardless of p — phase errors are invisible in the Z basis.",
        "Key insight: to detect phase errors, measure in the X basis instead.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="beginner",
        question_text=(
            f"A phase-flip (Z) error channel with rate p = {p} acts on |+⟩.\n\n"
            f"What is P(measuring |0⟩) in the Z basis?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |+⟩,  phase-flip rate p = {p}",
        solution_steps=steps,
        key_concepts=["phase-flip channel", "Pauli Z error", "basis sensitivity", "noise detection"],
        hints=[
            "|+⟩ and Z|+⟩ = |−⟩ both have equal |0⟩ and |1⟩ amplitudes in the Z basis.",
            "Z errors only change the relative phase; they cannot be detected in the Z eigenbasis.",
        ],
    )


def _bit_flip_on_plus() -> Problem:
    """Bit-flip on |+⟩ — the resulting mixture is still 50/50 in Z basis."""
    p = random.choice([0.1, 0.25, 0.4, 0.5])
    # ρ_out = (1-p)|+⟩⟨+| + p·X|+⟩⟨+|X† = (1-p)|+⟩⟨+| + p|+⟩⟨+| = |+⟩⟨+|
    # X|+⟩ = |+⟩, so the channel has no effect on |+⟩.
    correct = 0.5

    # At p = 0.5 the natural distractors collide with the answer; the fixed
    # tail of the pool guarantees 3 distinct wrong values, never a second 0.5.
    choices_f = [correct] + _distinct_distractors(
        correct,
        [round(1.0 - p, 4), round(p, 4), round(0.5 + p / 2, 4),
         0.25, 0.75, 0.0, 1.0, 0.125, 0.875],
    )
    random.shuffle(choices_f)
    choices = [str(round(v, 4)) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Bit-flip channel with p = {p} applied to |+⟩.",
        "Key observation: X|+⟩ = |+⟩ because |+⟩ is an eigenstate of X with eigenvalue +1.",
        "ρ_out = (1-p)|+⟩⟨+| + p·X|+⟩⟨+|X = |+⟩⟨+|  (channel has no effect!).",
        "P(|0⟩) in Z basis = |⟨0|+⟩|² = 1/2.",
        "Insight: bit-flip noise is invisible when the qubit is already in a Pauli X eigenstate.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="beginner",
        question_text=(
            f"A bit-flip (X) error channel with flip probability p = {p} acts on |+⟩.\n\n"
            f"What is P(measuring |0⟩) in the Z basis after the channel?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |+⟩,  bit-flip rate p = {p}",
        solution_steps=steps,
        key_concepts=["bit-flip channel", "X eigenstate", "noise resilience"],
        hints=[
            "|+⟩ is an eigenstate of the Pauli X gate — think about what X|+⟩ equals.",
            "If X|ψ⟩ = |ψ⟩, then applying the bit-flip channel does not change ρ.",
        ],
    )


def _phase_flip_x_basis() -> Problem:
    """Phase flip on |+⟩ measured in X basis."""
    p = random.choice([0.1, 0.2, 0.4])
    # Z|+⟩ = |−⟩.  ρ_out = (1-p)|+⟩⟨+| + p|−⟩⟨−|
    # In X basis: P(|+⟩) = (1-p)·1 + p·0 = 1-p
    correct = round(1.0 - p, 4)

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Phase-flip channel: ρ_out = (1-p)|+⟩⟨+| + p|−⟩⟨−|, p = {p}.",
        "In the X basis, |+⟩ and |−⟩ are orthogonal eigenstates.",
        f"P(measuring |+⟩) = (1-p)·⟨+|+⟩⟨+|+⟩ + p·⟨+|−⟩⟨−|+⟩ = (1-p)·1 + p·0 = {correct}.",
        "Conclusion: phase errors ARE visible in the X basis — unlike in the Z basis.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="beginner",
        question_text=(
            f"A phase-flip (Z) error channel with rate p = {p} acts on |+⟩.\n\n"
            f"What is P(measuring |+⟩) in the X basis after the channel?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |+⟩,  phase-flip rate p = {p}",
        solution_steps=steps,
        key_concepts=["phase-flip channel", "X basis measurement", "error detection"],
        hints=[
            "After the channel, the state is a mixture of |+⟩ and |−⟩.",
            "|+⟩ and |−⟩ are orthogonal, so the X-basis probabilities are just the mixture weights.",
        ],
    )


# ── Intermediate ──────────────────────────────────────────────────────────────

def _depolarizing_density_00() -> Problem:
    p = random.choice([0.1, 0.2, 0.3])
    # E(ρ) = (1-p)ρ + p·I/2
    # For ρ = |0⟩⟨0|: ρ_out[0,0] = (1-p)·1 + p·0.5 = 1 - p/2
    correct = round(1.0 - p / 2, 4)

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Depolarizing channel: E(ρ) = (1-p)ρ + p·(I/2),  p = {p}.",
        "I/2 is the maximally mixed state [[1/2, 0], [0, 1/2]].",
        f"For ρ = |0⟩⟨0| = [[1,0],[0,0]]:",
        f"  ρ_out[0,0] = (1-{p})·1 + {p}·(1/2) = {1-p} + {p/2} = {correct}.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="intermediate",
        question_text=(
            f"A depolarizing channel E(ρ) = (1-p)ρ + p·I/2 with p = {p} acts on |0⟩⟨0|.\n\n"
            f"What is ρ_out[0,0] (i.e., P(|0⟩)) after the channel?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |0⟩,  depolarizing rate p = {p}",
        solution_steps=steps,
        key_concepts=["depolarizing channel", "density matrix", "maximally mixed state"],
        hints=[
            "Substitute ρ = |0⟩⟨0| = [[1,0],[0,0]] and I/2 = [[0.5,0],[0,0.5]] into E(ρ).",
            f"ρ_out[0,0] = (1-p)·ρ[0,0] + p·(1/2).",
        ],
    )


def _depolarizing_on_bell() -> Problem:
    """P(00) after local depolarizing on qubit 0 of |Φ⁺⟩. Exact: P(00) = 1/2 - p/4."""
    p = random.choice([0.1, 0.2, 0.3])
    correct = round(0.5 - p / 4, 4)

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        "Noiseless Bell state |Φ⁺⟩: P(|00⟩) = P(|11⟩) = 1/2.",
        f"Depolarizing channel (p={p}) on qubit 0 only: E₁⊗I₂.",
        "Decompose via Pauli errors: X flips |Φ⁺⟩→|Ψ⁺⟩, Z→|Φ⁻⟩, Y→|Ψ⁻⟩.",
        "For |Ψ⁺⟩ and |Ψ⁻⟩: P(|00⟩)=0; for |Φ⁻⟩: P(|00⟩)=1/2.",
        f"P(|00⟩) = (1-3p/4)·(1/2) + (p/4)·(0+0+1/2) = 1/2 - p/4 = {correct}.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="intermediate",
        question_text=(
            f"A depolarizing channel with rate p = {p} acts on qubit 0 of the "
            f"Bell state |Φ⁺⟩ = (|00⟩+|11⟩)/√2.\n\n"
            f"What is P(measuring |00⟩) after the channel?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Bell state |Φ⁺⟩,  depolarizing on qubit 0 at rate p = {p}",
        solution_steps=steps,
        key_concepts=["depolarizing channel", "Bell state", "Pauli error decomposition", "fidelity"],
        hints=[
            "The depolarizing channel = (1-3p/4)·I + (p/4)·(X+Y+Z) error mixture.",
            "Track what each Pauli error does to |Φ⁺⟩ and whether the result contributes to P(|00⟩).",
        ],
    )


def _two_qubit_depolarizing() -> Problem:
    """Two independent bit-flip channels, one per qubit of |Φ⁺⟩."""
    p = random.choice([0.1, 0.15, 0.2])
    # P(|00⟩ still perfectly correlated) = (1-p)^2 * 1/2 + p^2 * 1/2
    # Bit flips both qubits → still |11⟩. Flip only one → parity error.
    # P(measuring |00⟩) = [(1-p)²  + p²] / 2
    correct = round(((1 - p) ** 2 + p ** 2) / 2, 4)

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Independent bit-flip channels with rate p = {p} on both qubits of |Φ⁺⟩.",
        "The 4 error scenarios: (no flip, no flip), (X₀, no flip), (no flip, X₁), (X₀, X₁).",
        "Probabilities: (1-p)², p(1-p), (1-p)p, p².",
        "Only (no flip, no flip) keeps |00⟩ component contributing +1/2 to P(|00⟩).",
        "Both-flip (X₀X₁)|Φ⁺⟩ = |Φ⁺⟩ — parity preserved, also contributes +1/2.",
        "Single-flip cases: X₀|Φ⁺⟩ = |Ψ⁺⟩ or X₁|Φ⁺⟩ = |Ψ⁺⟩ — P(|00⟩) = 0.",
        f"P(|00⟩) = [(1-p)² + p²] · (1/2) = {correct}.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="intermediate",
        question_text=(
            f"Independent bit-flip channels with rate p = {p} act simultaneously on both "
            f"qubits of |Φ⁺⟩ = (|00⟩+|11⟩)/√2.\n\n"
            f"What is P(measuring |00⟩)?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Bell state |Φ⁺⟩,  independent bit-flip rate p = {p} on each qubit",
        solution_steps=steps,
        key_concepts=["bit-flip channel", "Bell state", "independent noise", "parity"],
        hints=[
            "List all four combinations of whether each qubit is flipped or not.",
            "X₀X₁|Φ⁺⟩ = |Φ⁺⟩ (flipping both qubits preserves even parity).",
        ],
    )


def _repeated_bit_flip() -> Problem:
    """Applying a bit-flip channel twice."""
    p = random.choice([0.1, 0.2, 0.3])
    # Applying twice: effective flip prob = 2p(1-p) + (1-2p(1-p))·0 ... wait, actually:
    # Two applications: P(flip) = p·(1-p) + (1-p)·p = 2p(1-p). But also flip-flip = no flip.
    # Net: p_eff = 2p(1-p)
    p_eff = round(2 * p * (1 - p), 4)
    correct = p_eff

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Two independent applications of the bit-flip channel with rate p = {p} to |0⟩.",
        "A net flip occurs if exactly one of the two applications flips.",
        "P(exactly one flip) = p·(1-p) + (1-p)·p = 2p(1-p).",
        f"Effective flip rate: p_eff = 2·{p}·{1-p} = {p_eff}.",
        f"P(measuring |1⟩) = {correct}.",
        "Note: for 0 < p < 0.5, p_eff = 2p(1-p) > p — composing the channel with itself "
        "makes a net flip MORE likely (p_eff approaches 1/2, the completely mixed limit, "
        "as more layers are added).",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="intermediate",
        question_text=(
            f"A bit-flip channel with rate p = {p} is applied twice in succession to |0⟩.\n\n"
            f"What is the effective P(measuring |1⟩) after both applications?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |0⟩,  bit-flip channel applied twice, p = {p}",
        solution_steps=steps,
        key_concepts=["bit-flip channel", "channel composition", "effective noise rate"],
        hints=[
            "A net flip happens when exactly one of the two applications flips.",
            "P(exactly one flip) = p(1-p) + (1-p)p.",
        ],
    )


# ── Advanced ──────────────────────────────────────────────────────────────────

def _amplitude_damping_00() -> Problem:
    gamma = random.choice([0.1, 0.2, 0.5])
    # K₀ = [[1,0],[0,√(1-γ)]], K₁ = [[0,√γ],[0,0]]
    # For |+⟩: ρ = [[1/2,1/2],[1/2,1/2]]
    # ρ_out[0,0] = ρ[0,0] + γ·ρ[1,1] = 1/2 + γ/2
    correct = round(0.5 + gamma / 2, 4)

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Amplitude damping Kraus operators: K₀=[[1,0],[0,√(1-γ)]], K₁=[[0,√γ],[0,0]], γ={gamma}.",
        "Models T1 decay: excited state |1⟩ spontaneously decays to |0⟩ with rate γ.",
        "For |+⟩: ρ = [[1/2, 1/2],[1/2, 1/2]].",
        "ρ_out = K₀ρK₀† + K₁ρK₁†.",
        "ρ_out[0,0] = |K₀[0,0]|²·ρ[0,0] + |K₁[0,1]|²·ρ[1,1] = 1·ρ[0,0] + γ·ρ[1,1]  "
        "(K₁[0,0] = 0; the |1⟩→|0⟩ decay enters through K₁[0,1] = √γ)",
        f"= 1/2 + {gamma}·(1/2) = {correct}.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="advanced",
        question_text=(
            f"An amplitude-damping channel with γ = {gamma} acts on |+⟩.\n\n"
            f"What is ρ_out[0,0] = P(|0⟩) after the channel?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |+⟩,  amplitude damping γ = {gamma}",
        solution_steps=steps,
        key_concepts=["amplitude damping", "Kraus operators", "T1 relaxation", "density matrix"],
        hints=[
            "Compute ρ_out = K₀ρK₀† + K₁ρK₁† element by element.",
            "ρ_out[0,0] = ρ[0,0] + γ·ρ[1,1] (the [0,0] entry picks up the |1⟩→|0⟩ decay term).",
        ],
    )


def _identify_kraus() -> Problem:
    channels = [
        {
            "slug": "bitflip",
            "name": "Bit-flip channel (p = 0.3)",
            "kraus": "K₀ = √0.7 · I,   K₁ = √0.3 · X",
            "why": "K₁ ∝ X → applies Pauli X (bit-flip) error.",
        },
        {
            "slug": "phaseflip",
            "name": "Phase-flip channel (p = 0.3)",
            "kraus": "K₀ = √0.7 · I,   K₁ = √0.3 · Z",
            "why": "K₁ ∝ Z → applies Pauli Z (phase-flip) error.",
        },
        {
            "slug": "ampdamp",
            "name": "Amplitude-damping channel (γ = 0.3)",
            "kraus": "K₀ = [[1,0],[0,√0.7]],   K₁ = [[0,√0.3],[0,0]]",
            "why": "K₁ has shape [[0,√γ],[0,0]] — maps |1⟩→|0⟩ (T1 decay).",
        },
        {
            # Same convention as the rest of this module, E(ρ) = (1-p)ρ + p·I/2:
            # Pauli weights 1-3p/4 and p/4 each, so 0.7 / 0.1 ⇔ p = 0.4.
            "slug": "depol",
            "name": "Depolarizing channel (p = 0.4: each Pauli with probability 0.1)",
            "kraus": "K₀=√0.7·I,  K₁=√0.1·X,  K₂=√0.1·Y,  K₃=√0.1·Z",
            "why": ("Four Kraus ops with all three Paulis at equal weight — symmetric "
                    "depolarization. In this module's convention E(ρ) = (1-p)ρ + p·I/2 the "
                    "weights are 1-3p/4 = 0.7 and p/4 = 0.1, i.e. p = 0.4 (the same channel "
                    "is 'p = 0.3' in the (1-p)ρ + (p/3)Σ PρP parameterisation)."),
        },
    ]

    target_idx = random.randint(0, 3)
    target = channels[target_idx]
    choices = [c["name"] for c in channels]

    steps = [
        f"Examine the structure of K₁: {target['kraus'].split('K₁')[1].strip()}",
        f"Identification: {target['why']}",
        "Bit-flip: K₁ ∝ X.   Phase-flip: K₁ ∝ Z.   Amplitude damping: K₁ = [[0,√γ],[0,0]].",
        "Depolarizing: four Kraus ops using all Paulis equally — here weights 0.7 / 0.1, "
        "i.e. p = 0.4 with E(ρ) = (1-p)ρ + p·I/2 (p = 0.3 in the (p/3)Σ PρP convention).",
        f"Answer: {target['name']}.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="advanced",
        question_text=(
            f"A quantum channel has Kraus operators:\n\n"
            f"  {target['kraus']}\n\n"
            f"Which type of noise channel do these operators describe?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(target_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=None,
        solution_steps=steps,
        key_concepts=["Kraus operators", "noise channel identification", "quantum error models"],
        hints=[
            "Focus on K₁: what Pauli or operator is it proportional to?",
            "Amplitude damping K₁ has the distinctive off-diagonal structure [[0,√γ],[0,0]].",
        ],
        problem_id=f"noise:kraus:{target['slug']}",   # deterministic pool -> stable id
    )


def _t1_excited_state() -> Problem:
    """P(|0⟩) after amplitude damping starting from |1⟩."""
    gamma = random.choice([0.1, 0.3, 0.5, 0.8])
    # ρ = |1⟩⟨1| = [[0,0],[0,1]]
    # ρ_out[0,0] = γ·ρ[1,1] = γ
    correct = round(gamma, 4)

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Amplitude damping channel with γ = {gamma}, initial state |1⟩.",
        "ρ = |1⟩⟨1| = [[0,0],[0,1]].",
        "K₀ = [[1,0],[0,√(1-γ)]],  K₁ = [[0,√γ],[0,0]].",
        "K₀|1⟩ = √(1-γ)|1⟩  →  K₀ρK₀† contributes (1-γ)|1⟩⟨1|.",
        "K₁|1⟩ = √γ|0⟩  →  K₁ρK₁† contributes γ|0⟩⟨0|.",
        f"ρ_out = γ|0⟩⟨0| + (1-γ)|1⟩⟨1|.  P(|0⟩) = γ = {correct}.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="advanced",
        question_text=(
            f"An amplitude-damping channel with γ = {gamma} acts on the excited state |1⟩.\n\n"
            f"What is P(measuring |0⟩) after the channel?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |1⟩,  amplitude damping γ = {gamma}",
        solution_steps=steps,
        key_concepts=["amplitude damping", "T1 relaxation", "excited state decay", "Kraus operators"],
        hints=[
            "For |1⟩⟨1|, apply K₁ρK₁† — this is the term that maps |1⟩ to |0⟩.",
            "ρ_out[0,0] = γ (the decay probability).",
        ],
    )


def _amplitude_damping_superposition() -> Problem:
    """Off-diagonal element (coherence) after amplitude damping."""
    gamma = random.choice([0.1, 0.25, 0.5])
    # For arbitrary |ψ⟩ = α|0⟩ + β|1⟩: ρ = [[|α|², α·β*],[α*·β, |β|²]]
    # Use |+⟩: ρ[0,1] = 1/2 before. After: ρ_out[0,1] = √(1-γ)·ρ[0,1]
    import math
    correct = round(math.sqrt(1 - gamma) / 2, 4)

    distractors = [round(d, 4) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [str(v) for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"Amplitude damping (γ = {gamma}) on |+⟩: ρ = [[1/2, 1/2],[1/2, 1/2]].",
        "ρ_out = K₀ρK₀† + K₁ρK₁†.",
        f"ρ_out[0,1] = K₀[0,0]·K₀[1,1]·ρ[0,1] = 1·√(1-γ)·(1/2) = √(1-{gamma})/2.",
        f"= {round(math.sqrt(1-gamma), 4)} / 2 = {correct}.",
        "Interpretation: amplitude damping reduces off-diagonal coherences by √(1-γ), not γ.",
    ]
    return Problem(
        category=ProblemCategory.NOISE_CHANNEL,
        difficulty="advanced",
        question_text=(
            f"An amplitude-damping channel with γ = {gamma} acts on |+⟩.\n\n"
            f"What is |ρ_out[0,1]| (the magnitude of the off-diagonal coherence element)?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Initial state: |+⟩,  amplitude damping γ = {gamma}",
        solution_steps=steps,
        key_concepts=["amplitude damping", "coherence", "decoherence", "density matrix off-diagonal"],
        hints=[
            "The off-diagonal element ρ[0,1] is the coherence between |0⟩ and |1⟩.",
            f"After K₀: ρ_out[0,1] = K₀[0,0]·K₀[1,1]·ρ[0,1] = 1·√(1-γ)·ρ[0,1].",
        ],
    )
