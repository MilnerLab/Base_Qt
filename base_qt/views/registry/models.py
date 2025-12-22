
from dataclasses import dataclass
from typing import Callable, Optional
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

from base_qt.views.registry.enums import ViewKind


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
    factory: Callable[[], QWidget]
    icon: Optional[QIcon] = None
    order: int = 0
