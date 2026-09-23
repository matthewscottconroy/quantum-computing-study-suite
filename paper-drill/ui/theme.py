"""Dark theme — the suite palette plus paper-drill's own vocabulary.

The twelve palette constants and the base stylesheet were byte-identical in
all ten apps, so they now live in ``common.ui.theme`` and this module is a
re-export of them.  What stays here is what is genuinely this app's:
``QTYPE_COLORS`` (paper-drill grades questions as factual / conceptual /
derivation) and the two widget rules the base sheet has no reason to carry.

``from ui import theme`` keeps working exactly as before — ``theme.BG``,
``theme.ACCENT``, ``theme.apply(app)`` — so no screen needed a change.
"""
import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.theme import *          # noqa: F403  (the palette + QSS + alpha)
from common.ui.theme import (          # noqa: F401  (named, for the rules below)
    ACCENT, ACCENT2, BORDER, SURFACE, TEXT, extend,
)
from common.ui.theme import apply as _apply

#: Question types paper-drill asks for, and the colour each is labelled with.
#: App vocabulary, not shared style — the other nine apps have their own maps.
QTYPE_COLORS = {
    "factual":     "#1f6feb",
    "conceptual":  "#6e40c9",
    "derivation":  "#d29922",
}

#: Rules the base sheet does not carry because only this app used them: the
#: tree/splitter pair styled for the library and history panes.
_EXTRA = f"""
QTreeWidget {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 8px; padding: 4px; outline: none;
}}
QTreeWidget::item {{ padding: 4px 2px; border-radius: 4px; }}
QTreeWidget::item:hover {{ background-color: {ACCENT}22; }}
QTreeWidget::item:selected {{ background-color: {ACCENT2}; color: white; }}
QTreeWidget::branch {{ background: transparent; }}
QSplitter::handle {{ background-color: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical {{ height: 1px; }}
"""

#: The stylesheet this app actually installs: the shared base plus _EXTRA.
QSS_APP = extend(_EXTRA)


def apply(app) -> None:
    """Install the suite theme, extended with this app's own rules."""
    _apply(app, QSS_APP)
