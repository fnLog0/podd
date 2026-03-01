import { describe, it, expect } from "vitest";
import { foodParserPrompt } from "../../prompts/food-parser.js";

describe("foodParserPrompt", () => {
  it("is a ChatPromptTemplate", () => {
    expect(foodParserPrompt).toBeDefined();
    expect(typeof foodParserPrompt.formatMessages).toBe("function");
  });

  it("accepts input variable and renders it", async () => {
    const messages = await foodParserPrompt.formatMessages({
      input: "2 scrambled eggs and toast",
    });
    expect(messages).toHaveLength(2);
    const humanMsg = messages[1]!;
    expect(String(humanMsg.content)).toContain("2 scrambled eggs and toast");
  });

  it("system message describes the JSON schema", async () => {
    const messages = await foodParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("meal_type");
    expect(systemMsg).toContain("items");
    expect(systemMsg).toContain("macros");
    expect(systemMsg).toContain("calories");
    expect(systemMsg).toContain("protein_g");
    expect(systemMsg).toContain("carbs_g");
    expect(systemMsg).toContain("fat_g");
  });

  it("system message lists valid meal types", async () => {
    const messages = await foodParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("breakfast");
    expect(systemMsg).toContain("lunch");
    expect(systemMsg).toContain("dinner");
    expect(systemMsg).toContain("snack");
  });

  it("system message lists valid units", async () => {
    const messages = await foodParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("piece");
    expect(systemMsg).toContain("serving");
    expect(systemMsg).toContain("cup");
  });

  it("instructs to return only valid JSON", async () => {
    const messages = await foodParserPrompt.formatMessages({
      input: "test",
    });
    const systemMsg = String(messages[0]!.content);
    expect(systemMsg).toContain("ONLY valid JSON");
  });
});
