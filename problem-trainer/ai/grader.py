"""Claude-backed grading of problem parts and checking of derivation steps."""
from __future__ import annotations
from core.models import Problem, Part, Derivation, Step, GradeResult, StepCheck
from ai.client import make_client
from ai.prompts import build_part_grading_prompt, build_step_check_prompt
from ai.response_parser import parse_grade_response, parse_step_check_response, ParseError

_MAX_TOKENS = 700


def _call(system: str, user: str, parse):
    """One API call with a single retry on unparseable output."""
    client, model = make_client()
    last_exc: Exception | None = None
    for _ in range(2):
        msg = client.messages.create(
            model=model,
            max_tokens=_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        raw = "".join(
            block.text for block in msg.content if getattr(block, "type", "") == "text"
        ).strip()
        try:
            return parse(raw)
        except ParseError as exc:
            last_exc = exc
    raise last_exc  # type: ignore[misc]


def grade_part(problem: Problem, part: Part, answer: str, tries: int = 1) -> GradeResult:
    system, user = build_part_grading_prompt(problem, part, answer, tries)
    return _call(system, user, parse_grade_response)


def check_step(derivation: Derivation, step: Step, answer: str,
               accepted_steps: list[Step] | None = None, tries: int = 1) -> StepCheck:
    system, user = build_step_check_prompt(derivation, step, answer, accepted_steps, tries)
    return _call(system, user, parse_step_check_response)
