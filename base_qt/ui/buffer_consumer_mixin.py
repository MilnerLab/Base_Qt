from __future__ import annotations

from typing import Any, ClassVar


class BufferConsumerMixin:
    """
    Mixin for PanelVM subclasses that consume a shared-memory buffer.

    Subclass declares CONSUMER_ID and calls _setup_consumer(service) in __init__.
    Consumer registration is automatically undone in on_close() via MRO.

    Usage:
        class MyVM(BufferConsumerMixin, PanelVM):
            CONSUMER_ID: ClassVar[str] = "my_vm"

            def __init__(self, bus, dispatcher, svc, buffer):
                PanelVM.__init__(self, bus, dispatcher)
                self._setup_consumer(svc)
                ...
    """

    CONSUMER_ID: ClassVar[str]

    def _setup_consumer(self, service: Any) -> None:
        self._consumer_service = service
        service.add_consumer(self.CONSUMER_ID)

    def on_close(self) -> None:
        self._consumer_service.remove_consumer(self.CONSUMER_ID)
        super().on_close()  # type: ignore[misc]  # continues MRO to PanelVM.on_close
