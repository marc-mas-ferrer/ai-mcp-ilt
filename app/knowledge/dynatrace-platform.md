---
title: Dynatrace Platform
topic: dynatrace
---

## What is Dynatrace

Dynatrace is an AI-powered, full-stack observability platform that provides automatic and intelligent monitoring for cloud-native and enterprise environments. It collects logs, traces, metrics, events and user-experience data in one place, and uses Dynatrace Intelligence to automatically detect anomalies, identify root causes and give precise answers about application performance issues. Dynatrace is used by developers, SREs and platform teams to keep applications, infrastructure and AI workloads healthy.

## Core capabilities

Full-stack observability gives end-to-end visibility from user experience down to infrastructure. Distributed tracing with PurePath shows complete transactions across microservices. Real User Monitoring (RUM) and Session Replay track real user sessions. Synthetic monitoring tests proactively from global locations. Log management and analytics ingest, search and correlate logs. Infrastructure monitoring covers hosts, containers, Kubernetes and cloud platforms. Application Security detects runtime vulnerabilities. Business analytics supports custom metrics, dashboards and business events.

## Dynatrace Intelligence

Dynatrace Intelligence is the AI engine of the platform (formerly known as Davis AI). It combines causal, predictive and generative AI. It automatically detects anomalies, groups related events into a single problem, performs root cause analysis using topology and dependency data, and powers forecasting and natural-language assistance. Because it uses real topology and causation rather than only statistical correlation, it reduces alert noise.

## OneAgent

Dynatrace OneAgent is a single agent that automatically discovers and monitors all processes, services and infrastructure in an environment. It needs no manual configuration and provides full-stack visibility from the application layer down to the infrastructure. OneAgent is the automatic way to get data in. Open standards such as OpenTelemetry are the other way, and the two can be used together.

## Smartscape

Smartscape is the real-time topology model of the environment. It maps hosts, processes, services, Kubernetes workloads and cloud resources and the relationships between them. Dynatrace Intelligence uses Smartscape to work out which entity caused a problem and who is affected.

## Grail data lakehouse

Grail is the Dynatrace data lakehouse. It stores logs, traces, metrics, events and business events together in one place, with no indexes and no schema defined up front, so data keeps its full context and can be queried as it was ingested. Grail is the storage layer that DQL queries read from, and it also holds lookup tables that queries can join against.

## Platform apps

The modern Dynatrace platform is organised as apps that all read from Grail. Notebooks are for exploratory analysis, Dashboards for monitoring, Workflows for automation (for example alerting on token cost or sending a daily summary), Distributed Tracing for trace exploration, Logs for log analysis, and AI Observability for LLM and agent workloads. Every app uses DQL against the same data.

## Dynatrace for AI observability

Dynatrace observes AI and LLM applications the same way it observes any other service. Instrumentation emits spans for workflows, retrieval and model calls, with prompts, completions, token usage, model names and latency as attributes. Teams use this to debug RAG pipelines, analyse token cost and caching, track errors and rate limits, and watch guardrails and evaluations. In this workshop the data arrives through OpenTelemetry and OpenLLMetry.

## Application Security

Dynatrace Application Security provides runtime vulnerability detection and protection. It automatically identifies vulnerabilities in running applications without requiring code changes or additional agents.
