"""Calculator app demo"""

import sys
import os
import re
from functools import partial
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, SUPPRESS
import subprocess

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLineEdit,
    QListView,
    QHBoxLayout,
    QScrollBar,
)

from PyQt6.QtCore import QStringListModel

WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 400
# python -m PyInstaller --noconfirm quickplay.spec


class QuickplayView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quickplay")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.titleSelect = TitleSelect(self)
        self.episodeSelect = EpisodeSelect(self)

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.titleSelect)
        self.stackedWidget.addWidget(self.episodeSelect)

        self.setCentralWidget(self.stackedWidget)

class TitleSelect(QWidget):
    def __init__(self, parent: QuickplayView):
        super().__init__(parent)

        self.titleSelectLayout = QVBoxLayout()
        self.setLayout(self.titleSelectLayout)

        self._createSearch()
        self._createTitleList()
        self._createButtons()

    def _createSearch(self):
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self.titleSelectLayout.addWidget(self.search)

    def _createTitleList(self):
        self.listModel = QStringListModel()
        self.scrollBar = QScrollBar()
        self.list = QListView()
        self.list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.list.setVerticalScrollBar(self.scrollBar)
        self.list.setModel(self.listModel)
        self.titleSelectLayout.addWidget(self.list)

    def _createButtons(self):
        self.buttonLayout = QHBoxLayout()
        self.startPrevious = QPushButton("Start previous")
        self.next = QPushButton("Next")
        self.buttonLayout.addWidget(self.startPrevious)
        self.buttonLayout.addWidget(self.next)
        self.titleSelectLayout.addLayout(self.buttonLayout)


class EpisodeSelect(QWidget):
    def __init__(self, parent: QuickplayView):
        super().__init__(parent)

        self.episodeSelectLayout = QVBoxLayout()
        self.setLayout(self.episodeSelectLayout)

        self._createSearch()
        self._createEpisodeList()
        self._createButtons()

    def _createSearch(self):
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self.episodeSelectLayout.addWidget(self.search)

    def _createEpisodeList(self):
        self.listModel = QStringListModel()
        self.scrollBar = QScrollBar()
        self.list = QListView()
        self.list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.list.setVerticalScrollBar(self.scrollBar)
        self.list.setModel(self.listModel)
        self.episodeSelectLayout.addWidget(self.list)

    def _createButtons(self):
        self.buttonLayout = QHBoxLayout()
        self.back = QPushButton("Back")
        self.startAll = QPushButton("Start All")
        self.start = QPushButton("Start")
        self.buttonLayout.addWidget(self.back)
        self.buttonLayout.addWidget(self.startAll)
        self.buttonLayout.addWidget(self.start)
        self.episodeSelectLayout.addLayout(self.buttonLayout)

class QuickplayModel:
    def parseArguments(self):
        parser = ArgumentParser(
            add_help=False,
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            "-h",
            "--help",
            action="help",
            default=SUPPRESS,
            help="Show this help message.",
        )
        parser.add_argument(
            "-e",
            "--executable",
            dest="executable",
            default="mpv",
            help="MPV executable location.",
            metavar="PATH",
        )
        parser.add_argument(
            "-f",
            "--folder",
            dest="folderFile",
            default="_internal/folders.txt",
            help="The directory config text file used for parsing titles.",
            metavar="FILE",
        )
        parser.add_argument(
            "-p",
            "--playlist",
            dest="playlistFile",
            default="_internal/quickplay.txt",
            help="The playlist config text file used for storing playlist elements.",
            metavar="FILE",
        )
        parser.add_argument(
            "-x",
            "--extensions",
            dest="extensions",
            default=".mkv, .mp4",
            help='The extensions to include when searching the directories. \
                (eg.: ".mkv, .mp4, .mov")',
            metavar="LIST",
        )

        return parser.parse_args()


class QuickplayController:
    def __init__(self, model: QuickplayModel, view: QuickplayView):
        self._model = model
        self._view = view
        self._episodeList: list[str] = []
        self.filteredEpisodes: list[str] = []

        self._parseArguments()
        self._readTitles()
        self._filterTitles()
        self._connectInputs()

    def _parseArguments(self):
        args = self._model.parseArguments()
        self.executable: str = args.executable
        self.folderFile: str = args.folderFile
        self.playlistFile: str = args.playlistFile
        self.extensions: list[str] = re.sub(r"\s", "", args.extensions).split(",")

    def _selectPage(self, index):
        self._view.stackedWidget.setCurrentIndex(index)

    def _connectInputs(self):
        self._view.titleSelect.search.textChanged.connect(self._filterTitles)
        self._view.titleSelect.next.clicked.connect(self._goToEpisodes)
        self._view.titleSelect.startPrevious.clicked.connect(partial(self._openPlayer, []))
        self._view.titleSelect.list.doubleClicked.connect(self._goToEpisodes)

        self._view.episodeSelect.search.textChanged.connect(self._filterEpisodes)
        self._view.episodeSelect.back.clicked.connect(partial(self._selectPage, 0))
        self._view.episodeSelect.startAll.clicked.connect(self._startAllEpisodes)
        self._view.episodeSelect.start.clicked.connect(self._startSelectedEpisodes)
        self._view.episodeSelect.list.doubleClicked.connect(self._startSelectedEpisodes)

    def _readTitles(self):
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
                    if os.path.isdir(os.path.join(f, d)):
                        self.titleList.append((f, d))

    def _filterTitles(self, text = ""):
        if not text:
            self.filteredTitles = self.titleList.copy()
        else:
            self.filteredTitles = list(
                filter(
                    lambda x: x[1].lower().find(text.lower()) >= 0,
                    self.titleList,
                )
            )

        self._view.titleSelect.listModel.setStringList([l[1] for l in self.filteredTitles])

    def _goToEpisodes(self):
        self._selectPage(1)
        self._readEpisodes()

    def _readEpisodes(self):
        index = self._view.titleSelect.list.selectedIndexes()[0].row()
        base, title = self.filteredTitles[index]
        directory = os.path.join(base, title)
        self._episodeList = []

        if os.path.isdir(directory):
            dirs = os.listdir(directory)
            for d in dirs:
                if (
                    os.path.isfile(os.path.join(directory, d))
                    and os.path.splitext(d)[-1] in self.extensions
                ):
                    self._episodeList.append(d)
        else:
            print(f"Failed to find directory '{directory}'!")

        self._filterEpisodes()

    def _filterEpisodes(self, text = ""):
        if not text:
            self.filteredEpisodes = self._episodeList.copy()
        else:
            self.filteredEpisodes = list(
                filter(
                    lambda x: x.lower().find(text.lower()) >= 0,
                    self._episodeList,
                )
            )

        self._view.episodeSelect.listModel.setStringList(self.filteredEpisodes)

    def _getEpisodes(self):
        return self._episodeList

    def _startAllEpisodes(self):
        self._openPlayer(self._episodeList)

    def _startSelectedEpisodes(self):
        indexes = [i.row() for i in self._view.episodeSelect.list.selectedIndexes()]
        self._openPlayer([self.filteredEpisodes[i] for i in indexes])

    def _openPlayer(self, episodes):
        if len(episodes) > 0:
            with open(self.playlistFile, "w", encoding="utf-8") as file:
                index = self._view.titleSelect.list.selectedIndexes()[0].row()
                base, title = self.filteredTitles[index]

                for episode in episodes:
                    line = os.path.join(base, title, episode) + "\n"
                    file.write(line)

        subprocess.Popen(
            self.executable + " --playlist=" + self.playlistFile,
            creationflags=subprocess.CREATE_BREAKAWAY_FROM_JOB
        )
        self._view.close()

def getStyleSheet(path):
    content = ""
    with open(path, "r", encoding="utf-8") as styles:
        content = styles.read()

    return content

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(getStyleSheet("_internal/styles.qss"))

    view = QuickplayView()
    view.show()

    model = QuickplayModel()

    QuickplayController(model, view)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
