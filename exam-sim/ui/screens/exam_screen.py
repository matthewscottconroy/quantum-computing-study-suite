"""Exam screen — timed question runner with navigator, flag/skip/return."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QRadioButton, QButtonGroup, QTextBrowser, QScrollArea,
    QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QElapsedTimer
from core.models import Question, ExamAttempt, ExamResult
from ui import theme
from ui.format import question_html

_NAV_COLS = 6


class ExamScreen(QWidget):
    session_finished = pyqtSignal(object)   # ExamResult

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._attempts: list[ExamAttempt] = []
        self._idx = 0
        self._mode = "full"
        self._remaining_secs = 0
        self._nav_btns: list[QPushButton] = []
        self._elapsed = QElapsedTimer()
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(36, 24, 24, 20)
        root.setSpacing(24)

        # ---- left: question area ----
        left = QVBoxLayout(); left.setSpacing(12)
        root.addLayout(left, 5)

        meta_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        meta_row.addWidget(self._progress_lbl)
        meta_row.addStretch()
        self._section_lbl = QLabel("")
        meta_row.addWidget(self._section_lbl)
        left.addLayout(meta_row)

        q_frame = QFrame(); q_frame.setObjectName("card")
        q_layout = QVBoxLayout(q_frame)
        q_layout.setContentsMargins(20, 14, 20, 14)
        self._question_browser = QTextBrowser()
        self._question_browser.setOpenExternalLinks(False)
        self._question_browser.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        q_layout.addWidget(self._question_browser)
        left.addWidget(q_frame, 3)

        options_box = QWidget()
        opt_layout = QVBoxLayout(options_box)
        opt_layout.setContentsMargins(4, 0, 0, 0)
        opt_layout.setSpacing(8)
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(False)   # managed manually to allow clearing
        self._btn_group.buttonClicked.connect(self._on_option_clicked)
        self._radio_btns: list[QRadioButton] = []
        for i in range(4):
            rb = QRadioButton("")
            self._btn_group.addButton(rb, i)
            self._radio_btns.append(rb)
            opt_layout.addWidget(rb)
        opt_scroll = QScrollArea()
        opt_scroll.setWidgetResizable(True)
        opt_scroll.setWidget(options_box)
        opt_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left.addWidget(opt_scroll, 2)

        nav_row = QHBoxLayout()
        self._flag_btn = QPushButton("Flag for review")
        self._flag_btn.clicked.connect(self._on_flag)
        nav_row.addWidget(self._flag_btn)
        self._clear_btn = QPushButton("Clear answer")
        self._clear_btn.setObjectName("flat")
        self._clear_btn.clicked.connect(self._on_clear)
        nav_row.addWidget(self._clear_btn)
        nav_row.addStretch()
        self._prev_btn = QPushButton("← Previous")
        self._prev_btn.clicked.connect(lambda: self._goto(self._idx - 1))
        nav_row.addWidget(self._prev_btn)
        self._next_btn = QPushButton("Next →")
        self._next_btn.clicked.connect(lambda: self._goto(self._idx + 1))
        nav_row.addWidget(self._next_btn)
        left.addLayout(nav_row)

        # ---- right: timer + navigator ----
        right = QVBoxLayout(); right.setSpacing(12)
        root.addLayout(right, 2)

        self._timer_lbl = QLabel("--:--")
        self._timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._timer_lbl.setStyleSheet(
            f"font-size: 30px; font-weight: bold; color: {theme.TEXT};"
            f"font-family: {theme.MONO};"
        )
        right.addWidget(self._timer_lbl)

        nav_frame = QFrame(); nav_frame.setObjectName("card")
        nav_outer = QVBoxLayout(nav_frame)
        nav_outer.setContentsMargins(12, 10, 12, 10)
        nav_title = QLabel("QUESTIONS")
        nav_title.setStyleSheet(
            f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
        nav_outer.addWidget(nav_title)
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._nav_widget = QWidget()
        self._nav_grid = QGridLayout(self._nav_widget)
        self._nav_grid.setSpacing(6)
        self._nav_grid.setContentsMargins(0, 4, 0, 4)
        nav_scroll.setWidget(self._nav_widget)
        nav_outer.addWidget(nav_scroll)
        legend = QLabel(
            f'<span style="color:{theme.ACCENT}">■</span> answered   '
            f'<span style="color:{theme.FLAG}">■</span> flagged   '
            f'<span style="color:{theme.TEXT_MUTED}">■</span> unanswered'
        )
        legend.setStyleSheet("font-size: 11px;")
        nav_outer.addWidget(legend)
        right.addWidget(nav_frame, 1)

        self._answered_lbl = QLabel("")
        self._answered_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        right.addWidget(self._answered_lbl)

        submit_btn = QPushButton("Submit Exam")
        submit_btn.setObjectName("accent")
        submit_btn.clicked.connect(self._on_submit_clicked)
        right.addWidget(submit_btn)

    # ------------------------------------------------------------- session
    def start_session(self, questions: list[Question], minutes: int, mode: str) -> None:
        self._attempts = [ExamAttempt(question=q) for q in questions]
        self._idx = 0
        self._mode = mode
        self._remaining_secs = minutes * 60
        self._elapsed.start()
        self._build_navigator()
        self._update_timer_label()
        self._timer.start()
        self._show_current()

    def _build_navigator(self) -> None:
        while self._nav_grid.count():
            item = self._nav_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._nav_btns = []
        for i in range(len(self._attempts)):
            btn = QPushButton(str(i + 1))
            btn.setObjectName("nav")
            btn.clicked.connect(lambda _, k=i: self._goto(k))
            self._nav_grid.addWidget(btn, i // _NAV_COLS, i % _NAV_COLS)
            self._nav_btns.append(btn)

    # ------------------------------------------------------------- display
    def _show_current(self) -> None:
        attempt = self._attempts[self._idx]
        q = attempt.question
        total = len(self._attempts)
        self._progress_lbl.setText(f"Question {self._idx + 1} of {total}")
        color = theme.SECTION_COLORS.get(q.section, theme.ACCENT)
        self._section_lbl.setText(q.section.upper())
        self._section_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {color};")
        self._question_browser.setHtml(question_html(q.question))
        for i, rb in enumerate(self._radio_btns):
            rb.blockSignals(True)
            rb.setText(f"{chr(65 + i)}.  {q.options[i]}" if i < len(q.options) else "")
            rb.setVisible(i < len(q.options))
            rb.setChecked(attempt.chosen_index == i)
            rb.blockSignals(False)
        self._flag_btn.setText("Unflag" if attempt.flagged else "Flag for review")
        self._prev_btn.setEnabled(self._idx > 0)
        self._next_btn.setEnabled(self._idx < total - 1)
        self._refresh_navigator()

    def _refresh_navigator(self) -> None:
        for i, btn in enumerate(self._nav_btns):
            attempt = self._attempts[i]
            if attempt.flagged:
                bg, fg = theme.FLAG, theme.BG
            elif attempt.answered:
                bg, fg = theme.ACCENT, theme.BG
            else:
                bg, fg = theme.SURFACE2, theme.TEXT_MUTED
            border = theme.TEXT if i == self._idx else theme.BORDER
            btn.setStyleSheet(
                f"QPushButton#nav {{ background: {bg}; color: {fg};"
                f" border: 2px solid {border}; }}"
            )
        answered = sum(1 for a in self._attempts if a.answered)
        self._answered_lbl.setText(
            f"{answered}/{len(self._attempts)} answered — "
            f"{sum(1 for a in self._attempts if a.flagged)} flagged"
        )

    # ------------------------------------------------------------- actions
    def _on_option_clicked(self, clicked) -> None:
        idx = self._btn_group.id(clicked)
        for i, rb in enumerate(self._radio_btns):
            rb.blockSignals(True)
            rb.setChecked(i == idx)
            rb.blockSignals(False)
        self._attempts[self._idx].chosen_index = idx
        self._refresh_navigator()

    def _on_clear(self) -> None:
        self._attempts[self._idx].chosen_index = None
        for rb in self._radio_btns:
            rb.blockSignals(True)
            rb.setChecked(False)
            rb.blockSignals(False)
        self._refresh_navigator()

    def _on_flag(self) -> None:
        attempt = self._attempts[self._idx]
        attempt.flagged = not attempt.flagged
        self._flag_btn.setText("Unflag" if attempt.flagged else "Flag for review")
        self._refresh_navigator()

    def _goto(self, idx: int) -> None:
        if 0 <= idx < len(self._attempts):
            self._idx = idx
            self._show_current()

    # --------------------------------------------------------------- timer
    def _tick(self) -> None:
        self._remaining_secs -= 1
        if self._remaining_secs <= 0:
            self._remaining_secs = 0
            self._update_timer_label()
            self._timer.stop()
            QMessageBox.information(self, "Time", "Time is up — the exam has been submitted.")
            self._finish()
            return
        self._update_timer_label()

    def _update_timer_label(self) -> None:
        mins, secs = divmod(max(0, self._remaining_secs), 60)
        color = theme.ERROR if self._remaining_secs < 300 else theme.TEXT
        self._timer_lbl.setText(f"{mins:02d}:{secs:02d}")
        self._timer_lbl.setStyleSheet(
            f"font-size: 30px; font-weight: bold; color: {color};"
            f"font-family: {theme.MONO};"
        )

    # -------------------------------------------------------------- submit
    def _on_submit_clicked(self) -> None:
        unanswered = sum(1 for a in self._attempts if not a.answered)
        flagged = sum(1 for a in self._attempts if a.flagged)
        msg = "Submit the exam?"
        details = []
        if unanswered:
            details.append(f"{unanswered} unanswered")
        if flagged:
            details.append(f"{flagged} still flagged")
        if details:
            msg = f"Submit the exam? ({', '.join(details)})"
        btn = QMessageBox.question(
            self, "Submit", msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if btn == QMessageBox.StandardButton.Yes:
            self._timer.stop()
            self._finish()

    def _finish(self) -> None:
        result = ExamResult(
            mode=self._mode,
            attempts=self._attempts,
            duration_secs=self._elapsed.elapsed() / 1000.0,
        )
        self.session_finished.emit(result)

    def abort(self) -> None:
        self._timer.stop()
