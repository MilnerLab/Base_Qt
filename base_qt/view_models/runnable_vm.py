from __future__ import annotations

from typing import Generic, TypeVar

from base_core.framework.domain.interfaces import IRunnable
from base_qt.view_models.runnable_vm import IUiDispatcher  
from .thread_safe_vm_base import ThreadSafeVMBase
from base_core.framework.events.event_bus import EventBus

TService = TypeVar("TService", bound=IRunnable)


class RunnableVMBase(ThreadSafeVMBase, Generic[TService]):
    def __init__(self, engine_service: TService, ui: IUiDispatcher, bus: EventBus):
        super().__init__(ui, bus)
        self._engine: TService = engine_service

    @property
    def engine(self) -> TService:
        return self._engine

    def start(self) -> None:
        self._engine.start()

    def stop(self) -> None:
        self._engine.stop()

    def reset(self) -> None:
        self._engine.reset()
        
    def disconnect(self):
        self.stop()
        super().disconnect()
