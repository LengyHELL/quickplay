import locale
import sys

from PyQt6.QtWidgets import QApplication

from controller import QuickplayController
from models.app_config import parse_arguments
from services.directory_service import DirectoryService
from services.playlist_service import PlaylistService
from utils import get_stylesheet
from views.main_window import MainWindow


def main() -> None:
    locale.setlocale(locale.LC_NUMERIC, "C")

    app = QApplication(sys.argv)
    app.setStyleSheet(get_stylesheet("_internal/styles.qss"))

    config = parse_arguments()

    view = MainWindow()
    view.show()

    directoryService = DirectoryService()
    playlistService = PlaylistService()

    _controller = QuickplayController(config, view, directoryService, playlistService)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
