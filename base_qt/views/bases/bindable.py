from __future__ import annotations

from typing import Generic, Optional, TypeVar

VM = TypeVar("VM")


class BindableMixin(Generic[VM]):
    """
    Qt-agnostic MVVM lifecycle:
    - holds vm
    - build_ui() / bind() / unbind()
    - idempotent bind/unbind protection

    IMPORTANT:
    - This mixin does NOT inherit QWidget/QObject.
    - Concrete Qt base classes (QWidget/QMenuBar/QMainWindow/...) compose it via MI.
    """

    def __init_bindable__(self, vm: VM) -> None:
        self._vm: VM = vm
        self._bound: bool = False

    @property
    def vm(self) -> VM:
        return self._vm

    def build_ui(self) -> None:
        """Override: create widgets/menus/layouts."""
        pass

    def bind(self) -> None:
        """Override: connect signals. Must be idempotent."""
        self._bound = True

    def unbind(self) -> None:
        """Override: disconnect signals, stop streams, unsubscribe."""
        self._bound = False

    def _ensure_bound(self) -> None:
        if not self._bound:
            self.bind()

    def _ensure_unbound(self) -> None:
        if self._bound:
            self.unbind()
