# INFORMME

A full-stack **Django + React** application with:
- JWT authentication (register/login/reset password)
- Role-based admin area (upload PDF / ingest URL context)
- RAG-powered chatbot with per-user chat history
- Streaming AI responses (ChatGPT-like progressive output)
- Admin context cache refresh

---

## Tech Stack

- **Backend:** Django, Django REST Framework, SimpleJWT, LangChain, ChromaDB
- **Frontend:** React + Vite
- **Vector Store:** Chroma (local persistent storage)
- **Database:** SQLite (default)

---

## Project Structure

- `backend/` — Django API
- `frontend/` — React app
- `docker-compose.yml` — one-command local container orchestration

---

## Prerequisites

For local run (without Docker):
- Python 3.11+ (3.12 recommended)
- Node.js 20+
- npm 10+

For Docker run:
- Docker Desktop (or Docker Engine + Compose plugin)

---

## 1) Clone the Project

```bash
git clone <your-repo-url>
cd INFORMME
```

---

## 2) Environment Variables

Create `backend/.env` (or copy from `backend/.env.example`) and set values:

```env
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001
SMTP_PASSWORD=your_smtp_app_password
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_web_client_id
```

Create `frontend/.env` (or copy from `frontend/.env.example`) and set:

```env
VITE_GOOGLE_CLIENT_ID=your_google_oauth_web_client_id
```

> `GOOGLE_API_KEY` is required for embedding + chat generation.
> `GOOGLE_OAUTH_CLIENT_ID` and `VITE_GOOGLE_CLIENT_ID` must be the same Google OAuth **Web application** client ID.
> In Google Cloud Console, add authorized JavaScript origins for `http://localhost:5173` and `http://127.0.0.1:5173`.

---
## Run Option A: Docker (Single Command)

From project root:

```bash
docker compose up --build
```

Then open:
- Frontend: **http://localhost:5173**
- Backend: **http://localhost:8000**

Note for Google login in Docker:
- Ensure `frontend/.env` exists before `docker compose up --build`.
- `docker-compose.yml` now loads `./frontend/.env` into the frontend service.

To stop:

```bash
docker compose down
```

To also remove volumes:

```bash
docker compose down -v
```
---

## Run Option B: Local Development (No Docker)

### Backend (Terminal 1)

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend runs at: **http://127.0.0.1:8000**

### Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---


---

## Useful Commands

### Create Django superuser

```bash
cd backend
python manage.py createsuperuser
```

### Run backend migrations after model changes

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

---

## Common Issues

### 1) `docker: command not found`
Install Docker Desktop and restart your terminal.

### 2) Frontend port already in use (`5173`)
Stop the other process using the port or run Vite on another port.

### 3) Chatbot not answering from context
- Ensure files/URLs are uploaded from Admin page
- Ensure `GOOGLE_API_KEY` is valid
- If needed, use **Refresh Cache** and re-upload context

### 4) CORS errors
Make sure frontend runs on `http://localhost:5173` (or update backend CORS settings accordingly).

---

## API Base URLs (used by frontend)

- Auth: `http://127.0.0.1:8000/api/auth`
- Chatbot: `http://127.0.0.1:8000/api/chatbot`
- Knowledge Base: `http://127.0.0.1:8000/api/knowledge-base`

---

## License

No license file is currently included.
