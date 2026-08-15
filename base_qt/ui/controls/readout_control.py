from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from base_qt.ui.readouts.readout_label import ReadoutLabel


class ControlWithReadout(QWidget):
    """Base for editable controls that also show a live read-only current
    value above the input row.

    Subclasses build their editable widgets into ``self.input_layout``
    instead of laying out ``self`` directly, and override ``set_readout()``
    to format their own value type.
    """

    PLACEHOLDER = "—"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(2)

        self._readout = ReadoutLabel()
        self._readout.set_value(self.PLACEHOLDER)
        outer.addWidget(self._readout)

        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(4)
        outer.addLayout(self.input_layout)

    def set_readout(self, value: Any) -> None:
        """Show the live current value above the input. Default: str(value).

        Subclasses override to format with their own unit/prefix.
        """
        self._readout.set_value(str(value))
