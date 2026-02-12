from PyQt6.QtCore import QModelIndex, QSize, QSortFilterProxyModel, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QPalette, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QListView,
    QPushButton,
    QScrollBar,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from models.episode import Episode
from utils import makeIcon


class EpisodeItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QListView) -> None:
        super().__init__(parent)
        self.iconSize = 12
        self.iconSpacing = 4

    def paint(self, painter: QPainter | None, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()

        style = QApplication.style()
        option.decorationSize = QSize(0, 0)
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, None)

        if option.state & QStyle.StateFlag.State_Selected:
            accentColor = option.palette.color(QPalette.ColorRole.Accent)
            focusHMargin = style.pixelMetric(QStyle.PixelMetric.PM_FocusFrameHMargin)
            indicatorWidth = style.pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth)
            indicatorHeight = style.pixelMetric(QStyle.PixelMetric.PM_IndicatorHeight)
            vOffset = (option.rect.height() - indicatorHeight) // 2
            indicatorRect = option.rect.adjusted(
                focusHMargin, vOffset, -option.rect.width() + focusHMargin + indicatorWidth, -vOffset
            )
            painter.fillRect(indicatorRect, accentColor)

        text_offset = self.iconSize + self.iconSpacing * 2
        option.rect = option.rect.adjusted(text_offset, 0, 0, 0)

        text = index.data(Qt.ItemDataRole.DisplayRole)
        painter.setPen(option.palette.text().color())
        painter.drawText(option.rect, Qt.AlignmentFlag.AlignVCenter, text)

        painter.restore()

        icon: QIcon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon:
            icon_x = option.rect.left() - text_offset + self.iconSpacing
            icon_y = option.rect.top() + (option.rect.height() - self.iconSize) // 2
            painter.drawPixmap(icon_x, icon_y, self.iconSize, self.iconSize, icon.pixmap(self.iconSize, self.iconSize))

    def sizeHint(self, option: QStyleOptionViewItem, index: int) -> QSize:
        return super().sizeHint(option, index)


class EpisodeSelect(QWidget):
    episodesSelected = pyqtSignal(list)
    backClicked = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._episodes: list[Episode] = []

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._createSearch()
        self._createEpisodeList()
        self._createButtons()
        self._connectSignals()

    def _createSearch(self) -> None:
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search")
        self._layout.addWidget(self._search)

    def _createEpisodeList(self) -> None:
        self._sourceModel = QStandardItemModel()
        self._proxyModel = QSortFilterProxyModel()
        self._proxyModel.setSourceModel(self._sourceModel)
        self._proxyModel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self._scrollBar = QScrollBar()
        self._list = QListView()
        self._list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self._list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self._list.setVerticalScrollBar(self._scrollBar)
        self._list.setModel(self._proxyModel)
        self._list.setItemDelegate(EpisodeItemDelegate(self._list))
        self._layout.addWidget(self._list)

    def _createButtons(self) -> None:
        buttonLayout = QHBoxLayout()
        self._back = QPushButton("Back")
        self._startAll = QPushButton("Start All")
        self._start = QPushButton("Start")
        buttonLayout.addWidget(self._back)
        buttonLayout.addWidget(self._startAll)
        buttonLayout.addWidget(self._start)
        self._layout.addLayout(buttonLayout)

    def _connectSignals(self) -> None:
        self._search.textChanged.connect(self._proxyModel.setFilterFixedString)
        self._back.clicked.connect(self.backClicked)
        self._startAll.clicked.connect(self._onStartAllClicked)
        self._start.clicked.connect(self._onStartClicked)
        self._list.doubleClicked.connect(self._onStartClicked)
        self._list.selectionModel().selectionChanged.connect(self._updateButtonState)
        self._updateButtonState()

    def _updateButtonState(self) -> None:
        self._start.setDisabled(len(self._list.selectedIndexes()) <= 0)

    def _onStartAllClicked(self) -> None:
        self.episodesSelected.emit(self._episodes)

    def _onStartClicked(self) -> None:
        indexes = self._list.selectedIndexes()
        if not indexes:
            return

        selected = []
        for idx in indexes:
            source_idx = self._proxyModel.mapToSource(idx)
            selected.append(self._episodes[source_idx.row()])
        self.episodesSelected.emit(selected)

    def setEpisodes(self, episodes: list[Episode]) -> None:
        self._episodes = episodes
        self._sourceModel.clear()
        self._search.clear()
        unseen = makeIcon("circle", QPalette.ColorRole.PlaceholderText)
        inProgress = makeIcon("clock", QPalette.ColorRole.Text)
        completed = makeIcon("check-circle", QPalette.ColorRole.BrightText)
        for episode in episodes:
            icon = completed if episode.completed else inProgress if episode.progress > 0 else unseen
            item = QStandardItem(icon, episode.name)
            self._sourceModel.appendRow(item)
