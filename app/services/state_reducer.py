from math import exp

from app.domain.state import BoundedTrait, EmotionalDelta, EmotionalState, PersonalityDelta, PersonalityMatrix, SentimentDelta, SentimentMatrix
'''
You control realism centrally: tighter caps for personality (slow), looser for emotions (fast).

You can add cooldowns (e.g., ignore large absolute movement after a spike).

You can unify the decay loop: treat decay as a delta event ({"all": -1} every N seconds) rather than a separate path, or keep your loop and run it through this reducer.
'''

def _friction(t: BoundedTrait, d: float) -> int:
    # Damp movement near bounds so values saturate naturally
    span = max(1.0, float(t.max - t.min))
    up_room = (t.max - t.value) / span
    dn_room = (t.value - t.min) / span
    if d > 0: d *= up_room
    if d < 0: d *= dn_room
    return int(d)

def apply_deltas_emotion(state: EmotionalState, delta: EmotionalDelta, *, cap: float = 7.0) -> EmotionalState:
    '''
    # Optional: cross-trait coupling, e.g., joy vs sadness
    # new = normalize_pairs(new, pairs=[("joy","sadness")], max_sum=150)
    '''
    new = state.model_copy(deep=True)
    for k, raw in delta.deltas.items():
        print(k)
        print(raw)
        if k not in new.emotions: 
            continue
        d = float(raw)
        # 1) cap
        d = max(-cap, min(cap, d))

        # 2) confidence-weight (0..1)
        conf = delta.confidence or 0.7
        d *= conf
        print(d)
        # 3) friction near bounds (saturate near min/max)
        d = _friction(new.emotions[k], d)
        print(d)
        new.emotions[k] = new.emotions[k].apply(d)
    if delta.reason:
        new.reason = delta.reason
    
    return new

def apply_deltas_personality(mat: PersonalityMatrix, delta: PersonalityDelta, *, cap=3.0) -> PersonalityMatrix:
    new = mat.model_copy(deep=True)
    for k, raw in delta.deltas.items():
        if k not in new.traits: 
            continue
        d = float(raw)
        d = max(-cap, min(cap, d))
        conf = delta.confidence or 0.6
        d *= conf
        d = int(d)
        new.traits[k] = new.traits[k].apply(d)
    return new

def apply_deltas_sentiment(mat: SentimentMatrix, delta: SentimentDelta, *, cap=5.0) -> SentimentMatrix:
    new = mat.model_copy(deep=True)
    for k, raw in delta.deltas.items():
        if k not in new.sentiments: 
            continue
        d = float(raw)
        d = max(-cap, min(cap, d))
        conf = delta.confidence or 0.8
        d *= conf
        d = int(d)
        new.sentiments[k] = new.sentiments[k].apply(d)
    return new