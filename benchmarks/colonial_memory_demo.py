#!/usr/bin/env python3
"""
Colonial Memory Demo

Creates a series of tagged missions in the event bus,
runs the curator, and shows the generated memory files.
This demonstrates the full pipeline: Events → Curator → QMD-indexable markdown.
"""

import os
import sys
import json
import sqlite3
import tempfile
from datetime import datetime, timezone, timedelta

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from curator import curate_mission, get_completed_missions

DB_PATH = os.path.join(os.path.dirname(__file__), "lcm_demo.db")
MEMORY_ROOT = "/tmp/mycelium-ai-framework/memory"


def create_event(db_path: str, event_type: str, payload: dict, agent: str,
                 tags: list, seq: int = None, ts: str = None):
    """Insert an event directly into the bus."""
    if ts is None:
        ts = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        if seq is None:
            cur = conn.execute("SELECT COALESCE(MAX(sequence), 0) FROM events")
            seq = cur.fetchone()[0] + 1
        conn.execute(
            "INSERT INTO events (type, payload, sequence, timestamp, agent, tags) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (event_type, json.dumps(payload), seq, ts, agent, json.dumps(tags))
        )
        conn.execute("DELETE FROM events WHERE rowid NOT IN "
                     "(SELECT rowid FROM events ORDER BY sequence DESC LIMIT 1000)")
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('sequence', ?)",
            (str(seq),)
        )
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('updated', ?)",
            (ts,)
        )
        conn.commit()


def main():
    print("=== Colonial Memory Demo ===\n")

    # Clean start
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Create tables
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                payload TEXT NOT NULL,
                sequence INTEGER UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
        conn.commit()

    print("Event bus initialized.\n")

    # ── Mission 1: Deploy cv.it1st.com ──────────────────────────

    print("Creating Mission 1: deploy-cv-it1st")

    create_event(DB_PATH, "mission.start",
        {"mission": "deploy-cv-it1st", "project": "cv-quicklinks",
         "objective": "Deploy cv-quicklinks to hummingbot at cv.it1st.com"},
        "scout-deploy",
        ["mission:deploy-cv-it1st", "project:cv-quicklinks", "role:scout", "type:mission"])

    create_event(DB_PATH, "memory.write",
        {"lesson": "When git auth fails on remote server, use tar pipe instead of SCP",
         "context": "Clone failed because GitHub had no stored credentials for the remote host"},
        "scout-deploy",
        ["mission:deploy-cv-it1st", "project:cv-quicklinks", "role:scout",
         "type:lesson", "domain:deployment"])

    create_event(DB_PATH, "memory.write",
        {"pain_point": "SCP hung silently for 30 seconds with no error — had to kill and retry",
         "diagnosis": "SSH agent forwarding not configured on the remote"},
        "scout-deploy",
        ["mission:deploy-cv-it1st", "project:cv-quicklinks", "role:scout",
         "type:pain-point", "domain:deployment"])

    create_event(DB_PATH, "memory.write",
        {"lesson": "git credential cache used wrong GitHub account — run 'gh auth setup-git' first",
         "context": "Push failed with 403 because cached creds were for sexyloverman not SmartEst74"},
        "scout-deploy",
        ["mission:deploy-cv-it1st", "project:cv-quicklinks", "role:scout",
         "type:lesson", "domain:deployment"])

    create_event(DB_PATH, "memory.write",
        {"lesson": "Nginx on hummingbot serves multiple sites — just add a new server block in sites-enabled",
         "context": "Sites already configured for it1st.com, luxveris, price-api, staging-luxveris"},
        "scout-deploy",
        ["mission:deploy-cv-it1st", "project:cv-quicklinks", "role:scout",
         "type:lesson", "domain:deployment"])

    create_event(DB_PATH, "memory.write",
        {"metric": "First deploy time", "value": "15 minutes (including nginx config)"},
        "scout-deploy",
        ["mission:deploy-cv-it1st", "project:cv-quicklinks", "role:scout",
         "type:benchmark", "domain:deployment"])

    create_event(DB_PATH, "mission.complete",
        {"mission": "deploy-cv-it1st", "status": "success",
         "summary": "cv.it1st.com live on hummingbot via nginx reverse proxy"},
        "scout-deploy",
        ["mission:deploy-cv-it1st", "project:cv-quicklinks", "role:scout", "type:mission"])

    print("  7 events written (1 start, 4 lessons, 1 pain-point, 1 benchmark, 1 complete)\n")

    # ── Mission 2: Deploy crypto dashboard ──────────────────────

    print("Creating Mission 2: deploy-crypto-dashboard")

    create_event(DB_PATH, "mission.start",
        {"mission": "deploy-crypto-dashboard", "project": "crypto-income",
         "objective": "Deploy crypto opportunity scanner dashboard to hummingbot"},
        "general-deploy",
        ["mission:deploy-crypto-dashboard", "project:crypto-income", "role:general", "type:mission"])

    create_event(DB_PATH, "memory.write",
        {"lesson": "Reuse: already know to use tar pipe + gh auth setup-git (from deploy-cv-it1st)",
         "context": "Applying prior deployment lessons to save time"},
        "general-deploy",
        ["mission:deploy-crypto-dashboard", "project:crypto-income", "role:general",
         "type:lesson", "domain:deployment"])

    create_event(DB_PATH, "memory.write",
        {"lesson": "PM2 is the simplest process manager for Node.js apps on hummingbot",
         "context": "Installed PM2, configured ecosystem.config.js"},
        "general-deploy",
        ["mission:deploy-crypto-dashboard", "project:crypto-income", "role:general",
         "type:lesson", "domain:deployment"])

    create_event(DB_PATH, "memory.write",
        {"metric": "Deploy time with prior knowledge", "value": "5 minutes (67% faster than first deploy)"},
        "general-deploy",
        ["mission:deploy-crypto-dashboard", "project:crypto-income", "role:general",
         "type:benchmark", "domain:deployment"])

    create_event(DB_PATH, "mission.complete",
        {"mission": "deploy-crypto-dashboard", "status": "success",
         "summary": "Dashboard live at crypto.it1st.com via PM2 + nginx"},
        "general-deploy",
        ["mission:deploy-crypto-dashboard", "project:crypto-income", "role:general", "type:mission"])

    print("  5 events written (1 start, 2 lessons, 1 benchmark, 1 complete)\n")

    # ── Mission 3: Model selection for colony ops ───────────────

    print("Creating Mission 3: model-selection")

    create_event(DB_PATH, "mission.start",
        {"mission": "model-selection", "project": "mycelium-ai-framework",
         "objective": "Benchmark free models for colony operations"},
        "scout-models",
        ["mission:model-selection", "project:mycelium-ai-framework", "role:scout", "type:mission"])

    create_event(DB_PATH, "memory.write",
        {"lesson": "mimo-v2-omni:free is the ONLY free model with vision+tool calling",
         "context": "Tested 8 free models, only omni supports multimodal tool results"},
        "scout-models",
        ["mission:model-selection", "project:mycelium-ai-framework", "role:scout",
         "type:lesson", "domain:model-selection"])

    create_event(DB_PATH, "memory.write",
        {"lesson": "OpenRouter free models are unreliable — rate-limited, return null content",
         "context": "Tested qwen3-coder:free and nemotron:free, both failed in automated tests"},
        "scout-models",
        ["mission:model-selection", "project:mycelium-ai-framework", "role:scout",
         "type:lesson", "domain:model-selection"])

    create_event(DB_PATH, "memory.write",
        {"pain_point": "Fallback chain broke when OpenRouter models returned null — automated tasks failed silently",
         "fix": "Removed OpenRouter from fallback chain, kept kilocode + copilot models"},
        "scout-models",
        ["mission:model-selection", "project:mycelium-ai-framework", "role:scout",
         "type:pain-point", "domain:model-selection"])

    create_event(DB_PATH, "memory.write",
        {"metric": "Models tested", "value": "8 free models, 2 passed full test suite"},
        "scout-models",
        ["mission:model-selection", "project:mycelium-ai-framework", "role:scout",
         "type:benchmark", "domain:model-selection"])

    create_event(DB_PATH, "mission.complete",
        {"mission": "model-selection", "status": "success",
         "summary": "mimo-v2-omni:free confirmed as best free model, fallback chain fixed"},
        "scout-models",
        ["mission:model-selection", "project:mycelium-ai-framework", "role:scout", "type:mission"])

    print("  6 events written (1 start, 2 lessons, 1 pain-point, 1 benchmark, 1 complete)\n")

    # ── Run Curator ─────────────────────────────────────────────

    print("=== Running Curator ===\n")

    missions = get_completed_missions(DB_PATH)
    print(f"Completed missions: {missions}\n")

    results = []
    for mission_id in missions:
        result = curate_mission(DB_PATH, mission_id, memory_root=MEMORY_ROOT)
        if result:
            results.append(result)

    # ── Show Generated Files ────────────────────────────────────

    print("\n=== Generated Memory Files ===\n")

    all_dirs = [
        ("missions", os.path.join(MEMORY_ROOT, "missions")),
        ("projects", os.path.join(MEMORY_ROOT, "projects")),
        ("lessons", os.path.join(MEMORY_ROOT, "lessons")),
        ("benchmarks", os.path.join(MEMORY_ROOT, "benchmarks")),
        ("agents", os.path.join(MEMORY_ROOT, "agents")),
    ]
    for dir_name, dir_path in all_dirs:
        if os.path.exists(dir_path):
            files = sorted(os.listdir(dir_path))
            if files:
                print(f"{dir_path}/")
                for f in files:
                    size = os.path.getsize(os.path.join(dir_path, f))
                    print(f"  {f} ({size} bytes)")
                print()

    # Show content of first mission file
    mission_file = os.path.join(MEMORY_ROOT, "missions", "deploy-cv-it1st.md")
    if os.path.exists(mission_file):
        print("=== deploy-cv-it1st.md (preview) ===\n")
        with open(mission_file) as f:
            print(f.read())

    # Show lessons file
    lessons_file = os.path.join(MEMORY_ROOT, "lessons", "deployment.md")
    if os.path.exists(lessons_file):
        print("=== lessons/deployment.md (preview) ===\n")
        with open(lessons_file) as f:
            print(f.read())

    # ── Summary ─────────────────────────────────────────────────

    print("=== Summary ===\n")
    total_events = sum(r["events"] for r in results)
    total_lessons = sum(r["lessons"] for r in results)
    print(f"Missions processed: {len(results)}")
    print(f"Total events: {total_events}")
    print(f"Total lessons extracted: {total_lessons}")
    print(f"\nThese files are now in {MEMORY_ROOT}/ and will be indexed by QMD")
    print("on next 'qmd update', making them searchable by future agents.")


if __name__ == "__main__":
    main()
