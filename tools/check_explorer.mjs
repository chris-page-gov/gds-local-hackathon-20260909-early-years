#!/usr/bin/env node
/** Actual URL-based Svelte acceptance. Uses the selected Explorer's Playwright. */
import { parseArgs } from 'node:util';
import { createRequire } from 'node:module';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { values } = parseArgs({ options: {
  explorer: { type: 'string', default: resolve(root, '../okf-explorer') },
  'base-url': { type: 'string', default: 'http://127.0.0.1:4175/explore/' },
  out: { type: 'string', default: resolve(root, 'output/explorer') },
  browser: { type: 'string', default: 'chrome' }
} });
if (!['chrome', 'chromium'].includes(values.browser)) throw new Error('Use --browser chrome or chromium');
const explorer = resolve(values.explorer);
const require = createRequire(resolve(explorer, 'apps/okf-explorer/package.json'));
const { chromium } = require('@playwright/test');
const axeRequire = createRequire(require.resolve('@axe-core/playwright'));
const output = resolve(values.out);
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true, ...(values.browser === 'chrome' ? { channel: 'chrome' } : {}) });
try {
  const page = await browser.newPage();
  const receipt = await checkExplorer(page, { output, local: values['base-url'], axePath: axeRequire.resolve('axe-core/axe.min.js') });
  receipt.explorerCommit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: explorer, encoding: 'utf8' }).trim();
  receipt.bundleSha256 = createHash('sha256').update(await readFile(resolve(root, 'bundle/okf-bundle.json'))).digest('hex');
  await writeFile(resolve(output, 'acceptance.json'), JSON.stringify(receipt, null, 2) + '\n');
  console.log(JSON.stringify({ passed: receipt.passed, checks: receipt.checks.map(({name,result,error})=>({name,result,error})) }, null, 2));
  if (!receipt.passed) process.exitCode = 1;
} finally { await browser.close(); }

async function checkExplorer(page, { output, local, axePath }) {
  const bundle = new URL('/rehearsal/bundle/okf-bundle.json', local).href;
  const smallUrl = local + '?bundle=' + encodeURIComponent(bundle) + '#record/h-01';
  const context = await page.context().browser().newContext({ viewport: { width: 1440, height: 1000 }, hasTouch: true, serviceWorkers: 'block' });
  await context.tracing.start({ screenshots: true, snapshots: true });
  const p = await context.newPage();
  const errors = [];
  p.on('pageerror', error => errors.push(error.message));
  const checks = [];
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const test = async (name, action) => { try { checks.push({ name, result: 'passed', evidence: await action() }); } catch (error) { checks.push({ name, result: 'failed', error: String(error) }); } };
  const records = () => p.locator('[data-okf-ranked-results="primary"] [data-okf-ranked-result]');
  const facet = (key, value) => p.locator('[data-facet-key="' + key + '"] .facet-value').filter({ hasText: value });
  const count = async (highlighted, scope) => { await p.getByText(highlighted + ' highlighted / ' + scope + ' in scope', { exact: true }).waitFor({ timeout: 12000 }); };
  const openSmall = async () => { await p.setViewportSize({ width: 1440, height: 1000 }); await p.goto('about:blank'); const r = await p.goto(smallUrl); await records().first().waitFor();
    assert(await p.locator('.facet-toggle[aria-expanded="true"]').count() === 0, 'New bundle opened expanded facets');
    await p.getByRole('tab', { name: 'Results', exact: true }).click();
    assert(await p.locator('.sort-control select').inputValue() === 'title', 'New bundle did not default to Title');
    await p.getByRole('tab', { name: 'Facets', exact: true }).click();
    await p.locator('[data-facet-key="type"] .facet-toggle').click(); return r.status(); };
  try {
    await test('Actual URL navigation and synthetic fixture identity', async () => {
      const status = await openSmall(); const identity = await p.evaluate(async url => { const r = await fetch(url); const b = await r.json(); return { status: r.status, nodes: Object.values(b.corpora).reduce((sum, c) => sum + Object.keys(c.nodes).length, 0), relationships: Object.values(b.corpora).reduce((sum, c) => sum + c.relationships.length, 0), executed: Boolean(window.__fixtureExecuted) }; }, bundle);
      assert(status === 200 && identity.nodes === 22 && identity.relationships === 23 && !identity.executed, 'Fixture identity or inert-text boundary failed');
      return { url: p.url(), status, identity, cards: await records().count() };
    });
    await test('Replace within facet, modifier OR, cross-facet AND, auto-fold and zero preview', async () => {
      await openSmall(); await facet('type', 'Source record').click(); await count(11, 22);
      assert((await records().count()) === 22, 'Preview reduced the scope');
      assert((await records().first().innerText()).includes('Source record'), 'Highlight did not move first');
      await facet('type', 'Support action').click({ modifiers: [process.platform === 'darwin' ? 'Meta' : 'Control'] }); await count(14, 22);
      await facet('type', 'Candidate record link').click(); await count(3, 22);
      await p.locator('[data-facet-key="section"] .facet-toggle').click(); await facet('section', 'candidate').click(); await count(3, 22);
      assert((await p.locator('[data-facet-key="type"] .facet-toggle').getAttribute('aria-expanded')) === 'false', 'Previous facet did not fold');
      await p.locator('[data-facet-key="type"] .facet-toggle').click(); await facet('type', 'Source record').click(); await count(0, 22);
      return { cards: await records().count(), state: await p.locator('.exploration-toolbar').innerText(), url: p.url() };
    });
    await test('Double click keeps, repeated keep is non-destructive, Undo and reload preserve scope', async () => {
      await openSmall(); await facet('type', 'Source record').dblclick(); await count(0, 11);
      const keptUrl = p.url(); await p.reload(); await count(0, 11);
      await p.locator('[data-facet-key="type"] .facet-toggle').click();
      await facet('type', 'Source record').dblclick(); await count(0, 11);
      await p.getByRole('button', { name: 'Undo keep (2)', exact: true }).click(); await count(11, 11);
      await p.getByRole('button', { name: 'Undo keep (1)', exact: true }).click(); await count(11, 22);
      return { keptUrl, restored: await records().count() };
    });
    await test('Presentation folds preserve membership and update their bars', async () => {
      await openSmall(); await facet('type', 'Source record').click(); await p.getByRole('button', { name: 'Fold highlighted', exact: true }).click();
      assert(await records().count() === 11, 'Fold did not hide exactly eleven records'); await count(11, 22);
      await facet('type', 'Support action').click(); await count(3, 22);
      const summary = await p.locator('.folded-set').innerText(); assert(summary.includes('0 highlighted / 11 in scope'), 'Fold membership changed with preview');
      await p.locator('.folded-set').getByRole('button', { name: /Unfold/ }).click(); assert(await records().count() === 22, 'Unfold lost records');
      await p.getByRole('button', { name: 'Keep unhighlighted', exact: true }).click(); await count(0, 19);
      return { summary, complement: await records().count() };
    });
    await test('Displayed record, pin and graph focus agree; inspection preserves graph membership', async () => {
      await openSmall(); await records().filter({ hasText: 'C-01 — H-01 / E-01' }).getByRole('button').click();
      await p.getByRole('button', { name: 'Pin', exact: true }).click();
      const pin = await p.evaluate(() => JSON.parse(localStorage.getItem('okf-explorer:bookmarks:v2'))[0]);
      assert(pin.route === 'candidate/c-01' && pin.bundle === bundle, 'Pin targets another record or bundle');
      await p.getByLabel('Views').getByRole('button', { name: 'Graph', exact: true }).click();
      const graph = p.locator('.stage svg.graph'); await graph.waitFor(); const before = await graph.locator('[data-route]').evaluateAll(es => es.map(e => e.getAttribute('data-route')).sort());
      await graph.locator('[data-route="record/h-01"]').press('Enter');
      const after = await graph.locator('[data-route]').evaluateAll(es => es.map(e => e.getAttribute('data-route')).sort());
      assert(JSON.stringify(before) === JSON.stringify(after), 'Inspection changed graph neighbourhood');
      return { pin, before, after, url: p.url() };
    });
    await test('Inspector sections retain provenance and can be pinned', async () => {
      await openSmall(); const detail = p.locator('.right-panel'); await detail.getByRole('tab', { name: 'Evidence', exact: true }).click();
      await detail.getByRole('region', { name: 'OKF trust, lifecycle and provenance' }).waitFor();
      await detail.getByRole('tabpanel', { name: 'Evidence' }).getByRole('button', { name: 'Pin section', exact: true }).click();
      await detail.getByRole('tab', { name: 'Overview', exact: true }).click();
      assert(await detail.getByRole('region', { name: 'OKF trust, lifecycle and provenance' }).isVisible(), 'Pinned evidence disappeared');
      return { visibleSections: await detail.getByRole('tabpanel').evaluateAll(es => es.filter(e => !e.hidden).length) };
    });
    await test('Small search empty state and all eight view routes', async () => {
      await openSmall(); await p.getByPlaceholder('Search nodes').fill('zz-no-such-record'); await count(0, 0); assert(await records().count() === 0, 'Empty search retained cards');
      await p.getByText('No records match.', { exact: false }).waitFor(); await p.getByPlaceholder('Search nodes').fill('');
      const views = [];
      for (const view of ['Reader', 'Graph', 'Links', 'Timeline', 'Type', 'Resources', 'Map', 'Narrative']) { await p.getByLabel('Views').getByRole('button', { name: view, exact: true }).click(); views.push({ view, url: p.url(), visible: await p.locator('.stage').isVisible() }); }
      return views;
    });
    await test('Keyboard resize and collapsed vertical desktop rails', async () => {
      await openSmall(); const splitter = p.getByRole('separator', { name: 'Resize navigation' }); const before = Number(await splitter.getAttribute('aria-valuenow')); await splitter.press('ArrowRight'); assert(Number(await splitter.getAttribute('aria-valuenow')) === before + 10, 'Keyboard resize did not apply');
      await p.getByRole('button', { name: 'Toggle navigation', exact: true }).click(); return await p.locator('.left-panel').evaluate(e => ({ width: e.getBoundingClientRect().width, writingMode: getComputedStyle(e.querySelector('.panel-rail-label')).writingMode }));
    });
    await test('One mobile panel, footer, retained scroll position and keyboard focus', async () => {
      await openSmall(); await p.setViewportSize({ width: 412, height: 850 });
      const stage = p.locator('.stage'); await stage.evaluate(e => e.scrollTop = 240); const before = await stage.evaluate(e => e.scrollTop);
      await p.getByRole('navigation', { name: 'Workspace panels' }).getByRole('button', { name: /Search & facets/ }).click();
      await p.getByRole('navigation', { name: 'Workspace panels' }).getByRole('button', { name: /Results/ }).click(); assert(await stage.evaluate(e => e.scrollTop) === before, 'Panel switching lost scroll position');
      await records().first().getByRole('button').press('Enter');
      await p.locator('[data-panel="details"].mobile-active').waitFor();
      const dimensions = await p.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth, active: document.activeElement?.getAttribute('data-panel'), visible: [...document.querySelectorAll('.workspace-pane')].filter(e => getComputedStyle(e).display !== 'none').length, footerBottom: document.querySelector('.panel-footer').getBoundingClientRect().bottom, height: innerHeight }));
      assert(dimensions.width === dimensions.scrollWidth && dimensions.visible === 1 && dimensions.footerBottom <= dimensions.height && dimensions.active === 'details', 'Mobile layout/focus failed');
      await p.screenshot({ path: output + '/mobile-details.png' }); return dimensions;
    });
    await test('Real touch swipe switches panels without scrolling through neighbours', async () => {
      await p.getByRole('navigation', { name: 'Workspace panels' }).getByRole('button', { name: /Results/ }).click();
      const session = await context.newCDPSession(p);
      await session.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 330, y: 380 }] });
      await session.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 100, y: 382 }] });
      await session.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
      await p.locator('[data-panel="details"].mobile-active').waitFor({ timeout: 3000 }); await session.detach();
      return { activePanel: 'details' };
    });
    await test('Record relationships retain direction and expose assertion evidence', async () => {
      await openSmall();
      const relationship = p.locator('.right-panel .record-relationship').first();
      assert(/Incoming|Outgoing/.test(await relationship.innerText()), 'Missing relationship direction');
      await relationship.getByRole('button', { name: 'Inspect relationship', exact: true }).click();
      await p.getByRole('button', { name: 'Clear relationship', exact: true }).waitFor();
      assert((await p.locator('.right-panel').innerText()).includes('synthetic-fixture'), 'Relationship scope missing');
      return { url: p.url(), evidence: await p.locator('.right-panel').innerText() };
    });
    await test('Accessible desktop and mobile workspace surfaces', async () => {
      const scans = [];
      for (const width of [1440, 412]) {
        await openSmall(); await p.setViewportSize({ width, height: 900 });
        await p.addScriptTag({ path: axePath });
        for (const panel of width === 412 ? ['Search & facets', 'Results', 'Details'] : ['Desktop']) {
          if (panel !== 'Desktop') await p.getByRole('navigation', { name: 'Workspace panels' }).getByRole('button', { name: new RegExp(panel.replace('&', '&')) }).click();
          const result = await p.evaluate(async () => await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] } }));
          scans.push({ width, panel, passes: result.passes.length, violations: result.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.map(n => ({ target: n.target, summary: n.failureSummary })) })) });
        }
      }
      assert(scans.every(scan => scan.violations.length === 0), JSON.stringify(scans)); return scans;
    });
    await test('Corrupted JSON copy fails visibly after real URL navigation', async () => {
      const url = local + '?bundle=' + encodeURIComponent(new URL('/rehearsal/corrupt/corrupt-syntax.json', local).href); const response = await p.goto(url); await p.locator('.error').waitFor({ timeout: 8000 });
      const message = await p.locator('.error').innerText(); assert(await records().count() === 0, 'Corrupted data retained result cards'); return { url: p.url(), status: response.status(), message };
    });
  } finally {
    await context.tracing.stop({ path: output + '/interaction-trace.zip' }); await context.close();
  }
  return { recordedAt: new Date().toISOString(), browser: page.context().browser().version(), origin: local, checks, pageErrors: errors, passed: checks.every(row => row.result === 'passed') && errors.length === 0 };
}
