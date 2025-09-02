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
