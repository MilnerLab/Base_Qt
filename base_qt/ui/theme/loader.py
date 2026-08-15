from __future__ import annotations

from enum import Enum
from importlib import resources
from typing import Mapping

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from .tokens import TOKENS, as_qss_replacements


class ThemeMode(str, Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


_SETTINGS_KEY = "ui/theme_mode"


def _render_qss(qss_text: str, replacements: Mapping[str, str]) -> str:
    for k, v in replacements.items():
        qss_text = qss_text.replace(f"@{k}@", v)
    return qss_text


def _load_qss(filename: str) -> str:
    return resources.files(__package__).joinpath(filename).read_text(encoding="utf-8")


def effective_mode(app: QApplication, mode: ThemeMode) -> ThemeMode:
    # SYSTEM always resolves to DARK: the app intentionally uses the same
    # dark theme on every machine rather than following the OS preference.
    if mode is ThemeMode.SYSTEM:
        return ThemeMode.DARK
    return mode


def get_saved_theme_mode() -> ThemeMode:
    s = QSettings()
    raw = str(s.value(_SETTINGS_KEY, ThemeMode.SYSTEM.value))
    return ThemeMode(raw) if raw in {m.value for m in ThemeMode} else ThemeMode.SYSTEM


def save_theme_mode(mode: ThemeMode) -> None:
    s = QSettings()
    s.setValue(_SETTINGS_KEY, mode.value)


def apply_theme(app: QApplication, mode: ThemeMode) -> None:
    mode_eff = effective_mode(app, mode)

    base = _load_qss("base.qss")
    themed = _load_qss("dark.qss" if mode_eff is ThemeMode.DARK else "light.qss")

    qss = base + "\n\n" + themed
    qss = _render_qss(qss, as_qss_replacements(TOKENS))
    app.setStyleSheet(qss)


def apply_saved_theme(app: QApplication) -> None:
    apply_theme(app, get_saved_theme_mode())
