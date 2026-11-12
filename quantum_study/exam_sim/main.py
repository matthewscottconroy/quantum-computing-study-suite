"""Entry point for exam-sim."""
import sys
from PyQt6.QtWidgets import QApplication
from quantum_study.exam_sim.ui import theme
from quantum_study.exam_sim.ui.main_window import MainWindow
from quantum_study.exam_sim.config import APP_NAME


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    theme.apply(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
