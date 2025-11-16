from pydantic import BaseModel, EmailStr, validator
import re

from typing import Optional

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
    id: str
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    password: Optional[str] = None
    repeated_password: Optional[str] = None

    @validator("password")
    def validate_password(cls, value, values):
        if value is None:
            return value 
            
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value

    @validator("repeated_password")
    def passwords_match(cls, value, values):
        if "password" in values and values["password"] is not None and values["password"] != "":
            if value != values["password"]:
                raise ValueError("Passwords do not match")
        return value