from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from references.common.examples.dto import ExampleCreateInputDTO
from references.common.examples.entity import Example

from .models import ExampleModel


class ExampleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, input_data: ExampleCreateInputDTO) -> Example:
        stmt = (
            insert(ExampleModel)
            .values(title=input_data.title, description=input_data.description)
            .returning(ExampleModel)
        )
        record = (await self._session.scalars(stmt)).one()
        return self._to_entity(record)

    async def get_by_id(self, example_id: UUID) -> Example | None:
        stmt = select(ExampleModel).where(ExampleModel.id == example_id)
        record = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._to_entity(record) if record is not None else None

    @staticmethod
    def _to_entity(record: ExampleModel) -> Example:
        return Example(id=record.id, title=record.title, description=record.description)
