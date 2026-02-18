# API Documentation

## Dual-Database Architecture

The Podd Health Assistant backend uses a dual-database architecture:

### Databases

**1. SQLite (podd_auth.db) - Authentication Only**
- Stores only authentication-related data
- Tables: `Users`, `RefreshTokens`
- Used for JWT token management and user credentials
- Created automatically on first startup

**2. LocusGraph SDK - Health Data Store**
- Stores all health and personal data as structured events
- Event types: Profile, FoodLog, Vitals, Medication, MedicationSchedule, WaterLog, SleepLog, ExerciseLog, MoodLog, MeditationSession, MeditationLog, Appointment, EmergencyContact, Alarm, Notification, ChatMessage
- Each event uses a specific `context_id` format for efficient retrieval
- Accessed via LocusGraph SDK integration

### Data Flow

```
Client Request → API Endpoint → LocusGraph SDK → Store/Retrieve Events
                                                ↓
                                          SQLite (Auth Only)
```

**Health Data Storage:**
- Endpoints create events using `store_event()` from LocusGraph SDK
- Events use `event_kind` (fact, action, decision) and `context_id` prefixes
- Related events linked using `related_to` parameter
- Retrieved using `retrieve_context()` with filters

**Authentication Flow:**
- JWT tokens managed through SQLite database
- Token validation, refresh, and expiration handled by auth services
- No health data in SQLite - all stored in LocusGraph

## Base URL

All API requests should use the base URL: `http://localhost:8000/api`

## Authentication

Most endpoints require authentication. Include the JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

## Rate Limiting

Rate limits are applied to prevent abuse. Default limit: 100 requests per minute per user.

## Common Response Format

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Detailed error message",
    "details": { ... }
  }
}
```

## LocusGraph SDK Integration

### Context ID Formats

All health events use `context_id` prefixes for efficient retrieval:

```python
# Profile
profile:<user_id>

# Vitals
vitals:<id>

# Food Logs
food:<id>

# Medication Schedules
med_schedule:<id>

# Medication Logs
med_log:<id>

# Water Logs
water:<id>

# Sleep Logs
sleep:<id>

# Exercise Logs
exercise:<id>

# Mood Logs
mood:<id>

# Meditation Sessions
meditation_session:<id>

# Meditation Logs
meditation_log:<id>

# Appointments
appointment:<id>

# Emergency Contacts
emergency_contact:<id>

# Alarms
alarm:<id>

# Notifications
notification:<id>

# Chat Messages
chat:<id>
```

### Event Payload Structure

Events follow this structure:
```python
{
  "event_kind": "fact",  # or "action", "decision"
  "context_id": "vitals:<id>",
  "user_id": "<user_id>",
  "payload": {
    "heart_rate": 75,
    "blood_pressure": "125/82",
    "recorded_at": "2026-02-18T10:30:00Z"
  },
  "related_to": [],  # List of related context_ids
  "source": "api"  # or "web", "voice", "app"
}
```

### LocusGraph SDK Methods

**Store Event:**
```python
await store_event(
    event_kind="fact",
    context_id="vitals:<id>",
    payload={...},
    related_to=[],
    source="api"
)
```

**Retrieve Context:**
```python
events = await retrieve_context(
    context_type="vitals",
    user_id="<user_id>",
    filters={"recorded_after": "2026-02-01"}
)
```

**Generate Insights:**
```python
insights = await generate_insights(
    user_id="<user_id>",
    query={"context_type": "vitals", "metrics": ["heart_rate"]}
)
```

**Update Event:**
```python
await update_event(
    context_id="vitals:<id>",
    updates={"heart_rate": 80}
)
```

**Delete Event:**
```python
await delete_event(context_id="vitals:<id>")
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
}
```

#### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh_token"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "new_jwt_token",
    "refresh_token": "new_refresh_token"
  }
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

### Health Monitoring

#### Get Health Metrics
```http
GET /health
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "vitals": [
      {
        "id": "uuid",
        "heart_rate": 72,
        "blood_pressure": "120/80",
        "temperature": 98.6,
        "oxygen_level": 98,
        "recorded_at": "2026-02-18T10:00:00Z",
        "context_id": "vitals:abc-123"
      }
    ],
    "last_updated": "2026-02-18T10:00:00Z"
  }
}
```

**Implementation:**
- Retrieves all vitals from LocusGraph using `retrieve_context()`
- Filters by user_id from JWT token
- Returns formatted JSON response

#### Create Vital Signs
```http
POST /health/vitals
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "heart_rate": 75,
  "blood_pressure": "125/82",
  "temperature": 98.7,
  "oxygen_level": 97
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "heart_rate": 75,
    "blood_pressure": "125/82",
    "temperature": 98.7,
    "oxygen_level": 97,
    "recorded_at": "2026-02-18T10:30:00Z",
    "context_id": "vitals:xyz-456"
  }
}
```

**Implementation:**
- Validates input data
- Generates unique ID
- Calls `store_event()` with `context_id=vitals:<id>`, `event_kind=fact`
- Stores in LocusGraph SDK
- Returns created event

#### Get Health History
```http
GET /health/history?days=30&limit=100
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `days`: Number of days to retrieve (default: 30)
- `limit`: Maximum number of records (default: 100)

**Response:**
```json
{
  "status": "success",
  "data": {
    "total": 150,
    "records": [
      {
        "id": "uuid",
        "heart_rate": 72,
        "blood_pressure": "120/80",
        "temperature": 98.6,
        "oxygen_level": 98,
        "recorded_at": "2026-02-18T10:00:00Z",
        "context_id": "vitals:abc-123"
      }
    ]
  }
}
```

**Implementation:**
- Calls `retrieve_context(context_type="vitals", filters={...})`
- Filters by date range (days parameter)
- Returns paginated results

#### Get Health Recommendations
```http
GET /health/recommendations
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "type": "activity",
        "message": "Consider a 30-minute walk today",
        "priority": "medium",
        "category": "exercise"
      },
      {
        "type": "hydration",
        "message": "Drink an extra glass of water",
        "priority": "high",
        "category": "health"
      }
    ]
  }
}
```

**Implementation:**
- Calls `generate_insights(user_id, query={"context_type": "vitals"})`
- Uses AI to analyze stored health data
- Returns personalized recommendations

### Medication Management

#### Get Medication Schedules
```http
GET /medication/schedules
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "name": "Aspirin",
      "dosage": "100mg",
      "frequency": "daily",
      "time": "08:00",
      "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
      "refill_date": "2026-03-01",
      "quantity": 30,
      "total_doses": 210,
      "completed_doses": 45,
      "context_id": "med_schedule:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves all medication schedules from LocusGraph
- Uses `retrieve_context(context_type="med_schedule", user_id=...)`
- Calculates dose completion statistics

#### Create Medication Schedule
```http
POST /medication/schedules
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Metformin",
  "dosage": "500mg",
  "frequency": "twice_daily",
  "times": ["08:00", "20:00"],
  "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
  "quantity": 60,
  "prescription_date": "2026-01-15"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "Metformin",
    "dosage": "500mg",
    "frequency": "twice_daily",
    "times": ["08:00", "20:00"],
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    "quantity": 60,
    "prescription_date": "2026-01-15",
    "refill_date": "2026-04-15",
    "context_id": "med_schedule:xyz-456"
  }
}
```

**Implementation:**
- Validates medication data
- Calls `store_event()` with `context_id=med_schedule:<id>`, `event_kind=decision`
- Stores in LocusGraph SDK

#### Get Medication Logs
```http
GET /medication/logs?days=30
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `days`: Number of days to retrieve (default: 30)

**Response:**
```json
{
  "status": "success",
  "data": {
    "total": 60,
    "logs": [
      {
        "id": "uuid",
        "schedule_id": "uuid",
        "medication_name": "Aspirin",
        "dosage": "100mg",
        "taken_at": "2026-02-18T08:00:00Z",
        "status": "taken",
        "context_id": "med_log:abc-123"
      }
    ]
  }
}
```

**Implementation:**
- Retrieves medication logs from LocusGraph
- Links to schedules using `related_to` parameter
- Filters by date range

#### Create Medication Log
```http
POST /medication/logs
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "schedule_id": "uuid",
  "dosage": "100mg",
  "notes": "With food"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "schedule_id": "uuid",
    "medication_name": "Aspirin",
    "dosage": "100mg",
    "taken_at": "2026-02-18T08:05:00Z",
    "status": "taken",
    "notes": "With food",
    "context_id": "med_log:xyz-456"
  }
}
```

**Implementation:**
- Validates log data
- Links to schedule using `related_to=[schedule_id]`
- Calls `store_event()` with `event_kind=action`
- Stores in LocusGraph SDK

### Appointments

#### Get Appointments
```http
GET /appointments?date_from=2026-02-18&date_to=2026-02-28&status=upcoming
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `date_from`: Start date (default: today)
- `date_to`: End date (default: +30 days)
- `status`: Filter by status (upcoming, completed, cancelled)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "title": "Regular Checkup",
      "doctor_name": "Dr. Smith",
      "specialty": "General Practice",
      "date": "2026-02-20T10:00:00Z",
      "duration_minutes": 30,
      "status": "upcoming",
      "notes": "Annual checkup",
      "location": "123 Medical Center, Room 101",
      "context_id": "appointment:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves appointments from LocusGraph
- Uses `retrieve_context(context_type="appointment", user_id=...)`
- Filters by date range and status

#### Create Appointment
```http
POST /appointments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Follow-up Consultation",
  "doctor_name": "Dr. Johnson",
  "specialty": "Cardiology",
  "date": "2026-02-25T14:00:00Z",
  "duration_minutes": 45,
  "notes": "Post-surgery follow-up"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Follow-up Consultation",
    "doctor_name": "Dr. Johnson",
    "specialty": "Cardiology",
    "date": "2026-02-25T14:00:00Z",
    "duration_minutes": 45,
    "status": "upcoming",
    "notes": "Post-surgery follow-up",
    "location": null,
    "context_id": "appointment:xyz-456"
  }
}
```

**Implementation:**
- Validates appointment data
- Calls `store_event()` with `context_id=appointment:<id>`, `event_kind=decision`
- Stores in LocusGraph SDK

#### Update Appointment
```http
PUT /appointments/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Follow-up Consultation",
  "date": "2026-02-26T14:00:00Z",
  "status": "completed"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Follow-up Consultation",
    "date": "2026-02-26T14:00:00Z",
    "status": "completed",
    "context_id": "appointment:abc-123"
  }
}
```

**Implementation:**
- Retrieves existing event from LocusGraph
- Calls `update_event()` with updated data
- Saves changes back to LocusGraph

#### Cancel Appointment
```http
DELETE /appointments/{id}
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "message": "Appointment cancelled successfully"
}
```

**Implementation:**
- Calls `delete_event()` with appointment context_id
- Removes from LocusGraph SDK

### Emergency

#### Get Emergency Contacts
```http
GET /emergency/contacts
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "name": "John Smith",
      "relationship": "Spouse",
      "phone": "+1234567890",
      "email": "john@example.com",
      "is_primary": true,
      "notes": "Emergency contact for medical emergencies",
      "context_id": "emergency_contact:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves emergency contacts from LocusGraph
- Uses `retrieve_context(context_type="emergency_contact", user_id=...)`

#### Create Emergency Contact
```http
POST /emergency/contacts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Jane Doe",
  "relationship": "Sibling",
  "phone": "+1987654321",
  "email": "jane@example.com",
  "is_primary": false,
  "notes": "Call in case of emergency"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "Jane Doe",
    "relationship": "Sibling",
    "phone": "+1987654321",
    "email": "jane@example.com",
    "is_primary": false,
    "notes": "Call in case of emergency",
    "context_id": "emergency_contact:xyz-456"
  }
}
```

**Implementation:**
- Validates emergency contact data
- Calls `store_event()` with `context_id=emergency_contact:<id>`, `event_kind=decision`
- Stores in LocusGraph SDK

#### Create Emergency Alert
```http
POST /emergency/alert
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "medical",
  "severity": "high",
  "description": "Experiencing chest pain",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address": "123 Main St, New York, NY"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "type": "medical",
    "severity": "high",
    "description": "Experiencing chest pain",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "address": "123 Main St, New York, NY"
    },
    "created_at": "2026-02-18T10:30:00Z",
    "status": "pending",
    "context_id": "emergency_alert:abc-123"
  }
}
```

**Implementation:**
- Creates emergency alert event in LocusGraph
- Calls `store_event()` with `event_kind=action`
- Notifies emergency contacts via configured channels

### Voice Interface

#### Process Voice Command
```http
POST /voice/command
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "command": "I want to log my lunch",
  "context": {
    "food_type": "lunch",
    "items": ["sandwich", "apple", "juice"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "processed": true,
    "action": "log_food",
    "result": {
      "food_type": "lunch",
      "items": ["sandwich", "apple", "juice"],
      "logged_at": "2026-02-18T12:00:00Z",
      "context_id": "food:xyz-456"
    }
  }
}
```

**Implementation:**
- Processes voice command through Sarvam AI STT/TTS
- Extracts intent and entities
- Calls appropriate LocusGraph SDK method (e.g., `store_event()` for food logs)
- Returns confirmation with context_id

#### Get Voice Synthesis
```http
GET /voice/synthesize?text=Hello+World
Authorization: Bearer <access_token>
```

**Response:** Binary audio data

**Implementation:**
- Uses Sarvam AI TTS API
- Returns synthesized speech as audio bytes

### Meditation

#### Get Meditation Sessions
```http
GET /meditation/sessions
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "title": "Morning Meditation",
      "duration_minutes": 15,
      "date": "2026-02-18T07:00:00Z",
      "completed": true,
      "notes": "Good session",
      "context_id": "meditation_session:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves meditation sessions from LocusGraph
- Uses `retrieve_context(context_type="meditation_session", user_id=...)`

#### Create Meditation Session
```http
POST /meditation/sessions
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Evening Relaxation",
  "duration_minutes": 20
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Evening Relaxation",
    "duration_minutes": 20,
    "date": "2026-02-18T20:00:00Z",
    "completed": false,
    "notes": null,
    "context_id": "meditation_session:xyz-456"
  }
}
```

**Implementation:**
- Validates session data
- Calls `store_event()` with `context_id=meditation_session:<id>`, `event_kind=decision`
- Stores in LocusGraph SDK

#### Get Meditation History
```http
GET /meditation/history?days=90
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total": 120,
    "sessions": [
      {
        "id": "uuid",
        "title": "Morning Meditation",
        "duration_minutes": 15,
        "date": "2026-02-18T07:00:00Z",
        "completed": true,
        "context_id": "meditation_session:abc-123"
      }
    ]
  }
}
```

**Implementation:**
- Retrieves meditation history from LocusGraph
- Filters by date range
- Returns paginated results

### Activity Tracking

#### Get Food Logs
```http
GET /tracking/food?date=2026-02-18
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "food_name": "Oatmeal with berries",
      "calories": 350,
      "protein": 12,
      "carbs": 65,
      "fat": 6,
      "logged_at": "2026-02-18T08:00:00Z",
      "context_id": "food:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves food logs from LocusGraph
- Uses `retrieve_context(context_type="food", user_id=...)`
- Filters by date

#### Create Food Log
```http
POST /tracking/food
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "food_name": "Grilled chicken salad",
  "calories": 450,
  "protein": 40,
  "carbs": 15,
  "fat": 25
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "food_name": "Grilled chicken salad",
    "calories": 450,
    "protein": 40,
    "carbs": 15,
    "fat": 25,
    "logged_at": "2026-02-18T12:30:00Z",
    "context_id": "food:xyz-456"
  }
}
```

**Implementation:**
- Validates food data
- Calls `store_event()` with `context_id=food:<id>`, `event_kind=fact`
- Stores in LocusGraph SDK

#### Get Exercise Logs
```http
GET /tracking/exercise?date=2026-02-18
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "exercise_name": "Running",
      "duration_minutes": 30,
      "calories_burned": 300,
      "distance_km": 5,
      "logged_at": "2026-02-18T07:00:00Z",
      "context_id": "exercise:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves exercise logs from LocusGraph
- Uses `retrieve_context(context_type="exercise", user_id=...)`
- Filters by date

#### Create Exercise Log
```http
POST /tracking/exercise
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "exercise_name": "Yoga",
  "duration_minutes": 45,
  "calories_burned": 150
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "exercise_name": "Yoga",
    "duration_minutes": 45,
    "calories_burned": 150,
    "logged_at": "2026-02-18T18:00:00Z",
    "context_id": "exercise:xyz-456"
  }
}
```

**Implementation:**
- Validates exercise data
- Calls `store_event()` with `context_id=exercise:<id>`, `event_kind=fact`
- Stores in LocusGraph SDK

#### Get Mood Logs
```http
GET /tracking/mood?days=7
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total": 7,
    "logs": [
      {
        "id": "uuid",
        "mood": "happy",
        "score": 8,
        "notes": "Feeling great today",
        "logged_at": "2026-02-18T09:00:00Z",
        "context_id": "mood:abc-123"
      }
    ]
  }
}
```

**Implementation:**
- Retrieves mood logs from LocusGraph
- Uses `retrieve_context(context_type="mood", user_id=...)`
- Filters by date range

#### Create Mood Log
```http
POST /tracking/mood
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "mood": "neutral",
  "score": 5,
  "notes": "Average day"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "mood": "neutral",
    "score": 5,
    "notes": "Average day",
    "logged_at": "2026-02-18T17:00:00Z",
    "context_id": "mood:xyz-456"
  }
}
```

**Implementation:**
- Validates mood data
- Calls `store_event()` with `context_id=mood:<id>`, `event_kind=fact`
- Stores in LocusGraph SDK

#### Get Sleep Logs
```http
GET /tracking/sleep?date=2026-02-18
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "sleep_duration_hours": 7.5,
      "sleep_quality": 8,
      "bedtime": "2026-02-18T22:30:00Z",
      "wake_time": "2026-02-19T06:00:00Z",
      "logged_at": "2026-02-19T06:15:00Z",
      "context_id": "sleep:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves sleep logs from LocusGraph
- Uses `retrieve_context(context_type="sleep", user_id=...)`
- Filters by date

#### Create Sleep Log
```http
POST /tracking/sleep
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "sleep_duration_hours": 8,
  "sleep_quality": 9,
  "bedtime": "2026-02-18T23:00:00Z",
  "wake_time": "2026-02-19T07:00:00Z"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "sleep_duration_hours": 8,
    "sleep_quality": 9,
    "bedtime": "2026-02-18T23:00:00Z",
    "wake_time": "2026-02-19T07:00:00Z",
    "logged_at": "2026-02-19T07:15:00Z",
    "context_id": "sleep:xyz-456"
  }
}
```

**Implementation:**
- Validates sleep data
- Calls `store_event()` with `context_id=sleep:<id>`, `event_kind=fact`
- Stores in LocusGraph SDK

#### Get Water Logs
```http
GET /tracking/water?date=2026-02-18
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "amount_ml": 250,
      "logged_at": "2026-02-18T09:00:00Z",
      "context_id": "water:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves water logs from LocusGraph
- Uses `retrieve_context(context_type="water", user_id=...)`
- Filters by date

#### Create Water Log
```http
POST /tracking/water
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount_ml": 250
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "amount_ml": 250,
    "logged_at": "2026-02-18T09:00:00Z",
    "context_id": "water:xyz-456"
  }
}
```

**Implementation:**
- Validates water amount
- Calls `store_event()` with `context_id=water:<id>`, `event_kind=fact`
- Stores in LocusGraph SDK

### Chat

#### Send Chat Message
```http
POST /chat/message
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "What can you tell me about heart health?",
  "context": {
    "topic": "heart_health",
    "query_type": "information"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "message_id": "uuid",
    "response": "Heart health is important for overall wellness...",
    "context": {
      "topic": "heart_health",
      "query_type": "information"
    },
    "timestamp": "2026-02-18T14:30:00Z",
    "context_id": "chat:abc-123"
  }
}
```

**Implementation:**
- Creates chat message event in LocusGraph
- Calls `store_event()` with `context_id=chat:<id>`, `event_kind=fact`
- Generates AI response
- Stores interaction for context

#### Get Chat History
```http
GET /chat/history?limit=50
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit`: Maximum number of messages (default: 50)
- `days`: Number of days to retrieve (default: 30)

**Response:**
```json
{
  "status": "success",
  "data": {
    "total": 150,
    "messages": [
      {
        "id": "uuid",
        "message": "What can you tell me about heart health?",
        "response": "Heart health is important for overall wellness...",
        "timestamp": "2026-02-18T14:30:00Z",
        "context_id": "chat:xyz-456"
      }
    ]
  }
}
```

**Implementation:**
- Retrieves chat history from LocusGraph
- Uses `retrieve_context(context_type="chat", user_id=...)`
- Filters by date range
- Returns chronological messages

### Profile

#### Get Profile
```http
GET /profile
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "age": 35,
    "gender": "male",
    "height": 175,
    "weight": 70,
    "blood_type": "A+",
    "allergies": ["penicillin"],
    "medical_conditions": ["asthma"],
    "emergency_contact_id": "uuid",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-02-01T00:00:00Z",
    "context_id": "profile:abc-123"
  }
}
```

**Implementation:**
- Retrieves user profile from LocusGraph
- Uses `retrieve_context(context_type="profile", user_id=...)`

#### Update Profile
```http
PUT /profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "John Smith",
  "age": 36,
  "height": 180,
  "weight": 75,
  "blood_type": "A+",
  "allergies": ["penicillin", "latex"],
  "medical_conditions": ["asthma"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "John Smith",
    "age": 36,
    "height": 180,
    "weight": 75,
    "blood_type": "A+",
    "allergies": ["penicillin", "latex"],
    "medical_conditions": ["asthma"],
    "updated_at": "2026-02-18T15:00:00Z",
    "context_id": "profile:xyz-456"
  }
}
```

**Implementation:**
- Retrieves existing profile from LocusGraph
- Calls `update_event()` with updated data
- Saves changes back to LocusGraph

### Alarms

#### Get Alarms
```http
GET /alarms
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "title": "Morning Medication",
      "time": "08:00",
      "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
      "enabled": true,
      "medication_name": "Aspirin",
      "completed": false,
      "sound": "gentle",
      "context_id": "alarm:abc-123"
    }
  ]
}
```

**Implementation:**
- Retrieves alarms from LocusGraph
- Uses `retrieve_context(context_type="alarm", user_id=...)`

#### Create Alarm
```http
POST /alarms
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Evening Walk",
  "time": "19:00",
  "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
  "enabled": true,
  "sound": "upbeat"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Evening Walk",
    "time": "19:00",
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "enabled": true,
    "sound": "upbeat",
    "completed": false,
    "medication_name": null,
    "context_id": "alarm:xyz-456"
  }
}
```

**Implementation:**
- Validates alarm data
- Calls `store_event()` with `context_id=alarm:<id>`, `event_kind=decision`
- Stores in LocusGraph SDK

#### Update Alarm
```http
PUT /alarms/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Morning Medication",
  "time": "07:30",
  "enabled": true
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Morning Medication",
    "time": "07:30",
    "enabled": true,
    "completed": false,
    "context_id": "alarm:abc-123"
  }
}
```

**Implementation:**
- Retrieves existing alarm from LocusGraph
- Calls `update_event()` with updated data
- Saves changes back to LocusGraph

#### Delete Alarm
```http
DELETE /alarms/{id}
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "message": "Alarm deleted successfully"
}
```

**Implementation:**
- Calls `delete_event()` with alarm context_id
- Removes from LocusGraph SDK

#### Get Notifications
```http
GET /alarms/notifications
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "title": "Morning Medication",
      "message": "Time to take your Aspirin",
      "time": "2026-02-18T08:00:00Z",
      "read": false,
      "alarm_id": "uuid"
    }
  ]
}
```

**Implementation:**
- Retrieves notifications from LocusGraph
- Uses `retrieve_context(context_type="notification", user_id=...)`

#### Mark Notification Read
```http
POST /alarms/notifications/{id}/read
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "read": true
  }
}
```

**Implementation:**
- Retrieves notification from LocusGraph
- Calls `update_event()` to mark as read
- Saves changes back to LocusGraph

## Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_FAILED` | Invalid or missing authentication token |
| `INVALID_CREDENTIALS` | Invalid email or password |
| `USER_EXISTS` | Email already registered |
| `USER_NOT_FOUND` | User not found |
| `INVALID_TOKEN` | Invalid or expired token |
| `FORBIDDEN` | Insufficient permissions |
| `VALIDATION_ERROR` | Request validation failed |
| `INTERNAL_ERROR` | Server error |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `NOT_FOUND` | Resource not found |

## WebSockets

### Voice Stream WebSocket

Connect to: `ws://localhost:8000/api/voice/stream`

**Client → Server:**
```json
{
  "type": "start",
  "session_id": "uuid"
}
```

**Server → Client:**
```json
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio"
}
```

## WebSocket Events

### Notification Events

**Server → Client:**
```json
{
  "type": "notification",
  "data": {
    "title": "Morning Medication",
    "message": "Time to take your Aspirin",
    "timestamp": "2026-02-18T08:00:00Z"
  }
}
```

### Appointment Events

**Server → Client:**
```json
{
  "type": "appointment_reminder",
  "data": {
    "appointment_id": "uuid",
    "title": "Follow-up Consultation",
    "date": "2026-02-25T14:00:00Z",
    "reminder_minutes": 30
  }
}
```

## Rate Limiting

- Default limit: 100 requests per minute per user
- Different endpoints may have different limits
- Rate limit headers are included in responses:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1705665600
  ```

## LocusGraph Integration Summary

### Event Types and Their Uses

**Profile Events** (`context_id: profile:<id>`):
- Store user profile information
- Updateable endpoint: `/profile`
- Used for personalized recommendations

**Health Vitals** (`context_id: vitals:<id>`):
- Track heart rate, blood pressure, temperature, oxygen levels
- Create via `/health/vitals`
- Retrieve via `/health` and `/health/history`
- Used for health monitoring and recommendations

**Food Logs** (`context_id: food:<id>`):
- Log food intake with nutritional data
- Create via `/tracking/food`
- Retrieve via `/tracking/food`
- Used for nutrition tracking

**Medication**:
- Schedules: `context_id: med_schedule:<id>` - Create via `/medication/schedules`
- Logs: `context_id: med_log:<id>` - Create via `/medication/logs`
- Linked using `related_to` parameter
- Used for medication management

**Water Logs** (`context_id: water:<id>`):
- Log water intake
- Create via `/tracking/water`
- Retrieve via `/tracking/water`
- Used for hydration tracking

**Sleep Logs** (`context_id: sleep:<id>`):
- Log sleep duration and quality
- Create via `/tracking/sleep`
- Retrieve via `/tracking/sleep`
- Used for sleep tracking

**Exercise Logs** (`context_id: exercise:<id>`):
- Log exercise activities
- Create via `/tracking/exercise`
- Retrieve via `/tracking/exercise`
- Used for activity tracking

**Mood Logs** (`context_id: mood:<id>`):
- Log mood and emotional state
- Create via `/tracking/mood`
- Retrieve via `/tracking/mood`
- Used for mental health tracking

**Meditation**:
- Sessions: `context_id: meditation_session:<id>` - Create via `/meditation/sessions`
- Logs: `context_id: meditation_log:<id>` - Create via `/meditation/sessions`
- Used for meditation tracking

**Appointments** (`context_id: appointment:<id>`):
- Create via `/appointments`
- Retrieve via `/appointments`
- Used for appointment management

**Emergency Contacts** (`context_id: emergency_contact:<id>`):
- Create via `/emergency/contacts`
- Retrieve via `/emergency/contacts`
- Used for emergency contact management

**Alarms** (`context_id: alarm:<id>`):
- Create via `/alarms`
- Retrieve via `/alarms`
- Used for alarm management

**Notifications** (`context_id: notification:<id>`):
- Created automatically by alarm triggers
- Retrieved via `/alarms/notifications`
- Used for notification management

**Chat Messages** (`context_id: chat:<id>`):
- Create via `/chat/message`
- Retrieve via `/chat/history`
- Used for conversation history and context
