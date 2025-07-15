from pydantic import BaseModel, EmailStr
from enum import Enum

class FriendRequestCreate(BaseModel):
    receiver_email: EmailStr

class FriendRequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class FriendRequestResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: FriendRequestStatus

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class FriendSearchResult(BaseModel):
    email: EmailStr
    status: str

    class Config:
        orm_mode = True