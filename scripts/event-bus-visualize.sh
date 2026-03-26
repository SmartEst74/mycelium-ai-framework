#!/usr/bin/env bash
# Event Bus Visualizer — ASCII flow diagram
# Shows event tendrils flowing through the colony
# Usage: ./event-bus-visualize.sh [--project <id>] [--since <min>] [--live]

set -euo pipefail

WORKSPACE="${WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
EVENT_FILE="$WORKSPACE/events.jsonl"

# Role emoji/icon
role_icon() {
    case "$1" in
        mycelium|brain) echo "🧠" ;;
        scout|sensor) echo "🔍" ;;
        army-ant|protector) echo "🛡️" ;;
        dynamic-ant|builder) echo "🔨" ;;
        *) echo "•" ;;
    esac
}

# Type icon
type_icon() {
    case "$1" in
        spawn) echo "🌱" ;;
        think) echo "💭" ;;
        decide) echo "⚡" ;;
        execute) echo "🔨" ;;
        block) echo "🛑" ;;
        complete) echo "✅" ;;
        protect) echo "🛡️" ;;
        research) echo "🔍" ;;
        stream) echo "📝" ;;
        warn) echo "⚠️" ;;
        *) echo "•" ;;
    esac
}

# Draw a simple flow diagram for a project
draw_flow() {
    local project="${1:-}"
    local since="${2:-60}"
    
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         🌊 MYCELIUM EVENT BUS — Colony Flow                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Get events
    local events
    if [[ -n "$project" ]]; then
        events=$(jq -s "[.[] | select(.project == \"$project\")]" "$EVENT_FILE" 2>/dev/null)
        echo "📋 Project: $project"
    else
        events=$(jq -s '.' "$EVENT_FILE" 2>/dev/null)
        echo "📋 All Projects"
    fi
    
    local count
    count=$(echo "$events" | jq 'length')
    echo "📊 Events: $count"
    echo ""
    
    # Draw timeline
    echo "─────── Timeline ─────────────────────────────────────────────"
    echo ""
    
    echo "$events" | jq -r '.[] | "\(.ts)|\(.agent)|\(.type)|\(.message)|\(.project)"' 2>/dev/null | \
    while IFS='|' read -r ts agent type message project; do
        local t_icon
        t_icon=$(type_icon "$type")
        local r_icon
        r_icon=$(role_icon "$agent")
        
        # Truncate message
        if [[ ${#message} -gt 45 ]]; then
            message="${message:0:42}..."
        fi
        
        printf "  %s %s %-15s │ %-8s │ %s\n" "$t_icon" "$r_icon" "$agent" "$type" "$message"
    done
    
    echo ""
    echo "─────── Flow Diagram ────────────────────────────────────────"
    echo ""
    
    # Build agent relationships
    local agents
    agents=$(echo "$events" | jq -r '.[].agent' 2>/dev/null | sort -u)
    
    echo "  ┌─────────────┐"
    echo "  │  🧠 MYCELIUM │  (Brain — plans, routes)"
    echo "  └──────┬──────┘"
    echo "         │"
    
    echo "$agents" | while read -r agent; do
        local r_icon
        r_icon=$(role_icon "$agent")
        local agent_events
        agent_events=$(echo "$events" | jq "[.[] | select(.agent == \"$agent\")] | length")
        local completes
        completes=$(echo "$events" | jq "[.[] | select(.agent == \"$agent\" and .type == \"complete\")] | length")
        local blocks
        blocks=$(echo "$events" | jq "[.[] | select(.agent == \"$agent\" and .type == \"block\")] | length")
        
        if [[ "$agent" != "mycelium" ]]; then
            echo "         │"
            echo "    ┌────┴────┐"
            printf "    │ %s %-7s│  %d events\n" "$r_icon" "$agent" "$agent_events"
            echo "    └────┬────┘"
            [[ $completes -gt 0 ]] && echo "         │ ✅ $completes completed"
            [[ $blocks -gt 0 ]] && echo "         │ 🛑 $blocks blocked"
            echo "         │"
        fi
    done
    
    echo "  ┌──────┴──────┐"
    echo "  │  📦 RESULTS  │  (Memory, Output)"
    echo "  └─────────────┘"
    echo ""
    
    # Stats by agent
    echo "─────── Agent Activity ──────────────────────────────────────"
    echo ""
    echo "$agents" | while read -r agent; do
        local r_icon
        r_icon=$(role_icon "$agent")
        local agent_events
        agent_events=$(echo "$events" | jq "[.[] | select(.agent == \"$agent\")] | length")
        
        printf "  %s %-12s │ " "$r_icon" "$agent"
        
        # Draw bar
        local bar_len=$((agent_events * 2))
        [[ $bar_len -gt 40 ]] && bar_len=40
        local bar=""
        for ((i=0; i<bar_len; i++)); do bar="${bar}█"; done
        echo "$bar ($agent_events)"
    done
    echo ""
}

# Live mode (refresh every N seconds)
live_mode() {
    local project="${1:-}"
    local refresh="${2:-5}"
    
    while true; do
        clear
        draw_flow "$project"
        echo "  ⏱️  Refreshing every ${refresh}s... (Ctrl+C to stop)"
        sleep "$refresh"
    done
}

# Main
case "${1:-}" in
    --live|-l)
        shift
        project="${1:-}"
        refresh="${2:-5}"
        live_mode "$project" "$refresh"
        ;;
    --project|-p)
        shift
        draw_flow "$1" "${2:-60}"
        ;;
    --help|-h)
        cat <<'HELP'
🌊 Event Bus Visualizer

USAGE:
  event-bus-visualize.sh [--project <id>] [--since <min>] [--live]

OPTIONS:
  --project, -p    Filter by project ID
  --since, -s      Events from last N minutes (default: 60)
  --live, -l       Live refresh mode (Ctrl+C to stop)

EXAMPLES:
  ./event-bus-visualize.sh                    # All events
  ./event-bus-visualize.sh --project demo-001 # Project filter
  ./event-bus-visualize.sh --live             # Live mode
  ./event-bus-visualize.sh --live demo-001 3  # Live, project, 3s refresh
HELP
        ;;
    *)
        draw_flow "${1:-}"
        ;;
esac
