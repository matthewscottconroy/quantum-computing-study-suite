"""Assemble Claude prompts for math question generation and evaluation."""

from __future__ import annotations
from core.models import Question


# Map subject → one-sentence note on quantum computing relevance
_QC_RELEVANCE: dict[str, str] = {
    "Linear Algebra": (
        "Linear algebra is the primary language of quantum computing: quantum states are "
        "vectors in Hilbert space, gates are unitary operators, and measurements are "
        "projectors."
    ),
    "Abstract Algebra": (
        "Abstract algebra underpins error-correcting codes, the stabilizer formalism, "
        "the Clifford group, and the structure of quantum gates."
    ),
    "Representation Theory": (
        "Representation theory explains why the quantum Fourier transform works, provides "
        "the hidden subgroup framework for Shor's algorithm, and governs spin-j states."
    ),
    "Complex Analysis": (
        "Complex analysis provides tools for quantum amplitudes, contour integral techniques "
        "used in quantum algorithms, and the geometry of the complex plane underlying phases."
    ),
    "Calculus & Real Analysis": (
        "Real analysis supplies the rigorous foundations for limits and continuity used in "
        "quantum mechanics, convergence of perturbation series, and optimisation in VQE."
    ),
    "Ordinary Differential Equations": (
        "ODEs describe time evolution in quantum mechanics; the Schrödinger equation is a "
        "first-order linear ODE in time, and Hamiltonian simulation reduces to matrix ODEs."
    ),
    "Partial Differential Equations": (
        "PDEs appear in the time-dependent Schrödinger equation, continuous-variable QC, "
        "and quantum field theory foundations relevant to error models."
    ),
    "Functional Analysis": (
        "Functional analysis is the rigorous setting for infinite-dimensional Hilbert spaces, "
        "unbounded Hamiltonians, the spectral theorem for observables, and quantum channels."
    ),
    "Probability Theory": (
        "Probability theory formalises measurement outcomes, quantum entropy, entanglement "
        "measures, randomised algorithms in QC, and information-theoretic bounds."
    ),
    "Fourier Analysis": (
        "Fourier analysis is central to the quantum Fourier transform, phase estimation, "
        "signal processing in quantum control, and the hidden subgroup problem."
    ),
    "Number Theory": (
        "Number theory is the direct target of Shor's algorithm: period-finding, "
        "modular arithmetic, discrete logarithms, and factoring all live here."
    ),
    "Topology & Geometry": (
        "Topology and geometry underlie the Berry phase, topological quantum computation, "
        "the toric code, anyonic statistics, and Chern number topological invariants."
    ),
    "Quantum Connections": (
        "These topics explicitly bridge two or more mathematical disciplines as they appear "
        "together in quantum computing research — the cross-domain connections most critical "
        "for research-level work."
    ),
}

_DIFFICULTY_GUIDE: dict[str, str] = {
    "beginner":     "recall or state a definition, property, or basic fact",
    "intermediate": "apply a concept to a specific problem or scenario",
    "advanced":     "derive a result, analyse structure, or compare two concepts in depth",
    "expert":       "synthesise across topics, construct a non-trivial proof, or resolve a subtlety",
}

# Extra guidance injected when subject+type would otherwise produce weak questions
_SUBJECT_TYPE_SUPPLEMENT: dict[tuple[str, str], str] = {
    ("Topology & Geometry", "calculation"): (
        "For topology, a 'calculation' must be a specific algebraic-topology computation: "
        "e.g. compute π₁(T²) or π₁(S¹∨S¹), compute H₁ of a given space, compute a "
        "winding number, or evaluate a Chern number for a Hamiltonian with given parameters."
    ),
    ("Representation Theory", "calculation"): (
        "For representation theory, a 'calculation' must be concrete: compute a specific "
        "character value χ(g) for a given group element and representation, find a "
        "Clebsch-Gordan coefficient ⟨j₁m₁;j₂m₂|JM⟩ for explicit values, or decompose "
        "a given small representation into irreducibles."
    ),
    ("Functional Analysis", "calculation"): (
        "For functional analysis, a 'calculation' must involve a specific operator: compute "
        "the operator norm ‖T‖ of a given matrix or integral kernel, find all eigenvalues "
        "of a specific compact self-adjoint operator, or compute a Hilbert-Schmidt norm."
    ),
    ("Abstract Algebra", "calculation"): (
        "For abstract algebra, a 'calculation' must be a concrete algebraic computation: "
        "find the order of a specific element in a given group, compute a quotient group "
        "G/N for explicit G and N, determine if two explicitly given groups are isomorphic, "
        "or find the center Z(G) of a small concrete group."
    ),
    ("Quantum Connections", "calculation"): (
        "For a synthesis topic, a 'calculation' should demonstrate the cross-disciplinary "
        "connection numerically: e.g. compute the QFT on a specific 3-element group, "
        "evaluate a Trotter step error for a simple 2-term Hamiltonian, or compute a "
        "Berry phase for an explicit path on the Bloch sphere."
    ),
}

_TYPE_GUIDE: dict[str, str] = {
    "conceptual explanation": (
        "Ask the student to explain what a concept means, why it matters, or "
        "how it connects to quantum computing."
    ),
    "proof sketch": (
        "Ask for a proof or a proof outline. The student should state key steps "
        "and the main idea, not necessarily full ε-δ rigor."
    ),
    "calculation": (
        "Give a specific numerical or symbolic computation to carry out: compute "
        "an eigenvalue, evaluate an integral, find a determinant, etc."
    ),
    "example construction": (
        "Ask the student to construct a concrete example satisfying given "
        "conditions, or give an example illustrating a theorem or definition."
    ),
    "compare and contrast": (
        "Ask the student to compare two related objects, theorems, or definitions, "
        "highlighting similarities and key differences."
    ),
    "counterexample": (
        "Ask the student to provide or explain a counterexample to a plausible "
        "but false statement, or to show why a hypothesis cannot be dropped."
    ),
}


def build_generation_prompt(
    subject: str,
    topic: str,
    difficulty: str,
    question_type: str,
    previous_texts: list[str],
) -> str:
    recent_block = (
        "\n".join(f"  - {t}" for t in previous_texts)
        if previous_texts
        else "  (none yet)"
    )

    qc_note = _QC_RELEVANCE.get(subject, "")
    diff_guide = _DIFFICULTY_GUIDE.get(difficulty, "apply a concept")
    type_guide = _TYPE_GUIDE.get(question_type, "")
    supplement = _SUBJECT_TYPE_SUPPLEMENT.get((subject, question_type), "")
    type_block = type_guide + (f"\n  {supplement}" if supplement else "")

    return f"""You are an expert mathematics educator creating exam-quality questions for \
a student preparing for research in quantum computing.

Generate a single {difficulty}-level "{question_type}" question on this topic:

  Subject : {subject}
  Topic   : {topic}

Quantum computing relevance:
  {qc_note}

Difficulty "{difficulty}": {diff_guide}.
Question type "{question_type}": {type_block}

Requirements:
  • The question must be ORIGINAL — do not copy it from any textbook.
  • Use precise mathematical language appropriate to the difficulty level.
  • Use Unicode math symbols freely (ℝ, ℂ, ⊗, ⊕, ∈, ∀, ∃, ‖·‖, ⟨·,·⟩, etc.)
  • For a "calculation" type, include concrete numerical values so the student can \
compute a specific answer.
  • Do NOT include the answer or any hints inside the question text.
  • When relevant, note the quantum computing connection in the question itself to \
motivate the problem.

Do NOT repeat any of these recently asked questions:
{recent_block}

Respond with ONLY valid JSON matching this schema exactly:
{{
  "question": "<full question text>",
  "hints": ["<hint 1>", "<hint 2>", "<hint 3>"]
}}"""


def build_evaluation_prompt(question: Question, user_answer: str) -> str:
    qc_note = _QC_RELEVANCE.get(question.subject, "")

    return f"""You are an expert mathematics educator grading a student's answer. \
The student is preparing for research in quantum computing.

Subject   : {question.subject}
Topic     : {question.topic}
Difficulty: {question.difficulty}
Type      : {question.question_type}

Quantum computing context:
  {qc_note}

Question:
{question.text}

Student's answer:
{user_answer}

Evaluate thoroughly. Award partial credit where deserved. \
For "proof sketch" questions, assess whether the student identified the key ideas \
even if details are missing. For "calculation" questions, check both method and \
numerical result.

Respond with ONLY valid JSON matching this schema exactly:
{{
  "score": <integer 0–10>,
  "verdict": "<Correct | Partially correct | Incorrect>",
  "feedback": "<2–4 sentences of specific, constructive feedback referencing \
the student's own words>",
  "model_answer": "<a complete, rigorous model answer a professor would give, \
including the quantum computing connection where relevant>",
  "key_points_missed": ["<point>", ...],
  "follow_up": "<one harder follow-up question to push understanding further>"
}}"""
