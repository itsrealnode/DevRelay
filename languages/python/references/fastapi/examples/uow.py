from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession


class ExampleUow:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> Self:
        await self._session.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            await self._session.commit()
        else:
            await self._session.rollback()
