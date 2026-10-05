# AGENTS.md

This file provides guidance to AI coding agents like Claude Code (claude.ai/code), Cursor AI, Codex, Gemini CLI, GitHub Copilot, and other AI coding assistants when working with code in this repository.

## Project Summary

Hands-on workshop teaching AI/LLM observability with Dynatrace. Attendees run a RAG chatbot in GitHub Codespaces, add OpenLLMetry instrumentation, and analyze traces.

## Commands

```bash
# Run the sample app (from project root)
cd app && python main.py          # Serves on http://localhost:8000

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Dynatrace?", "use_rag": true}'

# Install dependencies
pip install -r app/requirements.txt

# Build docs locally
cd docs && bundle install && bundle exec jekyll serve
```

## Architecture

```
app/main.py          # FastAPI + LangChain RAG app (MAIN FILE attendees modify)
app/knowledge/       # Markdown knowledge base (one file per topic, front-matter + ## sections)
app/eval_rag.py      # Retrieval check: `python app/eval_rag.py` (offline), `--llm` for RAG on/off
app/static/          # Chat UI (marked.js for markdown, highlight.js for code)
docs/                # Jekyll GitHub Pages - lab guides (lab0-lab4)
.devcontainer/       # Codespace config (Python 3.11, Node 20)
```

### RAG Pipeline Flow (`app/main.py`)

```
@workflow: process_rag_chat()
  ├── @task: analyze_query_intent()   → LLM classifies query type
  ├── @task: retrieve_documents()     → select_documents(): best section → whole topic (+ related)
  ├── @task: generate_context()       → Format sections + workshop environment block
  └── @task: generate_response()      → Static system prompt; context sits next to the question
```

Retrieval uses `LocalHashingEmbeddings` (local, no embedding span). A topic named in the
question via a front-matter `keywords:` entry wins over the best-matching section. After
editing `app/knowledge/*.md` or the prompt, run `python app/eval_rag.py`. Keep
`RAG_SYSTEM_PROMPT` above 1,024 tokens (prompt caching) and free of facts; facts belong in the
knowledge files.

## Critical Configuration

| Variable | Required Value | Notes |
|----------|----------------|-------|
| `LLM_BASE_URL` | Must end with `/v1` | LiteLLM gateway |
| `LLM_CHAT_MODEL` | `workshop-chat` | Routes to Amazon Nova Micro |
| `DT_ENDPOINT` | Must end with `/api/v2/otlp` | Common mistake to omit suffix |

## Code Patterns

### Traceloop Decorators
```python
from traceloop.sdk.decorators import workflow, task

@workflow(name="rag_chat_pipeline")
def process_rag_chat(message: str):
    ...

@task(name="retrieve_documents")  
def retrieve_documents(query: str):
    ...
```

### FastAPI Lifespan (Modern Pattern)
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_rag()  # Startup
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)
```

### Instrumentation Location
Attendees add code at this marker in `app/main.py`:
```python
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# ---> ADD YOUR INSTRUMENTATION CODE HERE <---
```

## Workshop Labs Overview

| Lab | Focus | Persona Value |
|-----|-------|---------------|
| Lab 0 | Environment Setup | All |
| Lab 1 | Add Instrumentation | Developer: See your code in traces |
| Lab 2 | Explore Traces & Token Economics | Developer: Debug RAG pipeline; SRE: Cost analysis |
| Lab 3 | Dynatrace MCP + Error Investigation | Developer: Debug errors from IDE; SRE: Incident triage with MCP |
| Lab 4 | Workflow Automation | SRE: Automate cost alerts, daily summaries ("Hero Moment") |

## Error Simulation Feature

The UI has a **🐛 Simulate Errors** toggle that generates realistic RAG/LLM errors for workshop demos:

| Error Code | Exception | Simulates |
|------------|-----------|-----------|
| `EMB_NULL_VECTOR` | EmbeddingServiceError | Null vectors from embedding model |
| `CHROMA_COLLECTION_ERR` | VectorStoreConnectionError | ChromaDB connection failure |
| `LLM_MALFORMED_RESPONSE` | LLMResponseError | Invalid JSON from Azure OpenAI |
| `CTX_WINDOW_EXCEEDED` | ContextWindowExceededError | Token limit exceeded |
| `DOC_NO_MATCHES` | DocumentRetrievalError | No relevant documents found |
| `RAG_CHAIN_TIMEOUT` | RAGPipelineError | LangChain execution timeout |
| `CONTENT_FILTER_BLOCK` | LLMResponseError | Content policy violation |

Used in Lab 3 for practicing error investigation with Dynatrace MCP.

## Known Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Chat returns "Failed to send message" on long responses | Default fetch timeout | UI has 2-min AbortController timeout |
| Edits to `app/knowledge/` or `main.py` have no effect | Auto-reload is disabled | Stop and restart the app |
| Prompt caching not working | System prompt < 1024 tokens | Keep `RAG_SYSTEM_PROMPT` above 1,024 tokens |
| Deprecation warning on startup | `@app.on_event("startup")` | Use `lifespan` context manager |

## Protected Files

Do not modify without good reason:
- `.devcontainer/` — Tested Codespace config

## Key URLs

- Workshop Guide: https://marc-mas-ferrer.github.io/ai-mcp-ilt
- Secrets Server: https://workshop-secrets-server.azurewebsites.net
- Codespace: https://codespaces.new/marc-mas-ferrer/ai-mcp-ilt?quickstart=1
