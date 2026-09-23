"""Reference contract: the in-app docs browser renders the repo docs corpus.

Since the migration the screen itself is ``common.ui.reference.ReferenceScreen``
and this app supplies two things — the chapter it opens on and the category ->
chapter map.  These tests check the contract circuit-trainer depends on, not
the shared screen's internals (``tests/test_common_reference.py`` owns those).
"""
from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QPushButton

from core.models import ProblemCategory


def test_docs_root_is_the_repo_docs_dir_and_scan_finds_the_corpus():
    from ui.screens.reference_screen import docs_root, scan_docs

    root = docs_root()
    assert root.is_dir() and root.name == "docs"
    assert root.parent.name == "Quantum-Computing" or (root.parent / "circuit-trainer").is_dir()

    entries = scan_docs()
    assert len(entries) >= 50
    assert all(e.path.suffix == ".md" and e.path.is_file() for e in entries)
    # Top-level files (the corpus README) sort before the chapter directories.
    assert entries[0].chapter == "" and entries[0].rel == "README.md"
    assert scan_docs(root / "definitely-missing") == []


def test_load_all_populates_list_and_opens_this_apps_chapter(qapp):
    from ui.screens.reference_screen import DEFAULT_CHAPTER, ReferenceScreen, docs_root

    screen = ReferenceScreen()
    screen.load_all()
    assert screen.chapter_count() >= 50
    # Circuit Trainer lands on its own rung of the ladder, not the corpus README.
    current = screen.current_doc()
    assert current is not None
    assert current.parent == docs_root() / DEFAULT_CHAPTER
    assert len(screen._browser.toPlainText().strip()) > 200

    # Re-entry keeps the reader's place and adds no duplicate rows.
    before = screen._list.count()
    screen.load_all()
    assert screen._list.count() == before
    assert screen.current_doc() == current


def test_the_corpus_readme_is_still_reachable(qapp):
    from ui.screens.reference_screen import ReferenceScreen, docs_root

    screen = ReferenceScreen()
    screen.load_all()
    assert screen.show_doc(docs_root() / "README.md") is True
    assert screen.current_doc() == docs_root() / "README.md"
    assert screen.open_doc("README.md") is True          # the shared API too


@pytest.mark.parametrize("category", list(ProblemCategory), ids=lambda c: c.name)
def test_every_trainer_category_jumps_to_an_existing_chapter(qapp, category):
    from ui.screens.reference_screen import ReferenceScreen

    screen = ReferenceScreen()
    assert screen.show_category(category.value) is True
    doc = screen.current_doc()
    assert doc is not None and doc.exists() and doc.suffix == ".md"
    assert "Solution" in screen._browser.toPlainText() or "Exercises" in screen._browser.toPlainText()


def test_the_jump_picker_offers_every_category(qapp):
    from ui.screens.reference_screen import CATEGORY_DOCS, ReferenceScreen

    screen = ReferenceScreen()
    screen.load_all()
    offered = {screen._jump.itemText(i) for i in range(1, screen._jump.count())}
    assert offered == set(CATEGORY_DOCS)
    assert screen._jump.isVisible() or not screen.isVisible()   # shown once the screen is


def test_show_doc_on_a_missing_path_returns_false_and_keeps_your_place(qapp):
    from ui.screens.reference_screen import ReferenceScreen, docs_root

    screen = ReferenceScreen()
    screen.load_all()
    where_i_was = screen.current_doc()
    assert screen.show_doc(docs_root() / "no_such_chapter.md") is False
    # The old fork blanked the browser here; a failed jump must not cost the
    # reader the chapter they were reading.
    assert screen.current_doc() == where_i_was
    assert screen.show_category("Not a category") is False


def test_selecting_a_list_item_renders_that_chapter(qapp):
    from ui.screens.reference_screen import ReferenceScreen

    screen = ReferenceScreen()
    screen.load_all()
    items = [screen._list.item(i) for i in range(screen._list.count())]
    chapters = [it for it in items if it.data(256) is not None]   # Qt.UserRole
    target = chapters[1]
    screen._list.setCurrentItem(target)
    assert screen.current_doc() is not None
    assert screen.current_entry.label == target.text()
    assert screen._browser.toPlainText().strip()


def test_search_filters_the_list(qapp):
    from ui.screens.reference_screen import ReferenceScreen

    screen = ReferenceScreen()
    screen.load_all()
    everything = len(screen.visible_titles())
    screen.set_search("surface code")
    filtered = screen.visible_titles()
    assert 0 < len(filtered) < everything


def test_back_button_emits_back_requested(qapp):
    from ui.screens.reference_screen import ReferenceScreen

    screen = ReferenceScreen()
    fired = []
    screen.back_requested.connect(lambda: fired.append(True))
    back = [b for b in screen.findChildren(QPushButton) if b.text() == "← Back"]
    assert len(back) == 1
    back[0].click()
    assert fired == [True]


def test_main_window_routes_reference_and_back(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow, PAGE_REFERENCE, PAGE_SETUP

    win = MainWindow()
    try:
        assert win._stack.currentIndex() == PAGE_SETUP
        ref_btn = [b for b in win._setup.findChildren(QPushButton) if b.text() == "Reference"]
        assert len(ref_btn) == 1
        ref_btn[0].click()
        assert win._stack.currentIndex() == PAGE_REFERENCE
        assert win._reference.chapter_count() >= 50
        win._reference.back_requested.emit()
        assert win._stack.currentIndex() == PAGE_SETUP
    finally:
        win.close()
