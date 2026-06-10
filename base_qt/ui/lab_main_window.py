from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDockWidget, QMainWindow, QWidget

from base_core.framework.events import EventBus
from base_qt.app.dispatcher import QtDispatcher
from base_qt.ui.app_message import AppMessage
from base_qt.ui.status_area import StatusArea


class LabMainWindow(QMainWindow):
    """
    Base shell for all lab applications.

    Standard menu order (left to right): File | Panels | Settings
    Apps add their own menus after calling super().__init__().

      File     → Exit
      Panels   → one checkable entry per register_panel() call
      Settings → empty by default; extend via self.menu_settings

    The right side of the menu bar shows a StatusArea that collects
    warnings and errors in a navigable list.  INFO messages appear
    transiently for 6 s.  Any VM can post messages via self._msg().

    Usage:
        class MyShell(LabMainWindow):
            def __init__(self, bus, dispatcher):
                super().__init__("My App", bus, dispatcher)
                self.resize(1400, 900)
                install_ui(QApplication.instance())
                self.register_panel("Spectrum", panel, Qt.LeftDockWidgetArea)
                self.menuBar().addMenu("Devices").addAction("Settings…", ...)
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
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks
            | QMainWindow.DockOption.AllowNestedDocks
            | QMainWindow.DockOption.AllowTabbedDocks
        )

        mb = self.menuBar()
        self._menu_file    = mb.addMenu("File")
        self._menu_panels  = mb.addMenu("Panels")
        self.menu_settings = mb.addMenu("Settings")
        self._menu_file.addAction("Exit", self.close)

        self._status = StatusArea()
        mb.setCornerWidget(self._status, Qt.Corner.TopRightCorner)

        self._unsub_msg: Callable = bus.subscribe(
            AppMessage,
            lambda msg: dispatcher.post(lambda m=msg: self._status.push(m)),
        )

    # ------------------------------------------------------------------
    # Panel registration
    # ------------------------------------------------------------------

    def register_panel(
        self,
        title: str,
        widget: QWidget,
        area: Qt.DockWidgetArea = Qt.DockWidgetArea.LeftDockWidgetArea,
        *,
        floating: bool = False,
    ) -> QDockWidget:
        """
        Wrap widget in a dock, add it to the window, and add a checkable
        toggle action to the Panels menu.  Returns the QDockWidget.
        """
        dock = QDockWidget(title, self)
        dock.setObjectName(title)
        dock.setWidget(widget)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        # When a dock is floating, give it Qt.Window type so Linux/XCB can
        # move it without hitting the "mouse grab only for popups" restriction.
        def _on_top_level_changed(is_floating: bool) -> None:
            if is_floating:
                dock.setWindowFlags(Qt.WindowType.Window)
                dock.show()

        dock.topLevelChanged.connect(_on_top_level_changed)

        self.addDockWidget(area, dock)
        if floating:
            dock.setFloating(True)
            dock.setWindowFlags(Qt.WindowType.Window)
            dock.show()
        self._menu_panels.addAction(dock.toggleViewAction())
        return dock

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        self._unsub_msg()
        super().closeEvent(event)
