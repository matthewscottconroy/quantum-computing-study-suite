"""Coloured capsule labels — the widget is shared, the colours are ours.

:class:`common.ui.widgets.PillBadge` is the widget (math-quiz and quantum-quiz
shipped identical copies).  The two factory helpers below stay here because
they reach into *this app's* colour vocabulary, which is not shared style.
"""

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.widgets import PillBadge

from ui import theme

__all__ = ["PillBadge", "make_subject_pill", "make_difficulty_pill"]


def make_subject_pill(subject: str, parent=None) -> PillBadge:
    return PillBadge(subject, theme.subject_color(subject), parent)


def make_difficulty_pill(difficulty: str, parent=None) -> PillBadge:
    color = theme.DIFFICULTY_COLORS.get(difficulty, theme.ACCENT)
    return PillBadge(difficulty.upper(), color, parent)
