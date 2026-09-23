"""Subject / difficulty pills.

The badge itself is :class:`common.ui.widgets.PillBadge` — it was identical in
math-quiz and quantum-quiz.  What stays here are the two factories, because
they reach into *this app's* colour vocabulary (one colour per mathematical
subject, one per difficulty level), which is not shared style.
"""

from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.widgets import PillBadge

from ui import theme

__all__ = ["PillBadge", "make_subject_pill", "make_difficulty_pill"]


def make_subject_pill(subject: str, parent=None) -> PillBadge:
    return PillBadge(subject, theme.subject_color(subject), parent)


def make_difficulty_pill(difficulty: str, parent=None) -> PillBadge:
    color = theme.DIFFICULTY_COLORS.get(difficulty, theme.ACCENT)
    return PillBadge(difficulty.upper(), color, parent)
