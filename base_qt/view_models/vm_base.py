from PySide6.QtCore import QObject

class VMBase(QObject):
    def on_connect(self):
        self.connect()
    
    def on_disconnect(self):
        self.disconnect()
    
    def dispose(self) -> None:
        self.on_disconnect()