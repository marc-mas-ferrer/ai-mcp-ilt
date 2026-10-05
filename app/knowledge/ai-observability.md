---
title: AI Observability
topic: ai-observability
keywords: token cost, prompt caching, gen_ai
---

## Token usage and cost

In AI observability, token usage is recorded on LLM spans using the OpenTelemetry GenAI semantic conventions. The attributes gen_ai.usage.input_tokens and gen_ai.usage.output_tokens hold the token counts, and gen_ai.response.model records which model answered. Because models are billed per million tokens, those attributes are what cost and capacity analysis is built on. Cost is roughly input_tokens times the input price plus output_tokens times the output price, each divided by one million.

## What drives token cost in a RAG app

A large system prompt is sent on every request. Retrieved context adds input tokens for each chunk, so retrieving more or larger chunks raises cost without necessarily improving the answer. Every extra LLM call, such as an intent-classification step, adds its own tokens. Output length drives output tokens, which are usually priced higher than input tokens.

## Prompt caching

Providers can cache a repeated prompt prefix, charging less for the cached part. Caching generally needs a stable prefix of at least 1,024 tokens, which is why the app keeps a long, stable system prompt at the start of the prompt and puts the changing context after it.

## Debugging a poor RAG answer

Inspect the retrieved documents first, then the generated context, the final prompt and the completion, before changing the model. In a trace, check that the retrieve_documents task returned relevant chunks, that the context reached the prompt, and that the answer used it. Most poor RAG answers come from retrieval or prompt problems, not from the model.

## Signals worth monitoring

Token usage per model and per request, latency of LLM calls versus retrieval, error rate and error types, cache hit rate, and cost trends over time. These can be queried with DQL on spans and turned into dashboards or Workflow alerts.
