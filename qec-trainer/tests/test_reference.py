"""In-app docs browser (REFERENCE CONTRACT): discovery, rendering, links, topics.

Runs against the live ``<repo>/docs`` corpus so a broken docs root, a regex
regression in ``prepare_markdown`` / ``_linkify`` or a dead Back / anchor path
fails here rather than in the running app.
"""
from __future__ import annotations

import pathlib
import re

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QTextDocument, QTextFormat
from PyQt6.QtTest import QTest

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = APP_ROOT.parent / "docs"


def _live_docs() -> list[pathlib.Path]:
    """Every docs/**/*.md that the screen must list (hidden/_private parts skipped)."""
    return sorted(
        p for p in DOCS.rglob("*.md")
        if p.is_file() and not any(s.startswith((".", "_")) for s in p.relative_to(DOCS).parts)
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


@pytest.fixture
def app_first_rel(rs) -> str:
    chapter = DOCS / rs._APP_CHAPTER_DIR
    return f"{rs._APP_CHAPTER_DIR}/{sorted(p.name for p in chapter.glob('*.md'))[0]}"


# ── discovery ────────────────────────────────────────────────────────────────

def test_docs_root_is_the_repo_docs_folder(rs):
    assert rs.docs_root() == APP_ROOT.parent / "docs"
    assert rs.ReferenceScreen.docs_root() == rs.docs_root()
    assert rs.docs_root().is_dir()


def test_scan_docs_lists_every_markdown_file_in_ladder_order(rs):
    entries = rs.scan_docs()
    live = _live_docs()
    assert len(entries) == len(live) > 0
    assert {e.rel for e in entries} == {p.relative_to(DOCS).as_posix() for p in live}
    assert entries[0].rel == "README.md"                      # overview first
    chapters = [e for e in entries if e.chapter]
    assert len(chapters) == len(list(DOCS.glob("*/*.md")))
    assert all(re.match(r"^\d+\.\d+  \S", e.label) for e in chapters), \
        [e.label for e in chapters if not re.match(r"^\d+\.\d+  \S", e.label)][:3]
    assert [e.rel for e in chapters] == sorted(e.rel for e in chapters)


def test_every_bank_category_maps_to_an_existing_doc(rs):
    from problems import all_categories

    missing = [c for c in all_categories() if c not in rs.CATEGORY_DOC]
    assert not missing, f"categories without a CATEGORY_DOC entry: {missing}"
    for category, rel in rs.CATEGORY_DOC.items():
        assert (DOCS / rel).is_file(), f"{category!r} -> missing docs/{rel}"


# ── screen: opening, list, filters ───────────────────────────────────────────

def test_screen_opens_on_this_apps_chapter(ref, rs, app_first_rel):
    live = _live_docs()
    assert ref.current_entry is not None and ref.current_entry.rel == app_first_rel
    assert ref._doc_title.text() == ref.current_entry.title
    assert ref._doc_path.text().endswith(f"docs/{app_first_rel}")
    assert ref._browser.toPlainText().strip()
    assert ref._count_lbl.text() == f"{len(live)} documents"
    assert len(ref.visible_titles()) == len(live)
    assert ref._jump.count() == len(rs.CATEGORY_DOC) + 1
    assert ref._open_btn.isEnabled()


def test_open_doc_renders_once_and_reports_missing(ref, app_first_rel):
    opened: list[str] = []
    ref.doc_opened.connect(opened.append)
    other = next(e for e in ref.entries if e.chapter and e.rel != app_first_rel)
    assert ref.open_doc(other.rel) is True
    assert ref.current_entry is other
    assert opened == [other.rel]
    assert ref._doc_title.text() == other.title
    assert ref.open_doc("99_nonexistent/01_nope.md") is False
    assert ref.current_entry is other


def test_open_doc_hidden_by_filter_clears_filter_and_renders_only_target(ref, rs):
    ref.show_chapter(rs._APP_CHAPTER_DIR)
    assert all(e.chapter == rs._APP_CHAPTER_DIR
               for e in ref.entries if e.title in ref.visible_titles())
    other = next(e for e in ref.entries if e.chapter and e.chapter != rs._APP_CHAPTER_DIR)
    opened: list[str] = []
    ref.doc_opened.connect(opened.append)
    assert ref.open_doc(other.rel)
    assert opened == [other.rel]                 # no detour through the first match
    assert ref._chapter_filter.currentIndex() == 0
    assert ref.current_entry is other
    item = ref._list.currentItem()
    assert item is not None and ref.entries[item.data(rs._INDEX_ROLE)] is other


def test_chapter_filter_and_search(ref, rs):
    total = len(_live_docs())
    n_chapter = len(list((DOCS / rs._APP_CHAPTER_DIR).glob("*.md")))
    ref.show_chapter(rs._APP_CHAPTER_DIR)
    assert len(ref.visible_titles()) == n_chapter
    assert ref._count_lbl.text() == f"{n_chapter} of {total} documents"
    ref.show_chapter("")
    ref.set_search("zzzz_no_such_term_qqqq")
    assert ref.visible_titles() == []
    assert ref._count_lbl.text().startswith("0 of")
    ref.set_search("stabilizer")
    hits = ref.visible_titles()
    assert 0 < len(hits) < total
    rows = [ref._list.item(i).text() for i in range(ref._list.count())
            if ref._list.item(i).data(rs._INDEX_ROLE) is not None]
    assert all(re.search(r"\(\d+\)$", t) for t in rows), rows[:3]
    assert ref._browser.textCursor().selectedText().lower() == "stabilizer"
    ref.set_search("")
    assert len(ref.visible_titles()) == total


def test_show_category_for_every_topic_and_jump_picker(ref, rs):
    for category, rel in rs.CATEGORY_DOC.items():
        assert ref.show_category(category) is True
        assert ref.current_entry.rel == rel
    assert ref.show_category("No Such Topic") is False
    ref._jump.activated.emit(1)
    assert ref.current_entry.rel == next(iter(rs.CATEGORY_DOC.values()))
    assert ref._jump.currentIndex() == 0         # picker resets to its placeholder


def test_back_button_emits_back_requested(ref):
    fired: list[int] = []
    ref.back_requested.connect(lambda: fired.append(1))
    QTest.mouseClick(ref._back_btn, Qt.MouseButton.LeftButton)
    assert fired == [1]


# ── links ────────────────────────────────────────────────────────────────────

def test_relative_link_with_fragment_switches_doc_and_scrolls(ref, qapp, rs, app_first_rel):
    ref.open_doc(app_first_rel)
    qapp.processEvents()
    src = ref.current_entry
    target = next(e for e in ref.entries
                  if e.chapter and e.chapter != src.chapter and "\n## Summary" in e.text())
    sb = ref._browser.verticalScrollBar()
    ref._on_anchor_clicked(QUrl(f"../{target.rel}#summary"))
    qapp.processEvents()
    assert ref.current_entry is target
    assert sb.value() > 0, "'#summary' fragment did not scroll"
    item = ref._list.currentItem()
    assert item is not None and ref.entries[item.data(rs._INDEX_ROLE)] is target


def test_real_mouse_click_on_cross_reference_link_navigates(ref, qapp, rs, monkeypatch):
    """QTextBrowser -> anchorClicked -> open_doc, end to end through a real click."""
    from PyQt6.QtGui import QTextCursor

    opened_ext: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl",
                        staticmethod(lambda u: (opened_ext.append(u.toString()), True)[1]))
    link = None
    for e in sorted(ref.entries, key=lambda e: e.chapter != rs._APP_CHAPTER_DIR):
        ref.open_doc(e.rel)
        qapp.processEvents()
        block = ref._browser.document().begin()
        while block.isValid() and link is None:
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                href = frag.charFormat().anchorHref()
                if href.endswith(".md") and not href.startswith(("http", "#")):
                    link = (e, frag.position(), href)
                    break
                it += 1
            block = block.next()
        if link:
            break
    assert link, "no linkified cross-reference found in the corpus"
    src, pos, href = link
    emitted: list[str] = []
    ref._browser.anchorClicked.connect(lambda u: emitted.append(u.toString()))
    cur = QTextCursor(ref._browser.document())
    cur.setPosition(pos + 1)
    ref._browser.setTextCursor(cur)
    ref._browser.ensureCursorVisible()
    qapp.processEvents()
    rect = ref._browser.cursorRect(cur)
    point = rect.center()
    point.setX(rect.left() + 2)
    assert ref._browser.anchorAt(point) == href
    QTest.mouseClick(ref._browser.viewport(), Qt.MouseButton.LeftButton, pos=point)
    qapp.processEvents()
    assert emitted == [href]
    expect = (src.path.parent / href.split("#")[0]).resolve().relative_to(DOCS.resolve()).as_posix()
    assert ref.current_entry.rel == expect
    item = ref._list.currentItem()
    assert item is not None and ref.entries[item.data(rs._INDEX_ROLE)].rel == expect
    assert opened_ext == []


def test_same_document_fragment_scrolls(ref, qapp, app_first_rel):
    ref.open_doc(app_first_rel)
    qapp.processEvents()
    _, names = _anchors(ref._browser.document())
    assert {"key-formulas", "summary", "exercises"} <= names
    sb = ref._browser.verticalScrollBar()
    sb.setValue(0)
    ref._on_anchor_clicked(QUrl("#exercises"))
    qapp.processEvents()
    assert sb.value() > 0


def test_external_outside_and_missing_links(ref, monkeypatch, app_first_rel):
    opened: list[str] = []
    monkeypatch.setattr(QDesktopServices, "openUrl",
                        staticmethod(lambda u: (opened.append(u.toString()), True)[1]))
    ref.open_doc(app_first_rel)
    before = ref.current_entry
    ref._on_anchor_clicked(QUrl("https://example.com/x"))
    assert opened[-1].startswith("https://example.com")
    ref._on_anchor_clicked(QUrl("../../README.md"))          # repo README, outside docs/
    assert opened[-1].endswith("/README.md") and "/docs/" not in opened[-1]
    assert ref.current_entry is before
    n = len(opened)
    ref._on_anchor_clicked(QUrl("99_nonexistent/01_nope.md"))
    assert len(opened) == n and ref.current_entry is before
    ref._open_externally()
    assert opened[-1].endswith(before.rel)


# ── markdown preparation (pure functions) ────────────────────────────────────

def test_linkify_bare_refs_including_fragments(rs):
    entries = rs.scan_docs()
    here = next(e for e in entries if e.chapter)
    there = next(e for e in entries if e.chapter and e.chapter != here.chapter)
    sibling = next(e for e in entries if e.chapter == here.chapter and e is not here)
    prep = lambda md: rs.prepare_markdown(md, here.path.parent)

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
    assert rs.resolve_doc_ref(f"{there.rel}#summary", here.path.parent) == f"../{there.rel}#summary"
    assert rs.resolve_doc_ref("99_nonexistent/01_nope.md#x", here.path.parent) is None


def test_display_math_and_details_rewrites(rs):
    md = "Energy:\n\n$$E = mc^2$$\n\nUse `$$` in files.\n\n```\n$$ raw $$\n```\n"
    out = rs.prepare_markdown(md)
    assert "\n```math\nE = mc^2\n```\n" in out       # tagged so only formulas soft-wrap
    assert "`$$`" in out and "```\n$$ raw $$\n```" in out   # inline / fenced code untouched

    details = "<details><summary>Solution</summary>\n\nBecause `X` anticommutes.\n\n</details>\n"
    shown = rs.prepare_markdown(details, show_solutions=True)
    hidden = rs.prepare_markdown(details, show_solutions=False)
    assert "**▸ Solution**" in shown and "anticommutes" in shown and "<details>" not in shown
    assert "hidden — tick" in hidden and "anticommutes" not in hidden and "<details>" not in hidden


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


def test_heading_slug(rs):
    assert rs.heading_slug("Key Formulas") == "key-formulas"
    assert rs.heading_slug("QAOA: Quantum Approximate Optimization Algorithm") == \
        "qaoa-quantum-approximate-optimization-algorithm"
    # GitHub keeps one hyphen per space, so removed punctuation leaves a double hyphen
    assert rs.heading_slug("Important Distinction: QFT ≠ Classical FFT Speedup") == \
        "important-distinction-qft--classical-fft-speedup"
    assert rs.heading_slug("Step 2 — the `oracle` call") == "step-2--the-oracle-call"


def _block_anchor_names(doc: QTextDocument) -> list[str]:
    """Anchor names per block (a heading with inline code spans several fragments)."""
    names: list[str] = []
    block = doc.begin()
    while block.isValid():
        seen: list[str] = []
        it = block.begin()
        while not it.atEnd():
            fmt = it.fragment().charFormat()
            for n in (fmt.anchorNames() if fmt.isAnchor() else []):
                if n not in seen:
                    seen.append(n)
            it += 1
        names += seen
        block = block.next()
    return names


def test_repeated_headings_get_github_numbered_anchors(ref, qapp, rs):
    md = ("# Doc\n\n## The Algorithm\n\n" + "text\n\n" * 40 +
          "\n## The Algorithm\n\n" + "text\n\n" * 40 +
          "\n### The `Algorithm`\n\n" + "text\n\n" * 40 + "\n## Summary\n\ndone\n")
    ref._browser.setMarkdown(rs.prepare_markdown(md))
    rs.restyle_document(ref._browser.document())
    names = _block_anchor_names(ref._browser.document())
    assert names == ["doc", "the-algorithm", "the-algorithm-1", "the-algorithm-2", "summary"]
    sb = ref._browser.verticalScrollBar()
    positions = []
    for name in names[1:4]:
        sb.setValue(0)
        ref._browser.scrollToAnchor(name)
        qapp.processEvents()
        positions.append(sb.value())
    assert positions == sorted(positions) and len(set(positions)) == 3, positions


def test_only_generated_math_blocks_soft_wrap(ref, rs):
    md = ("$$E = mc^2$$\n\n```\nplain fence\n```\n\n```python\nprint(1)\n```\n\n"
          "> quoted\n> $$a = b$$\n")
    ref._browser.setMarkdown(rs.prepare_markdown(md))
    rs.restyle_document(ref._browser.document())
    seen = []
    block = ref._browser.document().begin()
    while block.isValid():
        bf = block.blockFormat()
        if bf.hasProperty(QTextFormat.Property.BlockCodeLanguage):
            seen.append((block.text(),
                         bf.stringProperty(QTextFormat.Property.BlockCodeLanguage),
                         bf.nonBreakableLines()))
        block = block.next()
    assert seen == [("E = mc^2", "math", False),        # formula: wraps
                    ("plain fence", "", True),          # author fences keep their layout
                    ("print(1)", "python", True),
                    ("a = b", "math", False)], seen


# ── whole corpus ─────────────────────────────────────────────────────────────

def test_every_doc_renders_clean_with_working_links_and_anchors(ref, rs):
    problems: list[str] = []
    n_links = 0
    for e in ref.entries:
        assert ref.open_doc(e.rel)
        text = ref._browser.toPlainText()
        if re.search(r"(^|\n)\s*\$\$", text) or re.search(r"</?(details|summary)>", text):
            problems.append(f"{e.rel}: raw $$ / <details> leaked")
        hrefs, names = _anchors(ref._browser.document())
        for h in hrefs:
            if h.startswith(("http", "#", "mailto")):
                continue
            n_links += 1
            if not (e.path.parent / h.split("#")[0]).resolve().is_file():
                problems.append(f"{e.rel}: dead link {h}")
        prose = "".join(rs._FENCE.split(e.text())[::2])       # headings outside code fences
        per_block = _block_anchor_names(ref._browser.document())
        if len(per_block) != len(set(per_block)):
            problems.append(f"{e.rel}: duplicate anchor names")
        count: dict[str, int] = {}
        for heading in re.findall(r"^#{1,6} +(.+?)\s*$", prose, re.M):
            slug = rs.heading_slug(heading)
            want = f"{slug}-{count[slug]}" if count.get(slug) else slug   # GitHub numbering
            count[slug] = count.get(slug, 0) + 1
            if want not in names:
                problems.append(f"{e.rel}: no anchor {want!r} for '{heading}'")
    assert not problems, problems[:10]
    assert n_links > 0                            # the corpus does cross-reference itself


def test_solutions_toggle_on_a_real_doc(ref, qapp):
    e = next(e for e in ref.entries if "<details>" in e.text())
    ref.open_doc(e.rel)
    shown = ref._browser.toPlainText()
    assert "▸ Solution" in shown and "<details>" not in shown
    ref._solutions_cb.setChecked(False)
    qapp.processEvents()
    hidden = ref._browser.toPlainText()
    assert "hidden — tick" in hidden and len(hidden) < len(shown)
    ref._solutions_cb.setChecked(True)


def test_reload_keeps_filters_search_and_place(ref, qapp, rs, app_first_rel):
    ref.open_doc(app_first_rel)
    ref.show_chapter(rs._APP_CHAPTER_DIR)
    ref.set_search("zzzz_no_such_term_qqqq")
    qapp.processEvents()
    assert ref.visible_titles() == []
    ref.reload()                                     # must not jump to a search hit elsewhere
    qapp.processEvents()
    assert ref.current_entry.rel == app_first_rel
    assert ref._chapter_filter.currentData() == rs._APP_CHAPTER_DIR
    assert ref._search.text() == "zzzz_no_such_term_qqqq"
    assert ref.visible_titles() == []
    ref.set_search("")
    sb = ref._browser.verticalScrollBar()
    sb.setValue(0)
    ref._browser.scrollToAnchor("summary")
    qapp.processEvents()
    kept = sb.value()
    assert kept > 0
    ref.reload()
    qapp.processEvents()
    assert ref.current_entry.rel == app_first_rel and sb.value() == kept


def test_load_all_rescans_when_the_docs_tree_changes(qapp, rs, monkeypatch, tmp_path):
    import os
    root = tmp_path / "docs"
    chapter = root / rs._APP_CHAPTER_DIR
    chapter.mkdir(parents=True)
    (root / "README.md").write_text("# Overview\n", encoding="utf-8")
    (chapter / "01_a.md").write_text("# A\n\nbody a\n", encoding="utf-8")
    monkeypatch.setattr(rs, "_DOCS_ROOT", root)
    screen = rs.ReferenceScreen()
    try:
        screen.load_all()
        assert [e.rel for e in screen.entries] == ["README.md", f"{rs._APP_CHAPTER_DIR}/01_a.md"]
        screen.show_chapter(rs._APP_CHAPTER_DIR)
        (chapter / "02_b.md").write_text("# B\n\nbody b\n", encoding="utf-8")
        screen.load_all()                            # notices the new file …
        assert [e.rel for e in screen.entries] == \
            ["README.md", f"{rs._APP_CHAPTER_DIR}/01_a.md", f"{rs._APP_CHAPTER_DIR}/02_b.md"]
        assert screen.current_entry.rel == f"{rs._APP_CHAPTER_DIR}/01_a.md"   # … keeps place
        assert screen._chapter_filter.currentData() == rs._APP_CHAPTER_DIR    # … and filter
        assert screen._count_lbl.text() == "2 of 3 documents"
        (chapter / "01_a.md").write_text("# A\n\nEDITED body\n", encoding="utf-8")
        os.utime(chapter / "01_a.md", ns=(2_000_000_000_000_000_000, 2_000_000_000_000_000_000))
        screen.load_all()                            # edited file is re-read
        assert "EDITED" in screen._browser.toPlainText()
        (chapter / "01_a.md").unlink()
        screen.load_all()                            # current file gone -> chapter default
        assert screen.current_entry.rel == f"{rs._APP_CHAPTER_DIR}/02_b.md"
        assert [e.rel for e in screen.entries] == ["README.md", f"{rs._APP_CHAPTER_DIR}/02_b.md"]
    finally:
        screen.close()


def test_missing_docs_root_degrades_gracefully(qapp, rs, monkeypatch, tmp_path):
    monkeypatch.setattr(rs, "_DOCS_ROOT", tmp_path / "no-docs-here")
    screen = rs.ReferenceScreen()
    try:
        screen.load_all()
        assert screen.entries == []
        assert screen.current_entry is None
        assert screen._doc_title.text() == "No documentation found"
        assert screen._count_lbl.text() == "0 documents"
        assert screen._jump.isHidden()
        assert not screen._open_btn.isEnabled()
        assert screen.open_doc("README.md") is False
        assert screen.show_category(next(iter(rs.CATEGORY_DOC))) is False
    finally:
        screen.close()
