from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.experiments.auth.config import settings
from backend.experiments.auth.routers import auth
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    from backend.experiments.auth.database.connection import create_tables
    await create_tables()
    logger.info("Application started")

@app.get("/")
async def root():
    return {"message": "SSO Auth Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}