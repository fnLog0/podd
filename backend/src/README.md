|# 🏥 Healthcare Workflow Management System

A comprehensive backend service designed to manage healthcare workflows, featuring user authentication, health monitoring, medication tracking, appointment scheduling, emergency response systems, and AI-powered health recommendations.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)

## Overview

This is a full-stack healthcare workflow management backend built with Python. It provides a robust platform for managing patient care workflows, integrating various healthcare services including:

- **Dual-Database Architecture**: SQLite for authentication + LocusGraph SDK for health data
- User authentication and authorization
- Health monitoring and vital signs tracking
- Medication management and reminders
- Appointment scheduling with providers
- Emergency response systems
- AI-powered health recommendations
- Voice interface support
- Wellness and activity tracking

## Key Features

### 🔐 Authentication & Security
- **JWT-based authentication** - Secure token management
- **User registration** - Registration with role-based access
- **Token refresh mechanism** - Extended session validity
- **Password encryption** - Secure password storage
- **SQLite authentication database** - Isolated user credentials

### 📊 Health Monitoring
- **Vital sign tracking** - Real-time health metrics collection
- **Alert system** - Automated health warnings
- **Dashboard customization** - Personalized health views
- **Historical data analysis** - Long-term health trends
- **LocusGraph SDK integration** - Event-based health data storage

### 💊 Medication Management
- **Medication scheduling** - Automated reminder system
- **Dosage tracking** - Medication adherence monitoring
- **Interaction checking** - Drug interaction validation
- **Refill notifications** - Prescription reminder system
- **LocusGraph event storage** - Linked schedules and logs

### 📅 Appointment System
- **Calendar integration** - Seamless booking experience
- **Automated reminders** - SMS/email notifications
- **Provider management** - Doctor availability tracking
- **Appointment types** - Specialized care scheduling

### ⚠️ Emergency Response
- **Immediate alerts** - Real-time emergency notifications
- **Location-based routing** - GPS-enabled emergency navigation
- **First responder coordination** - Multi-agency support
- **Emergency contacts** - Critical contact management

### 🤖 AI Health Assistant
- **Personalized recommendations** - Custom health advice
- **Symptom analysis** - AI-powered triage system
- **Interaction warnings** - Intelligent drug interaction detection
- **Health insights** - Data-driven recommendations

### 📝 Daily Health Summaries
- **Automated reports** - Daily health summaries
- **Progress tracking** - Long-term health monitoring
- **Actionable insights** - Recommendations based on data
- **LocusGraph queries** - Efficient data retrieval

### 🏃‍♂️ Activity Tracking
- **Fitness monitoring** - Exercise and activity tracking
- **Goal setting** - Personal health targets
- **Wearable integration** - Device connectivity support
- **LocusGraph events** - Structured activity logging

### 🧘‍♀️ Wellness Features
- **Guided meditation** - Meditation session integration
- **Mindfulness exercises** - Mental health resources
- **Stress reduction** - Wellness programs
- **LocusGraph tracking** - Session history and analytics

### 🎙️ Voice Interface
- **Voice commands** - Hands-free operation
- **Accessibility support** - For patients with disabilities
- **Natural language processing** - Voice recognition
- **Sarvam AI integration** - Indian language support

### 🗄️ Dual-Database Architecture
- **SQLite (podd_auth.db)** - Authentication-only database
  - Stores Users and RefreshTokens tables
  - Isolated security boundary
  - Created automatically
- **LocusGraph SDK** - Primary health data store
  - 16 event types for health data
  - Event-based schema with context_id prefixes
  - Scalable for large-scale health data

## Project Architecture

```
backend/src/
├── auth/                      # Authentication module
│   ├── __init__.py
│   ├── routes.py              # Authentication routes
│   ├── services.py            # Authentication business logic
│   └── models.py              # User authentication models (SQLite)
│
├── routes/                    # API route definitions
│   ├── auth.py                # Authentication routes
│   ├── health.py              # Health monitoring routes
│   ├── medication.py          # Medication management routes
│   ├── appointments.py        # Appointment routes
│   ├── emergency.py           # Emergency response routes
│   ├── wellness.py            # Wellness features routes
│   └── voice.py               # Voice interface routes
│
├── workflows/                 # Workflow management
│   ├── __init__.py
│   ├── processes.py           # Workflow process definitions
│   ├── orchestrator.py        # Workflow orchestration
│   └── state_management.py    # Workflow state management
│
├── models/                    # Data models
│   ├── __init__.py
│   ├── user.py                # User models (SQLite)
│   ├── health.py              # Health tracking models
│   ├── medication.py          # Medication models
│   ├── appointment.py         # Appointment models
│   ├── emergency.py           # Emergency models
│   └── ai_recommendations.py  # AI recommendation models
│
├── services/                  # Business logic services
│   ├── __init__.py
│   ├── locusgraph/            # LocusGraph SDK integration
│   │   ├── __init__.py
│   │   ├── service.py         # Core LocusGraph client wrapper
│   │   └── cache.py           # Cache within LocusGraph
│   ├── temporal/              # Time-based queries & scheduling
│   │   ├── __init__.py
│   │   └── scheduler.py
│   ├── validation/            # Validation & duplicate detection
│   │   ├── __init__.py
│   │   ├── memory.py          # Learn from validation failures
│   │   └── duplicate.py       # Semantic duplicate detection
│   ├── batch/                 # Bulk operations with tracking
│   │   ├── __init__.py
│   │   └── operations.py
│   ├── migration/             # Schema migration tracking
│   │   ├── __init__.py
│   │   └── schema.py
│   └── sarvam_service.py      # Sarvam AI service
│
├── config/                    # Configuration
│   ├── __init__.py
│   ├── settings.py            # Application settings
│   └── database.py            # Database configuration
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── helpers.py             # Helper functions
│   └── validators.py          # Validation utilities
│
└── app.py                     # Main application entry point
```

## Installation & Setup

### Prerequisites

- **Python 3.8+**
- **LocusGraph SDK** - Event-based health data storage
- **SQLite** - Authentication database (included with Python)
- **pip** package manager
- **Node.js** (for development tools, optional)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd podd/backend/src
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set Up Databases

The system uses a dual-database architecture:

**SQLite (Authentication Only) - Created Automatically:**
```bash
# SQLite database (podd_auth.db) is created automatically
# No additional setup needed
# Stores only Users and RefreshTokens tables
```

**LocusGraph SDK (Health Data):**
```bash
# No setup required if LocusGraph service is available
# Configured via environment variables
```

#### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
# SQLite Authentication Configuration
DATABASE_URL=sqlite:///podd_auth.db

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LocusGraph SDK Configuration
LOCUSGRAPH_API_URL=https://api.locusgraph.io
LOCUSGRAPH_API_KEY=your-locusgraph-api-key
LOCUSGRAPH_GRAPH_ID=your-graph-id

# Application Configuration
DEBUG=True
PORT=8000
HOST=0.0.0.0

# AI Service Configuration
AI_API_KEY=your-ai-api-key
AI_SERVICE_URL=https://api.example.com/ai

# Notification Configuration
SMS_API_KEY=your-sms-api-key
EMAIL_SERVICE_URL=https://api.example.com/email

# Emergency Configuration
EMERGENCY_CONTACT_NUMBER=1234567890
EMERGENCY_SERVICE_URL=https://api.example.com/emergency
```

#### 6. Run Database Setup

SQLite database is created automatically on first startup. No migrations required.

#### 7. Create Admin User

```bash
python -m src.auth.cli create-admin
```

## Configuration

### Dual-Database Architecture

The system uses a dual-database architecture:

**1. SQLite (podd_auth.db) - Authentication Only**
- Stores only authentication-related data
- Tables: `Users`, `RefreshTokens`
- Used for JWT token management and user credentials
- Created automatically on first startup
- Security boundary for authentication

**2. LocusGraph SDK - Health Data Store**
- Stores all health and personal data as structured events
- Event types: Profile, FoodLog, Vitals, Medication, MedicationSchedule, WaterLog, SleepLog, ExerciseLog, MoodLog, MeditationSession, MeditationLog, Appointment, EmergencyContact, Alarm, Notification, ChatMessage
- Each event uses a specific `context_id` format for efficient retrieval
- Accessed via LocusGraph SDK integration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | SQLite database path | Yes | `sqlite:///podd_auth.db` |
| `SECRET_KEY` | JWT secret key for token signing | Yes | - |
| `ALGORITHM` | JWT encryption algorithm | Yes | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | Yes | 30 |
| `LOCUSGRAPH_API_URL` | LocusGraph API endpoint | Yes | - |
| `LOCUSGRAPH_API_KEY` | LocusGraph API key | Yes | - |
| `LOCUSGRAPH_GRAPH_ID` | LocusGraph graph identifier | Yes | - |
| `DEBUG` | Debug mode | No | False |
| `PORT` | Application port | No | 8000 |
| `AI_API_KEY` | AI service API key | No | - |

## API Documentation

The API documentation is available via Swagger/OpenAPI at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints

#### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

#### Health Monitoring Endpoints
- `GET /api/health` - Get health metrics (vitals)
- `POST /api/health/vitals` - Create vital signs
- `GET /api/health/history` - Get health history

#### Medication Management Endpoints
- `GET /api/medication/schedules` - Get medication schedules
- `POST /api/medication/schedules` - Create medication schedule
- `GET /api/medication/logs` - Get medication logs
- `POST /api/medication/logs` - Create medication log

#### Appointment Endpoints
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Create appointment
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment

#### Emergency Endpoints
- `GET /api/emergency/contacts` - Get emergency contacts
- `POST /api/emergency/contacts` - Create emergency contact
- `POST /api/emergency/alert` - Trigger emergency alert

#### Voice Interface Endpoints
- `POST /api/voice/command` - Process voice command
- `GET /api/voice/synthesize` - Get voice synthesis

#### Wellness Endpoints
- `GET /api/tracking/food` - Get food logs
- `POST /api/tracking/food` - Create food log
- `GET /api/tracking/exercise` - Get exercise logs
- `POST /api/tracking/exercise` - Create exercise log
- `GET /api/tracking/mood` - Get mood logs
- `POST /api/tracking/mood` - Create mood log
- `GET /api/tracking/sleep` - Get sleep logs
- `POST /api/tracking/sleep` - Create sleep log
- `GET /api/tracking/water` - Get water logs
- `POST /api/tracking/water` - Create water log

#### Meditation Endpoints
- `GET /api/meditation/sessions` - Get meditation sessions
- `POST /api/meditation/sessions` - Create meditation session

#### Chat Endpoints
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history` - Get chat history

#### Profile Endpoints
- `GET /api/profile` - Get profile
- `PUT /api/profile` - Update profile

#### Alarm Endpoints
- `GET /api/alarms` - Get alarms
- `POST /api/alarms` - Create alarm
- `PUT /api/alarms/{id}` - Update alarm
- `DELETE /api/alarms/{id}` - Delete alarm
- `GET /api/alarms/notifications` - Get notifications
- `POST /api/alarms/notifications/{id}/read` - Mark notification read

For detailed API documentation and examples, visit the Swagger UI at `http://localhost:8000/docs`.

## Development

### Running the Application

```bash
# Development mode with auto-reload
python -m uvicorn app:app --reload --port 8000

# Production mode
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Code Style Guidelines

- **PEP 8** - Python code style guide
- **Type hints** - Use type annotations for functions
- **Docstrings** - Document all functions and classes
- **Import ordering** - Follow standard library → third party → local imports

### Project Structure

```
backend/
├── src/                      # Source code
├── tests/                    # Test files
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore patterns
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_health.py

# Run specific test function
python -m pytest tests/test_health.py::test_health_metric
```

### Test Coverage

Test coverage should be maintained at **80%+**. Coverage report is generated in `htmlcov/index.html`.

### Testing Dependencies

```bash
pip install pytest pytest-cov pytest-django
```

## Deployment

### Production Setup

1. **Set Environment Variables**
   - Configure production `.env` file
   - Use strong `SECRET_KEY`
   - Set `DEBUG=False`
   - Configure LocusGraph SDK with production API credentials

2. **Database Setup**
   - SQLite database created automatically
   - Configure LocusGraph backup strategy
   - Set up database backups for SQLite

3. **Run Application**
   ```bash
   python -m gunicorn app:app --workers 4 --bind 0.0.0.0:8000
   ```

### Docker Deployment

```bash
# Build Docker image
docker build -t healthcare-workflow .

# Run container
docker run -p 8000:8000 --env-file .env healthcare-workflow
```

### Environment for Production

| Variable | Production Value |
|----------|------------------|
| `DEBUG` | False |
| `DATABASE_URL` | `sqlite:///podd_auth.db` |
| `SECRET_KEY` | Strong random string |
| `PORT` | 8000 |
| `WORKERS` | 4 (or more) |
| `LOCUSGRAPH_API_URL` | Production LocusGraph endpoint |
| `LOCUSGRAPH_API_KEY` | Production LocusGraph API key |
| `LOCUSGRAPH_GRAPH_ID` | Production LocusGraph graph ID |

### Database Backup Strategy

**SQLite Backup:**
```bash
# Backup SQLite database
cp podd_auth.db podd_auth.db.backup

# Automated backup script
python scripts/backup_sqlite.py
```

**LocusGraph Backup:**
```bash
# Backup all events
python scripts/backup_locusgraph.py

# Export events by context type
python scripts/export_locusgraph.py --context-type vitals
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` is correct
   - Ensure SQLite database file exists
   - Check LocusGraph API credentials

2. **LocusGraph SDK Issues**
   - Verify `LOCUSGRAPH_API_URL` is accessible
   - Check API key has proper permissions
   - Ensure graph ID is correct
   - Test connectivity: `python scripts/test_locusgraph.py`

3. **JWT Token Issues**
   - Verify `SECRET_KEY` matches across services
   - Check token expiration time
   - Ensure correct algorithm is used

4. **Import Errors**
   - Verify all dependencies are installed
   - Check Python path configuration
   - Restart application after installation

### Getting Help

For issues and questions:
- Check the API documentation at `/docs`
- Review the troubleshooting section
- Check [Documentation Index](../docs/README.md) for detailed guides
- Open an issue on GitHub
- Contact the development team

## LocusGraph SDK Integration

### Event Types

The system uses 16 event types for health data:

- `profile:<id>` - User profile information
- `vitals:<id>` - Vital signs (heart rate, blood pressure, etc.)
- `food:<id>` - Food logs
- `med_schedule:<id>` - Medication schedules
- `med_log:<id>` - Medication logs
- `water:<id>` - Water intake logs
- `sleep:<id>` - Sleep logs
- `exercise:<id>` - Exercise logs
- `mood:<id>` - Mood logs
- `meditation_session:<id>` - Meditation sessions
- `meditation_log:<id>` - Meditation logs
- `appointment:<id>` - Appointments
- `emergency_contact:<id>` - Emergency contacts
- `alarm:<id>` - Alarms
- `notification:<id>` - Notifications
- `chat:<id>` - Chat messages

### SDK Methods

```python
# Store event
await store_event(
    event_kind="fact",
    context_id="vitals:<id>",
    payload={...},
    related_to=[],
    source="api"
)

# Retrieve context
events = await retrieve_context(
    context_type="vitals",
    user_id="<user_id>",
    filters={"recorded_after": "2026-02-01"}
)

# Generate insights
insights = await generate_insights(
    user_id="<user_id>",
    query={"context_type": "vitals"}
)

# Update event
await update_event(
    context_id="vitals:<id>",
    updates={"heart_rate": 80}
)

# Delete event
await delete_event(context_id="vitals:<id>")
```

For more details, see the [Database Schema Documentation](../docs/database_schema.md).

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Review Process

- All changes require a pull request
- Reviewers will check for code quality and security
- Tests must pass before approval
- Documentation should be updated if needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Healthcare API documentation standards
- Open source Python frameworks
- Medical community for feedback and suggestions
- LocusGraph SDK for event-based data storage

## Support

For support and questions, please contact the development team at support@healthcareworkflow.com

## Related Documentation

- [Documentation Index](../docs/README.md) - Complete documentation overview and reading guide
- [Architecture Documentation](../docs/architecture.md) - System design and dual-database architecture
- [Database Schema](../docs/database_schema.md) - SQLite and LocusGraph event schemas
- [API Documentation](../docs/api_documentation.md) - Complete API reference with LocusGraph integration details
- [Deployment Guide](../docs/deployment.md) - Deployment procedures
- [Workflow Documentation](../docs/workflows.md) - Workflow definitions and AI agents
- [Quick Reference](../docs/quick_reference.md) - Quick reference for developers

---

**Version**: 1.2.0
**Last Updated**: February 18, 2026
**Architecture**: Dual-Database (SQLite + LocusGraph SDK)
