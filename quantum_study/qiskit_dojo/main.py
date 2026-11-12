"""Entry point for qiskit-dojo."""
import sys
from PyQt6.QtWidgets import QApplication
from quantum_study.qiskit_dojo.ui import theme
from quantum_study.qiskit_dojo.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Qiskit Dojo")
    theme.apply(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
