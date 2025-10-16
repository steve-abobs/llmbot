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
