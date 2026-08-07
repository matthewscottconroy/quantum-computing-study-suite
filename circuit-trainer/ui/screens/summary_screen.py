"""Session summary screen with accuracy stats, category breakdown chart, and problem log."""

from __future__ import annotations
import json, datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QScrollArea, QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from core.models import SessionStats
from ui import theme


class SummaryScreen(QWidget):
    restart_requested = pyqtSignal()
    review_mistakes   = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._stats: SessionStats | None = None
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

        title = QLabel("Session Complete")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator"); root.addWidget(sep)

        # Stat cards
        cards = QHBoxLayout(); cards.setSpacing(16)
        self._total_card   = _StatCard("Problems", "0")
        self._correct_card = _StatCard("Correct", "0")
        self._acc_card     = _StatCard("Accuracy", "—")
        cards.addWidget(self._total_card)
        cards.addWidget(self._correct_card)
        cards.addWidget(self._acc_card)
        root.addLayout(cards)

        # Chart
        chart_lbl = QLabel("Accuracy by category")
        chart_lbl.setStyleSheet(f"font-weight:bold; font-size:11px; color:{theme.TEXT_MUTED};")
        root.addWidget(chart_lbl)
        self._chart_frame = QFrame(); self._chart_frame.setObjectName("card")
        self._chart_frame.setFixedHeight(240)
        self._chart_slot = QVBoxLayout(self._chart_frame)
        self._chart_slot.setContentsMargins(0,0,0,0)
        root.addWidget(self._chart_frame)

        # Table
        hist_lbl = QLabel("Problem log")
        hist_lbl.setStyleSheet(f"font-weight:bold; font-size:11px; color:{theme.TEXT_MUTED};")
        root.addWidget(hist_lbl)
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["#", "Category", "Difficulty", "Result", "Score"])
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(f"alternate-background-color: {theme.SURFACE2};")
        root.addWidget(self._table)
        root.addStretch()

        # Bottom bar
        bar = QWidget()
        bar.setStyleSheet(f"background:{theme.SURFACE}; border-top:1px solid {theme.BORDER};")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(48, 12, 48, 12)
        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(self._export_json)
        bl.addWidget(export_json_btn)
        export_md_btn = QPushButton("Export Markdown")
        export_md_btn.clicked.connect(self._export_markdown)
        bl.addWidget(export_md_btn)
        bl.addStretch()
        self._review_btn = QPushButton("Review Mistakes")
        self._review_btn.clicked.connect(self.review_mistakes)
        self._review_btn.hide()
        bl.addWidget(self._review_btn)
        restart_btn = QPushButton("New Session"); restart_btn.setObjectName("accent")
        restart_btn.clicked.connect(self.restart_requested)
        bl.addWidget(restart_btn)
        outer.addWidget(bar)

    def load_stats(self, stats: SessionStats) -> None:
        self._stats = stats
        self._total_card.set_value(str(stats.total))
        self._correct_card.set_value(str(stats.correct))
        self._acc_card.set_value(f"{stats.accuracy*100:.0f}%")
        self._populate_table(stats)
        self._render_chart(stats)
        # Show "Review Mistakes" only when there are wrong answers to revisit.
        if stats.wrong > 0:
            self._review_btn.show()
        else:
            self._review_btn.hide()
        try:
            from persistence import save_session
            save_session(stats)
        except Exception:
            pass

    def _populate_table(self, stats: SessionStats) -> None:
        self._table.setRowCount(0)
        for i, a in enumerate(stats.attempts):
            row = self._table.rowCount(); self._table.insertRow(row)
            self._table.setItem(row, 0, _cell(str(i+1), center=True))
            self._table.setItem(row, 1, _cell(a.problem.category.value))
            self._table.setItem(row, 2, _cell(a.problem.difficulty, center=True))
            verdict = "✓ Correct" if a.is_correct else "✗ Wrong"
            v_item = _cell(verdict, center=True)
            v_item.setForeground(QColor(theme.SUCCESS if a.is_correct else theme.ERROR))
            self._table.setItem(row, 3, v_item)
            s_item = _cell(f"{a.score}/10", center=True)
            s_item.setForeground(QColor(theme.SUCCESS if a.score>=7 else theme.PARTIAL if a.score>=4 else theme.ERROR))
            self._table.setItem(row, 4, s_item)

    def _render_chart(self, stats: SessionStats) -> None:
        while self._chart_slot.count():
            c = self._chart_slot.takeAt(0)
            if c.widget(): c.widget().deleteLater()

        by_cat = stats.scores_by_category()
        if not by_cat:
            return

        cats = list(by_cat.keys())
        # Count correct per category (score >= 7)
        accs = [sum(1 for s in scores if s >= 7) / len(scores) * 100 for scores in by_cat.values()]
        colors = [theme.CATEGORY_COLORS.get(c, theme.ACCENT) for c in cats]
        short_cats = [c.replace(" ", "\n") for c in cats]

        fig, ax = plt.subplots(figsize=(8, 2.6))
        fig.patch.set_facecolor(theme.SURFACE)
        ax.set_facecolor(theme.SURFACE)
        bars = ax.barh(short_cats, accs, color=colors, height=0.5, edgecolor="none")
        ax.set_xlim(0, 100)
        ax.set_xlabel("Accuracy %", color=theme.TEXT_MUTED, fontsize=9)
        ax.tick_params(colors=theme.TEXT_MUTED, labelsize=8)
        for spine in ax.spines.values(): spine.set_edgecolor(theme.BORDER)
        for bar, acc in zip(bars, accs):
            ax.text(acc+1, bar.get_y()+bar.get_height()/2, f"{acc:.0f}%",
                    va="center", color=theme.TEXT, fontsize=9)
        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setStyleSheet(f"background:{theme.SURFACE};")
        self._chart_slot.addWidget(canvas)
        plt.close(fig)

    def _export_json(self) -> None:
        if not self._stats:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export session",
            f"circuit-trainer-{datetime.date.today()}.json", "JSON (*.json)"
        )
        if not path:
            return
        data = {
            "date": str(datetime.date.today()),
            "total": self._stats.total,
            "correct": self._stats.correct,
            "accuracy": round(self._stats.accuracy, 4),
            "attempts": [
                {
                    "category": a.problem.category.value,
                    "difficulty": a.problem.difficulty,
                    "question": a.problem.question_text,
                    "user_answer": a.user_answer,
                    "correct": a.is_correct,
                    "score": a.score,
                    "feedback": a.feedback,
                }
                for a in self._stats.attempts
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _export_markdown(self) -> None:
        if not self._stats:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export session as Markdown",
            f"circuit-trainer-{datetime.date.today()}.md", "Markdown (*.md)"
        )
        if not path:
            return
        lines: list[str] = []
        lines.append(f"# Circuit Trainer — {datetime.date.today()}\n")
        lines.append(
            f"**Correct:** {self._stats.correct} / {self._stats.total} "
            f"({self._stats.accuracy*100:.0f}%)\n"
        )
        lines.append("---\n")
        for i, a in enumerate(self._stats.attempts, 1):
            verdict = "✓" if a.is_correct else ("~" if a.score >= 4 else "✗")
            lines.append(
                f"### {i} — {a.problem.category.value} · {a.problem.difficulty} · {verdict}\n"
            )
            lines.append(f"**Question:**\n{a.problem.question_text}\n")
            ans_label = a.user_answer
            if a.problem.choices and a.user_answer.isdigit():
                idx = int(a.user_answer)
                if 0 <= idx < len(a.problem.choices):
                    ans_label = a.problem.choices[idx]
            lines.append(
                f"**Your answer:** {ans_label} "
                f"({'✓' if a.is_correct else '✗'})\n"
            )
            if a.problem.solution_steps:
                lines.append("**Solution:**")
                for j, step in enumerate(a.problem.solution_steps, 1):
                    lines.append(f"{j}. {step}")
                lines.append("")
            lines.append(f"**Key concepts:** {' · '.join(a.problem.key_concepts)}\n")
            lines.append("---\n")
        with open(path, "w") as f:
            f.write("\n".join(lines))


class _StatCard(QFrame):
    def __init__(self, label: str, value: str, parent=None) -> None:
        super().__init__(parent); self.setObjectName("card")
        layout = QVBoxLayout(self); layout.setContentsMargins(20,16,20,16); layout.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size:11px; color:{theme.TEXT_MUTED}; font-weight:bold;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        self._val = QLabel(value)
        self._val.setStyleSheet("font-size:28px; font-weight:bold;")
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
