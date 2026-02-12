import re
from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter, ArgumentParser

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPainter, QPalette, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from models.app_config import AppConfig


def parseArguments() -> AppConfig:
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
        default="_internal/quickplay.json",
        help="The playlist config text file used for storing playlist elements.",
        metavar="FILE",
    )
    parser.add_argument(
        "-s",
        "--status",
        dest="statusFile",
        default="quickplay.json",
        help="The status config text file generated for each folder to store status information.",
        metavar="FILE",
    )
    parser.add_argument(
        "-x",
        "--extensions",
        dest="extensions",
        default=".mkv, .mp4",
        help='The extensions to include when searching the directories. (eg.: ".mkv, .mp4, .mov")',
        metavar="LIST",
    )

    args = parser.parse_args()
    extensions = re.sub(r"\s", "", args.extensions).split(",")
    return AppConfig(args.folderFile, args.playlistFile, args.statusFile, extensions)


def getStylesheet(path: str) -> str:
    with open(path, "r", encoding="utf-8") as styles:
        return styles.read()


def makeIcon(name: str, color: QPalette.ColorRole, size: int = 24) -> QIcon:
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
