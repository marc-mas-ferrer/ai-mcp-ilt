---
layout: default
title: Lab 3 - Dynatrace MCP
nav_order: 5
---

# 🤖 Lab 3: Investigating AI Services with Dynatrace MCP

**Duration:** ~30 minutes

In this lab, you will use Dynatrace MCP from GitHub Copilot in VS Code to investigate the AI service instrumented in the previous labs.

Instead of switching between your code and the Dynatrace interface, you will ask questions about traces, token usage, latency, and simulated errors directly from your development environment.

---

## 🎯 Learning Objectives

By the end of this lab, you will be able to:

- Explain how MCP connects an AI assistant with Dynatrace
- Verify the Dynatrace MCP connection in VS Code
- Query telemetry for your attendee-specific service
- Investigate LLM token usage and RAG latency
- Generate and analyse simulated application errors
- Ask Dynatrace MCP to create DQL for further investigation
- Improve MCP requests by adding precise scope and context

---

## What Is MCP?

**Model Context Protocol**, or MCP, is an open protocol that allows an AI assistant to work with external tools and data sources.

In this workshop, GitHub Copilot can use Dynatrace MCP tools to access permitted data from the workshop environment.

This allows you to:

- Query spans and logs
- Analyse token usage
- Review service latency
- Investigate application errors
- Generate DQL queries
- Continue an investigation without leaving VS Code

> MCP access is limited by the permissions assigned to the Dynatrace platform token configured by the instructor.

<div class="why-dynatrace" markdown="1">

## 🏆 Why Connect an AI Assistant to Dynatrace?

| Without Dynatrace MCP | With Dynatrace MCP |
|---|---|
| Manually navigate between tools | Investigate from the IDE |
| Write every query from scratch | Request and refine DQL using natural language |
| Copy telemetry into the conversation | Allow the assistant to retrieve permitted data |
| Start every search independently | Continue with contextual follow-up questions |
| Manually prepare investigation summaries | Ask for a summary based on retrieved evidence |

MCP does not replace observability expertise. It helps you retrieve and analyse evidence more efficiently.

</div>

---

## Step 1: Verify the MCP Configuration

The Dynatrace MCP server is already defined in:

```text
.vscode/mcp.json
```

The authentication token was configured when you ran:

```bash
bash .devcontainer/configure.sh
```

during Lab 0.

### 1.1 Check the configuration file

Open:

```text
.vscode/mcp.json
```

Confirm that it contains a server named:

```text
Dynatrace-MCP
```

The authorisation header should reference the environment variable rather than contain the token directly:

```json
"Authorization": "Bearer ${env:DT_MCP_BEARER_TOKEN}"
```

> ⚠️ Do not paste the platform token directly into `.vscode/mcp.json`. Do not share or commit the token.

### 1.2 Validate the JSON

Run:

```bash
python -m json.tool .vscode/mcp.json
```

The command should print the formatted JSON without an error.

### 1.3 Reload VS Code

If you changed `.env`, ran `configure.sh`, or edited `.vscode/mcp.json`:

1. Press `Cmd+Shift+P` on macOS or `Ctrl+Shift+P` on Windows.
2. Run **Developer: Reload Window**.
3. Wait for VS Code to reload.

The reload allows GitHub Copilot to read the updated MCP configuration and environment variable.

---

## Step 2: Verify the Dynatrace MCP Connection

### 2.1 Open GitHub Copilot Chat

Open GitHub Copilot Chat from the VS Code toolbar.

If your Copilot interface provides an agent-mode selector, switch to **Agent** mode so that Copilot can use MCP tools.

### 2.2 Check the available tools

Open the Copilot tools picker and confirm that tools from `Dynatrace-MCP` are available and enabled.

The exact tool names displayed can vary with the Dynatrace MCP version.

### 2.3 Run a simple test

Enter:

```text
Use Dynatrace MCP to list the services with telemetry in the last hour.
```

When Copilot requests permission to use a Dynatrace MCP tool, review the proposed action and allow it.

A successful response should contain data retrieved from the workshop environment.

> If `@dynatrace` is recognised in your Copilot version, you may use it. If it is not recognised, use Agent mode and explicitly write “Use Dynatrace MCP”.

### 2.4 Scope the investigation to your service

Run:

```text
Use Dynatrace MCP to find telemetry from the last hour for the service
ai-chat-service-{YOUR_ATTENDEE_ID}.

Tell me which data source and time range you queried.
```

The service name must exactly match the attendee ID configured in `.env`.

---

## 🎭 Choose Your Investigation

The next exercises examine the same service from two perspectives.

<div class="persona-box developer" markdown="1">

### 💻 Developer: Investigate a RAG request from the IDE

Your goal is to understand:

- Which stages make up the RAG request
- Which operation takes the most time
- How token use differs between LLM calls
- What evidence is available when an error occurs

**Focus on:** Steps 3 and 4.

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE or Platform Engineer: Triage service behaviour

Your goal is to determine:

- How much traffic the service generated
- How many input and output tokens were used
- Which operations contribute the most latency
- Which simulated errors occurred
- How to summarise the evidence for another team

**Focus on:** Steps 5 and 6.

</div>

---

<div class="persona-box developer" markdown="1">

## 💻 Step 3: Investigate the RAG Pipeline

### 3.1 Find recent requests

Enter:

```text
Use Dynatrace MCP to find spans from the last hour for
ai-chat-service-{YOUR_ATTENDEE_ID}.

Summarise the number of spans by span name and sort the result from highest
to lowest count.
```

Review whether the result includes operations associated with:

- The `/chat` request
- The RAG workflow
- Intent analysis
- Document retrieval
- Context generation
- Response generation
- ChromaDB vector search
- LLM calls

Exact automatic span names can vary between instrumentation versions.

### 3.2 Analyse token usage

Enter:

```text
Use Dynatrace MCP to analyse spans from the last hour for
ai-chat-service-{YOUR_ATTENDEE_ID} where gen_ai.usage.input_tokens is present.

Return:
- total input tokens
- total output tokens
- request count
- average input tokens
- average output tokens
- a breakdown by gen_ai.response.model

Show the DQL used.
```

Compare the result with the token analysis performed in Lab 2.

### 3.3 Find the slowest operations

Enter:

```text
Use Dynatrace MCP to calculate the average and maximum duration by span name
for ai-chat-service-{YOUR_ATTENDEE_ID} during the last hour.

Sort the result by average duration in descending order and show the DQL used.
```

Use the result to identify whether most of the observed time is associated with:

- The complete HTTP request
- The parent RAG workflow
- An LLM call
- Document retrieval
- Vector search
- Another operation

> Parent and child spans can overlap. Do not add the durations of every span and treat the result as total request time.

### 3.4 Compare RAG and direct requests

If you generated both request types in Lab 1, enter:

```text
Use Dynatrace MCP to compare recent traces for
ai-chat-service-{YOUR_ATTENDEE_ID}.

Identify one request that includes the rag_chat_pipeline workflow and one
request that does not. Compare their span structure and duration.

State clearly if the available telemetry is insufficient for the comparison.
```

This investigation should show that a RAG request contains more processing stages than a direct LLM request.

---

## 💻 Step 4: Investigate Simulated Errors

### 4.1 Generate errors

Return to the AI Chat interface.

1. Enable **🐛 Simulate Errors**.
2. Send at least eight messages.
3. Keep the toggle enabled until several failed requests appear.
4. Disable the toggle when finished.

The application selects simulated errors from several categories, including:

| Error code | Simulated condition |
|---|---|
| `EMB_NULL_VECTOR` | Local embedding generation returned an invalid vector |
| `EMB_TOKEN_MISMATCH` | Embedding processing returned unexpected token information |
| `CHROMA_COLLECTION_ERR` | ChromaDB collection or vector-store failure |
| `LLM_MALFORMED_RESPONSE` | The LLM gateway returned a malformed response |
| `CTX_WINDOW_EXCEEDED` | The request exceeded the simulated context limit |
| `DOC_NO_MATCHES` | Document retrieval returned no relevant matches |
| `RAG_CHAIN_TIMEOUT` | The RAG pipeline exceeded the simulated timeout |
| `CONTENT_FILTER_BLOCK` | The response was blocked by a simulated policy check |

These are intentionally generated workshop errors. They do not indicate a failure in Amazon Bedrock, LiteLLM, ChromaDB, or Dynatrace.

### 4.2 Find the generated errors

Enter:

```text
Use Dynatrace MCP to find error logs from the last 30 minutes for
ai-chat-service-{YOUR_ATTENDEE_ID}.

Filter to records where error.simulated equals "true".
Summarise the count by error.code and sort from highest to lowest.
Show the DQL used.
```

The application writes the following structured log attributes:

- `error.code`
- `error.message`
- `error.stage`
- `error.simulated`
- `attendee.id`

### 4.3 Inspect the error details

Enter:

```text
Use Dynatrace MCP to retrieve the simulated error logs from the last 30 minutes
for ai-chat-service-{YOUR_ATTENDEE_ID}.

Return timestamp, error.code, error.message, error.stage, attendee.id,
trace_id, and span_id when these fields are available.

Sort the newest errors first.
```

### 4.4 Investigate one error type

Choose an error code that appears in your data. For example:

```text
Use Dynatrace MCP to investigate EMB_NULL_VECTOR errors from the last
30 minutes for ai-chat-service-{YOUR_ATTENDEE_ID}.

Show the matching log records and any trace context available.
Explain what the application simulated, but do not claim that the real
embedding model failed.
```

This final instruction matters because the workshop deliberately generates the error.

### 4.5 Ask for a code-level recommendation

Enter:

```text
Review app/main.py and use the Dynatrace MCP evidence for the simulated
EMB_NULL_VECTOR errors in ai-chat-service-{YOUR_ATTENDEE_ID}.

Suggest a small Python change that would handle an invalid embedding result
gracefully. Separate:
1. what the telemetry shows
2. what the code currently does
3. your recommended change
```

Copilot can combine the local source code with evidence retrieved through Dynatrace MCP.

> Always review generated code before applying it. Telemetry can identify behaviour, but a suggested code change still requires engineering judgement.

</div>

---

<div class="persona-box sre" markdown="1">

## 🔧 Step 5: Assess Service Usage

### 5.1 Summarise recent activity

Enter:

```text
Use Dynatrace MCP to summarise telemetry from the last hour for
ai-chat-service-{YOUR_ATTENDEE_ID}.

Include:
- span count
- earliest and latest timestamp
- average span duration
- maximum span duration
- number of spans containing gen_ai.usage.input_tokens

Show the DQL used.
```

### 5.2 Analyse model usage

Enter:

```text
Use Dynatrace MCP to analyse LLM spans from the last hour for
ai-chat-service-{YOUR_ATTENDEE_ID}.

Group the result by gen_ai.response.model and return:
- request count
- total input tokens
- total output tokens
- average duration

Show the DQL used.
```

Depending on the instrumentation, the model may be recorded as:

```text
workshop-chat
```

or:

```text
us.amazon.nova-micro-v1:0
```

### 5.3 Identify unusual requests

Enter:

```text
Use Dynatrace MCP to find the 10 LLM spans with the highest input-token usage
for ai-chat-service-{YOUR_ATTENDEE_ID} during the last hour.

Return timestamp, span name, model, input tokens, output tokens, and duration.
Explain any visible pattern without assuming a cause that is not present in
the telemetry.
```

This request separates observed data from interpretation.

---

## 🔧 Step 6: Perform Error Triage

### 6.1 Generate the incident data

If you have not already generated errors:

1. Open the chat interface.
2. Enable **🐛 Simulate Errors**.
3. Send at least ten messages.
4. Disable the toggle.

### 6.2 Create an error overview

Enter:

```text
Use Dynatrace MCP to summarise simulated errors from the last 30 minutes for
ai-chat-service-{YOUR_ATTENDEE_ID}.

Filter to error.simulated == "true" and return:
- total simulated errors
- count by error.code
- earliest error timestamp
- latest error timestamp
- affected error.stage values

Show the DQL used.
```

### 6.3 Build an error timeline

Enter:

```text
Use Dynatrace MCP to create a one-minute time series of simulated error logs
from the last 30 minutes for ai-chat-service-{YOUR_ATTENDEE_ID}.

Break down the result by error.code and show the DQL used.
```

### 6.4 Compare errors with requests

Enter:

```text
Use Dynatrace MCP to compare simulated error logs with /chat request spans
for ai-chat-service-{YOUR_ATTENDEE_ID} during the last 30 minutes.

Report the number of simulated-error logs and the number of /chat request
spans. Do not calculate an error-rate percentage unless the two datasets
represent comparable requests and can be correlated reliably.
```

This prevents an invalid error rate from being calculated using unrelated span and log counts.

### 6.5 Prepare an investigation summary

Enter:

```text
Based only on the Dynatrace MCP evidence from the last 30 minutes, prepare a
short technical summary for ai-chat-service-{YOUR_ATTENDEE_ID}.

Include:
- observed error codes
- error counts
- affected stages
- first and latest observed error
- any available trace correlation
- recommended next investigation step

State clearly that the errors were intentionally simulated for the workshop.
Do not claim a production root cause.
```

### 6.6 Generate a stakeholder update

Enter:

```text
Using the same Dynatrace MCP evidence, draft a concise stakeholder update.

Explain that:
- this was a controlled workshop exercise
- failures were intentionally generated
- the affected workshop service
- the observed error categories
- no production impact occurred

Do not invent customer impact, business impact, or a root cause.
```

</div>

---

## Bonus: Use Dynatrace Intelligence in a Notebook

You can perform a similar natural-language investigation directly in Dynatrace.

1. Open **Notebooks**.
2. Create or open your workshop Notebook.
3. Add a **Prompt** section.
4. Enter:

```text
Show the five LLM spans with the highest total token usage for
ai-chat-service-{YOUR_ATTENDEE_ID} during the last hour.

Include span name, response model, input tokens, output tokens, total tokens,
and duration. Sort by total tokens in descending order.
```

Review the generated query before relying on the result.

Useful resources:

- [Dynatrace Intelligence documentation](https://docs.dynatrace.com/docs/shortlink/dynatrace-intelligence-landing)
- [Dynatrace Intelligence announcement](https://www.dynatrace.com/news/blog/dynatrace-intelligence-at-the-core-of-autonomous-operations/)

---

## Step 7: MCP Investigation Practices

### 7.1 Specify the data scope

A useful request identifies:

- The service
- The time range
- The required data source
- The fields or calculations needed
- The desired result format

Less useful:

```text
How is my service doing?
```

More useful:

```text
Use Dynatrace MCP to calculate the P95 duration of /chat request spans from
the last hour for ai-chat-service-{YOUR_ATTENDEE_ID}. Show the DQL used.
```

### 7.2 Ask for the query

Add:

```text
Show the DQL used.
```

This allows you to:

- Verify the filters
- Confirm the selected fields
- Reuse the query in Dynatrace
- Identify assumptions made by the assistant

### 7.3 Require evidence-based answers

For investigations, add:

```text
Separate observed evidence from interpretation. State when the available
telemetry is insufficient.
```

This reduces unsupported conclusions.

### 7.4 Refine the investigation iteratively

Start with an overview:

```text
Use Dynatrace MCP to summarise recent telemetry for
ai-chat-service-{YOUR_ATTENDEE_ID}.
```

Then narrow the investigation:

```text
Which span names account for the highest average duration?
```

Continue with a specific request:

```text
Show the five slowest instances of the highest-latency span and include their
trace IDs.
```

Finally, request correlation:

```text
For those trace IDs, identify related errors or logs when available.
```

### 7.5 Combine telemetry with code carefully

You can ask Copilot to compare Dynatrace evidence with `app/main.py`:

```text
Review app/main.py and use Dynatrace MCP to investigate the slowest operation
in ai-chat-service-{YOUR_ATTENDEE_ID}.

Separate:
- observations from telemetry
- relevant code paths
- recommended changes
```

Do not ask the assistant to modify the application automatically during the workshop. Review the recommendation first.

---

## ✅ Checkpoint

Before proceeding to Lab 4, verify that you can:

- [ ] Find `Dynatrace-MCP` in the Copilot tool list
- [ ] Run a Dynatrace MCP request from Agent mode
- [ ] Retrieve telemetry for `ai-chat-service-{YOUR_ATTENDEE_ID}`
- [ ] Ask for and review the generated DQL
- [ ] Analyse input and output token usage
- [ ] Identify high-latency operations
- [ ] Generate simulated errors
- [ ] Query logs using `error.code` and `error.simulated`
- [ ] Investigate one simulated error using logs and trace context
- [ ] Produce an evidence-based technical summary
- [ ] Distinguish observed evidence from suggested conclusions

---

## 🆘 Troubleshooting

### Dynatrace MCP does not appear in Copilot

1. Confirm `.vscode/mcp.json` exists.
2. Validate it:

```bash
python -m json.tool .vscode/mcp.json
```

3. Confirm that `DT_MCP_BEARER_TOKEN` has been configured without printing its value:

```bash
if [ -n "$DT_MCP_BEARER_TOKEN" ]; then
  echo "MCP token is configured"
else
  echo "MCP token is missing"
fi
```

4. Run:

```bash
bash .devcontainer/configure.sh
```

5. Run **Developer: Reload Window**.
6. Open a new Copilot Chat session in Agent mode.

### `@dynatrace` is not recognised

The available interaction syntax depends on the GitHub Copilot interface.

Use Agent mode and enter:

```text
Use Dynatrace MCP to list the services with telemetry in the last hour.
```

Also confirm that the Dynatrace MCP tools are enabled in the tools picker.

### Authentication fails

Confirm that:

1. Lab 0's `configure.sh` completed successfully.
2. The VS Code window was reloaded after configuration.
3. `.vscode/mcp.json` references `${env:DT_MCP_BEARER_TOKEN}`.
4. The instructor-provided platform token has not expired or been replaced.
5. The token has the permissions required by the workshop.

Do not paste the token into Copilot Chat or the terminal output.

### No data is returned

1. Confirm that `python app/main.py` is still running.
2. Generate several new chat requests.
3. Confirm that Lab 1 instrumentation initialised successfully.
4. Use the exact service name:

```text
ai-chat-service-{YOUR_ATTENDEE_ID}
```

5. Use a time range that includes the generated traffic.
6. Ask MCP to show the DQL so you can review the filters.

### Error queries return no data

Confirm that:

1. **Simulate Errors** was enabled.
2. Several requests were sent while the toggle was enabled.
3. The query uses logs rather than only spans.
4. The query filters on the actual field names:
   - `error.simulated`
   - `error.code`
   - `error.message`
   - `error.stage`
5. The selected time range includes the generated errors.

### Copilot returns a generic answer without using Dynatrace

Rewrite the request explicitly:

```text
Use the Dynatrace MCP tools to answer this question. Do not answer from general
knowledge. Show the DQL and summarise the retrieved records.
```

Check the tool-call information in Copilot Chat to verify that a Dynatrace MCP tool was invoked.

### The generated DQL fails

Ask Copilot to correct the query:

```text
The generated DQL failed with this error:

[PASTE THE ERROR ONLY]

Correct the query without changing the intended service or time range.
```

Do not paste credentials or tokens into the chat.

### The assistant claims a production root cause

The errors in this lab are simulated. Use:

```text
Rewrite the conclusion using only the retrieved evidence. State explicitly
that the errors were intentionally simulated and do not represent a real
provider or infrastructure failure.
```

---

## 🎓 What You Have Learned

<div class="persona-box developer" markdown="1">

### 💻 Developer Takeaways

You can now:

1. Query Dynatrace telemetry from VS Code
2. Investigate a RAG request without manually switching tools
3. Analyse workflow, vector-search, and LLM spans
4. Examine token usage and latency
5. Correlate simulated errors with available trace context
6. Combine local code context with observability evidence
7. Request DQL that can be reviewed and reused

**Your investigation workflow:** reproduce the behaviour, retrieve the evidence, inspect the relevant code, and only then propose a change.

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE and Platform Takeaways

You can now:

1. Scope MCP queries by service and time range
2. Summarise token usage and model activity
3. Identify operations with high latency
4. Triage structured application errors
5. Build an error timeline
6. Prepare evidence-based technical and stakeholder summaries
7. Avoid unsupported root-cause and impact claims

**Your triage workflow:** establish the scope, retrieve the data, identify the pattern, correlate the evidence, and communicate only what the telemetry supports.

</div>

---

## 🚀 Next Step

In Lab 4, you will use DQL and Dynatrace Workflows to automate analysis and notification for the instrumented AI service.

<div class="lab-nav">
  <a href="lab2-explore-traces">← Lab 2: Explore Traces</a>
  <a href="lab4-automation">Lab 4: Automation →</a>
</div>