# Podd Backend — Health Assistant for Mom

> **Tech stack:** Python · FastAPI · LangGraph · LocusGraph SDK · SQLite (auth only) · JWT auth
> **Frontend (separate repo):** React + Tailwind + shadcn/ui
> **Hardware:** ESP32 with mic + speaker

---

## Phase 1: Project Setup & Auth (Days 1–3)

- [ ] Set up Python virtual env (`python -m venv .venv`), create `requirements.txt` with FastAPI, uvicorn, SQLAlchemy, aiosqlite, python-jose, passlib, pydantic
- [ ] SQLite auto-creates on startup (`podd_auth.db`), create `.env` with `JWT_SECRET`, LocusGraph API key, etc.
- [ ] SQLite tables created automatically via SQLAlchemy `create_all()` on app startup
- [ ] Create `User` model (id, email, hashed_password, name, created_at, updated_at) — SQLite only
- [ ] Implement auth endpoints:
  - [ ] `POST /api/auth/register` — create user, return tokens
  - [ ] `POST /api/auth/login` — validate credentials, return access + refresh tokens
  - [ ] `POST /api/auth/logout` — invalidate refresh token
  - [ ] `POST /api/auth/refresh` — issue new access token from refresh token
  - [ ] `GET /api/auth/me` — return current user from JWT
- [ ] Test all auth endpoints with curl / Postman
- [ ] Add JWT middleware (`Depends(get_current_user)`) to protect all non-auth routes

---

## Phase 2: Health Profile & Core Tracking (Days 4–7)

- [ ] Install LocusGraph SDK, configure with API key in `.env`
- [ ] Define LocusGraph event schemas for non-auth data:
  - [ ] `Profile` — stored via LocusGraph SDK with `context_id` format `profile:<user_id>` (date_of_birth, gender, height_cm, weight_kg, blood_type, allergies, medical_conditions, dietary_preferences)
  - [ ] `FoodLog` — stored via LocusGraph SDK with `context_id` format `food:<id>` (description, calories, protein_g, carbs_g, fat_g, meal_type, logged_at)
  - [ ] `Vitals` — stored via LocusGraph SDK with `context_id` format `vitals:<id>` (blood_pressure_systolic, blood_pressure_diastolic, heart_rate, blood_sugar, temperature, weight_kg, logged_at)
  - [ ] `Medication` — stored via LocusGraph SDK with `context_id` format `medication:<id>` (name, dosage, frequency, instructions, active)
  - [ ] `MedicationSchedule` — stored via LocusGraph SDK with `context_id` format `med_schedule:<id>` (medication_id, time_of_day, days_of_week)
- [ ] Implement profile endpoints (data stored/retrieved via LocusGraph SDK):
  - [ ] `GET /api/profile` — get current user's health profile
  - [ ] `PUT /api/profile` — create or update health profile
- [ ] Implement food tracking (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/food/log` — log a meal/food item
  - [ ] `GET /api/food/logs` — get food logs (query params: date, meal_type, limit)
- [ ] Implement vitals tracking (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/health/vitals` — log vitals reading
  - [ ] `GET /api/health/vitals` — get vitals history (query params: date_from, date_to, limit)
- [ ] Implement medication (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/medication/log` — log that a medication was taken
  - [ ] `GET /api/medication/schedule` — get all active medication schedules
  - [ ] `POST /api/medication/schedule` — add a new medication + schedule
- [ ] On every health event (food log, vitals, medication), call `store_event()` with structured payload
- [ ] Link related events with `related_to` (e.g., medication events linked to vitals)

---

## Phase 3: Additional Tracking (Days 8–10)

- [ ] Define LocusGraph event schemas for additional tracking:
  - [ ] `WaterLog` — stored via LocusGraph SDK with `context_id` format `water:<id>` (amount_ml, logged_at)
  - [ ] `SleepLog` — stored via LocusGraph SDK with `context_id` format `sleep:<id>` (sleep_start, sleep_end, quality, notes)
  - [ ] `ExerciseLog` — stored via LocusGraph SDK with `context_id` format `exercise:<id>` (exercise_type, duration_minutes, calories_burned, intensity, logged_at)
  - [ ] `MoodLog` — stored via LocusGraph SDK with `context_id` format `mood:<id>` (mood, energy_level, notes, logged_at)
- [ ] Implement water tracking (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/water/log` — log water intake
  - [ ] `GET /api/water/history` — get water logs (query params: date, limit)
- [ ] Implement sleep tracking (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/sleep/log` — log sleep session
  - [ ] `GET /api/sleep/history` — get sleep logs (query params: date_from, date_to, limit)
- [ ] Implement exercise tracking (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/exercise/log` — log exercise session
  - [ ] `GET /api/exercise/history` — get exercise logs (query params: date, limit)
- [ ] Implement mood tracking (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/mood/log` — log mood entry
  - [ ] `GET /api/mood/history` — get mood logs (query params: date_from, date_to, limit)

---

## Phase 4: Meditation & Appointments (Days 11–13)

- [ ] Define LocusGraph event schemas:
  - [ ] `MeditationSession` — stored via LocusGraph SDK with `context_id` format `meditation_session:<id>` (title, description, audio_url, duration_minutes, category)
  - [ ] `MeditationLog` — stored via LocusGraph SDK with `context_id` format `meditation_log:<id>` (session_id, duration_minutes, completed, logged_at)
  - [ ] `Appointment` — stored via LocusGraph SDK with `context_id` format `appointment:<id>` (title, doctor_name, location, scheduled_at, notes, reminder_minutes_before)
  - [ ] `EmergencyContact` — stored via LocusGraph SDK with `context_id` format `emergency_contact:<id>` (name, relationship, phone, is_primary)
- [ ] Implement meditation endpoints (data stored/retrieved via LocusGraph SDK):
  - [ ] `GET /api/meditation/sessions` — list available meditation sessions (filterable by category)
  - [ ] `GET /api/meditation/sessions/:id` — get single session details
  - [ ] `POST /api/meditation/log` — log a completed meditation
  - [ ] `GET /api/meditation/history` — get meditation history
- [ ] Implement appointments (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/appointments` — create appointment
  - [ ] `GET /api/appointments` — list appointments (query: upcoming, past)
  - [ ] `PUT /api/appointments/:id` — update appointment
- [ ] Implement emergency contacts (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/emergency-contacts` — add emergency contact
  - [ ] `GET /api/emergency-contacts` — list all emergency contacts

---

## Phase 5: Alarms & Notifications (Days 14–16)

- [ ] Define LocusGraph event schemas:
  - [ ] `Alarm` — stored via LocusGraph SDK with `context_id` format `alarm:<id>` (type enum [medication/water/meal/meditation/appointment], title, message, time, days_of_week, active, reference_id)
  - [ ] `Notification` — stored via LocusGraph SDK with `context_id` format `notification:<id>` (alarm_id, title, message, type, read, created_at)
- [ ] Implement alarm CRUD (data stored/retrieved via LocusGraph SDK):
  - [ ] `POST /api/alarms` — create alarm
  - [ ] `GET /api/alarms` — list all alarms for user
  - [ ] `PUT /api/alarms/:id` — update alarm (toggle active, change time, etc.)
  - [ ] `DELETE /api/alarms/:id` — delete alarm
- [ ] Implement notifications (data stored/retrieved via LocusGraph SDK):
  - [ ] `GET /api/notifications` — list notifications (query: unread_only, limit)
  - [ ] `PUT /api/notifications/:id/read` — mark notification as read
- [ ] Background scheduler (APScheduler or similar):
  - [ ] Check every minute for alarms that should fire
  - [ ] Create `Notification` event in LocusGraph when alarm triggers
  - [ ] Alarm types to handle:
    - [ ] `medication` — "Time to take [medication name]"
    - [ ] `water` — "Time to drink water"
    - [ ] `meal` — "Time for [breakfast/lunch/dinner]"
    - [ ] `meditation` — "Time for your meditation session"
    - [ ] `appointment` — "Upcoming appointment: [title] in [X] minutes"
  - [ ] ESP32 integration: push notification to device so it announces via speaker

---

## Phase 6: LangGraph Workflow + LocusGraph (Days 17–21)

- [ ] Install LangGraph, set up workflow entry point
- [ ] Define LangGraph state schema (user_id, message, health_context, tool_results, response)
- [ ] Create health agents/nodes:
  - [ ] **Router node** — classify intent (food tracking, health query, general chat, etc.)
  - [ ] **Food tracking agent** — parse food descriptions, estimate calories, log meals
  - [ ] **Health query agent** — answer health questions using profile + vitals context
  - [ ] **Recommendation agent** — generate personalized health/diet recommendations
  - [ ] **General chat agent** — friendly conversation, emotional support
- [ ] LangGraph tools (callable by agents):
  - [ ] `store_health_event` — wraps LocusGraph SDK `store_event()`
  - [ ] `retrieve_health_context` — wraps LocusGraph SDK `retrieve_context()` to get relevant past health data
  - [ ] `generate_health_insights` — wraps LocusGraph SDK `generate_insights()` for analysis
  - [ ] `get_user_profile` — fetch profile via LocusGraph SDK
  - [ ] `get_recent_vitals` — fetch recent vitals via LocusGraph SDK
  - [ ] `get_medication_schedule` — fetch active medications via LocusGraph SDK
- [ ] Implement chat endpoints:
  - [ ] `POST /api/chat` — send message, run through LangGraph workflow, return response
  - [ ] `GET /api/chat/history` — get past conversations (stored in LocusGraph as events)
- [ ] Health-specific system prompts:
  - [ ] Food tracking prompt (parse food, estimate nutrition, suggest healthier alternatives)
  - [ ] Diagnosis suggestion prompt (disclaimer: not medical advice, suggest seeing doctor)
  - [ ] Recipe recommendation prompt (based on dietary preferences, allergies, available ingredients)
  - [ ] Daily health summary prompt (combine all today's data into a summary)
- [ ] Implement insight endpoints:
  - [ ] `GET /api/health/recommendations` — LLM-powered personalized recommendations (uses LangGraph + LocusGraph context)
  - [ ] `GET /api/health/insights` — LocusGraph-generated insights from stored health events

---

## Phase 7: Voice Pipeline — Sarvam AI (Days 22–25)

- [ ] Set up Sarvam AI SDK (`sarvamai`), configure with `SARVAM_API_KEY` in `.env`
- [ ] STT: Saaras v2.5 — auto language detect, 11 Indian languages, code-mixing support, ₹30/hr
- [ ] TTS: Bulbul v3 — 30+ Indian voices, 11 languages, ₹30/10K chars
- [ ] Implement voice endpoints:
  - [ ] `POST /api/voice/stream` — receive audio blob, run Saaras STT, return transcript as JSON
  - [ ] `POST /api/voice/synthesize` — receive text, run Bulbul TTS, return audio file (WAV)
  - [ ] `POST /api/voice/conversation` — full round-trip: audio → Saaras STT → LangGraph workflow → Bulbul TTS → return audio response
- [ ] WebSocket endpoint:
  - [ ] `WS /ws/voice` — real-time bidirectional audio streaming
  - [ ] Client sends audio chunks, server streams back TTS audio chunks
  - [ ] Handle interruptions (user speaks while TTS is playing)
- [ ] ESP32 integration:
  - [ ] Test audio capture from ESP32 mic → POST to `/api/voice/stream`
  - [ ] Test TTS playback: `/api/voice/synthesize` → ESP32 speaker
  - [ ] Test full conversation loop via WebSocket
  - [ ] Optimize audio format/compression for ESP32 bandwidth

---

## Phase 8: Polish & Testing (Days 26–30)

- [ ] Error handling: consistent error response format (`{"detail": "...", "code": "..."}`) on all endpoints
- [ ] Input validation: Pydantic models with proper constraints on all request bodies
- [ ] Rate limiting: add rate limiter middleware (e.g., slowapi) — especially on `/api/chat` and `/api/voice/*`
- [ ] API documentation: review FastAPI auto-generated docs at `/docs`, add descriptions to all endpoints
- [ ] Unit tests:
  - [ ] Auth (register, login, token refresh, protected routes)
  - [ ] Health tracking (food, vitals, water, sleep, exercise, mood)
  - [ ] Alarms (CRUD, scheduler trigger logic)
  - [ ] Profile (create, update, retrieve)
- [ ] Integration tests:
  - [ ] LangGraph workflow end-to-end (message → agent routing → tool calls → response)
  - [ ] LocusGraph event storage and retrieval
  - [ ] Voice pipeline (audio → transcript → response → audio)
- [ ] Hindi/Urdu language support:
  - [ ] Add language preference to user profile
  - [ ] System prompts in Hindi/Urdu for LangGraph agents
  - [ ] Saaras STT auto-detects Hindi/Urdu (no config needed)
  - [ ] Bulbul TTS voice selection for Hindi (`hi-IN`) — pick best speaker for mom
- [ ] Deployment:
  - [ ] Dockerize the app (`Dockerfile` + `docker-compose.yml`)
  - [ ] Deploy to cloud (or local server accessible to ESP32)
  - [ ] Set up environment variables in production
  - [ ] Configure CORS for frontend origin

---

## API Endpoints Summary (44 endpoints)

### Auth (5)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/register` | Create new user account |
| POST | `/api/auth/login` | Authenticate and get tokens |
| POST | `/api/auth/logout` | Invalidate refresh token |
| POST | `/api/auth/refresh` | Get new access token |
| GET | `/api/auth/me` | Get current user info |

### Chat (2)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/chat` | Send message through LangGraph workflow |
| GET | `/api/chat/history` | Get conversation history |

### Voice (4)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/voice/stream` | Audio → Saaras STT → transcript |
| POST | `/api/voice/synthesize` | Text → Bulbul TTS → audio |
| POST | `/api/voice/conversation` | Full round-trip: audio → Saaras → LLM → Bulbul → audio |
| WS | `/ws/voice` | Real-time bidirectional audio streaming |

### Profile (2)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/profile` | Get user health profile |
| PUT | `/api/profile` | Create/update health profile |

### Health & Insights (4)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/health/vitals` | Log vitals reading |
| GET | `/api/health/vitals` | Get vitals history |
| GET | `/api/health/recommendations` | LLM-powered health recommendations |
| GET | `/api/health/insights` | LocusGraph-generated insights |

### Food (2)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/food/log` | Log a meal or food item |
| GET | `/api/food/logs` | Get food log history |

### Medication (3)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/medication/log` | Log medication taken |
| GET | `/api/medication/schedule` | Get active medication schedules |
| POST | `/api/medication/schedule` | Add new medication + schedule |

### Water (2)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/water/log` | Log water intake |
| GET | `/api/water/history` | Get water intake history |

### Sleep (2)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/sleep/log` | Log sleep session |
| GET | `/api/sleep/history` | Get sleep history |

### Exercise (2)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/exercise/log` | Log exercise session |
| GET | `/api/exercise/history` | Get exercise history |

### Mood (2)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/mood/log` | Log mood entry |
| GET | `/api/mood/history` | Get mood history |

### Meditation (4)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/meditation/sessions` | List available meditation sessions |
| GET | `/api/meditation/sessions/:id` | Get single session details |
| POST | `/api/meditation/log` | Log completed meditation |
| GET | `/api/meditation/history` | Get meditation history |

### Alarms (4)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/alarms` | Create alarm |
| GET | `/api/alarms` | List all alarms |
| PUT | `/api/alarms/:id` | Update alarm |
| DELETE | `/api/alarms/:id` | Delete alarm |

### Appointments (3)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/appointments` | Create appointment |
| GET | `/api/appointments` | List appointments |
| PUT | `/api/appointments/:id` | Update appointment |

### Notifications (2)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/notifications` | List notifications |
| PUT | `/api/notifications/:id/read` | Mark notification as read |

### Emergency Contacts (2)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/emergency-contacts` | Add emergency contact |
| GET | `/api/emergency-contacts` | List emergency contacts |

---

## Tech Notes

- **SQLite** is used only for auth (users table, refresh tokens). The database file auto-creates on startup via SQLAlchemy `create_all()` — no migrations needed.
- **LocusGraph SDK** is the primary database for all non-auth data. Every health event (food, vitals, medication, water, sleep, exercise, mood, meditation), profile, appointments, alarms, notifications, emergency contacts, and chat history gets stored as a LocusGraph event with structured payloads. Use `retrieve_context()` to pull relevant data, and `generate_insights()` for analysis.
- **LangGraph** orchestrates health agents. Each agent is a node in the workflow graph. The router node classifies user intent and routes to the appropriate agent. Agents have access to tools that call LocusGraph SDK for all data operations.
- **JWT auth** on all non-auth routes. Access token (short-lived, ~15 min) + refresh token (long-lived, ~7 days). Store refresh tokens in SQLite to enable logout/revocation.
- **Sarvam AI** for voice: Saaras v2.5 (STT, ₹30/hr, 11 Indian languages, auto-detect, code-mixing) + Bulbul v3 (TTS, ₹30/10K chars, 30+ Indian voices). SDK: `sarvamai`. ₹1000 free credits to start.
- **ESP32** connects via WebSocket for voice, receives alarm notifications via push, and announces them through the speaker. Audio format: 16-bit PCM, 16kHz sample rate for Saaras compatibility.
- **Hindi/Urdu support** is critical — Mom's primary languages. Saaras auto-detects Hindi/Urdu. Bulbul v3 has 30+ native Indian voices for natural Hindi TTS.
