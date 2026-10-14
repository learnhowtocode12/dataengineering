// Generates docs-ds/*.md from datastructures/concepts/*.py plus ds-meta.json.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const srcDir = path.resolve(here, '../../datastructures/concepts');
const outDir = path.resolve(here, '../docs-ds');
const meta = JSON.parse(fs.readFileSync(path.join(here, 'ds-meta.json'), 'utf8'));

fs.rmSync(outDir, {recursive: true, force: true});
fs.mkdirSync(outDir, {recursive: true});

const files = fs.readdirSync(srcDir).filter((f) => f.endsWith('.py')).sort();
const rows = [];

for (const file of files) {
  const key = file.replace(/\.py$/, '');
  const m = meta[key];
  if (!m) throw new Error(`Missing ds-meta.json entry for ${key}`);
  const code = fs.readFileSync(path.join(srcDir, file), 'utf8').replace(/\r\n/g, '\n').trimEnd();
  const doc = (code.match(/^\s*"""([\s\S]*?)"""/) || [, ''])[1].trim().replace(/\s*\n\s*/g, ' ');

  const body = [
    `# ${m.title}`,
    '',
    doc,
    '',
    '## Complexity',
    '',
    '| Operation | Time |',
    '|---|---|',
    ...m.ops.map(([op, t]) => `| ${op} | ${t} |`),
    '',
    '## When to use',
    '',
    m.use,
    '',
    '## When to avoid',
    '',
    m.avoid,
    '',
    '## Data engineering relevance',
    '',
    m.de,
    '',
    `## Code (\`${file}\`)`,
    '',
    '```python',
    code,
    '```',
    '',
  ].join('\n');
  fs.writeFileSync(path.join(outDir, `${key}.md`), body);
  rows.push(`| [${m.title}](${key}.md) | ${m.ops[0].join(': ')} | ${m.de.split(/[;.]/)[0]} |`);
}

const index = [
  '---',
  'slug: /',
  '---',
  '',
  '# Data Structures',
  '',
  'Each page has a concept summary, complexity table, usage guidance and the runnable Python source.',
  '',
  '**Suggested order:** linear structures (list, tuple, stack, queue, linked lists), then hashing (set, dict, hash table), then trees (binary tree, BST, AVL, heap, trie), then graphs.',
  '',
  '| Structure | Headline operation | Typical data engineering use |',
  '|---|---|---|',
  ...rows,
  '',
].join('\n');
fs.writeFileSync(path.join(outDir, '00_index.md'), index);
console.log(`Generated ${files.length} pages in docs-ds`);
