"""Package recorded Decisions comparisons; makes no provider or database calls.

python -m scripts.compare_decisions_validation --validation-dir .venv/validation --prior prior-report.json
Use --prefix to package another run, with matching replay/local/autonomy exports.
Costs are observations, never a pass criterion. Optional --behavior-review and
--program-checks JSON files preserve separately recorded review/check evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

from scripts.cost_report import build_report
from scripts.replay import check_bounds, load_cases, validate_snapshot


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def without_provenance(value):
    """Only trim verbose dimension provenance; keep exact replies and events."""
    value = copy.deepcopy(value)
    if isinstance(value, dict):
        for event in value.get("state_events", []):
            for dimension in event.get("dimensions", []):
                dimension.pop("provenance", None)
        return {key: without_provenance(item) for key, item in value.items()}
    if isinstance(value, list):
        return [without_provenance(item) for item in value]
    return value


def check_credentials(value):
    forbidden = {"api_key", "openai_key", "access_token", "refresh_token", "jwt_secret", "argon2_pepper",
                 "authorization", "password", "password_hash", "client_secret"}
    if isinstance(value, dict):
        require(not forbidden.intersection(str(key).lower() for key in value), "Credential field in report inputs")
        for item in value.values():
            check_credentials(item)
    elif isinstance(value, list):
        for item in value:
            check_credentials(item)
    elif isinstance(value, str):
        require(not re.search(r"sk-[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9_.-]{20,}|"
                              r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", value),
                "Credential-shaped string in report inputs")


def validate_cost(cost):
    identifier = cost.get("run_id", "unknown")
    require(cost.get("accounting_complete") is True and cost.get("provisional") is False,
            f"Incomplete accounting: {identifier}")
    require(cost.get("execution_status") == "completed", f"Execution did not complete: {identifier}")
    require(cost.get("unknown_attempts", 0) == 0 and cost.get("recording_errors", 0) == 0,
            f"Unknown or missing attempts: {identifier}")
    stages = cost.get("stages", {})
    require(sum(stage.get("attempts", 0) for stage in stages.values()) == cost["attempt_count"],
            f"Attempt totals do not reconcile: {identifier}")
    require(sum((Decimal(stage["known_cost_usd"]) for stage in stages.values()), Decimal(0))
            == Decimal(cost["total_cost_usd"]), f"Stage costs do not reconcile: {identifier}")
    for name, stage in stages.items():
        require(stage.get("usage_unknown_attempts", 0) == 0, f"Missing token usage: {identifier}:{name}")
        require(all(type(stage.get(key, 0)) is int and stage.get(key, 0) >= 0
                    for key in ("input_tokens", "output_tokens", "cached_tokens", "cache_write_tokens")),
                f"Invalid token count: {identifier}:{name}")
        require(stage.get("cached_tokens", 0) <= stage.get("input_tokens", 0),
                f"Cached tokens exceed input: {identifier}:{name}")


def timestamp(value):
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def recovery_counts(outcome, cost):
    counts = Counter()
    for event in outcome.get("recovery_events", []):
        if event.get("code") != "recovery_used":
            continue
        if cost.get("kind") == "autonomy":
            phase = "autonomy"
        elif event.get("phase"):
            phase = event["phase"]
        else:
            at = timestamp(event["timestamp"])
            candidates = [name for name, entry in cost.get("phases", {}).items()
                          if entry.get("started_at") and entry.get("ended_at")
                          and timestamp(entry["started_at"]) <= at <= timestamp(entry["ended_at"])]
            require(len(candidates) == 1, f"Recovery event cannot be assigned to one phase: {cost['run_id']}")
            phase = candidates[0]
        require(phase in {"reply", "background", "autonomy"}, "Unexpected recovery phase")
        counts[phase] += 1
    require(all(count <= 1 for count in counts.values()), f"Recovery quota exceeded: {cost['run_id']}")
    return dict(counts)


def aggregate(costs):
    report = build_report(costs, include_cache_modes=False)
    require(len(report["groups"]) == 1, "Aggregation needs one kind and variant")
    group = next(iter(report["groups"].values()))
    calls = sum(cost["attempt_count"] for cost in costs)
    stages = {}
    for cost in costs:
        for name, stage in cost.get("stages", {}).items():
            total = stages.setdefault(name, {"cost_usd": Decimal(0), "attempts": 0, "input_tokens": 0,
                "output_tokens": 0, "cached_tokens": 0, "fallback_attempts": 0, "latency_ms": 0})
            total["cost_usd"] += Decimal(stage["known_cost_usd"])
            for key in total.keys() - {"cost_usd"}:
                total[key] += stage.get(key, 0)
    for stage in stages.values():
        stage["cost_usd"] = str(stage["cost_usd"])
    return {**group, "total_api_attempts": calls, "average_api_attempts": calls / len(costs),
            "stage_totals": stages}


def difference(before, after):
    values = {}
    keys = ("complete_total_cost_usd", "average_complete_exchange_cost_usd", "total_api_attempts",
            "average_complete_execution_latency_ms", "average_total_api_latency_ms", "fallback_attempts")
    for key in keys:
        first, second = before.get(key), after.get(key)
        if first is None or second is None:
            values[key] = None
        else:
            first, second = Decimal(str(first)), Decimal(str(second))
            values[key] = {"delta": str(second - first),
                           "percent": str((second - first) / first * 100) if first else None}
    values["observed_tokens"] = {key: {"delta": after["observed_tokens"][key] - before["observed_tokens"][key],
        "percent": str((Decimal(after["observed_tokens"][key]) - Decimal(before["observed_tokens"][key]))
                       / Decimal(before["observed_tokens"][key]) * 100) if before["observed_tokens"][key] else None}
        for key in ("input_tokens", "output_tokens", "cached_tokens")}
    return values


def validate_replay(data, variant, cases, expected_exchanges, warm_repetitions=2):
    require(data["variant"] == variant, "Unexpected replay variant")
    costs, outcomes = data["summaries"], data["outcomes"]
    require(len(costs) == len(outcomes) == expected_exchanges, f"Unexpected exchange count: {variant}")
    by_id = {cost["run_id"]: cost for cost in costs}
    require(len(by_id) == len(costs), "Duplicate cost run IDs")
    expected = Counter({(case["id"], mode, repetition, step): 1 for case in cases
        for mode, repetition in [("cold", 0)] + [("warm", index) for index in range(warm_repetitions)]
        for step in range(len(case.get("messages", [case.get("message")])) )})
    actual = Counter((row.get("case"), row.get("cache_mode"), row.get("repetition"), row.get("step")) for row in outcomes)
    require(actual == expected, f"Actual scenarios/steps/cohorts differ from fixture: {variant}")
    require(len({row["run_id"] for row in outcomes}) == len(outcomes), "Duplicate outcome run IDs")
    recoveries = {}
    for outcome in outcomes:
        require(not outcome.get("error_code") and not outcome.get("bounds_errors"), "Replay execution/bounds failure")
        require(outcome["variant"] == variant and outcome["run_id"] in by_id, "Outcome/cost mismatch")
        require(not check_bounds(outcome["agent_state"]) and not check_bounds(outcome["user_state"]),
                "Stored state has an invalid dimension")
        cost = by_id[outcome["run_id"]]
        validate_cost(cost)
        require(cost["metadata"]["scenario_id"] == outcome["case"]
                and cost["metadata"]["cache_mode"] == outcome["cache_mode"], "Cost metadata does not match outcome")
        recoveries[outcome["run_id"]] = recovery_counts(outcome, cost)
    return recoveries


def build_validation(args):
    root, prefix = Path(args.validation_dir), args.prefix
    paths = {name: root / f"{prefix}-{suffix}.json" for name, suffix in {
        "baseline": "replay-baseline", "decisions": "replay-decisions", "fixture": "local-fixture",
        "live": "local-live", "autonomy_baseline": "autonomy-paired-baseline",
        "autonomy_decisions": "autonomy-paired-decisions"}.items()}
    sources = {key: read_json(path) for key, path in paths.items()}
    snapshot_path = Path(args.snapshot) if args.snapshot else root / "snapshot.json"
    snapshot, cases, prior = read_json(snapshot_path), load_cases(args.cases), read_json(args.prior)
    validate_snapshot(snapshot)
    for key in ("baseline", "decisions"):
        validate_replay(sources[key], key, cases, args.expected_exchanges, args.warm_repetitions)
    require((sources["baseline"]["clock"], sources["baseline"]["seed"])
            == (sources["decisions"]["clock"], sources["decisions"]["seed"]), "Unmatched replay clock/seed")
    for key, provider in (("fixture", "fixture"), ("live", "live")):
        source = sources[key]
        require(source["provider"] == provider and source["passed"] is True, f"Failed {key} program validation")
        require({run["variant"] for run in source["runs"]} == {"baseline", "decisions"}, "Missing local variant")
        for run in source["runs"]:
            require(run["passed"] is True and all(value is True for value in run["checks"].values()),
                    f"Failed program checks: {key}:{run['variant']}")
            validate_cost(run["cost"])
    autonomy = {variant: sources["autonomy_" + variant] for variant in ("baseline", "decisions")}
    for variant, outcomes in autonomy.items():
        require(len(outcomes) == 2 and {row["branch"] for row in outcomes} == {"contextual", "random"},
                "Autonomy requires both recorded branches per variant")
        for outcome in outcomes:
            require(outcome["variant"] == variant and not check_bounds(outcome["state"]), "Invalid autonomy state/variant")
            require(outcome["seed"] == {"contextual": 0, "random": 1}[outcome["branch"]], "Unmatched autonomous branch seed")
            validate_cost(outcome["cost"])
            recovery_counts(outcome, outcome["cost"])
            require(all(message.get("recipient_id") in {str(snapshot["owner_id"]), "validation-old-contact"}
                        for message in outcome.get("outreach", [])), "Autonomy recipient is not a fixture contact")
    log_path = root / f"{prefix}-unit-tests.log"
    log_bytes = log_path.read_bytes()
    log = log_bytes.decode("utf-16" if log_bytes[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8-sig")
    counts = re.findall(r"Ran (\d+) tests?", log)
    require(bool(counts) and bool(re.search(r"^OK\s*$", log, re.MULTILINE))
            and not re.search(r"^FAILED\b", log, re.MULTILINE), "Unit-test log did not pass")
    metrics = {variant: aggregate(sources[variant]["summaries"]) for variant in ("baseline", "decisions")}
    prior_costs = prior["matched_exchange_comparison"]["costs"]["decisions"]
    prior_metrics = aggregate(prior_costs)
    review = read_json(args.behavior_review) if args.behavior_review else None
    program_checks = read_json(args.program_checks) if args.program_checks else None
    if program_checks is not None:
        require(isinstance(program_checks, dict) and all(value is True for value in program_checks.values()),
                "Additional program checks did not pass")
    result = {
        "date": args.date, "branch": args.branch, "data_source": "Synthetic fixtures; no production conversation or credentials.",
        "implementation": ["Original processing stages retained; compatible choices evaluated in shared batches.",
            "User sentiment, relationship, summary and identity share one refresh evaluation and one required writer.",
            "Memory worthiness, significance and emotional impacts share one memory evaluation.",
            "Dependent participation, prose and final-expression evaluations retain their ordering.",
            "Compact semantic context retains state dimensions/descriptions, identity, relationships, messages and commitments.",
            "Validated native judgments are accepted directly; state bounds, grounding and revision conflict checks remain."],
        "policy": {**prior.get("policy", {}), "cost": "Observed differences only; no lower-cost requirement."},
        "validation": {"automated_tests_passed": int(counts[-1]), "unit_command": "python -m unittest discover -s tests -v",
            "local_fixture_checks": sum(len(run["checks"]) for run in sources["fixture"]["runs"]),
            "local_live_checks": sum(len(run["checks"]) for run in sources["live"]["runs"]),
            "local_fixture": sources["fixture"], "local_live_final": sources["live"]["runs"],
            "complete_accounting": True, "state_bounds": True, "matching_scenarios": True,
            "one_recovery_per_phase": True, "credentials_absent": True, "additional_program_checks": program_checks},
        "matched_exchange_comparison": {"scenarios": len(cases), "exchanges_per_variant": args.expected_exchanges,
            "cold_per_variant": sum(row["cache_mode"] == "cold" for row in sources["baseline"]["outcomes"]),
            "warm_per_variant": sum(row["cache_mode"] == "warm" for row in sources["baseline"]["outcomes"]),
            "clock": sources["decisions"]["clock"], "seed": sources["decisions"]["seed"], "snapshot": snapshot, "cases": cases,
            "report": build_report(sources["baseline"]["summaries"] + sources["decisions"]["summaries"]),
            "aggregates": metrics, "baseline_vs_decisions": difference(metrics["baseline"], metrics["decisions"]),
            "costs": {variant: sources[variant]["summaries"] for variant in ("baseline", "decisions")},
            "outcomes": {variant: without_provenance(sources[variant]["outcomes"]) for variant in ("baseline", "decisions")}},
        "prior_decisions_vs_compact": {"prior_report": str(args.prior), "prior_exchanges": len(prior_costs),
            "compact_exchanges": args.expected_exchanges, "prior": prior_metrics, "compact": metrics["decisions"],
            "changes": difference(prior_metrics, metrics["decisions"])},
        "paired_autonomy": {"snapshot": prior["paired_autonomy"]["snapshot"],
            "clock": sources["decisions"]["clock"], "seeds": {"contextual": 0, "random": 1},
            "outcomes": without_provenance(autonomy),
            "report": build_report([row["cost"] for outcomes in autonomy.values() for row in outcomes])},
        "behavior_review": review,
        "source_files": {key: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                         for key, path in {**paths, "snapshot": snapshot_path, "cases": Path(args.cases),
                                           "prior": Path(args.prior), "unit_log": log_path}.items()},
        "limitations": ["Small stochastic sample; recorded pricing estimates are not invoice reconciliation.",
            "Cold/warm name input-marker cohorts. Actual cache usage is recorded, not assumed.",
            "Sequential runs and changing provider/cache conditions affect latency; this is not an isolated randomized latency benchmark.",
            "Autonomy has two controlled branches per variant and is excluded from message-exchange averages.",
            "Local API/worker smoke checks use independent profiles; their costs are not matched comparisons.",
            "Prior native measurements ran on another date; model/provider conditions can change.",
            "No automated quality score or blanket equivalence judgment is inferred from successful execution."]}
    check_credentials(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-dir", default=".venv/validation")
    parser.add_argument("--prefix", default="compact")
    parser.add_argument("--snapshot")
    parser.add_argument("--cases", default="scripts/fixtures/decisions_cases.json")
    parser.add_argument("--prior", required=True, help="Existing local comparison report; generated reports are not tracked")
    parser.add_argument("--output", default=".validation/decisions-comparison.json")
    parser.add_argument("--date", default="2026-10-13")
    parser.add_argument("--branch", default="feature/decisions")
    parser.add_argument("--expected-exchanges", type=int, default=30)
    parser.add_argument("--warm-repetitions", type=int, default=2)
    parser.add_argument("--behavior-review")
    parser.add_argument("--program-checks")
    args = parser.parse_args()
    try:
        payload = build_validation(args)
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        require(read_json(target) == payload, "Saved report did not round-trip")
    except (ValueError, KeyError, FileNotFoundError) as exc:
        parser.error(str(exc))
    print(json.dumps({"path": str(target), "bytes": target.stat().st_size,
        "tests": payload["validation"]["automated_tests_passed"],
        "aggregates": {variant: {key: value for key, value in metrics.items() if key in {
            "complete_total_cost_usd", "average_complete_exchange_cost_usd", "observed_tokens", "total_api_attempts",
            "fallback_attempts", "average_complete_execution_latency_ms"}}
            for variant, metrics in payload["matched_exchange_comparison"]["aggregates"].items()}}, indent=2))


if __name__ == "__main__":
    main()
