from __future__ import annotations

from PySide6.QtWidgets import QWidget

from base_core.quantities.enums import Prefix
from base_core.quantities.models import Frequency, Mass, Power, Time
from base_core.quantities.specific_models import GDD
from base_qt.ui.controls.prefixed_control import PREFIX_SYMBOLS, PrefixedControl
from base_qt.ui.controls.readout_control import ControlWithReadout


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


class GDDControl(PrefixedControl[GDD]):
    """Spinbox + prefix combo + 's²' label for entering a GDD quantity.

    GDD scales with the *square* of the time prefix (it's s^2, not s), unlike
    PrefixedControl's linear assumption, so set_value/_update_range/_on_prefix_changed
    are overridden here; _make/get_value already work unchanged since GDD's own
    constructor applies the square.
    """

    def __init__(
        self,
        default_prefix: Prefix = Prefix.PICO,
        allowed_prefixes: list[Prefix] | None = None,
        min_s2: float = -1e18,
        max_s2: float = 1e18,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("s²", default_prefix, allowed_prefixes, min_s2, max_s2, parent)

    def _make(self, value: float, prefix: Prefix) -> GDD:
        return GDD(value, prefix)

    def set_value(self, quantity: GDD) -> None:
        display = float(quantity) / (self._prefix.value ** 2)
        self._spinbox.blockSignals(True)
        self._spinbox.setDecimals(self._decimals_for(display))
        self._spinbox.setValue(display)
        self._spinbox.blockSignals(False)

    def _update_range(self) -> None:
        lo = self._min_base / (self._prefix.value ** 2)
        hi = self._max_base / (self._prefix.value ** 2)
        self._spinbox.setRange(min(lo, hi), max(lo, hi))

    def _on_prefix_changed(self) -> None:
        old_val = self._spinbox.value()
        new_prefix: Prefix = self._combo.currentData()
        new_val = old_val * (self._prefix.value ** 2) / (new_prefix.value ** 2)
        self._prefix = new_prefix
        self._spinbox.blockSignals(True)
        self._update_range()
        self._spinbox.setDecimals(self._decimals_for(new_val))
        self._spinbox.setValue(new_val)
        self._spinbox.blockSignals(False)

    def set_gdd(self, gdd: GDD) -> None:
        self.set_value(gdd)

    def get_gdd(self) -> GDD:
        return self.get_value()

    def set_readout(self, gdd: GDD) -> None:  # type: ignore[override]
        display = float(gdd) / (self._prefix.value ** 2)
        text = f"{display:.{self._decimals_for(display)}f} {PREFIX_SYMBOLS[self._prefix]}{self._unit_label}"
        ControlWithReadout.set_readout(self, text)
