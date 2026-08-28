"""Entry point for exam-sim."""
import sys
from PyQt6.QtWidgets import QApplication
from ui import theme
from ui.main_window import MainWindow
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
