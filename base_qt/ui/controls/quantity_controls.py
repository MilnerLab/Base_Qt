from __future__ import annotations

from PySide6.QtWidgets import QWidget

from base_core.quantities.enums import Prefix
from base_core.quantities.models import Frequency, Mass, Power, Time
from base_qt.ui.controls.prefixed_control import PrefixedControl


class TimeControl(PrefixedControl[Time]):
    """Spinbox + prefix combo + 's' label for entering a Time quantity."""

    def __init__(
        self,
        default_prefix: Prefix = Prefix.PICO,
        allowed_prefixes: list[Prefix] | None = None,
        min_s: float = 0.0,
        max_s: float = 1e18,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("s", default_prefix, allowed_prefixes, min_s, max_s, parent)

    def _make(self, value: float, prefix: Prefix) -> Time:
        return Time(value, prefix)

    def set_time(self, time: Time) -> None:
        self.set_value(time)

    def get_time(self) -> Time:
        return self.get_value()


class FrequencyControl(PrefixedControl[Frequency]):
    """Spinbox + prefix combo + 'Hz' label for entering a Frequency quantity."""

    def __init__(
        self,
        default_prefix: Prefix = Prefix.NONE,
        allowed_prefixes: list[Prefix] | None = None,
        min_hz: float = 0.0,
        max_hz: float = 1e18,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Hz", default_prefix, allowed_prefixes, min_hz, max_hz, parent)

    def _make(self, value: float, prefix: Prefix) -> Frequency:
        return Frequency(value, prefix)

    def set_frequency(self, frequency: Frequency) -> None:
        self.set_value(frequency)

    def get_frequency(self) -> Frequency:
        return self.get_value()


class MassControl(PrefixedControl[Mass]):
    """Spinbox + prefix combo + 'g' label for entering a Mass quantity.

    Note: displayed in grams (prefix relative to grams), stored in kg.
    The internal representation is kg so NONE prefix = 1 kg, not 1 g.
    Pass default_prefix=Prefix.MILLI for a 'g' default display.
    """

    def __init__(
        self,
        default_prefix: Prefix = Prefix.MILLI,
        allowed_prefixes: list[Prefix] | None = None,
        min_kg: float = 0.0,
        max_kg: float = 1e18,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("kg", default_prefix, allowed_prefixes, min_kg, max_kg, parent)

    def _make(self, value: float, prefix: Prefix) -> Mass:
        return Mass(value, prefix)

    def set_mass(self, mass: Mass) -> None:
        self.set_value(mass)

    def get_mass(self) -> Mass:
        return self.get_value()


class PowerControl(PrefixedControl[Power]):
    """Spinbox + prefix combo + 'W' label for entering a Power quantity."""

    def __init__(
        self,
        default_prefix: Prefix = Prefix.MILLI,
        allowed_prefixes: list[Prefix] | None = None,
        min_w: float = 0.0,
        max_w: float = 1e18,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("W", default_prefix, allowed_prefixes, min_w, max_w, parent)

    def _make(self, value: float, prefix: Prefix) -> Power:
        return Power(value, prefix)

    def set_power(self, power: Power) -> None:
        self.set_value(power)

    def get_power(self) -> Power:
        return self.get_value()
