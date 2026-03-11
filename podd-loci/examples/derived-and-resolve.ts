/**
 * Example: DerivedFrom link + resolution (rule → violation → resolve).
 *
 * Uses podd-loci config and LocusGraph client. Demonstrates storing a rule,
 * a constraint violation that relates to it, then resolving the rule context
 * to its locus so links point at the right memory.
 *
 * Run: npx tsx examples/derived-and-resolve.ts
 *
 * Env (same as demo):
 *   LOCUSGRAPH_SERVER_URL   - Server base URL (optional)
 *   LOCUSGRAPH_AGENT_SECRET - Agent bearer token (required)
 *   LOCUSGRAPH_GRAPH_ID     - Graph ID (optional; if missing, creates a graph first)
 */

import "dotenv/config";
import {
  configure,
  getClient,
  getGraphId,
} from "../src/index.js";
import {
  resolveLocusGraphServerUrl,
  resolveLocusGraphAgentSecret,
} from "../src/config.js";

configure({
  locusGraphServerUrl: process.env.LOCUSGRAPH_SERVER_URL,
  locusGraphAgentSecret: process.env.LOCUSGRAPH_AGENT_SECRET,
  locusGraphGraphId: process.env.LOCUSGRAPH_GRAPH_ID,
});

const RULE_CONTEXT_ID = "rule:max_calories_per_meal";
const VIOLATION_CONTEXT_ID = "constraint_violation:breakfast_over_limit";

async function api<T>(
  path: string,
  opts: { method?: string; body?: object } = {}
): Promise<{ data?: T; success?: boolean; error?: string }> {
  const baseUrl = resolveLocusGraphServerUrl().replace(/\/$/, "");
  const token = resolveLocusGraphAgentSecret();
  if (!token) throw new Error("LOCUSGRAPH_AGENT_SECRET is required");

  const res = await fetch(`${baseUrl}${path}`, {
    method: opts.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((json?.error?.message as string) ?? res.statusText);
  return json;
}

async function main() {
  if (!resolveLocusGraphAgentSecret()) {
    console.error("Set LOCUSGRAPH_AGENT_SECRET (and optionally LOCUSGRAPH_GRAPH_ID, LOCUSGRAPH_SERVER_URL).");
    process.exit(1);
  }

  const client = getClient();
  let graphId = getGraphId();

  if (!graphId) {
    const createGraph = await api<{ graph_id: string }>("/v1/graphs", {
      method: "POST",
      body: {
        name: "podd-derived-resolve-example",
        description: "Example: rule + violation + resolve",
      },
    });
    graphId = createGraph.data?.graph_id ?? "";
    if (!graphId) throw new Error("Failed to create graph");
    console.log("Created graph:", graphId);
    // Note: getGraphId() still returns the env value; we use local graphId below.
  }

  // Step 1: Store a rule (creates locus + DerivedFrom link to context rule:max_calories_per_meal)
  const ruleResult = await client.storeEvent({
    graph_id: graphId,
    event_kind: "rule",
    context_id: RULE_CONTEXT_ID,
    source: "validator",
    payload: {
      kind: "rule",
      data: {
        name: "max_calories_per_meal",
        value: "No single meal should exceed 800 calories.",
      },
    },
  });
  const ruleLocusId = (ruleResult as { event_id?: string }).event_id ?? (ruleResult as { data?: { event_id?: string } }).data?.event_id;
  if (!ruleLocusId) throw new Error("Step 1 failed: no event_id");
  console.log("Step 1 – Rule stored, locus_id:", ruleLocusId);

  // Step 2: Store a constraint_violation that relates to the rule (unresolved link to rule)
  const violationResult = await client.storeEvent({
    graph_id: graphId,
    event_kind: "constraint_violation",
    context_id: VIOLATION_CONTEXT_ID,
    source: "agent",
    related_to: [RULE_CONTEXT_ID],
    payload: {
      kind: "constraint_violation",
      data: {
        rule: "max_calories_per_meal",
        expected: "meal ≤ 800 cal",
        actual: "breakfast logged at 950 cal",
      },
    },
  });
  const violationLocusId = (violationResult as { event_id?: string }).event_id ?? (violationResult as { data?: { event_id?: string } }).data?.event_id;
  if (!violationLocusId) throw new Error("Step 2 failed: no event_id");
  console.log("Step 2 – Violation stored, locus_id:", violationLocusId);

  // Step 3: Resolve "rule:max_calories_per_meal" → ruleLocusId (so related_to links point at the rule locus)
  const resolveRes = await api<{ links_resolved: number; success: boolean }>(
    `/v1/resolve/${graphId}`,
    {
      method: "POST",
      body: {
        context_id: RULE_CONTEXT_ID,
        locus_id: ruleLocusId,
      },
    }
  );
  console.log(
    "Step 3 – Resolve:",
    resolveRes.data?.links_resolved ?? 0,
    "links resolved, success:",
    resolveRes.data?.success
  );

  // Step 4: Unresolved overview (rule:max_calories_per_meal should be resolved now)
  const unresolvedRes = await api<{
    total_unresolved_links: number;
    context_ids: Array<{ context_id: string; link_count: number }>;
  }>(`/v1/resolve/${graphId}/unresolved`);
  console.log(
    "Step 4 – Unresolved overview:",
    unresolvedRes.data?.total_unresolved_links ?? 0,
    "total; contexts:",
    unresolvedRes.data?.context_ids ?? []
  );

  console.log("\nDone. Rule locus:", ruleLocusId, "| Violation locus:", violationLocusId);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
