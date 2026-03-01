import { DynamicTool } from "@langchain/core/tools";
import { ChatOpenAI } from "@langchain/openai";
import { resolveOpenAIApiKey, resolveOpenAIModel } from "../../config.js";
import { getClient, getGraphId } from "../../locusgraph/client.js";
import { vitalReadingEvent } from "../../locusgraph/vitals/vital-reading.js";
import type { VitalPayload } from "../../locusgraph/vitals/vital-reading.js";
import {
  getCurrentSessionContextId,
  getCurrentTurnContextId,
} from "../../locusgraph/sessions/tracker.js";
import { vitalsParserPrompt } from "../../prompts/index.js";

function generateReadingName(payload: VitalPayload): string {
  const primary = payload.readings[0];
  if (!primary) return "unknown";

  const now = new Date();
  const dd = String(now.getDate()).padStart(2, "0");
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const yyyy = now.getFullYear();
  const date = `${dd}${mm}${yyyy}`;

  if (payload.vital_type === "blood_pressure") {
    const sys = payload.readings.find((r) => r.label === "systolic")?.value ?? primary.value;
    const dia = payload.readings.find((r) => r.label === "diastolic")?.value ?? 0;
    return `${sys}_${dia}_${date}`;
  }

  const val = String(primary.value).replace(".", "_");
  return `${val}${primary.unit.replace(/[°%]/g, "")}_${date}`;
}

export const logVitalTool = new DynamicTool({
  name: "log_vital",
  description:
    "Log a vital sign reading. Input is a natural language description, e.g. 'My blood pressure is 120/80' or 'I weigh 70 kg'. Parses it with an LLM and stores it in LocusGraph.",
  func: async (input: string) => {
    console.log("\n[log_vital] Input:", input);

    const llm = new ChatOpenAI({ model: resolveOpenAIModel(), temperature: 0, apiKey: resolveOpenAIApiKey() });
    const chain = vitalsParserPrompt.pipe(llm);
    const response = await chain.invoke({ input });

    const content =
      typeof response.content === "string"
        ? response.content
        : JSON.stringify(response.content);

    console.log("\n[log_vital] LLM raw response:", content);

    let parsed: VitalPayload;
    try {
      parsed = JSON.parse(content) as VitalPayload;
    } catch {
      return `Failed to parse vital data from LLM response: ${content}`;
    }

    console.log("\n[log_vital] Parsed payload:", JSON.stringify(parsed, null, 2));

    const readingName = generateReadingName(parsed);
    const related_to = [
      getCurrentSessionContextId(),
      getCurrentTurnContextId(),
    ].filter(Boolean);

    const event = vitalReadingEvent({
      name: readingName,
      vital_type: parsed.vital_type,
      payload: parsed,
      ...(related_to.length ? { related_to } : {}),
    });

    console.log("\n[log_vital] Event to store:", JSON.stringify(event, null, 2));

    try {
      const result = await getClient().storeEvent({
        graph_id: getGraphId(),
        ...event,
        payload: event.payload as unknown as Record<string, unknown>,
      });

      console.log("\n[log_vital] LocusGraph response:", JSON.stringify(result, null, 2));

      const summary = parsed.readings
        .map((r) => `${r.label}: ${r.value} ${r.unit}`)
        .join(", ");
      return `Logged ${parsed.vital_type}: ${summary}. Event ID: ${result.event_id}`;
    } catch (err) {
      console.error("\n[log_vital] Store error:", err);
      return `Failed to store vital event: ${err instanceof Error ? err.message : String(err)}`;
    }
  },
});
