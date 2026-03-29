/**
 * Minimal YAML parser — handles the subset used by config/models.yaml.
 * Supports: scalars, mappings, sequences (inline [] only), comments.
 * Zero dependencies. NOT a full YAML spec implementation.
 */
export function parse(text) {
  const lines = text.split('\n');
  const root = {};
  const stack = [{ indent: -1, obj: root }];

  for (const raw of lines) {
    const line = raw.replace(/#.*$/, '').trimEnd();
    if (!line.trim()) continue;

    const indent = line.search(/\S/);
    const content = line.trim();
    if (!content) continue;

    // Pop stack to correct parent
    while (stack.length > 1 && stack[stack.length - 1].indent >= indent) stack.pop();
    const parent = stack[stack.length - 1].obj;

    const match = content.match(/^([^:]+):\s*(.*)/);
    if (!match) continue;

    const key = match[1].trim();
    let val = match[2].trim();

    if (!val) {
      // Nested mapping
      const child = {};
      parent[key] = child;
      stack.push({ indent, obj: child });
    } else if (val.startsWith('[') && val.endsWith(']')) {
      // Inline sequence
      parent[key] = val.slice(1, -1).split(',').map(s => s.trim()).filter(Boolean);
    } else if (val.startsWith('"') && val.endsWith('"')) {
      parent[key] = val.slice(1, -1);
    } else if (val === 'true') {
      parent[key] = true;
    } else if (val === 'false') {
      parent[key] = false;
    } else if (!isNaN(val) && val !== '') {
      parent[key] = Number(val);
    } else {
      parent[key] = val;
    }
  }
  return root;
}
