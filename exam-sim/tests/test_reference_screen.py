"""Reference screen (REFERENCE CONTRACT): discovery, Markdown prep, links, navigation.

Runs against the live ``<repo>/docs`` corpus so a broken docs root, a regex
regression in ``prepare_markdown`` / ``_linkify`` or a dead Back / anchor path
fails here rather than in the running app.
"""
from __future__ import annotations

import pathlib
import re

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPalette, QTextDocument, QTextFormat
from PyQt6.QtTest import QTest

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = APP_ROOT.parent / "docs"
POSTULATES = "02_quantum_mechanics/01_postulates_of_quantum_mechanics.md"
OSCILLATOR = "02_quantum_mechanics/07_harmonic_oscillator.md"
BOSONIC = "05_quantum_error_correction/08_bosonic_codes.md"


def _live_docs() -> list[pathlib.Path]:
    return sorted(
        p for p in DOCS.rglob("*.md")
        if p.is_file() and not any(s.startswith((".", "_")) for s in p.relative_to(DOCS).parts))


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

def test_docs_root_resolves_to_the_repo_docs_folder(rs):
    assert rs._DOCS_ROOT == DOCS and DOCS.is_dir()
    assert rs.ReferenceScreen.docs_root.fget(None) == DOCS      # property reads the module global


def test_scan_docs_lists_every_markdown_file_readme_first(rs):
    entries = rs.scan_docs()
    live = _live_docs()
    assert len(live) >= 50                                     # the corpus is present
    assert [e.path for e in entries] == sorted(live, key=lambda p: (p != DOCS / "README.md", p.as_posix()))
    assert len({e.rel for e in entries}) == len(entries)       # no duplicates
    first = entries[0]
    assert first.rel == "README.md" and first.chapter == "Overview"
    assert first.title.startswith("Learning Ladder — ")
    assert first.root == DOCS
    ch = next(e for e in entries if e.rel == POSTULATES)
    assert ch.chapter == "2. Quantum Mechanics"
    assert ch.title == "Postulates of Quantum Mechanics"
    assert set(ch.sections) == {"Estimator"}


def test_every_suggested_doc_exists_and_every_section_is_covered(rs):
    for section, rels in rs._SECTION_DOCS.items():
        assert rels, section
        for rel in rels:
            assert (DOCS / rel).is_file(), f"{section}: {rel}"
    from config import SECTIONS
    assert set(rs._SECTION_DOCS) == set(SECTIONS)
    suggested = [e for e in rs.scan_docs() if e.sections]
    expected = {rel for rels in rs._SECTION_DOCS.values() for rel in rels}
    assert {e.rel for e in suggested} == expected
    assert len(suggested) == 12


def test_scan_docs_honours_an_explicit_root(rs, tmp_path):
    root = tmp_path / "docs"
    (root / "02_chapter_two").mkdir(parents=True)
    (root / "README.md").write_text("# Mini ladder\n")
    (root / "02_chapter_two" / "01_thing.md").write_text("# A Thing\n")
    (root / "02_chapter_two" / "_draft.md").write_text("# hidden\n")
    entries = rs.scan_docs(root)
    assert [(e.rel, e.chapter) for e in entries] == [
        ("README.md", "Overview"), ("02_chapter_two/01_thing.md", "2. Chapter Two")]
    assert all(e.root == root for e in entries)
    assert entries[0].title == "Learning Ladder — Mini ladder"
    assert rs.scan_docs(tmp_path / "missing") == []


# ── markdown preparation (pure functions) ────────────────────────────────────

def test_linkify_bare_refs_in_prose_and_code_spans(rs):
    here = DOCS / "02_quantum_mechanics"
    md = ("See docs/05_quantum_error_correction/08_bosonic_codes.md and "
          "06_wave_mechanics_and_schrodinger.md#summary; also `09_perturbation_theory.md`, "
          "03_quantum_gates_and_circuits/01_single_qubit_gates.md. "
          "Not 99_nope/01_missing.md nor [x](01_postulates_of_quantum_mechanics.md).")
    out = rs.prepare_markdown(md, here, DOCS)
    assert ("[docs/05_quantum_error_correction/08_bosonic_codes.md]"
            "(../05_quantum_error_correction/08_bosonic_codes.md)") in out
    assert ("[06_wave_mechanics_and_schrodinger.md#summary]"
            "(06_wave_mechanics_and_schrodinger.md#summary)") in out
    assert "[`09_perturbation_theory.md`](09_perturbation_theory.md)" in out
    assert ("[03_quantum_gates_and_circuits/01_single_qubit_gates.md]"
            "(../03_quantum_gates_and_circuits/01_single_qubit_gates.md)") in out
    assert "Not 99_nope/01_missing.md nor" in out                     # unresolvable: untouched
    assert out.count("[x](01_postulates_of_quantum_mechanics.md)") == 1   # existing link untouched
    # a bare file name unique elsewhere in the corpus resolves across chapters
    assert rs.resolve_doc_ref("08_bosonic_codes.md", here, DOCS) == \
        "../05_quantum_error_correction/08_bosonic_codes.md"
    # without doc_dir nothing is linkified
    assert rs.prepare_markdown("see 09_perturbation_theory.md") == "see 09_perturbation_theory.md"


def test_fenced_code_is_left_untouched(rs):
    md = "before $$a$$\n\n```python\nx = '$$b$$'\nprint('<details>')  # 01_linear_algebra.md\n```\n\nafter $$c$$\n"
    out = rs.prepare_markdown(md, DOCS / "01_mathematical_foundations", DOCS)
    fence = out[out.index("```python"):out.index("```\n\nafter")]
    assert "x = '$$b$$'" in fence and "<details>" in fence and "[" not in fence
    assert "$$a$$" not in out and "$$c$$" not in out
    assert out.count("```") == 6                                   # 1 original + 2 math fences


def test_display_math_and_details_rewrites(rs):
    md = ("Intro\n\n$$E = mc^2$$\n\nText\n\n<details><summary>Solution</summary>\n\n"
          "Body\n\n</details>\n")
    out = rs.prepare_markdown(md)
    assert "$$" not in out and "<details>" not in out and "</details>" not in out
    assert "\n```\nE = mc^2\n```\n" in out
    assert "\n\n**Solution**\n\n" in out
    doc = QTextDocument()
    doc.setMarkdown(out)
    assert "Solution" in doc.toPlainText() and "Body" in doc.toPlainText()


def test_quoted_display_math_stays_inside_the_block_quote(rs, qapp):
    md = ("> **Postulate 2**: the state at `t₂` is:\n"
          "> $$|\\psi(t_2)\\rangle = U|\\psi(t_1)\\rangle$$\n"
          "> where `U` is unitary.\n")
    out = rs.prepare_markdown(md)
    assert all(line.startswith(">") for line in out.strip().splitlines()), out
    doc = QTextDocument()
    doc.setMarkdown(out)
    levels, code_blocks = [], []
    block = doc.begin()
    while block.isValid():
        if block.text().strip():
            levels.append(block.blockFormat().property(QTextFormat.Property.BlockQuoteLevel))
            code_blocks.append(block.blockFormat().hasProperty(QTextFormat.Property.BlockCodeLanguage))
        block = block.next()
    assert levels == [1, 1, 1], levels            # one unbroken quote …
    assert code_blocks == [False, True, False]    # … with the formula as a code block


def test_postulates_chapter_quotes_survive_intact(rs):
    """The real chapter this app suggests for Estimator has three quoted formulas."""
    text = (DOCS / POSTULATES).read_text()
    out = rs.prepare_markdown(text, DOCS / "02_quantum_mechanics", DOCS)
    for marker in ("> **Postulate 2**", "> **Postulate 3**"):
        i = out.index(marker)
        j = out.index("\n\n", i)                  # the quote ends at the first blank line
        quote = out[i:j].splitlines()
        assert all(line.startswith(">") for line in quote), (marker, quote)
        assert any(line.startswith("> ```") for line in quote), marker
    assert "> where `U` is a unitary operator" in out


def test_heading_slug(rs):
    assert rs.heading_slug("Key Formulas") == "key-formulas"
    assert rs.heading_slug("Postulate 2: Dynamics") == "postulate-2-dynamics"


def test_every_real_doc_prepares_clean_with_live_links(rs):
    problems: list[str] = []
    n_links = 0
    for e in rs.scan_docs():
        out = rs.prepare_markdown(e.path.read_text(encoding="utf-8"), e.path.parent, e.root)
        if out.count("```") % 2:
            problems.append(f"{e.rel}: odd fence count")
        # Prose only: a `$$ … $$` *mentioned* inside inline code or a fence
        # (docs/README.md documents the syntax) must stay literal.
        prose = rs._CODE_SPAN.sub("", "".join(rs._FENCE.split(out)[::2]))
        if "$$" in prose:
            problems.append(f"{e.rel}: residual $$")
        if re.search(r"</?(details|summary)>", prose, re.I):
            problems.append(f"{e.rel}: residual <details>")
        for _label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", out):
            if target.startswith(("http", "#", "mailto")):
                continue
            n_links += 1
            if not (e.path.parent / target.split("#")[0]).resolve().is_file():
                problems.append(f"{e.rel}: dead link {target}")
    assert not problems, problems[:10]
    assert n_links >= 100                          # the corpus cross-references itself heavily


# ── widget ───────────────────────────────────────────────────────────────────

def test_load_all_populates_filter_and_list_and_scans_once(ref, rs, monkeypatch):
    n = len(rs.scan_docs())
    assert ref._count_lbl.text() == f"{n} CHAPTERS"
    assert ref._list.count() == n
    items = [ref._chapter_filter.itemText(i) for i in range(ref._chapter_filter.count())]
    assert items[:2] == [rs._ALL_LABEL, rs._SUGGESTED_LABEL]
    assert items[2] == "Overview" and "2. Quantum Mechanics" in items
    assert ref.current_entry is ref.entries[0]                    # README shown first
    assert ref._open_btn.isEnabled()
    assert "Quantum Computing: A Complete Learning Ladder" in ref._browser.toPlainText()
    calls = []
    monkeypatch.setattr(rs, "scan_docs", lambda *a, **k: calls.append(1) or [])
    ref.load_all()                                                # second visit: no rescan
    assert calls == [] and ref._list.count() == n


def test_link_palette_is_readable_on_the_dark_surface(ref, rs):
    pal = ref._browser.palette()
    assert pal.color(QPalette.ColorRole.Link).name() == rs.theme.ACCENT
    assert pal.color(QPalette.ColorRole.LinkVisited).name() == rs.theme.ACCENT2


def test_show_doc_selects_and_renders_with_heading_anchors(ref, qapp, rs):
    assert ref.show_doc(POSTULATES)
    qapp.processEvents()
    e = ref.current_entry
    assert e.rel == POSTULATES
    assert ref._list.currentRow() == ref._visible.index(e)
    assert ref._crumb_lbl.text().startswith(f"2. Quantum Mechanics  ›  {POSTULATES}")
    assert "exam sections: Estimator" in ref._crumb_lbl.text()
    hrefs, names = _anchors(ref._browser.document())
    assert {"key-formulas", "worked-example", "summary", "exercises", "further-reading"} <= names
    assert any(h.endswith(".md") or ".md#" in h for h in hrefs)  # bare cross-refs became links
    assert ref.show_doc("nope/does_not_exist.md") is False
    assert ref.current_entry is e


def test_chapter_filter_search_and_no_match_state(ref, qapp, rs):
    ref._chapter_filter.setCurrentText("2. Quantum Mechanics")
    qapp.processEvents()
    assert all(e.chapter == "2. Quantum Mechanics" for e in ref._visible)
    assert ref.current_entry is ref._visible[0]
    ref._chapter_filter.setCurrentText(rs._SUGGESTED_LABEL)
    qapp.processEvents()
    assert len(ref._visible) == 12 and all(e.sections for e in ref._visible)
    assert "↳" in ref._list.item(0).text()
    ref._chapter_filter.setCurrentText(rs._ALL_LABEL)
    ref._search.setText("postulates")
    qapp.processEvents()
    assert [e.rel for e in ref._visible] == [POSTULATES]
    assert ref._count_lbl.text() == "1 CHAPTER"
    ref._search.setText("zzzz-no-such-chapter")
    qapp.processEvents()
    assert ref._visible == [] and ref.current_entry is None
    assert not ref._open_btn.isEnabled()
    assert ref._count_lbl.text() == "0 CHAPTERS"
    assert "No chapters match" in ref._browser.toPlainText()
    ref._search.clear()
    qapp.processEvents()
    assert ref.current_entry is not None and ref._open_btn.isEnabled()


def test_search_keystrokes_do_not_rerender_or_scroll_the_open_chapter(ref, qapp):
    assert ref.show_doc(POSTULATES)
    qapp.processEvents()
    sb = ref._browser.verticalScrollBar()
    assert sb.maximum() > 0
    sb.setValue(sb.maximum() // 2)
    kept = sb.value()
    assert kept > 0
    calls: list[str] = []
    original = ref._render
    ref._render = lambda e: (calls.append(e.rel), original(e))[1]
    for ch in "pos":                                              # "postulates" keeps the doc visible
        ref._search.setText(ref._search.text() + ch)
        qapp.processEvents()
    assert calls == [], calls
    assert sb.value() == kept
    assert ref.current_entry.rel == POSTULATES
    assert ref._list.currentRow() == ref._visible.index(ref.current_entry)
    ref._search.setText("bosonic")                                # current doc filtered out -> one render
    qapp.processEvents()
    assert calls == [BOSONIC]


def test_show_doc_hidden_by_filter_resets_filter_and_renders_once(ref, qapp, rs):
    ref._chapter_filter.setCurrentText("7. Quantum Hardware")
    qapp.processEvents()
    assert all(e.rel not in (POSTULATES,) for e in ref._visible)
    calls: list[str] = []
    original = ref._render
    ref._render = lambda e: (calls.append(e.rel), original(e))[1]
    assert ref.show_doc(POSTULATES)
    qapp.processEvents()
    assert calls == [POSTULATES]
    assert ref._chapter_filter.currentText() == rs._ALL_LABEL and ref._search.text() == ""
    assert ref._list.currentRow() == ref._visible.index(ref.current_entry)


def test_relative_link_with_fragment_switches_doc_and_scrolls(ref, qapp):
    assert ref.show_doc(POSTULATES)
    qapp.processEvents()
    sb = ref._browser.verticalScrollBar()
    ref._on_anchor(QUrl(f"../{BOSONIC}#summary"))
    qapp.processEvents()
    assert ref.current_entry.rel == BOSONIC
    assert sb.value() > 0, "'#summary' fragment did not scroll"
    assert ref._list.currentRow() == ref._visible.index(ref.current_entry)


def test_same_document_fragment_scrolls(ref, qapp):
    assert ref.show_doc(POSTULATES)
    qapp.processEvents()
    sb = ref._browser.verticalScrollBar()
    sb.setValue(0)
    ref._on_anchor(QUrl("#exercises"))
    qapp.processEvents()
    assert sb.value() > 0


def test_external_outside_and_missing_links(ref, monkeypatch):
    opened: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl",
                        staticmethod(lambda u: (opened.append(u.toString()), True)[1]))
    assert ref.show_doc(POSTULATES)
    before = ref.current_entry
    ref._on_anchor(QUrl("https://example.com/x"))
    assert opened[-1].startswith("https://example.com")
    ref._on_anchor(QUrl("../../README.md"))                       # repo README, outside docs/
    assert opened[-1].endswith("/README.md") and "/docs/" not in opened[-1]
    assert ref.current_entry is before
    n = len(opened)
    ref._on_anchor(QUrl("99_nonexistent/01_nope.md"))
    assert len(opened) == n and ref.current_entry is before
    ref._open_btn.click()
    assert opened[-1].endswith(POSTULATES)


def test_back_button_emits_back_requested(ref):
    fired: list[int] = []
    ref.back_requested.connect(lambda: fired.append(1))
    QTest.mouseClick(ref._back_btn, Qt.MouseButton.LeftButton)
    assert fired == [1]


def test_every_doc_renders_in_the_widget(ref, rs):
    """Opening each chapter must not raise and must leave no raw math/details in the view."""
    problems = []
    for e in ref.entries:
        assert ref.show_doc(e.rel)
        text = ref._browser.toPlainText()
        if re.search(r"(^|\n)\s*\$\$", text) or re.search(r"</?(details|summary)>", text):
            problems.append(e.rel)
    assert not problems, problems[:10]


def test_missing_docs_root_degrades_gracefully(qapp, rs, monkeypatch, tmp_path):
    monkeypatch.setattr(rs, "_DOCS_ROOT", tmp_path / "no-docs-here")
    screen = rs.ReferenceScreen()
    try:
        screen.load_all()
        assert screen.entries == [] and screen.current_entry is None
        assert screen._count_lbl.text() == "NO DOCS FOUND"
        assert "Docs not found" in screen._browser.toPlainText()
        assert str(tmp_path / "no-docs-here") in screen._browser.toPlainText()
        assert not screen._open_btn.isEnabled()
        assert screen.show_doc("README.md") is False
        items = [screen._chapter_filter.itemText(i) for i in range(screen._chapter_filter.count())]
        assert items == [rs._ALL_LABEL]
    finally:
        screen.close()
        screen.deleteLater()
        qapp.processEvents()
