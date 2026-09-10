"""History screen for exam-sim — past attempts, per-section accuracy, score trend.

Reads ``exam_history.json`` through ``persistence.load_history()``; the file's
schema is owned by persistence.py and shared with the coach/dashboard, so this
screen is strictly read-only.
"""
from __future__ import annotations
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from config import SECTIONS, EXAM_QUESTION_COUNT, PASS_MARK, section_weight, pass_mark_for
from persistence import load_history
from ui import theme

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.ticker import MaxNLocator
    HAVE_MPL = True
except Exception:  # matplotlib is optional at runtime — tables still work without it
    HAVE_MPL = False

# Series colours validated as a categorical pair on the dark SURFACE
# (OKLCH band, CVD separation, contrast). Marker shape is the secondary encoding.
FULL_COLOR   = theme.ACCENT2      # full exams
SPRINT_COLOR = "#db6d28"          # sprints
PASS_PCT     = 100.0 * PASS_MARK / EXAM_QUESTION_COUNT
_MAX_VISIBLE_ROWS = 12


# ---------------------------------------------------------------- pure helpers
def _fmt_duration(secs: float) -> str:
    secs = max(0, int(secs or 0))
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m:02d}m" if h else f"{m}m {s:02d}s"


def _mode_label(entry: dict) -> str:
    if entry.get("mode") == "full":
        return "Full exam"
    sections = entry.get("sections") or {}
    if len(sections) == 1:
        return f"Sprint · {next(iter(sections))}"
    return "Sprint"


def attempt_rows(history: list[dict]) -> list[dict]:
    """Newest-first table rows derived from raw history entries."""
    rows = []
    for e in sorted(history, key=lambda e: e.get("timestamp", 0), reverse=True):
        total = int(e.get("total", 0) or 0)
        correct = int(e.get("correct", 0) or 0)
        need = pass_mark_for(total) if total else 0
        rows.append({
            "date":     time.strftime("%Y-%m-%d %H:%M", time.localtime(e.get("timestamp", 0))),
            "mode":     _mode_label(e),
            "is_full":  e.get("mode") == "full",
            "score":    f"{correct}/{total}",
            "pct":      100.0 * correct / total if total else 0.0,
            "passed":   total > 0 and correct >= need,
            "need":     need,
            "total":    total,
            "duration": _fmt_duration(e.get("duration_secs", 0)),
        })
    return rows


def section_totals(history: list[dict]) -> dict[str, dict[str, int]]:
    """Per-section {total, correct} aggregated over *full* exams only, in exam order."""
    agg: dict[str, dict[str, int]] = {}
    for e in history:
        if e.get("mode") != "full":
            continue
        for name, bucket in (e.get("sections") or {}).items():
            b = agg.setdefault(name, {"total": 0, "correct": 0})
            b["total"] += int(bucket.get("total", 0) or 0)
            b["correct"] += int(bucket.get("correct", 0) or 0)
    ordered = {s: agg[s] for s in SECTIONS if s in agg}
    ordered.update({s: agg[s] for s in agg if s not in SECTIONS})
    return ordered


def trend_series(history: list[dict]) -> dict[str, tuple[list[int], list[float]]]:
    """Chronological (x = attempt number, y = score %) per mode.

    Entries with ``total == 0`` (never written by the app, but tolerated) are
    skipped *and not counted*, so x runs 1..n over the plotted points only and
    the last point always sits inside the chart's x-range.
    """
    out: dict[str, tuple[list[int], list[float]]] = {"full": ([], []), "sprint": ([], [])}
    attempt = 0
    for e in sorted(history, key=lambda e: e.get("timestamp", 0)):
        total = int(e.get("total", 0) or 0)
        if not total:
            continue
        attempt += 1
        mode = "full" if e.get("mode") == "full" else "sprint"
        out[mode][0].append(attempt)
        out[mode][1].append(100.0 * int(e.get("correct", 0) or 0) / total)
    return out


# ---------------------------------------------------------------------- screen
class HistoryScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._canvas = None
        self._build_ui()

    # ------------------------------------------------------------------ UI
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
        root.setContentsMargins(48, 36, 48, 24)
        root.setSpacing(18)
        scroll.setWidget(content)

        title = QLabel("Exam History")
        title.setObjectName("heading")
        root.addWidget(title)
        self._sub_lbl = QLabel("")
        self._sub_lbl.setObjectName("subheading")
        self._sub_lbl.setWordWrap(True)
        root.addWidget(self._sub_lbl)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        cards_row = QHBoxLayout(); cards_row.setSpacing(16)
        self._sessions_card = _StatCard("Sessions", "0")
        self._full_card     = _StatCard("Full exams", "0")
        self._best_card     = _StatCard("Best full score", "—")
        self._pass_card     = _StatCard("Full-exam pass rate", "—")
        for c in (self._sessions_card, self._full_card, self._best_card, self._pass_card):
            cards_row.addWidget(c)
        root.addLayout(cards_row)

        self._empty_lbl = QLabel(
            "No sessions recorded yet — finish a full exam or a sprint and it will show up here.")
        self._empty_lbl.setObjectName("subheading")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._empty_lbl)

        # --- score trend -------------------------------------------------
        self._trend_lbl = _section_label("SCORE TREND — every attempt, chronological")
        root.addWidget(self._trend_lbl)
        self._trend_frame = QFrame(); self._trend_frame.setObjectName("card")
        self._trend_frame.setFixedHeight(270)
        trend_inner = QVBoxLayout(self._trend_frame)
        trend_inner.setContentsMargins(6, 6, 6, 6)
        self._trend_slot = trend_inner
        root.addWidget(self._trend_frame)

        # --- attempts table ----------------------------------------------
        self._attempts_lbl = _section_label("PAST ATTEMPTS — newest first")
        root.addWidget(self._attempts_lbl)
        self._attempts_table = _make_table(["Date", "Mode", "Score", "Result", "Duration"])
        root.addWidget(self._attempts_table)

        # --- per-section table ------------------------------------------
        self._section_lbl = _section_label("PER-SECTION ACCURACY — aggregated over full exams")
        root.addWidget(self._section_lbl)
        self._section_note = QLabel(
            "No full exams recorded yet — sprints are excluded from this table because "
            "they only sample one section.")
        self._section_note.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        self._section_note.setWordWrap(True)
        root.addWidget(self._section_note)
        self._section_table = _make_table(["Section", "Correct", "Accuracy", "Exam weight"])
        root.addWidget(self._section_table)

        root.addStretch()

        bar = QWidget()
        bar.setObjectName("bottombar")   # scoped selector: children keep their own styling
        bar.setStyleSheet(
            f"QWidget#bottombar {{ background: {theme.SURFACE};"
            f" border-top: 1px solid {theme.BORDER}; }}")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(48, 12, 48, 12)
        bar_layout.addStretch()
        back_btn = QPushButton("← Back to Home")
        back_btn.setObjectName("accent")
        back_btn.clicked.connect(self.back_requested)
        bar_layout.addWidget(back_btn)
        outer.addWidget(bar)

    # ------------------------------------------------------------ public
    def refresh(self) -> None:
        self.render_history(load_history())

    def render_history(self, history: list[dict]) -> None:
        """Populate every widget from a raw exam_history.json list."""
        rows = attempt_rows(history)
        has_any = bool(rows)
        self._empty_lbl.setVisible(not has_any)
        for w in (self._trend_lbl, self._trend_frame, self._attempts_lbl, self._attempts_table,
                  self._section_lbl):
            w.setVisible(has_any)

        full_rows = [r for r in rows if r["is_full"]]
        self._sessions_card.set_value(str(len(rows)))
        self._full_card.set_value(str(len(full_rows)))
        if full_rows:
            best = max(full_rows, key=lambda r: r["pct"])
            self._best_card.set_value(best["score"])
            passed = sum(1 for r in full_rows if r["passed"])
            self._pass_card.set_value(f"{passed}/{len(full_rows)} passed")
        else:
            self._best_card.set_value("—")
            self._pass_card.set_value("—")

        if not has_any:
            self._sub_lbl.setText(
                f"Pass mark is {PASS_MARK}/{EXAM_QUESTION_COUNT} ({PASS_PCT:.0f}%); "
                "sprints are judged against the same ratio.")
            self._section_note.setVisible(False)
            self._section_table.setVisible(False)
            return

        newest = rows[0]
        # Lower-case only the leading word ("full exam", "sprint · OpenQASM") so
        # the section name keeps its casing mid-sentence.
        mode = newest["mode"][:1].lower() + newest["mode"][1:]
        self._sub_lbl.setText(
            f"{len(rows)} session{'s' if len(rows) != 1 else ''} on file — most recent: "
            f"{mode} {newest['score']} on {newest['date']}. "
            f"Pass mark is {PASS_MARK}/{EXAM_QUESTION_COUNT} ({PASS_PCT:.0f}%); "
            "sprints are judged against the same ratio.")

        self._fill_attempts(rows)
        self._fill_sections(section_totals(history))
        self._draw_trend(history)

    # ------------------------------------------------------------ tables
    def _fill_attempts(self, rows: list[dict]) -> None:
        t = self._attempts_table
        t.setRowCount(len(rows))
        for r, row in enumerate(rows):
            verdict = "PASS" if row["passed"] else "FAIL"
            items = [
                QTableWidgetItem(row["date"]),
                QTableWidgetItem(row["mode"]),
                QTableWidgetItem(f"{row['score']}  ({row['pct']:.0f}%)"),
                QTableWidgetItem(verdict),
                QTableWidgetItem(row["duration"]),
            ]
            items[3].setForeground(QColor(theme.SUCCESS if row["passed"] else theme.ERROR))
            items[3].setToolTip(f"pass mark {row['need']}/{row['total']}")
            for c, item in enumerate(items):
                if c >= 2:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                t.setItem(r, c, item)
        _fit_table_height(t)

    def _fill_sections(self, totals: dict[str, dict[str, int]]) -> None:
        t = self._section_table
        has_full = bool(totals)
        self._section_note.setVisible(not has_full)
        t.setVisible(has_full)
        t.setRowCount(len(totals))
        for r, (section, b) in enumerate(totals.items()):
            pct = 100.0 * b["correct"] / b["total"] if b["total"] else 0.0
            items = [
                QTableWidgetItem(section),
                QTableWidgetItem(f"{b['correct']}/{b['total']}"),
                QTableWidgetItem(f"{pct:.0f}%"),
                QTableWidgetItem(f"{100.0 * section_weight(section):.0f}%"),
            ]
            # status colour: at/above the pass ratio is on track, below needs work
            items[2].setForeground(QColor(theme.SUCCESS if pct >= PASS_PCT else theme.WARNING))
            items[2].setToolTip(f"pass ratio {PASS_PCT:.0f}%")
            for c, item in enumerate(items):
                if c:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                t.setItem(r, c, item)
        _fit_table_height(t)

    # ------------------------------------------------------------- chart
    def _draw_trend(self, history: list[dict]) -> None:
        _clear_slot(self._trend_slot)
        self._canvas = None
        if not HAVE_MPL:
            lbl = QLabel("Install matplotlib>=3.8 (see requirements.txt) to see the score trend.")
            lbl.setStyleSheet(f"color: {theme.TEXT_MUTED};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._trend_slot.addWidget(lbl)
            return

        series = trend_series(history)
        n_points = sum(len(xs) for xs, _ in series.values())
        fig = Figure(figsize=(8, 2.6), dpi=96)
        fig.patch.set_facecolor(theme.SURFACE)
        ax = fig.add_subplot(111)
        ax.set_facecolor(theme.SURFACE)

        spec = {
            "full":   ("Full exam", FULL_COLOR, "o"),
            "sprint": ("Sprint", SPRINT_COLOR, "D"),
        }
        endpoints = []
        for mode, (label, color, marker) in spec.items():
            xs, ys = series[mode]
            if not xs:
                continue
            ax.plot(xs, ys, color=color, linewidth=2, solid_capstyle="round",
                    solid_joinstyle="round", marker=marker, markersize=6,
                    markerfacecolor=color, markeredgecolor=theme.SURFACE,
                    markeredgewidth=1.5, label=label, zorder=3)
            endpoints.append((xs[-1], ys[-1]))

        # pass threshold — muted, labelled at the right edge
        ax.axhline(PASS_PCT, color=theme.TEXT_MUTED, linewidth=1, linestyle=(0, (4, 3)),
                   zorder=2)
        x_max = max(n_points + 0.5, 5.5)
        ax.text(x_max, PASS_PCT + 1.5, f"pass mark {PASS_PCT:.0f}%", ha="right", va="bottom",
                fontsize=8, color=theme.TEXT_MUTED)

        # selective direct labels: the endpoint of each series only
        if len(endpoints) == 2 and abs(endpoints[0][1] - endpoints[1][1]) < 9:
            vas = ["bottom", "top"] if endpoints[0][1] >= endpoints[1][1] else ["top", "bottom"]
        else:
            vas = ["center"] * len(endpoints)
        for (x, y), va in zip(endpoints, vas):
            ax.annotate(f"{y:.0f}%", (x, y), xytext=(7, 0), textcoords="offset points",
                        ha="left", va=va, fontsize=9, color=theme.TEXT)

        ax.set_xlim(0.5, x_max + 0.6)
        ax.set_ylim(0, 104)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=12))
        ax.set_ylabel("Score %", color=theme.TEXT_MUTED, fontsize=9)
        ax.set_xlabel("Attempt", color=theme.TEXT_MUTED, fontsize=9)
        ax.tick_params(colors=theme.TEXT_MUTED, labelsize=8, length=0)
        ax.grid(axis="y", color=theme.BORDER, linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_edgecolor(theme.BORDER)
        if len(endpoints) == 2:
            leg = ax.legend(loc="lower left", frameon=False, fontsize=9, ncols=2,
                            handlelength=1.6, borderaxespad=0.2)
            for txt in leg.get_texts():
                txt.set_color(theme.TEXT)
        fig.tight_layout(pad=0.6)

        canvas = FigureCanvasQTAgg(fig)
        canvas.setStyleSheet(f"background: {theme.SURFACE};")
        self._trend_slot.addWidget(canvas)
        self._canvas = canvas


# --------------------------------------------------------------------- widgets
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
        self._val.setStyleSheet("font-size: 24px; font-weight: bold;")
        self._val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._val)

    def set_value(self, v: str) -> None:
        self._val.setText(v)

    def value(self) -> str:
        return self._val.text()


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
    return lbl


def _make_table(headers: list[str]) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.verticalHeader().setDefaultSectionSize(30)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    t.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    for c in range(1, len(headers)):
        t.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
    t.horizontalHeader().setStretchLastSection(False)
    return t


def _fit_table_height(t: QTableWidget) -> None:
    rows = min(t.rowCount(), _MAX_VISIBLE_ROWS)
    header_h = t.horizontalHeader().sizeHint().height()
    t.setFixedHeight(header_h + rows * t.verticalHeader().defaultSectionSize() + 4)


def _clear_slot(layout) -> None:
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
