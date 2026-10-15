"""Revision-checked cognition mutations; only definite conflicts are re-evaluated."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Mapping


@dataclass(frozen=True)
class CommitResult:
    status: str
    revision: int | None = None
    error: str | None = None

    def __bool__(self):
        return self.status == "committed"


@dataclass
class MutationResult:
    status: str
    snapshot: dict | None
    fields: dict
    value: Any = None
    attempts: int = 0
    error: str | None = None

    def __bool__(self):
        return self.status == "committed"


def _get_path(document: Mapping, path: str) -> Any:
    value: Any = document
    for part in path.split("."):
        if not isinstance(value, Mapping) or part not in value:
            return _MISSING
        value = value[part]
    return value


_MISSING = object()


async def commit_snapshot(collection, snapshot: Mapping, fields: Mapping) -> CommitResult:
    """Atomically apply intended fields once. Existing revisionless documents start at zero.

    A connection loss may occur after Mongo applies a write. Readback must prove our
    revision and all intended values before treating that case as successful. If
    proof is unavailable, return unknown and do not repeat the delta.
    """
    if "_id" not in snapshot:
        raise ValueError("A cognition snapshot needs its document _id")
    if any(key.split(".")[0] in {"_id", "cognition_revision"} or key.startswith("$") for key in fields):
        raise ValueError("Cognition updates cannot overwrite identity or revision")
    revision = int(snapshot.get("cognition_revision", 0))
    query = {"_id": snapshot["_id"]}
    if revision == 0:
        query["$or"] = [{"cognition_revision": 0}, {"cognition_revision": {"$exists": False}}]
    else:
        query["cognition_revision"] = revision
    intended = copy.deepcopy(dict(fields))
    try:
        result = await collection.update_one(query, {"$set": intended, "$inc": {"cognition_revision": 1}})
        if result.matched_count == 1:
            return CommitResult("committed", revision + 1)
        return CommitResult("conflict", revision)
    except Exception as exc:
        try:
            current = await collection.find_one({"_id": snapshot["_id"]})
            if current is not None and current.get("cognition_revision", 0) == revision + 1:
                if all(_get_path(current, key) == value for key, value in intended.items()):
                    return CommitResult("committed", revision + 1)
        except Exception:
            pass
        return CommitResult("unknown", revision, type(exc).__name__)


async def evaluate_and_commit(collection, identity: Mapping,
                              evaluate: Callable[[dict], Awaitable[tuple[dict, Any]]],
                              *, max_attempts: int = 3) -> MutationResult:
    if not 1 <= max_attempts <= 3:
        raise ValueError("Cognition evaluation allows one to three total attempts")
    last_snapshot = None
    for attempt in range(1, max_attempts + 1):
        snapshot = await collection.find_one(dict(identity))
        last_snapshot = snapshot
        if snapshot is None:
            return MutationResult("missing", None, {}, attempts=attempt)
        fields, value = await evaluate(copy.deepcopy(snapshot))
        if not fields:
            # An interaction-local result still depends on its captured cognition.
            # Verify no other writer changed that state while it was evaluated.
            current = await collection.find_one(dict(identity))
            if current is None:
                return MutationResult("missing", None, {}, attempts=attempt)
            if current.get("cognition_revision", 0) != snapshot.get("cognition_revision", 0):
                continue
            return MutationResult("unchanged", current, {}, value, attempt)
        result = await commit_snapshot(collection, snapshot, fields)
        if result.status == "unknown":
            try:
                current = await collection.find_one(dict(identity))
            except Exception:
                current = snapshot
            return MutationResult("unknown", current, {}, attempts=attempt, error=result.error)
        if result.status != "conflict":
            return MutationResult(result.status, snapshot, fields, value, attempt, result.error)
    # Read fresh state so callers continue with the winner's state rather than stale proposals.
    try:
        latest = await collection.find_one(dict(identity))
    except Exception as exc:
        return MutationResult("unknown", last_snapshot, {}, attempts=max_attempts, error=type(exc).__name__)
    return MutationResult("conflict", latest or last_snapshot, {}, attempts=max_attempts)
