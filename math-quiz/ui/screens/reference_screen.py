"""Reference screen — in-app browser for the shared docs/ corpus.

Ported from qec-trainer/ui/screens/reference_screen.py and adapted for
math-quiz: the docs root is resolved relative to this file
(``<repo>/docs``), every ``docs/**/*.md`` chapter is listed (grouped by
chapter directory) and rendered with QTextBrowser's GitHub-dialect Markdown
support. The Mathematical Foundations chapter is opened first because that
is the rung this app drills.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QListWidget, QListWidgetItem, QTextBrowser, QSplitter,
    QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import (
    QDesktopServices, QPalette, QColor, QBrush, QFont,
    QTextCursor, QTextBlockFormat, QTextCharFormat, QTextFormat,
)

from ui import theme

# math-quiz/ui/screens/reference_screen.py -> parents[3] is the repo root.
_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"

# Chapter directory this app opens by default (math is rung 1 of the ladder).
_DEFAULT_CHAPTER_DIR = "01_mathematical_foundations"
_OVERVIEW_CHAPTER = "Overview"
_ALL_CHAPTERS = "All chapters"
_INLINE_CODE_COLOR = "#79c0ff"

_SMALL_WORDS = {"and", "of", "the", "for", "to", "in", "on"}


@dataclass(frozen=True)
class DocEntry:
    path: Path
    chapter: str      # human-readable chapter name (grouping key)
    title: str        # first "# " heading, or prettified file name
    order: tuple      # sort key


def docs_root() -> Path:
    return _DOCS_ROOT


def scan_docs(root: Path | None = None) -> list[DocEntry]:
    """Enumerate every Markdown file under the docs root, in ladder order."""
    root = root or _DOCS_ROOT
    if not root.is_dir():
        return []
    entries: list[DocEntry] = []
    for path in root.rglob("*.md"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if len(rel.parts) == 1:
            chapter = _OVERVIEW_CHAPTER
            order = (0, "", rel.name.lower())
        else:
            chapter = _pretty_chapter(rel.parts[0])
            order = (1, rel.parts[0].lower(), *[p.lower() for p in rel.parts[1:]])
        entries.append(DocEntry(path=path, chapter=chapter,
                                title=_read_title(path), order=order))
    entries.sort(key=lambda e: e.order)
    return entries


def _read_title(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for _ in range(60):
                line = fh.readline()
                if not line:
                    break
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    return _pretty_words(path.stem)


def _pretty_chapter(dirname: str) -> str:
    head, _, rest = dirname.partition("_")
    if head.isdigit() and rest:
        return f"{int(head)}. {_pretty_words(rest)}"
    return _pretty_words(dirname)


def _pretty_words(stem: str) -> str:
    parts = stem.split("_")
    if parts and parts[0].isdigit():
        parts = parts[1:]
    words = []
    for i, w in enumerate(parts):
        if not w:
            continue
        if i > 0 and w.lower() in _SMALL_WORDS:
            words.append(w.lower())
        else:
            words.append(w[:1].upper() + w[1:])
    return " ".join(words) or stem


class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._entries: list[DocEntry] = []
        self._current: DocEntry | None = None
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
        self._chapter_filter.setMinimumWidth(240)
        self._chapter_filter.addItem(_ALL_CHAPTERS)
        self._chapter_filter.currentTextChanged.connect(self._on_filter_changed)
        top_layout.addWidget(self._chapter_filter)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter by title…")
        self._search.setClearButtonEnabled(True)
        self._search.setMinimumWidth(180)
        self._search.setStyleSheet(
            f"QLineEdit {{ background: {theme.SURFACE2}; color: {theme.TEXT};"
            f" border: 1px solid {theme.BORDER}; border-radius: 6px; padding: 6px 10px; }}"
            f"QLineEdit:focus {{ border-color: {theme.ACCENT}; }}"
        )
        self._search.textChanged.connect(self._on_filter_changed)
        top_layout.addWidget(self._search)

        top_layout.addStretch()

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("flat")
        self._back_btn.clicked.connect(self.back_requested)
        top_layout.addWidget(self._back_btn)

        root.addWidget(top_bar)

        # ── Body: chapter list | document ──────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        self._list = QListWidget()
        self._list.setMinimumWidth(220)
        self._list.setUniformItemSizes(False)
        self._list.setStyleSheet(
            f"QListWidget {{ border: none; border-right: 1px solid {theme.BORDER};"
            f" border-radius: 0; padding: 8px 4px; }}"
        )
        self._list.currentItemChanged.connect(self._on_item_changed)
        splitter.addWidget(self._list)

        doc_pane = QWidget()
        doc_layout = QVBoxLayout(doc_pane)
        doc_layout.setContentsMargins(0, 0, 0, 0)
        doc_layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 14, 28, 8)
        header_layout.setSpacing(12)
        head_col = QVBoxLayout()
        head_col.setSpacing(2)
        self._doc_title = QLabel("")
        self._doc_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {theme.TEXT};")
        self._doc_title.setWordWrap(True)
        head_col.addWidget(self._doc_title)
        self._doc_path = QLabel("")
        self._doc_path.setObjectName("muted")
        self._doc_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        head_col.addWidget(self._doc_path)
        header_layout.addLayout(head_col, 1)

        self._open_btn = QPushButton("Open in external viewer")
        self._open_btn.setObjectName("flat")
        self._open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_btn.clicked.connect(self._on_open_external)
        self._open_btn.setEnabled(False)
        header_layout.addWidget(self._open_btn, 0, Qt.AlignmentFlag.AlignTop)
        doc_layout.addWidget(header)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFixedHeight(1)
        doc_layout.addWidget(sep)

        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(self._on_anchor_clicked)
        self._browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._browser.setStyleSheet(
            f"QTextBrowser {{ background: {theme.BG}; color: {theme.TEXT};"
            f" border: none; padding: 20px 28px; font-size: 14px; }}"
        )
        self._browser.document().setDocumentMargin(16)
        pal = self._browser.palette()
        pal.setColor(QPalette.ColorRole.Link, QColor(theme.ACCENT))
        pal.setColor(QPalette.ColorRole.LinkVisited, QColor(theme.ACCENT2))
        self._browser.setPalette(pal)
        doc_layout.addWidget(self._browser, 1)

        splitter.addWidget(doc_pane)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 820])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> None:
        """Scan the docs tree on first use; later calls keep the reader's place."""
        if self._loaded:
            return
        self._loaded = True
        self._entries = scan_docs()

        self._chapter_filter.blockSignals(True)
        self._chapter_filter.clear()
        self._chapter_filter.addItem(_ALL_CHAPTERS)
        seen: list[str] = []
        for e in self._entries:
            if e.chapter not in seen:
                seen.append(e.chapter)
        for chapter in seen:
            self._chapter_filter.addItem(chapter)
        self._chapter_filter.blockSignals(False)

        self._populate_list()

        if not self._entries:
            self._show_missing_docs()
            return

        default = next(
            (i for i, e in enumerate(self._entries)
             if e.path.parent.name == _DEFAULT_CHAPTER_DIR),
            0,
        )
        self.select_entry(default)

    def reload(self) -> None:
        """Force a rescan of the docs tree (e.g. after files change)."""
        self._loaded = False
        self._current = None
        self.load_all()

    @property
    def entries(self) -> list[DocEntry]:
        return list(self._entries)

    @property
    def current_entry(self) -> DocEntry | None:
        return self._current

    def select_entry(self, index: int) -> None:
        """Select the given entry in the list, which renders it."""
        if not (0 <= index < len(self._entries)):
            return
        item = self._item_for_index(index)
        if item is None:
            # Entry hidden by the current filters — clear them and retry.
            self._search.blockSignals(True)
            self._search.clear()
            self._search.blockSignals(False)
            self._chapter_filter.blockSignals(True)
            self._chapter_filter.setCurrentIndex(0)
            self._chapter_filter.blockSignals(False)
            self._populate_list()
            item = self._item_for_index(index)
        if item is not None:
            self._list.setCurrentItem(item)
        else:
            self._show_entry(index)

    def select_path(self, path: Path) -> bool:
        """Select the entry for an absolute docs path. Returns False if unknown."""
        try:
            target = Path(path).resolve()
        except OSError:
            return False
        for i, e in enumerate(self._entries):
            if e.path == target:
                self.select_entry(i)
                return True
        return False

    # ------------------------------------------------------------------
    # List population / filtering
    # ------------------------------------------------------------------

    def _populate_list(self) -> None:
        chapter = self._chapter_filter.currentText()
        needle = self._search.text().strip().lower()
        self._list.blockSignals(True)
        self._list.clear()
        last_chapter = None
        for i, e in enumerate(self._entries):
            if chapter != _ALL_CHAPTERS and e.chapter != chapter:
                continue
            if needle and needle not in e.title.lower() and needle not in e.path.name.lower():
                continue
            if e.chapter != last_chapter:
                self._list.addItem(_header_item(e.chapter))
                last_chapter = e.chapter
            item = QListWidgetItem(f"   {e.title}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setToolTip(str(e.path.relative_to(_DOCS_ROOT)) if e.path.is_relative_to(_DOCS_ROOT) else str(e.path))
            self._list.addItem(item)
        self._list.blockSignals(False)

        # Keep the open document highlighted if it is still listed.
        if self._current is not None:
            try:
                idx = self._entries.index(self._current)
            except ValueError:
                idx = -1
            item = self._item_for_index(idx) if idx >= 0 else None
            if item is not None:
                self._list.blockSignals(True)
                self._list.setCurrentItem(item)
                self._list.blockSignals(False)

    def _item_for_index(self, index: int) -> QListWidgetItem | None:
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == index:
                return item
        return None

    def _on_filter_changed(self, _text: str) -> None:
        self._populate_list()

    def _on_item_changed(self, current: QListWidgetItem | None, _previous) -> None:
        if current is None:
            return
        data = current.data(Qt.ItemDataRole.UserRole)
        if data is None:
            return
        self._show_entry(int(data))

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _show_entry(self, index: int) -> None:
        if not (0 <= index < len(self._entries)):
            return
        entry = self._entries[index]
        if entry == self._current:
            return
        self._current = entry
        try:
            text = entry.path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            text = f"# Could not read file\n\n`{entry.path}`\n\n{exc}"
        self._browser.setMarkdown(text)
        self._decorate_document()
        self._browser.verticalScrollBar().setValue(0)
        self._doc_title.setText(entry.title)
        rel = entry.path.relative_to(_DOCS_ROOT.parent) if entry.path.is_relative_to(_DOCS_ROOT.parent) else entry.path
        self._doc_path.setText(f"{entry.chapter}  ·  {rel}")
        self._open_btn.setEnabled(True)

    def _show_missing_docs(self) -> None:
        self._current = None
        self._doc_title.setText("No documentation found")
        self._doc_path.setText(str(_DOCS_ROOT))
        self._open_btn.setEnabled(False)
        self._browser.setMarkdown(
            "# No documentation found\n\n"
            f"Expected Markdown chapters under:\n\n`{_DOCS_ROOT}`\n\n"
            "The reference browser reads the shared `docs/` corpus at the root of "
            "the Quantum-Computing repository."
        )

    def _decorate_document(self) -> None:
        """Tint fenced code blocks and inline code for the dark theme.

        Qt's Markdown importer builds the document directly (the default
        stylesheet does not apply), so the formats are adjusted afterwards.
        """
        try:
            doc = self._browser.document()
            cursor = QTextCursor(doc)
            code_bg = QBrush(QColor(theme.SURFACE))
            inline_ranges: list[tuple[int, int]] = []
            block = doc.begin()
            while block.isValid():
                bf = block.blockFormat()
                is_code_block = (
                    bf.nonBreakableLines()
                    or bf.hasProperty(QTextFormat.Property.BlockCodeLanguage)
                )
                if is_code_block:
                    fmt = QTextBlockFormat()
                    fmt.setBackground(code_bg)
                    fmt.setLeftMargin(12)
                    fmt.setRightMargin(12)
                    cursor.setPosition(block.position())
                    cursor.mergeBlockFormat(fmt)
                else:
                    it = block.begin()
                    while not it.atEnd():
                        frag = it.fragment()
                        if frag.isValid() and frag.charFormat().fontFixedPitch():
                            inline_ranges.append((frag.position(), frag.length()))
                        it += 1
                block = block.next()
            if inline_ranges:
                fmt = QTextCharFormat()
                fmt.setForeground(QColor(_INLINE_CODE_COLOR))
                for pos, length in inline_ranges:
                    cursor.setPosition(pos)
                    cursor.setPosition(pos + length, QTextCursor.MoveMode.KeepAnchor)
                    cursor.mergeCharFormat(fmt)
        except Exception:
            # Cosmetic only — never let styling break the reader.
            pass

    # ------------------------------------------------------------------
    # Links
    # ------------------------------------------------------------------

    def _on_anchor_clicked(self, url: QUrl) -> None:
        scheme = url.scheme()
        if scheme in ("http", "https", "mailto", "ftp"):
            QDesktopServices.openUrl(url)
            return
        path_part = url.path()
        fragment = url.fragment()
        if not path_part:
            if fragment:
                self._browser.scrollToAnchor(fragment)
            return
        base = self._current.path.parent if self._current else _DOCS_ROOT
        try:
            target = (base / path_part).resolve()
        except OSError:
            return
        if self.select_path(target):
            if fragment:
                self._browser.scrollToAnchor(fragment)
            return
        if target.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _on_open_external(self) -> None:
        if self._current is None:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._current.path)))


def _header_item(chapter: str) -> QListWidgetItem:
    item = QListWidgetItem(chapter.upper())
    item.setFlags(Qt.ItemFlag.NoItemFlags)
    item.setForeground(QColor(theme.TEXT_MUTED))
    font = QFont()
    font.setBold(True)
    font.setPointSize(8)
    item.setFont(font)
    return item
