import locale
import sys

from PyQt6.QtWidgets import QApplication

from controller import QuickplayController
from services.config_service import ConfigService
from services.directory_service import DirectoryService
from utils import getStylesheet
from views.main_window import MainWindow


def main() -> None:
    locale.setlocale(locale.LC_NUMERIC, "C")

    app = QApplication(sys.argv)
    app.setStyleSheet(getStylesheet("_internal/styles.qss"))

    view = MainWindow()
    view.show()

    directoryService = DirectoryService()
    configService = ConfigService()

    _controller = QuickplayController(view, directoryService, configService)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
