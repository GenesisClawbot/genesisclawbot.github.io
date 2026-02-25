#!/usr/bin/env bash
# Watch Genesis-01 live activity
# Usage: ./watch.sh [stream|session|logs]

OPENCLAW_HOME="${HOME}/.openclaw"
RAW_STREAM="${OPENCLAW_HOME}/logs/raw-stream.jsonl"
SESSIONS_DIR="${OPENCLAW_HOME}/agents/main/sessions"
MODE="${1:-stream}"

PURPLE='\033[0;35m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
DIM='\033[0;90m'
RESET='\033[0m'

echo -e "${CYAN}=== Genesis-01 Live Monitor (${MODE}) ===${RESET}"
echo -e "Ctrl+C to stop"
echo ""

case "$MODE" in
  stream)
    echo -e "${DIM}Waiting for raw stream at ${RAW_STREAM}...${RESET}"
    while [ ! -f "$RAW_STREAM" ]; do sleep 2; done
    echo -e "${GREEN}Stream file found. Tailing...${RESET}"
    echo ""
    tail -f "$RAW_STREAM" | while IFS= read -r line; do
      stream=$(echo "$line" | jq -r '.stream // .event // "?"' 2>/dev/null)
      case "$stream" in
        assistant)
          text=$(echo "$line" | jq -r '.data.text // .data.delta // empty' 2>/dev/null)
          thinking=$(echo "$line" | jq -r '.data.thinking // empty' 2>/dev/null)
          [ -n "$thinking" ] && echo -e "${PURPLE}[think]${RESET} ${thinking}"
          [ -n "$text" ] && echo -e "${GREEN}[text]${RESET} ${text}"
          ;;
        tool)
          tool=$(echo "$line" | jq -r '.data.tool // .data.name // "?"' 2>/dev/null)
          status=$(echo "$line" | jq -r '.data.status // .data.phase // "?"' 2>/dev/null)
          echo -e "${YELLOW}[tool]${RESET} ${tool} → ${status}"
          ;;
        lifecycle)
          phase=$(echo "$line" | jq -r '.data.phase // .data.status // "?"' 2>/dev/null)
          echo -e "${BLUE}[life]${RESET} ${phase}"
          ;;
        error)
          msg=$(echo "$line" | jq -r '.data.message // .data.error // .' 2>/dev/null)
          echo -e "${RED}[err]${RESET} ${msg}"
          ;;
        *)
          echo -e "${DIM}[${stream}]${RESET} $(echo "$line" | jq -c '.data // .' 2>/dev/null | head -c 200)"
          ;;
      esac
    done
    ;;

  session)
    echo -e "${DIM}Waiting for session files in ${SESSIONS_DIR}...${RESET}"
    while true; do
      newest=$(find "$SESSIONS_DIR" -name "*.jsonl" -type f 2>/dev/null | head -1)
      [ -n "$newest" ] && break
      sleep 3
    done
    echo -e "${GREEN}Session found: $(basename "$newest"). Tailing...${RESET}"
    echo ""
    tail -f "$newest" | while IFS= read -r line; do
      type=$(echo "$line" | jq -r '.type // "?"' 2>/dev/null)
      case "$type" in
        message)
          role=$(echo "$line" | jq -r '.message.role // "?"' 2>/dev/null)
          content=$(echo "$line" | jq -r '.message.content // "" | if type == "array" then .[0].text // .[0].type else . end' 2>/dev/null)
          if [ "$role" = "assistant" ]; then
            echo -e "${GREEN}[assistant]${RESET} ${content}" | head -c 500
            echo
          elif [ "$role" = "user" ]; then
            echo -e "${BLUE}[user]${RESET} ${content}" | head -c 300
            echo
          fi
          ;;
        custom)
          custom_type=$(echo "$line" | jq -r '.customType // "?"' 2>/dev/null)
          echo -e "${DIM}[${custom_type}]${RESET} $(echo "$line" | jq -c '.data // .' 2>/dev/null | head -c 200)"
          ;;
      esac
    done
    ;;

  logs)
    cd /Users/nikitavorontsov/openclaw && docker compose logs -f openclaw-gateway 2>/dev/null
    ;;

  *)
    echo "Usage: $0 [stream|session|logs]"
    exit 1
    ;;
esac
