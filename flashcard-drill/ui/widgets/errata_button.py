""""Report a problem with this item" — the card-back errata control.

:class:`common.ui.errata_dialog.ErrataButton` does the work: it collects what
is wrong, builds a prefilled GitHub issue URL with
:mod:`common.errata`, and hands it to ``QDesktopServices``.  This subclass
changes exactly two things, both of which matter inside a drill:

* **It never blocks.**  The shared button calls ``dialog.exec()``, which spins
  a nested event loop until the dialog closes.  Here the dialog is ``open()``'d
  — window-modal, non-blocking — and the report is finished on its
  ``finished`` signal, so the timer keeps counting, the card keeps repainting
  and the session is never frozen by a report the user walked away from.
* **It degrades when there is no browser.**  ``QDesktopServices.openUrl``
  returns False on a machine with no handler for ``https://`` (a bare X
  session, a locked-down container).  The URL is then copied to the clipboard
  and the button *says so in its own label* — visible without hovering, with
  the URL itself in the tooltip — instead of the click doing nothing.  The
  label goes back to normal on the next card.

Keyboard: it is an ordinary focusable button (Tab reaches it, Space and Enter
activate it) with an accessible name, and it emits :attr:`CardErrataButton.closed`
when its dialog goes away so the screen can take its keyboard focus back and the
drill shortcuts keep working.
"""
from __future__ import annotations

from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QGuiApplication
from PyQt6.QtWidgets import QDialog, QWidget

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import errata
from common.ui.errata_dialog import ErrataButton, ErrataDialog

#: What the control says on the card back.
BUTTON_TEXT = "⚠ Report a problem with this item"

#: …and what it says instead when there was no browser to open.
NO_BROWSER_TEXT = "⚠ No browser — issue URL copied to clipboard"

_NO_BROWSER = ("Could not open a browser — the issue URL is on your clipboard, "
               "paste it into one when you have a moment.")
_TOOLTIP = ("Wrong, ambiguous or out of date? Open a prefilled GitHub issue "
            "(nothing is sent until you submit it there).")


class CardErrataButton(ErrataButton):
    """A non-blocking "report this card" button for the card screen."""

    #: Emitted when the browser could not be opened; carries the URL, which is
    #: also on the clipboard.
    open_failed = pyqtSignal(str)

    #: Emitted whenever the dialog closes, accepted or not — the drill screen
    #: connects it to take keyboard focus back.
    closed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None, *, app: str,
                 item_id: str = "", item_text: str = "",
                 repo: str = errata.REPO, open_browser: bool = True) -> None:
        super().__init__(parent, app=app, item_id=item_id, item_text=item_text,
                         repo=repo, open_browser=open_browser, text=BUTTON_TEXT)
        self.setObjectName("flat")
        self.setToolTip(_TOOLTIP)
        self.setAccessibleName("Report a problem with this card")
        self.setAccessibleDescription(
            "Opens a prefilled GitHub issue about this card's content")
        self._dialog: ErrataDialog | None = None

    # -- the whole point: this does not spin a nested event loop -------------

    def report(self) -> None:                       # type: ignore[override]
        """Open the report dialog and return immediately.

        One dialog at a time: a second click while it is up just raises it.
        """
        if self._dialog is not None:
            self._dialog.raise_()
            self._dialog.activateWindow()
            return
        dialog = ErrataDialog(self, app=self._app, item_id=self._item_id,
                              item_text=self._item_text, repo=self._repo)
        self._dialog = dialog
        dialog.finished.connect(self._on_finished)
        dialog.open()                               # non-blocking, window-modal

    def set_item(self, item_id: str, item_text: str = "") -> None:
        """Point the button at the card on screen, and clear any stale notice."""
        super().set_item(item_id, item_text)
        self.setText(BUTTON_TEXT)
        self.setToolTip(_TOOLTIP)

    @property
    def dialog(self) -> ErrataDialog | None:
        """The dialog currently open, if any (the tests drive it through this)."""
        return self._dialog

    def _on_finished(self, result: int) -> None:
        dialog, self._dialog = self._dialog, None
        if dialog is not None:
            dialog.deleteLater()
        self.closed.emit()
        if dialog is None or result != QDialog.DialogCode.Accepted:
            return
        url = dialog.issue_url
        if not url:
            return
        if self._open_browser and not QDesktopServices.openUrl(QUrl(url)):
            self._no_browser(url)
        self.reported.emit(url)

    def _no_browser(self, url: str) -> None:
        """No handler for https: keep the report reachable instead of losing it."""
        try:
            clipboard = QGuiApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(url)
        except Exception:                           # pragma: no cover - platform
            pass
        self.setText(NO_BROWSER_TEXT)
        self.setToolTip(f"{_NO_BROWSER}\n\n{url}")
        self.open_failed.emit(url)


__all__ = ["CardErrataButton", "BUTTON_TEXT", "NO_BROWSER_TEXT"]
