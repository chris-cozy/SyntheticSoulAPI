"""Isolated live comparison using an explicitly supplied cognition snapshot.

python -m scripts.replay --snapshot snapshot.json                  # dry run
python -m scripts.replay --snapshot snapshot.json --live           # paid API calls

Snapshot (Mongo Extended JSON): {"owner_id": "...", "agent_name": "jasmine",
"mode": "lite", "collections": {"agent_lite": [...], "user_lite": [...], ...}}.
Only cognition/conversation collections are accepted; authentication is excluded.
Each input repetition restores the same snapshot. Separate subprocesses prevent
imported configuration or provider state from leaking between variants.
"""
import argparse
import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys
from uuid import uuid4

ALLOWED_COLLECTIONS = {"agent", "agent_lite", "user", "user_lite", "conversation", "message", "memory", "thought", "state_events"}
PREFIX = "syntheticsoul_replay_"
DEFAULT_CASES = Path(__file__).parent / "fixtures" / "decisions_cases.json"


def safe_database_name(name):
    if not name.startswith(PREFIX) or not re.fullmatch(r"[a-z0-9_]{1,63}", name):
        raise ValueError("Replay database must have the syntheticsoul_replay_ prefix and contain only lowercase letters, digits, underscores")
    return name


def validate_snapshot(snapshot):
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("collections"), dict):
        raise ValueError("Snapshot needs a collections mapping")
    if not snapshot.get("owner_id") or not snapshot.get("agent_name"):
        raise ValueError("Snapshot needs owner_id and agent_name")
    if snapshot.get("mode") not in {"lite", "rich"}:
        raise ValueError("Snapshot mode must be lite or rich")
    unexpected = set(snapshot["collections"]) - ALLOWED_COLLECTIONS
    if unexpected:
        raise ValueError(f"Unsupported snapshot collections: {sorted(unexpected)}")
    if any(not isinstance(docs, list) or any(not isinstance(doc, dict) for doc in docs)
           for docs in snapshot["collections"].values()):
        raise ValueError("Each snapshot collection must contain a list of documents")
    if any("_id" not in doc for docs in snapshot["collections"].values() for doc in docs):
        raise ValueError("Snapshot documents must retain their original _id so repetitions use identical evidence")
    suffix = "_lite" if snapshot["mode"] == "lite" else ""
    agents = snapshot["collections"].get("agent" + suffix, [])
    users = snapshot["collections"].get("user" + suffix, [])
    if not any(doc.get("name") == snapshot["agent_name"] for doc in agents):
        raise ValueError("Snapshot must include the active agent")
    if not any(str(doc.get("user_id")) == str(snapshot["owner_id"]) and doc.get("agent_perspective") == snapshot["agent_name"] for doc in users):
        raise ValueError("Snapshot must include the owner's perspective profile")
    return snapshot


def load_snapshot(path):
    from bson import json_util
    return validate_snapshot(json_util.loads(Path(path).read_text(encoding="utf-8")))


def load_cases(path):
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("Replay cases must be a nonempty list")
    ids = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise ValueError("Each replay case needs a string id")
        messages = case.get("messages", [case.get("message")])
        if not isinstance(messages, list) or not messages or any(not isinstance(message, str) or not 1 <= len(message) <= 4000 for message in messages):
            raise ValueError(f"Case {case['id']} needs messages of length 1 to 4000")
        if case.get("type", "dm") not in {"dm", "group"}:
            raise ValueError(f"Case {case['id']} has an invalid message type")
        ids.append(case["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("Replay case ids must be unique")
    return cases


def fixed_datetime(value):
    fixed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if fixed.tzinfo is None:
        fixed = fixed.replace(tzinfo=timezone.utc)
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed.astimezone(tz) if tz else fixed.replace(tzinfo=None)
        @classmethod
        def utcnow(cls):
            return fixed.astimezone(timezone.utc).replace(tzinfo=None)
    return FixedDateTime


def check_bounds(document):
    errors = []
    for field, matrix in (("emotional_status", "emotions"), ("personality", "personality_matrix"), ("sentiment_status", "sentiments")):
        container = document.get(field, {})
        if not isinstance(container, dict):
            errors.append(f"{field}:invalid")
            continue
        for key, trait in container.get(matrix, {}).items():
            if not isinstance(trait, dict) or type(trait.get("value")) is not int or not trait.get("min", 0) <= trait["value"] <= trait.get("max", 100):
                errors.append(f"{field}.{key}:out_of_bounds")
    return errors


async def restore_snapshot(db, snapshot):
    safe_database_name(db.name)
    # Clear only cognition collections; preserve accumulated cost records.
    for collection in ALLOWED_COLLECTIONS:
        await db[collection].delete_many({})
        documents = snapshot["collections"].get(collection, [])
        if documents:
            await db[collection].insert_many(deepcopy(documents))


async def worker(args, snapshot):
    from app.core import config
    from app.domain.memory import Memory
    from app.domain.models import InternalMessageRequest
    from app.services import accounting, database, decisions, message_processor, openai as chat_service, thinking
    from scripts.cost_report import build_report
    cases = load_cases(args.cases)
    config.validate_llm_configuration()
    await database.init_db()
    db = await database.get_database()
    safe_database_name(db.name)
    fixed = fixed_datetime(args.clock)
    bindings = []
    # Patch all loaded application datetime bindings used for evidence/storage.
    for name, module in list(sys.modules.items()):
        if name.startswith("app.") and name != "app.services.accounting" and getattr(module, "datetime", None) is datetime:
            bindings.append((module, "datetime", module.datetime))
            module.datetime = fixed
    memory_clock = Memory.model_fields["ts_created"].default_factory
    Memory.model_fields["ts_created"].default_factory = fixed.now
    Memory.model_rebuild(force=True)
    marker = {"value": ""}
    original_chat = chat_service._structured_query
    async def marked_chat(messages, schema, quality=True):
        copied = deepcopy(messages)
        prefix = "Replay cache marker (ignore when interpreting this exchange): " + marker["value"] + "\n"
        if copied and isinstance(copied[0].get("content"), str):
            copied[0]["content"] = prefix + copied[0]["content"]
        else:
            copied.insert(0, {"role": "system", "content": prefix})
        return await original_chat(copied, schema, quality)
    chat_service._structured_query = marked_chat
    original_decisions = decisions.evaluate
    async def marked_decisions(evidence, questions, **kwargs):
        marked = {"replay_cache_marker_ignore": marker["value"], "evidence": evidence}
        return await original_decisions(marked, questions, **kwargs)
    # Some pipeline modules import evaluate directly; replace each binding.
    for name, module in list(sys.modules.items()):
        if name.startswith("app."):
            for attr, value in list(vars(module).items()):
                if value is original_decisions:
                    bindings.append((module, attr, value))
                    setattr(module, attr, marked_decisions)
    outcomes, summaries = [], []
    try:
        for case_index, case in enumerate(cases):
            for mode in ("cold", "warm"):
                repetitions = 1 if mode == "cold" else args.warm_repetitions
                for repetition in range(repetitions):
                    random.seed(args.seed + case_index)
                    await restore_snapshot(db, snapshot)
                    marker["value"] = f"{args.session}_{args.variant}_{case['id']}_{mode}_{repetition if mode == 'cold' else 0}"
                    for step, message in enumerate(case.get("messages", [case.get("message")])):
                        if not isinstance(message, str):
                            raise ValueError(f"Case {case['id']} needs a message string or messages list")
                        run_id = str(uuid4())
                        metadata = {"variant": args.variant, "scenario_id": case["id"], "cache_mode": mode,
                                    "flags": {"decisions": config.DECISIONS_ENABLED, "features": ",".join(sorted(config.DECISIONS_FEATURES))}, "agent_name": config.AGENT_NAME}
                        await accounting.begin_run(run_id, snapshot["owner_id"], metadata=metadata)
                        await accounting.mark_phase(run_id, "reply", "running")
                        try:
                            sequence = await database.next_interaction_sequence(str(snapshot["owner_id"]))
                            with accounting.scope(run_id, snapshot["owner_id"], phase="reply", flags=metadata["flags"]):
                                result = await message_processor.generate_response(InternalMessageRequest(message=message, type=case.get("type", "dm"), user_id=str(snapshot["owner_id"]), sequence=sequence))
                            await accounting.mark_phase(run_id, "reply", "completed")
                            await accounting.mark_phase(run_id, "background", "running")
                            with accounting.scope(run_id, snapshot["owner_id"], phase="background", flags=metadata["flags"]):
                                await message_processor.post_processing(result.user_id, result.queries, sequence=sequence)
                            await accounting.mark_phase(run_id, "background", "completed")
                            agent = await database.grab_self()
                            user = await database.grab_user(str(snapshot["owner_id"]))
                            outcomes.append({"case": case["id"], "variant": args.variant, "cache_mode": mode, "repetition": repetition,
                                "step": step, "run_id": run_id, "response": result.message_response.model_dump(),
                                "agent_state": agent, "user_state": user,
                                "bounds_errors": check_bounds(agent) + check_bounds(user),
                                "review_labels": case.get("review_labels", []), "review_notes": case.get("review_notes", "")})
                            # Keep the qualitative evidence before the next snapshot reset or DB cleanup.
                            outcomes[-1]["state_events"] = await db["state_events"].find({"run_id": run_id}).to_list(length=None)
                            outcomes[-1]["memories"] = await db["memory"].find({"agent_name": config.AGENT_NAME}).to_list(length=None)
                            outcomes[-1]["thoughts"] = await db["thought"].find({"agent_name": config.AGENT_NAME}).to_list(length=None)
                            run = await db[accounting.RUN_COLLECTION].find_one({"run_id": run_id})
                            outcomes[-1]["recovery_events"] = (run or {}).get("events", [])
                        except Exception as exc:
                            await accounting.mark_phase(run_id, "reply", "failed", error=type(exc).__name__)
                            await accounting.mark_phase(run_id, "background", "failed", error=type(exc).__name__)
                            outcomes.append({"case": case["id"], "run_id": run_id, "error_code": type(exc).__name__})
                        cost = await accounting.get_cost(run_id, snapshot["owner_id"])
                        if cost:
                            summaries.append(cost)
                    if args.autonomy:
                        # Same restored/evolved case context, same seeded random branch.
                        await thinking.generate_thought(rng=random.Random(args.seed + case_index), now=fixed.now())
                        autonomous_messages = await db["message"].find({"from_agent": True, "recipient_id": {"$exists": True}}).to_list(length=None)
                        outcomes.append({"case": case["id"], "variant": args.variant, "cache_mode": mode,
                            "repetition": repetition, "kind": "autonomy_observation", "messages": autonomous_messages,
                            "thoughts": await db["thought"].find({"agent_name": config.AGENT_NAME}).to_list(length=None),
                            "memories": await db["memory"].find({"agent_name": config.AGENT_NAME}).to_list(length=None)})
        autonomous = await db[accounting.RUN_COLLECTION].find({"kind": "autonomy"}).to_list(length=None)
        for run in autonomous:
            summaries.append(accounting.summarize_cost(run, await db[accounting.ATTEMPT_COLLECTION].find({"run_id": run["run_id"]}).to_list(length=None)))
        payload = {"variant": args.variant, "clock": args.clock, "seed": args.seed, "summaries": summaries,
                   "outcomes": outcomes, "report": build_report(summaries),
                   "limitations": ["Provider outputs remain stochastic.", "Cold inputs include a unique ignored evidence marker; warm inputs reuse that marker. Cache hits must be verified from recorded usage.",
                                    "Each repetition resets the snapshot. Messages within a multi-message case share their evolving state.",
                                    "Human review labels are expectations to assess; legacy output is not ground truth."]}
        Path(args.output).write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    finally:
        for module, attr, value in reversed(bindings):
            setattr(module, attr, value)
        chat_service._structured_query = original_chat
        Memory.model_fields["ts_created"].default_factory = memory_clock
        Memory.model_rebuild(force=True)
        if not args.keep_db:
            await database._db_client.drop_database(safe_database_name(db.name))
        database._db_client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--mongo-uri", default="mongodb://127.0.0.1:27017")
    parser.add_argument("--database-prefix", default=PREFIX)
    parser.add_argument("--output", default=".validation/replay-results.json")
    parser.add_argument("--clock", default="2026-10-11T12:00:00Z")
    parser.add_argument("--seed", type=int, default=7301)
    parser.add_argument("--warm-repetitions", type=int, default=2)
    parser.add_argument("--autonomy", action="store_true")
    parser.add_argument("--keep-db", action="store_true")
    parser.add_argument("--live", action="store_true", help="Explicitly allow paid provider calls")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--variant", choices=("baseline", "decisions"), help=argparse.SUPPRESS)
    parser.add_argument("--session", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()
    snapshot = load_snapshot(args.snapshot)
    load_cases(args.cases)
    if args.warm_repetitions < 0:
        parser.error("--warm-repetitions must be nonnegative (zero runs the cold cohort only)")
    safe_database_name(args.database_prefix + "validation")
    fixed_datetime(args.clock)
    if not args.live:
        print(json.dumps({"dry_run": True, "variants": ["baseline", "decisions"], "snapshot_collections": list(snapshot["collections"]),
                          "database_prefix": args.database_prefix, "clock": args.clock, "seed": args.seed,
                          "note": "Add --live to run provider calls in isolated test databases."}, indent=2))
        return
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    if args.worker:
        if not args.variant or not args.session:
            parser.error("Worker requires variant and session")
        name = safe_database_name(args.database_prefix + args.session + "_" + args.variant)
        os.environ.update({"APP_ENV": "test", "DATABASE_NAME": name, "MONGO_MODE": "local", "MONGO_CONNECTION_LOCAL": args.mongo_uri,
            "MODE": snapshot["mode"], "BOT_NAME": snapshot["agent_name"], "LLM_MODE": "hosted", "DEBUG_MODE": "false",
            "DECISIONS_ENABLED": "true" if args.variant == "decisions" else "false", "COST_TRACKING_ENABLED": "true", "DECISIONS_FEATURES": "all"})
        asyncio.run(worker(args, snapshot))
        return
    args.session = uuid4().hex[:12]
    outputs = []
    for variant in ("baseline", "decisions"):
        output = str(Path(args.output).with_name(Path(args.output).stem + "-" + variant + ".json").resolve())
        command = [sys.executable, "-m", "scripts.replay", "--worker", "--live", "--variant", variant, "--session", args.session,
                   "--snapshot", str(Path(args.snapshot).resolve()), "--cases", str(Path(args.cases).resolve()), "--mongo-uri", args.mongo_uri,
                   "--database-prefix", args.database_prefix, "--clock", args.clock, "--seed", str(args.seed),
                   "--warm-repetitions", str(args.warm_repetitions), "--output", output]
        if args.autonomy: command.append("--autonomy")
        if args.keep_db: command.append("--keep-db")
        subprocess.run(command, check=True)
        outputs.append(json.loads(Path(output).read_text(encoding="utf-8")))
    from scripts.cost_report import build_report
    combined = {"clock": args.clock, "seed": args.seed, "variants": outputs,
                "report": build_report([summary for output in outputs for summary in output["summaries"]])}
    Path(args.output).write_text(json.dumps(combined, indent=2, default=str), encoding="utf-8")
    print(f"Saved comparison and review outputs to {args.output}")


if __name__ == "__main__": main()
