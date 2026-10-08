# Dynatrace AI Observability & MCP Workshop

A hands-on workshop for learning AI/LLM observability with Dynatrace, OpenTelemetry, OpenLLMetry and the Model Context Protocol (MCP).

Attendees run a small RAG chat service in a GitHub Codespace, instrument it with OpenLLMetry, analyse the resulting traces and logs in Dynatrace, investigate the service from the IDE with Dynatrace MCP, and automate a token-usage check with a Dynatrace Workflow.

---

> ## **Workshop Attendees: Start Here!**
> 
> ### [![📖 Open the guide](https://img.shields.io/badge/📖_Open_Workshop_Guide-Click_Here_to_Start-blue?style=for-the-badge&logoColor=white)](https://marc-mas-ferrer.github.io/ai-mcp-ilt)
>
> The guide walks you through launching your Codespace, configuring your environment, and completing all labs with detailed instructions, code snippets, and screenshots.

---

## Workshop overview

| | |
|---|---|
| **Duration** | 2 - 2.5 hours |
| **Level** | Intermediate |
| **Format** | Hands-on labs |
| **Platform** | GitHub Codespaces |
| **Language** | Python 3.11 |

### What you will learn

- Instrument a Python AI application with OpenLLMetry (Traceloop)
- Send traces and logs to Dynatrace over OTLP
- Analyse LLM calls, token usage, RAG stages and errors in Dynatrace
- Query your own telemetry from VS Code using Dynatrace MCP
- Automate a token-usage and cost check with a Dynatrace Workflow

---

## Labs

| Lab | Focus |
|---|---|
| [Lab 0 - Setup](https://marc-mas-ferrer.github.io/ai-mcp-ilt/lab0-setup.html) | Launch the Codespace, fill in `.env`, run the configuration script |
| [Lab 1 - Instrumentation](https://marc-mas-ferrer.github.io/ai-mcp-ilt/lab1-instrumentation.html) | Enable the Traceloop dependency and initialise OpenLLMetry |
| [Lab 2 - Explore traces](https://marc-mas-ferrer.github.io/ai-mcp-ilt/lab2-explore-traces.html) | Analyse spans, prompts, token usage and cost in Dynatrace |
| [Lab 3 - Dynatrace MCP](https://marc-mas-ferrer.github.io/ai-mcp-ilt/lab3-dynatrace-mcp.html) | Investigate the service from GitHub Copilot in VS Code |
| [Lab 4 - Automation](https://marc-mas-ferrer.github.io/ai-mcp-ilt/lab4-automation.html) | Build a workflow that evaluates token usage and notifies |

The source for the guide lives in the `docs/` folder and is published as the workshop site.

---

## Architecture

```text
Browser (chat UI served by FastAPI)
  │
  ▼
GitHub Codespace
  ├── FastAPI application (app/main.py)
  ├── LangChain RAG orchestration
  ├── Local deterministic vectoriser (no model download, no network call)
  ├── In-memory ChromaDB collection
  ├── OpenTelemetry logging  ──────────► Dynatrace (OTLP /v1/logs)
  ├── FastAPI OTel instrumentation ────► Dynatrace
  └── OpenLLMetry / Traceloop (added in Lab 1) ──► Dynatrace
  │
  └── Chat completions ───────────────► LiteLLM gateway ──► Amazon Bedrock (Amazon Nova Micro)
```

Only chat completions leave the Codespace for the model gateway. Retrieval vectors are produced locally, so there is no embedding-model API call and no embedding-provider span.

---

## The sample application

A small Retrieval Augmented Generation service built with FastAPI, LangChain and ChromaDB.

### Retrieval

- The knowledge base is a set of markdown files in `app/knowledge/`, one per topic (Dynatrace platform, OpenTelemetry, OpenLLMetry, AI observability, Grail and DQL, Dynatrace MCP, and this workshop app). Each file starts with a front-matter header (`title`, `topic`, `keywords`) and is divided into `##` sections.
- Each section is indexed as one chunk, prefixed with its title and section name. A section is only split further if it exceeds 1,500 characters, so a block of related facts is never cut in half.
- Vectors are produced by `LocalHashingEmbeddings`, a deterministic 384-dimension feature-hashing embedder. It combines word features, adjacent-word bigrams and character n-grams, hashes them with SHA-256 and applies L2 normalisation. Common question words are ignored, and identifiers such as `EMB_NULL_VECTOR` are also indexed by their parts.
- Chunks are stored in an in-memory Chroma collection named `workshop_{ATTENDEE_ID}`.
- Retrieval finds the best-matching section, then returns the whole topic it belongs to, plus up to two closely related sections from other topics. If the question names a topic by one of its front-matter `keywords` (for example "openllmetry" or "mcp"), that topic is used.
- A short "Your workshop environment" block (the attendee's service name, the chat model and a DQL query for their own traces) is added to every context.

The local vectoriser is intentionally simple and dependency-free so the workshop runs identically for every attendee. A production RAG system would normally use a trained embedding model.

### Extending the knowledge base

Add or edit a markdown file in `app/knowledge/`, using the same front-matter header and `##` sections, then restart the app. Put the keywords that should select the topic in the `keywords:` line. To check retrieval without calling a model:

```bash
python app/eval_rag.py
```

It prints the sections retrieved for a fixed set of questions and fails if the facts a good answer needs are missing from the context. Add `--llm` (needs the `LLM_*` values in `.env`) to also ask the chat model each question three times, with RAG on and off, and flag invented names or a missing "In this workshop" section.

### Request flow

With **Use Knowledge Base (RAG)** enabled, a `/chat` request runs a workflow with these stages:

1. `analyze_query_intent` - a short LLM call that classifies the question
2. `retrieve_documents` - local vectorisation plus a ChromaDB similarity search
3. `generate_context` - formats the retrieved sections and adds the workshop environment block
4. `generate_response` - the main LLM call; a static system prompt, with the retrieved reference material placed next to the question in the user message
5. source summarisation for the response payload

So one RAG request produces **two** chat-model calls. With RAG disabled, the request makes a single direct model call and skips retrieval.

### Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Chat UI |
| `/chat` | POST | Chat API (`message`, `use_rag`, `simulate_errors`) |
| `/documents` | POST | Add content to the in-memory vector store |
| `/info` | GET | Service name, attendee ID, model and vectoriser details |
| `/health` | GET | Health check |
| `/api/health` | GET | Health check used by the UI |

### Error simulation

The UI has a **Simulate Errors** toggle. When enabled, the service always raises a simulated failure, chosen at random from a set of realistic RAG scenarios such as a null vector, a missing Chroma collection, a malformed gateway response, an exceeded context window, an empty retrieval result, a chain timeout, a content-filter block, or a vector-dimension mismatch.

Each simulated failure writes a structured error log with an error code and stage, flushes the log to Dynatrace, and returns HTTP 500. This gives attendees real failure data to investigate.

### Chat UI

`app/static/index.html` is a single self-contained page with inline styles and scripts. It reads service details from `/info`, posts to `/chat`, renders Markdown responses, highlights code blocks, labels each answer ("Grounded in N workshop sources" for RAG, "General model knowledge" otherwise), shows retrieved sources when present, and aborts a request after two minutes. Fonts, Marked and Highlight.js are loaded from public CDNs, so the Codespace needs internet access.

---

## What is instrumented, and when

Part of the observability stack is already in place before Lab 1.

**Already configured in the repository:**

- OpenTelemetry logging to Dynatrace, exported to `{DT_ENDPOINT}/v1/logs` with `Api-Token` authentication, using a batch processor and the resource attribute `service.name = ai-chat-service-{ATTENDEE_ID}`
- `@workflow` and `@task` decorators on the RAG pipeline functions, imported conditionally

**Added by the attendee in Lab 1:**

- Uncommenting `traceloop-sdk` in `app/requirements.txt`
- Initialising Traceloop with the attendee service name, the Dynatrace OTLP endpoint and the API token

If Traceloop is not installed, the application still runs. The decorators fall back to no-ops and the `Traceloop.set_association_properties` call is skipped, so the RAG hierarchy and AI-specific attributes simply do not appear until Lab 1 is complete.

When Traceloop is active, each chat request also records association properties for the user question, the RAG setting and the error-simulation setting.

---

## Configuration

All configuration lives in a single `.env` file at the repository root.

| Variable | Purpose |
|---|---|
| `ATTENDEE_ID` | Written by `configure.sh`; drives the service and collection names |
| `LLM_BASE_URL` | LiteLLM gateway base URL; must end with `/v1` |
| `LLM_API_KEY` | Workshop gateway key |
| `LLM_CHAT_MODEL` | Must be `workshop-chat` |
| `DT_ENDPOINT` | Dynatrace OTLP endpoint; must end with `/api/v2/otlp` |
| `DT_API_TOKEN` | Dynatrace ingest token for traces and logs |
| `DT_MCP_BEARER_TOKEN` | Dynatrace platform token used by the MCP server in Lab 3 |

Optional overrides: `APP_HOST` (default `0.0.0.0`) and `APP_PORT` (default `8000`).

Do not commit `.env`.

---

## Attendee setup

1. **Launch the Codespace.** The devcontainer uses the Python 3.11 image, adds Node.js 20, installs the Python, Pylance, Copilot, Copilot Chat, YAML and Prettier extensions, and forwards port 8000, opening the chat UI in a browser automatically.

2. **Let `setup.sh` finish.** It runs automatically after creation, installs everything in `app/requirements.txt`, and creates a guided `.env` with `PASTE_HERE` placeholders. An existing `.env` is never overwritten.

3. **Fill in `.env`** with the credential values provided by the instructor. Leave `ATTENDEE_ID` empty.

4. **Run the personalised configuration command:**

   ```bash
   bash .devcontainer/configure.sh --attendee-id=YOUR_WORKSHOP_ID
   ```

   The Workshop ID is lower-cased and must be 2-31 characters of lowercase letters, numbers and hyphens. Email addresses are rejected.

   The script writes the ID into `.env`, verifies that every required variable is present and not still `PASTE_HERE`, checks that `LLM_BASE_URL` ends with `/v1`, that `LLM_CHAT_MODEL` is `workshop-chat`, and that `DT_ENDPOINT` ends with `/api/v2/otlp`, warns about unexpected token prefixes, exports the values into `~/.bashrc` for future terminals, and configures the authorization header in the workspace copy of `.mcp.json`. Secret values are validated but never printed.

5. **Reload VS Code** with *Developer: Reload Window*, so Copilot and the MCP client pick up the new configuration.

6. **Start the application:**

   ```bash
   python app/main.py
   ```

   The service starts on port 8000. Auto-reload is disabled on purpose, because it initialises OpenTelemetry twice, so stop the app (Ctrl+C) and start it again after editing. Your service appears in Dynatrace as `ai-chat-service-{ATTENDEE_ID}`.

If RAG initialisation fails at startup, the application stops with an error instead of serving degraded results.

---

## Dynatrace MCP (Lab 3)

MCP is configured in `.mcp.json` as an HTTP server named `Dynatrace-MCP`, pointing at the Dynatrace MCP gateway endpoint. The bearer token comes from `DT_MCP_BEARER_TOKEN` and is applied to the workspace copy by `configure.sh`.

`configure.sh` fails if `.mcp.json` is missing or has no authorization header, because Lab 3 cannot run without it.

Never paste a platform token directly into `.mcp.json`, and never commit one.

---

## Instructors: what the repository requires

This is not a setup runbook. It is the contract the repository enforces, so that whatever you stand up is accepted by `configure.sh`.

Attendees paste six values into `.env`. Everything else is derived.

| Value | Constraint enforced by `configure.sh` |
|---|---|
| `LLM_BASE_URL` | Must end with `/v1` |
| `LLM_API_KEY` | Warns if it does not start with `sk-workshop-` |
| `LLM_CHAT_MODEL` | Must be exactly `workshop-chat`; any other value is rejected |
| `DT_ENDPOINT` | Must end with `/api/v2/otlp` |
| `DT_API_TOKEN` | Warns if it does not start with `dt0c01.` |
| `DT_MCP_BEARER_TOKEN` | Warns if it does not start with `dt0s16.` |

So your gateway must publish the model alias `workshop-chat`, and your Dynatrace endpoint must be the OTLP path rather than the environment root. The prefix checks are warnings, not failures, so a mistyped token will pass configuration and fail later at runtime.

`configure.sh` also fails outright if `.mcp.json` is missing or has no `Authorization` header, because Lab 3 cannot run without it.

Attendees choose their own Workshop ID, so nothing per-attendee needs preparing.

Rotate the gateway key and the Dynatrace tokens after each session, and prefer a dedicated playground tenant.

> Token scopes, gateway deployment and the Lab 4 Grail pricing lookup are not visible from this repository. Keep those in the instructor guide.

---

## Repository layout

```text
.mcp.json                Dynatrace MCP server definition
.devcontainer/
  devcontainer.json     Codespace definition
  setup.sh              Dependency install and guided .env creation
  configure.sh          Workshop ID, validation, env persistence, MCP token
app/
  main.py               FastAPI service, RAG pipeline, local vectoriser
  knowledge/            Markdown knowledge base used for retrieval
  eval_rag.py           Retrieval check (offline) and RAG on/off check (--llm)
  requirements.txt      Dependencies, with traceloop-sdk commented out for Lab 1
  static/index.html     Self-contained chat UI
docs/                   Published workshop guide
```

---

## Troubleshooting

**No traces in Dynatrace.** Traces appear only after Lab 1. Confirm that `traceloop-sdk` is uncommented and installed, that the Traceloop initialisation sits below the marker and after `load_dotenv()`, and that `DT_ENDPOINT` ends with `/api/v2/otlp`.

**Logs but no AI spans.** Logs can arrive before OpenLLMetry is initialised. That is expected before Lab 1.

**Startup fails immediately.** RAG initialisation requires `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_CHAT_MODEL`. Re-run `configure.sh` and read its validation output.

**MCP tools missing in Copilot.** Reload the VS Code window, check that `.mcp.json` is valid JSON, and confirm the token is present and unexpired.

**Knowledge base looks empty after a restart.** The vector store is in memory and is rebuilt from `app/knowledge/` on every start. Anything added through `/documents` is lost when the process stops.

**An edit to a knowledge file has no effect.** The files are read at startup. Restart the app, since auto-reload is disabled.

---

## Security notes

- `.env` holds live workshop credentials. Keep it out of version control.
- `configure.sh` validates secrets without echoing them.
- Attendee changes stay inside each isolated Codespace.
- Rotate the gateway key and Dynatrace tokens after every workshop.

---

## Acknowledgments

- OpenLLMetry / Traceloop
- Dynatrace
- OpenTelemetry
- LangChain and ChromaDB
