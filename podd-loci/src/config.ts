export interface PoddConfig {
  locusGraphServerUrl?: string;
  locusGraphAgentSecret?: string;
  locusGraphGraphId?: string;
  openaiApiKey?: string;
  openaiModel?: string;
}

let _config: PoddConfig = {};
let _onReset: (() => void) | null = null;

/**
 * Configure podd-loci with explicit values.
 * Call once before using any other podd-loci function.
 * Falls back to process.env when a value is not set.
 */
export function configure(config: PoddConfig): void {
  _config = { ..._config, ...config };
  _onReset?.();
}

export function getConfig(): PoddConfig {
  return _config;
}

/** @internal */
export function onConfigReset(fn: () => void): void {
  _onReset = fn;
}

function env(key: string): string | undefined {
  try {
    return (globalThis as any).process?.env?.[key];
  } catch {
    return undefined;
  }
}

export function resolveLocusGraphServerUrl(): string {
  return _config.locusGraphServerUrl ?? env("LOCUSGRAPH_SERVER_URL") ?? "https://api-dev.locusgraph.com";
}

export function resolveLocusGraphAgentSecret(): string | undefined {
  return _config.locusGraphAgentSecret ?? env("LOCUSGRAPH_AGENT_SECRET");
}

export function resolveLocusGraphGraphId(): string {
  return _config.locusGraphGraphId ?? env("LOCUSGRAPH_GRAPH_ID") ?? "";
}

export function resolveOpenAIApiKey(): string | undefined {
  return _config.openaiApiKey ?? env("OPENAI_API_KEY");
}

export function resolveOpenAIModel(): string {
  return _config.openaiModel ?? "gpt-4o-mini";
}
