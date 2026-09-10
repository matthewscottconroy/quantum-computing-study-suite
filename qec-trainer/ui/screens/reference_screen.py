"""Reference screen — in-app browser for the shared ``docs/`` corpus.

This replaces the earlier problem-card browser (which only linked *out* to the
docs) with the suite-wide in-app docs browser (REFERENCE CONTRACT):

* the docs root is resolved relative to this file —
  ``<repo>/qec-trainer/ui/screens/reference_screen.py`` → ``parents[3] / "docs"``
  — never from a hard-coded home path;
* every ``docs/**/*.md`` file is listed, grouped by chapter directory, with a
  chapter filter and a title / full-text search; the tree is rescanned when
  files were added, removed or edited since the last visit;
* documents are rendered with QTextBrowser's GitHub-dialect Markdown support
  and restyled for the dark theme.  Relative links between docs — including
  the bare ``NN_chapter/NN_file.md`` cross-references the corpus writes in
  prose (optionally with a ``#heading`` suffix), which are turned into links —
  navigate inside the browser, ``#fragment`` links jump to headings (which get
  GitHub-style anchors, duplicates suffixed ``-1``, ``-2``, …), external links
  open in the system browser;
* ``$$ … $$`` display math and ``<details><summary>`` solution blocks, which
  Qt's Markdown importer cannot render, are rewritten before rendering (a
  formula inside a block quote stays inside the quote).

The one affordance kept from the old screen is "jump to the docs for a
problem category": ``CATEGORY_DOC`` maps each trainer topic to its chapter and
the "Jump to topic" picker / :meth:`ReferenceScreen.show_category` open it.
"""
from __future__ import annotations

import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QListWidget, QListWidgetItem, QTextBrowser, QSplitter,
    QFrame, QCheckBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import (
    QDesktopServices, QPalette, QColor, QBrush, QFont, QTextCursor,
    QTextBlockFormat, QTextCharFormat, QTextFormat, QTextFrameFormat,
    QTextTable, QTextDocument,
)

from ui import theme

_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"

# ── App-specific: which rung of the ladder this trainer drills ───────────────
# Chapter directory opened first when the screen is shown.
_APP_CHAPTER_DIR = "05_quantum_error_correction"

# Problem category -> doc (relative to docs/) that best covers it.  Drives the
# "Jump to topic" picker and show_category(); missing files are skipped.
CATEGORY_DOC: dict[str, str] = {
    "Repetition Code":      "05_quantum_error_correction/03_repetition_code.md",
    "Stabilizer Formalism": "05_quantum_error_correction/04_stabilizer_formalism.md",
    "Steane Code":          "05_quantum_error_correction/05_css_codes_and_steane.md",
    "Surface Code":         "05_quantum_error_correction/06_surface_code.md",
    "Fault Tolerance":      "05_quantum_error_correction/07_fault_tolerance.md",
    "Bosonic Codes":        "05_quantum_error_correction/08_bosonic_codes.md",
    "Decoder Game":         "05_quantum_error_correction/06_surface_code.md",
}
# ── end app-specific ─────────────────────────────────────────────────────────

_ALL_CHAPTERS     = "All chapters"
_OVERVIEW_CHAPTER = "Overview"
_JUMP_PLACEHOLDER = "Jump to topic…"
_CODE_FG          = "#a5d6ff"      # code / formula foreground on the dark surface
_MONO             = ["JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "Menlo", "monospace"]
_SMALL_WORDS      = {"and", "of", "the", "for", "to", "in", "on", "a", "an"}
_INDEX_ROLE       = Qt.ItemDataRole.UserRole
_MATH_LANG        = "math"         # fence info string given to rewritten $$ blocks


# ----------------------------------------------------------------------------
# Doc discovery (module level so it can be unit-tested without a widget)
# ----------------------------------------------------------------------------

@dataclass
class DocEntry:
    path: Path
    rel: str             # path relative to the docs root, posix style
    chapter: str         # chapter directory name ("" for top-level files)
    chapter_label: str   # human-readable chapter name
    title: str           # first "# " heading, else prettified file stem
    label: str           # text shown in the list ("5.6  The Surface Code")
    _text: str | None = field(default=None, repr=False, compare=False)
    _haystack: str | None = field(default=None, repr=False, compare=False)

    def text(self) -> str:
        """File contents (cached); unreadable files render their error inline."""
        if self._text is None:
            try:
                self._text = self.path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                self._text = f"# {self.title}\n\nCould not read `{self.path}`:\n\n```\n{exc}\n```\n"
        return self._text

    def haystack(self) -> str:
        """Lower-cased title + path + body used by the search box."""
        if self._haystack is None:
            self._haystack = f"{self.title}\n{self.rel}\n{self.text()}".lower()
        return self._haystack


def docs_root() -> Path:
    return _DOCS_ROOT


def _iter_docs(root: Path):
    """Every ``root/**/*.md`` file in sorted order, skipping hidden / ``_`` parts."""
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*.md")):
        if path.is_file() and not any(part.startswith((".", "_"))
                                      for part in path.relative_to(root).parts):
            yield path


def corpus_signature(root: Path | None = None) -> tuple:
    """Cheap fingerprint of the docs tree (paths, sizes, mtimes).

    :meth:`ReferenceScreen.load_all` compares it with the one taken at the
    last scan, so files added, removed or edited while the app is running are
    picked up the next time the screen is used.
    """
    root = root or _DOCS_ROOT
    sig: list[tuple[str, int, int]] = []
    for path in _iter_docs(root):
        try:
            st = path.stat()
        except OSError:
            continue
        sig.append((path.relative_to(root).as_posix(), st.st_size, st.st_mtime_ns))
    return tuple(sig)


def scan_docs(root: Path | None = None) -> list[DocEntry]:
    """List every Markdown file under ``root`` in ladder order.

    Top-level files (the README) come first, then chapter directories in their
    numeric/lexical order, then files within each chapter.
    """
    root = root or _DOCS_ROOT
    entries: list[DocEntry] = []
    for path in _iter_docs(root):
        rel = path.relative_to(root).as_posix()
        chapter = path.parent.relative_to(root).as_posix() if path.parent != root else ""
        title = _read_title(path) or _pretty_words(path.stem)
        entries.append(DocEntry(
            path=path, rel=rel, chapter=chapter,
            chapter_label=_pretty_chapter(chapter), title=title,
            label=_list_label(chapter, path.stem, title),
        ))
    entries.sort(key=lambda e: (e.chapter != "", e.chapter, e.rel))
    return entries


def _read_title(path: Path, max_lines: int = 40) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for _ in range(max_lines):
                line = fh.readline()
                if not line:
                    break
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        pass
    return ""


_NUM_PREFIX = re.compile(r"^(\d+)[_\-\s]*(.*)$")


def _split_prefix(name: str) -> tuple[str, str]:
    m = _NUM_PREFIX.match(name)
    return (m.group(1), m.group(2)) if m else ("", name)


def _pretty_words(stem: str) -> str:
    """'03_quantum_gates_and_circuits' -> 'Quantum Gates and Circuits'."""
    _, rest = _split_prefix(stem)
    words = [w for w in re.split(r"[_\-\s]+", rest) if w]
    out = []
    for i, w in enumerate(words):
        out.append(w.lower() if (i > 0 and w.lower() in _SMALL_WORDS) else w[:1].upper() + w[1:])
    return " ".join(out) or stem


def _pretty_chapter(chapter: str) -> str:
    if not chapter:
        return _OVERVIEW_CHAPTER
    num, _ = _split_prefix(chapter.split("/")[-1])
    name = _pretty_words(chapter.split("/")[-1])
    return f"{int(num)}. {name}" if num else name


def _list_label(chapter: str, stem: str, title: str) -> str:
    cnum, _ = _split_prefix(chapter.split("/")[-1]) if chapter else ("", "")
    fnum, _ = _split_prefix(stem)
    if cnum and fnum:
        return f"{int(cnum)}.{int(fnum)}  {title}"
    if fnum:
        return f"{int(fnum)}  {title}"
    return title


# ----------------------------------------------------------------------------
# Markdown preparation
# ----------------------------------------------------------------------------

# Fences may be indented up to 3 spaces (CommonMark), e.g. inside list items.
_FENCE         = re.compile(r"(^ {0,3}(?:```|~~~).*?^ {0,3}(?:```|~~~)[ \t]*$)", re.M | re.S)
_CODE_SPAN     = re.compile(r"(`+)(.+?)\1")
_DISPLAY_MATH  = re.compile(r"\$\$(.+?)\$\$", re.S)
_DETAILS_BLOCK = re.compile(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", re.I | re.S)
_DETAILS_OPEN  = re.compile(r"<details>\s*<summary>(.*?)</summary>", re.I | re.S)
_DETAILS_CLOSE = re.compile(r"</details>", re.I)
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
    * ``$$ … $$`` display math -> fenced code block tagged ``math``, so the
      formula source stays legible and monospaced instead of collapsing into a
      paragraph (the tag lets :func:`restyle_document` soft-wrap long formula
      lines while author-written code fences keep their layout); a formula
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
                return f"\n{p}\n{p}```{_MATH_LANG}\n{lines}\n{p}```\n{p}\n{p}"
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


def heading_slug(text: str) -> str:
    """GitHub-style anchor for a heading: 'Key Formulas' -> 'key-formulas'.

    Lower-cased, punctuation dropped, *each* space turned into a hyphen — so
    'QFT ≠ Classical FFT' -> 'qft--classical-fft', as GitHub renders it.  The
    ``-1``, ``-2``, … suffixes GitHub adds to repeated headings are applied per
    document by :func:`restyle_document`.
    """
    return re.sub(r"[^\w\- ]+", "", text.strip().lower()).replace(" ", "-")


def restyle_document(doc: QTextDocument) -> None:
    """Apply the dark palette to a document produced by ``setMarkdown()``.

    Qt's Markdown importer builds the document directly (the widget stylesheet
    does not reach into it), so code blocks, inline code, headings (which also
    get GitHub-style ``#slug`` anchors, repeated headings suffixed ``-1``,
    ``-2``, …), block quotes, links and tables are restyled here.  Only the
    ``math`` blocks generated from ``$$`` formulas are allowed to soft-wrap;
    author-written code fences keep their line layout.
    """
    block_jobs: list[tuple[int, QTextBlockFormat]] = []
    char_jobs:  list[tuple[int, int, QTextCharFormat]] = []
    slugs: Counter[str] = Counter()

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
            # keep the indent of a code block that sits inside a block quote
            nbf.setLeftMargin(max(bf.leftMargin(), 10.0)); nbf.setRightMargin(10)
            nbf.setTopMargin(1);   nbf.setBottomMargin(1)
            if bf.stringProperty(QTextFormat.Property.BlockCodeLanguage) == _MATH_LANG:
                nbf.setNonBreakableLines(False)     # wrap long formula lines only
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
            slug = heading_slug(block.text())
            seen_before = slugs[slug]
            slugs[slug] += 1
            cf.setAnchorNames([f"{slug}-{seen_before}" if seen_before else slug])
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
                span = (frag.position(), frag.position() + frag.length())
                if f.isAnchor() and f.anchorHref():
                    cf = QTextCharFormat()
                    cf.setForeground(QColor(theme.ACCENT))
                    cf.setFontUnderline(True)
                    char_jobs.append((*span, cf))
                elif f.fontFixedPitch():
                    cf = QTextCharFormat()
                    cf.setFontFamilies(_MONO)
                    cf.setForeground(QColor(_CODE_FG))
                    cf.setBackground(QColor(theme.SURFACE2))
                    char_jobs.append((*span, cf))
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


def _header_item(chapter_label: str) -> QListWidgetItem:
    item = QListWidgetItem(chapter_label.upper())
    item.setFlags(Qt.ItemFlag.NoItemFlags)
    item.setForeground(QColor(theme.TEXT_MUTED))
    font = QFont()
    font.setBold(True)
    font.setPointSize(8)
    item.setFont(font)
    return item


# ----------------------------------------------------------------------------
# Screen
# ----------------------------------------------------------------------------

class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()
    doc_opened     = pyqtSignal(str)    # docs-relative path of the doc just rendered

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._entries: list[DocEntry] = []
        self._current: DocEntry | None = None
        self._loaded = False
        self._signature: tuple = ()          # corpus_signature() at the last scan
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setObjectName("referenceScreen")
        # The app theme has no rules for list / splitter / line-edit widgets,
        # so style them here, scoped by object name.
        self.setStyleSheet(
            f"QListWidget#refList {{ background: {theme.SURFACE}; color: {theme.TEXT};"
            f" border: none; border-right: 1px solid {theme.BORDER}; padding: 8px 4px; outline: 0; }}"
            f"QListWidget#refList::item {{ padding: 5px 8px; border-radius: 4px; }}"
            f"QListWidget#refList::item:hover {{ background: {theme.SURFACE2}; }}"
            f"QListWidget#refList::item:selected {{ background: {theme.ACCENT2}; color: white; }}"
            f"QLineEdit#refSearch {{ background: {theme.SURFACE2}; color: {theme.TEXT};"
            f" border: 1px solid {theme.BORDER}; border-radius: 6px; padding: 6px 10px; font-size: 13px; }}"
            f"QLineEdit#refSearch:focus {{ border-color: {theme.ACCENT}; }}"
            f"QSplitter#refSplitter::handle {{ background: {theme.BORDER}; width: 1px; }}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ────────────────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setStyleSheet(
            f"background-color: {theme.SURFACE}; border-bottom: 1px solid {theme.BORDER};"
        )
        top = QHBoxLayout(top_bar)
        top.setContentsMargins(24, 10, 24, 10)
        top.setSpacing(12)

        title_lbl = QLabel("Reference")
        title_lbl.setObjectName("heading")
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {theme.TEXT};")
        top.addWidget(title_lbl)
        top.addSpacing(8)

        self._jump = QComboBox()
        self._jump.setMinimumWidth(180)
        self._jump.setToolTip("Open the chapter that covers a trainer topic")
        self._jump.addItem(_JUMP_PLACEHOLDER, "")
        self._jump.activated.connect(self._on_jump_activated)
        top.addWidget(self._jump)

        self._chapter_filter = QComboBox()
        self._chapter_filter.setMinimumWidth(220)
        self._chapter_filter.setToolTip("Show only one chapter")
        self._chapter_filter.addItem(_ALL_CHAPTERS, "")
        self._chapter_filter.currentIndexChanged.connect(self._rebuild_list)
        top.addWidget(self._chapter_filter)

        self._search = QLineEdit()
        self._search.setObjectName("refSearch")
        self._search.setPlaceholderText("Search titles and text…")
        self._search.setClearButtonEnabled(True)
        self._search.setMinimumWidth(180)
        self._search.textChanged.connect(self._rebuild_list)
        top.addWidget(self._search, 1)

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("flat")
        self._back_btn.clicked.connect(self.back_requested)
        top.addWidget(self._back_btn)
        root.addWidget(top_bar)

        # ── Body: chapter list | document ──────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("refSplitter")
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        left = QWidget()
        left.setStyleSheet(f"background: {theme.SURFACE};")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(
            f"font-size: 11px; color: {theme.TEXT_MUTED}; padding: 8px 12px 0 12px;"
        )
        left_layout.addWidget(self._count_lbl)
        self._list = QListWidget()
        self._list.setObjectName("refList")
        self._list.setMinimumWidth(240)
        self._list.setWordWrap(True)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.currentItemChanged.connect(self._on_item_changed)
        left_layout.addWidget(self._list, 1)
        splitter.addWidget(left)

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
        self._doc_path.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        self._doc_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        head_col.addWidget(self._doc_path)
        header_layout.addLayout(head_col, 1)

        self._solutions_cb = QCheckBox("Show solutions")
        self._solutions_cb.setChecked(True)
        self._solutions_cb.setToolTip("Hide exercise solutions to test yourself first")
        self._solutions_cb.toggled.connect(self._rerender_current)
        header_layout.addWidget(self._solutions_cb, 0, Qt.AlignmentFlag.AlignTop)

        self._open_btn = QPushButton("Open externally")
        self._open_btn.setObjectName("flat")
        self._open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_btn.setToolTip("Open this Markdown file with the system default application")
        self._open_btn.clicked.connect(self._open_externally)
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
            f"QTextBrowser {{ background-color: {theme.BG}; color: {theme.TEXT};"
            f" border: none; padding: 12px 20px; font-size: 14px; }}"
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
        splitter.setSizes([300, 800])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def docs_root() -> Path:
        return _DOCS_ROOT

    @property
    def entries(self) -> list[DocEntry]:
        return list(self._entries)

    @property
    def current_entry(self) -> DocEntry | None:
        return self._current

    def current_doc_path(self) -> Path | None:
        return self._current.path if self._current else None

    def load_all(self) -> None:
        """Scan docs/**/*.md on first use; later calls keep the reader's place.

        The first document shown is the first file of this app's chapter
        (``_APP_CHAPTER_DIR``) so the trainer opens on its own rung of the
        ladder; the whole corpus stays listed.  When the tree changed since the
        last scan (a file added, removed or edited) the corpus is rescanned via
        :meth:`reload`, which keeps the filters and the current document.
        """
        if self._loaded:
            if corpus_signature(_DOCS_ROOT) != self._signature:
                self.reload()
            return
        self._scan()
        if not self._entries:
            self._show_missing_docs()
            return
        self._render(self._default_entry())
        self._rebuild_list()

    def reload(self) -> None:
        """Rescan the docs tree, preserving the chapter filter, the search text
        and — when it still exists — the current document and scroll position.
        Called by :meth:`load_all` when the corpus changed; safe to call directly."""
        chapter = self._chapter_filter.currentData() or ""
        query = self._search.text()
        current_rel = self._current.rel if self._current else None
        self._scan()

        self._chapter_filter.blockSignals(True)
        idx = self._chapter_filter.findData(chapter)
        self._chapter_filter.setCurrentIndex(idx if idx >= 0 else 0)
        self._chapter_filter.blockSignals(False)
        self._search.blockSignals(True)
        self._search.setText(query)
        self._search.blockSignals(False)

        if not self._entries:
            self._show_missing_docs()
            return
        entry = next((e for e in self._entries if e.rel == current_rel), None)
        if entry is None:
            self._current = None
            entry = self._default_entry()
            self._render(entry)
        else:
            self._render(entry, keep_scroll=True)
        self._rebuild_list(keep=entry)

    def _default_entry(self) -> DocEntry:
        """First file of this app's chapter, else the first document listed."""
        return next((e for e in self._entries if e.chapter == _APP_CHAPTER_DIR), self._entries[0])

    def _scan(self) -> None:
        """(Re)read the docs tree and repopulate the chapter / topic pickers."""
        self._loaded = True
        self._signature = corpus_signature(_DOCS_ROOT)
        self._entries = scan_docs(_DOCS_ROOT)

        self._chapter_filter.blockSignals(True)
        self._chapter_filter.clear()
        self._chapter_filter.addItem(_ALL_CHAPTERS, "")
        seen: list[tuple[str, str]] = []
        for e in self._entries:
            if (e.chapter, e.chapter_label) not in seen:
                seen.append((e.chapter, e.chapter_label))
        for chapter, label in seen:
            self._chapter_filter.addItem(label, chapter)
        self._chapter_filter.blockSignals(False)

        known = {e.rel for e in self._entries}
        self._jump.blockSignals(True)
        self._jump.clear()
        self._jump.addItem(_JUMP_PLACEHOLDER, "")
        for category, rel in CATEGORY_DOC.items():
            if rel in known:
                self._jump.addItem(category, category)
        self._jump.blockSignals(False)
        self._jump.setVisible(self._jump.count() > 1)

    def open_doc(self, rel_path: str, fragment: str | None = None) -> bool:
        """Show the document at ``rel_path`` (relative to the docs root).

        Clears active filters if they would hide it; scrolls to ``fragment``
        (a heading slug) when given.  Returns True when the document exists.
        """
        self.load_all()
        target = re.sub(r"^(\./)+", "", rel_path.replace("\\", "/"))
        entry = next((e for e in self._entries if e.rel == target), None)
        if entry is None:
            return False
        item = self._item_for(entry)
        if item is None:                          # hidden by the filters
            self._search.blockSignals(True)
            self._search.clear()
            self._search.blockSignals(False)
            self._chapter_filter.blockSignals(True)
            self._chapter_filter.setCurrentIndex(0)
            self._chapter_filter.blockSignals(False)
            self._rebuild_list(keep=entry)        # select the target, not the first match
            item = self._item_for(entry)
        if item is not None:
            self._list.setCurrentItem(item)       # renders via _on_item_changed
        if entry is not self._current:
            self._render(entry)
        if fragment:
            self._browser.scrollToAnchor(fragment)
        return True

    def show_chapter(self, chapter_dir: str) -> None:
        """Filter the list to one chapter directory ("" = all)."""
        self.load_all()
        idx = self._chapter_filter.findData(chapter_dir)
        self._chapter_filter.setCurrentIndex(idx if idx >= 0 else 0)

    def show_category(self, category: str) -> bool:
        """Open the doc that covers a trainer problem category (see CATEGORY_DOC)."""
        rel = CATEGORY_DOC.get(category)
        return bool(rel) and self.open_doc(rel)

    def set_search(self, text: str) -> None:
        self._search.setText(text)

    def visible_titles(self) -> list[str]:
        """Titles of the docs currently listed (after chapter/search filters)."""
        out: list[str] = []
        for row in range(self._list.count()):
            idx = self._list.item(row).data(_INDEX_ROLE)
            if idx is not None:
                out.append(self._entries[idx].title)
        return out

    # ------------------------------------------------------------------
    # List population / filtering
    # ------------------------------------------------------------------

    def _rebuild_list(self, *_args, keep: DocEntry | None = None) -> None:
        """Repopulate the list for the current filters.

        ``keep`` (default: the document being read) stays selected when it is
        still listed; otherwise the first match is selected and rendered.
        """
        chapter = self._chapter_filter.currentData() or ""
        query = self._search.text().strip().lower()
        keep = keep or self._current

        self._list.blockSignals(True)
        self._list.clear()
        last_chapter = None
        keep_item = None
        visible = 0
        for idx, e in enumerate(self._entries):
            if chapter and e.chapter != chapter:
                continue
            hits = 0
            if query:
                in_title = query in e.title.lower() or query in e.rel.lower()
                hits = e.haystack().count(query)
                if not in_title and not hits:
                    continue
            if e.chapter_label != last_chapter:
                self._list.addItem(_header_item(e.chapter_label))
                last_chapter = e.chapter_label
            item = QListWidgetItem(f"{e.label}  ({hits})" if (query and hits) else e.label)
            item.setData(_INDEX_ROLE, idx)
            item.setToolTip(f"docs/{e.rel}")
            self._list.addItem(item)
            visible += 1
            if e is keep:
                keep_item = item
        if keep_item is not None:
            self._list.setCurrentItem(keep_item)
        self._list.blockSignals(False)

        total = len(self._entries)
        self._count_lbl.setText(
            f"{visible} of {total} documents" if visible != total else f"{total} documents"
        )

        if keep_item is None:
            first = self._first_doc_item()
            if first is not None:
                self._list.setCurrentItem(first)      # renders the first match
        elif query:
            self._highlight_query()

    def _first_doc_item(self) -> QListWidgetItem | None:
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item.data(_INDEX_ROLE) is not None:
                return item
        return None

    def _item_for(self, entry: DocEntry) -> QListWidgetItem | None:
        for row in range(self._list.count()):
            item = self._list.item(row)
            idx = item.data(_INDEX_ROLE)
            if idx is not None and self._entries[idx] is entry:
                return item
        return None

    def _on_item_changed(self, current: QListWidgetItem | None, _previous=None) -> None:
        if current is None:
            return
        idx = current.data(_INDEX_ROLE)
        if idx is None or not (0 <= idx < len(self._entries)):
            return
        entry = self._entries[idx]
        if entry is not self._current:
            self._render(entry)

    def _on_jump_activated(self, index: int) -> None:
        category = self._jump.itemData(index) if index > 0 else ""
        self._jump.setCurrentIndex(0)
        if category:
            self.show_category(category)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self, entry: DocEntry, keep_scroll: bool = False) -> None:
        scroll = self._browser.verticalScrollBar().value() if keep_scroll else 0
        self._current = entry
        md = prepare_markdown(entry.text(), entry.path.parent, self._solutions_cb.isChecked())
        self._browser.document().setBaseUrl(QUrl.fromLocalFile(str(entry.path.parent) + "/"))
        self._browser.setMarkdown(md)
        try:
            restyle_document(self._browser.document())
        except Exception:
            pass                                   # cosmetic only — never block reading
        self._browser.verticalScrollBar().setValue(scroll)
        self._doc_title.setText(entry.title)
        self._doc_path.setText(f"{entry.chapter_label}  ·  docs/{entry.rel}")
        self._open_btn.setEnabled(True)
        self._highlight_query()
        self.doc_opened.emit(entry.rel)

    def _rerender_current(self, *_args) -> None:
        if self._current is not None:
            self._render(self._current, keep_scroll=True)

    def _show_missing_docs(self) -> None:
        self._current = None
        self._list.clear()
        self._count_lbl.setText("0 documents")
        self._doc_title.setText("No documentation found")
        self._doc_path.setText(str(_DOCS_ROOT))
        self._open_btn.setEnabled(False)
        self._browser.setMarkdown(
            "# No documentation found\n\n"
            f"Expected Markdown chapters under:\n\n`{_DOCS_ROOT}`\n\n"
            "The reference browser reads the shared `docs/` corpus at the root of "
            "the Quantum-Computing repository — run the app from inside a checkout."
        )

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
        if scheme in ("http", "https", "mailto", "ftp"):
            QDesktopServices.openUrl(url)
            return
        path = url.toLocalFile() if url.isLocalFile() else url.path()
        fragment = url.fragment() or None
        if not path:                               # same-document anchor
            if fragment:
                self._browser.scrollToAnchor(fragment)
            return
        base = self._current.path.parent if self._current else _DOCS_ROOT
        try:
            target = (Path(path) if Path(path).is_absolute() else base / path).resolve()
        except (OSError, RuntimeError):
            return
        try:
            rel = target.relative_to(_DOCS_ROOT.resolve()).as_posix()
        except ValueError:                         # outside docs/
            rel = None
        if rel is not None and target.suffix.lower() == ".md" and self.open_doc(rel, fragment):
            return
        if target.exists():                        # anything else: repo README, notebook, …
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _open_externally(self) -> None:
        if self._current is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._current.path)))
