# Currency Analyst Agent

### Real-time currency intelligence, delivered through conversation.

Ask a question in plain language — *“What’s the USD to EUR rate right now?, Convert 200 USD to CNY”* — and get a grounded answer backed by live market data, not yesterday’s spreadsheet.

Currency Analyst Agent is a **CrewAI-powered financial intelligence system** that fetches live foreign-exchange data, reasons over it with a specialized AI agent, and returns clear, structured insights through a chat interface.

---

## Why it exists

Foreign exchange moves constantly. Most people don’t want APIs, tickers, or terminal screens — they want a confident answer to a simple question.

| For everyone | For builders |
| --- | --- |
| Natural-language questions about currencies | Modular CrewAI agent + tool architecture |
| Live rates from a production FX API | FastAPI contract with typed request/response schemas |
| Clear explanations of relative currency strength | Streamlit chat UI with streaming-style responses |
| No need to memorize ISO codes like `NGN` or `JPY` | `uv`-managed Python toolchain and Docker-ready deploy |

The system does **not** invent historical charts or future predictions from thin air for rate lookup — spot rates come from **ExchangeRate-API**. The agent interprets those rates into language you can act on.

---

## What you can ask

- Current exchange rate between two currencies or countries  
- Relative strength comparisons at the current market snapshot  
- Which currency codes the system supports  
- Concise explanations of currency relationships in plain language  

**Example prompts**

```text
What is the current exchange rate between USA currency and Germany currency?
What's the current exchange rate between USD and MXN?
List all supported currency codes.
What is the current amount of 200 USD in CNY?
```

---

## Architecture at a glance

```text
┌────────────────────┐     POST /currency/analyze       ┌────────────────────┐
│       Chat UI      │ ───────────────────────────────► │   FastAPI Backend  │
│      (frontend)    │ ◄─────────────────────────────── │                    │
└────────────────────┘           { response }           └─────────┬──────────┘
                                                                  │
                                                                  ▼
                                                      ┌───────────────────────┐
                                                      │       AI Agents       │
                                                      │                       │
                                                      └───────────┬───────────┘                                  
```

### How a request flows

1. **You** type a question in the Streamlit chat.  
2. The UI sends `POST /currency/analyze` with `{ "query": "..." }`.  
3. FastAPI hands the query to the **Currency Analyst** CrewAI crew.  
4. The agent decides which tools to call — supported codes, live pair rate, or both.  
5. Tools hit **ExchangeRate-API** for ground-truth market data.  
6. The agent composes a markdown-friendly answer; the UI streams it back word by word.

---

## Tech stack

| Layer | Technology | Role |
| --- | --- | --- |
| Agent framework | [CrewAI](https://www.crewai.com/) | Agent, tasks, sequential process, memory |
| LLM | OpenAI `gpt-4o-mini` (configurable in YAML) | Reasoning and natural-language synthesis |
| Market data | [ExchangeRate-API](https://www.exchangerate-api.com/) v6 | Supported codes + real-time pair rates |
| API | FastAPI + Uvicorn | HTTP boundary, CORS, health checks |
| UI | Streamlit | Conversational frontend |
| Packaging | `uv` + setuptools (`src/` layout) | Reproducible installs |
| Runtime | Docker / Compose | One-command local or server deploy |

---

## Project structure

```text
currency_analyst_agent/
├── api/                          # FastAPI application
│   ├── main.py                   # App entry, CORS, /health
│   ├── routes/currency.py        # POST /currency/analyze
│   └── schemas/currency_schema.py
├── frontend/
│   └── app.py                    # Streamlit chat experience
├── src/
│   └── currency_analyst_crew/    # Installable CrewAI package
│       ├── crew.py               # Agent + tasks wiring
│       ├── main.py               # kickoff() entrypoint
│       ├── config/
│       │   ├── agents.yaml       # Role, goal, LLM
│       │   └── tasks.yaml        # Task specs
│       └── tools/
│           ├── custom_tool.py    # FX tools
│           └── tool_schema.py    # Pydantic tool inputs
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## Prerequisites

- **Python** 3.10+  
- **[uv](https://docs.astral.sh/uv/)** (recommended)  
- **API keys**
  - `EXCHANGE_RATE_API_KEY` — ExchangeRate-API  
  - `OPENAI_API_KEY` — LLM provider used by CrewAI  
- **Docker** + Docker Compose (optional, for containerized runs)

Create a `.env` file in this project directory:

```env
EXCHANGE_RATE_API_KEY=your_exchangerate_api_key
OPENAI_API_KEY=your_openai_api_key
```

---

## Quick start (local)

### 1. Install dependencies

```bash
cd src/currency_analyst_agent
uv sync
```

This creates `.venv` and installs the `currency_analyst_crew` package from the `src/` layout.

### 2. Start the API

```bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/` | `GET` | Welcome payload |
| `/health` | `GET` | Liveness check |
| `/currency/analyze` | `POST` | Run currency analysis |
| `/docs` | `GET` | Interactive OpenAPI UI |

### 3. Start the chat UI (second terminal)

```bash
uv run streamlit run frontend/app.py
```

Open the URL Streamlit prints (typically `http://localhost:8501`).

### 4. Optional: run the crew from the CLI

```bash
uv run python -m currency_analyst_crew.main
```

---

## API contract

**Request**

```http
POST /currency/analyze
Content-Type: application/json
```

```json
{
  "query": "what is the current exchange rate between USA currency and Germany currency?"
}
```

**Response**

```json
{
  "response": "…"
}
```

The Streamlit client reads the `response` field and renders it in the chat transcript. Override the backend URL with:

```bash
export CURRENCY_API_URL=http://localhost:8000/currency/analyze
```

---

## Agent & tools (deeper dive)

### Agent — `currency_analyst`

Defined in `config/agents.yaml`: a real-time currency specialist whose goal is accurate rates and concise relationships for `{query}`. When a tool answer is sufficient, it is instructed to respond without unnecessary extra tool calls.

### Tasks (sequential)

1. **`supported_currencies_task`** — Reference context of supported ISO codes and names (used when validating or listing currencies).  
2. **`real_time_currency_task`** — Live analysis and conversion narrative; writes markdown to `output/report.md`.

### Tools

| Tool | Input | Behavior |
| --- | --- | --- |
| **Supported Currencies Tool** | none | `GET /v6/{key}/codes` → list of `CODE - Name` |
| **Currency Converter Tool** | `from_currency`, `to_currency` | `GET /v6/{key}/pair/{from}/{to}` → spot rate (`1 FROM = rate TO`), usable as **amount × rate** |

---

## Docker

One image, two processes: API and UI. Compose wires them on an internal network so the chat service talks to the API by service name.

### Build & run

```bash
cd src/currency_analyst_agent

# ensure .env exists with EXCHANGE_RATE_API_KEY and OPENAI_API_KEY
docker compose up --build
```

| Service | Host URL |
| --- | --- |
| Chat UI | http://localhost:8501 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

Stop with `Ctrl+C`, or:

```bash
docker compose down
```

### Image only

```bash
docker build -t currency-analyst-agent .
docker run --rm --env-file .env -p 8000:8000 currency-analyst-agent \
  uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```