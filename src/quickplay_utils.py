from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPainter, QPalette, QPixmap
from PyQt6.QtSvg import QSvgRenderer


class QuickPlayUtil:
    @staticmethod
    def getStyleSheet(path: str) -> None:
        content = ""
        with open(path, "r", encoding="utf-8") as styles:
            content = styles.read()

        return content

    @staticmethod
    def icon(name: str, color: QPalette.ColorRole, size: int = 24) -> QIcon:
        palette = QPalette()
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer = QSvgRenderer(f"_internal/icons/{name}.svg")
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), palette.color(color))
        painter.end()

        return QIcon(pixmap)
