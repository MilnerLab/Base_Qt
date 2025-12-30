from __future__ import annotations

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from base_core.framework.events import EventBus
from base_core.framework.lifecycle.cleanup_collection import CleanupCollection
from base_qt.app.interfaces import IUiDispatcher
from base_qt.view_models.vm_base import VMBase


T = TypeVar("T")
P = ParamSpec("P")

def ui_thread(method: Callable[P, None]) -> Callable[P, None]:
    @wraps(method)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        self = args[0]  # bound method => first arg is self
        self.post_ui(lambda: method(*args, **kwargs))
    return wrapper

class ThreadSafeVMBase(VMBase):
    def __init__(self, ui: IUiDispatcher, bus: EventBus) -> None:
        super().__init__()
        self._ui = ui
        self._bus = bus
        self._cleanup = CleanupCollection()

    def post_ui(self, fn: Callable[[], None]) -> None:
        self._ui.post(fn)

    def sub_event(self, topic: str, handler: Callable[[T], None]) -> None:
        unsub = self._bus.subscribe(topic, handler)
        self._cleanup.add(unsub)

    def on_disconnect(self) -> None:
        self._cleanup.clear()
        super().on_disconnect()
