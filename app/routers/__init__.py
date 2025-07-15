from fastapi import APIRouter
from . import user
from app.routers import session
from . import friend

router = APIRouter()
router.include_router(user.router, tags=["users"])
router.include_router(session.router, tags=["sessions"])
router.include_router(friend.router, tags=["friends"])