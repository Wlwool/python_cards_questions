import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import admin, cards

os.makedirs("data", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Python Interview Cards API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
