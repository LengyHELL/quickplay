from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from models.page import Page
from views.episode_select import EpisodeSelect
from views.player_page import PlayerPage
from views.title_select import TitleSelect

WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Quickplay")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setWindowIcon(QIcon("_internal/icon.ico"))

        self.titleSelect = TitleSelect(self)
        self.episodeSelect = EpisodeSelect(self)
        self.playerPage = PlayerPage(self)

        self._stackedWidget = QStackedWidget()
        self._stackedWidget.addWidget(self.titleSelect)
        self._stackedWidget.addWidget(self.episodeSelect)
        self._stackedWidget.addWidget(self.playerPage)

        self.setCentralWidget(self._stackedWidget)

    def setPage(self, page: Page) -> None:
        self._stackedWidget.setCurrentIndex(page)
