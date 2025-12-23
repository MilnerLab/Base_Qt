from __future__ import annotations

from typing import Generic, Optional, TypeVar

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QMenuBar, QWidget
from base_qt.views.bases.bindable import BindableMixin


VM = TypeVar("VM")


class MenuViewBase(QMenuBar, BindableMixin[VM], Generic[VM]):
    """
    Base menubar with a default "File -> Exit" action that quits the application.

    Override points:
    - build_ui(): call super().build_ui() first if you want the default File/Exit
    - build_file_menu(menu): add custom actions into the File menu
    - bind()/unbind(): connect/disconnect additional actions

    Notes:
    - The default Exit action is connected directly to QApplication.quit()
      (no VM required for this baseline behavior).
    """
    def __init__(self, vm: VM, parent: Optional[QWidget] = None) -> None:
        QMenuBar.__init__(self, parent)
        self.__init_bindable__(vm)

        self._file_menu: Optional[QMenu] = None
        self._act_exit: Optional[QAction] = None

        self.build_ui()
        self.bind()

    # -------- UI --------

    def build_ui(self) -> None:
        # Default "File" menu
        self._file_menu = self.addMenu("File")

        # Default Exit
        self._act_exit = QAction("Exit", self)
        self._act_exit.setShortcut("Ctrl+Q")
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._act_exit)

    # -------- bindings --------

    def bind(self) -> None:
        super().bind()
        if self._act_exit is not None:
            self._act_exit.triggered.connect(QApplication.quit)

    def unbind(self) -> None:
        if self._act_exit is not None:
            try:
                self._act_exit.triggered.disconnect(QApplication.quit)
            except (TypeError, RuntimeError):
                # already disconnected or object destroyed
                pass
        super().unbind()


    @property
    def file_menu(self) -> QMenu:
        if self._file_menu is None:
            raise RuntimeError("File menu is not initialized yet.")
        return self._file_menu