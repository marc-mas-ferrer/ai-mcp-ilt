#!/usr/bin/env bash
# Workshop setup. Runs automatically as the Codespace postCreateCommand.
#
# The postCreateCommand terminal closes as soon as this finishes, so the
# result is also recorded in ~/.workshop/ and displayed by welcome.sh in a
# terminal that stays open (VS Code task + every new terminal).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$REPO_DIR/.env"
STATE_DIR="$HOME/.workshop"
STATUS_FILE="$STATE_DIR/setup.status"
LOG_FILE="$STATE_DIR/setup.log"

# ---------------------------------------------------------------------------
# Steps (run in a child process so 'set -e' applies to every command)
# ---------------------------------------------------------------------------
if [ "${1:-}" = "--steps" ]; then
  echo ""
  echo "=============================================================="
  echo " Dynatrace AI Observability Workshop"
  echo " Setting up your Codespace"
  echo "=============================================================="
  echo ""
  echo "Repository: $REPO_DIR"
  echo ""
  echo "Installing Python dependencies..."
  python -m pip install --upgrade pip
  python -m pip install -r "$REPO_DIR/app/requirements.txt"
  echo "Python dependencies installed."

  if [ ! -f "$ENV_FILE" ]; then
    echo ""
    echo "Creating the guided .env configuration file..."

    cat > "$ENV_FILE" <<'ENVEOF'
# =====================================================================
# DYNATRACE AI + MCP WORKSHOP CONFIGURATION
#
# 1. Replace the block between the markers with the credential block
#    your instructor shares. Replace all six lines.
# 2. Save this file.
# 3. Run the personalised command shown in the workshop guide:
#      bash .devcontainer/configure.sh --attendee-id=YOUR_WORKSHOP_ID
#
# No quotation marks. No spaces around the equals sign.
# Do not commit this file. It contains workshop credentials.
# =====================================================================

# Leave empty. configure.sh fills this in from the personalised command.
ATTENDEE_ID=

# ------------------ PASTE THE INSTRUCTOR BLOCK BELOW ------------------
LLM_BASE_URL=PASTE_HERE
LLM_API_KEY=PASTE_HERE
LLM_CHAT_MODEL=PASTE_HERE
DT_ENDPOINT=PASTE_HERE
DT_API_TOKEN=PASTE_HERE
DT_MCP_BEARER_TOKEN=PASTE_HERE
# --------------------------- END OF BLOCK -----------------------------
ENVEOF

    echo "Created: $ENV_FILE"
  else
    echo ""
    echo ".env already exists. Existing values were preserved."
  fi
  exit 0
fi

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
mkdir -p "$STATE_DIR"
echo "running $$" > "$STATUS_FILE"
: > "$LOG_FILE"

# Show the welcome message in every new interactive terminal until the
# attendee has finished configure.sh (welcome.sh stays silent after that).
BASHRC="$HOME/.bashrc"
if ! grep -q '>>> workshop welcome >>>' "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" <<RCEOF

# >>> workshop welcome >>>
if [[ \$- == *i* ]] && [ -f "$SCRIPT_DIR/welcome.sh" ]; then
  bash "$SCRIPT_DIR/welcome.sh" --quiet-when-configured
fi
# <<< workshop welcome <<<
RCEOF
fi

if bash "$SCRIPT_DIR/setup.sh" --steps 2>&1 | tee -a "$LOG_FILE"; then
  echo "success" > "$STATUS_FILE"
  bash "$SCRIPT_DIR/welcome.sh"
else
  echo "failed" > "$STATUS_FILE"
  bash "$SCRIPT_DIR/welcome.sh"
  exit 1
fi
