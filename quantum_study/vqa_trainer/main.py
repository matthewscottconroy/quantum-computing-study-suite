"""Entry point for vqa-trainer."""
import sys
from PyQt6.QtWidgets import QApplication
from quantum_study.vqa_trainer.ui import theme
from quantum_study.vqa_trainer.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("VQA Trainer")
    theme.apply(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
