from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QListView, QMainWindow, QPushButton, QScrollBar, QVBoxLayout, QWidget


class TitleSelect(QWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)

        self.titleSelectLayout = QVBoxLayout()
        self.setLayout(self.titleSelectLayout)

        self._createSearch()
        self._createTitleList()
        self._createButtons()

    def _createSearch(self) -> None:
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self.titleSelectLayout.addWidget(self.search)

    def _createTitleList(self) -> None:
        self.listModel = QStringListModel()
        self.scrollBar = QScrollBar()
        self.list = QListView()
        self.list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.list.setVerticalScrollBar(self.scrollBar)
        self.list.setModel(self.listModel)
        self.titleSelectLayout.addWidget(self.list)

    def _createButtons(self) -> None:
        self.buttonLayout = QHBoxLayout()
        self.startPrevious = QPushButton("Start previous")
        self.next = QPushButton("Next")
        self.buttonLayout.addWidget(self.startPrevious)
        self.buttonLayout.addWidget(self.next)
        self.titleSelectLayout.addLayout(self.buttonLayout)
