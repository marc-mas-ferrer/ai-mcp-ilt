#!/bin/bash
# Reads .env and injects the MCP token into .vscode/mcp.json

REPO_DIR="/workspaces/$(basename "$(pwd)")"
ENV_FILE="$REPO_DIR/.env"
MCP_FILE="$REPO_DIR/.vscode/mcp.json"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ .env not found. Run this from the repo root."
  exit 1
fi

set -a; source "$ENV_FILE"; set +a

for v in ATTENDEE_ID LLM_BASE_URL LLM_API_KEY DT_ENDPOINT DT_API_TOKEN; do
  if [ -z "${!v}" ]; then echo "❌ $v is empty in .env"; exit 1; fi
done

# Persist for new terminals
for v in ATTENDEE_ID LLM_BASE_URL LLM_API_KEY LLM_CHAT_MODEL \
         DT_ENDPOINT DT_API_TOKEN DT_MCP_BEARER_TOKEN; do
  sed -i "/^export ${v}=/d" "$HOME/.bashrc" 2>/dev/null || true
  echo "export ${v}=\"${!v}\"" >> "$HOME/.bashrc"
done

# Inject MCP token
if [ -n "$DT_MCP_BEARER_TOKEN" ] && [ -f "$MCP_FILE" ]; then
  esc=$(printf '%s' "$DT_MCP_BEARER_TOKEN" | sed -e 's/[\\&/]/\\&/g')
  sed -i "s/\"Authorization\"[[:space:]]*:[[:space:]]*\"Bearer[^\"]*\"/\"Authorization\": \"Bearer ${esc}\"/" "$MCP_FILE"
  echo "✅ MCP token configured"
fi

echo "✅ Attendee ID: $ATTENDEE_ID"
echo ""
echo "⚠️  Now reload VS Code: Ctrl+Shift+P → 'Developer: Reload Window'"
