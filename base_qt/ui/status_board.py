from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from base_core.framework.app.service_status import ServiceStatus
from base_core.framework.events import EventBus
from base_qt.app.dispatcher import QtDispatcher


class StatusBoard(QWidget):
    """
    Persistent widget showing one status row per registered service.

    Each row: colored dot  |  service name  |  detail text

    Dots use object name "status_dot" with a "level" property so the
    stylesheet can colour them the same way as the StatusArea dot:
      running  → level "info"   (green)
      stopped  → level ""       (grey / neutral)
      error    → level "error"  (red)
    """

    def __init__(
        self,
        bus: EventBus,
        dispatcher: QtDispatcher,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._dispatcher = dispatcher
        self._rows: dict[str, _ServiceRow] = {}

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setHorizontalSpacing(8)
        self._layout.setVerticalSpacing(4)

        self._unsub: Callable = bus.subscribe(
            ServiceStatus,
            lambda e: dispatcher.post(lambda ev=e: self._on_status(ev)),
        )

    def register(self, name: str) -> None:
        if name in self._rows:
            return
        row_idx = len(self._rows)
        r = _ServiceRow(name)
        self._rows[name] = r
        self._layout.addWidget(r.dot,    row_idx, 0, Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(r.label,  row_idx, 1, Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(r.detail, row_idx, 2, Qt.AlignmentFlag.AlignVCenter)

    def _on_status(self, event: ServiceStatus) -> None:
        row = self._rows.get(event.name)
        if row is None:
            return
        if event.running:
            level = "info"
            detail = event.detail or "running"
        else:
            level = "error" if event.detail else ""
            detail = event.detail or "stopped"
        row.set_level(level)
        row.detail.setText(detail)

    def cleanup(self) -> None:
        self._unsub()


class _ServiceRow:
    def __init__(self, name: str) -> None:
        self.dot = QLabel()
        self.dot.setObjectName("status_dot")
        self.dot.setFixedSize(8, 8)

        self.label = QLabel(name)
        self.label.setObjectName("status_board_name")

        self.detail = QLabel("stopped")
        self.detail.setObjectName("status_board_detail")

        self.set_level("")

    def set_level(self, level: str) -> None:
        for w in (self.dot, self.label):
            w.setProperty("level", level)
            w.style().unpolish(w)
            w.style().polish(w)
