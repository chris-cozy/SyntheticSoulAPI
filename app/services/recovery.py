"""One generative recovery attempt per native pipeline phase.

Required prose generation does not consume recovery. Exhaustion never reuses a
stale model result: callers keep stored state or decline optional work.
"""
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps

from app.services import accounting
from app.services.openai import structured_query


@dataclass
class RecoveryPhase:
    name: str
    used: bool = False


_phase: ContextVar[RecoveryPhase | None] = ContextVar("decision_recovery_phase", default=None)
_active: ContextVar[bool] = ContextVar("decision_recovery_active", default=False)


def active() -> bool:
    """Disable SDK retries for the single physical recovery request."""
    return _active.get()


def phase(name):
    def decorate(function):
        @wraps(function)
        async def wrapped(*args, **kwargs):
            token = _phase.set(RecoveryPhase(name))
            try:
                return await function(*args, **kwargs)
            finally:
                _phase.reset(token)
        return wrapped
    return decorate


async def query(messages, schema, quality=True, *, stage=None, fallback=True, writer=None, recover_generation=False):
    writer = writer or structured_query
    if not fallback:
        result = await writer(messages, schema, quality=quality, stage=stage, fallback=False)
        if result is None and recover_generation:
            return await query(messages, schema, quality=quality, stage=(stage or "generation") + "_recovery",
                               writer=writer)
        return result
    budget = _phase.get()
    if budget is not None:
        if budget.used:
            try:
                with accounting.scope() as context:
                    if context.get("run_id"):
                        await accounting.record_event(context["run_id"], "recovery_exhausted",
                            stage=stage or budget.name)
            except Exception:
                pass
            return None
        budget.used = True  # A refused, malformed or failed recovery still consumes the attempt.
        try:
            with accounting.scope() as context:
                if context.get("run_id"):
                    await accounting.record_event(context["run_id"], "recovery_used",
                        stage=stage or budget.name)
        except Exception:
            pass
    token = _active.set(True)
    try:
        return await writer(messages, schema, quality=quality, stage=stage, fallback=True)
    finally:
        _active.reset(token)
