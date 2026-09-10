"""Reference screen: docs discovery, default chapter, selection, filters,
in-reader links, Back, and the missing-docs fallback."""
from __future__ import annotations

import os
import pathlib

import pytest
from PyQt6.QtCore import QUrl, Qt

import ui.screens.reference_screen as rs
from ui.screens.reference_screen import ReferenceScreen, scan_docs, docs_root

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_DOCS = APP_ROOT.parent / "docs"
USER_ROLE = Qt.ItemDataRole.UserRole


def _data_rows(screen: ReferenceScreen) -> list[int]:
    """Entry indices currently listed (header rows carry no UserRole data)."""
    rows = []
    for i in range(screen._list.count()):
        data = screen._list.item(i).data(USER_ROLE)
        if data is not None:
            rows.append(int(data))
    return rows


# ── scan_docs ─────────────────────────────────────────────────────────────────

def test_docs_root_resolves_to_repo_docs_regardless_of_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert docs_root() == REPO_DOCS.resolve()
    assert docs_root().is_dir()


def test_scan_docs_lists_every_chapter_file_in_ladder_order():
    entries = scan_docs()
    on_disk = sorted(p.resolve() for p in REPO_DOCS.rglob("*.md"))
    assert len(entries) >= 50
    assert sorted(e.path for e in entries) == on_disk
    assert all(e.path.suffix == ".md" and e.path.is_relative_to(REPO_DOCS.resolve()) for e in entries)
    assert all(e.title.strip() for e in entries)
    chapters = []
    for e in entries:
        if e.chapter not in chapters:
            chapters.append(e.chapter)
    assert chapters[0] == "Overview"                           # top-level README first
    assert "1. Mathematical Foundations" in chapters
    numbered = [c for c in chapters if c[0].isdigit()]
    assert numbered == sorted(numbered, key=lambda c: int(c.split(".")[0]))
    assert len(numbered) == 8
    # The math chapter's first file is the linear algebra primer.
    first_math = next(e for e in entries if e.path.parent.name == "01_mathematical_foundations")
    assert first_math.path.name.startswith("01_")


def test_scan_docs_missing_root_and_pretty_names(tmp_path):
    assert scan_docs(tmp_path / "nope") == []
    (tmp_path / "02_some_chapter").mkdir()
    (tmp_path / "02_some_chapter" / "03_the_thing_of_x.md").write_text("no heading\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Top Level\n", encoding="utf-8")
    entries = scan_docs(tmp_path)
    assert [(e.chapter, e.title) for e in entries] == [
        ("Overview", "Top Level"),
        ("2. Some Chapter", "The Thing of X"),
    ]


# ── ReferenceScreen ───────────────────────────────────────────────────────────

@pytest.fixture
def screen(qapp):
    s = ReferenceScreen()
    s.load_all()
    try:
        yield s
    finally:
        s.close()
        s.deleteLater()


def test_load_all_opens_mathematical_foundations(screen):
    assert len(screen.entries) == len(scan_docs())
    cur = screen.current_entry
    assert cur is not None
    assert cur.path.parent.name == "01_mathematical_foundations"
    assert cur.title in screen._doc_title.text()
    assert "01_mathematical_foundations" in screen._doc_path.text()
    assert len(screen._browser.toPlainText()) > 500
    assert screen._open_btn.isEnabled()
    chapters = [screen._chapter_filter.itemText(i) for i in range(screen._chapter_filter.count())]
    assert chapters[0] == "All chapters" and "Overview" in chapters
    assert len(chapters) == 1 + 1 + 8                            # all + overview + 8 rungs
    # Second load_all keeps the reader's place (no rescan).
    screen.select_entry(len(screen.entries) - 1)
    placed = screen.current_entry
    screen.load_all()
    assert screen.current_entry == placed


def test_select_entry_and_select_path(screen, tmp_path):
    other = next(i for i, e in enumerate(screen.entries)
                 if e.path.parent.name == "04_quantum_algorithms")
    screen.select_entry(other)
    assert screen.current_entry == screen.entries[other]
    assert screen.entries[other].title in screen._doc_title.text()
    assert screen._list.currentItem().data(USER_ROLE) == other

    assert screen.select_path(screen.entries[0].path) is True
    assert screen.current_entry == screen.entries[0]
    assert screen.select_path(tmp_path / "missing.md") is False
    assert screen.current_entry == screen.entries[0]
    screen.select_entry(-1)
    screen.select_entry(10_000)                                  # out of range: ignored
    assert screen.current_entry == screen.entries[0]


def test_chapter_and_title_filters(screen):
    other = next(i for i, e in enumerate(screen.entries)
                 if e.path.parent.name == "04_quantum_algorithms")
    screen.select_entry(other)
    chapter = screen.entries[other].chapter

    screen._chapter_filter.setCurrentText(chapter)
    rows = _data_rows(screen)
    assert rows and all(screen.entries[i].chapter == chapter for i in rows)
    assert screen._list.currentItem().data(USER_ROLE) == other   # stays highlighted

    screen._search.setText("zzzz-no-such-title")
    assert _data_rows(screen) == []
    screen._search.clear()
    screen._chapter_filter.setCurrentIndex(0)
    assert len(_data_rows(screen)) == len(screen.entries)

    needle = screen.entries[0].title.split()[0].lower()
    screen._search.setText(needle)
    rows = _data_rows(screen)
    assert 0 in rows
    assert all(needle in screen.entries[i].title.lower() or needle in screen.entries[i].path.name.lower()
               for i in rows)

    # Selecting an entry hidden by the filters clears them and opens it.
    screen._search.setText("zzzz")
    screen.select_entry(other)
    assert screen._search.text() == ""
    assert screen._chapter_filter.currentIndex() == 0
    assert screen.current_entry == screen.entries[other]


def test_relative_links_navigate_in_reader_and_bad_links_are_noops(screen, monkeypatch):
    opened = []
    monkeypatch.setattr(rs.QDesktopServices, "openUrl", lambda url: opened.append(url) or True)

    other = next(i for i, e in enumerate(screen.entries)
                 if e.path.parent.name == "04_quantum_algorithms")
    screen.select_entry(other)
    target = screen.entries[0].path
    rel = os.path.relpath(target, screen.entries[other].path.parent)
    screen._on_anchor_clicked(QUrl(rel))
    assert screen.current_entry == screen.entries[0]

    screen._on_anchor_clicked(QUrl("#summary"))                  # anchor only
    screen._on_anchor_clicked(QUrl("nope/does-not-exist.md"))    # dangling
    assert screen.current_entry == screen.entries[0]
    assert opened == []

    screen._on_anchor_clicked(QUrl("https://example.org/x"))
    assert [u.toString() for u in opened] == ["https://example.org/x"]
    screen._on_open_external()
    assert opened[-1].toLocalFile() == str(screen.entries[0].path)


def test_back_button_emits_back_requested(screen):
    fired = []
    screen.back_requested.connect(lambda: fired.append(True))
    screen._back_btn.click()
    assert fired == [True]


def test_missing_docs_root_shows_notice_without_raising(qapp, tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "_DOCS_ROOT", tmp_path / "no-docs-here")
    s = ReferenceScreen()
    try:
        s.load_all()
        assert s.entries == []
        assert s.current_entry is None
        assert s._doc_title.text() == "No documentation found"
        assert not s._open_btn.isEnabled()
        assert "No documentation found" in s._browser.toPlainText()
        assert str(tmp_path / "no-docs-here") in s._doc_path.text()
        s.select_entry(0)                                        # nothing to select: no raise
        assert s.select_path(tmp_path / "x.md") is False
        s._on_anchor_clicked(QUrl("../README.md"))               # no current doc: no raise
    finally:
        s.close()
        s.deleteLater()
