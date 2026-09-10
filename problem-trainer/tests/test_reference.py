"""Reference contract.

The in-app docs browser scans <repo>/docs/**/*.md (resolved relative to the
module, never a hardcoded home), lists every page grouped by chapter, renders
each one, jumps to the mapped chapter for a problem topic / derivation id,
resets its filters when opened from Setup, and Back returns to the page the
user came from with their work intact.
"""
from pathlib import Path
from types import SimpleNamespace

import pytest
from PyQt6.QtCore import Qt, QUrl

import ui.screens.reference_screen as ref_mod
from ui.screens.reference_screen import (
    ALL_CHAPTERS, DERIVATION_CHAPTER, TOPIC_CHAPTER, ReferenceScreen,
    chapter_label, doc_title, docs_root, render_markdown_source, scan_docs,
)

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = APP_ROOT.parent / "docs"
USER_ROLE = Qt.ItemDataRole.UserRole


def _md_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md")
                  if not any(part.startswith(".") for part in p.relative_to(root).parts))


def _selectable(screen):
    return [screen._list.item(i) for i in range(screen._list.count())
            if screen._list.item(i).flags() & Qt.ItemFlag.ItemIsSelectable]


def _listed_paths(screen) -> set[Path]:
    return {Path(item.data(USER_ROLE)) for item in _selectable(screen)}


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_docs_root_is_repo_docs_resolved_relative_to_the_module():
    assert docs_root() == Path(ref_mod.__file__).resolve().parents[3] / "docs"
    assert docs_root() == REPO_DOCS
    assert docs_root().is_dir()


def test_scan_docs_finds_every_markdown_page_in_order():
    expected = _md_files(REPO_DOCS)
    entries = scan_docs()
    assert len(entries) == len(expected) > 0
    assert sorted(e.path for e in entries) == expected

    chapters = [e.chapter for e in entries]
    assert "" in chapters, "root README should be listed under Overview"
    assert len(set(chapters)) >= 9, "expected the 8 numbered chapters plus the root"
    # root first, then chapter directories in name order
    assert chapters == sorted(chapters, key=lambda k: (k != "", k))
    for e in entries:
        assert e.title.strip() and e.chapter_label.strip()
        assert e.chapter_label == chapter_label(e.chapter)


def test_scan_docs_missing_root_is_empty(tmp_path):
    assert scan_docs(tmp_path / "nope") == []


def test_chapter_label_and_doc_title(tmp_path):
    assert chapter_label("03_quantum_gates_and_circuits") == "03 · Quantum Gates and Circuits"
    assert chapter_label("") == "Overview"
    p = tmp_path / "02_foo_bar.md"
    p.write_text("intro line\n# My Title\n", encoding="utf-8")
    assert doc_title(p) == "My Title"
    q = tmp_path / "02_no_heading.md"
    q.write_text("no heading here", encoding="utf-8")
    assert doc_title(q) == "No Heading"


def test_render_markdown_source_exposes_details_blocks():
    md = render_markdown_source("<details><summary>Solution</summary>\nfoo\n</details>")
    assert "**Solution**" in md and "foo" in md
    assert "<details>" not in md and "</details>" not in md


def test_topic_and_derivation_maps_cover_the_banks_and_real_chapters(problems, derivations):
    assert {p.topic for p in problems} <= set(TOPIC_CHAPTER)
    assert {d.id for d in derivations} <= set(DERIVATION_CHAPTER)
    for key in set(TOPIC_CHAPTER.values()) | set(DERIVATION_CHAPTER.values()):
        assert (REPO_DOCS / key).is_dir(), key
        assert list((REPO_DOCS / key).glob("*.md")), key


# ---------------------------------------------------------------------------
# ReferenceScreen on its own
# ---------------------------------------------------------------------------

@pytest.fixture
def screen(qapp):
    s = ReferenceScreen()
    s.load_all()
    yield s
    s.deleteLater()
    qapp.processEvents()


def test_load_all_lists_every_doc_and_opens_one(screen):
    n = len(_md_files(REPO_DOCS))
    assert len(screen.entries()) == n
    assert screen._count_lbl.text() == f"{n} pages"
    assert screen.current_chapter() == ALL_CHAPTERS
    assert len(_selectable(screen)) == n
    assert screen._list.count() > n, "chapter headers should be interleaved"
    assert screen.current_doc() is not None
    assert len(screen._browser.toPlainText().strip()) > 50
    assert screen._open_btn.isEnabled()
    assert "›" in screen._crumb_lbl.text()

    chapters = {e.chapter for e in screen.entries()}
    assert screen._chapter_filter.count() == len(chapters) + 1
    screen.load_all()                                   # idempotent
    assert len(screen.entries()) == n and screen._chapter_filter.count() == len(chapters) + 1


def test_selecting_a_list_item_renders_that_doc(screen):
    target = _selectable(screen)[-1]
    screen._list.setCurrentItem(target)
    assert screen.current_doc() == Path(target.data(USER_ROLE))
    assert len(screen._browser.toPlainText().strip()) > 50
    assert screen._crumb_lbl.text().endswith(target.text())


def test_every_doc_renders_with_content(screen):
    thin = []
    for e in screen.entries():
        if not screen.show_doc(e.path) or len(screen._browser.toPlainText().strip()) < 50:
            thin.append(e.path.name)
    assert not thin


def test_select_topic_and_derivation_land_in_the_mapped_chapter(screen):
    all_paths = {e.path for e in screen.entries()}
    for selector, mapping in ((screen.select_topic, TOPIC_CHAPTER),
                              (screen.select_derivation, DERIVATION_CHAPTER)):
        for name, key in mapping.items():
            assert selector(name) is True, name
            assert screen.current_chapter() == key
            doc = screen.current_doc()
            assert doc is not None and key in doc.relative_to(REPO_DOCS).parts
            assert _listed_paths(screen) == {p for p in all_paths if p.parent.name == key}
    assert screen.select_topic("Nope") is False and screen.current_chapter() == ALL_CHAPTERS
    assert screen.select_derivation("deriv_nope") is False and screen.current_chapter() == ALL_CHAPTERS
    assert _listed_paths(screen) == all_paths


def test_title_filter_narrows_and_a_jump_clears_it(screen):
    total = len(screen.entries())
    screen._search.setText("phase")
    visible = _selectable(screen)
    assert 0 < len(visible) < total
    for item in visible:
        haystack = item.text().lower() + Path(item.data(USER_ROLE)).name.lower()
        assert "phase" in haystack

    key = TOPIC_CHAPTER["Algorithms"]
    screen.select_topic("Algorithms")
    assert screen._search.text() == ""
    assert len(_selectable(screen)) == sum(1 for e in screen.entries() if e.chapter == key)


def test_show_all_resets_both_filters_and_keeps_the_open_doc(screen):
    screen.select_topic("Error Correction")
    doc = screen.current_doc()
    assert doc is not None
    screen._search.setText(doc.stem.split("_")[-1])
    assert screen.current_doc() == doc
    assert len(_selectable(screen)) < len(screen.entries())

    screen.show_all()
    assert screen.current_chapter() == ALL_CHAPTERS
    assert screen._search.text() == ""
    assert len(_selectable(screen)) == len(screen.entries())
    assert screen.current_doc() == doc
    assert screen._list.currentItem() is not None
    assert Path(screen._list.currentItem().data(USER_ROLE)) == doc


def test_no_match_filter_shows_message_and_disables_open(screen):
    screen._search.setText("zzzz-no-such-title")
    assert not _selectable(screen)
    assert screen.current_doc() is None
    assert not screen._open_btn.isEnabled()
    assert "No pages match" in screen._browser.toPlainText()
    screen._search.clear()
    assert screen.current_doc() is not None and screen._open_btn.isEnabled()


def test_anchor_links_and_open_externally(screen, monkeypatch):
    opened: list[str] = []
    monkeypatch.setattr(ref_mod, "QDesktopServices",
                        SimpleNamespace(openUrl=lambda u: opened.append(u.toString()) or True))
    by_chapter: dict[str, list] = {}
    for e in screen.entries():
        by_chapter.setdefault(e.chapter, []).append(e)
    chapter, docs = next((k, v) for k, v in by_chapter.items() if k and len(v) >= 2)
    a, b = docs[0], docs[1]
    other = next(e for e in screen.entries() if e.chapter and e.chapter != chapter)

    screen.show_doc(a.path)
    screen._on_anchor_clicked(QUrl(f"{b.path.name}#summary"))       # sibling .md
    assert screen.current_doc() == b.path and not opened
    screen._on_anchor_clicked(QUrl(f"../{other.chapter}/{other.path.name}"))   # ../chapter/x.md
    assert screen.current_doc() == other.path and not opened
    screen._on_anchor_clicked(QUrl("https://example.org/x"))         # external
    assert opened == ["https://example.org/x"]
    screen._on_anchor_clicked(QUrl("does_not_exist.md"))             # dead link: no-op
    assert screen.current_doc() == other.path and len(opened) == 1

    screen._open_btn.click()
    assert opened[-1].startswith("file:") and opened[-1].endswith(other.path.name)


def test_missing_docs_dir_shows_a_helpful_message(qapp, monkeypatch, tmp_path):
    monkeypatch.setattr(ref_mod, "_DOCS_ROOT", tmp_path / "missing")
    s = ReferenceScreen()
    try:
        s.load_all()
        assert s.entries() == [] and s._count_lbl.text() == "no docs found"
        assert "No documentation found" in s._browser.toPlainText()
        assert s.select_topic("Algorithms") is False
        s.show_all()
        assert "No documentation found" in s._browser.toPlainText()
        assert not s._open_btn.isEnabled()
    finally:
        s.deleteLater()
        qapp.processEvents()


# ---------------------------------------------------------------------------
# MainWindow integration
# ---------------------------------------------------------------------------

def test_setup_reference_button_opens_unfiltered_and_back_returns(main_window, qapp, find_button):
    from ui.main_window import PAGE_REFERENCE, PAGE_SETUP

    win = main_window
    ref = win._reference
    assert ref.entries() == [], "docs are scanned lazily, not at startup"

    find_button(win._setup, "📖 Reference").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_REFERENCE
    assert len(ref.entries()) == len(_md_files(REPO_DOCS))
    assert ref.current_chapter() == ALL_CHAPTERS and ref._search.text() == ""
    assert ref.current_doc() is not None

    find_button(ref, "← Back").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_SETUP


def test_setup_reference_resets_a_stale_topic_jump(main_window, problems, qapp, find_button):
    from ui.main_window import PAGE_PROBLEM, PAGE_REFERENCE, PAGE_SETUP
    from ui.screens.setup_screen import MODE_PROBLEMS

    win = main_window
    ref = win._reference
    key = TOPIC_CHAPTER["Error Correction"]
    p = next(p for p in problems if p.topic == "Error Correction")
    win._setup.session_started.emit(MODE_PROBLEMS, [p])
    qapp.processEvents()

    find_button(win._problem, "📖 Reference").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_REFERENCE
    assert ref.current_chapter() == key
    ref._search.setText("stab")                       # leave a title filter behind too
    find_button(ref, "← Back").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_PROBLEM

    find_button(win._problem, "End Session").click()  # no attempts -> straight to Setup
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_SETUP

    find_button(win._setup, "📖 Reference").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_REFERENCE
    assert ref.current_chapter() == ALL_CHAPTERS
    assert ref._search.text() == ""
    assert len(_selectable(ref)) == len(ref.entries())


def test_problem_reference_jump_returns_with_work_intact(main_window, problems, qapp, find_button):
    from ui.main_window import PAGE_PROBLEM, PAGE_REFERENCE
    from ui.screens.setup_screen import MODE_PROBLEMS

    win = main_window
    ref = win._reference
    p0 = problems[0]
    key = TOPIC_CHAPTER[p0.topic]
    win._setup.session_started.emit(MODE_PROBLEMS, [p0])
    qapp.processEvents()
    pw = win._problem._part_widgets[p0.parts[0].part_id]
    pw._answer_edit.setPlainText("my answer |ψ⟩")

    find_button(win._problem, "📖 Reference").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_REFERENCE
    assert ref.current_chapter() == key
    assert ref.current_doc() is not None and key in ref.current_doc().parts

    find_button(ref, "← Back").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_PROBLEM
    assert win._problem._problem is p0
    assert pw._answer_edit.toPlainText() == "my answer |ψ⟩"
    assert pw._submit_btn.isEnabled()


def test_derivation_reference_jump_returns_to_the_derivation(main_window, derivations, qapp,
                                                             find_button):
    from ui.main_window import PAGE_DERIVATION, PAGE_REFERENCE
    from ui.screens.setup_screen import MODE_DERIVATIONS

    win = main_window
    ref = win._reference
    d0 = derivations[0]
    win._setup.session_started.emit(MODE_DERIVATIONS, [d0])
    qapp.processEvents()
    ds = win._derivation
    ds._answer_edit.setPlainText("step one")

    find_button(ds, "📖 Reference").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_REFERENCE
    assert ref.current_chapter() == DERIVATION_CHAPTER[d0.id]

    find_button(ref, "← Back").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_DERIVATION
    assert ds._derivation is d0 and ds._idx == 0
    assert ds._answer_edit.toPlainText() == "step one"
