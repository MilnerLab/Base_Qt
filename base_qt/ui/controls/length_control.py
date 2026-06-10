from __future__ import annotations

from PySide6.QtWidgets import QWidget

from base_core.quantities.enums import Prefix
from base_core.quantities.models import Length
from base_qt.ui.controls.prefixed_control import PrefixedControl


class LengthControl(PrefixedControl[Length]):
    """Spinbox + prefix combo + 'm' label for entering a Length quantity.

    Layout: [value] [n▾] m
    Switching prefix converts the displayed number to preserve the physical value.
    """

    def __init__(
        self,
        default_prefix: Prefix = Prefix.NONE,
        allowed_prefixes: list[Prefix] | None = None,
        min_m: float = -1e18,
        max_m: float = 1e18,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("m", default_prefix, allowed_prefixes, min_m, max_m, parent)

    def _make(self, value: float, prefix: Prefix) -> Length:
        return Length(value, prefix)

    def set_length(self, length: Length) -> None:
        self.set_value(length)

    def get_length(self) -> Length:
        return self.get_value()
