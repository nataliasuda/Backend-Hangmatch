from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.database import engine, Base
from app.routers import router

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)


avatars_dir = static_dir / "avatars"
avatars_dir.mkdir(exist_ok=True)

app = FastAPI(
    title="HangMatch API",
    description="RESTful API for managing sessions, users, friends and shared activity voting in the HangMatch app — designed for social interaction and decision-making.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)
app.include_router(router)