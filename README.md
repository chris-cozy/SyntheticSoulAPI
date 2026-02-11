# Synthetic Soul API (J.A.S.M.I.N.E)

Synthetic Soul is an experimental artificial intelligence project designed to simulate human-like emotions, thought patterns, and relationship dynamics. Its purpose is to create a digital mind that not only responds to user input but also develops an evolving personality, one that reflects emotional depth, personal biases, and individualized sentiments toward different users shaped by unique experiences.

The AI is named Jasmine, short for Just a Simulation Modeling Interactive Neural Engagement, to reflect both its experimental nature and its focus on simulating authentic engagement.

## Features

- Emotion simulation with decay, reinforcement, and contextual shifts
- Rich and Lite personality schemas for lightweight or deeper simulation
- Persistent memory and relationship context backed by MongoDB
- Autonomous thinking loops independent of direct user prompts
- Relationship dynamics that evolve based on interaction history
- Async message processing with Redis + RQ workers
- Structured LLM integration with OpenAI (hosted) and Ollama (local) providers

## Philosophy

*Jasmine* explores affective computing and digital companionship by blending artificial intelligence with principles from psychology and human relationship studies. The goal is not just interaction but **evolution** — an AI that grows and adapts with users over time.

## Project Docs

- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Contributing](docs/CONTRIBUTING.md)

Synthetic Soul API is a FastAPI service that powers the runtime backend with:

- authenticated guest/user sessions
- async message processing via Redis + RQ
- persistent memory/state in MongoDB
- optional LLM backends (OpenAI, Ollama)

This document is a full setup and operations guide for local development on macOS, Linux, or Windows.

## API Versioning

Current version: `1.1.0`

Versioning policy:

- URL versioning uses the **major** version (`/v1/...`)
- **Breaking** changes require a major bump (`v2`)
- **Non-breaking** additions/fixes use minor/patch bumps (`1.1.x`, `1.2.x`)

Runtime version metadata:

- `GET /v1/meta/version`
- `X-API-Version` response header on all API responses

## Key Endpoints

- `GET /v1/` -> active agent name
- `GET /v1/meta/ping` -> liveness check
- `GET /v1/meta/version` -> semver + versioning metadata
- `GET /v1/meta/queue` -> Redis queue + worker diagnostics
- `GET /v1/meta/llm` -> active LLM mode/provider/model diagnostics
- `POST /v1/auth/guest` -> create guest session + access token
- `POST /v1/auth/login` -> login with email/password
- `POST /v1/auth/claim` -> convert guest account to password account
- `POST /v1/auth/refresh` -> rotate refresh/access tokens
- `POST /v1/auth/logout` -> revoke current session
- `GET /v1/auth/me` -> current identity claims
- `POST /v1/messages/submit` -> enqueue async response job
- `GET /v1/jobs/{job_id}` -> poll job status/result
- `GET /v1/jobs/{job_id}/events` -> SSE job progress/status stream
- `GET /v1/messages/conversation` -> current conversation
- `GET /v1/agents/active` -> active agent state
- `GET /v1/thoughts/latest` -> latest thought

## Architecture (Runtime)

- API server: FastAPI (`app/main.py`)
- Worker: RQ worker (`python -m app.worker`)
- Queue transport: Redis
- Persistence: MongoDB
- Background loops: emotional decay + periodic thinking

## Prerequisites

- Python `3.10+`
- Redis `6+`
- MongoDB `6+`
- Optional: Docker Desktop (recommended for cross-platform local infra)

## Containerized Deployment (Docker)

Use this for Linux server deployment. Two compose modes are available:

### Option A: API + Worker only (external Redis/Mongo)

Runs `api` + `worker` and expects Redis/Mongo to exist outside this compose project.

```bash
docker compose -f docker-compose.api.yml up -d --build
```

`docker-compose.api.yml` reads env vars from `.env`.

If Redis/Mongo run directly on the Linux host, use:

```env
MONGO_MODE=local
MONGO_CONNECTION_LOCAL=mongodb://host.docker.internal:27017
REDIS_URL=redis://host.docker.internal:6379/0
```

(`host.docker.internal` is mapped in this file using `extra_hosts`.)

### Option B: Full backend stack (API + Worker + Redis + Mongo)

Runs everything in containers, including data services and persistent volumes:

```bash
docker compose up -d --build
```

`docker-compose.yml` automatically wires:

- API + worker to `redis://redis:6379/0`
- API + worker to `mongodb://mongo:27017`
- persistent volumes (`redis_data`, `mongo_data`)

For this mode, keep `.env` focused on app settings/secrets (for example LLM keys, `DATABASE_NAME`, JWT/Argon2 secrets).

### Verify runtime health

```bash
docker compose ps
docker logs -f synthetic-soul-api
docker logs -f synthetic-soul-worker
curl http://127.0.0.1:8000/v1/meta/ping
```

To stop either mode:

```bash
docker compose down
docker compose -f docker-compose.api.yml down
```

## Local Setup

### 1) Start Redis and MongoDB

Docker (recommended, same on macOS/Linux/Windows):

```bash
docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
docker run -d --name mongo -p 27017:27017 -v mongo_data:/data/db mongo:7
```

### 2) Create and activate a virtual environment

macOS/Linux:

```bash
cd SyntheticSoulAPI
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
cd SyntheticSoulAPI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
cd SyntheticSoulAPI
py -m venv .venv
.venv\Scripts\activate.bat
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create `.env`

Minimum local `.env` (safe template values, replace keys):

```env
APP_ENV=development
BOT_NAME=jasmine
MODE=lite
LLM_MODE=hosted
MONGO_MODE=local

MONGO_CONNECTION_LOCAL=mongodb://127.0.0.1:27017
# Optional hosted Mongo URI for easy switching:
MONGO_CONNECTION_HOSTED=mongodb+srv://<user>:<pass>@<cluster>/<db>?retryWrites=true&w=majority
# Legacy fallback (still supported):
MONGO_CONNECTION=mongodb://127.0.0.1:27017
DATABASE_NAME=synthetic_soul

REDIS_URL=redis://127.0.0.1:6379/0

OPENAI_API_KEY=replace_me
GPT_FAST_MODEL=gpt-4o-mini
GPT_QUALITY_MODEL=gpt-5-mini

# Local mode (Ollama, OpenAI-compatible API)
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_API_KEY=ollama
OLLAMA_FAST_MODEL=qwen2.5:7b
OLLAMA_QUALITY_MODEL=qwen2.5:14b

JWT_SECRET_ENV=replace_with_long_random_secret
ARGON2_PEPPER_ENV=replace_with_long_random_pepper

WEB_UI_DOMAIN=http://127.0.0.1:5173
DEBUG_MODE=true
```

### 4a) Optional: run in local mode with Ollama

If you want to run LLM calls locally instead of OpenAI:

1. Install Ollama.
2. Start Ollama:

```bash
ollama serve
```

3. Pull your chosen models (examples):

```bash
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
```

4. Set `.env` for local mode:

```env
LLM_MODE=local
MONGO_MODE=local
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_API_KEY=ollama
OLLAMA_FAST_MODEL=qwen2.5:7b
OLLAMA_QUALITY_MODEL=qwen2.5:14b
```

5. Restart API + worker so new env values are loaded.
6. Verify configuration:

```bash
curl http://127.0.0.1:11434/api/tags
curl http://127.0.0.1:8000/v1/meta/llm
```

Generate strong secrets quickly:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 5) Run API server

macOS/Linux:

```bash
./.venv/bin/uvicorn app.main:app --reload
```

Windows:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

### 6) Run worker (separate terminal)

macOS/Linux:

```bash
./.venv/bin/python -m app.worker
```

Windows:

```powershell
.\.venv\Scripts\python -m app.worker
```

Notes:

- On macOS and Windows, worker defaults to `SimpleWorker` mode to avoid `fork()` issues.
- To force classic forking worker on fork-capable platforms (e.g., Linux): `RQ_USE_FORK_WORKER=true`.

### 7) Verify service health

```bash
curl http://127.0.0.1:8000/v1/meta/ping
curl http://127.0.0.1:8000/v1/meta/version
curl http://127.0.0.1:8000/v1/meta/queue
curl http://127.0.0.1:8000/v1/meta/llm
```

OpenAPI UI:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Authentication Model

Auth supports guest-first sessions and password accounts.

### Tokens

- Access token: JWT in `Authorization: Bearer ...`
- Refresh token: cookie-bound, rotated on refresh

### Refresh security (two-key check)

`POST /v1/auth/refresh` requires:

1. refresh cookies (`sid`, `rtoken`)
2. `X-CSRF-Token` header matching `refresh_csrf` cookie

This prevents cross-site refresh abuse while keeping browser-cookie refresh flow.

## Typical API Flow

### 1) Create guest

```http
POST /v1/auth/guest
```

Example response:

```json
{
  "access_token": "...",
  "username": "guest_xxx",
  "expires_in": 900
}
```

### 2) Submit message

```http
POST /v1/messages/submit
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "Good morning",
  "type": "dm"
}
```

Example response (`202 Accepted`):

```json
{
  "job_id": "uuid",
  "status": "queued"
}
```

### 3) Poll job

```http
GET /v1/jobs/{job_id}
Authorization: Bearer <access_token>
```

Status values: `queued`, `running`, `succeeded`, `failed`

### 4) Stream job events (recommended)

For long-running local-model jobs, use SSE to get push updates instead of frequent polling:

```http
GET /v1/jobs/{job_id}/events?access_token=<access_token>
```

SSE event types:

- `progress` -> progress updates from Redis pub/sub (`job:{job_id}`)
- `status` -> normalized job status snapshots
- `done` -> terminal status (`succeeded` or `failed`)

Recommended client flow:

1. `POST /v1/messages/submit` to get `job_id`
2. Open `EventSource` on `/v1/jobs/{job_id}/events`
3. On `done`, make one final `GET /v1/jobs/{job_id}` to fetch canonical `result`
4. Fall back to polling if SSE disconnects

## Queue Diagnostics

`GET /v1/meta/queue` returns:

- worker count and worker states
- queue backlog per queue (`high/default/low`)
- total backlog
- redis connectivity signal

Use this endpoint first when jobs remain queued.

## Troubleshooting

### Jobs stuck in `queued`

Symptoms:

- `POST /v1/messages/submit` returns `202`
- `GET /v1/jobs/{id}` returns `200` repeatedly with `status=queued`

Checks:

1. Ensure worker process is running.
2. Check `GET /v1/meta/queue`:
   - `worker_count` should be `> 0`
   - `total_backlog` should decrease over time

### macOS worker crash (`fork()` / ObjC error)

If you see ObjC `initialize`/`fork` crash logs, run worker with current default (`SimpleWorker`) via:

```bash
./.venv/bin/python -m app.worker
```

### Windows worker crash (`os.fork` or `signal.SIGALRM` attribute errors)

Use the standard worker entrypoint (it now selects `SimpleWorker` and Windows-safe timeout handling automatically):

```powershell
.\.venv\Scripts\python -m app.worker
```

### 401 on protected endpoints right after startup

During initial app boot, client may request protected resources before guest token acquisition. This is transient and expected.

### Refresh fails (`no_refresh` / `csrf_mismatch`)

- Ensure browser sends cookies (`credentials: include`)
- Ensure client sets `X-CSRF-Token` from `refresh_csrf` cookie
- Ensure client and API origins are configured in CORS

### Missing expression image 404s

Ensure expression assets exist in `app/assets/expressions/<BOT_NAME>/` and names match expression strings.

## Configuration Reference

Required for local runtime:

- `DATABASE_NAME`
- `JWT_SECRET_ENV`
- `ARGON2_PEPPER_ENV`

Optional/commonly used:

- `MONGO_MODE` (`hosted` or `local`, default: `hosted`)
- `MONGO_CONNECTION_LOCAL` (used when `MONGO_MODE=local`, default: `mongodb://127.0.0.1:27017`)
- `MONGO_CONNECTION_HOSTED` (used when `MONGO_MODE=hosted`)
- `MONGO_CONNECTION` (legacy fallback if mode-specific URI is not set)
- `LLM_MODE` (`hosted` or `local`, default: `hosted`)
- Hosted mode:
  - `OPENAI_API_KEY`
  - `GPT_FAST_MODEL`
  - `GPT_QUALITY_MODEL`
- Local mode (Ollama):
  - `OLLAMA_BASE_URL` (default: `http://127.0.0.1:11434/v1`)
  - `OLLAMA_API_KEY` (default: `ollama`)
  - `OLLAMA_FAST_MODEL`
  - `OLLAMA_QUALITY_MODEL`
- `REDIS_URL` (defaults to `redis://localhost:6379/0`)
- `REDIS_TLS_URL`, `REDIS_CA_CERT`, `REDIS_TLS_INSECURE_SKIP_VERIFY`
- `BOT_NAME`, `MODE`, `DEVELOPER_EMAIL`
- `ACCESS_TTL_MIN`, `REFRESH_TTL_DAYS`
- `THINKING_RATE_SECONDS`, `EMOTIONAL_DECAY_RATE_SECONDS`
- `WEB_UI_DOMAIN`
- `APP_ENV`, `DEBUG_MODE`

## Development Notes

- Use queue diagnostics endpoint during worker/queue debugging.
- Keep API and worker logs in separate terminals.
- When changing contracts, update both API and WebUI in lockstep.

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution workflow and expectations.

## License

MIT License.
