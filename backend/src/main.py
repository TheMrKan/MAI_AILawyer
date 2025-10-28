from src.application import logging

logging.setup()

from fastapi import FastAPI

from src.api.issue import router as issue_router
from src.application import provider

provider_instance = provider.build()
provider.global_provider = provider_instance

app = FastAPI()
app.dependency_overrides[provider.Provider] =  lambda: provider_instance

app.include_router(issue_router)
