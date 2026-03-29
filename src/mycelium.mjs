/**
 * Mycelium — Colonial AI Agent Orchestrator
 * Thinks, plans, dispatches. NEVER executes leaf work.
 * Every action is an event in Rhizomorph.
 */
import { Rhizomorph } from './rhizomorph.mjs';
import { createProvider } from './providers.mjs';
import { readdirSync, readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse as parseYaml } from './yaml.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

export class ModelConfig {
  constructor(configPath = join(ROOT, 'config', 'models.yaml')) {
    this.roles = {};
    this.fallbacks = [];
    if (!existsSync(configPath)) return;
    const cfg = parseYaml(readFileSync(configPath, 'utf8'));
    if (cfg.roles) this.roles = cfg.roles;
    if (cfg.fallbacks) this.fallbacks = Array.isArray(cfg.fallbacks) ? cfg.fallbacks : [];
  }
  modelFor(role) {
    const entry = this.roles[role];
    if (entry?.id && entry?.provider) return `${entry.provider}/${entry.id}`;
    if (entry?.id) return entry.id;
    return this.roles.mycelium?.id ? `kilocode/${this.roles.mycelium.id}` : 'kilocode/xiaomi/mimo-v2-pro:free';
  }
}

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
  constructor(provider, rhizo, modelConfig) {
    this.provider = provider;
    this.rhizo = rhizo;
    this.models = modelConfig || new ModelConfig();
  }

  _gatherContext(role) {
    const lessons = this.rhizo.query({ tags: ['#lesson'], limit: 5 });
    const painPoints = this.rhizo.query({ tags: ['#pain-point'], limit: 3 });
    const shortcuts = this.rhizo.query({ tags: ['#shortcut'], limit: 3 });
    let ctx = '';
    if (lessons.length) ctx += `\n## Colony Lessons\n${lessons.map(e => `- ${typeof e.payload === 'string' ? e.payload : JSON.stringify(e.payload)}`).join('\n')}`;
    if (painPoints.length) ctx += `\n## Known Pain Points\n${painPoints.map(e => `- ${typeof e.payload === 'string' ? e.payload : JSON.stringify(e.payload)}`).join('\n')}`;
    if (shortcuts.length) ctx += `\n## Shortcuts\n${shortcuts.map(e => `- ${typeof e.payload === 'string' ? e.payload : JSON.stringify(e.payload)}`).join('\n')}`;
    return ctx;
  }

  _selfEval(task, role, result) {
    const hasError = result.error;
    const scores = {
      accuracy: hasError ? 2 : 4,
      efficiency: hasError ? 2 : 4,
      completeness: hasError ? 1 : 4,
      reusability: hasError ? 1 : 3,
    };
    const avg = (scores.accuracy + scores.efficiency + scores.completeness + scores.reusability) / 4;
    const tags = [];
    if (avg >= 4) tags.push('#lesson');
    if (scores.efficiency < 4) tags.push('#shortcut');
    if (avg < 3) tags.push('#pain-point');
    tags.push('#self-eval');
    this.rhizo.emit('agent.self-eval', { task, role, scores, average: avg }, { agent: `dynamic-${role}`, tags });
    return scores;
  }

  execute({ task, role, model }) {
    const context = this._gatherContext(role);
    this.rhizo.emit('memory.write', { task, role }, { agent: 'dynamic-ant', tags: ['#mission'] });
    const enrichedTask = context
      ? `Registry role: ${role}\n\n${context}\n\nTASK: ${task}`
      : `Registry role: ${role}\nTASK: ${task}`;
    const result = this.provider.spawnAgent({
      model: model || this.models.modelFor('dynamic'),
      task: enrichedTask,
      agentId: `dynamic-${role}`,
    });
    this.rhizo.emit('memory.write', { task, role, result: result.result }, {
      agent: 'dynamic-ant',
      tags: result.error ? ['#pain-point'] : ['#mission-complete'],
    });
    const scores = this._selfEval(task, role, result);
    return { role, status: result.error ? 'failed' : 'completed', resp: result, scores };
  }
}

export class ArmyAnt {
  constructor(provider, rhizo, registry, modelConfig) {
    this.provider = provider;
    this.rhizo = rhizo;
    this.registry = registry;
    this.models = modelConfig || new ModelConfig();
  }
  buildTeam(mission, capabilities) {
    const team = capabilities.map(cap => ({
      capability: cap,
      role: this.registry.find(cap) || { department: 'general', role: `general-${cap}` },
      model: this.models.modelFor('dynamic'),
    }));
    this.rhizo.emit('memory.write', { mission, team }, { agent: 'army-ant', tags: ['#mission'] });
    return { mission, team };
  }
  coordinate(team, task) {
    const ant = new DynamicAnt(this.provider, this.rhizo, this.models);
    return team.map(m => ant.execute({ task, role: m.role?.role || m.capability, model: m.model }));
  }
}

export class Scout {
  constructor(provider, rhizo, modelConfig) {
    this.provider = provider;
    this.rhizo = rhizo;
    this.models = modelConfig || new ModelConfig();
  }

  _priorBenchmarks(domain) {
    const benchmarks = this.rhizo.query({ tags: ['#benchmark'], limit: 5 });
    if (!benchmarks.length) return '';
    return `\n## Prior Benchmarks\n${benchmarks.map(e => `- ${typeof e.payload === 'string' ? e.payload : JSON.stringify(e.payload)}`).join('\n')}\n`;
  }

  research(query) {
    this.rhizo.emit('memory.write', { query }, { agent: 'scout', tags: ['#mission'] });
    const prior = this._priorBenchmarks(query);
    const enrichedQuery = prior
      ? `SCOUT. Research only, never execute.\n${prior}\n${query}`
      : `SCOUT. Research only, never execute.\n${query}`;
    const result = this.provider.spawnAgent({
      model: this.models.modelFor('scout'),
      task: enrichedQuery,
      agentId: 'scout',
    });
    this.rhizo.emit('memory.write', { query, result: result.result }, { agent: 'scout', tags: ['#benchmark'] });
    return { query, ...result };
  }

  findOpportunities(domain) {
    const result = this.provider.spawnAgent({
      model: this.models.modelFor('scout'),
      task: `SCOUT. Find revenue opportunities in: ${domain}`,
      agentId: 'scout-opp',
    });
    this.rhizo.emit('memory.write', { domain, result: result.result }, { agent: 'scout', tags: ['#green-leaf'] });
    return { domain, ...result };
  }
}

export class Mycelium {
  constructor(opts = {}) {
    this.provider = opts.provider || createProvider(opts.providerType || 'auto');
    this.rhizo = new Rhizomorph(opts.dbPath || join(ROOT, 'lcm.db'));
    this.registry = new RoleRegistry();
    this.models = new ModelConfig(opts.modelsPath);
  }

  executeMission(mission, capabilities = ['frontend']) {
    this.rhizo.emit('memory.write', { mission }, { agent: 'mycelium', tags: ['#mission'] });
    const army = new ArmyAnt(this.provider, this.rhizo, this.registry, this.models);
    const plan = army.buildTeam(mission, capabilities);
    const results = army.coordinate(plan.team, mission);
    return { mission, rhizoSeq: this.rhizo.seq, dispatch: results };
  }

  checkColonyHealth() {
    const missions = this.rhizo.countByTag('#mission');
    const completed = this.rhizo.countByTag('#mission-complete');
    const painPoints = this.rhizo.countByTag('#pain-point');
    const greenLeaves = this.rhizo.countByTag('#green-leaf');
    const benchmarks = this.rhizo.countByTag('#benchmark');
    const lessons = this.rhizo.countByTag('#lesson');
    const selfEvals = this.rhizo.countByTag('#self-eval');
    return {
      status: painPoints > completed ? 'unhealthy' : 'healthy',
      activeMissions: missions - completed,
      completedMissions: completed,
      painPoints,
      greenLeaves,
      recentBenchmarks: benchmarks,
      lessons,
      selfEvals,
    };
  }

  scout() { return new Scout(this.provider, this.rhizo, this.models); }
  army() { return new ArmyAnt(this.provider, this.rhizo, this.registry, this.models); }
  close() { this.rhizo.close(); }
}
