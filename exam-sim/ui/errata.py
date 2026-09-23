""""Report a problem with this item" — exam-sim's wiring of the shared control.

The dialog and the URL builder are shared
(:mod:`common.ui.errata_dialog` over :mod:`common.errata`): three fields, then
a GitHub issue that is already filled in with the bank file, the question id,
the text as the learner saw it and their comment.  Nothing is sent from the
app — the learner reads and submits the issue themselves.

What this module adds is the two things that are exam-sim's own:

* :func:`item_text_for` — the "quote it exactly" payload for a bank question:
  the stem, the four options with the correct one marked, and the explanation
  the app showed.  That is what a maintainer cannot reconstruct from an id.
* :class:`ReportButton` — the shared button with ``open_browser=False`` so
  **this** module opens the URL and can tell whether it worked.  With no
  browser (a bare container, a locked-down desktop) the report is not lost:
  the URL goes to the clipboard and is shown in a non-modal box the learner
  can copy from.

Where it appears: the results screen's per-miss review cards and the review
screen's feedback area — never the timed exam runner, where a dialog would
eat exam time.  The button is a plain QPushButton, so it is tab-reachable and
draws the theme's focus ring; opening the browser is a fire-and-forget call,
so a slow or missing browser cannot stall the app.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.errata_dialog import ErrataButton
from config import APP_ID
from core.models import Question

BUTTON_TEXT = "⚑ Report a problem with this item"
TOOLTIP = ("Wrong answer key, ambiguous wording, retired Qiskit API? "
           "Opens a prefilled GitHub issue — nothing is sent from here.")


def item_text_for(question: Question, chosen_index: int | None = None) -> str:
    """The question exactly as the learner saw it, for the issue's quote box."""
    lines = [question.question, ""]
    for i, option in enumerate(question.options):
        marks = []
        if i == question.correct_index:
            marks.append("keyed correct")
        if chosen_index is not None and i == chosen_index:
            marks.append("your answer")
        suffix = f"   <- {', '.join(marks)}" if marks else ""
        lines.append(f"{chr(65 + i)}. {option}{suffix}")
    if question.explanation:
        lines += ["", f"Explanation shown: {question.explanation}"]
    return "\n".join(lines)


class ReportButton(ErrataButton):
    """The shared errata button, pointed at an exam-sim bank question."""

    def __init__(self, parent: QWidget | None = None, *, item_id: str = "",
                 item_text: str = "") -> None:
        super().__init__(parent, app=APP_ID, item_id=item_id,
                         item_text=item_text, open_browser=False,
                         text=BUTTON_TEXT)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Report a problem with this exam question")
        self.setToolTip(TOOLTIP)
        self.reported.connect(self.open_in_browser)

    def set_question(self, question: Question,
                     chosen_index: int | None = None) -> None:
        """Point the button at a bank question (id + the text it showed)."""
        self.set_item(question.id, item_text_for(question, chosen_index))

    # -- opening -----------------------------------------------------------

    def open_in_browser(self, url: str) -> bool:
        """Hand *url* to the desktop; fall back to the clipboard if that fails.

        ``QDesktopServices.openUrl`` returns False (or raises, on an exotic
        platform plugin) when there is no browser to hand it to.  Either way
        the learner keeps the report.
        """
        opened = False
        try:
            opened = bool(QDesktopServices.openUrl(QUrl(url)))
        except Exception:                       # pragma: no cover - platform
            opened = False
        if not opened:
            self._offer_url(url)
        return opened

    def _offer_url(self, url: str) -> None:
        """No browser: copy the URL and show it, without blocking anything."""
        copied = False
        try:
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(url)
                copied = True
        except Exception:                       # pragma: no cover - platform
            copied = False
        box = QMessageBox(self)
        box.setWindowTitle("Could not open a browser")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText("This machine has no browser to open the issue in."
                    + (" The link is on your clipboard." if copied else ""))
        box.setDetailedText(url)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        box.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # show(), not exec() and not open(): exec() spins its own event loop
        # and open() forces WindowModal.  This returns immediately and leaves
        # the window behind it usable.
        box.setWindowModality(Qt.WindowModality.NonModal)
        box.show()
