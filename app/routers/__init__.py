from fastapi import APIRouter
from . import user
from . import friend

router = APIRouter()
router.include_router(user.router, tags=["users"])
router.include_router(friend.router, tags=["friends"])