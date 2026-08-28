"""Optional Claude code review for dojo katas.

Everything else in the app is fully offline; this module is only imported
when the user clicks "Claude Review" and raises a clear error when no
API key is configured.
"""
from __future__ import annotations
import os
from config import API_KEY_FILE, MODEL
from core.models import Kata


def _get_client():
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY") or (
        API_KEY_FILE.read_text().strip() if API_KEY_FILE.exists() else None
    )
    if not key:
        raise RuntimeError(
            "No Anthropic API key found.\n\n"
            "Set the ANTHROPIC_API_KEY environment variable or put your key in\n"
            f"{API_KEY_FILE}\n\n"
            "The dojo itself is fully offline — only this review button needs a key."
        )
    return anthropic.Anthropic(api_key=key), MODEL


_SYSTEM = (
    "You are a senior Qiskit developer reviewing a student's solution to a "
    "short Qiskit 2.x coding kata. The code already passed the kata's "
    "assertion tests — do NOT re-grade correctness. Review STYLE and IDIOM: "
    "modern Qiskit 2.x API usage (V2 primitives, PUBs, generate_preset_pass_manager, "
    "qasm2/qasm3 modules, assign_parameters), little-endian handling, clarity, "
    "and anything that would bite on real hardware. Be specific and concise: "
    "a few short bullet points, praising what is genuinely idiomatic and "
    "flagging what is not. Plain text, no markdown headers."
)

_TMPL = """\
Kata task:
{prompt}

Student's passing solution:
```python
{code}
```

Give brief style/idiom feedback (the tests already passed).
"""


def review_code(kata: Kata, user_code: str) -> str:
    client, model = _get_client()
    msg = client.messages.create(
        model=model,
        max_tokens=700,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": _TMPL.format(prompt=kata.prompt, code=user_code),
        }],
    )
    return msg.content[0].text.strip()
