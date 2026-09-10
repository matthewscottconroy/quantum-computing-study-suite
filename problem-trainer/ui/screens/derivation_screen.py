"""Derivation screen — Socratic step-by-step guided derivation."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QPlainTextEdit, QScrollArea, QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from config import MAX_STEP_TRIES
from core.models import Derivation, Step, StepState, StepCheck
from ui import theme
from ui.theme import FLAG_ON_TEXT, FLAG_OFF_TEXT
from ui.widgets.collapsible import CollapsibleSection


class DerivationScreen(QWidget):
    step_submitted      = pyqtSignal(object, object, str, list, int)  # derivation, step, answer, accepted_steps, tries
    derivation_finished = pyqtSignal(object, list)                    # derivation, [StepState]
    session_ended       = pyqtSignal()
    flag_requested      = pyqtSignal()                                # toggle review flag on this derivation
    reference_requested = pyqtSignal(str)                             # open docs for this derivation id

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._derivation: Derivation | None = None
        self._states: list[StepState] = []
        self._idx = 0
        self._checking = False
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll, 1)

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(48, 28, 48, 24)
        root.setSpacing(14)
        scroll.setWidget(content)

        top_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        top_row.addWidget(self._progress_lbl)
        top_row.addStretch()
        ref_btn = QPushButton("📖 Reference")
        ref_btn.setObjectName("flat")
        ref_btn.setToolTip("Browse the docs chapter behind this derivation (your progress is kept)")
        ref_btn.clicked.connect(self._on_reference)
        top_row.addWidget(ref_btn)
        badge = QLabel("GUIDED DERIVATION")
        badge.setStyleSheet(
            f"font-size: 11px; font-weight: bold; "
            f"color: {theme.TOPIC_COLORS.get('Derivation', theme.WARNING)};")
        top_row.addWidget(badge)
        root.addLayout(top_row)

        self._title_lbl = QLabel("")
        self._title_lbl.setObjectName("heading")
        self._title_lbl.setWordWrap(True)
        root.addWidget(self._title_lbl)

        self._goal_lbl = QLabel("")
        self._goal_lbl.setObjectName("subheading")
        self._goal_lbl.setWordWrap(True)
        root.addWidget(self._goal_lbl)

        self._bar = QProgressBar()
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(8)
        root.addWidget(self._bar)
        self._bar_lbl = QLabel("")
        self._bar_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        root.addWidget(self._bar_lbl)

        # Transcript of accepted steps (collapsible entries)
        self._transcript = QVBoxLayout()
        self._transcript.setSpacing(8)
        root.addLayout(self._transcript)

        # Current step card
        self._step_frame = QFrame(); self._step_frame.setObjectName("card")
        sf = QVBoxLayout(self._step_frame)
        sf.setContentsMargins(20, 16, 20, 16)
        sf.setSpacing(10)

        self._step_lbl = QLabel("")
        self._step_lbl.setWordWrap(True)
        self._step_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._step_lbl.setStyleSheet(f"font-size: 15px; color: {theme.TEXT};")
        sf.addWidget(self._step_lbl)

        self._nudge_lbl = QLabel("")
        self._nudge_lbl.setWordWrap(True)
        self._nudge_lbl.hide()
        sf.addWidget(self._nudge_lbl)

        self._hint_lbl = QLabel("")
        self._hint_lbl.setWordWrap(True)
        self._hint_lbl.setStyleSheet(f"font-size: 13px; color: {theme.WARNING};")
        self._hint_lbl.hide()
        sf.addWidget(self._hint_lbl)

        self._answer_edit = QPlainTextEdit()
        self._answer_edit.setPlaceholderText(
            "Your step — plain text with unicode/backtick math…")
        self._answer_edit.setMinimumHeight(90)
        self._answer_edit.textChanged.connect(self._validate)
        sf.addWidget(self._answer_edit)

        btns = QHBoxLayout()
        self._check_btn = QPushButton("Check step")
        self._check_btn.setObjectName("accent")
        self._check_btn.setEnabled(False)
        self._check_btn.clicked.connect(self._on_check)
        btns.addWidget(self._check_btn)
        self._hint_btn = QPushButton("Hint")
        self._hint_btn.clicked.connect(self._on_hint)
        btns.addWidget(self._hint_btn)
        self._reveal_btn = QPushButton("Show model step && continue")
        self._reveal_btn.setObjectName("flat")
        self._reveal_btn.clicked.connect(self._on_reveal)
        btns.addWidget(self._reveal_btn)
        btns.addStretch()
        sf.addLayout(btns)
        root.addWidget(self._step_frame)
        root.addStretch()

        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(48, 12, 48, 12)
        quit_btn = QPushButton("End Session")
        quit_btn.setObjectName("flat")
        quit_btn.clicked.connect(self.session_ended)
        bl.addWidget(quit_btn)
        bl.addStretch()
        self._flag_btn = QPushButton(FLAG_OFF_TEXT)
        self._flag_btn.setObjectName("flag")
        self._flag_btn.setCheckable(True)
        self._flag_btn.setToolTip("Toggle: mark this derivation for later review")
        self._flag_btn.clicked.connect(self.flag_requested)
        bl.addWidget(self._flag_btn)
        self._finish_btn = QPushButton("Finish Derivation →")
        self._finish_btn.setObjectName("accent")
        self._finish_btn.clicked.connect(self._on_finish)
        self._finish_btn.hide()
        bl.addWidget(self._finish_btn)
        outer.addWidget(bar)

    # ------------------------------------------------------------------

    def show_derivation(self, derivation: Derivation, idx: int, total: int) -> None:
        self._derivation = derivation
        self._states = [StepState(step=s) for s in derivation.steps]
        self._idx = 0
        self._checking = False
        self.set_flagged(False)
        self._progress_lbl.setText(f"Derivation {idx} of {total}")
        self._title_lbl.setText(derivation.title)
        self._goal_lbl.setText(f"Goal: {derivation.goal}")
        self._bar.setRange(0, len(derivation.steps))
        while self._transcript.count():
            item = self._transcript.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._finish_btn.hide()
        self._step_frame.show()
        self._show_current_step()

    def _current(self) -> StepState | None:
        if self._derivation and self._idx < len(self._states):
            return self._states[self._idx]
        return None

    def _show_current_step(self) -> None:
        st = self._current()
        self._bar.setValue(self._idx)
        self._bar_lbl.setText(
            f"Step {min(self._idx + 1, len(self._states))} of {len(self._states)}")
        if st is None:
            self._complete()
            return
        self._step_lbl.setText(f"Step {self._idx + 1}:  {st.step.prompt}")
        self._nudge_lbl.hide()
        self._hint_lbl.hide()
        self._answer_edit.clear()
        self._answer_edit.setEnabled(True)
        self._hint_btn.setVisible(bool(st.step.hint))
        self._hint_btn.setText("Hint")
        # Model step reveal is always available (offline fallback); before
        # MAX_STEP_TRIES failed tries it is presented low-key.
        self._reveal_btn.show()
        self._validate()

    def _validate(self) -> None:
        st = self._current()
        ok = bool(st) and bool(self._answer_edit.toPlainText().strip()) and not self._checking
        self._check_btn.setEnabled(ok)
        self._check_btn.setText("Checking…" if self._checking else "Check step")

    def _on_hint(self) -> None:
        st = self._current()
        if st and st.step.hint:
            self._hint_lbl.setText(f"Hint: {st.step.hint}")
            self._hint_lbl.show()

    def _on_check(self) -> None:
        st = self._current()
        if not st or self._checking:
            return
        st.answer = self._answer_edit.toPlainText().strip()
        if not st.answer:
            return
        st.tries += 1
        self._checking = True
        self._validate()
        accepted = [s.step for s in self._states[:self._idx]]
        self.step_submitted.emit(self._derivation, st.step, st.answer, accepted, st.tries)

    def on_step_checked(self, step_id: str, check: StepCheck) -> None:
        st = self._current()
        self._checking = False
        if not st or st.step.step_id != step_id:
            self._validate()
            return
        if check.accepted:
            st.accepted = True
            note = check.nudge or "Accepted."
            self._append_transcript(st, note)
            self._idx += 1
            self._show_current_step()
        else:
            self._nudge_lbl.setText(
                f"Not quite ({st.tries} "
                f"{'try' if st.tries == 1 else 'tries'}): {check.nudge or 'Revise and try again.'}")
            self._nudge_lbl.setStyleSheet(
                f"font-size: 13px; color: {theme.PARTIAL}; font-weight: bold;")
            self._nudge_lbl.show()
            if st.tries >= MAX_STEP_TRIES:
                self._reveal_btn.show()
                self._nudge_lbl.setText(
                    self._nudge_lbl.text()
                    + "  —  You can show the model step and continue.")
            self._validate()

    def on_step_failed(self, step_id: str, err: str) -> None:
        st = self._current()
        self._checking = False
        if st:
            st.tries = max(0, st.tries - 1)   # failed call doesn't count as a try
        self._nudge_lbl.setText(
            f"Step check failed: {err}\nCheck your API key — or use "
            "“Show model step && continue” to keep working offline.")
        self._nudge_lbl.setStyleSheet(f"font-size: 13px; color: {theme.ERROR};")
        self._nudge_lbl.show()
        self._validate()

    def _on_reveal(self) -> None:
        st = self._current()
        if not st:
            return
        st.model_revealed = True
        st.accepted = True
        self._append_transcript(st, "(model step revealed)")
        self._idx += 1
        self._show_current_step()

    def _append_transcript(self, st: StepState, note: str) -> None:
        body = QLabel(
            (f"Your answer:\n{st.answer}\n\n" if st.answer and not st.model_revealed else "")
            + f"Model step:\n{st.step.model_step}"
        )
        body.setWordWrap(True)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        body.setStyleSheet(f"font-size: 13px; color: {theme.TEXT};")
        n = self._transcript.count() + 1
        clean = st.accepted and not st.model_revealed
        mark = "✓" if clean else "◦"
        accent = theme.SUCCESS if clean else theme.WARNING
        section = CollapsibleSection(
            f"{mark} Step {n} — {note}", body, expanded=False, accent=accent)
        self._transcript.addWidget(section)

    def _complete(self) -> None:
        self._bar.setValue(len(self._states))
        self._step_frame.hide()
        self._finish_btn.show()
        clean = sum(1 for s in self._states if s.accepted and not s.model_revealed)
        self._bar_lbl.setText(
            f"Derivation complete — {clean}/{len(self._states)} steps solved "
            "without the model step.")

    def _on_finish(self) -> None:
        if self._derivation is not None:
            self.derivation_finished.emit(self._derivation, self._states)

    def _on_reference(self) -> None:
        self.reference_requested.emit(self._derivation.id if self._derivation else "")

    # -- flag for review -------------------------------------------------

    def set_flagged(self, flagged: bool) -> None:
        """Reflect the persisted flag state on the toggle button."""
        self._flag_btn.setChecked(flagged)
        self._flag_btn.setText(FLAG_ON_TEXT if flagged else FLAG_OFF_TEXT)

    def is_flagged_shown(self) -> bool:
        return self._flag_btn.isChecked()
