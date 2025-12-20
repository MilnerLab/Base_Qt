from __future__ import annotations
from typing import Callable
from PySide6.QtCore import QTimer

from base_core.framework.app.dispatcher import UiDispatcher  # depends on base_lib

class QtDispatcher(UiDispatcher):
    def post(self, fn: Callable[[], None]) -> None:
        QTimer.singleShot(0, fn)
