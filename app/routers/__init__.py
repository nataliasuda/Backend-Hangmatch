from fastapi import APIRouter

from app.routers import session

from . import user



router = APIRouter()
router.include_router(user.router, tags=["users"])
router.include_router(session.router, tags=["sessions"])