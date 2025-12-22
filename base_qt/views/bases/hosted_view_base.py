from __future__ import annotations

from typing import Generic, Optional, TypeVar
from PySide6.QtWidgets import QWidget

from base_qt.shell.hosting import HostInfo
from base_qt.views.bases.view_base import ViewBase

VM = TypeVar("VM")


class HostedViewBase(ViewBase[VM], Generic[VM]):
    """
    Base for views that are hosted inside the application (tabs, docks, stacked pages).
    Provides a HostInfo metadata object the shell can read.
    """

    host_info: HostInfo  # subclasses should override

    def on_hosted(self) -> None:
        """Called by the host when the view becomes active/visible."""
        pass

    def on_unhosted(self) -> None:
        """Called by the host when the view is removed/hidden."""
        pass

    def closeEvent(self, event) -> None:
        try:
            # let derived classes stop streams etc. earlier if they want
            self.on_unhosted()
        finally:
            super().closeEvent(event)
