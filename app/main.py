from fastapi import FastAPI
from app.database import engine, Base
from app.routers import router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="HangMatch API",
    description="RESTful API for managing sessions, users, and shared activity voting in the HangMatch app — designed for social interaction and decision-making.",
    version="1.0.0",
)

app.include_router(router)