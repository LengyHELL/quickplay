from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from views.video_player import VideoPlayer


class PlayerPage(QWidget):
    stopRequested = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._createPlayer()
        self._createButtons()

    def _createPlayer(self) -> None:
        self.player = VideoPlayer()
        self._layout.addWidget(self.player)

    def _createButtons(self) -> None:
        self._buttonFrame = QFrame()
        buttonLayout = QHBoxLayout()
        buttonLayout.setVerticalSizeConstraint(QHBoxLayout.SizeConstraint.SetFixedSize)
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        back = QPushButton("Back")
        back.clicked.connect(self.stopRequested)
        buttonLayout.addWidget(back)
        self._buttonFrame.setLayout(buttonLayout)
        self._layout.addWidget(self._buttonFrame)

    def setControlsVisible(self, visible: bool) -> None:
        if visible:
            self._buttonFrame.show()
            self._layout.unsetContentsMargins()
        else:
            self._buttonFrame.hide()
            self._layout.setContentsMargins(0, 0, 0, 0)
