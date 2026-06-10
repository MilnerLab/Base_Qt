from __future__ import annotations

import math
from abc import abstractmethod
from typing import Generic, TypeVar

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QHBoxLayout, QLabel, QWidget

from base_core.quantities.enums import Prefix


PREFIX_SYMBOLS: dict[Prefix, str] = {
    Prefix.PICO:  "p",
    Prefix.NANO:  "n",
    Prefix.MICRO: "µ",
    Prefix.MILLI: "m",
    Prefix.CENTI: "c",
    Prefix.NONE:  "",
    Prefix.KILO:  "k",
    Prefix.MEGA:  "M",
    Prefix.GIGA:  "G",
    Prefix.TERA:  "T",
}

DEFAULT_PREFIXES: list[Prefix] = [
    Prefix.PICO,
    Prefix.NANO,
    Prefix.MICRO,
    Prefix.MILLI,
    Prefix.CENTI,
    Prefix.NONE,
    Prefix.KILO,
    Prefix.MEGA,
    Prefix.GIGA,
]

T = TypeVar("T")


class PrefixedControl(QWidget, Generic[T]):
    """
    Spinbox + prefix combo + unit label for any SI-prefix–based quantity.

    Subclasses implement _make(value, prefix) to construct the quantity type.
    The quantity type must store its SI base value as float(quantity).

    Layout:  [spinbox]  [prefix▾]  unit_label

    Switching prefix rescales the displayed number so the physical value is preserved.
    """

    def __init__(
        self,
        unit_label: str,
        default_prefix: Prefix = Prefix.NONE,
        allowed_prefixes: list[Prefix] | None = None,
        min_base: float = -1e18,
        max_base: float = 1e18,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._prefixes = allowed_prefixes if allowed_prefixes is not None else DEFAULT_PREFIXES
        self._min_base = min_base
        self._max_base = max_base

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._spinbox = QDoubleSpinBox()
        self._spinbox.setDecimals(6)
        layout.addWidget(self._spinbox, stretch=1)

        self._combo = QComboBox()
        for p in self._prefixes:
            self._combo.addItem(PREFIX_SYMBOLS[p], userData=p)
        layout.addWidget(self._combo)

        if unit_label:
            layout.addWidget(QLabel(unit_label))

        idx = next((i for i, p in enumerate(self._prefixes) if p == default_prefix), 0)
        self._combo.setCurrentIndex(idx)
        self._prefix: Prefix = self._combo.currentData()
        self._update_range()

        self._combo.currentIndexChanged.connect(self._on_prefix_changed)

    @abstractmethod
    def _make(self, value: float, prefix: Prefix) -> T:
        """Construct the quantity from a display value and its prefix."""

    def set_value(self, quantity: T) -> None:
        """Show quantity in the currently selected prefix."""
        display = float(quantity) / self._prefix.value  # type: ignore[arg-type]
        self._spinbox.blockSignals(True)
        self._spinbox.setDecimals(self._decimals_for(display))
        self._spinbox.setValue(display)
        self._spinbox.blockSignals(False)

    def get_value(self) -> T:
        return self._make(self._spinbox.value(), self._prefix)

    def _update_range(self) -> None:
        lo = self._min_base / self._prefix.value
        hi = self._max_base / self._prefix.value
        self._spinbox.setRange(min(lo, hi), max(lo, hi))

    def _on_prefix_changed(self) -> None:
        old_val = self._spinbox.value()
        new_prefix: Prefix = self._combo.currentData()
        new_val = old_val * self._prefix.value / new_prefix.value
        self._prefix = new_prefix
        # Block signals before setRange so Qt cannot clamp mid-transition.
        self._spinbox.blockSignals(True)
        self._update_range()
        self._spinbox.setDecimals(self._decimals_for(new_val))
        self._spinbox.setValue(new_val)
        self._spinbox.blockSignals(False)

    @staticmethod
    def _decimals_for(value: float) -> int:
        """Return enough decimal places to show at least 4 significant digits."""
        if value == 0.0:
            return 6
        magnitude = math.floor(math.log10(abs(value)))
        return max(2, min(-magnitude + 3, 15))
