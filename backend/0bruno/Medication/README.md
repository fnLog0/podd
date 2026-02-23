# Medication API Tests

## Workflow

Run these tests in order to test the medication endpoints:

1. **Create Medication** - Create a new medication (e.g., Aspirin)
2. **Get Medications** - List all medications for the current user
3. **Create Medication Schedule** - Set up a schedule for the medication
4. **Create Medication Log** - Log that medication was taken
5. **Get Medication Schedule** - Retrieve all schedules

## Notes

- You must create a medication before you can create schedules or logs
- The access token is set in pre-request variables
- Update `accessToken` if it expires (get it from Auth → Login)

## Example Data

**Medication:**
```json
{
  "name": "Aspirin",
  "dosage": "10mg",
  "frequency": "twice daily",
  "instructions": "Take with food",
  "active": true
}
```

**Schedule:**
```json
{
  "medication_name": "Aspirin",
  "time_of_day": "08:00",
  "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
}
```

**Log:**
```json
{
  "medication_name": "Aspirin",
  "taken_at": "2024-02-16T08:00:00Z",
  "notes": "Taken with food"
}
```
