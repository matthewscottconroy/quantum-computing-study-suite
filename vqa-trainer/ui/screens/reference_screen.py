"""Reference screen — this app's binding of the suite's in-app docs browser.

The screen itself (discovery, chapter filter, search, Markdown rendering,
``$$``/``<details>`` rewriting, GitHub-style heading anchors, cross-reference
linkification, external links) lives in :mod:`common.ui.reference`.  It was
992 lines here and 992 lines in qec-trainer, and the two differed in **exactly
two constants**: the chapter to open first, and the topic -> doc map.  Those
two constants are all that is left in this file; they are the screen's two
constructor arguments.

Everything the app and its tests used from the old module is re-exported
below, so nothing outside this file had to change.  The one name that could
not survive is the old ``_DOCS_ROOT`` module constant: the docs root is now
resolved at call time by :func:`common.ui.reference.docs_root`, which honours
``QUANTUM_STUDY_DOCS_DIR`` — set that to point the screen at another corpus.
"""
from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui import reference as _ref
from common.ui.reference import (  # noqa: F401  (re-exported for the app/tests)
    ALL_CHAPTERS, DOCS_ENV_VAR, DocEntry, JUMP_PLACEHOLDER, OVERVIEW_CHAPTER,
    corpus_signature, docs_root, heading_slug, iter_docs, list_label,
    prepare_markdown, pretty_chapter, pretty_words, read_title,
    resolve_doc_ref, restyle_document, scan_docs, split_prefix,
    unique_doc_named,
)
from common.ui.reference import _FENCE, _INDEX_ROLE, _MATH_LANG  # noqa: F401

# ── App-specific: which rung of the ladder this trainer drills ───────────────
# Chapter directory opened first when the screen is shown.
_APP_CHAPTER_DIR = "06_variational_quantum_algorithms"

# Problem category -> doc (relative to docs/) that best covers it.  Drives the
# "Jump to topic" picker and show_category(); missing files are skipped.
CATEGORY_DOC: dict[str, str] = {
    "VQE Fundamentals":   "06_variational_quantum_algorithms/01_vqe_fundamentals.md",
    "Ansatz Design":      "06_variational_quantum_algorithms/02_ansatz_design.md",
    "Parameter Shift":    "06_variational_quantum_algorithms/03_parameter_shift_gradient.md",
    "QAOA":               "06_variational_quantum_algorithms/04_qaoa.md",
    "Barren Plateaus":    "06_variational_quantum_algorithms/05_barren_plateaus.md",
    "Noise & Mitigation": "06_variational_quantum_algorithms/06_noise_and_error_mitigation.md",
    "Optimal Control":    "06_variational_quantum_algorithms/07_quantum_optimal_control.md",
}
# ── end app-specific ─────────────────────────────────────────────────────────


class ReferenceScreen(_ref.ReferenceScreen):
    """The shared Reference screen, opened on this trainer's own chapter.

    A subclass rather than a factory function so ``ReferenceScreen()`` still
    constructs the app's screen with no arguments — which is what
    ``ui/main_window.py`` and the app's test suite already do — while the
    caller can still pass the base class's keyword arguments (``docs_root=``
    in particular) when it needs to.
    """

    def __init__(self, parent=None, **kwargs) -> None:
        kwargs.setdefault("default_chapter", _APP_CHAPTER_DIR)
        kwargs.setdefault("category_docs", CATEGORY_DOC)
        super().__init__(parent, **kwargs)
