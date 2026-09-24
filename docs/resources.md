---
layout: default
title: Resources
nav_order: 7
---

# Workshop Resources

Use this page as a reference for the technologies, configuration, DQL queries, and troubleshooting commands used throughout the workshop.

---

## Official Documentation

### Dynatrace

| Resource | Link |
|---|---|
| Dynatrace documentation | [docs.dynatrace.com](https://docs.dynatrace.com) |
| AI Observability overview | [Send AI Observability data to Dynatrace](https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/get-started) |
| OpenLLMetry getting started | [Get started with OpenLLMetry](https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/get-started/openllmetry) |
| OpenTelemetry and Dynatrace | [OpenTelemetry ingestion](https://docs.dynatrace.com/docs/ingest-from/opentelemetry) |
| OpenTelemetry troubleshooting | [Troubleshoot OTel ingestion](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/troubleshooting) |
| Dynatrace Query Language | [DQL documentation](https://docs.dynatrace.com/docs/discover-dynatrace/references/dynatrace-query-language) |
| Grail lookup data | [Lookup data in Grail](https://docs.dynatrace.com/docs/platform/grail/lookup-data) |
| Dynatrace MCP server | [Dynatrace MCP](https://docs.dynatrace.com/docs/dynatrace-intelligence/dynatrace-mcp) |
| Dynatrace Workflows | [Workflow automation](https://docs.dynatrace.com/docs/analyze-explore-automate/workflows) |

### OpenLLMetry and OpenTelemetry

| Resource | Link |
|---|---|
| OpenLLMetry repository | [traceloop/openllmetry](https://github.com/traceloop/openllmetry) |
| Traceloop documentation | [traceloop.com/docs](https://www.traceloop.com/docs) |
| OpenTelemetry Python | [OTel Python](https://opentelemetry.io/docs/languages/python/) |
| OTLP specification | [OTLP spec](https://opentelemetry.io/docs/specs/otlp/) |
| GenAI semantic conventions | [GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) |

### Workshop technologies

| Technology | Purpose | Link |
|---|---|---|
| Amazon Bedrock | Hosts Amazon Nova Micro | [AWS Bedrock docs](https://docs.aws.amazon.com/bedrock/) |
| Amazon Nova | Language model used by the workshop | [Amazon Nova docs](https://docs.aws.amazon.com/nova/) |
| LiteLLM | OpenAI-compatible gateway to Bedrock | [LiteLLM docs](https://docs.litellm.ai/) |
| LangChain | Application orchestration | [LangChain docs](https://docs.langchain.com/) |
| ChromaDB | Local vector store | [Chroma docs](https://docs.trychroma.com/) |
| GitHub Codespaces | Attendee development environment | [Codespaces docs](https://docs.github.com/en/codespaces) |

---

## Workshop Architecture

```text
Attendee browser
    │
    ▼
GitHub Codespace
    │
    ├── FastAPI application
    ├── LangChain RAG pipeline
    ├── Local deterministic vectoriser (384 dimensions, in-process)
    ├── Local ChromaDB vector store (in memory)
    ├── OpenTelemetry logging and FastAPI instrumentation
    └── OpenLLMetry instrumentation (added in Lab 1)
             │
             ├── OTLP traces and logs ──► Dynatrace
             │
             └── Chat requests ─────────► LiteLLM gateway
                                                │
                                                ▼
                                      Amazon Bedrock
                                      Amazon Nova Micro
```

Retrieval vectors are generated in-process, so only chat requests leave the Codespace for the model gateway. There is no embedding-model API call and no embedding token cost.

---

## Workshop Configuration Reference

### Required environment variables

The root `.env` file uses:

```bash
# Attendee identity, written by configure.sh
ATTENDEE_ID=your-workshop-id

# LiteLLM gateway
LLM_BASE_URL=http://INSTRUCTOR_PROVIDED_HOST:4000/v1
LLM_API_KEY=sk-workshop-INSTRUCTOR_PROVIDED_VALUE
LLM_CHAT_MODEL=workshop-chat

# Dynatrace OTLP ingestion
DT_ENDPOINT=https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.INSTRUCTOR_PROVIDED_VALUE

# Dynatrace MCP
DT_MCP_BEARER_TOKEN=dt0s16.INSTRUCTOR_PROVIDED_VALUE
```

Do not commit `.env` or copy token values into documentation.

### Common commands

```bash
# Apply your personalised configuration (the attendee ID is required)
bash .devcontainer/configure.sh --attendee-id=YOUR_WORKSHOP_ID

# Start the application
python app/main.py

# Validate the application syntax
python -m py_compile app/main.py

# Validate the shell scripts
bash -n .devcontainer/setup.sh
bash -n .devcontainer/configure.sh
```

After running `configure.sh`, reload VS Code with **Developer: Reload Window**.

---

## Dynatrace Instrumentation Reference

```python
import os
from traceloop.sdk import Traceloop

ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
DT_ENDPOINT = os.getenv("DT_ENDPOINT")
DT_API_TOKEN = os.getenv("DT_API_TOKEN")

os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"

if DT_ENDPOINT and DT_API_TOKEN:
    headers = {
        "Authorization": f"Api-Token {DT_API_TOKEN}"
    }

    Traceloop.init(
        app_name=f"ai-chat-service-{ATTENDEE_ID}",
        api_endpoint=DT_ENDPOINT,
        headers=headers
    )
```

| Item | Value |
|---|---|
| Service name | `ai-chat-service-{YOUR_ATTENDEE_ID}` |
| OTLP endpoint | Must end with `/api/v2/otlp` |
| Ingest authentication | `Authorization: Api-Token dt0c01...` |
| MCP authentication | `Bearer dt0s16...`, a separate credential |

Logging and FastAPI instrumentation are configured in the repository and run before Lab 1. The Traceloop initialisation above is what adds AI-specific telemetry.

---

## Model and Retrieval Reference

| Component | Workshop configuration |
|---|---|
| LiteLLM model alias | `workshop-chat` |
| Bedrock inference profile | `us.amazon.nova-micro-v1:0` |
| Maximum input tokens | `128000` |
| Maximum output tokens | `5000` |
| Input price | `$0.035` per 1 million tokens |
| Output price | `$0.14` per 1 million tokens |
| Retrieval vectoriser | Local deterministic hashing, 384 dimensions |
| Vector store | ChromaDB, in memory |
| Chunk size and overlap | 500 characters, 50 overlap |
| Retrieved chunks | Up to 3 |
| LLM calls per RAG request | 2 (intent classification and response generation) |

Depending on the instrumentation, `gen_ai.response.model` may contain either `workshop-chat` or `us.amazon.nova-micro-v1:0`. Both lookup tables contain both values.

---

## Grail Lookup Tables

### Model pricing

```dql
load "/lookups/ai/bedrock/model-costs"
```

Fields: `model`, `input_cost_per_million_usd`, `output_cost_per_million_usd`

### Model token limits

```dql
load "/lookups/ai/bedrock/model-max-tokens"
```

Fields: `model`, `max_input_tokens`, `max_output_tokens`

---

## Useful DQL Queries

Replace `{YOUR_ATTENDEE_ID}` with your attendee ID before running the queries.

### Recent spans

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| fields timestamp, trace.id, span.id, span.name, duration
| sort timestamp desc
| limit 100
```

### Span distribution

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| summarize span_count = count(), by: {span.name}
| sort span_count desc
```

### Model usage distribution

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.response.model)
| summarize request_count = count(), by: {gen_ai.response.model}
| sort request_count desc
```

### Token usage by model

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize
    total_input_tokens = sum(gen_ai.usage.input_tokens),
    total_output_tokens = sum(gen_ai.usage.output_tokens),
    avg_input_tokens = avg(gen_ai.usage.input_tokens),
    avg_output_tokens = avg(gen_ai.usage.output_tokens),
    request_count = count(),
    by: {gen_ai.response.model}
| fieldsAdd total_tokens = total_input_tokens + total_output_tokens
| sort total_tokens desc
```

### Token utilisation against model limits

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize
    total_input_tokens = sum(gen_ai.usage.input_tokens),
    total_output_tokens = sum(gen_ai.usage.output_tokens),
    avg_input_tokens = avg(gen_ai.usage.input_tokens),
    avg_output_tokens = avg(gen_ai.usage.output_tokens),
    request_count = count(),
    by: {gen_ai.response.model}
| fieldsAdd total_tokens = total_input_tokens + total_output_tokens
| lookup [load "/lookups/ai/bedrock/model-max-tokens"],
    sourceField:gen_ai.response.model,
    lookupField:model,
    prefix:"limits."
| filter isNotNull(limits.model)
| fieldsAdd input_token_usage_percent = 100.0 * avg_input_tokens / limits.max_input_tokens
| fieldsAdd output_token_usage_percent = 100.0 * avg_output_tokens / limits.max_output_tokens
| fields gen_ai.response.model, request_count, total_input_tokens, total_output_tokens,
         total_tokens, avg_input_tokens, avg_output_tokens,
         input_token_usage_percent, output_token_usage_percent
| sort total_tokens desc
```

### Estimated model cost

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize
    total_input_tokens = sum(gen_ai.usage.input_tokens),
    total_output_tokens = sum(gen_ai.usage.output_tokens),
    request_count = count(),
    by: {gen_ai.response.model}
| fieldsAdd total_tokens = total_input_tokens + total_output_tokens
| lookup [load "/lookups/ai/bedrock/model-costs"],
    sourceField:gen_ai.response.model,
    lookupField:model,
    prefix:"pricing."
| filter isNotNull(pricing.model)
| fieldsAdd estimated_cost_usd = (
      total_input_tokens * pricing.input_cost_per_million_usd
    + total_output_tokens * pricing.output_cost_per_million_usd
  ) / 1000000.0
| fields gen_ai.response.model, request_count, total_input_tokens,
         total_output_tokens, total_tokens, estimated_cost_usd
| sort estimated_cost_usd desc
```

### LLM latency by operation

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.response.model)
| summarize
    request_count = count(),
    avg_duration = avg(duration),
    p50_duration = percentile(duration, 50),
    p95_duration = percentile(duration, 95),
    max_duration = max(duration),
    by: {span.name, gen_ai.response.model}
| sort avg_duration desc
```

### Requests with the largest prompts

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| fields timestamp, trace.id, span.name, gen_ai.response.model,
         gen_ai.usage.input_tokens, gen_ai.usage.output_tokens, duration
| sort gen_ai.usage.input_tokens desc
| limit 20
```

### Token usage over time

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| makeTimeseries
    total_input_tokens = sum(gen_ai.usage.input_tokens),
    total_output_tokens = sum(gen_ai.usage.output_tokens),
    request_count = count(),
    interval: 1m
```

### Simulated error logs

```dql
fetch logs
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter error.simulated == "true"
| fields timestamp, error.code, error.message, error.stage,
         attendee.id, trace_id, span_id
| sort timestamp desc
```

### Simulated error distribution

```dql
fetch logs
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter error.simulated == "true"
| summarize error_count = count(), by: {error.code}
| sort error_count desc
```

### Simulated error codes

The application selects one of these at random on each request while **Simulate Errors** is enabled:

| Error code | Simulated condition |
|---|---|
| `EMB_NULL_VECTOR` | Local vectorisation returned a null vector |
| `EMB_DIMENSION_MISMATCH` | Vector dimension mismatch, 384 expected and 0 received |
| `CHROMA_COLLECTION_ERR` | ChromaDB collection not found or corrupted |
| `LLM_MALFORMED_RESPONSE` | The LLM gateway returned a malformed response |
| `CTX_WINDOW_EXCEEDED` | The request exceeded the simulated context limit |
| `DOC_NO_MATCHES` | Vector search returned no relevant documents |
| `RAG_CHAIN_TIMEOUT` | The RAG pipeline exceeded the simulated timeout |
| `CONTENT_FILTER_BLOCK` | The response was blocked by a simulated policy check |

---

## Workshop Credentials and Permissions

The workshop uses two different Dynatrace tokens, and they are not interchangeable.

### OTLP ingest token

| Value | Purpose |
|---|---|
| Environment variable | `DT_API_TOKEN` |
| Prefix | `dt0c01.` |
| Authentication | `Api-Token` |
| Used by | OpenTelemetry and Traceloop exporters |

For a Classic access token, Dynatrace documents the required scopes for OpenLLMetry ingestion as `openTelemetryTrace.ingest`, `metrics.ingest` and `logs.ingest`. A platform token can be used instead, with the `openpipeline:traces:ingest`, `openpipeline:metrics:ingest` and `openpipeline:logs:ingest` scopes. See [Get started with OpenLLMetry](https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/get-started/openllmetry).

### MCP platform token

| Value | Purpose |
|---|---|
| Environment variable | `DT_MCP_BEARER_TOKEN` |
| Prefix | `dt0s16.` |
| Authentication | `Bearer` |
| Used by | `.vscode/mcp.json` |

The MCP server tools each require their own scopes. The Data Analysis Agent needs `storage:buckets:read` plus a read scope for each data type you query, such as `storage:logs:read`. The Davis CoPilot tools need `davis-copilot:nl2dql:execute`, `davis-copilot:dql2nl:execute` and `davis-copilot:conversations:execute`. See the [Dynatrace MCP server documentation](https://docs.dynatrace.com/docs/dynatrace-intelligence/dynatrace-mcp).

> `configure.sh` writes your MCP token directly into `.vscode/mcp.json`. That file contains a live credential after Lab 0. Do not commit it or share its contents.

---

## Verification Commands

### Confirm required variables without printing secrets

```bash
for variable in \
  ATTENDEE_ID \
  LLM_BASE_URL \
  LLM_API_KEY \
  LLM_CHAT_MODEL \
  DT_ENDPOINT \
  DT_API_TOKEN \
  DT_MCP_BEARER_TOKEN
do
  if [ -n "${!variable}" ]; then
    echo "OK: $variable is configured"
  else
    echo "MISSING: $variable"
  fi
done
```

### Confirm Traceloop is available

```bash
python -c "from traceloop.sdk import Traceloop; print('Traceloop available')"
```

### Test the local application

With the application running:

```bash
curl -s http://localhost:8000/health
```

```bash
curl -s http://localhost:8000/info
```

### Test the chat endpoint

```bash
curl -s http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Dynatrace?",
    "use_rag": true,
    "simulate_errors": false
  }'
```

---

## Common Issues

### The application cannot reach the LLM gateway

Check that `LLM_BASE_URL` ends with `/v1`, `LLM_API_KEY` matches the instructor-provided key, `LLM_CHAT_MODEL` is `workshop-chat`, and that no placeholder value such as `INSTRUCTOR_GATEWAY` or `PASTE_HERE` remains in `.env`.

### LiteLLM returns `No connected db`

For this workshop setup, this usually means the supplied `LLM_API_KEY` does not match the gateway key.

Copy the key again, save `.env`, rerun `configure.sh --attendee-id=YOUR_WORKSHOP_ID`, and restart the application.

### No traces appear

Traces only appear after Lab 1. Check that `traceloop-sdk` is installed, `Traceloop.init()` ran at startup, `DT_ENDPOINT` ends with `/api/v2/otlp`, the application processed recent requests, and the Dynatrace timeframe includes them.

Logs and HTTP spans can arrive before Lab 1, because those are configured in the repository.

### Lookup queries return no records

A lookup that finds no match does not error. The `filter isNotNull(...)` line removes the unmatched rows, leaving an empty result.

Compare the observed model value with the lookup:

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.response.model)
| summarize request_count = count(), by: {gen_ai.response.model}
```

```dql
load "/lookups/ai/bedrock/model-costs"
```

The observed value must exist in the lookup's `model` field.

### No embedding span appears

This is expected. Retrieval vectors are generated in-process by a deterministic hashing function, not by a trained embedding model, so nothing is sent to a hosted embedding endpoint.

Look for the document-retrieval task and the ChromaDB vector-search span instead.

### Dynatrace MCP does not appear in Copilot

1. `.vscode/mcp.json` exists and contains valid JSON.
2. The `Authorization` header contains a token beginning with `dt0s16.`, not an unreplaced placeholder.
3. `configure.sh --attendee-id=YOUR_WORKSHOP_ID` completed successfully.
4. VS Code was reloaded.
5. Copilot Chat is in Agent mode and the Dynatrace MCP tools are enabled.

---

## Where to Go Next

The workshop covers one instrumentation path and one automation pattern. These are the natural next steps.

### dtctl, the Dynatrace CLI

[dtctl](https://github.com/dynatrace-oss/dtctl) is the open-source, kubectl-style CLI for the Dynatrace platform, built for both engineers and AI agents. It is directly relevant to what you built in this workshop: it manages lookup tables, workflows, dashboards, notebooks and DQL queries from the terminal.

```bash
brew install dynatrace-oss/tap/dtctl
dtctl auth login --context my-env --environment "https://abc12345.apps.dynatrace.com"
dtctl doctor
```

```bash
dtctl query "fetch spans | limit 10"
dtctl get workflows --mine
dtctl apply -f workflow.yaml
dtctl exec copilot nl2dql "error logs from last hour"
```

The `apply` command is idempotent, so you can keep workflow and dashboard definitions in version control and push changes from CI/CD. That turns the Lab 4 workflow into something reviewable in a pull request rather than clicked together in a UI. See the [Quick Start guide](https://dynatrace-oss.github.io/dtctl/docs/quick-start/).

> dtctl is a community-supported open-source project, not an officially supported Dynatrace product.

### Zero-code AI observability with OneAgent

In Lab 1 you instrumented the application by hand. Dynatrace OneAgent can capture AI telemetry with no code changes at all, which is usually the faster path for existing workloads. See [Send AI Observability data to Dynatrace](https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/get-started).

### Other instrumentation options

Dynatrace ingests `gen_ai.*` telemetry from OpenLLMetry, OpenInference, plain OpenTelemetry and OneAgent, and presents them in the same experience. If your team already uses a different SDK, you do not need to switch to get the views you saw in Lab 2.

### Evaluate AI quality, not just cost and latency

This workshop measured tokens, latency and cost. It did not measure whether the answers were any good. Dynatrace supports LLM-as-a-judge scoring of production traces through the open-source `dt-evals` CLI, attaching quality scores to the same spans you already analysed, so regressions in completeness, relevance or toxicity surface alongside performance. See [LLM-as-a-judge evaluations](https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/get-started).

### Multi-agent systems

If your application grows into multiple agents calling each other, Smartscape maps the agent topology, including which models and tools each agent depends on. See [AI Observability on Dynatrace Hub](https://www.dynatrace.com/hub/detail/ai-and-llm-observability/).

### Extend the workshop workflow

The Lab 4 workflow evaluates one threshold. Practical extensions include SLOs on model latency or error rate, alerting on average prompt size rather than raw token volume, and a scheduled report that combines usage with cost.

---

## Further Learning

- [Dynatrace University](https://university.dynatrace.com/)
- [Dynatrace Community](https://community.dynatrace.com/)
- [Dynatrace Developer](https://developer.dynatrace.com/)
- [Dynatrace on GitHub](https://github.com/Dynatrace)
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)

### Workshop repository

- [Workshop repository](https://github.com/marc-mas-ferrer/ai-mcp-ilt)
- [Launch the workshop Codespace](https://codespaces.new/marc-mas-ferrer/ai-mcp-ilt?quickstart=1)
- [Workshop guide](https://marc-mas-ferrer.github.io/ai-mcp-ilt/)

---

## Getting Help

**During the workshop**, ask the instructor or use the workshop communication channel. Include the visible error message, but never share token values.

**After the workshop**, use the [Dynatrace Community](https://community.dynatrace.com/) or [Dynatrace Support](https://support.dynatrace.com/).

---

<div class="lab-nav">
  <a href="lab4-automation">← Lab 4: Automation</a>
  <a href="./">Back to Home →</a>
</div>
