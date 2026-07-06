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

from base_qt.ui.dirty_indicator import DirtyIndicator
from base_qt.ui.form.specs import FieldSpec
from base_qt.ui.panel_view import PanelView
from base_qt.ui.panel_view_model import PanelViewModel


class DirtyForm(PanelView):
    """Auto-generated config editor with per-field dirty indicators.

    Subclasses declare ``_specs`` and optionally ``_groups``, then override
    ``on_apply`` for side effects after the config is written back.

    Example::

        class MyDialog(DirtyForm):
            _specs = {"gain": FloatSpec("Gain", 0.0, 10.0)}
            _groups = [("Settings", ["gain"])]

            def __init__(self, svc, vm, parent):
                super().__init__("My Config", svc._config, parent)
                self._svc = svc

            def on_apply(self):
                self._svc.set_config()
    """

    _specs: ClassVar[dict[str, FieldSpec]]
    _groups: ClassVar[list[tuple[str, list[str]]] | None] = None
    _readonly_when_running: ClassVar[frozenset[str]] = frozenset()

    def __init__(self, title: str, config: Any, parent: QWidget, *, vm: PanelViewModel | None = None) -> None:
        super().__init__(title, parent, vm=vm)
        self._config = config
        self._widgets: dict[str, QWidget] = {}
        self._indicators: dict[str, DirtyIndicator] = {}
        self._build()
        self._populate()

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self._apply_btn = QPushButton("Apply")
        self._apply_btn.clicked.connect(self._apply)
        btn_row.addWidget(self._apply_btn)
        self.body_layout.addLayout(btn_row)

    @property
    def apply_button(self) -> QPushButton:
        return self._apply_btn

    def _build(self) -> None:
        field_sets: list[tuple[str | None, list[str]]] = (
            list(self._groups)
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

                ind = DirtyIndicator()
                self._indicators[name] = ind

                row = QHBoxLayout()
                row.setSpacing(6)
                row.addWidget(ind)
                lbl = QLabel(spec.label)
                lbl.setMinimumWidth(130)
                row.addWidget(lbl)
                row.addWidget(w, stretch=1)
                vbox.addLayout(row)

                spec.connect_change(w, lambda n=name: self._set_dirty(n))
            self.body_layout.addWidget(container)

    def _populate(self) -> None:
        for name, spec in self._specs.items():
            spec.set_value(self._widgets[name], getattr(self._config, name))
        for ind in self._indicators.values():
            ind.set_dirty(False)

    def _set_dirty(self, name: str) -> None:
        self._indicators[name].set_dirty(True)

    def _apply(self) -> None:
        for name, spec in self._specs.items():
            setattr(self._config, name, spec.get_value(self._widgets[name]))
        for ind in self._indicators.values():
            ind.set_dirty(False)
        self.on_apply()

    def set_running(self, running: bool) -> None:
        """Disable/enable widgets declared in _readonly_when_running."""
        for name in self._readonly_when_running:
            w = self._widgets.get(name)
            if w is not None:
                w.setEnabled(not running)
            ind = self._indicators.get(name)
            if ind is not None:
                ind.setEnabled(not running)

    def refresh_fields(self, names: frozenset[str]) -> None:
        """Re-read named fields from config and reset their dirty indicators."""
        for name in names:
            if name not in self._widgets:
                continue
            self._specs[name].set_value(self._widgets[name], getattr(self._config, name))
            self._indicators[name].set_dirty(False)

    def on_apply(self) -> None:
        """Override to trigger side effects after the config is written back."""
