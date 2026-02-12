import simplejson as json
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPainter, QPalette, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from episode import Episode, EpisodeConfig


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

    @staticmethod
    def loadEpisodes(filePath: str) -> EpisodeConfig:
        with open(filePath, "r", encoding="utf-8") as file:
            data = json.loads(file.read())
            episodes = [Episode(**e) for e in data["episodes"]]
            return EpisodeConfig(data["index"], episodes)

    @staticmethod
    def saveEpisodes(filePath: str, config: EpisodeConfig) -> None:
        with open(filePath, "w", encoding="utf-8") as file:
            data = {"index": config.index, "episodes": [e.__dict__ for e in config.episodes]}
            file.write(json.dumps(data, indent=2))
