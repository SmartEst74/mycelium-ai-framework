"""
Mycium AI Framework — Core Orchestration

Biological model:
  Mycelium (Brain) = mimo-v2-pro (1M context, no vision — needs memory not eyes)
  Scout (Sensor) = step-3.5-flash (fast/cheap — probes and reports)
  Army (Coordinators) = mimo-v2-pro (1M context — needs registry state)
  Dynamic (Workers) = mimo-v2-omni (vision+tools — the eyes and hands)

Shared Memory (QMD) = colony's nervous system. Every agent reads/writes it.

Usage:
  from core.mycelium import Mycelium, ArmyAnt, DynamicAnt
  brain = Mycelium()
  army = ArmyAnt(brain)
  result = brain.execute_mission("Build a landing page for IT1st")
"""

import yaml
import os
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).parent.parent


class Mycelium:
    """
    The brain. Reasons, routes, delegates. Never executes. Never sees.
    Model: mimo-v2-pro:free (1M context for full colony state)
    """

    def __init__(self):
        self.models = self._load_config("config/models.yaml")
        self.rules = self._load_config("config/rules.yaml")
        self.registry = self._load_registry()

    def _load_config(self, path):
        with open(FRAMEWORK_ROOT / path) as f:
            return yaml.safe_load(f)

    def _load_registry(self):
        roles = {}
        roles_dir = FRAMEWORK_ROOT / "registry" / "roles"
        for dept_dir in roles_dir.iterdir():
            if dept_dir.is_dir():
                dept = dept_dir.name
                roles[dept] = []
                for role_file in dept_dir.glob("*.md"):
                    roles[dept].append(role_file.stem)
        return roles

    def get_model_for_role(self, role):
        """Get the assigned model for a colony role."""
        return self.models["roles"].get(role, {}).get("id")

    def get_model_for_task(self, task_type):
        """Get the best model for a Dynamic Ant task type."""
        matrix = self.models.get("task_matrix", {})
        task = matrix.get(task_type, matrix.get("research"))
        return task["primary"] if task else self.models["roles"]["dynamic"]["id"]

    def find_agent_role(self, capability):
        """Find the best agency-agent role for a capability."""
        for dept, roles in self.registry.items():
            for role in roles:
                if capability.lower() in role.lower():
                    return {"department": dept, "role": role}
        return None

    def check_colony_health(self):
        """
        Check shared memory for colony health signals.
        Called on every heartbeat.
        """
        health = {
            "status": "unknown",
            "active_missions": 0,
            "completed_missions": 0,
            "pain_points": 0,
            "green_leaves": 0,
            "recent_benchmarks": 0,
        }
        # Implementation: read QMD for #mission, #mission-complete, #pain-point, etc.
        return health

    def execute_mission(self, mission):
        """Delegate a mission to Army Ants via shared memory."""
        return {
            "mission": mission,
            "status": "delegated",
            "model": self.get_model_for_role("mycelium"),
            "layers": ["army", "dynamic"],
            "memory_write": "#mission",
        }


class Scout:
    """
    Researcher. Finds better models, tools, opportunities. Never executes.
    Model: step-3.5-flash:free (fast and cheap)
    """

    def __init__(self, mycelium):
        self.mycelium = mycelium
        self.model = mycelium.get_model_for_role("scout")

    def research_models(self):
        """Find and test new free models. Write #benchmark to shared memory."""
        return {
            "status": "researching",
            "model": self.model,
            "memory_write": "#benchmark",
        }

    def find_opportunities(self):
        """Search for revenue opportunities. Write #green-leaf to shared memory."""
        return {
            "status": "searching",
            "model": self.model,
            "memory_write": "#green-leaf",
        }


class ArmyAnt:
    """
    Team builder. Selects agency-agent roles and spawns Dynamic Ants.
    Model: mimo-v2-pro:free (1M context for registry + mission state)
    """

    def __init__(self, mycelium):
        self.mycelium = mycelium
        self.model = mycelium.get_model_for_role("army")

    def build_team(self, mission, required_capabilities):
        """Build a team of Dynamic Ants for a mission."""
        team = []
        for cap in required_capabilities:
            role = self.mycelium.find_agent_role(cap)
            model = self.mycelium.get_model_for_task(cap)
            team.append({"role": role, "model": model, "capability": cap})
        return {
            "team": team,
            "model": self.model,
            "memory_write": "#mission",
        }


class DynamicAnt:
    """
    Focused worker. One task. One role. One model. One report. Done.
    Model: mimo-v2-omni:free (vision+tools — the eyes and hands)
    """

    def __init__(self, role, model, task):
        self.role = role
        self.model = model
        self.task = task

    def execute(self):
        """
        Execute the assigned task.
        MUST write to shared memory at each step:
        - #mission when starting
        - #pain-point if blocked
        - #shortcut if better way found
        - #mission-complete when done
        """
        return {
            "role": self.role,
            "model": self.model,
            "task": self.task,
            "status": "completed",
            "memory_writes": [
                "#mission",
                "#mission-complete",
            ],
        }
