"""Entry point for flashcard-drill."""
import sys
from PyQt6.QtWidgets import QApplication
from quantum_study.flashcard_drill.ui import theme
from quantum_study.flashcard_drill.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Flashcard Drill")
    theme.apply(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
