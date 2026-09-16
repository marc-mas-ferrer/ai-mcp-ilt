---
layout: default
title: Lab 3 - Dynatrace MCP
nav_order: 5
---

# 🤖 Lab 3: Using Dynatrace MCP for Agentic AI

**Duration:** ~30 minutes

In this lab, you'll configure and use the Dynatrace MCP (Model Context Protocol) server to interact with Dynatrace directly from your IDE using AI assistants like GitHub Copilot.

---

## 🎯 Learning Objectives

- Understand what MCP is and how it enables agentic AI
- Install and configure the Dynatrace MCP server
- Use natural language to query Dynatrace from VS Code
- Analyze problems and traces using AI assistance
- Explore real-world use cases for observability-driven AI

---

## What is MCP?

**Model Context Protocol (MCP)** is an open standard that allows AI assistants to interact with external tools and data sources. With Dynatrace MCP, you can:

- Query Dynatrace using natural language
- Analyze problems and incidents
- Retrieve metrics, traces, and logs
- Get AI-powered insights about your applications

Think of it as giving your AI assistant **direct access to Dynatrace**!

<div class="why-dynatrace" markdown="1">

## 🏆 Why Dynatrace MCP is Different

Other tools let you *see* traces. Dynatrace MCP lets you:

| Capability | Basic AI Assistants | Dynatrace MCP |
|------------|---------------------|---------------|
| Query observability data | ❌ No access | ✅ Natural language queries |
| Correlate AI + infrastructure | ❌ Separate tools | ✅ Unified view via Davis AI |
| Root cause analysis | ❌ You investigate | ✅ Davis AI explains issues |
| Take action | ❌ Copy/paste to other tools | ✅ Trigger workflows from IDE |
| Business context | ❌ Technical data only | ✅ Link tokens to user impact |

**The difference:** Ask "Why is my AI service slow?" and get answers that connect LLM latency to Azure region issues to user experience — all in one response.

</div>

---

## Step 1: Configure the Dynatrace MCP Server

The Dynatrace MCP server is already pre-configured in this workshop! The authentication token was automatically configured when you ran the setup script in Lab 0.

---

## Step 2: Verify MCP Connection

### 2.1 Open GitHub Copilot Chat

1. Click on the Copilot icon on the top bar
2. Or use keyboard shortcut: `Cmd+Shift+I` (Mac) / `Ctrl+Shift+I` (Windows)

### 2.2 Test the Connection

In the Copilot chat, type:

```
@dynatrace What services are available in my environment?
```

If configured correctly, Copilot will query Dynatrace and return a list of services!

---

# 🎭 New! Dynatrace Intelligence ✨

Dynatrace Intelligence provides agentic workflows that go beyond simple queries. These exercises showcase the latest capabilities for each persona. What this means is that with Dynatrace's MCP server, your personal AI agent (GitHub CoPilot for this lab) can actually interact with various agents provided by Dynatrace! When running the below queries, notice how your AI agent will interact with various agents from Dynatrace (e.g. Grail Query Agent, Data Analysis Agent, Root Cause Agent, etc.).

Learn more here:
* [Dynatrace Intelligence - Announcement](https://www.dynatrace.com/news/blog/dynatrace-intelligence-at-the-core-of-autonomous-operations/)
* [Dynatrace Intelligence - Documentation](https://docs.dynatrace.com/docs/shortlink/dynatrace-intelligence-landing)

---

## 🎭 Your Mission (Choose Your Persona)

From this point forward, you'll focus on different use cases depending on your role.

<div class="persona-box developer" markdown="1">

### 💻 Developer: "I want to debug without leaving my IDE"

**Your story:** You're deep in code, fixing a bug in your RAG pipeline. Every time you need performance data, you have to context-switch to Dynatrace. What if you could just *ask*?

**Your goal:** Set up MCP so you can query Dynatrace directly from VS Code. Debug while you code!

**Focus on:** Steps 3 and 4 (marked with 💻)

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE/Platform: "I need faster incident response"

**Your story:** It's 2 AM and you get paged. Instead of fumbling through dashboards half-asleep, what if you could just ask about the issue?

**Your goal:** Learn to use MCP for rapid incident triage. Get answers in seconds, not minutes.

**Focus on:** Steps 5 and 6 (marked with 🔧)

</div>

---

<div class="persona-box developer" markdown="1">

## 💻 Step 3: Query Your AI Service (Developer)

Use MCP to analyze your instrumented AI service while coding.

### 3.1 Find Your Service

```
@dynatrace Tell me about the service called ai-chat-service-{YOUR_ATTENDEE_ID}
```

### 3.2 Analyze Token Usage

```
@dynatrace What is the total input and output token usage for spans in regards to the ai-chat-service-{YOUR_ATTENDEE_ID}
```

### 3.3 Debug While You Code

Use MCP alongside your code to understand your application's behavior:

```
I'm looking at main.py where I call Azure OpenAI.
@dynatrace What's the average latency for Azure OpenAI calls from my ai-chat-service-{YOUR_ATTENDEE_ID} service?
```

No context switching — debug while you code!

---

## 💻 Step 4: Agentic Debugging Workflows (Developer)

MCP enables powerful agentic workflows where AI assistants can take action based on observability data.

### 4.1 Find the Bottleneck

```
I'm seeing slow responses in my RAG pipeline. 
@dynatrace Analyze the trace data and tell me which step is the bottleneck for my ai-chat-service-{YOUR_ATTENDEE_ID} service.
Is it embeddings, vector search, or the LLM call?
```

### 4.2 Proactive Analysis

```
@dynatrace Analyze my ai-chat-service-{YOUR_ATTENDEE_ID} service and suggest optimizations to reduce token usage while maintaining response quality
```

### 4.3 Debugging Assistance

```
@dynatrace Help me understand why some of my RAG queries might be slow. Look at the trace data for patterns.
```

---

## 💻 Step 4.4: Investigate Errors with MCP (Developer)

Now let's generate some realistic errors and use MCP to investigate them — without leaving your IDE!

### Generate Errors

1. Go to your AI Chat Service UI (http://localhost:8000)
2. Enable the **🐛 Simulate Errors** toggle in the options row
3. Send 5-10 messages to trigger various error types

The app will randomly generate realistic RAG/LLM errors like:
- `EMB_NULL_VECTOR`: Embedding service returning null vectors
- `CHROMA_COLLECTION_ERR`: Vector store connection issues
- `LLM_MALFORMED_RESPONSE`: Invalid LLM responses
- `CTX_WINDOW_EXCEEDED`: Context window limit errors
- `CONTENT_FILTER_BLOCK`: Content policy violations

### Find Your Errors with MCP

Now use Dynatrace MCP to investigate the errors you generated:

```
@dynatrace Show me all errors in the last 15 minutes for my ai-chat-service-{YOUR_ATTENDEE_ID} service.
What error codes are appearing most frequently?
```

### View Specific Log Entries

Ask MCP to show you the actual log details:

```
@dynatrace Show me the log entries for EMB_NULL_VECTOR errors in my ai-chat-service-{YOUR_ATTENDEE_ID}.
Include the error_message, stage, and timestamp for each.
```

### Understand Error Attributes

Each error log has structured attributes. Ask MCP to explain them:

```
@dynatrace For the errors in my ai-chat-service-{YOUR_ATTENDEE_ID} service, 
show me all the log attributes like error_code, error_message, and stage.
What patterns do you see?
```

### Deep Dive on a Specific Error

```
@dynatrace I'm seeing CTX_WINDOW_EXCEEDED errors in my ai-chat-service-{YOUR_ATTENDEE_ID} service. 
Show me the full log details for these errors and explain what's happening.
```

### Get Root Cause Analysis

```
@dynatrace What's causing the errors in my ai-chat-service-{YOUR_ATTENDEE_ID} service?
Analyze the error logs and tell me which component is failing most often.
```

### Generate a DQL Query (Optional)

If you want to see what DQL query would find these logs:

```
@dynatrace Generate a DQL query to find all logs where error_code equals 'EMB_NULL_VECTOR' 
for my ai-chat-service-{YOUR_ATTENDEE_ID} service in the last hour.
```

> **Pro tip:** You just investigated production errors without leaving your IDE — no dashboard tabs, no context switching!

</div>

---

<div class="persona-box sre" markdown="1">

## 🔧 Step 5: Query Your AI Service (SRE)

Use MCP for quick incident triage without leaving your terminal.

### 5.1 Find Your Service

```
@dynatrace Tell me about the service called ai-chat-service-{YOUR_ATTENDEE_ID}
```

### 5.2 Check for Anomalies

```
@dynatrace Are there any anomalies in the last hour for my ai-chat-service-{YOUR_ATTENDEE_ID} service?
What's the current error rate and how does it compare to the baseline?
```

Get Davis AI insights without opening the Dynatrace UI!

### 5.3 Analyze Token Usage

```
@dynatrace What is the total input and output token usage for spans in regards to the ai-chat-service-{YOUR_ATTENDEE_ID} service?
```

---

## 🔧 Step 6: Agentic Incident Response (SRE)

MCP enables powerful agentic workflows for incident response directly from your IDE.

### 6.1 Incident Response

```
@dynatrace Are there any open problems affecting my ai-chat-service-{YOUR_ATTENDEE_ID} service?
If so, what's the root cause and which services are impacted?
Draft a Slack message summarizing the incident.
```

**Note**: In this case, we don't anticipate that Dynatrace will have detected any problems due to lack of data and the small timeframe that this lab generates data. This example is meant to serve as inspiration for other types of questions you could ask!

### 6.2 Service Architecture

```
@dynatrace Generate a summary of my ai-chat-service-{YOUR_ATTENDEE_ID} service's architecture based on the service flow data
```

### 6.3 Capacity Planning

```
@dynatrace Analyze my ai-chat-service-{YOUR_ATTENDEE_ID} service and suggest optimizations to reduce token usage while maintaining response quality
```

---

## 🔧 Step 6.4: Error Triage with MCP (SRE)

Time to simulate a production incident and practice rapid triage using MCP!

### Generate Errors

1. Go to your AI Chat Service UI (http://localhost:8000)
2. Enable the **🐛 Simulate Errors** toggle
3. Send 10-15 messages rapidly to trigger various errors

### Rapid Error Assessment

Get an immediate overview of the error situation:

```
@dynatrace Give me a quick summary of all errors hitting my ai-chat-service-{YOUR_ATTENDEE_ID} service in the last 15 minutes.
How many errors occurred? What types? What's the error rate percentage?
```

### View Error Log Details

Ask MCP to show you what's in the actual logs:

```
@dynatrace Show me the error log entries for my ai-chat-service-{YOUR_ATTENDEE_ID} service.
Include the error_code, error_message, stage, and timestamp for each error.
```

### Analyze Error Timeline

```
@dynatrace When did errors start occurring in my ai-chat-service-{YOUR_ATTENDEE_ID} service?
Show me the timeline of errors over the last 15 minutes.
```

### Determine Error Impact

```
@dynatrace What percentage of requests to my ai-chat-service-{YOUR_ATTENDEE_ID} service are failing?
Is this affecting all users or just specific request types?
```

### Identify Top Error Types

```
@dynatrace What are the most common error_code values in my ai-chat-service-{YOUR_ATTENDEE_ID} service?
Rank them by frequency.
```

### Root Cause with Dynatrace Intelligence

```
@dynatrace Analyze the error patterns in my ai-chat-service-{YOUR_ATTENDEE_ID} service.
What is Dynatrace Intelligence's assessment of the root cause?
Which component is the source of the failures?
```

### Create Incident Communication

```
@dynatrace I need to communicate an incident to stakeholders.
Based on the errors in my ai-chat-service-{YOUR_ATTENDEE_ID} service, draft a brief incident summary
including: affected service, error types, error rate, and preliminary root cause.
```

> **SRE Pro tip:** You just triaged a production incident without opening a single dashboard. Error logs, timelines, root cause, and stakeholder communication — all from your IDE!

</div>

---

# Bonus - Dynatrace Intelligence in the Dynatrace Platform

Want to make use of Dynatrace Intelligence before even setting up the MCP? *Try it out directly in the Dynatrace UI.*

1. Open a Dynatrace Notebook
2. Add a **✨ Prompt** tile
3. Try out the following question: 
```
I would like to see top 5 spans summarized by token usage and span name for service "ai-chat-service-{YOUR_ATTENDEE_ID}" in descending order
```

> **Pro tip:** This is just one example. Dynatrace Intelligence is available in several parts of the platform including the Problems app, Notebooks and Dashboards, Logs app, Databases app, and more!

Learn more here:
* [Dynatrace Intelligence - Announcement](https://www.dynatrace.com/news/blog/dynatrace-intelligence-at-the-core-of-autonomous-operations/)
* [Dynatrace Intelligence - Documentation](https://docs.dynatrace.com/docs/shortlink/dynatrace-intelligence-landing)

---

## 🎭 Going Beyond the Basics

Below are some more advanced examples to get the most out of Dynatrace Intelligence and your AI agents!

<div class="persona-box developer" markdown="1">

## 💻 Developer Exercise: Propose & Fix Regressions

Use Dynatrace Intelligence's agentic capabilities to not just identify issues, but propose fixes.

### Detect Code-Level Issues

```
@dynatrace Look at the error traces for my ai-chat-service-{YOUR_ATTENDEE_ID} service.
Can you identify which function or code path is causing the failures?
Provide code-level details and stack traces if available.
```

### Get Fix Recommendations

```
@dynatrace Based on the EMB_NULL_VECTOR errors in my ai-chat-service-{YOUR_ATTENDEE_ID} service, 
what code changes would you recommend to handle this error gracefully?
Show me a Python code example for proper error handling.
```

### Link Errors to Changes

```
@dynatrace Have there been any recent deployments or configuration changes 
to my ai-chat-service-{YOUR_ATTENDEE_ID} service that correlate with the increase in errors?
```

### Generate DQL for Custom Investigation

```
@dynatrace Generate a DQL query to find all logs where error_code equals 'CTX_WINDOW_EXCEEDED' 
for my ai-chat-service-{YOUR_ATTENDEE_ID} service in the last hour.
Explain what the query does.
```

</div>

<div class="persona-box sre" markdown="1">

## 🔧 SRE Exercise: Agentic Incident Response

Use Dynatrace Intelligence's agentic workflows for automated incident management.

### Map Error Impact Across Dependencies

```
@dynatrace For the errors in my ai-chat-service-{YOUR_ATTENDEE_ID} service, 
show me the full dependency map. Which downstream services are affected?
What's the blast radius of this issue?
```

### Auto-Enrich Incident Data

```
@dynatrace Create a comprehensive incident report for the issues affecting 
my ai-chat-service-{YOUR_ATTENDEE_ID} service. Include:
- Timeline of when errors started
- Affected components and their relationships
- Error counts by type
- Recommended severity level
```

### Suggest Runbook Actions

```
@dynatrace Based on the current error patterns in my ai-chat-service-{YOUR_ATTENDEE_ID} service,
what remediation actions would you recommend?
Are there any runbooks or automation workflows that could help resolve this?
```

### Generate Operations Dashboard Query

```
@dynatrace Generate a DQL query for a dashboard tile that shows:
- Error rate over time for my ai-chat-service-{YOUR_ATTENDEE_ID} service
- Breakdown by error_code
- 5-minute time buckets for the last hour
```

</div>

---

## Step 7: MCP Best Practices

### 7.1 Effective Prompting

**Good prompts are specific:**

✅ Good: `@dynatrace Show me the P95 response time for my ai-chat-service-{YOUR_ATTENDEE_ID} service over the last 4 hours`

❌ Vague: `@dynatrace How is my service doing?`

### 7.2 Iterative Queries

Start broad, then drill down:

1. `@dynatrace Show me an overview of my AI service`
2. `@dynatrace What are the slowest endpoints?`
3. `@dynatrace Why is /chat endpoint slow?`
4. `@dynatrace Show me slow traces for /chat`

### 7.3 Combining with Code

You can use MCP alongside your code:

```
I'm looking at main.py where I call Azure OpenAI. 
@dynatrace What's the average latency for Azure OpenAI calls from my service?
```

---

## ✅ Checkpoint

Before completing the workshop, verify:

- [ ] You've added your `DT_ENVIRONMENT` URL to `.vscode/mcp.json`
- [ ] You've reloaded VS Code after saving the configuration
- [ ] You can query Dynatrace using `@dynatrace` in Copilot Chat
- [ ] You've successfully retrieved information about your AI service
- [ ] You've used the 🐛 **Simulate Errors** toggle to generate test errors
- [ ] You've investigated errors using MCP without leaving your IDE
- [ ] You understand how to use MCP for problem analysis
- [ ] You've explored the Dynatrace Intelligence agentic workflow exercises

---

## 🆘 Troubleshooting

### "MCP server not found"

1. Verify Node.js is installed: `node --version`
2. Ensure the `.vscode/mcp.json` file exists in your workspace
3. Test MCP server access: `npx @dynatrace-oss/dynatrace-mcp-server@latest --version`
4. Clear NPM cache if needed: `npm cache clean --force`

### "@dynatrace not recognized"

1. Check that `.vscode/mcp.json` contains the correct configuration
2. Verify the JSON syntax is valid (no trailing commas, proper quotes)
3. Reload VS Code window (`Developer: Reload Window`)
4. Make sure `DT_ENVIRONMENT` is set to your Dynatrace URL

### "Authentication failed" or "401 Unauthorized"

1. Verify `DT_ENVIRONMENT` in `.vscode/mcp.json` is correct
2. Ensure the URL format is `https://YOUR_ENV_ID.apps.dynatrace.com`
3. Check that your Dynatrace environment allows API access
4. Check that your token has appropriate permissions:
   - `Read entities`
   - `Read problems`
   - `Read metrics`
   - `Read logs`
   - `Read traces`

### "No data returned"

1. Verify `DT_ENVIRONMENT` in `.vscode/mcp.json` is correct
2. Check that your service is sending data to Dynatrace
3. Try a simpler query first: `@dynatrace List all services`

### "Connection refused" or "Network error"

1. If in a Codespace, ensure outbound connections are allowed
2. Check if your organization has firewall rules blocking the connection
3. Verify the URL format is `https://YOUR_ENV_ID.apps.dynatrace.com`

---

## 🎓 What You've Learned

<div class="persona-box developer" markdown="1">

### 💻 Developer Takeaways

You can now debug without leaving your IDE:

1. ✅ Configure Dynatrace MCP in VS Code
2. ✅ Query your service performance using natural language
3. ✅ Find bottlenecks in your RAG pipeline from the IDE
4. ✅ **Investigate errors** using error simulation and MCP queries
5. ✅ Get **fix recommendations** with code examples
6. ✅ Generate DQL queries for custom investigations
7. ✅ Combine code context with observability data

**Your new workflow:** See an error? Enable 🐛 Simulate Errors, reproduce the issue, then ask `@dynatrace` for the root cause and fix suggestions — all while looking at your code!

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE/Platform Takeaways

You can now respond to incidents faster:

1. ✅ Configure Dynatrace MCP for terminal/IDE access
2. ✅ Check for anomalies and error rates instantly
3. ✅ **Triage errors** with rapid assessment queries
4. ✅ **Map impact** across service dependencies
5. ✅ Get Davis AI root cause analysis via natural language
6. ✅ **Auto-generate incident reports** and communications
7. ✅ Query service architecture and capacity data

**Your 2 AM incident response:** Enable error simulation, generate test errors, then practice full incident triage — ask `@dynatrace` for error summary, root cause, blast radius, and draft a Slack message — all without opening a browser!

</div>

---

## 🚀 Next Steps

Now that you've completed this lab, continue to Lab 4 to learn how to automate your AI observability workflows!

---

## 🎉 Great Progress!

You've learned how to use Dynatrace MCP for agentic AI workflows. Now let's put it all together with automated workflows!

<div class="lab-nav">
  <a href="lab2-explore-traces">← Lab 2: Explore Traces</a>
  <a href="lab4-automation">Lab 4: Automation →</a>
</div>
