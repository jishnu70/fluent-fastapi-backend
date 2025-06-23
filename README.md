# 🔧 Fluent Backend – FastAPI Server for Secure Chat

This is the **backend server** for the [Fluent Secure Chat App](https://github.com/jishnu70/Fluent-Secure-E2E-Chat-App-Kotlin-Compose), built using **FastAPI**. It powers **real-time, end-to-end encrypted messaging** over **WebSockets**, handles **JWT-based authentication**, and manages user/message data with a clean, scalable architecture.

---

## 🚀 Features

- 🔐 **End-to-End Encryption Support** (RSA Key Exchange using Android Keystore)
- 🔑 **JWT Authentication** (Access + Refresh Tokens)
- 🔁 **Token Refresh Mechanism**
- 🧑‍🤝‍🧑 **User Registration, Login, and Search**
- 📩 **Message Storage and Retrieval**
- 🌐 **Real-Time Messaging** via WebSockets
- 📦 **Modular FastAPI Router Setup**
- 🔐 **CORS and Secure Headers Configured**
- 📁 **SQLite / PostgreSQL support**

---

## 📁 Project Structure

```
.
├── main.py                   # FastAPI application entry point
├── database.py               # Database setup and connection
├── requirements.txt          # Python dependencies

├── alembic/                  # DB migrations folder
│   ├── env.py
│   ├── script.py.mako
│   ├── versions/
│   └── README

├── core/                     # Core logic (encryption, chat hub, auth utils)
│   ├── authentication.py
│   ├── chatHub.py
│   ├── encryption.py
│   └── __init__.py

├── crud/                     # Database interaction layer
│   ├── MessageCrud.py
│   └── __init__.py

├── models/                   # SQLAlchemy ORM models
│   ├── Attachment.py
│   ├── Message.py
│   ├── User.py
│   └── __init__.py

├── schemas/                  # Pydantic request/response models
│   ├── AttachmentSchema.py
│   ├── MessageSchema.py
│   ├── TokenSchema.py
│   ├── UserSchema.py
│   ├── PartnerSchema.py
│   └── __init__.py

├── routes/                   # FastAPI route handlers
│   ├── authRoutes.py
│   ├── messageRoutes.py
│   └── __init__.py

├── websocket/                # (Currently empty, reserved for WebSocket logic)
└── venv/                     # Python virtual environment (excluded from version control)

```

---

## 🔐 Authentication Flow

1. 🔐 **Register/Login** → Get **Access + Refresh Tokens**
2. 🔄 Use Access Token for protected endpoints
3. ♻️ Use `/refresh` to get new tokens when expired
4. 💬 Authenticate WebSocket with token: `/chat/ws?token=...`

---

## 📡 WebSocket Messaging

- Clients connect using token auth (`?token=...`)
- Messages are encrypted on the client before sending
- Server **stores encrypted message** (no decryption happens server-side)
- Messages are relayed in real-time to the receiver if online

---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/jishnu70/fluent-fastapi-backend.git
cd fluent-fastapi-backend
```

### 2. Create Virtual Environment & Install

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Server

```bash
uvicorn main:app --reload
```

Server will run at `http://127.0.0.1:8000`

---

## 📬 Endpoints Overview

| Method | Endpoint                 | Description                    |
|--------|--------------------------|--------------------------------|
| POST   | `/auth/register`         | Register new user              |
| POST   | `/auth/login`            | Login and get JWT tokens       |
| POST   | `/auth/refresh`          | Refresh expired tokens         |
| GET    | `/users/search?query=`   | Search for users               |
| GET    | `/chat/all_messages`     | Get all messages with partner  |
| WS     | `/chat/ws?token=`        | WebSocket for real-time chat   |

---

## 🔐 Tech Stack

- **FastAPI** (Python)
- **SQLAlchemy** (ORM)
- **JWT** (Authentication)
- **SQLite/PostgreSQL** (Database)
- **WebSockets** (Real-time messaging)

---

## 📦 Future Improvements

- ⛔ Expire old messages (auto-delete after X days)
- 🖼️ Media support (images, audio)
- 📲 Push notification integration (FCM)
- 📁 Switch to PostgreSQL for production
- 🛡️ Rate-limiting and IP-based blocking

---

## 🧪 Testing with WebSocket

Use Postman or [websocat](https://github.com/vi/websocat):

```bash
websocat "ws://localhost:8000/chat/ws?token=YOUR_ACCESS_TOKEN"
```

---
