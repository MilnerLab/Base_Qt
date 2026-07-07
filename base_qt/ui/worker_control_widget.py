from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QWidget

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

    def set_status(self, status: WorkerStatus) -> None:
        """Update button states and labels to reflect the current WorkerStatus."""
        busy    = status == WorkerStatus.BUSY
        running = status == WorkerStatus.RUNNING
        paused  = status == WorkerStatus.PAUSED

        self._left_btn.setEnabled(not busy and not running)          # NEW or PAUSED
        self._left_btn.setText("Resume" if paused else "Start")

        self._right_btn.setEnabled(not busy and (running or paused))  # RUNNING or PAUSED
        self._right_btn.setText("Stop" if paused else "Pause")
