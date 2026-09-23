"""Reference screen (REFERENCE CONTRACT): the shared browser, seen from exam-sim.

The browser itself is ``common.ui.reference`` and the root suite
(``tests/test_common_reference.py``) owns its unit tests.  What is tested here
is everything that could still break *for this app*:

* the docs root really resolves to ``<repo>/docs`` when the process starts in
  the exam-sim directory (the migration's one genuinely per-app risk);
* exam-sim's own layer — ``SECTION_DOCS``, the "Jump to topic" picker, the
  ★ Suggested filter, the "exam sections: …" annotation, ``show_doc``;
* a live render of every chapter, because a regression in the shared Markdown
  preparation would show up here as unreadable study material.
"""
from __future__ import annotations

import pathlib
import re

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPalette
from PyQt6.QtTest import QTest

import common_path  # noqa: F401  (puts the repo root on sys.path)

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = APP_ROOT.parent / "docs"
POSTULATES = "02_quantum_mechanics/01_postulates_of_quantum_mechanics.md"
MEASUREMENTS = "02_quantum_mechanics/03_quantum_measurements.md"
BOSONIC = "05_quantum_error_correction/08_bosonic_codes.md"


def _live_docs() -> list[pathlib.Path]:
    return sorted(
        p for p in DOCS.rglob("*.md")
        if p.is_file() and not any(s.startswith((".", "_")) for s in p.relative_to(DOCS).parts))


def _rows(screen) -> list[str]:
    """Docs-relative paths of the document rows currently listed."""
    from common.ui import reference as common_reference

    out = []
    for row in range(screen._list.count()):
        item = screen._list.item(row)
        idx = item.data(common_reference._INDEX_ROLE) if item else None
        if idx is not None:
            out.append(screen.entries[idx].rel)
    return out


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
    screen.deleteLater()
    qapp.processEvents()


# ── discovery ────────────────────────────────────────────────────────────────

def test_docs_root_resolves_to_the_repo_docs_folder(rs, ref):
    """Resolved at call time from the package, not a hard-coded parents[3]."""
    assert rs.docs_root() == DOCS and DOCS.is_dir()
    assert ref.docs_root() == DOCS


def test_scan_docs_lists_every_markdown_file_readme_first(rs):
    entries = rs.scan_docs()
    live = _live_docs()
    assert len(live) >= 50                                     # the corpus is present
    assert {e.path for e in entries} == set(live)
    assert len({e.rel for e in entries}) == len(entries)       # no duplicates
    first = entries[0]
    assert first.rel == "README.md" and first.chapter == ""
    assert first.chapter_label == "Overview"
    ch = next(e for e in entries if e.rel == POSTULATES)
    assert ch.chapter == "02_quantum_mechanics"
    assert ch.chapter_label == "2. Quantum Mechanics"
    assert ch.title == "Postulates of Quantum Mechanics"


def test_scan_docs_honours_an_explicit_root(rs, tmp_path):
    root = tmp_path / "docs"
    (root / "02_chapter_two").mkdir(parents=True)
    (root / "README.md").write_text("# Mini ladder\n")
    (root / "02_chapter_two" / "01_thing.md").write_text("# A Thing\n")
    (root / "02_chapter_two" / "_draft.md").write_text("# hidden\n")
    entries = rs.scan_docs(root)
    assert [(e.rel, e.chapter_label) for e in entries] == [
        ("README.md", "Overview"), ("02_chapter_two/01_thing.md", "2. Chapter Two")]
    assert entries[0].title == "Mini ladder"
    assert rs.scan_docs(tmp_path / "missing") == []


# ── exam-sim's own layer: SECTION_DOCS ───────────────────────────────────────

def test_every_suggested_doc_exists_and_every_section_is_covered(rs):
    for section, rels in rs.SECTION_DOCS.items():
        assert rels, section
        for rel in rels:
            assert (DOCS / rel).is_file(), f"{section}: {rel}"
    from config import SECTIONS
    assert set(rs.SECTION_DOCS) == set(SECTIONS)
    assert len(rs.suggested_rels()) == 12


def test_sections_for_maps_both_ways(rs):
    assert rs.sections_for(POSTULATES) == ["Estimator"]
    assert rs.sections_for(MEASUREMENTS) == ["Sampler", "Results analysis"]
    assert rs.sections_for("no/such/file.md") == []


def test_category_docs_gives_the_shared_picker_one_doc_per_section(rs):
    from config import SECTIONS
    picker = rs.category_docs()
    assert set(picker) == set(SECTIONS)
    assert all(rel in rs.suggested_rels() for rel in picker.values())
    assert picker["Estimator"] == POSTULATES


# ── markdown preparation (shared, exercised on this app's chapters) ──────────

def test_prepare_markdown_linkifies_and_rewrites(rs):
    here = DOCS / "02_quantum_mechanics"
    md = ("See docs/05_quantum_error_correction/08_bosonic_codes.md and "
          "06_wave_mechanics_and_schrodinger.md#summary.\n\n$$E = mc^2$$\n\n"
          "<details><summary>Solution</summary>\n\nBody\n\n</details>\n")
    out = rs.prepare_markdown(md, here, root=DOCS)
    assert ("[docs/05_quantum_error_correction/08_bosonic_codes.md]"
            "(../05_quantum_error_correction/08_bosonic_codes.md)") in out
    assert ("[06_wave_mechanics_and_schrodinger.md#summary]"
            "(06_wave_mechanics_and_schrodinger.md#summary)") in out
    assert "$$" not in out and "<details>" not in out
    assert "E = mc^2" in out and "Solution" in out
    assert rs.resolve_doc_ref("08_bosonic_codes.md", here, DOCS) == \
        "../05_quantum_error_correction/08_bosonic_codes.md"
    assert rs.heading_slug("Postulate 2: Dynamics") == "postulate-2-dynamics"


def test_postulates_chapter_quotes_survive_intact(rs):
    """The real chapter this app suggests for Estimator has three quoted formulas."""
    text = (DOCS / POSTULATES).read_text()
    out = rs.prepare_markdown(text, DOCS / "02_quantum_mechanics", root=DOCS)
    for marker in ("> **Postulate 2**", "> **Postulate 3**"):
        i = out.index(marker)
        j = out.index("\n\n", i)                  # the quote ends at the first blank line
        quote = out[i:j].splitlines()
        assert all(line.startswith(">") for line in quote), (marker, quote)
        assert any(line.startswith("> ```") for line in quote), marker
    assert "> where `U` is a unitary operator" in out


# ── widget ───────────────────────────────────────────────────────────────────

def test_load_all_lists_the_corpus_and_opens_the_readme(ref, rs):
    n = len(rs.scan_docs())
    assert ref._count_lbl.text() == f"{n} documents"
    assert _rows(ref) == [e.rel for e in ref.entries]
    labels = [ref._chapter_filter.itemText(i)
              for i in range(ref._chapter_filter.count())]
    assert labels[0] == rs.ALL_CHAPTERS
    assert "Overview" in labels and "2. Quantum Mechanics" in labels
    assert ref.current_entry is ref.entries[0]                 # README shown first
    assert ref._open_btn.isEnabled()
    assert "Quantum Computing" in ref._browser.toPlainText()


def test_jump_picker_offers_every_exam_section(ref, rs, qapp):
    from config import SECTIONS

    items = [ref._jump.itemText(i) for i in range(1, ref._jump.count())]
    assert items == list(SECTIONS)
    assert ref._jump.isVisible() or ref._jump.isVisibleTo(ref)
    assert ref.show_section("Sampler")
    qapp.processEvents()
    assert ref.current_entry.rel == MEASUREMENTS


def test_link_palette_is_readable_on_the_dark_surface(ref):
    from common.ui import theme

    pal = ref._browser.palette()
    assert pal.color(QPalette.ColorRole.Link).name() == theme.ACCENT
    assert pal.color(QPalette.ColorRole.LinkVisited).name() == theme.ACCENT2


def test_show_doc_selects_renders_and_annotates_the_exam_sections(ref, qapp):
    assert ref.show_doc(POSTULATES)
    qapp.processEvents()
    e = ref.current_entry
    assert e.rel == POSTULATES
    assert ref._doc_title.text() == "Postulates of Quantum Mechanics"
    assert f"docs/{POSTULATES}" in ref._doc_path.text()
    assert "exam sections: Estimator" in ref._doc_path.text()
    assert ref.show_doc("nope/does_not_exist.md") is False
    assert ref.current_entry is e
    # a chapter no section suggests carries no annotation
    assert ref.show_doc(BOSONIC)
    qapp.processEvents()
    assert "exam sections" not in ref._doc_path.text()


def test_suggested_filter_narrows_the_list_and_keeps_the_entries_usable(ref, rs, qapp):
    ref.set_suggested_only(True)
    qapp.processEvents()
    assert ref.suggested_only is True
    listed = _rows(ref)
    assert set(listed) == rs.suggested_rels()
    assert ref._count_lbl.text() == f"12 suggested of {len(ref.entries)} documents"
    # every row still points at the real entry: selecting one renders it
    ref._list.setCurrentRow(ref._list.row(ref._list.findItems(
        ref.entries[[e.rel for e in ref.entries].index(listed[-1])].label,
        Qt.MatchFlag.MatchExactly)[0]))
    qapp.processEvents()
    assert ref.current_entry.rel == listed[-1]
    # tooltips say which section suggests the chapter
    tips = [ref._list.item(r).toolTip() for r in range(ref._list.count())]
    assert any("Suggested for: Estimator" in t for t in tips)
    ref.set_suggested_only(False)
    qapp.processEvents()
    assert _rows(ref) == [e.rel for e in ref.entries]
    assert ref._count_lbl.text() == f"{len(ref.entries)} documents"


def test_suggested_filter_composes_with_search_and_steps_aside_for_open_doc(ref, rs, qapp):
    ref.set_suggested_only(True)
    ref.set_search("bloch")
    qapp.processEvents()
    listed = _rows(ref)
    assert listed and set(listed) <= rs.suggested_rels()
    ref.set_search("")
    qapp.processEvents()
    # opening a chapter the filter hides turns the filter off rather than
    # rendering a document that is not in the list
    assert ref.open_doc(BOSONIC)
    qapp.processEvents()
    assert ref.suggested_only is False
    assert ref.current_entry.rel == BOSONIC
    assert BOSONIC in _rows(ref)


def test_chapter_filter_and_search(ref, rs, qapp):
    ref.show_chapter("02_quantum_mechanics")
    qapp.processEvents()
    assert all(rel.startswith("02_quantum_mechanics/") for rel in _rows(ref))
    ref.show_chapter("")
    ref.set_search("postulates")
    qapp.processEvents()
    assert POSTULATES in _rows(ref)
    ref.set_search("zzzz-no-such-chapter")
    qapp.processEvents()
    assert _rows(ref) == []
    ref.set_search("")
    qapp.processEvents()
    assert ref.current_entry is not None and ref._open_btn.isEnabled()


def test_relative_link_with_fragment_switches_doc_and_scrolls(ref, qapp):
    assert ref.show_doc(POSTULATES)
    qapp.processEvents()
    sb = ref._browser.verticalScrollBar()
    ref._on_anchor_clicked(QUrl(f"../{BOSONIC}#summary"))
    qapp.processEvents()
    assert ref.current_entry.rel == BOSONIC
    assert sb.value() > 0, "'#summary' fragment did not scroll"


def test_same_document_fragment_scrolls(ref, qapp):
    assert ref.show_doc(POSTULATES)
    qapp.processEvents()
    sb = ref._browser.verticalScrollBar()
    sb.setValue(0)
    ref._on_anchor_clicked(QUrl("#exercises"))
    qapp.processEvents()
    assert sb.value() > 0


def test_external_outside_and_missing_links(ref, monkeypatch):
    opened: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl",
                        staticmethod(lambda u: (opened.append(u.toString()), True)[1]))
    assert ref.show_doc(POSTULATES)
    before = ref.current_entry
    ref._on_anchor_clicked(QUrl("https://example.com/x"))
    assert opened[-1].startswith("https://example.com")
    ref._on_anchor_clicked(QUrl("../../README.md"))               # outside docs/
    assert opened[-1].endswith("/README.md") and "/docs/" not in opened[-1]
    assert ref.current_entry is before
    n = len(opened)
    ref._on_anchor_clicked(QUrl("99_nonexistent/01_nope.md"))
    assert len(opened) == n and ref.current_entry is before
    ref._open_btn.click()
    assert opened[-1].endswith(POSTULATES)


def test_back_button_emits_back_requested(ref):
    fired: list[int] = []
    ref.back_requested.connect(lambda: fired.append(1))
    QTest.mouseClick(ref._back_btn, Qt.MouseButton.LeftButton)
    assert fired == [1]


def test_every_doc_renders_in_the_widget(ref):
    """Opening each chapter must not raise and must leave no raw math/details."""
    problems = []
    for e in ref.entries:
        assert ref.show_doc(e.rel)
        text = ref._browser.toPlainText()
        if re.search(r"(^|\n)\s*\$\$", text) or re.search(r"</?(details|summary)>", text):
            problems.append(e.rel)
    assert not problems, problems[:10]


def test_missing_docs_root_degrades_gracefully(qapp, rs, tmp_path):
    missing = tmp_path / "no-docs-here"
    screen = rs.ReferenceScreen(docs_root=missing)
    try:
        screen.load_all()
        assert screen.entries == [] and screen.current_entry is None
        assert screen._count_lbl.text() == "0 documents"
        assert "No documentation found" in screen._browser.toPlainText()
        assert str(missing) in screen._browser.toPlainText()
        assert not screen._open_btn.isEnabled()
        assert screen.show_doc("README.md") is False
        assert not screen._suggested_cb.isEnabled()     # nothing to suggest
    finally:
        screen.close()
        screen.deleteLater()
        qapp.processEvents()
