"""Assemble Claude prompts from session state + optional Qiskit context."""

from __future__ import annotations
from core.models import Evaluation, Question, QuizConfig
from qiskit_contexts import QiskitContext

# Subjects/types that need extra guidance to avoid nonsensical combos.
# "circuit design" on purely mathematical subjects produces ill-formed questions;
# "proof sketch"/"mathematical derivation" on Qiskit/QASM topics risks ignoring context.
_SUBJECT_TYPE_SUPPLEMENT: dict[tuple[str, str], str] = {
    ("Quantum Error Correction", "circuit design"):
        "Design a specific stabilizer or logical gate circuit — "
        "give qubit count, gates used, and the error syndrome it detects.",
    ("Quantum Algorithms", "circuit design"):
        "Design a circuit for a named algorithm (e.g. QPE, amplitude amplification) "
        "referencing explicit gate layers and ancilla usage.",
    ("Linear Algebra", "circuit design"):
        "Re-interpret 'circuit design' as: construct a unitary matrix or sequence of "
        "gate operations that implements a given linear map — show the matrix.",
    ("Linear Algebra", "proof sketch"):
        "Sketch a proof of a theorem (e.g. spectral theorem, SVD existence, rank-nullity). "
        "Show key steps without full formalism.",
    ("Quantum Foundations", "circuit design"):
        "Illustrate the concept with a concrete 1–3 qubit circuit (e.g. Hardy paradox, "
        "CHSH test, or delayed-choice experiment).",
    ("Mathematics", "circuit design"):
        "Treat 'circuit design' as: construct a mathematical procedure (matrix product, "
        "Gram-Schmidt, etc.) step by step — concrete numbers preferred.",
}

# Type-wide guidance applied regardless of subject.
_TYPE_SUPPLEMENT: dict[str, str] = {
    "teach-back":
        "Phrase the question as a Feynman-style teaching task: instruct the student to "
        "EXPLAIN the topic to a bright undergraduate who has never seen quantum "
        "computing (e.g. \"Explain to a bright undergraduate who has never seen "
        "quantum computing why/how ...\"). The prompt should demand plain language, "
        "a well-chosen analogy, and coverage of the core idea — not a formal "
        "derivation. If a Qiskit context is provided, treat it as inspiration only; "
        "the explanation itself must stand alone without code.",
}

# Per-type grading rubrics injected into the evaluation prompt.
_TYPE_GRADING_RUBRIC: dict[str, str] = {
    "teach-back": (
        "This is a Feynman-style teach-back: the student explained the topic to an "
        "imagined bright newcomer. Grade against this rubric:\n"
        "  • Factual accuracy — the explanation must introduce NO errors or "
        "misleading claims, even in simplification.\n"
        "  • Completeness — the core idea of the topic is fully conveyed, not just "
        "a fragment of it.\n"
        "  • Analogy quality — analogies are apt and minimally leaky; penalise "
        "analogies that would leave the newcomer with a wrong mental model, and "
        "credit the student for flagging where an analogy breaks down.\n"
        "  • Appropriate level — no unexplained jargon; every technical term a "
        "newcomer could not know must be introduced in plain language.\n"
        "The \"model_answer\" field must itself be a model EXPLANATION aimed at "
        "the same bright newcomer — not a formal textbook treatment."
    ),
}

# Subject-wide guidance applied regardless of question type.
_SUBJECT_SUPPLEMENT: dict[str, str] = {
    "Qiskit Certification (C1000-179)":
        "Write an IBM certification exam-style question calibrated to ASSOCIATE level "
        "(recall and apply, not derive). Present a short Qiskit v2.x code snippet and "
        "ask what it does, what it outputs, or which single line completes or fixes "
        "it — offer four labelled options (A–D) with plausible distractors wherever "
        "the question type permits. Test precise current-API knowledge: SamplerV2/"
        "EstimatorV2 PUB shapes and result access (data.<creg>.get_counts(), data.evs), "
        "generate_preset_pass_manager and ISA circuits, job/Session/Batch execution "
        "modes, choosing the correct visualization function, OpenQASM 2/3 syntax, "
        "little-endian bit ordering, and quantum_info operators. Never use retired "
        "APIs (execute(), qiskit.pulse, BackendV1, V1 primitives).",
}


def build_generation_prompt(
    subject: str,
    topic: str,
    difficulty: str,
    question_type: str,
    previous_texts: list[str],
    context: QiskitContext,
) -> str:
    recent_block = (
        "\n".join(f"  - {t}" for t in previous_texts)
        if previous_texts
        else "  (none yet)"
    )

    context_block = _format_context(context)
    supplements = [
        s for s in (
            _SUBJECT_SUPPLEMENT.get(subject, ""),
            _TYPE_SUPPLEMENT.get(question_type, ""),
            _SUBJECT_TYPE_SUPPLEMENT.get((subject, question_type), ""),
        ) if s
    ]
    supplement_block = "".join(f"\n  • {s}" for s in supplements)

    return f"""You are an expert quantum computing educator creating exam-quality questions.

Generate a single {difficulty}-level {question_type} question on this topic:

  Subject : {subject}
  Topic   : {topic}
{context_block}
Requirements:
  • The question must be ORIGINAL — do not lift it verbatim from any textbook.
  • Difficulty {difficulty}: {'recall a definition or state a fact' if difficulty == 'beginner'
      else 'apply a concept to a specific scenario' if difficulty == 'intermediate'
      else 'derive, analyse, or compare at depth' if difficulty == 'advanced'
      else 'synthesise across topics or construct a proof'}
  • Question type "{question_type}": design the question accordingly.{supplement_block}
  • If a Qiskit context was provided above, ground the question in that specific
    circuit / Hamiltonian / state — reference gate names, qubit indices, or Pauli
    terms explicitly so the student must engage with the artefact.
  • Do NOT include the answer or any hints inside the question text.
  • Use Unicode math symbols freely (⟨, ⟩, ⊗, †, ψ, λ, π, etc.)

Do NOT repeat any of these recently asked questions:
{recent_block}

Respond with ONLY valid JSON matching this schema exactly:
{{
  "question": "<full question text>",
  "hints": ["<hint 1>", "<hint 2>", "<hint 3>"]
}}"""


def build_evaluation_prompt(question: Question, user_answer: str) -> str:
    rubric = _TYPE_GRADING_RUBRIC.get(question.question_type, "")
    rubric_block = f"\nGrading rubric:\n{rubric}\n" if rubric else ""
    return f"""You are an expert quantum computing educator grading a student's answer.

Subject  : {question.subject}
Topic    : {question.topic}
Difficulty: {question.difficulty}
Type     : {question.question_type}

Question:
{question.text}

Student's answer:
{user_answer}
{rubric_block}
Evaluate thoroughly. Respond with ONLY valid JSON matching this schema exactly:
{{
  "score": <integer 0–10>,
  "verdict": "<Correct | Partially correct | Incorrect>",
  "feedback": "<2–4 sentences of specific, constructive feedback that references the student's own words>",
  "model_answer": "<a complete, rigorous model answer a professor would give>",
  "key_points_missed": ["<point>", ...],
  "follow_up": "<one harder follow-up question to push understanding further>"
}}"""


def build_viva_probe_prompt(
    question: Question,
    user_answer: str,
    evaluation: Evaluation,
) -> str:
    """Prompt for ONE viva-style follow-up probe derived from the user's answer.

    Returns the same JSON contract as question generation ({"question", "hints"})
    so the response can be parsed by parse_question_response unchanged.
    """
    missed_block = (
        "\n".join(f"  - {p}" for p in evaluation.key_points_missed)
        if evaluation.key_points_missed
        else "  (none noted)"
    )
    return f"""You are an expert quantum computing examiner conducting a viva (oral exam).
The student has just answered a question and you will now probe their understanding
with exactly ONE follow-up question.

Original question ({question.subject} — {question.topic}, {question.difficulty}, {question.question_type}):
{question.text}

Student's answer (graded {evaluation.score}/10 — {evaluation.verdict}):
{user_answer}

Examiner's feedback on that answer:
{evaluation.feedback}

Key points the student missed:
{missed_block}

Requirements:
  • Ask exactly ONE probing question derived from the student's ACTUAL answer —
    target its weakest point, or probe one level deeper into something the student
    asserted but did not justify.
  • The follow-up must be SELF-CONTAINED: restate whatever minimal context from the
    original exchange is needed, because it will be graded on its own without the
    original question or answer attached.
  • Do NOT simply repeat the original question or ask for a generic summary.
  • Keep it at or slightly above {question.difficulty} difficulty.
  • Do NOT include the answer or any hints inside the question text.
  • Use Unicode math symbols freely (⟨, ⟩, ⊗, †, ψ, λ, π, etc.)

Respond with ONLY valid JSON matching this schema exactly:
{{
  "question": "<full follow-up question text>",
  "hints": ["<hint 1>", "<hint 2>", "<hint 3>"]
}}"""


# ── Internal helpers ──────────────────────────────────────────────────────────

def _format_context(ctx: QiskitContext) -> str:
    if not ctx.has_content():
        return ""
    parts = ["\nQiskit context (use this artefact in your question):\n"]
    if ctx.prose_description:
        parts.append(f"  Description : {ctx.prose_description}")
    if ctx.qasm_snippet:
        parts.append(f"\n  Circuit (QASM):\n```\n{ctx.qasm_snippet}\n```")
    if ctx.hamiltonian_str:
        parts.append(f"\n  Hamiltonian (Pauli decomposition):\n{ctx.hamiltonian_str}")
    if ctx.statevector_table:
        parts.append(f"\n  Quantum state (amplitudes):\n{ctx.statevector_table}")
    parts.append("")
    return "\n".join(parts)
