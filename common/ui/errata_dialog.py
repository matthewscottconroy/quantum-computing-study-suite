""""Report this item" — a button and a dialog that open a prefilled issue.

The repository is public.  When a card is wrong or an exam question is
ambiguous there is no path from "this is wrong" to a fix except remembering it
later.  This is the path: one click, three fields, and a GitHub issue that is
already filled in with the item id, the text as the learner saw it, and their
comment.

Two pieces, both thin over :mod:`common.errata`, which does the actual work
and is pure:

:class:`ErrataDialog`  the modal form (what is wrong / what it should say /
                       how bad).  ``exec()`` it and read :attr:`issue_url`.
:class:`ErrataButton`  a flat "⚑ Report an error" button that opens the dialog
                       and then hands the URL to ``QDesktopServices``.  Drop it
                       into any feedback or review screen with the item's id
                       and text.

Nothing here touches the network: opening the URL is the system browser's job,
and the learner sees and edits the issue before it is filed.
"""
from __future__ import annotations

from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QPlainTextEdit,
    QPushButton, QVBoxLayout, QWidget,
)

from common import errata
from common.ui import theme


class ErrataDialog(QDialog):
    """Collect a one-item error report and build the GitHub issue URL."""

    def __init__(self, parent: QWidget | None = None, *, app: str,
                 item_id: str = "", item_text: str = "",
                 repo: str = errata.REPO) -> None:
        super().__init__(parent)
        self._app = app
        self._item_id = item_id
        self._item_text = item_text
        self._repo = repo
        self._url: str | None = None

        self.setWindowTitle("Report an error in this item")
        self.setMinimumWidth(560)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)

        intro = QLabel(
            "This opens a prefilled issue on GitHub. The item id and its text "
            "are filled in for you — say what is wrong and, if you know it, "
            "what it should say. Nothing is sent until you submit it there."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        root.addWidget(intro)

        form = QFormLayout()
        form.setSpacing(10)

        location = QLabel(errata.item_location(app, item_id))
        location.setWordWrap(True)
        location.setStyleSheet(
            f"color: {theme.TEXT}; font-family: {theme.MONO}; font-size: 12px;")
        form.addRow("Item", location)

        self._why = QPlainTextEdit()
        self._why.setPlaceholderText(
            "The specific defect — a wrong sign, a wrong probability, a "
            "retired Qiskit API, an answer that is not the best of the four…")
        self._why.setMinimumHeight(90)
        form.addRow("What is wrong", self._why)

        self._fix = QPlainTextEdit()
        self._fix.setPlaceholderText("Optional: the corrected wording or number.")
        self._fix.setMinimumHeight(60)
        form.addRow("What it should say", self._fix)

        self._severity = QComboBox()
        for key, label in errata.SEVERITIES.items():
            self._severity.addItem(label, key)
        form.addRow("Severity", self._severity)
        root.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel)
        # addButton() is declared Optional but only returns None for an
        # invalid standard button, which this is not.
        open_btn = buttons.addButton("Open the issue on GitHub",
                                     QDialogButtonBox.ButtonRole.AcceptRole)
        assert open_btn is not None
        self._open_btn = open_btn
        self._open_btn.setObjectName("accent")
        self._open_btn.setEnabled(False)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        # A report with no description is not a report; the button stays off
        # until there is something to read.
        self._why.textChanged.connect(
            lambda: self._open_btn.setEnabled(bool(self._why.toPlainText().strip())))

    # -- public ------------------------------------------------------------

    @property
    def issue_url(self) -> str | None:
        """The built URL once the dialog was accepted, else None."""
        return self._url

    def build_url(self) -> str:
        """The URL for what is currently typed in (no side effects)."""
        return errata.issue_url(
            self._app, self._item_id, self._item_text,
            self._why.toPlainText(),
            severity=self._severity.currentData() or errata.DEFAULT_SEVERITY,
            correction=self._fix.toPlainText(),
            repo=self._repo,
        )

    def _on_accept(self) -> None:
        self._url = self.build_url()
        self.accept()


class ErrataButton(QPushButton):
    """A flat "report this item" button wired to :class:`ErrataDialog`.

    ::

        btn = ErrataButton(app="exam-sim")
        btn.set_item(question.id, question.text)
        layout.addWidget(btn)

    Emits :attr:`reported` with the URL it opened, so a screen can log or
    display it; set ``open_browser=False`` to emit without opening anything
    (which is also how the tests drive it).
    """

    #: Emitted with the issue URL after the dialog is accepted.
    reported = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None, *, app: str,
                 item_id: str = "", item_text: str = "",
                 repo: str = errata.REPO, open_browser: bool = True,
                 text: str = "⚑ Report an error") -> None:
        super().__init__(text, parent)
        self._app = app
        self._item_id = item_id
        self._item_text = item_text
        self._repo = repo
        self._open_browser = open_browser
        self.setObjectName("flat")
        self.setToolTip("Something wrong or ambiguous here? Open a prefilled "
                        "GitHub issue.")
        self.clicked.connect(self.report)

    def set_item(self, item_id: str, item_text: str = "") -> None:
        """Point the button at the item currently on screen."""
        self._item_id = item_id
        self._item_text = item_text

    def report(self) -> str | None:
        """Open the dialog; return the URL when it was accepted, else None."""
        dialog = ErrataDialog(self, app=self._app, item_id=self._item_id,
                              item_text=self._item_text, repo=self._repo)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        url = dialog.issue_url
        if not url:
            return None
        if self._open_browser:
            QDesktopServices.openUrl(QUrl(url))
        self.reported.emit(url)
        return url


__all__ = ["ErrataDialog", "ErrataButton"]
