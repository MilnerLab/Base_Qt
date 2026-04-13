from __future__ import annotations

from functools import partial
from typing import Generic, Optional, TypeVar

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QMenuBar, QWidget

from base_qt.views.bases.bindable import BindableMixin
from base_qt.view_models.menu_view_model_base import MenuViewModelBase


VM = TypeVar("VM", bound=MenuViewModelBase)


class MenuViewBase(QMenuBar, BindableMixin[VM], Generic[VM]):
    """
    Base menubar with:
    - File -> Exit
    - one top-level menu per closable dock view
    - each such menu contains an "Open" action
    """

    def __init__(self, vm: VM, parent: Optional[QWidget] = None) -> None:
        QMenuBar.__init__(self, parent)
        self.__init_bindable__(vm)

        self._file_menu: Optional[QMenu] = None
        self._act_exit: Optional[QAction] = None

        self._view_menus: dict[str, QMenu] = {}
        self._act_open_view: dict[str, QAction] = {}

        self.build_ui()
        self.bind()

    def build_ui(self) -> None:
        self._build_file_menu()
        self._build_open_view_menus()

    def _build_file_menu(self) -> None:
        self._file_menu = self.addMenu("File")

        self._act_exit = QAction("Exit", self)
        self._act_exit.setShortcut("Ctrl+Q")

        self._file_menu.addSeparator()
        self._file_menu.addAction(self._act_exit)

    def _build_open_view_menus(self) -> None:
        for item in self.vm.openable_views:
            menu = self.addMenu(item.title)
            if item.icon is not None:
                menu.setIcon(item.icon)

            act_open = QAction("Open", self)
            if item.icon is not None:
                act_open.setIcon(item.icon)

            menu.addAction(act_open)

            self._view_menus[item.view_id] = menu
            self._act_open_view[item.view_id] = act_open

    def bind(self) -> None:
        super().bind()

        if self._act_exit is not None:
            self.connect_binding(self._act_exit.triggered, QApplication.quit)

        for view_id, action in self._act_open_view.items():
            self.connect_binding(
                action.triggered,
                partial(self.vm.request_open_view, view_id),
            )

    @property
    def file_menu(self) -> QMenu:
        if self._file_menu is None:
            raise RuntimeError("File menu is not initialized yet.")
        return self._file_menu

    def get_view_menu(self, view_id: str) -> QMenu:
        try:
            return self._view_menus[view_id]
        except KeyError as exc:
            raise KeyError(f"No menu registered for view_id '{view_id}'.") from exc