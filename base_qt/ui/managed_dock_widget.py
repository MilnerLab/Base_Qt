from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDockWidget, QWidget


class ManagedDockWidget(QDockWidget):
    def __init__(
        self,
        dock_id: str,
        title: str,
        parent: QWidget | None = None,
        *,
        destroy_on_close: bool,
        on_destroy_requested: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(title, parent)
        self._dock_id = dock_id
        self._destroy_on_close = destroy_on_close
        self._on_destroy_requested = on_destroy_requested

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self._destroy_on_close:
            event.ignore()
            self.hide()
            return

        content = self.widget()
        if content is not None:
            if not content.close():
                event.ignore()
                return

        if self._on_destroy_requested is not None:
            self._on_destroy_requested(self._dock_id)

        super().closeEvent(event)