"""Per-problem result screen for qec-trainer.

This is where a study item is shown with its answer, so it is where the errata
control lives: "⚠ Report a problem with this item" opens the shared
:class:`common.ui.errata_dialog.ErrataDialog`, which builds a prefilled GitHub
issue URL for *this* problem (its id, its text, the learner's comment).  The
button is an ordinary tab-reachable QPushButton, the URL is built offline, and
opening it is handed to ``QDesktopServices`` — if there is no browser the link
goes to the clipboard and is printed on screen instead.
"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QPushButton, QFrame, QApplication,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.errata_dialog import ErrataButton

from config import APP_DIR_NAME
from core.models import Attempt, Verdict
from ui import theme
from ui.widgets.mistake_row import MistakeRow


_VERDICT_GLYPH = {
    Verdict.CORRECT:   "\u2713",   # ✓  — paired with colour, never colour alone
    Verdict.PARTIAL:   "\u25d0",   # ◐
    Verdict.INCORRECT: "\u2717",   # ✗
}


class ResultScreen(QWidget):
    next_requested  = pyqtSignal()
    flag_requested  = pyqtSignal()
    cause_selected  = pyqtSignal(str)    # a persistence.MISTAKE_CAUSES value
    note_edited     = pyqtSignal(str)
    errata_reported = pyqtSignal(str)    # the GitHub issue URL that was opened

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 20)
        root.setSpacing(16)

        score_row = QHBoxLayout()
        self._score_lbl = QLabel("")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold;")
        score_row.addWidget(self._score_lbl)
        score_row.addStretch()
        self._verdict_lbl = QLabel("")
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold;")
        score_row.addWidget(self._verdict_lbl)
        root.addLayout(score_row)

        self._q_lbl = QLabel("")
        self._q_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_MUTED};")
        self._q_lbl.setWordWrap(True)
        root.addWidget(self._q_lbl)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        fb_card = QFrame(); fb_card.setObjectName("card")
        fb_l = QVBoxLayout(fb_card)
        fb_l.setContentsMargins(20, 16, 20, 16)
        fb_l.addWidget(self._muted_label("Explanation"))
        self._explanation_browser = QTextBrowser()
        self._explanation_browser.setMinimumHeight(100)
        fb_l.addWidget(self._explanation_browser)
        root.addWidget(fb_card)

        # Mistake journal — only shown after a wrong answer. The mistake is
        # already logged by then, so ignoring this row loses nothing.
        self._mistake_card = QFrame(); self._mistake_card.setObjectName("card")
        mk_l = QVBoxLayout(self._mistake_card)
        mk_l.setContentsMargins(20, 12, 20, 12)
        mk_l.setSpacing(6)
        self._mistake_row = MistakeRow()
        self._mistake_row.cause_chosen.connect(self.cause_selected)
        self._mistake_row.note_edited.connect(self.note_edited)
        mk_l.addWidget(self._mistake_row)
        self._mistake_card.hide()
        root.addWidget(self._mistake_card)

        # Errata — "this item itself is wrong", as opposed to "flag it for me
        # to revisit".  Hidden until a report is made; then it says what
        # happened, and carries the URL when no browser could be opened.
        self._errata_lbl = QLabel("")
        self._errata_lbl.setWordWrap(True)
        self._errata_lbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        self._errata_lbl.setStyleSheet(
            f"font-size: 11px; color: {theme.TEXT_MUTED};")
        self._errata_lbl.setAccessibleName("Error report status")
        self._errata_lbl.hide()
        root.addWidget(self._errata_lbl)

        root.addStretch()

        btn_row = QHBoxLayout()
        self._flag_btn = QPushButton("⚑ Flag for Review")
        self._flag_btn.setObjectName("flat")
        self._flag_btn.setAccessibleName("Flag this problem for review")
        self._flag_btn.clicked.connect(self.flag_requested)
        btn_row.addWidget(self._flag_btn)

        self._errata_btn = ErrataButton(
            app=APP_DIR_NAME, open_browser=False,
            text="⚠ Report a problem with this item")
        self._errata_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._errata_btn.setAccessibleName(
            "Report a problem with this item on GitHub")
        self._errata_btn.reported.connect(self._on_errata_reported)
        btn_row.addWidget(self._errata_btn)

        btn_row.addStretch()
        self._next_btn = QPushButton("Next Problem")
        self._next_btn.setObjectName("accent")
        self._next_btn.clicked.connect(self.next_requested)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    def _muted_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        return lbl

    def show_attempt(self, attempt: Attempt, is_last: bool) -> None:
        color = (
            theme.SUCCESS if attempt.verdict == Verdict.CORRECT else
            theme.PARTIAL if attempt.verdict == Verdict.PARTIAL else
            theme.ERROR
        )
        self._score_lbl.setText(f"{attempt.score}/10")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        glyph = _VERDICT_GLYPH.get(attempt.verdict, "")
        self._verdict_lbl.setText(f"{glyph} {attempt.verdict.value}".strip())
        self._verdict_lbl.setAccessibleName(f"Verdict: {attempt.verdict.value}")
        self._score_lbl.setAccessibleName(f"Score {attempt.score} out of 10")
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color};")
        self._q_lbl.setText(attempt.problem.question)

        explanation = attempt.feedback or attempt.problem.explanation
        if attempt.model_answer and attempt.model_answer != attempt.problem.explanation:
            explanation += f"\n\nModel answer: {attempt.model_answer}"
        self._explanation_browser.setPlainText(explanation)
        self._next_btn.setText("View Summary" if is_last else "Next Problem")
        self._next_btn.setAccessibleName(self._next_btn.text())

        # Point the errata control at the item now on screen.
        self._errata_btn.set_item(attempt.problem.id,
                                  self._item_text(attempt))
        self._errata_lbl.hide()
        self._errata_lbl.setText("")

    def set_flagged(self, flagged: bool) -> None:
        """Update flag button to reflect flagged state. Button always enabled."""
        if flagged:
            self._flag_btn.setText("⚑ Flagged — click to unflag")
        else:
            self._flag_btn.setText("⚑ Flag for Review")
        self._flag_btn.setAccessibleName(self._flag_btn.text().lstrip("⚑ "))
        self._flag_btn.setEnabled(True)

    def show_mistake_row(self, logged: bool = True) -> None:
        """Reveal the "What went wrong?" row for a freshly logged mistake."""
        self._mistake_row.reset(logged=logged)
        self._mistake_card.show()

    def hide_mistake_row(self) -> None:
        self._mistake_card.hide()

    @property
    def mistake_row(self) -> MistakeRow:
        """The cause/note row — exposed for headless drives and tests."""
        return self._mistake_row

    @property
    def errata_button(self) -> ErrataButton:
        """The "report a problem" control — exposed for headless drives."""
        return self._errata_btn

    # ── Errata ────────────────────────────────────────────────────────────────

    @staticmethod
    def _item_text(attempt: Attempt) -> str:
        """The item exactly as the learner saw it, for the "quote it" field.

        A maintainer can reconstruct everything else from the id; the rendered
        question, its choices and the answer the bank calls correct are what
        they cannot.
        """
        p = attempt.problem
        lines = [p.question]
        for i, choice in enumerate(p.choices or []):
            lines.append(f"{chr(65 + i)}. {choice}")
        if p.choices and 0 <= p.correct_index < len(p.choices):
            lines.append(f"Bank answer: {chr(65 + p.correct_index)}. "
                         f"{p.choices[p.correct_index]}")
        if p.explanation:
            lines.append(f"Explanation: {p.explanation}")
        return "\n".join(lines)

    def _on_errata_reported(self, url: str) -> None:
        """Hand the finished issue URL to the browser, or to the clipboard.

        Never raises and never waits on anything: ``openUrl`` hands off to the
        desktop and returns, and a machine with no browser (a kiosk, a remote
        session, the offscreen platform) falls back to the clipboard so the
        report is not lost.
        """
        opened = False
        try:
            opened = bool(QDesktopServices.openUrl(QUrl(url)))
        except Exception:
            opened = False
        if opened:
            self._errata_lbl.setText(
                "Opened a prefilled issue in your browser. Nothing is sent "
                "until you submit it there.")
        elif self._copy_to_clipboard(url):
            self._errata_lbl.setText(
                "No browser could be opened — the issue link is on your "
                "clipboard. Paste it into a browser to finish the report.")
        else:
            self._errata_lbl.setText(
                "No browser could be opened. Copy this link to finish the "
                f"report:\n{url}")
        self._errata_lbl.show()
        self.errata_reported.emit(url)

    @staticmethod
    def _copy_to_clipboard(text: str) -> bool:
        try:
            clipboard = QApplication.clipboard()
            if clipboard is None:
                return False
            clipboard.setText(text)
            return True
        except Exception:
            return False
