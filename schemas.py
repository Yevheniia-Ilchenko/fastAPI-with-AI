from fastapi_users import schemas
from pydantic import BaseModel
from datetime import datetime


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    title: str
    content: str


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    content: str
    post_id: int


class CommentRead(BaseModel):
    id: int
    content: str
    post_id: int
    owner_id: int
    created_at: datetime
    is_blocked: bool

    class Config:
        orm_mode = True
