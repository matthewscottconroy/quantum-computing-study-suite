"""Reference screen — in-app browser for the suite's docs/ corpus.

The screen itself is :class:`common.ui.reference.ReferenceScreen`: one
implementation for all ten apps (docs discovery, the chapter filter, the
full-text search, Markdown preparation, cross-reference resolution, external
links).  The 439-line fork that used to live here is gone.

What is left is this app's vocabulary and the four verbs the rest of the app
calls, which the shared screen has no reason to know about:

* ``TOPIC_CHAPTER``/``DERIVATION_CHAPTER`` — which docs chapter backs a problem
  topic or a guided derivation;
* ``select_topic`` / ``select_derivation`` / ``select_chapter`` / ``show_all``
  / ``current_chapter`` / ``current_doc`` — the app's jump-and-reset API,
  expressed in terms of the shared screen's public ``load_all`` /
  ``show_chapter`` / ``set_search`` / ``current_doc_path``.

This app maps a topic to a whole **chapter**, not to one document, so no
``category_docs`` mapping is passed and the shared screen's "Jump to topic"
picker stays hidden — the chapter filter is this app's jump control, exactly
as before.
"""
from __future__ import annotations

from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.reference import (  # noqa: F401  (re-exported for callers/tests)
    ALL_CHAPTERS, DOCS_ENV_VAR, OVERVIEW_CHAPTER, DocEntry, docs_root,
    pretty_chapter, prepare_markdown, read_title, scan_docs,
)
from common.ui.reference import ReferenceScreen as _SharedReferenceScreen

# Problem topic -> docs chapter directory (used to preselect the chapter filter).
TOPIC_CHAPTER: dict[str, str] = {
    "Linear Algebra & QM Math": "01_mathematical_foundations",
    "Circuits & Gates":         "03_quantum_gates_and_circuits",
    "Algorithms":               "04_quantum_algorithms",
    "Error Correction":         "05_quantum_error_correction",
    "VQA":                      "06_variational_quantum_algorithms",
    "Information Theory":       "08_advanced_topics",
}

# Derivation id -> docs chapter directory.
DERIVATION_CHAPTER: dict[str, str] = {
    "deriv_qpe":           "04_quantum_algorithms",
    "deriv_grover_count":  "04_quantum_algorithms",
    "deriv_chsh":          "02_quantum_mechanics",
    "deriv_no_cloning":    "02_quantum_mechanics",
    "deriv_teleportation": "03_quantum_gates_and_circuits",
    "deriv_param_shift":   "06_variational_quantum_algorithms",
    "deriv_threshold":     "05_quantum_error_correction",
}


class ReferenceScreen(_SharedReferenceScreen):
    """The shared Reference screen with this app's chapter-jump verbs."""

    def __init__(self, parent=None, **kwargs) -> None:
        kwargs.setdefault("title", "Reference")
        super().__init__(parent, **kwargs)

    # -- the app's jump API ------------------------------------------------

    def current_chapter(self) -> str:
        """The selected chapter directory key, or :data:`ALL_CHAPTERS`.

        The shared screen models "no chapter filter" as the empty string; this
        app has always spelled it :data:`ALL_CHAPTERS`, and the setup/problem
        screens and their tests read it that way.
        """
        return self._chapter_filter.currentData() or ALL_CHAPTERS

    def current_doc(self) -> Path | None:
        """Path of the document on screen (the shared name is
        ``current_doc_path``)."""
        return self.current_doc_path()

    def select_chapter(self, chapter: str) -> bool:
        """Filter to a chapter directory key (e.g. '04_quantum_algorithms').

        Programmatic jumps always show the whole chapter, so any search text
        left from an earlier visit is cleared first.  False (and an unfiltered
        list) when there is no such chapter.
        """
        self.load_all()
        self.set_search("")
        self.show_chapter(chapter)
        return self.current_chapter() == chapter

    def select_topic(self, topic: str) -> bool:
        """Jump to the chapter that backs a problem topic (falls back to all)."""
        return self._jump_to(TOPIC_CHAPTER.get(topic))

    def select_derivation(self, derivation_id: str) -> bool:
        """Jump to the chapter that backs a guided derivation (falls back to all)."""
        return self._jump_to(DERIVATION_CHAPTER.get(derivation_id))

    def show_all(self) -> None:
        """Reset to the unfiltered view: every chapter, no search text.

        Used when Reference is opened from Setup so a chapter jump made earlier
        from a problem or derivation does not leak into the browse view.  The
        open document is kept.
        """
        self.load_all()
        self.set_search("")
        self.show_chapter("")

    # -- internals ---------------------------------------------------------

    def _jump_to(self, chapter: str | None) -> bool:
        if chapter and self.select_chapter(chapter):
            return True
        self.show_all()
        return False
