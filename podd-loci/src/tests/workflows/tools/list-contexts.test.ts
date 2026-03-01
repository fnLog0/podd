import { describe, it, expect, vi, beforeEach } from "vitest";

const mockListContexts = vi.fn();

vi.mock("../../../locusgraph/client.js", () => ({
  getClient: () => ({
    listContexts: mockListContexts,
  }),
  getGraphId: () => "mock-graph-id",
}));

describe("listContextsTool", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("is defined with correct name", async () => {
    const { listContextsTool } = await import(
      "../../../workflows/tools/list-contexts.js"
    );
    expect(listContextsTool.name).toBe("list_contexts");
  });

  it("returns contexts as TOON-encoded string", async () => {
    const mockContexts = {
      contexts: [
        { context_id: "foods:breakfast", context_type: "food" },
        { context_id: "foods:lunch", context_type: "food" },
      ],
    };
    mockListContexts.mockResolvedValue(mockContexts);

    const { listContextsTool } = await import(
      "../../../workflows/tools/list-contexts.js"
    );
    const result = await listContextsTool.invoke({
      context_type: "",
      context_name: "",
      limit: 50,
    });

    expect(result).toContain("foods:breakfast");
    expect(result).toContain("foods:lunch");
    expect(result).toContain("food");
  });

  it("handles API errors gracefully", async () => {
    mockListContexts.mockRejectedValue(new Error("Network error"));

    const { listContextsTool } = await import(
      "../../../workflows/tools/list-contexts.js"
    );
    const result = await listContextsTool.invoke({
      context_type: "",
      context_name: "",
      limit: 50,
    });
    expect(result).toContain("Failed to list contexts");
    expect(result).toContain("Network error");
  });
});

describe("prefetchContextMap", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches types then contexts and returns categorized map", async () => {
    mockListContexts
      .mockResolvedValueOnce({
        context_types: [
          { context_type: "person", count: 1 },
          { context_type: "foods", count: 2 },
        ],
      })
      .mockResolvedValueOnce({
        contexts: [{ context_id: "person:nasim_u123" }],
      })
      .mockResolvedValueOnce({
        contexts: [
          { context_id: "foods:breakfast" },
          { context_id: "foods:lunch" },
        ],
      });

    const { prefetchContextMap } = await import(
      "../../../workflows/tools/list-contexts.js"
    );
    const result = await prefetchContextMap();

    expect(result.user_contexts).toContain("person:nasim_u123");
    expect(result.food_contexts).toContain("foods:breakfast");
    expect(result.food_contexts).toContain("foods:lunch");
  });

  it("returns fallback when no context types found", async () => {
    mockListContexts.mockResolvedValueOnce({
      context_types: [],
    });

    const { prefetchContextMap } = await import(
      "../../../workflows/tools/list-contexts.js"
    );
    const result = await prefetchContextMap();

    expect(result.user_contexts).toBe("No user contexts available.");
    expect(result.food_contexts).toBe("No food contexts available.");
    expect(result.vitals_contexts).toBe("No vitals contexts available.");
    expect(result.session_contexts).toBe("No session contexts available.");
  });

  it("returns fallback messages on error", async () => {
    mockListContexts.mockRejectedValue(new Error("fail"));

    const { prefetchContextMap } = await import(
      "../../../workflows/tools/list-contexts.js"
    );
    const result = await prefetchContextMap();

    expect(result.user_contexts).toBe("No user contexts available.");
    expect(result.food_contexts).toBe("No food contexts available.");
    expect(result.vitals_contexts).toBe("No vitals contexts available.");
    expect(result.session_contexts).toBe("No session contexts available.");
  });
});
