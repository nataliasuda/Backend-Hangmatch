from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import uuid

class SessionCreate(BaseModel):
    name: str
    location_radius: int
    invited_users_ids: List[int]

class SessionOut(BaseModel):
    id: str
    name: str
    location_radius: int
    owner_id: int
    invited_user_ids: Optional[List[int]] = []
    created_at: datetime

    class Config:
        from_attributes = True