from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from base_qt.ui.panel_view_model import PanelViewModel


class Panel(QWidget):
    """
    Base widget for all lab panels.

    Layout:
        QLabel#panel_header  (styled title strip)
        self.body            (content area — add widgets to self.body_layout)

    Usage:
        class MyPanel(Panel):
            def setup(self) -> None:
                self.body_layout.addWidget(QLabel("Hello"))
                self._connect(self.vm.some_signal, self._on_something)
    """

    def __init__(self, title: str, vm: PanelViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.__dict__["vm"] = vm
        self._sigs: list[tuple] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header = QLabel(title)
        self._header.setObjectName("panel_header")
        root.addWidget(self._header)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(8, 8, 8, 8)
        self.body_layout.setSpacing(8)
        root.addWidget(self.body, stretch=1)

        self.setup()

    @property
    def vm(self) -> PanelViewModel:
        return self.__dict__["vm"]

    def setup(self) -> None:
        """Override: create and add widgets to self.body_layout."""

    def _connect(self, signal: Any, slot: Callable) -> None:
        """Connect a signal and automatically disconnect it when the panel closes."""
        signal.connect(slot)
        self._sigs.append((signal, slot))

    def closeEvent(self, event: QCloseEvent) -> None:
        for sig, slot in self._sigs:
            try:
                sig.disconnect(slot)
            except RuntimeError:
                pass
        self.vm.on_close()
        super().closeEvent(event)
