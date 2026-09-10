"""Reference screen — in-app browser for the suite's docs/ corpus.

Ported from qec-trainer's reference screen: same top bar (title, chapter
filter, Back button), same lazy ``load_all()`` entry point and
``back_requested`` signal.  Every ``docs/**/*.md`` chapter is listed on the
left (grouped by chapter directory) and rendered on the right in a
QTextBrowser.  The docs root is resolved relative to this file
(``<repo>/docs``) — never a hardcoded home path.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QListWidget, QListWidgetItem, QTextBrowser, QSplitter,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QColor, QFont
from ui import theme

# <repo>/problem-trainer/ui/screens/reference_screen.py  ->  parents[3] == <repo>
_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"

# Problem topic -> docs chapter directory (used to preselect the chapter filter).
TOPIC_CHAPTER: dict[str, str] = {
    "Linear Algebra & QM Math": "01_mathematical_foundations",
    "Circuits & Gates":         "03_quantum_gates_and_circuits",
    "Algorithms":               "04_quantum_algorithms",
    "Error Correction":         "05_quantum_error_correction",
    "VQA":                      "06_variational_quantum_algorithms",
    "Information Theory":       "08_advanced_topics",
}

# Derivation id -> docs chapter directory.
DERIVATION_CHAPTER: dict[str, str] = {
    "deriv_qpe":           "04_quantum_algorithms",
    "deriv_grover_count":  "04_quantum_algorithms",
    "deriv_chsh":          "02_quantum_mechanics",
    "deriv_no_cloning":    "02_quantum_mechanics",
    "deriv_teleportation": "03_quantum_gates_and_circuits",
    "deriv_param_shift":   "06_variational_quantum_algorithms",
    "deriv_threshold":     "05_quantum_error_correction",
}

ALL_CHAPTERS = "All Chapters"
OVERVIEW_LABEL = "Overview"
_SMALL_WORDS = {"and", "of", "the", "for", "in", "to", "a"}


@dataclass(frozen=True)
class DocEntry:
    path: Path
    chapter: str        # directory key relative to docs root ("" for root files)
    chapter_label: str
    title: str


def docs_root() -> Path:
    return _DOCS_ROOT


def chapter_label(key: str) -> str:
    """'03_quantum_gates_and_circuits' -> '03 · Quantum Gates and Circuits'."""
    if not key:
        return OVERVIEW_LABEL
    parts = []
    for seg in Path(key).parts:
        m = re.match(r"^(\d+)_(.+)$", seg)
        num, body = (m.group(1), m.group(2)) if m else ("", seg)
        words = body.replace("_", " ").split()
        titled = " ".join(
            w if (i and w.lower() in _SMALL_WORDS) else w[:1].upper() + w[1:]
            for i, w in enumerate(words)
        )
        parts.append(f"{num} · {titled}" if num else titled)
    return " / ".join(parts)


def doc_title(path: Path) -> str:
    """First level-1 markdown heading, else a prettified file stem."""
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for _ in range(40):
                line = fh.readline()
                if not line:
                    break
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    stem = re.sub(r"^\d+_", "", path.stem)
    return stem.replace("_", " ").strip().title() or path.name


def scan_docs(root: Path | None = None) -> list[DocEntry]:
    """Every *.md under the docs root, root files first, then chapters in order."""
    root = root or _DOCS_ROOT
    if not root.is_dir():
        return []
    entries: list[DocEntry] = []
    for p in root.rglob("*.md"):
        if any(part.startswith(".") for part in p.relative_to(root).parts):
            continue
        rel_dir = p.parent.relative_to(root)
        key = "" if rel_dir == Path(".") else rel_dir.as_posix()
        entries.append(DocEntry(p, key, chapter_label(key), doc_title(p)))
    entries.sort(key=lambda e: (e.chapter != "", e.chapter, e.path.name))
    return entries


def render_markdown_source(text: str) -> str:
    """Make the docs' HTML `<details>` solution blocks visible in Qt markdown."""
    text = re.sub(r"<details>\s*<summary>(.*?)</summary>", r"\n\n**\1**\n\n",
                  text, flags=re.S | re.I)
    text = re.sub(r"</details>", "\n", text, flags=re.I)
    return text


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
            f"background-color: {theme.SURFACE}; border-bottom: 1px solid {theme.BORDER};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 10, 24, 10)
        top_layout.setSpacing(16)

        title_lbl = QLabel("Reference")
        title_lbl.setObjectName("heading")
        title_lbl.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {theme.TEXT}; background: transparent;")
        top_layout.addWidget(title_lbl)

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(
            f"font-size: 12px; color: {theme.TEXT_MUTED}; background: transparent;")
        top_layout.addWidget(self._count_lbl)

        top_layout.addStretch()

        self._chapter_filter = QComboBox()
        self._chapter_filter.setMinimumWidth(260)
        self._chapter_filter.addItem(ALL_CHAPTERS)
        self._chapter_filter.currentTextChanged.connect(self._on_filter_changed)
        top_layout.addWidget(self._chapter_filter)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter titles…")
        self._search.setClearButtonEnabled(True)
        self._search.setMaximumWidth(220)
        self._search.textChanged.connect(self._on_filter_changed)
        top_layout.addWidget(self._search)

        top_layout.addStretch()

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        top_layout.addWidget(back_btn)

        root.addWidget(top_bar)

        # ── Body: chapter list | rendered document ─────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self._list = QListWidget()
        self._list.setMinimumWidth(240)
        self._list.setWordWrap(True)
        self._list.currentItemChanged.connect(self._on_current_item_changed)
        splitter.addWidget(self._list)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 12, 16, 12)
        rl.setSpacing(8)

        head_row = QHBoxLayout()
        self._crumb_lbl = QLabel("")
        self._crumb_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        head_row.addWidget(self._crumb_lbl)
        head_row.addStretch()
        self._open_btn = QPushButton("Open externally")
        self._open_btn.setObjectName("flat")
        self._open_btn.setToolTip("Open this chapter's .md file in your system viewer")
        self._open_btn.clicked.connect(self._on_open_externally)
        self._open_btn.setEnabled(False)
        head_row.addWidget(self._open_btn)
        rl.addLayout(head_row)

        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(self._on_anchor_clicked)
        self._browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {theme.SURFACE}; color: {theme.TEXT};"
            f" border: 1px solid {theme.BORDER}; border-radius: 8px; font-size: 14px; }}")
        self._browser.document().setDocumentMargin(18)
        rl.addWidget(self._browser, 1)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 720])
        root.addWidget(splitter, 1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> None:
        """Scan the docs tree once and populate the chapter list."""
        if self._loaded:
            return
        self._loaded = True
        self._entries = scan_docs()
        self._count_lbl.setText(
            f"{len(self._entries)} pages" if self._entries else "no docs found")

        self._chapter_filter.blockSignals(True)
        self._chapter_filter.clear()
        self._chapter_filter.addItem(ALL_CHAPTERS)
        seen: list[str] = []
        for e in self._entries:
            if e.chapter not in seen:
                seen.append(e.chapter)
                self._chapter_filter.addItem(e.chapter_label, e.chapter)
        self._chapter_filter.blockSignals(False)

        if not self._entries:
            self._browser.setPlainText(
                f"No documentation found.\n\nExpected markdown chapters under:\n{_DOCS_ROOT}")
            self._crumb_lbl.setText("")
            return
        self._rebuild_list()

    def entries(self) -> list[DocEntry]:
        return list(self._entries)

    def current_doc(self) -> Path | None:
        return self._current.path if self._current else None

    def current_chapter(self) -> str:
        """Selected chapter key ('' for root files); ALL_CHAPTERS when unfiltered."""
        data = self._chapter_filter.currentData()
        return ALL_CHAPTERS if data is None else data

    def show_all(self) -> None:
        """Reset to the unfiltered view: every chapter, no title filter.

        Used when Reference is opened from Setup so a chapter jump made
        earlier from a problem/derivation does not leak into the browse view.
        The open document is kept if it is still listed.
        """
        self.load_all()
        self._apply_filters(0)

    def select_chapter(self, chapter: str) -> bool:
        """Filter to a chapter directory key (e.g. '04_quantum_algorithms').

        Programmatic jumps always show the whole chapter, so any title filter
        text left from an earlier visit is cleared.
        """
        self.load_all()
        for i in range(self._chapter_filter.count()):
            if self._chapter_filter.itemData(i) == chapter:
                self._apply_filters(i)
                return True
        return False

    def select_topic(self, topic: str) -> bool:
        """Jump to the chapter that backs a problem topic (falls back to all)."""
        self.load_all()
        key = TOPIC_CHAPTER.get(topic)
        if key and self.select_chapter(key):
            return True
        self._apply_filters(0)
        return False

    def select_derivation(self, derivation_id: str) -> bool:
        """Jump to the chapter that backs a guided derivation (falls back to all)."""
        self.load_all()
        key = DERIVATION_CHAPTER.get(derivation_id)
        if key and self.select_chapter(key):
            return True
        self._apply_filters(0)
        return False

    def show_doc(self, path: Path) -> bool:
        """Render one markdown file; returns False if it could not be read."""
        self.load_all()
        path = Path(path).resolve()
        entry = next((e for e in self._entries if e.path == path), None)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self._browser.setPlainText(f"Could not read {path}:\n{exc}")
            return False
        self._current = entry or DocEntry(path, "", OVERVIEW_LABEL, doc_title(path))
        self._browser.setMarkdown(render_markdown_source(text))
        self._browser.verticalScrollBar().setValue(0)
        self._crumb_lbl.setText(
            f"{self._current.chapter_label}  ›  {self._current.title}")
        self._open_btn.setEnabled(True)
        self._sync_list_selection()
        return True

    # ------------------------------------------------------------------
    # List / filter
    # ------------------------------------------------------------------

    def _apply_filters(self, chapter_index: int) -> None:
        """Clear the title filter and select a chapter, rebuilding the list once."""
        for w in (self._search, self._chapter_filter):
            w.blockSignals(True)
        self._search.clear()
        self._chapter_filter.setCurrentIndex(chapter_index)
        for w in (self._search, self._chapter_filter):
            w.blockSignals(False)
        if self._loaded and self._entries:
            self._rebuild_list()

    def _visible_entries(self) -> list[DocEntry]:
        chapter = self.current_chapter()
        needle = self._search.text().strip().lower()
        out = []
        for e in self._entries:
            if chapter != ALL_CHAPTERS and e.chapter != chapter:
                continue
            if needle and needle not in e.title.lower() and needle not in e.path.name.lower():
                continue
            out.append(e)
        return out

    def _rebuild_list(self) -> None:
        self._list.blockSignals(True)
        self._list.clear()
        visible = self._visible_entries()
        show_headers = self.current_chapter() == ALL_CHAPTERS
        last_chapter: str | None = None
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(max(7, header_font.pointSize() - 2))
        for e in visible:
            if show_headers and e.chapter != last_chapter:
                last_chapter = e.chapter
                hdr = QListWidgetItem(e.chapter_label.upper())
                hdr.setFlags(Qt.ItemFlag.ItemIsEnabled)      # visible, not selectable
                hdr.setForeground(QColor(theme.TEXT_MUTED))
                hdr.setFont(header_font)
                self._list.addItem(hdr)
            li = QListWidgetItem(e.title)
            li.setToolTip(e.path.relative_to(_DOCS_ROOT).as_posix()
                          if _DOCS_ROOT in e.path.parents else str(e.path))
            li.setData(Qt.ItemDataRole.UserRole, str(e.path))
            self._list.addItem(li)
        self._list.blockSignals(False)

        # Keep the open doc if it is still listed; otherwise open the first one.
        if self._current and any(e.path == self._current.path for e in visible):
            self._sync_list_selection()
        elif visible:
            self.show_doc(visible[0].path)
        else:
            self._current = None
            self._crumb_lbl.setText("")
            self._open_btn.setEnabled(False)
            self._browser.setPlainText("No pages match the current filter.")

    def _sync_list_selection(self) -> None:
        if not self._current:
            return
        target = str(self._current.path)
        self._list.blockSignals(True)
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == target:
                self._list.setCurrentItem(item)
                self._list.scrollToItem(item)
                break
        self._list.blockSignals(False)

    def _on_filter_changed(self, *_args) -> None:
        if self._loaded:
            self._rebuild_list()

    def _on_current_item_changed(self, current: QListWidgetItem | None, _prev) -> None:
        if current is None:
            return
        path = current.data(Qt.ItemDataRole.UserRole)
        if path:
            self.show_doc(Path(path))

    # ------------------------------------------------------------------
    # Links
    # ------------------------------------------------------------------

    def _on_anchor_clicked(self, url: QUrl) -> None:
        if url.scheme() in ("http", "https", "mailto"):
            QDesktopServices.openUrl(url)
            return
        # Fragment-only link inside the current page.
        if not url.path() and url.hasFragment():
            self._browser.scrollToAnchor(url.fragment())
            return
        base = self._current.path.parent if self._current else _DOCS_ROOT
        target = (base / url.path()).resolve() if not url.isLocalFile() \
            else Path(url.toLocalFile()).resolve()
        if target.suffix.lower() == ".md" and target.is_file() \
                and _DOCS_ROOT.resolve() in target.parents:
            self.show_doc(target)
            if url.hasFragment():
                self._browser.scrollToAnchor(url.fragment())
        elif target.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _on_open_externally(self) -> None:
        if self._current:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._current.path)))
