from __future__ import annotations
from typing import Any, Callable

from base_core.framework.events import EventBus
from base_core.framework.app.dispatcher import UiDispatcher

def subscribe_ui(events: EventBus, ui: UiDispatcher, topic: str, handler: Callable[[Any], None]) -> Callable[[], None]:
    """
    Subscribe to `topic` but always run handler on UI thread.
    """
    def wrapped(payload: Any) -> None:
        ui.post(lambda: handler(payload))
    return events.subscribe(topic, wrapped)
