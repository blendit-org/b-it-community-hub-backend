from pydantic import BaseModel
from typing import List
from datetime import datetime

class PostBase(BaseModel):
    userId: str
    title: str
    content: str

class CommentBase(BaseModel):
    userId: str
    content: str

class ChatMessageBase(BaseModel):
    userId: str
    message: str


class PostResponse(PostBase):
    id: int
    createdAt: datetime
    class Config:
        orm_mode = True

class CommentResponse(CommentBase):
    id: int
    postId: int
    createdAt: datetime
    class Config:
        orm_mode = True

class ChatMessageResponse(ChatMessageBase):
    id: int
    createdAt: datetime
    class Config:
        orm_mode = True

class PaginatedPostsResponse(BaseModel):
    posts: List[PostResponse]
    total: int
