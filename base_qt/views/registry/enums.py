from enum import Enum, auto


class ViewKind(Enum):
    """
    Where/how a view should be shown by the shell.
    Extend as needed (TRAY, TOOLBAR, STATUS_PANEL, ...).
    """
    PAGE = auto()     # central area (tabs/stacked)
    DOCK = auto()     # QDockWidget
    DIALOG = auto()   # modal dialog (opened via action)
    POPOUT = auto()   # modeless window (opened via action)