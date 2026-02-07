# OmniRouter

**OmniRouter** is a memory-enabled conversational backend built using **FastAPI**.  
It provides structured session management, persistent short-term and long-term memory, relational storage with SQLite, and robust logging for reliable AI-powered chat systems.

This project demonstrates AI system architecture beyond just model usage — focusing on backend design, data modeling, and conversational state persistence.

---

## 🚀 Features

- **Short-Term Memory** for contextual responses within active sessions  
- **Long-Term Memory** stored persistently across sessions  
- **FastAPI REST Endpoints** for user, session, and chat management  
- **SQLite Database (5 Tables)** for structured data storage  
- **Error & Success Logging** for monitoring and debugging  
- Modular and extensible architecture  

---

## 🏗️ Architecture Overview

OmniRouter separates concerns into:

- API Layer (FastAPI routes)
- Memory Management Layer
- Database Layer (SQLite schema)
- Logging System
- Chat Processing Logic

This allows scalable extension for:

- LLM integrations  
- Multi-user systems  
- Production deployment  
- Analytics pipelines  

---

## 🧠 Memory Design

### Short-Term Memory

- Maintains conversational context within active sessions  
- Enables coherent multi-turn interactions  

### Long-Term Memory

- Persisted in SQLite  
- Enables contextual recall across sessions  
- Structured for retrieval and future expansion  

---

## 🗄️ Database Schema

OmniRouter uses SQLite with 5 relational tables:

| Table              | Purpose                          |
|--------------------|----------------------------------|
| `users`            | Stores user information          |
| `sessions`         | Tracks session lifecycle         |
| `chats`            | Stores individual conversations  |
| `messages`         | Stores message-level data        |
| `long_term_memory` | Persistent memory storage        |

This design ensures normalized storage and structured retrieval.

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/CaptianErek/OmniRouter.git
cd OmniRouter
```
---
## ▶️ Running the Application
Start the FastAPI server:
```bash
uvicorn api:app --reload
```
---
## 📊 Logging
The system logs:

1. API requests

2. Success events

3. Failures and exceptions

### Logging ensures reliability and easier debugging during development and deployment.
