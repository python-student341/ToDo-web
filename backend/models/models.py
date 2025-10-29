from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime

from database.database import Base

class UserModel(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()

    todos = relationship('ToDoModel', back_populates='user')

class ToDoModel(Base):
    __tablename__ = 'ToDo'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    task: Mapped[str] = mapped_column()
    date: Mapped[datetime] = mapped_column()

    user = relationship('UserModel', back_populates='todos')