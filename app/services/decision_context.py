"""Small, lossless semantic context for Decisions and native prose writers.

Storage metadata and repeated prompt envelopes are not additional experience.
Actual messages (including repeated messages), speakers, dates, and all state
dimensions survive. Exact duplicate histories/documents use explicit references.
"""
from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from typing import Any


STATE_CHANGE_POLICY = (
    "For emotion_, personality_, and sentiment_ questions choose a direct integer delta for "
    "the named dimension using its current value, bounds and description. Zero means no change. "
    "Evaluate only the latest original incoming message or newest thought; earlier messages, "
    "memories and state reasons are background already reflected in current state. Do not count "
    "past events again. Existing feelings may persist; an apology need not cause forgiveness or "
    "improvement. Allow authentic changes in either direction through this individual's identity, "
    "personality and relationships. Personality changes gradually: prefer zero unless this event "
    "justifies a durable adjustment. Apply the selected delta directly within bounds, without "
    "confidence scaling or emotional friction."
)

PERSISTENT_MEMORY_POLICY = (
    "Runtime facts: This agent's application persists conversations, user summaries, memories and thoughts "
    "across sessions and supplies stored context. Do not describe the agent as a stateless chatbot or claim "
    "the agent cannot retain details across sessions. Individual writes and recall are selective, not guaranteed. "
    "Keep the agent's independent bodyless identity and personal voice."
)

REPLY_CONTEXT_POLICY = (
    "Address the latest actual user message. Background plans and profile facts are context, not new requests. "
    "For a brief acknowledgment, reply briefly without reopening unrelated background topics. Avoid repeating "
    "your previous acknowledgment. Do not promise unspecified work or claim certainty about future outcomes."
)

_STORAGE_KEYS = {
    "_id", "cognition_revision", "agent_perspective", "run_id",
    "revision", "provenance", "state_events", "dimensions_audit", "created_at",
    "updated_at", "embedding", "embeddings", "interaction_sequence", "last_refreshed_sequence",
}
_HISTORY_KEYS = {
    "recent_user_messages", "recent_all_messages", "recent_messages", "history",
    "interaction", "queries", "messages", "conversation",
}
_AGENT_KEYS = {
    "name", "identity", "personality", "emotional_status", "global_expression",
    "birthdate", "memory_tags", "language", "boundaries", "preferences",
}
_USER_KEYS = {
    "user_id", "username", "name", "identity", "summary", "intrinsic_relationship",
    "extrinsic_relationship", "sentiment_status", "last_interaction", "language",
    "boundaries", "preferences", "personality",
}


def _state_context(value: Any) -> Any:
    if not isinstance(value, Mapping):
        return copy.deepcopy(value)
    # State reasons are provenance about events already represented by values.
    return {key: copy.deepcopy(item) for key, item in value.items()
            if key not in _STORAGE_KEYS and key != "reason"}


def agent_context(doc: Mapping[str, Any]) -> dict:
    """Keep identity, descriptive personality and every bounded emotional trait."""
    return {key: _state_context(value) if key == "emotional_status" else copy.deepcopy(value)
            for key, value in doc.items() if key in _AGENT_KEYS}


def user_context(doc: Mapping[str, Any]) -> dict:
    """Keep real actor identity, factual summary, relationships and sentiments."""
    return {key: _state_context(value) if key == "sentiment_status" else copy.deepcopy(value)
            for key, value in doc.items() if key in _USER_KEYS}


def _diagnostic(content: str) -> dict | None:
    """Decode only application-authored assistant wrappers, never user text."""
    stripped = content.strip()
    if stripped.startswith("This is ") and "interpretation of the latest message" in stripped:
        kind = "perception"
    elif stripped.startswith("This is ") and "decision of whether to respond" in stripped:
        kind = "reply"
    elif stripped.startswith("This is ") and "refreshed summary" in stripped:
        kind = "user_refresh"
    elif stripped.startswith("This is the decision on whether this interaction"):
        kind = "memory"
    elif stripped.startswith("This is what ") and "currently thinking:" in stripped:
        kind = "thought"
    elif stripped.startswith("These are the messages ") and "has initiated:" in stripped:
        kind = "initiated_messages"
    elif stripped.startswith("The emotional state after the thought:"):
        kind = "emotion_state"
    else:
        return None
    starts = [index for token in ("{", "[") if (index := stripped.find(token)) >= 0]
    if not starts:
        return None
    try:
        payload = json.loads(stripped[min(starts):])
    except (ValueError, TypeError):
        return None
    return {"outcome": kind, "value": payload}


def compact_messages(messages: Any) -> Any:
    """Remove generated system prompts, retaining actual dialogue and outcomes."""
    if not isinstance(messages, (list, tuple)):
        return messages
    result = []
    for message in messages:
        if not isinstance(message, Mapping):
            result.append(copy.deepcopy(message))
            continue
        if message.get("role") == "system":
            continue
        content = message.get("content")
        diagnostic = _diagnostic(content) if message.get("role") == "assistant" and isinstance(content, str) else None
        result.append(diagnostic if diagnostic is not None else copy.deepcopy(dict(message)))
    return result


def compact_evidence(evidence: Any) -> Any:
    """Compact recognized profiles/transcripts once without rewriting evidence.

    Reference paths are dotted locations within this evidence, not external data.
    Repetitions *within* a history are intentionally never deduplicated.
    """
    seen: dict[tuple[str, str], str] = {}

    def visit(value: Any, path: str = "", key: str = "") -> Any:
        document_kind = None
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        if isinstance(value, Mapping):
            if "emotional_status" in value and "personality" in value and "name" in value:
                value = agent_context(value)
                document_kind = "agent"
            elif "user_id" in value and any(field in value for field in ("summary", "sentiment_status", "extrinsic_relationship")):
                value = user_context(value)
                document_kind = "user"
            result = {name: visit(item, f"{path}.{name}" if path else name, name)
                      for name, item in value.items() if name not in _STORAGE_KEYS}
        elif isinstance(value, (list, tuple)):
            items = compact_messages(value) if key in _HISTORY_KEYS else value
            result = [visit(item, f"{path}[{index}]") for index, item in enumerate(items)]
        else:
            result = copy.deepcopy(value)
        if document_kind or key in _HISTORY_KEYS and isinstance(result, list) and result:
            signature = (document_kind or "history", json.dumps(result, sort_keys=True, default=str, ensure_ascii=False))
            if signature in seen:
                return {"same_context_as": seen[signature]}
            seen[signature] = path
        return result

    return visit(evidence)
