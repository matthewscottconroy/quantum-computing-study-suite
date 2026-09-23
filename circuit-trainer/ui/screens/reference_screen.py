"""Reference screen for circuit-trainer — a thin skin on the shared browser.

The 350-line fork that used to live here (itself a port of qec-trainer's) is
gone: the docs browser is :class:`common.ui.reference.ReferenceScreen`, and the
only things that were ever circuit-trainer's are the two constructor arguments
it takes — the chapter to open on, and the map from a trainer category to the
chapter that covers it.

Why a subclass rather than plain construction: this app's ``MainWindow``, its
sprint/problem flows and its tests speak in :class:`pathlib.Path` objects and
call ``show_doc()`` / ``current_doc()`` / ``chapter_count()``.  The shared
screen speaks in docs-relative strings (``open_doc("03_.../01_....md")``),
which is the better API — a path is not portable between a checkout and an
installed wheel.  Rather than fork the screen to keep three method names, the
four-line adapter below translates, so the behaviour is the shared one and the
app keeps its vocabulary.

Everything the shared screen adds comes with it: a search box over titles *and*
body text, a chapter filter, "hide solutions" for self-testing, ``$$``/
``<details>`` rewriting, cross-document link resolution and a rescan when the
corpus changes on disk while the app is open.
"""
from __future__ import annotations

from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.reference import (        # noqa: F401  (re-exported for callers)
    DocEntry, ReferenceScreen as _SharedReferenceScreen, docs_root, scan_docs,
)

#: The chapter Circuit Trainer opens on: gates and circuits, its own rung of
#: the ladder.
DEFAULT_CHAPTER = "03_quantum_gates_and_circuits"

#: Maps each trainer category (``ProblemCategory.value``) to the docs chapter
#: that best covers it, as a path relative to the docs root.  The shared screen
#: offers only the entries whose file actually exists, so a renamed chapter
#: quietly drops out of the picker instead of raising.
CATEGORY_DOCS: dict[str, str] = {
    "Single-gate output":           "03_quantum_gates_and_circuits/01_single_qubit_gates.md",
    "Gate sequence":                "03_quantum_gates_and_circuits/01_single_qubit_gates.md",
    "Measurement probabilities":    "02_quantum_mechanics/03_quantum_measurements.md",
    "Gate / matrix identification": "03_quantum_gates_and_circuits/01_single_qubit_gates.md",
    "Circuit unitary":              "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
    "Entanglement detection":       "02_quantum_mechanics/04_entanglement_and_nonlocality.md",
    "Multi-qubit circuit output":   "03_quantum_gates_and_circuits/02_multi_qubit_gates.md",
    "Circuit equivalence":          "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
    "Notation reading":             "01_mathematical_foundations/01_linear_algebra.md",
    "Circuit composition":          "03_quantum_gates_and_circuits/02_multi_qubit_gates.md",
    "Noise channel":                "02_quantum_mechanics/05_density_matrices_and_open_systems.md",
    "Circuit explanation":          "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
}


class ReferenceScreen(_SharedReferenceScreen):
    """The shared docs browser, pointed at Circuit Trainer's chapter and map."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent, default_chapter=DEFAULT_CHAPTER,
                         category_docs=CATEGORY_DOCS, title="Reference")

    # -- the three names this app's screens and tests use ------------------

    def show_doc(self, path: Path | str) -> bool:
        """Render one Markdown file, given as a path. False if it is not in the
        corpus (the shared screen is addressed by docs-relative path)."""
        target = Path(path)
        root = self.docs_root()
        try:
            rel = target.resolve().relative_to(root.resolve()).as_posix()
        except (OSError, ValueError):
            rel = target.as_posix()
        return self.open_doc(rel)

    def current_doc(self) -> Path | None:
        """The file currently rendered, or None."""
        return self.current_doc_path()

    def chapter_count(self) -> int:
        """How many documents the corpus scan found."""
        return len(self.entries)


__all__ = ["ReferenceScreen", "CATEGORY_DOCS", "DEFAULT_CHAPTER",
           "DocEntry", "docs_root", "scan_docs"]
