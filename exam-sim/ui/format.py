"""Render question text (with optional fenced code blocks) to rich HTML."""
from __future__ import annotations
import html
from ui import theme

_PRE_STYLE = (
    f"background-color:{theme.SURFACE2}; color:{theme.TEXT};"
    f"font-family:{theme.MONO}; font-size:13px;"
)


def question_html(text: str) -> str:
    """Convert question text to HTML: ``` fences become monospace <pre> blocks."""
    parts = text.split("```")
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # inside a fence
            code = part
            # strip an optional language tag on the first line
            first_nl = code.find("\n")
            if first_nl != -1 and code[:first_nl].strip().isalnum():
                code = code[first_nl + 1:]
            code = code.strip("\n")
            out.append(f'<pre style="{_PRE_STYLE}">{html.escape(code)}</pre>')
        else:
            out.append(html.escape(part).replace("\n", "<br>"))
    return "".join(out)
