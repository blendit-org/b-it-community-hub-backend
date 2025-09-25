from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import json
import logging

# Set up basic logging to see more details in Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assuming your models and database setup are in files named models.py and database.py
from . import models, database


# --- App Config ---
app = FastAPI(title="Community Q&A API")

models.Base.metadata.create_all(bind=database.engine)

origins = [
    "http://localhost:5173",
    "https://blendit-org.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

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

def get_or_create_tags(db: Session, tag_names: List[str]) -> List[models.Tag]:
    tags = []
    for name in tag_names:
        name = name.strip().lower()
        if not name: continue
        tag = db.query(models.Tag).filter(models.Tag.name == name).first()
        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)
    return tags

# --- Schemas ---
# Schemas remain the same...
class TagBase(BaseModel): name: str
class AnswerBase(BaseModel): userId: str; content: str
class QuestionBase(BaseModel): userId: str; title: str; content: str; tags: List[str] = []
class VoteRequest(BaseModel): direction: int
class AcceptAnswerRequest(BaseModel): userId: str
class ChatMessageBase(BaseModel): userId: str; message: str
class ChatMessageUpdate(BaseModel): message: str
class TagResponse(TagBase): id: int; 
class Config: from_attributes = True
class AnswerResponse(AnswerBase): id: int; question_id: int; createdAt: datetime; votes: int; is_accepted: bool; 
class Config: from_attributes = True
class QuestionResponse(BaseModel): id: int; userId: str; title: str; content: str; createdAt: datetime; votes: int; tags: List[TagResponse] = []; 
class Config: from_attributes = True
class QuestionDetailResponse(QuestionResponse): answers: List[AnswerResponse] = []
class PaginatedQuestionsResponse(BaseModel): questions: List[QuestionResponse]; total: int
class ChatMessageResponse(ChatMessageBase): id: int; createdAt: datetime; 
class Config: from_attributes = True




# --- API Routes (Questions & Answers) ---
# These routes remain the same...
@app.post("/questions", response_model=QuestionResponse)
def create_question(question: QuestionBase, db: Session = Depends(get_db)):
    user = get_or_create_user(db, question.userId)
    tags = get_or_create_tags(db, question.tags)
    new_question = models.Question(userId=user.userId, title=question.title, content=question.content, tags=tags)
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@app.get("/questions", response_model=PaginatedQuestionsResponse)
def get_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    questions_query = db.query(models.Question).order_by(models.Question.createdAt.desc())
    total_questions = questions_query.count()
    questions = questions_query.options(joinedload(models.Question.tags)).offset(skip).limit(limit).all()
    return {"questions": questions, "total": total_questions}

# Other Q&A routes...
@app.get("/questions/{question_id}", response_model=QuestionDetailResponse)
def get_question_details(question_id: int, db: Session = Depends(get_db)):
    question = db.query(models.Question).options(joinedload(models.Question.tags), joinedload(models.Question.answers)).filter(models.Question.id == question_id).first()
    if not question: raise HTTPException(status_code=404, detail="Question not found")
    question.answers.sort(key=lambda x: (not x.is_accepted, -x.votes))
    return question

@app.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question: raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return {"ok": True}

@app.post("/questions/{question_id}/answers", response_model=AnswerResponse)
def add_answer(question_id: int, answer: AnswerBase, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question: raise HTTPException(status_code=404, detail="Question not found")
    user = get_or_create_user(db, answer.userId)
    new_answer = models.Answer(question_id=question_id, userId=user.userId, content=answer.content)
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    return new_answer

@app.post("/questions/{question_id}/vote", response_model=QuestionResponse)
def vote_on_question(question_id: int, vote: VoteRequest, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question: raise HTTPException(status_code=404, detail="Question not found")
    question.votes += 1 if vote.direction == 1 else -1
    db.commit()
    db.refresh(question)
    return question

@app.post("/answers/{answer_id}/vote", response_model=AnswerResponse)
def vote_on_answer(answer_id: int, vote: VoteRequest, db: Session = Depends(get_db)):
    answer = db.query(models.Answer).filter(models.Answer.id == answer_id).first()
    if not answer: raise HTTPException(status_code=404, detail="Answer not found")
    answer.votes += 1 if vote.direction == 1 else -1
    db.commit()
    db.refresh(answer)
    return answer

@app.post("/answers/{answer_id}/accept", response_model=AnswerResponse)
def accept_an_answer(answer_id: int, request: AcceptAnswerRequest, db: Session = Depends(get_db)):
    answer_to_accept = db.query(models.Answer).options(joinedload(models.Answer.question)).filter(models.Answer.id == answer_id).first()
    if not answer_to_accept: raise HTTPException(status_code=404, detail="Answer not found")
    if answer_to_accept.question.userId != request.userId: raise HTTPException(status_code=403, detail="Only the question author can accept an answer")
    db.query(models.Answer).filter(models.Answer.question_id == answer_to_accept.question_id).update({"is_accepted": False})
    answer_to_accept.is_accepted = True
    db.commit()
    db.refresh(answer_to_accept)
    return answer_to_accept

# --- Chat History API Routes ---
# These routes remain the same...
@app.get("/chat", response_model=List[ChatMessageResponse])
def get_chat_history(db: Session = Depends(get_db)):
    return db.query(models.ChatMessage).order_by(models.ChatMessage.createdAt.asc()).all()

@app.put("/chat/{message_id}", response_model=ChatMessageResponse)
def update_chat_message(message_id: int, updated_message: ChatMessageUpdate, db: Session = Depends(get_db)):
    msg = db.query(models.ChatMessage).filter(models.ChatMessage.id == message_id).first()
    if not msg: raise HTTPException(status_code=404, detail="Chat message not found")
    msg.message = updated_message.message
    db.commit()
    db.refresh(msg)
    return msg

@app.delete("/chat/{message_id}", status_code=204)
def delete_chat_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(models.ChatMessage).filter(models.ChatMessage.id == message_id).first()
    if not msg: raise HTTPException(status_code=404, detail="Chat message not found")
    db.delete(msg)
    db.commit()
    return {"ok": True}

# --- Real-Time Chat WebSocket Endpoint (More Robust) ---
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    # This is the critical change: the connection is accepted FIRST.
    await manager.connect(websocket)
    db: Session = next(get_db())
    last_known_user_id = None
    
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            
            user_id = data.get("userId")
            message = data.get("message")
            last_known_user_id = user_id

            if not user_id or not message:
                logger.warning(f"Received malformed message: {data}")
                continue

            try:
                user = get_or_create_user(db, user_id)
                new_msg = models.ChatMessage(userId=user.userId, message=message)
                db.add(new_msg)
                db.commit()
                db.refresh(new_msg)
                
                response_data = {
                    "id": new_msg.id,
                    "userId": new_msg.userId,
                    "message": new_msg.message,
                    "createdAt": new_msg.createdAt.isoformat()
                }
                message_payload = {"type": "chat_message", "data": response_data}
                await manager.broadcast(json.dumps(message_payload))
            except Exception as e:
                logger.error(f"DB Error while handling message: {e}")
                db.rollback()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if last_known_user_id:
            leave_notification = {"type": "status", "message": f"User '{last_known_user_id}' has left the chat."}
            await manager.broadcast(json.dumps(leave_notification))
            
    except Exception as e:
        logger.error(f"An unexpected error occurred in WebSocket: {e}")
    finally:
        # Ensure resources are cleaned up
        if websocket in manager.active_connections:
            manager.disconnect(websocket)
        db.close()