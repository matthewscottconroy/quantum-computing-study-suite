"""Generate comprehension questions from paper text via Claude."""
from __future__ import annotations
import json
from config import MAX_PAPER_CHARS
from core.models import Question
from ai.client import make_client

_SYSTEM = (
    "You are an expert physics and quantum computing tutor. "
    "Given a research paper excerpt, generate comprehension questions that test "
    "deep understanding — not mere recall. Mix factual, conceptual, and derivation questions."
)

_USER_TMPL = """\
Paper excerpt (may be truncated):

{text}

Generate exactly {n} questions about the above paper.
Return a JSON array with no extra text. Each element has:
  "index": integer starting at 1,
  "text": the question string,
  "type": one of "factual" | "conceptual" | "derivation"
"""


def generate_questions(paper_text: str, count: int) -> list[Question]:
    client, model = make_client()
    truncated = paper_text[:MAX_PAPER_CHARS]
    prompt = _USER_TMPL.format(text=truncated, n=count)

    msg = client.messages.create(
        model=model,
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.lower().startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    data = json.loads(raw)
    return [
        Question(index=d["index"], text=d["text"], q_type=d.get("type", "conceptual"))
        for d in data
    ]
