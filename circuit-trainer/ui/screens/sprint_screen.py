"""Sprint mode screens — timed rapid-fire multiple-choice problems.

SprintScreen: one problem at a time with a visible 60-second countdown
(QTimer). Answering or timing out flashes right/wrong immediately, then
auto-advances — no worked solutions, no hints, no Claude.

SprintSummaryScreen: end-of-sprint stats — score, accuracy, average
response time, and a per-category breakdown.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt6.QtCore import Qt, pyqtSignal, QElapsedTimer, QTimer
from PyQt6.QtGui import QColor

from core.models import Problem, Attempt, SessionStats
from config import SPRINT_SECONDS, SPRINT_FLASH_MS
from ui import theme
from ui.widgets.circuit_panel import CircuitPanel


class SprintScreen(QWidget):
    answer_chosen     = pyqtSignal(int, int)   # (choice index, elapsed_secs)
    timed_out         = pyqtSignal(int)        # (elapsed_secs)
    advance_requested = pyqtSignal()           # emitted after the flash

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._problem: Problem | None = None
        self._answered = False
        self._remaining = SPRINT_SECONDS
        self._choice_btns: list[QPushButton] = []

        self._elapsed_timer = QElapsedTimer()
        self._countdown = QTimer(self)
        self._countdown.setInterval(1000)
        self._countdown.timeout.connect(self._tick)

        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar: badges + countdown + progress ───────────────────────────
        bar = QWidget()
        bar.setFixedHeight(48)
        bar.setStyleSheet(
            f"background:{theme.SURFACE}; border-bottom:1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 0, 16, 0)
        self._cat_badge = QLabel("")
        self._cat_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cat_badge.setFixedHeight(22)
        bar_layout.addWidget(self._cat_badge)
        sprint_badge = QLabel("SPRINT")
        sprint_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sprint_badge.setFixedHeight(22)
        sprint_badge.setStyleSheet(
            f"background:{theme.WARNING}22; color:{theme.WARNING};"
            f"border:1px solid {theme.WARNING}55; border-radius:10px;"
            "padding:2px 10px; font-size:11px; font-weight:bold;")
        bar_layout.addWidget(sprint_badge)
        bar_layout.addStretch()
        self._timer_lbl = QLabel("1:00")
        self._timer_lbl.setStyleSheet(
            f"color:{theme.TEXT}; font-size:20px; font-weight:bold;"
            "font-variant-numeric: tabular-nums;")
        bar_layout.addWidget(self._timer_lbl)
        bar_layout.addSpacing(16)
        self._progress_lbl = QLabel("")
        self._progress_lbl.setObjectName("muted")
        bar_layout.addWidget(self._progress_lbl)
        root.addWidget(bar)

        # ── Body ──────────────────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body_widget = QWidget()
        body = QVBoxLayout(body_widget)
        body.setContentsMargins(32, 20, 32, 20)
        body.setSpacing(14)

        self._question_lbl = QTextBrowser()
        self._question_lbl.setMinimumHeight(60)
        self._question_lbl.setMaximumHeight(140)
        body.addWidget(self._question_lbl)

        self._circuit = CircuitPanel("Circuit")
        body.addWidget(self._circuit)

        self._matrix_lbl = QLabel("")
        self._matrix_lbl.setObjectName("mono")
        self._matrix_lbl.setWordWrap(True)
        body.addWidget(self._matrix_lbl)

        self._state_lbl = QLabel("")
        self._state_lbl.setStyleSheet(f"color: {theme.TEAL}; font-size: 14px;")
        body.addWidget(self._state_lbl)

        # Flash verdict label (shown between answer and auto-advance)
        self._flash_lbl = QLabel("")
        self._flash_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flash_lbl.setFixedHeight(44)
        self._flash_lbl.hide()
        body.addWidget(self._flash_lbl)

        self._choices_container = QVBoxLayout()
        self._choices_container.setSpacing(8)
        body.addLayout(self._choices_container)

        body.addStretch()
        scroll.setWidget(body_widget)
        root.addWidget(scroll)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_problem(self, problem: Problem, number: int, total: int) -> None:
        self._problem = problem
        self._answered = False
        self._flash_lbl.hide()
        self._progress_lbl.setText(f"Question {number} of {total}")

        cat_color = theme.CATEGORY_COLORS.get(problem.category.value, theme.ACCENT)
        self._cat_badge.setText(problem.category.value)
        self._cat_badge.setStyleSheet(
            f"background:{cat_color}22; color:{cat_color};"
            f"border:1px solid {cat_color}55; border-radius:10px;"
            "padding:2px 10px; font-size:11px; font-weight:bold;")

        self._question_lbl.setPlainText(problem.question_text)

        self._circuit.clear()
        if problem.circuit_png:
            self._circuit.set_image(problem.circuit_png)

        if problem.matrix_str:
            self._matrix_lbl.setText(problem.matrix_str)
            self._matrix_lbl.show()
        else:
            self._matrix_lbl.hide()

        if problem.state_str:
            self._state_lbl.setText(problem.state_str)
            self._state_lbl.show()
        else:
            self._state_lbl.hide()

        self._clear_choices()
        for i, choice in enumerate(problem.choices or []):
            btn = QPushButton(choice)
            btn.setObjectName("choice")
            btn.clicked.connect(lambda _, idx=i: self._on_choice(idx))
            self._choice_btns.append(btn)
            self._choices_container.addWidget(btn)

        # Restart the countdown
        self._remaining = SPRINT_SECONDS
        self._update_timer_label()
        self._elapsed_timer.start()
        self._countdown.start()

    def show_flash(self, attempt: Attempt, timed_out: bool = False) -> None:
        """Colour the choices, flash the verdict, then request auto-advance."""
        self._answered = True
        self._countdown.stop()
        problem = attempt.problem

        correct_idx = int(problem.correct_answer)
        user_idx = (int(attempt.user_answer)
                    if attempt.user_answer.isdigit() else -1)
        for i, btn in enumerate(self._choice_btns):
            if i == correct_idx:
                btn.setObjectName("choice_correct")
            elif i == user_idx and not attempt.is_correct:
                btn.setObjectName("choice_wrong")
            btn.setEnabled(False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if timed_out:
            text, color = "⏱ Time's up!", theme.WARNING
        elif attempt.is_correct:
            text, color = "✓ Correct", theme.SUCCESS
        else:
            text, color = "✗ Wrong", theme.ERROR
        self._flash_lbl.setText(text)
        self._flash_lbl.setStyleSheet(
            f"background:{color}22; color:{color}; border:1px solid {color};"
            "border-radius:8px; font-size:20px; font-weight:bold;")
        self._flash_lbl.show()

        QTimer.singleShot(SPRINT_FLASH_MS, self.advance_requested.emit)

    def stop_timers(self) -> None:
        self._countdown.stop()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _elapsed_seconds(self) -> int:
        if self._elapsed_timer.isValid():
            return int(self._elapsed_timer.elapsed() / 1000)
        return 0

    def _update_timer_label(self) -> None:
        m, s = divmod(max(0, self._remaining), 60)
        self._timer_lbl.setText(f"{m}:{s:02d}")
        color = theme.ERROR if self._remaining <= 10 else theme.TEXT
        self._timer_lbl.setStyleSheet(
            f"color:{color}; font-size:20px; font-weight:bold;"
            "font-variant-numeric: tabular-nums;")

    def _tick(self) -> None:
        self._remaining -= 1
        self._update_timer_label()
        if self._remaining <= 0 and not self._answered:
            self._countdown.stop()
            self.timed_out.emit(self._elapsed_seconds())

    def _on_choice(self, idx: int) -> None:
        if self._answered:
            return
        self._answered = True
        self._countdown.stop()
        self.answer_chosen.emit(idx, self._elapsed_seconds())

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        """A/B/C/D select the corresponding answer."""
        if not self._answered:
            letter_map = {
                Qt.Key.Key_A: 0, Qt.Key.Key_B: 1,
                Qt.Key.Key_C: 2, Qt.Key.Key_D: 3,
            }
            key = event.key()
            if key in letter_map and letter_map[key] < len(self._choice_btns):
                self._on_choice(letter_map[key])
                return
        super().keyPressEvent(event)

    def _clear_choices(self) -> None:
        for btn in self._choice_btns:
            self._choices_container.removeWidget(btn)
            btn.deleteLater()
        self._choice_btns.clear()


class SprintSummaryScreen(QWidget):
    restart_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
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
        root.setSpacing(22)
        scroll.setWidget(content)

        title = QLabel("Sprint Complete")
        title.setObjectName("heading")
        root.addWidget(title)
        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        cards = QHBoxLayout(); cards.setSpacing(16)
        self._score_card = _StatCard("Score", "0/0")
        self._acc_card   = _StatCard("Accuracy", "—")
        self._time_card  = _StatCard("Avg Response", "—")
        cards.addWidget(self._score_card)
        cards.addWidget(self._acc_card)
        cards.addWidget(self._time_card)
        root.addLayout(cards)

        table_lbl = QLabel("Per-category breakdown")
        table_lbl.setStyleSheet(
            f"font-weight:bold; font-size:11px; color:{theme.TEXT_MUTED};")
        root.addWidget(table_lbl)
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(
            ["Category", "Correct", "Attempts", "Accuracy"])
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(f"alternate-background-color: {theme.SURFACE2};")
        root.addWidget(self._table)
        root.addStretch()

        bar = QWidget()
        bar.setStyleSheet(
            f"background:{theme.SURFACE}; border-top:1px solid {theme.BORDER};")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(48, 12, 48, 12)
        bl.addStretch()
        restart_btn = QPushButton("New Session")
        restart_btn.setObjectName("accent")
        restart_btn.clicked.connect(self.restart_requested)
        bl.addWidget(restart_btn)
        outer.addWidget(bar)

    def load_stats(self, stats: SessionStats) -> None:
        self._score_card.set_value(f"{stats.correct}/{stats.total}")
        self._acc_card.set_value(f"{stats.accuracy * 100:.0f}%")

        elapsed = [a.elapsed_secs for a in stats.attempts]
        if elapsed:
            self._time_card.set_value(f"{sum(elapsed) / len(elapsed):.1f}s")
        else:
            self._time_card.set_value("—")

        # Per-category breakdown
        by_cat: dict[str, list[bool]] = {}
        for a in stats.attempts:
            by_cat.setdefault(a.problem.category.value, []).append(a.is_correct)

        self._table.setRowCount(0)
        for cat, results in by_cat.items():
            n_ok = sum(results)
            row = self._table.rowCount()
            self._table.insertRow(row)
            cat_item = QTableWidgetItem(cat)
            cat_item.setFlags(
                Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            cat_item.setForeground(QColor(
                theme.CATEGORY_COLORS.get(cat, theme.ACCENT)))
            self._table.setItem(row, 0, cat_item)
            for col, text in (
                (1, str(n_ok)),
                (2, str(len(results))),
                (3, f"{n_ok / len(results) * 100:.0f}%"),
            ):
                item = QTableWidgetItem(text)
                item.setFlags(
                    Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row, col, item)

        # Persist in the standard schema, tagged as a sprint session
        try:
            from persistence import save_session
            save_session(stats, sprint=True)
        except Exception:
            pass


class _StatCard(QFrame):
    def __init__(self, label: str, value: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size:11px; color:{theme.TEXT_MUTED}; font-weight:bold;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        self._val = QLabel(value)
        self._val.setStyleSheet("font-size:28px; font-weight:bold;")
        self._val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._val)

    def set_value(self, v: str) -> None:
        self._val.setText(v)
