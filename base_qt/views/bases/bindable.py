from __future__ import annotations
from abc import abstractmethod
from typing import Generic, Optional, TypeVar

from base_qt.app.qt_cleanup_collection import QtCleanupCollection


VM = TypeVar("VM")

class BindableMixin(Generic[VM]):
    def __init_bindable__(self, vm: VM) -> None:
        self._vm: VM = vm
        self._bound: bool = False
        self._cleanup = QtCleanupCollection()

    @property
    def vm(self) -> VM:
        return self._vm

    @classmethod
    @abstractmethod
    def id(cls) -> str:
        ...
    
    def bind(self) -> None:
        if self._bound:
            return
        self._bound = True

    def unbind(self) -> None:
        self._cleanup.clear()
        self._bound = False

    def connect_binding(self, signal, slot) -> None:
        self._cleanup.connect(signal, slot)

    def _ensure_bound(self) -> None:
        if not self._bound:
            self.bind()

    def _ensure_unbound(self) -> None:
        if self._bound:
            self.unbind()
