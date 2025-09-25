# Havana Chatbot Backend

This is the backend for the Trade School Chatbot project. It provides:

- REST API endpoints for creating chats, sending messages, and managing status.  
- WebSocket support for **real-time chat updates** between users, AI, and admins.  
- OpenAI integration for automated AI responses.  
- Function calls to **escalate chats to a human** or **book a call**.  
- SQLAlchemy ORM with either SQLite (for dev) or PostgreSQL (for production).  
- Docker support for easy deployment.  

---

# How to Run This Project

## Prerequisites

- [Git](https://git-scm.com/) installed on your machine.
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.

## Steps

1. **Clone the repository:**

    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Start the application using Docker Compose:**

    ```sh
    docker compose up
    ```

    This command will build and start the fastapi uvicorn server as defined in the `docker-compose.yml` file.

3. **Access the application:**

    - Once the containers are running, you can access the frontend at [http://localhost:5173](http://localhost:5173) and the backend API at [http://localhost:8000](http://localhost:8000).

## Stopping the Application

To stop the running containers, press `Ctrl+C` in the terminal where Docker Compose is running


## ⚙️ Technologies

- **[FastAPI](https://fastapi.tiangolo.com/)** — high-performance async Python web framework.  
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM for database models and queries.  
- **[Uvicorn](https://www.uvicorn.org/)** — ASGI server with WebSocket support.  
- **[OpenAI API](https://platform.openai.com/)** — AI responses and function calls.  
- **Docker & Docker Compose** — containerization and orchestration.  

---

## 📡 Architecture Overview

### REST Endpoints

- `POST /chats` → Create a new chat.  
- `POST /chats/{chat_id}/messages` → Add a new message (user/admin/AI).  
- `GET /chats/{chat_id}` → Retrieve a single chat by its ID.  
- `GET /chats` → Retrieve all chats (for admin panel).  
- `POST /chats/{chat_id}/escalate` → Escalate the status of a chat to a human.  

For more information, you can view the docs at 127.0.0.1:8000/docs

### WebSockets

- `ws://localhost:8000/ws/{chat_id}`  
  - Each chat has its own WebSocket room.  
  - **ConnectionManager** maintains active connections per `chat_id`.  
  - All events are broadcast in a structured format:  

  ```json
  {
    "event": "NEW_MESSAGE",
    "body": {
      "id": 42,
      "sender": "user",
      "content": "Hi, I’d like info about scholarships",
      "timestamp": "2025-09-25T12:34:56.000Z"
    }
  }
  ```

### AI Use

- Used mainly to scaffold the project and endpoints
- Also used to generate the prompt for the open ai integration

### Time Taken

- About 4 hours overall

