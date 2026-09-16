#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(git rev-parse --show-toplevel)"
ENV_FILE="$REPO_DIR/.env"
MCP_FILE="$REPO_DIR/.vscode/mcp.json"
BASHRC_FILE="$HOME/.bashrc"
ATTENDEE_ID_ARGUMENT=""

print_usage() {
  echo "Use the personalised command shown in Lab 0:"
  echo ""
  echo "  bash .devcontainer/configure.sh --attendee-id=YOUR_WORKSHOP_ID"
  echo ""
  echo "Example:"
  echo ""
  echo "  bash .devcontainer/configure.sh --attendee-id=acme-alex"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --attendee-id)
      if [ -z "${2:-}" ]; then
        echo "ERROR: --attendee-id requires a value."
        echo ""
        print_usage
        exit 1
      fi
      ATTENDEE_ID_ARGUMENT="$2"
      shift 2
      ;;
    --attendee-id=*)
      ATTENDEE_ID_ARGUMENT="${1#*=}"
      shift
      ;;
    --help|-h)
      print_usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown option: $1"
      echo ""
      print_usage
      exit 1
      ;;
  esac
done

echo ""
echo "=============================================================="
echo " Dynatrace AI + MCP Workshop"
echo " Applying your configuration"
echo "=============================================================="
echo ""

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: .env was not found at:"
  echo "  $ENV_FILE"
  echo ""
  echo "Run this from the repository root:"
  echo "  bash .devcontainer/setup.sh"
  exit 1
fi

if [ -z "$ATTENDEE_ID_ARGUMENT" ]; then
  echo "ERROR: Workshop ID was not provided."
  echo ""
  echo "Return to Lab 0 and copy the personalised command."
  echo ""
  print_usage
  exit 1
fi

ATTENDEE_ID_ARGUMENT="$(printf '%s' "$ATTENDEE_ID_ARGUMENT" | tr '[:upper:]' '[:lower:]')"

if [[ ! "$ATTENDEE_ID_ARGUMENT" =~ ^[a-z0-9][a-z0-9-]{1,30}$ ]]; then
  echo "ERROR: Invalid Workshop ID: $ATTENDEE_ID_ARGUMENT"
  echo ""
  echo "Use between 2 and 31 characters."
  echo "Allowed characters: lowercase letters, numbers and hyphens."
  echo "Do not use an email address."
  echo "Examples: marc-mas, acme-alex, partner07"
  exit 1
fi

if grep -q '^ATTENDEE_ID=' "$ENV_FILE"; then
  sed -i "s/^ATTENDEE_ID=.*/ATTENDEE_ID=${ATTENDEE_ID_ARGUMENT}/" "$ENV_FILE"
else
  printf '\nATTENDEE_ID=%s\n' "$ATTENDEE_ID_ARGUMENT" >> "$ENV_FILE"
fi

echo "Workshop ID written to .env: $ATTENDEE_ID_ARGUMENT"
echo "Dynatrace service name: ai-chat-service-$ATTENDEE_ID_ARGUMENT"
echo ""

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

REQUIRED_VARIABLES=(
  ATTENDEE_ID
  LLM_BASE_URL
  LLM_API_KEY
  LLM_CHAT_MODEL
  DT_ENDPOINT
  DT_API_TOKEN
  DT_MCP_BEARER_TOKEN
)

CONFIGURATION_ERROR=false

echo "Checking configuration..."
echo ""

for VARIABLE in "${REQUIRED_VARIABLES[@]}"; do
  VALUE="${!VARIABLE:-}"

  if [ -z "$VALUE" ]; then
    echo "MISSING: $VARIABLE is empty"
    CONFIGURATION_ERROR=true
  elif [ "$VALUE" = "PASTE_HERE" ]; then
    echo "MISSING: $VARIABLE still contains PASTE_HERE"
    CONFIGURATION_ERROR=true
  else
    echo "OK: $VARIABLE"
  fi
done

if [[ "$LLM_BASE_URL" != */v1 ]]; then
  echo "INVALID: LLM_BASE_URL must end with /v1"
  CONFIGURATION_ERROR=true
fi

if [ "$LLM_CHAT_MODEL" != "workshop-chat" ]; then
  echo "INVALID: LLM_CHAT_MODEL must be workshop-chat"
  CONFIGURATION_ERROR=true
fi

if [[ "$DT_ENDPOINT" != */api/v2/otlp ]]; then
  echo "INVALID: DT_ENDPOINT must end with /api/v2/otlp"
  CONFIGURATION_ERROR=true
fi

if [[ "$LLM_API_KEY" != sk-workshop-* ]]; then
  echo "WARNING: LLM_API_KEY does not start with sk-workshop-"
fi

if [[ "$DT_API_TOKEN" != dt0c01.* ]]; then
  echo "WARNING: DT_API_TOKEN does not start with dt0c01."
fi

if [[ "$DT_MCP_BEARER_TOKEN" != dt0s16.* ]]; then
  echo "WARNING: DT_MCP_BEARER_TOKEN does not start with dt0s16."
fi

if [ "$CONFIGURATION_ERROR" = true ]; then
  echo ""
  echo "=============================================================="
  echo " CONFIGURATION INCOMPLETE"
  echo "=============================================================="
  echo ""
  echo "Open .env and fix the fields listed above."
  echo "Then run the same personalised command again:"
  echo ""
  echo "  bash .devcontainer/configure.sh --attendee-id=$ATTENDEE_ID_ARGUMENT"
  echo ""
  exit 1
fi

echo ""
echo "Persisting workshop values for new terminal sessions..."

for VARIABLE in "${REQUIRED_VARIABLES[@]}"; do
  sed -i "/^export ${VARIABLE}=/d" "$BASHRC_FILE" 2>/dev/null || true
  printf 'export %s=%q\n' "$VARIABLE" "${!VARIABLE}" >> "$BASHRC_FILE"
done

if [ ! -f "$MCP_FILE" ]; then
  echo ""
  echo "ERROR: .vscode/mcp.json was not found."
  echo "Lab 3 cannot use Dynatrace MCP until this tracked file exists."
  exit 1
fi

# The workspace copy is personal to this Codespace. Insert the MCP token so
# the VS Code MCP client can use it after the attendee reloads the window.
ESCAPED_MCP_TOKEN="$(printf '%s' "$DT_MCP_BEARER_TOKEN" | sed -e 's/[\\&/]/\\&/g')"

if grep -q '"Authorization"' "$MCP_FILE"; then
  sed -i \
    "s/\"Authorization\"[[:space:]]*:[[:space:]]*\"Bearer[^\"]*\"/\"Authorization\": \"Bearer ${ESCAPED_MCP_TOKEN}\"/" \
    "$MCP_FILE"
else
  echo "ERROR: Authorization header was not found in .vscode/mcp.json."
  exit 1
fi

echo "MCP token configured in the Codespace workspace."
echo ""
echo "=============================================================="
echo " CONFIGURATION COMPLETE"
echo "=============================================================="
echo ""
echo "Workshop ID:"
echo "  $ATTENDEE_ID"
echo ""
echo "Dynatrace service name:"
echo "  ai-chat-service-$ATTENDEE_ID"
echo ""
echo "LLM gateway:"
echo "  $LLM_BASE_URL"
echo ""
echo "LLM model:"
echo "  $LLM_CHAT_MODEL"
echo ""
echo "Dynatrace OTLP endpoint:"
echo "  $DT_ENDPOINT"
echo ""
echo "Secret values were validated but not printed."
echo ""
echo "NEXT STEPS"
echo ""
echo "1. Reload VS Code:"
echo "   Command Palette -> Developer: Reload Window"
echo ""
echo "2. Open a new terminal after the reload."
echo ""
echo "3. Start the application:"
echo "   python app/main.py"
echo ""
echo "The reload is required for GitHub Copilot and Dynatrace MCP."
echo "=============================================================="
echo ""
