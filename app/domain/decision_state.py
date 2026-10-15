"""State proposals retain per-dimension provenance through mixed-source fallback."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from app.domain.state import EmotionalDelta, PersonalityDelta, SentimentDelta
from app.services import state_reducer
from app.services.decisions import DecisionBatch, choice_question

CAPS = {"emotion": 7, "personality": 3, "sentiment": 5}
STATE_KEYS = {"emotion": "emotions", "personality": "traits", "sentiment": "sentiments"}


@dataclass(frozen=True)
class StateProposal:
    dimension: str
    delta: int
    source: str
    confidence: float | None = None
    reason: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)


def _trait_dict(trait: Any) -> dict:
    return trait.model_dump() if hasattr(trait, "model_dump") else dict(trait)


def state_questions(kind: str, traits: Mapping[str, Any]) -> list[dict]:
    cap = CAPS[kind]
    result = []
    for dimension, trait in traits.items():
        data = _trait_dict(trait)
        instructions = (
            f"Direct {kind} delta for {dimension}. "
            f"Description: {data.get('description') or dimension}. Current value: {data['value']}; "
            f"minimum: {data.get('min', 0)}; maximum: {data.get('max', 100)}. "
        )
        choices = [str(delta) for delta in range(-cap, cap + 1)]
        result.append(choice_question(f"{kind}_{dimension}", instructions, choices))
    return result


def proposals_from_batch(kind: str, traits: Mapping[str, Any], batch: DecisionBatch) -> list[StateProposal]:
    proposals = []
    for dimension in traits:
        name = f"{kind}_{dimension}"
        chosen = batch.choice(name)
        if chosen is None:
            continue
        delta = int(chosen)
        if not -CAPS[kind] <= delta <= CAPS[kind]:
            continue
        answer = batch.answers[name]
        proposals.append(StateProposal(dimension, delta, "decisions", confidence=answer["confidence"],
                                       provenance={"question": name, "probabilities": answer["probabilities"]}))
    return proposals


def fallback_proposals(kind: str, payload: Any, keys: Sequence[str]) -> list[StateProposal]:
    """Match legacy normalization, preserving its confidence-zero behavior in the reducer."""
    if not isinstance(payload, Mapping):
        return []
    deltas = payload.get("deltas", {})
    if not isinstance(deltas, Mapping):
        return []
    confidence = payload.get("confidence")
    if type(confidence) not in (int, float) or not math.isfinite(confidence):
        confidence = {"emotion": 0.7, "personality": 0.6, "sentiment": 0.8}[kind]
    confidence = max(0.0, min(1.0, float(confidence)))
    reason = payload.get("reason").strip() if isinstance(payload.get("reason"), str) and payload.get("reason").strip() else None
    result = []
    for dimension in keys:
        raw = deltas.get(dimension)
        if type(raw) not in (int, float) or not math.isfinite(raw):
            continue
        result.append(StateProposal(dimension, int(round(raw)), "legacy", confidence, reason,
                                    {"normalization": "legacy"}))
    return result


def apply_proposals(kind: str, state: Any, proposals: Sequence[StateProposal]) -> tuple[Any, list[dict]]:
    new = state.model_copy(deep=True)
    traits = getattr(new, STATE_KEYS[kind])
    seen = set()
    audits = []
    accepted_dimensions = []
    fallback_reason = None
    reducer = {"emotion": state_reducer.apply_deltas_emotion,
               "personality": state_reducer.apply_deltas_personality,
               "sentiment": state_reducer.apply_deltas_sentiment}.get(kind)
    delta_type = {"emotion": EmotionalDelta, "personality": PersonalityDelta, "sentiment": SentimentDelta}[kind]
    for proposal in proposals:
        if proposal.dimension in seen:
            raise ValueError(f"Duplicate state proposal for {proposal.dimension}")
        seen.add(proposal.dimension)
        if proposal.dimension not in traits:
            continue
        if type(proposal.delta) is not int:
            raise ValueError("State proposals require integer deltas")
        before = traits[proposal.dimension].value
        if proposal.source in {"decisions", "decay"}:
            capped = max(-CAPS[kind], min(CAPS[kind], proposal.delta))
            traits[proposal.dimension] = traits[proposal.dimension].apply(capped)
            if proposal.source == "decisions":
                accepted_dimensions.append(f"{proposal.dimension} {proposal.delta:+d}")
        elif proposal.source == "legacy":
            new = reducer(new, delta_type(deltas={proposal.dimension: proposal.delta},
                                         confidence=proposal.confidence, reason=proposal.reason))
            traits = getattr(new, STATE_KEYS[kind])
            fallback_reason = proposal.reason or fallback_reason
        else:
            raise ValueError(f"Unknown state proposal source: {proposal.source}")
        after = traits[proposal.dimension].value
        audits.append({"dimension": proposal.dimension, "pre": before, "post": after,
                       "requested_delta": proposal.delta, "actual_delta": after - before,
                       "source": proposal.source, "confidence": proposal.confidence,
                       "provenance": proposal.provenance})
    if hasattr(new, "reason") and accepted_dimensions:
        summary = "Decisions: " + ", ".join(accepted_dimensions) + "."
        new.reason = summary + (" Legacy fallback: " + fallback_reason if fallback_reason else "")
    return new, audits


def decay_proposals(traits: Mapping[str, Any]) -> list[StateProposal]:
    return [StateProposal(dimension, -1, "decay", reason="Passive emotional decay")
            for dimension, trait in traits.items()
            if _trait_dict(trait)["value"] > _trait_dict(trait).get("min", 0)]
