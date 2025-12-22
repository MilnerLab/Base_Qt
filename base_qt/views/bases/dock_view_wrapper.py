from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QWidget


class DockHostWidget(QDockWidget):
    def __init__(self, *, title: str, content: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        self.setWidget(content)
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea
        )
