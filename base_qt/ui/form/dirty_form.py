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


class DirtyFormWidget(QWidget):
    """Auto-generated config editor with per-field dirty indicators, free of any window.

    Subclasses declare ``_specs`` and optionally ``_groups``, then override ``on_apply``
    for side effects after the config is written back.

    This is a plain widget, not a popout, for the same reason ``MotionControls`` is: a
    device's controls appear BOTH in its floating popout (wrapped by ``DirtyForm``) and
    as a block on the docked Devices page, and there must be one implementation of them,
    not two.

    ``apply_button`` is built here but deliberately NOT placed -- the host decides where
    it goes, which is the pinned footer in a popout and an inline row in a dock block.

    Example::

        class MyForm(DirtyFormWidget):
            _specs = {"gain": FloatSpec("Gain", 0.0, 10.0)}
            _groups = [("Settings", ["gain"])]

            def on_apply(self):
                self._svc.set_config()
    """

    _specs: ClassVar[dict[str, FieldSpec]]
    _groups: ClassVar[list[tuple[str, list[str]]] | None] = None
    _readonly_when_running: ClassVar[frozenset[str]] = frozenset()

    def __init__(self, config: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = config
        self._widgets: dict[str, QWidget] = {}
        self._indicators: dict[str, DirtyIndicator] = {}

        self.form_layout = QVBoxLayout(self)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(8)

        self._build()
        self._populate()

        self._apply_btn = QPushButton("Apply")
        self._apply_btn.clicked.connect(self._apply)

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
            self.form_layout.addWidget(container)

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

    def reload(self) -> None:
        """Re-read every field from the config and clear the dirty indicators.

        For when the config changed somewhere else -- the same device shown twice, e.g.
        its popout and its block on the Devices page, both bound to the one config
        object. Unconditional: the config is the single truth, so both views agree
        afterwards even if one of them had a half-typed value.
        """
        self._populate()

    def refresh_fields(self, names: frozenset[str]) -> None:
        """Re-read named fields from config and reset their dirty indicators."""
        for name in names:
            if name not in self._widgets:
                continue
            self._specs[name].set_value(self._widgets[name], getattr(self._config, name))
            self._indicators[name].set_dirty(False)

    def on_apply(self) -> None:
        """Override to trigger side effects after the config is written back."""


class DirtyForm(PanelView):
    """A ``DirtyFormWidget`` in a popout: form in the scrolling body, Apply pinned below.

    Subclasses build their form in ``build_form``. The config is not a parameter here --
    a form is always constructed from the thing that owns the config (a view model or a
    service), which the subclass has and this base does not.

    Example::

        class MyDialog(DirtyForm):
            def __init__(self, vm, parent):
                self._vm = vm
                super().__init__("My Config", parent, vm=vm)
                self.add_worker_controls(vm)

            def build_form(self):
                return MyForm(self._vm, self)
    """

    def __init__(self, title: str, parent: QWidget, *, vm: PanelViewModel | None = None) -> None:
        super().__init__(title, parent, vm=vm)
        self.form = self.build_form()
        self.body_layout.addWidget(self.form)

        self.footer_layout.addStretch(1)
        self.footer_layout.addWidget(self.form.apply_button)
        self.footer_widget.setVisible(True)

    def build_form(self) -> DirtyFormWidget:
        raise NotImplementedError

    # -- forwarded to the form, so hosts and view models need not reach through it -----

    @property
    def apply_button(self) -> QPushButton:
        return self.form.apply_button

    def set_running(self, running: bool) -> None:
        self.form.set_running(running)

    def refresh_fields(self, names: frozenset[str]) -> None:
        self.form.refresh_fields(names)
