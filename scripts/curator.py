#!/usr/bin/env python3
"""
Mycelium Colonial Memory Curator

Reads events from the Rhizomorph event bus, extracts durable knowledge
by tag (lessons, pain-points, benchmarks), and writes curated markdown
to memory/ directories for QMD indexing.

Usage:
    python3 scripts/curator.py                    # process all completed missions
    python3 scripts/curator.py --mission <id>     # process specific mission
    python3 scripts/curator.py --dry-run          # show what would be written
"""

import sqlite3
import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ── Defaults ────────────────────────────────────────────────────

DEFAULT_DB = os.environ.get("RHIZOMORPH_DB", "/tmp/mycelium-ai-framework/benchmarks/lcm_demo.db")
MEMORY_ROOT = os.environ.get("MYCELIUM_MEMORY", "/tmp/mycelium-ai-framework/memory")
MEMORY_DIRS = {
    "missions":  os.path.join(MEMORY_ROOT, "missions"),
    "projects":  os.path.join(MEMORY_ROOT, "projects"),
    "lessons":   os.path.join(MEMORY_ROOT, "lessons"),
    "benchmarks": os.path.join(MEMORY_ROOT, "benchmarks"),
    "agents":    os.path.join(MEMORY_ROOT, "agents"),
}

# ── Event Extraction ───────────────────────────────────────────

def get_completed_missions(db_path: str) -> List[str]:
    """Find all missions that have a mission.complete event."""
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT payload FROM events WHERE type = 'mission.complete' "
            "ORDER BY sequence ASC"
        )
        return [json.loads(row[0]).get("mission", "unknown") for row in cur]


def get_mission_events(db_path: str, mission_id: str) -> List[Dict]:
    """Get all events tagged with a specific mission."""
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT type, payload, sequence, timestamp, agent, tags "
            "FROM events ORDER BY sequence ASC"
        )
        events = []
        mission_tag = f"mission:{mission_id}"
        for row in cur:
            event_type, payload_json, seq, ts, agent, tags_json = row
            tags = json.loads(tags_json)
            if mission_tag in tags:
                events.append({
                    "type": event_type,
                    "payload": json.loads(payload_json),
                    "sequence": seq,
                    "timestamp": ts,
                    "agent": agent,
                    "tags": tags,
                })
        return events


def extract_by_tag(events: List[Dict], tag_prefix: str) -> List[Dict]:
    """Extract events matching a tag prefix (e.g., 'type:lesson')."""
    return [e for e in events if any(t.startswith(tag_prefix) for t in e.get("tags", []))]


def extract_metadata(events: List[Dict]) -> Dict:
    """Extract mission metadata from events."""
    meta = {
        "mission_id": "unknown",
        "project": None,
        "started": None,
        "completed": None,
        "agents": set(),
        "event_count": len(events),
    }
    for e in events:
        meta["agents"].add(e.get("agent", "unknown"))
        if e["type"] == "mission.start":
            meta["mission_id"] = e["payload"].get("mission", meta["mission_id"])
            meta["started"] = e["timestamp"]
            meta["project"] = e["payload"].get("project")
        elif e["type"] == "mission.complete":
            meta["completed"] = e["timestamp"]
        # Extract from tags
        for tag in e.get("tags", []):
            if tag.startswith("mission:"):
                meta["mission_id"] = tag.split(":", 1)[1]
            elif tag.startswith("project:"):
                meta["project"] = tag.split(":", 1)[1]
    meta["agents"] = sorted(meta["agents"])
    return meta


# ── Markdown Generation ─────────────────────────────────────────

def format_mission_memory(meta: Dict, events: List[Dict],
                          lessons: List[Dict], pain_points: List[Dict],
                          benchmarks: List[Dict]) -> str:
    """Generate curated markdown for a mission memory file."""
    lines = []
    now = datetime.now(timezone.utc).isoformat()

    # Frontmatter
    lines.append("---")
    lines.append(f"mission: {meta['mission_id']}")
    if meta["project"]:
        lines.append(f"project: {meta['project']}")
    lines.append(f"curated: {now}")
    lines.append(f"event_count: {meta['event_count']}")
    lines.append(f"agents: [{', '.join(meta['agents'])}]")
    tags = set()
    for e in events:
        for t in e.get("tags", []):
            if ":" not in t or t.startswith(("mission:", "project:")):
                continue
            tags.add(t)
    lines.append(f"tags: [{', '.join(sorted(tags))}]")
    lines.append("---")
    lines.append("")

    # Title
    lines.append(f"# Mission: {meta['mission_id']}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Project:** {meta.get('project', 'N/A')}")
    lines.append(f"- **Started:** {meta.get('started', 'N/A')}")
    lines.append(f"- **Completed:** {meta.get('completed', 'N/A')}")
    lines.append(f"- **Events:** {meta['event_count']}")
    lines.append(f"- **Agents:** {', '.join(meta['agents'])}")
    lines.append("")

    # Lessons
    if lessons:
        lines.append("## Lessons Learned")
        lines.append("")
        for e in lessons:
            lesson = e["payload"].get("lesson", e["payload"].get("message", json.dumps(e["payload"])))
            agent = e.get("agent", "unknown")
            lines.append(f"- **[{agent}]** {lesson}")
        lines.append("")

    # Pain Points
    if pain_points:
        lines.append("## Pain Points")
        lines.append("")
        for e in pain_points:
            pain = e["payload"].get("pain_point", e["payload"].get("message", json.dumps(e["payload"])))
            agent = e.get("agent", "unknown")
            lines.append(f"- **[{agent}]** {pain}")
        lines.append("")

    # Benchmarks
    if benchmarks:
        lines.append("## Benchmarks")
        lines.append("")
        for e in benchmarks:
            metric = e["payload"].get("metric", json.dumps(e["payload"]))
            value = e["payload"].get("value", "")
            agent = e.get("agent", "unknown")
            if value:
                lines.append(f"- **{metric}:** {value} (by {agent})")
            else:
                lines.append(f"- **[{agent}]** {metric}")
        lines.append("")

    # Timeline
    lines.append("## Event Timeline")
    lines.append("")
    lines.append("| Seq | Time | Agent | Type | Summary |")
    lines.append("|-----|------|-------|------|---------|")
    for e in events:
        ts = e.get("timestamp", "—")[:19]
        agent = e.get("agent", "—")
        etype = e["type"]
        summary = json.dumps(e["payload"], ensure_ascii=False)[:80]
        lines.append(f"| {e['sequence']} | {ts} | {agent} | {etype} | {summary} |")
    lines.append("")

    return "\n".join(lines)


def format_lesson_file(mission_id: str, project: str, lessons: List[Dict]) -> str:
    """Append lessons to the cross-cutting lessons file."""
    lines = []
    lines.append("")
    lines.append(f"### From mission `{mission_id}` (project: {project})")
    lines.append("")
    for e in lessons:
        lesson = e["payload"].get("lesson", e["payload"].get("message", json.dumps(e["payload"])))
        agent = e.get("agent", "unknown")
        domain = "general"
        for tag in e.get("tags", []):
            if tag.startswith("domain:"):
                domain = tag.split(":", 1)[1]
                break
        lines.append(f"- **[{domain}]** {lesson} — *{agent}*")
    lines.append("")
    return "\n".join(lines)


# ── File Operations ─────────────────────────────────────────────

def ensure_dirs():
    """Create memory directory structure."""
    for path in MEMORY_DIRS.values():
        os.makedirs(path, exist_ok=True)


def write_mission_memory(meta: Dict, content: str, dry_run: bool = False) -> str:
    """Write mission memory file."""
    mission_id = meta["mission_id"]
    path = os.path.join(MEMORY_DIRS["missions"], f"{mission_id}.md")
    if dry_run:
        print(f"[DRY RUN] Would write {len(content)} bytes to {path}")
    else:
        with open(path, "w") as f:
            f.write(content)
        print(f"✓ Wrote {len(content)} bytes to {path}")
    return path


def update_lessons_index(mission_id: str, project: str, lessons: List[Dict],
                          dry_run: bool = False, lessons_dir: str = None):
    """Append lessons to cross-cutting lessons/colony-ops.md or domain-specific file."""
    if not lessons:
        return

    if lessons_dir is None:
        lessons_dir = MEMORY_DIRS["lessons"]

    # Group by domain
    by_domain = {}
    for e in lessons:
        domain = "general"
        for tag in e.get("tags", []):
            if tag.startswith("domain:"):
                domain = tag.split(":", 1)[1]
                break
        by_domain.setdefault(domain, []).append(e)

    for domain, domain_lessons in by_domain.items():
        path = os.path.join(lessons_dir, f"{domain}.md")
        content = format_lesson_file(mission_id, project, domain_lessons)

        if dry_run:
            print(f"[DRY RUN] Would append to {path}")
        else:
            # If file exists, append; otherwise create with header
            if os.path.exists(path):
                with open(path, "a") as f:
                    f.write(content)
            else:
                with open(path, "w") as f:
                    f.write(f"# Lessons: {domain.title()}\n")
                    f.write(content)
            print(f"✓ Updated {path}")


# ── Main ────────────────────────────────────────────────────────

def curate_mission(db_path: str, mission_id: str, dry_run: bool = False,
                   memory_root: str = None):
    """Curate a single mission's events into memory files."""
    if memory_root is None:
        memory_root = MEMORY_ROOT

    memory_dirs = {
        "missions":  os.path.join(memory_root, "missions"),
        "projects":  os.path.join(memory_root, "projects"),
        "lessons":   os.path.join(memory_root, "lessons"),
        "benchmarks": os.path.join(memory_root, "benchmarks"),
        "agents":    os.path.join(memory_root, "agents"),
    }
    for path in memory_dirs.values():
        os.makedirs(path, exist_ok=True)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Curating mission: {mission_id}")
    print(f"  DB: {db_path}")

    # Get events
    events = get_mission_events(db_path, mission_id)
    if not events:
        print(f"  No events found for mission {mission_id}")
        return

    print(f"  Events: {len(events)}")

    # Extract metadata
    meta = extract_metadata(events)
    meta["mission_id"] = mission_id

    # Extract by type
    lessons = extract_by_tag(events, "type:lesson")
    pain_points = extract_by_tag(events, "type:pain-point")
    benchmarks = extract_by_tag(events, "type:benchmark")

    print(f"  Lessons: {len(lessons)}, Pain points: {len(pain_points)}, Benchmarks: {len(benchmarks)}")

    # Generate mission memory file
    content = format_mission_memory(meta, events, lessons, pain_points, benchmarks)
    path = os.path.join(memory_dirs["missions"], f"{mission_id}.md")
    if dry_run:
        print(f"[DRY RUN] Would write {len(content)} bytes to {path}")
    else:
        with open(path, "w") as f:
            f.write(content)
        print(f"✓ Wrote {len(content)} bytes to {path}")

    # Update cross-cutting lesson files
    update_lessons_index(mission_id, meta.get("project", ""), lessons,
                         dry_run, lessons_dir=memory_dirs["lessons"])

    return {
        "mission_id": mission_id,
        "events": len(events),
        "lessons": len(lessons),
        "pain_points": len(pain_points),
        "benchmarks": len(benchmarks),
    }


def main():
    parser = argparse.ArgumentParser(description="Mycelium Colonial Memory Curator")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to event bus database")
    parser.add_argument("--mission", help="Process a specific mission ID")
    parser.add_argument("--memory-root", default=MEMORY_ROOT, help="Root directory for memory files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be written")
    args = parser.parse_args()

    # Set up dirs
    memory_root = args.memory_root
    memory_dirs = {
        "missions":  os.path.join(memory_root, "missions"),
        "projects":  os.path.join(memory_root, "projects"),
        "lessons":   os.path.join(memory_root, "lessons"),
        "benchmarks": os.path.join(memory_root, "benchmarks"),
        "agents":    os.path.join(memory_root, "agents"),
    }

    # Ensure dirs exist
    for path in memory_dirs.values():
        os.makedirs(path, exist_ok=True)

    # Determine missions to process
    if args.mission:
        missions = [args.mission]
    else:
        missions = get_completed_missions(args.db)
        if not missions:
            print("No completed missions found in event bus.")
            sys.exit(0)

    print(f"=== Mycelium Colonial Memory Curator ===")
    print(f"Event bus: {args.db}")
    print(f"Missions to process: {len(missions)}")
    print(f"Memory root: {memory_root}")
    print()

    # Process each mission
    results = []
    for mission_id in missions:
        result = curate_mission(args.db, mission_id, args.dry_run,
                               memory_root=memory_root)
        if result:
            results.append(result)

    # Summary
    print(f"\n=== Summary ===")
    total_events = sum(r["events"] for r in results)
    total_lessons = sum(r["lessons"] for r in results)
    print(f"Missions processed: {len(results)}")
    print(f"Total events: {total_events}")
    print(f"Total lessons extracted: {total_lessons}")
    print(f"Memory files in: {memory_root}/")


if __name__ == "__main__":
    main()
