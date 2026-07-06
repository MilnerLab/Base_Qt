from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from base_qt.ui.panel_view_model import PanelViewModel


class PanelView(QFrame):
    """
    A draggable floating widget overlaid on a parent panel.

    Unlike QDialog, this is a child QWidget (not a top-level OS window), so
    the WM never takes over dragging and the view is naturally constrained
    to the parent panel's bounds.

    Subclasses add their content to self.body_layout:

        class MyView(PanelView):
            def __init__(self, parent: QWidget) -> None:
                super().__init__("My Title", parent)
                self.body_layout.addWidget(...)

    Call open() to show it centered in the parent.

    Pass ``vm=`` for views constructed via a container factory (e.g. through
    ``ViewHost``): closing then calls ``vm.on_close()`` and destroys the
    widget, so the next ``ViewHost.open()`` rebuilds a fresh View/ViewModel
    pair. Views embedded inline with a borrowed, longer-lived VM (e.g.
    ``PhaseConfigView``) should omit ``vm=`` to keep the old hide-only close.
    """

    closed = Signal()

    def __init__(self, title: str, parent: QWidget, *, vm: PanelViewModel | None = None) -> None:
        super().__init__(parent)
        self.__dict__["vm"] = vm
        self.setObjectName("Card")
        self.setAutoFillBackground(True)
        self._drag_offset: QPoint | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Title bar — acts as the drag handle
        self._title_bar = QWidget()
        self._title_bar.setObjectName("popout_header")
        title_row = QHBoxLayout(self._title_bar)
        title_row.setContentsMargins(8, 0, 4, 0)
        title_row.setSpacing(4)

        lbl = QLabel(title)
        title_row.addWidget(lbl, stretch=1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setFlat(True)
        close_btn.clicked.connect(self._on_close)
        title_row.addWidget(close_btn)

        outer.addWidget(self._title_bar)

        body = QWidget()
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(8, 8, 8, 8)
        self.body_layout.setSpacing(8)
        outer.addWidget(body, stretch=1)

        self.hide()

    @property
    def vm(self) -> PanelViewModel | None:
        return self.__dict__.get("vm")

    def _on_close(self) -> None:
        if self.vm is not None:
            self.vm.on_close()
        self.hide()
        self.closed.emit()
        if self.vm is not None:
            self.deleteLater()

    def open(self) -> None:
        """Show the view centered in the parent and raise it to the front."""
        self.adjustSize()
        p = self.parentWidget()
        if p is not None:
            x = max(0, (p.width()  - self.width())  // 2)
            y = max(0, (p.height() - self.height()) // 2)
            self.move(x, y)
        self.show()
        self.raise_()

    # ── drag handling (title bar only) ──────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.MouseButton.LeftButton
                and self._title_bar.geometry().contains(event.pos())):
            self._drag_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = self.pos() + event.pos() - self._drag_offset
            p = self.parentWidget()
            if p is not None:
                x = max(0, min(new_pos.x(), p.width()  - self.width()))
                y = max(0, min(new_pos.y(), p.height() - self.height()))
                self.move(x, y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)
