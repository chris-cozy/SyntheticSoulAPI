from datetime import datetime, timezone

async def log_state_event(db, *, agent: str, kind: str, deltas: dict, pre: dict, post: dict, reason: str = "", confidence: float | None = None, source: str = "llm"):
    '''
    Call this right before/after applying deltas. Helps tune caps & friction.
    '''
    await db["state_events"].insert_one({
        "agent": agent,
        "ts": datetime.now(timezone.utc),
        "kind": kind,             # "emotion" | "personality" | "decay"
        "deltas": deltas,
        "pre": pre,
        "post": post,
        "reason": reason,
        "confidence": confidence,
        "source": source
    })
