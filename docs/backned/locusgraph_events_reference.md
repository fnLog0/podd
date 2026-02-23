# LocusGraph Events Reference

All events submitted to LocusGraph use the same request shape. The service sends:

- **graph_id** (from settings, added in service)
- **event_kind** (string)
- **payload** (object)
- **source** (string, default `"agent"`)
- **context_id** (optional)
- **related_to** (optional, list of context IDs)
- **extends** (optional, list of context IDs)
- **reinforces** (optional, list of context IDs)
- **contradicts** (optional, list of context IDs)
- **timestamp** (optional, ISO string)

**Update behavior (LocusGraph):** If you send an event with a `context_id` that already exists, the second call **overwrites the payload** of the first event. So `store_event` with the same `context_id` and a new payload is the way to "update whole payload" — no separate update API needed.

Use this for **static/singleton data**: profile (one per user: `profile:{user_id}`), cache entries, and any entity where you want a single up-to-date record per context_id.

Below are every event kind and the JSON payloads we submit.

---

## 1. Chat (routes/chat/chat.py)

### User message
```json
{
  "event_kind": "observation",
  "context_id": "chat:{chat_event_id}_user",
  "related_to": ["person:{user_id}"],
  "payload": {
    "kind": "chat_message",
    "data": {
      "role": "user",
      "content": "<message>",
      "locale": "<locale>",
      "channel": "<channel>",
      "user_id": "<user_id>",
      "timestamp": "<ISO timestamp>"
    }
  }
}
```

### Assistant message
```json
{
  "event_kind": "observation",
  "context_id": "chat:{chat_event_id}_assistant",
  "related_to": ["person:{user_id}", "chat:{chat_event_id}_user"],
  "payload": {
    "kind": "chat_message",
    "data": {
      "role": "assistant",
      "content": "<response text>",
      "intent": "<intent>",
      "locale": "<locale>",
      "channel": "<channel>",
      "user_id": "<user_id>",
      "timestamp": "<ISO timestamp>"
    }
  }
}
```

---

## 2. Workflow memory (workflows/nodes/memory.py)

### Conversation turn (always appended)
```json
{
  "event_kind": "observation",
  "context_id": "chat:{new_id}",
  "related_to": ["person:{user_id}"],
  "payload": {
    "kind": "conversation_turn",
    "data": {
      "user_text": "<user input>",
      "assistant_text": "<assistant reply>",
      "intent": "<intent>",
      "timestamp": "<ISO timestamp>"
    }
  }
}
```

### Food tracking (from agent_food_tracking)
```json
{
  "event_kind": "observation",
  "context_id": "food:{record_id}",
  "related_to": ["person:{user_id}", "vital:nutrition"],
  "payload": {
    "kind": "food_intake",
    "data": {
      "raw_text": "<user text>",
      "record_id": "<record_id>",
      "timestamp": "<ISO timestamp>"
    }
  }
}
```

### Medication (from agent_medication)
```json
{
  "event_kind": "action",
  "context_id": "medication_log:{record_id}",
  "related_to": ["person:{user_id}", "medication:general"],
  "reinforces": ["recommendation:medication_adherence"],
  "payload": {
    "kind": "medication_taken",
    "data": {
      "raw_text": "<user text>",
      "record_id": "<record_id>",
      "timestamp": "<ISO timestamp>"
    }
  }
}
```

### Health query (from agent_health_query)
```json
{
  "event_kind": "observation",
  "context_id": "health_query:{record_id}",
  "related_to": ["person:{user_id}", "vital:general"],
  "payload": {
    "kind": "health_query",
    "data": {
      "query": "<user text>",
      "context_used": <number of memories>,
      "record_id": "<record_id>",
      "timestamp": "<ISO timestamp>"
    }
  }
}
```

### General chat (from agent_general_chat)
```json
{
  "event_kind": "observation",
  "context_id": "chat:{record_id}",
  "related_to": ["person:{user_id}"],
  "payload": {
    "kind": "general_chat",
    "data": {
      "user_text": "<user text>",
      "record_id": "<record_id>",
      "timestamp": "<ISO timestamp>"
    }
  }
}
```

### Recommendation (from agent_recommendation)
```json
{
  "event_kind": "decision",
  "context_id": "recommendation:{record_id}",
  "related_to": ["person:{user_id}", "recommendation:general"],
  "payload": {
    "kind": "clinical_recommendation",
    "data": {
      "query": "<user text>",
      "record_id": "<record_id>",
      "timestamp": "<ISO timestamp>"
    }
  }
}
```

---

## 3. Validation (services/validation/memory.py)

### Validation failed (new pattern)
```json
{
  "event_kind": "validation.failed",
  "context_id": "validation_pattern:{error_type}:{pattern}",
  "source": "validator",
  "payload": {
    "error_type": "<e.g. invalid_url, duplicate_value>",
    "value": "<value that failed>",
    "pattern": "<extracted pattern>",
    "error_message": "<message>",
    "user_id": "<user_id or null>",
    "failed_at": "<ISO timestamp>",
    "additional_context": {}
  }
}
```

### Validation failed (reinforces existing pattern)
Same as above, plus:
```json
"reinforces": ["validation_pattern:{error_type}:{pattern}"]
```

### Validation passed
```json
{
  "event_kind": "validation.passed",
  "context_id": "validation_pattern:{error_type}:{pattern}",
  "source": "validator",
  "contradicts": ["validation.failed:validation_pattern:{error_type}:{pattern}"],
  "payload": {
    "validation_type": "<error_type>",
    "value": "<value that passed>",
    "pattern": "<extracted pattern>",
    "user_id": "<user_id or null>",
    "validated_at": "<ISO timestamp>",
    "additional_context": {}
  }
}
```

---

## 4. Migration (services/migration/schema.py)

### Migration started
```json
{
  "event_kind": "migration.run",
  "context_id": "schema_migration:{migration_id}",
  "source": "system",
  "payload": {
    "migration_id": "<id>",
    "from_version": "<version>",
    "to_version": "<version>",
    "description": "<description>",
    "estimated_entities": <number or null>,
    "started_at": "<ISO timestamp>",
    "status": "in_progress",
    "entities_migrated": 0,
    "entities_failed": 0
  }
}
```

### Migration step
```json
{
  "event_kind": "migration.step",
  "context_id": "schema_migration:{migration_id}:step:{entity_id}",
  "related_to": ["schema_migration:{migration_id}"],
  "source": "system",
  "payload": {
    "entity_type": "<type>",
    "entity_id": "<id>",
    "success": true | false,
    "old_data": {} | null,
    "new_data": {} | null,
    "error_message": "<string or null>",
    "migrated_at": "<ISO timestamp>"
  }
}
```

### Migration completed
```json
{
  "event_kind": "migration.completed",
  "context_id": "schema_migration:{migration_id}:completed",
  "extends": ["schema_migration:{migration_id}"],
  "source": "system",
  "payload": {
    "migration_id": "<id>",
    "entities_migrated": <number>,
    "entities_failed": <number>,
    "completed_at": "<ISO timestamp>",
    "status": "completed",
    "notes": "<string or null>"
  }
}
```

### Migration failed
```json
{
  "event_kind": "migration.failed",
  "context_id": "schema_migration:{migration_id}:failed",
  "extends": ["schema_migration:{migration_id}"],
  "source": "system",
  "payload": {
    "migration_id": "<id>",
    "error_message": "<message>",
    "entities_migrated": <number>,
    "failed_at": "<ISO timestamp>",
    "status": "failed"
  }
}
```

---

## 5. Batch (services/batch/operations.py)

### Batch created
```json
{
  "event_kind": "batch.create",
  "context_id": "batch_operation:{user_id}:{entity_type}:{batch_id}",
  "source": "system",
  "payload": {
    "batch_id": "<id>",
    "entity_type": "<e.g. appointment, emergency_contact>",
    "operation_type": "<create|update|delete>",
    "user_id": "<user_id>",
    "description": "<string or null>",
    "created_at": "<ISO timestamp>",
    "entity_ids": [],
    "status": "in_progress",
    "total_items": 0,
    "successful_items": 0,
    "failed_items": 0
  }
}
```

### Batch item added
```json
{
  "event_kind": "batch.item_added",
  "context_id": "{batch_context}:item:{entity_id}",
  "related_to": ["<batch_context>"],
  "source": "system",
  "payload": {
    "entity_id": "<id>",
    "success": true | false,
    "error_message": "<string or null>",
    "added_at": "<ISO timestamp>"
  }
}
```

### Batch completed
```json
{
  "event_kind": "batch.completed",
  "context_id": "{batch_context}:completed",
  "extends": ["<batch_context>"],
  "source": "system",
  "payload": {
    "total_items": <number>,
    "successful_items": <number>,
    "failed_items": <number>,
    "entity_ids": ["<id1>", "..."],
    "completed_at": "<ISO timestamp>",
    "status": "completed"
  }
}
```

### Batch failed
```json
{
  "event_kind": "batch.failed",
  "context_id": "{batch_context}:failed",
  "extends": ["<batch_context>"],
  "source": "system",
  "payload": {
    "error_message": "<message>",
    "partial_entity_ids": ["<id>", "..."],
    "failed_at": "<ISO timestamp>",
    "status": "failed"
  }
}
```

---

## 6. Cache (services/locusgraph/cache.py)

### Cache set
```json
{
  "event_kind": "cache.set",
  "context_id": "cache_entry:{key_hash}",
  "source": "cache",
  "payload": {
    "cache_key": "<key string>",
    "value": <any JSON-serializable value>,
    "expires_at": "<ISO timestamp>",
    "ttl_seconds": <number>,
    "cached_at": "<ISO timestamp>",
    "metadata": {}
  }
}
```

### Cache expired
```json
{
  "event_kind": "cache.expired",
  "context_id": "{cache_entry_context_id}:expired",
  "extends": ["<cache_entry_context_id>"],
  "source": "cache",
  "payload": {
    "expired_at": "<ISO timestamp>",
    "status": "expired"
  }
}
```

---

## 7. Reminders / temporal (services/temporal/scheduler.py)

### Reminder scheduled
```json
{
  "event_kind": "reminder.scheduled",
  "context_id": "reminder_scheduled:{reminder_id}",
  "related_to": ["<target_entity_type>:<target_entity_id>"],
  "source": "system",
  "payload": {
    "target_entity_type": "<e.g. appointment, meditation>",
    "target_entity_id": "<id>",
    "original_event_time": "<ISO>",
    "trigger_at": "<ISO>",
    "reminder_minutes_before": <number>,
    "user_id": "<user_id>",
    "title": "<string>",
    "message": "<string or null>",
    "due": "<temporal metadata from TemporalContext.enrich_payload>"
  }
}
```

### Reminder sent
```json
{
  "event_kind": "reminder.sent",
  "context_id": "<reminder_context_id>",
  "extends": ["<reminder_context_id>"],
  "source": "system",
  "payload": {
    "sent_at": "<ISO timestamp>",
    "status": "sent"
  }
}
```

### Reminder cancelled
```json
{
  "event_kind": "reminder.cancelled",
  "context_id": "<reminder_context_id>",
  "extends": ["<reminder_context_id>"],
  "source": "system",
  "payload": {
    "cancelled_at": "<ISO timestamp>",
    "status": "cancelled"
  }
}
```

---

## 8. Alarms / notifications (services/alarms/scheduler.py)

### Notification (when alarm fires)
```json
{
  "event_kind": "notification.create",
  "context_id": "notification:{notification_id}",
  "payload": {
    "alarm_id": "<alarm_id>",
    "title": "<string>",
    "message": "<string>",
    "type": "medication" | "water" | "meal" | "meditation" | "appointment",
    "read": false,
    "created_at": "<ISO timestamp>",
    "user_id": "<user_id>"
  }
}
```

---

## 9. Profile (routes/profile/profile.py)

Uses `EventKind.PROFILE_CREATE`, `PROFILE_UPDATE`, `PROFILE_DELETE` and `ProfileEventDefinition.create_payload()`.

### Profile create/update
```json
{
  "event_kind": "profile.create" | "profile.update",
  "context_id": "profile:{user_id}",
  "payload": {
    "date_of_birth": "<date or null>",
    "gender": "<string or null>",
    "height_cm": <number or null>,
    "weight_kg": <number or null>,
    "blood_type": "A+" | "A-" | "B+" | "B-" | "O+" | "O-" | "AB+" | "AB-" | null,
    "allergies": ["<string>", "..."],
    "medical_conditions": ["<string>", "..."],
    "dietary_preferences": ["<string>", "..."]
  }
}
```

### Profile delete
```json
{
  "event_kind": "profile.delete",
  "context_id": "profile:{user_id}",
  "payload": { "deleted": true, "user_id": "<user_id>" }
}
```

---

## 10. Vitals (routes/health/vitals.py)

### Vitals create/update
```json
{
  "event_kind": "vitals.create" | "vitals.update",
  "context_id": "vitals:{id}",
  "payload": {
    "blood_pressure_systolic": <50..250 or null>,
    "blood_pressure_diastolic": <30..150 or null>,
    "heart_rate": <30..220 or null>,
    "blood_sugar": <0..600 or null>,
    "temperature": <30..45 or null>,
    "weight_kg": <0 or null>,
    "logged_at": "<ISO timestamp>",
    "user_id": "<user_id>"
  }
}
```

### Vitals delete
```json
{
  "event_kind": "vitals.delete",
  "context_id": "vitals:{id}",
  "payload": {}
}
```

---

## 11. Food log (routes/health/food_log.py, routes/health/health.py)

### Food log create/update
```json
{
  "event_kind": "food_log.create" | "food_log.update",
  "context_id": "food:{id}",
  "payload": {
    "description": "<string>",
    "calories": <number or null>,
    "protein_g": <number or null>,
    "carbs_g": <number or null>,
    "fat_g": <number or null>,
    "meal_type": "breakfast" | "lunch" | "dinner" | "snack" | "other",
    "logged_at": "<ISO timestamp>",
    "user_id": "<user_id>"
  }
}
```

### Food log delete
```json
{
  "event_kind": "food_log.delete",
  "context_id": "food:{id}",
  "payload": {}
}
```

---

## 12. Tracking: water, sleep, exercise, mood (routes/health/tracking.py)

### Water log
```json
{
  "event_kind": "water_log.create",
  "context_id": "water:{id}",
  "payload": {
    "amount_ml": <number>,
    "logged_at": "<ISO timestamp>",
    "user_id": "<user_id>"
  }
}
```

### Sleep log
```json
{
  "event_kind": "sleep_log.create",
  "context_id": "sleep:{id}",
  "payload": {
    "sleep_start": "<ISO timestamp>",
    "sleep_end": "<ISO timestamp>",
    "quality": "poor" | "fair" | "good" | "excellent",
    "notes": "<string or null>",
    "user_id": "<user_id>"
  }
}
```

### Exercise log
```json
{
  "event_kind": "exercise_log.create",
  "context_id": "exercise:{id}",
  "payload": {
    "exercise_type": "<string>",
    "duration_minutes": <number>,
    "calories_burned": <number or null>,
    "intensity": "low" | "moderate" | "high" | "vigorous",
    "logged_at": "<ISO timestamp>",
    "user_id": "<user_id>"
  }
}
```

### Mood log
```json
{
  "event_kind": "mood_log.create",
  "context_id": "mood:{id}",
  "payload": {
    "mood": "very_bad" | "bad" | "neutral" | "good" | "very_good",
    "energy_level": "very_low" | "low" | "medium" | "high" | "very_high",
    "notes": "<string or null>",
    "logged_at": "<ISO timestamp>",
    "user_id": "<user_id>"
  }
}
```

---

## 13. Medication (routes/medication/medication.py, medication_schedule.py)

### Medication create/update
```json
{
  "event_kind": "medication.create" | "medication.update",
  "context_id": "medication:{id}",
  "payload": {
    "name": "<string>",
    "dosage": "<string>",
    "frequency": "<string>",
    "instructions": "<string or null>",
    "active": true | false,
    "user_id": "<user_id>"
  }
}
```

### Medication delete
```json
{
  "event_kind": "medication.delete",
  "context_id": "medication:{id}",
  "payload": {}
}
```

### Medication log
```json
{
  "event_kind": "medication.log",
  "context_id": "med_log:{id}",
  "payload": {
    "medication_id": "<id>",
    "scheduled_time": "<ISO or null>",
    "taken_at": "<ISO>",
    "notes": "<string or null>",
    "user_id": "<user_id>"
  }
}
```

### Medication schedule create/update
```json
{
  "event_kind": "medication_schedule.create" | "medication_schedule.update",
  "context_id": "med_schedule:{id}",
  "payload": {
    "medication_id": "<id>",
    "time_of_day": "<e.g. 08:00>",
    "days_of_week": ["mon", "tue", "..."],
    "user_id": "<user_id>"
  }
}
```

### Medication schedule delete
```json
{
  "event_kind": "medication_schedule.delete",
  "context_id": "med_schedule:{id}",
  "payload": {}
}
```

---

## 14. Appointments (routes/appointments/appointments.py)

### Appointment create/update
```json
{
  "event_kind": "appointment.create" | "appointment.update",
  "context_id": "appointment:{id}",
  "payload": {
    "title": "<string>",
    "doctor_name": "<string or null>",
    "location": "<string or null>",
    "scheduled_at": "<ISO timestamp>",
    "notes": "<string or null>",
    "reminder_minutes_before": <number or null>,
    "user_id": "<user_id>"
  }
}
```

### Appointment delete
```json
{
  "event_kind": "appointment.delete",
  "context_id": "appointment:{id}",
  "payload": {}
}
```

---

## 15. Emergency contacts (routes/emergency/emergency.py)

### Emergency contact create/update
```json
{
  "event_kind": "emergency_contact.create" | "emergency_contact.update",
  "context_id": "emergency_contact:{id}",
  "payload": {
    "name": "<string>",
    "relationship": "<string or null>",
    "phone": "<string>",
    "is_primary": true | false,
    "user_id": "<user_id>"
  }
}
```

### Emergency contact delete
```json
{
  "event_kind": "emergency_contact.delete",
  "context_id": "emergency_contact:{id}",
  "payload": {}
}
```

---

## 16. Alarms (routes/alarms/alarms.py)

### Alarm create/update
```json
{
  "event_kind": "alarm.create" | "alarm.update",
  "context_id": "alarm:{id}",
  "payload": {
    "type": "medication" | "water" | "meal" | "meditation" | "appointment",
    "title": "<string>",
    "message": "<string or null>",
    "time": "<HH:MM 24h>",
    "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
    "active": true | false,
    "reference_id": "<string or null>",
    "user_id": "<user_id>"
  }
}
```

### Alarm delete
```json
{
  "event_kind": "alarm.delete",
  "context_id": "alarm:{id}",
  "payload": {}
}
```

### Notification read
```json
{
  "event_kind": "notification.read",
  "context_id": "notification:{id}",
  "payload": { "read": true, "..." }
}
```

---

## 17. Meditation (routes/meditation/meditation.py)

### Meditation session create
```json
{
  "event_kind": "meditation_session.create",
  "context_id": "meditation_session:{id}",
  "payload": {
    "title": "<string>",
    "description": "<string or null>",
    "audio_url": "<string or null>",
    "duration_minutes": <number>,
    "category": "<string or null>"
  }
}
```

### Meditation log
```json
{
  "event_kind": "meditation.log",
  "context_id": "meditation_log:{id}",
  "payload": {
    "session_id": "<id>",
    "duration_minutes": <number>,
    "completed": true | false,
    "logged_at": "<ISO timestamp>",
    "user_id": "<user_id>"
  }
}
```

---

## Event kinds index

| event_kind | context_id pattern | source |
|------------|--------------------|--------|
| observation | chat:*, food:*, health_query:*, chat:* | (default agent) |
| action | medication_log:* | (default agent) |
| decision | recommendation:* | (default agent) |
| validation.failed | validation_pattern:* | validator |
| validation.passed | validation_pattern:* | validator |
| migration.run | schema_migration:* | system |
| migration.step | schema_migration:*:step:* | system |
| migration.completed | schema_migration:*:completed | system |
| migration.failed | schema_migration:*:failed | system |
| batch.create | batch_operation:* | system |
| batch.item_added | batch_operation:*:item:* | system |
| batch.completed | batch_operation:*:completed | system |
| batch.failed | batch_operation:*:failed | system |
| cache.set | cache_entry:* | cache |
| cache.expired | cache_entry:*:expired | cache |
| reminder.scheduled | reminder_scheduled:* | system |
| reminder.sent | reminder_scheduled:* | system |
| reminder.cancelled | reminder_scheduled:* | system |
| notification.create | notification:* | (default) |
| notification.read | notification:* | (default) |
| profile.create/update/delete | profile:{user_id} | (default) |
| vitals.create/update/delete | vitals:* | (default) |
| food_log.create/update/delete | food:* | (default) |
| water_log.create | water:* | (default) |
| sleep_log.create | sleep:* | (default) |
| exercise_log.create | exercise:* | (default) |
| mood_log.create | mood:* | (default) |
| medication.create/update/delete | medication:* | (default) |
| medication.log | med_log:* | (default) |
| medication_schedule.create/update/delete | med_schedule:* | (default) |
| appointment.create/update/delete | appointment:* | (default) |
| emergency_contact.create/update/delete | emergency_contact:* | (default) |
| alarm.create/update/delete | alarm:* | (default) |
| meditation_session.create | meditation_session:* | (default) |
| meditation.log | meditation_log:* | (default) |
