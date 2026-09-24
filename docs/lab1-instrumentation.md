---
layout: default
title: Lab 1 - AI Instrumentation
nav_order: 3
---

# Lab 1: Instrumenting an AI Application with OpenLLMetry

**Duration:** ~15 minutes

In this lab, you will add OpenLLMetry instrumentation to the sample RAG application and send its AI traces to Dynatrace.

The application already sends logs to Dynatrace and already creates spans for incoming HTTP requests. Both are configured in the repository. What is missing is the AI telemetry: prompts, completions, token usage, and the structure of the RAG pipeline. That is what you add here.

## Learning Objectives

By the end of this lab, you will be able to:

- Explain how OpenLLMetry extends OpenTelemetry for AI applications
- Add Traceloop instrumentation to a Python application
- Configure OTLP trace export to Dynatrace
- Generate traces from RAG and direct LLM requests
- Verify that the application is exporting telemetry successfully

## Step 1: Enable the OpenLLMetry Dependency

### 1.1 Edit requirements.txt

In the VS Code Explorer, open `app/requirements.txt` and find this section:

```text
# OpenLLMetry instrumentation
# Attendees uncomment this dependency during Lab 1
# traceloop-sdk==0.50.1
```

Remove the `#` from the `traceloop-sdk` line only:

```text
traceloop-sdk==0.50.1
```

Save the file.

> **Leave the other packages alone.** The OpenTelemetry packages above this section are already enabled, because they power the log export and HTTP spans that are running today. Do not comment them out, change their versions, or add extra OpenTelemetry packages. Use the version already written in the file.

### 1.2 Install the dependencies

From the repository root, run:

```bash
pip install -r app/requirements.txt
```

This installs Traceloop while keeping the rest of the application dependencies consistent.

### 1.3 Verify the installation

Run:

```bash
python -c "from traceloop.sdk import Traceloop; print('Traceloop is installed')"
```

Expected result:

```text
Traceloop is installed
```

## Step 2: Add Dynatrace Instrumentation

### 2.1 Open the application

Open `app/main.py`.

### 2.2 Find the instrumentation marker

Near the top of the file, find:

```python
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  LAB 1: INSTRUMENTATION SECTION                                          ║
# ║                                                                          ║
# ║  TODO: Add Dynatrace OpenLLMetry instrumentation here                    ║
# ║  Follow the instructions in the workshop guide to add the                ║
# ║  Traceloop initialization code below this comment block.                 ║
# ║                                                                          ║
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
    print("Traceloop initialised")
    print(f"   Service: ai-chat-service-{ATTENDEE_ID}")
    print(f"   Endpoint: {DT_ENDPOINT}")
else:
    print("Dynatrace configuration not found")
    print("   Check DT_ENDPOINT and DT_API_TOKEN in .env")
```

Save `app/main.py`.

> **Position matters.** Add this code where the marker was, which is after `load_dotenv()` has run. Do not move it to the very top of the file, or the environment configuration will not be loaded yet.

## Step 3: Understand What You Added

Three things in that code are worth understanding before you continue.

**The service name makes your telemetry findable.** `ATTENDEE_ID` comes from the `.env` file you configured in Lab 0, and it is used to build the service name:

```text
ai-chat-service-{YOUR_ATTENDEE_ID}
```

Every attendee sends data to the same Dynatrace environment, so this is how you filter for your own traces in Lab 2.

**The authentication header uses `Api-Token`, not `Bearer`.** Dynatrace OTLP ingestion expects:

```text
Authorization: Api-Token dt0c01...
```

Do not change this to `Bearer`. The MCP platform token you will use in Lab 3 is a different credential with a different scheme, and swapping them is a common cause of a 401.

**Metric temporality is set before initialisation.** The `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` line configures how exported metrics are reported, and it has to be set before `Traceloop.init()` runs.

## Step 4: Start the Instrumented Application

### 4.1 Check the Python syntax

Before starting the application, run:

```bash
python -m py_compile app/main.py
```

No output means that the Python syntax is valid.

### 4.2 Start the application

```bash
python app/main.py
```

### 4.3 Check the startup output

The new line to look for is:

```text
Traceloop initialised
   Service: ai-chat-service-{YOUR_ATTENDEE_ID}
   Endpoint: https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
```

You should also still see the lines that were there in Lab 0, including the logging and FastAPI instrumentation messages, `RAG initialized successfully` and `Uvicorn running on http://0.0.0.0:8000`.

Do not continue if the application reports:

```text
Dynatrace configuration not found
```

That message means `DT_ENDPOINT` or `DT_API_TOKEN` is missing from `.env`.

## Step 5: Generate Trace Data

### 5.1 Open the chat interface

The Codespace forwards port 8000 and opens the chat interface automatically. If the tab is no longer open, use the **Ports** tab and select the globe icon for port 8000.

### 5.2 Generate RAG traces

Make sure **Use Knowledge Base (RAG)** is enabled, and send at least three questions:

```text
What is Dynatrace?
How does OpenTelemetry work with Dynatrace?
What is the Dynatrace MCP?
```

### 5.3 Generate a direct LLM trace

Disable **Use Knowledge Base (RAG)** and send:

```text
Explain observability in one sentence.
```

### 5.4 Compare the two modes

| RAG enabled | RAG disabled |
|---|---|
| Classifies the question first | Sends the question directly |
| Vectorises the query locally | No retrieval step |
| Searches ChromaDB | No vector search |
| Adds retrieved context to the prompt | No retrieved context |
| Makes two model calls | Makes one model call |
| Returns knowledge-base sources | Returns no sources |

Generating both kinds of traffic now will make the differences easier to identify in Lab 2.

> **You will not see an embedding-model span.** Retrieval vectors are generated in-process by a local hashing function, so there is no call to a hosted embedding service and no embedding token cost. You will still see the `retrieve_documents` task and the ChromaDB query around it.

> **Tip:** Automatic span names and attributes can vary between instrumentation versions. In Lab 2, identify spans by their position and purpose rather than by one exact name.

## Step 6: Check for Export Errors

Review the terminal after generating the requests.

The application does not print a success message for every exported batch, so the useful check is the absence of repeated errors. Look for messages containing `401`, `403`, `404`, `OTLP` or `export`.

If no export errors appear, continue to the checkpoint.

## Checkpoint

Before proceeding to Lab 2, verify that:

- `traceloop-sdk==0.50.1` is enabled in `app/requirements.txt`, and the OpenTelemetry packages were left untouched
- `pip install -r app/requirements.txt` completed successfully
- The instrumentation code is in `app/main.py` and `python -m py_compile app/main.py` reports no errors
- The application prints `Traceloop initialised` with your attendee ID in the service name
- You generated at least three RAG requests and one request with RAG disabled
- No repeated OTLP export errors appear in the terminal

## Troubleshooting

### ModuleNotFoundError: No module named 'traceloop'

Confirm that the package is enabled in `app/requirements.txt`:

```text
traceloop-sdk==0.50.1
```

Then run `pip install -r app/requirements.txt` and verify with:

```bash
python -c "from traceloop.sdk import Traceloop; print('Traceloop is installed')"
```

### Dependency conflicts after installing

If pip reports conflicting OpenTelemetry versions, the pinned packages in `requirements.txt` were probably edited or duplicated. Restore the file so that only the `traceloop-sdk` line was uncommented, then reinstall.

### Dynatrace configuration not found

Open `.env` and confirm that both fields contain values:

```text
DT_ENDPOINT=https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01....
```

Then stop and restart the application.

### 401 Unauthorized

Check:

- The value of `DT_API_TOKEN`
- That no spaces or quotation marks surround the token
- That the header uses `Api-Token`, not `Bearer`

Do not print or share the complete token in the workshop chat.

### 403 Forbidden

The token may be valid but missing the required ingestion permission. Ask the instructor to verify the token scopes.

### 404 Not Found

Confirm that `DT_ENDPOINT` ends with `/api/v2/otlp`. Do not add `/v1/traces` manually, because the exporter builds the signal-specific path itself.

### The application crashes after adding the code

Run `python -m py_compile app/main.py` and check that:

- The instrumentation code was inserted where the marker was, after `load_dotenv()`
- Every opening parenthesis has a closing parenthesis
- The `if` and `else` blocks use consistent indentation
- The original application code was not deleted

### The application works but no traces appear

- Generate several new chat requests.
- Confirm that Traceloop initialised successfully.
- Check the terminal for exporter errors.
- Confirm that the service name contains the correct attendee ID.
- Expand the time range in Dynatrace and refresh.

### RAG works but no embedding-model span appears

This is expected. The workshop generates retrieval vectors locally, using a deterministic hashing function rather than a trained embedding model, so nothing is sent to a hosted embedding endpoint.

Look instead for the `retrieve_documents` task, the ChromaDB query span, and the two chat-model calls.

### More traces appear than expected

FastAPI instrumentation, LangChain instrumentation and the Traceloop decorators can each create spans at different levels. In Lab 2, use the parent-child structure to distinguish HTTP spans, workflow spans, task spans, vector-store spans and LLM spans.

## Excellent Work

You have instrumented the application and generated both RAG and direct LLM traces.

In Lab 2, you will examine the trace hierarchy, inspect model calls, analyse token usage, and estimate model cost.
