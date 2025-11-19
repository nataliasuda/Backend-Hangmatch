from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

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
    sender_email: EmailStr
    receiver_email: EmailStr
    direction: str
    other_email: EmailStr
    other_name: str
    sender_name: str
    receiver_name: str 

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class FriendSearchResult(BaseModel):
    id: str
    email: EmailStr
    name: str
    status: str

    class Config:
        from_attributes = True

class FriendRespond(BaseModel):
    accept: bool
