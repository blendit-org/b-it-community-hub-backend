````markdown
# Community API

**Community API** is a backend service built with **FastAPI** and **SQLAlchemy** for a community platform.  
It allows users to create posts, add comments, send chat messages, and manage data with full CRUD operations.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
  - [Posts](#posts)
  - [Comments](#comments)
  - [Chat](#chat)
- [Pagination](#pagination)
- [CORS](#cors)

---

## Features

- User management (automatic creation on first action)
- CRUD operations for Posts, Comments, and Chat Messages
- Paginated retrieval of posts
- Relational integrity with cascade deletes
- SQLAlchemy ORM for database interactions
- FastAPI type-safe requests/responses
- CORS enabled for all origins

---

## Tech Stack

- **Backend:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** MySQL / MariaDB
- **Data Validation:** Pydantic
- **Environment Variables:** python-dotenv

---

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/your-username/community-api.git
cd community-api
```
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory (see below).

4. Run the API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. API documentation is available at:

```
http://localhost:8000/docs
```

---

## Environment Variables

Create a `.env` file:

```dotenv
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/community
```

> `DATABASE_URL` format: `dialect+driver://username:password@host:port/database`

---

## Database Models

| Model           | Fields                                                          | Relations                       |
| --------------- | --------------------------------------------------------------- | ------------------------------- |
| **User**        | `userId` (PK)                                                   | `posts`, `comments`, `messages` |
| **Post**        | `id` (PK), `userId` (FK), `title`, `content`, `createdAt`       | `comments`                      |
| **Comment**     | `id` (PK), `postId` (FK), `userId` (FK), `content`, `createdAt` | None                            |
| **ChatMessage** | `id` (PK), `userId` (FK), `message`, `createdAt`                | None                            |

- Cascade Deletion: Deleting a post removes all associated comments.
- Automatic User Creation: Users are created on first post/comment/chat if they don’t exist.

---

## API Endpoints

### Posts

#### Create Post

**POST** `/posts`

**Request Body:**

```json
{
  "userId": "user123",
  "title": "My First Post",
  "content": "This is the content of my first post."
}
```

**Response:**

```json
{
  "id": 1,
  "userId": "user123",
  "title": "My First Post",
  "content": "This is the content of my first post.",
  "createdAt": "2025-09-21T12:34:56.789Z"
}
```

---

#### Get Posts (Paginated)

**GET** `/posts?skip=0&limit=10`

**Query Parameters:**

- `skip` (integer, default=0) – number of posts to skip
- `limit` (integer, default=10) – number of posts to return

**Response:**

```json
{
  "posts": [
    {
      "id": 1,
      "userId": "user123",
      "title": "My First Post",
      "content": "This is the content of my first post.",
      "createdAt": "2025-09-21T12:34:56.789Z"
    },
    {
      "id": 2,
      "userId": "user456",
      "title": "Another Post",
      "content": "Hello world!",
      "createdAt": "2025-09-21T12:35:56.123Z"
    }
  ],
  "total": 42
}
```

---

#### Delete Post

**DELETE** `/posts/{post_id}`

**Response:** `204 No Content`

```json
{
  "ok": true
}
```

---

### Comments

#### Add Comment

**POST** `/posts/{post_id}/comments`

**Request Body:**

```json
{
  "userId": "user123",
  "content": "This is a comment on the post."
}
```

**Response:**

```json
{
  "id": 1,
  "postId": 1,
  "userId": "user123",
  "content": "This is a comment on the post.",
  "createdAt": "2025-09-21T12:40:00.000Z"
}
```

---

#### Get Comments for a Post

**GET** `/posts/{post_id}/comments`

**Response:**

```json
[
  {
    "id": 1,
    "postId": 1,
    "userId": "user123",
    "content": "This is a comment on the post.",
    "createdAt": "2025-09-21T12:40:00.000Z"
  },
  {
    "id": 2,
    "postId": 1,
    "userId": "user456",
    "content": "Another comment.",
    "createdAt": "2025-09-21T12:41:00.000Z"
  }
]
```

---

#### Delete Comment

**DELETE** `/comments/{comment_id}`

**Response:** `204 No Content`

```json
{
  "ok": true
}
```

---

### Chat

#### Send Chat Message

**POST** `/chat/send`

**Request Body:**

```json
{
  "userId": "user123",
  "message": "Hello, community!"
}
```

**Response:**

```json
{
  "id": 1,
  "userId": "user123",
  "message": "Hello, community!",
  "createdAt": "2025-09-21T12:45:00.000Z"
}
```

---

#### Get Chat Messages

**GET** `/chat`

**Response:**

```json
[
  {
    "id": 1,
    "userId": "user123",
    "message": "Hello, community!",
    "createdAt": "2025-09-21T12:45:00.000Z"
  },
  {
    "id": 2,
    "userId": "user456",
    "message": "Hi there!",
    "createdAt": "2025-09-21T12:46:00.000Z"
  }
]
```

---

#### Delete Chat Message

**DELETE** `/chat/{chat_id}`

**Response:** `204 No Content`

```json
{
  "ok": true
}
```

---

## Pagination

- The `/posts` endpoint supports `skip` and `limit` query parameters.
- Response includes a `total` field for total post count.

---

## CORS

CORS is enabled for all origins, methods, and headers:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

Made with ❤️ using **FastAPI** and **SQLAlchemy**.
