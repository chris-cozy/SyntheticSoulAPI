# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-10-11

### Added
- Hosted Decisions evaluation for state changes, subjective perception, addressing, participation, relationships, durable identity/summary gates, memory metadata, expressions and autonomous behavior.
- Direct bounded Decisions deltas with per-dimension provenance and partial generative fallback preserving legacy calculations.
- Revision-checked agent/user cognition updates, bounded conflict re-evaluation, uncertain-write readback and deterministic emotional decay.
- Durable cost accounting across reply jobs, background work and autonomous passes; physical API attempts capture usage before SDK parsing, including retries and fallbacks.
- Owner-authenticated `GET /v1/jobs/{job_id}/cost`, versioned decimal pricing estimates, incomplete/unknown accounting and diagnostics in `/v1/meta/llm`.
- Cost/latency reporting and isolated baseline/Decisions replay with fixed application time, seeded randomness, cold/warm cohorts and labeled review scenarios.
- Automated regression tests and CI test execution.

### Changed
- Upgraded OpenAI SDK to `3.26.0` and compatible dependencies; Decisions is enabled by default in hosted mode with `DECISIONS_ENABLED=false` as an opt-out, and local Ollama stays on the generative path.
- Preserved original user input independently of perceived metadata, constrained outreach to real profiles with at most three recipients, and selected expressions from installed assets.
- Kept personality changes interaction-local and cost differences observational, without a lower-cost acceptance requirement.
- Accepted validated routine subjective Decisions results without a confidence veto, removed standalone expression recovery, and limited native recovery to one attempt per reply/background/autonomy phase while preserving accepted results and recording exhaustion.
- Batched compatible refresh and memory decisions within the original stages; shortened per-dimension questions and supplied shared state guidance once, with compact native evidence and prose context preserving emotions, personality, relationships and independent outreach checks.

### Fixed
- Prevented cost reconciliation from overwriting concurrent worker completion, refreshed interaction timestamps independently of sentiment changes, bounded outreach context with targeted older-contact lookup, and removed fixed agent names from native prompts.
- Propagated required persistence failures, guarded user refreshes with durable exchange sequences, scoped tagged recall to the active agent, and prioritized explicitly named outreach contacts before memory-linked candidates.
- Reserved per-user background dependency chains at submission so faster later replies cannot skip earlier durable updates; retained deferred payloads independently of reply-result expiry and released later work after predecessor failures.
- Preserved both the pre-message thought and any perception-updated thought in native reply context, including directive status, without changing thought-generation rules.

## [1.1.1] - 2026-02-08

### Added
- API request correlation via `X-Request-ID` response header.
- Global API version exposure via `X-API-Version` response header.
- Structured error envelope for HTTP/validation/unhandled failures (`error.code`, `error.message`, `error.request_id`).
- Queue diagnostics endpoint at `GET /v1/meta/queue`.
- LLM diagnostics endpoint at `GET /v1/meta/llm`.
- Local LLM runtime mode via Ollama (OpenAI-compatible local inference path).
- Global environment toggle to switch between hosted and local LLM execution modes.
- LLM diagnostics endpoint updates to expose active mode/provider/model for easier debugging.
- Refresh-session CSRF protection for `POST /v1/auth/refresh` using `refresh_csrf` cookie + `X-CSRF-Token` header validation.
- Session persistence of `csrf_hash` for refresh validation.
- Job ownership enforcement for polling (`GET /v1/jobs/{job_id}`) using `owner_user_id`.
- Job progress streaming over SSE at `GET /v1/jobs/{job_id}/events`.
- Job pub/sub payload helper (`publish_job_event`) supporting status/progress/error events.
- UI support for SSE-first job tracking with a final result fetch and polling fallback.
- Expression static compatibility loader at `GET /static/expressions/{agent}/{filename}` with extension fallback (`.jpeg/.jpg/.png/.webp/.gif`) and alias support (`neutral -> neutral_listening`).
- Project docs expansion with `docs/PROJECT_OVERVIEW.md`, `docs/ROADMAP.md`, `docs/CONTRIBUTING.md`, and changelog link in README.
- Expanded local setup documentation for Ollama in the README.
- MongoDB mode toggle via `MONGO_MODE` with separate local/hosted URI env vars.

### Changed
- API versioning moved to semver-aware config (`API_VERSION = 1.1.0`) and `API_BASE_PATH` is derived from major version (`/v{major}`).
- `GET /v1/meta/version` now includes semver breakdown and versioning policy metadata.
- FastAPI router mounting now uses `API_BASE_PATH` instead of hardcoded `/v1`.
- `POST /v1/messages/submit` now enforces per-user rate limiting, returns typed `202` response model, sets version-aware `Location` header (`{API_BASE_PATH}/jobs/{job_id}`), and publishes an initial queued job event.
- `GET /v1/jobs/{job_id}` now enforces per-user polling rate limits, normalizes RQ status values (`queued/running/succeeded/failed`), and returns sanitized failure message (`job_failed`) instead of internal stack traces.
- Async job lifecycle now emits richer status events (`queued`, `running`, `succeeded`, `failed`) through Redis pub/sub.
- Message submit flow now publishes an initial queued event for immediate client feedback.
- Job completion handling now publishes explicit terminal status events for better frontend synchronization.
- Auth/session flow tightened with login/claim rate limiting; refresh no longer depends on bearer auth and instead uses cookie + CSRF pair.
- Input contracts hardened in models with message length bounds (`1..4000`) and constrained message type (`dm | group`).
- Redis TLS behavior hardened with CA cert support and opt-in insecure verification only in dev/local modes.
- Worker/runtime reliability updates: macOS defaults to `SimpleWorker` unless explicitly overridden, and worker tasks use a persistent event loop to avoid per-job loop churn.
- Database write paths updated to await async calls consistently and normalize relationship labels.
- README rewritten into comprehensive, cross-platform local setup and operations guide.

### Fixed
- `RuntimeError: Event loop is closed` during post-processing tasks in worker context.
- macOS ObjC `fork()` crash behavior in worker execution path.
- Stuck job troubleshooting visibility via queue diagnostics and richer job state signals.
- Local model output reliability around structured fields used by persistence/validation.
- Failure-path handling for reply generation jobs to surface terminal failed state consistently.
- Missing expression asset resolution when UI requested mismatched name/extension
  (e.g., `neutral.jpeg` vs `neutral_listening.png`).

### Removed
- Legacy DeepSeek configuration surface and unused `app/services/deepseek.py` module.
- DeepSeek references from setup and overview documentation.

### Security
- Non-dev startup validation for auth secrets and Redis TLS safety blocks default JWT/Argon2 placeholder secrets, enforces minimum secret lengths, and disallows insecure Redis TLS verification outside dev/test/local.
