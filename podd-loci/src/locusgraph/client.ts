import { LocusGraphClient, type LocusGraphConfig } from "@locusgraph/client";
import {
  resolveLocusGraphServerUrl,
  resolveLocusGraphAgentSecret,
  resolveLocusGraphGraphId,
  onConfigReset,
} from "../config.js";

function buildConfig(): LocusGraphConfig {
  const config: LocusGraphConfig = {
    serverUrl: resolveLocusGraphServerUrl(),
  };
  const secret = resolveLocusGraphAgentSecret();
  if (secret) config.agentSecret = secret;
  const graphId = resolveLocusGraphGraphId();
  if (graphId) config.graphId = graphId;
  return config;
}

export function getGraphId(): string {
  return resolveLocusGraphGraphId();
}

let _client: LocusGraphClient | null = null;

onConfigReset(() => {
  _client = null;
});

export function getClient(config?: LocusGraphConfig): LocusGraphClient {
  if (!_client) {
    _client = new LocusGraphClient(config ?? buildConfig());
  }
  return _client;
}
