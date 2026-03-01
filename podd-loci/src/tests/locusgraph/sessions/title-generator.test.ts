import { describe, it, expect, vi, afterEach } from "vitest";
import { generateSessionTitle } from "../../../locusgraph/sessions/index.js";

describe("generateSessionTitle", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("creates a slug from the first 5 words + date", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-03-01T10:00:00Z"));

    const title = generateSessionTitle(
      "I had 2 scrambled eggs and a cup of green tea",
    );
    expect(title).toBe("i_had_2_scrambled_eggs_01032026");
  });

  it("strips non-alphanumeric characters", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-03-01T10:00:00Z"));

    const title = generateSessionTitle("What's my protein intake?");
    expect(title).toBe("whats_my_protein_intake_01032026");
  });

  it("limits to 5 words maximum", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-03-01T10:00:00Z"));

    const title = generateSessionTitle("one two three four five six seven");
    expect(title).toBe("one_two_three_four_five_01032026");
  });

  it("handles single word input", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-12-25T10:00:00Z"));

    const title = generateSessionTitle("hello");
    expect(title).toBe("hello_25122026");
  });

  it("handles messages with only special characters", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-01-15T10:00:00Z"));

    const title = generateSessionTitle("!!!");
    expect(title).toBe("_15012026");
  });

  it("pads single-digit day and month with zeros", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-01-05T10:00:00Z"));

    const title = generateSessionTitle("test");
    expect(title).toBe("test_05012026");
  });
});
