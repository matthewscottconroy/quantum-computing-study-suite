"""Reference screen for exam-sim — in-app browser for the shared docs corpus.

Ported from qec-trainer/ui/screens/reference_screen.py (the suite's canonical
docs browser). The docs root is resolved *relative to this file*
(``<repo>/docs``) so the app works from any checkout location, and every
``docs/**/*.md`` chapter is rendered in-app with QTextBrowser's Markdown
support. A curated "Suggested for C1000-179" view maps each exam section to
the chapters that back its objectives.

Rendering notes (see :func:`prepare_markdown`):

* the bare ``NN_chapter/NN_file.md`` cross-references the corpus writes in
  prose (also ``docs/…`` and same-chapter ``NN_file.md`` forms, optionally
  with a ``#heading`` suffix) are turned into relative links, so chapter-to-
  chapter navigation happens inside the browser; ``#fragment`` links jump to
  headings (every heading gets a GitHub-style anchor); external links open in
  the system browser;
* ``$$ … $$`` display math and ``<details><summary>`` solution blocks, which
  Qt's Markdown importer cannot render, are rewritten first — a formula
  inside a block quote stays inside the quote — and fenced code blocks are
  left untouched.
"""
from __future__ import annotations
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QListWidget, QListWidgetItem, QTextBrowser, QSplitter,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import (
    QDesktopServices, QPalette, QColor, QTextCursor, QTextCharFormat, QTextDocument,
)
from ui import theme

# exam-sim/ui/screens/reference_screen.py -> parents[3] is the repo root.
_DOCS_ROOT = Path(__file__).resolve().parents[3] / "docs"

_ALL_LABEL       = "All chapters"
_SUGGESTED_LABEL = "★ Suggested for C1000-179"

# Exam section -> docs (relative to the docs root) that back its objectives.
# Only files that exist on disk are shown; nothing here is load-bearing.
_SECTION_DOCS: dict[str, list[str]] = {
    "Create circuits": [
        "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
        "04_quantum_algorithms/01_quantum_parallelism_and_interference.md",
    ],
    "Quantum operations": [
        "03_quantum_gates_and_circuits/01_single_qubit_gates.md",
        "03_quantum_gates_and_circuits/02_multi_qubit_gates.md",
        "01_mathematical_foundations/03_tensor_products_and_multipartite_systems.md",
    ],
    "Run circuits": [
        "03_quantum_gates_and_circuits/04_quantum_circuit_complexity.md",
        "07_quantum_hardware/01_superconducting_qubits.md",
    ],
    "Sampler": [
        "02_quantum_mechanics/03_quantum_measurements.md",
    ],
    "Estimator": [
        "02_quantum_mechanics/01_postulates_of_quantum_mechanics.md",
        "06_variational_quantum_algorithms/01_vqe_fundamentals.md",
    ],
    "Visualization": [
        "02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md",
    ],
    "Results analysis": [
        "02_quantum_mechanics/03_quantum_measurements.md",
        "02_quantum_mechanics/10_distance_measures_and_lindblad.md",
    ],
    "OpenQASM": [
        "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
    ],
}


# ----------------------------------------------------------------------------
# Doc discovery (module level so it can be unit-tested without a widget)
# ----------------------------------------------------------------------------

@dataclass
class _DocEntry:
    path: Path
    title: str
    chapter: str                    # human chapter label ("3. Quantum Gates And Circuits")
    rel: str = ""                   # path relative to the docs root, posix style
    root: Path | None = None        # docs root this entry was scanned from
    sections: list[str] = field(default_factory=list)   # exam sections that suggest it


def _chapter_label(directory: Path, root: Path) -> str:
    """'03_quantum_gates_and_circuits' -> '3. Quantum Gates And Circuits'."""
    if directory == root:
        return "Overview"
    m = re.match(r"^(\d+)_(.*)$", directory.name)
    if not m:
        return directory.name.replace("_", " ").title()
    return f"{int(m.group(1))}. {m.group(2).replace('_', ' ').title()}"


def _doc_title(path: Path) -> str:
    """First '# ' heading, else a prettified filename."""
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
    return stem.replace("_", " ").title() or path.name


def scan_docs(root: Path | None = None) -> list[_DocEntry]:
    """Every docs/**/*.md under ``root`` (default: the repo docs), README first,
    then chapter/file order. Hidden / ``_private`` path parts are skipped."""
    root = root or _DOCS_ROOT
    _docs_by_name.cache_clear()
    if not root.is_dir():
        return []
    files = sorted(
        (p for p in root.rglob("*.md")
         if p.is_file() and not any(part.startswith((".", "_"))
                                    for part in p.relative_to(root).parts)),
        key=lambda p: (p != root / "README.md", p.as_posix()))
    entries = [_DocEntry(path=p, title=_doc_title(p), chapter=_chapter_label(p.parent, root),
                         rel=p.relative_to(root).as_posix(), root=root)
               for p in files]
    if entries and entries[0].path == root / "README.md":
        entries[0].title = f"Learning Ladder — {entries[0].title}"
    by_rel = {e.rel: e for e in entries}
    for section, rels in _SECTION_DOCS.items():
        for rel in rels:
            entry = by_rel.get(rel)
            if entry is not None and section not in entry.sections:
                entry.sections.append(section)
    return entries


# ----------------------------------------------------------------------------
# Markdown preparation
# ----------------------------------------------------------------------------

# Fences may be indented up to 3 spaces (CommonMark), e.g. inside list items.
_FENCE         = re.compile(r"(^ {0,3}(?:```|~~~).*?^ {0,3}(?:```|~~~)[ \t]*$)", re.M | re.S)
_CODE_SPAN     = re.compile(r"(`+)(.+?)\1")
_MATH_BLOCK    = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
_DETAILS_OPEN  = re.compile(r"<details>\s*<summary>(.*?)</summary>", re.IGNORECASE | re.DOTALL)
_DETAILS_CLOSE = re.compile(r"</details>", re.IGNORECASE)
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


@lru_cache(maxsize=8)
def _docs_by_name(root: Path) -> dict[str, list[Path]]:
    """``file.md`` -> every docs/**/file.md under ``root`` (one walk per root)."""
    index: dict[str, list[Path]] = {}
    if root.is_dir():
        for p in root.rglob("*.md"):
            if p.is_file() and not any(part.startswith((".", "_"))
                                       for part in p.relative_to(root).parts):
                index.setdefault(p.name, []).append(p)
    return index


def resolve_doc_ref(ref: str, doc_dir: Path, root: Path | None = None) -> str | None:
    """Turn a bare doc reference into a link target relative to ``doc_dir``.

    ``docs/…`` and ``chapter/file.md`` forms resolve against the docs root.  A
    bare ``file.md`` is taken as a sibling of the current document, falling
    back to the one file of that name anywhere in the corpus (chapters do cite
    each other's files by bare name).  A ``#fragment`` suffix is carried over
    to the target.  Returns None when nothing matches unambiguously (the text
    is then left alone).
    """
    root = root or _DOCS_ROOT
    ref, _, fragment = ref.partition("#")
    clean = ref[len("docs/"):] if ref.startswith("docs/") else ref
    if "/" in clean or ref.startswith("docs/"):
        target: Path | None = root / clean
    else:
        target = doc_dir / clean
        if not target.is_file():
            matches = _docs_by_name(root).get(clean, [])
            target = matches[0] if len(matches) == 1 else None
    if target is None or not target.is_file():
        return None
    rel = Path(os.path.relpath(target, doc_dir)).as_posix()
    return f"{rel}#{fragment}" if fragment else rel


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


def _linkify(segment: str, doc_dir: Path, root: Path | None = None) -> str:
    """Make bare doc cross-references clickable (outside inline code spans);
    a code span that *is* a doc reference becomes a link with code text.
    Text that is already the label of a Markdown link (``[…](``) is left alone."""
    def repl(m: re.Match) -> str:
        target = resolve_doc_ref(m.group(1), doc_dir, root)
        return f"[{m.group(1)}]({target})" if target else m.group(0)

    def code(ticks: str, code: str, after: str) -> str:
        m = None if after.startswith("](") else _DOC_REF.fullmatch(code.strip())
        target = resolve_doc_ref(m.group(1), doc_dir, root) if m else None
        return f"[{ticks}{code}{ticks}]({target})" if target else f"{ticks}{code}{ticks}"

    return _outside_code_spans(segment, lambda s, _start: _DOC_REF.sub(repl, s), code)


def prepare_markdown(text: str, doc_dir: Path | None = None,
                     root: Path | None = None) -> str:
    """Massage repo Markdown so QTextBrowser renders it legibly.

    Fenced code blocks are left untouched.  Elsewhere (skipping inline code
    spans where it matters):

    * bare doc cross-references become relative links (when ``doc_dir`` is
      given — ``root`` is the docs root they resolve against);
    * ``<details><summary>Solution</summary>`` … ``</details>`` becomes a bold
      "Solution" paragraph plus the body, so exercise solutions stay readable;
    * ``$$...$$`` display math becomes a fenced code block instead of a run of
      raw TeX; a formula inside a block quote gets the quote's ``> `` marker on
      every generated line, so the quote is not cut in two.
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
            return _MATH_BLOCK.sub(repl, prose)
        return _outside_code_spans(seg, rewrite)

    out: list[str] = []
    for i, seg in enumerate(_FENCE.split(text)):
        if i % 2:                                   # fenced code block
            out.append(seg)
            continue
        if doc_dir is not None:
            seg = _linkify(seg, doc_dir, root)
        seg = _DETAILS_OPEN.sub(lambda m: f"\n\n**{m.group(1).strip() or 'Details'}**\n\n", seg)
        seg = _DETAILS_CLOSE.sub("\n\n", seg)
        seg = display_math(seg)
        out.append(seg)
    return "".join(out)


def heading_slug(text: str) -> str:
    """GitHub-style anchor for a heading: 'Key Formulas' -> 'key-formulas'."""
    s = re.sub(r"[^\w\- ]+", "", text.strip().lower())
    return re.sub(r"\s+", "-", s)


def _anchor_headings(doc: QTextDocument) -> None:
    """Give every heading block a ``#slug`` anchor so ``#fragment`` links land.

    Qt's Markdown importer sets heading levels but no anchor names, so without
    this ``scrollToAnchor("summary")`` would be a silent no-op.
    """
    cursor = QTextCursor(doc)
    cursor.beginEditBlock()
    block = doc.begin()
    while block.isValid():
        if block.blockFormat().headingLevel() and block.length() > 1:
            fmt = QTextCharFormat()
            fmt.setAnchor(True)
            fmt.setAnchorNames([heading_slug(block.text())])
            cursor.setPosition(block.position())
            cursor.setPosition(block.position() + block.length() - 1,
                               QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(fmt)
        block = block.next()
    cursor.endEditBlock()


# ----------------------------------------------------------------------------
# Screen
# ----------------------------------------------------------------------------

class ReferenceScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._entries: list[_DocEntry] = []
        self._visible: list[_DocEntry] = []
        self._current: _DocEntry | None = None
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
        top_bar.setObjectName("topbar")   # scoped selector: children keep their own styling
        top_bar.setStyleSheet(
            f"QWidget#topbar {{ background-color: {theme.SURFACE};"
            f" border-bottom: 1px solid {theme.BORDER}; }}")
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
        self._chapter_filter.currentTextChanged.connect(self._apply_filter)
        top_layout.addWidget(self._chapter_filter)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search titles…")
        self._search.setClearButtonEnabled(True)
        self._search.setMinimumWidth(200)
        self._search.textChanged.connect(self._apply_filter)
        top_layout.addWidget(self._search)

        top_layout.addStretch()

        self._open_btn = QPushButton("Open externally")
        self._open_btn.setObjectName("flat")
        self._open_btn.setToolTip("Open the current chapter with the system's default .md handler")
        self._open_btn.clicked.connect(self._open_external)
        self._open_btn.setEnabled(False)
        top_layout.addWidget(self._open_btn)

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("flat")
        self._back_btn.clicked.connect(self.back_requested)
        top_layout.addWidget(self._back_btn)

        root.addWidget(top_bar)

        # ── Body: doc list | rendered chapter ──────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(24, 16, 12, 16)
        left_layout.setSpacing(8)
        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(
            f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
        left_layout.addWidget(self._count_lbl)
        self._list = QListWidget()
        self._list.setMinimumWidth(260)
        self._list.currentRowChanged.connect(self._on_row_changed)
        left_layout.addWidget(self._list, 1)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 16, 24, 16)
        right_layout.setSpacing(6)
        self._crumb_lbl = QLabel("")
        self._crumb_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        self._crumb_lbl.setWordWrap(True)
        right_layout.addWidget(self._crumb_lbl)
        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)           # we route links ourselves
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(self._on_anchor)
        self._browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {theme.SURFACE}; border: 1px solid {theme.BORDER};"
            f" border-radius: 8px; padding: 12px; font-size: 14px; }}")
        self._browser.document().setDocumentMargin(16)
        # Links default to QPalette.Link (#0000ff) — invisible on the dark surface.
        pal = self._browser.palette()
        pal.setColor(QPalette.ColorRole.Link, QColor(theme.ACCENT))
        pal.setColor(QPalette.ColorRole.LinkVisited, QColor(theme.ACCENT2))
        self._browser.setPalette(pal)
        right_layout.addWidget(self._browser, 1)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([320, 800])
        root.addWidget(splitter, 1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def docs_root(self) -> Path:
        return _DOCS_ROOT

    @property
    def entries(self) -> list[_DocEntry]:
        return list(self._entries)

    @property
    def current_entry(self) -> _DocEntry | None:
        return self._current

    def load_all(self) -> None:
        """Scan the docs corpus once and populate the chapter filter + list."""
        if self._loaded:
            self._browser.verticalScrollBar().setValue(0)
            return
        self._loaded = True
        self._entries = scan_docs()             # reads _DOCS_ROOT at call time

        self._chapter_filter.blockSignals(True)
        self._chapter_filter.clear()
        self._chapter_filter.addItem(_ALL_LABEL)
        if any(e.sections for e in self._entries):
            self._chapter_filter.addItem(_SUGGESTED_LABEL)
        seen: list[str] = []
        for e in self._entries:
            if e.chapter not in seen:
                seen.append(e.chapter)
        for chapter in seen:
            self._chapter_filter.addItem(chapter)
        self._chapter_filter.blockSignals(False)

        if not self._entries:
            self._count_lbl.setText("NO DOCS FOUND")
            self._browser.setMarkdown(
                f"# Docs not found\n\nExpected the shared docs corpus at:\n\n`{_DOCS_ROOT}`\n\n"
                "Run the app from inside the quantum-study repository checkout.")
            return
        self._apply_filter()

    def show_doc(self, rel_path: str) -> bool:
        """Select a doc by its path relative to the docs root. Returns success."""
        if not self._loaded:
            self.load_all()
        for e in self._entries:
            if e.rel == rel_path:
                if e not in self._visible:
                    # Reset the filter silently, then refilter once.
                    for w in (self._chapter_filter, self._search):
                        w.blockSignals(True)
                    self._chapter_filter.setCurrentText(_ALL_LABEL)
                    self._search.clear()
                    for w in (self._chapter_filter, self._search):
                        w.blockSignals(False)
                    self._apply_filter()
                self._select_entry(e)
                return True
        return False

    # ------------------------------------------------------------------
    # Filtering / list
    # ------------------------------------------------------------------

    def _apply_filter(self, *_args) -> None:
        chapter = self._chapter_filter.currentText()
        needle = self._search.text().strip().lower()
        visible: list[_DocEntry] = []
        for e in self._entries:
            if chapter == _SUGGESTED_LABEL:
                if not e.sections:
                    continue
            elif chapter not in (_ALL_LABEL, "") and e.chapter != chapter:
                continue
            if needle and needle not in e.title.lower() and needle not in e.rel.lower():
                continue
            visible.append(e)
        self._visible = visible

        self._list.blockSignals(True)
        self._list.clear()
        for e in visible:
            item = QListWidgetItem(e.title)
            tip = e.rel
            if e.sections:
                tip += "\nSuggested for: " + ", ".join(e.sections)
            item.setToolTip(tip)
            if chapter == _SUGGESTED_LABEL:
                item.setText(f"{e.title}\n    ↳ {', '.join(e.sections)}")
            elif chapter == _ALL_LABEL:
                item.setText(f"{e.title}\n    {e.chapter}")
            self._list.addItem(item)
        self._list.blockSignals(False)

        n = len(visible)
        self._count_lbl.setText(f"{n} CHAPTER{'S' if n != 1 else ''}")
        if not visible:
            self._current = None
            self._open_btn.setEnabled(False)
            self._crumb_lbl.setText("")
            self._browser.setMarkdown("_No chapters match this filter._")
            return
        # Keep the current doc if it survived the filter (moving the list
        # highlight without re-rendering, so the reader's scroll position is
        # kept while typing in the search box); otherwise show the first.
        if self._current in visible:
            self._set_row_silently(visible.index(self._current))
        else:
            self._set_row_silently(0)
            self._render(visible[0])

    def _set_row_silently(self, row: int) -> None:
        self._list.blockSignals(True)
        self._list.setCurrentRow(row)
        self._list.blockSignals(False)

    def _on_row_changed(self, row: int) -> None:
        if 0 <= row < len(self._visible):
            self._render(self._visible[row])

    def _select_entry(self, entry: _DocEntry) -> None:
        """Highlight ``entry`` in the list (if listed) and render it exactly once."""
        if entry in self._visible:
            self._set_row_silently(self._visible.index(entry))
        self._render(entry)

    # ------------------------------------------------------------------
    # Rendering / links
    # ------------------------------------------------------------------

    def _render(self, entry: _DocEntry) -> None:
        self._current = entry
        self._open_btn.setEnabled(True)
        crumb = f"{entry.chapter}  ›  {entry.rel}"
        if entry.sections:
            crumb += f"   ·   exam sections: {', '.join(entry.sections)}"
        self._crumb_lbl.setText(crumb)
        try:
            text = entry.path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self._browser.setMarkdown(f"# Could not read chapter\n\n`{entry.path}`\n\n{exc}")
            return
        self._browser.setMarkdown(prepare_markdown(text, entry.path.parent, entry.root))
        _anchor_headings(self._browser.document())
        self._browser.verticalScrollBar().setValue(0)

    def _on_anchor(self, url: QUrl) -> None:
        scheme = url.scheme()
        if scheme in ("http", "https", "mailto"):
            QDesktopServices.openUrl(url)
            return
        if scheme == "file":
            target = url.toLocalFile()
        else:
            target = url.toString(QUrl.UrlFormattingOption.RemoveFragment)
        if not target:
            if url.fragment():
                self._browser.scrollToAnchor(url.fragment())
            return
        base = self._current.path.parent if self._current else _DOCS_ROOT
        candidate = (base / target).resolve()
        if candidate.suffix.lower() == ".md" and candidate.is_file():
            for e in self._entries:
                if e.path == candidate:
                    self._select_entry(e)
                    if url.fragment():
                        self._browser.scrollToAnchor(url.fragment())
                    return
        if candidate.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(candidate)))

    def _open_external(self) -> None:
        if self._current is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._current.path)))
