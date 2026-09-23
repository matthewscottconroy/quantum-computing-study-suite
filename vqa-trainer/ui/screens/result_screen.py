"""Per-problem result screen for vqa-trainer."""
from __future__ import annotations
import common_path  # noqa: F401  (puts the repo root on sys.path)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QPushButton, QFrame, QApplication,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from common.ui.errata_dialog import ErrataButton
from config import APP_DIR_NAME
from core.models import Attempt, Verdict
from ui import theme
from ui.widgets.mistake_row import MistakeRow

# Verdict glyphs: the result must never be carried by colour alone.
_VERDICT_GLYPH = {
    Verdict.CORRECT:   "✓",   # check
    Verdict.PARTIAL:   "◐",   # half-filled circle
    Verdict.INCORRECT: "✗",   # cross
}


def item_text(attempt: Attempt) -> str:
    """The problem exactly as the learner saw it, for an errata report.

    A maintainer can look a bank id up, but "which of the four options was
    wrong" is only answerable from the text, so the choices go in too.
    """
    problem = attempt.problem
    parts = [problem.question.strip()]
    for i, choice in enumerate(problem.choices or []):
        parts.append(f"{chr(65 + i)}. {choice}")
    if problem.correct_value is not None:
        parts.append(f"(expected value: {problem.correct_value:.6g})")
    return "\n".join(p for p in parts if p)


class ResultScreen(QWidget):
    next_requested = pyqtSignal()
    flag_requested = pyqtSignal()
    mistake_cause_selected = pyqtSignal(str)
    mistake_note_committed = pyqtSignal(str)
    #: Emitted with the GitHub issue URL after an errata report is confirmed.
    errata_reported = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._is_last = False
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 20)
        root.setSpacing(16)

        score_row = QHBoxLayout()
        self._score_lbl = QLabel("")
        self._score_lbl.setStyleSheet("font-size: 36px; font-weight: bold;")
        score_row.addWidget(self._score_lbl)
        score_row.addStretch()
        self._verdict_lbl = QLabel("")
        self._verdict_lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
        score_row.addWidget(self._verdict_lbl)
        root.addLayout(score_row)

        self._q_lbl = QLabel("")
        self._q_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_MUTED};")
        self._q_lbl.setWordWrap(True)
        root.addWidget(self._q_lbl)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        exp_card = QFrame(); exp_card.setObjectName("card")
        exp_layout = QVBoxLayout(exp_card)
        exp_layout.setContentsMargins(20, 16, 20, 16)
        hdr = QLabel("Explanation")
        hdr.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        exp_layout.addWidget(hdr)
        self._explanation_browser = QTextBrowser()
        self._explanation_browser.setMinimumHeight(120)
        exp_layout.addWidget(self._explanation_browser)
        root.addWidget(exp_card)

        # Mistake journal — inline, compact, skippable. Shown only when the
        # answer scored below the app's "correct" bar (7/10).
        self._journal_card = QFrame(); self._journal_card.setObjectName("card")
        jl = QVBoxLayout(self._journal_card)
        jl.setContentsMargins(20, 12, 20, 12)
        jl.setSpacing(6)
        jhdr = QLabel("Mistake journal")
        jhdr.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        jl.addWidget(jhdr)
        self._mistake_row = MistakeRow()
        self._mistake_row.cause_selected.connect(self.mistake_cause_selected)
        self._mistake_row.note_committed.connect(self.mistake_note_committed)
        jl.addWidget(self._mistake_row)
        self._journal_card.hide()
        root.addWidget(self._journal_card)

        root.addStretch()

        # Fallback line for the errata button when no browser could be opened.
        self._errata_note = QLabel("")
        self._errata_note.setObjectName("subheading")
        self._errata_note.setWordWrap(True)
        self._errata_note.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        self._errata_note.setStyleSheet(f"font-size: 11px; color: {theme.WARNING};")
        self._errata_note.hide()
        root.addWidget(self._errata_note)

        btn_row = QHBoxLayout()
        self._flag_btn = QPushButton("⚑ Flag for Review")
        self._flag_btn.setObjectName("linkbtn")
        self._flag_btn.setAccessibleName("Flag this problem for review")
        self._flag_btn.clicked.connect(self.flag_requested)
        btn_row.addWidget(self._flag_btn)

        # "This item is wrong" -> a prefilled GitHub issue.  open_browser=False
        # because this screen opens the URL itself: QDesktopServices.openUrl
        # reports failure, and on a machine with no browser the link has to go
        # somewhere the learner can still reach it.
        self._errata_btn = ErrataButton(
            app=APP_DIR_NAME, open_browser=False,
            text="⚑ Report a problem with this item")
        self._errata_btn.setObjectName("linkbtn")
        self._errata_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._errata_btn.setAccessibleName("Report a problem with this problem")
        self._errata_btn.setAccessibleDescription(
            "Opens a prefilled GitHub issue about this item. Nothing is sent "
            "until you submit it there.")
        self._errata_btn.setEnabled(False)
        self._errata_btn.reported.connect(self._on_errata_reported)
        btn_row.addWidget(self._errata_btn)

        btn_row.addStretch()
        self._next_btn = QPushButton("Next Problem")
        self._next_btn.setObjectName("accent")
        self._next_btn.setAccessibleName("Next problem")
        self._next_btn.clicked.connect(self._on_next)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    def show_attempt(self, attempt: Attempt, is_last: bool) -> None:
        self._is_last = is_last
        color = (
            theme.SUCCESS if attempt.verdict == Verdict.CORRECT else
            theme.PARTIAL if attempt.verdict == Verdict.PARTIAL else
            theme.ERROR
        )
        glyph = _VERDICT_GLYPH.get(attempt.verdict, "")
        self._score_lbl.setText(f"{attempt.score}/10")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        self._score_lbl.setAccessibleName(f"Score {attempt.score} out of 10")
        self._verdict_lbl.setText(f"{glyph} {attempt.verdict.value}".strip())
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color};")
        self._verdict_lbl.setAccessibleName(f"Verdict: {attempt.verdict.value}")
        self._q_lbl.setText(attempt.problem.question)

        self._mistake_row.reset()
        self._journal_card.setVisible(attempt.score < 7)

        # Point the errata button at the problem now on screen.
        self._errata_btn.set_item(attempt.problem.id, item_text(attempt))
        self._errata_btn.setEnabled(True)
        self._errata_note.hide()
        self._errata_note.clear()

        text = attempt.feedback or attempt.problem.explanation
        if attempt.model_answer and attempt.model_answer not in text:
            text += f"\n\nModel answer: {attempt.model_answer}"
        self._explanation_browser.setPlainText(text)
        self._next_btn.setText("View Summary" if is_last else "Next Problem")

    def _on_next(self) -> None:
        self._mistake_row.flush_note()
        self.next_requested.emit()

    # -- errata --------------------------------------------------------------

    def _on_errata_reported(self, url: str) -> None:
        """Hand the prefilled issue URL to the system browser, or fall back.

        Never blocks and never raises into the session: ``openUrl`` returns
        False on a machine with no browser (or a sandbox with no portal), and
        the URL is then put on the clipboard and shown here so the report is
        not lost.
        """
        opened = False
        try:
            opened = bool(QDesktopServices.openUrl(QUrl(url)))
        except Exception:
            opened = False
        if opened:
            self._errata_note.hide()
        else:
            self._copy_to_clipboard(url)
            self._errata_note.setText(
                "Could not open a browser. The issue link has been copied to "
                "your clipboard — paste it into a browser when you have one."
            )
            self._errata_note.setToolTip(url)
            self._errata_note.show()
        self.errata_reported.emit(url)

    @staticmethod
    def _copy_to_clipboard(text: str) -> None:
        try:
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(text)
        except Exception:
            pass

    def errata_note(self) -> str:
        """The fallback message currently shown (``""`` when hidden)."""
        return self._errata_note.text() if not self._errata_note.isHidden() else ""

    # -- state ---------------------------------------------------------------

    def mistake_cause(self) -> str | None:
        return self._mistake_row.cause()

    def mistake_note(self) -> str:
        return self._mistake_row.note()

    def journal_visible(self) -> bool:
        return not self._journal_card.isHidden()

    def set_flagged(self, flagged: bool) -> None:
        if flagged:
            self._flag_btn.setText("⚑ Flagged — click to unflag")
        else:
            self._flag_btn.setText("⚑ Flag for Review")
        self._flag_btn.setEnabled(True)
