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
    for (const token of ['Cycle 4 is forbidden', '2-round rework budget', 'ARBITRATION_REQUIRED',
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

// -----------------------------------------------------------------------------
// v2.0.0 review-contract invariants (Context/Self-check/Sweep report fields,
// RV-ID finding schema, coordinator Required-reading + Context gate, Step 0
// documentation inventory, and the review-contract skill package itself).
// -----------------------------------------------------------------------------

const agentNames = fs.readdirSync(path.join(root, 'agents'))
  .filter(f => f.endsWith('.md'))
  .map(f => f.replace(/\.md$/, ''));

test('STATIC CX-005: every agent report carries a Context field naming required reading', () => {
  assert.equal(agentNames.length, 12);
  for (const name of agentNames) {
    const text = read(`agents/${name}.md`);
    assert.match(text, /^Context:[\s\S]{0,400}?required reading/im, `${name}: Context field must name required reading`);
  }
});

test('STATIC CX-006: Self-check and Sweep fields are scoped to the right agents', () => {
  const selfCheckAgents = ['backend-dev', 'frontend-dev', 'implementor', 'devops-engineer', 'tester'];
  const sweepAgents = ['code-reviewer', 'doc-reviewer'];
  for (const name of selfCheckAgents) {
    assert.match(read(`agents/${name}.md`), /^Self-check:/m, `${name}: missing Self-check field`);
  }
  for (const name of sweepAgents) {
    assert.match(read(`agents/${name}.md`), /^Sweep:/m, `${name}: missing Sweep field`);
  }
  const adversarial = read('agents/adversarial-reviewer.md');
  assert.doesNotMatch(adversarial, /^Self-check:/m, 'adversarial-reviewer must not carry a Self-check field');
  assert.doesNotMatch(adversarial, /^Sweep:/m, 'adversarial-reviewer must not carry a Sweep field');
});

test('STATIC CX-007: code-reviewer and doc-reviewer carry the RV-ID finding schema, all classes, and the late-finding rationale rule', () => {
  for (const name of ['code-reviewer', 'doc-reviewer']) {
    const text = read(`agents/${name}.md`);
    assert.match(text, /RV-<scope>-NNN/, `${name}: missing RV-<scope>-NNN grammar`);
    for (const cls of ['must-fix-now', 'fix-in-slice', 'backlog']) {
      assert.match(text, new RegExp('[`*]{1,2}' + cls + '[`*]{1,2}'), `${name}: missing finding class ${cls}`);
    }
    assert.match(text, /MUST carry exactly ONE of two rationale lines/, `${name}: missing corrected late-finding rationale rule (exactly one of two forms, not a bare 'a rationale line')`);
    assert.match(text, /Introduced by:\s*<the rework change that created it>/, `${name}: missing 'Introduced by:' rationale form for case (a)`);
    assert.match(text, /Pre-existing Critical:\s*<the reachable impact/, `${name}: missing 'Pre-existing Critical:' rationale form for case (b)`);
    assert.match(text, /carrying neither line is invalid/, `${name}: missing 'carrying neither line is invalid' clause — a finding with neither form must be filed as backlog, not forced into 'Introduced by:'`);
    assert.doesNotMatch(text, /MUST carry a rationale line/, `${name}: the old self-cancelling phrasing ('MUST carry a rationale line', which forced every case (b) finding to fabricate an 'Introduced by:' line) must not return`);
  }
});

test('STATIC CX-008: adversarial-reviewer keeps its own CH-* protocol and is explicitly not governed by RV-ID', () => {
  const text = read('agents/adversarial-reviewer.md');
  assert.match(text, /own `CH-\*` debate protocol/, 'adversarial-reviewer must state it keeps its own CH-* protocol');
  assert.match(text, /not governed by[\s\S]{0,60}RV-ID/, 'adversarial-reviewer must state it is not governed by the RV-ID schema');
});

test('STATIC CX-009: coordinator skills carry the Required-reading rule, Context gate, and RV-ID contract identically', () => {
  const names = ['dev-team', 'dev-team-node', 'dev-team-python'];
  const stripFrontmatterAndStackProfile = text => text
    .replace(/^---\n[\s\S]*?\n---\n/, '')
    .replace(/## Stack Profile\n[\s\S]*?(?=\n## )/, '');
  const stripped = {};
  for (const name of names) {
    const text = read(`skills/${name}/SKILL.md`);
    assert.match(text, /\*\*Required reading\*\*/, `${name}: missing Required-reading rule`);
    assert.ok(text.includes('Never write "read the documentation"'), `${name}: missing prohibition on writing "read the documentation"`);
    assert.match(text, /Context gate/, `${name}: missing Context gate`);
    assert.match(text, /RV-<scope>-NNN/, `${name}: missing RV-ID contract`);
    stripped[name] = stripFrontmatterAndStackProfile(text);
  }
  assert.ok(stripped['dev-team'].length > 0, 'stripped dev-team body must not be empty');
  assert.equal(stripped['dev-team-node'], stripped['dev-team'], 'dev-team-node diverges from dev-team outside frontmatter/Stack Profile');
  assert.equal(stripped['dev-team-python'], stripped['dev-team'], 'dev-team-python diverges from dev-team outside frontmatter/Stack Profile');
});

test('STATIC CX-010: document agents inventory existing docs via Glob before writing', () => {
  for (const name of ['product-analyst', 'architect', 'planner', 'ui-ux-designer']) {
    const text = read(`agents/${name}.md`);
    assert.match(text, /Glob\('docs\/\*\*\/\*\.md'\)/, `${name}: missing Step 0 documentation-inventory Glob call`);
  }
});

test('STATIC CX-011: review-contract skill exists with its three reference files', () => {
  const text = read('skills/review-contract/SKILL.md');
  assert.match(text, /^name:\s*review-contract\s*$/m, 'skills/review-contract/SKILL.md frontmatter must declare name: review-contract');
  for (const ref of ['code-dimensions.md', 'doc-dimensions.md', 'finding-schema.md']) {
    assert.ok(fs.existsSync(path.join(root, `skills/review-contract/references/${ref}`)), `missing skills/review-contract/references/${ref}`);
  }
});

// -----------------------------------------------------------------------------
// v2.0.0 review-contract fix-subtask corrections: both late-finding rationale
// forms, the reclassified carry-forward state, fix-in-slice/backlog closure and
// destination, Micro/MICRO behaviour, coordinator Required-reading/Context-gate/
// Review-state identity, the document agents' bounded Step 0, code-reviewer's
// full status set, skill-relative references, and the ask-* RV-ID contract.
// -----------------------------------------------------------------------------

const norm = text => text.replace(/\s+/g, ' ');
const askNames = shared.filter(n => n.startsWith('ask-'));

test('STATIC CX-012: both reviewers and the review-contract skill define both late-finding rationale forms', () => {
  for (const file of ['agents/code-reviewer.md', 'agents/doc-reviewer.md', 'skills/review-contract/SKILL.md']) {
    const text = read(file);
    assert.match(text, /Introduced by:/, `${file}: missing 'Introduced by:' rationale form (case a)`);
    assert.match(text, /Pre-existing Critical:/, `${file}: missing 'Pre-existing Critical:' rationale form (case b)`);
  }
});

test('STATIC CX-013: the reclassified carry-forward state exists in the skill and both reviewers', () => {
  for (const file of ['agents/code-reviewer.md', 'agents/doc-reviewer.md', 'skills/review-contract/SKILL.md']) {
    assert.match(read(file), /reclassified → <new class>/, `${file}: missing 'reclassified → <new class>' carry-forward state`);
  }
});

test('STATIC CX-014: the skill defines the fix-in-slice DoD-gate closure and backlog destination; coordinators carry the matching closure and ledger destination', () => {
  const skill = norm(read('skills/review-contract/SKILL.md'));
  assert.match(skill, /\*\*Closure:\*\* before slice N's Definition-of-Done gate passes, every open `fix-in-slice` finding for that slice is either fixed or explicitly re-classed `backlog`/, 'review-contract skill: missing fix-in-slice DoD-gate closure rule');
  assert.match(skill, /\*\*Destination:\*\* the `### Technical debt` section of `docs\/progress\.md`/, 'review-contract skill: missing backlog destination');
  for (const name of ['dev-team', 'dev-team-node', 'dev-team-python']) {
    const text = norm(read(`skills/${name}/SKILL.md`));
    assert.match(text, /Every open `fix-in-slice` finding from slice N's reviews is fixed or explicitly re-classed `backlog` with a recorded reason before slice N\+1 starts/, `${name}: missing matching DoD-gate fix-in-slice closure`);
    assert.match(text, /`### Technical debt` in `docs\/progress\.md` \(not the task table\) lists every `backlog`-classed finding/, `${name}: missing matching Technical-debt ledger destination`);
  }
});

test('STATIC CX-015: the skill defines Micro-profile review behaviour including the MICRO scope tag', () => {
  const skill = norm(read('skills/review-contract/SKILL.md'));
  assert.match(skill, /Under the Micro profile \(no slices, no `docs\/progress\.md`\), a review emits only/, 'missing Micro-profile review behaviour');
  assert.match(skill, /`fix-in-slice` has no referent because no slice exists\. Use scope tag `MICRO`/, 'missing MICRO scope tag rule');
});

test('STATIC CX-016: coordinators carry the Required-reading tool-grant rule, the Context-gate unreachable-source escape, and a coordinator-owned Review-state item, identically', () => {
  for (const name of ['dev-team', 'dev-team-node', 'dev-team-python']) {
    const text = read(`skills/${name}/SKILL.md`);
    assert.match(text, /never name a shell command for a Read\/Grep\/Glob-only agent \(code-reviewer, doc-reviewer, adversarial-reviewer\); paste the command's output into the prompt instead/, `${name}: missing Required-reading tool-grant rule`);
    assert.match(text, /A source the agent's tool grant cannot reach is accounted for as `<path> → unreachable with this agent's tools` and does not fail the gate/, `${name}: missing Context-gate unreachable-source escape`);
    assert.match(text, /\*\*Review state\*\*: for every review or recheck dispatch \(ordinary or debate\), the coordinator — not the reviewer — owns the scope tag and the next free number/, `${name}: missing coordinator-owned Review-state item`);
  }
});

test('STATIC CX-017: the four document agents\' Step 0 reads the five normative documents in full and bounds the rest to a one-line skim', () => {
  for (const name of ['product-analyst', 'architect', 'planner', 'ui-ux-designer']) {
    const text = norm(read(`agents/${name}.md`));
    assert.match(text, /Read `docs\/prd\.md`, `docs\/use-cases\.md`, `docs\/architecture\.md`, `docs\/design\.md`, and `docs\/plan\.md` in full when present/, `${name}: Step 0 must read the five normative documents in full`);
    assert.match(text, /Run `Glob\('docs\/\*\*\/\*\.md'\)`, skim every other document it returns, and account for each with one line in `Context:`/, `${name}: Step 0 must bound the rest to a Glob plus one-line skim, not "read every document"`);
  }
});

test('STATIC CX-018: code-reviewer carries all four statuses including NEEDS_CONTEXT and a Questions field', () => {
  const text = read('agents/code-reviewer.md');
  assert.match(text, /Status: DONE \| DONE_WITH_CONCERNS \| BLOCKED \| NEEDS_CONTEXT/, 'code-reviewer: missing the full status set including NEEDS_CONTEXT');
  assert.match(text, /^Questions:/m, 'code-reviewer: missing the Questions: report field');
});

test('STATIC CX-019: no agents/ or templates/ file references review-contract by a repo-rooted path', () => {
  for (const dir of ['agents', 'templates']) {
    const files = fs.readdirSync(path.join(root, dir)).filter(f => f.endsWith('.md'));
    for (const file of files) {
      const text = read(`${dir}/${file}`);
      assert.doesNotMatch(text, /skills\/review-contract\//, `${dir}/${file}: references review-contract by a repo-rooted path instead of by skill name — breaks when the installed plugin runs with the user's project as cwd`);
    }
  }
});

test('STATIC CX-020: all eleven ask-* skills carry the Required-reading obligation and the RV-ID rework contract', () => {
  assert.equal(askNames.length, 11);
  for (const name of askNames) {
    const text = read(`skills/${name}/SKILL.md`);
    assert.match(text, /\*\*Required reading\*\*/, `${name}: missing Required-reading obligation`);
    assert.match(text, /RV-<scope>-NNN|RV-PRD-NNN|RV-PLAN-NNN/, `${name}: missing RV-ID rework contract`);
    assert.match(text, /rework budget/, `${name}: missing rework-budget language`);
  }
});
