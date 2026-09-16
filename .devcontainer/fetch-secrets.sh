#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Fetch Workshop Secrets
# Run this script if you need to re-fetch Azure OpenAI credentials
# Secrets are stored directly in ~/.bashrc (no separate file)
# ═══════════════════════════════════════════════════════════════════════════

SECRETS_SERVER_URL="${SECRETS_SERVER_URL:-https://workshop-secrets-server.azurewebsites.net/api}"
BASHRC_FILE="$HOME/.bashrc"
MCP_FILE="/workspaces/dynatrace-ai-mcp-workshop/.vscode/mcp.json"

# Ensure jq is installed for JSON parsing
if ! command -v jq &> /dev/null; then
    echo "📦 Installing jq for JSON parsing..."
    sudo apt-get update -qq && sudo apt-get install -y -qq jq > /dev/null 2>&1
fi

# Function to add a secret to bashrc (avoiding duplicates)
add_secret_to_bashrc() {
    local var_name="$1"
    local var_value="$2"
    
    # Remove any existing entry for this variable
    sed -i "/^export ${var_name}=/d" "$BASHRC_FILE" 2>/dev/null || true
    
    # Append the new value
    echo "export ${var_name}=\"${var_value}\"" >> "$BASHRC_FILE"
}

echo "🔐 Workshop Credentials Setup"
echo ""

# Prompt for attendee ID
current_attendee="${ATTENDEE_ID:-}"
read -p "Enter your attendee ID (e.g., your initials) [${current_attendee:-press enter to generate}]: " input_attendee

if [ -n "$input_attendee" ]; then
    ATTENDEE_ID="$input_attendee"
elif [ -z "$current_attendee" ]; then
    RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1)
    ATTENDEE_ID="attendee-${RANDOM_ID}"
else
    ATTENDEE_ID="$current_attendee"
fi

# Set attendee ID
export ATTENDEE_ID
add_secret_to_bashrc "ATTENDEE_ID" "$ATTENDEE_ID"
echo "✅ Attendee ID: $ATTENDEE_ID"
echo ""

# Prompt for workshop token
read -p "Enter your workshop token: " WORKSHOP_TOKEN

if [ -z "$WORKSHOP_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

# Make request to secrets server
response=$(curl -s -w "\n%{http_code}" -X POST "${SECRETS_SERVER_URL}/get-credentials" \
    -H "Content-Type: application/json" \
    -d "{\"workshop_token\": \"${WORKSHOP_TOKEN}\"}" 2>/dev/null)

# Extract HTTP status code (last line) and body (everything else)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    # Parse JSON response using jq if available, otherwise fall back to sed
    if command -v jq &> /dev/null; then
        azure_openai_endpoint=$(echo "$body" | jq -r '.azure_openai_endpoint // empty')
        azure_openai_api_key=$(echo "$body" | jq -r '.azure_openai_api_key // empty')
        azure_openai_chat_deployment=$(echo "$body" | jq -r '.azure_openai_chat_deployment // empty')
        azure_openai_embedding_deployment=$(echo "$body" | jq -r '.azure_openai_embedding_deployment // empty')
        azure_openai_api_version=$(echo "$body" | jq -r '.azure_openai_api_version // empty')
        dt_mcp_bearer_token=$(echo "$body" | jq -r '.dt_mcp_bearer_token // empty')
    else
        # Fallback: use sed (less reliable)
        body_clean=$(echo "$body" | tr -d '\n\r')
        azure_openai_endpoint=$(echo "$body_clean" | sed -n 's/.*"azure_openai_endpoint": *"\([^"]*\)".*/\1/p')
        azure_openai_api_key=$(echo "$body_clean" | sed -n 's/.*"azure_openai_api_key": *"\([^"]*\)".*/\1/p')
        azure_openai_chat_deployment=$(echo "$body_clean" | sed -n 's/.*"azure_openai_chat_deployment": *"\([^"]*\)".*/\1/p')
        azure_openai_embedding_deployment=$(echo "$body_clean" | sed -n 's/.*"azure_openai_embedding_deployment": *"\([^"]*\)".*/\1/p')
        azure_openai_api_version=$(echo "$body_clean" | sed -n 's/.*"azure_openai_api_version": *"\([^"]*\)".*/\1/p')
        dt_mcp_bearer_token=$(echo "$body_clean" | sed -n 's/.*"dt_mcp_bearer_token": *"\([^"]*\)".*/\1/p')
    fi
    
    if [ -n "$azure_openai_endpoint" ] && [ -n "$azure_openai_api_key" ]; then
        # Export to current shell
        export AZURE_OPENAI_ENDPOINT="${azure_openai_endpoint}"
        export AZURE_OPENAI_API_KEY="${azure_openai_api_key}"
        export AZURE_OPENAI_CHAT_DEPLOYMENT="${azure_openai_chat_deployment}"
        export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="${azure_openai_embedding_deployment}"
        export AZURE_OPENAI_API_VERSION="${azure_openai_api_version}"
        export DT_MCP_BEARER_TOKEN="${dt_mcp_bearer_token}"
        
        # Add to bashrc for new terminals
        add_secret_to_bashrc "AZURE_OPENAI_ENDPOINT" "${azure_openai_endpoint}"
        add_secret_to_bashrc "AZURE_OPENAI_API_KEY" "${azure_openai_api_key}"
        add_secret_to_bashrc "AZURE_OPENAI_CHAT_DEPLOYMENT" "${azure_openai_chat_deployment}"
        add_secret_to_bashrc "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" "${azure_openai_embedding_deployment}"
        add_secret_to_bashrc "AZURE_OPENAI_API_VERSION" "${azure_openai_api_version}"
        add_secret_to_bashrc "DT_MCP_BEARER_TOKEN" "${dt_mcp_bearer_token}"
        
        if [ -f "$MCP_FILE" ]; then
            escaped_token=$(printf '%s' "$DT_MCP_BEARER_TOKEN" | sed -e 's/[\\&/]/\\&/g')
            sed -i "s/\"Authorization\"[[:space:]]*:[[:space:]]*\"Bearer[^\"]*\"/\"Authorization\": \"Bearer ${escaped_token}\"/" "$MCP_FILE"
        fi

        echo ""
        echo "✅ Azure OpenAI credentials configured!"
        echo ""
        echo "╔══════════════════════════════════════════════════════════════════╗"
        echo "║  ⚠️  IMPORTANT: Reload VS Code Window for MCP updates            ║"
        echo "║                                                                  ║"
        echo "║  Press Ctrl+Shift+P (Cmd+Shift+P on Mac), then                   ║"
        echo "║  run: Developer: Reload Window                                   ║"
        echo "╚══════════════════════════════════════════════════════════════════╝"
        echo ""
    else
        echo "❌ Failed to parse credentials from response"
        exit 1
    fi
elif [ "$http_code" = "401" ]; then
    echo "❌ Invalid workshop token. Please check with your instructor."
    exit 1
else
    echo "❌ Failed to fetch credentials (HTTP $http_code)"
    echo "   Response: $body"
    exit 1
fi
