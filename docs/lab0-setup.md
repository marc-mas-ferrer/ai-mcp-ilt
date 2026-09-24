---
layout: default
title: Lab 0 - Environment Setup
nav_order: 2
---

# Lab 0: Environment Setup

**Duration:** ~15 minutes

In this lab, you will choose a recognisable Workshop ID, launch your GitHub Codespace, add the shared workshop credentials, and verify the sample RAG application before adding observability instrumentation.

## Prerequisites

Before starting, make sure you have:

- A GitHub account with Codespaces access
- The workshop credential block provided by your instructor
- Access to the workshop repository
- Login access to the Dynatrace workshop environment

## Set Your Workshop ID

Choose your Workshop ID in the sidebar on the left side of this page. The guide uses this value to personalise commands and DQL queries. The configuration command later in this lab uses the same value to configure your Codespace automatically.

- Find the **Your Attendee ID** field in the sidebar. This is your Workshop ID.
- Enter a short identifier that you will recognise easily in Dynatrace.
- Use 2 to 31 characters.
- Use letters, numbers and hyphens only. Uppercase is converted to lowercase automatically.
- Start with a letter or a number, not a hyphen.
- Do not use an email address.
- Select **Set** or press Enter.

Examples:

```text
marc-mas
acme-alex
partner07
```

Your service will appear in Dynatrace as:

```text
ai-chat-service-{YOUR_ATTENDEE_ID}
```

> **Tip:** For a partner workshop, a short pattern such as `company-firstname` is easy to recognise while avoiding email addresses.

---

## Step 1: Launch Your GitHub Codespace

### 1.1 Open the workshop environment

Select the button below:

[Open in GitHub Codespaces](https://codespaces.new/marc-mas-ferrer/ai-mcp-ilt?quickstart=1)

### 1.2 Create the Codespace

On the GitHub Codespaces page:

- Keep the default repository configuration.
- Select **Create codespace**.
- Wait for VS Code to open in your browser.
- Wait until the automatic setup process in the terminal finishes.
- Do not close the terminal while Python dependencies are being installed.

The setup script automatically creates a guided `.env` file in the repository root.

> **Important:** Each attendee receives an isolated Codespace. Changes inside your Codespace do not modify the main workshop repository or another attendee's environment.

### 1.3 Check the setup result

At the end of setup, the terminal should display an **ACTION REQUIRED** section telling you to:

- Open `.env`.
- Replace the block between the PASTE markers with the instructor credential block.
- Save the file.
- Run the personalised configuration command shown later in this lab.

---

## Step 2: Add the Shared Workshop Credentials

Your instructor provides one shared credential block containing:

- The LiteLLM gateway URL
- The LiteLLM workshop key
- The LiteLLM model alias
- The Dynatrace OTLP endpoint
- The Dynatrace ingest token
- The Dynatrace MCP platform token

You do not need to enter the Workshop ID manually in `.env`. The personalised command in Step 3 writes it for you.

### 2.1 Open .env

In the VS Code Explorer:

- Find `.env` in the repository root.
- Open it.
- Leave this line empty:

```text
ATTENDEE_ID=
```

`configure.sh` populates it from the Workshop ID entered in the guide.

### 2.2 Paste the credential block

Your instructor shares one block containing every value. Inside `.env`, look for the marked section:

```text
# ------------------ PASTE THE INSTRUCTOR BLOCK BELOW ------------------
LLM_BASE_URL=PASTE_HERE
LLM_API_KEY=PASTE_HERE
LLM_CHAT_MODEL=PASTE_HERE
DT_ENDPOINT=PASTE_HERE
DT_API_TOKEN=PASTE_HERE
DT_MCP_BEARER_TOKEN=PASTE_HERE
# --------------------------- END OF BLOCK -----------------------------
```

Select the six lines between the markers and paste the instructor block over them. Do not paste over `ATTENDEE_ID=`, which sits above the markers and stays empty.

When you are done, no `PASTE_HERE` value should remain.

### 2.3 Understand each value

| Variable | Expected format | Purpose |
|---|---|---|
| `ATTENDEE_ID` | Filled by `configure.sh` | Creates your attendee-specific service name |
| `LLM_BASE_URL` | Ends with `/v1` | OpenAI-compatible LiteLLM gateway |
| `LLM_API_KEY` | Starts with `sk-workshop-` | Authenticates to the workshop gateway |
| `LLM_CHAT_MODEL` | `workshop-chat` | LiteLLM model alias |
| `DT_ENDPOINT` | Ends with `/api/v2/otlp` | Dynatrace OTLP ingest endpoint |
| `DT_API_TOKEN` | Starts with `dt0c01.` | Sends traces and logs to Dynatrace |
| `DT_MCP_BEARER_TOKEN` | Starts with `dt0s16.` | Allows GitHub Copilot to use Dynatrace MCP |

> **Important:** Do not add quotation marks. Do not add spaces before or after `=`. Do not share the token values or paste them into Copilot Chat.

### 2.4 Save .env

Save using:

- `Cmd+S` on macOS
- `Ctrl+S` on Windows or Linux

---

## Step 3: Apply Your Personalised Configuration

### 3.1 Copy the personalised command

The command below already contains the Workshop ID entered in the guide sidebar:

```bash
bash .devcontainer/configure.sh --attendee-id={YOUR_ATTENDEE_ID}
```

Copy the rendered command from this page and run it in the Codespace terminal.

For example, if the sidebar contains `acme-alex`, the command appears as:

```bash
bash .devcontainer/configure.sh --attendee-id=acme-alex
```

You enter the Workshop ID only once, in the guide. The command transfers that value into the Codespace `.env` file.

### 3.2 Review the validation output

The script validates your Workshop ID, checks every value in `.env` against the formats described in Step 2.3, and confirms that `.vscode/mcp.json` exists, because Lab 3 depends on it.

Successful output includes:

```text
CONFIGURATION COMPLETE

Workshop ID:
  {YOUR_ATTENDEE_ID}

Dynatrace service name:
  ai-chat-service-{YOUR_ATTENDEE_ID}
```

The script validates secrets without printing their values.

If configuration is incomplete, return to `.env`, correct the reported fields, save, and run the same personalised command again.

> **Not every problem stops configuration.** Token format issues are reported as warnings rather than errors, so configuration can complete successfully with a mistyped token. If the application cannot send data to Dynatrace in Step 5, re-check the token values in `.env` first.

### 3.3 Confirm that .env was updated

Open `.env` again. The first value should now be:

```text
ATTENDEE_ID={YOUR_ATTENDEE_ID}
```

Do not edit this value manually after configuration. If you change the Workshop ID in the guide, rerun the newly personalised command.

---

## Step 4: Reload VS Code

A reload is required so GitHub Copilot and the Dynatrace MCP integration can read the configured MCP credential.

- Open the Command Palette:
  - `Cmd+Shift+P` on macOS
  - `Ctrl+Shift+P` on Windows or Linux
- Search for **Developer: Reload Window**.
- Select the command.
- Wait until VS Code finishes reloading.
- Open a new terminal.

The Python application reads `.env` directly, but the VS Code reload is still required for the MCP configuration used in Lab 3.

---

## Step 5: Verify the Sample Application

### 5.1 Start the application

From the repository root, run:

```bash
python app/main.py
```

### 5.2 Check the startup output

Expected output includes:

```text
OpenTelemetry Logging initialized - sending logs to Dynatrace
FastAPI instrumented - HTTP endpoints will create trace spans

    Attendee ID: {YOUR_ATTENDEE_ID}
    Service: ai-chat-service-{YOUR_ATTENDEE_ID}

RAG initialized successfully for attendee: {YOUR_ATTENDEE_ID}
   Vectoriser: local-hashing-384
   Documents indexed: 7
   Chat model: workshop-chat

Uvicorn running on http://0.0.0.0:8000
```

Two of these lines are worth noticing now, because they explain what you will and will not see in Dynatrace before Lab 1.

Log export and FastAPI HTTP spans are already configured in this repository, so the application starts sending some data to Dynatrace immediately. What is missing is the AI-specific telemetry: prompts, completions, token usage and the RAG pipeline structure. You add that in Lab 1.

The workshop uses:

- Amazon Nova Micro through LiteLLM for chat completions
- Deterministic local vectorisation for workshop retrieval
- ChromaDB for local vector search

No external embedding model is downloaded and no external embedding service is called.

### 5.3 Open the private chat interface

The Codespace forwards port 8000 and opens the chat interface in a browser tab automatically.

If the tab does not appear:

- Open the **Ports** tab.
- Find port 8000.
- Confirm its visibility is **Private**.
- Select the globe icon.

Do not change the port visibility to **Public**.

### 5.4 Test with RAG enabled

Make sure **Use Knowledge Base (RAG)** is enabled.

Send:

```text
What is Dynatrace?
```

Verify that you receive:

- An AI-generated response
- Knowledge-base sources
- Your Workshop ID in the interface

### 5.5 Test with RAG disabled

Disable **Use Knowledge Base (RAG)** and send:

```text
What is OpenTelemetry?
```

Verify that you receive an AI-generated response without knowledge-base retrieval.

### 5.6 Stop the application

Return to the terminal and press:

```text
Ctrl+C
```

---

<div class="lab-checkpoint" markdown="1">

## Checkpoint

Work through these before moving on. If every item is true, you are ready for Lab 1.
{: .checkpoint-intro }

- You selected a recognisable Workshop ID in the guide sidebar
- `.env` contains the instructor values, with no `PASTE_HERE` remaining
- `configure.sh` reported `CONFIGURATION COMPLETE` and `.env` now contains your Workshop ID
- You ran **Developer: Reload Window** and opened a new terminal
- The application starts and the RAG index initialises without an external model download
- Chat works with RAG enabled and disabled, and port 8000 is still **Private**

<div class="checkpoint-actions" markdown="1">
[Something isn't working](#troubleshooting){: .ws-btn-secondary }
[Continue to Lab 1](lab1-instrumentation){: .ws-btn-primary }
</div>

</div>

<div class="appendix" markdown="1">

## Troubleshooting

<details markdown="1">
<summary>.env does not exist</summary>

From the repository root, run:

```bash
bash .devcontainer/setup.sh
```

Then open the generated `.env` file.

</details>

<details markdown="1">
<summary>configure.sh says that the Workshop ID is missing</summary>

Do not run the generic command without an ID. Return to this guide and copy the personalised command:

```bash
bash .devcontainer/configure.sh --attendee-id={YOUR_ATTENDEE_ID}
```

</details>

<details markdown="1">
<summary>configure.sh reports PASTE_HERE</summary>

Open `.env` and replace the remaining placeholder lines with the instructor credential block. Save the file and rerun the same personalised command.

</details>

<details markdown="1">
<summary>Invalid Workshop ID</summary>

Use 2 to 31 characters, made up of letters, numbers and hyphens, starting with a letter or a number. Uppercase is converted to lowercase automatically. Do not use spaces or an email address.

Valid examples:

```text
marc-mas
acme-alex
partner07
```

</details>

<details markdown="1">
<summary>LLM_BASE_URL must end with /v1</summary>

Use the exact gateway URL provided by the instructor. Its final path must be `/v1`.

</details>

<details markdown="1">
<summary>DT_ENDPOINT must end with /api/v2/otlp</summary>

Use the full Dynatrace OTLP endpoint supplied by the instructor. Do not add `/v1/traces` or `/v1/logs` manually.

</details>

<details markdown="1">
<summary>Token-prefix warning</summary>

Expected token formats are:

```text
LLM_API_KEY=sk-workshop-...
DT_API_TOKEN=dt0c01....
DT_MCP_BEARER_TOKEN=dt0s16....
```

A warning means the value may have been copied incorrectly. Configuration still completes, so check the instructor credential block before continuing.

</details>

<details markdown="1">
<summary>Application authentication fails or returns No connected db</summary>

This usually means `LLM_API_KEY` does not match the current LiteLLM gateway key.

- Copy the key again from the instructor credential block.
- Check for missing or additional characters.
- Do not add quotes.
- Save `.env`.
- Rerun the personalised configuration command.
- Restart the application.

</details>

<details markdown="1">
<summary>RAG initialisation fails</summary>

The application stops on purpose if retrieval cannot be initialised, rather than serving degraded results.

- Read the complete terminal error.
- Run `python -m py_compile app/main.py`.
- Confirm that `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_CHAT_MODEL` are all set in `.env`.
- Ask the instructor for assistance if the error continues.

</details>

<details markdown="1">
<summary>Port 8000 does not open</summary>

- Confirm that `python app/main.py` is still running.
- Open the **Ports** tab.
- Confirm port 8000 is present.
- Confirm visibility is **Private**.
- Select the globe icon.

</details>

<details markdown="1">
<summary>Environment values are missing after configuration</summary>

- Confirm that `configure.sh` displayed `CONFIGURATION COMPLETE`.
- Run **Developer: Reload Window**.
- Open a new terminal.

</details>

<details markdown="1">
<summary>Dynatrace MCP is not available later in Lab 3</summary>

- Confirm that `DT_MCP_BEARER_TOKEN` was configured.
- Confirm that `.vscode/mcp.json` exists.
- Rerun the personalised configuration command.
- Run **Developer: Reload Window**.
- Open Copilot Chat after the reload.

</details>

</div>

---

## Great Job

Your Workshop ID, Codespace, LiteLLM gateway, local RAG retrieval and Dynatrace credentials are configured.

In Lab 1, you will add OpenLLMetry instrumentation and begin sending AI traces to Dynatrace.

<div class="lab-nav">
  <a href="./">← Home</a>
  <a href="lab1-instrumentation">Lab 1: Instrumentation →</a>
</div>
