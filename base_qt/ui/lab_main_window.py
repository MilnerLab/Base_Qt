from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QWidget

from base_core.framework.events import EventBus
from base_qt.app.dispatcher import QtDispatcher
from base_qt.ui.app_message import AppMessage
from base_qt.ui.status_area import StatusArea


class LabMainWindow(QMainWindow):
    """
    Base class for the application's main window.

    Provides:
      - File → Exit menu
      - Settings menu (empty by default; extend via self.menu_settings)
      - StatusArea corner widget that collects app messages from the EventBus
      - self._bus / self._dispatcher for subclasses

    Does NOT manage dockable panels — that responsibility belongs to PanelWindow.
    """

    def __init__(
        self,
        title: str,
        bus: EventBus,
        dispatcher: QtDispatcher,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self._bus = bus
        self._dispatcher = dispatcher

        mb = self.menuBar()
        self._menu_file    = mb.addMenu("File")
        self.menu_settings = mb.addMenu("Settings")
        self._menu_file.addAction("Exit", self.close)

        self._status = StatusArea()
        mb.setCornerWidget(self._status, Qt.Corner.TopRightCorner)

        self._unsub_msg: Callable = bus.subscribe(
            AppMessage,
            lambda msg: dispatcher.post(lambda m=msg: self._status.push(m)),
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        self._unsub_msg()
        super().closeEvent(event)
