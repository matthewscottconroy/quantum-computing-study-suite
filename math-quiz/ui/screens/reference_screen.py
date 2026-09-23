"""math-quiz's Reference screen: the shared docs browser, pointed at rung 1.

The 497-line reader that used to live here was a cut-down fork of the same
design nine other apps carried.  It is now :class:`common.ui.reference.
ReferenceScreen`, which differs per app in exactly two things — the chapter it
opens on, and the topic→document map behind the "Jump to topic" picker.  Both
are constructor arguments, so this module is those two constants plus a
subclass that supplies them.

Choosing a subclass over constructing the shared screen inline in
``ui/main_window.py`` keeps ``from ui.screens.reference_screen import
ReferenceScreen`` working for the app and its tests, and keeps the map of
subjects to chapters beside the curriculum it belongs to.
"""

from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.reference import (  # noqa: F401  (re-exported for the app/tests)
    ALL_CHAPTERS, DocEntry, OVERVIEW_CHAPTER, ReferenceScreen as _SharedReference,
    docs_root, pretty_chapter, pretty_words, read_title, scan_docs,
)

#: Chapter directory this app opens by default — math is rung 1 of the ladder.
DEFAULT_CHAPTER = "01_mathematical_foundations"

#: Quiz subject -> the chapter file that covers it, for "Jump to topic".
#: Keys are the subjects in ``core/topics.py``; a subject with no obvious
#: chapter is simply left out and the picker does not offer it.
SUBJECT_DOCS: dict[str, str] = {
    "Linear Algebra":
        "01_mathematical_foundations/01_linear_algebra.md",
    "Complex Analysis":
        "01_mathematical_foundations/02_complex_numbers_and_hilbert_spaces.md",
    "Functional Analysis":
        "01_mathematical_foundations/02_complex_numbers_and_hilbert_spaces.md",
    "Quantum Connections":
        "01_mathematical_foundations/03_tensor_products_and_multipartite_systems.md",
    "Abstract Algebra":
        "01_mathematical_foundations/04_groups_and_abstract_algebra.md",
    "Representation Theory":
        "01_mathematical_foundations/05_representation_theory.md",
    "Probability Theory":
        "01_mathematical_foundations/06_probability_and_statistics.md",
    "Number Theory":
        "01_mathematical_foundations/07_number_theory_and_fourier_analysis.md",
    "Fourier Analysis":
        "01_mathematical_foundations/07_number_theory_and_fourier_analysis.md",
    "Calculus & Real Analysis":
        "01_mathematical_foundations/08_analysis_for_quantum_mechanics.md",
    "Ordinary Differential Equations":
        "01_mathematical_foundations/08_analysis_for_quantum_mechanics.md",
    "Partial Differential Equations":
        "01_mathematical_foundations/08_analysis_for_quantum_mechanics.md",
    "Topology & Geometry":
        "01_mathematical_foundations/09_topology_and_geometry.md",
}

__all__ = [
    "ReferenceScreen", "DEFAULT_CHAPTER", "SUBJECT_DOCS", "DocEntry",
    "ALL_CHAPTERS", "OVERVIEW_CHAPTER",
    "docs_root", "scan_docs", "read_title", "pretty_chapter", "pretty_words",
]


class ReferenceScreen(_SharedReference):
    """The shared docs reader, opened on the mathematical-foundations chapter."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent, default_chapter=DEFAULT_CHAPTER,
                         category_docs=SUBJECT_DOCS)

    def show_subject(self, subject: str) -> bool:
        """Open the chapter that covers a quiz subject.  False if there is none."""
        return self.show_category(subject)
