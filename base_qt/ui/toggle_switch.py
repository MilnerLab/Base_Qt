from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtWidgets import QAbstractButton
from PySide6.QtGui import QPainter, QColor, QPen


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None, text_on="ON", text_off="OFF"):
        super().__init__(parent)
        self._text_on = text_on
        self._text_off = text_off

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(56, 28)

        self._offset = 1.0 if self.isChecked() else 0.0

        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self.toggled.connect(self._start_anim)

    def sizeHint(self) -> QSize:
        return QSize(56, 28)

    # Wichtig: wenn du im write_to_ui blockSignals(True) nutzt,
    # kommt kein toggled-Signal -> dann Offset direkt setzen.
    def setChecked(self, checked: bool) -> None:
        was_blocked = self.signalsBlocked()
        super().setChecked(checked)
        if was_blocked:
            self._offset = 1.0 if checked else 0.0
            self.update()

    def _start_anim(self, checked: bool):
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def getOffset(self) -> float:
        return self._offset

    def setOffset(self, v: float):
        self._offset = float(v)
        self.update()

    offset = Property(float, getOffset, setOffset)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        r = self.rect().adjusted(1, 1, -1, -1)
        radius = r.height() / 2

        enabled = self.isEnabled()
        checked = self.isChecked()

        # Farben (ähnlich deinem Bild)
        col_on = QColor(0, 160, 230)
        col_off = QColor(230, 230, 230)
        col_border = QColor(180, 180, 180)
        col_thumb_border = QColor(190, 190, 190)

        if not enabled:
            track = QColor(240, 240, 240)
            text_col = QColor(170, 170, 170)
        else:
            track = col_on if checked else col_off
            text_col = QColor(255, 255, 255) if checked else QColor(160, 160, 160)

        # Track
        p.setPen(QPen(col_border, 1))
        p.setBrush(track)
        p.drawRoundedRect(r, radius, radius)

        # Thumb
        margin = 2
        d = r.height() - 2 * margin
        x_min = r.left() + margin
        x_max = r.right() - margin - d
        x = x_min + (x_max - x_min) * self._offset
        thumb_rect = (int(x), r.top() + margin, int(d), int(d))

        p.setPen(QPen(col_thumb_border, 1))
        p.setBrush(QColor(255, 255, 255) if enabled else QColor(250, 250, 250))
        p.drawEllipse(*thumb_rect)

        # Text ON/OFF
        p.setPen(text_col)
        text = self._text_on if checked else self._text_off
        pad = 10
        if checked:
            p.drawText(r.adjusted(pad, 0, -int(d) - pad, 0), Qt.AlignVCenter | Qt.AlignLeft, text)
        else:
            p.drawText(r.adjusted(int(d) + pad, 0, -pad, 0), Qt.AlignVCenter | Qt.AlignRight, text)
