from typing import List
from base_qt.views.registry.interfaces import IViewRegistry
from base_qt.views.registry.models import ViewSpec


class ViewRegistry(IViewRegistry):
    def __init__(self) -> None:
        self._specs: list[ViewSpec] = []

    def register(self, spec: ViewSpec) -> None:
        if any(s.id == spec.id for s in self._specs):
            raise ValueError(f"Duplicate ViewSpec id: {spec.id!r}")
        self._specs.append(spec)

    def list(self) -> List[ViewSpec]:
        return sorted(self._specs, key=lambda s: (s.order, s.title.lower()))