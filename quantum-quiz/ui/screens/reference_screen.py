"""Reference screen — in-app browser for the shared docs/ corpus.

Ported from qec-trainer/ui/screens/reference_screen.py (the canonical in-app
docs browser).  The docs root is resolved *relative to this file*:

    <repo>/quantum-quiz/ui/screens/reference_screen.py
                                   parents[0] = screens
                                   parents[1] = ui
                                   parents[2] = quantum-quiz
                                   parents[3] = <repo>   -> <repo>/docs

Every ``docs/**/*.md`` file is listed (grouped by chapter directory) and
rendered with QTextBrowser's Markdown support.  Relative links between docs —
including the bare ``NN_chapter/NN_file.md`` / ``NN_file.md`` cross-references
the corpus writes in prose (optionally with a ``#heading`` suffix), which are
turned into links — navigate inside the browser; ``#fragment`` links jump to
headings; external links open in the system browser.  ``$$ … $$`` display
math and ``<details><summary>`` solution blocks, which Qt's Markdown importer
cannot render, are rewritten before rendering (a formula inside a block quote
stays inside the quote).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QListWidget, QListWidgetItem, QTextBrowser, QSplitter,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QTextCharFormat, QTextCursor, QTextDocument

from ui import theme

_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"

_ALL_CHAPTERS = "All chapters"
_OVERVIEW_CHAPTER = "Overview"

# Quiz subject -> docs chapter directory that best covers it.  Used by
# show_subject() so callers can deep-link; unknown subjects show everything.
SUBJECT_CHAPTER: dict[str, str] = {
    "Linear Algebra":                   "01_mathematical_foundations",
    "Abstract Algebra":                 "01_mathematical_foundations",
    "Representation Theory":            "01_mathematical_foundations",
    "Quantum Mechanics":                "02_quantum_mechanics",
    "Foundations of Quantum Mechanics": "02_quantum_mechanics",
    "Quantum Computing":                "03_quantum_gates_and_circuits",
    "Qiskit":                           "03_quantum_gates_and_circuits",
    "QASM":                             "03_quantum_gates_and_circuits",
    "Transpiling":                      "03_quantum_gates_and_circuits",
    "Quantum Algorithm Design":         "04_quantum_algorithms",
    "Qiskit Certification (C1000-179)": "08_advanced_topics",
}


@dataclass
class _DocEntry:
    path: Path
    rel: str            # path relative to the docs root, posix style
    chapter: str        # chapter directory name ("" for top-level files)
    chapter_label: str  # human-readable chapter name
    title: str          # first "# " heading, else the file stem
    label: str          # text shown in the list
    search_key: str     # lower-cased haystack for the search box


class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._docs: list[_DocEntry] = []
        self._loaded = False
        self._current: _DocEntry | None = None
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
        self._chapter_filter.addItem(_ALL_CHAPTERS, "")
        self._chapter_filter.currentIndexChanged.connect(self._apply_filter)
        top_layout.addWidget(self._chapter_filter)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search titles…")
        self._search.setClearButtonEnabled(True)
        self._search.setMinimumWidth(200)
        self._search.setStyleSheet(
            f"background: {theme.SURFACE2}; color: {theme.TEXT};"
            f" border: 1px solid {theme.BORDER}; border-radius: 6px; padding: 6px 10px;"
        )
        self._search.textChanged.connect(self._apply_filter)
        top_layout.addWidget(self._search)

        top_layout.addStretch()

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        top_layout.addWidget(back_btn)

        root.addWidget(top_bar)

        # ── Body: document list | rendered document ────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 8, 16)
        left_layout.setSpacing(8)

        self._count_lbl = QLabel("")
        self._count_lbl.setObjectName("muted")
        left_layout.addWidget(self._count_lbl)

        self._list = QListWidget()
        self._list.setMinimumWidth(260)
        self._list.setWordWrap(True)
        self._list.currentItemChanged.connect(self._on_item_changed)
        left_layout.addWidget(self._list, 1)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 16, 24, 16)
        right_layout.setSpacing(8)

        path_row = QHBoxLayout()
        self._path_lbl = QLabel("")
        self._path_lbl.setObjectName("muted")
        self._path_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        path_row.addWidget(self._path_lbl)
        path_row.addStretch()
        self._open_btn = QPushButton("Open externally")
        self._open_btn.setObjectName("flat")
        self._open_btn.setToolTip("Open this Markdown file with the system default application")
        self._open_btn.clicked.connect(self._open_externally)
        self._open_btn.setEnabled(False)
        path_row.addWidget(self._open_btn)
        right_layout.addLayout(path_row)

        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(self._on_anchor_clicked)
        self._browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {theme.SURFACE}; color: {theme.TEXT};"
            f" border: 1px solid {theme.BORDER}; border-radius: 8px; padding: 16px;"
            f" font-size: 14px; }}"
        )
        right_layout.addWidget(self._browser, 1)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([320, 780])
        root.addWidget(splitter, 1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def docs_root() -> Path:
        return _DOCS_ROOT

    def load_all(self) -> None:
        """Scan docs/**/*.md once and populate the list; later calls are no-ops.

        Keeping the previously selected document on re-entry lets the user
        bounce between the quiz and the same reference page.
        """
        if self._loaded:
            return
        self._loaded = True
        self._docs = _scan_docs(_DOCS_ROOT)

        # Populate the chapter filter (keep "All chapters" at index 0).
        self._chapter_filter.blockSignals(True)
        while self._chapter_filter.count() > 1:
            self._chapter_filter.removeItem(1)
        seen: list[tuple[str, str]] = []
        for d in self._docs:
            key = (d.chapter, d.chapter_label)
            if key not in seen:
                seen.append(key)
        for chapter, label in seen:
            self._chapter_filter.addItem(label, chapter)
        self._chapter_filter.blockSignals(False)

        # Populate the list.
        self._list.blockSignals(True)
        self._list.clear()
        for idx, d in enumerate(self._docs):
            item = QListWidgetItem(d.label)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            item.setToolTip(d.rel)
            self._list.addItem(item)
        self._list.blockSignals(False)

        if not self._docs:
            self._browser.setMarkdown(
                "# No documentation found\n\n"
                f"Expected Markdown files under:\n\n`{_DOCS_ROOT}`\n\n"
                "Make sure the app is run from inside the study-suite repository."
            )
            self._count_lbl.setText("0 documents")
            return

        self._apply_filter()
        if self._list.currentItem() is None:
            self._select_first_visible()

    def reload(self) -> None:
        """Force a rescan of the docs folder (e.g. after files were added)."""
        self._loaded = False
        self._current = None
        self.load_all()

    def open_doc(self, rel_path: str) -> bool:
        """Show the document at ``rel_path`` (relative to the docs root).

        Clears active filters if they would hide the document.  Returns True
        when the document exists.
        """
        self.load_all()
        target = rel_path.replace("\\", "/").lstrip("./")
        for row in range(self._list.count()):
            item = self._list.item(row)
            d = self._docs[item.data(Qt.ItemDataRole.UserRole)]
            if d.rel == target:
                if item.isHidden():
                    self._search.clear()
                    self._chapter_filter.setCurrentIndex(0)
                self._list.setCurrentItem(item)
                return True
        return False

    def show_chapter(self, chapter_dir: str) -> None:
        """Filter the list to one chapter directory ("" = all)."""
        self.load_all()
        idx = self._chapter_filter.findData(chapter_dir)
        self._chapter_filter.setCurrentIndex(idx if idx >= 0 else 0)

    def show_subject(self, subject: str) -> None:
        """Filter to the chapter that best covers a quiz subject."""
        self.show_chapter(SUBJECT_CHAPTER.get(subject, ""))

    def current_doc_path(self) -> Path | None:
        return self._current.path if self._current else None

    # ------------------------------------------------------------------
    # Filtering / selection
    # ------------------------------------------------------------------

    def _apply_filter(self, *_args) -> None:
        chapter = self._chapter_filter.currentData() or ""
        needle = self._search.text().strip().lower()
        visible = 0
        for row in range(self._list.count()):
            item = self._list.item(row)
            d = self._docs[item.data(Qt.ItemDataRole.UserRole)]
            ok = (not chapter or d.chapter == chapter) and (not needle or needle in d.search_key)
            item.setHidden(not ok)
            visible += int(ok)
        total = len(self._docs)
        self._count_lbl.setText(
            f"{visible} of {total} documents" if visible != total else f"{total} documents"
        )
        cur = self._list.currentItem()
        if cur is None or cur.isHidden():
            self._select_first_visible()

    def _select_first_visible(self) -> None:
        for row in range(self._list.count()):
            item = self._list.item(row)
            if not item.isHidden():
                self._list.setCurrentItem(item)
                return

    def _on_item_changed(self, current: QListWidgetItem | None, _previous=None) -> None:
        if current is None:
            return
        idx = current.data(Qt.ItemDataRole.UserRole)
        if idx is None or not (0 <= idx < len(self._docs)):
            return
        self._render(self._docs[idx])

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self, doc: _DocEntry) -> None:
        self._current = doc
        try:
            text = doc.path.read_text(encoding="utf-8")
        except Exception as exc:  # unreadable file — show the error inline
            text = f"# Could not read document\n\n`{doc.rel}`\n\n{exc}"
        self._browser.document().setBaseUrl(QUrl.fromLocalFile(str(doc.path.parent) + "/"))
        self._browser.setMarkdown(_prepare_markdown(text, doc.path.parent))
        _add_heading_anchors(self._browser.document())
        self._browser.verticalScrollBar().setValue(0)
        self._path_lbl.setText(f"docs/{doc.rel}")
        self._open_btn.setEnabled(True)

    def _open_externally(self) -> None:
        if self._current is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._current.path)))

    def _on_anchor_clicked(self, url: QUrl) -> None:
        # Pure fragment: jump within the current document.
        if not url.path() and url.hasFragment():
            self._browser.scrollToAnchor(url.fragment())
            return

        # Relative or file:// link to another Markdown doc inside docs/.
        if url.isRelative() or url.isLocalFile():
            raw = url.toLocalFile() if url.isLocalFile() else url.path()
            base = self._current.path.parent if self._current else _DOCS_ROOT
            candidate = (Path(raw) if Path(raw).is_absolute() else base / raw).resolve()
            try:
                rel = candidate.relative_to(_DOCS_ROOT.resolve()).as_posix()
            except ValueError:
                rel = None
            if rel is not None and candidate.suffix.lower() == ".md" and candidate.exists():
                if self.open_doc(rel) and url.hasFragment():
                    self._browser.scrollToAnchor(url.fragment())
                return
            if candidate.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(candidate)))
            return

        QDesktopServices.openUrl(url)


# ----------------------------------------------------------------------
# Helpers (module level so they can be unit-tested without a widget)
# ----------------------------------------------------------------------

def _scan_docs(root: Path) -> list[_DocEntry]:
    """List every Markdown file under ``root`` in ladder order."""
    if not root.is_dir():
        return []
    entries: list[_DocEntry] = []
    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        chapter = path.parent.relative_to(root).as_posix() if path.parent != root else ""
        chapter_label = _pretty_chapter(chapter)
        title = _read_title(path) or _pretty_name(path.stem)
        entries.append(_DocEntry(
            path=path,
            rel=rel,
            chapter=chapter,
            chapter_label=chapter_label,
            title=title,
            label=_list_label(chapter, path.stem, title),
            search_key=f"{title} {chapter_label} {rel}".lower(),
        ))
    # Top-level files (README) first, then chapters in numeric/lexical order.
    entries.sort(key=lambda e: (e.chapter != "", e.chapter, e.rel))
    return entries


def _read_title(path: Path, max_lines: int = 40) -> str:
    try:
        with path.open(encoding="utf-8") as fh:
            for _ in range(max_lines):
                line = fh.readline()
                if not line:
                    break
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    return ""


_NUM_PREFIX = re.compile(r"^(\d+)[_\-\s]*(.*)$")


def _split_prefix(name: str) -> tuple[str, str]:
    m = _NUM_PREFIX.match(name)
    if m:
        return m.group(1), m.group(2)
    return "", name


def _pretty_name(stem: str) -> str:
    _, rest = _split_prefix(stem)
    return rest.replace("_", " ").replace("-", " ").strip().title() or stem


def _pretty_chapter(chapter: str) -> str:
    if not chapter:
        return _OVERVIEW_CHAPTER
    num, rest = _split_prefix(chapter.split("/")[-1])
    name = rest.replace("_", " ").replace("-", " ").strip().title() or chapter
    return f"{int(num)}. {name}" if num else name


def _list_label(chapter: str, stem: str, title: str) -> str:
    cnum, _ = _split_prefix(chapter.split("/")[-1]) if chapter else ("", "")
    fnum, _ = _split_prefix(stem)
    if cnum and fnum:
        return f"{int(cnum)}.{int(fnum)}  {title}"
    if fnum:
        return f"{int(fnum)}  {title}"
    return title


# ── Markdown preparation (ported from qec-trainer/ui/screens/reference_screen.py) ──

# Fences may be indented up to 3 spaces (CommonMark), e.g. inside list items.
_FENCE         = re.compile(r"(^ {0,3}(?:```|~~~).*?^ {0,3}(?:```|~~~)[ \t]*$)", re.M | re.S)
_CODE_SPAN     = re.compile(r"(`+)(.+?)\1")
_DISPLAY_MATH  = re.compile(r"\$\$(.+?)\$\$", re.S)
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


def _prepare_markdown(text: str, doc_dir: Path | None = None) -> str:
    """Rewrite constructs Qt's Markdown importer cannot render.

    Fenced code blocks are left untouched.  Elsewhere (and outside inline
    code spans):

    * bare doc cross-references become relative links (when ``doc_dir`` given);
    * ``<details><summary>X</summary>`` -> bold "▸ X" lead-in; ``</details>``
      dropped (QTextDocument does not support the details element);
    * ``$$ … $$`` display math -> fenced code block, so the formula source stays
      legible and monospaced instead of collapsing into a paragraph; a formula
      inside a block quote gets the quote's ``> `` marker on every generated
      line, so the quote is not cut in two.
    """
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


def heading_slug(text: str) -> str:
    """GitHub-style anchor for a heading: 'Key Formulas' -> 'key-formulas'."""
    s = re.sub(r"[^\w\- ]+", "", text.strip().lower())
    return re.sub(r"\s+", "-", s)


def _add_heading_anchors(doc: QTextDocument) -> None:
    """Give every heading block a ``#slug`` anchor name so ``#fragment`` links
    (same-document or carried on a cross-reference) can scrollToAnchor()."""
    jobs: list[tuple[int, int, str]] = []
    block = doc.begin()
    while block.isValid():
        if block.blockFormat().headingLevel() and block.text().strip():
            start = block.position()
            end = start + max(block.length() - 1, 0)
            if end > start:
                jobs.append((start, end, heading_slug(block.text())))
        block = block.next()
    if not jobs:
        return
    cursor = QTextCursor(doc)
    cursor.beginEditBlock()
    for start, end, slug in jobs:
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cf = QTextCharFormat()
        cf.setAnchor(True)
        cf.setAnchorNames([slug])
        cursor.mergeCharFormat(cf)
    cursor.endEditBlock()
