"""Reference screen — this app's use of the shared ``common.ui.reference``.

The ~700-line copy that used to live in ``ui/screens/reference_screen.py`` is
gone; the screen is now :class:`common.ui.reference.ReferenceScreen`, whose
internals (docs discovery, Markdown preparation, cross-reference resolution,
``<details>`` handling, slugs) are unit-tested once in the root suite's
``tests/test_common_reference.py``.

What is still this app's business, and is tested here: that the app ships the
shared screen, with the defaults it wants (the whole corpus, opened on its
README, no "Jump to topic" picker because this app has no topic map), that the
window wires it up, and that reading and navigating still work end to end.
"""
from __future__ import annotations

import re

import pytest
from PyQt6.QtCore import QUrl

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui import reference as ref

DOCS = ref.docs_root()
pytestmark = pytest.mark.skipif(not DOCS.is_dir(), reason="docs corpus not present")


def test_the_app_uses_the_shared_screen_and_finds_the_repo_corpus():
    import ui.main_window as main_window

    assert main_window.ReferenceScreen is ref.ReferenceScreen
    # The corpus is the repository's docs/, found from the package rather than
    # from a hard-coded "parents[3]" inside this app.
    assert DOCS.name == "docs"
    assert (DOCS / "README.md").is_file()
    assert len(ref.scan_docs()) >= 50


@pytest.fixture
def screen(qapp):
    s = ref.ReferenceScreen()
    s.resize(1000, 700)
    s.show()
    s.load_all()
    qapp.processEvents()
    yield s
    s.close()
    s.deleteLater()
    qapp.processEvents()


def test_it_opens_on_the_corpus_readme_with_no_topic_picker(qapp, screen):
    assert screen.current_entry is not None
    assert screen.current_entry.path.name.lower() == "readme.md"
    assert screen.category_docs == {}
    assert screen._jump.isHidden()          # no topic map: the control hides
    assert screen.docs_root() == DOCS


def test_navigation_and_cross_references(qapp, screen):
    assert screen.open_doc("02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md")
    assert screen.current_entry.rel == "02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md"

    # Bare cross-references in the rendered document are real anchors.
    hrefs = re.findall(r'href="([^"]+)"', screen._browser.toHtml())
    doc_links = [h for h in hrefs if ".md" in h and not h.startswith("http")]
    assert doc_links, "expected linkified cross-references"

    opened: list[str] = []
    screen.doc_opened.connect(opened.append)
    screen._on_anchor_clicked(
        QUrl("../01_mathematical_foundations/01_linear_algebra.md#key-formulas"))
    qapp.processEvents()
    assert screen.current_entry.rel == "01_mathematical_foundations/01_linear_algebra.md"
    assert opened == ["01_mathematical_foundations/01_linear_algebra.md"]

    # Unknown target: stays put, no exception.
    screen._on_anchor_clicked(QUrl("nope/missing.md"))
    qapp.processEvents()
    assert screen.current_entry.rel == "01_mathematical_foundations/01_linear_algebra.md"
    assert not screen.open_doc("nope/missing.md")


def test_filters_and_the_solutions_toggle(qapp, screen):
    total = len(screen.visible_titles())
    assert total == len(screen.entries)

    screen.show_chapter("02_quantum_mechanics")
    qapp.processEvents()
    listed = screen.visible_titles()
    assert 0 < len(listed) < total
    screen.show_chapter("")
    qapp.processEvents()
    assert len(screen.visible_titles()) == total

    screen.set_search("Toffoli")
    qapp.processEvents()
    hits = screen.visible_titles()
    assert 0 < len(hits) < total
    assert "Toffoli" in screen.current_entry.text()
    screen.set_search("")
    qapp.processEvents()

    assert screen.open_doc("01_mathematical_foundations/01_linear_algebra.md")
    screen._solutions_cb.setChecked(True)
    qapp.processEvents()
    with_solutions = screen._browser.toPlainText()
    screen._solutions_cb.setChecked(False)
    qapp.processEvents()
    without = screen._browser.toPlainText()
    assert "hidden" in without and len(without) < len(with_solutions)


def test_the_window_shows_it_and_takes_the_back_signal(qapp):
    from ui.main_window import MainWindow, PAGE_REFERENCE, PAGE_SETUP

    win = MainWindow()
    try:
        win.show()
        qapp.processEvents()
        assert isinstance(win._reference, ref.ReferenceScreen)
        win._on_reference()
        qapp.processEvents()
        assert win._stack.currentIndex() == PAGE_REFERENCE
        assert win._reference.current_entry is not None
        win._reference.back_requested.emit()
        qapp.processEvents()
        assert win._stack.currentIndex() == PAGE_SETUP
    finally:
        win.close()
        win.deleteLater()
        qapp.processEvents()
