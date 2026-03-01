import { describe, it, expect } from "vitest";
import { systemPrompt } from "../../prompts/system.js";

const defaultVars = {
  user_contexts: "- person:nasim_u123",
  food_contexts: "- nasim_u123:foods (anchor)\n  - foods:breakfast",
  session_contexts: "- nasim_u123:sessions (anchor)",
};

describe("systemPrompt", () => {
  it("is a ChatPromptTemplate", () => {
    expect(systemPrompt).toBeDefined();
    expect(typeof systemPrompt.formatMessages).toBe("function");
  });

  it("renders user_contexts variable", async () => {
    const messages = await systemPrompt.formatMessages(defaultVars);
    const content = String(messages[0]!.content);
    expect(content).toContain("person:nasim_u123");
  });

  it("renders food_contexts variable", async () => {
    const messages = await systemPrompt.formatMessages(defaultVars);
    const content = String(messages[0]!.content);
    expect(content).toContain("nasim_u123:foods (anchor)");
    expect(content).toContain("foods:breakfast");
  });

  it("renders session_contexts variable", async () => {
    const messages = await systemPrompt.formatMessages(defaultVars);
    const content = String(messages[0]!.content);
    expect(content).toContain("nasim_u123:sessions (anchor)");
  });

  it("has separate sections for each context category", async () => {
    const messages = await systemPrompt.formatMessages(defaultVars);
    const content = String(messages[0]!.content);
    expect(content).toContain("## User Contexts");
    expect(content).toContain("## Food Contexts");
    expect(content).toContain("## Session & Turn Contexts");
  });

  it("mentions all three tools in the prompt", async () => {
    const messages = await systemPrompt.formatMessages(defaultVars);
    const content = String(messages[0]!.content);
    expect(content).toContain("log_food_item");
    expect(content).toContain("retrieve_memories");
    expect(content).toContain("list_contexts");
  });

  it("prompt identifies as health assistant", async () => {
    const messages = await systemPrompt.formatMessages(defaultVars);
    const content = String(messages[0]!.content);
    expect(content).toContain("health assistant");
  });

  it("instructs agent to always search before saying no records", async () => {
    const messages = await systemPrompt.formatMessages(defaultVars);
    const content = String(messages[0]!.content);
    expect(content).toContain("MUST call retrieve_memories");
    expect(content).toContain("NEVER say");
  });

  it("tells agent food data persists across sessions", async () => {
    const messages = await systemPrompt.formatMessages(defaultVars);
    const content = String(messages[0]!.content);
    expect(content).toContain("persists across sessions");
  });
});
