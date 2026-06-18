from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable


@runtime_checkable
class BufferOutput(Protocol):
    def register_consumer(self, consumer_id: str) -> None: ...
    def unregister_consumer(self, consumer_id: str) -> None: ...



class BufferConsumerMixin:
    """
    Mixin for PanelVM subclasses that consume one or more shared-memory buffers.

    Subclass declares CONSUMER_ID and calls _setup_consumer(*outputs) in __init__.
    Consumer registration is automatically undone in on_close() via MRO.

    Usage:
        class MyVM(BufferConsumerMixin, PanelVM):
            CONSUMER_ID: ClassVar[str] = "my_vm"

            def __init__(self, bus, dispatcher, svc, buffer):
                PanelVM.__init__(self, bus, dispatcher)
                self._setup_consumer(svc.output)
                ...
    """

    CONSUMER_ID: ClassVar[str]

    def _setup_consumer(self, *outputs: BufferOutput) -> None:
        self._consumer_outputs = outputs
        for output in outputs:
            output.register_consumer(self.CONSUMER_ID)

    def on_close(self) -> None:
        for output in self._consumer_outputs:
            output.unregister_consumer(self.CONSUMER_ID)
        super().on_close()  # type: ignore[misc]  # continues MRO to PanelVM.on_close
