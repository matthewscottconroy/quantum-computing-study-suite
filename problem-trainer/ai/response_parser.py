"""Parse and validate raw Claude JSON responses into typed results.

Robustness pattern follows quantum-quiz/ai/response_parser.py: strip code
fences, fall back to extracting the first JSON object, validate fields.
"""
from __future__ import annotations
import json
import re
from core.models import GradeResult, StepCheck


class ParseError(Exception):
    pass


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.lower().startswith("json"):
                inner = inner[4:]
            text = inner.strip()
    return text


def _load(raw: str) -> dict:
    text = _strip_fences(raw)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fall back: grab the outermost {...} block anywhere in the text.
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            raise ParseError(f"No JSON object found in response:\n{raw[:400]}")
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError as exc:
            raise ParseError(f"Invalid JSON from Claude: {exc}\nRaw text:\n{raw[:400]}") from exc
    if not isinstance(data, dict):
        raise ParseError(f"Expected a JSON object, got {type(data).__name__}")
    return data


def parse_grade_response(raw: str) -> GradeResult:
    data = _load(raw)
    try:
        score = max(0, min(10, int(round(float(data["score"])))))
        missed = data.get("missed_points", [])
        if not isinstance(missed, list):
            missed = [str(missed)]
        return GradeResult(
            score=score,
            feedback=str(data.get("feedback", "")).strip(),
            missed_points=[str(p).strip() for p in missed if str(p).strip()],
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise ParseError(f"Missing/invalid field in grading response: {exc}") from exc


def parse_step_check_response(raw: str) -> StepCheck:
    data = _load(raw)
    try:
        verdict = str(data["verdict"]).strip().lower().replace("-", "_")
        if verdict not in ("accept", "needs_work"):
            # Be forgiving about near-miss labels.
            if verdict in ("accepted", "correct", "pass", "yes"):
                verdict = "accept"
            elif verdict in ("reject", "rejected", "incorrect", "needswork", "retry", "no"):
                verdict = "needs_work"
            else:
                raise ParseError(f"Unknown verdict: {verdict!r}")
        return StepCheck(verdict=verdict, nudge=str(data.get("nudge", "")).strip())
    except KeyError as exc:
        raise ParseError(f"Missing field in step-check response: {exc}") from exc
