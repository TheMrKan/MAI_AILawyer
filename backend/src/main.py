from src.application import logging

logging.setup()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.issue import router as issue_router
from src.api.laws import router as laws_router
from src.application import provider


@asynccontextmanager
async def lifespan(_app: FastAPI):
    provider_instance = await provider.build_async()
    provider.global_provider = provider_instance

    _app.dependency_overrides[provider.Provider] = lambda: provider_instance

    _app.include_router(issue_router)
    _app.include_router(laws_router)

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
