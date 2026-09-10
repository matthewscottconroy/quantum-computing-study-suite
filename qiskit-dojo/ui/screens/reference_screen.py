"""Reference screen for qiskit-dojo — in-app browser for the shared docs corpus.

Renders every Markdown chapter under ``<repo>/docs`` (``docs/**/*.md``) with
Qt's native Markdown import.  The docs root is resolved relative to this file
(``ui/screens/`` → app dir → repo root), never from a hard-coded home path.
Fully offline; no API key needed.
"""
from __future__ import annotations
import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QTextBrowser, QSplitter, QFrame,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import (
    QDesktopServices, QTextCursor, QTextBlockFormat, QTextCharFormat,
    QTextTable, QTextFrameFormat, QColor, QBrush, QFont,
)
from ui import theme

_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"
_PATH_ROLE = Qt.ItemDataRole.UserRole

# The corpus uses <details><summary>…</summary>…</details> for exercise
# solutions.  Qt's Markdown importer mangles inline code inside raw HTML
# blocks, so rewrite them as a bold "Solution:" lead-in before rendering.
_DETAILS_OPEN  = re.compile(r"<details>\s*<summary>(.*?)</summary>", re.S)
_DETAILS_CLOSE = re.compile(r"</details>")
_SLUG_STRIP    = re.compile(r"[^\w\s-]")
_SLUG_SPACES   = re.compile(r"\s+")


def _prettify(name: str) -> str:
    """'01_mathematical_foundations' → '1 · Mathematical Foundations'."""
    parts = name.split("_")
    num = ""
    if parts and parts[0].isdigit():
        num = str(int(parts[0]))
        parts = parts[1:]
    words = " ".join(w.capitalize() for w in parts if w)
    return f"{num} · {words}" if num else words


def _doc_title(path: Path) -> str:
    """First H1 of the file, else a prettified file stem."""
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    return _prettify(path.stem)


def _slug(text: str) -> str:
    """GitHub-style heading slug: 'Key Formulas (2)' → 'key-formulas-2'."""
    s = _SLUG_STRIP.sub("", text.strip().lower())
    return _SLUG_SPACES.sub("-", s).strip("-")


def _preprocess(md: str) -> str:
    md = _DETAILS_OPEN.sub(r"**\1:**", md)
    md = _DETAILS_CLOSE.sub("", md)
    return md


class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._loaded = False
        self._current: Path | None = None
        self._doc_count = 0
        self._anchors: set[str] = set()     # heading slugs in the shown doc
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top_bar = QWidget()
        top_bar.setObjectName("refTopBar")
        # Scoped to the bar: an unscoped rule cascades onto every child label
        # and button, drawing each with its own bottom border.
        top_bar.setStyleSheet(
            f"QWidget#refTopBar {{ background-color: {theme.SURFACE}; "
            f"border-bottom: 1px solid {theme.BORDER}; }}"
        )
        self._top_bar = top_bar
        top = QHBoxLayout(top_bar)
        top.setContentsMargins(24, 10, 24, 10)
        top.setSpacing(16)

        title = QLabel("Reference")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {theme.TEXT};")
        top.addWidget(title)

        self._crumb_lbl = QLabel("")
        self._crumb_lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        top.addWidget(self._crumb_lbl, 1)

        self._open_btn = QPushButton("Open externally")
        self._open_btn.setObjectName("flat")
        self._open_btn.setToolTip("Open the current chapter with your system's Markdown handler")
        self._open_btn.clicked.connect(self._on_open_external)
        self._open_btn.setEnabled(False)
        top.addWidget(self._open_btn)

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("flat")
        self._back_btn.clicked.connect(self.back_requested)
        top.addWidget(self._back_btn)
        root.addWidget(top_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # ---- left: chapter tree ----------------------------------------
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 8, 16)
        left_layout.setSpacing(8)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter chapters…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._apply_filter)
        left_layout.addWidget(self._search)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(14)
        self._tree.setStyleSheet(
            f"QTreeWidget {{ background: {theme.SURFACE}; border: 1px solid {theme.BORDER};"
            f" border-radius: 6px; font-size: 13px; }}"
            f"QTreeWidget::item {{ padding: 4px 2px; }}"
            f"QTreeWidget::item:selected {{ background: {theme.ACCENT2}; color: white; }}"
            f"QTreeWidget::item:hover {{ background: {theme.SURFACE2}; }}"
        )
        self._tree.currentItemChanged.connect(self._on_item_changed)
        left_layout.addWidget(self._tree, 1)

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        left_layout.addWidget(self._count_lbl)
        splitter.addWidget(left)

        # ---- right: rendered chapter -----------------------------------
        right = QFrame()
        right.setObjectName("card")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 8, 8)

        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(self._on_anchor)
        self._browser.document().setDocumentMargin(16)
        right_layout.addWidget(self._browser)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 860])

    # -------------------------------------------------------------- public

    @property
    def docs_root(self) -> Path:
        return _DOCS_ROOT

    @property
    def current_path(self) -> Path | None:
        return self._current

    def load_all(self) -> None:
        """Scan the docs tree once and show the landing page."""
        if self._loaded:
            return
        self._loaded = True
        self._populate()

    def show_doc(self, path: Path) -> bool:
        """Render one Markdown file; returns False if it cannot be read."""
        path = Path(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            self._browser.setPlainText(f"Could not read {path}:\n{e}")
            return False
        self._current = path
        self._browser.setMarkdown(_preprocess(text))
        self._style_document()
        self._browser.verticalScrollBar().setValue(0)
        try:
            rel = path.relative_to(_DOCS_ROOT)
        except ValueError:
            rel = path
        self._crumb_lbl.setText(f"docs / {' / '.join(rel.parts)}")
        self._open_btn.setEnabled(True)
        self._select_item_for(path)
        return True

    def scroll_to_fragment(self, fragment: str) -> bool:
        """Scroll to the heading whose GitHub-style slug matches `fragment`.

        Returns False (and does nothing) when no heading matches.
        """
        name = _slug(fragment)
        if name not in self._anchors:
            return False
        self._browser.scrollToAnchor(name)
        return True

    # ------------------------------------------------------------ populate

    def _populate(self) -> None:
        self._tree.clear()
        self._doc_count = 0
        if not _DOCS_ROOT.is_dir():
            self._browser.setPlainText(
                "Docs folder not found.\n\n"
                f"Expected the shared corpus at:\n  {_DOCS_ROOT}\n\n"
                "Run the dojo from inside the quantum-study repository."
            )
            self._count_lbl.setText("0 chapters")
            return

        first: QTreeWidgetItem | None = None

        # Top-level files (README.md = the learning ladder) come first.
        for md in sorted(_DOCS_ROOT.glob("*.md")):
            label = "Learning Ladder (README)" if md.name == "README.md" else _doc_title(md)
            item = self._make_leaf(label, md)
            self._tree.addTopLevelItem(item)
            first = first or item

        for chapter in sorted(p for p in _DOCS_ROOT.iterdir() if p.is_dir()):
            files = sorted(chapter.rglob("*.md"))
            if not files:
                continue
            parent = QTreeWidgetItem([_prettify(chapter.name)])
            parent.setFlags(parent.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = parent.font(0)
            font.setBold(True)
            parent.setFont(0, font)
            parent.setForeground(0, QBrush(QColor(theme.TEXT_MUTED)))
            self._tree.addTopLevelItem(parent)
            for md in files:
                leaf = self._make_leaf(_doc_title(md), md)
                parent.addChild(leaf)
                first = first or leaf
            parent.setExpanded(True)

        self._count_lbl.setText(f"{self._doc_count} chapters · {_DOCS_ROOT.name}/")
        if first is not None and self._current is None:
            self._tree.setCurrentItem(first)

    def _make_leaf(self, label: str, path: Path) -> QTreeWidgetItem:
        item = QTreeWidgetItem([label])
        item.setData(0, _PATH_ROLE, str(path))
        try:
            item.setToolTip(0, str(path.relative_to(_DOCS_ROOT)))
        except ValueError:
            item.setToolTip(0, str(path))
        self._doc_count += 1
        return item

    def _iter_leaves(self):
        for i in range(self._tree.topLevelItemCount()):
            top = self._tree.topLevelItem(i)
            if top.childCount() == 0:
                yield top
            for j in range(top.childCount()):
                yield top.child(j)

    def _select_item_for(self, path: Path) -> None:
        target = str(path)
        for leaf in self._iter_leaves():
            if leaf.data(0, _PATH_ROLE) == target:
                if self._tree.currentItem() is not leaf:
                    self._tree.blockSignals(True)
                    self._tree.setCurrentItem(leaf)
                    self._tree.blockSignals(False)
                return

    # ------------------------------------------------------------- styling

    def _style_document(self) -> None:
        """Dark-theme touches Qt's Markdown import does not apply itself."""
        doc = self._browser.document()
        mono = QFont("JetBrains Mono", 10)
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self._anchors = set()

        block = doc.begin()
        while block.isValid():
            bf = block.blockFormat()
            if bf.nonBreakableLines():              # fenced code block
                cur = QTextCursor(block)
                nbf = QTextBlockFormat(bf)
                nbf.setBackground(QColor(theme.SURFACE2))
                nbf.setLeftMargin(12)
                nbf.setRightMargin(12)
                cur.setBlockFormat(nbf)
                self._merge_block_chars(block, font=mono)
            elif bf.headingLevel() > 0:
                # Qt's Markdown importer emits no heading anchors; give every
                # heading a GitHub-style one so '#fragment' links can work.
                self._merge_block_chars(
                    block,
                    color=QColor(theme.ACCENT) if bf.headingLevel() == 1 else None,
                    anchor=self._register_anchor(block.text()),
                )
            block = block.next()

        self._style_tables(doc.rootFrame())

    def _register_anchor(self, heading: str) -> str:
        """Unique slug for a heading (duplicates get -1, -2 … like GitHub)."""
        base = _slug(heading) or "section"
        name, n = base, 1
        while name in self._anchors:
            name = f"{base}-{n}"
            n += 1
        self._anchors.add(name)
        return name

    @staticmethod
    def _merge_block_chars(block, font: QFont | None = None,
                           color: QColor | None = None,
                           anchor: str | None = None) -> None:
        if block.length() <= 1:
            return
        cur = QTextCursor(block)
        cur.setPosition(block.position())
        cur.setPosition(block.position() + block.length() - 1,
                        QTextCursor.MoveMode.KeepAnchor)
        cf = QTextCharFormat()
        if font is not None:
            cf.setFont(font)
        if color is not None:
            cf.setForeground(color)
        if anchor:
            cf.setAnchor(True)              # name only, no href: not link-styled
            cf.setAnchorNames([anchor])
        cur.mergeCharFormat(cf)

    def _style_tables(self, frame) -> None:
        if isinstance(frame, QTextTable):
            fmt = frame.format()
            fmt.setBorder(1)
            fmt.setBorderBrush(QBrush(QColor(theme.BORDER)))
            fmt.setBorderStyle(QTextFrameFormat.BorderStyle.BorderStyle_Solid)
            fmt.setCellPadding(6)
            fmt.setCellSpacing(0)
            frame.setFormat(fmt)
        for child in frame.childFrames():
            self._style_tables(child)

    # ------------------------------------------------------------- filters

    def _apply_filter(self, text: str) -> None:
        q = text.strip().lower()
        for i in range(self._tree.topLevelItemCount()):
            top = self._tree.topLevelItem(i)
            top_match = not q or q in top.text(0).lower()
            if top.childCount() == 0:
                top.setHidden(not top_match)
                continue
            any_visible = False
            for j in range(top.childCount()):
                child = top.child(j)
                show = top_match or q in child.text(0).lower()
                child.setHidden(not show)
                any_visible = any_visible or show
            top.setHidden(not any_visible)
            if q:
                top.setExpanded(True)

    # ------------------------------------------------------------ handlers

    def _on_item_changed(self, current: QTreeWidgetItem | None, _prev=None) -> None:
        if current is None:
            return
        raw = current.data(0, _PATH_ROLE)
        if raw:
            self.show_doc(Path(raw))

    def _on_anchor(self, url: QUrl) -> None:
        if url.scheme() in ("http", "https", "mailto"):
            QDesktopServices.openUrl(url)
            return
        base = (self._current.parent if self._current else _DOCS_ROOT)
        rel = url.path()
        if rel:
            target = (base / rel).resolve()
            if not target.exists():
                # Never hand a missing path to xdg-open; say what went wrong.
                self._crumb_lbl.setText(f"Link target not found: {rel}")
                return
            if target.suffix.lower() == ".md" and target.is_file():
                if not self.show_doc(target):
                    return
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))
                return
        if url.hasFragment():
            self.scroll_to_fragment(url.fragment())

    def _on_open_external(self) -> None:
        if self._current is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._current)))
