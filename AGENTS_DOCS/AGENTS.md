# AGENTS.md

Guide for AI agents working on the Podd Health Assistant codebase.

## Overview

Podd Health Assistant is a comprehensive health monitoring system with a **dual-database architecture**:

1. **SQLite (`podd_auth.db`)**: Stores ONLY authentication data (Users, RefreshTokens)
2. **LocusGraph SDK**: Stores ALL health and personal data (Profiles, Vitals, Medications, Schedules, Activities, Reminders, Chat)

**Tech Stack**: FastAPI, Python 3.12, SQLAlchemy, LangGraph, LocusGraph SDK, Sarvam AI (voice), OpenAI (LLM)

## Essential Commands

### Development

```bash
# Navigate to backend directory
cd backend

# Setup virtual environment (Python 3.11+ required, 3.12 recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run development server (auto-reload)
uvicorn src.main:app --reload

# Run with specific port
uvicorn src.main:app --reload --port 8000

# Access API docs
# http://localhost:8000/docs
```

### Testing

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/auth/
pytest tests/health/
pytest tests/medication/

# Run specific test file
pytest tests/auth/test_auth.py

# Run with verbose output
pytest -v

# Run with markers
pytest -m asyncio

# Run standalone verification scripts (not pytest)
python -m tests.verification.test_imports
python -m tests.verification.verify_imports
python -m tests.verification.verify_phase2
python -m tests.verification.verify_backend_status
```

### Code Quality

```bash
# Format code (if black/isort are used)
black src/
isort src/

# Lint code (if flake8/ruff are used)
flake8 src/
ruff check src/
```

### Database Operations

```bash
# SQLite auth database
sqlite3 podd_auth.db ".tables"
sqlite3 podd_auth.db ".schema"
sqlite3 podd_auth.db "SELECT * FROM users LIMIT 5;"
```

## Project Structure

```
backend/
├── src/                          # Main application code
│   ├── main.py                    # FastAPI app entry point
│   ├── config/
│   │   └── settings.py            # Pydantic Settings for configuration
│   ├── database.py                # SQLite database setup (auth only)
│   ├── auth/                     # Authentication module
│   │   ├── jwt.py                # JWT token creation/verification
│   │   └── dependencies.py        # FastAPI auth dependencies
│   ├── routes/                   # API endpoints (by domain)
│   │   ├── auth/                 # Authentication endpoints
│   │   ├── health/               # Vitals, food logs, insights
│   │   ├── medication/           # Medications and schedules
│   │   ├── profile/              # User profiles
│   │   ├── voice/                # Voice interface
│   │   ├── chat/                # AI chat
│   │   ├── meditation/          # Meditation tracking
│   │   ├── appointments/         # Appointment management
│   │   ├── emergency/           # Emergency contacts
│   │   └── alarms/              # Alarms and notifications
│   ├── models/                   # SQLAlchemy models (auth only)
│   │   ├── user.py
│   │   └── refresh_token.py
│   ├── schemas/                  # Pydantic schemas
│   │   ├── events/              # LocusGraph event kinds & context IDs
│   │   ├── auth/                # Auth request/response schemas
│   │   ├── health/              # Health data schemas
│   │   ├── medication/           # Medication schemas
│   │   ├── profile/             # Profile schemas
│   │   └── ...
│   ├── services/                 # Business logic
│   │   ├── locusgraph/          # LocusGraph SDK wrapper
│   │   │   └── service.py      # Core locusgraph_service
│   │   ├── temporal/            # Time-based queries & scheduling
│   │   ├── validation/          # Duplicate detection & validation memory
│   │   ├── batch/              # Bulk operations
│   │   ├── migration/           # Schema migration tracking
│   │   └── sarvam_service.py   # Voice AI service
│   ├── workflows/                # LangGraph workflows
│   │   ├── health_workflow.py    # Main health workflow
│   │   ├── state.py             # Workflow state definition
│   │   └── nodes/              # Workflow nodes
│   │       ├── agents/          # AI agents
│   │       ├── context.py        # Context retrieval
│   │       ├── memory.py        # Memory management
│   │       ├── normalize.py     # Input normalization
│   │       ├── response.py      # Response formatting
│   │       └── router.py       # Intent routing
│   └── alarms/                  # Alarm scheduling module
│       └── scheduler.py
├── tests/                       # Test suite
│   ├── conftest.py              # Shared fixtures
│   ├── auth/
│   ├── health/
│   ├── medication/
│   ├── profile/
│   └── verification/            # Standalone verification scripts
├── 0bruno/                     # Bruno API collection (API testing)
│   ├── Auth/
│   ├── Health/
│   ├── Medication/
│   └── environments/
│       └── local.bru
├── .env.example                 # Environment variables template
├── pyproject.toml              # Project configuration
├── requirements.txt             # Python dependencies
└── README.md
```

## Code Patterns & Conventions

### Route Handler Pattern

All routes follow FastAPI conventions with async/await:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/vitals", tags=["vitals"])

@router.get("", response_model=list[VitalsResponse])
async def get_vitals(
    limit: int = Query(10, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    """Retrieve all vitals for current user."""
    # 1. Query LocusGraph
    memories = await locusgraph_service.retrieve_context(query=...)

    # 2. Transform to response models
    vitals_entries = [VitalsResponse(**memory["payload"]) for memory in memories]

    # 3. Return
    return vitals_entries

@router.post("", response_model=VitalsResponse, status_code=status.HTTP_201_CREATED)
async def create_vitals(
    data: VitalsCreate,
    current_user=Depends(get_current_user),
):
    """Create new vitals entry."""
    # 1. Generate ID
    vitals_id = locusgraph_service.new_id()
    context_id = VitalsEventDefinition.get_context_id(vitals_id)

    # 2. Build payload
    payload = VitalsEventDefinition.create_payload(
        **data.model_dump(),
        user_id=str(current_user.id),
    )

    # 3. Store in LocusGraph
    await locusgraph_service.store_event(
        event_kind=EventKind.VITALS_CREATE,
        context_id=context_id,
        payload=payload,
    )

    # 4. Return response
    return VitalsResponse(id=vitals_id, **data.model_dump())
```

### Schema Pattern

Each domain has base/create/update/response Pydantic schemas:

```python
from pydantic import BaseModel, Field

class VitalsBase(BaseModel):
    """Base schema with common fields."""
    blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=250)
    heart_rate: Optional[int] = Field(None, ge=30, le=220)

class VitalsCreate(VitalsBase):
    """Schema for creating entries."""
    pass

class VitalsUpdate(VitalsBase):
    """Schema for updating entries (all fields optional)."""
    pass

class VitalsResponse(VitalsBase):
    """Schema for API responses."""
    id: str
    user_id: str
    logged_at: datetime
    created_at: datetime
```

### LocusGraph Service Pattern

All health data operations use `locusgraph_service`:

```python
from src.services.locusgraph.service import locusgraph_service

# Store event
await locusgraph_service.store_event(
    event_kind="fact",  # or use EventKind constant
    context_id="vitals:abc123",
    payload={"heart_rate": 75, "blood_pressure_systolic": 120},
    related_to=["med_schedule:def456"],  # Optional: link to other events
)

# Retrieve context
memories = await locusgraph_service.retrieve_context(
    query="vitals user-123",  # Natural language query
    context_ids=["vitals:abc123"],  # Optional: specific IDs
    context_types={"vitals": "vitals"},  # Optional: filter by type
    limit=10,
)

# Generate insights
insights = await locusgraph_service.generate_insights(
    task="Analyze heart health trends",
    locus_query="vitals heart rate user-123",
    limit=5,
)

# Generate short ID
id = locusgraph_service.new_id()  # Returns 12-char hex

# Get current timestamp
timestamp = locusgraph_service.now()  # Returns ISO format UTC
```

### Authentication Pattern

Protected routes use `get_current_user` dependency:

```python
from src.auth.dependencies import get_current_user
from src.models.user import User

@router.post("/endpoint")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    # current_user is authenticated User object
    return {"user_id": str(current_user.id), "email": current_user.email}
```

## LocusGraph Integration

### Critical Gotcha: Overwrite Behavior

**Important**: If you call `store_event` with a `context_id` that already exists, LocusGraph **overwrites the entire payload** of the existing event. This is intentional for static data like profiles.

Use this for:
- User profiles (one per user)
- Cache entries
- Any entity where you want single up-to-date record

Don't use for:
- Logs, entries, records (use unique IDs)
- Historical data

### Context ID Patterns

All LocusGraph events use `context_id` format: `<entity_type>:<id>`

| Entity Type | Context ID Format | Example |
|-------------|-------------------|---------|
| Profile | `profile:<user_id>` | `profile:user-123` |
| Vitals | `vitals:<id>` | `vitals:abc123` |
| Food Log | `food:<id>` | `food:def456` |
| Medication | `medication:<id>` | `medication:ghi789` |
| Medication Schedule | `med_schedule:<id>` | `med_schedule:jkl012` |
| Medication Log | `med_log:<id>` | `med_log:mno345` |
| Water Log | `water:<id>` | `water:pqr678` |
| Sleep Log | `sleep:<id>` | `sleep:stu901` |
| Exercise Log | `exercise:<id>` | `exercise:vwx234` |
| Mood Log | `mood:<id>` | `mood:yzw567` |
| Meditation Session | `meditation_session:<id>` | `meditation_session:abc123` |
| Meditation Log | `meditation_log:<id>` | `meditation_log:def456` |
| Appointment | `appointment:<id>` | `appointment:ghi789` |
| Emergency Contact | `emergency_contact:<id>` | `emergency_contact:jkl012` |
| Alarm | `alarm:<id>` | `alarm:mno345` |
| Notification | `notification:<id>` | `notification:pqr678` |
| Chat Message | `chat:<id>` | `chat:stu901` |

**Event Kind Constants** (defined in `src/schemas/events/locusgraph_events.py`):

```python
# Profile
PROFILE_CREATE = "profile.create"
PROFILE_UPDATE = "profile.update"
PROFILE_DELETE = "profile.delete"

# Vitals
VITALS_CREATE = "vitals.create"
VITALS_UPDATE = "vitals.update"
VITALS_DELETE = "vitals.delete"

# Food
FOOD_LOG_CREATE = "food_log.create"
FOOD_LOG_UPDATE = "food_log.update"
FOOD_LOG_DELETE = "food_log.delete"

# ... etc for all domains
```

**Always use constants** from `EventKind` class, not string literals.

### Event Schemas

Each domain has event schema classes with helper methods:

```python
from src.schemas.health.vitals import VitalsEventDefinition

# Get context_id
context_id = VitalsEventDefinition.get_context_id("abc123")
# Returns: "vitals:abc123"

# Create payload with validation
payload = VitalsEventDefinition.create_payload(
    blood_pressure_systolic=120,
    blood_pressure_diastolic=80,
    heart_rate=72,
    logged_at=datetime.now(timezone.utc),
    user_id="user-123",
)
```

## Important Gotchas

### Bcrypt Password Limit

Bcrypt has a **72-byte limit**. Passwords longer than this are truncated:

```python
# Pattern used in auth routes
BCRYPT_MAX_PASSWORD_BYTES = 72

def _password_bytes(password: str) -> bytes:
    """Encode password for bcrypt, truncating to 72 bytes if needed."""
    encoded = password.encode("utf-8")
    return encoded[:BCRYPT_MAX_PASSWORD_BYTES] if len(encoded) > BCRYPT_MAX_PASSWORD_BYTES else encoded

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")
```

**Never store raw passwords**. Always hash with bcrypt.

### LocusGraph Mock Mode

In development, set `USE_LOCUSGRAPH_MOCK=true` in `.env` to use in-memory mock instead of real LocusGraph SDK:

```python
# In src/services/locusgraph/service.py
class LocusGraphService:
    def __init__(self):
        self.use_mock = settings.USE_LOCUSGRAPH_MOCK

        if self.use_mock:
            print("🧪 Using MOCK LocusGraph service")
            self._mock_events = []  # In-memory storage
            return
        # ... initialize real client
```

Mock mode stores events in `self._mock_events` list for testing.

### Database Separation

**SQLite** (`podd_auth.db`):
- Stores: Users, RefreshTokens ONLY
- No health data
- Created automatically on startup
- Use SQLAlchemy for queries

**LocusGraph SDK**:
- Stores: ALL health data
- Events with structured payloads
- Use `locusgraph_service` for operations

**Never** mix the two. Auth data goes in SQLite, health data goes in LocusGraph.

### Import Conventions

Use `src` prefix for internal imports:

```python
from src.config import settings
from src.database import get_db
from src.models import User
from src.schemas.auth import LoginRequest
from src.services.locusgraph.service import locusgraph_service
```

This assumes running from backend directory or proper PYTHONPATH setup.

### Async/Await

All database operations and API calls must be async:

```python
# Good
async def get_vitals(user_id: str):
    memories = await locusgraph_service.retrieve_context(...)
    return memories

# Bad - will block event loop
def get_vitals(user_id: str):
    memories = locusgraph_service.retrieve_context(...)  # Missing await
    return memories
```

### Test Mocking

LocusGraph service is mocked in tests to avoid external dependencies:

```python
from tests.conftest import mock_locusgraph_service

@pytest_asyncio.fixture
async def client(mock_locusgraph_service, app):
    # mock_locusgraph_service patches locusgraph_service in all routes
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        yield ac
```

Tests use `mock_locusgraph_service` fixture which patches the service in routes.

## Environment Variables

Create `.env` from `.env.example`:

```bash
# Authentication
JWT_SECRET=generate-with-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
JWT_REFRESH_EXPIRATION_DAYS=7

# LocusGraph
LOCUSGRAPH_SERVER_URL=https://api-dev.locusgraph.com
LOCUSGRAPH_AGENT_SECRET=your-agent-secret
LOCUSGRAPH_GRAPH_ID=your-graph-id
USE_LOCUSGRAPH_MOCK=true  # Set to false for production

# OpenAI (for LLM features)
OPENAI_API_KEY=sk-...

# Sarvam AI (for voice features)
SARVAM_API_KEY=...

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

**Security**: Never commit `.env` to git. Add to `.gitignore`.

## Workflow System (LangGraph)

Workflows manage complex multi-step operations with AI agents:

```python
from src.workflows.health_workflow import run_workflow

# Execute workflow
result = await run_workflow(
    user_id="user-123",
    user_text="I'm feeling tired today",
    locale="en-IN",
    channel="text",
)
```

### Workflow State

```python
class PoddState(TypedDict):
    user_id: str
    user_text: str
    locale: str
    channel: Literal["text", "voice"]
    pending_events: list  # Events to store in LocusGraph
    errors: list
    flags: dict
```

### Workflow Nodes

Each node is a function that receives and returns state:

```python
async def normalize_input(state: PoddState) -> PoddState:
    """Normalize user input."""
    # Process state["user_text"]
    # Update state
    return state

async def retrieve_locus_context(state: PoddState) -> PoddState:
    """Retrieve user's health context from LocusGraph."""
    memories = await locusgraph_service.retrieve_context(...)
    # Store in state
    return state
```

## Testing Patterns

### Test Structure

```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_create_vitals(client: AsyncClient, test_user):
    """Test creating vitals entry."""
    # 1. Login to get token
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = response.json()["access_token"]

    # 2. Create vitals
    response = await client.post(
        "/api/vitals",
        json={"heart_rate": 75, "blood_pressure_systolic": 120},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 3. Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["heart_rate"] == 75
```

### Fixtures

```python
# app - FastAPI application
# client - AsyncClient with mocked services
# clean_db - Clears auth DB before/after each test
# mock_locusgraph_service - Mock LocusGraph service
# db_session - Async DB session
# test_user - Pre-created user: test@example.com / testpass123
```

## Naming Conventions

### Files and Directories

- **Routes**: `routes/<domain>/<entity>.py` (e.g., `routes/health/vitals.py`)
- **Schemas**: `schemas/<domain>/<entity>.py` (e.g., `schemas/health/vitals.py`)
- **Models**: `models/<entity>.py` (e.g., `models/user.py`)
- **Services**: `services/<module>/<name>.py` (e.g., `services/locusgraph/service.py`)

### Python Code

- **Classes**: PascalCase (e.g., `VitalsCreate`, `LocusGraphService`)
- **Functions**: snake_case (e.g., `get_vitals`, `create_payload`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `EventKind.VITALS_CREATE`, `BCRYPT_MAX_PASSWORD_BYTES`)
- **Private functions**: underscore prefix (e.g., `_hash_password`, `_token_hash`)

### Context IDs

Follow format `<entity_type>:<id>`:
- `vitals:abc123`
- `med_schedule:def456`
- `profile:user-123`

Use constants from `ContextIdPattern` class.

## API Testing with Bruno

Bruno collection in `backend/0bruno/` for API testing:

```bash
# Bruno CLI (if installed)
bru run 0bruno/Auth/Login.bru --env local

# Or use Bruno GUI
# Open 0bruno/ folder in Bruno app
# Select environment (local.bru)
# Run requests
```

Bruno environments in `0bruno/environments/local.bru`.

## Verification Scripts

Standalone scripts for project health checks:

```bash
# Check all imports load
python -m tests.verification.test_imports

# Check route import paths
python -m tests.verification.verify_imports

# Phase 2 completion checks
python -m tests.verification.verify_phase2

# Backend endpoint status vs TODO
python -m tests.verification.verify_backend_status
```

These are NOT pytest tests - run directly with Python.

## Common Tasks

### Adding New Health Entity

1. **Create schema** in `src/schemas/<domain>/`:
   - Base schema
   - Create/Update/Response schemas
   - Event definition class with `get_context_id()` and `create_payload()`

2. **Add EventKind** constants in `src/schemas/events/locusgraph_events.py`

3. **Create routes** in `src/routes/<domain>/`:
   - GET list (with filters)
   - GET single
   - POST create
   - PUT update
   - DELETE delete

4. **Register router** in `src/main.py`

5. **Add tests** in `tests/<domain>/`

### Adding New API Endpoint

1. Define request/response schemas in appropriate `schemas/` module
2. Add route handler in `routes/<module>/`
3. Import and register router in `main.py`
4. Add tests in `tests/<module>/`

### Modifying Workflow

1. Add node function in `workflows/nodes/`
2. Add node to graph in `workflows/health_workflow.py`
3. Add edges for flow control
4. Test with `run_workflow()`

## Key Files to Understand

- `backend/src/main.py` - Application entry point, router registration
- `backend/src/config/settings.py` - All configuration
- `backend/src/services/locusgraph/service.py` - LocusGraph integration
- `backend/src/auth/jwt.py` - JWT token handling
- `backend/tests/conftest.py` - Test fixtures
- `backend/docs/backned/architecture.md` - Detailed architecture
- `backend/docs/backned/workflows.md` - Workflow documentation
- `backend/docs/backned/quick_reference.md` - Quick reference guide

## Common Issues

### Import Errors

If you get "Module not found: src", ensure:
1. You're in `backend/` directory
2. Virtual environment is activated
3. PYTHONPATH includes project root

### Database Locked

SQLite can lock in tests. Ensure tests use `clean_db` fixture properly.

### LocusGraph Connection Failed

Check:
1. `USE_LOCUSGRAPH_MOCK` is set correctly in `.env`
2. `LOCUSGRAPH_AGENT_SECRET` is valid
3. Network connectivity to LocusGraph server

### JWT Token Expired

Access tokens expire based on `JWT_EXPIRATION_MINUTES`. Use refresh token to get new access token via `/api/auth/refresh`.

## Python Version

**Required**: Python 3.11+ (3.12 recommended)

**Avoid**: Python 3.13 (compatibility issues with some dependencies)

## Documentation

- [Architecture](backend/docs/backned/architecture.md) - Detailed system architecture
- [Workflows](backend/docs/backned/workflows.md) - LangGraph workflow documentation
- [Quick Reference](backend/docs/backned/quick_reference.md) - Quick reference for common tasks
- [API Documentation](backend/docs/backned/api_documentation.md) - API endpoint docs
- [Database Schema](backend/docs/backned/database_schema.md) - Schema documentation
- [LocusGraph Events](backend/docs/backned/locusgraph_events_reference.md) - Event reference

## External Dependencies

- **LocusGraph SDK**: `git+https://github.com/locusgraph/bindings.git@v0.1.1#subdirectory=python`
- **OpenAI**: For LLM features
- **Sarvam AI**: For Indian-language voice processing (STT/TTS)

## License

Check root repository for license information.
