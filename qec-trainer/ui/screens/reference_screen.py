"""Reference / Study screen for qec-trainer.

Displays all problems and their full explanations organized by category,
acting as a browsable cheat-sheet / textbook before taking a quiz.
"""
from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QScrollArea, QFrame, QTextBrowser, QSizePolicy,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from ui import theme

_DOCS_ROOT = Path("/home/matthewscott/Development/Quantum-Computing/docs")

# Maps each problem category to its corresponding documentation file.
# Only categories with an existing doc file are included.
_CATEGORY_DOC: dict[str, Path] = {
    "Repetition Code":     _DOCS_ROOT / "05_quantum_error_correction" / "03_repetition_code.md",
    "Stabilizer Formalism": _DOCS_ROOT / "05_quantum_error_correction" / "04_stabilizer_formalism.md",
    "Steane Code":         _DOCS_ROOT / "05_quantum_error_correction" / "05_css_codes_and_steane.md",
    "Surface Code":        _DOCS_ROOT / "05_quantum_error_correction" / "06_surface_code.md",
    "Fault Tolerance":     _DOCS_ROOT / "05_quantum_error_correction" / "07_fault_tolerance.md",
    "Bosonic Codes":       _DOCS_ROOT / "05_quantum_error_correction" / "08_bosonic_codes.md",
}


class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # list of (category: str, card_widget: QWidget)
        self._cards: list[tuple[str, QWidget]] = []
        self._loaded = False
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ────────────────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setStyleSheet(f"background-color: {theme.SURFACE}; border-bottom: 1px solid {theme.BORDER};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 10, 24, 10)
        top_layout.setSpacing(16)

        title_lbl = QLabel("Reference")
        title_lbl.setObjectName("heading")
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {theme.TEXT};")
        top_layout.addWidget(title_lbl)

        top_layout.addStretch()

        self._cat_filter = QComboBox()
        self._cat_filter.setMinimumWidth(200)
        self._cat_filter.currentTextChanged.connect(self._on_filter_changed)
        top_layout.addWidget(self._cat_filter)

        top_layout.addStretch()

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        top_layout.addWidget(back_btn)

        root.addWidget(top_bar)

        # ── Scroll area ────────────────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(32, 24, 32, 24)
        self._content_layout.setSpacing(16)
        self._content_layout.addStretch()

        self._scroll.setWidget(self._content_widget)
        root.addWidget(self._scroll, 1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> None:
        """Clear and repopulate the scroll area from all_problems()."""
        if self._loaded:
            self._scroll.verticalScrollBar().setValue(0)
            return
        self._loaded = True
        from problems import all_problems

        # Clear existing cards
        self._cards.clear()
        # Remove all widgets from layout (keep the trailing stretch)
        while self._content_layout.count() > 1:
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Populate filter dropdown
        self._cat_filter.blockSignals(True)
        self._cat_filter.clear()
        self._cat_filter.addItem("All Categories")
        seen_cats: list[str] = []

        problems = all_problems()
        for p in problems:
            if p.category not in seen_cats:
                seen_cats.append(p.category)

        for cat in seen_cats:
            self._cat_filter.addItem(cat)
        self._cat_filter.blockSignals(False)

        # Build cards
        for problem in problems:
            card = self._build_card(problem)
            self._content_layout.insertWidget(self._content_layout.count() - 1, card)
            self._cards.append((problem.category, card))

        # Scroll to top
        self._scroll.verticalScrollBar().setValue(0)

    # ------------------------------------------------------------------
    # Card builder
    # ------------------------------------------------------------------

    def _build_card(self, problem) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ── Top meta row ───────────────────────────────────────────────
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        # Category badge
        cat_color = theme.CATEGORY_COLORS.get(problem.category, theme.ACCENT)
        cat_badge = QLabel(problem.category.upper())
        cat_badge.setStyleSheet(
            f"font-size: 10px; font-weight: bold; color: {cat_color};"
            f" background: transparent; padding: 2px 6px;"
            f" border: 1px solid {cat_color}; border-radius: 3px;"
        )
        meta_row.addWidget(cat_badge)

        # Difficulty badge
        diff_color = {
            "beginner":     theme.SUCCESS,
            "intermediate": theme.WARNING,
            "advanced":     theme.ERROR,
        }.get(problem.difficulty, theme.TEXT_MUTED)
        diff_badge = QLabel(problem.difficulty.capitalize())
        diff_badge.setStyleSheet(
            f"font-size: 10px; color: {diff_color};"
            f" background: transparent; padding: 2px 6px;"
            f" border: 1px solid {diff_color}; border-radius: 3px;"
        )
        meta_row.addWidget(diff_badge)

        # Grade mode badge
        mode_label = problem.grade_mode.value.upper()
        mode_badge = QLabel(mode_label)
        mode_badge.setStyleSheet(
            f"font-size: 10px; color: {theme.TEXT_MUTED};"
            f" background: transparent; padding: 2px 6px;"
            f" border: 1px solid {theme.BORDER}; border-radius: 3px;"
        )
        meta_row.addWidget(mode_badge)

        # "Read more" doc link — only shown when a matching doc exists
        doc_path = _CATEGORY_DOC.get(problem.category)
        if doc_path and doc_path.exists():
            read_more_btn = QPushButton("📖 Read more in docs")
            read_more_btn.setObjectName("flat")
            read_more_btn.setStyleSheet(
                f"font-size: 10px; color: {theme.ACCENT}; background: transparent;"
                f" border: none; padding: 2px 4px; text-align: left;"
            )
            read_more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            _path = str(doc_path.resolve())
            read_more_btn.clicked.connect(
                lambda _checked, p=_path: QDesktopServices.openUrl(QUrl.fromLocalFile(p))
            )
            meta_row.addWidget(read_more_btn)

        meta_row.addStretch()
        layout.addLayout(meta_row)

        # ── Question text ──────────────────────────────────────────────
        q_lbl = QLabel(problem.question)
        q_lbl.setWordWrap(True)
        q_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {theme.TEXT};")
        layout.addWidget(q_lbl)

        # ── Separator ─────────────────────────────────────────────────
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # ── Answer / Explanation ───────────────────────────────────────
        if problem.choices and problem.correct_index >= 0:
            correct_text = problem.choices[problem.correct_index]
            ans_lbl = QLabel(f"✓ Answer: {correct_text}")
            ans_lbl.setWordWrap(True)
            ans_lbl.setStyleSheet(f"font-size: 13px; color: {theme.SUCCESS}; font-weight: bold;")
            layout.addWidget(ans_lbl)

        if problem.explanation:
            exp_browser = QTextBrowser()
            exp_browser.setPlainText(problem.explanation)
            exp_browser.setReadOnly(True)
            # Size to content, with a reasonable max
            exp_browser.document().setDocumentMargin(0)
            exp_browser.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            exp_browser.setMaximumHeight(220)
            layout.addWidget(exp_browser)

        return card

    # ------------------------------------------------------------------
    # Filter logic
    # ------------------------------------------------------------------

    def _on_filter_changed(self, text: str) -> None:
        show_all = (text == "All Categories")
        for cat, widget in self._cards:
            widget.setVisible(show_all or cat == text)
