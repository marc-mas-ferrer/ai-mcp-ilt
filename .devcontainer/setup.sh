#!/bin/bash
echo "🚀 Setting up Dynatrace AI Observability Workshop Environment..."

REPO_DIR="/workspaces/$(basename "$(pwd)")"
ENV_FILE="$REPO_DIR/.env"
BASHRC_FILE="$HOME/.bashrc"

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$REPO_DIR/app/requirements.txt"

if [ ! -f "$ENV_FILE" ]; then
  echo "📝 Creating configuration template..."
  cat > "$ENV_FILE" << 'EOF'
# ═══════════════════════════════════════════════════════════════════════════
# Dynatrace AI Observability Workshop - Configuration
# Fill in EVERY value below from your instructor's credential card.
# ═══════════════════════════════════════════════════════════════════════════

# Your unique ID - initials, no spaces (e.g. mmas)
ATTENDEE_ID=

# LLM gateway (provided by instructor)
LLM_BASE_URL=
LLM_API_KEY=
LLM_CHAT_MODEL=workshop-chat

# Dynatrace OTLP ingest
# ⚠️ DT_ENDPOINT MUST end with /api/v2/otlp
DT_ENDPOINT=
DT_API_TOKEN=

# Dynatrace MCP (Lab 3)
DT_MCP_BEARER_TOKEN=
EOF
  echo "✅ Created .env - fill it in before starting"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  📋 ACTION REQUIRED                                              ║"
echo "║  1. Open .env and paste the values from your credential card     ║"
echo "║  2. Run: bash .devcontainer/configure.sh                         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
