/**
 * DelegationGuard tests — proves mechanical enforcement works.
 * Uses node:test (built-in, no deps)
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { Rhizomorph } from '../src/rhizomorph.mjs';
import { MockProvider } from '../src/providers.mjs';
import {
  DelegationGuard,
  DelegationViolation,
  AgentRole,
  ActionType,
} from '../src/delegation.mjs';
import { Mycelium, DynamicAnt, ArmyAnt, Scout, RoleRegistry } from '../src/mycelium.mjs';
import { unlinkSync } from 'node:fs';

const TEST_DB = '/tmp/test_delegation.db';
function cleanDb() { try { unlinkSync(TEST_DB); } catch {} }

// ─── Unit tests for DelegationGuard itself ───────────────────────────

describe('DelegationGuard — static validation', () => {
  it('allows MYCELIUM to think, plan, dispatch, remember', () => {
    for (const action of [ActionType.THINK, ActionType.PLAN, ActionType.DISPATCH, ActionType.REMEMBER]) {
      const r = DelegationGuard.validateAction(AgentRole.MYCELIUM, action);
      assert.equal(r.allowed, true, `MYCELIUM should be allowed to ${action}`);
    }
  });

  it('DENIES MYCELIUM from execute, build, deploy, test, write', () => {
    for (const action of [ActionType.EXECUTE, ActionType.BUILD, ActionType.DEPLOY, ActionType.TEST, ActionType.WRITE]) {
      const r = DelegationGuard.validateAction(AgentRole.MYCELIUM, action);
      assert.equal(r.allowed, false, `MYCELIUM should be DENIED from ${action}`);
      assert.ok(r.reason.length > 0, 'Should have a reason');
    }
  });

  it('DENIES MYCELIUM from research and report', () => {
    for (const action of [ActionType.RESEARCH, ActionType.REPORT]) {
      const r = DelegationGuard.validateAction(AgentRole.MYCELIUM, action);
      assert.equal(r.allowed, false, `MYCELIUM should be DENIED from ${action}`);
      assert.ok(r.reason.toLowerCase().includes('scout'), 'Reason should mention Scout');
    }
  });

  it('allows SCOUT to research and report', () => {
    for (const action of [ActionType.RESEARCH, ActionType.REPORT]) {
      const r = DelegationGuard.validateAction(AgentRole.SCOUT, action);
      assert.equal(r.allowed, true, `SCOUT should be allowed to ${action}`);
    }
  });

  it('DENIES SCOUT from execute, build, deploy', () => {
    for (const action of [ActionType.EXECUTE, ActionType.BUILD, ActionType.DEPLOY]) {
      const r = DelegationGuard.validateAction(AgentRole.SCOUT, action);
      assert.equal(r.allowed, false, `SCOUT should be DENIED from ${action}`);
      assert.ok(r.reason.toLowerCase().includes('never'), 'Reason should say "never"');
    }
  });

  it('allows ARMY_ANT to coordinate and build-team', () => {
    for (const action of [ActionType.COORDINATE, ActionType.BUILD_TEAM]) {
      const r = DelegationGuard.validateAction(AgentRole.ARMY_ANT, action);
      assert.equal(r.allowed, true, `ARMY_ANT should be allowed to ${action}`);
    }
  });

  it('DENIES ARMY_ANT from execute, build, deploy', () => {
    for (const action of [ActionType.EXECUTE, ActionType.BUILD, ActionType.DEPLOY]) {
      const r = DelegationGuard.validateAction(AgentRole.ARMY_ANT, action);
      assert.equal(r.allowed, false, `ARMY_ANT should be DENIED from ${action}`);
      assert.ok(r.reason.toLowerCase().includes('dynamic ant'), 'Reason should mention Dynamic Ant');
    }
  });

  it('allows DYNAMIC_ANT to execute, build, deploy, test, write', () => {
    for (const action of [ActionType.EXECUTE, ActionType.BUILD, ActionType.DEPLOY, ActionType.TEST, ActionType.WRITE]) {
      const r = DelegationGuard.validateAction(AgentRole.DYNAMIC_ANT, action);
      assert.equal(r.allowed, true, `DYNAMIC_ANT should be allowed to ${action}`);
    }
  });

  it('DENIES DYNAMIC_ANT from dispatch, plan, coordinate', () => {
    for (const action of [ActionType.DISPATCH, ActionType.PLAN, ActionType.COORDINATE]) {
      const r = DelegationGuard.validateAction(AgentRole.DYNAMIC_ANT, action);
      assert.equal(r.allowed, false, `DYNAMIC_ANT should be DENIED from ${action}`);
    }
  });

  it('handles unknown roles', () => {
    const r = DelegationGuard.validateAction('BOGUS_ROLE', ActionType.EXECUTE);
    assert.equal(r.allowed, false);
    assert.ok(r.reason.includes('Unknown role'));
  });
});

describe('DelegationGuard — enforce() throws on violation', () => {
  it('throws DelegationViolation when MYCELIUM tries to execute', () => {
    const guard = new DelegationGuard({ role: AgentRole.MYCELIUM });
    assert.throws(
      () => guard.enforce(ActionType.EXECUTE),
      (err) => {
        assert.equal(err.name, 'DelegationViolation');
        assert.equal(err.isDelegationViolation, true);
        assert.equal(err.role, AgentRole.MYCELIUM);
        assert.equal(err.action, ActionType.EXECUTE);
        return true;
      }
    );
  });

  it('does not throw when MYCELIUM dispatches', () => {
    const guard = new DelegationGuard({ role: AgentRole.MYCELIUM });
    assert.doesNotThrow(() => guard.enforce(ActionType.DISPATCH));
  });

  it('tracks violation count', () => {
    const guard = new DelegationGuard({ role: AgentRole.MYCELIUM });
    try { guard.enforce(ActionType.EXECUTE); } catch {}
    try { guard.enforce(ActionType.BUILD); } catch {}
    assert.equal(guard.violationCount, 2);
    assert.equal(guard.violations.length, 2);
  });

  it('logs violations to Rhizomorph', () => {
    cleanDb();
    const rh = new Rhizomorph(TEST_DB);
    const guard = new DelegationGuard({ rhizo: rh, role: AgentRole.MYCELIUM });
    try { guard.enforce(ActionType.EXECUTE); } catch {}
    const events = rh.query({ tags: ['#violation'] });
    assert.ok(events.length >= 1, 'Should log violation event');
    assert.equal(events[0].type, 'delegation.violation');
    rh.close();
    cleanDb();
  });
});

describe('DelegationGuard — check() does not throw', () => {
  it('returns result object without throwing', () => {
    const guard = new DelegationGuard({ role: AgentRole.MYCELIUM });
    const result = guard.check(ActionType.EXECUTE);
    assert.equal(result.allowed, false);
    assert.ok(result.reason);
    assert.equal(guard.violationCount, 0, 'check() should not increment violation count');
  });
});

describe('DelegationGuard — utility methods', () => {
  it('getAllowedActions returns correct list', () => {
    const actions = DelegationGuard.getAllowedActions(AgentRole.MYCELIUM);
    assert.ok(actions.includes(ActionType.THINK));
    assert.ok(actions.includes(ActionType.DISPATCH));
    assert.ok(!actions.includes(ActionType.EXECUTE));
  });

  it('getDeniedActions returns correct list', () => {
    const actions = DelegationGuard.getDeniedActions(AgentRole.MYCELIUM);
    assert.ok(actions.includes(ActionType.EXECUTE));
    assert.ok(actions.includes(ActionType.BUILD));
    assert.ok(!actions.includes(ActionType.THINK));
  });

  it('formatPermissions returns human-readable output', () => {
    const output = DelegationGuard.formatPermissions(AgentRole.MYCELIUM);
    assert.ok(output.includes('MYCELIUM'));
    assert.ok(output.includes('✅'));
    assert.ok(output.includes('🚫'));
  });
});

// ─── Integration tests — enforcement in agent classes ────────────────

describe('Delegation enforcement — Mycelium class', () => {
  let brain;
  beforeEach(() => { cleanDb(); brain = new Mycelium({ providerType: 'mock', dbPath: TEST_DB }); });
  afterEach(() => { brain.close(); cleanDb(); });

  it('can executeMission (dispatch) — allowed', () => {
    assert.doesNotThrow(() => {
      brain.executeMission('Build landing page', ['frontend']);
    });
  });

  it('has a guard with MYCELIUM role', () => {
    assert.equal(brain.guard.role, AgentRole.MYCELIUM);
  });

  it('guard blocks execute action', () => {
    const result = brain.guard.check(ActionType.EXECUTE);
    assert.equal(result.allowed, false);
  });

  it('violations are logged to rhizomorph', () => {
    try { brain.guard.enforce(ActionType.EXECUTE); } catch {}
    const violations = brain.rhizo.query({ tags: ['#violation'] });
    assert.ok(violations.length >= 1);
  });
});

describe('Delegation enforcement — DynamicAnt class', () => {
  let rhizo;
  beforeEach(() => { cleanDb(); rhizo = new Rhizomorph(TEST_DB); });
  afterEach(() => { rhizo.close(); cleanDb(); });

  it('can execute tasks — allowed', () => {
    const ant = new DynamicAnt(new MockProvider(), rhizo);
    assert.doesNotThrow(() => {
      ant.execute({ task: 'Build page', role: 'frontend-dev' });
    });
  });

  it('has a guard with DYNAMIC_ANT role', () => {
    const ant = new DynamicAnt(new MockProvider(), rhizo);
    assert.equal(ant.guard.role, AgentRole.DYNAMIC_ANT);
  });
});

describe('Delegation enforcement — ArmyAnt class', () => {
  let rhizo, registry;
  beforeEach(() => { cleanDb(); rhizo = new Rhizomorph(TEST_DB); registry = new RoleRegistry(); });
  afterEach(() => { rhizo.close(); cleanDb(); });

  it('can build teams and coordinate — allowed', () => {
    const army = new ArmyAnt(new MockProvider(), rhizo, registry);
    assert.doesNotThrow(() => {
      const plan = army.buildTeam('Build page', ['frontend']);
      army.coordinate(plan.team, 'Build page');
    });
  });

  it('has a guard with ARMY_ANT role', () => {
    const army = new ArmyAnt(new MockProvider(), rhizo, registry);
    assert.equal(army.guard.role, AgentRole.ARMY_ANT);
    // Army Ant should NOT be able to execute directly
    const result = army.guard.check(ActionType.EXECUTE);
    assert.equal(result.allowed, false);
  });
});

describe('Delegation enforcement — Scout class', () => {
  let rhizo;
  beforeEach(() => { cleanDb(); rhizo = new Rhizomorph(TEST_DB); });
  afterEach(() => { rhizo.close(); cleanDb(); });

  it('can research — allowed', () => {
    const scout = new Scout(new MockProvider(), rhizo);
    assert.doesNotThrow(() => {
      scout.research('compare free models');
    });
  });

  it('has a guard with SCOUT role', () => {
    const scout = new Scout(new MockProvider(), rhizo);
    assert.equal(scout.guard.role, AgentRole.SCOUT);
    // Scout should NOT be able to execute
    const result = scout.guard.check(ActionType.EXECUTE);
    assert.equal(result.allowed, false);
  });
});

// ─── Cross-role denial matrix — every role/action combination ─────────

describe('Full permission matrix', () => {
  it('every role has exactly the right permissions', () => {
    // MYCELIUM: think, plan, dispatch, remember, check-health, check-delegation
    const mycAllowed = DelegationGuard.getAllowedActions(AgentRole.MYCELIUM);
    assert.equal(mycAllowed.length, 6);
    assert.ok(mycAllowed.includes(ActionType.THINK));
    assert.ok(mycAllowed.includes(ActionType.PLAN));
    assert.ok(mycAllowed.includes(ActionType.DISPATCH));
    assert.ok(mycAllowed.includes(ActionType.REMEMBER));
    assert.ok(mycAllowed.includes(ActionType.CHECK_HEALTH));
    assert.ok(mycAllowed.includes(ActionType.CHECK_DELEGATION));

    // SCOUT: research, report, check-delegation
    const scoutAllowed = DelegationGuard.getAllowedActions(AgentRole.SCOUT);
    assert.equal(scoutAllowed.length, 3);
    assert.ok(scoutAllowed.includes(ActionType.RESEARCH));
    assert.ok(scoutAllowed.includes(ActionType.REPORT));

    // ARMY_ANT: coordinate, build-team, check-delegation
    const armyAllowed = DelegationGuard.getAllowedActions(AgentRole.ARMY_ANT);
    assert.equal(armyAllowed.length, 3);
    assert.ok(armyAllowed.includes(ActionType.COORDINATE));
    assert.ok(armyAllowed.includes(ActionType.BUILD_TEAM));

    // DYNAMIC_ANT: execute, build, deploy, test, write, check-delegation
    const dynAllowed = DelegationGuard.getAllowedActions(AgentRole.DYNAMIC_ANT);
    assert.equal(dynAllowed.length, 6);
    assert.ok(dynAllowed.includes(ActionType.EXECUTE));
    assert.ok(dynAllowed.includes(ActionType.BUILD));
    assert.ok(dynAllowed.includes(ActionType.DEPLOY));
    assert.ok(dynAllowed.includes(ActionType.TEST));
    assert.ok(dynAllowed.includes(ActionType.WRITE));
  });

  it('no role can do everything (principle of least privilege)', () => {
    const allActions = Object.values(ActionType);
    for (const role of AgentRole.ALL) {
      const allowed = DelegationGuard.getAllowedActions(role);
      assert.ok(allowed.length < allActions.length, `${role} should not have all permissions`);
    }
  });

  it('DEPLOY is denied to all except DYNAMIC_ANT and GENERAL', () => {
    for (const role of [AgentRole.MYCELIUM, AgentRole.SCOUT, AgentRole.ARMY_ANT]) {
      const r = DelegationGuard.validateAction(role, ActionType.DEPLOY);
      assert.equal(r.allowed, false, `${role} should not be able to deploy`);
    }
    assert.equal(DelegationGuard.validateAction(AgentRole.DYNAMIC_ANT, ActionType.DEPLOY).allowed, true);
    assert.equal(DelegationGuard.validateAction(AgentRole.GENERAL, ActionType.DEPLOY).allowed, false); // general can't deploy
  });
});
