"""Reference screen for exam-sim — the shared docs browser, plus exam sections.

The browser itself is :class:`common.ui.reference.ReferenceScreen`: doc
discovery, the chapter filter, full-text search, the Markdown preparation
(``$$ … $$`` display math, ``<details><summary>`` solution blocks, bare
``NN_chapter/NN_file.md`` cross-references, heading anchors) and the dark
restyling all live there, once, for all ten apps.

What is exam-sim's own, and stays here:

* :data:`SECTION_DOCS` — the curated map from an exam section to the chapters
  that back its objectives.  Its first entry per section is handed to the
  shared screen as ``category_docs``, which drives the "Jump to topic" picker
  in the top bar;
* the **★ Suggested for C1000-179** filter, which narrows the list to just
  those chapters, and the "exam sections: …" annotation under a document's
  title and in its list tooltip.

The suggested filter is added by *composition*, not by forking the list code:
:meth:`ReferenceScreen._rebuild_list` narrows the entry list, delegates to the
shared implementation, and maps the row indices back onto the full list
afterwards.  The shared screen keeps sole ownership of how a list row is
built, selected and rendered.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QWidget

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui import reference as _ref
from common.ui import theme
from common.ui.reference import (  # noqa: F401  (re-exported for callers/tests)
    ALL_CHAPTERS, DocEntry, docs_root, heading_slug, prepare_markdown,
    resolve_doc_ref, scan_docs,
)

#: Exam section -> docs (relative to the docs root) that back its objectives.
#: Only files that exist on disk are shown; nothing here is load-bearing.
SECTION_DOCS: dict[str, list[str]] = {
    "Create circuits": [
        "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
        "04_quantum_algorithms/01_quantum_parallelism_and_interference.md",
    ],
    "Quantum operations": [
        "03_quantum_gates_and_circuits/01_single_qubit_gates.md",
        "03_quantum_gates_and_circuits/02_multi_qubit_gates.md",
        "01_mathematical_foundations/03_tensor_products_and_multipartite_systems.md",
    ],
    "Run circuits": [
        "03_quantum_gates_and_circuits/04_quantum_circuit_complexity.md",
        "07_quantum_hardware/01_superconducting_qubits.md",
    ],
    "Sampler": [
        "02_quantum_mechanics/03_quantum_measurements.md",
    ],
    "Estimator": [
        "02_quantum_mechanics/01_postulates_of_quantum_mechanics.md",
        "06_variational_quantum_algorithms/01_vqe_fundamentals.md",
    ],
    "Visualization": [
        "02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md",
    ],
    "Results analysis": [
        "02_quantum_mechanics/03_quantum_measurements.md",
        "02_quantum_mechanics/10_distance_measures_and_lindblad.md",
    ],
    "OpenQASM": [
        "03_quantum_gates_and_circuits/03_circuit_model_and_universality.md",
    ],
}

SUGGESTED_LABEL = "★ Suggested for C1000-179"


def category_docs() -> dict[str, str]:
    """Section -> the one chapter the "Jump to topic" picker opens for it.

    The shared screen's picker takes one document per category; a section that
    lists several is represented by the first, which is the one the objective
    maps onto most directly.  The rest stay reachable through the suggested
    filter.
    """
    return {section: rels[0] for section, rels in SECTION_DOCS.items() if rels}


def sections_for(rel: str) -> list[str]:
    """Exam sections that suggest the document at *rel* (docs-relative path)."""
    return [section for section, rels in SECTION_DOCS.items() if rel in rels]


def suggested_rels() -> set[str]:
    """Every docs-relative path named by :data:`SECTION_DOCS`."""
    return {rel for rels in SECTION_DOCS.values() for rel in rels}


class ReferenceScreen(_ref.ReferenceScreen):
    """The shared Reference screen with exam-sim's section suggestions."""

    def __init__(self, parent=None, **kwargs) -> None:
        kwargs.setdefault("category_docs", category_docs())
        super().__init__(parent, **kwargs)
        self._suggested_only = False
        self._suggested_cb = QCheckBox(SUGGESTED_LABEL)
        self._suggested_cb.setToolTip(
            "Show only the chapters that back an exam objective "
            f"({len(suggested_rels())} of them)")
        self._suggested_cb.setAccessibleName(
            "Show only chapters suggested for the C1000-179 objectives")
        self._suggested_cb.setStyleSheet(f"color: {theme.TEXT_MUTED};")
        self._suggested_cb.toggled.connect(self._on_suggested_toggled)
        self._install_suggested_checkbox()

    # -- construction ------------------------------------------------------

    def _install_suggested_checkbox(self) -> None:
        """Put the filter in the shared top bar, just before the search box."""
        bar = self.findChild(QWidget, "refTopBar")
        layout = bar.layout() if bar is not None else None
        if layout is None:                      # pragma: no cover - defensive
            return
        index = layout.indexOf(self._chapter_filter)
        layout.insertWidget(index + 1 if index >= 0 else 0, self._suggested_cb)

    # -- public API --------------------------------------------------------

    @property
    def suggested_only(self) -> bool:
        """True while the list is narrowed to the suggested chapters."""
        return self._suggested_only

    def set_suggested_only(self, on: bool) -> None:
        """Turn the ★ Suggested filter on or off (as the checkbox does)."""
        self._suggested_cb.setChecked(bool(on))

    def open_doc(self, rel_path: str, fragment: str | None = None) -> bool:
        """Shared ``open_doc``, but the ★ filter steps aside if it hides the target.

        The shared screen already clears the chapter filter and the search box
        when they would hide the document being opened; this keeps that
        promise for the one filter this app adds.
        """
        if self._suggested_only and not sections_for(
                rel_path.replace("\\", "/").lstrip("./")):
            self._suggested_cb.setChecked(False)
        return super().open_doc(rel_path, fragment)

    def show_doc(self, rel_path: str) -> bool:
        """Select a doc by its path relative to the docs root.

        The name this app used before the migration; ``open_doc`` (which also
        takes a heading fragment) is the shared spelling.
        """
        return self.open_doc(rel_path)

    def show_section(self, section: str) -> bool:
        """Open the chapter suggested for an exam section."""
        return self.show_category(section)

    # -- the suggested filter ---------------------------------------------

    def _scan(self) -> None:
        """Shared scan, plus: the ★ filter is only offered if it would match."""
        super()._scan()
        available = any(sections_for(e.rel) for e in self._entries)
        self._suggested_cb.setEnabled(available)
        if not available:
            self._suggested_cb.setChecked(False)

    def _on_suggested_toggled(self, on: bool) -> None:
        self._suggested_only = bool(on)
        if self._entries:
            self._rebuild_list()

    def _rebuild_list(self, *args, keep: DocEntry | None = None) -> None:
        """Shared list build, optionally narrowed to the suggested chapters.

        The narrowing swaps ``self._entries`` for the subset around the call
        to the shared implementation — which stores each row's index into
        ``self._entries`` — and then maps those indices back onto the full
        list, so every later lookup (selection, ``open_doc``, rendering) works
        on the real entries.
        """
        full = self._entries
        subset = ([e for e in full if sections_for(e.rel)]
                  if self._suggested_only else [])
        if subset:
            self._entries = subset
            try:
                super()._rebuild_list(*args, keep=keep)
            finally:
                self._entries = full
            self._remap_rows(subset, len(full))
        else:
            super()._rebuild_list(*args, keep=keep)
        self._annotate_rows()

    def _remap_rows(self, subset: list[DocEntry], total: int) -> None:
        """Rewrite each row's stored index from *subset* onto the full list."""
        position = {id(entry): i for i, entry in enumerate(self._entries)}
        shown = 0
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is None:
                continue
            idx = item.data(_ref._INDEX_ROLE)
            if idx is None or not (0 <= idx < len(subset)):
                continue
            item.setData(_ref._INDEX_ROLE, position[id(subset[idx])])
            shown += 1
        self._count_lbl.setText(f"{shown} suggested of {total} documents")

    def _annotate_rows(self) -> None:
        """Add "Suggested for: …" to the tooltip of every suggested row."""
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is None:
                continue
            idx = item.data(_ref._INDEX_ROLE)
            if idx is None or not (0 <= idx < len(self._entries)):
                continue
            sections = sections_for(self._entries[idx].rel)
            if sections:
                item.setToolTip(f"{item.toolTip()}\n"
                                f"Suggested for: {', '.join(sections)}")

    # -- rendering ---------------------------------------------------------

    def _render(self, entry: DocEntry, keep_scroll: bool = False) -> None:
        super()._render(entry, keep_scroll)
        sections = sections_for(entry.rel)
        if sections:
            self._doc_path.setText(
                f"{self._doc_path.text()}   ·   exam sections: "
                f"{', '.join(sections)}")
