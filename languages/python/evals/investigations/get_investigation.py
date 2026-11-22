from typing import Callable, ContextManager

from storage import InvestigationDto, InvestigationStorage


class GetInvestigation:
    def __init__(self, uow: Callable[[], ContextManager[InvestigationStorage]]):
        self.uow = uow

    def __call__(self, investigation_id: int) -> InvestigationDto:
        with self.uow() as storage:
            return storage.get(investigation_id)
