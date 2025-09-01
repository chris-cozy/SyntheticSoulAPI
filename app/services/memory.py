from typing import Optional, Dict
from app.constants.constants import (
    BASE_EMOTIONAL_STATUS_LITE,
    MIN_EMOTION_VALUE,
    MAX_EMOTION_VALUE,
)

EMOTION_KEYS = tuple(BASE_EMOTIONAL_STATUS_LITE["emotions"].keys())

def normalize_emotional_impact_fill_zeros(
    impact: Optional[Dict]
) -> Optional[Dict]:
    """
    If the LLM returns a partial emotional_impact (e.g., {"joy":{"value":35}})
    expand missing keys to {"value": 0}. If `impact` is None/empty, return None
    (saves storage and remains allowed by the validator).
    """
    if not impact:
        return None  # leave out entirely if LLM emitted nothing

    out: Dict[str, Dict[str, int]] = {}
    for k in EMOTION_KEYS:
        v = impact.get(k)
        if isinstance(v, dict) and ("value" in v) and (v["value"] is not None):
            try:
                val = int(v["value"])
            except Exception:
                val = 0
        else:
            val = 0

        # clamp to your global bounds
        if val < MIN_EMOTION_VALUE:
            val = MIN_EMOTION_VALUE
        if val > MAX_EMOTION_VALUE:
            val = MAX_EMOTION_VALUE

        out[k] = {"value": val}

    return out