from __future__ import annotations

from typing import Generic, TypeVar

from PySide6.QtCore import QObject, Signal

T = TypeVar("T")


class FieldDraft(QObject, Generic[T]):
    """Tracks a pending (typed) value separately from the last committed value.

    Emits dirty_changed(True) when pending diverges from committed, and
    dirty_changed(False) when they match again or commit() is called.
    """

    dirty_changed = Signal(bool)

    def __init__(self, initial: T, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._committed: T = initial
        self._pending: T = initial

    def set(self, value: T) -> None:
        self._pending = value
        self.dirty_changed.emit(self._pending != self._committed)

    def commit(self) -> T:
        """Adopt pending as committed. Returns the committed value."""
        self._committed = self._pending
        self.dirty_changed.emit(False)
        return self._committed

    @property
    def is_dirty(self) -> bool:
        return self._pending != self._committed

    @property
    def pending(self) -> T:
        return self._pending

    @property
    def committed(self) -> T:
        return self._committed
