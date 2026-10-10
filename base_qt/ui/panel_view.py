from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from base_qt.ui.device_frame import DeviceFrame
from base_qt.ui.panel_view_model import PanelViewModel
from base_qt.ui.worker_control_widget import WorkerControlWidget


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

    def __init__(self, title: str, parent: QWidget | None, *, vm: PanelViewModel | None = None) -> None:
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
        close_btn.setObjectName("popout_close")
        close_btn.setFixedSize(20, 20)
        close_btn.setFlat(True)
        close_btn.clicked.connect(self._on_close)
        title_row.addWidget(close_btn)

        outer.addWidget(self._title_bar)

        # The device frame does the actual work — pinned header, scrolling body, pinned
        # footer. Scrollable here because a popout is one device in a window the operator
        # can drag down to nothing, and Start/Stop must survive that. It is the only
        # stretched child, so the title bar and resize handle keep their sizeHint.
        self._frame = DeviceFrame(scrollable=True)
        outer.addWidget(self._frame, stretch=1)

        # Resize handle — always visible; lets the user drag to adjust
        # height only (width is fixed to content in open()). QSizeGrip isn't
        # usable here since it resizes window(), i.e. the top-level ancestor,
        # not this child widget — so this is hand-rolled like the title-bar
        # drag above, for the same reason.
        self._resize_handle = QWidget()
        self._resize_handle.setObjectName("popout_resize_handle")
        self._resize_handle.setFixedHeight(8)
        self._resize_handle.setCursor(Qt.CursorShape.SizeVerCursor)
        outer.addWidget(self._resize_handle)
        self._resize_offset_y: int | None = None
        self._resize_start_height: int | None = None

        self._watched_parent: QWidget | None = None
        self._watch_parent()

        self.hide()

    @property
    def vm(self) -> PanelViewModel | None:
        return self.__dict__.get("vm")

    # -- the frame's slots, forwarded so subclasses read as they always have ------------

    @property
    def header_widget(self) -> QWidget:
        return self._frame.header_widget

    @property
    def header_layout(self) -> QHBoxLayout:
        return self._frame.header_layout

    @property
    def body_layout(self) -> QVBoxLayout:
        return self._frame.body_layout

    @property
    def footer_widget(self) -> QWidget:
        return self._frame.footer_widget

    @property
    def footer_layout(self) -> QHBoxLayout:
        return self._frame.footer_layout

    def add_worker_controls(self, vm: Any) -> WorkerControlWidget:
        """Pin this device's Start/Pause bar in the header, centered. See DeviceFrame."""
        return self._frame.add_worker_controls(vm)

    def _on_close(self) -> None:
        if self.vm is not None:
            self.vm.on_close()
        self.hide()
        self.closed.emit()
        if self.vm is not None:
            self.deleteLater()

    def _natural_height(self) -> int:
        """Total height with no vertical scrollbar needed — the height at
        which the scrollbar disappears.

        Computed by summing each section's own sizeHint directly rather than
        via self.sizeHint()/QScrollArea.sizeHint(): QScrollArea internally
        clamps its sizeHint to a fixed maximum regardless of the actual
        widget size (verified empirically — ~400px in this environment),
        which silently truncated this for any popout with enough fields to
        exceed that clamp (e.g. PhaseConfigView, but not the smaller
        SpectrometerView), capping growth/initial size far below the true
        content height.

        Uses isHidden() rather than isVisible() for header_widget/
        footer_widget: this runs from open(), before self.show() — at that
        point isVisible() (actual on-screen visibility) is always False
        because the whole popout itself isn't shown yet, even if a subclass
        already called header_widget/footer_widget.setVisible(True) (e.g.
        DirtyForm's footer). isHidden() reflects the widget's own explicit
        shown/hidden flag regardless of its ancestors' current visibility.
        """
        body = self._frame.body
        h = self._title_bar.sizeHint().height() + body.sizeHint().height() + self._resize_handle.height()
        if not self.header_widget.isHidden():
            h += self.header_widget.sizeHint().height()
        if not self.footer_widget.isHidden():
            h += self.footer_widget.sizeHint().height()
        return h

    def open(self) -> None:
        """Show the view centered in the parent and raise it to the front."""
        # Width tracks content exactly (only as wide as needed), reserving
        # room for the vertical scrollbar so it never eats into the content's
        # required width and forces an unwanted horizontal scrollbar too.
        # Recomputed every open() so it stays correct even if a subclass adds
        # header/footer content after construction.
        body = self._frame.body
        sb_extent = self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
        content_widths = [body.sizeHint().width()]
        # isHidden(), not isVisible() — see _natural_height()'s docstring:
        # this runs before self.show(), so isVisible() would always be False.
        if not self.header_widget.isHidden():
            content_widths.append(self.header_widget.sizeHint().width())
        if not self.footer_widget.isHidden():
            content_widths.append(self.footer_widget.sizeHint().width())
        natural_w = max(content_widths) + sb_extent + 2
        self.setFixedWidth(natural_w)

        natural_h = self._natural_height()
        p = self.parentWidget()
        if p is not None:
            area = self._visible_area()
            # Open at most OPEN_FRACTION of the visible height, so the lower edge and its
            # resize handle always start well inside view; drag down for more.
            max_h = max(self._MIN_H, int(area.height() * self._OPEN_FRACTION))
            self.resize(self.width(), min(natural_h, max_h))
            x = max(0, area.x() + (area.width()  - self.width())  // 2)
            y = max(0, area.y() + (area.height() - self.height()) // 2)
            self.move(x, y)
        else:
            self.resize(self.width(), natural_h)
        self.show()
        self.raise_()

    _MIN_H = 100
    _OPEN_FRACTION = 0.75
    _MARGIN = 8

    def _visible_area(self) -> QRect:
        """The part of the parent the operator can actually see, in parent coordinates.

        NOT ``parent.rect()``: a parent taller than the screen (a window extending past the
        taskbar, a dock clipped by its main window) has a height nobody can see, and sizing
        against it put the popout's bottom rows and resize handle off-view -- the scroll area
        believed everything was shown, so there was nothing left to scroll to.
        """
        p = self.parentWidget()
        assert p is not None
        area = p.rect()
        if p.isVisible():
            clip = p.visibleRegion().boundingRect()
            if not clip.isEmpty():
                area = area.intersected(clip)
        screen = p.screen()
        if screen is not None:
            g = screen.availableGeometry()
            on_screen = QRect(p.mapFromGlobal(g.topLeft()), p.mapFromGlobal(g.bottomRight()))
            clipped = area.intersected(on_screen)
            if not clipped.isEmpty():
                area = clipped
        return area.adjusted(0, 0, 0, -self._MARGIN)

    def _fit_into_visible_area(self) -> None:
        """Pull the popout back inside the visible area, shrinking it if it cannot fit."""
        if self.parentWidget() is None or not self.isVisible():
            return
        area = self._visible_area()
        h = max(self._MIN_H, min(self.height(), area.height()))
        if h != self.height():
            self.resize(self.width(), h)
        x = max(area.left(), min(self.x(), area.right() + 1 - self.width()))
        y = max(area.top(), min(self.y(), area.bottom() + 1 - self.height()))
        if (x, y) != (self.x(), self.y()):
            self.move(max(0, x), max(0, y))

    def _watch_parent(self) -> None:
        """Point the resize/move filter at the current parent.

        Keeps the popout inside the visible part of the parent when the parent resizes.
        Without this, shrinking the window leaves the popout's lower edge -- and with it
        the resize handle and the last rows -- clipped off where no drag can reach.

        Deferred rather than done once in __init__: a view resolved through ``ViewHost``
        is built with parent=None and only reparented under the shell afterwards, so the
        constructor has no parent to watch. Called again on every ParentChange, and it
        drops the previous filter first -- a singleton view survives close/open and would
        otherwise stack a filter per reparent.
        """
        p = self.parentWidget()
        if p is self._watched_parent:
            return
        if self._watched_parent is not None:
            self._watched_parent.removeEventFilter(self)
        self._watched_parent = p
        if p is not None:
            p.installEventFilter(self)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.ParentChange:
            self._watch_parent()
        super().changeEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.parentWidget() and event.type() in (QEvent.Type.Resize,
                                                               QEvent.Type.Move):
            self._fit_into_visible_area()
        return super().eventFilter(watched, event)

    # ── drag handling (title bar only) ──────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self._resize_handle.geometry().contains(event.pos()):
                self._resize_offset_y = event.pos().y()
                self._resize_start_height = self.height()
            elif self._title_bar.geometry().contains(event.pos()):
                self._drag_offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._resize_offset_y is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.pos().y() - self._resize_offset_y
            p = self.parentWidget()
            # Cap growth at the content's natural (uncompressed) height — i.e.
            # never drag past the point where the vertical scrollbar
            # disappears, and never past the VISIBLE bottom edge of the parent
            # either, whichever is smaller — past it the handle is unreachable.
            natural_h = self._natural_height()
            max_h = (min(self._visible_area().bottom() + 1 - self.y(), natural_h)
                     if p is not None else natural_h)
            new_h = max(self._MIN_H, min(self._resize_start_height + delta, max_h))
            self.resize(self.width(), new_h)
        elif self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = self.pos() + event.pos() - self._drag_offset
            p = self.parentWidget()
            if p is not None:
                area = self._visible_area()
                x = max(0, min(new_pos.x(), p.width()  - self.width()))
                y = max(0, min(new_pos.y(), area.bottom() + 1 - self.height()))
                self.move(x, y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._resize_offset_y = None
        self._resize_start_height = None
        self._drag_offset = None
        super().mouseReleaseEvent(event)
