# Create a Python project for a Telegram bot
_Exported on 10/16/2025 at 16:12:36 GMT+3 from Cursor (1.7.33)_

---

**User**

Create a new Python project called "student-agent".  
This agent should run as a Telegram bot that integrates with Ollama (local LLM)  
and can access three MCP-like tools: Google Calendar, Google Sheets, and OpenWeatherMap.  

Please generate the initial folder structure with these folders:
- bot/
- llm/
- mcp/
- memory/
- kb/
and the following files:
- bot/main.py
- bot/config.py
- llm/ollama.py
- mcp/calendar.py
- mcp/sheets.py
- mcp/weather.py
- memory/json_memory.py
- kb/faiss_kb.py
- requirements.txt
- .env.example
- README.md

The environment variables should include:
TELEGRAM_TOKEN, GOOGLE_CREDENTIALS_PATH, GOOGLE_CALENDAR_ID, GOOGLE_SHEETS_ID,
OPENWEATHER_API_KEY, OLLAMA_HOST, OLLAMA_MODEL, MEMORY_PATH, FAISS_INDEX_PATH, FAISS_META_PATH.

Make the project Python 3.10+ compatible and ready for Docker deployment.

Implement three MCP-like modules:
1. mcp/calendar.py — read upcoming events from Google Calendar using service account credentials.
2. mcp/sheets.py — read homework data from Google Sheets.
3. mcp/weather.py — fetch weather using OpenWeatherMap API.

Each module should expose a simple Python function returning plain text summaries.

For example:
- get_upcoming_events() → str
- get_homework_for_today() → str
- get_weather(city: str = "Moscow") → str

All credentials and API keys must be read from environment variables.

In llm/ollama.py, implement a function call_ollama(prompt: str, functions: list = None, context: list = None)  
that sends a request to the Ollama HTTP API (default: http://localhost:11434/api/generate).

If the user provides a list of "functions", the LLM should be instructed to decide  
whether to call any of them, returning a JSON like {"function": "name", "arguments": {...}}.

Otherwise, return the model's generated text directly.

Example:
{
  "model": "llama3",
  "prompt": "User prompt with tool list and context",
  "max_tokens": 512
}

Add robust error handling, timeout protection, and JSON parsing fallback.

Implement simple conversational memory and a knowledge base:

1. memory/json_memory.py — store recent conversation history per user in a JSON file.  
Functions: append_user_message(), append_bot_message(), get_context(user_id: str, limit: int = 10)

2. kb/faiss_kb.py — implement a FAISS-based text retriever using sentence-transformers.  
Functions: add_documents(docs), query(text: str, top_k: int = 3)
The KB should store embeddings in FAISS and metadata (titles, ids) in a JSON file.

Add a simple "function calling" system to the bot.

The agent should:
1. Receive a user query (/ask <text>).
2. Provide Ollama with a description of available tools in English.
3. Let Ollama decide if it wants to call any function, returning JSON like:
   {"function": "get_weather", "arguments": {"city": "Moscow"}}
4. Parse this JSON, execute the corresponding Python function,  
   append the result to the context, and re-ask Ollama to produce the final user-facing answer.

Available functions:
- get_weather(city: str)
- get_upcoming_events()
- get_homework_for_today()

Design a clear system prompt for Ollama:
"You are a helpful school assistant. You can use tools to get information.
If the user's question requires one of the tools, respond with a JSON object describing which tool to call.
If not, respond directly to the user in natural language."

Implement this logic inside the /ask command handler.

Implement the Telegram bot in bot/main.py using python-telegram-bot (v20+).

Commands:
- /help — list commands
- /health — return "✅ Bot is running"
- /weather [city]
- /schedule
- /homework
- /ask <question>

For /ask:
- Retrieve user memory and KB context.
- Pass both to Ollama as context.
- Use function calling if needed.
- Save conversation in memory.

Add logging and error handling.
Make sure the bot can be easily deployed with Docker and automatically restarts.

Now integrate everything:
- Ollama runs locally.
- Telegram bot uses function calling via Ollama.
- All MCP tools return usable data.
- Memory and FAISS KB persist in ./data.
- Use .env for secrets.

Add unit tests for function calling (mock LLM responses), and a Dockerfile + docker-compose.yml.

Then generate a clean README.md explaining setup and usage:
1. Prerequisites
2. Installation
3. Configuration (.env)
4. Running with Docker
5. Commands overview
6. Architecture summary

Ensure that the code follows clean architecture and modular design.

---

**Cursor**

I'll set up a structured plan and start creating the project files and directories. First, I’ll add a todo list to track major tasks, then begin implementing the project skeleton, configuration, LLM integration, MCP tools, memory/KB, bot logic, tests, and Docker assets.

I'll start by creating the project scaffolding files (requirements, env, README, Docker assets), then implement the bot config and main, LLM client, MCP tools, memory/KB modules, and tests.

```pip-requirements
<<'PATCH'
*** Begin Patch
*** Add File: /home/abobs/not_importatn/llmbot4/requirements.txt
python-dotenv>=1.0.0
python-telegram-bot>=20.3
requests>=2.31.0
pydantic>=2.6.0
faiss-cpu>=1.7.4
sentence-transformers>=2.5.1
google-api-python-client>=2.143.0
google-auth>=2.23.0
google-auth-httplib2>=0.2.0
protobuf>=4.25.3
ujson>=5.9.0
pytest>=7.4.0
*** End Patch
PATCH
```

```markdown
<<'PATCH'
*** Begin Patch
*** Add File: /home/abobs/not_importatn/llmbot4/README.md
## student-agent

A Telegram bot that integrates with a local Ollama LLM and three MCP-like tools: Google Calendar, Google Sheets, and OpenWeatherMap. It includes simple JSON-based conversational memory and a FAISS-based knowledge base.

### Prerequisites
- Python 3.10+
- Docker and Docker Compose (optional but recommended)
- A Telegram Bot Token
- Google Cloud Service Account JSON with access to Calendar and Sheets
- OpenWeatherMap API key
- Ollama running locally with your chosen model pulled (e.g., `llama3`)

### Installation
1. Clone this repository.
2. Create a `.env` from `.env.example` and fill in values.
3. (Optional) Create `./credentials/service_account.json` and update `GOOGLE_CREDENTIALS_PATH`.
4. Install dependencies:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration (.env)
- `TELEGRAM_TOKEN`: Telegram bot token
- `GOOGLE_CREDENTIALS_PATH`: Path to Google service account JSON
- `GOOGLE_CALENDAR_ID`: Calendar ID (primary or explicit)
- `GOOGLE_SHEETS_ID`: Spreadsheet ID
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key
- `OLLAMA_HOST`: Ollama API host (Docker: `http://host.docker.internal:11434`)
- `OLLAMA_MODEL`: Model name (e.g., `llama3`)
- `MEMORY_PATH`: Path to JSON memory file (default `./data/memory.json`)
- `FAISS_INDEX_PATH`: FAISS index path
- `FAISS_META_PATH`: JSON metadata path

### Running with Docker
Ensure Ollama is running on the host. On Linux, Docker Compose includes an extra host mapping for `host.docker.internal`.
```bash
docker compose up --build -d
```
This will auto-restart the bot on failure.

### Commands
- `/help` — list commands
- `/health` — healthcheck
- `/weather [city]` — fetch weather via OpenWeatherMap
- `/schedule` — upcoming events from Google Calendar
- `/homework` — homework from Google Sheets
- `/ask <question>` — tool-aware Q&A using Ollama function calling

### Architecture
- `bot/` Telegram entrypoint, command handlers, function-calling loop
- `llm/` Ollama client with optional tool invocation
- `mcp/` MCP-like tools (Calendar, Sheets, Weather) returning plain text
- `memory/` JSON memory store per user
- `kb/` FAISS-based retriever with sentence-transformers
- `data/` persists memory and KB index/metadata

### Tests
Run unit tests:
```bash
pytest -q
```
*** End Patch
PATCH
```

```dockerfile
<<'PATCH'
*** Begin Patch
*** Add File: /home/abobs/not_importatn/llmbot4/Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for sentence-transformers / faiss
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Create data directories
RUN mkdir -p /app/data/faiss /app/credentials

# Use unprivileged user
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

CMD ["python", "-m", "bot.main"]
*** End Patch
PATCH
```

```dockercompose
<<'PATCH'
*** Begin Patch
*** Add File: /home/abobs/not_importatn/llmbot4/docker-compose.yml
version: "3.9"
services:
  student-agent:
    build: .
    restart: always
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./credentials:/app/credentials:ro
    extra_hosts:
      - "host.docker.internal:host-gateway"
*** End Patch
PATCH
```

I'll create the core project scaffolding files first (requirements, env, README, Docker assets) to establish the environment and containerization, then proceed to add Python packages and modules.

```pip-requirements
python-dotenv>=1.0.0
python-telegram-bot>=20.3
requests>=2.31.0
pydantic>=2.6.0
faiss-cpu>=1.7.4
sentence-transformers>=2.5.1
google-api-python-client>=2.143.0
google-auth>=2.23.0
google-auth-httplib2>=0.2.0
protobuf>=4.25.3
ujson>=5.9.0
pytest>=7.4.0
```

```markdown
## student-agent

A Telegram bot that integrates with a local Ollama LLM and three MCP-like tools: Google Calendar, Google Sheets, and OpenWeatherMap. It includes simple JSON-based conversational memory and a FAISS-based knowledge base.

### Prerequisites
- Python 3.10+
- Docker and Docker Compose (optional but recommended)
- A Telegram Bot Token
- Google Cloud Service Account JSON with access to Calendar and Sheets
- OpenWeatherMap API key
- Ollama running locally with your chosen model pulled (e.g., `llama3`)

### Installation
1. Clone this repository.
2. Create a `.env` from `.env.example` and fill in values.
3. (Optional) Create `./credentials/service_account.json` and update `GOOGLE_CREDENTIALS_PATH`.
4. Install dependencies:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration (.env)
- `TELEGRAM_TOKEN`: Telegram bot token
- `GOOGLE_CREDENTIALS_PATH`: Path to Google service account JSON
- `GOOGLE_CALENDAR_ID`: Calendar ID (primary or explicit)
- `GOOGLE_SHEETS_ID`: Spreadsheet ID
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key
- `OLLAMA_HOST`: Ollama API host (Docker: `http://host.docker.internal:11434`)
- `OLLAMA_MODEL`: Model name (e.g., `llama3`)
- `MEMORY_PATH`: Path to JSON memory file (default `./data/memory.json`)
- `FAISS_INDEX_PATH`: FAISS index path
- `FAISS_META_PATH`: JSON metadata path

### Running with Docker
Ensure Ollama is running on the host. On Linux, Docker Compose includes an extra host mapping for `host.docker.internal`.
```bash
docker compose up --build -d
```
This will auto-restart the bot on failure.

### Commands
- `/help` — list commands
- `/health` — healthcheck
- `/weather [city]` — fetch weather via OpenWeatherMap
- `/schedule` — upcoming events from Google Calendar
- `/homework` — homework from Google Sheets
- `/ask <question>` — tool-aware Q&A using Ollama function calling

### Architecture
- `bot/` Telegram entrypoint, command handlers, function-calling loop
- `llm/` Ollama client with optional tool invocation
- `mcp/` MCP-like tools (Calendar, Sheets, Weather) returning plain text
- `memory/` JSON memory store per user
- `kb/` FAISS-based retriever with sentence-transformers
- `data/` persists memory and KB index/metadata

### Tests
Run unit tests:
```bash
pytest -q
```
```

```dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for sentence-transformers / faiss
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Create data directories
RUN mkdir -p /app/data/faiss /app/credentials

# Use unprivileged user
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

CMD ["python", "-m", "bot.main"]
```

```dockercompose
version: "3.9"
services:
  student-agent:
    build: .
    restart: always
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./credentials:/app/credentials:ro
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Creating the initial code files and directories now: config, bot entrypoint, LLM client, MCP tools, memory store, KB, and tests.

```python
import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")
    google_credentials_path: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials/service_account.json")
    google_calendar_id: str = os.getenv("GOOGLE_CALENDAR_ID", "")
    google_sheets_id: str = os.getenv("GOOGLE_SHEETS_ID", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    memory_path: str = os.getenv("MEMORY_PATH", "./data/memory.json")
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "./data/faiss/index.faiss")
    faiss_meta_path: str = os.getenv("FAISS_META_PATH", "./data/faiss/meta.json")


_settings: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

```python
import json
import re
from typing import Any, Dict, List, Optional, Union
import requests

DEFAULT_TIMEOUT = 30


def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to find the first JSON object in the text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return None
    return None


def call_ollama(
    prompt: str,
    functions: Optional[List[Dict[str, Any]]] = None,
    context: Optional[List[str]] = None,
    host: str = None,
    model: str = None,
    max_tokens: int = 512,
    temperature: float = 0.2,
) -> Union[str, Dict[str, Any]]:
    """
    Call the Ollama HTTP API to generate text.

    - If `functions` is provided, instruct the model to decide on a tool call and
      return a JSON object {"function": "name", "arguments": {...}}.
    - Otherwise, return the generated text directly.
    """
    from bot.config import get_settings

    settings = get_settings()
    base_url = (host or settings.ollama_host).rstrip("/")
    model_name = model or settings.ollama_model

    tool_instructions = ""
    if functions:
        tool_list = []
        for f in functions:
            name = f.get("name")
            description = f.get("description", "")
            params = f.get("parameters", {})
            tool_list.append(f"- {name}: {description}. Parameters: {json.dumps(params)}")
        tool_instructions = (
            "You can use tools to get information. If the user's question requires one of the tools, "
            "respond ONLY with a JSON object describing which tool to call in the form: "
            "{\"function\": \"name\", \"arguments\": { ... }}. "
            "If not, respond directly in natural language.\n\nAvailable tools:\n" + "\n".join(tool_list)
        )

    ctx_text = ""
    if context:
        ctx_text = "\n\nContext:\n" + "\n".join(context[-20:])

    final_prompt = prompt
    if functions:
        final_prompt = tool_instructions + "\n\nUser:\n" + prompt + ctx_text
    else:
        final_prompt = prompt + ctx_text

    payload = {
        "model": model_name,
        "prompt": final_prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.Timeout:
        if functions:
            return {"function": None, "arguments": {}, "error": "timeout"}
        return "Request to LLM timed out. Please try again."
    except requests.RequestException as e:
        if functions:
            return {"function": None, "arguments": {}, "error": str(e)}
        return "LLM service unavailable."

    try:
        data = resp.json()
        generated = data.get("response") or data.get("text") or ""
    except Exception:
        generated = resp.text

    if not functions:
        return generated.strip()

    parsed = _extract_json_block(generated)
    if isinstance(parsed, dict) and "function" in parsed:
        # ensure arguments is dict
        args = parsed.get("arguments")
        if not isinstance(args, dict):
            try:
                args = json.loads(args) if args else {}
            except Exception:
                args = {}
        return {"function": parsed.get("function"), "arguments": args}

    # Fallback: no tool call, treat as direct answer
    return {"function": None, "arguments": {}, "text": generated.strip()}
```

```python
import os
from typing import Optional
import requests

API_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str = "Moscow") -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not api_key:
        return "OpenWeather API key is not configured."
    try:
        resp = requests.get(
            API_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=15,
        )
        if resp.status_code == 401:
            return "OpenWeather API key is invalid."
        resp.raise_for_status()
        data = resp.json()
        name = data.get("name", city)
        main = data.get("weather", [{}])[0].get("description", "N/A").capitalize()
        temp = data.get("main", {}).get("temp", "?")
        feels = data.get("main", {}).get("feels_like", "?")
        humidity = data.get("main", {}).get("humidity", "?")
        wind = data.get("wind", {}).get("speed", "?")
        return f"Weather in {name}: {main}. Temp {temp}°C (feels {feels}°C), humidity {humidity}%, wind {wind} m/s."
    except requests.Timeout:
        return "Weather service timed out."
    except requests.RequestException as e:
        return f"Weather service error: {e}"
```

```python
import datetime as dt
import os
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _get_service():
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials/service_account.json")
    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
    return service


def get_upcoming_events(days: int = 7, max_results: int = 10) -> str:
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "")
    if not calendar_id:
        return "Google Calendar ID is not configured."

    service = _get_service()
    now = dt.datetime.utcnow().isoformat() + "Z"
    end_time = (dt.datetime.utcnow() + dt.timedelta(days=days)).isoformat() + "Z"

    events_result = (
        service.events()
        .list(calendarId=calendar_id, timeMin=now, timeMax=end_time, singleEvents=True, orderBy="startTime", maxResults=max_results)
        .execute()
    )
    events: List[dict] = events_result.get("items", [])
    if not events:
        return "No upcoming events found."

    lines: List[str] = []
    for ev in events:
        start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date")
        summary = ev.get("summary", "(no title)")
        location = ev.get("location")
        start_fmt = start
        try:
            if "T" in start:
                start_dt = dt.datetime.fromisoformat(start.replace("Z", "+00:00"))
                start_fmt = start_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
        if location:
            lines.append(f"- {start_fmt}: {summary} @ {location}")
        else:
            lines.append(f"- {start_fmt}: {summary}")
    return "Upcoming events:\n" + "\n".join(lines)
```

```python
import os
import datetime as dt
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def _get_service():
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials/service_account.json")
    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    return service


def get_homework_for_today() -> str:
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", "")
    if not sheet_id:
        return "Google Sheets ID is not configured."

    service = _get_service()
    # Convention: first sheet, columns: Date | Subject | Task
    rng = "Sheet1!A:C"
    values = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=rng)
        .execute()
        .get("values", [])
    )

    if not values:
        return "No homework data found."

    today = dt.date.today().isoformat()
    rows: List[str] = []
    for row in values[1:] if values and len(values) > 1 else []:
        date = row[0] if len(row) > 0 else ""
        subject = row[1] if len(row) > 1 else ""
        task = row[2] if len(row) > 2 else ""
        if date == today:
            rows.append(f"- {subject}: {task}")

    if not rows:
        return "No homework for today."
    return "Homework for today:\n" + "\n".join(rows)
```

```python
import json
import os
import threading
from typing import Dict, List

_lock = threading.Lock()


def _ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _read_all(path: str) -> Dict[str, List[Dict[str, str]]]:
    _ensure_file(path)
    with _lock:
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}


def _write_all(path: str, data: Dict[str, List[Dict[str, str]]]):
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def append_user_message(path: str, user_id: str, text: str):
    data = _read_all(path)
    messages = data.get(user_id, [])
    messages.append({"role": "user", "text": text})
    data[user_id] = messages[-200:]
    _write_all(path, data)


def append_bot_message(path: str, user_id: str, text: str):
    data = _read_all(path)
    messages = data.get(user_id, [])
    messages.append({"role": "assistant", "text": text})
    data[user_id] = messages[-200:]
    _write_all(path, data)


def get_context(path: str, user_id: str, limit: int = 10) -> List[str]:
    data = _read_all(path)
    messages = data.get(user_id, [])
    return [f"{m['role']}: {m['text']}" for m in messages[-limit:]]
```

```python
import json
import os
from typing import Any, Dict, List, Tuple

import faiss  # type: ignore
from sentence_transformers import SentenceTransformer


class FaissKB:
    def __init__(self, index_path: str, meta_path: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.index_path = index_path
        self.meta_path = meta_path
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        self.model = SentenceTransformer(model_name)
        self._load()

    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.meta: List[Dict[str, Any]] = json.load(f)
        else:
            self.index = None
            self.meta = []

    def _save(self):
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

    def add_documents(self, docs: List[Dict[str, Any]]):
        # docs: [{"id": str, "title": str, "text": str}]
        texts = [d["text"] for d in docs]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.meta.extend(docs)
        self._save()

    def query(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.index is None or len(self.meta) == 0:
            return []
        q = self.model.encode([text], convert_to_numpy=True, show_progress_bar=False)
        distances, indices = self.index.search(q, top_k)
        results: List[Dict[str, Any]] = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.meta):
                continue
            item = self.meta[idx]
            item = dict(item)
            item["score"] = float(distances[0][i])
            results.append(item)
        return results

# Convenience functions for simple usage

def add_documents(index_path: str, meta_path: str, docs: List[Dict[str, Any]]):
    kb = FaissKB(index_path, meta_path)
    kb.add_documents(docs)


def query(index_path: str, meta_path: str, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    kb = FaissKB(index_path, meta_path)
    return kb.query(text, top_k=top_k)
```

```python
import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from bot.config import get_settings
from llm.ollama import call_ollama
from mcp.weather import get_weather
from mcp.calendar import get_upcoming_events
from mcp.sheets import get_homework_for_today
from memory.json_memory import append_bot_message, append_user_message, get_context as mem_context
from kb.faiss_kb import query as kb_query

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("student-agent")

SYSTEM_PROMPT = (
    "You are a helpful school assistant. You can use tools to get information. "
    "If the user's question requires one of the tools, respond with a JSON object describing which tool to call. "
    "If not, respond directly to the user in natural language."
)


def _available_functions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "get_weather",
            "description": "Get current weather for a city via OpenWeatherMap",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": []},
        },
        {
            "name": "get_upcoming_events",
            "description": "Read upcoming events from Google Calendar",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "get_homework_for_today",
            "description": "Read today's homework from Google Sheets",
            "parameters": {"type": "object", "properties": {}},
        },
    ]


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "/help — list commands\n"
        "/health — health check\n"
        "/weather [city] — current weather\n"
        "/schedule — upcoming events\n"
        "/homework — today's homework\n"
        "/ask <question> — tool-aware Q&A"
    )
    await update.message.reply_text(text)


async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running")


async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args) if context.args else "Moscow"
    await update.message.reply_text(get_weather(city))


async def schedule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_upcoming_events())


async def homework_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_homework_for_today())


def _run_function_call(name: Optional[str], arguments: Dict[str, Any]) -> Optional[str]:
    if not name:
        return None
    try:
        if name == "get_weather":
            return get_weather(arguments.get("city", "Moscow"))
        if name == "get_upcoming_events":
            return get_upcoming_events()
        if name == "get_homework_for_today":
            return get_homework_for_today()
    except Exception as e:
        return f"Tool error: {e}"
    return None


async def ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = get_settings()
    user = update.effective_user
    if not user or not update.message:
        return
    user_id = str(user.id)
    query_text = update.message.text.split(" ", 1)
    question = query_text[1].strip() if len(query_text) > 1 else ""
    if not question:
        await update.message.reply_text("Usage: /ask <question>")
        return

    # Memory and KB context
    mem = mem_context(settings.memory_path, user_id=user_id, limit=10)
    kb_results = kb_query(settings.faiss_index_path, settings.faiss_meta_path, question, top_k=3)
    kb_texts = [f"KB: {r.get('title', '')}: {r.get('text', '')}" for r in kb_results]

    append_user_message(settings.memory_path, user_id, question)

    # First call: let model decide on tool usage
    functions = _available_functions()
    prompt = SYSTEM_PROMPT + "\n\nUser: " + question
    fc = call_ollama(prompt=prompt, functions=functions, context=mem + kb_texts)

    tool_result: Optional[str] = None
    if isinstance(fc, dict) and (fc.get("function") or fc.get("text")):
        if fc.get("function"):
            tool_result = _run_function_call(fc.get("function"), fc.get("arguments", {}))
        else:
            # Model answered directly
            final_answer = fc.get("text", "")
            append_bot_message(settings.memory_path, user_id, final_answer)
            await update.message.reply_text(final_answer)
            return

    # Second call: produce final user-facing answer with tool result in context
    context_lines = mem + kb_texts
    if tool_result:
        context_lines.append(f"TOOL_RESULT: {tool_result}")

    final = call_ollama(
        prompt=f"Answer the user's question clearly. Question: {question}",
        functions=None,
        context=context_lines,
    )
    final_text = final if isinstance(final, str) else final.get("text", "")
    if not final_text:
        final_text = tool_result or "I couldn't generate a response."

    append_bot_message(settings.memory_path, user_id, final_text)
    await update.message.reply_text(final_text)


def main():
    settings = get_settings()
    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_TOKEN is not set")
    application = Application.builder().token(settings.telegram_token).build()

    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("health", health_cmd))
    application.add_handler(CommandHandler("weather", weather_cmd))
    application.add_handler(CommandHandler("schedule", schedule_cmd))
    application.add_handler(CommandHandler("homework", homework_cmd))
    application.add_handler(CommandHandler("ask", ask_cmd))

    logger.info("Starting student-agent bot...")
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
```

```python
import json
from unittest.mock import patch
from llm.ollama import call_ollama


def test_direct_answer_parsing():
    response = {"response": "Hello world"}
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = response
        mock_post.return_value.raise_for_status.return_value = None
        text = call_ollama("hi", functions=None)
        assert isinstance(text, str)
        assert "Hello" in text


def test_function_call_json_extract():
    # The model returns a JSON instruction to call a tool
    model_text = '{"function": "get_weather", "arguments": {"city": "Moscow"}}'
    response = {"response": model_text}
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = response
        mock_post.return_value.raise_for_status.return_value = None
        out = call_ollama("weather?", functions=[{"name": "get_weather", "parameters": {}}])
        assert isinstance(out, dict)
        assert out.get("function") == "get_weather"
        assert out.get("arguments", {}).get("city") == "Moscow"


def test_function_call_fallback_plain_text():
    model_text = "I think you should call get_weather for Moscow."
    response = {"response": model_text}
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = response
        mock_post.return_value.raise_for_status.return_value = None
        out = call_ollama("weather?", functions=[{"name": "get_weather", "parameters": {}}])
        # Fallback returns dict with text
        assert isinstance(out, dict)
        assert out.get("text")
```

- Created scaffolding: `requirements.txt`, `.env.example`, `README.md`, `Dockerfile`, `docker-compose.yml`.
- Implemented config `bot/config.py`, Ollama client `llm/ollama.py` with function-calling and fallbacks.
- Added MCP tools: `mcp/calendar.py`, `mcp/sheets.py`, `mcp/weather.py`.
- Added memory `memory/json_memory.py` and FAISS KB `kb/faiss_kb.py`.
- Implemented Telegram bot `bot/main.py` with commands and /ask function-calling loop.
- Added unit tests `tests/test_function_calling.py`.

Next steps to run:
- Create `./credentials/service_account.json` and fill `.env`.
- Ensure Ollama is running and the model is pulled.
- Run: docker compose up -d

Notes:
- Data persists in `./data`. 
- Tools read all credentials from env. 
- Bot auto-restarts via compose.

---

**User**

create .env file and run the bot using venv

---

**Cursor**

I'll create a .env file with placeholders, set up a virtual environment, install dependencies, create data directories, and attempt to start the bot only if TELEGRAM_TOKEN is set; otherwise I'll print next-step instructions.

I'll create the .env by copying from .env.example, set up a Python venv, install dependencies, and attempt to run the bot. If TELEGRAM_TOKEN isn't set, I'll print instructions instead of starting.

I'll create the .env file content directly, set up the venv, install dependencies, and try to launch the bot if TELEGRAM_TOKEN is set; otherwise, I'll print a reminder.

I created .env and set up the venv; dependency installation started but was canceled while downloading torch (large). I’ll proceed once you confirm continuing the install.

- To finish setup and run:
```bash
cd /home/abobs/not_importatn/llmbot4
# activate venv
source .venv/bin/activate
# edit .env and set TELEGRAM_TOKEN (and other keys)
nano .env
# install dependencies (this will download torch; may take a while)
pip install -r requirements.txt
# run the bot (uses env from .env)
env $(grep -v '^#' .env | xargs) python -m bot.main
```

- If you prefer, I can resume the installation now.

```shellscript
cd /home/abobs/not_importatn/llmbot4
# activate venv
source .venv/bin/activate
# edit .env and set TELEGRAM_TOKEN (and other keys)
nano .env
# install dependencies (this will download torch; may take a while)
pip install -r requirements.txt
# run the bot (uses env from .env)
env $(grep -v '^#' .env | xargs) python -m bot.main
```

