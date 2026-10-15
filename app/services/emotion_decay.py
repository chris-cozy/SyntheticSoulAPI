"""Deterministic passive decay shares the revision boundary of model changes."""
import asyncio
from datetime import datetime, timezone

from app.core.config import AGENT_NAME, EMOTIONAL_DECAY_RATE
from app.domain.decision_state import apply_proposals, decay_proposals
from app.domain.state import BoundedTrait, EmotionalState
from app.services import cognition, database


async def decay_once():
    await database.grab_self()
    db = await database.get_database()

    async def evaluate(snapshot):
        current = snapshot["emotional_status"]
        state = EmotionalState(emotions={k: BoundedTrait(**v) for k, v in current["emotions"].items()},
                               reason=current.get("reason"))
        proposals = decay_proposals(state.emotions)
        if not proposals:
            return {}, []
        updated, audits = apply_proposals("emotion", state, proposals)
        updated.reason = "decay"
        return {"emotional_status": updated.model_dump()}, audits

    result = await cognition.evaluate_and_commit(db[database.AGENT_COLLECTION], {"name": AGENT_NAME}, evaluate)
    if result.status == "committed" and result.value:
        try:
            await db["state_events"].insert_one({
                "agent": AGENT_NAME, "ts": datetime.now(timezone.utc), "kind": "decay",
                "revision": int(result.snapshot.get("cognition_revision", 0)) + 1,
                "status": result.status, "dimensions": result.value,
            })
        except Exception:
            pass
    return result

async def emotion_decay_loop(decay_rate: int = EMOTIONAL_DECAY_RATE):
    while True:
        try:
            result = await decay_once()
            if result.status in {"conflict", "unknown", "missing"}:
                print(f"Emotional decay {result.status}; stored state retained.")
        except Exception as exc:
            print(f"Error - Emotional decay: {type(exc).__name__}")
        await asyncio.sleep(decay_rate)



