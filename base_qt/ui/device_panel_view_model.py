"""Panel-side plumbing for a device's connection mode."""
from __future__ import annotations

from PySide6.QtCore import Signal

from base_core.ipc.connection_mode import ConnectionMode
from base_core.ipc.device_worker_handle import DeviceConnectionModeChanged
from base_qt.ui.panel_view_model import PanelViewModel, ui_thread


class DevicePanelViewModel(PanelViewModel):
    """A panel VM whose worker fronts hardware, and may end up on a mock instead.

    Subclasses pass their device handle, which supplies both the worker id to filter
    on and the live mode to read. Filtering matters: the mode event goes on the global
    bus, and on a rig with no hardware every device publishes one, so an unfiltered
    panel would badge itself for someone else's demotion.

    Wire it up in the view alongside the status bar, seeding from the current value so
    a panel opened from the Devices menu *after* the demotion still shows it::

        ctrl.set_mode(vm.connection_mode)
        vm.connection_mode_changed.connect(ctrl.set_mode)
    """

    #: (mode, reason) — feeds WorkerControlWidget.set_mode.
    connection_mode_changed = Signal(object, str)

    def __init__(self, bus, dispatcher, handle) -> None:
        super().__init__(bus, dispatcher)
        self._device_handle = handle
        self._worker_id = handle.worker_id
        self._sub(DeviceConnectionModeChanged, self._on_connection_mode_changed)

    @property
    def connection_mode(self) -> ConnectionMode | None:
        """What this panel's device is connected to. None until it has started.

        Read straight off the handle rather than cached from the last event, so a panel
        built after the device started is correct on its first paint instead of waiting
        for a change that already happened.
        """
        return self._device_handle.connection_mode

    @property
    def connection_reason(self) -> str:
        """Why, when the device demoted. Empty otherwise. Also read live."""
        return self._device_handle.connection_reason

    @ui_thread
    def _on_connection_mode_changed(self, event: DeviceConnectionModeChanged) -> None:
        if event.worker_id != self._worker_id:
            return
        self.connection_mode_changed.emit(event.mode, event.reason)
