# Podd Health Assistant Backend

FastAPI backend for the Podd health assistant, powered by LangGraph and LocusGraph.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # or `.venv\Scripts\activate` on Windows

pip install -e .
# or: pip install -r requirements.txt

cp .env.example .env
# Edit .env with JWT_SECRET, LOCUSGRAPH_API_KEY, etc.
```

SQLite database (`podd_auth.db`) and tables are created automatically on startup.

## Run

```bash
uvicorn src.main:app --reload
```

## API Docs

Once running, visit `http://localhost:8000/docs` for the interactive API documentation.

## Auth Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create user, returns tokens |
| POST | `/api/auth/login` | Validate credentials, returns access + refresh tokens |
| POST | `/api/auth/logout` | Invalidate refresh token (send `{"refresh_token": "..."}`) |
| POST | `/api/auth/refresh` | Issue new tokens from refresh token (send `{"refresh_token": "..."}`) |
| GET | `/api/auth/me` | Return current user (requires `Authorization: Bearer <access_token>`) |

All non-auth routes require `Authorization: Bearer <access_token>`.

### Test Auth with curl

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123","name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'

# Get current user (use access_token from response)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"

# Refresh tokens
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'

# Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'

```
locusgraph-client
pip install git+https://github.com/locusgraph/bindings.git@v0.1.1#subdirectory=python
