"""Problem screen — long-form multi-part problem with per-part grading."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QPlainTextEdit, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import Problem, Part, PartState, GradeResult, problem_score
from ui import theme
from ui.theme import FLAG_ON_TEXT, FLAG_OFF_TEXT
from ui.widgets.loading_overlay import LoadingOverlay
from ui.widgets.collapsible import CollapsibleSection
from ui.widgets.study_journal import ConfidenceStrip, MistakeRow, safe
import persistence

# A part counts as a mistake when it earns less than half its points; part
# scores are on a 0-10 scale, so half credit is 5.
MISTAKE_SCORE_THRESHOLD = 5


def part_item_id(problem, part) -> str:
    """Stable mistake-journal id for one part of one problem."""
    return f"{problem.id}:{part.part_id}" if problem is not None else str(part.part_id)


class _PartWidget(QFrame):
    """One part of a problem: prompt, answer box, grade feedback, model solution."""

    submit_requested = pyqtSignal(object)     # PartState

    def __init__(self, state: PartState, problem: Problem | None = None,
                 ask_confidence: bool = True, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.problem = problem
        self.setObjectName("card")
        part = state.part
        self.item_id = part_item_id(problem, part)
        self.category = problem.topic if problem is not None else ""
        self._pending_confidence: int | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        head = QHBoxLayout()
        lbl = QLabel(f"({part.part_id})")
        lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {theme.ACCENT};")
        head.addWidget(lbl)
        pts = QLabel(f"{part.points} pts")
        pts.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        head.addWidget(pts)
        head.addStretch()
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        head.addWidget(self._status_lbl)
        root.addLayout(head)

        prompt = QLabel(part.prompt)
        prompt.setWordWrap(True)
        prompt.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        prompt.setStyleSheet(f"font-size: 14px; color: {theme.TEXT};")
        root.addWidget(prompt)

        self._answer_edit = QPlainTextEdit()
        self._answer_edit.setPlaceholderText(
            "Write your solution — plain text with unicode or backtick math, "
            "e.g. |ψ⟩ = α|0⟩ + β|1⟩ or `H = (X+Z)/sqrt2` …"
        )
        self._answer_edit.setMinimumHeight(110)
        self._answer_edit.textChanged.connect(self._validate)
        root.addWidget(self._answer_edit)

        # Confidence strip — asked BEFORE grading so it can never be hindsight.
        self._conf_strip = ConfidenceStrip()
        self._conf_strip.setVisible(ask_confidence)
        root.addWidget(self._conf_strip)

        btn_row = QHBoxLayout()
        self._submit_btn = QPushButton("Submit for grading")
        self._submit_btn.setEnabled(False)
        self._submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(self._submit_btn)
        self._reveal_btn = QPushButton("Show model solution")
        self._reveal_btn.setObjectName("flat")
        self._reveal_btn.clicked.connect(self._on_reveal)
        btn_row.addWidget(self._reveal_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        # Feedback section (filled after grading)
        self._feedback_body = QLabel("")
        self._feedback_body.setWordWrap(True)
        self._feedback_body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._feedback_body.setStyleSheet(f"font-size: 13px; color: {theme.TEXT};")
        self._feedback_section = CollapsibleSection(
            "Feedback", self._feedback_body, expanded=True)
        self._feedback_section.hide()
        root.addWidget(self._feedback_section)

        # Mistake journal — compact, skippable, part of the feedback view.
        self._mistake_row = MistakeRow()
        self._mistake_row.hide()
        self._mistake_row.cause_chosen.connect(self._on_cause_chosen)
        self._mistake_row.note_changed.connect(self._on_note_changed)
        root.addWidget(self._mistake_row)

        # Model solution section (offline fallback — always available)
        sol_lbl = QLabel(part.model_solution)
        sol_lbl.setWordWrap(True)
        sol_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        sol_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT};")
        self._solution_section = CollapsibleSection(
            "Model solution", sol_lbl, expanded=True, accent=theme.WARNING)
        self._solution_section.hide()
        root.addWidget(self._solution_section)

    # ------------------------------------------------------------------

    def _validate(self) -> None:
        has_text = bool(self._answer_edit.toPlainText().strip())
        self._submit_btn.setEnabled(has_text and not self._busy())

    def _busy(self) -> bool:
        return self._submit_btn.text() == "Grading…"

    def _on_submit(self) -> None:
        self.state.answer = self._answer_edit.toPlainText().strip()
        if not self.state.answer:
            return
        self.state.tries += 1
        # Snapshot the rating now: the result is not visible yet.
        self._pending_confidence = self._conf_strip.value()
        self.submit_requested.emit(self.state)

    def _on_reveal(self) -> None:
        self.state.solution_revealed = True
        self._solution_section.show()
        self._solution_section.set_expanded(True)
        self._reveal_btn.setEnabled(False)

    def set_grading(self, grading: bool) -> None:
        if grading:
            self._submit_btn.setText("Grading…")
            self._submit_btn.setEnabled(False)
        else:
            label = "Resubmit revision" if self.state.result else "Submit for grading"
            self._submit_btn.setText(label)
            self._validate()

    def show_result(self, result: GradeResult) -> None:
        self.state.result = result
        self.set_grading(False)
        self._submit_btn.setText("Resubmit revision")

        score = result.score
        color = (theme.SUCCESS if score >= 7 else
                 theme.PARTIAL if score >= 4 else theme.ERROR)
        tries = self.state.tries
        self._status_lbl.setText(f"Score {score}/10 · attempt {tries}")
        self._status_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {color};")

        text = result.feedback or "(no feedback)"
        if result.missed_points:
            missed = "\n".join(f"  • {m}" for m in result.missed_points)
            text += f"\n\nMissed points:\n{missed}"
        text += "\n\nYou may revise your answer above and resubmit."
        self._feedback_body.setText(text)
        self._feedback_section.set_title(f"Feedback — {score}/10")
        self._feedback_section.show()
        self._feedback_section.set_expanded(True)
        self._record_outcome(score)

    # -- study journal ---------------------------------------------------

    def _record_outcome(self, score: int) -> None:
        """Pair the pre-answer confidence with the grade; log/resolve a mistake."""
        correct = score >= MISTAKE_SCORE_THRESHOLD

        level, self._pending_confidence = self._pending_confidence, None
        if level:
            safe(persistence.log_confidence, self.item_id, self.category,
                 level, correct)
            self._conf_strip.clear()      # a resubmission needs a fresh rating

        if correct:
            safe(persistence.resolve_mistake, self.item_id)
            self._mistake_row.hide()
            return

        safe(persistence.log_mistake,
             self.item_id, self.category, self.state.part.prompt,
             self.state.answer, self.state.part.model_solution)
        stored = safe(persistence.find_mistake, self.item_id) or {}
        self._mistake_row.set_context(
            f"Scored {score}/10 — what went wrong?")
        self._mistake_row.reset(stored.get("cause"), stored.get("note", ""))
        self._mistake_row.show()

    def _on_cause_chosen(self, cause: str) -> None:
        safe(persistence.set_mistake_cause, self.item_id, cause,
             self._mistake_row.note())

    def _on_note_changed(self, note: str) -> None:
        safe(persistence.set_mistake_cause, self.item_id,
             self._mistake_row.value(), note)

    def set_confidence_enabled(self, enabled: bool) -> None:
        self._conf_strip.setVisible(enabled)
        if not enabled:
            self._conf_strip.clear()
            self._pending_confidence = None

    def show_error(self, err: str) -> None:
        self.state.tries = max(0, self.state.tries - 1)   # failed try doesn't count
        self._pending_confidence = None                   # nothing graded: log nothing
        self.set_grading(False)
        self._feedback_body.setText(
            f"Grading failed: {err}\n\n"
            "Check your API key (ANTHROPIC_API_KEY or "
            "~/.config/quantum-study/api_key.txt) and try again — or use "
            "“Show model solution” to self-check offline."
        )
        self._feedback_section.set_title("Feedback — error")
        self._feedback_section.show()
        self._feedback_section.set_expanded(True)


class ProblemScreen(QWidget):
    part_submitted      = pyqtSignal(object, object, str, int)  # problem, part, answer, tries
    problem_finished    = pyqtSignal(object, list)              # problem, [PartState]
    session_ended       = pyqtSignal()
    flag_requested      = pyqtSignal()                          # toggle review flag on this problem
    reference_requested = pyqtSignal(str)                       # open docs for this topic

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._problem: Problem | None = None
        self._part_widgets: dict[str, _PartWidget] = {}
        self._states: list[PartState] = []
        self._overlay = LoadingOverlay(self)
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
        self._root = QVBoxLayout(content)
        self._root.setContentsMargins(48, 28, 48, 24)
        self._root.setSpacing(16)
        scroll.setWidget(content)

        top_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        top_row.addWidget(self._progress_lbl)
        top_row.addStretch()
        ref_btn = QPushButton("📖 Reference")
        ref_btn.setObjectName("flat")
        ref_btn.setToolTip("Browse the docs chapter for this topic (your work is kept)")
        ref_btn.clicked.connect(self._on_reference)
        top_row.addWidget(ref_btn)
        self._topic_lbl = QLabel("")
        top_row.addWidget(self._topic_lbl)
        self._root.addLayout(top_row)

        self._title_lbl = QLabel("")
        self._title_lbl.setObjectName("heading")
        self._title_lbl.setWordWrap(True)
        self._root.addWidget(self._title_lbl)

        stmt_frame = QFrame(); stmt_frame.setObjectName("card")
        stmt_layout = QVBoxLayout(stmt_frame)
        stmt_layout.setContentsMargins(20, 16, 20, 16)
        self._statement_lbl = QLabel("")
        self._statement_lbl.setWordWrap(True)
        self._statement_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._statement_lbl.setStyleSheet(f"font-size: 14px; color: {theme.TEXT};")
        stmt_layout.addWidget(self._statement_lbl)
        self._root.addWidget(stmt_frame)

        self._parts_container = QVBoxLayout()
        self._parts_container.setSpacing(14)
        self._root.addLayout(self._parts_container)
        self._root.addStretch()

        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(48, 12, 48, 12)
        quit_btn = QPushButton("End Session")
        quit_btn.setObjectName("flat")
        quit_btn.clicked.connect(self.session_ended)
        bl.addWidget(quit_btn)
        self._score_lbl = QLabel("")
        self._score_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        bl.addWidget(self._score_lbl)
        bl.addStretch()
        self._flag_btn = QPushButton(FLAG_OFF_TEXT)
        self._flag_btn.setObjectName("flag")
        self._flag_btn.setCheckable(True)
        self._flag_btn.setToolTip("Toggle: mark this problem for later review")
        self._flag_btn.clicked.connect(self.flag_requested)
        bl.addWidget(self._flag_btn)
        self._finish_btn = QPushButton("Finish Problem →")
        self._finish_btn.setObjectName("accent")
        self._finish_btn.clicked.connect(self._on_finish)
        bl.addWidget(self._finish_btn)
        outer.addWidget(bar)

    # ------------------------------------------------------------------

    def show_problem(self, problem: Problem, idx: int, total: int) -> None:
        self._problem = problem
        self._states = [PartState(part=p) for p in problem.parts]
        self.set_flagged(False)
        self._progress_lbl.setText(f"Problem {idx} of {total}")
        self._title_lbl.setText(problem.title)
        self._statement_lbl.setText(problem.statement)

        color = theme.TOPIC_COLORS.get(problem.topic, theme.ACCENT)
        self._topic_lbl.setText(problem.topic.upper())
        self._topic_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {color};")

        while self._parts_container.count():
            item = self._parts_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._part_widgets.clear()

        ask = safe(persistence.confidence_prompt_enabled)
        ask = True if ask is None else bool(ask)
        for st in self._states:
            w = _PartWidget(st, problem, ask_confidence=ask)
            w.submit_requested.connect(self._on_part_submit)
            w._conf_strip.opt_out_requested.connect(self._on_confidence_opt_out)
            self._part_widgets[st.part.part_id] = w
            self._parts_container.addWidget(w)
        self._update_score_label()

    def _on_confidence_opt_out(self) -> None:
        """“Don't ask” — persist the opt-out and hide every strip on screen."""
        safe(persistence.set_confidence_prompt_enabled, False)
        for w in self._part_widgets.values():
            w.set_confidence_enabled(False)

    def _on_part_submit(self, state: PartState) -> None:
        w = self._part_widgets.get(state.part.part_id)
        if w:
            w.set_grading(True)
        self.part_submitted.emit(self._problem, state.part, state.answer, state.tries)

    def on_part_graded(self, part_id: str, result: GradeResult) -> None:
        w = self._part_widgets.get(part_id)
        if w:
            w.show_result(result)
        self._update_score_label()

    def on_part_failed(self, part_id: str, err: str) -> None:
        w = self._part_widgets.get(part_id)
        if w:
            w.show_error(err)

    def _update_score_label(self) -> None:
        if not self._states:
            self._score_lbl.setText("")
            return
        graded = [s for s in self._states if s.result is not None]
        if graded:
            score = problem_score(self._states)
            self._score_lbl.setText(
                f"Graded {len(graded)}/{len(self._states)} parts · "
                f"problem score so far {score:.1f}/10")
        else:
            self._score_lbl.setText(f"{len(self._states)} parts · none graded yet")

    def _on_finish(self) -> None:
        if self._problem is not None:
            self.problem_finished.emit(self._problem, self._states)

    def _on_reference(self) -> None:
        self.reference_requested.emit(self._problem.topic if self._problem else "")

    # -- flag for review -------------------------------------------------

    def set_flagged(self, flagged: bool) -> None:
        """Reflect the persisted flag state on the toggle button."""
        self._flag_btn.setChecked(flagged)
        self._flag_btn.setText(FLAG_ON_TEXT if flagged else FLAG_OFF_TEXT)

    def is_flagged_shown(self) -> bool:
        return self._flag_btn.isChecked()

    def resizeEvent(self, event) -> None:
        self._overlay.resize(self.size())
        super().resizeEvent(event)
