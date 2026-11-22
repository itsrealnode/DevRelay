from uuid import UUID

from .dto import ExampleCreateInputDTO, ExampleDTO
from .entity import Example
from .repository_protocol import ExampleRepositoryProtocol
from .uow_protocol import ExampleUowProtocol
from .use_case_protocol import IUseCase


def _to_dto(example: Example) -> ExampleDTO:
    return ExampleDTO(id=example.id, title=example.title, description=example.description)


class ExampleUseCase(IUseCase[ExampleCreateInputDTO, ExampleDTO]):
    def __init__(self, *, db_uow: ExampleUowProtocol, example_storage: ExampleRepositoryProtocol) -> None:
        self.__db_uow = db_uow
        self.__example_storage = example_storage

    async def __call__(self, *, input_data: ExampleCreateInputDTO) -> ExampleDTO:
        async with self.__db_uow:
            example = await self.__example_storage.create(input_data=input_data)
            return _to_dto(example)


class GetExampleUseCase(IUseCase[UUID, ExampleDTO | None]):
    def __init__(self, *, db_uow: ExampleUowProtocol, example_storage: ExampleRepositoryProtocol) -> None:
        self.__db_uow = db_uow
        self.__example_storage = example_storage

    async def __call__(self, *, input_data: UUID) -> ExampleDTO | None:
        async with self.__db_uow:
            example = await self.__example_storage.get_by_id(example_id=input_data)
            return _to_dto(example) if example is not None else None
