from typing import Protocol
from uuid import UUID

from .dto import ExampleCreateInputDTO
from .entity import Example


class ExampleRepositoryProtocol(Protocol):
    async def create(self, input_data: ExampleCreateInputDTO) -> Example: ...

    async def get_by_id(self, example_id: UUID) -> Example | None: ...
