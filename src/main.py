import locale
import sys

from PyQt6.QtWidgets import QApplication

from controller import QuickplayController
from utils import getStylesheet
from views.main_window import MainWindow


def main() -> None:
    locale.setlocale(locale.LC_NUMERIC, "C")

    app = QApplication(sys.argv)
    app.setStyleSheet(getStylesheet("_internal/styles.qss"))

    view = MainWindow()
    view.show()

    _controller = QuickplayController(view)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
