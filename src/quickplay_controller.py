import os
import re
from functools import partial

from PyQt6.QtGui import QPalette, QStandardItem

from quickplay_model import QuickplayModel
from quickplay_utils import QuickPlayUtil
from quickplay_view import QuickplayView


class QuickplayController:
    def __init__(self, model: QuickplayModel, view: QuickplayView) -> None:
        self._model = model
        self._view = view
        self._episodeList: list[str] = []
        self.filteredEpisodes: list[str] = []

        self._parseArguments()
        self._readTitles()
        self._filterTitles()
        self._connectInputs()
        self._setTitleSelectDisable()
        self._setEpisodeSelectDisable()
        self._observePlayerFullscreen()
        self._observePlayerQuit()

    def _parseArguments(self) -> None:
        args = self._model.parseArguments()
        self.folderFile: str = args.folderFile
        self.playlistFile: str = args.playlistFile
        self.extensions: list[str] = re.sub(r"\s", "", args.extensions).split(",")

    def _selectPage(self, index: int) -> None:
        self._view.stackedWidget.setCurrentIndex(index)

    def _connectInputs(self) -> None:
        self._view.titleSelect.search.textChanged.connect(self._filterTitles)
        self._view.titleSelect.next.clicked.connect(self._goToEpisodes)
        self._view.titleSelect.startPrevious.clicked.connect(partial(self._goToPlayer, []))
        self._view.titleSelect.list.doubleClicked.connect(self._goToEpisodes)
        self._view.titleSelect.list.selectionModel().selectionChanged.connect(self._setTitleSelectDisable)

        self._view.episodeSelect.search.textChanged.connect(self._filterEpisodes)
        self._view.episodeSelect.back.clicked.connect(partial(self._selectPage, 0))
        self._view.episodeSelect.startAll.clicked.connect(self._startAllEpisodes)
        self._view.episodeSelect.start.clicked.connect(self._startSelectedEpisodes)
        self._view.episodeSelect.list.doubleClicked.connect(self._startSelectedEpisodes)
        self._view.episodeSelect.list.selectionModel().selectionChanged.connect(self._setEpisodeSelectDisable)

        self._view.videoPlayer.back.clicked.connect(self._stopPlayback)

    def _setTitleSelectDisable(self) -> None:
        disabled = len(self._view.titleSelect.list.selectedIndexes()) <= 0
        self._view.titleSelect.next.setDisabled(disabled)

    def _setEpisodeSelectDisable(self) -> None:
        disabled = len(self._view.episodeSelect.list.selectedIndexes()) <= 0
        self._view.episodeSelect.start.setDisabled(disabled)

    def _handleFullscreen(self, fullscreen: bool) -> None:
        if fullscreen:
            self._view.showFullScreen()
            self._view.videoPlayer.buttonFrame.hide()
            self._view.videoPlayer.videoPlayerLayout.setContentsMargins(0, 0, 0, 0)
        else:
            self._view.showNormal()
            self._view.videoPlayer.buttonFrame.show()
            self._view.videoPlayer.videoPlayerLayout.unsetContentsMargins()

    def _observePlayerFullscreen(self) -> None:
        self._view.videoPlayer.player.isFullscreen.connect(self._handleFullscreen)

    def _observePlayerQuit(self) -> None:
        self._view.videoPlayer.player.quitEvent.connect(self._stopPlayback)

    def _readTitles(self) -> None:
        self.titleList: list[tuple[str, str]] = []

        if not os.path.isfile(self.folderFile):
            print(f"Failed to open folder file '{self.folderFile}'!")
            return

        with open(self.folderFile, "r", encoding="utf-8") as file:
            folders = [f.strip() for f in file.readlines()]
            for f in folders:
                if not os.path.isdir(f):
                    print(f"Failed to find directory '{f}'!")
                    continue

                dirs = os.listdir(f)
                for d in dirs:
                    path = os.path.join(f, d)
                    if os.path.isdir(path) and any([os.path.isfile(os.path.join(path, f)) and os.path.splitext(os.path.join(path, f))[1] in self.extensions for f in os.listdir(path)]):
                        self.titleList.append((f, d))

    def _filterTitles(self, text: str = "") -> None:
        if not text:
            self.filteredTitles = self.titleList.copy()
        else:
            self.filteredTitles = list(
                filter(
                    lambda x: x[1].lower().find(text.lower()) >= 0,
                    self.titleList,
                )
            )

        self._view.titleSelect.list.clearSelection()
        self._view.titleSelect.listModel.setStringList([title[1] for title in self.filteredTitles])

    def _goToEpisodes(self) -> None:
        self._selectPage(1)
        self._readEpisodes()

    def _readEpisodes(self) -> None:
        index = self._view.titleSelect.list.selectedIndexes()[0].row()
        base, title = self.filteredTitles[index]
        directory = os.path.join(base, title)
        self._episodeList = []

        if os.path.isdir(directory):
            dirs = os.listdir(directory)
            for d in dirs:
                if os.path.isfile(os.path.join(directory, d)) and os.path.splitext(d)[-1] in self.extensions:
                    self._episodeList.append(d)
        else:
            print(f"Failed to find directory '{directory}'!")

        self._filterEpisodes()

    def _filterEpisodes(self, text: str = "") -> None:
        if not text:
            self.filteredEpisodes = self._episodeList.copy()
        else:
            self.filteredEpisodes = list(
                filter(
                    lambda x: x.lower().find(text.lower()) >= 0,
                    self._episodeList,
                )
            )

        self._view.episodeSelect.list.clearSelection()
        self._view.episodeSelect.listModel.clear()
        for index, episode in enumerate(self.filteredEpisodes):
            icon = QuickPlayUtil.icon("check", QPalette.ColorRole.Text)
            item = QStandardItem(icon, episode) if index % 2 == 0 else QStandardItem(episode)
            self._view.episodeSelect.listModel.appendRow(item)

    def _getEpisodes(self) -> None:
        return self._episodeList

    def _startAllEpisodes(self) -> None:
        self._goToPlayer(self._episodeList)

    def _startSelectedEpisodes(self) -> None:
        indexes = [i.row() for i in self._view.episodeSelect.list.selectedIndexes()]
        self._goToPlayer([self.filteredEpisodes[i] for i in indexes])

    def _goToPlayer(self, episodes: list[str]) -> None:
        if episodes:
            index = self._view.titleSelect.list.selectedIndexes()[0].row()
            base, title = self.filteredTitles[index]
            paths = [os.path.join(base, title, episode) for episode in episodes]

            self._view.videoPlayer.player.loadEpisodes(paths)
            self._selectPage(2)
            self._view.videoPlayer.player.start(0)

    def _stopPlayback(self) -> None:
        self._view.videoPlayer.player.stop()
        self._handleFullscreen(False)
        self._goToEpisodes()
