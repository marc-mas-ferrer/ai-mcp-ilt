#!/usr/bin/env bash
set -euo pipefail

echo ""
echo "=============================================================="
echo " Dynatrace AI Observability Workshop"
echo " Setting up your Codespace"
echo "=============================================================="
echo ""

REPO_DIR="$(git rev-parse --show-toplevel)"
ENV_FILE="$REPO_DIR/.env"

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

echo ""
echo "=============================================================="
echo " ACTION REQUIRED"
echo "=============================================================="
echo ""
echo "1. In the guide sidebar, set your recognisable Workshop ID."
echo ""
echo "2. Open .env in the VS Code Explorer."
echo ""
echo "3. Replace the block between the PASTE markers with the"
echo "   instructor credential block."
echo ""
echo "4. Save .env."
echo ""
echo "5. Return to Lab 0 and copy its personalised configure command."
echo "   It will look like:"
echo ""
echo "   bash .devcontainer/configure.sh --attendee-id=acme-alex"
echo ""
echo "6. Run that command in this terminal."
echo ""
echo "Do not run the application until configure.sh succeeds."
echo "=============================================================="
echo ""
