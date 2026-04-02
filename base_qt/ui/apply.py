# ui/apply.py
from __future__ import annotations

from PySide6.QtWidgets import QApplication
from base_qt.ui.theme.loader import apply_light_theme



def install_ui(app: QApplication) -> None:
    app.setStyle("Fusion")
    apply_light_theme(app)
