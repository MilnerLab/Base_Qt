from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import QDockWidget, QMainWindow, QWidget


class PanelWindow(QMainWindow):
    """
    Base class for the application's companion panel window.

    Hosts dockable panels created on demand from factories.  The window
    cannot be closed by the user — only the main window (AppShell) can
    destroy it.  Individual panels are closeable and reopen-able via the
    Panels menu.

    Usage:
        class MyPanelWindow(PanelWindow):
            def __init__(self, container, bus, dispatcher):
                super().__init__("My Panels")
                self.register_panel("Spectrum",
                    lambda: SpectrumPanel(SpectrumVM(bus, d, svc, buf)))
    """

    def __init__(self, title: str = "Panels") -> None:
        super().__init__()
        self.setWindowTitle(title)
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks
            | QMainWindow.DockOption.AllowNestedDocks
            | QMainWindow.DockOption.AllowTabbedDocks
        )
        self._menu_panels = self.menuBar().addMenu("Panels")

    # ------------------------------------------------------------------
    # Uncloseable — only AppShell.closeEvent may call destroy()
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()

    # ------------------------------------------------------------------
    # Panel registration
    # ------------------------------------------------------------------

    def register_panel(
        self,
        title: str,
        factory: Callable[[], QWidget],
        area: Qt.DockWidgetArea = Qt.DockWidgetArea.LeftDockWidgetArea,
        *,
        floating: bool = False,
    ) -> QDockWidget:
        """
        Wrap factory in a managed dock and add a toggle to the Panels menu.

        factory is called each time the dock is opened after being closed.
        The returned widget's vm.on_close() is called on close so subscriptions
        and buffer consumers are cleaned up automatically.
        """
        dock = _ManagedDock(title, factory, self)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

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


class _ManagedDock(QDockWidget):
    """
    QDockWidget that creates its content from a factory on open and
    destroys it (calling vm.on_close()) on close.
    """

    def __init__(
        self,
        title: str,
        factory: Callable[[], QWidget],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, parent)
        self.setObjectName(title)
        self._factory = factory
        self._open()

    def _open(self) -> None:
        self.setWidget(self._factory())

    def closeEvent(self, event: QCloseEvent) -> None:
        widget = self.widget()
        if widget is not None:
            widget.close()      # Panel.closeEvent → vm.on_close()
            self.setWidget(None)
        super().closeEvent(event)

    def showEvent(self, event: QShowEvent) -> None:
        if self.widget() is None:
            self._open()
        super().showEvent(event)
