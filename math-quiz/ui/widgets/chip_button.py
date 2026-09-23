"""Small checkable "chip" button used by the confidence strip and the
mistake-journal cause row.

Accessibility notes (these are the reason this is a widget and not a lambda):

* ``StrongFocus`` + an explicit ``:focus`` rule gives a visible 2 px focus
  ring, so the chips are usable from the keyboard alone (Tab / Space).
* Selection is never signalled by colour alone — the leading glyph flips from
  "○" to "✓" and the label goes bold, as well as the accent border. Both states
  carry a glyph so the label never shifts or elides when it is selected.
* Text stays :data:`ui.theme.TEXT` in both states (12.9:1 unchecked on
  ``SURFACE2``, 9.4:1 checked on the accent-tinted fill — both well past the
  4.5:1 minimum), and the state is mirrored into the accessible description
  for screen readers.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QPushButton

from ui import theme

CHECK_GLYPH = "✓"
UNCHECK_GLYPH = "○"
# Horizontal chrome around the label: 12 px padding + 2 px border each side,
# plus a little slack for the stylesheet font differing from the widget font.
_CHIP_CHROME_PX = 34


def _rgba(hex_color: str, alpha: float) -> str:
    """'#58a6ff', 0.18 → 'rgba(88, 166, 255, 0.18)' (Qt QSS understands rgba)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


CHIP_QSS = f"""
QPushButton {{
    background-color: {theme.SURFACE2};
    color: {theme.TEXT};
    border: 1px solid {theme.BORDER};
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 12px;
}}
QPushButton:hover {{ border-color: {theme.ACCENT}; }}
QPushButton:focus {{
    border: 2px solid {theme.ACCENT};
    padding: 3px 11px;
}}
QPushButton:checked {{
    background-color: {_rgba(theme.ACCENT, 0.18)};
    color: {theme.TEXT};
    border: 2px solid {theme.ACCENT};
    padding: 3px 11px;
    font-weight: bold;
}}
"""


class ChipButton(QPushButton):
    """Checkable pill whose checked state carries a glyph, not just a colour."""

    def __init__(self, text: str, accessible_name: str = "",
                 tooltip: str = "", parent=None) -> None:
        super().__init__(text, parent)
        self._base_text = text
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(accessible_name or text)
        if tooltip:
            self.setToolTip(tooltip)
        self.setStyleSheet(CHIP_QSS)
        # Reserve the *checked* (bold) width up front: growing the label on
        # click would otherwise elide it inside the already-laid-out button.
        bold = QFont(self.font())
        bold.setBold(True)
        self.setMinimumWidth(
            QFontMetrics(bold).horizontalAdvance(f"{CHECK_GLYPH} {text}")
            + _CHIP_CHROME_PX
        )
        self.toggled.connect(self._sync_state)
        self._sync_state(False)

    def base_text(self) -> str:
        return self._base_text

    def _sync_state(self, checked: bool) -> None:
        glyph = CHECK_GLYPH if checked else UNCHECK_GLYPH
        self.setText(f"{glyph} {self._base_text}")
        self.setAccessibleDescription("selected" if checked else "not selected")
