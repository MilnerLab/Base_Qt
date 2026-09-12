from __future__ import annotations

from typing import Generic, TypeVar

from PySide6.QtWidgets import QWidget

from base_core.framework.di import Container
from base_qt.ui.panel_view import PanelView

T = TypeVar("T", bound=PanelView)


class ViewHost(Generic[T]):
    """
    Lazily resolves a PanelView-family view from the container, reparenting it
    under `parent`. Works for both registration styles:

    - A view registered as a FACTORY and built with ``vm=`` is destroyed when
      the user closes it (PanelView._on_close -> vm.on_close() + deleteLater).
      The next open() resolves a fresh View/ViewModel pair.
    - A view registered as a SINGLETON and built without ``vm=`` -- the device
      views, whose ViewModel is shared with the Devices page -- is only hidden
      on close. The next open() re-shows that same widget.

    Usage:
        host = ViewHost(container, ELL14RotatorView, parent=self)
        menu.addAction("ELL14 Rotator", host.open)
    """

    def __init__(self, container: Container, view_type: type[T], parent: QWidget) -> None:
        self._container = container
        self._view_type = view_type
        self._parent = parent
        self._view: T | None = None

    def open(self) -> None:
        if self._view is None:
            view = self._container.get(self._view_type)
            view.setParent(self._parent)
            # destroyed, not closed: `closed` fires for a hide-only close too, which
            # would drop a singleton view we should keep -- and the next open() would
            # then re-resolve the same object and stack a second connection on it.
            # destroyed fires only when the widget really is gone, which is exactly
            # when the reference must be dropped.
            view.destroyed.connect(self._on_destroyed)
            self._view = view
        self._view.open()

    def _on_destroyed(self) -> None:
        self._view = None
