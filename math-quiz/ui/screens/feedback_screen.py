"""Evaluation / feedback screen shown after each answer is graded.

This is where a study item is finally *shown* — the question, your answer, the
grade and the model answer — so it is also where the "report a problem with
this item" control lives (:mod:`common.ui.errata_dialog`).
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextBrowser,
    QPushButton, QListWidget, QListWidgetItem, QFrame, QScrollArea,
    QApplication,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QColor, QDesktopServices

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.errata_dialog import ErrataButton
from common.ui.widgets import CollapsiblePanel, ScoreBar

from core.models import Evaluation
from persistence import APP, MISTAKE_CAUSES, NOTE_FIELD_MAX
from ui import theme
from ui.widgets.chip_button import ChipButton
from config import SCORE_CORRECT_THRESHOLD, SCORE_PARTIAL_THRESHOLD

# Cause code → button label, in the order they are shown.
CAUSE_LABELS: dict[str, str] = {
    "misread":          "Misread it",
    "didnt_know":       "Didn\u2019t know",
    "knew_but_slipped": "Knew but slipped",
    "confused":         "Confused two things",
    "out_of_time":      "Ran out of time",
    "other":            "Other",
}
NOTE_MAX_CHARS = NOTE_FIELD_MAX      # the journal clips to this anyway


class FeedbackScreen(QWidget):
    next_question_requested = pyqtSignal()
    flag_requested = pyqtSignal()          # toggle "flag for review" on this question
    # Mistake journal: cause code chosen ("" when the user unselects it again).
    mistake_cause_chosen = pyqtSignal(str)
    mistake_note_committed = pyqtSignal(str)
    #: An errata report was filed: (issue url, True if a browser opened it).
    errata_reported = pyqtSignal(str, bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._flagged = False
        self._cause_buttons: dict[str, ChipButton] = {}
        self._cause: str | None = None
        self._last_note_emitted = ""
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(48, 36, 48, 24)
        root.setSpacing(20)
        scroll.setWidget(content)

        # ── Score row ─────────────────────────────────────────────────────────
        score_row = QHBoxLayout()
        score_row.setSpacing(20)

        score_col = QVBoxLayout()
        score_col.setSpacing(6)
        score_lbl = QLabel("Score")
        score_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        score_col.addWidget(score_lbl)
        self._score_bar = ScoreBar()
        score_col.addWidget(self._score_bar)
        score_row.addLayout(score_col, 1)

        verdict_col = QVBoxLayout()
        verdict_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self._verdict_badge = QLabel("—")
        self._verdict_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._verdict_badge.setFixedHeight(32)
        verdict_col.addWidget(self._verdict_badge)
        score_row.addLayout(verdict_col)

        self._score_num = QLabel("")
        self._score_num.setStyleSheet("font-size: 28px; font-weight: bold;")
        self._score_num.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        score_row.addWidget(self._score_num)

        root.addLayout(score_row)

        sep = QFrame()
        sep.setObjectName("separator")
        root.addWidget(sep)

        # ── Feedback ──────────────────────────────────────────────────────────
        fb_lbl = QLabel("Feedback")
        fb_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        root.addWidget(fb_lbl)
        self._feedback_browser = QTextBrowser()
        self._feedback_browser.setMaximumHeight(120)
        root.addWidget(self._feedback_browser)

        # ── What went wrong? (mistake journal) ────────────────────────────────
        root.addWidget(self._build_mistake_row())

        # ── Model answer (collapsible) ────────────────────────────────────────
        self._model_answer_widget = QTextBrowser()
        self._model_answer_widget.setMinimumHeight(80)
        self._model_answer_widget.setStyleSheet(
            "font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', monospace;"
            "font-size: 13px; line-height: 1.5;"
        )
        self._model_panel = CollapsiblePanel("Model Answer", self._model_answer_widget)
        root.addWidget(self._model_panel)

        # ── Missed points ─────────────────────────────────────────────────────
        self._missed_container = QWidget()
        missed_layout = QVBoxLayout(self._missed_container)
        missed_layout.setContentsMargins(0, 0, 0, 0)
        missed_layout.setSpacing(6)
        missed_lbl = QLabel("Key points missed")
        missed_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        missed_layout.addWidget(missed_lbl)
        self._missed_list = QListWidget()
        self._missed_list.setMaximumHeight(120)
        missed_layout.addWidget(self._missed_list)
        root.addWidget(self._missed_container)

        # ── Follow-up ─────────────────────────────────────────────────────────
        self._followup_container = QFrame()
        self._followup_container.setObjectName("card")
        fu_layout = QVBoxLayout(self._followup_container)
        fu_layout.setContentsMargins(16, 12, 16, 12)
        fu_lbl = QLabel("Follow-up to consider")
        fu_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        fu_layout.addWidget(fu_lbl)
        self._followup_label = QLabel("")
        self._followup_label.setWordWrap(True)
        self._followup_label.setStyleSheet(f"font-style: italic; color: {theme.ACCENT};")
        fu_layout.addWidget(self._followup_label)
        root.addWidget(self._followup_container)

        root.addStretch()

        # ── Bottom bar ────────────────────────────────────────────────────────
        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(48, 12, 48, 12)
        self._flag_btn = QPushButton("⚑ Flag for review")
        self._flag_btn.setObjectName("flat")
        self._flag_btn.setToolTip(
            "Bookmark this question for later review (click again to remove)"
        )
        self._flag_btn.clicked.connect(self.flag_requested)
        bar_layout.addWidget(self._flag_btn)

        # "This item is wrong" -> a prefilled GitHub issue.  open_browser=False
        # so the browser call stays here, where a refusal can be handled
        # (see _on_errata_reported) instead of vanishing into the widget.
        self._errata_btn = ErrataButton(
            app=APP, open_browser=False,
            text="\u26a0 Report a problem with this item",
        )
        self._errata_btn.setAccessibleName("Report a problem with this question")
        self._errata_btn.setToolTip(
            "Wrong, ambiguous or badly worded? Open a prefilled GitHub issue "
            "(nothing is sent until you submit it there)."
        )
        self._errata_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._errata_btn.reported.connect(self._on_errata_reported)
        bar_layout.addWidget(self._errata_btn)

        bar_layout.addStretch()
        next_btn = QPushButton("Next Question →")
        next_btn.setObjectName("accent")
        next_btn.clicked.connect(self.next_question_requested)
        bar_layout.addWidget(next_btn)
        outer.addWidget(bar)

    def _build_mistake_row(self) -> QFrame:
        """Compact, skippable "what went wrong?" row for a wrong answer.

        The mistake itself is already journalled by the time this appears
        (cause=null); these buttons only add the diagnosis, which is the part
        that turns a pile of wrong answers into a pattern. Nothing here blocks
        the flow: "Next Question" stays live and no modal is ever shown.
        """
        self._mistake_container = QFrame()
        self._mistake_container.setObjectName("card")
        layout = QVBoxLayout(self._mistake_container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        header = QLabel("What went wrong?")
        header.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        layout.addWidget(header)

        hint = QLabel(
            "Optional \u2014 one tap records the cause in your mistake journal. "
            "Skip it and the mistake is still logged."
        )
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        chips = QHBoxLayout()
        chips.setSpacing(8)
        for code in MISTAKE_CAUSES:
            label = CAUSE_LABELS.get(code, code)
            chip = ChipButton(
                label,
                accessible_name=f"Cause of mistake: {label}",
                tooltip=f"Record \u201c{label}\u201d as the cause (click again to clear)",
                parent=self._mistake_container,
            )
            chip.clicked.connect(lambda _checked, c=code: self._on_cause_clicked(c))
            self._cause_buttons[code] = chip
            chips.addWidget(chip)
        chips.addStretch()
        layout.addLayout(chips)

        self._note_edit = QLineEdit()
        self._note_edit.setMaxLength(NOTE_MAX_CHARS)
        self._note_edit.setPlaceholderText(
            "Add a one-line note (optional) \u2014 press Enter to save"
        )
        self._note_edit.setAccessibleName("Note about this mistake")
        self._note_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._note_edit.setStyleSheet(
            f"QLineEdit {{ background: {theme.SURFACE2}; color: {theme.TEXT};"
            f" border: 1px solid {theme.BORDER}; border-radius: 6px;"
            "  padding: 6px 10px; font-size: 13px; }"
            f"QLineEdit:focus {{ border: 2px solid {theme.ACCENT}; padding: 5px 9px; }}"
        )
        self._note_edit.editingFinished.connect(self._on_note_committed)
        layout.addWidget(self._note_edit)

        self._mistake_container.hide()
        return self._mistake_container

    # ── Errata ────────────────────────────────────────────────────────────────

    def set_item(self, item_id: str, item_text: str = "") -> None:
        """Point the errata button at the question currently on screen."""
        self._errata_btn.set_item(str(item_id or ""), str(item_text or ""))

    def errata_item(self) -> tuple[str, str]:
        """The (id, text) the errata report would carry — for tests and callers."""
        return (self._errata_btn._item_id, self._errata_btn._item_text)

    def _on_errata_reported(self, url: str) -> None:
        """Hand the URL to the system browser; degrade if there is not one.

        ``QDesktopServices.openUrl`` returns False on a machine with no
        browser (a bare X session, a container, a locked-down desktop).  The
        report must not be lost in that case, so the URL goes to the clipboard
        and the window says so.  Nothing here blocks or raises.
        """
        opened = False
        try:
            opened = bool(QDesktopServices.openUrl(QUrl(url)))
        except Exception:
            opened = False
        if not opened:
            try:
                clipboard = QApplication.clipboard()
                if clipboard is not None:
                    clipboard.setText(url)
            except Exception:
                pass
        self.errata_reported.emit(url, opened)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_evaluation(self, ev: Evaluation) -> None:
        self._score_bar.animate_to(ev.score)
        self._score_num.setText(f"{ev.score}/10")

        verdict_color = _verdict_color(ev.verdict)
        self._verdict_badge.setText(ev.verdict)
        self._verdict_badge.setStyleSheet(
            f"background: {verdict_color}22; color: {verdict_color};"
            "border-radius: 10px; padding: 2px 14px;"
            "font-weight: bold; font-size: 13px;"
        )

        self._feedback_browser.setPlainText(ev.feedback)
        self._model_answer_widget.setPlainText(ev.model_answer)

        self._missed_list.clear()
        if ev.key_points_missed:
            for point in ev.key_points_missed:
                self._missed_list.addItem(QListWidgetItem(f"• {point}"))
            self._missed_container.show()
        else:
            self._missed_container.hide()

        if ev.follow_up:
            self._followup_label.setText(ev.follow_up)
            self._followup_container.show()
        else:
            self._followup_container.hide()

        # A graded score below the "partially correct" threshold is a mistake.
        self.reset_mistake_row(ev.score < SCORE_PARTIAL_THRESHOLD)

    def set_flagged(self, flagged: bool) -> None:
        """Reflect the question's flagged state on the toggle button."""
        self._flagged = flagged
        if flagged:
            self._flag_btn.setText("⚑ Flagged — click to unflag")
            self._flag_btn.setStyleSheet(f"color: {theme.WARNING}; font-weight: bold;")
        else:
            self._flag_btn.setText("⚑ Flag for review")
            self._flag_btn.setStyleSheet("")
        self._flag_btn.setEnabled(True)

    def is_flagged(self) -> bool:
        return self._flagged

    # ── Mistake journal row ───────────────────────────────────────────────────

    def reset_mistake_row(self, visible: bool) -> None:
        """Clear any previous cause/note and show or hide the row."""
        self._cause = None
        self._last_note_emitted = ""
        for chip in self._cause_buttons.values():
            chip.setChecked(False)
        self._note_edit.clear()
        self._mistake_container.setVisible(bool(visible))

    def mistake_prompt_visible(self) -> bool:
        return not self._mistake_container.isHidden()

    def mistake_cause(self) -> str | None:
        return self._cause

    def mistake_note(self) -> str:
        return self._note_edit.text().strip()

    def _on_cause_clicked(self, code: str) -> None:
        """Single-select; clicking the chosen cause again clears it."""
        chosen = self._cause_buttons[code].isChecked()
        for other, chip in self._cause_buttons.items():
            if other != code:
                chip.setChecked(False)
        self._cause = code if chosen else None
        self.mistake_cause_chosen.emit(self._cause or "")

    def _on_note_committed(self) -> None:
        """editingFinished also fires on focus-out, so only emit real changes."""
        note = self.mistake_note()
        if note == self._last_note_emitted:
            return
        self._last_note_emitted = note
        self.mistake_note_committed.emit(note)


def _verdict_color(verdict: str) -> str:
    if verdict == "Correct":
        return theme.SUCCESS
    if verdict == "Partially correct":
        return theme.PARTIAL
    return theme.ERROR
