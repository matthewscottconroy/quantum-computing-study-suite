#!/usr/bin/env python3
"""
Quantum Quiz — entry point.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python main.py
"""

import sys
import os

# Ensure project root is on sys.path regardless of where the user runs from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from ui import theme
from config import APP_NAME


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
