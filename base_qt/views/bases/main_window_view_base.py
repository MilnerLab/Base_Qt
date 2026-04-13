from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generic, Optional, TypeVar

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDockWidget, QMainWindow, QMenuBar, QWidget

from base_qt.view_models.main_window_view_model_base import MainWindowViewModelBase
from base_qt.views.bases.main_window_view_base import ManagedDockWidget
from base_qt.views.registry.enums import ViewKind
from base_qt.views.registry.interfaces import IViewRegistry
from base_qt.views.registry.models import DockConfig, ViewSpec, PopoutConfig

from .bindable import VM, BindableMixin

# import your configs/models from the real module location
# from base_qt.views.registry.models import ViewSpec, DockConfig, PopoutConfig


class MainWindowViewBase(QMainWindow, BindableMixin[VM], Generic[VM]):
    """
    Generic shell host main window that:
    - runs MVVM lifecycle
    - installs exactly one menubar from the registry (if present)
    - hosts and opens views by id
    - supports DOCK and POPOUT directly
    - leaves PAGE and DIALOG as overridable hooks
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
        self._registry = registry
        self.__init_bindable__(vm)

        self._view_specs: Dict[str, ViewSpec] = {}
        self._docks: Dict[str, QDockWidget] = {}
        self._popouts: Dict[str, QWidget] = {}

        self.setWindowTitle(title)
        self._install_menubar_from_registry()

        self._collect_view_specs()

        self._create_startup_views()
        self.bind()

    
    def bind(self) -> None:
        super().bind()
        self.connect_binding(self.vm.open_view_requested, self.open_view_by_id)
        self.vm.on_connect()

    # ------------------------------------------------------------------
    # Generic opening API
    # ------------------------------------------------------------------

    @Slot(str)
    def open_view_by_id(self, view_id: str) -> None:
        spec = self._view_specs.get(view_id)
        if spec is None:
            raise KeyError(f"No view registered with id '{view_id}'.")

        if spec.kind == ViewKind.DOCK:
            self._open_dock(spec)
            return

        if spec.kind == ViewKind.POPOUT:
            self._open_popout(spec)
            return

        if spec.kind == ViewKind.PAGE:
            self._open_page(spec)
            return

        if spec.kind == ViewKind.DIALOG:
            self._open_dialog(spec)
            return

        raise ValueError(
            f"View '{view_id}' with kind '{spec.kind}' cannot be opened generically."
        )


    # ------------------------------------------------------------------
    # Registry/bootstrap
    # ------------------------------------------------------------------

    def _collect_view_specs(self) -> None:
        specs = sorted(self._registry.list(), key=lambda s: (s.order, s.title.lower()))
        self._view_specs = {spec.id: spec for spec in specs}

    def _create_startup_views(self) -> None:
        for spec in self._view_specs.values():
            if spec.kind == ViewKind.DOCK:
                config = spec.view_config
                if isinstance(config, DockConfig) and config.create_on_startup:
                    self._create_dock_from_spec(spec)

            elif spec.kind == ViewKind.POPOUT:
                config = spec.view_config
                if isinstance(config, PopoutConfig) and config.show_on_startup:
                    self._create_popout_from_spec(spec).show()

    # ------------------------------------------------------------------
    # DOCK handling
    # ------------------------------------------------------------------

    def ensure_dock(self, view_id: str) -> QDockWidget:
        existing = self._docks.get(view_id)
        if existing is not None:
            return existing

        spec = self._view_specs.get(view_id)
        if spec is None:
            raise KeyError(f"No view spec registered with id '{view_id}'.")

        if spec.kind != ViewKind.DOCK:
            raise ValueError(f"View '{view_id}' is not a DOCK.")

        return self._create_dock_from_spec(spec)

    def _open_dock(self, spec: ViewSpec) -> None:
        dock = self.ensure_dock(spec.id)
        dock.show()
        dock.raise_()

    def _create_dock_from_spec(self, spec: ViewSpec) -> QDockWidget:
        existing = self._docks.get(spec.id)
        if existing is not None:
            return existing

        config = spec.view_config
        if not isinstance(config, DockConfig):
            raise TypeError(
                f"DOCK view '{spec.id}' requires a DockConfig in view_config."
            )

        content = spec.factory()

        dock = ManagedDockWidget(
            dock_id=spec.id,
            title=spec.title,
            parent=self,
            destroy_on_close=config.closable,
            on_destroy_requested=self._destroy_dock,
        )
        dock.setObjectName(spec.id)
        dock.setWidget(content)
        dock.setAllowedAreas(config.allowed_areas)

        features = QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
        if config.closable:
            features |= QDockWidget.DockWidgetFeature.DockWidgetClosable
        if config.movable:
            features |= QDockWidget.DockWidgetFeature.DockWidgetMovable
        if config.floatable:
            features |= QDockWidget.DockWidgetFeature.DockWidgetFloatable

        dock.setFeatures(features)
        self.addDockWidget(config.area, dock)

        if not config.visible_by_default:
            dock.hide()

        self._docks[spec.id] = dock
        return dock

    def _destroy_dock(self, view_id: str) -> None:
        dock = self._docks.pop(view_id, None)
        if dock is None:
            return

        self.removeDockWidget(dock)
        dock.deleteLater()

    # ------------------------------------------------------------------
    # POPOUT handling
    # ------------------------------------------------------------------

    def ensure_popout(self, view_id: str) -> QWidget:
        existing = self._popouts.get(view_id)
        if existing is not None:
            return existing

        spec = self._view_specs.get(view_id)
        if spec is None:
            raise KeyError(f"No view spec registered with id '{view_id}'.")

        if spec.kind != ViewKind.POPOUT:
            raise ValueError(f"View '{view_id}' is not a POPOUT.")

        return self._create_popout_from_spec(spec)

    def _open_popout(self, spec: ViewSpec) -> None:
        popout = self.ensure_popout(spec.id)
        popout.show()
        popout.raise_()
        popout.activateWindow()

    def _create_popout_from_spec(self, spec: ViewSpec) -> QWidget:
        existing = self._popouts.get(spec.id)
        if existing is not None:
            return existing

        config = spec.view_config
        if not isinstance(config, PopoutConfig):
            raise TypeError(
                f"POPOUT view '{spec.id}' requires a PopoutConfig in view_config."
            )

        widget = spec.factory()
        widget.setParent(None)
        widget.setWindowFlag(Qt.Window, True)
        widget.setWindowTitle(config.title or spec.title)

        # ViewBase already has WA_DeleteOnClose=True, so remove cache entry on destroy.
        widget.destroyed.connect(lambda _=None, vid=spec.id: self._popouts.pop(vid, None))

        self._popouts[spec.id] = widget
        return widget

    # ------------------------------------------------------------------
    # PAGE / DIALOG hooks
    # ------------------------------------------------------------------

    def _open_page(self, spec: ViewSpec) -> None:
        raise NotImplementedError(
            "PAGE opening is not implemented in MainWindowViewBase yet. "
            "Override _open_page() in your concrete shell."
        )

    def _open_dialog(self, spec: ViewSpec) -> None:
        raise NotImplementedError(
            "DIALOG opening is not implemented in MainWindowViewBase yet. "
            "Override _open_dialog() in your concrete shell."
        )

    # ------------------------------------------------------------------
    # Menubar / close
    # ------------------------------------------------------------------

    def _install_menubar_from_registry(self) -> None:
        specs = [s for s in self._registry.list() if s.kind == ViewKind.MENUBAR]

        if not specs:
            self.setMenuBar(QMenuBar(self))
            return

        spec = specs[0]
        w = spec.factory()

        if not isinstance(w, QMenuBar):
            raise TypeError(
                f"MENUBAR spec must create QMenuBar, got {type(w).__name__} "
                f"(id={spec.id!r})"
            )

        self.setMenuBar(w)

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            self._ensure_unbound()
        finally:
            super().closeEvent(event)