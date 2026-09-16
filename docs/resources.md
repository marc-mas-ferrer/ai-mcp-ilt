---
layout: default
title: Resources
nav_order: 7
---

# 📚 Workshop Resources

Use this page as a reference for the technologies, configuration, DQL queries, and troubleshooting commands used throughout the workshop.

---

## 🔗 Official Documentation

### Dynatrace

| Resource | Link |
|---|---|
| Dynatrace documentation | [Open Dynatrace documentation](https://docs.dynatrace.com) |
| OpenTelemetry and Dynatrace | [Learn about OpenTelemetry ingestion](https://docs.dynatrace.com/docs/ingest-from/opentelemetry) |
| OpenTelemetry setup | [Get started with OpenTelemetry](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/getting-started) |
| OpenTelemetry troubleshooting | [Troubleshoot OpenTelemetry ingestion](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/troubleshooting) |
| Dynatrace Query Language | [Explore DQL documentation](https://docs.dynatrace.com/docs/discover-dynatrace/references/dynatrace-query-language) |
| Grail lookup data | [Learn about lookup data in Grail](https://docs.dynatrace.com/docs/platform/grail/lookup-data) |
| Dynatrace MCP server | [Explore Dynatrace MCP](https://docs.dynatrace.com/docs/dynatrace-intelligence/dynatrace-mcp) |
| Dynatrace Intelligence | [Explore Dynatrace Intelligence](https://docs.dynatrace.com) |
| Dynatrace Workflows | [Explore workflow automation](https://docs.dynatrace.com/docs/analyze-explore-automate/workflows) |

### OpenLLMetry and Traceloop

| Resource | Link |
|---|---|
| OpenLLMetry repository | [View OpenLLMetry on GitHub](https://github.com/traceloop/openllmetry) |
| Traceloop documentation | https://www.traceloop.com/docs |
| Traceloop integrations | [Explore supported integrations](https://www.traceloop.com/docs/penTelemetry

| Resource | Link |
|---|---|
| OpenTelemetry Python | [ttps://opentelemetry.io/docs/languages/python/ |
| OTLP specification | [Read the OTLP specification](https://opentelemetry.io/docs/specs/otlp/) |
| GenAI semantic conventions | [Explore GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) |
| OpenTelemetry Collector | https://opentelemetry.io/docs/collector/ |

### Workshop technologies

| Technology | Purpose | Link |
|---|---|---|
| Amazon Bedrock | Hosts Amazon Nova Micro | https://docs.aws.amazon.com/bedrock/ |
| Amazon Nova | Language model used by the workshop | https://docs.aws.amazon.com/nova/ |
| LiteLLM | OpenAI-compatible gateway to Bedrock | https://docs.litellm.ai/ |
| LangChain | Application orchestration | https://docs.langchain.com/ |
| ChromaDB | Local vector store | https://docs.trychroma.com/ |
| Sentence Transformers | Local embedding model | https://sbert.net/ |
| GitHub Codespaces | Attendee development environment | https://docs.github.com/en/codespaces |

---

## 🏗️ Workshop Architecture

```text
Attendee browser
    │
    ▼
GitHub Codespace
    │
    ├── FastAPI application
    ├── LangChain RAG pipeline
    ├── Local all-MiniLM-L6-v2 embeddings
    ├── Local ChromaDB vector store
    └── OpenLLMetry instrumentation
             │
             ├── OTLP traces and logs ──► Dynatrace
             │
             └── Chat requests ─────────► LiteLLM gateway
                                                │
                                                ▼
                                      Amazon Bedrock
                                      Amazon Nova Micro
```

The local embedding model does not call Amazon Bedrock. Only chat requests pass through LiteLLM to Amazon Nova Micro.

---

## 🛠️ Workshop Configuration Reference

### Required environment variables

The root `.env` file uses:

```bash
# Attendee identity
ATTENDEE_ID=your-unique-id

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

### Apply the workshop configuration

```bash
bash .devcontainer/configure.sh
```

After running the script, reload VS Code using:

```text
Developer: Reload Window
```

### Start the application

```bash
python app/main.py
```

### Validate the application syntax

```bash
python -m py_compile app/main.py
```

### Validate the MCP configuration

```bash
python -m json.tool .vscode/mcp.json
```

---

## 🔬 Dynatrace Instrumentation Reference

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

The service name is:

```text
ai-chat-service-{YOUR_ATTENDEE_ID}
```

The OTLP ingest endpoint must end with:

```text
/api/v2/otlp
```

The ingest authentication header uses:

```text
Authorization: Api-Token dt0c01...
```

The MCP token uses Bearer authentication and is a separate credential.

---

## 🧠 Model and Retrieval Reference

| Component | Workshop configuration |
|---|---|
| LiteLLM model alias | `workshop-chat` |
| Bedrock inference profile | `us.amazon.nova-micro-v1:0` |
| Maximum input tokens | `128000` |
| Maximum output tokens | `10000` |
| Input price | `$0.035` per 1 million tokens |
| Output price | `$0.14` per 1 million tokens |
| Local embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store | ChromaDB |
| Retrieved chunks | Up to 3 |

Depending on the instrumentation, `gen_ai.response.model` may contain:

```text
workshop-chat
```

or:

```text
us.amazon.nova-micro-v1:0
```

The lookup tables contain both values.

---

## 📂 Grail Lookup Tables

### Model pricing

```dql
load "/lookups/ai/bedrock/model-costs"
```

Expected fields:

- `model`
- `input_cost_per_million_usd`
- `output_cost_per_million_usd`

### Model token limits

```dql
load "/lookups/ai/bedrock/model-max-tokens"
```

Expected fields:

- `model`
- `max_input_tokens`
- `max_output_tokens`

### List available Grail files

```dql
fetch dt.system.files
| filter startsWith(path, "/lookups/")
| sort path asc
```

---

## 📊 Useful DQL Queries

Replace `{YOUR_ATTENDEE_ID}` with your attendee ID before running the queries.

### Recent spans

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| fields
    timestamp,
    trace.id,
    span.id,
    span.name,
    duration
| sort timestamp desc
| limit 100
```

### Span distribution

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| summarize
    span_count = count(),
    by: {span.name}
| sort span_count desc
```

### Model usage distribution

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.response.model)
| summarize
    request_count = count(),
    by: {gen_ai.response.model}
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
| fieldsAdd total_tokens =
    total_input_tokens + total_output_tokens
| sort total_tokens desc
```

### Token utilisation against model limits

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize
    total_input = sum(gen_ai.usage.input_tokens),
    total_output = sum(gen_ai.usage.output_tokens),
    avg_input = avg(gen_ai.usage.input_tokens),
    avg_output = avg(gen_ai.usage.output_tokens),
    request_count = count(),
    by: {gen_ai.response.model}
| fieldsAdd total_tokens = total_input + total_output
| lookup [load "/lookups/ai/bedrock/model-max-tokens"],
    sourceField:gen_ai.response.model,
    lookupField:model,
    prefix:"limits."
| filter isNotNull(limits.model)
| fieldsAdd input_token_usage_percent =
    100.0 * avg_input / limits.max_input_tokens
| fieldsAdd output_token_usage_percent =
    100.0 * avg_output / limits.max_output_tokens
| fields
    gen_ai.response.model,
    request_count,
    total_input,
    total_output,
    total_tokens,
    avg_input,
    avg_output,
    input_token_usage_percent,
    output_token_usage_percent
| sort total_tokens desc
```

### Estimated model cost

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize
    total_input = sum(gen_ai.usage.input_tokens),
    total_output = sum(gen_ai.usage.output_tokens),
    request_count = count(),
    by: {gen_ai.response.model}
| fieldsAdd total_tokens = total_input + total_output
| lookup [load "/lookups/ai/bedrock/model-costs"],
    sourceField:gen_ai.response.model,
    lookupField:model,
    prefix:"pricing."
| filter isNotNull(pricing.model)
| fieldsAdd estimated_cost_usd =
    (
        total_input * pricing.input_cost_per_million_usd
        + total_output * pricing.output_cost_per_million_usd
    ) / 1000000.0
| fields
    gen_ai.response.model,
    request_count,
    total_input,
    total_output,
    total_tokens,
    estimated_cost_usd
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
| fields
    timestamp,
    trace.id,
    span.name,
    gen_ai.response.model,
    gen_ai.usage.input_tokens,
    gen_ai.usage.output_tokens,
    duration
| sort gen_ai.usage.input_tokens desc
| limit 20
```

### Token usage over time

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| makeTimeseries
    total_input = sum(gen_ai.usage.input_tokens),
    total_output = sum(gen_ai.usage.output_tokens),
    request_count = count(),
    interval: 1m
```

### Error spans

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter otel.status_code == "ERROR"
| fields
    timestamp,
    trace.id,
    span.id,
    span.name,
    duration,
    otel.status_code
| sort timestamp desc
```

### Simulated error logs

```dql
fetch logs
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter error.simulated == "true"
| fields
    timestamp,
    error.code,
    error.message,
    error.stage,
    attendee.id,
    trace_id,
    span_id
| sort timestamp desc
```

### Simulated error distribution

```dql
fetch logs
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter error.simulated == "true"
| summarize
    error_count = count(),
    by: {error.code}
| sort error_count desc
```

---

## 🔐 Workshop Credentials and Permissions

The workshop uses two different Dynatrace tokens.

### OTLP ingest token

The application uses a Dynatrace API token to export traces and logs.

| Value | Purpose |
|---|---|
| Environment variable | `DT_API_TOKEN` |
| Typical prefix | `dt0c01` |
| Authentication | `Api-Token` |
| Used by | OpenTelemetry and Traceloop exporters |
| Required permission | `openTelemetryTrace.ingest` |
| Additional permission used by the application | Log ingest permission configured by the instructor |

### MCP platform token

GitHub Copilot uses a Dynatrace platform token to call the remote MCP server.

| Value | Purpose |
|---|---|
| Environment variable | `DT_MCP_BEARER_TOKEN` |
| Typical prefix | `dt0s16` |
| Authentication | `Bearer` |
| Used by | `.vscode/mcp.json` |
| Access | Limited by the platform-token permissions |

The MCP token requires permissions for the MCP gateway and the data the workshop queries, including access to spans, logs, events, buckets, and lookup files.

> ⚠️ The ingest token and MCP platform token are not interchangeable.

---

## 🔍 Verification Commands

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
    echo "✅ $variable is configured"
  else
    echo "❌ $variable is missing"
  fi
done
```

### Confirm local embeddings are available

```bash
python -c "from langchain_huggingface import HuggingFaceEmbeddings; print('Local embeddings available')"
```

### Confirm Traceloop is available

```bash
python -c "from traceloop.sdk import Traceloop; print('Traceloop available')"
```

### Validate the shell scripts

```bash
bash -n .devcontainer/setup.sh
bash -n .devcontainer/configure.sh
```

### Test the local application

With the application running:

```bash
curl -s http://localhost:8000/health
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

## 🆘 Common Issues

### The application cannot reach the LLM gateway

Check:

- `LLM_BASE_URL` ends with `/v1`
- `LLM_API_KEY` matches the instructor-provided key
- `LLM_CHAT_MODEL` is `workshop-chat`
- The request runs inside the Codespace
- The LiteLLM gateway is running

### LiteLLM returns `No connected db`

For this workshop setup, this commonly indicates that the supplied `LLM_API_KEY` does not match the gateway's configured `master_key`.

Copy the workshop key again, save `.env`, run `configure.sh`, and restart the application.

### No traces appear

Check:

- `DT_ENDPOINT` ends with `/api/v2/otlp`
- `DT_API_TOKEN` contains the required ingest permission
- Traceloop initialised successfully
- The application processed recent requests
- The selected Dynatrace timeframe includes those requests
- No repeated `401`, `403`, `404`, or exporter errors appear in the terminal

### Lookup queries return no records

Compare the observed model value with the lookup:

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.response.model)
| summarize request_count = count(), by: {gen_ai.response.model}
```

Then:

```dql
load "/lookups/ai/bedrock/model-costs"
```

The observed `gen_ai.response.model` value must match a value in the lookup's `model` field.

### No remote embedding span appears

This is expected. Embeddings run locally using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Look for the surrounding document-retrieval task and ChromaDB vector-search span instead.

### Dynatrace MCP does not appear in Copilot

Check:

1. `.vscode/mcp.json` exists and contains valid JSON.
2. The configuration references `${env:DT_MCP_BEARER_TOKEN}`.
3. `.devcontainer/configure.sh` completed successfully.
4. VS Code was reloaded.
5. Copilot Chat is using Agent mode.
6. Dynatrace MCP tools are enabled.

---

## 🎓 Further Learning

### Dynatrace

- [Dynatrace University](https://university.dynatrace.com/)
- [Dynatrace Community](https://community.dynatrace.com/)
- [Dynatrace Developer resources](https://developer.dynatrace.com/)
- [Dynatrace GitHub organisation](https://github.com/Dynatrace)

### AI observability

- [OpenLLMetry repository](https://github.com/traceloop/openllmetry)
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OpenTelemetry GenAI working group](https://github.com/open-telemetry/community/tree/main/projects/genai)

### Workshop repository

- [Open the workshop repository](https://github.com/marc-mas-ferrer/ai-mcp-ilt)
- [Launch the workshop Codespace](https://codespaces.new/marc-mas-ferrer/ai-mcp-ilt?quickstart=1)
- https://marc-mas-ferrer.github.io/ai-mcp-ilt/

---

## 🆘 Getting Help

### During the workshop

- Ask the instructor for assistance
- Use the workshop communication channel
- Include the visible error message, but never share token values

### After the workshop

- [Visit Dynatrace Community](https://community.dynatrace.com/)
- [Open Dynatrace Support](https://support.dynatrace.com/)
- [Browse Dynatrace documentation](https://docs.dynatrace.com/)

---

## 📝 Feedback

Please share feedback using the form or communication channel provided by your instructor.

Useful feedback includes:

- Which lab was most valuable
- Which instruction was unclear
- Which step took longer than expected
- Which troubleshooting guidance was missing
- Which additional AI observability use case should be included

---

<div class="lab-nav">
  <a href="lab4-automation">← Lab 4: Automation</a>
  <a href="./">Back to Home →</a>
</div>