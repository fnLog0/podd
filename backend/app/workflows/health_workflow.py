from typing import Literal

from langgraph.graph import StateGraph, END

from app.workflows.state import PoddState
from app.workflows.nodes.normalize import normalize_input
from app.workflows.nodes.context import build_context_query, retrieve_locus_context
from app.workflows.nodes.router import router_intent, route_to_agent
from app.workflows.nodes.agents.food import agent_food_tracking
from app.workflows.nodes.agents.medication import agent_medication
from app.workflows.nodes.agents.health_query import agent_health_query
from app.workflows.nodes.agents.recommendation import agent_recommendation
from app.workflows.nodes.agents.general_chat import agent_general_chat
from app.workflows.nodes.memory import store_events
from app.workflows.nodes.response import format_response

builder = StateGraph(PoddState)

builder.add_node("normalize_input", normalize_input)
builder.add_node("build_context_query", build_context_query)
builder.add_node("retrieve_locus_context", retrieve_locus_context)
builder.add_node("router_intent", router_intent)
builder.add_node("agent_food_tracking", agent_food_tracking)
builder.add_node("agent_medication", agent_medication)
builder.add_node("agent_health_query", agent_health_query)
builder.add_node("agent_recommendation", agent_recommendation)
builder.add_node("agent_general_chat", agent_general_chat)
builder.add_node("store_events", store_events)
builder.add_node("format_response", format_response)

builder.set_entry_point("normalize_input")

builder.add_edge("normalize_input", "build_context_query")
builder.add_edge("build_context_query", "retrieve_locus_context")
builder.add_edge("retrieve_locus_context", "router_intent")

builder.add_conditional_edges(
    "router_intent",
    route_to_agent,
    {
        "agent_food_tracking": "agent_food_tracking",
        "agent_medication": "agent_medication",
        "agent_health_query": "agent_health_query",
        "agent_recommendation": "agent_recommendation",
        "agent_general_chat": "agent_general_chat",
    },
)

for agent_node in [
    "agent_food_tracking",
    "agent_medication",
    "agent_health_query",
    "agent_recommendation",
    "agent_general_chat",
]:
    builder.add_edge(agent_node, "store_events")

builder.add_edge("store_events", "format_response")
builder.add_edge("format_response", END)

graph = builder.compile()


async def run_workflow(
    user_id: str,
    user_text: str,
    locale: str = "en-IN",
    channel: Literal["text", "voice"] = "text",
) -> dict:
    initial_state: PoddState = {
        "user_id": user_id,
        "user_text": user_text,
        "locale": locale,
        "channel": channel,
        "pending_events": [],
        "errors": [],
        "flags": {},
    }
    result = await graph.ainvoke(initial_state)
    return result
