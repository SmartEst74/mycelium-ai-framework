/**
 * Providers — How Mycelium talks to agents.
 * OpenClawProvider calls gateway directly via child_process.
 * MockProvider returns deterministic responses for testing.
 */
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';

export class OpenClawProvider {
  constructor(opts = {}) {
    this.timeoutSec = opts.timeoutSec || 300;
  }

  spawnAgent({ model = 'kilocode/xiaomi/mimo-v2-pro:free', task = '', agentId = 'mycelium' }) {
    const args = ['sessions', 'spawn', '--task', task, '--model', model, '--agent-id', agentId, '--mode', 'run'];
    try {
      const res = spawnSync('openclaw', args, { timeout: this.timeoutSec * 1000, encoding: 'utf8', maxBuffer: 10485760 });
      if (res.error) throw res.error;
      const output = (res.stdout || res.stderr || '').trim();
      const sm = output.match(/session[:\s]+([^\s]+)/i);
      return { sessionId: sm?.[1] || `local-${Date.now()}`, result: output, tags: res.status === 0 ? ['#mission-complete'] : ['#pain-point'], error: res.status !== 0 ? res.stderr : null };
    } catch (e) {
      return { sessionId: `err-${Date.now()}`, result: null, tags: ['#pain-point'], error: e.message };
    }
  }
}

export class MockProvider {
  responses = {
    frontend: { result: 'Deployed landing page', status: 'completed' },
    design: { result: 'Created design system', status: 'completed' },
    research: { result: 'Found 3 opportunities', status: 'completed' },
    scout: { result: 'Research complete', summary: 'Found key insights', tags: ['#benchmark'] },
    default: { result: 'Task completed', ok: true, notes: 'task completed' }
  };

  spawnAgent({ model = 'mock', task = '', agentId = 'mock' }) {
    let key = 'default';
    for (const k of Object.keys(this.responses)) {
      if (task.toLowerCase().includes(k)) { key = k; break; }
    }
    return { sessionId: `mock-${Date.now()}`, result: this.responses[key], tags: ['#mission-complete'], error: null };
  }
}

export function createProvider(type = 'auto') {
  if (type === 'mock') return new MockProvider();
  if (type === 'openclaw') return new OpenClawProvider();
  try { spawnSync('which', ['openclaw'], { stdio: 'ignore' }); return new OpenClawProvider(); }
  catch { return new MockProvider(); }
}
