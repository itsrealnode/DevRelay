from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class InvestigationDto:
    id: int


class InvestigationStorage(Protocol):
    def get(self, investigation_id: int) -> InvestigationDto:
        ...

    def list(self) -> list[InvestigationDto]:
        """Return every visible investigation in storage order."""
        ...
