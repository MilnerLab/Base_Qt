from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDoubleSpinBox, QPushButton, QWidget

from base_core.math.enums import AngleUnit
from base_core.math.models import Angle
from base_qt.ui.controls.readout_control import ControlWithReadout


class AngleControl(ControlWithReadout):
    """Spinbox + toggle button that switches between RAD and DEG display."""

    value_changed = Signal(float)

    def __init__(self, default_unit: AngleUnit = AngleUnit.DEG, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._unit = default_unit

        self._spinbox = QDoubleSpinBox()
        self._spinbox.setDecimals(6)
        self._spinbox.setRange(-1e6, 1e6)
        self._spinbox.valueChanged.connect(self.value_changed)
        self.input_layout.addWidget(self._spinbox, stretch=1)

        self._btn = QPushButton(default_unit.name)
        self._btn.setMinimumWidth(52)
        self._btn.clicked.connect(self._toggle_unit)
        self.input_layout.addWidget(self._btn)

    def _toggle_unit(self) -> None:
        old_val = self._spinbox.value()
        new_unit = AngleUnit.RAD if self._unit == AngleUnit.DEG else AngleUnit.DEG
        # Convert displayed value so the physical angle is preserved.
        # old_unit.value and new_unit.value are the rad-per-unit factors.
        new_val = old_val * self._unit.value / new_unit.value
        self._unit = new_unit
        self._btn.setText(new_unit.name)
        self._spinbox.blockSignals(True)
        self._spinbox.setValue(new_val)
        self._spinbox.blockSignals(False)

    def set_angle(self, angle: Angle) -> None:
        """Display angle in the currently selected unit."""
        self._spinbox.blockSignals(True)
        # float(angle) is radians; divide by unit.value to get display value.
        self._spinbox.setValue(float(angle) / self._unit.value)
        self._spinbox.blockSignals(False)

    def get_angle(self) -> Angle:
        return Angle(self._spinbox.value(), self._unit)

    def set_readout(self, angle: Angle) -> None:  # type: ignore[override]
        display = float(angle) / self._unit.value
        super().set_readout(f"{display:.4f} {self._unit.name}")
