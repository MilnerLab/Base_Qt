from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStyle,
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

        # Header — pinned below the title bar, above the scrollable body;
        # hidden until a subclass uses it (e.g. Start/Pause controls), so
        # popouts that never touch it don't get extra blank space.
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(8, 8, 8, 4)
        self.header_layout.setSpacing(8)
        self.header_widget.setVisible(False)
        outer.addWidget(self.header_widget)

        body = QWidget()
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(8, 8, 8, 8)
        self.body_layout.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(body)
        outer.addWidget(scroll, stretch=1)

        # Footer — pinned below the scrollable body; hidden until a subclass
        # uses it (e.g. DirtyForm/ConfigForm's Apply button), so plain
        # PanelView popouts that never touch it don't get extra blank space.
        self.footer_widget = QWidget()
        self.footer_layout = QHBoxLayout(self.footer_widget)
        self.footer_layout.setContentsMargins(8, 4, 8, 8)
        self.footer_layout.setSpacing(8)
        self.footer_widget.setVisible(False)
        outer.addWidget(self.footer_widget)

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
        body = self.body_layout.parentWidget()
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
        body = self.body_layout.parentWidget()
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
            margin = 24
            max_h = max(100, p.height() - margin)
            self.resize(self.width(), min(natural_h, max_h))
            x = max(0, (p.width()  - self.width())  // 2)
            y = max(0, (p.height() - self.height()) // 2)
            self.move(x, y)
        else:
            self.resize(self.width(), natural_h)
        self.show()
        self.raise_()

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
            min_h = 100
            # Cap growth at the content's natural (uncompressed) height — i.e.
            # never drag past the point where the vertical scrollbar
            # disappears, and never past the parent's bottom edge either,
            # whichever is smaller.
            natural_h = self._natural_height()
            max_h = min(p.height() - self.y(), natural_h) if p is not None else natural_h
            new_h = max(min_h, min(self._resize_start_height + delta, max_h))
            self.resize(self.width(), new_h)
        elif self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = self.pos() + event.pos() - self._drag_offset
            p = self.parentWidget()
            if p is not None:
                x = max(0, min(new_pos.x(), p.width()  - self.width()))
                y = max(0, min(new_pos.y(), p.height() - self.height()))
                self.move(x, y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._resize_offset_y = None
        self._resize_start_height = None
        self._drag_offset = None
        super().mouseReleaseEvent(event)
