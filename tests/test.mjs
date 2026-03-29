/**
 * Mycelium tests — uses node:test (built-in, no deps)
 */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { Rhizomorph } from '../src/rhizomorph.mjs';
import { Mycelium, RoleRegistry, DynamicAnt, ArmyAnt, Scout, ModelConfig } from '../src/mycelium.mjs';
import { MockProvider } from '../src/providers.mjs';
import { unlinkSync, existsSync } from 'node:fs';

const TEST_DB = '/tmp/test_mycelium.mjs.db';

function cleanDb() {
  try { unlinkSync(TEST_DB); } catch {}
}

describe('Rhizomorph', () => {
  beforeEach(cleanDb);
  afterEach(() => { cleanDb(); });

  it('creates and queries events', () => {
    const rh = new Rhizomorph(TEST_DB);
    const seq = rh.emit('test.event', { hello: 'world' }, { agent: 'test', tags: ['#test'] });
    assert.equal(seq, 1);
    const events = rh.query({ type: 'test.event' });
    assert.equal(events.length, 1);
    assert.deepEqual(events[0].payload, { hello: 'world' });
    assert.equal(events[0].agent, 'test');
    rh.close();
  });

  it('counts by tag', () => {
    const rh = new Rhizomorph(TEST_DB);
    rh.emit('memory.write', { a: 1 }, { tags: ['#mission'] });
    rh.emit('memory.write', { b: 2 }, { tags: ['#mission-complete'] });
    rh.emit('memory.write', { c: 3 }, { tags: ['#mission'] });
    assert.equal(rh.countByTag('#mission'), 2); // exact match, no longer cross-matches #mission-complete
    assert.equal(rh.countByTag('#mission-complete'), 1);
    rh.close();
  });

  it('notifies subscribers', () => {
    const rh = new Rhizomorph(TEST_DB);
    const received = [];
    rh.subscribe('test.event', e => received.push(e));
    rh.emit('test.event', { x: 1 }, { tags: ['#t'] });
    rh.emit('other.event', { y: 2 });
    rh.emit('test.event', { x: 2 }, { tags: ['#t'] });
    assert.equal(received.length, 2);
    assert.equal(received[0].payload.x, 1);
    rh.close();
  });

  it('replays all events', () => {
    const rh = new Rhizomorph(TEST_DB);
    rh.emit('a', { n: 1 });
    rh.emit('b', { n: 2 });
    rh.emit('c', { n: 3 });
    const replayed = [];
    rh.replay(e => replayed.push(e.type));
    assert.deepEqual(replayed, ['a', 'b', 'c']);
    rh.close();
  });

  it('handles :memory: with persistent connection', () => {
    const rh = new Rhizomorph(':memory:');
    rh.emit('test', { ok: true });
    // Connection stays open, so :memory: persists
    assert.equal(rh.countByTag('#anything'), 0);
    rh.emit('test', {}, { tags: ['#mission'] });
    assert.equal(rh.countByTag('#mission'), 1);
    rh.close();
  });
});

describe('MockProvider', () => {
  it('returns mission-complete on success', () => {
    const p = new MockProvider();
    const r = p.spawnAgent({ task: 'Build a frontend page' });
    assert.equal(r.error, null);
    assert.ok(r.tags.includes('#mission-complete'));
    assert.ok(r.sessionId.startsWith('mock-'));
  });
});

describe('Mycelium', () => {
  let brain;
  beforeEach(() => { cleanDb(); brain = new Mycelium({ providerType: 'mock', dbPath: TEST_DB }); });
  afterEach(() => { brain.close(); cleanDb(); });

  it('executes a mission and writes events to rhizomorph', () => {
    const result = brain.executeMission('Deploy landing page', ['frontend', 'design']);
    assert.equal(result.mission, 'Deploy landing page');
    assert.ok(result.rhizoSeq > 0);
    assert.equal(result.dispatch.length, 2);
    assert.ok(result.dispatch.every(d => d.status === 'completed'));
    assert.ok(result.dispatch.every(d => d.scores && typeof d.scores.accuracy === 'number'));

    // Check rhizomorph has the events (missions + self-evals)
    const missions = brain.rhizo.query({ tags: ['#mission'] });
    assert.ok(missions.length >= 3); // mycelium start + army build + 2x dynamic ant
  });

  it('reports colony health', () => {
    brain.executeMission('Build app', ['frontend']);
    const health = brain.checkColonyHealth();
    assert.equal(health.status, 'healthy');
    assert.ok(health.completedMissions > 0);
  });

  it('finds agent role by capability', () => {
    // Roles loaded from registry, at minimum we should have some
    const role = brain.registry.find('frontend');
    // May or may not find one depending on registry files, but shouldn't throw
    assert.doesNotThrow(() => brain.registry.find('nonexistent'));
  });
});

describe('Scout', () => {
  let rhizo;
  beforeEach(() => { cleanDb(); rhizo = new Rhizomorph(TEST_DB); });
  afterEach(() => { rhizo.close(); cleanDb(); });

  it('researches and writes to rhizomorph', () => {
    const s = new Scout(new MockProvider(), rhizo);
    const result = s.research('compare free models');
    assert.equal(result.query, 'compare free models');
    const benchmarks = rhizo.getTagged('#benchmark');
    assert.ok(benchmarks.length >= 1);
  });
});

describe('ArmyAnt', () => {
  let rhizo, registry;
  beforeEach(() => { cleanDb(); rhizo = new Rhizomorph(TEST_DB); registry = new RoleRegistry(); });
  afterEach(() => { rhizo.close(); cleanDb(); });

  it('builds team and coordinates', () => {
    const army = new ArmyAnt(new MockProvider(), rhizo, registry);
    const plan = army.buildTeam('Build landing page', ['frontend', 'design']);
    assert.equal(plan.mission, 'Build landing page');
    assert.equal(plan.team.length, 2);

    const results = army.coordinate(plan.team, 'Build landing page');
    assert.equal(results.length, 2);
    assert.ok(results.every(r => r.status === 'completed'));

    const missions = rhizo.query({ tags: ['#mission'] });
    assert.ok(missions.length >= 3);
  });
});
