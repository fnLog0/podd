import { describe, it, expect } from "vitest";
import { toToon } from "../../../workflows/tools/toon-encoder.js";

describe("toToon", () => {
  it("encodes an object to TOON format", () => {
    const result = toToon({ name: "eggs", calories: 150 });
    expect(result).toContain("eggs");
    expect(result).toContain("150");
    expect(result).not.toContain("{");
  });

  it("encodes an array of objects", () => {
    const result = toToon([
      { id: 1, name: "Alice" },
      { id: 2, name: "Bob" },
    ]);
    expect(result).toContain("Alice");
    expect(result).toContain("Bob");
  });

  it("returns empty string for null/undefined", () => {
    expect(toToon(null)).toBe("");
    expect(toToon(undefined)).toBe("");
  });

  it("returns string values as-is", () => {
    expect(toToon("hello world")).toBe("hello world");
  });

  it("falls back to JSON for unencodable data", () => {
    const circular: Record<string, unknown> = {};
    const result = toToon(42);
    expect(result).toContain("42");
  });

  it("produces output shorter than JSON for structured data", () => {
    const data = {
      users: [
        { id: 1, name: "Alice", role: "admin" },
        { id: 2, name: "Bob", role: "user" },
        { id: 3, name: "Carol", role: "user" },
      ],
    };
    const toon = toToon(data);
    const json = JSON.stringify(data, null, 2);
    expect(toon.length).toBeLessThan(json.length);
  });
});
