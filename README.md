# 🚀 FastAPI Production Backend

A production-style backend built with FastAPI, featuring JWT authentication, multi-tenant architecture, async PostgreSQL, and Dockerized deployment.

---

## 🧱 Tech Stack

* FastAPI
* PostgreSQL
* SQLAlchemy (Async)
* Alembic
* Docker

---

## ✨ Features

* JWT Authentication (OAuth2 Password Flow)
* Multi-tenant architecture (Company → Users)
* Clean layered architecture (Router → Service → Repository)
* Async database support
* Dockerized setup
* Alembic migrations

---

## 📂 Project Structure

```
app/
├── api/v1/endpoints/
├── core/
├── db/
├── repositories/
├── schemas/
├── services/
└── main.py
```

---

## ⚙️ Setup & Run

### 1. Clone the repository

```
git clone <your-repo-url>
cd fastapi-production-backend
```

### 2. Start services

```
docker compose up --build
```

### 3. Access API docs

```
http://localhost:8000/docs
```

---

## 🔐 Authentication Flow

1. Register a user
2. Login to receive JWT token
3. Use token in requests:

```
Authorization: Bearer <your_token>
```

---

## 🗄️ Database

* PostgreSQL (Dockerized)
* Managed via Alembic migrations
* Persistent storage using Docker volumes

---

## 🧪 Testing

(Coming soon)

---

## 📌 Current Status

* Core backend complete
* Auth flow working
* Multi-tenant logic implemented
* Docker setup stable

---

## 🚧 Future Improvements

* Automated tests (pytest)
* CI/CD pipeline
* Improved security (company join flow)
* Exception handling improvements

---
