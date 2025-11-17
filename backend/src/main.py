from application import logging

logging.setup()

from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.issue import router as issue_router
from application import provider
from api.routers import router as auth_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from database.connection import create_tables
    await create_tables()

    provider_instance = await provider.build_async()
    provider.global_provider = provider_instance

    _app.dependency_overrides[provider.Provider] = lambda: provider_instance

    _app.include_router(issue_router)
    _app.include_router(auth_router)

    yield


app = FastAPI(lifespan=lifespan)