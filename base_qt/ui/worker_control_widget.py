from __future__ import annotations

from typing import Any, Callable

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from base_core.ipc.connection_mode import ConnectionMode
from base_core.ipc.worker_handle import WorkerStatus


class WorkerControlWidget(QWidget):
    """
    Two-button Start/Resume | Pause/Stop bar that reflects WorkerStatus.

        NEW     → Start  ✓   Pause ✗   (left labelled "Start", right "Pause")
        RUNNING → Start  ✗   Pause ✓   (left labelled "Start", right "Pause")
        PAUSED  → Resume ✓   Stop  ✓   (left relabelled "Resume", right "Stop")
        BUSY    → both ✗

    Left button toggles Start <-> Resume (enabled in NEW or PAUSED).
    Right button toggles Pause <-> Stop (enabled in RUNNING or PAUSED).

    Usage:
        bar = WorkerControlWidget(vm.start, vm.pause, vm.resume, vm.stop, parent=self)
        bar.set_status(vm.worker_status)
        vm.worker_state_changed.connect(bar.set_status)
    """

    def __init__(
        self,
        on_start: Callable[[], None],
        on_pause: Callable[[], None],
        on_resume: Callable[[], None],
        on_stop: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_start = on_start
        self._on_pause = on_pause
        self._on_resume = on_resume
        self._on_stop = on_stop

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        # Sits left of the buttons and stays there for the whole session. A banner that
        # clears itself is not enough: the operator who takes data an hour after the
        # demotion is exactly the one who needs to be told the rig is on a fake.
        self._mode_badge = QLabel("MOCK")
        # Fixed, like the buttons beside it. Without this the label takes whatever the
        # host layout offers, and in a header row with no stretch of its own it spreads
        # across the whole panel.
        self._mode_badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._mode_badge.setStyleSheet(
            "QLabel { color: #b8860b; border: 1px solid #b8860b; border-radius: 3px; "
            "padding: 0px 4px; font-weight: bold; }")
        self._mode_badge.hide()
        row.addWidget(self._mode_badge)

        self._left_btn = QPushButton("Start")
        self._right_btn = QPushButton("Pause")

        for btn in (self._left_btn, self._right_btn):
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            row.addWidget(btn)

        self._left_btn.clicked.connect(self._on_left_clicked)
        self._right_btn.clicked.connect(self._on_right_clicked)

        self.set_status(WorkerStatus.NEW)

    def _on_left_clicked(self) -> None:
        if self._left_btn.text() == "Start":
            self._on_start()
        else:
            self._on_resume()

    def _on_right_clicked(self) -> None:
        if self._right_btn.text() == "Pause":
            self._on_pause()
        else:
            self._on_stop()

    def set_mode(self, mode: ConnectionMode | None, reason: str = "") -> None:
        """Show or hide the mock badge. Orthogonal to status, and deliberately so.

        A worker can be RUNNING on a mock, and conflating the two would let "running"
        read as "running on the instrument".
        """
        if mode != ConnectionMode.MOCK:
            self._mode_badge.hide()
            return
        self._mode_badge.setToolTip(
            f"This device is simulated. {reason}".strip() if reason
            else "This device is simulated — no hardware is connected.")
        self._mode_badge.show()

    def set_status(self, status: WorkerStatus) -> None:
        """Update button states and labels to reflect the current WorkerStatus."""
        busy    = status == WorkerStatus.BUSY
        running = status == WorkerStatus.RUNNING
        paused  = status == WorkerStatus.PAUSED

        self._left_btn.setEnabled(not busy and not running)          # NEW or PAUSED
        self._left_btn.setText("Resume" if paused else "Start")

        self._right_btn.setEnabled(not busy and (running or paused))  # RUNNING or PAUSED
        self._right_btn.setText("Stop" if paused else "Pause")


def attach_worker_controls(vm: Any, parent: QWidget | None = None) -> WorkerControlWidget:
    """Build a bar wired to a device panel view model, in one call.

    ``vm`` is a ``DevicePanelViewModel`` that also carries the worker lifecycle:
    ``start``/``pause``/``resume``/``stop``, a ``worker_status`` property and a
    ``worker_state_changed`` signal. Only the connection-mode half of that contract is
    declared on the base class -- the lifecycle half is a convention every device VM
    follows, hence the loose annotation.

    Both halves are SEEDED from the current value and then connected, never merely
    connected: a panel opened from the Devices menu long after the device started has
    already missed the events it would otherwise be waiting for, and no further one is
    coming. That applies to the mock badge in particular -- the demotion it must show
    happened at startup.
    """
    ctrl = WorkerControlWidget(vm.start, vm.pause, vm.resume, vm.stop, parent=parent)
    ctrl.set_status(vm.worker_status)
    vm.worker_state_changed.connect(ctrl.set_status)
    ctrl.set_mode(vm.connection_mode, vm.connection_reason)
    vm.connection_mode_changed.connect(ctrl.set_mode)
    return ctrl
