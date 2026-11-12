"""Entry point for paper-drill."""
import sys
from PyQt6.QtWidgets import QApplication
from quantum_study.paper_drill.ui import theme
from quantum_study.paper_drill.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Paper Drill")
    theme.apply(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
