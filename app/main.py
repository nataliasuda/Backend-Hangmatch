from fastapi import FastAPI
from app import auth

app = FastAPI(
    title="HangMatch API",
    description="RESTful API for managing sessions, users, and shared activity voting in the HangMatch app — designed for social interaction and decision-making.",
    version="1.0.0",
)
app.include_router(auth.router)