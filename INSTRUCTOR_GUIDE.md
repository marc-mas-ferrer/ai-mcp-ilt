# Dynatrace AI Observability Workshop - Instructor Guide

This document provides comprehensive guidance for instructors running the workshop.

---

## 🛤️ Choose Your Setup Path

There are **two ways** to run this workshop:

| Path | Best For | What's Provided | What You Provide |
|------|----------|-----------------|------------------|
| **Option A: Use Existing Infrastructure** | Most instructors | Azure OpenAI pipeline + secrets server | Dynatrace tenant + collaborator access |
| **Option B: Stand Up Your Own** | Complete independence | Nothing | Everything (Azure OpenAI + secrets server + Dynatrace) |

---

## Option A: Use Existing Infrastructure (Recommended)

This is the **fastest and easiest way** to run the workshop. The Azure OpenAI resources and secrets server are already deployed and running at `workshop-secrets-server.azurewebsites.net`.

### Prerequisites

| Requirement | Details |
|-------------|---------|
| **Collaborator Access** | ⚠️ **Required!** You must be added as a collaborator on the [dynatrace-ai-mcp-workshop](https://github.com/sudosmitty/dynatrace-ai-mcp-workshop) repository to rotate workshop tokens via GitHub Actions. Contact the repository owner to request access. |
| **Dynatrace Environment** | Your own playground/demo tenant for attendees to send traces to |
| **GitHub Account** | With Codespaces enabled |

### How It Works

1. **Azure OpenAI** — Already provisioned with `gpt-4o` and `text-embedding-3-large` deployments
2. **Secrets Server** — Already deployed and running, distributes Azure OpenAI credentials to attendees
3. **Token Rotation** — You rotate the workshop token via GitHub Actions (requires collaborator access)
4. **Dynatrace** — You provide your own Dynatrace tenant and API token to attendees

### Create Dynatrace Platform Token for MCP (Option A)

> ⚠️ **Required for Lab 3 (MCP)!** Attendees need this token to use the Dynatrace Remote MCP server.

1. In your Dynatrace tenant, go to **Access tokens** (Settings → Access tokens)
2. Create a new **Platform token** with these scopes:
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
3. Copy the token value
4. **Add to Secrets Server:** Use the **"Update MCP Token"** GitHub Action:
   - Go to **Actions** → **Update MCP Token**
   - Click **Run workflow**
   - Paste your Dynatrace Platform token
   - Click **Run workflow**

The `fetch-secrets.sh` script will automatically distribute this token to attendees along with the Azure OpenAI credentials.

### Pre-Workshop Checklist (Option A)

#### 1 Week Before

- [ ] **Verify collaborator access** — Confirm you can see the **Actions** tab and run workflows in the repository
- [ ] Verify Dynatrace playground tenant access
- [ ] Create Dynatrace API token with required permissions (for OTLP traces)
- [ ] **Create Dynatrace Platform token for MCP** (see above) and update secrets server
- [ ] Test Codespace creation end-to-end
- [ ] Prepare attendee credential sharing document

#### Day Before

- [ ] Verify Dynatrace tenant is accessible
- [ ] Test API token is working
- [ ] **Rotate workshop token** using the GitHub Action (see below)
- [ ] Test the full flow: Codespace → workshop token → app runs
- [ ] Prepare backup credentials if needed
- [ ] Send reminder to attendees with GitHub account requirements

#### Day Of

- [ ] Verify all systems operational
- [ ] Have backup plans ready
- [ ] Prepare screen sharing for demos
- [ ] Have troubleshooting guide handy

### Rotating the Workshop Token (Option A)

> ⚠️ **You must be a repository collaborator to run this GitHub Action.**

1. Go to the repository's **Actions** tab
2. Select **"Rotate Workshop Token"** workflow
3. Click **"Run workflow"**
4. Enter a custom token (e.g., `dynatrace2026`) or leave empty to auto-generate
5. Click **"Run workflow"**
6. View the workflow summary to see the new token

> 💡 **Tip:** Use simple, memorable words that are easy to share verbally and type correctly.

If you cannot see the **Actions** tab or cannot run workflows, you need to request collaborator access from the repository owner.

---

## Option B: Stand Up Your Own Infrastructure

Choose this option if you want **complete independence** — using your own Azure OpenAI resources, secrets server, and Dynatrace tenant. This is ideal for organizations that want to run the workshop entirely on their own infrastructure.

### Prerequisites

| Requirement | Details |
|-------------|---------|
| **Azure Subscription** | With permissions to create Azure OpenAI and Azure Functions resources |
| **Dynatrace Environment** | Your own tenant |
| **GitHub Repository** | Fork this repository for your own use |

### Infrastructure Components to Deploy

#### 1. Azure OpenAI Resource

Deploy an Azure OpenAI resource with these model deployments:

| Deployment Name | Model | Purpose |
|-----------------|-------|---------|
| `gpt-4o` (or similar) | GPT-4o | Chat completions |
| `dynatraceRAG` | `text-embedding-3-large` | Document embeddings |

> **Critical:** Use API version `2025-07-01-preview` — other versions may return 404 errors.

#### 2. Secrets Server (Azure Function)

Deploy the secrets server from the `secrets-server/` directory. See [secrets-server/README.md](secrets-server/README.md) for detailed deployment instructions.

```bash
# Quick deployment commands
az group create --name rg-workshop-secrets --location eastus

az storage account create \
  --name stworkshopsecrets \
  --resource-group rg-workshop-secrets \
  --location eastus \
  --sku Standard_LRS

az functionapp create \
  --name YOUR-FUNCTION-APP-NAME \
  --resource-group rg-workshop-secrets \
  --storage-account stworkshopsecrets \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type linux

cd secrets-server
func azure functionapp publish YOUR-FUNCTION-APP-NAME
```

#### 3. Configure Secrets Server

Configure the Azure OpenAI credentials and Dynatrace MCP token in the function app:

```bash
az functionapp config appsettings set \
  --name YOUR-FUNCTION-APP-NAME \
  --resource-group rg-workshop-secrets \
  --settings \
    ADMIN_SECRET="your-secure-admin-secret" \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com" \
    AZURE_OPENAI_API_KEY="your-azure-openai-api-key" \
    AZURE_OPENAI_CHAT_DEPLOYMENT="gpt-4o" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="dynatraceRAG" \
    AZURE_OPENAI_API_VERSION="2024-08-01-preview" \
    DT_MCP_BEARER_TOKEN="your-dynatrace-platform-token"
```

> **Important:** The `DT_MCP_BEARER_TOKEN` is a Dynatrace Platform token required for Lab 3 (MCP). See the "Create Dynatrace Platform Token for MCP" section under Option A for the full list of required scopes.
>
> **Note for Option B:** You can set the MCP token either via the `az functionapp config appsettings` command above (for initial setup) or via the **"Update MCP Token"** GitHub Action in your forked repository (for updates). The MCP token is stored in blob storage and distributed automatically via `fetch-secrets.sh`.

#### 4. Configure Your Forked Repository

In your forked repository, set up GitHub Actions secrets and variables:

| Type | Name | Description |
|------|------|-------------|
| Secret | `ADMIN_SECRET` | Must match the `ADMIN_SECRET` in your Azure Function App Settings |
| Variable | `AZURE_FUNCTION_APP_NAME` | Your function app name (e.g., `my-workshop-secrets-server`) |

#### 5. Update Codespace Configuration

Modify `.devcontainer/fetch-secrets.sh` to point to your secrets server:

```bash
# Change this line:
SECRETS_URL="https://workshop-secrets-server.azurewebsites.net/api/get-credentials"

# To your function app URL:
SECRETS_URL="https://YOUR-FUNCTION-APP-NAME.azurewebsites.net/api/get-credentials"
```

#### 6. Verify Your Setup

```bash
curl -X POST https://YOUR-FUNCTION-APP-NAME.azurewebsites.net/api/get-credentials \
  -H "Content-Type: application/json" \
  -d '{"workshop_token": "YOUR_TOKEN_HERE"}'
```

### Pre-Workshop Checklist (Option B)

#### 1 Week Before

- [ ] Deploy and test Azure OpenAI resource
- [ ] Deploy and test secrets server
- [ ] Configure GitHub Actions secrets/variables in your fork
- [ ] Verify Dynatrace tenant access
- [ ] Create Dynatrace API token with required permissions (for OTLP traces)
- [ ] **Create Dynatrace Platform token for MCP** and add to secrets server as `DT_MCP_BEARER_TOKEN`
- [ ] Test end-to-end flow

#### Day Before

- [ ] Rotate workshop token via your GitHub Actions
- [ ] Test full flow: Codespace → workshop token → app runs
- [ ] Verify all Azure resources are operational

---

## How Secrets Work (Both Options)

The workshop uses a security-first approach to credential distribution:

### What Attendees See

1. **Codespace starts** - No prompts during creation (cleaner UX)
2. **Terminal shows prompt** - Asks them to run `fetch-secrets.sh`
3. **Interactive setup** - They enter attendee ID and workshop token (visible, not masked)
4. **In `.env` file:** Only Dynatrace credentials (which they need to enter manually)
5. **Azure OpenAI credentials:** Hidden in `~/.bashrc`

### How It Works Internally

1. When the Codespace starts, `setup.sh` runs
2. It generates a random attendee ID and shows a prompt to run `fetch-secrets.sh`
3. Attendee runs `fetch-secrets.sh` which prompts for ID and workshop token
4. Script fetches Azure OpenAI credentials from the secrets server
5. Credentials are exported directly to `~/.bashrc` as environment variables
6. No intermediate files are created - secrets exist only in memory and bashrc
7. Python's `os.getenv()` reads these environment variables seamlessly

### Why This Approach?

- **Security:** Attendees never see Azure OpenAI API keys (buried in bashrc, no obvious files)
- **Simplicity:** One token shared verbally; no credential files to distribute
- **Flexibility:** Token can be rotated per workshop without changing documentation
- **Isolation:** Each Codespace is independent with its own environment
- **No files to find:** No `.workshop-secrets` or similar files for curious attendees to discover

### Attendee Troubleshooting

If an attendee's Azure OpenAI credentials aren't working:

```bash
# Check if secrets are loaded
echo "Azure: ${AZURE_OPENAI_ENDPOINT:+configured}"
echo "Attendee: $ATTENDEE_ID"

# Re-fetch credentials (will prompt for workshop token)
bash .devcontainer/fetch-secrets.sh

# Then reload bashrc or open a new terminal
source ~/.bashrc
```

> **Note:** If an attendee asks where the secrets are stored, they're in `~/.bashrc`. This is intentionally obscure - most attendees won't think to look there.

---

## Credential Distribution

Create a simple slide or document to share with attendees:

```
╔═══════════════════════════════════════════════════════════════╗
║          Dynatrace AI Workshop - Credentials                  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  After your Codespace starts, run this command:               ║
║                                                               ║
║    bash .devcontainer/fetch-secrets.sh                        ║
║                                                               ║
║  You'll be prompted for:                                      ║
║    • Attendee ID: (your initials, e.g., jsmith)              ║
║    • Workshop Token: dynatrace2026                            ║
║                                                               ║
║  ─────────────────────────────────────────────────────────────║
║                                                               ║
║  Then add to your .env file:                                  ║
║                                                               ║
║  DT_ENDPOINT:                                                 ║
║  https://abc12345.live.dynatrace.com/api/v2/otlp             ║
║                                                               ║
║  DT_API_TOKEN:                                                ║
║  dt0c01.XXXXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYY              ║
║                                                               ║
║  ─────────────────────────────────────────────────────────────║
║                                                               ║
║  Dynatrace UI:                                                ║
║  https://abc12345.live.dynatrace.com                          ║
║  Username: workshop@example.com                               ║
║  Password: [provided verbally]                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

> **Tip:** The workshop token is visible when attendees type it (not masked), making it easier to verify they entered it correctly.

---

## Timing Guide

| Time | Activity | Notes |
|------|----------|-------|
| 0:00-0:15 | Introduction & Lab 0 | Welcome, objectives, environment setup |
| 0:15-0:30 | Lab 1 | Instrumentation - most hands-on coding |
| 0:30-1:00 | Lab 2 | Dynatrace exploration - lots of screen sharing |
| 1:00-1:30 | Lab 3 | MCP - interactive, exploratory |
| 1:30-1:45 | Wrap-up | Q&A, resources, feedback |
---

## Common Issues & Solutions

### Codespace Won't Start

**Symptom:** Codespace creation hangs or fails
**Solution:** 
1. Check GitHub status page
2. Try a different browser
3. Have attendee create from repo page directly

### Azure OpenAI Errors

**Symptom:** "API key invalid", "Resource not found", 404 errors, or rate limiting
**Solution:**
1. Verify the secrets server is running: `curl https://workshop-secrets-server.azurewebsites.net/api/health`
2. Check the workshop token is correct in the secrets server app settings
3. Check Azure OpenAI resource quotas in Azure Portal
4. Verify deployment names match (`gpt-4o-mini` for chat, `dynatraceRAG` for embeddings)
5. Verify API version is `2025-07-01-preview` (newer versions return 404)
6. Have attendees re-run: `bash .devcontainer/fetch-secrets.sh`

### Invalid Workshop Token

**Symptom:** Attendee gets "Invalid workshop token" error
**Solution:**
1. Verify the workshop token on your slide matches the one configured in the secrets server
2. Check for copy/paste errors (extra spaces, missing characters)
3. Have attendee re-run: `bash .devcontainer/fetch-secrets.sh`

### Cannot Run GitHub Action (Token Rotation)

**Symptom:** Cannot see or run the "Rotate Workshop Token" workflow
**Solution:**
1. **Verify you have collaborator access** to the repository
2. Contact the repository owner to be added as a collaborator
3. If using your own fork (Option B), verify GitHub Actions secrets are configured

### No Traces in Dynatrace

**Symptom:** Application runs but no traces appear
**Solution:**
1. Verify DT_ENDPOINT format (must include /api/v2/otlp)
2. Check API token permissions
3. Wait 1-2 minutes for data to appear
4. Check for typos in .env file

### MCP Not Connecting

**Symptom:** @dynatrace commands not recognized
**Solution:**
1. Verify mcp.json configuration
2. Reload VS Code window
3. Check Node.js installation: `node --version`
4. Reinstall MCP: `npm install -g @dynatrace/mcp-server`

---

## Demo Script

### Lab 2 Demo Points

When showing Dynatrace UI:

1. **Service Discovery**
   - Show how service name includes attendee ID
   - Explain automatic service detection

2. **Trace Analysis**
   - Walk through a complete trace
   - Highlight LLM-specific attributes
   - Show token usage

3. **DQL Queries**
   - Demo live query execution
   - Show how to iterate on queries

### Lab 3 Demo Points

When showing MCP:

1. **Basic Queries**
   - Start with simple queries
   - Show natural language flexibility

2. **Problem Analysis**
   - If problems exist, demo analysis
   - Otherwise, explain the capability

3. **Agentic Workflows**
   - Show how MCP enables multi-step analysis
   - Demonstrate follow-up questions

---

## Backup Plans

### If Dynatrace Unavailable

- Use pre-recorded demo videos
- Focus on instrumentation concepts
- Show screenshots of expected results

### If Azure OpenAI Unavailable

- Have a backup Azure OpenAI resource in a different region
- Focus on instrumentation patterns
- Can still explain the concepts

### If Codespaces Unavailable

- Provide local setup instructions
- Use Docker alternative:
  ```bash
  docker pull python:3.11
  docker run -it -v $(pwd):/app python:3.11 bash
  ```

---

## Feedback Collection

At the end of the workshop, ask attendees:

1. What was the most valuable part?
2. What could be improved?
3. Would you use these tools in production?
4. Any additional topics you'd like covered?

---

## Post-Workshop

- [ ] Rotate API tokens
- [ ] Clean up Dynatrace data (optional)
- [ ] Collect and review feedback
- [ ] Update materials based on learnings
- [ ] Share resources with attendees
