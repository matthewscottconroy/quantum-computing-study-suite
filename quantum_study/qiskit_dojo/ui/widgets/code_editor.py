"""Code editor widget — QPlainTextEdit with monospace font and 4-space tabs."""
from __future__ import annotations
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QFont, QFontMetricsF, QKeyEvent
from PyQt6.QtCore import Qt

_INDENT = "    "


class CodeEditor(QPlainTextEdit):
    """Minimal Python code editor: monospace, Tab -> 4 spaces, auto-indent."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("code")
        font = QFont("JetBrains Mono", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(QFontMetricsF(font).horizontalAdvance(" ") * 4)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText(_INDENT)
            return
        if event.key() == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.movePosition(cursor.MoveOperation.Right,
                                cursor.MoveMode.KeepAnchor,
                                min(4, len(_line_text(self))))
            if cursor.selectedText() and not cursor.selectedText().strip():
                cursor.removeSelectedText()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            line = _line_text(self)
            indent = line[: len(line) - len(line.lstrip())]
            if line.rstrip().endswith(":"):
                indent += _INDENT
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return
        super().keyPressEvent(event)


def _line_text(editor: QPlainTextEdit) -> str:
    return editor.textCursor().block().text()
