#!/bin/bash
# validate-write.sh — Mycelium file placement validator
# Usage: ./scripts/validate-write.sh <file-path> [content-type] [workspace-root]
#
# content-type: lesson | mission | project-doc | config | code | temp | unknown
# workspace-root: path to the colony workspace (default: current directory)
#
# Returns: 0 = approved, 1 = rejected (with reason printed to stderr)

FILE_PATH="$1"
CONTENT_TYPE="${2:-unknown}"
WORKSPACE="${3:-.}"

if [[ -z "$FILE_PATH" ]]; then
    echo "Usage: $0 <file-path> [content-type] [workspace-root]" >&2
    echo "Content types: lesson | mission | project-doc | config | code | temp | unknown" >&2
    exit 2
fi

# Portable path normalization (works on macOS and Linux)
normalize_path() {
    local path="$1"
    if [[ "$path" != /* ]]; then
        path="$(pwd)/$path"
    fi
    python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$path" 2>/dev/null || echo "$path"
}

FILE_PATH=$(normalize_path "$FILE_PATH")
WORKSPACE=$(normalize_path "$WORKSPACE")
MEMORY_DIR="$WORKSPACE/memory"
ERRORS=""

# Rule 1: Project docs go in the project repo, NOT in memory/
if [[ "$CONTENT_TYPE" == "project-doc" ]] && [[ "$FILE_PATH" == "$MEMORY_DIR"* ]]; then
    ERRORS+="REJECTED: Project docs belong in the project repo (e.g., <project>/docs/), NOT in memory/\n"
    ERRORS+="  The memory/ directory is for colony knowledge only: #lesson, #benchmark, #durable-state\n"
    ERRORS+="  Move this to the project repo and push it there.\n"
fi

# Rule 2: Lessons should go in daily memory files WITH tags
if [[ "$CONTENT_TYPE" == "lesson" ]] && [[ "$FILE_PATH" != "$MEMORY_DIR"* ]]; then
    ERRORS+="WARNING: Lessons should go in memory/ daily files with #lesson tag, not in $FILE_PATH\n"
fi

# Rule 3: No writing directly to MEMORY.md from sub-agents
if [[ "$FILE_PATH" == "$WORKSPACE/MEMORY.md" ]]; then
    ERRORS+="REJECTED: Sub-agents must NOT write directly to MEMORY.md. Write to daily memory file instead.\n"
    ERRORS+="  Only the Mycelium (main agent) updates MEMORY.md after review.\n"
fi

# Rule 4: Non-daily files in memory/ are suspect
if [[ "$FILE_PATH" == "$MEMORY_DIR/"* ]]; then
    BASENAME=$(basename "$FILE_PATH")
    if [[ "$BASENAME" != "MEMORY.md" ]] && ! [[ "$BASENAME" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$ ]]; then
        ERRORS+="WARNING: Non-daily file in memory/ ($BASENAME). Is this a project doc that belongs elsewhere?\n"
    fi
fi

# Rule 5: Temp files go in /tmp or workspace/tmp, not in memory/
if [[ "$CONTENT_TYPE" == "temp" ]] && [[ "$FILE_PATH" == "$MEMORY_DIR"* ]]; then
    ERRORS+="REJECTED: Temporary files belong in /tmp or workspace/tmp, not in memory/\n"
fi

# Output
if [[ -n "$ERRORS" ]]; then
    echo -e "🐜 MYCELIUM WRITE VALIDATOR\n$ERRORS" >&2
    if [[ "$ERRORS" == *"REJECTED"* ]]; then
        exit 1
    fi
fi

echo "✅ Write approved: $FILE_PATH (type: $CONTENT_TYPE)"
exit 0
