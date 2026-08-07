"""Claude-graded free-form VQA problems."""
from __future__ import annotations
import json
import os
from config import API_KEY_FILE, MODEL
from core.models import Problem, Attempt, Verdict


def _get_client():
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY") or (
        API_KEY_FILE.read_text().strip() if API_KEY_FILE.exists() else None
    )
    if not key:
        raise RuntimeError("No Anthropic API key found.")
    return anthropic.Anthropic(api_key=key), MODEL


_SYSTEM = (
    "You are an expert in variational quantum algorithms (VQE, QAOA, parameter shift, barren plateaus, "
    "error mitigation). Grade student answers strictly and fairly."
)

_TMPL = """\
Question: {question}

Reference answer: {model_answer}

Student answer: {student_answer}

Return JSON only:
  "score": 0-10
  "feedback": 2-4 sentences of specific feedback
  "model_answer": concise ideal answer
"""


def grade_open(problem: Problem, student_answer: str) -> Attempt:
    client, model = _get_client()
    prompt = _TMPL.format(
        question=problem.question,
        model_answer=problem.explanation,
        student_answer=student_answer,
    )

    def _parse(raw: str) -> dict:
        if "```" in raw:
            parts = raw.split("```")
            for part in parts[1::2]:
                part = part.strip()
                if part.lower().startswith("json"):
                    part = part[4:].strip()
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    pass
        return json.loads(raw)

    data = None
    for attempt_num in range(2):
        msg = client.messages.create(
            model=model,
            max_tokens=512,
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        try:
            data = _parse(raw)
            break
        except (json.JSONDecodeError, IndexError, KeyError):
            if attempt_num == 1:
                raise

    score = max(0, min(10, int(data["score"])))
    verdict = (
        Verdict.CORRECT if score >= 7 else
        Verdict.PARTIAL if score >= 4 else
        Verdict.INCORRECT
    )
    return Attempt(
        problem=problem,
        answer=student_answer,
        score=score,
        verdict=verdict,
        feedback=data.get("feedback", ""),
        model_answer=data.get("model_answer", problem.explanation),
    )
