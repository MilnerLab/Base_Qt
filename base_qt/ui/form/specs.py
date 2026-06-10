from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QWidget,
)

from base_core.math.enums import AngleUnit
from base_core.math.models import Angle, Range
from base_core.quantities.enums import Prefix
from base_core.quantities.models import Frequency, Length, Mass, Power, Time
from base_qt.ui.controls.angle_control import AngleControl
from base_qt.ui.controls.length_control import LengthControl
from base_qt.ui.controls.quantity_controls import (
    FrequencyControl,
    MassControl,
    PowerControl,
    TimeControl,
)


class FieldSpec(ABC):
    def __init__(self, label: str) -> None:
        self.label = label

    @abstractmethod
    def create_widget(self) -> QWidget: ...

    @abstractmethod
    def set_value(self, widget: QWidget, value: Any) -> None: ...

    @abstractmethod
    def get_value(self, widget: QWidget) -> Any: ...


class FloatSpec(FieldSpec):
    def __init__(
        self,
        label: str,
        min: float,
        max: float,
        decimals: int = 4,
        step: float = 0.01,
        suffix: str = "",
    ) -> None:
        super().__init__(label)
        self._min = min
        self._max = max
        self._decimals = decimals
        self._step = step
        self._suffix = suffix

    def create_widget(self) -> QDoubleSpinBox:
        sb = QDoubleSpinBox()
        sb.setRange(self._min, self._max)
        sb.setDecimals(self._decimals)
        sb.setSingleStep(self._step)
        if self._suffix:
            sb.setSuffix(f" {self._suffix}")
        return sb

    def set_value(self, widget: QDoubleSpinBox, value: float) -> None:  # type: ignore[override]
        widget.setValue(float(value))

    def get_value(self, widget: QDoubleSpinBox) -> float:  # type: ignore[override]
        return widget.value()


class IntSpec(FieldSpec):
    def __init__(self, label: str, min: int, max: int, step: int = 1) -> None:
        super().__init__(label)
        self._min = min
        self._max = max
        self._step = step

    def create_widget(self) -> QSpinBox:
        sb = QSpinBox()
        sb.setRange(self._min, self._max)
        sb.setSingleStep(self._step)
        return sb

    def set_value(self, widget: QSpinBox, value: int) -> None:  # type: ignore[override]
        widget.setValue(int(value))

    def get_value(self, widget: QSpinBox) -> int:  # type: ignore[override]
        return widget.value()


class BoolSpec(FieldSpec):
    def create_widget(self) -> QCheckBox:
        return QCheckBox()

    def set_value(self, widget: QCheckBox, value: bool) -> None:  # type: ignore[override]
        widget.setChecked(bool(value))

    def get_value(self, widget: QCheckBox) -> bool:  # type: ignore[override]
        return widget.isChecked()


class AngleSpec(FieldSpec):
    def __init__(self, label: str, default_unit: AngleUnit = AngleUnit.DEG) -> None:
        super().__init__(label)
        self._default_unit = default_unit

    def create_widget(self) -> AngleControl:
        return AngleControl(self._default_unit)

    def set_value(self, widget: AngleControl, value: Angle) -> None:  # type: ignore[override]
        widget.set_angle(value)

    def get_value(self, widget: AngleControl) -> Angle:  # type: ignore[override]
        return widget.get_angle()


class LengthSpec(FieldSpec):
    def __init__(
        self,
        label: str,
        default_prefix: Prefix,
        allowed_prefixes: list[Prefix] | None = None,
        min: float | None = None,
        max: float | None = None,
    ) -> None:
        super().__init__(label)
        self._default_prefix = default_prefix
        self._allowed_prefixes = allowed_prefixes
        # Store bounds in meters; min/max are given in default_prefix units.
        self._min_m = min * float(default_prefix) if min is not None else -1e18
        self._max_m = max * float(default_prefix) if max is not None else 1e18

    def create_widget(self) -> LengthControl:
        return LengthControl(
            self._default_prefix,
            self._allowed_prefixes,
            self._min_m,
            self._max_m,
        )

    def set_value(self, widget: LengthControl, value: Length) -> None:  # type: ignore[override]
        widget.set_length(value)

    def get_value(self, widget: LengthControl) -> Length:  # type: ignore[override]
        return widget.get_length()


class TimeSpec(FieldSpec):
    def __init__(
        self,
        label: str,
        default_prefix: Prefix = Prefix.PICO,
        allowed_prefixes: list[Prefix] | None = None,
        min: float | None = None,
        max: float | None = None,
    ) -> None:
        super().__init__(label)
        self._default_prefix = default_prefix
        self._allowed_prefixes = allowed_prefixes
        self._min_s = min * float(default_prefix) if min is not None else 0.0
        self._max_s = max * float(default_prefix) if max is not None else 1e18

    def create_widget(self) -> TimeControl:
        return TimeControl(self._default_prefix, self._allowed_prefixes, self._min_s, self._max_s)

    def set_value(self, widget: TimeControl, value: Time) -> None:  # type: ignore[override]
        widget.set_time(value)

    def get_value(self, widget: TimeControl) -> Time:  # type: ignore[override]
        return widget.get_time()


class FrequencySpec(FieldSpec):
    def __init__(
        self,
        label: str,
        default_prefix: Prefix = Prefix.NONE,
        allowed_prefixes: list[Prefix] | None = None,
        min: float | None = None,
        max: float | None = None,
    ) -> None:
        super().__init__(label)
        self._default_prefix = default_prefix
        self._allowed_prefixes = allowed_prefixes
        self._min_hz = min * float(default_prefix) if min is not None else 0.0
        self._max_hz = max * float(default_prefix) if max is not None else 1e18

    def create_widget(self) -> FrequencyControl:
        return FrequencyControl(self._default_prefix, self._allowed_prefixes, self._min_hz, self._max_hz)

    def set_value(self, widget: FrequencyControl, value: Frequency) -> None:  # type: ignore[override]
        widget.set_frequency(value)

    def get_value(self, widget: FrequencyControl) -> Frequency:  # type: ignore[override]
        return widget.get_frequency()


class MassSpec(FieldSpec):
    def __init__(
        self,
        label: str,
        default_prefix: Prefix = Prefix.MILLI,
        allowed_prefixes: list[Prefix] | None = None,
        min: float | None = None,
        max: float | None = None,
    ) -> None:
        super().__init__(label)
        self._default_prefix = default_prefix
        self._allowed_prefixes = allowed_prefixes
        self._min_kg = min * float(default_prefix) if min is not None else 0.0
        self._max_kg = max * float(default_prefix) if max is not None else 1e18

    def create_widget(self) -> MassControl:
        return MassControl(self._default_prefix, self._allowed_prefixes, self._min_kg, self._max_kg)

    def set_value(self, widget: MassControl, value: Mass) -> None:  # type: ignore[override]
        widget.set_mass(value)

    def get_value(self, widget: MassControl) -> Mass:  # type: ignore[override]
        return widget.get_mass()


class PowerSpec(FieldSpec):
    def __init__(
        self,
        label: str,
        default_prefix: Prefix = Prefix.MILLI,
        allowed_prefixes: list[Prefix] | None = None,
        min: float | None = None,
        max: float | None = None,
    ) -> None:
        super().__init__(label)
        self._default_prefix = default_prefix
        self._allowed_prefixes = allowed_prefixes
        self._min_w = min * float(default_prefix) if min is not None else 0.0
        self._max_w = max * float(default_prefix) if max is not None else 1e18

    def create_widget(self) -> PowerControl:
        return PowerControl(self._default_prefix, self._allowed_prefixes, self._min_w, self._max_w)

    def set_value(self, widget: PowerControl, value: Power) -> None:  # type: ignore[override]
        widget.set_power(value)

    def get_value(self, widget: PowerControl) -> Power:  # type: ignore[override]
        return widget.get_power()


class EnumSpec(FieldSpec):
    def __init__(self, label: str, enum_type: type) -> None:
        super().__init__(label)
        self._enum_type = enum_type

    def create_widget(self) -> QComboBox:
        combo = QComboBox()
        for item in self._enum_type:
            combo.addItem(item.name, userData=item)
        return combo

    def set_value(self, widget: QComboBox, value: Any) -> None:  # type: ignore[override]
        for i in range(widget.count()):
            if widget.itemData(i) == value:
                widget.setCurrentIndex(i)
                return

    def get_value(self, widget: QComboBox) -> Any:  # type: ignore[override]
        return widget.currentData()


class _RangeWidget(QWidget):
    def __init__(self, min_widget: QWidget, max_widget: QWidget) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(min_widget, stretch=1)
        layout.addWidget(QLabel("–"))
        layout.addWidget(max_widget, stretch=1)
        self.min_widget = min_widget
        self.max_widget = max_widget


class RangeSpec(FieldSpec):
    """Two side-by-side controls for a Range[T] field (min – max)."""

    def __init__(self, label: str, inner: FieldSpec) -> None:
        super().__init__(label)
        self._inner = inner

    def create_widget(self) -> _RangeWidget:
        return _RangeWidget(
            self._inner.create_widget(),
            self._inner.create_widget(),
        )

    def set_value(self, widget: _RangeWidget, value: Range) -> None:  # type: ignore[override]
        self._inner.set_value(widget.min_widget, value.min)
        self._inner.set_value(widget.max_widget, value.max)

    def get_value(self, widget: _RangeWidget) -> Range:  # type: ignore[override]
        return Range(
            self._inner.get_value(widget.min_widget),
            self._inner.get_value(widget.max_widget),
        )
