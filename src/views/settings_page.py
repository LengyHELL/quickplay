import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from _version import VERSION
from models.app_config import AppConfig
from utils import makeIcon


class SettingsPage(QWidget):
    settingsSaved = pyqtSignal(AppConfig)
    "appConfig"
    backClicked = pyqtSignal()
    checkForUpdates = pyqtSignal()
    downloadUpdate = pyqtSignal()
    installUpdate = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._createTabs()
        self._createButtons()
        self._connectSignals()

    def _createTabs(self) -> None:
        self._tabWidget = QTabWidget()
        self._createFoldersTab()
        self._createUpdateTab()
        self._layout.addWidget(self._tabWidget)

    def _createFoldersTab(self) -> None:
        tab = QWidget()

        layout = QVBoxLayout()
        tab.setLayout(layout)

        layout.addWidget(QLabel("Media Folders"))

        folderListLayout = QHBoxLayout()

        self._folderList = QListWidget()
        folderListLayout.addWidget(self._folderList)

        folderButtonLayout = QVBoxLayout()
        self._addFolderBtn = QPushButton(makeIcon("plus", QPalette.ColorRole.Text), None)
        self._removeFolderBtn = QPushButton(makeIcon("minus", QPalette.ColorRole.Text), None)
        folderButtonLayout.addWidget(self._addFolderBtn)
        folderButtonLayout.addWidget(self._removeFolderBtn)
        folderButtonLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        folderListLayout.addLayout(folderButtonLayout)

        layout.addLayout(folderListLayout)

        layout.addWidget(QLabel("File Extensions (comma-separated)"))

        self._extensionsInput = QLineEdit()
        self._extensionsInput.setPlaceholderText(".mkv, .mp4")
        layout.addWidget(self._extensionsInput)

        self._tabWidget.addTab(tab, makeIcon("folder", QPalette.ColorRole.Text, 14), "Folders")

    def _createUpdateTab(self) -> None:
        tab = QWidget()

        layout = QVBoxLayout()
        tab.setLayout(layout)

        updateBarLayout = QHBoxLayout()

        self._versionLabel = QLabel(f"Current version: {VERSION}")
        updateBarLayout.addWidget(self._versionLabel)

        self._downloadProgress = QProgressBar()
        self._downloadProgress.setRange(0, 100)
        self._downloadProgress.setVisible(False)
        updateBarLayout.addWidget(self._downloadProgress)

        self._installUpdateBtn = QPushButton(makeIcon("hard-drive", QPalette.ColorRole.Text), None)
        self._installUpdateBtn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self._installUpdateBtn.setVisible(False)
        updateBarLayout.addWidget(self._installUpdateBtn)

        self._downloadUpdateBtn = QPushButton(makeIcon("download", QPalette.ColorRole.Text), None)
        self._downloadUpdateBtn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self._downloadUpdateBtn.setVisible(False)
        updateBarLayout.addWidget(self._downloadUpdateBtn)

        self._checkUpdateBtn = QPushButton(makeIcon("refresh-cw", QPalette.ColorRole.Text), None)
        self._checkUpdateBtn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        updateBarLayout.addWidget(self._checkUpdateBtn)

        layout.addLayout(updateBarLayout)

        self._updateStatusLabel = QLabel("")
        layout.addWidget(self._updateStatusLabel)

        layout.addStretch()

        self._tabWidget.addTab(tab, makeIcon("download", QPalette.ColorRole.Text, 14), "Update")

    def _createButtons(self) -> None:
        buttonLayout = QHBoxLayout()
        self._saveBtn = QPushButton("Save")
        self._backBtn = QPushButton("Back")
        buttonLayout.addWidget(self._backBtn)
        buttonLayout.addWidget(self._saveBtn)
        self._layout.addLayout(buttonLayout)

    def _connectSignals(self) -> None:
        self._addFolderBtn.clicked.connect(self._onAddFolder)
        self._removeFolderBtn.clicked.connect(self._onRemoveFolder)
        self._saveBtn.clicked.connect(self._onSave)
        self._backBtn.clicked.connect(self.backClicked)
        self._checkUpdateBtn.clicked.connect(self.checkForUpdates)
        self._downloadUpdateBtn.clicked.connect(self.downloadUpdate)
        self._installUpdateBtn.clicked.connect(self.installUpdate)

    def _onAddFolder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Media Folder")
        if folder:
            self._folderList.addItem(os.path.normpath(folder))

    def _onRemoveFolder(self) -> None:
        currentRow = self._folderList.currentRow()
        if currentRow >= 0:
            self._folderList.takeItem(currentRow)

    def _onSave(self) -> None:
        folders = [self._folderList.item(i).text() for i in range(self._folderList.count())]
        rawExtensions = self._extensionsInput.text()
        extensions = [ext.strip() for ext in rawExtensions.split(",") if ext.strip()]
        config = AppConfig(playlistConfig="", folders=folders, extensions=extensions)
        self.settingsSaved.emit(config)

    def setConfig(self, config: AppConfig) -> None:
        self._folderList.clear()
        for folder in config.folders:
            self._folderList.addItem(folder)
        self._extensionsInput.setText(", ".join(config.extensions))

    def setUpdateStatus(self, status: str) -> None:
        self._updateStatusLabel.setText(status)

    def setDownloadProgress(self, percent: int) -> None:
        self._downloadProgress.setVisible(True)
        self._downloadProgress.setValue(percent)

    def setDownloadAvailable(self, available: bool) -> None:
        self._downloadUpdateBtn.setVisible(available)
        self._checkUpdateBtn.setVisible(not available)

    def setInstallReady(self, ready: bool) -> None:
        self._downloadUpdateBtn.setVisible(False)
        self._downloadProgress.setVisible(False)
        self._installUpdateBtn.setVisible(ready)
