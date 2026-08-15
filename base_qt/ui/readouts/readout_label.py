from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget


class ReadoutLabel(QLabel):
    """Read-only display of a live device value. Never accepts user edits."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("role", "readout")

    def set_value(self, text: str) -> None:
        self.setText(text)
