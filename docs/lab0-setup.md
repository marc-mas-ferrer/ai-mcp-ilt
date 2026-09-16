---
layout: default
title: Lab 0 - Environment Setup
nav_order: 2
---

# 🔧 Lab 0: Environment Setup

**Duration:** ~15 minutes

In this lab, you will launch your GitHub Codespace, configure the credentials provided by your instructor, and verify that the sample RAG application works before adding observability instrumentation.

---

## 📋 Prerequisites

Before starting, make sure you have:

- ✅ A GitHub account with Codespaces access
- ✅ The workshop credentials provided by your instructor
- ✅ Access to the workshop repository
- ✅ Login access to the Dynatrace workshop environment

---

## 🏷️ Set Your Attendee ID

Before starting the lab, set your attendee ID in the sidebar on the left side of this page.

Your attendee ID personalises the commands and DQL queries throughout the workshop.

1. Find the **Your Attendee ID** field in the sidebar.
2. Enter a short identifier using lowercase letters, numbers, or hyphens.
3. Select **Set** or press Enter.

For example:

```text
mmas
```

> 💡 **Tip:** Use a short, unique identifier without spaces. The workshop uses it to create your service name:
>
> `ai-chat-service-{YOUR_ATTENDEE_ID}`

---

## Step 1: Launch Your GitHub Codespace

### 1.1 Open the workshop environment

Select the button below:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/marc-mas-ferrer/ai-mcp-ilt?quickstart=1){:target="_blank" rel="noopener noreferrer"}

### 1.2 Create the Codespace

On the GitHub Codespaces page:

1. Keep the default repository configuration.
2. Select **Create codespace**.
3. Wait for the Codespace to finish building.
4. Confirm that VS Code opens in your browser.
5. Wait until the setup process in the terminal has finished.

> 💡 **Important:** Each attendee gets an isolated Codespace. Changes made in your Codespace do not modify the workshop repository or affect other attendees.

---

## Step 2: Configure Your Workshop Credentials

Your instructor will provide the values required by the application.

These include:

- Your attendee ID
- The LiteLLM gateway URL
- The LiteLLM workshop key
- The Dynatrace OTLP endpoint
- The Dynatrace ingest token
- The Dynatrace MCP platform token

### 2.1 Open the `.env` file

In the VS Code Explorer:

1. Locate the `.env` file in the root of the repository.
2. Open the file.
3. Replace the empty values with those provided by your instructor.

Your `.env` file should have this structure:

```bash
# Your unique workshop identifier
ATTENDEE_ID={YOUR_ATTENDEE_ID}

# LLM gateway
LLM_BASE_URL=http://18.118.23.218:4000/v1
LLM_API_KEY=sk-workshop-INSTRUCTOR_PROVIDED_VALUE
LLM_CHAT_MODEL=workshop-chat

# Dynatrace OTLP ingestion
DT_ENDPOINT=https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.INSTRUCTOR_PROVIDED_VALUE

# Dynatrace MCP
DT_MCP_BEARER_TOKEN=dt0s16.INSTRUCTOR_PROVIDED_VALUE
```

> ⚠️ **Important:** Do not add quotation marks around the values. Do not add spaces before or after `=`.

### 2.2 Check the endpoint formats

Confirm the following:

- `LLM_BASE_URL` ends with `/v1`
- `DT_ENDPOINT` ends with `/api/v2/otlp`
- `LLM_CHAT_MODEL` is `workshop-chat`
- `ATTENDEE_ID` matches the value you entered in the workshop sidebar

### 2.3 Save the file

Save `.env` using:

- `Cmd+S` on macOS
- `Ctrl+S` on Windows or Linux

---

## Step 3: Apply the Configuration

The application can load `.env` directly, but VS Code also needs the MCP token in its environment before Lab 3.

### 3.1 Run the configuration script

From the repository root, run:

```bash
bash .devcontainer/configure.sh
```

The script validates the required values, configures the Dynatrace MCP token, and makes the workshop variables available to new terminal sessions.

Expected output includes:

```text
✅ MCP token configured
✅ Attendee ID: {YOUR_ATTENDEE_ID}
```

If the script reports an empty value, return to `.env`, complete the missing field, save the file, and run the script again.

### 3.2 Reload VS Code

After the script completes:

1. Press `Cmd+Shift+P` on macOS or `Ctrl+Shift+P` on Windows.
2. Search for **Developer: Reload Window**.
3. Select the command.
4. Wait for VS Code to reload.

This allows VS Code and GitHub Copilot to read the updated MCP configuration.

### 3.3 Open a new terminal

After the reload:

1. Open **Terminal**.
2. Select **New Terminal**.
3. Run:

```bash
echo "Attendee: $ATTENDEE_ID"
echo "LLM gateway: $LLM_BASE_URL"
echo "LLM model: $LLM_CHAT_MODEL"
echo "Dynatrace endpoint: $DT_ENDPOINT"
```

Expected result:

```text
Attendee: {YOUR_ATTENDEE_ID}
LLM gateway: http://18.118.23.218:4000/v1
LLM model: workshop-chat
Dynatrace endpoint: https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
```

The command intentionally does not print any token values.

---

## Step 4: Verify the Sample Application

Before adding instrumentation, confirm that the RAG application can start and communicate with the LLM gateway.

### 4.1 Start the application

From the repository root, run:

```bash
python app/main.py
```

### 4.2 Check the startup output

You should see output similar to:

```text
╔══════════════════════════════════════════════════════════════════════╗
║         🚀 AI Chat Service Starting...                              ║
║                                                                     ║
║         Attendee ID: {YOUR_ATTENDEE_ID}                             ║
║         Service: ai-chat-service-{YOUR_ATTENDEE_ID}                 ║
╚══════════════════════════════════════════════════════════════════════╝

✅ RAG initialized successfully for attendee: {YOUR_ATTENDEE_ID}
INFO: Uvicorn running on http://0.0.0.0:8000
```

The first start may take longer because the local embedding model must be downloaded into the Codespace.

The application uses:

- Amazon Nova Micro through the LiteLLM gateway for chat completions
- `sentence-transformers/all-MiniLM-L6-v2` locally for embeddings
- ChromaDB for vector search

### 4.3 Open the chat interface

When the application starts, VS Code should detect port `8000`.

1. Select **Open in Browser** in the port notification.
2. If the notification does not appear, open the **Ports** tab.
3. Find port `8000`.
4. Select the globe icon.

### 4.4 Test the application with RAG enabled

In the chat interface, make sure **Use Knowledge Base (RAG)** is enabled.

Send:

```text
What is Dynatrace?
```

You should receive:

- An AI-generated response
- A list of knowledge-base sources below the response
- Your attendee ID displayed in the interface

### 4.5 Test the application without RAG

Disable **Use Knowledge Base (RAG)** and send:

```text
What is OpenTelemetry?
```

You should receive another AI-generated response, this time without retrieving context from the local knowledge base.

Both modes must work before continuing.

### 4.6 Stop the application

Return to the terminal and press:

```text
Ctrl+C
```

---

## ✅ Checkpoint

Before proceeding to Lab 1, verify that:

- [ ] Your attendee ID is set in the workshop sidebar
- [ ] Your Codespace is running
- [ ] The `.env` file contains all instructor-provided values
- [ ] `LLM_BASE_URL` ends with `/v1`
- [ ] `DT_ENDPOINT` ends with `/api/v2/otlp`
- [ ] `.devcontainer/configure.sh` completes successfully
- [ ] You reloaded the VS Code window
- [ ] The application starts without errors
- [ ] The local embedding model loads successfully
- [ ] The chat works with RAG enabled
- [ ] The chat works with RAG disabled

---

## 🆘 Troubleshooting

### `.env` does not exist

Run:

```bash
bash .devcontainer/setup.sh
```

Then open the newly created `.env` file and enter the instructor-provided values.

### `configure.sh` reports an empty variable

Open `.env` and confirm that every required field contains a value.

Check the variable names carefully:

```text
ATTENDEE_ID
LLM_BASE_URL
LLM_API_KEY
LLM_CHAT_MODEL
DT_ENDPOINT
DT_API_TOKEN
DT_MCP_BEARER_TOKEN
```

Save the file and run:

```bash
bash .devcontainer/configure.sh
```

### `configure.sh` cannot be executed

Run it explicitly with Bash:

```bash
bash .devcontainer/configure.sh
```

If required, make it executable:

```bash
chmod +x .devcontainer/configure.sh
```

### The LLM gateway cannot be reached

Confirm that:

1. `LLM_BASE_URL` is exactly the value provided by the instructor.
2. The URL ends with `/v1`.
3. The application is running inside the GitHub Codespace.
4. The workshop gateway is running.

The gateway uses port `4000`. Some corporate networks block this port from local computers, but the application runs from the Codespace rather than from your local computer.

### Authentication fails or `No connected db` appears

This usually means that `LLM_API_KEY` does not match the gateway key.

1. Copy the key again from the instructor-provided credentials.
2. Check for missing or additional characters.
3. Do not add quotes around the value.
4. Save `.env`.
5. Run `bash .devcontainer/configure.sh` again.
6. Restart the application.

### RAG initialisation fails

Check the complete terminal error.

Then verify that the local embedding dependencies are installed:

```bash
python -c "from langchain_huggingface import HuggingFaceEmbeddings; print('Local embeddings available')"
```

If the import fails, run:

```bash
pip install -r app/requirements.txt
```

Then restart the application:

```bash
python app/main.py
```

### Port 8000 does not open

1. Confirm that the application is still running.
2. Open the **Ports** tab in VS Code.
3. Confirm that port `8000` is listed.
4. Select the globe icon next to port `8000`.

### The application reports an incorrect attendee ID

1. Stop the application.
2. Open `.env`.
3. Correct `ATTENDEE_ID`.
4. Save the file.
5. Run:

```bash
bash .devcontainer/configure.sh
```

6. Open a new terminal.
7. Restart the application.

### Dynatrace configuration is not detected

Confirm that `.env` contains:

```bash
DT_ENDPOINT=https://YOUR_ENV.live.dynatrace.com/api/v2/otlp
DT_API_TOKEN=dt0c01.INSTRUCTOR_PROVIDED_VALUE
```

The ingest token must start with `dt0c01` and have the permissions configured by the instructor.

---

## 🎉 Great Job!

Your Codespace, LLM gateway, local embedding model, and Dynatrace configuration are ready.

In Lab 1, you will add OpenLLMetry instrumentation and begin sending AI traces to Dynatrace.

<div class="lab-nav">
  <a href="./">← Home</a>
  <a href="lab1-instrumentation">Lab 1: Instrumentation →</a>
</div>