from __future__ import annotations

from typing import Generic, Optional, TypeVar
from PySide6.QtWidgets import QWidget

from .bindable import BindableMixin

VM = TypeVar("VM")


class ViewBase(QWidget, BindableMixin[VM], Generic[VM]):
    def __init__(self, vm: VM, parent: Optional[QWidget] = None) -> None:
        QWidget.__init__(self, parent)
        self.__init_bindable__(vm)
        self.build_ui()
        self.bind()

    def closeEvent(self, event) -> None:
        try:
            self._ensure_unbound()
        finally:
            super().closeEvent(event)
