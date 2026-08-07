"""Assemble Claude prompts from session state + optional Qiskit context."""

from __future__ import annotations
from core.models import Question, QuizConfig
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
    supplement = _SUBJECT_TYPE_SUPPLEMENT.get((subject, question_type), "")
    supplement_block = f"\n  • {supplement}" if supplement else ""

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
    return f"""You are an expert quantum computing educator grading a student's answer.

Subject  : {question.subject}
Topic    : {question.topic}
Difficulty: {question.difficulty}
Type     : {question.question_type}

Question:
{question.text}

Student's answer:
{user_answer}

Evaluate thoroughly. Respond with ONLY valid JSON matching this schema exactly:
{{
  "score": <integer 0–10>,
  "verdict": "<Correct | Partially correct | Incorrect>",
  "feedback": "<2–4 sentences of specific, constructive feedback that references the student's own words>",
  "model_answer": "<a complete, rigorous model answer a professor would give>",
  "key_points_missed": ["<point>", ...],
  "follow_up": "<one harder follow-up question to push understanding further>"
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
