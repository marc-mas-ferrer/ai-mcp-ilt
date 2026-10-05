---
title: Workshop App
topic: workshop
keywords: emb_, chroma_, simulated error, error code, lab 0, lab 1, lab 2, lab 3, lab 4
---

## The RAG chatbot

The workshop application is a FastAPI service that answers questions with Retrieval Augmented Generation (RAG). The chat endpoint is POST /chat. With Use Knowledge Base (RAG) enabled, the question goes through a pipeline; with it disabled, the question goes straight to the chat model with no retrieved context. Comparing the two is a good way to see what retrieval adds.

## Pipeline and spans

The pipeline is a single workflow, rag_chat_pipeline, with four tasks. analyze_query_intent makes a small LLM call that classifies the question. retrieve_documents vectorises the question and searches ChromaDB for the most relevant chunks. generate_context formats the retrieved chunks into a context string. generate_response makes the main LLM call with the context in the system prompt. After Lab 1 each step appears as a span in Dynatrace under the FastAPI request span.

## Local vectorisation

Retrieval vectors are produced by a local, deterministic hashing function, LocalHashingEmbeddings with 384 dimensions, rather than by a hosted embedding model. It makes no network calls, so there is no embedding span and no embedding token cost in traces. A production system would normally use a trained embedding model and that call would show up as its own span. The knowledge base is split into chunks, stored in an in-memory ChromaDB collection, and searched when a question arrives.

## Models and configuration

Chat completions go through LiteLLM, which routes the workshop-chat model to Amazon Nova Micro. Important settings are LLM_BASE_URL, LLM_API_KEY and LLM_CHAT_MODEL for the model, and DT_ENDPOINT (ending in /api/v2/otlp) and DT_API_TOKEN for Dynatrace. ATTENDEE_ID is used in the service name ai-chat-service-ATTENDEE_ID so each attendee can find their own traces.

## Workshop labs

Lab 0 sets up the environment in GitHub Codespaces. Lab 1 adds OpenLLMetry instrumentation to the app. Lab 2 explores traces and token economics in Dynatrace. Lab 3 uses the Dynatrace MCP server and error investigation from the IDE. Lab 4 builds Workflow automation, such as cost alerts and daily summaries.

## Simulated errors

The Simulate Errors toggle makes requests fail with realistic RAG and LLM errors, for practising investigation in Lab 3. The error codes are EMB_NULL_VECTOR (null vector from the embedder), CHROMA_COLLECTION_ERR (ChromaDB connection failure), LLM_MALFORMED_RESPONSE (invalid response from the LLM gateway), CTX_WINDOW_EXCEEDED (token limit exceeded), DOC_NO_MATCHES (no relevant documents found), RAG_CHAIN_TIMEOUT (pipeline timeout), CONTENT_FILTER_BLOCK (content policy violation) and EMB_DIMENSION_MISMATCH (vector dimension mismatch). Each is logged with its error.code attribute so it can be found with DQL.
