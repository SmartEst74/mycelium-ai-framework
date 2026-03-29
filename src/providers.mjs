/**
 * Providers — How Mycelium talks to agents.
 * OpenClawProvider calls gateway directly via child_process.
 * MockProvider returns deterministic responses for testing.
 * CircuitBreaker wraps any provider with fail-fast protection.
 */
import { spawnSync } from 'node:child_process';

class CircuitBreaker {
  constructor(threshold = 5, resetMs = 60_000) {
    this.threshold = threshold;
    this.resetMs = resetMs;
    this.failures = 0;
    this.lastFailure = 0;
    this.state = 'closed'; // closed | open | half-open
  }

  canExecute() {
    if (this.state === 'closed') return true;
    if (this.state === 'open' && Date.now() - this.lastFailure > this.resetMs) {
      this.state = 'half-open';
      return true;
    }
    return this.state === 'half-open';
  }

  recordSuccess() {
    this.failures = 0;
    this.state = 'closed';
  }

  recordFailure() {
    this.failures++;
    this.lastFailure = Date.now();
    if (this.failures >= this.threshold) this.state = 'open';
  }
}

export class OpenClawProvider {
  constructor(opts = {}) {
    this.timeoutSec = opts.timeoutSec || 300;
    this.maxRetries = opts.maxRetries || 2;
    this.breaker = new CircuitBreaker(opts.failThreshold || 5, opts.resetMs || 60_000);
  }

  spawnAgent({ model = 'kilocode/xiaomi/mimo-v2-pro:free', task = '', agentId = 'mycelium' }) {
    if (!this.breaker.canExecute()) {
      return {
        sessionId: `circuit-open-${Date.now()}`,
        result: null,
        tags: ['#pain-point'],
        error: 'Circuit breaker open — too many recent failures',
      };
    }

    const args = ['sessions', 'spawn', '--task', task, '--model', model, '--agent-id', agentId, '--mode', 'run'];
    let lastError = null;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const res = spawnSync('openclaw', args, {
          timeout: this.timeoutSec * 1000,
          encoding: 'utf8',
          maxBuffer: 10_485_760,
        });
        if (res.error) throw res.error;
        const output = (res.stdout || res.stderr || '').trim();
        const sm = output.match(/session[:\s]+([^\s]+)/i);

        if (res.status === 0) {
          this.breaker.recordSuccess();
          return {
            sessionId: sm?.[1] || `local-${Date.now()}`,
            result: output,
            tags: ['#mission-complete'],
            error: null,
          };
        }
        lastError = res.stderr || `Exit code ${res.status}`;
      } catch (e) {
        lastError = e.message;
      }

      // Exponential backoff between retries (100ms, 400ms)
      if (attempt < this.maxRetries) {
        const delay = 100 * Math.pow(2, attempt);
        spawnSync('sleep', [String(delay / 1000)]);
      }
    }

    this.breaker.recordFailure();
    return {
      sessionId: `err-${Date.now()}`,
      result: null,
      tags: ['#pain-point'],
      error: lastError,
    };
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
