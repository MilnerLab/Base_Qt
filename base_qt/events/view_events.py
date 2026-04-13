from dataclasses import dataclass


@dataclass(frozen=True)
class OpenViewRequested:
    view_id: strEvent