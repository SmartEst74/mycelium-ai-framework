"""
Mycium AI Framework — Core Orchestration

Chain of Command:
  Mycelium (Brain) → Scout (Researcher) → Army (Team Builder) → Dynamic (Worker)

Usage:
  from core.mycelium import Mycelium
  brain = Mycelium()
  result = brain.execute_mission("Build a landing page for IT1st")
"""

import yaml
import os
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).parent.parent

class Mycelium:
    """The brain. Reasons, delegates, monitors. Never executes."""

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

    def get_model_for_task(self, task_type):
        """Get the best model for a task type. Never downgrades."""
        matrix = self.models.get("task_matrix", {})
        task = matrix.get(task_type, matrix.get("research"))
        return task["primary"] if task else self.models["models"]["primary"]["id"]

    def find_agent_role(self, capability):
        """Find the best agency-agent role for a capability."""
        for dept, roles in self.registry.items():
            for role in roles:
                if capability.lower() in role.lower():
                    return {"department": dept, "role": role}
        return None

    def execute_mission(self, mission):
        """Delegate a mission to the appropriate layer."""
        # Mycelium reasons about the mission
        # Then delegates to Army for execution
        return {
            "mission": mission,
            "status": "delegated",
            "layers": ["scout", "army", "dynamic"],
            "model": self.get_model_for_task("reasoning")
        }


class Scout:
    """Researcher. Finds better models, tools, opportunities. Never executes."""

    def __init__(self, mycelium):
        self.mycelium = mycelium

    def research_models(self):
        """Find and test new free models. Return findings."""
        return {"status": "researching", "model": self.mycelium.get_model_for_task("research")}

    def find_opportunities(self):
        """Search for revenue opportunities (green leaves)."""
        return {"status": "searching", "model": self.mycelium.get_model_for_task("research")}


class ArmyAnt:
    """Team builder. Selects agency-agent roles and spawns Dynamic Ants."""

    def __init__(self, mycelium):
        self.mycelium = mycelium

    def build_team(self, mission, required_capabilities):
        """Build a team of Dynamic Ants for a mission."""
        team = []
        for cap in required_capabilities:
            role = self.mycelium.find_agent_role(cap)
            model = self.mycelium.get_model_for_task(cap)
            team.append({"role": role, "model": model, "capability": cap})
        return team


class DynamicAnt:
    """Focused worker. One task. One role. One model. One report. Done."""

    def __init__(self, role, model, task):
        self.role = role
        self.model = model
        self.task = task

    def execute(self):
        """Execute the assigned task with the assigned role and model."""
        return {
            "role": self.role,
            "model": self.model,
            "task": self.task,
            "status": "completed"
        }
