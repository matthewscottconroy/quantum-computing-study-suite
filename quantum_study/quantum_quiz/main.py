#!/usr/bin/env python3
"""
Quantum Quiz — entry point.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python -m quantum_study.quantum_quiz
"""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from quantum_study.quantum_quiz.ui.main_window import MainWindow
from quantum_study.quantum_quiz.ui import theme
from quantum_study.quantum_quiz.config import APP_NAME


def main() -> None:
    # High-DPI support
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)

    theme.apply(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
