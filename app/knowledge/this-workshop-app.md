---
title: Workshop App
topic: workshop
keywords: chatbot, rag pipeline, my traces, your traces, emb_, chroma_, simulated error, error code, lab 0, lab 1, lab 2, lab 3, lab 4
---

## The RAG chatbot

The workshop application is a FastAPI service that answers questions with Retrieval Augmented Generation (RAG). The chat endpoint is POST /chat. With Use Knowledge Base (RAG) enabled, the question goes through a pipeline; with it disabled, the question goes straight to the chat model with no retrieved context. Comparing the two is a good way to see what retrieval adds.

## Pipeline and spans

The pipeline is a single workflow, rag_chat_pipeline, with four tasks. analyze_query_intent makes a small LLM call that classifies the question. retrieve_documents vectorises the question and searches ChromaDB for the most relevant chunks. generate_context formats the retrieved chunks into a context string. generate_response makes the main LLM call with the retrieved context next to the question. After Lab 1 each step appears as a span in Dynatrace under the FastAPI request span.

## Local vectorisation

Retrieval vectors are produced by a local, deterministic hashing function, LocalHashingEmbeddings with 384 dimensions, rather than by a hosted embedding model. It makes no network calls, so there is no embedding span and no embedding token cost in traces. A production system would normally use a trained embedding model and that call would show up as its own span. The knowledge base is split into chunks, stored in an in-memory ChromaDB collection, and searched when a question arrives.

## Models and configuration

The chat models are Amazon Bedrock models reached through a LiteLLM gateway, which speaks the OpenAI chat-completions protocol. Each model has a LiteLLM alias: amazon-nova-micro (Amazon Nova Micro), amazon-nova-lite (Amazon Nova Lite, the default answer model) and amazon-nova-pro (Amazon Nova Pro, the most capable and most expensive). The analyze_query_intent task always uses amazon-nova-micro; generate_response uses the model chosen in the chat UI dropdown. The alias is what spans record in gen_ai.request.model and gen_ai.response.model. LLM spans are named ChatBedrockViaLiteLLM.chat and report gen_ai.system as AWS, because the app uses an OpenAI-compatible client class for Amazon Bedrock. Important settings are LLM_BASE_URL, LLM_API_KEY and LLM_CHAT_MODEL (the default answer model), optionally LLM_INTENT_MODEL and LLM_AVAILABLE_MODELS, and DT_ENDPOINT (ending in /api/v2/otlp) and DT_API_TOKEN for Dynatrace. ATTENDEE_ID is used in the service name ai-chat-service-ATTENDEE_ID so each attendee can find their own traces.

## Finding your traces in Dynatrace

Every attendee sends data to the same Dynatrace environment, so each app has its own service name, ai-chat-service-ATTENDEE_ID, taken from the ATTENDEE_ID value in the .env file. Filter on that name to see only your own traces, for example: fetch spans | filter service.name == "ai-chat-service-ATTENDEE_ID". Your traces appear only after Lab 1 adds the OpenLLMetry instrumentation. Before Lab 1 only logs and FastAPI HTTP spans arrive.

## Workshop labs

Lab 0 sets up the environment in GitHub Codespaces. Lab 1 adds OpenLLMetry instrumentation to the app. Lab 2 explores traces and token economics in Dynatrace. Lab 3 uses the Dynatrace MCP server and error investigation from the IDE. Lab 4 builds Workflow automation, such as cost alerts and daily summaries.

## Simulated errors

The Simulate Errors toggle makes requests fail with realistic RAG and LLM errors, for practising investigation in Lab 3. The error codes are EMB_NULL_VECTOR (null vector from the embedder), CHROMA_COLLECTION_ERR (ChromaDB connection failure), LLM_MALFORMED_RESPONSE (invalid response from the LLM gateway), CTX_WINDOW_EXCEEDED (token limit exceeded), DOC_NO_MATCHES (no relevant documents found), RAG_CHAIN_TIMEOUT (pipeline timeout), CONTENT_FILTER_BLOCK (content policy violation) and EMB_DIMENSION_MISMATCH (vector dimension mismatch). Each is logged with its error.code attribute so it can be found with DQL.
