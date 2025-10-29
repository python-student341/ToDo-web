from pydantic import EmailStr, Field, BaseModel
from datetime import datetime

class UserShema(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=10, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    repeat_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    age: int = Field(ge=1, le=100)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class ToDoSchema(BaseModel):
    task: str = Field(min_length=5, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s.?!]+$')
    date: datetime