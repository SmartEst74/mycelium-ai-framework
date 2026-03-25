"""
Rhizomorph — Lossless Context Management Layer

The underground network that connects all colony members. Provides:
- Event sourcing (append-only SQLite log)
- Real-time event propagation
- State reconstruction via replay
- Deterministic replay for testing

Biological analog: the rhizomorph connects individual fungi into a
networked organism — each node can communicate, share resources, and
collectively respond to the environment.
"""

import sqlite3
import json
import time
import threading
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class Event:
    """An immutable event in the colony's nervous system."""
    type: str
    payload: dict
    sequence: int = 0
    timestamp: str = ""
    agent: str = ""
    tags: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class Rhizomorph:
    """
    Lossless Context Management (LCM) engine.

    The Rhizomorph is the persistence layer of the Mycelium framework.
    It provides:
    1. Event store (append-only SQLite, WAL mode)
    2. Real-time event bus (subscribers + notifications)
    3. Replay engine (state reconstruction from event log)
    4. Checkpoint system (snapshots for fast recovery)

    Usage:
        rhy = Rhizomorph("/path/to/lcm.db")
        rhy.on("memory.write", handle_lesson)
        rhy.emit("memory.write", {"tag": "#lesson", "content": "..."})
        state = rhy.replay(from_seq=0, callback=apply_event)
    """

    def __init__(self, db_path: str = "lcm.db", auto_checkpoint: bool = True):
        self.db_path = db_path
        self.auto_checkpoint = auto_checkpoint
        self._subscribers: Dict[str, List[Callable]] = {}
        self._replaying = False  # flag to suppress side-effects during replay
        self._init_store()

    # ── Persistence ──────────────────────────────────────────────

    def _init_store(self):
        """Initialize the event store with WAL mode for durability."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]'
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def _now(self) -> str:
        """ISO-8601 timestamp in UTC."""
        return datetime.now(timezone.utc).isoformat()

    # ── Core Operations ──────────────────────────────────────────

    def emit(self, event_type: str, payload: dict,
             agent: str = "", tags: Optional[List[str]] = None) -> int:
        """
        Emit an event into the colony's nervous system.

        The event is persisted (append-only), then delivered to all
        matching subscribers synchronously.

        Args:
            event_type: Event type (e.g., "memory.write", "mission.start")
            payload: Arbitrary JSON-serializable data
            agent: Source agent name (for audit trail)
            tags: Optional tags for indexing

        Returns:
            Sequence number of the emitted event
        """
        if self._replaying:
            # During replay, don't persist — just notify (for state rebuild)
            return 0

        tags = tags or []
        timestamp = self._now()

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO events (type, payload, timestamp, agent, tags) VALUES (?, ?, ?, ?, ?)",
                (event_type, json.dumps(payload), timestamp, agent, json.dumps(tags))
            )
            sequence = cur.lastrowid
            conn.commit()

        # Notify subscribers
        self._notify(event_type, payload, sequence, timestamp, agent, tags)
        return sequence

    def on(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def off(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb is not callback
            ]

    def _notify(self, event_type: str, payload: dict,
                sequence: int, timestamp: str, agent: str, tags: List[str]) -> None:
        """Deliver an event to all matching subscribers."""
        event = Event(event_type, payload, sequence, timestamp, agent, tags)
        for cb in self._subscribers.get(event_type, []):
            try:
                cb(event)
            except Exception as e:
                # Log but don't crash — one subscriber failing shouldn't kill the bus
                print(f"[Rhizomorph] Subscriber error on {event_type}: {e}")

    # ── Replay & Recovery ────────────────────────────────────────

    def replay(self, from_sequence: int = 0,
               callback: Optional[Callable] = None,
               to_sequence: Optional[int] = None) -> List[Event]:
        """
        Replay events from the event log.

        This is the core disaster recovery mechanism. A fresh agent can
        reconstruct its state by replaying events from sequence 0.

        Args:
            from_sequence: Start replaying from this sequence number
            callback: Called for each event during replay
            to_sequence: Optional end sequence (None = latest)

        Returns:
            List of replayed Event objects
        """
        self._replaying = True
        events = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                if to_sequence is not None:
                    cur = conn.execute(
                        "SELECT type, payload, sequence, timestamp, agent, tags FROM events "
                        "WHERE sequence >= ? AND sequence <= ? ORDER BY sequence ASC",
                        (from_sequence, to_sequence)
                    )
                else:
                    cur = conn.execute(
                        "SELECT type, payload, sequence, timestamp, agent, tags FROM events "
                        "WHERE sequence >= ? ORDER BY sequence ASC",
                        (from_sequence,)
                    )

                for row in cur:
                    event_type, payload_json, seq, ts, agent, tags_json = row
                    payload = json.loads(payload_json)
                    tags = json.loads(tags_json)
                    event = Event(event_type, payload, seq, ts, agent, tags)
                    events.append(event)

                    if callback:
                        try:
                            callback(event)
                        except Exception as e:
                            print(f"[Rhizomorph] Replay callback error on #{seq}: {e}")

                    # Also notify subscribers during replay (for state rebuild)
                    self._notify(event_type, payload, seq, ts, agent, tags)
        finally:
            self._replaying = False

        return events

    def replay_range(self, start_seq: int, end_seq: int,
                     callback: Optional[Callable] = None) -> List[Event]:
        """Replay events in a specific sequence range."""
        return self.replay(from_sequence=start_seq, to_sequence=end_seq, callback=callback)

    # ── Checkpoints ──────────────────────────────────────────────

    def checkpoint(self, name: str, state: dict) -> int:
        """
        Save a checkpoint (snapshot of current state).

        Used for fast recovery — instead of replaying all events,
        restore from the latest checkpoint and replay only recent events.
        """
        sequence = self.get_sequence()
        timestamp = self._now()

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO checkpoints (name, sequence, state, timestamp) VALUES (?, ?, ?, ?)",
                (name, sequence, json.dumps(state), timestamp)
            )
            checkpoint_id = cur.lastrowid
            conn.commit()

        return checkpoint_id

    def restore_checkpoint(self, name: str) -> Optional[dict]:
        """Restore the latest checkpoint for a given name."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT sequence, state FROM checkpoints WHERE name = ? ORDER BY sequence DESC LIMIT 1",
                (name,)
            )
            row = cur.fetchone()
            if row:
                sequence, state_json = row
                return {
                    "sequence": sequence,
                    "state": json.loads(state_json),
                }
        return None

    def get_checkpoint_events(self, name: str) -> List[Event]:
        """Get events since the last checkpoint (for incremental replay)."""
        checkpoint = self.restore_checkpoint(name)
        if checkpoint:
            return self.replay(from_sequence=checkpoint["sequence"] + 1)
        return self.replay(from_sequence=0)

    # ── Queries ──────────────────────────────────────────────────

    def get_sequence(self) -> int:
        """Get the latest event sequence number."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT MAX(sequence) FROM events")
            row = cur.fetchone()
            return row[0] or 0

    def get_events_by_type(self, event_type: str,
                           limit: int = 100) -> List[Event]:
        """Get recent events of a specific type."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT type, payload, sequence, timestamp, agent, tags FROM events "
                "WHERE type = ? ORDER BY sequence DESC LIMIT ?",
                (event_type, limit)
            )
            events = []
            for row in cur:
                event_type, payload_json, seq, ts, agent, tags_json = row
                tags = json.loads(tags_json)
                events.append(Event(event_type, json.loads(payload_json), seq, ts, agent, tags))
            return events

    def get_events_by_tag(self, tag: str, limit: int = 100) -> List[Event]:
        """Get events with a specific tag."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT type, payload, sequence, timestamp, agent, tags FROM events "
                "ORDER BY sequence DESC LIMIT 500"
            )
            events = []
            for row in cur:
                event_type, payload_json, seq, ts, agent, tags_json = row
                tags = json.loads(tags_json)
                if tag in tags:
                    events.append(Event(event_type, json.loads(payload_json), seq, ts, agent, tags))
                if len(events) >= limit:
                    break
            return events

    def get_events_since(self, minutes: int = 60) -> List[Event]:
        """Get events from the last N minutes."""
        cutoff = datetime.now(timezone.utc).timestamp() - (minutes * 60)
        cutoff_iso = datetime.fromtimestamp(cutoff, tz=timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT type, payload, sequence, timestamp, agent, tags FROM events "
                "WHERE timestamp >= ? ORDER BY sequence ASC",
                (cutoff_iso,)
            )
            events = []
            for row in cur:
                event_type, payload_json, seq, ts, agent, tags_json = row
                tags = json.loads(tags_json)
                events.append(Event(event_type, json.loads(payload_json), seq, ts, agent, tags))
            return events

    def event_count(self) -> int:
        """Total number of events in the store."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM events")
            return cur.fetchone()[0]

    # ── Metrics ──────────────────────────────────────────────────

    def health(self) -> dict:
        """Health check for the Rhizomorph."""
        try:
            seq = self.get_sequence()
            count = self.event_count()
            return {
                "status": "healthy",
                "db_path": self.db_path,
                "total_events": count,
                "latest_sequence": seq,
                "subscribers": {k: len(v) for k, v in self._subscribers.items()},
                "replaying": self._replaying,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }
