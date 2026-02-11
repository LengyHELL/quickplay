import os

os.environ["PATH"] = os.path.dirname("./_internal/libmpv-2.dll") + os.pathsep + os.environ["PATH"]
import mpv
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QPushButton, QVBoxLayout, QWidget


class Player(mpv.MPV):
    def __init__(self, wid: str) -> None:
        super().__init__(wid=wid, ytdl=True, input_cursor=True, input_default_bindings=True, input_vo_keyboard=True, osc=True)
        self.on_key_press("n")(self.nextItem)
        self.on_key_press("N")(self.nextChapter)
        self.on_key_press("p")(self.previousItem)
        self.on_key_press("P")(self.previousChapter)
        self.on_key_press("Ctrl+l")(self.showList)

    def loadEpisodes(self, episodes: list[str]) -> None:
        self.playlist_clear()
        for episode in episodes:
            self.playlist_append(episode)
        self.playlist_pos = 0

    def nextItem(self) -> None:
        if self.playlist_pos < len(self.playlist) - 1:
            self.playlist_next()

    def nextChapter(self) -> None:
        self.command("add", "chapter", "1")

    def previousItem(self) -> None:
        if self.playlist_pos > 0:
            self.playlist_prev()

    def previousChapter(self) -> None:
        self.command("add", "chapter", "-1")

    def showList(self) -> None:
        self.command("script-message", "osc-playlist")

    def startPlaylist(self) -> None:
        self.wait_until_playing()


class PlayerContainer(QWidget):
    player: Player
    keyboardKeys = {
        Qt.Key.Key_Backspace: "BS",
        Qt.Key.Key_PageUp: "PGUP",
        Qt.Key.Key_PageDown: "PGDWN",
        Qt.Key.Key_Home: "HOME",
        Qt.Key.Key_End: "END",
        Qt.Key.Key_Left: "LEFT",
        Qt.Key.Key_Up: "UP",
        Qt.Key.Key_Right: "RIGHT",
        Qt.Key.Key_Down: "DOWN",
        # ...
    }
    mouseKeys = {
        Qt.MouseButton.NoButton: None,
        Qt.MouseButton.LeftButton: "MOUSE_BTN0",
        Qt.MouseButton.MiddleButton: "MOUSE_BTN1",
        Qt.MouseButton.RightButton: "MOUSE_BTN2",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_DontCreateNativeAncestors)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    def _handleMouseEvent(self, event: QMouseEvent | None, release: bool = False) -> None:
        if event is not None:
            x = event.pos().x()
            y = event.pos().y()
            self.player.command("mouse", x, y)

            button = self.mouseKeys.get(event.button())
            if button is not None:
                self.player.command("keyup" if release else "keydown", button)

    def setPlayer(self, player: Player) -> None:
        self.player = player

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event.key() != Qt.Key.Key_Shift:
            key = self.keyboardKeys.get(event.key(), event.text())
            self.player.keypress(key)

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        self._handleMouseEvent(event)

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self._handleMouseEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        self._handleMouseEvent(event, True)

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        if event.angleDelta().y() < 0:
            self.player.keypress("MOUSE_BTN4")
        elif event.angleDelta().y() > 0:
            self.player.keypress("MOUSE_BTN3")


class VideoPlayer(QWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)

        self.videoPlayerLayout = QVBoxLayout()
        self.setLayout(self.videoPlayerLayout)

        self._createPlayer()
        self._createButtons()

    def _createPlayer(self) -> None:
        self.playerContainer = PlayerContainer()
        self.player = Player(str(int(self.playerContainer.winId())))
        self.playerContainer.setPlayer(self.player)
        self.videoPlayerLayout.addWidget(self.playerContainer)

    def _createButtons(self) -> None:
        self.buttonFrame = QFrame()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setVerticalSizeConstraint(QHBoxLayout.SizeConstraint.SetFixedSize)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.back = QPushButton("Back")
        self.buttonLayout.addWidget(self.back)
        self.buttonFrame.setLayout(self.buttonLayout)
        self.videoPlayerLayout.addWidget(self.buttonFrame)
