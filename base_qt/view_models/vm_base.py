from PySide6.QtCore import QObject

class VMBase(QObject):
    def connect(self):
        pass
    
    def disconnect(self):
        pass
    
    def dispose(self) -> None:
        self.disconnect()