from __future__ import annotations

from typing import Any, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget


class SegmentedControl(QWidget):
    """
    A row of mutually exclusive buttons drawn as one control; the selected one stays pushed in.
    Themeable via QSS:
      Selector anchor is objectName "SegmentedControl"
      Each segment carries [segment="left"|"middle"|"right"] so only the outer corners round
    """

    value_changed = Signal(object)

    def __init__(self, options: Sequence[tuple[str, Any]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SegmentedControl")  # reliable QSS selector anchor
        if not options:
            raise ValueError("SegmentedControl needs at least one option")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._values: list[Any] = []

        last = len(options) - 1
        for i, (label, value) in enumerate(options):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("segment", "left" if i == 0 else "right" if i == last else "middle")
            self._group.addButton(btn, i)
            self._values.append(value)
            layout.addWidget(btn)

        self._group.button(0).setChecked(True)
        # idToggled fires for the button going down AND the one coming up; only the former
        # is a selection.
        self._group.idToggled.connect(self._on_toggled)

    def value(self) -> Any:
        return self._values[self._group.checkedId()]

    def set_value(self, value: Any) -> None:
        """Select ``value`` without emitting ``value_changed`` (for syncing from the model)."""
        btn = self._group.button(self._values.index(value))
        self._group.blockSignals(True)
        btn.setChecked(True)
        self._group.blockSignals(False)

    def _on_toggled(self, idx: int, checked: bool) -> None:
        if checked:
            self.value_changed.emit(self._values[idx])
