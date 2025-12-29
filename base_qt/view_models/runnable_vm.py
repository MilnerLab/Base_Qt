from base_core.framework.events import EventBus
from base_qt.view_models.thread_safe_vm_base import ThreadSafeVMBase
from base_qt.app.interfaces import IUiDispatcher
from base_core.framework.domain.interfaces import IRunnable
from base_core.framework.services.runnable_service_base import RunnableServiceBase


class RunnableVMBase(ThreadSafeVMBase, IRunnable):
    
    def __init__(self, engine_service: RunnableServiceBase, ui: IUiDispatcher, bus: EventBus):
        super().__init__(ui, bus)
        self._engine = engine_service
    
    def run(self) -> None:
        self._engine.start()
        
    def stop(self) -> None:
        self._engine.stop()
        
    def reset(self) -> None:
        self._engine.reset()
