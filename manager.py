import uuid
from typing import Optional
from passlib.context import CryptContext
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

import models
from db import SQLAlchemyUserDatabase
from models import User
from db import get_user_db

SECRET = "SECRET"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class UserManager(IntegerIDMixin, BaseUserManager[models.User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def authenticate(self, credentials) -> Optional[User]:
        email = credentials.username
        password = credentials.password
        user = await self.user_db.get_by_email(email)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    async def create(self, user_create, **kwargs):
        hashed_password = get_password_hash(user_create.password)
        user_dict = user_create.dict()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        created_user = await self.user_db.create(user_dict)
        return created_user


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
