"""Reference screen for circuit-trainer — an in-app browser for the shared docs corpus.

Ported from qec-trainer/ui/screens/reference_screen.py.  circuit-trainer has no
static problem bank (every problem is generated fresh by Qiskit), so instead of
listing problem cards this screen renders the repo-level ``docs/**/*.md``
chapters directly: a chapter list on the left, the rendered Markdown on the
right, plus a "Jump to category" picker that opens the chapter most relevant to
each trainer category.

The docs root is resolved relative to this file (``parents[3] / "docs"``), never
from a hardcoded home path.
"""
from __future__ import annotations

import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QListWidget, QListWidgetItem, QTextBrowser, QSplitter, QFrame,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QTextDocument, QColor, QFont

from ui import theme

_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"

# Maps each trainer category (ProblemCategory.value) to the docs chapter that
# best covers it.  Only entries whose file exists are offered in the picker.
_CATEGORY_DOC: dict[str, Path] = {
    "Single-gate output":           _DOCS_ROOT / "03_quantum_gates_and_circuits" / "01_single_qubit_gates.md",
    "Gate sequence":                _DOCS_ROOT / "03_quantum_gates_and_circuits" / "01_single_qubit_gates.md",
    "Measurement probabilities":    _DOCS_ROOT / "02_quantum_mechanics" / "03_quantum_measurements.md",
    "Gate / matrix identification": _DOCS_ROOT / "03_quantum_gates_and_circuits" / "01_single_qubit_gates.md",
    "Circuit unitary":              _DOCS_ROOT / "03_quantum_gates_and_circuits" / "03_circuit_model_and_universality.md",
    "Entanglement detection":       _DOCS_ROOT / "02_quantum_mechanics" / "04_entanglement_and_nonlocality.md",
    "Multi-qubit circuit output":   _DOCS_ROOT / "03_quantum_gates_and_circuits" / "02_multi_qubit_gates.md",
    "Circuit equivalence":          _DOCS_ROOT / "03_quantum_gates_and_circuits" / "03_circuit_model_and_universality.md",
    "Notation reading":             _DOCS_ROOT / "01_mathematical_foundations" / "01_linear_algebra.md",
    "Circuit composition":          _DOCS_ROOT / "03_quantum_gates_and_circuits" / "02_multi_qubit_gates.md",
    "Noise channel":                _DOCS_ROOT / "02_quantum_mechanics" / "05_density_matrices_and_open_systems.md",
    "Circuit explanation":          _DOCS_ROOT / "03_quantum_gates_and_circuits" / "03_circuit_model_and_universality.md",
}

_ROLE_PATH = Qt.ItemDataRole.UserRole


def docs_root() -> Path:
    """The resolved docs directory (exposed for tests / diagnostics)."""
    return _DOCS_ROOT


def _section_title(dirname: str) -> str:
    """'03_quantum_gates_and_circuits' -> 'Chapter 3: Quantum Gates and Circuits'."""
    m = re.match(r"^(\d+)_(.*)$", dirname)
    if not m:
        return dirname.replace("_", " ").title()
    num, rest = m.groups()
    words = rest.replace("_", " ").split()
    small = {"and", "of", "the", "in", "to"}
    pretty = " ".join(
        w if (i and w in small) else w.capitalize() for i, w in enumerate(words)
    )
    return f"Chapter {int(num)}: {pretty}"


def _chapter_title(path: Path) -> str:
    """First '# ' heading of the file, else a prettified filename."""
    try:
        with path.open(encoding="utf-8") as fh:
            for _ in range(40):
                line = fh.readline()
                if not line:
                    break
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    stem = re.sub(r"^\d+_", "", path.stem)
    return stem.replace("_", " ").title()


def scan_docs(root: Path | None = None) -> list[tuple[str, list[Path]]]:
    """Return [(section_title, [chapter paths...])] for every docs/**/*.md.

    Top-level files (e.g. docs/README.md) are grouped under 'Overview'.
    """
    root = root or _DOCS_ROOT
    if not root.is_dir():
        return []
    sections: list[tuple[str, list[Path]]] = []
    top_level = sorted(p for p in root.glob("*.md") if p.is_file())
    if top_level:
        sections.append(("Overview", top_level))
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        files = sorted(p for p in d.rglob("*.md") if p.is_file())
        if files:
            sections.append((_section_title(d.name), files))
    return sections


class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._loaded = False
        self._current: Path | None = None
        self._items_by_path: dict[Path, QListWidgetItem] = {}
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
        top_bar.setStyleSheet(
            f"background-color: {theme.SURFACE}; border-bottom: 1px solid {theme.BORDER};"
        )
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 10, 24, 10)
        top_layout.setSpacing(16)

        title_lbl = QLabel("Reference")
        title_lbl.setObjectName("heading")
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {theme.TEXT};")
        top_layout.addWidget(title_lbl)

        self._path_lbl = QLabel("")
        self._path_lbl.setObjectName("muted")
        top_layout.addWidget(self._path_lbl)

        top_layout.addStretch()

        self._cat_picker = QComboBox()
        self._cat_picker.setMinimumWidth(240)
        self._cat_picker.addItem("Jump to category…", None)
        for cat, path in _CATEGORY_DOC.items():
            if path.exists():
                self._cat_picker.addItem(cat, str(path))
        self._cat_picker.activated.connect(self._on_category_picked)
        top_layout.addWidget(self._cat_picker)

        self._open_btn = QPushButton("Open externally")
        self._open_btn.setObjectName("flat")
        self._open_btn.setToolTip("Open the current chapter in your system Markdown viewer")
        self._open_btn.clicked.connect(self._open_external)
        self._open_btn.setEnabled(False)
        top_layout.addWidget(self._open_btn)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        top_layout.addWidget(back_btn)

        root.addWidget(top_bar)

        # ── Body: chapter list | rendered doc ──────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        self._list = QListWidget()
        self._list.setMinimumWidth(240)
        self._list.setStyleSheet(
            f"QListWidget {{ background: {theme.SURFACE}; border: none;"
            f" border-right: 1px solid {theme.BORDER}; outline: none; }}"
            f"QListWidget::item {{ padding: 6px 12px; color: {theme.TEXT}; }}"
            f"QListWidget::item:selected {{ background: {theme.ACCENT2}; color: white; }}"
            f"QListWidget::item:hover {{ background: {theme.SURFACE2}; }}"
        )
        self._list.currentItemChanged.connect(self._on_item_changed)
        splitter.addWidget(self._list)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)          # we route links ourselves
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(self._on_anchor_clicked)
        self._browser.setStyleSheet(
            f"QTextBrowser {{ background: {theme.BG}; color: {theme.TEXT};"
            f" border: none; padding: 24px 32px; font-size: 15px; }}"
        )
        self._browser.document().setDefaultStyleSheet(
            f"h1 {{ color: {theme.TEXT}; }}"
            f"h2, h3, h4 {{ color: {theme.ACCENT}; }}"
            f"a {{ color: {theme.ACCENT}; }}"
            f"code {{ font-family: 'JetBrains Mono','Fira Code','Consolas',monospace;"
            f" color: {theme.TEAL}; }}"
            f"pre {{ font-family: 'JetBrains Mono','Fira Code','Consolas',monospace;"
            f" background: {theme.SURFACE}; }}"
            f"blockquote {{ color: {theme.TEXT_MUTED}; }}"
            f"th {{ color: {theme.TEXT_MUTED}; }}"
        )
        right_layout.addWidget(self._browser, 1)

        self._empty_lbl = QLabel("")
        self._empty_lbl.setObjectName("subheading")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setWordWrap(True)
        self._empty_lbl.hide()
        right_layout.addWidget(self._empty_lbl)

        splitter.addWidget(right)
        splitter.setSizes([300, 900])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> None:
        """Populate the chapter list from docs/**/*.md (once) and show a chapter."""
        if self._loaded:
            self._browser.verticalScrollBar().setValue(0)
            return
        self._loaded = True
        self._list.blockSignals(True)
        self._list.clear()
        self._items_by_path.clear()

        sections = scan_docs()
        for section_title, files in sections:
            header = QListWidgetItem(section_title)
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            header.setForeground(QColor(theme.TEXT_MUTED))
            font = QFont()
            font.setBold(True)
            font.setPointSize(9)
            header.setFont(font)
            self._list.addItem(header)
            for path in files:
                item = QListWidgetItem("    " + _chapter_title(path))
                item.setData(_ROLE_PATH, str(path))
                item.setToolTip(str(path.relative_to(_DOCS_ROOT)))
                self._list.addItem(item)
                self._items_by_path[path] = item
        self._list.blockSignals(False)

        if not self._items_by_path:
            self._browser.hide()
            self._empty_lbl.setText(
                f"No documentation found.\nExpected Markdown chapters under:\n{_DOCS_ROOT}"
            )
            self._empty_lbl.show()
            return

        # Prefer the docs README as the landing page, else the first chapter.
        readme = _DOCS_ROOT / "README.md"
        first = readme if readme in self._items_by_path else next(iter(self._items_by_path))
        self.show_doc(first)

    def show_doc(self, path: Path | str) -> bool:
        """Render one Markdown file. Returns False if it cannot be read."""
        path = Path(path)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            self._browser.setPlainText(f"Could not read {path}:\n{exc}")
            self._current = None
            self._open_btn.setEnabled(False)
            return False

        self._current = path
        doc = self._browser.document()
        doc.setBaseUrl(QUrl.fromLocalFile(str(path.parent) + "/"))
        doc.setMarkdown(text, QTextDocument.MarkdownFeature.MarkdownDialectGitHub)
        self._browser.verticalScrollBar().setValue(0)
        self._browser.show()
        self._empty_lbl.hide()
        self._open_btn.setEnabled(True)
        try:
            self._path_lbl.setText(str(path.relative_to(_DOCS_ROOT)))
        except ValueError:
            self._path_lbl.setText(path.name)

        item = self._items_by_path.get(path)
        if item is not None and self._list.currentItem() is not item:
            self._list.blockSignals(True)
            self._list.setCurrentItem(item)
            self._list.blockSignals(False)
        return True

    def show_category(self, category_value: str) -> bool:
        """Open the chapter mapped to a trainer category (ProblemCategory.value)."""
        if not self._loaded:
            self.load_all()
        path = _CATEGORY_DOC.get(category_value)
        if path is None or not path.exists():
            return False
        return self.show_doc(path)

    def current_doc(self) -> Path | None:
        return self._current

    def chapter_count(self) -> int:
        return len(self._items_by_path)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _on_item_changed(self, current: QListWidgetItem | None, _prev) -> None:
        if current is None:
            return
        raw = current.data(_ROLE_PATH)
        if raw:
            self.show_doc(Path(raw))

    def _on_category_picked(self, index: int) -> None:
        raw = self._cat_picker.itemData(index)
        if raw:
            self.show_doc(Path(raw))
        self._cat_picker.setCurrentIndex(0)

    def _on_anchor_clicked(self, url: QUrl) -> None:
        scheme = url.scheme()
        if scheme in ("http", "https", "mailto"):
            QDesktopServices.openUrl(url)
            return
        # Fragment-only link: scroll within the current document.
        if not url.path() and url.hasFragment():
            self._browser.scrollToAnchor(url.fragment())
            return
        # Relative / local link to another Markdown chapter.
        if url.isLocalFile():
            target = Path(url.toLocalFile())
        else:
            base = self._current.parent if self._current else _DOCS_ROOT
            target = (base / url.path()).resolve()
        if target.suffix.lower() == ".md" and target.exists():
            self.show_doc(target)
            if url.hasFragment():
                self._browser.scrollToAnchor(url.fragment())
        elif target.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _open_external(self) -> None:
        if self._current is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._current.resolve())))
