"""Reference contract: the in-app docs browser renders the repo docs corpus."""
from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QPushButton

from core.models import ProblemCategory


def test_docs_root_is_the_repo_docs_dir_and_scan_finds_the_corpus():
    from ui.screens.reference_screen import docs_root, scan_docs

    root = docs_root()
    assert root.is_dir() and root.name == "docs"
    assert root.parent.name == "Quantum-Computing" or (root.parent / "circuit-trainer").is_dir()

    sections = scan_docs()
    files = [p for _, files in sections for p in files]
    assert len(files) >= 50
    assert all(p.suffix == ".md" and p.is_file() for p in files)
    assert sections[0][0] == "Overview" and root / "README.md" in sections[0][1]
    assert scan_docs(root / "definitely-missing") == []


def test_load_all_populates_list_and_shows_landing_page(qapp):
    from ui.screens.reference_screen import ReferenceScreen, docs_root

    screen = ReferenceScreen()
    screen.load_all()
    assert screen.chapter_count() >= 50
    assert screen.current_doc() == docs_root() / "README.md"
    assert len(screen._browser.toPlainText().strip()) > 200
    assert screen._path_lbl.text() == "README.md"

    # Re-entry reuses the cached list (no duplicate rows).
    before = screen._list.count()
    screen.load_all()
    assert screen._list.count() == before


@pytest.mark.parametrize("category", list(ProblemCategory), ids=lambda c: c.name)
def test_every_trainer_category_jumps_to_an_existing_chapter(qapp, category):
    from ui.screens.reference_screen import ReferenceScreen

    screen = ReferenceScreen()
    assert screen.show_category(category.value) is True
    doc = screen.current_doc()
    assert doc is not None and doc.exists() and doc.suffix == ".md"
    assert "Solution" in screen._browser.toPlainText() or "Exercises" in screen._browser.toPlainText()


def test_show_doc_on_missing_path_returns_false(qapp):
    from ui.screens.reference_screen import ReferenceScreen, docs_root

    screen = ReferenceScreen()
    screen.load_all()
    assert screen.show_doc(docs_root() / "no_such_chapter.md") is False
    assert screen.current_doc() is None
    assert screen.show_category("Not a category") is False


def test_selecting_a_list_item_renders_that_chapter(qapp):
    from ui.screens.reference_screen import ReferenceScreen, _ROLE_PATH
    from pathlib import Path

    screen = ReferenceScreen()
    screen.load_all()
    items = [screen._list.item(i) for i in range(screen._list.count())]
    chapters = [it for it in items if it.data(_ROLE_PATH)]
    target = chapters[1]
    screen._list.setCurrentItem(target)
    assert screen.current_doc() == Path(target.data(_ROLE_PATH))
    assert screen._browser.toPlainText().strip()


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
