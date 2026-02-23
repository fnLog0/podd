# Quick Reference Guide

## Overview

The Podd Health Assistant uses a **dual-database architecture**:
- **SQLite (`podd_auth.db`)**: Stores ONLY authentication data (Users, RefreshTokens)
- **LocusGraph SDK**: Stores ALL health and personal data (Profiles, Vitals, Medications, etc.)

## Getting Started

### Local Development Setup

```bash
# 1. Clone and navigate
git clone <repo>
cd podd/backend

# 2. Create virtual environment
python -m venv podd_env
source podd_env/bin/activate  # Linux/Mac
# or
podd_env\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run application
python src/main.py
# or
uvicorn src.main:app --reload --port 8000
```

### Accessing the Application

- **API Root**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Commands

### Running the Application

```bash
# Development mode (auto-reload)
uvicorn src.main:app --reload --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# With logging
uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_health.py

# Run specific test function
pytest tests/test_health.py::test_health_metrics

# Run with verbose output
pytest -v

# Run with dry-run
pytest --dry-run
```

### Database Operations

#### SQLite Authentication Database

```bash
# Check database connection
sqlite3 podd_auth.db ".tables"

# View database schema
sqlite3 podd_auth.db ".schema"

# Query database
sqlite3 podd_auth.db "SELECT * FROM users LIMIT 5;"

# Backup database
sqlite3 podd_auth.db ".backup 'backup_$(date +%Y%m%d).db'"

# Vacuum database
sqlite3 podd_auth.db "VACUUM;"

# Check database integrity
sqlite3 podd_auth.db "PRAGMA integrity_check;"
```

#### LocusGraph SDK

```bash
# Check LocusGraph service health
curl http://localhost:8001/health

# Test LocusGraph API connectivity
curl -X GET "http://localhost:8001/health" \
  -H "X-API-Key: $LOCUSGRAPH_API_KEY"

# Export LocusGraph graph data (if supported)
curl -X POST "http://localhost:8001/export" \
  -H "X-API-Key: $LOCUSGRAPH_API_KEY" \
  -o "locusgraph_backup.json"
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite auth database URL | `sqlite+aiosqlite:///./podd_auth.db` |
| `LOCUSGRAPH_API_URL` | LocusGraph SDK service URL | `http://localhost:8001` |
| `LOCUSGRAPH_API_KEY` | LocusGraph API key | `your-locusgraph-key` |
| `LOCUSGRAPH_GRAPH_ID` | Graph ID | `podd_health` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `JWT_SECRET` | JWT secret key | `generate with openssl rand -hex 32` |
| `CORS_ORIGINS` | Allowed origins | `["http://localhost:8000"]` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SARVAM_API_KEY` | Sarvam API key | `""` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Token expiration | `60` |
| `JWT_REFRESH_EXPIRATION_DAYS` | Refresh token expiration | `7` |
| `REDIS_URL` | Redis cache URL | `""` |
| `CACHE_TTL` | Cache TTL in seconds | `3600` |

### Generate Secure JWT Secret

```bash
openssl rand -hex 32
```

## LocusGraph SDK Usage

### Storing Health Events

```python
# Store vitals
await locusgraph_service.store_event(
    event_kind="fact",
    context_id="vitals:12345",
    payload={
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "heart_rate": 72,
        "logged_at": "2026-02-18T08:00:00Z"
    }
)

# Store food log
await locusgraph_service.store_event(
    event_kind="fact",
    context_id="food:67890",
    payload={
        "description": "Rice and dal",
        "calories": 400,
        "meal_type": "lunch",
        "logged_at": "2026-02-18T12:30:00Z"
    }
)

# Store medication log
await locusgraph_service.store_event(
    event_kind="fact",
    context_id="medication:99999",
    payload={
        "name": "Metformin",
        "dosage": "500mg",
        "frequency": "twice daily",
        "instructions": "Take after meals",
        "active": true,
        "logged_at": "2026-02-18T08:00:00Z"
    }
)
```

### Retrieving Health Data

```python
# Get user's vitals for the last 7 days
vitals = await locusgraph_service.retrieve_context(
    context_type="vitals",
    user_id="user_123",
    filters={"min_date": "2026-02-11"}
)

# Get user's food logs
food_logs = await locusgraph_service.retrieve_context(
    context_type="food",
    user_id="user_123"
)

# Get all meditation sessions
meditation_sessions = await locusgraph_service.retrieve_context(
    context_type="meditation_session",
    user_id="user_123"
)
```

### Generating Health Insights

```python
# Get health insights
insights = await locusgraph_service.generate_insights(
    user_id="user_123",
    query={"topic": "heart_health", "days": 30}
)
```

### Updating and Deleting Events

```python
# Update vitals
await locusgraph_service.update_event(
    context_id="vitals:12345",
    updates={"heart_rate": 75, "logged_at": "2026-02-18T09:00:00Z"}
)

# Delete a food log
await locusgraph_service.delete_event("food:67890")
```

### Using Modular Services

The services directory is now organized into specialized modules for better maintainability:

```python
# Import main locusgraph service (backward compatible)
from src.services import locusgraph_service

# Or import from specific modules
from src.services.locusgraph.service import LocusGraphService, locusgraph_service
from src.services.locusgraph.cache import LocusGraphCache, MeditationSessionCache
from src.services.temporal.scheduler import TemporalScheduler, get_temporal_contexts
from src.services.validation.memory import ValidationMemory, URLValidator, PhoneValidator
from src.services.validation.duplicate import DuplicateDetector, AppointmentDuplicateDetector
from src.services.batch.operations import BatchOperation, BatchAppointmentCreator
from src.services.migration.schema import SchemaMigrationManager, ensure_schema_version
```

**Service Modules:**
- `locusgraph/` - Core LocusGraph SDK integration and caching
- `temporal/` - Time-based queries and reminder scheduling
- `validation/` - Validation memory and duplicate detection
- `batch/` - Bulk operations with tracking
- `migration/` - Schema migration tracking and rollback



## API Endpoints

### Authentication

```bash
# Register
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}

# Login
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

# Refresh Token
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "..."
}

# Get Current User
GET /api/auth/me
Authorization: Bearer <token>
```

### Health Monitoring

```bash
# Get Health Metrics
GET /api/health
Authorization: Bearer <token>

# Create Vitals
POST /api/health/vitals
Authorization: Bearer <token>
Content-Type: application/json

{
  "heart_rate": 75,
  "blood_pressure": "125/82",
  "temperature": 98.7,
  "oxygen_level": 97
}

# Get Health History
GET /api/health/history?days=30
Authorization: Bearer <token>

# Get Recommendations
GET /api/health/recommendations
Authorization: Bearer <token>
```

### Medication Management

```bash
# Get Schedules
GET /api/medication/schedules
Authorization: Bearer <token>

# Create Schedule
POST /api/medication/schedules
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Metformin",
  "dosage": "500mg",
  "frequency": "twice_daily",
  "times": ["08:00", "20:00"],
  "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
  "quantity": 60
}

# Get Logs
GET /api/medication/logs?days=30
Authorization: Bearer <token>

# Create Log
POST /api/medication/logs
Authorization: Bearer <token>
Content-Type: application/json

{
  "schedule_id": "uuid",
  "dosage": "500mg",
  "notes": "With food"
}
```

### Appointments

```bash
# Get Appointments
GET /api/appointments?date_from=2026-02-18&date_to=2026-02-28
Authorization: Bearer <token>

# Create Appointment
POST /api/appointments
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Follow-up Consultation",
  "doctor_name": "Dr. Johnson",
  "specialty": "Cardiology",
  "date": "2026-02-25T14:00:00Z",
  "duration_minutes": 45
}

# Update Appointment
PUT /api/appointments/{id}
Authorization: Bearer <token>

# Cancel Appointment
DELETE /api/appointments/{id}
Authorization: Bearer <token>
```

### Emergency

```bash
# Get Emergency Contacts
GET /api/emergency/contacts
Authorization: Bearer <token>

# Create Emergency Contact
POST /api/emergency/contacts
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Jane Doe",
  "relationship": "Sibling",
  "phone": "+1987654321",
  "email": "jane@example.com",
  "is_primary": false
}

# Create Emergency Alert
POST /api/emergency/alert
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "medical",
  "severity": "high",
  "description": "Experiencing chest pain"
}
```

### Voice Interface

```bash
# Process Voice Command
POST /api/voice/command
Authorization: Bearer <token>
Content-Type: application/json

{
  "command": "I want to log my lunch",
  "context": {
    "food_type": "lunch",
    "items": ["sandwich", "apple", "juice"]
  }
}
```

### Meditation

```bash
# Get Sessions
GET /api/meditation/sessions
Authorization: Bearer <token>

# Create Session
POST /api/meditation/sessions
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Evening Relaxation",
  "duration_minutes": 20
}

# Get History
GET /api/meditation/history?days=90
Authorization: Bearer <token>
```

### Activity Tracking

```bash
# Get Food Logs
GET /api/tracking/food?date=2026-02-18
Authorization: Bearer <token>

# Create Food Log
POST /api/tracking/food
Authorization: Bearer <token>
Content-Type: application/json

{
  "food_name": "Grilled chicken salad",
  "calories": 450,
  "protein": 40,
  "carbs": 15,
  "fat": 25
}

# Get Exercise Logs
GET /api/tracking/exercise?date=2026-02-18
Authorization: Bearer <token>

# Create Exercise Log
POST /api/tracking/exercise
Authorization: Bearer <token>
Content-Type: application/json

{
  "exercise_name": "Yoga",
  "duration_minutes": 45,
  "calories_burned": 150
}

# Get Mood Logs
GET /api/tracking/mood?days=7
Authorization: Bearer <token>

# Create Mood Log
POST /api/tracking/mood
Authorization: Bearer <token>
Content-Type: application/json

{
  "mood": "neutral",
  "score": 5,
  "notes": "Average day"
}

# Get Sleep Logs
GET /api/tracking/sleep?date=2026-02-18
Authorization: Bearer <token>

# Create Sleep Log
POST /api/tracking/sleep
Authorization: Bearer <token>
Content-Type: application/json

{
  "sleep_duration_hours": 8,
  "sleep_quality": 9,
  "bedtime": "2026-02-18T23:00:00Z",
  "wake_time": "2026-02-19T07:00:00Z"
}

# Get Water Logs
GET /api/tracking/water?date=2026-02-18
Authorization: Bearer <token>

# Create Water Log
POST /api/tracking/water
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount_ml": 250
}
```

### Chat

```bash
# Send Chat Message
POST /api/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "What can you tell me about heart health?",
  "context": {
    "topic": "heart_health",
    "query_type": "information"
  }
}

# Get Chat History
GET /api/chat/history?limit=50
Authorization: Bearer <token>
```

### Profile

```bash
# Get Profile
GET /api/profile
Authorization: Bearer <token>

# Update Profile
PUT /api/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Smith",
  "age": 36,
  "height": 180,
  "weight": 75
}
```

### Alarms

```bash
# Get Alarms
GET /api/alarms
Authorization: Bearer <token>

# Create Alarm
POST /api/alarms
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Evening Walk",
  "time": "19:00",
  "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
  "enabled": true
}

# Update Alarm
PUT /api/alarms/{id}
Authorization: Bearer <token>

# Delete Alarm
DELETE /api/alarms/{id}
Authorization: Bearer <token>

# Get Notifications
GET /api/alarms/notifications
Authorization: Bearer <token>

# Mark Notification Read
POST /api/alarms/notifications/{id}/read
Authorization: Bearer <token>
```

## Project Structure

```
backend/
├── src/                           # Source code
│   ├── auth/                      # Authentication
│   │   ├── dependencies.py        # JWT dependencies
│   │   ├── jwt.py                 # JWT token handling
│   │   └── __init__.py
│   ├── routes/                    # API routes
│   │   ├── auth.py
│   │   ├── health.py
│   │   ├── medication.py
│   │   ├── appointments.py
│   │   ├── emergency.py
│   │   ├── voice.py
│   │   ├── meditation.py
│   │   ├── tracking.py
│   │   ├── chat.py
│   │   ├── profile.py
│   │   └── alarms.py
│   ├── services/                  # Business logic
│   │   ├── locusgraph/            # LocusGraph SDK integration
│   │   │   ├── service.py
│   │   │   ├── cache.py
│   │   │   └── __init__.py
│   │   ├── temporal/              # Time-based queries
│   │   │   ├── scheduler.py
│   │   │   └── __init__.py
│   │   ├── validation/            # Validation & duplicates
│   │   │   ├── memory.py
│   │   │   ├── duplicate.py
│   │   │   └── __init__.py
│   │   ├── batch/                 # Bulk operations
│   │   │   ├── operations.py
│   │   │   └── __init__.py
│   │   ├── migration/             # Schema migrations
│   │   │   ├── schema.py
│   │   │   └── __init__.py
│   │   ├── sarvam_service.py
│   │   └── __init__.py
│   ├── models/                    # Data models
│   │   ├── user.py
│   │   ├── refresh_token.py
│   │   └── __init__.py
│   ├── schemas/                   # Pydantic schemas
│   │   ├── auth.py
│   │   └── __init__.py
│   ├── workflows/                 # Workflows
│   │   ├── daily_summary.py
│   │   ├── health_workflow.py
│   │   └── nodes/
│   ├── config.py                  # Configuration
│   ├── database.py                # SQLite database setup
│   └── main.py                    # Main application
├── podd_env/                      # Virtual environment
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── requirements.txt               # Dependencies
├── pyproject.toml                 # Project config
└── README.md                      # Documentation
```

## Code Style Guidelines

### Python Code Style

- **PEP 8** - Follow Python style guide
- **Type hints** - Use type annotations
- **Docstrings** - Document all functions and classes
- **Imports** - Standard → Third party → Local

### Example

```python
# Good example
from typing import Optional
from fastapi import FastAPI, HTTPException

app = FastAPI()

async def get_user(user_id: str) -> Optional[User]:
    """Get user by ID.

    Args:
        user_id: User identifier

    Returns:
        User object or None if not found
    """
    try:
        return await db.get_user(user_id)
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    """Get user by ID."""
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Database Architecture

### SQLite Authentication Database

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Refresh Tokens Table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### LocusGraph Health Data Store

**All health data is stored as events in LocusGraph with specific `context_id` formats:**

| Entity Type | Context ID Format | Example |
|-------------|-------------------|---------|
| Profile | `profile:<user_id>` | `profile:user_123` |
| Vitals | `vitals:<id>` | `vitals:abc123` |
| Food Log | `food:<id>` | `food:def456` |
| Medication | `medication:<id>` | `medication:ghi789` |
| Medication Schedule | `med_schedule:<id>` | `med_schedule:jkl012` |
| Water Log | `water:<id>` | `water:mno345` |
| Sleep Log | `sleep:<id>` | `sleep:pqr678` |
| Exercise Log | `exercise:<id>` | `exercise:stu901` |
| Mood Log | `mood:<id>` | `mood:vwx234` |
| Meditation Session | `meditation_session:<id>` | `meditation_session:yzw567` |
| Meditation Log | `meditation_log:<id>` | `meditation_log:abc123` |
| Appointment | `appointment:<id>` | `appointment:def456` |
| Emergency Contact | `emergency_contact:<id>` | `emergency_contact:ghi789` |
| Alarm | `alarm:<id>` | `alarm:jkl012` |
| Notification | `notification:<id>` | `notification:mno345` |
| Chat Message | `chat:<id>` | `chat:pqr678` |

**LocusGraph Event Payloads**:
- All events use `event_kind` (e.g., "fact", "action", "decision")
- Events are stored with `context_id` for identification
- Related events use `related_to` links

## Testing Best Practices

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── test_auth.py                # Authentication tests
├── test_health.py              # Health monitoring tests
├── test_medication.py          # Medication tests
├── test_appointments.py        # Appointment tests
├── test_emergency.py           # Emergency tests
├── test_tracking.py            # Activity tracking tests
├── test_chat.py                # Chat tests
├── test_profile.py             # Profile tests
└── test_alarms.py              # Alarm tests
```

### Test Example

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_health_vitals():
    """Test creating health vitals"""
    response = client.post(
        "/api/health/vitals",
        json={
            "heart_rate": 75,
            "blood_pressure": "125/82",
            "temperature": 98.7,
            "oxygen_level": 97
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
```

## Common Issues

### Module Import Errors

```bash
# Ensure you're in the project root
cd /path/to/podd/backend

# Check virtual environment is active
which python  # Should show podd_env/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### SQLite Database Connection Errors

```bash
# Check database exists
ls -la podd_auth.db

# Check database connection
sqlite3 podd_auth.db ".tables"

# Verify environment variable
echo $DATABASE_URL
```

### LocusGraph SDK Connection Errors

```bash
# Check LocusGraph service is running
curl http://localhost:8001/health

# Check API key
echo $LOCUSGRAPH_API_KEY

# Verify LocusGraph configuration
nano .env
```

### JWT Token Issues

```bash
# Generate new JWT secret
openssl rand -hex 32

# Update .env file with new secret
# Restart application
sudo systemctl restart podd
```

## Useful Commands

### Python

```bash
# List installed packages
pip list

# Show package info
pip show fastapi

# Upgrade pip
pip install --upgrade pip

# Install package in editable mode
pip install -e .
```

### Git

```bash
# Check status
git status

# View changes
git diff

# Commit changes
git add .
git commit -m "message"

# Push to remote
git push origin feature/branch

# Pull changes
git pull origin main
```

### Docker

```bash
# Build image
docker build -t podd-backend:latest .

# Run container
docker run -p 8000:8000 podd-backend:latest

# View logs
docker logs -f container_id

# Stop container
docker stop container_id

# Remove container
docker rm container_id
```

### System

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check running services
systemctl status podd

# View application logs
tail -f /var/log/podd/app.log
```

## Environment Setup Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] .env file created
- [ ] SQLite database initialized
- [ ] LocusGraph SDK configured
- [ ] OpenAI API key configured
- [ ] JWT secret generated
- [ ] CORS origins configured
- [ ] Application running
- [ ] API documentation accessible

## Development Workflow

1. **Fork repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**: Modify code
4. **Test changes**: Run `pytest`
5. **Format code**: Run `black .`
6. **Lint code**: Run `ruff check .`
7. **Commit changes**: `git commit -m "Add amazing feature"`
8. **Push branch**: `git push origin feature/amazing-feature`
9. **Create PR**: Open pull request

## Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [LocusGraph Documentation](https://locusgraph.com/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python PEP 8 Style Guide](https://peps.python.org/pep-0008/)

## Getting Help

- **Documentation**: Check docs folder
- **Issues**: Check GitHub issues
- **Email**: support@example.com
- **Slack**: #podd-help channel
