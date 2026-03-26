"""Tests for the Mycelium core module."""

import pytest
import os
from core.mycelium import Mycelium, Scout, ArmyAnt, DynamicAnt
from core.providers import MockAgentProvider


class TestMycelium:
    """Tests for the Mycelium brain."""

    def test_initialization(self):
        brain = Mycelium()
        assert brain.models is not None
        assert brain.rules is not None
        assert brain.registry is not None

    def test_model_assignment_brain(self):
        brain = Mycelium()
        model = brain.get_model_for_role("mycelium")
        assert "mimo-v2-pro" in model, "Brain MUST use mimo-v2-pro (1M context, no vision)"

    def test_model_assignment_dynamic(self):
        brain = Mycelium()
        model = brain.get_model_for_role("dynamic")
        assert "mimo-v2-omni" in model, "Dynamic Ants MUST use mimo-v2-omni (vision+tools)"

    def test_model_assignment_scout(self):
        brain = Mycelium()
        model = brain.get_model_for_role("scout")
        assert "step-3.5-flash" in model, "Scout MUST use step-3.5-flash (fast/cheap)"

    def test_no_vision_on_brain(self):
        """The brain does not need vision. This is a biological invariant."""
        brain = Mycelium()
        brain_caps = brain.models["roles"]["mycelium"]["capabilities"]
        assert "vision" not in brain_caps, "Brain MUST NOT use vision — ants see, brain routes"

    def test_vision_on_ants(self):
        """Dynamic Ants are the eyes. They MUST have vision."""
        brain = Mycelium()
        ant_caps = brain.models["roles"]["dynamic"]["capabilities"]
        assert "vision" in ant_caps, "Dynamic Ants MUST have vision — they are the eyes"

    def test_find_agent_role(self):
        brain = Mycelium()
        role = brain.find_agent_role("frontend")
        assert role is not None, "Should find a frontend agent role in the registry"
        assert "department" in role
        assert "role" in role

    def test_get_model_for_task(self):
        brain = Mycelium()
        model = brain.get_model_for_task("vision")
        assert "mimo-v2-omni" in model, "Vision tasks MUST use mimo-v2-omni"

    def test_execute_mission(self):
        brain = Mycelium(provider=MockAgentProvider(), rhizomorph_db="/tmp/test_mycelium_lcm.db")
        result = brain.execute_mission("Test mission")
        # ensure rhizomorph sequence was returned and dispatch exists
        assert "rhizo_seq" in result
        assert "dispatch" in result


class TestScout:
    """Tests for the Scout sensor."""

    def test_scout_model(self):
        brain = Mycelium()
        scout = Scout(brain)
        assert "step-3.5-flash" in scout.model

    def test_research_models(self):
        brain = Mycelium(provider=MockAgentProvider(), rhizomorph_db="/tmp/test_mycelium_lcm.db")
        scout = Scout(brain)
        result = scout.research_models("compare free models")
        # provider returns tags indicating benchmark
        assert isinstance(result, dict)

    def test_find_opportunities(self):
        brain = Mycelium(provider=MockAgentProvider(), rhizomorph_db="/tmp/test_mycelium_lcm.db")
        scout = Scout(brain)
        result = scout.find_opportunities("micro-saas")
        assert isinstance(result, dict)


class TestArmyAnt:
    """Tests for Army Ants (coordinators)."""

    def test_army_model(self):
        brain = Mycelium()
        army = ArmyAnt(brain)
        assert "mimo-v2-pro" in army.model

    def test_build_team(self):
        brain = Mycelium(provider=MockAgentProvider(), rhizomorph_db="/tmp/test_mycelium_lcm.db")
        army = ArmyAnt(brain)
        team = army.build_team("Build a landing page", ["frontend", "design"])
        assert len(team["team"]) == 2


class TestDynamicAnt:
    """Tests for Dynamic Ants (workers)."""

    def test_execute_writes_memory(self):
        brain = Mycelium(provider=MockAgentProvider(), rhizomorph_db="/tmp/test_mycelium_lcm.db")
        # build a dynamic ant via ArmyAnt coordinate path to ensure rhizomorph writes
        army = ArmyAnt(brain)
        team = army.build_team("Small mission", ["frontend"])
        results = army.coordinate(team["team"], "Small mission")
        assert len(results) == 1
        assert results[0]["status"] == "completed"


class TestModelInvariants:
    """Immutable rules that must never be violated."""

    def test_never_spend_money(self):
        """No model in the primary chain should cost money."""
        brain = Mycelium()
        for role_name, role_data in brain.models["roles"].items():
            cost = role_data.get("cost", 0)
            assert cost == 0, f"{role_name} uses a paid model — FREE TIER ONLY"

    def test_fallback_last_resort_paid(self):
        """Paid fallback is explicitly marked as last resort."""
        brain = Mycelium()
        fallbacks = brain.models["fallbacks"]
        paid = [f for f in fallbacks if f.get("cost") == "paid"]
        # If there's a paid fallback, it must be last
        if paid:
            assert fallbacks.index(paid[0]) == len(fallbacks) - 1, "Paid model must be last resort"
