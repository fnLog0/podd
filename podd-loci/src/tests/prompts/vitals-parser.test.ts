import { describe, it, expect } from "vitest";
import { vitalsParserPrompt } from "../../prompts/vitals-parser.js";

describe("vitalsParserPrompt", () => {
  it("is a ChatPromptTemplate", () => {
    expect(vitalsParserPrompt).toBeDefined();
    expect(typeof vitalsParserPrompt.formatMessages).toBe("function");
  });

  it("accepts input variable and renders it", async () => {
    const messages = await vitalsParserPrompt.formatMessages({
      input: "My blood pressure is 120/80",
    });
    expect(messages).toHaveLength(2);
    const humanMsg = messages[1]!;
    expect(String(humanMsg.content)).toContain("blood pressure is 120/80");
  });

  it("system message describes the JSON schema", async () => {
    const messages = await vitalsParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("vital_type");
    expect(systemMsg).toContain("readings");
    expect(systemMsg).toContain("measured_at");
    expect(systemMsg).toContain("context");
    expect(systemMsg).toContain("notes");
  });

  it("system message lists all vital types", async () => {
    const messages = await vitalsParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("blood_pressure");
    expect(systemMsg).toContain("heart_rate");
    expect(systemMsg).toContain("weight");
    expect(systemMsg).toContain("blood_sugar");
    expect(systemMsg).toContain("temperature");
    expect(systemMsg).toContain("oxygen_saturation");
  });

  it("system message lists valid units", async () => {
    const messages = await vitalsParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("mmHg");
    expect(systemMsg).toContain("bpm");
    expect(systemMsg).toContain("kg");
    expect(systemMsg).toContain("mg/dL");
  });

  it("instructs to return only valid JSON", async () => {
    const messages = await vitalsParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("ONLY valid JSON");
  });

  it("has specific blood pressure rules for systolic/diastolic", async () => {
    const messages = await vitalsParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("systolic");
    expect(systemMsg).toContain("diastolic");
  });
});
