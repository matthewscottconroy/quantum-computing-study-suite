"""Decoder Game screen — rounds of syndrome decoding with score and streaks.

Difficulty ladder: rep-3 → rep-5 → surface-d3 weight-1 → surface-d3 weight-2.
Repetition-code rounds are multiple choice; surface-code rounds render the
3×3 data-qubit grid with fired checks and let the user click qubits to place
an X/Z/Y correction. Success is verified by GF(2)/symplectic computation in
core.decoder_game (correction must equal the error up to a stabilizer).
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QButtonGroup, QRadioButton, QStackedWidget, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QElapsedTimer

from core.decoder_game import (
    LEVELS, LEVEL_TITLES, LEVEL_DIFFICULTY, Round, generate_round,
    pauli_label, pauli_xor, SURFACE_X_CHECKS, SURFACE_Z_CHECKS,
)
from core.models import Problem, Attempt, Verdict, GradeMode, SessionStats
from ui import theme
from ui.widgets.confidence_strip import ConfidenceStrip
from ui.widgets.mistake_row import MistakeRow

ROUNDS_PER_LEVEL = 3
DECODER_CATEGORY = "Decoder Game"

X_COLOR = "#388bfd"   # X-type checks (blue)
Z_COLOR = "#2da44e"   # Z-type checks (green)

_PAGE_PLAY = 0
_PAGE_END = 1


class DecoderScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._round: Round | None = None
        self._round_idx = 0
        self._plan: list[str] = []
        self._score = 0
        self._streak = 0
        self._best_streak = 0
        self._results: list[tuple[str, bool, int]] = []   # (level, success, secs)
        self._timer = QElapsedTimer()
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._pages = QStackedWidget()
        outer.addWidget(self._pages)
        self._pages.addWidget(self._build_play_page())   # 0
        self._pages.addWidget(self._build_end_page())    # 1

    def _build_play_page(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(48, 28, 48, 20)
        root.setSpacing(14)

        top = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        top.addWidget(self._progress_lbl)
        self._streak_lbl = QLabel("")
        self._streak_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {theme.WARNING};")
        top.addWidget(self._streak_lbl)
        top.addStretch()
        self._score_lbl = QLabel("")
        self._score_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {theme.ACCENT};")
        top.addWidget(self._score_lbl)
        root.addLayout(top)

        self._level_lbl = QLabel("")
        self._level_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.WARNING};")
        root.addWidget(self._level_lbl)

        # Question card: code description + syndrome
        q_frame = QFrame(); q_frame.setObjectName("card")
        q_layout = QVBoxLayout(q_frame)
        q_layout.setContentsMargins(24, 18, 24, 18)
        self._question_lbl = QLabel("")
        self._question_lbl.setWordWrap(True)
        self._question_lbl.setStyleSheet(f"font-size: 15px; color: {theme.TEXT};")
        q_layout.addWidget(self._question_lbl)
        self._syndrome_lbl = QLabel("")
        self._syndrome_lbl.setTextFormat(Qt.TextFormat.RichText)
        self._syndrome_lbl.setWordWrap(True)
        self._syndrome_lbl.setStyleSheet(
            "font-family: 'JetBrains Mono','Fira Code',monospace; font-size: 14px;")
        q_layout.addWidget(self._syndrome_lbl)
        root.addWidget(q_frame)

        # Multiple-choice answers (repetition codes)
        self._mc_widget = QWidget()
        mc_layout = QVBoxLayout(self._mc_widget)
        mc_layout.setSpacing(8)
        mc_layout.setContentsMargins(0, 0, 0, 0)
        self._btn_group = QButtonGroup(self)
        self._btn_group.buttonClicked.connect(
            lambda _=None: self._submit_btn.setEnabled(True))
        self._radio_btns: list[QRadioButton] = []
        for i in range(4):
            rb = QRadioButton("")
            rb.setStyleSheet(f"font-size: 14px; color: {theme.TEXT};")
            rb.setAccessibleName(f"Correction choice {chr(65 + i)}")
            self._btn_group.addButton(rb, i)
            self._radio_btns.append(rb)
            mc_layout.addWidget(rb)
        root.addWidget(self._mc_widget)

        # Surface-code grid (click qubits to place corrections)
        self._grid_widget = QWidget()
        grid_layout = QHBoxLayout(self._grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(24)
        self._surface_grid = _SurfaceGrid()
        self._surface_grid.correction_changed.connect(self._on_grid_changed)
        grid_layout.addWidget(self._surface_grid, 0,
                              Qt.AlignmentFlag.AlignTop)
        side = QVBoxLayout(); side.setSpacing(6)
        grid_help = QLabel(
            "Click a data qubit to cycle its correction:\n"
            "·  →  X  →  Z  →  Y  →  ·\n\n"
            "Squares are stabilizer checks. One that fired reads X− or Z− "
            "(measured −1) and is filled red; a quiet one reads X+ or Z+. "
            "Place a correction that returns the state to the codespace "
            "without applying a logical operator.")
        grid_help.setWordWrap(True)
        grid_help.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        side.addWidget(grid_help)
        self._proposed_lbl = QLabel("Proposed correction: —")
        self._proposed_lbl.setStyleSheet(
            f"font-size: 13px; color: {theme.TEXT};"
            "font-family: 'JetBrains Mono','Fira Code',monospace;")
        side.addWidget(self._proposed_lbl)
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("flat")
        clear_btn.setAccessibleName("Clear the proposed correction")
        clear_btn.clicked.connect(self._on_grid_clear)
        side.addWidget(clear_btn, 0, Qt.AlignmentFlag.AlignLeft)
        side.addStretch()
        grid_layout.addLayout(side, 1)
        root.addWidget(self._grid_widget)

        # Feedback (shown after submitting)
        self._feedback_frame = QFrame(); self._feedback_frame.setObjectName("card")
        fb_layout = QVBoxLayout(self._feedback_frame)
        fb_layout.setContentsMargins(20, 14, 20, 14)
        self._verdict_lbl = QLabel("")
        self._verdict_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        fb_layout.addWidget(self._verdict_lbl)
        self._explain_lbl = QLabel("")
        self._explain_lbl.setWordWrap(True)
        self._explain_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_MUTED};")
        fb_layout.addWidget(self._explain_lbl)
        # Mistake journal — shown only when the round failed. The mistake is
        # already logged by then, so ignoring the row loses nothing.
        self._mistake_row = MistakeRow()
        self._mistake_row.cause_chosen.connect(self._on_mistake_cause)
        self._mistake_row.note_edited.connect(self._on_mistake_note)
        self._mistake_row.hide()
        fb_layout.addWidget(self._mistake_row)
        self._feedback_frame.hide()
        root.addWidget(self._feedback_frame)

        root.addStretch()

        # Confidence calibration, asked before the correction is submitted.
        self._confidence = ConfidenceStrip()
        root.addWidget(self._confidence)

        btn_row = QHBoxLayout()
        quit_btn = QPushButton("End Game")
        quit_btn.setObjectName("flat")
        quit_btn.setAccessibleName("End the decoder game and see results")
        quit_btn.clicked.connect(self._finish)
        btn_row.addWidget(quit_btn)
        btn_row.addStretch()
        self._submit_btn = QPushButton("Submit Correction")
        self._submit_btn.setObjectName("accent")
        self._submit_btn.setAccessibleName("Submit correction")
        self._submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(self._submit_btn)
        self._next_btn = QPushButton("Next Round")
        self._next_btn.setObjectName("accent")
        self._next_btn.clicked.connect(self._advance)
        self._next_btn.hide()
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)
        return page

    def _build_end_page(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(48, 48, 48, 36)
        root.setSpacing(20)

        title = QLabel("Decoder Game Complete")
        title.setObjectName("heading")
        root.addWidget(title)
        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        self._end_score_lbl = QLabel("")
        self._end_score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._end_score_lbl.setStyleSheet(
            f"font-size: 52px; font-weight: bold; color: {theme.ACCENT};")
        root.addWidget(self._end_score_lbl)

        self._end_sub_lbl = QLabel("")
        self._end_sub_lbl.setObjectName("subheading")
        self._end_sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._end_sub_lbl)

        self._end_breakdown = QVBoxLayout(); self._end_breakdown.setSpacing(4)
        root.addLayout(self._end_breakdown)
        root.addStretch()

        btn_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        btn_row.addWidget(back_btn)
        btn_row.addStretch()
        again_btn = QPushButton("Play Again")
        again_btn.setObjectName("accent")
        again_btn.clicked.connect(self.start_game)
        btn_row.addWidget(again_btn)
        root.addLayout(btn_row)
        return page

    # ── Game flow ─────────────────────────────────────────────────────────────

    def start_game(self) -> None:
        self._plan = [lvl for lvl in LEVELS for _ in range(ROUNDS_PER_LEVEL)]
        self._round_idx = 0
        self._score = 0
        self._streak = 0
        self._best_streak = 0
        self._results = []
        self._pages.setCurrentIndex(_PAGE_PLAY)
        self._show_round()

    def _show_round(self) -> None:
        if self._round_idx >= len(self._plan):
            self._finish()
            return
        level = self._plan[self._round_idx]
        self._round = generate_round(level)
        r = self._round

        self._progress_lbl.setText(
            f"Round {self._round_idx + 1} of {len(self._plan)}")
        self._streak_lbl.setText(f"  🔥 {self._streak}" if self._streak >= 2 else "")
        self._score_lbl.setText(f"Score: {self._score}")
        self._level_lbl.setText(LEVEL_TITLES[level].upper())

        self._feedback_frame.hide()
        self._mistake_row.hide()
        self._next_btn.hide()
        self._submit_btn.show()
        self._confidence.reset()

        if r.is_grid_round:
            self._question_lbl.setText(
                f"A weight-{1 if level == 'surface1' else 2} Pauli error hit the "
                f"{r.code.name}. The checks below measured this syndrome — "
                "click data qubits to build a correction.")
            self._syndrome_lbl.setText(self._syndrome_html(r))
            self._mc_widget.hide()
            self._grid_widget.show()
            self._surface_grid.load_syndrome(r.syndrome)
            self._proposed_lbl.setText("Proposed correction: —")
            self._submit_btn.setEnabled(True)   # "no correction" is a legal guess
        else:
            self._question_lbl.setText(
                f"An X error (weight ≤ {1 if level == 'rep3' else 2}) hit the "
                f"{r.code.name}. Given the Z-stabilizer syndrome below, "
                "which correction fixes it?")
            self._syndrome_lbl.setText(self._syndrome_html(r))
            self._grid_widget.hide()
            self._mc_widget.show()
            self._btn_group.setExclusive(False)
            for i, rb in enumerate(self._radio_btns):
                rb.setChecked(False)
                if i < len(r.choices):
                    rb.setText(f"{chr(65 + i)}.  Apply {r.choices[i][0]}")
                    rb.setAccessibleName(
                        f"Correction choice {chr(65 + i)}: apply {r.choices[i][0]}")
                    rb.setEnabled(True)
                    rb.show()
                else:
                    rb.hide()
            self._btn_group.setExclusive(True)
            self._submit_btn.setEnabled(False)

        self._timer.start()

    def _syndrome_html(self, r: Round) -> str:
        parts = []
        for label, bit in zip(r.code.stabilizer_labels, r.syndrome):
            color = theme.ERROR if bit else theme.SUCCESS
            sign = "−1" if bit else "+1"
            parts.append(f'<span style="color:{color};">{label} = {sign}</span>')
        return "Syndrome:&nbsp;&nbsp;" + "&nbsp;&nbsp;&nbsp;".join(parts)

    def _on_grid_changed(self) -> None:
        if self._round is None:
            return
        corr = self._surface_grid.correction()
        self._proposed_lbl.setText(
            "Proposed correction: " + pauli_label(corr, self._round.code.n))

    def _on_grid_clear(self) -> None:
        self._surface_grid.clear_correction()
        self._on_grid_changed()

    def _on_submit(self) -> None:
        r = self._round
        if r is None:
            return
        if r.is_grid_round:
            correction = self._surface_grid.correction()
            self._surface_grid.set_locked(True)
        else:
            checked = self._btn_group.checkedId()
            if checked < 0 or checked >= len(r.choices):
                return
            correction = r.choices[checked][1]
            for rb in self._radio_btns:
                rb.setEnabled(False)

        elapsed = max(0, int(self._timer.elapsed() // 1000))
        success = r.code.is_success(r.error, correction)
        self._confidence.lock()

        if success:
            self._score += 1
            self._streak += 1
            self._best_streak = max(self._best_streak, self._streak)
        else:
            self._streak = 0
        self._results.append((r.level, success, elapsed))
        self._score_lbl.setText(f"Score: {self._score}")

        color = theme.SUCCESS if success else theme.ERROR
        self._verdict_lbl.setText("✓ Decoded!" if success else "✗ Logical error")
        self._verdict_lbl.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {color};")
        residual = pauli_xor(r.error, correction)
        detail = (
            f"Actual error: {pauli_label(r.error, r.code.n)}.   "
            f"Your correction: {pauli_label(correction, r.code.n)}.   "
            f"Residual (error ⊕ correction): {pauli_label(residual, r.code.n)}"
        )
        if success:
            detail += (" — the residual is in the stabilizer group, so the "
                       "logical state is restored.")
        else:
            detail += (" — the residual acts nontrivially on the code "
                       "(fires a check or implements a logical operator).")
        self._explain_lbl.setText(detail)
        self._feedback_frame.show()
        self._record_analytics(r, correction, success)

        self._submit_btn.hide()
        self._next_btn.setText(
            "View Results" if self._round_idx + 1 >= len(self._plan)
            else "Next Round")
        self._next_btn.show()
        self._next_btn.setFocus()

    # ── Mistake journal / confidence calibration ─────────────────────────────

    @staticmethod
    def _round_item_id(level: str) -> str:
        """Stable journal id for a decoder round: code + round type."""
        return f"decoder_{level}"

    def _record_analytics(self, r: Round, correction, success: bool) -> None:
        item_id = self._round_item_id(r.level)
        rating = self._confidence.rating()
        if rating is not None:
            try:
                from persistence import log_confidence
                log_confidence(item_id, DECODER_CATEGORY, rating, success)
            except Exception:
                pass

        if success:
            self._mistake_row.hide()
            try:
                from persistence import resolve_mistake
                resolve_mistake(item_id)
            except Exception:
                pass
            return

        logged = True
        try:
            from persistence import log_mistake, make_mistake_entry
            log_mistake(make_mistake_entry(
                item_id=item_id,
                category=DECODER_CATEGORY,
                question=(f"{LEVEL_TITLES[r.level]} — syndrome "
                          f"{''.join(str(b) for b in r.syndrome)}"),
                your_answer=pauli_label(correction, r.code.n),
                correct_answer=pauli_label(r.error, r.code.n),
            ))
        except Exception:
            logged = False
        self._mistake_row.reset(logged=logged)
        self._mistake_row.show()

    def _on_mistake_cause(self, cause: str) -> None:
        if self._round is None:
            return
        try:
            from persistence import set_mistake_cause
            set_mistake_cause(self._round_item_id(self._round.level), cause,
                              self._mistake_row.note())
        except Exception:
            pass

    def _on_mistake_note(self, note: str) -> None:
        if self._round is None:
            return
        try:
            from persistence import set_mistake_cause
            set_mistake_cause(self._round_item_id(self._round.level),
                              self._mistake_row.cause(), note)
        except Exception:
            pass

    def _advance(self) -> None:
        self._round_idx += 1
        self._show_round()

    def _finish(self) -> None:
        stats = self._build_stats()
        if stats.total > 0:
            try:
                from persistence import save_session
                save_session(stats)
            except Exception:
                pass
        self._populate_end_page()
        self._pages.setCurrentIndex(_PAGE_END)

    def _build_stats(self) -> SessionStats:
        stats = SessionStats()
        for i, (level, success, secs) in enumerate(self._results):
            problem = Problem(
                id=f"decoder_{level}",
                category=DECODER_CATEGORY,
                difficulty=LEVEL_DIFFICULTY[level],
                question=f"Decoder Game round on the {LEVEL_TITLES[level]}",
                choices=[],
                correct_index=-1,
                explanation="",
                grade_mode=GradeMode.AUTO,
            )
            stats.total += 1
            if success:
                stats.correct += 1
            stats.attempts.append(Attempt(
                problem=problem,
                answer="decoded" if success else "logical error",
                score=10 if success else 0,
                verdict=Verdict.CORRECT if success else Verdict.INCORRECT,
                feedback="",
                hints_used=0,
                elapsed_secs=secs,
            ))
        return stats

    def _populate_end_page(self) -> None:
        total = len(self._results)
        acc = self._score / total * 100 if total else 0.0
        color = (theme.SUCCESS if acc >= 70 else
                 theme.WARNING if acc >= 40 else theme.ERROR)
        self._end_score_lbl.setText(f"{self._score} / {total}")
        self._end_score_lbl.setStyleSheet(
            f"font-size: 52px; font-weight: bold; color: {color};")
        self._end_sub_lbl.setText(
            f"{acc:.0f}% decoded correctly · best streak {self._best_streak}")

        while self._end_breakdown.count():
            item = self._end_breakdown.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for level in LEVELS:
            rounds = [(s, secs) for lvl, s, secs in self._results if lvl == level]
            if not rounds:
                continue
            n_ok = sum(1 for s, _ in rounds if s)
            lbl = QLabel(f"{LEVEL_TITLES[level]}:  {n_ok}/{len(rounds)}")
            lbl.setStyleSheet(f"font-size: 14px; color: {theme.TEXT};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._end_breakdown.addWidget(lbl)


# ── Surface-code grid widget ──────────────────────────────────────────────────

# (row, col) widget-grid positions. Data qubit q (row-major 3x3) sits at
# (1 + 2*(q//3), 1 + 2*(q%3)); stabilizer squares sit between/beside them.
_X_CHECK_POS = {(1, 2): (0, 4), (0, 1, 3, 4): (2, 2),
                (4, 5, 7, 8): (4, 4), (6, 7): (6, 2)}
_Z_CHECK_POS = {(0, 3): (2, 0), (1, 2, 4, 5): (2, 4),
                (3, 4, 6, 7): (4, 2), (5, 8): (4, 6)}

_CYCLE = ["·", "X", "Z", "Y"]


class _SurfaceGrid(QWidget):
    """3×3 data-qubit grid with stabilizer squares; clicks cycle corrections."""

    correction_changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._locked = False
        self._states: list[int] = [0] * 9      # index into _CYCLE per qubit
        grid = QGridLayout(self)
        grid.setSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)

        self._qubit_btns: list[QPushButton] = []
        for q in range(9):
            btn = QPushButton("·")
            btn.setFixedSize(48, 48)
            btn.setToolTip(f"Data qubit {q + 1} — click to cycle · X Z Y")
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.clicked.connect(lambda _=None, i=q: self._on_qubit_clicked(i))
            self._style_qubit(btn, 0)
            grid.addWidget(btn, 1 + 2 * (q // 3), 1 + 2 * (q % 3))
            self._qubit_btns.append(btn)

        # Stabilizer squares in the same order as SURFACE.stabilizers:
        # 4 X-checks then 4 Z-checks.
        self._check_lbls: list[QLabel] = []
        for sup in SURFACE_X_CHECKS:
            self._check_lbls.append(self._add_check(grid, _X_CHECK_POS[sup], "X"))
        for sup in SURFACE_Z_CHECKS:
            self._check_lbls.append(self._add_check(grid, _Z_CHECK_POS[sup], "Z"))
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _add_check(self, grid: QGridLayout, pos: tuple[int, int],
                   kind: str) -> QLabel:
        lbl = QLabel(kind)
        lbl.setFixedSize(34, 34)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(lbl, pos[0], pos[1],
                       Qt.AlignmentFlag.AlignCenter)
        self._style_check(lbl, kind, fired=False)
        return lbl

    @staticmethod
    def _check_text(kind: str, fired: bool) -> str:
        """Fired checks read "X−" (measured −1), quiet ones "X+": the red fill
        is never the only signal."""
        return f"{kind}\u2212" if fired else f"{kind}+"

    _STATE_NAMES = {0: "no correction", 1: "X correction",
                    2: "Z correction", 3: "Y correction"}

    def _style_qubit(self, btn: QPushButton, state: int) -> None:
        colors = {0: theme.TEXT_MUTED, 1: X_COLOR, 2: Z_COLOR, 3: theme.WARNING}
        c = colors[state]
        base_name = btn.toolTip().split(" — ")[0] or "Data qubit"
        btn.setAccessibleName(f"{base_name} — {self._STATE_NAMES[state]}")
        btn.setStyleSheet(
            f"QPushButton {{ background: {theme.SURFACE2}; color: {c};"
            f" border: 2px solid {c if state else theme.BORDER};"
            " border-radius: 24px; font-size: 18px; font-weight: bold;"
            " padding: 0; }"
            f"QPushButton:hover {{ border-color: {theme.ACCENT}; }}")
        btn.setText(_CYCLE[state])

    def _style_check(self, lbl: QLabel, kind: str, fired: bool) -> None:
        base = X_COLOR if kind == "X" else Z_COLOR
        lbl.setText(self._check_text(kind, fired))
        lbl.setAccessibleName(
            f"{kind}-type stabilizer check, "
            + ("fired, measured minus one" if fired else "quiet, measured plus one"))
        lbl.setToolTip(lbl.accessibleName())
        if fired:
            # theme.BG on ERROR is 5.7:1; white on ERROR was only 3.4:1.
            lbl.setStyleSheet(
                f"background: {theme.ERROR}; color: {theme.BG}; border-radius: 4px;"
                f" border: 2px solid {theme.ERROR};"
                " font-size: 13px; font-weight: bold;")
        else:
            lbl.setStyleSheet(
                f"background: {base}33; color: {theme.TEXT}; border-radius: 4px;"
                f" border: 1px solid {base};"
                " font-size: 13px; font-weight: bold;")

    def _on_qubit_clicked(self, q: int) -> None:
        if self._locked:
            return
        self._states[q] = (self._states[q] + 1) % 4
        self._style_qubit(self._qubit_btns[q], self._states[q])
        self.correction_changed.emit()

    # ── API ───────────────────────────────────────────────────────────────────

    def load_syndrome(self, syndrome: tuple[int, ...]) -> None:
        """Show fired checks for a new round and reset the correction."""
        self.set_locked(False)
        self.clear_correction()
        kinds = ["X"] * len(SURFACE_X_CHECKS) + ["Z"] * len(SURFACE_Z_CHECKS)
        for lbl, kind, bit in zip(self._check_lbls, kinds, syndrome):
            self._style_check(lbl, kind, fired=bool(bit))

    def clear_correction(self) -> None:
        self._states = [0] * 9
        for q, btn in enumerate(self._qubit_btns):
            self._style_qubit(btn, 0)

    def set_locked(self, locked: bool) -> None:
        self._locked = locked

    def correction(self) -> tuple[int, int]:
        x_mask = z_mask = 0
        for q, state in enumerate(self._states):
            if _CYCLE[state] in ("X", "Y"):
                x_mask |= 1 << q
            if _CYCLE[state] in ("Z", "Y"):
                z_mask |= 1 << q
        return (x_mask, z_mask)
