from __future__ import annotations

from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QAbstractButton


def _to_qcolor(v) -> QColor:
    if isinstance(v, QColor):
        return v
    return QColor(v)  # accepts "#RRGGBB", "rgba(...)" strings, etc.


class ToggleSwitch(QAbstractButton):
    """
    Custom-painted toggle that is themeable via QSS:
      QSS sets qproperty-* colors
      Selector uses objectName + [role="..."]
    """

    def __init__(self, parent=None, text_on="ON", text_off="OFF"):
        super().__init__(parent)

        self.setObjectName("ToggleSwitch")  # reliable QSS selector anchor
        self._text_on = text_on
        self._text_off = text_off

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(56, 28)

        # ---- themeable properties (defaults; will be overridden by QSS) ----
        self._trackOn = QColor(30, 120, 255, 220)
        self._trackOff = QColor(230, 230, 230)
        self._trackBorder = QColor(180, 180, 180)

        self._thumbFill = QColor(255, 255, 255)
        self._thumbBorder = QColor(190, 190, 190)

        self._textOn = QColor(255, 255, 255)
        self._textOff = QColor(120, 120, 120)

        self._trackDisabled = QColor(240, 240, 240)
        self._textDisabled = QColor(170, 170, 170)
        self._thumbDisabled = QColor(250, 250, 250)

        # ---- animation ----
        self._offset = 1.0 if self.isChecked() else 0.0
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self.toggled.connect(self._start_anim)

    # --- role helper (optional but convenient) ---
    def setRole(self, role: str | None) -> None:
        if role is None:
            self.setProperty("role", None)
        else:
            self.setProperty("role", role)
        # force stylesheet re-application if role changes at runtime
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(56, 28)

    # IMPORTANT: if caller uses blockSignals(True) during write-to-ui,
    # toggled won't fire -> set offset immediately.
    def setChecked(self, checked: bool) -> None:
        was_blocked = self.signalsBlocked()
        super().setChecked(checked)
        if was_blocked:
            self._offset = 1.0 if checked else 0.0
            self.update()

    # ---- animated offset property ----
    def getOffset(self) -> float:
        return self._offset

    def setOffset(self, v: float) -> None:
        self._offset = float(v)
        self.update()

    offset = Property(float, getOffset, setOffset)

    def _start_anim(self, checked: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    # ---- QSS-settable color properties ----
    def _get_trackOn(self) -> QColor: return self._trackOn
    def _set_trackOn(self, v) -> None: self._trackOn = _to_qcolor(v); self.update()
    trackOn = Property(QColor, _get_trackOn, _set_trackOn)

    def _get_trackOff(self) -> QColor: return self._trackOff
    def _set_trackOff(self, v) -> None: self._trackOff = _to_qcolor(v); self.update()
    trackOff = Property(QColor, _get_trackOff, _set_trackOff)

    def _get_trackBorder(self) -> QColor: return self._trackBorder
    def _set_trackBorder(self, v) -> None: self._trackBorder = _to_qcolor(v); self.update()
    trackBorder = Property(QColor, _get_trackBorder, _set_trackBorder)

    def _get_thumbFill(self) -> QColor: return self._thumbFill
    def _set_thumbFill(self, v) -> None: self._thumbFill = _to_qcolor(v); self.update()
    thumbFill = Property(QColor, _get_thumbFill, _set_thumbFill)

    def _get_thumbBorder(self) -> QColor: return self._thumbBorder
    def _set_thumbBorder(self, v) -> None: self._thumbBorder = _to_qcolor(v); self.update()
    thumbBorder = Property(QColor, _get_thumbBorder, _set_thumbBorder)

    def _get_textOn(self) -> QColor: return self._textOn
    def _set_textOn(self, v) -> None: self._textOn = _to_qcolor(v); self.update()
    textOn = Property(QColor, _get_textOn, _set_textOn)

    def _get_textOff(self) -> QColor: return self._textOff
    def _set_textOff(self, v) -> None: self._textOff = _to_qcolor(v); self.update()
    textOff = Property(QColor, _get_textOff, _set_textOff)

    def _get_trackDisabled(self) -> QColor: return self._trackDisabled
    def _set_trackDisabled(self, v) -> None: self._trackDisabled = _to_qcolor(v); self.update()
    trackDisabled = Property(QColor, _get_trackDisabled, _set_trackDisabled)

    def _get_textDisabled(self) -> QColor: return self._textDisabled
    def _set_textDisabled(self, v) -> None: self._textDisabled = _to_qcolor(v); self.update()
    textDisabled = Property(QColor, _get_textDisabled, _set_textDisabled)

    def _get_thumbDisabled(self) -> QColor: return self._thumbDisabled
    def _set_thumbDisabled(self, v) -> None: self._thumbDisabled = _to_qcolor(v); self.update()
    thumbDisabled = Property(QColor, _get_thumbDisabled, _set_thumbDisabled)

    # ---- painting ----
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        r = self.rect().adjusted(1, 1, -1, -1)
        radius = r.height() / 2

        enabled = self.isEnabled()
        checked = self.isChecked()

        if not enabled:
            track = self._trackDisabled
            text_col = self._textDisabled
            thumb_fill = self._thumbDisabled
        else:
            track = self._trackOn if checked else self._trackOff
            text_col = self._textOn if checked else self._textOff
            thumb_fill = self._thumbFill

        # Track
        p.setPen(QPen(self._trackBorder, 1))
        p.setBrush(track)
        p.drawRoundedRect(r, radius, radius)

        # Thumb
        margin = 2
        d = r.height() - 2 * margin
        x_min = r.left() + margin
        x_max = r.right() - margin - d
        x = x_min + (x_max - x_min) * self._offset
        thumb_rect = (int(x), r.top() + margin, int(d), int(d))

        p.setPen(QPen(self._thumbBorder, 1))
        p.setBrush(thumb_fill)
        p.drawEllipse(*thumb_rect)

        # Text
        p.setPen(text_col)
        text = self._text_on if checked else self._text_off
        pad = 10
        if checked:
            p.drawText(r.adjusted(pad, 0, -int(d) - pad, 0), Qt.AlignVCenter | Qt.AlignLeft, text)
        else:
            p.drawText(r.adjusted(int(d) + pad, 0, -pad, 0), Qt.AlignVCenter | Qt.AlignRight, text)