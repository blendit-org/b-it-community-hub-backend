from sqlalchemy import Boolean, Column, String, Text, ForeignKey, DateTime, Integer, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

# NEW: Association table for the many-to-many relationship between Questions and Tags
question_tags = Table('question_tags', Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    # No changes needed for the User table itself
    userId = Column(String(100), primary_key=True, index=True)

    # UPDATED: Relationships renamed for clarity
    questions = relationship("Question", back_populates="author")
    answers = relationship("Answer", back_populates="author")
    messages = relationship("ChatMessage", back_populates="author")


# UPDATED: 'Post' is now 'Question' with new features
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String(100), ForeignKey("users.userId", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    votes = Column(Integer, default=0) # NEW: For voting

    author = relationship("User", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete")
    tags = relationship("Tag", secondary=question_tags, back_populates="questions") # NEW: For tags


# UPDATED: 'Comment' is now 'Answer' with new features
class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False) # Renamed from postId
    userId = Column(String(100), ForeignKey("users.userId", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    votes = Column(Integer, default=0) # NEW: For voting
    is_accepted = Column(Boolean, default=False) # NEW: To mark the correct answer

    question = relationship("Question", back_populates="answers")
    author = relationship("User", back_populates="answers")


# NEW: Tag model for categorizing questions
class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    
    questions = relationship("Question", secondary=question_tags, back_populates="tags")


# No changes needed for the ChatMessage table
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String(100), ForeignKey("users.userId", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="messages")
