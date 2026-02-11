from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
)

from episode_select import EpisodeSelect
from title_select import TitleSelect
from video_player import VideoPlayer

WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 400


class QuickplayView(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Quickplay")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setWindowIcon(QIcon("_internal/icon.ico"))

        self.titleSelect = TitleSelect(self)
        self.episodeSelect = EpisodeSelect(self)
        self.videoPlayer = VideoPlayer(self)

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.titleSelect)
        self.stackedWidget.addWidget(self.episodeSelect)
        self.stackedWidget.addWidget(self.videoPlayer)

        self.setCentralWidget(self.stackedWidget)
