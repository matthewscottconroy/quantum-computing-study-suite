"""qec-trainer's Reference screen — :mod:`common.ui.reference`, parameterised.

This file used to be 992 lines.  vqa-trainer's copy was 992 lines too and
differed from it in exactly two constants: the chapter to open first, and the
problem-category -> doc map.  Those two constants are all that is left here;
the screen itself — docs discovery, the chapter filter, full-text search,
``$$`` math and ``<details>`` rewriting, cross-reference linkification, heading
anchors, dark-theme restyling and rescan-on-change — is the shared
:class:`common.ui.reference.ReferenceScreen`.

An app-local **subclass** rather than a bare call site, for two reasons: the
rest of the app constructs ``ReferenceScreen()`` with no arguments (so the two
constants stay a property of this app, not of its main window), and this app's
tests drive the module's helper functions by name.  The subclass adds no
behaviour — it only supplies the two arguments.

The module-level names the old file exported (``docs_root``, ``scan_docs``,
``prepare_markdown``, ``restyle_document``, ``heading_slug``, ``DocEntry``, …)
are re-exported below so importers and tests need not know where they moved.
The one rename: ``_DOCS_ROOT``, a module constant frozen at import, is now the
function :func:`docs_root`, resolved on each call and overridable with
``QUANTUM_STUDY_DOCS_DIR`` — which is how the tests point it at a temp corpus.
"""
from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui import reference as _reference
from common.ui.reference import (  # noqa: F401  (the module's public surface)
    ALL_CHAPTERS,
    DOCS_ENV_VAR,
    JUMP_PLACEHOLDER,
    OVERVIEW_CHAPTER,
    DocEntry,
    corpus_signature,
    docs_root,
    heading_slug,
    iter_docs,
    list_label,
    prepare_markdown,
    pretty_chapter,
    pretty_words,
    read_title,
    resolve_doc_ref,
    restyle_document,
    scan_docs,
    split_prefix,
    unique_doc_named,
)
from common.ui.reference import _FENCE, _INDEX_ROLE  # noqa: F401  (for the tests)

# ── App-specific: which rung of the ladder this trainer drills ───────────────
# Chapter directory opened first when the screen is shown.
_APP_CHAPTER_DIR = "05_quantum_error_correction"

# Problem category -> doc (relative to docs/) that best covers it.  Drives the
# "Jump to topic" picker and show_category(); missing files are skipped.
CATEGORY_DOC: dict[str, str] = {
    "Repetition Code":      "05_quantum_error_correction/03_repetition_code.md",
    "Stabilizer Formalism": "05_quantum_error_correction/04_stabilizer_formalism.md",
    "Steane Code":          "05_quantum_error_correction/05_css_codes_and_steane.md",
    "Surface Code":         "05_quantum_error_correction/06_surface_code.md",
    "Fault Tolerance":      "05_quantum_error_correction/07_fault_tolerance.md",
    "Bosonic Codes":        "05_quantum_error_correction/08_bosonic_codes.md",
    "Decoder Game":         "05_quantum_error_correction/06_surface_code.md",
}
# ── end app-specific ─────────────────────────────────────────────────────────


class ReferenceScreen(_reference.ReferenceScreen):
    """The shared Reference screen, opened on chapter 5 with the QEC topic map.

    Signals (inherited): ``back_requested``, ``doc_opened(str)``.
    """

    def __init__(self, parent=None, **kwargs) -> None:
        kwargs.setdefault("default_chapter", _APP_CHAPTER_DIR)
        kwargs.setdefault("category_docs", CATEGORY_DOC)
        super().__init__(parent, **kwargs)


__all__ = [
    "ReferenceScreen", "CATEGORY_DOC", "DocEntry",
    "ALL_CHAPTERS", "OVERVIEW_CHAPTER", "JUMP_PLACEHOLDER", "DOCS_ENV_VAR",
    "docs_root", "iter_docs", "corpus_signature", "scan_docs", "read_title",
    "split_prefix", "pretty_words", "pretty_chapter", "list_label",
    "resolve_doc_ref", "unique_doc_named", "prepare_markdown", "heading_slug",
    "restyle_document",
]
