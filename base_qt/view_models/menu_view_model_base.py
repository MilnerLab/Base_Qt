from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtGui import QIcon

from base_core.framework.events import EventBus
from base_qt.app.interfaces import IUiDispatcher
from base_qt.events.view_events import OpenViewRequested
from base_qt.view_models.thread_safe_vm_base import ThreadSafeVMBase
from base_qt.views.registry.enums import ViewKind
from base_qt.views.registry.interfaces import IViewRegistry
from base_qt.views.registry.models import DockConfig


@dataclass(frozen=True)
class OpenableViewMenuItem:
    view_id: str
    title: str
    order: int
    icon: Optional[QIcon] = None


class MenuViewModelBase(ThreadSafeVMBase):
    def __init__(
        self,
        ui: IUiDispatcher,
        bus: EventBus,
        registry: IViewRegistry,
    ) -> None:
        super().__init__(ui=ui, bus=bus)
        self._registry = registry

    @property
    def openable_views(self) -> list[OpenableViewMenuItem]:
        items: list[OpenableViewMenuItem] = []

        for spec in self._registry.list():
            if spec.kind != ViewKind.DOCK:
                continue

            config = spec.view_config
            if not isinstance(config, DockConfig):
                continue

            if not config.closable:
                continue

            items.append(
                OpenableViewMenuItem(
                    view_id=spec.id,
                    title=spec.title,
                    order=spec.order,
                    icon=spec.icon,
                )
            )

        items.sort(key=lambda x: (x.order, x.title.lower()))
        return items

    def request_open_view(self, view_id: str) -> None:
        self._bus.publish(OpenViewRequested(view_id=view_id))