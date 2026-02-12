from PyQt6.QtCore import QSortFilterProxyModel, Qt, pyqtSignal
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QListView, QPushButton, QScrollBar, QVBoxLayout, QWidget

from models.title import Title

TITLE_VALUE_ROLE = Qt.ItemDataRole.UserRole + 1


class TitleSelect(QWidget):
    titleSelected = pyqtSignal(Title)
    startPreviousClicked = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._createSearch()
        self._createTitleList()
        self._createButtons()
        self._connectSignals()

    def _createSearch(self) -> None:
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search")
        self._layout.addWidget(self._search)

    def _createTitleList(self) -> None:
        self._sourceModel = QStandardItemModel()
        self._proxyModel = QSortFilterProxyModel()
        self._proxyModel.setSourceModel(self._sourceModel)
        self._proxyModel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self._scrollBar = QScrollBar()
        self._list = QListView()
        self._list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self._list.setVerticalScrollBar(self._scrollBar)
        self._list.setModel(self._proxyModel)
        self._layout.addWidget(self._list)

    def _createButtons(self) -> None:
        buttonLayout = QHBoxLayout()
        self._startPrevious = QPushButton("Start previous")
        self._next = QPushButton("Next")
        buttonLayout.addWidget(self._startPrevious)
        buttonLayout.addWidget(self._next)
        self._layout.addLayout(buttonLayout)

    def _connectSignals(self) -> None:
        self._search.textChanged.connect(self._proxyModel.setFilterFixedString)
        self._next.clicked.connect(self._onNextClicked)
        self._startPrevious.clicked.connect(self.startPreviousClicked)
        self._list.doubleClicked.connect(self._onNextClicked)
        self._list.selectionModel().selectionChanged.connect(self._updateButtonState)
        self._updateButtonState()

    def _updateButtonState(self) -> None:
        self._next.setDisabled(len(self._list.selectedIndexes()) <= 0)

    def _onNextClicked(self) -> None:
        indexes = self._list.selectedIndexes()
        if not indexes:
            return

        source_index = self._proxyModel.mapToSource(indexes[0])
        item = self._sourceModel.item(source_index.row())
        title: Title = item.data(TITLE_VALUE_ROLE)
        self.titleSelected.emit(title)

    def setTitles(self, titles: list[Title]) -> None:
        self._sourceModel.clear()
        for title in titles:
            item = QStandardItem(title.name)
            item.setData(title, TITLE_VALUE_ROLE)
            self._sourceModel.appendRow(item)

    def hasSelection(self) -> bool:
        return len(self._list.selectedIndexes()) > 0
