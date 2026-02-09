from PyQt6.QtCore import QModelIndex, QSize, Qt
from PyQt6.QtGui import QIcon, QPainter, QPalette, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLineEdit, QListView, QMainWindow, QPushButton, QScrollBar, QStyle, QStyledItemDelegate, QStyleOptionViewItem, QVBoxLayout, QWidget


class EpisodeItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QListView) -> None:
        super().__init__(parent)
        self.icon_size = 16
        self.icon_spacing = 4

    def paint(self, painter: QPainter | None, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()

        style = QApplication.style()
        option.decorationSize = QSize(0, 0)
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, None)

        textColor = option.palette.text()

        if option.state & QStyle.StateFlag.State_Selected:
            textColor = option.palette.highlightedText()

            accentColor = option.palette.color(QPalette.ColorRole.Accent)
            focusHMargin = style.pixelMetric(QStyle.PixelMetric.PM_FocusFrameHMargin)
            indicatorWidth = style.pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth)
            indicatorHeight = style.pixelMetric(QStyle.PixelMetric.PM_IndicatorHeight)
            vOffset = (option.rect.height() - indicatorHeight) // 2
            indicatorRect = option.rect.adjusted(focusHMargin, vOffset, -option.rect.width() + focusHMargin + indicatorWidth, -vOffset)
            painter.fillRect(indicatorRect, accentColor)

        text_offset = self.icon_size + self.icon_spacing * 2
        option.rect = option.rect.adjusted(text_offset, 0, 0, 0)

        text = index.data(Qt.ItemDataRole.DisplayRole)
        painter.setPen(textColor.color())
        painter.drawText(option.rect, Qt.AlignmentFlag.AlignVCenter, text)

        painter.restore()

        icon: QIcon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon:
            icon_x = option.rect.left() - text_offset + self.icon_spacing
            icon_y = option.rect.top() + (option.rect.height() - self.icon_size) // 2
            painter.drawPixmap(icon_x, icon_y, self.icon_size, self.icon_size, icon.pixmap(self.icon_size, self.icon_size))

    def sizeHint(self, option: QStyleOptionViewItem, index: int) -> QSize:
        return super().sizeHint(option, index)


class EpisodeSelect(QWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)

        self.episodeSelectLayout = QVBoxLayout()
        self.setLayout(self.episodeSelectLayout)

        self._createSearch()
        self._createEpisodeList()
        self._createButtons()

    def _createSearch(self) -> None:
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self.episodeSelectLayout.addWidget(self.search)

    def _createEpisodeList(self) -> None:
        self.listModel = QStandardItemModel()
        self.scrollBar = QScrollBar()
        self.list = QListView()
        self.list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.list.setVerticalScrollBar(self.scrollBar)
        self.list.setModel(self.listModel)
        self.list.setItemDelegate(EpisodeItemDelegate(self.list))
        self.episodeSelectLayout.addWidget(self.list)

    def _createButtons(self) -> None:
        self.buttonLayout = QHBoxLayout()
        self.back = QPushButton("Back")
        self.startAll = QPushButton("Start All")
        self.start = QPushButton("Start")
        self.buttonLayout.addWidget(self.back)
        self.buttonLayout.addWidget(self.startAll)
        self.buttonLayout.addWidget(self.start)
        self.episodeSelectLayout.addLayout(self.buttonLayout)
