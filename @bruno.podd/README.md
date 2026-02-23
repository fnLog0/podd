# Podd Health Assistant API - Bruno Collection Documentation

Complete guide for using the Bruno API collection to test the Podd Health Assistant backend.

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Collection Structure](#collection-structure)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Testing Workflows](#testing-workflows)
- [Response Examples](#response-examples)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Installation

1. **Install Bruno**: Download from [https://www.usebruno.com/](https://www.usebruno.com/)
   - Available for macOS, Windows, and Linux
   - Free and open-source

2. **Open Collection**: `File > Open Folder` and select `/backend/@bruno.podd`

3. **Verify Setup**: You should see the collection "Podd Health Assistant API" with all folders

---

## ⚡ Quick Start

### 1. Set Up Environment Variables

Create an environment in Bruno (Environments > Create):

```json
{
  "baseUrl": "http://localhost:8000",
  "accessToken": "",
  "refreshToken": "",
  "alarm_id": "",
  "notification_id": "",
  "appointment_id": "",
  "session_id": "",
  "audio_file": "/path/to/test-audio.mp3"
}
```

### 2. Register and Login

```
1. Run: Auth > Register
2. Run: Auth > Login
3. Copy tokens from response
4. Update environment variables
```

### 3. Test Protected Endpoints

Any endpoint in folders other than `Auth` requires the `accessToken` to be set.

---

## 🔧 Environment Setup

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `baseUrl` | API base URL | `http://localhost:8000` |
| `accessToken` | JWT access token | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `refreshToken` | JWT refresh token | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### Optional Variables (for testing specific resources)

| Variable | Description | Source |
|----------|-------------|--------|
| `alarm_id` | ID of an existing alarm | From Create Alarm response |
| `notification_id` | ID of a notification | From Get Notifications response |
| `appointment_id` | ID of an appointment | From Create Appointment response |
| `session_id` | ID of a meditation session | From Get Sessions response |
| `audio_file` | Path to audio file | For voice endpoints |

---

## 📁 Collection Structure

```
@bruno.podd/
├── Auth/                   # Authentication endpoints
│   ├── Register.bru
│   ├── Login.bru
│   ├── Refresh.bru
│   ├── Logout.bru
│   └── Get Current User.bru
│
├── Health/                 # Health tracking endpoints
│   ├── Create Food Log.bru
│   ├── Get Food Logs.bru
│   ├── Create Vitals.bru
│   ├── Get Vitals.bru
│   ├── Get Insights.bru
│   └── Get Recommendations.bru
│
├── Tracking/               # Activity tracking
│   ├── Create Water Log.bru
│   ├── Get Water History.bru
│   ├── Create Sleep Log.bru
│   ├── Get Sleep History.bru
│   ├── Create Exercise Log.bru
│   ├── Get Exercise History.bru
│   ├── Create Mood Log.bru
│   └── Get Mood History.bru
│
├── Medication/             # Medication management
│   ├── Create Medication Log.bru
│   ├── Create Medication Schedule.bru
│   └── Get Medication Schedule.bru
│
├── Meditation/             # Meditation sessions
│   ├── Get Sessions.bru
│   ├── Get Session.bru
│   ├── Create Meditation Log.bru
│   └── Get History.bru
│
├── Alarms/                # Alarm & notifications
│   ├── Create Alarm.bru
│   ├── Get Alarms.bru
│   ├── Update Alarm.bru
│   ├── Delete Alarm.bru
│   ├── Get Notifications.bru
│   └── Mark Notification Read.bru
│
├── Appointments/          # Appointment management
│   ├── Create Appointment.bru
│   ├── Get Appointments.bru
│   └── Update Appointment.bru
│
├── Chat/                 # AI chat assistant
│   ├── Chat.bru
│   ├── Chat - Medication Tracking.bru
│   ├── Chat - Health Query.bru
│   ├── Chat - Recommendation.bru
│   ├── Chat - General Conversation.bru
│   ├── Chat - Hindi Language Support.bru
│   ├── Chat - Voice Channel.bru
│   ├── Chat - Empty Message Validation.bru
│   ├── Get Chat History.bru
│   └── README.md
│
├── Voice/                # Voice interactions
│   ├── Voice Stream.bru
│   ├── Voice Synthesize.bru
│   ├── Voice Conversation.bru
│   └── Voice WebSocket.bru
│
├── Emergency/            # Emergency contacts
│   ├── Create Emergency Contact.bru
│   └── Get Emergency Contacts.bru
│
├── Profile/              # User profile
│   ├── Get Profile.bru
│   └── Update Profile.bru
│
├── bruno.json            # Collection metadata
└── README.md             # This file
```

---

## 🔐 Authentication

### Authentication Flow

1. **Register**: Create a new user account
   ```
   POST /api/auth/register
   ```

2. **Login**: Authenticate and receive tokens
   ```
   POST /api/auth/login
   ```

3. **Update Environment**: Copy tokens to Bruno environment

4. **Use Protected Endpoints**: All subsequent requests include Bearer token

5. **Refresh**: Get new access token when expired
   ```
   POST /api/auth/refresh
   ```

6. **Logout**: Revoke refresh token
   ```
   POST /api/auth/logout
   ```

### Token Management

The collection uses Bearer authentication:

```
Authorization: Bearer {{accessToken}}
```

**Note**: Each request's `auth` section is configured automatically. Just ensure `accessToken` is set in your environment.

---

## 📡 API Endpoints

### Authentication (`/api/auth`)

#### POST `/api/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

**Response:** `201 Created` with access and refresh tokens

---

#### POST `/api/auth/login`
Authenticate existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

#### POST `/api/auth/refresh`
Refresh expired access token.

**Request Body:**
```json
{
  "refresh_token": "{{refreshToken}}"
}
```

---

#### POST `/api/auth/logout`
Revoke refresh token.

**Request Body:**
```json
{
  "refresh_token": "{{refreshToken}}"
}
```

---

#### GET `/api/auth/me`
Get currently authenticated user info.

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-02-16T00:00:00Z"
}
```

---

### Health (`/api/health`)

#### GET `/api/health/food/logs`
Get user's food logs.

**Query Parameters:**
- `start_date` (optional): Filter logs from this date
- `end_date` (optional): Filter logs until this date

**Response:**
```json
{
  "logs": [
    {
      "id": "log_id",
      "meal_type": "breakfast",
      "items": [{"name": "Oatmeal", "calories": 150}],
      "total_calories": 150,
      "logged_at": "2024-02-16T08:00:00Z"
    }
  ]
}
```

---

#### POST `/api/health/food/log`
Create a new food log.

**Request Body:**
```json
{
  "meal_type": "breakfast",
  "items": [
    {
      "name": "Oatmeal",
      "calories": 150
    }
  ],
  "total_calories": 150,
  "logged_at": "2024-02-16T08:00:00Z"
}
```

**Meal types:** `breakfast`, `lunch`, `dinner`, `snack`

---

#### GET `/api/health/vitals`
Get vitals records.

**Response:**
```json
{
  "vitals": [
    {
      "id": "vital_id",
      "heart_rate": 72,
      "blood_pressure_systolic": 120,
      "blood_pressure_diastolic": 80,
      "temperature": 98.6,
      "recorded_at": "2024-02-16T08:00:00Z"
    }
  ]
}
```

---

#### POST `/api/health/vitals`
Create a vitals record.

**Request Body:**
```json
{
  "heart_rate": 72,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "temperature": 98.6,
  "recorded_at": "2024-02-16T08:00:00Z"
}
```

---

#### GET `/api/health/recommendations`
Get AI-generated health recommendations.

**Response:**
```json
{
  "recommendations": [
    {
      "category": "nutrition",
      "title": "Increase Water Intake",
      "description": "Drink at least 8 glasses of water daily",
      "priority": "high"
    }
  ]
}
```

---

#### GET `/api/health/insights`
Get health analytics and insights.

**Response:**
```json
{
  "insights": {
    "average_calories": 1850,
    "average_sleep_hours": 7.5,
    "exercise_frequency": 4,
    "health_score": 85
  }
}
```

---

### Tracking (`/api/tracking`)

#### Water Tracking
```
POST   /api/tracking/water/log          - Log water intake
GET    /api/tracking/water/history      - Get water history
```

**Water Log Request:**
```json
{
  "amount_ml": 250,
  "logged_at": "2024-02-16T08:00:00Z"
}
```

---

#### Sleep Tracking
```
POST   /api/tracking/sleep/log          - Log sleep
GET    /api/tracking/sleep/history      - Get sleep history
```

**Sleep Log Request:**
```json
{
  "hours_slept": 7.5,
  "sleep_quality": "good",
  "bedtime": "2024-02-15T22:00:00Z",
  "wake_time": "2024-02-16T06:30:00Z",
  "logged_at": "2024-02-16T06:30:00Z"
}
```

**Sleep quality:** `poor`, `fair`, `good`, `excellent`

---

#### Exercise Tracking
```
POST   /api/tracking/exercise/log       - Log exercise
GET    /api/tracking/exercise/history   - Get exercise history
```

**Exercise Log Request:**
```json
{
  "exercise_type": "running",
  "duration_minutes": 30,
  "calories_burned": 300,
  "logged_at": "2024-02-16T07:00:00Z"
}
```

**Exercise types:** `running`, `walking`, `cycling`, `swimming`, `weights`, `yoga`, `other`

---

#### Mood Tracking
```
POST   /api/tracking/mood/log           - Log mood
GET    /api/tracking/mood/history       - Get mood history
```

**Mood Log Request:**
```json
{
  "mood": "happy",
  "note": "Had a productive morning",
  "logged_at": "2024-02-16T09:00:00Z"
}
```

**Mood options:** `very_sad`, `sad`, `neutral`, `happy`, `very_happy`

---

### Medication (`/api/medication`)

```
POST   /api/medication/log              - Log medication taken
POST   /api/medication/schedule         - Create medication schedule
GET    /api/medication/schedule         - Get medication schedule
```

**Medication Log Request:**
```json
{
  "medication_name": "Vitamin D",
  "dosage": "1000 IU",
  "logged_at": "2024-02-16T08:00:00Z"
}
```

**Medication Schedule Request:**
```json
{
  "medication_name": "Vitamin D",
  "dosage": "1000 IU",
  "frequency": "daily",
  "time": "08:00",
  "notes": "Take with breakfast"
}
```

---

### Meditation (`/api/meditation`)

```
GET    /api/meditation/sessions         - Get all sessions
GET    /api/meditation/sessions/{id}    - Get specific session
POST   /api/meditation/log              - Log meditation session
GET    /api/meditation/history          - Get meditation history
```

**Meditation Log Request:**
```json
{
  "session_id": "session_id",
  "duration_minutes": 15,
  "completed": true,
  "logged_at": "2024-02-16T07:00:00Z"
}
```

---

### Alarms (`/api/alarms`)

```
POST   /api/alarms                       - Create alarm
GET    /api/alarms                       - Get all alarms
PUT    /api/alarms/{alarm_id}           - Update alarm
DELETE /api/alarms/{alarm_id}           - Delete alarm
GET    /api/notifications               - Get notifications
PUT    /api/notifications/{id}/read     - Mark as read
```

**Create Alarm Request:**
```json
{
  "time": "07:00",
  "label": "Morning Medication",
  "repeat": ["monday", "tuesday", "wednesday", "thursday", "friday"],
  "enabled": true
}
```

**Repeat options:** `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`

---

### Appointments (`/api/appointments`)

```
POST   /api/appointments                 - Create appointment
GET    /api/appointments                 - Get all appointments
PUT    /api/appointments/{id}           - Update appointment
```

**Create Appointment Request:**
```json
{
  "title": "Doctor Checkup",
  "description": "Quarterly checkup with Dr. Smith",
  "datetime": "2024-03-01T10:00:00Z",
  "location": "City Medical Center",
  "reminder_minutes": 60
}
```

---

### Chat (`/api/chat`)

```
POST   /api/chat                         - Send message
GET    /api/chat/history                - Get chat history
```

**Send Message Request:**
```json
{
  "message": "What should I eat for breakfast?",
  "locale": "en-IN",
  "channel": "text"
}
```

**Parameters:**
- `message` (required): User's message (1-1000 characters)
- `locale` (optional): Language preference - `en-IN` or `hi-IN` (default: `en-IN`)
- `channel` (optional): Communication channel - `text` or `voice` (default: `text`)

**Response:**
```json
{
  "response": "Based on your health goals, I recommend oatmeal with berries...",
  "intent": "recommendation",
  "locale": "en-IN"
}
```

**Intent Classification:**
The LangGraph router automatically classifies messages into these intents:
- `food_tracking` - Keywords: khana, roti, chawal, eaten, ate, breakfast, lunch, dinner, food, meal
- `medication` - Keywords: medicine, dawai, tablet, goli, prescription
- `health_query` - Keywords: blood pressure, sugar, bp, weight, symptoms, diagnosis
- `recommendation` - Keywords: suggest, recommend, recipe, kya khau, what should i eat
- `general_chat` - Default for friendly conversation

**Get Chat History Request:**
```
GET /api/chat/history?limit=10
```

**Query Parameters:**
- `limit` (optional): Maximum number of conversations to return (default: 10)

**Response:**
```json
{
  "conversations": [
    {
      "user_text": "I ate roti and chawal for lunch",
      "assistant_text": "Got it! I've logged your food: I ate roti and chawal for lunch",
      "intent": "food_tracking",
      "timestamp": "2024-02-16T12:00:00Z"
    }
  ],
  "total_count": 5
}
```

---

### Voice (`/api/voice`)

```
POST   /api/voice/stream                - Speech-to-text (STT)
POST   /api/voice/synthesize             - Text-to-speech (TTS)
POST   /api/voice/conversation           - Voice conversation
WS     /api/voice/ws                     - WebSocket connection
```

#### Voice Stream (STT)
Submit audio file and get transcription.

**Request:** Multipart form with audio file

**Response:**
```json
{
  "text": "Hello, I need help with my health",
  "confidence": 0.95
}
```

---

#### Voice Synthesize (TTS)
Convert text to audio.

**Request Body:**
```json
{
  "text": "Hello! How can I help you today?"
}
```

**Response:** Audio file (MP3)

---

#### Voice Conversation
Complete voice interaction cycle.

**Request:** Multipart form with audio file

**Response:**
```json
{
  "transcript": "How are you feeling?",
  "response": "I'm feeling great! Thanks for asking.",
  "audio": "base64_encoded_audio"
}
```

---

#### Voice WebSocket
Real-time bidirectional voice communication.

**Connection:**
```
WS {{baseUrl}}/api/voice/ws
Headers: Authorization: Bearer {{accessToken}}
```

---

### Emergency (`/api/emergency-contacts`)

```
POST   /api/emergency-contacts          - Create contact
GET    /api/emergency-contacts          - Get all contacts
```

**Create Contact Request:**
```json
{
  "name": "Dr. Smith",
  "phone": "+1234567890",
  "relationship": "Primary Care Physician",
  "priority": 1
}
```

---

### Profile (`/api/profile`)

```
GET    /api/profile                      - Get user profile
PUT    /api/profile                      - Update profile
```

**Update Profile Request:**
```json
{
  "name": "John Doe",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "preferences": {
    "units": "metric",
    "notifications": true,
    "theme": "light"
  }
}
```

---

## 🧪 Testing Workflows

### Complete Health Tracking Workflow

1. **Create Food Log**
   ```
   Health > Create Food Log
   ```

2. **Log Exercise**
   ```
   Tracking > Create Exercise Log
   ```

3. **Track Sleep**
   ```
   Tracking > Create Sleep Log
   ```

4. **Log Water Intake**
   ```
   Tracking > Create Water Log
   ```

5. **Get Health Insights**
   ```
   Health > Get Insights
   ```

---

### Medication Management Workflow

1. **Create Medication Schedule**
   ```
   Medication > Create Medication Schedule
   ```

2. **Log Medication Taken**
   ```
   Medication > Create Medication Log
   ```

3. **View Schedule**
   ```
   Medication > Get Medication Schedule
   ```

---

### Voice Interaction Workflow

1. **Voice Stream (STT)**
   ```
   Voice > Voice Stream
   ```
   Upload audio file → Get transcription

2. **Voice Synthesize (TTS)**
   ```
   Voice > Voice Synthesize
   ```
   Send text → Get audio response

3. **Full Voice Conversation**
   ```
   Voice > Voice Conversation
   ```
   Upload audio → Get AI response audio

4. **WebSocket (Real-time)**
   ```
   Voice > Voice WebSocket
   ```
   Connect → Exchange messages in real-time

---

### Alarm & Reminder Workflow

1. **Create Alarm**
   ```
   Alarms > Create Alarm
   ```
   Copy `alarm_id` from response to environment

2. **Get Alarms**
   ```
   Alarms > Get Alarms
   ```

3. **Update Alarm**
   ```
   Alarms > Update Alarm
   ```

4. **Get Notifications**
   ```
   Alarms > Get Notifications
   ```

5. **Mark Notification as Read**
   ```
   Alarms > Mark Notification Read
   ```

---

### AI Chat Assistant Workflow

1. **Food Tracking**
   ```
   Chat > Chat
   ```
   Send: "I ate roti and chawal for lunch"
   Intent: food_tracking

2. **Medication Logging**
   ```
   Chat > Chat - Medication Tracking
   ```
   Send: "I took my medicine today"
   Intent: medication

3. **Health Queries**
   ```
   Chat > Chat - Health Query
   ```
   Send: "What is my blood pressure?"
   Intent: health_query

4. **Recommendations**
   ```
   Chat > Chat - Recommendation
   ```
   Send: "What should I eat for breakfast?"
   Intent: recommendation

5. **General Conversation**
   ```
   Chat > Chat - General Conversation
   ```
   Send: "Hello, how are you?"
   Intent: general_chat

6. **Hindi Language Support**
   ```
   Chat > Chat - Hindi Language Support
   ```
   Send: "Maine aaj khana khaya"
   Locale: hi-IN

7. **Voice Channel**
   ```
   Chat > Chat - Voice Channel
   ```
   Send: "I had breakfast this morning"
   Channel: voice

8. **View History**
   ```
   Chat > Get Chat History
   ```
   Retrieves all past conversations

9. **Test Validation**
   ```
   Chat > Chat - Empty Message Validation
   ```
   Tests error handling (should return 422)

---

## 📊 Response Examples

### Success Response (2xx)

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation successful"
}
```

---

### Error Response (4xx/5xx)

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* additional details */ }
  }
}
```

**Common Error Codes:**
- `INVALID_TOKEN` - Expired or invalid access token
- `UNAUTHORIZED` - Missing or invalid credentials
- `VALIDATION_ERROR` - Invalid request data
- `NOT_FOUND` - Resource not found
- `SERVER_ERROR` - Internal server error

---

## 🔍 Troubleshooting

### Issue: "401 Unauthorized"

**Cause:** Missing or invalid access token

**Solution:**
1. Check `accessToken` in environment variables
2. Run `Auth > Login` to get fresh tokens
3. Ensure token hasn't expired (use `Auth > Refresh`)

---

### Issue: "404 Not Found"

**Cause:** Incorrect URL or resource doesn't exist

**Solution:**
1. Verify `baseUrl` is correct
2. Check the endpoint path
3. Ensure resource ID is valid (for update/delete operations)

---

### Issue: "422 Validation Error"

**Cause:** Invalid request data

**Solution:**
1. Check request body format
2. Verify required fields are present
3. Ensure data types are correct
4. Check enum values for restricted fields

---

### Issue: Voice Endpoints Not Working

**Cause:** Audio file not properly formatted or missing

**Solution:**
1. Ensure audio file path is set in `audio_file` environment variable
2. Verify file format (MP3, WAV)
3. Check file size (should be < 10MB)
4. For WebSocket: Ensure connection is established before sending data

---

### Issue: WebSocket Connection Fails

**Cause:** Invalid token or connection timeout

**Solution:**
1. Verify `accessToken` is valid
2. Check network connectivity
3. Ensure backend server is running
4. Try reconnecting after refreshing token

---

## 💡 Best Practices

1. **Always Login First**: Before testing protected endpoints
2. **Use Environment Variables**: Keep tokens and IDs organized
3. **Test in Order**: Follow the workflow sequence for related operations
4. **Check Responses**: Verify success before proceeding
5. **Refresh Tokens**: Use refresh endpoint before access token expires
6. **Clean Up**: Delete test resources (alarms, appointments) after testing

---

## 📚 Additional Resources

- [Bruno Documentation](https://docs.usebruno.com/)
- [JWT Token Information](https://jwt.io/)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Backend README](../README.md)

---

## 📝 Version History

- **v1.0** - Initial collection setup with all endpoints
- **v1.1** - Added WebSocket support for voice
- **v1.2** - Enhanced documentation with examples
- **v1.3** - Phase 6 Complete: Added LangGraph chat workflow with 8 test cases

---

**Last Updated:** February 23, 2026
