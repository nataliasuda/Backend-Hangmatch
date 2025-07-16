from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class SessionCreate(BaseModel):
    name: str
    location_radius: int
    invited_users_ids: List[str]

class SessionOut(BaseModel):
    id: str
    name: str
    location_radius: int
    owner_id: str
    invited_user_ids: Optional[List[str]] = []
    created_at: datetime

    class Config:
        from_attributes = True