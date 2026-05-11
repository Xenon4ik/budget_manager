from fastapi import FastAPI

from app import models
from app.database import engine
from app.routers import analytics, auth, categories, goals, transactions

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Budget Manager API",
    description="REST API for personal budget management.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(goals.router)
app.include_router(analytics.router)


@app.get("/")
def root() -> dict[str, str]:
    """Return a simple health-check message."""
    return {
        "message": "Budget Manager API is running",
    }
