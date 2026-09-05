// Static instruction/package contracts. These do not prove model execution.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const baseline = require('./baseline.json');
const root = path.resolve(__dirname, '../..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8').replace(/\r\n/g, '\n');
const hash = text => crypto.createHash('sha256').update(text).digest('hex');
const bridge = () => read('skills/dev-team-codex/SKILL.md');
const shared = Object.keys(baseline.shared);
const entryPattern = /<!-- codex-entry:start -->\n[\s\S]*?<!-- codex-entry:end -->\n\n/g;

test('STATIC CX-003: shared Claude workflows are byte-preserved outside one bounded entry', () => {
  assert.equal(shared.length, 14);
  for (const name of shared) {
    const text = read(`skills/${name}/SKILL.md`);
    const blocks = text.match(entryPattern) || [];
    assert.equal(blocks.length, 1, `${name}: exactly one Codex entry block`);
    const block = blocks[0];
    assert.match(block, /Codex/);
    assert.match(block, /dev-team-codex/);
    assert.match(block, /template/i, `${name}: recursive template reads must bypass routing`);
    assert.ok(block.length < 1600, `${name}: routing must stay short`);
    assert.equal(hash(text.replace(entryPattern, '')), baseline.shared[name], `${name}: Claude text/frontmatter changed`);
  }
});

test('STATIC CX-003: Claude agents, manifests, continuity skills and model runners remain intact', () => {
  for (const [file, expected] of Object.entries(baseline.preserved)) {
    assert.equal(hash(read(file)), expected, file);
  }
});

test('STATIC CX-002: fourteen direct entrypoints are explicit-only and bridge remains automatic', () => {
  for (const name of shared) {
    assert.match(read(`skills/${name}/agents/openai.yaml`), /policy:\s*\n\s+allow_implicit_invocation:\s*false\s*(?:\n|$)/, name);
  }
  const metadata = path.join(root, 'skills/dev-team-codex/agents/openai.yaml');
  if (fs.existsSync(metadata)) assert.doesNotMatch(fs.readFileSync(metadata, 'utf8'), /allow_implicit_invocation:\s*false/);
});

test('STATIC CX-002: every alias selects its shared workflow including continuity', () => {
  for (const name of [...shared, 'handoff', 'resume']) {
    assert.ok(bridge().includes(`skills/${name}/SKILL.md`), `missing route to ${name}`);
  }
  assert.match(bridge(), /\$ARGUMENTS/);
  assert.match(bridge(), /original (?:user )?(?:request|task)|user(?:'s)? (?:request|task)/i);
  assert.match(bridge(), /template/i);
});

test('STATIC CX-002: installed package paths are distinct from project working directory', () => {
  assert.match(bridge(), /PLUGIN_ROOT/);
  assert.match(bridge(), /PROJECT_ROOT/);
  assert.match(bridge(), /missing[\s\S]{0,200}BLOCKED|BLOCKED[\s\S]{0,200}missing/i);
  assert.match(read('README.md'), /marketplace/i);
  assert.doesNotMatch(read('README.md'), /cp\s+-r\s+skills\/\*/);
});

// Check the actual package inventory relative to a known installed entry file.
// This checks files only, not whether a Codex model resolves paths correctly.
function requirePackage(entry) {
  const packageRoot = path.resolve(path.dirname(entry), '../..');
  const required = ['.codex-plugin/plugin.json', ...shared.map(n => `skills/${n}/SKILL.md`),
    'skills/handoff/SKILL.md', 'skills/resume/SKILL.md',
    ...Object.keys(baseline.preserved).filter(n => n.startsWith('agents/'))];
  for (const file of required) assert.ok(fs.existsSync(path.join(packageRoot, file)), `Incomplete plugin package: ${file}`);
  return packageRoot;
}

test('STATIC CX-002: complete package resolves from alien cwd; skills-only package is rejected', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'dev-team-package-contract-'));
  const previousCwd = process.cwd();
  try {
    process.chdir(temp);
    assert.equal(requirePackage(path.join(root, 'skills/dev-team-codex/SKILL.md')), root);
    const entry = path.join(temp, 'partial/skills/dev-team-codex/SKILL.md');
    fs.mkdirSync(path.dirname(entry), { recursive: true });
    fs.copyFileSync(path.join(root, 'skills/dev-team-codex/SKILL.md'), entry);
    assert.throws(() => requirePackage(entry), /Incomplete plugin package/);
  } finally {
    process.chdir(previousCwd);
    fs.rmSync(temp, { recursive: true, force: true });
  }
});

test('STATIC CX-002: dispatch uses advertised schema with explicit context isolation', () => {
  const text = bridge();
  assert.match(text, /schema/);
  assert.match(text, /task_name/);
  assert.match(text, /message/);
  assert.match(text, /fork_turns\s*[:=]\s*["']none["']/);
  assert.match(text, /model[\s\S]*color[\s\S]*tools/);
  assert.match(text, /inherit/i);
  assert.doesNotMatch(text, /Spawn a Codex sub-agent with `spawn_agent\(agent_type="worker"/);
  assert.match(text, /BLOCKED/);
  assert.match(text, /(?:never|do not|must not)[\s\S]{0,130}(?:substitute|replace|impersonate|inline)/i);
});

test('STATIC CX-002: continuation, interruption, slots and review write checks are explicit', () => {
  const text = bridge();
  for (const token of ['followup_task', 'wait_agent', 'interrupt_agent', 'list_agents']) assert.ok(text.includes(token), token);
  assert.match(text, /run counter/i);
  assert.match(text, /slot|capacity/);
  assert.match(text, /read-only/);
  assert.match(text, /before[\s\S]{0,300}(?:after|post-review)/i);
  assert.match(text, /hash|fingerprint/i);
  assert.match(text, /untracked/i);
});

test('STATIC CX-004: thin bridge delegates gates and Evidence to canonical sources', () => {
  const text = bridge();
  assert.ok(text.split(/\s+/).length < 2000, 'bridge must remain below skill word budget');
  assert.match(text, /source of truth|authoritative|canonical/);
  assert.match(text, /out-of-scope/);
  assert.match(text, /Evidence/);
  assert.match(text, /use-cases\.md/);
  assert.match(text, /\/ask-prd/);
  assert.match(text, /\/ask-planner/);
  assert.doesNotMatch(text, /^## Coordinator workflow in Codex/m, 'do not retain a competing pipeline');
});

test('STATIC CX-004: shared workflow still owns proportional debate, limits and PRD/catalogue gate', () => {
  for (const name of ['dev-team', 'dev-team-node', 'dev-team-python']) {
    const text = read(`skills/${name}/SKILL.md`);
    for (const token of ['**Light**', '**Standard**', '**Deep**', 'Micro/Standard: 8 runs', 'Full: 40 runs',
      '6 implementation dispatches', 'out-of-scope', 'docs/use-cases.md', 'one adversarial debate', 'one ordinary doc-review']) {
      assert.ok(text.includes(token), `${name}: ${token}`);
    }
  }
  for (const name of ['ask-prd', 'ask-planner']) {
    const text = read(`skills/${name}/SKILL.md`);
    for (const token of ['Cycle 4 is forbidden', 'maximum 2 ordinary reworks', 'ARBITRATION_REQUIRED',
      'without restarting debate', 'create neither `docs/progress.md` nor a challenge file']) assert.ok(text.includes(token), `${name}: ${token}`);
  }
});

test('STATIC CX-004: unrelated adversarial cases and material-restart expectations are preserved', () => {
  const suite = JSON.parse(read('evals/cases/adversarial-planning-v1.json'));
  const other = suite.evals.filter(c => !['AP-006', 'AP-M006'].includes(c.id));
  assert.deepEqual(other.map(c => c.id), Object.keys(baseline.otherAdversarialCases));
  for (const item of other) assert.equal(hash(JSON.stringify(item)), baseline.otherAdversarialCases[item.id], item.id);
  assert.deepEqual(suite.evals.find(c => c.id === 'AP-M006').expected, baseline.materialRestartExpected);
});
