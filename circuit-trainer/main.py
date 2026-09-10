#!/usr/bin/env python3
"""
Circuit Trainer — entry point.

Usage:
    python main.py
    (No API key required — all grading is done locally via Qiskit.)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialise qiskit's native extension on the main thread before any
# ProblemWorker QThread runs (see workers/problem_worker.py for the why).
import qiskit  # noqa: F401,E402

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui import theme
from config import APP_NAME


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    theme.apply(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
