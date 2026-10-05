---
title: OpenLLMetry
topic: openllmetry
---

## What is OpenLLMetry

OpenLLMetry is an open-source project, created by Traceloop, that is built on OpenTelemetry for monitoring LLM applications. It provides automatic instrumentation for popular AI frameworks and providers such as OpenAI, LangChain and vector databases like ChromaDB, capturing prompts, completions, token usage and latency as spans. This makes AI workloads observable in the same way as any other service, and because it emits standard OpenTelemetry data, it works with Dynatrace without a proprietary agent. The Python package is traceloop-sdk.

## What it captures

Instrumentors patch the supported libraries, so there is little or no change to application code. For each LLM call you get a span with the model, the prompt and completion (when content tracing is enabled), input and output token counts, and latency. Vector database calls such as ChromaDB queries get their own spans. Errors and rate limits are recorded on the span. Attributes follow the OpenTelemetry GenAI semantic conventions, for example gen_ai.usage.input_tokens, gen_ai.usage.output_tokens and gen_ai.response.model, plus traceloop.* attributes for workflow and task names.

## Traceloop.init

Instrumentation is switched on by calling Traceloop.init() once at startup, after the environment is loaded. The key arguments are app_name (becomes the service name), api_endpoint (the OTLP endpoint, which for Dynatrace is DT_ENDPOINT ending in /api/v2/otlp) and headers (for Dynatrace, Authorization: Api-Token followed by the token).

Example used in Lab 1:

from traceloop.sdk import Traceloop
Traceloop.init(
    app_name=f"ai-chat-service-{ATTENDEE_ID}",
    api_endpoint=DT_ENDPOINT,
    headers={"Authorization": f"Api-Token {DT_API_TOKEN}"}
)

Set OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE to delta before calling init, because Dynatrace needs delta metrics. Install the package by uncommenting traceloop-sdk in requirements.txt.

## Workflow and task decorators

The @workflow and @task decorators group calls into a meaningful trace hierarchy. A workflow is the top-level unit of work and tasks are the steps inside it. In this app the workflow rag_chat_pipeline contains the tasks analyze_query_intent, retrieve_documents, generate_context and generate_response. Without decorators the LLM calls still appear, but as separate unrelated spans.

Example:

from traceloop.sdk.decorators import workflow, task

@workflow(name="rag_chat_pipeline")
def process_rag_chat(message): ...

@task(name="retrieve_documents")
def retrieve_documents(query): ...

## Association properties

Traceloop.set_association_properties() attaches business context, such as a user ID, session ID, conversation ID or the user's question, to every span in the current trace. In Dynatrace these become attributes you can filter and group by in DQL.

## Content tracing

By default OpenLLMetry records prompts and completions on spans, which is what makes debugging possible. Because these can contain sensitive data, content tracing can be turned off with the TRACELOOP_TRACE_CONTENT environment variable set to false. Token counts and latency are still recorded.

## Common mistakes

DT_ENDPOINT missing the /api/v2/otlp suffix. Using Bearer instead of Api-Token in the header. Placing Traceloop.init before load_dotenv, so the environment values are empty. Forgetting to restart the app after editing, because auto-reload is disabled to avoid duplicate OpenTelemetry initialisation. Using wrapt 2.x, which breaks the LangChain instrumentor, so keep wrapt below 2.
