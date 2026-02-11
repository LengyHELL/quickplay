import os

os.environ["PATH"] = os.path.dirname("./_internal/libmpv-2.dll") + os.pathsep + os.environ["PATH"]
import mpv
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QPushButton, QVBoxLayout, QWidget


class Player(QWidget):
    isFullscreen = pyqtSignal(bool)
    quitEvent = pyqtSignal()

    player: mpv.MPV

    keyboardKeys: dict[Qt.Key, str] = {
        Qt.Key.Key_Escape: "ESC",
        Qt.Key.Key_Tab: "TAB",
        Qt.Key.Key_Backspace: "BS",
        Qt.Key.Key_Return: "ENTER",
        Qt.Key.Key_Enter: "ENTER",
        Qt.Key.Key_Insert: "INS",
        Qt.Key.Key_Delete: "DEL",
        Qt.Key.Key_Home: "HOME",
        Qt.Key.Key_End: "END",
        Qt.Key.Key_PageUp: "PGUP",
        Qt.Key.Key_PageDown: "PGDWN",
        Qt.Key.Key_Left: "LEFT",
        Qt.Key.Key_Up: "UP",
        Qt.Key.Key_Right: "RIGHT",
        Qt.Key.Key_Down: "DOWN",
        Qt.Key.Key_Space: "SPACE",
        Qt.Key.Key_F1: "F1",
        Qt.Key.Key_F2: "F2",
        Qt.Key.Key_F3: "F3",
        Qt.Key.Key_F4: "F4",
        Qt.Key.Key_F5: "F5",
        Qt.Key.Key_F6: "F6",
        Qt.Key.Key_F7: "F7",
        Qt.Key.Key_F8: "F8",
        Qt.Key.Key_F9: "F9",
        Qt.Key.Key_F10: "F10",
        Qt.Key.Key_F11: "F11",
        Qt.Key.Key_F12: "F12",
    }

    mouseKeys: dict[Qt.MouseButton, str] = {
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
        self._initCursorTimer()
        self._initPlayer()

    def __del__(self) -> None:
        print("Video player destroyed.")
        super().__del__(self)

    def _initPlayer(self) -> None:
        self.player = mpv.MPV(wid=str(int(self.winId())), ytdl=True, input_cursor=True, input_default_bindings=True, input_vo_keyboard=True, osc=True)
        self.player.on_key_press("n")(self._nextItem)
        self.player.on_key_press("N")(self._nextChapter)
        self.player.on_key_press("p")(self._previousItem)
        self.player.on_key_press("P")(self._previousChapter)
        self.player.on_key_press("Ctrl+l")(self._showList)
        for key in ("q", "Q", "POWER", "STOP", "CLOSE_WIN"):
            self.player.on_key_press(key)(self.quitEvent.emit)
        self.player.observe_property("fullscreen", lambda _, value: self.isFullscreen.emit(value))
        self.player.observe_property("idle-active", lambda _, value: value and self.quitEvent.emit())

    def _initCursorTimer(self) -> None:
        self.cursorTimer = QTimer(self)
        self.cursorTimer.setSingleShot(True)
        self.cursorTimer.setInterval(1000)
        self.cursorTimer.timeout.connect(lambda: self.setCursor(Qt.CursorShape.BlankCursor))

    def _nextItem(self) -> None:
        if self.player.playlist_pos < len(self.player.playlist) - 1:
            self.player.playlist_next()

    def _nextChapter(self) -> None:
        try:
            self.player.command("add", "chapter", "1")
        except SystemError:
            print("No chapters in video.")

    def _previousItem(self) -> None:
        if self.player.playlist_pos > 0:
            self.player.playlist_prev()

    def _previousChapter(self) -> None:
        try:
            self.player.command("add", "chapter", "-1")
        except SystemError:
            print("No chapters in video.")

    def _showList(self) -> None:
        self.player.command("script-message", "osc-playlist")

    def _modifierPrefix(self, mods: Qt.KeyboardModifier) -> str:
        prefix = ""
        if mods & Qt.KeyboardModifier.ShiftModifier:
            prefix += "Shift+"
        if mods & Qt.KeyboardModifier.ControlModifier:
            prefix += "Ctrl+"
        if mods & Qt.KeyboardModifier.AltModifier:
            prefix += "Alt+"
        if mods & Qt.KeyboardModifier.MetaModifier:
            prefix += "Meta+"
        return prefix

    def _handleMouseEvent(self, event: QMouseEvent | None, release: bool = False) -> None:
        if event is None:
            return

        x = event.pos().x()
        y = event.pos().y()
        self.player.command("mouse", x, y)

        button = self.mouseKeys.get(event.button())
        if button is not None:
            prefix = self._modifierPrefix(event.modifiers())
            self.player.command("keyup" if release else "keydown", prefix + button)

    def loadEpisodes(self, episodes: list[str]) -> None:
        self.player.keypress("ESC")
        self.player.stop()
        self.player.playlist_clear()

        for episode in episodes:
            self.player.playlist_append(episode)

    def start(self, index: int | None = None) -> None:
        if index is not None:
            self.player.playlist_pos = index

        self.player.pause = False

    def stop(self) -> None:
        self.player.pause = True

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            return

        mods: Qt.KeyboardModifier = event.modifiers()
        prefix: str = self._modifierPrefix(mods)

        key: str | None = None
        if event.key() in self.keyboardKeys:
            key = prefix + self.keyboardKeys[event.key()]
        elif mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            if Qt.Key.Key_A <= event.key() <= Qt.Key.Key_Z:
                key = prefix + chr(event.key()).lower()
            elif Qt.Key.Key_0 <= event.key() <= Qt.Key.Key_9:
                key = prefix + chr(event.key())
        elif event.text():
            key = event.text()

        if key is not None:
            self.player.keypress(key)

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        self.unsetCursor()
        self.cursorTimer.start()
        self._handleMouseEvent(event)

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self._handleMouseEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        self._handleMouseEvent(event, True)

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        prefix = self._modifierPrefix(event.modifiers())
        if event.angleDelta().y() < 0:
            self.player.keypress(prefix + "MOUSE_BTN4")
        elif event.angleDelta().y() > 0:
            self.player.keypress(prefix + "MOUSE_BTN3")


class VideoPlayer(QWidget):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)

        self.videoPlayerLayout = QVBoxLayout()
        self.setLayout(self.videoPlayerLayout)

        self._createPlayer()
        self._createButtons()

    def _createPlayer(self) -> None:
        self.player = Player()
        self.videoPlayerLayout.addWidget(self.player)

    def _createButtons(self) -> None:
        self.buttonFrame = QFrame()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setVerticalSizeConstraint(QHBoxLayout.SizeConstraint.SetFixedSize)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.back = QPushButton("Back")
        self.buttonLayout.addWidget(self.back)
        self.buttonFrame.setLayout(self.buttonLayout)
        self.videoPlayerLayout.addWidget(self.buttonFrame)
