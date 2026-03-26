#!/usr/bin/env bash
# Event Bus for Mycelium AI Framework
# Records all colony activity as structured events
# Usage: ./event-bus.sh <action> [options]
#
# Actions:
#   emit    - Emit an event
#   query   - Query events
#   stream  - Tail events (like tail -f)
#   projects - List all project IDs
#   stats   - Show event statistics
#
# Environment:
#   EVENT_BUS_FILE - Override event log location (default: workspace/events.jsonl)

set -euo pipefail

WORKSPACE="${WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
EVENT_FILE="${EVENT_BUS_FILE:-$WORKSPACE/events.jsonl}"

# Ensure event file exists
touch "$EVENT_FILE"

# Emit an event
# Usage: emit --agent <id> --role <role> --type <type> --project <project_id> --message <msg> [--data <json>]
emit() {
    local agent="" role="" type="" project="default" message="" data="{}"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --agent|-a) agent="$2"; shift 2 ;;
            --role|-r) role="$2"; shift 2 ;;
            --type|-t) type="$2"; shift 2 ;;
            --project|-p) project="$2"; shift 2 ;;
            --message|-m) message="$2"; shift 2 ;;
            --data|-d) data="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    # Validate required fields
    if [[ -z "$agent" || -z "$type" || -z "$message" ]]; then
        echo '{"error":"missing required fields: --agent, --type, --message"}' >&2
        return 1
    fi
    
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    local id
    id=$(uuidgen | tr '[:upper:]' '[:lower:]' | tr -d '-')
    
    # Build event JSON
    local event
    event=$(cat <<EOF
{"id":"$id","ts":"$timestamp","agent":"$agent","role":"$role","type":"$type","project":"$project","message":"$(echo "$message" | sed 's/"/\\"/g' | tr '\n' ' ')","data":$data}
EOF
)
    
    echo "$event" >> "$EVENT_FILE"
    
    # Also emit to stream file for live tailing
    echo "$event" >> "$WORKSPACE/events.stream"
    
    echo "$event"
}

# Query events
# Usage: query [--project <id>] [--agent <id>] [--type <type>] [--since <minutes>] [--limit <n>]
query() {
    local project="" agent="" type="" since="" limit=50
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --project|-p) project="$2"; shift 2 ;;
            --agent|-a) agent="$2"; shift 2 ;;
            --type|-t) type="$2"; shift 2 ;;
            --since|-s) since="$2"; shift 2 ;;
            --limit|-l) limit="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    local filter=""
    
    if [[ -n "$project" ]]; then
        filter="$filter | select(.project == \"$project\")"
    fi
    if [[ -n "$agent" ]]; then
        filter="$filter | select(.agent == \"$agent\")"
    fi
    if [[ -n "$type" ]]; then
        filter="$filter | select(.type == \"$type\")"
    fi
    if [[ -n "$since" ]]; then
        local since_ts
        since_ts=$(date -u -v-${since}M +"%Y-%m-%dT%H:%M:%S.000Z" 2>/dev/null || date -u -d "$since minutes ago" +"%Y-%m-%dT%H:%M:%S.000Z" 2>/dev/null || echo "")
        if [[ -n "$since_ts" ]]; then
            filter="$filter | select(.ts >= \"$since_ts\")"
        fi
    fi
    
    # Remove leading " | " if present
    filter="${filter# | }"
    
    if [[ -z "$filter" ]]; then
        tail -n "$limit" "$EVENT_FILE" | jq -s '. | reverse'
    else
        tail -n "$limit" "$EVENT_FILE" | jq -s "[.[] | select($filter)] | reverse"
    fi
}

# Stream events (tail -f style)
stream() {
    local project="" agent="" type=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --project|-p) project="$2"; shift 2 ;;
            --agent|-a) agent="$2"; shift 2 ;;
            --type|-t) type="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    echo "🌊 Event Bus Stream — $(date -u)"
    echo "────────────────────────────────────"
    [[ -n "$project" ]] && echo "Filter: project=$project"
    [[ -n "$agent" ]] && echo "Filter: agent=$agent"
    [[ -n "$type" ]] && echo "Filter: type=$type"
    echo "────────────────────────────────────"
    echo ""
    
    # Create stream file if needed
    touch "$WORKSPACE/events.stream"
    
    tail -f "$WORKSPACE/events.stream" 2>/dev/null | while IFS= read -r line; do
        local show=true
        [[ -n "$project" ]] && ! echo "$line" | jq -e ".project == \"$project\"" >/dev/null 2>&1 && show=false
        [[ -n "$agent" ]] && ! echo "$line" | jq -e ".agent == \"$agent\"" >/dev/null 2>&1 && show=false
        [[ -n "$type" ]] && ! echo "$line" | jq -e ".type == \"$type\"" >/dev/null 2>&1 && show=false
        
        if [[ "$show" == "true" ]]; then
            local ts agent_name type_name message
            ts=$(echo "$line" | jq -r '.ts' 2>/dev/null)
            agent_name=$(echo "$line" | jq -r '.agent' 2>/dev/null)
            type_name=$(echo "$line" | jq -r '.type' 2>/dev/null)
            message=$(echo "$line" | jq -r '.message' 2>/dev/null)
            
            local icon=""
            case "$type_name" in
                spawn) icon="🌱" ;;
                think) icon="💭" ;;
                decide) icon="⚡" ;;
                execute) icon="🔨" ;;
                block) icon="🛑" ;;
                complete) icon="✅" ;;
                protect) icon="🛡️" ;;
                research) icon="🔍" ;;
                stream) icon="📝" ;;
                *) icon="•" ;;
            esac
            
            echo "[$ts] $icon $agent_name ($type_name): $message"
        fi
    done
}

# List all project IDs
projects() {
    jq -r '.project' "$EVENT_FILE" 2>/dev/null | sort -u
}

# Show statistics
stats() {
    local total
    total=$(wc -l < "$EVENT_FILE" | tr -d ' ')
    
    echo "📊 Event Bus Statistics"
    echo "──────────────────────"
    echo "Total events: $total"
    echo ""
    echo "By type:"
    jq -r '.type' "$EVENT_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -20
    echo ""
    echo "By agent:"
    jq -r '.agent' "$EVENT_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -20
    echo ""
    echo "By project:"
    jq -r '.project' "$EVENT_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -20
    echo ""
    echo "Last 10 events:"
    tail -10 "$EVENT_FILE" | jq -r '"[\(.ts)] \(.type) \(.agent): \(.message)"' 2>/dev/null
}

# Show help
help() {
    cat <<'HELP'
🌊 Mycelium Event Bus

Records all colony activity as structured, filterable events.

USAGE:
  event-bus.sh <action> [options]

ACTIONS:
  emit        Emit an event
              --agent, --role, --type, --project, --message, --data

  query       Query events (returns JSON array)
              --project, --agent, --type, --since <min>, --limit <n>

  stream      Tail events in real-time (like tail -f)
              --project, --agent, --type

  projects    List all project IDs

  stats       Show event statistics

EVENT TYPES:
  spawn       Agent spawned
  think       Agent reasoning
  decide      Decision made
  execute     Action taken
  block       Blocker encountered
  complete    Task completed
  protect     Army Ant protection action
  research    Scout research action
  stream      Consciousness stream entry

EXAMPLES:
  # Emit event
  ./event-bus.sh emit --agent mycelium --role brain --type spawn --project demo-001 --message "Spawned demo-scout"

  # Query by project
  ./event-bus.sh query --project demo-001

  # Query last 5 minutes
  ./event-bus.sh query --since 5

  # Stream all events
  ./event-bus.sh stream

  # Stream only demo-001 project
  ./event-bus.sh stream --project demo-001

  # Stats
  ./event-bus.sh stats
HELP
}

# Main dispatch
case "${1:-help}" in
    emit) shift; emit "$@" ;;
    query) shift; query "$@" ;;
    stream) shift; stream "$@" ;;
    projects) shift; projects ;;
    stats) shift; stats ;;
    help|--help|-h) help ;;
    *) echo "Unknown action: $1. Use 'help' for usage." >&2; exit 1 ;;
esac
