# Synthetic Soul (Jasmine)


**Synthetic Soul** is an experimental artificial intelligence project designed to simulate human-like emotions, thought patterns, and relationship dynamics. Its purpose is to create a digital mind that not only responds to user input but also develops an evolving personality—one that reflects emotional depth, personal biases, and individualized sentiments toward different users, shaped by unique experiences.


The AI is named **Jasmine**—short for *Just a Simulation Modeling Interactive Neural Engagement*—to reflect both its experimental nature and its focus on simulating authentic engagement.


---


## 🌟 Features
- **Emotion Simulation**: Dynamic emotions with decay, reinforcement, and contextual shifts.
- **Personality Traits**: Rich and Lite personality schemas, enabling both lightweight and detailed simulations.
- **Memory System**: Persistence of conversations and experiences in MongoDB for long-term evolution.
- **Autonomous Thinking**: Periodic thought generation independent of user input.
- **Relationship Dynamics**: Sentiments and biases toward different users evolve over time.
- **Background Processing**: Redis + RQ worker queue for async message handling.
- **LLM Integration**: Structured responses powered by OpenAI and DeepSeek.


---


## 🏛 Architecture


### Core Components
- **API Server**: `main.py` (FastAPI entrypoint).
- **Lifecycle Management**: `lifespan.py` initializes DB, emotional decay, and periodic thinking.
- **Async Workers**: `worker.py`, `redis_queue.py` with Redis + RQ for task queuing.


### State & Reasoning
- **State Engine**: `state.py`, `state_events.py`, `state_reducer.py` for handling agent state transitions.
- **Thoughts & Prompts**: `thinking.py`, `prompting.py` for periodic self-reflection and schema-driven prompts.


### Emotions & Personality
- **Decay Loop**: `emotion_decay.py` for natural emotional regression.
- **Traits & Deltas**: `models.py`, `state_reducer.py` for applying personality/emotion/sentiment changes.
- **Schemas**: `schemas.py`, `schemas_lite.py` defining rich vs. lite representations.


### Memory & Persistence
- **Database**: `database.py` for MongoDB operations.
- **Memory Management**: `memory.py` for storing and retrieving tagged memories.
- **Validators**: `validators.py` enforces schema constraints in MongoDB.


### APIs
- **Agents**: `/agents` – list all agents, get active agent.
- **Messages**: `/messages` – submit user messages, retrieve conversations.
- **Jobs**: `/jobs/{id}` – check async job status.
- **Meta**: `/meta` – API version, health check.
- **Root**: `/` – generate a random autonomous thought.


### Integrations
- **OpenAI**: `openai.py` for structured responses.
- **DeepSeek**: `deepseek.py` for alternative model integration.


---


## 🔐 Authentication


### Features
- **Guest sessions**: `POST /v1/auth/guest` → creates an anonymous but tokenized identity (guest_<uuid>).

- **Claim account**: `POST /v1/auth/claim` → upgrade a guest with email, username, and password.

- **Login**: `POST /v1/auth/login` → authenticate existing accounts.

- **Refresh**: `POST /v1/auth/refresh` → rotate refresh + access tokens (refresh stored in HttpOnly cookie).

- **Logout**: `POST /v1/auth/logout` → revoke current session.

- **Tokens**:

-  - Access tokens (JWT): short-lived, carry `user_id`, `username`, `sid`.

- - Refresh tokens: opaque, session-bound, rotated on each use.

- **Password storage**: Argon2id with per-user salt + optional global pepper.
  
### Using Tokens in Postman
1. Call `/auth/guest` or `/auth/login` to get an access_token.
2. In Postman → Authorization tab → Type: **Bearer Token** → paste the access token.
3. Now protected endpoints will work.

### Protected vs Public Endpoints
Public
- /v1/meta/ping
- /v1/meta/version
- /v1/auth/login
- /v1/auth/guest
- /v1/auth/logout

Auth-required (guest or user)
- /v1/messages/*
- /v1/jobs/*
- /v1/agents/*
- /v1/auth/claim
- /v1/auth/me
- /v1/auth/refresh

### Summary
- All user-related endpoints now require at least a guest token.

- Tokens are short-lived; refresh flow handles rotation.

- Passwords are hashed with Argon2id + pepper.

- Sessions and refresh tokens are stored/revoked server-side.
  
---

## ⚙️ Configuration
Configuration is managed via environment variables (`.env`).


### Key Variables
- `BOT_NAME` – agent display name.
- `OPENAI_API_KEY` – OpenAI key.
- `GPT_FAST_MODEL`, `GPT_QUALITY_MODEL` – model IDs.
- `DEEPSEEK_BASE_URL`, `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL` – DeepSeek configuration.
- `MONGO_CONNECTION`, `DATABASE_NAME` – MongoDB connection.
- `REDIS_URL` or `REDIS_TLS_URL` – Redis connection string.
- `WEB_UI_DOMAIN` – Allowed frontend domain.
- `JWT_SECRET`=your-long-random-secret # e.g., `openssl rand -base64 64`
- `PASSWORD_PEPPER`=your-random-pepper # e.g., `openssl rand -base64 32`
- `JWT_AUD`=synthetic-soul # audience claim
- `JWT_ISS`=synthetic-soul-api # issuer claim
- `ACCESS_TOKEN_TTL`=900 # seconds (15 minutes typical)
- `REFRESH_TOKEN_TTL`=604800 # seconds (7 days typical)


### Rates & Retention
- Emotional Decay: every 240s.
- Thinking: every 300s.
- Conversation message retention: 10.


---


## 🚀 Getting Started


### Requirements
- Python 3.10+
- Redis server
- MongoDB

### Running the API Locally
1. Make sure **Redis** and **MongoDB** are running locally or accessible. Redis - Run Docker desktop, then in the command prompt:
```bash
docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
```


2. Install dependencies and Start the FastAPI server:
```bash
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
The API will be available at: [http://localhost:8000](http://localhost:8000)


3. Start the background worker in a separate terminal:
```bash
rq worker
```

---


## 📡 Usage

### Authentication Flow
1. Guest session
   ```http
    POST /auth/guest
    ```

    Response
    ```http
    {
    "access_token": "...",
    "username": "guest_123..."
    }
    ```

2. Claim account
    ```http
    POST /auth/claim
    {
    "email": "me@example.com"
    "username": "alice",
    "password": "secret123"
    }
    ```

3. Login
    ```http
    POST /auth/login
    {
    "email": "me@example.com"
    "password": "secret123"
    }
    ```
4. Refresh
   ```http
    POST /auth/refresh
    ```
    (Uses HttpOnly refresh cookie; server rotates both refresh + access tokens.)

5. Logout
   ```http
    POST /auth/logout
    ```
    Revokes session and clears refresh cookie.

### Submit a Message
```http
POST /messages/submit
{
"username": "alice",
"content": "How are you feeling today?"
}
```


Response:
```json
{
"job_id": "abc123",
"status": "queued"
}
```


### Poll Job Status
```http
GET /jobs/abc123
```

Response:
```json
{
"job_id": "8bbf5e53-a9b5-4020-bf2d-bde3026a26e4",
    "status": "succeeded",
    "progress": 100.0,
    "result": {
        "response": "I’m doing really well, thank you — that made my day to hear! I’m so happy we’ve been chatting ♡",
        "time": 22,
        "expression": "happy"
    },
    "error": null
}
```

### Get Active Agent
```http
GET /agents/active
```


### Random Thought
```http
GET /
```

## 🧠 Philosophy
*Jasmine* explores affective computing and digital companionship by blending artificial intelligence with principles from psychology and human relationship studies. The goal is not just interaction but **evolution**—an AI that grows and adapts with users over time.


---


## 📌 Roadmap
- Enhanced relationship graphs between multiple users.
- Expanded multi-agent simulations.
- Advanced long-term personality drift and adaptation.
- Robust memory retrieval system
- Function calling, allowing for deliberate execution certain actions/functions
- Non-reaction based messaging. Agent can choose to reach out first
- Advanced groupchat context system
- Handling of user sending multiple messages before response is generated
- Agents builds personality profiles of users through interactions
- Option for agent to schedule a response for later


---


## 🤝 Contributing
Pull requests and experiments are welcome. This project is exploratory—expect rapid iteration.


---


## 📄 License
MIT License. See `LICENSE` file for details.
