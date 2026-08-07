"""Session summary screen with stats, chart, and per-question log."""

from __future__ import annotations
import io
import json
import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QScrollArea, QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.models import SessionStats
from ui import theme


class SummaryScreen(QWidget):
    restart_requested = pyqtSignal()
    review_mistakes = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._stats: SessionStats | None = None
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
        root.setSpacing(24)
        scroll.setWidget(content)

        # ── Title ─────────────────────────────────────────────────────────────
        title = QLabel("Session Complete")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame()
        sep.setObjectName("separator")
        root.addWidget(sep)

        # ── Stat cards ────────────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        self._answered_card = _StatCard("Answered", "0")
        self._skipped_card = _StatCard("Skipped", "0")
        self._avg_card = _StatCard("Avg Score", "—")
        cards_row.addWidget(self._answered_card)
        cards_row.addWidget(self._skipped_card)
        cards_row.addWidget(self._avg_card)
        root.addLayout(cards_row)

        # ── Subject chart ─────────────────────────────────────────────────────
        chart_lbl = QLabel("Score by subject")
        chart_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(chart_lbl)
        self._chart_frame = QFrame()
        self._chart_frame.setObjectName("card")
        self._chart_frame.setFixedHeight(220)
        chart_inner = QVBoxLayout(self._chart_frame)
        chart_inner.setContentsMargins(0, 0, 0, 0)
        self._chart_canvas_slot = chart_inner
        root.addWidget(self._chart_frame)

        # ── History table ─────────────────────────────────────────────────────
        hist_lbl = QLabel("Question log")
        hist_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(hist_lbl)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["#", "Subject", "Topic", "Type", "Score"])
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(
            f"alternate-background-color: {theme.SURFACE2};"
        )
        root.addWidget(self._table)
        root.addStretch()

        # ── Bottom bar ────────────────────────────────────────────────────────
        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(48, 12, 48, 12)

        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(self._on_export)
        bar_layout.addWidget(export_json_btn)
        export_md_btn = QPushButton("Export Markdown")
        export_md_btn.clicked.connect(self._on_export_markdown)
        bar_layout.addWidget(export_md_btn)
        bar_layout.addStretch()

        self._review_btn = QPushButton("Review Mistakes")
        self._review_btn.clicked.connect(self.review_mistakes)
        self._review_btn.hide()
        bar_layout.addWidget(self._review_btn)

        restart_btn = QPushButton("New Session")
        restart_btn.setObjectName("accent")
        restart_btn.clicked.connect(self.restart_requested)
        bar_layout.addWidget(restart_btn)
        outer.addWidget(bar)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_stats(self, stats: SessionStats) -> None:
        self._stats = stats
        self._answered_card.set_value(str(stats.answered))
        self._skipped_card.set_value(str(stats.skipped))
        self._avg_card.set_value(
            f"{stats.average_score:.1f}/10" if stats.history else "—"
        )
        self._populate_table(stats)
        self._render_chart(stats)

        # Show "Review Mistakes" only when at least one question scored < 7
        has_mistakes = any(r.evaluation.score < 7 for r in stats.history)
        self._review_btn.setVisible(has_mistakes)

        if stats.answered > 0:
            try:
                from persistence import save_session
                save_session(stats)
            except Exception:
                pass

    # ── Internals ─────────────────────────────────────────────────────────────

    def _populate_table(self, stats: SessionStats) -> None:
        self._table.setRowCount(0)
        for i, record in enumerate(stats.history):
            ev = record.evaluation
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, _cell(str(i + 1), center=True))
            self._table.setItem(row, 1, _cell(record.question.subject))
            self._table.setItem(row, 2, _cell(record.question.topic))
            self._table.setItem(row, 3, _cell(record.question.question_type))
            score_item = _cell(f"{ev.score}/10", center=True)
            score_item.setForeground(QColor(_score_color(ev.score)))
            self._table.setItem(row, 4, score_item)

    def _render_chart(self, stats: SessionStats) -> None:
        # Remove previous canvas if any
        while self._chart_canvas_slot.count():
            child = self._chart_canvas_slot.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        by_subject = stats.scores_by_subject()
        if not by_subject:
            return

        subjects = list(by_subject.keys())
        averages = [sum(v) / len(v) for v in by_subject.values()]
        colors = [theme.subject_color(s) for s in subjects]

        fig, ax = plt.subplots(figsize=(8, 2.4))
        fig.patch.set_facecolor(theme.SURFACE)
        ax.set_facecolor(theme.SURFACE)

        bars = ax.barh(subjects, averages, color=colors, height=0.5, edgecolor="none")
        ax.set_xlim(0, 10)
        ax.set_xlabel("Average score", color=theme.TEXT_MUTED, fontsize=9)
        ax.tick_params(colors=theme.TEXT_MUTED, labelsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor(theme.BORDER)
        ax.set_facecolor(theme.SURFACE)
        for bar, avg in zip(bars, averages):
            ax.text(
                avg + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{avg:.1f}", va="center", color=theme.TEXT, fontsize=9
            )

        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setStyleSheet(f"background: {theme.SURFACE};")
        self._chart_canvas_slot.addWidget(canvas)
        plt.close(fig)

    def _on_export(self) -> None:
        if not self._stats:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export session", f"quantum-quiz-{datetime.date.today()}.json", "JSON (*.json)"
        )
        if not path:
            return
        data = {
            "date": str(datetime.date.today()),
            "answered": self._stats.answered,
            "skipped": self._stats.skipped,
            "average_score": round(self._stats.average_score, 2),
            "questions": [
                {
                    "subject": r.question.subject,
                    "topic": r.question.topic,
                    "difficulty": r.question.difficulty,
                    "type": r.question.question_type,
                    "question": r.question.text,
                    "answer": r.user_answer,
                    "score": r.evaluation.score,
                    "verdict": r.evaluation.verdict,
                    "feedback": r.evaluation.feedback,
                    "model_answer": r.evaluation.model_answer,
                }
                for r in self._stats.history
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _on_export_markdown(self) -> None:
        if not self._stats:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export session as Markdown",
            f"quantum-quiz-{datetime.date.today()}.md", "Markdown (*.md)"
        )
        if not path:
            return
        lines: list[str] = []
        lines.append(f"# Quantum Quiz — {datetime.date.today()}\n")
        avg = self._stats.average_score
        lines.append(
            f"**Average:** {avg:.1f}/10 "
            f"({self._stats.answered} answered, {self._stats.skipped} skipped)\n"
        )
        lines.append("---\n")
        for i, r in enumerate(self._stats.history, 1):
            ev = r.evaluation
            score_sym = "✓" if ev.score >= 7 else ("~" if ev.score >= 4 else "✗")
            lines.append(
                f"### {i} — {r.question.subject} · {r.question.difficulty} · "
                f"{ev.score}/10 {score_sym}\n"
            )
            lines.append(f"**Topic:** {r.question.topic}\n")
            lines.append(f"**Type:** {r.question.question_type}\n")
            lines.append(f"**Question:**\n{r.question.text}\n")
            lines.append(f"**Your answer:**\n{r.user_answer}\n")
            lines.append(f"**Score:** {ev.score}/10 — {ev.verdict}\n")
            lines.append(f"**Feedback:** {ev.feedback}\n")
            lines.append(f"**Model answer:**\n{ev.model_answer}\n")
            if ev.key_points_missed:
                lines.append("**Key points missed:**")
                for pt in ev.key_points_missed:
                    lines.append(f"- {pt}")
                lines.append("")
            if ev.follow_up:
                lines.append(f"**Follow-up question:** {ev.follow_up}\n")
            lines.append("---\n")
        with open(path, "w") as f:
            f.write("\n".join(lines))


# ── Helper widgets ────────────────────────────────────────────────────────────

class _StatCard(QFrame):
    def __init__(self, label: str, value: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED}; font-weight: bold;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        self._val = QLabel(value)
        self._val.setStyleSheet("font-size: 26px; font-weight: bold;")
        self._val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._val)

    def set_value(self, v: str) -> None:
        self._val.setText(v)


def _cell(text: str, center: bool = False) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
    if center:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item


def _score_color(score: int) -> str:
    if score >= 7:
        return theme.SUCCESS
    if score >= 4:
        return theme.PARTIAL
    return theme.ERROR
