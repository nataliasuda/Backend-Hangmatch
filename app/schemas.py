from pydantic import BaseModel, EmailStr, validator
import re
from typing import List

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    repeated_password: str

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value

    @validator("name")
    def validate_name(cls, value):
        if not value[0].isupper():
            raise ValueError("Name must start with a capital letter")
        return value

    @validator("repeated_password")
    def passwords_match(cls, value, values):
        if "password" in values and value != values["password"]:
            raise ValueError("Passwords do not match")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class SessionCreate(BaseModel):
    name: str
    location_radius: int
    invited_users_ids: List[int]

class SessionOut(BaseModel):
    id: int
    name: str
    location_radius: int
    owner_id: int
    invited_users_ids: List[int]

    class Config:
        from_attributes = True