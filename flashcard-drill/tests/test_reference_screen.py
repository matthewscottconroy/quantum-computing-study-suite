"""Reference screen: docs discovery, Markdown preparation, navigation."""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from PyQt6.QtCore import QUrl

from ui.screens import reference_screen as rs

DOCS = rs.docs_root()
pytestmark = pytest.mark.skipif(not DOCS.is_dir(), reason="docs corpus not present")


def test_docs_root_is_repo_docs_relative_to_source():
    here = Path(rs.__file__).resolve()
    assert DOCS == here.parents[3] / "docs"
    assert here.parents[2].name == "flashcard-drill"


def test_discover_docs_lists_every_markdown_file_readme_first():
    entries = rs.discover_docs()
    files = {p for p in DOCS.rglob("*.md")
             if not any(part.startswith((".", "_")) for part in p.relative_to(DOCS).parts)}
    assert {e.path for e in entries} == files
    assert len(entries) >= 50
    assert entries[0].path.name.lower() == "readme.md"
    assert entries[0].chapter == rs._START_HERE and entries[0].chapter_key == ""
    chapters = [e.chapter for e in entries if e.chapter_key]
    assert chapters == sorted(chapters, key=chapters.index)     # grouped, in order
    assert all(re.match(r"^Ch \d+ · ", c) for c in chapters)


def test_prepare_markdown_details_toggle():
    src = "Q?\n\n<details><summary>Solution</summary>\n\nBecause.\n\n</details>\n"
    shown = rs.prepare_markdown(src, show_solutions=True)
    assert "**▸ Solution**" in shown and "Because." in shown and "<details>" not in shown
    hidden = rs.prepare_markdown(src, show_solutions=False)
    assert "Because." not in hidden and "hidden" in hidden


def test_prepare_markdown_display_math_becomes_fence_and_keeps_quote():
    plain = rs.prepare_markdown("Text $$a = b$$ more")
    assert "```\na = b\n```" in plain
    quoted = rs.prepare_markdown("> Postulate:\n> $$x = y$$\n> where x.\n")
    lines = quoted.splitlines()
    assert all(l.startswith(">") for l in lines if l.strip()), quoted
    assert "> ```" in quoted and "> x = y" in quoted
    # Fenced code is never rewritten.
    fenced = "```\n$$ not math $$\n01_linear_algebra.md\n```\n"
    assert rs.prepare_markdown(fenced, doc_dir=DOCS / "01_mathematical_foundations") == fenced


def test_prepare_markdown_linkifies_bare_doc_refs():
    doc_dir = DOCS / "02_quantum_mechanics"
    src = ("Prerequisites: 01_mathematical_foundations/01_linear_algebra.md and "
           "`01_postulates_of_quantum_mechanics.md#key-formulas`; "
           "see also docs/04_quantum_algorithms/05_grover_search.md. "
           "Missing 99_nowhere/01_nothing.md stays plain; "
           "[already](01_postulates_of_quantum_mechanics.md) untouched.")
    out = rs.prepare_markdown(src, doc_dir=doc_dir)
    assert "[01_mathematical_foundations/01_linear_algebra.md](../01_mathematical_foundations/01_linear_algebra.md)" in out
    assert "[`01_postulates_of_quantum_mechanics.md#key-formulas`](01_postulates_of_quantum_mechanics.md#key-formulas)" in out
    assert "[docs/04_quantum_algorithms/05_grover_search.md](../04_quantum_algorithms/05_grover_search.md)" in out
    assert "99_nowhere/01_nothing.md stays plain" in out and "](99_nowhere" not in out
    assert out.count("[already](01_postulates_of_quantum_mechanics.md)") == 1
    # Without a doc_dir nothing is linkified.
    assert "](" not in rs.prepare_markdown("see 01_mathematical_foundations/01_linear_algebra.md")


def test_resolve_doc_ref_forms():
    doc_dir = DOCS / "02_quantum_mechanics"
    assert rs.resolve_doc_ref("01_mathematical_foundations/01_linear_algebra.md#x", doc_dir) == \
        "../01_mathematical_foundations/01_linear_algebra.md#x"
    assert rs.resolve_doc_ref("02_qubits_and_the_bloch_sphere.md", doc_dir) == "02_qubits_and_the_bloch_sphere.md"
    assert rs.resolve_doc_ref("no_such_file.md", doc_dir) is None


@pytest.fixture
def screen(qapp):
    s = rs.ReferenceScreen()
    s.resize(1000, 700)
    s.show()
    s.load_all()
    qapp.processEvents()
    yield s
    s.close()
    s.deleteLater()
    qapp.processEvents()


def test_screen_lands_on_readme_and_navigates(qapp, screen):
    assert screen.current_doc is not None
    assert screen.current_doc.path.name.lower() == "readme.md"
    assert screen.select_doc("02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md")
    assert screen.current_doc.rel == "02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md"

    # Bare cross-references in the rendered document are real anchors now.
    hrefs = re.findall(r'href="([^"]+)"', screen._browser.toHtml())
    doc_links = [h for h in hrefs if ".md" in h and not h.startswith("http")]
    assert doc_links, "expected linkified cross-references"

    # Clicking a relative link (with fragment) navigates and scrolls.
    opened = []
    screen.doc_opened.connect(opened.append)
    screen._on_anchor_clicked(QUrl("../01_mathematical_foundations/01_linear_algebra.md#key-formulas"))
    qapp.processEvents()
    assert screen.current_doc.rel == "01_mathematical_foundations/01_linear_algebra.md"
    assert opened == ["01_mathematical_foundations/01_linear_algebra.md"]
    assert screen._browser.verticalScrollBar().value() > 0

    # Same-document anchor.
    screen._browser.verticalScrollBar().setValue(0)
    screen._on_anchor_clicked(QUrl("#exercises")); qapp.processEvents()
    assert screen._browser.verticalScrollBar().value() > 0

    # Unknown target: stays put, no exception.
    screen._on_anchor_clicked(QUrl("nope/missing.md")); qapp.processEvents()
    assert screen.current_doc.rel == "01_mathematical_foundations/01_linear_algebra.md"


def test_screen_filters_and_solutions(qapp, screen):
    total = len(screen.visible_titles())
    assert total == len(screen.entries)
    screen.set_chapter(rs._START_HERE); qapp.processEvents()
    assert len(screen.visible_titles()) == 1
    screen.set_chapter(rs._ALL_CHAPTERS); qapp.processEvents()
    assert len(screen.visible_titles()) == total

    screen.set_search("Toffoli"); qapp.processEvents()
    hits = screen.visible_titles()
    assert 0 < len(hits) < total
    assert "Toffoli" in screen.current_doc.text()
    screen.set_search(""); qapp.processEvents()

    assert screen.select_doc("01_mathematical_foundations/01_linear_algebra.md")
    screen._solutions_cb.setChecked(True); qapp.processEvents()
    with_solutions = screen._browser.toPlainText()
    screen._solutions_cb.setChecked(False); qapp.processEvents()
    without = screen._browser.toPlainText()
    assert "hidden" in without and len(without) < len(with_solutions)
