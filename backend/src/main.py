import src.logs

src.logs.setup()

from fastapi import FastAPI

from src.api.issue import router as issue_router
from src.core.container import Container

app = FastAPI()


Container.build()

app.include_router(issue_router)
