
from dataclasses import dataclass
from typing import Any, Callable, Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from base_qt.views.bases.view_base import ViewBase
from base_qt.views.registry.enums import ViewKind


@dataclass(frozen=True)
class DockConfig:
    area: Qt.DockWidgetArea = Qt.LeftDockWidgetArea
    visible_by_default: bool = True
    closable: bool = True
    movable: bool = True
    floatable: bool = True
    allowed_areas: Qt.DockWidgetAreas = Qt.AllDockWidgetAreas
    tab_group: Optional[str] = None
    create_on_startup: bool = False
    
@dataclass(frozen=True)
class PopoutConfig:
    title: Optional[str] = None
    show_on_startup: bool = False

@dataclass(frozen=True)
class ViewSpec:
    """
    A declarative description of a view that a shell can materialize.

    factory(): must create and return a QWidget each time it is called.
    (If you want singleton views, see the "ShellViewHost" caching extension later.)
    """
    id: str
    title: str
    kind: ViewKind
    factory: Callable[[], ViewBase]
    view_config: object | None = None
    icon: Optional[QIcon] = None
    order: int = 0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("ViewSpec id cannot be empty.")

        if not self.title.strip():
            raise ValueError("ViewSpec title cannot be empty.")

        if self.kind == ViewKind.DOCK and not isinstance(self.view_config, DockConfig):
            raise TypeError(
                "ViewKind.DOCK requires view_config to be a DockConfig instance."
            )