import locale
import sys

from PyQt6.QtWidgets import (
    QApplication,
)

from quickplay_controller import QuickplayController
from quickplay_model import QuickplayModel
from quickplay_utils import QuickPlayUtil
from quickplay_view import QuickplayView


def main() -> None:
    locale.setlocale(locale.LC_NUMERIC, "C")

    app = QApplication(sys.argv)
    app.setStyleSheet(QuickPlayUtil.getStyleSheet("_internal/styles.qss"))

    view = QuickplayView()
    view.show()

    model = QuickplayModel()

    QuickplayController(model, view)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
