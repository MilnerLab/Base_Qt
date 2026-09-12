from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from base_qt.ui.worker_control_widget import WorkerControlWidget, attach_worker_controls


class DeviceFrame(QWidget):
    """Pinned header, content, pinned footer -- the shape every device view has.

    One device is always the same three parts in the same order: its Start/Pause bar, its
    controls, and (for a settings form) Apply. This owns that arrangement so the two hosts
    that show a device -- the floating popout via ``PanelView``, and a block on the docked
    Devices page -- are literally the same widget structure rather than two imitations of
    each other.

    ``scrollable=True`` wraps the content in a QScrollArea, so the header and footer stay
    put however small the host gets. That is what a popout wants: one device in a window
    the operator drags down to nothing, where Start/Stop must never scroll out of reach.

    ``scrollable=False`` lets the content take its natural height instead. That is what a
    block on the Devices page wants: several of these stack inside ONE scroll area, and a
    block that scrolled internally would put a scrollbar inside a scrollbar. The page owns
    the scrolling; the block just states its true height.

    Header and footer start hidden, so a frame that never uses them costs no blank space.
    """

    def __init__(self, parent: QWidget | None = None, *, scrollable: bool = True) -> None:
        super().__init__(parent)
        self._scrollable = scrollable

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(8, 8, 8, 4)
        self.header_layout.setSpacing(8)
        self.header_widget.setVisible(False)
        outer.addWidget(self.header_widget)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(8, 8, 8, 8)
        self.body_layout.setSpacing(8)

        if scrollable:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            # Horizontal off, not AsNeeded: setWidgetResizable already keeps the content
            # at the viewport width, so a horizontal bar would only ever appear because a
            # single row refuses to shrink -- and then it steals height from the content.
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setWidget(self.body)
            # The only stretched child, so the header and footer collapse to their
            # sizeHint and the scroll area absorbs every pixel of a resize.
            outer.addWidget(scroll, stretch=1)
        else:
            outer.addWidget(self.body, stretch=1)

        self.footer_widget = QWidget()
        self.footer_layout = QHBoxLayout(self.footer_widget)
        self.footer_layout.setContentsMargins(8, 4, 8, 8)
        self.footer_layout.setSpacing(8)
        self.footer_widget.setVisible(False)
        outer.addWidget(self.footer_widget)

    def add_worker_controls(self, vm: Any) -> WorkerControlWidget:
        """Put this device's Start/Pause bar in the header, centered.

        Centered and on its own row in every host, so the control an operator reaches for
        under time pressure is in the same place on every device rather than moving with
        whatever happens to sit beside it.
        """
        ctrl = attach_worker_controls(vm, parent=self)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(ctrl)
        self.header_layout.addStretch(1)
        self.header_widget.setVisible(True)
        return ctrl
