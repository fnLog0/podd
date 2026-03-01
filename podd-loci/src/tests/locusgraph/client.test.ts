import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("getGraphId", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it("returns LOCUSGRAPH_GRAPH_ID from env", async () => {
    process.env.LOCUSGRAPH_GRAPH_ID = "test-graph-id";
    const { getGraphId } = await import("../../locusgraph/client.js");
    expect(getGraphId()).toBe("test-graph-id");
  });

  it("returns empty string when env var is not set", async () => {
    delete process.env.LOCUSGRAPH_GRAPH_ID;
    const { getGraphId } = await import("../../locusgraph/client.js");
    expect(getGraphId()).toBe("");
  });
});

describe("getClient", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it("returns a LocusGraphClient instance", async () => {
    process.env.LOCUSGRAPH_SERVER_URL = "https://test.example.com";
    const { getClient } = await import("../../locusgraph/client.js");
    const client = getClient();
    expect(client).toBeDefined();
    expect(typeof client.storeEvent).toBe("function");
  });

  it("returns the same singleton instance on repeated calls", async () => {
    const { getClient } = await import("../../locusgraph/client.js");
    const a = getClient();
    const b = getClient();
    expect(a).toBe(b);
  });
});
