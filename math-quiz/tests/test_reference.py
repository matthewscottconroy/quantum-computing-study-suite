"""Reference screen: docs discovery, the default chapter, subject jumps,
filters, in-reader links, Back, and the missing-docs fallback.

The 497-line reader that used to live in ``ui/screens/reference_screen.py`` is
now :class:`common.ui.reference.ReferenceScreen`; what this app still owns is
the two constructor arguments (``DEFAULT_CHAPTER`` and ``SUBJECT_DOCS``), so
that is what is pinned hardest here.  The shared reader's own behaviour is
covered by ``tests/test_common_reference.py`` in the root suite.
"""
from __future__ import annotations

import os
import pathlib

import pytest
from PyQt6.QtCore import QUrl, Qt

import common_path  # noqa: F401  (puts the repo root on sys.path)

import common.ui.reference as refmod
from core.topics import TOPICS
from ui.screens.reference_screen import (
    DEFAULT_CHAPTER, SUBJECT_DOCS, ReferenceScreen, docs_root, scan_docs,
)

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_DOCS = APP_ROOT.parent / "docs"
INDEX_ROLE = Qt.ItemDataRole.UserRole


def _chapter_dirs_on_disk() -> list[str]:
    """Top-level docs/ directories holding Markdown, as scan_docs groups them.

    Derived rather than hard-coded: the shared corpus gains chapters over time
    (a 12th rung would otherwise "break" a reader that is working perfectly).
    """
    return sorted({p.relative_to(REPO_DOCS).parts[0]
                   for p in REPO_DOCS.rglob("*.md")
                   if len(p.relative_to(REPO_DOCS).parts) > 1})


def _data_rows(screen: ReferenceScreen) -> list[int]:
    """Entry indices currently listed (header rows carry no index data)."""
    rows = []
    for i in range(screen._list.count()):
        data = screen._list.item(i).data(INDEX_ROLE)
        if data is not None:
            rows.append(int(data))
    return rows


# ── The app's two constants ───────────────────────────────────────────────────

def test_default_chapter_and_subject_docs_point_at_files_that_exist():
    assert (REPO_DOCS / DEFAULT_CHAPTER).is_dir()
    known = {e.rel for e in scan_docs()}
    assert SUBJECT_DOCS, "the jump-to-topic map must not be empty"
    for subject, rel in SUBJECT_DOCS.items():
        assert rel in known, f"{subject} -> missing doc {rel}"
        assert rel.startswith(DEFAULT_CHAPTER + "/"), subject
    # Every subject the quiz can generate is reachable from the picker.
    assert set(SUBJECT_DOCS) == set(TOPICS)


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
    assert all(e.path.suffix == ".md" and e.path.is_relative_to(REPO_DOCS.resolve())
               for e in entries)
    assert all(e.title.strip() for e in entries)
    chapters = []
    for e in entries:
        if e.chapter_label not in chapters:
            chapters.append(e.chapter_label)
    assert chapters[0] == "Overview"                           # top-level README first
    assert "1. Mathematical Foundations" in chapters
    numbered = [c for c in chapters if c[0].isdigit()]
    assert numbered == sorted(numbered, key=lambda c: int(c.split(".")[0]))
    numbered_dirs = [d for d in _chapter_dirs_on_disk() if d[:1].isdigit()]
    assert len(numbered) == len(numbered_dirs) >= 8      # one entry per rung on disk
    # The math chapter's first file is the linear algebra primer.
    first_math = next(e for e in entries if e.chapter == DEFAULT_CHAPTER)
    assert first_math.path.name.startswith("01_")


def test_scan_docs_missing_root_and_pretty_names(tmp_path):
    assert scan_docs(tmp_path / "nope") == []
    (tmp_path / "02_some_chapter").mkdir()
    (tmp_path / "02_some_chapter" / "03_the_thing_of_x.md").write_text(
        "no heading\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Top Level\n", encoding="utf-8")
    entries = scan_docs(tmp_path)
    assert [(e.chapter_label, e.title) for e in entries] == [
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
    assert cur.chapter == DEFAULT_CHAPTER
    assert cur.title in screen._doc_title.text()
    assert DEFAULT_CHAPTER in screen._doc_path.text()
    assert len(screen._browser.toPlainText()) > 500
    assert screen._open_btn.isEnabled()
    chapters = [screen._chapter_filter.itemText(i)
                for i in range(screen._chapter_filter.count())]
    assert chapters[0] == "All chapters" and "Overview" in chapters
    # all + overview + one per chapter directory (the corpus grows; see helper)
    assert len(chapters) == 1 + 1 + len(_chapter_dirs_on_disk())
    # Second load_all keeps the reader's place (no rescan of an unchanged tree).
    assert screen.open_doc(screen.entries[-1].rel) is True
    placed = screen.current_entry
    screen.load_all()
    assert screen.current_entry == placed


def test_open_doc_and_the_subject_jump_picker(screen):
    target = SUBJECT_DOCS["Number Theory"]
    opened: list[str] = []
    screen.doc_opened.connect(opened.append)

    assert screen.open_doc(target) is True
    assert screen.current_entry.rel == target
    assert screen.current_doc_path() == (REPO_DOCS / target).resolve()
    assert opened[-1] == target

    assert screen.open_doc("nope/does-not-exist.md") is False
    assert screen.current_entry.rel == target

    # The picker is visible because this app supplies a category map, and it
    # offers one entry per distinct document (Number Theory and Fourier
    # Analysis share a chapter file, so both are listed).
    assert screen._jump.isVisible() or screen._jump.count() > 1
    labels = [screen._jump.itemText(i) for i in range(1, screen._jump.count())]
    assert set(labels) == set(SUBJECT_DOCS)

    assert screen.show_category("Topology & Geometry") is True
    assert screen.current_entry.rel == SUBJECT_DOCS["Topology & Geometry"]
    assert screen.show_subject("Linear Algebra") is True
    assert screen.current_entry.rel == SUBJECT_DOCS["Linear Algebra"]
    assert screen.show_subject("No Such Subject") is False


def test_chapter_and_title_filters(screen):
    other = "04_quantum_algorithms"
    target = next(e for e in screen.entries if e.chapter == other)
    screen.open_doc(target.rel)

    screen.show_chapter(other)
    rows = _data_rows(screen)
    assert rows and all(screen.entries[i].chapter == other for i in rows)
    assert screen._list.currentItem().data(INDEX_ROLE) == screen.entries.index(target)

    screen.set_search("zzzz-no-such-title")
    assert _data_rows(screen) == []
    assert screen.visible_titles() == []
    screen.set_search("")
    screen.show_chapter("")
    assert len(_data_rows(screen)) == len(screen.entries)

    needle = screen.entries[0].title.split()[0].lower()
    screen.set_search(needle)
    rows = _data_rows(screen)
    assert rows
    assert all(needle in screen.entries[i].title.lower()
               or needle in screen.entries[i].rel.lower()
               or needle in screen.entries[i].haystack()
               for i in rows)
    screen.set_search("")

    # Opening a document the filters would hide clears them and shows it.
    screen.set_search("zzzz")
    assert screen.open_doc(target.rel) is True
    assert screen._search.text() == ""
    assert screen._chapter_filter.currentIndex() == 0
    assert screen.current_entry == target


def test_relative_links_navigate_in_reader_and_bad_links_are_noops(screen, monkeypatch):
    opened = []
    monkeypatch.setattr(refmod.QDesktopServices, "openUrl",
                        lambda url: opened.append(url) or True)

    start = next(e for e in screen.entries if e.chapter == "04_quantum_algorithms")
    screen.open_doc(start.rel)
    first = screen.entries[0]
    rel = os.path.relpath(first.path, start.path.parent)
    screen._on_anchor_clicked(QUrl(rel))
    assert screen.current_entry == first

    screen._on_anchor_clicked(QUrl("#summary"))                  # anchor only
    screen._on_anchor_clicked(QUrl("nope/does-not-exist.md"))    # dangling
    assert screen.current_entry == first
    assert opened == []

    screen._on_anchor_clicked(QUrl("https://example.org/x"))
    assert [u.toString() for u in opened] == ["https://example.org/x"]
    screen._open_externally()
    assert opened[-1].toLocalFile() == str(first.path)


def test_back_button_emits_back_requested(screen):
    fired = []
    screen.back_requested.connect(lambda: fired.append(True))
    screen._back_btn.click()
    assert fired == [True]


def test_missing_docs_root_shows_notice_without_raising(qapp, tmp_path, monkeypatch):
    monkeypatch.setenv(refmod.DOCS_ENV_VAR, str(tmp_path / "no-docs-here"))
    s = ReferenceScreen()
    try:
        s.load_all()
        assert s.entries == []
        assert s.current_entry is None
        assert s.current_doc_path() is None
        assert s._doc_title.text() == "No documentation found"
        assert not s._open_btn.isEnabled()
        assert "No documentation found" in s._browser.toPlainText()
        assert str(tmp_path / "no-docs-here") in s._doc_path.text()
        assert s.open_doc("anything.md") is False                # nothing to open
        assert s.show_category("Linear Algebra") is False
        s._on_anchor_clicked(QUrl("../README.md"))               # no current doc
    finally:
        s.close()
        s.deleteLater()
