"""Question screen — shows one question at a time, takes free-text answer,
and asks for an optional pre-answer confidence rating."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import Question, DrillConfig, QuestionAttempt
from ui import theme
from ui.widgets.loading_overlay import LoadingOverlay

# 1 = guessing … 4 = certain.  Rated *before* Submit so the number cannot be
# hindsight; paired with the grade in confidence.json.
CONFIDENCE_LEVELS = {1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}


class QuestionScreen(QWidget):
    answer_submitted  = pyqtSignal(object)   # QuestionAttempt (no evaluation yet)
    session_cancelled = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._questions: list[Question] = []
        self._idx = 0
        self._paper_text = ""
        self._confidence: int | None = None
        self._conf_buttons: dict[int, QPushButton] = {}
        self._overlay = LoadingOverlay(self)
        self._build_ui()
        self._refresh_confidence_visibility()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 24)
        root.setSpacing(16)

        prog_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        prog_row.addWidget(self._progress_lbl)
        prog_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("flat")
        cancel_btn.clicked.connect(self.session_cancelled)
        prog_row.addWidget(cancel_btn)
        root.addLayout(prog_row)

        self._qtype_lbl = QLabel("")
        self._qtype_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        root.addWidget(self._qtype_lbl)

        q_frame = QFrame(); q_frame.setObjectName("card")
        q_layout = QVBoxLayout(q_frame)
        q_layout.setContentsMargins(24, 20, 24, 20)
        self._question_lbl = QLabel("")
        self._question_lbl.setWordWrap(True)
        self._question_lbl.setStyleSheet(f"font-size: 16px; color: {theme.TEXT};")
        q_layout.addWidget(self._question_lbl)
        root.addWidget(q_frame)

        ans_lbl = QLabel("Your answer:")
        ans_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        root.addWidget(ans_lbl)

        self._answer_edit = QPlainTextEdit()
        self._answer_edit.setPlaceholderText("Write your answer here…")
        self._answer_edit.textChanged.connect(self._validate)
        root.addWidget(self._answer_edit, 1)

        self._conf_strip = self._build_confidence_strip()
        root.addWidget(self._conf_strip)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        self._submit_btn = QPushButton("Submit Answer")
        self._submit_btn.setObjectName("accent")
        self._submit_btn.setEnabled(False)
        self._submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(self._submit_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Confidence strip (optional, shown before the answer is submitted)
    # ------------------------------------------------------------------

    def _build_confidence_strip(self) -> QWidget:
        """Four skippable self-rating buttons plus a permanent opt-out.

        Keyboard-reachable (Tab order, StrongFocus), each button carries an
        accessible name, the chosen level is marked with a ✓ glyph as well as
        a border so the state never rests on colour alone, and the focus ring
        is a dashed accent border that stays visible on the chosen button.
        """
        strip = QWidget()
        strip.setObjectName("confidenceStrip")
        strip.setStyleSheet(
            f"QWidget#confidenceStrip {{ background: transparent; }}"
            f"QPushButton {{ padding: 5px 12px; font-size: 12px; }}"
            f"QPushButton[chosen=\"yes\"] {{ border: 2px solid {theme.ACCENT};"
            f" color: {theme.TEXT}; font-weight: bold; background: {theme.SURFACE2}; }}"
            f"QPushButton:focus {{ border: 2px dashed {theme.ACCENT}; }}"
        )
        row = QHBoxLayout(strip)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        prompt = QLabel("How sure are you?")
        prompt.setStyleSheet(f"font-size: 12px; color: {theme.TEXT};")
        row.addWidget(prompt)
        hint = QLabel("(optional)")
        hint.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        row.addWidget(hint)

        for level, label in CONFIDENCE_LEVELS.items():
            btn = QPushButton(label)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setAccessibleName(f"Confidence {level} of 4: {label}")
            btn.setAccessibleDescription(
                "Optional — rate how sure you are before submitting this answer"
            )
            btn.setToolTip(f"{level} — {label}")
            btn.clicked.connect(lambda _checked=False, lv=level: self._on_confidence(lv))
            self._conf_buttons[level] = btn
            row.addWidget(btn)

        row.addStretch()
        self._conf_optout_btn = QPushButton("Don't ask again")
        self._conf_optout_btn.setObjectName("flat")
        self._conf_optout_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._conf_optout_btn.setAccessibleName("Stop asking for confidence ratings")
        self._conf_optout_btn.setToolTip(
            "Hide the confidence strip for good (paper_settings.json)"
        )
        self._conf_optout_btn.clicked.connect(self._on_confidence_optout)
        row.addWidget(self._conf_optout_btn)
        return strip

    def confidence(self) -> int | None:
        """Chosen rating for the current question, or None if not rated."""
        return self._confidence

    def confidence_enabled(self) -> bool:
        """Whether the strip is being shown (the learner can opt out for good)."""
        return not self._conf_strip.isHidden()

    def _on_confidence(self, level: int) -> None:
        # Clicking the chosen level again clears it — the rating stays optional.
        self._confidence = None if self._confidence == level else level
        self._paint_confidence()

    def _paint_confidence(self) -> None:
        for level, btn in self._conf_buttons.items():
            chosen = (level == self._confidence)
            btn.setText(f"✓ {CONFIDENCE_LEVELS[level]}" if chosen
                        else CONFIDENCE_LEVELS[level])
            btn.setProperty("chosen", "yes" if chosen else "no")
            btn.setAccessibleDescription(
                "Selected" if chosen
                else "Optional — rate how sure you are before submitting this answer"
            )
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _clear_confidence(self) -> None:
        self._confidence = None
        self._paint_confidence()

    def _refresh_confidence_visibility(self) -> None:
        """Honour the saved opt-out (a bad settings file just leaves it on)."""
        try:
            from persistence import confidence_prompt_enabled
            enabled = confidence_prompt_enabled()
        except Exception:
            enabled = True
        self._conf_strip.setVisible(enabled)

    def _on_confidence_optout(self) -> None:
        try:
            from persistence import set_confidence_prompt_enabled
            set_confidence_prompt_enabled(False)
        except Exception:
            pass
        self._clear_confidence()
        self._conf_strip.hide()

    # ------------------------------------------------------------------

    def start(self, questions: list[Question], paper_text: str) -> None:
        self._questions  = questions
        self._idx        = 0
        self._paper_text = paper_text
        self._refresh_confidence_visibility()
        self._show_question()

    def show_current(self) -> None:
        self._show_question()

    def advance(self) -> None:
        """Move on to the next question.

        Called by the controller only after the current question has been
        graded (or explicitly skipped).  Submitting does *not* advance, so a
        failed grade leaves the same question — and the typed answer — in
        place for a retry.
        """
        if self._idx < len(self._questions):
            self._idx += 1

    def current_index(self) -> int:
        """Zero-based index of the question currently shown."""
        return self._idx

    def has_current(self) -> bool:
        """False once every question has been graded (nothing left to show)."""
        return self._idx < len(self._questions)

    def _show_question(self) -> None:
        if not self.has_current():
            self._submit_btn.setEnabled(False)
            return
        q = self._questions[self._idx]
        self._progress_lbl.setText(f"Question {self._idx + 1} of {len(self._questions)}")
        color = theme.QTYPE_COLORS.get(q.q_type, theme.ACCENT)
        self._qtype_lbl.setText(q.q_type.upper())
        self._qtype_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color};")
        self._question_lbl.setText(q.text)
        self._answer_edit.clear()
        self._clear_confidence()
        self._submit_btn.setEnabled(False)

    def _validate(self) -> None:
        self._submit_btn.setEnabled(bool(self._answer_edit.toPlainText().strip()))

    def _on_submit(self) -> None:
        if not self.has_current():
            self._submit_btn.setEnabled(False)
            return
        q = self._questions[self._idx]
        attempt = QuestionAttempt(
            question=q,
            answer_text=self._answer_edit.toPlainText().strip(),
            confidence=self._confidence,
        )
        # The index is advanced by the controller (advance()) only once this
        # attempt has been graded or skipped — see MainWindow._on_grade_failed.
        self.answer_submitted.emit(attempt)

    def show_grading(self) -> None:
        self._overlay.show_with_message("Grading…")

    def hide_grading(self) -> None:
        self._overlay.hide()

    def resizeEvent(self, event) -> None:
        self._overlay.resize(self.size())
        super().resizeEvent(event)
