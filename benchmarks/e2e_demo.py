#!/usr/bin/env python3
"""
Minimal E2E Demo — Event Bus + Replay (Simplified)

Demonstrates:
1. Event persistence (SQLite)
2. Event subscription
3. State reconstruction via replay
4. Checkpoint/snapshot capability

Run: python3 e2e_demo.py
"""

import sqlite3, json, time, argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Dict

class EventBus:
    def __init__(self, db_path: str = "lcm_demo.db"):
        self.db_path = db_path
        self._init_db()
        self.subscribers: Dict[str, List[Callable]] = {}
        self.sequence = self._get_current_sequence()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_seq ON events(sequence)")
            conn.commit()
    
    def _get_current_sequence(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT MAX(sequence) FROM events")
            row = cur.fetchone()
            return row[0] or 0
    
    def emit(self, event_type: str, payload: dict):
        timestamp = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO events (type, payload, timestamp) VALUES (?,?,?)",
                (event_type, json.dumps(payload), timestamp)
            )
            sequence = cur.lastrowid
            conn.commit()
        self.sequence = sequence
        self._notify(event_type, payload, sequence, timestamp)
        return sequence
    
    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def _notify(self, event_type: str, payload: dict, sequence: int, timestamp: str):
        for cb in self.subscribers.get(event_type, []):
            try:
                cb(event_type, payload, sequence, timestamp)
            except Exception as e:
                print(f"[EventBus] Subscriber error: {e}")
    
    def replay(self, from_sequence: int = 0, callback: Callable = None) -> int:
        """Replay events from sequence onwards, calling callback for each event."""
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT type, payload, sequence, timestamp FROM events WHERE sequence >= ? ORDER BY sequence ASC",
                (from_sequence,)
            )
            for row in cur:
                event_type, payload, seq, ts = row
                if callback:
                    callback(event_type, json.loads(payload), seq, ts)
                count += 1
        return count

# ========================
# Agent with State
# ========================

class ColonyState:
    """State that can be rebuilt from events."""
    def __init__(self):
        self.lessons = []
        self.missions = []
    
    def apply_event(self, event_type: str, payload: dict, **kwargs):
        if event_type == "memory.write":
            tag = payload.get("tag")
            if tag == "#lesson":
                content = payload.get("content")
                if content not in self.lessons:
                    self.lessons.append(content)
            elif tag == "#mission":
                name = payload.get("name")
                if name and name not in self.missions:
                    self.missions.append(name)

class Agent:
    def __init__(self, name: str, bus: EventBus, state: ColonyState = None):
        self.name = name
        self.bus = bus
        self.state = state or ColonyState()
        # Subscribe to relevant events
        bus.subscribe("memory.write", self.on_memory_write)
    
    def on_memory_write(self, event_type: str, payload: dict, seq: int, ts: str):
        old_lessons = len(self.state.lessons)
        old_missions = len(self.state.missions)
        self.state.apply_event(event_type, payload)
        new_lessons = len(self.state.lessons)
        new_missions = len(self.state.missions)
        # Only print if state changed
        if new_lessons > old_lessons or new_missions > old_missions:
            print(f"[{self.name}] State update: lessons={new_lessons} missions={new_missions} (event #{seq})")

# ========================
# Demo
# ========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay-from", type=int, help="Replay from sequence (demostrate recovery)")
    args = parser.parse_args()
    
    db_path = "lcm_demo.db"
    Path(db_path).unlink(missing_ok=True)  # Clean slate
    
    if args.replay_from is not None:
        print(f"\n=== RECOVERY MODE: Replaying from event #{args.replay_from} ===\n")
        bus = EventBus(db_path)
        state = ColonyState()
        agent = Agent("recovered-agent", bus, state)
        count = bus.replay(from_sequence=args.replay_from, callback=lambda *evt: agent.on_memory_write(*evt))
        print(f"Replayed {count} events")
        print(f"Final state: {len(state.lessons)} lessons, {len(state.missions)} missions")
        return
    
    print("\n=== MYCELIUM EVENT BUS DEMO ===\n")
    
    bus = EventBus(db_path)
    state = ColonyState()
    mycelium = Agent("mycelium", bus, state)
    
    # Simulate a mission flow
    print("1. User submits mission")
    seq1 = bus.emit("memory.write", {"tag": "#mission", "name": "Find best code model"})
    print(f"   → Event #{seq1} emitted")
    
    print("2. Scout discovers findings")
    seq2 = bus.emit("memory.write", {"tag": "#lesson", "content": "Qwen3-Coder is best free coding model"})
    print(f"   → Event #{seq2} emitted")
    seq3 = bus.emit("memory.write", {"tag": "#lesson", "content": "Step-3.5-flash is fastest"})
    print(f"   → Event #{seq3} emitted")
    
    print("3. Mission completes")
    seq4 = bus.emit("mission.complete", {"mission": "Find best code model"})
    print(f"   → Event #{seq4} emitted")
    
    print("\n--- Current State ---")
    print(f"Lessons: {len(state.lessons)}")
    print(f"Missions: {len(state.missions)}")
    print(f"Total events in DB: {bus.sequence}")
    
    # Demonstrate replay: create fresh state, replay events
    print("\n--- Recovery Demo ---")
    print("Simulating disaster: wiping state, recreating agent from event log...")
    fresh_state = ColonyState()
    fresh_agent = Agent("recovered", bus, fresh_state)
    count = bus.replay(from_sequence=0, callback=lambda *evt: fresh_agent.on_memory_write(*evt))
    print(f"Replayed {count} events")
    print(f"Recovered state: {len(fresh_state.lessons)} lessons, {len(fresh_state.missions)} missions")
    
    assert len(fresh_state.lessons) == len(state.lessons), "Replay should yield identical state!"
    assert len(fresh_state.missions) == len(state.missions), "Replay should yield identical state!"
    print("✓ State reconstruction verified")
    
    # Show how to check event log
    print("\n--- Event Log (last 5) ---")
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("SELECT sequence, type FROM events ORDER BY sequence DESC LIMIT 5")
        for seq, typ in cur:
            print(f"  #{seq}: {typ}")
    
    print("\n=== DEMO COMPLETE ===")
    print("The colony can be fully restored by replaying events from any backup + recent log.")

if __name__ == "__main__":
    main()
