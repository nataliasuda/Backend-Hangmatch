from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    repeated_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class Message(BaseModel):
    message: str