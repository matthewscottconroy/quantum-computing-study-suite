"""Prompt builders for part grading and derivation step checking.

Each builder returns (system, user) strings. Answers are free-form plain text
with unicode / backtick math, so graders are told to be notation-tolerant.
"""
from __future__ import annotations
from core.models import Part, Problem, Derivation, Step

GRADING_SYSTEM = (
    "You are a rigorous but fair quantum-computing instructor grading long-form, "
    "textbook-style problem solutions (Nielsen & Chuang level). Students write "
    "plain text with unicode or backtick math; accept any unambiguous notation "
    "(e.g. |psi>, ⟨ψ|, dagger as † or ^† or *). Grade strictly against the rubric: "
    "award credit only for points the student actually demonstrates. Partial "
    "credit is fine. Never reveal rubric text verbatim; paraphrase missed points "
    "as actionable guidance. Respond with JSON only — no markdown fences, no prose."
)

_GRADING_TMPL = """\
PROBLEM: {title} [topic: {topic}]

Statement:
{statement}

Part ({part_id}) — worth {points} points:
{prompt}

Grading rubric (each bullet is a creditable element; the part score 0-10 should \
reflect what fraction of these, weighted by importance, the answer earns):
{rubric}

Reference model solution (for your eyes only — do not require identical wording \
or an identical method; any mathematically valid route earns full credit):
{model_solution}

Student answer (attempt #{tries}):
\"\"\"
{answer}
\"\"\"

Return a single JSON object with exactly these keys:
  "score": integer 0-10 (10 = complete and correct for this part)
  "feedback": 2-5 sentences: what was right, what was wrong or unjustified
  "missed_points": array of short strings, one per rubric element the answer \
missed or botched (empty array if none)
"""

STEP_SYSTEM = (
    "You are a Socratic tutor guiding a quantum-computing derivation one step at "
    "a time. Students write plain text with unicode / backtick math; accept any "
    "unambiguous notation. Judge ONLY whether the student's response achieves the "
    "current step described in EXPECTED — not style, not later steps. Be "
    "encouraging but do not accept wrong or empty reasoning. If the response is "
    "close but incomplete, verdict is needs_work with a nudge that points at the "
    "gap WITHOUT giving the step away. Respond with JSON only — no markdown "
    "fences, no prose."
)

_STEP_TMPL = """\
DERIVATION: {title}
Overall goal: {goal}

Progress so far (accepted steps, in order):
{context}

Current step ({step_id}) — the question posed to the student:
{prompt}

EXPECTED (grader-facing description of what a correct step must contain):
{expected}

Student response (attempt #{tries}):
\"\"\"
{answer}
\"\"\"

Return a single JSON object with exactly these keys:
  "verdict": "accept" if the response contains the essential content of EXPECTED \
(minor notation slips are fine), otherwise "needs_work"
  "nudge": one sentence. If accept: brief confirmation of what was right. If \
needs_work: a single Socratic hint at what is missing, without revealing the answer.
"""


def build_part_grading_prompt(problem: Problem, part: Part, answer: str,
                              tries: int = 1) -> tuple[str, str]:
    rubric = "\n".join(f"- {r}" for r in part.rubric)
    user = _GRADING_TMPL.format(
        title=problem.title,
        topic=problem.topic,
        statement=problem.statement,
        part_id=part.part_id,
        points=part.points,
        prompt=part.prompt,
        rubric=rubric,
        model_solution=part.model_solution,
        tries=max(1, tries),
        answer=answer.strip() or "(empty)",
    )
    return GRADING_SYSTEM, user


def build_step_check_prompt(derivation: Derivation, step: Step, answer: str,
                            accepted_steps: list[Step] | None = None,
                            tries: int = 1) -> tuple[str, str]:
    if accepted_steps:
        context = "\n".join(
            f"{i}. {s.model_step}" for i, s in enumerate(accepted_steps, start=1)
        )
    else:
        context = "(this is the first step)"
    user = _STEP_TMPL.format(
        title=derivation.title,
        goal=derivation.goal,
        context=context,
        step_id=step.step_id,
        prompt=step.prompt,
        expected=step.expected,
        tries=max(1, tries),
        answer=answer.strip() or "(empty)",
    )
    return STEP_SYSTEM, user
