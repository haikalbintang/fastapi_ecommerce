from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import logging

from db import main as init_db
from .dependencies import get_token_header
from .internal import admin_router
from .routers import users_router, products_router, auth_router


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_):
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized and seeded successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title="My FastAPI App",
    description="A clean and modular FastAPI application",
    version="1.0.0",
    lifespan=lifespan,
    # dependencies=[Depends(get_query_token)]
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)

app.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello Bigger Applications!"}