# models.py
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    userId = Column(String(100), primary_key=True, index=True)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    messages = relationship("ChatMessage", back_populates="author")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String(100), ForeignKey("users.userId", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    postId = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    userId = Column(String(100), ForeignKey("users.userId", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String(100), ForeignKey("users.userId", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="messages")
