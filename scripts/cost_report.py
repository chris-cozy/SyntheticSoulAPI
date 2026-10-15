"""Compare measured complete-exchange estimates; no cheaper-cost pass criterion.

python -m scripts.cost_report [--owner USER_ID] [--limit 1000]
python -m scripts.cost_report --json summaries.json
JSON input is a list of GET /v1/jobs/{id}/cost response objects.
"""
import argparse
import asyncio
from decimal import Decimal
import json
import math
from statistics import mean


def _percentile(values, fraction=.95):
    if not values:
        return None
    values = sorted(values)
    return values[max(0, math.ceil(len(values) * fraction) - 1)]


def build_report(summaries, include_cache_modes=True):
    summaries = list(summaries)
    groups = {}
    for item in summaries:
        metadata = item.get("metadata", {})
        flags = metadata.get("flags", {})
        enabled = flags.get("decisions_enabled", flags.get("decisions", False)) if isinstance(flags, dict) else "decisions" in flags
        variant = metadata.get("variant") or ("decisions" if enabled else "baseline")
        key = f"{item.get('kind', 'exchange')}:{variant}"
        groups.setdefault(key, []).append(item)
    result = {}
    for name, items in groups.items():
        complete = [x for x in items if x.get("accounting_complete")]
        incomplete = [x for x in items if not x.get("accounting_complete")]
        costs = [Decimal(x["total_cost_usd"]) for x in complete]
        latencies = [sum(s.get("latency_ms", 0) for s in x.get("stages", {}).values()) for x in complete]
        complete_latencies = [x["execution_latency_ms"] for x in complete if x.get("execution_latency_ms") is not None]
        attempts = sum(x.get("attempt_count", 0) for x in items)
        fallback = sum(s.get("fallback_attempts", 0) for x in items for s in x.get("stages", {}).values())
        retries = sum(s.get("retry_attempts", 0) for x in items for s in x.get("stages", {}).values())
        phase_latencies = {}
        for phase in {k for x in complete for k in x.get("phases", {})}:
            durations = []
            for item in complete:
                entry = item.get("phases", {}).get(phase, {})
                started, ended = entry.get("started_at"), entry.get("ended_at")
                if started and ended:
                    from datetime import datetime
                    if isinstance(started, str):
                        started = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    if isinstance(ended, str):
                        ended = datetime.fromisoformat(ended.replace("Z", "+00:00"))
                    durations.append((ended-started).total_seconds()*1000)
            phase_latencies[phase] = {"samples": len(durations), "average_ms": mean(durations) if durations else None,
                                      "p95_ms": _percentile(durations)}
        result[name] = {"runs": len(items), "complete_runs": len(complete), "incomplete_runs": len(incomplete),
                        "complete_total_cost_usd": str(sum(costs, Decimal(0))),
                        "average_complete_exchange_cost_usd": str(sum(costs, Decimal(0))/len(costs)) if costs else None,
                        "p95_complete_exchange_cost_usd": str(_percentile(costs)) if costs else None,
                        "incomplete_known_cost_usd": str(sum((Decimal(x.get("known_cost_usd", "0")) for x in incomplete), Decimal(0))),
                        "unknown_attempts": sum(x.get("unknown_attempts", 0) for x in items),
                        "fallback_attempts": fallback, "retry_attempts": retries,
                        "observed_tokens": {key: sum(stage.get(key, 0) for x in items for stage in x.get("stages", {}).values())
                                            for key in ("input_tokens", "output_tokens", "cached_tokens", "cache_write_tokens")},
                        "usage_unknown_attempts": sum(stage.get("usage_unknown_attempts", 0) for x in items for stage in x.get("stages", {}).values()),
                        "fallback_attempt_rate": fallback/attempts if attempts else 0,
                        "average_total_api_latency_ms": mean(latencies) if latencies else None,
                        "p95_total_api_latency_ms": _percentile(latencies), "phase_latencies": phase_latencies,
                        "average_complete_execution_latency_ms": mean(complete_latencies) if complete_latencies else None,
                        "p95_complete_execution_latency_ms": _percentile(complete_latencies),
                        "pricing_versions": sorted({v for x in items for v in x.get("pricing_versions", [])})}
    comparisons = {}
    for kind in {x.split(":", 1)[0] for x in result}:
        baseline, decisions = result.get(f"{kind}:baseline"), result.get(f"{kind}:decisions")
        if not baseline or not decisions:
            continue
        b, d = baseline["average_complete_exchange_cost_usd"], decisions["average_complete_exchange_cost_usd"]
        if b is not None and d is not None:
            b, d = Decimal(b), Decimal(d)
            comparisons[kind] = {"average_cost_delta_usd": str(d-b),
                                  "average_cost_delta_percent": str((d-b)/b*100) if b else None,
                                  "average_api_latency_delta_ms": decisions["average_total_api_latency_ms"] - baseline["average_total_api_latency_ms"],
                                  "fallback_attempt_rate_delta": decisions["fallback_attempt_rate"] - baseline["fallback_attempt_rate"]}
    report = {"currency": "USD", "estimated": True, "groups": result, "comparisons": comparisons,
              "note": "Incomplete runs are excluded from complete-cost averages. Autonomous runs remain separate. API latency sums provider attempts; phase latency measures worker execution. Differences are observations, not acceptance gates."}
    if include_cache_modes:
        modes = {x.get("metadata", {}).get("cache_mode") for x in summaries} - {None}
        report["cache_modes"] = {mode: build_report([x for x in summaries if x.get("metadata", {}).get("cache_mode") == mode], False) for mode in sorted(modes)}
    return report


async def _load_mongo(args):
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import MONGO_CONNECTION, DATABASE_NAME
    from app.services.accounting import RUN_COLLECTION, ATTEMPT_COLLECTION, summarize_cost
    client = AsyncIOMotorClient(MONGO_CONNECTION, serverSelectionTimeoutMS=5000)
    try:
        db = client[DATABASE_NAME]
        query = {"owner_id": args.owner} if args.owner else {}
        runs = await db[RUN_COLLECTION].find(query).sort("created_at", -1).limit(args.limit).to_list(length=args.limit)
        return [summarize_cost(run, await db[ATTEMPT_COLLECTION].find({"run_id": run["run_id"]}).to_list(length=None)) for run in runs]
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", help="Read exported cost summaries instead of Mongo")
    parser.add_argument("--owner", help="Only this owner (Mongo input)")
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()
    if args.json:
        with open(args.json, encoding="utf-8") as source:
            summaries = json.load(source)
    else:
        summaries = asyncio.run(_load_mongo(args))
    print(json.dumps(build_report(summaries), indent=2, default=str))


if __name__ == "__main__":
    main()
