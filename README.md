# Blendit Community API

### Available: [https://blendit-community-production.up.railway.app](https://blendit-community-production.up.railway.app)

This is the backend server for the **Blendit Community Hub**, a feature-rich platform designed to foster interaction through a Q&A forum and a real-time chat. Built with **FastAPI** and **SQLAlchemy**, this API provides a robust foundation for a modern, interactive web application.

The application includes a Stack Overflow–style Q&A system with voting and tagging, plus a persistent, real-time chat powered by WebSockets.

---

## ✨ Features

### Q&A Platform

- Create, read, and delete questions.
- Post, read, and delete answers to questions.
- Upvote and downvote both questions and answers.
- Question authors can accept an answer as correct.
- Categorize questions with dynamic tags.

### Real-Time Chat

- Persistent chat history saved to the database.
- Live, bidirectional communication using WebSockets.
- Broadcast messages instantly to all connected clients.

### User Management

- Automatic user creation on their first interaction (posting, answering, etc.).

### Database

- Uses **SQLAlchemy ORM** for robust data modeling.
- Designed for **PostgreSQL**.

---

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Production Server:** Gunicorn + Uvicorn
- **Data Validation:** Pydantic

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Running PostgreSQL instance

### Local Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd blenditCommunity

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root with your database URL:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### Run the Development Server

```bash
uvicorn backend.main:app --reload
```

API will be available at:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📖 API Endpoints

### Questions

| Method | Endpoint                        | Description                                                | Example Body                                                                                   |
| ------ | ------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| POST   | `/questions`                    | Create a new question                                      | `{"userId": "user1", "title": "My Title", "content": "My Content", "tags": ["blender", "3D"]}` |
| GET    | `/questions`                    | Get a paginated list of all questions (`?skip=0&limit=10`) | –                                                                                              |
| GET    | `/questions/{question_id}`      | Get details + answers for a question                       | –                                                                                              |
| POST   | `/questions/{question_id}/vote` | Vote on a question                                         | `{"direction": 1}` (1 = up, -1 = down)                                                         |
| DELETE | `/questions/{question_id}`      | Delete a question                                          | –                                                                                              |

### Answers

| Method | Endpoint                           | Description       | Example Body                                  |
| ------ | ---------------------------------- | ----------------- | --------------------------------------------- |
| POST   | `/questions/{question_id}/answers` | Add an answer     | `{"userId": "user2", "content": "My Answer"}` |
| POST   | `/answers/{answer_id}/vote`        | Vote on an answer | `{"direction": 1}`                            |
| POST   | `/answers/{answer_id}/accept`      | Accept an answer  | `{"userId": "question_author_id"}`            |

### Chat History

| Method | Endpoint             | Description             |
| ------ | -------------------- | ----------------------- |
| GET    | `/chat`              | Get entire chat history |
| PUT    | `/chat/{message_id}` | Update a chat message   |
| DELETE | `/chat/{message_id}` | Delete a chat message   |

---

## 🔌 Real-Time Chat (WebSocket)

- **Endpoint:** `/ws/chat`
- **URL:** `ws://127.0.0.1:8000/ws/chat`

### Client → Server

```json
{
  "userId": "the_current_user_id",
  "message": "The message text to be sent."
}
```

### Server → Client

**New Chat Message:**

```json
{
  "type": "chat_message",
  "data": {
    "id": 101,
    "userId": "user_who_sent_it",
    "message": "The message text.",
    "createdAt": "2025-09-26T10:30:00.123Z"
  }
}
```

**Status Update (Join/Leave):**

```json
{
  "type": "status",
  "message": "User 'some_user' has left the chat."
}
```

---

## ☁️ Deployment

This backend is designed for persistent web services such as **Render** or **Railway**.

⚠️ Note: WebSockets require long-lived connections, so platforms like Vercel’s Hobby tier are not supported.

### Example Procfile

```bash
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

---

## License

MIT License
