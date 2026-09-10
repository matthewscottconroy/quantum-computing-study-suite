"""Reference screen — in-app browser for the shared ``docs/`` corpus.

Ported from qec-trainer's reference screen (the suite's canonical in-app docs
browser) and adapted to paper-drill's theme.  The docs root is resolved
relative to this file — paper-drill/ui/screens/ → repository root / docs — so
the app works from any checkout location; nothing here hardcodes a home path.

Layout: a top bar (title, chapter filter, search, Back) over a splitter with
a chapter → document tree on the left and a markdown reading pane on the
right.  Every ``docs/**/*.md`` file is listed; a chapter is a sub-directory.
"""
from __future__ import annotations
import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QTextBrowser, QSplitter,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from ui import theme

_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"

_OVERVIEW_CHAPTER = "Overview"

# ``<details><summary>Solution</summary> … </details>`` blocks are what the docs
# use for exercise solutions.  Qt's markdown importer flattens the tags and
# runs the summary into the body, so rewrite them as a bold lead-in instead.
_DETAILS_OPEN  = re.compile(r"<details>\s*<summary>(.*?)</summary>", re.IGNORECASE | re.DOTALL)
_DETAILS_CLOSE = re.compile(r"</details>", re.IGNORECASE)
_DIR_PREFIX    = re.compile(r"^(\d+)[_\-\s]*(.*)$")

# Title-casing for directory / file stems: joining words stay lowercase and
# common quantum-computing initialisms keep their capitals ("qec" -> "QEC").
_SMALL_WORDS = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on",
                "or", "the", "to", "vs", "with"}
_ACRONYMS    = {"qec", "qft", "qpe", "qaoa", "vqe", "vqa", "nisq", "ibm",
                "qkd", "qml", "qram", "css", "ldpc", "cnot", "swap"}


def docs_root() -> Path:
    """The resolved docs directory (exposed for tests and diagnostics)."""
    return _DOCS_ROOT


def _title_words(text: str) -> str:
    """'quantum_gates_and_circuits' → 'Quantum Gates and Circuits'."""
    words = text.replace("_", " ").replace("-", " ").split()
    out: list[str] = []
    for i, word in enumerate(words):
        lower = word.lower()
        if lower in _ACRONYMS:
            out.append(lower.upper())
        elif i > 0 and lower in _SMALL_WORDS:
            out.append(lower)
        else:
            out.append(word[:1].upper() + word[1:])
    return " ".join(out)


def _prettify_dir(name: str) -> str:
    """'05_quantum_error_correction' → '05 · Quantum Error Correction'."""
    m = _DIR_PREFIX.match(name)
    num, rest = (m.group(1), m.group(2)) if m else ("", name)
    words = _title_words(rest)
    return f"{num} · {words}" if num and words else (words or name)


def _doc_title(path: Path) -> str:
    """First ``# `` heading in the file, else a prettified file stem."""
    try:
        with path.open(encoding="utf-8") as fh:
            for _ in range(40):
                line = fh.readline()
                if not line:
                    break
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    m = _DIR_PREFIX.match(path.stem)
    stem = m.group(2) if m else path.stem
    return _title_words(stem) or path.name


def _preprocess(markdown: str) -> str:
    """Make the docs' HTML details blocks readable in QTextBrowser."""
    markdown = _DETAILS_OPEN.sub(
        lambda m: f"\n\n**{(m.group(1).strip() or 'Solution')}.**\n\n", markdown
    )
    return _DETAILS_CLOSE.sub("\n", markdown)


def scan_docs(root: Path = _DOCS_ROOT) -> list[tuple[str, str, Path]]:
    """Return (chapter, title, path) for every ``*.md`` under ``root``.

    Ladder order: files directly in the root (docs/README.md, filed under
    'Overview') come first, then chapter directories and the files inside
    them sorted by their numbered prefixes.
    """
    if not root.is_dir():
        return []

    def _order(path: Path) -> tuple[bool, tuple[str, ...]]:
        rel = path.relative_to(root)
        return (len(rel.parts) > 1, rel.parts)

    entries: list[tuple[str, str, Path]] = []
    for path in sorted(root.rglob("*.md"), key=_order):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        chapter = _OVERVIEW_CHAPTER if len(rel.parts) == 1 else _prettify_dir(rel.parts[0])
        entries.append((chapter, _doc_title(path), path))
    return entries


class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._loaded = False
        self._current: Path | None = None
        # chapter title -> tree item; doc path -> tree item
        self._chapter_items: dict[str, QTreeWidgetItem] = {}
        self._doc_items: dict[Path, QTreeWidgetItem] = {}
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

        top_layout.addStretch()

        self._chapter_filter = QComboBox()
        self._chapter_filter.setMinimumWidth(220)
        self._chapter_filter.currentTextChanged.connect(self._apply_filters)
        top_layout.addWidget(self._chapter_filter)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search titles…")
        self._search.setClearButtonEnabled(True)
        self._search.setMinimumWidth(200)
        self._search.textChanged.connect(self._apply_filters)
        top_layout.addWidget(self._search)

        top_layout.addStretch()

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        top_layout.addWidget(back_btn)

        root.addWidget(top_bar)

        # ── Body: tree | reading pane ──────────────────────────────────
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 16, 24, 16)
        body_layout.setSpacing(8)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(14)
        self._tree.setMinimumWidth(220)
        self._tree.currentItemChanged.connect(self._on_tree_selection)
        self._splitter.addWidget(self._tree)

        pane = QWidget()
        pane_layout = QVBoxLayout(pane)
        pane_layout.setContentsMargins(0, 0, 0, 0)
        pane_layout.setSpacing(6)

        self._path_lbl = QLabel("")
        self._path_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        self._path_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        pane_layout.addWidget(self._path_lbl)

        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(self._on_anchor_clicked)
        self._browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {theme.SURFACE}; color: {theme.TEXT};"
            f" border: 1px solid {theme.BORDER}; border-radius: 8px;"
            f" padding: 12px; font-size: 14px; }}"
        )
        pane_layout.addWidget(self._browser, 1)

        self._splitter.addWidget(pane)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([280, 700])
        body_layout.addWidget(self._splitter, 1)

        root.addWidget(body, 1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> None:
        """Scan the docs tree on first use; later calls just re-show it."""
        if self._loaded:
            return
        self._loaded = True

        entries = scan_docs()
        self._tree.blockSignals(True)
        self._chapter_filter.blockSignals(True)
        self._tree.clear()
        self._chapter_items.clear()
        self._doc_items.clear()
        self._chapter_filter.clear()
        self._chapter_filter.addItem("All Chapters")

        for chapter, title, path in entries:
            parent = self._chapter_items.get(chapter)
            if parent is None:
                parent = QTreeWidgetItem([chapter])
                parent.setFlags(parent.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                font = parent.font(0)
                font.setBold(True)
                parent.setFont(0, font)
                self._tree.addTopLevelItem(parent)
                self._chapter_items[chapter] = parent
                self._chapter_filter.addItem(chapter)
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, str(path))
            item.setToolTip(0, str(path.relative_to(_DOCS_ROOT)))
            parent.addChild(item)
            self._doc_items[path] = item

        self._tree.expandAll()
        self._chapter_filter.blockSignals(False)
        self._tree.blockSignals(False)

        if not entries:
            self._path_lbl.setText("")
            self._browser.setMarkdown(
                f"# Docs not found\n\nExpected the shared documentation folder at:\n\n"
                f"`{_DOCS_ROOT}`\n\nRun paper-drill from inside the Quantum-Computing "
                f"checkout so the `docs/` corpus can be located."
            )
            return

        # Land on the ladder overview if present, otherwise the first doc.
        first = _DOCS_ROOT / "README.md"
        if first not in self._doc_items:
            first = entries[0][2]
        self.open_doc(first)

    def open_doc(self, path: Path) -> bool:
        """Render ``path`` in the reading pane and select it in the tree."""
        path = Path(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return False
        self._current = path
        try:
            shown = path.relative_to(_DOCS_ROOT)
        except ValueError:
            shown = path
        self._path_lbl.setText(f"docs / {' / '.join(shown.parts)}")
        self._browser.setMarkdown(_preprocess(text))
        self._browser.verticalScrollBar().setValue(0)

        item = self._doc_items.get(path)
        if item is not None and self._tree.currentItem() is not item:
            self._tree.blockSignals(True)
            self._tree.setCurrentItem(item)
            self._tree.blockSignals(False)
        return True

    def current_doc(self) -> Path | None:
        return self._current

    def doc_count(self) -> int:
        return len(self._doc_items)

    def visible_doc_count(self) -> int:
        return sum(1 for it in self._doc_items.values() if not it.isHidden())

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_tree_selection(self, current: QTreeWidgetItem | None, _previous=None) -> None:
        if current is None:
            return
        raw = current.data(0, Qt.ItemDataRole.UserRole)
        if raw:
            self.open_doc(Path(raw))

    def _on_anchor_clicked(self, url: QUrl) -> None:
        """Relative .md links open in-app (a ``#fragment`` scrolls to that
        anchor); a bare ``#fragment`` scrolls the current document; anything
        else goes to the OS."""
        if url.scheme().lower() in ("http", "https", "mailto", "ftp"):
            QDesktopServices.openUrl(url)
            return
        rel = url.toLocalFile() if url.isLocalFile() else url.path()
        fragment = url.fragment()
        if not rel:                                   # same-document anchor
            if fragment:
                self._browser.scrollToAnchor(fragment)
            return
        if self._current is None:
            return
        target = (self._current.parent / rel).resolve()
        if target.suffix.lower() == ".md" and target.is_file():
            if self.open_doc(target) and fragment:
                self._browser.scrollToAnchor(fragment)
        elif target.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _apply_filters(self, *_args) -> None:
        chapter = self._chapter_filter.currentText()
        show_all = chapter in ("", "All Chapters")
        needle = self._search.text().strip().lower()

        for name, parent in self._chapter_items.items():
            chapter_ok = show_all or name == chapter
            any_visible = False
            for i in range(parent.childCount()):
                child = parent.child(i)
                text_ok = (not needle) or (needle in child.text(0).lower()) \
                    or (needle in name.lower())
                visible = chapter_ok and text_ok
                child.setHidden(not visible)
                any_visible = any_visible or visible
            parent.setHidden(not any_visible)
