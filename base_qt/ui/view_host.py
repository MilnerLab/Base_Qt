from __future__ import annotations

from typing import Generic, TypeVar

from PySide6.QtWidgets import QWidget

from base_core.framework.di import Container
from base_qt.ui.panel_view import PanelView

T = TypeVar("T", bound=PanelView)


class ViewHost(Generic[T]):
    """
    Lazily resolves a PanelView-family view from a container factory,
    reparenting it under `parent`. When the user closes the view, its
    ViewModel's subscriptions are torn down (PanelView._on_close ->
    vm.on_close()) and the widget is deleted; the next open() resolves a
    fresh View/ViewModel pair from the container factory.

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
            view.closed.connect(self._on_closed)
            self._view = view
        self._view.open()

    def _on_closed(self) -> None:
        self._view = None
