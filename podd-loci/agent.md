# Agent Development Guide — podd-loci

## Project Overview

A health assistant that tracks food intake via LangGraph workflows, stores structured nutrition data in LocusGraph, and provides nutritional guidance through conversational AI.

**Stack:** TypeScript, LangGraph, LangChain, OpenAI, LocusGraph, Vitest

---

## Project Structure

```
src/
├── index.ts                          # Entry point
├── locusgraph/                       # LocusGraph context layer
│   ├── client.ts                     # Singleton client + config from env
│   ├── user.ts                       # User person context + types
│   ├── context.ts                    # Re-exports all context types
│   ├── bootstrap.ts                  # Bootstrap all contexts for a user
│   ├── foods/                        # Food domain contexts
│   │   ├── anchor.ts                 # Root food context (extends person)
│   │   ├── meal.ts                   # Meal-type contexts (breakfast/lunch/dinner/snack)
│   │   ├── food-item.ts             # Individual food item events
│   │   └── index.ts                  # Exports + bootstrapFoodContexts
│   └── sessions/                     # Session/turn tracking
│       ├── anchor.ts                 # Root sessions context (extends person)
│       ├── session.ts                # Individual session contexts
│       ├── turn.ts                   # Turn events within sessions
│       ├── tracker.ts                # In-memory session/turn state
│       └── index.ts                  # Exports + store helpers + title generator
├── prompts/                          # LLM prompt templates
│   ├── system.ts                     # System prompt (3 context variables)
│   ├── food-parser.ts                # Food parsing prompt (JSON schema)
│   └── index.ts                      # Re-exports
├── workflows/                        # LangGraph workflow
│   ├── graph.ts                      # State graph: context → agent → tools → logTurn
│   ├── index.ts                      # Re-exports + runWorkflow helper
│   └── tools/                        # Agent tools
│       ├── log-food-item.ts          # log_food_item tool
│       ├── retrieve-memories.ts      # retrieve_memories tool
│       ├── list-contexts.ts          # list_contexts tool + prefetchContextMap
│       ├── context-formatter.ts      # Categorizes raw contexts into user/food/session
│       └── index.ts                  # Exports all tools
└── tests/                            # Mirrors src/ structure
    ├── locusgraph/
    │   ├── client.test.ts
    │   ├── user.test.ts
    │   ├── foods/
    │   │   ├── anchor.test.ts
    │   │   ├── meal.test.ts
    │   │   └── food-item.test.ts
    │   └── sessions/
    │       ├── anchor.test.ts
    │       ├── session.test.ts
    │       ├── turn.test.ts
    │       ├── tracker.test.ts
    │       └── title-generator.test.ts
    ├── prompts/
    │   ├── system.test.ts
    │   └── food-parser.test.ts
    └── workflows/tools/
        ├── log-food-item.test.ts
        ├── retrieve-memories.test.ts
        ├── list-contexts.test.ts
        └── context-formatter.test.ts
```

---

## Modular Code Rules

### 1. One concern per file

Each file owns a single responsibility. Never mix unrelated logic.

- `anchor.ts` only builds the anchor context ID and event payload
- `meal.ts` only builds meal-type context IDs and event payloads
- `food-item.ts` only builds food item events
- `tracker.ts` only manages in-memory session/turn state

### 2. Pure functions first, side effects last

Separate pure logic from API calls. Every context module follows this pattern:

```
anchor.ts       → pure functions (anchorFoodContext, anchorFoodEventPayload)
meal.ts         → pure functions (mealEventPayload)
food-item.ts    → pure functions (foodItemEvent)
index.ts        → side effects (bootstrapFoodContexts — calls client)
```

Pure functions are trivially testable. Side effects are isolated to `index.ts` or dedicated store helpers.

### 3. Barrel exports via index.ts

Each domain folder has an `index.ts` that re-exports its public API. Consumers import from the folder, not individual files:

```typescript
import { anchorFoodContext, mealEventPayload } from "./foods/index.js";
```

### 4. Types live next to their logic

Interfaces and types are defined in the same file that uses them. Export them via `index.ts` for external consumers. Use `import type` for type-only imports.

### 5. Tools are self-contained

Each tool file in `workflows/tools/` contains:
- Its own imports
- Internal variables (LLM instances, etc.) scoped inside the tool function
- A single exported tool instance

### 6. Prompts are isolated templates

Prompt templates live in `prompts/` and are pure data — no side effects. Each prompt file exports a single `ChatPromptTemplate`.

---

## Adding a New Feature

Follow this checklist every time:

### Step 1: Define the context layer

Create files under `src/locusgraph/<domain>/`:

```
src/locusgraph/vitals/
├── anchor.ts         # anchorVitalsContext, anchorVitalsEventPayload
├── reading.ts        # vitalReadingEvent, types
└── index.ts          # re-exports + bootstrapVitalsContexts
```

Each file must:
- Export pure functions that build context IDs and event payloads
- Export TypeScript interfaces for the payload shapes
- Use `as const` for `event_kind` and `source` literals

### Step 2: Add re-exports to context.ts

Update `src/locusgraph/context.ts` to re-export the new domain's public API.

### Step 3: Create the prompt (if needed)

Add a new prompt template in `src/prompts/` and re-export from `src/prompts/index.ts`.

### Step 4: Create the tool

Add a new tool file in `src/workflows/tools/`:

```typescript
import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";

export const myNewTool = new DynamicStructuredTool({
  name: "tool_name",
  description: "...",
  schema: z.object({ /* ... */ }),
  func: async (input) => {
    // Internal LLM, client calls, etc.
  },
});
```

Then register it in `src/workflows/tools/index.ts`:

```typescript
import { myNewTool } from "./my-new-tool.js";
export { myNewTool } from "./my-new-tool.js";
export const tools = [logFoodItemTool, retrieveMemoriesTool, listContextsTool, myNewTool];
```

### Step 5: Update the system prompt

Add the new tool to the tool list in `src/prompts/system.ts` so the LLM knows it exists.

### Step 6: Update context-formatter (if new context category)

If the new domain introduces a new context prefix pattern, update `src/workflows/tools/context-formatter.ts` to categorize it. Add a new field to `CategorizedContexts`, update `categorizeContexts()`, and update `graph.ts` state + `agentNode` to pass the new variable.

### Step 7: Update bootstrap (if needed)

If the new domain needs contexts pre-created, add a bootstrap function and call it from `src/locusgraph/bootstrap.ts`.

### Step 8: Write tests

See the testing section below.

---

## Testing

### Test file placement

Tests mirror the source structure under `src/tests/`:

```
src/locusgraph/foods/anchor.ts    →    src/tests/locusgraph/foods/anchor.test.ts
src/workflows/tools/list-contexts.ts  →  src/tests/workflows/tools/list-contexts.test.ts
```

### Writing tests

**Pure function tests** — no mocking needed:

```typescript
import { describe, it, expect } from "vitest";
import { anchorFoodContext } from "../../../locusgraph/foods/anchor.js";

describe("anchorFoodContext", () => {
  it("returns correct context id", () => {
    expect(anchorFoodContext("nasim", "u123")).toBe("nasim_u123:foods");
  });
});
```

**Tests with external dependencies** — mock the client and LLMs:

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../../../locusgraph/client.js", () => ({
  getClient: () => ({
    storeEvent: vi.fn().mockResolvedValue({ event_id: "evt_mock" }),
    listContexts: vi.fn().mockResolvedValue({ contexts: [] }),
    retrieveMemories: vi.fn().mockResolvedValue({ memories: [] }),
  }),
  getGraphId: () => "mock-graph-id",
}));

vi.mock("@langchain/openai", () => ({
  ChatOpenAI: class {
    bindTools() { return this; }
  },
}));
```

**Stateful module tests** — reset state in `beforeEach`:

```typescript
beforeEach(() => {
  setCurrentSession("", 0);
});
```

**Time-dependent tests** — use fake timers:

```typescript
import { vi, afterEach } from "vitest";

afterEach(() => vi.useRealTimers());

it("formats date correctly", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-03-01T10:00:00Z"));
  // ...
});
```

### What every test file must cover

1. **Return shape** — correct `context_id`, `event_kind`, `source`, `extends`
2. **Edge cases** — empty inputs, missing optional fields, boundary values
3. **Error handling** — API failures return graceful error messages
4. **Multiple inputs** — use `it.each()` for parameterized tests (e.g., all 4 meal types)

---

## Commands

### Type check

```bash
npx tsc --noEmit
```

Run this before every commit. Catches type errors, missing exports, wrong imports.

### Run tests

```bash
pnpm test            # Single run
pnpm test:watch      # Watch mode (re-runs on file changes)
```

### Run a specific test file

```bash
npx vitest run src/tests/locusgraph/foods/anchor.test.ts
```

### Start the app

```bash
pnpm start
```

---

## Pre-Commit Checklist

Before committing any change, run these in order:

```bash
# 1. Type check — catch compile errors
npx tsc --noEmit

# 2. Run all tests — catch regressions
pnpm test

# 3. Verify no unused exports or broken imports
#    (tsc --noEmit covers this, but double-check new index.ts re-exports)
```

Every new feature must have:
- [ ] Pure functions with no side effects where possible
- [ ] Types exported via barrel `index.ts`
- [ ] Matching test file under `src/tests/`
- [ ] All existing tests still passing
- [ ] System prompt updated (if new tool added)
- [ ] Context formatter updated (if new context category added)

---

## Context Hierarchy Reference

```
person:{name}_{user_id}                              ← user (user.ts)
  ├── {name}_{user_id}:foods                         ← food anchor (foods/anchor.ts)
  │     ├── foods:breakfast                          ← meal type (foods/meal.ts)
  │     │     ├── breakfast:{food_name}              ← food item (foods/food-item.ts)
  │     │     └── breakfast:{food_name}
  │     ├── foods:lunch
  │     ├── foods:dinner
  │     └── foods:snack
  └── {name}_{user_id}:sessions                      ← session anchor (sessions/anchor.ts)
        ├── session:{title}_{date}                   ← session (sessions/session.ts)
        │     ├── turn:{title}_{date}_t1             ← turn (sessions/turn.ts)
        │     └── turn:{title}_{date}_t2
        └── session:{title}_{date}
```

The system prompt receives these as three categorized sections:
- `{user_contexts}` — person contexts
- `{food_contexts}` — food anchor → meal types → food items
- `{session_contexts}` — session anchor → sessions → turns
