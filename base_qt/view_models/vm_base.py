from PySide6.QtCore import QObject

class VMBase(QObject):
    def on_connect(self):
        pass
    
    def on_disconnect(self):
        pass
    
    def dispose(self) -> None:
        self.on_disconnect()