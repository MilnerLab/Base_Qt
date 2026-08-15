from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable

from PySide6.QtWidgets import QWidget

from base_qt.ui.readouts.indicator_light import IndicatorLight
from base_qt.ui.readouts.readout_label import ReadoutLabel


class Readout(ABC):
    """Declarative descriptor for a read-only field: builds a widget and
    pushes live values into it. Unlike FieldSpec, there is no get_value or
    connect_change — readouts are one-way (device -> UI) and never edited.
    """

    def __init__(self, label: str) -> None:
        self.label = label

    @abstractmethod
    def create_widget(self) -> QWidget: ...

    @abstractmethod
    def set_value(self, widget: QWidget, value: Any) -> None: ...


class ValueReadout(Readout):
    def __init__(self, label: str, fmt: Callable[[Any], str] = str, suffix: str = "") -> None:
        super().__init__(label)
        self._fmt = fmt
        self._suffix = f" {suffix}" if suffix else ""

    def create_widget(self) -> ReadoutLabel:
        return ReadoutLabel()

    def set_value(self, widget: ReadoutLabel, value: Any) -> None:  # type: ignore[override]
        widget.set_value(f"{self._fmt(value)}{self._suffix}")


class BoolReadout(Readout):
    def create_widget(self) -> IndicatorLight:
        return IndicatorLight()

    def set_value(self, widget: IndicatorLight, value: bool) -> None:  # type: ignore[override]
        widget.set_active(bool(value))
