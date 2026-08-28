"""Thin wrapper around the Anthropic SDK. Raises typed exceptions only."""

from __future__ import annotations
import os
import anthropic

from config import CLAUDE_MODEL, GENERATION_MAX_TOKENS, EVALUATION_MAX_TOKENS, API_KEY_FILE
from core.models import Question, Evaluation
from ai.response_parser import parse_question_response, parse_evaluation_response


class GenerationError(Exception):
    pass


class EvaluationError(Exception):
    pass


def _client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key and API_KEY_FILE.exists():
        key = API_KEY_FILE.read_text().strip()
    if not key:
        raise GenerationError(
            "No Anthropic API key found. "
            "Export it with: export ANTHROPIC_API_KEY=sk-ant-... "
            f"or put it in {API_KEY_FILE}"
        )
    return anthropic.Anthropic(api_key=key)


def generate_question(prompt: str) -> Question:
    try:
        client = _client()
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=GENERATION_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        return parse_question_response(raw)
    except GenerationError:
        raise
    except anthropic.APIError as exc:
        raise GenerationError(f"Anthropic API error: {exc}") from exc
    except Exception as exc:
        raise GenerationError(f"Question generation failed: {exc}") from exc


def evaluate_answer(prompt: str) -> Evaluation:
    try:
        client = _client()
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=EVALUATION_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text
        return parse_evaluation_response(raw)
    except EvaluationError:
        raise
    except anthropic.APIError as exc:
        raise EvaluationError(f"Anthropic API error: {exc}") from exc
    except Exception as exc:
        raise EvaluationError(f"Answer evaluation failed: {exc}") from exc
