from datetime import datetime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(55), nullable=False, unique=True, index=True)
    email: str = Column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)

    posts = relationship("DBPost", back_populates="owner")
    comments = relationship("DBComment", back_populates="owner")


class DBPost(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(55), nullable=False)
    content = Column(String(511), nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="posts")
    comments = relationship("DBComment", back_populates="post")


class DBComment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"))
    owner_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_blocked = Column(Boolean, default=False)

    owner = relationship("User", back_populates="comments")
    post = relationship("DBPost", back_populates="comments")
