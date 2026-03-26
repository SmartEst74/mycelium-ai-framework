/**
 * DelegationGuard — Mechanical enforcement of the Mycelium chain of command.
 *
 * This is NOT a guideline. It's a gate. Every action passes through here.
 * If a role attempts an action outside its permissions, it is BLOCKED.
 *
 * Chain of command:
 *   MYCELIUM    → think, plan, dispatch, remember (NEVER execute/build/research)
 *   SCOUT       → research, report (NEVER execute/build)
 *   ARMY_ANT    → coordinate, build-teams (NEVER execute leaf work)
 *   DYNAMIC_ANT → execute, build, deploy, test, write (the workers)
 *   GENERAL     → execute, build (fallback for unrecognized roles)
 */

export class AgentRole {
  static MYCELIUM = 'MYCELIUM';
  static SCOUT = 'SCOUT';
  static ARMY_ANT = 'ARMY_ANT';
  static DYNAMIC_ANT = 'DYNAMIC_ANT';
  static GENERAL = 'GENERAL';

  static ALL = [AgentRole.MYCELIUM, AgentRole.SCOUT, AgentRole.ARMY_ANT, AgentRole.DYNAMIC_ANT, AgentRole.GENERAL];
}

/**
 * Action types that can be validated.
 * Each maps to a concrete behavior in the framework.
 */
export class ActionType {
  // Thinking / planning (brain work)
  static THINK = 'think';
  static PLAN = 'plan';
  static DISPATCH = 'dispatch';
  static REMEMBER = 'remember';

  // Research (sensor work)
  static RESEARCH = 'research';
  static REPORT = 'report';

  // Coordination (protector work)
  static COORDINATE = 'coordinate';
  static BUILD_TEAM = 'build-team';

  // Execution (worker work)
  static EXECUTE = 'execute';
  static BUILD = 'build';
  static DEPLOY = 'deploy';
  static TEST = 'test';
  static WRITE = 'write';

  // Meta
  static CHECK_HEALTH = 'check-health';
  static CHECK_DELEGATION = 'check-delegation';
}

/**
 * The permission matrix. Each role maps to a Set of allowed actions.
 * Anything NOT in the set is DENIED. Default-deny.
 */
const PERMISSIONS = {
  [AgentRole.MYCELIUM]: new Set([
    ActionType.THINK,
    ActionType.PLAN,
    ActionType.DISPATCH,
    ActionType.REMEMBER,
    ActionType.CHECK_HEALTH,
    ActionType.CHECK_DELEGATION,
  ]),
  [AgentRole.SCOUT]: new Set([
    ActionType.RESEARCH,
    ActionType.REPORT,
    ActionType.CHECK_DELEGATION,
  ]),
  [AgentRole.ARMY_ANT]: new Set([
    ActionType.COORDINATE,
    ActionType.BUILD_TEAM,
    ActionType.CHECK_DELEGATION,
  ]),
  [AgentRole.DYNAMIC_ANT]: new Set([
    ActionType.EXECUTE,
    ActionType.BUILD,
    ActionType.DEPLOY,
    ActionType.TEST,
    ActionType.WRITE,
    ActionType.CHECK_DELEGATION,
  ]),
  [AgentRole.GENERAL]: new Set([
    ActionType.EXECUTE,
    ActionType.BUILD,
    ActionType.TEST,
    ActionType.WRITE,
    ActionType.CHECK_DELEGATION,
  ]),
};

/**
 * Human-readable descriptions of why each role is blocked from certain actions.
 */
const VIOLATION_REASONS = {
  [AgentRole.MYCELIUM]: {
    [ActionType.EXECUTE]: 'Mycelium is the brain — it THINKS and DISPATCHES, never executes. Delegate to a Dynamic Ant.',
    [ActionType.BUILD]: 'Mycelium is the brain — it PLANS, never builds. Spawn an Army Ant to assemble a team.',
    [ActionType.DEPLOY]: 'Mycelium is the brain — it DISPATCHES, never deploys. Delegate to a Dynamic Ant.',
    [ActionType.TEST]: 'Mycelium is the brain — it thinks, never tests. Delegate to a Dynamic Ant.',
    [ActionType.WRITE]: 'Mycelium is the brain — it remembers, but never writes code/artifacts. Delegate to a Dynamic Ant.',
    [ActionType.RESEARCH]: 'Mycelium routes, never researches directly. Spawn a Scout.',
    [ActionType.REPORT]: 'Mycelium receives reports, never generates them. Spawn a Scout.',
    [ActionType.COORDINATE]: 'Mycelium dispatches; Army Ants coordinate. Use army().buildTeam().',
    [ActionType.BUILD_TEAM]: 'Mycelium dispatches; Army Ants build teams. Use army().buildTeam().',
  },
  [AgentRole.SCOUT]: {
    [ActionType.EXECUTE]: 'Scouts research and report — they NEVER execute. Hand findings to an Army Ant.',
    [ActionType.BUILD]: 'Scouts research and report — they NEVER build. Hand findings to an Army Ant.',
    [ActionType.DEPLOY]: 'Scouts research and report — they NEVER deploy.',
    [ActionType.TEST]: 'Scouts research and report — they NEVER test.',
    [ActionType.WRITE]: 'Scouts research and report — they NEVER write artifacts.',
    [ActionType.DISPATCH]: 'Scouts do not dispatch. Report findings to the Mycelium.',
    [ActionType.COORDINATE]: 'Scouts do not coordinate. Report findings to the Mycelium.',
  },
  [AgentRole.ARMY_ANT]: {
    [ActionType.EXECUTE]: 'Army Ants coordinate and build teams — they NEVER do leaf work. Assign a Dynamic Ant.',
    [ActionType.BUILD]: 'Army Ants coordinate teams — they NEVER build directly. Assign a Dynamic Ant.',
    [ActionType.DEPLOY]: 'Army Ants coordinate teams — they NEVER deploy directly. Assign a Dynamic Ant.',
    [ActionType.TEST]: 'Army Ants coordinate teams — they never test directly. Assign a Dynamic Ant.',
    [ActionType.WRITE]: 'Army Ants coordinate teams — they never write artifacts directly. Assign a Dynamic Ant.',
  },
  [AgentRole.DYNAMIC_ANT]: {
    [ActionType.DISPATCH]: 'Dynamic Ants execute — they do not dispatch. That is Mycelium work.',
    [ActionType.PLAN]: 'Dynamic Ants execute — they do not plan. That is Mycelium work.',
    [ActionType.COORDINATE]: 'Dynamic Ants execute — they do not coordinate. That is Army Ant work.',
    [ActionType.BUILD_TEAM]: 'Dynamic Ants execute — they do not build teams. That is Army Ant work.',
  },
  [AgentRole.GENERAL]: {
    [ActionType.DISPATCH]: 'General agents execute — they do not dispatch.',
    [ActionType.PLAN]: 'General agents execute — they do not plan.',
  },
};

/**
 * Default violation reason for actions not in the specific map.
 */
function getDefaultReason(role, action) {
  return `${role} agents are not permitted to perform '${action}'. Check the chain of command.`;
}

export class DelegationGuard {
  /**
   * @param {object} opts
   * @param {Rhizomorph} [opts.rhizo] - Optional Rhizomorph instance for logging violations
   * @param {string} [opts.role] - Current role (defaults to MYCELIUM)
   */
  constructor(opts = {}) {
    this.rhizo = opts.rhizo || null;
    this.role = opts.role || AgentRole.MYCELIUM;
    this._violationCount = 0;
    this._violationLog = [];
  }

  /**
   * Validate whether a role can perform an action.
   * @param {string} role - AgentRole constant
   * @param {string} action - ActionType constant
   * @returns {{ allowed: boolean, reason: string, role: string, action: string }}
   */
  static validateAction(role, action) {
    if (!AgentRole.ALL.includes(role)) {
      return {
        allowed: false,
        reason: `Unknown role '${role}'. Valid roles: ${AgentRole.ALL.join(', ')}`,
        role,
        action,
      };
    }

    const perms = PERMISSIONS[role];
    if (perms && perms.has(action)) {
      return { allowed: true, reason: 'Action permitted.', role, action };
    }

    const roleReasons = VIOLATION_REASONS[role];
    const specificReason = roleReasons?.[action];
    const reason = specificReason || getDefaultReason(role, action);

    return { allowed: false, reason, role, action };
  }

  /**
   * Validate action for the current role. Throws on violation.
   * @param {string} action - ActionType constant
   * @param {object} [context] - Optional context for logging
   * @returns {{ allowed: true, role: string, action: string }}
   * @throws {DelegationViolation} if action is not allowed
   */
  enforce(action, context = {}) {
    const result = DelegationGuard.validateAction(this.role, action);

    if (!result.allowed) {
      this._violationCount++;
      const violation = {
        role: this.role,
        action,
        reason: result.reason,
        context,
        timestamp: new Date().toISOString(),
      };
      this._violationLog.push(violation);

      // Log to rhizomorph if available
      if (this.rhizo) {
        this.rhizo.emit('delegation.violation', violation, {
          agent: this.role.toLowerCase().replace('_', '-'),
          tags: ['#violation', '#pain-point'],
        });
      }

      throw new DelegationViolation(result.reason, this.role, action);
    }

    return result;
  }

  /**
   * Check without throwing — returns result object.
   * @param {string} action
   * @returns {{ allowed: boolean, reason: string }}
   */
  check(action) {
    return DelegationGuard.validateAction(this.role, action);
  }

  /**
   * Get violation history for this guard instance.
   */
  get violations() {
    return [...this._violationLog];
  }

  get violationCount() {
    return this._violationCount;
  }

  /**
   * Get the full permission matrix for a role.
   * @param {string} role
   * @returns {string[]} Allowed action types
   */
  static getAllowedActions(role) {
    const perms = PERMISSIONS[role];
    return perms ? Array.from(perms) : [];
  }

  /**
   * Get denied actions for a role.
   * @param {string} role
   * @returns {string[]} Denied action types
   */
  static getDeniedActions(role) {
    const allActions = Object.values(ActionType);
    const perms = PERMISSIONS[role] || new Set();
    return allActions.filter(a => !perms.has(a));
  }

  /**
   * Format a human-readable permissions report.
   */
  static formatPermissions(role) {
    const allowed = DelegationGuard.getAllowedActions(role);
    const denied = DelegationGuard.getDeniedActions(role);
    let out = `Role: ${role}\n`;
    out += `  ✅ Allowed: ${allowed.join(', ') || '(none)'}\n`;
    out += `  🚫 Denied:  ${denied.join(', ') || '(none)'}`;
    return out;
  }
}

/**
 * Custom error class for delegation violations.
 */
export class DelegationViolation extends Error {
  constructor(message, role, action) {
    super(`🚫 DELEGATION VIOLATION [${role} → ${action}]: ${message}`);
    this.name = 'DelegationViolation';
    this.role = role;
    this.action = action;
    this.isDelegationViolation = true;
  }
}
