from __future__ import annotations
from typing import Any, Callable

from base_core.framework.lifecycle.cleanup_collection import CleanupCollection



class QtCleanupCollection(CleanupCollection):
    def connect(self, signal: Any, slot: Callable[..., Any]) -> None:
        signal.connect(slot)
        self.add(lambda s=signal, f=slot: _safe_disconnect(s, f))

def _safe_disconnect(signal: Any, slot: Callable[..., Any]) -> None:
    try:
        signal.disconnect(slot)
    except (TypeError, RuntimeError):
        pass
