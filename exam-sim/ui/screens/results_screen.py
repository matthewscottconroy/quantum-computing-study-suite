"""Results screen — score vs pass bar, per-section table, missed-question review."""
from __future__ import annotations
import html
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QScrollArea, QProgressBar, QHeaderView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import ExamResult
from config import SECTIONS, section_weight, pass_mark_for
from ui import theme
from ui.format import question_html


class ResultsScreen(QWidget):
    home_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 24)
        root.setSpacing(14)

        header = QHBoxLayout()
        self._verdict_lbl = QLabel("")
        self._verdict_lbl.setObjectName("heading")
        header.addWidget(self._verdict_lbl)
        header.addStretch()
        self._detail_lbl = QLabel("")
        self._detail_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 14px;")
        header.addWidget(self._detail_lbl)
        root.addLayout(header)

        self._pass_bar = QProgressBar()
        self._pass_bar.setFixedHeight(14)
        self._pass_bar.setTextVisible(False)
        root.addWidget(self._pass_bar)
        self._bar_lbl = QLabel("")
        self._bar_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        root.addWidget(self._bar_lbl)

        body = QHBoxLayout(); body.setSpacing(24)
        root.addLayout(body, 1)

        # left: per-section table
        left = QVBoxLayout()
        sec_lbl = QLabel("PER-SECTION BREAKDOWN")
        sec_lbl.setStyleSheet(
            f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
        left.addWidget(sec_lbl)
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(
            ["Section", "Correct", "Your %", "Exam weight"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        left.addWidget(self._table, 1)
        body.addLayout(left, 2)

        # right: review pane of missed questions
        right = QVBoxLayout()
        rev_lbl = QLabel("REVIEW — MISSED QUESTIONS")
        rev_lbl.setStyleSheet(
            f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
        right.addWidget(rev_lbl)
        self._review_scroll = QScrollArea()
        self._review_scroll.setWidgetResizable(True)
        self._review_container = QWidget()
        self._review_layout = QVBoxLayout(self._review_container)
        self._review_layout.setSpacing(12)
        self._review_scroll.setWidget(self._review_container)
        right.addWidget(self._review_scroll, 1)
        body.addLayout(right, 3)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        home_btn = QPushButton("Back to Home")
        home_btn.setObjectName("accent")
        home_btn.clicked.connect(self.home_requested)
        btn_row.addWidget(home_btn)
        root.addLayout(btn_row)

    # ---------------------------------------------------------------- show
    def show_result(self, result: ExamResult) -> None:
        total, correct = result.total, result.correct
        need = pass_mark_for(total)
        passed = correct >= need
        color = theme.SUCCESS if passed else theme.ERROR
        self._verdict_lbl.setText("PASS" if passed else "FAIL")
        self._verdict_lbl.setStyleSheet(
            f"font-size: 26px; font-weight: bold; color: {color};")
        mins, secs = divmod(int(result.duration_secs), 60)
        mode_name = "Full exam" if result.mode == "full" else "Sprint"
        self._detail_lbl.setText(
            f"{mode_name} — {correct}/{total} correct in {mins}m {secs:02d}s "
            f"(pass mark {need}/{total})"
        )
        self._pass_bar.setRange(0, total)
        self._pass_bar.setValue(correct)
        self._pass_bar.setStyleSheet(
            f"QProgressBar {{ background: {theme.SURFACE2}; border: none;"
            f" border-radius: 7px; }}"
            f"QProgressBar::chunk {{ background: {color}; border-radius: 7px; }}"
        )
        pct = 100.0 * correct / total if total else 0.0
        self._bar_lbl.setText(
            f"Score {pct:.0f}% — pass bar at {100.0 * need / total:.0f}% ({need}/{total})")

        self._fill_table(result)
        self._fill_review(result)

    def _fill_table(self, result: ExamResult) -> None:
        breakdown = result.section_breakdown()
        sections = [s for s in SECTIONS if s in breakdown]
        sections += [s for s in breakdown if s not in SECTIONS]
        self._table.setRowCount(len(sections))
        for row, section in enumerate(sections):
            b = breakdown[section]
            your_pct = 100.0 * b["correct"] / b["total"] if b["total"] else 0.0
            weight_pct = 100.0 * section_weight(section)
            items = [
                QTableWidgetItem(section),
                QTableWidgetItem(f"{b['correct']}/{b['total']}"),
                QTableWidgetItem(f"{your_pct:.0f}%"),
                QTableWidgetItem(f"{weight_pct:.0f}%"),
            ]
            items[0].setForeground(Qt.GlobalColor.white)
            for col, item in enumerate(items):
                if col:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row, col, item)

    def _fill_review(self, result: ExamResult) -> None:
        while self._review_layout.count():
            item = self._review_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        missed = result.missed
        if not missed:
            lbl = QLabel("Nothing missed — a clean run.")
            lbl.setStyleSheet(f"color: {theme.SUCCESS}; font-size: 14px;")
            self._review_layout.addWidget(lbl)
        for attempt in missed:
            q = attempt.question
            card = QFrame(); card.setObjectName("card")
            lay = QVBoxLayout(card)
            lay.setContentsMargins(16, 12, 16, 12)
            lay.setSpacing(6)
            chosen = (q.options[attempt.chosen_index]
                      if attempt.chosen_index is not None else "(no answer)")
            correct = q.options[q.correct_index]
            body = QLabel(
                f'<span style="color:{theme.SECTION_COLORS.get(q.section, theme.ACCENT)};'
                f'font-size:11px;font-weight:bold;">{html.escape(q.section.upper())}</span>'
                f"<div style='font-size:14px;'>{question_html(q.question)}</div>"
                f'<div style="color:{theme.ERROR};">Your answer: '
                f"{html.escape(chosen)}</div>"
                f'<div style="color:{theme.SUCCESS};">Correct: '
                f"{html.escape(correct)}</div>"
                f'<div style="color:{theme.TEXT_MUTED};font-size:13px;">'
                f"{html.escape(q.explanation)}</div>"
            )
            body.setWordWrap(True)
            body.setTextFormat(Qt.TextFormat.RichText)
            lay.addWidget(body)
            self._review_layout.addWidget(card)
        self._review_layout.addStretch()
