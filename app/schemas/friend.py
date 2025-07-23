from pydantic import BaseModel, EmailStr
from enum import Enum

class FriendRequestCreate(BaseModel):
    receiver_email: EmailStr

class FriendRequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class FriendRequestResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    status: FriendRequestStatus

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class FriendSearchResult(BaseModel):
    email: EmailStr
    status: str

    class Config:
        orm_mode = True