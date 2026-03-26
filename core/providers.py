from typing import Protocol, Dict, Any, Optional, List
import os
import json
from pathlib import Path
import uuid
import requests


class AgentProvider(Protocol):
    """Interface for spawning and managing AI agents."""

    def spawn_agent(self, model: str, task: str, system_prompt: str = "") -> Dict[str, Any]:
        """Spawn an agent with a model and task. Returns {session_id, result}."""
        ...

    def get_agent_status(self, session_id: str) -> Dict[str, Any]:
        """Check status of a spawned agent."""
        ...


class MockAgentProvider:
    """A lightweight provider for tests and local runs.

    It returns canned responses based on simple keyword matching in the task.
    """

    def __init__(self):
        # store sessions in memory
        self.sessions = {}

    def spawn_agent(self, model: str, task: str, system_prompt: str = "") -> Dict[str, Any]:
        sid = str(uuid.uuid4())
        # simple canned logic
        lower = task.lower()
        if "research" in lower or "compare" in lower or "benchmark" in lower:
            result = {"summary": "found 3 free models", "details": ["model-a", "model-b", "model-c"]}
            tags = ["#benchmark"]
        elif "opportunity" in lower or "green-leaf" in lower or "revenue" in lower:
            result = {"summary": "found 2 opportunities", "details": ["affiliate", "ad"]}
            tags = ["#green-leaf"]
        elif "fail" in lower or "error" in lower or "blocked" in lower:
            result = {"error": "blocked by missing creds"}
            tags = ["#pain-point"]
        else:
            result = {"ok": True, "notes": "task completed"}
            tags = ["#mission-complete"]

        self.sessions[sid] = {"model": model, "task": task, "result": result, "status": "completed", "tags": tags}
        return {"session_id": sid, "result": result, "tags": tags}

    def get_agent_status(self, session_id: str) -> Dict[str, Any]:
        return self.sessions.get(session_id, {"status": "unknown"})


class OpenClawAgentProvider:
    """Provider that talks to an OpenClaw gateway REST API running locally.

    It expects a ~/.openclaw/openclaw.json file for configuration but will
    fall back to http://localhost:3456 as the gateway.
    """

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        cfg = {}
        try:
            with open(config_path) as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
        self.gateway = cfg.get("gateway_url") or os.environ.get("OPENCLAW_GATEWAY") or "http://localhost:3456"

    def spawn_agent(self, model: str, task: str, system_prompt: str = "") -> Dict[str, Any]:
        url = f"{self.gateway}/sessions_spawn"
        payload = {"task": task, "model": model, "agentId": "auto", "thinking": system_prompt}
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_agent_status(self, session_id: str) -> Dict[str, Any]:
        url = f"{self.gateway}/sessions/{session_id}"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

