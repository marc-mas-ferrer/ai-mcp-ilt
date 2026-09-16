# 🎯 Dynatrace AI Observability & MCP Workshop

> [!IMPORTANT]  
> Collaborators are not being added, and the workshop token is not being rotated to avoid impacting active workshops. Please contact the internal team to obtain the current workshop token.

A hands-on workshop for learning AI/LLM observability with Dynatrace and the Model Context Protocol (MCP).

---

> ## 🚀 **Workshop Attendees: Start Here!**
> 
> ### [![📖 Open Workshop Guide](https://img.shields.io/badge/📖_Open_Workshop_Guide-Click_Here_to_Start-blue?style=for-the-badge&logoColor=white)](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop)
>
> The guide walks you through launching your Codespace, configuring your environment, and completing all labs with detailed instructions, code snippets, and screenshots.

---

## 📋 Workshop Overview

| **Duration** | 2 - 2.5 hours |
|--------------|---------------|
| **Level** | Intermediate |
| **Format** | Hands-on Labs |
| **Platform** | GitHub Codespaces |

### What You'll Learn

- ✅ Instrument AI/LLM applications with OpenLLMetry
- ✅ Send traces to Dynatrace via OTLP
- ✅ Analyze LLM performance, token usage, and costs
- ✅ Use Dynatrace MCP for agentic AI workflows
- ✅ Automate AI cost monitoring with Dynatrace Workflows

---

## 📚 Workshop Labs

| Lab | Duration | Description |
|-----|----------|-------------|
| [Lab 0: Setup](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab0-setup.html) | 15 min | Environment configuration |
| [Lab 1: Instrumentation](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab1-instrumentation.html) | 15 min | Add OpenLLMetry to the sample app |
| [Lab 2: Explore Traces](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab2-explore-traces.html) | 30 min | Analyze AI traces in Dynatrace |
| [Lab 3: Dynatrace MCP](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab3-dynatrace-mcp.html) | 30 min | Use MCP for agentic AI |
| [Lab 4: Automation](https://sudosmitty.github.io/dynatrace-ai-mcp-workshop/lab4-automation.html) | 30 min | Create automated workflows |

---

## 👨‍🏫 Instructor Setup

### How It Works

> **Attendees share the same repository**—they don't fork it. Each attendee launches their own isolated Codespace, and all their code modifications stay private to that Codespace session.

The workshop uses a pre-deployed **Azure Function secrets server** to securely distribute Azure OpenAI credentials. Attendees enter a workshop token—they never see the actual API keys.

---

### 🛤️ Choose Your Setup Path

There are **two ways** to run this workshop as an instructor:

| Path | Best For | Requirements |
|------|----------|--------------|
| **Option A: Use Existing Infrastructure** | Most instructors | Collaborator access to this repository |
| **Option B: Stand Up Your Own** | Using your own Dynatrace tenant + Azure OpenAI | Azure subscription + deployment skills |

---

### Option A: Use Existing Infrastructure (Recommended)

Use the pre-deployed Azure OpenAI pipeline and secrets server. This is the fastest way to get started.

#### Prerequisites

1. **GitHub Account** with Codespaces enabled
2. **Collaborator access to this repository** — Required to run the GitHub Action that rotates workshop tokens. Contact the repository owner to be added as a collaborator.
3. **Dynatrace Environment** (playground/demo tenant) — You provide your own Dynatrace credentials to attendees

#### Setup Steps (Before Each Workshop)

##### 1. Rotate the Workshop Token

> ⚠️ **You must be a collaborator on this repository to run this GitHub Action.**

Use the **"Rotate Workshop Token"** GitHub Action:

1. Go to **Actions** → **Rotate Workshop Token**
2. Click **Run workflow**
3. Enter a memorable token (e.g., `perform2026`, `acepaces`, `dynatraceai`)
4. The summary will confirm the new token

> 💡 **Tip:** Rotate the token before and after each workshop session for security.

##### 2. Create Dynatrace API Token (for OTLP Traces)

Create an API token in your Dynatrace tenant with these permissions:
- `openTelemetryTrace.ingest`
- `metrics.ingest`
- `entities.read`
- `problems.read`
- `logs.read`
- `DataExport`

##### 3. Create Dynatrace Platform Token (for MCP)

> ⚠️ **Required for Lab 3!** This token enables the Dynatrace Remote MCP server.

Create a **Platform token** in your Dynatrace tenant with these scopes:
- `mcp-gateway:servers:invoke`
- `mcp-gateway:servers:read`
- `davis:analyzers:read`
- `davis:analyzers:execute`
- `davis-copilot:conversations:execute`
- `davis-copilot:nl2dql:execute`
- `davis-copilot:dql2nl:execute`
- `davis-copilot:document-search:execute`
- `storage:events:read`
- `storage:metrics:read`
- `storage:logs:read`
- `storage:buckets:read`
- `storage:files:read`
- `storage:security.events:read`
- `storage:entities:read`
- `storage:spans:read`
- `storage:bizevents:read`
- `storage:smartscape:read`

**Add to Secrets Server:** Use the **"Update MCP Token"** GitHub Action to update `DT_MCP_BEARER_TOKEN` in the secrets server (requires collaborator access). The `fetch-secrets.sh` script will automatically distribute this to attendees.

##### 4. Prepare Attendee Credentials

Create a shared document or slide with:

| Credential | Value | Notes |
|------------|-------|-------|
| `WORKSHOP_TOKEN` | The token you set in Step 1 | For Azure OpenAI + MCP access |
| `DT_ENDPOINT` | `https://YOUR_ENV.live.dynatrace.com/api/v2/otlp` | Include `/api/v2/otlp` suffix! |
| `DT_API_TOKEN` | Your Dynatrace API token | From Step 2 |

> **Note:** The Dynatrace MCP Platform token (`DT_MCP_BEARER_TOKEN`) is distributed automatically via `fetch-secrets.sh` — attendees don't need to enter it manually.

---

### Option B: Stand Up Your Own Infrastructure

If you want complete control over the Azure OpenAI resources and secrets server (e.g., using your own Azure subscription and Dynatrace tenant), you'll need to deploy your own infrastructure.

#### Prerequisites

1. **Azure Subscription** with permissions to create:
   - Azure OpenAI resource with `gpt-4o` and `text-embedding-3-large` deployments
   - Azure Function App for the secrets server
2. **Dynatrace Environment** (your own tenant)
3. **GitHub Repository** (fork this repo for your own use)

#### Setup Steps

1. **Deploy Azure OpenAI Resource** — Create model deployments for chat and embeddings
2. **Deploy the Secrets Server** — See [secrets-server/README.md](secrets-server/README.md) for detailed deployment instructions
3. **Configure GitHub Actions** — Set up the `ADMIN_SECRET` secret and `AZURE_FUNCTION_APP_NAME` variable in your forked repository
4. **Update Codespace Configuration** — Modify `.devcontainer/fetch-secrets.sh` to point to your secrets server URL

For detailed instructions, see the [Instructor Guide](INSTRUCTOR_GUIDE.md).

---

### 🔧 Existing Secrets Server (Option A)

The Azure Function secrets server is already deployed at `workshop-secrets-server.azurewebsites.net` and is ready to use.

For maintenance, configuration changes, or troubleshooting, see [secrets-server/README.md](secrets-server/README.md).

---

## 🔧 The Sample Application

### Overview

A RAG (Retrieval Augmented Generation) service built with:
- **FastAPI** - Web framework
- **Azure OpenAI** - LLM provider
- **LangChain** - Orchestration
- **ChromaDB** - Vector store

### Key Features

- 🎨 **Beautiful Chat UI** - Interactive web interface for conversations
- 📚 Pre-loaded with Dynatrace-related knowledge
- 🏷️ Unique service naming per attendee (`ai-chat-service-{ATTENDEE_ID}`)
- 🔬 Ready for OpenLLMetry instrumentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Chat UI (web interface) |
| `/chat` | POST | Chat API endpoint |
| `/info` | GET | Service information |
| `/health` | GET | Health check |
| `/documents` | POST | Add documents to knowledge base |

---

## 📊 What Gets Traced

After instrumentation, Dynatrace captures:

| Span Type | Data Captured |
|-----------|---------------|
| HTTP Requests | Endpoint, status, duration |
| Embeddings | Model, token count, latency |
| Vector Search | Query count, results |
| LLM Completion | Model, tokens, prompt/response |

---

## 🔐 Security Notes

- Azure OpenAI credentials are distributed via a secure secrets server with rotating workshop tokens
- Attendees never see the raw Azure OpenAI API key—it's fetched automatically
- Workshop tokens should be rotated after each workshop session
- Dynatrace tokens should be rotated after workshops
- Consider using a dedicated playground tenant

---

## 📝 License

This workshop is provided for educational purposes. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [OpenLLMetry / Traceloop](https://github.com/traceloop/openllmetry)
- [Dynatrace](https://www.dynatrace.com)
- [OpenTelemetry](https://opentelemetry.io)
