import src.logs

src.logs.setup()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.issue import router as issue_router
from src.core.container import Container

app = FastAPI()

origins = [
    "*",  # Allows all origins (not recommended for production)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # allow methods
    allow_headers=["*"], # allow headers
)


Container.build()

app.include_router(issue_router)
