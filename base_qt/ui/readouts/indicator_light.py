from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget


class IndicatorLight(QLabel):
    """Small status dot reflecting live device state (e.g. "moving").

    Reuses the app's existing #status_dot QSS (see theme/*.qss) rather than
    introducing new styling.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("status_dot")
        self.setFixedSize(8, 8)
        self._set_level("")

    def set_active(self, active: bool) -> None:
        self._set_level("info" if active else "")

    def set_level(self, level: str) -> None:
        """level: "" (off), "info", "warning", or "error"."""
        self._set_level(level)

    def _set_level(self, level: str) -> None:
        self.setProperty("level", level)
        self.style().unpolish(self)
        self.style().polish(self)
