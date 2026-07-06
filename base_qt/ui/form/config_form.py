from __future__ import annotations

from typing import Any, ClassVar

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from base_qt.ui.form.specs import FieldSpec
from base_qt.ui.panel_view import PanelView
from base_qt.ui.panel_view_model import PanelViewModel


class ConfigForm(PanelView):
    """Auto-generated config editor driven by a dataclass instance.

    Subclasses declare ``_specs`` mapping field names to FieldSpec instances,
    and optionally ``_groups`` to organise fields into QGroupBox sections.

    Example::

        class MyDialog(ConfigForm):
            _specs = {
                "wavelength": LengthSpec("Wavelength", Prefix.NANO, min=700, max=1000),
                "enabled":    BoolSpec("Enable"),
            }
            _groups = [("Settings", ["wavelength", "enabled"])]

            def __init__(self, svc, parent):
                super().__init__("My Config", svc._config, parent)
                self._svc = svc

            def on_apply(self):
                self._svc.set_config()
    """

    _specs: ClassVar[dict[str, FieldSpec]]
    _groups: ClassVar[list[tuple[str, list[str]]] | None] = None

    def __init__(self, title: str, config: Any, parent: QWidget, *, vm: PanelViewModel | None = None) -> None:
        super().__init__(title, parent, vm=vm)
        self._config = config
        self._widgets: dict[str, QWidget] = {}
        self._build()
        self._populate()

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply)
        btn_row.addWidget(apply_btn)
        self.body_layout.addLayout(btn_row)

    def _build(self) -> None:
        field_sets = (
            [(group_title, field_names) for group_title, field_names in self._groups]
            if self._groups is not None
            else [(None, list(self._specs.keys()))]
        )
        for group_title, field_names in field_sets:
            if group_title is not None:
                container: QWidget = QGroupBox(group_title)
            else:
                container = QWidget()
            vbox = QVBoxLayout(container)
            vbox.setSpacing(4)
            for name in field_names:
                spec = self._specs[name]
                w = spec.create_widget()
                self._widgets[name] = w
                row = QHBoxLayout()
                row.setSpacing(8)
                lbl = QLabel(spec.label)
                lbl.setMinimumWidth(130)
                row.addWidget(lbl)
                row.addWidget(w, stretch=1)
                vbox.addLayout(row)
            self.body_layout.addWidget(container)

    def _populate(self) -> None:
        for name, spec in self._specs.items():
            spec.set_value(self._widgets[name], getattr(self._config, name))

    def _apply(self) -> None:
        for name, spec in self._specs.items():
            setattr(self._config, name, spec.get_value(self._widgets[name]))
        self.on_apply()

    def on_apply(self) -> None:
        """Override to trigger side effects after the config is written back."""
