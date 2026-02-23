# Chat API - Bruno Collection

This folder contains API test requests for the Chat endpoints that use LangGraph workflow.

## Endpoints

### POST /api/chat
Send a message through the LangGraph workflow and get a response.

**Request Body:**
```json
{
  "message": "User message (required, 1-1000 chars)",
  "locale": "en-IN or hi-IN (optional, default: en-IN)",
  "channel": "text or voice (optional, default: text)"
}
```

**Response:**
```json
{
  "response": "Assistant's response",
  "intent": "detected_intent",
  "locale": "en-IN"
}
```

### GET /api/chat/history
Get past conversation history.

**Query Parameters:**
- `limit` (optional, default: 10): Maximum number of conversations to return

**Response:**
```json
{
  "conversations": [
    {
      "user_text": "User's message",
      "assistant_text": "Assistant's response",
      "intent": "detected_intent",
      "timestamp": "2024-02-16T12:00:00Z"
    }
  ],
  "total_count": 5
}
```

## Test Cases

| Test Case | Description | Expected Intent |
|-----------|-------------|----------------|
| Chat | Food tracking (roti and chawal for lunch) | food_tracking |
| Chat - Medication Tracking | Medication logging | medication |
| Chat - Health Query | Blood pressure query | health_query |
| Chat - Recommendation | Breakfast recommendation | recommendation |
| Chat - General Conversation | General conversation | general_chat |
| Chat - Hindi Language Support | Hindi text input | food_tracking |
| Chat - Voice Channel | Voice channel input | food_tracking |
| Chat - Empty Message Validation | Empty message (should fail validation) | - |

## Intent Classification

The LangGraph router classifies user messages into these intents:

1. **food_tracking** - Keywords: khana, roti, chawal, eaten, ate, breakfast, lunch, dinner, food, meal
2. **medication** - Keywords: medicine, dawai, tablet, goli, prescription
3. **health_query** - Keywords: blood pressure, sugar, bp, weight, symptoms, diagnosis
4. **recommendation** - Keywords: suggest, recommend, recipe, kya khau, what should i eat
5. **general_chat** - Default intent when no other keywords match

## Prerequisites

- Must be authenticated with valid JWT token
- Use the **Login** request from Auth folder to get access token
- Update `{{accessToken}}` variable after login

## Workflow Pipeline

```
User Input → Normalize → Build Context Query → Retrieve LocusGraph Context
→ Router (classify intent) → Route to Appropriate Agent
→ Store Events → Format Response → Return to User
```

## Agents

- **Food Tracking Agent** - Parses food descriptions and logs meals
- **Medication Agent** - Logs medication intake
- **Health Query Agent** - Answers health questions using profile + vitals context
- **Recommendation Agent** - Provides personalized health/diet recommendations
- **General Chat Agent** - Friendly conversation and emotional support
