"""Grade a user's answer to a paper question via Claude."""
from __future__ import annotations
import json
from core.models import Evaluation, Verdict
from ai.client import make_client

_SYSTEM = (
    "You are a rigorous but fair physics tutor grading answers to research paper questions. "
    "Base your evaluation strictly on the paper context provided."
)

_USER_TMPL = """\
Paper context (truncated):
{context}

Question: {question}

Student answer:
{answer}

Evaluate the answer. Return JSON only (no markdown), with keys:
  "score": integer 0–10
  "feedback": 2–4 sentences explaining what was right/wrong
  "model_answer": concise ideal answer (3–6 sentences)
"""


def grade_answer(paper_text: str, question: str, answer: str) -> Evaluation:
    from config import MAX_PAPER_CHARS
    client, model = make_client()
    context = paper_text[:MAX_PAPER_CHARS]
    prompt = _USER_TMPL.format(context=context, question=question, answer=answer)

    msg = client.messages.create(
        model=model,
        max_tokens=512,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.lower().startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    data = json.loads(raw)
    score = max(0, min(10, int(data["score"])))
    if score >= 7:
        verdict = Verdict.CORRECT
    elif score >= 4:
        verdict = Verdict.PARTIAL
    else:
        verdict = Verdict.INCORRECT

    return Evaluation(
        score=score,
        verdict=verdict,
        feedback=data.get("feedback", ""),
        model_answer=data.get("model_answer", ""),
    )
