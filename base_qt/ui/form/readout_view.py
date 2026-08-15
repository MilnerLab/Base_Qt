from __future__ import annotations

from typing import Any, ClassVar

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from base_qt.ui.form.readouts import Readout
from base_qt.ui.panel_view import PanelView
from base_qt.ui.panel_view_model import PanelViewModel


class ReadoutView(PanelView):
    """Read-only device panel driven by ``_readouts`` — no Apply button,
    since there's nothing to edit.

    Example::

        class PressureView(ReadoutView):
            _readouts = {
                "pressure": ValueReadout("Pressure", suffix="mbar"),
            }

            def __init__(self, vm, parent):
                super().__init__("Pressure Gauge", parent, vm=vm)
                vm.pressure_updated.connect(lambda p: self.update_readout("pressure", p))
    """

    _readouts: ClassVar[dict[str, Readout]]

    def __init__(self, title: str, parent: QWidget, *, vm: PanelViewModel | None = None) -> None:
        super().__init__(title, parent, vm=vm)
        self._widgets: dict[str, QWidget] = {}
        self._build()

    def _build(self) -> None:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(4)
        for name, readout in self._readouts.items():
            w = readout.create_widget()
            self._widgets[name] = w
            row = QHBoxLayout()
            row.setSpacing(8)
            lbl = QLabel(readout.label)
            lbl.setMinimumWidth(130)
            row.addWidget(lbl)
            row.addWidget(w, stretch=1)
            vbox.addLayout(row)
        self.body_layout.addWidget(container)

    def update_readout(self, name: str, value: Any) -> None:
        w = self._widgets.get(name)
        if w is not None:
            self._readouts[name].set_value(w, value)
