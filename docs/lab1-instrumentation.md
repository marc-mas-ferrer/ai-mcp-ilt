---
layout: default
title: Lab 1 - AI Instrumentation
nav_order: 3
---

# 🔬 Lab 1: Instrumenting an AI Application with OpenLLMetry

**Duration:** ~15 minutes

In this lab, you will add OpenLLMetry instrumentation to the sample RAG application and send its traces to Dynatrace.

The application already works. Your task is to make its AI workflow observable.

---

## 🎯 Learning Objectives

By the end of this lab, you will be able to:

- Explain how OpenLLMetry extends OpenTelemetry for AI applications
- Add Traceloop instrumentation to a Python application
- Configure OTLP trace export to Dynatrace
- Generate traces from RAG and direct LLM requests
- Verify that the application is exporting telemetry successfully

---

## Step 1: Enable the OpenLLMetry Dependencies

The application dependencies already include the packages required to run the web application. The OpenLLMetry dependencies are commented out so that you can enable them during this lab.

### 1.1 Open `requirements.txt`

In the VS Code Explorer, open:

```text
app/requirements.txt
```

Find these commented lines:

```text
# traceloop-sdk==0.50.0
# opentelemetry-exporter-otlp==1.39.0
```

Remove the `#` characters:

```text
traceloop-sdk==0.50.0
opentelemetry-exporter-otlp==1.39.0
```

Save the file.

> ⚠️ Use the versions already specified in `requirements.txt`. Do not replace them with different versions during the workshop.

### 1.2 Install the dependencies

From the repository root, run:

```bash
pip install -r app/requirements.txt
```

This installs the newly enabled packages while keeping the rest of the application dependencies consistent.

### 1.3 Verify the installation

Run:

```bash
python -c "from traceloop.sdk import Traceloop; print('Traceloop is installed')"
```

Expected result:

```text
Traceloop is installed
```

---

## Step 2: Add Dynatrace Instrumentation

### 2.1 Open the application

Open:

```text
app/main.py
```

### 2.2 Find the instrumentation marker

Near the top of the file, find:

```python
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                      ║
# ║                                                                         ║
# ║  TODO: Add Dynatrace OpenLLMetry instrumentation here                   ║
# ║  Follow the instructions in the workshop guide to add the               ║
# ║  Traceloop initialization code below this comment block.                ║
# ║                                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# --> ADD YOUR INSTRUMENTATION CODE HERE <--
```

### 2.3 Replace the marker

Replace only this line:

```python
# --> ADD YOUR INSTRUMENTATION CODE HERE <--
```

with:

```python
from traceloop.sdk import Traceloop

# Read the Dynatrace configuration loaded from .env
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
DT_ENDPOINT = os.getenv("DT_ENDPOINT")
DT_API_TOKEN = os.getenv("DT_API_TOKEN")

# Use Delta temporality for exported OpenTelemetry metrics
os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"

# Initialise OpenLLMetry only when the required Dynatrace values are present
if DT_ENDPOINT and DT_API_TOKEN:
    headers = {
        "Authorization": f"Api-Token {DT_API_TOKEN}"
    }

    Traceloop.init(
        app_name=f"ai-chat-service-{ATTENDEE_ID}",
        api_endpoint=DT_ENDPOINT,
        headers=headers
    )

    print("✅ Traceloop initialised")
    print(f"   Service: ai-chat-service-{ATTENDEE_ID}")
    print(f"   Endpoint: {DT_ENDPOINT}")
else:
    print("⚠️ Dynatrace configuration not found")
    print("   Check DT_ENDPOINT and DT_API_TOKEN in .env")
```

Save `app/main.py`.

> ⚠️ Add this code directly below the instrumentation marker, after `load_dotenv()` has run. Do not add it at the very beginning of the file before the environment configuration is loaded.

---

## Step 3: Understand the Instrumentation

### 3.1 Import Traceloop

```python
from traceloop.sdk import Traceloop
```

Traceloop provides the OpenLLMetry instrumentation used by the workshop.

It adds AI-specific telemetry to the OpenTelemetry traces produced by the application.

### 3.2 Read the attendee and Dynatrace configuration

```python
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
DT_ENDPOINT = os.getenv("DT_ENDPOINT")
DT_API_TOKEN = os.getenv("DT_API_TOKEN")
```

These values come from the `.env` file configured in Lab 0.

`ATTENDEE_ID` is used to give every attendee a unique service name:

```text
ai-chat-service-{YOUR_ATTENDEE_ID}
```

This allows multiple attendees to send data to the same Dynatrace environment while filtering their own telemetry.

### 3.3 Set metric temporality

```python
os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"
```

This configures the preferred temporality for OpenTelemetry metrics exported by the instrumentation.

It must be set before calling `Traceloop.init()`.

### 3.4 Create the authentication header

```python
headers = {
    "Authorization": f"Api-Token {DT_API_TOKEN}"
}
```

The workshop uses a Dynatrace API token to authenticate OTLP ingestion.

The header format must be:

```text
Authorization: Api-Token dt0c01...
```

Do not replace `Api-Token` with `Bearer`. The MCP platform token used in Lab 3 is a separate credential with a different purpose.

### 3.5 Initialise Traceloop

```python
Traceloop.init(
    app_name=f"ai-chat-service-{ATTENDEE_ID}",
    api_endpoint=DT_ENDPOINT,
    headers=headers
)
```

| Parameter | Purpose |
|---|---|
| `app_name` | Defines the service name recorded in Dynatrace |
| `api_endpoint` | Specifies the Dynatrace OTLP endpoint |
| `headers` | Provides the API-token authentication header |

The endpoint configured in `.env` must end with:

```text
/api/v2/otlp
```

### 3.6 Understand what is instrumented

The application uses:

- FastAPI for the HTTP service
- LangChain to call the chat model
- LiteLLM as the OpenAI-compatible gateway
- Amazon Nova Micro as the language model
- A local sentence-transformers model for embeddings
- ChromaDB for vector retrieval
- Traceloop workflow and task decorators for the RAG pipeline

The local embedding model does not make a remote API request. Therefore, it does not create a hosted embedding-model span with token usage.

---

## Step 4: Check the Updated File

The beginning of `app/main.py` should now follow this structure:

```python
"""
Dynatrace AI Observability Workshop
"""

import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the repository .env file
env_path = Path(__file__).parent.parent / ".env"

if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

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

    print("✅ Traceloop initialised")
    print(f"   Service: ai-chat-service-{ATTENDEE_ID}")
    print(f"   Endpoint: {DT_ENDPOINT}")
else:
    print("⚠️ Dynatrace configuration not found")
    print("   Check DT_ENDPOINT and DT_API_TOKEN in .env")

# The existing application code continues below
```

You do not need to copy this complete example if you already added the code in Step 2. Use it to compare the structure of your file.

---

## Step 5: Start the Instrumented Application

### 5.1 Check the Python syntax

Before starting the application, run:

```bash
python -m py_compile app/main.py
```

No output means that the Python syntax is valid.

### 5.2 Start the application

Run:

```bash
python app/main.py
```

### 5.3 Check the startup output

Expected output includes:

```text
✅ Traceloop initialised
   Service: ai-chat-service-{YOUR_ATTENDEE_ID}
   Endpoint: https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
```

You should also see:

```text
✅ RAG initialized successfully for attendee: {YOUR_ATTENDEE_ID}
INFO: Uvicorn running on http://0.0.0.0:8000
```

Do not continue if the application reports:

```text
⚠️ Dynatrace configuration not found
```

That message means `DT_ENDPOINT` or `DT_API_TOKEN` is missing.

---

## Step 6: Generate Trace Data

### 6.1 Open the chat interface

When VS Code detects port `8000`:

1. Select **Open in Browser**.
2. If the notification is no longer visible, open the **Ports** tab.
3. Find port `8000`.
4. Select the globe icon.

### 6.2 Generate RAG traces

Make sure **Use Knowledge Base (RAG)** is enabled.

Send at least three questions:

```text
What is Dynatrace?
```

```text
How does OpenTelemetry work with Dynatrace?
```

```text
What is the Dynatrace MCP?
```

Each RAG request performs:

1. An intent-classification LLM call
2. Local embedding generation
3. ChromaDB document retrieval
4. Context generation
5. A final LLM call using the retrieved context

### 6.3 Generate a direct LLM trace

Disable **Use Knowledge Base (RAG)**.

Send:

```text
Explain observability in one sentence.
```

This creates a simpler request that calls the language model without retrieving knowledge-base context.

### 6.4 Compare the two modes

| RAG enabled | RAG disabled |
|---|---|
| Classifies the question | Sends the question directly |
| Generates an embedding locally | No retrieval embedding |
| Searches ChromaDB | No vector search |
| Adds retrieved context | No retrieved context |
| Makes two LLM calls | Makes one LLM call |
| Returns knowledge-base sources | Returns no knowledge-base sources |

Generating both types of traffic will make the differences easier to identify in Lab 2.

---

## Step 7: Understand What Gets Traced

### RAG request

A RAG request should contain telemetry for:

- **HTTP request:** The incoming FastAPI `/chat` request
- **RAG workflow:** The complete `rag_chat_pipeline` operation
- **Intent analysis:** The short LLM classification call
- **Document retrieval:** The `retrieve_documents` task
- **Vector search:** The ChromaDB query
- **Context generation:** Formatting the retrieved documents
- **Response generation:** The final LLM call through LiteLLM and Amazon Bedrock
- **Token usage:** Input and output token attributes on the LLM calls

### Direct request

A request with RAG disabled should contain:

- **HTTP request:** The incoming FastAPI `/chat` request
- **LLM completion:** A direct model call through LiteLLM and Amazon Bedrock
- **Token usage:** Input and output token attributes when captured by the instrumentation

### Local embedding generation

The embedding model runs locally inside the Codespace.

You should not expect:

- A remote embedding API call
- Bedrock embedding-token costs
- A remote `openai.embeddings` span

You can still observe the surrounding `retrieve_documents.task` and the ChromaDB vector-search operation.

> 💡 Exact automatic span names and available attributes can vary between instrumentation versions. In Lab 2, identify spans by their position and purpose rather than relying only on one exact span name.

---

## Step 8: Check for Export Errors

Review the terminal after generating the requests.

The application may not print a success message for every exported batch. The important check is that no repeated exporter errors appear.

Look for messages containing:

```text
401
403
404
OTLP
export
```

If no export errors appear, continue to the checkpoint.

---

## ✅ Checkpoint

Before proceeding to Lab 2, verify that:

- [ ] `traceloop-sdk==0.50.0` is enabled in `requirements.txt`
- [ ] `opentelemetry-exporter-otlp==1.39.0` is enabled in `requirements.txt`
- [ ] `pip install -r app/requirements.txt` completes successfully
- [ ] The instrumentation code is present in `app/main.py`
- [ ] `python -m py_compile app/main.py` produces no errors
- [ ] The application prints `✅ Traceloop initialised`
- [ ] The service name contains your attendee ID
- [ ] You generated at least three RAG requests
- [ ] You generated at least one request with RAG disabled
- [ ] No repeated OTLP export errors appear in the terminal

---

## 🆘 Troubleshooting

### `ModuleNotFoundError: No module named 'traceloop'`

Confirm that the package is enabled in `app/requirements.txt`:

```text
traceloop-sdk==0.50.0
```

Then run:

```bash
pip install -r app/requirements.txt
```

Verify:

```bash
python -c "from traceloop.sdk import Traceloop; print('Traceloop is installed')"
```

### `Dynatrace configuration not found`

Open `.env` and confirm that both fields contain values:

```bash
DT_ENDPOINT=https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.INSTRUCTOR_PROVIDED_VALUE
```

Then stop and restart the application.

### `401 Unauthorized`

Check:

1. The value of `DT_API_TOKEN`
2. That the token has the `openTelemetryTrace.ingest` permission
3. That no spaces or quotation marks surround the token
4. That the header uses `Api-Token`, not `Bearer`

Do not print or share the complete token in the workshop chat.

### `403 Forbidden`

The token may be valid but missing the required ingestion permission.

Ask the instructor to verify that the token includes:

```text
openTelemetryTrace.ingest
```

### `404 Not Found`

Confirm that `DT_ENDPOINT` ends with:

```text
/api/v2/otlp
```

Do not add `/v1/traces` manually. The exporter constructs the signal-specific endpoint.

### The application crashes after adding the code

Run:

```bash
python -m py_compile app/main.py
```

Check that:

- The instrumentation code was inserted after `load_dotenv()`
- Every opening parenthesis has a closing parenthesis
- The `if` and `else` blocks use consistent indentation
- The original application code was not deleted

### The application works but no traces appear

1. Generate several new chat requests.
2. Confirm that Traceloop initialised successfully.
3. Check the terminal for exporter errors.
4. Confirm that the service name contains the correct attendee ID.
5. Expand the time range in Dynatrace.
6. Wait briefly and refresh the Dynatrace view.

### RAG works but no embedding-model span appears

This is expected.

The workshop uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embedding model runs locally and does not call a hosted embedding endpoint.

Look for:

- `retrieve_documents.task`
- The ChromaDB query span
- The two remote chat-model calls

### More traces appear than expected

FastAPI instrumentation, LangChain instrumentation, Traceloop decorators, and model instrumentation can each create spans at different levels.

In Lab 2, use the parent-child structure to distinguish:

- HTTP spans
- Workflow spans
- Task spans
- Vector-store spans
- LLM spans

---

## 🎉 Excellent Work!

You have instrumented the application and generated both RAG and direct LLM traces.

In Lab 2, you will examine the trace hierarchy, inspect model calls, analyse token usage, and estimate model cost.

<div class="lab-nav">
  <a href="lab0-setup">← Lab 0: Setup</a>
  <a href="lab2-explore-traces">Lab 2: Explore Traces →</a>
</div>