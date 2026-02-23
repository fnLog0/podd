# Architecture Documentation

## Overview

The Podd Health Assistant is built on a **dual-database architecture** designed for healthcare applications:

1. **SQLite (`podd_auth.db`)**: Stores ONLY authentication data (User, RefreshToken tables) - no health data
2. **LocusGraph SDK**: Stores ALL health and personal data (Profiles, Vitals, Medications, Schedules, Activities, Reminders, Chat) - the primary data store

The architecture follows best practices for security, performance, and maintainability, with specific integration patterns for:
- **Dual-database model**: SQLite for auth, LocusGraph SDK for health data
- **LocusGraph event schemas**: Structured payloads with specific `context_id` formats
- **LangGraph workflow**: Orchestrating health agents with LocusGraph SDK tools
- **Sarvam AI**: Indian-language voice processing (STT/TTS)

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Mobile  │  │  Web App │  │  Voice   │  │  Desktop │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway Layer                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              FastAPI Application Server                   │  │
│  │  - RESTful API Endpoints                                   │  │
│  │  - WebSocket Support                                       │  │
│  │  - CORS Middleware                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Auth Layer  │   │  Business     │   │  AI/LLM Layer │
│   (Auth)      │   │  Services     │   │  (LangChain)  │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  JWT Token    │   │  Workflow     │   │  Sarvam AI    │
│  Management   │   │  Orchestration│   │  (Voice)      │
└───────────────┘   │  Engine       │   └───────────────┘
                    └───────────────┘         │
                    └───────────────┘         │
                                             ▼
                                      ┌───────────────┐
                                      │   LocusGraph  │
                                      │   Memory Svc  │
                                      └───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Data Layer                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │   SQLite DB      │  │   LocusGraph     │  │  Redis Cache   │  │  Sarvam AI     │ │
│  │  (Auth Only)     │  │   SDK (Health)   │  │  (Optional)    │  │  (Voice)       │ │
│  │  (podd_auth.db)  │  │  - store_event() │  │                │  │  - STT/TTS     │ │
│  └──────────────────┘  │  - retrieve()    │  └────────────────┘  └────────────────┘ │
│                        │  - insights()    │                                 │
│                        └──────────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Core Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | Web Framework | 0.122.0 |
| **Uvicorn** | ASGI Server | 0.38.0 |
| **SQLAlchemy** | ORM (Auth only) | 2.0.46 |
| **aiosqlite** | Async SQLite Driver | 0.22.1 |
| **LocusGraph SDK** | Primary Health Data Store | Custom |
| **Pydantic** | Data Validation | 2.12.5 |

### AI & LLM Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **LangChain** | LLM Framework | 0.6.11 |
| **LangGraph** | Stateful Workflows | 0.6.11 |
| **Sarvam AI** | Regional AI Service (Voice STT/TTS) | Latest |
| **LocusGraph SDK** | Memory Service (Health Data) | Custom |

### Database Architecture

**Dual-Database Model**:

The Podd Health Assistant uses a **dual-database architecture**:

1. **SQLite (`podd_auth.db`)**: Stores ONLY authentication data
   - `users` table (id, email, password_hash, name, created_at, updated_at)
   - `refresh_tokens` table (id, user_id, token, expires_at, created_at)
   - Created automatically on startup via SQLAlchemy `create_all()`
   - No migrations required

2. **LocusGraph SDK**: Stores ALL health and personal data
   - Health events: Profile, FoodLog, Vitals, Medication, WaterLog, SleepLog, ExerciseLog, MoodLog
   - Schedules: MedicationSchedule, Appointment, EmergencyContact
   - Reminders: Alarm, Notification
   - Activities: MeditationSession, MeditationLog, ChatMessages
   - Uses `context_id` format for each entity type (e.g., `profile:<user_id>`, `vitals:<id>`, `food:<id>`)
   - Primary operations: `store_event()`, `retrieve_context()`, `generate_insights()`

### Security Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **PyJWT** | JWT Tokens | 2.11.0 |
| **python-jose** | JWT Library | 3.5.0 |
| **passlib** | Password Hashing | 1.7.4 |
| **bcrypt** | Secure Hashing | 5.0.0 |
| **cryptography** | Encryption | 46.0.5 |

### Development Tools

| Technology | Purpose | Version |
|------------|---------|---------|
| **pytest** | Testing Framework | 8.4.2 |
| **pytest-asyncio** | Async Testing | 1.2.0 |
| **black** | Code Formatter | 25.11.0 |
| **ruff** | Linter | 0.14.7 |
| **mypy** | Type Checker | Latest |

## Application Modules

### 1. Authentication Module (`src/auth`)

**Purpose**: Handles user authentication and authorization

**Components**:
- `jwt.py`: JWT token creation, verification, and refresh
- `dependencies.py`: FastAPI dependencies for authentication
- `models.py`: Authentication-related models

**Key Features**:
- JWT token-based authentication
- Token refresh mechanism
- Role-based access control (planned)
- Secure password hashing with bcrypt

**Flow**:
```
1. User logs in → Generate JWT tokens
2. Client stores tokens → Access token + refresh token
3. Access token expires → Use refresh token to get new access token
4. Refresh token expires → User must re-authenticate
```

### 2. API Routes (`src/routes`)

**Purpose**: Defines all API endpoints

**Components**:
- `auth.py`: Authentication endpoints
- `health.py`: Health monitoring endpoints
- `medication.py`: Medication management endpoints
- `appointments.py`: Appointment endpoints
- `emergency.py`: Emergency response endpoints
- `voice.py`: Voice interface endpoints
- `meditation.py`: Meditation tracking endpoints
- `tracking.py`: Activity tracking endpoints
- `chat.py`: AI chat endpoints
- `profile.py`: User profile endpoints
- `alarms.py`: Alarm and notification endpoints

**Design Pattern**:
- Each module has its own router
- All routers are mounted to `/api` prefix
- Consistent response format across all endpoints

### 3. Business Services (`src/services`)

**Purpose**: Contains business logic and external service integrations

**Structure**:
```
src/services/
├── __init__.py                    # Main exports
├── locusgraph/                    # LocusGraph SDK integration
│   ├── __init__.py
│   ├── service.py                 # Core LocusGraph client wrapper
│   └── cache.py                   # Cache within LocusGraph
├── temporal/                      # Time-based queries & scheduling
│   ├── __init__.py
│   └── scheduler.py
├── validation/                    # Validation & duplicate detection
│   ├── __init__.py
│   ├── memory.py                  # Learn from validation failures
│   └── duplicate.py               # Semantic duplicate detection
├── batch/                         # Bulk operations with tracking
│   ├── __init__.py
│   └── operations.py
├── migration/                    # Schema migration tracking
│   ├── __init__.py
│   └── schema.py
└── sarvam_service.py              # Sarvam AI service integration
```

**LocusGraph SDK Integration**:
- **store_event()**: Store health events with structured payloads
- **retrieve_context()**: Retrieve relevant health data by context_id or type
- **generate_insights()**: Generate health insights from stored events

**Temporal Utilities**:
- **TemporalScheduler**: Schedule reminders and manage temporal queries
- **TemporalContext**: Enrich events with temporal metadata (day_of_week, is_today)
- **get_temporal_contexts()**: Query events by time ranges (upcoming, past, due)

**Validation Services**:
- **ValidationMemory**: Remember validation failures to prevent recurring errors
- **URLValidator**: Validate and learn from broken URLs
- **PhoneValidator**: Validate phone numbers and learn patterns

**Duplicate Detection**:
- **DuplicateDetector**: Generic semantic duplicate detection
- **AppointmentDuplicateDetector**: Find similar appointments
- **EmergencyContactDuplicateDetector**: Find duplicate contacts
- **MeditationSessionDuplicateDetector**: Find duplicate meditation sessions

**Batch Operations**:
- **BatchOperation**: Track batch operations with context linking
- **BatchAppointmentCreator**: Bulk create appointments
- **BatchEmergencyContactCreator**: Bulk create emergency contacts
- **BatchMeditationSessionCreator**: Bulk create meditation sessions

**Schema Migrations**:
- **SchemaMigrationManager**: Track and rollback schema changes
- **ensure_schema_version()**: Ensure database schema is at correct version

**LangGraph Tools**:
- `store_health_event`: Wraps LocusGraph SDK `store_event()`
- `retrieve_health_context`: Wraps LocusGraph SDK `retrieve_context()`
- `generate_health_insights`: Wraps LocusGraph SDK `generate_insights()`
- `get_user_profile`: Fetches profile via LocusGraph SDK
- `get_recent_vitals`: Fetches recent vitals via LocusGraph SDK
- `get_medication_schedule`: Fetches active medications via LocusGraph SDK

**Responsibilities**:
- External API integration
- Business logic implementation
- Data transformation and validation
- Caching (within LocusGraph)
- Workflow orchestration via LangGraph
- Temporal queries and scheduling
- Duplicate detection and validation

### 4. Data Models (`src/models`)

**Purpose**: Defines database schemas and data structures

**Components**:
- `user.py`: User model
- `refresh_token.py`: Refresh token model
- Other models (planned)

**Database Design**:
- Uses SQLAlchemy ORM
- Async operations with aiosqlite
- Automatic table creation on startup

### 5. Schemas (`src/schemas`)

**Purpose**: Pydantic models for request/response validation

**Components**:
- `auth.py`: Authentication schemas
- Other schemas (planned)

**Benefits**:
- Automatic validation
- Type checking
- Documentation generation (Swagger)
- Serialization/deserialization

### 6. Workflow Engine (`src/workflows`)

**Purpose**: Manages complex workflows and AI agent coordination

**Components**:
- `health_workflow.py`: Health monitoring workflows
- `daily_summary.py`: Daily summary generation workflows
- `nodes/`: Workflow nodes and agents
  - `agents/`: AI agents for different tasks
  - `context.py`: Workflow context management
  - `memory.py`: Memory management
  - `normalize.py`: Data normalization
  - `response.py`: Response generation
  - `router.py`: Workflow routing

**LangGraph Integration**:
- Stateful workflows
- Agent coordination (Router, Food Tracking, Health Query, Recommendation, General Chat)
- Human-in-the-loop workflows
- Memory and checkpointing
- Tools wrapping LocusGraph SDK for data operations

### 7. Configuration (`src/config`)

**Purpose**: Centralized configuration management

**Components**:
- `settings.py`: Application settings using Pydantic Settings

**Features**:
- Environment variable loading
- Type-safe configuration
- Default values
- Validation

### 8. Database Layer (`src/database`)

**Purpose**: Database connection and session management

**Components**:
- Database engine creation
- Session management
- Base model definition
- Table creation utilities

**Architecture**:
- Async database operations
- Connection pooling
- Context-based session management

## Database Schema

### Authentication Database (SQLite)

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Health Data Store (LocusGraph SDK)

**LocusGraph stores all health-related data as events with structured payloads.** Each entity type uses a specific `context_id` format for identification.

#### Profile Event
```json
{
  "event_kind": "fact",
  "context_id": "profile:<user_id>",
  "payload": {
    "date_of_birth": "1960-01-15",
    "gender": "female",
    "height_cm": 165,
    "weight_kg": 60,
    "blood_type": "O+",
    "allergies": ["penicillin", "peanuts"],
    "medical_conditions": ["hypertension"],
    "dietary_preferences": "vegetarian"
  }
}
```

#### FoodLog Event
```json
{
  "event_kind": "fact",
  "context_id": "food:<id>",
  "payload": {
    "description": "Rice and dal",
    "calories": 400,
    "protein_g": 12,
    "carbs_g": 60,
    "fat_g": 8,
    "meal_type": "lunch",
    "logged_at": "2026-02-18T12:30:00Z"
  }
}
```

#### Vitals Event
```json
{
  "event_kind": "fact",
  "context_id": "vitals:<id>",
  "payload": {
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "heart_rate": 72,
    "blood_sugar": 100,
    "temperature": 98.6,
    "weight_kg": 60,
    "logged_at": "2026-02-18T08:00:00Z"
  }
}
```

#### Medication Event
```json
{
  "event_kind": "fact",
  "context_id": "medication:<id>",
  "payload": {
    "name": "Metformin",
    "dosage": "500mg",
    "frequency": "twice daily",
    "instructions": "Take after meals",
    "active": true
  }
}
```

#### MedicationSchedule Event
```json
{
  "event_kind": "fact",
  "context_id": "med_schedule:<id>",
  "payload": {
    "medication_id": "medication:<med_id>",
    "time_of_day": "08:00",
    "days_of_week": ["1", "2", "3", "4", "5"]
  }
}
```

#### WaterLog Event
```json
{
  "event_kind": "fact",
  "context_id": "water:<id>",
  "payload": {
    "amount_ml": 250,
    "logged_at": "2026-02-18T10:00:00Z"
  }
}
```

#### SleepLog Event
```json
{
  "event_kind": "fact",
  "context_id": "sleep:<id>",
  "payload": {
    "sleep_start": "2026-02-17T23:00:00Z",
    "sleep_end": "2026-02-18T06:30:00Z",
    "quality": 7,
    "notes": "Felt rested"
  }
}
```

#### ExerciseLog Event
```json
{
  "event_kind": "fact",
  "context_id": "exercise:<id>",
  "payload": {
    "exercise_type": "walking",
    "duration_minutes": 30,
    "calories_burned": 150,
    "intensity": "moderate",
    "logged_at": "2026-02-18T17:00:00Z"
  }
}
```

#### MoodLog Event
```json
{
  "event_kind": "fact",
  "context_id": "mood:<id>",
  "payload": {
    "mood": "happy",
    "energy_level": 8,
    "notes": "Good day overall",
    "logged_at": "2026-02-18T18:00:00Z"
  }
}
```

#### MeditationSession Event
```json
{
  "event_kind": "fact",
  "context_id": "meditation_session:<id>",
  "payload": {
    "title": "Morning Calm",
    "description": "5-minute guided meditation",
    "audio_url": "https://example.com/audio/morning_calm.mp3",
    "duration_minutes": 5,
    "category": "morning"
  }
}
```

#### MeditationLog Event
```json
{
  "event_kind": "fact",
  "context_id": "meditation_log:<id>",
  "payload": {
    "session_id": "meditation_session:<session_id>",
    "duration_minutes": 5,
    "completed": true,
    "logged_at": "2026-02-18T07:00:00Z"
  }
}
```

#### Appointment Event
```json
{
  "event_kind": "fact",
  "context_id": "appointment:<id>",
  "payload": {
    "title": "Annual Checkup",
    "doctor_name": "Dr. Sharma",
    "location": "City Hospital",
    "scheduled_at": "2026-03-15T10:00:00Z",
    "notes": "Bring recent reports",
    "reminder_minutes_before": 30
  }
}
```

#### EmergencyContact Event
```json
{
  "event_kind": "fact",
  "context_id": "emergency_contact:<id>",
  "payload": {
    "name": "Rahul (Son)",
    "relationship": "son",
    "phone": "+91-9876543210",
    "is_primary": true
  }
}
```

#### Alarm Event
```json
{
  "event_kind": "fact",
  "context_id": "alarm:<id>",
  "payload": {
    "type": "medication",
    "title": "Take Metformin",
    "message": "Time to take your 500mg Metformin",
    "time": "08:00",
    "days_of_week": ["1", "2", "3", "4", "5"],
    "active": true,
    "reference_id": "med_schedule:<schedule_id>"
  }
}
```

#### Notification Event
```json
{
  "event_kind": "fact",
  "context_id": "notification:<id>",
  "payload": {
    "alarm_id": "alarm:<alarm_id>",
    "title": "Time to take Metformin",
    "message": "Take your 500mg Metformin now",
    "type": "medication",
    "read": false,
    "created_at": "2026-02-18T08:00:00Z"
  }
}
```

#### ChatMessage Event
```json
{
  "event_kind": "action",
  "context_id": "chat:<id>",
  "payload": {
    "user_message": "How are you feeling today?",
    "ai_response": "I'm doing well, thanks for asking! How about you?",
    "context": {"topic": "health"},
    "timestamp": "2026-02-18T14:30:00Z"
  }
}
```

**LocusGraph API Methods**:
- `store_event(event_kind, context_id, payload, related_to=[])`: Store a new event
- `retrieve_context(context_type, user_id, filters={})`: Retrieve events by type and filters
- `generate_insights(user_id, query={})`: Generate health insights from stored events
- `update_event(context_id, updates)`: Update an existing event
- `delete_event(context_id)`: Delete an event

## Data Flow

### Authentication Flow
```
1. Client → POST /auth/register
   {
     email, password, name
   }

2. Server → Validate inputs
           → Hash password
           → Create user
           → Generate JWT tokens
           → Return tokens

3. Client → Store access_token + refresh_token
           → Use access_token for subsequent requests
           → Send refresh_token when access_token expires

4. Server → Verify JWT signature
           → Check token expiration
           → Return user data

5. Server → POST /auth/refresh
           → Validate refresh token
           → Generate new access token
           → Return new tokens
```

### Health Monitoring Flow
```
1. Client → POST /health/vitals
   {
     heart_rate, blood_pressure, temperature, oxygen_level
   }

2. Server → Validate inputs
           → Call LocusGraph SDK store_event() with event_kind "vitals:<id>"
           → Trigger workflow for recommendations
           → Return created record

3. Server → GET /health/recommendations
           → Call LocusGraph SDK retrieve_context() for user's vitals history
           → Call LocusGraph SDK generate_insights() for health analysis
           → Generate AI recommendations
           → Return recommendations
```

### Medication Management Flow
```
1. Client → POST /medication/schedules
   {
     name, dosage, frequency, times, days, quantity
   }

2. Server → Validate inputs
           → Call LocusGraph SDK store_event() with event_kind "med_schedule:<id>"
           → Schedule reminders (future enhancement)
           → Return created schedule

3. Client → POST /medication/logs
   {
     schedule_id, dosage, notes
   }

4. Server → Validate inputs
           → Call LocusGraph SDK store_event() with event_kind "medication:<id>"
           → Update schedule completion status
           → Send notification via LocusGraph SDK
           → Return created log
```

### Workflow Execution Flow
```
1. Client → Trigger workflow
   {
     workflow_type: "daily_summary",
     parameters: { user_id, date }
   }

2. Server → Create workflow instance
           → Initialize LangGraph workflow
           → Execute workflow steps

3. Server → Workflow Execution
   Step 1: Collect health data
   Step 2: Analyze trends
   Step 3: Generate insights
   Step 4: Create recommendations
   Step 5: Store results

4. Server → Return workflow results
```

### AI Chat Flow
```
1. Client → POST /chat/message
   {
     message: "What can you tell me about heart health?",
     context: { topic: "heart_health" }
   }

2. Server → Process message
           → Call LocusGraph SDK retrieve_context() for user's health data
           → Generate prompt for LLM
           → Send to Sarvam AI API

3. Server → Receive LLM response
           → Format response
           → Call LocusGraph SDK store_event() with event_kind "chat:<id>"
           → Update LocusGraph memory
           → Return response to client
```

## Security Architecture

### Authentication & Authorization

**JWT Token Flow**:
1. User credentials validated
2. Access token generated (15-60 minutes)
3. Refresh token generated (7-30 days)
4. Tokens stored in secure cookies/local storage
5. Access token sent with each request in `Authorization: Bearer <token>` header

**Token Refresh**:
- When access token expires, client uses refresh token
- Server validates refresh token
- New access token generated
- Refresh token rotation (optional)

**Security Measures**:
- Password hashing with bcrypt (cost factor 12)
- JWT signing with HS256
- Token expiration
- HTTPS enforcement (recommended)
- CORS configuration
- Input validation and sanitization

### Data Protection

**Data Storage**:
- All sensitive data encrypted at rest
- Database queries parameterized to prevent SQL injection
- Environment variables for secrets
- No sensitive data in logs

**API Security**:
- Rate limiting
- Request validation
- Error messages sanitized
- JWT signature verification

### Communication Security

**HTTPS**:
- Use HTTPS in production
- Certificate management
- HSTS headers (optional)

**CORS**:
- Whitelist allowed origins
- Credentials allowed only for trusted origins
- Prevents cross-origin attacks

## Performance Considerations

### Database Performance

**Optimizations**:
- Async database operations with SQLAlchemy
- Indexes on frequently queried columns
- Connection pooling
- Prepared statements
- Query optimization

**Scalability**:
- SQLite for small to medium deployments
- PostgreSQL migration path for large deployments
- Database indexing strategy
- Connection pooling

### API Performance

**Optimizations**:
- Async/await throughout
- Efficient query design
- Response caching
- Pagination for large datasets
- Background processing for heavy operations

**Monitoring**:
- Request/response logging
- Performance metrics
- Error tracking with Sentry
- Database query profiling

### Caching Strategy

**Caching Layers**:
1. Memory cache for frequently accessed data
2. Redis cache (optional)
3. HTTP caching headers
4. Client-side caching

**Cache Invalidation**:
- Time-based expiration
- Write-through cache updates
- Manual invalidation for critical data

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Value is invalid"
    }
  }
}
```

### Error Categories

1. **Authentication Errors**:
   - Invalid credentials
   - Expired token
   - Invalid token

2. **Authorization Errors**:
   - Insufficient permissions
   - Resource not accessible

3. **Validation Errors**:
   - Invalid input format
   - Missing required fields
   - Constraint violations

4. **Resource Errors**:
   - Resource not found
   - Resource already exists
   - Resource update conflict

5. **System Errors**:
   - Database errors
   - External service errors
   - Unexpected exceptions

## Monitoring & Logging

### Logging Strategy

**Log Levels**:
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

**Log Format**:
```
[timestamp] [level] [request_id] [user_id] message
```

**Key Logs**:
- Authentication events
- API requests/responses
- Database queries
- External service calls
- Errors and exceptions

### Monitoring

**Metrics**:
- Request rate
- Response time
- Error rate
- Database query performance
- External service health

**Alerts**:
- High error rate
- Slow response times
- Database connection issues
- External service failures

## Deployment Architecture

### Development Environment

```
Local Development:
- Python virtual environment
- SQLite database
- Development server with auto-reload
- Debug mode enabled
- No caching
```

### Production Environment

```
Production:
- Multiple worker processes
- PostgreSQL database
- Nginx/Gunicorn as reverse proxy
- SSL/TLS enabled
- HTTPS enforced
- Production logging
- Error tracking integration
- Database connection pooling
- Background workers for workflows
```

### Infrastructure Components

**Application Server**:
- Uvicorn with multiple workers
- Process management (systemd/supervisor)
- Health checks

**Web Server (Optional)**:
- Nginx as reverse proxy
- SSL termination
- Static file serving
- Load balancing support

**Database**:
- PostgreSQL (recommended)
- Connection pooling
- Backup strategy
- Replication (optional)

**Caching (Optional)**:
- Redis
- Session storage
- API response caching

**Queue (Optional)**:
- Celery or similar
- Background task processing
- Scheduled jobs

## Scalability Considerations

### Horizontal Scaling

**Stateless Application**:
- All session state stored in database
- JWT tokens stateless
- Stateless API design

**Load Balancing**:
- Multiple instances behind load balancer
- Consistent hashing for sticky sessions
- Scaling database separately

### Vertical Scaling

**Database Optimization**:
- Read replicas
- Query optimization
- Index strategy
- Partitioning for large tables

**Application Optimization**:
- Connection pooling
- Efficient code
- Caching strategy
- Resource limits

## Future Enhancements

### Planned Features

1. **Multi-factor Authentication**
2. **Advanced Analytics**
3. **Integration with Health APIs**
4. **Mobile App Integration**
5. **Advanced Workflow Automation**
6. **Predictive Analytics**
7. **Health Score Calculations**
8. **Family Member Accounts**
9. **Medical Record Integration**
10. **Insurance Integration**

### Infrastructure Improvements

1. **Microservices Architecture**
2. **Containerization with Docker**
3. **Kubernetes Deployment**
4. **CI/CD Pipeline**
5. **Comprehensive Testing**
6. **API Gateway**
7. **Service Mesh**

### Performance Enhancements

1. **GraphQL API**
2. **Real-time Data Pushing**
3. **Advanced Caching**
4. **CDN Integration**
5. **Database Sharding**
