""""Report a problem with this item" — one click from a bad item to an issue.

The repository is public.  When a rubric is wrong, a model solution has a sign
error, or a derivation's expected step is ambiguous, there was no path from
"this is wrong" to a fix except remembering it later, and nobody remembers it
later.  This is the path: the button opens
:class:`common.ui.errata_dialog.ErrataDialog`, which collects the defect, an
optional correction and a severity, and builds a **prefilled GitHub issue URL**
through :mod:`common.errata` (pure, offline — it never touches the network).
The system browser then shows the issue form, already filled in with the file,
the item id and the text as the learner saw it; nothing is filed until they
press Submit there.

Two things are added to the shared button, both presentation, neither touching
how the URL is built:

**It never blocks.**  ``ErrataButton.report()`` in ``common`` calls
``dialog.exec()``, which spins a nested event loop and does not return until
the dialog closes.  Here the same dialog is ``show()``n, modeless, and the
result is handled on its ``finished`` signal — so a grading worker keeps
running, the drill stays live behind it, and a half-written report can be left
open while you carry on.  Handing the URL to ``QDesktopServices`` is itself a
hand-off to the desktop that returns immediately; nothing here waits on a
browser, a network call or a subprocess.

**It degrades with no browser.**  ``QDesktopServices.openUrl`` returns False on
a headless or browserless desktop and the shared button ignores that, so the
report would vanish on the click.  Here the URL is shown in a selectable box
instead, ready to copy to a machine that does have a browser.

Keyboard reachable: a plain ``QPushButton`` with strong focus and the theme's
focus ring, opening an ordinary tab-order form.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout, QWidget,
)

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import errata
from common.ui.errata_dialog import ErrataDialog
from common.ui.errata_dialog import ErrataButton as _SharedErrataButton
from config import APP_KEY
from ui import theme

#: What the control says.  Long enough to be unambiguous on a feedback view
#: that already has "Show model solution" next to it.
REPORT_TEXT = "⚑ Report a problem with this item"


def quote_for(*parts: object) -> str:
    """The "quote it exactly" field: the item as the learner saw it.

    Each labelled part that has text is included, so a report about a wrong
    model answer carries the model answer.  ``common.errata`` truncates the
    longest field if the whole URL would get too long, so passing plenty here
    costs nothing.
    """
    out: list[str] = []
    for label, text in zip(parts[::2], parts[1::2]):
        body = str(text or "").strip()
        if body:
            out.append(f"{label}:\n{body}")
    return "\n\n".join(out)


class _FallbackDialog(QDialog):
    """The "copy this link" window shown when no browser could be opened."""

    def __init__(self, url: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Copy this link to report the problem")
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(10)

        intro = QLabel(
            "No browser could be opened from here. The report is not lost — "
            "copy this link and open it anywhere:")
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {theme.TEXT}; font-size: 12px;")
        layout.addWidget(intro)

        self.url_box = QPlainTextEdit(url)
        self.url_box.setReadOnly(True)
        self.url_box.setMinimumHeight(140)
        self.url_box.setStyleSheet(f"font-family: {theme.MONO}; font-size: 11px;")
        self.url_box.setAccessibleName("Prefilled GitHub issue link")
        layout.addWidget(self.url_box)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        self.url_box.selectAll()


class ErrataButton(_SharedErrataButton):
    """:class:`common.ui.errata_dialog.ErrataButton`, modeless and fail-safe."""

    def __init__(self, parent: QWidget | None = None, *, item_id: str = "",
                 item_text: str = "", text: str = REPORT_TEXT) -> None:
        # open_browser=False: the base would call openUrl and drop the result,
        # so the open is done below, where its failure can be handled.
        super().__init__(parent, app=APP_KEY, item_id=item_id,
                         item_text=item_text, open_browser=False, text=text)
        self._dialog: ErrataDialog | None = None
        self._fallback: _FallbackDialog | None = None
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName("Report a problem with this study item")
        self.setToolTip(
            "Wrong, ambiguous or out of date? Opens a prefilled GitHub issue — "
            "you see and edit it before anything is filed.")
        self.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none;"
            f"  color: {theme.TEXT_MUTED}; padding: 4px 8px; font-size: 11px; }}"
            f"QPushButton:hover {{ color: {theme.WARNING}; }}"
            f"QPushButton:focus {{ border: 2px solid {theme.ACCENT};"
            f"  border-radius: 6px; padding: 2px 6px; }}"
        )

    # -- the open form -----------------------------------------------------

    @property
    def dialog(self) -> ErrataDialog | None:
        """The open report form, or None."""
        return self._dialog

    def report(self) -> None:
        """Open the report form.  Returns immediately — nothing is blocked.

        Overrides the shared ``report()``, which ``exec()``s the dialog and so
        does not return until it closes.  The dialog itself, and every field in
        it, is the shared one; only how it is shown is different.
        """
        if self._dialog is not None:
            self._dialog.raise_()
            self._dialog.activateWindow()
            return
        dialog = ErrataDialog(self, app=self._app, item_id=self._item_id,
                              item_text=self._item_text, repo=self._repo)
        dialog.setModal(False)
        dialog.finished.connect(self._on_finished)
        self._dialog = dialog
        dialog.show()

    def _on_finished(self, result: int) -> None:
        dialog, self._dialog = self._dialog, None
        if dialog is None:
            return
        url = dialog.issue_url if result == QDialog.DialogCode.Accepted else None
        dialog.deleteLater()
        if not url:
            return
        if not self.open_in_browser(url):
            self.show_url_fallback(url)
        self.reported.emit(url)

    # -- browser hand-off --------------------------------------------------

    @staticmethod
    def open_in_browser(url: str) -> bool:
        """Hand the URL to the desktop.  False when there is no browser.

        ``QDesktopServices.openUrl`` starts the handler and returns; it never
        waits for the browser.
        """
        try:
            return bool(QDesktopServices.openUrl(QUrl(url)))
        except Exception:                      # pragma: no cover - exotic desktop
            return False

    def show_url_fallback(self, url: str) -> None:
        """Show the URL so it can be copied when no browser could be opened."""
        self._fallback = self.fallback_dialog(url)
        self._fallback.finished.connect(lambda _r: setattr(self, "_fallback", None))
        self._fallback.show()

    def fallback_dialog(self, url: str) -> _FallbackDialog:
        """The "copy this link" dialog, built but not shown."""
        return _FallbackDialog(url, self)


__all__ = ["ErrataButton", "ErrataDialog", "REPORT_TEXT", "quote_for", "errata"]
