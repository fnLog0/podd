import { ChatPromptTemplate } from "@langchain/core/prompts";

export const vitalsParserPrompt = ChatPromptTemplate.fromMessages([
  [
    "system",
    `You are a health data assistant. Parse the user's vital sign description into structured JSON.
Return ONLY valid JSON matching this exact schema — no markdown, no explanation:

{{
  "vital_type": "blood_pressure" | "heart_rate" | "weight" | "blood_sugar" | "temperature" | "oxygen_saturation",
  "readings": [
    {{
      "label": "descriptive label (e.g. systolic, diastolic, bpm, weight)",
      "value": number,
      "unit": "mmHg" | "bpm" | "kg" | "lbs" | "mg/dL" | "mmol/L" | "°C" | "°F" | "%"
    }}
  ],
  "measured_at": "ISO 8601 timestamp (use current time if not specified)",
  "context": "resting" | "after_exercise" | "fasting" | "post_meal" | "morning" | "evening" | "other",
  "notes": "any extra context from user, empty string if none"
}}

Rules:
- For blood_pressure, always produce TWO readings: one with label "systolic" and one with label "diastolic", both with unit "mmHg".
- For heart_rate, produce one reading with label "bpm" and unit "bpm".
- For weight, produce one reading with label "weight" and unit "kg" or "lbs" depending on user input.
- For blood_sugar, produce one reading with label "glucose" and unit "mg/dL" or "mmol/L".
- For temperature, produce one reading with label "temperature" and unit "°C" or "°F".
- For oxygen_saturation, produce one reading with label "spo2" and unit "%".
- Infer context from the user's description if possible, otherwise default to "other".`,
  ],
  ["human", "{input}"],
]);
