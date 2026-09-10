"""Reference screen — in-app browser for the shared study docs (docs/**/*.md).

Ported from qec-trainer/ui/screens/reference_screen.py and adapted for
flashcard-drill.  The docs root is resolved *relative to this file*:

    <repo>/flashcard-drill/ui/screens/reference_screen.py
      parents[0] = screens, [1] = ui, [2] = flashcard-drill, [3] = <repo>

so ``parents[3] / "docs"`` is the suite-wide documentation corpus.  Markdown is
rendered natively by Qt (``QTextBrowser.setMarkdown``); the document is then
restyled for the dark theme (code, links, tables, quotes) and ``<details>``
solution blocks — which Qt would otherwise flatten — are turned into labelled
"Solution" sections that can be hidden for self-testing.

Cross-references: the corpus writes bare ``NN_chapter/NN_file.md`` (or
same-chapter ``NN_file.md``) references in prose rather than Markdown links;
:func:`prepare_markdown` turns those into relative links (optionally carrying
a ``#heading`` fragment) so they navigate in place, and ``$$ … $$`` display
math becomes a fenced block — keeping the ``> `` marker when the formula sits
inside a block quote.  Fenced code is never rewritten.
"""
from __future__ import annotations
import os
import re
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QListWidget, QListWidgetItem, QTextBrowser, QSplitter,
    QCheckBox,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import (
    QDesktopServices, QTextCursor, QTextCharFormat, QTextBlockFormat,
    QTextFrameFormat, QTextTable, QTextFormat, QTextDocument, QColor, QFont,
    QBrush,
)
from ui import theme

_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"

_ALL_CHAPTERS = "All Chapters"
_START_HERE   = "Start Here"
_CODE_FG      = "#a5d6ff"          # light blue for code / formulas on the dark surface
_MONO         = ["JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "Menlo", "monospace"]
_SMALL_WORDS  = {"and", "of", "the", "in", "to", "for", "a", "an"}

# Fences may be indented up to 3 spaces (CommonMark), e.g. inside list items.
_FENCE         = re.compile(r"(^ {0,3}(?:```|~~~).*?^ {0,3}(?:```|~~~)[ \t]*$)", re.M | re.S)
_CODE_SPAN     = re.compile(r"(`+)(.+?)\1")
_DETAILS_OPEN  = re.compile(r"<details>\s*<summary>(.*?)</summary>", re.I | re.S)
_DETAILS_BLOCK = re.compile(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", re.I | re.S)
_DETAILS_CLOSE = re.compile(r"</details>", re.I)
_DISPLAY_MATH  = re.compile(r"\$\$(.+?)\$\$", re.S)
# Leading block-quote markers of a line ("> ", "> > ").
_QUOTE_PREFIX  = re.compile(r"^(?: {0,3}>[ \t]?)+", re.M)
# Bare cross-references the corpus writes in prose, e.g.
# "see 07_quantum_hardware/04_benchmarking_and_characterization.md" or
# "(docs/05_quantum_error_correction/06_surface_code.md)"; a same-chapter
# file may be cited as just "04_quantum_phase_estimation.md", and any form may
# carry a "#heading-slug" suffix.  Anything that is already a Markdown link
# target ("](…"), a Markdown link label ("[…](") or part of a longer path is
# skipped.
_DOC_REF = re.compile(
    r"(?<!\]\()(?<![\w/`.\-])"
    r"((?:docs/)?(?:\d{2}_[a-z0-9_]+/)?\d{2}_[a-z0-9_]+\.md(?:#[\w\-]+)?)"
    r"(?![\w`/\-])(?!\]\()"
)


def docs_root() -> Path:
    """Resolved docs directory (relative to this file — never a hard-coded home path)."""
    return _DOCS_ROOT


# ----------------------------------------------------------------------------
# Doc discovery
# ----------------------------------------------------------------------------

@dataclass
class DocEntry:
    path: Path
    chapter: str        # display name of the chapter group
    chapter_key: str    # directory name ("" for root-level files)
    title: str          # first H1 of the file (or prettified stem)
    _text: str | None = None

    @property
    def rel(self) -> str:
        try:
            return self.path.relative_to(_DOCS_ROOT).as_posix()
        except ValueError:
            return self.path.as_posix()

    def text(self) -> str:
        if self._text is None:
            try:
                self._text = self.path.read_text(encoding="utf-8")
            except Exception as exc:  # unreadable file — show the error inline
                self._text = f"# {self.title}\n\nCould not read `{self.path}`:\n\n```\n{exc}\n```\n"
        return self._text


def _pretty(stem: str) -> str:
    """'03_quantum_gates_and_circuits' -> 'Quantum Gates and Circuits'."""
    stem = re.sub(r"^\d+[_-]?", "", stem)
    words = [w for w in re.split(r"[_\-\s]+", stem) if w]
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        out.append(lw if (i > 0 and lw in _SMALL_WORDS) else (w.upper() if lw in {"qec", "qsvt", "hhl", "qaoa", "vqe"} else w.capitalize()))
    return " ".join(out) or stem


def _chapter_label(dirname: str) -> str:
    m = re.match(r"^(\d+)", dirname)
    name = _pretty(dirname)
    return f"Ch {int(m.group(1))} · {name}" if m else name


def _doc_title(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as fh:
            for _ in range(5):
                line = fh.readline()
                if not line:
                    break
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    return _pretty(path.stem)


def discover_docs(root: Path | None = None) -> list[DocEntry]:
    """Return every docs/**/*.md as a DocEntry, root files first then chapters in order."""
    root = root or _DOCS_ROOT
    entries: list[DocEntry] = []
    if not root.is_dir():
        return entries
    for f in sorted(root.glob("*.md")):
        title = _doc_title(f)
        if f.name.lower() == "readme.md":
            title = f"{title} (README)"
        entries.append(DocEntry(path=f, chapter=_START_HERE, chapter_key="", title=title))
    for d in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
        files = sorted(d.rglob("*.md"))
        if not files:
            continue
        label = _chapter_label(d.name)
        for f in files:
            entries.append(DocEntry(path=f, chapter=label, chapter_key=d.name, title=_doc_title(f)))
    return entries


# ----------------------------------------------------------------------------
# Markdown preparation + dark-theme restyle
# ----------------------------------------------------------------------------

def resolve_doc_ref(ref: str, doc_dir: Path) -> str | None:
    """Turn a bare doc reference into a link target relative to ``doc_dir``.

    ``docs/…`` and ``chapter/file.md`` forms resolve against the docs root.  A
    bare ``file.md`` is taken as a sibling of the current document, falling
    back to the one file of that name anywhere in the corpus (chapters do cite
    each other's files by bare name).  A ``#fragment`` suffix is carried over
    to the target.  Returns None when nothing matches unambiguously (the text
    is then left alone).
    """
    ref, _, fragment = ref.partition("#")
    clean = ref[len("docs/"):] if ref.startswith("docs/") else ref
    if "/" in clean or ref.startswith("docs/"):
        target: Path | None = _DOCS_ROOT / clean
    else:
        target = doc_dir / clean
        if not target.is_file():
            target = _unique_doc_named(clean)
    if target is None or not target.is_file():
        return None
    rel = Path(os.path.relpath(target, doc_dir)).as_posix()
    return f"{rel}#{fragment}" if fragment else rel


def _unique_doc_named(name: str) -> Path | None:
    """The single ``docs/**/<name>`` file, or None when there are 0 or 2+."""
    if not _DOCS_ROOT.is_dir():
        return None
    matches = [
        p for p in _DOCS_ROOT.rglob(name)
        if p.is_file() and not any(part.startswith((".", "_"))
                                   for part in p.relative_to(_DOCS_ROOT).parts)
    ]
    return matches[0] if len(matches) == 1 else None


def _outside_code_spans(segment: str, prose_fn, code_fn=None) -> str:
    """Apply ``prose_fn(prose, start)`` to the text between inline code spans.

    ``start`` is the offset of that prose chunk within ``segment`` (so a
    rewrite can look at the enclosing line).  The spans themselves are left
    alone, or handed to ``code_fn(ticks, code, after)`` — ``after`` being the
    prose that follows the span — when one is given.
    """
    parts = _CODE_SPAN.split(segment)      # prose, ticks, code, prose, ticks, code, …
    out: list[str] = []
    start = 0
    for i in range(0, len(parts), 3):
        out.append(prose_fn(parts[i], start))
        start += len(parts[i])
        if i + 2 < len(parts):
            ticks, code = parts[i + 1], parts[i + 2]
            after = parts[i + 3] if i + 3 < len(parts) else ""
            out.append(code_fn(ticks, code, after) if code_fn else f"{ticks}{code}{ticks}")
            start += 2 * len(ticks) + len(code)
    return "".join(out)


def _linkify(segment: str, doc_dir: Path) -> str:
    """Make bare doc cross-references clickable (outside inline code spans);
    a code span that *is* a doc reference becomes a link with code text.
    Text that is already the label of a Markdown link (``[…](``) is left alone."""
    def repl(m: re.Match) -> str:
        target = resolve_doc_ref(m.group(1), doc_dir)
        return f"[{m.group(1)}]({target})" if target else m.group(0)

    def code(ticks: str, code: str, after: str) -> str:
        m = None if after.startswith("](") else _DOC_REF.fullmatch(code.strip())
        target = resolve_doc_ref(m.group(1), doc_dir) if m else None
        return f"[{ticks}{code}{ticks}]({target})" if target else f"{ticks}{code}{ticks}"

    return _outside_code_spans(segment, lambda s, _start: _DOC_REF.sub(repl, s), code)


def prepare_markdown(text: str, doc_dir: Path | None = None,
                     show_solutions: bool = True) -> str:
    """Rewrite constructs Qt's Markdown importer cannot render.

    Fenced code blocks are left untouched.  Elsewhere:

    * bare doc cross-references become relative links (when ``doc_dir`` given);
    * ``<details><summary>X</summary>…</details>`` -> bold "▸ X" lead-in plus
      the body, or a one-line placeholder when ``show_solutions`` is False;
    * ``$$ … $$`` display math -> fenced code block, so the formula source stays
      legible and monospaced instead of collapsing into a paragraph; a formula
      inside a block quote gets the quote's ``> `` marker on every generated
      line, so the quote is not cut in two.

    Solutions are hidden on the *whole* text before the fence split, because a
    solution body may itself contain a fenced code block (the corpus never
    writes ``<details>`` tags inside code, so this is safe); a stray open /
    close tag that survives is still rewritten per prose segment.  The other
    rewrites are per prose segment and skip inline code spans.
    """
    if not show_solutions:
        text = _DETAILS_BLOCK.sub(
            lambda m: f"\n\n*▸ {m.group(1).strip()} hidden — tick “Show solutions” to reveal.*\n\n",
            text,
        )

    def display_math(seg: str) -> str:
        def rewrite(prose: str, start: int) -> str:
            def repl(m: re.Match) -> str:
                # Quote marker of the line the formula starts on ("" outside quotes).
                abs_start = start + m.start()
                line_start = seg.rfind("\n", 0, abs_start) + 1
                qm = _QUOTE_PREFIX.match(seg, line_start, abs_start)
                p = qm.group(0) if qm else ""
                body = m.group(1).strip()
                if p:
                    body = _QUOTE_PREFIX.sub("", body)
                lines = "\n".join(p + line for line in body.split("\n"))
                return f"\n{p}\n{p}```\n{lines}\n{p}```\n{p}\n{p}"
            return _DISPLAY_MATH.sub(repl, prose)
        return _outside_code_spans(seg, rewrite)

    out: list[str] = []
    for i, seg in enumerate(_FENCE.split(text)):
        if i % 2:                                   # fenced code block
            out.append(seg)
            continue
        if doc_dir is not None:
            seg = _linkify(seg, doc_dir)
        seg = _DETAILS_OPEN.sub(lambda m: f"\n\n**▸ {m.group(1).strip()}**\n\n", seg)
        seg = _DETAILS_CLOSE.sub("\n\n", seg)
        seg = display_math(seg)
        out.append(seg)
    return "".join(out)


def _slug(text: str) -> str:
    s = re.sub(r"[^\w\- ]+", "", text.strip().lower())
    return re.sub(r"\s+", "-", s)


def restyle_document(doc: QTextDocument) -> None:
    """Apply the dark palette to a document produced by setMarkdown()."""
    block_jobs: list[tuple[int, QTextBlockFormat]] = []
    char_jobs:  list[tuple[int, int, QTextCharFormat]] = []

    block = doc.begin()
    while block.isValid():
        bf = block.blockFormat()
        start = block.position()
        end = start + max(block.length() - 1, 0)
        is_code = bf.hasProperty(QTextFormat.Property.BlockCodeLanguage) or bf.nonBreakableLines()
        level = bf.headingLevel()

        if is_code:
            nbf = QTextBlockFormat()
            nbf.setBackground(QColor(theme.SURFACE2))
            nbf.setLeftMargin(10); nbf.setRightMargin(10)
            nbf.setTopMargin(1);   nbf.setBottomMargin(1)
            # Let long formula / code lines wrap instead of forcing a horizontal
            # scrollbar on the whole reader.
            nbf.setNonBreakableLines(False)
            block_jobs.append((start, nbf))
            cf = QTextCharFormat()
            cf.setFontFamilies(_MONO); cf.setFontFixedPitch(True)
            cf.setForeground(QColor(_CODE_FG))
            char_jobs.append((start, end, cf))
        elif level:
            nbf = QTextBlockFormat()
            nbf.setTopMargin(20 if level <= 2 else 14)
            nbf.setBottomMargin(6)
            block_jobs.append((start, nbf))
            cf = QTextCharFormat()
            cf.setForeground(QColor(theme.ACCENT if level == 1 else theme.TEXT))
            cf.setAnchor(True)
            cf.setAnchorNames([_slug(block.text())])
            char_jobs.append((start, end, cf))
        elif bf.hasProperty(QTextFormat.Property.BlockQuoteLevel):
            nbf = QTextBlockFormat()
            nbf.setLeftMargin(18)
            nbf.setBackground(QColor(theme.SURFACE2))
            block_jobs.append((start, nbf))
            cf = QTextCharFormat()
            cf.setForeground(QColor(theme.TEXT_MUTED))
            char_jobs.append((start, end, cf))

        if not is_code:
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                f = frag.charFormat()
                if f.isAnchor() and f.anchorHref():
                    cf = QTextCharFormat()
                    cf.setForeground(QColor(theme.ACCENT))
                    cf.setFontUnderline(True)
                    char_jobs.append((frag.position(), frag.position() + frag.length(), cf))
                elif f.fontFixedPitch():
                    cf = QTextCharFormat()
                    cf.setFontFamilies(_MONO)
                    cf.setForeground(QColor(_CODE_FG))
                    cf.setBackground(QColor(theme.SURFACE2))
                    char_jobs.append((frag.position(), frag.position() + frag.length(), cf))
                it += 1
        block = block.next()

    cursor = QTextCursor(doc)
    cursor.beginEditBlock()
    for pos, nbf in block_jobs:
        cursor.setPosition(pos)
        cursor.mergeBlockFormat(nbf)
    for s, e, cf in char_jobs:
        if e <= s:
            continue
        cursor.setPosition(s)
        cursor.setPosition(e, QTextCursor.MoveMode.KeepAnchor)
        cursor.mergeCharFormat(cf)
    _style_tables(doc.rootFrame())
    cursor.endEditBlock()


def _style_tables(frame) -> None:
    for child in frame.childFrames():
        if isinstance(child, QTextTable):
            fmt = child.format()
            fmt.setBorder(1)
            fmt.setBorderBrush(QBrush(QColor(theme.BORDER)))
            fmt.setBorderStyle(QTextFrameFormat.BorderStyle.BorderStyle_Solid)
            fmt.setBorderCollapse(True)
            fmt.setCellPadding(6)
            fmt.setCellSpacing(0)
            fmt.setTopMargin(8); fmt.setBottomMargin(8)
            child.setFormat(fmt)
            if child.rows() > 0:
                for c in range(child.columns()):
                    cell = child.cellAt(0, c)
                    if cell.isValid():
                        cf = cell.format()
                        cf.setBackground(QColor(theme.SURFACE2))
                        cell.setFormat(cf)
        _style_tables(child)


# ----------------------------------------------------------------------------
# Screen
# ----------------------------------------------------------------------------

class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()
    doc_opened     = pyqtSignal(str)   # relative path of the doc just rendered

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
        top_bar.setStyleSheet(f"background-color: {theme.SURFACE}; border-bottom: 1px solid {theme.BORDER};")
        top = QHBoxLayout(top_bar)
        top.setContentsMargins(24, 10, 24, 10)
        top.setSpacing(12)

        title_lbl = QLabel("Reference")
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {theme.TEXT};")
        top.addWidget(title_lbl)

        self._chapter_combo = QComboBox()
        self._chapter_combo.setMinimumWidth(220)
        self._chapter_combo.addItem(_ALL_CHAPTERS)
        self._chapter_combo.currentIndexChanged.connect(self._rebuild_list)
        top.addWidget(self._chapter_combo)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search titles and text…")
        self._search.setClearButtonEnabled(True)
        self._search.setMinimumWidth(200)
        self._search.textChanged.connect(self._rebuild_list)
        top.addWidget(self._search, 1)

        self._solutions_cb = QCheckBox("Show solutions")
        self._solutions_cb.setChecked(True)
        self._solutions_cb.toggled.connect(self._rerender_current)
        top.addWidget(self._solutions_cb)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        top.addWidget(back_btn)
        root.addWidget(top_bar)

        # ── Body: nav list | reader ────────────────────────────────────
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setChildrenCollapsible(False)

        self._list = QListWidget()
        self._list.setMinimumWidth(240)
        self._list.setMaximumWidth(360)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setWordWrap(True)
        self._list.currentItemChanged.connect(self._on_item_changed)
        self._splitter.addWidget(self._list)

        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(self._on_anchor_clicked)
        self._browser.document().setDocumentMargin(20)
        self._splitter.addWidget(self._browser)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(16, 16, 16, 12)
        body_layout.setSpacing(8)
        body_layout.addWidget(self._splitter, 1)

        self._path_lbl = QLabel("")
        self._path_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        body_layout.addWidget(self._path_lbl)
        root.addWidget(body, 1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def entries(self) -> list[DocEntry]:
        return list(self._entries)

    @property
    def current_doc(self) -> DocEntry | None:
        return self._current

    def load_all(self) -> None:
        """Discover docs on first use and show the landing page (README)."""
        if self._loaded:
            return
        self._loaded = True
        self.reload()

    def reload(self) -> None:
        """Rescan the docs directory and rebuild the navigation."""
        self._entries = discover_docs()
        self._chapter_combo.blockSignals(True)
        self._chapter_combo.clear()
        self._chapter_combo.addItem(_ALL_CHAPTERS)
        seen: list[str] = []
        for e in self._entries:
            if e.chapter not in seen:
                seen.append(e.chapter)
        for ch in seen:
            self._chapter_combo.addItem(ch)
        self._chapter_combo.blockSignals(False)

        if not self._entries:
            self._list.clear()
            self._current = None
            self._browser.setMarkdown(
                "# Docs not found\n\n"
                f"Expected the shared documentation folder at:\n\n`{_DOCS_ROOT}`\n\n"
                "Keep the `flashcard-drill/` folder inside the Quantum-Computing "
                "checkout so the `docs/` corpus can be located (the working "
                "directory does not matter)."
            )
            restyle_document(self._browser.document())
            self._path_lbl.setText(str(_DOCS_ROOT))
            return

        self._rebuild_list()
        if self._list.currentItem() is None or self._current is None:
            landing = next((e for e in self._entries if e.chapter_key == ""), self._entries[0])
            self.select_doc(landing.rel)

    def select_doc(self, rel_path: str, fragment: str | None = None) -> bool:
        """Open a doc by path relative to docs/ (e.g. '04_quantum_algorithms/05_grover_search.md')."""
        target = re.sub(r"^(\./)+", "", rel_path.replace("\\", "/"))
        entry = next((e for e in self._entries if e.rel == target), None)
        if entry is None:
            return False
        # Make sure the entry is visible in the list, widening the filter if needed.
        if self._chapter_combo.currentText() not in (_ALL_CHAPTERS, entry.chapter):
            self._chapter_combo.setCurrentIndex(0)
        item = self._find_item(entry)
        if item is None:
            self._search.clear()
            item = self._find_item(entry)
        if item is not None:
            self._list.setCurrentItem(item)      # triggers _on_item_changed -> _show_doc
        else:
            self._show_doc(entry)
        if fragment:
            self._browser.scrollToAnchor(fragment)
        return True

    def set_chapter(self, chapter_label: str) -> None:
        idx = self._chapter_combo.findText(chapter_label)
        if idx >= 0:
            self._chapter_combo.setCurrentIndex(idx)

    def set_search(self, text: str) -> None:
        self._search.setText(text)

    def visible_titles(self) -> list[str]:
        """Titles of docs currently listed in the nav (after chapter/search filters)."""
        out = []
        for i in range(self._list.count()):
            it = self._list.item(i)
            if it.data(Qt.ItemDataRole.UserRole) is not None:
                out.append(it.data(Qt.ItemDataRole.UserRole + 1))
        return out

    # ------------------------------------------------------------------
    # Navigation list
    # ------------------------------------------------------------------

    def _find_item(self, entry: DocEntry) -> QListWidgetItem | None:
        for i in range(self._list.count()):
            it = self._list.item(i)
            idx = it.data(Qt.ItemDataRole.UserRole)
            if idx is not None and self._entries[idx] is entry:
                return it
        return None

    def _rebuild_list(self, *_args) -> None:
        chapter = self._chapter_combo.currentText()
        query = self._search.text().strip().lower()
        keep = self._current

        self._list.blockSignals(True)
        self._list.clear()
        last_chapter = None
        for idx, e in enumerate(self._entries):
            if chapter != _ALL_CHAPTERS and e.chapter != chapter:
                continue
            hits = 0
            if query:
                in_title = query in e.title.lower()
                hits = e.text().lower().count(query)
                if not in_title and hits == 0:
                    continue
            if e.chapter != last_chapter:
                hdr = QListWidgetItem(e.chapter.upper())
                hdr.setFlags(Qt.ItemFlag.NoItemFlags)
                f = QFont(); f.setBold(True); f.setPointSize(8)
                hdr.setFont(f)
                hdr.setForeground(QColor(theme.TEXT_MUTED))
                self._list.addItem(hdr)
                last_chapter = e.chapter
            label = e.title if not (query and hits) else f"{e.title}  ({hits})"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            item.setData(Qt.ItemDataRole.UserRole + 1, e.title)
            item.setToolTip(e.rel)
            self._list.addItem(item)
            if e is keep:
                self._list.setCurrentItem(item)
        self._list.blockSignals(False)

        # With an active search, jump straight to the first matching doc so the
        # reader shows something relevant (and highlight the first occurrence).
        if query and self._list.currentItem() is None:
            for i in range(self._list.count()):
                if self._list.item(i).data(Qt.ItemDataRole.UserRole) is not None:
                    self._list.setCurrentItem(self._list.item(i))
                    break
        elif query and self._current is not None:
            self._highlight_query()

    def _on_item_changed(self, current: QListWidgetItem | None, _previous=None) -> None:
        if current is None:
            return
        idx = current.data(Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        entry = self._entries[idx]
        if entry is not self._current:
            self._show_doc(entry)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _show_doc(self, entry: DocEntry, keep_scroll: bool = False) -> None:
        scroll = self._browser.verticalScrollBar().value() if keep_scroll else 0
        self._current = entry
        md = prepare_markdown(entry.text(), doc_dir=entry.path.parent,
                              show_solutions=self._solutions_cb.isChecked())
        self._browser.setMarkdown(md)
        restyle_document(self._browser.document())
        self._browser.verticalScrollBar().setValue(scroll)
        self._path_lbl.setText(f"{entry.chapter}  ›  {entry.title}     docs/{entry.rel}")
        self._highlight_query()
        self.doc_opened.emit(entry.rel)

    def _rerender_current(self, *_args) -> None:
        if self._current is not None:
            self._show_doc(self._current, keep_scroll=True)

    def _highlight_query(self) -> None:
        query = self._search.text().strip()
        if not query:
            return
        cursor = self._browser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self._browser.setTextCursor(cursor)
        self._browser.find(query)

    # ------------------------------------------------------------------
    # Links
    # ------------------------------------------------------------------

    def _on_anchor_clicked(self, url: QUrl) -> None:
        scheme = url.scheme().lower()
        if scheme in ("http", "https", "mailto"):
            QDesktopServices.openUrl(url)
            return
        path = url.path()
        fragment = url.fragment() or None
        if not path:                      # same-document anchor
            if fragment:
                self._browser.scrollToAnchor(fragment)
            return
        base = self._current.path.parent if self._current else _DOCS_ROOT
        target = (base / path).resolve()
        try:
            rel = target.relative_to(_DOCS_ROOT.resolve()).as_posix()
        except ValueError:
            rel = None
        if rel is not None and self.select_doc(rel, fragment):
            return
        if target.exists():               # a non-doc file inside the repo (e.g. a notebook)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))
