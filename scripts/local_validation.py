"""Run the actual loopback API and RQ worker against isolated Mongo and Redis.

Default provider is an explicit deterministic HTTP fixture, not a live provider.
Usage: python -m scripts.local_validation --output .validation/local.json
Use --provider live only when paid provider calls are intended. Local services
must already exist at the dedicated ports; the runner never starts containers.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import time
from urllib.parse import urlparse
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
MESSAGE = "Jasmine, thank you for being here. Talking with you makes me happy."


def validate_services(mongo_uri: str, redis_url: str, database: str) -> None:
    """Reject production/shared endpoints even when explicitly supplied."""
    mongo, redis = urlparse(mongo_uri), urlparse(redis_url)
    for endpoint in (mongo, redis):
        if endpoint.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Validation services must use loopback addresses")
        if endpoint.username or endpoint.password:
            raise ValueError("Validation services must not contain credentials")
    if mongo.scheme != "mongodb" or mongo.port != 27028:
        raise ValueError("Validation requires dedicated Mongo port 27028")
    if redis.scheme != "redis" or redis.port != 16379 or redis.path != "/15":
        raise ValueError("Validation requires dedicated Redis port 16379, database 15")
    if not database.startswith("syntheticsoul_replay_") or not all(c.islower() or c.isdigit() or c == "_" for c in database):
        raise ValueError("Validation database requires the syntheticsoul_replay_ prefix")


def fixture_value(schema: dict, path: tuple[str, ...] = ()):
    """Generate schema-shaped fixture content; this does not simulate intelligence."""
    key = path[-1] if path else ""
    kind = schema.get("type", "object" if "properties" in schema else "string")
    if isinstance(kind, list):
        kind = next((value for value in kind if value != "null"), "null")
    if "enum" in schema:
        preferred = {"response_choice": "respond", "directive": "unchanged", "expression": "unchanged"}.get(key)
        return preferred if preferred in schema["enum"] else schema["enum"][0]
    if kind == "object":
        properties = schema.get("properties", {})
        if key == "deltas" and not properties:
            return {"joy": 7} if "emotion_deltas" in path else {}
        return {name: fixture_value(child, path + (name,)) for name, child in properties.items()}
    if kind == "array":
        return [fixture_value(schema["items"], path + (str(i),)) for i in range(schema.get("minItems", 0))]
    if kind in {"number", "integer"}:
        if key == "confidence":
            return 0.7
        if key == "joy" and "deltas" in path:
            return 7
        return max(0, schema.get("minimum", 0))
    if kind == "boolean":
        return False
    if kind == "null":
        return None
    values = {"response_choice": "respond", "message": "I appreciate that. It feels good to share this moment with you.",
              "purpose": "affection", "tone": "friendly", "thought": "no", "new_expression": "no",
              "expression": "neutral_listening", "reason": "Deterministic local HTTP fixture",
              "summary": "", "identity": "", "extrinsic_relationship": "stranger", "event": "", "thoughts": ""}
    return values.get(key, "fixture" if schema.get("minLength", 0) else "")


def fixture_decisions(questions: list[dict]) -> list[dict]:
    answers = []
    for question in questions:
        name, kind = question["name"], question["type"]
        if kind == "predicate":
            answers.append({"name": name, "type": kind, "probability": 0.01})
        elif kind == "choice":
            values = [item["value"] for item in question["choices"]]
            preferred = {"emotion_joy": "7", "purpose": "affection", "tone": "friendly",
                         "directive": "unchanged", "participation": "respond", "relationship": "stranger",
                         "expression": "unchanged"}.get(name, "0")
            choice = preferred if preferred in values else values[0]
            answers.append({"name": name, "type": kind, "choice": choice, "confidence": 1.0,
                            "probabilities": [{"value": value, "probability": float(value == choice)} for value in values]})
        else:
            answers.append({"name": name, "type": kind, "score": 0, "confidence": 1.0,
                            "probabilities": [{"value": i, "label": level["label"], "probability": float(i == 0)}
                                              for i, level in enumerate(question["levels"])]})
    return answers


class FixtureHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        identifier = "fixture_" + str(uuid4())
        if self.path.rstrip("/") == "/v1/decisions":
            payload = {"id": identifier, "object": "decision", "created_at": int(time.time()), "model": request["model"],
                       "answers": fixture_decisions(request["questions"]),
                       "usage": {"input_tokens": 100, "output_tokens": 0, "total_tokens": 100,
                                 "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                                 "output_tokens_details": {"reasoning_tokens": 0}}}
        elif self.path.rstrip("/") == "/v1/chat/completions":
            schema = request["response_format"]["json_schema"]["schema"]
            payload = {"id": identifier, "object": "chat.completion", "created": int(time.time()), "model": request["model"],
                       "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": json.dumps(fixture_value(schema))}}],
                       "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120,
                                 "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 0}}}
        else:
            self.send_error(404)
            return
        encoded = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("x-request-id", identifier)
        self.end_headers()
        self.wfile.write(encoded)


@contextmanager
def fixture_provider():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def stop_process(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        # RQ may launch a scheduler child. Stop only this runner's process tree.
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW, timeout=15, check=False)
        process.wait(timeout=5)
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def start_process(arguments, environment):
    # Never capture app output: provider errors can contain text. The report has
    # explicit check outcomes; subprocesses do not expose credentials or JWTs.
    environment = {**environment, "PYTHONUNBUFFERED": "1"}
    return subprocess.Popen([sys.executable, *arguments], cwd=ROOT, env=environment,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def wait_for(function, timeout=90, interval=0.5):
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            value = function()
            if value:
                return value
        except Exception as exc:
            last_error = type(exc).__name__
        time.sleep(interval)
    raise RuntimeError("Validation timed out" + (f" ({last_error})" if last_error else ""))


def run_variant(args, variant, provider_url=None):
    import httpx2 as httpx
    from pymongo import MongoClient
    from redis import Redis
    from rq.job import Job

    database = "syntheticsoul_replay_local_" + uuid4().hex
    validate_services(args.mongo_uri, args.redis_url, database)
    env = os.environ.copy()
    # Override legacy .env aliases explicitly. Never route to saved hosted services.
    env.update({"APP_ENV": "test", "MONGO_MODE": "local", "MONGO_CONNECTION_LOCAL": args.mongo_uri,
                "MONGO_CONNECTION": args.mongo_uri, "DATABASE_NAME": database,
                "REDIS_URL": args.redis_url, "REDIS_TLS_URL": "", "BOT_NAME": "jasmine", "MODE": "lite",
                "LLM_MODE": "hosted", "DEBUG_MODE": "false", "DECISIONS_ENABLED": str(variant == "decisions").lower(),
                "DECISIONS_FEATURES": "all", "COST_TRACKING_ENABLED": "true",
                "GPT_FAST_MODEL": "gpt-4o-mini", "GPT_QUALITY_MODEL": "gpt-5-mini",
                "JWT_SECRET_ENV": "isolated-local-validation-secret-" + uuid4().hex,
                "ARGON2_PEPPER_ENV": "isolated-local-validation-pepper-" + uuid4().hex,
                "THINKING_RATE_SECONDS": "86400", "EMOTIONAL_DECAY_RATE_SECONDS": "86400"})
    if provider_url:
        env.update({"OPENAI_API_KEY": "local-validation-no-secret", "OPENAI_BASE_URL": provider_url})
    else:
        env.pop("OPENAI_BASE_URL", None)
    mongo = MongoClient(args.mongo_uri, serverSelectionTimeoutMS=5000)
    redis = Redis.from_url(args.redis_url)
    mongo.admin.command("ping")
    redis.ping()
    # This dedicated DB belongs only to this runner. Refuse to interrupt another run.
    if redis.dbsize():
        raise ValueError("Dedicated Redis DB15 must be empty before validation")
    processes = []
    checks = {}
    report = {"variant": variant, "provider": args.provider, "checks": checks,
              "database": database, "fixture_costs_are_synthetic": args.provider == "fixture",
              "scope": "local API/worker integration smoke; live matched-snapshot behavior and cost comparisons require scripts.replay"}
    def check(name, result):
        checks[name] = bool(result)
        if not result:
            raise AssertionError("Validation check failed: " + name)
    try:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", args.port))
        processes.append(start_process(["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(args.port)], env))
        with httpx.Client(base_url=f"http://127.0.0.1:{args.port}", timeout=10) as client:
            wait_for(lambda: client.get("/v1/meta/ping").status_code == 200)
            check("api_started", processes[0].poll() is None)
            # The existing lifespan performs one initial autonomous pass. Let it
            # finish before seeding controlled state; periodic runs sleep 24h.
            wait_for(lambda: bool(list(mongo[database].api_cost_runs.find({"kind": "autonomy"}))) and
                     all(run.get("phases", {}).get("autonomy", {}).get("status") in {"completed", "failed"}
                         for run in mongo[database].api_cost_runs.find({"kind": "autonomy"})), timeout=args.timeout)
            processes.append(start_process(["-m", "app.worker"], env))
            wait_for(lambda: client.get("/v1/meta/queue").json().get("worker_count", 0) >= 1)
            check("worker_registered", processes[1].poll() is None)
            metadata = client.get("/v1/meta/llm").json()
            check("decisions_flag", metadata["decisions"]["enabled"] == (variant == "decisions"))
            guest = client.post("/v1/auth/guest")
            check("guest_authentication", guest.status_code == 200)
            headers = {"Authorization": "Bearer " + guest.json()["access_token"]}
            owner = client.get("/v1/auth/me", headers=headers).json()["user_id"]
            other = client.post("/v1/auth/guest")
            other_headers = {"Authorization": "Bearer " + other.json()["access_token"]}
            mongo[database].agent_lite.update_one({"name": "jasmine"}, {"$set": {"emotional_status.emotions.joy.value": 50}})
            check("submit_requires_authentication", client.post("/v1/messages/submit", json={"message": MESSAGE, "type": "dm"}).status_code == 401)
            submitted = client.post("/v1/messages/submit", headers=headers, json={"message": MESSAGE, "type": "dm"})
            check("message_enqueued", submitted.status_code == 202)
            job_id = submitted.json()["job_id"]
            reserved_id = Job.fetch(job_id, connection=redis).meta.get("background_job_id")
            check("background_reserved_at_submission", reserved_id == job_id + ":background"
                  and Job.exists(reserved_id, connection=redis))
            job_path = f"/v1/jobs/{job_id}"
            check("job_owner_denial", client.get(job_path, headers=other_headers).status_code == 404)
            check("cost_owner_denial", client.get(job_path + "/cost", headers=other_headers).status_code == 404)
            check("cost_requires_authentication", client.get(job_path + "/cost").status_code == 401)
            def job_done():
                response = client.get(job_path, headers=headers)
                response.raise_for_status()
                payload = response.json()
                return payload if payload["status"] in {"succeeded", "failed"} else None
            result = wait_for(job_done, timeout=args.timeout)
            report["job_status"] = result["status"]
            # Public response is useful human-review evidence. Authentication
            # tokens, identity, sessions and provider request bodies stay omitted.
            report["public_response"] = result.get("result")
            check("reply_job_succeeded", result["status"] == "succeeded")
            check("response_shape", isinstance(result.get("result"), dict) and {"response", "time", "expression"} <= set(result["result"]))
            if args.provider == "fixture":
                check("fixture_reply_generated", result["result"]["response"] == "I appreciate that. It feels good to share this moment with you.")
            else:
                check("reply_is_not_error_placeholder", result["result"]["response"] !=
                      "I hit a thinking issue on my side, but I should be good now. Could you resend that once?")
            def cost_done():
                response = client.get(job_path + "/cost", headers=headers)
                response.raise_for_status()
                payload = response.json()
                return payload if payload["execution_status"] != "pending" else None
            cost = wait_for(cost_done, timeout=args.timeout)
            report["cost"] = cost
            check("background_job_completed", cost["execution_status"] == "completed")
            if args.provider == "fixture":
                check("fixture_usage_accounted", cost["accounting_complete"] and cost["attempt_count"] > 0)
                check("state_endpoint_selection", ("reply_state" in cost["stages"] and "reply_state_fallback" not in cost["stages"])
                      if variant == "decisions" else "reply_state_fallback" in cost["stages"])
            check("exchange_owner_persisted", mongo[database].api_cost_runs.find_one({"run_id": job_id})["owner_id"] == owner)
            raw_attempts = list(mongo[database].api_cost_attempts.find({"run_id": job_id}))
            check("attempts_present", bool(raw_attempts))
            check("attempt_ids_unique", len({a["attempt_id"] for a in raw_attempts}) == len(raw_attempts))
            check("cost_records_have_no_content", not any(set(a) & {"prompt", "messages", "content", "response", "api_key", "access_token"} for a in raw_attempts))
            user_message = mongo[database].message.find_one({"sender_id": owner, "from_agent": False})
            check("original_message_persisted", bool(user_message) and user_message.get("original_message") == MESSAGE)
            profile = mongo[database].user_lite.find_one({"user_id": owner, "agent_perspective": "jasmine"})
            check("exchange_sequence_forwarded_and_committed", user_message.get("interaction_sequence") ==
                  profile.get("interaction_sequence") == profile.get("last_refreshed_sequence") == 1)
            check("user_message_persisted_once", mongo[database].message.count_documents({"sender_id": owner, "from_agent": False}) == 1)
            joy = mongo[database].agent_lite.find_one({"name": "jasmine"})["emotional_status"]["emotions"]["joy"]["value"]
            report["joy_before"] = 50
            report["joy_after"] = joy
            if args.provider == "fixture":
                check("state_semantics", joy == (57 if variant == "decisions" else 52))
            Job.fetch(job_id, connection=redis).delete()
            check("redis_job_expired", client.get(job_path, headers=headers).status_code == 404)
            surviving = client.get(job_path + "/cost", headers=headers)
            check("cost_survives_redis_expiry", surviving.status_code == 200 and surviving.json()["attempt_count"] == cost["attempt_count"])
            check("owner_denial_after_expiry", client.get(job_path + "/cost", headers=other_headers).status_code == 404)
            report["passed"] = True
    except Exception as exc:
        report["passed"] = False
        report["error"] = str(exc) if isinstance(exc, (AssertionError, ValueError, RuntimeError)) else type(exc).__name__
    finally:
        for process in reversed(processes):
            stop_process(process)
        if not args.keep_data:
            mongo.drop_database(database)
        redis.flushdb()
        mongo.close()
        redis.close()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--variant", choices=("baseline", "decisions", "both"), default="both")
    parser.add_argument("--mongo-uri", default="mongodb://127.0.0.1:27028")
    parser.add_argument("--redis-url", default="redis://127.0.0.1:16379/15")
    parser.add_argument("--port", type=int, default=18001)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--keep-data", action="store_true")
    args = parser.parse_args(argv)
    validate_services(args.mongo_uri, args.redis_url, "syntheticsoul_replay_validation")
    variants = ("baseline", "decisions") if args.variant == "both" else (args.variant,)
    if args.provider == "fixture":
        with fixture_provider() as provider_url:
            reports = [run_variant(args, variant, provider_url) for variant in variants]
    else:
        reports = [run_variant(args, variant) for variant in variants]
    payload = {"provider": args.provider, "fixture_results_are_not_live_comparison": args.provider == "fixture",
               "runs": reports, "passed": all(report["passed"] for report in reports)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"provider": args.provider, "passed": payload["passed"], "runs": [
        {"variant": report["variant"], "passed": report["passed"], "checks": len(report["checks"]), "error": report.get("error")}
        for report in reports]}))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
