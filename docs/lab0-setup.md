---
layout: default
title: Lab 0 - Environment Setup
nav_order: 2
---

# 🔧 Lab 0: Environment Setup

**Duration:** ~15 minutes

In this lab, you will choose a recognisable Workshop ID, launch your GitHub Codespace, add the shared workshop credentials, and verify the sample RAG application before adding observability instrumentation.

---

## 📋 Prerequisites

Before starting, make sure you have:

- ✅ A GitHub account with Codespaces access
- ✅ The workshop credential block provided by your instructor
- ✅ Access to the workshop repository
- ✅ Login access to the Dynatrace workshop environment

---

## 🏷️ Set Your Workshop ID

Choose your Workshop ID in the sidebar on the left side of this page.

The guide uses this value to personalise commands and DQL queries. The configuration command later in this lab uses the same value to configure your Codespace automatically.

1. Find the **Your Attendee ID** field in the sidebar.
2. Enter a short identifier that you will recognise easily in Dynatrace.
3. Use only lowercase letters, numbers and hyphens.
4. Do not use an email address.
5. Select **Set** or press Enter.

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

> 💡 **Tip:** For a partner workshop, a short pattern such as `company-firstname` is easy to recognise while avoiding email addresses.

---

## Step 1: Launch Your GitHub Codespace

### 1.1 Open the workshop environment

Select the button below:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/marc-mas-ferrer/ai-mcp-ilt?quickstart=1){:target="_blank" rel="noopener noreferrer"}

### 1.2 Create the Codespace

On the GitHub Codespaces page:

1. Keep the default repository configuration.
2. Select **Create codespace**.
3. Wait for VS Code to open in your browser.
4. Wait until the automatic setup process in the terminal finishes.
5. Do not close the terminal while Python dependencies are being installed.

The setup script automatically creates a guided `.env` file in the repository root.

> 💡 **Important:** Each attendee receives an isolated Codespace. Changes inside your Codespace do not modify the main workshop repository or another attendee's environment.

### 1.3 Check the setup result

At the end of setup, the terminal should display an **ACTION REQUIRED** section telling you to:

1. Open `.env`.
2. Replace every `PASTE_HERE` value.
3. Save the file.
4. Run the personalised configuration command shown later in this lab.

---

## Step 2: Add the Shared Workshop Credentials

Your instructor provides one shared credential block containing:

- The LiteLLM gateway URL
- The LiteLLM workshop key
- The Dynatrace OTLP endpoint
- The Dynatrace ingest token
- The Dynatrace MCP platform token

You do not need to enter the Workshop ID manually in `.env`. The personalised command in Step 3 writes it for you.

### 2.1 Open `.env`

In the VS Code Explorer:

1. Find `.env` in the repository root.
2. Open it.
3. Leave this line empty:

```bash
ATTENDEE_ID=
```

`configure.sh` populates it from the Workshop ID entered in the guide.

### 2.2 Replace the credential placeholders

Replace every `PASTE_HERE` value with the corresponding value from the instructor credential block.

Before configuration, the editable section looks like:

```bash
ATTENDEE_ID=

LLM_BASE_URL=PASTE_HERE
LLM_API_KEY=PASTE_HERE
LLM_CHAT_MODEL=workshop-chat

DT_ENDPOINT=PASTE_HERE
DT_API_TOKEN=PASTE_HERE

DT_MCP_BEARER_TOKEN=PASTE_HERE
```

After pasting the instructor values, the structure should look similar to:

```bash
ATTENDEE_ID=

LLM_BASE_URL=http://INSTRUCTOR_GATEWAY:4000/v1
LLM_API_KEY=sk-workshop-INSTRUCTOR_PROVIDED
LLM_CHAT_MODEL=workshop-chat

DT_ENDPOINT=https://INSTRUCTOR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.INSTRUCTOR_PROVIDED

DT_MCP_BEARER_TOKEN=dt0s16.INSTRUCTOR_PROVIDED
```

The examples above show the expected format only. Use the exact values supplied by your instructor.

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

> ⚠️ **Important:** Do not add quotation marks. Do not add spaces before or after `=`. Do not share the token values or paste them into Copilot Chat.

### 2.4 Save `.env`

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

The script checks:

- The Workshop ID format
- That every required value is present
- That no `PASTE_HERE` values remain
- That `LLM_BASE_URL` ends with `/v1`
- That `LLM_CHAT_MODEL` is `workshop-chat`
- That `DT_ENDPOINT` ends with `/api/v2/otlp`
- Whether the three token values use their expected prefixes
- That `.vscode/mcp.json` exists

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

### 3.3 Confirm that `.env` was updated

Open `.env` again. The first value should now be:

```bash
ATTENDEE_ID={YOUR_ATTENDEE_ID}
```

Do not edit this value manually after configuration. If you change the Workshop ID in the guide, rerun the newly personalised command.

---

## Step 4: Reload VS Code

A reload is required so GitHub Copilot and the Dynatrace MCP integration can read the configured MCP credential.

1. Open the Command Palette:
   - `Cmd+Shift+P` on macOS
   - `Ctrl+Shift+P` on Windows or Linux
2. Search for **Developer: Reload Window**.
3. Select the command.
4. Wait until VS Code finishes reloading.
5. Open a new terminal.

> The Python application can read `.env` directly, but the VS Code reload is still required for the MCP configuration used in Lab 3.

### 4.1 Verify the non-secret values

In the new terminal, run:

```bash
echo "Workshop ID: $ATTENDEE_ID"
echo "Service: ai-chat-service-$ATTENDEE_ID"
echo "LLM gateway: $LLM_BASE_URL"
echo "LLM model: $LLM_CHAT_MODEL"
echo "Dynatrace endpoint: $DT_ENDPOINT"
```

Expected structure:

```text
Workshop ID: {YOUR_ATTENDEE_ID}
Service: ai-chat-service-{YOUR_ATTENDEE_ID}
LLM gateway: http://INSTRUCTOR_GATEWAY:4000/v1
LLM model: workshop-chat
Dynatrace endpoint: https://INSTRUCTOR_ENV.live.dynatrace.com/api/v2/otlp
```

Do not print `LLM_API_KEY`, `DT_API_TOKEN`, or `DT_MCP_BEARER_TOKEN`.

### 4.2 Verify that secrets are present without printing them

Run:

```bash
for variable in LLM_API_KEY DT_API_TOKEN DT_MCP_BEARER_TOKEN; do
  if [ -n "${!variable}" ]; then
    echo "OK: $variable is configured"
  else
    echo "MISSING: $variable"
  fi
done
```

All three values should report `OK`.

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
Attendee ID: {YOUR_ATTENDEE_ID}
Service: ai-chat-service-{YOUR_ATTENDEE_ID}
RAG initialized successfully
Uvicorn running on http://0.0.0.0:8000
```

The workshop uses:

- Amazon Nova Micro through LiteLLM for chat completions
- Deterministic local vectorisation for workshop retrieval
- ChromaDB for local vector search

No external embedding model is downloaded and no external embedding service is called.

### 5.3 Open the private chat interface

When VS Code detects port `8000`:

1. Select **Open in Browser**.
2. If the notification does not appear, open the **Ports** tab.
3. Find port `8000`.
4. Confirm its visibility is **Private**.
5. Select the globe icon.

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

## ✅ Checkpoint

Before proceeding to Lab 1, verify that:

- [ ] You selected a recognisable Workshop ID in the guide sidebar
- [ ] The Codespace setup completed
- [ ] `.env` was created automatically
- [ ] Every `PASTE_HERE` value was replaced
- [ ] You ran the personalised `configure.sh` command
- [ ] `.env` now contains your Workshop ID
- [ ] The service name is `ai-chat-service-{YOUR_ATTENDEE_ID}`
- [ ] `LLM_BASE_URL` ends with `/v1`
- [ ] `DT_ENDPOINT` ends with `/api/v2/otlp`
- [ ] `LLM_API_KEY` is configured
- [ ] `DT_API_TOKEN` is configured
- [ ] `DT_MCP_BEARER_TOKEN` is configured
- [ ] You ran **Developer: Reload Window**
- [ ] You opened a new terminal after the reload
- [ ] The application starts without errors
- [ ] The RAG index initialises without an external model download
- [ ] Chat works with RAG enabled
- [ ] Chat works with RAG disabled
- [ ] Port `8000` remains private

---

## 🆘 Troubleshooting

### `.env` does not exist

From the repository root, run:

```bash
bash .devcontainer/setup.sh
```

Then open the generated `.env` file.

### `configure.sh` says that the Workshop ID is missing

Do not run the generic command without an ID.

Return to this guide and copy the personalised command:

```bash
bash .devcontainer/configure.sh --attendee-id={YOUR_ATTENDEE_ID}
```

### `configure.sh` reports `PASTE_HERE`

Open `.env` and replace every remaining `PASTE_HERE` value with the corresponding instructor-provided value.

Save the file and rerun the same personalised command.

### Invalid Workshop ID

Use only:

- Lowercase letters
- Numbers
- Hyphens

Do not use spaces or an email address.

Valid examples:

```text
marc-mas
acme-alex
partner07
```

### `LLM_BASE_URL must end with /v1`

Use the exact gateway URL provided by the instructor. Its final path must be:

```text
/v1
```

### `DT_ENDPOINT must end with /api/v2/otlp`

Use the full Dynatrace OTLP endpoint supplied by the instructor. Do not add `/v1/traces` or `/v1/logs` manually.

### Token-prefix warning

Expected token formats are:

```text
LLM_API_KEY=sk-workshop-...
DT_API_TOKEN=dt0c01....
DT_MCP_BEARER_TOKEN=dt0s16....
```

A warning means the value may have been copied incorrectly. Check the instructor credential block before continuing.

### Application authentication fails or returns `No connected db`

This usually means `LLM_API_KEY` does not match the current LiteLLM gateway key.

1. Copy the key again from the instructor credential block.
2. Check for missing or additional characters.
3. Do not add quotes.
4. Save `.env`.
5. Rerun the personalised configuration command.
6. Restart the application.

### RAG initialisation fails

1. Read the complete terminal error.
2. Run:

```bash
python -m py_compile app/main.py
```

3. Confirm that the application uses the workshop's deterministic local vectoriser.
4. Confirm that no old Hugging Face or sentence-transformers dependency remains.
5. Ask the instructor for assistance if the error continues.

### Port 8000 does not open

1. Confirm that `python app/main.py` is still running.
2. Open the **Ports** tab.
3. Confirm port `8000` is present.
4. Confirm visibility is **Private**.
5. Select the globe icon.

### Environment values are missing after configuration

1. Confirm that `configure.sh` displayed `CONFIGURATION COMPLETE`.
2. Run **Developer: Reload Window**.
3. Open a new terminal.
4. Run the non-secret verification commands from Step 4.1.

### Dynatrace MCP is not available later in Lab 3

1. Confirm that `DT_MCP_BEARER_TOKEN` was configured.
2. Confirm that `.vscode/mcp.json` exists.
3. Rerun the personalised configuration command.
4. Run **Developer: Reload Window**.
5. Open Copilot Chat after the reload.

---

## 🎉 Great Job!

Your Workshop ID, Codespace, LiteLLM gateway, local RAG retrieval and Dynatrace credentials are configured.

In Lab 1, you will add OpenLLMetry instrumentation and begin sending AI traces to Dynatrace.

<div class="lab-nav">
  <a href="./">← Home</a>
  <a href="lab1-instrumentation">Lab 1: Instrumentation →</a>
</div>
