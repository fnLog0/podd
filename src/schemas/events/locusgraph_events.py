"""LocusGraph event schemas for non-auth data storage.

This module defines the event kinds and context ID patterns used with LocusGraph SDK
for storing health and user profile data.

Event-specific payload schemas and definitions are in separate modules:
- profile_events.py - Profile events
- food_events.py - FoodLog events
- vitals_events.py - Vitals events
- medication_events.py - Medication, MedicationLog, and MedicationSchedule events
- tracking_events.py - WaterLog, SleepLog, ExerciseLog, and MoodLog events
- meditation_events.py - MeditationSession and MeditationLog events
- appointments_events.py - Appointment events
- emergency_events.py - EmergencyContact events
- alarms/alarms_events.py - Alarm and Notification events
"""

# ==================== LocusGraph Event Kind Constants ====================


class EventKind:
    """Constants for LocusGraph event kinds."""

    # Profile events
    PROFILE_CREATE = "profile.create"
    PROFILE_UPDATE = "profile.update"
    PROFILE_DELETE = "profile.delete"

    # FoodLog events
    FOOD_LOG_CREATE = "food_log.create"
    FOOD_LOG_UPDATE = "food_log.update"
    FOOD_LOG_DELETE = "food_log.delete"

    # Vitals events
    VITALS_CREATE = "vitals.create"
    VITALS_UPDATE = "vitals.update"
    VITALS_DELETE = "vitals.delete"

    # Medication events
    MEDICATION_CREATE = "medication.create"
    MEDICATION_UPDATE = "medication.update"
    MEDICATION_DELETE = "medication.delete"
    MEDICATION_LOG = "medication.log"

    # MedicationSchedule events
    MEDICATION_SCHEDULE_CREATE = "medication_schedule.create"
    MEDICATION_SCHEDULE_UPDATE = "medication_schedule.update"
    MEDICATION_SCHEDULE_DELETE = "medication_schedule.delete"

    # WaterLog events
    WATER_LOG_CREATE = "water_log.create"

    # SleepLog events
    SLEEP_LOG_CREATE = "sleep_log.create"

    # ExerciseLog events
    EXERCISE_LOG_CREATE = "exercise_log.create"

    # MoodLog events
    MOOD_LOG_CREATE = "mood_log.create"

    # Meditation events
    MEDITATION_SESSION_CREATE = "meditation_session.create"
    MEDITATION_LOG = "meditation.log"

    # Appointment events
    APPOINTMENT_CREATE = "appointment.create"
    APPOINTMENT_UPDATE = "appointment.update"
    APPOINTMENT_DELETE = "appointment.delete"

    # EmergencyContact events
    EMERGENCY_CONTACT_CREATE = "emergency_contact.create"
    EMERGENCY_CONTACT_UPDATE = "emergency_contact.update"
    EMERGENCY_CONTACT_DELETE = "emergency_contact.delete"

    # Alarm events
    ALARM_CREATE = "alarm.create"
    ALARM_UPDATE = "alarm.update"
    ALARM_DELETE = "alarm.delete"

    # Notification events
    NOTIFICATION_CREATE = "notification.create"
    NOTIFICATION_READ = "notification.read"


# ==================== Context ID Patterns ====================


class ContextIdPattern:
    """Constants for context ID patterns used in LocusGraph.

    Context IDs follow the format: <entity_type>:<entity_id>
    """

    # Profile contexts: profile:<user_id>
    PROFILE = "profile:{user_id}"

    # FoodLog contexts: food:<id>
    FOOD_LOG = "food:{id}"

    # Vitals contexts: vitals:<id>
    VITALS = "vitals:{id}"

    # Medication contexts: medication:<id>
    MEDICATION = "medication:{id}"

    # MedicationLog contexts: med_log:<id>
    MEDICATION_LOG = "med_log:{id}"

    # MedicationSchedule contexts: med_schedule:<id>
    MEDICATION_SCHEDULE = "med_schedule:{id}"

    # WaterLog contexts: water:<id>
    WATER_LOG = "water:{id}"

    # SleepLog contexts: sleep:<id>
    SLEEP_LOG = "sleep:{id}"

    # ExerciseLog contexts: exercise:<id>
    EXERCISE_LOG = "exercise:{id}"

    # MoodLog contexts: mood:<id>
    MOOD_LOG = "mood:{id}"

    # MeditationSession contexts: meditation_session:<id>
    MEDITATION_SESSION = "meditation_session:{id}"

    # MeditationLog contexts: meditation_log:<id>
    MEDITATION_LOG = "meditation_log:{id}"

    # Appointment contexts: appointment:<id>
    APPOINTMENT = "appointment:{id}"

    # EmergencyContact contexts: emergency_contact:<id>
    EMERGENCY_CONTACT = "emergency_contact:{id}"

    # Alarm contexts: alarm:<id>
    ALARM = "alarm:{id}"

    # Notification contexts: notification:<id>
    NOTIFICATION = "notification:{id}"
