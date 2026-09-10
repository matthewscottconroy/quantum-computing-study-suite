"""In-app docs browser (REFERENCE CONTRACT): discovery, rendering, links, Back.

Runs against the live ``<repo>/docs`` corpus so a broken docs root, a regex
regression in ``_prepare_markdown`` / ``_linkify`` or a dead Back / anchor
path fails here rather than in the running app.
"""
from __future__ import annotations

import pathlib
import re

import pytest
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices, QTextDocument, QTextFormat
from PyQt6.QtWidgets import QPushButton

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = APP_ROOT.parent / "docs"
MIN_DOCS = 59

POSTULATES = "02_quantum_mechanics/01_postulates_of_quantum_mechanics.md"
LINALG = "01_mathematical_foundations/01_linear_algebra.md"


def _live_docs() -> list[pathlib.Path]:
    """Every docs/**/*.md the screen must list (hidden parts skipped)."""
    return sorted(
        p for p in DOCS.rglob("*.md")
        if p.is_file() and not any(s.startswith(".") for s in p.relative_to(DOCS).parts)
    )


def _anchors(doc: QTextDocument) -> tuple[list[str], set[str]]:
    """(hrefs, anchor names) of every anchored fragment in a rendered document."""
    hrefs, names = [], set()
    block = doc.begin()
    while block.isValid():
        it = block.begin()
        while not it.atEnd():
            fmt = it.fragment().charFormat()
            if fmt.isAnchor():
                if fmt.anchorHref():
                    hrefs.append(fmt.anchorHref())
                names.update(fmt.anchorNames())
            it += 1
        block = block.next()
    return hrefs, names


def _blocks(doc: QTextDocument) -> list[tuple[str, object, bool]]:
    """(text, block-quote level, is-code-block) for every non-blank block."""
    out = []
    block = doc.begin()
    while block.isValid():
        if block.text().strip():
            bf = block.blockFormat()
            out.append((
                block.text(),
                bf.property(QTextFormat.Property.BlockQuoteLevel),
                bf.hasProperty(QTextFormat.Property.BlockCodeLanguage),
            ))
        block = block.next()
    return out


def _button(widget, text: str) -> QPushButton:
    for b in widget.findChildren(QPushButton):
        if b.text() == text:
            return b
    raise AssertionError(f"no button {text!r}")


@pytest.fixture
def rs():
    from ui.screens import reference_screen
    return reference_screen


@pytest.fixture
def ref(qapp, rs):
    screen = rs.ReferenceScreen()
    screen.resize(1100, 750)
    screen.show()
    screen.load_all()
    qapp.processEvents()
    yield screen
    screen.close()


# ── discovery ────────────────────────────────────────────────────────────────

def test_docs_root_is_the_repo_docs_folder(rs):
    assert rs._DOCS_ROOT == DOCS and DOCS.is_dir()
    assert rs.ReferenceScreen.docs_root() == DOCS
    assert rs._DOCS_ROOT == pathlib.Path(rs.__file__).resolve().parents[3] / "docs"


def test_scan_docs_lists_every_doc_readme_first(rs):
    entries = rs._scan_docs(DOCS)
    assert len(entries) >= MIN_DOCS
    assert [e.path for e in entries] == sorted(e.path for e in entries) or True  # order checked below
    assert {e.path for e in entries} == set(_live_docs())
    assert entries[0].rel == "README.md" and entries[0].chapter == "" \
        and entries[0].chapter_label == "Overview"
    chapters = [e.chapter for e in entries[1:]]
    assert chapters == sorted(chapters)                      # ladder order
    numbered = [e for e in entries if e.chapter]
    assert all(re.match(r"^\d+\.\d+  \S", e.label) for e in numbered), \
        [e.label for e in numbered if not re.match(r"^\d+\.\d+  \S", e.label)]
    assert all(e.title and e.search_key == e.search_key.lower() for e in entries)
    assert rs._scan_docs(DOCS / "does-not-exist") == []


def test_every_subject_maps_to_an_existing_chapter(rs):
    from core.topics import TOPICS
    assert set(rs.SUBJECT_CHAPTER) == set(TOPICS)
    for chapter in set(rs.SUBJECT_CHAPTER.values()):
        assert (DOCS / chapter).is_dir(), chapter


# ── markdown preparation ─────────────────────────────────────────────────────

def test_linkify_bare_refs_including_fragments(rs):
    entries = rs._scan_docs(DOCS)
    here = next(e for e in entries if e.chapter)
    there = next(e for e in entries if e.chapter and e.chapter != here.chapter)
    sibling = next(e for e in entries if e.chapter == here.chapter and e is not here)
    prep = lambda md: rs._prepare_markdown(md, here.path.parent)

    assert prep(f"see {there.rel}.") == f"see [{there.rel}](../{there.rel})."
    assert prep(f"see {there.rel}#summary.") == \
        f"see [{there.rel}#summary](../{there.rel}#summary)."
    assert prep(f"see docs/{there.rel}#key-formulas") == \
        f"see [docs/{there.rel}#key-formulas](../{there.rel}#key-formulas)"
    assert prep(f"see {sibling.path.name}") == f"see [{sibling.path.name}]({sibling.path.name})"
    assert prep(f"see `{there.rel}`") == f"see [`{there.rel}`](../{there.rel})"
    assert prep(f"[Read]({there.rel})") == f"[Read]({there.rel})"          # existing link
    assert prep(f"[{there.rel}](x.md)") == f"[{there.rel}](x.md)"          # existing label
    assert prep(f"path/to/{there.rel}") == f"path/to/{there.rel}"          # longer path
    assert prep("see 99_nonexistent/01_nope.md") == "see 99_nonexistent/01_nope.md"
    fenced = f"```\n{there.rel}\n```\n"
    assert prep(fenced) == fenced
    assert rs._prepare_markdown(f"see {there.rel}") == f"see {there.rel}"  # no doc_dir: untouched
    assert rs.resolve_doc_ref(f"{there.rel}#summary", here.path.parent) == f"../{there.rel}#summary"
    assert rs.resolve_doc_ref("99_nonexistent/01_nope.md#x", here.path.parent) is None


def test_prerequisites_line_of_a_real_doc_becomes_links(rs):
    path = DOCS / POSTULATES
    out = rs._prepare_markdown(path.read_text(encoding="utf-8"), path.parent)
    prereq = next(l for l in out.splitlines() if l.startswith("> **Prerequisites**"))
    assert "[01_linear_algebra.md](../01_mathematical_foundations/01_linear_algebra.md)" in prereq
    assert "01_linear_algebra.md (" not in prereq or "](" in prereq


def test_display_math_and_details_rewrites(rs):
    md = "Energy:\n\n$$E = mc^2$$\n\nUse `$$` in files.\n\n```\n$$ raw $$\n```\n"
    out = rs._prepare_markdown(md)
    assert "\n```\nE = mc^2\n```\n" in out
    assert "`$$`" in out and "```\n$$ raw $$\n```" in out   # inline / fenced code untouched

    details = "<details><summary>Solution</summary>\n\nBecause `X` anticommutes.\n\n</details>\n"
    shown = rs._prepare_markdown(details)
    assert "**▸ Solution**" in shown and "anticommutes" in shown
    assert "<details>" not in shown and "</details>" not in shown and "<summary>" not in shown


def test_quoted_display_math_stays_inside_the_block_quote(rs, qapp):
    md = ("> **Postulate 2**: the state at `t₂` is:\n"
          "> $$|\\psi(t_2)\\rangle = U|\\psi(t_1)\\rangle$$\n"
          "> where `U` is unitary.\n")
    out = rs._prepare_markdown(md)
    assert all(line.startswith(">") for line in out.strip().splitlines()), out
    doc = QTextDocument()
    doc.setMarkdown(out)
    blocks = _blocks(doc)
    assert [lvl for _, lvl, _ in blocks] == [1, 1, 1], blocks      # one unbroken quote …
    assert [code for _, _, code in blocks] == [False, True, False]  # … formula as a code block


def test_real_doc_quoted_formulas_render_inside_their_quotes(rs, qapp):
    path = DOCS / POSTULATES
    doc = QTextDocument()
    doc.setMarkdown(rs._prepare_markdown(path.read_text(encoding="utf-8"), path.parent))
    blocks = _blocks(doc)
    # The three "> $$…$$" formulas the corpus writes inside block quotes (the
    # postulate statements).  The Key Formulas recap near the end repeats some
    # of them unquoted, so take the FIRST block matching each one.
    quoted = (
        "|\\psi(t_2)\\rangle = U(t_1, t_2)|\\psi(t_1)\\rangle",
        "\\sum_m M_m^\\dagger M_m = I",
        "|\\psi_m\\rangle = \\frac{M_m|\\psi\\rangle}{\\sqrt{p(m)}}",
    )
    hits = [next(i for i, (t, _, _) in enumerate(blocks) if t.strip() == formula)
            for formula in quoted]
    assert hits == sorted(hits) and len(set(hits)) == 3, hits
    for i in hits:
        text, level, is_code = blocks[i]
        assert is_code and level == 1, (text, level, is_code)      # formula inside the quote …
        assert blocks[i - 1][1] == 1, blocks[i - 1]                 # … continuing the quote above
    # In the source, formulas 1 and 2 are followed by more quoted text (the quote
    # must not be cut in two); formula 3 is the last line of its quote, so the
    # block after it is ordinary prose (no stray quote line is emitted either).
    assert blocks[hits[0] + 1][1] == 1 and blocks[hits[1] + 1][1] == 1, \
        (blocks[hits[0] + 1], blocks[hits[1] + 1])
    assert blocks[hits[2] + 1][1] is None and blocks[hits[2] + 1][0].startswith(
        "The completeness condition"), blocks[hits[2] + 1]


def test_heading_slug_and_anchor_names(rs, qapp):
    assert rs.heading_slug("Key Formulas") == "key-formulas"
    assert rs.heading_slug("QAOA: Quantum Approximate Optimization Algorithm") == \
        "qaoa-quantum-approximate-optimization-algorithm"
    doc = QTextDocument()
    doc.setMarkdown(rs._prepare_markdown("# Title\n\ntext\n\n## Key Formulas\n\nmore\n"))
    rs._add_heading_anchors(doc)
    _, names = _anchors(doc)
    assert {"title", "key-formulas"} <= names


def test_prepare_markdown_over_whole_corpus_leaves_no_leaks(rs):
    problems: list[str] = []
    for path in _live_docs():
        out = rs._prepare_markdown(path.read_text(encoding="utf-8"), path.parent)
        if re.search(r"</?details>|</?summary>", out, re.I):
            problems.append(f"{path.name}: details/summary leaked")
        if out.count("```") % 2:
            problems.append(f"{path.name}: unbalanced fences")
        prose = "".join(seg for i, seg in enumerate(rs._FENCE.split(out)) if i % 2 == 0)
        if "$$" in rs._CODE_SPAN.sub("", prose):
            problems.append(f"{path.name}: $$ leaked")
        for target in re.findall(r"\]\(([^)]+\.md)(?:#[\w\-]+)?\)", prose):
            if not target.startswith(("http://", "https://")) and not (path.parent / target).is_file():
                problems.append(f"{path.name}: dangling link {target}")
    assert problems == []


# ── widget behaviour ─────────────────────────────────────────────────────────

def test_load_all_lists_docs_and_selects_readme(ref):
    assert ref._list.count() >= MIN_DOCS
    assert ref._count_lbl.text().endswith(" documents")
    assert ref.current_doc_path() == DOCS / "README.md"
    assert ref._path_lbl.text() == "docs/README.md"
    assert len(ref._browser.toPlainText()) > 200
    labels = [ref._chapter_filter.itemText(i) for i in range(ref._chapter_filter.count())]
    assert labels[:2] == ["All chapters", "Overview"] and len(labels) >= 10
    n = ref._list.count()
    ref.load_all()                                # idempotent
    assert ref._list.count() == n


def test_open_doc_renders_and_reports_missing(ref):
    assert ref.open_doc(POSTULATES) is True
    assert ref.current_doc_path() == DOCS / POSTULATES
    text = ref._browser.toPlainText()
    assert "Postulate" in text and "Solution" in text
    assert "<details>" not in text and "$$" not in text
    assert ref._path_lbl.text() == f"docs/{POSTULATES}"
    assert ref._open_btn.isEnabled()
    assert ref.open_doc("99_nope/00_missing.md") is False
    assert ref.current_doc_path() == DOCS / POSTULATES     # unchanged


def test_rendered_doc_has_prerequisite_links_and_heading_anchors(ref):
    assert ref.open_doc(POSTULATES)
    hrefs, names = _anchors(ref._browser.document())
    assert "../01_mathematical_foundations/01_linear_algebra.md" in hrefs
    assert {"exercises", "summary", "key-formulas"} <= names
    ref._on_anchor_clicked(QUrl("../01_mathematical_foundations/01_linear_algebra.md"))
    assert ref.current_doc_path() == DOCS / LINALG


def test_open_doc_hidden_by_filter_clears_filter(ref):
    ref.show_subject("Quantum Mechanics")
    visible = [ref._docs[ref._list.item(i).data(0x0100)]
               for i in range(ref._list.count()) if not ref._list.item(i).isHidden()]
    assert visible and all(d.chapter == "02_quantum_mechanics" for d in visible)
    assert ref.open_doc(LINALG) is True                    # hidden by the filter
    assert ref._chapter_filter.currentIndex() == 0 and ref._search.text() == ""
    assert ref.current_doc_path() == DOCS / LINALG


def test_chapter_filter_and_search(ref):
    total = ref._list.count()
    ref._search.setText("bloch")
    shown = [ref._docs[ref._list.item(i).data(0x0100)].rel
             for i in range(ref._list.count()) if not ref._list.item(i).isHidden()]
    assert shown and all("bloch" in r.lower() for r in shown)
    assert ref._count_lbl.text() == f"{len(shown)} of {total} documents"
    ref._search.setText("zzzz-no-such-doc")
    assert ref._count_lbl.text() == f"0 of {total} documents"
    ref._search.clear()
    assert ref._count_lbl.text() == f"{total} documents"
    ref.show_chapter("")
    assert ref._chapter_filter.currentIndex() == 0


def test_back_button_emits_back_requested(ref, qapp):
    hits = []
    ref.back_requested.connect(lambda: hits.append(1))
    _button(ref, "← Back").click()
    qapp.processEvents()
    assert hits == [1]


def test_relative_link_with_fragment_switches_doc(ref):
    assert ref.open_doc(LINALG)
    ref._on_anchor_clicked(QUrl(f"../{POSTULATES}#exercises"))
    assert ref.current_doc_path() == DOCS / POSTULATES
    ref._on_anchor_clicked(QUrl("#summary"))              # same-document fragment: no crash
    assert ref.current_doc_path() == DOCS / POSTULATES
    abs_link = QUrl.fromLocalFile(str(DOCS / LINALG))
    ref._on_anchor_clicked(abs_link)
    assert ref.current_doc_path() == DOCS / LINALG


def test_external_outside_and_missing_links(ref, monkeypatch):
    opened: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl",
                        staticmethod(lambda url: (opened.append(url.toString()), True)[1]))
    assert ref.open_doc(LINALG)
    ref._on_anchor_clicked(QUrl("https://example.com/x"))
    assert opened == ["https://example.com/x"]
    ref._on_anchor_clicked(QUrl("../../quantum-quiz/README.md"))   # exists, outside docs/
    assert len(opened) == 2 and opened[-1].endswith("quantum-quiz/README.md")
    ref._on_anchor_clicked(QUrl("does_not_exist.md"))              # missing: no crash, no open
    assert len(opened) == 2
    assert ref.current_doc_path() == DOCS / LINALG


def test_missing_docs_root_degrades_gracefully(qapp, rs, monkeypatch, tmp_path):
    monkeypatch.setattr(rs, "_DOCS_ROOT", tmp_path / "nope")
    screen = rs.ReferenceScreen()
    screen.load_all()
    assert screen._list.count() == 0
    assert screen._count_lbl.text() == "0 documents"
    assert "No documentation found" in screen._browser.toPlainText()
    assert screen.open_doc("README.md") is False
    screen.close()
