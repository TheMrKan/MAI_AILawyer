from src.application import logging

logging.setup()

from fastapi import FastAPI

from src.api.issue import router as issue_router
from src.application.provider import build as build_provider

provider = build_provider()
app = FastAPI()
for iface, factory in provider.mapping.items():
    # lambda, т. к. входные аргументы фабрики он пытается извлечь из запроса
    def fastapi_factory(f):
        return lambda: f()
    app.dependency_overrides[iface] = fastapi_factory(factory)

app.include_router(issue_router)
