#!/usr/bin/env node
import { Mycelium } from './mycelium.mjs';

const args = process.argv.slice(2);
const cmd = args[0];

const flags = {};
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--provider') flags.provider = args[++i];
  else if (args[i] === '--db') flags.db = args[++i];
  else if (args[i] === '--type') flags.type = args[++i];
  else if (args[i] === '--tag') flags.tag = args[++i];
  else if (args[i] === '--limit') flags.limit = parseInt(args[++i]);
}

const brain = new Mycelium({ providerType: flags.provider || 'mock', dbPath: flags.db || './lcm.db' });

switch (cmd) {
  case 'mission': {
    const desc = args[1];
    if (!desc) { console.error('Usage: mycelium mission "description"'); process.exit(1); }
    const caps = [];
    const ci = args.indexOf('--capabilities');
    if (ci > -1) for (let i = ci + 1; i < args.length && !args[i].startsWith('--'); i++) caps.push(args[i]);
    console.log(JSON.stringify(brain.executeMission(desc, caps.length ? caps : ['frontend', 'design']), null, 2));
    break;
  }
  case 'health':
    console.log(JSON.stringify(brain.checkColonyHealth(), null, 2));
    break;
  case 'scout': {
    const q = args.slice(1).filter(a => !a.startsWith('--')).join(' ');
    if (!q) { console.error('Usage: mycelium scout "query"'); process.exit(1); }
    console.log(JSON.stringify(brain.scout().research(q), null, 2));
    break;
  }
  case 'events': {
    const f = {};
    if (flags.type) f.type = flags.type;
    if (flags.tag) f.tags = [flags.tag];
    if (flags.limit) f.limit = flags.limit;
    for (const e of brain.rhizo.query(f)) console.log(`[${e.seq}] ${e.type} @ ${e.timestamp} by ${e.agent} ${e.tags.join(' ')}`);
    break;
  }
  default:
    console.log(`Mycelium — Colonial AI Agent Orchestrator\n\nCommands:\n  mission <desc>   Execute a mission\n  health           Check colony health\n  scout <query>    Scout research\n  events           Query events\n  replay           Replay all events`);
}
brain.close();
