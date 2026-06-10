from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QToolButton, QWidget

from base_qt.ui.app_message import AppMessage, MessageLevel

_MAX_TEXT_PX = 340


class StatusArea(QWidget):
    """
    Menubar corner widget that shows application messages.

    INFO messages display transiently for 6 s and are not stored.
    WARNING and ERROR messages are collected in a persistent list.
    The user can navigate through the list with ← / → and delete
    entries with ✕.  A "2/5" counter shows the current position.

    When a new warning or error arrives the view jumps to it automatically.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._msgs: list[AppMessage] = []
        self._idx: int = -1
        self._showing_info: bool = False

        self._info_timer = QTimer(self)
        self._info_timer.setSingleShot(True)
        self._info_timer.timeout.connect(self._on_info_expired)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 0, 8, 0)
        lay.setSpacing(3)

        self._prev_btn = _nav_button("←")
        self._prev_btn.clicked.connect(self._go_prev)

        self._dot = QLabel()
        self._dot.setObjectName("status_dot")
        self._dot.setFixedSize(8, 8)

        self._text = QLabel()
        self._text.setObjectName("status_text")
        self._text.setMaximumWidth(_MAX_TEXT_PX)

        self._counter = QLabel()
        self._counter.setObjectName("status_counter")

        self._next_btn = _nav_button("→")
        self._next_btn.clicked.connect(self._go_next)

        self._del_btn = _nav_button("✕")
        self._del_btn.clicked.connect(self._delete_current)

        for w in (self._prev_btn, self._dot, self._text,
                  self._counter, self._next_btn, self._del_btn):
            lay.addWidget(w)

        self._refresh()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def push(self, msg: AppMessage) -> None:
        if msg.level is MessageLevel.INFO:
            self._showing_info = True
            self._info_timer.start(6_000)
            self._refresh(transient_text=msg.text)
        else:
            self._msgs.append(msg)
            self._idx = len(self._msgs) - 1
            self._showing_info = False
            self._info_timer.stop()
            self._refresh()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _go_prev(self) -> None:
        if self._idx > 0:
            self._idx -= 1
            self._showing_info = False
            self._refresh()

    def _go_next(self) -> None:
        if self._idx < len(self._msgs) - 1:
            self._idx += 1
            self._showing_info = False
            self._refresh()

    def _delete_current(self) -> None:
        if not self._msgs or self._idx < 0:
            return
        self._msgs.pop(self._idx)
        self._idx = max(0, min(self._idx, len(self._msgs) - 1))
        if not self._msgs:
            self._idx = -1
        self._refresh()

    def _on_info_expired(self) -> None:
        self._showing_info = False
        self._refresh()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _refresh(self, transient_text: str = "") -> None:
        if self._showing_info:
            self._set_level("info")
            self._set_text(transient_text)
            self._set_counter("")
            self._show_nav(False)
        elif self._msgs and self._idx >= 0:
            msg = self._msgs[self._idx]
            n = len(self._msgs)
            self._set_level(msg.level.value)
            self._set_text(msg.text)
            self._set_counter(f"{self._idx + 1}/{n}")
            self._prev_btn.setEnabled(self._idx > 0)
            self._next_btn.setEnabled(self._idx < n - 1)
            self._show_nav(True)
        else:
            self._set_level("")
            self._set_text("")
            self._set_counter("")
            self._show_nav(False)

    def _set_text(self, text: str) -> None:
        fm   = self._text.fontMetrics()
        elided = fm.elidedText(text, Qt.TextElideMode.ElideRight, _MAX_TEXT_PX)
        self._text.setText(elided)
        self._text.setToolTip(text if elided != text else "")

    def _set_counter(self, text: str) -> None:
        self._counter.setText(text)

    def _set_level(self, level: str) -> None:
        for w in (self._dot, self._text):
            w.setProperty("level", level)
            w.style().unpolish(w)
            w.style().polish(w)

    def _show_nav(self, visible: bool) -> None:
        for w in (self._prev_btn, self._counter, self._next_btn, self._del_btn):
            w.setVisible(visible)


def _nav_button(symbol: str) -> QToolButton:
    btn = QToolButton()
    btn.setText(symbol)
    btn.setAutoRaise(True)
    btn.setObjectName("status_nav_btn")
    return btn
