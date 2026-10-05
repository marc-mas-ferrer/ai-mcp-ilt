#!/usr/bin/env bash
# Shows the workshop setup result and the next step.
#
# If setup.sh is still running, follows its progress live and then shows the
# result. Called by setup.sh, by the "Workshop setup" VS Code task and by
# ~/.bashrc in every new terminal.
#
#   --quiet-when-configured   Print nothing once configure.sh has completed.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$REPO_DIR/.env"
STATE_DIR="$HOME/.workshop"
STATUS_FILE="$STATE_DIR/setup.status"
LOG_FILE="$STATE_DIR/setup.log"

GREEN_BG=$'\033[1;97;42m'
RED_BG=$'\033[1;97;41m'
YELLOW=$'\033[1;33m'
CYAN=$'\033[1;36m'
BOLD=$'\033[1m'
RESET=$'\033[0m'

is_configured() {
  [ -f "$ENV_FILE" ] &&
    grep -Eq '^ATTENDEE_ID=.+' "$ENV_FILE" &&
    ! grep -q 'PASTE_HERE' "$ENV_FILE"
}

if [ "${1:-}" = "--quiet-when-configured" ] && is_configured; then
  exit 0
fi

read_status() { cat "$STATUS_FILE" 2>/dev/null || true; }

# Wait for setup.sh to start (the task can open before postCreateCommand runs)
STATUS="$(read_status)"
if [ -z "$STATUS" ]; then
  echo -e "${YELLOW}Waiting for the workshop setup to start...${RESET}"
  for _ in $(seq 1 120); do
    sleep 1
    STATUS="$(read_status)"
    [ -n "$STATUS" ] && break
  done
fi

# Follow progress while setup.sh is running
if [[ "$STATUS" == running* ]]; then
  SETUP_PID="${STATUS#running }"
  if [ -d "/proc/$SETUP_PID" ] || kill -0 "$SETUP_PID" 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}${BOLD}Workshop setup is running. Progress is shown below.${RESET}"
    echo -e "${YELLOW}Leave this terminal open. The next step appears here when it finishes.${RESET}"
    echo -e "${YELLOW}(Press Ctrl+C only if you need this terminal before then.)${RESET}"
    echo ""
    tail -n +1 -f --pid="$SETUP_PID" "$LOG_FILE" 2>/dev/null
    # Give setup.sh a moment to write its final status
    for _ in 1 2 3 4 5; do
      [[ "$(read_status)" == running* ]] || break
      sleep 1
    done
  fi
  STATUS="$(read_status)"
fi

echo ""
case "$STATUS" in
  success)
    echo -e "${GREEN_BG}                                                              ${RESET}"
    echo -e "${GREEN_BG}             ✔  SETUP COMPLETED SUCCESSFULLY                  ${RESET}"
    echo -e "${GREEN_BG}                                                              ${RESET}"
    echo ""
    if is_configured; then
      echo -e "${BOLD}Your environment is configured.${RESET} Continue with the workshop guide."
      echo ""
      exit 0
    fi
    echo -e "${CYAN}${BOLD}▶ NEXT STEP: Lab 0, Step 2 - Add the shared workshop credentials${RESET}"
    echo ""
    echo "  1. Open .env in the VS Code Explorer (repository root)."
    echo "  2. Replace the block between the PASTE markers with the"
    echo "     instructor credential block, then save the file."
    echo "  3. Copy the personalised configure command from Lab 0, Step 3"
    echo "     and run it in this terminal. It looks like:"
    echo ""
    echo -e "       ${BOLD}bash .devcontainer/configure.sh --attendee-id=acme-alex${RESET}"
    echo ""
    echo "  Do not run the application until configure.sh succeeds."
    echo ""
    # Open .env in the editor once, when running inside a VS Code terminal
    if [ -n "${VSCODE_IPC_HOOK_CLI:-}" ] && command -v code >/dev/null 2>&1 &&
      [ ! -f "$STATE_DIR/env-opened" ]; then
      touch "$STATE_DIR/env-opened"
      timeout 10 code "$ENV_FILE" >/dev/null 2>&1 || true
    fi
    ;;
  failed)
    echo -e "${RED_BG}                                                              ${RESET}"
    echo -e "${RED_BG}             ✘  SETUP FAILED                                  ${RESET}"
    echo -e "${RED_BG}                                                              ${RESET}"
    echo ""
    echo "  Review the error in the log: $LOG_FILE"
    echo "  Then run the setup again:"
    echo ""
    echo -e "       ${BOLD}bash .devcontainer/setup.sh${RESET}"
    echo ""
    ;;
  *)
    echo -e "${RED_BG}  Workshop setup did not finish.  ${RESET}"
    echo ""
    echo "  Run it from the repository root:"
    echo ""
    echo -e "       ${BOLD}bash .devcontainer/setup.sh${RESET}"
    echo ""
    ;;
esac
