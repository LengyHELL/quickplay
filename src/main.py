import locale
import sys

from PyQt6.QtWidgets import QApplication

from controller import QuickplayController
from services.directory_service import DirectoryService
from services.playlist_service import PlaylistService
from utils import getStylesheet, parseArguments
from views.main_window import MainWindow


def main() -> None:
    locale.setlocale(locale.LC_NUMERIC, "C")

    app = QApplication(sys.argv)
    app.setStyleSheet(getStylesheet("_internal/styles.qss"))

    config = parseArguments()

    view = MainWindow()
    view.show()

    directoryService = DirectoryService()
    playlistService = PlaylistService()

    _controller = QuickplayController(config, view, directoryService, playlistService)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
