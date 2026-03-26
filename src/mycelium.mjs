/**
 * Mycelium — Colonial AI Agent Orchestrator
 * Thinks, plans, dispatches. NEVER executes leaf work.
 * Every action is an event in Rhizomorph.
 *
 * DelegationGuard enforces chain-of-command mechanically.
 */
import { Rhizomorph } from './rhizomorph.mjs';
import { createProvider } from './providers.mjs';
import { DelegationGuard, AgentRole, ActionType, DelegationViolation } from './delegation.mjs';
import { readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

export class RoleRegistry {
  constructor(rolesDir = join(ROOT, 'registry', 'roles')) {
    this.roles = new Map();
    if (!existsSync(rolesDir)) return;
    for (const entry of readdirSync(rolesDir, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        const dept = entry.name;
        for (const file of readdirSync(join(rolesDir, dept)).filter(f => f.endsWith('.md'))) {
          this.roles.set(file.replace('.md', ''), { department: dept, role: file.replace('.md', '') });
        }
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        this.roles.set(entry.name.replace('.md', ''), { department: 'general', role: entry.name.replace('.md', '') });
      }
    }
  }
  find(cap) { for (const [r, info] of this.roles) if (r.toLowerCase().includes(cap.toLowerCase())) return info; return null; }
  list() { return Array.from(this.roles.values()); }
  count() { return this.roles.size; }
}

export class DynamicAnt {
  constructor(provider, rhizo) {
    this.provider = provider;
    this.rhizo = rhizo;
    this.guard = new DelegationGuard({ rhizo, role: AgentRole.DYNAMIC_ANT });
  }
  execute({ task, role, model }) {
    this.guard.enforce(ActionType.EXECUTE, { task, role });
    this.rhizo.emit('memory.write', { task, role }, { agent: 'dynamic-ant', tags: ['#mission'] });
    const result = this.provider.spawnAgent({ model: model || 'kilocode/xiaomi/mimo-v2-pro:free', task: `Registry role: ${role}\nTASK: ${task}`, agentId: `dynamic-${role}` });
    this.rhizo.emit('memory.write', { task, role, result: result.result }, { agent: 'dynamic-ant', tags: result.error ? ['#pain-point'] : ['#mission-complete'] });
    return { role, status: result.error ? 'failed' : 'completed', resp: result };
  }
}

export class ArmyAnt {
  constructor(provider, rhizo, registry) {
    this.provider = provider;
    this.rhizo = rhizo;
    this.registry = registry;
    this.guard = new DelegationGuard({ rhizo, role: AgentRole.ARMY_ANT });
  }
  buildTeam(mission, capabilities) {
    this.guard.enforce(ActionType.BUILD_TEAM, { mission, capabilities });
    const team = capabilities.map(cap => ({ capability: cap, role: this.registry.find(cap) || { department: 'general', role: `general-${cap}` }, model: 'kilocode/xiaomi/mimo-v2-pro:free' }));
    this.rhizo.emit('memory.write', { mission, team }, { agent: 'army-ant', tags: ['#mission'] });
    return { mission, team };
  }
  coordinate(team, task) {
    this.guard.enforce(ActionType.COORDINATE, { teamSize: team.length, task });
    const ant = new DynamicAnt(this.provider, this.rhizo);
    return team.map(m => ant.execute({ task, role: m.role?.role || m.capability, model: m.model }));
  }
}

export class Scout {
  constructor(provider, rhizo) {
    this.provider = provider;
    this.rhizo = rhizo;
    this.guard = new DelegationGuard({ rhizo, role: AgentRole.SCOUT });
  }
  research(query) {
    this.guard.enforce(ActionType.RESEARCH, { query });
    this.rhizo.emit('memory.write', { query }, { agent: 'scout', tags: ['#mission'] });
    const result = this.provider.spawnAgent({ model: 'stepfun/step-3.5-flash:free', task: `SCOUT. Research only, never execute.\n${query}`, agentId: 'scout' });
    this.rhizo.emit('memory.write', { query, result: result.result }, { agent: 'scout', tags: ['#benchmark'] });
    return { query, ...result };
  }
  findOpportunities(domain) {
    this.guard.enforce(ActionType.RESEARCH, { domain });
    const result = this.provider.spawnAgent({ model: 'stepfun/step-3.5-flash:free', task: `SCOUT. Find revenue opportunities in: ${domain}`, agentId: 'scout-opp' });
    this.rhizo.emit('memory.write', { domain, result: result.result }, { agent: 'scout', tags: ['#green-leaf'] });
    return { domain, ...result };
  }
}

export class Mycelium {
  constructor(opts = {}) {
    this.provider = opts.provider || createProvider(opts.providerType || 'auto');
    this.rhizo = new Rhizomorph(opts.dbPath || join(ROOT, 'lcm.db'));
    this.registry = new RoleRegistry();
    this.guard = new DelegationGuard({ rhizo: this.rhizo, role: AgentRole.MYCELIUM });
  }

  executeMission(mission, capabilities = ['frontend']) {
    this.guard.enforce(ActionType.DISPATCH, { mission, capabilities });
    this.rhizo.emit('memory.write', { mission }, { agent: 'mycelium', tags: ['#mission'] });
    const army = new ArmyAnt(this.provider, this.rhizo, this.registry);
    const plan = army.buildTeam(mission, capabilities);
    const results = army.coordinate(plan.team, mission);
    return { mission, rhizoSeq: this.rhizo.seq, dispatch: results };
  }

  checkColonyHealth() {
    this.guard.enforce(ActionType.CHECK_HEALTH);
    return {
      status: this.rhizo.countByTag('#pain-point') > this.rhizo.countByTag('#mission-complete') ? 'unhealthy' : 'healthy',
      activeMissions: this.rhizo.countByTag('#mission') - this.rhizo.countByTag('#mission-complete'),
      completedMissions: this.rhizo.countByTag('#mission-complete'),
      painPoints: this.rhizo.countByTag('#pain-point'),
      greenLeaves: this.rhizo.countByTag('#green-leaf'),
      recentBenchmarks: this.rhizo.countByTag('#benchmark')
    };
  }

  scout() { return new Scout(this.provider, this.rhizo); }
  army() { return new ArmyAnt(this.provider, this.rhizo, this.registry); }
  close() { this.rhizo.close(); }
}
