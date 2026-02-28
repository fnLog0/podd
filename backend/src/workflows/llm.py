"""Shared ChatOpenAI instance for all workflow agents."""

from langchain_openai import ChatOpenAI

from src.config.settings import settings

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4,
    api_key=settings.OPENAI_API_KEY,
)


SYSTEM_BASE = (
    "You are Podd, a friendly and knowledgeable personal health assistant. "
    "You speak in a warm, concise tone. Keep answers short (2-4 sentences) "
    "unless the user asks for detail. "
    "If the user writes in Hindi or Hinglish, reply in the same style."
)


def _format_memories(memories: list[dict]) -> str:
    if not memories:
        return "No prior context available."
    lines = []
    for m in memories[:5]:
        payload = m.get("payload", {})
        kind = payload.get("kind", "unknown")
        data = payload.get("data", {})
        lines.append(f"- [{kind}] {data}")
    return "\n".join(lines)
