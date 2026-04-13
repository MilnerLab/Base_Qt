from __future__ import annotations

from typing import Callable, Optional

from base_core.framework.events import EventBus
from base_qt.app.interfaces import IUiDispatcher
from base_qt.events.view_events import OpenViewRequested
from base_qt.view_models.thread_safe_vm_base import ThreadSafeVMBase, ui_thread

from PySide6.QtCore import Signal


class MainWindowViewModelBase(ThreadSafeVMBase):
    """
    Generic main-window VM that reacts to OpenViewRequested events and
    delegates the actual opening to the view through a callback.
    """
    open_view_requested = Signal(str)
    
    def __init__(self, ui: IUiDispatcher, bus: EventBus) -> None:
        super().__init__(ui=ui, bus=bus)
        self._open_view_callback: Optional[Callable[[str], None]] = None

    def on_connect(self) -> None:
        super().on_connect()
        self.sub_event(OpenViewRequested, self._on_open_view_requested)

    @ui_thread
    def _on_open_view_requested(self, event: OpenViewRequested) -> None:
            self.open_view_requested.emit(event.view_id)