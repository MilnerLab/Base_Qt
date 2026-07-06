from __future__ import annotations

from functools import wraps
from typing import Callable

from PySide6.QtCore import QObject

from base_core.framework.events import EventBus
from base_qt.app.dispatcher import QtDispatcher
from base_qt.ui.app_message import AppMessage, MessageLevel


class PanelViewModel(QObject):
    """
    Base VM for a lab panel.

    Manages EventBus subscriptions (auto-cleared on close) and
    marshals callbacks to the Qt main thread via the dispatcher.
    All event handlers that touch Qt widgets must use @ui_thread.
    """

    def __init__(self, bus: EventBus, dispatcher: QtDispatcher) -> None:
        super().__init__()
        self._bus = bus
        self._dispatcher = dispatcher
        self._subs: list[Callable] = []

    def _sub(self, event_type: type, handler: Callable) -> None:
        unsub = self._bus.subscribe(event_type, handler)
        self._subs.append(unsub)

    def _post(self, fn: Callable[[], None]) -> None:
        self._dispatcher.post(fn)

    def _msg(self, text: str, level: MessageLevel = MessageLevel.INFO) -> None:
        self._bus.publish(AppMessage(text, level))

    def on_close(self) -> None:
        for unsub in self._subs:
            unsub()
        self._subs.clear()


def ui_thread(method: Callable) -> Callable:
    """
    Decorator: marshals a PanelViewModel method to the Qt main thread.
    The wrapped method runs asynchronously; return values are discarded.
    """
    @wraps(method)
    def wrapper(self: PanelViewModel, *args, **kwargs) -> None:
        self._post(lambda: method(self, *args, **kwargs))
    return wrapper
