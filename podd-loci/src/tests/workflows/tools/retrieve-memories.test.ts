import { describe, it, expect, vi, beforeEach } from "vitest";

const mockRetrieveMemories = vi.fn();

vi.mock("../../../locusgraph/client.js", () => ({
  getClient: () => ({
    retrieveMemories: mockRetrieveMemories,
  }),
  getGraphId: () => "mock-graph-id",
}));

describe("retrieveMemoriesTool", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("is defined with correct name", async () => {
    const { retrieveMemoriesTool } = await import(
      "../../../workflows/tools/retrieve-memories.js"
    );
    expect(retrieveMemoriesTool.name).toBe("retrieve_memories");
  });

  it("returns memories as JSON string when found", async () => {
    mockRetrieveMemories.mockResolvedValue({
      items_found: 2,
      memories: [
        { context_id: "breakfast:eggs", content: "2 scrambled eggs" },
        { context_id: "breakfast:toast", content: "1 toast" },
      ],
    });

    const { retrieveMemoriesTool } = await import(
      "../../../workflows/tools/retrieve-memories.js"
    );
    const result = await retrieveMemoriesTool.invoke({
      query: "what did I eat for breakfast",
      contextIds: ["foods:breakfast"],
      limit: 5,
    });

    expect(result).toContain("breakfast:eggs");
    expect(result).toContain("scrambled eggs");
  });

  it("returns 'No memories found.' when empty", async () => {
    mockRetrieveMemories.mockResolvedValue({
      items_found: 0,
      memories: [],
    });

    const { retrieveMemoriesTool } = await import(
      "../../../workflows/tools/retrieve-memories.js"
    );
    const result = await retrieveMemoriesTool.invoke({
      query: "test query",
      contextIds: [],
      limit: 5,
    });
    expect(result).toBe("No memories found.");
  });

  it("returns string memories directly", async () => {
    mockRetrieveMemories.mockResolvedValue({
      items_found: 1,
      memories: "Some memory text",
    });

    const { retrieveMemoriesTool } = await import(
      "../../../workflows/tools/retrieve-memories.js"
    );
    const result = await retrieveMemoriesTool.invoke({
      query: "test",
      contextIds: [],
      limit: 5,
    });
    expect(result).toBe("Some memory text");
  });

  it("handles API errors gracefully", async () => {
    mockRetrieveMemories.mockRejectedValue(new Error("API is down"));

    const { retrieveMemoriesTool } = await import(
      "../../../workflows/tools/retrieve-memories.js"
    );
    const result = await retrieveMemoriesTool.invoke({
      query: "test",
      contextIds: [],
      limit: 5,
    });
    expect(result).toContain("Failed to retrieve memories");
    expect(result).toContain("API is down");
  });
});
