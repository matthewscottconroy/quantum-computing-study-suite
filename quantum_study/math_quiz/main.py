#!/usr/bin/env python3
"""
Math for Quantum — entry point.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python -m quantum_study.math_quiz
"""

import sys
import os

from PyQt6.QtWidgets import QApplication

from quantum_study.math_quiz.ui.main_window import MainWindow
from quantum_study.math_quiz.ui import theme
from quantum_study.math_quiz.config import APP_NAME


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    theme.apply(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
