from datetime import datetime
from typing import List
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
    invited_users_ids: List[str]
    created_at: datetime
    status: str

    class Config:
        orm_mode = True

class SessionInvitationRequest(BaseModel):
    emails: List[str]
