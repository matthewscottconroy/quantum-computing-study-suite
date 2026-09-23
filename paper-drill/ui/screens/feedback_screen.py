"""Per-question feedback screen — shows score, feedback, model answer, a
flag-for-review toggle, an errata report control, and (on a wrong answer) the
mistake-journal row."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QPushButton, QFrame, QLineEdit, QMessageBox,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import journal
from common.ui.errata_dialog import ErrataButton

from config import APP_ID
from core.models import QuestionAttempt, Verdict
from ui import theme

# Cause categories of the shared mistake-journal contract, in the order shown.
# The taxonomy and its labels come from common.journal, so the buttons and the
# rows written to mistakes.json can never drift apart.  A wrong answer is
# logged the moment it is graded; picking a cause turns that bookmark into
# analysis ("six misreads this month" is the signal).
MISTAKE_CAUSES = tuple((key, journal.CAUSE_LABELS[key])
                       for key in journal.MISTAKE_CAUSES)


class FeedbackScreen(QWidget):
    next_requested = pyqtSignal()
    done_requested = pyqtSignal()    # emitted on last question
    flag_requested = pyqtSignal()    # toggle "flag for review" on the shown question
    # (cause key or "" when only a note was typed, note text) — the journal
    # entry already exists by the time this fires; it is an update, not a save.
    mistake_cause_selected = pyqtSignal(str, str)
    # The GitHub issue URL that "Report a problem with this item" produced.
    errata_reported = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._is_last = False
        self._cause = None
        self._cause_buttons: dict[str, QPushButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 24)
        root.setSpacing(16)

        # Score row
        score_row = QHBoxLayout()
        self._score_lbl = QLabel("")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold;")
        score_row.addWidget(self._score_lbl)
        score_row.addStretch()
        self._verdict_lbl = QLabel("")
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold;")
        score_row.addWidget(self._verdict_lbl)
        root.addLayout(score_row)

        # Question recap
        self._q_lbl = QLabel("")
        self._q_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_MUTED};")
        self._q_lbl.setWordWrap(True)
        root.addWidget(self._q_lbl)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        # Feedback card
        fb_card = QFrame(); fb_card.setObjectName("card")
        fb_layout = QVBoxLayout(fb_card)
        fb_layout.setContentsMargins(20, 16, 20, 16)
        fb_lbl_hdr = QLabel("Feedback")
        fb_lbl_hdr.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        fb_layout.addWidget(fb_lbl_hdr)
        self._feedback_browser = QTextBrowser()
        self._feedback_browser.setFixedHeight(90)
        fb_layout.addWidget(self._feedback_browser)
        root.addWidget(fb_card)

        # Model answer card
        ma_card = QFrame(); ma_card.setObjectName("card")
        ma_layout = QVBoxLayout(ma_card)
        ma_layout.setContentsMargins(20, 16, 20, 16)
        ma_hdr = QLabel("Model Answer")
        ma_hdr.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        ma_layout.addWidget(ma_hdr)
        self._model_browser = QTextBrowser()
        self._model_browser.setFixedHeight(120)
        ma_layout.addWidget(self._model_browser)
        root.addWidget(ma_card)

        root.addStretch()

        self._mistake_row = self._build_mistake_row()
        root.addWidget(self._mistake_row)
        self._mistake_row.hide()

        btn_row = QHBoxLayout()
        self._flag_btn = QPushButton("⚑ Flag for Review")
        self._flag_btn.setObjectName("flat")
        self._flag_btn.setToolTip("Toggle this question in your review list")
        self._flag_btn.clicked.connect(self.flag_requested)
        btn_row.addWidget(self._flag_btn)
        btn_row.addWidget(self._build_errata_button())
        btn_row.addStretch()
        self._next_btn = QPushButton("Next Question")
        self._next_btn.setObjectName("accent")
        self._next_btn.clicked.connect(self._on_next)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    def show_attempt(self, attempt: QuestionAttempt, is_last: bool) -> None:
        self._is_last = is_last
        ev = attempt.evaluation
        score = ev.score if ev else 0
        verdict = ev.verdict if ev else Verdict.INCORRECT

        color = theme.SUCCESS if verdict == Verdict.CORRECT else (
            theme.PARTIAL if verdict == Verdict.PARTIAL else theme.ERROR
        )
        self._score_lbl.setText(f"{score}/10")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        self._verdict_lbl.setText(verdict.value)
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color};")

        self._q_lbl.setText(f"Q: {attempt.question.text}")
        self._feedback_browser.setPlainText(ev.feedback if ev else "")
        self._model_browser.setPlainText(ev.model_answer if ev else "")
        self._next_btn.setText("View Summary" if is_last else "Next Question")
        self.set_errata_item("", attempt.question.text)   # id set by the controller
        self.set_flagged(False)   # caller refreshes from persistence after this
        self.show_mistake_prompt(False)   # ditto: the controller decides

    def set_flagged(self, flagged: bool) -> None:
        """Reflect the question's flagged state on the toggle button."""
        self._flag_btn.setText(
            "⚑ Flagged — click to unflag" if flagged else "⚑ Flag for Review"
        )
        self._flag_btn.setStyleSheet(
            f"color: {theme.WARNING};" if flagged else ""
        )

    def is_flagged_shown(self) -> bool:
        return self._flag_btn.text().startswith("⚑ Flagged")

    # ------------------------------------------------------------------
    # Errata — "this question is wrong"
    #
    # The repository is public, and until now a wrong or ambiguous generated
    # question had no path from "this is wrong" to a fix except remembering it
    # later, which nobody does.  One click opens a GitHub issue that is already
    # filled in with the item id, the question as it was shown, and whatever the
    # learner types.  Nothing is sent from here: the issue form opens in the
    # browser and they submit it themselves.
    #
    # Three properties this has to keep:
    #   keyboard reachable  a plain QPushButton in the tab order, with an
    #                       accessible name and the base sheet's focus ring;
    #   never blocking      the drill is never gated on it — Next Question stays
    #                       live, no network call is made, and the "no browser"
    #                       fallback is a modeless box, not a modal one;
    #   degrades            QDesktopServices.openUrl returns False on a machine
    #                       with no browser (a bare container, a locked-down
    #                       desktop).  Instead of failing silently the URL is
    #                       shown in a selectable box so it can be copied out.
    # ------------------------------------------------------------------

    def _build_errata_button(self) -> ErrataButton:
        """The "report this item" control, opened by click or by keyboard.

        ``open_browser=False`` is deliberate: the shared button would call
        ``QDesktopServices.openUrl`` and ignore the result, so this screen does
        it instead and can fall back when there is no browser.
        """
        btn = ErrataButton(app=APP_ID, open_browser=False,
                           text="⚑ Report a problem with this item")
        btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        btn.setAccessibleName("Report a problem with this question")
        btn.setAccessibleDescription(
            "Opens a prefilled GitHub issue about this generated question")
        btn.setToolTip("Wrong, ambiguous or unanswerable from the paper? "
                       "Open a prefilled GitHub issue.")
        btn.reported.connect(self._on_errata_reported)
        self._errata_btn = btn
        return btn

    def set_errata_item(self, item_id: str, item_text: str = "") -> None:
        """Point the report control at the question currently on screen."""
        self._errata_btn.set_item(item_id, item_text)

    def _on_errata_reported(self, url: str) -> None:
        """Hand the built URL to the browser, or show it if there is none."""
        self.errata_reported.emit(url)
        opened = False
        try:
            opened = bool(QDesktopServices.openUrl(QUrl(url)))
        except Exception:
            opened = False
        if not opened:
            self._show_errata_url(url)

    def _show_errata_url(self, url: str) -> None:
        """Modeless, selectable fallback: the report is not lost to a missing
        browser, and the drill is not blocked waiting for a dialog."""
        box = QMessageBox(self)
        box.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        box.setWindowTitle("Could not open your browser")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText("Your report is ready, but no browser could be opened.\n"
                    "Copy this link and open it yourself:")
        box.setInformativeText(url)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse
                                    | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        box.setModal(False)
        box.show()

    # ------------------------------------------------------------------
    # Mistake journal — "What went wrong?"
    # ------------------------------------------------------------------

    def _build_mistake_row(self) -> QWidget:
        """Compact, skippable cause picker shown under a wrong answer.

        Never a modal and never a blocker: Next Question stays live, and the
        mistake is already on record with cause=null before this row is even
        shown.  Keyboard reachable, dashed accent focus ring, ✓ glyph on the
        chosen cause (state is never colour alone).
        """
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            f"QFrame#card {{ background-color: {theme.SURFACE};"
            f" border: 1px solid {theme.BORDER}; border-radius: 8px; }}"
            f"QPushButton {{ padding: 5px 12px; font-size: 12px; }}"
            f"QPushButton[chosen=\"yes\"] {{ border: 2px solid {theme.ACCENT};"
            f" color: {theme.TEXT}; font-weight: bold; background: {theme.SURFACE2}; }}"
            f"QPushButton:focus {{ border: 2px dashed {theme.ACCENT}; }}"
            f"QLineEdit:focus {{ border: 2px dashed {theme.ACCENT}; }}"
        )
        outer = QVBoxLayout(card)
        outer.setContentsMargins(20, 12, 20, 12)
        outer.setSpacing(8)

        hdr_row = QHBoxLayout()
        hdr_row.setSpacing(8)
        hdr = QLabel("What went wrong?")
        hdr.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {theme.TEXT};")
        hdr_row.addWidget(hdr)
        hint = QLabel("optional — skip it and the mistake is still logged")
        hint.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        hdr_row.addWidget(hint)
        hdr_row.addStretch()
        outer.addLayout(hdr_row)

        btns = QHBoxLayout()
        btns.setSpacing(8)
        for key, label in MISTAKE_CAUSES:
            btn = QPushButton(label)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setAccessibleName(f"Cause: {label}")
            btn.setAccessibleDescription("Optional — why this answer was wrong")
            btn.clicked.connect(lambda _checked=False, k=key: self._on_cause(k))
            self._cause_buttons[key] = btn
            btns.addWidget(btn)
        btns.addStretch()
        outer.addLayout(btns)

        self._note_edit = QLineEdit()
        self._note_edit.setPlaceholderText(
            "Optional note — e.g. \u201cread the qubit order backwards again\u201d"
        )
        self._note_edit.setAccessibleName("Note about this mistake (optional)")
        self._note_edit.setMaxLength(200)
        self._note_edit.returnPressed.connect(self._on_note_committed)
        self._note_edit.editingFinished.connect(self._on_note_committed)
        outer.addWidget(self._note_edit)
        return card

    def show_mistake_prompt(self, visible: bool) -> None:
        """Show (and reset) the cause picker, or hide it on a right answer."""
        self._cause = None
        self._note_edit.clear()
        self._paint_causes()
        self._mistake_row.setVisible(bool(visible))

    def mistake_prompt_visible(self) -> bool:
        return not self._mistake_row.isHidden()

    def selected_cause(self) -> str | None:
        return self._cause

    def note_text(self) -> str:
        return self._note_edit.text().strip()

    def _paint_causes(self) -> None:
        for key, label in MISTAKE_CAUSES:
            btn = self._cause_buttons[key]
            chosen = (key == self._cause)
            btn.setText(f"✓ {label}" if chosen else label)
            btn.setProperty("chosen", "yes" if chosen else "no")
            btn.setAccessibleDescription(
                "Selected" if chosen else "Optional — why this answer was wrong"
            )
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _on_cause(self, key: str) -> None:
        # Clicking the chosen cause again clears it back to "not categorised".
        self._cause = None if self._cause == key else key
        self._paint_causes()
        self.mistake_cause_selected.emit(self._cause or "", self.note_text())

    def _on_note_committed(self) -> None:
        if not self.mistake_prompt_visible():
            return
        note = self.note_text()
        if not note and self._cause is None:
            return          # nothing to say — leave the entry as it was logged
        self.mistake_cause_selected.emit(self._cause or "", note)

    # ------------------------------------------------------------------

    def _on_next(self) -> None:
        if self._is_last:
            self.done_requested.emit()
        else:
            self.next_requested.emit()
