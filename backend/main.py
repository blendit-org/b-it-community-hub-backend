from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# Assuming your models and database setup are in files named models.py and database.py
# in the same directory. If not, adjust the import path.
from . import models, database

# --- App Config ---
app = FastAPI(title="Community API")

# Ensure the database tables are created
models.Base.metadata.create_all(bind=database.engine)
# models.Base.metadata.create_all(bind=database.engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB Dependency ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper Functions ---
def get_or_create_user(db: Session, user_id: str):
    user = db.query(models.User).filter(models.User.userId == user_id).first()
    if not user:
        user = models.User(userId=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# --- Schemas ---
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

# Response Schemas
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

# PAGINATION FIX: New response model for paginated posts
class PaginatedPostsResponse(BaseModel):
    posts: List[PostResponse]
    total: int


# --- Routes ---

# Create Post
@app.post("/posts", response_model=PostResponse)
def create_post(post: PostBase, db: Session = Depends(get_db)):
    user = get_or_create_user(db, post.userId)
    new_post = models.Post(userId=user.userId, title=post.title, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# PAGINATION FIX: Updated Get All Posts endpoint
@app.get("/posts", response_model=PaginatedPostsResponse)
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts_query = db.query(models.Post).order_by(models.Post.createdAt.desc())
    
    total_posts = posts_query.count()
    
    posts = posts_query.offset(skip).limit(limit).all()
    
    return {"posts": posts, "total": total_posts}

# Delete Post
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"ok": True}

# Add Comment
@app.post("/posts/{post_id}/comments", response_model=CommentResponse)
def add_comment(post_id: int, comment: CommentBase, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    user = get_or_create_user(db, comment.userId)
    new_comment = models.Comment(postId=post_id, userId=user.userId, content=comment.content)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

# Get Comments for a Post
@app.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Comment)
        .filter(models.Comment.postId == post_id)
        .order_by(models.Comment.createdAt.asc())
        .all()
    )

# Delete Comment
@app.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return {"ok": True}


# Send Chat Message
@app.post("/chat/send", response_model=ChatMessageResponse)
def send_message(msg: ChatMessageBase, db: Session = Depends(get_db)):
    user = get_or_create_user(db, msg.userId)
    new_msg = models.ChatMessage(userId=user.userId, message=msg.message)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

# Get Chat Messages
@app.get("/chat", response_model=List[ChatMessageResponse])
def get_chat_messages(db: Session = Depends(get_db)):
    # Return messages in ascending order so new ones appear at the bottom
    return db.query(models.ChatMessage).order_by(models.ChatMessage.createdAt.asc()).all()

# Delete Chat Message
@app.delete("/chat/{chat_id}", status_code=204)
def delete_chat_message(chat_id: int, db: Session = Depends(get_db)):
    msg = db.query(models.ChatMessage).filter(models.ChatMessage.id == chat_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Chat message not found")
    db.delete(msg)
    db.commit()
    return {"ok": True}
