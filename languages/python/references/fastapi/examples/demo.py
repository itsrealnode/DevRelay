from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from .dishka_provider import ExampleProvider
from .models import ExampleBase
from .router import router


def create_app() -> FastAPI:
    container = make_async_container(ExampleProvider("sqlite+aiosqlite:///:memory:"))

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            engine = await container.get(AsyncEngine)
            async with engine.begin() as connection:
                await connection.run_sync(ExampleBase.metadata.create_all)
            yield
        finally:
            await container.close()

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    setup_dishka(container, app)
    return app
