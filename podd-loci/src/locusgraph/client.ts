import { LocusGraphClient, type LocusGraphConfig } from "@locusgraph/client";

function getConfig(): LocusGraphConfig {
  const config: LocusGraphConfig = {
    serverUrl: process.env.LOCUSGRAPH_SERVER_URL ?? "https://api-dev.locusgraph.com",
  };
  if (process.env.LOCUSGRAPH_AGENT_SECRET) config.agentSecret = process.env.LOCUSGRAPH_AGENT_SECRET;
  if (process.env.LOCUSGRAPH_GRAPH_ID) config.graphId = process.env.LOCUSGRAPH_GRAPH_ID;
  return config;
}

export function getGraphId(): string {
  return process.env.LOCUSGRAPH_GRAPH_ID ?? "";
}

let _client: LocusGraphClient | null = null;

export function getClient(config?: LocusGraphConfig): LocusGraphClient {
  if (!_client) {
    _client = new LocusGraphClient(config ?? getConfig());
  }
  return _client;
}
