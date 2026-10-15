"""Best-effort durable API-attempt ledger; never stores model content.

The sync HTTPX hooks run before SDK parsing and are safe in asyncio.to_thread.
Call flush in a query's finally block. Pending work and worker failures stay
incomplete, even when every already-observed response has a known price.
"""
from collections import defaultdict
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from decimal import Decimal
import inspect
import json
import logging
import os
import threading
import time
from uuid import uuid4

from app.services.pricing import PRICING_VERSION, estimate_cost, normalize_usage

RUN_COLLECTION = "api_cost_runs"
ATTEMPT_COLLECTION = "api_cost_attempts"
_context = ContextVar("api_accounting_context", default={})
_db = None
_lock = threading.Lock()
_pending: dict[str, dict] = {}
_recording_failures: set[str] = set()
_logger = logging.getLogger(__name__)
_META_KEYS = {"stage", "phase", "endpoint", "provider", "model", "service_tier", "regional",
              "revision", "fallback", "flags", "agent_name", "variant", "scenario_id", "cache_mode"}


def enabled() -> bool:
    return os.getenv("COST_TRACKING_ENABLED", "true").strip().lower() in {"true", "1", "yes", "on"}


def _now():
    return datetime.now(timezone.utc)


def _metadata(values):
    result = {}
    for k, v in values.items():
        if k not in _META_KEYS:
            continue
        if isinstance(v, (str, int, float, bool)) or v is None:
            result[k] = v
        elif k == "flags" and isinstance(v, dict):
            result[k] = {str(key): value for key, value in v.items() if isinstance(value, (bool, int, str))}
        elif k == "flags" and isinstance(v, (list, tuple, set)):
            result[k] = sorted(str(x) for x in v)
    return result


@contextmanager
def scope(run_id=None, owner_id=None, stage=None, **metadata):
    value = dict(_context.get())
    if run_id is not None:
        value["run_id"] = str(run_id)
        value["owner_id"] = str(owner_id) if owner_id is not None else None
    elif owner_id is not None:
        value["owner_id"] = str(owner_id)
    if stage is not None:
        value["stage"] = stage
    value.update(_metadata(metadata))
    token = _context.set(value)
    try:
        yield value
    finally:
        _context.reset(token)


async def initialize_accounting(db):
    global _db
    _db = db
    if not enabled():
        return
    try:
        await db[RUN_COLLECTION].create_index("run_id", unique=True)
        await db[RUN_COLLECTION].create_index([("owner_id", 1), ("created_at", -1)])
        await db[RUN_COLLECTION].create_index([("kind", 1), ("created_at", -1)])
        await db[ATTEMPT_COLLECTION].create_index("attempt_id", unique=True)
        await db[ATTEMPT_COLLECTION].create_index([("run_id", 1), ("stage", 1)])
        await db[ATTEMPT_COLLECTION].create_index([("owner_id", 1), ("started_at", -1)])
    except Exception:
        _logger.warning("API accounting index initialization failed")


async def _database():
    global _db
    if _db is None:
        try:
            from app.services.database import get_database
            result = get_database()
            _db = await result if inspect.isawaitable(result) else result
        except Exception:
            return None
    return _db


async def begin_run(run_id, owner_id, kind="exchange", metadata=None):
    if not enabled():
        return
    db = await _database()
    try:
        if db is None:
            raise RuntimeError("Accounting database unavailable")
        phases = {"reply": {"status": "pending", "job_id": str(run_id)},
                  "background": {"status": "pending"}} if kind == "exchange" else {kind: {"status": "pending"}}
        await db[RUN_COLLECTION].update_one({"run_id": str(run_id)}, {"$setOnInsert": {
            "run_id": str(run_id), "owner_id": str(owner_id) if owner_id is not None else None,
            "kind": kind, "created_at": _now(), "phases": phases,
            "metadata": _metadata(metadata or {}), "recording_errors": 0,
            "pricing_version": PRICING_VERSION}}, upsert=True)
    except Exception:
        with _lock:
            _recording_failures.add(str(run_id))
        _logger.warning("API accounting run registration failed")


async def mark_phase(run_id, phase, status, job_id=None, error=None):
    if not enabled():
        return
    # Phase/error are codes supplied by application, never provider/user text.
    if phase not in {"reply", "background", "autonomy", "decay", "replay"}:
        raise ValueError("Unknown accounting phase")
    if status not in {"pending", "running", "completed", "failed", "cancelled", "unknown"}:
        raise ValueError("Unknown accounting phase status")
    await flush()
    db = await _database()
    changes = {f"phases.{phase}.status": status, "updated_at": _now()}
    if job_id is not None:
        changes[f"phases.{phase}.job_id"] = str(job_id)
    if status == "running":
        changes[f"phases.{phase}.started_at"] = _now()
    if status in {"completed", "failed", "cancelled", "unknown"}:
        changes[f"phases.{phase}.ended_at"] = _now()
    if error:
        changes[f"phases.{phase}.error_code"] = str(error)[:80]
    try:
        await db[RUN_COLLECTION].update_one({"run_id": str(run_id)}, {"$set": changes})
    except Exception:
        with _lock:
            _recording_failures.add(str(run_id))
        _logger.warning("API accounting phase update failed")


async def mark_incomplete(run_id, error="recording_failure"):
    """Record a code indicating lost accounting evidence, without aborting work."""
    if not enabled():
        return
    with _lock:
        _recording_failures.add(str(run_id))
    await flush()
    await record_event(run_id, error)


async def record_event(run_id, code, **metadata):
    """Attach application event codes and whitelisted metadata, never text."""
    if not enabled():
        return
    db = await _database()
    try:
        await db[RUN_COLLECTION].update_one({"run_id": str(run_id)}, {"$push": {"events": {
            "code": str(code)[:80], "timestamp": _now(), **_metadata(metadata)}}})
    except Exception:
        with _lock:
            _recording_failures.add(str(run_id))
        _logger.warning("API accounting event persistence failed")


def _queue(record):
    with _lock:
        if len(_pending) >= 10000 and record["attempt_id"] not in _pending:
            _recording_failures.add(record["run_id"])
            return
        _pending[record["attempt_id"]] = record


def httpx_hooks():
    """Sync event hooks for httpx.Client, including SDK's physical retries."""
    def request_hook(request):
        if not enabled() or not _context.get().get("run_id"):
            return
        try:
            context = dict(_context.get())
            try:
                payload = json.loads(request.content)
            except Exception:
                payload = {}
            # Never retain payload; only whitelist billing/routing metadata.
            model = payload.get("model", context.get("model"))
            tier = payload.get("service_tier", context.get("service_tier", "default"))
            endpoint = "decisions" if request.url.path.endswith("/decisions") else "chat.completions" if request.url.path.endswith("/chat/completions") else "responses" if request.url.path.endswith("/responses") else "unknown"
            attempt_id = str(uuid4())
            record = {**_metadata(context), "attempt_id": attempt_id,
                      "run_id": context["run_id"], "owner_id": context.get("owner_id"),
                      "stage": context.get("stage", "unspecified"), "phase": context.get("phase", "reply"),
                      "provider": context.get("provider", "openai"), "endpoint": endpoint,
                      "requested_model": model, "model": model, "service_tier": tier,
                      "started_at": _now(), "status": "pending", "usage": None,
                      "sdk_retry_count": int(request.headers.get("x-stainless-retry-count", 0))}
            request.extensions["api_cost_record"] = record
            request.extensions["api_cost_clock"] = time.monotonic()
            _queue(record)
        except Exception:
            with _lock:
                _recording_failures.add(_context.get().get("run_id"))
            _logger.warning("API accounting request capture failed")

    def response_hook(response):
        record = response.request.extensions.get("api_cost_record")
        if record is None:
            return
        try:
            record = dict(record)
            # Reading caches HTTPX body for the SDK, including malformed output.
            response.read()
            try:
                payload = response.json()
            except Exception:
                payload = {}
            if not isinstance(payload, dict):
                payload = {}
            usage = normalize_usage(payload.get("usage"), decisions=record["endpoint"] == "decisions")
            model = payload.get("model") or record["requested_model"]
            tier = payload.get("service_tier") or record["service_tier"]
            record.update({"model": model, "service_tier": tier, "usage": usage,
                           "status": "responded", "status_code": response.status_code,
                           "ended_at": _now(), "latency_ms": round((time.monotonic() - response.request.extensions["api_cost_clock"]) * 1000, 3),
                           "provider_request_id": response.headers.get("x-request-id"),
                           "provider_response_id": payload.get("id") if isinstance(payload.get("id"), str) else None})
            regional = bool(record.get("regional")) or response.request.url.host in {"eu.api.openai.com", "us.api.openai.com"}
            record.update(estimate_cost(record["provider"], record["endpoint"], model, usage, tier, regional))
            _queue(record)
        except Exception:
            with _lock:
                _recording_failures.add(record["run_id"])
            _logger.warning("API accounting response capture failed")
    return {"request": [request_hook], "response": [response_hook]}


async def flush():
    """Idempotently persist buffered attempts. Recording errors never fail replies."""
    if not enabled():
        return
    db = await _database()
    if db is None:
        return
    with _lock:
        records = list(_pending.values())
        _pending.clear()
        failures = set(_recording_failures)
    for record in records:
        if "known" not in record:
            record.update(estimate_cost(record["provider"], record["endpoint"], record["model"], None,
                                        record["service_tier"], bool(record.get("regional"))))
        try:
            # A concurrent flush of a request snapshot must never overwrite a
            # response already persisted by another flush.
            operation = "$setOnInsert" if record["status"] == "pending" else "$set"
            await db[ATTEMPT_COLLECTION].update_one({"attempt_id": record["attempt_id"]}, {operation: record}, upsert=True)
        except Exception:
            failures.add(record["run_id"])
            _queue(record)
            _logger.warning("API accounting attempt persistence failed")
    for run_id in failures:
        try:
            await db[RUN_COLLECTION].update_one({"run_id": run_id}, {"$set": {"recording_errors": 1}})
            with _lock:
                _recording_failures.discard(run_id)
        except Exception:
            with _lock:
                _recording_failures.add(run_id)


async def reconcile_run(run_id, rq_status_lookup=None, *, run=None):
    """Mark a missing completion signal incomplete after a terminal RQ state.

    rq_status_lookup(job_id) should return an RQ state string, or None if expired.
    An expired job cannot prove a pending run succeeded; it becomes unknown.
    """
    db = await _database()
    if db is None or rq_status_lookup is None:
        return
    try:
        if run is None:
            run = await db[RUN_COLLECTION].find_one({"run_id": str(run_id)})
        if not run:
            return
        for phase, entry in run.get("phases", {}).items():
            if entry.get("status") not in {"pending", "running"}:
                continue
            job_id = entry.get("job_id")
            orphan_background = phase == "background" and not job_id
            if orphan_background:
                job_id = run.get("phases", {}).get("reply", {}).get("job_id")
            if not job_id:
                continue
            status = rq_status_lookup(job_id)
            if inspect.isawaitable(status):
                status = await status
            status = getattr(status, "value", status)
            if orphan_background and status in {"finished", "failed", "stopped", "canceled", "cancelled", None}:
                terminal, error = "unknown", "background_not_registered"
            elif status in {"failed", "stopped", "canceled", "cancelled"}:
                terminal, error = "failed", "worker_terminal_without_completion"
            elif status == "finished" or status is None:
                terminal, error = "unknown", "missing_completion_signal"
            else:
                continue
            # The worker may have completed or registered a new job during the lookup.
            await db[RUN_COLLECTION].update_one(
                {"run_id": str(run_id), f"phases.{phase}": entry},
                {"$set": {f"phases.{phase}.status": terminal,
                          f"phases.{phase}.error_code": error,
                          f"phases.{phase}.ended_at": _now(), "updated_at": _now()}})
    except Exception:
        _logger.warning("API accounting reconciliation unavailable")


def summarize_cost(run, attempts):
    stages = {}
    phase_cost = defaultdict(lambda: Decimal(0))
    unknown = 0
    snapshots = {}
    for attempt in attempts:
        stage = attempt.get("stage", "unspecified")
        row = stages.setdefault(stage, {"known_cost_usd": Decimal(0), "attempts": 0,
                                        "unknown_attempts": 0, "fallback_attempts": 0,
                                        "retry_attempts": 0, "latency_ms": 0.0,
                                        "input_tokens": 0, "output_tokens": 0, "cached_tokens": 0,
                                        "cache_write_tokens": 0, "usage_unknown_attempts": 0})
        row["attempts"] += 1
        row["fallback_attempts"] += bool(attempt.get("fallback"))
        row["retry_attempts"] += int(attempt.get("sdk_retry_count", 0)) > 0
        row["latency_ms"] += attempt.get("latency_ms", 0)
        usage = attempt.get("usage")
        if usage is None:
            row["usage_unknown_attempts"] += 1
        else:
            for key in ("input_tokens", "output_tokens", "cached_tokens", "cache_write_tokens"):
                row[key] += usage.get(key, 0)
        if attempt.get("known") and attempt.get("cost_usd") is not None:
            value = Decimal(attempt["cost_usd"])
            row["known_cost_usd"] += value
            phase_cost[attempt.get("phase", "reply")] += value
        else:
            row["unknown_attempts"] += 1
            unknown += 1
        if attempt.get("pricing"):
            pricing = attempt["pricing"]
            snapshots[json.dumps(pricing, sort_keys=True)] = pricing
    phases = run.get("phases", {})
    pending = any(p.get("status") in {"pending", "running"} for p in phases.values())
    successful = bool(phases) and all(p.get("status") == "completed" for p in phases.values())
    failed = any(p.get("status") in {"failed", "cancelled", "unknown"} for p in phases.values())
    errors = run.get("recording_errors", 0)
    complete = successful and not unknown and not errors
    for row in stages.values():
        row["known_cost_usd"] = str(row["known_cost_usd"])
    ended = [p.get("ended_at") for p in phases.values() if p.get("ended_at") is not None]
    execution_latency_ms = None
    if ended and run.get("created_at"):
        try:
            execution_latency_ms = max(0, (max(ended) - run["created_at"]).total_seconds() * 1000)
        except (TypeError, ValueError):
            pass
    return {"run_id": run["run_id"], "kind": run.get("kind", "exchange"), "currency": "USD",
            "estimated": True, "execution_status": "failed" if failed else "pending" if pending else "completed" if successful else "unknown",
            "accounting_complete": complete, "provisional": pending,
            "known_cost_usd": str(sum(phase_cost.values(), Decimal(0))),
            "total_cost_usd": str(sum(phase_cost.values(), Decimal(0))) if complete else None,
            "reply_known_cost_usd": str(phase_cost["reply"]),
            "background_known_cost_usd": str(phase_cost["background"]),
            "unknown_attempts": unknown, "recording_errors": errors, "attempt_count": len(attempts),
            "execution_latency_ms": execution_latency_ms,
            "phases": phases, "stages": stages, "pricing_versions": sorted({p.get("version", "unknown") for p in snapshots.values()}),
            "pricing_snapshots": list(snapshots.values()), "created_at": run.get("created_at"),
            "updated_at": run.get("updated_at"), "metadata": run.get("metadata", {})}


async def get_cost(run_id, owner_id, *, rq_status_lookup=None):
    """Owner lookup uses Mongo, so it survives Redis/RQ result expiry."""
    if not enabled():
        return None
    await flush()
    db = await _database()
    if db is None:
        return None
    try:
        query = {"run_id": str(run_id), "owner_id": str(owner_id) if owner_id is not None else None}
        run = await db[RUN_COLLECTION].find_one(query)
        if run is None:
            return None
        if rq_status_lookup is not None:
            await reconcile_run(run_id, rq_status_lookup, run=run)
            run = await db[RUN_COLLECTION].find_one(query)
            if run is None:
                return None
        attempts = await db[ATTEMPT_COLLECTION].find({"run_id": str(run_id)}).to_list(length=None)
        return summarize_cost(run, attempts)
    except Exception:
        _logger.warning("API accounting lookup unavailable")
        return None
