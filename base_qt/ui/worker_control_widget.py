from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QWidget

from base_core.ipc.worker_handle import WorkerStatus


class WorkerControlWidget(QWidget):
    """
    Two-button Start / Pause-or-Reset bar that reflects WorkerStatus.

        NEW     → Start ✓    Pause ✗   (second button grayed, labelled "Pause")
        RUNNING → Start ✗    Pause ✓   (second button active, labelled "Pause")
        PAUSED  → Resume ✓   Reset ✓   (first button relabelled "Resume", second "Reset")
        BUSY    → both ✗

    Usage:
        bar = WorkerControlWidget(vm.start, vm.pause, vm.reset, parent=self)
        bar.set_status(vm.worker_status)
        vm.worker_state_changed.connect(bar.set_status)
    """

    def __init__(
        self,
        on_start: Callable[[], None],
        on_pause: Callable[[], None],
        on_reset: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_pause = on_pause
        self._on_reset = on_reset

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        self._start_btn      = QPushButton("Start")
        self._pause_reset_btn = QPushButton("Pause")

        for btn in (self._start_btn, self._pause_reset_btn):
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            row.addWidget(btn)

        self._start_btn.clicked.connect(on_start)
        self._pause_reset_btn.clicked.connect(self._on_pause_reset_clicked)

        self.set_status(WorkerStatus.NEW)

    def _on_pause_reset_clicked(self) -> None:
        if self._pause_reset_btn.text() == "Pause":
            self._on_pause()
        else:
            self._on_reset()

    def set_status(self, status: WorkerStatus) -> None:
        """Update button states and labels to reflect the current WorkerStatus."""
        busy   = status == WorkerStatus.BUSY
        running = status == WorkerStatus.RUNNING
        paused  = status == WorkerStatus.PAUSED

        self._start_btn.setEnabled(not busy and not running)       # NEW or PAUSED
        self._start_btn.setText("Resume" if paused else "Start")
        self._pause_reset_btn.setEnabled(not busy and status != WorkerStatus.NEW)
        self._pause_reset_btn.setText("Reset" if paused else "Pause")
