from src.application import logging

logging.setup()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from src.api.issue import router as issue_router
from src.api.laws import router as laws_router
from src.api.routers import router as auth_router
from src.api.profile import router as profile_router
from src.application import provider

load_dotenv()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    from src.database.connection import create_tables
    await create_tables()

    provider_instance = await provider.build_async()
    provider.global_provider = provider_instance

    _app.dependency_overrides[provider.Provider] = lambda: provider_instance
    _app.dependency_overrides[provider.Scope] = lambda: provider.Scope(provider_instance)

    _app.include_router(issue_router)
    _app.include_router(laws_router)
    _app.include_router(auth_router)
    _app.include_router(profile_router)

    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
