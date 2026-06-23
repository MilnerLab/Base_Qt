from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QSizePolicy, QWidget

_CLEAN = QColor("#4b5563")
_DIRTY = QColor("#f59e0b")
_SIZE = 8


class DirtyIndicator(QWidget):
    """8×8 filled circle: gray when clean, amber when dirty."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._dirty = False
        self.setFixedSize(_SIZE, _SIZE)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_dirty(self, dirty: bool) -> None:
        if dirty != self._dirty:
            self._dirty = dirty
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_DIRTY if self._dirty else _CLEAN)
        painter.drawEllipse(0, 0, _SIZE, _SIZE)
