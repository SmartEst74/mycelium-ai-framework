"""
Mycium AI Framework — Core Orchestration (implemented)
"""

import yaml
import os
from pathlib import Path
from typing import List, Optional
from rhizomorph.lcm import Rhizomorph
from core.providers import AgentProvider, MockAgentProvider

FRAMEWORK_ROOT = Path(__file__).parent.parent


class Mycelium:
    """
    The brain. Reasons, routes, delegates. Never executes. Never sees.
    """

    def __init__(self, provider: Optional[AgentProvider] = None, rhizomorph_db: str = "./lcm.db"):
        self.provider = provider or MockAgentProvider()
        self.models = self._load_config("config/models.yaml")
        self.rules = self._load_config("config/rules.yaml")
        self.registry = self._load_registry()
        self.rhizo = Rhizomorph(rhizomorph_db)

    def _load_config(self, path):
        with open(FRAMEWORK_ROOT / path) as f:
            return yaml.safe_load(f)

    def _load_registry(self):
        roles = {}
        roles_dir = FRAMEWORK_ROOT / "registry" / "roles"
        # Load roles from subdirectories (e.g., design/, marketing/)
        for dept_dir in roles_dir.iterdir():
            if dept_dir.is_dir():
                dept = dept_dir.name
                roles[dept] = []
                for role_file in dept_dir.glob("*.md"):
                    roles[dept].append(role_file.stem)
        # Also load roles directly in roles/ (e.g., engineering-*.md)
        root_roles = []
        for role_file in roles_dir.glob("*.md"):
            root_roles.append(role_file.stem)
        if root_roles:
            roles["engineering"] = root_roles
        return roles

    def get_model_for_role(self, role):
        return self.models["roles"].get(role, {}).get("id")

    def get_model_for_task(self, task_type):
        matrix = self.models.get("task_matrix", {})
        task = matrix.get(task_type, matrix.get("research"))
        return task["primary"] if task else self.models["roles"]["dynamic"]["id"]

    def find_agent_role(self, capability):
        for dept, roles in self.registry.items():
            for role in roles:
                if capability.lower() in role.lower():
                    return {"department": dept, "role": role}
        return None

    def check_colony_health(self):
        """Query Rhizomorph for mission-related events and summarize."""
        health = {"status": "healthy", "active_missions": 0, "completed_missions": 0, "pain_points": 0, "green_leaves": 0, "recent_benchmarks": 0}
        # count events by tag
        missions = self.rhizo.get_events_by_tag("#mission", limit=100)
        completed = self.rhizo.get_events_by_tag("#mission-complete", limit=100)
        pain = self.rhizo.get_events_by_tag("#pain-point", limit=100)
        green = self.rhizo.get_events_by_tag("#green-leaf", limit=100)
        bench = self.rhizo.get_events_by_tag("#benchmark", limit=100)

        health.update({
            "active_missions": len(missions),
            "completed_missions": len(completed),
            "pain_points": len(pain),
            "green_leaves": len(green),
            "recent_benchmarks": len(bench),
        })
        return health

    def execute_mission(self, mission: str, capabilities: List[str] = None):
        """Create a mission event, delegate to ArmyAnt, return dispatch summary."""
        capabilities = capabilities or ["frontend", "design"]
        # write mission start to rhizomorph
        seq = self.rhizo.emit("memory.write", {"mission": mission}, agent="mycelium", tags=["#mission"])
        army = ArmyAnt(self, provider=self.provider)
        team = army.build_team(mission, capabilities)
        dispatch = army.coordinate(team["team"], mission)
        return {"mission": mission, "rhizo_seq": seq, "dispatch": dispatch}


class Scout:
    def __init__(self, mycelium: Mycelium):
        self.mycelium = mycelium
        self.model = mycelium.get_model_for_role("scout")
        self.provider = mycelium.provider
        self.rhizo = mycelium.rhizo

    def research_models(self, query: str):
        task = f"research free models for: {query}"
        resp = self.provider.spawn_agent(self.model, task)
        # write result to rhizomorph
        tags = resp.get("tags", ["#benchmark"]) if isinstance(resp, dict) else ["#benchmark"]
        self.rhizo.emit("memory.write", {"query": query, "result": resp}, agent="scout", tags=tags)
        return resp

    def find_opportunities(self, domain: str):
        task = f"opportunity scan: {domain}"
        resp = self.provider.spawn_agent(self.model, task)
        tags = resp.get("tags", ["#green-leaf"]) if isinstance(resp, dict) else ["#green-leaf"]
        self.rhizo.emit("memory.write", {"domain": domain, "result": resp}, agent="scout", tags=tags)
        return resp


class ArmyAnt:
    def __init__(self, mycelium: Mycelium, provider: Optional[AgentProvider] = None):
        self.mycelium = mycelium
        self.provider = provider or mycelium.provider
        self.model = mycelium.get_model_for_role("army")
        self.rhizo = mycelium.rhizo

    def build_team(self, mission: str, required_capabilities: List[str]):
        team = []
        for cap in required_capabilities:
            role = self.mycelium.find_agent_role(cap)
            model = self.mycelium.get_model_for_task(cap)
            team.append({"role": role, "model": model, "capability": cap})
        # write team plan to rhizomorph
        self.rhizo.emit("memory.write", {"mission": mission, "team": team}, agent="army", tags=["#mission"])
        return {"team": team}

    def coordinate(self, team: List[dict], mission: str):
        results = []
        for member in team:
            role = member.get("role") or {"role": "unknown"}
            model = member.get("model")
            cap = member.get("capability")
            task = f"Execute {cap} for mission: {mission}"
            ant = DynamicAnt(role, model, task, provider=self.provider, rhizo=self.rhizo)
            res = ant.execute()
            results.append(res)
        # emit coordination complete
        self.rhizo.emit("memory.write", {"mission": mission, "coordinated": True}, agent="army", tags=["#mission"])
        return results


class DynamicAnt:
    def __init__(self, role, model, task, provider: Optional[AgentProvider] = None, rhizo: Optional[Rhizomorph] = None):
        self.role = role
        self.model = model
        self.task = task
        self.provider = provider or MockAgentProvider()
        self.rhizo = rhizo or Rhizomorph()

    def execute(self):
        # write mission start
        self.rhizo.emit("memory.write", {"task": self.task, "role": self.role}, agent=str(self.role), tags=["#mission"])
        resp = self.provider.spawn_agent(self.model, self.task)
        # if provider returned error, write pain-point
        tags = resp.get("tags", []) if isinstance(resp, dict) else []
        if isinstance(resp, dict) and resp.get("result", {}).get("error"):
            self.rhizo.emit("memory.write", {"task": self.task, "error": resp}, agent=str(self.role), tags=["#pain-point"])
            return {"role": self.role, "status": "failed", "resp": resp}

        # normal completion
        self.rhizo.emit("memory.write", {"task": self.task, "result": resp}, agent=str(self.role), tags=["#mission-complete"])
        return {"role": self.role, "status": "completed", "resp": resp}


# CLI entrypoint support
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    m = sub.add_parser("mission")
    m.add_argument("mission")
    m.add_argument("--provider", default="mock")
    sub.add_parser("health")
    s = sub.add_parser("scout")
    s.add_argument("query")

    args = parser.parse_args()
    provider = MockAgentProvider() if getattr(args, "provider", "mock") == "mock" else None
    brain = Mycelium(provider=provider)
    if args.cmd == "mission":
        print(brain.execute_mission(args.mission))
    elif args.cmd == "health":
        print(brain.check_colony_health())
    elif args.cmd == "scout":
        sc = Scout(brain)
        print(sc.research_models(args.query))

