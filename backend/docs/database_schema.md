# Database Schema Documentation

## Overview

The Podd Health Assistant uses a **dual-database architecture**:

1. **SQLite (`podd_auth.db`)**: Stores ONLY authentication data (Users, RefreshTokens tables) - no health data
2. **LocusGraph SDK**: Stores ALL health and personal data (Profiles, Vitals, Medications, Schedules, Activities, Reminders, Chat) - the primary data store

This architecture provides:
- **Security**: Authentication data isolated in SQLite
- **Scalability**: LocusGraph handles large-scale health data
- **Flexibility**: Easy to switch databases without changing business logic

## Database Connection

### SQLite Authentication Database

```python
# src/config.py
DATABASE_URL = "sqlite+aiosqlite:///./podd_auth.db"
```

### LocusGraph SDK

```python
# LocusGraph SDK configuration
LOCUSGRAPH_API_URL = "http://localhost:8001"
LOCUSGRAPH_API_KEY = "your-api-key"
```

## Table Relationships

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  LocusGraph SDK  │
│  (Health Data)   │
└──────────────────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌───────────────┐                   ┌──────────────────┐
│Profile Event  │                   │  Vitals Events   │
│(context_id:   │                   │(context_id:      │
│  profile:     │                   │  vitals:<id>)    │
│  <user_id>)   │                   └──────────────────┘
└───────────────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌───────────────┐                   ┌──────────────────┐
│FoodLog Event  │                   │Medication Event  │
│(context_id:   │                   │(context_id:      │
│  food:<id>)   │                   │  medication:<id>)│
└───────────────┘                   └──────────────────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌───────────────┐                   ┌──────────────────┐
│SleepLog Event │                   │ExerciseLog Event │
│(context_id:   │                   │(context_id:      │
│  sleep:<id>)  │                   │  exercise:<id>)  │
└───────────────┘                   └──────────────────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌───────────────┐                   ┌──────────────────┐
│MoodLog Event  │                   │WaterLog Event    │
│(context_id:   │                   │(context_id:      │
│  mood:<id>)   │                   │  water:<id>)     │
└───────────────┘                   └──────────────────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌───────────────┐                   ┌──────────────────┐
│MedSchedule   │                   │Appointment       │
│Event         │                   │Event             │
│(context_id:  │                   │(context_id:      │
│ med_schedule: │                   │ appointment:<id>)│
│ <id>)        │                   └──────────────────┘
└───────────────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌───────────────┐                   ┌──────────────────┐
│Emergency     │                   │Alarm Event       │
│Contact Event │                   │(context_id:      │
│(context_id:  │                   │  alarm:<id>)     │
│emergency     │                   └──────────────────┘
│_contact:<id>)│
└───────────────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌───────────────┐                   ┌──────────────────┐
│Meditation    │                   │Notification      │
│Session Event │                   │Event             │
│(context_id:  │                   │(context_id:      │
│meditation_   │                   │  notification:<id>)│
│session:<id>) │                   └──────────────────┘
└───────────────┘
       │
       ▼
┌───────────────┐
│ChatMessage   │
│Event         │
│(context_id:  │
│ chat:<id>)   │
└───────────────┘
```

## SQLite Authentication Tables

### Users Table

Stores user account information.

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

**Indexes**:
- Primary key on `id`
- Unique index on `email`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| name | VARCHAR(255) | NOT NULL | User's display name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

---

### Refresh Tokens Table

Stores refresh tokens for JWT token refresh mechanism.

```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes**:
- Primary key on `id`
- Unique index on `token`
- Foreign key on `user_id`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique token identifier |
| user_id | UUID | NOT NULL, FK → users(id) | Associated user |
| token | VARCHAR(255) | UNIQUE, NOT NULL | Refresh token value |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Token creation time |

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

**Cleanup Strategy**:
- Periodic cleanup of expired tokens
- Example: `DELETE FROM refresh_tokens WHERE expires_at < datetime('now', '-7 days');`

---

## LocusGraph Health Data Store

**LocusGraph stores all health-related data as events with structured payloads.** Each entity type uses a specific `context_id` format for identification.

### Profile Event

Stores user profile information.

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

---

### FoodLog Event

Tracks food intake.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| description | string | Yes | Food item description |
| calories | integer | No | Calories consumed |
| protein_g | integer | No | Protein in grams |
| carbs_g | integer | No | Carbohydrates in grams |
| fat_g | integer | No | Fat in grams |
| meal_type | string | No | Meal type (breakfast/lunch/dinner/snack) |
| logged_at | timestamp | Yes | Time food was logged |

---

### Vitals Event

Tracks vital signs measurements.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| blood_pressure_systolic | integer | No | Systolic BP (mmHg) |
| blood_pressure_diastolic | integer | No | Diastolic BP (mmHg) |
| heart_rate | integer | No | Heart beats per minute |
| blood_sugar | integer | No | Blood sugar level (mg/dL) |
| temperature | float | No | Body temperature (°C) |
| weight_kg | float | No | Weight in kilograms |
| logged_at | timestamp | Yes | Measurement timestamp |

---

### Medication Event

Tracks medication usage.

```json
{
  "event_kind": "fact",
  "context_id": "medication:<id>",
  "payload": {
    "name": "Metformin",
    "dosage": "500mg",
    "frequency": "twice daily",
    "instructions": "Take after meals",
    "active": true,
    "logged_at": "2026-02-18T08:00:00Z"
  }
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Medication name |
| dosage | string | No | Dosage amount |
| frequency | string | No | Frequency (e.g., "twice daily") |
| instructions | string | No | Taking instructions |
| active | boolean | Yes | Whether medication is currently active |
| logged_at | timestamp | Yes | Time medication was logged |

---

### MedicationSchedule Event

Defines medication schedules and reminders.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| medication_id | string | Yes | Reference to medication event |
| time_of_day | string | Yes | Time in HH:MM format |
| days_of_week | array | Yes | Days of week (0=Sunday, 1=Monday, etc.) |

---

### WaterLog Event

Tracks daily water intake.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| amount_ml | integer | Yes | Water amount in milliliters |
| logged_at | timestamp | Yes | Time water was logged |

---

### SleepLog Event

Tracks sleep patterns.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sleep_start | timestamp | Yes | Sleep start time |
| sleep_end | timestamp | Yes | Sleep end time |
| quality | integer | No | Sleep quality score (1-10) |
| notes | string | No | Sleep notes |

---

### ExerciseLog Event

Tracks exercise activities.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| exercise_type | string | Yes | Exercise type (walking, running, etc.) |
| duration_minutes | integer | No | Duration in minutes |
| calories_burned | integer | No | Calories burned |
| intensity | string | No | Exercise intensity (low/medium/high) |
| logged_at | timestamp | Yes | Time exercise was logged |

---

### MoodLog Event

Tracks mood and emotional states.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mood | string | Yes | Mood value (happy, sad, anxious, etc.) |
| energy_level | integer | No | Energy level (1-10) |
| notes | string | No | Additional mood notes |
| logged_at | timestamp | Yes | Time mood was logged |

---

### MeditationSession Event

Tracks meditation sessions.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Session title |
| description | string | No | Session description |
| audio_url | string | No | Audio file URL |
| duration_minutes | integer | No | Duration in minutes |
| category | string | No | Meditation category (morning/afternoon/night) |

---

### MeditationLog Event

Tracks completed meditation sessions.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | Yes | Reference to meditation session event |
| duration_minutes | integer | No | Duration in minutes |
| completed | boolean | Yes | Whether session was completed |
| logged_at | timestamp | Yes | Time session was logged |

---

### Appointment Event

Stores appointment information.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Appointment title/description |
| doctor_name | string | No | Doctor's name |
| location | string | No | Appointment location |
| scheduled_at | timestamp | Yes | Appointment date and time |
| notes | string | No | Appointment notes |
| reminder_minutes_before | integer | No | Notification reminder time |

---

### EmergencyContact Event

Stores emergency contact information.

```json
{
  "event_kind": "fact",
  "context_id": "emergency_contact:<id>",
  "payload": {
    "name": "Rahul (Son)",
    "relationship": "son",
    "phone": "+91-9876543210",
    "email": "rahul@email.com",
    "is_primary": true
  }
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Contact name |
| relationship | string | No | Relationship to user |
| phone | string | Yes | Phone number |
| email | string | No | Email address |
| is_primary | boolean | Yes | Whether this is the primary contact |

---

### Alarm Event

Stores alarm settings and schedules.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Alarm type (medication/reminder/custom) |
| title | string | Yes | Alarm title |
| message | string | No | Alarm message |
| time | string | Yes | Alarm time in HH:MM format |
| days_of_week | array | Yes | Days of week (0=Sunday, 1=Monday, etc.) |
| active | boolean | Yes | Whether alarm is enabled |
| reference_id | string | No | Reference to related event (e.g., med_schedule) |

---

### Notification Event

Stores notification records.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| alarm_id | string | Yes | Reference to alarm event |
| title | string | No | Notification title |
| message | string | No | Notification message |
| type | string | No | Notification type |
| read | boolean | Yes | Whether notification is read |
| created_at | timestamp | Yes | Notification creation time |

---

### ChatMessage Event

Stores AI chat messages.

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

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_message | string | Yes | User's message |
| ai_response | string | No | AI's response |
| context | object | No | Chat context (metadata) |
| timestamp | timestamp | Yes | Message timestamp |

---

## LocusGraph SDK API Methods

### store_event()

Stores a new health event in LocusGraph.

**Parameters**:
- `event_kind` (str): Event type (e.g., "fact", "action", "decision")
- `context_id` (str): Unique identifier for the event (e.g., "vitals:<id>", "food:<id>")
- `payload` (dict): Event data
- `related_to` (list, optional): Related event IDs for linking

**Example**:
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
```

---

### retrieve_context()

Retrieves events by type and filters.

**Parameters**:
- `context_type` (str): Event type to retrieve (e.g., "vitals", "food")
- `user_id` (str): User identifier
- `filters` (dict, optional): Additional filters (e.g., `{"min_date": "2026-01-01"}`)

**Example**:
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
```

---

### generate_insights()

Generates health insights from stored events.

**Parameters**:
- `user_id` (str): User identifier
- `query` (dict, optional): Query parameters

**Example**:
```python
# Get health insights
insights = await locusgraph_service.generate_insights(
    user_id="user_123",
    query={"topic": "heart_health", "days": 30}
)
```

---

### update_event()

Updates an existing event.

**Parameters**:
- `context_id` (str): Event identifier to update
- `updates` (dict): Fields to update

**Example**:
```python
# Update vitals
await locusgraph_service.update_event(
    context_id="vitals:12345",
    updates={"heart_rate": 75, "logged_at": "2026-02-18T09:00:00Z"}
)
```

---

### delete_event()

Deletes an event.

**Parameters**:
- `context_id` (str): Event identifier to delete

**Example**:
```python
# Delete a food log
await locusgraph_service.delete_event("food:67890")
```

---

## LangGraph Tools

The LocusGraph SDK is wrapped as LangGraph tools for workflow integration:

**Available Tools**:
1. `store_health_event` - Wraps `store_event()` for health data
2. `retrieve_health_context` - Wraps `retrieve_context()` for data retrieval
3. `generate_health_insights` - Wraps `generate_insights()` for analysis
4. `get_user_profile` - Fetches profile via LocusGraph SDK
5. `get_recent_vitals` - Fetches recent vitals via LocusGraph SDK
6. `get_medication_schedule` - Fetches active medications via LocusGraph SDK

**Example Workflow Integration**:
```python
# In LangGraph workflow
from src.workflows.tools import store_health_event, retrieve_health_context

async def health_tracking_node(state):
    # Store vitals
    await store_health_event(
        context_id="vitals:" + state["vitals_id"],
        payload=state["vitals_data"]
    )

    # Retrieve recent health data
    health_data = await retrieve_health_context(
        context_type="vitals",
        user_id=state["user_id"],
        filters={"min_date": "2026-02-01"}
    )

    return state
```

---

## Data Flow

### Health Monitoring Flow

```
1. Client → POST /health/vitals
   {
     heart_rate, blood_pressure, temperature, weight_kg
   }

2. Server → Validate inputs
           → Call LocusGraph SDK store_event() with context_id="vitals:<id>"
           → Store vitals in LocusGraph
           → Return created record

3. Client → GET /health/recommendations
           → Call LocusGraph SDK retrieve_context() for user's vitals
           → Call LocusGraph SDK generate_insights() for analysis
           → Receive health recommendations
```

### Medication Management Flow

```
1. Client → POST /medication/schedules
   {
     name, dosage, frequency, time_of_day, days_of_week
   }

2. Server → Validate inputs
           → Call LocusGraph SDK store_event() with context_id="med_schedule:<id>"
           → Create medication event
           → Return created schedule

3. Client → POST /medication/logs
   {
     medication_id, dosage, notes
   }

4. Server → Validate inputs
           → Call LocusGraph SDK store_event() with context_id="medication:<id>"
           → Update schedule completion
           → Return created log
```

### Food Logging Flow

```
1. Client → POST /tracking/food
   {
     description, calories, meal_type
   }

2. Server → Validate inputs
           → Call LocusGraph SDK store_event() with context_id="food:<id>"
           → Store food log
           → Return created record
```

### Chat Flow

```
1. Client → POST /chat/message
   {
     message, context: {topic: "health"}
   }

2. Server → Process message
           → Call LocusGraph SDK retrieve_context() for user's health data
           → Generate prompt for LLM
           → Send to Sarvam AI API

3. Server → Receive LLM response
           → Format response
           → Call LocusGraph SDK store_event() with context_id="chat:<id>"
           → Store chat message
           → Return response to client
```

---

## SQLite Health Tables (Deprecated)

**Note**: The following sections document the old SQLite health tables for migration reference only. All new code should use LocusGraph SDK event schemas.

### Deprecated: Health Vitals Table

```sql
CREATE TABLE health_vitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    heart_rate INTEGER,
    blood_pressure VARCHAR(50),
    temperature DECIMAL(3,1),
    weight_kg DECIMAL(5,2),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Deprecated: Food Logs Table

```sql
CREATE TABLE food_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    description VARCHAR(255) NOT NULL,
    calories INTEGER,
    protein_g INTEGER,
    carbs_g INTEGER,
    fat_g INTEGER,
    meal_type VARCHAR(50),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Deprecated: Medication Schedules Table

```sql
CREATE TABLE medication_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    times VARCHAR(255),
    days VARCHAR(255),
    quantity INTEGER
);
```

---

## Database Migration Strategy

### From SQLite to LocusGraph

**Migration Steps**:

1. **Backup Data**: Export all health data from SQLite before migration
2. **Create LocusGraph Events**: Convert SQLite rows to LocusGraph events
3. **Verify Data Integrity**: Ensure all data migrated successfully
4. **Update Application**: Modify code to use LocusGraph SDK instead of SQLite
5. **Clean Up**: Remove old SQLite health tables after successful migration

**Migration Script Example**:

```python
async def migrate_sqlite_to_locusgraph(user_id):
    """Migrate all health data from SQLite to LocusGraph"""

    # 1. Fetch all health vitals from SQLite
    vitals = await sqlite_service.fetch_all("SELECT * FROM health_vitals WHERE user_id = ?", [user_id])

    # 2. Store each vitals record in LocusGraph
    for vitals_record in vitals:
        await locusgraph_service.store_event(
            event_kind="fact",
            context_id=f"vitals:{vitals_record['id']}",
            payload=vitals_record
        )

    # 3. Fetch and migrate other health data (food, exercise, etc.)
    # Repeat for each entity type

    # 4. Remove old SQLite health tables (optional)
    # await sqlite_service.execute("DROP TABLE IF EXISTS health_vitals")
```

---

## Indexing Strategy

### SQLite Indexes (Auth Only)

**Primary Indexes**:
- All tables have a primary key index on their UUID field

**Foreign Key Indexes**:
- All foreign key columns are indexed for efficient joins
- Example: `user_id` columns in refresh_tokens are indexed

### LocusGraph Indexing

**Context IDs**:
- All events use specific `context_id` formats (e.g., `vitals:<id>`, `food:<id>`)
- Context IDs are used for efficient retrieval and updates
- Related events use `related_to` links for data relationships

**Query Patterns**:
- Retrieve by context type and user_id
- Filter by date ranges (logged_at field)
- Filter by status flags (active, completed, read)
- Retrieve related events via `related_to` links

---

## Performance Considerations

### LocusGraph Performance

**Optimizations**:
- Context-based retrieval for fast data access
- Event linking via `related_to` for relationship queries
- Date-indexed fields for time-based queries
- Efficient bulk operations for multiple events

**Best Practices**:
- Use context_id prefixes for type filtering
- Include timestamps for date range queries
- Use related_to links for event relationships
- Batch multiple store_event() calls

### SQLite Performance

**Optimizations**:
- Indexes on frequently queried columns
- Connection pooling
- Prepared statements
- Async operations

---

## Data Retention Policies

### Recommended Retention Periods

| Entity Type | Retention Period | Reason |
|-------------|------------------|--------|
| Profile Event | Indefinite | User profile data |
| Vitals Events | 1 year | Historical health tracking |
| Food Logs | 90 days | Recent dietary tracking |
| Medication Logs | 2 years | Compliance and refill tracking |
| Exercise Logs | 90 days | Recent activity tracking |
| Mood Logs | 90 days | Recent emotional tracking |
| Sleep Logs | 90 days | Recent sleep tracking |
| Water Logs | 30 days | Recent hydration tracking |
| Meditation Logs | 1 year | Wellness progress tracking |
| Chat Messages | 90 days | User interaction history |
| Notifications | 30 days (read), 7 days (unread) | Notification management |
| Alarms | Keep indefinitely | User preferences |

### Cleanup Strategy (LocusGraph)

**LocusGraph SDK Cleanup**:

```python
async def cleanup_old_events(context_type, retention_days):
    """Delete events older than retention_days"""

    from datetime import datetime, timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    # Retrieve events older than cutoff
    old_events = await locusgraph_service.retrieve_context(
        context_type=context_type,
        user_id="*",
        filters={"logged_at": {"lt": cutoff_date.isoformat()}}
    )

    # Delete each event
    for event in old_events:
        await locusgraph_service.delete_event(event["context_id"])
```

---

## Appendix: SQL Scripts

### SQLite Auth Database Setup

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
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Refresh Tokens Table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

---

## Related Documentation

- [Architecture Documentation](./architecture.md) - Detailed system architecture
- [Deployment Documentation](./deployment.md) - Deployment and infrastructure
- [Quick Reference](./quick_reference.md) - Quick API reference
- [Workflows Documentation](./workflows.md) - Workflow execution patterns
- [API Documentation](./api_documentation.md) - REST API endpoints
