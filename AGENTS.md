# EcomAgent Development Guide

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env          # fill OPENAI_API_KEY + OPENAI_BASE_URL + MODEL_NAME
python app/scripts/build_kb_index.py --backend numpy   # required before first run
python main.py
```

### Configuration Checklist

1. Copy `.env.example` to `.env`
2. Set `OPENAI_API_KEY` to your API key
3. Set `OPENAI_BASE_URL` to your API endpoint (default: `https://api.openai.com/v1`)
4. Set `MODEL_NAME` to your model (default: `gpt-5.5`)
5. If your API doesn't support embeddings, use `--local-embed` when building the RAG index

## Key Commands

| Command | Notes |
|---------|-------|
| `python main.py` | Interactive CLI; `quit`/`exit` to leave, `reset` to clear, `memory` to inspect, `skills` to list |
| `python app/gradio_app.py` | Web UI on `127.0.0.1:7860` |
| `python app/scripts/build_kb_index.py --backend numpy` | Build RAG index (zero-dependency, teaching) |
| `python app/scripts/build_kb_index.py --backend chroma --local-embed` | Build RAG index with local embeddings (no API needed) |
| `python mcp_server/server.py` | MCP server on `127.0.0.1:9123/mcp` |
| `python app/scripts/run_eval.py --no-judge` | Fast evaluation (code rules only) |
| `python app/scripts/run_eval.py --judge` | Full evaluation with LLM-as-judge |
| `pytest tests/ -v` | All tests (require live API key) |
| `pytest tests/test_rag.py -v` | RAG-only tests (no API key needed) |

## Architecture

**Two modes**, selected via `MULTI_AGENT_ENABLED` in `.env`:

1. **Single Agent** (default): `app/agent/chat.py:EcomAgent` — ReAct loop (max 5 steps), tool calling, auto-compress history after 10 messages.
2. **Multi-Agent**: `app/multi_agent/orchestrator.py:MultiAgentOrchestrator` — Router classifies intent → delegates to sub-agent (presale/postsale/complaint).

**Core data flow**: user input → `_build_messages()` (system prompt + memory + history) → `_react_loop()` (LLM ↔ tools) → `_extract_structured_response()` → `CustomerServiceResponse` → session saved to `app/sessions/session.json`.

### Subsystems

| Subsystem | Location | Notes |
|-----------|----------|-------|
| Tool system | `app/agent/tools/` | `ToolManager` dispatches to local or MCP tools |
| RAG | `app/agent/rag/` | NumPy (hand-rolled cosine) or ChromaDB backend; Markdown split on `##` headings |
| Memory | `app/agent/memory/` | STM (in-session facts) + LTM (persistent JSON per user_id) |
| Skills | `app/agent/skills/definitions/` | SKILL.md per skill; catalog injected into system prompt, full body loaded on demand |
| MCP | `mcp_server/server.py` | FastMCP HTTP; auto-fallback to local tools if MCP connection fails |
| Evaluation | `app/evaluation/` | Sandbox isolates sessions, disables memory/MCP; dual-layer scoring (code rules + LLM judge) |
| Multi-Agent | `app/multi_agent/` | Router + 3 sub-agents with tool whitelists |

### Configuration

All in `app/config/settings.py` via pydantic-settings, loaded from `.env`.

Key toggles: `MCP_ENABLED`, `MULTI_AGENT_ENABLED`, `MEMORY_ENABLED`, `SKILLS_ENABLED`, `RAG_BACKEND` (numpy|chroma).

### Required Environment Variables

**Must be set in `.env`** (copy from `.env.example`):

```bash
# LLM API Configuration (required)
OPENAI_API_KEY=sk-your-api-key        # Your API key
OPENAI_BASE_URL=https://api.openai.com/v1  # API endpoint (supports any OpenAI-compatible service)
MODEL_NAME=gpt-5.5                    # Model name to use
```

**Optional but useful:**

```bash
# Embedding Configuration (defaults to reusing LLM config)
EMBEDDING_MODEL=text-embedding-3-small  # Default embedding model
EMBEDDING_API_KEY=                      # Leave empty to reuse OPENAI_API_KEY
EMBEDDING_BASE_URL=                     # Leave empty to reuse OPENAI_BASE_URL

# Feature Toggles
MCP_ENABLED=false                       # Enable MCP tool server
MULTI_AGENT_ENABLED=false               # Enable multi-agent routing
MEMORY_ENABLED=true                     # Enable memory system
SKILLS_ENABLED=true                     # Enable skill system
RAG_BACKEND=numpy                       # numpy (default) or chroma
```

**Important**: If using an API proxy that doesn't support embeddings, use `--local-embed` flag when building the RAG index to avoid embedding API errors.

### Structured Output

`app/schemas/response.py:CustomerServiceResponse` — every reply includes intent, confidence, reply, requires_human, follow_up_question. The agent uses `response_format` (parsed) with a JSON fallback for non-supporting APIs.

## Testing

Tests call the real LLM API (no mocks). Requires a valid `OPENAI_API_KEY` in `.env`.

```bash
pytest tests/ -v
```

**Exception**: `test_rag.py` tests the RAG pipeline logic and does NOT require an API key.

Test file purposes:
- `test_agent.py` — structured output, intent recognition, multi-turn, reset
- `test_react_agent.py` — ReAct loop, tool calling, session persistence
- `test_rag.py` — RAG retrieval (no API key needed)
- `test_mcp.py` — MCP client/server integration
- `test_multi_agent.py` — multi-agent routing
- `test_memory.py` — memory system (STM + LTM)
- `test_skills.py` — skill loading
- `test_evaluation.py` — evaluation framework
- `test_conversation_management.py` — history compression

## Pitfalls

- **RAG index staleness**: After editing docs in `app/agent/rag/knowledge/`, rebuild the index. The retriever checks `embedding_model` consistency and raises `ValueError` if mismatched.
- **Session files are gitignored**: `app/sessions/` contains runtime data. Tests create isolated temp sessions.
- **Evaluation sandbox**: Disables `memory_enabled` and `mcp_enabled` globally during eval runs. Restore manually if running eval interactively.
- **Embedding fallback**: If your API provider doesn't support embeddings, use `--local-embed` (Chroma's `all-MiniLM-L6-v2`). Without it, RAG calls will fail.
- **History compression**: After 10 messages (configurable), old messages are summarized by LLM. Recent 3 are kept. This means context from very early in a long session may be lost.
- **Tool mock data**: All data is in `app/agent/tools/mock_data.py`. Order IDs follow `ORD-YYYYMMDD-NNN`.
