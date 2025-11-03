from pydantic import EmailStr, Field, BaseModel
from datetime import datetime

class UserSchema(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=10, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    repeat_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    age: int = Field(ge=1, le=100)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class PasswordSchema(BaseModel):
    old_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    new_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    repeat_new_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')

class UserDeleteSchema(BaseModel):
    password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')

class UserNameSchema(BaseModel):
    name: str = Field(min_length=1, max_length=10, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')

class ToDoSchema(BaseModel):
    task: str = Field(min_length=4, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s.?!]+$')
    date: datetime

class SubToDoSchema(BaseModel):
    task: str = Field(min_length=4, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s.?!]+$')