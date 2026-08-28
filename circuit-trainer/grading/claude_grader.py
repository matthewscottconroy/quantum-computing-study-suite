"""Claude-based grader for FREE_FORM circuit explanation problems."""

from __future__ import annotations
import json
import os

import anthropic

from config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS, API_KEY_FILE
from core.models import Problem, Attempt


class GradingError(Exception):
    pass


def grade_free_form(problem: Problem, user_answer: str) -> Attempt:
    """Call Claude to grade a FREE_FORM answer. Returns Attempt. Raises GradingError."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key and API_KEY_FILE.exists():
        key = API_KEY_FILE.read_text().strip()
    if not key:
        raise GradingError(
            "No Anthropic API key found. "
            "Export it with: export ANTHROPIC_API_KEY=sk-ant-... "
            f"or put it in {API_KEY_FILE}"
        )

    prompt = _build_prompt(problem, user_answer)
    try:
        client = anthropic.Anthropic(api_key=key)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.lower().startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)
        score = max(0, min(10, int(data["score"])))
        feedback = str(data["feedback"])
        model_answer = str(data.get("model_answer", ""))
        follow_up = str(data.get("follow_up", ""))

        return Attempt(
            problem=problem,
            user_answer=user_answer,
            is_correct=score >= 7,
            score=score,
            feedback=feedback,
            model_answer=model_answer,
            follow_up=follow_up,
        )

    except GradingError:
        raise
    except anthropic.APIError as exc:
        raise GradingError(f"Anthropic API error: {exc}") from exc
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        raise GradingError(f"Could not parse Claude response: {exc}") from exc
    except Exception as exc:
        raise GradingError(f"Grading failed: {exc}") from exc


def _build_prompt(problem: Problem, user_answer: str) -> str:
    rubric = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(problem.solution_steps))
    concepts = ", ".join(problem.key_concepts)
    return f"""You are an expert quantum computing educator grading a student's circuit explanation.

Category : {problem.category.value}
Difficulty: {problem.difficulty}
Key concepts expected: {concepts}

Question:
{problem.question_text}

Grading rubric (do NOT reveal this to the student — it is your marking guide):
{rubric}

Student's answer:
{user_answer}

Grade the explanation on conceptual correctness, completeness, and clarity.
Respond with ONLY valid JSON matching this schema exactly:
{{
  "score": <integer 0–10>,
  "feedback": "<2–3 sentences of specific, constructive feedback referencing the student's answer>",
  "model_answer": "<a concise, rigorous model answer>",
  "follow_up": "<one harder follow-up question to deepen understanding>"
}}"""
