"""Entry point for problem-trainer."""
import sys
from PyQt6.QtWidgets import QApplication
from quantum_study.problem_trainer.ui import theme
from quantum_study.problem_trainer.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Problem Trainer")
    theme.apply(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
