import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# SQLAlchemy ORM Models

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String)
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    content = relationship("Content", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    likes = relationship("Like", back_populates="user")

class Content(Base):
    __tablename__ = "content"

    content_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="content")
    comments = relationship("Comment", back_populates="content")
    likes = relationship("Like", back_populates="content")

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    content = relationship("Content", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"

    like_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    content = relationship("Content", back_populates="likes")
    user = relationship("User", back_populates="likes")

    # Ensure a user can only like a content item once
    __table_args__ = (UniqueConstraint('content_id', 'user_id'),)


# Pydantic Models for API Responses and Requests

class UserPydantic(BaseModel):
    user_id: int
    email: str
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ContentPydantic(BaseModel):
    content_id: int
    user_id: int
    title: str
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author: Optional[UserPydantic] = None # Include author details

    model_config = ConfigDict(from_attributes=True)

class CommentPydantic(BaseModel):
    comment_id: int
    content_id: int
    user_id: int
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author: Optional[UserPydantic] = None # Include author details

    model_config = ConfigDict(from_attributes=True)

class LikePydantic(BaseModel):
    like_id: int
    content_id: int
    user_id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
