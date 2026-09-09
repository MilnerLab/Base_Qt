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

    The readout row stays hidden until a device actually reports a value. It used to
    be shown from the start holding a placeholder dash, which meant every field in
    every config form carried an empty box forever: nothing in the application calls
    ``ConfigForm.update_readout``, so no value ever arrived to replace it. A row that
    only ever says "—" costs vertical space and teaches the operator to ignore it,
    which is the opposite of what a live readout is for.
    """

    PLACEHOLDER = "—"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(2)

        self._readout = ReadoutLabel()
        self._readout.set_value(self.PLACEHOLDER)
        self._readout.hide()
        outer.addWidget(self._readout)

        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(4)
        outer.addLayout(self.input_layout)

    @property
    def has_readout(self) -> bool:
        """True once a live value has been pushed in."""
        return not self._readout.isHidden()

    def set_readout(self, value: Any) -> None:
        """Show the live current value above the input. Default: str(value).

        Subclasses override to format with their own unit/prefix.
        """
        self._readout.set_value(str(value))
        self._readout.show()

    def clear_readout(self) -> None:
        """Drop back to no live value, e.g. when the device stops."""
        self._readout.set_value(self.PLACEHOLDER)
        self._readout.hide()
