import json

from langchain_core.messages import SystemMessage, HumanMessage

from src.workflows.state import PoddState
from src.workflows.llm import llm

SYSTEM_PROMPT = """\
You are a preprocessing step for a health assistant called Podd.

Given a raw user message and their user_id, produce a JSON object with these fields:

1. "normalized_text": Clean version of the user message.
   - Translate any Hindi/Hinglish words to English
   - Translate Hindi units (मिलीलीटर→ml, ग्राम→grams, किलो→kg, चम्मच→tsp, लीटर→liters)
   - Remove filler words (um, uh, like, acha, haan, toh, basically, etc.)
   - Fix obvious typos
   - Keep the core meaning intact

2. "context_query": A concise semantic search query to retrieve relevant past \
memories from the user's health graph. Focus on the key medical/health entities \
mentioned (foods, medications, vitals, symptoms, conditions).
   - Example: user says "I ate roti and dal" → context_query: "food intake roti dal nutrition"
   - Example: user says "my BP is high today" → context_query: "blood pressure vitals readings"
   - Example: user says "took crocin tablet" → context_query: "medication crocin dosage schedule"

3. "context_ids": A list of LocusGraph context_id prefixes to filter retrieval. \
Pick ONLY the relevant ones from this list:
   - "food_log:" — for food/nutrition mentions
   - "vitals:" — for BP, sugar, weight, heart rate
   - "medication:" — for medicine/tablet/prescription mentions
   - "medication_schedule:" — for dosage schedules
   - "medication_log:" — for medication intake history
   - "sleep_log:" — for sleep mentions
   - "exercise_log:" — for exercise/workout mentions
   - "mood_log:" — for mood/emotion mentions
   - "water_log:" — for water/hydration mentions
   - "appointment:" — for doctor/appointment mentions
   - "meditation_session:" — for meditation mentions
   Always include "profile:" for user profile context.
   For general chat with no specific domain, return only ["profile:"].

Respond with ONLY valid JSON, no markdown, no explanation.

Example input: "um acha maine subah 2 roti aur dal khayi"
Example output:
{"normalized_text": "I ate 2 roti and dal in the morning", "context_query": "food intake roti dal morning breakfast nutrition", "context_ids": ["profile:", "food_log:"]}
"""


async def normalize_input(state: PoddState) -> dict:
    user_text = state.get("user_text", "").strip()
    user_id = state.get("user_id", "")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"user_id: {user_id}\nmessage: {user_text}"),
    ]
    response = await llm.ainvoke(messages)
    raw = response.content.strip()

    # Strip markdown code fences if the LLM wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "normalized_text": user_text,
            "user_text": user_text,
            "context_query": f"{user_text} person:{user_id}",
            "context_ids": [f"person:{user_id}"],
        }

    normalized = parsed.get("normalized_text", user_text)
    context_query = parsed.get("context_query", normalized)
    context_ids = parsed.get("context_ids", ["profile:"])

    # Always scope to the user
    context_ids_scoped = [f"person:{user_id}"] + [
        cid for cid in context_ids if cid != "profile:"
    ]
    if "profile:" in context_ids:
        context_ids_scoped.append(f"profile:{user_id}")

    return {
        "normalized_text": normalized,
        "user_text": normalized,
        "context_query": f"{context_query} person:{user_id}",
        "context_ids": context_ids_scoped,
    }
