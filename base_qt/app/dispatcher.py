from __future__ import annotations
from typing import Callable, Optional, Protocol

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication
from base_qt.app.interfaces import IUiDispatcher


class QtDispatcher(IUiDispatcher):
    def __init__(self, context: Optional[QObject] = None):
        self._ctx = context or QApplication.instance()
        if self._ctx is None:
            raise RuntimeError("QApplication existiert noch nicht")

    def post(self, fn: Callable[[], None]) -> None:
        QTimer.singleShot(0, self._ctx, fn)
