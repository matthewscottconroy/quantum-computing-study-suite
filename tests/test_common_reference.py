"""``common.ui.reference`` — docs discovery and Markdown preparation.

The screen itself is Qt; these tests cover the module-level functions it is
built from (which is why they are module-level), plus the docs-root resolution
that has to work from any app directory, plus one offscreen construction of the
widget so a syntax or signal error cannot hide behind "it is only UI".
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from common.ui import reference                     # noqa: E402

REAL_DOCS = ROOT / "docs"


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    """A small stand-in corpus, pointed at by the env override."""
    root = tmp_path / "docs"
    (root / "01_mathematical_foundations").mkdir(parents=True)
    (root / "05_quantum_error_correction").mkdir(parents=True)
    (root / "README.md").write_text("# The Corpus\n\nStart here.\n")
    (root / "01_mathematical_foundations" / "02_linear_algebra.md").write_text(
        "# Linear Algebra\n\nEigenvalues and the spectral theorem.\n")
    (root / "05_quantum_error_correction" / "06_surface_code.md").write_text(
        "# The Surface Code\n\nSee 01_mathematical_foundations/"
        "02_linear_algebra.md for the basis.\n")
    (root / ".hidden").mkdir()
    (root / ".hidden" / "draft.md").write_text("# Hidden\n")
    (root / "_private").mkdir()
    (root / "_private" / "notes.md").write_text("# Private\n")
    monkeypatch.setenv(reference.DOCS_ENV_VAR, str(root))
    return root


# ---------------------------------------------------------------------------
# Docs root resolution
# ---------------------------------------------------------------------------

def test_the_real_corpus_is_found_beside_the_package(monkeypatch):
    monkeypatch.delenv(reference.DOCS_ENV_VAR, raising=False)
    assert reference.docs_root() == REAL_DOCS
    assert reference.docs_root().is_dir()


def test_the_env_override_wins(corpus):
    assert reference.docs_root() == corpus


def test_a_blank_override_is_no_override(monkeypatch):
    monkeypatch.setenv(reference.DOCS_ENV_VAR, "   ")
    assert reference.docs_root() == REAL_DOCS


def test_resolution_works_from_inside_every_app_directory(monkeypatch):
    """Each app hard-coded ``parents[3] / "docs"``; this is the replacement,
    and it has to hold from all ten working directories."""
    monkeypatch.delenv(reference.DOCS_ENV_VAR, raising=False)
    apps = sorted(p.parent for p in ROOT.glob("*/main.py"))
    assert len(apps) == 10
    for app in apps:
        monkeypatch.chdir(app)
        assert reference.docs_root() == REAL_DOCS, f"not found from {app.name}"


def test_resolution_is_at_call_time(corpus, tmp_path, monkeypatch):
    other = tmp_path / "elsewhere"
    other.mkdir()
    (other / "x.md").write_text("# X\n")
    monkeypatch.setenv(reference.DOCS_ENV_VAR, str(other))
    assert reference.docs_root() == other


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def test_scan_docs_lists_the_corpus_in_ladder_order(corpus):
    entries = reference.scan_docs()
    assert [e.rel for e in entries] == [
        "README.md",
        "01_mathematical_foundations/02_linear_algebra.md",
        "05_quantum_error_correction/06_surface_code.md",
    ]
    assert entries[0].chapter == "" and entries[0].chapter_label == "Overview"
    assert entries[1].chapter_label == "1. Mathematical Foundations"
    assert entries[2].title == "The Surface Code"
    assert entries[2].label == "5.6  The Surface Code"


def test_hidden_and_underscore_directories_are_skipped(corpus):
    rels = {e.rel for e in reference.scan_docs()}
    assert not any(r.startswith((".", "_")) for r in rels)
    assert len(rels) == 3


def test_scan_docs_on_the_real_corpus():
    entries = reference.scan_docs(REAL_DOCS)
    assert len(entries) == len(list(REAL_DOCS.rglob("*.md")))
    assert len(entries) >= 60
    assert all(e.title for e in entries), "every chapter needs an H1"
    assert all(e.path.is_file() for e in entries)


def test_a_missing_corpus_scans_as_empty(tmp_path):
    assert reference.scan_docs(tmp_path / "nope") == []
    assert reference.corpus_signature(tmp_path / "nope") == ()


def test_corpus_signature_changes_when_a_file_changes(corpus):
    first = reference.corpus_signature(corpus)
    (corpus / "README.md").write_text("# The Corpus\n\nEdited.\n")
    assert reference.corpus_signature(corpus) != first
    (corpus / "07_new.md").write_text("# New\n")
    assert len(reference.corpus_signature(corpus)) == len(first) + 1


def test_doc_entry_text_and_haystack_are_cached(corpus):
    entry = reference.scan_docs()[0]
    assert "Start here" in entry.text()
    (corpus / "README.md").write_text("# Changed\n")
    assert "Start here" in entry.text(), "the body should be cached"
    assert "start here" in entry.haystack()


def test_an_unreadable_file_renders_its_error_inline(corpus):
    entry = reference.scan_docs()[0]
    entry.path = corpus / "gone.md"
    entry._text = None
    assert "Could not read" in entry.text()


def test_read_title_falls_back_to_the_stem(tmp_path):
    p = tmp_path / "03_quantum_gates_and_circuits.md"
    p.write_text("no heading here\n")
    assert reference.read_title(p) == ""
    assert reference.pretty_words(p.stem) == "Quantum Gates and Circuits"


@pytest.mark.parametrize("stem,want", [
    ("01_mathematical_foundations", "Mathematical Foundations"),
    ("06_noise_and_error_mitigation", "Noise and Error Mitigation"),
    ("plain_name", "Plain Name"),
    ("", ""),
])
def test_pretty_words(stem, want):
    assert reference.pretty_words(stem) == want


def test_pretty_chapter_and_list_label():
    assert reference.pretty_chapter("") == "Overview"
    assert reference.pretty_chapter("05_quantum_error_correction") == \
        "5. Quantum Error Correction"
    assert reference.list_label("05_x", "06_y", "T") == "5.6  T"
    assert reference.list_label("", "06_y", "T") == "6  T"
    assert reference.list_label("", "readme", "T") == "T"


# ---------------------------------------------------------------------------
# Markdown preparation
# ---------------------------------------------------------------------------

def test_display_math_becomes_a_tagged_fence():
    out = reference.prepare_markdown("Before\n\n$$E = mc^2$$\n\nAfter")
    assert "```math\nE = mc^2\n```" in out
    assert "$$" not in out


def test_display_math_inside_a_block_quote_keeps_the_quote():
    out = reference.prepare_markdown("> a note\n>\n> $$x = 1$$\n")
    for line in out.splitlines():
        if "x = 1" in line or "```math" in line:
            assert line.startswith(">"), f"quote broken at: {line!r}"


def test_details_blocks_become_a_lead_in():
    md = "<details><summary>Solution</summary>\n\nThe answer.\n</details>"
    shown = reference.prepare_markdown(md)
    assert "**▸ Solution**" in shown and "The answer." in shown
    assert "<details>" not in shown


def test_solutions_can_be_hidden():
    md = "<details><summary>Solution</summary>\n\nThe answer.\n</details>"
    hidden = reference.prepare_markdown(md, show_solutions=False)
    assert "The answer." not in hidden
    assert "hidden" in hidden and "Show solutions" in hidden


def test_a_solution_containing_a_code_fence_is_still_hidden():
    md = ("<details><summary>Solution</summary>\n\n```python\n"
          "print('the answer')\n```\n</details>")
    hidden = reference.prepare_markdown(md, show_solutions=False)
    assert "the answer" not in hidden


def test_fenced_code_is_left_completely_alone():
    md = "```python\n# $$not math$$ and <details> too\nx = 1\n```\n"
    assert reference.prepare_markdown(md) == md


def test_cross_references_become_links(corpus):
    doc_dir = corpus / "05_quantum_error_correction"
    out = reference.prepare_markdown(
        "See 01_mathematical_foundations/02_linear_algebra.md for the basis.",
        doc_dir, root=corpus)
    assert "](../01_mathematical_foundations/02_linear_algebra.md)" in out


def test_an_unresolvable_reference_is_left_as_written(corpus):
    text = "See 99_nothing/00_here.md for more."
    out = reference.prepare_markdown(text, corpus, root=corpus)
    assert out == text


def test_resolve_doc_ref_forms(corpus):
    here = corpus / "05_quantum_error_correction"
    target = "01_mathematical_foundations/02_linear_algebra.md"
    assert reference.resolve_doc_ref(target, here, corpus) == f"../{target}"
    assert reference.resolve_doc_ref(f"docs/{target}", here, corpus) == f"../{target}"
    assert reference.resolve_doc_ref("02_linear_algebra.md", here, corpus) == \
        f"../{target}", "a bare name resolves to the one file of that name"
    assert reference.resolve_doc_ref("06_surface_code.md", here, corpus) == \
        "06_surface_code.md", "a sibling wins over the corpus-wide search"
    assert reference.resolve_doc_ref("nope.md", here, corpus) is None


def test_a_fragment_survives_resolution(corpus):
    here = corpus / "05_quantum_error_correction"
    out = reference.resolve_doc_ref(
        "01_mathematical_foundations/02_linear_algebra.md#eigenvalues",
        here, corpus)
    assert out.endswith("02_linear_algebra.md#eigenvalues")


def test_an_existing_markdown_link_is_not_double_wrapped(corpus):
    text = "[the basis](01_mathematical_foundations/02_linear_algebra.md)"
    out = reference.prepare_markdown(text, corpus, root=corpus)
    assert out == text


@pytest.mark.parametrize("heading,slug", [
    ("Key Formulas", "key-formulas"),
    ("QFT ≠ Classical FFT", "qft--classical-fft"),
    ("  Spaced  Out  ", "spaced--out"),
    ("Chapter 5: Codes!", "chapter-5-codes"),
])
def test_heading_slug_matches_github(heading, slug):
    assert reference.heading_slug(heading) == slug


def _outside_code(text: str) -> str:
    """*text* with fenced blocks and inline code spans removed.

    Those are deliberately left untouched by ``prepare_markdown`` — the corpus
    README documents its own conventions with a literal ``$$ … $$`` inside
    backticks — so the "everything was converted" assertions must ignore them.
    """
    kept = [seg for i, seg in enumerate(reference._FENCE.split(text)) if not i % 2]
    return reference._CODE_SPAN.sub("", "".join(kept))


def test_the_real_corpus_survives_preparation():
    """All 71 chapters through the rewriter: no exception, nothing left over."""
    entries = reference.scan_docs(REAL_DOCS)
    assert entries, "the real corpus is missing"
    for entry in entries:
        out = reference.prepare_markdown(entry.text(), entry.path.parent,
                                         root=REAL_DOCS)
        prose = _outside_code(out)
        assert "$$" not in prose, f"unconverted display math in {entry.rel}"
        assert "<details>" not in prose, f"unconverted details in {entry.rel}"
        assert "</details>" not in prose, f"stray close tag in {entry.rel}"
        assert out.strip(), f"{entry.rel} prepared to nothing"


def test_hiding_solutions_across_the_real_corpus():
    """Every ``<details>`` body in the corpus really does disappear."""
    hid_something = False
    for entry in reference.scan_docs(REAL_DOCS):
        raw = entry.text()
        if "<details>" not in raw:
            continue
        hid_something = True
        out = reference.prepare_markdown(raw, entry.path.parent,
                                         show_solutions=False, root=REAL_DOCS)
        assert "<details>" not in _outside_code(out), entry.rel
        assert "Show solutions" in out, entry.rel
    assert hid_something, "no chapter uses <details> — has the corpus changed?"


# ---------------------------------------------------------------------------
# The widget itself (offscreen)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_the_screen_builds_and_loads_the_corpus(qapp, corpus):
    screen = reference.ReferenceScreen(
        default_chapter="05_quantum_error_correction",
        category_docs={"Surface Code":
                       "05_quantum_error_correction/06_surface_code.md"},
    )
    screen.load_all()
    assert screen.docs_root() == corpus
    assert len(screen.entries) == 3
    assert screen.current_entry is not None
    assert screen.current_entry.rel == \
        "05_quantum_error_correction/06_surface_code.md", \
        "the app's own chapter should open first"
    assert "The Surface Code" in screen.visible_titles()
    screen.deleteLater()


def test_the_jump_picker_appears_only_with_a_mapping(qapp, corpus):
    plain = reference.ReferenceScreen()
    plain.load_all()
    assert plain._jump.isVisible() is False
    assert plain.show_category("anything") is False
    assert plain.current_entry.rel == "README.md", "no default chapter: first doc"
    plain.deleteLater()

    mapped = reference.ReferenceScreen(
        category_docs={"Surface Code":
                       "05_quantum_error_correction/06_surface_code.md",
                       "Not In The Corpus": "99_nope/00_none.md"})
    mapped.load_all()
    assert mapped._jump.count() == 2, "a category with no file must be skipped"
    assert mapped.show_category("Surface Code") is True
    assert mapped.show_category("Not In The Corpus") is False
    mapped.deleteLater()


def test_open_doc_and_search(qapp, corpus):
    screen = reference.ReferenceScreen()
    screen.load_all()
    assert screen.open_doc("01_mathematical_foundations/02_linear_algebra.md")
    assert screen.current_entry.title == "Linear Algebra"
    assert screen.open_doc("./01_mathematical_foundations/02_linear_algebra.md")
    assert screen.open_doc("nope/none.md") is False

    screen.set_search("spectral")
    assert screen.visible_titles() == ["Linear Algebra"]
    screen.set_search("")
    assert len(screen.visible_titles()) == 3
    screen.deleteLater()


def test_a_missing_corpus_shows_a_useful_message(qapp, tmp_path, monkeypatch):
    monkeypatch.setenv(reference.DOCS_ENV_VAR, str(tmp_path / "nope"))
    screen = reference.ReferenceScreen()
    screen.load_all()
    assert screen.entries == [] and screen.current_entry is None
    assert reference.DOCS_ENV_VAR in screen._browser.toMarkdown()
    screen.deleteLater()


def test_the_screen_rescans_when_the_corpus_changes(qapp, corpus):
    screen = reference.ReferenceScreen()
    screen.load_all()
    assert len(screen.entries) == 3
    (corpus / "08_new_chapter.md").write_text("# Brand New\n")
    screen.load_all()                       # notices via corpus_signature
    assert len(screen.entries) == 4
    assert "Brand New" in [e.title for e in screen.entries]
    screen.deleteLater()


def test_the_screen_renders_the_real_corpus(qapp, monkeypatch):
    monkeypatch.delenv(reference.DOCS_ENV_VAR, raising=False)
    screen = reference.ReferenceScreen(default_chapter="05_quantum_error_correction")
    screen.load_all()
    assert len(screen.entries) >= 60
    assert screen.current_entry.chapter == "05_quantum_error_correction"
    assert screen._browser.toPlainText().strip()
    screen.deleteLater()
