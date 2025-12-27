from __future__ import annotations

from typing import Generic, Optional, TypeVar
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget

from base_qt.views.bases.bindable import BindableMixin
from base_qt.view_models.vm_base import VMBase


VM = TypeVar("VM", bound=VMBase)

class ViewBase(QWidget, BindableMixin[VM], Generic[VM]):
    def __init__(self, vm: VM, parent: Optional[QWidget] = None) -> None:
        QWidget.__init__(self, parent)
        self.__init_bindable__(vm)
        self.build_ui()
        self.bind()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
    
    def build_ui(self) -> None:
        """Override: create widgets/menus/layouts."""
        pass
    
    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            self._ensure_unbound()
            self.vm.dispose()
        finally:
            super().closeEvent(event)