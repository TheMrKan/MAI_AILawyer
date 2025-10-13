from fastapi import FastAPI

from src.api.issue import router as issue_router

app = FastAPI()

app.include_router(issue_router)
