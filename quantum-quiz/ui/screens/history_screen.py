"""Lifetime history screen — score trend + per-subject averages + stats cards."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui import theme


class HistoryScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
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

        title = QLabel("Session History")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame()
        sep.setObjectName("separator")
        root.addWidget(sep)

        # ── Stat cards ────────────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        self._sessions_card  = _StatCard("Sessions", "0")
        self._questions_card = _StatCard("Questions", "0")
        self._avg_card       = _StatCard("Lifetime Avg", "—")
        cards_row.addWidget(self._sessions_card)
        cards_row.addWidget(self._questions_card)
        cards_row.addWidget(self._avg_card)
        root.addLayout(cards_row)

        # ── Score trend chart ─────────────────────────────────────────────────
        trend_lbl = QLabel("Score trend (last 30 sessions)")
        trend_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};"
        )
        root.addWidget(trend_lbl)
        self._trend_frame = QFrame()
        self._trend_frame.setObjectName("card")
        self._trend_frame.setFixedHeight(200)
        trend_inner = QVBoxLayout(self._trend_frame)
        trend_inner.setContentsMargins(0, 0, 0, 0)
        self._trend_slot = trend_inner
        root.addWidget(self._trend_frame)

        # ── Per-subject bar chart ─────────────────────────────────────────────
        subj_lbl = QLabel("Average score by subject (all time)")
        subj_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};"
        )
        root.addWidget(subj_lbl)
        self._subj_frame = QFrame()
        self._subj_frame.setObjectName("card")
        self._subj_frame.setMinimumHeight(120)
        subj_inner = QVBoxLayout(self._subj_frame)
        subj_inner.setContentsMargins(0, 0, 0, 0)
        self._subj_slot = subj_inner
        root.addWidget(self._subj_frame)

        self._empty_lbl = QLabel("No session history yet. Complete a session to see stats here.")
        self._empty_lbl.setObjectName("subheading")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._empty_lbl)

        # ── Flagged for review ────────────────────────────────────────────────
        flag_hdr = QHBoxLayout()
        flag_lbl = QLabel("Flagged for review")
        flag_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};"
        )
        flag_hdr.addWidget(flag_lbl)
        flag_hdr.addStretch()
        self._flag_count_lbl = QLabel("")
        self._flag_count_lbl.setObjectName("muted")
        flag_hdr.addWidget(self._flag_count_lbl)
        root.addLayout(flag_hdr)

        self._flag_frame = QFrame()
        self._flag_frame.setObjectName("card")
        self._flag_slot = QVBoxLayout(self._flag_frame)
        self._flag_slot.setContentsMargins(16, 12, 16, 12)
        self._flag_slot.setSpacing(6)
        root.addWidget(self._flag_frame)

        root.addStretch()

        # ── Bottom bar ────────────────────────────────────────────────────────
        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(48, 12, 48, 12)
        bar_layout.addStretch()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("accent")
        back_btn.clicked.connect(self.back_requested)
        bar_layout.addWidget(back_btn)
        outer.addWidget(bar)

    def refresh(self) -> None:
        try:
            from persistence import _load_raw
            sessions = _load_raw()
        except Exception:
            sessions = []

        self._render(sessions)
        self._render_flagged()

    # ── Flagged list ──────────────────────────────────────────────────────────

    def _render_flagged(self) -> None:
        _clear_slot(self._flag_slot)
        try:
            from persistence import load_flagged
            entries = load_flagged()
        except Exception:
            entries = []
        self._flagged_rows: list[_FlagRow] = []

        if not entries:
            self._flag_count_lbl.setText("")
            empty = QLabel(
                "No flagged questions. Use \u2691 Flag for review on the feedback "
                "screen to collect questions you want to revisit."
            )
            empty.setObjectName("muted")
            empty.setWordWrap(True)
            self._flag_slot.addWidget(empty)
            return

        self._flag_count_lbl.setText(f"{len(entries)} flagged")
        for entry in reversed(entries):            # newest first
            row = _FlagRow(entry)
            row.unflag_requested.connect(self._on_unflag)
            self._flag_slot.addWidget(row)
            self._flagged_rows.append(row)

    def _on_unflag(self, flag_id: str) -> None:
        try:
            from persistence import unflag
            unflag(flag_id)
        except Exception:
            pass
        self._render_flagged()

    def flagged_labels(self) -> list[str]:
        """Labels currently shown in the flagged list (newest first)."""
        return [r.label for r in getattr(self, "_flagged_rows", [])]

    def _render(self, sessions: list[dict]) -> None:
        if not sessions:
            self._empty_lbl.show()
            self._trend_frame.hide()
            self._subj_frame.hide()
            self._sessions_card.set_value("0")
            self._questions_card.set_value("0")
            self._avg_card.set_value("—")
            return

        self._empty_lbl.hide()
        self._trend_frame.show()
        self._subj_frame.show()

        total_q = sum(s.get("answered", 0) for s in sessions)
        all_avgs = [s["average_score"] for s in sessions if s.get("answered", 0) > 0]
        lifetime_avg = sum(all_avgs) / len(all_avgs) if all_avgs else 0.0

        self._sessions_card.set_value(str(len(sessions)))
        self._questions_card.set_value(str(total_q))
        self._avg_card.set_value(f"{lifetime_avg:.1f}/10" if all_avgs else "—")

        self._render_trend(sessions)
        self._render_subjects(sessions)

    def _render_trend(self, sessions: list[dict]) -> None:
        _clear_slot(self._trend_slot)
        window = sessions[-30:]
        if not window:
            return

        avgs = [s.get("average_score", 0) for s in window]
        xs = list(range(1, len(avgs) + 1))

        fig, ax = plt.subplots(figsize=(8, 1.8), dpi=96)
        fig.patch.set_facecolor(theme.SURFACE)
        ax.set_facecolor(theme.SURFACE)

        ax.plot(xs, avgs, color=theme.ACCENT, linewidth=2, marker="o",
                markersize=4, markerfacecolor=theme.ACCENT2)
        ax.fill_between(xs, avgs, alpha=0.15, color=theme.ACCENT)
        ax.set_xlim(0.5, max(len(avgs) + 0.5, 5))
        ax.set_ylim(0, 10.5)
        ax.set_ylabel("Avg score", color=theme.TEXT_MUTED, fontsize=9)
        ax.set_xlabel("Session", color=theme.TEXT_MUTED, fontsize=9)
        ax.tick_params(colors=theme.TEXT_MUTED, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(theme.BORDER)
        ax.axhline(7, color=theme.SUCCESS, linewidth=0.8, linestyle="--", alpha=0.5)

        fig.tight_layout(pad=0.4)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setStyleSheet(f"background: {theme.SURFACE};")
        self._trend_slot.addWidget(canvas)
        plt.close(fig)

    def _render_subjects(self, sessions: list[dict]) -> None:
        _clear_slot(self._subj_slot)

        buckets: dict[str, list[int]] = {}
        for s in sessions:
            for r in s.get("records", []):
                subj = r.get("subject", "")
                if subj:
                    buckets.setdefault(subj, []).append(r.get("score", 0))

        if not buckets:
            return

        subjects = list(buckets.keys())
        averages = [sum(v) / len(v) for v in buckets.values()]
        colors   = [theme.subject_color(s) for s in subjects]

        frame_h = max(120, len(subjects) * 38 + 50)
        self._subj_frame.setFixedHeight(frame_h)
        fig_h = frame_h / 96

        fig, ax = plt.subplots(figsize=(8, fig_h), dpi=96)
        fig.patch.set_facecolor(theme.SURFACE)
        ax.set_facecolor(theme.SURFACE)

        bars = ax.barh(subjects, averages, color=colors, height=0.55, edgecolor="none")
        ax.set_xlim(0, 10)
        ax.set_xlabel("Average score", color=theme.TEXT_MUTED, fontsize=9)
        ax.tick_params(colors=theme.TEXT_MUTED, labelsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor(theme.BORDER)
        for bar, avg in zip(bars, averages):
            ax.text(
                avg + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{avg:.1f}", va="center", color=theme.TEXT, fontsize=9
            )

        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setStyleSheet(f"background: {theme.SURFACE};")
        self._subj_slot.addWidget(canvas)
        plt.close(fig)


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


class _FlagRow(QWidget):
    """One flagged question: label, subject/date line, and an Unflag button."""
    unflag_requested = pyqtSignal(str)

    def __init__(self, entry: dict, parent=None) -> None:
        super().__init__(parent)
        self.flag_id = str(entry.get("id", ""))
        self.label = str(entry.get("label") or self.flag_id)
        category = str(entry.get("category") or "")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title = QLabel(self.label)
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 13px;")
        text_col.addWidget(title)

        meta_bits = []
        if category:
            meta_bits.append(category)
        when = _fmt_timestamp(entry.get("timestamp"))
        if when:
            meta_bits.append(when)
        meta = QLabel("  ·  ".join(meta_bits))
        meta.setObjectName("muted")
        text_col.addWidget(meta)
        layout.addLayout(text_col, 1)

        unflag_btn = QPushButton("Unflag")
        unflag_btn.setObjectName("flat")
        unflag_btn.setToolTip("Remove this question from the review list")
        unflag_btn.clicked.connect(lambda: self.unflag_requested.emit(self.flag_id))
        self._unflag_btn = unflag_btn
        layout.addWidget(unflag_btn, 0, Qt.AlignmentFlag.AlignTop)


def _fmt_timestamp(ts) -> str:
    try:
        return datetime.datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def _clear_slot(layout) -> None:
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
