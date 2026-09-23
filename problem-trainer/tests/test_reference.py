"""Reference contract.

The docs browser is now :class:`common.ui.reference.ReferenceScreen`; what
lives in this app is the thin subclass in ``ui/screens/reference_screen.py``
that adds the topic/derivation chapter maps and the jump-and-reset verbs the
rest of the app calls.  These tests cover both halves: the shared screen does
what this app needs of it (scan <repo>/docs/**/*.md, list every page grouped by
chapter, render each one), and this app's verbs jump to the mapped chapter,
reset their filters when opened from Setup, and Back returns to the page the
user came from with their work intact.
"""
from pathlib import Path
from types import SimpleNamespace

import pytest
from PyQt6.QtCore import Qt, QUrl

import common_path  # noqa: F401  (puts the repo root on sys.path)

import common.ui.reference as shared_ref
import ui.screens.reference_screen as ref_mod
from ui.screens.reference_screen import (
    ALL_CHAPTERS, DERIVATION_CHAPTER, TOPIC_CHAPTER, ReferenceScreen, docs_root,
    pretty_chapter, prepare_markdown, read_title, scan_docs,
)

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = APP_ROOT.parent / "docs"
INDEX_ROLE = Qt.ItemDataRole.UserRole          # common.ui.reference._INDEX_ROLE


def _md_files(root: Path) -> list[Path]:
    """Every corpus page, using the shared scanner's own hidden-part rule."""
    return sorted(p for p in root.rglob("*.md")
                  if p.is_file() and not any(part.startswith((".", "_"))
                                             for part in p.relative_to(root).parts))


def _selectable(screen):
    """The document rows of the list (chapter headers carry no index)."""
    return [screen._list.item(i) for i in range(screen._list.count())
            if screen._list.item(i).data(INDEX_ROLE) is not None]


def _listed_paths(screen) -> set[Path]:
    return {screen.entries[item.data(INDEX_ROLE)].path for item in _selectable(screen)}


# ---------------------------------------------------------------------------
# The shared corpus helpers, as this app relies on them
# ---------------------------------------------------------------------------

def test_docs_root_is_the_repo_corpus():
    assert docs_root() is not None
    assert docs_root() == REPO_DOCS
    assert docs_root().is_dir()
    assert docs_root() is not shared_ref.docs_root() or True  # resolved per call
    assert ref_mod.docs_root is shared_ref.docs_root          # not a local fork


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
        assert e.title.strip() and e.chapter_label.strip() and e.label.strip()
        assert e.chapter_label == pretty_chapter(e.chapter)
        assert e.rel == e.path.relative_to(REPO_DOCS).as_posix()


def test_scan_docs_missing_root_is_empty(tmp_path):
    assert scan_docs(tmp_path / "nope") == []


def test_chapter_label_and_doc_title(tmp_path):
    assert pretty_chapter("03_quantum_gates_and_circuits") == "3. Quantum Gates and Circuits"
    assert pretty_chapter("") == "Overview"
    p = tmp_path / "02_foo_bar.md"
    p.write_text("intro line\n# My Title\n", encoding="utf-8")
    assert read_title(p) == "My Title"
    q = tmp_path / "02_no_heading.md"
    q.write_text("no heading here", encoding="utf-8")
    assert read_title(q) == ""                # the scanner falls back to the stem


def test_prepare_markdown_exposes_details_blocks():
    md = prepare_markdown("<details><summary>Solution</summary>\nfoo\n</details>")
    assert "Solution" in md and "foo" in md
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
    assert len(screen.entries) == n
    assert screen._count_lbl.text() == f"{n} documents"
    assert screen.current_chapter() == ALL_CHAPTERS
    assert len(_selectable(screen)) == n
    assert screen._list.count() > n, "chapter headers should be interleaved"
    assert screen.current_doc() is not None
    assert len(screen._browser.toPlainText().strip()) > 50

    chapters = {e.chapter for e in screen.entries}
    assert screen._chapter_filter.count() == len(chapters) + 1
    screen.load_all()                                   # idempotent
    assert len(screen.entries) == n and screen._chapter_filter.count() == len(chapters) + 1


def test_the_jump_to_topic_picker_stays_hidden():
    """This app maps a topic to a whole chapter, not to one document, so no
    category_docs mapping is passed and the shared picker hides itself."""
    s = ReferenceScreen()
    try:
        s.load_all()
        assert s.category_docs == {}
        assert not s._jump.isVisible()
        assert s.show_category("Algorithms") is False
    finally:
        s.deleteLater()


def test_selecting_a_list_item_renders_that_doc(screen):
    target = _selectable(screen)[-1]
    entry = screen.entries[target.data(INDEX_ROLE)]
    screen._list.setCurrentItem(target)
    assert screen.current_doc() == entry.path
    assert len(screen._browser.toPlainText().strip()) > 50
    assert screen._doc_title.text() == entry.title
    assert entry.rel in screen._doc_path.text()


def test_every_doc_renders_with_content(screen):
    thin = []
    for e in screen.entries:
        if not screen.open_doc(e.rel) or len(screen._browser.toPlainText().strip()) < 50:
            thin.append(e.rel)
    assert not thin


def test_select_topic_and_derivation_land_in_the_mapped_chapter(screen):
    all_paths = {e.path for e in screen.entries}
    for selector, mapping in ((screen.select_topic, TOPIC_CHAPTER),
                              (screen.select_derivation, DERIVATION_CHAPTER)):
        for name, key in mapping.items():
            assert selector(name) is True, name
            assert screen.current_chapter() == key
            doc = screen.current_doc()
            assert doc is not None and key in doc.relative_to(REPO_DOCS).parts
            assert _listed_paths(screen) == {p for p in all_paths if p.parent.name == key}
    assert screen.select_topic("Nope") is False and screen.current_chapter() == ALL_CHAPTERS
    assert screen.select_derivation("deriv_nope") is False
    assert screen.current_chapter() == ALL_CHAPTERS
    assert _listed_paths(screen) == all_paths


def test_search_narrows_and_a_jump_clears_it(screen):
    total = len(screen.entries)
    screen.set_search("phase")
    assert 0 < len(_selectable(screen)) < total

    key = TOPIC_CHAPTER["Algorithms"]
    screen.select_topic("Algorithms")
    assert screen._search.text() == ""
    assert len(_selectable(screen)) == sum(1 for e in screen.entries if e.chapter == key)


def test_show_all_resets_both_filters_and_keeps_the_open_doc(screen):
    screen.select_topic("Error Correction")
    doc = screen.current_doc()
    assert doc is not None
    screen.set_search(doc.stem.split("_")[-1])
    assert screen.current_doc() == doc
    assert len(_selectable(screen)) < len(screen.entries)

    screen.show_all()
    assert screen.current_chapter() == ALL_CHAPTERS
    assert screen._search.text() == ""
    assert len(_selectable(screen)) == len(screen.entries)
    assert screen.current_doc() == doc
    current = screen._list.currentItem()
    assert current is not None
    assert screen.entries[current.data(INDEX_ROLE)].path == doc


def test_anchor_links_and_open_externally(screen, monkeypatch):
    opened: list[str] = []
    monkeypatch.setattr(shared_ref, "QDesktopServices",
                        SimpleNamespace(openUrl=lambda u: opened.append(u.toString()) or True))
    by_chapter: dict[str, list] = {}
    for e in screen.entries:
        by_chapter.setdefault(e.chapter, []).append(e)
    chapter, docs = next((k, v) for k, v in by_chapter.items() if k and len(v) >= 2)
    a, b = docs[0], docs[1]
    other = next(e for e in screen.entries if e.chapter and e.chapter != chapter)

    screen.open_doc(a.rel)
    screen._on_anchor_clicked(QUrl(f"{b.path.name}#summary"))       # sibling .md
    assert screen.current_doc() == b.path and not opened
    screen._on_anchor_clicked(QUrl(f"../{other.chapter}/{other.path.name}"))
    assert screen.current_doc() == other.path and not opened
    screen._on_anchor_clicked(QUrl("https://example.org/x"))        # external
    assert opened == ["https://example.org/x"]
    screen._on_anchor_clicked(QUrl("does_not_exist.md"))            # dead link: no-op
    assert screen.current_doc() == other.path and len(opened) == 1

    screen._open_btn.click()
    assert opened[-1].startswith("file:") and opened[-1].endswith(other.path.name)


def test_missing_docs_dir_shows_a_helpful_message(qapp, tmp_path):
    s = ReferenceScreen(docs_root=tmp_path / "missing")
    try:
        s.load_all()
        assert s.entries == [] and s._count_lbl.text() == "0 documents"
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
    assert ref.entries == [], "docs are scanned lazily, not at startup"

    find_button(win._setup, "📖 Reference").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_REFERENCE
    assert len(ref.entries) == len(_md_files(REPO_DOCS))
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
    ref.set_search("stab")                            # leave a search behind too
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
    assert len(_selectable(ref)) == len(ref.entries)


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
