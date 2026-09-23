"""The small widgets the apps genuinely repeated.

Four of these existed in two to eight app trees each, with differences that
were comment-only, or that were one app's improvement the others never got.

Reconciled divergences
======================
:class:`LoadingOverlay`
    Two families.  The plain one (qec-trainer, vqa-trainer, paper-drill,
    problem-trainer, qiskit-dojo — a translucent stylesheet background and a
    single label) and the animated one (math-quiz, quantum-quiz,
    circuit-trainer — ``paintEvent`` fill, a sub-label, and a dot-ellipsis
    timer).  **Kept: the animated one**, because it is a strict superset and
    because a static "Grading…" over a frozen window is indistinguishable
    from a hang.  Both APIs are provided: ``show_message(main, sub="")`` and
    the older ``show_with_message`` alias, plus ``hide_overlay()``, which the
    plain family lacked — it left the timer running and the widget shown.
    The plain family also resized against ``self.parent()``, which is the
    *QObject* parent and has no ``size()`` when it is not a widget; the
    animated family's ``parentWidget()`` is correct and is what is kept.

:class:`CollapsiblePanel`
    math-quiz / quantum-quiz / circuit-trainer.  Identical but for the
    animation duration (a ``config`` constant in two, a private module
    constant in the third) and quantum-quiz wrapping the content in a
    ``QScrollArea`` "to handle large model answers".  **Kept:** the scroll
    area (a long model answer must not push the panel past the window) and
    :data:`common.ui.theme.COLLAPSIBLE_ANIMATION_MS`, overridable per panel.

:class:`PillBadge`
    math-quiz / quantum-quiz, identical bar comments.  The ``{color}22`` /
    ``{color}55`` alpha suffixes are now :func:`common.ui.theme.alpha` calls.
    The two ``make_*_pill`` helpers that reached into each app's own colour
    map stay in the app — they are app vocabulary, not shared style.

:class:`ScoreBar`
    math-quiz / quantum-quiz, identical but for an unused ``QFont`` import.
    The 0-10 block gradient is the suite's scoring scale; ``blocks`` is now a
    constructor argument so a 0-5 scale needs no second copy.
"""
from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
# pyqtProperty is a runtime decorator PyQt6's bundled stubs do not declare.
from PyQt6.QtCore import pyqtProperty  # type: ignore[attr-defined]
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from common.ui import theme


class LoadingOverlay(QWidget):
    """A translucent "working…" cover over its parent widget.

    Blocks mouse input to what is underneath (an answer must not be submitted
    twice while it is being graded) and animates a dot ellipsis so a slow
    Claude call never looks like a frozen window.
    """

    #: Milliseconds between dot-ellipsis frames.
    TICK_MS = 400

    def __init__(self, parent: QWidget, message: str = "Working…") -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.hide()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel(message, self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(
            f"color: {theme.TEXT}; font-size: 18px; font-weight: bold;"
            " background: transparent;"
        )
        layout.addWidget(self._label)

        self._sub = QLabel("", self)
        self._sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub.setWordWrap(True)
        self._sub.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: 13px; background: transparent;"
        )
        layout.addWidget(self._sub)

        self._base = message
        self._dots = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    # -- public ------------------------------------------------------------

    def show_message(self, main: str, sub: str = "") -> None:
        """Show the overlay over the whole parent with this message."""
        self._base = main.rstrip(".")
        self._dots = 0
        self._label.setText(main)
        self._sub.setText(sub)
        parent = self.parentWidget()
        if parent is not None:
            self.resize(parent.size())
        self.raise_()
        self.show()
        self._timer.start(self.TICK_MS)

    #: The name three apps used; kept so a migration is a one-line import swap.
    show_with_message = show_message

    def hide_overlay(self) -> None:
        """Hide the overlay and stop the animation.

        Five of the ten copies had no such method and simply called ``hide()``,
        leaving a 400 ms timer running for the life of the window.
        """
        self._timer.stop()
        self.hide()

    # -- Qt ----------------------------------------------------------------

    def resizeEvent(self, event) -> None:      # noqa: N802 (Qt naming)
        parent = self.parentWidget()
        if parent is not None:
            self.resize(parent.size())
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:       # noqa: N802 (Qt naming)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(13, 17, 23, 210))
        painter.end()

    def _tick(self) -> None:
        self._dots = (self._dots + 1) % 4
        self._label.setText(self._base + "." * self._dots)


class CollapsiblePanel(QWidget):
    """A disclosure panel: a flat toggle button over an animated content area.

    Used for model answers, hints and worked solutions — content that must be
    available but must not be on screen before the learner has tried.
    """

    def __init__(self, title: str, content_widget: QWidget, parent=None, *,
                 duration_ms: int = theme.COLLAPSIBLE_ANIMATION_MS,
                 expanded: bool = False) -> None:
        super().__init__(parent)
        self._title = title
        self._content = content_widget
        self._duration = duration_ms

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._toggle = QPushButton(f"▶  {title}")
        self._toggle.setObjectName("flat")
        self._toggle.setCheckable(True)
        self._toggle.clicked.connect(self._on_toggle)
        self._toggle.setStyleSheet(
            f"text-align: left; padding: 6px 4px; color: {theme.ACCENT}; "
            "font-size: 13px; font-weight: bold;"
        )
        layout.addWidget(self._toggle)

        # A scroll area, so a long model answer scrolls inside the panel
        # instead of pushing the rest of the screen off the bottom.
        self._area = QScrollArea()
        self._area.setWidgetResizable(True)
        self._area.setWidget(content_widget)
        self._area.setStyleSheet(
            f"background: {theme.SURFACE}; border-radius: 6px;")
        self._area.setMaximumHeight(0)
        self._area.setMinimumHeight(0)
        layout.addWidget(self._area)

        if expanded:
            self._toggle.setChecked(True)
            self._on_toggle(True)

    @property
    def expanded(self) -> bool:
        return self._toggle.isChecked()

    def set_expanded(self, expanded: bool) -> None:
        """Open or close the panel programmatically."""
        if self._toggle.isChecked() != bool(expanded):
            self._toggle.setChecked(bool(expanded))
            self._on_toggle(bool(expanded))

    def _on_toggle(self, checked: bool) -> None:
        arrow = "▼" if checked else "▶"
        self._toggle.setText(f"{arrow}  {self._title}")
        target = self._content.sizeHint().height() + 20 if checked else 0
        anim = QPropertyAnimation(self._area, b"maximumHeight", self)
        anim.setDuration(self._duration)
        anim.setStartValue(self._area.maximumHeight())
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        self._anim = anim                      # keep a reference alive


class PillBadge(QLabel):
    """A coloured capsule label — a subject, a difficulty, a section."""

    def __init__(self, text: str, color: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_color(color)

    def _set_color(self, color: str) -> None:
        self.setStyleSheet(
            f"background-color: {theme.alpha(color, 13)};"
            f"color: {color};"
            f"border: 1px solid {theme.alpha(color, 33)};"
            "border-radius: 10px;"
            "padding: 2px 10px;"
            "font-size: 11px;"
            "font-weight: bold;"
        )

    def update_text(self, text: str, color: str) -> None:
        self.setText(text)
        self._set_color(color)


class ScoreBar(QWidget):
    """An animated block bar for a 0-N score (N = 10 across the suite).

    Red at the bottom through yellow to green at the top, filling on entry so
    the number is felt before it is read.
    """

    def __init__(self, parent=None, *, blocks: int = 10,
                 duration_ms: int = theme.SCORE_BAR_ANIMATION_MS) -> None:
        super().__init__(parent)
        self._score: float = 0.0
        self._blocks = max(1, int(blocks))
        self._duration = duration_ms
        self.setFixedHeight(32)
        self.setMinimumWidth(200)

    # -- Qt property, so QPropertyAnimation can drive it --------------------

    def _get_score(self) -> float:
        return self._score

    def _set_score(self, value: float) -> None:
        self._score = value
        self.update()

    score = pyqtProperty(float, _get_score, _set_score)

    # -- public ------------------------------------------------------------

    def animate_to(self, target: float) -> None:
        """Fill from empty to *target* over the theme's animation duration."""
        anim = QPropertyAnimation(self, b"score", self)
        anim.setDuration(self._duration)
        anim.setStartValue(0.0)
        anim.setEndValue(float(target))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._anim = anim                      # keep a reference alive

    def set_score(self, value: float) -> None:
        """Set the score with no animation (restoring a saved screen)."""
        self._set_score(float(value))

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:       # noqa: N802 (Qt naming)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        blocks = self._blocks
        gap = 4
        block_w = (self.width() - (blocks - 1) * gap) / blocks
        block_h = self.height()

        filled = int(self._score)
        frac = self._score - filled

        for i in range(blocks):
            x = i * (block_w + gap)
            if i < filled:
                color = block_color(i, blocks)
            elif i == filled and frac > 0.01:
                color = QColor(block_color(i, blocks))
                color.setAlphaF(frac)
            else:
                color = QColor(theme.SURFACE2)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(x), 0, int(block_w), block_h, 4, 4)

        painter.end()


def block_color(index: int, blocks: int = 10) -> QColor:
    """Gradient for the score bar: red at 0 -> yellow -> green at the top."""
    span = max(1, blocks - 1)
    t = min(1.0, max(0.0, index / span))
    if t < 0.5:
        r, g, b = 248, int(83 + t * 2 * (185 - 83)), 73
    else:
        r, g, b = int(248 - (t - 0.5) * 2 * (248 - 63)), 185, 80
    return QColor(r, g, b)


__all__ = ["LoadingOverlay", "CollapsiblePanel", "PillBadge", "ScoreBar",
           "block_color"]
