from __future__ import annotations

from typing import Generic, Optional, TypeVar
from PySide6.QtWidgets import QMenuBar, QWidget

from .bindable import BindableMixin

VM = TypeVar("VM")


class MenuViewBase(QMenuBar, BindableMixin[VM], Generic[VM]):
    def __init__(self, vm: VM, parent: Optional[QWidget] = None) -> None:
        QMenuBar.__init__(self, parent)
        self.__init_bindable__(vm)
        self.build_ui()
        self.bind()
