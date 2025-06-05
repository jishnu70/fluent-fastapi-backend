from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    public_key: str

class UserLogin(BaseModel):
    username: str
    password: str