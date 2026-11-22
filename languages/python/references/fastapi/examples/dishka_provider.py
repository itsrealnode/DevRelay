from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from references.common.examples.repository_protocol import ExampleRepositoryProtocol
from references.common.examples.uow_protocol import ExampleUowProtocol
from references.common.examples.use_case import ExampleUseCase, GetExampleUseCase

from .sqlalchemy_repository import ExampleRepository
from .uow import ExampleUow


class ExampleProvider(Provider):
    def __init__(self, database_url: str) -> None:
        super().__init__()
        self._database_url = database_url

    @provide(scope=Scope.APP)
    async def engine(self) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(self._database_url)
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def session(self, engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
        async with AsyncSession(engine) as session:
            yield session

    uow = provide(ExampleUow, provides=ExampleUowProtocol, scope=Scope.REQUEST)
    repository = provide(ExampleRepository, provides=ExampleRepositoryProtocol, scope=Scope.REQUEST)
    use_case = provide(ExampleUseCase, scope=Scope.REQUEST)
    get_use_case = provide(GetExampleUseCase, scope=Scope.REQUEST)
