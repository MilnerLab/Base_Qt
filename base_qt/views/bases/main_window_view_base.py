from __future__ import annotations

from typing import Generic, Optional, TypeVar

from PySide6.QtWidgets import QMainWindow, QMenuBar, QWidget

from base_qt.views.registry.enums import ViewKind
from base_qt.views.registry.interfaces import IViewRegistry

from .bindable import BindableMixin

VM = TypeVar("VM")

class MainWindowViewBase(QMainWindow, BindableMixin[VM], Generic[VM]):
    """
    Main window base that:
    - runs MVVM lifecycle (build_ui/bind/unbind)
    - ALWAYS installs exactly one MENUBAR from the registry (if present)
      (otherwise installs an empty QMenuBar)
    """

    def __init__(
        self,
        vm: VM,
        registry: IViewRegistry,
        parent: Optional[QWidget] = None,
        *,
        title: str = "App",
    ) -> None:
        QMainWindow.__init__(self, parent)
        self.__init_bindable__(vm)
        self._registry = registry

        self.setWindowTitle(title)
        self._install_menubar_from_registry()
        
        self._central = QWidget(self)
        self.setCentralWidget(self._central)
        
        self.build_ui()
        self.bind()
        
    @property
    def central(self) -> QWidget:
        """Central placeholder widget that derived classes can populate."""
        return self._central
    
    def _install_menubar_from_registry(self) -> None:
        specs = [s for s in self._registry.list() if s.kind == ViewKind.MENUBAR]

        if not specs:
            self.setMenuBar(QMenuBar(self))
            return

        # Policy: first (sorted by order/title in registry.list()) wins
        spec = specs[0]
        w = spec.factory()

        if not isinstance(w, QMenuBar):
            raise TypeError(
                f"MENUBAR spec must create QMenuBar, got {type(w).__name__} (id={spec.id!r})"
            )

        self.setMenuBar(w)

    def closeEvent(self, event) -> None:
        try:
            self._ensure_unbound()
        finally:
            super().closeEvent(event)
