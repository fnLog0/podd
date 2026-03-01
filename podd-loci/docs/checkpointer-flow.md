# LangGraph Checkpointer (MemorySaver) — How It Works

## What is `MemorySaver` (Checkpointer)?

Think of it as a **save file** for your graph's state. Every time the graph completes a step, it saves a snapshot (checkpoint) to memory, tagged with a `thread_id`.

---

## Before (No Checkpointer)

Each `graph.invoke()` was completely independent — like 3 separate strangers talking to the agent:

```
Call 1: "I had eggs for breakfast"
┌─────────────────────────────────────────┐
│  messages: [HumanMessage("I had eggs")] │
│  → agent calls log_food tool            │
│  → agent responds "Logged breakfast!"   │
│  messages: [Human, AI_tool, Tool, AI]   │
└─────────────────────────────────────────┘
          ↓ GONE. State is thrown away.

Call 2: "What did I eat today?"
┌─────────────────────────────────────────┐
│  messages: [HumanMessage("What did I")] │  ← starts EMPTY, no memory of Call 1
│  → agent has NO conversation history    │
│  → "I don't have any information..."    │
└─────────────────────────────────────────┘
          ↓ GONE again.

Call 3: "Am I getting enough protein?"
┌─────────────────────────────────────────┐
│  messages: [HumanMessage("protein?")]   │  ← starts EMPTY again
│  → agent has NO idea what you ate       │
└─────────────────────────────────────────┘
```

**Problem**: The agent has amnesia between calls.

---

## After (With MemorySaver + thread_id)

All calls share the same `thread_id`, so the checkpointer **loads previous state** before each call and **saves new state** after:

```
thread_id: "nasim_u123_session_1"
┌──────────────────────────────────┐
│         CHECKPOINTER             │
│  (MemorySaver - in-memory DB)    │
│                                  │
│  Saves/loads state by thread_id  │
└──────────┬───────────────────────┘
           │
           │
Call 1: "I had eggs for breakfast"
           │
    ┌──────▼──────────────────────────────────────┐
    │  1. Load checkpoint for thread → empty       │
    │  2. Add HumanMessage("I had eggs")           │
    │  3. Agent calls log_food → logs to LocusGraph│
    │  4. Agent responds "Logged breakfast!"       │
    │  5. SAVE checkpoint ━━━━━━━━━━━━━━━━━━━━━┓   │
    │     messages: [Human, AI, Tool, AI]      ┃   │
    └──────────────────────────────────────────┃───┘
                                               ┃
                                          ┌────▼────┐
                                          │ SAVED!  │
                                          │ 4 msgs  │
                                          └────┬────┘
                                               │
Call 2: "What did I eat today?"                │
           │                                   │
    ┌──────▼───────────────────────────────────▼──┐
    │  1. Load checkpoint for thread → 4 messages  │
    │  2. ADD HumanMessage("What did I eat")       │
    │  3. Agent sees FULL history:                 │
    │     - User said "I had eggs"                 │
    │     - It called log_food                     │
    │     - It responded "Logged breakfast"        │
    │     - User now asks "What did I eat"         │
    │  4. Agent answers from conversation memory!  │
    │  5. SAVE checkpoint ━━━━━━━━━━━━━━━━━━━━━┓   │
    │     messages: [H, AI, Tool, AI, H, AI]   ┃   │
    └──────────────────────────────────────────┃───┘
                                               ┃
                                          ┌────▼────┐
                                          │ SAVED!  │
                                          │ 6 msgs  │
                                          └────┬────┘
                                               │
Call 3: "Am I getting enough protein?"         │
           │                                   │
    ┌──────▼───────────────────────────────────▼──┐
    │  1. Load checkpoint → 6 messages             │
    │  2. ADD HumanMessage("protein?")             │
    │  3. Agent sees EVERYTHING:                   │
    │     - Eggs were logged (12g protein)          │
    │     - What user ate today                    │
    │  4. Agent can answer about protein!           │
    │  5. SAVE checkpoint                          │
    └──────────────────────────────────────────────┘
```

---

## The Key Pieces

```
┌──────────────┐     ┌──────────────────┐     ┌───────────────┐
│  graph.ts    │     │  MemorySaver     │     │  index.ts     │
│              │     │                  │     │               │
│  compile({   │────▶│  Stores state    │◀────│  invoke(input,│
│  checkpointer│     │  per thread_id   │     │  { thread_id })│
│  })          │     │                  │     │               │
└──────────────┘     └──────────────────┘     └───────────────┘
                              │
                     Key: thread_id
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        thread "abc"    thread "def"    thread "ghi"
        (conversation1) (conversation2) (conversation3)
              │               │               │
          Own msgs        Own msgs        Own msgs
```

**Same `thread_id`** = same conversation = agent remembers everything.
**Different `thread_id`** = fresh conversation = agent starts clean.

---

## Summary

| Concept | What it does |
|---|---|
| `MemorySaver` | In-memory checkpointer that saves graph state snapshots |
| `thread_id` | Groups multiple `invoke()` calls into one conversation |
| `checkpoint` | A snapshot of the full graph state (messages, context_map, etc.) |
| Without it | Each call is stateless — agent forgets everything |
| With it | Messages accumulate — agent has full conversation history |

`MemorySaver` is for development/testing (lives in RAM, lost on restart). For production you'd swap it with `PostgresSaver`, `RedisSaver`, or `SqliteSaver` — same interface, persistent storage.
