"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import DbSession, engine, init_db
from app.routers import notes, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()  # creates missing tables only; existing data is untouched
    yield
    await engine.dispose()


app = FastAPI(
    title="Users & Notes API",
    description=(
        "A small REST API that stores users and their notes permanently in SQLite "
        "using async SQLAlchemy 2.0. One user can have many notes."
    ),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "General", "description": "Service information and health check."},
        {"name": "Users", "description": "Create and read users."},
        {"name": "Notes", "description": "Full CRUD for notes that belong to a user."},
    ],
)

app.include_router(users.router)
app.include_router(notes.router)


@app.get("/", tags=["General"], summary="API information")
async def root() -> dict[str, str]:
    return {
        "message": "Users & Notes API is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["General"], summary="Health check")
async def health(db: DbSession) -> dict[str, str]:
    """Runs a trivial query to confirm the database connection works."""
    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Database is not reachable."
        )
    return {"status": "ok", "database": "connected"}
