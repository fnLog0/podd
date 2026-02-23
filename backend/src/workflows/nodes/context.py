from src.services.locusgraph.service import locusgraph_service
from src.workflows.state import PoddState


def build_context_query(state: PoddState) -> dict:
    user_id = state.get("user_id", "")
    text = state.get("user_text", "")
    return {"context_query": f"{text} person:{user_id}"}


def retrieve_locus_context(state: PoddState) -> dict:
    query = state.get("context_query", "")
    user_id = state.get("user_id", "")

    results = locusgraph_service.retrieve_context(
        query=query,
        limit=5,
        context_ids=[f"person:{user_id}"],
    )

    return {"lg_context": {"memories": results, "user_id": user_id}}
