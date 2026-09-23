"""Reference screen — this app's binding of the shared docs browser.

The browser itself (discovery, chapter filter, full-text search, the Markdown
rewrites for ``$$…$$`` and ``<details>``, cross-reference linkification,
heading anchors, dark-theme restyling, external links) is
:class:`common.ui.reference.ReferenceScreen`; ten near-identical copies of it
used to live one per app, and each had missed a different fix.

What is genuinely this app's own is the *subject* vocabulary: quantum-quiz
generates questions per curriculum subject, so it can deep-link a subject to
the chapter that covers it.  That map, and the one-line
:meth:`ReferenceScreen.show_subject` built on it, are all that is left here.

The module-level helpers the shared screen exposes are re-exported below so
callers (and the tests) have one import site.
"""

from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui import reference as _reference
from common.ui.reference import (  # noqa: F401  (re-exported for callers/tests)
    ALL_CHAPTERS,
    DOCS_ENV_VAR,
    DocEntry,
    OVERVIEW_CHAPTER,
    docs_root,
    heading_slug,
    list_label,
    prepare_markdown,
    pretty_chapter,
    pretty_words,
    read_title,
    resolve_doc_ref,
    restyle_document,
    scan_docs,
)

#: Quiz subject -> docs chapter directory that best covers it.  Used by
#: :meth:`ReferenceScreen.show_subject` so callers can deep-link; an unknown
#: subject shows everything.  Every subject in ``core.topics.TOPICS`` must have
#: an entry (asserted in tests/test_reference_screen.py).
SUBJECT_CHAPTER: dict[str, str] = {
    "Linear Algebra":                   "01_mathematical_foundations",
    "Abstract Algebra":                 "01_mathematical_foundations",
    "Representation Theory":            "01_mathematical_foundations",
    "Quantum Mechanics":                "02_quantum_mechanics",
    "Foundations of Quantum Mechanics": "02_quantum_mechanics",
    "Quantum Computing":                "03_quantum_gates_and_circuits",
    "Qiskit":                           "03_quantum_gates_and_circuits",
    "QASM":                             "03_quantum_gates_and_circuits",
    "Transpiling":                      "03_quantum_gates_and_circuits",
    "Quantum Algorithm Design":         "04_quantum_algorithms",
    "Qiskit Certification (C1000-179)": "08_advanced_topics",
}


class ReferenceScreen(_reference.ReferenceScreen):
    """The shared docs browser, plus this app's subject deep-link.

    No ``default_chapter``: a quiz ranges over the whole curriculum, so the
    browser opens on the corpus README rather than on one chapter.  No
    ``category_docs`` either — this app's categories are broad subjects that
    map to a *chapter*, not to a single document, so the "Jump to topic"
    picker (which opens one named file) would be misleading; it hides itself.
    """

    def show_subject(self, subject: str) -> None:
        """Filter the list to the chapter that covers *subject*."""
        self.show_chapter(SUBJECT_CHAPTER.get(subject, ""))
