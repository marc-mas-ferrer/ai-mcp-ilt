---
title: OpenTelemetry
topic: opentelemetry
keywords: opentelemetry, otel, otlp
---

## What is OpenTelemetry

OpenTelemetry (OTel) is an open-source, vendor-neutral observability framework hosted by the CNCF. It provides APIs, SDKs, semantic conventions and tools for generating and collecting telemetry data: traces, metrics and logs. Instrument once with OpenTelemetry and send the data to any compatible backend, including Dynatrace, without being locked in to a vendor agent.

## How OpenTelemetry works

Application code, or an instrumentation library, calls the OpenTelemetry API to create spans, record metrics and emit logs. The SDK, configured once at startup, receives that data, adds resource attributes such as service.name, applies sampling and batches it. An exporter then sends the batches over OTLP to a backend, either directly or through an OpenTelemetry Collector. The backend, for example Dynatrace, stores the data and lets you query it. Because the API and the wire format are standard, you can change the backend without changing the instrumentation.

## Signals

Traces describe the path of a request as a tree of spans. Each span has a name, start time, duration, status and attributes. Metrics are numeric measurements over time, such as request counts or token usage. Logs are timestamped records; when emitted inside a span they carry the trace and span IDs so they can be correlated with the trace.

## Building blocks

The API is what application code calls to create spans and metrics. The SDK implements the API and handles sampling, processing and exporting. Instrumentation libraries add spans automatically for common frameworks (FastAPI, requests, database drivers). Exporters send data out, most commonly over OTLP. The Collector is an optional standalone service that receives, processes and forwards telemetry. Resource attributes such as service.name describe the entity that produced the data.

## OTLP

OTLP, the OpenTelemetry Protocol, is the standard wire format for sending telemetry, over HTTP (protobuf) or gRPC. Dynatrace ingests traces, metrics and logs natively over OTLP.

## Context propagation

OpenTelemetry propagates trace context between services using the W3C Trace Context headers (traceparent and tracestate), and Baggage for extra key-value context. This is how a single trace can span several services, and how Dynatrace stitches OpenTelemetry spans together with other data.

## Semantic conventions

Semantic conventions define standard attribute names so data means the same thing everywhere, for example http.request.method, db.system and service.name. For AI workloads there are GenAI semantic conventions (gen_ai.*) covering the model, token usage and operation type.

## Sending OpenTelemetry data to Dynatrace

Dynatrace accepts OTLP at the endpoint DT_ENDPOINT, which must end with /api/v2/otlp (for example https://YOUR_ENV.live.dynatrace.com/api/v2/otlp). Omitting the /api/v2/otlp suffix is the most common configuration mistake and causes 404 errors. Exporters append the signal path themselves: /v1/traces, /v1/metrics and /v1/logs. Use the http/protobuf protocol.

Authenticate with an access token in the header Authorization: Api-Token dt0c01... (the scheme is Api-Token, not Bearer). The token needs the scopes openTelemetryTrace.ingest for traces, metrics.ingest for metrics and logs.ingest for logs. Dynatrace requires metrics with delta temporality, so set OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=delta.

You can send directly from the SDK to Dynatrace, or route through an OpenTelemetry Collector.

## Python example: send traces to Dynatrace

This sends spans directly from the Python SDK to Dynatrace over OTLP/HTTP. It uses the same endpoint and header pattern as the log exporter in this workshop app.

import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

DT_ENDPOINT = os.getenv("DT_ENDPOINT")  # ends with /api/v2/otlp
DT_API_TOKEN = os.getenv("DT_API_TOKEN")

provider = TracerProvider(resource=Resource.create({"service.name": "my-service"}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=f"{DT_ENDPOINT}/v1/traces",
    headers={"Authorization": f"Api-Token {DT_API_TOKEN}"},
)))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("handle_request") as span:
    span.set_attribute("user.id", "42")

The packages are opentelemetry-sdk and opentelemetry-exporter-otlp-proto-http. The token needs the openTelemetryTrace.ingest scope. For logs, use OTLPLogExporter with the /v1/logs path and the logs.ingest scope; for metrics use the /v1/metrics path, the metrics.ingest scope and delta temporality.

## OpenTelemetry in this workshop app

The app already exports logs with the OTLP log exporter and creates HTTP spans with the FastAPI instrumentation, so some data reaches Dynatrace before Lab 1. In Lab 1 you add OpenLLMetry, which builds on OpenTelemetry to add the AI-specific spans: the RAG workflow, retrieval and LLM calls.
