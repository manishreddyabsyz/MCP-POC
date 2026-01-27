## Salesforce MCP POC (Backend + Frontend)

This repo demonstrates proper MCP (Model Context Protocol) tool usage with:
- `backend/`: FastAPI client + MCP tool server + Salesforce integration + ChatGPT summarization
- `frontend/`: React (Vite) chat UI integrated with the backend

### Architecture

```
Frontend → FastAPI (MCP Client) → MCP Server → Tools → Agent Core → Salesforce
```

The FastAPI server acts as an MCP client that communicates with the MCP server to execute tools.

### Prerequisites

- Python 3.11+ (recommended)
- Node.js 18+ / 20+
- Environment variables (in `backend/.env` or your shell):
  - `OPENAI_API_KEY`
  - `SF_USERNAME`
  - `SF_PASSWORD`
  - `SF_SECURITY_TOKEN`
  - `SF_DOMAIN` (optional, default `login`)

### Run backend (FastAPI)

From repo root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

Backend endpoint used by the UI:
- `POST /query` with body: `{ "query": "...", "session_id": "..." }`

### Run frontend (Chat UI)

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL (usually `http://localhost:5173`).

### MCP Tools Available

The MCP server exposes these tools:
- `ask`: Main query handler for Salesforce case operations
- `salesforce_health`: Health check for Salesforce connectivity

### MCP server (standalone)

If you want to run the MCP tool server directly for external MCP clients:

```bash
python backend\server.py
```

### MCP Configuration

For external MCP clients (like Kiro), use the configuration in `.kiro/settings/mcp.json`.

