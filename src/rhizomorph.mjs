/**
 * Rhizomorph — Event-sourced shared memory for AI colonies.
 * Append-only SQLite event store with subscriber notifications.
 * Uses node:sqlite (built-in, no external deps).
 */
import { DatabaseSync } from 'node:sqlite';

export class Rhizomorph {
  constructor(dbPath = './lcm.db') {
    this.db = new DatabaseSync(dbPath);
    this.db.exec('PRAGMA journal_mode = WAL');
    this.db.exec('PRAGMA busy_timeout = 5000');
    this.db.exec('PRAGMA synchronous = NORMAL');
    this._subscribers = new Map();
    this._initStore();
  }

  _initStore() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS events (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        payload TEXT NOT NULL,
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        agent TEXT NOT NULL DEFAULT '',
        tags TEXT NOT NULL DEFAULT '[]'
      )
    `);
    this.db.exec('CREATE INDEX IF NOT EXISTS idx_type ON events(type)');
    this.db.exec('CREATE INDEX IF NOT EXISTS idx_agent ON events(agent)');
  }

  emit(type, payload, opts = {}) {
    const { agent = '', tags = [] } = opts;
    const stmt = this.db.prepare(
      'INSERT INTO events (type, payload, agent, tags) VALUES (?, ?, ?, ?)'
    );
    const res = stmt.run(type, JSON.stringify(payload), agent, JSON.stringify(tags));
    const seq = Number(res.lastInsertRowid);

    for (const [pattern, handler] of this._subscribers) {
      if (type === pattern || pattern === '*') {
        try { handler({ type, payload, agent, tags, seq }); } catch {}
      }
    }
    return seq;
  }

  subscribe(pattern, handler) {
    this._subscribers.set(pattern, handler);
    return () => this._subscribers.delete(pattern);
  }

  query(filters = {}) {
    let sql = 'SELECT * FROM events WHERE 1=1';
    const p = [];
    if (filters.type) { sql += ' AND type = ?'; p.push(filters.type); }
    if (filters.agent) { sql += ' AND agent = ?'; p.push(filters.agent); }
    if (filters.tags) { sql += ' AND tags LIKE ?'; p.push(`%${filters.tags[0]}%`); }
    sql += ' ORDER BY seq ASC';
    if (filters.limit) { sql += ' LIMIT ?'; p.push(filters.limit); }
    return this.db.prepare(sql).all(...p).map(r => ({
      ...r, payload: JSON.parse(r.payload), tags: JSON.parse(r.tags)
    }));
  }

  replay(handler) {
    for (const row of this.db.prepare('SELECT * FROM events ORDER BY seq ASC').iterate()) {
      handler({ ...row, payload: JSON.parse(row.payload), tags: JSON.parse(row.tags) });
    }
  }

  getTagged(tag, limit = 100) { return this.query({ tags: [tag], limit }); }

  countByTag(tag) {
    return this.db.prepare('SELECT COUNT(*) as c FROM events WHERE tags LIKE ?').get(`%${tag}%`).c;
  }

  get seq() {
    return this.db.prepare('SELECT COALESCE(MAX(seq), 0) as s FROM events').get().s;
  }

  close() { this.db.close(); }
}
